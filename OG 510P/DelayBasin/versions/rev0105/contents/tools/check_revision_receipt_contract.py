import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
receipt_path = ROOT / "REVISION-RECEIPT.json"
contract_path = ROOT / "docs/20-constitution/revision-receipt-contract.md"

if not receipt_path.exists():
    raise SystemExit("missing REVISION-RECEIPT.json")
if not contract_path.exists():
    raise SystemExit("missing docs/20-constitution/revision-receipt-contract.md")

receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
required = [
    "project",
    "revision",
    "previous_revision",
    "summary",
    "move_classes",
    "canon_additions",
    "quarantine_additions",
    "refs_used",
    "checks_passed",
    "touched_surfaces",
    "packaged_release",
    "basis_witness",
    "scope_witness",
    "authorship_witness",
    "reentry_cue_witness",
    "retrospective_write_witness",
    "followthrough_witness",
    "assumption_witness",
    "foreign_pressure_witness",
    "resolution_witness",
    "reasoning_firebreak_witness",
    "counterfactual_shadow",
]
for key in required:
    if key not in receipt:
        raise SystemExit(f"receipt missing key: {key}")

if receipt.get("project") != "DelayBasin":
    raise SystemExit("receipt project must be DelayBasin")
if not str(receipt.get("revision", "")).startswith("rev"):
    raise SystemExit("receipt revision missing rev####")
if not isinstance(receipt["move_classes"], list) or not receipt["move_classes"]:
    raise SystemExit("receipt move_classes must be a non-empty list")
if "make lint" not in receipt.get("checks_passed", []):
    raise SystemExit("receipt must record make lint")
if not isinstance(receipt.get("packaged_release"), bool):
    raise SystemExit("receipt packaged_release must be boolean")
basis = receipt.get("basis_witness")
if not isinstance(basis, dict):
    raise SystemExit("receipt basis_witness must be an object")
for key in ["expected_head", "observed_head", "basis_surfaces", "session_provenance", "basis_state", "repair"]:
    if key not in basis:
        raise SystemExit(f"receipt basis_witness missing key: {key}")
if not isinstance(basis.get("basis_surfaces"), list) or not basis["basis_surfaces"]:
    raise SystemExit("receipt basis_witness.basis_surfaces must be a non-empty list")
for rel in basis.get("basis_surfaces", []):
    if not (ROOT / rel).exists():
        raise SystemExit(f"receipt basis_witness surface missing: {rel}")
if basis.get("basis_state") not in {"current", "stale", "partial", "mismatched", "resynced"}:
    raise SystemExit("receipt basis_witness.basis_state invalid")
if basis.get("repair") not in {"ordinary-continuation", "bounded-reread", "rerequest", "hold", "recover-resync"}:
    raise SystemExit("receipt basis_witness.repair invalid")
scope = receipt.get("scope_witness")
if not isinstance(scope, dict):
    raise SystemExit("receipt scope_witness must be an object")
for key in ["active_request", "exact_target", "scope_surfaces", "ambient_exclusions", "scope_state", "repair"]:
    if key not in scope:
        raise SystemExit(f"receipt scope_witness missing key: {key}")
if not isinstance(scope.get("scope_surfaces"), list) or not scope["scope_surfaces"]:
    raise SystemExit("receipt scope_witness.scope_surfaces must be a non-empty list")
for rel in scope.get("scope_surfaces", []):
    if not (ROOT / rel).exists():
        raise SystemExit(f"receipt scope_witness surface missing: {rel}")
if not isinstance(scope.get("ambient_exclusions"), list):
    raise SystemExit("receipt scope_witness.ambient_exclusions must be a list")
if scope.get("scope_state") not in {"exact", "broadened", "ambiguous", "ambient", "rescoped"}:
    raise SystemExit("receipt scope_witness.scope_state invalid")
if scope.get("repair") not in {"ordinary-continuation", "narrow-scope", "rerequest", "hold", "recover-resync"}:
    raise SystemExit("receipt scope_witness.repair invalid")

auth = receipt.get("authorship_witness")
if not isinstance(auth, dict):
    raise SystemExit("receipt authorship_witness must be an object")
for key in ["initiating_lane", "draft_authorship", "approval_lane", "execution_lane", "review_lane", "autonomy_posture", "collapse_state", "repair"]:
    if key not in auth:
        raise SystemExit(f"receipt authorship_witness missing key: {key}")
if auth.get("autonomy_posture") not in {"human-piloted", "assisted", "approval-bounded", "bounded-autonomous", "mixed"}:
    raise SystemExit("receipt authorship_witness.autonomy_posture invalid")
if auth.get("collapse_state") not in {"separated", "partially-collapsed", "collapsed-with-compensation"}:
    raise SystemExit("receipt authorship_witness.collapse_state invalid")
if auth.get("repair") not in {"ordinary-continuation", "record-compensating-control", "require-independent-review", "hold", "recover-resync"}:
    raise SystemExit("receipt authorship_witness.repair invalid")

reentry = receipt.get("reentry_cue_witness")
if not isinstance(reentry, dict):
    raise SystemExit("receipt reentry_cue_witness must be an object")
for key in ["surface_lineage", "primary_landing_surface", "supporting_cues", "excluded_paths", "cue_state", "repair"]:
    if key not in reentry:
        raise SystemExit(f"receipt reentry_cue_witness missing key: {key}")
primary = reentry.get("primary_landing_surface")
if not isinstance(primary, str) or not primary:
    raise SystemExit("receipt reentry_cue_witness.primary_landing_surface must be a non-empty string")
if not (ROOT / primary).exists():
    raise SystemExit(f"receipt reentry_cue_witness primary surface missing: {primary}")
if not isinstance(reentry.get("supporting_cues"), list) or not reentry["supporting_cues"]:
    raise SystemExit("receipt reentry_cue_witness.supporting_cues must be a non-empty list")
for rel in reentry.get("supporting_cues", []):
    if not (ROOT / rel).exists():
        raise SystemExit(f"receipt reentry_cue_witness supporting cue missing: {rel}")
if not isinstance(reentry.get("excluded_paths"), list):
    raise SystemExit("receipt reentry_cue_witness.excluded_paths must be a list")
if reentry.get("cue_state") not in {"fresh-aligned", "stale", "split-brain", "broken-jump", "overwritten"}:
    raise SystemExit("receipt reentry_cue_witness.cue_state invalid")
if reentry.get("repair") not in {"ordinary-continuation", "refresh-cues", "re-open-primary", "narrow-scope", "recover-resync"}:
    raise SystemExit("receipt reentry_cue_witness.repair invalid")


retrospective = receipt.get("retrospective_write_witness")
if not isinstance(retrospective, dict):
    raise SystemExit("receipt retrospective_write_witness must be an object")
for key in ["witness_surface", "candidate_surface", "cooldown_window", "adjudication_family", "supersession_link", "cooling_state", "disposition", "repair"]:
    if key not in retrospective:
        raise SystemExit(f"receipt retrospective_write_witness missing key: {key}")
for ref in [retrospective.get("witness_surface"), retrospective.get("candidate_surface"), retrospective.get("supersession_link")]:
    if not isinstance(ref, str) or not ref:
        raise SystemExit("receipt retrospective_write_witness referenced surfaces must be non-empty strings")
    base = ref.split('#', 1)[0]
    if base and not (ROOT / base).exists():
        raise SystemExit(f"receipt retrospective_write_witness referenced surface missing: {ref}")
if retrospective.get("cooling_state") not in {"captured", "cooling", "promoted", "demoted", "expired", "quarantined"}:
    raise SystemExit("receipt retrospective_write_witness.cooling_state invalid")
if retrospective.get("disposition") not in {"await-adjudication", "promote", "demote", "expire", "quarantine"}:
    raise SystemExit("receipt retrospective_write_witness.disposition invalid")
if retrospective.get("repair") not in {"ordinary-continuation", "keep-cooling", "promote-now", "expire-candidate", "quarantine-or-retire", "recover-resync"}:
    raise SystemExit("receipt retrospective_write_witness.repair invalid")


follow = receipt.get("followthrough_witness")
if not isinstance(follow, dict):
    raise SystemExit("receipt followthrough_witness must be an object")
for key in ["blocked_object", "local_surface", "followthrough_state", "boundary", "next_proof_surface", "receiving_surface", "repair"]:
    if key not in follow:
        raise SystemExit(f"receipt followthrough_witness missing key: {key}")
local_surface = follow.get("local_surface")
if not isinstance(local_surface, str) or not local_surface:
    raise SystemExit("receipt followthrough_witness.local_surface must be a non-empty string")
local_base = local_surface.split('#', 1)[0]
if local_base and not (ROOT / local_base).exists():
    raise SystemExit(f"receipt followthrough_witness local surface missing: {local_base}")
next_surface = follow.get("next_proof_surface")
if not isinstance(next_surface, str) or not next_surface:
    raise SystemExit("receipt followthrough_witness.next_proof_surface must be a non-empty string")
next_base = next_surface.split('#', 1)[0]
if next_base and not (ROOT / next_base).exists():
    raise SystemExit(f"receipt followthrough_witness next proof surface missing: {next_base}")
recv = follow.get("receiving_surface")
if not isinstance(recv, str) or not recv:
    raise SystemExit("receipt followthrough_witness.receiving_surface must be a non-empty string")
recv_base = recv.split('#', 1)[0]
if recv_base and not (ROOT / recv_base).exists():
    raise SystemExit(f"receipt followthrough_witness receiving surface missing: {recv_base}")
if follow.get("followthrough_state") not in {"local", "queued", "handed-off", "blocked", "expired", "none"}:
    raise SystemExit("receipt followthrough_witness.followthrough_state invalid")
if follow.get("repair") not in {"ordinary-continuation", "refresh-followthrough", "reclaim-local", "expire", "hold", "recover-resync"}:
    raise SystemExit("receipt followthrough_witness.repair invalid")

assumption = receipt.get("assumption_witness")
if not isinstance(assumption, dict):
    raise SystemExit("receipt assumption_witness must be an object")
for key in ["assumption_surface", "assumption_statement", "scope", "supporting_surfaces", "invalidation_triggers", "assumption_state", "repair"]:
    if key not in assumption:
        raise SystemExit(f"receipt assumption_witness missing key: {key}")
assumption_surface = assumption.get("assumption_surface")
if not isinstance(assumption_surface, str) or not assumption_surface:
    raise SystemExit("receipt assumption_witness.assumption_surface must be a non-empty string")
assumption_base = assumption_surface.split('#', 1)[0]
if assumption_base and not (ROOT / assumption_base).exists():
    raise SystemExit(f"receipt assumption_witness surface missing: {assumption_surface}")
if not isinstance(assumption.get("supporting_surfaces"), list) or not assumption["supporting_surfaces"]:
    raise SystemExit("receipt assumption_witness.supporting_surfaces must be a non-empty list")
for rel in assumption.get("supporting_surfaces", []):
    base = rel.split('#', 1)[0]
    if base and not (ROOT / base).exists():
        raise SystemExit(f"receipt assumption_witness supporting surface missing: {rel}")
if not isinstance(assumption.get("invalidation_triggers"), list) or not assumption["invalidation_triggers"]:
    raise SystemExit("receipt assumption_witness.invalidation_triggers must be a non-empty list")
if assumption.get("assumption_state") not in {"active", "discharged", "invalidated", "retired", "quarantined"}:
    raise SystemExit("receipt assumption_witness.assumption_state invalid")
if assumption.get("repair") not in {"ordinary-continuation", "refresh-assumptions", "retest-and-shrink", "quarantine-or-retire", "hold", "recover-resync"}:
    raise SystemExit("receipt assumption_witness.repair invalid")

foreign = receipt.get("foreign_pressure_witness")
if not isinstance(foreign, dict):
    raise SystemExit("receipt foreign_pressure_witness must be an object")
for key in ["witness_surface", "source_packets", "local_gap", "bounded_take", "explicit_non_take", "assimilation_state", "repair"]:
    if key not in foreign:
        raise SystemExit(f"receipt foreign_pressure_witness missing key: {key}")
foreign_surface = foreign.get("witness_surface")
if not isinstance(foreign_surface, str) or not foreign_surface:
    raise SystemExit("receipt foreign_pressure_witness.witness_surface must be a non-empty string")
foreign_base = foreign_surface.split('#', 1)[0]
if foreign_base and not (ROOT / foreign_base).exists():
    raise SystemExit(f"receipt foreign_pressure_witness surface missing: {foreign_surface}")
if not isinstance(foreign.get("source_packets"), list) or not foreign["source_packets"]:
    raise SystemExit("receipt foreign_pressure_witness.source_packets must be a non-empty list")
for pkt in foreign.get("source_packets", []):
    if not isinstance(pkt, dict):
        raise SystemExit("receipt foreign_pressure_witness source_packets entries must be objects")
    for key in ["datacube", "surfaces", "pressure"]:
        if key not in pkt:
            raise SystemExit(f"receipt foreign_pressure_witness source packet missing key: {key}")
    if not isinstance(pkt.get("surfaces"), list) or not pkt["surfaces"]:
        raise SystemExit("receipt foreign_pressure_witness source packet surfaces must be a non-empty list")
if not isinstance(foreign.get("explicit_non_take"), list) or not foreign["explicit_non_take"]:
    raise SystemExit("receipt foreign_pressure_witness.explicit_non_take must be a non-empty list")
if foreign.get("assimilation_state") not in {"imported", "supporting-only", "deferred", "rejected", "retired"}:
    raise SystemExit("receipt foreign_pressure_witness.assimilation_state invalid")
if foreign.get("repair") not in {"ordinary-continuation", "narrow-import", "defer-import", "quarantine-or-retire", "hold", "recover-resync"}:
    raise SystemExit("receipt foreign_pressure_witness.repair invalid")

resolution = receipt.get("resolution_witness")
if not isinstance(resolution, dict):
    raise SystemExit("receipt resolution_witness must be an object")
for key in ["witness_surface", "resolved_objects", "prior_state", "closure_reason", "successor_surface", "reopen_triggers", "closure_state", "repair"]:
    if key not in resolution:
        raise SystemExit(f"receipt resolution_witness missing key: {key}")
resolution_surface = resolution.get("witness_surface")
if not isinstance(resolution_surface, str) or not resolution_surface:
    raise SystemExit("receipt resolution_witness.witness_surface must be a non-empty string")
resolution_base = resolution_surface.split('#', 1)[0]
if resolution_base and not (ROOT / resolution_base).exists():
    raise SystemExit(f"receipt resolution_witness surface missing: {resolution_surface}")
if not isinstance(resolution.get("resolved_objects"), list) or not resolution["resolved_objects"]:
    raise SystemExit("receipt resolution_witness.resolved_objects must be a non-empty list")
successor = resolution.get("successor_surface")
if not isinstance(successor, str) or not successor:
    raise SystemExit("receipt resolution_witness.successor_surface must be a non-empty string")
successor_base = successor.split('#', 1)[0]
if successor_base and not (ROOT / successor_base).exists():
    raise SystemExit(f"receipt resolution_witness successor surface missing: {successor}")
if not isinstance(resolution.get("reopen_triggers"), list) or not resolution["reopen_triggers"]:
    raise SystemExit("receipt resolution_witness.reopen_triggers must be a non-empty list")
if resolution.get("closure_state") not in {"resolved", "superseded", "retired", "deprecated", "rejected"}:
    raise SystemExit("receipt resolution_witness.closure_state invalid")
if resolution.get("repair") not in {"ordinary-continuation", "reopen-via-successor", "recover-closure-basis", "quarantine-or-retire", "hold", "recover-resync"}:
    raise SystemExit("receipt resolution_witness.repair invalid")

move_registry_text = (ROOT / "docs/20-constitution/move-registry.md").read_text(encoding="utf-8")
certified_moves = set()
for line in move_registry_text.splitlines():
    line = line.strip()
    if line.startswith("- `MV-") and "—" in line:
        certified_moves.add(line.split("`")[1])
for move in receipt.get("move_classes", []):
    if move not in certified_moves:
        raise SystemExit(f"receipt move not in move registry: {move}")
for rel in receipt.get("touched_surfaces", []):
    if not (ROOT / rel).exists():
        raise SystemExit(f"receipt touched surface missing: {rel}")

shadow = receipt.get("counterfactual_shadow")
if not isinstance(shadow, dict):
    raise SystemExit("receipt counterfactual_shadow must be an object")
for key in ["status", "nearby_rejected_move", "pivot_surface", "rejection_reason", "still_live"]:
    if key not in shadow:
        raise SystemExit(f"receipt counterfactual_shadow missing key: {key}")
if shadow["status"] not in {"recorded", "none"}:
    raise SystemExit("receipt counterfactual_shadow.status must be 'recorded' or 'none'")
if shadow["status"] == "recorded":
    if not shadow["nearby_rejected_move"] or not shadow["rejection_reason"]:
        raise SystemExit("recorded counterfactual_shadow requires nearby_rejected_move and rejection_reason")
    if not (ROOT / shadow["pivot_surface"]).exists():
        raise SystemExit(f"counterfactual_shadow pivot_surface missing: {shadow['pivot_surface']}")
    still_live = shadow["still_live"]
    base = still_live.split('#', 1)[0]
    if base and not (ROOT / base).exists():
        raise SystemExit(f"counterfactual_shadow still_live base path missing: {base}")

print("check_revision_receipt_contract: OK")
