import json
import pathlib
import re

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
    "status_witness",
    "reentry_cue_witness",
    "retrospective_write_witness",
    "followthrough_witness",
    "assumption_witness",
    "obligation_witness",
    "applicability_witness",
    "foreign_pressure_witness",
    "transfer_witness",
    "resolution_witness",
    "reasoning_firebreak_witness",
    "vocabulary_witness",
    "counterfactual_shadow",
    "receipt_freshness_witness",
    "question_posture_witness",
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
for key in ["expected_head", "observed_head", "basis_surfaces", "session_provenance", "basis_state", "basis_anchor_precision", "basis_omission_basis", "repair"]:
    if key not in basis:
        raise SystemExit(f"receipt basis_witness missing key: {key}")
if not isinstance(basis.get("basis_surfaces"), list) or not basis["basis_surfaces"]:
    raise SystemExit("receipt basis_witness.basis_surfaces must be a non-empty list")
for rel in basis.get("basis_surfaces", []):
    if not (ROOT / rel).exists():
        raise SystemExit(f"receipt basis_witness surface missing: {rel}")
if basis.get("basis_state") not in {"current", "stale", "partial", "mismatched", "resynced"}:
    raise SystemExit("receipt basis_witness.basis_state invalid")
if basis.get("basis_anchor_precision") not in {"direct-underlier", "underlier-plus-wrapper", "wrapper-routed", "packet-only"}:
    raise SystemExit("receipt basis_witness.basis_anchor_precision invalid")
if not isinstance(basis.get("basis_omission_basis"), str) or not basis.get("basis_omission_basis").strip():
    raise SystemExit("receipt basis_witness.basis_omission_basis must be a non-empty string")
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


status = receipt.get("status_witness")
if not isinstance(status, dict):
    raise SystemExit("receipt status_witness must be an object")
for key in ["candidate_surface", "decision_surface", "decision_state", "execution_surface", "execution_state", "frozen_public_surface", "public_state", "durable_status_surface", "mismatch_consequence", "repair"]:
    if key not in status:
        raise SystemExit(f"receipt status_witness missing key: {key}")
for relkey in ["decision_surface", "execution_surface", "durable_status_surface"]:
    rel = status.get(relkey)
    if not isinstance(rel, str) or not rel:
        raise SystemExit(f"receipt status_witness.{relkey} must be a non-empty string")
    if not (ROOT / rel).exists():
        raise SystemExit(f"receipt status_witness referenced surface missing: {rel}")
if status.get("candidate_surface") is not None:
    cand = status.get("candidate_surface")
    if not isinstance(cand, str) or not cand:
        raise SystemExit("receipt status_witness.candidate_surface must be null or a non-empty string")
    base = cand.split('#', 1)[0]
    if base and not (ROOT / base).exists():
        raise SystemExit(f"receipt status_witness candidate surface missing: {cand}")
if status.get("decision_state") not in {"candidate", "admitted", "held", "rejected"}:
    raise SystemExit("receipt status_witness.decision_state invalid")
if status.get("execution_state") not in {"unmaterialized", "packaged", "superseded", "rolled-back"}:
    raise SystemExit("receipt status_witness.execution_state invalid")
if status.get("public_state") not in {"working", "frozen-citable", "deprecated-public", "absent"}:
    raise SystemExit("receipt status_witness.public_state invalid")
if not isinstance(status.get("frozen_public_surface"), str) or not status.get("frozen_public_surface"):
    raise SystemExit("receipt status_witness.frozen_public_surface must be a non-empty string")
if status.get("repair") not in {"ordinary-continuation", "citation-warning", "rollback-or-repackage", "hold", "recover-resync"}:
    raise SystemExit("receipt status_witness.repair invalid")
if not isinstance(status.get("mismatch_consequence"), str) or not status.get("mismatch_consequence").strip():
    raise SystemExit("receipt status_witness.mismatch_consequence must be a non-empty string")

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


obligation = receipt.get("obligation_witness")
if not isinstance(obligation, dict):
    raise SystemExit("receipt obligation_witness must be an object")
for key in ["witness_surface", "target_surfaces", "missing_support", "current_support", "discharge_path", "obligation_state", "repair"]:
    if key not in obligation:
        raise SystemExit(f"receipt obligation_witness missing key: {key}")
ob_surface = obligation.get("witness_surface")
if not isinstance(ob_surface, str) or not ob_surface:
    raise SystemExit("receipt obligation_witness.witness_surface must be a non-empty string")
ob_base = ob_surface.split('#', 1)[0]
if ob_base and not (ROOT / ob_base).exists():
    raise SystemExit(f"receipt obligation_witness surface missing: {ob_surface}")
if not isinstance(obligation.get("target_surfaces"), list) or not obligation["target_surfaces"]:
    raise SystemExit("receipt obligation_witness.target_surfaces must be a non-empty list")
for rel in obligation.get("target_surfaces", []):
    base = rel.split('#', 1)[0]
    if base and not (ROOT / base).exists():
        raise SystemExit(f"receipt obligation_witness target surface missing: {rel}")
if not isinstance(obligation.get("current_support"), list) or not obligation["current_support"]:
    raise SystemExit("receipt obligation_witness.current_support must be a non-empty list")
for rel in obligation.get("current_support", []):
    base = rel.split('#', 1)[0]
    if base and not (ROOT / base).exists():
        raise SystemExit(f"receipt obligation_witness current support surface missing: {rel}")
if obligation.get("obligation_state") not in {"open", "staged", "satisfied", "waived", "retired"}:
    raise SystemExit("receipt obligation_witness.obligation_state invalid")
if obligation.get("repair") not in {"ordinary-continuation", "narrow-claim", "hold-via-followthrough", "quarantine-or-retire", "refresh-support", "recover-resync"}:
    raise SystemExit("receipt obligation_witness.repair invalid")

applicability = receipt.get("applicability_witness")
if not isinstance(applicability, dict):
    raise SystemExit("receipt applicability_witness must be an object")
for key in ["witness_surface", "target_objective", "carry_object", "applicability_conditions", "baselines", "non_fit_slice", "budget", "negative_transfer_budget", "applicability_state", "repair"]:
    if key not in applicability:
        raise SystemExit(f"receipt applicability_witness missing key: {key}")
app_surface = applicability.get("witness_surface")
if not isinstance(app_surface, str) or not app_surface:
    raise SystemExit("receipt applicability_witness.witness_surface must be a non-empty string")
app_base = app_surface.split('#', 1)[0]
if app_base and not (ROOT / app_base).exists():
    raise SystemExit(f"receipt applicability_witness surface missing: {app_surface}")
if not isinstance(applicability.get("applicability_conditions"), list) or not applicability["applicability_conditions"]:
    raise SystemExit("receipt applicability_witness.applicability_conditions must be a non-empty list")
if not isinstance(applicability.get("baselines"), list) or not applicability["baselines"]:
    raise SystemExit("receipt applicability_witness.baselines must be a non-empty list")
if applicability.get("applicability_state") not in {"gated", "narrow-fit", "eligible", "negative-transfer", "quarantined", "retired"}:
    raise SystemExit("receipt applicability_witness.applicability_state invalid")
if applicability.get("repair") not in {"ordinary-continuation", "narrow-reuse", "close-gate", "quarantine-carry", "recover-resync"}:
    raise SystemExit("receipt applicability_witness.repair invalid")

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


vocab = receipt.get("vocabulary_witness")
if not isinstance(vocab, dict):
    raise SystemExit("receipt vocabulary_witness must be an object")
for key in ["witness_surface", "controlled_families", "target_surfaces", "ambient_synonyms_excluded", "comparability_budget", "vocabulary_state", "repair"]:
    if key not in vocab:
        raise SystemExit(f"receipt vocabulary_witness missing key: {key}")
if vocab.get("witness_surface") != "WITNESS-VOCABULARY.json":
    raise SystemExit("receipt vocabulary_witness.witness_surface must point to WITNESS-VOCABULARY.json")
if not (ROOT / "WITNESS-VOCABULARY.json").exists():
    raise SystemExit("receipt vocabulary_witness requires WITNESS-VOCABULARY.json")
if not isinstance(vocab.get("controlled_families"), list) or not vocab["controlled_families"]:
    raise SystemExit("receipt vocabulary_witness.controlled_families must be a non-empty list")
if not isinstance(vocab.get("target_surfaces"), list) or not vocab["target_surfaces"]:
    raise SystemExit("receipt vocabulary_witness.target_surfaces must be a non-empty list")
for rel in vocab.get("target_surfaces", []):
    if not (ROOT / rel).exists():
        raise SystemExit(f"receipt vocabulary_witness target surface missing: {rel}")
if not isinstance(vocab.get("ambient_synonyms_excluded"), list) or not vocab["ambient_synonyms_excluded"]:
    raise SystemExit("receipt vocabulary_witness.ambient_synonyms_excluded must be a non-empty list")
if vocab.get("vocabulary_state") not in {"locked", "provisional", "drifting", "superseded"}:
    raise SystemExit("receipt vocabulary_witness.vocabulary_state invalid")
if vocab.get("repair") not in {"ordinary-continuation", "use-registry", "narrow-family", "hold", "recover-resync"}:
    raise SystemExit("receipt vocabulary_witness.repair invalid")


posture = receipt.get("question_posture_witness")
if not isinstance(posture, dict):
    raise SystemExit("receipt question_posture_witness must be an object")
for key in ["resolution_surface", "registry_surface", "trajectory_surface", "synced_resolved_questions", "frontier_selection_rule", "posture_state", "repair"]:
    if key not in posture:
        raise SystemExit(f"receipt question_posture_witness missing key: {key}")
for relkey in ["resolution_surface", "registry_surface", "trajectory_surface"]:
    rel = posture[relkey]
    if not isinstance(rel, str) or not rel:
        raise SystemExit(f"receipt question_posture_witness.{relkey} must be a non-empty string")
    if not (ROOT / rel).exists():
        raise SystemExit(f"receipt question_posture_witness referenced surface missing: {rel}")
if not isinstance(posture.get("synced_resolved_questions"), list) or not posture.get("synced_resolved_questions"):
    raise SystemExit("receipt question_posture_witness.synced_resolved_questions must be a non-empty list")
for oid in posture["synced_resolved_questions"]:
    if not re.fullmatch(r"OQ-\d{4}", oid):
        raise SystemExit(f"receipt question_posture_witness invalid OQ id: {oid}")
if len(set(posture["synced_resolved_questions"])) != len(posture["synced_resolved_questions"]):
    raise SystemExit("receipt question_posture_witness.synced_resolved_questions must be unique")
if not isinstance(posture.get("frontier_selection_rule"), str) or not posture.get("frontier_selection_rule"):
    raise SystemExit("receipt question_posture_witness.frontier_selection_rule must be a non-empty string")
if posture.get("posture_state") != "resolved-sync-current":
    raise SystemExit("receipt question_posture_witness.posture_state invalid")
if posture.get("repair") != "ordinary-continuation":
    raise SystemExit("receipt question_posture_witness.repair invalid")

fresh = receipt.get("receipt_freshness_witness")
if not isinstance(fresh, dict):
    raise SystemExit("receipt receipt_freshness_witness must be an object")
for key in ["packaged_bundle_filename", "manifest_timestamp_token", "receipt_timestamp_token", "bundle_stem_suffix_relation", "current_import_id", "current_pressure_id", "change_anchor_surface", "freshness_state", "repair"]:
    if key not in fresh:
        raise SystemExit(f"receipt receipt_freshness_witness missing key: {key}")
if not isinstance(fresh.get("packaged_bundle_filename"), str) or not fresh.get("packaged_bundle_filename"):
    raise SystemExit("receipt receipt_freshness_witness.packaged_bundle_filename must be a non-empty string")
for key in ["manifest_timestamp_token", "receipt_timestamp_token"]:
    if not isinstance(fresh.get(key), str) or not fresh.get(key):
        raise SystemExit(f"receipt receipt_freshness_witness.{key} must be a non-empty string")
if not isinstance(fresh.get("bundle_stem_suffix_relation"), str) or not fresh.get("bundle_stem_suffix_relation").strip():
    raise SystemExit("receipt receipt_freshness_witness.bundle_stem_suffix_relation must be a non-empty string")
for key in ["current_import_id", "current_pressure_id"]:
    if not isinstance(fresh.get(key), str) or not fresh.get(key):
        raise SystemExit(f"receipt receipt_freshness_witness.{key} must be a non-empty string")
anchor = fresh.get("change_anchor_surface")
if not isinstance(anchor, str) or not anchor:
    raise SystemExit("receipt receipt_freshness_witness.change_anchor_surface must be a non-empty string")
anchor_base = anchor.split('#', 1)[0]
if anchor_base and not (ROOT / anchor_base).exists():
    raise SystemExit(f"receipt receipt_freshness_witness change anchor surface missing: {anchor}")
if fresh.get("freshness_state") not in {"current-aligned", "slug-drift", "timestamp-drift", "comparison-drift", "stale-carryforward"}:
    raise SystemExit("receipt receipt_freshness_witness.freshness_state invalid")
if fresh.get("repair") not in {"ordinary-continuation", "refresh-receipt", "regenerate-manifest", "reopen-ledgers", "recover-resync"}:
    raise SystemExit("receipt receipt_freshness_witness.repair invalid")

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
