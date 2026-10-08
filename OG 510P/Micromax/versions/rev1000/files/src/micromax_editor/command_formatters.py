from __future__ import annotations

from pathlib import Path

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


def _format_macro_detail_row(row: list[object]) -> str:
    query = str(row[0]) if row else ""
    name = str(row[1]) if len(row) >= 2 else query
    state = str(row[2]) if len(row) >= 3 else "saved"
    try:
        steps = int(row[3]) if len(row) >= 4 else 0
    except Exception:
        steps = 0
    try:
        default = int(row[4]) if len(row) >= 5 else 0
    except Exception:
        default = 0
    try:
        shadow_steps = int(row[5]) if len(row) >= 6 else 0
    except Exception:
        shadow_steps = 0

    shown = query or name
    msg = f"showmacro {shown}" if shown else 'showmacro'
    flags: list[str] = []
    if state == 'recording':
        flags.append('recording')
    elif state == 'playing':
        flags.append('playing')
    if default:
        flags.append('default')
    if flags:
        msg += ' [' + ', '.join(flags) + ']'
    step_word = 'step' if steps == 1 else 'steps'
    if state == 'recording':
        msg += f": {steps} live {step_word}"
        extras: list[str] = ['stop to save, cancel to discard']
        if shadow_steps > 0:
            shadow_word = 'step' if shadow_steps == 1 else 'steps'
            extras.append(f"saved={shadow_steps} {shadow_word}")
        msg += ' · ' + ' · '.join(extras)
        return msg
    msg += f": {steps} {step_word}"
    if state == 'playing':
        msg += ' · wait for playback'
    elif default:
        msg += ' · default replay slot'
    return msg


def _describe_macro(ed: "Editor", name: str) -> str | None:
    row = ed.macro_detail_row(str(name))
    if row is None:
        return None
    return _format_macro_detail_row(list(row))


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
    visible = {str(index)} if index > 0 else set()
    if index > 0:
        visible.add(f"#{index}")
    if index > 0 and shown not in visible:
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

    try:
        basename = str(Path(path).name) if path else ""
    except Exception:
        basename = ""
    extras = ed._recent_location_parts(section, detail, basename=basename)
    if disk_truth:
        extras.append(disk_truth)
    if action_truth:
        extras.append(action_truth)
    if extras:
        label += " — " + " | ".join(extras)
    return label


def _describe_recent(ed: "Editor", query: str) -> str | None:
    raw = str(query)
    row = ed.recent_detail_row_by_index(raw)
    if row is None:
        row = ed.recent_detail_row(raw)
    if row is None:
        return None
    vals = list(row)
    if vals:
        try:
            vals[0] = str(vals[1]) if len(vals) >= 2 else ""
        except Exception:
            vals[0] = ""
    return _format_recent_detail_row(ed, vals)


def _format_recent_reopen_feedback(ed: "Editor", index: int, path: str) -> str:
    msg = f"recent {max(0, int(index))} -> {_format_cursor_target(ed)}"
    row = ed.recent_detail_row(str(path))
    if row is None:
        return msg
    disk_truth = str(row[10]) if len(row) >= 11 else ""
    action_truth = str(row[11]) if len(row) >= 12 else ""
    extras = [part for part in (disk_truth, action_truth) if str(part).strip()]
    if extras:
        msg += " | " + " | ".join(str(part) for part in extras)
    return msg


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
    trimmed_info = ed._trim_leading_location_echo(sample_info, directory)
    if trimmed_info:
        extras.append(trimmed_info)
    elif sample_detail and sample_detail != directory:
        extras.append(sample_detail)
    if extras:
        label += " — " + " | ".join(extras)
    return label


def _describe_recent_dir(ed: "Editor", query: str) -> str | None:
    raw = str(query)
    row = ed.recent_dir_detail_row_by_index(raw)
    if row is None:
        row = ed.recent_dir_detail_row(raw)
    if row is None:
        return None
    vals = list(row)
    if vals:
        vals[0] = raw
    return _format_recent_dir_detail_row(ed, vals)


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
    if bool(info.get("forced", False)):
        msg += " (forced overwrite)"
    if cleanup_parts:
        msg += f" (normalized: {', '.join(cleanup_parts)})"
    recovery_warning = str(info.get("recovery_warning") or "").strip()
    if recovery_warning:
        msg += f" (recovery unavailable: {recovery_warning})"
    return msg


def _format_revert_feedback(info: object) -> str:
    if not isinstance(info, dict):
        return "reverted"
    path = str(info.get("path") or "").strip()
    msg = "reverted" if not path else f"reverted: {path}"
    if bool(info.get("forced", False)):
        msg += " (discarded local edits)"
    return msg


def _parse_diff_limit(args: list[str]) -> int:
    if not args:
        return 80
    raw = str(args[0] or "").strip()
    if raw in {"--all", "all"}:
        return 0
    if raw.isdigit():
        return max(1, int(raw))
    raise ValueError("usage: diff [N|--all]")


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
    disk_truth = str(row[7]) if len(row) >= 8 else ""
    action_truth = str(row[8]) if len(row) >= 9 else ""

    label = f"{index}:*{path}" if active else f"{index}:{path}"
    flags: list[str] = []
    if open_flag and not active:
        flags.append("open")
    if dirty:
        flags.append("dirty")
    if readonly:
        flags.append("readonly")
    entry = f"{label}"
    if flags:
        entry += f" [{', '.join(flags)}]"
    if position:
        entry += f" @ {position}"
    if disk_truth:
        entry += f" | {disk_truth}"
    if action_truth:
        entry += f" | {action_truth}"
    return entry


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


def _plugin_runtime_inventory_summary(ed: "Editor", *, label: str, include_state_counts: bool) -> str:
    """Return one tiny runtime inventory summary for broad plugin entry points.

    Command-bar previews already expose whether the plugin subsystem is
    unavailable, empty, or populated. Post-Enter umbrella entry points
    should not drift back to bare usage lines when Micromax already knows
    the same live inventory truth.
    """

    pm = getattr(ed, "plugin_manager", None)
    if pm is None:
        return f"{label}: no plugin manager"
    rows = ed.plugin_inventory_rows()
    if not rows:
        return f"{label}: 0 plugin(s)"
    summary = f"{label}: {len(rows)} plugin(s)"
    if include_state_counts:
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
        if count_parts:
            summary += " (" + ", ".join(count_parts) + ")"
    summary += f" · e.g. {_plugin_inventory_entry_from_row(list(rows[0]))}"
    return summary


def _plugin_runtime_root_summary(ed: "Editor") -> str:
    """Return one tiny runtime summary for the umbrella ``plugin`` command.

    Command-bar preview for raw ``plugin`` already exposes live plugin
    inventory truth before Enter. The post-Enter root dispatcher should not
    drift back to a bare usage line when Micromax already knows whether the
    subsystem is missing, empty, or populated. Keep the runtime summary
    compact and leave the detailed full inventory to ``plugin list``.
    """

    return _plugin_runtime_inventory_summary(ed, label="plugin", include_state_counts=True)


def _showplugin_runtime_root_summary(ed: "Editor") -> str:
    """Return one tiny runtime summary for raw ``showplugin``.

    Plain ``showplugin`` is still a usage-shaped exact inspector, but its
    no-arg command-bar preview already exposes whether there is a missing,
    empty, or live plugin inventory behind that exact path. Keep the
    post-Enter runtime row equally truthful before the usage hint.
    """

    return _plugin_runtime_inventory_summary(ed, label="showplugin", include_state_counts=False)


def _showhook_runtime_root_summary(ed: "Editor") -> str:
    """Return one tiny runtime summary for raw ``showhook``.

    Plain ``showhook`` is still a usage-shaped exact inspector, but its
    no-arg path should tell the truth about the live hook namespace before
    it falls back to syntax. Keep that summary aligned with the command-bar
    preview instead of hiding known hook state immediately after Enter.
    """

    return f"showhook: {ed._hook_inventory_preview_summary('')}"


def _macro_runtime_root_summary(ed: "Editor") -> str:
    """Return one tiny runtime summary for raw ``macro``.

    Plain ``macro`` is still a usage-shaped umbrella command, but its
    no-arg path should keep one compact macro status+inventory witness
    visible before it falls back to syntax.
    """

    return f"macro: {ed._macro_root_preview_summary()}"


def _macro_subcommand_runtime_summary(ed: "Editor", subcommand: str) -> str:
    """Return one tiny runtime witness for one macro subcommand root.

    Command-line failures and direct editor/hostcall macro paths should use
    the same tiny blocker dialect, so reuse the editor-owned summary helper
    instead of rebuilding partial messages here.
    """

    return ed._macro_runtime_subcommand_summary(subcommand)


def _showdoc_runtime_root_summary(ed: "Editor") -> str:
    """Return one tiny runtime summary for raw ``showdoc``.

    Plain ``showdoc`` is still a usage-shaped exact inspector, but its
    no-arg path should keep one compact live docs-catalog witness visible
    before it falls back to syntax.
    """

    return f"showdoc: {ed._doc_inventory_preview_summary()}"


def _showtopic_runtime_root_summary(ed: "Editor") -> str:
    """Return one tiny runtime summary for raw ``showtopic``.

    Plain ``showtopic`` is still a usage-shaped exact inspector, but its
    no-arg path should keep one compact live topic-catalog witness visible
    before it falls back to syntax.
    """

    return f"showtopic: {ed._topic_inventory_preview_summary()}"


def _showkeymode_runtime_root_summary(ed: "Editor") -> str:
    """Return one tiny runtime summary for raw ``showkeymode``.

    Plain ``showkeymode`` is still a usage-shaped exact inspector, but its
    no-arg path should keep the live keymode inventory visible before it
    asks for one exact mode name.
    """

    return f"showkeymode: {ed._keymode_inventory_preview_summary()}"


def _showoption_runtime_root_summary(ed: "Editor") -> str:
    """Return one tiny runtime summary for raw ``showoption``.

    Plain ``showoption`` is still a usage-shaped exact inspector, but its
    no-arg path should keep one compact live option-inventory witness
    visible before it falls back to syntax.
    """

    return f"showoption: {ed._option_inventory_preview_summary()}"


def _showmark_runtime_root_summary(ed: "Editor") -> str:
    """Return one tiny runtime summary for raw ``showmark``.

    Plain ``showmark`` is still a usage-shaped exact inspector, but its
    no-arg path should keep one compact live mark-inventory witness visible
    before it falls back to syntax.
    """

    return f"showmark: {ed._mark_inventory_preview_summary()}"


def _showmacro_runtime_root_summary(ed: "Editor") -> str:
    """Return one tiny runtime summary for raw ``showmacro``.

    Plain ``showmacro`` is still a usage-shaped exact inspector, but its
    no-arg path should keep the same exact-root witness the command bar
    previews, including the default empty `last` slot when that is the most
    important inspectable truth on a fresh editor.
    """

    return f"showmacro: {ed._showmacro_root_preview_summary()}"


def _mark_runtime_root_summary(ed: "Editor", *, label: str) -> str:
    """Return one tiny runtime summary for raw ``mark`` / ``markjump``.

    The root mark-setting and mark-jump commands are still usage-shaped,
    but their no-arg paths should keep one compact live mark-inventory
    witness visible before they fall back to syntax.
    """

    return f"{label}: {ed._mark_inventory_preview_summary()}"


def _showbuffer_runtime_root_summary(ed: "Editor") -> str:
    """Return one tiny runtime summary for raw ``showbuffer``.

    Plain ``showbuffer`` is still a usage-shaped exact inspector, but its
    no-arg path should keep one compact live buffer-inventory witness
    visible before it falls back to syntax.
    """

    return f"showbuffer: {ed._buffer_inventory_preview_summary()}"


def _buffer_runtime_root_summary(ed: "Editor") -> str:
    """Return one tiny runtime summary for raw ``buffer``.

    Plain ``buffer`` is still a usage-shaped switching command, but its
    no-arg path should keep one compact live buffer-inventory witness
    visible before it falls back to syntax.
    """

    return f"buffer: {ed._buffer_inventory_preview_summary()}"


def _showjump_runtime_root_summary(ed: "Editor") -> str:
    """Return one tiny runtime summary for raw ``showjump``.

    Plain ``showjump`` is still a usage-shaped exact inspector, but its
    no-arg path should keep one compact live jumplist witness visible
    before it falls back to syntax.
    """

    return f"showjump: {ed._jump_inventory_preview_summary()}"


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


def _plugin_zero_error_state_suffix(ed: "Editor", name: str) -> str:
    """Return one tiny runtime suffix for known zero-error plugin targets.

    Exact command-bar previews already preserve the calm loaded/available
    state for ``plugin errors NAME`` / ``plugin info NAME``. Runtime
    filtered detail should not drift back to a bare ``errors: 0`` when
    Micromax already knows whether that target is loaded or merely
    available on disk.
    """

    state = _plugin_inventory_state(ed, name)
    if state == "available":
        return "available plugin · not loaded"
    if state == "loaded":
        return "loaded plugin"
    return ""


def _plugin_showplugin_detail(ed: "Editor", name: str, *, error_count: int, detail: str) -> str:
    """Return one tiny ``showplugin NAME`` detail suffix.

    ``showplugin NAME`` is the narrowest post-Enter exact plugin inspector.
    Keep it aligned with the exact command-bar row dialect: one known load
    error may show the raw detail directly, but multi-error targets should
    keep both the total count and the trailing detail witness instead of
    flattening back to only the last recorded string. When a plugin is
    healthy and lacks richer descriptive detail, still preserve one tiny
    loaded/available state witness so the exact runtime row stays concrete.
    """

    detail_text = str(detail or "").strip()
    count = int(error_count or 0)
    if count > 0:
        if not detail_text:
            return "1 load error" if count == 1 else f"{count} load errors"
        if count == 1:
            return detail_text
        return f"{count} load errors · last: {detail_text}"
    if detail_text:
        return detail_text
    state = _plugin_inventory_state(ed, name)
    if state == "loaded":
        return "loaded plugin"
    return _plugin_zero_error_state_suffix(ed, name)


def _plugin_error_count_line(count: int, state_suffix: str = "") -> str:
    """Return the tiny shared plugin-error count dialect.

    Plugin inventory/detail paths have become increasingly count-aware.
    Filtered detail should stay explicit too, so healthy plugins say
    ``errors: 0`` instead of falling back to ``(none)`` while broken
    plugins keep the same ``errors: N`` shape. Known available-but-unloaded
    targets may append a tiny runtime state suffix when the zero-error case
    would otherwise hide that witness.
    """

    line = f"  errors: {max(0, int(count))}"
    suffix = str(state_suffix or "").strip()
    if max(0, int(count)) == 0 and suffix:
        line += f" · {suffix}"
    return line


def _plugin_runtime_error_line(count: int, detail: str, *, state_suffix: str = "") -> str:
    """Return one tiny filtered runtime error-detail line.

    Exact rows and other runtime exact surfaces already preserve the last
    known plugin error detail for one broken target. Filtered ``plugin
    info NAME`` / ``plugin errors NAME`` should not drift back to a bare
    ``errors: N`` header when Micromax already knows the trailing witness.
    """

    total = max(0, int(count))
    suffix = str(state_suffix or "").strip()
    detail_text = str(detail or "").strip()
    if total <= 0:
        return _plugin_error_count_line(0, suffix)
    if not detail_text:
        return _plugin_error_count_line(total)
    if total == 1:
        return f"  errors: {detail_text}"
    return f"  errors: {total} load errors · last: {detail_text}"
