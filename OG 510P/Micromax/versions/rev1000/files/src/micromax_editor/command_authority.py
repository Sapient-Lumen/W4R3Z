from __future__ import annotations


def script_code_load_allowed(ed: "Editor", op: str) -> bool:
    """Return False when script-originated code-load operations lack authority."""

    try:
        in_script = bool(ed.in_script_context())
    except Exception:
        in_script = False
    if in_script and not bool(ed.options.get("cap.fs-require")):
        ed.message(f"{op}: disabled for scripts (cap.fs-require)")
        return False
    return True
