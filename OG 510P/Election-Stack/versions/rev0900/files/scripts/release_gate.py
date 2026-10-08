#!/usr/bin/env python3
"""scripts/release_gate.py

One-command release gate runner.

This is intentionally stdlib-only. It runs the required checks in docs/162 in
stable order, keeps child checks isolated in subprocesses, and exposes bounded
slice/profile controls for diagnostics without turning a partial run into a
release verdict.  With ``--write-manifest --build-zip ABSOLUTE_PATH`` it also
binds the full gate, manifest write, deterministic ZIP build, and ZIP verifier
under the same single-instance lock.
"""

from __future__ import annotations

import argparse
import os
import signal
import subprocess
import sys

# The gate imports a local inventory module before it runs the cache-artifact
# hygiene check. Do not create __pycache__ merely by asking for --list or
# starting the gate. Child checks also receive PYTHONDONTWRITEBYTECODE=1.
sys.dont_write_bytecode = True

import tempfile
import time
from pathlib import Path

import build_release_zip
import release_gate_steps
import release_gate_lock

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_STEP_TIMEOUT_S = 60
POSIX = os.name == "posix"


def _positive_int(raw: object, label: str) -> int:
    try:
        value = int(str(raw))
    except (TypeError, ValueError):
        print(f"FAIL invalid {label} {raw!r}; use a positive integer number of seconds")
        return -1
    if value <= 0:
        print(f"FAIL invalid {label} {raw!r}; use a positive integer number of seconds")
        return -1
    return value


def step_timeout_from_env(env: dict[str, str], override: int | None = None) -> int:
    if override is not None:
        return _positive_int(override, "--step-timeout")
    raw = env.get("ELECTION_STACK_RELEASE_STEP_TIMEOUT", str(DEFAULT_STEP_TIMEOUT_S))
    return _positive_int(raw, "ELECTION_STACK_RELEASE_STEP_TIMEOUT")


def label_for(cmd: list[str]) -> str:
    return " ".join(cmd[1:]) if cmd and cmd[0] == sys.executable else " ".join(cmd)


def step_name(cmd: list[str]) -> str:
    for part in reversed(cmd):
        if part.endswith(".py"):
            return Path(part).name
    return label_for(cmd)


def _kill_process_group(proc: subprocess.Popen[str]) -> None:
    if proc.poll() is not None:
        return
    if POSIX:
        try:
            os.killpg(proc.pid, signal.SIGTERM)
        except ProcessLookupError:
            return
        except OSError:
            proc.terminate()
    else:
        proc.terminate()


def _kill_process_group_force(proc: subprocess.Popen[str]) -> None:
    if proc.poll() is not None:
        return
    if POSIX:
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except ProcessLookupError:
            return
        except OSError:
            proc.kill()
    else:
        proc.kill()


def _proc_stat_pgrp_session(stat_text: str) -> tuple[int, int] | None:
    """Return (process_group, session) from a Linux ``/proc/<pid>/stat`` line."""

    # Field 2 is the command in parentheses and can contain spaces.  Parse from
    # the final ``)`` before the fixed numeric fields.  After that point the
    # fields begin: state, ppid, pgrp, session, ...
    end = stat_text.rfind(")")
    if end < 0 or end + 2 >= len(stat_text):
        return None
    rest = stat_text[end + 2 :].split()
    if len(rest) < 4:
        return None
    try:
        return int(rest[2]), int(rest[3])
    except ValueError:
        return None


def _process_group_member_pids(pgid: int, *, session_id: int | None = None) -> list[int]:
    """Return live POSIX PIDs still in a child process group.

    Post-step cleanup should not use ``killpg(pgid, 0)`` as a discovery
    primitive.  If a group id is unexpectedly reused or projected oddly by the
    host environment, a diagnostic release-gate slice could signal an unrelated
    group.  On Linux, enumerate ``/proc`` and require both the child process
    group and the child session id to match.  On other POSIX platforms, skip the
    post-completion daemonization sweep rather than risk killing the runner.
    Timeout handling still uses direct process-group signalling while the named
    child process is alive.
    """

    if not POSIX:
        return []
    proc_root = Path("/proc")
    if not proc_root.is_dir():
        return []

    self_pid = os.getpid()
    members: list[int] = []
    for entry in proc_root.iterdir():
        if not entry.name.isdigit():
            continue
        pid = int(entry.name)
        if pid == self_pid:
            continue
        try:
            parsed = _proc_stat_pgrp_session((entry / "stat").read_text(encoding="utf-8", errors="replace"))
        except OSError:
            continue
        if parsed is None:
            continue
        pgrp, sid = parsed
        if pgrp != pgid:
            continue
        if session_id is not None and sid != session_id:
            continue
        members.append(pid)
    return sorted(members)


def _signal_pids(pids: list[int], sig: signal.Signals) -> None:
    for pid in pids:
        try:
            os.kill(pid, sig)
        except (ProcessLookupError, OSError):
            continue


def _cleanup_leftover_process_group(pgid: int, *, session_id: int | None = None) -> list[int]:
    """Return descendants that outlive a completed child step.

    Release-gate children are not allowed to daemonize.  Older revisions tried
    to terminate any post-step process-group members immediately after each
    child completed.  In containerized/PID-namespace environments that is too
    sharp a tool: a diagnostic release-gate run must never risk signalling the
    harness that invoked it.

    The default behavior is now detect-and-fail-closed: report scoped leftover
    PIDs to the caller and let the child step fail, but do not send signals.
    Maintainers who are running the gate on an isolated local machine can opt
    into the old termination behavior with
    ``ELECTION_STACK_RELEASE_GATE_TERMINATE_LEFTOVERS=1``.
    """

    members = _process_group_member_pids(pgid, session_id=session_id)
    if not members:
        return []

    if os.environ.get("ELECTION_STACK_RELEASE_GATE_TERMINATE_LEFTOVERS") != "1":
        return members

    _signal_pids(members, signal.SIGTERM)
    time.sleep(0.05)
    survivors = _process_group_member_pids(pgid, session_id=session_id)
    if survivors:
        _signal_pids(survivors, signal.SIGKILL)
    return _process_group_member_pids(pgid, session_id=session_id)


def run(
    cmd: list[str],
    *,
    quiet: bool,
    timeout_override: int | None,
    progress: bool,
    profile: bool,
    ordinal: int | None = None,
    total: int | None = None,
) -> bool:
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    timeout_s = step_timeout_from_env(env, timeout_override)
    if timeout_s < 1:
        return False

    label = label_for(cmd)
    if progress:
        prefix = f"RUN {ordinal:03d}/{total:03d}" if ordinal is not None and total is not None else "RUN"
        print(prefix, label, flush=True)

    start = time.monotonic()
    leftover_pids: list[int] = []
    with tempfile.TemporaryDirectory(prefix="tes_release_gate_step_") as td:
        stdout_path = Path(td) / "stdout.txt"
        stderr_path = Path(td) / "stderr.txt"
        try:
            with stdout_path.open("w", encoding="utf-8", newline="") as stdout_file, stderr_path.open("w", encoding="utf-8", newline="") as stderr_file:
                proc = subprocess.Popen(
                    cmd,
                    stdin=subprocess.DEVNULL,
                    stdout=stdout_file,
                    stderr=stderr_file,
                    text=True,
                    env=env,
                    cwd=ROOT,
                    start_new_session=POSIX,
                )
                try:
                    proc.wait(timeout=timeout_s)
                except subprocess.TimeoutExpired:
                    _kill_process_group(proc)
                    try:
                        proc.wait(timeout=3)
                    except subprocess.TimeoutExpired:
                        _kill_process_group_force(proc)
                        proc.wait()
                    elapsed = time.monotonic() - start
                    stdout_file.flush()
                    stderr_file.flush()
                    stdout = stdout_path.read_text(encoding="utf-8", errors="replace")
                    stderr = stderr_path.read_text(encoding="utf-8", errors="replace")
                    print("FAIL", label)
                    print(f"timed out after {timeout_s}s (elapsed {elapsed:.2f}s)")
                    if stdout:
                        print(stdout.rstrip())
                    if stderr:
                        print(stderr.rstrip())
                    return False
                finally:
                    if POSIX:
                        leftover_pids = _cleanup_leftover_process_group(proc.pid, session_id=proc.pid)
        except OSError as exc:
            print("FAIL", label)
            print(f"could not start child process: {exc}")
            return False

        elapsed = time.monotonic() - start
        ok = proc.returncode == 0 and not leftover_pids
        stdout = stdout_path.read_text(encoding="utf-8", errors="replace")
        stderr = stderr_path.read_text(encoding="utf-8", errors="replace")
        if leftover_pids:
            stderr = (stderr + "\n" if stderr else "") + (
                "release-gate child left scoped process-group members after exit; "
                f"pids={leftover_pids}; set ELECTION_STACK_RELEASE_GATE_TERMINATE_LEFTOVERS=1 "
                "only on an isolated local machine to terminate them automatically"
            )
    if quiet and ok and not profile:
        return True

    status = "PASS" if ok else "FAIL"
    timing = f" ({elapsed:.2f}s)" if profile else ""
    print(status, label + timing)
    if stdout:
        print(stdout.rstrip())
    if stderr:
        print(stderr.rstrip())
    return ok


def _normalise_step_ref(ref: str) -> str:
    ref = ref.strip()
    if ref.startswith("scripts/"):
        ref = ref.split("/", 1)[1]
    if ref and not ref.endswith(".py") and not ref.isdigit():
        ref = ref + ".py"
    return ref


def _resolve_step_ref(ref: str, check_steps: list[list[str]]) -> int:
    ref = _normalise_step_ref(ref)
    if not ref:
        raise ValueError("empty step reference")
    if ref.isdigit():
        idx = int(ref)
        if idx < 1 or idx > len(check_steps):
            raise ValueError(f"step number {idx} outside 1..{len(check_steps)}")
        return idx - 1

    matches = [i for i, cmd in enumerate(check_steps) if step_name(cmd) == ref]
    if not matches:
        raise ValueError(f"unknown release-gate step {ref!r}")
    return matches[0]


def select_steps(
    check_steps: list[list[str]],
    *,
    only: str | None,
    from_step: str | None,
    to_step: str | None,
) -> tuple[list[list[str]], bool]:
    selectors = [bool(only), bool(from_step), bool(to_step)]
    partial = any(selectors)

    if only and (from_step or to_step):
        raise ValueError("use either --only or --from-step/--to-step, not both")

    if only:
        selected: list[list[str]] = []
        seen: set[int] = set()
        for raw in only.split(","):
            idx = _resolve_step_ref(raw, check_steps)
            if idx not in seen:
                selected.append(check_steps[idx])
                seen.add(idx)
        return selected, True

    if from_step or to_step:
        start = _resolve_step_ref(from_step, check_steps) if from_step else 0
        end = _resolve_step_ref(to_step, check_steps) if to_step else len(check_steps) - 1
        if start > end:
            raise ValueError("--from-step must not come after --to-step")
        return check_steps[start : end + 1], True

    return list(check_steps), partial


def print_step_list(check_steps: list[list[str]], manifest_step: list[str]) -> None:
    for i, cmd in enumerate(check_steps, 1):
        print(f"{i:03d} {step_name(cmd)}")
    print(f"manifest {label_for(manifest_step)}")


def release_zip_steps(out_zip: str) -> list[list[str]]:
    """Return the deterministic build and independent verifier commands."""

    return [
        [
            sys.executable,
            str(ROOT / "scripts" / "build_release_zip.py"),
            "--root",
            str(ROOT),
            "--out",
            out_zip,
        ],
        [sys.executable, str(ROOT / "scripts" / "verify_release_zip.py"), out_zip],
    ]


def _preflight_release_zip_request(args: argparse.Namespace, *, partial: bool) -> bool:
    out_zip = getattr(args, "build_zip", None)
    if not out_zip:
        return True
    if not args.write_manifest:
        print("FAIL: --build-zip requires --write-manifest so the built ZIP seals the checked tree")
        return False
    if args.skip_manifest:
        print("FAIL: --build-zip cannot be combined with --skip-manifest")
        return False
    if partial:
        print("FAIL: --build-zip requires the full release gate, not a diagnostic subset")
        return False
    raw = Path(out_zip)
    if not raw.is_absolute():
        print("FAIL: --build-zip requires an absolute output path")
        return False
    try:
        audited = build_release_zip.preflight_output_path(out_zip)
    except SystemExit as exc:
        print(f"FAIL: invalid --build-zip output path: {exc}")
        return False
    if audited.exists():
        print(f"FAIL: --build-zip output already exists; refusing to replace it: {audited}")
        return False
    return True


def _remove_failed_release_zip(out_zip: str) -> bool:
    """Remove a newly built ZIP after verifier failure; return cleanup success."""

    try:
        Path(out_zip).unlink(missing_ok=True)
    except OSError as exc:
        print(f"FAIL: verifier rejected the release ZIP and cleanup failed: {exc}")
        return False
    return True


def _run_selected_gate(args: argparse.Namespace, check_steps: list[list[str]], manifest_step: list[str]) -> int:
    if args.write_manifest and args.skip_manifest:
        print("FAIL: --write-manifest cannot be combined with --skip-manifest")
        return 2

    try:
        selected_steps, partial = select_steps(
            check_steps,
            only=args.only,
            from_step=args.from_step,
            to_step=args.to_step,
        )
    except ValueError as exc:
        print(f"FAIL: {exc}")
        return 2

    if args.write_manifest and partial:
        print("FAIL: --write-manifest requires the full release gate, not a diagnostic subset")
        return 2
    if not _preflight_release_zip_request(args, partial=partial):
        return 2

    run_manifest = not args.skip_manifest and not partial
    if partial and not args.quiet:
        print("INFO diagnostic subset selected; final manifest step is skipped")

    ok_all = True
    zip_steps = release_zip_steps(args.build_zip) if getattr(args, "build_zip", None) else []
    total = len(selected_steps) + (1 if run_manifest else 0) + len(zip_steps)
    ordinal = 0
    for s in selected_steps:
        ordinal += 1
        ok = run(
            s,
            quiet=args.quiet,
            timeout_override=args.step_timeout,
            progress=args.progress,
            profile=args.profile,
            ordinal=ordinal,
            total=total,
        )
        ok_all = ok_all and ok
        if not ok and not args.keep_going:
            return 2

    if not ok_all:
        if run_manifest:
            print("FAIL release gate: previous step failed; skipping manifest write/check")
        return 2

    if run_manifest:
        ordinal += 1
        ok_all = run(
            manifest_step,
            quiet=args.quiet,
            timeout_override=args.step_timeout,
            progress=args.progress,
            profile=args.profile,
            ordinal=ordinal,
            total=total,
        )

    if not ok_all:
        return 2

    for idx, cmd in enumerate(zip_steps):
        ordinal += 1
        ok = run(
            cmd,
            quiet=args.quiet,
            timeout_override=args.step_timeout,
            progress=args.progress,
            profile=args.profile,
            ordinal=ordinal,
            total=total,
        )
        if not ok:
            if idx == 1:
                _remove_failed_release_zip(args.build_zip)
            return 2

    return 0

def main() -> int:
    ap = argparse.ArgumentParser(description="Run the archive release gate")
    ap.add_argument("--quiet", action="store_true", help="only emit failures")
    ap.add_argument(
        "--write-manifest",
        action="store_true",
        help="regenerate MANIFEST.sha256 after all other release checks pass",
    )
    ap.add_argument(
        "--keep-going",
        action="store_true",
        help="continue after failures to collect diagnostics; manifest step is still skipped if any earlier step fails",
    )
    ap.add_argument("--list", action="store_true", help="print numbered release-gate child steps and exit")
    ap.add_argument("--only", help="run a comma-separated diagnostic subset by number or script name")
    ap.add_argument("--from-step", help="first diagnostic child step to run, by number or script name")
    ap.add_argument("--to-step", help="last diagnostic child step to run, by number or script name")
    ap.add_argument("--skip-manifest", action="store_true", help="skip final manifest check/write for diagnostics")
    ap.add_argument(
        "--build-zip",
        metavar="ABSOLUTE_PATH",
        help=(
            "after a full --write-manifest gate, build a new deterministic ZIP at this absolute path "
            "and verify it before returning success; existing outputs are never replaced"
        ),
    )
    ap.add_argument("--profile", action="store_true", help="print elapsed time for each completed step")
    ap.add_argument("--progress", action="store_true", help="print each step before it starts")
    ap.add_argument("--step-timeout", type=int, help="per-step timeout override in seconds for this invocation")
    args = ap.parse_args()

    py = sys.executable

    check_steps = release_gate_steps.build_check_steps(ROOT, py)


    manifest_step = release_gate_steps.build_manifest_step(ROOT, py, check=not args.write_manifest)


    if args.list:
        print_step_list(check_steps, manifest_step)
        return 0

    try:
        with release_gate_lock.acquire_release_gate_lock(ROOT):
            return _run_selected_gate(args, check_steps, manifest_step)
    except release_gate_lock.ReleaseGateLockError as exc:
        print(f"FAIL release gate single-instance lock: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
