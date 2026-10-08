from __future__ import annotations

from .command_formatters import (
    _apropos_entry,
    _counted_inventory_summary,
    _jump_history_inventory_entry,
)


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
