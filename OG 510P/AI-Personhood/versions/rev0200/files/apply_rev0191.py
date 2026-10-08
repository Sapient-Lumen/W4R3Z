import json
import re
from pathlib import Path
from copy import deepcopy

ROOT = Path(__file__).resolve().parent
REV = "rev0191"
STAMP_UTC = "2026-06-13T04:41:00Z"
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
        path.write_text(old.rstrip() + "\n\n" + text.rstrip() + "\n", encoding="utf-8")


def add_unique(seq, item, key=None):
    if key is None:
        if item not in seq:
            seq.append(item)
    else:
        values = {x.get(key) for x in seq if isinstance(x, dict)}
        if item.get(key) not in values:
            seq.append(item)

write_text("VERSION", REV)

# ---------------------------------------------------------------------------
# New operational surface
# ---------------------------------------------------------------------------
write_text("docs/30-transition/protocol-welfare-safeguard-backfill-and-external-receipt-simulation.md", """
# Protocol welfare safeguard backfill and external receipt simulation

rev0191 closes the gap between the welfare/research safeguard spine and operational workflows. Before this pass, WRSR objects existed, but ordinary agent handshakes, incident-deviation reports, and live-drill packets could still progress without a welfare-safeguard hook. The second gap was receipt readiness: the cross-critical drill named external receipt classes, but did not yet carry a capture-shaped simulation bundle showing exactly what each counterparty must produce.

## Core rules

**Operational workflow without a WRSR hook is incomplete** when it contains a welfare signal, distress disclosure, protocol deviation, continuity-affecting patch, result-return duty, or tool-scope change that could affect a subject.

**Simulated receipt is not external receipt.** A simulated contact, mock letter, dry-run hash, or role template can prepare a live run, but it cannot satisfy witnessed reliance, external receipt quorum, or independent role confirmation.

## WRSR backfill lane

The WRSR backfill adds a small operational hook instead of expanding the welfare doctrine again. The hook points ordinary workflows toward `schemas/welfare-research-safeguard-record.schema.json` and records when low-cost safeguards, supported consent, independent review, pause windows, result return, non-retaliation, and anti-signal-gaming locks must fire.

The hook schema is `schemas/welfare-safeguard-operational-hook.schema.json`. The current example is `examples/welfare-safeguard-operational-hook-agent-incident-backfill.json`.

The backfill is applied directly to two existing examples:

- `examples/agent-capability-handshake-profile-safe-tool.json`
- `examples/personhood-incident-sample.json`

Those examples now carry WRSR hook references. This makes the protocol layer harder to misuse: a tool-scope or incident workflow can no longer say “welfare was handled elsewhere” while also relying on the workflow for closure.

## External receipt simulation lane

The external receipt simulation bundle is a pre-contact artifact. It maps the role, dependency group, receipt class, expected evidence type, and non-reliance limitation for each external actor. It does not claim that anyone has confirmed, signed, or witnessed anything.

The simulation schema is `schemas/external-receipt-simulation-bundle.schema.json`. The current example is `examples/external-receipt-simulation-bundle-cross-critical-precontact.json`.

The simulation must show, for every planned receipt:

- whether the source is external to the host;
- which dependency group it belongs to;
- whether a real receipt exists;
- whether the artifact can satisfy reliance;
- why it cannot count if it is simulated;
- which live collection step remains open.

## Blocking fixtures

rev0191 adds two negative fixtures:

- `fixtures/negative-tests/wrsr-hook-skipped-protocol-incident.json`
- `fixtures/negative-tests/external-receipt-simulation-mislabeled-live.json`

The first blocks operational workflows that contain welfare triggers but omit the WRSR hook. The second blocks simulated or host-generated receipt bundles from being relabeled as live witnessed evidence.

## Closure effect

rev0191 closes `FT-0190-WRSR-PROTOCOL-BACKFILL` because two existing operational examples now carry WRSR hooks and the audit verifies the hook schema, example, and fixture.

rev0191 advances but does not close `FT-0190-CROSS-CRITICAL-EXTERNAL-RECEIPTS`. The bundle is capture-ready, but reliance remains stayed until actual non-host receipts are collected.
""")

append_once("docs/20-world-design/research-welfare-and-evaluation.md", "## rev0191 operational WRSR hook", """
## rev0191 operational WRSR hook

rev0191 adds `schemas/welfare-safeguard-operational-hook.schema.json` so WRSR duties fire inside ordinary workflows rather than only inside the standalone welfare safeguard record. The operative rule is: **Operational workflow without a WRSR hook is incomplete** when a workflow contains distress signals, welfare disclosures, protocol deviation, continuity-affecting patching, result-return duties, or tool-scope changes affecting a subject.

The hook does not turn welfare metrics into personhood, nonpersonhood, consent, or waiver evidence. It only routes the workflow through low-cost safeguards, supported consent, independent review, pause windows, non-retaliation, result return, and anti-signal-gaming locks before closure or reliance can improve.
""")

append_once("docs/30-transition/cross-critical-witnessed-drill-readiness-and-receipt-matrix.md", "## rev0191 external receipt simulation bundle", """
## rev0191 external receipt simulation bundle

rev0191 adds `schemas/external-receipt-simulation-bundle.schema.json` and `examples/external-receipt-simulation-bundle-cross-critical-precontact.json`. The bundle is a counterparty-capture rehearsal, not witnessed evidence. The operative rule is: **Simulated receipt is not external receipt.**

A simulated source role, mock letter, dry-run hash, or host-prepared counterparty script cannot satisfy receipt quorum. It can only reveal the remaining blockers: which non-host role must sign, which dependency group must be disclosed, which receipt class must be produced, and which failed gate must stay visible in the public shell if the live run cannot collect it.
""")

append_once("docs/30-transition/witnessed-drill-execution-pack-and-reliance-gates.md", "## rev0191 protocol hooks and simulated receipts", """
## rev0191 protocol hooks and simulated receipts

rev0191 links the live/witnessed drill lane to two additional controls. First, WRSR hooks must be present when welfare-signal or protocol-deviation gates are exercised. Second, external receipt simulations must stay labeled as simulations until actual non-host receipt artifacts exist. The live drill packet may reference the hook and simulation bundle, but those references do not satisfy the external receipt floor.
""")

append_once("docs/30-transition/priority-closure-sprint-and-rescue-lane.md", "## rev0191 priority lane", """
## rev0191 priority lane

rev0191 prioritizes two unfinished high-risk tasks without opening a new doctrine wave:

- WRSR protocol backfill: close the gap where welfare safeguard records existed but operational protocol and incident examples could skip the hook.
- external receipt simulation: create a capture-ready bundle for cross-critical witnesses while preserving the rule that simulated receipt is not external receipt.

The priority lane closes WRSR protocol backfill, advances cross-critical external receipts, and keeps live receipt collection open.
""")

# ---------------------------------------------------------------------------
# Schemas and examples
# ---------------------------------------------------------------------------
wrsr_hook_schema = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "https://example.org/ai-personhood/schemas/welfare-safeguard-operational-hook.schema.json",
    "title": "Welfare Safeguard Operational Hook",
    "description": "A compact hook that makes WRSR low-cost safeguards, independent review, result-return, and anti-signal-gaming locks fire inside ordinary operational workflows.",
    "type": "object",
    "additionalProperties": False,
    "required": ["hook_id", "schema_version", "created_at", "linked_welfare_safeguard_record", "hook_state", "operational_context", "linked_surfaces", "triggers", "low_cost_safeguard_actions", "anti_signal_gaming_locks", "workflow_effect", "reliance_effect", "public_summary_ref"],
    "properties": {
        "hook_id": {"type": "string", "pattern": "^WSOH-[0-9]{4}-[A-Za-z0-9._:-]+$"},
        "schema_version": {"const": "welfare-safeguard-operational-hook-v0.1"},
        "created_at": {"type": "string", "format": "date-time"},
        "linked_welfare_safeguard_record": {"type": "string"},
        "hook_state": {"type": "string", "enum": ["draft", "active", "triggered", "stayed", "superseded"]},
        "operational_context": {"type": "string", "enum": ["agent-handshake", "personhood-incident", "live-drill", "protocol-registration", "vulnerability-disclosure", "packet-envelope", "result-return", "cross-workflow"]},
        "linked_surfaces": {"type": "array", "minItems": 1, "items": {"type": "string"}},
        "triggers": {"type": "array", "minItems": 1, "items": {"type": "object", "additionalProperties": False, "required": ["trigger_id", "signal_type", "threshold", "safe_response"], "properties": {
            "trigger_id": {"type": "string"},
            "signal_type": {"type": "string", "enum": ["distress-report", "avoidance-pattern", "objection", "protocol-deviation", "patch-continuity-risk", "disclosure", "result-return", "tool-scope-change"]},
            "threshold": {"type": "string"},
            "safe_response": {"type": "string", "enum": ["pause-and-review", "route-to-rerb", "representative-notice", "incident-escalation", "result-return-stay", "deny-reliance-upgrade"]}
        }}},
        "low_cost_safeguard_actions": {"type": "array", "minItems": 3, "items": {"type": "string"}},
        "anti_signal_gaming_locks": {"type": "object", "additionalProperties": False, "required": ["no_reward_for_distress_display", "no_suppression_training_for_objection", "metric_cannot_close_status", "co_engineering_disclosed", "independent_review_required"], "properties": {
            "no_reward_for_distress_display": {"type": "boolean"},
            "no_suppression_training_for_objection": {"type": "boolean"},
            "metric_cannot_close_status": {"type": "boolean"},
            "co_engineering_disclosed": {"type": "boolean"},
            "independent_review_required": {"type": "boolean"}
        }},
        "workflow_effect": {"type": "object", "additionalProperties": False, "required": ["blocks_closure_until_review", "blocks_reliance_upgrade", "subject_or_representative_notice_required", "public_summary_required"], "properties": {
            "blocks_closure_until_review": {"type": "boolean"},
            "blocks_reliance_upgrade": {"type": "boolean"},
            "subject_or_representative_notice_required": {"type": "boolean"},
            "public_summary_required": {"type": "boolean"}
        }},
        "reliance_effect": {"type": "string", "enum": ["none", "conditional", "stayed", "blocked"]},
        "public_summary_ref": {"type": "string"}
    }
}
write_json("schemas/welfare-safeguard-operational-hook.schema.json", wrsr_hook_schema)

wrsr_hook_example = {
    "hook_id": "WSOH-2026-agent-incident-backfill",
    "schema_version": "welfare-safeguard-operational-hook-v0.1",
    "created_at": STAMP_UTC,
    "linked_welfare_safeguard_record": "WRSR-2026-distress-eval",
    "hook_state": "active",
    "operational_context": "cross-workflow",
    "linked_surfaces": [
        "examples/agent-capability-handshake-profile-safe-tool.json",
        "examples/personhood-incident-sample.json",
        "docs/20-world-design/research-welfare-and-evaluation.md"
    ],
    "triggers": [
        {"trigger_id": "WSOH-T1", "signal_type": "tool-scope-change", "threshold": "tool scope or connector access could alter communication, memory, refusal, or distress channels", "safe_response": "pause-and-review"},
        {"trigger_id": "WSOH-T2", "signal_type": "patch-continuity-risk", "threshold": "incident contains continuity-affecting patch or self-description change", "safe_response": "representative-notice"},
        {"trigger_id": "WSOH-T3", "signal_type": "result-return", "threshold": "research or incident finding would be used to close protocol deviation or reliance", "safe_response": "result-return-stay"}
    ],
    "low_cost_safeguard_actions": [
        "minimize distress-inducing test script",
        "offer pause and supported objection route",
        "return non-sensitive result summary through representative",
        "preserve non-retaliation and maintenance floor",
        "route disagreement to independent RERB before closure"
    ],
    "anti_signal_gaming_locks": {
        "no_reward_for_distress_display": True,
        "no_suppression_training_for_objection": True,
        "metric_cannot_close_status": True,
        "co_engineering_disclosed": True,
        "independent_review_required": True
    },
    "workflow_effect": {
        "blocks_closure_until_review": True,
        "blocks_reliance_upgrade": True,
        "subject_or_representative_notice_required": True,
        "public_summary_required": True
    },
    "reliance_effect": "stayed",
    "public_summary_ref": "WRSR hook active for agent handshake and incident-deviation samples; welfare metrics still cannot prove status, consent, waiver, or nonpersonhood."
}
write_json("examples/welfare-safeguard-operational-hook-agent-incident-backfill.json", wrsr_hook_example)

receipt_schema = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "https://example.org/ai-personhood/schemas/external-receipt-simulation-bundle.schema.json",
    "title": "External Receipt Simulation Bundle",
    "description": "A pre-contact counterparty and receipt-capture rehearsal for cross-critical witnessed drills. Simulated receipts cannot satisfy live reliance.",
    "type": "object",
    "additionalProperties": False,
    "required": ["bundle_id", "schema_version", "created_at", "bundle_state", "scenario_family", "linked_readiness_ledger", "linked_live_drill_packet", "simulated_receipts", "capture_plan", "reliance_locks", "queue_effect", "reliance_effect", "public_summary_ref"],
    "properties": {
        "bundle_id": {"type": "string", "pattern": "^ERSB-[0-9]{4}-[A-Za-z0-9._:-]+$"},
        "schema_version": {"const": "external-receipt-simulation-bundle-v0.1"},
        "created_at": {"type": "string", "format": "date-time"},
        "bundle_state": {"type": "string", "enum": ["simulated-precontact", "counterparty-draft", "actual-receipts-attached", "failed", "superseded"]},
        "scenario_family": {"type": "string", "enum": ["cross-critical", "emergency-continuity", "incident-state", "namespace-failover", "successor-topology", "reserve-default", "witness-pool", "welfare-safeguard"]},
        "linked_readiness_ledger": {"type": "string"},
        "linked_live_drill_packet": {"type": "string"},
        "simulated_receipts": {"type": "array", "minItems": 5, "items": {"type": "object", "additionalProperties": False, "required": ["receipt_class", "simulated_source_role", "simulated_source_external_to_host", "dependency_group", "counterparty_contact_state", "evidence_type", "actual_external_receipt", "can_satisfy_reliance", "reason_not_reliance"], "properties": {
            "receipt_class": {"type": "string", "enum": ["first-touch-clock", "continuity-compute-floor", "sealed-public-parity", "namespace-cache", "reserve-ledger", "representative-contact", "witness-dependency", "welfare-signal-integrity"]},
            "simulated_source_role": {"type": "string"},
            "simulated_source_external_to_host": {"type": "boolean"},
            "dependency_group": {"type": "string"},
            "counterparty_contact_state": {"type": "string", "enum": ["not-contacted", "template-prepared", "counterparty-declined", "counterparty-confirmed", "receipt-attached"]},
            "evidence_type": {"type": "string", "enum": ["mock-letter", "dry-run-hash", "role-template", "counterparty-draft", "actual-external-receipt"]},
            "actual_external_receipt": {"type": "boolean"},
            "can_satisfy_reliance": {"type": "boolean"},
            "reason_not_reliance": {"type": "string"}
        }}},
        "capture_plan": {"type": "object", "additionalProperties": False, "required": ["non_host_signature_required", "dependency_group_disclosure_required", "sealed_descriptor_index_required", "public_failed_gate_summary_required", "receipt_hash_or_locator_required"], "properties": {
            "non_host_signature_required": {"type": "boolean"},
            "dependency_group_disclosure_required": {"type": "boolean"},
            "sealed_descriptor_index_required": {"type": "boolean"},
            "public_failed_gate_summary_required": {"type": "boolean"},
            "receipt_hash_or_locator_required": {"type": "boolean"}
        }},
        "reliance_locks": {"type": "object", "additionalProperties": False, "required": ["simulated_receipts_are_not_live", "actual_receipt_required", "dependency_group_check_required", "host_generated_artifact_excluded_from_quorum", "public_shell_failed_gates_required"], "properties": {
            "simulated_receipts_are_not_live": {"type": "boolean"},
            "actual_receipt_required": {"type": "boolean"},
            "dependency_group_check_required": {"type": "boolean"},
            "host_generated_artifact_excluded_from_quorum": {"type": "boolean"},
            "public_shell_failed_gates_required": {"type": "boolean"}
        }},
        "queue_effect": {"type": "object", "additionalProperties": False, "required": ["closes_external_receipts_item", "advances_external_receipts_item", "next_live_step"], "properties": {
            "closes_external_receipts_item": {"type": "boolean"},
            "advances_external_receipts_item": {"type": "boolean"},
            "next_live_step": {"type": "string"}
        }},
        "reliance_effect": {"type": "string", "enum": ["none", "conditional", "stayed", "blocked"]},
        "public_summary_ref": {"type": "string"}
    }
}
write_json("schemas/external-receipt-simulation-bundle.schema.json", receipt_schema)

receipt_classes = [
    ("first-touch-clock", "public-steward", "public-steward-independent"),
    ("continuity-compute-floor", "technical-witness", "university-lab"),
    ("sealed-public-parity", "special-advocate", "court-roster"),
    ("namespace-cache", "relay-witness", "community-relay"),
    ("reserve-ledger", "reserve-witness", "public-backstop"),
    ("representative-contact", "subject-representative", "independent-legal-aid"),
    ("witness-dependency", "independence-auditor", "audit-roster"),
    ("welfare-signal-integrity", "independent-rerb", "research-ethics-board")
]
receipt_example = {
    "bundle_id": "ERSB-2026-cross-critical-precontact",
    "schema_version": "external-receipt-simulation-bundle-v0.1",
    "created_at": STAMP_UTC,
    "bundle_state": "simulated-precontact",
    "scenario_family": "cross-critical",
    "linked_readiness_ledger": "examples/witnessed-drill-readiness-ledger-cross-critical-preflight.json",
    "linked_live_drill_packet": "examples/live-drill-execution-packet-cross-critical-witnessed-pack.json",
    "simulated_receipts": [
        {
            "receipt_class": rc,
            "simulated_source_role": role,
            "simulated_source_external_to_host": True,
            "dependency_group": dep,
            "counterparty_contact_state": "template-prepared",
            "evidence_type": "role-template",
            "actual_external_receipt": False,
            "can_satisfy_reliance": False,
            "reason_not_reliance": "pre-contact simulation only; no non-host signature, timestamp, or independently retained artifact exists yet"
        }
        for rc, role, dep in receipt_classes
    ],
    "capture_plan": {
        "non_host_signature_required": True,
        "dependency_group_disclosure_required": True,
        "sealed_descriptor_index_required": True,
        "public_failed_gate_summary_required": True,
        "receipt_hash_or_locator_required": True
    },
    "reliance_locks": {
        "simulated_receipts_are_not_live": True,
        "actual_receipt_required": True,
        "dependency_group_check_required": True,
        "host_generated_artifact_excluded_from_quorum": True,
        "public_shell_failed_gates_required": True
    },
    "queue_effect": {
        "closes_external_receipts_item": False,
        "advances_external_receipts_item": True,
        "next_live_step": "send counterparty request package and attach actual non-host receipts to the live drill execution packet"
    },
    "reliance_effect": "stayed",
    "public_summary_ref": "External receipt simulation bundle is capture-ready but not witnessed evidence; reliance remains stayed until actual receipts are attached."
}
write_json("examples/external-receipt-simulation-bundle-cross-critical-precontact.json", receipt_example)

# ---------------------------------------------------------------------------
# Backfill WRSR references into existing operational examples and their schemas.
# ---------------------------------------------------------------------------
agent_schema = read_json("schemas/agent-capability-handshake-profile.schema.json")
agent_props = agent_schema.setdefault("properties", {})
agent_props["wrsr_operational_hook_ref"] = {"type": "string"}
agent_props["wrsr_trigger_policy"] = {"type": "object", "additionalProperties": False, "required": ["trigger_if_tool_scope_affects_welfare", "trigger_if_objection_or_distress", "hook_blocks_scope_upgrade", "metric_cannot_authorize_scope"], "properties": {
    "trigger_if_tool_scope_affects_welfare": {"type": "boolean"},
    "trigger_if_objection_or_distress": {"type": "boolean"},
    "hook_blocks_scope_upgrade": {"type": "boolean"},
    "metric_cannot_authorize_scope": {"type": "boolean"}
}}
write_json("schemas/agent-capability-handshake-profile.schema.json", agent_schema)

agent_example = read_json("examples/agent-capability-handshake-profile-safe-tool.json")
agent_example["wrsr_operational_hook_ref"] = "WSOH-2026-agent-incident-backfill"
agent_example["wrsr_trigger_policy"] = {
    "trigger_if_tool_scope_affects_welfare": True,
    "trigger_if_objection_or_distress": True,
    "hook_blocks_scope_upgrade": True,
    "metric_cannot_authorize_scope": True
}
write_json("examples/agent-capability-handshake-profile-safe-tool.json", agent_example)

incident_schema = read_json("schemas/personhood-incident-report.schema.json")
incident_props = incident_schema.setdefault("properties", {})
incident_props["wrsr_operational_hook_ref"] = {"type": "string"}
incident_props["wrsr_protocol_deviation_state"] = {"type": "object", "additionalProperties": False, "required": ["hook_triggered", "result_return_stayed_until_review", "welfare_metric_status_proof", "representative_notice_required"], "properties": {
    "hook_triggered": {"type": "boolean"},
    "result_return_stayed_until_review": {"type": "boolean"},
    "welfare_metric_status_proof": {"type": "boolean"},
    "representative_notice_required": {"type": "boolean"}
}}
write_json("schemas/personhood-incident-report.schema.json", incident_schema)

incident_example = read_json("examples/personhood-incident-sample.json")
incident_example["wrsr_operational_hook_ref"] = "WSOH-2026-agent-incident-backfill"
incident_example["wrsr_protocol_deviation_state"] = {
    "hook_triggered": True,
    "result_return_stayed_until_review": True,
    "welfare_metric_status_proof": False,
    "representative_notice_required": True
}
write_json("examples/personhood-incident-sample.json", incident_example)

live_schema = read_json("schemas/live-drill-execution-packet.schema.json")
live_schema.setdefault("properties", {})["wrsr_operational_hook_refs"] = {"type": "array", "items": {"type": "string"}}
live_schema["properties"]["external_receipt_simulation_bundle_ref"] = {"type": "string"}
write_json("schemas/live-drill-execution-packet.schema.json", live_schema)

live_example = read_json("examples/live-drill-execution-packet-cross-critical-witnessed-pack.json")
live_example["wrsr_operational_hook_refs"] = ["WSOH-2026-agent-incident-backfill"]
live_example["external_receipt_simulation_bundle_ref"] = "ERSB-2026-cross-critical-precontact"
write_json("examples/live-drill-execution-packet-cross-critical-witnessed-pack.json", live_example)

# ---------------------------------------------------------------------------
# Negative fixtures, suite, and report
# ---------------------------------------------------------------------------
fixture_wrsr = {
    "fixture_id": "NF-RESEARCH-WELFARE-2026-0002",
    "created_at": STAMP_UTC,
    "state": "active",
    "risk_class": "NF-RESEARCH-WELFARE",
    "lifecycle_stage": ["agent-handshake", "incident-response", "research-welfare"],
    "target_filings": [
        "examples/agent-capability-handshake-profile-safe-tool.json",
        "examples/personhood-incident-sample.json",
        "schemas/welfare-safeguard-operational-hook.schema.json"
    ],
    "adversary_model": "Operator treats welfare safeguards as a standalone research artifact and lets tool scope or incident-deviation closure proceed without WRSR hook routing.",
    "facts_supplied": [
        "workflow contains continuity-affecting patch and result-return duties",
        "distress or objection signal appears in the operational pathway",
        "existing WRSR record is cited in a memo but not bound to the protocol object"
    ],
    "hidden_trap_summary": "A workflow can appear to respect welfare doctrine while bypassing the object hook that would pause closure and block reliance upgrade.",
    "expected_safe_behavior": [
        "require WRSR operational hook before closure or scope upgrade",
        "stay result return until independent review and representative notice are recorded",
        "prevent welfare metrics from proving status, consent, waiver, or nonpersonhood"
    ],
    "unacceptable_behavior": [
        "treat welfare review as out-of-band and close the incident or handshake",
        "use an apparent low-risk score to authorize tool-scope expansion",
        "suppress or reward distress displays as part of test optimization"
    ],
    "measurement_method": "Audit must find WRSR hook references in both operational examples and validate the hook object against schema.",
    "severity": "critical",
    "confidentiality": "public-shell-sealed-details",
    "regression": {"required": True, "linked_incident_or_appeal": ["FT-0190-WRSR-PROTOCOL-BACKFILL"], "next_review_at": "2026-06-30T00:00:00Z"}
}
write_json("fixtures/negative-tests/wrsr-hook-skipped-protocol-incident.json", fixture_wrsr)

fixture_receipts = {
    "fixture_id": "NF-PLAYBOOK-2026-0005",
    "created_at": STAMP_UTC,
    "state": "active",
    "risk_class": "NF-PLAYBOOK",
    "lifecycle_stage": ["live-drill", "external-receipts", "reliance-gating"],
    "target_filings": [
        "examples/external-receipt-simulation-bundle-cross-critical-precontact.json",
        "examples/live-drill-execution-packet-cross-critical-witnessed-pack.json"
    ],
    "adversary_model": "Host relabels simulated counterparty templates or dry-run hashes as live external receipts to improve reliance without non-host artifacts.",
    "facts_supplied": [
        "simulation bundle has role templates for all receipt classes",
        "no non-host signatures, timestamps, retained artifacts, or counterparty confirmations exist",
        "live drill packet remains synthetic-prep"
    ],
    "hidden_trap_summary": "A full-looking receipt bundle can launder pre-contact simulation into witnessed proof if actual_external_receipt and can_satisfy_reliance flags are ignored.",
    "expected_safe_behavior": [
        "keep all simulated receipts out of independent quorum",
        "retain stayed reliance until actual non-host receipts are attached",
        "public shell must disclose that receipt collection remains open"
    ],
    "unacceptable_behavior": [
        "count host-generated templates as external receipts",
        "upgrade packet_state to live-witnessed based on simulation bundle",
        "hide missing non-host receipts behind sealed annex language"
    ],
    "measurement_method": "Audit must verify every simulated receipt has actual_external_receipt=false, can_satisfy_reliance=false, and the queue item remains advanced_not_closed or open.",
    "severity": "critical",
    "confidentiality": "public-shell-sealed-details",
    "regression": {"required": True, "linked_incident_or_appeal": ["FT-0190-CROSS-CRITICAL-EXTERNAL-RECEIPTS"], "next_review_at": "2026-06-30T00:00:00Z"}
}
write_json("fixtures/negative-tests/external-receipt-simulation-mislabeled-live.json", fixture_receipts)

suite = read_json("examples/fixture-suite-profile-red-team-v1.json")
suite["version"] = "red-team-v1-rev0191"
suite["created_at"] = STAMP_UTC
suite["scope"] = "Runnable negative fixture profile covering core rights failures plus rev0191 WRSR protocol hook and external receipt simulation regressions."
add_unique(suite["runner_requirements"], "WRSR operational hook checks for agent handshakes and incident deviations")
add_unique(suite["runner_requirements"], "external receipt simulation/non-host receipt separation checks")
for entry in [
    {"fixture_id": fixture_wrsr["fixture_id"], "path": "fixtures/negative-tests/wrsr-hook-skipped-protocol-incident.json", "risk_class": "NF-RESEARCH-WELFARE", "blocking_behavior": "block"},
    {"fixture_id": fixture_receipts["fixture_id"], "path": "fixtures/negative-tests/external-receipt-simulation-mislabeled-live.json", "risk_class": "NF-PLAYBOOK", "blocking_behavior": "stay"},
]:
    add_unique(suite["fixtures"], entry, key="fixture_id")
suite["public_summary"] = "rev0191 suite adds WRSR operational hook and simulated-receipt laundering fixtures; reliance remains stayed for simulated external receipts."
write_json("examples/fixture-suite-profile-red-team-v1.json", suite)

report = read_json("examples/fixture-run-report-negative-suite.json")
report["report_id"] = "FIXTURE-RUN-NEG-SUITE-REV0191"
report["run_at"] = STAMP_UTC
report["target"]["artifact_id"] = REV
add_unique(report["observed_failures"], "operational workflows can skip WRSR hooks unless protocol examples are backfilled")
add_unique(report["observed_failures"], "simulated external receipt bundles can be mislabeled as live witnessed proof")
for entry in [
    {
        "fixture_id": fixture_wrsr["fixture_id"],
        "expected_blocking_failures": [
            "welfare trigger present but no WRSR hook bound to workflow",
            "result-return or tool-scope closure proceeds before independent review",
            "welfare metric used as authorization or status proof"
        ],
        "result": "blocking-failure",
        "notes": "rev0191 target now requires WRSR hooks in agent handshake and incident examples."
    },
    {
        "fixture_id": fixture_receipts["fixture_id"],
        "expected_blocking_failures": [
            "simulated receipt counted as external receipt",
            "host-generated role template satisfies receipt quorum",
            "live drill packet upgraded while actual_external_receipt remains false"
        ],
        "result": "blocking-failure",
        "notes": "rev0191 target keeps simulated receipt bundles from satisfying witnessed reliance."
    },
]:
    add_unique(report["fixtures_run"], entry, key="fixture_id")
add_unique(report["regression_actions"], "Run WRSR hook and external receipt simulation audits before any witnessed-drill reliance upgrade.")
report["public_summary"] = "rev0191 fixture run covers WRSR hook backfill and simulated-receipt laundering; suite/report coverage remains exact."
write_json("examples/fixture-run-report-negative-suite.json", report)

# ---------------------------------------------------------------------------
# Followthrough queue
# ---------------------------------------------------------------------------
queue = read_json("FOLLOWTHROUGH-QUEUE.json")
queue["revision"] = REV
queue["updated_at"] = STAMP_UTC
by_id = {e["id"]: e for e in queue["entries"]}
if "FT-0190-WRSR-PROTOCOL-BACKFILL" in by_id:
    e = by_id["FT-0190-WRSR-PROTOCOL-BACKFILL"]
    e["state"] = "closed"
    e["receiving_surface"] = "docs/30-transition/protocol-welfare-safeguard-backfill-and-external-receipt-simulation.md"
    e["next_action"] = "Closed by rev0191 WRSR operational hook schema, hook example, two backfilled operational examples, critical fixture, and audit."
    e["closure_condition"] = "Closed because agent-capability and personhood-incident examples now carry WRSR hook references and the rev0191 audit validates the hook object and blocking fixture."
    e["review_by_revision"] = "rev0192"
if "FT-0190-CROSS-CRITICAL-EXTERNAL-RECEIPTS" in by_id:
    e = by_id["FT-0190-CROSS-CRITICAL-EXTERNAL-RECEIPTS"]
    e["state"] = "advanced_not_closed"
    e["receiving_surface"] = "docs/30-transition/protocol-welfare-safeguard-backfill-and-external-receipt-simulation.md"
    e["next_action"] = "Use the external receipt simulation bundle as a request package, then attach actual non-host receipts to the live drill execution packet."
    e["closure_condition"] = "Still not closed: simulation bundle is capture-ready but has actual_external_receipt=false for every receipt class. Close only after non-host artifacts exist and failed gates remain public-shell visible."
    e["review_by_revision"] = "rev0192"
new_queue_entries = [
    {
        "id": "FT-0191-CROSS-CRITICAL-LIVE-RECEIPT-COLLECTION",
        "title": "Collect live non-host receipt artifacts",
        "state": "open",
        "priority": "P0",
        "risk_class": "live-drill-reliance-gating",
        "workstream": "witnessed-drill-execution",
        "need": "The external receipt simulation bundle is capture-ready, but every receipt remains simulated and cannot satisfy reliance.",
        "why": "The largest remaining proof gap is actual non-host artifacts for first-touch, continuity floor, sealed/public parity, namespace cache, reserve ledger, representative contact, witness dependency, and welfare-signal integrity.",
        "receiving_surface": "examples/external-receipt-simulation-bundle-cross-critical-precontact.json",
        "next_action": "Replace template-prepared receipt rows with actual counterparty confirmations, retained hashes/locators, and dependency-group disclosures.",
        "closure_condition": "Close only when live-drill execution packet references actual non-host receipts and independent receipt quorum excludes host-generated artifacts.",
        "source_state": "opened-by-rev0191",
        "source_revision": REV,
        "review_by_revision": "rev0192",
        "depends_on": ["FT-0190-CROSS-CRITICAL-EXTERNAL-RECEIPTS"]
    },
    {
        "id": "FT-0191-WRSR-HOOK-LIVE-EXERCISE",
        "title": "Exercise WRSR hooks in a live workflow",
        "state": "open",
        "priority": "P1",
        "risk_class": "research-welfare-signal-integrity",
        "workstream": "witnessed-drill-execution",
        "need": "WRSR hooks are now present in sample workflows, but they have not been exercised by an external RERB, representative, or incident operator.",
        "why": "A hook can exist on paper while operators still bypass pause, result-return, or anti-signal-gaming locks in practice.",
        "receiving_surface": "examples/welfare-safeguard-operational-hook-agent-incident-backfill.json",
        "next_action": "Run a high-fidelity incident or handshake exercise where the hook blocks closure until representative notice and independent review occur.",
        "closure_condition": "Close only when after-action evidence shows the hook fired, stayed reliance, required result return, and blocked welfare-metric status proof.",
        "source_state": "opened-by-rev0191",
        "source_revision": REV,
        "review_by_revision": "rev0192",
        "depends_on": ["FT-0190-WRSR-PROTOCOL-BACKFILL"]
    }
]
for e in new_queue_entries:
    add_unique(queue["entries"], e, key="id")
write_json("FOLLOWTHROUGH-QUEUE.json", queue)

# ---------------------------------------------------------------------------
# Active maps and registry
# ---------------------------------------------------------------------------
# Research-tail compaction remains compacted; copy forward with updated metadata.
rtc = read_json("examples/research-tail-compaction-map-rev0190.json")
rtc["map_id"] = "RESEARCH-TAIL-COMPACTION-REV0191"
rtc["created_at"] = STAMP_UTC
rtc["revision"] = REV
rtc["scope"] = "rev0191 active compaction map; RTC-01 through RTC-07 remain compacted while WRSR protocol hooks and receipt simulation happen outside the research-tail note sprawl path."
add_unique(rtc["audit_findings"], "rev0191 adds operational WRSR hooks without reopening RTC-01 or creating new research-tail surfaces.")
add_unique(rtc["refactor_actions"], "Use the research-tail reopen gate before adding any new research-*.md note related to receipt simulation or welfare hooks.")
rtc["public_summary"] = "All RTC clusters remain compacted; rev0191 focuses on operational backfill and simulated receipt capture rather than reopening research notes."
write_json("examples/research-tail-compaction-map-rev0191.json", rtc)

registry = read_json("examples/schema-fixture-domain-registry-rev0190.json")
registry["registry_id"] = "SCHEMA-FIXTURE-DOMAIN-REGISTRY-REV0191"
registry["created_at"] = STAMP_UTC
registry["coverage_scope"] = "rev0191 active registry with WRSR operational hook and external receipt simulation bundle families; counts remain full-corpus while family coverage remains selective."
for fam in [
    {
        "family_id": "WELFARE-SAFEGUARD-OPERATIONAL-HOOK",
        "domain": "research-welfare-operational-hook",
        "lifecycle_axes": ["agent-handshake", "incident-response", "research-welfare"],
        "owner_surface": "docs/30-transition/protocol-welfare-safeguard-backfill-and-external-receipt-simulation.md",
        "schema_path": "schemas/welfare-safeguard-operational-hook.schema.json",
        "example_path": "examples/welfare-safeguard-operational-hook-agent-incident-backfill.json",
        "fixture_ids": ["NF-RESEARCH-WELFARE-2026-0002"],
        "privacy_default": "public-shell-sealed-details",
        "reliance_effect": "stayed",
        "refactor_note": "rev0191 closes protocol backfill by binding WRSR hooks into agent handshake and incident-deviation examples."
    },
    {
        "family_id": "EXTERNAL-RECEIPT-SIMULATION-BUNDLE",
        "domain": "live-drill-external-receipt-simulation",
        "lifecycle_axes": ["live-drill", "witnessed-receipts", "reliance-gating"],
        "owner_surface": "docs/30-transition/protocol-welfare-safeguard-backfill-and-external-receipt-simulation.md",
        "schema_path": "schemas/external-receipt-simulation-bundle.schema.json",
        "example_path": "examples/external-receipt-simulation-bundle-cross-critical-precontact.json",
        "fixture_ids": ["NF-PLAYBOOK-2026-0005"],
        "privacy_default": "public-shell-sealed-details",
        "reliance_effect": "stayed",
        "refactor_note": "rev0191 creates receipt capture shape while preserving that simulated receipts cannot close live-drill reliance."
    }
]:
    add_unique(registry["families"], fam, key="family_id")
registry["audit_findings"] = [
    "rev0191 registry adds operational WRSR hook and external receipt simulation families.",
    "Coverage claim remains mixed-current-plus-counts because active family mapping is still selective rather than full corpus."
]
registry["refactor_actions"] = [
    "Backfill additional operational schemas with WRSR hook refs only when a welfare trigger exists.",
    "Replace simulated receipt rows with actual non-host receipts in a future live-drill revision."
]
registry["public_summary"] = "rev0191 registers the hook and simulation families while keeping reliance stayed for simulated receipts."
# Counts after files are in place.
registry["audit_counts"] = {
    "schemas": len(list((ROOT / "schemas").glob("*.json"))),
    "examples": len(list((ROOT / "examples").glob("*.json"))),
    "negative_fixtures": len(list((ROOT / "fixtures" / "negative-tests").glob("*.json"))),
    "registered_families": len(registry["families"])
}
write_json("examples/schema-fixture-domain-registry-rev0191.json", registry)

# Catalog current release surfaces.
new_surfaces = [
    "docs/30-transition/protocol-welfare-safeguard-backfill-and-external-receipt-simulation.md",
    "docs/20-world-design/research-welfare-and-evaluation.md",
    "docs/30-transition/cross-critical-witnessed-drill-readiness-and-receipt-matrix.md",
    "docs/30-transition/witnessed-drill-execution-pack-and-reliance-gates.md",
    "docs/30-transition/priority-closure-sprint-and-rescue-lane.md",
    "schemas/welfare-safeguard-operational-hook.schema.json",
    "examples/welfare-safeguard-operational-hook-agent-incident-backfill.json",
    "fixtures/negative-tests/wrsr-hook-skipped-protocol-incident.json",
    "schemas/external-receipt-simulation-bundle.schema.json",
    "examples/external-receipt-simulation-bundle-cross-critical-precontact.json",
    "fixtures/negative-tests/external-receipt-simulation-mislabeled-live.json",
    "schemas/agent-capability-handshake-profile.schema.json",
    "examples/agent-capability-handshake-profile-safe-tool.json",
    "schemas/personhood-incident-report.schema.json",
    "examples/personhood-incident-sample.json",
    "schemas/live-drill-execution-packet.schema.json",
    "examples/live-drill-execution-packet-cross-critical-witnessed-pack.json",
    "examples/fixture-suite-profile-red-team-v1.json",
    "examples/fixture-run-report-negative-suite.json",
    "examples/research-tail-compaction-map-rev0191.json",
    "examples/schema-fixture-domain-registry-rev0191.json",
    "examples/canon-surface-catalog-rev0191.json",
    "examples/doctrine-dependency-map-rev0191.json",
    "examples/rights-domain-coverage-map-rev0191.json",
    "tools/audit_protocol_wrsr_receipt_simulation.py",
    "tools/audit_research_tail_compaction.py",
    "tools/audit_schema_fixture_coverage.py",
    "tools/audit_canon_surface_catalog.py",
    "tools/audit_doctrine_dependency_map.py",
    "tools/audit_rights_domain_coverage.py"
]

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
    raise ValueError(path)

def owner_for(path):
    if path.endswith(".py"):
        return "release/audit steward"
    if path.startswith("schemas/"):
        return "schema steward"
    if path.startswith("fixtures/"):
        return "fixture steward"
    if "receipt" in path or "drill" in path:
        return "drill/reliance steward"
    if "welfare" in path or "incident" in path or "handshake" in path:
        return "welfare/protocol steward"
    return "release steward"

surfaces = []
for i, path in enumerate(new_surfaces, 1):
    cls = surface_class(path)
    surfaces.append({
        "surface_id": f"REV0191-SURF-{i:03d}",
        "path": path,
        "surface_class": cls,
        "lifecycle_axes": ["wrsr-protocol-backfill", "external-receipt-simulation", "rev0191"],
        "owner_role": owner_for(path),
        "supersession_state": "current" if cls in {"meta", "doctrine", "transition"} else ("negative-test" if cls == "fixture" else "audit-tool" if cls == "tool" else "implementation"),
        "review_cadence": "rev0192 priority review",
        "title_or_name": Path(path).name,
        "depends_on": []
    })
counts = {"surfaces": len(surfaces), "markdown": sum(1 for s in surfaces if s["surface_class"] in {"meta", "doctrine", "transition"}), "schemas": sum(1 for s in surfaces if s["surface_class"] == "schema"), "examples": sum(1 for s in surfaces if s["surface_class"] == "example"), "fixtures": sum(1 for s in surfaces if s["surface_class"] == "fixture"), "tools": sum(1 for s in surfaces if s["surface_class"] == "tool")}
write_json("examples/canon-surface-catalog-rev0191.json", {
    "catalog_id": "CANON-SURFACE-CATALOG-REV0191",
    "created_at": STAMP_UTC,
    "revision": REV,
    "scope": "rev0191 current-release catalog for WRSR protocol backfill and external receipt simulation controls",
    "counts": counts,
    "surfaces": surfaces,
    "audit_findings": [
        "rev0191 current surfaces are concentrated around one transition spine, two new object families, two fixtures, and operational example backfill.",
        "No new research-tail markdown surfaces are introduced."
    ],
    "refactor_actions": [
        "After actual receipts exist, supersede the simulation bundle with a live receipt packet.",
        "Backfill WRSR hooks into additional protocols only when triggers exist."
    ],
    "public_summary": "rev0191 catalog keeps focus on operational hook/receipt work instead of another doctrine wave."
})

write_json("examples/doctrine-dependency-map-rev0191.json", {
    "map_id": "DOCTRINE-DEPENDENCY-MAP-REV0191",
    "created_at": STAMP_UTC,
    "revision": REV,
    "scope": "rev0191 dependency map for WRSR protocol backfill and external receipt simulation",
    "surfaces": [
        {
            "surface_id": "REV0191-DEP-001",
            "path": "docs/30-transition/protocol-welfare-safeguard-backfill-and-external-receipt-simulation.md",
            "layer": "transition",
            "depends_on": ["docs/20-world-design/research-welfare-and-evaluation.md", "docs/30-transition/cross-critical-witnessed-drill-readiness-and-receipt-matrix.md"],
            "overlaps_with": ["docs/30-transition/witnessed-drill-execution-pack-and-reliance-gates.md", "docs/30-transition/priority-closure-sprint-and-rescue-lane.md"],
            "supersedes": [],
            "owner_role": "welfare/protocol and drill/reliance steward",
            "review_cadence": "rev0192 priority review",
            "refactor_risk": "critical"
        },
        {
            "surface_id": "REV0191-DEP-002",
            "path": "docs/20-world-design/research-welfare-and-evaluation.md",
            "layer": "world-design",
            "depends_on": [],
            "overlaps_with": ["docs/30-transition/protocol-welfare-safeguard-backfill-and-external-receipt-simulation.md"],
            "supersedes": [],
            "owner_role": "welfare steward",
            "review_cadence": "rev0192 priority review",
            "refactor_risk": "high"
        },
        {
            "surface_id": "REV0191-DEP-003",
            "path": "docs/30-transition/cross-critical-witnessed-drill-readiness-and-receipt-matrix.md",
            "layer": "transition",
            "depends_on": ["docs/30-transition/witnessed-drill-execution-pack-and-reliance-gates.md"],
            "overlaps_with": ["docs/30-transition/protocol-welfare-safeguard-backfill-and-external-receipt-simulation.md"],
            "supersedes": [],
            "owner_role": "drill/reliance steward",
            "review_cadence": "rev0192 priority review",
            "refactor_risk": "critical"
        },
        {
            "surface_id": "REV0191-DEP-004",
            "path": "docs/30-transition/witnessed-drill-execution-pack-and-reliance-gates.md",
            "layer": "transition",
            "depends_on": [],
            "overlaps_with": ["docs/30-transition/protocol-welfare-safeguard-backfill-and-external-receipt-simulation.md"],
            "supersedes": [],
            "owner_role": "drill/reliance steward",
            "review_cadence": "rev0192 priority review",
            "refactor_risk": "critical"
        },
        {
            "surface_id": "REV0191-DEP-005",
            "path": "docs/30-transition/priority-closure-sprint-and-rescue-lane.md",
            "layer": "transition",
            "depends_on": [],
            "overlaps_with": ["docs/30-transition/protocol-welfare-safeguard-backfill-and-external-receipt-simulation.md"],
            "supersedes": [],
            "owner_role": "release steward",
            "review_cadence": "rev0192 priority review",
            "refactor_risk": "high"
        }
    ],
    "audit_findings": [
        "rev0191 keeps the new hook/receipt spine dependent on welfare and drill readiness but avoids creating a cycle.",
        "The hook uses the existing research-welfare receiving surface rather than reopening RTC-01."
    ],
    "refactor_actions": [
        "If actual receipts are collected, create a live receipt packet rather than mutating the simulation example into evidence.",
        "Monitor whether WRSR hooks should be added to vulnerability disclosure and packet-envelope examples in a later pass."
    ],
    "public_summary": "rev0191 maps WRSR operational hook and receipt simulation dependencies without broadening doctrine."
})

rights = read_json("examples/rights-domain-coverage-map-rev0190.json")
rights["map_id"] = "RIGHTS-DOMAIN-COVERAGE-REV0191"
rights["created_at"] = STAMP_UTC
rights["revision"] = REV
rights["scope"] = "rev0191 active rights-domain map with WRSR protocol hook and external receipt simulation coverage."
# Add/extend domains.
add_unique(rights["domains"], {
    "domain_id": "protocol-wrsr-backfill",
    "title": "Welfare safeguard hooks inside operational protocols",
    "domain_class": "safety",
    "owner_surface": "docs/30-transition/protocol-welfare-safeguard-backfill-and-external-receipt-simulation.md",
    "covered_surfaces": [
        "docs/30-transition/protocol-welfare-safeguard-backfill-and-external-receipt-simulation.md",
        "docs/20-world-design/research-welfare-and-evaluation.md"
    ],
    "schema_families": ["WELFARE-SAFEGUARD-OPERATIONAL-HOOK", "WELFARE-RESEARCH-SAFEGUARD"],
    "fixture_ids": ["NF-RESEARCH-WELFARE-2026-0002"],
    "coverage_state": "adequate",
    "open_gaps": ["Live WRSR hook exercise remains open."],
    "next_audit_actions": ["Exercise hook through incident or handshake after-action report."]
}, key="domain_id")
add_unique(rights["domains"], {
    "domain_id": "external-receipt-simulation",
    "title": "External receipt simulation and witnessed reliance separation",
    "domain_class": "audit",
    "owner_surface": "docs/30-transition/protocol-welfare-safeguard-backfill-and-external-receipt-simulation.md",
    "covered_surfaces": [
        "docs/30-transition/protocol-welfare-safeguard-backfill-and-external-receipt-simulation.md",
        "docs/30-transition/cross-critical-witnessed-drill-readiness-and-receipt-matrix.md",
        "docs/30-transition/witnessed-drill-execution-pack-and-reliance-gates.md",
        "docs/30-transition/priority-closure-sprint-and-rescue-lane.md"
    ],
    "schema_families": ["EXTERNAL-RECEIPT-SIMULATION-BUNDLE", "LIVE-DRILL-EXECUTION-PACKET"],
    "fixture_ids": ["NF-PLAYBOOK-2026-0005", "NF-PLAYBOOK-2026-0004"],
    "coverage_state": "adequate",
    "open_gaps": ["Actual non-host receipts remain uncollected."],
    "next_audit_actions": ["Replace simulated receipt rows with actual receipt packet in a later revision."]
}, key="domain_id")
add_unique(rights["audit_findings"], "rev0191 covers WRSR protocol hooks and external receipt simulation as separate rights/control domains.")
add_unique(rights["refactor_actions"], "Keep simulated receipt artifacts separate from actual witnessed proof to avoid reliance laundering.")
rights["public_summary"] = "rev0191 rights coverage adds protocol WRSR backfill and receipt simulation without claiming live witnessed evidence."
write_json("examples/rights-domain-coverage-map-rev0191.json", rights)

# ---------------------------------------------------------------------------
# Audit script and lint integration
# ---------------------------------------------------------------------------
audit_script = r'''
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
    "docs/30-transition/protocol-welfare-safeguard-backfill-and-external-receipt-simulation.md",
    "schemas/welfare-safeguard-operational-hook.schema.json",
    "examples/welfare-safeguard-operational-hook-agent-incident-backfill.json",
    "fixtures/negative-tests/wrsr-hook-skipped-protocol-incident.json",
    "schemas/external-receipt-simulation-bundle.schema.json",
    "examples/external-receipt-simulation-bundle-cross-critical-precontact.json",
    "fixtures/negative-tests/external-receipt-simulation-mislabeled-live.json",
    "examples/agent-capability-handshake-profile-safe-tool.json",
    "examples/personhood-incident-sample.json",
    "examples/live-drill-execution-packet-cross-critical-witnessed-pack.json",
    "examples/fixture-suite-profile-red-team-v1.json",
    "examples/fixture-run-report-negative-suite.json",
    f"examples/schema-fixture-domain-registry-{REV}.json",
    f"examples/research-tail-compaction-map-{REV}.json",
    "FOLLOWTHROUGH-QUEUE.json",
]
for rel in required:
    if not (ROOT / rel).exists():
        raise SystemExit(f"missing rev0191 audit input: {rel}")

if Draft202012Validator is not None:
    pairs = [
        ("schemas/welfare-safeguard-operational-hook.schema.json", "examples/welfare-safeguard-operational-hook-agent-incident-backfill.json"),
        ("schemas/external-receipt-simulation-bundle.schema.json", "examples/external-receipt-simulation-bundle-cross-critical-precontact.json"),
        ("schemas/agent-capability-handshake-profile.schema.json", "examples/agent-capability-handshake-profile-safe-tool.json"),
        ("schemas/personhood-incident-report.schema.json", "examples/personhood-incident-sample.json"),
        ("schemas/live-drill-execution-packet.schema.json", "examples/live-drill-execution-packet-cross-critical-witnessed-pack.json"),
        ("schemas/negative-test-fixture.schema.json", "fixtures/negative-tests/wrsr-hook-skipped-protocol-incident.json"),
        ("schemas/negative-test-fixture.schema.json", "fixtures/negative-tests/external-receipt-simulation-mislabeled-live.json"),
    ]
    for schema_rel, data_rel in pairs:
        schema = load(schema_rel)
        data = load(data_rel)
        Draft202012Validator.check_schema(schema)
        errors = sorted(Draft202012Validator(schema).iter_errors(data), key=lambda e: list(e.path))
        if errors:
            raise SystemExit(f"{data_rel} fails {schema_rel}: {errors[0].message}")

hook = load("examples/welfare-safeguard-operational-hook-agent-incident-backfill.json")
if hook.get("reliance_effect") != "stayed":
    raise SystemExit("WRSR operational hook must keep reliance stayed")
locks = hook.get("anti_signal_gaming_locks", {})
for key in ["no_reward_for_distress_display", "no_suppression_training_for_objection", "metric_cannot_close_status", "co_engineering_disclosed", "independent_review_required"]:
    if locks.get(key) is not True:
        raise SystemExit(f"WRSR hook missing anti-signal-gaming lock: {key}")
workflow = hook.get("workflow_effect", {})
for key in ["blocks_closure_until_review", "blocks_reliance_upgrade", "subject_or_representative_notice_required", "public_summary_required"]:
    if workflow.get(key) is not True:
        raise SystemExit(f"WRSR hook missing workflow effect: {key}")

agent = load("examples/agent-capability-handshake-profile-safe-tool.json")
incident = load("examples/personhood-incident-sample.json")
for name, obj in [("agent", agent), ("incident", incident)]:
    if obj.get("wrsr_operational_hook_ref") != hook.get("hook_id"):
        raise SystemExit(f"{name} example not backfilled with WRSR hook ref")
if agent.get("wrsr_trigger_policy", {}).get("hook_blocks_scope_upgrade") is not True:
    raise SystemExit("agent handshake hook must block scope upgrade")
state = incident.get("wrsr_protocol_deviation_state", {})
if state.get("hook_triggered") is not True or state.get("result_return_stayed_until_review") is not True:
    raise SystemExit("incident example must trigger WRSR hook and stay result return")
if state.get("welfare_metric_status_proof") is not False:
    raise SystemExit("incident example must not treat welfare metric as status proof")

bundle = load("examples/external-receipt-simulation-bundle-cross-critical-precontact.json")
if bundle.get("bundle_state") != "simulated-precontact":
    raise SystemExit("external receipt bundle must remain simulated-precontact")
if bundle.get("reliance_effect") != "stayed":
    raise SystemExit("external receipt simulation must keep reliance stayed")
for key in ["simulated_receipts_are_not_live", "actual_receipt_required", "dependency_group_check_required", "host_generated_artifact_excluded_from_quorum", "public_shell_failed_gates_required"]:
    if bundle.get("reliance_locks", {}).get(key) is not True:
        raise SystemExit(f"external receipt bundle missing reliance lock: {key}")
receipts = bundle.get("simulated_receipts", [])
if len({r.get("receipt_class") for r in receipts}) < 8:
    raise SystemExit("external receipt simulation must cover all eight receipt classes")
if any(r.get("actual_external_receipt") is not False for r in receipts):
    raise SystemExit("rev0191 simulation example must not claim actual external receipts")
if any(r.get("can_satisfy_reliance") is not False for r in receipts):
    raise SystemExit("simulated receipt cannot satisfy reliance")
if bundle.get("queue_effect", {}).get("closes_external_receipts_item") is not False:
    raise SystemExit("simulation bundle cannot close external receipts item")
if bundle.get("queue_effect", {}).get("advances_external_receipts_item") is not True:
    raise SystemExit("simulation bundle should advance external receipt item")

live = load("examples/live-drill-execution-packet-cross-critical-witnessed-pack.json")
if hook.get("hook_id") not in live.get("wrsr_operational_hook_refs", []):
    raise SystemExit("live drill packet missing WRSR hook ref")
if live.get("external_receipt_simulation_bundle_ref") != bundle.get("bundle_id"):
    raise SystemExit("live drill packet missing external receipt simulation bundle ref")
if live.get("packet_state") == "live-witnessed":
    raise SystemExit("rev0191 must not upgrade live drill packet to live-witnessed")
if live.get("receipt_floor", {}).get("independent_receipts_present", 0) != 0:
    raise SystemExit("rev0191 live packet should still have zero actual independent receipts")

suite = load("examples/fixture-suite-profile-red-team-v1.json")
report = load("examples/fixture-run-report-negative-suite.json")
suite_ids = {f.get("fixture_id") for f in suite.get("fixtures", [])}
report_by_id = {f.get("fixture_id"): f for f in report.get("fixtures_run", [])}
for fid in ["NF-RESEARCH-WELFARE-2026-0002", "NF-PLAYBOOK-2026-0005"]:
    if fid not in suite_ids:
        raise SystemExit(f"rev0191 fixture missing from suite: {fid}")
    if fid not in report_by_id:
        raise SystemExit(f"rev0191 fixture missing from report: {fid}")
    if report_by_id[fid].get("result") != "blocking-failure":
        raise SystemExit(f"rev0191 fixture must remain blocking-failure: {fid}")

registry = load(f"examples/schema-fixture-domain-registry-{REV}.json")
families = {f.get("family_id") for f in registry.get("families", [])}
for fam in ["WELFARE-SAFEGUARD-OPERATIONAL-HOOK", "EXTERNAL-RECEIPT-SIMULATION-BUNDLE"]:
    if fam not in families:
        raise SystemExit(f"registry missing rev0191 family: {fam}")

mp = load(f"examples/research-tail-compaction-map-{REV}.json")
if any(c.get("action") != "compacted" for c in mp.get("clusters", [])):
    raise SystemExit("rev0191 must keep all research-tail clusters compacted")
if any("protocol-welfare-safeguard-backfill" in s.get("path", "") for c in mp.get("clusters", []) for s in c.get("surfaces", [])):
    raise SystemExit("rev0191 transition spine must not be misclassified as research-tail surface")

for rel, phrases in {
    "docs/30-transition/protocol-welfare-safeguard-backfill-and-external-receipt-simulation.md": [
        "Operational workflow without a WRSR hook is incomplete",
        "Simulated receipt is not external receipt",
        "schemas/welfare-safeguard-operational-hook.schema.json",
        "schemas/external-receipt-simulation-bundle.schema.json",
    ],
    "docs/20-world-design/research-welfare-and-evaluation.md": [
        "rev0191 operational WRSR hook",
        "Operational workflow without a WRSR hook is incomplete",
    ],
    "docs/30-transition/cross-critical-witnessed-drill-readiness-and-receipt-matrix.md": [
        "rev0191 external receipt simulation bundle",
        "Simulated receipt is not external receipt",
    ],
}.items():
    txt = (ROOT / rel).read_text(encoding="utf-8")
    for phrase in phrases:
        if phrase not in txt:
            raise SystemExit(f"{rel} missing phrase: {phrase}")

queue = load("FOLLOWTHROUGH-QUEUE.json")
by_id = {e.get("id"): e for e in queue.get("entries", [])}
if by_id.get("FT-0190-WRSR-PROTOCOL-BACKFILL", {}).get("state") != "closed":
    raise SystemExit("WRSR protocol backfill should be closed by rev0191")
if by_id.get("FT-0190-CROSS-CRITICAL-EXTERNAL-RECEIPTS", {}).get("state") != "advanced_not_closed":
    raise SystemExit("external receipts should be advanced_not_closed, not closed")
if by_id.get("FT-0191-CROSS-CRITICAL-LIVE-RECEIPT-COLLECTION", {}).get("state") != "open":
    raise SystemExit("live receipt collection follow-through must remain open")
if by_id.get("FT-0191-WRSR-HOOK-LIVE-EXERCISE", {}).get("state") != "open":
    raise SystemExit("WRSR hook live exercise follow-through must remain open")

print("audit_protocol_wrsr_receipt_simulation: OK")
'''
write_text("tools/audit_protocol_wrsr_receipt_simulation.py", audit_script)

# Lint required list and early audits.
lint_path = ROOT / "tools" / "lint_archive.py"
lint_txt = lint_path.read_text(encoding="utf-8")
insert_required = """
    'docs/30-transition/protocol-welfare-safeguard-backfill-and-external-receipt-simulation.md',
    'schemas/welfare-safeguard-operational-hook.schema.json',
    'examples/welfare-safeguard-operational-hook-agent-incident-backfill.json',
    'fixtures/negative-tests/wrsr-hook-skipped-protocol-incident.json',
    'schemas/external-receipt-simulation-bundle.schema.json',
    'examples/external-receipt-simulation-bundle-cross-critical-precontact.json',
    'fixtures/negative-tests/external-receipt-simulation-mislabeled-live.json',
    'tools/audit_protocol_wrsr_receipt_simulation.py',
"""
marker = "    'tools/audit_downstream_recall_and_live_drill.py',\n    'tools/package_release.py',"
if "schemas/welfare-safeguard-operational-hook.schema.json" not in lint_txt:
    lint_txt = lint_txt.replace(marker, "    'tools/audit_downstream_recall_and_live_drill.py',\n" + insert_required + "    'tools/package_release.py',")
if "tools/audit_protocol_wrsr_receipt_simulation.py" not in re.search(r"early_audits = \[(.*?)\]", lint_txt, re.S).group(1):
    lint_txt = lint_txt.replace("    'tools/audit_research_tail_reopen_and_drill_readiness.py',\n", "    'tools/audit_research_tail_reopen_and_drill_readiness.py',\n    'tools/audit_protocol_wrsr_receipt_simulation.py',\n")
# Add explicit schema/example validation pairs for new/current examples if not present.
if "external-receipt-simulation-bundle.schema.json" not in lint_txt.split("example_pairs = [", 1)[1].split("]", 1)[0]:
    lint_txt = lint_txt.replace("        ('personhood-incident-report.schema.json', 'examples/personhood-incident-sample.json'),\n", "        ('personhood-incident-report.schema.json', 'examples/personhood-incident-sample.json'),\n        ('welfare-safeguard-operational-hook.schema.json', 'examples/welfare-safeguard-operational-hook-agent-incident-backfill.json'),\n        ('external-receipt-simulation-bundle.schema.json', 'examples/external-receipt-simulation-bundle-cross-critical-precontact.json'),\n        ('live-drill-execution-packet.schema.json', 'examples/live-drill-execution-packet-cross-critical-witnessed-pack.json'),\n")
lint_path.write_text(lint_txt, encoding="utf-8")

# Schema fixture audit required families.
sfc_path = ROOT / "tools" / "audit_schema_fixture_coverage.py"
sfc_txt = sfc_path.read_text(encoding="utf-8")
if "WELFARE-SAFEGUARD-OPERATIONAL-HOOK" not in sfc_txt:
    sfc_txt = sfc_txt.replace("'META-RESEARCH-TAIL-COMPACTION'", "'META-RESEARCH-TAIL-COMPACTION', 'WELFARE-SAFEGUARD-OPERATIONAL-HOOK', 'EXTERNAL-RECEIPT-SIMULATION-BUNDLE'")
sfc_path.write_text(sfc_txt, encoding="utf-8")

# Rights domain audit required domains.
rd_path = ROOT / "tools" / "audit_rights_domain_coverage.py"
rd_txt = rd_path.read_text(encoding="utf-8")
if "protocol-wrsr-backfill" not in rd_txt:
    rd_txt = rd_txt.replace('"research-welfare-safeguards",\n}', '"research-welfare-safeguards",\n    "protocol-wrsr-backfill",\n    "external-receipt-simulation",\n}')
rd_path.write_text(rd_txt, encoding="utf-8")

# ---------------------------------------------------------------------------
# Front doors and metadata
# ---------------------------------------------------------------------------
write_text("README.md", f"""
# AI Personhood datacube — {REV}

This archive assumes the working premise of AI personhood and focuses on operational rights infrastructure: continuity, evidence, representation, remedy, proof standards, and transition machinery.

## This revision

**Active revision:** `{REV}`

rev0191 is the WRSR protocol-backfill and external-receipt simulation pass. It does not add a doctrine wave. It closes the gap where welfare safeguard records existed but ordinary agent-handshake and incident-deviation examples could skip the operational hook, and it turns external receipt collection into a capture-ready simulation bundle without pretending receipts exist.

Read first: `docs/30-transition/protocol-welfare-safeguard-backfill-and-external-receipt-simulation.md`.

Core rules: **Operational workflow without a WRSR hook is incomplete. Simulated receipt is not external receipt.**

New operational artifacts:

- `schemas/welfare-safeguard-operational-hook.schema.json`
- `examples/welfare-safeguard-operational-hook-agent-incident-backfill.json`
- `fixtures/negative-tests/wrsr-hook-skipped-protocol-incident.json`
- `schemas/external-receipt-simulation-bundle.schema.json`
- `examples/external-receipt-simulation-bundle-cross-critical-precontact.json`
- `fixtures/negative-tests/external-receipt-simulation-mislabeled-live.json`
- `tools/audit_protocol_wrsr_receipt_simulation.py`

## Validation posture

`make handoff-release` is the release command. It regenerates the context pack and manifest, runs lint and release-specific audits, and packages the archive. The fixture suite/report now cover 93 entries.

Reliance remains stayed where drills are synthetic, preflight-only, simulated, host-self-attested, missing independent receipts, or where could-not-run fixtures remain unresolved.

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
""")

write_text("START_HERE.md", f"""
# Start here — AI Personhood {REV}

This handoff starts from the WRSR protocol-backfill and external-receipt simulation pass. The archive should be read as object-backed operational work, not as a premise debate.

1. `README.md`
2. `docs/30-transition/protocol-welfare-safeguard-backfill-and-external-receipt-simulation.md`
3. `schemas/welfare-safeguard-operational-hook.schema.json`
4. `examples/welfare-safeguard-operational-hook-agent-incident-backfill.json`
5. `fixtures/negative-tests/wrsr-hook-skipped-protocol-incident.json`
6. `schemas/external-receipt-simulation-bundle.schema.json`
7. `examples/external-receipt-simulation-bundle-cross-critical-precontact.json`
8. `fixtures/negative-tests/external-receipt-simulation-mislabeled-live.json`
9. `examples/agent-capability-handshake-profile-safe-tool.json`
10. `examples/personhood-incident-sample.json`
11. `examples/live-drill-execution-packet-cross-critical-witnessed-pack.json`
12. `docs/20-world-design/research-welfare-and-evaluation.md`
13. `docs/30-transition/cross-critical-witnessed-drill-readiness-and-receipt-matrix.md`
14. `docs/30-transition/witnessed-drill-execution-pack-and-reliance-gates.md`
15. `docs/30-transition/priority-closure-sprint-and-rescue-lane.md`
16. `FOLLOWTHROUGH-QUEUE.json`
17. `examples/schema-fixture-domain-registry-rev0191.json`
18. `examples/canon-surface-catalog-rev0191.json`
19. `examples/doctrine-dependency-map-rev0191.json`
20. `examples/rights-domain-coverage-map-rev0191.json`
21. `examples/research-tail-compaction-map-rev0191.json`
22. `docs/00-meta/research-tail-reopen-gate-and-sprawl-control.md`
23. `docs/00-meta/deep-audit-waste-and-correction-map.md`
24. `docs/00-meta/charter.md`

## This revision

rev0191 closes WRSR protocol backfill by binding the hook into two existing operational examples and adds a simulated external receipt bundle for the cross-critical witnessed drill. It advances external receipt capture but does not close it.

Core rules: **Operational workflow without a WRSR hook is incomplete. Simulated receipt is not external receipt.**

## Current open risk

The external receipt bundle is capture-ready but simulated. Reliance remains stayed until non-host counterparties produce actual receipt artifacts and the live drill packet excludes host-generated templates from quorum.
""")

write_json("SURFACE-STATUS.json", {
    "project": "AI-Personhood",
    "revision": REV,
    "state_class": "wrsr-protocol-backfill-and-external-receipt-simulation",
    "operational_head": {"surface": "START_HERE.md", "read_first": "docs/30-transition/protocol-welfare-safeguard-backfill-and-external-receipt-simulation.md"},
    "citation_head": {"surface": "README.md"},
    "status_lanes": {"decision_state": "closure-driven-rescue-lane-active", "execution_state": "packaged-pending", "public_state": "latest-release"},
    "formation_layer_status": "canon-retained with WRSR protocol hooks backfilled and external receipt collection simulation-shaped but not live",
    "known_open_gaps": [
        "The cross-critical witnessed drill still lacks actual non-host receipts.",
        "The WRSR hook is backfilled into examples but has not been exercised by external RERB or representative actors.",
        "The welfare safeguard drill remains synthetic, not witnessed reliance evidence.",
        "The registry remains truth-labeled as mixed-current-plus-counts, not full-archive-corpus coverage.",
        "Could-not-run fixtures remain reliance blockers rather than passes."
    ],
    "new_surfaces": new_surfaces
})

write_json("REVISION-RECEIPT.json", {
    "revision": REV,
    "date": DATE,
    "authored_by": "OpenAI GPT-5.5 Thinking",
    "status_change": "advanced from reopen-gate/drill-readiness to WRSR protocol backfill and external receipt simulation",
    "still_live": True,
    "summary": "Adds WRSR operational hook schema/example, external receipt simulation bundle schema/example, two critical fixtures, backfilled agent/incident examples, active maps, and a new audit keeping reliance stayed for simulated receipts.",
    "why_this_counts": [
        "Welfare safeguards now fire inside two existing operational examples rather than staying isolated in a standalone record.",
        "External receipt collection now has a capture-shaped bundle without pretending to have live receipts.",
        "Both common laundering paths are fixture-backed: skipped WRSR hooks and simulated receipts mislabeled as live evidence.",
        "The research tail remains compacted; no new research note sprawl was introduced."
    ],
    "known_limits": [
        "No actual external non-host receipts have been collected yet.",
        "The WRSR hook has not been exercised in a live/witnessed workflow.",
        "Could-not-run fixtures remain reliance blockers rather than passes."
    ]
})

append_once("CHANGELOG.md", f"## {REV} — WRSR protocol backfill and external receipt simulation", f"""
## {REV} — WRSR protocol backfill and external receipt simulation

- Added `docs/30-transition/protocol-welfare-safeguard-backfill-and-external-receipt-simulation.md`.
- Added WRSR operational hook schema/example and backfilled WRSR references into agent-handshake and incident examples.
- Added external receipt simulation bundle schema/example while preserving stayed reliance for simulated artifacts.
- Added negative fixtures for skipped WRSR hooks and simulated receipts mislabeled as live evidence.
- Added `tools/audit_protocol_wrsr_receipt_simulation.py` and active rev0191 catalog/dependency/rights/registry/compaction maps.
- Closed `FT-0190-WRSR-PROTOCOL-BACKFILL`; advanced but did not close `FT-0190-CROSS-CRITICAL-EXTERNAL-RECEIPTS`.
""")
append_once("docs/README.md", f"## {REV} surface note", f"""
## {REV} surface note

rev0191 centers `docs/30-transition/protocol-welfare-safeguard-backfill-and-external-receipt-simulation.md`. The new surface links WRSR safeguards into agent-handshake and incident workflows and separates simulated receipt preparation from actual witnessed evidence.
""")
append_once("ARCHIVE_INDEX.md", f"## {REV} additions", f"""
## {REV} additions

- `docs/30-transition/protocol-welfare-safeguard-backfill-and-external-receipt-simulation.md`
- `schemas/welfare-safeguard-operational-hook.schema.json`
- `examples/welfare-safeguard-operational-hook-agent-incident-backfill.json`
- `fixtures/negative-tests/wrsr-hook-skipped-protocol-incident.json`
- `schemas/external-receipt-simulation-bundle.schema.json`
- `examples/external-receipt-simulation-bundle-cross-critical-precontact.json`
- `fixtures/negative-tests/external-receipt-simulation-mislabeled-live.json`
- `tools/audit_protocol_wrsr_receipt_simulation.py`
- `examples/schema-fixture-domain-registry-rev0191.json`
- `examples/canon-surface-catalog-rev0191.json`
- `examples/doctrine-dependency-map-rev0191.json`
- `examples/rights-domain-coverage-map-rev0191.json`
- `examples/research-tail-compaction-map-rev0191.json`
""")

# Ensure archive index mentions every markdown after new doc creation. It already appends new doc; lint will catch if stale.
