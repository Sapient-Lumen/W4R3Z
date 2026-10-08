from __future__ import annotations

from .command_formatters import (
    _apropos_entry,
    _describe_action,
    _describe_command,
    _describe_vm_word,
    _format_cursor_target,
)


def c_help(ed: "Editor", args: list[str]) -> bool:
    if not args:
        d = ed.command_dispatcher
        ed.message("Commands: " + ", ".join(d.names()))
        ed.message("Actions: " + ", ".join(ed.action_names()))
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


def c_helpforward(ed: "Editor", args: list[str]) -> bool:
    if args:
        ed.message("usage: helpforward")
        return False
    return bool(ed.help_forward())


def c_helphistory(ed: "Editor", args: list[str]) -> bool:
    if args:
        ed.message("usage: helphistory")
        return False
    ed.message(ed.help_history_inventory_summary())
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
        checked = ed.check_external_url(u)
        if not checked.ok:
            ed.message(f"urlopen: {checked.reason}: {u}")
            return False
        u = str(checked.url)
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
