from __future__ import annotations

import os
import re
import shlex
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Mapping

from vhk.i3.ipc import I3Connection, discover_socket_path
from vhk.system.session import detect_backend


_TRUTHY = {"1", "true", "yes", "on"}


def _env_truthy(value: str | None) -> bool:
    return bool(value) and value.strip().lower() in _TRUTHY


def _shell_env_prefix(env: Mapping[str, str | None], *names: str) -> str:
    parts: list[str] = []
    for name in names:
        value = env.get(name)
        if value:
            parts.append(f"{name}={shlex.quote(value)}")
    return " ".join(parts)


def build_clear_stuck_keys_hint(env: Mapping[str, str | None] | None = None) -> dict[str, Any]:
    env_map = os.environ if env is None else env
    backend = detect_backend()
    x11vnc = shutil.which("x11vnc")
    prefix = _shell_env_prefix(env_map, "DISPLAY", "XAUTHORITY")
    command = " ".join(p for p in [prefix, "x11vnc -deny_all -clear_keys -timeout 1"] if p)

    if backend != "x11":
        return {
            "backend": backend,
            "available": False,
            "reason": "x11_only",
            "tool": x11vnc,
            "command": None,
            "notes": [
                "Recovery command is intended for X11 sessions.",
                "Wayland sessions should prefer ResetModifiers / compositor-specific recovery tools.",
            ],
        }

    return {
        "backend": backend,
        "available": bool(x11vnc),
        "reason": None if x11vnc else "x11vnc_missing",
        "tool": x11vnc,
        "command": command,
        "notes": [
            "Releases pressed keys on the target X11 display.",
            "Can interfere with someone actively typing at the physical keyboard.",
        ],
    }


def _parse_busctl_address(stdout: str) -> str | None:
    match = re.search(r'"([^"]+)"', stdout)
    if match:
        return match.group(1)
    text = stdout.strip()
    if text.startswith("s "):
        return text[2:].strip()
    return text or None


def _run_probe(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, capture_output=True, text=True, timeout=3)


def probe_accessibility_bus(env: Mapping[str, str | None] | None = None) -> dict[str, Any]:
    env_map = os.environ if env is None else env
    busctl = shutil.which("busctl")
    gsettings = shutil.which("gsettings")
    disabled = _env_truthy(env_map.get("NO_AT_BRIDGE"))

    result: dict[str, Any] = {
        "disabled_by_env": disabled,
        "probe_tool": "busctl" if busctl else None,
        "tool": busctl,
        "status": "not_checked",
        "address": None,
        "registry_available": None,
        "error": None,
        "toolkit_accessibility": None,
        "commands": {
            "get_address": "busctl --user call org.a11y.Bus /org/a11y/bus org.a11y.Bus GetAddress",
            "check_registry": "busctl --address=ADDRESS list | grep org.a11y.atspi.Registry",
            "enable_toolkit_accessibility": "gsettings set org.gnome.desktop.interface toolkit-accessibility true",
        },
    }

    if gsettings:
        try:
            proc = _run_probe([gsettings, "get", "org.gnome.desktop.interface", "toolkit-accessibility"])
            if proc.returncode == 0:
                result["toolkit_accessibility"] = (proc.stdout or "").strip()
        except Exception:
            pass

    if disabled:
        result["status"] = "disabled_by_env"
        return result

    if not busctl:
        result["status"] = "probe_tool_missing"
        return result

    try:
        proc = _run_probe([
            busctl,
            "--user",
            "call",
            "org.a11y.Bus",
            "/org/a11y/bus",
            "org.a11y.Bus",
            "GetAddress",
        ])
    except Exception as exc:
        result["status"] = "probe_failed"
        result["error"] = str(exc)
        return result

    if proc.returncode != 0:
        result["status"] = "probe_failed"
        result["error"] = (proc.stderr or proc.stdout).strip() or "GetAddress failed"
        return result

    address = _parse_busctl_address(proc.stdout)
    result["address"] = address
    if not address:
        result["status"] = "address_unparsed"
        result["error"] = "GetAddress succeeded but returned an unparseable value"
        return result

    try:
        list_proc = _run_probe([busctl, f"--address={address}", "list"])
    except Exception as exc:
        result["status"] = "address_ok_registry_unknown"
        result["error"] = str(exc)
        return result

    if list_proc.returncode != 0:
        result["status"] = "address_ok_registry_unknown"
        result["error"] = (list_proc.stderr or list_proc.stdout).strip() or "registry listing failed"
        return result

    registry_available = "org.a11y.atspi.Registry" in list_proc.stdout
    result["registry_available"] = registry_available
    result["status"] = "ok" if registry_available else "registry_missing"
    return result


def _parse_busctl_uint(stdout: str) -> int | None:
    # busctl get-property prints like: "u 2" or "u 1".
    m = re.search(r"\b(\d+)\b", stdout)
    if not m:
        return None
    try:
        return int(m.group(1))
    except Exception:
        return None


def probe_xdg_portal_screenshot(env: Mapping[str, str | None] | None = None) -> dict[str, Any]:
    """Probe whether the XDG Screenshot portal interface is available."""

    env_map = os.environ if env is None else env
    busctl = shutil.which("busctl")
    backend = detect_backend()

    result: dict[str, Any] = {
        "backend": backend,
        "probe_tool": "busctl" if busctl else None,
        "tool": busctl,
        "status": "not_checked",
        "screenshot_version": None,
        "error": None,
        "commands": {
            "get_screenshot_version": "busctl --user get-property org.freedesktop.portal.Desktop /org/freedesktop/portal/desktop org.freedesktop.portal.Screenshot version",
        },
    }

    if not busctl:
        result["status"] = "probe_tool_missing"
        return result

    try:
        proc = _run_probe(
            [
                busctl,
                "--user",
                "get-property",
                "org.freedesktop.portal.Desktop",
                "/org/freedesktop/portal/desktop",
                "org.freedesktop.portal.Screenshot",
                "version",
            ]
        )
    except Exception as exc:
        result["status"] = "probe_failed"
        result["error"] = str(exc)
        return result

    if proc.returncode != 0:
        err = (proc.stderr or proc.stdout).strip()
        result["error"] = err or "get-property failed"
        if "No such interface" in err:
            result["status"] = "interface_missing"
        elif "org.freedesktop.portal.Desktop" in err and ("not provided" in err or "Unknown" in err or "No such service" in err or "not found" in err):
            result["status"] = "service_missing"
        else:
            result["status"] = "probe_failed"
        return result

    version = _parse_busctl_uint(proc.stdout)
    result["screenshot_version"] = version
    result["status"] = "ok" if version is not None else "unparsed"
    return result


def probe_xdg_portal_global_shortcuts(env: Mapping[str, str | None] | None = None) -> dict[str, Any]:
    """Probe whether the XDG GlobalShortcuts portal interface is available."""

    env_map = os.environ if env is None else env
    busctl = shutil.which("busctl")
    backend = detect_backend()

    result: dict[str, Any] = {
        "backend": backend,
        "probe_tool": "busctl" if busctl else None,
        "tool": busctl,
        "status": "not_checked",
        "global_shortcuts_version": None,
        "error": None,
        "commands": {
            "get_global_shortcuts_version": "busctl --user get-property org.freedesktop.portal.Desktop /org/freedesktop/portal/desktop org.freedesktop.portal.GlobalShortcuts version",
        },
    }

    if not busctl:
        result["status"] = "probe_tool_missing"
        return result

    try:
        proc = _run_probe(
            [
                busctl,
                "--user",
                "get-property",
                "org.freedesktop.portal.Desktop",
                "/org/freedesktop/portal/desktop",
                "org.freedesktop.portal.GlobalShortcuts",
                "version",
            ]
        )
    except Exception as exc:
        result["status"] = "probe_failed"
        result["error"] = str(exc)
        return result

    if proc.returncode != 0:
        err = (proc.stderr or proc.stdout).strip()
        result["error"] = err or "get-property failed"
        if "No such interface" in err:
            result["status"] = "interface_missing"
        elif "org.freedesktop.portal.Desktop" in err and (
            "not provided" in err or "Unknown" in err or "No such service" in err or "not found" in err
        ):
            result["status"] = "service_missing"
        else:
            result["status"] = "probe_failed"
        return result

    version = _parse_busctl_uint(proc.stdout)
    result["global_shortcuts_version"] = version
    result["status"] = "ok" if version is not None else "unparsed"
    return result


def probe_xdg_portal_remote_desktop(env: Mapping[str, str | None] | None = None) -> dict[str, Any]:
    """Probe whether the XDG RemoteDesktop portal interface is available."""

    env_map = os.environ if env is None else env
    busctl = shutil.which("busctl")
    backend = detect_backend()

    result: dict[str, Any] = {
        "backend": backend,
        "probe_tool": "busctl" if busctl else None,
        "tool": busctl,
        "status": "not_checked",
        "remote_desktop_version": None,
        "available_device_types": None,
        "error": None,
        "commands": {
            "get_remote_desktop_version": "busctl --user get-property org.freedesktop.portal.Desktop /org/freedesktop/portal/desktop org.freedesktop.portal.RemoteDesktop version",
            "get_available_device_types": "busctl --user get-property org.freedesktop.portal.Desktop /org/freedesktop/portal/desktop org.freedesktop.portal.RemoteDesktop AvailableDeviceTypes",
        },
    }

    if not busctl:
        result["status"] = "probe_tool_missing"
        return result

    def _gp(prop: str) -> tuple[int | None, str | None, int]:
        try:
            proc = _run_probe(
                [
                    busctl,
                    "--user",
                    "get-property",
                    "org.freedesktop.portal.Desktop",
                    "/org/freedesktop/portal/desktop",
                    "org.freedesktop.portal.RemoteDesktop",
                    prop,
                ]
            )
        except Exception as exc:
            return None, str(exc), 1
        if proc.returncode != 0:
            return None, (proc.stderr or proc.stdout).strip() or "get-property failed", proc.returncode
        return _parse_busctl_uint(proc.stdout), None, 0

    v, err, rc = _gp("version")
    if rc != 0:
        result["error"] = err
        if err and "No such interface" in err:
            result["status"] = "interface_missing"
        elif err and "org.freedesktop.portal.Desktop" in err and (
            "not provided" in err or "Unknown" in err or "No such service" in err or "not found" in err
        ):
            result["status"] = "service_missing"
        else:
            result["status"] = "probe_failed"
        return result

    result["remote_desktop_version"] = v
    dt, _, _ = _gp("AvailableDeviceTypes")
    result["available_device_types"] = dt
    result["status"] = "ok" if v is not None else "unparsed"
    return result


def _parse_xdpyinfo_extensions(stdout: str) -> list[str]:
    names: list[str] = []
    capture = False
    for raw_line in stdout.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("number of extensions:"):
            capture = True
            continue
        if capture:
            if raw_line.startswith("screen #") or raw_line.startswith("default screen number"):
                break
            name = stripped.split()[0]
            if name and name not in names:
                names.append(name)
    return names


def probe_x11_extensions(env: Mapping[str, str | None] | None = None) -> dict[str, Any]:
    env_map = os.environ if env is None else env
    backend = detect_backend()
    display = env_map.get("DISPLAY")
    xdpyinfo = shutil.which("xdpyinfo")

    result: dict[str, Any] = {
        "backend": backend,
        "display": display,
        "probe_tool": "xdpyinfo" if xdpyinfo else None,
        "tool": xdpyinfo,
        "status": "not_checked",
        "xtest_available": None,
        "record_available": None,
        "xinput_available": None,
        "extensions": [],
        "error": None,
        "commands": {
            "query_extensions": "xdpyinfo -queryExtensions",
            "show_xtest": "xdpyinfo -ext XTEST",
            "show_record": "xdpyinfo -ext RECORD",
        },
    }

    if not display:
        result["status"] = "display_missing"
        return result
    if backend != "x11":
        result["status"] = "not_x11"
        return result
    if not xdpyinfo:
        result["status"] = "probe_tool_missing"
        return result

    try:
        proc = _run_probe([xdpyinfo, "-queryExtensions"])
    except Exception as exc:
        result["status"] = "probe_failed"
        result["error"] = str(exc)
        return result

    if proc.returncode != 0:
        result["status"] = "probe_failed"
        result["error"] = (proc.stderr or proc.stdout).strip() or "xdpyinfo failed"
        return result

    extensions = _parse_xdpyinfo_extensions(proc.stdout)
    result["extensions"] = extensions
    extset = {ext.upper() for ext in extensions}
    result["xtest_available"] = "XTEST" in extset
    result["record_available"] = "RECORD" in extset
    result["xinput_available"] = any(ext in extset for ext in {"XINPUTEXTENSION", "XINPUT", "XINPUTEXT"})
    result["status"] = "ok"
    return result




def _parse_lsmod(stdout: str) -> set[str]:
    mods: set[str] = set()
    for line in (stdout or '').splitlines():
        parts = line.strip().split()
        if not parts or parts[0] == 'Module':
            continue
        mods.add(parts[0])
    return mods


def probe_uinput(path: str | Path = "/dev/uinput", *, lsmod_text: str | None = None) -> dict[str, Any]:
    """Probe whether /dev/uinput is present and writable for the current user.

    This is the most common Wayland automation footgun for tools like ydotool,
    kanata, kmonad, etc.

    Notes
    -----
    - Some distros load the uinput module lazily; if the device node never
      appears, ensure the `uinput` kernel module is loaded at boot.
    - Permissions are typically managed via a udev rule that sets GROUP/MODE and
      optionally TAG+=\"uaccess\".
    """

    p = Path(path)
    result: dict[str, Any] = {
        "path": str(p),
        "exists": p.exists(),
        "status": "not_checked",
        "mode": None,
        "uid": None,
        "gid": None,
        "group": None,
        "can_write": None,
        "module_loaded": None,
        "error": None,
        "suggested_rules": {
            "group_uinput": 'KERNEL=="uinput", GROUP="uinput", MODE="0660", OPTIONS+="static_node=uinput"',
            "group_input": 'KERNEL=="uinput", GROUP="input", MODE="0660", OPTIONS+="static_node=uinput"',
            "uaccess": 'KERNEL=="uinput", SUBSYSTEM=="misc", TAG+=\"uaccess\", OPTIONS+="static_node=uinput"',
        },
    }

    # Module probe (best-effort).
    if lsmod_text is None:
        lsmod = shutil.which('lsmod')
        if lsmod:
            try:
                proc = _run_probe([lsmod])
                if proc.returncode == 0:
                    lsmod_text = proc.stdout
            except Exception:
                pass
    if lsmod_text is not None:
        mods = _parse_lsmod(lsmod_text)
        result["module_loaded"] = "uinput" in mods

    if not p.exists():
        result["status"] = "missing"
        return result

    try:
        st = p.stat()
        result["mode"] = oct(st.st_mode & 0o777)
        result["uid"] = st.st_uid
        result["gid"] = st.st_gid
        try:
            import grp

            result["group"] = grp.getgrgid(st.st_gid).gr_name
        except Exception:
            result["group"] = None

        # Try opening for write.
        try:
            fd = os.open(str(p), os.O_WRONLY | getattr(os, 'O_CLOEXEC', 0))
            os.close(fd)
            result["can_write"] = True
        except PermissionError:
            result["can_write"] = False
        except Exception as exc:
            result["can_write"] = False
            result["error"] = str(exc)

    except Exception as exc:
        result["status"] = "stat_failed"
        result["error"] = str(exc)
        return result

    result["status"] = "ok" if result.get("can_write") else "permission_denied"
    return result


_WAYLAND_INTERFACE_RE = re.compile(r"interface: '([^']+)'|interface: \"([^\"]+)\"", re.IGNORECASE)
_WAYLAND_GLOBAL_RE = re.compile(r"\bglobal\b[^\n]*\b([a-zA-Z0-9_]+)\b")


def probe_wayland_protocols(env: Mapping[str, str | None] | None = None) -> dict[str, Any]:
    """Probe advertised Wayland globals via `wayland-info` when available.

    This is best-effort and intended for diagnostics, not strict capability
    gating: compositors can advertise globals yet restrict them at runtime.
    """

    env_map = os.environ if env is None else env
    backend = detect_backend()
    wayland_display = env_map.get("WAYLAND_DISPLAY")
    wayland_info = shutil.which("wayland-info")

    result: dict[str, Any] = {
        "backend": backend,
        "wayland_display": wayland_display,
        "probe_tool": "wayland-info" if wayland_info else None,
        "tool": wayland_info,
        "status": "not_checked",
        "interfaces": [],
        "virtual_keyboard": None,
        "virtual_pointer": None,
        "layer_shell": None,
        "screencopy": None,
        "error": None,
        "commands": {"wayland_info": "wayland-info"},
    }

    if backend != "wayland":
        result["status"] = "not_wayland"
        return result
    if not wayland_display:
        result["status"] = "display_missing"
        return result
    if not wayland_info:
        result["status"] = "probe_tool_missing"
        return result

    try:
        proc = _run_probe([wayland_info])
    except Exception as exc:
        result["status"] = "probe_failed"
        result["error"] = str(exc)
        return result

    if proc.returncode != 0:
        result["status"] = "probe_failed"
        result["error"] = (proc.stderr or proc.stdout).strip() or "wayland-info failed"
        return result

    interfaces: list[str] = []
    text = proc.stdout or ""
    for m in _WAYLAND_INTERFACE_RE.finditer(text):
        name = m.group(1) or m.group(2)
        if name and name not in interfaces:
            interfaces.append(name)

    if not interfaces:
        # Fallback for older output formats.
        for m in _WAYLAND_GLOBAL_RE.finditer(text):
            name = m.group(1)
            if name and name not in interfaces:
                interfaces.append(name)

    result["interfaces"] = interfaces
    ifaces = set(interfaces)
    result["virtual_keyboard"] = "zwp_virtual_keyboard_v1" in ifaces
    result["virtual_pointer"] = "zwlr_virtual_pointer_manager_v1" in ifaces
    result["layer_shell"] = "zwlr_layer_shell_v1" in ifaces
    result["screencopy"] = "zwlr_screencopy_manager_v1" in ifaces
    result["status"] = "ok"
    return result


def probe_ydotool_socket(env: Mapping[str, str | None] | None = None) -> dict[str, Any]:
    """Probe whether ydotool can reach its daemon socket (ydotoold).

    ydotool is split into a client (ydotool) and daemon (ydotoold). The client
    connects to a UNIX socket controlled by ydotoold.

    Unfortunately, the default socket path varies across distros and service
    setups:
    - some run ydotoold as root using /tmp/.ydotool_socket
    - others run ydotoold as a user service using $XDG_RUNTIME_DIR/.ydotool_socket

    We probe both locations (and YDOTOOL_SOCKET when set).
    """

    import socket

    env_map = os.environ if env is None else env
    ydotool = shutil.which("ydotool")

    forced = (env_map.get("YDOTOOL_SOCKET") or "").strip()
    xdg_runtime = (env_map.get("XDG_RUNTIME_DIR") or "").strip()
    if not xdg_runtime:
        try:
            xdg_runtime = f"/run/user/{os.getuid()}"
        except Exception:
            xdg_runtime = ""

    candidates: list[str] = []
    if forced:
        candidates.append(forced)
    if xdg_runtime:
        candidates.append(str(Path(xdg_runtime) / ".ydotool_socket"))
    candidates.append("/tmp/.ydotool_socket")

    # De-dupe while preserving order.
    seen: set[str] = set()
    cand = []
    for c in candidates:
        if c and c not in seen:
            cand.append(c)
            seen.add(c)

    result: dict[str, Any] = {
        "tool": ydotool,
        "socket": cand[0] if cand else None,
        "status": "not_checked",
        "candidates": [],
    }

    if not ydotool:
        result["status"] = "tool_missing"
        return result

    any_ok = False
    chosen_socket = None

    for path in cand:
        pth = Path(path)
        item: dict[str, Any] = {
            "socket": str(pth),
            "exists": pth.exists(),
            "is_socket": None,
            "can_connect": None,
            "status": "not_checked",
            "error": None,
        }

        if not pth.exists():
            item["status"] = "socket_missing"
            item["can_connect"] = False
            result["candidates"].append(item)
            continue

        try:
            import stat

            item["is_socket"] = stat.S_ISSOCK(pth.stat().st_mode)
        except Exception:
            item["is_socket"] = None

        try:
            s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            s.settimeout(0.25)
            s.connect(str(pth))
            s.close()
            item["can_connect"] = True
            item["status"] = "ok"
            any_ok = True
            if chosen_socket is None:
                chosen_socket = str(pth)
        except PermissionError as exc:
            item["can_connect"] = False
            item["status"] = "permission_denied"
            item["error"] = str(exc)
        except Exception as exc:
            item["can_connect"] = False
            item["status"] = "connect_failed"
            item["error"] = str(exc)

        result["candidates"].append(item)

    # Overall status: prefer the first ok candidate.
    if any_ok:
        result["status"] = "ok"
        result["socket"] = chosen_socket
        return result

    # Otherwise, pick the first candidate status as summary.
    if result["candidates"]:
        result["status"] = result["candidates"][0]["status"]
        result["socket"] = result["candidates"][0]["socket"]
    else:
        result["status"] = "socket_missing"
    return result


def probe_kdotool(env: Mapping[str, str | None] | None = None) -> dict[str, Any]:
    """Probe kdotool availability (KDE Plasma / KWin helper).

    kdotool is an xdotool-like tool that controls KWin via scripting+DBus.
    VHK uses it for best-effort KDE Wayland support, such as querying global
    cursor position and active window metadata.
    """

    _ = os.environ if env is None else env
    exe = shutil.which("kdotool")
    backend = detect_backend()

    result: dict[str, Any] = {
        "backend": backend,
        "tool": exe,
        "available": bool(exe),
        "status": "ok" if exe else "missing",
        "version": None,
        "error": None,
        "commands": {
            "version": "kdotool --version",
            "cursorpos": "kdotool getmouselocation --shell",
            "active_window": "kdotool getactivewindow getwindowid getwindowname",
        },
        "notes": [
            "Useful on KDE Wayland where generic cursor position APIs are not available.",
            "Not an input injection tool (pair with dotool/ydotool for mouse/keyboard).",
        ],
    }

    if not exe:
        return result

    try:
        proc = _run_probe([exe, "--version"])
        if proc.returncode == 0:
            result["version"] = (proc.stdout or "").strip() or None
        else:
            # Some builds may not support --version; tolerate.
            result["version"] = None
    except Exception as exc:
        result["status"] = "probe_failed"
        result["error"] = str(exc)

    return result


def _parse_setxkbmap_query(stdout: str) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for line in stdout.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip().lower().replace(" ", "_")
        value = value.strip()
        if value:
            parsed[key] = value
    return parsed


def probe_xkb_layout(env: Mapping[str, str | None] | None = None) -> dict[str, Any]:
    env_map = os.environ if env is None else env
    backend = detect_backend()
    display = env_map.get("DISPLAY")
    setxkbmap = shutil.which("setxkbmap")

    result: dict[str, Any] = {
        "backend": backend,
        "display": display,
        "probe_tool": "setxkbmap" if setxkbmap else None,
        "tool": setxkbmap,
        "status": "not_checked",
        "layout": None,
        "variant": None,
        "options": None,
        "model": None,
        "error": None,
        "commands": {
            "query": "setxkbmap -query",
        },
    }

    if not display:
        result["status"] = "display_missing"
        return result
    if backend != "x11":
        result["status"] = "not_x11"
        return result
    if not setxkbmap:
        result["status"] = "probe_tool_missing"
        return result

    try:
        proc = _run_probe([setxkbmap, "-query"])
    except Exception as exc:
        result["status"] = "probe_failed"
        result["error"] = str(exc)
        return result

    if proc.returncode != 0:
        result["status"] = "probe_failed"
        result["error"] = (proc.stderr or proc.stdout).strip() or "setxkbmap failed"
        return result

    parsed = _parse_setxkbmap_query(proc.stdout)
    result["layout"] = parsed.get("layout")
    result["variant"] = parsed.get("variant")
    result["options"] = parsed.get("options")
    result["model"] = parsed.get("model")
    result["status"] = "ok"
    return result


def probe_screenshot_capture(env: Mapping[str, str | None] | None = None) -> dict[str, Any]:
    from vhk.system.screenshot import capture as capture_screenshot
    from vhk.system.screenshot import choose_backend as choose_screenshot_backend

    env_map = os.environ if env is None else env
    backend_name = detect_backend()
    screenshot_backend = choose_screenshot_backend()

    result: dict[str, Any] = {
        "backend": screenshot_backend.name if screenshot_backend else None,
        "tool": screenshot_backend.exe if screenshot_backend else None,
        "converter_tool": screenshot_backend.converter_exe if screenshot_backend else None,
        "desktop_backend": backend_name,
        "status": "not_checked",
        "bytes": None,
        "error": None,
        "capture_mode": "full_screen_tempfile",
        "grim_scale": None,
    }

    if not screenshot_backend:
        result["status"] = "backend_missing"
        return result

    if screenshot_backend and screenshot_backend.name == "grim":
        raw = (env_map.get("VHK_GRIM_SCALE") or "").strip()
        result["grim_scale"] = raw or "1"

    if backend_name == "x11" and not env_map.get("DISPLAY"):
        result["status"] = "display_missing"
        return result

    if backend_name == "wayland" and not env_map.get("WAYLAND_DISPLAY"):
        result["status"] = "display_missing"
        return result

    try:
        with tempfile.TemporaryDirectory(prefix="vhk_doctor_ss_") as tmpdir:
            out = Path(tmpdir) / "doctor_probe.png"
            capture_screenshot(out)
            result["bytes"] = out.stat().st_size
            result["status"] = "ok"
            return result
    except Exception as exc:
        result["status"] = "probe_failed"
        result["error"] = str(exc)
        return result


def _parse_tesseract_languages(text: str) -> list[str]:
    lines = text.splitlines()
    languages: list[str] = []
    capture = False

    for raw_line in lines:
        stripped = raw_line.strip()
        if not stripped:
            continue
        if stripped.lower().startswith("list of available languages"):
            capture = True
            continue
        if not capture:
            continue
        if stripped.startswith("Error") or stripped.startswith("Failed") or stripped.startswith("Please "):
            continue
        if re.fullmatch(r"[A-Za-z0-9_.+-]+", stripped):
            if stripped not in languages:
                languages.append(stripped)
    return languages


def probe_tesseract_languages(env: Mapping[str, str | None] | None = None) -> dict[str, Any]:
    env_map = os.environ if env is None else env
    tesseract = shutil.which("tesseract")
    result: dict[str, Any] = {
        "probe_tool": "tesseract" if tesseract else None,
        "tool": tesseract,
        "status": "not_checked",
        "languages": [],
        "language_count": 0,
        "has_eng": None,
        "warning": None,
        "error": None,
        "tessdata_prefix": env_map.get("TESSDATA_PREFIX"),
        "commands": {
            "list_languages": "tesseract --list-langs",
        },
    }

    if not tesseract:
        result["status"] = "binary_missing"
        return result

    try:
        proc = _run_probe([tesseract, "--list-langs"])
    except Exception as exc:
        result["status"] = "probe_failed"
        result["error"] = str(exc)
        return result

    combined = "\n".join(part for part in [proc.stdout, proc.stderr] if part)
    languages = _parse_tesseract_languages(combined)
    warning = (proc.stderr or "").strip() or None

    result["languages"] = languages
    result["language_count"] = len(languages)
    result["has_eng"] = "eng" in languages
    result["warning"] = warning

    if proc.returncode == 0:
        result["status"] = "ok" if languages else "no_languages"
        return result

    if languages:
        result["status"] = "ok_with_warnings"
        result["error"] = (proc.stderr or proc.stdout).strip() or None
        return result

    result["status"] = "probe_failed"
    result["error"] = (proc.stderr or proc.stdout).strip() or "tesseract --list-langs failed"
    return result


def _safe_div(numerator: float, denominator: float) -> float | None:
    if denominator <= 0:
        return None
    return numerator / denominator


def _monitor_dpi(width_px: int | None, height_px: int | None, width_mm: int | None, height_mm: int | None) -> tuple[float | None, float | None, float | None]:
    dpi_x = _safe_div(width_px * 25.4, width_mm) if width_px and width_mm else None
    dpi_y = _safe_div(height_px * 25.4, height_mm) if height_px and height_mm else None
    if dpi_x and dpi_y:
        return dpi_x, dpi_y, (dpi_x + dpi_y) / 2.0
    return dpi_x, dpi_y, dpi_x or dpi_y


def _parse_xrandr_screen(stdout: str) -> dict[str, int] | None:
    match = re.search(
        r"Screen\s+\d+:\s+minimum\s+\d+\s+x\s+\d+,\s+current\s+(\d+)\s+x\s+(\d+),\s+maximum\s+(\d+)\s+x\s+(\d+)",
        stdout,
    )
    if not match:
        return None
    return {
        "current_width": int(match.group(1)),
        "current_height": int(match.group(2)),
        "maximum_width": int(match.group(3)),
        "maximum_height": int(match.group(4)),
    }


def _finalize_monitor_entry(entry: dict[str, Any]) -> dict[str, Any]:
    dpi_x, dpi_y, dpi_avg = _monitor_dpi(entry.get("width_px"), entry.get("height_px"), entry.get("width_mm"), entry.get("height_mm"))
    entry["dpi_x"] = round(dpi_x, 2) if dpi_x is not None else None
    entry["dpi_y"] = round(dpi_y, 2) if dpi_y is not None else None
    entry["dpi_avg"] = round(dpi_avg, 2) if dpi_avg is not None else None
    entry["estimated_scale_vs_96dpi"] = round(dpi_avg / 96.0, 2) if dpi_avg is not None else None
    return entry


def _parse_xrandr_monitors(stdout: str) -> list[dict[str, Any]]:
    monitors: list[dict[str, Any]] = []
    for raw_line in stdout.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("Monitors:"):
            continue
        match = re.match(
            r"^\d+:\s+([+*]*)(\S+)\s+(\d+)/(\d+)x(\d+)/(\d+)\+(-?\d+)\+(-?\d+)(?:\s+(.*))?$",
            line,
        )
        if not match:
            continue
        outputs = (match.group(9) or "").split()
        entry = {
            "name": match.group(2),
            "flags": match.group(1),
            "primary": "*" in match.group(1),
            "width_px": int(match.group(3)),
            "width_mm": int(match.group(4)),
            "height_px": int(match.group(5)),
            "height_mm": int(match.group(6)),
            "x": int(match.group(7)),
            "y": int(match.group(8)),
            "outputs": outputs,
            "source": "xrandr --listmonitors",
        }
        monitors.append(_finalize_monitor_entry(entry))
    return monitors


_CONNECTED_RE = re.compile(
    r"^(?P<name>\S+)\s+connected(?:\s+primary)?(?:\s+(?P<width>\d+)x(?P<height>\d+)\+(?P<x>-?\d+)\+(?P<y>-?\d+))?.*?(?:(?P<width_mm>\d+)mm x (?P<height_mm>\d+)mm)?\s*$"
)


def _parse_xrandr_connected_outputs(stdout: str) -> list[dict[str, Any]]:
    monitors: list[dict[str, Any]] = []
    for raw_line in stdout.splitlines():
        line = raw_line.rstrip()
        if " connected" not in line:
            continue
        match = _CONNECTED_RE.match(line)
        if not match:
            continue
        entry = {
            "name": match.group("name"),
            "flags": "*" if " primary " in f" {line} " else "",
            "primary": " primary " in f" {line} ",
            "width_px": int(match.group("width")) if match.group("width") else None,
            "height_px": int(match.group("height")) if match.group("height") else None,
            "x": int(match.group("x")) if match.group("x") else None,
            "y": int(match.group("y")) if match.group("y") else None,
            "width_mm": int(match.group("width_mm")) if match.group("width_mm") else None,
            "height_mm": int(match.group("height_mm")) if match.group("height_mm") else None,
            "outputs": [match.group("name")],
            "source": "xrandr --query",
        }
        monitors.append(_finalize_monitor_entry(entry))
    return monitors


def _display_scale_summary(monitors: list[dict[str, Any]]) -> dict[str, Any]:
    dpi_values = [m["dpi_avg"] for m in monitors if m.get("dpi_avg") is not None]
    scale_values = [m["estimated_scale_vs_96dpi"] for m in monitors if m.get("estimated_scale_vs_96dpi") is not None]
    if not dpi_values and not scale_values:
        return {"mixed_dpi": False, "dpi_spread": None, "scale_spread": None}

    dpi_spread = round(max(dpi_values) - min(dpi_values), 2) if dpi_values else None
    scale_spread = round(max(scale_values) - min(scale_values), 2) if scale_values else None
    mixed = bool(scale_spread is not None and scale_spread >= 0.25) or bool(dpi_spread is not None and dpi_spread >= 24.0)
    return {"mixed_dpi": mixed, "dpi_spread": dpi_spread, "scale_spread": scale_spread}


def probe_display_geometry(env: Mapping[str, str | None] | None = None) -> dict[str, Any]:
    env_map = os.environ if env is None else env
    backend = detect_backend()
    display = env_map.get("DISPLAY")
    xrandr = shutil.which("xrandr")

    result: dict[str, Any] = {
        "backend": backend,
        "display": display,
        "probe_tool": "xrandr" if xrandr else None,
        "tool": xrandr,
        "status": "not_checked",
        "screen": None,
        "monitors": [],
        "monitor_count": 0,
        "mixed_dpi": False,
        "dpi_spread": None,
        "scale_spread": None,
        "error": None,
        "commands": {
            "query": "xrandr --query",
            "list_monitors": "xrandr --listmonitors",
        },
    }

    if not display:
        result["status"] = "display_missing"
        return result
    if backend != "x11":
        result["status"] = "not_x11"
        return result
    if not xrandr:
        result["status"] = "probe_tool_missing"
        return result

    query_proc = None
    list_proc = None
    try:
        query_proc = _run_probe([xrandr, "--query"])
    except Exception as exc:
        result["error"] = str(exc)

    try:
        list_proc = _run_probe([xrandr, "--listmonitors"])
    except Exception as exc:
        if not result["error"]:
            result["error"] = str(exc)

    monitors: list[dict[str, Any]] = []

    if query_proc and query_proc.returncode == 0:
        result["screen"] = _parse_xrandr_screen(query_proc.stdout)
        monitors = _parse_xrandr_connected_outputs(query_proc.stdout)
    elif query_proc and not result["error"]:
        result["error"] = (query_proc.stderr or query_proc.stdout).strip() or "xrandr --query failed"

    if list_proc and list_proc.returncode == 0:
        list_monitors = _parse_xrandr_monitors(list_proc.stdout)
        if list_monitors:
            monitors = list_monitors
    elif list_proc and not result["error"]:
        result["error"] = (list_proc.stderr or list_proc.stdout).strip() or "xrandr --listmonitors failed"

    result["monitors"] = monitors
    result["monitor_count"] = len(monitors)
    summary = _display_scale_summary(monitors)
    result.update(summary)

    if result["screen"] or monitors:
        result["status"] = "ok"
    else:
        result["status"] = "probe_failed"
        if not result["error"]:
            result["error"] = "xrandr did not return monitor geometry"
    return result


def probe_i3_ipc() -> dict[str, Any]:
    result: dict[str, Any] = {
        "status": "not_checked",
        "socket_path": None,
        "workspace_count": None,
        "wm": None,
        "error": None,
    }

    try:
        socket_path = discover_socket_path()
    except Exception as exc:
        result["status"] = "unavailable"
        result["error"] = str(exc)
        return result

    result["socket_path"] = socket_path
    if "sway" in socket_path:
        result["wm"] = "sway"
    elif "i3" in socket_path:
        result["wm"] = "i3"

    try:
        conn = I3Connection(socket_path=socket_path, timeout=2.0)
        workspaces = conn.get_workspaces()
    except Exception as exc:
        result["status"] = "connect_failed"
        result["error"] = str(exc)
        return result

    result["workspace_count"] = len(workspaces) if isinstance(workspaces, list) else None
    result["status"] = "ok"
    return result


def probe_wayland_virtual_screen(env: Mapping[str, str | None] | None = None) -> dict[str, Any]:
    """Probe VHK's Wayland virtual screen size logic.

    This is primarily used to support dotool-style backends that accept
    normalized coordinates.
    """

    _ = os.environ if env is None else env
    backend = detect_backend()

    result: dict[str, Any] = {
        "backend": backend,
        "status": "not_checked",
        "width": None,
        "height": None,
        "probe": None,
        "error": None,
        "notes": [
            "Wayland has no single cross-DE screen-geometry API.",
            "VHK probes Hyprland (hyprctl), sway/i3 IPC, GNOME DisplayConfig (gdbus), and KDE kscreen-doctor when available.",
        ],
    }

    if backend != "wayland":
        result["status"] = "not_wayland"
        return result

    try:
        from vhk.system.display import get_virtual_screen_size

        sz = get_virtual_screen_size(refresh=True)
    except Exception as exc:
        result["status"] = "probe_failed"
        result["error"] = str(exc)
        return result

    result["status"] = "ok"
    result["width"] = sz.width
    result["height"] = sz.height
    result["probe"] = sz.backend
    return result


def build_doctor_advice(
    *,
    desktop_backend: str,
    helpers: Mapping[str, str | None],
    a11y: Mapping[str, Any],
    recovery: Mapping[str, Any],
    screenshot: Mapping[str, Any] | None = None,
    xdg_portal: Mapping[str, Any] | None = None,
    xdg_global_shortcuts: Mapping[str, Any] | None = None,
    xdg_remote_desktop: Mapping[str, Any] | None = None,
    tesseract: Mapping[str, Any] | None = None,
    displays: Mapping[str, Any] | None = None,
    x11: Mapping[str, Any] | None = None,
    i3: Mapping[str, Any] | None = None,
    xkb: Mapping[str, Any] | None = None,
    uinput: Mapping[str, Any] | None = None,
    wayland_protocols: Mapping[str, Any] | None = None,
    ydotool_socket: Mapping[str, Any] | None = None,
) -> list[dict[str, str]]:
    advice: list[dict[str, str]] = []

    xcd = (os.environ.get("XDG_CURRENT_DESKTOP") or "").strip().lower()
    kde_like = ("kde" in xcd) or ("plasma" in xcd) or bool(os.environ.get("KDE_FULL_SESSION"))

    if desktop_backend == "wayland" and kde_like and not helpers.get("kdotool"):
        advice.append(
            {
                "severity": "info",
                "topic": "kde",
                "summary": "On KDE Wayland, installing kdotool improves Window Spy and cursor position probing (it queries KWin via scripting+DBus).",
            }
        )

    if desktop_backend == "wayland" and helpers.get("xdotool"):
        advice.append(
            {
                "severity": "info",
                "topic": "wayland",
                "summary": "xdotool is installed, but Wayland sessions should prefer wtype/ydotool-style helpers.",
            }
        )

    if not helpers.get("espanso"):
        advice.append(
            {
                "severity": "info",
                "topic": "hotstrings",
                "summary": "Espanso is not installed. If you want hotstrings/text-expansion, VHK can export project.yaml hotstrings via `vhk gen-espanso`.",
            }
        )

    if a11y.get("status") == "disabled_by_env":
        advice.append(
            {
                "severity": "warning",
                "topic": "accessibility",
                "summary": "NO_AT_BRIDGE disables the AT-SPI bridge for this process; accessibility targeting will be unavailable.",
            }
        )
    elif a11y.get("status") in {"probe_tool_missing", "probe_failed", "registry_missing"}:
        advice.append(
            {
                "severity": "warning",
                "topic": "accessibility",
                "summary": "Accessibility bus probe is incomplete or failing; vision fallbacks may be needed until AT-SPI is healthy.",
            }
        )

    if recovery.get("reason") == "x11vnc_missing" and desktop_backend == "x11":
        advice.append(
            {
                "severity": "info",
                "topic": "recovery",
                "summary": "Install x11vnc if you want an emergency 'clear stuck keys' recovery command in the Doctor.",
            }
        )

    if helpers.get("ydotool") and not helpers.get("uinput"):
        advice.append(
            {
                "severity": "info",
                "topic": "wayland-input",
                "summary": "ydotool is present but /dev/uinput tooling is missing from PATH; deeper pointer injection may still need extra setup.",
            }
        )

    if uinput:
        status = uinput.get("status")
        # Only raise this when a tool that *needs* uinput is in play.
        needs_uinput = bool(helpers.get("ydotool") or helpers.get("dotool") or helpers.get("dotoolc") or helpers.get("dotoold") or helpers.get("kanata") or helpers.get("kmonad") or helpers.get("keyd"))
        if needs_uinput and status == "missing":
            advice.append(
                {
                    "severity": "info",
                    "topic": "uinput",
                    "summary": "/dev/uinput was not found. Some distros load the uinput module lazily; ensure the uinput kernel module is loaded (e.g. via /etc/modules-load.d/uinput.conf) before relying on ydotool/kanata/kmonad-style injection.",
                }
            )
        elif needs_uinput and status == "permission_denied":
            advice.append(
                {
                    "severity": "warning",
                    "topic": "uinput",
                    "summary": "/dev/uinput exists but is not writable by this user. Install a udev rule (and/or TAG+=\"uaccess\") or add your user to the appropriate group. VHK can generate a starter rule via `vhk gen-udev-uinput`.",
                }
            )

    if desktop_backend == "wayland" and wayland_protocols:
        if helpers.get("wtype") and wayland_protocols.get("virtual_keyboard") is False:
            advice.append(
                {
                    "severity": "warning",
                    "topic": "wayland-input",
                    "summary": "wayland-info did not report zwp_virtual_keyboard_v1; wtype may fail with 'Compositor does not support the virtual keyboard protocol'. Consider ydotool or compositor-native bindings.",
                }
            )

    if ydotool_socket and helpers.get("ydotool"):
        status = ydotool_socket.get("status")
        if status in {"socket_missing", "permission_denied", "connect_failed"}:
            advice.append(
                {
                    "severity": "warning",
                    "topic": "ydotool",
                    "summary": f"ydotool is installed but its daemon socket is not reachable (status={status}). Ensure ydotoold is running and YDOTOOL_SOCKET points at the right socket.",
                }
            )
        elif needs_uinput and status == "permission_denied":
            advice.append(
                {
                    "severity": "warning",
                    "topic": "uinput",
                    "summary": "/dev/uinput exists but is not writable by this user. Install a udev rule (and/or TAG+=\"uaccess\") or add your user to the appropriate group. VHK can generate a starter rule via `vhk gen-udev-uinput`.",
                }
            )


    if x11:
        if x11.get("status") == "ok" and x11.get("xtest_available") is False:
            advice.append(
                {
                    "severity": "warning",
                    "topic": "x11-input",
                    "summary": "XTEST is missing from the X server, so xdotool-style injection will not be available.",
                }
            )
        if x11.get("status") == "ok" and x11.get("record_available") is False:
            advice.append(
                {
                    "severity": "info",
                    "topic": "x11-recorder",
                    "summary": "RECORD is missing, so advanced synchronized recorder modes should stay disabled; basic capture can still work.",
                }
            )
        elif x11.get("status") in {"probe_tool_missing", "probe_failed"} and desktop_backend == "x11":
            advice.append(
                {
                    "severity": "info",
                    "topic": "x11-input",
                    "summary": "Install xdpyinfo to probe XTEST/RECORD availability directly from the Doctor.",
                }
            )

    if i3:
        if i3.get("status") == "connect_failed":
            advice.append(
                {
                    "severity": "warning",
                    "topic": "i3-ipc",
                    "summary": "An i3/sway IPC socket was found but could not be queried; window-scoped steps may not be reliable until IPC is healthy.",
                }
            )
        elif i3.get("status") == "unavailable" and desktop_backend in {"x11", "wayland"}:
            advice.append(
                {
                    "severity": "info",
                    "topic": "i3-ipc",
                    "summary": "No i3/sway IPC socket was discovered; i3-native selectors and waits will be unavailable outside i3/sway sessions.",
                }
            )

    if xkb and xkb.get("status") in {"probe_tool_missing", "probe_failed"} and desktop_backend == "x11":
        advice.append(
            {
                "severity": "info",
                "topic": "keyboard-layout",
                "summary": "Install setxkbmap if you want the Doctor to report the active XKB layout and options.",
            }
        )

    if screenshot:
        if screenshot.get("status") == "backend_missing":
            advice.append(
                {
                    "severity": "info",
                    "topic": "screenshots",
                    "summary": "No screenshot helper was found; install grim (wlroots) or spectacle/gnome-screenshot on Wayland, or maim/scrot/import/xwd+convert on X11.",
                }
            )
        elif screenshot.get("status") == "probe_failed":
            if desktop_backend == "wayland" and screenshot.get("backend") == "grim":
                advice.append(
                    {
                        "severity": "warning",
                        "topic": "screenshots",
                        "summary": "grim was found but a real capture failed; compositor screencopy support may be missing or blocked, so visual steps may need a portal or desktop-native fallback (e.g. spectacle/gnome-screenshot).",
                    }
                )
            else:
                advice.append(
                    {
                        "severity": "warning",
                        "topic": "screenshots",
                        "summary": "A screenshot helper is installed but a temporary capture failed; image search, OCR, and screenshot-on-error will be unreliable until capture works.",
                    }
                )

    if desktop_backend == "wayland" and xdg_portal:
        if xdg_portal.get("status") in {"service_missing", "interface_missing"}:
            advice.append(
                {
                    "severity": "info",
                    "topic": "portals",
                    "summary": "XDG Desktop Portal Screenshot interface was not detected. Portal-based capture (for stricter Wayland desktops) may require installing/configuring a portal backend (gtk/kde/wlr).",
                }
            )

    # GlobalShortcuts portal (Wayland hotkeys)
    if desktop_backend == "wayland" and xdg_global_shortcuts:
        st = xdg_global_shortcuts.get("status")
        if st in {"service_missing", "interface_missing"}:
            advice.append(
                {
                    "severity": "info",
                    "topic": "portals",
                    "summary": "XDG Desktop Portal GlobalShortcuts interface was not detected. Wayland global hotkeys via the portal may only work on desktops that implement it (Plasma currently has the most complete support). On wlroots-based setups, prefer compositor-native triggers (Hyprland custom events) or external hotkey daemons feeding the VHK bus.",
                }
            )
        elif st == "ok" and xdg_global_shortcuts.get("global_shortcuts_version") is None:
            advice.append(
                {
                    "severity": "info",
                    "topic": "portals",
                    "summary": "GlobalShortcuts portal probe returned an unparsed version; hotkey portal support may be present but mismatched with the probing tool.",
                }
            )

    # RemoteDesktop portal (permissioned input emulation)
    if desktop_backend == "wayland" and xdg_remote_desktop:
        st = xdg_remote_desktop.get("status")
        if st in {"service_missing", "interface_missing"}:
            advice.append(
                {
                    "severity": "info",
                    "topic": "portals",
                    "summary": "XDG Desktop Portal RemoteDesktop interface was not detected. If you want permissioned input emulation via portals/libei, you may need a portal backend that implements RemoteDesktop; otherwise use uinput-based helpers (ydotool/dotool) where acceptable.",
                }
            )
    if tesseract:
        if tesseract.get("status") in {"no_languages", "probe_failed"} and not tesseract.get("languages"):
            advice.append(
                {
                    "severity": "warning",
                    "topic": "ocr",
                    "summary": "Tesseract is present but usable language data was not discovered; OCR steps will fail until tessdata packages are installed/configured.",
                }
            )
        elif tesseract.get("languages") and tesseract.get("has_eng") is False:
            advice.append(
                {
                    "severity": "info",
                    "topic": "ocr",
                    "summary": "English traineddata is not installed, so the default OCR language (eng) will fail unless workflows set lang= explicitly.",
                }
            )

    if displays:
        if displays.get("status") in {"probe_tool_missing", "probe_failed"} and desktop_backend == "x11":
            advice.append(
                {
                    "severity": "info",
                    "topic": "display-geometry",
                    "summary": "Install xrandr if you want the Doctor to report monitor geometry and estimated DPI/scale on X11.",
                }
            )
        elif displays.get("mixed_dpi"):
            advice.append(
                {
                    "severity": "info",
                    "topic": "display-geometry",
                    "summary": "The connected monitors appear to have mixed DPI/scale, which can make image matching and coordinate-based clicks drift across screens.",
                }
            )

    return advice
