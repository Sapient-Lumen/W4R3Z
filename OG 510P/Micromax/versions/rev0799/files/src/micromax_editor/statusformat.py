from __future__ import annotations

from typing import Any, TYPE_CHECKING


if TYPE_CHECKING:  # pragma: no cover
    from .editor import Editor


def _fmt_bool(v: object) -> str:
    return "true" if bool(v) else "false"


def _binding_for_action_spec(ed: "Editor", action_spec: str) -> str:
    """Return a representative key bound to `action_spec`.

    This is best-effort and deterministic: we scan resolved bindings in the
    currently-active key modes and return the first key (sorted order).
    """

    target = str(action_spec or "").strip()
    if not target:
        return ""

    rows = ed.keymap.resolved_binding_rows(ed.active_key_modes())
    for row in rows:
        # [mode, key, action_spec, group, span]
        try:
            spec = str(row[2])
            key = str(row[1])
        except Exception:
            continue
        if spec == target:
            return key
    return ""


def _opt_value(ed: "Editor", name: str, status: dict[str, Any]) -> str:
    n = str(name or "").strip()
    if not n:
        return ""

    # 1) registered options (buffer-local first)
    try:
        eb = ed.cur()
        v = ed.options.get(n, local=eb.local_options)
        if isinstance(v, bool):
            return _fmt_bool(v)
        return str(v)
    except Exception:
        pass

    # 2) fall back to status model keys (handy for filetype/encoding)
    if n in status:
        v = status.get(n)
        if isinstance(v, bool):
            return _fmt_bool(v)
        return str(v)
    return ""


def _truthy(s: str) -> bool:
    v = str(s or "").strip().lower()
    if v in ("", "0", "false", "off", "no", "none", "null"):
        return False
    return True


def _split_unescaped(s: str, *, sep: str = "|") -> list[str]:
    r"""Split s on unescaped separators.

    We support a tiny escape syntax:
      - \\ escapes itself
      - \| (or \\ + sep) escapes the separator

    This keeps the statusformat conditional directive usable without adding a
    full parser.
    """
    out: list[str] = []
    cur: list[str] = []
    i = 0
    while i < len(s):
        ch = s[i]
        if ch == "\\" and i + 1 < len(s):
            cur.append(s[i + 1])
            i += 2
            continue
        if ch == sep:
            out.append("".join(cur))
            cur = []
            i += 1
            continue
        cur.append(ch)
        i += 1
    out.append("".join(cur))
    return out


def _parse_expr(expr: str) -> tuple[str, str | None]:
    inner = str(expr or "").strip()
    if not inner:
        return ("", None)
    if ":" in inner:
        name, arg = inner.split(":", 1)
        return (name.strip(), arg.strip())
    return (inner, None)


def _directive_value(ed: "Editor", name: str, arg: str | None, status: dict[str, Any], *, depth: int) -> str:
    n = str(name or "").strip()
    a = None if arg is None else str(arg)

    if not n:
        return ""

    # micro-like core directives
    if n == "filename":
        return str(status.get("display_name", status.get("file_name", "")) or "")
    if n == "modified":
        return "*" if int(status.get("dirty", 0) or 0) else ""
    if n == "line":
        return str(int(status.get("display_line", 0) or 0))
    if n == "col":
        return str(int(status.get("display_col", 0) or 0))
    if n == "lines":
        return str(int(status.get("line_count", 0) or 0))
    if n == "percentage":
        return str(int(status.get("percentage", 0) or 0))
    if n == "overwrite":
        # We don't have a real overwrite mode yet, but keeping the directive
        # makes ported micro statusformat strings usable.
        return ""
    if n == "opt":
        return _opt_value(ed, a or "", status)
    if n == "bind":
        return _binding_for_action_spec(ed, a or "")

    # Tiny conditional:
    #   $(if:COND|THEN|ELSE)
    # - COND is a directive-like expression (e.g. "modified" or "opt:filetype")
    # - THEN/ELSE are themselves templates (so they can contain $() directives)
    if n == "if":
        if depth >= 8:
            return ""
        parts = _split_unescaped(a or "", sep="|")
        if not parts:
            return ""
        cond_expr = parts[0].strip()
        then_t = parts[1] if len(parts) >= 2 else ""
        else_t = parts[2] if len(parts) >= 3 else ""
        cn, ca = _parse_expr(cond_expr)
        cond_val = _directive_value(ed, cn, ca, status, depth=depth + 1) if cn else ""
        chosen = then_t if _truthy(cond_val) else else_t
        return render_status_template(chosen, ed=ed, status=status, _depth=depth + 1)

    # Micromax-editor extensions (useful for default templates)
    if n in ("ro", "readonly"):
        return " [RO]" if int(status.get("readonly", 0) or 0) else ""
    if n in ("disk", "diskstate"):
        summary = str(status.get("disk_summary", "") or "").strip()
        return f" [{summary}]" if summary else ""
    if n in ("km", "keymode"):
        km = str(status.get("keymode", "") or "")
        if not km:
            return ""
        suffix = "!" if int(status.get("keymode_once", 0) or 0) else ""
        return f" [{km}{suffix}]"
    if n in ("sel", "sels"):
        sc = int(status.get("selection_count", 0) or 0)
        return f" sel:{sc}" if sc else ""
    if n in ("cur", "cursors"):
        cs = str(status.get("cursor_summary", "") or "")
        return f" cur:{cs}" if cs else ""
    if n in ("search", "searchpos", "searchcount"):
        ss = str(status.get("search_summary", "") or "")
        return f" [{ss}]" if ss else ""
    if n in ("bufpos", "bufferpos", "buffers"):
        bs = str(status.get("buffer_summary", "") or "")
        bc = int(status.get("buffer_count", 0) or 0)
        return f" [{bs}]" if bc > 1 and bs else ""
    if n == "macro":
        if int(status.get("macro_recording", 0) or 0):
            return " REC"
        if int(status.get("macro_playing", 0) or 0):
            return " PLAY"
        return ""

    # Fall back: if the directive is a key in status_model, substitute it.
    if n in status:
        v = status.get(n)
        if isinstance(v, bool):
            return _fmt_bool(v)
        return str(v)

    return ""


def render_status_template(template: str, *, ed: "Editor", status: dict[str, Any], _depth: int = 0) -> str:
    """Render a micro-esque status format template.

    Directives are embedded as `$()` forms, e.g. `$(filename)` or `$(opt:filetype)`.
    `$$` escapes a literal `$`.

    Extension:
      - `$(if:COND|THEN|ELSE)` — tiny conditional with `|` separators.
    """

    s = str(template or "")
    if not s:
        return ""

    out: list[str] = []
    i = 0
    while i < len(s):
        ch = s[i]
        if ch != "$":
            out.append(ch)
            i += 1
            continue

        # Escaped '$'
        if i + 1 < len(s) and s[i + 1] == "$":
            out.append("$")
            i += 2
            continue

        # Directive
        if i + 1 < len(s) and s[i + 1] == "(":
            j = s.find(")", i + 2)
            if j == -1:
                # Unterminated; treat literally.
                out.append("$(")
                i += 2
                continue
            inner = s[i + 2 : j].strip()
            if ":" in inner:
                name, arg = inner.split(":", 1)
                out.append(_directive_value(ed, name.strip(), arg.strip(), status, depth=_depth))
            else:
                out.append(_directive_value(ed, inner, None, status, depth=_depth))
            i = j + 1
            continue

        # Lone '$'
        out.append("$")
        i += 1

    return "".join(out)
