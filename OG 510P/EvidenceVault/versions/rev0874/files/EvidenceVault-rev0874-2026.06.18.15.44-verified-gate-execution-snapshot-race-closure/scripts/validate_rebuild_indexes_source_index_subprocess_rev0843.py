#!/usr/bin/env python3
"""Validate rev0843 SOURCE_INDEX subprocess handoff in rebuild_indexes.py."""
from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "rebuild_indexes.py"


REQUIRED_SNIPPETS = [
    "def refresh_source_index_subprocess()",
    'run_material_builder_subprocess("build_source_index")',
    "_require_json_object(source_json, \"build_source_index.py\")",
    'source_md = ROOT / "SOURCE_INDEX.md"',
    'raise RuntimeError("build_source_index.py emitted empty SOURCE_INDEX.json")',
]
FORBIDDEN_SNIPPETS = [
    "from build_source_index import build_source_index",
    "from build_source_index import render_markdown",
    "data = build_source_index()",
    "render_markdown(data)",
]


def fail(msg: str) -> None:
    print(f"rebuild-indexes-source-index-subprocess-rev0843: FAIL: {msg}", file=sys.stderr)
    sys.exit(1)


def assert_static_contract() -> None:
    text = SCRIPT.read_text(encoding="utf-8")
    missing = [snippet for snippet in REQUIRED_SNIPPETS if snippet not in text]
    forbidden = [snippet for snippet in FORBIDDEN_SNIPPETS if snippet in text]
    if missing:
        fail("missing required snippets: " + ", ".join(missing))
    if forbidden:
        fail("forbidden in-process snippets present: " + ", ".join(forbidden))


def import_fixture_rebuild_indexes(root: Path):
    module_path = root / "scripts" / "rebuild_indexes.py"
    spec = importlib.util.spec_from_file_location("fixture_rebuild_indexes", module_path)
    if spec is None or spec.loader is None:
        fail("could not import fixture rebuild_indexes.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_fixture(root: Path, builder_body: str) -> None:
    (root / "scripts").mkdir(parents=True, exist_ok=True)
    shutil.copy2(SCRIPT, root / "scripts" / "rebuild_indexes.py")
    (root / "scripts" / "build_source_index.py").write_text(builder_body, encoding="utf-8")


def assert_no_bytecode(root: Path) -> None:
    offenders = [path.relative_to(root).as_posix() for path in root.rglob("*") if path.name == "__pycache__" or path.suffix == ".pyc"]
    if offenders:
        fail("fixture emitted bytecode: " + ", ".join(offenders[:10]))


def probe_successful_json_handoff() -> None:
    with tempfile.TemporaryDirectory(prefix="ev-rev0843-source-index-ok-") as tmp:
        root = Path(tmp) / "EvidenceVault-fixture"
        builder = '''#!/usr/bin/env python3\nimport json\nfrom pathlib import Path\nROOT = Path(__file__).resolve().parents[1]\n(ROOT / "SOURCE_INDEX.json").write_text(json.dumps({"version": 1, "probe": "source-index-subprocess"}, indent=2) + "\\n", encoding="utf-8")\n(ROOT / "SOURCE_INDEX.md").write_text("# Source index\\n\\nfixture\\n", encoding="utf-8")\nprint("build-source-index-fixture: OK")\n'''
        write_fixture(root, builder)
        module = import_fixture_rebuild_indexes(root)
        module.refresh_source_index_subprocess()
        data = json.loads((root / "SOURCE_INDEX.json").read_text(encoding="utf-8"))
        if data.get("probe") != "source-index-subprocess":
            fail("fixture SOURCE_INDEX.json was not produced by child builder")
        if not (root / "SOURCE_INDEX.md").read_text(encoding="utf-8").startswith("# Source index"):
            fail("fixture SOURCE_INDEX.md was not produced by child builder")
        assert_no_bytecode(root)


def probe_builder_failure_is_reported() -> None:
    with tempfile.TemporaryDirectory(prefix="ev-rev0843-source-index-fail-") as tmp:
        root = Path(tmp) / "EvidenceVault-fixture"
        builder = '''#!/usr/bin/env python3\nimport sys\nprint("intentional fixture failure")\nsys.exit(7)\n'''
        write_fixture(root, builder)
        module = import_fixture_rebuild_indexes(root)
        try:
            module.refresh_source_index_subprocess()
        except RuntimeError as exc:
            if "returned non-zero status 7" not in str(exc):
                fail(f"unexpected failure message for builder nonzero: {exc}")
        else:
            fail("builder non-zero exit did not fail refresh_source_index_subprocess()")
        assert_no_bytecode(root)


def probe_empty_json_fails_closed() -> None:
    with tempfile.TemporaryDirectory(prefix="ev-rev0843-source-index-empty-") as tmp:
        root = Path(tmp) / "EvidenceVault-fixture"
        builder = '''#!/usr/bin/env python3\nfrom pathlib import Path\nROOT = Path(__file__).resolve().parents[1]\n(ROOT / "SOURCE_INDEX.json").write_text("{}\\n", encoding="utf-8")\n(ROOT / "SOURCE_INDEX.md").write_text("# Empty fixture\\n", encoding="utf-8")\n'''
        write_fixture(root, builder)
        module = import_fixture_rebuild_indexes(root)
        try:
            module.refresh_source_index_subprocess()
        except RuntimeError as exc:
            if "empty SOURCE_INDEX.json" not in str(exc):
                fail(f"unexpected failure message for empty JSON: {exc}")
        else:
            fail("empty SOURCE_INDEX.json did not fail refresh_source_index_subprocess()")
        assert_no_bytecode(root)


def main() -> int:
    assert_static_contract()
    probe_successful_json_handoff()
    probe_builder_failure_is_reported()
    probe_empty_json_fails_closed()
    print("rebuild-indexes-source-index-subprocess-rev0843: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
