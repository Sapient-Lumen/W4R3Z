from __future__ import annotations

from .command_formatters import _option_inventory_entry


def c_set(ed: "Editor", args: list[str]) -> bool:
    if len(args) < 2:
        ed.message("usage: set OPTION VALUE")
        return False
    name = args[0]
    raw = " ".join(args[1:])
    try:
        val = ed.set_option_value(name, raw)
    except Exception as e:
        ed.message(f"set: {e}")
        return False
    ed.message(f"set: {name}={val}")
    return True


def c_setlocal(ed: "Editor", args: list[str]) -> bool:
    if len(args) < 2:
        ed.message("usage: setlocal OPTION VALUE")
        return False
    name = args[0]
    raw = " ".join(args[1:])
    try:
        val = ed.set_option_value(name, raw, local=True)
    except Exception as e:
        ed.message(f"setlocal: {e}")
        return False
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
    try:
        val = ed.toggle_option_value(name)
    except Exception as e:
        ed.message(f"toggle: {e}")
        return False
    ed.message(f"toggle: {name}={val}")
    return True


def c_togglelocal(ed: "Editor", args: list[str]) -> bool:
    if not args:
        ed.message("usage: togglelocal OPTION")
        return False
    name = args[0]
    try:
        val = ed.toggle_option_value(name, local=True)
    except Exception as e:
        ed.message(f"togglelocal: {e}")
        return False
    ed.message(f"togglelocal: {name}(local)={val}")
    return True
