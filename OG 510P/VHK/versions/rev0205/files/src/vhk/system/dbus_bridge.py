from __future__ import annotations

"""DBus signal bridge (best-effort, zero extra deps).

Why this exists
---------------
Some desktop environments deliberately limit what window-manager scripts may do.
KWin scripting, for example, historically avoids allowing arbitrary command
execution directly, and community guidance often suggests emitting a DBus signal
and letting an external helper react.

VHK uses the same principle: let the WM emit a tiny event, and keep heavy
automation (vision, retries, macros) in VHK.

Implementation notes
--------------------
We intentionally avoid Python DBus bindings to keep dependencies light.
Instead we parse the output of external tools:
- dbus-monitor (preferred when available)
- gdbus monitor (fallback)

Parsing is heuristic but designed to be stable enough for simple payloads
(strings / ints / booleans / doubles). For complex structs, pass JSON as the
first string arg and let the bridge decode it.
"""

import json
import re
import shutil
import subprocess
from dataclasses import dataclass
from typing import Any, Iterator

from vhk.system.gvariant import gdbus_call_output_to_python


@dataclass(frozen=True)
class DBusSignal:
    sender: str | None
    path: str | None
    interface: str | None
    member: str | None
    args: list[Any]
    raw: str


_SIGNAL_HEADER_RE = re.compile(
    r"^signal\s+time=.*?sender=(?P<sender>\S+)\s+->\s+destination=.*?\s+path=(?P<path>\S+);\s+interface=(?P<iface>[^;]+);\s+member=(?P<member>[^\s]+)"
)
_GDBUS_LINE_RE = re.compile(
    r"^(?P<path>/\S*?)\s*:\s*(?P<iface>[A-Za-z0-9_.]+)\.(?P<member>[A-Za-z0-9_]+)\s*\((?P<args>.*)\)$"
)


def _parse_arg_line(line: str) -> Any | None:
    line = line.strip()
    if not line:
        return None

    # dbus-monitor prints typed lines like:
    #   string "hello"
    #   int32 123
    #   uint32 0
    #   boolean true
    #   double 0.5
    m = re.match(r"^(string)\s+\"(.*)\"$", line)
    if m:
        return m.group(2)

    m = re.match(r"^(object path)\s+\"(.*)\"$", line)
    if m:
        return m.group(2)

    m = re.match(r"^(int32|uint32|int64|uint64)\s+(-?\d+)$", line)
    if m:
        try:
            return int(m.group(2))
        except Exception:
            return m.group(2)

    m = re.match(r"^(double)\s+([0-9]*\.?[0-9]+)$", line)
    if m:
        try:
            return float(m.group(2))
        except Exception:
            return m.group(2)

    m = re.match(r"^(boolean)\s+(true|false)$", line)
    if m:
        return m.group(2) == "true"

    return None


def _decode_first_json_arg(args: list[Any]) -> None:
    if args and isinstance(args[0], str):
        s = args[0].strip()
        if (s.startswith("{") and s.endswith("}")) or (s.startswith("[") and s.endswith("]")):
            try:
                args[0] = json.loads(s)
            except Exception:
                try:
                    unescaped = s.replace('\\"', '"').replace('\\\\', '\\')
                    args[0] = json.loads(unescaped)
                except Exception:
                    pass


def parse_dbus_monitor_block(text: str) -> DBusSignal | None:
    """Parse a single dbus-monitor block into a DBusSignal."""

    lines = [ln.rstrip("\n") for ln in text.splitlines() if ln.strip()]
    if not lines:
        return None

    m = _SIGNAL_HEADER_RE.match(lines[0])
    if not m:
        return None

    args: list[Any] = []
    for ln in lines[1:]:
        v = _parse_arg_line(ln)
        if v is not None:
            args.append(v)

    _decode_first_json_arg(args)

    return DBusSignal(
        sender=m.group("sender"),
        path=m.group("path"),
        interface=m.group("iface"),
        member=m.group("member"),
        args=args,
        raw=text,
    )


def parse_gdbus_monitor_line(text: str) -> DBusSignal | None:
    """Parse a one-line `gdbus monitor` signal record into a DBusSignal."""

    line = (text or "").strip()
    if not line or line.startswith("Monitoring ") or line.startswith("The name "):
        return None

    m = _GDBUS_LINE_RE.match(line)
    if not m:
        return None

    args_text = (m.group("args") or "").strip()
    args: list[Any]
    if not args_text:
        args = []
    else:
        src = args_text.replace("objectpath ", "").replace("object path ", "").replace("signature ", "")
        src = re.sub(r"@[A-Za-z0-9{}()_]+\s+", "", src)
        try:
            parsed = gdbus_call_output_to_python(f"({src})")
            if isinstance(parsed, tuple):
                args = list(parsed)
            else:
                args = [parsed]
        except Exception:
            args = [args_text]

    _decode_first_json_arg(args)

    return DBusSignal(
        sender=None,
        path=m.group("path"),
        interface=m.group("iface"),
        member=m.group("member"),
        args=args,
        raw=line + "\n",
    )


def _extract_match_field(match_rule: str, field: str) -> str | None:
    m = re.search(rf"(?:^|,)\s*{re.escape(field)}='([^']+)'", match_rule)
    if m:
        return m.group(1)
    return None


def build_match_rule(
    *,
    sender: str | None = None,
    path: str | None = None,
    interface: str | None = None,
    member: str | None = None,
    raw_rule: str | None = None,
) -> str:
    parts: list[str] = []
    if raw_rule:
        raw = raw_rule.strip().strip(",")
        if raw:
            parts.append(raw)
    if not any("type='signal'" in p or 'type="signal"' in p for p in parts):
        parts.insert(0, "type='signal'")
    for key, value in (("sender", sender), ("path", path), ("interface", interface), ("member", member)):
        if value is None:
            continue
        if any(f"{key}='" in p or f'{key}="' in p for p in parts):
            continue
        parts.append(f"{key}='{value}'")
    return ",".join(parts)


def signal_text(sig: DBusSignal) -> str:
    return json.dumps(
        {
            "sender": sig.sender,
            "path": sig.path,
            "interface": sig.interface,
            "member": sig.member,
            "args": sig.args,
        },
        ensure_ascii=False,
        sort_keys=True,
        default=str,
    )


def _signal_matches_rule(sig: DBusSignal, match_rule: str) -> bool:
    if not match_rule:
        return True
    interface = _extract_match_field(match_rule, "interface")
    member = _extract_match_field(match_rule, "member")
    path = _extract_match_field(match_rule, "path")
    sender = _extract_match_field(match_rule, "sender")
    if interface is not None and sig.interface != interface:
        return False
    if member is not None and sig.member != member:
        return False
    if path is not None and sig.path != path:
        return False
    if sender is not None and sig.sender not in {None, sender}:
        return False
    return True


def _spawn_monitor(*, rules: list[str], bus: str) -> tuple[subprocess.Popen[str], str]:
    """Start a D-Bus monitor process.

    Returns ``(proc, backend)`` where backend is ``dbus-monitor`` or ``gdbus``.
    """

    dbus_monitor = shutil.which("dbus-monitor")
    if dbus_monitor:
        cmd = [dbus_monitor, f"--{bus}", *rules]
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)
        return proc, "dbus-monitor"

    gdbus = shutil.which("gdbus")
    if not gdbus:
        raise RuntimeError("Need dbus-monitor or gdbus")

    match_rule = rules[0] if rules else ""
    dest = _extract_match_field(match_rule, "sender")
    if not dest:
        raise RuntimeError("gdbus fallback requires sender='org.example.Service' (or a raw match rule containing sender=...) to scope monitoring")
    cmd = [gdbus, "monitor", f"--{bus}", "--dest", dest]
    path = _extract_match_field(match_rule, "path")
    if path:
        cmd += ["--object-path", path]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)
    return proc, "gdbus"


def iter_dbus_signals(*, match_rule: str, bus: str = "session", timeout_s: float | None = None) -> Iterator[DBusSignal]:
    """Yield DBus signals matching the given rule.

    Parameters
    ----------
    match_rule:
        A dbus-monitor match rule string, e.g.
        ``interface='org.vhk.Trigger',member='Fire'``.

    Notes
    -----
    ``dbus-monitor`` is preferred because it supports native match rules and
    richer typed output. When only ``gdbus monitor`` is available, VHK requires
    a sender/bus-name filter and then applies the remaining rule fields in user
    code.
    """

    proc, backend = _spawn_monitor(rules=[match_rule], bus=bus)
    if not proc.stdout:
        raise RuntimeError("monitor process missing stdout")

    buf: list[str] = []

    try:
        if backend == "dbus-monitor":
            for line in proc.stdout:
                if not line:
                    break
                line = line.rstrip("\n")

                if line.startswith("signal time="):
                    if buf:
                        sig = parse_dbus_monitor_block("\n".join(buf) + "\n")
                        if sig is not None:
                            yield sig
                    buf = [line]
                else:
                    if buf:
                        buf.append(line)

            if buf:
                sig = parse_dbus_monitor_block("\n".join(buf) + "\n")
                if sig is not None:
                    yield sig
            return

        for line in proc.stdout:
            if not line:
                break
            sig = parse_gdbus_monitor_line(line)
            if sig is None:
                continue
            if _signal_matches_rule(sig, match_rule):
                yield sig

    finally:
        try:
            proc.terminate()
        except Exception:
            pass
        try:
            proc.wait(timeout=1)
        except Exception:
            pass
