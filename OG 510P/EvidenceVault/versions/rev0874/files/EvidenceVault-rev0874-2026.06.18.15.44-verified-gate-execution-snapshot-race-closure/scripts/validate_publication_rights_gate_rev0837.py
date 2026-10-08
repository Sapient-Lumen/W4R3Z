#!/usr/bin/env python3
"""Validate that package_release.py enforces the rights-readiness blocker."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_publication_rights_gate_audit_rev0837 import build, render_markdown  # noqa: E402


def fail(msg: str) -> None:
    print(f"publication-rights-gate-validate: FAIL: {msg}", file=sys.stderr)
    sys.exit(1)


def assert_no_transient_bytecode() -> None:
    offenders = []
    for path in ROOT.rglob("*"):
        if path.name == "__pycache__" or path.suffix == ".pyc":
            offenders.append(path.relative_to(ROOT).as_posix())
            if len(offenders) >= 5:
                break
    if offenders:
        fail("transient bytecode present before package-release refusal test: " + ", ".join(offenders))


def assert_package_release_refuses_fast() -> None:
    manifest = json.loads((ROOT / "RELEASE_MANIFEST.json").read_text(encoding="utf-8"))
    bundle_path = ROOT.parent / manifest.get("bundle", "")
    before_exists = bundle_path.exists()
    before_stat = bundle_path.stat() if before_exists else None
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONUNBUFFERED"] = "1"
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "package_release.py")],
        cwd=ROOT,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=30,
    )
    combined = (result.stdout or "") + (result.stderr or "")
    if result.returncode == 0:
        fail("package_release.py succeeded even though rights readiness says publication is blocked")
    if "publication rights gate blocked" not in combined:
        fail("package_release.py did not fail with the rights gate message")
    for forbidden in ("package-refresh:", "package-write:", "package-verify:", "package-artifact-verify:"):
        if forbidden in combined:
            fail(f"package_release.py reached {forbidden!r} despite rights blocker")
    after_exists = bundle_path.exists()
    if before_exists != after_exists:
        fail("package_release.py changed bundle presence during rights refusal test")
    if before_exists and before_stat is not None:
        after_stat = bundle_path.stat()
        if (after_stat.st_size, after_stat.st_mtime_ns) != (before_stat.st_size, before_stat.st_mtime_ns):
            fail("package_release.py changed existing bundle during rights refusal test")


def main() -> None:
    data = build(ROOT)
    json_path = ROOT / "AUDIT" / "PUBLICATION_RIGHTS_GATE_REV0837.json"
    md_path = ROOT / "AUDIT" / "PUBLICATION_RIGHTS_GATE_REV0837.md"
    if not json_path.is_file() or not md_path.is_file():
        fail("publication rights gate audit files are missing")
    actual = json.loads(json_path.read_text(encoding="utf-8"))
    if actual != data:
        fail("AUDIT/PUBLICATION_RIGHTS_GATE_REV0837.json is stale")
    if md_path.read_text(encoding="utf-8") != render_markdown(data):
        fail("AUDIT/PUBLICATION_RIGHTS_GATE_REV0837.md does not exactly mirror JSON audit output")
    if data["missing_required_snippets"]:
        fail("package_release.py missing rights guard snippets: " + ", ".join(data["missing_required_snippets"]))
    if not data["guard_call_precedes_package_refresh"]:
        fail("rights guard call must occur before package refresh")
    if not data["guard_function_precedes_zip_write"]:
        fail("rights guard must resolve through the shared helper before ZIP writer in package_release.py")
    if not data["current_tree_expected_to_refuse_package_release"]:
        fail("current tree is no longer rights-blocked; update/review this rev0837 refusal test")
    assert_no_transient_bytecode()
    assert_package_release_refuses_fast()
    assert_no_transient_bytecode()
    print("publication-rights-gate-validate: OK (package_release.py refuses rights-blocked ZIP emission through shared helper before refresh/write)")


if __name__ == "__main__":
    main()
