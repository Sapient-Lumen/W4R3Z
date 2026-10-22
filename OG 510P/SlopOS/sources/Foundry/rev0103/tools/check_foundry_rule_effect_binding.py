#!/usr/bin/env python3
"""Check Foundry specimen 97 rule-effect binding fixtures."""
from pathlib import Path
import json
import sys

try:
    from foundry_checklib import FIXTURES, ROOT, load_json, parse_time, require_sha256, fail
except ModuleNotFoundError:  # pragma: no cover
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from foundry_checklib import FIXTURES, ROOT, load_json, parse_time, require_sha256, fail

FIXTURE_DIR = FIXTURES / "specimen-97-rule-effect-binding"
LEDGER_STATUSES = {"bound", "partial", "refused", "quarantined", "no_effect", "informational"}
WITNESS_STATUSES = {"effect_applied", "effect_partial", "effect_refused", "effect_missing", "effect_bypassed", "effect_quarantined", "effect_superseded"}
FENCE_REASONS = {
    "evaluation_without_effect",
    "effect_without_trace",
    "wrong_surface",
    "scope_widening",
    "missing_effect_witness",
    "bypass_unrecorded",
    "stale_trace",
    "selected_rule_erased",
    "default_outcome_laundering",
    "warning_as_enforcement",
    "audit_only_as_block",
    "public_release_laundering",
    "authorization_laundering",
    "repair_lifecycle_laundering",
    "sibling_boundary_laundering",
    "shadow_rule_activation",
    "deprecated_rule_activation",
    "ambiguity_fence_ignored",
    "checker_success_as_effect",
    "reference_integrity_drift",
}
SCOPE_KEYS = ["consumers", "surfaces", "audiences", "purpose_classes", "carriers", "rule_targets"]
AUTHORITY_WORDS = ["authorization", "audit", "release", "repair", "lifecycle", "verdict", "truth", "approval", "sibling", "policy"]

errors = []
fixture_files = sorted(FIXTURE_DIR.glob("*.json"))
if not fixture_files:
    print("Missing specimen 97 fixture")
    sys.exit(1)

source_path = FIXTURES / "specimen-96-rule-evaluation" / "fixture.json"
source_traces = {}
source_witnesses = {}
source_fences = {}
if source_path.exists():
    source = load_json(source_path)
    source_traces = {t.get("trace_id"): t for t in source.get("rule_evaluation_traces") or []}
    source_witnesses = {w.get("witness_id"): w for w in source.get("applicability_witnesses") or []}
    source_fences = {f.get("fence_id"): f for f in source.get("misapplication_fences") or []}
else:
    errors.append("fixtures/specimen-96-rule-evaluation/fixture.json is required for specimen 97")

ledger_count = witness_count = fence_count = 0
ledger_status_counts = {s: 0 for s in LEDGER_STATUSES}
witness_status_counts = {s: 0 for s in WITNESS_STATUSES}

for path in fixture_files:
    rel = path.relative_to(ROOT)
    data = load_json(path)
    if data.get("fixture_family") != "foundry_semantic_fixture_bundle_v0":
        errors.append(f"{rel}: wrong fixture_family")
    if str(data.get("specimen_id")) != "97":
        errors.append(f"{rel}: wrong specimen_id")
    if not parse_time(data.get("fixture_now")):
        errors.append(f"{rel}: missing/unparsable fixture_now")

    local_traces = {t.get("trace_id"): t for t in data.get("source_rule_evaluation_trace_refs") or []}
    local_witnesses = {w.get("witness_id"): w for w in data.get("source_applicability_witness_refs") or []}
    local_fences = {f.get("fence_id"): f for f in data.get("source_misapplication_fence_refs") or []}
    ledgers = data.get("rule_effect_ledgers") or []
    witnesses = data.get("effect_witnesses") or []
    fences = data.get("bypass_fences") or []
    negative_cases = data.get("negative_cases") or []

    for name, index in [("source traces", local_traces), ("source applicability witnesses", local_witnesses), ("source misapplication fences", local_fences)]:
        if not index:
            errors.append(f"{rel}: missing {name}")

    for tid, trace in local_traces.items():
        if tid not in source_traces:
            errors.append(f"{rel}: source trace ref {tid} is not present in specimen 96")
        elif trace.get("trace_digest") != source_traces[tid].get("trace_digest"):
            errors.append(f"{rel}: source trace ref {tid} digest mismatch")
        if trace.get("evaluation_status") not in {"applied", "refused", "partial", "skipped", "quarantined", "informational"}:
            errors.append(f"{rel}: source trace ref {tid} status looks invalid")
    for wid, witness in local_witnesses.items():
        if wid not in source_witnesses:
            errors.append(f"{rel}: source applicability witness {wid} is not present in specimen 96")
        elif witness.get("trace_id") != source_witnesses[wid].get("trace_id"):
            errors.append(f"{rel}: source applicability witness {wid} trace mismatch")
        if witness.get("trace_id") not in local_traces:
            errors.append(f"{rel}: source applicability witness {wid} points outside local traces")
        if not require_sha256(witness.get("witness_digest")):
            errors.append(f"{rel}: source applicability witness {wid} missing digest")
    for fid, fence in local_fences.items():
        if fid not in source_fences:
            errors.append(f"{rel}: source misapplication fence {fid} is not present in specimen 96")
        elif fence.get("trace_id") != source_fences[fid].get("trace_id"):
            errors.append(f"{rel}: source misapplication fence {fid} trace mismatch")
        if fence.get("trace_id") not in local_traces:
            errors.append(f"{rel}: source misapplication fence {fid} points outside local traces")

    ledger_by_id = {}
    required_witnesses = {}
    required_fences = {}
    for ledger in ledgers:
        ledger_count += 1
        lid = ledger.get("ledger_id", "<missing>")
        if lid in ledger_by_id:
            errors.append(f"{rel}: duplicate rule-effect ledger_id {lid}")
        ledger_by_id[lid] = ledger
        if ledger.get("ledger_family") != "foundry_rule_effect_ledger_v0":
            errors.append(f"{rel}: ledger {lid} has wrong ledger_family")
        if not require_sha256(ledger.get("ledger_digest")):
            errors.append(f"{rel}: ledger {lid} missing sha256 ledger_digest")
        status = ledger.get("effect_status")
        if status not in LEDGER_STATUSES:
            errors.append(f"{rel}: ledger {lid} has unknown effect_status {status!r}")
        else:
            ledger_status_counts[status] += 1
        if not parse_time(ledger.get("bound_at")):
            errors.append(f"{rel}: ledger {lid} missing/unparsable bound_at")
        for key in ["source_trace_ids", "source_applicability_witness_ids", "source_misapplication_fence_ids", "effect_context", "intended_effects", "effect_witness_ids", "required_bypass_fence_ids", "blocked_inferences", "authority_boundaries"]:
            if key not in ledger or ledger.get(key) in (None, ""):
                errors.append(f"{rel}: ledger {lid} missing {key}")
        context = ledger.get("effect_context") or {}
        for skey in SCOPE_KEYS:
            if not context.get(skey):
                errors.append(f"{rel}: ledger {lid} context missing {skey}")
        for tid in ledger.get("source_trace_ids") or []:
            if tid not in local_traces:
                errors.append(f"{rel}: ledger {lid} references unknown source trace {tid}")
        for wid in ledger.get("source_applicability_witness_ids") or []:
            if wid not in local_witnesses:
                errors.append(f"{rel}: ledger {lid} references unknown source applicability witness {wid}")
            elif local_witnesses[wid].get("trace_id") not in set(ledger.get("source_trace_ids") or []):
                errors.append(f"{rel}: ledger {lid} witness {wid} is not tied to ledger source traces")
        for fid in ledger.get("source_misapplication_fence_ids") or []:
            if fid not in local_fences:
                errors.append(f"{rel}: ledger {lid} references unknown source misapplication fence {fid}")
            elif local_fences[fid].get("trace_id") not in set(ledger.get("source_trace_ids") or []):
                errors.append(f"{rel}: ledger {lid} source fence {fid} is not tied to ledger source traces")
        if status in {"bound", "partial", "quarantined"} and not ledger.get("bound_effects"):
            errors.append(f"{rel}: ledger {lid} has {status} status without bound_effects")
        if status in {"refused", "no_effect", "informational"} and ledger.get("bound_effects"):
            errors.append(f"{rel}: ledger {lid} should not carry bound_effects for {status} status")
        boundary_text = " ".join((ledger.get("blocked_inferences") or []) + (ledger.get("authority_boundaries") or [])).lower()
        if not any(word in boundary_text for word in AUTHORITY_WORDS):
            errors.append(f"{rel}: ledger {lid} must block authority/audit/release/repair/lifecycle/sibling inferences")
        required_witnesses[lid] = set(ledger.get("effect_witness_ids") or [])
        required_fences[lid] = set(ledger.get("required_bypass_fence_ids") or [])

    witness_by_id = {}
    for witness in witnesses:
        witness_count += 1
        wid = witness.get("witness_id", "<missing>")
        if wid in witness_by_id:
            errors.append(f"{rel}: duplicate effect witness_id {wid}")
        witness_by_id[wid] = witness
        lid = witness.get("ledger_id")
        tid = witness.get("trace_id")
        if witness.get("witness_family") != "foundry_effect_witness_v0":
            errors.append(f"{rel}: witness {wid} has wrong witness_family")
        if lid not in ledger_by_id:
            errors.append(f"{rel}: witness {wid} references missing ledger {lid}")
        if tid not in local_traces:
            errors.append(f"{rel}: witness {wid} references unknown trace {tid}")
        elif lid in ledger_by_id and tid not in (ledger_by_id[lid].get("source_trace_ids") or []):
            errors.append(f"{rel}: witness {wid} trace {tid} not listed on ledger {lid}")
        if not require_sha256(witness.get("witness_digest")):
            errors.append(f"{rel}: witness {wid} missing sha256 witness_digest")
        status = witness.get("effect_status")
        if status not in WITNESS_STATUSES:
            errors.append(f"{rel}: witness {wid} has unknown effect_status {status!r}")
        else:
            witness_status_counts[status] += 1
        if not parse_time(witness.get("observed_at")):
            errors.append(f"{rel}: witness {wid} missing/unparsable observed_at")
        for key in ["effect_context_echo", "effect_action", "evidence_refs", "residual_fence_refs", "negative_case_ids", "blocked_inferences", "authority_boundaries"]:
            if not witness.get(key):
                errors.append(f"{rel}: witness {wid} missing {key}")
        context = witness.get("effect_context_echo") or {}
        for skey in SCOPE_KEYS:
            if not context.get(skey):
                errors.append(f"{rel}: witness {wid} context echo missing {skey}")
        ledger = ledger_by_id.get(lid) or {}
        if ledger and context != (ledger.get("effect_context") or {}):
            errors.append(f"{rel}: witness {wid} context echo does not match ledger {lid}")
        if status in {"effect_refused", "effect_missing", "effect_bypassed", "effect_quarantined", "effect_superseded", "effect_partial"} and not witness.get("residual_fence_refs"):
            errors.append(f"{rel}: witness {wid} needs residual fences for non-clean status")
        boundary_text = " ".join((witness.get("blocked_inferences") or []) + (witness.get("authority_boundaries") or [])).lower()
        if not any(word in boundary_text for word in AUTHORITY_WORDS):
            errors.append(f"{rel}: witness {wid} must block authority/audit/release/repair/lifecycle/sibling inferences")

    fence_by_id = {}
    fences_by_ledger = {}
    for fence in fences:
        fence_count += 1
        fid = fence.get("fence_id", "<missing>")
        if fid in fence_by_id:
            errors.append(f"{rel}: duplicate bypass fence_id {fid}")
        fence_by_id[fid] = fence
        lid = fence.get("ledger_id")
        tid = fence.get("trace_id")
        fences_by_ledger.setdefault(lid, set()).add(fid)
        if fence.get("fence_family") != "foundry_bypass_fence_v0":
            errors.append(f"{rel}: fence {fid} has wrong fence_family")
        if lid not in ledger_by_id:
            errors.append(f"{rel}: fence {fid} references missing ledger {lid}")
        if tid not in local_traces:
            errors.append(f"{rel}: fence {fid} references unknown trace {tid}")
        elif lid in ledger_by_id and tid not in (ledger_by_id[lid].get("source_trace_ids") or []):
            errors.append(f"{rel}: fence {fid} trace {tid} not listed on ledger {lid}")
        if not require_sha256(fence.get("fence_digest")):
            errors.append(f"{rel}: fence {fid} missing sha256 fence_digest")
        if fence.get("fence_reason") not in FENCE_REASONS:
            errors.append(f"{rel}: fence {fid} has unknown fence_reason {fence.get('fence_reason')!r}")
        if not parse_time(fence.get("created_at")):
            errors.append(f"{rel}: fence {fid} missing/unparsable created_at")
        for key in ["affected_effects", "subject_refs", "blocked_actions", "required_clearance", "authority_boundaries"]:
            if not fence.get(key):
                errors.append(f"{rel}: fence {fid} missing {key}")
        for lid2 in fence.get("affected_effects") or []:
            if lid2 not in ledger_by_id:
                errors.append(f"{rel}: fence {fid} affected_effects references unknown ledger {lid2}")
        boundary_text = " ".join(fence.get("authority_boundaries") or []).lower()
        if not any(word in boundary_text for word in AUTHORITY_WORDS):
            errors.append(f"{rel}: fence {fid} must block authority/audit/release/repair/lifecycle/sibling inferences")

    for ledger in ledgers:
        lid = ledger.get("ledger_id")
        for wid in required_witnesses.get(lid, set()):
            if wid not in witness_by_id:
                errors.append(f"{rel}: ledger {lid} lists missing effect witness {wid}")
        for fid in required_fences.get(lid, set()):
            if fid not in fence_by_id:
                errors.append(f"{rel}: ledger {lid} lists missing bypass fence {fid}")
        for wid in [w.get("witness_id") for w in witnesses if w.get("ledger_id") == lid]:
            if wid not in required_witnesses.get(lid, set()):
                errors.append(f"{rel}: witness {wid} is not listed on ledger {lid}")
        if not required_fences.get(lid, set()).issubset(fences_by_ledger.get(lid, set())):
            missing = sorted(required_fences.get(lid, set()) - fences_by_ledger.get(lid, set()))
            errors.append(f"{rel}: ledger {lid} missing required bypass fences: {', '.join(missing)}")

    case_ids = [c.get("case_id") for c in negative_cases]
    if len(case_ids) != len(set(case_ids)):
        errors.append(f"{rel}: duplicate negative case ids")
    if len(negative_cases) < 24:
        errors.append(f"{rel}: specimen 97 must carry at least 24 negative cases")
    for case in negative_cases:
        if case.get("must_fail") is not True:
            errors.append(f"{rel}: negative case {case.get('case_id')} must set must_fail=true")
        if not case.get("failure_code") or not case.get("failure_mode") or not case.get("expected_failure"):
            errors.append(f"{rel}: negative case {case.get('case_id')} missing failure_code/failure_mode/expected_failure")
    negative_text = " ".join((c.get("failure_code", "") + " " + c.get("failure_mode", "") + " " + c.get("expected_failure", "")) for c in negative_cases).lower()
    for word in ["effect", "trace", "ledger", "witness", "bypass", "surface", "scope", "shadow", "deprecated", "default", "warning", "audit", "public", "authorization", "repair", "lifecycle", "sibling", "checker", "reference"]:
        if word not in negative_text:
            errors.append(f"{rel}: negative cases should cover {word}")

for status in ["bound", "partial", "refused", "quarantined", "no_effect", "informational"]:
    if ledger_status_counts.get(status, 0) == 0:
        errors.append(f"specimen 97 needs at least one {status} ledger")
for status in ["effect_applied", "effect_partial", "effect_refused", "effect_missing", "effect_bypassed", "effect_quarantined", "effect_superseded"]:
    if witness_status_counts.get(status, 0) == 0:
        errors.append(f"specimen 97 needs at least one {status} witness")

fail(errors)
print(
    f"Foundry rule-effect binding check passed for {len(fixture_files)} fixture file(s), "
    f"{ledger_count} rule-effect ledger(s), {witness_count} effect witness(es), and {fence_count} bypass fence(s)"
)
