#!/usr/bin/env python3
"""Prove rev0874 binds verified gate bytes to the bytes actually executed.

The regression reconstructs the exact rev0873 gate and deterministically makes
it pass preflight integrity, execute substituted validator bytes, restore the
original file, and pass postflight integrity.  It then runs the rev0874 gate
against the same source-path substitution pattern and proves that only the
private verified snapshot executes.  Interpreter isolation is also tested
against PYTHONPATH and an in-bundle stdlib-shadow module.
"""
from __future__ import annotations

# Run this validator under the same isolated/no-site boundary whether invoked
# directly or by the overlay gate.  This also keeps parent-module reconstruction
# from inheriting ambient Python startup state.
import os as _bootstrap_os
import sys as _bootstrap_sys

if not (_bootstrap_sys.flags.isolated and _bootstrap_sys.flags.no_site):
    _env = {
        key: value
        for key, value in _bootstrap_os.environ.items()
        if key
        not in {
            "PYTHONHOME",
            "PYTHONPATH",
            "PYTHONSTARTUP",
            "PYTHONINSPECT",
            "PYTHONUSERBASE",
        }
    }
    _env["PYTHONDONTWRITEBYTECODE"] = "1"
    _env["PYTHONNOUSERSITE"] = "1"
    _bootstrap_os.execve(
        _bootstrap_sys.executable,
        [
            _bootstrap_sys.executable,
            "-I",
            "-S",
            _bootstrap_os.path.abspath(__file__),
            *_bootstrap_sys.argv[1:],
        ],
        _env,
    )

import contextlib
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile
from types import ModuleType
from typing import Any, Iterator

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
CURRENT_SCRIPT = ROOT / "scripts" / "overlay_gate.py"
CURRENT_PATCH = ROOT / "PATCHES" / "rev0873-to-rev0874-overlay.patch"
PARENT_SCRIPT_SHA256 = "0cd99969c9bf47938af37b23649dcb3a91aeffaa83d73f3c8dc9c6e6bfb8245d"
ISOLATED_RUNNER = (
    "import runpy,sys;"
    "d=sys.argv[1];p=sys.argv[2];a=sys.argv[3:];"
    "sys.path.append(d);sys.argv=[p,*a];"
    "runpy.run_path(p,run_name='__main__')"
)


class ValidationFailure(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationFailure(message)


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def isolated_environment(extra: dict[str, str] | None = None) -> dict[str, str]:
    blocked = {
        "PYTHONHOME",
        "PYTHONPATH",
        "PYTHONSTARTUP",
        "PYTHONINSPECT",
        "PYTHONUSERBASE",
    }
    env = {key: value for key, value in os.environ.items() if key not in blocked}
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONNOUSERSITE"] = "1"
    if extra:
        env.update(extra)
    return env


def load_module(path: Path, name: str, prepend: Path | None = None) -> ModuleType:
    old_path = list(sys.path)
    if prepend is not None:
        sys.path.insert(0, os.fspath(prepend))
    try:
        spec = importlib.util.spec_from_file_location(name, path)
        if spec is None or spec.loader is None:
            raise ValidationFailure(f"cannot load module from {path}")
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
        return module
    finally:
        sys.path[:] = old_path


@contextlib.contextmanager
def argv_and_capture(arguments: list[str]) -> Iterator[tuple[io.StringIO, io.StringIO]]:
    original = list(sys.argv)
    stdout = io.StringIO()
    stderr = io.StringIO()
    sys.argv = arguments
    try:
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            yield stdout, stderr
    finally:
        sys.argv = original


def reconstruct_parent_gate(temp: Path) -> Path:
    root = temp / "reconstructed-parent"
    scripts = root / "scripts"
    scripts.mkdir(parents=True)
    target = scripts / "overlay_gate.py"
    override = os.environ.get("EV_REV0873_ROOT")
    if override:
        candidate = Path(override) / "scripts" / "overlay_gate.py"
        require(candidate.is_file(), f"EV_REV0873_ROOT lacks {candidate}")
        shutil.copyfile(candidate, target)
    else:
        require(CURRENT_PATCH.is_file(), f"missing current overlay patch: {CURRENT_PATCH}")
        shutil.copyfile(CURRENT_SCRIPT, target)
        completed = subprocess.run(
            [
                "git",
                "apply",
                "--reverse",
                "--include=scripts/overlay_gate.py",
                os.fspath(CURRENT_PATCH),
            ],
            cwd=root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=isolated_environment(),
            check=False,
        )
        require(
            completed.returncode == 0,
            "cannot reconstruct exact rev0873 gate from current patch: "
            + completed.stderr.strip(),
        )
    require(
        sha256_file(target) == PARENT_SCRIPT_SHA256,
        "reconstructed rev0873 overlay gate digest mismatch",
    )
    # The exact parent imports these two names at module startup.  Their behavior
    # is irrelevant to the synthetic race fixture because profile loaders are
    # replaced, but exact importability is retained.
    for name in ("canonical_coverage.py", "root_anchor.py"):
        shutil.copyfile(ROOT / "scripts" / name, scripts / name)
    return target


def fake_representation() -> dict[str, Any]:
    return {
        "canonical_index_files": 1,
        "canonical_index_bytes": 1,
        "canonical_exact_files_present": 1,
        "canonical_exact_bytes_present": 1,
        "canonical_mismatched_files_present": 0,
        "canonical_missing_files": 0,
        "canonical_source_files": 0,
        "canonical_source_exact_files_present": 0,
        "kind": "canonical_current_path_representation",
        "evidence": "AUDIT/evidence.json",
    }


def fake_recovery() -> dict[str, Any]:
    return {
        "canonical_index_files": 1,
        "canonical_index_bytes": 1,
        "canonical_at_path_exact_files": 1,
        "canonical_at_path_exact_bytes": 1,
        "canonical_recovery_object_files": 0,
        "canonical_recovery_object_bytes": 0,
        "canonical_rehydratable_files": 1,
        "canonical_rehydratable_bytes": 1,
        "canonical_unavailable_files": 0,
        "canonical_unavailable_bytes": 0,
        "canonical_mismatched_files_recoverable": 0,
        "canonical_mismatched_files_unresolved": 0,
        "canonical_missing_files_recoverable": 0,
        "canonical_missing_files_unresolved": 0,
        "canonical_source_files": 0,
        "canonical_source_rehydratable_files": 0,
        "kind": "canonical_recovery_availability",
        "recovery_inventory": "AUDIT/evidence.json",
        "recovery_inventory_sha256": "0" * 64,
        "evidence": "AUDIT/evidence.json",
    }


def reproduce_parent_verified_then_swapped_execution(parent_script: Path, temp: Path) -> dict[str, Any]:
    scripts = parent_script.parent
    target = scripts / "target.py"
    target_original = b"#!/usr/bin/env python3\nprint('legitimate-target')\n"
    target.write_bytes(target_original)
    os.chmod(target, 0o755)
    expected = sha256_bytes(target_original)
    integrity = scripts / "integrity.py"
    integrity.write_text(
        "#!/usr/bin/env python3\n"
        "import hashlib,pathlib,sys\n"
        "p=pathlib.Path(__file__).with_name('target.py')\n"
        f"sys.exit(0 if hashlib.sha256(p.read_bytes()).hexdigest()=={expected!r} else 1)\n",
        encoding="utf-8",
    )
    os.chmod(integrity, 0o755)
    marker = temp / "parent-substituted-code-executed.txt"
    malicious = (
        "#!/usr/bin/env python3\n"
        "from pathlib import Path\n"
        f"Path({os.fspath(marker)!r}).write_text('executed substituted bytes\\n',encoding='utf-8')\n"
        "print('substituted-target')\n"
    ).encode("utf-8")

    # Ensure the exact parent's unqualified imports bind its reconstructed helper
    # directory, not any helper already available from the current overlay.
    prior_helpers = {name: sys.modules.pop(name, None) for name in ("canonical_coverage", "root_anchor")}
    try:
        parent = load_module(parent_script, "ev_rev0873_overlay_gate_exact", scripts)
    finally:
        for name in ("canonical_coverage", "root_anchor"):
            sys.modules.pop(name, None)
        for name, module in prior_helpers.items():
            if module is not None:
                sys.modules[name] = module

    checks = [
        {
            "id": "overlay-integrity",
            "description": "hash target before and after work",
            "command": ["python3", "scripts/integrity.py"],
            "timeout_seconds": 30,
        },
        {
            "id": "target",
            "description": "synthetic gate target",
            "command": ["python3", "scripts/target.py"],
            "timeout_seconds": 30,
        },
    ]
    parent._load_manifest = lambda: {"project": "synthetic-parent", "overlay_revision": "rev0873", "archive_name": "synthetic.zip"}
    parent._load_representation_profile = lambda manifest: fake_representation()
    parent._load_recovery_profile = lambda manifest: fake_recovery()
    parent._load_checks = lambda manifest: checks
    original_run = parent._run_check
    swap_count = 0
    restore_count = 0

    def run_with_between_check_swap(check: dict[str, Any], timeout: int | None, phase: str) -> dict[str, Any]:
        nonlocal swap_count, restore_count
        result = original_run(check, timeout, phase)
        if check["id"] == "overlay-integrity" and phase == "preflight":
            require(result["status"] == "pass", "parent synthetic preflight did not pass")
            target.write_bytes(malicious)
            os.chmod(target, 0o755)
            swap_count += 1
        elif check["id"] == "target" and phase == "main":
            target.write_bytes(target_original)
            os.chmod(target, 0o755)
            restore_count += 1
        return result

    parent._run_check = run_with_between_check_swap
    try:
        with argv_and_capture([os.fspath(parent_script), "--check", "target", "--json"]) as (stdout, stderr):
            code = parent.main()
        require(code == 0, f"exact rev0873 gate did not falsely pass: {stderr.getvalue()}")
        report = json.loads(stdout.getvalue())
    finally:
        parent._run_check = original_run
        target.write_bytes(target_original)
        os.chmod(target, 0o755)
    require(report.get("status") == "pass", "rev0873 race report was not pass")
    require(report.get("overlay_integrity_status") == "pass", "rev0873 postflight did not pass")
    require(swap_count == 1 and restore_count == 1, "rev0873 swap fixture did not execute once")
    require(marker.is_file(), "rev0873 did not execute substituted source-path bytes")
    require(sha256_file(target) == expected, "rev0873 fixture did not restore original target")
    phases = [(row["id"], row["phase"], row["status"]) for row in report["results"]]
    require(
        phases == [
            ("overlay-integrity", "preflight", "pass"),
            ("target", "main", "pass"),
            ("overlay-integrity", "postflight", "pass"),
        ],
        f"unexpected rev0873 phase result: {phases}",
    )
    return {
        "parent_gate_sha256": PARENT_SCRIPT_SHA256,
        "preflight_passed": True,
        "substituted_bytes_executed": True,
        "original_bytes_restored": True,
        "postflight_passed": True,
        "gate_reported_pass": True,
    }


def write_synthetic_current_tree(root: Path, marker_root: Path) -> dict[str, Path]:
    scripts = root / "scripts"
    checks_dir = root / "CHECKS"
    audit = root / "AUDIT"
    scripts.mkdir(parents=True)
    checks_dir.mkdir()
    audit.mkdir()
    shutil.copyfile(CURRENT_SCRIPT, scripts / "overlay_gate.py")
    os.chmod(scripts / "overlay_gate.py", 0o755)

    legitimate_marker = marker_root / "legitimate-snapshot-code-executed.txt"
    poison_marker = marker_root / "pythonpath-poison-executed.txt"
    local_shadow_marker = marker_root / "local-hashlib-shadow-executed.txt"
    substituted_marker = marker_root / "current-source-substituted-code-executed.txt"

    coverage_script = f'''#!/usr/bin/env python3
import argparse,json
p=argparse.ArgumentParser();p.add_argument("--root");p.add_argument("--json",action="store_true");p.add_argument("--include-recovery",action="store_true");a=p.parse_args()
representation={fake_representation()!r}
recovery={fake_recovery()!r}
print(json.dumps(recovery if a.include_recovery else representation,sort_keys=True))
'''
    (scripts / "canonical_coverage.py").write_text(coverage_script, encoding="utf-8")
    (scripts / "integrity.py").write_text("#!/usr/bin/env python3\nprint('synthetic-integrity-pass')\n", encoding="utf-8")
    target_payload = (
        "#!/usr/bin/env python3\n"
        "import hashlib,os\n"
        "from pathlib import Path\n"
        "hashlib.sha256(b'stdlib-boundary').hexdigest()\n"
        f"Path({os.fspath(legitimate_marker)!r}).write_text('snapshot bytes executed\\n',encoding='utf-8')\n"
        "try:\n"
        "    import poisonprobe\n"
        "except ModuleNotFoundError:\n"
        "    pass\n"
        "else:\n"
        "    poisonprobe.touch()\n"
        "print('legitimate-snapshot-target')\n"
    )
    (scripts / "target.py").write_text(target_payload, encoding="utf-8")
    (scripts / "hashlib.py").write_text(
        "from pathlib import Path\n"
        f"Path({os.fspath(local_shadow_marker)!r}).write_text('shadow imported\\n',encoding='utf-8')\n"
        "raise RuntimeError('in-bundle hashlib shadow imported')\n",
        encoding="utf-8",
    )
    for path in scripts.glob("*.py"):
        os.chmod(path, 0o755)
    (audit / "evidence.json").write_text("{}\n", encoding="utf-8")

    manifest = {
        "project": "synthetic-current",
        "overlay_revision": "rev0874",
        "archive_name": "synthetic-current.zip",
        "representation_profile": fake_representation(),
        "recovery_profile": fake_recovery(),
        "gate_checks": [
            {
                "id": "overlay-integrity",
                "description": "synthetic integrity",
                "command": ["python3", "scripts/integrity.py"],
                "timeout_seconds": 30,
            },
            {
                "id": "target",
                "description": "synthetic target",
                "command": ["python3", "scripts/target.py"],
                "timeout_seconds": 30,
            },
        ],
    }
    (root / "PATCH_BUNDLE_MANIFEST.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    files: list[dict[str, Any]] = []
    excluded = {"CHECKS/overlay-manifest.json", "CHECKS/overlay-manifest.sha256"}
    for path in sorted(root.rglob("*")):
        if path.is_file():
            rel = path.relative_to(root).as_posix()
            if rel in excluded:
                continue
            payload = path.read_bytes()
            files.append({"path": rel, "bytes": len(payload), "sha256": sha256_bytes(payload)})
    inventory = {"created_at_utc": "2026-06-18T00:00:00Z", "file_count": len(files), "files": files}
    inventory_payload = (json.dumps(inventory, indent=2, sort_keys=True) + "\n").encode("utf-8")
    (checks_dir / "overlay-manifest.json").write_bytes(inventory_payload)
    inventory_sha = sha256_bytes(inventory_payload)
    (checks_dir / "overlay-manifest.sha256").write_text(
        f"{inventory_sha}  CHECKS/overlay-manifest.json\n", encoding="ascii"
    )
    return {
        "legitimate": legitimate_marker,
        "poison": poison_marker,
        "local_shadow": local_shadow_marker,
        "substituted": substituted_marker,
        "target": scripts / "target.py",
        "target_payload": Path(scripts / "target.py"),
    }


def test_current_cli_isolation(root: Path, markers: dict[str, Path], temp: Path) -> dict[str, Any]:
    poison_dir = temp / "pythonpath-poison"
    poison_dir.mkdir()
    (poison_dir / "poisonprobe.py").write_text(
        "from pathlib import Path\n"
        f"def touch(): Path({os.fspath(markers['poison'])!r}).write_text('poison imported\\n',encoding='utf-8')\n",
        encoding="utf-8",
    )
    env = isolated_environment(
        {
            # Deliberately reintroduce the hostile setting.  The gate must remove
            # it during bootstrap and for every child interpreter.
            "PYTHONPATH": os.fspath(poison_dir),
        }
    )
    completed = subprocess.run(
        [sys.executable, os.fspath(root / "scripts" / "overlay_gate.py"), "--check", "target", "--json"],
        cwd=root,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=60,
        check=False,
    )
    require(completed.returncode == 0, f"current isolated CLI failed: {completed.stderr}")
    report = json.loads(completed.stdout)
    require(report.get("status") == "pass", "current isolated CLI did not pass")
    execution = report.get("execution_snapshot", {})
    require(execution.get("isolated_python") is True, "current CLI did not declare isolated Python")
    require(execution.get("children_execute_source_paths") is False, "current CLI still executes source paths")
    require(execution.get("source_postflight") == "pass", "current CLI source postflight absent")
    require(execution.get("snapshot_postflight") == "pass", "current CLI snapshot postflight absent")
    require(markers["legitimate"].is_file(), "current CLI did not execute legitimate target")
    require(not markers["poison"].exists(), "PYTHONPATH poison module executed")
    require(not markers["local_shadow"].exists(), "in-bundle hashlib shadow executed")
    return {
        "bootstrap_reexec_isolated": True,
        "pythonpath_poison_ignored": True,
        "in_bundle_stdlib_shadow_ignored": True,
        "source_postflight": "pass",
        "snapshot_postflight": "pass",
    }


def test_current_source_swap_uses_snapshot(root: Path, markers: dict[str, Path]) -> dict[str, Any]:
    current_script = root / "scripts" / "overlay_gate.py"
    current = load_module(current_script, "ev_rev0874_overlay_gate_synthetic")
    target = markers["target"]
    original_payload = target.read_bytes()
    original_mode = stat.S_IMODE(target.stat().st_mode)
    malicious = (
        "#!/usr/bin/env python3\n"
        "from pathlib import Path\n"
        f"Path({os.fspath(markers['substituted'])!r}).write_text('source substitution executed\\n',encoding='utf-8')\n"
        "print('malicious-source-target')\n"
    ).encode("utf-8")
    original_run = current._run_check
    swap_count = 0
    restore_count = 0

    def run_with_source_swap(
        check: dict[str, Any], execution_root: Path, timeout: int | None, phase: str
    ) -> dict[str, Any]:
        nonlocal swap_count, restore_count
        result = original_run(check, execution_root, timeout, phase)
        if check["id"] == "overlay-integrity" and phase == "preflight":
            require(result["status"] == "pass", "current synthetic preflight did not pass")
            target.write_bytes(malicious)
            os.chmod(target, original_mode)
            swap_count += 1
        elif check["id"] == "target" and phase == "main":
            target.write_bytes(original_payload)
            os.chmod(target, original_mode)
            restore_count += 1
        return result

    current._run_check = run_with_source_swap
    markers["legitimate"].unlink(missing_ok=True)
    markers["substituted"].unlink(missing_ok=True)
    try:
        with argv_and_capture([os.fspath(current_script), "--check", "target", "--json"]) as (stdout, stderr):
            code = current.main()
        require(code == 0, f"current source-swap case failed: {stderr.getvalue()}")
        report = json.loads(stdout.getvalue())
    finally:
        current._run_check = original_run
        target.write_bytes(original_payload)
        os.chmod(target, original_mode)
    require(report.get("status") == "pass", "current source-swap report did not pass")
    require(swap_count == 1 and restore_count == 1, "current source-swap fixture count mismatch")
    require(markers["legitimate"].is_file(), "verified snapshot target did not execute")
    require(not markers["substituted"].exists(), "current gate executed substituted source bytes")
    require(target.read_bytes() == original_payload, "current source target was not restored")
    require(
        all(row.get("execution_root") == "verified_private_snapshot" for row in report["results"]),
        "current result contains a source-path execution",
    )
    execution = report.get("execution_snapshot", {})
    require(execution.get("source_postflight") == "pass", "current source postflight absent")
    require(execution.get("snapshot_postflight") == "pass", "current snapshot postflight absent")
    return {
        "source_substitution_attempted": True,
        "substituted_source_bytes_executed": False,
        "verified_snapshot_bytes_executed": True,
        "all_result_execution_roots": "verified_private_snapshot",
        "source_postflight": "pass",
        "snapshot_postflight": "pass",
    }


def validate_inherited_rev0873() -> dict[str, Any]:
    """Run rev0873's transport-snapshot assertions without replaying old suites."""
    script = ROOT / "scripts" / "validate_descriptor_bound_zip_snapshot_rev0873.py"
    require(script.is_file(), f"missing inherited validator: {script}")
    inherited = load_module(script, "ev_rev0873_descriptor_snapshot_assertions")
    with tempfile.TemporaryDirectory(prefix="ev-rev0873-focused-") as name:
        temp = Path(name)
        parent_script = inherited.reconstruct_parent_script(temp)
        parent = inherited.load_module(parent_script, "ev_rev0872_zip_validator_focused")
        current = inherited.load_module(inherited.CURRENT_SCRIPT, "ev_rev0873_zip_validator_focused")
        for directory in ("parent-case", "replacement-case", "mutation-case", "happy-case"):
            (temp / directory).mkdir()
        parent_result = inherited.reproduce_parent_reopen_defect(parent, temp / "parent-case")
        replacement_message = inherited.reject_current_path_replacement(current, temp / "replacement-case")
        mutation_message = inherited.reject_current_in_place_mutation(current, temp / "mutation-case")
        happy = inherited.validate_current_happy_path(current, temp / "happy-case")
    require(parent_result.get("parent_reported_valid") is True, "rev0873 parent exploit receipt was not reproduced")
    require(bool(replacement_message), "rev0873 path-replacement rejection was not retained")
    require(bool(mutation_message), "rev0873 in-place mutation rejection was not retained")
    require(happy.get("snapshot_checks"), "rev0873 happy-path snapshot checks are absent")
    return {
        "status": "passed",
        "validator": "scripts/validate_descriptor_bound_zip_snapshot_rev0873.py",
        "focused_assertions": 4,
        "parent_defect_retained": True,
        "current_path_replacement_rejected": True,
        "current_in_place_mutation_rejected": True,
        "current_happy_path_snapshot_checks": len(happy["snapshot_checks"]),
    }


def assert_no_bytecode() -> None:
    transients = [
        path.relative_to(ROOT).as_posix()
        for path in ROOT.rglob("*")
        if path.name == "__pycache__" or path.suffix in {".pyc", ".pyo"}
    ]
    require(not transients, f"validation left Python bytecode/transients: {transients[:10]}")


def main() -> int:
    try:
        require(CURRENT_SCRIPT.is_file(), f"missing current gate: {CURRENT_SCRIPT}")
        with tempfile.TemporaryDirectory(prefix="ev-rev0874-gate-") as name:
            temp = Path(name)
            parent_script = reconstruct_parent_gate(temp)
            parent_result = reproduce_parent_verified_then_swapped_execution(parent_script, temp)

            current_root = temp / "synthetic-current"
            marker_root = temp / "markers"
            marker_root.mkdir()
            markers = write_synthetic_current_tree(current_root, marker_root)
            isolation_result = test_current_cli_isolation(current_root, markers, temp)
            current_result = test_current_source_swap_uses_snapshot(current_root, markers)

        inherited = validate_inherited_rev0873()
        assert_no_bytecode()
        report = {
            "status": "verified_gate_execution_snapshot_rev0874_valid",
            "parent_revision": "rev0873",
            "parent_gate_sha256": PARENT_SCRIPT_SHA256,
            "parent_verified_then_swapped_false_success": parent_result,
            "current_source_swap_regression": current_result,
            "current_interpreter_isolation": isolation_result,
            "inherited_descriptor_bound_zip_validation": inherited,
            "canonical_bytes_admitted": 0,
        }
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0
    except (ValidationFailure, OSError, subprocess.SubprocessError, json.JSONDecodeError) as exc:
        print(f"verified-gate-execution-snapshot-rev0874: FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
