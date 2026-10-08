from __future__ import annotations

import importlib.util
import json
from collections import Counter
import re
import subprocess
import sys
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _load_mkrevzip_module():
    spec = importlib.util.spec_from_file_location("mkrevzip_test_module", ROOT / "tools" / "mkrevzip.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_mkrevzip_skips_bootstrap_virtualenv_tree() -> None:
    module = _load_mkrevzip_module()

    assert module.should_skip(Path(".venv/lib/site-packages/vendor.py"))
    assert module.should_skip(Path(".pytest_cache/v/cache/nodeids"))
    assert module.should_skip(Path(".artifacts/mxtest-plan.json"))
    assert module.should_skip(Path(".artifacts/mxtest-all-64-rev0835-probe.json"))
    assert not module.should_skip(Path(".artifacts/mxtest-all.json"))
    assert not module.should_skip(Path(".artifacts/mxtest-all-64.json"))
    assert module.should_skip(Path("build/generated.txt"))
    assert module.should_skip(Path("src/micromax_editor/plugin.cpython-313.pyc"))
    assert module.should_skip(Path("src/micromax_editor/__pycache__/plugin.cpython-313.pyc"))
    assert module.should_skip(Path("src/micromax.egg-info/SOURCES.txt"))
    assert module.should_skip(Path("Micromax-rev0000-test.zip"))
    assert not module.should_skip(Path("src/micromax/vm.py"))



def test_mkrevzip_carries_current_aggregate_evidence_manifest(tmp_path) -> None:
    module = _load_mkrevzip_module()
    stamp = "2026.03.18.16.22"
    artifacts = ROOT / ".artifacts"
    artifacts.mkdir(exist_ok=True)
    carried = artifacts / "mxtest-all.json"
    skipped = artifacts / "mxtest-all-64-rev0835-probe.json"
    carried.write_text('{"sentinel":"carry-me"}\n', encoding="utf-8")
    skipped.write_text('{"sentinel":"skip-me"}\n', encoding="utf-8")
    try:
        proc = subprocess.run(
            [
                sys.executable,
                str(ROOT / "tools" / "mkrevzip.py"),
                "--tag",
                "archive-evidence-manifest-carryotter",
                "--stamp",
                stamp,
                "--outdir",
                str(tmp_path),
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        assert proc.returncode == 0, proc.stderr
        outpath = Path(proc.stdout.strip())
        with zipfile.ZipFile(outpath) as zf:
            names = set(zf.namelist())
            assert ".artifacts/mxtest-all.json" in names
            assert ".artifacts/mxtest-all-64-rev0835-probe.json" not in names
            assert json.loads(zf.read(".artifacts/mxtest-all.json"))["sentinel"] == "carry-me"
    finally:
        carried.unlink(missing_ok=True)
        skipped.unlink(missing_ok=True)


def _expected_rev() -> int:
    first = (ROOT / "TODO.md").read_text(encoding="utf-8").splitlines()[0]
    match = re.search(r"rev\s*(\d+)", first, flags=re.IGNORECASE)
    assert match is not None
    return int(match.group(1))


def test_context_snapshot_prefers_current_tree_snapshot_without_live_import(tmp_path, monkeypatch) -> None:
    module = _load_mkrevzip_module()
    rev = _expected_rev()
    context = {
        "project": "micromax",
        "rev": rev,
        "checks": {"ok": True},
        "revision_sources": {"ok": True},
        "sentinel": "from-existing-context",
    }
    (tmp_path / "MICROMAX-CONTEXT.json").write_text(json.dumps(context), encoding="utf-8")

    def fail_import(name, *args, **kwargs):
        if name == "mxcontext":
            raise AssertionError("mkrevzip should not rebuild context when the tree snapshot is current")
        return original_import(name, *args, **kwargs)

    import builtins

    original_import = builtins.__import__
    monkeypatch.setattr(builtins, "__import__", fail_import)

    assert module.context_snapshot(tmp_path, rev=rev)["sentinel"] == "from-existing-context"


def test_mkrevzip_embeds_context_manifest(tmp_path) -> None:
    stamp = "2026.03.18.16.20"
    proc = subprocess.run(
        [
            sys.executable,
            str(ROOT / "tools" / "mkrevzip.py"),
            "--tag",
            "archive-context-manifest-mapotter",
            "--stamp",
            stamp,
            "--outdir",
            str(tmp_path),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr
    outpath = Path(proc.stdout.strip())
    assert outpath.exists()
    assert outpath.name == (
        f"Micromax-rev{_expected_rev():04d}-{stamp}-archive-context-manifest-mapotter.zip"
    )

    with zipfile.ZipFile(outpath) as zf:
        names = set(zf.namelist())
        assert not any(name.startswith(".tmp") for name in names)
        assert "README.md" in names
        assert "MICROMAX-CONTEXT.json" in names
        manifest = json.loads(zf.read("MICROMAX-CONTEXT.json"))

    assert manifest["archive"]["name"] == outpath.name
    assert manifest["archive"]["tag"] == "archive-context-manifest-mapotter"
    assert manifest["archive"]["timestamp"] == stamp
    assert manifest["archive"]["timezone"] == "America/New_York"
    assert manifest["archive"]["context_path"] == "MICROMAX-CONTEXT.json"
    assert manifest["archive"]["created_by"] == "tools/mkrevzip.py"

    context = manifest["context"]
    assert context["project"] == "micromax"
    assert context["rev"] == _expected_rev()
    assert context["checks"]["ok"] is True
    assert {
        "README.md",
        "TODO.md",
        "docs/00-vision.md",
        "docs/revision-index.json",
        "docs/installed-help-manifest.txt",
    } <= set(context["docs"])
    assert len(context["docs"]) <= 64
    assert len(context["code"]) <= 48
    assert not any(path.startswith("docs/history/") for path in context["docs"])
    assert context["inventory"]["docs"]["listed"] == len(context["docs"])
    assert context["inventory"]["catalogs"]["revision_history"] == (
        "docs/revision-index.json"
    )

def test_mkrevzip_skips_tree_file_that_matches_manifest_name(tmp_path) -> None:
    stamp = "2026.03.18.16.21"
    manifest_name = "ZZZ-TEMP-MANIFEST.json"
    manifest_path = ROOT / manifest_name
    manifest_path.write_text('{"stale": true}\n', encoding='utf-8')
    try:
        proc = subprocess.run(
            [
                sys.executable,
                str(ROOT / "tools" / "mkrevzip.py"),
                "--tag",
                "archive-context-manifest-skipotter",
                "--stamp",
                stamp,
                "--manifest-name",
                manifest_name,
                "--outdir",
                str(tmp_path),
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        assert proc.returncode == 0, proc.stderr
        outpath = Path(proc.stdout.strip())
        with zipfile.ZipFile(outpath) as zf:
            counts = Counter(zf.namelist())
            assert counts[manifest_name] == 1
            manifest = json.loads(zf.read(manifest_name))
        assert manifest["archive"]["context_path"] == manifest_name
        assert manifest["archive"]["name"] == outpath.name
        assert manifest["context"]["project"] == "micromax"
    finally:
        manifest_path.unlink(missing_ok=True)
