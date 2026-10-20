#!/usr/bin/env python3
"""Plan, rehearse, and launch the IoTox massive soak campaign.

This is an operator/lab orchestrator.  It intentionally composes the native
IoTox binary surfaces and the existing Sandwurm/Toxic lab tools instead of
inventing a second product semantics layer.

The safe default is:

    tools/run-massive-soak.py plan
    tools/run-massive-soak.py preflight
    tools/run-massive-soak.py smoke

The true elapsed campaign is explicit:

    tools/run-massive-soak.py launch-long --include sync --include terminal ...

Long-running processes are recorded in a bounded manifest below
.sandwurm/massive-soak so status/watch/stop can target only the campaign's own
children.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import glob
import hashlib
import importlib.util
import json
import os
import pathlib
import random
import shlex
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from dataclasses import asdict, dataclass
from typing import Any


SCHEMA = "iotox.massive-soak.v1"
MANIFEST = "campaign.json"
DEFAULT_ROOT = pathlib.Path(".sandwurm/massive-soak")
DEFAULT_TERMINAL_SECONDS = 86_400
DEFAULT_TERMINAL_SAMPLE_EVERY = 300
DEFAULT_PERSON_CYCLES = 1_440
DEFAULT_PERSON_INTERVAL = 60
DEFAULT_TOXIC_SECONDS = 86_400


class SoakError(RuntimeError):
    pass


@dataclass(frozen=True)
class Stage:
    name: str
    surface: str
    mode: str
    command: list[str]
    duration_seconds: int | None
    required_for: str
    description: str
    receipt: str | None = None
    optional: bool = False


@dataclass
class StepResult:
    name: str
    command: list[str]
    returncode: int
    expected_returncodes: list[int]
    elapsed_seconds: float
    log: str
    status: str


def repo_root() -> pathlib.Path:
    return pathlib.Path(__file__).resolve().parents[1]


def now_utc() -> str:
    return _dt.datetime.now(tz=_dt.timezone.utc).replace(microsecond=0).isoformat()


def run_id() -> str:
    stamp = _dt.datetime.now(tz=_dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    suffix = "".join(random.choice("abcdefghijklmnopqrstuvwxyz0123456789") for _ in range(8))
    return f"run.{stamp}.{suffix}"


def shell_join(command: list[str]) -> str:
    return shlex.join(command)


def sha256_file(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def default_sodium_library() -> str | None:
    if os.environ.get("IOTOX_SODIUM_LIBRARY"):
        return os.environ["IOTOX_SODIUM_LIBRARY"]
    if shutil.which("pkg-config"):
        result = subprocess.run(
            ["pkg-config", "--variable=libdir", "libsodium"],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            timeout=10,
        )
        if result.returncode == 0:
            directory = pathlib.Path(result.stdout.strip())
            for name in ("libsodium.so.23", "libsodium.so", "libsodium.dylib"):
                candidate = directory / name
                if candidate.exists():
                    return str(candidate)
    for pattern in (
        "/nix/store/*-libsodium-*/lib/libsodium.so.23",
        "/nix/store/*-libsodium-*/lib/libsodium.so",
        "/run/current-system/sw/lib/libsodium.so.23",
        "/run/current-system/sw/lib/libsodium.so",
    ):
        matches = sorted(glob.glob(pattern))
        if matches:
            return matches[0]
    return None


def command_env() -> dict[str, str]:
    env = os.environ.copy()
    sodium = default_sodium_library()
    if sodium and "IOTOX_SODIUM_LIBRARY" not in env:
        env["IOTOX_SODIUM_LIBRARY"] = sodium
    return env


def resolve_path(path: pathlib.Path) -> pathlib.Path:
    if path.is_absolute():
        return path
    return (repo_root() / path).resolve()


def default_iotox() -> pathlib.Path:
    root = repo_root()
    candidates = [
        root / "build" / "iotox",
        root / "build" / "iotox-nix-debug" / "iotox",
        root / "build" / "gcc-debug" / "iotox",
        root / "build" / "debug" / "iotox",
    ]
    for candidate in candidates:
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return candidate.resolve()
    found = shutil.which("iotox")
    if found:
        return pathlib.Path(found).resolve()
    return (root / "build" / "iotox").resolve()


def resolve_toxic_iotox(value: str | None = None) -> pathlib.Path:
    """Resolve the IoTox binary used by live Toxic bridge labs.

    The ordinary build/iotox used by fast native receipts may be a
    runtime-loaded provider build.  The Toxic compatibility labs need a genuine
    c-toxcore-capable process; the single-device Toxic harness already carries
    the canonical source-linked auto-build path, so reuse it here instead of
    teaching this campaign runner a second copy of that build recipe.
    """

    if value:
        candidate = pathlib.Path(value).resolve()
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return candidate
        raise SoakError(f"requested Toxic IoTox binary is not executable: {candidate}")

    helper = repo_root() / "tools" / "run-toxic-compat-bridge-lab.py"
    spec = importlib.util.spec_from_file_location("iotox_toxic_compat_lab", helper)
    if spec is None or spec.loader is None:
        raise SoakError(f"unable to load Toxic compatibility helper: {helper}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    try:
        return pathlib.Path(module.resolve_iotox(None, True)).resolve()
    except Exception as exc:  # pragma: no cover - defensive wrapper for helper errors.
        raise SoakError(f"unable to resolve source-linked IoTox for Toxic loop: {exc}") from exc


def require_safe_root(root: pathlib.Path) -> pathlib.Path:
    resolved = resolve_path(root)
    repo = repo_root().resolve()
    try:
        resolved.relative_to(repo)
    except ValueError as exc:
        raise SoakError(f"campaign root must stay inside the repository: {resolved}") from exc
    if resolved == repo:
        raise SoakError("campaign root cannot be the repository root")
    return resolved


def ensure_private_dir(path: pathlib.Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    try:
        path.chmod(0o700)
    except PermissionError:
        pass


def command_result(
    name: str,
    command: list[str],
    *,
    log: pathlib.Path,
    expected: set[int] | None = None,
    timeout: float = 120.0,
) -> StepResult:
    expected_codes = expected or {0}
    started = time.monotonic()
    with log.open("wb") as output:
        output.write(("$ " + shell_join(command) + "\n").encode("utf-8"))
        output.flush()
        try:
            proc = subprocess.run(
                command,
                cwd=repo_root(),
                stdout=output,
                stderr=subprocess.STDOUT,
                env=command_env(),
                timeout=timeout,
            )
            rc = proc.returncode
        except subprocess.TimeoutExpired as exc:
            output.write((f"\n[timeout after {timeout:.1f}s]\n").encode("utf-8"))
            rc = 124
        output.flush()
    elapsed = time.monotonic() - started
    status = "passed" if rc in expected_codes else "failed"
    return StepResult(
        name=name,
        command=command,
        returncode=rc,
        expected_returncodes=sorted(expected_codes),
        elapsed_seconds=round(elapsed, 3),
        log=str(log),
        status=status,
    )


def latest_manifest(root: pathlib.Path) -> pathlib.Path | None:
    current = root / "current"
    if current.is_symlink():
        target = current.resolve()
        manifest = target / MANIFEST
        if manifest.is_file():
            return manifest
    if current.is_dir() and (current / MANIFEST).is_file():
        return current / MANIFEST
    manifests = sorted(root.glob("run.*/" + MANIFEST), key=lambda item: item.stat().st_mtime)
    return manifests[-1] if manifests else None


def write_json(path: pathlib.Path, data: dict[str, Any]) -> None:
    temporary = path.with_name("." + path.name + ".tmp")
    temporary.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.chmod(0o600)
    temporary.replace(path)


def update_current(root: pathlib.Path, campaign: pathlib.Path) -> None:
    current = root / "current"
    if current.exists() or current.is_symlink():
        if current.is_symlink() or current.is_file():
            current.unlink()
        elif current.is_dir():
            # A preexisting directory named current is not one of this tool's
            # symlinks.  Leave it alone and rely on explicit --campaign for
            # status/stop.
            return
    current.symlink_to(campaign.name)


def build_stages(
    *,
    iotox: pathlib.Path,
    toxic_iotox: pathlib.Path | None = None,
    root: pathlib.Path,
    terminal_seconds: int,
    terminal_sample_every: int,
    person_cycles: int,
    person_interval: int,
    toxic_seconds: int,
) -> list[Stage]:
    proof = root / "proof"
    terminal_receipt = proof / "terminal-long-soak.receipt"
    terminal_smoke = proof / "terminal-smoke.receipt"
    person_root = root / "person"
    toxic_root = root / "toxic"
    service_root = root / "service-root"
    sync_receipt = proof / "sync-long-soak.json"
    toxic_default_command = [
        sys.executable,
        str(repo_root() / "tools" / "run-massive-soak.py"),
        "toxic-loop",
        "--root",
        str(toxic_root / "default"),
        "--seconds",
        str(toxic_seconds),
        "--variant",
        "default",
    ]
    toxic_forced_tcp_command = [
        sys.executable,
        str(repo_root() / "tools" / "run-massive-soak.py"),
        "toxic-loop",
        "--root",
        str(toxic_root / "forced-tcp"),
        "--seconds",
        str(toxic_seconds),
        "--variant",
        "forced-tcp",
    ]
    if toxic_iotox is not None:
        toxic_default_command.extend(["--iotox", str(toxic_iotox)])
        toxic_forced_tcp_command.extend(["--iotox", str(toxic_iotox)])
    toxic_default_command.append("--keep-going")
    toxic_forced_tcp_command.append("--keep-going")

    return [
        Stage(
            name="host.full-ctest",
            surface="repo",
            mode="preflight",
            command=[
                "ctest",
                "--test-dir",
                "build",
                "--output-on-failure",
                "-j",
                str(max(1, os.cpu_count() or 1)),
            ],
            duration_seconds=None,
            required_for="all",
            description="full host unit/coherence suite before trusting a soak run",
        ),
        Stage(
            name="sync.current-long-receipt",
            surface="sync",
            mode="preflight",
            command=[
                "tools/iotox-repo.sh",
                "current-sync-long-soak-receipt",
                "--out",
                str(sync_receipt),
            ],
            duration_seconds=None,
            required_for="sync.long-soak",
            description="mint the native receipt from the current accepted 24h three-writer proof",
            receipt=str(sync_receipt),
        ),
        Stage(
            name="sync.three-writer-smoke",
            surface="sync",
            mode="smoke",
            command=["tools/iotox-sandwurm-lab.sh", "up-three-writer", "soak-smoke"],
            duration_seconds=None,
            required_for="sync.daily-folder",
            description="short VM-backed three-writer rehearsal before the real 24h cell",
            optional=True,
        ),
        Stage(
            name="sync.three-writer-24h",
            surface="sync",
            mode="long",
            command=["tools/iotox-sandwurm-lab.sh", "up-three-writer", "soak-24h"],
            duration_seconds=86_400,
            required_for="sync.long-soak",
            description="real Sandwurm three-writer elapsed soak; use watch/status helpers on its proof root",
        ),
        Stage(
            name="terminal.native-smoke",
            surface="terminal",
            mode="smoke",
            command=[
                str(iotox),
                "terminal",
                "soak-run",
                "--root",
                str(root / "terminal-root"),
                "--peer",
                "alias:self",
                "--route",
                "native",
                "--seconds",
                "6",
                "--sample-every",
                "2",
                "--out",
                str(terminal_smoke),
                "--label",
                "terminal.smoke",
            ],
            duration_seconds=6,
            required_for="terminal.long-soak-runner",
            description="fast native elapsed runner rehearsal; not stable evidence",
            receipt=str(terminal_smoke),
        ),
        Stage(
            name="terminal.native-24h",
            surface="terminal",
            mode="long",
            command=[
                str(iotox),
                "terminal",
                "soak-run",
                "--root",
                str(root / "terminal-root"),
                "--peer",
                "alias:self",
                "--route",
                "native",
                "--seconds",
                str(terminal_seconds),
                "--sample-every",
                str(terminal_sample_every),
                "--out",
                str(terminal_receipt),
                "--label",
                "terminal.24h",
            ],
            duration_seconds=terminal_seconds,
            required_for="terminal.long-soak",
            description="native elapsed terminal receipt accepted by terminal soak-verify",
            receipt=str(terminal_receipt),
        ),
        Stage(
            name="person.background-smoke",
            surface="person",
            mode="smoke",
            command=[
                str(iotox),
                "person",
                "background-run",
                "--contacts",
                str(person_root / "contacts.store"),
                "--seen",
                str(person_root / "seen.store"),
                "--transcript",
                str(person_root / "transcript.store"),
                "--receipts",
                str(person_root / "receipts.store"),
                "--max-routes",
                "8",
                "--cycles",
                "3",
                "--interval",
                "0",
                "--expire-after",
                "60",
                "--dry-run",
            ],
            duration_seconds=None,
            required_for="person.background-delivery",
            description="native person worker status loop rehearsal; live send/retry is covered by Toxic bridge loops",
        ),
        Stage(
            name="person.background-24h",
            surface="person",
            mode="long",
            command=[
                str(iotox),
                "person",
                "background-run",
                "--contacts",
                str(person_root / "contacts.store"),
                "--seen",
                str(person_root / "seen.store"),
                "--transcript",
                str(person_root / "transcript.store"),
                "--receipts",
                str(person_root / "receipts.store"),
                "--max-routes",
                "16",
                "--cycles",
                str(person_cycles),
                "--interval",
                str(person_interval),
                "--expire-after",
                "604800",
            ],
            duration_seconds=person_cycles * person_interval,
            required_for="person.background-delivery",
            description="resident person messenger status-loop soak; pair with Toxic bridge loops for live send/retry/fanout",
        ),
        Stage(
            name="toxic.multidevice-default-loop",
            surface="toxic-bridge",
            mode="long",
            command=toxic_default_command,
            duration_seconds=toxic_seconds,
            required_for="toxic bridge default route",
            description="repeated live Toxic <-> three-device IoTox multidevice bridge proof; uses source-linked IoTox unless --iotox is forced",
            optional=True,
        ),
        Stage(
            name="toxic.multidevice-forced-tcp-loop",
            surface="toxic-bridge",
            mode="long",
            command=toxic_forced_tcp_command,
            duration_seconds=toxic_seconds,
            required_for="toxic bridge forced TCP route",
            description="repeated Toxic bridge proof through forced-TCP/native-relay mode; uses source-linked IoTox unless --iotox is forced",
            optional=True,
        ),
        Stage(
            name="service.reality-plan",
            surface="resident-service",
            mode="smoke",
            command=[
                str(iotox),
                "service",
                "status-plan",
                "--target",
                "all",
                "--root",
                str(service_root),
                "--manager",
                "systemd-user",
                "--unit-prefix",
                "iotox-soak",
                "--binary",
                str(iotox),
            ],
            duration_seconds=None,
            required_for="resident service reality",
            description="prints operator commands for actual active/enabled/log/health/upgrade receipt",
        ),
        Stage(
            name="person.graduation-blocked",
            surface="person",
            mode="smoke",
            command=[str(iotox), "person", "graduation-check", "--root", str(person_root)],
            duration_seconds=None,
            required_for="person readiness gate",
            description="must fail closed without evidence labels while printing exact next steps",
        ),
        Stage(
            name="bridge.graduation-blocked",
            surface="toxic-bridge",
            mode="smoke",
            command=[
                str(iotox),
                "person",
                "tox-bridge-graduation-check",
                "--root",
                str(person_root),
            ],
            duration_seconds=None,
            required_for="Toxic bridge readiness gate",
            description="must fail closed without bridge evidence while printing Toxic lab commands",
        ),
        Stage(
            name="routes.qualification-blocked",
            surface="route",
            mode="smoke",
            command=[str(iotox), "route-qualification-check", "--scope", "all"],
            duration_seconds=None,
            required_for="route claims",
            description="must fail closed without route labels and keep anonymity/fallback nonclaims explicit",
        ),
    ]


def print_plan(stages: list[Stage], *, as_json: bool) -> None:
    if as_json:
        print(json.dumps({"schema": SCHEMA, "stages": [asdict(stage) for stage in stages]}, indent=2, sort_keys=True))
        return
    print("iotox-massive-soak-plan-v1")
    print(f"schema={SCHEMA}")
    for stage in stages:
        print(f"stage={stage.name}")
        print(f"  surface={stage.surface}")
        print(f"  mode={stage.mode}")
        print(f"  required-for={stage.required_for}")
        if stage.duration_seconds is not None:
            print(f"  duration-seconds={stage.duration_seconds}")
        if stage.receipt:
            print(f"  receipt={stage.receipt}")
        if stage.optional:
            print("  optional=1")
        print(f"  description={stage.description}")
        print(f"  command={shell_join(stage.command)}")
    print("boundary=plan-only; launch-long records PIDs and logs; stop targets only recorded campaign children")


def preflight(args: argparse.Namespace) -> int:
    root = require_safe_root(args.root)
    ensure_private_dir(root)
    iotox = pathlib.Path(args.iotox).resolve() if args.iotox else default_iotox()
    results: list[StepResult] = []
    logs = root / "preflight"
    ensure_private_dir(logs)

    checks: list[tuple[str, list[str], set[int], float]] = [
        ("iotox.help", [str(iotox), "help"], {0}, 30.0),
        ("git.diff-check", ["git", "diff", "--check"], {0}, 60.0),
        ("sync.accepted-long-receipt", ["tools/iotox-repo.sh", "current-sync-long-soak-receipt", "--out", str(root / "preflight-sync-long-soak.json")], {0}, 120.0),
        ("sandwurm.script-present", ["test", "-x", "tools/iotox-sandwurm-lab.sh"], {0}, 10.0),
    ]
    if args.with_vm:
        checks.append(("sandwurm.preflight", ["tools/iotox-sandwurm-lab.sh", "preflight"], {0}, float(args.vm_preflight_timeout)))
    if args.with_toxic:
        checks.append(("toxic.resolvable", [sys.executable, str(repo_root() / "tools" / "run-toxic-compat-bridge-lab.py"), "--help"], {0}, 30.0))
        checks.append((
            "toxic.obtainable",
            [
                sys.executable,
                "-c",
                "import shutil, sys; sys.exit(0 if (shutil.which('toxic') or shutil.which('nix')) else 1)",
            ],
            {0},
            10.0,
        ))

    for index, (name, command, expected, timeout) in enumerate(checks, start=1):
        print(f"[preflight {index}/{len(checks)}] {name}", file=sys.stderr, flush=True)
        result = command_result(name, command, log=logs / f"{name}.log", expected=expected, timeout=timeout)
        results.append(result)
        print(
            f"  status={result.status} rc={result.returncode} log={result.log}",
            file=sys.stderr,
            flush=True,
        )
        if result.status != "passed" and not args.keep_going:
            break

    report = {
        "schema": SCHEMA,
        "kind": "preflight",
        "created_at": now_utc(),
        "root": str(root),
        "iotox": str(iotox),
        "results": [asdict(result) for result in results],
        "status": "passed" if all(result.status == "passed" for result in results) else "failed",
    }
    write_json(root / "preflight.json", report)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "passed" else 1


def smoke(args: argparse.Namespace) -> int:
    root = require_safe_root(args.root)
    ensure_private_dir(root)
    smoke_root = root / "smoke-runs" / run_id()
    ensure_private_dir(smoke_root)
    iotox = pathlib.Path(args.iotox).resolve() if args.iotox else default_iotox()
    stages = build_stages(
        iotox=iotox,
        root=smoke_root,
        terminal_seconds=DEFAULT_TERMINAL_SECONDS,
        terminal_sample_every=DEFAULT_TERMINAL_SAMPLE_EVERY,
        person_cycles=DEFAULT_PERSON_CYCLES,
        person_interval=DEFAULT_PERSON_INTERVAL,
        toxic_seconds=DEFAULT_TOXIC_SECONDS,
    )
    smoke_names = {
        "sync.current-long-receipt",
        "terminal.native-smoke",
        "person.background-smoke",
        "service.reality-plan",
        "person.graduation-blocked",
        "bridge.graduation-blocked",
        "routes.qualification-blocked",
    }
    if args.with_vm_smoke:
        smoke_names.add("sync.three-writer-smoke")
    selected = [stage for stage in stages if stage.name in smoke_names]
    logs = smoke_root / "logs"
    ensure_private_dir(logs)
    ensure_private_dir(smoke_root / "proof")
    ensure_private_dir(smoke_root / "person")
    ensure_private_dir(smoke_root / "service-root")

    expected = {
        "person.graduation-blocked": {4},
        "bridge.graduation-blocked": {4},
        "routes.qualification-blocked": {4},
    }
    timeouts = {
        "sync.three-writer-smoke": float(args.vm_smoke_timeout),
        "terminal.native-smoke": 30.0,
    }
    results: list[StepResult] = []
    for index, stage in enumerate(selected, start=1):
        print(f"[smoke {index}/{len(selected)}] {stage.name}", file=sys.stderr, flush=True)
        result = command_result(
            stage.name,
            stage.command,
            log=logs / f"{stage.name}.log",
            expected=expected.get(stage.name, {0}),
            timeout=timeouts.get(stage.name, 120.0),
        )
        results.append(result)
        print(
            f"  status={result.status} rc={result.returncode} log={result.log}",
            file=sys.stderr,
            flush=True,
        )
        if result.status != "passed" and not args.keep_going:
            break

    terminal_receipt = smoke_root / "proof" / "terminal-smoke.receipt"
    if terminal_receipt.exists():
        verify = command_result(
            "terminal.native-smoke-verify",
            [str(iotox), "terminal", "soak-verify", str(terminal_receipt), "--minimum-seconds", "6"],
            log=logs / "terminal.native-smoke-verify.log",
            expected={0},
            timeout=30.0,
        )
        results.append(verify)
        print(
            f"[smoke verify] status={verify.status} rc={verify.returncode} log={verify.log}",
            file=sys.stderr,
            flush=True,
        )

    report = {
        "schema": SCHEMA,
        "kind": "smoke",
        "created_at": now_utc(),
        "root": str(root),
        "smoke_root": str(smoke_root),
        "iotox": str(iotox),
        "results": [asdict(result) for result in results],
        "status": "passed" if all(result.status == "passed" for result in results) else "failed",
    }
    write_json(smoke_root / "smoke.json", report)
    write_json(root / "latest-smoke.json", report)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "passed" else 1


def launch_long(args: argparse.Namespace) -> int:
    root = require_safe_root(args.root)
    ensure_private_dir(root)
    campaign = root / run_id()
    ensure_private_dir(campaign)
    logs = campaign / "logs"
    ensure_private_dir(logs)
    ensure_private_dir(campaign / "proof")
    ensure_private_dir(campaign / "person")
    ensure_private_dir(campaign / "toxic")
    iotox = pathlib.Path(args.iotox).resolve() if args.iotox else default_iotox()
    include = set(args.include)
    toxic_iotox: pathlib.Path | None = None
    if args.iotox:
        toxic_iotox = pathlib.Path(args.iotox).resolve()
    elif "toxic" in include and not args.dry_run:
        print(
            "[launch-long] resolving source-linked IoTox binary for Toxic bridge loops...",
            file=sys.stderr,
            flush=True,
        )
        toxic_iotox = resolve_toxic_iotox(None)
        print(f"[launch-long] toxic-iotox={toxic_iotox}", file=sys.stderr, flush=True)

    stages = build_stages(
        iotox=iotox,
        toxic_iotox=toxic_iotox,
        root=campaign,
        terminal_seconds=args.terminal_seconds,
        terminal_sample_every=args.terminal_sample_every,
        person_cycles=args.person_cycles,
        person_interval=args.person_interval,
        toxic_seconds=args.toxic_seconds,
    )
    names_by_include = {
        "sync": {"sync.three-writer-24h"},
        "terminal": {"terminal.native-24h"},
        "person": {"person.background-24h"},
        "toxic": {"toxic.multidevice-default-loop", "toxic.multidevice-forced-tcp-loop"},
    }
    selected_names: set[str] = set()
    for item in include:
        selected_names.update(names_by_include[item])
    selected = [stage for stage in stages if stage.name in selected_names]
    if not selected:
        raise SoakError("no long stages selected")

    manifest: dict[str, Any] = {
        "schema": SCHEMA,
        "kind": "long-campaign",
        "created_at": now_utc(),
        "campaign": str(campaign),
        "iotox": str(iotox),
        "status": "planned" if args.dry_run else "running",
        "processes": [],
        "boundary": "only recorded PIDs are controlled by status/watch/stop",
    }
    if args.dry_run:
        manifest["processes"] = [
            {
                "stage": stage.name,
                "surface": stage.surface,
                "mode": stage.mode,
                "pid": None,
                "command": stage.command,
                "log": str(logs / f"{stage.name}.log"),
                "duration_seconds": stage.duration_seconds,
                "status": "dry-run",
            }
            for stage in selected
        ]
        write_json(campaign / MANIFEST, manifest)
        update_current(root, campaign)
        print(json.dumps(manifest, indent=2, sort_keys=True))
        return 0

    for stage in selected:
        log_path = logs / f"{stage.name}.log"
        log = log_path.open("ab")
        log.write(("$ " + shell_join(stage.command) + "\n").encode("utf-8"))
        log.flush()
        process = subprocess.Popen(
            stage.command,
            cwd=repo_root(),
            stdout=log,
            stderr=subprocess.STDOUT,
            env=command_env(),
            start_new_session=True,
        )
        manifest["processes"].append(
            {
                "stage": stage.name,
                "surface": stage.surface,
                "mode": stage.mode,
                "pid": process.pid,
                "command": stage.command,
                "log": str(log_path),
                "duration_seconds": stage.duration_seconds,
                "receipt": stage.receipt,
                "started_at": now_utc(),
                "status": "running",
            }
        )
        print(f"started stage={stage.name} pid={process.pid} log={log_path}", flush=True)
    write_json(campaign / MANIFEST, manifest)
    update_current(root, campaign)
    print(f"manifest={campaign / MANIFEST}")
    print(f"status-command={shell_join([sys.executable, str(repo_root() / 'tools' / 'run-massive-soak.py'), 'status', '--root', str(root)])}")
    print(f"watch-command={shell_join([sys.executable, str(repo_root() / 'tools' / 'run-massive-soak.py'), 'watch', '--root', str(root)])}")
    print(f"stop-command={shell_join([sys.executable, str(repo_root() / 'tools' / 'run-massive-soak.py'), 'stop', '--root', str(root)])}")
    return 0


def pid_status(pid: int) -> str:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return "exited"
    except PermissionError:
        return "unknown-permission"
    return "running"


def load_manifest(args: argparse.Namespace) -> tuple[pathlib.Path, dict[str, Any]]:
    root = require_safe_root(args.root)
    manifest_path = pathlib.Path(args.campaign).resolve() / MANIFEST if args.campaign else latest_manifest(root)
    if manifest_path is None or not manifest_path.is_file():
        raise SoakError(f"no campaign manifest found under {root}")
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    if data.get("schema") != SCHEMA:
        raise SoakError(f"unsupported campaign schema in {manifest_path}")
    return manifest_path, data


def log_text(path: pathlib.Path, limit: int = 256 * 1024) -> str:
    if not path.is_file():
        return ""
    size = path.stat().st_size
    with path.open("rb") as source:
        if size > limit:
            source.seek(size - limit)
        data = source.read(limit)
    return data.decode("utf-8", errors="replace")


def proof_root_from_log(text: str) -> pathlib.Path | None:
    for line in text.splitlines():
        if line.startswith("proof-root="):
            value = line.split("=", 1)[1].strip()
            if value:
                return pathlib.Path(value)
    return None


def argument_value(arguments: object, option: str) -> str | None:
    if not isinstance(arguments, list):
        return None
    values = [str(item) for item in arguments]
    try:
        index = values.index(option)
    except ValueError:
        return None
    if index + 1 >= len(values):
        return None
    return values[index + 1]


def infer_sync_three_writer_health(process: dict[str, Any], text: str) -> str:
    proof_root = proof_root_from_log(text)
    if proof_root is None:
        return "completed-unknown"
    process["sync_proof_root"] = str(proof_root)
    receipt = proof_root / "live/workspace-export/guest-receipts/iotox/sync-three-writer.json"
    live_chain = proof_root / "direct-cloud-hypervisor-live-chain.json"
    process["sync_receipt_present"] = receipt.is_file()
    process["sync_live_chain_present"] = live_chain.is_file()
    if receipt.is_file():
        process["sync_receipt_sha256"] = sha256_file(receipt)
    if not live_chain.is_file():
        return "completed-awaiting-live-chain"
    verify = subprocess.run(
        ["tools/iotox-sandwurm-lab.sh", "verify-three-writer", str(proof_root)],
        cwd=repo_root(),
        env=command_env(),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        timeout=120,
    )
    process["sync_verify_returncode"] = verify.returncode
    process["sync_verify_summary"] = "status=passed" if '"status": "passed"' in verify.stdout else "not-passed"
    return "completed-ok" if verify.returncode == 0 else "completed-failed"


def infer_toxic_loop_health(process: dict[str, Any], text: str) -> str:
    root_value = argument_value(process.get("command"), "--root")
    variant = argument_value(process.get("command"), "--variant")
    if root_value is None or variant is None:
        return "completed-failed" if " status=failed " in text else "completed-unknown"

    summary = pathlib.Path(root_value) / f"{variant}.summary.json"
    process["toxic_summary"] = str(summary)
    process["toxic_summary_present"] = summary.is_file()
    if not summary.is_file():
        return "completed-unknown"

    try:
        report = json.loads(summary.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        process["toxic_summary_error"] = "invalid-json"
        return "completed-failed"

    results = report.get("results", [])
    if not isinstance(results, list):
        results = []
    passed = sum(1 for result in results if isinstance(result, dict) and result.get("status") == "passed")
    failed = sum(1 for result in results if isinstance(result, dict) and result.get("status") == "failed")
    attempts = int(report.get("iterations") or len(results) or passed + failed)
    failures = int(report.get("failures") or failed)
    if failed != failures and failed > 0:
        failures = failed
    pass_rate = passed / attempts if attempts > 0 else 0.0
    process["toxic_summary_status"] = report.get("status", "unknown")
    process["toxic_iterations"] = attempts
    process["toxic_passed"] = passed
    process["toxic_failures"] = failures
    process["toxic_pass_rate"] = round(pass_rate, 6)
    process["toxic_first_iteration"] = report.get("first_iteration")
    process["toxic_last_iteration"] = report.get("last_iteration")

    if attempts <= 0:
        return "completed-unknown"
    if failures == 0 and passed > 0:
        return "completed-ok"
    if passed > 0 and failures > 0:
        return "completed-degraded"
    return "completed-failed"


def infer_process_health(process: dict[str, Any], manifest: dict[str, Any]) -> str:
    observed = process.get("observed_status")
    if process.get("status") == "dry-run":
        return "dry-run"
    if observed == "running":
        return "running"

    stage = str(process.get("stage", ""))
    text = log_text(pathlib.Path(str(process.get("log", ""))))
    lowered = text.lower()
    if stage.startswith("toxic.") and observed == "exited":
        return infer_toxic_loop_health(process, text)
    suspicious = any(
        marker in lowered
        for marker in (
            "[failed]",
            "traceback",
            "massive soak failed",
            " result=rejected",
            " status=failed",
            "accepted=0",
        )
    )
    if suspicious:
        return "completed-failed"

    receipt_value = process.get("receipt")
    if isinstance(receipt_value, str) and receipt_value:
        receipt = pathlib.Path(receipt_value)
        process["receipt_present"] = receipt.is_file()
        if receipt.is_file():
            process["receipt_sha256"] = sha256_file(receipt)
            if stage.startswith("terminal."):
                iotox = str(manifest.get("iotox", "iotox"))
                minimum = str(process.get("duration_seconds") or DEFAULT_TERMINAL_SECONDS)
                verify = subprocess.run(
                    [
                        iotox,
                        "terminal",
                        "soak-verify",
                        str(receipt),
                        "--minimum-seconds",
                        minimum,
                    ],
                    cwd=repo_root(),
                    env=command_env(),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    timeout=30,
                )
                process["receipt_verify_returncode"] = verify.returncode
                process["receipt_verify_summary"] = "accepted=1" if "accepted=1" in verify.stdout else "not-accepted"
                return "completed-ok" if verify.returncode == 0 else "completed-failed"
            return "completed-ok"
        return "completed-no-receipt"

    if stage.startswith("person.") and "boundary=bounded-native-scheduler-loop" in text:
        return "completed-ok"
    if stage == "sync.three-writer-24h" and observed == "exited":
        return infer_sync_three_writer_health(process, text)
    if stage.startswith("toxic.") and "status=passed" in lowered:
        return "completed-ok"
    if "result=accepted" in text or "status=passed" in lowered:
        return "completed-ok"
    if observed == "exited":
        return "completed-unknown"
    return "unknown"


def status(args: argparse.Namespace) -> int:
    manifest_path, data = load_manifest(args)
    processes = data.get("processes", [])
    live = 0
    healthy = 0
    for process in processes:
        pid = process.get("pid")
        process["observed_status"] = pid_status(int(pid)) if isinstance(pid, int) else process.get("status", "unknown")
        if process["observed_status"] == "running":
            live += 1
        log = pathlib.Path(process.get("log", ""))
        if log.is_file():
            process["log_bytes"] = log.stat().st_size
            process["log_sha256"] = sha256_file(log) if args.hash_logs else "not-requested"
        else:
            process["log_bytes"] = 0
            process["log_sha256"] = "absent"
        process["observed_health"] = infer_process_health(process, data)
        if process["observed_health"] in {"running", "completed-ok", "dry-run"}:
            healthy += 1
    data["observed_at"] = now_utc()
    data["observed_live_processes"] = live
    data["observed_status"] = "running" if live else "inactive"
    data["observed_healthy_processes"] = healthy
    data["observed_campaign_health"] = "ok" if healthy == len(processes) else "attention"
    if args.json:
        print(json.dumps(data, indent=2, sort_keys=True))
    else:
        print("iotox-massive-soak-status-v1")
        print(f"manifest={manifest_path}")
        print(f"campaign={data.get('campaign')}")
        print(f"observed-status={data['observed_status']}")
        print(f"observed-health={data['observed_campaign_health']}")
        print(f"live-processes={live}/{len(processes)}")
        for process in processes:
            extra = ""
            if str(process.get("stage", "")).startswith("toxic."):
                extra = (
                    f" toxic-passed={process.get('toxic_passed', 'unknown')}"
                    f" toxic-failures={process.get('toxic_failures', 'unknown')}"
                    f" toxic-pass-rate={process.get('toxic_pass_rate', 'unknown')}"
                )
            print(
                "process "
                f"stage={process.get('stage')} "
                f"pid={process.get('pid')} "
                f"status={process.get('observed_status')} "
                f"health={process.get('observed_health')} "
                f"log={process.get('log')} "
                f"log-bytes={process.get('log_bytes')}"
                f"{extra}"
            )
    return 0


def stop(args: argparse.Namespace) -> int:
    manifest_path, data = load_manifest(args)
    stopped = 0
    for process in data.get("processes", []):
        pid = process.get("pid")
        if not isinstance(pid, int):
            continue
        if pid_status(pid) != "running":
            process["stop_status"] = "not-running"
            continue
        try:
            os.killpg(pid, signal.SIGTERM)
            process["stop_status"] = "sigterm-sent"
            stopped += 1
        except ProcessLookupError:
            process["stop_status"] = "exited-before-stop"
        except PermissionError as exc:
            process["stop_status"] = f"permission-error:{exc}"
    data["stopped_at"] = now_utc()
    data["status"] = "stop-requested"
    write_json(manifest_path, data)
    print("iotox-massive-soak-stop-v1")
    print(f"manifest={manifest_path}")
    print(f"sigterm-sent={stopped}")
    return 0


def stage_catalog_for_campaign(manifest: dict[str, Any]) -> dict[str, Stage]:
    campaign = pathlib.Path(str(manifest.get("campaign", ""))).resolve()
    iotox = pathlib.Path(str(manifest.get("iotox", default_iotox()))).resolve()
    stages = build_stages(
        iotox=iotox,
        toxic_iotox=iotox,
        root=campaign,
        terminal_seconds=DEFAULT_TERMINAL_SECONDS,
        terminal_sample_every=DEFAULT_TERMINAL_SAMPLE_EVERY,
        person_cycles=DEFAULT_PERSON_CYCLES,
        person_interval=DEFAULT_PERSON_INTERVAL,
        toxic_seconds=DEFAULT_TOXIC_SECONDS,
    )
    return {stage.name: stage for stage in stages}


def command_value(command: list[str], option: str) -> str | None:
    return argument_value(command, option)


def archive_toxic_summary(command: list[str], stamp: str) -> str | None:
    root_value = command_value(command, "--root")
    variant = command_value(command, "--variant")
    if root_value is None or variant is None:
        return None
    summary = pathlib.Path(root_value) / f"{variant}.summary.json"
    if not summary.is_file():
        return None
    archived = summary.with_name(f"{summary.stem}.before-restart-{stamp}{summary.suffix}")
    summary.replace(archived)
    write_json(
        summary,
        {
            "schema": SCHEMA,
            "kind": "toxic-loop",
            "variant": variant,
            "created_at": now_utc(),
            "status": "restarted-running",
            "summary_archive": str(archived),
            "boundary": "previous terminal summary archived; final restarted summary will be written when toxic-loop exits",
        },
    )
    return str(archived)


def restart_stage(args: argparse.Namespace) -> int:
    manifest_path, data = load_manifest(args)
    catalog = stage_catalog_for_campaign(data)
    processes = data.get("processes", [])
    if not isinstance(processes, list):
        raise SoakError("campaign manifest has no process list")
    by_name = {str(process.get("stage")): process for process in processes if isinstance(process, dict)}
    campaign = pathlib.Path(str(data.get("campaign", ""))).resolve()
    logs = campaign / "logs"
    ensure_private_dir(logs)
    stamp = _dt.datetime.now(tz=_dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    restarted = 0

    for stage_name in args.stage:
        if stage_name not in catalog:
            raise SoakError(f"unknown restart stage: {stage_name}")
        process = by_name.get(stage_name)
        if process is None:
            raise SoakError(f"campaign does not contain stage: {stage_name}")
        pid = process.get("pid")
        observed = pid_status(int(pid)) if isinstance(pid, int) else str(process.get("status", "unknown"))
        if observed == "running":
            if not args.force:
                raise SoakError(f"stage is still running; use --force to restart it: {stage_name}")
            os.killpg(int(pid), signal.SIGTERM)
            process["forced_restart_stop_status"] = "sigterm-sent"

        stage = catalog[stage_name]
        log_path = logs / f"{stage.name}.restart-{stamp}.log"
        archived_summary = archive_toxic_summary(stage.command, stamp)
        log = log_path.open("ab")
        log.write(("$ " + shell_join(stage.command) + "\n").encode("utf-8"))
        log.flush()
        child = subprocess.Popen(
            stage.command,
            cwd=repo_root(),
            stdout=log,
            stderr=subprocess.STDOUT,
            env=command_env(),
            start_new_session=True,
        )
        history = process.setdefault("restart_history", [])
        if isinstance(history, list):
            history.append(
                {
                    "archived_at": now_utc(),
                    "observed_status": observed,
                    "pid": pid,
                    "command": process.get("command"),
                    "log": process.get("log"),
                    "status": process.get("status"),
                    "summary_archive": archived_summary,
                }
            )
        process.update(
            {
                "pid": child.pid,
                "command": stage.command,
                "log": str(log_path),
                "duration_seconds": stage.duration_seconds,
                "receipt": stage.receipt,
                "started_at": now_utc(),
                "status": "running",
                "restart_count": int(process.get("restart_count", 0) or 0) + 1,
                "restart_reason": args.reason,
            }
        )
        restarted += 1
        print(f"restarted stage={stage.name} pid={child.pid} log={log_path}", flush=True)

    data["status"] = "running"
    data["last_restarted_at"] = now_utc()
    write_json(manifest_path, data)
    print(f"manifest={manifest_path}")
    print(f"restarted={restarted}")
    return 0


def watch(args: argparse.Namespace) -> int:
    for sample in range(1, args.samples + 1):
        print(f"sample={sample}/{args.samples}", flush=True)
        rc = status(argparse.Namespace(root=args.root, campaign=args.campaign, json=False, hash_logs=False))
        if rc != 0:
            return rc
        if sample != args.samples:
            time.sleep(args.interval)
    return 0


def latest_toxic_iteration(root: pathlib.Path, variant: str) -> int:
    latest = 0
    for path in list(root.glob(f"{variant}.iter-*.log")) + list(root.glob(f"{variant}.iter-*")):
        suffix = path.name.removeprefix(f"{variant}.iter-")
        if suffix.endswith(".log"):
            suffix = suffix[:-4]
        try:
            latest = max(latest, int(suffix))
        except ValueError:
            continue
    return latest


def toxic_loop(args: argparse.Namespace) -> int:
    root = require_safe_root(args.root)
    ensure_private_dir(root)
    iotox = resolve_toxic_iotox(args.iotox)
    print(f"[toxic-loop] iotox={iotox}", flush=True)
    deadline = time.monotonic() + args.seconds
    start_iteration = latest_toxic_iteration(root, args.variant)
    iteration = start_iteration
    attempts = 0
    failures = 0
    passed = 0
    summary: list[dict[str, Any]] = []
    while time.monotonic() < deadline:
        iteration += 1
        attempts += 1
        lab = root / f"{args.variant}.iter-{iteration:04d}"
        command = [
            sys.executable,
            str(repo_root() / "tools" / "run-toxic-multidevice-bridge-lab.py"),
            "--iotox",
            str(iotox),
            "--lab",
            str(lab),
            "--run-ms",
            str(args.run_ms),
        ]
        if args.variant == "forced-tcp":
            command.append("--toxic-force-tcp")
        log = root / f"{args.variant}.iter-{iteration:04d}.log"
        result = command_result(
            f"toxic.{args.variant}.iter-{iteration:04d}",
            command,
            log=log,
            expected={0},
            timeout=args.iteration_timeout,
        )
        summary.append(asdict(result))
        if result.status == "passed":
            passed += 1
        print(
            f"iteration={iteration} variant={args.variant} status={result.status} rc={result.returncode} log={log}",
            flush=True,
        )
        if result.status != "passed":
            failures += 1
            if not args.keep_going:
                break
    if failures == 0:
        status_value = "passed"
    elif args.keep_going and passed > 0:
        status_value = "completed-with-failures"
    else:
        status_value = "failed"
    report = {
        "schema": SCHEMA,
        "kind": "toxic-loop",
        "variant": args.variant,
        "created_at": now_utc(),
        "seconds": args.seconds,
        "first_iteration": start_iteration + 1,
        "last_iteration": iteration,
        "iterations": attempts,
        "passed": passed,
        "failures": failures,
        "pass_rate": round(passed / attempts, 6) if attempts > 0 else 0.0,
        "results": summary,
        "status": status_value,
    }
    write_json(root / f"{args.variant}.summary.json", report)
    return 0 if failures == 0 else 1


def self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="iotox-massive-soak-self-test-") as raw:
        test_root = pathlib.Path(raw)
        iotox = pathlib.Path("/tmp/iotox")
        stages = build_stages(
            iotox=iotox,
            root=test_root,
            terminal_seconds=12,
            terminal_sample_every=3,
            person_cycles=2,
            person_interval=1,
            toxic_seconds=30,
        )
        names = {stage.name for stage in stages}
        required = {
            "sync.three-writer-24h",
            "terminal.native-24h",
            "person.background-24h",
            "toxic.multidevice-default-loop",
            "toxic.multidevice-forced-tcp-loop",
            "service.reality-plan",
            "person.graduation-blocked",
            "bridge.graduation-blocked",
            "routes.qualification-blocked",
        }
        if not required.issubset(names):
            missing = sorted(required - names)
            raise SoakError(f"plan is missing stages: {missing}")
        campaign = test_root / "run.selftest"
        ensure_private_dir(campaign)
        manifest = {
            "schema": SCHEMA,
            "kind": "long-campaign",
            "campaign": str(campaign),
            "processes": [
                {
                    "stage": "terminal.native-24h",
                    "pid": None,
                    "log": str(campaign / "terminal.log"),
                    "status": "dry-run",
                }
            ],
        }
        write_json(campaign / MANIFEST, manifest)
        loaded = json.loads((campaign / MANIFEST).read_text(encoding="utf-8"))
        if loaded["schema"] != SCHEMA or loaded["processes"][0]["stage"] != "terminal.native-24h":
            raise SoakError("manifest roundtrip failed")

        toxic_root = campaign / "toxic" / "default"
        ensure_private_dir(toxic_root)
        write_json(
            toxic_root / "default.summary.json",
            {
                "schema": SCHEMA,
                "kind": "toxic-loop",
                "variant": "default",
                "iterations": 3,
                "failures": 1,
                "results": [
                    {"status": "passed"},
                    {"status": "failed"},
                    {"status": "passed"},
                ],
                "status": "completed-with-failures",
            },
        )
        toxic_process = {
            "stage": "toxic.multidevice-default-loop",
            "observed_status": "exited",
            "command": [
                sys.executable,
                str(repo_root() / "tools" / "run-massive-soak.py"),
                "toxic-loop",
                "--root",
                str(toxic_root),
                "--variant",
                "default",
            ],
        }
        if infer_toxic_loop_health(toxic_process, "") != "completed-degraded":
            raise SoakError("mixed Toxic summary did not classify as degraded")
        if toxic_process.get("toxic_passed") != 2 or toxic_process.get("toxic_failures") != 1:
            raise SoakError("mixed Toxic summary counts were not retained")
    print("iotox-massive-soak-self-test=pass")
    return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="IoTox massive soak campaign runner")
    parser.add_argument("--self-test", action="store_true")
    sub = parser.add_subparsers(dest="command")

    plan_p = sub.add_parser("plan")
    plan_p.add_argument("--root", type=pathlib.Path, default=DEFAULT_ROOT)
    plan_p.add_argument("--iotox")
    plan_p.add_argument("--json", action="store_true")

    pre = sub.add_parser("preflight")
    pre.add_argument("--root", type=pathlib.Path, default=DEFAULT_ROOT)
    pre.add_argument("--iotox")
    pre.add_argument("--with-vm", action="store_true")
    pre.add_argument("--with-toxic", action="store_true")
    pre.add_argument("--vm-preflight-timeout", type=int, default=900)
    pre.add_argument("--keep-going", action="store_true")
    pre.add_argument("--json", action="store_true")

    sm = sub.add_parser("smoke")
    sm.add_argument("--root", type=pathlib.Path, default=DEFAULT_ROOT)
    sm.add_argument("--iotox")
    sm.add_argument("--with-vm-smoke", action="store_true")
    sm.add_argument("--vm-smoke-timeout", type=int, default=3_600)
    sm.add_argument("--keep-going", action="store_true")
    sm.add_argument("--json", action="store_true")

    launch = sub.add_parser("launch-long")
    launch.add_argument("--root", type=pathlib.Path, default=DEFAULT_ROOT)
    launch.add_argument("--iotox")
    launch.add_argument(
        "--include",
        action="append",
        choices=("sync", "terminal", "person", "toxic"),
        required=True,
        help="long surface to launch; repeat for multiple surfaces",
    )
    launch.add_argument("--terminal-seconds", type=int, default=DEFAULT_TERMINAL_SECONDS)
    launch.add_argument("--terminal-sample-every", type=int, default=DEFAULT_TERMINAL_SAMPLE_EVERY)
    launch.add_argument("--person-cycles", type=int, default=DEFAULT_PERSON_CYCLES)
    launch.add_argument("--person-interval", type=int, default=DEFAULT_PERSON_INTERVAL)
    launch.add_argument("--toxic-seconds", type=int, default=DEFAULT_TOXIC_SECONDS)
    launch.add_argument("--dry-run", action="store_true")

    st = sub.add_parser("status")
    st.add_argument("--root", type=pathlib.Path, default=DEFAULT_ROOT)
    st.add_argument("--campaign")
    st.add_argument("--json", action="store_true")
    st.add_argument("--hash-logs", action="store_true")

    wa = sub.add_parser("watch")
    wa.add_argument("--root", type=pathlib.Path, default=DEFAULT_ROOT)
    wa.add_argument("--campaign")
    wa.add_argument("--samples", type=int, default=3)
    wa.add_argument("--interval", type=int, default=60)

    sp = sub.add_parser("stop")
    sp.add_argument("--root", type=pathlib.Path, default=DEFAULT_ROOT)
    sp.add_argument("--campaign")

    rs = sub.add_parser("restart-stage")
    rs.add_argument("--root", type=pathlib.Path, default=DEFAULT_ROOT)
    rs.add_argument("--campaign")
    rs.add_argument(
        "--stage",
        action="append",
        choices=(
            "sync.three-writer-24h",
            "terminal.native-24h",
            "person.background-24h",
            "toxic.multidevice-default-loop",
            "toxic.multidevice-forced-tcp-loop",
        ),
        required=True,
        help="long campaign stage to restart in-place; repeat for multiple stages",
    )
    rs.add_argument("--force", action="store_true", help="SIGTERM a still-running recorded stage before restart")
    rs.add_argument("--reason", default="operator restart")

    loop = sub.add_parser("toxic-loop")
    loop.add_argument("--root", type=pathlib.Path, required=True)
    loop.add_argument(
        "--iotox",
        help="IoTox binary for Toxic labs; defaults to the source-linked package",
    )
    loop.add_argument("--seconds", type=int, default=DEFAULT_TOXIC_SECONDS)
    loop.add_argument("--variant", choices=("default", "forced-tcp"), required=True)
    loop.add_argument("--run-ms", type=int, default=1_200_000)
    loop.add_argument("--iteration-timeout", type=float, default=900.0)
    loop.add_argument("--keep-going", action="store_true")

    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        if args.self_test:
            return self_test()
        if args.command == "plan":
            root = require_safe_root(args.root)
            iotox = pathlib.Path(args.iotox).resolve() if args.iotox else default_iotox()
            print_plan(
                build_stages(
                    iotox=iotox,
                    toxic_iotox=pathlib.Path(args.iotox).resolve() if args.iotox else None,
                    root=root,
                    terminal_seconds=DEFAULT_TERMINAL_SECONDS,
                    terminal_sample_every=DEFAULT_TERMINAL_SAMPLE_EVERY,
                    person_cycles=DEFAULT_PERSON_CYCLES,
                    person_interval=DEFAULT_PERSON_INTERVAL,
                    toxic_seconds=DEFAULT_TOXIC_SECONDS,
                ),
                as_json=args.json,
            )
            return 0
        if args.command == "preflight":
            return preflight(args)
        if args.command == "smoke":
            return smoke(args)
        if args.command == "launch-long":
            return launch_long(args)
        if args.command == "status":
            return status(args)
        if args.command == "watch":
            return watch(args)
        if args.command == "stop":
            return stop(args)
        if args.command == "restart-stage":
            return restart_stage(args)
        if args.command == "toxic-loop":
            return toxic_loop(args)
        raise SoakError("choose a command or --self-test")
    except (SoakError, OSError, subprocess.SubprocessError, json.JSONDecodeError) as exc:
        print(f"massive soak failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
