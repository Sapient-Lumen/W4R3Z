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

from contextlib import contextmanager
from dataclasses import dataclass
import json
import operator
import re
import sys
import unicodedata
from typing import Any, Callable, Dict, Iterator, List, Optional, Sequence

from .stdlib_resource import (
    STDLIB_RESOURCE_NAME,
    STDLIB_SOURCE_NAME,
    StdlibResourceLimitError,
    read_stdlib_resource_bounded,
    stdlib_resource_contract,
)

from .host_limits import (
    DEFAULT_HOSTCALL_RESULT_MAX_BYTES,
    DEFAULT_HOSTCALL_RESULT_MAX_CELLS,
    DEFAULT_VALUE_TEXT_MAX_BYTES,
    changed_stack_suffix,
    hostcall_result_budget_violation,
)


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


@dataclass(frozen=True)
class WordlistAccessScope:
    """Temporary namespace boundary installed by an embedding.

    Standalone Micromax keeps its historical open wordlist semantics.  An
    embedding can install one of these scopes while evaluating extension code
    to make readable and writable wordlists explicit.  The VM enforces writes
    at the dictionary mutation point; core namespace words also preflight reads
    and wordlist creation so failures remain understandable.
    """

    label: str
    readable_wids: frozenset[int]
    writable_wids: frozenset[int]
    allow_create: bool = False

    def __post_init__(self) -> None:
        readable = frozenset(int(wid) for wid in self.readable_wids)
        writable = frozenset(int(wid) for wid in self.writable_wids)
        if not writable.issubset(readable):
            raise ValueError("writable wordlists must also be readable")
        object.__setattr__(self, "readable_wids", readable)
        object.__setattr__(self, "writable_wids", writable)


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


# Micromax's portable value model promises one integer shape to every host:
# signed 64-bit.  The Python reference VM must enforce that promise rather
# than silently inheriting CPython's arbitrary-precision arithmetic.  Keeping
# the boundary here gives the tokenizer, core words, bytecode loader, plugins,
# and future Rust/Wasm hosts one shared definition.
PORTABLE_INT_BITS = 64
PORTABLE_INT_MIN = -(1 << (PORTABLE_INT_BITS - 1))
PORTABLE_INT_MAX = (1 << (PORTABLE_INT_BITS - 1)) - 1
PORTABLE_INT_RANGE_LABEL = "signed 64-bit"
BYTECODE_CONST_OPS = frozenset({"PUSH", "EXEC_NAME", "CALL_Q"})


def is_portable_int(value: Any) -> bool:
    """Return whether ``value`` is representable by Micromax ``Int``."""

    return (
        isinstance(value, int)
        and not isinstance(value, bool)
        and PORTABLE_INT_MIN <= value <= PORTABLE_INT_MAX
    )


def portable_int_value(value: Any, *, context: str = "") -> int:
    """Return ``value`` as a portable Micromax integer.

    This helper deliberately does not interpolate an out-of-range integer into
    the error text: rendering a host-injected giant Python integer can itself
    be expensive.  Callers may inspect before mutating their stacks, which is
    the basis of the transactional arithmetic paths in ``micromax.core``.
    """

    prefix = f"{context}: " if context else ""
    if not isinstance(value, int) or isinstance(value, bool):
        if context:
            raise MicromaxError(f"{prefix}expected int, got {type(value).__name__}")
        raise MicromaxError(f"Expected int, got {type(value).__name__}")
    if value < PORTABLE_INT_MIN or value > PORTABLE_INT_MAX:
        raise MicromaxError(
            f"{prefix}integer out of range ({PORTABLE_INT_RANGE_LABEL})"
        )
    return int(value)


def checked_portable_int(value: int, *, operation: str) -> int:
    """Return one arithmetic result or raise a stable overflow error."""

    if value < PORTABLE_INT_MIN or value > PORTABLE_INT_MAX:
        raise MicromaxError(
            f"integer overflow: {operation} exceeds {PORTABLE_INT_RANGE_LABEL} range"
        )
    return int(value)


def validated_bytecode_operand(
    value: Any,
    *,
    op: str,
    const_count: int,
    context: str,
) -> int:
    """Validate one portable operand, including constant-pool geometry.

    CPython accepts negative list indexes, while the portable bytecode format
    defines PUSH/EXEC_NAME/CALL_Q operands as ordinary zero-based indexes.
    Keeping this check beside the i64 boundary prevents malformed or
    host-mutated bytecode from acquiring Python-only meaning.
    """

    operand = portable_int_value(value, context=context)
    if op in BYTECODE_CONST_OPS and not 0 <= operand < const_count:
        raise MicromaxError(f"{context}: {op} constant index out of range")
    return operand


def parse_portable_int_decimal(
    text: str,
    *,
    context: str,
    allow_whitespace: bool = False,
    allow_plus: bool = False,
    allow_underscores: bool = False,
) -> int:
    """Parse decimal text without ever constructing an unbounded Python int.

    ``int(text, 10)`` first materializes an arbitrary-precision value and only
    then lets a caller discover whether it fits the language.  This scanner
    accumulates only while the result remains inside the signed-i64 magnitude
    bound.  It still validates the complete input, so malformed input does not
    get mislabeled merely because an earlier prefix was already too large.

    Source literals use the strict defaults.  ``to-int`` enables surrounding
    whitespace, a leading plus sign, and underscores between decimal digits to
    retain the useful part of the reference VM's historical conversion syntax.
    Unicode decimal digits are accepted, matching Python's ordinary base-10
    conversion rather than silently narrowing the language to ASCII.
    """

    if not isinstance(text, str):
        raise MicromaxError(f"{context}: invalid integer")

    start = 0
    end = len(text)
    if allow_whitespace:
        while start < end and text[start].isspace():
            start += 1
        while end > start and text[end - 1].isspace():
            end -= 1
    if start >= end:
        raise MicromaxError(f"{context}: invalid integer")

    negative = False
    first = text[start]
    if first == "-":
        negative = True
        start += 1
    elif first == "+" and allow_plus:
        start += 1
    if start >= end:
        raise MicromaxError(f"{context}: invalid integer")

    limit = -PORTABLE_INT_MIN if negative else PORTABLE_INT_MAX
    magnitude = 0
    overflow = False
    saw_digit = False
    previous_was_digit = False

    for pos in range(start, end):
        ch = text[pos]
        if ch == "_" and allow_underscores:
            if not previous_was_digit:
                raise MicromaxError(f"{context}: invalid integer")
            previous_was_digit = False
            continue
        try:
            digit = int(unicodedata.decimal(ch))
        except (TypeError, ValueError):
            raise MicromaxError(f"{context}: invalid integer") from None
        saw_digit = True
        previous_was_digit = True
        if overflow:
            continue
        if magnitude > (limit - digit) // 10:
            overflow = True
            continue
        magnitude = (magnitude * 10) + digit

    if not saw_digit or not previous_was_digit:
        raise MicromaxError(f"{context}: invalid integer")
    if overflow:
        raise MicromaxError(
            f"{context}: integer out of range ({PORTABLE_INT_RANGE_LABEL})"
        )
    return -magnitude if negative else magnitude


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
    # Stamped by VM._add_word.  Keeping ownership on the executable object lets
    # mutation primitives (not only dictionary-definition paths) enforce an
    # embedding's namespace boundary even when a word is passed around as an
    # execution token.
    _micromax_owner_wid: int | None = None

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
    script_context: bool = False
    plugin_load_root: str | None = None
    plugin_generation: int | None = None
    script_origin_id: str | None = None


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
    script_context: bool = False
    plugin_load_root: str | None = None
    plugin_generation: int | None = None
    script_origin_id: str | None = None
    group: str | None = None

    def execute(self, vm: "VM") -> None:
        # Hook handlers are treated as *notifications*.
        #
        # Policy: each handler runs with the same initial data stack and
        # return-stack depth, and any stack effects are discarded between
        # handlers. This prevents accidental ordering dependencies between
        # handlers and keeps hooks predictable for plugins.
        base_stack = list(vm.stack)
        base_rdepth = len(vm.rstack)
        handlers = list(self.handlers)
        ed = getattr(vm, "editor_owner", None)
        fire_filter = getattr(ed, "filter_hook_handlers_for_fire", None) if ed is not None else None
        if callable(fire_filter):
            handlers = list(fire_filter(str(self.name), handlers))
        for h in handlers:
            xt = h.xt if isinstance(h, HookHandler) else h
            # Restore baseline before running each handler.
            vm.stack[:] = list(base_stack)
            if len(vm.rstack) > base_rdepth:
                del vm.rstack[base_rdepth:]
            if bool(getattr(h, "script_context", False)):
                ed = getattr(vm, "editor_owner", None)
                runner = getattr(ed, "run_script_origin_callback", None) if ed is not None else None
                if callable(runner):
                    runner(
                        lambda xt=xt: vm.exec_xt(xt),
                        plugin_load_root=getattr(h, "plugin_load_root", None),
                        group=getattr(h, "group", None),
                        plugin_generation=getattr(h, "plugin_generation", None),
                        script_origin_id=getattr(h, "script_origin_id", None),
                    )
                else:
                    script_ctx = getattr(ed, "script_context", None) if ed is not None else None
                    plugin_ctx = getattr(ed, "plugin_callback_context", None) if ed is not None else None
                    plugin_root = getattr(h, "plugin_load_root", None)
                    plugin_generation = getattr(h, "plugin_generation", None)
                    group = getattr(h, "group", None)
                    script_origin_id = getattr(h, "script_origin_id", None)
                    if callable(plugin_ctx) and callable(script_ctx):
                        with plugin_ctx(plugin_root, group, plugin_generation=plugin_generation):
                            with script_ctx(origin_id=script_origin_id):
                                vm.exec_xt(xt)
                    elif callable(script_ctx):
                        with script_ctx(origin_id=script_origin_id):
                            vm.exec_xt(xt)
                    else:
                        vm.exec_xt(xt)
            else:
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
            try:
                value = parse_portable_int_decimal(lex, context="integer literal")
            except MicromaxError as exc:
                if exc.span is None:
                    exc.span = sp
                raise
            tokens.append(Token(kind="int", value=value, span=sp))
        else:
            tokens.append(Token(kind="word", value=lex, span=sp))

    return tokens


class VM:
    def __init__(self, *, load_stdlib: bool = True, strict_stdlib: bool = False) -> None:
        self.stack: List[Any] = []
        self.rstack: List[Any] = []

        # wordlists/search order (namespacing)
        self._next_wid: int = 2
        self.wordlists: Dict[int, Dict[str, Word]] = {1: {}}  # wid -> {name:word}
        self.wordlist_names: Dict[int, str] = {1: "forth"}
        self.forth_wid: int = 1
        self.current_wid: int = 1
        self.search_order: List[int] = [1]  # wid1 searched first
        # Optional embedding-owned namespace boundary.  Plugin evaluation uses
        # this to expose only the plugin wordlist, its declared dependency
        # closure, and Forth while keeping standalone VM behavior unchanged.
        self.wordlist_access_scope: Optional[WordlistAccessScope] = None

        # dictionary version (for tier-2 inline caching / invalidation)
        # Incremented on any definition change or search-order change.
        self.dict_version: int = 0

        # host bridge (allowlist)
        self.host_fns: Dict[str, Callable[["VM"], None]] = {}
        # Optional embedding policies.  A non-empty denial string blocks the
        # call/advertisement before the hostcall name is consumed from the
        # stack.  Standalone VMs leave both unset.
        self.hostcall_access_policy: Optional[Callable[["VM", str], str]] = None
        self.host_feature_access_policy: Optional[Callable[["VM", str], str]] = None

        # host API contract (for embedding; host owns the world)
        self.host_api_version: str = "0.1"
        self.host_features: set[str] = set()

        # VM-visible result payload limits for allowlisted hostcalls.  These
        # budgets are intentionally approximate and embedding-tunable; values
        # <= 0 disable the corresponding limit.
        self.hostcall_result_max_bytes: int = DEFAULT_HOSTCALL_RESULT_MAX_BYTES
        self.hostcall_result_max_cells: int = DEFAULT_HOSTCALL_RESULT_MAX_CELLS

        # Core value-to-text operations such as ``to-str`` are not hostcalls,
        # so they need their own preallocation ceiling.  This bounds textual
        # amplification of shared lists/maps before one primitive returns.
        # Values <= 0 are an explicit embedding opt-out.
        self.value_text_max_bytes: int = DEFAULT_VALUE_TEXT_MAX_BYTES

        # Hostcall-specific regex input limits.  Result budgets run after an
        # allowlisted helper returns; these preflight limits keep oversized
        # regex inputs from entering Python's backtracking engine or replacement
        # compiler in the first place.  Values <= 0 disable the corresponding
        # limit for embeddings that provide their own containment.
        self.hostcall_regex_max_haystack_bytes: int = 262_144
        self.hostcall_regex_max_pattern_bytes: int = 10_000
        self.hostcall_regex_max_replacement_bytes: int = 262_144
        # Risky regex shapes are routed through a worker process by default.
        # Values <= 0 disable wall-clock containment for embeddings that supply
        # their own defended engine or worker boundary.
        self.hostcall_regex_timeout_seconds: float = 0.25

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

        # Optional embedder callback fired whenever a word is added/replaced.
        # The editor uses this to attach script/plugin authority metadata to
        # dynamic VM definitions without making the standalone VM know about
        # editor capability policy.
        self.word_authority_stamp: Optional[Callable[["VM", int, Word], None]] = None

        # module registry (friendly names for wordlists)
        self.modules: Dict[str, int] = {"forth": self.forth_wid}
        self._module_stack: List[tuple[int, List[int]]] = []  # (prev_current, prev_order)

        # file loading hygiene
        self.loaded_paths: set[str] = set()

        # Startup/resource diagnostics.  These are intentionally plain data so
        # tools, editors, and future hosts can explain degraded-mode startup
        # states without scraping stderr.  The stdlib is loaded from package
        # resources by default; missing resources are non-fatal for minimal
        # embeddings unless strict_stdlib=True is requested.
        self.load_stdlib: bool = bool(load_stdlib)
        self.strict_stdlib: bool = bool(strict_stdlib)
        self.stdlib_loaded: bool = False
        self.stdlib_source_name: str | None = None
        self.stdlib_error: str | None = None
        self.stdlib_resource: Dict[str, Any] = stdlib_resource_contract()
        self.startup_diagnostics: List[Dict[str, Any]] = []

        # Optional additional search roots for include/require.
        # Hosts can populate this (e.g., plugin roots) without changing scripts.
        self.load_paths: List[str] = []

        # Optional host policy hooks for core include/require/reload.  Standalone
        # VMs keep ordinary local-file behavior.  Embedders can intercept path
        # resolution and source reads so script-originated code loading obeys the
        # same capability/containment policy as host-level file APIs.
        self.load_path_policy: Optional[Callable[["VM", str, str, Optional[Span]], Optional[str]]] = None
        self.load_source_reader: Optional[Callable[["VM", str, str, Optional[Span]], Optional[str]]] = None

        # source cache for nicer error messages / tooling
        # filename -> full source string
        self.sources: Dict[str, str] = {}

        # Script-visible execution budgets. ``set-budget`` owns the persistent
        # base frame while ``with-budget`` owns nested frames.  Keeping them
        # separate makes the documented "base" behavior real: setting or
        # clearing the base cannot destroy an enclosing ``with-budget`` frame.
        self._base_step_budget: int | None = None
        self._budget_stack: List[int] = []

        # Embedding-owned execution budgets.  These are deliberately separate
        # from ``_budget_stack``: guest code may tune or clear its own budget,
        # but it must not erase a host limit supplied to ``eval`` or wrapped
        # around a plugin callback.  Every active host frame is decremented so
        # nested evaluations/callbacks compose with their caller's limit.
        self._host_budget_stack: List[int] = []

        # dev-mode stack effect checking:
        #   0 = off
        #   1 = warn (stderr)
        #   2 = error (raise)
        self.stackcheck_mode: int = 0

        self._install_builtins()
        if self.load_stdlib:
            self._load_stdlib()
        else:
            self.startup_diagnostics.append(
                {
                    "kind": "stdlib-disabled",
                    "resource": STDLIB_RESOURCE_NAME,
                    "message": "Micromax stdlib loading was disabled by the host",
                }
            )

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
    def _wordlist_label(self, wid: int) -> str:
        return f"{int(wid)}:{self.wordlist_names.get(int(wid), '?')}"

    def require_wordlist_read(
        self,
        wid: int,
        *,
        operation: str,
        module_name: str | None = None,
    ) -> None:
        """Fail when the active embedding scope cannot read *wid*."""

        scope = self.wordlist_access_scope
        if scope is None or int(wid) in scope.readable_wids:
            return
        target = f"module {module_name}" if module_name else f"wordlist {self._wordlist_label(wid)}"
        raise MicromaxError(f"{scope.label}: undeclared namespace read denied: {operation}: {target}")

    def require_wordlist_write(
        self,
        wid: int,
        *,
        operation: str,
        module_name: str | None = None,
    ) -> None:
        """Fail when the active embedding scope cannot mutate *wid*."""

        scope = self.wordlist_access_scope
        if scope is None or int(wid) in scope.writable_wids:
            return
        target = f"module {module_name}" if module_name else f"wordlist {self._wordlist_label(wid)}"
        raise MicromaxError(f"{scope.label}: namespace write denied: {operation}: {target}")

    def require_wordlist_creation(self, *, operation: str) -> None:
        """Fail when the active embedding scope does not permit new wordlists."""

        scope = self.wordlist_access_scope
        if scope is None or bool(scope.allow_create):
            return
        raise MicromaxError(f"{scope.label}: wordlist creation is internal: {operation}")

    def require_word_mutation(self, word: Word, *, operation: str) -> None:
        """Require write authority for the dictionary that owns *word*.

        Some words contain mutable behavior (notably ``defer``).  Visibility is
        only read authority: a declared dependency may execute or inspect such
        a word, but it must not silently acquire authority to rewrite it.
        """

        scope = self.wordlist_access_scope
        if scope is None:
            return
        owner_wid = getattr(word, "_micromax_owner_wid", None)
        if owner_wid is None:
            raise MicromaxError(
                f"{scope.label}: namespace write denied: {operation}: "
                f"unowned word {getattr(word, 'name', '<word>')}"
            )
        self.require_wordlist_write(int(owner_wid), operation=operation)

    def new_wordlist(self, name: str = "") -> int:
        # Core namespace words preflight this operation for precise source-level
        # errors, but the mutation point must remain authoritative.  Embeddings
        # and future primitives can call ``new_wordlist`` directly; none may
        # bypass an active namespace scope simply by omitting the preflight.
        label = str(name or "").strip() or "<anonymous>"
        self.require_wordlist_creation(operation=f"new wordlist {label}")
        wid = self._next_wid
        self._next_wid += 1
        self.wordlists[wid] = {}
        self.wordlist_names[wid] = name or f"wl{wid}"
        return wid

    def _add_word(self, wid: int, word: Word) -> None:
        self.require_wordlist_write(int(wid), operation=f"define {word.name}")
        word._micromax_owner_wid = int(wid)
        self.wordlists.setdefault(wid, {})[word.name] = word
        stamper = getattr(self, "word_authority_stamp", None)
        if callable(stamper):
            stamper(self, int(wid), word)
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

        If ``step_budget`` is provided, it is enforced as an embedding-owned
        limit for the duration of this evaluation.  Guest ``set-budget`` calls
        cannot clear or enlarge it.
        """
        # Keep the latest source around for error contexts and tooling.
        # This is intentionally simple (no eviction); the VM is a small substrate.
        self.sources[filename] = src
        toks = tokenize(src, filename=filename)
        if step_budget is None:
            self._execute(toks)
            return
        with self.host_step_budget(step_budget):
            self._execute(toks)

    @contextmanager
    def host_step_budget(self, step_budget: int) -> Iterator[None]:
        """Install a non-bypassable embedding execution-step budget.

        This is the host-side companion to the language's script-owned
        ``set-budget`` and ``with-budget`` words.  Active host budgets are
        private VM state: guest code can observe ordinary execution failure but
        cannot remove the frame.  Nested host frames all consume the same VM
        steps, so a loaded file or nested plugin callback cannot reset its
        caller's allowance by opening a fresh evaluation.
        """

        try:
            if isinstance(step_budget, bool):
                raise TypeError("bool is not an execution-step count")
            budget = operator.index(step_budget)
        except TypeError as exc:
            raise MicromaxError("step_budget must be an integer") from exc
        if budget < 0:
            raise MicromaxError("step_budget must be >= 0")
        self._host_budget_stack.append(budget)
        try:
            yield
        finally:
            self._host_budget_stack.pop()



    def resolve_load_path_for_op(self, path: str, *, op: str, span: Optional[Span] = None) -> str:
        """Resolve a load path, allowing a host policy hook to override it.

        Core Micromax remains a small local-file VM by default. Hosts that run
        untrusted or semi-trusted scripts can install ``load_path_policy`` to
        gate ``include``/``require``/``reload`` without replacing the core words
        themselves. A policy returning ``None`` means "use the ordinary VM
        resolver."
        """

        policy = self.load_path_policy
        if policy is not None:
            resolved = policy(self, str(op), str(path), span)
            if resolved is not None:
                return str(resolved)
        return self.resolve_load_path(path, span=span)

    def read_load_source(self, path: str, *, op: str, span: Optional[Span] = None) -> str:
        """Read source for a core load word, allowing a host reader hook.

        ``load_source_reader`` is the read-side companion to
        ``load_path_policy``. Editor-owned VMs use it to bind reads to the
        opened fd under ``cap.fs-root``; standalone VMs keep the historical
        direct UTF-8 file read.
        """

        reader = self.load_source_reader
        if reader is not None:
            source = reader(self, str(op), str(path), span)
            if source is not None:
                return str(source)
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

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
        if (
            self._base_step_budget is None
            and not self._budget_stack
            and not self._host_budget_stack
        ):
            return
        if self._base_step_budget is not None:
            self._base_step_budget -= 1
            if self._base_step_budget < 0:
                raise MicromaxError("Execution budget exceeded", code=-100, span=span)
        for budgets in (self._budget_stack, self._host_budget_stack):
            for i in range(len(budgets)):
                budgets[i] -= 1
                if budgets[i] < 0:
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
                        value = tok.value
                        if tok.kind == "int":
                            value = portable_int_value(value, context="integer literal")
                        self.stack.append(value)
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
                    index = validated_bytecode_operand(
                        ins.arg,
                        op=ins.op,
                        const_count=len(consts),
                        context="bytecode operand",
                    )
                    value = consts[index]
                    if isinstance(value, int):
                        value = portable_int_value(value, context="bytecode")
                    self.stack.append(value)
                    continue

                if ins.op == "EXEC_NAME":
                    if ins.arg is None:
                        raise MicromaxError("EXEC_NAME missing operand", span=ins.span)
                    index = validated_bytecode_operand(
                        ins.arg,
                        op=ins.op,
                        const_count=len(consts),
                        context="bytecode operand",
                    )
                    ref = consts[index]
                    if isinstance(ref, WordRef):
                        self._exec_ref(ref, span=ins.span)
                    else:
                        # Back-compat: allow raw strings in const pool
                        self._exec_name(str(ref), span=ins.span)
                    continue

                if ins.op == "CALL_Q":
                    if ins.arg is None:
                        raise MicromaxError("CALL_Q missing operand", span=ins.span)
                    index = validated_bytecode_operand(
                        ins.arg,
                        op=ins.op,
                        const_count=len(consts),
                        context="bytecode operand",
                    )
                    q = consts[index]
                    if not isinstance(q, Quotation):
                        raise MicromaxError("CALL_Q expects quotation const", span=ins.span)
                    self.exec_xt(q)
                    continue

                if ins.op == "JMP":
                    if ins.arg is None:
                        raise MicromaxError("JMP missing operand", span=ins.span)
                    offset = portable_int_value(ins.arg, context="bytecode operand")
                    ip += offset
                    continue

                if ins.op == "JZ":
                    if ins.arg is None:
                        raise MicromaxError("JZ missing operand", span=ins.span)
                    offset = portable_int_value(ins.arg, context="bytecode operand")
                    flag = self.pop_int()
                    if flag == 0:
                        ip += offset
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
            return [
                str(sp.filename),
                portable_int_value(sp.line, context="bytecode span line"),
                portable_int_value(sp.col, context="bytecode span col"),
            ]

        def enc_const(v: Any) -> Any:
            if isinstance(v, int):
                return ["i", portable_int_value(v, context="bytecode")]
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

        def enc_instr(ins: Instruction) -> list[Any]:
            arg = None
            if ins.arg is not None:
                arg = validated_bytecode_operand(
                    ins.arg,
                    op=str(ins.op),
                    const_count=len(bc.consts),
                    context="bytecode operand",
                )
            return [str(ins.op), arg, enc_span(ins.span)]

        return {
            "magic": "micromax-bc",
            "ver": 1,
            "consts": [enc_const(c) for c in bc.consts],
            "instrs": [enc_instr(ins) for ins in bc.instrs],
        }

    @staticmethod
    def bytecode_from_portable(obj: Any) -> Bytecode:
        """Inverse of bytecode_to_portable."""

        if not isinstance(obj, dict) or obj.get("magic") != "micromax-bc":
            raise MicromaxError("bytecode-from-json: bad magic")
        version = obj.get("ver", 0)
        if not isinstance(version, int) or portable_int_value(
            version, context="bytecode-from-json"
        ) != 1:
            raise MicromaxError(f"bytecode-from-json: unsupported ver {obj.get('ver')!r}")

        def dec_span(x: Any) -> Span:
            if not isinstance(x, list) or len(x) != 3:
                return Span(filename="<bytecode>", line=1, col=1)
            return Span(
                filename=str(x[0]),
                line=portable_int_value(x[1], context="bytecode-from-json span line"),
                col=portable_int_value(x[2], context="bytecode-from-json span col"),
            )

        def dec_const(x: Any) -> Any:
            if not isinstance(x, list) or not x:
                raise MicromaxError("bytecode-from-json: bad const entry")
            tag = x[0]
            if tag == "i":
                if len(x) != 2:
                    raise MicromaxError("bytecode-from-json: bad int entry")
                return portable_int_value(x[1], context="bytecode-from-json")
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
            arg = (
                None
                if it[1] is None
                else validated_bytecode_operand(
                    it[1],
                    op=op,
                    const_count=len(consts),
                    context="bytecode-from-json",
                )
            )
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
        obj = json.loads(
            s,
            parse_int=lambda raw: parse_portable_int_decimal(
                raw,
                context="bytecode-from-json",
            ),
        )
        return VM.bytecode_from_portable(obj)

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
            retired_reason = str(getattr(xt, "_micromax_retired_reason", "") or "")
            if retired_reason:
                plugin = str(getattr(xt, "_micromax_retired_plugin", "") or "")
                generation = getattr(xt, "_micromax_retired_generation", "")
                name = str(getattr(xt, "name", "<xt>") or "<xt>")
                detail = f"plugin {plugin}" if plugin else "retired plugin"
                if generation != "":
                    detail += f" generation {generation}"
                raise MicromaxError(f"Retired execution token: {name} ({detail}, {retired_reason})")
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
        x = self.peek_int()
        del self.stack[-1:]
        return x

    def peek_int(self, depth: int = 0) -> int:
        """Inspect one portable integer without mutating the data stack."""

        if depth < 0 or len(self.stack) <= depth:
            raise MicromaxError("Stack underflow")
        return portable_int_value(self.stack[-1 - depth])

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


    def _record_stdlib_failure(self, exc: Exception) -> None:
        """Record package-resource stdlib load failures as startup diagnostics."""

        self.stdlib_loaded = False
        self.stdlib_source_name = None
        self.stdlib_error = f"{type(exc).__name__}: {exc}"
        kind = "stdlib-resource-limit" if isinstance(exc, StdlibResourceLimitError) else "missing-stdlib"
        message = (
            "Micromax stdlib resource exceeded its byte budget"
            if kind == "stdlib-resource-limit"
            else "Micromax stdlib resource could not be loaded"
        )
        diagnostic = {
            "kind": kind,
            "resource": STDLIB_RESOURCE_NAME,
            "message": message,
            "error": self.stdlib_error,
            "resource_contract": dict(self.stdlib_resource),
        }
        self.startup_diagnostics.append(diagnostic)

    def stdlib_health(self) -> Dict[str, Any]:
        """Return a small inspectable health record for stdlib startup state."""

        if not self.load_stdlib:
            state = "disabled"
        elif self.stdlib_loaded:
            state = "loaded"
        else:
            state = "missing"
        return {
            "state": state,
            "resource": STDLIB_RESOURCE_NAME,
            "loaded": bool(self.stdlib_loaded),
            "source": self.stdlib_source_name,
            "error": self.stdlib_error,
            "resource_contract": dict(self.stdlib_resource),
        }

    def startup_health(self) -> Dict[str, Any]:
        """Return startup health in a host/tool-friendly shape."""

        return {
            "stdlib": self.stdlib_health(),
            "diagnostics": list(self.startup_diagnostics),
        }

    def _load_stdlib(self) -> None:
        """Load micromax's standard library.

        The stdlib is micromax-written convenience words, kept separate from VM primitives
        to preserve portability to Rust/WASM and other hosts.

        Missing stdlib resources are non-fatal for minimal embeddings by default, but
        they are now observable through ``startup_diagnostics`` / ``stdlib_health()``.
        Hosts that need installed-package semantics can request ``strict_stdlib=True``
        and fail closed.
        """
        try:
            loaded = read_stdlib_resource_bounded()
        except Exception as exc:
            self._record_stdlib_failure(exc)
            if self.strict_stdlib:
                raise MicromaxError(f"Micromax stdlib resource missing: {STDLIB_RESOURCE_NAME}: {exc}") from exc
            return
        self.stdlib_resource = dict(loaded.metadata)
        # Use a stable pseudo-filename for nicer errors.
        self.eval(loaded.text, filename=STDLIB_SOURCE_NAME)
        self.stdlib_loaded = True
        self.stdlib_source_name = STDLIB_SOURCE_NAME
        self.stdlib_error = None

    def _install_builtins(self) -> None:
        from .core import install_core_words

        # Install core words into the FORTH wordlist.
        install_core_words(self, wid=self.forth_wid)
