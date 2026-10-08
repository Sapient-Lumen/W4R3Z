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
from typing import Any, Iterable, Iterator


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

    # Auto-json decode first arg when it looks like JSON.
    if args and isinstance(args[0], str):
        s = args[0].strip()
        if (s.startswith("{") and s.endswith("}")) or (s.startswith("[") and s.endswith("]")):
            try:
                args[0] = json.loads(s)
            except Exception:
                # dbus-monitor may escape quotes (e.g. {\"k\":1}).
                try:
                    unescaped = s.replace('\\"', '"').replace('\\\\', '\\')
                    args[0] = json.loads(unescaped)
                except Exception:
                    pass

    return DBusSignal(
        sender=m.group("sender"),
        path=m.group("path"),
        interface=m.group("iface"),
        member=m.group("member"),
        args=args,
        raw=text,
    )


def _spawn_monitor(*, rules: list[str]) -> subprocess.Popen[str]:
    """Start a DBus monitor process for the session bus."""

    dbus_monitor = shutil.which("dbus-monitor")
    if dbus_monitor:
        # dbus-monitor supports explicit match rules.
        cmd = [dbus_monitor, "--session", *rules]
        return subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)

    gdbus = shutil.which("gdbus")
    if not gdbus:
        raise RuntimeError("Need dbus-monitor or gdbus")

    # gdbus monitor can't express the same match syntax, so we monitor the whole bus
    # and filter in user code.
    cmd = [gdbus, "monitor", "--session"]
    return subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)


def iter_dbus_signals(*, match_rule: str, timeout_s: float | None = None) -> Iterator[DBusSignal]:
    """Yield DBus signals matching the given dbus-monitor match rule.

    Parameters
    ----------
    match_rule:
        A dbus-monitor match rule string, e.g.
        "interface='org.vhk.Trigger',member='Fire'".

    Notes
    -----
    When dbus-monitor is not available, we fall back to gdbus monitor and do a
    best-effort filter. In that mode, some metadata may be missing.
    """

    rules = [match_rule]
    proc = _spawn_monitor(rules=rules)
    if not proc.stdout:
        raise RuntimeError("monitor process missing stdout")

    buf: list[str] = []

    try:
        for line in proc.stdout:
            if not line:
                break
            line = line.rstrip("\n")

            # dbus-monitor starts new blocks with "signal time=".
            if line.startswith("signal time="):
                if buf:
                    sig = parse_dbus_monitor_block("\n".join(buf) + "\n")
                    if sig is not None:
                        yield sig
                buf = [line]
            else:
                if buf:
                    buf.append(line)

        # flush last block
        if buf:
            sig = parse_dbus_monitor_block("\n".join(buf) + "\n")
            if sig is not None:
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
