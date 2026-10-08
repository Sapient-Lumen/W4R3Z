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
    HookWord,
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
            ed.message(f"command: no such command: {cl.name}")
            return False
        try:
            return bool(cmd.fn(ed, cl.args))
        except Exception as e:
            ed.message(f"command {cl.name}: error: {e}")
            return False


def install_default_commands(ed: "Editor") -> None:
    """Install a micro-inspired set of command-bar commands.

    Reference: micro runtime help/commands.md (Ctrl-e command bar, help/save/quit,
    set/toggle/show, reload, etc.).
    """

    d = ed.command_dispatcher

    def _format_command_detail_row(row: list[object]) -> str:
        name = str(row[0]) if row else ""
        doc = str(row[1]) if len(row) >= 2 else ""
        group = row[2] if len(row) >= 3 else 0
        span = row[3] if len(row) >= 4 else 0
        msg = f"{name}: {doc}" if doc else name
        if group not in (0, ""):
            msg += f" [group {group}]"
        if isinstance(span, list) and len(span) >= 3:
            msg += f" (defined at {span[0]}:{span[1]}:{span[2]})"
        return msg

    def _describe_command(ed: "Editor", name: str) -> str | None:
        row = ed.command_detail_row(str(name))
        if row is None:
            return None
        return _format_command_detail_row(list(row))

    def _format_action_detail_row(row: list[object]) -> str:
        name = str(row[0]) if row else ""
        doc = str(row[1]) if len(row) >= 2 else ""
        span = row[2] if len(row) >= 3 else 0
        msg = f"action {name}: {doc}" if doc else f"action {name}"
        if isinstance(span, list) and len(span) >= 3:
            msg += f" (defined at {span[0]}:{span[1]}:{span[2]})"
        return msg

    def _describe_action(ed: "Editor", name: str) -> str | None:
        row = ed.action_detail_row(str(name))
        if row is None:
            return None
        return _format_action_detail_row(list(row))

    def _format_word_detail_row(row: list[object]) -> str:
        name = str(row[0]) if row else ""
        kind = str(row[1]) if len(row) >= 2 else "word"
        effect = str(row[2]) if len(row) >= 3 else ""
        wl = str(row[3]) if len(row) >= 4 else ""
        summary = str(row[4]) if len(row) >= 5 else ""
        span = row[5] if len(row) >= 6 else 0
        src = row[6] if len(row) >= 7 else 0
        parts = [f"word {name}", f"[{kind}]"]
        if effect:
            parts.append(effect)
        if wl:
            parts.append(f"[wl {wl}]")
        msg = " ".join(parts)
        if summary:
            msg += f": {summary}"
        if isinstance(span, list) and len(span) >= 3:
            msg += f" (defined at {span[0]}:{span[1]}:{span[2]})"
        if src not in (0, ""):
            msg += "\n" + str(src)
        return msg

    def _describe_vm_word(ed: "Editor", name: str) -> str | None:
        row = ed.word_detail_row(str(name))
        if row is None:
            return None
        return _format_word_detail_row(list(row))

    def _format_doc_detail_row(row: list[object]) -> str:
        topic = str(row[0]) if row else ""
        title = str(row[1]) if len(row) >= 2 else ""
        summary = str(row[2]) if len(row) >= 3 else ""
        section = str(row[3]) if len(row) >= 4 else ""
        path = str(row[4]) if len(row) >= 5 else ""
        try:
            p = Path(path).expanduser()
            if p.is_absolute():
                try:
                    path = str(p.relative_to(Path.cwd()))
                except Exception:
                    path = str(p)
        except Exception:
            pass
        msg = f"doc {topic}: {title}" if title else f"doc {topic}"
        if section:
            msg += f" [{section}]"
        if summary:
            msg += f" — {summary}"
        if path:
            msg += f" ({path})"
        return msg

    def _describe_doc(ed: "Editor", name: str) -> str | None:
        row = ed.doc_detail_row(str(name))
        if row is None:
            return None
        return _format_doc_detail_row(list(row))

    def _format_help_heading_detail_row(row: list[object], *, prefix: str = "helpheading") -> str:
        topic = str(row[0]) if row else ""
        title = str(row[1]) if len(row) >= 2 else ""
        frag = str(row[2]) if len(row) >= 3 else ""
        level = int(row[3]) if len(row) >= 4 else 0
        line = int(row[4]) if len(row) >= 5 else 0
        col = int(row[5]) if len(row) >= 6 else 0
        section = str(row[6]) if len(row) >= 7 else ""
        head = f"{prefix} {title}" if title else str(prefix)
        if topic:
            head += f" @{topic}"
        msg = head
        if level > 0:
            msg += f" [h{level}]"
        if section:
            msg += f" [section {section}]"
        if frag:
            msg += f" [#{frag}]"
        if line > 0 and col > 0:
            msg += f" @ {line}:{col}"
        return msg

    def _describe_help_heading(ed: "Editor", query: str) -> str | None:
        row = ed.help_heading_detail_row(str(query))
        if row is None:
            return None
        return _format_help_heading_detail_row(list(row), prefix="helpjump")

    def _describe_current_help_heading(ed: "Editor") -> str | None:
        row = ed.current_help_heading_detail_row()
        if row is None:
            return None
        return _format_help_heading_detail_row(list(row), prefix="helpheading")

    def _format_help_link_detail_row(row: list[object]) -> str:
        topic = str(row[0]) if row else ""
        label = str(row[1]) if len(row) >= 2 else ""
        target = str(row[2]) if len(row) >= 3 else ""
        kind = str(row[3]) if len(row) >= 4 else ""
        line = int(row[4]) if len(row) >= 5 else 0
        col = int(row[5]) if len(row) >= 6 else 0
        section = str(row[6]) if len(row) >= 7 else ""
        head = f"helplink {label}" if label else "helplink"
        if topic:
            head += f" @{topic}"
        msg = head
        if kind:
            msg += f" [{kind}]"
        if section:
            msg += f" [section {section}]"
        if target:
            msg += f" -> {target}"
        if line > 0 and col > 0:
            msg += f" @ {line}:{col}"
        return msg

    def _describe_current_help_link(ed: "Editor") -> str | None:
        row = ed.help_link_detail_row()
        if row is None:
            return None
        return _format_help_link_detail_row(list(row))

    def _format_option_detail_row(row: list[object]) -> str:
        query = str(row[0]) if row else ""
        canonical = str(row[1]) if len(row) >= 2 else query
        value = str(row[2]) if len(row) >= 3 else ""
        default = str(row[3]) if len(row) >= 4 else ""
        kind = str(row[4]) if len(row) >= 5 else "option"
        try:
            local_override = int(row[5]) if len(row) >= 6 else 0
        except Exception:
            local_override = 0
        doc = str(row[6]) if len(row) >= 7 else ""
        msg = f"option {query}" if query else "option"
        if canonical and canonical != query:
            msg += f" -> {canonical}"
        if kind:
            msg += f" [{kind}]"
        msg += f" value={value} default={default}"
        if local_override:
            msg += " (local)"
        if doc:
            msg += f": {doc}"
        return msg

    def _describe_option(ed: "Editor", name: str) -> str | None:
        row = ed.option_detail_row(str(name))
        if row is None:
            return None
        return _format_option_detail_row(list(row))

    def _format_buffer_detail_row(ed: "Editor", row: list[object]) -> str:
        name = str(row[0]) if row else ""
        position = str(row[1]) if len(row) >= 2 else ""
        try:
            active = int(row[2]) if len(row) >= 3 else 0
        except Exception:
            active = 0
        try:
            dirty = int(row[3]) if len(row) >= 4 else 0
        except Exception:
            dirty = 0
        try:
            readonly = int(row[4]) if len(row) >= 5 else 0
        except Exception:
            readonly = 0
        section = str(row[5]) if len(row) >= 6 else ""
        path = str(row[6]) if len(row) >= 7 else ""
        try:
            line_count = int(row[7]) if len(row) >= 8 else 0
        except Exception:
            line_count = 0
        parts = [f"buffer {name}"]
        flags: list[str] = []
        if active:
            flags.append("active")
        if dirty:
            flags.append("dirty")
        if readonly:
            flags.append("readonly")
        if flags:
            parts.append(f"[{', '.join(flags)}]")
        if position:
            parts.append(f"@ {position}")
        msg = " ".join(parts)
        extras: list[str] = []
        if section:
            extras.append(f"section={section}")
        if path:
            extras.append(path)
        if line_count > 0:
            extras.append(ed._count_label(line_count, 'line'))
        if extras:
            msg += " — " + " | ".join(extras)
        return msg

    def _describe_buffer(ed: "Editor", name: str) -> str | None:
        row = ed.buffer_detail_row(str(name))
        if row is None:
            return None
        return _format_buffer_detail_row(ed, list(row))

    def _format_mark_detail_row(row: list[object]) -> str:
        name = str(row[0]) if row else ""
        buffer_name = str(row[1]) if len(row) >= 2 else ""
        position = str(row[2]) if len(row) >= 3 else ""
        preview = str(row[3]) if len(row) >= 4 else ""
        try:
            active = int(row[4]) if len(row) >= 5 else 0
        except Exception:
            active = 0
        try:
            here = int(row[5]) if len(row) >= 6 else 0
        except Exception:
            here = 0

        msg = f"mark {name}" if name else "mark"
        if buffer_name:
            owner = buffer_name
            if active:
                owner = "*" + owner
            msg += f" -> {owner}"
        if here:
            msg += " [here]"
        if position:
            msg += f" @ {position}"
        if preview:
            msg += f" — {preview}"
        return msg

    def _describe_mark(ed: "Editor", name: str) -> str | None:
        row = ed.mark_detail_row(str(name))
        if row is None:
            return None
        return _format_mark_detail_row(list(row))

    def _format_jump_detail_row(row: list[object]) -> str:
        query = str(row[0]) if row else ""
        try:
            index = int(row[1]) if len(row) >= 2 else 0
        except Exception:
            index = 0
        lane = str(row[2]) if len(row) >= 3 else ""
        try:
            depth = int(row[3]) if len(row) >= 4 else 0
        except Exception:
            depth = 0
        buffer_name = str(row[4]) if len(row) >= 5 else ""
        position = str(row[5]) if len(row) >= 6 else ""
        preview = str(row[6]) if len(row) >= 7 else ""

        tag = lane or "jump"
        if lane == "current":
            tag = "current"
        elif depth > 0:
            tag = f"{lane} {depth}"

        msg = "showjump"
        shown = query or (str(index) if index > 0 else "")
        if shown:
            msg += f" {shown}"
        if index > 0 and shown != str(index):
            msg += f" -> #{index}"
        msg += f" [{tag}]"
        if buffer_name:
            msg += f" {buffer_name}"
        if position:
            msg += f" @ {position}"
        if preview:
            msg += f" — {preview}"
        return msg

    def _describe_jump(ed: "Editor", query: str) -> str | None:
        row = ed.jump_detail_row(str(query))
        if row is None:
            return None
        return _format_jump_detail_row(list(row))

    def _format_recent_detail_row(ed: "Editor", row: list[object]) -> str:
        query = str(row[0]) if row else ""
        path = str(row[1]) if len(row) >= 2 else query
        try:
            index = int(row[2]) if len(row) >= 3 else 0
        except Exception:
            index = 0
        position = str(row[3]) if len(row) >= 4 else ""
        try:
            active = int(row[4]) if len(row) >= 5 else 0
        except Exception:
            active = 0
        try:
            open_flag = int(row[5]) if len(row) >= 6 else 0
        except Exception:
            open_flag = 0
        try:
            dirty = int(row[6]) if len(row) >= 7 else 0
        except Exception:
            dirty = 0
        try:
            readonly = int(row[7]) if len(row) >= 8 else 0
        except Exception:
            readonly = 0
        section = str(row[8]) if len(row) >= 9 else ""
        detail = str(row[9]) if len(row) >= 10 else ""
        disk_truth = str(row[10]) if len(row) >= 11 else ""
        action_truth = str(row[11]) if len(row) >= 12 else ""

        label = f"recent #{index}" if index > 0 else "recent"
        shown = query or path
        if shown:
            label += f" {shown}"
        if path and path != shown:
            label += f" -> {path}"

        flags: list[str] = []
        if active:
            flags.append("active")
        elif open_flag:
            flags.append("open")
        if dirty:
            flags.append("dirty")
        if readonly:
            flags.append("readonly")
        if flags:
            label += f" [{' , '.join(flags)}]".replace(' , ', ', ')
        if position:
            label += f" @ {position}"

        extras: list[str] = []
        if section:
            extras.append(f"section={section}")
        if detail:
            extras.append(detail)
        if disk_truth:
            extras.append(disk_truth)
        if action_truth:
            extras.append(action_truth)
        if extras:
            label += " — " + " | ".join(extras)
        return label

    def _describe_recent(ed: "Editor", path: str) -> str | None:
        row = ed.recent_detail_row(str(path))
        if row is None:
            return None
        return _format_recent_detail_row(ed, list(row))

    def _format_recent_dir_detail_row(ed: "Editor", row: list[object]) -> str:
        query = str(row[0]) if row else ""
        directory = str(row[1]) if len(row) >= 2 else query
        try:
            count = int(row[2]) if len(row) >= 3 else 0
        except Exception:
            count = 0
        try:
            active_count = int(row[3]) if len(row) >= 4 else 0
        except Exception:
            active_count = 0
        try:
            open_count = int(row[4]) if len(row) >= 5 else 0
        except Exception:
            open_count = 0
        try:
            dirty_count = int(row[5]) if len(row) >= 6 else 0
        except Exception:
            dirty_count = 0
        try:
            readonly_count = int(row[6]) if len(row) >= 7 else 0
        except Exception:
            readonly_count = 0
        sample_path = str(row[7]) if len(row) >= 8 else ""
        sample_detail = str(row[8]) if len(row) >= 9 else ""
        sample_menu = str(row[9]) if len(row) >= 10 else ""
        sample_info = str(row[10]) if len(row) >= 11 else ""

        label = "recentdir"
        shown = query or directory
        if shown:
            label += f" {shown}"
        if directory and directory != shown:
            label += f" -> {directory}"
        label += f": {ed._count_label(count, 'file')}"

        flags: list[str] = []
        if active_count:
            flags.append("active")
        if open_count:
            flags.append(f"open={open_count}")
        if dirty_count:
            flags.append(f"dirty={dirty_count}")
        if readonly_count:
            flags.append(f"readonly={readonly_count}")
        if flags:
            label += f" [{' , '.join(flags)}]".replace(' , ', ', ')

        extras: list[str] = []
        if sample_menu:
            extras.append(f"e.g. {sample_menu}")
        elif sample_path:
            extras.append(f"e.g. {sample_path}")
        if sample_info:
            extras.append(sample_info)
        elif sample_detail and sample_detail != directory:
            extras.append(sample_detail)
        if extras:
            label += " — " + " | ".join(extras)
        return label

    def _describe_recent_dir(ed: "Editor", query: str) -> str | None:
        row = ed.recent_dir_detail_row(str(query))
        if row is None:
            return None
        return _format_recent_dir_detail_row(ed, list(row))

    def _format_keymode_detail_row(row: list[object]) -> str:
        mode = str(row[0]) if row else ""
        active = int(row[1]) if len(row) >= 2 else 0
        known = int(row[2]) if len(row) >= 3 else 0
        once = int(row[3]) if len(row) >= 4 else 0
        binding_count = int(row[4]) if len(row) >= 5 else 0
        sample_key = str(row[5]) if len(row) >= 6 and row[5] not in (0, "") else ""
        sample_action = str(row[6]) if len(row) >= 7 and row[6] not in (0, "") else ""
        sample_desc = str(row[7]) if len(row) >= 8 and row[7] not in (0, "") else ""
        flags: list[str] = []
        if active:
            flags.append("active")
        if once:
            flags.append("once")
        if known:
            flags.append("known")
        elif active:
            flags.append("internal")
        msg = f"keymode {mode}" if mode else "keymode"
        if flags:
            msg += " [" + " ".join(flags) + "]"
        msg += f" bindings={binding_count}"
        if sample_key and sample_action:
            msg += f" sample={sample_key}->{sample_action}"
            if sample_desc:
                msg += f" ({sample_desc})"
        return msg

    def _describe_keymode(ed: "Editor", name: str) -> str | None:
        row = ed.keymode_detail_row(str(name))
        if row is None:
            return None
        return _format_keymode_detail_row(list(row))

    def _describe_topic(ed: "Editor", name: str) -> str | None:
        row = ed.topic_detail_row(name)
        if row is None:
            return None
        kind = str(row[1]) if len(row) >= 2 else ""
        detail = list(row[2]) if len(row) >= 3 and isinstance(row[2], list) else []
        if kind == "command":
            return _format_command_detail_row(detail)
        if kind == "action":
            return _format_action_detail_row(detail)
        if kind == "word":
            return _format_word_detail_row(detail)
        if kind == "doc":
            return _format_doc_detail_row(detail)
        return _apropos_entry(list(row))

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

    def _section_summary_entry(row: list[object]) -> str:
        label = str(row[0]) if row else ""
        try:
            count = int(row[1]) if len(row) >= 2 else 0
        except Exception:
            count = 0
        sample = str(row[2]) if len(row) >= 3 else ""
        detail = str(row[3]) if len(row) >= 4 else ""
        msg = f"{label}: {count}"
        if sample:
            msg += f" (e.g. {sample}"
            if detail:
                msg += f" — {detail}"
            msg += ")"
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
                ed.message(f"help docs: {ed.format_help_target()}")
                return True
            ed.message(f"help docs: no such doc: {doc_topic}")
            return False

        topic = args[0]
        query = " ".join(str(a) for a in args).strip() or str(topic)
        # Minimal: help for commands/actions/visible micromax words
        cmd_msg = _describe_command(ed, topic)
        if cmd_msg is not None:
            ed.message(cmd_msg)
            return True
        action_msg = _describe_action(ed, topic)
        if action_msg is not None:
            ed.message(action_msg)
            return True
        vm_msg = _describe_vm_word(ed, topic)
        if vm_msg is not None:
            ed.message(vm_msg)
            return True

        # Docs fallback: if no command/action/word help matched, try opening a docs page.
        if ed.open_help_doc(query):
            ed.message(f"help: {ed.format_help_target()}")
            return True
        matches = ed.apropos_rows(query, limit=4)
        if matches:
            preview = ", ".join(_apropos_entry(row) for row in matches[:3])
            more = max(0, len(matches) - 3)
            suffix = f" ... (+{more} more)" if more else ""
            ed.message(f"help: no such topic: {query}. Try: {preview}{suffix}")
            return False
        ed.message(f"help: no such topic: {query}")
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

    def c_helpresume(ed: "Editor", args: list[str]) -> bool:
        if args:
            ed.message("usage: helpresume")
            return False
        return bool(ed.help_resume())

    def c_helpprune(ed: "Editor", args: list[str]) -> bool:
        if args:
            ed.message("usage: helpprune")
            return False
        return bool(ed.help_prune())

    def _help_history_inventory_entry(row: list[object]) -> str:
        lane = str(row[0]) if row else ""
        try:
            depth = int(row[1]) if len(row) >= 2 else 0
        except Exception:
            depth = 0
        topic = str(row[2]) if len(row) >= 3 else ""
        position = str(row[4]) if len(row) >= 5 else ""
        state = str(row[5]) if len(row) >= 6 else ""
        tag = lane or "help"
        if lane == "current":
            tag = "here"
        elif lane == "dormant":
            tag = "dormant"
        elif depth > 0:
            tag = f"{lane} {depth}"
        if state == "missing":
            tag = f"{tag} missing"
        msg = f"[{tag}] {topic or '?'}"
        if position:
            msg += f" @ {position}"
        return msg

    def _jump_history_inventory_entry(row: list[object]) -> str:
        lane = str(row[0]) if row else ""
        try:
            depth = int(row[1]) if len(row) >= 2 else 0
        except Exception:
            depth = 0
        try:
            index = int(row[2]) if len(row) >= 3 else 0
        except Exception:
            index = 0
        name = str(row[3]) if len(row) >= 4 else ""
        position = str(row[4]) if len(row) >= 5 else ""
        preview = str(row[5]) if len(row) >= 6 else ""
        tag = lane or "jump"
        if lane == "current":
            tag = "current"
        elif depth > 0:
            tag = f"{lane} {depth}"
        msg = f"[{tag}]"
        if index > 0:
            msg += f" #{index}"
        if name:
            msg += f" {name}"
        if position:
            msg += f" @ {position}"
        if preview:
            msg += f": {preview}"
        return msg

    def c_helpforward(ed: "Editor", args: list[str]) -> bool:
        if args:
            ed.message("usage: helpforward")
            return False
        return bool(ed.help_forward())

    def c_helphistory(ed: "Editor", args: list[str]) -> bool:
        if args:
            ed.message("usage: helphistory")
            return False
        rows = ed.help_history_rows()
        parts = [_help_history_inventory_entry(list(r)) for r in rows]
        ed.message(_counted_inventory_summary("helphistory", "help target", parts))
        return True

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
                ed.message(f"urlopen: {u}")
                return True
            ed.message(f"urlopen: failed: {u}")
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
            ed.message(f"urlcopy: {u}")
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
        row = ed.help_heading_detail_row(query)
        if row is None:
            ed.message(f"helpjump: no heading match: {query}")
            return False
        try:
            line1 = int(row[4] if len(row) > 4 else 0)
            col1 = int(row[5] if len(row) > 5 else 0)
        except Exception:
            line1 = 0
            col1 = 0
        if line1 <= 0 or col1 <= 0:
            ed.message("helpjump: invalid heading position")
            return False

        if not ed._jump_help_target(line1, col1, push_history=True):
            return False
        ed.message(f"helpjump: {_format_cursor_target(ed)}")
        return True

    def c_showhelpheading(ed: "Editor", args: list[str]) -> bool:
        if args:
            ed.message("usage: showhelpheading")
            return False
        if not ed.current_help_doc_topic():
            ed.message("showhelpheading: not in a docs buffer")
            return False
        msg = _describe_current_help_heading(ed)
        if msg is None:
            ed.message("showhelpheading: no heading under cursor")
            return False
        ed.message(msg)
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
        ed.message(f"bind: {_binding_target(key)} -> {spec}")
        return True

    def c_bindmode(ed: "Editor", args: list[str]) -> bool:
        if len(args) < 3:
            ed.message("usage: bindmode MODE KEY ACTIONSPEC")
            return False
        mode = args[0]
        key = args[1]
        spec = " ".join(args[2:])
        ed.keymap.bind(key, spec, mode=mode)
        ed.message(f"bindmode: {_binding_target(key, mode=mode)} -> {spec}")
        return True

    def _no_such_binding(cmd: str, key: str, *, mode: str | None = None) -> str:
        target = f"{key}@{mode}" if mode not in (None, "", "global") else str(key)
        return f"{cmd}: no such binding: {target}"

    def c_binddoc(ed: "Editor", args: list[str]) -> bool:
        if len(args) < 2:
            ed.message("usage: binddoc KEY DOC...")
            return False
        key = args[0]
        doc = " ".join(args[1:]).strip()
        if not ed.keymap.set_desc(key, doc):
            ed.message(_no_such_binding("binddoc", key))
            return False
        ed.message(f"binddoc: {_binding_target(key)} -> {doc}")
        return True

    def c_bindmodedoc(ed: "Editor", args: list[str]) -> bool:
        if len(args) < 3:
            ed.message("usage: bindmodedoc MODE KEY DOC...")
            return False
        mode = args[0]
        key = args[1]
        doc = " ".join(args[2:]).strip()
        if not ed.keymap.set_desc(key, doc, mode=mode):
            ed.message(_no_such_binding("bindmodedoc", key, mode=mode))
            return False
        ed.message(f"bindmodedoc: {_binding_target(key, mode=mode)} -> {doc}")
        return True

    def _binding_target(key: str, *, mode: str | None = None) -> str:
        return f"{key}@{mode}" if mode not in (None, "", "global") else str(key)

    def c_unbind(ed: "Editor", args: list[str]) -> bool:
        if not args:
            ed.message("usage: unbind KEY")
            return False
        key = args[0]
        if not ed.keymap.unbind(key):
            ed.message(_no_such_binding("unbind", key))
            return False
        ed.message(f"unbind: {_binding_target(key)}")
        return True

    def c_unbindmode(ed: "Editor", args: list[str]) -> bool:
        if len(args) < 2:
            ed.message("usage: unbindmode MODE KEY")
            return False
        mode = args[0]
        key = args[1]
        if not ed.keymap.unbind(key, mode=mode):
            ed.message(_no_such_binding("unbindmode", key, mode=mode))
            return False
        ed.message(f"unbindmode: {_binding_target(key, mode=mode)}")
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
        ed.message(f"bindprefix: {_binding_target(key)} -> {mode}")
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
        ed.message(f"bindmodeprefix: {_binding_target(key, mode=owner_mode)} -> {mode}")
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
        row = ed.binding_detail_row(key)
        if row == 0:
            ed.message(_no_such_binding("showkey", key))
            return False
        mode, key2, action, desc, group, span = row
        msg = f"{key2} -> {action}"
        if desc not in (0, None, ''):
            msg = msg + f" [desc {desc}]"
        if mode not in (0, None, '', 'global'):
            msg = msg + f" [mode {mode}]"
        if group not in (0, None, ''):
            msg = msg + f" [group {group}]"
        if span not in (0, None, ''):
            msg = msg + f" (defined at {span[0]}:{span[1]}:{span[2]})"
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
            rows = ed.available_binding_inventory_rows()
            once_modes = {str(mode) for mode, _key, _action, _label, once in rows if once}
            parts = [_fmt_binding_item(str(mode), str(key), str(action), once_modes=once_modes, show_mode=True) for mode, key, action, _label, _once in rows]
            ed.message(_counted_inventory_summary('bindings active', 'binding', parts, sep=', '))
            return bool(rows)

        mode = None if target in ('', '0', 'global') else target
        label = 'global' if mode is None else str(mode)
        rows = ed.keymap.binding_detail_rows_for(mode)
        parts = [_fmt_binding_item(label, str(r[0]), str(r[1])) for r in rows]
        ed.message(_counted_inventory_summary(f'bindings {label}', 'binding', parts, sep=', '))
        return bool(rows)

    def c_showbindingmodes(ed: "Editor", args: list[str]) -> bool:
        query = " ".join(str(x) for x in args).strip()
        rows = ed._resolved_section_summary_rows_for_command("showbindingmodes", query)
        total = sum(int(row[1]) for row in rows if isinstance(row, list) and len(row) >= 2)
        head = f"showbindingmodes{(' ' + query) if query else ''}: {len(rows)} section(s), {total} binding(s)"
        ed.message(head)
        for row in rows:
            ed.message(_section_summary_entry(list(row)))
        return bool(rows)

    def c_whichkey(ed: "Editor", args: list[str]) -> bool:
        if args:
            ed.message("usage: whichkey")
            return False
        rows = ed.available_binding_inventory_rows()
        once_modes = {str(mode) for mode, _key, _action, _label, once in rows if once}
        parts: list[str] = []
        for mode, key, _action, label, _once in rows:
            parts.append(_fmt_binding_item(str(mode), str(key), str(label), once_modes=once_modes, show_mode=True))
        ed.message(_counted_inventory_summary('whichkey', 'binding', parts, sep=', '))
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
        rows = ed.keymode_inventory_rows()
        active = [
            f"{str(name)}{'!' if int(once) else ''}"
            for section, name, once in rows
            if str(section) == "active"
        ]
        known = [str(name) for section, name, _once in rows if str(section) == "known"]
        ed.message("active keymodes: " + ", ".join(active or ['global']))
        ed.message("known keymodes: " + ", ".join(known or ['global']))
        return True

    def c_showkeymode(ed: "Editor", args: list[str]) -> bool:
        if len(args) != 1:
            ed.message("usage: showkeymode MODE")
            return False
        msg = _describe_keymode(ed, str(args[0]))
        if msg is None:
            ed.message(f"showkeymode: no such keymode: {args[0]}")
            return False
        ed.message(msg)
        return True

    def c_showoption(ed: "Editor", args: list[str]) -> bool:
        if len(args) != 1:
            ed.message("usage: showoption NAME")
            return False
        msg = _describe_option(ed, str(args[0]))
        if msg is None:
            ed.message(f"showoption: no such option: {args[0]}")
            return False
        ed.message(msg)
        return True

    def c_showoptiongroups(ed: "Editor", args: list[str]) -> bool:
        query = " ".join(str(x) for x in args).strip()
        rows = ed._resolved_section_summary_rows_for_command("showoptiongroups", query)
        total = sum(int(row[1]) for row in rows if isinstance(row, list) and len(row) >= 2)
        head = f"showoptiongroups{(' ' + query) if query else ''}: {len(rows)} section(s), {total} option(s)"
        ed.message(head)
        for row in rows:
            ed.message(_section_summary_entry(list(row)))
        return True

    def c_showbuffergroups(ed: "Editor", args: list[str]) -> bool:
        query = " ".join(str(x) for x in args).strip()
        rows = ed._resolved_section_summary_rows_for_command("showbuffergroups", query)
        total = sum(int(row[1]) for row in rows if isinstance(row, list) and len(row) >= 2)
        head = f"showbuffergroups{(' ' + query) if query else ''}: {len(rows)} section(s), {total} buffer(s)"
        ed.message(head)
        for row in rows:
            ed.message(_section_summary_entry(list(row)))
        return True

    def c_showbuffer(ed: "Editor", args: list[str]) -> bool:
        if not args:
            ed.message("usage: showbuffer NAME")
            return False
        name = str(args[0])
        msg = _describe_buffer(ed, name)
        if msg is None:
            ed.message(f"showbuffer: no such buffer: {name}")
            return False
        ed.message(msg)
        return True

    def c_showrecent(ed: "Editor", args: list[str]) -> bool:
        if not args:
            ed.message("usage: showrecent PATH")
            return False
        path = str(args[0])
        msg = _describe_recent(ed, path)
        if msg is None:
            ed.message(f"showrecent: no such recent file: {path}")
            return False
        ed.message(msg)
        return True

    def c_showrecentdir(ed: "Editor", args: list[str]) -> bool:
        if not args:
            ed.message("usage: showrecentdir DIR")
            return False
        query = str(args[0])
        msg = _describe_recent_dir(ed, query)
        if msg is None:
            ed.message(f"showrecentdir: no such recent directory: {query}")
            return False
        ed.message(msg)
        return True

    def c_showmark(ed: "Editor", args: list[str]) -> bool:
        if not args:
            ed.message("usage: showmark NAME")
            return False
        name = str(args[0])
        msg = _describe_mark(ed, name)
        if msg is None:
            ed.message(f"showmark: no such mark: {name}")
            return False
        ed.message(msg)
        return True

    def c_showjump(ed: "Editor", args: list[str]) -> bool:
        if not args:
            ed.message("usage: showjump INDEX")
            return False
        query = str(args[0])
        msg = _describe_jump(ed, query)
        if msg is None:
            ed.message(f"showjump: no such jump: {query}")
            return False
        ed.message(msg)
        return True

    def c_showmarkgroups(ed: "Editor", args: list[str]) -> bool:
        query = " ".join(str(x) for x in args).strip()
        rows = ed._resolved_section_summary_rows_for_command("showmarkgroups", query)
        total = sum(int(row[1]) for row in rows if isinstance(row, list) and len(row) >= 2)
        head = f"showmarkgroups{(' ' + query) if query else ''}: {len(rows)} section(s), {total} mark(s)"
        ed.message(head)
        for row in rows:
            ed.message(_section_summary_entry(list(row)))
        return True

    def c_showpalettegroups(ed: "Editor", args: list[str]) -> bool:
        query = " ".join(str(x) for x in args).strip()
        rows = ed._resolved_section_summary_rows_for_command("showpalettegroups", query)
        total = sum(int(row[1]) for row in rows if isinstance(row, list) and len(row) >= 2)
        head = f"showpalettegroups{(' ' + query) if query else ''}: {len(rows)} section(s), {total} item(s)"
        ed.message(head)
        for row in rows:
            ed.message(_section_summary_entry(list(row)))
        return True

    def c_showcmd(ed: "Editor", args: list[str]) -> bool:
        if not args:
            ed.message("usage: showcmd NAME")
            return False
        name = args[0]
        msg = _describe_command(ed, name)
        if msg is None:
            ed.message(f"showcmd: no such command: {name}")
            return False
        ed.message(msg)
        return True

    def c_showaction(ed: "Editor", args: list[str]) -> bool:
        if not args:
            ed.message("usage: showaction NAME")
            return False
        name = args[0]
        msg = _describe_action(ed, name)
        if msg is None:
            ed.message(f"showaction: no such action: {name}")
            return False
        ed.message(msg)
        return True

    def c_showword(ed: "Editor", args: list[str]) -> bool:
        if not args:
            ed.message("usage: showword NAME")
            return False
        name = args[0]
        msg = _describe_vm_word(ed, name)
        if msg is None:
            ed.message(f"showword: no such word: {name}")
            return False
        ed.message(msg)
        return True

    def c_showdoc(ed: "Editor", args: list[str]) -> bool:
        if not args:
            ed.message("usage: showdoc TOPIC")
            return False
        name = args[0]
        msg = _describe_doc(ed, name)
        if msg is None:
            ed.message(f"showdoc: no such doc: {name}")
            return False
        ed.message(msg)
        return True

    def c_showtopic(ed: "Editor", args: list[str]) -> bool:
        if not args:
            ed.message("usage: showtopic NAME")
            return False
        name = args[0]
        msg = _describe_topic(ed, name)
        if msg is None:
            ed.message(f"showtopic: no such topic: {name}")
            return False
        ed.message(msg)
        return True

    def c_showtopics(ed: "Editor", args: list[str]) -> bool:
        query = " ".join(str(x) for x in args).strip()
        rows = ed._resolved_section_summary_rows_for_command("showtopics", query)
        total = sum(int(row[1]) for row in rows if isinstance(row, list) and len(row) >= 2)
        head = f"showtopics{(' ' + query) if query else ''}: {len(rows)} section(s), {total} topic(s)"
        ed.message(head)
        for row in rows:
            ed.message(_section_summary_entry(list(row)))
        return True

    def c_showdocs(ed: "Editor", args: list[str]) -> bool:
        query = " ".join(str(x) for x in args).strip()
        rows = ed._resolved_section_summary_rows_for_command("showdocs", query)
        total = sum(int(row[1]) for row in rows if isinstance(row, list) and len(row) >= 2)
        head = f"showdocs{(' ' + query) if query else ''}: {len(rows)} section(s), {total} doc(s)"
        ed.message(head)
        for row in rows:
            ed.message(_section_summary_entry(list(row)))
        return True

    def c_showplugins(ed: "Editor", args: list[str]) -> bool:
        query = " ".join(str(x) for x in args).strip()
        rows = ed._resolved_section_summary_rows_for_command("showplugins", query)
        total = sum(int(row[1]) for row in rows if isinstance(row, list) and len(row) >= 2)
        head = f"showplugins{(' ' + query) if query else ''}: {len(rows)} section(s), {total} plugin(s)"
        ed.message(head)
        for row in rows:
            ed.message(_section_summary_entry(list(row)))
        return True

    def c_showplugin(ed: "Editor", args: list[str]) -> bool:
        if not args:
            ed.message("usage: showplugin NAME")
            return False
        if ed.plugin_manager is None:
            ed.message("showplugin: no plugin manager")
            return False
        name = str(args[0])
        row = ed.plugin_detail_row(name)
        if row is None:
            ed.message(f"showplugin: no such plugin: {name}")
            return False
        plugin_name = str(row[1]) if len(row) >= 2 else name
        error_count = int(row[5]) if len(row) >= 6 else 0
        detail = str(row[6]) if len(row) >= 7 else ""
        entry = _plugin_inventory_entry(ed, plugin_name)
        if entry.startswith(plugin_name):
            entry = entry[len(plugin_name):].strip()
        msg = f"plugin {plugin_name} {entry} errors={error_count}"
        if detail:
            msg += f" — {detail}"
        ed.message(msg)
        return True

    def c_showhelplink(ed: "Editor", args: list[str]) -> bool:
        if args:
            ed.message("usage: showhelplink")
            return False
        if not ed.current_help_doc_topic():
            ed.message("showhelplink: not in a docs buffer")
            return False
        msg = _describe_current_help_link(ed)
        if msg is None:
            ed.message("showhelplink: no link under cursor")
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

    def c_jumps(ed: "Editor", args: list[str]) -> bool:
        if args:
            ed.message("usage: jumps")
            return False
        rows = ed.jump_history_rows()
        parts = [_jump_history_inventory_entry(list(r)) for r in rows]
        ed.message(_counted_inventory_summary("jumps", "jump", parts))
        return True


    def c_apropos(ed: "Editor", args: list[str]) -> bool:
        if not args:
            ed.message("usage: apropos QUERY")
            return False
        query = " ".join(str(a) for a in args).strip()
        rows = ed.apropos_rows(query, limit=None)
        preview_rows = rows[:6]
        parts = [_apropos_entry(row) for row in preview_rows]
        more = max(0, len(rows) - len(preview_rows))
        suffix = f" ... (+{more} more)" if more else ""
        msg = _counted_inventory_summary(f"apropos {query}", "topic", parts, sep=', ', count=len(rows))
        ed.message(msg + suffix)
        return bool(rows)

    def c_showhelpnav(ed: "Editor", args: list[str]) -> bool:
        if not ed.current_help_doc_topic():
            ed.message("showhelpnav: not in a docs buffer")
            return False
        query = " ".join(str(a) for a in args).strip()
        rows = ed._resolved_section_summary_rows_for_command("showhelpnav", query)
        total = sum(int(r[1]) for r in rows if len(r) >= 2)
        head = f"showhelpnav{(' ' + query) if query else ''}: {len(rows)} section(s), {total} target(s)"
        ed.message(head)
        for row in rows[:8]:
            ed.message(_section_summary_entry(list(row)))
        return bool(rows)

    def c_showhook(ed: "Editor", args: list[str]) -> bool:
        if not args:
            ed.message("usage: showhook NAME")
            return False
        name = args[0]
        rows = ed.hook_inventory_rows(name)
        w = ed.vm.find_word(name)
        if rows is None or not isinstance(w, HookWord):
            ed.message(f"showhook: not a hook: {name}")
            return False
        parts = [ed._hook_inventory_entry_from_row(list(r)) for r in rows]
        msg = _counted_inventory_summary(f"hook {name}", "handler", parts, sep=', ')
        if w.span is not None:
            msg += f" (defined at {w.span.filename}:{w.span.line}:{w.span.col})"
        ed.message(msg)
        return True

    def c_showhooks(ed: "Editor", args: list[str]) -> bool:
        query = " ".join(str(x) for x in args).strip()
        rows = ed.hook_summary_rows(query)
        total = sum(int(row[1]) for row in rows if isinstance(row, list) and len(row) >= 2)
        head = f"showhooks{(' ' + query) if query else ''}: {len(rows)} hook(s), {total} handler(s)"
        ed.message(head)
        for row in rows:
            ed.message(_hook_summary_entry(list(row)))
        return True

    def c_showstatus(ed: "Editor", args: list[str]) -> bool:
        if args:
            ed.message("usage: showstatus")
            return False
        ed.message(ed.status_summary())
        return True

    def c_undo(ed: "Editor", args: list[str]) -> bool:
        if args:
            ed.message("usage: undo")
            return False
        return ed.undo_feedback()

    def c_redo(ed: "Editor", args: list[str]) -> bool:
        if args:
            ed.message("usage: redo")
            return False
        return ed.redo_feedback()

    def c_macro(ed: "Editor", args: list[str]) -> bool:
        """Manage keyboard macros.

        Subcommands:
          - macro record [name]
          - macro stop
          - macro cancel
          - macro play [name] [count]
          - macro list
          - macro status
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
            ed.message(ed.macro_list_message())
            return True
        if sub in ("status", "st"):
            ed.message(ed.macro_status_message())
            return True

        ed.message(f"macro: no such subcommand: {sub}")
        return False

    def _parse_linecol(arg: str) -> tuple[int, int | None]:
        if ":" in arg:
            a, b = arg.split(":", 1)
            return int(a, 10), int(b, 10)
        return int(arg, 10), None

    def _format_save_feedback(info: object) -> str:
        if not isinstance(info, dict):
            return "saved"
        path = str(info.get("path") or "").strip()
        cleanup_raw = info.get("cleanup_parts") or []
        cleanup_parts = [str(part).strip() for part in cleanup_raw if str(part).strip()]
        msg = "saved" if not path else f"saved: {path}"
        if cleanup_parts:
            msg += f" (normalized: {', '.join(cleanup_parts)})"
        return msg

    def _format_open_feedback(ed: "Editor") -> str:
        eb = ed.cur()
        path = str(getattr(eb.buf, "path", "") or getattr(eb, "name", "") or "").strip()
        c = ed.primary_cursor()
        if path:
            return f"opened: {path} @ {c.line + 1}:{c.col}"
        return f"opened @ {c.line + 1}:{c.col}"

    def _format_cursor_target(ed: "Editor") -> str:
        eb = ed.cur()
        name = str(getattr(eb.buf, "path", "") or getattr(eb, "name", "") or "").strip()
        c = ed.primary_cursor()
        if name:
            return f"{name} @ {c.line + 1}:{c.col}"
        return f"{c.line + 1}:{c.col}"

    def _format_active_buffer_feedback(ed: "Editor", prefix: str = "buffer") -> str:
        return f"{prefix}: {_format_cursor_target(ed)}"

    def _buffer_inventory_entry(row: list[object]) -> str:
        name = str(row[0]) if row else ""
        position = str(row[1]) if len(row) >= 2 else ""
        try:
            active = int(row[2]) if len(row) >= 3 else 0
        except Exception:
            active = 0
        try:
            dirty = int(row[3]) if len(row) >= 4 else 0
        except Exception:
            dirty = 0
        try:
            readonly = int(row[4]) if len(row) >= 5 else 0
        except Exception:
            readonly = 0

        label = f"*{name}" if active else name
        flags: list[str] = []
        if dirty:
            flags.append("dirty")
        if readonly:
            flags.append("readonly")
        loc = f" @ {position}" if position else ""
        if flags:
            return f"{label} [{', '.join(flags)}]{loc}"
        return f"{label}{loc}"

    def _recent_inventory_entry(row: list[object]) -> str:
        try:
            index = int(row[0]) if row else 0
        except Exception:
            index = 0
        path = str(row[1]) if len(row) >= 2 else ""
        position = str(row[2]) if len(row) >= 3 else ""
        try:
            active = int(row[3]) if len(row) >= 4 else 0
        except Exception:
            active = 0
        try:
            open_flag = int(row[4]) if len(row) >= 5 else 0
        except Exception:
            open_flag = 0
        try:
            dirty = int(row[5]) if len(row) >= 6 else 0
        except Exception:
            dirty = 0
        try:
            readonly = int(row[6]) if len(row) >= 7 else 0
        except Exception:
            readonly = 0

        label = f"{index}:*{path}" if active else f"{index}:{path}"
        flags: list[str] = []
        if open_flag and not active:
            flags.append("open")
        if dirty:
            flags.append("dirty")
        if readonly:
            flags.append("readonly")
        loc = f" @ {position}" if position else ""
        if flags:
            return f"{label} [{', '.join(flags)}]{loc}"
        return f"{label}{loc}"

    def _mark_inventory_entry(row: list[object]) -> str:
        name = str(row[0]) if row else ""
        owner = str(row[1]) if len(row) >= 2 else ""
        position = str(row[2]) if len(row) >= 3 else ""
        try:
            active = int(row[4]) if len(row) >= 5 else 0
        except Exception:
            active = 0
        try:
            here = int(row[5]) if len(row) >= 6 else 0
        except Exception:
            here = 0
        if active:
            owner = "*" + owner
        flags: list[str] = []
        if here:
            flags.append("here")
        loc = f" @ {position}" if position else ""
        if flags:
            return f"{name} -> {owner} [{', '.join(flags)}]{loc}"
        return f"{name} -> {owner}{loc}"

    def _hook_summary_entry(row: list[object]) -> str:
        name = str(row[0]) if row else ""
        try:
            count = int(row[1]) if len(row) >= 2 else 0
        except Exception:
            count = 0
        sample = row[2] if len(row) >= 3 else 0
        span = row[3] if len(row) >= 4 else 0
        msg = f"{name}: {count} handler(s)"
        if sample not in (0, None, ""):
            msg += f" (e.g. {sample})"
        if isinstance(span, list) and len(span) >= 3:
            msg += f" (defined at {span[0]}:{span[1]}:{span[2]})"
        return msg

    def _option_inventory_entry(row: list[object]) -> str:
        name = str(row[0]) if row else ""
        value = str(row[1]) if len(row) >= 2 else ""
        try:
            local_override = int(row[4]) if len(row) >= 5 else 0
        except Exception:
            local_override = 0
        msg = f"{name}={value}" if name else value
        if local_override:
            msg += " (local)"
        return msg

    def _counted_inventory_summary(
        label: str,
        noun: str,
        parts: list[str],
        *,
        sep: str = '; ',
        count: int | None = None,
    ) -> str:
        """Return one tiny count-aware inventory dialect for zero/non-zero cases."""

        total = len(parts) if count is None else max(0, int(count))
        head = f"{str(label)}: {total} {str(noun)}(s)"
        return head if not parts else head + ", " + str(sep).join(parts)

    def _plugin_inventory_entry(ed: "Editor", name: str) -> str:
        try:
            return str(ed.plugin_inventory_entry(name))
        except Exception:
            return str(name)

    def _plugin_inventory_state(ed: "Editor", name: str) -> str:
        pm = getattr(ed, "plugin_manager", None)
        if pm is None:
            return "available"
        plugin_name = str(name)
        try:
            errs = [1 for (n, _e) in getattr(pm, "load_errors", []) if str(n) == plugin_name]
        except Exception:
            errs = []
        if errs:
            return "error"
        try:
            if plugin_name in getattr(pm, "plugins", {}):
                return "loaded"
        except Exception:
            pass
        return "available"

    def _plugin_inventory_entry_from_row(row: list[object]) -> str:
        name = str(row[0] if len(row) > 0 else "")
        state = str(row[1] if len(row) > 1 else "") or "available"
        version = str(row[2] if len(row) > 2 else "")
        deps = str(row[3] if len(row) > 3 else "")
        flags: list[str] = [state]
        if version:
            flags.append(f"v{version}")
        if deps:
            flags.append("deps:" + deps)
        return f"{name} [{', '.join(flags)}]" if name and flags else name

    def _plugin_inventory_state_from_row(row: list[object]) -> str:
        state = str(row[1] if len(row) > 1 else "")
        return state if state in {"error", "loaded", "available"} else "available"

    def _plugin_dependency_entry(ed: "Editor", name: str) -> str:
        """Return a tiny inspectable dependency summary for plugin detail views."""

        pm = getattr(ed, "plugin_manager", None)
        dep_name = str(name)
        if pm is None:
            return f"{dep_name} [missing]"
        try:
            loaded = bool(dep_name in getattr(pm, "plugins", {}))
        except Exception:
            loaded = False
        try:
            cand = getattr(pm, "candidates", {}).get(dep_name) if hasattr(pm, "candidates") else None
        except Exception:
            cand = None
        try:
            errs = [str(e) for (n, e) in getattr(pm, "load_errors", []) if str(n) == dep_name]
        except Exception:
            errs = []
        if cand is None and not loaded and not errs:
            return f"{dep_name} [missing]"
        return _plugin_inventory_entry(ed, dep_name)

    def _plugin_error_count_line(count: int) -> str:
        """Return the tiny shared plugin-error count dialect.

        Plugin inventory/detail paths have become increasingly count-aware.
        Filtered detail should stay explicit too, so healthy plugins say
        ``errors: 0`` instead of falling back to ``(none)`` while broken
        plugins keep the same ``errors: N`` shape.
        """

        return f"  errors: {max(0, int(count))}"

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
            ed.message(f"goto: {_format_cursor_target(ed)}")
            return True
        eb.cursors[eb.primary] = new_c
        ed.message(f"goto: {_format_cursor_target(ed)}")
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
            ed.message(f"jump: {_format_cursor_target(ed)}")
            return True
        eb.cursors[eb.primary] = new_c
        ed.message(f"jump: {_format_cursor_target(ed)}")
        return True

    def c_jumpback(ed: "Editor", args: list[str]) -> bool:
        if args:
            ed.message("usage: jumpback")
            return False
        return ed.jump_back_feedback()

    def c_jumpforward(ed: "Editor", args: list[str]) -> bool:
        if args:
            ed.message("usage: jumpforward")
            return False
        return ed.jump_forward_feedback()

    def _convert_template(value: str) -> str:
        # Shared with the VM's regex hostcalls to avoid drift.
        return convert_replacement_template(value)

    def c_replace(ed: "Editor", args: list[str]) -> bool:
        if len(args) < 2:
            ed.message("usage: replace SEARCH VALUE [-a] [-l]")
            return False

        def _occurrence_label(n: int) -> str:
            return "occurrence" if int(n) == 1 else "occurrences"

        search = args[0]
        value = args[1]
        flags = set(args[2:])
        replace_all = "-a" in flags
        literal = "-l" in flags
        action_name = "replaceall" if replace_all else "replace"

        # Protected buffers (help/docs) should reject edits.
        try:
            if hasattr(ed, "is_protected_buffer") and ed.is_protected_buffer():
                ed.message(f"{action_name}: read-only buffer")
                return False
        except Exception:
            pass

        eb = ed.cur()
        ignorecase = bool(ed.options.get("ignorecase", local=eb.local_options))
        before = ed._snapshot_buffer_state(eb)

        text = before[0]
        ed._normalize_cursor_lists(eb)
        start_idx = 0 if replace_all else cursor_to_index(eb.buf, eb.cursors[eb.primary])
        count = 0

        if literal:
            if replace_all:
                if not ignorecase:
                    if search not in text:
                        ed.message(f"{action_name}: not found")
                        return False
                    count = text.count(search)
                    new = text.replace(search, value)
                else:
                    # Case-insensitive literal replace-all: use a regex with a literal pattern
                    # and a lambda replacement to avoid backslash expansion surprises.
                    pat_lit = re.compile(re.escape(search), re.IGNORECASE)
                    new, count = pat_lit.subn(lambda _m: value, text)
                    if count == 0:
                        ed.message(f"{action_name}: not found")
                        return False
            else:
                if not ignorecase:
                    i = text.find(search, start_idx)
                else:
                    hay_l = text.lower()
                    needle_l = search.lower()
                    i = hay_l.find(needle_l, start_idx)
                if i < 0:
                    ed.message(f"{action_name}: not found")
                    return False
                count = 1
                new = text[:i] + value + text[i + len(search) :]
        else:
            try:
                flags_re = re.IGNORECASE if ignorecase else 0
                pat = re.compile(search, flags_re)
            except re.error as e:
                ed.message(f"{action_name}: invalid regex: {e}")
                return False
            repl_py = _convert_template(value)
            if replace_all:
                new, count = pat.subn(repl_py, text)
                if count == 0:
                    ed.message(f"{action_name}: not found")
                    return False
            else:
                m = pat.search(text, pos=start_idx)
                if m is None:
                    ed.message(f"{action_name}: not found")
                    return False
                count = 1
                new = text[: m.start()] + m.expand(repl_py) + text[m.end() :]

        eb.buf.set_text(new)
        after = ed._snapshot_buffer_state(eb)
        ed._record_undo_snapshot(eb, before, after, action_name)
        if replace_all:
            ed.message(f"replaceall: replaced {count} {_occurrence_label(count)}")
        else:
            ed.message(f"replace: replaced {count} {_occurrence_label(count)} from cursor")
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
                ok = bool(ed.open_file(str(p), initial_cursor=initial_cursor))
                if ok:
                    ed.message(_format_open_feedback(ed))
                return ok
            except Exception as e:
                ed.message(f"open: {e}")
                return False

        # Interactive open: keep the normal editor UX (unrestricted by caps).
        try:
            ok = bool(ed.open_file(raw))
            if ok:
                ed.message(_format_open_feedback(ed))
            return ok
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
                info = ed.save()
            except Exception as e:
                ed.message(f"save: {e}")
                return False
            ed.message(_format_save_feedback(info))
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
            info = ed.save()
        except Exception as e:
            ed.message(f"save: {e}")
            return False
        ed.message(_format_save_feedback(info))
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
        target = str(name or (ed.active or "")).strip()
        was_active = target and target == str(ed.active or "")
        ok = ed.close_buffer(name, force=force)
        if ok:
            if was_active:
                ed.message(f"close: {target} -> " + _format_active_buffer_feedback(ed, prefix="buffer"))
            else:
                ed.message(f"close: {target}")
            return True
        # When not ok, close_buffer will have emitted a warning message if dirty.
        if name and name not in ed.buffers:
            ed.message(f"close: no such buffer: {name}")
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
            ed.message(f"closeall: error: {e}")
            return False
        ed.message("closeall -> " + _format_active_buffer_feedback(ed, prefix="buffer"))
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
            ed.message(f"only: error: {e}")
            return False
        ed.message("only -> " + _format_active_buffer_feedback(ed, prefix="buffer"))
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
            ed.message("prevbuf: no previous buffer")
            return False
        if not ed.switch_buffer(name):
            ed.message("prevbuf: no previous buffer")
            return False
        ed.message(_format_active_buffer_feedback(ed, prefix="prevbuf"))
        return True

    def c_recent(ed: "Editor", args: list[str]) -> bool:
        """recent [N|clear] - show or open recent files.

        - `recent` shows the MRU list (up to 12).
        - `recent N` opens the Nth entry (1-based).
        - `recent clear` clears the list.
        """
        if not args:
            rows = ed.recent_inventory_rows(limit=12)
            parts = [_recent_inventory_entry(list(r)) for r in rows]
            total = len(ed.recent_inventory_rows())
            more = max(0, total - len(rows))
            msg = _counted_inventory_summary('recent', 'recent file', parts, count=len(rows))
            if more:
                msg += f" ... (+{more} more)"
            ed.message(msg)
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

    def c_recentdirpick(ed: "Editor", args: list[str]) -> bool:
        q = str(args[0]) if args else ''
        ed.enter_recent_dir_prompt(q)
        return True

    def c_showrecentgroups(ed: "Editor", args: list[str]) -> bool:
        query = " ".join(str(x) for x in args).strip()
        rows = ed._resolved_section_summary_rows_for_command("showrecentgroups", query)
        total = sum(int(row[1]) for row in rows if isinstance(row, list) and len(row) >= 2)
        head = f"showrecentgroups{(' ' + query) if query else ''}: {len(rows)} section(s), {total} file(s)"
        ed.message(head)
        for row in rows:
            ed.message(_section_summary_entry(list(row)))
        return True

    def c_showrecentdirgroups(ed: "Editor", args: list[str]) -> bool:
        query = " ".join(str(x) for x in args).strip()
        rows = ed._resolved_section_summary_rows_for_command("showrecentdirgroups", query)
        total = sum(int(row[1]) for row in rows if isinstance(row, list) and len(row) >= 2)
        head = f"showrecentdirgroups{(' ' + query) if query else ''}: {len(rows)} section(s), {total} file(s)"
        ed.message(head)
        for row in rows:
            ed.message(_section_summary_entry(list(row)))
        return True


    def c_buffers(ed: "Editor", args: list[str]) -> bool:
        if args:
            ed.message("usage: buffers")
            return False
        rows = ed.buffer_inventory_rows()
        parts = [_buffer_inventory_entry(row) for row in rows]
        ed.message(_counted_inventory_summary("buffers", "buffer", parts))
        return True

    def c_buffer(ed: "Editor", args: list[str]) -> bool:
        if not args:
            ed.message("usage: buffer NAME")
            return False
        name = str(args[0])
        if not ed.switch_buffer(name):
            ed.message(f"buffer: no such buffer: {name}")
            return False
        ed.message(_format_active_buffer_feedback(ed, prefix="buffer"))
        return True

    def c_mark(ed: "Editor", args: list[str]) -> bool:
        if not args:
            ed.message("usage: mark NAME")
            return False
        name = str(args[0])
        if not ed.mark_set(name):
            ed.message("mark: invalid name")
            return False
        ed.message(f"mark set: {name} -> {_format_cursor_target(ed)}")
        return True

    def c_markjump(ed: "Editor", args: list[str]) -> bool:
        if not args:
            ed.message("usage: markjump NAME")
            return False
        name = str(args[0])
        if not ed.mark_jump(name):
            ed.message(f"markjump: no such mark: {name}")
            return False
        ed.message(f"markjump: {name} -> {_format_cursor_target(ed)}")
        return True

    def c_marks(ed: "Editor", args: list[str]) -> bool:
        if args:
            ed.message("usage: marks")
            return False
        rows = ed.mark_inventory_rows()
        parts = [_mark_inventory_entry(list(r)) for r in rows]
        ed.message(_counted_inventory_summary("marks", "mark", parts))
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
        ed.message(f"set: {name}={val}")
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
        ed.message(f"setlocal: {name}(local)={val}")
        return True

    def c_show(ed: "Editor", args: list[str]) -> bool:
        if not args:
            for row in ed.option_inventory_rows():
                ed.message(_option_inventory_entry(list(row)))
            return True
        name = str(args[0])
        rows = ed.option_inventory_rows(names=[name])
        if not rows:
            ed.message(f"show: no such option: {name}")
            return False
        ed.message(_option_inventory_entry(list(rows[0])))
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
        ed.message(f"toggle: {name}={val}")
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
        ed.message(f"togglelocal: {name}(local)={val}")
        return True

    def c_reload(ed: "Editor", args: list[str]) -> bool:
        return ed.reload_runtime()

    def c_plugin(ed: "Editor", args: list[str]) -> bool:
        if not args:
            ed.message("usage: plugin list|reload NAME|info NAME|errors [NAME]")
            return False
        sub = args[0]
        if sub == "list":
            rows = ed.plugin_inventory_rows()
            if not rows:
                ed.message("plugin list: 0 plugin(s)")
                return True
            parts = [_plugin_inventory_entry_from_row(list(row)) for row in rows]
            counts = {"error": 0, "loaded": 0, "available": 0}
            for row in rows:
                state = _plugin_inventory_state_from_row(list(row))
                counts[state] = counts.get(state, 0) + 1
            count_parts = [
                f"{counts['error']} error" + ("s" if counts['error'] != 1 else "")
                for _k in [0]
                if counts['error']
            ]
            count_parts += [
                f"{counts['loaded']} loaded"
                for _k in [0]
                if counts['loaded']
            ]
            count_parts += [
                f"{counts['available']} available"
                for _k in [0]
                if counts['available']
            ]
            prefix = f"plugin list: {len(rows)} plugin(s)"
            if count_parts:
                prefix += " (" + ", ".join(count_parts) + ")"
            ed.message(prefix + "; " + "; ".join(parts))
            return True
        if sub == "reload" and len(args) >= 2:
            return ed.plugin_reload_with_feedback(str(args[1]))
        if sub == "errors":
            pm = ed.plugin_manager
            if not pm:
                ed.message("plugin errors: no plugin manager")
                return False
            flt = args[1] if len(args) >= 2 else ""
            errs = [(n, e) for (n, e) in getattr(pm, "load_errors", []) if (not flt or str(n) == str(flt))]
            if flt:
                name = str(flt)
                loaded = bool(name in getattr(pm, "plugins", {}))
                cand = getattr(pm, "candidates", {}).get(name) if hasattr(pm, "candidates") else None
                if cand is None and not loaded and not errs:
                    ed.message(f"plugin errors: no such plugin: {name}")
                    return False
                ed.message(f"plugin errors: {_plugin_inventory_entry(ed, name)}")
                if not errs:
                    ed.message(_plugin_error_count_line(0))
                    return True
                ed.message(_plugin_error_count_line(len(errs)))
                for _n, err in errs[-50:]:
                    ed.message(f"    - {err}")
                return True
            if not errs:
                ed.message("plugin errors: 0 plugin(s), 0 error(s)")
                return True
            grouped: dict[str, list[str]] = {}
            order: list[str] = []
            for n, err in errs:
                name = str(n)
                if name not in grouped:
                    grouped[name] = []
                    order.append(name)
                grouped[name].append(str(err))
            ed.message(f"plugin errors: {len(grouped)} plugin(s), {len(errs)} error(s)")
            for name in order[-50:]:
                item_errs = grouped.get(name, [])
                label = "error" if len(item_errs) == 1 else "errors"
                ed.message(f"  - {_plugin_inventory_entry(ed, name)} ({len(item_errs)} {label})")
                for err in item_errs[-50:]:
                    ed.message(f"    - {err}")
            return True
        if sub == "info" and len(args) >= 2:
            pm = ed.plugin_manager
            if not pm:
                ed.message("plugin info: no plugin manager")
                return False
            name = args[1]
            loaded = bool(name in getattr(pm, "plugins", {}))
            cand = getattr(pm, "candidates", {}).get(name) if hasattr(pm, "candidates") else None
            errs = [e for (n, e) in getattr(pm, "load_errors", []) if str(n) == str(name)]
            if cand is None and not loaded and not errs:
                ed.message(f"plugin info: no such plugin: {name}")
                return False
            ed.message(f"plugin info: {_plugin_inventory_entry(ed, name)}")
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
            dep_counts = {"loaded": 0, "error": 0, "missing": 0, "available": 0}
            for dep in reqs:
                state = _plugin_inventory_state(ed, dep)
                pm_dep = getattr(ed, "plugin_manager", None)
                dep_name = str(dep)
                known = False
                if pm_dep is not None:
                    try:
                        known = bool(dep_name in getattr(pm_dep, "plugins", {}))
                    except Exception:
                        known = False
                    if not known:
                        try:
                            known = getattr(pm_dep, "candidates", {}).get(dep_name) is not None if hasattr(pm_dep, "candidates") else False
                        except Exception:
                            known = False
                    if not known:
                        try:
                            known = any(str(n) == dep_name for (n, _e) in getattr(pm_dep, "load_errors", []))
                        except Exception:
                            known = False
                if not known:
                    state = "missing"
                dep_counts[state] = dep_counts.get(state, 0) + 1
            dep_count_parts = [
                f"{dep_counts['loaded']} loaded"
                for _k in [0]
                if dep_counts['loaded']
            ]
            dep_count_parts += [
                f"{dep_counts['error']} error" + ("s" if dep_counts['error'] != 1 else "")
                for _k in [0]
                if dep_counts['error']
            ]
            dep_count_parts += [
                f"{dep_counts['available']} available"
                for _k in [0]
                if dep_counts['available']
            ]
            dep_count_parts += [
                f"{dep_counts['missing']} missing"
                for _k in [0]
                if dep_counts['missing']
            ]
            dep_prefix = f"  requires: {len(reqs)}"
            if dep_count_parts:
                dep_prefix += " (" + ", ".join(dep_count_parts) + ")"
            ed.message(dep_prefix)
            for dep in reqs:
                ed.message(f"    - {_plugin_dependency_entry(ed, dep)}")
            if not errs:
                ed.message(_plugin_error_count_line(0))
                return True
            ed.message(_plugin_error_count_line(len(errs)))
            for err in errs[-50:]:
                ed.message(f"    - {err}")
            return True
        ed.message("usage: plugin list|reload NAME|info NAME|errors [NAME]")
        return False

    d.register("help", c_help, doc="help [topic] - show help for commands/actions")
    d.register("helppick", c_helppick, doc="helppick [QUERY] - open searchable docs picker")
    d.register("helpback", c_helpback, doc="helpback - go back in docs help navigation")
    d.register("helpresume", c_helpresume, doc="helpresume - reopen the last dormant session-local docs help target")
    d.register("helpprune", c_helpprune, doc="helpprune - prune missing docs targets from local help history")
    d.register("helpforward", c_helpforward, doc="helpforward - go forward in docs help navigation")
    d.register("helphistory", c_helphistory, doc="helphistory - show the tiny docs help history register")
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
    d.register("jumps", c_jumps, doc="jumps - show the current jumplist register")
    d.register("showjump", c_showjump, doc="showjump INDEX - show exact jumplist entry without jumping")
    d.register("apropos", c_apropos, doc="apropos QUERY - search commands/actions/words/docs by name")
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
    d.register("showkeymode", c_showkeymode, doc="showkeymode MODE - show exact keymode detail")
    d.register("showoption", c_showoption, doc="showoption NAME - show exact option value/default/doc detail")
    d.register("showoptiongroups", c_showoptiongroups, doc="showoptiongroups [QUERY] - show count-aware option families")
    d.register("showbuffergroups", c_showbuffergroups, doc="showbuffergroups [QUERY] - show count-aware buffer sections")
    d.register("showbuffer", c_showbuffer, doc="showbuffer NAME - show exact buffer state without switching")
    d.register("showrecent", c_showrecent, doc="showrecent PATH - show exact recent-file state without opening")
    d.register("showrecentdir", c_showrecentdir, doc="showrecentdir DIR - show exact recent-directory bucket state without opening")
    d.register("showmark", c_showmark, doc="showmark NAME - show exact mark state without jumping")
    d.register("showmarkgroups", c_showmarkgroups, doc="showmarkgroups [QUERY] - show count-aware mark buckets by owning buffer")
    d.register("showpalettegroups", c_showpalettegroups, doc="showpalettegroups [QUERY] - show count-aware command-palette buckets")
    d.register("showkey", c_showkey, doc="showkey KEY - show resolved binding for key")
    d.register("rawkeys", c_rawkeys, doc="rawkeys [on|off] - TUI raw key debugging (print key events instead of dispatching)")
    d.register("showbindings", c_showbindings, doc="showbindings [MODE|active] - show discoverable bindings")
    d.register("showbindingmodes", c_showbindingmodes, doc="showbindingmodes [QUERY] - show reachable binding buckets by winning mode")
    d.register("whichkey", c_whichkey, doc="whichkey - show currently available bindings with descriptions")
    d.register("showcmd", c_showcmd, doc="show command docs/provenance")
    d.register("showaction", c_showaction, doc="showaction NAME - show editor action docs")
    d.register("showword", c_showword, doc="showword NAME - show visible micromax word docs/effect/provenance")
    d.register("showdoc", c_showdoc, doc="showdoc TOPIC - show resolved docs title/section/summary/path")
    d.register("showtopic", c_showtopic, doc="showtopic NAME - show exact help topic detail without reopening docs")
    d.register("showtopics", c_showtopics, doc="showtopics [QUERY] - show count-aware generic help-topic sections")
    d.register("showdocs", c_showdocs, doc="showdocs - show count-aware docs-family sections")
    d.register("showplugins", c_showplugins, doc="showplugins [QUERY] - show count-aware plugin-state sections")
    d.register("showplugin", c_showplugin, doc="showplugin NAME - show exact plugin state without opening verbose detail")
    d.register("showhelpheading", c_showhelpheading, doc="showhelpheading - show current docs heading under cursor")
    d.register("showhelplink", c_showhelplink, doc="showhelplink - show current docs-link target under cursor")
    d.register("showhelpnav", c_showhelpnav, doc="showhelpnav [QUERY] - show count-aware current-doc navigation sections")
    d.register("showhook", c_showhook, doc="showhook NAME - show installed hook handlers")
    d.register("showhooks", c_showhooks, doc="showhooks [QUERY] - show count-aware live hook summary")
    d.register("showstatus", c_showstatus, doc="showstatus - show portable statusline summary")
    d.register("undo", c_undo, doc="undo - undo the latest edit")
    d.register("redo", c_redo, doc="redo - redo the latest undone edit")
    d.register("macro", c_macro, doc="macro record|stop|cancel|play|list - keyboard macros")
    d.register("goto", c_goto, doc="goto line[:col] - go to absolute line")
    d.register("jump", c_jump, doc="jump +/-n[:col] - move relative lines")
    d.register("jumpback", c_jumpback, doc="jumpback - jump to the previous jumplist entry")
    d.register("jumpforward", c_jumpforward, doc="jumpforward - jump to the next jumplist entry")
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
    d.register("recentdirpick", c_recentdirpick, doc="recentdirpick [QUERY] - open searchable recent file picker grouped by directory")
    d.register("showrecentgroups", c_showrecentgroups, doc="showrecentgroups [QUERY] - show count-aware recent file buckets")
    d.register("showrecentdirgroups", c_showrecentdirgroups, doc="showrecentdirgroups [QUERY] - show count-aware recent directory buckets")

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
    d.register("plugin", c_plugin, doc="plugin list|reload NAME|info NAME|errors [NAME]")
