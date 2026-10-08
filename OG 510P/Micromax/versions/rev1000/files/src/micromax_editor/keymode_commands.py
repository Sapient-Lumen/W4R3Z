from __future__ import annotations


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
