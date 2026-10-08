from __future__ import annotations

import os
import random
import re
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path

from vhk.system.session import detect_backend


_INT_RE = re.compile(r"(-?\d+)")


@dataclass
class IdleSample:
    ms: int
    backend: str
    source: str


def _which(cmd: str) -> str | None:
    for p in os.environ.get("PATH", "").split(os.pathsep):
        fp = Path(p) / cmd
        try:
            if fp.exists() and os.access(fp, os.X_OK):
                return str(fp)
        except OSError:
            continue
    return None


def _first_int(text: str) -> int:
    vals = _INT_RE.findall(text or "")
    if not vals:
        raise RuntimeError(f"Unable to parse idle value from output: {text!r}")
    # gdbus/dbus-send outputs may contain type markers like `uint64 1234`; use
    # the final integer token so we pick the value instead of the type width.
    return int(vals[-1])


def _run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, capture_output=True, text=True)


def _probe_xprintidle() -> IdleSample | None:
    exe = _which("xprintidle")
    if not exe:
        return None
    proc = _run([exe])
    if proc.returncode != 0:
        raise RuntimeError((proc.stderr or proc.stdout).strip() or "xprintidle failed")
    return IdleSample(ms=_first_int(proc.stdout), backend="x11", source="xprintidle")


def _probe_mutter_idle_monitor() -> IdleSample | None:
    gdbus = _which("gdbus")
    if gdbus:
        proc = _run(
            [
                gdbus,
                "call",
                "--session",
                "--dest",
                "org.gnome.Mutter.IdleMonitor",
                "--object-path",
                "/org/gnome/Mutter/IdleMonitor/Core",
                "--method",
                "org.gnome.Mutter.IdleMonitor.GetIdletime",
            ]
        )
        if proc.returncode == 0:
            return IdleSample(ms=_first_int(proc.stdout), backend="wayland", source="mutter-idle-monitor")
    dbus_send = _which("dbus-send")
    if dbus_send:
        proc = _run(
            [
                dbus_send,
                "--session",
                "--print-reply",
                "--dest=org.gnome.Mutter.IdleMonitor",
                "/org/gnome/Mutter/IdleMonitor/Core",
                "org.gnome.Mutter.IdleMonitor.GetIdletime",
            ]
        )
        if proc.returncode == 0:
            return IdleSample(ms=_first_int(proc.stdout), backend="wayland", source="mutter-idle-monitor")
    return None


def get_idle_ms() -> IdleSample:
    """Best-effort idle-time probe.

    Current VHK support is intentionally conservative:
    - X11: prefer ``xprintidle``.
    - Wayland: prefer GNOME's ``org.gnome.Mutter.IdleMonitor`` when available.

    Other desktops/compositors should currently bridge idle/active state into the
    VHK bus using a dedicated helper such as swayidle/xidlehook instead of
    pretending that generic idle probing is universally available.
    """

    backend = detect_backend()
    if backend == "x11":
        res = _probe_xprintidle()
        if res is not None:
            return res
        raise RuntimeError("Unable to probe idle time on X11 (install xprintidle).")

    # Wayland: GNOME exposes a useful compositor-specific DBus API. We keep the
    # rest of the story explicit rather than fabricating a generic claim.
    res = _probe_mutter_idle_monitor()
    if res is not None:
        return res
    raise RuntimeError(
        "Unable to probe idle time on this Wayland session. Use GNOME Mutter IdleMonitor when available, "
        "or bridge compositor-specific idle events into VHK via the local bus."
    )


def wait_for_idle(
    minimum_ms: int,
    *,
    timeout_ms: int = 10_000,
    poll_ms: int = 200,
    max_poll_ms: int = 1_000,
    jitter_ms: int = 30,
    max_attempts: int | None = None,
    on_attempt=None,
) -> IdleSample:
    if minimum_ms < 0:
        raise ValueError("minimum_ms must be >= 0")

    deadline = time.time() + (timeout_ms / 1000.0)
    attempt = 0
    poll = max(0, int(poll_ms))
    last: IdleSample | None = None

    while True:
        attempt += 1
        cur = get_idle_ms()
        last = cur
        ok = int(cur.ms) >= int(minimum_ms)
        if on_attempt is not None:
            on_attempt(attempt, cur, ok)
        if ok:
            return cur
        if max_attempts is not None and attempt >= max_attempts:
            break
        if time.time() > deadline:
            break

        if poll > 0:
            remaining_to_threshold = max(0, int(minimum_ms) - int(cur.ms))
            sleep_ms = poll if remaining_to_threshold <= 0 else min(poll, remaining_to_threshold)
            jitter = random.randint(-jitter_ms, jitter_ms) if jitter_ms else 0
            sleep_ms = max(0, sleep_ms + jitter)
            time.sleep(sleep_ms / 1000.0)
        poll = min(max_poll_ms, int(poll * 1.4) + 1) if poll else 0

    got = None if last is None else last.ms
    raise TimeoutError(f"WaitForIdle timed out after {timeout_ms}ms (minimum_ms={minimum_ms}, attempts={attempt}, last_idle_ms={got})")


def wait_for_user_activity(
    maximum_ms: int,
    *,
    armed_after_ms: int | None = None,
    timeout_ms: int = 10_000,
    poll_ms: int = 200,
    max_poll_ms: int = 1_000,
    jitter_ms: int = 30,
    max_attempts: int | None = None,
    on_attempt=None,
) -> IdleSample:
    """Wait until the user appears active again.

    This is the complementary primitive to :func:`wait_for_idle`.

    - ``maximum_ms`` defines the threshold for considering the session active
      again (for example, idle <= 1500ms).
    - ``armed_after_ms`` is optional. When set, the wait will *first* observe
      the session becoming idle enough to arm the wait, then return only once
      the idle time drops back to ``maximum_ms`` or lower. This mirrors the
      timeout/resume pairing used by tools such as swayidle, hypridle, and
      xidlehook.
    """

    if maximum_ms < 0:
        raise ValueError("maximum_ms must be >= 0")
    if armed_after_ms is not None and armed_after_ms < 0:
        raise ValueError("armed_after_ms must be >= 0")

    deadline = time.time() + (timeout_ms / 1000.0)
    attempt = 0
    initial_poll = max(0, int(poll_ms))
    poll = initial_poll
    last: IdleSample | None = None
    armed = armed_after_ms is None

    while True:
        attempt += 1
        cur = get_idle_ms()
        last = cur

        if not armed and armed_after_ms is not None and int(cur.ms) >= int(armed_after_ms):
            armed = True
            # Once we're armed we care about responsiveness to the user's next
            # action more than about backing off toward the arm threshold.
            poll = initial_poll

        ok = armed and int(cur.ms) <= int(maximum_ms)
        if on_attempt is not None:
            on_attempt(attempt, cur, armed, ok)
        if ok:
            return cur
        if max_attempts is not None and attempt >= max_attempts:
            break
        if time.time() > deadline:
            break

        if poll > 0:
            sleep_ms = poll
            if not armed and armed_after_ms is not None:
                remaining_to_arm = max(0, int(armed_after_ms) - int(cur.ms))
                if remaining_to_arm > 0:
                    sleep_ms = min(poll, remaining_to_arm)
            jitter = random.randint(-jitter_ms, jitter_ms) if jitter_ms else 0
            sleep_ms = max(0, sleep_ms + jitter)
            time.sleep(sleep_ms / 1000.0)
        poll = min(max_poll_ms, int(poll * 1.4) + 1) if poll else 0

    got = None if last is None else last.ms
    raise TimeoutError(
        f"WaitForUserActivity timed out after {timeout_ms}ms "
        f"(maximum_ms={maximum_ms}, armed_after_ms={armed_after_ms}, attempts={attempt}, armed={armed}, last_idle_ms={got})"
    )
