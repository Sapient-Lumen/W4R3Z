#!/usr/bin/env python3
"""Check release-gate single-instance locking and detect-only leftover handling.

The release gate mutates generated control surfaces before manifest sealing.  Two
concurrent gate runs against the same source root are therefore unsafe.  The
runner must also avoid signalling the harness by default when it notices a child
step that daemonized; it should fail closed and report scoped leftovers instead.
"""

from __future__ import annotations

import contextlib
import io
import os
import subprocess
import sys
import tempfile
import textwrap
import time
from pathlib import Path

sys.dont_write_bytecode = True

import release_gate
import release_gate_lock

ROOT = Path(__file__).resolve().parents[1]


def fail(msg: str) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    raise SystemExit(2)


def run_py(code: str, *, env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-S", "-c", code],
        cwd=ROOT,
        env=env,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
        timeout=30,
    )


def assert_lock_exclusion() -> None:
    with tempfile.TemporaryDirectory(prefix="tes_release_gate_lock_check_") as td:
        lock_dir = Path(td)
        env = dict(os.environ)
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        env["ELECTION_STACK_RELEASE_GATE_LOCK_DIR"] = str(lock_dir)
        env["PYTHONPATH"] = str(ROOT / "scripts") + os.pathsep + env.get("PYTHONPATH", "")

        lock_path = release_gate_lock.lock_path_for_root(ROOT, lock_dir=lock_dir)
        if ROOT.resolve() in lock_path.resolve().parents:
            fail(f"release-gate lock path is inside the release root: {lock_path}")

        with release_gate_lock.acquire_release_gate_lock(ROOT, lock_dir=lock_dir):
            nested = run_py(
                """
from pathlib import Path
import release_gate_lock
try:
    with release_gate_lock.acquire_release_gate_lock(Path('.').resolve()):
        raise SystemExit(7)
except release_gate_lock.ReleaseGateLockError as exc:
    print(str(exc))
    raise SystemExit(0)
""".strip(),
                env=env,
            )
            if nested.returncode != 0 or "already running" not in (nested.stdout + nested.stderr):
                fail(
                    "nested release-gate lock acquisition did not fail closed "
                    f"rc={nested.returncode} stdout={nested.stdout!r} stderr={nested.stderr!r}"
                )

            listed = subprocess.run(
                [sys.executable, "-S", str(ROOT / "scripts" / "release_gate.py"), "--list"],
                cwd=ROOT,
                env=env,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
                timeout=30,
            )
            if listed.returncode != 0 or "check_index.py" not in listed.stdout:
                fail("release_gate.py --list should remain available without acquiring the mutation lock")

            blocked_runner = subprocess.run(
                [
                    sys.executable,
                    "-S",
                    str(ROOT / "scripts" / "release_gate.py"),
                    "--only",
                    "check_version_consistency.py",
                    "--quiet",
                    "--skip-manifest",
                ],
                cwd=ROOT,
                env=env,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
                timeout=30,
            )
            blocked_text = blocked_runner.stdout + blocked_runner.stderr
            if blocked_runner.returncode == 0 or "single-instance lock" not in blocked_text:
                fail(
                    "release_gate.py did not fail closed under an already-held lock "
                    f"rc={blocked_runner.returncode} stdout={blocked_runner.stdout!r} stderr={blocked_runner.stderr!r}"
                )

        reacquired = run_py(
            """
from pathlib import Path
import release_gate_lock
with release_gate_lock.acquire_release_gate_lock(Path('.').resolve()):
    print('reacquired')
""".strip(),
            env=env,
        )
        if reacquired.returncode != 0 or "reacquired" not in reacquired.stdout:
            fail(f"release-gate lock did not release cleanly: rc={reacquired.returncode} stderr={reacquired.stderr!r}")


def _pid_active_not_zombie(pid: int) -> bool:
    """Return true only for a running process, not a zombie/reaped PID.

    The checker must never signal a process merely to clean up a synthetic
    release-gate leftover.  In cloud/PID-namespace harnesses a numeric PID can
    be translated or reused in surprising ways; natural expiry is safer than a
    self-test that sends SIGTERM/SIGKILL.
    """

    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True

    try:
        stat_text = Path(f"/proc/{pid}/stat").read_text(encoding="utf-8", errors="replace")
    except OSError:
        return True
    end = stat_text.rfind(")")
    if end >= 0 and end + 2 < len(stat_text):
        fields = stat_text[end + 2 :].split()
        if fields and fields[0] == "Z":
            return False
    return True


def assert_stale_lock_recovery() -> None:
    """Prove dead-PID locks self-heal while corrupt/live holders fail closed."""

    with tempfile.TemporaryDirectory(prefix="tes_release_gate_stale_lock_check_") as td:
        lock_dir = Path(td)
        lock_path = release_gate_lock.lock_path_for_root(ROOT, lock_dir=lock_dir)

        stale_pid = 99999999
        while _pid_active_not_zombie(stale_pid):
            stale_pid += 1
        lock_path.write_text(f"pid={stale_pid} root={ROOT.resolve()} acquired_at_unix=0\n", encoding="utf-8")
        with release_gate_lock.acquire_release_gate_lock(ROOT, lock_dir=lock_dir):
            holder = lock_path.read_text(encoding="utf-8", errors="replace")
            if f"pid={os.getpid()}" not in holder:
                fail(f"stale release-gate lock was not replaced by current holder: {holder!r}")

        lock_path.write_text("pid=not-a-number root=x acquired_at_unix=0\n", encoding="utf-8")
        try:
            with release_gate_lock.acquire_release_gate_lock(ROOT, lock_dir=lock_dir):
                fail("corrupt release-gate lock metadata should fail closed, not be discarded")
        except release_gate_lock.ReleaseGateLockError as exc:
            if "already running" not in str(exc):
                fail(f"corrupt release-gate lock failed with unexpected message: {exc}")
        lock_path.unlink(missing_ok=True)

        lock_path.write_text(f"pid={os.getpid()} root={ROOT.resolve()} acquired_at_unix=0\n", encoding="utf-8")
        try:
            with release_gate_lock.acquire_release_gate_lock(ROOT, lock_dir=lock_dir):
                fail("live release-gate lock should fail closed")
        except release_gate_lock.ReleaseGateLockError as exc:
            if "already running" not in str(exc):
                fail(f"live release-gate lock failed with unexpected message: {exc}")


def assert_leftover_detection_without_default_termination() -> None:
    if os.name != "posix":
        return
    old = os.environ.pop("ELECTION_STACK_RELEASE_GATE_TERMINATE_LEFTOVERS", None)
    try:
        with tempfile.TemporaryDirectory(prefix="tes_release_gate_leftover_check_") as td:
            tdir = Path(td)
            pidfile = tdir / "leftover.pid"
            child = tdir / "daemonizing_child.py"
            child.write_text(
                textwrap.dedent(
                    f"""
                    import os
                    import subprocess
                    import sys
                    from pathlib import Path
                    # Keep the synthetic leftover alive long enough for the
                    # release-gate runner to detect it, then let it expire on
                    # its own. The checker intentionally sends no cleanup
                    # signal; PID namespace/reuse ambiguity is part of the
                    # risk this self-test must avoid.
                    p = subprocess.Popen(
                        [sys.executable, '-S', '-c', 'import time; time.sleep(2.0)'],
                        stdin=subprocess.DEVNULL,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        close_fds=True,
                    )
                    Path({str(pidfile)!r}).write_text(str(p.pid), encoding='utf-8')
                    os._exit(0)
                    """
                ).strip(),
                encoding="utf-8",
            )
            captured_out = io.StringIO()
            captured_err = io.StringIO()
            with contextlib.redirect_stdout(captured_out), contextlib.redirect_stderr(captured_err):
                ok = release_gate.run(
                    [sys.executable, "-S", str(child)],
                    quiet=True,
                    timeout_override=5,
                    progress=False,
                    profile=False,
                )
            captured_text = captured_out.getvalue() + captured_err.getvalue()
            if ok:
                fail("release_gate.run accepted a child step that left a scoped process-group member behind")
            if "left scoped process-group members" not in captured_text:
                fail(f"leftover detection did not report the scoped process-group member: {captured_text!r}")
            if not pidfile.exists():
                fail("daemonizing child did not write a leftover pidfile")
            pid = int(pidfile.read_text(encoding="utf-8").strip())
            if not _pid_active_not_zombie(pid):
                fail("detect-only release-gate leftover path terminated the synthetic leftover before it could be observed")

            deadline = time.time() + 6
            while time.time() < deadline and _pid_active_not_zombie(pid):
                time.sleep(0.05)
            if _pid_active_not_zombie(pid):
                fail(
                    "synthetic release-gate leftover did not expire naturally; "
                    "refusing to send cleanup signals from the self-test"
                )
    finally:
        if old is not None:
            os.environ["ELECTION_STACK_RELEASE_GATE_TERMINATE_LEFTOVERS"] = old


def main() -> int:
    assert_lock_exclusion()
    assert_stale_lock_recovery()
    assert_leftover_detection_without_default_termination()
    print("PASS: release-gate single-instance lock and detect-only leftover handling are bounded")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
