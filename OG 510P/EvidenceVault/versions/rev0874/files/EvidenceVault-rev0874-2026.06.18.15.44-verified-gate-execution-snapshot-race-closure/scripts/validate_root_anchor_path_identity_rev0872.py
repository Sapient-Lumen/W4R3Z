#!/usr/bin/env python3
"""Validate rev0872 root-identity anchoring and canonical path spelling."""
from __future__ import annotations

import contextlib
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from typing import Any, Callable

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))
try:
    import apply_overlay_stack_rev0850 as apply_stack
    import canonical_coverage as coverage
    import overlay_gate
    import recover_indexed_files_from_patches as patch_recovery
    import recover_indexed_versions_from_overlay_history as history_recovery
    import root_anchor
    import safe_materialize as safe
finally:
    try:
        sys.path.remove(str(SCRIPTS))
    except ValueError:
        pass

EXPECTED_COVERAGE = {
    "canonical_index_files": 4586,
    "canonical_index_bytes": 106421990,
    "canonical_exact_files_present": 109,
    "canonical_exact_bytes_present": 4885540,
    "canonical_mismatched_files_present": 17,
    "canonical_missing_files": 4460,
    "canonical_source_files": 3476,
    "canonical_source_exact_files_present": 22,
}
EXPECTED_RECOVERY = {
    "canonical_index_files": 4586,
    "canonical_index_bytes": 106421990,
    "canonical_at_path_exact_files": 109,
    "canonical_at_path_exact_bytes": 4885540,
    "canonical_recovery_object_files": 16,
    "canonical_recovery_object_bytes": 88101,
    "canonical_rehydratable_files": 125,
    "canonical_rehydratable_bytes": 4973641,
    "canonical_unavailable_files": 4461,
    "canonical_unavailable_bytes": 101448349,
    "canonical_mismatched_files_recoverable": 16,
    "canonical_mismatched_files_unresolved": 1,
    "canonical_missing_files_recoverable": 0,
    "canonical_missing_files_unresolved": 4460,
    "canonical_source_files": 3476,
    "canonical_source_rehydratable_files": 22,
}
PARENT_HASHES = {
    "scripts/safe_materialize.py": "7b18bcd6fd3b50ebf7743e0035de9a4f9f59a7b70f77fadb250c6005be604404",
    "scripts/canonical_coverage.py": "cb88636c5d204d08c3e7f3ce7deaa526c42605c8e1fb15994899be86020745e0",
    "scripts/overlay_gate.py": "d193e1abef2eeb2622b6a3363b23fd265fc4113ed356ce66359a3460a37bfab3",
    "scripts/validate_overlay_bundle_integrity_rev0848.py": "e20c410582cb442de3fef36c056cb5b87e0ef87eb6e5f011551a2bac78779f77",
}
ALIASES = ("./a", "a//b", "a/./b", "a/b/")


class ValidationError(RuntimeError):
    pass


def fail(message: str) -> None:
    raise ValidationError(message)


def expect_error(call: Callable[[], Any], error_type: type[BaseException], phrase: str = "") -> str:
    try:
        call()
    except error_type as exc:
        text = str(exc)
        if phrase and phrase.lower() not in text.lower():
            fail(f"operation failed for the wrong reason: {text}")
        return text
    else:
        fail(f"unsafe operation unexpectedly succeeded; expected {error_type.__name__}")


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        fail(f"cannot load module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def assert_parent_exploit_receipt() -> None:
    path = ROOT / "AUDIT/ROOT_ANCHOR_PATH_IDENTITY_REV0872.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    receipt = data.get("parent_rev0871_exploit_reproduction")
    if not isinstance(receipt, dict):
        fail("parent exploit receipt is missing")
    if receipt.get("parent_revision") != "rev0871":
        fail("parent exploit receipt revision is stale")
    if receipt.get("parent_script_sha256") != PARENT_HASHES:
        fail("parent exploit receipt is not bound to the tested rev0871 code")
    expected = {
        "materialization_accepted_replacement_root": True,
        "replacement_root_received_write": True,
        "validated_original_received_write": False,
        "coverage_accepted_replacement_root": True,
        "coverage_read_replacement_bytes": True,
    }
    for key, value in expected.items():
        if receipt.get(key) is not value:
            fail(f"parent exploit receipt field is stale: {key}")
    aliases = receipt.get("path_aliases_accepted_and_normalized")
    if aliases != {
        "./a": "a",
        "a//b": "a/b",
        "a/./b": "a/b",
        "a/b/": "a/b",
    }:
        fail("parent path-alias receipt is stale")


def assert_canonical_path_spelling() -> None:
    if root_anchor.clean_relative_path("a/b", "test path") != "a/b":
        fail("canonical relative path was not preserved")
    if safe.clean_relative_path("a/b") != "a/b":
        fail("safe materializer rejected canonical spelling")
    if coverage.clean_rel_path("a/b", "test path") != "a/b":
        fail("coverage engine rejected canonical spelling")
    if overlay_gate._safe_rel("a/b", "test path") != "a/b":
        fail("overlay gate rejected canonical spelling")
    if apply_stack.clean_archive_path("a/a/b", "test path") != "a/b":
        fail("overlay-chain parser rejected canonical prefixed spelling")
    if patch_recovery.clean_relative_path("a/b", "test path") != "a/b":
        fail("patch-byte recovery parser rejected canonical spelling")
    if history_recovery.clean_rel("a/b", "test path") != "a/b":
        fail("history recovery parser rejected canonical spelling")

    integrity = _load_module(
        "ev_integrity_rev0872", SCRIPTS / "validate_overlay_bundle_integrity_rev0848.py"
    )
    if integrity.clean_archive_path("a/b", "test path") != "a/b":
        fail("overlay integrity validator rejected canonical spelling")

    for alias in ALIASES:
        expect_error(
            lambda alias=alias: root_anchor.clean_relative_path(alias, "test path"),
            root_anchor.RootAnchorError,
            "canonical spelling",
        )
        expect_error(
            lambda alias=alias: safe.clean_relative_path(alias),
            safe.MaterializationError,
            "canonical spelling",
        )
        expect_error(
            lambda alias=alias: coverage.clean_rel_path(alias, "test path"),
            coverage.CoverageError,
            "canonical spelling",
        )
        expect_error(
            lambda alias=alias: overlay_gate._safe_rel(alias, "test path"),
            overlay_gate.GateError,
            "canonical spelling",
        )
        expect_error(
            lambda alias=alias: apply_stack.clean_archive_path(
                f"a/{alias}", "test path"
            ),
            apply_stack.OverlayApplyError,
            "canonical spelling",
        )
        expect_error(
            lambda alias=alias: patch_recovery.clean_relative_path(alias, "test path"),
            patch_recovery.RecoveryError,
            "canonical spelling",
        )
        expect_error(
            lambda alias=alias: history_recovery.clean_rel(alias, "test path"),
            history_recovery.HistoryRecoveryError,
            "canonical spelling",
        )
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            try:
                integrity.clean_archive_path(alias, "test path")
            except SystemExit as exc:
                if exc.code != 1 or "canonical spelling" not in stderr.getvalue():
                    fail(f"overlay integrity rejected alias for the wrong reason: {alias!r}")
            else:
                fail(f"overlay integrity normalized path alias: {alias!r}")


def assert_stable_root_happy_path() -> None:
    with tempfile.TemporaryDirectory(prefix="ev-rev0872-stable-root-") as tmp_text:
        root = Path(tmp_text) / "root"
        root.mkdir()
        anchor = safe.prepare_root_anchor(root)
        data = b"stable anchored bytes\n"
        digest = hashlib.sha256(data).hexdigest()
        result = safe.materialize_exact_bytes(
            anchor, "nested/value.bin", data, expected_sha256=digest
        )
        if result.status != "written":
            fail("stable anchored materialization did not write")
        snap = coverage.snapshot_regular_file(
            anchor, "nested/value.bin", "stable anchored read", capture_bytes=True
        )
        if snap.get("bytes") != data or snap.get("sha256") != digest:
            fail("stable anchored coverage read returned different bytes")
        status = safe.target_status(
            anchor,
            "nested/value.bin",
            expected_size=len(data),
            expected_sha256=digest,
        )
        if status != "exact":
            fail("stable anchored target inspection was not exact")


def assert_materialization_root_swap_rejected() -> None:
    with tempfile.TemporaryDirectory(prefix="ev-rev0872-materialize-swap-") as tmp_text:
        base = Path(tmp_text)
        trusted = base / "trusted"
        replacement = base / "replacement"
        trusted.mkdir()
        replacement.mkdir()
        original_coerce = safe._coerce_root_anchor
        swapped = False

        def swap_after_capture(root):
            nonlocal swapped
            anchor = original_coerce(root)
            if not swapped:
                trusted.rename(base / "trusted-original")
                replacement.rename(trusted)
                swapped = True
            return anchor

        safe._coerce_root_anchor = swap_after_capture
        try:
            expect_error(
                lambda: safe.materialize_exact_bytes(
                    trusted, "redirected.txt", b"redirected\n"
                ),
                safe.MaterializationError,
                "no longer names",
            )
        finally:
            safe._coerce_root_anchor = original_coerce
        if (trusted / "redirected.txt").exists():
            fail("replacement root received a redirected materialization")
        if (base / "trusted-original" / "redirected.txt").exists():
            fail("failed root-swap operation left bytes in the original root")


def assert_existing_exact_root_swap_rejected() -> None:
    """An early already-exact return must still bind to the captured root."""
    with tempfile.TemporaryDirectory(prefix="ev-rev0872-existing-exact-swap-") as tmp_text:
        base = Path(tmp_text)
        trusted = base / "trusted"
        replacement = base / "replacement"
        trusted.mkdir()
        replacement.mkdir()
        data = b"already exact bytes\n"
        (trusted / "value.bin").write_bytes(data)
        (replacement / "value.bin").write_bytes(data)
        original_inspect = safe._inspect_at
        swapped = False

        def swap_after_exact(parent_fd, name, rel):
            nonlocal swapped
            result = original_inspect(parent_fd, name, rel)
            if not swapped and result[0] == "regular":
                trusted.rename(base / "trusted-original")
                replacement.rename(trusted)
                swapped = True
            return result

        safe._inspect_at = swap_after_exact
        try:
            expect_error(
                lambda: safe.materialize_exact_bytes(trusted, "value.bin", data),
                safe.MaterializationError,
                "no longer names",
            )
        finally:
            safe._inspect_at = original_inspect
        if (trusted / "value.bin").read_bytes() != data:
            fail("replacement exact target was altered during rejected root swap")
        if (base / "trusted-original" / "value.bin").read_bytes() != data:
            fail("original exact target was altered during rejected root swap")


def assert_coverage_root_swap_rejected() -> None:
    with tempfile.TemporaryDirectory(prefix="ev-rev0872-coverage-swap-") as tmp_text:
        base = Path(tmp_text)
        trusted = base / "trusted"
        replacement = base / "replacement"
        trusted.mkdir()
        replacement.mkdir()
        (trusted / "value.bin").write_bytes(b"trusted bytes\n")
        (replacement / "value.bin").write_bytes(b"replacement bytes\n")
        original_prepare = coverage._prepare_root_anchor
        swapped = False

        def swap_after_capture(root):
            nonlocal swapped
            anchor = original_prepare(root)
            if not swapped:
                trusted.rename(base / "trusted-original")
                replacement.rename(trusted)
                swapped = True
            return anchor

        coverage._prepare_root_anchor = swap_after_capture
        try:
            expect_error(
                lambda: coverage.snapshot_regular_file(
                    trusted, "value.bin", "root substitution test", capture_bytes=True
                ),
                coverage.CoverageError,
                "no longer names",
            )
        finally:
            coverage._prepare_root_anchor = original_prepare


def assert_external_target_anchor_survives_workflow_gap() -> None:
    with tempfile.TemporaryDirectory(prefix="ev-rev0872-external-anchor-") as tmp_text:
        base = Path(tmp_text)
        target = base / "target"
        replacement = base / "replacement"
        (target / "INDEX").mkdir(parents=True)
        replacement.mkdir()
        shutil.copyfile(ROOT / "INDEX/files.csv", target / "INDEX/files.csv")
        anchor = safe.prepare_external_target_root(target, bundle_root=ROOT)
        if not isinstance(anchor, root_anchor.RootAnchor):
            fail("external target preparation did not return a retained RootAnchor")
        target.rename(base / "target-original")
        replacement.rename(target)
        expect_error(
            lambda: safe.materialize_exact_bytes(anchor, "redirected.bin", b"bad"),
            safe.MaterializationError,
            "no longer names",
        )
        if (target / "redirected.bin").exists():
            fail("replacement external target received a redirected write")


def assert_root_symlink_rejected() -> None:
    if not hasattr(os, "symlink"):
        return
    with tempfile.TemporaryDirectory(prefix="ev-rev0872-root-alias-") as tmp_text:
        base = Path(tmp_text)
        real = base / "real"
        alias = base / "alias"
        real.mkdir()
        os.symlink(real, alias)
        expect_error(
            lambda: safe.prepare_root_anchor(alias), safe.MaterializationError, "symlink"
        )
        expect_error(
            lambda: coverage.snapshot_regular_file(alias, "missing", "root alias"),
            coverage.CoverageError,
            "symlink",
        )


def assert_live_profiles_and_manifest() -> None:
    live, recoverable = coverage.compute_profiles(ROOT)
    for key, expected in EXPECTED_COVERAGE.items():
        if live.get(key) != expected:
            fail(f"coverage mismatch for {key}: {live.get(key)!r} != {expected!r}")
    for key, expected in EXPECTED_RECOVERY.items():
        if recoverable.get(key) != expected:
            fail(f"recovery mismatch for {key}: {recoverable.get(key)!r} != {expected!r}")
    manifest = json.loads((ROOT / "PATCH_BUNDLE_MANIFEST.json").read_text(encoding="utf-8"))
    if manifest.get("overlay_revision") != "rev0872":
        fail("patch-bundle manifest is not rev0872")
    if coverage.compare_profile(live, manifest.get("representation_profile", {})):
        fail("manifest representation profile is stale")
    if coverage.compare_recovery_profile(recoverable, manifest.get("recovery_profile", {})):
        fail("manifest recovery profile is stale")
    hardening = manifest.get("root_anchor_path_identity_hardening")
    if not isinstance(hardening, dict):
        fail("manifest root-anchor hardening block is missing")
    if hardening.get("parent_exploit_reproduced") is not True:
        fail("manifest does not record the reproduced parent exploit")
    if hardening.get("current_swap_regressions_rejected") != 4:
        fail("manifest current swap regression count is stale")
    if hardening.get("lexical_alias_spellings_rejected") != list(ALIASES):
        fail("manifest alias rejection set is stale")


def assert_inherited_boundaries() -> None:
    inherited = _load_module(
        "ev_rev0871_validator",
        SCRIPTS / "validate_embedded_digest_recovery_safe_materialization_rev0871.py",
    )
    inherited.assert_exact_recoveries()
    inherited.assert_shared_writer_guards()
    inherited.assert_recovery_tools_share_boundary()
    inherited.assert_inherited_rev0870_boundaries()
    inherited.assert_remaining_boundaries()


def assert_entrypoints_do_not_emit_bytecode() -> None:
    """Local entrypoints must disable bytecode before importing shared modules."""
    cases = (
        ("apply_overlay_stack_rev0850.py", ("--help",), {0}),
        ("canonical_coverage.py", ("--help",), {0}),
        ("overlay_gate.py", ("--help",), {0}),
        ("safe_materialize.py", (), {0}),
        ("validate_overlay_bundle_integrity_rev0848.py", (), {1}),
        ("recover_indexed_files_from_patches.py", ("--help",), {0}),
        ("recover_indexed_versions_from_overlay_history.py", ("--help",), {0}),
        ("recover_indexed_low_entropy_constants_rev0870.py", ("--help",), {0}),
        ("recover_indexed_embedded_evidence_rev0871.py", ("--help",), {0}),
    )
    with tempfile.TemporaryDirectory(prefix="ev-rev0872-bytecode-boundary-") as tmp_text:
        sandbox = Path(tmp_text)
        scripts = sandbox / "scripts"
        scripts.mkdir()
        for source in SCRIPTS.glob("*.py"):
            shutil.copyfile(source, scripts / source.name)
        env = os.environ.copy()
        env.pop("PYTHONDONTWRITEBYTECODE", None)
        env.pop("PYTHONPYCACHEPREFIX", None)
        env["PYTHONNOUSERSITE"] = "1"
        for name, args, allowed_codes in cases:
            shutil.rmtree(scripts / "__pycache__", ignore_errors=True)
            for pyc in scripts.rglob("*.pyc"):
                pyc.unlink()
            result = subprocess.run(
                [sys.executable, str(scripts / name), *args],
                cwd=sandbox,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
            )
            if result.returncode not in allowed_codes:
                fail(
                    f"bytecode-boundary probe failed for {name}: "
                    f"exit={result.returncode}; stderr={result.stderr[-400:]}"
                )
            caches = [p.relative_to(sandbox).as_posix() for p in sandbox.rglob("__pycache__")]
            caches.extend(p.relative_to(sandbox).as_posix() for p in sandbox.rglob("*.pyc"))
            if caches:
                fail(f"entrypoint emitted Python bytecode before policy activation: {name}: {caches[:5]}")


def assert_no_transients() -> None:
    transients = [p.relative_to(ROOT).as_posix() for p in ROOT.rglob("__pycache__")]
    transients.extend(p.relative_to(ROOT).as_posix() for p in ROOT.rglob("*.pyc"))
    if transients:
        fail("transient Python cache paths are present: " + ", ".join(transients[:10]))


def main() -> int:
    try:
        assert_parent_exploit_receipt()
        assert_canonical_path_spelling()
        assert_stable_root_happy_path()
        assert_materialization_root_swap_rejected()
        assert_existing_exact_root_swap_rejected()
        assert_coverage_root_swap_rejected()
        assert_external_target_anchor_survives_workflow_gap()
        assert_root_symlink_rejected()
        assert_live_profiles_and_manifest()
        assert_inherited_boundaries()
        assert_entrypoints_do_not_emit_bytecode()
        assert_no_transients()
        print("root-anchor-path-identity-rev0872: OK")
        return 0
    except (
        ValidationError,
        coverage.CoverageError,
        safe.MaterializationError,
        root_anchor.RootAnchorError,
        OSError,
        ValueError,
    ) as exc:
        print(f"root-anchor-path-identity-rev0872: FAIL: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(
            f"root-anchor-path-identity-rev0872: FAIL: unexpected error: {exc}",
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
