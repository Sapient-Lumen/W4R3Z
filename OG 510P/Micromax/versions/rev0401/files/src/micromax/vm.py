"""micromax.vm

A deliberately small, readable, Python-hosted concatenative VM.

Design intent (rev12):
- dynamic, concatenative
- quotations: [ ... ] values executed via `call`
- colon definitions: : name ... ;
- wordlists + search order (namespace / plugin hygiene)
- simple immediate-style parsing for a few defining words (e.g. variable/constant)
- structured errors w/ source spans + call trace
- locals as runtime sugar: `->name` stores, `name` loads
- postfix message-send sugar: `.word` => "word" send
- host owns the world: hostcalls are allowlisted + versioned

This is a *substrate* for iterating on language design inside the container.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
import re
import importlib.resources as importlib_resources
import sys
from typing import Any, Callable, Dict, List, Optional, Sequence


@dataclass(frozen=True)
class Span:
    filename: str
    line: int
    col: int


@dataclass(frozen=True)
class Token:
    kind: str  # "word" | "int" | "str" | "sym" | "comment"
    value: Any
    span: Span

    def __repr__(self) -> str:
        return f"Token({self.kind!r},{self.value!r},{self.span.filename}:{self.span.line}:{self.span.col})"


class MicromaxError(Exception):
    """Structured VM error."""

    def __init__(
        self,
        message: str,
        *,
        code: int = -1,
        span: Optional[Span] = None,
        trace: Optional[List[str]] = None,
    ):
        super().__init__(message)
        self.code = code
        self.span = span
        self.trace = trace or []

ForthError = MicromaxError


@dataclass
class Instruction:
    """A single bytecode instruction.

    `arg` is op-specific:

    - PUSH / EXEC_NAME / CALL_Q: index into Bytecode.consts
    - JMP / JZ: signed relative instruction offset (from the *next* instruction)

    This keeps the bytecode stream small and portable while still supporting
    control flow in tier-2.
    """

    op: str  # e.g. "PUSH" | "EXEC_NAME" | "CALL_Q" | "JMP" | "JZ"
    arg: Optional[int]
    span: Span


@dataclass
class Bytecode:
    """Tier-2 bytecode.

    This is intentionally small and *portable*: a constant pool plus a linear list
    of instructions.

    Why a constant pool? Many bytecode VMs avoid embedding large immediates in
    the instruction stream (strings, nested quotations, etc.) and instead refer
    to them by index. This keeps a clear path to a compact Rust/WASM encoding.
    """

    consts: List[Any]
    instrs: List[Instruction]


@dataclass
class Code:
    """Executable code.

    Tier-1: token-backed.
    Tier-2: bytecode-backed (optional), compiled from the same tokens.

    Current policy: code that relies on token-stream parsing words (e.g. `module`,
    `constant`, `local@`) should run in tier-1. Tier-2 targets runtime quotations
    used by keybindings/actions and other stable hot paths.
    """

    tokens: List[Token]
    bytecode: Optional[Bytecode] = None


@dataclass
class Quotation:
    code: Code
    span: Span

    @property
    def tokens(self) -> List[Token]:
        # Back-compat convenience; prefer .code in new code.
        return self.code.tokens

    def __repr__(self) -> str:
        return f"[{len(self.tokens)} tokens]"


@dataclass
class Cell:
    value: Any = 0


class Word:
    name: str

    def execute(self, vm: "VM") -> None:
        raise NotImplementedError


@dataclass
class PrimitiveWord(Word):
    name: str
    fn: Callable[["VM"], None]
    doc: str = ""
    effect: str = ""

    def execute(self, vm: "VM") -> None:
        self.fn(vm)


@dataclass
class ColonWord(Word):
    name: str
    code: Code
    doc: str = ""
    effect: str = ""
    span: Span | None = None

    def execute(self, vm: "VM") -> None:
        vm._push_frame()
        try:
            vm._execute_code(self.code)
        finally:
            vm._pop_frame()


@dataclass
class DeferredWord(Word):
    """A deferred word whose behavior is stored in a cell (execution token)."""

    name: str
    cell: Cell
    doc: str = ""
    effect: str = ""

    def execute(self, vm: "VM") -> None:
        xt = self.cell.value
        if xt is None:
            raise MicromaxError(f"Deferred word '{self.name}' is unset")
        vm.exec_xt(xt)


@dataclass
class HookHandler:
    """One installed hook handler with optional provenance/grouping."""

    xt: Any
    span: Span | None = None
    group: str | None = None


@dataclass
class HookWord(Word):
    """A multi-handler hook.

    This is inspired by editor hook systems (e.g. Emacs hooks) where a single hook
    point can run an ordered list of callbacks.
    """

    name: str
    handlers: List[Any]
    doc: str = ""
    effect: str = ""
    span: Span | None = None

    def execute(self, vm: "VM") -> None:
        # Hook handlers are treated as *notifications*.
        #
        # Policy: each handler runs with the same initial data stack and
        # return-stack depth, and any stack effects are discarded between
        # handlers. This prevents accidental ordering dependencies between
        # handlers and keeps hooks predictable for plugins.
        base_stack = list(vm.stack)
        base_rdepth = len(vm.rstack)
        for h in list(self.handlers):
            xt = h.xt if isinstance(h, HookHandler) else h
            # Restore baseline before running each handler.
            vm.stack[:] = list(base_stack)
            if len(vm.rstack) > base_rdepth:
                del vm.rstack[base_rdepth:]
            vm.exec_xt(xt)
            # Discard any stack effects.
            vm.stack[:] = list(base_stack)
            if len(vm.rstack) > base_rdepth:
                del vm.rstack[base_rdepth:]

@dataclass
class WordRef:
    """A cached reference to a word name.

    Tier-2 bytecode keeps late-binding semantics (names resolve through the current
    search order), but uses a tiny inline cache per call-site.

    The cache is invalidated by VM.dict_version, which is bumped on any dictionary
    or search-order mutation.
    """

    name: str
    _cached: Optional["Word"] = None
    _cached_missing: bool = False
    _dict_version: int = -1

    def get(self, vm: "VM") -> Optional["Word"]:
        if self._dict_version == vm.dict_version:
            return None if self._cached_missing else self._cached
        w = vm.find_word(self.name)
        self._cached = w
        self._cached_missing = w is None
        self._dict_version = vm.dict_version
        return w

    def require(self, vm: "VM", *, span: Optional[Span] = None) -> "Word":
        w = self.get(vm)
        if w is None:
            raise MicromaxError(f"Unknown word: {self.name}", span=span)
        return w

    def __repr__(self) -> str:
        return f"<WordRef {self.name}>"


_STACK_EFFECT_PAREN_RE = re.compile(r"^\(\s*(.*?)\s*\)\s*(.*)$")


def normalize_stack_effect(effect: str) -> str:
    inner = " ".join(str(effect or "").strip().split())
    if not inner:
        return ""
    if inner.startswith("(") and inner.endswith(")"):
        inner = inner[1:-1].strip()
        inner = " ".join(inner.split())
    return f"( {inner} )" if inner else ""


def split_stack_effect_doc(doc: str) -> tuple[str, str]:
    """Split a docstring into `( effect )` and descriptive text.

    Micromax keeps docs lightweight and source-friendly, so we accept both:
    - `( x y -- z ) rest of doc`
    - `x y -- z` on the first doc line (common for leading paren comments in colon defs)

    If no effect is present, the effect part is ``""`` and the doc is returned unchanged.
    """

    text = str(doc or "").strip()
    if not text:
        return "", ""

    lines = text.splitlines()
    first = lines[0].strip()
    rest_lines = lines[1:]

    effect = ""
    trailing = ""
    m = _STACK_EFFECT_PAREN_RE.match(first)
    if m is not None and "--" in m.group(1):
        effect = normalize_stack_effect(m.group(1))
        trailing = m.group(2).strip()
    elif "--" in first and "(" not in first and ")" not in first:
        effect = normalize_stack_effect(first)

    if not effect:
        return "", text

    kept: List[str] = []
    if trailing:
        kept.append(trailing)
    kept.extend(rest_lines)
    return effect, "\n".join(line.rstrip() for line in kept).strip()


def word_effect(obj: Any) -> str:
    effect = str(getattr(obj, "effect", "") or "").strip()
    if effect:
        return normalize_stack_effect(effect)
    doc = str(getattr(obj, "doc", "") or "")
    eff, _ = split_stack_effect_doc(doc)
    return eff


def word_doc_summary(obj: Any) -> str:
    doc = str(getattr(obj, "doc", "") or "")
    _, summary = split_stack_effect_doc(doc)
    return summary


@dataclass(frozen=True)
class EffectSig:
    """Parsed stack effect signature.

    Micromax stack effects start as documentation, but we can still get useful
    tooling by parsing *counts*.

    We keep the parser intentionally conservative:
    - If we see any token that looks row-polymorphic/variadic (e.g. "..a", "...", "x*"),
      we mark the signature as non-closed and skip strict checking.
    - Closed signatures are eligible for dev-mode consistency checks.
    """

    ins: int
    outs: int
    closed: bool
    raw: str

    @property
    def delta(self) -> int:
        return int(self.outs - self.ins)


def _effect_tokens_to_counts(tokens: List[str]) -> tuple[int, bool]:
    """Return (count, closed) for one side of an effect."""
    closed = True
    count = 0
    for t in tokens:
        tt = str(t).strip()
        if not tt:
            continue
        # Row variables / variadic markers (Factor-style, and a tiny Micromax convention).
        if tt == "..." or tt.startswith("..") or ".." in tt or tt.endswith("*"):
            closed = False
        else:
            count += 1
    return count, closed


def parse_effect_sig(effect: str) -> Optional[EffectSig]:
    """Parse a normalized effect string into counts.

    Returns None if the string doesn't look like a stack effect.
    """
    eff = normalize_stack_effect(effect)
    if not eff:
        return None
    if not (eff.startswith("(") and eff.endswith(")")):
        return None
    inner = eff[1:-1].strip()
    if "--" not in inner:
        return None
    left_s, right_s = inner.split("--", 1)
    left = [t for t in left_s.strip().split() if t]
    right = [t for t in right_s.strip().split() if t]
    ins, closed_l = _effect_tokens_to_counts(left)
    outs, closed_r = _effect_tokens_to_counts(right)
    return EffectSig(ins=ins, outs=outs, closed=(closed_l and closed_r), raw=eff)


def _effect_string_from_counts(ins: int, outs: int) -> str:
    left = " ".join([f"x{i+1}" for i in range(int(ins))])
    right = " ".join([f"y{i+1}" for i in range(int(outs))])
    inner = f"{left} -- {right}".strip()
    inner = " ".join(inner.split())
    return f"( {inner} )" if inner else ""


def quote_effect(q: Quotation) -> str:
    """Best-effort stack effect for a quotation.

    Convention: a leading paren-comment inside a quotation can contain
    a stack effect, e.g.:
        [ ( x -- y ) ... ]

    This matches common Forth hygiene and gives tooling something to work with.
    """
    for t in q.code.tokens:
        if t.kind == "comment":
            eff, _ = split_stack_effect_doc(str(t.value).strip())
            return eff
        # Stop at first non-comment.
        break
    return ""


def xt_declared_effect(xt: Any) -> str:
    if isinstance(xt, Quotation):
        return quote_effect(xt)
    return word_effect(xt)


def infer_effect_sig_for_code(vm: "VM", tokens: Sequence[Token]) -> Optional[EffectSig]:
    """Best-effort effect inference for a straight-line token sequence.

    This is intentionally conservative: it only succeeds when every referenced
    word has a *closed* declared effect.
    """

    depth = 0
    min_depth = 0
    i = 0

    def apply(ins: int, outs: int) -> None:
        nonlocal depth, min_depth
        depth -= int(ins)
        if depth < min_depth:
            min_depth = depth
        depth += int(outs)

    while i < len(tokens):
        t = tokens[i]
        i += 1
        if t.kind == "comment":
            continue

        if t.kind in ("int", "str"):
            apply(0, 1)
            continue

        if t.kind == "sym" and t.value == "[":
            # Quotation literal: pushes one value.
            # Skip nested token bodies until matching ']'.
            apply(0, 1)
            depth_n = 1
            while i < len(tokens) and depth_n > 0:
                tt = tokens[i]
                i += 1
                if tt.kind == "comment":
                    continue
                if tt.kind == "sym" and tt.value == "[":
                    depth_n += 1
                elif tt.kind == "sym" and tt.value == "]":
                    depth_n -= 1
            if depth_n != 0:
                return None
            continue

        if t.kind == "sym":
            # Unhandled symbol in executable tier.
            return None

        if t.kind != "word":
            return None

        name = str(t.value)

        # locals sugar: ->name stores a value into the current frame.
        if name.startswith("->") and len(name) > 2:
            apply(1, 0)
            continue

        w = vm.find_word(name)
        if w is None:
            return None
        sig = parse_effect_sig(word_effect(w))
        if sig is None or not sig.closed:
            return None
        apply(sig.ins, sig.outs)

    ins = -min_depth if min_depth < 0 else 0
    outs = int(ins + depth)
    if outs < 0:
        return None
    return EffectSig(ins=int(ins), outs=int(outs), closed=True, raw=_effect_string_from_counts(int(ins), int(outs)))


def tokenize(src: str, *, filename: str = "<input>") -> List[Token]:
    """Tokenize micromax source.

    Tokenizer (rev2):
    - whitespace separates tokens
    - symbols ':', ';', '[', ']' are tokens
    - strings in double quotes with basic escapes
    - line comment starts with '\\' (Forth-style)
    - paren comments: ( ... )  (non-nesting). These are preserved as `comment` tokens.
    """

    tokens: List[Token] = []
    i = 0
    line, col = 1, 1

    def span_here() -> Span:
        return Span(filename=filename, line=line, col=col)

    def adv(n: int = 1) -> None:
        nonlocal i, line, col
        for _ in range(n):
            if i >= len(src):
                return
            ch = src[i]
            i += 1
            if ch == "\n":
                line += 1
                col = 1
            else:
                col += 1

    def peek(n: int = 0) -> str:
        j = i + n
        return src[j] if 0 <= j < len(src) else ""

    while i < len(src):
        ch = peek()
        # whitespace
        if ch.isspace():
            adv()
            continue

        # line comment: '\\' to end of line
        if ch == "\\":
            while i < len(src) and peek() != "\n":
                adv()
            continue

        # paren comment: ( ... )
        if ch == "(":
            sp = span_here()
            adv()  # consume '('
            buf: List[str] = []
            while i < len(src) and peek() != ")":
                buf.append(peek())
                adv()
            if peek() == ")":
                adv()  # consume ')'
            tokens.append(Token(kind="comment", value="".join(buf).strip(), span=sp))
            continue

        # single-character symbols
        if ch in [":", ";", "[", "]"]:
            sp = span_here()
            adv()
            tokens.append(Token(kind="sym", value=ch, span=sp))
            continue

        # string literal
        if ch == '"':
            sp = span_here()
            adv()
            buf: List[str] = []
            while i < len(src):
                c = peek()
                if c == '"':
                    adv()
                    break
                if c == "\\":
                    adv()
                    esc = peek()
                    if esc == "n":
                        buf.append("\n")
                        adv()
                    elif esc == "t":
                        buf.append("\t")
                        adv()
                    elif esc == "r":
                        buf.append("\r")
                        adv()
                    elif esc == '"':
                        buf.append('"')
                        adv()
                    elif esc == "\\":
                        buf.append("\\")
                        adv()
                    else:
                        # unknown escape: keep raw
                        buf.append(esc)
                        adv()
                    continue
                buf.append(c)
                adv()
            tokens.append(Token(kind="str", value="".join(buf), span=sp))
            continue

        # regular token (word or int)
        sp = span_here()
        buf: List[str] = []
        while i < len(src):
            c = peek()
            if c.isspace() or c in [":", ";", "[", "]", '"', "(", "\\"]:
                break
            buf.append(c)
            adv()
        lex = "".join(buf)
        # int?
        if lex and (lex.isdigit() or (lex.startswith("-") and lex[1:].isdigit())):
            tokens.append(Token(kind="int", value=int(lex), span=sp))
        else:
            tokens.append(Token(kind="word", value=lex, span=sp))

    return tokens


class VM:
    def __init__(self) -> None:
        self.stack: List[Any] = []
        self.rstack: List[Any] = []

        # wordlists/search order (namespacing)
        self._next_wid: int = 2
        self.wordlists: Dict[int, Dict[str, Word]] = {1: {}}  # wid -> {name:word}
        self.wordlist_names: Dict[int, str] = {1: "forth"}
        self.forth_wid: int = 1
        self.current_wid: int = 1
        self.search_order: List[int] = [1]  # wid1 searched first

        # dictionary version (for tier-2 inline caching / invalidation)
        # Incremented on any definition change or search-order change.
        self.dict_version: int = 0

        # host bridge (allowlist)
        self.host_fns: Dict[str, Callable[["VM"], None]] = {}

        # host API contract (for embedding; host owns the world)
        self.host_api_version: str = "0.1"
        self.host_features: set[str] = set()

        # locals (runtime sugar; per-call frames + a persistent session frame)
        self.locals_stack: List[Dict[str, Any]] = [ {} ]

        # execution context
        self._exec_tokens: Optional[Sequence[Token]] = None
        self._ip: int = 0
        self.callstack: List[str] = []
        self.last_error: Optional[ForthError] = None

        # The most recently *executed* source span (best-effort).
        #
        # This is intentionally a small debugging/provenance affordance for
        # host integrations. For example, the editor can attach a span to
        # dynamically-registered commands so `help` can show where a command was
        # defined.
        #
        # Policy: comments do not update last_span.
        self.last_span: Optional[Span] = None

        # Optional default hook registration group. Embeddings (for example the
        # plugin loader) can set this temporarily so `hook-add` registrations
        # carry a cleanup/debugging tag without complicating plugin code.
        self.current_hook_group: Optional[str] = None

        # Optional default editor registration group. The editor bridge uses
        # this for dynamic command/keybinding registrations so plugin loaders
        # can clean them up in one sweep during unload/reload.
        self.current_editor_group: Optional[str] = None

        # Best-effort backpointer to an embedding that owns editor-style
        # registrations. install_editor_hostcalls() sets this for cleanup and
        # inspection helpers used by the plugin loader.
        self.editor_owner: Any = None

        # module registry (friendly names for wordlists)
        self.modules: Dict[str, int] = {"forth": self.forth_wid}
        self._module_stack: List[tuple[int, List[int]]] = []  # (prev_current, prev_order)

        # file loading hygiene
        self.loaded_paths: set[str] = set()

        # Optional additional search roots for include/require.
        # Hosts can populate this (e.g., plugin roots) without changing scripts.
        self.load_paths: List[str] = []

        # source cache for nicer error messages / tooling
        # filename -> full source string
        self.sources: Dict[str, str] = {}

        # safety: execution budgets (step limits)
        # If _budget_stack is empty, execution is unlimited.
        self._budget_stack: List[int] = []

        # dev-mode stack effect checking:
        #   0 = off
        #   1 = warn (stderr)
        #   2 = error (raise)
        self.stackcheck_mode: int = 0

        self._install_builtins()
        self._load_stdlib()

    # ---------- dev-mode stack effect checking ----------
    def _stackcheck_report(self, message: str, *, span: Optional[Span] = None) -> None:
        if self.stackcheck_mode <= 0:
            return
        if self.stackcheck_mode == 1:
            loc = ""
            if span is not None:
                loc = f"{span.filename}:{span.line}:{span.col}: "
            print(f"stackcheck: {loc}{message}", file=sys.stderr)
            return
        raise MicromaxError(message, span=span)

    def _maybe_stackcheck_xt(self, xt: Any, *, pre_depth: int, post_depth: int) -> None:
        if self.stackcheck_mode <= 0:
            return

        eff = xt_declared_effect(xt)
        sig = parse_effect_sig(eff)
        if sig is None or not sig.closed:
            return

        actual_delta = int(post_depth - pre_depth)
        expected_delta = int(sig.delta)
        if actual_delta != expected_delta:
            name = getattr(xt, "name", "<quote>")
            span = getattr(xt, "span", None) or self.last_span
            self._stackcheck_report(
                f"{name}: declared {sig.raw} (delta {expected_delta}), observed delta {actual_delta} (depth {pre_depth}->{post_depth})",
                span=span,
            )

    # ---------- wordlist management ----------
    def new_wordlist(self, name: str = "") -> int:
        wid = self._next_wid
        self._next_wid += 1
        self.wordlists[wid] = {}
        self.wordlist_names[wid] = name or f"wl{wid}"
        return wid

    def _add_word(self, wid: int, word: Word) -> None:
        self.wordlists.setdefault(wid, {})[word.name] = word
        self._touch_dict()

    def _touch_dict(self) -> None:
        """Bump the dictionary version.

        This invalidates tier-2 inline caches and keeps compiled code consistent
        with tier-1 late-binding semantics.
        """
        self.dict_version += 1

    def set_search_order(self, wids: List[int]) -> None:
        """Set the search order and bump dict_version.

        Search order changes affect how names are resolved, so compiled caches
        must be invalidated.
        """
        self.search_order = list(wids)
        self._touch_dict()


    def find_word(self, name: str) -> Optional[Word]:
        for wid in self.search_order:
            wl = self.wordlists.get(wid, {})
            w = wl.get(name)
            if w is not None:
                return w
        return None

    def find_word_with_wid(self, name: str) -> Optional[tuple[int, Word]]:
        for wid in self.search_order:
            wl = self.wordlists.get(wid, {})
            w = wl.get(name)
            if w is not None:
                return (wid, w)
        return None

    def find_word_in_wid(self, wid: int, name: str) -> Optional[Word]:
        """Find a word in a specific wordlist (no search-order lookup).

        This is useful for plugin/module loaders that want to call a lifecycle
        word (e.g. `init`) *inside* the plugin's own namespace.
        """
        return self.wordlists.get(wid, {}).get(name)

    def all_words_view(self) -> Dict[str, Word]:
        """A merged view of the current search order, useful for tooling."""
        merged: Dict[str, Word] = {}
        # last searched wins in this view; it's just for listing.
        for wid in reversed(self.search_order):
            merged.update(self.wordlists.get(wid, {}))
        return merged

    def remove_hook_group(self, group: str) -> int:
        """Remove every hook handler tagged with *group* across all hooks.

        This is intentionally tiny but useful for plugin reload/unload cleanup:
        a loader can evaluate plugin code with `current_hook_group` set, then
        sweep all matching hook handlers during unload.
        """

        removed = 0
        seen: set[int] = set()
        for wl in self.wordlists.values():
            for w in wl.values():
                if not isinstance(w, HookWord):
                    continue
                if id(w) in seen:
                    continue
                seen.add(id(w))
                kept: List[Any] = []
                for h in w.handlers:
                    hg = h.group if isinstance(h, HookHandler) else None
                    if hg == group:
                        removed += 1
                    else:
                        kept.append(h)
                w.handlers = kept
        return removed


    # ---------- locals frames ----------
    def _push_frame(self) -> None:
        """Push a new locals frame (used for colon-word calls)."""
        self.locals_stack.append({})

    def _pop_frame(self) -> None:
        if len(self.locals_stack) <= 1:
            # never pop the session frame
            return
        self.locals_stack.pop()

    def _set_local(self, name: str, value: Any) -> None:
        self.locals_stack[-1][name] = value

    def _del_local(self, name: str) -> None:
        self.locals_stack[-1].pop(name, None)

    def _clear_session_locals(self) -> None:
        self.locals_stack[0].clear()

    def _lookup_local(self, name: str) -> Optional[Any]:
        for frame in reversed(self.locals_stack):
            if name in frame:
                return frame[name]
        return None

    # ---------- public API ----------
    def define_primitive(
        self,
        name: str,
        fn: Callable[["VM"], None],
        doc: str = "",
        *,
        wid: Optional[int] = None,
        effect: str = "",
    ) -> None:
        ww = PrimitiveWord(name=name, fn=fn, doc=doc, effect=effect)
        self._add_word(self.current_wid if wid is None else wid, ww)

    def define_colon(
        self,
        name: str,
        tokens: List[Token],
        doc: str = "",
        *,
        wid: Optional[int] = None,
        span: Optional[Span] = None,
        effect: str = "",
    ) -> None:
        # Dev-mode check: if the definition has a *closed* declared effect and
        # its body is a straight-line sequence of other closed-effect words and
        # literals, verify counts now (fast feedback while authoring).
        decl = parse_effect_sig(effect)
        if self.stackcheck_mode > 0 and decl is not None and decl.closed:
            inferred = infer_effect_sig_for_code(self, tokens)
            if inferred is not None and (inferred.ins != decl.ins or inferred.outs != decl.outs):
                self._stackcheck_report(
                    f"{name}: declared {decl.raw} but inferred {inferred.raw}",
                    span=span,
                )

        ww = ColonWord(name=name, code=Code(tokens=list(tokens)), doc=doc, effect=effect, span=span)
        self._add_word(self.current_wid if wid is None else wid, ww)

    def register_host(self, name: str, fn: Callable[["VM"], None]) -> None:
        """Register a host function (explicit allowlist)."""
        self.host_fns[name] = fn

    def eval(self, src: str, *, filename: str = "<input>", step_budget: Optional[int] = None) -> None:
        """Evaluate a source string.

        If step_budget is provided, it is pushed for the duration of this evaluation.
        """
        # Keep the latest source around for error contexts and tooling.
        # This is intentionally simple (no eviction); the VM is a small substrate.
        self.sources[filename] = src
        toks = tokenize(src, filename=filename)
        if step_budget is None:
            self._execute(toks)
            return
        if step_budget < 0:
            raise MicromaxError("step_budget must be >= 0")
        self._budget_stack.append(step_budget)
        try:
            self._execute(toks)
        finally:
            self._budget_stack.pop()



    def resolve_load_path(self, path: str, *, span: Optional[Span] = None) -> str:
        """Resolve an include/require path using a small search convention.

        Resolution order for relative paths:
          1) directory of the calling source span (if available)
          2) current working directory
          3) `self.load_paths` (host-provided)
          4) `$MICROMAX_PATH` entries (os.pathsep-separated)

        Returns an absolute path to an existing file or raises MicromaxError.
        """
        import os

        raw = os.path.expanduser(str(path))
        if os.path.isabs(raw):
            return os.path.abspath(raw)

        candidates: list[str] = []

        # 1) Calling file directory (best-effort).
        if span is not None:
            fn = str(getattr(span, 'filename', '') or '')
            if fn and not fn.startswith('<'):
                base = os.path.dirname(fn)
                if base:
                    candidates.append(os.path.abspath(os.path.join(base, raw)))

        # 2) CWD
        candidates.append(os.path.abspath(raw))

        # 3) Host-provided load paths
        for d in list(self.load_paths or []):
            dd = os.path.expanduser(str(d))
            if dd:
                candidates.append(os.path.abspath(os.path.join(dd, raw)))

        # 4) Env search path
        env = os.environ.get('MICROMAX_PATH', '')
        if env:
            for d in env.split(os.pathsep):
                d = d.strip()
                if not d:
                    continue
                dd = os.path.expanduser(d)
                candidates.append(os.path.abspath(os.path.join(dd, raw)))

        # Prefer the first existing file.
        for cand in candidates:
            try:
                if os.path.isfile(cand):
                    return os.path.abspath(cand)
            except OSError:
                continue

        preview = ", ".join(candidates[:6])
        more = max(0, len(candidates) - 6)
        suffix = f" ... (+{more} more)" if more else ""
        raise MicromaxError(f"file not found: {path} (searched: {preview}{suffix})", span=span)
    # ---------- token helpers for "immediate" words ----------
    def next_token(self) -> Token:
        if self._exec_tokens is None:
            raise MicromaxError("No active execution context")
        if self._ip >= len(self._exec_tokens):
            raise MicromaxError("Unexpected end of input")
        t = self._exec_tokens[self._ip]
        self._ip += 1
        return t

    def expect_word_name(self) -> str:
        t = self.next_token()
        if t.kind != "word":
            raise MicromaxError("Expected a word name", span=t.span)
        return str(t.value)

    # ---------- execution ----------
    def _consume_step(self, *, span: Optional[Span] = None) -> None:
        """Consume one execution step from all active budgets."""
        if not self._budget_stack:
            return
        for i in range(len(self._budget_stack)):
            self._budget_stack[i] -= 1
            if self._budget_stack[i] < 0:
                raise MicromaxError("Execution budget exceeded", code=-100, span=span)

    def _execute(self, tokens: Sequence[Token]) -> None:
        prev_tokens, prev_ip = self._exec_tokens, self._ip
        self._exec_tokens = tokens
        self._ip = 0
        try:
            while self._ip < len(tokens):
                tok = tokens[self._ip]
                self._ip += 1
                # Comments are non-executable and should not consume budget.
                if tok.kind == "comment":
                    continue

                # Update provenance span before executing the token.
                self.last_span = tok.span
                self._consume_step(span=tok.span)
                try:
                    if tok.kind in ("int", "str"):
                        self.stack.append(tok.value)
                        continue

                    if tok.kind == "sym":
                        if tok.value == "[":
                            q_tokens = self._collect_bracket(open_span=tok.span)
                            self.stack.append(Quotation(code=Code(tokens=q_tokens), span=tok.span))
                            continue
                        if tok.value == ":":
                            name = self.expect_word_name()
                            effect, doc, body = self._collect_definition(colon_span=tok.span)
                            self.define_colon(name, body, doc=doc, effect=effect, span=tok.span)
                            continue
                        if tok.value in (";", "]"):
                            raise MicromaxError(f"Unexpected token {tok.value!r}", span=tok.span)

                    if tok.kind == "word":
                        self._exec_name(str(tok.value), span=tok.span)
                        continue

                    raise MicromaxError(f"Unhandled token: {tok.kind}", span=tok.span)

                except MicromaxError as fe:
                    if fe.span is None:
                        fe.span = tok.span
                    if not fe.trace:
                        fe.trace = list(self.callstack)
                    self.last_error = fe
                    raise
                except Exception as e:
                    fe = MicromaxError(str(e), span=tok.span, trace=list(self.callstack))
                    self.last_error = fe
                    raise fe from e
        finally:
            self._exec_tokens, self._ip = prev_tokens, prev_ip

    # ---------- tier-2 bytecode (rev13) ----------
    # Tier-2 currently targets *runtime* code (quotations used by actions).
    # Words that parse the token stream (e.g. `module`, `constant`, `local@`) are
    # intentionally not supported in compiled code yet.
    TIER2_FORBIDDEN_WORDS: set[str] = {
        "'", "see", "help", "where",
        "constant", "variable", "defer", "is",
        "module", "endmodule", "use", "in",
        "local@", "local?", "local!", "unlocal",
    }

    def _execute_code(self, code: Code) -> None:
        """Execute a Code object (token tier or compiled tier)."""
        if code.bytecode is None:
            self._execute(code.tokens)
            return
        self._execute_bytecode(code.bytecode)

    def compile_code(self, code: Code) -> None:
        """Compile token-backed Code into tier-2 bytecode (in place)."""
        if code.bytecode is not None:
            return
        code.bytecode = self._compile_tokens_to_bytecode(code.tokens)

    def compile_xt(self, xt: Any) -> Any:
        """( xt -- xt ) Compile a quotation or colon word (no-op for primitives)."""
        if isinstance(xt, Quotation):
            self.compile_code(xt.code)
            return xt
        if isinstance(xt, ColonWord):
            self.compile_code(xt.code)
            return xt
        if isinstance(xt, Word):
            return xt
        raise MicromaxError(f"compile: expected execution token, got {type(xt).__name__}")

    def _compile_tokens_to_bytecode(self, tokens: Sequence[Token]) -> Bytecode:
        consts: List[Any] = []
        instrs: List[Instruction] = []
        i = 0

        def add_const(v: Any) -> int:
            consts.append(v)
            return len(consts) - 1

        def _is_push_quote(ins: Instruction) -> bool:
            if ins.op != "PUSH" or ins.arg is None:
                return False
            try:
                return isinstance(consts[int(ins.arg)], Quotation)
            except Exception:
                return False

        def _pop_push_quote() -> int:
            if not instrs:
                raise MicromaxError("compile: expected quotation (no instructions)")
            ins = instrs.pop()
            if not _is_push_quote(ins):
                raise MicromaxError("compile: expected quotation literal immediately before control word", span=ins.span)
            assert ins.arg is not None
            return int(ins.arg)

        while i < len(tokens):
            t = tokens[i]
            i += 1

            if t.kind == "comment":
                continue

            if t.kind in ("int", "str"):
                idx = add_const(t.value)
                instrs.append(Instruction(op="PUSH", arg=idx, span=t.span))
                continue

            if t.kind == "word":
                name = str(t.value)

                # Peephole compilation for a few control-flow words.
                #
                # Patterns:
                #   flag [t] when
                #   flag [t] [f] if
                #   [cond] [body] while
                #
                # This preserves semantics while avoiding the runtime cost of
                # pushing quotations and calling these control words.
                if name == "when":
                    if instrs and _is_push_quote(instrs[-1]):
                        q_idx = _pop_push_quote()
                        jz_pos = len(instrs)
                        instrs.append(Instruction(op="JZ", arg=0, span=t.span))
                        instrs.append(Instruction(op="CALL_Q", arg=q_idx, span=t.span))
                        end_pos = len(instrs)
                        instrs[jz_pos].arg = int(end_pos - (jz_pos + 1))
                        continue

                if name == "if":
                    if len(instrs) >= 2 and _is_push_quote(instrs[-1]) and _is_push_quote(instrs[-2]):
                        q_false = _pop_push_quote()
                        q_true = _pop_push_quote()
                        jz_pos = len(instrs)
                        instrs.append(Instruction(op="JZ", arg=0, span=t.span))
                        instrs.append(Instruction(op="CALL_Q", arg=q_true, span=t.span))
                        jmp_pos = len(instrs)
                        instrs.append(Instruction(op="JMP", arg=0, span=t.span))
                        else_pos = len(instrs)
                        instrs.append(Instruction(op="CALL_Q", arg=q_false, span=t.span))
                        end_pos = len(instrs)
                        instrs[jz_pos].arg = int(else_pos - (jz_pos + 1))
                        instrs[jmp_pos].arg = int(end_pos - (jmp_pos + 1))
                        continue

                if name == "while":
                    if len(instrs) >= 2 and _is_push_quote(instrs[-1]) and _is_push_quote(instrs[-2]):
                        q_body = _pop_push_quote()
                        q_cond = _pop_push_quote()
                        loop_start = len(instrs)
                        instrs.append(Instruction(op="CALL_Q", arg=q_cond, span=t.span))
                        jz_pos = len(instrs)
                        instrs.append(Instruction(op="JZ", arg=0, span=t.span))
                        instrs.append(Instruction(op="CALL_Q", arg=q_body, span=t.span))
                        jmp_pos = len(instrs)
                        instrs.append(Instruction(op="JMP", arg=0, span=t.span))
                        end_pos = len(instrs)
                        instrs[jz_pos].arg = int(end_pos - (jz_pos + 1))
                        instrs[jmp_pos].arg = int(loop_start - (jmp_pos + 1))
                        continue

                if name in self.TIER2_FORBIDDEN_WORDS:
                    raise MicromaxError(
                        f"compile: {name!r} requires token-stream parsing; run this code uncompiled",
                        span=t.span,
                    )

                # Default: each call-site gets its own WordRef (inline cache).
                idx = add_const(WordRef(name=name))
                instrs.append(Instruction(op="EXEC_NAME", arg=idx, span=t.span))
                continue

            if t.kind == "sym":
                if t.value == "[":
                    inner, i = self._collect_bracket_from_list(tokens, i, open_span=t.span)
                    q = Quotation(code=Code(tokens=list(inner)), span=t.span)
                    # compile nested quotes eagerly for nicer disassembly
                    self.compile_code(q.code)
                    idx = add_const(q)
                    instrs.append(Instruction(op="PUSH", arg=idx, span=t.span))
                    continue
                raise MicromaxError(f"compile: unsupported symbol {t.value!r}", span=t.span)

            raise MicromaxError(f"compile: unhandled token {t.kind!r}", span=t.span)

        return Bytecode(consts=consts, instrs=instrs)

    def _collect_bracket_from_list(
        self, tokens: Sequence[Token], i: int, *, open_span: Span
    ) -> tuple[List[Token], int]:
        """Collect quotation tokens from an in-memory token list (for compilation)."""
        depth = 1
        out: List[Token] = []
        while i < len(tokens):
            t = tokens[i]
            i += 1
            if t.kind == "sym" and t.value == "[":
                depth += 1
                out.append(t)
                continue
            if t.kind == "sym" and t.value == "]":
                depth -= 1
                if depth == 0:
                    return (out, i)
                out.append(t)
                continue
            out.append(t)
        raise MicromaxError("Unterminated quotation '['", span=open_span)

    def _execute_bytecode(self, bc: Bytecode) -> None:
        consts = bc.consts
        instrs = bc.instrs
        ip = 0
        while ip < len(instrs):
            ins = instrs[ip]
            ip += 1
            self.last_span = ins.span
            self._consume_step(span=ins.span)
            try:
                if ins.op == "PUSH":
                    if ins.arg is None:
                        raise MicromaxError("PUSH missing operand", span=ins.span)
                    self.stack.append(consts[int(ins.arg)])
                    continue

                if ins.op == "EXEC_NAME":
                    if ins.arg is None:
                        raise MicromaxError("EXEC_NAME missing operand", span=ins.span)
                    ref = consts[int(ins.arg)]
                    if isinstance(ref, WordRef):
                        self._exec_ref(ref, span=ins.span)
                    else:
                        # Back-compat: allow raw strings in const pool
                        self._exec_name(str(ref), span=ins.span)
                    continue

                if ins.op == "CALL_Q":
                    if ins.arg is None:
                        raise MicromaxError("CALL_Q missing operand", span=ins.span)
                    q = consts[int(ins.arg)]
                    if not isinstance(q, Quotation):
                        raise MicromaxError("CALL_Q expects quotation const", span=ins.span)
                    self.exec_xt(q)
                    continue

                if ins.op == "JMP":
                    if ins.arg is None:
                        raise MicromaxError("JMP missing operand", span=ins.span)
                    ip += int(ins.arg)
                    continue

                if ins.op == "JZ":
                    if ins.arg is None:
                        raise MicromaxError("JZ missing operand", span=ins.span)
                    flag = self.pop_int()
                    if flag == 0:
                        ip += int(ins.arg)
                    continue

                raise MicromaxError(f"Unknown bytecode op: {ins.op}", span=ins.span)

            except MicromaxError as fe:
                if fe.span is None:
                    fe.span = ins.span
                if not fe.trace:
                    fe.trace = list(self.callstack)
                self.last_error = fe
                raise
            except Exception as e:
                fe = MicromaxError(str(e), span=ins.span, trace=list(self.callstack))
                self.last_error = fe
                raise fe from e



    # ---------- bytecode serialization (rev21 draft) ----------
    # This is *tooling-first*: it helps offline caching and makes the Rust/WASM
    # port easier to validate. The JSON shape is intentionally simple and avoids
    # maps in constant entries (lists + tags), so it is easy to parse elsewhere.

    def bytecode_to_portable(self, bc: Bytecode) -> dict[str, Any]:
        """Convert Bytecode into a JSON-serializable dict.

        Schema (ver=1):
          {"magic":"micromax-bc","ver":1,
           "consts":[ [tag, ...], ... ],
           "instrs":[ [op, arg_or_null, [file,line,col]], ... ] }

        Constant tags:
          - ["i", n]               int
          - ["s", text]            string
          - ["wr", name]           WordRef (inline cache, name only)
          - ["q", span, bc_dict]   quotation (span + nested bytecode)
        """

        def enc_span(sp: Span) -> list[Any]:
            return [str(sp.filename), int(sp.line), int(sp.col)]

        def enc_const(v: Any) -> Any:
            if isinstance(v, int):
                return ["i", int(v)]
            if isinstance(v, str):
                return ["s", str(v)]
            if isinstance(v, WordRef):
                return ["wr", str(v.name)]
            if isinstance(v, Quotation):
                # Ensure nested quotations are compiled for portability.
                self.compile_code(v.code)
                if v.code.bytecode is None:
                    raise MicromaxError("bytecode: quotation failed to compile", span=v.span)
                return ["q", enc_span(v.span), self.bytecode_to_portable(v.code.bytecode)]
            raise MicromaxError(f"bytecode: unsupported const type: {type(v).__name__}")

        return {
            "magic": "micromax-bc",
            "ver": 1,
            "consts": [enc_const(c) for c in bc.consts],
            "instrs": [[ins.op, ins.arg, enc_span(ins.span)] for ins in bc.instrs],
        }

    @staticmethod
    def bytecode_from_portable(obj: Any) -> Bytecode:
        """Inverse of bytecode_to_portable."""

        if not isinstance(obj, dict) or obj.get("magic") != "micromax-bc":
            raise MicromaxError("bytecode-from-json: bad magic")
        if int(obj.get("ver", 0)) != 1:
            raise MicromaxError(f"bytecode-from-json: unsupported ver {obj.get('ver')!r}")

        def dec_span(x: Any) -> Span:
            if not isinstance(x, list) or len(x) != 3:
                return Span(filename="<bytecode>", line=1, col=1)
            return Span(filename=str(x[0]), line=int(x[1]), col=int(x[2]))

        def dec_const(x: Any) -> Any:
            if not isinstance(x, list) or not x:
                raise MicromaxError("bytecode-from-json: bad const entry")
            tag = x[0]
            if tag == "i":
                return int(x[1])
            if tag == "s":
                return str(x[1])
            if tag == "wr":
                return WordRef(name=str(x[1]))
            if tag == "q":
                if len(x) != 3:
                    raise MicromaxError("bytecode-from-json: bad quote entry")
                sp = dec_span(x[1])
                bc2 = VM.bytecode_from_portable(x[2])
                return Quotation(code=Code(tokens=[], bytecode=bc2), span=sp)
            raise MicromaxError(f"bytecode-from-json: unknown const tag {tag!r}")

        consts_raw = obj.get("consts", [])
        instrs_raw = obj.get("instrs", [])
        if not isinstance(consts_raw, list) or not isinstance(instrs_raw, list):
            raise MicromaxError("bytecode-from-json: malformed")

        consts: List[Any] = [dec_const(c) for c in consts_raw]
        instrs: List[Instruction] = []
        for it in instrs_raw:
            if not isinstance(it, list) or len(it) != 3:
                raise MicromaxError("bytecode-from-json: bad instruction entry")
            op = str(it[0])
            arg = None if it[1] is None else int(it[1])
            sp = dec_span(it[2])
            instrs.append(Instruction(op=op, arg=arg, span=sp))

        return Bytecode(consts=consts, instrs=instrs)

    def bytecode_to_json(self, bc: Bytecode) -> str:
        """Serialize bytecode to a stable JSON string (utf-8, deterministic)."""
        obj = self.bytecode_to_portable(bc)
        return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))

    @staticmethod
    def bytecode_from_json(s: str) -> Bytecode:
        """Parse bytecode JSON."""
        return VM.bytecode_from_portable(json.loads(s))

    def quote_from_bytecode_json(self, s: str) -> Quotation:
        """( s -- q ) Create a quotation backed only by tier-2 bytecode."""
        bc = VM.bytecode_from_json(s)
        return Quotation(code=Code(tokens=[], bytecode=bc), span=Span(filename="<bytecode>", line=1, col=1))
    def _exec_name(self, name: str, *, span: Optional[Span] = None) -> None:
        """Execute a name with VM sugar (locals + postfix send)."""
        # locals sugar: ->name stores a value into the current frame
        if name.startswith("->") and len(name) > 2:
            self._set_local(name[2:], self.pop())
            return

        # local lookup shadows dictionary words
        local_val = self._lookup_local(name)
        if local_val is not None:
            self.stack.append(local_val)
            return

        # postfix send sugar: .word  =>  "word" send (unless a real .word exists)
        if name.startswith(".") and len(name) > 1:
            existing = self.find_word(name)
            if existing is not None:
                self.callstack.append(name)
                try:
                    existing.execute(self)
                finally:
                    self.callstack.pop()
                return

            self.stack.append(name[1:])
            sendw = self.find_word("send")
            if sendw is None:
                raise MicromaxError("send is not defined", span=span)
            self.callstack.append("send")
            try:
                sendw.execute(self)
            finally:
                self.callstack.pop()
            return

        word = self.find_word(name)
        if not word:
            raise MicromaxError(f"Unknown word: {name}", span=span)
        self.callstack.append(name)
        try:
            word.execute(self)
        finally:
            self.callstack.pop()

    def _exec_ref(self, ref: WordRef, *, span: Optional[Span] = None) -> None:
        """Execute a cached name reference (tier-2 call-site inline cache).

        Semantics must match _exec_name exactly; the only difference is that
        dictionary lookups use WordRef's per-call-site cache keyed by dict_version.
        """
        name = ref.name

        # locals sugar: ->name stores a value into the current frame
        if name.startswith("->") and len(name) > 2:
            self._set_local(name[2:], self.pop())
            return

        # local lookup shadows dictionary words
        local_val = self._lookup_local(name)
        if local_val is not None:
            self.stack.append(local_val)
            return

        # postfix send sugar: .word  =>  "word" send (unless a real .word exists)
        if name.startswith(".") and len(name) > 1:
            existing = ref.get(self)
            if existing is not None:
                self.callstack.append(name)
                try:
                    existing.execute(self)
                finally:
                    self.callstack.pop()
                return

            self.stack.append(name[1:])
            sendw = self.find_word("send")
            if sendw is None:
                raise MicromaxError("send is not defined", span=span)
            self.callstack.append("send")
            try:
                sendw.execute(self)
            finally:
                self.callstack.pop()
            return

        word = ref.require(self, span=span)
        self.callstack.append(name)
        try:
            word.execute(self)
        finally:
            self.callstack.pop()



    def _collect_bracket(self, *, open_span: Span) -> List[Token]:
        if self._exec_tokens is None:
            raise MicromaxError("No active execution context", span=open_span)
        depth = 1
        out: List[Token] = []
        while self._ip < len(self._exec_tokens):
            t = self._exec_tokens[self._ip]
            self._ip += 1
            if t.kind == "sym" and t.value == "[":
                depth += 1
                out.append(t)
                continue
            if t.kind == "sym" and t.value == "]":
                depth -= 1
                if depth == 0:
                    return out
                out.append(t)
                continue
            out.append(t)
        raise MicromaxError("Unterminated quotation '['", span=open_span)

    def _collect_definition(self, *, colon_span: Span) -> tuple[str, str, List[Token]]:
        """Collect tokens for a colon definition.

        Leading paren comments become documentation.
        The first leading comment may also provide a stack effect.
        All comment tokens are stripped from the executable body.
        """
        if self._exec_tokens is None:
            raise MicromaxError("No active execution context", span=colon_span)

        docs: List[str] = []
        saw_code = False
        out: List[Token] = []

        while self._ip < len(self._exec_tokens):
            t = self._exec_tokens[self._ip]
            self._ip += 1
            if t.kind == "sym" and t.value == ";":
                effect, doc = split_stack_effect_doc("\n".join(docs).strip())
                return (effect, doc, out)

            if t.kind == "comment":
                if not saw_code:
                    docs.append(str(t.value))
                # Always strip comments from executable body.
                continue

            saw_code = True
            out.append(t)

        raise MicromaxError("Unterminated definition ':' (missing ';')", span=colon_span)

    # (rev5) _collect_until_semicolon removed in favor of _collect_definition

    def exec_xt(self, xt: Any) -> None:
        """Execute an execution token (Word or Quotation)."""
        pre_depth = len(self.stack)

        if isinstance(xt, Quotation):
            self._execute_code(xt.code)
            self._maybe_stackcheck_xt(xt, pre_depth=pre_depth, post_depth=len(self.stack))
            return

        if isinstance(xt, Word):
            self.callstack.append(getattr(xt, "name", "<xt>"))
            try:
                xt.execute(self)
            finally:
                self.callstack.pop()
            self._maybe_stackcheck_xt(xt, pre_depth=pre_depth, post_depth=len(self.stack))
            return
        raise MicromaxError(f"Expected execution token, got {type(xt).__name__}")

    def pop_xt(self) -> Any:
        x = self.pop()
        if isinstance(x, (Word, Quotation)):
            return x
        raise MicromaxError(f"Expected execution token, got {type(x).__name__}")

    # ---------- stack helpers ----------
    def pop(self) -> Any:
        if not self.stack:
            raise MicromaxError("Stack underflow")
        return self.stack.pop()

    def pop_int(self) -> int:
        x = self.pop()
        if not isinstance(x, int):
            raise MicromaxError(f"Expected int, got {type(x).__name__}")
        return x

    def pop_str(self) -> str:
        x = self.pop()
        if not isinstance(x, str):
            raise MicromaxError(f"Expected str, got {type(x).__name__}")
        return x

    def pop_quote(self) -> Quotation:
        x = self.pop()
        if not isinstance(x, Quotation):
            raise MicromaxError(f"Expected quotation, got {type(x).__name__}")
        return x

    def pop_cell(self) -> Cell:
        x = self.pop()
        if not isinstance(x, Cell):
            raise MicromaxError(f"Expected cell, got {type(x).__name__}")
        return x

    def pop_list(self) -> list:
        x = self.pop()
        if not isinstance(x, list):
            raise MicromaxError(f"Expected list, got {type(x).__name__}")
        return x

    def pop_map(self) -> dict:
        x = self.pop()
        if not isinstance(x, dict):
            raise MicromaxError(f"Expected map, got {type(x).__name__}")
        return x

    # ---------- errors ----------
    def format_error(self, err: MicromaxError) -> str:
        parts: List[str] = []
        if err.span:
            parts.append(f"{err.span.filename}:{err.span.line}:{err.span.col}: ")
        parts.append(str(err))
        if err.code not in (-1, 0):
            parts.append(f" (code {err.code})")

        # Source excerpt (best effort)
        if err.span and err.span.filename in self.sources:
            src = self.sources.get(err.span.filename, "")
            lines = src.splitlines()
            li = err.span.line - 1
            if 0 <= li < len(lines):
                ln = lines[li]
                # Trim long lines, but keep the caret region visible.
                col0 = max(0, err.span.col - 1)
                maxw = 120
                if len(ln) > maxw:
                    # center-ish window around col
                    start = max(0, min(len(ln) - maxw, col0 - maxw // 3))
                    end = start + maxw
                    prefix = "…" if start > 0 else ""
                    suffix = "…" if end < len(ln) else ""
                    shown = prefix + ln[start:end] + suffix
                    caret_pos = (col0 - start) + (1 if start > 0 else 0)
                    caret_pos = max(0, min(len(shown), caret_pos))
                    parts.append("\n" + shown)
                    parts.append("\n" + (" " * caret_pos) + "^")
                else:
                    parts.append("\n" + ln)
                    parts.append("\n" + (" " * col0) + "^")

        if err.trace:
            parts.append("\ntrace: " + " -> ".join(err.trace))
        return "".join(parts)

    # ---------- builtins ----------


    def _load_stdlib(self) -> None:
        """Load micromax's standard library.

        The stdlib is micromax-written convenience words, kept separate from VM primitives
        to preserve portability to Rust/WASM and other hosts.

        Missing stdlib files are treated as non-fatal (useful for minimal embeddings).
        """
        try:
            p = importlib_resources.files("micromax").joinpath("stdlib/core.mx")
            src = p.read_text(encoding="utf-8")
        except Exception:
            return
        # Use a stable pseudo-filename for nicer errors.
        self.eval(src, filename="<stdlib/core.mx>")

    def _install_builtins(self) -> None:
        from .core import install_core_words

        # Install core words into the FORTH wordlist.
        install_core_words(self, wid=self.forth_wid)
