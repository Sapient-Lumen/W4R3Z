from __future__ import annotations

import shlex

from dataclasses import dataclass
from pathlib import Path
import re

from micromax.regex_tools import convert_replacement_template

from .fs_sandbox import resolve_path as fs_resolve_path, is_allowed as fs_path_allowed, deny_reason as fs_deny_reason

from .buffer import Cursor
from .textpos import cursor_to_index
from typing import Callable

from micromax.vm import (
    Span,
    HookHandler,
    HookWord,
    ColonWord,
    DeferredWord,
    PrimitiveWord,
    Word,
    word_doc_summary,
    word_effect,
)

from .cmdline import CommandLine


CommandFn = Callable[["Editor", list[str]], bool]


@dataclass(frozen=True)
class Command:
    name: str
    fn: CommandFn
    doc: str = ""
    span: Span | None = None
    group: str | None = None


class CommandDispatcher:
    def __init__(self) -> None:
        self._cmds: dict[str, Command] = {}

    def register(
        self,
        name: str,
        fn: CommandFn,
        *,
        doc: str = "",
        span: Span | None = None,
        group: str | None = None,
    ) -> None:
        self._cmds[name] = Command(name=name, fn=fn, doc=doc, span=span, group=group)

    def remove(self, name: str) -> bool:
        return self._cmds.pop(name, None) is not None

    def get(self, name: str) -> Command | None:
        return self._cmds.get(name)

    def names(self) -> list[str]:
        return sorted(self._cmds.keys())

    def command_rows(self) -> list[list[object]]:
        rows: list[list[object]] = []
        for name in sorted(self._cmds.keys()):
            c = self._cmds[name]
            span = 0 if c.span is None else [c.span.filename, int(c.span.line), int(c.span.col)]
            rows.append([c.name, c.doc, c.group or 0, span])
        return rows

    def remove_group(self, group: str) -> int:
        removed = 0
        for name, c in list(self._cmds.items()):
            if c.group == group:
                del self._cmds[name]
                removed += 1
        return removed

    def groups(self) -> list[str]:
        out = sorted({str(c.group) for c in self._cmds.values() if c.group})
        return out

    def exec(self, ed: "Editor", cl: CommandLine) -> bool:
        cmd = self.get(cl.name)
        if cmd is None:
            ed.message(f"Unknown command: {cl.name}")
            return False
        try:
            return bool(cmd.fn(ed, cl.args))
        except Exception as e:
            ed.message(f"Command error: {e}")
            return False


def install_default_commands(ed: "Editor") -> None:
    """Install a micro-inspired set of command-bar commands.

    Reference: micro runtime help/commands.md (Ctrl-e command bar, help/save/quit,
    set/toggle/show, reload, etc.).
    """

    d = ed.command_dispatcher

    def _vm_word_kind(w: Word) -> str:
        if isinstance(w, PrimitiveWord):
            return "primitive"
        if isinstance(w, ColonWord):
            return "colon"
        if isinstance(w, DeferredWord):
            return "deferred"
        if isinstance(w, HookWord):
            return "hook"
        return "word"

    def _describe_vm_word(ed: "Editor", name: str) -> str | None:
        found = ed.vm.find_word_with_wid(str(name))
        if found is None:
            return None
        wid, w = found
        kind = _vm_word_kind(w)
        effect = str(word_effect(w) or "").strip()
        summary = str(word_doc_summary(w) or "").strip()
        wl = ed.vm.wordlist_names.get(int(wid), f"wl{wid}")

        parts = [f"word {name}", f"[{kind}]"]
        if effect:
            parts.append(effect)
        parts.append(f"[wl {wl}]")
        msg = " ".join(parts)
        if summary:
            msg += f": {summary}"
        sp = getattr(w, "span", None)
        if sp is not None:
            msg += f" (defined at {sp.filename}:{sp.line}:{sp.col})"
        src = ""
        before_len = len(ed.vm.stack)
        try:
            xt_src = ed.vm.find_word("xt-src")
            if isinstance(xt_src, PrimitiveWord):
                ed.vm.stack.append(w)
                xt_src.execute(ed.vm)
                src = ed.vm.pop_str()
        except Exception:
            src = ""
        finally:
            # ensure showword does not leak stack items even if tooling fails
            del ed.vm.stack[before_len:]

        if src:
            msg += "\n" + src
        return msg

    def _apropos_entry(row: list[object]) -> str:
        name = str(row[0]) if row else ""
        kind = str(row[1]) if len(row) >= 2 else ""
        menu = str(row[2]) if len(row) >= 3 else ""
        info = str(row[3]) if len(row) >= 4 else ""
        parts = [name]
        if kind:
            parts.append(f"[{kind}]")
        msg = " ".join(p for p in parts if p)
        if menu:
            msg += f" {menu}"
        if info:
            msg += f": {info}"
        return msg

    def _binding_entry(row: list[object]) -> str:
        key = str(row[0]) if row else ""
        menu = str(row[2]) if len(row) >= 3 else ""
        info = str(row[3]) if len(row) >= 4 else ""
        msg = key
        if menu:
            msg += f" {menu}"
        if info:
            msg += f": {info}"
        return msg

    def c_help(ed: "Editor", args: list[str]) -> bool:
        if not args:
            ed.message("Commands: " + ", ".join(d.names()))
            ed.message("Actions: " + ", ".join(ed.actions.names()))
            ed.message("Use: apropos QUERY, commandpick, topicpick, or helppick")
            return True

        # Explicit docs help: `help docs TOPIC`.
        if str(args[0]).casefold() in {"docs", "doc"}:
            if len(args) < 2:
                ed.message("usage: help docs TOPIC")
                return False
            doc_topic = " ".join(str(a) for a in args[1:]).strip()
            if ed.open_help_doc(doc_topic):
                return True
            ed.message(f"No doc for: {doc_topic}")
            return False

        topic = args[0]
        query = " ".join(str(a) for a in args).strip() or str(topic)
        # Minimal: help for commands/actions/visible micromax words
        if topic in d._cmds:
            c = d._cmds[topic]
            msg = (f"{topic}: {c.doc}" if c.doc else topic)
            if c.group:
                msg = msg + f" [group {c.group}]"
            if c.span is not None:
                msg = msg + f" (defined at {c.span.filename}:{c.span.line}:{c.span.col})"
            ed.message(msg)
            return True
        if ed.actions.get(topic) is not None:
            a = ed.actions.get(topic)
            ed.message(f"{topic}: {a.doc}" if a and a.doc else topic)
            return True
        vm_msg = _describe_vm_word(ed, topic)
        if vm_msg is not None:
            ed.message(vm_msg)
            return True

        # Docs fallback: if no command/action/word help matched, try opening a docs page.
        if ed.open_help_doc(query):
            return True
        matches = ed.apropos_rows(query, limit=4)
        if matches:
            preview = ", ".join(_apropos_entry(row) for row in matches[:3])
            more = max(0, len(matches) - 3)
            suffix = f" ... (+{more} more)" if more else ""
            ed.message(f"No help for: {query}. Try: {preview}{suffix}")
            return False
        ed.message(f"No help for: {query}")
        return False

    def c_helppick(ed: "Editor", args: list[str]) -> bool:
        query = " ".join(str(a) for a in args).strip()
        ed.enter_doc_prompt(query)
        return True

    def c_helpback(ed: "Editor", args: list[str]) -> bool:
        if args:
            ed.message("usage: helpback")
            return False
        return bool(ed.help_back())

    def c_helpfollow(ed: "Editor", args: list[str]) -> bool:
        if args:
            ed.message("usage: helpfollow")
            return False
        return bool(ed.help_follow())

    def c_helplinkcopy(ed: "Editor", args: list[str]) -> bool:
        if args:
            ed.message("usage: helplinkcopy")
            return False
        return bool(ed.help_copy_link_target())

    def c_urlopen(ed: "Editor", args: list[str]) -> bool:
        """Open a URL.

        - urlopen            (open URL under cursor)
        - urlopen URL        (open explicit URL)

        Opening external URLs is capability-gated by `cap.open-url` and may
        require confirmation when `open-url.confirm` is enabled.
        """

        if len(args) > 1:
            ed.message("usage: urlopen [URL]")
            return False
        if args:
            u = str(args[0] or "").strip()
            if not u:
                ed.message("usage: urlopen [URL]")
                return False
            if not bool(ed.options.get("cap.open-url")):
                ed.message(f"urlopen: disabled (cap.open-url). Enable with: set cap.open-url true\n{u}")
                return False
            if bool(ed.options.get("open-url.confirm")):
                return bool(ed.begin_open_url_confirm(u, source="command"))
            ok = ed.open_url(u)
            if ok:
                ed.message("opened url")
                return True
            ed.message(f"url open failed: {u}")
            return False
        return bool(ed.open_url_under_cursor())

    def c_urlcopy(ed: "Editor", args: list[str]) -> bool:
        """Copy a URL to clipboard.

        - urlcopy            (copy URL under cursor)
        - urlcopy URL        (copy explicit URL)
        """

        if len(args) > 1:
            ed.message("usage: urlcopy [URL]")
            return False
        if args:
            u = str(args[0] or "").strip()
            if not u:
                ed.message("usage: urlcopy [URL]")
                return False
            ed.set_clipboard_items([u], kind="items")
            ed.message(f"copied url\n{u}")
            return True
        return bool(ed.copy_url_under_cursor())

    def c_helplinkpick(ed: "Editor", args: list[str]) -> bool:
        query = " ".join(str(a) for a in args).strip()
        if not ed.current_help_doc_topic():
            ed.message("helplinkpick: not in a docs buffer")
            return False
        ed.enter_helplink_prompt(query)
        return True


    def c_helpoutlinepick(ed: "Editor", args: list[str]) -> bool:
        query = " ".join(str(a) for a in args).strip()
        if not ed.current_help_doc_topic():
            ed.message("helpoutlinepick: not in a docs buffer")
            return False
        ed.enter_helpoutline_prompt(query)
        return True


    def c_helpnavpick(ed: "Editor", args: list[str]) -> bool:
        """Pick headings + links from the current docs page."""

        query = " ".join(str(a) for a in args).strip()
        if not ed.current_help_doc_topic():
            ed.message("helpnavpick: not in a docs buffer")
            return False
        ed.enter_helpnav_prompt(query)
        return True


    def c_helpjump(ed: "Editor", args: list[str]) -> bool:
        """Jump to a heading on the current docs page (or open outline picker)."""
        if not ed.current_help_doc_topic():
            ed.message("helpjump: not in a docs buffer")
            return False
        if not args:
            ed.enter_helpoutline_prompt("")
            return True
        query = " ".join(str(a) for a in args).strip()
        if not query:
            ed.enter_helpoutline_prompt("")
            return True
        rows = ed.help_outline_rows(query, limit=1)
        if not rows:
            ed.message(f"helpjump: no heading match: {query}")
            return False
        row = rows[0]
        info = str(row[3] if len(row) > 3 else "")
        if ":" not in info:
            ed.message("helpjump: internal error (missing position)")
            return False
        try:
            line_s, col_s = info.split(":", 1)
            line1 = int(line_s, 10)
            col1 = int(col_s, 10)
        except Exception:
            ed.message("helpjump: invalid heading position")
            return False

        line0 = max(0, line1 - 1)
        col0 = max(0, col1 - 1)

        eb = ed.cur()
        ed._normalize_cursor_lists(eb)
        c = eb.cursors[eb.primary]
        new_c = eb.buf.clamp(Cursor(line0, col0))
        if (new_c.line, new_c.col) != (c.line, c.col) and bool(ed.options.get("jumplist.auto", local=eb.local_options)):
            ed.push_jump()
            eb.cursors[eb.primary] = new_c
            ed.push_jump()
            return True
        eb.cursors[eb.primary] = new_c
        return True

    def c_statusfmt(ed: "Editor", args: list[str]) -> bool:
        """Render a statusformat template and print it (debug helper)."""
        if not args:
            ed.message("usage: sfmt TEMPLATE")
            return False
        template = " ".join(str(a) for a in args)
        try:
            from .statusformat import render_status_template
            out = render_status_template(ed.status_model(), template)
        except Exception as e:
            ed.message(f"statusfmt: {e}")
            return False
        s = str(out)
        if len(s) > 200:
            s = s[:197] + "..."
        ed.message(s)
        return True

    def c_commandpick(ed: "Editor", args: list[str]) -> bool:
        query = " ".join(str(a) for a in args).strip()
        ed.enter_command_palette(query)
        return True

    def c_bind(ed: "Editor", args: list[str]) -> bool:
        if len(args) < 2:
            ed.message("usage: bind KEY ACTIONSPEC")
            return False
        key = args[0]
        spec = " ".join(args[1:])
        ed.keymap.bind(key, spec)
        ed.message(f"bound {key} -> {spec}")
        return True

    def c_bindmode(ed: "Editor", args: list[str]) -> bool:
        if len(args) < 3:
            ed.message("usage: bindmode MODE KEY ACTIONSPEC")
            return False
        mode = args[0]
        key = args[1]
        spec = " ".join(args[2:])
        ed.keymap.bind(key, spec, mode=mode)
        ed.message(f"bound {key} -> {spec} [mode {mode}]")
        return True

    def c_binddoc(ed: "Editor", args: list[str]) -> bool:
        if len(args) < 2:
            ed.message("usage: binddoc KEY DOC...")
            return False
        key = args[0]
        doc = " ".join(args[1:]).strip()
        if not ed.keymap.set_desc(key, doc):
            ed.message(f"{key}: (unbound)")
            return False
        ed.message(f"binddoc {key}: {doc}")
        return True

    def c_bindmodedoc(ed: "Editor", args: list[str]) -> bool:
        if len(args) < 3:
            ed.message("usage: bindmodedoc MODE KEY DOC...")
            return False
        mode = args[0]
        key = args[1]
        doc = " ".join(args[2:]).strip()
        if not ed.keymap.set_desc(key, doc, mode=mode):
            ed.message(f"{key}@{mode}: (unbound)")
            return False
        ed.message(f"bindmodedoc {key}@{mode}: {doc}")
        return True

    def c_unbind(ed: "Editor", args: list[str]) -> bool:
        if not args:
            ed.message("usage: unbind KEY")
            return False
        key = args[0]
        if not ed.keymap.unbind(key):
            ed.message(f"{key}: (unbound)")
            return False
        ed.message(f"unbound {key}")
        return True

    def c_unbindmode(ed: "Editor", args: list[str]) -> bool:
        if len(args) < 2:
            ed.message("usage: unbindmode MODE KEY")
            return False
        mode = args[0]
        key = args[1]
        if not ed.keymap.unbind(key, mode=mode):
            ed.message(f"{key}@{mode}: (unbound)")
            return False
        ed.message(f"unbound {key} [mode {mode}]")
        return True

    def c_bindprefix(ed: "Editor", args: list[str]) -> bool:
        if len(args) < 2:
            ed.message("usage: bindprefix KEY MODE [DOC...]")
            return False
        key = args[0]
        mode = args[1]
        doc = " ".join(args[2:]).strip() or f"prefix {mode}"
        spec = f"command:prefixmode {shlex.quote(mode)}"
        ed.keymap.bind(key, spec)
        ed.keymap.set_desc(key, doc)
        ed.message(f"bound prefix {key} -> {mode}")
        return True

    def c_bindmodeprefix(ed: "Editor", args: list[str]) -> bool:
        if len(args) < 3:
            ed.message("usage: bindmodeprefix OWNERMODE KEY MODE [DOC...]")
            return False
        owner_mode = args[0]
        key = args[1]
        mode = args[2]
        doc = " ".join(args[3:]).strip() or f"prefix {mode}"
        spec = f"command:prefixmode {shlex.quote(mode)}"
        ed.keymap.bind(key, spec, mode=owner_mode)
        ed.keymap.set_desc(key, doc, mode=owner_mode)
        ed.message(f"bound prefix {key}@{owner_mode} -> {mode}")
        return True

    def c_prefixmode(ed: "Editor", args: list[str]) -> bool:
        if not args:
            ed.message("usage: prefixmode MODE")
            return False
        mode = args[0]
        if mode in ('', '0', 'global', 'none'):
            ed.message("usage: prefixmode MODE")
            return False
        ed.push_key_mode(mode, once=True)
        # Show the currently reachable bindings immediately so prefix maps are
        # useful even in a headless/debug environment.
        ed.exec_command_line('whichkey')
        return True

    def c_showkey(ed: "Editor", args: list[str]) -> bool:
        if not args:
            ed.message("usage: showkey KEY")
            return False
        key = args[0]
        b = ed.resolve_key_binding(key)
        if b is None:
            ed.message(f"{key}: (unbound)")
            return False
        msg = f"{key} -> {b.action_spec}"
        desc = ed.binding_desc(b)
        if desc:
            msg = msg + f" [desc {desc}]"
        if b.mode and b.mode != 'global':
            msg = msg + f" [mode {b.mode}]"
        if b.group:
            msg = msg + f" [group {b.group}]"
        if b.span is not None:
            msg = msg + f" (defined at {b.span.filename}:{b.span.line}:{b.span.col})"
        ed.message(msg)
        return True

    def c_rawkeys(ed: "Editor", args: list[str]) -> bool:
        """Toggle TUI raw-key debug mode.

        When enabled, the curses TUI prints raw key events instead of
        dispatching them. This is a micro-inspired debugging tool for figuring
        out what your terminal sends for a given key combo.
        """

        if len(args) > 1:
            ed.message("usage: rawkeys [on|off]")
            return False
        cur = bool(ed.options.get('tui.rawkeys'))
        want = (not cur) if not args else None
        if want is None:
            v = str(args[0] or '').strip().casefold()
            if v in ('1', 'true', 'on', 'yes'):
                want = True
            elif v in ('0', 'false', 'off', 'no'):
                want = False
            else:
                ed.message("usage: rawkeys [on|off]")
                return False
        ed.options.set('tui.rawkeys', 'true' if want else 'false')
        ed.message(f"rawkeys: {'on' if want else 'off'} (TUI only)")
        return True

    def _fmt_binding_item(mode: str, key: str, action: str, *, once_modes: set[str] | None = None, show_mode: bool = False) -> str:
        label = str(mode)
        if once_modes and label in once_modes:
            label += '!'
        if show_mode:
            return f"{key}@{label}->{action}"
        return f"{key}->{action}"

    def c_showbindings(ed: "Editor", args: list[str]) -> bool:
        if len(args) > 1:
            ed.message("usage: showbindings [MODE|active]")
            return False
        target = args[0] if args else 'active'
        if target == 'active':
            rows = ed.available_binding_rows()
            once_modes = {str(m) for m, once in ed.active_key_mode_rows() if once}
            parts = [_fmt_binding_item(str(r[0]), str(r[1]), str(r[2]), once_modes=once_modes, show_mode=True) for r in rows]
            ed.message("bindings active: " + (", ".join(parts) if parts else '(none)'))
            return bool(rows)

        mode = None if target in ('', '0', 'global') else target
        label = 'global' if mode is None else str(mode)
        rows = ed.keymap.binding_detail_rows_for(mode)
        parts = [_fmt_binding_item(label, str(r[0]), str(r[1])) for r in rows]
        ed.message(f"bindings {label}: " + (", ".join(parts) if parts else '(none)'))
        return bool(rows)

    def c_whichkey(ed: "Editor", args: list[str]) -> bool:
        if args:
            ed.message("usage: whichkey")
            return False
        rows = ed.available_binding_info_rows()
        once_modes = {str(m) for m, once in ed.active_key_mode_rows() if once}
        parts: list[str] = []
        for mode, key, action, desc, group, span in rows:
            label = str(desc) if desc not in (0, None, '') else str(action)
            parts.append(_fmt_binding_item(str(mode), str(key), label, once_modes=once_modes, show_mode=True))
        ed.message("whichkey: " + (", ".join(parts) if parts else '(none)'))
        return bool(rows)

    def c_keymode(ed: "Editor", args: list[str]) -> bool:
        if not args:
            cur = ed.current_key_mode() or 'global'
            ed.message(f"keymode={cur}")
            return True
        mode = args[0]
        if mode in ('', '0', 'global', 'none'):
            ed.set_key_mode(None)
            ed.message('keymode=global')
            return True
        ed.set_key_mode(mode)
        ed.message(f"keymode={mode}")
        return True

    def c_pushkeymode(ed: "Editor", args: list[str]) -> bool:
        if not args:
            ed.message("usage: pushkeymode MODE")
            return False
        ed.push_key_mode(args[0])
        active = [f"{m}{'!' if once else ''}" for m, once in ed.active_key_mode_rows()] or ['global']
        ed.message("keymodes=" + ", ".join(active))
        return True

    def c_pushkeymode_once(ed: "Editor", args: list[str]) -> bool:
        if not args:
            ed.message("usage: pushkeymode-once MODE")
            return False
        ed.push_key_mode(args[0], once=True)
        active = [f"{m}{'!' if once else ''}" for m, once in ed.active_key_mode_rows()] or ['global']
        ed.message("keymodes=" + ", ".join(active))
        return True

    def c_popkeymode(ed: "Editor", args: list[str]) -> bool:
        mode = ed.pop_key_mode()
        if mode is None:
            ed.message('keymodes=global')
            return False
        active = [f"{m}{'!' if once else ''}" for m, once in ed.active_key_mode_rows()] or ['global']
        ed.message("keymodes=" + ", ".join(active))
        return True

    def c_showkeymodes(ed: "Editor", args: list[str]) -> bool:
        active_rows = ed.active_key_mode_rows()
        active = [f"{m}{'!' if once else ''}" for m, once in active_rows] or ['global']
        # Hide tiny internal modes by default to keep this human-facing output
        # focused. (They still exist and can be discovered via bindings.)
        internal = {"qreplace", "openurl", "prompt"}
        known = [m for m in ed.keymap.modes() if m not in internal and not str(m).startswith("_")]
        ed.message("active keymodes: " + ", ".join(active))
        ed.message("known keymodes: " + ", ".join(known))
        return True

    def c_showcmd(ed: "Editor", args: list[str]) -> bool:
        if not args:
            ed.message("usage: showcmd NAME")
            return False
        name = args[0]
        c = d.get(name)
        if c is None:
            ed.message(f"{name}: (unknown command)")
            return False
        msg = f"{name}: {c.doc}" if c.doc else name
        if c.group:
            msg += f" [group {c.group}]"
        if c.span is not None:
            msg += f" (defined at {c.span.filename}:{c.span.line}:{c.span.col})"
        ed.message(msg)
        return True

    def c_showword(ed: "Editor", args: list[str]) -> bool:
        if not args:
            ed.message("usage: showword NAME")
            return False
        name = args[0]
        msg = _describe_vm_word(ed, name)
        if msg is None:
            ed.message(f"{name}: (unknown word)")
            return False
        ed.message(msg)
        return True

    def c_topicpick(ed: "Editor", args: list[str]) -> bool:
        query = " ".join(args).strip()
        ed.enter_topic_prompt(query)
        return True

    def c_bindingpick(ed: "Editor", args: list[str]) -> bool:
        query = " ".join(args).strip()
        ed.enter_binding_prompt(query)
        return True

    def c_bufferpick(ed: "Editor", args: list[str]) -> bool:
        query = " ".join(args).strip()
        ed.enter_buffer_prompt(query)
        return True

    def c_pluginpick(ed: "Editor", args: list[str]) -> bool:
        query = " ".join(args).strip()
        ed.enter_plugin_prompt(query)
        return True

    def c_markpick(ed: "Editor", args: list[str]) -> bool:
        query = " ".join(args).strip()
        ed.enter_mark_prompt(query)
        return True


    def c_jumppick(ed: "Editor", args: list[str]) -> bool:
        query = " ".join(args).strip()
        ed.enter_jump_prompt(query)
        return True


    def c_apropos(ed: "Editor", args: list[str]) -> bool:
        if not args:
            ed.message("usage: apropos QUERY")
            return False
        query = " ".join(str(a) for a in args).strip()
        rows = ed.apropos_rows(query, limit=12)
        if not rows:
            ed.message(f"apropos {query}: (none)")
            return False
        preview = ", ".join(_apropos_entry(row) for row in rows[:6])
        more = max(0, len(rows) - 6)
        suffix = f" ... (+{more} more)" if more else ""
        ed.message(f"apropos {query}: {preview}{suffix}")
        return True

    def c_showhook(ed: "Editor", args: list[str]) -> bool:
        if not args:
            ed.message("usage: showhook NAME")
            return False
        name = args[0]
        w = ed.vm.find_word(name)
        if not isinstance(w, HookWord):
            ed.message(f"{name}: (not a hook)")
            return False
        parts: list[str] = []
        for h in w.handlers:
            xt = h.xt if isinstance(h, HookHandler) else h
            sp = h.span if isinstance(h, HookHandler) else None
            group = h.group if isinstance(h, HookHandler) else None
            hs = getattr(xt, "name", "<quote>")
            if group:
                hs += f"#{group}"
            if sp is not None:
                hs += f"@{sp.filename}:{sp.line}:{sp.col}"
            parts.append(hs)
        msg = f"hook {name}: {', '.join(parts) if parts else '(none)'}"
        if w.span is not None:
            msg += f" (defined at {w.span.filename}:{w.span.line}:{w.span.col})"
        ed.message(msg)
        return True

    def c_showstatus(ed: "Editor", args: list[str]) -> bool:
        if args:
            ed.message("usage: showstatus")
            return False
        ed.message(ed.status_summary())
        return True

    def c_macro(ed: "Editor", args: list[str]) -> bool:
        """Manage keyboard macros.

        Subcommands:
          - macro record [name]
          - macro stop
          - macro cancel
          - macro play [name] [count]
          - macro list
        """

        if not args:
            ed.message("usage: macro record|stop|cancel|play|list ...")
            return False

        sub = args[0]
        if sub in ("record", "rec", "start"):
            name = args[1] if len(args) >= 2 else "last"
            return bool(ed.start_macro(name))
        if sub in ("stop", "end"):
            return bool(ed.stop_macro())
        if sub in ("cancel", "abort"):
            return bool(ed.cancel_macro())
        if sub in ("play", "run"):
            name = args[1] if len(args) >= 2 else "last"
            count = 1
            if len(args) >= 3:
                try:
                    count = int(args[2], 10)
                except ValueError:
                    ed.message("macro play: count must be an int")
                    return False
            return bool(ed.play_macro(name, count=count))
        if sub in ("list", "ls"):
            ed.message("macros: " + ", ".join(ed.macro_names()))
            return True

        ed.message("unknown macro subcommand")
        return False

    def _parse_linecol(arg: str) -> tuple[int, int | None]:
        if ":" in arg:
            a, b = arg.split(":", 1)
            return int(a, 10), int(b, 10)
        return int(arg, 10), None

    def c_goto(ed: "Editor", args: list[str]) -> bool:
        if not args:
            ed.message("usage: goto line[:col]")
            return False
        line, col = _parse_linecol(args[0])
        # micro uses 1-based line numbers in UI; we accept 1-based in `goto`.
        line0 = max(0, line - 1)
        eb = ed.cur()
        ed._normalize_cursor_lists(eb)
        c = eb.cursors[eb.primary]
        new_col = c.col if col is None else max(0, col)
        new_c = eb.buf.clamp(Cursor(line0, new_col))
        if (new_c.line, new_c.col) != (c.line, c.col) and bool(ed.options.get("jumplist.auto", local=eb.local_options)):
            # Save both "from" and "to" so JumpBack can immediately return.
            ed.push_jump()
            eb.cursors[eb.primary] = new_c
            ed.push_jump()
            return True
        eb.cursors[eb.primary] = new_c
        return True

    def c_jump(ed: "Editor", args: list[str]) -> bool:
        if not args:
            ed.message("usage: jump +/-n[:col]")
            return False
        delta, col = _parse_linecol(args[0])
        eb = ed.cur()
        ed._normalize_cursor_lists(eb)
        c = eb.cursors[eb.primary]
        new_line = c.line + delta
        new_col = c.col if col is None else max(0, col)
        new_c = eb.buf.clamp(Cursor(new_line, new_col))
        if (new_c.line, new_c.col) != (c.line, c.col) and bool(ed.options.get("jumplist.auto", local=eb.local_options)):
            # Save both "from" and "to" so JumpBack can immediately return.
            ed.push_jump()
            eb.cursors[eb.primary] = new_c
            ed.push_jump()
            return True
        eb.cursors[eb.primary] = new_c
        return True

    def _convert_template(value: str) -> str:
        # Shared with the VM's regex hostcalls to avoid drift.
        return convert_replacement_template(value)

    def c_replace(ed: "Editor", args: list[str]) -> bool:
        if len(args) < 2:
            ed.message("usage: replace SEARCH VALUE [-a] [-l]")
            return False

        # Protected buffers (help/docs) should reject edits.
        try:
            if hasattr(ed, "is_protected_buffer") and ed.is_protected_buffer():
                ed.message("replace: read-only buffer")
                return False
        except Exception:
            pass
        search = args[0]
        value = args[1]
        flags = set(args[2:])
        replace_all = "-a" in flags
        literal = "-l" in flags

        eb = ed.cur()
        ignorecase = bool(ed.options.get("ignorecase", local=eb.local_options))
        before = ed._snapshot_buffer_state(eb)

        text = before[0]
        ed._normalize_cursor_lists(eb)
        start_idx = 0 if replace_all else cursor_to_index(eb.buf, eb.cursors[eb.primary])

        if literal:
            if replace_all:
                if not ignorecase:
                    if search not in text:
                        return False
                    new = text.replace(search, value)
                else:
                    # Case-insensitive literal replace-all: use a regex with a literal pattern
                    # and a lambda replacement to avoid backslash expansion surprises.
                    pat_lit = re.compile(re.escape(search), re.IGNORECASE)
                    new, n = pat_lit.subn(lambda _m: value, text)
                    if n == 0:
                        return False
            else:
                if not ignorecase:
                    i = text.find(search, start_idx)
                else:
                    hay_l = text.lower()
                    needle_l = search.lower()
                    i = hay_l.find(needle_l, start_idx)
                if i < 0:
                    return False
                new = text[:i] + value + text[i + len(search) :]
        else:
            try:
                flags_re = re.IGNORECASE if ignorecase else 0
                pat = re.compile(search, flags_re)
            except re.error as e:
                ed.message(f"invalid regex: {e}")
                return False
            repl_py = _convert_template(value)
            if replace_all:
                new, n = pat.subn(repl_py, text)
                if n == 0:
                    return False
            else:
                m = pat.search(text, pos=start_idx)
                if m is None:
                    return False
                new = text[: m.start()] + m.expand(repl_py) + text[m.end() :]

        eb.buf.set_text(new)
        after = ed._snapshot_buffer_state(eb)
        ed._record_undo_snapshot(eb, before, after, "replace")
        return True

    def c_replaceall(ed: "Editor", args: list[str]) -> bool:
        # micro has replaceall as a convenience wrapper for replace -a.
        if len(args) < 2:
            ed.message("usage: replaceall SEARCH VALUE [-l]")
            return False
        return c_replace(ed, [args[0], args[1], "-a", *args[2:]])

    def c_qreplace(ed: "Editor", args: list[str]) -> bool:
        """Interactive (confirming) replace loop.

        This mirrors micro's "replace then confirm" workflow: it finds matches
        from the cursor and asks the user to confirm each replacement.
        """
        if len(args) < 2:
            ed.message("usage: qreplace SEARCH VALUE [-l]")
            return False
        flags = set(args[2:])
        literal = "-l" in flags
        return bool(ed.begin_query_replace(args[0], args[1], literal=literal))

    def c_open(ed: "Editor", args: list[str]) -> bool:
        if not args:
            ed.message("usage: open FILENAME")
            return False

        raw = str(args[0] or "")

        # When a script executes commands (via `ed.command` / prompt-submit), we
        # enforce the same filesystem capability gates as `ed.open`.
        if hasattr(ed, "in_script_context") and ed.in_script_context():
            if not bool(ed.options.get("cap.fs-open")):
                ed.message("open: disabled for scripts (cap.fs-open)")
                return False
            try:
                raw_path, initial_cursor = ed._parse_open_target(raw)
                p = fs_resolve_path(ed, raw_path)
                if not fs_path_allowed(ed, p):
                    ed.message("open: " + fs_deny_reason(ed, p))
                    return False
                return bool(ed.open_file(str(p), initial_cursor=initial_cursor))
            except Exception as e:
                ed.message(f"open: {e}")
                return False

        # Interactive open: keep the normal editor UX (unrestricted by caps).
        try:
            return bool(ed.open_file(raw))
        except Exception as e:
            ed.message(f"open: {e}")
            return False

    def c_save(ed: "Editor", args: list[str]) -> bool:
        # When a script executes commands (via `ed.command` / prompt-submit), we
        # enforce the same filesystem capability gates as `ed.save`.
        if hasattr(ed, "in_script_context") and ed.in_script_context():
            if not bool(ed.options.get("cap.fs-save")):
                ed.message("save: disabled for scripts (cap.fs-save)")
                return False

            # Resolve/validate the intended target before mutating buffer metadata.
            eb0 = ed.cur()
            raw_target = str(args[0] if args else (eb0.buf.path or "")).strip()
            if not raw_target:
                ed.message("save: buffer has no path")
                return False
            p0 = fs_resolve_path(ed, raw_target)
            if not fs_path_allowed(ed, p0):
                ed.message("save: " + fs_deny_reason(ed, p0))
                return False

            # If save-as, update buffer identity using the resolved path.
            if args:
                eb = eb0
                old = eb.name
                ed._update_buffer_path(eb, str(p0))
                # Keep marks stable if the buffer is retitled.
                if not ed.rename_buffer(old, str(p0)):
                    eb.name = str(p0)
                    ed._activate_buffer(eb.name)

            try:
                ed.save()
            except Exception as e:
                ed.message(f"save: {e}")
                return False
            ed.message("saved")
            return True

        # Interactive save: normal editor behavior.
        if args:
            # save as
            p = Path(args[0])
            eb = ed.cur()
            old = eb.name
            ed._update_buffer_path(eb, str(p))
            # keep marks stable if the buffer is retitled
            if not ed.rename_buffer(old, str(p)):
                eb.name = str(p)
                ed._activate_buffer(eb.name)
        try:
            ed.save()
        except Exception as e:
            ed.message(f"save: {e}")
            return False
        ed.message("saved")
        return True

    def c_saveas(ed: "Editor", args: list[str]) -> bool:
        """saveas FILE - save current buffer under a new path (alias for `save FILE`)."""
        if not args:
            ed.message("usage: saveas FILE")
            return False
        return c_save(ed, args)

    def c_close(ed: "Editor", args: list[str]) -> bool:
        """close [NAME] [-f] - close a buffer (default: current).

        If the buffer is dirty, `close` uses a double-tap safety guard
        (mirroring `quit`). Use `close -f` / `close!` to force.
        """
        force = any(str(a) in {"-f", "!", "--force"} for a in args)
        # Optional explicit buffer name (first non-flag arg).
        name = None
        for a in args:
            if str(a) in {"-f", "!", "--force"}:
                continue
            name = str(a)
            break
        ok = ed.close_buffer(name, force=force)
        if ok:
            ed.message("closed" + (f" {name}" if name else ""))
            return True
        # When not ok, close_buffer will have emitted a warning message if dirty.
        if name and name not in ed.buffers:
            ed.message(f"no such buffer: {name}")
        return False

    def c_closeall(ed: "Editor", args: list[str]) -> bool:
        """closeall [-f|!] - close all buffers.

        Mirrors `quit`/`close` dirty-buffer safety: when any buffers are dirty,
        closeall arms once and only proceeds on a second attempt (or with -f/!).
        """
        force = any(str(a) in {"-f", "!", "--force"} for a in args)
        targets = list(ed.buffers.keys())
        dirty = [n for n in targets if bool(ed.buffers.get(n).buf.dirty)]
        if dirty and not force:
            if getattr(ed, "_closeall_armed", False):
                pass
            else:
                ed._closeall_armed = True
                preview = ", ".join(sorted(dirty)[:6])
                more = max(0, len(dirty) - 6)
                suffix = f" ... (+{more} more)" if more else ""
                ed.message(f"unsaved changes in: {preview}{suffix}; run `closeall` again or `closeall -f` to force")
                return False
        ed._closeall_armed = False
        try:
            ed.close_buffers(targets)
        except Exception as e:
            ed.message(f"closeall error: {e}")
            return False
        ed.message("closed all")
        return True

    def c_only(ed: "Editor", args: list[str]) -> bool:
        """only [-f|!] - close all buffers except the current one."""
        force = any(str(a) in {"-f", "!", "--force"} for a in args)
        keep = str(ed.active or "")
        targets = [n for n in list(ed.buffers.keys()) if n != keep]
        dirty = [n for n in targets if bool(ed.buffers.get(n).buf.dirty)]
        if dirty and not force:
            if getattr(ed, "_only_armed", False):
                pass
            else:
                ed._only_armed = True
                preview = ", ".join(sorted(dirty)[:6])
                more = max(0, len(dirty) - 6)
                suffix = f" ... (+{more} more)" if more else ""
                ed.message(f"unsaved changes in: {preview}{suffix}; run `only` again or `only -f` to force")
                return False
        ed._only_armed = False
        try:
            ed.close_buffers(targets, keep=keep)
        except Exception as e:
            ed.message(f"only error: {e}")
            return False
        ed.message("only: closed others")
        return True

    def c_prevbuf(ed: "Editor", args: list[str]) -> bool:
        """prevbuf - switch to the previous (MRU) buffer."""
        if args:
            ed.message("usage: prevbuf")
            return False
        name = ""
        try:
            name = str(ed.previous_buffer_name() or "")
        except Exception:
            name = ""
        if not name:
            ed.message("prevbuf: (none)")
            return False
        if not ed.switch_buffer(name):
            ed.message("prevbuf: (none)")
            return False
        ed.message(f"prevbuf: {name}")
        return True

    def c_recent(ed: "Editor", args: list[str]) -> bool:
        """recent [N|clear] - show or open recent files.

        - `recent` shows the MRU list (up to 12).
        - `recent N` opens the Nth entry (1-based).
        - `recent clear` clears the list.
        """
        if not args:
            xs = list(getattr(ed, 'recent_files', []))
            if not xs:
                ed.message('recent: (none)')
                return True
            show = xs[:12]
            parts = [f"{i+1}:{p}" for i,p in enumerate(show)]
            more = max(0, len(xs) - len(show))
            suffix = f" ... (+{more} more)" if more else ''
            ed.message('recent: ' + '; '.join(parts) + suffix)
            return True
        if str(args[0]) == 'clear':
            ed.clear_recent_files()
            ed.message('recent cleared')
            return True
        # open nth
        try:
            n = int(str(args[0]), 10)
        except Exception:
            ed.message('usage: recent [N|clear]')
            return False
        xs = list(getattr(ed, 'recent_files', []))
        if n <= 0 or n > len(xs):
            ed.message(f"recent: out of range: {n}")
            return False
        return ed.exec_command_line('open ' + shlex.quote(xs[n-1]))

    def c_recentpick(ed: "Editor", args: list[str]) -> bool:
        q = str(args[0]) if args else ''
        ed.enter_recent_prompt(q)
        return True



    def c_buffers(ed: "Editor", args: list[str]) -> bool:
        if args:
            ed.message("usage: buffers")
            return False
        names = ed.buffer_names()
        ed.message("buffers: " + (", ".join(names) if names else "(none)"))
        return True

    def c_buffer(ed: "Editor", args: list[str]) -> bool:
        if not args:
            ed.message("usage: buffer NAME")
            return False
        name = str(args[0])
        if not ed.switch_buffer(name):
            ed.message(f"no such buffer: {name}")
            return False
        ed.message(f"buffer: {name}")
        return True

    def c_mark(ed: "Editor", args: list[str]) -> bool:
        if not args:
            ed.message("usage: mark NAME")
            return False
        name = str(args[0])
        if not ed.mark_set(name):
            ed.message("mark: invalid name")
            return False
        ed.message(f"mark set: {name}")
        return True

    def c_markjump(ed: "Editor", args: list[str]) -> bool:
        if not args:
            ed.message("usage: markjump NAME")
            return False
        name = str(args[0])
        if not ed.mark_jump(name):
            ed.message(f"markjump: unknown mark {name}")
            return False
        ed.message(f"markjumped: {name}")
        return True

    def c_marks(ed: "Editor", args: list[str]) -> bool:
        if args:
            ed.message("usage: marks")
            return False
        rows = ed.mark_rows()
        if not rows:
            ed.message("marks: (none)")
            return True
        parts = [f"{n} -> {b}:{l}:{c}" for n, b, l, c in rows]
        ed.message("marks: " + "; ".join(parts))
        return True

    def c_quit(ed: "Editor", args: list[str]) -> bool:
        """Quit the editor.

        If any buffers are dirty, `quit` arms once (prints a warning) and only
        quits on a second attempt or when forced.

        Force forms:
          - quit -f
          - quit !
          - quit! (alias)
        """

        force = any(str(a) in {"-f", "!", "--force"} for a in args)
        dirty = [name for name, eb in ed.buffers.items() if bool(eb.buf.dirty)]
        if dirty and not force:
            try:
                ed.autosave_dirty_buffers(immediate=True)
            except Exception:
                pass
            dirty = [name for name, eb in ed.buffers.items() if bool(eb.buf.dirty)]
        if dirty and not force:
            if getattr(ed, "_quit_armed", False):
                ed.should_quit = True
                return True
            ed._quit_armed = True
            preview = ", ".join(sorted(dirty)[:6])
            more = max(0, len(dirty) - 6)
            suffix = f" ... (+{more} more)" if more else ""
            ed.message(f"unsaved changes in: {preview}{suffix}; run `quit` again or `quit -f` to force")
            return False

        ed.should_quit = True
        return True

    def c_pwd(ed: "Editor", args: list[str]) -> bool:
        ed.message(str(Path.cwd()))
        return True

    def c_cd(ed: "Editor", args: list[str]) -> bool:
        if not args:
            ed.message("usage: cd PATH")
            return False
        import os

        raw = str(args[0] or "").strip()
        if not raw:
            ed.message("usage: cd PATH")
            return False

        p = Path(raw).expanduser()
        try:
            p = p.resolve()
        except Exception:
            try:
                p = p.absolute()
            except Exception:
                pass

        try:
            os.chdir(str(p))
        except Exception as e:
            ed.message(f"cd: {e}")
            return False
        ed.message(str(Path.cwd()))
        return True

    def c_set(ed: "Editor", args: list[str]) -> bool:
        if len(args) < 2:
            ed.message("usage: set OPTION VALUE")
            return False
        name = args[0]
        raw = " ".join(args[1:])
        val = ed.options.set(name, raw)
        if str(ed.options.resolve_name(str(name))) == "fastdirty":
            try:
                ed._sync_all_buffer_fastdirty_modes()
            except Exception:
                pass
        if str(name).startswith("cap."):
            try:
                ed.refresh_capabilities()
            except Exception:
                pass
        ed.message(f"{name}={val}")
        return True

    def c_setlocal(ed: "Editor", args: list[str]) -> bool:
        if len(args) < 2:
            ed.message("usage: setlocal OPTION VALUE")
            return False
        name = args[0]
        raw = " ".join(args[1:])
        val = ed.options.set(name, raw, local=ed.cur().local_options)
        if str(ed.options.resolve_name(str(name))) == "fastdirty":
            try:
                ed._sync_all_buffer_fastdirty_modes()
            except Exception:
                pass
        ed.message(f"{name}(local)={val}")
        return True

    def c_show(ed: "Editor", args: list[str]) -> bool:
        if not args:
            # list
            for spec in ed.options.list_specs():
                ed.message(f"{spec.name}={ed.options.get(spec.name)}")
            return True
        name = args[0]
        val = ed.options.get(name, local=ed.cur().local_options)
        ed.message(f"{name}={val}")
        return True

    def c_toggle(ed: "Editor", args: list[str]) -> bool:
        if not args:
            ed.message("usage: toggle OPTION")
            return False
        name = args[0]
        val = ed.options.toggle(name)
        if str(ed.options.resolve_name(str(name))) == "fastdirty":
            try:
                ed._sync_all_buffer_fastdirty_modes()
            except Exception:
                pass
        if str(name).startswith("cap."):
            try:
                ed.refresh_capabilities()
            except Exception:
                pass
        ed.message(f"{name}={val}")
        return True

    def c_togglelocal(ed: "Editor", args: list[str]) -> bool:
        if not args:
            ed.message("usage: togglelocal OPTION")
            return False
        name = args[0]
        val = ed.options.toggle(name, local=ed.cur().local_options)
        if str(ed.options.resolve_name(str(name))) == "fastdirty":
            try:
                ed._sync_all_buffer_fastdirty_modes()
            except Exception:
                pass
        ed.message(f"{name}(local)={val}")
        return True

    def c_reload(ed: "Editor", args: list[str]) -> bool:
        return ed.reload_runtime()

    def c_plugin(ed: "Editor", args: list[str]) -> bool:
        if not args:
            ed.message("usage: plugin list|reload NAME|info NAME|errors [NAME]")
            return False
        sub = args[0]
        if sub == "list":
            pm = ed.plugin_manager
            names = sorted(pm.plugins.keys()) if pm else []
            ed.message("plugins: " + (", ".join(names) if names else "(none)"))
            if pm and pm.load_errors:
                # Show captured non-fatal load/dep errors (best-effort).
                for n, err in pm.load_errors[-10:]:
                    ed.message(f"plugin error: {n}: {err}")
            return True
        if sub == "reload" and len(args) >= 2:
            if not ed.plugin_manager:
                ed.message("no plugin manager")
                return False
            try:
                ed.plugin_manager.reload(args[1])
            except Exception as e:
                ed.message(f"plugin reload error: {args[1]}: {e}")
                return False
            ed.message(f"reloaded {args[1]}")
            return True
        if sub == "errors":
            pm = ed.plugin_manager
            if not pm:
                ed.message("no plugin manager")
                return False
            flt = args[1] if len(args) >= 2 else ""
            errs = [(n, e) for (n, e) in getattr(pm, "load_errors", []) if (not flt or str(n) == str(flt))]
            if not errs:
                ed.message("plugin errors: (none)")
                return True
            for n, err in errs[-50:]:
                ed.message(f"plugin error: {n}: {err}")
            return True
        if sub == "info" and len(args) >= 2:
            pm = ed.plugin_manager
            if not pm:
                ed.message("no plugin manager")
                return False
            name = args[1]
            loaded = bool(name in getattr(pm, "plugins", {}))
            ed.message(f"plugin {name}: {'loaded' if loaded else 'not loaded'}")
            cand = getattr(pm, "candidates", {}).get(name) if hasattr(pm, "candidates") else None
            version = ""
            desc = ""
            reqs: list[str] = []
            entry = ""
            root = ""
            try:
                if cand is not None:
                    version = str(cand.meta.version or "")
                    desc = str(cand.meta.description or "")
                    reqs = list(cand.meta.requires or [])
                    entry = str(cand.meta.entry or "")
                    root = str(cand.root)
                elif loaded:
                    pl = pm.plugins.get(name)
                    if pl is not None:
                        root = str(pl.root)
                        meta = pl.meta or {}
                        version = str(meta.get("version") or "")
                        desc = str(meta.get("description") or "")
                        entry = str(meta.get("entry") or "")
                        reqs = list(meta.get("requires") or [])
            except Exception:
                pass
            if version:
                ed.message(f"  version: {version}")
            if entry:
                ed.message(f"  entry: {entry}")
            if root:
                ed.message(f"  root: {root}")
            if desc:
                ed.message(f"  desc: {desc}")
            if reqs:
                ed.message("  requires: " + ", ".join(reqs))
                for dep in reqs:
                    dep_loaded = bool(dep in getattr(pm, "plugins", {}))
                    ed.message(f"    - {dep}: {'loaded' if dep_loaded else 'missing'}")
            errs = [e for (n, e) in getattr(pm, "load_errors", []) if str(n) == str(name)]
            if errs:
                ed.message(f"  errors: {len(errs)} (last: {errs[-1]})")
            return True
        ed.message("usage: plugin list|reload NAME|info NAME|errors [NAME]")
        return False

    d.register("help", c_help, doc="help [topic] - show help for commands/actions")
    d.register("helppick", c_helppick, doc="helppick [QUERY] - open searchable docs picker")
    d.register("helpback", c_helpback, doc="helpback - go back in docs help navigation")
    d.register("helpfollow", c_helpfollow, doc="helpfollow - follow a markdown link under cursor in docs help")
    d.register("helplinkcopy", c_helplinkcopy, doc="helplinkcopy - copy markdown link target under cursor in docs help")
    d.register("helpcopylink", c_helplinkcopy, doc="helpcopylink - alias for helplinkcopy")
    d.register("helplinkpick", c_helplinkpick, doc="helplinkpick [QUERY] - pick a link from the current docs page")
    d.register("helpoutlinepick", c_helpoutlinepick, doc="helpoutlinepick [QUERY] - pick a heading from the current docs page")
    d.register("helpnavpick", c_helpnavpick, doc="helpnavpick [QUERY] - pick a heading or link from the current docs page")
    d.register("helpjump", c_helpjump, doc="helpjump [QUERY] - jump to a heading on the current docs page")
    d.register("urlopen", c_urlopen, doc="urlopen [URL] - open URL under cursor (or explicit URL) [cap.open-url]")
    d.register("openurl", c_urlopen, doc="openurl [URL] - alias for urlopen")
    d.register("urlcopy", c_urlcopy, doc="urlcopy [URL] - copy URL under cursor (or explicit URL)")

    d.register("sfmt", c_statusfmt, doc="sfmt TEMPLATE - render a statusformat template (debug)")
    d.register("commandpick", c_commandpick, doc="commandpick [QUERY] - open searchable command/action palette")
    d.register("topicpick", c_topicpick, doc="topicpick [QUERY] - open searchable topic/help prompt")
    d.register("bindingpick", c_bindingpick, doc="bindingpick [QUERY] - open searchable current-binding prompt")
    d.register("bufferpick", c_bufferpick, doc="bufferpick [QUERY] - open searchable buffer picker")
    d.register("pluginpick", c_pluginpick, doc="pluginpick [QUERY] - open searchable plugin picker")
    d.register("markpick", c_markpick, doc="markpick [QUERY] - open searchable mark picker")
    d.register("jumppick", c_jumppick, doc="jumppick [QUERY] - open searchable jumplist picker")
    d.register("apropos", c_apropos, doc="apropos QUERY - search commands/actions/words by name")
    d.register("bind", c_bind, doc="bind KEY ACTIONSPEC - bind a global key")
    d.register("bindmode", c_bindmode, doc="bindmode MODE KEY ACTIONSPEC - bind a key in a mode")
    d.register("bindprefix", c_bindprefix, doc="bindprefix KEY MODE [DOC...] - bind a prefix key that enters a one-shot mode")
    d.register("bindmodeprefix", c_bindmodeprefix, doc="bindmodeprefix OWNERMODE KEY MODE [DOC...] - bind a mode-local prefix key that enters a one-shot mode")
    d.register("binddoc", c_binddoc, doc="binddoc KEY DOC... - attach a keybinding description")
    d.register("bindmodedoc", c_bindmodedoc, doc="bindmodedoc MODE KEY DOC... - attach a mode-keybinding description")
    d.register("unbind", c_unbind, doc="unbind KEY - remove a global key binding")
    d.register("unbindmode", c_unbindmode, doc="unbindmode MODE KEY - remove a mode-specific binding")
    d.register("keymode", c_keymode, doc="keymode [MODE|global] - show/set active key mode")
    d.register("pushkeymode", c_pushkeymode, doc="pushkeymode MODE - push an active key mode")
    d.register("pushkeymode-once", c_pushkeymode_once, doc="pushkeymode-once MODE - push a one-shot key mode")
    d.register("prefixmode", c_prefixmode, doc="prefixmode MODE - enter a one-shot prefix mode and show reachable bindings")
    d.register("popkeymode", c_popkeymode, doc="popkeymode - pop the active key mode")
    d.register("showkeymodes", c_showkeymodes, doc="showkeymodes - show active and known key modes")
    d.register("showkey", c_showkey, doc="showkey KEY - show resolved binding for key")
    d.register("rawkeys", c_rawkeys, doc="rawkeys [on|off] - TUI raw key debugging (print key events instead of dispatching)")
    d.register("showbindings", c_showbindings, doc="showbindings [MODE|active] - show discoverable bindings")
    d.register("whichkey", c_whichkey, doc="whichkey - show currently available bindings with descriptions")
    d.register("showcmd", c_showcmd, doc="show command docs/provenance")
    d.register("showword", c_showword, doc="showword NAME - show visible micromax word docs/effect/provenance")
    d.register("showhook", c_showhook, doc="showhook NAME - show installed hook handlers")
    d.register("showstatus", c_showstatus, doc="showstatus - show portable statusline summary")
    d.register("macro", c_macro, doc="macro record|stop|cancel|play|list - keyboard macros")
    d.register("goto", c_goto, doc="goto line[:col] - go to absolute line")
    d.register("jump", c_jump, doc="jump +/-n[:col] - move relative lines")
    d.register("replace", c_replace, doc="replace SEARCH VALUE [-a] [-l] - replace (regex by default)")
    d.register("replaceall", c_replaceall, doc="replaceall SEARCH VALUE [-l] - replace all occurrences")
    d.register("qreplace", c_qreplace, doc="qreplace SEARCH VALUE [-l] - interactive confirming replace")
    d.register("queryreplace", c_qreplace, doc="queryreplace SEARCH VALUE [-l] - alias for qreplace")
    d.register("open", c_open, doc="open FILE - open file")
    d.register("save", c_save, doc="save [FILE] - save (optionally save as)")
    d.register("saveas", c_saveas, doc="saveas FILE - save as")
    d.register("close", c_close, doc="close [NAME] [-f] - close a buffer")
    d.register("closeall", c_closeall, doc="closeall [-f] - close all buffers")
    d.register("closeall!", c_closeall, doc="closeall! - force close all buffers")
    d.register("only", c_only, doc="only [-f] - close all other buffers")
    d.register("only!", c_only, doc="only! - force close other buffers")
    d.register("prevbuf", c_prevbuf, doc="prevbuf - switch to previous buffer")
    d.register("close!", c_close, doc="close! - force close a buffer")
    d.register("recent", c_recent, doc="recent [N|clear] - show/open recent files")
    d.register("recentpick", c_recentpick, doc="recentpick [QUERY] - open searchable recent file picker")

    d.register("buffers", c_buffers, doc="buffers - list open buffers")
    d.register("buffer", c_buffer, doc="buffer NAME - switch active buffer")
    d.register("mark", c_mark, doc="mark NAME - set a named mark at the primary cursor")
    d.register("markjump", c_markjump, doc="markjump NAME - jump to a named mark")
    d.register("marks", c_marks, doc="marks - list marks")

    d.register("quit", c_quit, doc="quit - request editor quit")
    d.register("quit!", c_quit, doc="quit! - force quit (no warning)")
    d.register("pwd", c_pwd, doc="pwd - show current directory")
    d.register("cd", c_cd, doc="cd PATH - change directory")
    d.register("set", c_set, doc="set OPTION VALUE")
    d.register("setlocal", c_setlocal, doc="setlocal OPTION VALUE")
    d.register("show", c_show, doc="show [OPTION] - show option(s)")
    d.register("toggle", c_toggle, doc="toggle OPTION")
    d.register("togglelocal", c_togglelocal, doc="togglelocal OPTION")
    d.register("reload", c_reload, doc="reload - reload runtime/plugins")
    d.register("plugin", c_plugin, doc="plugin list|reload NAME")
