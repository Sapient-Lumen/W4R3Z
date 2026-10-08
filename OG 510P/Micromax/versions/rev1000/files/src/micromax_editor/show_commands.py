from __future__ import annotations

from micromax.vm import HookWord

from .binding_commands import _no_such_binding
from .command_formatters import (
    _counted_inventory_summary,
    _describe_action,
    _describe_command,
    _describe_current_help_heading,
    _describe_current_help_link,
    _describe_doc,
    _describe_keymode,
    _describe_macro,
    _describe_option,
    _describe_topic,
    _describe_vm_word,
    _hook_summary_entry,
    _plugin_inventory_entry,
    _plugin_showplugin_detail,
    _section_summary_entry,
    _showdoc_runtime_root_summary,
    _showhook_runtime_root_summary,
    _showkeymode_runtime_root_summary,
    _showmacro_runtime_root_summary,
    _showoption_runtime_root_summary,
    _showplugin_runtime_root_summary,
    _showtopic_runtime_root_summary,
)



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


def _showkey_runtime_root_summary(ed: "Editor") -> str:
    """Return the tiny live binding witness plain ``showkey`` should reuse.

    Plain ``showkey`` is still a usage-shaped exact inspector, but its
    runtime root should keep the same compact reachable-binding truth
    visible that prompt completion already knows before asking for one key.
    """

    return f"showkey: {ed._binding_inventory_preview_summary()}"


def c_showkey(ed: "Editor", args: list[str]) -> bool:
    if not args:
        ed.message(_showkey_runtime_root_summary(ed))
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
    rows = ed.binding_detail_rows_for(mode)
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


def c_showkeymodes(ed: "Editor", args: list[str]) -> bool:
    if args:
        ed.message("usage: showkeymodes")
        return False
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
        ed.message(_showkeymode_runtime_root_summary(ed))
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
        ed.message(_showoption_runtime_root_summary(ed))
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


def c_showmacro(ed: "Editor", args: list[str]) -> bool:
    if not args:
        ed.message(_showmacro_runtime_root_summary(ed))
        ed.message("usage: showmacro NAME")
        return False
    name = str(args[0])
    msg = _describe_macro(ed, name)
    if msg is None:
        ed.message(f"showmacro: no such macro: {name}")
        return False
    ed.message(msg)
    return True


def _showcmd_runtime_root_summary(ed: "Editor") -> str:
    """Return one tiny runtime summary for raw ``showcmd``.

    Plain ``showcmd`` is still a usage-shaped exact inspector, but its
    runtime root should keep the same compact command-register truth visible
    that prompt completion already knows before asking for one command name.
    """

    return f"showcmd: {ed._command_inventory_preview_summary()}"


def c_showcmd(ed: "Editor", args: list[str]) -> bool:
    if not args:
        ed.message(_showcmd_runtime_root_summary(ed))
        ed.message("usage: showcmd NAME")
        return False
    name = args[0]
    msg = _describe_command(ed, name)
    if msg is None:
        ed.message(f"showcmd: no such command: {name}")
        return False
    ed.message(msg)
    return True


def _showaction_runtime_root_summary(ed: "Editor") -> str:
    """Return one tiny runtime summary for raw ``showaction``.

    Plain ``showaction`` is still a usage-shaped exact inspector, but its
    runtime root should keep the same compact live action-register truth
    visible that prompt completion already knows before asking for one
    action name.
    """

    return f"showaction: {ed._action_inventory_preview_summary()}"


def c_showaction(ed: "Editor", args: list[str]) -> bool:
    if not args:
        ed.message(_showaction_runtime_root_summary(ed))
        ed.message("usage: showaction NAME")
        return False
    name = args[0]
    msg = _describe_action(ed, name)
    if msg is None:
        ed.message(f"showaction: no such action: {name}")
        return False
    ed.message(msg)
    return True


def _showword_runtime_root_summary(ed: "Editor") -> str:
    """Return one tiny runtime summary for raw ``showword``.

    Plain ``showword`` is still a usage-shaped exact inspector, but its
    runtime root should keep the same compact visible-word truth visible
    that prompt completion already knows before asking for one word name.
    """

    return f"showword: {ed._word_inventory_preview_summary()}"


def c_showword(ed: "Editor", args: list[str]) -> bool:
    if not args:
        ed.message(_showword_runtime_root_summary(ed))
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
        ed.message(_showdoc_runtime_root_summary(ed))
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
        ed.message(_showtopic_runtime_root_summary(ed))
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
    if getattr(ed, "plugin_manager", None) is None:
        ed.message("showplugins: no plugin manager")
        return False
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
        ed.message(_showplugin_runtime_root_summary(ed))
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
    detail = _plugin_showplugin_detail(ed, plugin_name, error_count=error_count, detail=detail)
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
        ed.message(_showhook_runtime_root_summary(ed))
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
