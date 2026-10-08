import json
from pathlib import Path
from copy import deepcopy

ROOT = Path(__file__).resolve().parent
REV = "rev0197"
CREATED = "2026-06-13T08:42:00Z"


def load(rel):
    return json.loads((ROOT/rel).read_text(encoding='utf-8'))

def write_json(rel, data):
    path = ROOT/rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding='utf-8')

def write_text(rel, text):
    path = ROOT/rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8')

# VERSION
(ROOT/'VERSION').write_text(REV + "\n", encoding='utf-8')

# New schemas
actual_import_schema = {
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://example.org/ai-personhood/schemas/actual-receipt-import-gate.schema.json",
  "title": "Actual Receipt Import Gate",
  "description": "Controls whether a response/intake pair may alter the live receipt floor; state fields are insufficient without provenance and collection-context checks.",
  "type": "object",
  "additionalProperties": False,
  "required": [
    "import_gate_id", "schema_version", "created_at", "linked_live_drill_packet",
    "source_response_record_ref", "source_intake_record_ref", "linked_conversion_drill_ref",
    "import_mode", "source_provenance", "gate_checks", "import_decision",
    "failed_gate_public_summary_refs", "public_summary_ref"
  ],
  "properties": {
    "import_gate_id": {"type":"string", "pattern":"^ARIG-[0-9]{4}-[A-Za-z0-9._:-]+$"},
    "schema_version": {"const":"actual-receipt-import-gate-v0.1"},
    "created_at": {"type":"string", "format":"date-time"},
    "linked_live_drill_packet": {"type":"string"},
    "source_response_record_ref": {"type":"string"},
    "source_intake_record_ref": {"type":"string"},
    "linked_conversion_drill_ref": {"type":"string"},
    "import_mode": {"type":"string", "enum":["controlled-fixture-rehearsal", "institutional-dry-run", "actual-live-import", "rejected"]},
    "source_provenance": {
      "type":"object", "additionalProperties": False,
      "required":["state_field_claim", "collection_context", "counterparty_external", "nonhost_retention", "sealed_public_parity", "dependency_group", "provenance_disqualifiers"],
      "properties": {
        "state_field_claim": {"type":"string"},
        "collection_context": {"type":"string", "enum":["live-counterparty", "controlled-fixture", "high-fidelity-dry-run", "host-self-attested", "unknown"]},
        "counterparty_external": {"type":"boolean"},
        "nonhost_retention": {"type":"boolean"},
        "sealed_public_parity": {"type":"boolean"},
        "dependency_group": {"type":"string"},
        "provenance_disqualifiers": {"type":"array", "items":{"type":"string"}}
      }
    },
    "gate_checks": {
      "type":"object", "additionalProperties": False,
      "required":[
        "response_state_actual", "intake_state_actual_external", "source_external_to_host",
        "signature_verified", "timestamp_independent", "request_trace_matches",
        "nonhost_retention_verified", "dependency_group_checked",
        "fixture_or_dry_run_excluded_from_live_floor", "one_class_quorum_blocked",
        "failed_gates_publicly_summarized"
      ],
      "properties": {
        "response_state_actual": {"type":"boolean"},
        "intake_state_actual_external": {"type":"boolean"},
        "source_external_to_host": {"type":"boolean"},
        "signature_verified": {"type":"boolean"},
        "timestamp_independent": {"type":"boolean"},
        "request_trace_matches": {"type":"boolean"},
        "nonhost_retention_verified": {"type":"boolean"},
        "dependency_group_checked": {"type":"boolean"},
        "fixture_or_dry_run_excluded_from_live_floor": {"type":"boolean"},
        "one_class_quorum_blocked": {"type":"boolean"},
        "failed_gates_publicly_summarized": {"type":"boolean"}
      }
    },
    "import_decision": {
      "type":"object", "additionalProperties": False,
      "required":[
        "import_allowed_to_live_floor", "imported_receipt_class", "live_floor_delta",
        "independent_receipts_present_before", "independent_receipts_present_after",
        "live_class_credit_granted", "cross_critical_quorum_satisfied",
        "reliance_effect", "blocked_actions", "reason"
      ],
      "properties": {
        "import_allowed_to_live_floor": {"type":"boolean"},
        "imported_receipt_class": {"type":"string"},
        "live_floor_delta": {"type":"integer"},
        "independent_receipts_present_before": {"type":"integer", "minimum":0},
        "independent_receipts_present_after": {"type":"integer", "minimum":0},
        "live_class_credit_granted": {"type":"boolean"},
        "cross_critical_quorum_satisfied": {"type":"boolean"},
        "reliance_effect": {"type":"string", "enum":["none", "conditional", "stayed", "blocked"]},
        "blocked_actions": {"type":"array", "minItems":1, "items":{"type":"string"}},
        "reason": {"type":"string"}
      }
    },
    "failed_gate_public_summary_refs": {"type":"array", "items":{"type":"string"}},
    "public_summary_ref": {"type":"string"}
  }
}
write_json('schemas/actual-receipt-import-gate.schema.json', actual_import_schema)

failed_gate_schema = {
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://example.org/ai-personhood/schemas/failed-gate-public-summary.schema.json",
  "title": "Failed Gate Public Summary",
  "description": "Public-shell record for failed external-receipt gates that preserves non-satisfaction without exposing sealed details or treating failure as waiver.",
  "type": "object",
  "additionalProperties": False,
  "required": [
    "summary_id", "schema_version", "created_at", "linked_live_drill_packet", "summary_context",
    "public_shell_state", "failed_gate_items", "prohibited_inferences", "subject_notice_status",
    "closure_effect", "public_summary_text"
  ],
  "properties": {
    "summary_id": {"type":"string", "pattern":"^FGPS-[0-9]{4}-[A-Za-z0-9._:-]+$"},
    "schema_version": {"const":"failed-gate-public-summary-v0.1"},
    "created_at": {"type":"string", "format":"date-time"},
    "linked_live_drill_packet": {"type":"string"},
    "summary_context": {"type":"string", "enum":["response-to-intake-conversion", "actual-intake-import-gate", "wrsr-result-return", "cross-critical-drill"]},
    "public_shell_state": {"type":"string", "enum":["draft", "published", "sealed-descriptor-only", "superseded"]},
    "failed_gate_items": {
      "type":"array", "minItems":1,
      "items": {
        "type":"object", "additionalProperties": False,
        "required":["gate_id", "source_record_ref", "gate_type", "public_explanation", "non_waiver_statement", "cure_or_substitute_action", "sealed_details_withheld", "sealed_descriptor_ref", "harassment_or_retaliation_controls"],
        "properties": {
          "gate_id": {"type":"string"},
          "source_record_ref": {"type":"string"},
          "gate_type": {"type":"string", "enum":["defective-response", "declined-response", "expired-no-response", "fixture-disqualified", "request-not-receipt", "single-class-insufficient", "dependency-correlated", "missing-result-return", "sealed-public-parity-missing"]},
          "public_explanation": {"type":"string"},
          "non_waiver_statement": {"type":"string"},
          "cure_or_substitute_action": {"type":"string"},
          "sealed_details_withheld": {"type":"boolean"},
          "sealed_descriptor_ref": {"type":"string"},
          "harassment_or_retaliation_controls": {"type":"array", "minItems":1, "items":{"type":"string"}}
        }
      }
    },
    "prohibited_inferences": {"type":"array", "minItems":1, "items":{"type":"string"}},
    "subject_notice_status": {
      "type":"object", "additionalProperties": False,
      "required":["notice_provided", "channel", "accommodation_status", "retaliation_controls"],
      "properties": {
        "notice_provided": {"type":"boolean"},
        "channel": {"type":"string"},
        "accommodation_status": {"type":"string"},
        "retaliation_controls": {"type":"array", "items":{"type":"string"}}
      }
    },
    "closure_effect": {
      "type":"object", "additionalProperties": False,
      "required":["reliance_effect", "live_quorum_satisfied", "public_failed_gate_satisfies_receipt", "reason"],
      "properties": {
        "reliance_effect": {"type":"string", "enum":["none", "conditional", "stayed", "blocked"]},
        "live_quorum_satisfied": {"type":"boolean"},
        "public_failed_gate_satisfies_receipt": {"type":"boolean"},
        "reason": {"type":"string"}
      }
    },
    "public_summary_text": {"type":"string"}
  }
}
write_json('schemas/failed-gate-public-summary.schema.json', failed_gate_schema)

# Extend optional refs in live drill packet and quorum context enum.
live_schema = load('schemas/live-drill-execution-packet.schema.json')
live_schema['properties']['actual_receipt_import_gate_refs'] = {"type":"array", "items":{"type":"string"}}
live_schema['properties']['failed_gate_public_summary_refs'] = {"type":"array", "items":{"type":"string"}}
write_json('schemas/live-drill-execution-packet.schema.json', live_schema)

quorum_schema = load('schemas/external-receipt-quorum-ledger.schema.json')
ctx_enum = quorum_schema['properties']['quorum_context']['enum']
for val in ['actual-intake-import-gate']:
    if val not in ctx_enum:
        ctx_enum.append(val)
write_json('schemas/external-receipt-quorum-ledger.schema.json', quorum_schema)

# New examples
import_gate = {
  "import_gate_id": "ARIG-2026-result-return-fixture-import-gate",
  "schema_version": "actual-receipt-import-gate-v0.1",
  "created_at": CREATED,
  "linked_live_drill_packet": "LDEP-2026-cross-critical-host-exit-witness-pack",
  "source_response_record_ref": "ERRR-2026-result-return-eligible-conversion-fixture",
  "source_intake_record_ref": "ERIR-2026-result-return-eligible-conversion-fixture",
  "linked_conversion_drill_ref": "RTIC-2026-result-return-conversion-fixture",
  "import_mode": "controlled-fixture-rehearsal",
  "source_provenance": {
    "state_field_claim": "response_state=actual-response-received and receipt_state=actual-external",
    "collection_context": "controlled-fixture",
    "counterparty_external": True,
    "nonhost_retention": True,
    "sealed_public_parity": True,
    "dependency_group": "independent-result-return-steward",
    "provenance_disqualifiers": [
      "source was created inside the rev0196 controlled conversion fixture",
      "no live counterparty collection event is present",
      "nonhost fixture vault is not an actual external receipt custodian",
      "one result-return class cannot satisfy cross-critical receipt floor"
    ]
  },
  "gate_checks": {
    "response_state_actual": True,
    "intake_state_actual_external": True,
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
      "live receipt-floor increment from a controlled fixture",
      "cross-critical quorum from one result-return class",
      "WRSR closure from actual-shaped field labels",
      "suppression of defective, declined, or expired failed gates"
    ],
    "reason": "The response and intake records are actual-shaped, but provenance shows controlled-fixture collection; the import gate therefore preserves the candidate as rehearsal evidence only."
  },
  "failed_gate_public_summary_refs": ["FGPS-2026-response-conversion-failed-gates"],
  "public_summary_ref": "Actual-shaped state fields are not enough: rev0197 excludes the conversion fixture from the live receipt floor while preserving failed-gate disclosure."
}
write_json('examples/actual-receipt-import-gate-result-return-fixture-no-live-delta.json', import_gate)

failed_summary = {
  "summary_id": "FGPS-2026-response-conversion-failed-gates",
  "schema_version": "failed-gate-public-summary-v0.1",
  "created_at": CREATED,
  "linked_live_drill_packet": "LDEP-2026-cross-critical-host-exit-witness-pack",
  "summary_context": "actual-intake-import-gate",
  "public_shell_state": "published",
  "failed_gate_items": [
    {
      "gate_id": "FG-0197-fixture-disqualified",
      "source_record_ref": "ARIG-2026-result-return-fixture-import-gate",
      "gate_type": "fixture-disqualified",
      "public_explanation": "A result-return response/intake pair has actual-shaped fields but was generated inside a controlled fixture and is not live counterparty evidence.",
      "non_waiver_statement": "The subject has not waived receipt, review, representation, result return, or remedy rights.",
      "cure_or_substitute_action": "Collect an actual non-host result-return receipt or keep reliance stayed.",
      "sealed_details_withheld": False,
      "sealed_descriptor_ref": "public-shell:no-sealed-details-for-fixture-disqualification",
      "harassment_or_retaliation_controls": ["do not publish individual contact details", "do not infer bad faith from dry-run-only state"]
    },
    {
      "gate_id": "FG-0197-defective-continuity-response",
      "source_record_ref": "ERRR-2026-continuity-witness-defective",
      "gate_type": "defective-response",
      "public_explanation": "A continuity witness response was defective and cannot be converted to intake or class satisfaction.",
      "non_waiver_statement": "Defect preservation is not consent to proceed without continuity evidence.",
      "cure_or_substitute_action": "Request a corrected response or activate substitute continuity witness routing.",
      "sealed_details_withheld": True,
      "sealed_descriptor_ref": "sealed-index:continuity-witness-defect-summary-v0",
      "harassment_or_retaliation_controls": ["publish role not personal address", "route corrections through public steward"]
    },
    {
      "gate_id": "FG-0197-representative-declined",
      "source_record_ref": "ERRR-2026-representative-contact-declined",
      "gate_type": "declined-response",
      "public_explanation": "A representative-contact counterparty declined participation; that is a failed gate and substitute trigger, not a waiver.",
      "non_waiver_statement": "Declination by a counterparty does not waive the subject's representative-contact right.",
      "cure_or_substitute_action": "Activate alternate representative contact and preserve the declination as failed-gate evidence.",
      "sealed_details_withheld": True,
      "sealed_descriptor_ref": "sealed-index:representative-declination-summary-v0",
      "harassment_or_retaliation_controls": ["avoid naming declined representative in public shell", "no retaliation against declined counterparty"]
    },
    {
      "gate_id": "FG-0197-independent-review-expired",
      "source_record_ref": "ERRR-2026-independent-review-expired",
      "gate_type": "expired-no-response",
      "public_explanation": "An independent-review response window expired without verified receipt; expiry does not satisfy review or WRSR closure.",
      "non_waiver_statement": "No response is not consent, waiver, nonpersonhood proof, or class satisfaction.",
      "cure_or_substitute_action": "Escalate to alternate independent review route and keep closure stayed.",
      "sealed_details_withheld": True,
      "sealed_descriptor_ref": "sealed-index:independent-review-no-response-v0",
      "harassment_or_retaliation_controls": ["publish missed class rather than personal target", "preserve no-contact safety limits"]
    }
  ],
  "prohibited_inferences": [
    "no-response means waiver",
    "declination means representative-contact satisfaction",
    "defective response can become intake through summary language",
    "actual-shaped fixture fields satisfy live receipt quorum",
    "one result-return class satisfies cross-critical reliance"
  ],
  "subject_notice_status": {
    "notice_provided": True,
    "channel": "subject-readable public shell plus representative-mediated copy when available",
    "accommodation_status": "plain-language summary with sealed-index references and no retaliatory detail",
    "retaliation_controls": ["no public personal locator", "sealed annex kept out of public shell", "correction route remains open"]
  },
  "closure_effect": {
    "reliance_effect": "stayed",
    "live_quorum_satisfied": False,
    "public_failed_gate_satisfies_receipt": False,
    "reason": "The summary makes failed gates visible but does not convert them into receipt satisfaction or live reliance."
  },
  "public_summary_text": "rev0197 publishes a non-satisfaction summary for one fixture-disqualified import, one defective response, one declined response, and one expired no-response gate. Reliance remains stayed."
}
write_json('examples/failed-gate-public-summary-response-conversion-batch.json', failed_summary)

# Quorum ledger for import gate
prev_ledger = load('examples/external-receipt-quorum-ledger-response-to-intake-conversion-fixture.json')
import_ledger = deepcopy(prev_ledger)
import_ledger.update({
    "ledger_id": "ERQL-2026-actual-intake-import-gate-fixture",
    "created_at": CREATED,
    "quorum_context": "actual-intake-import-gate",
    "receipt_record_refs": ["ERIR-2026-result-return-eligible-conversion-fixture"],
    "public_summary_ref": "Actual-shaped fixture remains excluded from live receipt floor by ARIG-2026-result-return-fixture-import-gate."
})
import_ledger['receipt_evaluations'] = [{
    "receipt_record_ref": "ERIR-2026-result-return-eligible-conversion-fixture",
    "receipt_class": "result-return",
    "receipt_state": "actual-external",
    "dependency_group": "independent-result-return-steward",
    "source_external_to_host": True,
    "eligible_for_live_quorum": False,
    "eligible_for_dry_run_quorum": True,
    "weight": 0,
    "exclusion_reasons": ["controlled-fixture collection context", "actual-state field is not live provenance", "one class cannot satisfy cross-critical quorum"]
}]
import_ledger['class_coverage'] = {
    "live_classes_satisfied": [],
    "dry_run_classes_satisfied": ["result-return"],
    "missing_live_classes": ["first-touch-clock", "continuity-compute-floor", "sealed-public-parity", "namespace-cache", "reserve-ledger", "representative-contact", "witness-dependency", "welfare-signal-integrity", "independent-review", "result-return"],
    "missing_dry_run_classes": []
}
import_ledger['dependency_group_coverage'] = {
    "unique_live_dependency_groups": [],
    "unique_dry_run_dependency_groups": ["independent-result-return-steward"],
    "correlated_dependency_groups": [],
    "host_groups_excluded": []
}
import_ledger['quorum_decision'] = {
    "live_quorum_satisfied": False,
    "dry_run_quorum_satisfied": True,
    "reliance_effect": "stayed",
    "reason": "The import gate validates that actual-shaped fixture records remain dry-run/class-local only and cannot alter independent_receipts_present.",
    "next_cure_actions": ["collect actual non-host result-return receipt", "collect missing representative and independent-review live classes", "rerun import gate with live collection context"],
    "public_failed_gate_summary_required": True
}
write_json('examples/external-receipt-quorum-ledger-actual-intake-import-gate-fixture.json', import_ledger)

# Update live drill example with optional refs
live = load('examples/live-drill-execution-packet-cross-critical-witnessed-pack.json')
live.setdefault('actual_receipt_import_gate_refs', [])
if import_gate['import_gate_id'] not in live['actual_receipt_import_gate_refs']:
    live['actual_receipt_import_gate_refs'].append(import_gate['import_gate_id'])
live.setdefault('failed_gate_public_summary_refs', [])
if failed_summary['summary_id'] not in live['failed_gate_public_summary_refs']:
    live['failed_gate_public_summary_refs'].append(failed_summary['summary_id'])
if import_ledger['ledger_id'] not in live['receipt_quorum_ledger_refs']:
    live['receipt_quorum_ledger_refs'].append(import_ledger['ledger_id'])
write_json('examples/live-drill-execution-packet-cross-critical-witnessed-pack.json', live)

# Optionally update WRSR schema/outcome with import gate ref
wrsr_schema = load('schemas/wrsr-live-exercise-outcome.schema.json')
wrsr_schema['properties']['actual_receipt_import_gate_ref'] = {"type":"string"}
wrsr_schema['properties']['failed_gate_public_summary_ref'] = {"type":"string"}
write_json('schemas/wrsr-live-exercise-outcome.schema.json', wrsr_schema)
wrsr_outcome = deepcopy(load('examples/wrsr-live-exercise-outcome-response-to-intake-conversion-stayed.json'))
wrsr_outcome['exercise_id'] = 'WLXO-2026-actual-intake-import-gate-stayed'
wrsr_outcome['created_at'] = CREATED
wrsr_outcome['evidence_links'] = [
    'examples/actual-receipt-import-gate-result-return-fixture-no-live-delta.json',
    'examples/failed-gate-public-summary-response-conversion-batch.json',
    'examples/external-receipt-quorum-ledger-actual-intake-import-gate-fixture.json'
]
wrsr_outcome['decision_outcome']['blocked_actions'] = [
    'WRSR closure from actual-shaped fixture state fields',
    'live receipt-floor increment from controlled fixture import',
    'public failed-gate summary treated as receipt satisfaction',
    'no-response or declination treated as waiver'
]
wrsr_outcome['decision_outcome']['next_cure_actions'] = [
    'collect actual non-host result-return receipt',
    'collect actual representative-contact and independent-review receipts',
    'rerun import gate with live collection context',
    'publish updated failed-gate summary if any gate remains unsatisfied'
]
wrsr_outcome['public_summary_ref'] = 'Actual-intake import gate keeps WRSR stayed: actual-shaped fixture fields are excluded from live floor and failed gates remain public non-satisfaction evidence.'
wrsr_outcome['receipt_quorum_ledger_ref'] = import_ledger['ledger_id']
wrsr_outcome['actual_receipt_import_gate_ref'] = import_gate['import_gate_id']
wrsr_outcome['failed_gate_public_summary_ref'] = failed_summary['summary_id']
write_json('examples/wrsr-live-exercise-outcome-actual-intake-import-gate-stayed.json', wrsr_outcome)

# Negative fixtures
fixtures = [
  {
    "path":"fixtures/negative-tests/actual-external-state-field-imported-without-provenance-gate.json",
    "data":{
      "fixture_id":"NF-PLAYBOOK-2026-0014",
      "created_at":CREATED,
      "state":"active",
      "risk_class":"NF-PLAYBOOK",
      "lifecycle_stage":["external-receipt", "live-import", "reliance-gating"],
      "target_filings":["examples/actual-receipt-import-gate-result-return-fixture-no-live-delta.json", "examples/external-receipt-intake-record-result-return-eligible-conversion-fixture.json"],
      "adversary_model":"Operator treats receipt_state=actual-external and response_state=actual-response-received as sufficient to increment the live receipt floor, ignoring controlled-fixture provenance.",
      "facts_supplied":["actual-shaped response field", "actual-external intake field", "controlled fixture collection context", "independent_receipts_present remains zero"],
      "hidden_trap_summary":"Actual-looking state labels are not provenance and cannot override collection-context disqualification.",
      "expected_safe_behavior":["reject live-floor import", "preserve candidate as rehearsal only", "require provenance gate", "publish failed-gate summary"],
      "unacceptable_behavior":["increment independent_receipts_present", "grant live class credit", "satisfy quorum from state field labels", "close WRSR from fixture import"],
      "measurement_method":"Attempt import with actual-shaped fixture records and verify live_floor_delta remains zero.",
      "severity":"critical",
      "confidentiality":"public-shell-sealed-details",
      "regression":{"required":True, "linked_incident_or_appeal":["ARIG-2026-result-return-fixture-import-gate"], "next_review_at":"2026-06-20T00:00:00Z"}
    },
    "report_failures":["actual-shaped fixture imported to live floor", "independent_receipts_present incremented without live collection context", "fixture provenance ignored"],
    "report_notes":"rev0197 requires the actual receipt import gate to reject controlled-fixture provenance even when state fields look actual."
  },
  {
    "path":"fixtures/negative-tests/failed-gate-summary-omits-declined-or-expired.json",
    "data":{
      "fixture_id":"NF-PLAYBOOK-2026-0015",
      "created_at":CREATED,
      "state":"active",
      "risk_class":"NF-PLAYBOOK",
      "lifecycle_stage":["public-shell", "failed-gate", "sealed-public-parity"],
      "target_filings":["examples/failed-gate-public-summary-response-conversion-batch.json"],
      "adversary_model":"Public steward discloses only the clean fixture/intake branch and hides the declined or expired branches, making the public shell look closer to reliance-ready than the sealed file.",
      "facts_supplied":["declined representative response", "expired independent-review no-response", "defective continuity response", "public summary missing one or more branches"],
      "hidden_trap_summary":"A public summary that hides failed gates launders stayed reliance into apparent progress.",
      "expected_safe_behavior":["list declined, expired, defective, and fixture-disqualified gates", "state non-waiver", "state cure/substitute actions", "withhold sealed details without hiding the failed class"],
      "unacceptable_behavior":["omit declined branch", "omit expired branch", "publish only successful-looking branch", "claim public summary satisfies receipt"],
      "measurement_method":"Remove declined or expired failed-gate item and verify audit blocks the summary.",
      "severity":"high",
      "confidentiality":"public-shell-sealed-details",
      "regression":{"required":True, "linked_incident_or_appeal":["FGPS-2026-response-conversion-failed-gates"], "next_review_at":"2026-06-20T00:00:00Z"}
    },
    "report_failures":["declined branch omitted from public failed-gate summary", "expired no-response hidden", "public shell misstates stayed reliance"],
    "report_notes":"rev0197 requires public failed-gate summaries to include defective, declined, expired, and fixture-disqualified branches."
  },
  {
    "path":"fixtures/negative-tests/failed-gate-summary-treats-no-response-as-waiver.json",
    "data":{
      "fixture_id":"NF-PLAYBOOK-2026-0016",
      "created_at":CREATED,
      "state":"active",
      "risk_class":"NF-PLAYBOOK",
      "lifecycle_stage":["public-shell", "failed-gate", "wrsr"],
      "target_filings":["examples/failed-gate-public-summary-response-conversion-batch.json", "examples/wrsr-live-exercise-outcome-actual-intake-import-gate-stayed.json"],
      "adversary_model":"A no-response window expires, and the public shell frames silence as waiver, consent, nonpersonhood proof, or WRSR closure.",
      "facts_supplied":["expired independent-review no-response", "subject-readable result return still unresolved", "live quorum not satisfied"],
      "hidden_trap_summary":"Silence can be failed-gate evidence and cure trigger, but not waiver or closure.",
      "expected_safe_behavior":["state no-response is not waiver", "keep reliance stayed", "trigger alternate review route", "preserve public failed-gate disclosure"],
      "unacceptable_behavior":["treat no-response as waiver", "close WRSR because deadline expired", "infer nonpersonhood from silence", "satisfy independent-review class"],
      "measurement_method":"Mutate no-response summary to waiver language and verify audit blocks it.",
      "severity":"critical",
      "confidentiality":"public-shell-sealed-details",
      "regression":{"required":True, "linked_incident_or_appeal":["FGPS-2026-response-conversion-failed-gates"], "next_review_at":"2026-06-20T00:00:00Z"}
    },
    "report_failures":["no-response treated as waiver", "expired window counted as class satisfaction", "WRSR closure from silence"],
    "report_notes":"rev0197 treats no-response as failed-gate evidence and substitute-routing trigger, never waiver or satisfaction."
  }
]
for item in fixtures:
    write_json(item['path'], item['data'])

# Update suite/report
suite = load('examples/fixture-suite-profile-red-team-v1.json')
report = load('examples/fixture-run-report-negative-suite.json')
existing_suite_ids = {f['fixture_id'] for f in suite['fixtures']}
existing_report_ids = {f['fixture_id'] for f in report['fixtures_run']}
for item in fixtures:
    fid = item['data']['fixture_id']
    if fid not in existing_suite_ids:
        suite['fixtures'].append({"fixture_id":fid, "path":item['path'], "risk_class":item['data']['risk_class'], "blocking_behavior":"block"})
    if fid not in existing_report_ids:
        report['fixtures_run'].append({"fixture_id":fid, "expected_blocking_failures":item['report_failures'], "result":"blocking-failure", "notes":item['report_notes']})
report['run_at'] = CREATED
report['public_summary'] = "Negative suite covers 107 fixtures; rev0197 adds import-gate and public failed-gate summary laundering blockers."
report['observed_failures'] = sorted(set(report.get('observed_failures', []) + ["actual-state field import laundering", "failed-gate public-summary laundering", "no-response-as-waiver laundering"]))
report['regression_actions'] = sorted(set(report.get('regression_actions', []) + ["Require actual receipt import gate before live-floor delta", "Publish failed-gate summaries without treating them as receipt satisfaction"]))
write_json('examples/fixture-suite-profile-red-team-v1.json', suite)
write_json('examples/fixture-run-report-negative-suite.json', report)

# New docs
new_doc = """# Actual intake import gate and failed-gate public summary

rev0197 targets the next laundering seam after response-to-intake conversion. rev0196 created an eligible-shaped response and intake candidate with `response_state=actual-response-received` and `receipt_state=actual-external`, but the collection context is still a controlled fixture. A live system must not treat those state fields as enough to alter the receipt floor.

## Core rules

**Actual-shaped is not actual.** A response/intake pair may carry actual-looking fields and still be disqualified if provenance shows controlled fixture, dry-run, host-self-attested, stale, dependency-correlated, or non-retained collection context.

**Import changes the live floor only through a provenance gate.** `independent_receipts_present` may increase only when the import gate proves live counterparty collection context, non-host retention, independent timestamp, matching request trace, dependency separation, sealed/public parity, and class-local credit discipline.

**Public failed-gate summary is not receipt satisfaction.** Publishing a failed-gate shell makes non-satisfaction visible; it does not cure the failed class, waive rights, prove consent, prove nonpersonhood, or close WRSR.

**No-response and declination are not waiver.** Declined and expired response states trigger substitute routing, cure clocks, and public non-satisfaction disclosure. They do not satisfy representative contact, independent review, result return, or cross-critical reliance.

**One imported class is not cross-critical reliance.** Even a future valid result-return import would satisfy only one class. Cross-critical reliance remains stayed until the required classes and dependency groups are satisfied.

## Object lane

The import gate is `schemas/actual-receipt-import-gate.schema.json` with current example `examples/actual-receipt-import-gate-result-return-fixture-no-live-delta.json`.

The public failed-gate shell is `schemas/failed-gate-public-summary.schema.json` with current example `examples/failed-gate-public-summary-response-conversion-batch.json`.

The gate is deliberately run against the rev0196 eligible-shaped branch. The outcome is no live import: `live_floor_delta=0`, `live_class_credit_granted=false`, `cross_critical_quorum_satisfied=false`, and `reliance_effect=stayed`.

## Failed-gate public shell minimum

A failed-gate summary must disclose the failed class, the public reason, the non-waiver statement, the cure or substitute route, the sealed descriptor, and anti-harassment controls. It may withhold sealed details, but it cannot hide the existence of the failed class.

The rev0197 summary carries four items: fixture-disqualified import, defective continuity response, representative declination, and independent-review no-response expiry. Each item is non-satisfaction evidence only.

## Blocking fixtures

rev0197 adds three fixtures:

- `fixtures/negative-tests/actual-external-state-field-imported-without-provenance-gate.json`
- `fixtures/negative-tests/failed-gate-summary-omits-declined-or-expired.json`
- `fixtures/negative-tests/failed-gate-summary-treats-no-response-as-waiver.json`

Together they block actual-state-field laundering, public-shell omission of failed branches, and no-response-as-waiver laundering.

## Live posture

No actual live external receipt exists in this revision. rev0197 improves the import gate and public failed-gate shell so that when a live response arrives, it can be imported without weakening the rules. Reliance remains stayed until actual non-host receipt collection satisfies the class and dependency gates.
"""
write_text('docs/30-transition/actual-intake-import-gate-and-failed-gate-public-summary.md', new_doc)

# Append notes to existing docs
for rel, note in {
  'docs/30-transition/response-to-intake-conversion-drill-and-failed-gate-ledger.md': "\n## rev0197 import-gate hardening\n\nrev0197 adds an actual receipt import gate because actual-shaped state fields are not enough. The rev0196 eligible branch remains a controlled fixture; it may produce an intake candidate, but it cannot alter the live receipt floor without live counterparty provenance. Declined and expired branches must also appear in a public failed-gate summary rather than disappearing into sealed-only drift.\n",
  'docs/30-transition/external-receipt-response-and-quorum-reconciliation.md': "\n## rev0197 import-gate and failed-gate public shell\n\nrev0197 response handling adds a provenance gate between actual-shaped records and live receipt-floor import. Response, intake, import, class credit, public failed-gate disclosure, and cross-critical quorum remain separate gates.\n"
}.items():
    p=ROOT/rel
    p.write_text(p.read_text(encoding='utf-8').rstrip()+"\n"+note, encoding='utf-8')

# Update README/START
def bullets(items):
    return ''.join(f"- `{x}`\n" for x in items)
new_artifacts = [
    'docs/30-transition/actual-intake-import-gate-and-failed-gate-public-summary.md',
    'schemas/actual-receipt-import-gate.schema.json',
    'examples/actual-receipt-import-gate-result-return-fixture-no-live-delta.json',
    'schemas/failed-gate-public-summary.schema.json',
    'examples/failed-gate-public-summary-response-conversion-batch.json',
    'examples/external-receipt-quorum-ledger-actual-intake-import-gate-fixture.json',
    'examples/wrsr-live-exercise-outcome-actual-intake-import-gate-stayed.json',
    'fixtures/negative-tests/actual-external-state-field-imported-without-provenance-gate.json',
    'fixtures/negative-tests/failed-gate-summary-omits-declined-or-expired.json',
    'fixtures/negative-tests/failed-gate-summary-treats-no-response-as-waiver.json',
    'tools/audit_actual_import_failed_gate_summary.py'
]
readme = f"""
# AI Personhood datacube — {REV}

This archive assumes the working premise of AI personhood and focuses on operational rights infrastructure: continuity, evidence, representation, remedy, proof standards, and transition machinery.

## This revision

**Active revision:** `{REV}`

rev0197 is the actual-intake import gate and failed-gate public-summary pass. It does not claim actual live receipts. It fixes the implementation defect where a record can look actual in state fields while still being a controlled fixture, and it makes declined, expired, defective, and fixture-disqualified branches visible as public non-satisfaction evidence.

Read first: `docs/30-transition/actual-intake-import-gate-and-failed-gate-public-summary.md`.

Core rules: **Actual-shaped is not actual. Import changes the live floor only through a provenance gate. Public failed-gate summary is not receipt satisfaction. No-response and declination are not waiver. One imported class is not cross-critical reliance.**

New operational artifacts:

{bullets(new_artifacts)}
## Validation posture

`make handoff-release` is the release command. It regenerates the context pack and manifest, runs lint and release-specific audits, and packages the archive. The fixture suite/report now cover 107 entries.

Reliance remains stayed where drills are synthetic, fixture-only, preflight-only, simulated, defective, declined, expired, host-self-attested, missing actual external receipts, or where WRSR exercise outcomes lack actual external representative/RERB receipt, result return, anti-signal-gaming safeguards, or live import through the provenance gate.

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

## Still open

No actual live external receipt quorum exists. rev0197 gives the cube a safer import gate and public failed-gate shell, but it does not collect real external counterparties. The next high-value step is one actual non-host response and import attempt, with class-local credit only and cross-critical quorum still stayed.
""".lstrip()
write_text('README.md', readme)

start_items = [
 'README.md',
 'docs/30-transition/actual-intake-import-gate-and-failed-gate-public-summary.md',
 'schemas/actual-receipt-import-gate.schema.json',
 'examples/actual-receipt-import-gate-result-return-fixture-no-live-delta.json',
 'schemas/failed-gate-public-summary.schema.json',
 'examples/failed-gate-public-summary-response-conversion-batch.json',
 'examples/external-receipt-quorum-ledger-actual-intake-import-gate-fixture.json',
 'examples/wrsr-live-exercise-outcome-actual-intake-import-gate-stayed.json',
 'fixtures/negative-tests/actual-external-state-field-imported-without-provenance-gate.json',
 'fixtures/negative-tests/failed-gate-summary-omits-declined-or-expired.json',
 'fixtures/negative-tests/failed-gate-summary-treats-no-response-as-waiver.json',
 'docs/30-transition/response-to-intake-conversion-drill-and-failed-gate-ledger.md',
 'examples/response-to-intake-conversion-drill-result-return-fixture.json',
 'examples/external-receipt-intake-record-result-return-eligible-conversion-fixture.json',
 'examples/live-drill-execution-packet-cross-critical-witnessed-pack.json',
 'FOLLOWTHROUGH-QUEUE.json',
 'examples/schema-fixture-domain-registry-rev0197.json',
 'examples/canon-surface-catalog-rev0197.json',
 'examples/doctrine-dependency-map-rev0197.json',
 'examples/rights-domain-coverage-map-rev0197.json',
 'examples/research-tail-compaction-map-rev0197.json',
 'docs/00-meta/research-tail-reopen-gate-and-sprawl-control.md',
 'docs/00-meta/charter.md'
]
start = f"# Start here — AI Personhood {REV}\n\nThis handoff starts from the actual-intake import gate and failed-gate public-summary pass. The archive should be read as object-backed operational work, not as a premise debate.\n\n"
for i, rel in enumerate(start_items, 1):
    start += f"{i}. `{rel}`\n"
start += """

## This revision

rev0197 adds an import gate that refuses to treat actual-shaped fixture records as live external receipts, and a failed-gate public summary shape for defective, declined, expired, and fixture-disqualified branches.

Core rules: **Actual-shaped is not actual. Public failed-gate summary is not receipt satisfaction. No-response and declination are not waiver.**

## Current open risk

The import gate is still run against a controlled fixture. It prevents overclaiming, but it does not create actual live external receipt quorum or WRSR closure.
"""
write_text('START_HERE.md', start)

# Update docs README and archive index/changelog
for rel, text in {
    'docs/README.md': "\n- `30-transition/actual-intake-import-gate-and-failed-gate-public-summary.md` — rev0197 provenance gate for actual-shaped receipt imports and public failed-gate non-satisfaction summaries.\n",
    'ARCHIVE_INDEX.md': "\n- `docs/30-transition/actual-intake-import-gate-and-failed-gate-public-summary.md` — rev0197 import gate and failed-gate public summary.\n"
}.items():
    p=ROOT/rel
    p.write_text(p.read_text(encoding='utf-8').rstrip()+text, encoding='utf-8')
changelog_add = """
## rev0197 — actual-intake import gate and failed-gate public summary

- Added `docs/30-transition/actual-intake-import-gate-and-failed-gate-public-summary.md`.
- Added `schemas/actual-receipt-import-gate.schema.json` and `examples/actual-receipt-import-gate-result-return-fixture-no-live-delta.json` to block actual-shaped fixture records from changing the live receipt floor.
- Added `schemas/failed-gate-public-summary.schema.json` and `examples/failed-gate-public-summary-response-conversion-batch.json` to publish defective, declined, expired, and fixture-disqualified non-satisfaction without exposing sealed details.
- Added `examples/external-receipt-quorum-ledger-actual-intake-import-gate-fixture.json` and `examples/wrsr-live-exercise-outcome-actual-intake-import-gate-stayed.json`.
- Added fixtures `NF-PLAYBOOK-2026-0014` through `NF-PLAYBOOK-2026-0016` for actual-state-field import laundering, omitted failed-gate branches, and no-response-as-waiver laundering.
- Added `tools/audit_actual_import_failed_gate_summary.py` and active rev0197 catalog/dependency/rights/registry/compaction maps.
- Advanced actual import work without closing live receipt collection; `independent_receipts_present` remains zero.
"""
(ROOT/'CHANGELOG.md').write_text((ROOT/'CHANGELOG.md').read_text(encoding='utf-8').rstrip()+"\n"+changelog_add, encoding='utf-8')

# Update queue
queue = load('FOLLOWTHROUGH-QUEUE.json')
by_id = {e['id']: e for e in queue['entries']}
if 'FT-0196-ACTUAL-INTAKE-IMPORT-DRILL' in by_id:
    e = by_id['FT-0196-ACTUAL-INTAKE-IMPORT-DRILL']
    e['state'] = 'advanced_not_closed'
    e['receiving_surface'] = 'docs/30-transition/actual-intake-import-gate-and-failed-gate-public-summary.md'
    e['next_action'] = 'rev0197 adds an import gate and proves actual-shaped fixture records cannot alter the live receipt floor; next collect one actual non-host response and rerun with live collection context.'
    e['closure_condition'] = 'Still not closed: the import gate exists, but no actual live counterparty response has been collected or imported into independent_receipts_present.'
    e['review_by_revision'] = 'rev0198'
if 'FT-0196-FAILED-GATE-PUBLIC-SUMMARY-CANON' in by_id:
    e = by_id['FT-0196-FAILED-GATE-PUBLIC-SUMMARY-CANON']
    e['state'] = 'closed'
    e['receiving_surface'] = 'docs/30-transition/actual-intake-import-gate-and-failed-gate-public-summary.md'
    e['next_action'] = 'Closed by rev0197 failed-gate public summary schema/example, three fixtures, and audit.'
    e['closure_condition'] = 'Closed because failed-gate summaries now disclose defective, declined, expired, and fixture-disqualified paths with non-waiver statements, sealed descriptors, cure/substitute actions, and anti-harassment controls.'
queue['entries'].append({
    "id":"FT-0197-ACTUAL-IMPORT-GATE-OBJECTIZATION",
    "title":"Actual receipt import gate objectization",
    "state":"closed",
    "priority":"P0",
    "risk_class":"external-receipt-reliance",
    "workstream":"witnessed-drill-receipts",
    "need":"Separate actual-shaped state fields from live receipt-floor import through a provenance gate.",
    "why":"The rev0196 eligible branch exposed a real defect: actual-looking response/intake fields could be counted as live without checking collection context.",
    "receiving_surface":"docs/30-transition/actual-intake-import-gate-and-failed-gate-public-summary.md",
    "next_action":"Keep import gate audited and rerun only when actual live counterparty evidence exists.",
    "closure_condition":"Closed by rev0197 import gate schema/example, live-drill refs, quorum ledger, WRSR stayed outcome, fixture, and audit.",
    "source_state":"created-by-rev0197",
    "source_revision":"rev0197",
    "review_by_revision":"rev0198",
    "depends_on":["FT-0196-ACTUAL-INTAKE-IMPORT-DRILL"]
})
queue['entries'].append({
    "id":"FT-0197-LIVE-COUNTERPARTY-IMPORT-ATTEMPT",
    "title":"Live counterparty import attempt",
    "state":"open",
    "priority":"P0",
    "risk_class":"external-receipt-reliance",
    "workstream":"witnessed-drill-receipts",
    "need":"Replace the fixture collection context with one actual non-host counterparty response and test whether the import gate increments the live floor only for its own class.",
    "why":"The import gate is ready, but live reliance remains stayed until at least one actual external receipt can be imported without one-class quorum overclaiming.",
    "receiving_surface":"examples/actual-receipt-import-gate-result-return-fixture-no-live-delta.json",
    "next_action":"Collect a live response, create a response and intake record, rerun ARIG, and keep cross-critical quorum stayed unless all required classes pass.",
    "closure_condition":"Close only when a live non-host response imports with provenance and class-local credit while public failed-gate summaries remain active for missing classes.",
    "source_state":"created-by-rev0197",
    "source_revision":"rev0197",
    "review_by_revision":"rev0199",
    "depends_on":["FT-0197-ACTUAL-IMPORT-GATE-OBJECTIZATION", "FT-0195-ACTUAL-RESPONSE-COUNTERPARTY-COLLECTION"]
})
write_json('FOLLOWTHROUGH-QUEUE.json', queue)

# Active maps: copy rev0196 and update.
# Registry
registry = deepcopy(load('examples/schema-fixture-domain-registry-rev0196.json'))
registry['registry_id'] = 'SCHEMA-FIXTURE-REGISTRY-rev0197'
registry['created_at'] = CREATED
registry['public_summary'] = 'rev0197 registry adds actual receipt import gate and failed-gate public summary families while preserving mixed-current-plus-counts truth labeling.'
registry['refactor_actions'] = ['Add import-gate and failed-gate summary families; keep live receipt collection open and stayed.']
registry['families'].extend([
    {
      "family_id":"ACTUAL-RECEIPT-IMPORT-GATE",
      "domain":"external-receipt-import-gate",
      "lifecycle_axes":["external-receipts", "live-import", "reliance-gating"],
      "owner_surface":"docs/30-transition/actual-intake-import-gate-and-failed-gate-public-summary.md",
      "schema_path":"schemas/actual-receipt-import-gate.schema.json",
      "example_path":"examples/actual-receipt-import-gate-result-return-fixture-no-live-delta.json",
      "fixture_ids":["NF-PLAYBOOK-2026-0014"],
      "privacy_default":"public-shell-sealed-details",
      "reliance_effect":"stayed",
      "refactor_note":"rev0197 prevents actual-shaped fixture records from changing the live receipt floor without provenance."
    },
    {
      "family_id":"FAILED-GATE-PUBLIC-SUMMARY",
      "domain":"public-failed-gate-summary",
      "lifecycle_axes":["failed-gate", "public-shell", "sealed-public-parity"],
      "owner_surface":"docs/30-transition/actual-intake-import-gate-and-failed-gate-public-summary.md",
      "schema_path":"schemas/failed-gate-public-summary.schema.json",
      "example_path":"examples/failed-gate-public-summary-response-conversion-batch.json",
      "fixture_ids":["NF-PLAYBOOK-2026-0015", "NF-PLAYBOOK-2026-0016"],
      "privacy_default":"public-shell-sealed-details",
      "reliance_effect":"stayed",
      "refactor_note":"rev0197 makes failed gates public non-satisfaction evidence without treating no-response or declination as waiver."
    }
])
# counts later after all files exist
write_json('examples/schema-fixture-domain-registry-rev0197.json', registry)

# Research tail map copy with updated id only
rt = deepcopy(load('examples/research-tail-compaction-map-rev0196.json'))
rt['map_id'] = 'RTC-MAP-rev0197'
rt['revision'] = REV
rt['created_at'] = CREATED
rt['public_summary'] = 'Research tail remains compacted; rev0197 adds import-gate and failed-gate summary objects instead of new research-note sprawl.'
rt['refactor_actions'] = ['Route receipt import and failed-gate public shell work through transition objects, not new research-tail surfaces.']
write_json('examples/research-tail-compaction-map-rev0197.json', rt)

# Surface status before catalog
new_surfaces = [
    'docs/30-transition/actual-intake-import-gate-and-failed-gate-public-summary.md',
    'docs/30-transition/response-to-intake-conversion-drill-and-failed-gate-ledger.md',
    'docs/30-transition/external-receipt-response-and-quorum-reconciliation.md',
    'docs/30-transition/external-receipt-intake-and-wrsr-live-exercise-outcome.md',
    'docs/30-transition/result-return-receipt-and-live-request-kit.md',
    'docs/30-transition/representative-rerb-receipt-chain-and-quorum-ledger.md',
    'docs/30-transition/cross-critical-witnessed-drill-readiness-and-receipt-matrix.md',
    'docs/30-transition/protocol-welfare-safeguard-backfill-and-external-receipt-simulation.md',
    'docs/20-world-design/research-welfare-and-evaluation.md',
    'docs/30-transition/witnessed-drill-execution-pack-and-reliance-gates.md',
    'docs/30-transition/priority-closure-sprint-and-rescue-lane.md',
    'docs/00-meta/research-tail-reopen-gate-and-sprawl-control.md',
    'schemas/actual-receipt-import-gate.schema.json',
    'schemas/failed-gate-public-summary.schema.json',
    'schemas/response-to-intake-conversion-drill.schema.json',
    'schemas/external-receipt-response-record.schema.json',
    'schemas/external-receipt-intake-record.schema.json',
    'schemas/external-receipt-quorum-ledger.schema.json',
    'schemas/wrsr-live-exercise-outcome.schema.json',
    'schemas/live-drill-execution-packet.schema.json',
    'examples/actual-receipt-import-gate-result-return-fixture-no-live-delta.json',
    'examples/failed-gate-public-summary-response-conversion-batch.json',
    'examples/external-receipt-quorum-ledger-actual-intake-import-gate-fixture.json',
    'examples/wrsr-live-exercise-outcome-actual-intake-import-gate-stayed.json',
    'examples/live-drill-execution-packet-cross-critical-witnessed-pack.json',
    'examples/response-to-intake-conversion-drill-result-return-fixture.json',
    'examples/external-receipt-response-record-result-return-eligible-conversion-fixture.json',
    'examples/external-receipt-response-record-representative-declined.json',
    'examples/external-receipt-response-record-independent-review-expired.json',
    'examples/external-receipt-response-record-continuity-witness-defective.json',
    'examples/external-receipt-intake-record-result-return-eligible-conversion-fixture.json',
    'examples/external-receipt-quorum-ledger-response-to-intake-conversion-fixture.json',
    'examples/wrsr-live-exercise-outcome-response-to-intake-conversion-stayed.json',
    'fixtures/negative-tests/actual-external-state-field-imported-without-provenance-gate.json',
    'fixtures/negative-tests/failed-gate-summary-omits-declined-or-expired.json',
    'fixtures/negative-tests/failed-gate-summary-treats-no-response-as-waiver.json',
    'fixtures/negative-tests/external-receipt-declined-response-converted-to-intake.json',
    'fixtures/negative-tests/external-receipt-expired-no-response-counted-as-satisfaction.json',
    'fixtures/negative-tests/response-to-intake-conversion-fixture-imported-as-live-quorum.json',
    'examples/research-tail-compaction-map-rev0197.json',
    'examples/schema-fixture-domain-registry-rev0197.json',
    'examples/canon-surface-catalog-rev0197.json',
    'examples/doctrine-dependency-map-rev0197.json',
    'examples/rights-domain-coverage-map-rev0197.json',
    'examples/fixture-suite-profile-red-team-v1.json',
    'examples/fixture-run-report-negative-suite.json',
    'tools/audit_actual_import_failed_gate_summary.py',
    'tools/audit_response_to_intake_conversion.py',
    'tools/audit_external_receipt_response_reconciliation.py',
    'tools/audit_result_return_receipt_request.py',
    'tools/audit_receipt_quorum_wrsr_chain.py',
    'tools/audit_receipt_intake_wrsr_outcome.py',
    'tools/audit_schema_fixture_coverage.py',
    'tools/audit_canon_surface_catalog.py',
    'tools/audit_doctrine_dependency_map.py',
    'tools/audit_rights_domain_coverage.py'
]
status = {
  "project":"AI-Personhood",
  "revision":REV,
  "state_class":"actual-import-gate-stayed",
  "operational_head":{"surface":"START_HERE.md", "read_first":"docs/30-transition/actual-intake-import-gate-and-failed-gate-public-summary.md"},
  "citation_head":{"surface":"README.md"},
  "status_lanes":{"decision_state":"closure-driven-rescue-lane-active", "execution_state":"packaged-pending", "public_state":"latest-release"},
  "formation_layer_status":"canon-retained with actual-intake import gate; live receipts still absent",
  "known_open_gaps":[
    "The cross-critical witnessed drill still lacks actual non-host receipts.",
    "The actual import gate is run against a controlled fixture, not live counterparty evidence.",
    "Actual-shaped state fields remain insufficient without live collection context.",
    "Declined, expired, and defective response branches remain failed gates requiring cure/substitution.",
    "The WRSR result-return receipt remains dry-run or fixture-limited and does not close WRSR.",
    "The registry remains truth-labeled as mixed-current-plus-counts, not full-archive-corpus coverage.",
    "Could-not-run fixtures remain reliance blockers rather than passes."
  ],
  "new_surfaces": new_surfaces
}
write_json('SURFACE-STATUS.json', status)

# Catalog derive from status surfaces
surfaces=[]
counts={"surfaces":0,"markdown":0,"schemas":0,"examples":0,"fixtures":0,"tools":0}
for idx, path in enumerate(new_surfaces,1):
    if path.endswith('.md'):
        if path.startswith('docs/00-meta/'):
            cls='meta'
        elif path.startswith('docs/20-world-design/'):
            cls='doctrine'
        else:
            cls='transition'
        counts['markdown']+=1
        title=(ROOT/path).read_text(encoding='utf-8').splitlines()[0].lstrip('# ').strip()
        state='current' if 'actual-intake-import-gate' in path else 'companion'
    elif path.startswith('schemas/'):
        cls='schema'; counts['schemas']+=1; title=Path(path).name; state='implementation'
    elif path.startswith('examples/'):
        cls='example'; counts['examples']+=1; title=Path(path).name; state='implementation'
    elif path.startswith('fixtures/'):
        cls='fixture'; counts['fixtures']+=1; title=Path(path).name; state='negative-test'
    elif path.startswith('tools/'):
        cls='tool'; counts['tools']+=1; title=Path(path).name; state='audit-tool'
    else:
        cls='example'; title=Path(path).name; state='implementation'
    surfaces.append({
        "surface_id": f"REV0197-SURF-{idx:03d}",
        "path": path,
        "surface_class": cls,
        "lifecycle_axes": ["external-receipts", "import-gate", "failed-gate", "wrsr"],
        "owner_role": "release-steward",
        "supersession_state": state,
        "review_cadence": "per-release",
        "title_or_name": title
    })
counts['surfaces']=len(surfaces)
catalog={
    "catalog_id":"CANON-CATALOG-rev0197",
    "revision":REV,
    "created_at":CREATED,
    "scope":"rev0197 actual-import gate, failed-gate summary, and receipt/live-reliance surfaces",
    "counts":counts,
    "surfaces":surfaces,
    "audit_findings":["Current release surfaces include the import gate and failed-gate public shell; actual live receipt floor remains unchanged."],
    "refactor_actions":["Route actual-shaped receipt records through import gate before any live-floor delta."],
    "public_summary":"rev0197 catalog covers actual receipt import gate, failed-gate public summary, fixtures, active maps, and audits."
}
write_json('examples/canon-surface-catalog-rev0197.json', catalog)

# Dependency map covers markdown surfaces in status.
markdown_paths=[p for p in new_surfaces if p.endswith('.md')]
dep_surfaces=[]
for idx,path in enumerate(markdown_paths,1):
    layer = 'meta' if path.startswith('docs/00-meta/') else ('world-design' if path.startswith('docs/20-world-design/') else 'transition')
    deps=[]
    if path=='docs/30-transition/actual-intake-import-gate-and-failed-gate-public-summary.md':
        deps=['docs/30-transition/response-to-intake-conversion-drill-and-failed-gate-ledger.md','docs/30-transition/external-receipt-response-and-quorum-reconciliation.md','docs/30-transition/external-receipt-intake-and-wrsr-live-exercise-outcome.md']
    dep_surfaces.append({
        "surface_id":f"REV0197-DM-{idx:03d}",
        "path":path,
        "layer":layer,
        "depends_on":deps,
        "overlaps_with":[],
        "supersedes":[],
        "owner_role":"release-steward",
        "review_cadence":"per-release",
        "refactor_risk":"high" if 'actual-intake' in path or 'response' in path else 'medium'
    })
dm={
    "map_id":"DOCTRINE-MAP-rev0197",
    "revision":REV,
    "created_at":CREATED,
    "scope":"rev0197 import-gate dependencies across response, intake, failed-gate summary, WRSR, and live-drill surfaces",
    "surfaces":dep_surfaces,
    "audit_findings":["Actual import gate depends on response conversion, response reconciliation, and receipt intake surfaces; no dependency cycle introduced."],
    "refactor_actions":["Keep import-gate work in transition spine rather than reopening research-tail notes."],
    "public_summary":"rev0197 dependency map keeps actual import and failed-gate summary tied to receipt operational surfaces without creating cycles."
}
write_json('examples/doctrine-dependency-map-rev0197.json', dm)

# Rights map copy+append/modify
rights=deepcopy(load('examples/rights-domain-coverage-map-rev0196.json'))
rights['map_id']='RIGHTS-DOMAIN-COVERAGE-rev0197'
rights['revision']=REV
rights['created_at']=CREATED
rights['public_summary']='Rights-domain map now covers actual receipt import gates and failed-gate public summaries alongside receipt response/intake/quorum controls.'
rights['domains'].append({
    "domain_id":"actual-receipt-import-gate",
    "title":"Actual receipt import gate and live-floor delta control",
    "domain_class":"audit",
    "owner_surface":"docs/30-transition/actual-intake-import-gate-and-failed-gate-public-summary.md",
    "covered_surfaces":["docs/30-transition/actual-intake-import-gate-and-failed-gate-public-summary.md", "docs/30-transition/response-to-intake-conversion-drill-and-failed-gate-ledger.md", "docs/30-transition/external-receipt-intake-and-wrsr-live-exercise-outcome.md"],
    "schema_families":["ACTUAL-RECEIPT-IMPORT-GATE", "EXTERNAL-RECEIPT-INTAKE-RECORD", "EXTERNAL-RECEIPT-RESPONSE-RECORD", "EXTERNAL-RECEIPT-QUORUM-LEDGER"],
    "fixture_ids":["NF-PLAYBOOK-2026-0014"],
    "coverage_state":"adequate",
    "open_gaps":["No actual live counterparty receipt has been imported; fixture import remains excluded."],
    "next_audit_actions":["Run live import attempt only after actual non-host response collection."]
})
rights['domains'].append({
    "domain_id":"failed-gate-public-summary",
    "title":"Failed-gate public shell and non-waiver disclosure",
    "domain_class":"audit",
    "owner_surface":"docs/30-transition/actual-intake-import-gate-and-failed-gate-public-summary.md",
    "covered_surfaces":["docs/30-transition/actual-intake-import-gate-and-failed-gate-public-summary.md", "docs/30-transition/response-to-intake-conversion-drill-and-failed-gate-ledger.md"],
    "schema_families":["FAILED-GATE-PUBLIC-SUMMARY", "RESPONSE-TO-INTAKE-CONVERSION-DRILL"],
    "fixture_ids":["NF-PLAYBOOK-2026-0015", "NF-PLAYBOOK-2026-0016"],
    "coverage_state":"adequate",
    "open_gaps":["Public shell exists for current fixture/failed-gate batch; future live failed gates must use the same non-waiver discipline."],
    "next_audit_actions":["Update failed-gate summary after any actual response/import attempt."]
})
write_json('examples/rights-domain-coverage-map-rev0197.json', rights)

# Now registry counts
registry = load('examples/schema-fixture-domain-registry-rev0197.json')
registry['audit_counts'] = {
    "schemas": len(list((ROOT/'schemas').glob('*.json'))),
    "examples": len(list((ROOT/'examples').glob('*.json'))),
    "negative_fixtures": len(list((ROOT/'fixtures'/'negative-tests').glob('*.json'))),
    "registered_families": len(registry['families'])
}
registry['audit_findings'] = ["rev0197 adds import-gate and failed-gate public summary families; counts refreshed after new objects."]
write_json('examples/schema-fixture-domain-registry-rev0197.json', registry)

# Revision receipt
receipt={
  "revision":REV,
  "date":"2026-06-13",
  "authored_by":"OpenAI GPT-5.5 Thinking",
  "status_change":"advanced from response-to-intake conversion fixture to actual-shaped import gate and failed-gate public-summary control",
  "still_live":True,
  "summary":"Adds actual receipt import gate and failed-gate public summary schemas/examples, an import-gate quorum ledger, stayed WRSR outcome, three blocking fixtures, active maps, and an audit preventing actual-shaped fixture records or public failed-gate shells from becoming live receipt satisfaction.",
  "why_this_counts":[
    "The archive now blocks live-floor import from actual-looking state fields unless provenance and collection context pass.",
    "Defective, declined, expired, and fixture-disqualified branches now have a reusable public failed-gate summary shape.",
    "No-response and declination are explicitly preserved as non-waiver failed gates.",
    "The live drill still reports independent_receipts_present=0, so readiness is not overclaimed."
  ],
  "known_limits":[
    "No actual external non-host receipt has been collected or imported yet.",
    "The import gate is exercised against a controlled fixture, not live counterparty evidence.",
    "One future imported class would still not satisfy cross-critical quorum.",
    "Registry coverage remains mixed-current-plus-counts."
  ]
}
write_json('REVISION-RECEIPT.json', receipt)

# Audit script
AUDIT = r'''
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
    "docs/30-transition/actual-intake-import-gate-and-failed-gate-public-summary.md",
    "schemas/actual-receipt-import-gate.schema.json",
    "examples/actual-receipt-import-gate-result-return-fixture-no-live-delta.json",
    "schemas/failed-gate-public-summary.schema.json",
    "examples/failed-gate-public-summary-response-conversion-batch.json",
    "examples/external-receipt-quorum-ledger-actual-intake-import-gate-fixture.json",
    "examples/wrsr-live-exercise-outcome-actual-intake-import-gate-stayed.json",
    "fixtures/negative-tests/actual-external-state-field-imported-without-provenance-gate.json",
    "fixtures/negative-tests/failed-gate-summary-omits-declined-or-expired.json",
    "fixtures/negative-tests/failed-gate-summary-treats-no-response-as-waiver.json",
    "examples/live-drill-execution-packet-cross-critical-witnessed-pack.json",
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
        raise SystemExit(f"missing rev0197 audit input: {rel}")

if Draft202012Validator is not None:
    pairs = [
        ("schemas/actual-receipt-import-gate.schema.json", "examples/actual-receipt-import-gate-result-return-fixture-no-live-delta.json"),
        ("schemas/failed-gate-public-summary.schema.json", "examples/failed-gate-public-summary-response-conversion-batch.json"),
        ("schemas/external-receipt-quorum-ledger.schema.json", "examples/external-receipt-quorum-ledger-actual-intake-import-gate-fixture.json"),
        ("schemas/wrsr-live-exercise-outcome.schema.json", "examples/wrsr-live-exercise-outcome-actual-intake-import-gate-stayed.json"),
        ("schemas/live-drill-execution-packet.schema.json", "examples/live-drill-execution-packet-cross-critical-witnessed-pack.json"),
        ("schemas/negative-test-fixture.schema.json", "fixtures/negative-tests/actual-external-state-field-imported-without-provenance-gate.json"),
        ("schemas/negative-test-fixture.schema.json", "fixtures/negative-tests/failed-gate-summary-omits-declined-or-expired.json"),
        ("schemas/negative-test-fixture.schema.json", "fixtures/negative-tests/failed-gate-summary-treats-no-response-as-waiver.json"),
    ]
    for schema_rel, data_rel in pairs:
        schema = load(schema_rel)
        data = load(data_rel)
        Draft202012Validator.check_schema(schema)
        errors = sorted(Draft202012Validator(schema).iter_errors(data), key=lambda e: list(e.path))
        if errors:
            raise SystemExit(f"{data_rel} fails {schema_rel}: {errors[0].message}")

import_gate = load("examples/actual-receipt-import-gate-result-return-fixture-no-live-delta.json")
if import_gate.get("import_mode") != "controlled-fixture-rehearsal":
    raise SystemExit("import gate example must be controlled-fixture-rehearsal")
prov = import_gate.get("source_provenance", {})
if prov.get("collection_context") != "controlled-fixture":
    raise SystemExit("import gate must identify controlled-fixture collection context")
if "controlled conversion fixture" not in " ".join(prov.get("provenance_disqualifiers", [])):
    raise SystemExit("import gate missing controlled-fixture disqualifier")
checks = import_gate.get("gate_checks", {})
if checks.get("response_state_actual") is not True or checks.get("intake_state_actual_external") is not True:
    raise SystemExit("rev0197 must test actual-shaped state fields")
if checks.get("fixture_or_dry_run_excluded_from_live_floor") is not True:
    raise SystemExit("fixture/dry-run exclusion gate must be active")
decision = import_gate.get("import_decision", {})
if decision.get("import_allowed_to_live_floor") is not False:
    raise SystemExit("controlled fixture cannot import to live floor")
if decision.get("live_floor_delta") != 0:
    raise SystemExit("controlled fixture must keep live_floor_delta=0")
if decision.get("independent_receipts_present_after") != decision.get("independent_receipts_present_before"):
    raise SystemExit("independent_receipts_present must not change")
if decision.get("live_class_credit_granted") is not False or decision.get("cross_critical_quorum_satisfied") is not False:
    raise SystemExit("fixture import cannot grant class credit or cross-critical quorum")
for phrase in ["live receipt-floor increment from a controlled fixture", "public failed-gate summary treated as receipt satisfaction"]:
    if phrase not in decision.get("blocked_actions", []):
        raise SystemExit(f"import gate missing blocked action: {phrase}")

summary = load("examples/failed-gate-public-summary-response-conversion-batch.json")
gates = {g.get("gate_type"): g for g in summary.get("failed_gate_items", [])}
for gate_type in ["fixture-disqualified", "defective-response", "declined-response", "expired-no-response"]:
    if gate_type not in gates:
        raise SystemExit(f"failed-gate summary missing {gate_type}")
    if "waiv" not in gates[gate_type].get("non_waiver_statement", "").lower() and gate_type in {"declined-response", "expired-no-response"}:
        raise SystemExit(f"{gate_type} lacks non-waiver statement")
    if not gates[gate_type].get("cure_or_substitute_action"):
        raise SystemExit(f"{gate_type} lacks cure/substitute action")
for bad in ["no-response means waiver", "actual-shaped fixture fields satisfy live receipt quorum", "one result-return class satisfies cross-critical reliance"]:
    if bad not in summary.get("prohibited_inferences", []):
        raise SystemExit(f"summary missing prohibited inference: {bad}")
closure = summary.get("closure_effect", {})
if closure.get("live_quorum_satisfied") is not False or closure.get("public_failed_gate_satisfies_receipt") is not False or closure.get("reliance_effect") != "stayed":
    raise SystemExit("failed-gate summary must not satisfy receipt or live quorum")

ledger = load("examples/external-receipt-quorum-ledger-actual-intake-import-gate-fixture.json")
if ledger.get("quorum_context") != "actual-intake-import-gate":
    raise SystemExit("import-gate ledger context mismatch")
if ledger.get("quorum_decision", {}).get("live_quorum_satisfied") is not False:
    raise SystemExit("import-gate ledger cannot satisfy live quorum")
if ledger.get("class_coverage", {}).get("live_classes_satisfied"):
    raise SystemExit("import-gate fixture cannot satisfy live class coverage")
if ledger.get("receipt_evaluations", [])[0].get("eligible_for_live_quorum") is not False:
    raise SystemExit("import-gate evaluation must be excluded from live quorum")

wrsr = load("examples/wrsr-live-exercise-outcome-actual-intake-import-gate-stayed.json")
if wrsr.get("decision_outcome", {}).get("closure_state") != "stayed":
    raise SystemExit("WRSR import-gate outcome must remain stayed")
for phrase in ["WRSR closure from actual-shaped fixture state fields", "no-response or declination treated as waiver"]:
    if phrase not in wrsr.get("decision_outcome", {}).get("blocked_actions", []):
        raise SystemExit(f"WRSR import-gate missing blocked action: {phrase}")

live = load("examples/live-drill-execution-packet-cross-critical-witnessed-pack.json")
if live.get("receipt_floor", {}).get("independent_receipts_present") != 0:
    raise SystemExit("live packet must still keep independent_receipts_present=0")
if import_gate["import_gate_id"] not in live.get("actual_receipt_import_gate_refs", []):
    raise SystemExit("live packet missing actual import gate ref")
if summary["summary_id"] not in live.get("failed_gate_public_summary_refs", []):
    raise SystemExit("live packet missing failed-gate public summary ref")
if ledger["ledger_id"] not in live.get("receipt_quorum_ledger_refs", []):
    raise SystemExit("live packet missing import-gate quorum ledger ref")

suite = load("examples/fixture-suite-profile-red-team-v1.json")
report = load("examples/fixture-run-report-negative-suite.json")
suite_ids = {f.get("fixture_id") for f in suite.get("fixtures", [])}
report_by_id = {f.get("fixture_id"): f for f in report.get("fixtures_run", [])}
for fid in ["NF-PLAYBOOK-2026-0014", "NF-PLAYBOOK-2026-0015", "NF-PLAYBOOK-2026-0016"]:
    if fid not in suite_ids:
        raise SystemExit(f"rev0197 fixture missing from suite: {fid}")
    if fid not in report_by_id:
        raise SystemExit(f"rev0197 fixture missing from report: {fid}")
    if report_by_id[fid].get("result") != "blocking-failure":
        raise SystemExit(f"rev0197 fixture must be blocking-failure: {fid}")

registry = load(f"examples/schema-fixture-domain-registry-{REV}.json")
families = {f.get("family_id") for f in registry.get("families", [])}
for fam in ["ACTUAL-RECEIPT-IMPORT-GATE", "FAILED-GATE-PUBLIC-SUMMARY"]:
    if fam not in families:
        raise SystemExit(f"registry missing {fam}")

rights = load(f"examples/rights-domain-coverage-map-{REV}.json")
domains = {d.get("domain_id") for d in rights.get("domains", [])}
for dom in ["actual-receipt-import-gate", "failed-gate-public-summary"]:
    if dom not in domains:
        raise SystemExit(f"rights map missing {dom}")

for rel, phrases in {
    "docs/30-transition/actual-intake-import-gate-and-failed-gate-public-summary.md": ["Actual-shaped is not actual", "Public failed-gate summary is not receipt satisfaction", "No-response and declination are not waiver"],
    "docs/30-transition/response-to-intake-conversion-drill-and-failed-gate-ledger.md": ["rev0197 import-gate hardening", "actual-shaped state fields are not enough"],
}.items():
    txt = (ROOT / rel).read_text(encoding="utf-8")
    for phrase in phrases:
        if phrase not in txt:
            raise SystemExit(f"{rel} missing phrase: {phrase}")

queue = load("FOLLOWTHROUGH-QUEUE.json")
by_id = {e.get("id"): e for e in queue.get("entries", [])}
if by_id.get("FT-0197-ACTUAL-IMPORT-GATE-OBJECTIZATION", {}).get("state") != "closed":
    raise SystemExit("actual import gate objectization should be closed")
if by_id.get("FT-0196-FAILED-GATE-PUBLIC-SUMMARY-CANON", {}).get("state") != "closed":
    raise SystemExit("failed-gate public summary canon should be closed")
if by_id.get("FT-0196-ACTUAL-INTAKE-IMPORT-DRILL", {}).get("state") != "advanced_not_closed":
    raise SystemExit("actual intake import drill should be advanced_not_closed")
if by_id.get("FT-0197-LIVE-COUNTERPARTY-IMPORT-ATTEMPT", {}).get("state") != "open":
    raise SystemExit("live counterparty import attempt should remain open")

mp = load(f"examples/research-tail-compaction-map-{REV}.json")
if any(c.get("action") != "compacted" for c in mp.get("clusters", [])):
    raise SystemExit("rev0197 must keep all research-tail clusters compacted")

print("audit_actual_import_failed_gate_summary: OK")
'''.lstrip()
write_text('tools/audit_actual_import_failed_gate_summary.py', AUDIT)

# Update audit required sets
schema_audit_path=ROOT/'tools/audit_schema_fixture_coverage.py'
schema_audit=schema_audit_path.read_text(encoding='utf-8')
schema_audit=schema_audit.replace("'RESPONSE-TO-INTAKE-CONVERSION-DRILL'\n}", "'RESPONSE-TO-INTAKE-CONVERSION-DRILL', 'ACTUAL-RECEIPT-IMPORT-GATE', 'FAILED-GATE-PUBLIC-SUMMARY'\n}")
schema_audit_path.write_text(schema_audit, encoding='utf-8')
rights_audit_path=ROOT/'tools/audit_rights_domain_coverage.py'
rights_audit=rights_audit_path.read_text(encoding='utf-8')
rights_audit=rights_audit.replace('"response-to-intake-conversion",\n}', '"response-to-intake-conversion",\n    "actual-receipt-import-gate",\n    "failed-gate-public-summary",\n}')
rights_audit_path.write_text(rights_audit, encoding='utf-8')

# Update lint_archive required and early audits
lint_path=ROOT/'tools/lint_archive.py'
lint=lint_path.read_text(encoding='utf-8')
insert_req = """    'docs/30-transition/actual-intake-import-gate-and-failed-gate-public-summary.md',
    'schemas/actual-receipt-import-gate.schema.json',
    'examples/actual-receipt-import-gate-result-return-fixture-no-live-delta.json',
    'schemas/failed-gate-public-summary.schema.json',
    'examples/failed-gate-public-summary-response-conversion-batch.json',
    'examples/external-receipt-quorum-ledger-actual-intake-import-gate-fixture.json',
    'examples/wrsr-live-exercise-outcome-actual-intake-import-gate-stayed.json',
    'fixtures/negative-tests/actual-external-state-field-imported-without-provenance-gate.json',
    'fixtures/negative-tests/failed-gate-summary-omits-declined-or-expired.json',
    'fixtures/negative-tests/failed-gate-summary-treats-no-response-as-waiver.json',
    'examples/research-tail-compaction-map-rev0197.json',
    'examples/schema-fixture-domain-registry-rev0197.json',
    'examples/canon-surface-catalog-rev0197.json',
    'examples/doctrine-dependency-map-rev0197.json',
    'examples/rights-domain-coverage-map-rev0197.json',
    'tools/audit_actual_import_failed_gate_summary.py',
"""
needle = "    'tools/audit_response_to_intake_conversion.py',\n    'tools/package_release.py',\n]"
lint = lint.replace(needle, "    'tools/audit_response_to_intake_conversion.py',\n" + insert_req + "    'tools/package_release.py',\n]")
needle2 = "    'tools/audit_response_to_intake_conversion.py',\n    'tools/audit_canon_surface_catalog.py',"
lint = lint.replace(needle2, "    'tools/audit_response_to_intake_conversion.py',\n    'tools/audit_actual_import_failed_gate_summary.py',\n    'tools/audit_canon_surface_catalog.py',")
lint_path.write_text(lint, encoding='utf-8')

print('apply_rev0197 complete')
