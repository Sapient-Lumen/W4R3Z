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
    assert "docs/460-recent-picker-query-completion.md" in context["docs"]
    assert "docs/461-recent-clear-count-hostcall.md" in context["docs"]
    assert "docs/462-recent-picker-row-hostcalls.md" in context["docs"]
    assert "docs/465-showrecentdir-slot-detail.md" in context["docs"]
    assert "docs/466-showjump-hash-dialect.md" in context["docs"]
    assert "docs/468-jumppick-hash-dialect.md" in context["docs"]
    assert "docs/469-jumppick-command-completion.md" in context["docs"]
    assert "docs/470-jumppick-exact-miss.md" in context["docs"]
    assert "docs/471-jumppick-submit-slot-feedback.md" in context["docs"]
    assert "docs/472-jump-navigation-slot-feedback.md" in context["docs"]
    assert "docs/473-jump-navigation-status-model.md" in context["docs"]
    assert "docs/474-jump-navigation-command-preview.md" in context["docs"]
    assert "docs/475-jumps-command-preview.md" in context["docs"]
    assert "docs/476-showjumpgroups-command-preview.md" in context["docs"]
    assert "docs/477-showjump-command-preview.md" in context["docs"]
    assert "docs/478-jumppick-command-preview.md" in context["docs"]
    assert "docs/479-showstatus-command-preview.md" in context["docs"]
    assert "docs/480-showrecent-command-preview.md" in context["docs"]
    assert "docs/481-showrecentdir-command-preview.md" in context["docs"]
    assert "docs/482-showrecentgroups-command-preview.md" in context["docs"]
    assert "docs/483-showrecentdirgroups-command-preview.md" in context["docs"]
    assert "docs/484-recentpick-command-preview.md" in context["docs"]
    assert "docs/485-recentdirpick-command-preview.md" in context["docs"]
    assert "docs/486-recent-command-preview.md" in context["docs"]
    assert "docs/487-recentpick-exact-slot-miss.md" in context["docs"]
    assert "docs/488-showrecentdir-exact-slot-miss.md" in context["docs"]
    assert "docs/489-showrecent-exact-path-miss.md" in context["docs"]
    assert "docs/490-showrecentdir-exact-path-miss.md" in context["docs"]
    assert "docs/491-recent-group-zero-summary-preview.md" in context["docs"]
    assert "docs/492-recent-picker-zero-summary-preview.md" in context["docs"]
    assert "docs/493-recent-command-exact-slot-miss.md" in context["docs"]
    assert "docs/494-recent-command-hash-doc.md" in context["docs"]
    assert "docs/495-save-saveas-command-preview.md" in context["docs"]
    assert "docs/496-group-summary-command-preview.md" in context["docs"]
    assert "docs/497-close-family-command-preview.md" in context["docs"]
    assert "docs/498-quit-command-preview.md" in context["docs"]
    assert "docs/499-undo-redo-command-preview.md" in context["docs"]
    assert "docs/500-close-force-command-preview.md" in context["docs"]
    assert "docs/501-showkeymodes-command-preview.md" in context["docs"]
    assert "docs/502-showhooks-command-preview.md" in context["docs"]
    assert "docs/503-plugin-list-command-preview.md" in context["docs"]
    assert "docs/504-macro-subcommand-preview.md" in context["docs"]
    assert "docs/505-plugin-subcommand-preview.md" in context["docs"]
    assert "docs/506-macro-slot-command-preview.md" in context["docs"]
    assert "docs/507-macro-action-command-preview.md" in context["docs"]
    assert "docs/508-plugin-target-command-preview.md" in context["docs"]
    assert "docs/509-showplugin-missing-command-preview.md" in context["docs"]
    assert "docs/510-showhook-missing-command-preview.md" in context["docs"]
    assert "docs/511-exact-inspection-missing-command-preview.md" in context["docs"]
    assert "docs/512-exact-editor-state-missing-command-preview.md" in context["docs"]
    assert "docs/513-showbindings-mode-command-preview.md" in context["docs"]
    assert "docs/514-showbindings-command-preview.md" in context["docs"]
    assert "docs/515-whichkey-command-preview.md" in context["docs"]
    assert "docs/516-group-summary-sample-truth.md" in context["docs"]
    assert "docs/517-group-summary-command-preview-wording.md" in context["docs"]
    assert "docs/518-recent-group-preview-neutral-wording.md" in context["docs"]
    assert "docs/519-showjumpgroups-sample-preview.md" in context["docs"]
    assert "docs/520-showhooks-empty-sample-preview.md" in context["docs"]
    assert "docs/521-showkeymodes-empty-sample-preview.md" in context["docs"]
    assert "docs/522-active-binding-empty-witness.md" in context["docs"]
    assert "docs/523-plugin-manager-unavailable-previews.md" in context["docs"]
    assert "docs/524-pluginpick-no-manager-feedback.md" in context["docs"]
    assert "docs/525-pluginpick-compact-menu-dialect.md" in context["docs"]
    assert "docs/526-pluginpick-command-preview.md" in context["docs"]
    assert "docs/527-plugin-root-command-preview.md" in context["docs"]
    assert "docs/528-showplugin-command-preview.md" in context["docs"]
    assert "docs/529-plugin-subcommand-empty-subset-witness.md" in context["docs"]
    assert "docs/530-plugin-reload-target-detail-preview.md" in context["docs"]
    assert "docs/531-plugin-info-target-state-fallback.md" in context["docs"]
    assert "docs/532-plugin-exact-multierror-preview.md" in context["docs"]
    assert "docs/534-plugin-errors-available-state-witness.md" in context["docs"]
    assert "docs/535-plugin-runtime-zeroerror-state-witness.md" in context["docs"]
    assert "docs/536-plugin-info-available-notloaded-preview.md" in context["docs"]
    assert "docs/537-showplugin-runtime-available-witness.md" in context["docs"]
    assert "docs/538-showplugin-runtime-multierror-summary.md" in context["docs"]
    assert "docs/539-plugin-reload-runtime-broken-detail.md" in context["docs"]
    assert "docs/540-plugin-runtime-filterederror-detail.md" in context["docs"]
    assert "docs/541-plugin-runtime-singleerror-dedup.md" in context["docs"]
    assert "docs/542-showplugin-runtime-loaded-state-witness.md" in context["docs"]
    assert "docs/543-plugin-errors-runtime-emptywitness.md" in context["docs"]
    assert "docs/544-plugin-info-runtime-loaded-witness.md" in context["docs"]
    assert "docs/546-plugin-runtime-no-manager-distinction.md" in context["docs"]
    assert "docs/547-plugin-runtime-root-summary.md" in context["docs"]
    assert "docs/548-showplugin-runtime-root-summary.md" in context["docs"]


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
