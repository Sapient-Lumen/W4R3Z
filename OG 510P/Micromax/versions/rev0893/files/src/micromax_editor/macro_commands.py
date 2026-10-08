from __future__ import annotations

from .command_formatters import _macro_runtime_root_summary, _macro_subcommand_runtime_summary

MACRO_ROOT_DOC = "macro record/rec/start|stop/end|cancel/abort|play/run|list/ls|status/st - keyboard macros"
MACRO_ROOT_USAGE = "usage: macro record|rec|start|stop|end|cancel|abort|play|run|list|ls|status|st ..."


def c_macro(ed: "Editor", args: list[str]) -> bool:
    """Manage keyboard macros.

    Subcommands:
      - macro record|rec|start [name]
      - macro stop|end
      - macro cancel|abort
      - macro play|run [name] [count]
      - macro list|ls
      - macro status|st
    """

    if not args:
        ed.message(_macro_runtime_root_summary(ed))
        ed.message(MACRO_ROOT_USAGE)
        return False

    sub = str(args[0] if args else '').strip().lower()
    if sub in ("record", "rec", "start"):
        if len(args) > 2:
            ed.message(f"macro {sub}: takes at most 1 arg")
            ed.message(f"usage: macro {sub} [NAME]")
            return False
        if ed._macro_playing or ed.macro_recording:
            ed.message(_macro_subcommand_runtime_summary(ed, sub))
            return False
        name = args[1] if len(args) >= 2 else "last"
        return bool(ed.start_macro(name))
    if sub in ("stop", "end"):
        if len(args) > 1:
            ed.message(f"macro {sub}: takes no args")
            ed.message(f"usage: macro {sub}")
            return False
        if ed._macro_playing or not ed.macro_recording:
            ed.message(_macro_subcommand_runtime_summary(ed, sub))
            return False
        return bool(ed.stop_macro())
    if sub in ("cancel", "abort"):
        if len(args) > 1:
            ed.message(f"macro {sub}: takes no args")
            ed.message(f"usage: macro {sub}")
            return False
        if ed._macro_playing or not ed.macro_recording:
            ed.message(_macro_subcommand_runtime_summary(ed, sub))
            return False
        return bool(ed.cancel_macro())
    if sub in ("play", "run"):
        if len(args) > 3:
            ed.message(f"macro {sub}: takes at most 2 args")
            ed.message(f"usage: macro {sub} [NAME] [COUNT]")
            return False
        if ed._macro_playing or ed.macro_recording:
            ed.message(_macro_subcommand_runtime_summary(ed, sub))
            return False
        name = args[1] if len(args) >= 2 else "last"
        count = 1
        if len(args) >= 3:
            try:
                count = int(args[2], 10)
            except ValueError:
                ed.message(ed._macro_invalid_count_type_runtime_message(sub))
                return False
        if count <= 0:
            ed.message(ed._macro_invalid_count_runtime_message(sub))
            return False
        steps = ed.macros.get(str(name), None)
        if steps is None and str(name) == 'last':
            steps = ed.macro
        if not steps:
            if str(name) == 'last':
                ed.message(ed._macro_default_slot_empty_runtime_message(sub))
            else:
                ed.message(ed._macro_missing_runtime_message(str(name), sub))
            return False
        return bool(ed.play_macro(name, count=count))
    if sub in ("list", "ls"):
        if len(args) > 1:
            ed.message(f"macro {sub}: takes no args")
            ed.message(f"usage: macro {sub}")
            return False
        ed.message(ed.macro_list_message())
        return True
    if sub in ("status", "st"):
        if len(args) > 1:
            ed.message(f"macro {sub}: takes no args")
            ed.message(f"usage: macro {sub}")
            return False
        ed.message(ed.macro_status_message())
        return True

    ed.message(f"macro: no such subcommand: {sub}")
    return False
