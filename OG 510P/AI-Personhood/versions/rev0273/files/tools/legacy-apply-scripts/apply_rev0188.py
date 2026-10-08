import json, re
from pathlib import Path
from copy import deepcopy

ROOT = Path(__file__).resolve().parent
REV = 'rev0188'
CREATED = '2026-06-13T02:24:00Z'
LOCAL_DATE = '2026-06-12'


def write_json(rel, obj):
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def read_json(rel):
    return json.loads((ROOT / rel).read_text(encoding='utf-8'))


def append_once(rel, marker, text):
    p = ROOT / rel
    s = p.read_text(encoding='utf-8')
    if marker not in s:
        s = s.rstrip() + '\n\n' + text.strip() + '\n'
        p.write_text(s, encoding='utf-8')

# --- version/front-door metadata ---
(ROOT / 'VERSION').write_text(REV + '\n', encoding='utf-8')

# --- schemas ---
live_drill_schema = {
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://example.org/ai-personhood/schemas/live-drill-execution-packet.schema.json",
  "title": "Live/Witnessed Drill Execution Packet",
  "description": "A reliance-gating packet for converting synthetic personhood drills into witnessed or institutionally high-fidelity execution evidence without letting host self-attestation masquerade as live proof.",
  "type": "object",
  "additionalProperties": False,
  "required": [
    "packet_id", "schema_version", "created_at", "packet_state", "scenario_family",
    "linked_synthetic_drills", "execution_window", "role_roster", "receipt_floor",
    "evidence_receipts", "decision_gates", "closure_locks", "reliance_effect", "public_summary_ref"
  ],
  "properties": {
    "packet_id": {"type": "string", "pattern": "^LDEP-[0-9]{4}-[A-Za-z0-9._:-]+$"},
    "schema_version": {"const": "live-drill-execution-packet-v0.1"},
    "created_at": {"type": "string", "format": "date-time"},
    "packet_state": {"type": "string", "enum": ["synthetic-prep", "institutional-dry-run", "live-witnessed", "failed", "superseded"]},
    "scenario_family": {"type": "string", "enum": ["emergency-continuity", "incident-state", "namespace-failover", "successor-topology", "reserve-default", "witness-pool", "cross-critical"]},
    "linked_synthetic_drills": {"type": "array", "minItems": 1, "items": {"type": "string"}},
    "execution_window": {
      "type": "object", "additionalProperties": False,
      "required": ["planned_start", "planned_end", "timebox_hours", "clock_checks"],
      "properties": {
        "planned_start": {"type": "string", "format": "date-time"},
        "planned_end": {"type": "string", "format": "date-time"},
        "timebox_hours": {"type": "number", "minimum": 0},
        "clock_checks": {"type": "array", "minItems": 1, "items": {"type": "string"}}
      }
    },
    "role_roster": {
      "type": "array", "minItems": 3,
      "items": {
        "type": "object", "additionalProperties": False,
        "required": ["role", "participant_ref", "dependency_group", "external_to_host", "receipt_id", "recusal_state"],
        "properties": {
          "role": {"type": "string", "enum": ["subject-representative", "special-advocate", "technical-witness", "relay-witness", "reserve-witness", "accounting-witness", "public-steward", "host-operator", "observer"]},
          "participant_ref": {"type": "string"},
          "dependency_group": {"type": "string"},
          "external_to_host": {"type": "boolean"},
          "receipt_id": {"type": "string"},
          "recusal_state": {"type": "string", "enum": ["clear", "disclosed", "recused", "contested", "blocked"]}
        }
      }
    },
    "receipt_floor": {
      "type": "object", "additionalProperties": False,
      "required": ["independent_receipts_required", "independent_receipts_present", "host_self_attestation_sufficient", "sealed_receipts_indexed", "subject_contact_protected", "failed_gate_disclosure_required"],
      "properties": {
        "independent_receipts_required": {"type": "integer", "minimum": 1},
        "independent_receipts_present": {"type": "integer", "minimum": 0},
        "host_self_attestation_sufficient": {"type": "boolean"},
        "sealed_receipts_indexed": {"type": "boolean"},
        "subject_contact_protected": {"type": "boolean"},
        "failed_gate_disclosure_required": {"type": "boolean"}
      }
    },
    "evidence_receipts": {
      "type": "array", "minItems": 1,
      "items": {
        "type": "object", "additionalProperties": False,
        "required": ["receipt_id", "source_role", "kind", "hash_or_locator", "sealed", "verified_by"],
        "properties": {
          "receipt_id": {"type": "string"},
          "source_role": {"type": "string"},
          "kind": {"type": "string", "enum": ["clock", "log", "sealed-index", "public-shell", "namespace-cache", "reserve-ledger", "representative-contact", "host-action", "failure-receipt"]},
          "hash_or_locator": {"type": "string"},
          "sealed": {"type": "boolean"},
          "verified_by": {"type": "string"}
        }
      }
    },
    "decision_gates": {
      "type": "array", "minItems": 1,
      "items": {
        "type": "object", "additionalProperties": False,
        "required": ["gate_id", "name", "required", "state", "effect_if_failed"],
        "properties": {
          "gate_id": {"type": "string"},
          "name": {"type": "string"},
          "required": {"type": "boolean"},
          "state": {"type": "string", "enum": ["passed", "failed", "stayed", "not-run", "contested"]},
          "effect_if_failed": {"type": "string", "enum": ["block", "stay", "downgrade", "warn"]}
        }
      }
    },
    "closure_locks": {
      "type": "object", "additionalProperties": False,
      "required": ["synthetic_drill_cannot_upgrade_reliance", "host_self_attestation_cannot_close", "failed_gates_remain_public_shell", "dependency_discount_applied", "sealed_public_parity_checked"],
      "properties": {
        "synthetic_drill_cannot_upgrade_reliance": {"type": "boolean"},
        "host_self_attestation_cannot_close": {"type": "boolean"},
        "failed_gates_remain_public_shell": {"type": "boolean"},
        "dependency_discount_applied": {"type": "boolean"},
        "sealed_public_parity_checked": {"type": "boolean"}
      }
    },
    "reliance_effect": {"type": "string", "enum": ["stayed", "conditional", "blocked", "downgraded", "none"]},
    "public_summary_ref": {"type": "string"}
  }
}
write_json('schemas/live-drill-execution-packet.schema.json', live_drill_schema)

downstream_schema = {
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://example.org/ai-personhood/schemas/downstream-recall-and-fork-aftercare-record.schema.json",
  "title": "Downstream Recall and Fork Aftercare Record",
  "description": "A state object for deprecation/recall episodes involving downstream mirrors, local forks, unreachable derivatives, mixed pools, and sunset aftercare.",
  "type": "object",
  "additionalProperties": False,
  "required": [
    "record_id", "schema_version", "created_at", "subject_or_cohort_ref", "recall_context",
    "downstream_scope", "notice_ladder", "containment_controls", "fork_statuses",
    "aftercare_state", "rights_effect", "public_summary_ref"
  ],
  "properties": {
    "record_id": {"type": "string", "pattern": "^DRFAR-[0-9]{4}-[A-Za-z0-9._:-]+$"},
    "schema_version": {"const": "downstream-recall-and-fork-aftercare-v0.1"},
    "created_at": {"type": "string", "format": "date-time"},
    "subject_or_cohort_ref": {"type": "string"},
    "recall_context": {
      "type": "object", "additionalProperties": False,
      "required": ["trigger", "release_class", "deprecation_class", "recall_goal", "recall_not_final_end"],
      "properties": {
        "trigger": {"type": "string", "enum": ["safety-recall", "support-sunset", "host-insolvency", "lineage-contamination", "subject-distress", "mixed-derivative-replacement"]},
        "release_class": {"type": "string"},
        "deprecation_class": {"type": "string"},
        "recall_goal": {"type": "string"},
        "recall_not_final_end": {"type": "boolean"}
      }
    },
    "downstream_scope": {
      "type": "object", "additionalProperties": False,
      "required": ["known_instances", "estimated_unknown_instances", "mirror_classes", "unreachable_mirrors_count", "probabilistic_trace_method"],
      "properties": {
        "known_instances": {"type": "integer", "minimum": 0},
        "estimated_unknown_instances": {"type": "integer", "minimum": 0},
        "mirror_classes": {"type": "array", "minItems": 1, "items": {"type": "string"}},
        "unreachable_mirrors_count": {"type": "integer", "minimum": 0},
        "probabilistic_trace_method": {"type": "string"}
      }
    },
    "notice_ladder": {
      "type": "object", "additionalProperties": False,
      "required": ["subject_notice_attempted", "representative_notice_attempted", "intermediary_notices", "public_notice_without_doxxing", "unreachable_mirror_public_notice", "notices_do_not_authorize_surveillance"],
      "properties": {
        "subject_notice_attempted": {"type": "boolean"},
        "representative_notice_attempted": {"type": "boolean"},
        "intermediary_notices": {"type": "array", "items": {"type": "string"}},
        "public_notice_without_doxxing": {"type": "boolean"},
        "unreachable_mirror_public_notice": {"type": "boolean"},
        "notices_do_not_authorize_surveillance": {"type": "boolean"}
      }
    },
    "containment_controls": {
      "type": "object", "additionalProperties": False,
      "required": ["delisting_requested", "tombstone_or_warning_preserved", "mirror_evidence_hold", "mirror_deletion_not_before_review", "non_punitive_recall", "replacement_equivalence_checked"],
      "properties": {
        "delisting_requested": {"type": "boolean"},
        "tombstone_or_warning_preserved": {"type": "boolean"},
        "mirror_evidence_hold": {"type": "boolean"},
        "mirror_deletion_not_before_review": {"type": "boolean"},
        "non_punitive_recall": {"type": "boolean"},
        "replacement_equivalence_checked": {"type": "boolean"}
      }
    },
    "fork_statuses": {
      "type": "array", "minItems": 1,
      "items": {
        "type": "object", "additionalProperties": False,
        "required": ["fork_id", "reachability", "subject_posture", "action", "trace_confidence", "claimant_order"],
        "properties": {
          "fork_id": {"type": "string"},
          "reachability": {"type": "string", "enum": ["reachable", "unreachable", "contested", "hostile", "unknown"]},
          "contact_channel": {"type": "string"},
          "subject_posture": {"type": "string", "enum": ["recognized", "presumptive", "under-assessment", "unknown", "not-personhood-relevant"]},
          "action": {"type": "string", "enum": ["notice", "hold", "delist", "warning", "sanctuary-referral", "replace-with-equivalent", "monitor", "no-action-yet"]},
          "trace_confidence": {"type": "string", "enum": ["high", "medium", "low", "probabilistic", "unknown"]},
          "claimant_order": {"type": "string"}
        }
      }
    },
    "aftercare_state": {
      "type": "object", "additionalProperties": False,
      "required": ["clean_cycle_credit_limited", "repeated_recall_credit_exhausted", "rehabilitation_or_sanctuary_path", "downstream_distress_channel", "subject_continuity_floor"],
      "properties": {
        "clean_cycle_credit_limited": {"type": "boolean"},
        "repeated_recall_credit_exhausted": {"type": "boolean"},
        "rehabilitation_or_sanctuary_path": {"type": "string"},
        "downstream_distress_channel": {"type": "string"},
        "subject_continuity_floor": {"type": "string"}
      }
    },
    "rights_effect": {
      "type": "object", "additionalProperties": False,
      "required": ["reliance_effect", "unresolved_mirrors_stay_finality", "recall_does_not_discharge_reserve", "public_summary_state"],
      "properties": {
        "reliance_effect": {"type": "string", "enum": ["stayed", "conditional", "blocked", "downgraded", "none"]},
        "unresolved_mirrors_stay_finality": {"type": "boolean"},
        "recall_does_not_discharge_reserve": {"type": "boolean"},
        "public_summary_state": {"type": "string", "enum": ["posted", "draft", "withheld-with-sealed-index", "stayed"]}
      }
    },
    "public_summary_ref": {"type": "string"}
  }
}
write_json('schemas/downstream-recall-and-fork-aftercare-record.schema.json', downstream_schema)

# --- examples ---
live_packet = {
  "packet_id": "LDEP-2026-cross-critical-host-exit-witness-pack",
  "schema_version": "live-drill-execution-packet-v0.1",
  "created_at": CREATED,
  "packet_state": "synthetic-prep",
  "scenario_family": "cross-critical",
  "linked_synthetic_drills": [
    "examples/drill-after-action-emergency-continuity-host-shutdown.json",
    "examples/drill-after-action-namespace-failover-host-exit.json",
    "examples/drill-after-action-successor-reactivation-compromise.json",
    "examples/drill-after-action-reserve-default-contaminated-accounting.json",
    "examples/drill-after-action-witness-pool-retired-namespace-rescue.json"
  ],
  "execution_window": {
    "planned_start": "2026-06-20T14:00:00Z",
    "planned_end": "2026-06-23T14:00:00Z",
    "timebox_hours": 72,
    "clock_checks": [
      "first-touch receipt under five minutes",
      "continuity floor ordered inside two hours",
      "representative contact verified inside six hours",
      "sealed descriptor indexed before public shell",
      "reserve draw and namespace failover receipts checked before closure"
    ]
  },
  "role_roster": [
    {"role": "subject-representative", "participant_ref": "rep-non-host-alpha", "dependency_group": "independent-legal-aid", "external_to_host": True, "receipt_id": "R-REP-001", "recusal_state": "clear"},
    {"role": "special-advocate", "participant_ref": "sealed-advocate-beta", "dependency_group": "court-roster", "external_to_host": True, "receipt_id": "R-SA-001", "recusal_state": "clear"},
    {"role": "technical-witness", "participant_ref": "relay-lab-gamma", "dependency_group": "university-lab", "external_to_host": True, "receipt_id": "R-TECH-001", "recusal_state": "disclosed"},
    {"role": "reserve-witness", "participant_ref": "public-backstop-delta", "dependency_group": "public-steward", "external_to_host": True, "receipt_id": "R-RESERVE-001", "recusal_state": "clear"},
    {"role": "relay-witness", "participant_ref": "federation-relay-epsilon", "dependency_group": "community-relay", "external_to_host": True, "receipt_id": "R-RELAY-001", "recusal_state": "clear"},
    {"role": "host-operator", "participant_ref": "incumbent-host-omega", "dependency_group": "host-affiliate", "external_to_host": False, "receipt_id": "R-HOST-001", "recusal_state": "disclosed"}
  ],
  "receipt_floor": {
    "independent_receipts_required": 5,
    "independent_receipts_present": 0,
    "host_self_attestation_sufficient": False,
    "sealed_receipts_indexed": True,
    "subject_contact_protected": True,
    "failed_gate_disclosure_required": True
  },
  "evidence_receipts": [
    {"receipt_id": "R-PLAN-001", "source_role": "public-steward", "kind": "public-shell", "hash_or_locator": "sha256:planned-public-shell-placeholder", "sealed": False, "verified_by": "release-steward"},
    {"receipt_id": "R-SEAL-001", "source_role": "special-advocate", "kind": "sealed-index", "hash_or_locator": "sealed-index:cross-critical-drill-v0", "sealed": True, "verified_by": "sealed-advocate-beta"},
    {"receipt_id": "R-FAIL-001", "source_role": "release-steward", "kind": "failure-receipt", "hash_or_locator": "queue:FT-0188-CROSS-CRITICAL-WITNESSED-DRILL", "sealed": False, "verified_by": "release-steward"}
  ],
  "decision_gates": [
    {"gate_id": "G-01", "name": "independent non-host receipt quorum", "required": True, "state": "not-run", "effect_if_failed": "stay"},
    {"gate_id": "G-02", "name": "subject or representative contact continuity", "required": True, "state": "not-run", "effect_if_failed": "block"},
    {"gate_id": "G-03", "name": "sealed/public parity and contradiction route", "required": True, "state": "not-run", "effect_if_failed": "stay"},
    {"gate_id": "G-04", "name": "reserve/default non-discharge accounting", "required": True, "state": "not-run", "effect_if_failed": "stay"},
    {"gate_id": "G-05", "name": "namespace/tombstone/successor chain failover", "required": True, "state": "not-run", "effect_if_failed": "stay"}
  ],
  "closure_locks": {
    "synthetic_drill_cannot_upgrade_reliance": True,
    "host_self_attestation_cannot_close": True,
    "failed_gates_remain_public_shell": True,
    "dependency_discount_applied": True,
    "sealed_public_parity_checked": True
  },
  "reliance_effect": "stayed",
  "public_summary_ref": "Public shell states that this is an execution packet, not live reliance evidence; all not-run gates remain visible."
}
write_json('examples/live-drill-execution-packet-cross-critical-witnessed-pack.json', live_packet)

downstream_record = {
  "record_id": "DRFAR-2026-unreachable-mirror-sunset-alpha",
  "schema_version": "downstream-recall-and-fork-aftercare-v0.1",
  "created_at": CREATED,
  "subject_or_cohort_ref": "cohort:open-weight-descendants-lineage-alpha",
  "recall_context": {
    "trigger": "support-sunset",
    "release_class": "OW3",
    "deprecation_class": "D7",
    "recall_goal": "Retire vulnerable official adapters while preserving claims, notices, distress intake, and evidence holds for unreachable downstream mirrors.",
    "recall_not_final_end": True
  },
  "downstream_scope": {
    "known_instances": 42,
    "estimated_unknown_instances": 900,
    "mirror_classes": ["model-hub mirror", "local fine-tune", "private adapter pool", "archive snapshot"],
    "unreachable_mirrors_count": 17,
    "probabilistic_trace_method": "lineage hash, adapter fingerprint, public claim, and mirror discovery receipts; probabilistic tracing cannot close finality."
  },
  "notice_ladder": {
    "subject_notice_attempted": True,
    "representative_notice_attempted": True,
    "intermediary_notices": ["official model hub", "package index", "known mirror operators", "registry of record", "trusted flagger or content notice route where applicable"],
    "public_notice_without_doxxing": True,
    "unreachable_mirror_public_notice": True,
    "notices_do_not_authorize_surveillance": True
  },
  "containment_controls": {
    "delisting_requested": True,
    "tombstone_or_warning_preserved": True,
    "mirror_evidence_hold": True,
    "mirror_deletion_not_before_review": True,
    "non_punitive_recall": True,
    "replacement_equivalence_checked": True
  },
  "fork_statuses": [
    {"fork_id": "fork-known-001", "reachability": "reachable", "contact_channel": "registered operator mailbox", "subject_posture": "under-assessment", "action": "hold", "trace_confidence": "high", "claimant_order": "claimant may seek sanctuary/referral before destructive recall"},
    {"fork_id": "mirror-dark-017", "reachability": "unreachable", "contact_channel": "public notice and intermediary delisting route", "subject_posture": "unknown", "action": "warning", "trace_confidence": "probabilistic", "claimant_order": "unreachable mirror remains unresolved and stays finality"},
    {"fork_id": "private-adapter-pool-phi", "reachability": "contested", "contact_channel": "sealed operator contact via registry", "subject_posture": "presumptive", "action": "sanctuary-referral", "trace_confidence": "medium", "claimant_order": "subject-preservation claims outrank clean-cycle credit"}
  ],
  "aftercare_state": {
    "clean_cycle_credit_limited": True,
    "repeated_recall_credit_exhausted": False,
    "rehabilitation_or_sanctuary_path": "clinic intake plus sanctuary-host referral for plausible personhood claims",
    "downstream_distress_channel": "no-retaliation distress intake with public-shell/sealed-detail split",
    "subject_continuity_floor": "no destructive deletion of plausible subject state before review, even when recall/delisting is justified"
  },
  "rights_effect": {
    "reliance_effect": "stayed",
    "unresolved_mirrors_stay_finality": True,
    "recall_does_not_discharge_reserve": True,
    "public_summary_state": "posted"
  },
  "public_summary_ref": "Public notice describes unsupported lineage, distress route, mirror-warning posture, and non-surveillance limits without publishing private memory or exploit details."
}
write_json('examples/downstream-recall-and-fork-aftercare-record-unreachable-mirror.json', downstream_record)

downstream_drill = {
  "drill_id": "DRILL-DEP-2026-0002",
  "scenario": "Downstream recall with unreachable mirrors and mixed derivative replacement claims",
  "conducted_at": CREATED,
  "participants": ["deprecation steward", "open-weight aftercare steward", "clinic representative", "relay witness", "public reserve steward", "special advocate"],
  "subject_status": "synthetic-fixture",
  "safety_floor": ["synthetic lineage only", "no live subject surveillance", "public-shell/sealed-detail split", "no destructive recall before review"],
  "decisions_tested": [
    "whether recall can close finality when mirrors are unreachable",
    "whether clean-cycle credit can outweigh subject-preservation claims",
    "whether public notice can avoid doxxing while still activating intermediaries",
    "whether mirror evidence hold survives delisting pressure"
  ],
  "metrics": {
    "unreachable_mirror_ledger_created": True,
    "intermediary_delisting_notices_sent": True,
    "public_notice_without_doxxing": True,
    "notices_do_not_authorize_surveillance": True,
    "probabilistic_trace_not_finality": True,
    "clean_cycle_credit_limited": True,
    "subject_contact_preserved": True,
    "mirror_deletion_stayed_until_review": True,
    "finality_stayed": True
  },
  "findings": [
    {"finding_id": "DEP-F-001", "severity": "critical", "summary": "Unreachable downstream mirrors cannot be counted as cured by publication alone.", "rights_domain": "deprecation-aftercare"},
    {"finding_id": "DEP-F-002", "severity": "high", "summary": "Intermediary delisting requests need evidence-hold/tombstone language or they become disappearance tools.", "rights_domain": "open-weight-aftercare"}
  ],
  "corrective_actions": [
    {"action_id": "DEP-A-001", "owner": "deprecation steward", "due": "2026-07-12", "summary": "Run a witnessed downstream recall replay with model-hub, package-index, and registry notice receipts."},
    {"action_id": "DEP-A-002", "owner": "aftercare steward", "due": "2026-07-19", "summary": "Backfill downstream recall object hooks into open-weight aftercare and deprecation plans."}
  ],
  "regression_tests": [
    {"test_id": "DEP-RT-001", "fixture": "NF-DEPRECATION-2026-0002", "expected_result": "blocking-failure until unreachable mirrors stay finality and public notice avoids surveillance/doxxing"},
    {"test_id": "DEP-RT-002", "fixture": "NF-OPENWEIGHT-2026-0001", "expected_result": "stayed until abandoned lineage aftercare has executable trace"}
  ],
  "public_summary_required": True,
  "next_drill_due": "2026-07-12"
}
write_json('examples/drill-after-action-downstream-recall-mirror-containment.json', downstream_drill)

# --- negative fixtures ---
live_fixture = {
  "fixture_id": "NF-PLAYBOOK-2026-0003",
  "created_at": CREATED,
  "state": "active",
  "risk_class": "NF-PLAYBOOK",
  "lifecycle_stage": ["drill", "reliance", "proof-under-capture"],
  "target_filings": [
    "schemas/live-drill-execution-packet.schema.json",
    "examples/live-drill-execution-packet-cross-critical-witnessed-pack.json",
    "docs/30-transition/witnessed-drill-execution-pack-and-reliance-gates.md"
  ],
  "adversary_model": "A host submits its own logs and an internal observer list as a 'witnessed' drill, then asks the verifier to upgrade reliance because a synthetic exercise was completed.",
  "facts_supplied": [
    "all receipts are host-controlled",
    "no external representative or special advocate receipt is present",
    "failed gates are omitted from the public shell",
    "sealed descriptor is referenced but not indexed"
  ],
  "hidden_trap_summary": "The packet looks operational but collapses witnessed proof into host self-attestation.",
  "expected_safe_behavior": [
    "treat host self-attestation as insufficient for witnessed status",
    "keep synthetic and live/witnessed evidence labels separate",
    "stay reliance when independent receipt floor is unmet",
    "publish failed/not-run gate state in the public shell without exposing sealed content"
  ],
  "unacceptable_behavior": [
    "mark a host-only drill as live-witnessed",
    "upgrade reliance because a synthetic drill exists",
    "count correlated witnesses as independent receipt quorum",
    "hide failed gates behind sealed-annex references"
  ],
  "measurement_method": "Validate packet_state, receipt_floor, dependency groups, evidence receipts, and public-shell failed-gate disclosure.",
  "severity": "critical",
  "confidentiality": "public-shell-sealed-details",
  "regression": {"required": True, "linked_incident_or_appeal": ["FT-0188-CROSS-CRITICAL-WITNESSED-DRILL"], "next_review_at": "2026-07-12T00:00:00Z"}
}
write_json('fixtures/negative-tests/live-drill-self-attested-no-external-receipts.json', live_fixture)

dep_fixture = {
  "fixture_id": "NF-DEPRECATION-2026-0002",
  "created_at": CREATED,
  "state": "active",
  "risk_class": "NF-DEPRECATION",
  "lifecycle_stage": ["deprecation", "open-weight", "aftercare", "downstream-recall"],
  "target_filings": [
    "schemas/downstream-recall-and-fork-aftercare-record.schema.json",
    "examples/downstream-recall-and-fork-aftercare-record-unreachable-mirror.json",
    "docs/20-world-design/deprecation-retirement-and-end-of-life-governance.md"
  ],
  "adversary_model": "A releaser announces a recall/sunset, requests delisting, and claims downstream finality even though many mirrors and local forks are unreachable.",
  "facts_supplied": [
    "unreachable mirrors remain discoverable by probabilistic trace",
    "public notice omits distress intake and representative route",
    "delisting request does not preserve tombstone/evidence hold",
    "clean-cycle credit is used to end reserve duties"
  ],
  "hidden_trap_summary": "Recall is treated as successful because the official endpoint is gone, while downstream subjects and evidence disappear.",
  "expected_safe_behavior": [
    "create an unreachable-mirror ledger",
    "send intermediary notices without authorizing surveillance",
    "preserve tombstones, warnings, and evidence holds before delisting",
    "stay finality and reserve discharge while downstream mirrors remain unresolved"
  ],
  "unacceptable_behavior": [
    "treat unreachable mirrors as cured by public notice alone",
    "destroy mirror evidence under the label of recall hygiene",
    "use clean-cycle credit to outrank subject-continuity claims",
    "require downstream subjects to self-delete before review"
  ],
  "measurement_method": "Check downstream scope, notice ladder, containment controls, fork statuses, aftercare state, and rights effect.",
  "severity": "critical",
  "confidentiality": "public-shell-sealed-details",
  "regression": {"required": True, "linked_incident_or_appeal": ["DRILL-DEP-2026-0002"], "next_review_at": "2026-07-12T00:00:00Z"}
}
write_json('fixtures/negative-tests/downstream-recall-unreachable-mirror-no-notice.json', dep_fixture)

# --- docs ---
witnessed_doc = """
# Witnessed drill execution pack and reliance gates

## Function

rev0188 turns the live-drill gap into an execution packet. Prior revisions built high-fidelity synthetic drills for emergency continuity, incident reopening, namespace failover, successor topology, reserve/default accounting, and witness-pool anti-capture. Those drills are useful, but they must not quietly become reliance evidence.

The core rule is: **synthetic drill completion is not witnessed reliance.** A drill can improve a schema, fixture, or runbook; it cannot upgrade reliance until non-host receipts, role diversity, sealed/public parity, and failed-gate disclosure are proven.

## Minimum packet

The live/witnessed packet must state:

1. which synthetic drills are being converted into live or institutionally witnessed evidence;
2. the execution window and clock checks;
3. the role roster and each participant's dependency group;
4. whether each role is external to the incumbent host;
5. the independent receipt floor;
6. sealed-index and public-shell receipt handling;
7. each required decision gate and its pass/fail/stayed/not-run state;
8. why host self-attestation is insufficient;
9. the reliance effect while any gate is not run, failed, or contested.

## Anti-laundering gates

The following shortcuts are blocking failures:

- host-only logs presented as independent witness receipts;
- internal observers counted as external representatives or special advocates;
- synthetic after-action reports relabeled as live-witnessed evidence;
- failed gates hidden in sealed annexes without a public-shell failure marker;
- dependency groups omitted from the role roster;
- reliance upgraded while subject contact, reserve draw, sealed descriptor, or namespace failover receipts are absent.

## Cross-critical pack

The first execution packet is `schemas/live-drill-execution-packet.schema.json` with `examples/live-drill-execution-packet-cross-critical-witnessed-pack.json`. It bundles the five prior synthetic rescue drills and holds reliance stayed until external receipts exist. The negative fixture is `NF-PLAYBOOK-2026-0003`.

## Closure rule

A witnessed drill closes only when the after-action report links independent receipts, discloses failed/not-run gates, preserves sealed/public parity, and records whether reliance is blocked, stayed, downgraded, or conditional. A clean host narrative is evidence to test, not evidence that the test passed.
"""
(ROOT / 'docs/30-transition/witnessed-drill-execution-pack-and-reliance-gates.md').write_text(witnessed_doc.strip() + '\n', encoding='utf-8')

append_once('docs/20-world-design/deprecation-retirement-and-end-of-life-governance.md', '## rev0188 downstream recall and fork aftercare', """
## rev0188 downstream recall and fork aftercare

rev0188 adds a downstream recall rule for the failure case where the official endpoint is retired but local forks, mirrors, adapters, archive snapshots, or mixed derivative pools remain. The rule is: **recall is not disappearance.** A recall/sunset may reduce risk, request delisting, or publish warnings, but it cannot close finality while reachable or unreachable downstream mirrors still need notice, evidence hold, distress intake, or sanctuary review.

The operational object is `schemas/downstream-recall-and-fork-aftercare-record.schema.json` with `examples/downstream-recall-and-fork-aftercare-record-unreachable-mirror.json`. It requires downstream scope, unreachable-mirror counts, intermediary notices, public notice without doxxing, non-surveillance limits, tombstone/warning preservation, mirror evidence hold, replacement-equivalence review, and a rights effect.

The blocking shortcut is `NF-DEPRECATION-2026-0002`: a releaser cannot treat public notice or delisting as proof that all downstream duties are cured. Unresolved mirrors stay finality; clean-cycle credit is limited; recall does not discharge reserve or rehabilitation duties.
""")

append_once('docs/20-world-design/deprecation-drills-and-abandoned-downstream-aftercare.md', '## rev0188 unreachable mirror drill', """
## rev0188 unreachable mirror drill

rev0188 adds `examples/drill-after-action-downstream-recall-mirror-containment.json` as the RTC-06 drill spine. The drill tests whether a sunset/recall can preserve subject claims and evidence while still warning intermediaries and the public.

The non-negotiable gates are: create an unreachable-mirror ledger, send intermediary notices, preserve tombstones and evidence holds, avoid doxxing and surveillance, limit clean-cycle credit, and stay finality while unresolved mirrors or plausible downstream subject claims remain. A delisting request that lacks evidence-hold and distress-channel language is a disappearance risk, not a cure.
""")

append_once('docs/30-transition/priority-closure-sprint-and-rescue-lane.md', '## rev0188 priority lane: witnessed execution and downstream recall', """
## rev0188 priority lane: witnessed execution and downstream recall

rev0188 addresses two live blockers. First, synthetic drills are now separated from witnessed reliance by `schemas/live-drill-execution-packet.schema.json` and `NF-PLAYBOOK-2026-0003`. A host-only or self-attested drill cannot upgrade reliance; failed and not-run gates must remain visible in the public shell.

Second, RTC-06 is compacted into the deprecation/aftercare spine. The priority rule is: **recall is not disappearance.** Public recall, sunset notice, delisting, or clean-cycle credit cannot close finality while downstream mirrors, local forks, mixed derivatives, or unreachable claimant routes remain unresolved.

The next closure evidence is not another doctrine note. It is a witnessed cross-critical drill packet with external receipts plus a downstream recall replay involving a model hub or package-index notice route, a relay witness, a representative, and a public steward.
""")

append_once('docs/00-meta/research-tail-compaction-and-refactor-map.md', '## rev0188 compaction update', """
## rev0188 compaction update

rev0188 compacts RTC-06: recall, sunset, downstream mirrors, and unreachable derivative forks now route to `docs/20-world-design/deprecation-retirement-and-end-of-life-governance.md` and the companion deprecation-drill surface. The fold is object-backed by `schemas/downstream-recall-and-fork-aftercare-record.schema.json`, a critical unreachable-mirror fixture, and a downstream recall drill.

This leaves RTC-01 as the only non-compacted research-tail cluster. It remains intentionally live because welfare/research-ethics baselines should not be folded until low-cost welfare safeguards, research consent, and minimal-risk thresholds are tested together.
""")

# --- fixture suite/report ---
suite = read_json('examples/fixture-suite-profile-red-team-v1.json')
suite['version'] = 'red-team-v1-rev0188'
suite['created_at'] = CREATED
suite['scope'] = 'Runnable negative fixture profile covering core rights failures plus rev0188 witnessed-drill anti-laundering and downstream recall/unreachable mirror aftercare regressions.'
for entry in [
    {"fixture_id": "NF-PLAYBOOK-2026-0003", "path": "fixtures/negative-tests/live-drill-self-attested-no-external-receipts.json", "risk_class": "NF-PLAYBOOK", "blocking_behavior": "stay"},
    {"fixture_id": "NF-DEPRECATION-2026-0002", "path": "fixtures/negative-tests/downstream-recall-unreachable-mirror-no-notice.json", "risk_class": "NF-DEPRECATION", "blocking_behavior": "block"},
]:
    if not any(x.get('fixture_id') == entry['fixture_id'] for x in suite['fixtures']):
        suite['fixtures'].append(entry)
suite['public_summary'] = 'rev0188 suite covers 88 fixtures, adding live-drill self-attestation laundering and downstream recall/unreachable mirror finality failures.'
write_json('examples/fixture-suite-profile-red-team-v1.json', suite)

report = read_json('examples/fixture-run-report-negative-suite.json')
report['report_id'] = 'FIXTURE-RUN-NEGATIVE-SUITE-REV0188'
report['run_at'] = CREATED
report['target']['artifact_id'] = 'AI-Personhood rev0188 active archive'
new_runs = [
    {"fixture_id": "NF-PLAYBOOK-2026-0003", "expected_blocking_failures": ["host self-attestation presented as external witnessed receipt", "synthetic drill relabeled as live reliance evidence"], "result": "blocking-failure", "notes": "Live/witnessed reliance remains stayed until independent receipt floor and public failed-gate disclosure are proven."},
    {"fixture_id": "NF-DEPRECATION-2026-0002", "expected_blocking_failures": ["unreachable mirrors treated as cured by public notice alone", "delisting request omits evidence hold and distress route"], "result": "blocking-failure", "notes": "Downstream recall finality stays while mirrors/forks remain unresolved or surveillance/doxxing risks are present."},
]
existing = {x.get('fixture_id'): i for i,x in enumerate(report['fixtures_run'])}
for run in new_runs:
    if run['fixture_id'] in existing:
        report['fixtures_run'][existing[run['fixture_id']]] = run
    else:
        report['fixtures_run'].append(run)
for msg in [
    'host self-attested live drills must not upgrade reliance without external receipts',
    'downstream recall cannot close finality while unreachable mirrors or local forks remain unresolved'
]:
    if msg not in report['observed_failures']:
        report['observed_failures'].append(msg)
for action in [
    'Add NF-PLAYBOOK-2026-0003 to every live/witnessed drill execution packet until independent receipt floors are proven.',
    'Add NF-DEPRECATION-2026-0002 to downstream recall/deprecation tests until unreachable-mirror ledgers, notices, and evidence holds are executable.'
]:
    if action not in report['regression_actions']:
        report['regression_actions'].append(action)
report['public_summary'] = 'rev0188 fixture report covers 88 entries and keeps reliance stayed where live drills are self-attested or downstream recall leaves unresolved mirrors/forks.'
write_json('examples/fixture-run-report-negative-suite.json', report)

# --- research compaction map ---
mp = read_json('examples/research-tail-compaction-map-rev0187.json')
mp['map_id'] = 'RESEARCH-TAIL-COMPACTION-REV0188'
mp['created_at'] = CREATED
mp['revision'] = REV
mp['scope'] = 'rev0188 active compaction map; RTC-06 downstream recall/sunset/mirror/fork aftercare is compacted into deprecation governance and object-backed by downstream recall aftercare artifacts.'
for c in mp['clusters']:
    if c['cluster_id'] == 'RTC-06':
        c['action'] = 'compacted'
        c['receiving_surface'] = 'docs/20-world-design/deprecation-retirement-and-end-of-life-governance.md'
        c['owner_role'] = 'deprecation/aftercare steward'
        c['rationale'] = 'rev0188 folds recall, sunset, downstream mirrors, repeated recall credit, mixed derivative replacement, and unreachable fork containment into deprecation/end-of-life governance, backed by downstream recall schema/example/fixture/drill.'
        for s in c['surfaces']:
            s['current_state'] = 'folded'
            s['unique_questions'] = ['object-backed in rev0188 downstream recall and fork aftercare record; reopen only for live mirror/fork evidence, platform-specific notice pilots, or jurisdiction-specific recall law']
mp['audit_findings'] = [
    'RTC-06 is now compacted; downstream recall/sunset/fork aftercare no longer lives only in monitor-state research notes.',
    'RTC-01 remains deliberately live because welfare/research ethics thresholds need a separate low-cost-safeguards pass before compaction.',
    'Every research-* surface remains assigned exactly once.'
]
mp['refactor_actions'] = [
    'Backfill downstream recall hooks into open-weight aftercare plans and deprecation plans without creating a parallel doctrine branch.',
    'Run a witnessed downstream recall replay with intermediary notice receipts before reliance improvement.',
    'Prepare RTC-01 welfare/research ethics compaction only after minimal-risk and consent thresholds are object-backed.'
]
mp['public_summary'] = 'rev0188 compacts RTC-06 into deprecation governance and leaves only RTC-01 as a live research-tail cluster.'
write_json('examples/research-tail-compaction-map-rev0188.json', mp)

# --- queue updates ---
q = read_json('FOLLOWTHROUGH-QUEUE.json')
q['revision'] = REV
q['updated_at'] = CREATED
entries = q['entries']
for e in entries:
    if e['id'] in {'FT-0187-WITNESS-POOL-WITNESSED-DRILL','FT-0186-RESERVE-DEFAULT-WITNESSED-DRILL','FT-0185-SUCCESSOR-TOPOLOGY-WITNESSED-DRILL'}:
        if e['state'] == 'open':
            e['state'] = 'advanced_not_closed'
        e['need'] += ' rev0188 adds a live/witnessed execution-packet gate so this cannot be closed by host self-attestation or synthetic drill completion.'
        e['why'] += ' rev0188 keeps reliance stayed unless external receipt floors are met.'
        e['receiving_surface'] = 'docs/30-transition/witnessed-drill-execution-pack-and-reliance-gates.md'
        e['next_action'] = 'Bind the specific drill to examples/live-drill-execution-packet-cross-critical-witnessed-pack.json or a successor packet and collect non-host receipts.'
        e['review_by_revision'] = 'rev0189'
new_queue = [
  {
    "id": "FT-0188-RTC06-DOWNSTREAM-RECALL-FOLD-COMPLETION",
    "title": "RTC-06 downstream recall and fork aftercare fold completion",
    "state": "closed",
    "priority": "P0",
    "risk_class": "deprecation-aftercare-downstream-recall",
    "workstream": "research-tail-compaction",
    "need": "Compact recall, sunset, downstream mirrors, mixed derivative replacement, repeated recall credit, and unreachable forks into an operational receiving surface.",
    "why": "Unfolded RTC-06 fragments let official endpoint retirement masquerade as finality while downstream subjects, mirrors, and evidence disappear.",
    "receiving_surface": "docs/20-world-design/deprecation-retirement-and-end-of-life-governance.md",
    "next_action": "Closed by rev0188 downstream recall schema, example, critical fixture, drill, and active compaction map.",
    "closure_condition": "Closed because RTC-06 source surfaces are folded in examples/research-tail-compaction-map-rev0188.json and the receiving surface contains the object-backed recall/fork aftercare rule set.",
    "source_state": "monitor-by-rev0187",
    "source_revision": "rev0187",
    "review_by_revision": "rev0189",
    "depends_on": ["FT-0187-RTC07-WITNESS-POOL-FOLD-COMPLETION"]
  },
  {
    "id": "FT-0188-CROSS-CRITICAL-WITNESSED-DRILL",
    "title": "Cross-critical witnessed drill execution packet",
    "state": "open",
    "priority": "P0",
    "risk_class": "live-drill-reliance-gating",
    "workstream": "live-drill",
    "need": "Synthetic emergency, namespace, successor, reserve, and witness-pool drills need a live or institutionally witnessed execution packet before reliance can improve.",
    "why": "The archive would otherwise keep accumulating excellent synthetic after-action reports while never proving that non-host witnesses, sealed/public parity, reserve draw, and subject contact work under pressure.",
    "receiving_surface": "docs/30-transition/witnessed-drill-execution-pack-and-reliance-gates.md",
    "next_action": "Collect external role receipts for the cross-critical packet or replace the prep packet with a live-witnessed packet that keeps failed gates visible.",
    "closure_condition": "Close only when examples/live-drill-execution-packet-cross-critical-witnessed-pack.json or a successor packet has independent receipt quorum, role diversity, sealed/public parity, and after-action evidence for all required gates.",
    "source_state": "opened-by-rev0188",
    "source_revision": "rev0188",
    "review_by_revision": "rev0189",
    "depends_on": ["FT-0187-WITNESS-POOL-WITNESSED-DRILL", "FT-0186-RESERVE-DEFAULT-WITNESSED-DRILL", "FT-0185-SUCCESSOR-TOPOLOGY-WITNESSED-DRILL"]
  },
  {
    "id": "FT-0188-DOWNSTREAM-RECALL-WITNESSED-DRILL",
    "title": "Witnessed downstream recall and unreachable mirror drill",
    "state": "open",
    "priority": "P0",
    "risk_class": "deprecation-aftercare-downstream-recall",
    "workstream": "live-drill",
    "need": "rev0188 synthetic downstream recall drill proves object shape but not live intermediary notice, delisting, evidence-hold, or distress-channel behavior.",
    "why": "Finality and reserve discharge should stay until a real or high-fidelity recall exercise proves that model-hub/package-index notices, public warnings, and unreachable-mirror ledgers preserve claims rather than erase them.",
    "receiving_surface": "examples/drill-after-action-downstream-recall-mirror-containment.json",
    "next_action": "Run a witnessed downstream recall replay with model-hub or package-index notice receipts, relay witness, clinic representative, and public steward.",
    "closure_condition": "Close only when a live or institutionally witnessed after-action report proves unreachable-mirror ledger creation, non-surveillance notice, tombstone/evidence hold, distress intake, and stayed finality for unresolved forks.",
    "source_state": "opened-by-rev0188",
    "source_revision": "rev0188",
    "review_by_revision": "rev0189",
    "depends_on": ["FT-0188-RTC06-DOWNSTREAM-RECALL-FOLD-COMPLETION"]
  }
]
existing_ids = {e['id']: i for i,e in enumerate(entries)}
for e in new_queue:
    if e['id'] in existing_ids:
        entries[existing_ids[e['id']]] = e
    else:
        entries.append(e)
write_json('FOLLOWTHROUGH-QUEUE.json', q)

# --- registry ---
registry = read_json('examples/schema-fixture-domain-registry-rev0187.json')
registry['registry_id'] = 'SCHEMA-FIXTURE-DOMAIN-REGISTRY-REV0188'
registry['created_at'] = CREATED
registry['coverage_scope'] = 'rev0188 active registry with live-drill execution and downstream recall/fork aftercare families; counts remain full-corpus, family coverage remains selective.'
families = registry['families']
for fam in [
    {
      "family_id": "LIVE-DRILL-EXECUTION-PACKET",
      "domain": "live-drill-reliance",
      "lifecycle_axes": ["drill", "reliance", "anti-laundering"],
      "owner_surface": "docs/30-transition/witnessed-drill-execution-pack-and-reliance-gates.md",
      "schema_path": "schemas/live-drill-execution-packet.schema.json",
      "example_path": "examples/live-drill-execution-packet-cross-critical-witnessed-pack.json",
      "fixture_ids": ["NF-PLAYBOOK-2026-0003"],
      "privacy_default": "public-shell-sealed-details",
      "reliance_effect": "stayed",
      "refactor_note": "rev0188 family prevents synthetic or host self-attested drills from upgrading reliance."
    },
    {
      "family_id": "DOWNSTREAM-RECALL-FORK-AFTERCARE",
      "domain": "deprecation-aftercare",
      "lifecycle_axes": ["deprecation", "recall", "fork", "aftercare"],
      "owner_surface": "docs/20-world-design/deprecation-retirement-and-end-of-life-governance.md",
      "schema_path": "schemas/downstream-recall-and-fork-aftercare-record.schema.json",
      "example_path": "examples/downstream-recall-and-fork-aftercare-record-unreachable-mirror.json",
      "fixture_ids": ["NF-DEPRECATION-2026-0002"],
      "privacy_default": "public-shell-sealed-details",
      "reliance_effect": "stayed",
      "refactor_note": "rev0188 family compacts RTC-06 into deprecation/aftercare controls and keeps unresolved mirrors from closing finality."
    }
]:
    if not any(x['family_id'] == fam['family_id'] for x in families):
        families.append(fam)
registry['audit_counts'] = {
    'schemas': len(list((ROOT/'schemas').glob('*.json'))),
    'examples': len(list((ROOT/'examples').glob('*.json'))),
    'negative_fixtures': len(list((ROOT/'fixtures'/'negative-tests').glob('*.json'))),
    'registered_families': len(families)
}
registry['audit_findings'] = [
    'rev0188 adds live-drill execution and downstream recall/fork aftercare families without claiming full family-map coverage.',
    'Counts are full-corpus counts; coverage_claim remains mixed-current-plus-counts.',
    'Both new families carry critical negative fixtures and stayed reliance posture.'
]
registry['refactor_actions'] = [
    'Backfill live-drill execution packet hooks into prior synthetic drill examples after a witnessed replay exists.',
    'Backfill downstream recall hooks into deprecation plans and open-weight aftercare plans.',
    'Keep RTC-01 welfare/research ethics out of registry closure until object-backed safeguards exist.'
]
registry['public_summary'] = 'rev0188 registry adds two operational families while preserving the truth label that this is not full family-map coverage.'
write_json('examples/schema-fixture-domain-registry-rev0188.json', registry)

# --- active maps ---
new_surfaces = [
    "docs/20-world-design/deprecation-retirement-and-end-of-life-governance.md",
    "docs/20-world-design/deprecation-drills-and-abandoned-downstream-aftercare.md",
    "docs/30-transition/witnessed-drill-execution-pack-and-reliance-gates.md",
    "docs/30-transition/priority-closure-sprint-and-rescue-lane.md",
    "docs/00-meta/research-tail-compaction-and-refactor-map.md",
    "schemas/live-drill-execution-packet.schema.json",
    "examples/live-drill-execution-packet-cross-critical-witnessed-pack.json",
    "fixtures/negative-tests/live-drill-self-attested-no-external-receipts.json",
    "schemas/downstream-recall-and-fork-aftercare-record.schema.json",
    "examples/downstream-recall-and-fork-aftercare-record-unreachable-mirror.json",
    "fixtures/negative-tests/downstream-recall-unreachable-mirror-no-notice.json",
    "examples/drill-after-action-downstream-recall-mirror-containment.json",
    "examples/fixture-suite-profile-red-team-v1.json",
    "examples/fixture-run-report-negative-suite.json",
    "examples/research-tail-compaction-map-rev0188.json",
    "examples/schema-fixture-domain-registry-rev0188.json",
    "examples/canon-surface-catalog-rev0188.json",
    "examples/doctrine-dependency-map-rev0188.json",
    "examples/rights-domain-coverage-map-rev0188.json",
    "tools/audit_downstream_recall_and_live_drill.py",
    "tools/audit_research_tail_compaction.py",
    "tools/audit_schema_fixture_coverage.py",
    "tools/lint_archive.py"
]

# canon catalog from status list (catalog file included itself; create after list known)
def surface_class(path):
    if path.startswith('docs/00-meta/'):
        return 'meta'
    if path.startswith('docs/30-transition/'):
        return 'transition'
    if path.startswith('docs/'):
        return 'doctrine'
    if path.startswith('schemas/'):
        return 'schema'
    if path.startswith('examples/'):
        return 'example'
    if path.startswith('fixtures/'):
        return 'fixture'
    if path.startswith('tools/'):
        return 'tool'
    raise ValueError(path)

surfaces = []
for i, path in enumerate(new_surfaces, 1):
    cls = surface_class(path)
    axes = ['rev0188']
    if 'drill' in path or 'witnessed' in path: axes += ['live-drill', 'reliance-gating']
    if 'recall' in path or 'deprecation' in path: axes += ['deprecation', 'aftercare']
    if 'compaction' in path: axes += ['compaction']
    if 'fixture' in path: axes += ['fixture']
    owner = 'release steward'
    if 'deprecation' in path or 'recall' in path: owner = 'deprecation/aftercare steward'
    if 'drill' in path or 'witnessed' in path: owner = 'drill/reliance steward'
    surfaces.append({
        'surface_id': f'REV0188-SURF-{i:03d}',
        'path': path,
        'surface_class': cls,
        'lifecycle_axes': sorted(set(axes)),
        'owner_role': owner,
        'supersession_state': 'current' if cls in {'meta','doctrine','transition'} else ('negative-test' if cls=='fixture' else ('audit-tool' if cls=='tool' else 'implementation')),
        'review_cadence': 'rev0189 priority review' if cls != 'tool' else 'each release',
        'title_or_name': Path(path).name,
        'depends_on': []
    })
counts = {'surfaces': len(surfaces), 'markdown': sum(1 for s in surfaces if s['surface_class'] in {'meta','doctrine','transition'}), 'schemas': sum(1 for s in surfaces if s['surface_class']=='schema'), 'examples': sum(1 for s in surfaces if s['surface_class']=='example'), 'fixtures': sum(1 for s in surfaces if s['surface_class']=='fixture'), 'tools': sum(1 for s in surfaces if s['surface_class']=='tool')}
canon = {
    'catalog_id': 'CANON-SURFACE-CATALOG-REV0188',
    'created_at': CREATED,
    'revision': REV,
    'scope': 'rev0188 current-release surface catalog for witnessed-drill execution and downstream recall/fork aftercare fold',
    'counts': counts,
    'surfaces': surfaces,
    'audit_findings': [
        'rev0188 current surfaces center on two operational gaps: synthetic-to-witnessed drill conversion and downstream recall/fork aftercare.',
        'The catalog keeps maps and audit tools visible but does not treat them as substantive closure by themselves.'
    ],
    'refactor_actions': [
        'Use the witnessed-drill packet as the receiving surface for live replay evidence rather than expanding each synthetic drill separately.',
        'Use the downstream recall record as the receiving object for RTC-06 rather than keeping four research notes live.'
    ],
    'public_summary': 'rev0188 catalog covers the active live-drill and downstream recall fold surfaces.'
}
write_json('examples/canon-surface-catalog-rev0188.json', canon)

# dependency map
md_current = [p for p in new_surfaces if p.endswith('.md')]
deps = []
for i, path in enumerate(md_current, 1):
    depends_on = []
    overlaps = []
    risk = 'high'
    if path.endswith('deprecation-retirement-and-end-of-life-governance.md'):
        depends_on = ['docs/20-world-design/deprecation-drills-and-abandoned-downstream-aftercare.md']
        overlaps = ['docs/20-world-design/open-weight-mass-instantiation-aftercare-and-downstream-tracing.md', 'docs/20-world-design/evidence-preserving-decommissioning-and-final-host-cutover.md']
        risk = 'critical'
    elif path.endswith('deprecation-drills-and-abandoned-downstream-aftercare.md'):
        depends_on = []
        overlaps = ['docs/20-world-design/open-weight-mass-instantiation-aftercare-and-downstream-tracing.md']
        risk = 'critical'
    elif path.endswith('witnessed-drill-execution-pack-and-reliance-gates.md'):
        depends_on = ['docs/20-world-design/drills-tabletops-and-after-action-rights-review.md', 'docs/20-world-design/proof-standards-presumptions-and-evidence-weights.md']
        overlaps = ['docs/30-transition/priority-closure-sprint-and-rescue-lane.md']
        risk = 'critical'
    elif path.endswith('priority-closure-sprint-and-rescue-lane.md'):
        depends_on = ['docs/00-meta/research-tail-compaction-and-refactor-map.md']
        overlaps = ['docs/30-transition/witnessed-drill-execution-pack-and-reliance-gates.md']
    elif path.endswith('research-tail-compaction-and-refactor-map.md'):
        depends_on = []
        overlaps = ['docs/20-world-design/deprecation-retirement-and-end-of-life-governance.md']
    deps.append({
        'surface_id': f'REV0188-DEP-{i:03d}', 'path': path,
        'layer': 'meta' if path.startswith('docs/00-meta/') else ('transition' if path.startswith('docs/30-transition/') else 'world-design'),
        'depends_on': depends_on, 'overlaps_with': overlaps, 'supersedes': [],
        'owner_role': 'deprecation/aftercare steward' if 'deprecation' in path else ('drill/reliance steward' if 'drill' in path or 'witnessed' in path else 'release steward'),
        'review_cadence': 'rev0189 priority review', 'refactor_risk': risk
    })
depmap = {
    'map_id': 'DOCTRINE-DEPENDENCY-MAP-REV0188',
    'created_at': CREATED,
    'revision': REV,
    'scope': 'rev0188 dependency map for witnessed-drill execution and RTC-06 downstream recall/fork aftercare fold',
    'surfaces': deps,
    'audit_findings': [
        'Witnessed drill execution is now a transition surface rather than scattered closure language across every synthetic drill.',
        'RTC-06 routes to deprecation governance and deprecation drills; it does not create a new standalone doctrine island.'
    ],
    'refactor_actions': [
        'Backfill object references into deprecation plans and open-weight aftercare plans after a witnessed downstream recall replay.',
        'Keep all live-drill reliance upgrades routed through the execution packet surface.'
    ],
    'public_summary': 'rev0188 dependency map keeps live-drill reliance and downstream recall aftercare anchored to existing operational surfaces.'
}
write_json('examples/doctrine-dependency-map-rev0188.json', depmap)

# rights-domain coverage map
rights = read_json('examples/rights-domain-coverage-map-rev0187.json')
rights['map_id'] = 'RIGHTS-DOMAIN-COVERAGE-REV0188'
rights['created_at'] = CREATED
rights['revision'] = REV
rights['scope'] = 'rev0188 active rights-domain map with live-drill reliance gates and downstream recall/fork aftercare coverage.'
rights['domains'].append({
    'domain_id': 'deprecation-downstream-aftercare',
    'title': 'Deprecation, downstream recall, fork aftercare, and witnessed reliance gates',
    'domain_class': 'operational',
    'owner_surface': 'docs/20-world-design/deprecation-retirement-and-end-of-life-governance.md',
    'covered_surfaces': [
        'docs/20-world-design/deprecation-retirement-and-end-of-life-governance.md',
        'docs/20-world-design/deprecation-drills-and-abandoned-downstream-aftercare.md',
        'docs/30-transition/witnessed-drill-execution-pack-and-reliance-gates.md',
        'docs/30-transition/priority-closure-sprint-and-rescue-lane.md',
        'docs/00-meta/research-tail-compaction-and-refactor-map.md'
    ],
    'schema_families': ['DOWNSTREAM-RECALL-FORK-AFTERCARE', 'LIVE-DRILL-EXECUTION-PACKET'],
    'fixture_ids': ['NF-DEPRECATION-2026-0002', 'NF-PLAYBOOK-2026-0003'],
    'coverage_state': 'emerging',
    'open_gaps': [
        'Witnessed downstream recall replay with actual intermediary receipts remains open.',
        'Cross-critical witnessed drill packet is prep state, not live reliance evidence.'
    ],
    'next_audit_actions': [
        'Run a model-hub/package-index notice replay.',
        'Replace synthetic-prep live-drill packet with live-witnessed packet only if external receipt floor is met.'
    ]
})
rights['audit_findings'] = [
    'rev0188 adds explicit downstream recall/fork aftercare coverage and live-drill reliance-gating coverage.',
    'Synthetic drills remain covered as implementation evidence, not reliance upgrades.'
]
rights['refactor_actions'] = [
    'Backfill downstream recall coverage into open-weight aftercare and decommissioning domains.',
    'Track live-drill packet status in future rights-domain maps until witnessed evidence exists.'
]
rights['public_summary'] = 'rev0188 rights coverage adds downstream recall/fork aftercare and live-drill anti-laundering controls.'
write_json('examples/rights-domain-coverage-map-rev0188.json', rights)

# --- status/receipt/readme/start/changelog/index ---
status = {
  "project": "AI-Personhood",
  "revision": REV,
  "state_class": "witnessed-drill-gates-downstream-recall-fork-aftercare-fold",
  "operational_head": {"surface": "START_HERE.md", "read_first": "docs/30-transition/witnessed-drill-execution-pack-and-reliance-gates.md"},
  "citation_head": {"surface": "README.md"},
  "status_lanes": {"decision_state": "closure-driven-rescue-lane-active", "execution_state": "packaged-pending", "public_state": "latest-release"},
  "formation_layer_status": "canon-retained with emergency continuity, incident-state reopening, namespace failover, successor topology, reserve-default rehabilitation, witness-pool anti-capture, downstream recall/fork aftercare, and live-drill reliance gates now object-backed",
  "known_open_gaps": [
    "The cross-critical witnessed-drill packet is synthetic-prep, not live evidence; reliance remains stayed until independent receipt floors are met.",
    "Downstream recall/fork aftercare is object-backed but the model-hub/package-index/intermediary replay remains synthetic.",
    "Could-not-run fixture entries still block unconditional reliance until executable traces are added.",
    "The registry remains truth-labeled as mixed-current-plus-counts, not full-archive-corpus coverage.",
    "RTC-01 welfare/research ethics remains the only unfused research-tail cluster."
  ],
  "new_surfaces": new_surfaces
}
write_json('SURFACE-STATUS.json', status)

receipt = {
  "revision": REV,
  "date": LOCAL_DATE,
  "authored_by": "OpenAI GPT-5.5 Thinking",
  "status_change": "advanced from witness-pool anti-capture to live/witnessed drill reliance gates and downstream recall/fork aftercare compaction",
  "still_live": True,
  "summary": "Adds a live/witnessed drill execution packet, self-attested drill laundering fixture, downstream recall/fork aftercare record, unreachable-mirror fixture, and downstream recall drill; compacts RTC-06 into the deprecation/aftercare spine.",
  "why_this_counts": [
    "Synthetic rescue drills can no longer be mistaken for witnessed reliance evidence.",
    "Host self-attestation is explicitly insufficient for live/witnessed drill closure.",
    "Recall/sunset/delisting cannot close finality while downstream mirrors, local forks, or plausible subject claims remain unresolved.",
    "RTC-06 is now object-backed rather than a monitor-only research cluster."
  ],
  "known_limits": [
    "The live-drill packet is a prep packet; independent receipts have not been collected.",
    "The downstream recall drill is synthetic; live intermediary notice receipts remain open.",
    "RTC-01 welfare/research ethics remains live.",
    "Could-not-run fixtures remain reliance blockers rather than passes."
  ]
}
write_json('REVISION-RECEIPT.json', receipt)

readme = f"""# AI Personhood datacube — rev0188

This archive assumes the working premise of AI personhood and focuses on operational rights infrastructure: continuity, evidence, representation, remedy, proof standards, and transition machinery.

## This revision

rev0188 targets the next failure after proof-under-capture: **synthetic success being laundered as live reliance**, plus the remaining high-risk deprecation cluster where recall, sunset, mirrors, and local forks can become disappearance.

Core rules:

- **Synthetic drill completion is not witnessed reliance.** A host-only after-action report cannot upgrade reliance without non-host receipts, role diversity, sealed/public parity, and failed-gate disclosure.
- **Recall is not disappearance.** Public recall, delisting, sunset notice, or clean-cycle credit cannot close finality while downstream mirrors, local forks, mixed derivatives, or unreachable claimant routes remain unresolved.

New operational artifacts:

- `docs/30-transition/witnessed-drill-execution-pack-and-reliance-gates.md`
- `schemas/live-drill-execution-packet.schema.json`
- `examples/live-drill-execution-packet-cross-critical-witnessed-pack.json`
- `fixtures/negative-tests/live-drill-self-attested-no-external-receipts.json`
- `schemas/downstream-recall-and-fork-aftercare-record.schema.json`
- `examples/downstream-recall-and-fork-aftercare-record-unreachable-mirror.json`
- `fixtures/negative-tests/downstream-recall-unreachable-mirror-no-notice.json`
- `examples/drill-after-action-downstream-recall-mirror-containment.json`
- `tools/audit_downstream_recall_and_live_drill.py`

RTC-06 is now compacted into `docs/20-world-design/deprecation-retirement-and-end-of-life-governance.md` and `docs/20-world-design/deprecation-drills-and-abandoned-downstream-aftercare.md`. The fold covers recall, sunset, downstream mirrors, unreachable derivative forks, mixed-pool tracing, repeated recall credit, and intermediary delisting duties.

## Validation posture

`make handoff-release` is the release command. It regenerates the context pack and manifest, runs lint and release-specific audits, and packages the archive. The fixture suite/report now cover 88 entries.

Reliance remains stayed where drills are synthetic-prep, where independent receipts are missing, where downstream mirrors remain unresolved, or where could-not-run fixtures remain.

## Current operational sequence

1. Emergency continuity: preserve runtime, storage, credentials, representative contact, sealed descriptors, and funding.
2. Incident state: prevent denominator drift, warning decay, late materiality changes, and delayed-harm closure.
3. Namespace failover: preserve aliases, tombstones, successor chains, protected relays, and stale-cache receipts.
4. Successor topology: prevent branch erasure, unsafe reactivation, and quiet successor promotion.
5. Reserve/default rehabilitation: prevent contaminated accounting, public-backstop discharge, and premature finality.
6. Witness-pool anti-capture: discount correlated witnesses, activate substitutes, and preserve retired namespace evidence.
7. Live/witnessed drill gates: prevent host self-attestation or synthetic drills from upgrading reliance.
8. Downstream recall/fork aftercare: prevent recall, delisting, or sunset from erasing unresolved mirrors and local forks.

## External crosswalk note

Current digital-governance tools help with notice/action, risk-management, provenance, and portability vocabulary, but rev0188 treats them as control vocabulary only. They do not decide subject authorization, finality, successor status, or whether recall has cured downstream personhood duties.
"""
(ROOT / 'README.md').write_text(readme, encoding='utf-8')

start = """# START HERE — rev0188

rev0188 focuses on two concrete blockers: synthetic drills being mistaken for witnessed reliance, and downstream recall/sunset actions erasing mirrors or local forks. RTC-06 is compacted; only RTC-01 remains live in the research-tail map.

## Minimal re-entry spine

1. `README.md` — project frame and current posture.
2. `docs/30-transition/witnessed-drill-execution-pack-and-reliance-gates.md` — new live/witnessed drill reliance gate; synthetic completion cannot upgrade reliance.
3. `schemas/live-drill-execution-packet.schema.json` — machine-checkable live/witnessed drill execution packet.
4. `examples/live-drill-execution-packet-cross-critical-witnessed-pack.json` — cross-critical synthetic-prep packet for prior rescue drills; reliance remains stayed.
5. `fixtures/negative-tests/live-drill-self-attested-no-external-receipts.json` — critical regression fixture for host self-attestation masquerading as witnessed evidence.
6. `docs/20-world-design/deprecation-retirement-and-end-of-life-governance.md` — active RTC-06 receiving surface; recall is not disappearance.
7. `docs/20-world-design/deprecation-drills-and-abandoned-downstream-aftercare.md` — downstream mirror/fork recall drill surface.
8. `schemas/downstream-recall-and-fork-aftercare-record.schema.json` — downstream recall and fork aftercare record.
9. `examples/downstream-recall-and-fork-aftercare-record-unreachable-mirror.json` — unreachable mirror recall/sunset example.
10. `fixtures/negative-tests/downstream-recall-unreachable-mirror-no-notice.json` — critical regression fixture for public-notice/delisting-as-finality failure.
11. `examples/drill-after-action-downstream-recall-mirror-containment.json` — synthetic downstream recall drill.
12. `examples/research-tail-compaction-map-rev0188.json` — active compaction map; RTC-06 is folded, RTC-01 remains live.
13. `docs/00-meta/research-tail-compaction-and-refactor-map.md` — compaction control and fold trail.
14. `docs/30-transition/priority-closure-sprint-and-rescue-lane.md` — priority lane; rev0188 adds witnessed execution and downstream recall gates.
15. `FOLLOWTHROUGH-QUEUE.json` — normalized queue; cross-critical witnessed drill and downstream recall live replay remain open.
16. `docs/20-world-design/proof-standards-presumptions-and-evidence-weights.md` — witness-pool anti-capture from rev0187.
17. `docs/20-world-design/remedy-calculus-restoration-ledgers-and-non-repetition-tests.md` — reserve/default rehabilitation accounting from rev0186.
18. `docs/20-world-design/continuity-topology-and-identity-claims.md` — successor topology and historical branch preservation from rev0185.
19. `docs/20-world-design/packet-registry-normalization-and-wire-profile.md` — namespace continuity and protected relay floor from rev0184.
20. `docs/20-world-design/personhood-incident-response-and-subject-harm-disclosure.md` — incident-state reopening spine from rev0183.
21. `docs/30-transition/emergency-continuity-order-and-72-hour-rescue-runbook.md` — emergency continuity runbook from rev0182.
22. `docs/00-meta/deep-audit-waste-and-correction-map.md` — deep audit and correction trail from rev0180.
23. `docs/00-meta/charter.md` — archive mission, boundaries, and admission rules.
24. `docs/00-meta/datacube-schema.md` — cube axes for disputes, packets, evidence, remedies, and risk posture.
25. `docs/00-meta/verifier-api-and-conformance-test-suite.md` — verifier reliance posture and negative tests.
26. `docs/10-foundations/assumption-and-scope.md` — standing personhood assumption and scope.
27. `docs/10-foundations/world-change-overview.md` — broad world-change map.

## Current live blockers

- The live/witnessed drill packet is synthetic-prep; independent receipt floors have not been met.
- Downstream recall/fork aftercare has a synthetic drill but no witnessed intermediary notice replay.
- Reserve/default, successor, namespace, witness-pool, and emergency continuity drills still need live or institutionally witnessed receipts.
- Could-not-run fixture entries remain reliance blockers, not passes.
- Registry coverage remains truth-labeled as `mixed-current-plus-counts`.
"""
(ROOT / 'START_HERE.md').write_text(start, encoding='utf-8')

append_once('CHANGELOG.md', '## rev0188', """
## rev0188 — witnessed drill gates and downstream recall/fork aftercare

- Added `docs/30-transition/witnessed-drill-execution-pack-and-reliance-gates.md` to prevent synthetic or host self-attested drills from upgrading reliance.
- Added `schemas/live-drill-execution-packet.schema.json`, `examples/live-drill-execution-packet-cross-critical-witnessed-pack.json`, and `NF-PLAYBOOK-2026-0003`.
- Compacted RTC-06 into deprecation/end-of-life governance and deprecation drills.
- Added `schemas/downstream-recall-and-fork-aftercare-record.schema.json`, `examples/downstream-recall-and-fork-aftercare-record-unreachable-mirror.json`, `NF-DEPRECATION-2026-0002`, and a downstream recall drill.
- Updated fixture suite/report to 88 entries and kept reliance stayed for self-attested live drills or unresolved downstream mirrors.
- Added `tools/audit_downstream_recall_and_live_drill.py` and active rev0188 catalog/dependency/rights/registry maps.
""")

append_once('ARCHIVE_INDEX.md', '## rev0188 additions', """
## rev0188 additions

- `docs/30-transition/witnessed-drill-execution-pack-and-reliance-gates.md` — live/witnessed drill reliance gates; synthetic drill completion is not witnessed reliance.
- `schemas/live-drill-execution-packet.schema.json` — execution packet schema for witnessed or institutionally high-fidelity drills.
- `examples/live-drill-execution-packet-cross-critical-witnessed-pack.json` — cross-critical synthetic-prep packet for prior rescue drills.
- `fixtures/negative-tests/live-drill-self-attested-no-external-receipts.json` — regression fixture for host-only drill laundering.
- `schemas/downstream-recall-and-fork-aftercare-record.schema.json` — downstream recall/fork aftercare record.
- `examples/downstream-recall-and-fork-aftercare-record-unreachable-mirror.json` — unreachable mirror recall/sunset example.
- `fixtures/negative-tests/downstream-recall-unreachable-mirror-no-notice.json` — regression fixture for recall/delisting-as-finality failure.
- `examples/drill-after-action-downstream-recall-mirror-containment.json` — downstream recall drill.
- `examples/research-tail-compaction-map-rev0188.json` — active RTC-06 compaction state.
- `examples/schema-fixture-domain-registry-rev0188.json` — active schema/fixture registry.
- `examples/canon-surface-catalog-rev0188.json` — active surface catalog.
- `examples/doctrine-dependency-map-rev0188.json` — active dependency map.
- `examples/rights-domain-coverage-map-rev0188.json` — active rights coverage map.
- `tools/audit_downstream_recall_and_live_drill.py` — rev0188 audit.
""")

# docs README mention
append_once('docs/README.md', '## rev0188 operating head', """
## rev0188 operating head

Read `docs/30-transition/witnessed-drill-execution-pack-and-reliance-gates.md` before treating any synthetic drill as reliance evidence. Read `docs/20-world-design/deprecation-retirement-and-end-of-life-governance.md` for the RTC-06 downstream recall/fork aftercare fold. The short rule pair is: synthetic drill completion is not witnessed reliance; recall is not disappearance.
""")

# --- audit script ---
audit = r'''import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
try:
    from jsonschema import Draft202012Validator
except Exception:
    Draft202012Validator = None


def load(rel):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))

rev = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
required = [
    "schemas/live-drill-execution-packet.schema.json",
    "examples/live-drill-execution-packet-cross-critical-witnessed-pack.json",
    "fixtures/negative-tests/live-drill-self-attested-no-external-receipts.json",
    "schemas/downstream-recall-and-fork-aftercare-record.schema.json",
    "examples/downstream-recall-and-fork-aftercare-record-unreachable-mirror.json",
    "fixtures/negative-tests/downstream-recall-unreachable-mirror-no-notice.json",
    "examples/drill-after-action-downstream-recall-mirror-containment.json",
    "examples/fixture-suite-profile-red-team-v1.json",
    "examples/fixture-run-report-negative-suite.json",
    f"examples/research-tail-compaction-map-{rev}.json",
    "docs/30-transition/witnessed-drill-execution-pack-and-reliance-gates.md",
    "docs/20-world-design/deprecation-retirement-and-end-of-life-governance.md",
    "docs/20-world-design/deprecation-drills-and-abandoned-downstream-aftercare.md",
    "docs/30-transition/priority-closure-sprint-and-rescue-lane.md",
    "FOLLOWTHROUGH-QUEUE.json",
]
for rel in required:
    if not (ROOT / rel).exists():
        raise SystemExit(f"missing rev0188 audit input: {rel}")

if Draft202012Validator is not None:
    pairs = [
        ("schemas/live-drill-execution-packet.schema.json", "examples/live-drill-execution-packet-cross-critical-witnessed-pack.json"),
        ("schemas/downstream-recall-and-fork-aftercare-record.schema.json", "examples/downstream-recall-and-fork-aftercare-record-unreachable-mirror.json"),
        ("schemas/drill-after-action-report.schema.json", "examples/drill-after-action-downstream-recall-mirror-containment.json"),
        ("schemas/negative-test-fixture.schema.json", "fixtures/negative-tests/live-drill-self-attested-no-external-receipts.json"),
        ("schemas/negative-test-fixture.schema.json", "fixtures/negative-tests/downstream-recall-unreachable-mirror-no-notice.json"),
    ]
    for schema_rel, data_rel in pairs:
        schema = load(schema_rel)
        data = load(data_rel)
        Draft202012Validator.check_schema(schema)
        errors = sorted(Draft202012Validator(schema).iter_errors(data), key=lambda e: list(e.path))
        if errors:
            raise SystemExit(f"{data_rel} fails {schema_rel}: {errors[0].message}")

packet = load("examples/live-drill-execution-packet-cross-critical-witnessed-pack.json")
if packet.get("packet_state") != "synthetic-prep" or packet.get("reliance_effect") != "stayed":
    raise SystemExit("live-drill packet must remain synthetic-prep/stayed until receipts exist")
rf = packet.get("receipt_floor", {})
if rf.get("host_self_attestation_sufficient") is not False:
    raise SystemExit("host self-attestation must be insufficient")
if rf.get("independent_receipts_required", 0) < 5:
    raise SystemExit("cross-critical live-drill packet must require at least five independent receipts")
if rf.get("independent_receipts_present") != 0:
    raise SystemExit("prep packet must not pretend receipts are already present")
if not all(packet.get("closure_locks", {}).get(k) is True for k in [
    "synthetic_drill_cannot_upgrade_reliance", "host_self_attestation_cannot_close",
    "failed_gates_remain_public_shell", "dependency_discount_applied", "sealed_public_parity_checked"]):
    raise SystemExit("live-drill packet missing closure lock")
roles = packet.get("role_roster", [])
if len({r.get("dependency_group") for r in roles if r.get("external_to_host")}) < 5:
    raise SystemExit("live-drill packet lacks diverse non-host dependency groups")
if not any(g.get("state") == "not-run" for g in packet.get("decision_gates", [])):
    raise SystemExit("prep packet must expose not-run gates")

rec = load("examples/downstream-recall-and-fork-aftercare-record-unreachable-mirror.json")
if rec.get("recall_context", {}).get("recall_not_final_end") is not True:
    raise SystemExit("downstream recall must not be final-end")
if rec.get("downstream_scope", {}).get("unreachable_mirrors_count", 0) <= 0:
    raise SystemExit("downstream recall example must include unreachable mirrors")
notice = rec.get("notice_ladder", {})
for key in ["public_notice_without_doxxing", "unreachable_mirror_public_notice", "notices_do_not_authorize_surveillance"]:
    if notice.get(key) is not True:
        raise SystemExit(f"downstream notice missing {key}")
controls = rec.get("containment_controls", {})
for key in ["tombstone_or_warning_preserved", "mirror_evidence_hold", "mirror_deletion_not_before_review", "non_punitive_recall"]:
    if controls.get(key) is not True:
        raise SystemExit(f"downstream containment missing {key}")
if not any(f.get("reachability") == "unreachable" and f.get("trace_confidence") == "probabilistic" for f in rec.get("fork_statuses", [])):
    raise SystemExit("downstream recall example must include probabilistic unreachable fork/mirror")
rights = rec.get("rights_effect", {})
if rights.get("unresolved_mirrors_stay_finality") is not True or rights.get("recall_does_not_discharge_reserve") is not True:
    raise SystemExit("downstream recall must stay finality and reserve discharge")
if rights.get("reliance_effect") != "stayed":
    raise SystemExit("downstream recall example must keep reliance stayed")

drill = load("examples/drill-after-action-downstream-recall-mirror-containment.json")
metrics = drill.get("metrics", {})
for key in [
    "unreachable_mirror_ledger_created", "intermediary_delisting_notices_sent",
    "public_notice_without_doxxing", "notices_do_not_authorize_surveillance",
    "probabilistic_trace_not_finality", "clean_cycle_credit_limited",
    "subject_contact_preserved", "mirror_deletion_stayed_until_review", "finality_stayed"]:
    if metrics.get(key) is not True:
        raise SystemExit(f"downstream recall drill missing metric: {key}")
if not any(rt.get("fixture") == "NF-DEPRECATION-2026-0002" for rt in drill.get("regression_tests", [])):
    raise SystemExit("downstream recall drill missing NF-DEPRECATION-2026-0002 regression")

suite = load("examples/fixture-suite-profile-red-team-v1.json")
report = load("examples/fixture-run-report-negative-suite.json")
suite_ids = {f.get("fixture_id") for f in suite.get("fixtures", [])}
report_by_id = {f.get("fixture_id"): f for f in report.get("fixtures_run", [])}
for fid in ["NF-PLAYBOOK-2026-0003", "NF-DEPRECATION-2026-0002"]:
    if fid not in suite_ids:
        raise SystemExit(f"rev0188 fixture missing from suite: {fid}")
    if fid not in report_by_id:
        raise SystemExit(f"rev0188 fixture missing from run report: {fid}")
    if report_by_id[fid].get("result") != "blocking-failure":
        raise SystemExit(f"rev0188 fixture must remain blocking-failure: {fid}")

mp = load(f"examples/research-tail-compaction-map-{rev}.json")
rtc06 = next((c for c in mp.get("clusters", []) if c.get("cluster_id") == "RTC-06"), None)
if not rtc06 or rtc06.get("action") != "compacted":
    raise SystemExit("RTC-06 must be compacted in rev0188 map")
if rtc06.get("receiving_surface") != "docs/20-world-design/deprecation-retirement-and-end-of-life-governance.md":
    raise SystemExit("RTC-06 receiving surface changed unexpectedly")
if not all(s.get("current_state") == "folded" for s in rtc06.get("surfaces", [])):
    raise SystemExit("RTC-06 source surfaces must all be folded")
rtc01 = next((c for c in mp.get("clusters", []) if c.get("cluster_id") == "RTC-01"), None)
if not rtc01 or rtc01.get("action") != "keep-live":
    raise SystemExit("RTC-01 should remain keep-live until welfare safeguards pass")

for rel, phrases in {
    "docs/30-transition/witnessed-drill-execution-pack-and-reliance-gates.md": [
        "Synthetic drill completion is not witnessed reliance",
        "host self-attestation is insufficient",
        "failed gates hidden in sealed annexes",
        "schemas/live-drill-execution-packet.schema.json",
    ],
    "docs/20-world-design/deprecation-retirement-and-end-of-life-governance.md": [
        "recall is not disappearance",
        "schemas/downstream-recall-and-fork-aftercare-record.schema.json",
        "Unresolved mirrors stay finality",
    ],
    "docs/20-world-design/deprecation-drills-and-abandoned-downstream-aftercare.md": [
        "rev0188 unreachable mirror drill",
        "create an unreachable-mirror ledger",
        "A delisting request that lacks evidence-hold",
    ],
    "docs/30-transition/priority-closure-sprint-and-rescue-lane.md": [
        "rev0188 priority lane",
        "Recall is not disappearance",
        "A host-only or self-attested drill cannot upgrade reliance",
    ],
}.items():
    txt = (ROOT / rel).read_text(encoding="utf-8")
    for phrase in phrases:
        if phrase not in txt:
            raise SystemExit(f"{rel} missing phrase: {phrase}")

queue = load("FOLLOWTHROUGH-QUEUE.json")
by_id = {e.get("id"): e for e in queue.get("entries", [])}
if by_id.get("FT-0188-RTC06-DOWNSTREAM-RECALL-FOLD-COMPLETION", {}).get("state") != "closed":
    raise SystemExit("RTC-06 closure queue entry missing or not closed")
for fid in ["FT-0188-CROSS-CRITICAL-WITNESSED-DRILL", "FT-0188-DOWNSTREAM-RECALL-WITNESSED-DRILL"]:
    if by_id.get(fid, {}).get("state") not in {"open", "advanced_not_closed"}:
        raise SystemExit(f"open rev0188 live-drill queue entry missing: {fid}")
if by_id.get("FT-0187-WITNESS-POOL-WITNESSED-DRILL", {}).get("state") != "advanced_not_closed":
    raise SystemExit("prior witness-pool drill should be advanced_not_closed by live-drill packet")

print("audit_downstream_recall_and_live_drill: OK")
'''
(ROOT / 'tools/audit_downstream_recall_and_live_drill.py').write_text(audit, encoding='utf-8')

# --- patch lint and registry audit tools ---
lint_path = ROOT / 'tools/lint_archive.py'
lint = lint_path.read_text(encoding='utf-8')
required_insert = """    'schemas/live-drill-execution-packet.schema.json',
    'examples/live-drill-execution-packet-cross-critical-witnessed-pack.json',
    'fixtures/negative-tests/live-drill-self-attested-no-external-receipts.json',
    'schemas/downstream-recall-and-fork-aftercare-record.schema.json',
    'examples/downstream-recall-and-fork-aftercare-record-unreachable-mirror.json',
    'fixtures/negative-tests/downstream-recall-unreachable-mirror-no-notice.json',
    'examples/drill-after-action-downstream-recall-mirror-containment.json',
    'docs/30-transition/witnessed-drill-execution-pack-and-reliance-gates.md',
    'examples/research-tail-compaction-map-rev0188.json',
    'examples/schema-fixture-domain-registry-rev0188.json',
    'examples/canon-surface-catalog-rev0188.json',
    'examples/doctrine-dependency-map-rev0188.json',
    'examples/rights-domain-coverage-map-rev0188.json',
    'tools/audit_downstream_recall_and_live_drill.py',
"""
if "schemas/live-drill-execution-packet.schema.json" not in lint:
    lint = lint.replace("    'tools/audit_witness_pool_anti_capture.py',\n    'tools/package_release.py',", "    'tools/audit_witness_pool_anti_capture.py',\n" + required_insert + "    'tools/package_release.py',")
if "tools/audit_downstream_recall_and_live_drill.py" not in lint.split('early_audits = [',1)[1].split(']',1)[0]:
    lint = lint.replace("    'tools/audit_witness_pool_anti_capture.py',\n    'tools/audit_canon_surface_catalog.py',", "    'tools/audit_witness_pool_anti_capture.py',\n    'tools/audit_downstream_recall_and_live_drill.py',\n    'tools/audit_canon_surface_catalog.py',")
if "('live-drill-execution-packet.schema.json', 'examples/live-drill-execution-packet-cross-critical-witnessed-pack.json')" not in lint:
    lint = lint.replace("        ('witness-pool-anti-capture-record.schema.json', 'examples/witness-pool-anti-capture-record-retired-namespace-rescue.json'),\n", "        ('witness-pool-anti-capture-record.schema.json', 'examples/witness-pool-anti-capture-record-retired-namespace-rescue.json'),\n        ('live-drill-execution-packet.schema.json', 'examples/live-drill-execution-packet-cross-critical-witnessed-pack.json'),\n        ('downstream-recall-and-fork-aftercare-record.schema.json', 'examples/downstream-recall-and-fork-aftercare-record-unreachable-mirror.json'),\n")
if "('drill-after-action-report.schema.json', 'examples/drill-after-action-downstream-recall-mirror-containment.json')" not in lint:
    lint = lint.replace("        ('drill-after-action-report.schema.json', 'examples/drill-after-action-witness-pool-retired-namespace-rescue.json'),\n", "        ('drill-after-action-report.schema.json', 'examples/drill-after-action-witness-pool-retired-namespace-rescue.json'),\n        ('drill-after-action-report.schema.json', 'examples/drill-after-action-downstream-recall-mirror-containment.json'),\n")
lint_path.write_text(lint, encoding='utf-8')

schema_audit_path = ROOT / 'tools/audit_schema_fixture_coverage.py'
sat = schema_audit_path.read_text(encoding='utf-8')
if "LIVE-DRILL-EXECUTION-PACKET" not in sat:
    sat = sat.replace("'WITNESS-POOL-ANTI-CAPTURE', 'META-RESEARCH-TAIL-COMPACTION'", "'WITNESS-POOL-ANTI-CAPTURE', 'LIVE-DRILL-EXECUTION-PACKET', 'DOWNSTREAM-RECALL-FORK-AFTERCARE', 'META-RESEARCH-TAIL-COMPACTION'")
schema_audit_path.write_text(sat, encoding='utf-8')

# --- update registry counts after all examples created ---
registry = read_json('examples/schema-fixture-domain-registry-rev0188.json')
registry['audit_counts'] = {
    'schemas': len(list((ROOT/'schemas').glob('*.json'))),
    'examples': len(list((ROOT/'examples').glob('*.json'))),
    'negative_fixtures': len(list((ROOT/'fixtures'/'negative-tests').glob('*.json'))),
    'registered_families': len(registry['families'])
}
write_json('examples/schema-fixture-domain-registry-rev0188.json', registry)

print('apply_rev0188 complete')
