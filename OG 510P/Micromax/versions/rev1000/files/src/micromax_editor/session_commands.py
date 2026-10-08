from __future__ import annotations

from .buffer_scriptops import (
    BufferCapabilityError,
    require_buffer_discard_capability,
)
from .command_authority import script_code_load_allowed
from .discard_guard import (
    DISCARD_CONFIRMED,
    DISCARD_REARMED,
    format_discard_warning,
)


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


def c_undostatus(ed: "Editor", args: list[str]) -> bool:
    if args:
        ed.message("usage: undostatus")
        return False
    ed.message(ed.undo_status_message())
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
    if dirty:
        try:
            require_buffer_discard_capability(ed, "quit", dirty)
        except BufferCapabilityError as e:
            ed.message(str(e))
            return False
    if dirty and not force:
        confirmation = ed._discard_confirmation_request("quit")
        if confirmation == DISCARD_CONFIRMED:
            ed.should_quit = True
            return True
        if confirmation == DISCARD_REARMED:
            ed.message(
                format_discard_warning(
                    "quit", dirty, force_hint="quit -f", refreshed=True
                )
            )
            return False
        ed.message(format_discard_warning("quit", dirty, force_hint="quit -f"))
        return False

    ed._clear_discard_confirmation()
    ed.should_quit = True
    return True


def c_reload(ed: "Editor", args: list[str]) -> bool:
    if not script_code_load_allowed(ed, "reload"):
        return False
    return ed.reload_runtime()
