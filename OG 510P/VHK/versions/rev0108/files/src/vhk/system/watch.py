from __future__ import annotations
import re
import email.utils

import os
import random
import subprocess
import time
import select
from dataclasses import dataclass
import fnmatch
from pathlib import Path

from vhk.system.session import detect_backend


def _which(cmd: str) -> str | None:
    for p in os.environ.get("PATH", "").split(os.pathsep):
        fp = Path(p) / cmd
        try:
            if fp.exists() and os.access(fp, os.X_OK):
                return str(fp)
        except OSError:
            continue
    return None

# Cache whether `wl-paste --watch` works in the current environment. Some
# compositors do not support the required protocol, and older wl-clipboard
# builds may not have the flag.
_WL_PASTE_WATCH_OK: bool | None = None


def _wait_wl_paste_watch_event(wl_paste: str | None, *, selection: str, timeout_left: float) -> bool:
    """Best-effort clipboard event helper for Wayland via wl-paste --watch.

    `wl-paste --watch` runs a command each time the selection changes, piping
    the selection to stdin. We run a tiny command that drains stdin and prints
    a sentinel line, then watch stdout for that sentinel.

    Notes:
    - This requires a compositor that supports the wlroots data-control protocol.
    - If --watch is unsupported or fails immediately, we cache that and fall back
      to polling for the remainder of the process.
    """

    global _WL_PASTE_WATCH_OK

    if not wl_paste or timeout_left <= 0:
        return False
    if _WL_PASTE_WATCH_OK is False:
        return False

    cmd = [wl_paste]
    if selection == "primary":
        cmd.append("--primary")
    cmd += [
        "--watch",
        "sh",
        "-c",
        "cat >/dev/null; printf '__VHK_CLIP_EVENT__\n'",
    ]

    proc: subprocess.Popen[str] | None = None
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if proc.stdout is None:
            return False

        # If the process exits immediately, treat it as unsupported and cache it.
        poll = getattr(proc, "poll", None)
        rc = poll() if callable(poll) else None
        if rc is not None and rc != 0:
            try:
                _out, err = proc.communicate(timeout=0.05)
            except Exception:
                err = ""
            msg = (err or "").lower()
            if "watch" in msg or "unknown option" in msg or "unrecognized" in msg or "data-control" in msg:
                _WL_PASTE_WATCH_OK = False
            return False

        r, _, _ = select.select([proc.stdout], [], [], timeout_left)
        if not r:
            return False
        line = proc.stdout.readline()
        if line:
            _WL_PASTE_WATCH_OK = True
            return True
        return False
    except Exception:
        return False
    finally:
        if proc is not None:
            try:
                proc.terminate()
                proc.wait(timeout=0.2)
            except Exception:
                try:
                    proc.kill()
                except Exception:
                    pass
            try:
                proc.communicate(timeout=0.1)
            except Exception:
                pass



@dataclass
class FileState:
    exists: bool
    mtime_ns: int | None
    size: int | None


def file_state(path: str | Path) -> FileState:
    p = Path(path).expanduser()
    if not p.exists():
        return FileState(False, None, None)
    st = p.stat()
    return FileState(True, int(getattr(st, "st_mtime_ns", int(st.st_mtime * 1e9))), int(st.st_size))


def wait_for_file(path: str | Path, *, condition: str = "exists", timeout_ms: int = 10_000, poll_ms: int = 200, max_poll_ms: int = 1000, jitter_ms: int = 30, max_attempts: int | None = None, on_attempt=None) -> FileState:
    p = Path(path).expanduser()
    deadline = time.time() + (timeout_ms / 1000.0)
    attempt = 0
    poll = max(0, int(poll_ms))
    baseline = file_state(p)
    ino = _which("inotifywait")

    while True:
        attempt += 1
        cur = file_state(p)
        ok = False
        if condition == "exists":
            ok = cur.exists
        elif condition == "missing":
            ok = not cur.exists
        elif condition == "changed":
            ok = cur != baseline
        else:
            raise ValueError(f"Unsupported file wait condition: {condition}")

        if on_attempt is not None:
            on_attempt(attempt, cur, ok, helper=("inotifywait" if ino else None))
        if ok:
            return cur
        if max_attempts is not None and attempt >= max_attempts:
            break

        # Final chance: ensure we re-check after any helper wait, even if we just crossed the deadline.
        if time.time() > deadline:
            break


        # inotifywait has integer-second timeout resolution and process spawn
        # overhead. For very small timeouts, polling is often more reliable.
        timeout_left = max(0.0, deadline - time.time())
        use_inotify = bool(ino) and condition in {"exists", "missing", "changed"} and timeout_left >= 1.2

        if use_inotify:
            timeout_left = max(0.05, timeout_left)
            watch_target = p if p.exists() else p.parent
            cmd = [ino, "--quiet", "--timeout", str(max(1, int(timeout_left + 0.999))), "-e", "modify", "-e", "close_write", "-e", "move", "-e", "create", "-e", "delete", "-e", "attrib", str(watch_target)]
            try:
                subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_left + 0.2)
            except subprocess.TimeoutExpired:
                pass
        else:
            if poll > 0:
                jitter = random.randint(-jitter_ms, jitter_ms) if jitter_ms else 0
                sleep_ms = max(0, poll + jitter)
                time.sleep(sleep_ms / 1000.0)
            poll = min(max_poll_ms, int(poll * 1.4) + 1) if poll else 0

    raise TimeoutError(f"WaitForFile timed out after {timeout_ms}ms ({condition})")


def wait_for_clipboard_change(
    read_func,
    *,
    selection: str = "clipboard",
    initial_text: str | None = None,
    timeout_ms: int = 10_000,
    poll_ms: int = 200,
    max_poll_ms: int = 1000,
    jitter_ms: int = 30,
    max_attempts: int | None = None,
    on_attempt=None,
) -> str:
    baseline = initial_text if initial_text is not None else read_func(selection=selection)
    deadline = time.time() + (timeout_ms / 1000.0)
    attempt = 0
    poll = max(0, int(poll_ms))
    backend = detect_backend()
    clipnotify = _which("clipnotify") if backend == "x11" else None
    wl_paste = _which("wl-paste") if backend == "wayland" else None

    while True:
        attempt += 1
        cur = read_func(selection=selection)
        changed = cur != baseline
        if on_attempt is not None:
            on_attempt(attempt, cur, changed, helper=("clipnotify" if clipnotify else "wl-paste" if wl_paste else None))
        if changed:
            return cur
        if max_attempts is not None and attempt >= max_attempts:
            break

        # Final chance: ensure we re-check after any helper wait, even if we just crossed the deadline.
        if time.time() > deadline:
            break

        # If we have a helper-backed waiter, do a quick "race" re-check before
        # blocking on it so we don't miss events that happened between the last
        # read and spawning the helper.
        if clipnotify or wl_paste:
            try:
                cur2 = read_func(selection=selection)
                if cur2 != baseline:
                    return cur2
            except Exception:
                pass

        if clipnotify:
            cmd = [clipnotify]
            if selection == "primary":
                cmd += ["-s", "PRIMARY"]
            timeout_left = max(0.05, deadline - time.time())
            try:
                subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_left)
            except subprocess.TimeoutExpired:
                pass
        elif wl_paste:
            timeout_left = max(0.05, deadline - time.time())
            _wait_wl_paste_watch_event(wl_paste, selection=selection, timeout_left=timeout_left)
        else:
            if poll > 0:
                jitter = random.randint(-jitter_ms, jitter_ms) if jitter_ms else 0
                sleep_ms = max(0, poll + jitter)
                time.sleep(sleep_ms / 1000.0)
            poll = min(max_poll_ms, int(poll * 1.4) + 1) if poll else 0

    raise TimeoutError(f"WaitForClipboardChange timed out after {timeout_ms}ms")


def wait_for_clipboard_event(
    read_func,
    *,
    selection: str = "clipboard",
    initial_text: str | None = None,
    timeout_ms: int = 10_000,
    poll_ms: int = 200,
    max_poll_ms: int = 1000,
    jitter_ms: int = 30,
    max_attempts: int | None = None,
    on_attempt=None,
) -> tuple[str, bool]:
    """Wait for a clipboard *event* and return (text, changed).

    This is subtly different from wait_for_clipboard_change:

    - If a helper that reports clipboard-owner changes is available (clipnotify
      on X11, wl-paste --watch on Wayland), this returns even if the clipboard
      *contents* are identical to the baseline.
    - When no helper exists, VHK falls back to polling; in that mode it can only
      detect content changes.
    """

    baseline = initial_text if initial_text is not None else read_func(selection=selection)
    deadline = time.time() + (timeout_ms / 1000.0)
    attempt = 0
    poll = max(0, int(poll_ms))

    backend = detect_backend()
    clipnotify = _which("clipnotify") if backend == "x11" else None
    wl_paste = _which("wl-paste") if backend == "wayland" else None

    def _attempt_read(helper: str | None = None) -> tuple[str, bool]:
        nonlocal attempt
        attempt += 1
        cur = read_func(selection=selection)
        changed = cur != baseline
        if on_attempt is not None:
            on_attempt(attempt, cur, changed, helper=helper)
        return cur, changed

    # First attempt: if it's already changed from the baseline, return.
    cur0, changed0 = _attempt_read(helper=("clipnotify" if clipnotify else "wl-paste" if wl_paste else None))
    if changed0:
        return cur0, True
    if max_attempts is not None and attempt >= max_attempts:
        raise TimeoutError(f"WaitForClipboardEvent reached max_attempts={max_attempts} without an event")

    # Helper-backed event mode.
    if clipnotify or wl_paste:
        while True:
            if time.time() > deadline:
                break
            timeout_left = max(0.05, deadline - time.time())
            got = False
            helper = None
            if clipnotify:
                helper = "clipnotify"
                cmd = [clipnotify]
                if selection == "primary":
                    cmd += ["-s", "PRIMARY"]
                try:
                    subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_left)
                    got = True
                except subprocess.TimeoutExpired:
                    got = False
            elif wl_paste:
                helper = "wl-paste"
                got = _wait_wl_paste_watch_event(wl_paste, selection=selection, timeout_left=timeout_left)

            if got:
                cur, changed = _attempt_read(helper=helper)
                return cur, changed
            if max_attempts is not None and attempt >= max_attempts:
                break

        raise TimeoutError(f"WaitForClipboardEvent timed out after {timeout_ms}ms")

    # Polling fallback (no reliable event signal).
    while True:
        if time.time() > deadline:
            break
        cur, changed = _attempt_read(helper=None)
        if changed:
            return cur, True
        if max_attempts is not None and attempt >= max_attempts:
            break
        if poll > 0:
            jitter = random.randint(-jitter_ms, jitter_ms) if jitter_ms else 0
            sleep_ms = max(0, poll + jitter)
            time.sleep(sleep_ms / 1000.0)
        poll = min(max_poll_ms, int(poll * 1.4) + 1) if poll else 0

    raise TimeoutError(f"WaitForClipboardEvent timed out after {timeout_ms}ms")
def wait_for_new_file(
    directory: str | Path,
    *,
    pattern: str = "*",
    recursive: bool = False,
    exclude: list[str] | None = None,
    min_size: int = 0,
    stable_ms: int = 0,
    timeout_ms: int = 10_000,
    poll_ms: int = 200,
    max_poll_ms: int = 1000,
    jitter_ms: int = 30,
    max_attempts: int | None = None,
    since_ns: int | None = None,
    on_attempt=None,
) -> Path:
    root = Path(directory).expanduser()
    if not root.exists():
        raise FileNotFoundError(f"Directory does not exist: {root}")

    globber = root.rglob if bool(recursive) else root.glob

    def _iter_candidates():
        for p in globber(pattern):
            if exclude and any(fnmatch.fnmatch(p.name, ex) for ex in exclude):
                continue
            # Ignore directories: this is a "new file" wait.
            try:
                if p.is_dir():
                    continue
            except Exception:
                continue
            yield p

    # Track baseline mtime_ns so we can reliably detect modifications of
    # existing paths (useful for overwrite-style producers) without treating
    # every "touched" file as a new one.
    baseline: dict[Path, int] = {}
    for p in _iter_candidates():
        try:
            st = p.stat()
            mtime_ns = int(getattr(st, "st_mtime_ns", int(st.st_mtime * 1e9)))
        except Exception:
            mtime_ns = 0
        baseline[p.resolve()] = mtime_ns

    deadline = time.time() + (timeout_ms / 1000.0)
    attempt = 0
    poll = max(0, int(poll_ms))
    ino = _which("inotifywait")

    while True:
        attempt += 1

        # Collect candidates with best-effort stat so transient files don't
        # crash the wait loop.
        entries: list[tuple[Path, int]] = []
        for pth in _iter_candidates():
            try:
                st = pth.stat()
                mtime_ns = int(getattr(st, "st_mtime_ns", int(st.st_mtime * 1e9)))
            except Exception:
                mtime_ns = 0
            entries.append((pth, mtime_ns))

        # Sort by mtime then name so we return the most recently changed file.
        entries.sort(key=lambda t: (t[1], t[0].name))

        def _is_new(pth: Path, mtime_ns_val: int) -> bool:
            rp = pth.resolve()
            if rp not in baseline:
                return True
            # Treat modifications of already-existing files as "new" only if
            # they actually changed since the baseline snapshot.
            if since_ns is not None and mtime_ns_val >= int(since_ns):
                base = int(baseline.get(rp, 0))
                if base == 0:
                    return True
                if mtime_ns_val != base:
                    return True
                return False
            return False

        new_files = [pth for (pth, mtime_ns_val) in entries if _is_new(pth, mtime_ns_val)]
        found = new_files[-1] if new_files else None
        if on_attempt is not None:
            on_attempt(attempt, found, bool(found), helper=("inotifywait" if ino else None))
        if found is not None:
            # Best-effort settle: some producers create the file first and only
            # later write content (or write in multiple bursts). For downloads
            # this can show up as a zero-sized placeholder or a file that grows
            # for a while.

            def _wait_until_ready(pth: Path) -> bool:
                # Fast path: keep the historical behavior (a tiny settle for
                # empty files) unless users ask for stricter checks.
                if int(min_size) <= 0 and int(stable_ms) <= 0:
                    try:
                        st0 = pth.stat()
                        if int(st0.st_size) == 0:
                            settle_deadline = min(deadline, time.time() + 0.2)
                            while time.time() < settle_deadline:
                                time.sleep(0.01)
                                try:
                                    st1 = pth.stat()
                                except Exception:
                                    continue
                                if int(st1.st_size) != 0:
                                    break
                    except Exception:
                        pass
                    return True

                # Stricter mode: require min_size + stability window.
                last: tuple[int, int] | None = None
                stable_start = time.time()
                while time.time() <= deadline:
                    try:
                        st = pth.stat()
                    except Exception:
                        time.sleep(0.02)
                        continue
                    size = int(st.st_size)
                    mtime_ns2 = int(getattr(st, "st_mtime_ns", int(st.st_mtime * 1e9)))
                    cur = (size, mtime_ns2)

                    if size < int(min_size):
                        last = cur
                        stable_start = time.time()
                        time.sleep(0.02)
                        continue

                    if int(stable_ms) <= 0:
                        return True

                    if last is None or cur != last:
                        last = cur
                        stable_start = time.time()

                    if (time.time() - stable_start) * 1000.0 >= float(stable_ms):
                        return True

                    time.sleep(0.02)
                return False

            if _wait_until_ready(found):
                return found

        if max_attempts is not None and attempt >= max_attempts:
            break

        # Final chance: ensure we re-check after any helper wait, even if we just crossed the deadline.
        if time.time() > deadline:
            break


        # inotifywait has integer-second timeout resolution and process spawn
        # overhead. For very small timeouts, polling is often more reliable.
        timeout_left = max(0.0, deadline - time.time())
        use_inotify = bool(ino) and timeout_left >= 1.2

        if use_inotify:
            timeout_left = max(0.05, timeout_left)
            cmd = [
                ino,
                "--quiet",
                *( ["--recursive"] if bool(recursive) else [] ),
                "--timeout",
                str(max(1, int(timeout_left + 0.999))),
                "-e",
                "close_write",
                "-e",
                "move",
                "-e",
                "create",
                str(root),
            ]
            try:
                subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_left + 0.2)
            except subprocess.TimeoutExpired:
                pass
        else:
            if poll > 0:
                jitter = random.randint(-jitter_ms, jitter_ms) if jitter_ms else 0
                sleep_ms = max(0, poll + jitter)
                time.sleep(sleep_ms / 1000.0)
            poll = min(max_poll_ms, int(poll * 1.4) + 1) if poll else 0

    raise TimeoutError(f"WaitForNewFile timed out after {timeout_ms}ms in {root}")


# Common partial-download suffixes used by browsers and download tools.
# - Chrome/Chromium: *.crdownload
# - Firefox: *.part
# - Safari: *.download
_DEFAULT_DOWNLOAD_EXCLUDE: list[str] = [
    "*.crdownload",
    "*.part",
    "*.download",
    "*.opdownload",
    "*.partial",
    "*.tmp",
    "*.aria2",
]


def wait_for_download(
    directory: str | Path,
    *,
    pattern: str = "*",
    recursive: bool = False,
    exclude: list[str] | None = None,
    include_existing_changes: bool = False,
    since_ns: int | None = None,
    min_size: int = 1,
    stable_ms: int = 500,
    timeout_ms: int = 30_000,
    poll_ms: int = 200,
    max_poll_ms: int = 1000,
    jitter_ms: int = 30,
    max_attempts: int | None = None,
    on_attempt=None,
) -> Path:
    """Wait for a download-like file to appear and settle.

    This is a small convenience wrapper around wait_for_new_file that:

    - layers in a default exclude list for common partial-download names
    - defaults to `min_size=1` and a small `stable_ms` window

    If include_existing_changes is enabled, files that were already present in
    the directory at baseline can be treated as candidates when they change,
    using since_ns as the threshold.
    """

    ex = list(_DEFAULT_DOWNLOAD_EXCLUDE)
    if exclude:
        ex.extend(list(exclude))

    # De-dupe while preserving order.
    seen = set()
    ex2: list[str] = []
    for pat in ex:
        if pat not in seen:
            seen.add(pat)
            ex2.append(pat)

    eff_since: int | None = None
    if include_existing_changes:
        eff_since = since_ns

    return wait_for_new_file(
        directory,
        pattern=pattern,
        recursive=bool(recursive),
        exclude=ex2,
        min_size=int(min_size),
        stable_ms=int(stable_ms),
        timeout_ms=int(timeout_ms),
        poll_ms=int(poll_ms),
        max_poll_ms=int(max_poll_ms),
        jitter_ms=int(jitter_ms),
        max_attempts=max_attempts,
        since_ns=eff_since,
        on_attempt=on_attempt,
    )


def _parse_retry_after_seconds(value: str) -> float | None:
    """Parse an HTTP Retry-After header value.

    Retry-After can be either:
    - delay-seconds (integer), or
    - an HTTP date.

    Returns a non-negative seconds float, or None if parsing fails.
    """
    v = (value or "").strip()
    if not v:
        return None
    try:
        sec = int(v)
        return max(0.0, float(sec))
    except Exception:
        pass
    try:
        dt = email.utils.parsedate_to_datetime(v)
        # parsedate_to_datetime returns an aware datetime for RFC 2822 dates.
        # Convert to timestamp and compute delta.
        now = time.time()
        ts = dt.timestamp()
        return max(0.0, ts - now)
    except Exception:
        return None


def wait_for_http(
    request_func,
    *,
    method: str,
    url: str,
    headers: dict[str, str] | None = None,
    params: dict[str, object] | None = None,
    body: str | bytes | None = None,
    json_body: object | None = None,
    timeout_ms: int = 30_000,
    allow_error_status: bool = True,
    ok_statuses: list[int] | None = None,
    status_min: int | None = 200,
    status_max: int | None = 299,
    text_contains: str | None = None,
    text_regex: str | None = None,
    check_func=None,
    respect_retry_after: bool = True,
    poll_ms: int = 200,
    max_poll_ms: int = 2000,
    jitter_ms: int = 30,
    max_attempts: int | None = None,
    on_attempt=None,
):
    """Poll an HTTP endpoint until a condition is met.

    The `request_func` should have the same shape as vhk.system.network.http_request.
    """
    deadline = time.time() + (timeout_ms / 1000.0)
    attempt = 0
    poll = max(0, int(poll_ms))
    last_err: Exception | None = None
    last_status: int | None = None
    rx = re.compile(text_regex) if text_regex else None

    while True:
        attempt += 1
        resp = None
        ok = False
        err_str: str | None = None

        try:
            resp = request_func(
                method,
                url,
                headers=headers,
                params=params,
                body=body,
                json_body=json_body,
                timeout_ms=max(1, int(timeout_ms)),
                allow_error_status=bool(allow_error_status),
            )
            last_status = getattr(resp, "status", None)

            # Default checks.
            if ok_statuses is not None:
                ok = int(resp.status) in {int(x) for x in ok_statuses}
            elif status_min is not None or status_max is not None:
                smin = int(status_min) if status_min is not None else -10**9
                smax = int(status_max) if status_max is not None else 10**9
                ok = smin <= int(resp.status) <= smax
            else:
                ok = 200 <= int(resp.status) <= 299

            if ok and text_contains is not None:
                ok = str(text_contains) in resp.text
            if ok and rx is not None:
                ok = rx.search(resp.text) is not None

            if check_func is not None:
                ok = bool(check_func(resp))

        except Exception as e:
            last_err = e
            err_str = str(e) or type(e).__name__
            ok = False

        if on_attempt is not None:
            on_attempt(attempt, resp, ok, err_str)

        if ok and resp is not None:
            return resp, attempt

        if max_attempts is not None and attempt >= int(max_attempts):
            break

        if time.time() > deadline:
            break

        # Sleep/backoff.
        timeout_left = max(0.0, deadline - time.time())
        sleep_s = 0.0
        if respect_retry_after and resp is not None:
            ra = None
            try:
                ra = resp.headers.get("retry-after")  # headers are normalized to lower-case in network.py
            except Exception:
                ra = None
            if ra:
                parsed = _parse_retry_after_seconds(str(ra))
                if parsed is not None:
                    sleep_s = min(timeout_left, float(parsed))

        if sleep_s <= 0.0:
            if poll > 0:
                jitter = random.randint(-jitter_ms, jitter_ms) if jitter_ms else 0
                sleep_ms = max(0, poll + jitter)
                sleep_s = min(timeout_left, sleep_ms / 1000.0)
            poll = min(max_poll_ms, int(poll * 1.4) + 1) if poll else 0

        if sleep_s > 0:
            time.sleep(sleep_s)

    msg = f"WaitForHttp timed out after {timeout_ms}ms"
    if last_status is not None:
        msg += f" (last status {last_status})"
    if last_err is not None:
        msg += f" (last error: {type(last_err).__name__}: {last_err})"
    raise TimeoutError(msg)
