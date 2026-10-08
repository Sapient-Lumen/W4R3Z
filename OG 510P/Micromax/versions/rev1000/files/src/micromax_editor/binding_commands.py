from __future__ import annotations

import shlex


def _binding_target(key: str, *, mode: str | None = None) -> str:
    return f"{key}@{mode}" if mode not in (None, "", "global") else str(key)


def _no_such_binding(cmd: str, key: str, *, mode: str | None = None) -> str:
    target = f"{key}@{mode}" if mode not in (None, "", "global") else str(key)
    return f"{cmd}: no such binding: {target}"


def c_bind(ed: "Editor", args: list[str]) -> bool:
    if len(args) < 2:
        ed.message("usage: bind KEY ACTIONSPEC")
        return False
    key = args[0]
    spec = " ".join(args[1:])
    try:
        ed.bind_key_checked(key, spec)
    except PermissionError as e:
        ed.message(f"bind: {e}")
        return False
    ed.message(f"bind: {_binding_target(key)} -> {spec}")
    return True


def c_bindmode(ed: "Editor", args: list[str]) -> bool:
    if len(args) < 3:
        ed.message("usage: bindmode MODE KEY ACTIONSPEC")
        return False
    mode = args[0]
    key = args[1]
    spec = " ".join(args[2:])
    try:
        ed.bind_key_checked(key, spec, mode=mode)
    except PermissionError as e:
        ed.message(f"bindmode: {e}")
        return False
    ed.message(f"bindmode: {_binding_target(key, mode=mode)} -> {spec}")
    return True


def c_binddoc(ed: "Editor", args: list[str]) -> bool:
    if len(args) < 2:
        ed.message("usage: binddoc KEY DOC...")
        return False
    key = args[0]
    doc = " ".join(args[1:]).strip()
    try:
        ok = ed.set_key_binding_desc_checked(key, doc)
    except PermissionError as e:
        ed.message(f"binddoc: {e}")
        return False
    if not ok:
        ed.message(_no_such_binding("binddoc", key))
        return False
    ed.message(f"binddoc: {_binding_target(key)} -> {doc}")
    return True


def c_bindmodedoc(ed: "Editor", args: list[str]) -> bool:
    if len(args) < 3:
        ed.message("usage: bindmodedoc MODE KEY DOC...")
        return False
    mode = args[0]
    key = args[1]
    doc = " ".join(args[2:]).strip()
    try:
        ok = ed.set_key_binding_desc_checked(key, doc, mode=mode)
    except PermissionError as e:
        ed.message(f"bindmodedoc: {e}")
        return False
    if not ok:
        ed.message(_no_such_binding("bindmodedoc", key, mode=mode))
        return False
    ed.message(f"bindmodedoc: {_binding_target(key, mode=mode)} -> {doc}")
    return True


def c_unbind(ed: "Editor", args: list[str]) -> bool:
    if not args:
        ed.message("usage: unbind KEY")
        return False
    key = args[0]
    try:
        ok = ed.unbind_key_checked(key)
    except PermissionError as e:
        ed.message(f"unbind: {e}")
        return False
    if not ok:
        ed.message(_no_such_binding("unbind", key))
        return False
    ed.message(f"unbind: {_binding_target(key)}")
    return True


def c_unbindmode(ed: "Editor", args: list[str]) -> bool:
    if len(args) < 2:
        ed.message("usage: unbindmode MODE KEY")
        return False
    mode = args[0]
    key = args[1]
    try:
        ok = ed.unbind_key_checked(key, mode=mode)
    except PermissionError as e:
        ed.message(f"unbindmode: {e}")
        return False
    if not ok:
        ed.message(_no_such_binding("unbindmode", key, mode=mode))
        return False
    ed.message(f"unbindmode: {_binding_target(key, mode=mode)}")
    return True


def c_bindprefix(ed: "Editor", args: list[str]) -> bool:
    if len(args) < 2:
        ed.message("usage: bindprefix KEY MODE [DOC...]")
        return False
    key = args[0]
    mode = args[1]
    doc = " ".join(args[2:]).strip() or f"prefix {mode}"
    spec = f"command:prefixmode {shlex.quote(mode)}"
    try:
        ed.bind_key_checked(key, spec, desc=doc)
    except PermissionError as e:
        ed.message(f"bindprefix: {e}")
        return False
    ed.message(f"bindprefix: {_binding_target(key)} -> {mode}")
    return True


def c_bindmodeprefix(ed: "Editor", args: list[str]) -> bool:
    if len(args) < 3:
        ed.message("usage: bindmodeprefix OWNERMODE KEY MODE [DOC...]")
        return False
    owner_mode = args[0]
    key = args[1]
    mode = args[2]
    doc = " ".join(args[3:]).strip() or f"prefix {mode}"
    spec = f"command:prefixmode {shlex.quote(mode)}"
    try:
        ed.bind_key_checked(key, spec, mode=owner_mode, desc=doc)
    except PermissionError as e:
        ed.message(f"bindmodeprefix: {e}")
        return False
    ed.message(f"bindmodeprefix: {_binding_target(key, mode=owner_mode)} -> {mode}")
    return True
