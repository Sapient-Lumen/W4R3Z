import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
out = ROOT / "innovation-packet.json"

receipt = json.loads((ROOT / "REVISION-RECEIPT.json").read_text(encoding="utf-8"))
status = json.loads((ROOT / "SURFACE-STATUS.json").read_text(encoding="utf-8"))
manifest = json.loads((ROOT / "RELEASE-MANIFEST.json").read_text(encoding="utf-8"))

pack = {
    "project": "DelayBasin",
    "revision": receipt["revision"],
    "surface": "innovation-packet.json",
    "derivative_note": "Derivative current innovation packet; canon wins.",
    "packet_sources": [
        "REVISION-RECEIPT.json",
        "SURFACE-STATUS.json",
        "CHANGELOG.md",
        "RELEASE-MANIFEST.json",
    ],
    "anchor": {
        "previous_revision": receipt["previous_revision"],
        "expected_head": receipt["basis_witness"]["expected_head"],
        "observed_head": receipt["basis_witness"]["observed_head"],
        "basis_state": receipt["basis_witness"]["basis_state"],
        "basis_anchor_precision": receipt["basis_witness"]["basis_anchor_precision"],
        "basis_omission_basis": receipt["basis_witness"]["basis_omission_basis"],
    },
    "innovation": {
        "summary": receipt["summary"],
        "move_classes": receipt["move_classes"],
        "canon_additions": receipt["canon_additions"],
        "hot_current_supports": receipt["hot_current_supports"],
        "quarantine_additions": receipt["quarantine_additions"],
        "touched_surfaces": receipt["touched_surfaces"],
        "exact_list_source": "REVISION-RECEIPT.json",
    },
    "reconciliation": {
        "basis_surfaces": receipt["basis_witness"]["basis_surfaces"],
        "status_surface": "SURFACE-STATUS.json",
        "manifest_surface": "RELEASE-MANIFEST.json",
        "changelog_surface": "CHANGELOG.md",
        "continuation_mode": receipt["basis_witness"]["repair"],
    },
    "public_state": {
        "citation_head": status["citation_head"]["surface"],
        "frozen_public_surface": status["status_lanes"]["frozen_public_surface"],
        "public_state": status["status_lanes"]["public_state"],
        "bundle": manifest["bundle"],
    },
    "explicit_non_claim": "Not a recap blob, summary-authority surface, or substitute for REVISION-RECEIPT.json.",
}
out.write_text(json.dumps(pack, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
print(f"wrote {out}")
