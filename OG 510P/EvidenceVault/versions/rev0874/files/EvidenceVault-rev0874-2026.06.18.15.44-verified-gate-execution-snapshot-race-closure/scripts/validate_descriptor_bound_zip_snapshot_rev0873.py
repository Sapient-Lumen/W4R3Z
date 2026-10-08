#!/usr/bin/env python3
"""Regression-test rev0873 descriptor-bound ZIP validation.

The test deterministically reproduces rev0872's final-path reopen defect, then
proves that rev0873 validates one retained descriptor snapshot and rejects both
pathname replacement and in-place byte mutation before returning success.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile
from types import ModuleType
import zipfile

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
CURRENT_SCRIPT = ROOT / "scripts" / "validate_zip_container.py"
CURRENT_PATCH = ROOT / "PATCHES" / "rev0872-to-rev0873-overlay.patch"
PARENT_SCRIPT_SHA256 = "bd06e3ecabc4a8a5eefed3960e53af2a29990e0cb405d4a705d1d1135901a0f5"


class ValidationFailure(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationFailure(message)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_module(path: Path, name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ValidationFailure(f"cannot load module from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def reconstruct_parent_script(temp: Path) -> Path:
    override = os.environ.get("EV_REV0872_ROOT")
    if override:
        candidate = Path(override) / "scripts" / "validate_zip_container.py"
        require(candidate.is_file(), f"EV_REV0872_ROOT lacks {candidate}")
        target = temp / "validate_zip_container_rev0872.py"
        shutil.copyfile(candidate, target)
    else:
        require(CURRENT_PATCH.is_file(), f"missing current overlay patch: {CURRENT_PATCH}")
        repo = temp / "parent-reconstruction"
        target = repo / "scripts" / "validate_zip_container.py"
        target.parent.mkdir(parents=True)
        shutil.copyfile(CURRENT_SCRIPT, target)
        completed = subprocess.run(
            [
                "git",
                "apply",
                "--reverse",
                "--include=scripts/validate_zip_container.py",
                os.fspath(CURRENT_PATCH),
            ],
            cwd=repo,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        )
        require(
            completed.returncode == 0,
            "cannot reconstruct exact rev0872 validator from current patch: "
            + completed.stderr.strip(),
        )
    require(
        sha256_file(target) == PARENT_SCRIPT_SHA256,
        "reconstructed rev0872 validator digest mismatch",
    )
    return target


def write_strict_zip(path: Path, payload: bytes) -> None:
    root_name = "bundle"
    directory = zipfile.ZipInfo(f"{root_name}/", date_time=(1980, 1, 1, 0, 0, 0))
    directory.create_system = 3
    directory.external_attr = (stat.S_IFDIR | 0o755) << 16
    directory.compress_type = zipfile.ZIP_STORED
    member = zipfile.ZipInfo(
        f"{root_name}/payload.txt", date_time=(1980, 1, 1, 0, 0, 0)
    )
    member.create_system = 3
    member.external_attr = (stat.S_IFREG | 0o644) << 16
    member.compress_type = zipfile.ZIP_DEFLATED
    with zipfile.ZipFile(path, "w", allowZip64=False) as archive:
        archive.writestr(directory, b"")
        archive.writestr(member, payload)


def validate_structural(module: ModuleType, path: Path) -> dict[str, object]:
    return module.validate_archive(
        path,
        expected_root="bundle",
        logical_archive_name="bundle.zip",
        require_overlay_manifest=False,
    )


def reproduce_parent_reopen_defect(parent: ModuleType, temp: Path) -> dict[str, object]:
    archive = temp / "bundle.zip"
    replacement = temp / "invalid-replacement.bin"
    write_strict_zip(archive, b"validated original payload\n")
    original_sha = sha256_file(archive)
    original_size = archive.stat().st_size
    replacement.write_bytes(b"this path no longer contains a ZIP\n")
    replacement_sha = sha256_file(replacement)

    original_hash_function = parent.sha256_file
    swap_count = 0

    def swap_before_parent_reopen(path: Path) -> str:
        nonlocal swap_count
        swap_count += 1
        os.replace(replacement, path)
        return original_hash_function(path)

    parent.sha256_file = swap_before_parent_reopen
    try:
        report = validate_structural(parent, archive)
    finally:
        parent.sha256_file = original_hash_function

    require(swap_count == 1, "parent race hook did not execute exactly once")
    require(report.get("status") == "zip_container_valid", "parent did not report success")
    require(report.get("archive_sha256") == replacement_sha, "parent digest did not bind replacement")
    require(report.get("archive_bytes") == original_size, "parent size was not retained from original")
    require(sha256_file(archive) == replacement_sha, "replacement is not at reported path")
    require(replacement_sha != original_sha, "test fixtures unexpectedly share a digest")
    try:
        zipfile.ZipFile(archive).close()
    except zipfile.BadZipFile:
        replacement_is_invalid_zip = True
    else:
        replacement_is_invalid_zip = False
    require(replacement_is_invalid_zip, "replacement fixture unexpectedly parses as ZIP")
    return {
        "parent_reported_valid": True,
        "validated_original_sha256": original_sha,
        "reported_replacement_sha256": replacement_sha,
        "reported_original_size": original_size,
        "replacement_is_invalid_zip": replacement_is_invalid_zip,
    }


def reject_current_path_replacement(current: ModuleType, temp: Path) -> str:
    archive = temp / "bundle.zip"
    replacement = temp / "invalid-replacement.bin"
    write_strict_zip(archive, b"descriptor-bound original payload\n")
    replacement.write_bytes(b"invalid replacement at the same pathname\n")

    original = current._sha256_fd
    calls = 0

    def swap_before_final_descriptor_hash(fd: int, expected_size: int) -> str:
        nonlocal calls
        calls += 1
        os.replace(replacement, archive)
        return original(fd, expected_size)

    current._sha256_fd = swap_before_final_descriptor_hash
    try:
        try:
            validate_structural(current, archive)
        except current.ZipContainerError as exc:
            message = str(exc)
        else:
            raise ValidationFailure("rev0873 accepted archive pathname replacement")
    finally:
        current._sha256_fd = original
    require(calls == 1, "current path-replacement hook did not execute exactly once")
    require(
        ("no longer names the validated inode" in message)
        or ("has no live filesystem link" in message),
        f"unexpected path-replacement rejection: {message}",
    )
    return message


def reject_current_in_place_mutation(current: ModuleType, temp: Path) -> str:
    archive = temp / "bundle.zip"
    write_strict_zip(archive, b"stable payload before mutation\n")

    original = current._sha256_fd
    calls = 0

    def mutate_before_final_descriptor_hash(fd: int, expected_size: int) -> str:
        nonlocal calls
        calls += 1
        with archive.open("r+b", buffering=0) as handle:
            first = handle.read(1)
            require(bool(first), "mutation fixture is empty")
            handle.seek(0)
            handle.write(bytes([first[0] ^ 0x01]))
            os.fsync(handle.fileno())
        return original(fd, expected_size)

    current._sha256_fd = mutate_before_final_descriptor_hash
    try:
        try:
            validate_structural(current, archive)
        except current.ZipContainerError as exc:
            message = str(exc)
        else:
            raise ValidationFailure("rev0873 accepted in-place archive mutation")
    finally:
        current._sha256_fd = original
    require(calls == 1, "current mutation hook did not execute exactly once")
    require(
        "bytes changed after the validated descriptor snapshot" in message,
        f"unexpected mutation rejection: {message}",
    )
    return message


def validate_inherited_rev0872_boundary() -> dict[str, object]:
    """Run every inherited rev0872 assertion against the current tree.

    rev0872's own main pins its manifest revision.  Later overlays instead call
    its assertions directly, then compare the unchanged coverage expectations
    and root-hardening block against the current manifest revision.
    """
    script = ROOT / "scripts" / "validate_root_anchor_path_identity_rev0872.py"
    require(script.is_file(), f"missing inherited validator: {script}")
    inherited = load_module(script, "ev_rev0872_root_boundary")
    for name in (
        "assert_parent_exploit_receipt",
        "assert_canonical_path_spelling",
        "assert_stable_root_happy_path",
        "assert_materialization_root_swap_rejected",
        "assert_existing_exact_root_swap_rejected",
        "assert_coverage_root_swap_rejected",
        "assert_external_target_anchor_survives_workflow_gap",
        "assert_root_symlink_rejected",
    ):
        getattr(inherited, name)()

    live, recoverable = inherited.coverage.compute_profiles(ROOT)
    for key, expected in inherited.EXPECTED_COVERAGE.items():
        require(live.get(key) == expected, f"inherited coverage mismatch for {key}")
    for key, expected in inherited.EXPECTED_RECOVERY.items():
        require(
            recoverable.get(key) == expected,
            f"inherited recovery mismatch for {key}",
        )
    manifest = json.loads((ROOT / "PATCH_BUNDLE_MANIFEST.json").read_text("utf-8"))
    require(manifest.get("overlay_revision") == "rev0873", "manifest is not rev0873")
    require(
        not inherited.coverage.compare_profile(
            live, manifest.get("representation_profile", {})
        ),
        "current representation profile is stale",
    )
    require(
        not inherited.coverage.compare_recovery_profile(
            recoverable, manifest.get("recovery_profile", {})
        ),
        "current recovery profile is stale",
    )
    hardening = manifest.get("root_anchor_path_identity_hardening")
    require(isinstance(hardening, dict), "inherited root hardening block is missing")
    require(hardening.get("parent_exploit_reproduced") is True, "root exploit receipt lost")
    require(hardening.get("current_swap_regressions_rejected") == 4, "root regressions lost")
    require(
        hardening.get("lexical_alias_spellings_rejected") == list(inherited.ALIASES),
        "strict inherited alias set changed",
    )

    inherited.assert_inherited_boundaries()
    inherited.assert_entrypoints_do_not_emit_bytecode()
    inherited.assert_no_transients()
    return {
        "status": "passed",
        "assertions": 13,
        "manifest_revision": manifest["overlay_revision"],
    }


def validate_current_happy_path(current: ModuleType, temp: Path) -> dict[str, object]:
    archive = temp / "bundle.zip"
    write_strict_zip(archive, b"stable descriptor snapshot payload\n")
    expected_sha = sha256_file(archive)
    report = validate_structural(current, archive)
    checks = report.get("source_container_checks")
    require(isinstance(checks, dict), "current report lacks source_container_checks")
    for key in (
        "descriptor_bound_source",
        "immutable_validation_snapshot",
        "source_bytes_equal_validated_snapshot_at_return",
        "source_path_still_names_opened_inode",
    ):
        require(checks.get(key) == "verified", f"current report does not verify {key}")
    require(report.get("archive_sha256") == expected_sha, "happy-path digest mismatch")
    return {
        "archive_sha256": expected_sha,
        "archive_bytes": archive.stat().st_size,
        "snapshot_checks": {key: checks[key] for key in checks if "source" in key or "snapshot" in key},
    }


def main() -> int:
    try:
        with tempfile.TemporaryDirectory(prefix="ev-rev0873-") as name:
            temp = Path(name)
            parent_script = reconstruct_parent_script(temp)
            parent = load_module(parent_script, "ev_rev0872_zip_validator")
            current = load_module(CURRENT_SCRIPT, "ev_rev0873_zip_validator")
            # Keep test fixtures isolated because the parent exploit replaces its path.
            (temp / "parent-case").mkdir()
            (temp / "replacement-case").mkdir()
            (temp / "mutation-case").mkdir()
            (temp / "happy-case").mkdir()
            parent_result = reproduce_parent_reopen_defect(parent, temp / "parent-case")
            replacement_message = reject_current_path_replacement(current, temp / "replacement-case")
            mutation_message = reject_current_in_place_mutation(current, temp / "mutation-case")
            happy = validate_current_happy_path(current, temp / "happy-case")
            inherited = validate_inherited_rev0872_boundary()
        report = {
            "status": "descriptor_bound_zip_snapshot_rev0873_valid",
            "parent_validator_sha256": PARENT_SCRIPT_SHA256,
            "parent_defect_reproduced": parent_result,
            "current_path_replacement_rejected": replacement_message,
            "current_in_place_mutation_rejected": mutation_message,
            "current_happy_path": happy,
            "inherited_rev0872_boundary": inherited,
        }
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0
    except (ValidationFailure, OSError, subprocess.SubprocessError) as exc:
        print(f"descriptor-bound-zip-snapshot-rev0873: FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
