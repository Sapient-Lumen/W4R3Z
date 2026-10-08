#!/usr/bin/env python3
"""Validate the rev0850 guarded overlay-stack application harness."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import apply_overlay_stack_rev0850 as overlay  # noqa: E402

REQUIRED_SNIPPETS = [
    "CANONICAL_HANDOFF_REVISION = 840",
    "missing handoff patch prevents a full canonical application pass",
    "validate_patch_payload",
    "git apply",
    "target root contains symlink paths",
]


def fail(message: str) -> None:
    print(f"overlay-stack-application-harness-rev0850: FAIL: {message}", file=sys.stderr)
    sys.exit(1)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def assert_static_contract() -> None:
    text = (ROOT / "scripts" / "apply_overlay_stack_rev0850.py").read_text(encoding="utf-8")
    missing = [snippet for snippet in REQUIRED_SNIPPETS if snippet not in text]
    if missing:
        fail("missing required snippets: " + ", ".join(missing))


def assert_current_bundle_chain_is_continuous() -> None:
    expected_end = overlay.infer_current_revision(ROOT) or 850
    result = overlay.discover_overlay_chain(ROOT, expected_start_rev=840, expected_end_rev=expected_end)
    minimum_patch_count = expected_end - 840
    if result.get("patch_count", 0) < minimum_patch_count:
        fail(f"expected seed plus carried-forward overlay patches through rev{expected_end:04d}, got {result}")
    ordered = result.get("ordered_patch_paths", [])
    if ordered[0] != "PATCHES/rev0840-to-rev0841-overlay.patch":
        fail(f"overlay chain does not begin with the recovered seed patch: {ordered[:3]}")
    expected_last = f"PATCHES/rev{expected_end - 1:04d}-to-rev{expected_end:04d}-overlay.patch"
    if ordered[-1] != expected_last:
        fail(f"overlay chain does not end with the current rev{expected_end:04d} patch: {ordered[-3:]}")


def assert_cli_check_only_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/apply_overlay_stack_rev0850.py",
            "--bundle-root",
            str(ROOT),
            "--expected-end-rev",
            str(overlay.infer_current_revision(ROOT) or 850),
            "--json",
        ],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        fail(f"check-only CLI failed: stdout={result.stdout!r} stderr={result.stderr!r}")
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        fail(f"check-only CLI did not emit JSON: {exc}: {result.stdout!r}")
    if payload.get("status") != "overlay_chain_ready" or payload.get("expected_start_revision") != "rev0840":
        fail(f"unexpected check-only payload: {payload}")


def assert_patch_path_traversal_is_rejected() -> None:
    with tempfile.TemporaryDirectory(prefix="ev-rev0850-bad-patch-") as tmp:
        path = Path(tmp) / "rev0001-to-rev0002-overlay.patch"
        write(
            path,
            "diff --git a/good.txt b/../escape.txt\n"
            "--- a/good.txt\n"
            "+++ b/../escape.txt\n"
            "@@ -1 +1 @@\n"
            "-old\n"
            "+new\n",
        )
        try:
            overlay.validate_patch_payload(path)
        except overlay.OverlayApplyError as exc:
            if "escapes" not in str(exc) and "relative" not in str(exc):
                fail(f"path traversal rejection had unexpected message: {exc}")
        else:
            fail("path-traversing patch payload was accepted")


def assert_synthetic_chain_dry_run_and_apply() -> None:
    with tempfile.TemporaryDirectory(prefix="ev-rev0850-synthetic-chain-") as tmp:
        base = Path(tmp)
        bundle = base / "EvidenceVault-rev0003-synthetic"
        patches = bundle / "PATCHES"
        patches.mkdir(parents=True)
        target = base / "target"
        target.mkdir()
        write(target / "alpha.txt", "old\n")
        write(
            patches / "rev0001-to-rev0002-overlay.patch",
            "diff --git a/alpha.txt b/alpha.txt\n"
            "index 3e75765..b6fc4c6 100644\n"
            "--- a/alpha.txt\n"
            "+++ b/alpha.txt\n"
            "@@ -1 +1 @@\n"
            "-old\n"
            "+middle\n",
        )
        write(
            patches / "rev0002-to-rev0003-overlay.patch",
            "diff --git a/beta.txt b/beta.txt\n"
            "new file mode 100644\n"
            "index 0000000..b66ba06\n"
            "--- /dev/null\n"
            "+++ b/beta.txt\n"
            "@@ -0,0 +1 @@\n"
            "+added\n",
        )
        dry = overlay.apply_patch_chain(bundle, target, apply=False, expected_start_rev=1, expected_end_rev=3)
        if dry.get("status") != "overlay_chain_dry_run_ok":
            fail(f"synthetic dry run returned unexpected payload: {dry}")
        if (target / "alpha.txt").read_text(encoding="utf-8") != "old\n" or (target / "beta.txt").exists():
            fail("dry run mutated the target root")
        applied = overlay.apply_patch_chain(bundle, target, apply=True, expected_start_rev=1, expected_end_rev=3)
        if applied.get("status") != "overlay_chain_applied":
            fail(f"synthetic apply returned unexpected payload: {applied}")
        if (target / "alpha.txt").read_text(encoding="utf-8") != "middle\n":
            fail("synthetic apply did not update alpha.txt")
        if (target / "beta.txt").read_text(encoding="utf-8") != "added\n":
            fail("synthetic apply did not add beta.txt")


def main() -> int:
    assert_static_contract()
    assert_current_bundle_chain_is_continuous()
    assert_cli_check_only_json()
    assert_patch_path_traversal_is_rejected()
    assert_synthetic_chain_dry_run_and_apply()
    print("overlay-stack-application-harness-rev0850: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
