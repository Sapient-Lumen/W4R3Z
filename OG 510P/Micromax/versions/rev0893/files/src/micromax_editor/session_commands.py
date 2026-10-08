from __future__ import annotations

from .buffer_scriptops import (
    BufferCapabilityError,
    require_buffer_discard_capability,
)
from .command_authority import script_code_load_allowed


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


def c_reload(ed: "Editor", args: list[str]) -> bool:
    if not script_code_load_allowed(ed, "reload"):
        return False
    return ed.reload_runtime()
