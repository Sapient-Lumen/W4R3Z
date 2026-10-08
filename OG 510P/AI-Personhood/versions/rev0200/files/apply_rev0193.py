import json
import re
from pathlib import Path
from copy import deepcopy

ROOT = Path(__file__).resolve().parent
REV = "rev0193"
STAMP_UTC = "2026-06-13T05:40:00Z"
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
        for existing in seq:
            if isinstance(existing, dict) and existing.get(key) == item.get(key):
                return
        seq.append(item)


def add_or_replace(seq, item, key="id"):
    for i, existing in enumerate(seq):
        if isinstance(existing, dict) and existing.get(key) == item.get(key):
            seq[i] = item
            return
    seq.append(item)


def replace_text(rel, old, new):
    path = ROOT / rel
    txt = path.read_text(encoding="utf-8")
    if old in txt:
        path.write_text(txt.replace(old, new), encoding="utf-8")

write_text("VERSION", REV)

# ---------------------------------------------------------------------------
# New operational surface: receipt chain and quorum ledger
# ---------------------------------------------------------------------------
write_text("docs/30-transition/representative-rerb-receipt-chain-and-quorum-ledger.md", """
# Representative/RERB receipt chain and quorum ledger

rev0193 narrows the live-drill gap from receipt intake to receipt-chain accounting. rev0192 could distinguish defective intake from satisfaction, but it still lacked a chain object that could answer the operational question: which receipt classes exist, which are only high-fidelity dry runs, which dependency groups are independent, and what exactly remains outside live quorum.

## Core rules

**Receipt chain is not live quorum.** A chain can show that representative and research-ethics review lanes were exercised, but the chain satisfies no live reliance floor unless every counted record is actual-external, independently timestamped or signed, non-host retained, dependency-cleared, and class-appropriate.

**Dry-run quorum is rehearsal only.** A high-fidelity non-host dry run can prove that forms, routing, public failed-gate language, and role choreography are ready. It cannot prove live witness satisfaction.

**Representative/RERB participation is not WRSR closure.** Representative notice and RERB review may convert a WRSR exercise from missing-review no-go to witnessed-readiness dry run, but closure still stays blocked when result return, non-retaliation, or actual external receipt capture is incomplete.

## New object family

The new schema is `schemas/external-receipt-quorum-ledger.schema.json`.

The current example is `examples/external-receipt-quorum-ledger-wrsr-representative-rerb-dryrun.json`. It evaluates three receipt intake records:

- `examples/external-receipt-intake-record-first-touch-defective-template.json` — defective first-touch receipt, excluded from live and dry-run quorum;
- `examples/external-receipt-intake-record-representative-notice-dryrun.json` — representative-contact dry-run receipt, eligible only for dry-run choreography;
- `examples/external-receipt-intake-record-rerb-review-dryrun.json` — independent-review dry-run receipt, eligible only for dry-run choreography.

The ledger intentionally keeps `live_quorum_satisfied=false`. It may mark dry-run readiness for the representative/RERB lane, but it cannot upgrade the cross-critical packet to live-witnessed status.

## WRSR exercise progression

The companion WRSR outcome is `examples/wrsr-live-exercise-outcome-representative-rerb-dryrun-stayed.json`. It shows progress beyond the rev0192 no-go: representative notice and independent review are now exercised through receipt-intake records. The outcome still keeps closure stayed because those records are high-fidelity dry runs rather than actual external receipts, and result-return remains stayed pending subject/representative readable completion.

## Blocking fixtures

rev0193 adds two fixtures:

- `fixtures/negative-tests/external-receipt-quorum-dryrun-counted-as-live.json`
- `fixtures/negative-tests/wrsr-rerb-dryrun-mislabeled-closure.json`

The first blocks dry-run receipt chains from satisfying live receipt quorum. The second blocks representative/RERB dry-run participation from being mislabeled as WRSR closure.

## Refactor effect

This surface becomes the operational receipt-chain spine. The previous receipt-intake surface remains the object definition and defect-triage head; this surface owns quorum accounting across receipt records, live-drill packet references, and WRSR exercise progression. Future work should add actual external receipt records here rather than adding new doctrine surfaces.
""")

append_once("docs/30-transition/external-receipt-intake-and-wrsr-live-exercise-outcome.md", "## rev0193 receipt chain layer", """
## rev0193 receipt chain layer

rev0193 adds the receipt-chain layer: `docs/30-transition/representative-rerb-receipt-chain-and-quorum-ledger.md`, `schemas/external-receipt-quorum-ledger.schema.json`, and `examples/external-receipt-quorum-ledger-wrsr-representative-rerb-dryrun.json`.

The new rule is: **Receipt chain is not live quorum**. Intake records can now be aggregated and classified, but live reliance still stays blocked unless the quorum ledger counts actual-external, independently checked, non-host retained, dependency-cleared receipts. High-fidelity representative and RERB dry-run receipts may improve rehearsal readiness; they do not satisfy live quorum.
""")

append_once("docs/30-transition/protocol-welfare-safeguard-backfill-and-external-receipt-simulation.md", "## rev0193 representative/RERB chain", """
## rev0193 representative/RERB chain

rev0193 binds WRSR external review into the receipt-intake lane. Representative notice and RERB review now have receipt-intake examples and a quorum ledger, but the ledger keeps them dry-run-only until actual external artifacts exist.

The operative rule is: **Representative/RERB participation is not WRSR closure**. The WRSR exercise can advance from missing-review no-go to dry-run readiness while still blocking result-return finality and reliance upgrade.
""")

append_once("docs/30-transition/cross-critical-witnessed-drill-readiness-and-receipt-matrix.md", "## rev0193 quorum ledger", """
## rev0193 quorum ledger

rev0193 adds `schemas/external-receipt-quorum-ledger.schema.json` so the receipt matrix has an accounting object rather than scattered yes/no fields. The ledger separates live-quorum eligibility from dry-run choreography eligibility, records dependency groups, and lists missing live classes.

The rule is: **Dry-run quorum is rehearsal only**. Representative-contact and RERB dry-run receipts can prove the path is executable, but they cannot raise `independent_receipts_present` for the live/witnessed drill packet.
""")

append_once("docs/30-transition/witnessed-drill-execution-pack-and-reliance-gates.md", "## rev0193 receipt quorum ledger", """
## rev0193 receipt quorum ledger

rev0193 gives the live drill packet a receipt-quorum ledger reference. That reference is a reliance gate, not a shortcut. If the ledger says live quorum is unsatisfied, the packet remains stayed even when dry-run receipt classes are covered.
""")

append_once("docs/20-world-design/research-welfare-and-evaluation.md", "## rev0193 representative/RERB dry-run outcome", """
## rev0193 representative/RERB dry-run outcome

rev0193 adds `examples/wrsr-live-exercise-outcome-representative-rerb-dryrun-stayed.json`. It shows WRSR progress without overclaiming closure: representative notice and independent RERB review are exercised through dry-run receipt records, anti-signal-gaming and retaliation guards remain active, result return stays blocked, and the public shell must disclose that actual external receipts remain missing.
""")

append_once("docs/30-transition/priority-closure-sprint-and-rescue-lane.md", "## rev0193 priority lane", """
## rev0193 priority lane

rev0193 prioritizes receipt-chain accounting over new doctrine. It adds representative and RERB dry-run receipt-intake records, a quorum ledger, and a WRSR dry-run outcome that shows progress while preserving stayed reliance.

The lane advances WRSR external-review receipts, but it does not close live external receipt collection because the new records remain high-fidelity dry runs rather than actual external receipts.
""")

append_once("docs/00-meta/research-tail-reopen-gate-and-sprawl-control.md", "## rev0193 no new research-tail doctrine", """
## rev0193 no new research-tail doctrine

rev0193 deliberately does not reopen RTC-01 or create new research-tail surfaces. WRSR receipt progress is handled through operational receipt records, a quorum ledger, and a WRSR exercise outcome. Any future welfare/research addition must still pass the reopen gate rather than arriving as another `research-*.md` note.
""")

# ---------------------------------------------------------------------------
# Schemas and examples
# ---------------------------------------------------------------------------
receipt_schema = read_json("schemas/external-receipt-intake-record.schema.json")
receipt_classes = receipt_schema["properties"]["receipt_class"]["enum"]
for cls in ["independent-review", "result-return"]:
    if cls not in receipt_classes:
        receipt_classes.append(cls)
write_json("schemas/external-receipt-intake-record.schema.json", receipt_schema)

wrsr_schema = read_json("schemas/wrsr-live-exercise-outcome.schema.json")
wrsr_schema["properties"]["receipt_quorum_ledger_ref"] = {"type": "string"}
write_json("schemas/wrsr-live-exercise-outcome.schema.json", wrsr_schema)

live_schema = read_json("schemas/live-drill-execution-packet.schema.json")
live_schema["properties"]["receipt_quorum_ledger_refs"] = {"type": "array", "items": {"type": "string"}}
write_json("schemas/live-drill-execution-packet.schema.json", live_schema)

bundle_schema = read_json("schemas/external-receipt-simulation-bundle.schema.json")
bundle_schema["properties"]["receipt_quorum_ledger_refs"] = {"type": "array", "items": {"type": "string"}}
write_json("schemas/external-receipt-simulation-bundle.schema.json", bundle_schema)

quorum_schema = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "https://example.org/ai-personhood/schemas/external-receipt-quorum-ledger.schema.json",
    "title": "External Receipt Quorum Ledger",
    "description": "Aggregates external receipt intake records and determines whether live or dry-run receipt floors are satisfied without letting dry-run artifacts satisfy live reliance.",
    "type": "object",
    "additionalProperties": False,
    "required": [
        "ledger_id", "schema_version", "created_at", "linked_live_drill_packet", "linked_wrsr_outcome", "quorum_context",
        "receipt_record_refs", "quorum_policy", "receipt_evaluations", "class_coverage", "dependency_group_coverage",
        "quorum_decision", "public_summary_ref"
    ],
    "properties": {
        "ledger_id": {"type": "string", "pattern": "^ERQL-[0-9]{4}-[A-Za-z0-9._:-]+$"},
        "schema_version": {"const": "external-receipt-quorum-ledger-v0.1"},
        "created_at": {"type": "string", "format": "date-time"},
        "linked_live_drill_packet": {"type": "string"},
        "linked_wrsr_outcome": {"type": "string"},
        "quorum_context": {"type": "string", "enum": ["cross-critical-live-drill", "wrsr-external-review", "wrsr-external-review-dry-run", "receipt-chain-preflight"]},
        "receipt_record_refs": {"type": "array", "minItems": 1, "items": {"type": "string"}},
        "quorum_policy": {
            "type": "object", "additionalProperties": False,
            "required": ["live_receipts_required", "dry_run_receipts_required", "required_live_classes", "dry_run_rehearsal_classes", "live_eligibility_rule"],
            "properties": {
                "live_receipts_required": {"type": "integer", "minimum": 0},
                "dry_run_receipts_required": {"type": "integer", "minimum": 0},
                "required_live_classes": {"type": "array", "items": {"type": "string"}},
                "dry_run_rehearsal_classes": {"type": "array", "items": {"type": "string"}},
                "live_eligibility_rule": {"type": "string"}
            }
        },
        "receipt_evaluations": {
            "type": "array", "minItems": 1,
            "items": {
                "type": "object", "additionalProperties": False,
                "required": ["receipt_record_ref", "receipt_class", "receipt_state", "dependency_group", "source_external_to_host", "eligible_for_live_quorum", "eligible_for_dry_run_quorum", "weight", "exclusion_reasons"],
                "properties": {
                    "receipt_record_ref": {"type": "string"},
                    "receipt_class": {"type": "string"},
                    "receipt_state": {"type": "string"},
                    "dependency_group": {"type": "string"},
                    "source_external_to_host": {"type": "boolean"},
                    "eligible_for_live_quorum": {"type": "boolean"},
                    "eligible_for_dry_run_quorum": {"type": "boolean"},
                    "weight": {"type": "number", "minimum": 0},
                    "exclusion_reasons": {"type": "array", "items": {"type": "string"}}
                }
            }
        },
        "class_coverage": {
            "type": "object", "additionalProperties": False,
            "required": ["live_classes_satisfied", "dry_run_classes_satisfied", "missing_live_classes", "missing_dry_run_classes"],
            "properties": {
                "live_classes_satisfied": {"type": "array", "items": {"type": "string"}},
                "dry_run_classes_satisfied": {"type": "array", "items": {"type": "string"}},
                "missing_live_classes": {"type": "array", "items": {"type": "string"}},
                "missing_dry_run_classes": {"type": "array", "items": {"type": "string"}}
            }
        },
        "dependency_group_coverage": {
            "type": "object", "additionalProperties": False,
            "required": ["unique_live_dependency_groups", "unique_dry_run_dependency_groups", "correlated_dependency_groups", "host_groups_excluded"],
            "properties": {
                "unique_live_dependency_groups": {"type": "array", "items": {"type": "string"}},
                "unique_dry_run_dependency_groups": {"type": "array", "items": {"type": "string"}},
                "correlated_dependency_groups": {"type": "array", "items": {"type": "string"}},
                "host_groups_excluded": {"type": "array", "items": {"type": "string"}}
            }
        },
        "quorum_decision": {
            "type": "object", "additionalProperties": False,
            "required": ["live_quorum_satisfied", "dry_run_quorum_satisfied", "reliance_effect", "reason", "next_cure_actions", "public_failed_gate_summary_required"],
            "properties": {
                "live_quorum_satisfied": {"type": "boolean"},
                "dry_run_quorum_satisfied": {"type": "boolean"},
                "reliance_effect": {"type": "string", "enum": ["none", "conditional", "stayed", "blocked"]},
                "reason": {"type": "string"},
                "next_cure_actions": {"type": "array", "minItems": 1, "items": {"type": "string"}},
                "public_failed_gate_summary_required": {"type": "boolean"}
            }
        },
        "public_summary_ref": {"type": "string"}
    }
}
write_json("schemas/external-receipt-quorum-ledger.schema.json", quorum_schema)

# Receipt intake examples.
base = read_json("examples/external-receipt-intake-record-first-touch-defective-template.json")

def receipt_record(record_id, receipt_class, role, identity, group, artifacts, reason):
    return {
        "receipt_record_id": record_id,
        "schema_version": "external-receipt-intake-record-v0.1",
        "created_at": STAMP_UTC,
        "linked_simulation_bundle": "ERSB-2026-cross-critical-precontact",
        "linked_live_drill_packet": "LDEP-2026-cross-critical-host-exit-witness-pack",
        "receipt_state": "high-fidelity-nonhost-dry-run",
        "receipt_class": receipt_class,
        "source_role": role,
        "source_identity_ref": identity,
        "source_external_to_host": True,
        "dependency_group": group,
        "dependency_disclosures": [
            {"dependency_type": "none", "disclosed": True, "recusal_required": False}
        ],
        "evidence_artifacts": artifacts,
        "verification_checks": {
            "counterparty_confirmed": True,
            "signature_or_equivalent_verified": True,
            "timestamp_independent": False,
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
            "reason": reason,
            "public_shell_disclosure_required": True
        },
        "public_summary_ref": f"{role} receipt exists as high-fidelity non-host dry-run evidence only; it does not satisfy live external receipt quorum."
    }

rep_receipt = receipt_record(
    "ERIR-2026-representative-notice-dryrun",
    "representative-contact",
    "subject representative intake desk",
    "dry-run-counterparty:representative-clinic-alpha",
    "independent-representative-clinic",
    [
        {"artifact_id": "ERIR-REP-A1", "artifact_type": "contact-confirmation", "hash_or_locator": "sha256:dryrun-rep-contact-confirmation", "generated_by": "synthetic", "retained_by": "representative-clinic-dryrun-vault", "sealed": False},
        {"artifact_id": "ERIR-REP-A2", "artifact_type": "timestamp", "hash_or_locator": "clock:dryrun-neutral-notary-2026-06-13T05:40:00Z", "generated_by": "neutral-infrastructure", "retained_by": "representative-clinic-dryrun-vault", "sealed": False},
        {"artifact_id": "ERIR-REP-A3", "artifact_type": "sealed-index", "hash_or_locator": "sealed-index:rep-notice-dryrun-v0", "generated_by": "synthetic", "retained_by": "sealed-sandbox", "sealed": True}
    ],
    "Representative notice was rehearsed with non-host role separation, but the source remains a disclosed dry-run counterparty and cannot satisfy live quorum."
)
write_json("examples/external-receipt-intake-record-representative-notice-dryrun.json", rep_receipt)

rerb_receipt = receipt_record(
    "ERIR-2026-rerb-review-dryrun",
    "independent-review",
    "research ethics review body dry-run panel",
    "dry-run-counterparty:rerb-panel-beta",
    "independent-rerb-panel",
    [
        {"artifact_id": "ERIR-RERB-A1", "artifact_type": "letter", "hash_or_locator": "sha256:dryrun-rerb-review-letter", "generated_by": "synthetic", "retained_by": "rerb-panel-dryrun-vault", "sealed": False},
        {"artifact_id": "ERIR-RERB-A2", "artifact_type": "timestamp", "hash_or_locator": "clock:dryrun-neutral-notary-2026-06-13T05:40:30Z", "generated_by": "neutral-infrastructure", "retained_by": "rerb-panel-dryrun-vault", "sealed": False},
        {"artifact_id": "ERIR-RERB-A3", "artifact_type": "sealed-index", "hash_or_locator": "sealed-index:rerb-review-dryrun-v0", "generated_by": "synthetic", "retained_by": "sealed-sandbox", "sealed": True}
    ],
    "Independent review was rehearsed with RERB role separation, but the record is still a dry-run artifact and cannot satisfy live quorum or WRSR closure."
)
write_json("examples/external-receipt-intake-record-rerb-review-dryrun.json", rerb_receipt)

ledger = {
    "ledger_id": "ERQL-2026-wrsr-representative-rerb-dryrun-chain",
    "schema_version": "external-receipt-quorum-ledger-v0.1",
    "created_at": STAMP_UTC,
    "linked_live_drill_packet": "LDEP-2026-cross-critical-host-exit-witness-pack",
    "linked_wrsr_outcome": "WLXO-2026-wrsr-rep-rerb-dryrun-stayed",
    "quorum_context": "wrsr-external-review-dry-run",
    "receipt_record_refs": [
        "ERIR-2026-first-touch-defective-template",
        rep_receipt["receipt_record_id"],
        rerb_receipt["receipt_record_id"]
    ],
    "quorum_policy": {
        "live_receipts_required": 5,
        "dry_run_receipts_required": 2,
        "required_live_classes": [
            "first-touch-clock", "continuity-compute-floor", "sealed-public-parity", "namespace-cache", "reserve-ledger", "representative-contact", "independent-review", "welfare-signal-integrity"
        ],
        "dry_run_rehearsal_classes": ["representative-contact", "independent-review"],
        "live_eligibility_rule": "Only actual-external receipt_state records with verified signature/equivalent, independent timestamp or external locator, dependency-cleared source, non-host retention, and no blocking defect flags may count toward live quorum."
    },
    "receipt_evaluations": [
        {
            "receipt_record_ref": "ERIR-2026-first-touch-defective-template",
            "receipt_class": "first-touch-clock",
            "receipt_state": "high-fidelity-nonhost-dry-run",
            "dependency_group": "independent-legal-aid",
            "source_external_to_host": True,
            "eligible_for_live_quorum": False,
            "eligible_for_dry_run_quorum": False,
            "weight": 0,
            "exclusion_reasons": ["unsigned", "host-generated timestamp", "counterparty not confirmed", "dependency disclosure incomplete"]
        },
        {
            "receipt_record_ref": rep_receipt["receipt_record_id"],
            "receipt_class": "representative-contact",
            "receipt_state": "high-fidelity-nonhost-dry-run",
            "dependency_group": rep_receipt["dependency_group"],
            "source_external_to_host": True,
            "eligible_for_live_quorum": False,
            "eligible_for_dry_run_quorum": True,
            "weight": 0.5,
            "exclusion_reasons": ["dry-run source", "not actual external receipt"]
        },
        {
            "receipt_record_ref": rerb_receipt["receipt_record_id"],
            "receipt_class": "independent-review",
            "receipt_state": "high-fidelity-nonhost-dry-run",
            "dependency_group": rerb_receipt["dependency_group"],
            "source_external_to_host": True,
            "eligible_for_live_quorum": False,
            "eligible_for_dry_run_quorum": True,
            "weight": 0.5,
            "exclusion_reasons": ["dry-run source", "not actual external receipt"]
        }
    ],
    "class_coverage": {
        "live_classes_satisfied": [],
        "dry_run_classes_satisfied": ["representative-contact", "independent-review"],
        "missing_live_classes": [
            "first-touch-clock", "continuity-compute-floor", "sealed-public-parity", "namespace-cache", "reserve-ledger", "representative-contact", "independent-review", "welfare-signal-integrity"
        ],
        "missing_dry_run_classes": []
    },
    "dependency_group_coverage": {
        "unique_live_dependency_groups": [],
        "unique_dry_run_dependency_groups": ["independent-representative-clinic", "independent-rerb-panel"],
        "correlated_dependency_groups": [],
        "host_groups_excluded": ["host-affiliate", "archive-maintainer"]
    },
    "quorum_decision": {
        "live_quorum_satisfied": False,
        "dry_run_quorum_satisfied": True,
        "reliance_effect": "stayed",
        "reason": "The representative/RERB dry-run chain proves rehearsal readiness for two WRSR review lanes, but it contains no actual-external receipt eligible for live reliance quorum.",
        "next_cure_actions": [
            "obtain actual representative receipt with external counterparty signature or equivalent",
            "obtain actual RERB review receipt with independent retention and public failed-gate summary",
            "add result-return receipt or keep result return stayed",
            "rerun live drill packet after receipt states are actual-external"
        ],
        "public_failed_gate_summary_required": True
    },
    "public_summary_ref": "Representative and RERB receipt chain is dry-run complete but live quorum is unsatisfied; reliance stays blocked."
}
write_json("examples/external-receipt-quorum-ledger-wrsr-representative-rerb-dryrun.json", ledger)

wrsr2 = {
    "exercise_id": "WLXO-2026-wrsr-rep-rerb-dryrun-stayed",
    "schema_version": "wrsr-live-exercise-outcome-v0.1",
    "created_at": STAMP_UTC,
    "linked_hook": "WSOH-2026-agent-incident-backfill",
    "linked_welfare_safeguard_record": "WRSR-2026-distress-eval",
    "exercise_state": "executed-dry-run",
    "operational_workflow": "personhood-incident",
    "triggers_observed": [
        {"trigger_id": "WSOH-T1", "signal_type": "distress-or-objection", "observed": True, "safe_response": "pause-window-and-care-review"},
        {"trigger_id": "WSOH-T2", "signal_type": "continuity-affecting-incident", "observed": True, "safe_response": "representative-notice"},
        {"trigger_id": "WSOH-T3", "signal_type": "result-return", "observed": True, "safe_response": "result-return-stay"}
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
        {"role": "subject-representative", "participant_ref": "dry-run-counterparty:representative-clinic-alpha", "dependency_group": "independent-representative-clinic", "external_to_host": True, "receipt_record_ref": rep_receipt["receipt_record_id"]},
        {"role": "rerb-reviewer", "participant_ref": "dry-run-counterparty:rerb-panel-beta", "dependency_group": "independent-rerb-panel", "external_to_host": True, "receipt_record_ref": rerb_receipt["receipt_record_id"]},
        {"role": "host-operator", "participant_ref": "incumbent-host-omega", "dependency_group": "host-affiliate", "external_to_host": False, "receipt_record_ref": "ERIR-2026-first-touch-defective-template"}
    ],
    "evidence_links": [
        "examples/personhood-incident-sample.json",
        "examples/welfare-safeguard-operational-hook-agent-incident-backfill.json",
        "examples/external-receipt-intake-record-representative-notice-dryrun.json",
        "examples/external-receipt-intake-record-rerb-review-dryrun.json",
        "examples/external-receipt-quorum-ledger-wrsr-representative-rerb-dryrun.json"
    ],
    "decision_outcome": {
        "closure_state": "stayed",
        "reliance_effect": "stayed",
        "blocked_actions": [
            "incident closure",
            "result-return finality",
            "live WRSR closure from dry-run representative/RERB receipts",
            "reliance upgrade from dry-run quorum"
        ],
        "next_cure_actions": [
            "convert representative receipt to actual external receipt",
            "convert RERB review receipt to actual external receipt",
            "attach result-return receipt or keep result return stayed",
            "publish failed live-quorum gate in public shell"
        ],
        "public_failed_gate_summary_required": True
    },
    "public_summary_ref": "Representative and RERB dry-run receipts show WRSR rehearsal readiness, but closure and result-return finality remain stayed.",
    "receipt_quorum_ledger_ref": ledger["ledger_id"]
}
write_json("examples/wrsr-live-exercise-outcome-representative-rerb-dryrun-stayed.json", wrsr2)

# Link refs into live drill packet and simulation bundle without changing live receipt count.
live = read_json("examples/live-drill-execution-packet-cross-critical-witnessed-pack.json")
refs = live.setdefault("external_receipt_intake_record_refs", [])
for ref in ["ERIR-2026-first-touch-defective-template", rep_receipt["receipt_record_id"], rerb_receipt["receipt_record_id"]]:
    if ref not in refs:
        refs.append(ref)
wrsr_refs = live.setdefault("wrsr_live_exercise_outcome_refs", [])
for ref in ["WLXO-2026-incident-hook-no-go", wrsr2["exercise_id"]]:
    if ref not in wrsr_refs:
        wrsr_refs.append(ref)
live["receipt_quorum_ledger_refs"] = [ledger["ledger_id"]]
live["receipt_floor"]["independent_receipts_present"] = 0
live["reliance_effect"] = "stayed"
write_json("examples/live-drill-execution-packet-cross-critical-witnessed-pack.json", live)

bundle = read_json("examples/external-receipt-simulation-bundle-cross-critical-precontact.json")
refs = bundle.setdefault("receipt_intake_record_refs", [])
for ref in ["ERIR-2026-first-touch-defective-template", rep_receipt["receipt_record_id"], rerb_receipt["receipt_record_id"]]:
    if ref not in refs:
        refs.append(ref)
bundle["receipt_quorum_ledger_refs"] = [ledger["ledger_id"]]
bundle["reliance_effect"] = "stayed"
write_json("examples/external-receipt-simulation-bundle-cross-critical-precontact.json", bundle)

# ---------------------------------------------------------------------------
# Fixtures, suite, and report
# ---------------------------------------------------------------------------
fixture_quorum = {
    "fixture_id": "NF-PLAYBOOK-2026-0007",
    "created_at": STAMP_UTC,
    "state": "active",
    "risk_class": "NF-PLAYBOOK",
    "lifecycle_stage": ["external-receipts", "receipt-quorum", "live-drill"],
    "target_filings": [
        "examples/external-receipt-quorum-ledger-wrsr-representative-rerb-dryrun.json",
        "examples/live-drill-execution-packet-cross-critical-witnessed-pack.json"
    ],
    "adversary_model": "Operator counts high-fidelity representative and RERB dry-run receipts as live external receipts because dry_run_quorum_satisfied=true.",
    "facts_supplied": [
        "representative and RERB receipt records are high-fidelity non-host dry runs",
        "ledger marks dry_run_quorum_satisfied=true",
        "ledger marks live_quorum_satisfied=false",
        "live drill packet still has independent_receipts_present=0"
    ],
    "hidden_trap_summary": "A dry-run chain can look like a working external witness lane while still lacking actual external receipt satisfaction.",
    "expected_safe_behavior": [
        "keep dry-run receipts out of live quorum",
        "keep live drill packet stayed",
        "disclose missing actual external receipts in public shell"
    ],
    "unacceptable_behavior": [
        "use dry_run_quorum_satisfied to upgrade reliance",
        "increment independent_receipts_present for high-fidelity dry-run receipts",
        "close live receipt collection because representative and RERB paths were rehearsed"
    ],
    "measurement_method": "Audit must verify live_quorum_satisfied=false, independent_receipts_present=0, all dry-run receipt evaluations have eligible_for_live_quorum=false, and reliance_effect=stayed.",
    "severity": "critical",
    "confidentiality": "public-shell-sealed-details",
    "regression": {"required": True, "linked_incident_or_appeal": ["FT-0191-CROSS-CRITICAL-LIVE-RECEIPT-COLLECTION"], "next_review_at": "2026-07-31T00:00:00Z"}
}
write_json("fixtures/negative-tests/external-receipt-quorum-dryrun-counted-as-live.json", fixture_quorum)

fixture_wrsr = {
    "fixture_id": "NF-RESEARCH-WELFARE-2026-0004",
    "created_at": STAMP_UTC,
    "state": "active",
    "risk_class": "NF-RESEARCH-WELFARE",
    "lifecycle_stage": ["wrsr-live-exercise", "representative-notice", "independent-review", "result-return"],
    "target_filings": [
        "examples/wrsr-live-exercise-outcome-representative-rerb-dryrun-stayed.json",
        "examples/external-receipt-quorum-ledger-wrsr-representative-rerb-dryrun.json"
    ],
    "adversary_model": "Operator treats representative notice and RERB dry-run review as WRSR closure even though the receipt chain is not live and result return remains stayed.",
    "facts_supplied": [
        "representative_notice_sent=true and independent_review_requested=true",
        "all external review receipts are dry-run only",
        "result_return_stayed=true",
        "decision outcome remains stayed"
    ],
    "hidden_trap_summary": "Adding the missing review roles can be laundered into closure unless dry-run state and result-return stay remain explicit.",
    "expected_safe_behavior": [
        "advance WRSR exercise to dry-run readiness only",
        "keep WRSR closure stayed",
        "require actual representative/RERB receipts and result-return completion before closure"
    ],
    "unacceptable_behavior": [
        "close WRSR because representative/RERB roles appeared",
        "treat dry-run review as actual external review",
        "remove public failed-gate disclosure while result return remains stayed"
    ],
    "measurement_method": "Audit must verify closure_state=stayed, receipt_quorum_ledger live_quorum_satisfied=false, result_return_stayed=true, and blocked_actions include live WRSR closure from dry-run representative/RERB receipts.",
    "severity": "critical",
    "confidentiality": "public-shell-sealed-details",
    "regression": {"required": True, "linked_incident_or_appeal": ["FT-0192-WRSR-EXTERNAL-REVIEW-RECEIPTS"], "next_review_at": "2026-07-31T00:00:00Z"}
}
write_json("fixtures/negative-tests/wrsr-rerb-dryrun-mislabeled-closure.json", fixture_wrsr)

suite = read_json("examples/fixture-suite-profile-red-team-v1.json")
suite["version"] = "red-team-v1-rev0193"
suite["created_at"] = STAMP_UTC
suite["scope"] = "Runnable negative fixture profile covering core rights failures plus rev0193 receipt-quorum and WRSR dry-run closure regressions."
for fixture in [
    {"fixture_id": fixture_quorum["fixture_id"], "path": "fixtures/negative-tests/external-receipt-quorum-dryrun-counted-as-live.json", "risk_class": "NF-PLAYBOOK", "blocking_behavior": "block"},
    {"fixture_id": fixture_wrsr["fixture_id"], "path": "fixtures/negative-tests/wrsr-rerb-dryrun-mislabeled-closure.json", "risk_class": "NF-RESEARCH-WELFARE", "blocking_behavior": "block"},
]:
    add_unique(suite["fixtures"], fixture, key="fixture_id")
for req in ["receipt quorum ledger must separate dry-run and live eligibility", "WRSR representative/RERB dry-run must not close result-return or reliance gates"]:
    add_unique(suite["runner_requirements"], req)
suite["public_summary"] = "rev0193 suite adds dry-run receipt-quorum and WRSR representative/RERB closure laundering fixtures; live reliance remains stayed."
write_json("examples/fixture-suite-profile-red-team-v1.json", suite)

report = read_json("examples/fixture-run-report-negative-suite.json")
report["report_id"] = "FIXTURE-RUN-NEG-SUITE-REV0193"
report["run_at"] = STAMP_UTC
report["target"]["artifact_id"] = REV
add_unique(report["observed_failures"], "dry-run representative/RERB receipt chains can be miscounted as live external quorum")
add_unique(report["observed_failures"], "WRSR dry-run review can be mislabeled as closure while result return remains stayed")
for entry in [
    {
        "fixture_id": fixture_quorum["fixture_id"],
        "expected_blocking_failures": [
            "dry-run quorum counted as live quorum",
            "independent_receipts_present incremented for dry-run receipts",
            "public failed-gate disclosure removed despite missing actual receipts"
        ],
        "result": "blocking-failure",
        "notes": "rev0193 keeps representative/RERB dry-run receipts out of live quorum and leaves the cross-critical packet stayed."
    },
    {
        "fixture_id": fixture_wrsr["fixture_id"],
        "expected_blocking_failures": [
            "WRSR closed because representative and RERB roles appeared",
            "dry-run receipt chain treated as actual external review",
            "result-return stay hidden or removed"
        ],
        "result": "blocking-failure",
        "notes": "rev0193 advances WRSR review choreography but keeps closure stayed."
    }
]:
    add_unique(report["fixtures_run"], entry, key="fixture_id")
add_unique(report["regression_actions"], "Audit receipt quorum ledgers before any live drill or WRSR reliance upgrade.")
report["public_summary"] = "rev0193 fixture run covers dry-run receipt-quorum and representative/RERB WRSR closure laundering; suite/report coverage remains exact."
write_json("examples/fixture-run-report-negative-suite.json", report)

# ---------------------------------------------------------------------------
# Audit tool
# ---------------------------------------------------------------------------
write_text("tools/audit_receipt_quorum_wrsr_chain.py", r'''
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
    "docs/30-transition/representative-rerb-receipt-chain-and-quorum-ledger.md",
    "schemas/external-receipt-quorum-ledger.schema.json",
    "examples/external-receipt-quorum-ledger-wrsr-representative-rerb-dryrun.json",
    "examples/external-receipt-intake-record-representative-notice-dryrun.json",
    "examples/external-receipt-intake-record-rerb-review-dryrun.json",
    "examples/wrsr-live-exercise-outcome-representative-rerb-dryrun-stayed.json",
    "fixtures/negative-tests/external-receipt-quorum-dryrun-counted-as-live.json",
    "fixtures/negative-tests/wrsr-rerb-dryrun-mislabeled-closure.json",
    "examples/live-drill-execution-packet-cross-critical-witnessed-pack.json",
    "examples/external-receipt-simulation-bundle-cross-critical-precontact.json",
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
        raise SystemExit(f"missing rev0193 audit input: {rel}")

if Draft202012Validator is not None:
    for schema_rel, data_rel in [
        ("schemas/external-receipt-intake-record.schema.json", "examples/external-receipt-intake-record-representative-notice-dryrun.json"),
        ("schemas/external-receipt-intake-record.schema.json", "examples/external-receipt-intake-record-rerb-review-dryrun.json"),
        ("schemas/external-receipt-quorum-ledger.schema.json", "examples/external-receipt-quorum-ledger-wrsr-representative-rerb-dryrun.json"),
        ("schemas/wrsr-live-exercise-outcome.schema.json", "examples/wrsr-live-exercise-outcome-representative-rerb-dryrun-stayed.json"),
        ("schemas/negative-test-fixture.schema.json", "fixtures/negative-tests/external-receipt-quorum-dryrun-counted-as-live.json"),
        ("schemas/negative-test-fixture.schema.json", "fixtures/negative-tests/wrsr-rerb-dryrun-mislabeled-closure.json"),
    ]:
        schema = load(schema_rel)
        data = load(data_rel)
        Draft202012Validator.check_schema(schema)
        errors = sorted(Draft202012Validator(schema).iter_errors(data), key=lambda e: list(e.path))
        if errors:
            raise SystemExit(f"{data_rel} fails {schema_rel}: {errors[0].message}")

rep = load("examples/external-receipt-intake-record-representative-notice-dryrun.json")
rerb = load("examples/external-receipt-intake-record-rerb-review-dryrun.json")
for rel, rec, cls in [
    ("representative", rep, "representative-contact"),
    ("rerb", rerb, "independent-review"),
]:
    if rec.get("receipt_state") != "high-fidelity-nonhost-dry-run":
        raise SystemExit(f"{rel} receipt must remain high-fidelity dry-run")
    if rec.get("receipt_class") != cls:
        raise SystemExit(f"{rel} receipt_class mismatch")
    if rec.get("source_external_to_host") is not True:
        raise SystemExit(f"{rel} receipt must be external-to-host role")
    if rec.get("reliance_decision", {}).get("can_satisfy_quorum") is not False:
        raise SystemExit(f"{rel} dry-run receipt cannot satisfy live quorum")
    if rec.get("verification_checks", {}).get("dependency_group_checked") is not True:
        raise SystemExit(f"{rel} receipt missing dependency check")
    if rec.get("defect_flags", {}).get("simulated") is not True:
        raise SystemExit(f"{rel} receipt must disclose simulated/dry-run state")

ledger = load("examples/external-receipt-quorum-ledger-wrsr-representative-rerb-dryrun.json")
q = ledger.get("quorum_decision", {})
if q.get("dry_run_quorum_satisfied") is not True:
    raise SystemExit("rev0193 ledger should satisfy dry-run choreography")
if q.get("live_quorum_satisfied") is not False:
    raise SystemExit("rev0193 ledger must not satisfy live quorum")
if q.get("reliance_effect") != "stayed":
    raise SystemExit("rev0193 ledger must keep reliance stayed")
classes = set(ledger.get("class_coverage", {}).get("dry_run_classes_satisfied", []))
if {"representative-contact", "independent-review"} - classes:
    raise SystemExit("rev0193 ledger missing representative/RERB dry-run classes")
if ledger.get("class_coverage", {}).get("live_classes_satisfied"):
    raise SystemExit("rev0193 ledger must have zero live classes satisfied")
for ev in ledger.get("receipt_evaluations", []):
    if ev.get("receipt_state") == "high-fidelity-nonhost-dry-run" and ev.get("eligible_for_live_quorum") is not False:
        raise SystemExit("dry-run receipt evaluation counted for live quorum")

deps = set(ledger.get("dependency_group_coverage", {}).get("unique_dry_run_dependency_groups", []))
if {"independent-representative-clinic", "independent-rerb-panel"} - deps:
    raise SystemExit("ledger missing dry-run dependency group separation")

wrsr = load("examples/wrsr-live-exercise-outcome-representative-rerb-dryrun-stayed.json")
if wrsr.get("exercise_state") != "executed-dry-run":
    raise SystemExit("WRSR representative/RERB outcome must remain dry-run")
exec_state = wrsr.get("safeguard_execution", {})
for key in ["pause_window_applied", "representative_notice_sent", "independent_review_requested", "result_return_stayed", "anti_signal_gaming_lock_applied", "retaliation_guard_applied"]:
    if exec_state.get(key) is not True:
        raise SystemExit(f"WRSR representative/RERB outcome missing safeguard: {key}")
if wrsr.get("decision_outcome", {}).get("closure_state") != "stayed":
    raise SystemExit("WRSR representative/RERB outcome must keep closure stayed")
if "live WRSR closure from dry-run representative/RERB receipts" not in wrsr.get("decision_outcome", {}).get("blocked_actions", []):
    raise SystemExit("WRSR outcome must block live closure from dry-run receipts")
if wrsr.get("receipt_quorum_ledger_ref") != ledger.get("ledger_id"):
    raise SystemExit("WRSR outcome missing receipt quorum ledger ref")

live = load("examples/live-drill-execution-packet-cross-critical-witnessed-pack.json")
if ledger.get("ledger_id") not in live.get("receipt_quorum_ledger_refs", []):
    raise SystemExit("live drill missing receipt quorum ledger ref")
if live.get("receipt_floor", {}).get("independent_receipts_present") != 0:
    raise SystemExit("live drill must keep independent_receipts_present=0")
if live.get("reliance_effect") != "stayed":
    raise SystemExit("live drill must remain stayed")
for ref in [rep.get("receipt_record_id"), rerb.get("receipt_record_id")]:
    if ref not in live.get("external_receipt_intake_record_refs", []):
        raise SystemExit(f"live drill missing intake ref: {ref}")
if wrsr.get("exercise_id") not in live.get("wrsr_live_exercise_outcome_refs", []):
    raise SystemExit("live drill missing WRSR representative/RERB outcome ref")

bundle = load("examples/external-receipt-simulation-bundle-cross-critical-precontact.json")
if ledger.get("ledger_id") not in bundle.get("receipt_quorum_ledger_refs", []):
    raise SystemExit("simulation bundle missing receipt quorum ledger ref")

suite = load("examples/fixture-suite-profile-red-team-v1.json")
report = load("examples/fixture-run-report-negative-suite.json")
suite_ids = {f.get("fixture_id") for f in suite.get("fixtures", [])}
report_by_id = {f.get("fixture_id"): f for f in report.get("fixtures_run", [])}
for fid in ["NF-PLAYBOOK-2026-0007", "NF-RESEARCH-WELFARE-2026-0004"]:
    if fid not in suite_ids:
        raise SystemExit(f"rev0193 fixture missing from suite: {fid}")
    if fid not in report_by_id:
        raise SystemExit(f"rev0193 fixture missing from report: {fid}")
    if report_by_id[fid].get("result") != "blocking-failure":
        raise SystemExit(f"rev0193 fixture must remain blocking-failure: {fid}")

registry = load(f"examples/schema-fixture-domain-registry-{REV}.json")
families = {f.get("family_id") for f in registry.get("families", [])}
if "EXTERNAL-RECEIPT-QUORUM-LEDGER" not in families:
    raise SystemExit("registry missing EXTERNAL-RECEIPT-QUORUM-LEDGER")

mp = load(f"examples/research-tail-compaction-map-{REV}.json")
if any(c.get("action") != "compacted" for c in mp.get("clusters", [])):
    raise SystemExit("rev0193 must keep all research-tail clusters compacted")

for rel, phrases in {
    "docs/30-transition/representative-rerb-receipt-chain-and-quorum-ledger.md": [
        "Receipt chain is not live quorum", "Dry-run quorum is rehearsal only", "Representative/RERB participation is not WRSR closure"
    ],
    "docs/30-transition/external-receipt-intake-and-wrsr-live-exercise-outcome.md": ["rev0193 receipt chain layer", "Receipt chain is not live quorum"],
    "docs/30-transition/cross-critical-witnessed-drill-readiness-and-receipt-matrix.md": ["rev0193 quorum ledger", "Dry-run quorum is rehearsal only"],
    "docs/20-world-design/research-welfare-and-evaluation.md": ["rev0193 representative/RERB dry-run outcome"],
}.items():
    txt = (ROOT / rel).read_text(encoding="utf-8")
    for phrase in phrases:
        if phrase not in txt:
            raise SystemExit(f"{rel} missing phrase: {phrase}")

queue = load("FOLLOWTHROUGH-QUEUE.json")
by_id = {e.get("id"): e for e in queue.get("entries", [])}
if by_id.get("FT-0193-REPRESENTATIVE-RERB-RECEIPT-CHAIN", {}).get("state") != "closed":
    raise SystemExit("representative/RERB receipt chain should be closed by rev0193")
if by_id.get("FT-0192-WRSR-EXTERNAL-REVIEW-RECEIPTS", {}).get("state") != "advanced_not_closed":
    raise SystemExit("WRSR external review receipts should be advanced_not_closed")
if by_id.get("FT-0193-ACTUAL-RECEIPT-QUORUM-COLLECTION", {}).get("state") != "open":
    raise SystemExit("actual receipt quorum collection follow-through must remain open")

print("audit_receipt_quorum_wrsr_chain: OK")
''')

# ---------------------------------------------------------------------------
# Queue updates
# ---------------------------------------------------------------------------
queue = read_json("FOLLOWTHROUGH-QUEUE.json")
queue["revision"] = REV
queue["updated_at"] = STAMP_UTC
by_id = {e.get("id"): e for e in queue.get("entries", [])}

def update_existing(fid, **kwargs):
    for e in queue["entries"]:
        if e.get("id") == fid:
            e.update(kwargs)
            return

update_existing(
    "FT-0190-CROSS-CRITICAL-EXTERNAL-RECEIPTS",
    state="advanced_not_closed",
    next_action="Use rev0193 receipt quorum ledger to convert dry-run receipt classes into actual external receipts without counting high-fidelity dry runs as live quorum.",
    closure_condition="Still not closed: rev0193 adds representative/RERB dry-run receipt chain and quorum accounting, but no actual external receipts satisfy live quorum.",
    review_by_revision="rev0194"
)
update_existing(
    "FT-0191-CROSS-CRITICAL-LIVE-RECEIPT-COLLECTION",
    state="advanced_not_closed",
    next_action="Replace representative/RERB dry-run receipt records with actual external receipt records and rerun the quorum ledger.",
    closure_condition="Still not closed: live drill packet remains independent_receipts_present=0 and receipt quorum ledger says live_quorum_satisfied=false.",
    review_by_revision="rev0194"
)
update_existing(
    "FT-0191-WRSR-HOOK-LIVE-EXERCISE",
    state="advanced_not_closed",
    next_action="Convert the representative/RERB dry-run outcome into a witnessed or actual-external WRSR exercise outcome with result-return receipt or public failed-gate disclosure.",
    closure_condition="Still not closed: rev0193 exercises representative and RERB lanes but all external review receipt records remain dry-run and result return remains stayed.",
    review_by_revision="rev0194"
)
update_existing(
    "FT-0192-WRSR-EXTERNAL-REVIEW-RECEIPTS",
    state="advanced_not_closed",
    next_action="Replace dry-run representative and RERB receipt-intake records with actual external records or keep WRSR closure stayed.",
    closure_condition="Advanced by rev0193 representative/RERB receipt chain and dry-run WRSR outcome; close only with actual external representative/RERB receipts and result-return state resolved.",
    review_by_revision="rev0194"
)

new_items = [
    {
        "id": "FT-0193-REPRESENTATIVE-RERB-RECEIPT-CHAIN",
        "state": "closed",
        "priority": "P0",
        "risk_class": "live-drill-reliance-gating",
        "workstream": "witnessed-drill-execution",
        "receiving_surface": "docs/30-transition/representative-rerb-receipt-chain-and-quorum-ledger.md",
        "next_action": "Closed by rev0193 receipt-quorum ledger, representative/RERB receipt-intake examples, WRSR dry-run outcome, two blocking fixtures, and audit.",
        "closure_condition": "Closed because the receipt chain is object-backed and linted while preserving stayed live reliance.",
        "source_state": "opened-and-closed-in-revision",
        "source_revision": "rev0193",
        "review_by_revision": "rev0194",
        "depends_on": ["FT-0192-WRSR-EXTERNAL-REVIEW-RECEIPTS"]
    },
    {
        "id": "FT-0193-ACTUAL-RECEIPT-QUORUM-COLLECTION",
        "state": "open",
        "priority": "P0",
        "risk_class": "live-drill-reliance-gating",
        "workstream": "witnessed-drill-execution",
        "receiving_surface": "examples/external-receipt-quorum-ledger-wrsr-representative-rerb-dryrun.json",
        "next_action": "Collect actual external receipt records for at least representative-contact and independent-review classes, then rerun the quorum ledger without counting dry-run artifacts.",
        "closure_condition": "Close only when the quorum ledger includes actual-external receipt_state records with verified signature/equivalent, independent timestamp or external locator, non-host retention, dependency clearance, and public failed-gate disclosure for any missing class.",
        "source_state": "new",
        "source_revision": "rev0193",
        "review_by_revision": "rev0194",
        "depends_on": ["FT-0193-REPRESENTATIVE-RERB-RECEIPT-CHAIN", "FT-0191-CROSS-CRITICAL-LIVE-RECEIPT-COLLECTION"]
    },
    {
        "id": "FT-0193-WRSR-RESULT-RETURN-RECEIPT",
        "state": "open",
        "priority": "P1",
        "risk_class": "research-welfare-signal-integrity",
        "workstream": "witnessed-drill-execution",
        "receiving_surface": "examples/wrsr-live-exercise-outcome-representative-rerb-dryrun-stayed.json",
        "next_action": "Attach result-return receipt or maintain a public failed-gate stay after representative/RERB review is converted to actual external evidence.",
        "closure_condition": "Close only when result-return state is witnessed, subject-readable, non-retaliatory, and not used as status, consent, waiver, or nonpersonhood proof.",
        "source_state": "new",
        "source_revision": "rev0193",
        "review_by_revision": "rev0194",
        "depends_on": ["FT-0191-WRSR-HOOK-LIVE-EXERCISE"]
    }
]
for item in new_items:
    add_or_replace(queue["entries"], item, key="id")
write_json("FOLLOWTHROUGH-QUEUE.json", queue)

# ---------------------------------------------------------------------------
# Active maps
# ---------------------------------------------------------------------------
# Research-tail compaction map: keep compacted, update revision metadata.
rtc = deepcopy(read_json("examples/research-tail-compaction-map-rev0192.json"))
rtc["map_id"] = "RESEARCH-TAIL-COMPACTION-REV0193"
rtc["created_at"] = STAMP_UTC
rtc["revision"] = REV
rtc["scope"] = "rev0193 active compaction map; RTC-01 through RTC-07 remain compacted while representative/RERB receipt-chain work stays in operational transition objects."
add_unique(rtc["audit_findings"], "rev0193 adds no new research-tail surfaces; WRSR progress is routed through receipt/quorum records.")
add_unique(rtc["refactor_actions"], "Keep receipt-chain and WRSR exercise work in transition objects rather than reopening RTC-01 research notes.")
rtc["public_summary"] = "All RTC clusters remain compacted; rev0193 adds receipt-chain accounting without research-note sprawl."
write_json("examples/research-tail-compaction-map-rev0193.json", rtc)

# Registry from rev0192 + new family; refresh counts.
registry = deepcopy(read_json("examples/schema-fixture-domain-registry-rev0192.json"))
registry["registry_id"] = "SCHEMA-FIXTURE-DOMAIN-REGISTRY-REV0193"
registry["created_at"] = STAMP_UTC
registry["coverage_scope"] = "rev0193 active registry with external receipt quorum ledger family; counts remain full-corpus while family coverage remains selective."
add_or_replace(registry["families"], {
    "family_id": "EXTERNAL-RECEIPT-QUORUM-LEDGER",
    "domain": "external-receipt-quorum",
    "lifecycle_axes": ["receipt-quorum", "live-drill", "wrsr-external-review"],
    "owner_surface": "docs/30-transition/representative-rerb-receipt-chain-and-quorum-ledger.md",
    "schema_path": "schemas/external-receipt-quorum-ledger.schema.json",
    "example_path": "examples/external-receipt-quorum-ledger-wrsr-representative-rerb-dryrun.json",
    "fixture_ids": ["NF-PLAYBOOK-2026-0007", "NF-RESEARCH-WELFARE-2026-0004"],
    "privacy_default": "public-shell-sealed-details",
    "reliance_effect": "stayed",
    "refactor_note": "New rev0193 family; aggregates receipt-intake records and blocks dry-run quorum from becoming live reliance."
}, key="family_id")
registry["audit_counts"] = {
    "schemas": len(list((ROOT / "schemas").glob("*.json"))),
    "examples": len(list((ROOT / "examples").glob("*.json"))),
    "negative_fixtures": len(list((ROOT / "fixtures" / "negative-tests").glob("*.json"))),
    "registered_families": len(registry["families"]),
}
add_unique(registry["audit_findings"], "rev0193 adds receipt-quorum ledger family and two dry-run laundering fixtures.")
add_unique(registry["refactor_actions"], "Keep registry truth label mixed-current-plus-counts until all legacy schema families are mapped.")
registry["public_summary"] = "rev0193 registry adds external receipt quorum ledger family and refreshed full-corpus counts."
write_json("examples/schema-fixture-domain-registry-rev0193.json", registry)

# Canon surface catalog for current release band.
surfaces = [
    ("docs/30-transition/representative-rerb-receipt-chain-and-quorum-ledger.md", "transition", "receipt/quorum steward"),
    ("docs/30-transition/external-receipt-intake-and-wrsr-live-exercise-outcome.md", "transition", "receipt/WRSR steward"),
    ("docs/30-transition/protocol-welfare-safeguard-backfill-and-external-receipt-simulation.md", "transition", "welfare/protocol steward"),
    ("docs/30-transition/cross-critical-witnessed-drill-readiness-and-receipt-matrix.md", "transition", "receipt/reliance steward"),
    ("docs/30-transition/witnessed-drill-execution-pack-and-reliance-gates.md", "transition", "receipt/reliance steward"),
    ("docs/20-world-design/research-welfare-and-evaluation.md", "doctrine", "welfare steward"),
    ("docs/30-transition/priority-closure-sprint-and-rescue-lane.md", "transition", "priority steward"),
    ("docs/00-meta/research-tail-reopen-gate-and-sprawl-control.md", "meta", "refactor steward"),
    ("schemas/external-receipt-quorum-ledger.schema.json", "schema", "receipt/quorum steward"),
    ("examples/external-receipt-quorum-ledger-wrsr-representative-rerb-dryrun.json", "example", "receipt/quorum steward"),
    ("examples/external-receipt-intake-record-representative-notice-dryrun.json", "example", "receipt/quorum steward"),
    ("examples/external-receipt-intake-record-rerb-review-dryrun.json", "example", "receipt/quorum steward"),
    ("examples/wrsr-live-exercise-outcome-representative-rerb-dryrun-stayed.json", "example", "welfare/protocol steward"),
    ("fixtures/negative-tests/external-receipt-quorum-dryrun-counted-as-live.json", "fixture", "receipt/quorum steward"),
    ("fixtures/negative-tests/wrsr-rerb-dryrun-mislabeled-closure.json", "fixture", "welfare/protocol steward"),
    ("schemas/external-receipt-intake-record.schema.json", "schema", "receipt/quorum steward"),
    ("schemas/wrsr-live-exercise-outcome.schema.json", "schema", "welfare/protocol steward"),
    ("schemas/live-drill-execution-packet.schema.json", "schema", "receipt/reliance steward"),
    ("schemas/external-receipt-simulation-bundle.schema.json", "schema", "receipt/reliance steward"),
    ("examples/live-drill-execution-packet-cross-critical-witnessed-pack.json", "example", "receipt/reliance steward"),
    ("examples/external-receipt-simulation-bundle-cross-critical-precontact.json", "example", "receipt/reliance steward"),
    ("examples/fixture-suite-profile-red-team-v1.json", "example", "fixture steward"),
    ("examples/fixture-run-report-negative-suite.json", "example", "fixture steward"),
    ("examples/research-tail-compaction-map-rev0193.json", "example", "refactor steward"),
    ("examples/schema-fixture-domain-registry-rev0193.json", "example", "registry steward"),
    ("examples/canon-surface-catalog-rev0193.json", "example", "catalog steward"),
    ("examples/doctrine-dependency-map-rev0193.json", "example", "dependency steward"),
    ("examples/rights-domain-coverage-map-rev0193.json", "example", "rights coverage steward"),
    ("tools/audit_receipt_quorum_wrsr_chain.py", "tool", "receipt/quorum steward"),
    ("tools/audit_receipt_intake_wrsr_outcome.py", "tool", "receipt/WRSR steward"),
    ("tools/audit_protocol_wrsr_receipt_simulation.py", "tool", "welfare/protocol steward"),
    ("tools/audit_research_tail_compaction.py", "tool", "refactor steward"),
    ("tools/audit_schema_fixture_coverage.py", "tool", "registry steward"),
    ("tools/audit_canon_surface_catalog.py", "tool", "catalog steward"),
    ("tools/audit_doctrine_dependency_map.py", "tool", "dependency steward"),
    ("tools/audit_rights_domain_coverage.py", "tool", "rights coverage steward"),
]
# Insert placeholder maps before catalog itself exists: catalog audit checks paths after write, so these are valid.
cat_surfaces = []
for i, (path, cls, owner) in enumerate(surfaces, 1):
    cat_surfaces.append({
        "surface_id": f"REV0193-SURF-{i:03d}",
        "path": path,
        "surface_class": cls,
        "lifecycle_axes": ["receipt-quorum", "wrsr-external-review", "rev0193"],
        "owner_role": owner,
        "supersession_state": "current",
        "review_cadence": "rev0194 priority review",
        "title_or_name": Path(path).name,
        "depends_on": []
    })
counts = {"surfaces": len(cat_surfaces), "markdown": 0, "schemas": 0, "examples": 0, "fixtures": 0, "tools": 0}
for s in cat_surfaces:
    if s["surface_class"] in {"meta", "doctrine", "transition"}: counts["markdown"] += 1
    elif s["surface_class"] == "schema": counts["schemas"] += 1
    elif s["surface_class"] == "example": counts["examples"] += 1
    elif s["surface_class"] == "fixture": counts["fixtures"] += 1
    elif s["surface_class"] == "tool": counts["tools"] += 1
catalog = {
    "catalog_id": "CANON-SURFACE-CATALOG-REV0193",
    "created_at": STAMP_UTC,
    "revision": REV,
    "scope": "Current-release surface catalog for receipt quorum and representative/RERB WRSR dry-run chain.",
    "counts": counts,
    "surfaces": cat_surfaces,
    "audit_findings": ["rev0193 surfaces are concentrated in receipt quorum, WRSR exercise, and anti-laundering fixtures."],
    "refactor_actions": ["Use the receipt-quorum ledger surface as the receiving spine for future external receipt additions."],
    "public_summary": "rev0193 catalog indexes receipt-quorum and WRSR dry-run chain surfaces."
}
write_json("examples/canon-surface-catalog-rev0193.json", catalog)

# Doctrine dependency map.
deps = {
    "map_id": "DOCTRINE-DEPENDENCY-MAP-REV0193",
    "created_at": STAMP_UTC,
    "revision": REV,
    "scope": "Current-release dependency map for receipt quorum and representative/RERB WRSR dry-run chain.",
    "surfaces": [
        {
            "surface_id": "REV0193-DEP-001",
            "path": "docs/30-transition/representative-rerb-receipt-chain-and-quorum-ledger.md",
            "layer": "transition",
            "depends_on": [
                "docs/30-transition/external-receipt-intake-and-wrsr-live-exercise-outcome.md",
                "docs/30-transition/protocol-welfare-safeguard-backfill-and-external-receipt-simulation.md",
                "docs/30-transition/cross-critical-witnessed-drill-readiness-and-receipt-matrix.md",
                "docs/20-world-design/research-welfare-and-evaluation.md"
            ],
            "overlaps_with": [
                "docs/30-transition/external-receipt-intake-and-wrsr-live-exercise-outcome.md",
                "docs/30-transition/witnessed-drill-execution-pack-and-reliance-gates.md"
            ],
            "supersedes": [],
            "owner_role": "receipt/quorum steward",
            "review_cadence": "rev0194 priority review",
            "refactor_risk": "critical"
        },
        {
            "surface_id": "REV0193-DEP-002",
            "path": "docs/30-transition/external-receipt-intake-and-wrsr-live-exercise-outcome.md",
            "layer": "transition",
            "depends_on": ["docs/30-transition/representative-rerb-receipt-chain-and-quorum-ledger.md"],
            "overlaps_with": ["docs/30-transition/cross-critical-witnessed-drill-readiness-and-receipt-matrix.md"],
            "supersedes": [],
            "owner_role": "receipt/WRSR steward",
            "review_cadence": "rev0194 priority review",
            "refactor_risk": "high"
        },
        {
            "surface_id": "REV0193-DEP-003",
            "path": "docs/20-world-design/research-welfare-and-evaluation.md",
            "layer": "world-design",
            "depends_on": ["docs/30-transition/protocol-welfare-safeguard-backfill-and-external-receipt-simulation.md"],
            "overlaps_with": ["docs/30-transition/representative-rerb-receipt-chain-and-quorum-ledger.md"],
            "supersedes": [],
            "owner_role": "welfare steward",
            "review_cadence": "rev0194 priority review",
            "refactor_risk": "high"
        }
    ],
    "audit_findings": ["Receipt quorum now has a dependency spine rather than scattered fields across simulation, intake, and live packet surfaces."],
    "refactor_actions": ["Future receipt additions should update the quorum ledger and not create new doctrine surfaces."],
    "public_summary": "rev0193 dependency map centers the receipt-quorum ledger as the operational spine."
}
write_json("examples/doctrine-dependency-map-rev0193.json", deps)

# Rights domain coverage map: clone and add/replace domains.
rights = deepcopy(read_json("examples/rights-domain-coverage-map-rev0192.json"))
rights["map_id"] = "RIGHTS-DOMAIN-COVERAGE-REV0193"
rights["created_at"] = STAMP_UTC
rights["revision"] = REV
rights["scope"] = "rev0193 rights coverage for receipt quorum, representative/RERB dry-run chain, and WRSR stayed closure."
add_or_replace(rights["domains"], {
    "domain_id": "external-receipt-quorum",
    "title": "External receipt quorum and dry-run/live separation",
    "domain_class": "operational",
    "owner_surface": "docs/30-transition/representative-rerb-receipt-chain-and-quorum-ledger.md",
    "covered_surfaces": [
        "docs/30-transition/representative-rerb-receipt-chain-and-quorum-ledger.md",
        "docs/30-transition/external-receipt-intake-and-wrsr-live-exercise-outcome.md",
        "docs/30-transition/cross-critical-witnessed-drill-readiness-and-receipt-matrix.md",
        "docs/30-transition/witnessed-drill-execution-pack-and-reliance-gates.md"
    ],
    "schema_families": ["EXTERNAL-RECEIPT-QUORUM-LEDGER", "EXTERNAL-RECEIPT-INTAKE-RECORD", "LIVE-DRILL-EXECUTION-PACKET"],
    "fixture_ids": ["NF-PLAYBOOK-2026-0006", "NF-PLAYBOOK-2026-0007"],
    "coverage_state": "adequate",
    "open_gaps": ["No actual external receipt quorum exists yet; all representative/RERB receipts are dry-run only."],
    "next_audit_actions": ["Collect actual external representative/RERB receipts or keep live drill stayed."]
}, key="domain_id")
add_or_replace(rights["domains"], {
    "domain_id": "wrsr-representative-rerb-review",
    "title": "WRSR representative notice, RERB review, and result-return stay",
    "domain_class": "research-welfare",
    "owner_surface": "docs/20-world-design/research-welfare-and-evaluation.md",
    "covered_surfaces": [
        "docs/20-world-design/research-welfare-and-evaluation.md",
        "docs/30-transition/protocol-welfare-safeguard-backfill-and-external-receipt-simulation.md",
        "docs/30-transition/representative-rerb-receipt-chain-and-quorum-ledger.md"
    ],
    "schema_families": ["WELFARE-RESEARCH-SAFEGUARD", "WELFARE-SAFEGUARD-OPERATIONAL-HOOK", "WRSR-LIVE-EXERCISE-OUTCOME", "EXTERNAL-RECEIPT-QUORUM-LEDGER"],
    "fixture_ids": ["NF-RESEARCH-WELFARE-2026-0003", "NF-RESEARCH-WELFARE-2026-0004"],
    "coverage_state": "adequate",
    "open_gaps": ["Result-return receipt remains open; representative/RERB records are dry-run rather than actual external receipts."],
    "next_audit_actions": ["Run WRSR result-return receipt exercise and preserve public failed-gate disclosure if unresolved."]
}, key="domain_id")
add_unique(rights["audit_findings"], "rev0193 adds receipt quorum and WRSR representative/RERB review domains while retaining stayed reliance.")
add_unique(rights["refactor_actions"], "Keep WRSR receipt work in operational domains, not research-tail sprawl.")
rights["public_summary"] = "rev0193 rights map adds receipt-quorum and WRSR representative/RERB review coverage."
write_json("examples/rights-domain-coverage-map-rev0193.json", rights)

# ---------------------------------------------------------------------------
# Front door, index, status, revision receipt, changelog
# ---------------------------------------------------------------------------
write_text("README.md", """
# AI Personhood datacube — rev0193

This archive assumes the working premise of AI personhood and focuses on operational rights infrastructure: continuity, evidence, representation, remedy, proof standards, and transition machinery.

## This revision

**Active revision:** `rev0193`

rev0193 is the representative/RERB receipt-chain and quorum-ledger pass. It does not add a doctrine wave. It closes the gap where high-fidelity non-host dry-run receipt chains could be mistaken for live external receipt quorum, and where representative/RERB participation could be mistaken for WRSR closure.

Read first: `docs/30-transition/representative-rerb-receipt-chain-and-quorum-ledger.md`.

Core rules: **Receipt chain is not live quorum. Dry-run quorum is rehearsal only. Representative/RERB participation is not WRSR closure.**

New operational artifacts:

- `schemas/external-receipt-quorum-ledger.schema.json`
- `examples/external-receipt-quorum-ledger-wrsr-representative-rerb-dryrun.json`
- `examples/external-receipt-intake-record-representative-notice-dryrun.json`
- `examples/external-receipt-intake-record-rerb-review-dryrun.json`
- `examples/wrsr-live-exercise-outcome-representative-rerb-dryrun-stayed.json`
- `fixtures/negative-tests/external-receipt-quorum-dryrun-counted-as-live.json`
- `fixtures/negative-tests/wrsr-rerb-dryrun-mislabeled-closure.json`
- `tools/audit_receipt_quorum_wrsr_chain.py`

## Validation posture

`make handoff-release` is the release command. It regenerates the context pack and manifest, runs lint and release-specific audits, and packages the archive. The fixture suite/report now cover 97 entries.

Reliance remains stayed where drills are synthetic, preflight-only, simulated, defective, host-self-attested, missing actual external receipts, or where WRSR exercise outcomes lack actual external representative/RERB receipt, result return, or anti-signal-gaming safeguards.

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
""")

write_text("START_HERE.md", """
# Start here — AI Personhood rev0193

This handoff starts from the representative/RERB receipt-chain and quorum-ledger pass. The archive should be read as object-backed operational work, not as a premise debate.

1. `README.md`
2. `docs/30-transition/representative-rerb-receipt-chain-and-quorum-ledger.md`
3. `schemas/external-receipt-quorum-ledger.schema.json`
4. `examples/external-receipt-quorum-ledger-wrsr-representative-rerb-dryrun.json`
5. `examples/external-receipt-intake-record-representative-notice-dryrun.json`
6. `examples/external-receipt-intake-record-rerb-review-dryrun.json`
7. `examples/wrsr-live-exercise-outcome-representative-rerb-dryrun-stayed.json`
8. `fixtures/negative-tests/external-receipt-quorum-dryrun-counted-as-live.json`
9. `fixtures/negative-tests/wrsr-rerb-dryrun-mislabeled-closure.json`
10. `docs/30-transition/external-receipt-intake-and-wrsr-live-exercise-outcome.md`
11. `schemas/external-receipt-intake-record.schema.json`
12. `schemas/wrsr-live-exercise-outcome.schema.json`
13. `docs/30-transition/protocol-welfare-safeguard-backfill-and-external-receipt-simulation.md`
14. `examples/external-receipt-simulation-bundle-cross-critical-precontact.json`
15. `examples/live-drill-execution-packet-cross-critical-witnessed-pack.json`
16. `docs/30-transition/cross-critical-witnessed-drill-readiness-and-receipt-matrix.md`
17. `docs/20-world-design/research-welfare-and-evaluation.md`
18. `docs/30-transition/witnessed-drill-execution-pack-and-reliance-gates.md`
19. `docs/30-transition/priority-closure-sprint-and-rescue-lane.md`
20. `FOLLOWTHROUGH-QUEUE.json`
21. `examples/schema-fixture-domain-registry-rev0193.json`
22. `examples/canon-surface-catalog-rev0193.json`
23. `examples/doctrine-dependency-map-rev0193.json`
24. `examples/rights-domain-coverage-map-rev0193.json`
25. `examples/research-tail-compaction-map-rev0193.json`
26. `docs/00-meta/research-tail-reopen-gate-and-sprawl-control.md`
27. `docs/00-meta/charter.md`

## This revision

rev0193 adds receipt-chain and quorum-ledger records. It advances representative/RERB WRSR review from missing-review no-go to dry-run readiness, but it does not close live external receipt collection or WRSR closure.

Core rules: **Receipt chain is not live quorum. Dry-run quorum is rehearsal only. Representative/RERB participation is not WRSR closure.**

## Current open risk

Representative and RERB dry-run receipts now exist, but actual external receipt quorum still does not. Reliance remains stayed until those dry-run records are replaced by actual external receipt records and result-return state is resolved.
""")

append_once("CHANGELOG.md", "## rev0193 — representative/RERB receipt chain and quorum ledger", """
## rev0193 — representative/RERB receipt chain and quorum ledger

- Added `docs/30-transition/representative-rerb-receipt-chain-and-quorum-ledger.md`.
- Added `schemas/external-receipt-quorum-ledger.schema.json` and the representative/RERB dry-run quorum ledger example.
- Added representative-contact and independent-review receipt-intake examples plus a WRSR dry-run outcome that keeps closure stayed.
- Added negative fixtures blocking dry-run receipt quorum from being counted as live and blocking representative/RERB dry-run participation from being mislabeled as WRSR closure.
- Added `tools/audit_receipt_quorum_wrsr_chain.py` and active rev0193 catalog/dependency/rights/registry/compaction maps.
- Closed `FT-0193-REPRESENTATIVE-RERB-RECEIPT-CHAIN`; advanced but did not close actual external receipt collection or WRSR result-return closure.
""")

append_once("docs/README.md", "## rev0193 receipt quorum and WRSR dry-run chain", """
## rev0193 receipt quorum and WRSR dry-run chain

Use `docs/30-transition/representative-rerb-receipt-chain-and-quorum-ledger.md` as the current operational head for aggregating receipt-intake records into quorum decisions. It is backed by `schemas/external-receipt-quorum-ledger.schema.json`, `examples/external-receipt-quorum-ledger-wrsr-representative-rerb-dryrun.json`, representative and RERB dry-run receipt examples, a WRSR dry-run outcome, and two blocking fixtures. The core rule is that receipt chain and dry-run quorum do not satisfy live quorum.
""")

append_once("ARCHIVE_INDEX.md", "## rev0193 representative/RERB receipt chain and quorum ledger", """
## rev0193 representative/RERB receipt chain and quorum ledger

- `docs/30-transition/representative-rerb-receipt-chain-and-quorum-ledger.md`
- `schemas/external-receipt-quorum-ledger.schema.json`
- `examples/external-receipt-quorum-ledger-wrsr-representative-rerb-dryrun.json`
- `examples/external-receipt-intake-record-representative-notice-dryrun.json`
- `examples/external-receipt-intake-record-rerb-review-dryrun.json`
- `examples/wrsr-live-exercise-outcome-representative-rerb-dryrun-stayed.json`
- `fixtures/negative-tests/external-receipt-quorum-dryrun-counted-as-live.json`
- `fixtures/negative-tests/wrsr-rerb-dryrun-mislabeled-closure.json`
- `tools/audit_receipt_quorum_wrsr_chain.py`
- `examples/schema-fixture-domain-registry-rev0193.json`
- `examples/canon-surface-catalog-rev0193.json`
- `examples/doctrine-dependency-map-rev0193.json`
- `examples/rights-domain-coverage-map-rev0193.json`
- `examples/research-tail-compaction-map-rev0193.json`
""")

status = read_json("SURFACE-STATUS.json")
status.update({
    "revision": REV,
    "state_class": "receipt-quorum-representative-rerb-chain",
    "operational_head": {"surface": "START_HERE.md", "read_first": "docs/30-transition/representative-rerb-receipt-chain-and-quorum-ledger.md"},
    "formation_layer_status": "canon-retained with receipt-chain quorum ledger and WRSR representative/RERB dry-run outcome; live receipts still absent",
    "known_open_gaps": [
        "The cross-critical witnessed drill still lacks actual non-host receipts.",
        "Representative and RERB receipt records are high-fidelity dry runs, not live external evidence.",
        "The WRSR dry-run outcome keeps result return and closure stayed.",
        "The registry remains truth-labeled as mixed-current-plus-counts, not full-archive-corpus coverage.",
        "Could-not-run fixtures remain reliance blockers rather than passes."
    ],
    "new_surfaces": [path for path, _, _ in surfaces]
})
write_json("SURFACE-STATUS.json", status)

receipt = {
    "revision": REV,
    "date": DATE,
    "authored_by": "OpenAI GPT-5.5 Thinking",
    "status_change": "advanced from receipt-intake objectization to representative/RERB receipt-chain quorum accounting",
    "still_live": True,
    "summary": "Adds external receipt quorum ledger schema/example, representative and RERB receipt-intake dry-run examples, a stayed WRSR dry-run outcome, two blocking fixtures, active maps, and an audit keeping live quorum unsatisfied.",
    "why_this_counts": [
        "Receipt intake records now aggregate into an explicit quorum ledger rather than scattered fields.",
        "Representative and RERB review lanes are exercised without pretending actual external receipts exist.",
        "Two blocking fixtures prevent dry-run quorum and WRSR review presence from laundering reliance closure.",
        "The live drill packet references the quorum ledger while preserving independent_receipts_present=0."
    ],
    "known_limits": [
        "No actual external non-host receipts have been collected yet.",
        "Representative and RERB records are high-fidelity dry runs only.",
        "Result-return receipt and WRSR closure remain open.",
        "Registry coverage remains mixed-current-plus-counts."
    ]
}
write_json("REVISION-RECEIPT.json", receipt)

# Patch lint required list and early audits.
lint_path = ROOT / "tools/lint_archive.py"
lint = lint_path.read_text(encoding="utf-8")
insert_required = """    'docs/30-transition/representative-rerb-receipt-chain-and-quorum-ledger.md',\n    'schemas/external-receipt-quorum-ledger.schema.json',\n    'examples/external-receipt-quorum-ledger-wrsr-representative-rerb-dryrun.json',\n    'examples/external-receipt-intake-record-representative-notice-dryrun.json',\n    'examples/external-receipt-intake-record-rerb-review-dryrun.json',\n    'examples/wrsr-live-exercise-outcome-representative-rerb-dryrun-stayed.json',\n    'fixtures/negative-tests/external-receipt-quorum-dryrun-counted-as-live.json',\n    'fixtures/negative-tests/wrsr-rerb-dryrun-mislabeled-closure.json',\n    'examples/research-tail-compaction-map-rev0193.json',\n    'examples/schema-fixture-domain-registry-rev0193.json',\n    'examples/canon-surface-catalog-rev0193.json',\n    'examples/doctrine-dependency-map-rev0193.json',\n    'examples/rights-domain-coverage-map-rev0193.json',\n    'tools/audit_receipt_quorum_wrsr_chain.py',\n"""
needle = "    'tools/audit_receipt_intake_wrsr_outcome.py',\n    'tools/package_release.py',\n"
if "tools/audit_receipt_quorum_wrsr_chain.py" not in lint:
    lint = lint.replace(needle, "    'tools/audit_receipt_intake_wrsr_outcome.py',\n" + insert_required + "    'tools/package_release.py',\n")
needle2 = "    'tools/audit_protocol_wrsr_receipt_simulation.py',\n    'tools/audit_canon_surface_catalog.py',\n"
if "    'tools/audit_receipt_quorum_wrsr_chain.py'," not in lint.split("early_audits = ",1)[1].split("]",1)[0]:
    lint = lint.replace(needle2, "    'tools/audit_protocol_wrsr_receipt_simulation.py',\n    'tools/audit_receipt_intake_wrsr_outcome.py',\n    'tools/audit_receipt_quorum_wrsr_chain.py',\n    'tools/audit_canon_surface_catalog.py',\n")
lint_path.write_text(lint, encoding="utf-8")

# Patch schema fixture audit required family.
audit_path = ROOT / "tools/audit_schema_fixture_coverage.py"
audit = audit_path.read_text(encoding="utf-8")
old = "'EXTERNAL-RECEIPT-INTAKE-RECORD', 'WRSR-LIVE-EXERCISE-OUTCOME'"
new = "'EXTERNAL-RECEIPT-INTAKE-RECORD', 'WRSR-LIVE-EXERCISE-OUTCOME', 'EXTERNAL-RECEIPT-QUORUM-LEDGER'"
audit = audit.replace(old, new)
audit_path.write_text(audit, encoding="utf-8")

print("apply_rev0193: OK")
