from __future__ import annotations

import json
from collections import Counter
import re
import subprocess
import sys
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]



def _expected_rev() -> int:
    first = (ROOT / "TODO.md").read_text(encoding="utf-8").splitlines()[0]
    match = re.search(r"rev\s*(\d+)", first, flags=re.IGNORECASE)
    assert match is not None
    return int(match.group(1))



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
    assert outpath.name == f"Micromax-rev{_expected_rev():04d}-{stamp}-archive-context-manifest-mapotter.zip"

    with zipfile.ZipFile(outpath) as zf:
        names = set(zf.namelist())
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
    assert context["checks"]["revision_warnings"] == []
    assert context["revision_sources"]["ok"] is True
    assert "docs/245-archive-context-manifest.md" in context["docs"]
    assert "docs/247-docs-cues-blockquote-break-metadata.md" in context["docs"]
    assert "docs/250-docs-cues-image-target-metadata.md" in context["docs"]
    assert "docs/252-docs-cues-block-kind-metadata.md" in context["docs"]
    assert "docs/255-docs-cues-definition-kind-metadata.md" in context["docs"]
    assert "docs/258-docs-cues-image-source-kind-metadata.md" in context["docs"]
    assert "docs/260-docs-cues-markup-delimiter-metadata.md" in context["docs"]
    assert "docs/344-help-navigation-model.md" in context["docs"]
    assert "docs/357-help-navigation-missingdoc-command-honesty.md" in context["docs"]
    assert "docs/362-macro-inventory-rows.md" in context["docs"]
    assert "docs/363-recent-inventory-rows.md" in context["docs"]
    assert "docs/364-plugin-inventory-rows.md" in context["docs"]


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
