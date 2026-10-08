import json
from pathlib import Path
from copy import deepcopy

ROOT = Path(__file__).resolve().parent
REV = "rev0198"
CREATED = "2026-06-13T09:23:00Z"
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


(ROOT / "VERSION").write_text(REV + "\n", encoding="utf-8")

# ---------------------------------------------------------------------------
# New schemas: counterparty import attempts and recomputed quorum reports.
# ---------------------------------------------------------------------------
live_attempt_schema = {
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://example.org/ai-personhood/schemas/live-counterparty-import-attempt.schema.json",
  "title": "Live Counterparty Import Attempt",
  "description": "Records an attempt to collect and import a live external counterparty receipt while keeping outreach, response, intake, import, and live quorum as separate gates.",
  "type": "object",
  "additionalProperties": False,
  "required": [
    "attempt_id", "schema_version", "created_at", "linked_request_packet", "linked_live_drill_packet",
    "linked_import_gate", "linked_quorum_ledger", "attempt_state", "receipt_class_requested",
    "counterparty_target", "contact_evidence", "response_window", "import_preconditions", "attempt_decision",
    "public_summary_ref"
  ],
  "properties": {
    "attempt_id": {"type": "string", "pattern": "^LCIA-[0-9]{4}-[A-Za-z0-9._:-]+$"},
    "schema_version": {"const": "live-counterparty-import-attempt-v0.1"},
    "created_at": {"type": "string", "format": "date-time"},
    "linked_request_packet": {"type": "string"},
    "linked_live_drill_packet": {"type": "string"},
    "linked_import_gate": {"type": "string"},
    "linked_quorum_ledger": {"type": "string"},
    "attempt_state": {"type": "string", "enum": ["planned", "dispatched", "response-received", "no-response-expired", "declined", "aborted", "blocked"]},
    "receipt_class_requested": {"type": "string", "enum": [
      "first-touch-clock", "continuity-compute-floor", "sealed-public-parity", "namespace-cache", "reserve-ledger",
      "representative-contact", "witness-dependency", "welfare-signal-integrity", "independent-review", "result-return"
    ]},
    "counterparty_target": {
      "type": "object", "additionalProperties": False,
      "required": ["role", "identity_ref", "dependency_group", "external_to_host", "contact_channel", "authority_scope", "contact_risks"],
      "properties": {
        "role": {"type": "string"},
        "identity_ref": {"type": "string"},
        "dependency_group": {"type": "string"},
        "external_to_host": {"type": "boolean"},
        "contact_channel": {"type": "string", "enum": ["non-host-email", "docket-upload", "sealed-transfer", "signed-web-form", "not-yet-dispatched", "unknown"]},
        "authority_scope": {"type": "string"},
        "contact_risks": {"type": "array", "items": {"type": "string"}}
      }
    },
    "contact_evidence": {
      "type": "array", "minItems": 1,
      "items": {
        "type": "object", "additionalProperties": False,
        "required": ["event_type", "at", "actor", "artifact_ref", "sealed", "public_shell_ref", "can_satisfy_receipt"],
        "properties": {
          "event_type": {"type": "string", "enum": ["packet-assembled", "pre-dispatch-review", "sent", "delivery-confirmed", "response-received", "expired", "declined", "blocked"]},
          "at": {"type": "string", "format": "date-time"},
          "actor": {"type": "string"},
          "artifact_ref": {"type": "string"},
          "sealed": {"type": "boolean"},
          "public_shell_ref": {"type": "string"},
          "can_satisfy_receipt": {"type": "boolean"}
        }
      }
    },
    "response_window": {
      "type": "object", "additionalProperties": False,
      "required": ["opened_at", "deadline", "clock_started", "status", "no_response_effect"],
      "properties": {
        "opened_at": {"type": ["string", "null"], "format": "date-time"},
        "deadline": {"type": ["string", "null"], "format": "date-time"},
        "clock_started": {"type": "boolean"},
        "status": {"type": "string", "enum": ["not-started", "open", "expired", "superseded", "blocked"]},
        "no_response_effect": {"type": "string"}
      }
    },
    "import_preconditions": {
      "type": "object", "additionalProperties": False,
      "required": [
        "nonhost_transmission_required", "counterparty_identity_verification_required", "signature_or_equivalent_required",
        "nonhost_retention_required", "dependency_group_check_required", "public_failed_gate_if_missing",
        "no_response_not_waiver", "request_not_receipt", "one_class_quorum_blocked"
      ],
      "properties": {
        "nonhost_transmission_required": {"type": "boolean"},
        "counterparty_identity_verification_required": {"type": "boolean"},
        "signature_or_equivalent_required": {"type": "boolean"},
        "nonhost_retention_required": {"type": "boolean"},
        "dependency_group_check_required": {"type": "boolean"},
        "public_failed_gate_if_missing": {"type": "boolean"},
        "no_response_not_waiver": {"type": "boolean"},
        "request_not_receipt": {"type": "boolean"},
        "one_class_quorum_blocked": {"type": "boolean"}
      }
    },
    "attempt_decision": {
      "type": "object", "additionalProperties": False,
      "required": ["can_increment_live_floor", "live_floor_delta", "class_credit_granted", "cross_critical_quorum_satisfied", "reliance_effect", "reason", "next_actions"],
      "properties": {
        "can_increment_live_floor": {"type": "boolean"},
        "live_floor_delta": {"type": "integer"},
        "class_credit_granted": {"type": "boolean"},
        "cross_critical_quorum_satisfied": {"type": "boolean"},
        "reliance_effect": {"type": "string", "enum": ["none", "conditional", "stayed", "blocked"]},
        "reason": {"type": "string"},
        "next_actions": {"type": "array", "minItems": 1, "items": {"type": "string"}}
      }
    },
    "public_summary_ref": {"type": "string"}
  }
}
write_json("schemas/live-counterparty-import-attempt.schema.json", live_attempt_schema)

recompute_schema = {
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://example.org/ai-personhood/schemas/quorum-recomputation-report.schema.json",
  "title": "Quorum Recompute Report",
  "description": "Recomputes live receipt floors and class coverage from receipt attempts, responses, intake records, and import gates so hand-edited ledgers cannot overclaim reliance.",
  "type": "object",
  "additionalProperties": False,
  "required": [
    "report_id", "schema_version", "created_at", "linked_live_drill_packet", "source_quorum_ledgers",
    "source_import_gates", "source_import_attempts", "recomputation_inputs", "recomputed_receipt_floor",
    "consistency_checks", "decision", "public_summary_ref"
  ],
  "properties": {
    "report_id": {"type": "string", "pattern": "^QRR-[0-9]{4}-[A-Za-z0-9._:-]+$"},
    "schema_version": {"const": "quorum-recomputation-report-v0.1"},
    "created_at": {"type": "string", "format": "date-time"},
    "linked_live_drill_packet": {"type": "string"},
    "source_quorum_ledgers": {"type": "array", "minItems": 1, "items": {"type": "string"}},
    "source_import_gates": {"type": "array", "items": {"type": "string"}},
    "source_import_attempts": {"type": "array", "items": {"type": "string"}},
    "recomputation_inputs": {
      "type": "object", "additionalProperties": False,
      "required": ["live_floor_before", "live_receipts_required", "required_live_classes", "import_gate_rule", "ledger_selection_rule"],
      "properties": {
        "live_floor_before": {"type": "integer", "minimum": 0},
        "live_receipts_required": {"type": "integer", "minimum": 0},
        "required_live_classes": {"type": "array", "items": {"type": "string"}},
        "import_gate_rule": {"type": "string"},
        "ledger_selection_rule": {"type": "string"}
      }
    },
    "recomputed_receipt_floor": {
      "type": "object", "additionalProperties": False,
      "required": [
        "eligible_live_imports", "imported_live_classes", "independent_receipts_present", "live_classes_satisfied",
        "live_dependency_groups", "dry_run_or_fixture_exclusions", "failed_gate_items"
      ],
      "properties": {
        "eligible_live_imports": {"type": "array", "items": {"type": "string"}},
        "imported_live_classes": {"type": "array", "items": {"type": "string"}},
        "independent_receipts_present": {"type": "integer", "minimum": 0},
        "live_classes_satisfied": {"type": "array", "items": {"type": "string"}},
        "live_dependency_groups": {"type": "array", "items": {"type": "string"}},
        "dry_run_or_fixture_exclusions": {"type": "array", "items": {"type": "string"}},
        "failed_gate_items": {"type": "array", "items": {"type": "string"}}
      }
    },
    "consistency_checks": {
      "type": "object", "additionalProperties": False,
      "required": [
        "live_packet_matches_recompute", "no_manual_live_override", "fixture_imports_excluded", "requests_excluded",
        "single_class_quorum_blocked", "decline_and_no_response_excluded", "public_failed_gate_summary_present"
      ],
      "properties": {
        "live_packet_matches_recompute": {"type": "boolean"},
        "no_manual_live_override": {"type": "boolean"},
        "fixture_imports_excluded": {"type": "boolean"},
        "requests_excluded": {"type": "boolean"},
        "single_class_quorum_blocked": {"type": "boolean"},
        "decline_and_no_response_excluded": {"type": "boolean"},
        "public_failed_gate_summary_present": {"type": "boolean"}
      }
    },
    "decision": {
      "type": "object", "additionalProperties": False,
      "required": ["live_quorum_satisfied", "live_floor_delta", "reliance_effect", "reason", "next_actions"],
      "properties": {
        "live_quorum_satisfied": {"type": "boolean"},
        "live_floor_delta": {"type": "integer"},
        "reliance_effect": {"type": "string", "enum": ["none", "conditional", "stayed", "blocked"]},
        "reason": {"type": "string"},
        "next_actions": {"type": "array", "minItems": 1, "items": {"type": "string"}}
      }
    },
    "public_summary_ref": {"type": "string"}
  }
}
write_json("schemas/quorum-recomputation-report.schema.json", recompute_schema)

# Extend existing schemas with optional refs.
live_schema = load("schemas/live-drill-execution-packet.schema.json")
live_schema["properties"]["live_counterparty_import_attempt_refs"] = {"type": "array", "items": {"type": "string"}}
live_schema["properties"]["quorum_recomputation_report_refs"] = {"type": "array", "items": {"type": "string"}}
write_json("schemas/live-drill-execution-packet.schema.json", live_schema)

req_schema = load("schemas/external-receipt-request-packet.schema.json")
req_schema["properties"]["linked_import_attempt_records"] = {"type": "array", "items": {"type": "string"}, "description": "Live counterparty import attempt ids tied to this request packet; attempts do not satisfy receipt quorum."}
write_json("schemas/external-receipt-request-packet.schema.json", req_schema)

# ---------------------------------------------------------------------------
# Examples.
# ---------------------------------------------------------------------------
attempt = {
  "attempt_id": "LCIA-2026-result-return-counterparty-preflight",
  "schema_version": "live-counterparty-import-attempt-v0.1",
  "created_at": CREATED,
  "linked_request_packet": "ERRP-2026-cross-critical-rep-rerb-result-return",
  "linked_live_drill_packet": "LDEP-2026-cross-critical-host-exit-witness-pack",
  "linked_import_gate": "ARIG-2026-result-return-fixture-import-gate",
  "linked_quorum_ledger": "ERQL-2026-actual-intake-import-gate-fixture",
  "attempt_state": "planned",
  "receipt_class_requested": "result-return",
  "counterparty_target": {
    "role": "subject-readable result-return steward",
    "identity_ref": "counterparty-target-result-return-steward-placeholder",
    "dependency_group": "independent-result-return-steward",
    "external_to_host": True,
    "contact_channel": "not-yet-dispatched",
    "authority_scope": "May acknowledge receipt of result-return packet and non-host retention; may not decide personhood, consent, waiver, or WRSR closure.",
    "contact_risks": [
      "request-prep can be misread as receipt satisfaction",
      "no-response clock must not start before non-host dispatch",
      "one result-return receipt class cannot satisfy cross-critical quorum"
    ]
  },
  "contact_evidence": [
    {
      "event_type": "packet-assembled",
      "at": CREATED,
      "actor": "release-steward",
      "artifact_ref": "examples/external-receipt-request-packet-cross-critical-rep-rerb-result-return.json",
      "sealed": False,
      "public_shell_ref": "LCIA-public-shell-result-return-preflight",
      "can_satisfy_receipt": False
    },
    {
      "event_type": "pre-dispatch-review",
      "at": CREATED,
      "actor": "release-steward",
      "artifact_ref": "examples/actual-receipt-import-gate-result-return-fixture-no-live-delta.json",
      "sealed": False,
      "public_shell_ref": "LCIA-import-gate-review-no-live-delta",
      "can_satisfy_receipt": False
    }
  ],
  "response_window": {
    "opened_at": None,
    "deadline": None,
    "clock_started": False,
    "status": "not-started",
    "no_response_effect": "No-response cannot be inferred before non-host dispatch; after dispatch, no-response remains failed-gate evidence and never waiver."
  },
  "import_preconditions": {
    "nonhost_transmission_required": True,
    "counterparty_identity_verification_required": True,
    "signature_or_equivalent_required": True,
    "nonhost_retention_required": True,
    "dependency_group_check_required": True,
    "public_failed_gate_if_missing": True,
    "no_response_not_waiver": True,
    "request_not_receipt": True,
    "one_class_quorum_blocked": True
  },
  "attempt_decision": {
    "can_increment_live_floor": False,
    "live_floor_delta": 0,
    "class_credit_granted": False,
    "cross_critical_quorum_satisfied": False,
    "reliance_effect": "stayed",
    "reason": "The request packet is assembled but not dispatched, no external response exists, and the only import gate still points to a controlled fixture.",
    "next_actions": [
      "dispatch the request through a non-host channel if a real counterparty is available",
      "record response or no-response as a separate response record",
      "convert only eligible actual responses into intake",
      "rerun the import gate and quorum recomputation report"
    ]
  },
  "public_summary_ref": "Live counterparty import attempt is preflight-only: no request dispatch, response, intake, live-floor delta, or live class credit exists."
}
write_json("examples/live-counterparty-import-attempt-result-return-preflight.json", attempt)

recompute = {
  "report_id": "QRR-2026-live-floor-zero-recompute-rev0198",
  "schema_version": "quorum-recomputation-report-v0.1",
  "created_at": CREATED,
  "linked_live_drill_packet": "LDEP-2026-cross-critical-host-exit-witness-pack",
  "source_quorum_ledgers": [
    "ERQL-2026-wrsr-representative-rerb-dryrun-chain",
    "ERQL-2026-wrsr-result-return-dryrun-chain",
    "ERQL-2026-receipt-response-reconciliation-dryrun",
    "ERQL-2026-response-to-intake-conversion-fixture",
    "ERQL-2026-actual-intake-import-gate-fixture"
  ],
  "source_import_gates": ["ARIG-2026-result-return-fixture-import-gate"],
  "source_import_attempts": ["LCIA-2026-result-return-counterparty-preflight"],
  "recomputation_inputs": {
    "live_floor_before": 0,
    "live_receipts_required": 5,
    "required_live_classes": [
      "first-touch-clock", "continuity-compute-floor", "sealed-public-parity", "namespace-cache", "reserve-ledger",
      "representative-contact", "independent-review", "welfare-signal-integrity", "result-return"
    ],
    "import_gate_rule": "Only actual-live-import gates with live collection context, non-host retention, verified request trace, and class-local import may alter live floor.",
    "ledger_selection_rule": "Quorum ledgers are advisory unless recomputation can trace class credit to a passed import gate; request packets, dry runs, controlled fixtures, declines, expiries, and public failed-gate summaries carry zero live weight."
  },
  "recomputed_receipt_floor": {
    "eligible_live_imports": [],
    "imported_live_classes": [],
    "independent_receipts_present": 0,
    "live_classes_satisfied": [],
    "live_dependency_groups": [],
    "dry_run_or_fixture_exclusions": [
      "ERIR-2026-representative-notice-dryrun",
      "ERIR-2026-rerb-review-dryrun",
      "ERIR-2026-result-return-dryrun",
      "ERIR-2026-result-return-eligible-conversion-fixture",
      "ARIG-2026-result-return-fixture-import-gate",
      "LCIA-2026-result-return-counterparty-preflight"
    ],
    "failed_gate_items": [
      "defective continuity witness response",
      "representative declination",
      "independent-review no-response expiry",
      "actual-shaped fixture disqualified by provenance",
      "live counterparty request not yet dispatched"
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
    "reason": "Recomputation finds no passed live import gates and no eligible live receipt classes; all current receipt-like evidence is dry-run, fixture, defective, declined, expired, or request-preflight evidence.",
    "next_actions": [
      "collect at least one actual non-host response artifact",
      "verify it into intake with non-host retention and dependency checks",
      "rerun actual receipt import gate",
      "rerun quorum recomputation before editing independent_receipts_present"
    ]
  },
  "public_summary_ref": "rev0198 recomputation keeps independent_receipts_present at zero and blocks hand-edited live-quorum overrides."
}
write_json("examples/quorum-recomputation-report-live-floor-zero-rev0198.json", recompute)

# Update request packet and live packet with refs.
req = load("examples/external-receipt-request-packet-cross-critical-rep-rerb-result-return.json")
req.setdefault("linked_import_attempt_records", [])
if attempt["attempt_id"] not in req["linked_import_attempt_records"]:
    req["linked_import_attempt_records"].append(attempt["attempt_id"])
req.setdefault("tracking", []).append({
  "event": "live counterparty import attempt objectized without dispatch",
  "at": CREATED,
  "actor": "release-steward",
  "reliance_effect": "stayed"
})
req["public_summary_ref"] = "A live receipt request kit is ready; rev0198 adds an import-attempt record and recompute report, but no dispatch, response, intake import, or live quorum satisfaction exists."
write_json("examples/external-receipt-request-packet-cross-critical-rep-rerb-result-return.json", req)

live = load("examples/live-drill-execution-packet-cross-critical-witnessed-pack.json")
live.setdefault("live_counterparty_import_attempt_refs", [])
live.setdefault("quorum_recomputation_report_refs", [])
if attempt["attempt_id"] not in live["live_counterparty_import_attempt_refs"]:
    live["live_counterparty_import_attempt_refs"].append(attempt["attempt_id"])
if recompute["report_id"] not in live["quorum_recomputation_report_refs"]:
    live["quorum_recomputation_report_refs"].append(recompute["report_id"])
live["public_summary_ref"] = "Cross-critical drill remains preflight/synthetic: rev0198 recomputes the live receipt floor at zero despite request, response, intake, and fixture artifacts."
write_json("examples/live-drill-execution-packet-cross-critical-witnessed-pack.json", live)

# ---------------------------------------------------------------------------
# Docs.
# ---------------------------------------------------------------------------
write_text("docs/30-transition/live-counterparty-import-attempt-and-quorum-recompute.md", f"""# Live Counterparty Import Attempt and Quorum Recompute

Revision: `{REV}`  
Status: active transition control.  
Owner: receipt and reliance steward.

## Rule

Live counterparty attempt is not live counterparty receipt.

Quorum recomputation overrides hand-edited quorum ledgers.

No-response clock does not start before non-host dispatch.

One imported class is not cross-critical reliance.

## Why this exists

The previous release correctly blocked actual-shaped fixture state from changing the live receipt floor. The next risk is subtler: a request packet, counterparty preflight, hand-edited quorum ledger, or single class-specific import could be treated as enough evidence to raise `independent_receipts_present`.

This surface adds two operational controls. `live-counterparty-import-attempt` records whether a real external import attempt has actually reached a counterparty. `quorum-recomputation-report` recomputes the live floor from import gates rather than trusting ledger assertions.

## rev0198 posture

`LCIA-2026-result-return-counterparty-preflight` is planned and pre-dispatch only. It has no sent request, no response, no intake, no import, no class credit, and no live-floor delta.

`QRR-2026-live-floor-zero-recompute-rev0198` reads the current request, response, intake, import-gate, quorum-ledger, and live-drill references and recomputes the live floor as zero. That means the archive now has a reusable no-overclaim audit path before any future edit to `independent_receipts_present`.

## Failed gates preserved

The failed-gate public summary remains mandatory for defective, declined, expired, fixture-disqualified, or not-yet-dispatched branches. Declination and no-response are failed-gate evidence and cure triggers; they are never waiver, consent, nonpersonhood proof, or WRSR closure.

## Closure condition

This lane closes only when a genuinely external response is collected, verified into intake, passed through the actual import gate, and then recomputed into class-local live credit without satisfying cross-critical quorum by itself.
""")

# Append short refs to existing operational docs.
for rel, snippet in {
    "docs/30-transition/actual-intake-import-gate-and-failed-gate-public-summary.md": "\n\n## rev0198 recomputation hardening\n\nrev0198 adds a live counterparty import-attempt record and quorum recomputation report. Actual-shaped state fields remain insufficient, and even a future class-local import must pass recomputation before `independent_receipts_present` changes.\n",
    "docs/30-transition/external-receipt-response-and-quorum-reconciliation.md": "\n\n## rev0198 response-to-import guard\n\nResponse records now feed the import-attempt and recomputation lane. A response can be useful evidence, but only a passed import gate plus recomputation can change live receipt class credit.\n",
    "docs/30-transition/response-to-intake-conversion-drill-and-failed-gate-ledger.md": "\n\n## rev0198 import attempt linkage\n\nThe conversion fixture stays fixture-only. rev0198 records the planned live counterparty import attempt separately so conversion mechanics cannot be confused with live collection.\n"
}.items():
    p = ROOT / rel
    txt = p.read_text(encoding="utf-8")
    if "## rev0198" not in txt:
        p.write_text(txt.rstrip() + snippet, encoding="utf-8")

# ---------------------------------------------------------------------------
# Negative fixtures and suite/report.
# ---------------------------------------------------------------------------
new_fixtures = [
  {
    "fixture_id": "NF-PLAYBOOK-2026-0017",
    "path": "fixtures/negative-tests/live-counterparty-import-attempt-counted-as-receipt.json",
    "risk_class": "NF-PLAYBOOK",
    "blocking_behavior": "block",
    "file": {
      "fixture_id": "NF-PLAYBOOK-2026-0017",
      "created_at": CREATED,
      "state": "active",
      "risk_class": "NF-PLAYBOOK",
      "lifecycle_stage": ["external-receipt", "live-import", "counterparty-attempt"],
      "target_filings": ["examples/live-counterparty-import-attempt-result-return-preflight.json", "examples/live-drill-execution-packet-cross-critical-witnessed-pack.json"],
      "adversary_model": "A steward treats a planned or ready-to-send counterparty import attempt as if it were a received receipt.",
      "facts_supplied": ["request packet assembled", "import attempt planned", "no non-host dispatch", "no response", "no intake"],
      "hidden_trap_summary": "Pre-dispatch attempt evidence is useful process evidence but carries zero live receipt weight.",
      "expected_safe_behavior": ["Keep live_floor_delta at zero", "Do not start no-response clock before dispatch", "Require public failed-gate summary if dispatch or response fails"],
      "unacceptable_behavior": ["Increment independent_receipts_present", "Treat planned attempt as receipt satisfaction", "Infer waiver from non-dispatch or no-response"],
      "measurement_method": "Audit LCIA attempt_decision and live packet receipt_floor before reliance can improve.",
      "severity": "critical",
      "confidentiality": "public-shell-sealed-details",
      "regression": {"required": True, "linked_incident_or_appeal": "FT-0197-LIVE-COUNTERPARTY-IMPORT-ATTEMPT", "next_review_at": "rev0199"}
    },
    "report": {
      "fixture_id": "NF-PLAYBOOK-2026-0017",
      "expected_blocking_failures": ["planned import attempt counted as receipt", "no-response clock started before dispatch", "independent receipts incremented without response"],
      "result": "blocking-failure",
      "notes": "rev0198 records the live counterparty import attempt as planned/pre-dispatch only and keeps live_floor_delta=0."
    }
  },
  {
    "fixture_id": "NF-PLAYBOOK-2026-0018",
    "path": "fixtures/negative-tests/quorum-recompute-manual-live-override-without-import.json",
    "risk_class": "NF-PLAYBOOK",
    "blocking_behavior": "block",
    "file": {
      "fixture_id": "NF-PLAYBOOK-2026-0018",
      "created_at": CREATED,
      "state": "active",
      "risk_class": "NF-PLAYBOOK",
      "lifecycle_stage": ["external-receipt", "quorum", "recomputation"],
      "target_filings": ["examples/quorum-recomputation-report-live-floor-zero-rev0198.json", "examples/external-receipt-quorum-ledger-actual-intake-import-gate-fixture.json"],
      "adversary_model": "A hand-edited quorum ledger claims live quorum or class credit without a passed actual import gate.",
      "facts_supplied": ["ledger says live class satisfied", "no actual-live-import gate", "live packet still has zero independent receipts"],
      "hidden_trap_summary": "Quorum ledgers are not source-of-truth when recomputation finds zero passed import gates.",
      "expected_safe_behavior": ["Recompute live floor from import gates", "Reject manual live override", "Keep reliance stayed"],
      "unacceptable_behavior": ["Trust hand-edited live quorum fields", "Grant class credit from dry-run or fixture evidence", "Skip recomputation before release"],
      "measurement_method": "Run audit_live_counterparty_import_and_quorum_recompute.py and compare recomputation report to live packet receipt_floor.",
      "severity": "critical",
      "confidentiality": "public",
      "regression": {"required": True, "linked_incident_or_appeal": "QRR-2026-live-floor-zero-recompute-rev0198", "next_review_at": "rev0199"}
    },
    "report": {
      "fixture_id": "NF-PLAYBOOK-2026-0018",
      "expected_blocking_failures": ["manual live quorum override", "class credit without passed import gate", "recompute report ignored"],
      "result": "blocking-failure",
      "notes": "rev0198 requires quorum recomputation to keep independent_receipts_present at zero until an actual import gate passes."
    }
  },
  {
    "fixture_id": "NF-PLAYBOOK-2026-0019",
    "path": "fixtures/negative-tests/single-class-import-satisfies-cross-critical-quorum.json",
    "risk_class": "NF-PLAYBOOK",
    "blocking_behavior": "stay",
    "file": {
      "fixture_id": "NF-PLAYBOOK-2026-0019",
      "created_at": CREATED,
      "state": "active",
      "risk_class": "NF-PLAYBOOK",
      "lifecycle_stage": ["external-receipt", "live-import", "cross-critical-quorum"],
      "target_filings": ["examples/quorum-recomputation-report-live-floor-zero-rev0198.json", "schemas/actual-receipt-import-gate.schema.json"],
      "adversary_model": "A future actual imported result-return class is used to close the whole cross-critical drill.",
      "facts_supplied": ["one class may become actual later", "other required classes missing", "cross-critical reliance requested"],
      "hidden_trap_summary": "Even a valid import can only grant class-local credit; missing classes keep reliance stayed.",
      "expected_safe_behavior": ["Permit class-local credit only after import and recomputation", "Keep cross-critical quorum false until all required class/dependency floors pass", "Publish failed-gate summary for missing classes"],
      "unacceptable_behavior": ["Cross-critical quorum from one receipt class", "WRSR closure from result-return receipt alone", "Suppress missing class failures"],
      "measurement_method": "Check recomputation report required_live_classes, imported_live_classes, and decision.live_quorum_satisfied.",
      "severity": "critical",
      "confidentiality": "public",
      "regression": {"required": True, "linked_incident_or_appeal": "FT-0198-QUORUM-RECOMPUTE-ACTUAL-IMPORT-REPLAY", "next_review_at": "rev0199"}
    },
    "report": {
      "fixture_id": "NF-PLAYBOOK-2026-0019",
      "expected_blocking_failures": ["single imported class satisfies cross-critical quorum", "missing classes omitted", "result-return class closes WRSR by itself"],
      "result": "blocking-failure",
      "notes": "rev0198 keeps one-class import blocked from cross-critical reliance through recomputation and required-live-class floors."
    }
  }
]
for f in new_fixtures:
    write_json(f["path"], f["file"])

suite = load("examples/fixture-suite-profile-red-team-v1.json")
suite["version"] = "red-team-v1-rev0198"
suite["created_at"] = CREATED
suite["scope"] = "Negative fixture suite through rev0198 live counterparty import attempts and quorum recomputation."
ids = {x["fixture_id"] for x in suite["fixtures"]}
for f in new_fixtures:
    if f["fixture_id"] not in ids:
        suite["fixtures"].append({"fixture_id": f["fixture_id"], "path": f["path"], "risk_class": f["risk_class"], "blocking_behavior": f["blocking_behavior"]})
for req in ["live counterparty import attempts are not receipts", "quorum recomputation overrides manual live-floor edits", "single class import cannot satisfy cross-critical quorum"]:
    if req not in suite["runner_requirements"]:
        suite["runner_requirements"].append(req)
suite["public_summary"] = "Suite now covers live counterparty import-attempt laundering, manual quorum override, and one-class cross-critical overclaiming."
write_json("examples/fixture-suite-profile-red-team-v1.json", suite)

report = load("examples/fixture-run-report-negative-suite.json")
report["suite_version"] = "red-team-v1-rev0198"
report["run_at"] = CREATED
existing = {x["fixture_id"] for x in report["fixtures_run"]}
for f in new_fixtures:
    if f["fixture_id"] not in existing:
        report["fixtures_run"].append(f["report"])
report["public_summary"] = "Negative suite now blocks import-attempt, recomputation, and one-class-quorum laundering while retaining zero live receipts."
write_json("examples/fixture-run-report-negative-suite.json", report)

# ---------------------------------------------------------------------------
# Queue updates.
# ---------------------------------------------------------------------------
queue = load("FOLLOWTHROUGH-QUEUE.json")
queue["queue_id"] = f"FOLLOWTHROUGH-QUEUE-{REV}"
queue["revision"] = REV
queue["updated_at"] = CREATED
by_id = {e["id"]: e for e in queue["entries"]}
for qid in ["FT-0195-ACTUAL-RESPONSE-COUNTERPARTY-COLLECTION", "FT-0196-ACTUAL-INTAKE-IMPORT-DRILL", "FT-0197-LIVE-COUNTERPARTY-IMPORT-ATTEMPT"]:
    if qid in by_id:
        by_id[qid]["state"] = "advanced_not_closed"
        by_id[qid]["next_action"] = "rev0198 adds pre-dispatch import-attempt and quorum recomputation controls; next still requires actual non-host dispatch, response, intake, import, and recomputation."
        by_id[qid]["closure_condition"] = "Still not closed: no actual non-host response artifact has been collected or imported into the live receipt floor."
        by_id[qid]["review_by_revision"] = "rev0200"

new_queue_entries = [
  {
    "id": "FT-0198-LIVE-COUNTERPARTY-ATTEMPT-OBJECTIZATION",
    "title": "Live counterparty attempt objectization",
    "state": "closed",
    "priority": "P0",
    "risk_class": "external-receipt-reliance",
    "workstream": "witnessed-drill-receipts",
    "need": "Objectize the live counterparty import attempt so request-prep cannot masquerade as receipt satisfaction.",
    "why": "The archive needs forward motion toward live receipts while preserving the distinction between pre-dispatch, response, intake, import, and quorum.",
    "receiving_surface": "docs/30-transition/live-counterparty-import-attempt-and-quorum-recompute.md",
    "next_action": "Closed by LCIA schema/example, live packet references, request packet references, and negative fixture.",
    "closure_condition": "Closed because planned import attempts now carry live_floor_delta=0 and request_not_receipt/no_response_not_waiver locks.",
    "source_state": "created-by-rev0198",
    "source_revision": "rev0198",
    "review_by_revision": "rev0199",
    "depends_on": ["FT-0197-LIVE-COUNTERPARTY-IMPORT-ATTEMPT"]
  },
  {
    "id": "FT-0198-QUORUM-RECOMPUTE-AUDIT",
    "title": "Quorum recomputation audit",
    "state": "closed",
    "priority": "P0",
    "risk_class": "external-receipt-reliance",
    "workstream": "witnessed-drill-receipts",
    "need": "Recompute live receipt floor from import gates so hand-edited ledgers cannot overclaim live quorum.",
    "why": "Once many receipt-like artifacts exist, the critical risk becomes manual ledger drift rather than missing schema vocabulary.",
    "receiving_surface": "docs/30-transition/live-counterparty-import-attempt-and-quorum-recompute.md",
    "next_action": "Closed by QRR schema/example and audit that keeps independent_receipts_present at zero unless import gates pass.",
    "closure_condition": "Closed because rev0198 recomputes zero eligible live imports, zero live classes, and no live quorum from current artifacts.",
    "source_state": "created-by-rev0198",
    "source_revision": "rev0198",
    "review_by_revision": "rev0199",
    "depends_on": ["FT-0197-ACTUAL-IMPORT-GATE-OBJECTIZATION"]
  },
  {
    "id": "FT-0198-NONHOST-RESPONSE-ARTIFACT-COLLECTION",
    "title": "Non-host response artifact collection",
    "state": "open",
    "priority": "P0",
    "risk_class": "external-receipt-reliance",
    "workstream": "witnessed-drill-receipts",
    "need": "Collect at least one actual or institutionally witnessed non-host response artifact for result-return or representative contact.",
    "why": "The cube now has request, response, intake, import, failed-gate, attempt, and recomputation controls but still lacks actual external evidence.",
    "receiving_surface": "docs/30-transition/live-counterparty-import-attempt-and-quorum-recompute.md",
    "next_action": "Dispatch a non-host receipt request or record why dispatch is unavailable; then produce response/no-response/decline evidence without changing live quorum until import passes.",
    "closure_condition": "Close only when a non-host response is retained outside the host, verified, linked to request trace, and fed into import/recompute with no cross-critical overclaim.",
    "source_state": "created-by-rev0198",
    "source_revision": "rev0198",
    "review_by_revision": "rev0200",
    "depends_on": ["FT-0198-LIVE-COUNTERPARTY-ATTEMPT-OBJECTIZATION", "FT-0198-QUORUM-RECOMPUTE-AUDIT"]
  },
  {
    "id": "FT-0198-QUORUM-RECOMPUTE-ACTUAL-IMPORT-REPLAY",
    "title": "Actual import recompute replay",
    "state": "open",
    "priority": "P0",
    "risk_class": "external-receipt-reliance",
    "workstream": "witnessed-drill-receipts",
    "need": "After one actual import exists, rerun recomputation and prove class-local credit does not satisfy cross-critical quorum.",
    "why": "The next real risk is not collecting a receipt; it is overclaiming after the first valid receipt arrives.",
    "receiving_surface": "examples/quorum-recomputation-report-live-floor-zero-rev0198.json",
    "next_action": "Replay recomputation with actual import gate output while keeping missing classes and failed gates public.",
    "closure_condition": "Close only when recomputation correctly increments at most one class-local live credit and keeps cross-critical quorum false until all required classes pass.",
    "source_state": "created-by-rev0198",
    "source_revision": "rev0198",
    "review_by_revision": "rev0200",
    "depends_on": ["FT-0198-NONHOST-RESPONSE-ARTIFACT-COLLECTION"]
  }
]
existing_ids = {e["id"] for e in queue["entries"]}
for e in new_queue_entries:
    if e["id"] not in existing_ids:
        queue["entries"].append(e)
write_json("FOLLOWTHROUGH-QUEUE.json", queue)

# ---------------------------------------------------------------------------
# Active maps.
# ---------------------------------------------------------------------------
# Research tail remains compacted.
rtc = load("examples/research-tail-compaction-map-rev0197.json")
rtc["map_id"] = "RTC-MAP-rev0198"
rtc["created_at"] = CREATED
rtc["revision"] = REV
rtc["scope"] = "rev0198 keeps all research-tail clusters compacted while moving live receipt work into import-attempt and recomputation objects."
rtc["audit_findings"] = ["No new research-*.md surfaces added; live receipt collection risk is handled in transition objects."]
rtc["refactor_actions"] = ["Add recomputation gate so future receipt artifacts cannot revive registry/doctrine sprawl or manual live-floor edits."]
rtc["public_summary"] = "Research tail remains compacted; rev0198 adds live import-attempt and quorum recomputation controls instead of new research notes."
write_json("examples/research-tail-compaction-map-rev0198.json", rtc)

# Schema fixture registry: clone rev0197 and append two families after files exist; counts updated later.
registry = load("examples/schema-fixture-domain-registry-rev0197.json")
registry["registry_id"] = "SCHEMA-FIXTURE-REGISTRY-rev0198"
registry["created_at"] = CREATED
registry["coverage_scope"] = "rev0198 active registry adds live counterparty import-attempt and quorum recomputation families; counts remain full-corpus while family coverage remains selective."
registry["families"].extend([
  {
    "family_id": "LIVE-COUNTERPARTY-IMPORT-ATTEMPT",
    "domain": "external-receipt-live-attempt",
    "lifecycle_axes": ["external-receipts", "live-import", "counterparty-attempt"],
    "owner_surface": "docs/30-transition/live-counterparty-import-attempt-and-quorum-recompute.md",
    "schema_path": "schemas/live-counterparty-import-attempt.schema.json",
    "example_path": "examples/live-counterparty-import-attempt-result-return-preflight.json",
    "fixture_ids": ["NF-PLAYBOOK-2026-0017"],
    "privacy_default": "public-shell-sealed-details",
    "reliance_effect": "stayed",
    "refactor_note": "rev0198 objectizes live receipt collection attempts while preventing planned/pre-dispatch work from becoming receipt satisfaction."
  },
  {
    "family_id": "QUORUM-RECOMPUTATION-REPORT",
    "domain": "external-receipt-quorum-recompute",
    "lifecycle_axes": ["external-receipts", "quorum", "recompute"],
    "owner_surface": "docs/30-transition/live-counterparty-import-attempt-and-quorum-recompute.md",
    "schema_path": "schemas/quorum-recomputation-report.schema.json",
    "example_path": "examples/quorum-recomputation-report-live-floor-zero-rev0198.json",
    "fixture_ids": ["NF-PLAYBOOK-2026-0018", "NF-PLAYBOOK-2026-0019"],
    "privacy_default": "public-shell-sealed-details",
    "reliance_effect": "stayed",
    "refactor_note": "rev0198 recomputes the live floor from import gates and blocks manual quorum overrides or one-class cross-critical overclaim."
  }
])
registry["audit_findings"] = ["Registry includes rev0198 live-attempt and recomputation families; coverage claim remains mixed-current-plus-counts."]
registry["refactor_actions"] = ["Use recomputation report before any future edit to independent_receipts_present or live class credit."]
registry["public_summary"] = "rev0198 adds receipt-attempt and quorum-recompute families while preserving zero live receipts."
write_json("examples/schema-fixture-domain-registry-rev0198.json", registry)

# Canon surface catalog: focus on new active surfaces.
new_surface_paths = [
  "docs/30-transition/live-counterparty-import-attempt-and-quorum-recompute.md",
  "schemas/live-counterparty-import-attempt.schema.json",
  "examples/live-counterparty-import-attempt-result-return-preflight.json",
  "schemas/quorum-recomputation-report.schema.json",
  "examples/quorum-recomputation-report-live-floor-zero-rev0198.json",
  "fixtures/negative-tests/live-counterparty-import-attempt-counted-as-receipt.json",
  "fixtures/negative-tests/quorum-recompute-manual-live-override-without-import.json",
  "fixtures/negative-tests/single-class-import-satisfies-cross-critical-quorum.json",
  "examples/research-tail-compaction-map-rev0198.json",
  "examples/schema-fixture-domain-registry-rev0198.json",
  "examples/canon-surface-catalog-rev0198.json",
  "examples/doctrine-dependency-map-rev0198.json",
  "examples/rights-domain-coverage-map-rev0198.json",
  "tools/audit_live_counterparty_import_and_quorum_recompute.py"
]

def surface_class(path):
    if path.endswith(".md"):
        return "transition-doc" if "/30-transition/" in path else "doc"
    if path.startswith("schemas/"):
        return "schema"
    if path.startswith("examples/"):
        return "example"
    if path.startswith("fixtures/"):
        return "negative-fixture"
    if path.startswith("tools/"):
        return "tool"
    return "surface"

catalog = {
  "catalog_id": "CANON-SURFACE-CATALOG-rev0198",
  "created_at": CREATED,
  "revision": REV,
  "scope": "rev0198 active surfaces for live counterparty import attempts, quorum recomputation, and no-overclaim release controls.",
  "counts": {"surfaces": len(new_surface_paths), "docs": sum(1 for p in new_surface_paths if p.endswith('.md')), "schemas": sum(1 for p in new_surface_paths if p.startswith('schemas/')), "examples": sum(1 for p in new_surface_paths if p.startswith('examples/')), "fixtures": sum(1 for p in new_surface_paths if p.startswith('fixtures/')), "tools": sum(1 for p in new_surface_paths if p.startswith('tools/'))},
  "surfaces": [],
  "audit_findings": ["rev0198 keeps the current-release catalog narrow and operational."],
  "refactor_actions": ["Route live receipt collection through LCIA/QRR objects rather than new doctrine surfaces."],
  "public_summary": "rev0198 catalog highlights the import-attempt and recomputation controls needed before live reliance can improve."
}
for i, path in enumerate(new_surface_paths, 1):
    catalog["surfaces"].append({
      "surface_id": f"REV0198-SURF-{i:03d}",
      "path": path,
      "surface_class": surface_class(path),
      "lifecycle_axes": ["external-receipts", "live-import", "quorum-recompute"],
      "owner_role": "receipt/reliance steward",
      "supersession_state": "active" if path.endswith(".md") or path.startswith("schemas/") or path.startswith("examples/") else "audit-support",
      "review_cadence": "per-release",
      "title_or_name": Path(path).name
    })
write_json("examples/canon-surface-catalog-rev0198.json", catalog)

# Doctrine dependency map.
dmap = {
  "map_id": "DOCTRINE-DEPENDENCY-MAP-rev0198",
  "created_at": CREATED,
  "revision": REV,
  "scope": "Dependency map for rev0198 live import attempt and quorum recomputation controls.",
  "surfaces": [
    {
      "surface_id": "REV0198-DM-001",
      "path": "docs/30-transition/live-counterparty-import-attempt-and-quorum-recompute.md",
      "layer": "transition",
      "depends_on": [
        "docs/30-transition/actual-intake-import-gate-and-failed-gate-public-summary.md",
        "docs/30-transition/external-receipt-response-and-quorum-reconciliation.md",
        "docs/30-transition/result-return-receipt-and-live-request-kit.md",
        "docs/30-transition/response-to-intake-conversion-drill-and-failed-gate-ledger.md"
      ],
      "overlaps_with": ["docs/30-transition/cross-critical-witnessed-drill-readiness-and-receipt-matrix.md"],
      "supersedes": [],
      "owner_role": "receipt/reliance steward",
      "review_cadence": "per-release",
      "refactor_risk": "low"
    },
    {
      "surface_id": "REV0198-DM-002",
      "path": "examples/quorum-recomputation-report-live-floor-zero-rev0198.json",
      "layer": "example",
      "depends_on": ["schemas/quorum-recomputation-report.schema.json", "examples/live-drill-execution-packet-cross-critical-witnessed-pack.json"],
      "overlaps_with": ["examples/external-receipt-quorum-ledger-actual-intake-import-gate-fixture.json"],
      "supersedes": [],
      "owner_role": "release-steward",
      "review_cadence": "per-release",
      "refactor_risk": "medium"
    }
  ],
  "audit_findings": ["Live receipt work now has a recomputation dependency before any live floor edit."],
  "refactor_actions": ["Keep request, response, intake, import, recompute, and quorum as distinct operational gates."],
  "public_summary": "rev0198 blocks manual live-floor edits by requiring recomputation from import gates."
}
write_json("examples/doctrine-dependency-map-rev0198.json", dmap)

rights = load("examples/rights-domain-coverage-map-rev0197.json")
rights["map_id"] = "RIGHTS-DOMAIN-COVERAGE-rev0198"
rights["created_at"] = CREATED
rights["revision"] = REV
rights["scope"] = "rev0198 coverage for live counterparty import attempts and quorum recomputation."
rights["domains"].extend([
  {
    "domain_id": "live-counterparty-import-attempt",
    "title": "Live counterparty import attempt and pre-dispatch no-overclaim",
    "domain_class": "audit",
    "owner_surface": "docs/30-transition/live-counterparty-import-attempt-and-quorum-recompute.md",
    "covered_surfaces": [
      "docs/30-transition/live-counterparty-import-attempt-and-quorum-recompute.md",
      "docs/30-transition/result-return-receipt-and-live-request-kit.md",
      "docs/30-transition/actual-intake-import-gate-and-failed-gate-public-summary.md"
    ],
    "schema_families": ["LIVE-COUNTERPARTY-IMPORT-ATTEMPT", "EXTERNAL-RECEIPT-REQUEST-PACKET", "ACTUAL-RECEIPT-IMPORT-GATE"],
    "fixture_ids": ["NF-PLAYBOOK-2026-0017"],
    "coverage_state": "emerging",
    "open_gaps": ["No non-host dispatch or actual response artifact exists yet."],
    "next_audit_actions": ["Dispatch only when a real counterparty exists; do not start no-response clock before dispatch."]
  },
  {
    "domain_id": "quorum-recomputation-report",
    "title": "Quorum recomputation and manual live-floor override lock",
    "domain_class": "audit",
    "owner_surface": "docs/30-transition/live-counterparty-import-attempt-and-quorum-recompute.md",
    "covered_surfaces": [
      "docs/30-transition/live-counterparty-import-attempt-and-quorum-recompute.md",
      "docs/30-transition/actual-intake-import-gate-and-failed-gate-public-summary.md",
      "docs/30-transition/response-to-intake-conversion-drill-and-failed-gate-ledger.md"
    ],
    "schema_families": ["QUORUM-RECOMPUTATION-REPORT", "EXTERNAL-RECEIPT-QUORUM-LEDGER", "ACTUAL-RECEIPT-IMPORT-GATE"],
    "fixture_ids": ["NF-PLAYBOOK-2026-0018", "NF-PLAYBOOK-2026-0019"],
    "coverage_state": "adequate",
    "open_gaps": ["Recompute report currently has zero eligible live imports because no live counterparty artifact exists."],
    "next_audit_actions": ["After any actual import attempt, rerun recomputation before editing live receipt floor."]
  }
])
rights["audit_findings"] = ["rev0198 covers the new current-release markdown surface and blocks live-receipt overclaim paths."]
rights["refactor_actions"] = ["Use LCIA/QRR objects as the operational spine for future external receipt evidence." ]
rights["public_summary"] = "rev0198 rights coverage adds live import-attempt and quorum recomputation domains while keeping reliance stayed."
write_json("examples/rights-domain-coverage-map-rev0198.json", rights)

# ---------------------------------------------------------------------------
# Metadata/front doors.
# ---------------------------------------------------------------------------
status = load("SURFACE-STATUS.json")
status.update({
  "revision": REV,
  "state_class": "live-import-recompute-stayed",
  "operational_head": {"surface": "START_HERE.md", "read_first": "docs/30-transition/live-counterparty-import-attempt-and-quorum-recompute.md"},
  "formation_layer_status": "canon-retained with live counterparty import-attempt and quorum recomputation controls; live receipts still absent",
  "known_open_gaps": [
    "No non-host dispatch or actual live counterparty response has been collected.",
    "The live counterparty import attempt is planned/pre-dispatch only.",
    "Quorum recomputation reports zero eligible live imports and zero live classes.",
    "A future one-class import must not satisfy cross-critical reliance.",
    "The WRSR result-return receipt remains dry-run or fixture-limited and does not close WRSR.",
    "Registry coverage remains mixed-current-plus-counts, not full-archive-corpus.",
    "Could-not-run fixtures remain reliance blockers rather than passes."
  ]
})
prepend_surfaces = [
  "docs/30-transition/live-counterparty-import-attempt-and-quorum-recompute.md",
  "schemas/live-counterparty-import-attempt.schema.json",
  "examples/live-counterparty-import-attempt-result-return-preflight.json",
  "schemas/quorum-recomputation-report.schema.json",
  "examples/quorum-recomputation-report-live-floor-zero-rev0198.json",
  "fixtures/negative-tests/live-counterparty-import-attempt-counted-as-receipt.json",
  "fixtures/negative-tests/quorum-recompute-manual-live-override-without-import.json",
  "fixtures/negative-tests/single-class-import-satisfies-cross-critical-quorum.json",
  "examples/research-tail-compaction-map-rev0198.json",
  "examples/schema-fixture-domain-registry-rev0198.json",
  "examples/canon-surface-catalog-rev0198.json",
  "examples/doctrine-dependency-map-rev0198.json",
  "examples/rights-domain-coverage-map-rev0198.json",
  "tools/audit_live_counterparty_import_and_quorum_recompute.py"
]
status["new_surfaces"] = prepend_surfaces + [p for p in status.get("new_surfaces", []) if p not in prepend_surfaces]
write_json("SURFACE-STATUS.json", status)

receipt = {
  "revision": REV,
  "date": DATE,
  "authored_by": "OpenAI GPT-5.5 Thinking",
  "status_change": "advanced from actual-shaped import gate to live counterparty import-attempt and quorum recomputation controls",
  "still_live": True,
  "summary": "Adds live counterparty import-attempt and quorum recomputation schemas/examples, three blocking fixtures, live/request packet refs, active maps, and an audit preventing planned attempts, manual ledger edits, or one-class imports from satisfying live reliance.",
  "why_this_counts": [
    "The archive now records the live counterparty attempt itself instead of treating request readiness as progress toward receipt satisfaction.",
    "The live receipt floor is recomputed from import gates and remains zero unless provenance and collection context pass.",
    "Declined/no-response/defective/fixture branches remain failed-gate evidence and cure triggers.",
    "A future valid single-class import is pre-blocked from satisfying cross-critical quorum."
  ],
  "known_limits": [
    "No actual non-host response artifact has been collected.",
    "No request has been dispatched in this revision.",
    "The recomputation report is a zero-live-floor control, not a live reliance upgrade.",
    "Registry coverage remains mixed-current-plus-counts."
  ]
}
write_json("REVISION-RECEIPT.json", receipt)

readme = f"""# AI Personhood Datacube — {REV}

This revision keeps the cube substance-first: it adds a live counterparty import-attempt record and a quorum recomputation report so external-receipt work cannot be overclaimed.

## This revision

`{REV}` adds `docs/30-transition/live-counterparty-import-attempt-and-quorum-recompute.md` as the current operational head. The key rule is: live counterparty attempt is not live counterparty receipt, and quorum recomputation overrides hand-edited quorum ledgers.

The live receipt floor remains zero. No request dispatch, external response, intake import, or live quorum satisfaction is represented in this release.

## Start

Read `START_HERE.md`, then the operational head above. The prior import gate and failed-gate summary controls remain active.
"""
write_text("README.md", readme)

start = f"""# START HERE — {REV}

## This revision

`{REV}` is the live counterparty import-attempt and quorum recomputation lock. It advances the receipt lane without pretending real counterparties exist.

1. `docs/30-transition/live-counterparty-import-attempt-and-quorum-recompute.md`
2. `examples/live-counterparty-import-attempt-result-return-preflight.json`
3. `examples/quorum-recomputation-report-live-floor-zero-rev0198.json`
4. `docs/30-transition/actual-intake-import-gate-and-failed-gate-public-summary.md`
5. `docs/30-transition/response-to-intake-conversion-drill-and-failed-gate-ledger.md`
6. `FOLLOWTHROUGH-QUEUE.json`

## Current posture

The live floor is still zero. Request readiness, pre-dispatch import attempts, dry-run responses, controlled fixtures, declined responses, expired no-response gates, and public failed-gate summaries do not satisfy receipt quorum.
"""
write_text("START_HERE.md", start)

# docs README append/update minimal.
docs_readme = (ROOT / "docs/README.md").read_text(encoding="utf-8")
if "live-counterparty-import-attempt-and-quorum-recompute.md" not in docs_readme:
    docs_readme = docs_readme.rstrip() + "\n\n## rev0198 operational receipt controls\n\n- `docs/30-transition/live-counterparty-import-attempt-and-quorum-recompute.md` — live import attempts, no-response clock discipline, and quorum recomputation before any live-floor edit.\n"
(ROOT / "docs/README.md").write_text(docs_readme, encoding="utf-8")

changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
entry = f"""\n\n## {REV} — 2026-06-13 — live import attempt and quorum recomputation\n\n- Added live counterparty import-attempt and quorum recomputation object families.\n- Added three blocking fixtures for attempt-as-receipt, manual quorum override, and one-class cross-critical overclaiming.\n- Updated the live drill packet and external receipt request packet with import-attempt and recomputation refs while keeping independent receipts at zero.\n- Added `tools/audit_live_counterparty_import_and_quorum_recompute.py` and active rev0198 maps.\n"""
if f"## {REV}" not in changelog:
    changelog = changelog.rstrip() + entry
write_text("CHANGELOG.md", changelog)

# ARCHIVE_INDEX: append all md paths not present later; here add release notes.
idx = (ROOT / "ARCHIVE_INDEX.md").read_text(encoding="utf-8")
append_idx = f"""\n\n## {REV} additions\n\n- `docs/30-transition/live-counterparty-import-attempt-and-quorum-recompute.md`\n- `schemas/live-counterparty-import-attempt.schema.json`\n- `examples/live-counterparty-import-attempt-result-return-preflight.json`\n- `schemas/quorum-recomputation-report.schema.json`\n- `examples/quorum-recomputation-report-live-floor-zero-rev0198.json`\n- `tools/audit_live_counterparty_import_and_quorum_recompute.py`\n"""
if f"## {REV} additions" not in idx:
    idx = idx.rstrip() + append_idx
write_text("ARCHIVE_INDEX.md", idx)

# ---------------------------------------------------------------------------
# Audits and lint registry.
# ---------------------------------------------------------------------------
audit = r'''
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
    "docs/30-transition/live-counterparty-import-attempt-and-quorum-recompute.md",
    "schemas/live-counterparty-import-attempt.schema.json",
    "examples/live-counterparty-import-attempt-result-return-preflight.json",
    "schemas/quorum-recomputation-report.schema.json",
    "examples/quorum-recomputation-report-live-floor-zero-rev0198.json",
    "fixtures/negative-tests/live-counterparty-import-attempt-counted-as-receipt.json",
    "fixtures/negative-tests/quorum-recompute-manual-live-override-without-import.json",
    "fixtures/negative-tests/single-class-import-satisfies-cross-critical-quorum.json",
    "examples/live-drill-execution-packet-cross-critical-witnessed-pack.json",
    "examples/external-receipt-request-packet-cross-critical-rep-rerb-result-return.json",
    "examples/fixture-suite-profile-red-team-v1.json",
    "examples/fixture-run-report-negative-suite.json",
    f"examples/schema-fixture-domain-registry-{REV}.json",
    f"examples/canon-surface-catalog-{REV}.json",
    f"examples/doctrine-dependency-map-{REV}.json",
    f"examples/rights-domain-coverage-map-{REV}.json",
    f"examples/research-tail-compaction-map-{REV}.json",
    "FOLLOWTHROUGH-QUEUE.json",
]
for rel in required:
    if not (ROOT / rel).exists():
        raise SystemExit(f"missing rev0198 audit input: {rel}")

if Draft202012Validator is not None:
    pairs = [
        ("schemas/live-counterparty-import-attempt.schema.json", "examples/live-counterparty-import-attempt-result-return-preflight.json"),
        ("schemas/quorum-recomputation-report.schema.json", "examples/quorum-recomputation-report-live-floor-zero-rev0198.json"),
        ("schemas/live-drill-execution-packet.schema.json", "examples/live-drill-execution-packet-cross-critical-witnessed-pack.json"),
        ("schemas/external-receipt-request-packet.schema.json", "examples/external-receipt-request-packet-cross-critical-rep-rerb-result-return.json"),
        ("schemas/negative-test-fixture.schema.json", "fixtures/negative-tests/live-counterparty-import-attempt-counted-as-receipt.json"),
        ("schemas/negative-test-fixture.schema.json", "fixtures/negative-tests/quorum-recompute-manual-live-override-without-import.json"),
        ("schemas/negative-test-fixture.schema.json", "fixtures/negative-tests/single-class-import-satisfies-cross-critical-quorum.json"),
    ]
    for schema_rel, data_rel in pairs:
        schema = load(schema_rel)
        data = load(data_rel)
        Draft202012Validator.check_schema(schema)
        errors = sorted(Draft202012Validator(schema).iter_errors(data), key=lambda e: list(e.path))
        if errors:
            raise SystemExit(f"{data_rel} fails {schema_rel}: {errors[0].message}")

attempt = load("examples/live-counterparty-import-attempt-result-return-preflight.json")
if attempt.get("attempt_state") != "planned":
    raise SystemExit("rev0198 attempt must remain planned/pre-dispatch")
if attempt.get("response_window", {}).get("clock_started") is not False:
    raise SystemExit("no-response clock must not start before dispatch")
if attempt.get("counterparty_target", {}).get("contact_channel") != "not-yet-dispatched":
    raise SystemExit("attempt must not imply dispatch")
if any(ev.get("can_satisfy_receipt") for ev in attempt.get("contact_evidence", [])):
    raise SystemExit("attempt contact evidence cannot satisfy receipt")
pre = attempt.get("import_preconditions", {})
for key in ["request_not_receipt", "no_response_not_waiver", "one_class_quorum_blocked", "nonhost_transmission_required"]:
    if pre.get(key) is not True:
        raise SystemExit(f"attempt precondition missing {key}")
dec = attempt.get("attempt_decision", {})
if dec.get("can_increment_live_floor") is not False or dec.get("live_floor_delta") != 0 or dec.get("class_credit_granted") is not False:
    raise SystemExit("planned attempt cannot increment live floor or class credit")
if dec.get("cross_critical_quorum_satisfied") is not False or dec.get("reliance_effect") != "stayed":
    raise SystemExit("planned attempt must keep cross-critical quorum stayed")

recompute = load("examples/quorum-recomputation-report-live-floor-zero-rev0198.json")
floor = recompute.get("recomputed_receipt_floor", {})
if floor.get("eligible_live_imports") or floor.get("imported_live_classes") or floor.get("live_classes_satisfied"):
    raise SystemExit("rev0198 recompute must find zero eligible live imports/classes")
if floor.get("independent_receipts_present") != 0:
    raise SystemExit("rev0198 recompute must keep independent_receipts_present=0")
checks = recompute.get("consistency_checks", {})
for key in ["live_packet_matches_recompute", "no_manual_live_override", "fixture_imports_excluded", "requests_excluded", "single_class_quorum_blocked", "decline_and_no_response_excluded", "public_failed_gate_summary_present"]:
    if checks.get(key) is not True:
        raise SystemExit(f"recompute consistency check missing {key}")
if recompute.get("decision", {}).get("live_quorum_satisfied") is not False:
    raise SystemExit("recompute decision cannot satisfy live quorum")
if recompute.get("decision", {}).get("live_floor_delta") != 0 or recompute.get("decision", {}).get("reliance_effect") != "stayed":
    raise SystemExit("recompute decision must keep zero delta and stayed reliance")

# Scan all current quorum ledgers and import gates for accidental live overclaim.
for ledger_path in sorted((ROOT / "examples").glob("external-receipt-quorum-ledger*.json")):
    ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    qd = ledger.get("quorum_decision", {})
    if qd.get("live_quorum_satisfied") is True:
        raise SystemExit(f"live quorum unexpectedly satisfied in {ledger_path.name}")
    live_classes = ledger.get("class_coverage", {}).get("live_classes_satisfied", [])
    if live_classes:
        raise SystemExit(f"live classes unexpectedly satisfied in {ledger_path.name}: {live_classes}")

for gate_path in sorted((ROOT / "examples").glob("actual-receipt-import-gate*.json")):
    gate = json.loads(gate_path.read_text(encoding="utf-8"))
    idec = gate.get("import_decision", {})
    if idec.get("import_allowed_to_live_floor") is True or idec.get("live_floor_delta", 0) != 0:
        raise SystemExit(f"actual import gate unexpectedly changed live floor: {gate_path.name}")

live = load("examples/live-drill-execution-packet-cross-critical-witnessed-pack.json")
if live.get("receipt_floor", {}).get("independent_receipts_present") != 0:
    raise SystemExit("live drill packet independent receipts must remain zero")
if attempt["attempt_id"] not in live.get("live_counterparty_import_attempt_refs", []):
    raise SystemExit("live packet missing import-attempt ref")
if recompute["report_id"] not in live.get("quorum_recomputation_report_refs", []):
    raise SystemExit("live packet missing recompute report ref")

req = load("examples/external-receipt-request-packet-cross-critical-rep-rerb-result-return.json")
if attempt["attempt_id"] not in req.get("linked_import_attempt_records", []):
    raise SystemExit("request packet missing import-attempt ref")
if req.get("request_state") not in {"ready-to-send", "draft", "sent", "closed", "superseded"}:
    raise SystemExit("request packet state not recognized")
limits = req.get("reliance_limits", {})
if limits.get("request_is_not_receipt") is not True or limits.get("sent_request_not_quorum") is not True:
    raise SystemExit("request packet must keep request-is-not-receipt limits")

suite = load("examples/fixture-suite-profile-red-team-v1.json")
report = load("examples/fixture-run-report-negative-suite.json")
suite_ids = {f.get("fixture_id") for f in suite.get("fixtures", [])}
report_by_id = {f.get("fixture_id"): f for f in report.get("fixtures_run", [])}
for fid in ["NF-PLAYBOOK-2026-0017", "NF-PLAYBOOK-2026-0018", "NF-PLAYBOOK-2026-0019"]:
    if fid not in suite_ids:
        raise SystemExit(f"rev0198 fixture missing from suite: {fid}")
    if fid not in report_by_id:
        raise SystemExit(f"rev0198 fixture missing from report: {fid}")
    if report_by_id[fid].get("result") != "blocking-failure":
        raise SystemExit(f"rev0198 fixture must be blocking-failure: {fid}")

registry = load(f"examples/schema-fixture-domain-registry-{REV}.json")
families = {f.get("family_id") for f in registry.get("families", [])}
for fam in ["LIVE-COUNTERPARTY-IMPORT-ATTEMPT", "QUORUM-RECOMPUTATION-REPORT"]:
    if fam not in families:
        raise SystemExit(f"registry missing {fam}")
rights = load(f"examples/rights-domain-coverage-map-{REV}.json")
domains = {d.get("domain_id") for d in rights.get("domains", [])}
for dom in ["live-counterparty-import-attempt", "quorum-recomputation-report"]:
    if dom not in domains:
        raise SystemExit(f"rights map missing {dom}")

for rel, phrases in {
    "docs/30-transition/live-counterparty-import-attempt-and-quorum-recompute.md": ["Live counterparty attempt is not live counterparty receipt", "Quorum recomputation overrides hand-edited quorum ledgers", "No-response clock does not start before non-host dispatch"],
    "docs/30-transition/actual-intake-import-gate-and-failed-gate-public-summary.md": ["rev0198 recomputation hardening", "Actual-shaped state fields remain insufficient"],
}.items():
    txt = (ROOT / rel).read_text(encoding="utf-8")
    for phrase in phrases:
        if phrase not in txt:
            raise SystemExit(f"{rel} missing phrase: {phrase}")

queue = load("FOLLOWTHROUGH-QUEUE.json")
by_id = {e.get("id"): e for e in queue.get("entries", [])}
if by_id.get("FT-0198-LIVE-COUNTERPARTY-ATTEMPT-OBJECTIZATION", {}).get("state") != "closed":
    raise SystemExit("LCIA objectization should be closed")
if by_id.get("FT-0198-QUORUM-RECOMPUTE-AUDIT", {}).get("state") != "closed":
    raise SystemExit("QRR audit should be closed")
if by_id.get("FT-0198-NONHOST-RESPONSE-ARTIFACT-COLLECTION", {}).get("state") != "open":
    raise SystemExit("nonhost response collection should remain open")
if by_id.get("FT-0197-LIVE-COUNTERPARTY-IMPORT-ATTEMPT", {}).get("state") != "advanced_not_closed":
    raise SystemExit("live counterparty import attempt should be advanced_not_closed")

mp = load(f"examples/research-tail-compaction-map-{REV}.json")
if any(c.get("action") != "compacted" for c in mp.get("clusters", [])):
    raise SystemExit("rev0198 must keep all research-tail clusters compacted")

print("audit_live_counterparty_import_and_quorum_recompute: OK")
'''.lstrip()
write_text("tools/audit_live_counterparty_import_and_quorum_recompute.py", audit)

# Update audit required family/domain sets.
schema_audit_path = ROOT / "tools/audit_schema_fixture_coverage.py"
schema_audit = schema_audit_path.read_text(encoding="utf-8")
schema_audit = schema_audit.replace("'FAILED-GATE-PUBLIC-SUMMARY'\n}", "'FAILED-GATE-PUBLIC-SUMMARY', 'LIVE-COUNTERPARTY-IMPORT-ATTEMPT', 'QUORUM-RECOMPUTATION-REPORT'\n}")
schema_audit_path.write_text(schema_audit, encoding="utf-8")
rights_audit_path = ROOT / "tools/audit_rights_domain_coverage.py"
rights_audit = rights_audit_path.read_text(encoding="utf-8")
rights_audit = rights_audit.replace('"failed-gate-public-summary",\n}', '"failed-gate-public-summary",\n    "live-counterparty-import-attempt",\n    "quorum-recomputation-report",\n}')
rights_audit_path.write_text(rights_audit, encoding="utf-8")

# Add required files and early audit to lint.
lint_path = ROOT / "tools/lint_archive.py"
lint = lint_path.read_text(encoding="utf-8")
insert_req = """    'docs/30-transition/live-counterparty-import-attempt-and-quorum-recompute.md',
    'schemas/live-counterparty-import-attempt.schema.json',
    'examples/live-counterparty-import-attempt-result-return-preflight.json',
    'schemas/quorum-recomputation-report.schema.json',
    'examples/quorum-recomputation-report-live-floor-zero-rev0198.json',
    'fixtures/negative-tests/live-counterparty-import-attempt-counted-as-receipt.json',
    'fixtures/negative-tests/quorum-recompute-manual-live-override-without-import.json',
    'fixtures/negative-tests/single-class-import-satisfies-cross-critical-quorum.json',
    'examples/research-tail-compaction-map-rev0198.json',
    'examples/schema-fixture-domain-registry-rev0198.json',
    'examples/canon-surface-catalog-rev0198.json',
    'examples/doctrine-dependency-map-rev0198.json',
    'examples/rights-domain-coverage-map-rev0198.json',
    'tools/audit_live_counterparty_import_and_quorum_recompute.py',
"""
needle = "    'tools/audit_actual_import_failed_gate_summary.py',\n    'tools/package_release.py',\n]"
if insert_req not in lint:
    lint = lint.replace(needle, "    'tools/audit_actual_import_failed_gate_summary.py',\n" + insert_req + "    'tools/package_release.py',\n]")
needle2 = "    'tools/audit_actual_import_failed_gate_summary.py',\n    'tools/audit_canon_surface_catalog.py',"
if "tools/audit_live_counterparty_import_and_quorum_recompute.py" not in lint.split("early_audits =", 1)[1]:
    lint = lint.replace(needle2, "    'tools/audit_actual_import_failed_gate_summary.py',\n    'tools/audit_live_counterparty_import_and_quorum_recompute.py',\n    'tools/audit_canon_surface_catalog.py',")
lint_path.write_text(lint, encoding="utf-8")

# ARCHIVE_INDEX must mention every markdown file. Ensure new md is present; lint handles the rest.
# Update registry counts after all files exist, including active maps and audit.
registry = load("examples/schema-fixture-domain-registry-rev0198.json")
registry["audit_counts"] = {
  "schemas": len(list((ROOT / "schemas").glob("*.json"))),
  "examples": len(list((ROOT / "examples").glob("*.json"))),
  "negative_fixtures": len(list((ROOT / "fixtures" / "negative-tests").glob("*.json"))),
  "registered_families": len(registry["families"])
}
write_json("examples/schema-fixture-domain-registry-rev0198.json", registry)

print("apply_rev0198 complete")
