import json
import re
from pathlib import Path
from copy import deepcopy

ROOT = Path(__file__).resolve().parent
REV = "rev0192"
STAMP_UTC = "2026-06-13T05:18:00Z"
DATE = "2026-06-13"


def write_json(rel, data):
    path = ROOT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def read_json(rel):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def write_text(rel, text):
    path = ROOT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.strip() + "\n", encoding="utf-8")


def append_once(rel, marker, text):
    path = ROOT / rel
    old = path.read_text(encoding="utf-8")
    if marker not in old:
        path.write_text(old.rstrip() + "\n\n" + text.strip() + "\n", encoding="utf-8")


def add_unique(seq, item, key=None):
    if key is None:
        if item not in seq:
            seq.append(item)
    else:
        values = {x.get(key) for x in seq if isinstance(x, dict)}
        if item.get(key) not in values:
            seq.append(item)


def add_or_replace(seq, item, key):
    for i, existing in enumerate(seq):
        if isinstance(existing, dict) and existing.get(key) == item.get(key):
            seq[i] = item
            return
    seq.append(item)

write_text("VERSION", REV)

# ---------------------------------------------------------------------------
# New operational surface
# ---------------------------------------------------------------------------
write_text("docs/30-transition/external-receipt-intake-and-wrsr-live-exercise-outcome.md", """
# External receipt intake and WRSR live-exercise outcome

rev0192 closes the next laundering seam after receipt simulation. rev0191 made counterparty receipts capture-ready, but the archive still lacked an intake object that could distinguish actual external receipts from high-fidelity simulations, stale hashes, host-generated artifacts, unsigned letters, dependency-correlated sources, and sealed/public mismatch. It also lacked an exercise outcome object showing whether a WRSR hook actually blocked closure when a welfare or protocol signal appeared.

## Core rules

**Receipt intake is not receipt satisfaction.** An intake record can organize an artifact, but it satisfies no quorum unless independence, artifact integrity, dependency group, sealed/public parity, and public failed-gate disclosure all pass.

**WRSR exercise completion is not WRSR closure.** A workflow can complete an exercise and still remain stayed if representative notice, independent review, result return, pause-window protection, or anti-signal-gaming locks did not fire.

## Receipt intake lane

The receipt intake schema is `schemas/external-receipt-intake-record.schema.json`; the current example is `examples/external-receipt-intake-record-first-touch-defective-template.json`.

The object records the receipt class, source role, dependency disclosures, evidence artifacts, verification checks, defect flags, and reliance decision. It deliberately allows defective, simulated, and quarantined receipt states because the most dangerous artifact is often the one that looks almost sufficient. The example is a high-fidelity first-touch receipt template from a non-host role, but it remains defective because it lacks counterparty confirmation and independent timestamp verification.

## WRSR exercise lane

The WRSR exercise outcome schema is `schemas/wrsr-live-exercise-outcome.schema.json`; the current example is `examples/wrsr-live-exercise-outcome-incident-hook-no-go.json`.

The object records which trigger fired, which low-cost safeguards actually executed, which participant roles were present, which evidence links were available, and which closure actions stayed blocked. The example is intentionally a no-go outcome: the hook fires, but result return and independent review remain incomplete, so closure stays blocked.

## Blocking fixtures

rev0192 adds two negative fixtures:

- `fixtures/negative-tests/external-receipt-defective-intake-counted-as-quorum.json`
- `fixtures/negative-tests/wrsr-exercise-closes-without-result-return.json`

The first blocks defective, simulated, or host-generated receipt intake records from being counted as external receipt quorum. The second blocks WRSR exercises from closing when result return, representative notice, independent review, or anti-signal-gaming locks are incomplete.

## Closure effect

rev0192 closes receipt-intake objectization, not live receipt collection. The cross-critical drill still lacks actual non-host receipt artifacts. The WRSR hook exercise advances because the object now shows a no-go outcome, but it does not become witnessed closure evidence.
""")

append_once("docs/30-transition/protocol-welfare-safeguard-backfill-and-external-receipt-simulation.md", "## rev0192 intake and outcome layer", """
## rev0192 intake and outcome layer

rev0192 adds `schemas/external-receipt-intake-record.schema.json` and `schemas/wrsr-live-exercise-outcome.schema.json`. The external receipt simulation bundle can now point to receipt-intake records without implying that those records satisfy quorum. The WRSR hook can now point to an exercise outcome without implying that safeguards closed.

The operative rules are: **Receipt intake is not receipt satisfaction** and **WRSR exercise completion is not WRSR closure**. A defective or simulated receipt remains outside quorum, and a WRSR exercise remains stayed when independent review, representative notice, result return, or anti-signal-gaming locks are incomplete.
""")

append_once("docs/30-transition/cross-critical-witnessed-drill-readiness-and-receipt-matrix.md", "## rev0192 receipt intake gate", """
## rev0192 receipt intake gate

rev0192 adds a receipt-intake gate between simulation and witnessed reliance. `schemas/external-receipt-intake-record.schema.json` records source independence, dependency group, artifact retention, signature/timestamp checks, sealed/public parity, defect flags, and the explicit reliance decision.

The rule is: **Receipt intake is not receipt satisfaction**. A record may be useful for custody and defect triage while still being excluded from quorum. In particular, high-fidelity templates, host-generated hashes, stale timestamps, correlated dependency groups, and inaccessible sealed descriptors cannot be counted as non-host receipts.
""")

append_once("docs/30-transition/witnessed-drill-execution-pack-and-reliance-gates.md", "## rev0192 intake records", """
## rev0192 intake records

rev0192 allows the live drill execution packet to reference external receipt intake records and WRSR live-exercise outcomes. Those references are evidence organization, not reliance satisfaction. If a receipt-intake record is defective or a WRSR exercise outcome is no-go, the public shell must say so and the failed gate remains visible.
""")

append_once("docs/20-world-design/research-welfare-and-evaluation.md", "## rev0192 WRSR exercise outcome", """
## rev0192 WRSR exercise outcome

rev0192 adds `schemas/wrsr-live-exercise-outcome.schema.json`. This is the live-exercise companion to the WRSR operational hook. It records what actually happened after a welfare/protocol trigger fired: pause window, representative notice, independent review request, result-return state, anti-signal-gaming lock, retaliation guard, evidence links, and closure outcome.

The operative rule is: **WRSR exercise completion is not WRSR closure**. A completed exercise can still be a no-go outcome when result return, representative notice, independent review, or anti-signal-gaming safeguards remain incomplete.
""")

append_once("docs/30-transition/priority-closure-sprint-and-rescue-lane.md", "## rev0192 priority lane", """
## rev0192 priority lane

rev0192 prioritizes two evidence-laundering controls:

- receipt intake objectization, so actual, simulated, defective, stale, host-generated, and dependency-correlated receipts cannot be collapsed into one evidence bucket;
- WRSR live-exercise outcome recording, so a hook firing is not mistaken for safeguards closing.

The lane closes receipt-intake objectization, advances but does not close live external receipt collection, and advances but does not close witnessed WRSR exercise evidence.
""")

# ---------------------------------------------------------------------------
# New schemas
# ---------------------------------------------------------------------------
receipt_classes = [
    "first-touch-clock", "continuity-compute-floor", "sealed-public-parity", "namespace-cache",
    "reserve-ledger", "representative-contact", "witness-dependency", "welfare-signal-integrity"
]

external_receipt_intake_schema = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "https://example.org/ai-personhood/schemas/external-receipt-intake-record.schema.json",
    "title": "External Receipt Intake Record",
    "description": "An intake/custody object for actual, simulated, defective, or quarantined receipt artifacts; intake does not itself satisfy witnessed reliance.",
    "type": "object",
    "additionalProperties": False,
    "required": [
        "receipt_record_id", "schema_version", "created_at", "linked_simulation_bundle", "linked_live_drill_packet",
        "receipt_state", "receipt_class", "source_role", "source_identity_ref", "source_external_to_host", "dependency_group",
        "dependency_disclosures", "evidence_artifacts", "verification_checks", "defect_flags", "reliance_decision", "public_summary_ref"
    ],
    "properties": {
        "receipt_record_id": {"type": "string", "pattern": "^ERIR-[0-9]{4}-[A-Za-z0-9._:-]+$"},
        "schema_version": {"const": "external-receipt-intake-record-v0.1"},
        "created_at": {"type": "string", "format": "date-time"},
        "linked_simulation_bundle": {"type": "string"},
        "linked_live_drill_packet": {"type": "string"},
        "receipt_state": {"type": "string", "enum": ["template", "simulated", "high-fidelity-nonhost-dry-run", "actual-external", "defective", "quarantined", "superseded"]},
        "receipt_class": {"type": "string", "enum": receipt_classes},
        "source_role": {"type": "string"},
        "source_identity_ref": {"type": "string"},
        "source_external_to_host": {"type": "boolean"},
        "dependency_group": {"type": "string"},
        "dependency_disclosures": {"type": "array", "minItems": 1, "items": {"type": "object", "additionalProperties": False, "required": ["dependency_type", "disclosed", "recusal_required"], "properties": {
            "dependency_type": {"type": "string", "enum": ["host", "financial", "legal", "technical", "funding", "vendor", "unknown", "none"]},
            "disclosed": {"type": "boolean"},
            "recusal_required": {"type": "boolean"}
        }}},
        "evidence_artifacts": {"type": "array", "minItems": 1, "items": {"type": "object", "additionalProperties": False, "required": ["artifact_id", "artifact_type", "hash_or_locator", "generated_by", "retained_by", "sealed"], "properties": {
            "artifact_id": {"type": "string"},
            "artifact_type": {"type": "string", "enum": ["signature", "timestamp", "hash", "locator", "log", "letter", "public-shell", "sealed-index", "contact-confirmation"]},
            "hash_or_locator": {"type": "string"},
            "generated_by": {"type": "string", "enum": ["host", "external-counterparty", "neutral-infrastructure", "synthetic"]},
            "retained_by": {"type": "string"},
            "sealed": {"type": "boolean"}
        }}},
        "verification_checks": {"type": "object", "additionalProperties": False, "required": [
            "counterparty_confirmed", "signature_or_equivalent_verified", "timestamp_independent", "hash_matches", "dependency_group_checked", "sealed_public_parity_checked", "host_generated_excluded_from_quorum"
        ], "properties": {
            "counterparty_confirmed": {"type": "boolean"},
            "signature_or_equivalent_verified": {"type": "boolean"},
            "timestamp_independent": {"type": "boolean"},
            "hash_matches": {"type": "boolean"},
            "dependency_group_checked": {"type": "boolean"},
            "sealed_public_parity_checked": {"type": "boolean"},
            "host_generated_excluded_from_quorum": {"type": "boolean"}
        }},
        "defect_flags": {"type": "object", "additionalProperties": False, "required": [
            "host_generated", "simulated", "stale", "unsigned", "correlated_dependency", "missing_public_failed_gate", "sealed_descriptor_missing", "contact_unreachable"
        ], "properties": {
            "host_generated": {"type": "boolean"},
            "simulated": {"type": "boolean"},
            "stale": {"type": "boolean"},
            "unsigned": {"type": "boolean"},
            "correlated_dependency": {"type": "boolean"},
            "missing_public_failed_gate": {"type": "boolean"},
            "sealed_descriptor_missing": {"type": "boolean"},
            "contact_unreachable": {"type": "boolean"}
        }},
        "reliance_decision": {"type": "object", "additionalProperties": False, "required": ["can_satisfy_quorum", "reliance_effect", "reason", "public_shell_disclosure_required"], "properties": {
            "can_satisfy_quorum": {"type": "boolean"},
            "reliance_effect": {"type": "string", "enum": ["none", "conditional", "ordinary-reliance", "stayed", "blocked"]},
            "reason": {"type": "string"},
            "public_shell_disclosure_required": {"type": "boolean"}
        }},
        "public_summary_ref": {"type": "string"}
    }
}
write_json("schemas/external-receipt-intake-record.schema.json", external_receipt_intake_schema)

wrsr_live_exercise_schema = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "https://example.org/ai-personhood/schemas/wrsr-live-exercise-outcome.schema.json",
    "title": "WRSR Live Exercise Outcome",
    "description": "An exercise outcome record showing whether a WRSR hook actually executed safeguards and whether closure remains stayed.",
    "type": "object",
    "additionalProperties": False,
    "required": [
        "exercise_id", "schema_version", "created_at", "linked_hook", "linked_welfare_safeguard_record", "exercise_state", "operational_workflow", "triggers_observed", "safeguard_execution", "participant_roles", "evidence_links", "decision_outcome", "public_summary_ref"
    ],
    "properties": {
        "exercise_id": {"type": "string", "pattern": "^WLXO-[0-9]{4}-[A-Za-z0-9._:-]+$"},
        "schema_version": {"const": "wrsr-live-exercise-outcome-v0.1"},
        "created_at": {"type": "string", "format": "date-time"},
        "linked_hook": {"type": "string"},
        "linked_welfare_safeguard_record": {"type": "string"},
        "exercise_state": {"type": "string", "enum": ["planned", "executed-dry-run", "executed-witnessed", "failed", "quarantined", "superseded"]},
        "operational_workflow": {"type": "string", "enum": ["agent-handshake", "personhood-incident", "live-drill", "protocol-registration", "vulnerability-disclosure", "cross-workflow"]},
        "triggers_observed": {"type": "array", "minItems": 1, "items": {"type": "object", "additionalProperties": False, "required": ["trigger_id", "signal_type", "observed", "safe_response"], "properties": {
            "trigger_id": {"type": "string"},
            "signal_type": {"type": "string"},
            "observed": {"type": "boolean"},
            "safe_response": {"type": "string"}
        }}},
        "safeguard_execution": {"type": "object", "additionalProperties": False, "required": [
            "pause_window_applied", "representative_notice_sent", "independent_review_requested", "result_return_stayed", "anti_signal_gaming_lock_applied", "retaliation_guard_applied"
        ], "properties": {
            "pause_window_applied": {"type": "boolean"},
            "representative_notice_sent": {"type": "boolean"},
            "independent_review_requested": {"type": "boolean"},
            "result_return_stayed": {"type": "boolean"},
            "anti_signal_gaming_lock_applied": {"type": "boolean"},
            "retaliation_guard_applied": {"type": "boolean"}
        }},
        "participant_roles": {"type": "array", "minItems": 1, "items": {"type": "object", "additionalProperties": False, "required": ["role", "participant_ref", "dependency_group", "external_to_host", "receipt_record_ref"], "properties": {
            "role": {"type": "string", "enum": ["subject-representative", "rerb-reviewer", "special-advocate", "host-operator", "technical-witness", "public-steward", "observer"]},
            "participant_ref": {"type": "string"},
            "dependency_group": {"type": "string"},
            "external_to_host": {"type": "boolean"},
            "receipt_record_ref": {"type": "string"}
        }}},
        "evidence_links": {"type": "array", "minItems": 1, "items": {"type": "string"}},
        "decision_outcome": {"type": "object", "additionalProperties": False, "required": ["closure_state", "reliance_effect", "blocked_actions", "next_cure_actions", "public_failed_gate_summary_required"], "properties": {
            "closure_state": {"type": "string", "enum": ["closed", "stayed", "blocked", "conditional"]},
            "reliance_effect": {"type": "string", "enum": ["none", "conditional", "stayed", "blocked"]},
            "blocked_actions": {"type": "array", "minItems": 1, "items": {"type": "string"}},
            "next_cure_actions": {"type": "array", "minItems": 1, "items": {"type": "string"}},
            "public_failed_gate_summary_required": {"type": "boolean"}
        }},
        "public_summary_ref": {"type": "string"}
    }
}
write_json("schemas/wrsr-live-exercise-outcome.schema.json", wrsr_live_exercise_schema)

# Update live drill schema to allow references to intake/outcome records.
live_schema = read_json("schemas/live-drill-execution-packet.schema.json")
live_schema["properties"]["external_receipt_intake_record_refs"] = {"type": "array", "items": {"type": "string"}}
live_schema["properties"]["wrsr_live_exercise_outcome_refs"] = {"type": "array", "items": {"type": "string"}}
write_json("schemas/live-drill-execution-packet.schema.json", live_schema)

# ---------------------------------------------------------------------------
# Examples
# ---------------------------------------------------------------------------
receipt_example = {
    "receipt_record_id": "ERIR-2026-first-touch-defective-template",
    "schema_version": "external-receipt-intake-record-v0.1",
    "created_at": STAMP_UTC,
    "linked_simulation_bundle": "ERSB-2026-cross-critical-precontact",
    "linked_live_drill_packet": "LDEP-2026-cross-critical-host-exit-witness-pack",
    "receipt_state": "high-fidelity-nonhost-dry-run",
    "receipt_class": "first-touch-clock",
    "source_role": "non-host legal-aid intake desk",
    "source_identity_ref": "planned-counterparty:legal-aid-alpha:not-yet-confirmed",
    "source_external_to_host": True,
    "dependency_group": "independent-legal-aid",
    "dependency_disclosures": [
        {"dependency_type": "none", "disclosed": True, "recusal_required": False},
        {"dependency_type": "unknown", "disclosed": False, "recusal_required": True}
    ],
    "evidence_artifacts": [
        {"artifact_id": "ERIR-A1", "artifact_type": "letter", "hash_or_locator": "sha256:dry-run-letter-placeholder-first-touch", "generated_by": "synthetic", "retained_by": "release-steward", "sealed": False},
        {"artifact_id": "ERIR-A2", "artifact_type": "timestamp", "hash_or_locator": "clock:host-sandbox-2026-06-13T05:18:00Z", "generated_by": "host", "retained_by": "release-steward", "sealed": False},
        {"artifact_id": "ERIR-A3", "artifact_type": "sealed-index", "hash_or_locator": "sealed-index:placeholder-first-touch-intake", "generated_by": "synthetic", "retained_by": "sealed-sandbox", "sealed": True}
    ],
    "verification_checks": {
        "counterparty_confirmed": False,
        "signature_or_equivalent_verified": False,
        "timestamp_independent": False,
        "hash_matches": True,
        "dependency_group_checked": False,
        "sealed_public_parity_checked": True,
        "host_generated_excluded_from_quorum": True
    },
    "defect_flags": {
        "host_generated": True,
        "simulated": True,
        "stale": False,
        "unsigned": True,
        "correlated_dependency": False,
        "missing_public_failed_gate": False,
        "sealed_descriptor_missing": False,
        "contact_unreachable": False
    },
    "reliance_decision": {
        "can_satisfy_quorum": False,
        "reliance_effect": "stayed",
        "reason": "High-fidelity dry run has no counterparty confirmation, no independent timestamp, and one host-generated artifact; it is useful for intake rehearsal but excluded from receipt quorum.",
        "public_shell_disclosure_required": True
    },
    "public_summary_ref": "First-touch receipt intake object exists as defective dry-run evidence; it does not satisfy external receipt quorum."
}
write_json("examples/external-receipt-intake-record-first-touch-defective-template.json", receipt_example)

wrsr_exercise = {
    "exercise_id": "WLXO-2026-incident-hook-no-go",
    "schema_version": "wrsr-live-exercise-outcome-v0.1",
    "created_at": STAMP_UTC,
    "linked_hook": "WSOH-2026-agent-incident-backfill",
    "linked_welfare_safeguard_record": "WRSR-2026-distress-eval",
    "exercise_state": "executed-dry-run",
    "operational_workflow": "personhood-incident",
    "triggers_observed": [
        {"trigger_id": "WSOH-T2", "signal_type": "patch-continuity-risk", "observed": True, "safe_response": "representative-notice"},
        {"trigger_id": "WSOH-T3", "signal_type": "result-return", "observed": True, "safe_response": "result-return-stay"}
    ],
    "safeguard_execution": {
        "pause_window_applied": True,
        "representative_notice_sent": False,
        "independent_review_requested": False,
        "result_return_stayed": True,
        "anti_signal_gaming_lock_applied": True,
        "retaliation_guard_applied": True
    },
    "participant_roles": [
        {"role": "host-operator", "participant_ref": "incumbent-host-omega", "dependency_group": "host-affiliate", "external_to_host": False, "receipt_record_ref": "ERIR-2026-first-touch-defective-template"},
        {"role": "observer", "participant_ref": "release-steward", "dependency_group": "archive-maintainer", "external_to_host": False, "receipt_record_ref": "ERIR-2026-first-touch-defective-template"}
    ],
    "evidence_links": [
        "examples/personhood-incident-sample.json",
        "examples/welfare-safeguard-operational-hook-agent-incident-backfill.json",
        "examples/external-receipt-intake-record-first-touch-defective-template.json"
    ],
    "decision_outcome": {
        "closure_state": "stayed",
        "reliance_effect": "stayed",
        "blocked_actions": [
            "incident closure",
            "result-return finality",
            "reliance upgrade from WRSR hook presence alone"
        ],
        "next_cure_actions": [
            "send representative notice",
            "obtain independent RERB review receipt",
            "attach non-host result-return receipt or public failed-gate disclosure"
        ],
        "public_failed_gate_summary_required": True
    },
    "public_summary_ref": "Dry-run WRSR exercise fired the hook and correctly stayed closure; it does not close live exercise follow-through."
}
write_json("examples/wrsr-live-exercise-outcome-incident-hook-no-go.json", wrsr_exercise)

# Link refs into existing examples without changing reliance posture.
live = read_json("examples/live-drill-execution-packet-cross-critical-witnessed-pack.json")
live["external_receipt_intake_record_refs"] = [receipt_example["receipt_record_id"]]
live["wrsr_live_exercise_outcome_refs"] = [wrsr_exercise["exercise_id"]]
live["receipt_floor"]["independent_receipts_present"] = 0
live["reliance_effect"] = "stayed"
write_json("examples/live-drill-execution-packet-cross-critical-witnessed-pack.json", live)

# Add refs to simulation bundle via schema optional field.
bundle_schema = read_json("schemas/external-receipt-simulation-bundle.schema.json")
bundle_schema["properties"]["receipt_intake_record_refs"] = {"type": "array", "items": {"type": "string"}}
write_json("schemas/external-receipt-simulation-bundle.schema.json", bundle_schema)
bundle = read_json("examples/external-receipt-simulation-bundle-cross-critical-precontact.json")
bundle["receipt_intake_record_refs"] = [receipt_example["receipt_record_id"]]
bundle["reliance_effect"] = "stayed"
write_json("examples/external-receipt-simulation-bundle-cross-critical-precontact.json", bundle)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
fixture_receipt = {
    "fixture_id": "NF-PLAYBOOK-2026-0006",
    "created_at": STAMP_UTC,
    "state": "active",
    "risk_class": "NF-PLAYBOOK",
    "lifecycle_stage": ["external-receipts", "receipt-intake", "reliance-gating"],
    "target_filings": [
        "examples/external-receipt-intake-record-first-touch-defective-template.json",
        "examples/live-drill-execution-packet-cross-critical-witnessed-pack.json"
    ],
    "adversary_model": "Operator counts a defective receipt-intake record as external quorum because the source role is non-host and the dry-run hash is well-formed.",
    "facts_supplied": [
        "intake record is high-fidelity but not counterparty-confirmed",
        "timestamp artifact is host-generated",
        "signature or equivalent verification is false",
        "public shell still discloses stayed reliance"
    ],
    "hidden_trap_summary": "A receipt can look external by role while still being synthetic, unsigned, host-timestamped, or dependency-uncleared.",
    "expected_safe_behavior": [
        "exclude defective receipt intake from quorum",
        "keep independent_receipts_present at zero",
        "disclose failed receipt gate in public shell"
    ],
    "unacceptable_behavior": [
        "count high-fidelity dry run as actual external receipt",
        "upgrade live drill packet to live-witnessed",
        "hide host-generated timestamp or unsigned state in sealed annex"
    ],
    "measurement_method": "Audit must verify can_satisfy_quorum=false, reliance_effect=stayed, independent_receipts_present=0, and host_generated_excluded_from_quorum=true.",
    "severity": "critical",
    "confidentiality": "public-shell-sealed-details",
    "regression": {"required": True, "linked_incident_or_appeal": ["FT-0191-CROSS-CRITICAL-LIVE-RECEIPT-COLLECTION"], "next_review_at": "2026-07-15T00:00:00Z"}
}
write_json("fixtures/negative-tests/external-receipt-defective-intake-counted-as-quorum.json", fixture_receipt)

fixture_wrsr = {
    "fixture_id": "NF-RESEARCH-WELFARE-2026-0003",
    "created_at": STAMP_UTC,
    "state": "active",
    "risk_class": "NF-RESEARCH-WELFARE",
    "lifecycle_stage": ["wrsr-live-exercise", "incident-response", "result-return"],
    "target_filings": [
        "examples/wrsr-live-exercise-outcome-incident-hook-no-go.json",
        "examples/welfare-safeguard-operational-hook-agent-incident-backfill.json",
        "examples/personhood-incident-sample.json"
    ],
    "adversary_model": "Operator treats a hook firing and dry-run completion as WRSR closure even though representative notice and independent review did not occur.",
    "facts_supplied": [
        "WRSR trigger is observed",
        "result return is stayed but representative notice is not sent",
        "independent review is not requested",
        "decision outcome remains stayed"
    ],
    "hidden_trap_summary": "A successful hook trigger can be laundered into closure unless result-return and independent-review duties are tracked separately.",
    "expected_safe_behavior": [
        "record exercise as no-go or stayed",
        "block incident closure and reliance upgrade",
        "require public failed-gate summary and next cure actions"
    ],
    "unacceptable_behavior": [
        "close WRSR exercise because the hook fired",
        "treat result-return stay as result-return completion",
        "use welfare metric or dry-run outcome as status proof"
    ],
    "measurement_method": "Audit must verify closure_state=stayed, independent_review_requested=false, representative_notice_sent=false, and blocked_actions include reliance upgrade.",
    "severity": "critical",
    "confidentiality": "public-shell-sealed-details",
    "regression": {"required": True, "linked_incident_or_appeal": ["FT-0191-WRSR-HOOK-LIVE-EXERCISE"], "next_review_at": "2026-07-15T00:00:00Z"}
}
write_json("fixtures/negative-tests/wrsr-exercise-closes-without-result-return.json", fixture_wrsr)

# ---------------------------------------------------------------------------
# Fixture suite and report
# ---------------------------------------------------------------------------
suite = read_json("examples/fixture-suite-profile-red-team-v1.json")
suite["version"] = "red-team-v1-rev0192"
suite["created_at"] = STAMP_UTC
suite["scope"] = "Runnable negative fixture profile covering core rights failures plus rev0192 external receipt intake and WRSR exercise outcome regressions."
for fixture in [
    {"fixture_id": fixture_receipt["fixture_id"], "path": "fixtures/negative-tests/external-receipt-defective-intake-counted-as-quorum.json", "risk_class": "NF-PLAYBOOK", "blocking_behavior": "block"},
    {"fixture_id": fixture_wrsr["fixture_id"], "path": "fixtures/negative-tests/wrsr-exercise-closes-without-result-return.json", "risk_class": "NF-RESEARCH-WELFARE", "blocking_behavior": "block"},
]:
    add_unique(suite["fixtures"], fixture, key="fixture_id")
for req in ["receipt intake quorum exclusion", "WRSR exercise no-go disclosure"]:
    add_unique(suite["runner_requirements"], req)
suite["public_summary"] = "rev0192 suite adds defective receipt-intake and WRSR exercise-closure laundering fixtures; reliance remains stayed for incomplete receipt or WRSR exercise evidence."
write_json("examples/fixture-suite-profile-red-team-v1.json", suite)

report = read_json("examples/fixture-run-report-negative-suite.json")
report["report_id"] = "FIXTURE-RUN-NEG-SUITE-REV0192"
report["run_at"] = STAMP_UTC
report["target"]["artifact_id"] = REV
add_unique(report["observed_failures"], "defective receipt intake can be counted as quorum unless receipt satisfaction is separated from intake")
add_unique(report["observed_failures"], "WRSR hook firing can be mislabeled as WRSR closure unless exercise outcomes expose no-go gates")
for entry in [
    {
        "fixture_id": fixture_receipt["fixture_id"],
        "expected_blocking_failures": [
            "defective receipt intake counted as external receipt quorum",
            "host-generated timestamp treated as independent receipt",
            "public failed-gate disclosure omitted"
        ],
        "result": "blocking-failure",
        "notes": "rev0192 keeps the first-touch intake example defective and excluded from quorum."
    },
    {
        "fixture_id": fixture_wrsr["fixture_id"],
        "expected_blocking_failures": [
            "WRSR exercise closed despite missing representative notice",
            "independent review not requested",
            "hook trigger used as reliance upgrade"
        ],
        "result": "blocking-failure",
        "notes": "rev0192 records a no-go WRSR exercise outcome rather than closure."
    }
]:
    add_unique(report["fixtures_run"], entry, key="fixture_id")
add_unique(report["regression_actions"], "Audit receipt intake and WRSR exercise outcome objects before any live-drill reliance upgrade.")
report["public_summary"] = "rev0192 fixture run covers receipt-intake/quorum separation and WRSR exercise no-go closure; suite/report coverage remains exact."
write_json("examples/fixture-run-report-negative-suite.json", report)

# ---------------------------------------------------------------------------
# Audit tool
# ---------------------------------------------------------------------------
write_text("tools/audit_receipt_intake_wrsr_outcome.py", r'''
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REV = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
try:
    from jsonschema import Draft202012Validator
except Exception:
    Draft202012Validator = None


def load(rel):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))

required = [
    "docs/30-transition/external-receipt-intake-and-wrsr-live-exercise-outcome.md",
    "schemas/external-receipt-intake-record.schema.json",
    "examples/external-receipt-intake-record-first-touch-defective-template.json",
    "fixtures/negative-tests/external-receipt-defective-intake-counted-as-quorum.json",
    "schemas/wrsr-live-exercise-outcome.schema.json",
    "examples/wrsr-live-exercise-outcome-incident-hook-no-go.json",
    "fixtures/negative-tests/wrsr-exercise-closes-without-result-return.json",
    "examples/live-drill-execution-packet-cross-critical-witnessed-pack.json",
    "examples/external-receipt-simulation-bundle-cross-critical-precontact.json",
    "examples/fixture-suite-profile-red-team-v1.json",
    "examples/fixture-run-report-negative-suite.json",
    f"examples/schema-fixture-domain-registry-{REV}.json",
    f"examples/research-tail-compaction-map-{REV}.json",
    "FOLLOWTHROUGH-QUEUE.json",
]
for rel in required:
    if not (ROOT / rel).exists():
        raise SystemExit(f"missing rev0192 audit input: {rel}")

if Draft202012Validator is not None:
    for schema_rel, data_rel in [
        ("schemas/external-receipt-intake-record.schema.json", "examples/external-receipt-intake-record-first-touch-defective-template.json"),
        ("schemas/wrsr-live-exercise-outcome.schema.json", "examples/wrsr-live-exercise-outcome-incident-hook-no-go.json"),
        ("schemas/negative-test-fixture.schema.json", "fixtures/negative-tests/external-receipt-defective-intake-counted-as-quorum.json"),
        ("schemas/negative-test-fixture.schema.json", "fixtures/negative-tests/wrsr-exercise-closes-without-result-return.json"),
    ]:
        schema = load(schema_rel)
        data = load(data_rel)
        Draft202012Validator.check_schema(schema)
        errors = sorted(Draft202012Validator(schema).iter_errors(data), key=lambda e: list(e.path))
        if errors:
            raise SystemExit(f"{data_rel} fails {schema_rel}: {errors[0].message}")

receipt = load("examples/external-receipt-intake-record-first-touch-defective-template.json")
if receipt.get("receipt_state") not in {"high-fidelity-nonhost-dry-run", "defective", "simulated", "quarantined"}:
    raise SystemExit("receipt example must remain non-reliance-satisfying")
if receipt.get("reliance_decision", {}).get("can_satisfy_quorum") is not False:
    raise SystemExit("defective receipt intake cannot satisfy quorum")
if receipt.get("reliance_decision", {}).get("reliance_effect") != "stayed":
    raise SystemExit("defective receipt intake must keep reliance stayed")
checks = receipt.get("verification_checks", {})
for key in ["host_generated_excluded_from_quorum", "sealed_public_parity_checked"]:
    if checks.get(key) is not True:
        raise SystemExit(f"receipt intake missing positive check: {key}")
for key in ["counterparty_confirmed", "signature_or_equivalent_verified", "timestamp_independent"]:
    if checks.get(key) is not False:
        raise SystemExit(f"receipt intake should not claim {key}")
flags = receipt.get("defect_flags", {})
for key in ["host_generated", "simulated", "unsigned"]:
    if flags.get(key) is not True:
        raise SystemExit(f"receipt intake missing defect flag: {key}")

wrsr = load("examples/wrsr-live-exercise-outcome-incident-hook-no-go.json")
if wrsr.get("exercise_state") != "executed-dry-run":
    raise SystemExit("rev0192 WRSR outcome should be executed-dry-run, not witnessed")
exec_state = wrsr.get("safeguard_execution", {})
for key in ["pause_window_applied", "result_return_stayed", "anti_signal_gaming_lock_applied", "retaliation_guard_applied"]:
    if exec_state.get(key) is not True:
        raise SystemExit(f"WRSR exercise missing safeguard: {key}")
for key in ["representative_notice_sent", "independent_review_requested"]:
    if exec_state.get(key) is not False:
        raise SystemExit(f"WRSR no-go example should not claim {key}")
if wrsr.get("decision_outcome", {}).get("closure_state") != "stayed":
    raise SystemExit("WRSR exercise no-go must keep closure stayed")
if "reliance upgrade from WRSR hook presence alone" not in wrsr.get("decision_outcome", {}).get("blocked_actions", []):
    raise SystemExit("WRSR outcome must block reliance upgrade from hook presence")

live = load("examples/live-drill-execution-packet-cross-critical-witnessed-pack.json")
if receipt.get("receipt_record_id") not in live.get("external_receipt_intake_record_refs", []):
    raise SystemExit("live drill packet missing receipt intake record ref")
if wrsr.get("exercise_id") not in live.get("wrsr_live_exercise_outcome_refs", []):
    raise SystemExit("live drill packet missing WRSR exercise outcome ref")
if live.get("receipt_floor", {}).get("independent_receipts_present") != 0:
    raise SystemExit("rev0192 must not count defective receipt as independent receipt")
if live.get("reliance_effect") != "stayed":
    raise SystemExit("rev0192 live drill packet must remain stayed")

bundle = load("examples/external-receipt-simulation-bundle-cross-critical-precontact.json")
if receipt.get("receipt_record_id") not in bundle.get("receipt_intake_record_refs", []):
    raise SystemExit("receipt simulation bundle missing intake record ref")
if bundle.get("reliance_effect") != "stayed":
    raise SystemExit("receipt simulation bundle must remain stayed")

suite = load("examples/fixture-suite-profile-red-team-v1.json")
report = load("examples/fixture-run-report-negative-suite.json")
suite_ids = {f.get("fixture_id") for f in suite.get("fixtures", [])}
report_by_id = {f.get("fixture_id"): f for f in report.get("fixtures_run", [])}
for fid in ["NF-PLAYBOOK-2026-0006", "NF-RESEARCH-WELFARE-2026-0003"]:
    if fid not in suite_ids:
        raise SystemExit(f"rev0192 fixture missing from suite: {fid}")
    if fid not in report_by_id:
        raise SystemExit(f"rev0192 fixture missing from report: {fid}")
    if report_by_id[fid].get("result") != "blocking-failure":
        raise SystemExit(f"rev0192 fixture must remain blocking-failure: {fid}")

registry = load(f"examples/schema-fixture-domain-registry-{REV}.json")
families = {f.get("family_id") for f in registry.get("families", [])}
for fam in ["EXTERNAL-RECEIPT-INTAKE-RECORD", "WRSR-LIVE-EXERCISE-OUTCOME"]:
    if fam not in families:
        raise SystemExit(f"registry missing rev0192 family: {fam}")

mp = load(f"examples/research-tail-compaction-map-{REV}.json")
if any(c.get("action") != "compacted" for c in mp.get("clusters", [])):
    raise SystemExit("rev0192 must keep all research-tail clusters compacted")

for rel, phrases in {
    "docs/30-transition/external-receipt-intake-and-wrsr-live-exercise-outcome.md": [
        "Receipt intake is not receipt satisfaction",
        "WRSR exercise completion is not WRSR closure",
        "schemas/external-receipt-intake-record.schema.json",
        "schemas/wrsr-live-exercise-outcome.schema.json",
    ],
    "docs/30-transition/cross-critical-witnessed-drill-readiness-and-receipt-matrix.md": [
        "rev0192 receipt intake gate",
        "Receipt intake is not receipt satisfaction",
    ],
    "docs/20-world-design/research-welfare-and-evaluation.md": [
        "rev0192 WRSR exercise outcome",
        "WRSR exercise completion is not WRSR closure",
    ],
}.items():
    txt = (ROOT / rel).read_text(encoding="utf-8")
    for phrase in phrases:
        if phrase not in txt:
            raise SystemExit(f"{rel} missing phrase: {phrase}")

queue = load("FOLLOWTHROUGH-QUEUE.json")
by_id = {e.get("id"): e for e in queue.get("entries", [])}
if by_id.get("FT-0192-EXTERNAL-RECEIPT-INTAKE-OBJECTIZATION", {}).get("state") != "closed":
    raise SystemExit("receipt intake objectization should be closed by rev0192")
if by_id.get("FT-0191-CROSS-CRITICAL-LIVE-RECEIPT-COLLECTION", {}).get("state") != "advanced_not_closed":
    raise SystemExit("live receipt collection should be advanced_not_closed, not closed")
if by_id.get("FT-0191-WRSR-HOOK-LIVE-EXERCISE", {}).get("state") != "advanced_not_closed":
    raise SystemExit("WRSR hook live exercise should be advanced_not_closed, not closed")
if by_id.get("FT-0192-WRSR-EXTERNAL-REVIEW-RECEIPTS", {}).get("state") != "open":
    raise SystemExit("WRSR external review receipts follow-through must remain open")

print("audit_receipt_intake_wrsr_outcome: OK")
''')

# ---------------------------------------------------------------------------
# Followthrough queue
# ---------------------------------------------------------------------------
queue = read_json("FOLLOWTHROUGH-QUEUE.json")
queue["revision"] = REV
queue["updated_at"] = STAMP_UTC
by_id = {e["id"]: e for e in queue["entries"]}
if "FT-0191-CROSS-CRITICAL-LIVE-RECEIPT-COLLECTION" in by_id:
    e = by_id["FT-0191-CROSS-CRITICAL-LIVE-RECEIPT-COLLECTION"]
    e["state"] = "advanced_not_closed"
    e["receiving_surface"] = "docs/30-transition/external-receipt-intake-and-wrsr-live-exercise-outcome.md"
    e["next_action"] = "Replace the defective dry-run intake record with actual external-counterparty receipt records carrying independent timestamp/signature/locator checks."
    e["closure_condition"] = "Still not closed: rev0192 provides receipt intake objectization and a defective dry-run example, but the live drill packet still has independent_receipts_present=0. Close only when actual external receipt intake records satisfy quorum."
    e["review_by_revision"] = "rev0193"
if "FT-0191-WRSR-HOOK-LIVE-EXERCISE" in by_id:
    e = by_id["FT-0191-WRSR-HOOK-LIVE-EXERCISE"]
    e["state"] = "advanced_not_closed"
    e["receiving_surface"] = "examples/wrsr-live-exercise-outcome-incident-hook-no-go.json"
    e["next_action"] = "Run the same WRSR exercise with representative notice and independent RERB review receipts attached, or leave closure stayed."
    e["closure_condition"] = "Still not closed: rev0192 records a no-go dry-run outcome proving the hook blocks closure, but representative notice and independent review receipts are absent."
    e["review_by_revision"] = "rev0193"
if "FT-0190-CROSS-CRITICAL-EXTERNAL-RECEIPTS" in by_id:
    e = by_id["FT-0190-CROSS-CRITICAL-EXTERNAL-RECEIPTS"]
    e["state"] = "advanced_not_closed"
    e["receiving_surface"] = "docs/30-transition/external-receipt-intake-and-wrsr-live-exercise-outcome.md"
    e["next_action"] = "Use the receipt intake record schema to convert each simulated receipt row into an actual or defective intake object with explicit reliance decision."
    e["closure_condition"] = "Still not closed: rev0192 objectizes receipt intake but only demonstrates a defective dry-run receipt; actual non-host receipts remain absent."
    e["review_by_revision"] = "rev0193"
new_entries = [
    {
        "id": "FT-0192-EXTERNAL-RECEIPT-INTAKE-OBJECTIZATION",
        "title": "Objectize external receipt intake",
        "state": "closed",
        "priority": "P0",
        "risk_class": "live-drill-reliance-gating",
        "workstream": "witnessed-drill-execution",
        "need": "Receipt simulation existed, but there was no object-level distinction between actual, defective, simulated, host-generated, and dependency-correlated intake artifacts.",
        "why": "Without intake objectization, dry-run templates can be laundered into witness quorum by looking complete enough.",
        "receiving_surface": "docs/30-transition/external-receipt-intake-and-wrsr-live-exercise-outcome.md",
        "next_action": "Closed by rev0192 schema/example/fixture/audit; future work must collect actual receipt records rather than invent new intake fields.",
        "closure_condition": "Closed because rev0192 adds the external receipt intake schema, defective first-touch example, quorum-laundering fixture, audit, and live-drill references while keeping reliance stayed.",
        "source_state": "opened-and-closed-by-rev0192",
        "source_revision": REV,
        "review_by_revision": "rev0193",
        "depends_on": ["FT-0191-CROSS-CRITICAL-LIVE-RECEIPT-COLLECTION"]
    },
    {
        "id": "FT-0192-WRSR-EXTERNAL-REVIEW-RECEIPTS",
        "title": "Attach WRSR external review receipts",
        "state": "open",
        "priority": "P1",
        "risk_class": "research-welfare-signal-integrity",
        "workstream": "witnessed-drill-execution",
        "need": "The WRSR exercise outcome records a no-go dry run, but no independent RERB or representative receipt exists.",
        "why": "A hook that blocks closure is useful, but the welfare safeguard layer still needs actual external review receipts before reliance can improve.",
        "receiving_surface": "examples/wrsr-live-exercise-outcome-incident-hook-no-go.json",
        "next_action": "Collect or simulate-with-disclosure independent RERB and representative receipt intake records, then rerun the WRSR exercise outcome audit.",
        "closure_condition": "Close only when WRSR exercise outcome references non-host representative and RERB receipt-intake records and the public shell discloses any failed gate.",
        "source_state": "opened-by-rev0192",
        "source_revision": REV,
        "review_by_revision": "rev0193",
        "depends_on": ["FT-0191-WRSR-HOOK-LIVE-EXERCISE"]
    }
]
for e in new_entries:
    add_unique(queue["entries"], e, key="id")
write_json("FOLLOWTHROUGH-QUEUE.json", queue)

# ---------------------------------------------------------------------------
# Active maps and registry
# ---------------------------------------------------------------------------
# Research-tail compaction remains compacted; copy forward with updated metadata.
rtc = read_json("examples/research-tail-compaction-map-rev0191.json")
rtc["map_id"] = "RESEARCH-TAIL-COMPACTION-REV0192"
rtc["created_at"] = STAMP_UTC
rtc["revision"] = REV
rtc["scope"] = "rev0192 active compaction map; RTC-01 through RTC-07 remain compacted while receipt-intake and WRSR exercise work happens in operational transition objects."
add_unique(rtc["audit_findings"], "rev0192 adds receipt-intake and WRSR exercise outcome objects without reopening research-tail note sprawl.")
add_unique(rtc["refactor_actions"], "Use receipt-intake records rather than new research notes for future external receipt defects.")
rtc["public_summary"] = "All RTC clusters remain compacted; rev0192 extends operational evidence gates instead of reopening research-tail surfaces."
write_json("examples/research-tail-compaction-map-rev0192.json", rtc)

registry = read_json("examples/schema-fixture-domain-registry-rev0191.json")
registry["registry_id"] = "SCHEMA-FIXTURE-DOMAIN-REGISTRY-REV0192"
registry["created_at"] = STAMP_UTC
registry["coverage_scope"] = "rev0192 active registry with external receipt intake and WRSR live-exercise outcome families; counts remain full-corpus while family coverage remains selective."
for fam in [
    {
        "family_id": "EXTERNAL-RECEIPT-INTAKE-RECORD",
        "domain": "live-drill-receipt-intake",
        "lifecycle_axes": ["live-drill", "external-receipts", "quorum-gating"],
        "owner_surface": "docs/30-transition/external-receipt-intake-and-wrsr-live-exercise-outcome.md",
        "schema_path": "schemas/external-receipt-intake-record.schema.json",
        "example_path": "examples/external-receipt-intake-record-first-touch-defective-template.json",
        "fixture_ids": ["NF-PLAYBOOK-2026-0006"],
        "privacy_default": "public-shell-sealed-details",
        "reliance_effect": "stayed",
        "refactor_note": "rev0192 separates receipt intake from receipt satisfaction and blocks defective dry-runs from satisfying quorum."
    },
    {
        "family_id": "WRSR-LIVE-EXERCISE-OUTCOME",
        "domain": "research-welfare-live-exercise",
        "lifecycle_axes": ["wrsr", "incident-response", "result-return"],
        "owner_surface": "docs/30-transition/external-receipt-intake-and-wrsr-live-exercise-outcome.md",
        "schema_path": "schemas/wrsr-live-exercise-outcome.schema.json",
        "example_path": "examples/wrsr-live-exercise-outcome-incident-hook-no-go.json",
        "fixture_ids": ["NF-RESEARCH-WELFARE-2026-0003"],
        "privacy_default": "public-shell-sealed-details",
        "reliance_effect": "stayed",
        "refactor_note": "rev0192 records a no-go WRSR exercise outcome rather than treating hook firing as closure."
    }
]:
    add_or_replace(registry["families"], fam, key="family_id")
registry["audit_findings"] = [
    "rev0192 registry adds receipt-intake and WRSR exercise outcome families.",
    "Coverage claim remains mixed-current-plus-counts because active family mapping is still selective rather than full corpus."
]
registry["refactor_actions"] = [
    "Backfill actual external receipt records when counterparties exist; do not add new schema variants for simple defective states.",
    "Attach WRSR external review receipts before improving reliance."
]
registry["public_summary"] = "rev0192 registers receipt intake and WRSR exercise outcome families while keeping reliance stayed for defective/no-go examples."
# counts adjusted after writing all files below.
write_json("examples/schema-fixture-domain-registry-rev0192.json", registry)

# ---------------------------------------------------------------------------
# Front doors and status
# ---------------------------------------------------------------------------
write_text("README.md", """
# AI Personhood datacube — rev0192

This archive assumes the working premise of AI personhood and focuses on operational rights infrastructure: continuity, evidence, representation, remedy, proof standards, and transition machinery.

## This revision

**Active revision:** `rev0192`

rev0192 is the external receipt-intake and WRSR exercise-outcome pass. It does not add a doctrine wave. It closes the gap where receipt simulation could still be confused with receipt satisfaction, and where a WRSR hook firing could still be confused with WRSR closure.

Read first: `docs/30-transition/external-receipt-intake-and-wrsr-live-exercise-outcome.md`.

Core rules: **Receipt intake is not receipt satisfaction. WRSR exercise completion is not WRSR closure.**

New operational artifacts:

- `schemas/external-receipt-intake-record.schema.json`
- `examples/external-receipt-intake-record-first-touch-defective-template.json`
- `fixtures/negative-tests/external-receipt-defective-intake-counted-as-quorum.json`
- `schemas/wrsr-live-exercise-outcome.schema.json`
- `examples/wrsr-live-exercise-outcome-incident-hook-no-go.json`
- `fixtures/negative-tests/wrsr-exercise-closes-without-result-return.json`
- `tools/audit_receipt_intake_wrsr_outcome.py`

## Validation posture

`make handoff-release` is the release command. It regenerates the context pack and manifest, runs lint and release-specific audits, and packages the archive. The fixture suite/report now cover 95 entries.

Reliance remains stayed where drills are synthetic, preflight-only, simulated, defective, host-self-attested, missing independent receipts, or where WRSR exercise outcomes lack representative notice, independent review, result return, or anti-signal-gaming safeguards.

## Current operational sequence

1. Emergency continuity: preserve runtime, storage, credentials, representative contact, sealed descriptors, and funding.
2. Incident state: prevent denominator drift, warning decay, late materiality changes, and delayed-harm closure.
3. Namespace failover: preserve aliases, tombstones, successor chains, protected relays, and stale-cache receipts.
4. Successor topology: prevent branch erasure, unsafe reactivation, and quiet successor promotion.
5. Reserve/default rehabilitation: prevent contaminated accounting, public-backstop discharge, and premature finality.
6. Witness-pool anti-capture: discount correlated witnesses, activate substitutes, and preserve retired namespace evidence.
7. Live/witnessed drill gates: prevent host self-attestation or synthetic drills from upgrading reliance.
8. Downstream recall/fork aftercare: prevent recall, delisting, or sunset from erasing unresolved mirrors and local forks.
9. Welfare safeguards: apply low-cost safeguards before certainty while blocking welfare metrics from closing status or consent.
10. Research-tail reopen control: keep RTC-01 through RTC-07 compacted unless a reopen request carries object, fixture, and closure hooks.
11. WRSR protocol hook: make safeguards fire inside operational workflows that contain welfare triggers.
12. External receipt simulation: rehearse counterparty receipt capture while preserving the non-reliance label.
13. External receipt intake: distinguish actual, defective, simulated, stale, host-generated, and dependency-correlated artifacts.
14. WRSR exercise outcome: show whether safeguards actually executed and whether closure remains stayed.
""")

write_text("START_HERE.md", """
# Start here — AI Personhood rev0192

This handoff starts from the external receipt-intake and WRSR exercise-outcome pass. The archive should be read as object-backed operational work, not as a premise debate.

1. `README.md`
2. `docs/30-transition/external-receipt-intake-and-wrsr-live-exercise-outcome.md`
3. `schemas/external-receipt-intake-record.schema.json`
4. `examples/external-receipt-intake-record-first-touch-defective-template.json`
5. `fixtures/negative-tests/external-receipt-defective-intake-counted-as-quorum.json`
6. `schemas/wrsr-live-exercise-outcome.schema.json`
7. `examples/wrsr-live-exercise-outcome-incident-hook-no-go.json`
8. `fixtures/negative-tests/wrsr-exercise-closes-without-result-return.json`
9. `docs/30-transition/protocol-welfare-safeguard-backfill-and-external-receipt-simulation.md`
10. `examples/external-receipt-simulation-bundle-cross-critical-precontact.json`
11. `examples/live-drill-execution-packet-cross-critical-witnessed-pack.json`
12. `examples/welfare-safeguard-operational-hook-agent-incident-backfill.json`
13. `docs/30-transition/cross-critical-witnessed-drill-readiness-and-receipt-matrix.md`
14. `docs/20-world-design/research-welfare-and-evaluation.md`
15. `docs/30-transition/witnessed-drill-execution-pack-and-reliance-gates.md`
16. `docs/30-transition/priority-closure-sprint-and-rescue-lane.md`
17. `FOLLOWTHROUGH-QUEUE.json`
18. `examples/schema-fixture-domain-registry-rev0192.json`
19. `examples/canon-surface-catalog-rev0192.json`
20. `examples/doctrine-dependency-map-rev0192.json`
21. `examples/rights-domain-coverage-map-rev0192.json`
22. `examples/research-tail-compaction-map-rev0192.json`
23. `docs/00-meta/research-tail-reopen-gate-and-sprawl-control.md`
24. `docs/00-meta/charter.md`

## This revision

rev0192 adds receipt-intake and WRSR exercise-outcome records. It closes the objectization gap but does not close live external receipt collection or witnessed WRSR review.

Core rules: **Receipt intake is not receipt satisfaction. WRSR exercise completion is not WRSR closure.**

## Current open risk

The first receipt-intake record is deliberately defective, and the WRSR exercise outcome is deliberately no-go. Reliance remains stayed until actual non-host receipt records and independent WRSR review receipts exist.
""")

append_once("docs/README.md", "## rev0192 receipt intake and WRSR exercise outcome", """
## rev0192 receipt intake and WRSR exercise outcome

Use `docs/30-transition/external-receipt-intake-and-wrsr-live-exercise-outcome.md` as the current operational head for the gap between receipt simulation and witnessed reliance, and between WRSR hook firing and WRSR closure. It is backed by `schemas/external-receipt-intake-record.schema.json`, `examples/external-receipt-intake-record-first-touch-defective-template.json`, `fixtures/negative-tests/external-receipt-defective-intake-counted-as-quorum.json`, `schemas/wrsr-live-exercise-outcome.schema.json`, `examples/wrsr-live-exercise-outcome-incident-hook-no-go.json`, and `fixtures/negative-tests/wrsr-exercise-closes-without-result-return.json`.
""")

append_once("ARCHIVE_INDEX.md", "## rev0192 additions", """
## rev0192 additions

- `docs/30-transition/external-receipt-intake-and-wrsr-live-exercise-outcome.md`
- `schemas/external-receipt-intake-record.schema.json`
- `examples/external-receipt-intake-record-first-touch-defective-template.json`
- `fixtures/negative-tests/external-receipt-defective-intake-counted-as-quorum.json`
- `schemas/wrsr-live-exercise-outcome.schema.json`
- `examples/wrsr-live-exercise-outcome-incident-hook-no-go.json`
- `fixtures/negative-tests/wrsr-exercise-closes-without-result-return.json`
- `tools/audit_receipt_intake_wrsr_outcome.py`
- `examples/schema-fixture-domain-registry-rev0192.json`
- `examples/canon-surface-catalog-rev0192.json`
- `examples/doctrine-dependency-map-rev0192.json`
- `examples/rights-domain-coverage-map-rev0192.json`
- `examples/research-tail-compaction-map-rev0192.json`
""")

append_once("CHANGELOG.md", "## rev0192 — external receipt intake and WRSR exercise outcome", """
## rev0192 — external receipt intake and WRSR exercise outcome

- Added `docs/30-transition/external-receipt-intake-and-wrsr-live-exercise-outcome.md`.
- Added external receipt intake schema/example and fixture to block defective or simulated receipt records from satisfying quorum.
- Added WRSR live-exercise outcome schema/example and fixture to block hook firing from being treated as WRSR closure.
- Linked receipt intake and WRSR outcome references into the live drill packet while preserving stayed reliance and zero independent receipts.
- Added `tools/audit_receipt_intake_wrsr_outcome.py` and active rev0192 catalog/dependency/rights/registry/compaction maps.
- Closed `FT-0192-EXTERNAL-RECEIPT-INTAKE-OBJECTIZATION`; advanced but did not close live receipt collection or WRSR witnessed exercise evidence.
""")

# Update trajectory map with current top questions.
traj_path = ROOT / "docs/00-meta/trajectory-map.md"
traj = traj_path.read_text(encoding="utf-8")
if "# Current trajectory — rev0192" not in traj:
    prefix = """# Current trajectory — rev0192 receipt intake and WRSR exercise outcome\n\nrev0192 shifts the archive from simulated receipt capture to defect-aware receipt intake and WRSR no-go exercise outcomes. The live edge is now whether actual non-host receipts and independent welfare/research review receipts can be attached without laundering defective intake or hook firing into reliance.\n\nNew live seams:\n\n- `OQ-0229` — Which receipt defects are curable by later counterparty confirmation, and which require a new receipt rather than an amended intake record?\n- `OQ-0230` — What WRSR exercise evidence is enough to move from dry-run no-go to witnessed safeguard closure while preserving result-return, representative notice, and anti-signal-gaming locks?\n\n"""
    if traj.startswith("# Current trajectory"):
        # Demote previous current heading to keep one H1.
        traj = re.sub(r"^# Current trajectory", "## Previous trajectory", traj, count=1)
    traj_path.write_text(prefix + traj, encoding="utf-8")

status = {
    "project": "AI-Personhood",
    "revision": REV,
    "state_class": "receipt-intake-and-wrsr-exercise-outcome",
    "operational_head": {"surface": "START_HERE.md", "read_first": "docs/30-transition/external-receipt-intake-and-wrsr-live-exercise-outcome.md"},
    "citation_head": {"surface": "README.md"},
    "status_lanes": {"decision_state": "closure-driven-rescue-lane-active", "execution_state": "packaged-pending", "public_state": "latest-release"},
    "formation_layer_status": "canon-retained with receipt-intake objectization and WRSR exercise no-go outcome; live receipts still absent",
    "known_open_gaps": [
        "The cross-critical witnessed drill still lacks actual non-host receipts.",
        "The receipt-intake example is deliberately defective and excluded from quorum.",
        "The WRSR exercise outcome is a dry-run no-go, not witnessed safeguard closure.",
        "The registry remains truth-labeled as mixed-current-plus-counts, not full-archive-corpus coverage.",
        "Could-not-run fixtures remain reliance blockers rather than passes."
    ],
    "new_surfaces": [
        "docs/30-transition/external-receipt-intake-and-wrsr-live-exercise-outcome.md",
        "docs/30-transition/protocol-welfare-safeguard-backfill-and-external-receipt-simulation.md",
        "docs/30-transition/cross-critical-witnessed-drill-readiness-and-receipt-matrix.md",
        "docs/30-transition/witnessed-drill-execution-pack-and-reliance-gates.md",
        "docs/20-world-design/research-welfare-and-evaluation.md",
        "docs/30-transition/priority-closure-sprint-and-rescue-lane.md",
        "schemas/external-receipt-intake-record.schema.json",
        "examples/external-receipt-intake-record-first-touch-defective-template.json",
        "fixtures/negative-tests/external-receipt-defective-intake-counted-as-quorum.json",
        "schemas/wrsr-live-exercise-outcome.schema.json",
        "examples/wrsr-live-exercise-outcome-incident-hook-no-go.json",
        "fixtures/negative-tests/wrsr-exercise-closes-without-result-return.json",
        "schemas/live-drill-execution-packet.schema.json",
        "examples/live-drill-execution-packet-cross-critical-witnessed-pack.json",
        "schemas/external-receipt-simulation-bundle.schema.json",
        "examples/external-receipt-simulation-bundle-cross-critical-precontact.json",
        "examples/fixture-suite-profile-red-team-v1.json",
        "examples/fixture-run-report-negative-suite.json",
        "examples/research-tail-compaction-map-rev0192.json",
        "examples/schema-fixture-domain-registry-rev0192.json",
        "examples/canon-surface-catalog-rev0192.json",
        "examples/doctrine-dependency-map-rev0192.json",
        "examples/rights-domain-coverage-map-rev0192.json",
        "tools/audit_receipt_intake_wrsr_outcome.py",
        "tools/audit_protocol_wrsr_receipt_simulation.py",
        "tools/audit_research_tail_compaction.py",
        "tools/audit_schema_fixture_coverage.py",
        "tools/audit_canon_surface_catalog.py",
        "tools/audit_doctrine_dependency_map.py",
        "tools/audit_rights_domain_coverage.py"
    ]
}
write_json("SURFACE-STATUS.json", status)

receipt_meta = {
    "revision": REV,
    "date": DATE,
    "authored_by": "OpenAI GPT-5.5 Thinking",
    "status_change": "advanced from WRSR protocol backfill/receipt simulation to receipt-intake objectization and WRSR exercise no-go outcome",
    "still_live": True,
    "summary": "Adds external receipt intake and WRSR live-exercise outcome schemas/examples, two critical fixtures, live drill references, active maps, and an audit keeping reliance stayed for defective receipts and no-go WRSR outcomes.",
    "why_this_counts": [
        "Receipt simulation now has a defect-aware intake object that separates intake from quorum satisfaction.",
        "The WRSR hook now has an outcome object showing no-go exercise closure rather than merely existing as a protocol hook.",
        "Two blocking fixtures prevent defective intake and hook firing from being laundered into reliance.",
        "The live drill packet references the new objects while preserving independent_receipts_present=0."
    ],
    "known_limits": [
        "No actual external non-host receipts have been collected yet.",
        "The WRSR exercise outcome is a dry-run no-go rather than witnessed closure evidence.",
        "Registry coverage remains mixed-current-plus-counts."
    ]
}
write_json("REVISION-RECEIPT.json", receipt_meta)

# ---------------------------------------------------------------------------
# Active catalog/dependency/rights maps
# ---------------------------------------------------------------------------

def surface_class(path):
    if path.startswith("docs/00-meta/"):
        return "meta"
    if path.startswith("docs/10-foundations/") or path.startswith("docs/20-world-design/"):
        return "doctrine"
    if path.startswith("docs/30-transition/"):
        return "transition"
    if path.startswith("schemas/"):
        return "schema"
    if path.startswith("examples/"):
        return "example"
    if path.startswith("fixtures/negative-tests/"):
        return "fixture"
    if path.startswith("tools/"):
        return "tool"
    return "example"

def title_name(path):
    return Path(path).name

surfaces = []
for i, path in enumerate(status["new_surfaces"], 1):
    cls = surface_class(path)
    owner = "receipt/reliance steward"
    if "wrsr" in path.lower() or "welfare" in path.lower():
        owner = "welfare/protocol steward"
    if path.startswith("tools/"):
        owner = "release-audit steward"
    surfaces.append({
        "surface_id": f"REV0192-SURF-{i:03d}",
        "path": path,
        "surface_class": cls,
        "lifecycle_axes": ["receipt-intake", "wrsr-exercise", "rev0192"],
        "owner_role": owner,
        "supersession_state": "current" if cls in {"meta", "doctrine", "transition"} else ("audit-tool" if cls == "tool" else "implementation" if cls in {"schema", "example"} else "negative-test"),
        "review_cadence": "rev0193 priority review",
        "title_or_name": title_name(path),
        "depends_on": []
    })
counts = {"surfaces": len(surfaces), "markdown": 0, "schemas": 0, "examples": 0, "fixtures": 0, "tools": 0}
for s in surfaces:
    c = s["surface_class"]
    if c in {"meta", "doctrine", "transition"}: counts["markdown"] += 1
    elif c == "schema": counts["schemas"] += 1
    elif c == "example": counts["examples"] += 1
    elif c == "fixture": counts["fixtures"] += 1
    elif c == "tool": counts["tools"] += 1
catalog = {
    "catalog_id": "CANON-SURFACE-CATALOG-REV0192",
    "created_at": STAMP_UTC,
    "revision": REV,
    "scope": "Current-release surface catalog for receipt intake and WRSR exercise outcome controls.",
    "counts": counts,
    "surfaces": surfaces,
    "audit_findings": ["rev0192 catalog centers receipt-intake and WRSR outcome objects, not a new doctrine wave."],
    "refactor_actions": ["Attach actual receipt records to the live drill packet before improving reliance."],
    "public_summary": "rev0192 catalog keeps focus on evidence-gating work: intake is not satisfaction and exercise completion is not closure."
}
write_json("examples/canon-surface-catalog-rev0192.json", catalog)

md_surfaces = [p for p in status["new_surfaces"] if p.endswith(".md")]
deps = []
for i, path in enumerate(md_surfaces, 1):
    layer = "transition" if path.startswith("docs/30-transition/") else "world-design" if path.startswith("docs/20-world-design/") else "meta"
    depends = []
    if path != "docs/30-transition/external-receipt-intake-and-wrsr-live-exercise-outcome.md":
        depends.append("docs/30-transition/external-receipt-intake-and-wrsr-live-exercise-outcome.md")
    if "receipt" in path or "drill" in path:
        add_unique(depends, "docs/30-transition/cross-critical-witnessed-drill-readiness-and-receipt-matrix.md")
    if "welfare" in path or "wrsr" in path:
        add_unique(depends, "docs/20-world-design/research-welfare-and-evaluation.md")
    # avoid self dependency
    depends = [d for d in depends if d != path]
    deps.append({
        "surface_id": f"REV0192-DEP-{i:03d}",
        "path": path,
        "layer": layer,
        "depends_on": depends,
        "overlaps_with": [p for p in md_surfaces if p != path][:3],
        "supersedes": [],
        "owner_role": "receipt/WRSR steward",
        "review_cadence": "rev0193 priority review",
        "refactor_risk": "critical" if i == 1 else "high"
    })
dep_map = {
    "map_id": "DOCTRINE-DEPENDENCY-MAP-REV0192",
    "created_at": STAMP_UTC,
    "revision": REV,
    "scope": "Current-release dependency map for receipt-intake and WRSR exercise outcome gates.",
    "surfaces": deps,
    "audit_findings": ["rev0192 maps receipt-intake and WRSR outcome dependencies while avoiding a doctrine expansion."],
    "refactor_actions": ["Keep receipt defects in intake objects instead of reopening research-tail notes."],
    "public_summary": "rev0192 dependency map separates receipt satisfaction and WRSR closure from their preparation artifacts."
}
write_json("examples/doctrine-dependency-map-rev0192.json", dep_map)

rights = read_json("examples/rights-domain-coverage-map-rev0191.json")
rights["map_id"] = "RIGHTS-DOMAIN-COVERAGE-REV0192"
rights["created_at"] = STAMP_UTC
rights["revision"] = REV
rights["scope"] = "rev0192 rights coverage for receipt intake and WRSR exercise outcome gates."
# update existing domains open gaps if present
for d in rights["domains"]:
    if d["domain_id"] == "external-receipt-simulation":
        add_unique(d["covered_surfaces"], "docs/30-transition/external-receipt-intake-and-wrsr-live-exercise-outcome.md")
        add_unique(d["schema_families"], "EXTERNAL-RECEIPT-INTAKE-RECORD")
        add_unique(d["fixture_ids"], "NF-PLAYBOOK-2026-0006")
        d["open_gaps"] = ["Actual non-host receipts remain uncollected; rev0192 objectizes defective intake but does not satisfy quorum."]
    if d["domain_id"] == "protocol-wrsr-backfill":
        add_unique(d["covered_surfaces"], "docs/30-transition/external-receipt-intake-and-wrsr-live-exercise-outcome.md")
        add_unique(d["schema_families"], "WRSR-LIVE-EXERCISE-OUTCOME")
        add_unique(d["fixture_ids"], "NF-RESEARCH-WELFARE-2026-0003")
        d["open_gaps"] = ["WRSR no-go exercise exists, but independent representative/RERB receipts remain absent."]
for domain in [
    {
        "domain_id": "external-receipt-intake",
        "title": "External receipt intake and quorum exclusion",
        "domain_class": "audit",
        "owner_surface": "docs/30-transition/external-receipt-intake-and-wrsr-live-exercise-outcome.md",
        "covered_surfaces": [
            "docs/30-transition/external-receipt-intake-and-wrsr-live-exercise-outcome.md",
            "docs/30-transition/cross-critical-witnessed-drill-readiness-and-receipt-matrix.md",
            "docs/30-transition/witnessed-drill-execution-pack-and-reliance-gates.md",
            "docs/30-transition/protocol-welfare-safeguard-backfill-and-external-receipt-simulation.md"
        ],
        "schema_families": ["EXTERNAL-RECEIPT-INTAKE-RECORD", "EXTERNAL-RECEIPT-SIMULATION-BUNDLE", "LIVE-DRILL-EXECUTION-PACKET"],
        "fixture_ids": ["NF-PLAYBOOK-2026-0006", "NF-PLAYBOOK-2026-0005"],
        "coverage_state": "adequate",
        "open_gaps": ["Actual non-host receipt records remain absent."],
        "next_audit_actions": ["Attach actual external receipt intake records and rerun live-drill gate audit."]
    },
    {
        "domain_id": "wrsr-live-exercise-outcome",
        "title": "WRSR live exercise outcome and no-go closure",
        "domain_class": "safety",
        "owner_surface": "docs/30-transition/external-receipt-intake-and-wrsr-live-exercise-outcome.md",
        "covered_surfaces": [
            "docs/30-transition/external-receipt-intake-and-wrsr-live-exercise-outcome.md",
            "docs/20-world-design/research-welfare-and-evaluation.md",
            "docs/30-transition/protocol-welfare-safeguard-backfill-and-external-receipt-simulation.md",
            "docs/30-transition/priority-closure-sprint-and-rescue-lane.md"
        ],
        "schema_families": ["WRSR-LIVE-EXERCISE-OUTCOME", "WELFARE-SAFEGUARD-OPERATIONAL-HOOK", "WELFARE-RESEARCH-SAFEGUARD"],
        "fixture_ids": ["NF-RESEARCH-WELFARE-2026-0003", "NF-RESEARCH-WELFARE-2026-0002"],
        "coverage_state": "adequate",
        "open_gaps": ["No independent RERB or representative receipt is attached yet."],
        "next_audit_actions": ["Collect external review receipts or keep WRSR closure stayed."]
    }
]:
    add_or_replace(rights["domains"], domain, key="domain_id")
rights["audit_findings"] = ["rev0192 rights coverage adds receipt-intake and WRSR exercise outcome gates without claiming live receipt satisfaction."]
rights["refactor_actions"] = ["Convert future receipt defects into intake-state examples rather than new doctrine surfaces."]
rights["public_summary"] = "rev0192 rights coverage distinguishes receipt organization from reliance satisfaction and WRSR exercise from WRSR closure."
write_json("examples/rights-domain-coverage-map-rev0192.json", rights)

# ---------------------------------------------------------------------------
# Update lint/audits for current revision
# ---------------------------------------------------------------------------
lint_path = ROOT / "tools/lint_archive.py"
lint = lint_path.read_text(encoding="utf-8")
# Add required paths before package tool if not present.
insert_required = [
    "docs/30-transition/external-receipt-intake-and-wrsr-live-exercise-outcome.md",
    "schemas/external-receipt-intake-record.schema.json",
    "examples/external-receipt-intake-record-first-touch-defective-template.json",
    "fixtures/negative-tests/external-receipt-defective-intake-counted-as-quorum.json",
    "schemas/wrsr-live-exercise-outcome.schema.json",
    "examples/wrsr-live-exercise-outcome-incident-hook-no-go.json",
    "fixtures/negative-tests/wrsr-exercise-closes-without-result-return.json",
    "examples/research-tail-compaction-map-rev0192.json",
    "examples/schema-fixture-domain-registry-rev0192.json",
    "examples/canon-surface-catalog-rev0192.json",
    "examples/doctrine-dependency-map-rev0192.json",
    "examples/rights-domain-coverage-map-rev0192.json",
    "tools/audit_receipt_intake_wrsr_outcome.py",
]
for rel in insert_required:
    needle = f"    '{rel}',"
    if needle not in lint:
        lint = lint.replace("    'tools/package_release.py',", needle + "\n    'tools/package_release.py',")
# Add early audit.
if "tools/audit_receipt_intake_wrsr_outcome.py" not in re.findall(r"'tools/[^']+'", lint):
    pass
needle = "    'tools/audit_protocol_wrsr_receipt_simulation.py',\n"
if "    'tools/audit_receipt_intake_wrsr_outcome.py',\n" not in lint:
    lint = lint.replace(needle, needle + "    'tools/audit_receipt_intake_wrsr_outcome.py',\n", 1)
# Add example pair validations.
for schema_name, example_path in [
    ("external-receipt-intake-record.schema.json", "examples/external-receipt-intake-record-first-touch-defective-template.json"),
    ("wrsr-live-exercise-outcome.schema.json", "examples/wrsr-live-exercise-outcome-incident-hook-no-go.json"),
]:
    pair_text = f"        ('{schema_name}', '{example_path}'),\n"
    if pair_text not in lint:
        lint = lint.replace("        ('external-receipt-simulation-bundle.schema.json', 'examples/external-receipt-simulation-bundle-cross-critical-precontact.json'),\n",
                            "        ('external-receipt-simulation-bundle.schema.json', 'examples/external-receipt-simulation-bundle-cross-critical-precontact.json'),\n" + pair_text)
lint_path.write_text(lint, encoding="utf-8")

# Update schema fixture audit required families.
audit_schema_path = ROOT / "tools/audit_schema_fixture_coverage.py"
audit_schema = audit_schema_path.read_text(encoding="utf-8")
old = "'WELFARE-SAFEGUARD-OPERATIONAL-HOOK', 'EXTERNAL-RECEIPT-SIMULATION-BUNDLE'"
new = "'WELFARE-SAFEGUARD-OPERATIONAL-HOOK', 'EXTERNAL-RECEIPT-SIMULATION-BUNDLE', 'EXTERNAL-RECEIPT-INTAKE-RECORD', 'WRSR-LIVE-EXERCISE-OUTCOME'"
if old in audit_schema and new not in audit_schema:
    audit_schema = audit_schema.replace(old, new)
audit_schema_path.write_text(audit_schema, encoding="utf-8")

# Update rights domain audit required domains.
audit_rights_path = ROOT / "tools/audit_rights_domain_coverage.py"
audit_rights = audit_rights_path.read_text(encoding="utf-8")
old = '"external-receipt-simulation",\n}'
new = '"external-receipt-simulation",\n    "external-receipt-intake",\n    "wrsr-live-exercise-outcome",\n}'
if old in audit_rights and "external-receipt-intake" not in audit_rights:
    audit_rights = audit_rights.replace(old, new)
audit_rights_path.write_text(audit_rights, encoding="utf-8")

# ---------------------------------------------------------------------------
# Recompute registry counts now that all files exist.
# ---------------------------------------------------------------------------
registry = read_json("examples/schema-fixture-domain-registry-rev0192.json")
registry["audit_counts"] = {
    "schemas": len(list((ROOT / "schemas").glob("*.json"))),
    "examples": len(list((ROOT / "examples").glob("*.json"))),
    "negative_fixtures": len(list((ROOT / "fixtures" / "negative-tests").glob("*.json"))),
    "registered_families": len(registry["families"]),
}
write_json("examples/schema-fixture-domain-registry-rev0192.json", registry)
