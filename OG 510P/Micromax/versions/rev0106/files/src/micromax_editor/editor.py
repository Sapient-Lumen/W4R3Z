from __future__ import annotations

from dataclasses import dataclass, field
from contextlib import contextmanager
from bisect import bisect_right
import json
import time
import re
import shlex
import os
import webbrowser
from pathlib import Path
from typing import Any

from micromax import VM
from micromax.regex_tools import convert_replacement_template

from .buffer import Buffer, Cursor
from .command_dispatcher import CommandDispatcher, install_default_commands
from .commandbar import Prompt
from .cmdline import parse_cmdline
from .commands import ActionRegistry
from .keymap import Keymap, parse_action_chain
from .options import Options
from .search import SearchState, find_next, find_prev
from .textpos import cursor_to_index, index_to_cursor
from .selection import Selection
from .undo import Edit, UndoManager
from .filetypes import detect_filetype
from .timers import TimerQueue
from .highlight import highlight_line, HIGHLIGHT_TAGS
from .statusformat import render_status_template
from .capabilities import refresh_vm_features
from .fs_sandbox import fs_root as fs_sandbox_root, resolve_path as fs_resolve_path, is_allowed as fs_path_allowed
from .persist_sandbox import persist_root as persist_sandbox_root, resolve_path as persist_resolve_path, is_allowed as persist_path_allowed, deny_reason as persist_deny_reason


# Actions that are expected to mutate the active buffer.
#
# This list powers the "protected/read-only" buffer guard used for internal
# help/docs buffers. Unlike OS-level readonly file permissions, protected
# buffers should reject edits (so users don't accidentally trash generated
# content).
MUTATING_ACTIONS: set[str] = {
    "InsertText",
    "InsertNewline",
    "Backspace",
    "Delete",
    "Undo",
    "Redo",
    "Cut",
    "Paste",
    "CutLine",
    "DuplicateLine",
    "MoveLinesUp",
    "MoveLinesDown",
    "IndentSelection",
    "UnindentSelection",
    "InsertTab",
    "QueryReplaceYes",
    "QueryReplaceAll",
    "QueryReplaceLast",
}

# --- Markdown helpers (docs/help browser) ---

def md_norm_ref_id(s: str) -> str:
    """Normalize a markdown reference-id (case-insensitive, collapse whitespace)."""

    try:
        return re.sub(r"\s+", " ", str(s or "").strip()).casefold()
    except Exception:
        return ""


def md_inline_link_target(inner: str) -> str:
    """Extract and *validate* an inline-link destination from markdown parens content.

    Supports common forms:
      - (target)
      - (target "title")
      - (<target> "title")

    This is intentionally conservative: if the remaining content doesn't look
    like an optional title, we return '' so docs parsing can fall back to other
    link forms (notably shortcut reference links, per CommonMark).
    """

    s = str(inner or "").strip()
    if not s:
        return ""

    def _rest_is_title(rest: str) -> bool:
        r = str(rest or "").strip()
        if not r:
            return True
        if r.startswith(('"', "'")):
            return True
        if r.startswith('(') and r.endswith(')'):
            return True
        return False

    if s.startswith('<'):
        j = s.find('>')
        if j == -1:
            return ""
        dest = s[1:j].strip()
        rest = s[j + 1 :]
        if dest and _rest_is_title(rest):
            return str(dest).strip().strip('"').strip("'")
        return ""

    parts = s.split()
    if not parts:
        return ""
    raw_tok = parts[0]
    dest = str(raw_tok).strip().strip('"').strip("'")
    if not dest:
        return ""
    rest = s[len(raw_tok) :]
    if _rest_is_title(rest):
        return dest
    return ""



@dataclass
class EditorBuffer:
    name: str
    buf: Buffer
    cursors: list[Cursor]
    sel_anchors: list[Cursor | None]
    cursor_ids: list[int]
    # Index into `cursors`/`sel_anchors` designating the *primary* cursor.
    # Cursor lists remain in document order.
    primary: int
    local_options: dict[str, Any]

    # Per-cursor "goal" x (visual column) used for softwrap-aware vertical motion.
    goal_x_by_cursor: dict[int, int] = field(default_factory=dict)

    # A small stack used to recover from accidental selection/cursor clears.
    # This is intentionally *not* part of undo history (it's closer to a register).
    sel_stack: list[tuple[list[Cursor], list[Cursor | None], list[int], int]] = field(default_factory=list)

    # A tiny "jumplist" for navigation (Vim/Helix-style).
    # - push current cursor/selection state
    # - jump back/forward through the list
    #
    # This is intentionally *not* undo: it captures *where you were*, not edits.
    jump_list: list[tuple[list[Cursor], list[Cursor | None], list[int], int]] = field(default_factory=list)
    jump_index: int = -1


@dataclass(frozen=True)
class MacroStep:
    kind: str  # 'action' | 'command'
    name: str
    payload: dict[str, Any]


@dataclass(frozen=True)
class ActiveKeyMode:
    name: str
    once: bool = False
    # If true, this mode *captures* all keys: unbound keys do not fall through
    # to lower-precedence modes/global bindings.
    #
    # This is useful for modal interactions like query-replace confirmation
    # prompts (y/n/a/q) where accidental global bindings would be surprising.
    capture: bool = False


@dataclass
class QueryReplaceSession:
    """State for an interactive, micro/Emacs-style "query replace" loop."""

    buffer_name: str
    search: str
    value: str
    literal: bool

    # Match semantics (mirrors search): case-insensitive when ignorecase is enabled.
    case_sensitive: bool = True

    # Best-effort count of remaining matches from the session start (for UX).
    total: int = 0

    # Precompiled regex and replacement template for regex mode.
    regex: re.Pattern[str] | None = None
    repl_py: str = ""

    # Search continuation point.
    next_start: Cursor = field(default_factory=lambda: Cursor(0, 0))

    # Current match span and the concrete replacement text for this match.
    match_start: Cursor | None = None
    match_end: Cursor | None = None
    match_repl: str = ""

    # Undo snapshot at session start (recorded as one undo entry on finish).
    before: tuple[str, list[Cursor], list[Cursor | None], list[int], int] | None = None

    replaced: int = 0
    examined: int = 0


class Editor:
    """Headless editor core.

    Design priorities:
      - **unit-testable** core (no terminal dependencies)
      - micro-esque UX primitives (command bar, action chains, incsearch, macros)
      - micromax embedded as the plugin/macro language

    This is intentionally not a full TUI yet. The goal is to keep core logic
    highly testable while we steadily steal the best "goodies" from micro.
    """

    def __init__(self) -> None:
        # Monotonic ids for cursors so we can implement "remove latest cursor"
        # semantics while still keeping the cursor list in document order.
        self._next_cursor_id: int = 1

        self.buffers: dict[str, EditorBuffer] = {}
        self.active: str | None = None

        # Buffer MRU: tracks recently-active buffers for prev-buffer behavior.
        self._buffer_mru: list[str] = []

        self.keymap = Keymap()
        self._install_builtin_keymode_bindings()
        self.actions = ActionRegistry()
        # Back-compat alias
        self.commands = self.actions

        self.undo = UndoManager()

        self.options = Options()
        self._install_default_options()

        self.command_dispatcher = CommandDispatcher()
        install_default_commands(self)

        self.search = SearchState(query="", literal=True, case_sensitive=False)

        # Interactive query-replace session (qreplace/queryreplace).
        self.qreplace: QueryReplaceSession | None = None
        self.prompt: Prompt | None = None

        self.messages: list[str] = []
        self.should_quit: bool = False

        # Script context depth (non-zero when called from micromax hostcalls).
        # Used to enforce capability gates on powerful editor commands.
        self._script_depth: int = 0

        # Double-tap quit guard: when dirty buffers exist, `quit` arms once
        # (prints a warning) and only quits on a second attempt or with -f/!.
        self._quit_armed: bool = False

        # Double-tap close-buffer guard: mirrors quit semantics, but scoped to the
        # `close` command so users don't accidentally discard a dirty buffer.
        self._close_armed: bool = False
        self._close_armed_name: str = ""


        # Double-tap bulk-close guards (closeall/only).
        self._closeall_armed: bool = False
        self._only_armed: bool = False

        # Clipboard is stored as a *list* of items.
        # - Most copy operations produce a single item.
        # - Multi-cursor copy/cut can produce one item per cursor.
        self.clipboard_items: list[str] = []
        self.clipboard_kind: str = "items"  # items|lines
        self._cutline_accum: bool = False

        # Clipboard change tracking (used by UI layers for external backends).
        # - serial increments on every clipboard mutation
        # - from_script is true when the change happened inside script_context()
        self.clipboard_serial: int = 0
        self.clipboard_from_script: bool = False

        # Prompt history (command + find).
        self.history: dict[str, list[str]] = {"command": [], "find": []}

        # Search-first command palette MRU, scoped to actual palette selections
        # rather than all editor actions. This keeps the palette helpful without
        # letting high-frequency movement actions dominate it.
        self._palette_recent: list[tuple[str, str]] = []
        self._palette_recent_limit: int = 12

        # Recent files MRU (fast file switching / command palette companion).
        # Entries are absolute-ish paths as strings (best-effort normalized).
        self.recent_files: list[str] = []
        self._recent_limit: int = 20

        # Help/docs navigation stack (for docs-backed help buffers).
        # Stores docs topics (slugs) so users can `helpback` after `helpfollow`.
        self._help_stack: list[str] = []
        self._help_stack_limit: int = 40

        # Help/docs heading cache (best-effort).
        # Used for docs-link section labeling when `help.linksections=heading`.
        self._help_heading_cache_topic: str = ""
        self._help_heading_cache_nlines: int = 0
        self._help_heading_cache: list[tuple[int, str]] = []

        # External URL opener (capability-gated). Tests can override this.
        self._open_url_fn = webbrowser.open

        # Pending external URL open confirmation (docs browser safety).
        self._pending_open_url: str | None = None
        self._pending_open_url_source: str = ""

        # Embedded micromax VM.
        self.vm = VM()
        self._install_default_actions()

        # Editor -> micromax event hooks (non-authoritative; notifications only).
        # Plugins can `hook-add` handlers to these.
        try:
            self.vm.eval(
                "hook ed.pre-action hook ed.on-action "
                "hook ed.on-open hook ed.on-save hook ed.on-change",
                filename="<editor>",
            )
        except Exception:
            pass

        # Keep VM feature advertisement aligned with capability options.
        # Optional hostcalls may be installed later by the UI/bridge.
        try:
            self.refresh_capabilities()
        except Exception:
            pass

        # optional: set externally
        self.plugin_manager: Any = None

        # Deterministic timer queue (for plugins: debounce/autosave).
        # Tests can override _now_fn to avoid real time.
        self._now_fn = time.monotonic
        self.timers = TimerQueue()

        # scratch input for actions/commands
        self.input: dict[str, Any] = {}

        # Macro recording (micro-style "record/play last macro", extended with named macros)
        self.macro_recording: bool = False
        self._macro_buffer: list[MacroStep] = []
        self._macro_target: str = "last"
        self._macro_prev_last: list[MacroStep] | None = None
        self._macro_playing: bool = False

        # Stored macros (name -> steps). "last" is the default.
        self.macro: list[MacroStep] = []
        self.macros: dict[str, list[MacroStep]] = {"last": self.macro}

        # Multi-cursor selection search state (for Alt-n / Alt-x style workflows)
        self._mc_last_match_start: Cursor | None = None

        # Optional keymap mode stack.
        #
        # This is intentionally smaller than a full modal editor architecture:
        # the active stack only affects keybinding lookup order. Global bindings
        # always remain as the final fallback.
        #
        # Modes can be persistent or one-shot. One-shot (transient) modes are
        # inspired by Helix minor modes, Kakoune's next-key layers, and Emacs'
        # transient maps: they get first crack at the next key, then pop.
        self.key_mode_stack: list[ActiveKeyMode] = []

        # Named marks (portable, headless navigation points).
        # Stored as: name -> (buffer_name, Cursor).
        self.marks: dict[str, tuple[str, Cursor]] = {}

        # Viewport state (headless-friendly scrolling model).
        # A UI should keep this updated via `ed.viewport!`.
        self.viewport_top_line: int = 0
        # When softwrap is enabled, the viewport may begin partway through a long
        # logical line. This is the wrap-row index (0-based) within top_line.
        self.viewport_top_subline: int = 0
        self.viewport_left_col: int = 0
        self.viewport_height: int = 0
        self.viewport_width: int = 0

    # ----- messaging -----
    def message(self, s: str) -> None:
        self.messages.append(str(s))



    # ----- script context -----
    @contextmanager
    def script_context(self):
        """Context manager marking operations as originating from scripts/plugins.

        The headless editor is the "host world." Some commands (open/save, etc.)
        provide filesystem authority. We want interactive users to keep the usual
        editor UX while allowing hosts to run scripts with **no ambient authority**
        unless a capability is explicitly enabled.

        Hostcalls that can execute editor commands or submit prompts should wrap
        their work in this context so command implementations can enforce
        capability gates for *script-originated* requests.
        """

        self._script_depth += 1
        try:
            yield
        finally:
            self._script_depth = max(0, int(self._script_depth) - 1)

    def in_script_context(self) -> bool:
        """True when the current call stack originated from a script hostcall."""

        return bool(int(self._script_depth) > 0)

    # ----- prompt completion matching -----

    def _completion_fuzzy_positions(self, candidate: str, query: str) -> list[int] | None:
        """Return subsequence match positions for query in candidate, or None.

        This is intentionally tiny and deterministic: it is *not* trying to be a
        full fzf clone. We only need a predictable fallback when exact-prefix
        completion finds nothing.
        """
        q = str(query or "").casefold()
        c = str(candidate).casefold()
        if q == "":
            return []

        out: list[int] = []
        start = 0
        for ch in q:
            pos = c.find(ch, start)
            if pos < 0:
                return None
            out.append(pos)
            start = pos + 1
        return out

    def _completion_fuzzy_sort_key(self, candidate: str, query: str) -> tuple[int, int, int, int, int, int, str] | None:
        """Return a deterministic sort key for fuzzy completion candidates.

        Lower is better. We prefer:
        - contiguous substring hits over plain subsequence hits
        - earlier matches
        - tighter spans
        - more consecutive / boundary-aligned characters
        - shorter candidates
        """
        positions = self._completion_fuzzy_positions(candidate, query)
        if positions is None:
            return None

        folded_candidate = str(candidate).casefold()
        folded_query = str(query or "").casefold()
        substring_at = folded_candidate.find(folded_query) if folded_query else 0

        consecutive = 0
        boundary = 0
        for idx, pos in enumerate(positions):
            if idx > 0 and pos == (positions[idx - 1] + 1):
                consecutive += 1

            if pos == 0:
                boundary += 1
            else:
                prev = candidate[pos - 1]
                cur = candidate[pos]
                if prev in "-_/.: " or (prev.islower() and cur.isupper()):
                    boundary += 1

        start = positions[0] if positions else 0
        span = (positions[-1] - positions[0]) if positions else 0
        return (
            0 if substring_at >= 0 else 1,
            substring_at if substring_at >= 0 else start,
            start,
            span,
            -consecutive,
            -boundary,
            len(candidate),
            str(candidate),
        )

    def _completion_candidates_for_prefix(
        self,
        names: list[str],
        prefix: str,
        *,
        at_eol: bool,
    ) -> tuple[list[str], bool]:
        """Return built-in completion candidates and whether fuzzy fallback was used.

        Policy:
        - exact prefix matches win when present
        - otherwise, fall back to a tiny subsequence matcher for command-ish names
        - path completion stays on its own explicit prefix-based path
        """
        raw_names = sorted({str(n) for n in names})
        exact = [n for n in raw_names if n.startswith(prefix)]
        fuzzy = False

        if exact:
            chosen = exact
        elif prefix != "":
            scored: list[tuple[tuple[int, int, int, int, int, int, str], str]] = []
            for n in raw_names:
                key = self._completion_fuzzy_sort_key(n, prefix)
                if key is not None:
                    scored.append((key, n))
            scored.sort(key=lambda item: item[0])
            chosen = [n for _key, n in scored]
            fuzzy = bool(chosen)
        else:
            chosen = []

        if at_eol:
            chosen = [n + " " for n in chosen]
        return (chosen, fuzzy)

    def _prompt_known_keymodes(self) -> list[str]:
        names = set(self.keymap.modes())
        names.update(str(m) for m in self.active_key_modes())
        return sorted(str(n) for n in names if str(n))

    def _prompt_hook_names(self) -> list[str]:
        from micromax.vm import HookWord

        names: set[str] = set()
        for wl in self.vm.wordlists.values():
            for name, word in wl.items():
                if isinstance(word, HookWord):
                    names.add(str(name))
        return sorted(names)

    def _prompt_vm_word_names(self) -> list[str]:
        return sorted(str(n) for n in self.vm.all_words_view().keys())

    def _prompt_help_topic_names(self) -> list[str]:
        names = list(self.command_dispatcher.names()) + list(self.actions.names()) + self._prompt_vm_word_names()
        return sorted({str(n) for n in names})

    def _prompt_command_palette_names(self) -> list[str]:
        names = list(self.command_dispatcher.names()) + list(self.actions.names())
        return sorted({str(n) for n in names})

    def _prompt_vm_word_row(self, insert: str) -> list[str]:
        from micromax.vm import ColonWord, DeferredWord, HookWord, PrimitiveWord, word_doc_summary, word_effect

        raw = str(insert)
        name = raw[:-1] if raw.endswith(" ") else raw
        found = self.vm.find_word_with_wid(name)
        if found is None:
            return [str(insert), "word", "", ""]
        wid, w = found
        kind = "word"
        if isinstance(w, PrimitiveWord):
            kind = "primitive"
        elif isinstance(w, ColonWord):
            kind = "colon"
        elif isinstance(w, DeferredWord):
            kind = "deferred"
        elif isinstance(w, HookWord):
            kind = "hook"
        effect = str(word_effect(w) or "").strip()
        wl = str(self.vm.wordlist_names.get(int(wid), f"wl{wid}"))
        menu = f"{kind} wl={wl}"
        if effect:
            menu = f"{menu} {effect}"
        info = str(word_doc_summary(w) or "")
        return [str(insert), "word", menu, info]


    def _prompt_buffer_row(self, insert: str) -> list[str]:
        raw = str(insert)
        name = raw[:-1] if raw.endswith(" ") else raw
        eb = self.buffers.get(name)
        if eb is None:
            return [str(insert), "buffer", "", ""]
        menu = "active" if (self.active == name) else "buffer"
        path = getattr(eb.buf, "path", None) or ""
        nlines = len(getattr(eb.buf, "lines", []) or [])
        info_parts: list[str] = []
        if path:
            info_parts.append(str(path))
        if nlines:
            info_parts.append(f"{nlines} lines")
        info = " | ".join(info_parts)
        return [str(insert), "buffer", str(menu), str(info)]

    def _prompt_mark_row(self, insert: str) -> list[str]:
        raw = str(insert)
        name = raw[:-1] if raw.endswith(" ") else raw
        if name not in self.marks:
            return [str(insert), "mark", "", ""]
        buf_name, cur = self.marks[name]
        menu = f"{buf_name}:{int(cur.line)+1}:{int(cur.col)+1}"
        info = ""
        eb = self.buffers.get(buf_name)
        if eb is not None:
            line_i = int(cur.line)
            if 0 <= line_i < len(eb.buf.lines):
                s = eb.buf.lines[line_i].rstrip("\n")
                s = s.strip()
                if len(s) > 80:
                    s = s[:77] + "..."
                info = s
        return [str(insert), "mark", str(menu), str(info)]

    def _prompt_plugin_row(self, insert: str) -> list[str]:
        raw = str(insert)
        name = raw[:-1] if raw.endswith(" ") else raw
        pm = getattr(self, "plugin_manager", None)
        if pm is None:
            return [str(insert), "plugin", "", ""]

        loaded = name in getattr(pm, "plugins", {})
        cand = getattr(pm, "candidates", {}).get(name) if hasattr(pm, "candidates") else None

        version = ""
        desc = ""
        reqs: list[str] = []
        try:
            if cand is not None:
                version = str(cand.meta.version or "")
                desc = str(cand.meta.description or "")
                reqs = list(cand.meta.requires or [])
            elif loaded:
                meta = getattr(pm.plugins.get(name), "meta", {}) if pm else {}
                version = str(meta.get("version") or "")
                desc = str(meta.get("description") or "")
                reqs = list(meta.get("requires") or [])
        except Exception:
            pass

        errs: list[str] = []
        try:
            errs = [str(e) for (n, e) in getattr(pm, "load_errors", []) if str(n) == name]
        except Exception:
            errs = []

        menu_parts: list[str] = [("loaded" if loaded else "not loaded")]
        if version:
            menu_parts.append(f"v{version}")
        if reqs:
            menu_parts.append("deps:" + ",".join(reqs))
        if errs:
            menu_parts.append("ERROR")
        menu = " ".join(menu_parts).strip()

        info = desc
        if errs:
            info = errs[-1] if len(errs) == 1 else f"{len(errs)} errors; last: {errs[-1]}"
        return [str(insert), "plugin", str(menu), str(info)]


    def _prompt_option_value_candidates(
        self,
        name: str,
        prefix: str,
        *,
        at_eol: bool,
    ) -> tuple[list[str], bool]:
        spec = self.options.specs.get(str(name))
        if spec is None:
            return ([], False)
        if spec.kind == "bool":
            return self._completion_candidates_for_prefix(["true", "false"], prefix, at_eol=at_eol)
        if spec.kind == "enum" and spec.enum:
            return self._completion_candidates_for_prefix(list(spec.enum), prefix, at_eol=at_eol)
        return ([], False)


    def _prompt_display_value(self, value: object) -> str:
        if isinstance(value, bool):
            return "true" if value else "false"
        if value is None:
            return "0"
        return str(value)

    def _prompt_option_row(self, name: str, *, local: bool) -> list[str]:
        spec = self.options.specs.get(str(name))
        if spec is None:
            return [str(name), "option", "", ""]

        scope = "local" if local else "global"
        kind = str(spec.kind)
        if spec.kind == "enum" and spec.enum:
            kind = kind + "[" + "|".join(str(x) for x in spec.enum) + "]"

        cur_local = self.cur().local_options if local else None
        cur = self.options.get(spec.name, local=cur_local)
        menu = f"{kind} {scope} current={self._prompt_display_value(cur)} default={self._prompt_display_value(spec.default)}"
        return [spec.name + " ", "option", menu, str(spec.doc or "")]

    def _prompt_path_row(self, insert: str) -> list[str]:
        import os

        raw = str(insert)
        body = raw[:-1] if raw.endswith(" ") else raw
        if body.startswith(("'", '"')):
            body = body[1:]
        if body.endswith(("'", '"')):
            body = body[:-1]
        kind = "dir" if body.endswith(os.sep) else "file"
        menu = "directory" if kind == "dir" else "file"
        return [str(insert), kind, menu, body]

    def _help_topic_meta_text(self, row: list[object]) -> str:
        parts: list[str] = []
        if len(row) >= 3 and row[2] not in (None, 0, ""):
            parts.append(str(row[2]))
        if len(row) >= 4 and row[3] not in (None, 0, ""):
            parts.append(str(row[3]))
        return " ".join(parts).strip()

    def _search_terms(self, query: str) -> list[str]:
        return [str(part) for part in str(query or "").split() if str(part)]

    def _multi_term_field_key(
        self,
        fields: list[tuple[int, str]],
        query: str,
        *,
        fallback_rank: int,
        tie_name: str,
    ) -> tuple[int, int, int, int, int, int, int, int, int, str] | None:
        terms = self._search_terms(query)
        if len(terms) <= 1:
            return None

        matched: list[tuple[int, int, int, int, int, int, int, str]] = []
        for term in terms:
            best: tuple[int, int, int, int, int, int, int, str] | None = None
            for field_rank, raw_text in fields:
                text = str(raw_text or "")
                if text == "":
                    continue
                key = self._completion_fuzzy_sort_key(text, term)
                if key is None:
                    continue
                cand = (field_rank, *key)
                if best is None or cand < best:
                    best = cand
            if best is None:
                return None
            matched.append(best)

        return (
            fallback_rank,
            sum(item[0] for item in matched),
            sum(item[1] for item in matched),
            sum(item[2] for item in matched),
            sum(item[3] for item in matched),
            sum(item[4] for item in matched),
            sum(item[5] for item in matched),
            sum(item[6] for item in matched),
            sum(item[7] for item in matched),
            str(tie_name).casefold(),
        )

    def _apropos_row_sort_key(self, row: list[object], query: str) -> tuple[int, int, int, int, int, int, int, int, int, str] | None:
        q = str(query or "").strip()
        if q == "":
            return (0, 0, 0, 0, 0, 0, 0, 0, 0, "")

        name = str(row[0]) if row else ""
        name_key = self._completion_fuzzy_sort_key(name, q)
        if name_key is not None:
            return (0, *name_key, name.casefold())

        meta = self._help_topic_meta_text(row)
        if meta:
            folded_meta = meta.casefold()
            folded_q = q.casefold()
            if folded_q and folded_q in folded_meta:
                pos = folded_meta.find(folded_q)
                return (1, pos, pos, 0, 0, 0, 0, len(meta), len(name), name.casefold())

            meta_key = self._completion_fuzzy_sort_key(meta, q)
            if meta_key is not None:
                return (2, *meta_key, name.casefold())

        multi_key = self._multi_term_field_key([(0, name), (1, meta)], q, fallback_rank=3, tie_name=name)
        if multi_key is not None:
            return multi_key
        return None

    def _command_palette_row_key(self, row: list[object]) -> tuple[str, str]:
        name = str(row[0]) if row else ""
        kind = str(row[1]) if len(row) >= 2 else ""
        return (kind, name)

    def _record_palette_recent(self, kind: str, name: str) -> None:
        k = str(kind or "").strip()
        nm = str(name or "").strip()
        if k not in ("command", "action") or not nm:
            return
        entry = (k, nm)
        self._palette_recent = [it for it in self._palette_recent if it != entry]
        self._palette_recent.insert(0, entry)
        limit = max(1, int(self._palette_recent_limit))
        del self._palette_recent[limit:]

    def _command_palette_recent_rank(self, row: list[object]) -> int:
        entry = self._command_palette_row_key(row)
        try:
            return self._palette_recent.index(entry)
        except ValueError:
            return max(1000, len(self._palette_recent) + 100)

    def command_palette_recent_rows(self, *, limit: int | None = None) -> list[list[str]]:
        rows: list[list[str]] = []
        for kind, name in self._palette_recent:
            if kind == "command":
                c = self.command_dispatcher.get(name)
                if c is None:
                    continue
                info = f"group={c.group}" if c.group else ""
                rows.append([str(name), "command", str(c.doc or ""), info])
                continue
            if kind == "action":
                a = self.actions.get(name)
                if a is None:
                    continue
                rows.append([str(name), "action", str(a.doc or ""), ""])
        return rows[:limit] if limit is not None else rows

    def command_palette_recent_file_rows(self, *, limit: int | None = None) -> list[list[str]]:
        """Rows for recent files shown inside the command palette."""
        rows: list[list[str]] = []
        for raw in list(getattr(self, 'recent_files', [])):
            p = str(raw)
            try:
                pp = Path(p)
                menu = str(pp.name) if pp.name else 'file'
                info = str(pp.parent) if str(pp.parent) not in ('.', '') else ''
            except Exception:
                menu, info = 'file', ''
            rows.append([p, 'recentfile', menu, info])
        return rows[:limit] if limit is not None else rows

    def _command_palette_nonrecent_rows(self) -> list[list[str]]:
        recent = {self._command_palette_row_key(row) for row in self.command_palette_recent_rows()}
        out: list[list[str]] = []
        for row in self.command_palette_rows():
            if self._command_palette_row_key(row) in recent:
                continue
            out.append([str(x) for x in row[:4]])
        return out

    def _command_palette_section_label(self, row: list[object]) -> str:
        kind = str(row[1]) if len(row) >= 2 else ""
        if kind == 'openpath':
            return 'Open'
        if kind == 'recentfile':
            return 'Recent Files'
        if self._command_palette_recent_rank(row) < max(1000, len(self._palette_recent) + 100):
            return 'Recent'
        if kind == 'action':
            return 'Actions'
        return 'Commands'

    def _looks_like_path_query(self, q: str) -> bool:
        """Heuristic: does a palette query look like a filesystem path?"""

        s = str(q or "").strip()
        if not s:
            return False
        if any(ch in s for ch in ("/", "\\")):
            return True
        if s.startswith(("./", "../", "~", "/")):
            return True
        if s.endswith((".md", ".mx", ".py", ".json", ".toml", ".yaml", ".yml")):
            return True
        return False

    def command_palette_rows(self) -> list[list[str]]:
        rows: list[list[str]] = []
        for name in self.command_dispatcher.names():
            c = self.command_dispatcher.get(name)
            if c is None:
                continue
            info = f"group={c.group}" if c.group else ""
            rows.append([str(name), "command", str(c.doc or ""), info])
        for name in self.actions.names():
            a = self.actions.get(name)
            if a is None:
                continue
            rows.append([str(name), "action", str(a.doc or ""), ""])

        def _kind_rank(kind: str) -> int:
            return {"recentfile": 0, "command": 1, "action": 2}.get(str(kind), 3)

        rows.sort(key=lambda row: (str(row[0]).casefold(), _kind_rank(str(row[1])), str(row[1]).casefold()))
        return rows

    def command_palette_apropos_rows(self, query: str, *, limit: int | None = None) -> list[list[str]]:
        q = str(query or "").strip()
        file_rows = self.command_palette_recent_file_rows()

        def _path_completion_rows(raw: str, *, limit: int = 60) -> list[list[str]]:
            """Best-effort filesystem path completion rows for the palette.

            This is capability-gated (cap.fs-list) because it exposes host filesystem
            information to scripts/UI surfaces.

            Rows are: [path kind menu info] with kind=openpath and menu=dir|file.
            Directory rows include a trailing '/' so pressing Enter can drill down.
            """

            if not bool(self.options.get("cap.fs-list")):
                return []
            s = str(raw or "").strip()
            if not s:
                return []

            expanded = fs_resolve_path(self, s)

            ends_sep = s.endswith(("/", "\\"))
            try:
                if not ends_sep and expanded.exists() and expanded.is_dir():
                    base = expanded
                    prefix = ""
                elif ends_sep:
                    base = expanded
                    prefix = ""
                else:
                    base = expanded.parent
                    prefix = expanded.name
            except Exception:
                base = expanded.parent
                prefix = expanded.name

            # Optional filesystem sandbox: when cap.fs-root is set, refuse
            # to list outside it (including via symlink escapes).
            if not fs_path_allowed(self, base):
                return []

            try:
                if not base.exists() or not base.is_dir():
                    return []
            except Exception:
                return []

            try:
                items = list(base.iterdir())
            except Exception:
                return []

            want = prefix.casefold()
            rows2: list[list[str]] = []

            # Preserve the user's typed directory prefix (./, ../, ~/, /abs/, etc.)
            # so completion candidates actually match the query string.
            typed_dir = ""
            if ends_sep:
                typed_dir = s
            else:
                try:
                    if expanded.exists() and expanded.is_dir() and not prefix:
                        typed_dir = s
                except Exception:
                    typed_dir = ""
            if typed_dir and not typed_dir.endswith(("/", "\\")):
                typed_dir = typed_dir + "/"
            if not typed_dir:
                slash = max(s.rfind("/"), s.rfind("\\"))
                typed_dir = s[: slash + 1] if slash >= 0 else ""
            typed_dir = typed_dir.replace("\\", "/")


            for child in items:
                name = child.name
                if want and not name.casefold().startswith(want):
                    continue
                is_dir = False
                is_file = False
                try:
                    is_dir = child.is_dir()
                    is_file = child.is_file()
                except Exception:
                    pass
                menu = "dir" if is_dir else "file" if is_file else "other"
                disp = typed_dir + name
                if is_dir and not disp.endswith("/"):
                    disp = disp + "/"
                rows2.append([disp, "openpath", menu, ""])

            def _rank(row: list[str]) -> tuple[int, str]:
                menu = str(row[2])
                return (0 if menu == "dir" else 1, str(row[0]).casefold())

            rows2.sort(key=_rank)
            return rows2[: max(0, int(limit))]

        open_rows: list[list[str]] = []
        if q and self._looks_like_path_query(q):
            open_rows = [[q, "openpath", "open", "path-like query"]]
            open_rows = _path_completion_rows(q, limit=max(0, min(80, int(limit or 60)))) + open_rows
        rows = self.command_palette_rows() + file_rows + open_rows
        if q == "":
            out = file_rows + self.command_palette_recent_rows() + self._command_palette_nonrecent_rows()
            return out[:limit] if limit is not None else out

        scored: list[tuple[tuple[int, int, int, int, int, int, int, int, int, str], int, int, int, list[str]]] = []

        def _kind_rank(kind: str) -> int:
            return {"openpath": 0, "recentfile": 1, "command": 2, "action": 3}.get(str(kind), 4)

        for idx, row in enumerate(rows):
            key = self._apropos_row_sort_key(row, q)
            if key is None:
                continue
            recent_rank = self._command_palette_recent_rank(row)
            scored.append((key, recent_rank, _kind_rank(str(row[1])), idx, [str(x) for x in row]))

        scored.sort(
            key=lambda item: (
                item[0][:-2],
                item[1],
                item[0][-2],
                item[0][-1],
                item[2],
                item[3],
            )
        )
        out = [row for _key, _recent, _rank, _idx, row in scored]
        return out[:limit] if limit is not None else out

    def command_palette_section_rows(self, query: str = "", *, limit: int | None = None) -> list[list[object]]:
        rows = self.command_palette_apropos_rows(query, limit=limit)
        section_order = ["Open", "Recent Files", "Recent", "Commands", "Actions"]
        buckets: dict[str, list[list[str]]] = {label: [] for label in section_order}
        for row in rows:
            vals = [str(x) for x in list(row[:4])]
            while len(vals) < 4:
                vals.append("")
            label = self._command_palette_section_label(vals)
            buckets.setdefault(label, [])
            buckets[label].append(vals)
        out: list[list[object]] = []
        for label in section_order:
            items = buckets.get(label, [])
            if items:
                out.append([label, items])
        return out

    def help_topic_rows(self) -> list[list[str]]:
        rows = self.command_palette_rows()
        for name in self._prompt_vm_word_names():
            row = self._prompt_vm_word_row(name)
            rows.append([str(name), str(row[1]), str(row[2]), str(row[3])])
        return rows

    def _topic_section_names(self, kind: str) -> tuple[str, str]:
        k = str(kind or "").strip().casefold()
        if k == "command":
            return ("Command", "Commands")
        if k == "action":
            return ("Action", "Actions")
        if k == "buffer":
            return ("Buffer", "Buffers")
        if k == "mark":
            return ("Mark", "Marks")
        if k == "jump":
            return ("Jump", "Jumps")
        if k == "doc":
            return ("Doc", "Docs")
        if k == "link":
            return ("Link", "Links")
        if k in ("recent", "recentfile"):
            return ("Recent file", "Recent files")
        return ("Word", "Words")

    def _group_topic_rows(self, rows: list[list[str]]) -> list[list[object]]:
        section_order = ["Commands", "Actions", "Words"]
        buckets: dict[str, list[list[str]]] = {label: [] for label in section_order}
        extra_labels: list[str] = []
        for row in rows:
            vals = [str(x) for x in list(row[:4])]
            while len(vals) < 4:
                vals.append("")
            _single, plural = self._topic_section_names(vals[1])
            if plural not in buckets:
                buckets[plural] = []
                extra_labels.append(plural)
            buckets[plural].append(vals)
        out: list[list[object]] = []
        for label in section_order + extra_labels:
            items = buckets.get(label, [])
            if items:
                out.append([label, items])
        return out

    def help_topic_section_rows(self) -> list[list[object]]:
        return self._group_topic_rows(self.help_topic_rows())

    def apropos_rows(self, query: str, *, limit: int | None = None) -> list[list[str]]:
        q = str(query or "").strip()
        rows = self.help_topic_rows()
        if q == "":
            return rows[:limit] if limit is not None else rows

        scored: list[tuple[tuple[int, int, int, int, int, int, int, int, str], int, int, list[str]]] = []

        def _kind_rank(kind: str) -> int:
            return {"recentfile": 0, "command": 1, "action": 2}.get(str(kind), 3)

        for idx, row in enumerate(rows):
            key = self._apropos_row_sort_key(row, q)
            if key is None:
                continue
            scored.append((key, _kind_rank(str(row[1])), idx, [str(x) for x in row]))

        scored.sort(key=lambda item: (item[0], item[1], item[2]))
        out = [row for _key, _rank, _idx, row in scored]
        return out[:limit] if limit is not None else out

    def apropos_section_rows(self, query: str, *, limit: int | None = None) -> list[list[object]]:
        return self._group_topic_rows(self.apropos_rows(query, limit=limit))

    def binding_prompt_rows(self) -> list[list[str]]:
        rows: list[list[str]] = []
        for mode, key, action, desc, _group, _span in self.available_binding_info_rows():
            mode_s = str(mode or "global")
            menu = f"@{mode_s} {action}"
            info = str(desc or "")
            rows.append([str(key), "binding", menu, info])
        rows.sort(key=lambda row: (str(row[0]).casefold(), str(row[2]).casefold(), str(row[3]).casefold()))
        return rows



    def _buffer_section_label(self, row: list[str]) -> str:
        """Best-effort section label for buffer picker rows.

        Used by the TUI to render section headers (and by the prompt row sorter so
        buffers appear grouped rather than interleaved).
        """
        try:
            name = str(row[0] if row else "")
            if name.startswith("help:"):
                return "Help"
            if name.startswith("*"):
                return "Scratch"
            info = str(row[3] if len(row) > 3 else "")
            path = info.split("|", 1)[0].strip() if info else ""
            if path:
                try:
                    root = self._project_root_for_path(path)
                except Exception:
                    root = None
                if root:
                    return str(root)
                try:
                    return str(Path(path).parent)
                except Exception:
                    return "(unknown)"
        except Exception:
            pass
        return "Buffers"

    def _buffer_section_sort_key(self, row: list[str]) -> tuple[int, str, str]:
        label = self._buffer_section_label(row)
        rank = 2
        if label == "Help":
            rank = 0
        elif label == "Scratch":
            rank = 1
        elif label == "Buffers":
            rank = 1
        name = str(row[0] if row else "")
        return (int(rank), str(label).casefold(), name.casefold())


    def buffer_prompt_rows(self) -> list[list[str]]:
        rows: list[list[str]] = []
        for name in self.buffer_names():
            insert = str(name)
            row = self._prompt_buffer_row(insert)
            # _prompt_buffer_row expects an 'insert' string; ensure 4 cols
            vals = list(row[:4])
            while len(vals) < 4:
                vals.append("")
            rows.append([str(vals[0]), str(vals[1]), str(vals[2]), str(vals[3])])
        rows.sort(key=self._buffer_section_sort_key)
        return rows

    def plugin_names(self) -> list[str]:
        pm = getattr(self, "plugin_manager", None)
        names: set[str] = set()
        if pm is not None:
            try:
                names.update(str(n) for n in getattr(pm, "plugins", {}).keys())
            except Exception:
                pass
            try:
                names.update(str(n) for n in getattr(pm, "candidates", {}).keys())
            except Exception:
                pass
            try:
                names.update(str(n) for (n, _e) in getattr(pm, "load_errors", []))
            except Exception:
                pass
        return sorted({str(n) for n in names if str(n).strip() != ""}, key=lambda s: s.casefold())


    def _plugin_section_label(self, row: list[str]) -> str:
        """Best-effort section label for plugin picker rows."""
        try:
            menu = str(row[2] if len(row) > 2 else "")
            low = menu.casefold()
            if "error" in low:
                return "Errors"
            if low.startswith("loaded"):
                return "Loaded"
            return "Available"
        except Exception:
            return "Plugins"

    def _plugin_section_sort_key(self, row: list[str]) -> tuple[int, str, str]:
        label = self._plugin_section_label(row)
        rank = {"Errors": 0, "Loaded": 1, "Available": 2}.get(label, 3)
        name = str(row[0] if row else "")
        return (int(rank), str(label).casefold(), name.casefold())


    def plugin_prompt_rows(self) -> list[list[str]]:
        rows: list[list[str]] = []
        for name in self.plugin_names():
            insert = str(name)
            row = self._prompt_plugin_row(insert)
            vals = list(row[:4])
            while len(vals) < 4:
                vals.append("")
            rows.append([str(vals[0]), str(vals[1]), str(vals[2]), str(vals[3])])
        rows.sort(key=self._plugin_section_sort_key)
        return rows

    def _plugin_row_sort_key(self, row: list[object], query: str) -> tuple[int, int, int, int, int, int, int, int, int, str] | None:
        q = str(query or "").strip()
        if q == "":
            return (0, 0, 0, 0, 0, 0, 0, 0, 0, "")

        key = str(row[0]) if row else ""
        key_key = self._completion_fuzzy_sort_key(key, q)
        if key_key is not None:
            return (0, *key_key, key.casefold())

        meta = " ".join([str(row[2]) if len(row) >= 3 else "", str(row[3]) if len(row) >= 4 else ""]).strip()
        if meta:
            folded_meta = meta.casefold()
            folded_q = q.casefold()
            if folded_q and folded_q in folded_meta:
                pos = folded_meta.find(folded_q)
                return (1, pos, pos, 0, 0, 0, 0, len(meta), len(key), key.casefold())

            meta_key = self._completion_fuzzy_sort_key(meta, q)
            if meta_key is not None:
                return (2, *meta_key, key.casefold())
        return None

    def plugin_apropos_rows(self, query: str, *, limit: int | None = None) -> list[list[str]]:
        q = str(query or "").strip()
        rows = self.plugin_prompt_rows()
        if q == "":
            return rows[:limit] if limit is not None else rows

        scored: list[tuple[tuple[int, int, int, int, int, int, int, int, int, str], int, list[str]]] = []
        for idx, row in enumerate(rows):
            key = self._plugin_row_sort_key(row, q)
            if key is None:
                continue
            scored.append((key, idx, [str(x) for x in row]))

        scored.sort(key=lambda item: (item[0], item[1]))
        out = [row for _key, _idx, row in scored]
        return out[:limit] if limit is not None else out


    def _buffer_row_sort_key(self, row: list[object], query: str) -> tuple[int, int, int, int, int, int, int, int, int, str] | None:
        q = str(query or "").strip()
        if q == "":
            return (0, 0, 0, 0, 0, 0, 0, 0, 0, "")

        key = str(row[0]) if row else ""
        key_key = self._completion_fuzzy_sort_key(key, q)
        if key_key is not None:
            return (0, *key_key, key.casefold())

        info = str(row[3]) if len(row) >= 4 else ""
        if info:
            folded_info = info.casefold()
            folded_q = q.casefold()
            if folded_q and folded_q in folded_info:
                pos = folded_info.find(folded_q)
                return (1, pos, pos, 0, 0, 0, 0, len(info), len(key), key.casefold())
            info_key = self._completion_fuzzy_sort_key(info, q)
            if info_key is not None:
                return (2, *info_key, key.casefold())

        menu = str(row[2]) if len(row) >= 3 else ""
        if menu:
            folded_menu = menu.casefold()
            folded_q = q.casefold()
            if folded_q and folded_q in folded_menu:
                pos = folded_menu.find(folded_q)
                return (3, pos, pos, 0, 0, 0, 0, len(menu), len(key), key.casefold())
            menu_key = self._completion_fuzzy_sort_key(menu, q)
            if menu_key is not None:
                return (4, *menu_key, key.casefold())

        multi_key = self._multi_term_field_key([(0, key), (1, info), (2, menu)], q, fallback_rank=5, tie_name=key)
        if multi_key is not None:
            return multi_key
        return None

    def buffer_apropos_rows(self, query: str, *, limit: int | None = None) -> list[list[str]]:
        q = str(query or "").strip()
        rows = self.buffer_prompt_rows()
        if q == "":
            return rows[:limit] if limit is not None else rows

        scored: list[tuple[tuple[int, int, int, int, int, int, int, int, int, str], int, list[str]]] = []
        for idx, row in enumerate(rows):
            key = self._buffer_row_sort_key(row, q)
            if key is None:
                continue
            scored.append((key, idx, [str(x) for x in row]))

        scored.sort(key=lambda item: (item[0], item[1]))
        out = [row for _key, _idx, row in scored]
        return out[:limit] if limit is not None else out

    def mark_prompt_rows(self) -> list[list[str]]:
        rows: list[list[str]] = []
        for name in sorted(self.marks.keys()):
            insert = str(name)
            row = self._prompt_mark_row(insert)
            vals = list(row[:4])
            while len(vals) < 4:
                vals.append("")
            rows.append([str(vals[0]), str(vals[1]), str(vals[2]), str(vals[3])])
        rows.sort(key=lambda r: (str(r[0]).casefold(), str(r[2]).casefold(), str(r[3]).casefold()))
        return rows

    def _mark_row_sort_key(self, row: list[object], query: str) -> tuple[int, int, int, int, int, int, int, int, int, str] | None:
        q = str(query or "").strip()
        if q == "":
            return (0, 0, 0, 0, 0, 0, 0, 0, 0, "")

        key = str(row[0]) if row else ""
        key_key = self._completion_fuzzy_sort_key(key, q)
        if key_key is not None:
            return (0, *key_key, key.casefold())

        info = str(row[3]) if len(row) >= 4 else ""
        if info:
            folded_info = info.casefold()
            folded_q = q.casefold()
            if folded_q and folded_q in folded_info:
                pos = folded_info.find(folded_q)
                return (1, pos, pos, 0, 0, 0, 0, len(info), len(key), key.casefold())
            info_key = self._completion_fuzzy_sort_key(info, q)
            if info_key is not None:
                return (2, *info_key, key.casefold())

        menu = str(row[2]) if len(row) >= 3 else ""
        if menu:
            folded_menu = menu.casefold()
            folded_q = q.casefold()
            if folded_q and folded_q in folded_menu:
                pos = folded_menu.find(folded_q)
                return (3, pos, pos, 0, 0, 0, 0, len(menu), len(key), key.casefold())
            menu_key = self._completion_fuzzy_sort_key(menu, q)
            if menu_key is not None:
                return (4, *menu_key, key.casefold())

        multi_key = self._multi_term_field_key([(0, key), (1, info), (2, menu)], q, fallback_rank=5, tie_name=key)
        if multi_key is not None:
            return multi_key
        return None

    def mark_apropos_rows(self, query: str, *, limit: int | None = None) -> list[list[str]]:
        q = str(query or "").strip()
        rows = self.mark_prompt_rows()
        if q == "":
            return rows[:limit] if limit is not None else rows

        scored: list[tuple[tuple[int, int, int, int, int, int, int, int, int, str], int, list[str]]] = []
        for idx, row in enumerate(rows):
            key = self._mark_row_sort_key(row, q)
            if key is None:
                continue
            scored.append((key, idx, [str(x) for x in row]))

        scored.sort(key=lambda item: (item[0], item[1]))
        out = [row for _key, _idx, row in scored]
        return out[:limit] if limit is not None else out



    def jump_prompt_rows(self) -> list[list[str]]:
        """Return jumplist picker rows for the current buffer.

        Rows are [[insert kind menu info] ...]. `insert` is a 1-based jumplist
        index so users can type a number, while `menu`/`info` carry the useful
        context for fuzzy search.
        """
        eb = self.cur()
        self._normalize_cursor_lists(eb)
        rows: list[list[str]] = []
        n = int(len(eb.jump_list))
        # Newest-first feels best for navigation history.
        for idx0 in range(n - 1, -1, -1):
            snap = eb.jump_list[idx0]
            curs, _anchors, _cursor_ids, primary = snap
            if not curs:
                continue
            pi = int(primary) if 0 <= int(primary) < len(curs) else 0
            c = curs[pi]
            insert = str(idx0 + 1)
            marker = "*" if idx0 == int(eb.jump_index) else " "
            menu = f"{marker}{idx0 + 1}/{n} {int(c.line) + 1}:{int(c.col) + 1}"
            info = ""
            li = int(c.line)
            if 0 <= li < len(eb.buf.lines):
                s = eb.buf.lines[li].rstrip("\n").strip()
                if len(s) > 80:
                    s = s[:77] + "..."
                info = s
            rows.append([insert, "jump", str(menu), str(info)])
        return rows

    def _jump_row_sort_key(self, row: list[object], query: str) -> tuple[int, int, int, int, int, int, int, int, int, str] | None:
        q = str(query or "").strip()
        if q == "":
            return (0, 0, 0, 0, 0, 0, 0, 0, 0, "")

        key = str(row[0]) if row else ""
        key_key = self._completion_fuzzy_sort_key(key, q)
        if key_key is not None:
            return (0, *key_key, key.casefold())

        info = str(row[3]) if len(row) >= 4 else ""
        if info:
            folded_info = info.casefold()
            folded_q = q.casefold()
            if folded_q and folded_q in folded_info:
                pos = folded_info.find(folded_q)
                return (1, pos, pos, 0, 0, 0, 0, len(info), len(key), key.casefold())
            info_key = self._completion_fuzzy_sort_key(info, q)
            if info_key is not None:
                return (2, *info_key, key.casefold())

        menu = str(row[2]) if len(row) >= 3 else ""
        if menu:
            folded_menu = menu.casefold()
            folded_q = q.casefold()
            if folded_q and folded_q in folded_menu:
                pos = folded_menu.find(folded_q)
                return (3, pos, pos, 0, 0, 0, 0, len(menu), len(key), key.casefold())
            menu_key = self._completion_fuzzy_sort_key(menu, q)
            if menu_key is not None:
                return (4, *menu_key, key.casefold())

        multi_key = self._multi_term_field_key([(0, key), (1, info), (2, menu)], q, fallback_rank=5, tie_name=key)
        if multi_key is not None:
            return multi_key
        return None

    def jump_apropos_rows(self, query: str, *, limit: int | None = None) -> list[list[str]]:
        q = str(query or "").strip()
        rows = self.jump_prompt_rows()
        if q == "":
            return rows[:limit] if limit is not None else rows

        scored: list[tuple[tuple[int, int, int, int, int, int, int, int, int, str], int, list[str]]] = []
        for idx0, row in enumerate(rows):
            key = self._jump_row_sort_key(row, q)
            if key is None:
                continue
            scored.append((key, idx0, [str(x) for x in row]))

        scored.sort(key=lambda item: (item[0], item[1]))
        out = [row for _key, _idx, row in scored]
        return out[:limit] if limit is not None else out
    def _binding_row_sort_key(self, row: list[object], query: str) -> tuple[int, int, int, int, int, int, int, int, int, str] | None:
        q = str(query or "").strip()
        if q == "":
            return (0, 0, 0, 0, 0, 0, 0, 0, 0, "")

        key = str(row[0]) if row else ""
        key_key = self._completion_fuzzy_sort_key(key, q)
        if key_key is not None:
            return (0, *key_key, key.casefold())

        info = str(row[3]) if len(row) >= 4 else ""
        if info:
            folded_info = info.casefold()
            folded_q = q.casefold()
            if folded_q and folded_q in folded_info:
                pos = folded_info.find(folded_q)
                return (1, pos, pos, 0, 0, 0, 0, len(info), len(key), key.casefold())
            info_key = self._completion_fuzzy_sort_key(info, q)
            if info_key is not None:
                return (2, *info_key, key.casefold())

        menu = str(row[2]) if len(row) >= 3 else ""
        if menu:
            folded_menu = menu.casefold()
            folded_q = q.casefold()
            if folded_q and folded_q in folded_menu:
                pos = folded_menu.find(folded_q)
                return (3, pos, pos, 0, 0, 0, 0, len(menu), len(key), key.casefold())
            menu_key = self._completion_fuzzy_sort_key(menu, q)
            if menu_key is not None:
                return (4, *menu_key, key.casefold())

        multi_key = self._multi_term_field_key([(0, key), (1, info), (2, menu)], q, fallback_rank=5, tie_name=key)
        if multi_key is not None:
            return multi_key
        return None

    def binding_apropos_rows(self, query: str, *, limit: int | None = None) -> list[list[str]]:
        q = str(query or "").strip()
        rows = self.binding_prompt_rows()
        if q == "":
            return rows[:limit] if limit is not None else rows

        scored: list[tuple[tuple[int, int, int, int, int, int, int, int, str], int, list[str]]] = []
        for idx, row in enumerate(rows):
            key = self._binding_row_sort_key(row, q)
            if key is None:
                continue
            scored.append((key, idx, [str(x) for x in row]))

        scored.sort(key=lambda item: (item[0], item[1]))
        out = [row for _key, _idx, row in scored]
        return out[:limit] if limit is not None else out

    def _prompt_commandish_suggestion_rows(
        self,
        *,
        cmd: str,
        toks: list[str],
        tok_i: int,
        candidates: list[str],
    ) -> list[list[str]]:
        rows: list[list[str]] = []
        for cand in candidates:
            insert = str(cand)
            raw = insert[:-1] if insert.endswith(" ") else insert
            row = [insert, "", "", ""]

            if tok_i == 0:
                c = self.command_dispatcher.get(raw)
                if c is not None:
                    info = ""
                    if c.group:
                        info = f"group={c.group}"
                    row = [insert, "command", str(c.doc or ""), info]
                rows.append(row)
                continue

            if tok_i == 1 and cmd in ("set", "setlocal", "show", "toggle", "togglelocal"):
                rows.append(self._prompt_option_row(raw, local=(cmd in ("setlocal", "togglelocal"))))
                continue

            if tok_i == 2 and cmd in ("set", "setlocal") and len(toks) >= 2:
                name = str(toks[1])
                spec = self.options.specs.get(name)
                cur_local = self.cur().local_options if cmd == "setlocal" else None
                cur = None
                if spec is not None:
                    cur = self.options.get(name, local=cur_local)
                menu = f"value for {name}"
                if cur is not None and raw == self._prompt_display_value(cur):
                    menu = menu + " (current)"
                info = str(spec.doc or "") if spec is not None else ""
                row = [insert, "value", menu, info]
                rows.append(row)
                continue

            if tok_i == 1 and cmd in ("help", "apropos"):
                topic_kind = "help topic" if cmd == "help" else "search topic"
                c = self.command_dispatcher.get(raw)
                if c is not None:
                    rows.append([insert, "command", str(c.doc or ""), topic_kind])
                    continue
                a = self.actions.get(raw)
                if a is not None:
                    rows.append([insert, "action", str(a.doc or ""), topic_kind])
                    continue
                rows.append(self._prompt_vm_word_row(insert))
                continue

            if tok_i == 1 and cmd == "commandpick":
                c = self.command_dispatcher.get(raw)
                if c is not None:
                    rows.append([insert, "command", str(c.doc or ""), "command palette"])
                    continue
                a = self.actions.get(raw)
                if a is not None:
                    rows.append([insert, "action", str(a.doc or ""), "command palette"])
                    continue

            if tok_i == 1 and cmd == "showcmd":
                c = self.command_dispatcher.get(raw)
                if c is not None:
                    rows.append([insert, "command", str(c.doc or ""), "inspect command"])
                    continue

            if tok_i == 1 and cmd == "showhook":
                rows.append([insert, "hook", "hook", "inspect hook"])
                continue

            if tok_i == 1 and cmd == "showword":
                rows.append(self._prompt_vm_word_row(insert))
                continue

            if tok_i == 1 and cmd == "buffer":
                rows.append(self._prompt_buffer_row(insert))
                continue

            if tok_i == 1 and cmd in ("mark", "markjump"):
                rows.append(self._prompt_mark_row(insert))
                continue

            if tok_i == 1 and cmd == "plugin":
                rows.append([insert, "subcommand", "plugin action", ""])
                continue

            if tok_i == 2 and cmd == "plugin" and len(toks) >= 2 and str(toks[1]) in ("reload", "info", "errors"):
                rows.append(self._prompt_plugin_row(insert))
                continue

            if tok_i == 1 and cmd == "macro":
                rows.append([insert, "subcommand", "macro action", ""])
                continue

            if tok_i == 2 and cmd == "macro" and len(toks) >= 2 and toks[1] in ("play", "record", "rec", "start"):
                rows.append([insert, "macro", "macro slot", ""])
                continue

            if tok_i == 1 and cmd in ("keymode", "pushkeymode", "pushkeymode-once", "prefixmode"):
                menu = "active keymode" if raw in self.active_key_modes() else "keymode"
                rows.append([insert, "keymode", menu, ""])
                continue

            if tok_i == 1 and cmd == "showbindings":
                if raw == "active":
                    rows.append([insert, "special", "currently active keymodes", ""])
                else:
                    menu = "active keymode" if raw in self.active_key_modes() else "keymode"
                    rows.append([insert, "keymode", menu, "show bindings"])
                continue

            if tok_i == 1 and cmd in ("bindmode", "bindmodedoc", "unbindmode", "bindmodeprefix"):
                rows.append([insert, "keymode", "owner mode", ""])
                continue

            if tok_i == 3 and cmd == "bindmodeprefix":
                rows.append([insert, "keymode", "prefix mode", ""])
                continue

            rows.append(row)
        return rows

    def _prompt_bind_suggestion_rows(
        self,
        *,
        cmd: str,
        toks: list[str],
        tok_i: int,
        candidates: list[str],
    ) -> list[list[str]]:
        action_tok_i = 2 if cmd == "bind" else 3
        if tok_i < action_tok_i or len(toks) <= action_tok_i:
            return [[str(c), "", "", ""] for c in candidates]

        action_head = toks[action_tok_i]
        for lead in ("command-edit:", "command:"):
            if action_head.startswith(lead):
                first = action_head[len(lead):]
                nested_toks = [first] + toks[action_tok_i + 1 :]
                nested_tok_i = tok_i - action_tok_i
                if nested_tok_i == 0:
                    rows: list[list[str]] = []
                    for cand in candidates:
                        insert = str(cand)
                        raw = insert[:-1] if insert.endswith(" ") else insert
                        if raw.startswith(lead):
                            nested_raw = raw[len(lead):]
                        else:
                            nested_raw = raw
                        nested_rows = self._prompt_commandish_suggestion_rows(
                            cmd=nested_raw,
                            toks=[nested_raw],
                            tok_i=0,
                            candidates=[nested_raw + (" " if insert.endswith(" ") else "")],
                        )
                        nr = nested_rows[0] if nested_rows else [nested_raw, "command", "", ""]
                        rows.append([insert, "binding-command", nr[2], lead[:-1]])
                    return rows
                return self._prompt_commandish_suggestion_rows(
                    cmd=(nested_toks[0] if nested_toks else ""),
                    toks=nested_toks,
                    tok_i=nested_tok_i,
                    candidates=candidates,
                )

        if tok_i == action_tok_i:
            rows: list[list[str]] = []
            for cand in candidates:
                insert = str(cand)
                raw = insert[:-1] if insert.endswith(" ") else insert
                if raw in ("command:", "command-edit:"):
                    rows.append([insert, "binding-prefix", "binding command rhs", ""])
                    continue
                a = self.actions.get(raw)
                if a is not None:
                    rows.append([insert, "action", str(a.doc or ""), "binding rhs"])
                    continue
                rows.append([insert, "", "", ""])
            return rows

        return [[str(c), "", "", ""] for c in candidates]

    def _prompt_suggestion_rows(
        self,
        *,
        cmd: str,
        toks: list[str],
        tok_i: int,
        candidates: list[str],
        path_mode: bool = False,
    ) -> list[list[str]]:
        if path_mode:
            return [self._prompt_path_row(c) for c in candidates]
        if cmd in ("bind", "bindmode"):
            return self._prompt_bind_suggestion_rows(cmd=cmd, toks=toks, tok_i=tok_i, candidates=candidates)
        return self._prompt_commandish_suggestion_rows(cmd=cmd, toks=toks, tok_i=tok_i, candidates=candidates)

    def _prompt_action_spec_prefix_candidates(
        self,
        prefix: str,
        *,
        at_eol: bool,
    ) -> tuple[list[str], bool]:
        names = list(self.actions.names()) + ["command:", "command-edit:"]
        chosen, fuzzy = self._completion_candidates_for_prefix(names, prefix, at_eol=False)
        out: list[str] = []
        for c in chosen:
            if c.endswith(":"):
                out.append(c)
            elif at_eol:
                out.append(c + " ")
            else:
                out.append(c)
        return (out, fuzzy)

    def _prompt_bind_action_candidates(
        self,
        *,
        cmd: str,
        toks: list[str],
        tok_i: int,
        prefix: str,
        at_eol: bool,
    ) -> tuple[list[str], bool]:
        if cmd == "bind":
            action_tok_i = 2
        elif cmd == "bindmode":
            action_tok_i = 3
        else:
            return ([], False)

        if tok_i < action_tok_i or len(toks) <= action_tok_i:
            return ([], False)

        action_head = toks[action_tok_i]
        for lead in ("command-edit:", "command:"):
            if action_head.startswith(lead):
                first = action_head[len(lead) :]
                nested_toks = [first] + toks[action_tok_i + 1 :]
                nested_tok_i = tok_i - action_tok_i
                nested_cmd = nested_toks[0] if nested_toks else ""
                nested_prefix = first if nested_tok_i == 0 else prefix
                candidates, fuzzy = self._prompt_command_token_candidates(
                    cmd=nested_cmd,
                    toks=nested_toks,
                    tok_i=nested_tok_i,
                    prefix=nested_prefix,
                    at_eol=at_eol,
                )
                if nested_tok_i == 0:
                    candidates = [lead + c for c in candidates]
                return (candidates, fuzzy)

        if tok_i == action_tok_i:
            return self._prompt_action_spec_prefix_candidates(prefix, at_eol=at_eol)
        return ([], False)

    def _prompt_command_token_candidates(
        self,
        *,
        cmd: str,
        toks: list[str],
        tok_i: int,
        prefix: str,
        at_eol: bool,
    ) -> tuple[list[str], bool]:
        if tok_i == 0:
            return self._completion_candidates_for_prefix(
                self.command_dispatcher.names(),
                prefix,
                at_eol=at_eol,
            )
        if tok_i == 1 and cmd in ("set", "setlocal", "show", "toggle", "togglelocal"):
            return self._completion_candidates_for_prefix(
                list(self.options.specs.keys()),
                prefix,
                at_eol=at_eol,
            )
        if tok_i == 2 and cmd in ("set", "setlocal") and len(toks) >= 2:
            return self._prompt_option_value_candidates(toks[1], prefix, at_eol=at_eol)
        if tok_i == 1 and cmd in ("help", "apropos"):
            return self._completion_candidates_for_prefix(
                self._prompt_help_topic_names(),
                prefix,
                at_eol=at_eol,
            )
        if tok_i == 1 and cmd == "commandpick":
            return self._completion_candidates_for_prefix(
                self._prompt_command_palette_names(),
                prefix,
                at_eol=at_eol,
            )
        if tok_i == 1 and cmd == "showcmd":
            return self._completion_candidates_for_prefix(
                list(self.command_dispatcher.names()),
                prefix,
                at_eol=at_eol,
            )
        if tok_i == 1 and cmd == "showhook":
            return self._completion_candidates_for_prefix(
                self._prompt_hook_names(),
                prefix,
                at_eol=at_eol,
            )
        if tok_i == 1 and cmd == "showword":
            return self._completion_candidates_for_prefix(
                self._prompt_vm_word_names(),
                prefix,
                at_eol=at_eol,
            )

        if tok_i == 1 and cmd == "buffer":
            return self._completion_candidates_for_prefix(
                self.buffer_names(),
                prefix,
                at_eol=at_eol,
            )
        if tok_i == 1 and cmd in ("mark", "markjump"):
            return self._completion_candidates_for_prefix(
                sorted(list(self.marks.keys())),
                prefix,
                at_eol=at_eol,
            )
        if tok_i == 1 and cmd == "plugin":
            return self._completion_candidates_for_prefix(
                ["list", "reload", "info", "errors"],
                prefix,
                at_eol=at_eol,
            )
        if tok_i == 2 and cmd == "plugin" and len(toks) >= 2:
            sub = str(toks[1])
            if sub == "reload":
                if self.plugin_manager:
                    return self._completion_candidates_for_prefix(
                        list(self.plugin_manager.plugins.keys()),
                        prefix,
                        at_eol=at_eol,
                    )
                return ([], False)
            if sub in ("info", "errors"):
                return self._completion_candidates_for_prefix(
                    self.plugin_names(),
                    prefix,
                    at_eol=at_eol,
                )
        if tok_i == 1 and cmd == "macro":
            return self._completion_candidates_for_prefix(
                ["record", "stop", "cancel", "play", "list"],
                prefix,
                at_eol=at_eol,
            )
        if tok_i == 2 and cmd == "macro" and len(toks) >= 2 and toks[1] in ("play", "record", "rec", "start"):
            return self._completion_candidates_for_prefix(
                list(self.macros.keys()),
                prefix,
                at_eol=at_eol,
            )
        if tok_i == 1 and cmd in ("keymode", "pushkeymode", "pushkeymode-once", "prefixmode"):
            mode_names = [m for m in self._prompt_known_keymodes() if m != "global"]
            if cmd == "keymode":
                mode_names = ["global"] + mode_names
            return self._completion_candidates_for_prefix(
                mode_names,
                prefix,
                at_eol=at_eol,
            )
        if tok_i == 1 and cmd == "showbindings":
            return self._completion_candidates_for_prefix(
                ["active"] + self._prompt_known_keymodes(),
                prefix,
                at_eol=at_eol,
            )
        if tok_i == 1 and cmd in ("bindmode", "bindmodedoc", "unbindmode"):
            mode_names = [m for m in self._prompt_known_keymodes() if m != "global"]
            return self._completion_candidates_for_prefix(
                mode_names,
                prefix,
                at_eol=at_eol,
            )
        if tok_i == 1 and cmd == "bindmodeprefix":
            mode_names = [m for m in self._prompt_known_keymodes() if m != "global"]
            return self._completion_candidates_for_prefix(
                mode_names,
                prefix,
                at_eol=at_eol,
            )
        if tok_i == 3 and cmd == "bindmodeprefix":
            mode_names = [m for m in self._prompt_known_keymodes() if m != "global"]
            return self._completion_candidates_for_prefix(
                mode_names,
                prefix,
                at_eol=at_eol,
            )
        if cmd in ("bind", "bindmode"):
            return self._prompt_bind_action_candidates(
                cmd=cmd,
                toks=toks,
                tok_i=tok_i,
                prefix=prefix,
                at_eol=at_eol,
            )
        return ([], False)

    # ----- keymap modes -----
    def active_key_mode_rows(self) -> list[list[object]]:
        out: list[list[object]] = []
        seen: set[str] = set()
        for km in reversed(self.key_mode_stack):
            m = str(km.name)
            if not m or m == 'global' or m in seen:
                continue
            seen.add(m)
            out.append([m, 1 if km.once else 0])
        return out

    def active_key_modes(self) -> list[str]:
        return [str(row[0]) for row in self.active_key_mode_rows()]

    def current_key_mode(self) -> str | None:
        modes = self.active_key_modes()
        return modes[0] if modes else None

    def current_key_mode_once(self) -> bool:
        rows = self.active_key_mode_rows()
        return bool(rows and rows[0][1])

    def set_key_mode(self, mode: str | None, *, capture: bool = False) -> None:
        if mode is None or str(mode) == '' or str(mode) == 'global':
            self.key_mode_stack = []
            return
        self.key_mode_stack = [ActiveKeyMode(str(mode), once=False, capture=bool(capture))]

    def push_key_mode(self, mode: str, *, once: bool = False, capture: bool = False) -> None:
        m = str(mode)
        if not m or m == 'global':
            return
        self.key_mode_stack.append(ActiveKeyMode(m, once=bool(once), capture=bool(capture)))

    def pop_key_mode(self) -> str | None:
        if not self.key_mode_stack:
            return None
        return self.key_mode_stack.pop().name

    def _install_builtin_keymode_bindings(self) -> None:
        """Install tiny internal keymode bindings that must work without plugins.

        Plugins are expected to provide the full default keymap, but some
        modal/editor-internal loops (like query-replace) should remain usable
        even in a headless test harness or minimal embed.
        """

        # Query-replace confirmation loop (capture mode).
        self.keymap.bind("y", "QueryReplaceYes", mode="qreplace")
        self.keymap.bind("Y", "QueryReplaceYes", mode="qreplace")
        self.keymap.bind("Enter", "QueryReplaceYes", mode="qreplace")

        self.keymap.bind("n", "QueryReplaceNo", mode="qreplace")
        self.keymap.bind("N", "QueryReplaceNo", mode="qreplace")

        self.keymap.bind("a", "QueryReplaceAll", mode="qreplace")
        self.keymap.bind("A", "QueryReplaceAll", mode="qreplace")

        self.keymap.bind("l", "QueryReplaceLast", mode="qreplace")
        self.keymap.bind("L", "QueryReplaceLast", mode="qreplace")

        self.keymap.bind("q", "QueryReplaceQuit", mode="qreplace")
        self.keymap.bind("Q", "QueryReplaceQuit", mode="qreplace")
        self.keymap.bind("Esc", "QueryReplaceQuit", mode="qreplace")

        # External URL open confirmation loop (capture mode).
        # This keeps docs browsing safe-by-default even when cap.open-url is enabled.
        self.keymap.bind("y", "OpenUrlYes", mode="openurl")
        self.keymap.bind("Y", "OpenUrlYes", mode="openurl")
        self.keymap.bind("Enter", "OpenUrlYes", mode="openurl")

        self.keymap.bind("n", "OpenUrlNo", mode="openurl")
        self.keymap.bind("N", "OpenUrlNo", mode="openurl")
        self.keymap.bind("Esc", "OpenUrlNo", mode="openurl")

        self.keymap.bind("c", "OpenUrlCopy", mode="openurl")
        self.keymap.bind("C", "OpenUrlCopy", mode="openurl")

        # Prompt picker navigation (non-command prompts).
        # This makes built-in pickers usable even without plugins.
        self.keymap.bind("UpArrow", "PromptSuggestPrev|PromptHistoryPrev", mode="prompt")
        self.keymap.bind("DownArrow", "PromptSuggestNext|PromptHistoryNext", mode="prompt")
        # PageUp/PageDown jump by a small window in picker lists (without mutating the query).
        # For command/find prompts, these fall back to history navigation.
        self.keymap.bind("PageUp", "PromptSuggestPageUp|PromptHistoryPrev", mode="prompt")
        self.keymap.bind("PageDown", "PromptSuggestPageDown|PromptHistoryNext", mode="prompt")
        # Section jumps for grouped suggestion lists.
        self.keymap.bind("Alt-UpArrow", "PromptSuggestPrevSection", mode="prompt")
        self.keymap.bind("Alt-DownArrow", "PromptSuggestNextSection", mode="prompt")
        self.keymap.bind("Ctrl-y", "PromptCopySelected", mode="prompt")
        self.keymap.bind("Ctrl-Home", "PromptSuggestFirst|PromptHome", mode="prompt")
        self.keymap.bind("Ctrl-End", "PromptSuggestLast|PromptEnd", mode="prompt")

    # ----- prompt keymode -----
    def _push_prompt_keymode(self) -> None:
        # Reserve the keymap mode name "prompt" for the built-in prompt bar.
        self.key_mode_stack = [km for km in self.key_mode_stack if km.name != 'prompt']
        self.key_mode_stack.append(ActiveKeyMode('prompt', once=False))

    def _pop_prompt_keymode(self) -> None:
        self.key_mode_stack = [km for km in self.key_mode_stack if km.name != 'prompt']

    def resolve_key_binding(self, key: str):
        return self.keymap.get_binding(key, modes=self.active_key_modes())

    def binding_desc(self, binding: object) -> str:
        b = binding
        desc = str(getattr(b, 'desc', '') or '').strip()
        if desc:
            return desc

        spec = str(getattr(b, 'action_spec', '') or '').strip()
        if not spec:
            return ''
        steps = parse_action_chain(spec)
        if not steps:
            return ''

        def _short_doc(doc: str) -> str:
            d = str(doc).strip()
            if ' - ' in d:
                return d.split(' - ', 1)[1].strip()
            return d

        def _step_desc(action: str) -> str:
            act = str(action).strip()
            if not act:
                return ''
            if act.startswith('command:'):
                tail = act[len('command:') :].strip()
                if not tail:
                    return ''
                try:
                    cl = parse_cmdline(tail)
                except Exception:
                    cl = None
                name = cl.name if cl is not None else tail.split(None, 1)[0]
                cmd = self.command_dispatcher.get(name)
                if cmd is not None and cmd.doc:
                    return _short_doc(cmd.doc)
            a = self.actions.get(act)
            if a is not None and a.doc:
                return _short_doc(a.doc)
            return ''

        first = _step_desc(steps[0].action)
        if len(steps) <= 1:
            return first
        if first:
            return first + ' …'
        return ''

    def available_binding_rows(self) -> list[list[object]]:
        return self.keymap.resolved_binding_rows(self.active_key_modes())

    def available_binding_info_rows(self) -> list[list[object]]:
        rows = self.keymap.resolved_binding_info_rows(self.active_key_modes())
        out: list[list[object]] = []
        for mode, key, action, desc, group, span in rows:
            resolved_desc = str(desc) if desc not in (0, None, '') else self.binding_desc(
                self.keymap.get_binding(str(key), modes=[str(mode)])
            )
            out.append([mode, key, action, resolved_desc or 0, group, span])
        return out

    def resolve_key_info_row(self, key: str) -> list[object] | int:
        row = self.keymap.resolved_binding_info_row(key, modes=self.active_key_modes())
        if row == 0:
            return 0
        mode, key2, action, desc, group, span = row
        if desc in (0, None, ''):
            b = self.resolve_key_binding(str(key))
            desc = self.binding_desc(b) if b is not None else ''
        return [mode, key2, action, desc or 0, group, span]

    def binding_info_rows_for(self, mode: str | None = None) -> list[list[object]]:
        rows = self.keymap.binding_info_rows_for(mode)
        out: list[list[object]] = []
        for key, action, desc, group, span in rows:
            resolved_desc = str(desc) if desc not in (0, None, '') else self.binding_desc(
                self.keymap.get_binding(str(key), modes=[('global' if mode is None else str(mode))])
            )
            out.append([key, action, resolved_desc or 0, group, span])
        return out

    def dispatch_key(self, key: str) -> bool:
        """Resolve and execute a bound key.

        One-shot keymodes get first crack at the next key press. If the key is
        not bound in the topmost one-shot mode, that mode is popped and lookup
        falls through to the remaining active modes and global bindings.
        """

        while self.key_mode_stack and self.key_mode_stack[-1].once:
            top = self.key_mode_stack[-1]
            b = self.keymap.get_binding(key, modes=[top.name])
            if b is not None:
                try:
                    return self.run_action_chain(b.action_spec)
                finally:
                    if self.key_mode_stack and self.key_mode_stack[-1] == top:
                        self.key_mode_stack.pop()
            self.key_mode_stack.pop()

        # Capture modes intercept all keypresses: if a key is not bound in the
        # active capture mode, it does not fall through to global bindings.
        if self.key_mode_stack and getattr(self.key_mode_stack[-1], 'capture', False):
            top = self.key_mode_stack[-1]
            b = self.keymap.get_binding(key, modes=[top.name])
            if b is None:
                return False
            try:
                return self.run_action_chain(b.action_spec)
            finally:
                if top.once and self.key_mode_stack and self.key_mode_stack[-1] == top:
                    self.key_mode_stack.pop()

        # Docs/help buffers act like a tiny in-editor browser:
        # - Enter follows the markdown link under cursor (best-effort).
        # - Backspace goes back in the docs navigation stack.
        # - y copies the link target under cursor (like "copy link address").
        if self.prompt is None and self.current_help_doc_topic():
            if key == "Enter":
                return bool(self.help_follow())
            if key == "Backspace":
                return bool(self.help_back())
            if key in {"y", "Y"}:
                return bool(self.help_copy_link_target())


        b = self.resolve_key_binding(key)
        if b is None:
            # Fallback: treat unbound printable keys as text input.
            # - when a prompt is active, edit the prompt
            # - otherwise, insert into the buffer
            if len(key) == 1 and key.isprintable() and key not in ('\n', '\r', '\t'):
                self.input['text'] = key
                return self.run_action('PromptInsertText' if self.prompt is not None else 'InsertText')
            return False
        return self.run_action_chain(b.action_spec)

    def _emit_mx_hook(self, hook_word: str, *args: Any) -> None:
        """Fire a micromax hook word if present.

        Hooks are best-effort: exceptions are caught and recorded as messages.
        Hook handlers run in the editor's embedded VM but are treated as
        notifications: we discard any stack effects after the call.
        """

        try:
            if self.vm.find_word(hook_word) is None:
                return
            depth = len(self.vm.stack)
            self.vm.stack.extend(args)
            self.vm.eval(hook_word, filename="<editor-hook>")
            del self.vm.stack[depth:]
        except Exception as e:
            self.message(f"hook {hook_word} error: {e}")

    # ----- undo snapshot helpers -----
    def _snapshot_buffer_state(self, eb: EditorBuffer) -> tuple[str, list[Cursor], list[Cursor | None], list[int], int]:
        self._normalize_cursor_lists(eb)
        return (
            eb.buf.get_text(),
            [Cursor(c.line, c.col) for c in eb.cursors],
            [Cursor(a.line, a.col) if a else None for a in eb.sel_anchors],
            [int(x) for x in eb.cursor_ids],
            int(eb.primary),
        )

    def _restore_buffer_state(self, eb: EditorBuffer, snap: tuple[str, list[Cursor], list[Cursor | None], list[int], int]) -> None:
        text, curs, anchors, cursor_ids, primary = snap
        eb.buf.set_text(text)
        eb.cursors[:] = [Cursor(c.line, c.col) for c in curs]
        eb.sel_anchors[:] = [Cursor(a.line, a.col) if a else None for a in anchors]
        eb.cursor_ids[:] = [int(x) for x in cursor_ids]
        eb.primary = int(primary)
        self._normalize_cursor_lists(eb)

    def _record_undo_snapshot(
        self,
        eb: EditorBuffer,
        before: tuple[str, list[Cursor], list[Cursor | None], list[int], int],
        after: tuple[str, list[Cursor], list[Cursor | None], list[int], int],
        desc: str,
    ) -> None:
        def _undo() -> None:
            self._restore_buffer_state(eb, before)
            eb.buf.dirty = True

        def _redo() -> None:
            self._restore_buffer_state(eb, after)
            eb.buf.dirty = True

        self.undo.record(Edit(undo=_undo, redo=_redo, description=desc))

    # ----- buffers -----
    def new_buffer(self, name: str = "*scratch*", text: str = "", *, path: str | None = None) -> None:
        cid = self._alloc_cursor_id()
        ft = detect_filetype(str(path or ""), str(text or ""))
        self.buffers[name] = EditorBuffer(
            name=name,
            buf=Buffer(text, path=path),
            cursors=[Cursor(0, 0)],
            sel_anchors=[None],
            cursor_ids=[cid],
            primary=0,
            local_options={"filetype": ft},
        )
        self._activate_buffer(name)

    def filetype(self) -> str:
        """Return the active buffer's detected filetype."""
        eb = self.cur()
        ft = eb.local_options.get("filetype")
        if isinstance(ft, str) and ft:
            return ft
        # Best-effort fallback.
        ft2 = detect_filetype(str(eb.buf.path or ""), eb.buf.get_text())
        eb.local_options["filetype"] = ft2
        return ft2

    def _update_buffer_path(self, eb: EditorBuffer, path: str) -> None:
        eb.buf.path = str(path)
        eb.local_options["filetype"] = detect_filetype(str(path), eb.buf.get_text())



    def _persist_enabled(self) -> bool:
        """Return True if editor-owned persistence is enabled (cap.persist)."""

        try:
            return bool(self.options.get("cap.persist"))
        except Exception:
            return False

    def _persist_store_path(self, raw: str, *, default: str) -> Path | None:
        """Resolve a persistence file path under cap.persist-root (best-effort)."""

        if not self._persist_enabled():
            return None

        s = str(raw or "").strip() or str(default or "").strip()
        if not s:
            return None

        p = persist_resolve_path(self, s)
        if not persist_path_allowed(self, p):
            self.message(persist_deny_reason(self, p))
            return None
        return p

    def _recent_store_path(self) -> Path | None:
        """Return the configured recent-files persistence path (or None)."""

        raw = os.environ.get("MICROMAX_RECENT_FILE") or str(self.options.get("recent.file") or "")
        return self._persist_store_path(raw, default="~/.config/micromax/recent.json")

    def load_recent_files(self) -> bool:
        """Load recent file MRU from disk (best-effort).

        This is gated by options:
        - `recent.persist` (opt-in)
        - `cap.persist` (unsafe; off by default)

        Returns True when a file existed and was loaded.
        """
        if not bool(self.options.get("recent.persist")):
            return False
        p = self._recent_store_path()
        if p is None:
            return False
        if not p.exists() or p.is_dir():
            return False
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            if isinstance(data, list):
                xs = [str(x) for x in data if isinstance(x, (str, int, float))]
                out: list[str] = []
                seen: set[str] = set()
                for raw in xs:
                    n = self._normalize_path(str(raw))
                    if not n or n in seen:
                        continue
                    seen.add(n)
                    out.append(str(raw))
                self.recent_files[:] = out[: int(self._recent_limit)]
        except Exception as e:
            self.message(f"recent load error: {e}")
            return False
        return True

    def save_recent_files(self) -> bool:
        """Persist recent file MRU to disk (best-effort)."""
        if not bool(self.options.get("recent.persist")):
            return False
        p = self._recent_store_path()
        if p is None:
            return False
        try:
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(json.dumps(list(self.recent_files), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        except Exception as e:
            self.message(f"recent save error: {e}")
            return False
        return True

    def _history_store_path(self) -> Path | None:
        """Return the configured prompt-history persistence path (or None)."""

        raw = os.environ.get("MICROMAX_HISTORY_FILE") or str(self.options.get("history.file") or "")
        return self._persist_store_path(raw, default="~/.config/micromax/history.json")

    def load_prompt_history(self) -> bool:
        """Load prompt history from disk (best-effort).

        This is gated by options:
        - `history.persist` (opt-in)
        - `cap.persist` (unsafe; off by default)

        Returns True when a file existed and was loaded.
        """

        if not bool(self.options.get("history.persist")):
            return False
        p = self._history_store_path()
        if p is None:
            return False
        if not p.exists() or p.is_dir():
            return False

        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except Exception as e:
            self.message(f"history load error: {e}")
            return False

        limit = 200
        try:
            limit = max(1, int(self.options.get("history.limit")))
        except Exception:
            limit = 200

        def _norm_list(v: object) -> list[str]:
            if not isinstance(v, list):
                return []
            out: list[str] = []
            for it in v:
                if isinstance(it, (str, int, float)):
                    s = str(it).strip("\n")
                    if s:
                        out.append(s)
            # Clamp to last N (most recent).
            return out[-limit:]

        if isinstance(data, dict):
            for k, v in data.items():
                kk = str(k)
                xs = _norm_list(v)
                if xs:
                    self.history[kk] = xs
        elif isinstance(data, list):
            # Legacy: treat a bare list as command history.
            xs = _norm_list(data)
            if xs:
                self.history["command"] = xs
        else:
            return False

        return True

    def save_prompt_history(self) -> bool:
        """Persist prompt history to disk (best-effort)."""

        if not bool(self.options.get("history.persist")):
            return False
        p = self._history_store_path()
        if p is None:
            return False

        limit = 200
        try:
            limit = max(1, int(self.options.get("history.limit")))
        except Exception:
            limit = 200

        # Clamp each kind and keep the JSON deterministic.
        data: dict[str, list[str]] = {}
        for k in sorted(self.history.keys(), key=lambda x: str(x)):
            xs = self.history.get(k, [])
            if not isinstance(xs, list):
                continue
            out: list[str] = []
            for it in xs:
                s = str(it).strip("\n")
                if s:
                    out.append(s)
            if out:
                data[str(k)] = out[-limit:]

        try:
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        except Exception as e:
            self.message(f"history save error: {e}")
            return False

        return True

    def _project_root_for_path(self, path: str) -> str:
        """Best-effort project root: walk up looking for .git/.hg/.svn/pyproject/etc."""
        raw = str(path or "")
        if not raw:
            return ""
        try:
            p = Path(raw).expanduser().resolve(strict=False)
        except Exception:
            p = Path(raw).expanduser()
        cur = p.parent if p.is_file() else p
        for _ in range(8):
            if not cur:
                break
            try:
                if (cur / '.git').exists() or (cur / '.hg').exists() or (cur / '.svn').exists():
                    return str(cur)
                if (cur / 'pyproject.toml').exists() or (cur / 'package.json').exists() or (cur / 'Cargo.toml').exists():
                    return str(cur)
            except Exception:
                pass
            if cur.parent == cur:
                break
            cur = cur.parent
        return ""

    def _normalize_path(self, path: str) -> str:
        """Best-effort normalize a filesystem path for comparisons/MRUs.

        We keep buffer names stable (what the user typed) but use normalization
        for deduping and matching *the same file* across relative/tilde paths.
        """
        raw = str(path or "")
        if not raw:
            return ""
        p = Path(raw).expanduser()
        try:
            return str(p.resolve(strict=False))
        except Exception:
            return str(p)

    def _push_recent_file(self, path: str) -> None:
        """Insert path into the recent-files MRU (front).

        Recent lists are intentionally tiny and deterministic: we keep them
        headless-friendly and make no attempt to persist yet.
        """
        raw = str(path or "")
        if raw == "":
            return
        norm = self._normalize_path(raw)
        if norm == "":
            return
        # Dedup by normalized path, but keep the stored string stable-ish.
        for i, existing in enumerate(list(self.recent_files)):
            if self._normalize_path(existing) == norm:
                del self.recent_files[i]
                break
        self.recent_files.insert(0, raw)
        if len(self.recent_files) > int(self._recent_limit):
            self.recent_files[:] = self.recent_files[: int(self._recent_limit)]

        try:
            self.save_recent_files()
        except Exception:
            pass

    def clear_recent_files(self) -> None:
        self.recent_files.clear()
        try:
            self.save_recent_files()
        except Exception:
            pass

    def recent_prompt_rows(self) -> list[list[str]]:
        """Rows for the recent-file picker: [[path kind menu info] ...]."""
        out: list[list[str]] = []
        for raw in self.recent_files:
            p = str(raw)
            try:
                pp = Path(p)
                menu = str(pp.name) if pp.name else "file"
                info = str(pp.parent) if str(pp.parent) not in (".", "") else ""
            except Exception:
                menu, info = "file", ""
            out.append([p, "recent", menu, info])
        return out

    def recent_apropos_rows(self, query: str, *, limit: int | None = None) -> list[list[str]]:
        q = str(query or "").strip()
        rows = self.recent_prompt_rows()
        if q == "":
            return rows[:limit] if limit is not None else rows
        scored: list[tuple[tuple[int, int, int, int, int, int, int, int, int, str], int, list[str]]] = []
        for idx, row in enumerate(rows):
            key = self._buffer_row_sort_key(row, q)
            if key is None:
                continue
            scored.append((key, idx, [str(x) for x in row]))
        scored.sort(key=lambda item: (item[0], item[1]))
        out2 = [row for _k, _idx, row in scored]
        return out2[:limit] if limit is not None else out2

    def recent_section_rows_by_dir(self, query: str = "", *, limit: int | None = None) -> list[list[object]]:
        """Group recent file rows into directory sections."""
        rows = self.recent_apropos_rows(query, limit=limit)
        buckets: dict[str, list[list[str]]] = {}
        for row in rows:
            p = str(row[0]) if row else ""
            try:
                label = str(Path(p).parent)
            except Exception:
                label = "(unknown)"
            buckets.setdefault(label or "(unknown)", []).append([str(x) for x in row[:4]])
        out: list[list[object]] = []
        for label in sorted(buckets.keys(), key=lambda s: s.casefold()):
            out.append([label, buckets[label]])
        return out

    def recent_section_rows_by_project(self, query: str = "", *, limit: int | None = None) -> list[list[object]]:
        """Group recent file rows into project-root sections (Helix-style)."""
        rows = self.recent_apropos_rows(query, limit=limit)
        buckets: dict[str, list[list[str]]] = {}
        for row in rows:
            p = str(row[0]) if row else ""
            root = self._project_root_for_path(p)
            if root:
                label = root
                try:
                    rel = str(Path(p).expanduser().resolve(strict=False).relative_to(Path(root)))
                except Exception:
                    rel = str(Path(p).name)
                vals = [str(x) for x in row[:4]]
                while len(vals) < 4:
                    vals.append("")
                vals[2] = str(Path(root).name or "project")
                vals[3] = rel
                buckets.setdefault(label, []).append(vals)
            else:
                try:
                    label = str(Path(p).parent)
                except Exception:
                    label = "(unknown)"
                buckets.setdefault(label or "(unknown)", []).append([str(x) for x in row[:4]])
        out: list[list[object]] = []
        for label in sorted(buckets.keys(), key=lambda s: s.casefold()):
            out.append([label, buckets[label]])
        return out

    # ----- docs/help buffers -----
    def docs_root(self) -> Path:
        """Return the docs root directory (best-effort).

        By default we look for a `docs/` directory relative to the current
        working directory (repo layout). This can be overridden via the
        MICROMAX_DOCS environment variable.
        """

        raw = os.environ.get("MICROMAX_DOCS") or "docs"
        p = Path(str(raw)).expanduser()
        if not p.is_absolute():
            p = (Path.cwd() / p)
        return p

    def _scan_docs(self) -> list[dict[str, str]]:
        """Return a small docs index as a list of dicts.

        Each entry contains: topic, path, title, summary.
        """

        root = self.docs_root()
        if not root.exists() or root.is_dir() is False:
            return []
        out: list[dict[str, str]] = []
        try:
            files = sorted([p for p in root.glob("*.md") if p.is_file()], key=lambda p: p.name.casefold())
        except Exception:
            files = []

        for p in files:
            stem = p.stem
            slug = re.sub(r"^\d+\-", "", stem)
            topic = slug or stem
            title = ""
            summary = ""
            try:
                txt = p.read_text(encoding="utf-8")
                for line in txt.splitlines():
                    s = line.strip()
                    if not s:
                        continue
                    if not title and s.startswith("#"):
                        title = s.lstrip("#").strip()
                        continue
                    if not summary and not s.startswith("#"):
                        summary = s
                        break
            except Exception:
                pass
            out.append({"topic": str(topic), "path": str(p), "title": str(title), "summary": str(summary)})
        return out

    def doc_prompt_rows(self) -> list[list[str]]:
        """Rows for docs picker: [[topic kind menu info] ...]."""

        out: list[list[str]] = []
        for ent in self._scan_docs():
            topic = str(ent.get("topic", ""))
            path = str(ent.get("path", ""))
            title = str(ent.get("title", ""))
            summary = str(ent.get("summary", ""))
            menu = title or Path(path).name
            info = summary
            out.append([topic, "doc", menu, info])
        out.sort(key=lambda row: (str(row[0]).casefold(), str(row[2]).casefold()))
        return out

    def doc_apropos_rows(self, query: str, *, limit: int | None = None) -> list[list[str]]:
        q = str(query or "").strip()
        rows = self.doc_prompt_rows()
        if q == "":
            return rows[:limit] if limit is not None else rows

        scored: list[tuple[tuple[int, int, int, int, int, int, int, int, int, str], int, list[str]]] = []
        for idx, row in enumerate(rows):
            key = self._apropos_row_sort_key(row, q)
            if key is None:
                continue
            scored.append((key, idx, [str(x) for x in row]))
        scored.sort(key=lambda item: (item[0], item[1]))
        out2 = [row for _k, _idx, row in scored]
        return out2[:limit] if limit is not None else out2

    def find_doc_path(self, topic_or_path: str) -> str | None:
        """Resolve a docs topic (or path) to an on-disk markdown file."""

        raw = str(topic_or_path or "").strip()
        if not raw:
            return None

        # Explicit path (absolute or contains separators).
        if raw.endswith(".md") or ("/" in raw) or ("\\" in raw):
            p = Path(raw).expanduser()
            if not p.is_absolute():
                p = Path.cwd() / p
            if p.exists() and p.is_file():
                return str(p)

        want = raw.casefold()
        for ent in self._scan_docs():
            topic = str(ent.get("topic", ""))
            stem = Path(str(ent.get("path", ""))).stem
            if want in {topic.casefold(), stem.casefold()}:
                return str(ent.get("path"))
        return None

    def open_help_doc(self, topic: str, *, push_stack: bool = True) -> bool:
        """Open a docs markdown file into a protected read-only help buffer."""

        path = self.find_doc_path(topic)
        if not path:
            return False

        p = Path(path)
        stem = p.stem
        slug = re.sub(r"^\d+\-", "", stem)
        name = f"help:{slug or stem}"

        # Help navigation: if we are currently in a help buffer and are
        # switching to a different docs topic, push the current topic.
        if bool(push_stack):
            cur_help = self.current_help_doc_topic()
            new_help = str(slug or stem)
            if cur_help and cur_help != new_help:
                self._help_stack.append(cur_help)
                if len(self._help_stack) > int(self._help_stack_limit):
                    self._help_stack = self._help_stack[-int(self._help_stack_limit) :]

        # If already open (by normalized path), just switch to it.
        target_norm = self._normalize_path(str(p))
        if target_norm:
            for bname, eb in self.buffers.items():
                if eb.buf.path and self._normalize_path(str(eb.buf.path)) == target_norm:
                    self.switch_buffer(bname)
                    # Mark as protected in case it was opened via `open`.
                    try:
                        self.cur().local_options["readonly"] = True
                        self.cur().local_options["help_doc"] = str(slug or stem)
                    except Exception:
                        pass
                    return True

        try:
            text = p.read_text(encoding="utf-8")
        except Exception as e:
            self.message(f"help: {e}")
            return False

        self.new_buffer(name=name, text=text, path=str(p))
        try:
            eb2 = self.cur()
            eb2.local_options["readonly"] = True
            eb2.local_options["help_doc"] = str(slug or stem)
            eb2.buf.dirty = False
        except Exception:
            pass
        return True

    def refresh_capabilities(self) -> None:
        """Refresh capability feature advertisement based on current options."""

        refresh_vm_features(self, self.vm)

    def open_url(self, url: str) -> bool:
        """Open an external URL (capability-gated; best-effort)."""

        if not bool(self.options.get("cap.open-url")):
            return False
        u = str(url or "").strip()
        if not u:
            return False
        try:
            return bool(self._open_url_fn(u, new=2))
        except TypeError:
            # Some openers don't accept keyword args.
            try:
                return bool(self._open_url_fn(u))
            except Exception:
                return False
        except Exception:
            return False

    def current_help_doc_topic(self) -> str | None:
        """Return the current help-doc topic slug (or None)."""

        try:
            eb = self.cur()
        except Exception:
            return None
        try:
            if not bool(eb.local_options.get("readonly")):
                return None
            t = eb.local_options.get("help_doc")
            s = str(t or "").strip()
            return s or None
        except Exception:
            return None

    def help_back(self) -> bool:
        """Go back to the previous docs help page (best-effort)."""

        if not self._help_stack:
            self.message("help: back stack empty")
            return False
        topic = str(self._help_stack.pop()).strip()
        if not topic:
            return False
        # Avoid re-pushing onto the stack.
        if self.open_help_doc(topic, push_stack=False):
            return True
        self.message(f"help: no doc for {topic}")
        return False



    def _md_norm_ref_id(self, s: str) -> str:
        """Normalize a markdown reference-id (case-insensitive, collapse whitespace)."""

        return md_norm_ref_id(s)

    def _md_reference_defs(self, lines: list[object]) -> dict[str, str]:
        """Parse markdown reference definitions: [id]: target "title".

        This is intentionally small and conservative: it supports the common forms
        used in docs/help pages without needing a full markdown parser.
        """

        defs: dict[str, str] = {}
        for ln in lines:
            s = str(ln)
            m = re.match(r"^\s*\[(?P<id>[^\]]+)\]\s*:\s*(?P<rest>.+?)\s*$", s)
            if not m:
                continue
            rid = self._md_norm_ref_id(m.group('id') or '')
            if not rid:
                continue
            rest = str(m.group('rest') or '').strip()
            if not rest:
                continue

            # Target token may be <...> or a bare token; we ignore the optional title.
            target = ""
            if rest.startswith('<'):
                j = rest.find('>')
                if j != -1:
                    target = rest[1:j].strip()
                else:
                    inner = rest.strip('<>')
                    target = inner.split()[0] if inner.split() else ''
            else:
                target = rest.split()[0] if rest.split() else ''

            target = str(target).strip().strip('"').strip("'")
            if target:
                defs[rid] = target
        return defs

    def _md_target_from_parens(self, inner: str) -> str:
        """Extract a link target from inside markdown (...) content.

        This uses :func:`md_inline_link_target` so invalid inline-link forms can
        fall back to reference-link parsing.
        """

        return md_inline_link_target(inner)

    def help_follow(self) -> bool:
        """Follow a markdown link under the cursor in a help/docs buffer."""

        eb = self.cur()
        if not self.current_help_doc_topic():
            self.message("help: not in a docs buffer")
            return False
        target = self._help_link_target_under_cursor(eb)
        if not target:
            self.message("help: no link under cursor")
            return False
        return bool(self._follow_help_link(target, base_path=str(eb.buf.path) if eb.buf.path else None))

    def help_copy_link_target(self) -> bool:
        """Copy the markdown link target under the cursor (docs/help buffers only)."""

        eb = self.cur()
        if not self.current_help_doc_topic():
            self.message("helplinkcopy: not in a docs buffer")
            return False
        target = self._help_link_target_under_cursor(eb)
        if not target:
            self.message("helplinkcopy: no link under cursor")
            return False
        self.set_clipboard_items([str(target)], kind="items")
        self.message(f"help: copied link target\n{target}")
        return True

    # ----- URL-under-cursor helpers -----

    _URL_TOKEN_RE = re.compile(r'(?:https?://|mailto:)[^\s<>()\[\]{}"\']+')

    def _trim_url_token(self, tok: str) -> str:
        s = str(tok or "").strip()
        if not s:
            return ""

        left_wrap = set("<([{") | {"'", chr(34)}
        right_wrap = set(">)]}") | {"'", chr(34), ".", ",", ";", "!"}

        while s and s[0] in left_wrap:
            s = s[1:]
        while s and s[-1] in right_wrap:
            s = s[:-1]
        return s.strip()

    def url_under_cursor(self) -> str | None:
        """Best-effort URL under the primary cursor (any buffer).

        This is intentionally conservative and only recognizes:
        - http://...
        - https://...
        - mailto:...

        The cursor must be within the detected URL span.
        """

        eb = self.cur()
        if not eb.buf.lines:
            return None
        self._normalize_cursor_lists(eb)
        c = eb.cursors[eb.primary]
        idx = max(0, min(int(c.line), len(eb.buf.lines) - 1))
        line = str(eb.buf.lines[idx])
        col = int(c.col)

        for m in self._URL_TOKEN_RE.finditer(line):
            a, b = int(m.start()), int(m.end())
            if a <= col <= b:
                u = self._trim_url_token(str(m.group(0) or ""))
                return u or None
        return None

    def open_url_under_cursor(self) -> bool:
        """Open an external URL under cursor (capability-gated; confirm by default)."""

        u = self.url_under_cursor()
        if not u:
            self.message("openurl: no url under cursor")
            return False

        if not bool(self.options.get("cap.open-url")):
            self.message(f"openurl: disabled (cap.open-url). Enable with: set cap.open-url true\n{u}")
            return False

        if bool(self.options.get("open-url.confirm")):
            return bool(self.begin_open_url_confirm(u, source="cursor"))

        ok = self.open_url(u)
        if ok:
            self.message("opened url")
            return True
        self.message(f"url open failed: {u}")
        return False

    def copy_url_under_cursor(self) -> bool:
        """Copy the URL under cursor into the clipboard (any buffer)."""

        u = self.url_under_cursor()
        if not u:
            self.message("urlcopy: no url under cursor")
            return False
        self.set_clipboard_items([u], kind="items")
        self.message(f"copied url\n{u}")
        return True


    def _help_link_target_under_cursor(self, eb: "EditorBuffer") -> str | None:
        """Best-effort markdown link target under the primary cursor."""

        if not eb.buf.lines:
            return None
        self._normalize_cursor_lists(eb)
        c = eb.cursors[eb.primary]
        idx = max(0, min(int(c.line), len(eb.buf.lines) - 1))
        line = str(eb.buf.lines[idx])
        col = int(c.col)

        # Markdown link scan (best-effort).
        # Supported forms:
        #   - inline links: [label](target "title")
        #   - reference links: [label][id] and [label][] (collapsed)
        #   - shortcut reference links: [id]
        #   - autolinks: <https://...> and <mailto:...>

        defs = self._md_reference_defs(list(eb.buf.lines))

        # 1) Inline links: [label](...)
        for m in re.finditer(r"\[[^\]]*\]\((?P<inner>[^)]+)\)", line):
            a, b = int(m.start()), int(m.end())
            if a <= col <= b:
                t = self._md_target_from_parens(str(m.group('inner') or ''))
                if t:
                    return t

        # 2) Reference-style links: [label][id] and [label][] (implicit id=label)
        for m in re.finditer(r"\[(?P<label>[^\]]+)\]\[(?P<id>[^\]]*)\]", line):
            a, b = int(m.start()), int(m.end())
            if a <= col <= b:
                rid = str(m.group('id') or '').strip() or str(m.group('label') or '').strip()
                t = defs.get(md_norm_ref_id(rid))
                if t:
                    return t

        # 3) Shortcut reference links: [id]
        # Only treat these as links when a matching definition exists.
        for m in re.finditer(r"\[(?P<id>[^\]]+)\]", line):
            a, b = int(m.start()), int(m.end())
            if not (a <= col <= b):
                continue
            # Skip images: ![alt]
            if a > 0 and line[a - 1] == '!':
                continue
            # Skip definitions: [id]: target
            after = line[b:b+1]
            if after in (':', '['):
                continue
            rid = str(m.group('id') or '').strip()
            if not rid:
                continue
            t = defs.get(md_norm_ref_id(rid))
            if t:
                return t

        # 4) Autolinks: <https://...> / <mailto:...>
        for m in re.finditer(r"<(?P<url>(?:https?://|mailto:)[^ >]+)>", line):
            a, b = int(m.start()), int(m.end())
            if a <= col <= b:
                url = str(m.group('url') or '').strip()
                return url or None

        return None

    def _follow_help_link(self, target: str, *, base_path: str | None) -> bool:
        """Follow a docs-help link target (internal docs, relative file, or external URL)."""

        t = str(target or "").strip().strip('"').strip("'")
        if not t:
            return False

        low = t.casefold()
        if low.startswith("http://") or low.startswith("https://") or low.startswith("mailto:"):
            if bool(self.options.get("cap.open-url")):
                # Safe-by-default: confirm before opening external URLs.
                if bool(self.options.get("open-url.confirm")):
                    return bool(self.begin_open_url_confirm(t, source="help"))

                ok = self.open_url(t)
                if ok:
                    self.message("help: opened external link")
                    return True
                self.message(f"help: external link failed: {t}")
                return False
            # Keep the UX explicit: this is intentionally capability-gated.
            # (Docs page `98-help-browser.md` includes the same hint.)
            self.message(
                f"help: external link disabled (cap.open-url). Enable with: set cap.open-url true\n{t}"
            )
            return False

        # Relative paths are relative to the current docs file.
        if base_path:
            try:
                base = Path(str(base_path)).parent
                cand = (base / t).resolve()
                if cand.exists() and cand.is_file():
                    return bool(self.open_help_doc(str(cand), push_stack=True))
            except Exception:
                pass

        # Otherwise treat as a docs topic (slug) or explicit path.
        if self.open_help_doc(t, push_stack=True):
            return True
        self.message(f"help: no doc for {t}")
        return False

    def begin_open_url_confirm(self, url: str, *, source: str = "") -> bool:
        """Begin a capture-mode confirmation loop for opening an external URL."""

        u = str(url or "").strip()
        if not u:
            return False
        if not bool(self.options.get("cap.open-url")):
            return False

        # Remove any prior openurl mode so we don't stack confirmations.
        self.key_mode_stack = [km for km in self.key_mode_stack if km.name != "openurl"]

        self._pending_open_url = u
        self._pending_open_url_source = str(source or "")
        self.push_key_mode("openurl", capture=True)
        self.message(f"open external link? y/Enter=open n/Esc=cancel c=copy\n{u}")
        return True

    def _finish_open_url_confirm(self) -> None:
        self._pending_open_url = None
        self._pending_open_url_source = ""
        self.key_mode_stack = [km for km in self.key_mode_stack if km.name != "openurl"]

    def help_link_rows(self, query: str = "", *, limit: int | None = None) -> list[list[str]]:
        """Return markdown links in the current help/docs buffer as rows.

        Rows are: [label kind target info]
        """

        topic = self.current_help_doc_topic()
        if not topic:
            return []
        eb = self.cur()
        rows: list[list[str]] = []
        defs = self._md_reference_defs(list(eb.buf.lines))
        for i, ln in enumerate(eb.buf.lines):
            s = str(ln)

            # Inline: [label](target "title")
            for m in re.finditer(r"\[(?P<label>[^\]]+)\]\((?P<inner>[^)]+)\)", s):
                label = str(m.group('label') or '').strip()
                target = self._md_target_from_parens(str(m.group('inner') or ''))
                if not target:
                    continue
                info = f"{i+1}:{int(m.start('label'))+1}"
                rows.append([label or target, 'link', target, info])

            # Reference: [label][id] and [label][] (implicit id=label)
            for m in re.finditer(r"\[(?P<label>[^\]]+)\]\[(?P<id>[^\]]*)\]", s):
                label = str(m.group('label') or '').strip()
                rid = str(m.group('id') or '').strip() or label
                target = defs.get(md_norm_ref_id(rid))
                if not target:
                    continue
                info = f"{i+1}:{int(m.start('label'))+1}"
                rows.append([label or target, 'link', target, info])

            # Shortcut reference: [id] (only when a matching definition exists).
            for m in re.finditer(r"\[(?P<id>[^\]]+)\]", s):
                a, b = int(m.start()), int(m.end())
                # Skip images: ![alt]
                if a > 0 and s[a - 1] == '!':
                    continue
                after = s[b:b+1]
                # Skip definitions ([id]: ...) and full/collapsed ref forms ([id][...]).
                if after in (':', '['):
                    continue
                # Skip valid inline links: [id](...) is handled above.
                if after == '(':
                    mm = re.match(r"\[(?P<label>[^\]]+)\]\((?P<inner>[^)]+)\)", s[a:])
                    if mm is not None:
                        inner = str(mm.group('inner') or '')
                        if self._md_target_from_parens(inner):
                            continue
                rid = str(m.group('id') or '').strip()
                if not rid:
                    continue
                target = defs.get(md_norm_ref_id(rid))
                if not target:
                    continue
                info = f"{i+1}:{a+1}"
                rows.append([rid or target, 'link', target, info])

            # Autolink: <https://...> / <mailto:...>
            for m in re.finditer(r"<(?P<url>(?:https?://|mailto:)[^ >]+)>", s):
                url = str(m.group('url') or '').strip()
                if not url:
                    continue
                info = f"{i+1}:{int(m.start('url'))+1}"
                rows.append([url, 'link', url, info])

        q = str(query or '').strip()
        if q:
            scored: list[tuple[tuple[int, int, int, int, int, int, int, int, int, str], int, list[str]]] = []
            for idx, row in enumerate(rows):
                key = self._apropos_row_sort_key([row[0], row[1], row[2], row[3]], q)
                if key is None:
                    continue
                scored.append((key, idx, row))
            scored.sort(key=lambda item: (item[0], item[1]))
            rows = [r for _k, _i, r in scored]

        if limit is not None:
            return rows[: max(1, int(limit))]
        return rows

    def _helplink_section_label(self, row: list[str]) -> str:
        """Backward-compat section label helper for docs-link rows.

        Rows are: [label kind target info]

        New code should prefer:
          - `_helplink_kind_label` (Docs/Files/External)
          - `_helplink_heading_label` (nearest heading breadcrumb)
        """

        return self._helplink_kind_label(row)

    def _helplink_kind_label(self, row: list[str]) -> str:
        """Classify docs links as Docs/Files/External (stable default)."""

        try:
            tgt = str(row[2] if len(row) > 2 else "")
            low = tgt.strip().casefold()
            if low.startswith("http://") or low.startswith("https://") or low.startswith("mailto:"):
                return "External"
            if tgt.endswith(".md") or ("/" in tgt) or ("\\" in tgt):
                return "Files"
        except Exception:
            pass
        return "Docs"

    def _help_heading_paths(self) -> list[tuple[int, str]]:
        """Return [(line1, path), ...] heading paths for the current docs buffer.

        The "path" is a breadcrumb-like label built from heading levels.
        We intentionally treat the page's H1 as a document title and omit it
        from the breadcrumb, so most pages yield readable section labels like
        "Links" or "External links" rather than "Help browser › Links".

        Paths are best-effort and cached by (topic, nlines).
        """

        topic = self.current_help_doc_topic()
        if not topic:
            return []
        eb = self.cur()
        nlines = len(eb.buf.lines)
        if topic == self._help_heading_cache_topic and nlines == self._help_heading_cache_nlines:
            return list(self._help_heading_cache)

        idx: list[tuple[int, str]] = []
        stack: list[str] = []

        for i, ln in enumerate(eb.buf.lines):
            s = str(ln)
            m = re.match(r"^\s{0,3}(?P<hashes>#{1,6})\s+(?P<title>.+?)\s*(?:#+\s*)?$", s)
            if not m:
                continue
            title = str(m.group("title") or "").strip()
            if not title:
                continue
            level = len(str(m.group("hashes") or ""))
            level = max(1, min(int(level), 6))

            # Ignore H1 as a "document title".
            if level == 1:
                stack = []
                continue

            # Shift levels down so H2 becomes breadcrumb level 1.
            lvl = max(1, min(level - 1, 6))
            stack = stack[: max(0, int(lvl) - 1)]
            stack.append(title)
            path = " › ".join(stack).strip()
            idx.append((i + 1, path))

        self._help_heading_cache_topic = str(topic)
        self._help_heading_cache_nlines = int(nlines)
        self._help_heading_cache = list(idx)
        return list(idx)

    def _help_heading_path_for_line(self, line1: int) -> str:
        """Return the nearest heading breadcrumb for 1-based line number."""

        line = max(1, int(line1))
        idx = self._help_heading_paths()
        if not idx:
            return "Top"
        lines = [n for n, _p in idx]
        j = int(bisect_right(lines, line)) - 1
        if j < 0:
            return "Top"
        try:
            return str(idx[j][1] or "Top")
        except Exception:
            return "Top"

    def _helplink_heading_label(self, row: list[str]) -> str:
        """Section label for a docs link row based on nearest markdown heading."""

        try:
            info = str(row[3] if len(row) > 3 else "")
            if ":" in info:
                line_s, _col_s = info.split(":", 1)
                line = int(line_s)
                return self._help_heading_path_for_line(line)
        except Exception:
            pass
        return "Top"

    def helplink_section_label(self, row: list[str]) -> str:
        """Section label for docs-link pickers.

        Controlled by option `help.linksections`:
          - "kind" (default): Docs/Files/External
          - "heading": nearest heading breadcrumb (Top/Links/External links/...)
        """

        mode = str(self.options.get("help.linksections") or "kind").strip().lower()
        if mode == "heading":
            return self._helplink_heading_label(row)
        return self._helplink_kind_label(row)

    def help_link_section_rows_kind(self, query: str = "", *, limit: int | None = None) -> list[list[object]]:
        """Grouped link rows by kind (Docs/Files/External)."""

        rows = self.help_link_rows(query, limit=limit)
        section_order = ["Docs", "Files", "External"]
        buckets: dict[str, list[list[str]]] = {label: [] for label in section_order}
        for row in rows:
            vals = [str(x) for x in list(row[:4])]
            while len(vals) < 4:
                vals.append("")
            label = self._helplink_kind_label(vals)
            buckets.setdefault(label, [])
            buckets[label].append(vals)
        out: list[list[object]] = []
        for label in section_order:
            items = buckets.get(label, [])
            if items:
                out.append([label, items])
        return out

    def help_link_section_rows_heading(self, query: str = "", *, limit: int | None = None) -> list[list[object]]:
        """Grouped link rows by nearest markdown heading."""

        rows = self.help_link_rows(query, limit=limit)
        buckets: dict[str, list[list[str]]] = {}
        for row in rows:
            vals = [str(x) for x in list(row[:4])]
            while len(vals) < 4:
                vals.append("")
            label = self._helplink_heading_label(vals)
            if label not in buckets:
                buckets[label] = []
            buckets[label].append(vals)
        return [[label, items] for (label, items) in buckets.items() if items]

    def help_link_section_rows(self, query: str = "", *, limit: int | None = None) -> list[list[object]]:
        """Grouped link rows for the current docs/help buffer.

        Shape: [[label, rows] ...], where rows are [[label kind target info] ...].
        """

        mode = str(self.options.get("help.linksections") or "kind").strip().lower()
        if mode == "heading":
            return self.help_link_section_rows_heading(query, limit=limit)
        return self.help_link_section_rows_kind(query, limit=limit)

    def help_outline_rows(self, query: str = "", *, limit: int | None = None) -> list[list[str]]:
        """Return markdown headings in the current help/docs buffer as rows.

        Rows are: [title kind menu info]
          - title: heading text (without leading hashes)
          - kind: "heading"
          - menu: heading level marker ("h1".."h6")
          - info: "line:col" position (1-based)
        """

        topic = self.current_help_doc_topic()
        if not topic:
            return []
        eb = self.cur()
        rows: list[list[str]] = []
        for i, ln in enumerate(eb.buf.lines):
            s = str(ln)
            m = re.match(r"^\s{0,3}(?P<hashes>#{1,6})\s+(?P<title>.+?)\s*(?:#+\s*)?$", s)
            if not m:
                continue
            title = str(m.group("title") or "").strip()
            if not title:
                continue
            level = len(str(m.group("hashes") or ""))
            level = max(1, min(int(level), 6))
            menu = f"h{level}"
            col = int(m.start("title"))
            info = f"{i+1}:{col+1}"
            rows.append([title, "heading", menu, info])

        q = str(query or "").strip()
        if q:
            scored: list[tuple[tuple[int, int, int, int, int, int, int, int, int, str], int, list[str]]] = []
            for idx, row in enumerate(rows):
                key = self._apropos_row_sort_key([row[0], row[1], row[2], row[3]], q)
                if key is None:
                    continue
                scored.append((key, idx, row))
            scored.sort(key=lambda item: (item[0], item[1]))
            rows = [r for _k, _i, r in scored]

        if limit is not None:
            return rows[: max(1, int(limit))]
        return rows

    def help_nav_section_rows(self, query: str = "", *, limit: int | None = None) -> list[list[object]]:
        """Return combined headings + link rows for the current docs/help buffer.

        Shape: [[label, rows] ...], where rows are in the familiar
        [name kind menu info] shape.

        Sections are ordered as:
          - Headings
          - Docs/Files/External (links)
        """

        # Split the total limit to keep both headings and links represented.
        head_cap: int | None
        link_cap: int | None
        if limit is None:
            head_cap = None
            link_cap = None
        else:
            lim = max(1, int(limit))
            head_cap = max(1, lim // 2)
            link_cap = max(1, lim - head_cap)

        headings = self.help_outline_rows(query, limit=head_cap)
        # Keep traditional link kind sections (Docs/Files/External) for helpnav.
        link_sections = self.help_link_section_rows_kind(query, limit=link_cap)

        # helpnav polish: include the nearest heading breadcrumb in link-row info
        # so links are easier to scan and search (without changing helplink rows).
        for sec in link_sections:
            try:
                if not isinstance(sec, list) or len(sec) < 2:
                    continue
                rows = sec[1]
                if not isinstance(rows, list):
                    continue
                for row in rows:
                    if not isinstance(row, list) or len(row) < 4:
                        continue
                    info = str(row[3] or '')
                    if ':' not in info:
                        continue
                    try:
                        line_s, _col_s = info.split(':', 1)
                        line = int(line_s)
                    except Exception:
                        continue
                    crumb = self._help_heading_path_for_line(line)
                    if crumb and crumb != 'Top' and crumb not in info:
                        row[3] = f"{info} — {crumb}"
            except Exception:
                continue


        out: list[list[object]] = []
        if headings:
            out.append(["Headings", headings])
        # Preserve link-section order from help_link_section_rows.
        for sec in link_sections:
            try:
                if isinstance(sec, list) and len(sec) >= 2 and sec[1]:
                    out.append([sec[0], sec[1]])
            except Exception:
                continue
        return out

    def help_nav_rows(self, query: str = "", *, limit: int | None = None) -> list[list[str]]:
        """Flattened combined docs navigator rows.

        This is used by the built-in help navigator picker (`helpnavpick`).
        """

        sections = self.help_nav_section_rows(query, limit=limit)
        flat: list[list[str]] = []
        for sec in sections:
            if not isinstance(sec, list) or len(sec) < 2:
                continue
            rows = sec[1]
            if not isinstance(rows, list):
                continue
            for row in rows:
                try:
                    vals = [str(x) for x in list(row[:4])]
                    while len(vals) < 4:
                        vals.append("")
                    flat.append(vals)
                except Exception:
                    continue

        if limit is not None:
            return flat[: max(1, int(limit))]
        return flat



    def close_buffer(self, name: str | None = None, *, force: bool = False) -> bool:
        """Close (delete) a buffer by name, or the active buffer when name is None.

        If the buffer is dirty, this uses a double-tap guard (unless force=True),
        mirroring the `quit` command's safety behavior.
        """
        target = str(name or (self.active or ""))
        if not target or target not in self.buffers:
            return False
        eb = self.buffers[target]
        if eb.buf.dirty and not bool(force):
            if self._close_armed and self._close_armed_name == target:
                # proceed
                pass
            else:
                self._close_armed = True
                self._close_armed_name = target
                self.message(f"unsaved changes in: {target}; run `close` again or `close -f` to force")
                return False

        self._close_armed = False
        self._close_armed_name = ""

        # Drop marks pointing at this buffer (keeps navigation helpers sane).
        for mk, (bufname, _cur) in list(self.marks.items()):
            if bufname == target:
                del self.marks[mk]

        # Delete the buffer.
        del self.buffers[target]

        # Choose a new active buffer.
        if self.active == target:
            self._buffer_mru = [x for x in self._buffer_mru if x != target and x in self.buffers]
            nxt = self.previous_buffer_name()
            if nxt:
                self._activate_buffer(nxt)
            elif self.buffers:
                names = list(self.buffers.keys())
                self._activate_buffer(names[-1])
            else:
                self.new_buffer("*scratch*", "")
        else:
            self._buffer_mru = [x for x in self._buffer_mru if x in self.buffers]
        return True

    def buffer_names(self) -> list[str]:
        """Return buffer names (stable sorted order)."""
        return sorted(self.buffers.keys())

    def _touch_buffer_mru(self, name: str) -> None:
        """Record that buffer `name` became active (best-effort)."""
        n = str(name or "").strip()
        if not n:
            return
        self._buffer_mru = [n] + [x for x in self._buffer_mru if x != n]
        if self.buffers:
            self._buffer_mru = [x for x in self._buffer_mru if x in self.buffers]

    def _activate_buffer(self, name: str) -> None:
        """Set active buffer and touch MRU (expects buffer exists)."""
        self.active = str(name)
        self._touch_buffer_mru(str(name))

    def previous_buffer_name(self) -> str:
        """Return the most-recently-used *other* buffer name, or ''."""
        cur = str(self.active or "")
        for n in list(self._buffer_mru):
            if n and n != cur and n in self.buffers:
                return n
        return ""

    def close_buffers(self, names: list[str], *, keep: str | None = None) -> None:
        """Close many buffers (forcefully; caller handles dirty confirmation)."""
        close_set = {str(n) for n in names if str(n) in self.buffers}
        if not close_set:
            return

        for mk, (bn, _cur) in list(self.marks.items()):
            if bn in close_set:
                del self.marks[mk]

        for n in close_set:
            if n in self.buffers:
                del self.buffers[n]

        self._buffer_mru = [x for x in self._buffer_mru if x in self.buffers]

        k = str(keep or "")
        if k and k in self.buffers:
            self._activate_buffer(k)
            return

        for n in list(self._buffer_mru):
            if n in self.buffers:
                self._activate_buffer(n)
                return

        if self.buffers:
            names2 = list(self.buffers.keys())
            self._activate_buffer(names2[-1])
        else:
            self.new_buffer("*scratch*", "")

    def switch_buffer(self, name: str) -> bool:
        """Make `name` the active buffer if it exists."""
        n = str(name)
        if n not in self.buffers:
            return False
        self._activate_buffer(n)
        return True

    def rename_buffer(self, old: str, new: str) -> bool:
        """Rename a buffer key (and update mark targets).

        This keeps buffer identity stable enough for marks and scripts while
        still allowing commands like `save as` to retitle the buffer.
        """
        o = str(old)
        n = str(new)
        if o not in self.buffers:
            return False
        if n == o:
            return True
        if n in self.buffers:
            # refuse to clobber
            return False
        eb = self.buffers.pop(o)
        eb.name = n
        self.buffers[n] = eb
        if self.active == o:
            self._activate_buffer(n)
        # Update MRU entry (if any).
        self._buffer_mru = [n if x == o else x for x in self._buffer_mru]
        self._buffer_mru = [x for i,x in enumerate(self._buffer_mru) if x and x not in self._buffer_mru[:i]]
        # Update mark targets.
        for mk, (bn, cur) in list(self.marks.items()):
            if bn == o:
                self.marks[mk] = (n, Cursor(cur.line, cur.col))
        return True

    def mark_set(self, name: str) -> bool:
        """Set a named mark at the primary cursor in the active buffer."""
        mk = str(name or "").strip()
        if not mk:
            return False
        eb = self.cur()
        self._normalize_cursor_lists(eb)
        c = eb.cursors[eb.primary]
        self.marks[mk] = (eb.name, Cursor(int(c.line), int(c.col)))
        return True

    def mark_jump(self, name: str) -> bool:
        """Jump to a named mark, pushing the jumplist."""
        mk = str(name or "").strip()
        if not mk:
            return False
        if mk not in self.marks:
            return False
        buf_name, tgt = self.marks[mk]
        if buf_name not in self.buffers:
            return False
        # Save where we were.
        self.push_jump()
        self.switch_buffer(buf_name)
        eb = self.cur()
        self._normalize_cursor_lists(eb)
        eb.primary = max(0, min(int(eb.primary), len(eb.cursors) - 1))
        eb.cursors[eb.primary] = eb.buf.clamp(Cursor(int(tgt.line), int(tgt.col)))
        eb.sel_anchors[eb.primary] = None
        return True

    def mark_rows(self) -> list[list[object]]:
        """Return rows for marks as [[name buffer line col] ...]."""
        rows: list[list[object]] = []
        for name in sorted(self.marks.keys()):
            bn, cur = self.marks[name]
            rows.append([str(name), str(bn), int(cur.line), int(cur.col)])
        return rows

    def cur(self) -> EditorBuffer:
        if self.active is None or self.active not in self.buffers:
            raise RuntimeError("No active buffer")
        return self.buffers[self.active]

    def primary_index(self) -> int:
        eb = self.cur()
        self._normalize_cursor_lists(eb)
        return int(eb.primary)

    def set_primary_index(self, i: int) -> None:
        eb = self.cur()
        self._normalize_cursor_lists(eb)
        if not eb.cursors:
            eb.primary = 0
            return
        eb.primary = max(0, min(int(i), len(eb.cursors) - 1))
        self._normalize_cursor_lists(eb)

    def primary_cursor(self) -> Cursor:
        eb = self.cur()
        self._normalize_cursor_lists(eb)
        return eb.cursors[eb.primary]

    def _alloc_cursor_id(self) -> int:
        cid = int(self._next_cursor_id)
        self._next_cursor_id += 1
        return cid

    def _normalize_cursor_lists(self, eb: EditorBuffer) -> None:
        """Normalize multi-cursor invariants.

        Invariants (rev14):
          - `cursors` + `sel_anchors` are the same length
          - list order is document order (line,col)
          - duplicate cursor positions are removed
          - `primary` points at the primary cursor
          - cursor and anchor positions are clamped to the buffer
        """

        # Keep sel_anchors aligned with cursors.
        if len(eb.sel_anchors) < len(eb.cursors):
            eb.sel_anchors.extend([None] * (len(eb.cursors) - len(eb.sel_anchors)))
        if len(eb.sel_anchors) > len(eb.cursors):
            eb.sel_anchors[:] = eb.sel_anchors[: len(eb.cursors)]

        # Keep cursor_ids aligned with cursors.
        if len(eb.cursor_ids) < len(eb.cursors):
            eb.cursor_ids.extend([self._alloc_cursor_id() for _ in range(len(eb.cursors) - len(eb.cursor_ids))])
        if len(eb.cursor_ids) > len(eb.cursors):
            eb.cursor_ids[:] = eb.cursor_ids[: len(eb.cursors)]

        if not eb.cursors:
            eb.cursors[:] = [Cursor(0, 0)]
            eb.sel_anchors[:] = [None]
            eb.cursor_ids[:] = [self._alloc_cursor_id()]
            eb.primary = 0

        # Clamp primary index.
        if eb.primary < 0:
            eb.primary = 0
        if eb.primary >= len(eb.cursors):
            eb.primary = max(0, len(eb.cursors) - 1)

        # Clamp cursor + anchor positions.
        items: list[tuple[Cursor, Cursor | None, int, bool, int]] = []
        for i, c in enumerate(eb.cursors):
            cc = eb.buf.clamp(Cursor(c.line, c.col))
            a = eb.sel_anchors[i]
            aa = eb.buf.clamp(Cursor(a.line, a.col)) if a is not None else None
            cid = int(eb.cursor_ids[i])
            items.append((cc, aa, cid, i == eb.primary, i))

        # Deduplicate by cursor position.
        chosen: dict[tuple[int, int], tuple[Cursor, Cursor | None, int, bool, int]] = {}
        for c, a, cid, is_primary, idx in items:
            key = (c.line, c.col)
            if key not in chosen:
                chosen[key] = (c, a, cid, is_primary, idx)
                continue
            c0, a0, cid0, p0, idx0 = chosen[key]

            # Prefer the primary cursor when merging duplicates, else earliest.
            take_new = False
            if is_primary and not p0:
                take_new = True
            elif is_primary == p0 and idx < idx0:
                take_new = True

            if take_new:
                # Preserve a non-empty anchor if possible.
                if a is None and a0 is not None:
                    a = a0
                chosen[key] = (c, a, cid, is_primary, idx)
            else:
                if a0 is None and a is not None:
                    chosen[key] = (c0, a, cid0, p0, idx0)

        deduped = list(chosen.values())
        deduped.sort(key=lambda t: (t[0].line, t[0].col, t[2]))

        # Rebuild lists + primary index.
        new_primary = 0
        for j, (_c, _a, _cid, p, _idx) in enumerate(deduped):
            if p:
                new_primary = j
                break

        eb.cursors[:] = [Cursor(c.line, c.col) for (c, _a, _cid, _p, _idx) in deduped]
        eb.sel_anchors[:] = [Cursor(a.line, a.col) if a is not None else None for (_c, a, _cid, _p, _idx) in deduped]
        eb.cursor_ids[:] = [int(cid) for (_c, _a, cid, _p, _idx) in deduped]
        eb.primary = new_primary

    # ----- selection (per cursor) -----
    def selection(self, i: int | None = None) -> Selection | None:
        eb = self.cur()
        self._normalize_cursor_lists(eb)
        if i is None:
            i = eb.primary
        if i < 0 or i >= len(eb.cursors):
            return None
        a = eb.sel_anchors[i]
        if a is None:
            return None
        return Selection(a, eb.cursors[i])

    def has_selection(self, i: int | None = None) -> bool:
        """Return True if there is a non-empty selection.

        - i is None: any cursor
        - i >= 0: that cursor index
        """

        eb = self.cur()
        self._normalize_cursor_lists(eb)
        if i is not None:
            sel = self.selection(i)
            return sel is not None and not sel.is_empty()
        for j in range(len(eb.cursors)):
            sel = self.selection(j)
            if sel is not None and not sel.is_empty():
                return True
        return False

    def has_primary_selection(self) -> bool:
        """Return True if the primary cursor has a non-empty selection."""
        eb = self.cur()
        self._normalize_cursor_lists(eb)
        sel = self.selection(None)
        return sel is not None and not sel.is_empty()

    def clear_selection(self, i: int | None = None) -> None:
        eb = self.cur()
        self._normalize_cursor_lists(eb)
        if i is None:
            # clear all
            eb.sel_anchors[:] = [None] * len(eb.cursors)
            return
        if i == -1:
            i = eb.primary
        if 0 <= i < len(eb.sel_anchors):
            eb.sel_anchors[i] = None


    # ----- selection/cursor recovery stack -----
    def push_selections(self) -> None:
        """Push the current cursor+selection state onto a small stack.

        This is inspired by selection-oriented editors where it's easy to
        accidentally clear/merge selections; having a tiny recovery stack is
        a cheap, testable escape hatch. This stack is *not* part of undo.
        """

        eb = self.cur()
        self._normalize_cursor_lists(eb)
        snap = (
            [Cursor(c.line, c.col) for c in eb.cursors],
            [Cursor(a.line, a.col) if a else None for a in eb.sel_anchors],
            [int(x) for x in eb.cursor_ids],
            int(eb.primary),
        )
        eb.sel_stack.append(snap)

    def pop_selections(self) -> bool:
        """Pop and restore the last saved cursor+selection state."""

        eb = self.cur()
        self._normalize_cursor_lists(eb)
        if not eb.sel_stack:
            return False
        curs, anchors, cursor_ids, primary = eb.sel_stack.pop()
        eb.cursors[:] = [Cursor(c.line, c.col) for c in curs]
        eb.sel_anchors[:] = [Cursor(a.line, a.col) if a else None for a in anchors]
        eb.cursor_ids[:] = [int(x) for x in cursor_ids]
        eb.primary = int(primary)
        self._normalize_cursor_lists(eb)
        return True

    def clear_saved_selections(self) -> None:
        eb = self.cur()
        eb.sel_stack.clear()

    # ----- jumplist (navigation) -----
    def _snapshot_cursor_only(self, eb: EditorBuffer) -> tuple[list[Cursor], list[Cursor | None], list[int], int]:
        self._normalize_cursor_lists(eb)
        return (
            [Cursor(c.line, c.col) for c in eb.cursors],
            [Cursor(a.line, a.col) if a else None for a in eb.sel_anchors],
            [int(x) for x in eb.cursor_ids],
            int(eb.primary),
        )

    def _restore_cursor_only(
        self,
        eb: EditorBuffer,
        snap: tuple[list[Cursor], list[Cursor | None], list[int], int],
    ) -> None:
        curs, anchors, cursor_ids, primary = snap
        eb.cursors[:] = [Cursor(c.line, c.col) for c in curs]
        eb.sel_anchors[:] = [Cursor(a.line, a.col) if a else None for a in anchors]
        eb.cursor_ids[:] = [int(x) for x in cursor_ids]
        eb.primary = int(primary)
        self._normalize_cursor_lists(eb)

    def push_jump(self) -> bool:
        """Push current cursor/selection state onto the jumplist.

        This is the navigation sibling of undo: it tracks *where you were*.
        Inspired by Vim/Helix jump lists.
        """

        eb = self.cur()
        snap = self._snapshot_cursor_only(eb)

        # Deduplicate consecutive identical entries.
        if eb.jump_list and eb.jump_index == len(eb.jump_list) - 1:
            if eb.jump_list[-1] == snap:
                return False

        # If we've jumped back, truncate the "forward" tail (browser/Vim semantics).
        if eb.jump_index >= 0 and eb.jump_index < len(eb.jump_list) - 1:
            eb.jump_list[:] = eb.jump_list[: eb.jump_index + 1]

        eb.jump_list.append(snap)
        eb.jump_index = len(eb.jump_list) - 1

        # Bounded size.
        MAX_JUMPS = 100
        if len(eb.jump_list) > MAX_JUMPS:
            drop = len(eb.jump_list) - MAX_JUMPS
            eb.jump_list[:] = eb.jump_list[drop:]
            eb.jump_index = max(-1, eb.jump_index - drop)

        return True

    def jump_back(self) -> bool:
        eb = self.cur()
        self._normalize_cursor_lists(eb)
        if eb.jump_index <= 0 or not eb.jump_list:
            return False
        eb.jump_index -= 1
        self._restore_cursor_only(eb, eb.jump_list[eb.jump_index])
        return True

    def jump_forward(self) -> bool:
        eb = self.cur()
        self._normalize_cursor_lists(eb)
        if not eb.jump_list:
            return False
        if eb.jump_index < 0:
            return False
        if eb.jump_index >= len(eb.jump_list) - 1:
            return False
        eb.jump_index += 1
        self._restore_cursor_only(eb, eb.jump_list[eb.jump_index])
        return True

    def jump_to_index(self, idx: int) -> bool:
        """Jump to an explicit jumplist entry (0-based index)."""
        eb = self.cur()
        self._normalize_cursor_lists(eb)
        if not eb.jump_list:
            return False
        i = int(idx)
        if i < 0 or i >= len(eb.jump_list):
            return False
        eb.jump_index = i
        self._restore_cursor_only(eb, eb.jump_list[eb.jump_index])
        try:
            self.ensure_cursor_visible()
        except Exception:
            pass
        return True

    def jump_info(self) -> tuple[int, int]:
        eb = self.cur()
        return int(eb.jump_index), int(len(eb.jump_list))

    def clear_jumps(self) -> None:
        eb = self.cur()
        eb.jump_list.clear()
        eb.jump_index = -1
    def selection_range(self, i: int | None = None) -> tuple[Cursor, Cursor] | None:
        sel = self.selection(i)
        if sel is None:
            return None
        s, e = sel.normalized()
        if (s.line, s.col) == (e.line, e.col):
            return None
        return s, e

    def selection_text(self, i: int | None = None) -> str:
        rng = self.selection_range(i)
        if rng is None:
            return ""
        s, e = rng
        return self.cur().buf.get_range_text(s, e)

    def _all_selection_ranges(self) -> list[tuple[int, Cursor, Cursor]]:
        eb = self.cur()
        self._normalize_cursor_lists(eb)
        out: list[tuple[int, Cursor, Cursor]] = []
        for i in range(len(eb.cursors)):
            rng = self.selection_range(i)
            if rng is None:
                continue
            s, e = rng
            out.append((i, s, e))
        return out

    def _delete_selections(self) -> bool:
        """Delete all non-empty selections across cursors."""
        eb = self.cur()
        ranges = self._all_selection_ranges()
        if not ranges:
            return False
        # Delete from bottom to top so earlier coordinates remain valid.
        ranges.sort(key=lambda t: (t[1].line, t[1].col), reverse=True)
        for i, s, e in ranges:
            eb.cursors[i] = eb.buf.delete_range(s, e)
            eb.sel_anchors[i] = None
        return True

    # ----- files -----
    def open_file(self, path: str) -> bool:
        p = Path(str(path or "")).expanduser()

        # Refuse to open directories (deterministic UX + avoids exceptions).
        try:
            if p.exists() and p.is_dir():
                self.message(f"open: is a directory: {p}")
                return False
        except OSError:
            pass

        # If this file is already open (by normalized path), just switch to it.
        target_norm = self._normalize_path(str(p))
        if target_norm:
            for name, eb in self.buffers.items():
                if eb.buf.path and self._normalize_path(str(eb.buf.path)) == target_norm:
                    self.switch_buffer(name)
                    self._push_recent_file(str(eb.buf.path))
                    return True

        text = p.read_text(encoding="utf-8") if p.exists() else ""
        self.new_buffer(name=str(p), text=text, path=str(p))
        self._push_recent_file(str(p))

        # lifecycle hook
        try:
            self._emit_mx_hook("ed.on-open", str(self.cur().name), str(p), self.filetype())
        except Exception:
            pass
        return True

    def save(self) -> None:
        eb = self.cur()
        if bool(eb.local_options.get("readonly")):
            raise RuntimeError("Buffer is read-only")
        if not eb.buf.path:
            raise RuntimeError("Buffer has no path")
        p = Path(str(eb.buf.path))
        if p.exists() and p.is_dir():
            raise IsADirectoryError(str(p))
        p.write_text(eb.buf.get_text(), encoding="utf-8")
        eb.buf.dirty = False
        self._push_recent_file(str(eb.buf.path))
        try:
            self._emit_mx_hook("ed.on-save", str(eb.name), str(eb.buf.path))
        except Exception:
            pass

    def load_user_init(self, *, path: str | None = None) -> bool:
        """Load a user init/rc file (best-effort).

        Default path: ~/.config/micromax/init.mx
        Override via the MICROMAX_INIT environment variable or the explicit path arg.

        Returns True when a file existed and was evaluated successfully.
        """
        raw = path or os.environ.get("MICROMAX_INIT") or "~/.config/micromax/init.mx"
        p = Path(raw).expanduser()
        if not p.exists() or p.is_dir():
            return False
        try:
            self.vm.eval(p.read_text(encoding="utf-8"), filename=str(p))
        except Exception as e:
            self.message(f"init error: {e}")
            return False
        return True

    # ----- viewport (scrolling model) -----
    def viewport_model(self) -> dict[str, int]:
        """Return the current viewport model.

        This is UI-owned state, but stored in the headless core so actions can
        keep the cursor visible and future renderers can share semantics.
        """
        return {
            "top_line": int(self.viewport_top_line),
            "top_subline": int(self.viewport_top_subline),
            "left_col": int(self.viewport_left_col),
            "height": int(self.viewport_height),
            "width": int(self.viewport_width),
        }

    def set_viewport(
        self,
        *,
        top_line: int | None = None,
        top_subline: int | None = None,
        left_col: int | None = None,
        height: int | None = None,
        width: int | None = None,
        follow_cursor: bool = True,
    ) -> None:
        """Set viewport fields (best-effort clamped)."""
        if height is not None:
            self.viewport_height = max(1, int(height))
        if width is not None:
            self.viewport_width = max(1, int(width))

        eb = self.cur()
        softwrap = bool(self.options.get("softwrap", local=eb.local_options))
        # When softwrap is enabled, horizontal scrolling is disabled.
        if softwrap:
            self.viewport_left_col = 0
        max_top = max(0, len(eb.buf.lines) - 1)
        # Softwrap introduces a secondary vertical offset: which wrapped row within
        # `top_line` is at the top of the viewport.
        if not bool(self.options.get("softwrap", local=eb.local_options)):
            self.viewport_top_subline = 0
        if top_subline is not None:
            self.viewport_top_subline = max(0, int(top_subline))
        if top_line is not None:
            self.viewport_top_line = max(0, min(int(top_line), max_top))
            if top_subline is None:
                self.viewport_top_subline = 0
        if left_col is not None:
            # When softwrap is enabled, horizontal scrolling is disabled.
            if bool(self.options.get("softwrap", local=eb.local_options)):
                self.viewport_left_col = 0
            else:
                self.viewport_left_col = max(0, int(left_col))
        if follow_cursor:
            self.ensure_cursor_visible()

    # ----- softwrap visual-row mapping helpers -----
    def _softwrap_contindent_setting(self, eb: "EditorBuffer") -> int:
        try:
            return int(self.options.get("softwrap.contindent", local=eb.local_options))
        except Exception:
            return -1

    @staticmethod
    def _leading_ws_cols(s: str) -> int:
        # Count leading spaces/tabs as visual columns (tabs count as 1 here; renderers may expand later).
        n = 0
        for ch in str(s or ""):
            if ch in (" ", "	"):
                n += 1
            else:
                break
        return int(n)

    def _contindent_for_line(self, eb: "EditorBuffer", s: str, *, w: int) -> int:
        """Continuation indent for wrapped fragments under softwrap.

        This mirrors the common UX of "use the original line's indent for wrapped
        fragments", while keeping the model tiny and deterministic.
        """
        w = int(w)
        if w <= 1:
            return 0
        setting = self._softwrap_contindent_setting(eb)
        if setting == 0:
            return 0
        if setting < 0:
            lead = self._leading_ws_cols(s)
            max_cont = min(8, w - 1)
            return max(0, min(int(lead), int(max_cont)))
        return max(0, min(int(setting), w - 1))

    @staticmethod
    def _wrap_seg(w: int, cont: int) -> int:
        w = int(w)
        cont = max(0, int(cont))
        if w <= 0:
            return 1
        if cont <= 0:
            return max(1, w)
        return max(1, w - cont)

    @classmethod
    def _wrap_start_for_row(cls, w: int, cont: int, row: int) -> int:
        w = int(w)
        row = max(0, int(row))
        if row <= 0:
            return 0
        seg = cls._wrap_seg(w, cont)
        return int(w + (row - 1) * seg)

    @classmethod
    def _wrap_cap_for_row(cls, w: int, cont: int, row: int) -> int:
        w = int(w)
        if row <= 0:
            return max(0, w)
        return cls._wrap_seg(w, cont)

    @classmethod
    def _wrap_end_for_row(cls, s_len: int, w: int, cont: int, row: int) -> int:
        start = cls._wrap_start_for_row(w, cont, row)
        cap = cls._wrap_cap_for_row(w, cont, row)
        return min(int(s_len), int(start + cap))

    @classmethod
    def _wraps_for_line_with_cont(cls, s: str, w: int, cont: int) -> int:
        w = int(w)
        if w <= 0:
            return 1
        if s == "":
            return 1
        cont = max(0, min(int(cont), w - 1))
        if len(s) <= w:
            return 1
        seg = cls._wrap_seg(w, cont)
        rem = len(s) - w
        return int(1 + (rem + seg - 1) // seg)

    @classmethod
    def _wrap_row_for_col_with_cont(cls, s: str, col: int, w: int, cont: int) -> int:
        """Return wrap-row index for a character column in a softwrapped line."""
        w = int(w)
        if w <= 0:
            return 0
        col = max(0, min(int(col), len(s)))
        if len(s) <= w:
            return 0
        cont = max(0, min(int(cont), w - 1))
        seg = cls._wrap_seg(w, cont)
        if col < w:
            return 0

        # If the cursor is exactly at EOL on a wrap boundary, keep it on the last visual row.
        if col > 0 and col == len(s):
            rem = len(s) - w
            if rem > 0 and (rem % seg) == 0:
                return max(0, rem // seg)

        return int(1 + ((col - w) // seg))

    def _wraps_for_line(self, eb: "EditorBuffer", s: str, *, w: int) -> int:
        cont = self._contindent_for_line(eb, s, w=w)
        return self._wraps_for_line_with_cont(s, int(w), int(cont))

    def _visual_row_index(self, eb: "EditorBuffer", line: int, wrap_row: int, *, w: int) -> int:
        """Return global visual-row index for (line, wrap_row)."""
        line = max(0, min(int(line), max(0, len(eb.buf.lines) - 1)))
        wrap_row = max(0, int(wrap_row))
        y = 0
        for li in range(0, line):
            y += self._wraps_for_line(eb, eb.buf.lines[li], w=int(w))
        return int(y + wrap_row)

    def _cursor_visual_yx(self, eb: "EditorBuffer", c: "Cursor", *, w: int) -> tuple[int, int]:
        """Return (global_y, x_in_wrap_row) for cursor c under width w."""
        w = int(w)
        if w <= 0:
            return (int(c.line), int(c.col))
        line = max(0, min(int(c.line), max(0, len(eb.buf.lines) - 1)))
        s = eb.buf.lines[line] if line < len(eb.buf.lines) else ""
        col = max(0, min(int(c.col), len(s)))
        cont = self._contindent_for_line(eb, s, w=w)
        wrap_row = self._wrap_row_for_col_with_cont(s, col, w, cont)
        wrap_start = self._wrap_start_for_row(w, cont, wrap_row)
        x = (col - wrap_start) + (cont if wrap_row > 0 else 0)
        y = self._visual_row_index(eb, line, wrap_row, w=w)
        return (int(y), int(x))

    def _total_visual_rows(self, eb: "EditorBuffer", *, w: int) -> int:
        w = int(w)
        if w <= 0:
            return max(1, len(eb.buf.lines))
        return max(1, sum(self._wraps_for_line(eb, s, w=w) for s in eb.buf.lines))

    def _doc_pos_for_visual_row(self, eb: "EditorBuffer", target_y: int, goal_x: int, *, w: int) -> "Cursor":
        """Map a global visual-row index + desired x to a document Cursor."""
        w = int(w)
        if w <= 0:
            # Fallback: treat visual rows as logical lines.
            li = max(0, min(int(target_y), max(0, len(eb.buf.lines) - 1)))
            s = eb.buf.lines[li] if li < len(eb.buf.lines) else ""
            return Cursor(li, max(0, min(int(goal_x), len(s))))

        y = max(0, int(target_y))
        goal_x = max(0, int(goal_x))
        acc = 0
        if not eb.buf.lines:
            return Cursor(0, 0)
        for li, s in enumerate(eb.buf.lines):
            cont = self._contindent_for_line(eb, s, w=w)
            wraps = self._wraps_for_line_with_cont(s, w, cont)
            if y < acc + wraps:
                sub = y - acc
                if s == "":
                    return Cursor(li, 0)
                wrap_start = self._wrap_start_for_row(w, cont, sub)
                row_end = self._wrap_end_for_row(len(s), w, cont, sub)
                if sub <= 0:
                    col = min(wrap_start + goal_x, row_end)
                    return Cursor(li, col)
                # continuation row: x includes indent
                if goal_x <= cont:
                    return Cursor(li, wrap_start)
                col = min(wrap_start + (goal_x - cont), row_end)
                return Cursor(li, col)
            acc += wraps
        # Clamp to end of last line.
        li = len(eb.buf.lines) - 1
        s = eb.buf.lines[li]
        return Cursor(li, len(s))

    def _viewport_visual_start(self, eb: "EditorBuffer", *, w: int) -> int:
        """Return global visual-row index for the viewport's top."""
        w = int(w)
        top = max(0, min(int(self.viewport_top_line), max(0, len(eb.buf.lines) - 1)))
        sub = max(0, int(self.viewport_top_subline))
        if w <= 0:
            return int(top)
        s = eb.buf.lines[top] if top < len(eb.buf.lines) else ""
        wraps = self._wraps_for_line(eb, s, w=w)
        sub = min(sub, max(0, wraps - 1))
        return self._visual_row_index(eb, top, sub, w=w)

    def _set_viewport_from_visual_start(self, eb: "EditorBuffer", start_y: int, *, w: int) -> None:
        """Set viewport_top_line/top_subline from a global visual-row index."""
        w = int(w)
        if not eb.buf.lines:
            self.viewport_top_line = 0
            self.viewport_top_subline = 0
            return
        if w <= 0:
            self.viewport_top_line = max(0, min(int(start_y), max(0, len(eb.buf.lines) - 1)))
            self.viewport_top_subline = 0
            return
        y = max(0, int(start_y))
        acc = 0
        for li, s in enumerate(eb.buf.lines):
            wraps = self._wraps_for_line(eb, s, w=w)
            if y < acc + wraps:
                self.viewport_top_line = li
                self.viewport_top_subline = y - acc
                return
            acc += wraps
        self.viewport_top_line = len(eb.buf.lines) - 1
        self.viewport_top_subline = 0


    def _move_cursors_visual(self, dy: int, *, extend_selection: bool = False) -> bool:
        """Move all cursors by dy visual rows when softwrap is enabled."""
        eb = self.cur()
        self._normalize_cursor_lists(eb)
        w = int(self.viewport_width)
        if w <= 0:
            # no viewport width yet; fall back to logical-line motion
            for i, c in enumerate(eb.cursors):
                eb.cursors[i] = eb.buf.clamp(Cursor(int(c.line) + int(dy), int(c.col)))
            if not extend_selection:
                self.clear_selection()
            return True

        total = self._total_visual_rows(eb, w=w)
        # Maintain per-cursor goal x (visual column) for vertical motions.
        if not hasattr(eb, "goal_x_by_cursor"):
            eb.goal_x_by_cursor = {}  # type: ignore[attr-defined]

        for i, c in enumerate(eb.cursors):
            cid = int(eb.cursor_ids[i]) if i < len(eb.cursor_ids) else i
            y, x = self._cursor_visual_yx(eb, c, w=w)
            goal_x = int(eb.goal_x_by_cursor.get(cid, x))  # type: ignore[attr-defined]
            target_y = max(0, min(int(y) + int(dy), max(0, total - 1)))
            eb.cursors[i] = eb.buf.clamp(self._doc_pos_for_visual_row(eb, target_y, goal_x, w=w))

        if not extend_selection:
            self.clear_selection()
        return True

    def ensure_cursor_visible(self) -> None:
        """Adjust viewport so the primary cursor is visible."""
        try:
            eb = self.cur()
            self._normalize_cursor_lists(eb)
            c = eb.cursors[eb.primary]
        except Exception:
            return
        h = int(self.viewport_height)
        w = int(self.viewport_width)
        if h <= 0 or w <= 0:
            return

        softwrap = bool(self.options.get("softwrap", local=eb.local_options))

        # vertical
        if not softwrap:
            if int(c.line) < int(self.viewport_top_line):
                self.viewport_top_line = int(c.line)
            elif int(c.line) >= int(self.viewport_top_line) + h:
                self.viewport_top_line = max(0, int(c.line) - h + 1)
            self.viewport_top_subline = 0
        else:
            # Softwrap scrolling is in *visual rows* (wrapped fragments), not logical lines.
            start_y = self._viewport_visual_start(eb, w=w)
            cur_y, _cur_x = self._cursor_visual_yx(eb, c, w=w)
            total = self._total_visual_rows(eb, w=w)
            max_start = max(0, total - h)
            if cur_y < start_y:
                start_y = cur_y
            elif cur_y >= start_y + h:
                start_y = cur_y - h + 1
            start_y = max(0, min(int(start_y), int(max_start)))
            self._set_viewport_from_visual_start(eb, start_y, w=w)

        # horizontal
        if bool(self.options.get("softwrap", local=eb.local_options)):
            # softwrap disables horizontal scrolling
            self.viewport_left_col = 0
        else:
            if int(c.col) < int(self.viewport_left_col):
                self.viewport_left_col = int(c.col)
            elif int(c.col) >= int(self.viewport_left_col) + w:
                self.viewport_left_col = max(0, int(c.col) - w + 1)

        # Clamp top against buffer length.
        self.viewport_top_line = max(0, min(int(self.viewport_top_line), max(0, len(eb.buf.lines) - 1)))
        if softwrap and eb.buf.lines:
            wraps = self._wraps_for_line(eb, eb.buf.lines[int(self.viewport_top_line)], w=int(w))
            self.viewport_top_subline = max(0, min(int(self.viewport_top_subline), max(0, wraps - 1)))
        else:
            self.viewport_top_subline = 0
        self.viewport_left_col = max(0, int(self.viewport_left_col))


    def view_rows(self, *, height: int | None = None, width: int | None = None) -> list[tuple[int, int, str]]:
        """Return screen rows for the active buffer under the current viewport.

        Each row is a tuple: (line_index, start_col, fragment).

        - When softwrap is disabled, start_col is the viewport's left_col and
          fragment is a simple substring slice.
        - When softwrap is enabled, long logical lines are wrapped into multiple
          screen rows and start_col is the wrap's starting *character* column.

        Notes:
          - This is a **rendering model**, not a UI. It intentionally ignores
            styling/spans for now.
          - Tabs are treated as single characters here; a future renderer can
            expand tabs to visual columns.
        """

        eb = self.cur()
        h = int(height if height is not None else self.viewport_height)
        w = int(width if width is not None else self.viewport_width)
        if h <= 0 or w <= 0:
            return []

        top = int(self.viewport_top_line)
        left = int(self.viewport_left_col)
        softwrap = bool(self.options.get("softwrap", local=eb.local_options))

        rows: list[tuple[int, int, str]] = []
        if not softwrap:
            for row in range(h):
                li = top + row
                if li >= len(eb.buf.lines):
                    break
                ln = eb.buf.lines[li]
                frag = ln[left : left + w]
                rows.append((li, left, frag))
            return rows

        # softwrap: walk logical lines, emit wrapped fragments until the screen fills.
        li = top
        first_subline = max(0, int(self.viewport_top_subline))
        while li < len(eb.buf.lines) and len(rows) < h:
            ln = eb.buf.lines[li]
            if ln == "":
                rows.append((li, 0, ""))
                li += 1
                continue

            cont = self._contindent_for_line(eb, ln, w=w)
            wraps = self._wraps_for_line_with_cont(ln, w, cont)
            sub = first_subline if li == top else 0
            sub = max(0, min(int(sub), max(0, wraps - 1)))

            while len(rows) < h and sub < wraps:
                start = self._wrap_start_for_row(w, cont, sub)
                cap = self._wrap_cap_for_row(w, cont, sub)
                prefix = (" " * cont) if sub > 0 and cont > 0 else ""
                frag = prefix + ln[start : start + cap]
                rows.append((li, start, frag))
                sub += 1
            li += 1
        return rows

    def cursor_view_pos(self, *, height: int | None = None, width: int | None = None) -> tuple[int, int]:
        """Return (y, x) of the primary cursor within the current viewport.

        For softwrap, this maps the cursor into wrapped screen rows.
        """
        try:
            eb = self.cur()
            self._normalize_cursor_lists(eb)
            c = eb.cursors[eb.primary]
        except Exception:
            return (0, 0)

        h = int(height if height is not None else self.viewport_height)
        w = int(width if width is not None else self.viewport_width)
        if h <= 0 or w <= 0:
            return (0, 0)

        top = int(self.viewport_top_line)
        left = int(self.viewport_left_col)
        softwrap = bool(self.options.get("softwrap", local=eb.local_options))

        if not softwrap:
            return (int(c.line) - top, int(c.col) - left)

        start_y = self._viewport_visual_start(eb, w=w)
        cy, cx = self._cursor_visual_yx(eb, c, w=w)
        y = int(cy) - int(start_y)
        x = int(cx)
        return (y, x)

    # ----- timers (host-driven, deterministic) -----
    def now(self) -> float:
        return float(self._now_fn())

    def pump_timers(self, *, limit: int = 1000) -> int:
        """Run due timer callbacks.

        Timer callbacks run in the embedded VM and are treated like hooks:
        best-effort notifications. We isolate stack effects and record
        exceptions as editor messages.
        """

        now = self.now()
        tasks = self.timers.pop_due(now=now, limit=int(limit))
        ran = 0
        for t in tasks:
            depth = len(self.vm.stack)
            try:
                self.vm.exec_xt(t.xt)
            except Exception as e:
                self.message(f"timer {t.task_id} error: {e}")
            finally:
                del self.vm.stack[depth:]
            ran += 1
        return int(ran)

    # ----- syntax highlighting (span model) -----
    def highlight_tags(self) -> list[str]:
        return list(HIGHLIGHT_TAGS)

    def highlight_spans(self, start: int, count: int) -> list[list[list[object]]]:
        """Return per-line highlight spans for the active buffer.

        Result is a list aligned with the requested range: out[0] contains
        spans for line `start`. Each per-line span is [start_col, end_col, tag].

        This is intentionally tiny; renderers/themes decide how to map tags to
        color or attributes.
        """

        eb = self.cur()
        lines = eb.buf.lines
        if int(count) <= 0 or not lines:
            return []
        a = max(0, int(start))
        b = min(len(lines), a + int(count))
        ft = str(self.filetype())
        return [highlight_line(ft, str(lines[i])) for i in range(a, b)]

    def page_height(self, *, eb: EditorBuffer | None = None) -> int:
        """Return the current page movement size.

        If a UI has set a viewport height, page movement uses it. Otherwise we
        fall back to the `page.height` option.
        """
        if int(self.viewport_height) > 0:
            return int(self.viewport_height)
        eb2 = eb or self.cur()
        return int(self.options.get("page.height", local=eb2.local_options))

    def is_protected_buffer(self, eb: EditorBuffer | None = None) -> bool:
        """Return True if this buffer is marked as protected/read-only."""

        eb2 = eb or self.cur()
        try:
            return bool(eb2.local_options.get("readonly"))
        except Exception:
            return False

    # ----- status / infobar model -----
    def editor_mode(self) -> str:
        """Return a tiny, headless editor mode label.

        This is intentionally conservative: until we have richer modal editing,
        the statusline model only distinguishes normal editing from active prompt
        modes. Macro recording/playback are reported as orthogonal flags in the
        status model instead of becoming separate editor modes.
        """

        if self.prompt is not None:
            kind = str(self.prompt.kind or "").strip().lower()
            return kind or "prompt"
        return "normal"

    def status_model(self) -> dict[str, Any]:
        """Return a small, portable statusline/infobar model.

        The goal is to let future UI layers render shared editor state without
        inventing semantics. Values are chosen to be easy for micromax scripts,
        tests, and future tooling to inspect directly.
        """

        eb = self.cur()
        self._normalize_cursor_lists(eb)
        c = eb.cursors[eb.primary]

        path = str(eb.buf.path or "")
        file_name = Path(path).name if path else str(eb.name)
        filetype = self.filetype()

        protected = bool(eb.local_options.get("readonly"))

        # OS-level read-only status (file permissions). This is distinct from
        # "protected" buffers: you can still edit an unwritable file and then
        # `saveas` elsewhere, but protected buffers should reject edits.
        try:
            readonly_file = bool(path) and Path(path).exists() and (not Path(path).is_dir()) and (not os.access(Path(path), os.W_OK))
        except OSError:
            readonly_file = False
        readonly = bool(protected) or bool(readonly_file)

        selection_count = 0
        for i in range(len(eb.cursors)):
            sel = self.selection(i)
            if sel is not None and not sel.is_empty():
                selection_count += 1

        primary_sel = self.selection(None)
        primary_sel_chars = 0
        if primary_sel is not None and not primary_sel.is_empty():
            primary_sel_chars = len(self.selection_text(None))

        prompt_kind = self.prompt.kind if self.prompt is not None else ""
        prompt_text = self.prompt.text if self.prompt is not None else ""
        prompt_current_row = self.prompt_current_row()
        prompt_current_insert = prompt_current_row[0] if prompt_current_row else ""
        prompt_current_kind = prompt_current_row[1] if prompt_current_row else ""
        prompt_current_menu = prompt_current_row[2] if prompt_current_row else ""
        prompt_current_info = prompt_current_row[3] if prompt_current_row else ""

        out: dict[str, Any] = {
            "mode": self.editor_mode(),
            "keymode": self.current_key_mode() or "",
            "keymode_once": 1 if self.current_key_mode_once() else 0,
            "buffer_name": str(eb.name),
            "file_name": str(file_name),
            "filetype": str(filetype),
            "encoding": "utf-8",
            "fileformat": "unix",
            "path": path,
            "cwd": str(Path.cwd()),
            "dirty": 1 if eb.buf.dirty else 0,
            "readonly": 1 if readonly else 0,
            "protected": 1 if protected else 0,
            "line": int(c.line),
            "col": int(c.col),
            "display_line": int(c.line) + 1,
            "display_col": int(c.col) + 1,
            "position": f"{int(c.line) + 1}:{int(c.col) + 1}",
            "line_count": int(len(eb.buf.lines)),
            "percentage": int((int(c.line) / max(1, int(len(eb.buf.lines)) - 1)) * 100),
            "cursor_count": int(len(eb.cursors)),
            "primary_cursor_index": int(eb.primary),
            "cursor_summary": f"{int(eb.primary) + 1}/{int(len(eb.cursors))}",
            "selection_count": int(selection_count),
            "selection_summary": str(int(selection_count)),
            "primary_selection_chars": int(primary_sel_chars),
            "prompt_kind": str(prompt_kind),
            "prompt_text": str(prompt_text),
            "prompt_cursor": int(self.prompt.cursor) if self.prompt is not None else 0,

            "viewport_top_line": int(self.viewport_top_line),
            "viewport_left_col": int(self.viewport_left_col),
            "viewport_height": int(self.viewport_height),
            "viewport_width": int(self.viewport_width),
            "display_viewport_top_line": int(self.viewport_top_line) + 1,
            "display_viewport_left_col": int(self.viewport_left_col) + 1,
            "prompt_current_insert": str(prompt_current_insert),
            "prompt_current_kind": str(prompt_current_kind),
            "prompt_current_menu": str(prompt_current_menu),
            "prompt_current_info": str(prompt_current_info),
            "prompt_current_section": self.prompt_current_section(),
            "prompt_current_preview": self.prompt_current_preview(),
            "last_message": str(self.messages[-1]) if self.messages else "",
            "macro_recording": 1 if self.macro_recording else 0,
            "macro_playing": 1 if self._macro_playing else 0,
            "macro_name": str(self._macro_target) if self.macro_recording else "",
        }
        return out

    def status_summary(self) -> str:
        """Return a compact, deterministic status summary string.

        This is mainly for the headless REPL and `showstatus` command. UI layers
        should prefer `status_model()`.
        """

        st = self.status_model()
        parts = [
            f"mode={st['mode']}",
            f"buffer={st['file_name']!r}",
            f"dirty={st['dirty']}",
            f"readonly={st['readonly']}",
            f"pos={st['position']}",
            f"cursors={int(st['primary_cursor_index']) + 1}/{st['cursor_count']}",
            f"sels={st['selection_count']}",
            f"selchars={st['primary_selection_chars']}",
        ]
        if st['keymode']:
            suffix = '!' if st.get('keymode_once') else ''
            parts.append(f"keymode={st['keymode']!r}{suffix}")
        if st['prompt_kind']:
            parts.append(f"prompt={st['prompt_kind']!r}")
        if st['prompt_kind'] in ('palette', 'topic', 'binding') and st.get('prompt_current_preview'):
            parts.append(f"prompt_item={st['prompt_current_preview']!r}")
        if st['macro_recording']:
            parts.append(f"macro=rec:{st['macro_name']!r}")
        if st['macro_playing']:
            parts.append("macro=play")
        return " ".join(parts)

    def statusline_text(self, width: int) -> str:
        """Return a micro-esque single-line statusline string for the current viewport width.

        UI layers should generally prefer `status_model()` for richer structure, but having
        a deterministic reference formatter is useful for the minimal TUI, REPL output, and tests.
        """
        if width <= 0:
            return ""

        if not bool(self.options.get("statusline", local=self.cur().local_options)):
            return ""

        st = self.status_model()
        fmt_l = str(self.options.get("statusformatl", local=self.cur().local_options) or "")
        fmt_r = str(self.options.get("statusformatr", local=self.cur().local_options) or "")
        left = render_status_template(fmt_l, ed=self, status=st)
        right = render_status_template(fmt_r, ed=self, status=st).strip()

        # If the right side alone is too long, show the end (keeps mode/key hints).
        if len(right) >= width:
            return right[-width:]

        # Fit left + right into width, truncating left if needed.
        avail_left = width - len(right)
        left2 = left
        if len(left2) > avail_left:
            # Reserve at least one char if possible; add an ellipsis when truncating.
            if avail_left <= 0:
                left2 = ""
            elif avail_left == 1:
                left2 = left2[:1]
            else:
                left2 = left2[: max(0, avail_left - 1)] + "…"

        padding = " " * max(0, width - len(left2) - len(right))
        return (left2 + padding + right)[:width]

    # ----- prompt (command bar / find bar) -----
    def enter_prompt(self, kind: str, *, prefill: str = "") -> None:
        self.prompt = Prompt(kind=kind)
        self.prompt.prefill(prefill)
        self._push_prompt_keymode()

    def _palette_prompt_rows(self, query: str, *, limit: int = 40) -> list[list[str]]:
        q = str(query or "").strip()
        rows = self.command_palette_apropos_rows(q)
        return [[str(x) for x in row[:4]] for row in rows[: max(1, int(limit))]]

    def _topic_prompt_rows(self, query: str, *, limit: int = 40) -> list[list[str]]:
        q = str(query or "").strip()
        rows = self.apropos_rows(q) if q else self.help_topic_rows()
        return [[str(x) for x in row[:4]] for row in rows[: max(1, int(limit))]]

    def _binding_prompt_rows(self, query: str, *, limit: int = 40) -> list[list[str]]:
        q = str(query or "").strip()
        rows = self.binding_apropos_rows(q) if q else self.binding_prompt_rows()
        return [[str(x) for x in row[:4]] for row in rows[: max(1, int(limit))]]


    def _buffer_prompt_rows(self, query: str, *, limit: int = 40) -> list[list[str]]:
        q = str(query or "").strip()
        rows = self.buffer_apropos_rows(q) if q else self.buffer_prompt_rows()
        return [[str(x) for x in row[:4]] for row in rows[: max(1, int(limit))]]

    def _mark_prompt_rows(self, query: str, *, limit: int = 40) -> list[list[str]]:
        q = str(query or "").strip()
        rows = self.mark_apropos_rows(q) if q else self.mark_prompt_rows()
        return [[str(x) for x in row[:4]] for row in rows[: max(1, int(limit))]]

    def _jump_prompt_rows(self, query: str, *, limit: int = 40) -> list[list[str]]:
        q = str(query or "").strip()
        rows = self.jump_apropos_rows(q) if q else self.jump_prompt_rows()
        return [[str(x) for x in row[:4]] for row in rows[: max(1, int(limit))]]

    def _plugin_prompt_rows(self, query: str, *, limit: int = 40) -> list[list[str]]:
        q = str(query or "").strip()
        rows = self.plugin_apropos_rows(q) if q else self.plugin_prompt_rows()
        return [[str(x) for x in row[:4]] for row in rows[: max(1, int(limit))]]

    def _recent_prompt_rows(self, query: str, *, limit: int = 40) -> list[list[str]]:
        q = str(query or "").strip()
        rows = self.recent_apropos_rows(q) if q else self.recent_prompt_rows()
        return [[str(x) for x in row[:4]] for row in rows[: max(1, int(limit))]]

    def _refresh_buffer_prompt_suggestions(self, *, limit: int = 40) -> bool:
        if self.prompt is None or self.prompt.kind != "buffer":
            return False
        rows = self._buffer_prompt_rows(self.prompt.text, limit=limit)
        if not rows:
            return False
        cands = [str(row[0]) for row in rows]
        self.prompt.begin_suggestions(cands, start=0, end=len(self.prompt.text), rows=rows)
        return True

    def _refresh_mark_prompt_suggestions(self, *, limit: int = 40) -> bool:
        if self.prompt is None or self.prompt.kind != "mark":
            return False
        rows = self._mark_prompt_rows(self.prompt.text, limit=limit)
        if not rows:
            return False
        cands = [str(row[0]) for row in rows]
        self.prompt.begin_suggestions(cands, start=0, end=len(self.prompt.text), rows=rows)
        return True

    def _refresh_jump_prompt_suggestions(self, *, limit: int = 40) -> bool:
        if self.prompt is None or self.prompt.kind != "jump":
            return False
        rows = self._jump_prompt_rows(self.prompt.text, limit=limit)
        if not rows:
            return False
        cands = [str(row[0]) for row in rows]
        self.prompt.begin_suggestions(cands, start=0, end=len(self.prompt.text), rows=rows)
        return True

    def _refresh_plugin_prompt_suggestions(self, *, limit: int = 40) -> bool:
        if self.prompt is None or self.prompt.kind != "plugin":
            return False
        rows = self._plugin_prompt_rows(self.prompt.text, limit=limit)
        if not rows:
            return False
        cands = [str(row[0]) for row in rows]
        self.prompt.begin_suggestions(cands, start=0, end=len(self.prompt.text), rows=rows)
        return True

    def _refresh_recent_prompt_suggestions(self, *, limit: int = 40) -> bool:
        if self.prompt is None or self.prompt.kind != "recent":
            return False
        rows = self._recent_prompt_rows(self.prompt.text, limit=limit)
        if not rows:
            return False
        cands = [str(row[0]) for row in rows]
        self.prompt.begin_suggestions(cands, start=0, end=len(self.prompt.text), rows=rows)
        return True

    def _refresh_doc_prompt_suggestions(self, *, limit: int = 40) -> bool:
        if self.prompt is None or self.prompt.kind != "doc":
            return False
        q = str(self.prompt.text or "").strip()
        rows = self.doc_apropos_rows(q, limit=limit) if q else self.doc_prompt_rows()
        if not rows:
            return False
        cands = [str(row[0]) for row in rows]
        self.prompt.begin_suggestions(cands, start=0, end=len(self.prompt.text), rows=rows)
        return True

    def _refresh_helplink_prompt_suggestions(self, *, limit: int = 80) -> bool:
        if self.prompt is None or self.prompt.kind != "helplink":
            return False
        q = str(self.prompt.text or "").strip()
        rows = self.help_link_rows(q, limit=limit)
        if not rows:
            return False
        cands = [str(row[0]) for row in rows]
        self.prompt.begin_suggestions(cands, start=0, end=len(self.prompt.text), rows=rows)
        return True

    def _refresh_helpoutline_prompt_suggestions(self, *, limit: int = 120) -> bool:
        if self.prompt is None or self.prompt.kind != "helpoutline":
            return False
        q = str(self.prompt.text or "").strip()
        rows = self.help_outline_rows(q, limit=limit)
        if not rows:
            return False
        cands = [str(row[0]) for row in rows]
        self.prompt.begin_suggestions(cands, start=0, end=len(self.prompt.text), rows=rows)
        return True

    def _refresh_helpnav_prompt_suggestions(self, *, limit: int = 160) -> bool:
        if self.prompt is None or self.prompt.kind != "helpnav":
            return False
        q = str(self.prompt.text or "").strip()
        rows = self.help_nav_rows(q, limit=limit)
        if not rows:
            return False
        cands = [str(row[0]) for row in rows]
        self.prompt.begin_suggestions(cands, start=0, end=len(self.prompt.text), rows=rows)
        return True


    def _refresh_palette_prompt_suggestions(self, *, limit: int = 40) -> bool:
        if self.prompt is None or self.prompt.kind != "palette":
            return False
        rows = self._palette_prompt_rows(self.prompt.text, limit=limit)
        if not rows:
            return False
        cands = [str(row[0]) for row in rows]
        self.prompt.begin_suggestions(cands, start=0, end=len(self.prompt.text), rows=rows)
        return True

    def _refresh_topic_prompt_suggestions(self, *, limit: int = 40) -> bool:
        if self.prompt is None or self.prompt.kind != "topic":
            return False
        rows = self._topic_prompt_rows(self.prompt.text, limit=limit)
        if not rows:
            return False
        cands = [str(row[0]) for row in rows]
        self.prompt.begin_suggestions(cands, start=0, end=len(self.prompt.text), rows=rows)
        return True

    def _refresh_binding_prompt_suggestions(self, *, limit: int = 40) -> bool:
        if self.prompt is None or self.prompt.kind != "binding":
            return False
        rows = self._binding_prompt_rows(self.prompt.text, limit=limit)
        if not rows:
            return False
        cands = [str(row[0]) for row in rows]
        self.prompt.begin_suggestions(cands, start=0, end=len(self.prompt.text), rows=rows)
        return True

    def enter_command_palette(self, query: str = "") -> None:
        self.enter_prompt("palette", prefill=str(query or ""))
        self._refresh_palette_prompt_suggestions()

    def enter_topic_prompt(self, query: str = "") -> None:
        self.enter_prompt("topic", prefill=str(query or ""))
        self._refresh_topic_prompt_suggestions()

    def enter_binding_prompt(self, query: str = "") -> None:
        self.enter_prompt("binding", prefill=str(query or ""))
        self._refresh_binding_prompt_suggestions()


    def enter_buffer_prompt(self, query: str = "") -> None:
        self.enter_prompt("buffer", prefill=str(query or ""))
        self._refresh_buffer_prompt_suggestions()

    def enter_mark_prompt(self, query: str = "") -> None:
        self.enter_prompt("mark", prefill=str(query or ""))
        self._refresh_mark_prompt_suggestions()


    def enter_jump_prompt(self, query: str = "") -> None:
        self.enter_prompt("jump", prefill=str(query or ""))
        self._refresh_jump_prompt_suggestions()

    def enter_plugin_prompt(self, query: str = "") -> None:
        self.enter_prompt("plugin", prefill=str(query or ""))
        self._refresh_plugin_prompt_suggestions()

    def enter_recent_prompt(self, query: str = "") -> None:
        self.enter_prompt("recent", prefill=str(query or ""))
        self._refresh_recent_prompt_suggestions()

    def enter_doc_prompt(self, query: str = "") -> None:
        self.enter_prompt("doc", prefill=str(query or ""))
        self._refresh_doc_prompt_suggestions()

    def enter_helplink_prompt(self, query: str = "") -> None:
        """Open a picker over links in the current docs/help buffer."""

        self.enter_prompt("helplink", prefill=str(query or ""))
        self._refresh_helplink_prompt_suggestions()

    def enter_helpoutline_prompt(self, query: str = "") -> None:
        """Open a picker over headings in the current docs/help buffer."""

        self.enter_prompt("helpoutline", prefill=str(query or ""))
        self._refresh_helpoutline_prompt_suggestions()

    def enter_helpnav_prompt(self, query: str = "") -> None:
        """Open a combined picker over headings + links in the current docs/help buffer."""

        self.enter_prompt("helpnav", prefill=str(query or ""))
        self._refresh_helpnav_prompt_suggestions()


    def _sync_prompt_after_text_change(self) -> None:
        if self.prompt is None:
            return
        if self.prompt.kind == "palette":
            self._refresh_palette_prompt_suggestions()
        elif self.prompt.kind == "topic":
            self._refresh_topic_prompt_suggestions()
        elif self.prompt.kind == "binding":
            self._refresh_binding_prompt_suggestions()
        elif self.prompt.kind == "buffer":
            self._refresh_buffer_prompt_suggestions()
        elif self.prompt.kind == "mark":
            self._refresh_mark_prompt_suggestions()
        elif self.prompt.kind == "jump":
            self._refresh_jump_prompt_suggestions()
        elif self.prompt.kind == "plugin":
            self._refresh_plugin_prompt_suggestions()
        elif self.prompt.kind == "recent":
            self._refresh_recent_prompt_suggestions()
        elif self.prompt.kind == "doc":
            self._refresh_doc_prompt_suggestions()
        elif self.prompt.kind == "helplink":
            self._refresh_helplink_prompt_suggestions()
        elif self.prompt.kind == "helpoutline":
            self._refresh_helpoutline_prompt_suggestions()
        elif self.prompt.kind == "helpnav":
            self._refresh_helpnav_prompt_suggestions()
        elif self.prompt.kind == "find" and bool(self.options.get("incsearch", local=self.cur().local_options)):
            self.find(self.prompt.text, literal=self.search.literal)

    def set_prompt_text(self, s: str) -> bool:
        if self.prompt is None:
            return False
        self.prompt.set_text(s)
        self._sync_prompt_after_text_change()
        return True

    def set_prompt_text_cursor(self, s: str, cursor: int) -> bool:
        """Set prompt text and cursor (0-based), then refresh prompt state."""
        if self.prompt is None:
            return False
        self.prompt.set_text(s)
        self.prompt.set_cursor(int(cursor))
        self._sync_prompt_after_text_change()
        return True

    def prompt_current_row(self) -> list[str]:
        if self.prompt is None or not self.prompt.suggestion_rows:
            return []
        idx = int(self.prompt.suggest_index)
        if idx < 0 or idx >= len(self.prompt.suggestion_rows):
            idx = 0
        row = list(self.prompt.suggestion_rows[idx][:4])
        while len(row) < 4:
            row.append("")
        return [str(row[0]), str(row[1]), str(row[2]), str(row[3])]

    def prompt_current_section(self) -> str:
        row = self.prompt_current_row()
        if not row:
            return ""
        # Prompt-specific section naming overrides.
        if self.prompt is not None and self.prompt.kind == "helplink":
            # helplink rows are: [label "link" target info]
            label = self._helplink_kind_label([str(x) for x in row])
            if label == "External":
                return "External link"
            if label == "Files":
                return "File link"
            return "Doc link"

        if self.prompt is not None and self.prompt.kind == "helpnav":
            # Rows are either headings ([title "heading" hN line:col])
            # or links ([label "link" target line:col]).
            kind2 = str(row[1] or "").strip().lower()
            if kind2 == "heading":
                return "Heading"
            if kind2 == "link":
                label = self._helplink_kind_label([str(x) for x in row])
                if label == "External":
                    return "External link"
                if label == "Files":
                    return "File link"
                return "Doc link"
            return "Item"
        if self.prompt is not None and self.prompt.kind == "binding":
            return "Binding"
        if self.prompt is not None and self.prompt.kind == "palette":
            label = self._command_palette_section_label(row)
            return label[:-1] if label.endswith("s") else label
        kind = str(row[1] or "")
        if kind == "binding":
            return "Binding"
        single, _plural = self._topic_section_names(kind)
        return single

    def prompt_current_preview(self) -> str:
        row = self.prompt_current_row()
        if not row:
            return ""
        name, _kind, menu, info = row
        section = self.prompt_current_section()
        head = f"{section}: {name}" if section else str(name)
        detail = ""
        if menu and info:
            detail = f"{menu} | {info}"
        elif menu:
            detail = menu
        elif info:
            detail = info
        return head if not detail else f"{head} — {detail}"

    def cancel_prompt(self) -> bool:
        if self.prompt is None:
            return False
        self.prompt = None
        self._pop_prompt_keymode()
        return True

    def _push_history(self, kind: str, text: str) -> None:
        text = text.strip("\n")
        if not text:
            return
        h = self.history.setdefault(kind, [])
        if h and h[-1] == text:
            return
        h.append(text)

        # Keep histories bounded.
        limit = 200
        try:
            limit = max(1, int(self.options.get("history.limit")))
        except Exception:
            limit = 200
        if len(h) > limit:
            del h[:-limit]

        # Best-effort persistence (gated by history.persist + cap.persist).
        try:
            self.save_prompt_history()
        except Exception:
            pass

    def submit_prompt(self) -> bool:
        if self.prompt is None:
            return False
        prompt = self.prompt
        kind = prompt.kind
        text = prompt.text
        self.prompt = None
        self._pop_prompt_keymode()
        if kind == "command":
            # exec_command_line records command history.
            return self.exec_command_line(text)
        if kind == "find":
            self._push_history("find", text)
            return self.find(text)
        if kind == "palette":
            self._push_history("palette", text)
            q = str(text or "").strip()
            target = ""
            target_kind = ""
            if prompt.suggestions:
                idx = int(prompt.suggest_index) % len(prompt.suggestions)
                target = str(prompt.suggestions[idx]).strip()
                row = list(prompt.suggestion_rows[idx][:4]) if idx < len(prompt.suggestion_rows) else []
                target_kind = str(row[1]) if len(row) >= 2 else ""
                if prompt.text != prompt.suggest_base and q:
                    target = q
                    target_kind = ""
            if target and not target_kind:
                if self.command_dispatcher.get(target) is not None:
                    target_kind = "command"
                elif self.actions.get(target) is not None:
                    target_kind = "action"
                elif self._looks_like_path_query(str(target)):
                    target_kind = "openpath"
            if not target:
                if q and self.command_dispatcher.get(q) is not None:
                    target, target_kind = q, "command"
                elif q and self.actions.get(q) is not None:
                    target, target_kind = q, "action"
                elif q:
                    rows = self.command_palette_apropos_rows(q, limit=1)
                    if rows:
                        target = str(rows[0][0]).strip()
                        target_kind = str(rows[0][1]).strip()
            if not target or target_kind not in ("command", "action", "recentfile", "openpath"):
                self.message("commandpick: (none)")
                return False
            if target_kind in ("recentfile", "openpath"):
                # When filesystem listing is enabled, treat directory targets as
                # a drill-down: keep the palette open and navigate into that dir
                # instead of trying to open it as a file.
                if target_kind == "openpath" and bool(self.options.get("cap.fs-list")):
                    try:
                        p = fs_resolve_path(self, str(target))
                        if fs_sandbox_root(self) is not None and not fs_path_allowed(self, p):
                            raise RuntimeError(f"outside cap.fs-root: {p}")
                        if p.exists() and p.is_dir():
                            raw = str(target).strip()
                            if raw and not raw.endswith(("/", "\\")):
                                raw = raw + "/"
                            self.enter_command_palette(raw)
                            return True
                    except Exception:
                        pass

                # Script safety: selecting an openpath/recentfile row must not grant
                # ambient filesystem authority. Require cap.fs-open in script context.
                if self.in_script_context() and not bool(self.options.get("cap.fs-open")):
                    self.message("open: disabled (cap.fs-open). Enable with: set cap.fs-open true")
                    return False

                try:
                    # Optional filesystem sandbox root.
                    if fs_sandbox_root(self) is not None:
                        p2 = fs_resolve_path(self, str(target))
                        if not fs_path_allowed(self, p2):
                            self.message(f"open: outside cap.fs-root: {p2}")
                            return False
                        ok2 = self.open_file(str(p2))
                    else:
                        ok2 = self.open_file(str(target))
                except Exception as e:
                    self.message(f"open: {e}")
                    return False
                return bool(ok2)
            if target_kind == "action":
                ok = self.run_action(target)
                if ok:
                    self._record_palette_recent("action", target)
                return ok
            self._record_palette_recent("command", target)
            self.enter_prompt("command", prefill=target + " " )
            return True
        if kind == "topic":
            self._push_history("topic", text)
            target = ""
            if prompt.suggestions:
                idx = int(prompt.suggest_index) % len(prompt.suggestions)
                target = str(prompt.suggestions[idx]).strip()
                if prompt.text != prompt.suggest_base and str(prompt.text).strip():
                    target = str(prompt.text).strip()
            if not target:
                q = str(text or "").strip()
                if q:
                    rows = self.apropos_rows(q, limit=1)
                    if rows:
                        target = str(rows[0][0]).strip()
            if not target:
                self.message("topicpick: (none)")
                return False
            return self.exec_command_line("help " + shlex.quote(target))
        if kind == "binding":
            self._push_history("binding", text)
            target = ""
            if prompt.suggestions:
                idx = int(prompt.suggest_index) % len(prompt.suggestions)
                target = str(prompt.suggestions[idx]).strip()
                if prompt.text != prompt.suggest_base and str(prompt.text).strip():
                    target = str(prompt.text).strip()
            if not target:
                q = str(text or "").strip()
                if q:
                    rows = self.binding_apropos_rows(q, limit=1)
                    if rows:
                        target = str(rows[0][0]).strip()
            if not target:
                self.message("bindingpick: (none)")
                return False
            return self.exec_command_line("showkey " + shlex.quote(target))
        if kind == "buffer":
            self._push_history("buffer", text)
            target = ""
            if prompt.suggestions:
                idx = int(prompt.suggest_index) % len(prompt.suggestions)
                target = str(prompt.suggestions[idx]).strip()
                if prompt.text != prompt.suggest_base and str(prompt.text).strip():
                    target = str(prompt.text).strip()
            if not target:
                q = str(text or "").strip()
                if q and q in self.buffers:
                    target = q
                elif q:
                    rows = self.buffer_apropos_rows(q, limit=1)
                    if rows:
                        target = str(rows[0][0]).strip()
            if not target:
                self.message("bufferpick: (none)")
                return False
            if not self.switch_buffer(target):
                self.message(f"bufferpick: no such buffer: {target}")
                return False
            self.message(f"buffer: {target}")
            return True
        if kind == "plugin":
            self._push_history("plugin", text)
            target = ""
            if prompt.suggestions:
                idx = int(prompt.suggest_index) % len(prompt.suggestions)
                target = str(prompt.suggestions[idx]).strip()
                if prompt.text != prompt.suggest_base and str(prompt.text).strip():
                    target = str(prompt.text).strip()
            if not target:
                q = str(text or "").strip()
                if q:
                    rows = self.plugin_apropos_rows(q, limit=1)
                    if rows:
                        target = str(rows[0][0]).strip()
            if not target:
                self.message("pluginpick: (none)")
                return False

            pm = getattr(self, "plugin_manager", None)
            loaded = bool(pm and target in getattr(pm, "plugins", {}))
            cmd = ("plugin reload " if loaded else "plugin info ") + shlex.quote(target)
            return self.exec_command_line(cmd)
        if kind == "recent":
            self._push_history("recent", text)
            target = ""
            if prompt.suggestions:
                idx = int(prompt.suggest_index) % len(prompt.suggestions)
                target = str(prompt.suggestions[idx]).strip()
                if prompt.text != prompt.suggest_base and str(prompt.text).strip():
                    target = str(prompt.text).strip()
            if not target:
                q = str(text or "").strip()
                if q:
                    rows = self.recent_apropos_rows(q, limit=1)
                    if rows:
                        target = str(rows[0][0]).strip()
            if not target:
                self.message("recentpick: (none)")
                return False
            return self.exec_command_line("open " + shlex.quote(target))

        if kind == "doc":
            self._push_history("doc", text)
            target = ""
            if prompt.suggestions:
                idx = int(prompt.suggest_index) % len(prompt.suggestions)
                target = str(prompt.suggestions[idx]).strip()
                if prompt.text != prompt.suggest_base and str(prompt.text).strip():
                    target = str(prompt.text).strip()
            if not target:
                q = str(text or "").strip()
                if q:
                    rows = self.doc_apropos_rows(q, limit=1)
                    if rows:
                        target = str(rows[0][0]).strip()
            if not target:
                self.message("docpick: (none)")
                return False
            if not self.open_help_doc(target):
                self.message(f"docpick: no such doc: {target}")
                return False
            return True

        if kind == "helpnav":
            self._push_history("helpnav", text)

            chosen: list[str] | None = None
            if prompt.suggestion_rows and prompt.suggestions:
                idx = int(prompt.suggest_index) % len(prompt.suggestions)
                row = list(prompt.suggestion_rows[idx][:4]) if idx < len(prompt.suggestion_rows) else []
                chosen = [str(x) for x in row]

                # If the user typed extra text, treat it as a query and re-resolve.
                if prompt.text != prompt.suggest_base and str(prompt.text).strip():
                    q2 = str(prompt.text).strip()
                    rows2 = self.help_nav_rows(q2, limit=1)
                    chosen = [str(x) for x in rows2[0][:4]] if rows2 else None

            if chosen is None:
                q = str(text or "").strip()
                if q:
                    rows = self.help_nav_rows(q, limit=1)
                    chosen = [str(x) for x in rows[0][:4]] if rows else None

            if not chosen or len(chosen) < 2:
                self.message("helpnavpick: (none)")
                return False

            row_kind = str(chosen[1] or "").strip().lower()
            if row_kind == "link":
                target = str(chosen[2] if len(chosen) > 2 else "").strip()
                if not target:
                    self.message("helpnavpick: invalid link")
                    return False
                eb = self.cur()
                return bool(self._follow_help_link(target, base_path=str(eb.buf.path) if eb.buf.path else None))

            if row_kind == "heading":
                linecol = str(chosen[3] if len(chosen) > 3 else "").strip()
                if not linecol:
                    self.message("helpnavpick: bad heading location")
                    return False
                try:
                    if ":" in linecol:
                        a, b = linecol.split(":", 1)
                        line_i = int(a, 10)
                        col_i = int(b, 10)
                    else:
                        line_i = int(linecol, 10)
                        col_i = 1
                except Exception:
                    self.message("helpnavpick: bad heading location")
                    return False

                line0 = max(0, int(line_i) - 1)
                col0 = max(0, int(col_i) - 1)
                eb = self.cur()
                self._normalize_cursor_lists(eb)
                eb.cursors[eb.primary] = eb.buf.clamp(Cursor(line0, col0))
                self.ensure_cursor_visible()
                return True

            self.message("helpnavpick: invalid selection")
            return False

        if kind == "helplink":
            self._push_history("helplink", text)
            target = ""
            if prompt.suggestion_rows and prompt.suggestions:
                idx = int(prompt.suggest_index) % len(prompt.suggestions)
                row = list(prompt.suggestion_rows[idx][:4]) if idx < len(prompt.suggestion_rows) else []
                # row: [label kind target info]
                target = str(row[2] if len(row) > 2 else "").strip()
                if prompt.text != prompt.suggest_base and str(prompt.text).strip():
                    target = str(prompt.text).strip()
            if not target:
                q = str(text or "").strip()
                if q:
                    rows = self.help_link_rows(q, limit=1)
                    if rows:
                        target = str(rows[0][2] if len(rows[0]) > 2 else rows[0][0]).strip()
            if not target:
                self.message("helplinkpick: (none)")
                return False
            eb = self.cur()
            return bool(self._follow_help_link(target, base_path=str(eb.buf.path) if eb.buf.path else None))
        if kind == "helpoutline":
            self._push_history("helpoutline", text)
            linecol = ""
            if prompt.suggestion_rows and prompt.suggestions:
                idx = int(prompt.suggest_index) % len(prompt.suggestions)
                row = list(prompt.suggestion_rows[idx][:4]) if idx < len(prompt.suggestion_rows) else []
                # row: [title kind menu info], where info is "line:col"
                linecol = str(row[3] if len(row) > 3 else "").strip()
                if prompt.text != prompt.suggest_base and str(prompt.text).strip():
                    # If the user typed extra text, treat it as a query and re-resolve.
                    q2 = str(prompt.text).strip()
                    rows2 = self.help_outline_rows(q2, limit=1)
                    if rows2:
                        linecol = str(rows2[0][3] if len(rows2[0]) > 3 else "").strip()
            if not linecol:
                q = str(text or "").strip()
                if q:
                    rows = self.help_outline_rows(q, limit=1)
                    if rows:
                        linecol = str(rows[0][3] if len(rows[0]) > 3 else "").strip()
            if not linecol:
                self.message("helpoutlinepick: (none)")
                return False
            # Parse 1-based "line:col"
            try:
                if ":" in linecol:
                    a, b = linecol.split(":", 1)
                    line_i = int(a, 10)
                    col_i = int(b, 10)
                else:
                    line_i = int(linecol, 10)
                    col_i = 1
            except Exception:
                self.message("helpoutlinepick: bad heading location")
                return False

            line0 = max(0, int(line_i) - 1)
            col0 = max(0, int(col_i) - 1)
            eb = self.cur()
            self._normalize_cursor_lists(eb)
            eb.cursors[eb.primary] = eb.buf.clamp(Cursor(line0, col0))
            self.ensure_cursor_visible()
            return True



        if kind == "mark":
            self._push_history("mark", text)
            target = ""
            if prompt.suggestions:
                idx = int(prompt.suggest_index) % len(prompt.suggestions)
                target = str(prompt.suggestions[idx]).strip()
                if prompt.text != prompt.suggest_base and str(prompt.text).strip():
                    target = str(prompt.text).strip()
            if not target:
                q = str(text or "").strip()
                if q and q in self.marks:
                    target = q
                elif q:
                    rows = self.mark_apropos_rows(q, limit=1)
                    if rows:
                        target = str(rows[0][0]).strip()
            if not target:
                self.message("markpick: (none)")
                return False
            if not self.mark_jump(target):
                self.message(f"markpick: no such mark: {target}")
                return False
            self.message(f"markjump: {target}")
            return True
        if kind == "jump":
            self._push_history("jump", text)
            target = ""
            if prompt.suggestions:
                idx = int(prompt.suggest_index) % len(prompt.suggestions)
                target = str(prompt.suggestions[idx]).strip()
                if prompt.text != prompt.suggest_base and str(prompt.text).strip():
                    target = str(prompt.text).strip()
            if not target:
                q = str(text or "").strip()
                if q:
                    rows = self.jump_apropos_rows(q, limit=1)
                    if rows:
                        target = str(rows[0][0]).strip()
            if not target:
                self.message("jumppick: (none)")
                return False
            m = re.match(r"\s*(\d+)", str(target))
            if not m:
                self.message("jumppick: invalid selection")
                return False
            n = int(m.group(1), 10)
            if not self.jump_to_index(n - 1):
                self.message(f"jumppick: out of range: {n}")
                return False
            eb = self.cur()
            self._normalize_cursor_lists(eb)
            c = eb.cursors[eb.primary]
            self.message(f"jump: {int(c.line) + 1}:{int(c.col) + 1}")
            return True
        return False

    def prompt_history_prev(self) -> bool:
        if self.prompt is None:
            return False
        h = self.history.get(self.prompt.kind, [])
        if not h:
            return False
        if self.prompt.hist_index is None:
            self.prompt.hist_saved = self.prompt.text
            self.prompt.hist_index = len(h)
        if self.prompt.hist_index <= 0:
            return False
        self.prompt.hist_index -= 1
        self.set_prompt_text(h[self.prompt.hist_index])
        return True

    def prompt_history_next(self) -> bool:
        if self.prompt is None:
            return False
        h = self.history.get(self.prompt.kind, [])
        if self.prompt.hist_index is None:
            return False
        if self.prompt.hist_index >= len(h) - 1:
            # restore saved
            saved = self.prompt.hist_saved
            self.prompt.hist_index = None
            self.prompt.hist_saved = ""
            self.set_prompt_text(saved)
            return True
        self.prompt.hist_index += 1
        self.set_prompt_text(h[self.prompt.hist_index])
        return True


    # ----- prompt completion (command bar) -----
    def prompt_suggestions(self) -> list[str]:
        """Return current prompt suggestions as a new list."""
        if self.prompt is None:
            return []
        return list(self.prompt.suggestions)

    def prompt_suggestion_rows(self) -> list[list[str]]:
        """Return current prompt suggestion rows as [[insert kind menu info] ...]."""
        if self.prompt is None:
            return []
        out: list[list[str]] = []
        for row in self.prompt.suggestion_rows:
            vals = list(row[:4])
            while len(vals) < 4:
                vals.append("")
            out.append([str(vals[0]), str(vals[1]), str(vals[2]), str(vals[3])])
        return out

    def clear_prompt_suggestions(self) -> bool:
        """Clear the active prompt suggestion session."""
        if self.prompt is None or not self.prompt.suggestions:
            return False
        self.prompt.clear_suggestions()
        return True

    def prompt_suggest_move(self, delta: int) -> bool:
        """Move picker selection within the active prompt's suggestion list.

        This is intended for *picker-style* prompts (buffer/doc/help pickers,
        palette, etc.) where Up/Down should move the highlighted selection
        without mutating the user's typed query.

        Command/find prompts keep their traditional Up/Down semantics (history
        navigation), so this returns False for those prompt kinds.

        Wrap policy:
        - when option `prompt.wrap` is true (default), selection wraps at ends
        - when false, selection clamps to [0, n-1]
        """

        if self.prompt is None:
            return False
        if self.prompt.kind in ("command", "find"):
            return False
        if not self.prompt.suggestion_rows:
            return False
        n = len(self.prompt.suggestion_rows)
        if n <= 0:
            return False
        i = int(self.prompt.suggest_index)
        wrap = True
        try:
            wrap = bool(self.options.get("prompt.wrap"))
        except Exception:
            wrap = True
        if wrap:
            self.prompt.suggest_index = (i + int(delta)) % n
        else:
            self.prompt.suggest_index = max(0, min(n - 1, i + int(delta)))
        return True

    def prompt_suggest_page(self, pages: int) -> bool:
        """Move picker selection by a fixed page step.

        This is bound to PageUp/PageDown in prompt mode for picker-style
        prompts. The step size is controlled by option `prompt.page` (default
        8), matching the typical number of suggestion rows visible in the
        minimal TUI.

        Returns False for command/find prompts so those keys can fall back to
        history navigation.
        """

        if self.prompt is None:
            return False
        if self.prompt.kind in ("command", "find"):
            return False
        step = 8
        try:
            raw = int(self.options.get("prompt.page"))
            if raw > 0:
                step = raw
        except Exception:
            step = 8
        return bool(self.prompt_suggest_move(int(pages) * int(step)))

    def prompt_suggest_first(self) -> bool:
        """Jump picker selection to the first suggestion row (index 0).

        Returns False for command/find prompts.
        """

        if self.prompt is None:
            return False
        if self.prompt.kind in ("command", "find"):
            return False
        if not self.prompt.suggestion_rows:
            return False
        self.prompt.suggest_index = 0
        return True


    def prompt_suggest_last(self) -> bool:
        """Jump picker selection to the last suggestion row (index n-1).

        Returns False for command/find prompts.
        """

        if self.prompt is None:
            return False
        if self.prompt.kind in ("command", "find"):
            return False
        if not self.prompt.suggestion_rows:
            return False
        self.prompt.suggest_index = max(0, len(self.prompt.suggestion_rows) - 1)
        return True

    def prompt_row_section_label(self, row: list[str], *, prompt_kind: str | None = None) -> str:
        """Best-effort section label for a prompt suggestion row.

        This is used for:
        - rendering section headers in the minimal TUI suggestion list
        - section-jump navigation in picker-style prompts

        Row shape is generally: [insert kind menu info].
        """

        kind = str(prompt_kind or (self.prompt.kind if self.prompt is not None else "") or "")
        vals = [str(x) for x in list(row[:4])]
        while len(vals) < 4:
            vals.append("")

        try:
            if kind == "palette":
                return str(self._command_palette_section_label(vals))
            if kind == "topic":
                _single, plural = self._topic_section_names(str(vals[1] if len(vals) > 1 else ""))
                return str(plural)
            if kind == "recent":
                path = str(vals[0] if vals else "")
                root = self._project_root_for_path(path)
                if root:
                    return str(root)
                try:
                    from pathlib import Path

                    return str(Path(path).parent)
                except Exception:
                    return "(unknown)"
            if kind == "buffer":
                return str(self._buffer_section_label(vals))
            if kind == "plugin":
                return str(self._plugin_section_label(vals))
            if kind == "doc":
                return "Docs"
            if kind == "helplink":
                return str(self.helplink_section_label(vals))
            if kind == "helpoutline":
                return "Headings"
            if kind == "helpnav":
                k2 = str(vals[1] if len(vals) > 1 else "")
                if k2 == "heading":
                    return "Headings"
                if k2 == "link":
                    return str(self._helplink_kind_label(vals))
                return "Items"
        except Exception:
            pass

        return kind.title() if kind else "Items"

    def _prompt_section_starts(self) -> list[int]:
        """Return indices of the first row of each section in the suggestion list."""

        if self.prompt is None or not self.prompt.suggestion_rows:
            return []
        out: list[int] = []
        last = None
        for i, row in enumerate(self.prompt.suggestion_rows):
            lbl = self.prompt_row_section_label([str(x) for x in list(row[:4])])
            if lbl != last:
                out.append(i)
                last = lbl
        return out

    def prompt_suggest_next_section(self) -> bool:
        """Jump picker selection to the next section in the suggestion list."""

        if self.prompt is None:
            return False
        if self.prompt.kind in ("command", "find"):
            return False
        if not self.prompt.suggestion_rows:
            return False
        starts = self._prompt_section_starts()
        if not starts:
            return False
        i = int(self.prompt.suggest_index)
        # Find current section start index.
        cur_s = 0
        for si, st in enumerate(starts):
            if st <= i:
                cur_s = si
            else:
                break
        wrap = True
        try:
            wrap = bool(self.options.get("prompt.wrap"))
        except Exception:
            wrap = True
        if cur_s + 1 < len(starts):
            self.prompt.suggest_index = int(starts[cur_s + 1])
            return True
        if wrap:
            self.prompt.suggest_index = int(starts[0])
            return True
        self.prompt.suggest_index = int(starts[-1])
        return True

    def prompt_suggest_prev_section(self) -> bool:
        """Jump picker selection to the start of the current/previous section."""

        if self.prompt is None:
            return False
        if self.prompt.kind in ("command", "find"):
            return False
        if not self.prompt.suggestion_rows:
            return False
        starts = self._prompt_section_starts()
        if not starts:
            return False
        i = int(self.prompt.suggest_index)
        cur_s = 0
        for si, st in enumerate(starts):
            if st <= i:
                cur_s = si
            else:
                break
        cur_start = int(starts[cur_s])
        # If we're inside the section, jump to its start first.
        if i > cur_start:
            self.prompt.suggest_index = cur_start
            return True
        wrap = True
        try:
            wrap = bool(self.options.get("prompt.wrap"))
        except Exception:
            wrap = True
        if cur_s > 0:
            self.prompt.suggest_index = int(starts[cur_s - 1])
            return True
        if wrap:
            self.prompt.suggest_index = int(starts[-1])
            return True
        self.prompt.suggest_index = int(starts[0])
        return True

    def prompt_copy_selected(self) -> bool:
        """Copy the currently selected prompt row to the clipboard.

        Heuristic:
        - for link rows (kind == 'link'), copy the link target (col 2)
        - otherwise copy the displayed name/insert text (col 0)

        This is useful in docs pickers (copy link target without moving the
        buffer cursor) and is generic enough to be handy in other pickers.
        """

        row = self.prompt_current_row()
        if not row:
            return False
        name, kind, target, _info = [str(x or "") for x in row[:4]]
        out = ""
        if str(kind).strip().lower() == "link" and str(target).strip():
            out = str(target).strip()
        else:
            out = str(name).strip()
        if not out:
            return False
        self.set_clipboard_items([out], kind="items")
        self.message(f"copied\n{out}")
        return True

    def _path_completion_candidates(
        self,
        unquoted_prefix: str,
        *,
        at_eol: bool,
        quote: str | None = None,
        close_dirs: bool = False,
    ) -> list[str]:
        """Return filesystem path completion candidates for the command prompt.

        This is intentionally simple and portable:

        - String-based suggestions (no UI coupling).
        - Hidden files are only suggested when the user starts the name with '.'.
        - Directories get a trailing path separator so you can keep completing inside.
        - Files at end-of-line get a trailing space (dirs do not).

        Quoting policy (shell-ish, but tiny):

        - If the user already started a quote token (" or '), we complete inside
          that quote style.
        - If the user did *not* start a quote token, but the completion contains
          whitespace or a double quote, we auto-wrap the path in double quotes and
          escape internal backslashes and `"`.
        - For directory completions where quoting is active, we keep the closing
          quote *open* (unless `close_dirs=True`) so users can keep tabbing into
          the path.

        Note: This consults the current process working directory via pathlib/os.
        If a host embedding needs tighter sandboxing, it should gate filesystem
        access before exposing editor commands that rely on it.
        """
        import os
        from pathlib import Path

        typed = str(unquoted_prefix or "")
        # Split into (dirpart, namepart) preserving a trailing separator for dirs.
        dirpart, namepart = os.path.split(typed)
        if dirpart != "" and not dirpart.endswith(os.sep):
            dirpart = dirpart + os.sep

        # Special-case a bare '~' so users can type `open ~` then Tab.
        if typed == "~":
            dirpart, namepart = "~" + os.sep, ""

        # Resolve search directory for listing (expand ~, keep user-typed text for display).
        search_dir = Path(dirpart or ".").expanduser()
        try:
            if not search_dir.exists() or not search_dir.is_dir():
                return []
            entries = list(search_dir.iterdir())
        except OSError:
            return []

        show_hidden = namepart.startswith(".")
        max_items = 60 if typed == "" else 200

        def _escape_double(s: str) -> str:
            return s.replace("\\", "\\\\").replace('"', '\\"')

        def _render(path: str, *, is_dir: bool) -> str:
            # Decide whether we should quote even if the user didn't.
            needs_quote = any(ch.isspace() for ch in path) or ('"' in path)
            q = quote
            if q is None and needs_quote:
                q = '"'

            trail = " " if (at_eol and (not is_dir)) else ""

            if q is None:
                return path + trail

            body = path
            # Only escape for double quotes (posix-ish).
            if q == '"':
                body = _escape_double(body)

            # Keep quotes open for dirs so users can keep completing.
            if is_dir:
                return (q + body + q) if close_dirs else (q + body)
            return q + body + q + trail

        cands: list[tuple[int, str]] = []  # (kind, candidate) where kind=0 dir, 1 file
        for child in entries:
            nm = child.name
            if not show_hidden and nm.startswith("."):
                continue
            if not nm.startswith(namepart):
                continue
            try:
                is_dir = child.is_dir()
            except OSError:
                is_dir = False
            suffix = os.sep if is_dir else ""
            cand_path = f"{dirpart}{nm}{suffix}"
            cands.append((0 if is_dir else 1, _render(cand_path, is_dir=is_dir)))
            if len(cands) >= max_items:
                break

        # Sort dirs first, then lexicographically (case-sensitive, like many shells).
        cands.sort(key=lambda t: (t[0], t[1]))
        return [c for _k, c in cands]


    def _mx_prompt_completion_candidates(
        self,
        *,
        cmd: str,
        tok_i: int,
        prefix: str,
        toks: list[str],
    ) -> tuple[list[str], list[list[str]], int]:
        """Ask embedded micromax for extra prompt completion candidates.

        Lookup order:
          1) `ed.complete.<cmd>`
          2) `ed.complete`

        Supported completion-word contracts (best-effort):

            ( cmd tok_i prefix toks -- cands mode )
            ( cmd tok_i prefix toks -- cands rows mode )

        - cands: list of strings to insert into the prompt
        - rows: optional list of `[insert kind menu info]` annotations
        - mode: 0 = no candidates, 1 = add, 2 = replace

        This stays intentionally small, but the optional row contract lets
        plugins participate in the same metadata surface as built-in
        completions without forcing a UI choice.

        Errors are caught and surfaced as editor messages. The VM stack is
        restored after the call.
        """

        def _normalize_mode(value: object) -> int:
            if isinstance(value, bool):
                return 1 if value else 0
            if isinstance(value, int):
                return int(value)
            return 1 if value else 0

        def _normalize_rows(value: object, cands: list[str]) -> list[list[str]]:
            out: list[list[str]] = []
            if not isinstance(value, list):
                return out
            for i, item in enumerate(value):
                if i >= len(cands):
                    break
                if isinstance(item, list):
                    row = [str(x) for x in item[:4]]
                else:
                    row = [str(item)]
                while len(row) < 4:
                    row.append("")
                row[0] = cands[i]
                out.append(row[:4])
            return out

        vm = self.vm
        cmd = str(cmd)
        name_candidates = [f"ed.complete.{cmd}", "ed.complete"]

        for wname in name_candidates:
            if vm.find_word(wname) is None:
                continue

            depth = len(vm.stack)
            try:
                vm.stack.extend([cmd, int(tok_i), str(prefix), list(toks)])
                vm.eval(wname, filename="<editor-complete>")

                produced = vm.stack[depth:]
                if len(produced) < 2:
                    return ([], [], 0)

                cands = produced[-2]
                rows_obj: object = []
                mode = produced[-1]
                if len(produced) >= 3 and isinstance(produced[-2], list) and isinstance(produced[-3], list):
                    cands = produced[-3]
                    rows_obj = produced[-2]
                    mode = produced[-1]

                out: list[str] = []
                if isinstance(cands, list):
                    for x in cands:
                        out.append(str(x))

                # Sanity caps (avoid pathological suggestion lists).
                if len(out) > 400:
                    out = out[:400]

                rows = _normalize_rows(rows_obj, out)
                return (out, rows, _normalize_mode(mode))
            except Exception as e:
                try:
                    from micromax.vm import MicromaxError

                    if isinstance(e, MicromaxError):
                        self.message(vm.format_error(e))
                    else:
                        self.message(f"mx completion error: {e}")
                except Exception:
                    self.message(f"mx completion error: {e}")
                return ([], [], 0)
            finally:
                del vm.stack[depth:]

        return ([], [], 0)


    def _overlay_suggestion_rows(
        self,
        base_rows: list[list[str]],
        candidates: list[str],
        extra_candidates: list[str],
        extra_rows: list[list[str]],
    ) -> list[list[str]]:
        """Overlay plugin-provided suggestion rows onto inferred row metadata."""

        if not base_rows or not extra_candidates or not extra_rows:
            return base_rows

        out = [list(r[:4]) + [""] * max(0, 4 - len(r[:4])) for r in base_rows]
        index_by_insert: dict[str, int] = {}
        for i, cand in enumerate(candidates):
            index_by_insert.setdefault(str(cand), i)

        for i, cand in enumerate(extra_candidates):
            if i >= len(extra_rows):
                continue
            dst_i = index_by_insert.get(str(cand))
            if dst_i is None or dst_i >= len(out):
                continue
            row = [str(x) for x in list(extra_rows[i])[:4]]
            while len(row) < 4:
                row.append("")
            row[0] = str(candidates[dst_i])
            for j in range(1, 4):
                if row[j] != "":
                    out[dst_i][j] = row[j]
        return [r[:4] for r in out]


    def prompt_complete(self, *, direction: int = 1) -> bool:
        """Autocomplete / cycle suggestions in the active prompt.

        Intended to be bound to Tab (forward) and Shift-Tab (backward).
        Command prompts use token-aware completion; topic prompts use ranked
        command/action/word topic rows; binding prompts use ranked current
        binding rows.
        """
        if self.prompt is None or self.prompt.kind not in (
            "command",
            "palette",
            "topic",
            "binding",
            "buffer",
            "mark",
            "jump",
            "plugin",
            "recent",
            "doc",
            "helplink",
            "helpoutline",
            "helpnav",
        ):
            return False

        # If a suggestion session is active, cycle through candidates.
        if self.prompt.suggestions:
            step = 1 if int(direction) >= 0 else -1
            if self.prompt.text == self.prompt.suggest_base:
                idx = 0 if step > 0 else (len(self.prompt.suggestions) - 1)
            else:
                idx = self.prompt.suggest_index + step
            self.prompt.apply_suggestion(idx)
            return True

        if self.prompt.kind == "topic":
            ok = self._refresh_topic_prompt_suggestions()
            if ok:
                preview = ", ".join(str(c) for c in self.prompt.suggestions[:6])
                suffix = " ..." if len(self.prompt.suggestions) > 6 else ""
                self.message("topics: " + preview + suffix)
            return ok
        if self.prompt.kind == "binding":
            ok = self._refresh_binding_prompt_suggestions()
            if ok:
                preview = ", ".join(str(c) for c in self.prompt.suggestions[:6])
                suffix = " ..." if len(self.prompt.suggestions) > 6 else ""
                self.message("bindings: " + preview + suffix)
            return ok

        # Picker-style prompts: ensure a suggestion session exists, then cycle.
        if self.prompt.kind == "palette":
            return bool(self._refresh_palette_prompt_suggestions())
        if self.prompt.kind == "buffer":
            return bool(self._refresh_buffer_prompt_suggestions())
        if self.prompt.kind == "mark":
            return bool(self._refresh_mark_prompt_suggestions())
        if self.prompt.kind == "jump":
            return bool(self._refresh_jump_prompt_suggestions())
        if self.prompt.kind == "plugin":
            return bool(self._refresh_plugin_prompt_suggestions())
        if self.prompt.kind == "recent":
            return bool(self._refresh_recent_prompt_suggestions())
        if self.prompt.kind == "doc":
            return bool(self._refresh_doc_prompt_suggestions())

        text = self.prompt.text
        cur = self.prompt.cursor

        def scan_tokens(s: str) -> list[tuple[str, int, int]]:
            """Return [(token, start, end), ...] using forgiving shell-ish rules.

            This is for completion only (not command execution). It is quote-aware
            (whitespace inside quotes stays inside the token) and handles a minimal
            subset of escapes so completions like `"a\\\"b"` stay one token.

            We don't attempt to fully emulate `/bin/sh` here; execution uses
            `shlex.split` in `parse_cmdline()`.
            """
            out: list[tuple[str, int, int]] = []
            start: int | None = None
            in_single = False
            in_double = False

            i = 0
            while i < len(s):
                ch = s[i]

                # Minimal escaping: outside single quotes, backslash escapes the
                # next character so it cannot terminate a quote.
                if ch == "\\" and not in_single:
                    if start is None:
                        start = i
                    i = i + 2 if (i + 1) < len(s) else i + 1
                    continue

                if ch == "'" and not in_double:
                    in_single = not in_single
                    if start is None:
                        start = i
                    i += 1
                    continue
                if ch == '"' and not in_single:
                    in_double = not in_double
                    if start is None:
                        start = i
                    i += 1
                    continue

                if (not in_single) and (not in_double) and ch.isspace():
                    if start is not None:
                        out.append((s[start:i], start, i))
                        start = None
                    i += 1
                    continue

                if start is None and not ch.isspace():
                    start = i

                i += 1

            if start is not None:
                out.append((s[start:len(s)], start, len(s)))
            return out

        spans = scan_tokens(text)
        toks = [t for t, _s, _e in spans]

        # Find the token under the cursor, or treat cursor as a new token.
        tok_i: int | None = None
        tok_start = tok_end = cur
        tok = ""
        for i, (t, s, e) in enumerate(spans):
            if s <= cur <= e:
                tok_i = i
                tok_start, tok_end = s, e
                tok = t
                break

        if tok_i is None:
            # cursor in whitespace
            tok_i = 0
            for _t, _s, e in spans:
                if e < cur:
                    tok_i += 1
            tok_start = tok_end = cur
            tok = ""

        # Quote-aware completion: if the current token begins with a quote, we
        # complete *within* it. For convenience we normalize away a trailing
        # matching quote when determining the prefix.
        quote: str | None = None
        quote_closed = False
        tok_inner = tok
        tok_norm = tok
        if tok.startswith(("'", '"')):
            quote = tok[0]
            rest = tok[1:]
            if rest.endswith(quote):
                quote_closed = True
                rest = rest[:-1]
            tok_inner = rest
            tok_norm = quote + rest

        cmd = toks[0] if toks else ""
        prefix = tok_norm

        # Avoid dumping huge suggestion lists on empty prefix.
        if prefix == "" and tok_i == 0:
            return False

        candidates, fuzzy_candidates = self._prompt_command_token_candidates(
            cmd=cmd,
            toks=toks,
            tok_i=tok_i,
            prefix=prefix,
            at_eol=(tok_end >= len(text)),
        )
        path_mode = False

        if (not candidates) and tok_i == 1 and cmd in ("open", "save", "cd"):
            # Filesystem completion for micro-style commands remains explicit
            # prefix completion; fuzzy path search is a separate future feature.
            candidates = self._path_completion_candidates(
                tok_inner,
                at_eol=(tok_end >= len(text)),
                quote=quote,
                close_dirs=quote_closed,
            )
            path_mode = bool(candidates)

        # Allow micromax plugins to extend/override completion.
        mx_cands, mx_rows, mx_mode = self._mx_prompt_completion_candidates(cmd=cmd, tok_i=tok_i, prefix=prefix, toks=toks)
        if mx_mode == 2:
            candidates = list(mx_cands)
            fuzzy_candidates = False
            path_mode = False
        elif mx_mode == 1 and mx_cands:
            if not candidates:
                candidates = list(mx_cands)
            else:
                for c in mx_cands:
                    if c not in candidates:
                        candidates.append(c)

        if not candidates:
            return False

        rows = self._prompt_suggestion_rows(
            cmd=cmd,
            toks=toks,
            tok_i=tok_i,
            candidates=candidates,
            path_mode=path_mode,
        )
        rows = self._overlay_suggestion_rows(rows, candidates, mx_cands, mx_rows)

        # Strip the added space for common-prefix calculation and headless
        # message/debug output.
        raw = [c[:-1] if c.endswith(" ") else c for c in candidates]

        import os as _os

        common = _os.path.commonprefix(raw) if (raw and (not fuzzy_candidates)) else ""

        if len(candidates) == 1:
            c = candidates[0]
            new = text[:tok_start] + c + text[tok_end:]
            self.set_prompt_text(new)
            self.prompt.set_cursor(tok_start + len(c))
            if fuzzy_candidates:
                self.message("fuzzy: " + raw[0])
            return True

        if common and len(common) > len(prefix):
            def _prefer_exact_common_candidate() -> bool:
                """Heuristic: prefer the exact candidate over starting a session.

                We only do this when the other matches are clearly "picker"
                variants.

                Rationale:
                - `he` should complete to `help ` even if `helppick` exists.
                - `tog` should *not* complete to `toggle ` when `togglelocal`
                  exists; the first Tab should expand to the common prefix
                  (`toggle`) and start a session.
                - `bind ... command:sh` completion should start a session rather
                  than snapping to the exact `command:show ` candidate.
                """

                if common not in raw:
                    return False
                others = [r for r in raw if r != common]
                if not others:
                    return False

                # Special-case `help` (and derived forms like
                # `command-edit:help`): it's almost always what the user meant
                # when typing `he`, even if helper commands like `helppick`,
                # `helpback`, and `helpfollow` exist.
                if common.endswith("help"):
                    return True

                def _is_pick_variant(r: str) -> bool:
                    if not r.startswith(common):
                        return False
                    suf = r[len(common) :]
                    return suf.startswith("pick") or suf.startswith("-pick") or suf.startswith("_pick")

                return all(_is_pick_variant(r) for r in others)

            if _prefer_exact_common_candidate():
                # If the common prefix itself is a full candidate, prefer it.
                #
                # Example: completing `he` with candidates `help` and
                # `helppick`. In that case we want the first Tab to land on
                # `help ` (a full command), not just insert `help` and require
                # another keypress.
                for cand in candidates:
                    rc = cand[:-1] if cand.endswith(" ") else cand
                    if rc == common:
                        c = cand
                        new = text[:tok_start] + c + text[tok_end:]
                        self.set_prompt_text(new)
                        self.prompt.set_cursor(tok_start + len(c))
                        if fuzzy_candidates:
                            self.message("fuzzy: " + common)
                        return True
            new = text[:tok_start] + common + text[tok_end:]
            self.set_prompt_text(new)
            self.prompt.set_cursor(tok_start + len(common))
            self.prompt.begin_suggestions(candidates, start=tok_start, end=(tok_start + len(common)), rows=rows)
            self.message("matches: " + ", ".join(raw))
            return True

        self.prompt.begin_suggestions(candidates, start=tok_start, end=tok_end, rows=rows)
        self.message(("fuzzy matches: " if fuzzy_candidates else "matches: ") + ", ".join(raw))
        return True

    # ----- command bar -----
    def exec_command_line(self, cmdline: str) -> bool:
        """Execute a command-bar line.

        If macro recording is enabled, successful command lines are recorded as
        macro steps *except* for macro-management commands themselves.
        """

        self._push_history("command", cmdline)
        cl = parse_cmdline(cmdline)
        if cl is None:
            return False

        if cl.name not in {"quit", "quit!"}:
            self._quit_armed = False


        if cl.name not in {"close", "close!"}:
            self._close_armed = False
            self._close_armed_name = ""

        if self.macro_recording and not self._macro_playing and cl.name != "macro":
            self._macro_buffer.append(MacroStep(kind="command", name="command", payload={"cmdline": cmdline}))

        return self.command_dispatcher.exec(self, cl)

    # ----- search -----
    def _sync_search_options(self) -> None:
        eb = self.cur()
        ignorecase = bool(self.options.get("ignorecase", local=eb.local_options))
        self.search.case_sensitive = not ignorecase

    def find(self, query: str, *, literal: bool | None = None) -> bool:
        self._sync_search_options()
        self.search.query = query
        if literal is not None:
            self.search.literal = bool(literal)

        eb = self.cur()
        self._normalize_cursor_lists(eb)
        start = eb.cursors[eb.primary]
        m = find_next(eb.buf, self.search, start=start)
        if m is None:
            self.message("not found")
            return False
        eb.cursors[eb.primary] = m
        self.search.last_match = m
        return True

    def find_next(self) -> bool:
        if not self.search.query:
            return False
        self._sync_search_options()
        eb = self.cur()
        self._normalize_cursor_lists(eb)
        start = eb.cursors[eb.primary]
        start2 = Cursor(start.line, start.col + 1)
        m = find_next(eb.buf, self.search, start=start2)
        if m is None:
            return False
        eb.cursors[eb.primary] = m
        self.search.last_match = m
        return True

    def find_prev(self) -> bool:
        if not self.search.query:
            return False
        self._sync_search_options()
        eb = self.cur()
        self._normalize_cursor_lists(eb)
        start = eb.cursors[eb.primary]
        m = find_prev(eb.buf, self.search, start=start)
        if m is None:
            return False
        eb.cursors[eb.primary] = m
        self.search.last_match = m
        return True

    # ----- query replace (interactive) -----
    def begin_query_replace(self, search: str, value: str, *, literal: bool = False) -> bool:
        """Start an interactive query-replace session.

        This is deliberately small and headless:
        - current match is selected
        - y/Enter replaces, n skips, a replaces all remaining, l replaces and quits, q/Esc quits
        """

        # Protected buffers (help/docs) should reject edits.
        try:
            if hasattr(self, "is_protected_buffer") and self.is_protected_buffer():
                self.message("qreplace: read-only buffer")
                return False
        except Exception:
            pass

        eb = self.cur()
        self._normalize_cursor_lists(eb)
        p = eb.primary

        sess = QueryReplaceSession(
            buffer_name=str(eb.name),
            search=str(search),
            value=str(value),
            literal=bool(literal),
            next_start=Cursor(eb.cursors[p].line, eb.cursors[p].col),
        )

        # Match semantics follow the editor's ignorecase option (like find/FindNext).
        ignorecase = bool(self.options.get("ignorecase", local=eb.local_options))
        sess.case_sensitive = not ignorecase

        if not sess.literal:
            try:
                flags_re = re.IGNORECASE if not sess.case_sensitive else 0
                sess.regex = re.compile(sess.search, flags_re)
            except re.error as e:
                self.message(f"qreplace: invalid regex: {e}")
                return False
            sess.repl_py = convert_replacement_template(sess.value)
        sess.before = self._snapshot_buffer_state(eb)

        # Best-effort count of matches remaining from the starting cursor.
        try:
            text0 = str(sess.before[0]) if sess.before is not None else eb.buf.get_text()
            start_i0 = cursor_to_index(eb.buf, sess.next_start)
            if sess.literal:
                if sess.search:
                    hay = text0 if sess.case_sensitive else text0.lower()
                    needle = sess.search if sess.case_sensitive else sess.search.lower()
                    pos = start_i0
                    total = 0
                    while True:
                        i = hay.find(needle, pos)
                        if i < 0:
                            break
                        total += 1
                        pos = i + max(1, len(needle))
                    sess.total = total
            else:
                if sess.regex is not None:
                    sess.total = sum(1 for _m in sess.regex.finditer(text0, pos=start_i0))
        except Exception:
            sess.total = 0

        self.qreplace = sess

        # Enter a capture keymode so global bindings can't fire accidentally.
        self.push_key_mode("qreplace", capture=True)
        return self._qreplace_select_next()

    def _qreplace_clear_primary_selection(self) -> None:
        eb = self.cur()
        self._normalize_cursor_lists(eb)
        eb.sel_anchors[eb.primary] = None

    def _qreplace_select_next(self) -> bool:
        sess = self.qreplace
        if sess is None:
            return False

        eb = self.cur()
        if str(eb.name) != str(sess.buffer_name):
            # If the user switched buffers mid-session, bail safely.
            return self._qreplace_finish(canceled=True)

        self._normalize_cursor_lists(eb)
        p = eb.primary

        text = eb.buf.get_text()
        start_i = cursor_to_index(eb.buf, sess.next_start)

        # Find next match.
        if sess.literal:
            if sess.case_sensitive:
                i = text.find(sess.search, start_i)
            else:
                i = text.lower().find(sess.search.lower(), start_i)
            if i < 0:
                if sess.examined == 0 and sess.replaced == 0:
                    # Nothing matched at all; treat as a normal "not found".
                    self.key_mode_stack = [km for km in self.key_mode_stack if km.name != "qreplace"]
                    self.qreplace = None
                    self.message("qreplace: not found")
                    return False
                return self._qreplace_finish(canceled=False)
            j = i + len(sess.search)
            sess.match_start = index_to_cursor(eb.buf, i)
            sess.match_end = index_to_cursor(eb.buf, j)
            sess.match_repl = sess.value
        else:
            assert sess.regex is not None
            m = sess.regex.search(text, pos=start_i)
            if m is None:
                if sess.examined == 0 and sess.replaced == 0:
                    self.key_mode_stack = [km for km in self.key_mode_stack if km.name != "qreplace"]
                    self.qreplace = None
                    self.message("qreplace: not found")
                    return False
                return self._qreplace_finish(canceled=False)
            i, j = m.span()
            sess.match_start = index_to_cursor(eb.buf, i)
            sess.match_end = index_to_cursor(eb.buf, j)
            try:
                sess.match_repl = m.expand(sess.repl_py)
            except Exception:
                sess.match_repl = sess.value

        sess.examined += 1

        # Select the match so it is visible in the TUI.
        eb.sel_anchors[p] = Cursor(sess.match_start.line, sess.match_start.col)  # type: ignore[union-attr]
        eb.cursors[p] = Cursor(sess.match_end.line, sess.match_end.col)  # type: ignore[union-attr]

        extra = f"match {sess.examined}"
        if sess.total:
            extra += f"/{sess.total}"

        self.message(
            f"qreplace: y/Enter replace, n skip, a all, l last, q/Esc quit  ({sess.replaced} replaced; {extra})"
        )
        return True

    def _qreplace_apply_current(self) -> bool:
        sess = self.qreplace
        if sess is None or sess.match_start is None or sess.match_end is None:
            return False
        eb = self.cur()
        if str(eb.name) != str(sess.buffer_name):
            return self._qreplace_finish(canceled=True)

        self._normalize_cursor_lists(eb)
        p = eb.primary

        cur = eb.buf.replace_range(sess.match_start, sess.match_end, sess.match_repl)
        eb.cursors[p] = cur
        eb.sel_anchors[p] = None
        sess.replaced += 1
        sess.next_start = Cursor(cur.line, cur.col)
        return True

    def qreplace_yes(self) -> bool:
        if not self._qreplace_apply_current():
            return False
        return self._qreplace_select_next()

    def qreplace_no(self) -> bool:
        sess = self.qreplace
        if sess is None or sess.match_end is None:
            return False
        # Skip: continue search after the end of the current match.
        sess.next_start = Cursor(sess.match_end.line, sess.match_end.col)
        self._qreplace_clear_primary_selection()
        return self._qreplace_select_next()

    def qreplace_last(self) -> bool:
        if not self._qreplace_apply_current():
            return False
        return self._qreplace_finish(canceled=False)

    def qreplace_all(self) -> bool:
        if self.qreplace is None:
            return False
        # Replace current + all remaining matches without pausing.
        while self.qreplace is not None:
            sess = self.qreplace
            if sess is None or sess.match_start is None or sess.match_end is None:
                break
            self._qreplace_apply_current()
            if self.qreplace is None:
                break
            self._qreplace_select_next()
        return True

    def qreplace_quit(self) -> bool:
        return self._qreplace_finish(canceled=True)

    def _qreplace_finish(self, *, canceled: bool) -> bool:
        sess = self.qreplace
        if sess is None:
            return False

        eb = self.cur()
        if str(eb.name) == str(sess.buffer_name):
            self._normalize_cursor_lists(eb)
            eb.sel_anchors[eb.primary] = None

            after = self._snapshot_buffer_state(eb)
            if sess.before is not None and sess.before != after and sess.replaced > 0:
                self._record_undo_snapshot(eb, sess.before, after, "qreplace")

        # Drop the capture mode.
        self.key_mode_stack = [km for km in self.key_mode_stack if km.name != "qreplace"]
        self.qreplace = None

        if canceled:
            self.message(f"qreplace: canceled ({sess.replaced} replaced)")
        else:
            self.message(f"qreplace: done ({sess.replaced} replaced)")
        return True

    # ----- runtime reload (plugins, bindings, etc.) -----
    def reload_runtime(self) -> bool:
        self.keymap = Keymap()
        self._install_builtin_keymode_bindings()
        if not self.plugin_manager:
            self.message("reloaded (no plugins)")
            return True
        names = list(self.plugin_manager.plugins.keys())
        for n in names:
            self.plugin_manager.reload(n)
        self.message("reloaded")
        return True

    # ----- macros -----
    def start_macro(self, name: str = "last") -> bool:
        """Start recording a macro into `name`.

        By default, this records into "last" (micro-style). Recording captures the
        actions/commands the editor runs, plus the action input snapshot needed
        to replay those actions deterministically.
        """
        if self._macro_playing or self.macro_recording:
            return False
        nm = str(name or "last")
        self._macro_target = nm
        self._macro_prev_last = list(self.macro)
        self._macro_buffer.clear()
        self.macro_recording = True
        self.message(f"macro: recording ({nm})")
        return True

    def stop_macro(self) -> bool:
        """Stop recording, saving the macro to its target name and to 'last'."""
        if self._macro_playing or not self.macro_recording:
            return False
        self.macro_recording = False
        steps = list(self._macro_buffer)
        self._macro_buffer.clear()

        # Save into 'last' (mutate list to keep stable reference).
        self.macro[:] = steps
        # Also save into the target name.
        self.macros[self._macro_target] = list(steps)
        self.macros["last"] = self.macro

        self.message(f"macro: saved {len(steps)} steps ({self._macro_target})")
        return True

    def cancel_macro(self) -> bool:
        """Stop recording and discard recorded steps (restore previous last macro)."""
        if self._macro_playing or not self.macro_recording:
            return False
        self.macro_recording = False
        self._macro_buffer.clear()
        if self._macro_prev_last is not None:
            self.macro[:] = list(self._macro_prev_last)
            self.macros["last"] = self.macro
        self.message("macro: canceled")
        return True

    def toggle_macro(self) -> bool:
        """Toggle recording of the 'last' macro (micro-style)."""
        return self.stop_macro() if self.macro_recording else self.start_macro("last")

    def play_macro(self, name: str = "last", *, count: int = 1) -> bool:
        """Play a recorded macro by name (default: 'last')."""
        if self._macro_playing or int(count) <= 0:
            return False
        steps = self.macros.get(str(name), None)
        if steps is None:
            steps = self.macro
        if not steps:
            return False

        self._macro_playing = True
        try:
            for _ in range(int(count)):
                for step in list(steps):
                    if step.kind == "action":
                        # restore input snapshot
                        self.input = dict(step.payload.get("input", {}))
                        self.run_action(step.name)
                    elif step.kind == "command":
                        self.exec_command_line(str(step.payload.get("cmdline", "")))
        finally:
            self._macro_playing = False
        return True

    def macro_names(self) -> list[str]:
        return sorted(self.macros.keys())

    def get_macro(self, name: str = "last") -> list[MacroStep]:
        return list(self.macros.get(str(name), self.macro))

    def set_macro(self, name: str, steps: list[MacroStep]) -> None:
        nm = str(name or "last")
        if nm == "last":
            self.macro[:] = list(steps)
            self.macros["last"] = self.macro
        else:
            self.macros[nm] = list(steps)


# ----- action execution -----
    def run_action(self, name: str) -> bool:
        act = self.actions.get(name)
        if act is None:
            raise KeyError(f"Unknown action: {name}")
        try:
            eb0 = self.cur()
            before_ver = int(getattr(eb0.buf, "version", 0))
        except Exception:
            eb0 = None  # type: ignore[assignment]
            before_ver = 0
        self._emit_mx_hook("ed.pre-action", name)

        if self.macro_recording and not self._macro_playing and name not in {"ToggleMacro", "PlayMacro", "CancelMacro"}:
            # Snapshot only the parts of input needed by common actions.
            self._macro_buffer.append(MacroStep(kind="action", name=name, payload={"input": dict(self.input)}))

        protected = False
        try:
            if eb0 is None:
                eb0 = self.cur()
            protected = bool(getattr(eb0, "local_options", {}).get("readonly"))
        except Exception:
            protected = False

        if protected and str(name) in MUTATING_ACTIONS:
            self.message(f"{name}: read-only buffer")
            ok = False
        else:
            ok = bool(act.fn(self))

        # Lifecycle-ish notification: did this action mutate the active buffer?
        try:
            eb1 = self.cur()
            after_ver = int(getattr(eb1.buf, "version", 0))
            if ok and after_ver != before_ver:
                self._emit_mx_hook("ed.on-change", str(eb1.name), str(name))
        except Exception:
            pass

        # Keep multi-cursor invariants stable after every action.
        try:
            eb = self.cur()
            self._normalize_cursor_lists(eb)
        except Exception:
            eb = None  # type: ignore[assignment]

        # Softwrap vertical motion wants a stable per-cursor "goal" x (visual column).
        # We update it after most actions, but avoid overwriting it after vertical
        # visual moves (Up/Down/PageUp/PageDown + selection variants), where we want
        # to preserve the goal even when clamped by short wrap rows.
        try:
            if eb is not None and bool(self.options.get("softwrap", local=eb.local_options)):
                if name not in {"CursorUp", "CursorDown", "PageUp", "PageDown", "SelectUp", "SelectDown"}:
                    w = int(self.viewport_width) if int(self.viewport_width) > 0 else 1
                    for i, c in enumerate(eb.cursors):
                        cid = int(eb.cursor_ids[i]) if i < len(eb.cursor_ids) else i
                        _y, x = self._cursor_visual_yx(eb, c, w=w)
                        eb.goal_x_by_cursor[cid] = int(x)
        except Exception:
            pass

        # Keep viewport aligned with the primary cursor for UI layers.
        try:
            self.ensure_cursor_visible()
        except Exception:
            pass

        self._emit_mx_hook("ed.on-action", name, 1 if ok else 0)
        return ok

    def _run_action_spec(self, spec: str) -> bool:
        s = spec.lstrip()

        if s.startswith("command:"):
            return self.exec_command_line(s[len("command:") :])
        if s.startswith("command-edit:"):
            self.enter_prompt("command", prefill=s[len("command-edit:") :])
            return True
        if s.startswith("mx:"):
            code = s[len("mx:") :]
            try:
                self.vm.eval(code, filename="<keybinding>")
                return True
            except Exception as e:
                self.message(str(e))
                return False

        return self.run_action(s.strip())

    def run_action_chain(self, spec: str) -> bool:
        """Execute a micro-style action chain string."""
        steps = parse_action_chain(spec)
        last_ok = False
        for step in steps:
            last_ok = self._run_action_spec(step.action)
            if step.sep == ",":
                continue
            if step.sep == "|" and last_ok:
                break
            if step.sep == "&" and not last_ok:
                break
        return last_ok

    # ----- clipboard helpers -----
    def clipboard_text(self) -> str:
        if self.clipboard_kind == "lines":
            if not self.clipboard_items:
                return ""
            return "\n".join(self.clipboard_items) + "\n"
        return "\n".join(self.clipboard_items)
    def set_clipboard_items(self, items: list[str], *, kind: str = "items") -> None:
        self.clipboard_items = list(items)
        self.clipboard_kind = kind
        # Track source so UI layers can avoid exporting script-driven clipboard
        # updates to privileged backends unless explicitly enabled.
        try:
            self.clipboard_from_script = bool(self.in_script_context())
        except Exception:
            self.clipboard_from_script = False
        self.clipboard_serial = int(getattr(self, 'clipboard_serial', 0)) + 1
    def _paste_reset(self) -> None:
        self._cutline_accum = False

    def clipboard_terminal_export_sequence(self) -> tuple[str | None, str]:
        """Return an OSC 52 sequence for exporting the clipboard (best-effort).

        This is primarily used by the curses TUI when:
          - clipboard=terminal
          - clipboard.osc52=true

        Safety: if the clipboard change was triggered in script context, we
        only allow export when cap.clipboard-write is enabled.

        Returns (seq, err). When seq is None, err may contain a human hint.
        """

        try:
            if str(self.options.get('clipboard') or '') != 'terminal':
                return (None, '')
            if not bool(self.options.get('clipboard.osc52')):
                return (None, '')
        except Exception:
            return (None, '')

        # Script-driven clipboard exports are gated.
        if bool(getattr(self, 'clipboard_from_script', False)) and not bool(self.options.get('cap.clipboard-write')):
            return (None, 'clipboard export disabled for scripts (set cap.clipboard-write true)')

        try:
            max_bytes = int(self.options.get('clipboard.osc52.max') or 0)
        except Exception:
            max_bytes = 0

        try:
            from .osc52 import osc52_sequence
        except Exception as e:
            return (None, f'osc52 unavailable: {e}')

        return osc52_sequence(self.clipboard_text(), max_bytes=max_bytes)


    def clipboard_external_export(self) -> tuple[bool, str]:
        """Best-effort export of the clipboard via external tools.

        Used primarily by UI layers when clipboard=external.

        Safety: script-originated clipboard updates are gated by
        cap.clipboard-write.

        Returns (ok, err). When ok is False, err may contain a human hint.
        """

        try:
            if str(self.options.get('clipboard') or '') != 'external':
                return (False, '')
        except Exception:
            return (False, '')

        # Script-driven clipboard exports are gated.
        if bool(getattr(self, 'clipboard_from_script', False)) and not bool(self.options.get('cap.clipboard-write')):
            return (False, 'clipboard export disabled for scripts (set cap.clipboard-write true)')

        try:
            cmd = str(self.options.get('clipboard.external.cmd') or '')
            args = str(self.options.get('clipboard.external.args') or '')
        except Exception:
            cmd = ''
            args = ''

        try:
            from .clipboard_external import detect_external_clipboard_cmd, parse_override
        except Exception as e:
            return (False, f'external clipboard unavailable: {e}')

        cc = parse_override(cmd, args) or detect_external_clipboard_cmd()
        if cc is None:
            # Avoid spamming the user; UI layers may show this once.
            if not bool(getattr(self, '_clipboard_external_warned', False)):
                setattr(self, '_clipboard_external_warned', True)
            return (False, 'no external clipboard tool found (try wl-copy/xclip/xsel/pbcopy/clip)')

        import subprocess

        try:
            timeout = float(self.options.get('clipboard.external.timeout') or 1.0)
        except Exception:
            timeout = 1.0

        try:
            p = subprocess.run(
                list(cc.argv),
                input=self.clipboard_text(),
                text=True,
                encoding='utf-8',
                errors='replace',
                timeout=timeout if timeout and timeout > 0 else None,
                capture_output=True,
                check=False,
            )
        except Exception as e:
            return (False, f'clipboard tool failed: {e}')

        if int(getattr(p, 'returncode', 1) or 0) != 0:
            err = ''
            try:
                err = (p.stderr or '').strip()
            except Exception:
                err = ''
            if not err:
                err = f'clipboard tool exited {p.returncode}'
            return (False, err)

        return (True, '')



    def clipboard_external_import_text(self) -> tuple[str | None, str]:
        """Best-effort import of clipboard text via external tools.

        Used primarily by editor actions (Paste) and hostcalls when
        clipboard=external.

        Safety: in script context, imports are gated by cap.clipboard-read.
        Interactive imports remain allowed.

        Returns (text, err). When text is None, err may contain a human hint.
        """

        try:
            if str(self.options.get('clipboard') or '') != 'external':
                return (None, 'clipboard backend is not external (set clipboard external)')
        except Exception:
            return (None, 'clipboard backend is not external (set clipboard external)')

        # Script-driven clipboard imports are gated.
        try:
            if bool(self.in_script_context()) and not bool(self.options.get('cap.clipboard-read')):
                return (None, 'clipboard import disabled for scripts (set cap.clipboard-read true)')
        except Exception:
            pass

        try:
            cmd = str(self.options.get('clipboard.external.readcmd') or '')
            args = str(self.options.get('clipboard.external.readargs') or '')
        except Exception:
            cmd = ''
            args = ''

        try:
            from .clipboard_external import detect_external_clipboard_read_cmd, parse_override
        except Exception as e:
            return (None, f'external clipboard unavailable: {e}')

        cc = parse_override(cmd, args) or detect_external_clipboard_read_cmd()
        if cc is None:
            return (None, 'no external clipboard read tool found (try wl-paste/xclip/xsel/pbpaste/powershell)')

        import subprocess

        try:
            timeout = float(self.options.get('clipboard.external.readtimeout') or 1.0)
        except Exception:
            timeout = 1.0

        try:
            pr = subprocess.run(
                list(cc.argv),
                input=None,
                capture_output=True,
                check=False,
                timeout=timeout if timeout and timeout > 0 else None,
            )
        except Exception as e:
            return (None, f'clipboard read tool failed: {e}')

        if int(getattr(pr, 'returncode', 1) or 0) != 0:
            err = ''
            try:
                err = (pr.stderr or b'').decode('utf-8', errors='replace').strip()
            except Exception:
                err = ''
            if not err:
                err = f'clipboard read tool exited {pr.returncode}'
            return (None, err)

        try:
            out = (pr.stdout or b'').decode('utf-8', errors='replace')
        except Exception:
            out = ''
        return (out, '')
    # ----- defaults -----
    def _install_default_options(self) -> None:
        self.options.register("ignorecase", True, kind="bool", doc="case-insensitive searching")
        self.options.register("incsearch", True, kind="bool", doc="incremental search as you type")
        self.options.register("hlsearch", False, kind="bool", doc="highlight matches (UI layer)")


        # Paste aggregation: when enabled, UI layers may aggregate bursts of
        # character key events into a single insert so terminal pastes don't
        # trigger auto-indent/auto-pairs on a per-key basis. (micro-esque)
        self.options.register(
            "paste",
            False,
            kind="bool",
            doc="aggregate paste bursts (UI layer; enable temporarily if your terminal lacks bracketed paste)",
        )

        self.options.register(
            "clipboard",
            "internal",
            kind="enum",
            enum=["internal", "external", "terminal"],
            doc="clipboard backend (internal/external/terminal)",
        )


        # Terminal clipboard export (OSC 52). UI layers can optionally export
        # the editor's clipboard to the system clipboard via terminal escape
        # sequences. This is best-effort (terminal support varies).
        self.options.register(
            "clipboard.osc52",
            True,
            kind="bool",
            doc="clipboard=terminal: export copies via OSC 52 (TUI, best-effort)",
        )
        self.options.register(
            "clipboard.osc52.max",
            100000,
            kind="int",
            doc="clipboard=terminal: max UTF-8 bytes to export via OSC 52 (0=unlimited)",
        )

        # External clipboard export (best-effort). UI layers may use these
        # settings to pipe copied text to a system clipboard tool.
        self.options.register(
            "clipboard.external.cmd",
            "",
            kind="str",
            doc="clipboard=external: override clipboard tool command (empty=auto-detect)",
        )
        self.options.register(
            "clipboard.external.args",
            "",
            kind="str",
            doc="clipboard=external: override clipboard tool args (shell-like string)",
        )
        self.options.register(
            "clipboard.external.timeout",
            1.0,
            kind="float",
            doc="clipboard=external: timeout (seconds) for clipboard tool",
        )

        # External clipboard import (best-effort). Paste may use these settings
        # to read the system clipboard via a platform clipboard tool.
        self.options.register(
            "clipboard.external.readcmd",
            "",
            kind="str",
            doc="clipboard=external: override clipboard read command (empty=auto-detect)",
        )
        self.options.register(
            "clipboard.external.readargs",
            "",
            kind="str",
            doc="clipboard=external: override clipboard read args (shell-like string)",
        )
        self.options.register(
            "clipboard.external.readtimeout",
            1.0,
            kind="float",
            doc="clipboard=external: timeout (seconds) for clipboard read tool",
        )
        self.options.register(
            "clipboard.external.import",
            True,
            kind="bool",
            doc="clipboard=external: on Paste, import from system clipboard (best-effort)",
        )

        # Capability gate: allow script-driven clipboard exports when a privileged
        # clipboard backend is in use (terminal/external). Interactive copy/cut
        # remains allowed; this only affects exports triggered in script context.
        self.options.register(
            "cap.clipboard-write",
            False,
            kind="bool",
            doc="allow scripts to export clipboard to system clipboard (terminal/external)",
        )

        # Capability gate: allow scripts to read/import the system clipboard via
        # external tools. Interactive paste remains allowed.
        self.options.register(
            "cap.clipboard-read",
            False,
            kind="bool",
            doc="allow scripts to import system clipboard via external tools",
        )

        self.options.register("jumplist.auto", True, kind="bool", doc="auto-push jumplist for jump commands (goto/jump)")

        self.options.register("indent", "    ", kind="str", doc="indent prefix")

        # Tabs: we follow micro-esque naming so config muscle-memory ports.
        # - tabsize controls *display* width (and how many spaces we insert when
        #   tabstospaces=true).
        # - tabstospaces controls whether the Tab key inserts '\t' or spaces.
        # Note: the core buffer is character-based; UI layers render tabs using
        # tabsize and can choose their own visual policies.
        self.options.register("tabsize", 4, kind="int", doc="tab width in spaces (display + tab insertion)")
        self.options.register("tabstospaces", True, kind="bool", doc="convert typed tabs to spaces")

        self.options.register("page.height", 30, kind="int", doc="page movement size for PageUp/PageDown")
        self.options.register(
            "prompt.page",
            8,
            kind="int",
            doc="picker prompts: PageUp/PageDown selection jump size (rows)",
        )
        self.options.register(
            "prompt.wrap",
            True,
            kind="bool",
            doc="picker prompts: wrap selection at ends (true) or clamp (false)",
        )

        # Docs browser: controls how `helplinkpick` sections are labeled.
        # - kind: legacy Docs/Files/External grouping
        # - heading: group links by nearest markdown heading (Top/Links/...)
        self.options.register(
            "help.linksections",
            "kind",
            kind="enum",
            enum=["kind", "heading"],
            doc="docs browser: helplinkpick section labels (kind|heading)",
        )
        # Viewport defaults for UI layers. A future TUI should call `ed.viewport!`
        # on startup and on resize to keep these current.
        self.options.register("viewport.height", 30, kind="int", doc="viewport height (lines) for UI scrolling")
        self.options.register("viewport.width", 80, kind="int", doc="viewport width (cols) for UI horizontal scrolling")
        self.options.register("softwrap", False, kind="bool", doc="soft-wrap long lines instead of horizontal scrolling")
        self.options.register("softwrap.contindent", -1, kind="int", doc="softwrap continuation indent columns (-1=auto, 0=off)")

        # Recent files MRU + prompt history (optional persistence).
        #
        # Persistence touches the host filesystem, so it is gated by `cap.persist`
        # (disabled by default). When enabled, `cap.persist-root` can constrain
        # where persistence files live.
        self.options.register("recent.persist", False, kind="bool", doc="persist recent file MRU to disk (requires cap.persist)")
        self.options.register("recent.file", "~/.config/micromax/recent.json", kind="str", doc="path for recent file MRU persistence")

        self.options.register("history.persist", False, kind="bool", doc="persist prompt history to disk (requires cap.persist)")
        self.options.register("history.file", "~/.config/micromax/history.json", kind="str", doc="path for prompt history persistence")
        self.options.register("history.limit", 200, kind="int", doc="max stored history entries per prompt kind")

        # Capability gates (host-owned world). These control whether *unsafe*
        # host surfaces are advertised/enabled.
        self.options.register("cap.persist", False, kind="bool", doc="allow editor-owned persistence files (recent/history) to be read/written (unsafe)")
        self.options.register("cap.persist-root", "~/.config/micromax", kind="str", doc="sandbox root for persistence files (empty=unrestricted)")
        self.options.register("cap.open-url", False, kind="bool", doc="allow opening external URLs from docs (unsafe)")
        self.options.register(
            "open-url.confirm",
            True,
            kind="bool",
            doc="confirm before opening external URLs from docs (even when cap.open-url is enabled)",
        )
        self.options.register("cap.shell", False, kind="bool", doc="allow running shell commands from scripts (unsafe)")
        self.options.register("cap.fs-open", False, kind="bool", doc="allow scripts to open files from disk (unsafe)")
        self.options.register("cap.fs-save", False, kind="bool", doc="allow scripts to save buffers to disk (unsafe)")
        self.options.register("cap.fs-read", False, kind="bool", doc="allow scripts to read arbitrary files from disk (unsafe)")
        self.options.register("cap.fs-list", False, kind="bool", doc="allow scripts to list directory entries from disk (unsafe)")
        self.options.register("cap.fs-stat", False, kind="bool", doc="allow scripts to stat paths on disk (unsafe)")
        self.options.register("cap.fs-root", "", kind="str", doc="filesystem sandbox root for cap.fs-* helpers (empty=unrestricted)")

        # Statusline: micro-esque split format strings.
        # Directives are embedded as $() expressions, e.g. $(filename), $(line),
        # $(opt:filetype), $(bind:SomeAction).
        self.options.register("statusline", True, kind="bool", doc="show status line (UI layer)")
        # TUI debug helpers.
        self.options.register(
            "tui.bracketedpaste",
            True,
            kind="bool",
            doc="TUI: enable bracketed paste mode (CSI ? 2004 h/l)",
        )
        self.options.register("tui.rawkeys", False, kind="bool", doc="TUI: show raw key events instead of dispatching")
        self.options.register(
            "statusformatl",
            "$(filename)$(modified)$(readonly)",
            kind="str",
            doc="status line left format string (micro-esque $() directives)",
        )
        self.options.register(
            "statusformatr",
            "ft:$(opt:filetype) enc:$(opt:encoding) $(opt:fileformat) $(position)$(cur)$(sel) $(percentage)% $(mode)$(keymode)$(macro)",
            kind="str",
            doc="status line right format string (micro-esque $() directives)",
        )

    def _install_default_actions(self) -> None:
        # ---- editing ----
        def a_insert_text(ed: Editor) -> bool:
            text = str(ed.input.get("text", ""))
            eb = ed.cur()
            ed._normalize_cursor_lists(eb)
            before = ed._snapshot_buffer_state(eb)

            # Replace selections per cursor.
            ranges = ed._all_selection_ranges()
            if ranges:
                ranges.sort(key=lambda t: (t[1].line, t[1].col), reverse=True)
                for i, s, e in ranges:
                    eb.cursors[i] = eb.buf.replace_range(s, e, text)
                    eb.sel_anchors[i] = None
            # Insert at all cursors.
            for i in reversed(range(len(eb.cursors))):
                if ed.selection_range(i) is not None:
                    # already handled above
                    continue
                eb.cursors[i] = eb.buf.insert(eb.cursors[i], text)

            after = ed._snapshot_buffer_state(eb)
            ed._record_undo_snapshot(eb, before, after, f"insert {len(text)}")
            return True

        def a_insert_newline(ed: Editor) -> bool:
            eb = ed.cur()
            ed._normalize_cursor_lists(eb)
            before = ed._snapshot_buffer_state(eb)

            def _leading_ws(s: str) -> str:
                i = 0
                while i < len(s) and s[i] in (" ", "\t"):
                    i += 1
                return s[:i]

            def _newline_indent(line: str, col: int) -> str:
                # Preserve the current line's indentation without duplicating it
                # when splitting *inside* the indent prefix.
                lead = _leading_ws(line)
                if col <= len(lead):
                    return lead[:col]
                return lead

            # Replace selections per cursor first.
            ranges = ed._all_selection_ranges()
            if ranges:
                ranges.sort(key=lambda t: (t[1].line, t[1].col), reverse=True)
                for i, s, e in ranges:
                    line = eb.buf.lines[s.line]
                    indent = _newline_indent(line, int(s.col))
                    eb.cursors[i] = eb.buf.replace_range(s, e, "\n" + indent)
                    eb.sel_anchors[i] = None

            # Insert newline at all remaining cursors.
            for i in reversed(range(len(eb.cursors))):
                if ed.selection_range(i) is not None:
                    continue
                c = eb.cursors[i]
                line = eb.buf.lines[c.line]
                indent = _newline_indent(line, int(c.col))
                eb.cursors[i] = eb.buf.insert(c, "\n" + indent)

            after = ed._snapshot_buffer_state(eb)
            if before == after:
                return False
            ed._record_undo_snapshot(eb, before, after, "newline")
            return True

        def a_backspace(ed: Editor) -> bool:
            eb = ed.cur()
            ed._normalize_cursor_lists(eb)
            before = ed._snapshot_buffer_state(eb)

            if ed._delete_selections():
                after = ed._snapshot_buffer_state(eb)
                ed._record_undo_snapshot(eb, before, after, "delete selection")
                return True

            for i in reversed(range(len(eb.cursors))):
                eb.cursors[i] = eb.buf.delete_char(eb.cursors[i], backward=True)

            after = ed._snapshot_buffer_state(eb)
            if before == after:
                return False
            ed._record_undo_snapshot(eb, before, after, "backspace")
            return True

        def a_delete_forward(ed: Editor) -> bool:
            """Delete char to the right (forward delete / Delete key)."""

            eb = ed.cur()
            ed._normalize_cursor_lists(eb)
            before = ed._snapshot_buffer_state(eb)

            if ed._delete_selections():
                after = ed._snapshot_buffer_state(eb)
                ed._record_undo_snapshot(eb, before, after, "delete selection")
                return True

            for i in reversed(range(len(eb.cursors))):
                eb.cursors[i] = eb.buf.delete_char(eb.cursors[i], backward=False)

            after = ed._snapshot_buffer_state(eb)
            if before == after:
                return False
            ed._record_undo_snapshot(eb, before, after, "delete")
            return True

        def a_undo(ed: Editor) -> bool:
            return ed.undo.undo()

        def a_redo(ed: Editor) -> bool:
            return ed.undo.redo()

        # ---- movement ----
        def _move_all(ed: Editor, dline: int, dcol: int) -> bool:
            eb = ed.cur()
            ed._normalize_cursor_lists(eb)
            for i, c in enumerate(eb.cursors):
                eb.cursors[i] = eb.buf.clamp(Cursor(c.line + dline, c.col + dcol))
            ed.clear_selection()
            return True

        def a_left(ed: Editor) -> bool:
            return _move_all(ed, 0, -1)

        def a_right(ed: Editor) -> bool:
            return _move_all(ed, 0, +1)

        def a_up(ed: Editor) -> bool:
            eb = ed.cur()
            if bool(ed.options.get("softwrap", local=eb.local_options)):
                return ed._move_cursors_visual(-1, extend_selection=False)
            return _move_all(ed, -1, 0)

        def a_down(ed: Editor) -> bool:
            eb = ed.cur()
            if bool(ed.options.get("softwrap", local=eb.local_options)):
                return ed._move_cursors_visual(+1, extend_selection=False)
            return _move_all(ed, +1, 0)

        def a_start_line(ed: Editor) -> bool:
            eb = ed.cur()
            ed._normalize_cursor_lists(eb)
            softwrap = bool(ed.options.get("softwrap", local=eb.local_options))
            w = int(ed.viewport_width) if int(ed.viewport_width) > 0 else int(ed.options.get("viewport.width", local=eb.local_options))
            for i, c in enumerate(eb.cursors):
                if not softwrap or w <= 0:
                    eb.cursors[i] = Cursor(c.line, 0)
                    continue
                s = eb.buf.lines[int(c.line)] if 0 <= int(c.line) < len(eb.buf.lines) else ""
                cont = ed._contindent_for_line(eb, s, w=w)
                row = ed._wrap_row_for_col_with_cont(s, int(c.col), w, cont)
                start = ed._wrap_start_for_row(w, cont, row)
                eb.cursors[i] = Cursor(c.line, start)
            ed.clear_selection()
            return True

        def a_end_line(ed: Editor) -> bool:
            eb = ed.cur()
            ed._normalize_cursor_lists(eb)
            softwrap = bool(ed.options.get("softwrap", local=eb.local_options))
            w = int(ed.viewport_width) if int(ed.viewport_width) > 0 else int(ed.options.get("viewport.width", local=eb.local_options))
            for i, c in enumerate(eb.cursors):
                s = eb.buf.lines[int(c.line)] if 0 <= int(c.line) < len(eb.buf.lines) else ""
                if not softwrap or w <= 0:
                    eb.cursors[i] = Cursor(c.line, len(s))
                    continue
                cont = ed._contindent_for_line(eb, s, w=w)
                row = ed._wrap_row_for_col_with_cont(s, int(c.col), w, cont)
                end_col = ed._wrap_end_for_row(len(s), w, cont, row)
                eb.cursors[i] = Cursor(c.line, end_col)
            ed.clear_selection()
            return True

        def a_doc_top(ed: Editor) -> bool:
            """Move cursor(s) to top of document (Ctrl-Home)."""
            eb = ed.cur()
            ed._normalize_cursor_lists(eb)
            for i, c in enumerate(eb.cursors):
                eb.cursors[i] = eb.buf.clamp(Cursor(0, int(c.col)))
            ed.clear_selection()
            return True

        def a_doc_bottom(ed: Editor) -> bool:
            """Move cursor(s) to bottom of document (Ctrl-End)."""
            eb = ed.cur()
            ed._normalize_cursor_lists(eb)
            last = max(0, len(eb.buf.lines) - 1)
            for i, c in enumerate(eb.cursors):
                eb.cursors[i] = eb.buf.clamp(Cursor(last, int(c.col)))
            ed.clear_selection()
            return True

        def a_page_up(ed: Editor) -> bool:
            """Move cursor(s) up by a page (PageUp).

            Page height is controlled by `page.height` (default: 30).
            Under softwrap, this is measured in *visual rows*.
            """
            eb = ed.cur()
            ed._normalize_cursor_lists(eb)
            page = int(ed.page_height(eb=eb))
            if bool(ed.options.get("softwrap", local=eb.local_options)):
                return ed._move_cursors_visual(-page, extend_selection=False)
            for i, c in enumerate(eb.cursors):
                eb.cursors[i] = eb.buf.clamp(Cursor(int(c.line) - page, int(c.col)))
            ed.clear_selection()
            return True

        def a_page_down(ed: Editor) -> bool:
            """Move cursor(s) down by a page (PageDown)."""
            eb = ed.cur()
            ed._normalize_cursor_lists(eb)
            page = int(ed.page_height(eb=eb))
            if bool(ed.options.get("softwrap", local=eb.local_options)):
                return ed._move_cursors_visual(+page, extend_selection=False)
            for i, c in enumerate(eb.cursors):
                eb.cursors[i] = eb.buf.clamp(Cursor(int(c.line) + page, int(c.col)))
            ed.clear_selection()
            return True

        def a_word_left(ed: Editor) -> bool:
            """Move cursor(s) left by one word boundary (Ctrl-Left)."""
            eb = ed.cur()
            ed._normalize_cursor_lists(eb)
            for i, c in enumerate(eb.cursors):
                eb.cursors[i] = eb.buf.word_boundary_left(c)
            ed.clear_selection()
            return True

        def a_word_right(ed: Editor) -> bool:
            """Move cursor(s) right to the next word boundary (Ctrl-Right)."""
            eb = ed.cur()
            ed._normalize_cursor_lists(eb)
            for i, c in enumerate(eb.cursors):
                eb.cursors[i] = eb.buf.word_boundary_right(c)
            ed.clear_selection()
            return True

        # ---- navigation history (jumplist) ----
        def a_push_jump(ed: Editor) -> bool:
            return ed.push_jump()

        def a_jump_back(ed: Editor) -> bool:
            return ed.jump_back()

        def a_jump_forward(ed: Editor) -> bool:
            return ed.jump_forward()

        # ---- selection ----
        def _ensure_anchor_all(ed: Editor) -> None:
            eb = ed.cur()
            ed._normalize_cursor_lists(eb)
            for i, a in enumerate(eb.sel_anchors):
                if a is None:
                    c = eb.cursors[i]
                    eb.sel_anchors[i] = Cursor(c.line, c.col)

        def _select_move(ed: Editor, dline: int, dcol: int) -> bool:
            _ensure_anchor_all(ed)
            eb = ed.cur()
            for i, c in enumerate(eb.cursors):
                eb.cursors[i] = eb.buf.clamp(Cursor(c.line + dline, c.col + dcol))
            return True

        def a_select_left(ed: Editor) -> bool:
            return _select_move(ed, 0, -1)

        def a_select_right(ed: Editor) -> bool:
            return _select_move(ed, 0, +1)

        def a_select_word_left(ed: Editor) -> bool:
            """Extend selection left to previous word boundary (Shift-Ctrl-Left)."""
            _ensure_anchor_all(ed)
            eb = ed.cur()
            ed._normalize_cursor_lists(eb)
            for i, c in enumerate(eb.cursors):
                eb.cursors[i] = eb.buf.word_boundary_left(c)
            return True

        def a_select_word_right(ed: Editor) -> bool:
            """Extend selection right to next word boundary (Shift-Ctrl-Right)."""
            _ensure_anchor_all(ed)
            eb = ed.cur()
            ed._normalize_cursor_lists(eb)
            for i, c in enumerate(eb.cursors):
                eb.cursors[i] = eb.buf.word_boundary_right(c)
            return True

        def a_select_up(ed: Editor) -> bool:
            _ensure_anchor_all(ed)
            eb = ed.cur()
            if bool(ed.options.get("softwrap", local=eb.local_options)):
                return ed._move_cursors_visual(-1, extend_selection=True)
            return _select_move(ed, -1, 0)

        def a_select_down(ed: Editor) -> bool:
            _ensure_anchor_all(ed)
            eb = ed.cur()
            if bool(ed.options.get("softwrap", local=eb.local_options)):
                return ed._move_cursors_visual(+1, extend_selection=True)
            return _select_move(ed, +1, 0)

        def a_select_all(ed: Editor) -> bool:
            eb = ed.cur()
            # SelectAll collapses to a single cursor (simple, predictable).
            eb.cursors[:] = [Cursor(0, 0)]
            eb.sel_anchors[:] = [Cursor(0, 0)]
            eb.cursor_ids[:] = [ed._alloc_cursor_id()]
            eb.primary = 0
            last_line = len(eb.buf.lines) - 1
            eb.cursors[0] = Cursor(last_line, len(eb.buf.lines[last_line]))
            return True

        def a_clear_selection(ed: Editor) -> bool:
            if not ed.has_selection() and all(a is None for a in ed.cur().sel_anchors):
                return False
            ed.clear_selection()
            return True

        def a_flip_selections(ed: Editor) -> bool:
            """Swap selection anchor/cursor endpoints (Helix/Kakoune-inspired)."""

            eb = ed.cur()
            ed._normalize_cursor_lists(eb)
            changed = False
            for i, a in enumerate(eb.sel_anchors):
                if a is None:
                    continue
                c = eb.cursors[i]
                eb.cursors[i] = Cursor(a.line, a.col)
                eb.sel_anchors[i] = Cursor(c.line, c.col)
                changed = True
            if changed:
                ed._normalize_cursor_lists(eb)
            return changed

        def a_ensure_selections_forward(ed: Editor) -> bool:
            """Ensure selection direction is forward (anchor <= cursor)."""

            eb = ed.cur()
            ed._normalize_cursor_lists(eb)
            changed = False
            for i, a in enumerate(eb.sel_anchors):
                if a is None:
                    continue
                c = eb.cursors[i]
                if (c.line, c.col) < (a.line, a.col):
                    eb.cursors[i] = Cursor(a.line, a.col)
                    eb.sel_anchors[i] = Cursor(c.line, c.col)
                    changed = True
            if changed:
                ed._normalize_cursor_lists(eb)
            return changed

        # ---- clipboard ----
        def a_copy(ed: Editor) -> bool:
            eb = ed.cur()
            ed._normalize_cursor_lists(eb)
            parts: list[str] = []
            for i in range(len(eb.cursors)):
                if ed.has_selection(i):
                    parts.append(ed.selection_text(i))
            if not parts:
                ed.message("no selection")
                return False
            ed.set_clipboard_items(parts, kind="items")
            ed._cutline_accum = False
            ed.message("copied")
            return True

        def a_cut(ed: Editor) -> bool:
            eb = ed.cur()
            ed._normalize_cursor_lists(eb)
            parts: list[str] = []
            for i in range(len(eb.cursors)):
                if ed.has_selection(i):
                    parts.append(ed.selection_text(i))
            if not parts:
                ed.message("no selection")
                return False

            before = ed._snapshot_buffer_state(eb)
            # Delete selections across cursors
            ok = ed._delete_selections()
            after = ed._snapshot_buffer_state(eb)
            if ok:
                ed._record_undo_snapshot(eb, before, after, "cut")
            ed.set_clipboard_items(parts, kind="items")
            ed._cutline_accum = False
            ed.message("cut")
            return ok
        def a_paste(ed: Editor) -> bool:
            system_text: str | None = None
            err_hint = ""

            # When clipboard=external, micro-esque Ctrl-v should paste from the
            # system clipboard (best-effort). We keep the editor's internal clipboard
            # as a fallback when tools are unavailable.
            try:
                backend = str(ed.options.get('clipboard') or '')
            except Exception:
                backend = ''
            if backend == 'external':
                try:
                    do_import = bool(ed.options.get('clipboard.external.import'))
                except Exception:
                    do_import = True
                if do_import:
                    system_text, err_hint = ed.clipboard_external_import_text()

            if system_text is None and not ed.clipboard_items:
                # No internal clipboard; show a gentle one-time hint for external
                # clipboard missing (interactive only).
                if err_hint and not ed.in_script_context():
                    if err_hint.startswith('no external clipboard read tool'):
                        if not bool(getattr(ed, '_clipboard_external_read_warned', False)):
                            setattr(ed, '_clipboard_external_read_warned', True)
                            ed.message(str(err_hint))
                    elif err_hint.startswith('clipboard import disabled for scripts'):
                        pass
                    elif err_hint.startswith('clipboard backend is not external'):
                        pass
                    else:
                        ed.message(str(err_hint))
                return False

            eb = ed.cur()
            ed._normalize_cursor_lists(eb)
            before = ed._snapshot_buffer_state(eb)

            if system_text is not None:
                per_cursor = [system_text] * len(eb.cursors)
            else:
                items = ed.clipboard_items
                if ed.clipboard_kind == 'items' and len(items) == len(eb.cursors):
                    per_cursor = items
                else:
                    per_cursor = [ed.clipboard_text()] * len(eb.cursors)

            ops: list[tuple[int, Cursor, Cursor | None]] = []
            for i in range(len(eb.cursors)):
                rng = ed.selection_range(i)
                if rng is None:
                    ops.append((i, eb.cursors[i], None))
                else:
                    s, e = rng
                    ops.append((i, s, e))

            # Apply from bottom to top.
            def _key(t: tuple[int, Cursor, Cursor | None]) -> tuple[int, int]:
                return (t[1].line, t[1].col)

            ops.sort(key=_key, reverse=True)
            for i, s, e in ops:
                text = per_cursor[i]
                if e is None:
                    eb.cursors[i] = eb.buf.insert(eb.cursors[i], text)
                else:
                    eb.cursors[i] = eb.buf.replace_range(s, e, text)
                eb.sel_anchors[i] = None

            after = ed._snapshot_buffer_state(eb)
            ed._record_undo_snapshot(eb, before, after, 'paste')
            ed._paste_reset()
            return True

        # ---- line ops ----
        def a_cut_line(ed: Editor) -> bool:
            eb = ed.cur()
            ed._normalize_cursor_lists(eb)
            before = ed._snapshot_buffer_state(eb)

            # Delete unique lines touched by cursors.
            lines = sorted({c.line for c in eb.cursors}, reverse=True)
            cut_parts: list[str] = []
            for li in lines:
                cut_parts.append(eb.buf.lines[li])
                eb.buf.delete_line(li)
                # adjust cursors + anchors above deleted line
                for i, c in enumerate(eb.cursors):
                    if c.line > li:
                        eb.cursors[i] = Cursor(c.line - 1, c.col)
                    elif c.line == li:
                        eb.cursors[i] = eb.buf.clamp(Cursor(li, 0))
                    a = eb.sel_anchors[i]
                    if a is not None:
                        if a.line > li:
                            eb.sel_anchors[i] = Cursor(a.line - 1, a.col)
                        elif a.line == li:
                            eb.sel_anchors[i] = Cursor(li, 0)

            ed.clear_selection()

            if ed._cutline_accum and ed.clipboard_items:
                ed.clipboard_items.extend(reversed(cut_parts))
                ed.clipboard_kind = "lines"
            else:
                ed.set_clipboard_items(list(reversed(cut_parts)), kind="lines")
            ed._cutline_accum = True

            after = ed._snapshot_buffer_state(eb)
            ed._record_undo_snapshot(eb, before, after, "cut line")
            return True

        def a_duplicate_line(ed: Editor) -> bool:
            eb = ed.cur()
            ed._normalize_cursor_lists(eb)
            before = ed._snapshot_buffer_state(eb)
            line = eb.cursors[eb.primary].line
            eb.cursors[eb.primary] = eb.buf.duplicate_line(line)
            after = ed._snapshot_buffer_state(eb)
            ed._record_undo_snapshot(eb, before, after, "duplicate line")
            return True

        def a_move_lines_up(ed: Editor) -> bool:
            eb = ed.cur()
            ed._normalize_cursor_lists(eb)
            before = ed._snapshot_buffer_state(eb)

            span = _selected_line_span(ed)
            if span is None:
                span = (eb.cursors[eb.primary].line, eb.cursors[eb.primary].line)
            start, end = span
            if start <= 0:
                return False
            # move block up by one
            block = eb.buf.lines[start : end + 1]
            eb.buf.lines[start - 1 : end + 1] = block + [eb.buf.lines[start - 1]]
            eb.buf.dirty = True

            # adjust cursors/anchors in block
            for i, c in enumerate(eb.cursors):
                if start <= c.line <= end:
                    eb.cursors[i] = Cursor(c.line - 1, c.col)
                elif c.line == start - 1:
                    eb.cursors[i] = Cursor(end, c.col)
            for i, a in enumerate(eb.sel_anchors):
                if a is None:
                    continue
                if start <= a.line <= end:
                    eb.sel_anchors[i] = Cursor(a.line - 1, a.col)
                elif a.line == start - 1:
                    eb.sel_anchors[i] = Cursor(end, a.col)

            after = ed._snapshot_buffer_state(eb)
            ed._record_undo_snapshot(eb, before, after, "move lines up")
            return True

        def a_move_lines_down(ed: Editor) -> bool:
            eb = ed.cur()
            ed._normalize_cursor_lists(eb)
            before = ed._snapshot_buffer_state(eb)

            span = _selected_line_span(ed)
            if span is None:
                span = (eb.cursors[eb.primary].line, eb.cursors[eb.primary].line)
            start, end = span
            if end >= len(eb.buf.lines) - 1:
                return False
            block = eb.buf.lines[start : end + 1]
            eb.buf.lines[start : end + 2] = [eb.buf.lines[end + 1]] + block
            eb.buf.dirty = True

            for i, c in enumerate(eb.cursors):
                if start <= c.line <= end:
                    eb.cursors[i] = Cursor(c.line + 1, c.col)
                elif c.line == end + 1:
                    eb.cursors[i] = Cursor(start, c.col)
            for i, a in enumerate(eb.sel_anchors):
                if a is None:
                    continue
                if start <= a.line <= end:
                    eb.sel_anchors[i] = Cursor(a.line + 1, a.col)
                elif a.line == end + 1:
                    eb.sel_anchors[i] = Cursor(start, a.col)

            after = ed._snapshot_buffer_state(eb)
            ed._record_undo_snapshot(eb, before, after, "move lines down")
            return True

        # ---- indent ----
        def _selected_line_span(ed: Editor) -> tuple[int, int] | None:
            # Union of all cursor selections; returns bounding span.
            ranges = ed._all_selection_ranges()
            if not ranges:
                return None
            starts: list[int] = []
            ends: list[int] = []
            for _, s, e in ranges:
                start = s.line
                end = e.line
                if e.col == 0 and end > start:
                    end -= 1
                starts.append(start)
                ends.append(end)
            return (min(starts), max(ends))

        def a_indent_selection(ed: Editor) -> bool:
            span = _selected_line_span(ed)
            if span is None:
                return False
            eb = ed.cur()
            before = ed._snapshot_buffer_state(eb)
            pref = str(ed.options.get("indent", local=eb.local_options))
            for li in range(span[0], span[1] + 1):
                eb.buf.lines[li] = pref + eb.buf.lines[li]

            # adjust cursors/anchors if on affected lines
            for i, a in enumerate(eb.sel_anchors):
                if a and span[0] <= a.line <= span[1]:
                    eb.sel_anchors[i] = Cursor(a.line, a.col + len(pref))
            for i, c in enumerate(eb.cursors):
                if span[0] <= c.line <= span[1]:
                    eb.cursors[i] = Cursor(c.line, c.col + len(pref))
            eb.buf.dirty = True

            after = ed._snapshot_buffer_state(eb)
            ed._record_undo_snapshot(eb, before, after, "indent")
            return True

        def a_unindent_selection(ed: Editor) -> bool:
            span = _selected_line_span(ed)
            if span is None:
                return False
            eb = ed.cur()
            before = ed._snapshot_buffer_state(eb)
            pref = str(ed.options.get("indent", local=eb.local_options))
            removed = 0
            for li in range(span[0], span[1] + 1):
                ln = eb.buf.lines[li]
                if ln.startswith(pref):
                    eb.buf.lines[li] = ln[len(pref) :]
                    removed = len(pref)
                else:
                    n = 0
                    while n < len(pref) and n < len(ln) and ln[n] == " ":
                        n += 1
                    if n:
                        eb.buf.lines[li] = ln[n:]
                        removed = max(removed, n)

            if removed:
                for i, a in enumerate(eb.sel_anchors):
                    if a and span[0] <= a.line <= span[1]:
                        eb.sel_anchors[i] = Cursor(a.line, max(0, a.col - removed))
                for i, c in enumerate(eb.cursors):
                    if span[0] <= c.line <= span[1]:
                        eb.cursors[i] = Cursor(c.line, max(0, c.col - removed))

            eb.buf.dirty = True
            after = ed._snapshot_buffer_state(eb)
            if before == after:
                return False
            ed._record_undo_snapshot(eb, before, after, "unindent")
            return True

        # ---- prompt / completion ----
        def a_autocomplete(ed: Editor) -> bool:
            # Prompt completion (command bar) lives on Editor so it can consult
            # command names, options, macros, plugin names, etc.
            return ed.prompt_complete(direction=1)

        def a_prompt_complete_prev(ed: Editor) -> bool:
            return ed.prompt_complete(direction=-1)

        def a_insert_tab(ed: Editor) -> bool:
            if ed.prompt is not None:
                # In the command prompt, Tab is reserved for completion; don't insert a
                # literal tab when completion fails.
                if ed.prompt.kind == "find":
                    ed.set_prompt_text(ed.prompt.text + "\t")
                    return True
                return False

            eb = ed.cur()
            ed._normalize_cursor_lists(eb)
            before = ed._snapshot_buffer_state(eb)

            tabstospaces = bool(ed.options.get("tabstospaces", local=eb.local_options))
            tabsize_raw = int(ed.options.get("tabsize", local=eb.local_options))
            tabsize = max(1, tabsize_raw)

            def _visual_col(line: str, col: int) -> int:
                # Best-effort visual column accounting for existing tabs.
                v = 0
                for ch in line[: max(0, min(col, len(line)))]:
                    if ch == "\t":
                        v += tabsize - (v % tabsize)
                    else:
                        v += 1
                return v

            def _tab_text_at(line: str, col: int) -> str:
                if not tabstospaces:
                    return "\t"
                v = _visual_col(line, col)
                n = tabsize - (v % tabsize)
                if n <= 0:
                    n = tabsize
                return " " * n

            # Replace selections per cursor first (should usually be handled by
            # IndentSelection, but we keep this action robust).
            ranges = ed._all_selection_ranges()
            if ranges:
                ranges.sort(key=lambda t: (t[1].line, t[1].col), reverse=True)
                for i, s, e in ranges:
                    line = eb.buf.lines[s.line]
                    eb.cursors[i] = eb.buf.replace_range(s, e, _tab_text_at(line, int(s.col)))
                    eb.sel_anchors[i] = None

            # Insert at all remaining cursors.
            for i in reversed(range(len(eb.cursors))):
                if ed.selection_range(i) is not None:
                    continue
                c = eb.cursors[i]
                line = eb.buf.lines[c.line]
                eb.cursors[i] = eb.buf.insert(c, _tab_text_at(line, int(c.col)))

            after = ed._snapshot_buffer_state(eb)
            if before == after:
                return False
            ed._record_undo_snapshot(eb, before, after, "tab")
            return True


        def _is_text_key(k: str) -> bool:
            return len(k) == 1 and k.isprintable() and k not in ('\n', '\r', '\t')

        def a_prompt_insert_text(ed: Editor) -> bool:
            if ed.prompt is None:
                return False
            text = str(ed.input.get('text', ''))
            if text == '':
                return False
            p = ed.prompt
            s = p.text
            i = int(p.cursor)
            new = s[:i] + text + s[i:]
            return ed.set_prompt_text_cursor(new, i + len(text))

        def a_prompt_backspace(ed: Editor) -> bool:
            if ed.prompt is None:
                return False
            p = ed.prompt
            i = int(p.cursor)
            if i <= 0:
                return False
            s = p.text
            new = s[: i - 1] + s[i:]
            return ed.set_prompt_text_cursor(new, i - 1)

        def a_prompt_delete(ed: Editor) -> bool:
            if ed.prompt is None:
                return False
            p = ed.prompt
            i = int(p.cursor)
            s = p.text
            if i >= len(s):
                return False
            new = s[:i] + s[i + 1 :]
            return ed.set_prompt_text_cursor(new, i)

        def a_prompt_left(ed: Editor) -> bool:
            if ed.prompt is None:
                return False
            ed.prompt.set_cursor(int(ed.prompt.cursor) - 1)
            return True

        def a_prompt_right(ed: Editor) -> bool:
            if ed.prompt is None:
                return False
            ed.prompt.set_cursor(int(ed.prompt.cursor) + 1)
            return True

        def a_prompt_home(ed: Editor) -> bool:
            if ed.prompt is None:
                return False
            ed.prompt.set_cursor(0)
            return True

        def a_prompt_end(ed: Editor) -> bool:
            if ed.prompt is None:
                return False
            ed.prompt.set_cursor(len(ed.prompt.text))
            return True

        # ---- prompt modes ----
        def a_command_mode(ed: Editor) -> bool:
            ed.enter_prompt("command")
            return True

        def a_command_palette(ed: Editor) -> bool:
            ed.enter_command_palette()
            return True

        def a_topic_prompt(ed: Editor) -> bool:
            ed.enter_topic_prompt()
            return True

        def a_binding_prompt(ed: Editor) -> bool:
            ed.enter_binding_prompt()
            return True

        def a_find(ed: Editor) -> bool:
            ed.search.literal = True
            ed.enter_prompt("find")
            return True

        def a_find_literal(ed: Editor) -> bool:
            ed.search.literal = True
            ed.enter_prompt("find")
            return True

        def a_find_regex(ed: Editor) -> bool:
            ed.search.literal = False
            ed.enter_prompt("find")
            return True

        def a_find_next(ed: Editor) -> bool:
            return ed.find_next()

        def a_find_prev(ed: Editor) -> bool:
            return ed.find_prev()

        def a_escape(ed: Editor) -> bool:
            return ed.cancel_prompt()

        def a_submit(ed: Editor) -> bool:
            return ed.submit_prompt()

        # ---- query replace confirmation loop ----
        def a_qreplace_yes(ed: Editor) -> bool:
            return ed.qreplace_yes()

        def a_qreplace_no(ed: Editor) -> bool:
            return ed.qreplace_no()

        def a_qreplace_all(ed: Editor) -> bool:
            return ed.qreplace_all()

        def a_qreplace_last(ed: Editor) -> bool:
            return ed.qreplace_last()

        def a_qreplace_quit(ed: Editor) -> bool:
            return ed.qreplace_quit()

        def a_prompt_prev(ed: Editor) -> bool:
            return ed.prompt_history_prev()

        def a_prompt_next(ed: Editor) -> bool:
            return ed.prompt_history_next()

        def a_prompt_suggest_prev(ed: Editor) -> bool:
            return ed.prompt_suggest_move(-1)

        def a_prompt_suggest_next(ed: Editor) -> bool:
            return ed.prompt_suggest_move(+1)

        def a_prompt_suggest_prev_section(ed: Editor) -> bool:
            return ed.prompt_suggest_prev_section()

        def a_prompt_suggest_next_section(ed: Editor) -> bool:
            return ed.prompt_suggest_next_section()

        def a_prompt_suggest_page_up(ed: Editor) -> bool:
            return ed.prompt_suggest_page(-1)

        def a_prompt_suggest_page_down(ed: Editor) -> bool:
            return ed.prompt_suggest_page(+1)

        def a_prompt_copy_selected(ed: Editor) -> bool:
            return ed.prompt_copy_selected()

        def a_prompt_suggest_first(ed: Editor) -> bool:
            return ed.prompt_suggest_first()

        def a_prompt_suggest_last(ed: Editor) -> bool:
            return ed.prompt_suggest_last()

        # ---- macros ----
        def a_toggle_macro(ed: Editor) -> bool:
            return ed.toggle_macro()

        def a_play_macro(ed: Editor) -> bool:
            return ed.play_macro()

        def a_cancel_macro(ed: Editor) -> bool:
            return ed.cancel_macro()

        # ---- multiple cursors ----
        def a_spawn_mc_up(ed: Editor) -> bool:
            eb = ed.cur()
            ed._normalize_cursor_lists(eb)
            c = eb.cursors[eb.primary]
            if c.line <= 0:
                return False
            eb.cursors.append(eb.buf.clamp(Cursor(c.line - 1, c.col)))
            eb.sel_anchors.append(None)
            eb.cursor_ids.append(ed._alloc_cursor_id())
            return True

        def a_spawn_mc_down(ed: Editor) -> bool:
            eb = ed.cur()
            ed._normalize_cursor_lists(eb)
            c = eb.cursors[eb.primary]
            if c.line >= len(eb.buf.lines) - 1:
                return False
            eb.cursors.append(eb.buf.clamp(Cursor(c.line + 1, c.col)))
            eb.sel_anchors.append(None)
            eb.cursor_ids.append(ed._alloc_cursor_id())
            return True

        def a_remove_mc(ed: Editor) -> bool:
            eb = ed.cur()
            if len(eb.cursors) <= 1:
                return False
            ed._normalize_cursor_lists(eb)
            # Remove the most recently created *non-primary* cursor.
            candidates = [(cid, i) for i, cid in enumerate(eb.cursor_ids) if i != eb.primary]
            if not candidates:
                return False
            _cid, idx = max(candidates, key=lambda t: t[0])
            eb.cursors.pop(idx)
            eb.sel_anchors.pop(idx)
            eb.cursor_ids.pop(idx)
            if eb.primary > idx:
                eb.primary -= 1
            return True

        def a_remove_all_mc(ed: Editor) -> bool:
            eb = ed.cur()
            if len(eb.cursors) <= 1:
                return False
            ed._normalize_cursor_lists(eb)
            p = eb.primary
            eb.cursors[:] = [eb.cursors[p]]
            eb.sel_anchors[:] = [eb.sel_anchors[p]]
            eb.cursor_ids[:] = [eb.cursor_ids[p]]
            eb.primary = 0
            return True

        def a_cycle_primary_next(ed: Editor) -> bool:
            """Cycle the primary cursor forward (Kakoune/Helix-inspired)."""
            eb = ed.cur()
            ed._normalize_cursor_lists(eb)
            if len(eb.cursors) <= 1:
                return False
            eb.primary = (eb.primary + 1) % len(eb.cursors)
            return True

        def a_cycle_primary_prev(ed: Editor) -> bool:
            """Cycle the primary cursor backward (Kakoune/Helix-inspired)."""
            eb = ed.cur()
            ed._normalize_cursor_lists(eb)
            if len(eb.cursors) <= 1:
                return False
            eb.primary = (eb.primary - 1) % len(eb.cursors)
            return True

        def a_collapse_to_primary(ed: Editor) -> bool:
            """Drop all cursors except the primary one."""
            eb = ed.cur()
            ed._normalize_cursor_lists(eb)
            if len(eb.cursors) <= 1:
                return False
            p = eb.primary
            eb.cursors[:] = [eb.cursors[p]]
            eb.sel_anchors[:] = [eb.sel_anchors[p]]
            eb.cursor_ids[:] = [eb.cursor_ids[p]]
            eb.primary = 0
            return True

        def _mc_needle(ed: Editor, eb: EditorBuffer) -> tuple[str, int] | None:
            # Ensure selection exists on primary cursor; if not, select current word.
            p = eb.primary
            if not ed.has_primary_selection():
                r = eb.buf.word_range_at(eb.cursors[p])
                if r is None:
                    return None
                s, e = r
                eb.sel_anchors[p] = s
                eb.cursors[p] = e
            text = ed.selection_text(None)
            if text == "":
                return None
            return text, len(text)

        def _find_next_literal(ed: Editor, eb: EditorBuffer, needle: str, start: Cursor) -> Cursor | None:
            ignorecase = bool(ed.options.get("ignorecase", local=eb.local_options))
            if not ignorecase:
                return eb.buf.find(needle, start=start)
            # naive case-insensitive forward search
            nlow = needle.lower()
            cur = eb.buf.clamp(start)
            # first line
            idx = eb.buf.lines[cur.line].lower().find(nlow, cur.col)
            if idx >= 0:
                return Cursor(cur.line, idx)
            for li in range(cur.line + 1, len(eb.buf.lines)):
                idx = eb.buf.lines[li].lower().find(nlow)
                if idx >= 0:
                    return Cursor(li, idx)
            return None

        def a_spawn_mc_select(ed: Editor) -> bool:
            eb = ed.cur()
            ed._normalize_cursor_lists(eb)
            info = _mc_needle(ed, eb)
            if info is None:
                return False
            needle, nlen = info

            # Start after the end of the current selection.
            rng = ed.selection_range(None)
            assert rng is not None
            _s, e = rng
            start = Cursor(e.line, e.col)
            m = _find_next_literal(ed, eb, needle, start)
            if m is None:
                return False

            eb.cursors.append(Cursor(m.line, m.col + nlen))
            eb.sel_anchors.append(Cursor(m.line, m.col))
            eb.cursor_ids.append(ed._alloc_cursor_id())
            ed._mc_last_match_start = Cursor(m.line, m.col)
            return True

        def a_skip_mc(ed: Editor) -> bool:
            eb = ed.cur()
            ed._normalize_cursor_lists(eb)
            info = _mc_needle(ed, eb)
            if info is None:
                return False
            needle, nlen = info

            # Continue from last match start if present; else from current selection end.
            start = ed._mc_last_match_start
            if start is None:
                rng = ed.selection_range(None)
                assert rng is not None
                _s, e = rng
                start = e
            m = _find_next_literal(ed, eb, needle, Cursor(start.line, start.col + 1))
            if m is None:
                return False

            # move primary selection to this match (visual feedback)
            p = eb.primary
            eb.sel_anchors[p] = Cursor(m.line, m.col)
            eb.cursors[p] = Cursor(m.line, m.col + nlen)
            ed._mc_last_match_start = Cursor(m.line, m.col)
            return True

        def a_spawn_mc_lines(ed: Editor) -> bool:
            eb = ed.cur()
            ed._normalize_cursor_lists(eb)
            if not ed.has_primary_selection():
                return False
            rng = ed.selection_range(None)
            assert rng is not None
            s, e = rng
            start_line = s.line
            end_line = e.line
            if e.col == 0 and end_line > start_line:
                end_line -= 1
            # replace cursor set with one cursor per line at col 0
            eb.cursors[:] = [Cursor(li, 0) for li in range(start_line, end_line + 1)]
            eb.sel_anchors[:] = [None] * len(eb.cursors)
            eb.cursor_ids[:] = [ed._alloc_cursor_id() for _ in eb.cursors]
            eb.primary = 0
            return True

        def a_noop(ed: Editor) -> bool:
            return False

        # ---- docs/help browser helpers ----
        def a_help_copy_link_target(ed: Editor) -> bool:
            return bool(ed.help_copy_link_target())

        def a_open_url_under_cursor(ed: Editor) -> bool:
            return bool(ed.open_url_under_cursor())

        def a_copy_url_under_cursor(ed: Editor) -> bool:
            return bool(ed.copy_url_under_cursor())

        # ---- external URL confirmation (capture mode) ----
        def a_openurl_yes(ed: Editor) -> bool:
            u = str(ed._pending_open_url or "").strip()
            if not u:
                ed._finish_open_url_confirm()
                return False
            ed._finish_open_url_confirm()
            ok = ed.open_url(u)
            if ok:
                ed.message("opened external link")
                return True
            ed.message(f"external link failed: {u}")
            return False

        def a_openurl_no(ed: Editor) -> bool:
            u = str(ed._pending_open_url or "").strip()
            ed._finish_open_url_confirm()
            if u:
                ed.message("canceled")
            return True

        def a_openurl_copy(ed: Editor) -> bool:
            u = str(ed._pending_open_url or "").strip()
            if not u:
                ed._finish_open_url_confirm()
                return False
            ed.set_clipboard_items([u], kind="items")
            ed._finish_open_url_confirm()
            ed.message(f"copied link\n{u}")
            return True

        # ---- register actions ----
        self.actions.register("InsertText", a_insert_text, doc="Insert editor.input['text'] at cursor(s)")
        self.actions.register("InsertNewline", a_insert_newline, doc="Insert newline at cursor(s)")
        self.actions.register("Backspace", a_backspace, doc="Delete char to the left")
        self.actions.register("Delete", a_delete_forward, doc="Delete char to the right")
        self.actions.register("Undo", a_undo)
        self.actions.register("Redo", a_redo)

        self.actions.register("CursorLeft", a_left)
        self.actions.register("CursorRight", a_right)
        self.actions.register("CursorUp", a_up)
        self.actions.register("CursorDown", a_down)
        self.actions.register("StartOfLine", a_start_line)
        self.actions.register("EndOfLine", a_end_line)

        self.actions.register("WordLeft", a_word_left, doc="Move left by word boundary")
        self.actions.register("WordRight", a_word_right, doc="Move right by word boundary")
        self.actions.register("PageUp", a_page_up)
        self.actions.register("PageDown", a_page_down)
        self.actions.register("DocTop", a_doc_top)
        self.actions.register("DocBottom", a_doc_bottom)

        self.actions.register("PushJump", a_push_jump, doc="Save cursor/selection state to jumplist")
        self.actions.register("JumpBack", a_jump_back, doc="Jump backward in the jumplist")
        self.actions.register("JumpForward", a_jump_forward, doc="Jump forward in the jumplist")

        self.actions.register("SelectLeft", a_select_left, doc="Extend selection left")
        self.actions.register("SelectRight", a_select_right, doc="Extend selection right")
        self.actions.register("SelectWordLeft", a_select_word_left, doc="Extend selection left by word")
        self.actions.register("SelectWordRight", a_select_word_right, doc="Extend selection right by word")
        self.actions.register("SelectUp", a_select_up, doc="Extend selection up")
        self.actions.register("SelectDown", a_select_down, doc="Extend selection down")
        self.actions.register("SelectAll", a_select_all)
        self.actions.register("ClearSelection", a_clear_selection)
        self.actions.register("FlipSelections", a_flip_selections, doc="Swap selection anchor/cursor endpoints")
        self.actions.register("EnsureSelectionsForward", a_ensure_selections_forward, doc="Ensure selection direction is forward")

        self.actions.register("Copy", a_copy)
        self.actions.register("Cut", a_cut)
        self.actions.register("Paste", a_paste)
        self.actions.register("CutLine", a_cut_line)
        self.actions.register("DuplicateLine", a_duplicate_line)
        self.actions.register("MoveLinesUp", a_move_lines_up)
        self.actions.register("MoveLinesDown", a_move_lines_down)
        self.actions.register("IndentSelection", a_indent_selection)
        self.actions.register("UnindentSelection", a_unindent_selection)

        self.actions.register("Autocomplete", a_autocomplete, doc="Autocomplete/cycle in the active prompt")
        self.actions.register("PromptCompletePrev", a_prompt_complete_prev, doc="Cycle prompt completions backward")
        self.actions.register("InsertTab", a_insert_tab)

        self.actions.register("PromptInsertText", a_prompt_insert_text, doc="Insert editor.input['text'] into the active prompt")
        self.actions.register("PromptBackspace", a_prompt_backspace, doc="Delete char left in prompt")
        self.actions.register("PromptDelete", a_prompt_delete, doc="Delete char right in prompt")
        self.actions.register("PromptLeft", a_prompt_left, doc="Move prompt cursor left")
        self.actions.register("PromptRight", a_prompt_right, doc="Move prompt cursor right")
        self.actions.register("PromptHome", a_prompt_home, doc="Move prompt cursor to start")
        self.actions.register("PromptEnd", a_prompt_end, doc="Move prompt cursor to end")

        self.actions.register("CommandMode", a_command_mode, doc="Open the command bar")
        self.actions.register("CommandPalette", a_command_palette, doc="Open the searchable command/action palette")
        self.actions.register("TopicPrompt", a_topic_prompt, doc="Open the searchable topic/help prompt")
        self.actions.register("BindingPrompt", a_binding_prompt, doc="Open the searchable binding/help prompt")
        self.actions.register("Find", a_find, doc="Open find prompt (literal)")
        self.actions.register("FindLiteral", a_find_literal, doc="Open find prompt (literal)")
        self.actions.register("FindRegex", a_find_regex, doc="Open find prompt (regex)")
        self.actions.register("FindNext", a_find_next)
        self.actions.register("FindPrevious", a_find_prev)
        self.actions.register("Escape", a_escape, doc="Close the active prompt")
        self.actions.register("SubmitPrompt", a_submit, doc="Submit active prompt")

        self.actions.register("HelpCopyLinkTarget", a_help_copy_link_target, doc="Docs browser: copy link target under cursor")
        self.actions.register("OpenUrlUnderCursor", a_open_url_under_cursor, doc="Open URL under cursor (cap.open-url; confirm)")
        self.actions.register("CopyUrlUnderCursor", a_copy_url_under_cursor, doc="Copy URL under cursor to clipboard")


        self.actions.register("QueryReplaceYes", a_qreplace_yes, doc="Query-replace: replace this match")
        self.actions.register("QueryReplaceNo", a_qreplace_no, doc="Query-replace: skip this match")
        self.actions.register("QueryReplaceAll", a_qreplace_all, doc="Query-replace: replace all remaining matches")
        self.actions.register("QueryReplaceLast", a_qreplace_last, doc="Query-replace: replace this match and quit")
        self.actions.register("QueryReplaceQuit", a_qreplace_quit, doc="Query-replace: quit")

        self.actions.register("OpenUrlYes", a_openurl_yes, doc="Open external URL (confirm mode): yes")
        self.actions.register("OpenUrlNo", a_openurl_no, doc="Open external URL (confirm mode): cancel")
        self.actions.register("OpenUrlCopy", a_openurl_copy, doc="Open external URL (confirm mode): copy")

        self.actions.register("PromptHistoryPrev", a_prompt_prev)
        self.actions.register("PromptHistoryNext", a_prompt_next)

        self.actions.register("PromptSuggestPrev", a_prompt_suggest_prev, doc="Picker prompts: move selection up")
        self.actions.register("PromptSuggestNext", a_prompt_suggest_next, doc="Picker prompts: move selection down")
        self.actions.register(
            "PromptSuggestPrevSection",
            a_prompt_suggest_prev_section,
            doc="Picker prompts: jump to start of current/previous section",
        )
        self.actions.register(
            "PromptSuggestNextSection",
            a_prompt_suggest_next_section,
            doc="Picker prompts: jump to start of next section",
        )
        self.actions.register(
            "PromptSuggestPageUp",
            a_prompt_suggest_page_up,
            doc="Picker prompts: jump selection up by a page (prompt.page)",
        )
        self.actions.register(
            "PromptSuggestPageDown",
            a_prompt_suggest_page_down,
            doc="Picker prompts: jump selection down by a page (prompt.page)",
        )
        self.actions.register("PromptCopySelected", a_prompt_copy_selected, doc="Picker prompts: copy selected row")
        self.actions.register("PromptSuggestFirst", a_prompt_suggest_first, doc="Picker prompts: jump selection to first row")
        self.actions.register("PromptSuggestLast", a_prompt_suggest_last, doc="Picker prompts: jump selection to last row")

        self.actions.register("ToggleMacro", a_toggle_macro)
        self.actions.register("PlayMacro", a_play_macro)
        self.actions.register("CancelMacro", a_cancel_macro, doc="Cancel macro recording without saving")

        self.actions.register("SpawnMultiCursorUp", a_spawn_mc_up)
        self.actions.register("SpawnMultiCursorDown", a_spawn_mc_down)
        self.actions.register("SpawnMultiCursorSelect", a_spawn_mc_select)
        self.actions.register("SpawnMultiCursor", a_spawn_mc_lines, doc="Spawn cursors at each line in selection")
        self.actions.register("RemoveMultiCursor", a_remove_mc)
        self.actions.register("RemoveAllMultiCursors", a_remove_all_mc)
        self.actions.register("SkipMultiCursor", a_skip_mc)

        self.actions.register("CyclePrimaryNext", a_cycle_primary_next)
        self.actions.register("CyclePrimaryPrev", a_cycle_primary_prev)
        self.actions.register("CollapseToPrimary", a_collapse_to_primary)

        self.actions.register("Noop", a_noop)
