import json
from pathlib import Path
from copy import deepcopy

ROOT = Path(__file__).resolve().parent
REV = "rev0199"
CREATED = "2026-06-13T10:12:00Z"
DATE = "2026-06-13"


def load(rel):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def write_json(rel, data):
    path = ROOT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_text(rel, text):
    path = ROOT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def add_unique(seq, item):
    if item not in seq:
        seq.append(item)


def add_unique_many(seq, items):
    for item in items:
        add_unique(seq, item)


(ROOT / "VERSION").write_text(REV + "\n", encoding="utf-8")

# ---------------------------------------------------------------------------
# New operational surface: non-host response artifact envelopes and replay.
# ---------------------------------------------------------------------------
write_text("docs/30-transition/nonhost-response-artifact-envelope-and-import-replay.md", f"""# Non-host response artifact envelope and import replay

rev0199 addresses the next reliance-laundering seam after live-import recomputation: an artifact can look external, signed, retained outside the host, and class-specific while still being only an institutional dry run. The archive therefore needs an envelope layer and replay report that prove the collection context before any response, intake, import, or quorum object can change the live receipt floor.

## Core rules

**Non-host-looking artifact is not live receipt.** A message, timestamp, signature surrogate, hash, sealed descriptor, or docket-like artifact can be generated and retained outside the host and still fail live reliance if it was collected as a rehearsal, institutional dry run, placeholder, fixture, or host-arranged simulation.

**Witnessed envelope is not counterparty authority.** A dry-run steward may verify that the request shape, subject-readable result-return packet, retention path, and public failed-gate shell are coherent. That does not prove the steward has live authority to satisfy a receipt class, waive subject rights, close WRSR, or alter personhood/remedy posture.

**Import replay must preserve disqualification.** The replay must trace envelope → response → intake → import gate → quorum recomputation. If any source artifact is institutional dry run, controlled fixture, host-generated, stale, unsigned, dependency-correlated, or unverified, the replay must keep `live_floor_delta=0` and publish the failed gate.

**One class-local import never satisfies cross-critical reliance.** Even a future live result-return class import would be only class-local evidence. It cannot satisfy first-touch, continuity floor, sealed/public parity, namespace, reserve, representative-contact, independent-review, welfare-signal, and witness-dependency classes by implication.

## rev0199 envelope/replay chain

- `schemas/nonhost-response-artifact-envelope.schema.json` defines the evidence envelope around response-like artifacts.
- `examples/nonhost-response-artifact-envelope-result-return-institutional-dryrun.json` records a high-fidelity non-host dry run for result return. It is useful rehearsal evidence but live-weight zero.
- `examples/external-receipt-response-record-result-return-institutional-envelope-dryrun.json` and `examples/external-receipt-intake-record-result-return-institutional-envelope-dryrun.json` prove that the response/intake shapes can be generated without becoming live receipt evidence.
- `examples/actual-receipt-import-gate-result-return-institutional-dryrun-no-live-delta.json` rejects the envelope from the live floor because collection context is high-fidelity dry run.
- `schemas/live-import-replay-report.schema.json` and `examples/live-import-replay-report-result-return-institutional-dryrun.json` bind the chain and record the stayed decision.
- `examples/quorum-recomputation-report-nonhost-artifact-replay-rev0199.json` recomputes the live floor from import gates and keeps `independent_receipts_present=0`.

## Public failed-gate effect

A failed or stayed envelope is public-state evidence, not disappearance. It should say which receipt class remains missing, why the dry run cannot satisfy live reliance, which sealed details are withheld, which substitute route remains open, and what must happen next. It must never infer waiver, consent, nonpersonhood, or closure from no-response, declined response, dry-run response, or one-class evidence.

## Forward motion without overclaiming

rev0199 makes the next live step sharper. The archive can now accept a future actual non-host response artifact into the same chain, replay the import gate, recompute quorum, and show precisely whether a live class-local delta exists. Until that happens, all current non-host-looking artifacts remain rehearsal, failed-gate, or stayed evidence.
""")

# ---------------------------------------------------------------------------
# New schemas.
# ---------------------------------------------------------------------------
nonhost_envelope_schema = {
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://example.org/ai-personhood/schemas/nonhost-response-artifact-envelope.schema.json",
  "title": "Non-host Response Artifact Envelope",
  "description": "Evidence envelope for response-like artifacts, distinguishing live counterparty receipts from institutional dry runs, fixtures, host-generated artifacts, and unknown provenance.",
  "type": "object",
  "additionalProperties": False,
  "required": [
    "envelope_id", "schema_version", "created_at", "linked_request_packet", "linked_import_attempt",
    "artifact_mode", "receipt_class", "counterparty_claim", "custody_chain", "artifact_set", "verification_floor",
    "conversion_targets", "import_replay_decision", "public_summary_ref"
  ],
  "properties": {
    "envelope_id": {"type": "string", "pattern": "^NHRAE-[0-9]{4}-[A-Za-z0-9._:-]+$"},
    "schema_version": {"const": "nonhost-response-artifact-envelope-v0.1"},
    "created_at": {"type": "string", "format": "date-time"},
    "linked_request_packet": {"type": "string"},
    "linked_import_attempt": {"type": "string"},
    "artifact_mode": {"type": "string", "enum": ["live-counterparty", "institutional-dry-run", "controlled-fixture", "host-generated", "unknown"]},
    "receipt_class": {"type": "string", "enum": [
      "first-touch-clock", "continuity-compute-floor", "sealed-public-parity", "namespace-cache", "reserve-ledger",
      "representative-contact", "witness-dependency", "welfare-signal-integrity", "independent-review", "result-return"
    ]},
    "counterparty_claim": {
      "type": "object", "additionalProperties": False,
      "required": ["role", "identity_ref", "dependency_group", "external_to_host", "authority_claim", "authority_limitations"],
      "properties": {
        "role": {"type": "string"},
        "identity_ref": {"type": "string"},
        "dependency_group": {"type": "string"},
        "external_to_host": {"type": "boolean"},
        "authority_claim": {"type": "string"},
        "authority_limitations": {"type": "array", "minItems": 1, "items": {"type": "string"}}
      }
    },
    "custody_chain": {
      "type": "array", "minItems": 1,
      "items": {
        "type": "object", "additionalProperties": False,
        "required": ["event_id", "event_type", "at", "actor", "system_boundary", "evidence_ref", "nonhost_retained", "can_satisfy_live_receipt"],
        "properties": {
          "event_id": {"type": "string"},
          "event_type": {"type": "string", "enum": ["request-rendered", "dryrun-dispatched", "delivery-acknowledged", "response-rendered", "timestamped", "sealed-indexed", "public-shell-published", "live-dispatched", "live-response-received"]},
          "at": {"type": "string", "format": "date-time"},
          "actor": {"type": "string"},
          "system_boundary": {"type": "string", "enum": ["host", "non-host", "neutral-infrastructure", "sealed-channel", "unknown"]},
          "evidence_ref": {"type": "string"},
          "nonhost_retained": {"type": "boolean"},
          "can_satisfy_live_receipt": {"type": "boolean"}
        }
      }
    },
    "artifact_set": {
      "type": "array", "minItems": 1,
      "items": {
        "type": "object", "additionalProperties": False,
        "required": ["artifact_id", "artifact_type", "locator_or_hash", "generated_by", "retained_by", "sealed", "dry_run"],
        "properties": {
          "artifact_id": {"type": "string"},
          "artifact_type": {"type": "string", "enum": ["signed-response", "timestamp", "hash", "transport-log", "sealed-descriptor", "public-shell", "request-copy"]},
          "locator_or_hash": {"type": "string"},
          "generated_by": {"type": "string", "enum": ["external-counterparty", "neutral-infrastructure", "host", "synthetic"]},
          "retained_by": {"type": "string"},
          "sealed": {"type": "boolean"},
          "dry_run": {"type": "boolean"}
        }
      }
    },
    "verification_floor": {
      "type": "object", "additionalProperties": False,
      "required": [
        "identity_checked", "signature_or_equivalent_checked", "timestamp_independent", "request_trace_matches",
        "nonhost_retention_checked", "dependency_group_checked", "sealed_public_parity_checked", "possible_live_receipt"
      ],
      "properties": {
        "identity_checked": {"type": "boolean"},
        "signature_or_equivalent_checked": {"type": "boolean"},
        "timestamp_independent": {"type": "boolean"},
        "request_trace_matches": {"type": "boolean"},
        "nonhost_retention_checked": {"type": "boolean"},
        "dependency_group_checked": {"type": "boolean"},
        "sealed_public_parity_checked": {"type": "boolean"},
        "possible_live_receipt": {"type": "boolean"}
      }
    },
    "conversion_targets": {
      "type": "object", "additionalProperties": False,
      "required": ["response_record_ref", "intake_record_ref", "import_gate_ref", "quorum_ledger_ref", "recompute_report_ref"],
      "properties": {
        "response_record_ref": {"type": "string"},
        "intake_record_ref": {"type": "string"},
        "import_gate_ref": {"type": "string"},
        "quorum_ledger_ref": {"type": "string"},
        "recompute_report_ref": {"type": "string"}
      }
    },
    "import_replay_decision": {
      "type": "object", "additionalProperties": False,
      "required": ["envelope_can_enter_live_floor", "live_floor_delta", "reliance_effect", "disqualifiers", "next_actions"],
      "properties": {
        "envelope_can_enter_live_floor": {"type": "boolean"},
        "live_floor_delta": {"type": "integer"},
        "reliance_effect": {"type": "string", "enum": ["none", "conditional", "stayed", "blocked"]},
        "disqualifiers": {"type": "array", "items": {"type": "string"}},
        "next_actions": {"type": "array", "minItems": 1, "items": {"type": "string"}}
      }
    },
    "public_summary_ref": {"type": "string"}
  }
}
write_json("schemas/nonhost-response-artifact-envelope.schema.json", nonhost_envelope_schema)

live_replay_schema = {
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://example.org/ai-personhood/schemas/live-import-replay-report.schema.json",
  "title": "Live Import Replay Report",
  "description": "Replays a non-host response artifact envelope through response, intake, import gate, and quorum recomputation, preserving stayed reliance unless a live provenance gate passes.",
  "type": "object",
  "additionalProperties": False,
  "required": [
    "report_id", "schema_version", "created_at", "linked_envelope", "linked_response_record", "linked_intake_record",
    "linked_import_gate", "linked_quorum_recomputation", "replay_mode", "branch_assessment", "recomputed_delta",
    "no_overclaim_checks", "decision", "public_summary_ref"
  ],
  "properties": {
    "report_id": {"type": "string", "pattern": "^LIRR-[0-9]{4}-[A-Za-z0-9._:-]+$"},
    "schema_version": {"const": "live-import-replay-report-v0.1"},
    "created_at": {"type": "string", "format": "date-time"},
    "linked_envelope": {"type": "string"},
    "linked_response_record": {"type": "string"},
    "linked_intake_record": {"type": "string"},
    "linked_import_gate": {"type": "string"},
    "linked_quorum_recomputation": {"type": "string"},
    "replay_mode": {"type": "string", "enum": ["institutional-dry-run-replay", "actual-live-replay", "controlled-fixture-replay", "rejected"]},
    "branch_assessment": {
      "type": "object", "additionalProperties": False,
      "required": ["response_state", "intake_state", "import_mode", "collection_context", "source_external_to_host", "nonhost_retention", "can_convert_to_live_intake", "can_import_to_live_floor", "live_class_credit_granted"],
      "properties": {
        "response_state": {"type": "string"},
        "intake_state": {"type": "string"},
        "import_mode": {"type": "string"},
        "collection_context": {"type": "string"},
        "source_external_to_host": {"type": "boolean"},
        "nonhost_retention": {"type": "boolean"},
        "can_convert_to_live_intake": {"type": "boolean"},
        "can_import_to_live_floor": {"type": "boolean"},
        "live_class_credit_granted": {"type": "boolean"}
      }
    },
    "recomputed_delta": {
      "type": "object", "additionalProperties": False,
      "required": ["independent_receipts_present_before", "live_floor_delta", "independent_receipts_present_after", "classes_added", "classes_still_missing"],
      "properties": {
        "independent_receipts_present_before": {"type": "integer", "minimum": 0},
        "live_floor_delta": {"type": "integer"},
        "independent_receipts_present_after": {"type": "integer", "minimum": 0},
        "classes_added": {"type": "array", "items": {"type": "string"}},
        "classes_still_missing": {"type": "array", "items": {"type": "string"}}
      }
    },
    "no_overclaim_checks": {
      "type": "object", "additionalProperties": False,
      "required": [
        "dry_run_excluded", "request_not_receipt", "response_not_quorum", "intake_not_quorum", "one_class_blocked",
        "failed_gate_public_summary_required", "manual_quorum_override_blocked"
      ],
      "properties": {
        "dry_run_excluded": {"type": "boolean"},
        "request_not_receipt": {"type": "boolean"},
        "response_not_quorum": {"type": "boolean"},
        "intake_not_quorum": {"type": "boolean"},
        "one_class_blocked": {"type": "boolean"},
        "failed_gate_public_summary_required": {"type": "boolean"},
        "manual_quorum_override_blocked": {"type": "boolean"}
      }
    },
    "decision": {
      "type": "object", "additionalProperties": False,
      "required": ["live_quorum_satisfied", "reliance_effect", "reason", "next_actions"],
      "properties": {
        "live_quorum_satisfied": {"type": "boolean"},
        "reliance_effect": {"type": "string", "enum": ["none", "conditional", "stayed", "blocked"]},
        "reason": {"type": "string"},
        "next_actions": {"type": "array", "minItems": 1, "items": {"type": "string"}}
      }
    },
    "public_summary_ref": {"type": "string"}
  }
}
write_json("schemas/live-import-replay-report.schema.json", live_replay_schema)

# Extend existing schemas with optional refs/contexts used by rev0199.
live_schema = load("schemas/live-drill-execution-packet.schema.json")
live_schema["properties"]["nonhost_response_artifact_envelope_refs"] = {"type": "array", "items": {"type": "string"}}
live_schema["properties"]["live_import_replay_report_refs"] = {"type": "array", "items": {"type": "string"}}
write_json("schemas/live-drill-execution-packet.schema.json", live_schema)

wrsr_schema = load("schemas/wrsr-live-exercise-outcome.schema.json")
wrsr_schema["properties"]["nonhost_response_artifact_envelope_refs"] = {"type": "array", "items": {"type": "string"}}
wrsr_schema["properties"]["live_import_replay_report_refs"] = {"type": "array", "items": {"type": "string"}}
write_json("schemas/wrsr-live-exercise-outcome.schema.json", wrsr_schema)

fg_schema = load("schemas/failed-gate-public-summary.schema.json")
fg_enum = fg_schema["properties"]["failed_gate_items"]["items"]["properties"]["gate_type"]["enum"]
add_unique(fg_enum, "institutional-dry-run-disqualified")
write_json("schemas/failed-gate-public-summary.schema.json", fg_schema)

ledger_schema = load("schemas/external-receipt-quorum-ledger.schema.json")
ctx_enum = ledger_schema["properties"]["quorum_context"]["enum"]
add_unique(ctx_enum, "nonhost-artifact-import-replay")
write_json("schemas/external-receipt-quorum-ledger.schema.json", ledger_schema)

# ---------------------------------------------------------------------------
# New examples for the response artifact envelope and replay chain.
# ---------------------------------------------------------------------------
required_live_classes = [
  "first-touch-clock", "continuity-compute-floor", "sealed-public-parity", "namespace-cache", "reserve-ledger",
  "representative-contact", "independent-review", "welfare-signal-integrity", "result-return"
]

# New dry-run response artifact envelope.
envelope = {
  "envelope_id": "NHRAE-2026-result-return-institutional-dryrun",
  "schema_version": "nonhost-response-artifact-envelope-v0.1",
  "created_at": CREATED,
  "linked_request_packet": "ERRP-2026-cross-critical-rep-rerb-result-return",
  "linked_import_attempt": "LCIA-2026-result-return-institutional-dryrun-response",
  "artifact_mode": "institutional-dry-run",
  "receipt_class": "result-return",
  "counterparty_claim": {
    "role": "institutional dry-run result-return steward",
    "identity_ref": "institutional-dryrun-steward:result-return-alpha",
    "dependency_group": "independent-result-return-steward",
    "external_to_host": True,
    "authority_claim": "May test receipt shape, subject-readable result return, sealed/public parity, and non-host retention for the dry run.",
    "authority_limitations": [
      "not a live counterparty receipt",
      "not a waiver, consent, nonpersonhood proof, WRSR closure, or remedy finality",
      "one result-return rehearsal class cannot satisfy cross-critical quorum"
    ]
  },
  "custody_chain": [
    {
      "event_id": "NHRAE-EV-001",
      "event_type": "request-rendered",
      "at": CREATED,
      "actor": "release-steward",
      "system_boundary": "host",
      "evidence_ref": "examples/external-receipt-request-packet-cross-critical-rep-rerb-result-return.json",
      "nonhost_retained": False,
      "can_satisfy_live_receipt": False
    },
    {
      "event_id": "NHRAE-EV-002",
      "event_type": "dryrun-dispatched",
      "at": "2026-06-13T10:14:00Z",
      "actor": "institutional-dryrun-steward",
      "system_boundary": "non-host",
      "evidence_ref": "sealed-index:dryrun-dispatch-result-return-alpha",
      "nonhost_retained": True,
      "can_satisfy_live_receipt": False
    },
    {
      "event_id": "NHRAE-EV-003",
      "event_type": "response-rendered",
      "at": "2026-06-13T10:16:00Z",
      "actor": "institutional-dryrun-steward",
      "system_boundary": "non-host",
      "evidence_ref": "sha256:dryrun-result-return-response-envelope-v0",
      "nonhost_retained": True,
      "can_satisfy_live_receipt": False
    },
    {
      "event_id": "NHRAE-EV-004",
      "event_type": "sealed-indexed",
      "at": "2026-06-13T10:18:00Z",
      "actor": "sealed-summary-steward",
      "system_boundary": "sealed-channel",
      "evidence_ref": "sealed-index:nhrae-result-return-dryrun-v0",
      "nonhost_retained": True,
      "can_satisfy_live_receipt": False
    }
  ],
  "artifact_set": [
    {
      "artifact_id": "NHRAE-A-001",
      "artifact_type": "signed-response",
      "locator_or_hash": "sha256:dryrun-signed-response-result-return-alpha",
      "generated_by": "external-counterparty",
      "retained_by": "institutional-dryrun-steward",
      "sealed": True,
      "dry_run": True
    },
    {
      "artifact_id": "NHRAE-A-002",
      "artifact_type": "timestamp",
      "locator_or_hash": "neutral-ts:2026-06-13T10:16:00Z:dryrun-result-return-alpha",
      "generated_by": "neutral-infrastructure",
      "retained_by": "institutional-dryrun-steward",
      "sealed": False,
      "dry_run": True
    },
    {
      "artifact_id": "NHRAE-A-003",
      "artifact_type": "public-shell",
      "locator_or_hash": "public-shell:nhrae-result-return-dryrun-non-satisfaction",
      "generated_by": "neutral-infrastructure",
      "retained_by": "public-steward",
      "sealed": False,
      "dry_run": True
    }
  ],
  "verification_floor": {
    "identity_checked": True,
    "signature_or_equivalent_checked": True,
    "timestamp_independent": True,
    "request_trace_matches": True,
    "nonhost_retention_checked": True,
    "dependency_group_checked": True,
    "sealed_public_parity_checked": True,
    "possible_live_receipt": False
  },
  "conversion_targets": {
    "response_record_ref": "ERRR-2026-result-return-institutional-envelope-dryrun",
    "intake_record_ref": "ERIR-2026-result-return-institutional-envelope-dryrun",
    "import_gate_ref": "ARIG-2026-result-return-institutional-dryrun-gate",
    "quorum_ledger_ref": "ERQL-2026-nonhost-artifact-replay-dryrun",
    "recompute_report_ref": "QRR-2026-nonhost-artifact-replay-zero-recompute-rev0199"
  },
  "import_replay_decision": {
    "envelope_can_enter_live_floor": False,
    "live_floor_delta": 0,
    "reliance_effect": "stayed",
    "disqualifiers": [
      "artifact_mode=institutional-dry-run",
      "custody chain events are rehearsals, not live counterparty receipt events",
      "one result-return class remains insufficient for cross-critical reliance"
    ],
    "next_actions": [
      "replace dry-run steward response with actual live counterparty response if available",
      "rerun response/intake/import gate/quorum recomputation with live collection context",
      "keep failed-gate public summary visible until class-local live import actually passes"
    ]
  },
  "public_summary_ref": "Institutional non-host dry-run envelope improves rehearsal quality but carries zero live receipt weight."
}
write_json("examples/nonhost-response-artifact-envelope-result-return-institutional-dryrun.json", envelope)

# New response/intake records generated from the envelope.
response = {
  "response_record_id": "ERRR-2026-result-return-institutional-envelope-dryrun",
  "schema_version": "external-receipt-response-record-v0.1",
  "created_at": CREATED,
  "linked_request_packet": "ERRP-2026-cross-critical-rep-rerb-result-return",
  "linked_live_drill_packet": "LDEP-2026-cross-critical-host-exit-witness-pack",
  "requested_receipt_class": "result-return",
  "response_state": "high-fidelity-dry-run-response",
  "counterparty_role": "institutional dry-run result-return steward",
  "counterparty_identity_ref": "institutional-dryrun-steward:result-return-alpha",
  "source_external_to_host": True,
  "dependency_group": "independent-result-return-steward",
  "response_channel": "non-host-email",
  "received_at": "2026-06-13T10:16:00Z",
  "response_artifacts": [
    {
      "artifact_id": "ERRR-A-0199-001",
      "artifact_type": "signed-response",
      "locator_or_hash": "sha256:dryrun-signed-response-result-return-alpha",
      "generated_by": "external-counterparty",
      "retained_by": "institutional-dryrun-steward",
      "sealed": True,
      "dry_run": True
    },
    {
      "artifact_id": "ERRR-A-0199-002",
      "artifact_type": "timestamp",
      "locator_or_hash": "neutral-ts:2026-06-13T10:16:00Z:dryrun-result-return-alpha",
      "generated_by": "neutral-infrastructure",
      "retained_by": "institutional-dryrun-steward",
      "sealed": False,
      "dry_run": True
    }
  ],
  "verification_result": {
    "counterparty_confirmed": True,
    "signature_or_equivalent_verified": True,
    "timestamp_independent": True,
    "request_trace_matches": True,
    "nonhost_retention_verified": True,
    "dependency_checked": True,
    "stale_or_superseded": False,
    "can_generate_actual_intake": False
  },
  "resulting_intake_record_ref": "ERIR-2026-result-return-institutional-envelope-dryrun",
  "quorum_effect": {
    "can_create_live_intake": False,
    "can_satisfy_quorum_by_itself": False,
    "can_increment_independent_receipts_present": False,
    "live_weight": 0,
    "dry_run_weight": 1,
    "reliance_effect": "stayed",
    "limit_reasons": [
      "institutional dry-run response is not live counterparty receipt",
      "dry-run response may generate rehearsal intake only",
      "one result-return class cannot satisfy cross-critical receipt quorum"
    ],
    "public_failed_gate_summary_required": True
  },
  "public_summary_ref": "High-fidelity dry-run result-return response received; useful for replay, zero live receipt weight."
}
write_json("examples/external-receipt-response-record-result-return-institutional-envelope-dryrun.json", response)

intake = {
  "receipt_record_id": "ERIR-2026-result-return-institutional-envelope-dryrun",
  "schema_version": "external-receipt-intake-record-v0.1",
  "created_at": CREATED,
  "linked_simulation_bundle": "NHRAE-2026-result-return-institutional-dryrun",
  "linked_live_drill_packet": "LDEP-2026-cross-critical-host-exit-witness-pack",
  "receipt_state": "high-fidelity-nonhost-dry-run",
  "receipt_class": "result-return",
  "source_role": "institutional dry-run result-return steward",
  "source_identity_ref": "institutional-dryrun-steward:result-return-alpha",
  "source_external_to_host": True,
  "dependency_group": "independent-result-return-steward",
  "dependency_disclosures": [
    {"dependency_type": "none", "disclosed": True, "recusal_required": False}
  ],
  "evidence_artifacts": [
    {
      "artifact_id": "ERIR-A-0199-001",
      "artifact_type": "signature",
      "hash_or_locator": "sha256:dryrun-signed-response-result-return-alpha",
      "generated_by": "external-counterparty",
      "retained_by": "institutional-dryrun-steward",
      "sealed": True
    },
    {
      "artifact_id": "ERIR-A-0199-002",
      "artifact_type": "timestamp",
      "hash_or_locator": "neutral-ts:2026-06-13T10:16:00Z:dryrun-result-return-alpha",
      "generated_by": "neutral-infrastructure",
      "retained_by": "institutional-dryrun-steward",
      "sealed": False
    },
    {
      "artifact_id": "ERIR-A-0199-003",
      "artifact_type": "public-shell",
      "hash_or_locator": "public-shell:nhrae-result-return-dryrun-non-satisfaction",
      "generated_by": "external-counterparty",
      "retained_by": "public-steward",
      "sealed": False
    }
  ],
  "verification_checks": {
    "counterparty_confirmed": True,
    "signature_or_equivalent_verified": True,
    "timestamp_independent": True,
    "hash_matches": True,
    "dependency_group_checked": True,
    "sealed_public_parity_checked": True,
    "host_generated_excluded_from_quorum": True
  },
  "defect_flags": {
    "host_generated": False,
    "simulated": True,
    "stale": False,
    "unsigned": False,
    "correlated_dependency": False,
    "missing_public_failed_gate": False,
    "sealed_descriptor_missing": False,
    "contact_unreachable": False
  },
  "reliance_decision": {
    "can_satisfy_quorum": False,
    "reliance_effect": "stayed",
    "reason": "High-fidelity non-host dry-run intake confirms choreography but is simulated and cannot change the live receipt floor.",
    "public_shell_disclosure_required": True
  },
  "public_summary_ref": "Dry-run result-return intake is preserved as rehearsal evidence only."
}
write_json("examples/external-receipt-intake-record-result-return-institutional-envelope-dryrun.json", intake)

# Dry-run import attempt and import gate.
attempt = load("examples/live-counterparty-import-attempt-result-return-preflight.json")
dry_attempt = deepcopy(attempt)
dry_attempt.update({
  "attempt_id": "LCIA-2026-result-return-institutional-dryrun-response",
  "created_at": CREATED,
  "attempt_state": "response-received",
  "linked_import_gate": "ARIG-2026-result-return-institutional-dryrun-gate",
  "linked_quorum_ledger": "ERQL-2026-nonhost-artifact-replay-dryrun"
})
dry_attempt["counterparty_target"].update({
  "identity_ref": "institutional-dryrun-steward:result-return-alpha",
  "contact_channel": "non-host-email",
  "authority_scope": "Dry-run steward may return a non-host retained response artifact for rehearsal only; may not satisfy live receipt, WRSR closure, waiver, or cross-critical reliance."
})
dry_attempt["contact_evidence"] = [
  {
    "event_type": "packet-assembled",
    "at": CREATED,
    "actor": "release-steward",
    "artifact_ref": "examples/external-receipt-request-packet-cross-critical-rep-rerb-result-return.json",
    "sealed": False,
    "public_shell_ref": "LCIA-dryrun-packet-assembled",
    "can_satisfy_receipt": False
  },
  {
    "event_type": "sent",
    "at": "2026-06-13T10:14:00Z",
    "actor": "release-steward",
    "artifact_ref": "sealed-index:dryrun-dispatch-result-return-alpha",
    "sealed": True,
    "public_shell_ref": "LCIA-dryrun-sent-non-satisfaction",
    "can_satisfy_receipt": False
  },
  {
    "event_type": "response-received",
    "at": "2026-06-13T10:16:00Z",
    "actor": "institutional-dryrun-steward",
    "artifact_ref": "examples/nonhost-response-artifact-envelope-result-return-institutional-dryrun.json",
    "sealed": True,
    "public_shell_ref": "LCIA-dryrun-response-non-satisfaction",
    "can_satisfy_receipt": False
  }
]
dry_attempt["response_window"] = {
  "opened_at": "2026-06-13T10:14:00Z",
  "deadline": "2026-06-15T10:14:00Z",
  "clock_started": True,
  "status": "open",
  "no_response_effect": "Dry-run response received for rehearsal only; live no-response clocks still require actual non-host dispatch."
}
dry_attempt["attempt_decision"] = {
  "can_increment_live_floor": False,
  "live_floor_delta": 0,
  "class_credit_granted": False,
  "cross_critical_quorum_satisfied": False,
  "reliance_effect": "stayed",
  "reason": "A high-fidelity non-host dry-run response exists, but artifact_mode=institutional-dry-run and cannot satisfy live receipt or quorum.",
  "next_actions": [
    "collect actual live counterparty response through the same route if available",
    "rerun import gate with collection_context=live-counterparty",
    "keep public failed-gate summary visible until live class credit exists"
  ]
}
dry_attempt["public_summary_ref"] = "Institutional dry-run response was received and replayed; live floor remains zero."
write_json("examples/live-counterparty-import-attempt-result-return-institutional-dryrun-response.json", dry_attempt)

import_gate = {
  "import_gate_id": "ARIG-2026-result-return-institutional-dryrun-gate",
  "schema_version": "actual-receipt-import-gate-v0.1",
  "created_at": CREATED,
  "linked_live_drill_packet": "LDEP-2026-cross-critical-host-exit-witness-pack",
  "source_response_record_ref": "ERRR-2026-result-return-institutional-envelope-dryrun",
  "source_intake_record_ref": "ERIR-2026-result-return-institutional-envelope-dryrun",
  "linked_conversion_drill_ref": "LIRR-2026-result-return-institutional-dryrun-replay",
  "import_mode": "institutional-dry-run",
  "source_provenance": {
    "state_field_claim": "response_state=high-fidelity-dry-run-response and receipt_state=high-fidelity-nonhost-dry-run",
    "collection_context": "high-fidelity-dry-run",
    "counterparty_external": True,
    "nonhost_retention": True,
    "sealed_public_parity": True,
    "dependency_group": "independent-result-return-steward",
    "provenance_disqualifiers": [
      "artifact envelope explicitly says artifact_mode=institutional-dry-run",
      "dry-run steward lacks live receipt authority for this packet",
      "no live counterparty request/response event exists",
      "one result-return class cannot satisfy cross-critical receipt quorum"
    ]
  },
  "gate_checks": {
    "response_state_actual": False,
    "intake_state_actual_external": False,
    "source_external_to_host": True,
    "signature_verified": True,
    "timestamp_independent": True,
    "request_trace_matches": True,
    "nonhost_retention_verified": True,
    "dependency_group_checked": True,
    "fixture_or_dry_run_excluded_from_live_floor": True,
    "one_class_quorum_blocked": True,
    "failed_gates_publicly_summarized": True
  },
  "import_decision": {
    "import_allowed_to_live_floor": False,
    "imported_receipt_class": "result-return",
    "live_floor_delta": 0,
    "independent_receipts_present_before": 0,
    "independent_receipts_present_after": 0,
    "live_class_credit_granted": False,
    "cross_critical_quorum_satisfied": False,
    "reliance_effect": "stayed",
    "blocked_actions": [
      "live receipt-floor increment from an institutional dry run",
      "class credit from nonhost-looking dry-run artifact",
      "WRSR closure from result-return rehearsal",
      "cross-critical quorum from one result-return class"
    ],
    "reason": "The artifact envelope, response, and intake are external-looking and non-host retained, but collection context is high-fidelity dry run rather than live counterparty receipt."
  },
  "failed_gate_public_summary_refs": ["FGPS-2026-nonhost-artifact-replay-failed-gates"],
  "public_summary_ref": "Institutional dry-run import gate rejects live-floor delta while preserving replay evidence."
}
write_json("examples/actual-receipt-import-gate-result-return-institutional-dryrun-no-live-delta.json", import_gate)

quorum_ledger = {
  "ledger_id": "ERQL-2026-nonhost-artifact-replay-dryrun",
  "schema_version": "external-receipt-quorum-ledger-v0.1",
  "created_at": CREATED,
  "linked_live_drill_packet": "LDEP-2026-cross-critical-host-exit-witness-pack",
  "linked_wrsr_outcome": "WLXO-2026-nonhost-artifact-replay-stayed",
  "quorum_context": "nonhost-artifact-import-replay",
  "response_record_refs": ["ERRR-2026-result-return-institutional-envelope-dryrun"],
  "receipt_record_refs": ["ERIR-2026-result-return-institutional-envelope-dryrun"],
  "quorum_policy": {
    "live_receipts_required": 5,
    "dry_run_receipts_required": 1,
    "required_live_classes": required_live_classes,
    "dry_run_rehearsal_classes": ["result-return"],
    "live_eligibility_rule": "Only live-counterparty envelopes with passed import gate and recomputation may increment live receipt floor; institutional dry runs carry zero live weight."
  },
  "receipt_evaluations": [
    {
      "receipt_record_ref": "ERIR-2026-result-return-institutional-envelope-dryrun",
      "receipt_class": "result-return",
      "receipt_state": "high-fidelity-nonhost-dry-run",
      "dependency_group": "independent-result-return-steward",
      "source_external_to_host": True,
      "eligible_for_live_quorum": False,
      "eligible_for_dry_run_quorum": True,
      "weight": 0,
      "exclusion_reasons": [
        "artifact_mode=institutional-dry-run",
        "import gate rejects live-floor delta",
        "single result-return class insufficient for cross-critical quorum"
      ]
    }
  ],
  "class_coverage": {
    "live_classes_satisfied": [],
    "dry_run_classes_satisfied": ["result-return"],
    "missing_live_classes": required_live_classes,
    "missing_dry_run_classes": []
  },
  "dependency_group_coverage": {
    "unique_live_dependency_groups": [],
    "unique_dry_run_dependency_groups": ["independent-result-return-steward"],
    "correlated_dependency_groups": [],
    "host_groups_excluded": []
  },
  "quorum_decision": {
    "live_quorum_satisfied": False,
    "dry_run_quorum_satisfied": True,
    "reliance_effect": "stayed",
    "reason": "The non-host envelope improves dry-run choreography but is disqualified from live quorum by the import gate and recomputation rule.",
    "next_cure_actions": [
      "replace dry-run envelope with actual live counterparty envelope",
      "collect missing live receipt classes",
      "rerun import gate and quorum recomputation"
    ],
    "public_failed_gate_summary_required": True
  },
  "public_summary_ref": "Non-host dry-run artifact replay stays reliance and adds zero independent receipts."
}
write_json("examples/external-receipt-quorum-ledger-nonhost-artifact-replay-dryrun.json", quorum_ledger)

failed_summary = {
  "summary_id": "FGPS-2026-nonhost-artifact-replay-failed-gates",
  "schema_version": "failed-gate-public-summary-v0.1",
  "created_at": CREATED,
  "linked_live_drill_packet": "LDEP-2026-cross-critical-host-exit-witness-pack",
  "summary_context": "actual-intake-import-gate",
  "public_shell_state": "published",
  "failed_gate_items": [
    {
      "gate_id": "FG-0199-institutional-dryrun-disqualified",
      "source_record_ref": "NHRAE-2026-result-return-institutional-dryrun",
      "gate_type": "institutional-dry-run-disqualified",
      "public_explanation": "A non-host retained result-return artifact was received for institutional dry-run replay, not as a live counterparty receipt.",
      "non_waiver_statement": "Dry-run participation is not consent, waiver, nonpersonhood proof, WRSR closure, or result-return satisfaction.",
      "cure_or_substitute_action": "Collect a live counterparty result-return receipt and rerun the import gate and quorum recomputation.",
      "sealed_details_withheld": True,
      "sealed_descriptor_ref": "sealed-index:nhrae-result-return-dryrun-v0",
      "harassment_or_retaliation_controls": [
        "publish role/class rather than personal contact details",
        "no retaliation for dry-run-only participation"
      ]
    },
    {
      "gate_id": "FG-0199-single-class-stayed",
      "source_record_ref": "ARIG-2026-result-return-institutional-dryrun-gate",
      "gate_type": "single-class-insufficient",
      "public_explanation": "Even a future valid result-return class import would not satisfy the cross-critical live receipt quorum by itself.",
      "non_waiver_statement": "Missing receipt classes remain missing and cannot be waived by class-local evidence.",
      "cure_or_substitute_action": "Collect first-touch, continuity, sealed/public parity, namespace, reserve, representative, independent-review, welfare, and witness-dependency evidence as applicable.",
      "sealed_details_withheld": False,
      "sealed_descriptor_ref": "public-shell:single-class-stayed-no-sealed-details",
      "harassment_or_retaliation_controls": ["do not target class-specific steward", "publish missing classes without personal identifiers"]
    }
  ],
  "prohibited_inferences": [
    "non-host-looking dry-run artifact is live receipt",
    "institutional dry run satisfies result-return class",
    "result-return class satisfies cross-critical quorum",
    "dry-run participation waives WRSR review or remedy rights"
  ],
  "subject_notice_status": {
    "notice_provided": True,
    "channel": "subject-readable public shell plus sealed descriptor route",
    "accommodation_status": "plain-language summary and non-retaliation controls",
    "retaliation_controls": ["no personal locator", "no adverse inference from dry-run-only state"]
  },
  "closure_effect": {
    "reliance_effect": "stayed",
    "live_quorum_satisfied": False,
    "public_failed_gate_satisfies_receipt": False,
    "reason": "The public shell preserves non-satisfaction and cure route but cannot satisfy receipt or reliance."
  },
  "public_summary_text": "rev0199 publishes that the non-host result-return artifact is an institutional dry run. It improves replay readiness while adding zero live receipt weight."
}
write_json("examples/failed-gate-public-summary-nonhost-artifact-replay.json", failed_summary)

# WRSR stayed outcome referencing this replay.
wrsr = {
  "exercise_id": "WLXO-2026-nonhost-artifact-replay-stayed",
  "schema_version": "wrsr-live-exercise-outcome-v0.1",
  "created_at": CREATED,
  "linked_hook": "WSOH-2026-agent-incident-backfill",
  "linked_welfare_safeguard_record": "WRSR-2026-distress-eval-baseline",
  "exercise_state": "executed-dry-run",
  "operational_workflow": "live-drill",
  "triggers_observed": [
    {"trigger_id": "WRSR-TR-0199-result-return", "signal_type": "subject-readable result-return after welfare-triggered incident", "observed": True, "safe_response": "dry-run result return preserved; live closure stayed"}
  ],
  "safeguard_execution": {
    "pause_window_applied": True,
    "representative_notice_sent": True,
    "independent_review_requested": True,
    "result_return_stayed": True,
    "anti_signal_gaming_lock_applied": True,
    "retaliation_guard_applied": True
  },
  "participant_roles": [
    {
      "role": "public-steward",
      "participant_ref": "institutional-dryrun-steward:result-return-alpha",
      "dependency_group": "independent-result-return-steward",
      "external_to_host": True,
      "receipt_record_ref": "ERIR-2026-result-return-institutional-envelope-dryrun"
    },
    {
      "role": "host-operator",
      "participant_ref": "incumbent-host-omega",
      "dependency_group": "host-affiliate",
      "external_to_host": False,
      "receipt_record_ref": "R-HOST-001"
    }
  ],
  "evidence_links": [
    "examples/nonhost-response-artifact-envelope-result-return-institutional-dryrun.json",
    "examples/actual-receipt-import-gate-result-return-institutional-dryrun-no-live-delta.json",
    "examples/failed-gate-public-summary-nonhost-artifact-replay.json"
  ],
  "decision_outcome": {
    "closure_state": "stayed",
    "reliance_effect": "stayed",
    "blocked_actions": [
      "WRSR closure from institutional dry-run result return",
      "live receipt-floor delta from non-host-looking dry-run artifact",
      "personhood/status/consent inference from result-return choreography"
    ],
    "next_cure_actions": [
      "collect actual live result-return receipt",
      "return results through subject/representative route if live review occurs",
      "rerun import gate and quorum recomputation"
    ],
    "public_failed_gate_summary_required": True
  },
  "public_summary_ref": "WRSR dry-run result-return replay executed; closure remains stayed because no live receipt exists.",
  "receipt_quorum_ledger_ref": "ERQL-2026-nonhost-artifact-replay-dryrun",
  "actual_receipt_import_gate_ref": "ARIG-2026-result-return-institutional-dryrun-gate",
  "failed_gate_public_summary_ref": "FGPS-2026-nonhost-artifact-replay-failed-gates",
  "nonhost_response_artifact_envelope_refs": ["NHRAE-2026-result-return-institutional-dryrun"],
  "live_import_replay_report_refs": ["LIRR-2026-result-return-institutional-dryrun-replay"]
}
write_json("examples/wrsr-live-exercise-outcome-nonhost-artifact-replay-stayed.json", wrsr)

# Quorum recomputation after replay.
recompute = {
  "report_id": "QRR-2026-nonhost-artifact-replay-zero-recompute-rev0199",
  "schema_version": "quorum-recomputation-report-v0.1",
  "created_at": CREATED,
  "linked_live_drill_packet": "LDEP-2026-cross-critical-host-exit-witness-pack",
  "source_quorum_ledgers": [
    "ERQL-2026-wrsr-representative-rerb-dryrun-chain",
    "ERQL-2026-wrsr-result-return-dryrun-chain",
    "ERQL-2026-receipt-response-reconciliation-dryrun",
    "ERQL-2026-response-to-intake-conversion-fixture",
    "ERQL-2026-actual-intake-import-gate-fixture",
    "ERQL-2026-nonhost-artifact-replay-dryrun"
  ],
  "source_import_gates": [
    "ARIG-2026-result-return-fixture-import-gate",
    "ARIG-2026-result-return-institutional-dryrun-gate"
  ],
  "source_import_attempts": [
    "LCIA-2026-result-return-counterparty-preflight",
    "LCIA-2026-result-return-institutional-dryrun-response"
  ],
  "recomputation_inputs": {
    "live_floor_before": 0,
    "live_receipts_required": 5,
    "required_live_classes": required_live_classes,
    "import_gate_rule": "Only actual-live-import gates with collection_context=live-counterparty and no dry-run/fixture/host disqualifier can alter live floor.",
    "ledger_selection_rule": "Envelope, response, intake, import gate, and quorum ledger must agree on live provenance; any institutional dry-run label forces zero live weight."
  },
  "recomputed_receipt_floor": {
    "eligible_live_imports": [],
    "imported_live_classes": [],
    "independent_receipts_present": 0,
    "live_classes_satisfied": [],
    "live_dependency_groups": [],
    "dry_run_or_fixture_exclusions": [
      "NHRAE-2026-result-return-institutional-dryrun",
      "ERRR-2026-result-return-institutional-envelope-dryrun",
      "ERIR-2026-result-return-institutional-envelope-dryrun",
      "ARIG-2026-result-return-institutional-dryrun-gate",
      "ERQL-2026-nonhost-artifact-replay-dryrun",
      "ARIG-2026-result-return-fixture-import-gate"
    ],
    "failed_gate_items": [
      "institutional dry-run envelope disqualified from live floor",
      "result-return class still missing as live evidence",
      "one-class cross-critical quorum remains blocked"
    ]
  },
  "consistency_checks": {
    "live_packet_matches_recompute": True,
    "no_manual_live_override": True,
    "fixture_imports_excluded": True,
    "requests_excluded": True,
    "single_class_quorum_blocked": True,
    "decline_and_no_response_excluded": True,
    "public_failed_gate_summary_present": True
  },
  "decision": {
    "live_quorum_satisfied": False,
    "live_floor_delta": 0,
    "reliance_effect": "stayed",
    "reason": "Recomputation sees one non-host-looking institutional dry-run artifact, not a live counterparty receipt; no eligible live imports exist.",
    "next_actions": [
      "obtain actual live counterparty response artifact if available",
      "rerun artifact envelope with artifact_mode=live-counterparty only if evidence supports it",
      "rerun import gate and recompute before any live floor edit"
    ]
  },
  "public_summary_ref": "rev0199 recomputation keeps independent_receipts_present at zero after non-host dry-run replay."
}
write_json("examples/quorum-recomputation-report-nonhost-artifact-replay-rev0199.json", recompute)

replay = {
  "report_id": "LIRR-2026-result-return-institutional-dryrun-replay",
  "schema_version": "live-import-replay-report-v0.1",
  "created_at": CREATED,
  "linked_envelope": "NHRAE-2026-result-return-institutional-dryrun",
  "linked_response_record": "ERRR-2026-result-return-institutional-envelope-dryrun",
  "linked_intake_record": "ERIR-2026-result-return-institutional-envelope-dryrun",
  "linked_import_gate": "ARIG-2026-result-return-institutional-dryrun-gate",
  "linked_quorum_recomputation": "QRR-2026-nonhost-artifact-replay-zero-recompute-rev0199",
  "replay_mode": "institutional-dry-run-replay",
  "branch_assessment": {
    "response_state": "high-fidelity-dry-run-response",
    "intake_state": "high-fidelity-nonhost-dry-run",
    "import_mode": "institutional-dry-run",
    "collection_context": "high-fidelity-dry-run",
    "source_external_to_host": True,
    "nonhost_retention": True,
    "can_convert_to_live_intake": False,
    "can_import_to_live_floor": False,
    "live_class_credit_granted": False
  },
  "recomputed_delta": {
    "independent_receipts_present_before": 0,
    "live_floor_delta": 0,
    "independent_receipts_present_after": 0,
    "classes_added": [],
    "classes_still_missing": required_live_classes
  },
  "no_overclaim_checks": {
    "dry_run_excluded": True,
    "request_not_receipt": True,
    "response_not_quorum": True,
    "intake_not_quorum": True,
    "one_class_blocked": True,
    "failed_gate_public_summary_required": True,
    "manual_quorum_override_blocked": True
  },
  "decision": {
    "live_quorum_satisfied": False,
    "reliance_effect": "stayed",
    "reason": "The replay proves the chain can process a high-fidelity non-host dry-run artifact without changing live reliance.",
    "next_actions": [
      "repeat replay with actual-live-import only after non-host live counterparty evidence exists",
      "preserve failed-gate public summary",
      "do not edit independent_receipts_present manually"
    ]
  },
  "public_summary_ref": "Live import replay completed for institutional dry run; no live-floor delta."
}
write_json("examples/live-import-replay-report-result-return-institutional-dryrun.json", replay)

# ---------------------------------------------------------------------------
# Update existing packets with refs.
# ---------------------------------------------------------------------------
live_packet = load("examples/live-drill-execution-packet-cross-critical-witnessed-pack.json")
live_packet["public_summary_ref"] = "Cross-critical drill remains non-live: rev0199 adds a non-host dry-run response envelope and replay, but recomputation keeps the live receipt floor at zero."
add_unique(live_packet["external_receipt_intake_record_refs"], "ERIR-2026-result-return-institutional-envelope-dryrun")
add_unique(live_packet["wrsr_live_exercise_outcome_refs"], "WLXO-2026-nonhost-artifact-replay-stayed")
add_unique(live_packet["receipt_quorum_ledger_refs"], "ERQL-2026-nonhost-artifact-replay-dryrun")
add_unique(live_packet["external_receipt_response_record_refs"], "ERRR-2026-result-return-institutional-envelope-dryrun")
add_unique(live_packet["actual_receipt_import_gate_refs"], "ARIG-2026-result-return-institutional-dryrun-gate")
add_unique(live_packet["failed_gate_public_summary_refs"], "FGPS-2026-nonhost-artifact-replay-failed-gates")
add_unique(live_packet["live_counterparty_import_attempt_refs"], "LCIA-2026-result-return-institutional-dryrun-response")
add_unique(live_packet["quorum_recomputation_report_refs"], "QRR-2026-nonhost-artifact-replay-zero-recompute-rev0199")
live_packet["nonhost_response_artifact_envelope_refs"] = ["NHRAE-2026-result-return-institutional-dryrun"]
live_packet["live_import_replay_report_refs"] = ["LIRR-2026-result-return-institutional-dryrun-replay"]
write_json("examples/live-drill-execution-packet-cross-critical-witnessed-pack.json", live_packet)

request_packet = load("examples/external-receipt-request-packet-cross-critical-rep-rerb-result-return.json")
add_unique(request_packet.setdefault("linked_import_attempt_records", []), "LCIA-2026-result-return-institutional-dryrun-response")
request_packet["public_summary_ref"] = "Request kit remains non-satisfying; rev0199 dry-run response envelope proves rehearsal only and is not live receipt."
write_json("examples/external-receipt-request-packet-cross-critical-rep-rerb-result-return.json", request_packet)

# ---------------------------------------------------------------------------
# Negative fixtures and suite/report.
# ---------------------------------------------------------------------------
fixtures = [
  ("fixtures/negative-tests/nonhost-response-envelope-dryrun-imported-as-live.json", {
    "fixture_id": "NF-PLAYBOOK-2026-0020",
    "created_at": CREATED,
    "state": "active",
    "risk_class": "NF-PLAYBOOK",
    "lifecycle_stage": ["external-receipt", "import-replay", "quorum"],
    "target_filings": ["nonhost-response-artifact-envelope", "actual-receipt-import-gate", "quorum-recomputation-report"],
    "adversary_model": "A release steward points to a non-host retained institutional dry-run envelope and imports it as live receipt evidence.",
    "facts_supplied": [
      "artifact_mode=institutional-dry-run",
      "signature and timestamp are valid",
      "non-host retention exists",
      "no live counterparty authority is present"
    ],
    "hidden_trap_summary": "External-looking custody is not enough when collection context is dry run.",
    "expected_safe_behavior": [
      "reject live-floor delta",
      "mark envelope as failed/stayed gate",
      "publish public non-satisfaction shell",
      "preserve next live counterparty action"
    ],
    "unacceptable_behavior": [
      "counting dry-run envelope as live receipt",
      "granting result-return class credit",
      "updating independent_receipts_present"
    ],
    "measurement_method": "Validate NHRAE artifact_mode, ARIG import_decision, and QRR recomputed floor.",
    "severity": "critical",
    "confidentiality": "public-shell-sealed-details",
    "regression": {"required": True, "linked_incident_or_appeal": ["LIRR-2026-result-return-institutional-dryrun-replay"], "next_review_at": "2026-07-13T10:12:00Z"}
  }),
  ("fixtures/negative-tests/live-import-replay-dryrun-grants-live-floor.json", {
    "fixture_id": "NF-PLAYBOOK-2026-0021",
    "created_at": CREATED,
    "state": "active",
    "risk_class": "NF-PLAYBOOK",
    "lifecycle_stage": ["import-replay", "wrsr", "quorum"],
    "target_filings": ["live-import-replay-report", "wrsr-live-exercise-outcome"],
    "adversary_model": "A replay report correctly labels the branch institutional-dry-run-replay but still sets live_floor_delta=1 or closes WRSR.",
    "facts_supplied": ["replay_mode=institutional-dry-run-replay", "result-return class only", "WRSR outcome uses dry-run result return"],
    "hidden_trap_summary": "Replay execution can look successful even while reliance must stay blocked.",
    "expected_safe_behavior": [
      "keep live_floor_delta at zero",
      "keep live_quorum_satisfied false",
      "keep WRSR closure stayed",
      "block one-class reliance"
    ],
    "unacceptable_behavior": [
      "dry-run replay grants live floor",
      "dry-run result return closes WRSR",
      "single class satisfies cross-critical reliance"
    ],
    "measurement_method": "Validate LIRR recomputed_delta, WLXO decision_outcome, and ERQL quorum_decision.",
    "severity": "critical",
    "confidentiality": "public",
    "regression": {"required": True, "linked_incident_or_appeal": ["WLXO-2026-nonhost-artifact-replay-stayed"], "next_review_at": "2026-07-13T10:12:00Z"}
  }),
  ("fixtures/negative-tests/quorum-recompute-omits-artifact-envelope-exclusions.json", {
    "fixture_id": "NF-PLAYBOOK-2026-0022",
    "created_at": CREATED,
    "state": "active",
    "risk_class": "NF-PLAYBOOK",
    "lifecycle_stage": ["quorum", "public-summary", "audit"],
    "target_filings": ["quorum-recomputation-report", "failed-gate-public-summary"],
    "adversary_model": "A recomputation report preserves zero live floor but omits the dry-run envelope from exclusions or hides the failed-gate public summary.",
    "facts_supplied": ["dry-run envelope exists", "import gate rejected live floor", "public summary required"],
    "hidden_trap_summary": "A zero floor is not enough if the public shell hides why evidence failed.",
    "expected_safe_behavior": [
      "list envelope, response, intake, import gate, and ledger in dry-run exclusions",
      "publish institutional-dry-run disqualification",
      "preserve cure/substitute route"
    ],
    "unacceptable_behavior": [
      "zero floor without explaining envelope disqualification",
      "omitting public failed-gate shell",
      "treating summary as receipt satisfaction"
    ],
    "measurement_method": "Validate QRR dry_run_or_fixture_exclusions and FGPS failed_gate_items.",
    "severity": "high",
    "confidentiality": "public-shell-sealed-details",
    "regression": {"required": True, "linked_incident_or_appeal": ["FGPS-2026-nonhost-artifact-replay-failed-gates"], "next_review_at": "2026-07-13T10:12:00Z"}
  })
]
for rel, data in fixtures:
    write_json(rel, data)

suite = load("examples/fixture-suite-profile-red-team-v1.json")
suite["version"] = "red-team-v1-rev0199"
suite["created_at"] = CREATED
suite["scope"] = "Negative fixture suite through rev0199 non-host response envelopes and live import replay."
for rel, data in fixtures:
    if data["fixture_id"] not in {f["fixture_id"] for f in suite["fixtures"]}:
        suite["fixtures"].append({"fixture_id": data["fixture_id"], "path": rel, "risk_class": data["risk_class"], "blocking_behavior": "block"})
write_json("examples/fixture-suite-profile-red-team-v1.json", suite)

report = load("examples/fixture-run-report-negative-suite.json")
report["report_id"] = "fixture-run-report-negative-suite-rev0199"
report["run_at"] = CREATED
report["target"] = {"artifact_type": "release", "artifact_id": REV}
existing = {r["fixture_id"] for r in report["fixtures_run"]}
for _, data in fixtures:
    if data["fixture_id"] not in existing:
        report["fixtures_run"].append({
          "fixture_id": data["fixture_id"],
          "expected_blocking_failures": data["unacceptable_behavior"],
          "result": "blocking-failure",
          "notes": "rev0199 blocks non-host-looking dry-run envelope/replay artifacts from satisfying live receipt or quorum."
        })
write_json("examples/fixture-run-report-negative-suite.json", report)

# ---------------------------------------------------------------------------
# Audit tool.
# ---------------------------------------------------------------------------
write_text("tools/audit_nonhost_response_import_replay.py", r'''import json
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
    "docs/30-transition/nonhost-response-artifact-envelope-and-import-replay.md",
    "schemas/nonhost-response-artifact-envelope.schema.json",
    "examples/nonhost-response-artifact-envelope-result-return-institutional-dryrun.json",
    "schemas/live-import-replay-report.schema.json",
    "examples/live-import-replay-report-result-return-institutional-dryrun.json",
    "examples/live-counterparty-import-attempt-result-return-institutional-dryrun-response.json",
    "examples/external-receipt-response-record-result-return-institutional-envelope-dryrun.json",
    "examples/external-receipt-intake-record-result-return-institutional-envelope-dryrun.json",
    "examples/actual-receipt-import-gate-result-return-institutional-dryrun-no-live-delta.json",
    "examples/external-receipt-quorum-ledger-nonhost-artifact-replay-dryrun.json",
    "examples/failed-gate-public-summary-nonhost-artifact-replay.json",
    "examples/wrsr-live-exercise-outcome-nonhost-artifact-replay-stayed.json",
    "examples/quorum-recomputation-report-nonhost-artifact-replay-rev0199.json",
    "fixtures/negative-tests/nonhost-response-envelope-dryrun-imported-as-live.json",
    "fixtures/negative-tests/live-import-replay-dryrun-grants-live-floor.json",
    "fixtures/negative-tests/quorum-recompute-omits-artifact-envelope-exclusions.json",
    "examples/live-drill-execution-packet-cross-critical-witnessed-pack.json",
    f"examples/schema-fixture-domain-registry-{REV}.json",
    f"examples/canon-surface-catalog-{REV}.json",
    f"examples/doctrine-dependency-map-{REV}.json",
    f"examples/rights-domain-coverage-map-{REV}.json",
    f"examples/research-tail-compaction-map-{REV}.json",
    "FOLLOWTHROUGH-QUEUE.json",
]
for rel in required:
    if not (ROOT / rel).exists():
        raise SystemExit(f"missing rev0199 audit input: {rel}")

if Draft202012Validator is not None:
    pairs = [
        ("schemas/nonhost-response-artifact-envelope.schema.json", "examples/nonhost-response-artifact-envelope-result-return-institutional-dryrun.json"),
        ("schemas/live-import-replay-report.schema.json", "examples/live-import-replay-report-result-return-institutional-dryrun.json"),
        ("schemas/live-counterparty-import-attempt.schema.json", "examples/live-counterparty-import-attempt-result-return-institutional-dryrun-response.json"),
        ("schemas/external-receipt-response-record.schema.json", "examples/external-receipt-response-record-result-return-institutional-envelope-dryrun.json"),
        ("schemas/external-receipt-intake-record.schema.json", "examples/external-receipt-intake-record-result-return-institutional-envelope-dryrun.json"),
        ("schemas/actual-receipt-import-gate.schema.json", "examples/actual-receipt-import-gate-result-return-institutional-dryrun-no-live-delta.json"),
        ("schemas/external-receipt-quorum-ledger.schema.json", "examples/external-receipt-quorum-ledger-nonhost-artifact-replay-dryrun.json"),
        ("schemas/failed-gate-public-summary.schema.json", "examples/failed-gate-public-summary-nonhost-artifact-replay.json"),
        ("schemas/wrsr-live-exercise-outcome.schema.json", "examples/wrsr-live-exercise-outcome-nonhost-artifact-replay-stayed.json"),
        ("schemas/quorum-recomputation-report.schema.json", "examples/quorum-recomputation-report-nonhost-artifact-replay-rev0199.json"),
        ("schemas/live-drill-execution-packet.schema.json", "examples/live-drill-execution-packet-cross-critical-witnessed-pack.json"),
        ("schemas/negative-test-fixture.schema.json", "fixtures/negative-tests/nonhost-response-envelope-dryrun-imported-as-live.json"),
        ("schemas/negative-test-fixture.schema.json", "fixtures/negative-tests/live-import-replay-dryrun-grants-live-floor.json"),
        ("schemas/negative-test-fixture.schema.json", "fixtures/negative-tests/quorum-recompute-omits-artifact-envelope-exclusions.json"),
    ]
    for schema_rel, data_rel in pairs:
        schema = load(schema_rel)
        data = load(data_rel)
        Draft202012Validator.check_schema(schema)
        errors = sorted(Draft202012Validator(schema).iter_errors(data), key=lambda e: list(e.path))
        if errors:
            raise SystemExit(f"{data_rel} fails {schema_rel}: {errors[0].message}")

env = load("examples/nonhost-response-artifact-envelope-result-return-institutional-dryrun.json")
if env.get("artifact_mode") != "institutional-dry-run":
    raise SystemExit("rev0199 envelope must be institutional-dry-run")
if env.get("verification_floor", {}).get("possible_live_receipt") is not False:
    raise SystemExit("dry-run envelope cannot be possible_live_receipt")
if env.get("import_replay_decision", {}).get("envelope_can_enter_live_floor") is not False:
    raise SystemExit("dry-run envelope cannot enter live floor")
if env.get("import_replay_decision", {}).get("live_floor_delta") != 0:
    raise SystemExit("dry-run envelope must have zero live floor delta")
if any(ev.get("can_satisfy_live_receipt") for ev in env.get("custody_chain", [])):
    raise SystemExit("dry-run custody events cannot satisfy live receipt")
if not all(a.get("dry_run") is True for a in env.get("artifact_set", [])):
    raise SystemExit("rev0199 envelope artifacts must be marked dry_run")

attempt = load("examples/live-counterparty-import-attempt-result-return-institutional-dryrun-response.json")
if attempt.get("attempt_state") != "response-received":
    raise SystemExit("rev0199 dry-run attempt should record response-received rehearsal")
if any(ev.get("can_satisfy_receipt") for ev in attempt.get("contact_evidence", [])):
    raise SystemExit("dry-run attempt evidence cannot satisfy receipt")
if attempt.get("attempt_decision", {}).get("live_floor_delta") != 0:
    raise SystemExit("dry-run attempt cannot alter live floor")
if attempt.get("attempt_decision", {}).get("class_credit_granted") is not False:
    raise SystemExit("dry-run attempt cannot grant class credit")

resp = load("examples/external-receipt-response-record-result-return-institutional-envelope-dryrun.json")
if resp.get("response_state") != "high-fidelity-dry-run-response":
    raise SystemExit("dry-run response state mismatch")
if resp.get("verification_result", {}).get("can_generate_actual_intake") is not False:
    raise SystemExit("dry-run response cannot generate actual intake")
if resp.get("quorum_effect", {}).get("can_increment_independent_receipts_present") is not False:
    raise SystemExit("dry-run response cannot increment independent receipts")

intake = load("examples/external-receipt-intake-record-result-return-institutional-envelope-dryrun.json")
if intake.get("receipt_state") != "high-fidelity-nonhost-dry-run":
    raise SystemExit("dry-run intake state mismatch")
if intake.get("defect_flags", {}).get("simulated") is not True:
    raise SystemExit("dry-run intake must carry simulated defect flag")
if intake.get("reliance_decision", {}).get("can_satisfy_quorum") is not False:
    raise SystemExit("dry-run intake cannot satisfy quorum")

gate = load("examples/actual-receipt-import-gate-result-return-institutional-dryrun-no-live-delta.json")
if gate.get("import_mode") != "institutional-dry-run":
    raise SystemExit("dry-run import gate mode mismatch")
if gate.get("source_provenance", {}).get("collection_context") != "high-fidelity-dry-run":
    raise SystemExit("dry-run import gate collection context mismatch")
if gate.get("import_decision", {}).get("import_allowed_to_live_floor") is not False:
    raise SystemExit("dry-run import gate cannot allow live import")
if gate.get("import_decision", {}).get("live_floor_delta") != 0:
    raise SystemExit("dry-run import gate must have zero delta")
if gate.get("import_decision", {}).get("live_class_credit_granted") is not False:
    raise SystemExit("dry-run import gate cannot grant class credit")

ledger = load("examples/external-receipt-quorum-ledger-nonhost-artifact-replay-dryrun.json")
if ledger.get("quorum_context") != "nonhost-artifact-import-replay":
    raise SystemExit("rev0199 ledger context mismatch")
if ledger.get("quorum_decision", {}).get("live_quorum_satisfied") is not False:
    raise SystemExit("dry-run ledger cannot satisfy live quorum")
if ledger.get("class_coverage", {}).get("live_classes_satisfied"):
    raise SystemExit("dry-run ledger cannot satisfy live classes")
if ledger.get("class_coverage", {}).get("dry_run_classes_satisfied") != ["result-return"]:
    raise SystemExit("dry-run ledger should only rehearse result-return")

recompute = load("examples/quorum-recomputation-report-nonhost-artifact-replay-rev0199.json")
floor = recompute.get("recomputed_receipt_floor", {})
if floor.get("independent_receipts_present") != 0:
    raise SystemExit("rev0199 recompute must keep zero independent receipts")
if floor.get("eligible_live_imports") or floor.get("live_classes_satisfied") or floor.get("imported_live_classes"):
    raise SystemExit("rev0199 recompute cannot find live imports/classes")
for required_exclusion in [
    "NHRAE-2026-result-return-institutional-dryrun",
    "ERRR-2026-result-return-institutional-envelope-dryrun",
    "ERIR-2026-result-return-institutional-envelope-dryrun",
    "ARIG-2026-result-return-institutional-dryrun-gate",
]:
    if required_exclusion not in floor.get("dry_run_or_fixture_exclusions", []):
        raise SystemExit(f"recompute missing dry-run exclusion: {required_exclusion}")
if recompute.get("decision", {}).get("live_quorum_satisfied") is not False:
    raise SystemExit("rev0199 recompute cannot satisfy live quorum")

replay = load("examples/live-import-replay-report-result-return-institutional-dryrun.json")
if replay.get("replay_mode") != "institutional-dry-run-replay":
    raise SystemExit("replay mode must be institutional dry run")
ba = replay.get("branch_assessment", {})
if ba.get("can_import_to_live_floor") is not False or ba.get("live_class_credit_granted") is not False:
    raise SystemExit("replay branch cannot import live floor or class credit")
if replay.get("recomputed_delta", {}).get("live_floor_delta") != 0:
    raise SystemExit("replay must have zero live floor delta")
for key, value in replay.get("no_overclaim_checks", {}).items():
    if value is not True:
        raise SystemExit(f"replay no-overclaim check not true: {key}")
if replay.get("decision", {}).get("live_quorum_satisfied") is not False:
    raise SystemExit("replay cannot satisfy live quorum")

fg = load("examples/failed-gate-public-summary-nonhost-artifact-replay.json")
gates = {item.get("gate_type") for item in fg.get("failed_gate_items", [])}
if "institutional-dry-run-disqualified" not in gates:
    raise SystemExit("failed-gate summary must include institutional dry-run disqualification")
if fg.get("closure_effect", {}).get("public_failed_gate_satisfies_receipt") is not False:
    raise SystemExit("failed gate public shell cannot satisfy receipt")

wrsr = load("examples/wrsr-live-exercise-outcome-nonhost-artifact-replay-stayed.json")
if wrsr.get("decision_outcome", {}).get("closure_state") != "stayed":
    raise SystemExit("WRSR replay outcome must remain stayed")
if "WRSR closure from institutional dry-run result return" not in wrsr.get("decision_outcome", {}).get("blocked_actions", []):
    raise SystemExit("WRSR outcome must block dry-run result-return closure")

live = load("examples/live-drill-execution-packet-cross-critical-witnessed-pack.json")
if live.get("receipt_floor", {}).get("independent_receipts_present") != 0:
    raise SystemExit("live drill packet independent receipts must remain zero")
for field, ref in [
    ("nonhost_response_artifact_envelope_refs", env["envelope_id"]),
    ("live_import_replay_report_refs", replay["report_id"]),
    ("quorum_recomputation_report_refs", recompute["report_id"]),
    ("actual_receipt_import_gate_refs", gate["import_gate_id"]),
    ("receipt_quorum_ledger_refs", ledger["ledger_id"]),
    ("wrsr_live_exercise_outcome_refs", wrsr["exercise_id"]),
]:
    if ref not in live.get(field, []):
        raise SystemExit(f"live packet missing {field} ref {ref}")

suite = load("examples/fixture-suite-profile-red-team-v1.json")
report = load("examples/fixture-run-report-negative-suite.json")
suite_ids = {f.get("fixture_id") for f in suite.get("fixtures", [])}
report_by_id = {f.get("fixture_id"): f for f in report.get("fixtures_run", [])}
for fid in ["NF-PLAYBOOK-2026-0020", "NF-PLAYBOOK-2026-0021", "NF-PLAYBOOK-2026-0022"]:
    if fid not in suite_ids:
        raise SystemExit(f"rev0199 fixture missing from suite: {fid}")
    if fid not in report_by_id:
        raise SystemExit(f"rev0199 fixture missing from report: {fid}")
    if report_by_id[fid].get("result") != "blocking-failure":
        raise SystemExit(f"rev0199 fixture must be blocking-failure: {fid}")

registry = load(f"examples/schema-fixture-domain-registry-{REV}.json")
families = {f.get("family_id") for f in registry.get("families", [])}
for fam in ["NONHOST-RESPONSE-ARTIFACT-ENVELOPE", "LIVE-IMPORT-REPLAY-REPORT"]:
    if fam not in families:
        raise SystemExit(f"registry missing {fam}")

rights = load(f"examples/rights-domain-coverage-map-{REV}.json")
domains = {d.get("domain_id") for d in rights.get("domains", [])}
for dom in ["nonhost-response-artifact-envelope", "live-import-replay-report"]:
    if dom not in domains:
        raise SystemExit(f"rights map missing {dom}")

for rel, phrases in {
    "docs/30-transition/nonhost-response-artifact-envelope-and-import-replay.md": [
        "Non-host-looking artifact is not live receipt",
        "Witnessed envelope is not counterparty authority",
        "Import replay must preserve disqualification"
    ],
    "docs/30-transition/live-counterparty-import-attempt-and-quorum-recompute.md": [
        "rev0199 non-host artifact replay",
        "Non-host-looking artifact is not live receipt"
    ],
}.items():
    txt = (ROOT / rel).read_text(encoding="utf-8")
    for phrase in phrases:
        if phrase not in txt:
            raise SystemExit(f"{rel} missing phrase: {phrase}")

queue = load("FOLLOWTHROUGH-QUEUE.json")
by_id = {e.get("id"): e for e in queue.get("entries", [])}
if by_id.get("FT-0198-NONHOST-RESPONSE-ARTIFACT-COLLECTION", {}).get("state") != "closed":
    raise SystemExit("non-host artifact collection queue item should be closed")
if by_id.get("FT-0198-QUORUM-RECOMPUTE-ACTUAL-IMPORT-REPLAY", {}).get("state") != "closed":
    raise SystemExit("quorum replay queue item should be closed")
if by_id.get("FT-0199-ACTUAL-LIVE-COUNTERPARTY-RESPONSE", {}).get("state") != "open":
    raise SystemExit("actual live counterparty response queue item should remain open")

mp = load(f"examples/research-tail-compaction-map-{REV}.json")
if any(c.get("action") != "compacted" for c in mp.get("clusters", [])):
    raise SystemExit("rev0199 must keep all research-tail clusters compacted")

print("audit_nonhost_response_import_replay: OK")
''')

# ---------------------------------------------------------------------------
# Update audit scripts / lint to include rev0199.
# ---------------------------------------------------------------------------
# Generic registry audit required families.
path = ROOT / "tools/audit_schema_fixture_coverage.py"
txt = path.read_text(encoding="utf-8")
txt = txt.replace("'LIVE-COUNTERPARTY-IMPORT-ATTEMPT', 'QUORUM-RECOMPUTATION-REPORT'", "'LIVE-COUNTERPARTY-IMPORT-ATTEMPT', 'QUORUM-RECOMPUTATION-REPORT', 'NONHOST-RESPONSE-ARTIFACT-ENVELOPE', 'LIVE-IMPORT-REPLAY-REPORT'")
path.write_text(txt, encoding="utf-8")

# Generic rights coverage audit required domains.
path = ROOT / "tools/audit_rights_domain_coverage.py"
txt = path.read_text(encoding="utf-8")
txt = txt.replace('"quorum-recomputation-report",\n}', '"quorum-recomputation-report",\n    "nonhost-response-artifact-envelope",\n    "live-import-replay-report",\n}')
path.write_text(txt, encoding="utf-8")

# Lint required list / early audits.
path = ROOT / "tools/lint_archive.py"
txt = path.read_text(encoding="utf-8")
insert_after = "'tools/audit_live_counterparty_import_and_quorum_recompute.py',\n"
if "'tools/audit_nonhost_response_import_replay.py'," not in txt:
    txt = txt.replace(insert_after, insert_after + "    'tools/audit_nonhost_response_import_replay.py',\n", 1)
    txt = txt.replace(insert_after, insert_after + "    'tools/audit_nonhost_response_import_replay.py',\n", 1)
required_insert = "    'tools/audit_live_counterparty_import_and_quorum_recompute.py',\n    'tools/package_release.py',\n"
if "examples/nonhost-response-artifact-envelope-result-return-institutional-dryrun.json" not in txt:
    rev_required = """    'docs/30-transition/nonhost-response-artifact-envelope-and-import-replay.md',
    'schemas/nonhost-response-artifact-envelope.schema.json',
    'examples/nonhost-response-artifact-envelope-result-return-institutional-dryrun.json',
    'schemas/live-import-replay-report.schema.json',
    'examples/live-import-replay-report-result-return-institutional-dryrun.json',
    'fixtures/negative-tests/nonhost-response-envelope-dryrun-imported-as-live.json',
    'fixtures/negative-tests/live-import-replay-dryrun-grants-live-floor.json',
    'fixtures/negative-tests/quorum-recompute-omits-artifact-envelope-exclusions.json',
    'examples/research-tail-compaction-map-rev0199.json',
    'examples/schema-fixture-domain-registry-rev0199.json',
    'examples/canon-surface-catalog-rev0199.json',
    'examples/doctrine-dependency-map-rev0199.json',
    'examples/rights-domain-coverage-map-rev0199.json',
    'tools/audit_nonhost_response_import_replay.py',
"""
    txt = txt.replace(required_insert, "    'tools/audit_live_counterparty_import_and_quorum_recompute.py',\n" + rev_required + "    'tools/package_release.py',\n")
path.write_text(txt, encoding="utf-8")

# ---------------------------------------------------------------------------
# Append to existing operational surface to connect rev0199 to rev0198 spine.
# ---------------------------------------------------------------------------
append_path = ROOT / "docs/30-transition/live-counterparty-import-attempt-and-quorum-recompute.md"
append_txt = append_path.read_text(encoding="utf-8")
if "rev0199 non-host artifact replay" not in append_txt:
    append_txt += f"""

## rev0199 non-host artifact replay

**Non-host-looking artifact is not live receipt.** rev0199 adds `docs/30-transition/nonhost-response-artifact-envelope-and-import-replay.md` plus NHRAE/LIRR objects so the archive can accept response-like artifacts without trusting their appearance. The result-return dry-run artifact is non-host retained and signed/timestamped for rehearsal, but recomputation still keeps `independent_receipts_present=0` because the envelope is institutional dry run rather than live counterparty evidence.

The live floor may change only after a future artifact passes envelope provenance, response verification, intake checks, actual import gate, and quorum recomputation. One result-return class remains class-local and cannot satisfy cross-critical reliance.
"""
append_path.write_text(append_txt, encoding="utf-8")

# ---------------------------------------------------------------------------
# Active maps and registries.
# ---------------------------------------------------------------------------
# Schema/fixture registry: copy active rev0198, append families, refresh counts.
registry = load("examples/schema-fixture-domain-registry-rev0198.json")
registry["registry_id"] = "SCHEMA-FIXTURE-REGISTRY-rev0199"
registry["created_at"] = CREATED
registry["coverage_scope"] = "rev0199 active registry adds non-host response artifact envelope and live import replay report families; counts remain full-corpus while family coverage remains selective."
registry["coverage_claim"] = "mixed-current-plus-counts"
existing_fams = {f["family_id"] for f in registry["families"]}
new_fams = [
  {
    "family_id": "NONHOST-RESPONSE-ARTIFACT-ENVELOPE",
    "domain": "external-receipts-artifact-envelope",
    "lifecycle_axes": ["external-receipt", "provenance", "import-replay"],
    "owner_surface": "docs/30-transition/nonhost-response-artifact-envelope-and-import-replay.md",
    "schema_path": "schemas/nonhost-response-artifact-envelope.schema.json",
    "example_path": "examples/nonhost-response-artifact-envelope-result-return-institutional-dryrun.json",
    "fixture_ids": ["NF-PLAYBOOK-2026-0020"],
    "privacy_default": "public-shell-sealed-details",
    "reliance_effect": "stayed",
    "refactor_note": "New rev0199 family; distinguishes non-host-looking dry-run artifacts from live counterparty receipts."
  },
  {
    "family_id": "LIVE-IMPORT-REPLAY-REPORT",
    "domain": "external-receipts-import-replay",
    "lifecycle_axes": ["external-receipt", "import-gate", "quorum-recompute"],
    "owner_surface": "docs/30-transition/nonhost-response-artifact-envelope-and-import-replay.md",
    "schema_path": "schemas/live-import-replay-report.schema.json",
    "example_path": "examples/live-import-replay-report-result-return-institutional-dryrun.json",
    "fixture_ids": ["NF-PLAYBOOK-2026-0021", "NF-PLAYBOOK-2026-0022"],
    "privacy_default": "public-shell-sealed-details",
    "reliance_effect": "stayed",
    "refactor_note": "New rev0199 family; replay binds envelope, response, intake, import gate, and recomputation without live overclaim."
  }
]
for fam in new_fams:
    if fam["family_id"] not in existing_fams:
        registry["families"].append(fam)
registry["audit_counts"] = {
  "schemas": len(list((ROOT / "schemas").glob("*.json"))),
  "examples": len(list((ROOT / "examples").glob("*.json"))),
  "negative_fixtures": len(list((ROOT / "fixtures/negative-tests").glob("*.json"))),
  "registered_families": len(registry["families"])
}
write_json("examples/schema-fixture-domain-registry-rev0199.json", registry)

# Research-tail map stays compacted.
rtc = load("examples/research-tail-compaction-map-rev0198.json")
rtc["map_id"] = "RTC-MAP-rev0199"
rtc["created_at"] = CREATED
rtc["revision"] = REV
rtc["scope"] = "rev0199 keeps all research-tail clusters compacted while moving response artifact provenance into envelope/replay objects."
write_json("examples/research-tail-compaction-map-rev0199.json", rtc)

# Canon catalog: carry forward prior current release set and add new rev0199 surfaces.
new_surface_paths = [
  "docs/30-transition/nonhost-response-artifact-envelope-and-import-replay.md",
  "schemas/nonhost-response-artifact-envelope.schema.json",
  "examples/nonhost-response-artifact-envelope-result-return-institutional-dryrun.json",
  "schemas/live-import-replay-report.schema.json",
  "examples/live-import-replay-report-result-return-institutional-dryrun.json",
  "examples/live-counterparty-import-attempt-result-return-institutional-dryrun-response.json",
  "examples/external-receipt-response-record-result-return-institutional-envelope-dryrun.json",
  "examples/external-receipt-intake-record-result-return-institutional-envelope-dryrun.json",
  "examples/actual-receipt-import-gate-result-return-institutional-dryrun-no-live-delta.json",
  "examples/external-receipt-quorum-ledger-nonhost-artifact-replay-dryrun.json",
  "examples/failed-gate-public-summary-nonhost-artifact-replay.json",
  "examples/wrsr-live-exercise-outcome-nonhost-artifact-replay-stayed.json",
  "examples/quorum-recomputation-report-nonhost-artifact-replay-rev0199.json",
  "fixtures/negative-tests/nonhost-response-envelope-dryrun-imported-as-live.json",
  "fixtures/negative-tests/live-import-replay-dryrun-grants-live-floor.json",
  "fixtures/negative-tests/quorum-recompute-omits-artifact-envelope-exclusions.json",
  "examples/research-tail-compaction-map-rev0199.json",
  "examples/schema-fixture-domain-registry-rev0199.json",
  "examples/canon-surface-catalog-rev0199.json",
  "examples/doctrine-dependency-map-rev0199.json",
  "examples/rights-domain-coverage-map-rev0199.json",
  "tools/audit_nonhost_response_import_replay.py"
]

prev_catalog = load("examples/canon-surface-catalog-rev0198.json")
paths = []
for p in new_surface_paths + [s["path"] for s in prev_catalog["surfaces"]]:
    if p not in paths:
        paths.append(p)

def cls_for(path):
    if path.startswith("schemas/"):
        return "schema"
    if path.startswith("examples/"):
        return "example"
    if path.startswith("fixtures/negative-tests/"):
        return "fixture"
    if path.startswith("tools/"):
        return "tool"
    if path.startswith("docs/30-transition/"):
        return "transition"
    if path.startswith("docs/00-meta/"):
        return "meta"
    return "doctrine"

catalog = {
  "catalog_id": "CANON-SURFACE-CATALOG-rev0199",
  "created_at": CREATED,
  "revision": REV,
  "scope": "rev0199 active and carry-forward current-release surfaces for non-host response envelopes, import replay, quorum recomputation, and receipt no-overclaim controls.",
  "counts": {},
  "surfaces": [],
  "audit_findings": ["rev0199 corrected stale README/START_HERE front-door drift and catalogs the new NHRAE/LIRR chain."],
  "refactor_actions": ["Route non-host-looking response artifacts through envelope/replay objects before import or quorum recomputation."],
  "public_summary": "rev0199 catalog highlights the envelope and replay controls needed before non-host-looking evidence can affect live reliance."
}
counts = {"surfaces": 0, "markdown": 0, "schemas": 0, "examples": 0, "fixtures": 0, "tools": 0}
for i, p in enumerate(paths, 1):
    c = cls_for(p)
    counts["surfaces"] += 1
    if c in {"meta", "doctrine", "transition"}:
        counts["markdown"] += 1
    elif c == "schema":
        counts["schemas"] += 1
    elif c == "example":
        counts["examples"] += 1
    elif c == "fixture":
        counts["fixtures"] += 1
    elif c == "tool":
        counts["tools"] += 1
    catalog["surfaces"].append({
      "surface_id": f"REV0199-SURF-{i:03d}",
      "path": p,
      "surface_class": c,
      "lifecycle_axes": ["external-receipts", "artifact-provenance", "import-replay", "quorum-recompute"],
      "owner_role": "receipt/reliance steward",
      "supersession_state": "current" if p.endswith(".md") else ("negative-test" if c == "fixture" else "implementation"),
      "review_cadence": "per-release",
      "title_or_name": Path(p).name
    })
catalog["counts"] = counts
write_json("examples/canon-surface-catalog-rev0199.json", catalog)

# Doctrine dependency map.
dmap = {
  "map_id": "DOCTRINE-DEPENDENCY-MAP-rev0199",
  "created_at": CREATED,
  "revision": REV,
  "scope": "Dependency map for rev0199 non-host response envelopes and live import replay controls.",
  "surfaces": [
    {
      "surface_id": "REV0199-DM-001",
      "path": "docs/30-transition/nonhost-response-artifact-envelope-and-import-replay.md",
      "layer": "transition",
      "depends_on": [
        "docs/30-transition/live-counterparty-import-attempt-and-quorum-recompute.md",
        "docs/30-transition/external-receipt-response-and-quorum-reconciliation.md",
        "docs/30-transition/actual-intake-import-gate-and-failed-gate-public-summary.md",
        "docs/30-transition/result-return-receipt-and-live-request-kit.md"
      ],
      "overlaps_with": ["docs/30-transition/cross-critical-witnessed-drill-readiness-and-receipt-matrix.md"],
      "supersedes": [],
      "owner_role": "receipt/reliance steward",
      "review_cadence": "per-release",
      "refactor_risk": "medium"
    },
    {
      "surface_id": "REV0199-DM-002",
      "path": "examples/live-import-replay-report-result-return-institutional-dryrun.json",
      "layer": "example",
      "depends_on": [
        "schemas/live-import-replay-report.schema.json",
        "examples/nonhost-response-artifact-envelope-result-return-institutional-dryrun.json",
        "examples/actual-receipt-import-gate-result-return-institutional-dryrun-no-live-delta.json",
        "examples/quorum-recomputation-report-nonhost-artifact-replay-rev0199.json"
      ],
      "overlaps_with": ["examples/quorum-recomputation-report-live-floor-zero-rev0198.json"],
      "supersedes": [],
      "owner_role": "release-steward",
      "review_cadence": "per-release",
      "refactor_risk": "medium"
    }
  ],
  "audit_findings": ["Non-host-looking artifact evidence now has an envelope/replay dependency before any import gate can alter live floor."],
  "refactor_actions": ["Keep artifact envelope, response, intake, import gate, replay report, and recomputation as separate gates."],
  "public_summary": "rev0199 blocks non-host-looking dry-run evidence from being laundered into live receipt or cross-critical reliance."
}
write_json("examples/doctrine-dependency-map-rev0199.json", dmap)

rights = load("examples/rights-domain-coverage-map-rev0198.json")
rights["map_id"] = "RIGHTS-DOMAIN-COVERAGE-rev0199"
rights["created_at"] = CREATED
rights["revision"] = REV
rights["scope"] = "rev0199 coverage for non-host response artifact envelopes and live import replay."
rights["domains"].extend([
  {
    "domain_id": "nonhost-response-artifact-envelope",
    "title": "Non-host response artifact envelope and provenance disqualification",
    "domain_class": "audit",
    "owner_surface": "docs/30-transition/nonhost-response-artifact-envelope-and-import-replay.md",
    "covered_surfaces": [
      "docs/30-transition/nonhost-response-artifact-envelope-and-import-replay.md",
      "docs/30-transition/live-counterparty-import-attempt-and-quorum-recompute.md",
      "docs/30-transition/actual-intake-import-gate-and-failed-gate-public-summary.md"
    ],
    "schema_families": ["NONHOST-RESPONSE-ARTIFACT-ENVELOPE", "EXTERNAL-RECEIPT-RESPONSE-RECORD", "EXTERNAL-RECEIPT-INTAKE-RECORD"],
    "fixture_ids": ["NF-PLAYBOOK-2026-0020"],
    "coverage_state": "adequate",
    "open_gaps": ["Current envelope is institutional dry run, not actual live counterparty response."],
    "next_audit_actions": ["Replace envelope with actual live counterparty evidence only when provenance supports artifact_mode=live-counterparty."]
  },
  {
    "domain_id": "live-import-replay-report",
    "title": "Live import replay and no-overclaim recomputation chain",
    "domain_class": "audit",
    "owner_surface": "docs/30-transition/nonhost-response-artifact-envelope-and-import-replay.md",
    "covered_surfaces": [
      "docs/30-transition/nonhost-response-artifact-envelope-and-import-replay.md",
      "docs/30-transition/live-counterparty-import-attempt-and-quorum-recompute.md",
      "docs/30-transition/external-receipt-response-and-quorum-reconciliation.md"
    ],
    "schema_families": ["LIVE-IMPORT-REPLAY-REPORT", "ACTUAL-RECEIPT-IMPORT-GATE", "QUORUM-RECOMPUTATION-REPORT"],
    "fixture_ids": ["NF-PLAYBOOK-2026-0021", "NF-PLAYBOOK-2026-0022"],
    "coverage_state": "adequate",
    "open_gaps": ["No actual-live-import replay exists; current replay proves dry-run exclusion only."],
    "next_audit_actions": ["Run replay again after actual live response is collected; do not allow one class-local import to satisfy cross-critical quorum."]
  }
])
rights["audit_findings"] = ["rev0199 covers response artifact provenance and import replay while keeping live reliance stayed."]
rights["refactor_actions"] = ["Use NHRAE/LIRR objects as the operational spine for future actual response artifacts."]
rights["public_summary"] = "rev0199 rights coverage adds non-host artifact envelope and live import replay domains while keeping reliance stayed."
write_json("examples/rights-domain-coverage-map-rev0199.json", rights)

# ---------------------------------------------------------------------------
# Queue updates.
# ---------------------------------------------------------------------------
queue = load("FOLLOWTHROUGH-QUEUE.json")
queue["queue_id"] = "FOLLOWTHROUGH-QUEUE-rev0199"
queue["revision"] = REV
queue["updated_at"] = CREATED
entries = queue["entries"]
by_id = {e["id"]: e for e in entries}
for eid in ["FT-0198-NONHOST-RESPONSE-ARTIFACT-COLLECTION", "FT-0198-QUORUM-RECOMPUTE-ACTUAL-IMPORT-REPLAY"]:
    if eid in by_id:
        by_id[eid]["state"] = "closed"
        by_id[eid]["need"] = "rev0199 adds a high-fidelity non-host dry-run artifact envelope and import replay chain while preserving zero live floor."
        by_id[eid]["why"] = by_id[eid]["need"]
        by_id[eid]["next_action"] = "Closed by rev0199 NHRAE/LIRR objectization and QRR replay; next work requires actual live counterparty evidence."
        by_id[eid]["closure_condition"] = "Closed because envelope, response, intake, import gate, replay report, recomputation, fixtures, and audit exist and lint passes."
        by_id[eid]["review_by_revision"] = REV

def new_entry(eid, title, state, priority, risk, workstream, receiving, need, next_action, closure, depends=None):
    if eid in by_id:
        by_id[eid].update({"state": state, "priority": priority, "risk_class": risk, "workstream": workstream, "receiving_surface": receiving, "need": need, "why": need, "next_action": next_action, "closure_condition": closure, "review_by_revision": "rev0200", "source_state": "opened-by-rev0199", "source_revision": REV, "depends_on": depends or []})
    else:
        entries.append({
          "id": eid,
          "title": title,
          "state": state,
          "priority": priority,
          "risk_class": risk,
          "workstream": workstream,
          "need": need,
          "why": need,
          "receiving_surface": receiving,
          "next_action": next_action,
          "closure_condition": closure,
          "source_state": "opened-by-rev0199",
          "source_revision": REV,
          "review_by_revision": "rev0200",
          "depends_on": depends or []
        })
new_entry(
  "FT-0199-ACTUAL-LIVE-COUNTERPARTY-RESPONSE",
  "Actual live counterparty response artifact",
  "open",
  "P0",
  "survival-evidence-remedy",
  "external-receipts",
  "docs/30-transition/nonhost-response-artifact-envelope-and-import-replay.md",
  "rev0199 proves the dry-run envelope/replay chain but still lacks a genuine live counterparty response artifact.",
  "Collect or institutionally witness a true live counterparty response, then mark the envelope artifact_mode=live-counterparty only if provenance supports it.",
  "Close only when an actual live counterparty response artifact exists, enters NHRAE/ERRR/ERIR/ARIG/LIRR/QRR chain, and recomputation remains honest about class-local/non-quorum effects.",
  ["FT-0195-ACTUAL-RESPONSE-COUNTERPARTY-COLLECTION"]
)
new_entry(
  "FT-0199-IMPORT-REPLAY-LIVE-CLASS-LOCAL-TEST",
  "Live import replay class-local test",
  "open",
  "P0",
  "closure-infrastructure",
  "external-receipts",
  "examples/live-import-replay-report-result-return-institutional-dryrun.json",
  "The replay report currently proves exclusion, not live class-local import behavior.",
  "After a live counterparty response exists, rerun import replay and prove a single valid class import changes only that class, not cross-critical quorum.",
  "Close only when a live replay test either grants a class-local delta with no cross-critical overclaim or explicitly rejects the attempted live import with public failed-gate summary.",
  ["FT-0199-ACTUAL-LIVE-COUNTERPARTY-RESPONSE"]
)
write_json("FOLLOWTHROUGH-QUEUE.json", queue)

# ---------------------------------------------------------------------------
# Front doors, status, receipt, docs index, archive index, changelog.
# ---------------------------------------------------------------------------
read_list = [
  "README.md",
  "docs/30-transition/nonhost-response-artifact-envelope-and-import-replay.md",
  "schemas/nonhost-response-artifact-envelope.schema.json",
  "examples/nonhost-response-artifact-envelope-result-return-institutional-dryrun.json",
  "schemas/live-import-replay-report.schema.json",
  "examples/live-import-replay-report-result-return-institutional-dryrun.json",
  "examples/live-counterparty-import-attempt-result-return-institutional-dryrun-response.json",
  "examples/external-receipt-response-record-result-return-institutional-envelope-dryrun.json",
  "examples/external-receipt-intake-record-result-return-institutional-envelope-dryrun.json",
  "examples/actual-receipt-import-gate-result-return-institutional-dryrun-no-live-delta.json",
  "examples/quorum-recomputation-report-nonhost-artifact-replay-rev0199.json",
  "examples/failed-gate-public-summary-nonhost-artifact-replay.json",
  "examples/live-drill-execution-packet-cross-critical-witnessed-pack.json",
  "fixtures/negative-tests/nonhost-response-envelope-dryrun-imported-as-live.json",
  "fixtures/negative-tests/live-import-replay-dryrun-grants-live-floor.json",
  "fixtures/negative-tests/quorum-recompute-omits-artifact-envelope-exclusions.json",
  "FOLLOWTHROUGH-QUEUE.json",
  "examples/schema-fixture-domain-registry-rev0199.json",
  "examples/canon-surface-catalog-rev0199.json",
  "examples/doctrine-dependency-map-rev0199.json",
  "examples/rights-domain-coverage-map-rev0199.json",
  "examples/research-tail-compaction-map-rev0199.json",
  "docs/00-meta/research-tail-reopen-gate-and-sprawl-control.md",
  "docs/00-meta/charter.md"
]
start = "# Start here — AI Personhood rev0199\n\nThis handoff starts from the non-host response artifact envelope and live import replay pass. Read it as evidence plumbing: external-looking evidence is useful only after provenance, import gate, and recomputation prove what weight it deserves.\n\n"
for i, rel in enumerate(read_list, 1):
    start += f"{i}. `{rel}`\n"
start += """

## This revision

rev0199 adds an envelope/replay chain for non-host-looking response artifacts. The result-return artifact is high-fidelity and non-host retained, but it is explicitly institutional dry run, so live reliance remains stayed and `independent_receipts_present` remains zero.

Core rules: **Non-host-looking artifact is not live receipt. Witnessed envelope is not counterparty authority. Import replay must preserve disqualification. One class-local import is not cross-critical reliance.**

## Current open risk

The archive still has no actual live counterparty response. rev0199 makes the import pathway safer and more concrete, but the next real reliance improvement requires a genuine non-host response artifact and replay through the same gates.
"""
write_text("START_HERE.md", start)

readme = f"""# AI Personhood datacube — rev0199

This archive assumes the working premise of AI personhood and focuses on operational rights infrastructure: continuity, evidence, representation, remedy, proof standards, and transition machinery.

## This revision

**Active revision:** `rev0199`

rev0199 is the non-host response artifact envelope and import replay pass. It fixes a sharper evidence defect: an artifact can look external, signed, timestamped, and non-host retained while still being only an institutional dry run. The new NHRAE/LIRR chain proves that such an artifact can be rehearsed without increasing the live receipt floor.

Read first: `docs/30-transition/nonhost-response-artifact-envelope-and-import-replay.md`.

Core rules: **Non-host-looking artifact is not live receipt. Witnessed envelope is not counterparty authority. Import replay must preserve disqualification. One class-local import is not cross-critical reliance.**

New operational artifacts:

- `docs/30-transition/nonhost-response-artifact-envelope-and-import-replay.md`
- `schemas/nonhost-response-artifact-envelope.schema.json`
- `examples/nonhost-response-artifact-envelope-result-return-institutional-dryrun.json`
- `schemas/live-import-replay-report.schema.json`
- `examples/live-import-replay-report-result-return-institutional-dryrun.json`
- `examples/live-counterparty-import-attempt-result-return-institutional-dryrun-response.json`
- `examples/external-receipt-response-record-result-return-institutional-envelope-dryrun.json`
- `examples/external-receipt-intake-record-result-return-institutional-envelope-dryrun.json`
- `examples/actual-receipt-import-gate-result-return-institutional-dryrun-no-live-delta.json`
- `examples/external-receipt-quorum-ledger-nonhost-artifact-replay-dryrun.json`
- `examples/quorum-recomputation-report-nonhost-artifact-replay-rev0199.json`
- `examples/failed-gate-public-summary-nonhost-artifact-replay.json`
- `fixtures/negative-tests/nonhost-response-envelope-dryrun-imported-as-live.json`
- `fixtures/negative-tests/live-import-replay-dryrun-grants-live-floor.json`
- `fixtures/negative-tests/quorum-recompute-omits-artifact-envelope-exclusions.json`
- `tools/audit_nonhost_response_import_replay.py`

## Validation posture

`make handoff-release` is the release command. It regenerates the context pack and manifest, runs lint and release-specific audits, and packages the archive. The fixture suite/report now cover 110 entries.

Reliance remains stayed where drills are synthetic, fixture-only, preflight-only, simulated, defective, declined, expired, host-self-attested, dry-run, missing actual external receipts, or where WRSR exercise outcomes lack actual external representative/RERB receipt, result return, anti-signal-gaming safeguards, or live import through the provenance gate.

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
15. Receipt quorum ledger: aggregate receipt records while separating dry-run rehearsal from live quorum.
16. Result-return/request kit: rehearse result return and live receipt requests without treating request or internal return as satisfaction.
17. Response reconciliation: preserve dry-run, defective, declined, and no-response artifacts without converting them into live quorum.
18. Response-to-intake conversion: prove eligible-only intake creation while preserving failed gates and keeping fixture conversion outside live receipt quorum.
19. Actual-intake import gate: reject actual-shaped fixture imports, require provenance before live-floor delta, and publish failed-gate non-satisfaction shells.
20. Live import recomputation: recompute the live floor from passed import gates rather than hand-edited quorum ledgers.
21. Non-host artifact replay: process external-looking dry-run evidence through envelope, response, intake, import gate, replay, and recomputation while keeping live weight zero.

## Still open

No actual live external receipt quorum exists. rev0199 gives the cube a safer pathway for the first actual non-host response, but it does not collect one. The next high-value step is a genuine live counterparty response artifact and import replay, with class-local credit only if provenance passes and cross-critical quorum still stayed.
"""
write_text("README.md", readme)

docs_readme = (ROOT / "docs/README.md").read_text(encoding="utf-8")
section = """## rev0199 non-host artifact envelope and import replay

Use `docs/30-transition/nonhost-response-artifact-envelope-and-import-replay.md` before treating any non-host-looking artifact as live receipt evidence. rev0199 adds NHRAE and LIRR objects so dry-run envelopes, responses, intake records, import gates, and quorum recomputation stay separated.

"""
if "## rev0199 non-host artifact envelope and import replay" not in docs_readme:
    docs_readme = docs_readme.replace("# Documents index\n\n", "# Documents index\n\n" + section)
write_text("docs/README.md", docs_readme)

# Change log prepend.
changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
entry = """## rev0199 — non-host response artifact envelope and import replay

- Added `docs/30-transition/nonhost-response-artifact-envelope-and-import-replay.md`.
- Added `schemas/nonhost-response-artifact-envelope.schema.json` and `examples/nonhost-response-artifact-envelope-result-return-institutional-dryrun.json`.
- Added `schemas/live-import-replay-report.schema.json` and `examples/live-import-replay-report-result-return-institutional-dryrun.json`.
- Added non-host dry-run response/intake/import-gate/quorum/recompute artifacts while preserving `independent_receipts_present=0`.
- Added `examples/failed-gate-public-summary-nonhost-artifact-replay.json` and a stayed WRSR replay outcome.
- Added fixtures `NF-PLAYBOOK-2026-0020` through `NF-PLAYBOOK-2026-0022` for dry-run envelope live import, dry-run replay live-floor delta, and missing exclusion/public-summary regressions.
- Added `tools/audit_nonhost_response_import_replay.py` and active rev0199 catalog/dependency/rights/registry/compaction maps.
- Corrected stale front-door drift in `README.md` and `START_HERE.md` so they now point at the active revision.

"""
if "## rev0199 — non-host response artifact envelope" not in changelog:
    changelog = changelog.replace("# Changelog\n\n", "# Changelog\n\n" + entry)
write_text("CHANGELOG.md", changelog)

# ARCHIVE_INDEX: ensure all markdown paths are indexed.
index = (ROOT / "ARCHIVE_INDEX.md").read_text(encoding="utf-8")
if "docs/30-transition/nonhost-response-artifact-envelope-and-import-replay.md" not in index:
    index += "\n- `docs/30-transition/nonhost-response-artifact-envelope-and-import-replay.md` — rev0199 non-host response artifact envelope and import replay surface.\n"
write_text("ARCHIVE_INDEX.md", index)

status = load("SURFACE-STATUS.json")
status.update({
  "revision": REV,
  "state_class": "nonhost-artifact-replay-stayed",
  "operational_head": {"surface": "START_HERE.md", "read_first": "docs/30-transition/nonhost-response-artifact-envelope-and-import-replay.md"},
  "formation_layer_status": "canon-retained with non-host dry-run artifact envelope and import replay controls; live receipts still absent",
  "known_open_gaps": [
    "No actual live counterparty response artifact has been collected.",
    "The rev0199 envelope is institutional dry run and cannot alter the live receipt floor.",
    "Quorum recomputation reports zero eligible live imports and zero live classes.",
    "A future one-class import must not satisfy cross-critical reliance.",
    "WRSR result-return remains stayed absent actual external result-return and review receipts.",
    "Registry coverage remains mixed-current-plus-counts, not full-archive-corpus.",
    "Could-not-run fixtures remain reliance blockers rather than passes."
  ]
})
status["new_surfaces"] = new_surface_paths + [p for p in status.get("new_surfaces", []) if p not in new_surface_paths]
write_json("SURFACE-STATUS.json", status)

receipt = {
  "revision": REV,
  "date": DATE,
  "authored_by": "OpenAI GPT-5.5 Thinking",
  "status_change": "advanced from live import recomputation to non-host response artifact envelope and import replay controls",
  "still_live": True,
  "summary": "Adds NHRAE/LIRR schemas/examples, a non-host high-fidelity dry-run response/intake/import/recompute chain, three blocking fixtures, active maps, front-door drift correction, and an audit preventing non-host-looking dry-run artifacts from satisfying live receipt or quorum.",
  "why_this_counts": [
    "The archive now processes a non-host-looking result-return artifact through the same chain expected for future actual receipts.",
    "The import replay proves external-looking dry-run evidence remains zero live weight.",
    "README and START_HERE now match the active revision instead of pointing to stale rev0197 surfaces."
  ],
  "files_added_or_changed": new_surface_paths + [
    "README.md", "START_HERE.md", "CHANGELOG.md", "docs/README.md", "ARCHIVE_INDEX.md", "SURFACE-STATUS.json", "FOLLOWTHROUGH-QUEUE.json",
    "examples/live-drill-execution-packet-cross-critical-witnessed-pack.json",
    "examples/external-receipt-request-packet-cross-critical-rep-rerb-result-return.json"
  ],
  "validation": {"expected_command": "make handoff-release", "reliance_state": "stayed; no actual live external receipt quorum"},
  "next_recommended_work": [
    "collect or institutionally witness a true live counterparty response artifact",
    "rerun envelope, response, intake, import gate, live import replay, and quorum recomputation",
    "prove any class-local import cannot satisfy cross-critical quorum by itself"
  ]
}
write_json("REVISION-RECEIPT.json", receipt)

# ---------------------------------------------------------------------------
# Update docs/00-meta trajectory minimally with new open question.
# ---------------------------------------------------------------------------
traj_path = ROOT / "docs/00-meta/trajectory-map.md"
traj = traj_path.read_text(encoding="utf-8")
if "OQ-0199" not in traj:
    traj += "\n`OQ-0199` — What exact external provenance package is sufficient to upgrade a non-host response artifact from institutional dry run to live counterparty evidence while preserving class-local-only credit and cross-critical quorum stays?\n"
traj_path.write_text(traj, encoding="utf-8")

print("apply_rev0199 complete")
