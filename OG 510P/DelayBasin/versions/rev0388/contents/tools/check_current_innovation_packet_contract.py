import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
PACK = ROOT / "innovation-packet.json"
RECEIPT = ROOT / "REVISION-RECEIPT.json"
STATUS = ROOT / "SURFACE-STATUS.json"
MANIFEST = ROOT / "RELEASE-MANIFEST.json"

pack = json.loads(PACK.read_text(encoding="utf-8"))
receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
status = json.loads(STATUS.read_text(encoding="utf-8"))
manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

required = {"project", "revision", "surface", "derivative_note", "packet_sources", "anchor", "innovation", "reconciliation", "public_state", "explicit_non_claim"}
missing = required - set(pack)
if missing:
    raise SystemExit(f"innovation-packet missing keys: {sorted(missing)}")
if pack["project"] != "DelayBasin":
    raise SystemExit("innovation-packet project mismatch")
if pack["surface"] != "innovation-packet.json":
    raise SystemExit("innovation-packet surface self-id drift")
if pack["revision"] != receipt["revision"]:
    raise SystemExit("innovation-packet revision must match receipt")
if pack["derivative_note"] != "Derivative current innovation packet; canon wins.":
    raise SystemExit("innovation-packet derivative_note drift")
for rel in pack["packet_sources"]:
    if not (ROOT / rel).exists():
        raise SystemExit(f"innovation-packet packet source missing: {rel}")

anchor = pack["anchor"]
for key in ["previous_revision", "expected_head", "observed_head", "basis_state", "basis_anchor_precision", "basis_omission_basis"]:
    if key not in anchor:
        raise SystemExit(f"innovation-packet anchor missing {key}")
checks = {
    "previous_revision": receipt["previous_revision"],
    "expected_head": receipt["basis_witness"]["expected_head"],
    "observed_head": receipt["basis_witness"]["observed_head"],
    "basis_state": receipt["basis_witness"]["basis_state"],
    "basis_anchor_precision": receipt["basis_witness"]["basis_anchor_precision"],
    "basis_omission_basis": receipt["basis_witness"]["basis_omission_basis"],
}
for key, expected in checks.items():
    if anchor.get(key) != expected:
        raise SystemExit(f"innovation-packet anchor mismatch on {key}")

innovation = pack["innovation"]
for key in ["summary", "move_classes", "canon_additions", "quarantine_additions", "touched_surfaces", "exact_list_source"]:
    if key not in innovation:
        raise SystemExit(f"innovation-packet innovation missing {key}")
checks = {
    "summary": receipt["summary"],
    "move_classes": receipt["move_classes"],
    "canon_additions": receipt["canon_additions"],
    "quarantine_additions": receipt["quarantine_additions"],
    "touched_surfaces": receipt["touched_surfaces"],
}
for key, expected in checks.items():
    if innovation.get(key) != expected:
        raise SystemExit(f"innovation-packet innovation mismatch on {key}")
if innovation["exact_list_source"] != "REVISION-RECEIPT.json":
    raise SystemExit("innovation-packet exact_list_source drift")

recon = pack["reconciliation"]
for key in ["basis_surfaces", "status_surface", "manifest_surface", "changelog_surface", "continuation_mode"]:
    if key not in recon:
        raise SystemExit(f"innovation-packet reconciliation missing {key}")
if recon["basis_surfaces"] != receipt["basis_witness"]["basis_surfaces"]:
    raise SystemExit("innovation-packet reconciliation basis_surfaces drift")
for relkey in ["status_surface", "manifest_surface", "changelog_surface"]:
    rel = recon[relkey]
    if not (ROOT / rel).exists():
        raise SystemExit(f"innovation-packet reconciliation surface missing: {rel}")
if recon["continuation_mode"] != receipt["basis_witness"]["repair"]:
    raise SystemExit("innovation-packet continuation_mode drift")

public = pack["public_state"]
if public.get("citation_head") != status["citation_head"]["surface"]:
    raise SystemExit("innovation-packet public_state citation_head drift")
if public.get("frozen_public_surface") != status["status_lanes"]["frozen_public_surface"]:
    raise SystemExit("innovation-packet public_state frozen_public_surface drift")
if public.get("public_state") != status["status_lanes"]["public_state"]:
    raise SystemExit("innovation-packet public_state token drift")
if public.get("bundle") != manifest["bundle"]:
    raise SystemExit("innovation-packet public_state bundle drift")

if "Not a recap blob" not in pack["explicit_non_claim"] or "REVISION-RECEIPT.json" not in pack["explicit_non_claim"]:
    raise SystemExit("innovation-packet explicit_non_claim drift")

print("check_current_innovation_packet_contract: OK")
