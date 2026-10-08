from __future__ import annotations

from pathlib import Path
import shlex
import sys

from .buffer import Cursor
from .buffer_scriptops import (
    BufferCapabilityError,
    dirty_buffer_names,
    require_buffer_discard_capability,
)
from .command_formatters import (
    _buffer_inventory_entry,
    _buffer_runtime_root_summary,
    _counted_inventory_summary,
    _describe_buffer,
    _describe_jump,
    _describe_mark,
    _describe_recent,
    _describe_recent_dir,
    _format_active_buffer_feedback,
    _format_cursor_target,
    _format_open_feedback,
    _format_recent_reopen_feedback,
    _format_revert_feedback,
    _format_save_feedback,
    _mark_inventory_entry,
    _mark_runtime_root_summary,
    _parse_diff_limit,
    _parse_linecol,
    _recent_inventory_entry,
    _section_summary_entry,
    _showbuffer_runtime_root_summary,
    _showjump_runtime_root_summary,
    _showmark_runtime_root_summary,
)
from .discard_guard import (
    DISCARD_CONFIRMED,
    DISCARD_REARMED,
    format_discard_warning,
)
from .file_scriptops import (
    checked_sandbox_path,
    chdir_under_caps,
    disk_diff_lines_under_caps,
    disk_state_rows_under_caps,
    fs_cap_root,
    revert_buffer_under_caps,
    save_current_buffer_under_caps,
)


def _command_dispatcher_checked_sandbox_path(ed: "Editor", raw_path: str) -> Path:
    """Resolve the sandbox checker through command_dispatcher when patched.

    Older tests and downstream probes monkeypatch
    ``micromax_editor.command_dispatcher.checked_sandbox_path`` because the
    open-command handler used to live in that module.  The command family now
    lives here, but preserving that seam keeps the late-symlink recheck probe
    useful instead of silently bypassing the monkeypatch.
    """

    dispatcher = sys.modules.get("micromax_editor.command_dispatcher")
    resolver = getattr(dispatcher, "checked_sandbox_path", checked_sandbox_path)
    return resolver(ed, raw_path)


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
        ed.message(_showbuffer_runtime_root_summary(ed))
        ed.message("usage: showbuffer NAME")
        return False
    name = str(args[0])
    msg = _describe_buffer(ed, name)
    if msg is None:
        ed.message(f"showbuffer: no such buffer: {name}")
        return False
    ed.message(msg)
    return True


def _showrecent_runtime_root_summary(ed: "Editor") -> str:
    """Return the tiny live recent-file witness plain ``showrecent`` reuses."""

    return f"showrecent: {ed._recent_inventory_preview_summary()}"


def c_showrecent(ed: "Editor", args: list[str]) -> bool:
    if not args:
        ed.message(_showrecent_runtime_root_summary(ed))
        ed.message("usage: showrecent PATH|N|#N")
        return False
    path = str(args[0])
    msg = _describe_recent(ed, path)
    if msg is None:
        ed.message(f"showrecent: no such recent file: {path}")
        return False
    ed.message(msg)
    return True


def _showrecentdir_runtime_root_summary(ed: "Editor") -> str:
    """Return the tiny live recent-directory witness plain ``showrecentdir`` reuses."""

    return f"showrecentdir: {ed._recent_dir_inventory_preview_summary()}"


def c_showrecentdir(ed: "Editor", args: list[str]) -> bool:
    if not args:
        ed.message(_showrecentdir_runtime_root_summary(ed))
        ed.message("usage: showrecentdir DIR|N|#N")
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
        ed.message(_showmark_runtime_root_summary(ed))
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
        ed.message(_showjump_runtime_root_summary(ed))
        ed.message("usage: showjump INDEX|#N")
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


def c_showjumpgroups(ed: "Editor", args: list[str]) -> bool:
    query = " ".join(str(x) for x in args).strip()
    rows = ed._resolved_section_summary_rows_for_command("showjumpgroups", query)
    total = sum(int(row[1]) for row in rows if isinstance(row, list) and len(row) >= 2)
    head = f"showjumpgroups{(' ' + query) if query else ''}: {len(rows)} section(s), {total} jump(s)"
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
            p = _command_dispatcher_checked_sandbox_path(ed, raw_path)
            ok = bool(ed.open_file(str(p), initial_cursor=initial_cursor, containment_root=fs_cap_root(ed)))
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


def c_new(ed: "Editor", args: list[str]) -> bool:
    """new [NAME] - create an empty, collision-free untitled buffer."""

    if len(args) > 1:
        ed.message("usage: new [NAME]")
        return False
    preferred = str(args[0]) if args else "*scratch*"
    try:
        ed.create_untitled_buffer(preferred)
    except Exception as e:
        ed.message(f"new: {e}")
        return False
    ed.message(_format_active_buffer_feedback(ed, prefix="new"))
    return True


def _save_command(ed: "Editor", args: list[str], *, force: bool = False) -> bool:
    # When a script executes commands (via `ed.command` / prompt-submit), we
    # enforce the same filesystem capability gates as `ed.save`.  The helper
    # also anchors relative paths under cap.fs-root before saving; otherwise
    # a script-owned relative buffer path could be validated against the
    # sandbox but written relative to the process cwd.
    if hasattr(ed, "in_script_context") and ed.in_script_context():
        try:
            info = save_current_buffer_under_caps(ed, force=force, target=str(args[0]) if args else None)
        except Exception as e:
            ed.message(f"save: {e}")
            return False
        ed.message(_format_save_feedback(info))
        return True

    # Interactive save: normal editor behavior.
    try:
        info = ed.save_as(str(args[0]), force=force) if args else ed.save(force=force)
    except Exception as e:
        ed.message(f"save: {e}")
        return False
    ed.message(_format_save_feedback(info))
    return True


def c_save(ed: "Editor", args: list[str]) -> bool:
    return _save_command(ed, args, force=False)


def c_save_bang(ed: "Editor", args: list[str]) -> bool:
    return _save_command(ed, args, force=True)


def c_saveas(ed: "Editor", args: list[str]) -> bool:
    """saveas FILE - save current buffer under a new path (alias for `save FILE`)."""
    if not args:
        ed.message("usage: saveas FILE")
        return False
    return c_save(ed, args)


def c_revert(ed: "Editor", args: list[str], *, force: bool = False) -> bool:
    """revert[!] - reload the current path-backed buffer from disk."""
    if args:
        ed.message("usage: revert" + ("!" if force else ""))
        return False
    try:
        if hasattr(ed, "in_script_context") and ed.in_script_context():
            info = revert_buffer_under_caps(ed, force=force)
        else:
            info = ed.revert_buffer_from_disk(force=force)
    except Exception as e:
        ed.message(f"revert: {e}")
        return False
    ed.message(_format_revert_feedback(info))
    return True


def c_revert_soft(ed: "Editor", args: list[str]) -> bool:
    return c_revert(ed, args, force=False)


def c_revert_bang(ed: "Editor", args: list[str]) -> bool:
    return c_revert(ed, args, force=True)


def _disk_state_entry(row: list[object]) -> str:
    vals = list(row) + [""] * 9
    name = str(vals[0])
    state = str(vals[1])
    warning = int(vals[2] or 0)
    changed = int(vals[3] or 0)
    missing = int(vals[4] or 0)
    dirty = int(vals[5] or 0)
    active = int(vals[6] or 0)
    path = str(vals[7] or "")
    error = str(vals[8] or "")
    flags: list[str] = []
    if warning:
        flags.append("warning")
    if changed:
        flags.append("changed")
    if missing:
        flags.append("missing")
    if dirty:
        flags.append("dirty")
    if active:
        flags.append("active")
    text = f"{name}={state or 'unknown'}"
    if path:
        text += f" {path}"
    if flags:
        text += " [" + ",".join(flags) + "]"
    if error:
        text += f" error={error}"
    return text


def c_diskstate(ed: "Editor", args: list[str]) -> bool:
    """diskstate [--all] - list per-buffer disk freshness/conflict states."""

    include_all = False
    for arg in args:
        value = str(arg)
        if value in {"--all", "-a", "all"}:
            include_all = True
            continue
        ed.message("usage: diskstate [--all]")
        return False
    if hasattr(ed, "in_script_context") and ed.in_script_context():
        rows = disk_state_rows_under_caps(ed, include_fresh=include_all)
    else:
        rows = ed.disk_state_rows(include_fresh=include_all)
    warning_count = sum(1 for row in rows if int((list(row) + [0, 0, 0])[2] or 0))
    if not rows:
        ed.message("diskstate: 0 warning buffers")
        return True
    label = "buffer" if warning_count == 1 else "buffers"
    suffix = " (all)" if include_all else ""
    ed.message(f"diskstate: {warning_count} warning {label}{suffix}")
    for row in rows:
        ed.message("diskstate: " + _disk_state_entry(list(row)))
    return True


def c_diff(ed: "Editor", args: list[str]) -> bool:
    """diff [N|--all] - show disk-vs-buffer unified diff for current file."""
    try:
        limit = _parse_diff_limit(args)
    except Exception as e:
        ed.message(f"diff: {e}")
        return False
    try:
        if hasattr(ed, "in_script_context") and ed.in_script_context():
            lines = disk_diff_lines_under_caps(ed, max_lines=limit)
        else:
            lines = ed.disk_diff_lines(max_lines=limit)
    except Exception as e:
        ed.message(f"diff: {e}")
        return False
    if not lines:
        ed.message("diff: no differences")
        return True
    hidden = 0
    if lines and str(lines[-1]).startswith("...") and "more diff line" in str(lines[-1]):
        try:
            hidden = int(str(lines[-1]).split()[1])
        except Exception:
            hidden = 0
    shown = len(lines) - (1 if hidden else 0)
    suffix = f", {hidden} omitted" if hidden else ""
    ed.message(f"diff: {shown} line{'s' if shown != 1 else ''}{suffix}")
    for line in lines:
        ed.message(str(line))
    return True


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
    if target:
        dirty = dirty_buffer_names(ed, [target])
        if dirty:
            try:
                require_buffer_discard_capability(ed, "close", dirty)
            except BufferCapabilityError as e:
                ed.message(str(e))
                return False
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
    if dirty:
        try:
            require_buffer_discard_capability(ed, "closeall", dirty)
        except BufferCapabilityError as e:
            ed.message(str(e))
            return False
    if dirty and not force:
        confirmation = ed._discard_confirmation_request("closeall")
        if confirmation != DISCARD_CONFIRMED:
            if confirmation == DISCARD_REARMED:
                ed.message(
                    format_discard_warning(
                        "closeall",
                        dirty,
                        force_hint="closeall -f",
                        refreshed=True,
                    )
                )
                return False
            ed.message(
                format_discard_warning("closeall", dirty, force_hint="closeall -f")
            )
            return False
    ed._clear_discard_confirmation()
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
    if dirty:
        try:
            require_buffer_discard_capability(ed, "only", dirty)
        except BufferCapabilityError as e:
            ed.message(str(e))
            return False
    if dirty and not force:
        confirmation = ed._discard_confirmation_request("only", keep=keep)
        if confirmation != DISCARD_CONFIRMED:
            if confirmation == DISCARD_REARMED:
                ed.message(
                    format_discard_warning(
                        "only",
                        dirty,
                        force_hint="only -f",
                        refreshed=True,
                    )
                )
                return False
            ed.message(format_discard_warning("only", dirty, force_hint="only -f"))
            return False
    ed._clear_discard_confirmation()
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
    try:
        ok = bool(ed.switch_buffer_checked(name) if hasattr(ed, "switch_buffer_checked") else ed.switch_buffer(name))
    except PermissionError as e:
        ed.message(f"prevbuf: {e}")
        return False
    if not ok:
        ed.message("prevbuf: no previous buffer")
        return False
    ed.message(_format_active_buffer_feedback(ed, prefix="prevbuf"))
    return True


def c_recent(ed: "Editor", args: list[str]) -> bool:
    """recent [N|#N|clear] - show or open recent files.

    - `recent` shows the MRU list (up to 12).
    - `recent N` opens the Nth entry (1-based).
    - `recent #N` opens the same visible slot using the picker/inventory dialect.
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
        forgotten = int(ed.clear_recent_files())
        ed.message(f"recent cleared: forgot {ed._count_label(forgotten, 'recent file')}")
        return True
    # open nth
    n = ed.parse_recent_slot_token(args[0])
    if n is None:
        ed.message('usage: recent [N|#N|clear]')
        return False
    # Recent slots are visible slots, not raw MRU indexes.  The MRU
    # register can contain trusted/user or other-origin path history that
    # lower-authority scripts are not allowed to inspect or replay; opening
    # by raw index would silently bypass the read filter.
    xs = list(ed.visible_recent_files()) if hasattr(ed, "visible_recent_files") else list(getattr(ed, 'recent_files', []))
    if n <= 0 or n > len(xs):
        ed.message(f"recent: no such recent file: {args[0]}")
        return False
    target = str(xs[n - 1])
    before = len(getattr(ed, 'messages', []))
    ok = bool(ed.exec_command_line('open ' + shlex.quote(target)))
    if ok:
        msg = _format_recent_reopen_feedback(ed, n, target)
        if len(getattr(ed, 'messages', [])) > before:
            ed.messages[-1] = msg
        else:
            ed.message(msg)
    return ok


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
        ed.message(_buffer_runtime_root_summary(ed))
        ed.message("usage: buffer NAME")
        return False
    name = str(args[0])
    try:
        ok = bool(ed.switch_buffer_checked(name) if hasattr(ed, "switch_buffer_checked") else ed.switch_buffer(name))
    except PermissionError as e:
        ed.message(f"buffer: {e}")
        return False
    if not ok:
        ed.message(f"buffer: no such buffer: {name}")
        return False
    ed.message(_format_active_buffer_feedback(ed, prefix="buffer"))
    return True


def c_mark(ed: "Editor", args: list[str]) -> bool:
    if not args:
        ed.message(_mark_runtime_root_summary(ed, label="mark"))
        ed.message("usage: mark NAME")
        return False
    name = str(args[0])
    try:
        ok = ed.mark_set(name)
    except PermissionError as e:
        ed.message(f"mark: {e}")
        return False
    if not ok:
        ed.message("mark: invalid name")
        return False
    ed.message(f"mark set: {name} -> {_format_cursor_target(ed)}")
    return True


def c_markjump(ed: "Editor", args: list[str]) -> bool:
    if not args:
        ed.message(_mark_runtime_root_summary(ed, label="markjump"))
        ed.message("usage: markjump NAME")
        return False
    name = str(args[0])
    try:
        ok = ed.mark_jump(name)
    except PermissionError as e:
        ed.message(f"markjump: {e}")
        return False
    if not ok:
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

    if hasattr(ed, "in_script_context") and ed.in_script_context():
        try:
            cwd = chdir_under_caps(ed, raw)
        except Exception as e:
            ed.message(f"cd: {e}")
            return False
        try:
            clear_display_cache = getattr(ed, "clear_path_display_cache", None)
            if callable(clear_display_cache):
                clear_display_cache()
            clear_docs_root_cache = getattr(ed, "clear_docs_root_cache", None)
            if callable(clear_docs_root_cache):
                clear_docs_root_cache()
        except Exception:
            pass
        ed.message(str(cwd))
        return True

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
    try:
        clear_display_cache = getattr(ed, "clear_path_display_cache", None)
        if callable(clear_display_cache):
            clear_display_cache()
        clear_docs_root_cache = getattr(ed, "clear_docs_root_cache", None)
        if callable(clear_docs_root_cache):
            clear_docs_root_cache()
    except Exception:
        pass
    ed.message(str(Path.cwd()))
    return True
