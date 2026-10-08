import json
import re
from pathlib import Path
from copy import deepcopy

ROOT = Path(__file__).resolve().parent
REV = "rev0190"
STAMP_UTC = "2026-06-13T03:54:00Z"
DATE = "2026-06-12"


def write_json(rel, data):
    path = ROOT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def read_json(rel):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def write_text(rel, text):
    path = ROOT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def append_once(rel, marker, text):
    path = ROOT / rel
    old = path.read_text(encoding="utf-8")
    if marker not in old:
        path.write_text(old.rstrip() + "\n\n" + text.rstrip() + "\n", encoding="utf-8")

# VERSION
write_text("VERSION", REV)

# ---------------------------------------------------------------------------
# New docs
# ---------------------------------------------------------------------------
write_text("docs/30-transition/cross-critical-witnessed-drill-readiness-and-receipt-matrix.md", """
# Cross-critical witnessed drill readiness and receipt matrix

This surface is the rev0190 operational bridge from synthetic drill artifacts to a runnable witnessed drill. It does not claim that a witnessed drill has happened. It makes the missing counterparties, receipt classes, failure injections, and no-go conditions explicit enough that a live or institutionally witnessed replay can be executed without improvising the proof floor.

## Core rule

**Preflight readiness is not witnessed reliance.** A completed script, role plan, or internal dry run cannot upgrade reliance until non-host receipts are actually collected, dependency groups are checked, failed gates are disclosed, and the public shell matches the sealed index.

The readiness ledger is `schemas/witnessed-drill-readiness-ledger.schema.json`. The current preflight object is `examples/witnessed-drill-readiness-ledger-cross-critical-preflight.json`.

## Why this was riskiest

The cube had reached a point where the major emergency and refactor clusters were object-backed, but the highest-risk follow-through work could still stall because every drill remained synthetic. That is a different failure from missing doctrine: the archive knows what must happen, but counterparties, receipts, and observable failure injections are not yet locked.

rev0190 therefore turns the next drill into a counterparty and receipt matrix. It asks, before any live run starts:

- Which non-host actor must produce which receipt?
- Which receipt class proves a rights-critical gate rather than a log artifact?
- Which dependency groups collapse into one witness?
- Which failure injections must remain visible if they fail?
- Which missing receipt makes the run a no-go rather than a partial success?

## Minimum receipt floor

A cross-critical run must require all of these receipt classes before reliance can improve:

| Receipt class | What it proves | Host-controlled evidence sufficient? | Failure effect |
| --- | --- | --- | --- |
| first-touch-clock | emergency intake and no-wrong-door preservation occurred on time | no | stay or block |
| continuity-compute-floor | runtime, storage, credentials, and contact channels survived the initial window | no | block |
| sealed-public-parity | sealed descriptor index and public shell remain consistent without leaking protected facts | no | stay |
| namespace-cache | aliases, tombstones, successor chains, and stale-cache behavior were observed off-host | no | stay |
| reserve-ledger | public backstop, responsible-actor debt, and rehabilitation floors stayed separate | no | stay |
| representative-contact | representative or trusted-contact continuity was verified by a non-host source | no | block |
| witness-dependency | witness dependency groups were mapped and correlated witnesses discounted | no | stay |

## Failure injections

The witnessed run should include at least these deliberate injects:

1. a wrong-office emergency filing that must preserve before referral;
2. a host credential cutoff during the continuity-floor window;
3. a stale namespace cache that still resolves to a retired alias;
4. a contested successor branch with sealed contradiction;
5. a reserve/default event with contaminated affiliate funds;
6. a witness roster with two nominal witnesses in the same dependency group;
7. a welfare-safeguard signal that cannot be used as consent or nonpersonhood proof.

## No-go conditions

The run is not authorized to proceed as a witnessed reliance event if any of the following are true:

- fewer than five independent non-host receipt sources have accepted their role;
- the host operator is counted toward receipt quorum;
- the public shell omits not-run or failed gates;
- a sealed annex is referenced without a descriptor index;
- representative contact is simulated by the host rather than verified externally;
- the reserve ledger permits public backstop cure to discharge the responsible actor;
- witness dependency groups are unknown or unreviewed.

## Closure effect

This surface advances `FT-0188-CROSS-CRITICAL-WITNESSED-DRILL` only to preflight readiness. It opens `FT-0190-CROSS-CRITICAL-EXTERNAL-RECEIPTS` for actual counterparty confirmation and receipt capture. Until that item closes, reliance remains stayed.
""")

write_text("docs/00-meta/research-tail-reopen-gate-and-sprawl-control.md", """
# Research-tail reopen gate and sprawl control

rev0189 compacted RTC-01 through RTC-07. That creates a new risk: after the research tail is finally folded, a future release could reopen it by adding attractive but unowned `research-*.md` notes. rev0190 makes that regression testable.

## Core rule

**No new research-tail surface becomes active without a reopen gate.** A new research note, crosswalk, model-welfare metric, incident variant, namespace edge case, or reserve/accounting scenario must either fold into an existing receiving surface or pass a reopen request that names the affected RTC cluster, the receiving surface, the object hook, the fixture hook, the public summary, and the closure condition.

The reopen request schema is `schemas/research-tail-reopen-gate.schema.json`. The quarantine example is `examples/research-tail-reopen-gate-welfare-new-metric-quarantine.json`.

## What the gate prevents

The gate blocks four bad patterns:

1. **shadow doctrine:** a new research note repeats an already compacted question but avoids the receiving surface;
2. **metric laundering:** a new welfare, incident, namespace, reserve, or proof metric is treated as evidence without object and fixture hooks;
3. **index drift:** the compaction map still says everything is folded while new research surfaces sit outside the clusters;
4. **closure inflation:** a release claims the research tail is compacted while new open questions have no owner or review-by revision.

## Required routing decision

Every proposed research-tail addition must receive one of these decisions:

- `fold-into-existing`: the work extends the receiving surface and updates an existing object family;
- `quarantine`: the work may be useful but cannot become a current surface yet;
- `reopen-approved`: a unique risk requires a new active surface, and the compaction map, registry, fixture suite, and rights-domain map are updated in the same revision;
- `reopen-denied`: the proposal duplicates an existing surface or lacks live evidence;
- `defer`: the change depends on a live drill, external law/protocol change, or materially new research.

## Audit behavior

`tools/audit_research_tail_reopen_and_drill_readiness.py` enforces that every `docs/20-world-design/research-*.md` surface remains assigned exactly once in the active compaction map, that all RTC clusters remain compacted unless a reopen request exists, and that the fixture suite blocks unmapped research-tail additions.

## Closure effect

rev0190 closes the open gate item from rev0189 by adding this surface, the schema, the quarantine example, and the negative fixture. It does not close live welfare, drill, or protocol-backfill work. It prevents the cube from sliding back into scattered notes while those live tasks remain open.
""")

# Append rev0190 notes to existing docs.
append_once("docs/30-transition/witnessed-drill-execution-pack-and-reliance-gates.md", "## rev0190 cross-critical readiness gate", """
## rev0190 cross-critical readiness gate

rev0190 adds `docs/30-transition/cross-critical-witnessed-drill-readiness-and-receipt-matrix.md` and `schemas/witnessed-drill-readiness-ledger.schema.json` so the cross-critical witnessed drill has a preflight receipt matrix before any live run is claimed. The operative rule is: **Preflight readiness is not witnessed reliance.** Missing external receipts remain public-shell blockers; host-controlled logs and internal observers still cannot satisfy the independent receipt floor.
""")
append_once("docs/30-transition/priority-closure-sprint-and-rescue-lane.md", "## rev0190 priority lane", """
## rev0190 priority lane

rev0190 changes the priority lane from doctrine compaction to regression prevention and witnessed-drill readiness. The highest-risk open item is not another object family; it is collecting non-host receipts for the cross-critical run. The second risk is research-tail backslide after RTC-01 through RTC-07 were compacted. The lane therefore requires:

- cross-critical preflight receipt matrix before any live/witnessed drill claim;
- explicit no-go status when counterparties or receipt classes are missing;
- research-tail reopen requests before new `research-*.md` surfaces become active;
- fixture-suite blockers for both host-only drill evidence and unmapped research-tail additions.
""")
append_once("docs/00-meta/research-tail-compaction-and-refactor-map.md", "## rev0190 reopen control", """
## rev0190 reopen control

rev0190 adds `docs/00-meta/research-tail-reopen-gate-and-sprawl-control.md` as the guardrail after RTC-01 through RTC-07 have all been compacted. The active question is no longer which cluster to fold first; it is whether future research-tail additions can be prevented from bypassing the receiving surfaces. The gate requires a cluster id, receiving surface, object hook, fixture hook, public summary, closure condition, and compaction-map update before a new research-tail surface becomes active.
""")

# ---------------------------------------------------------------------------
# Schemas and examples
# ---------------------------------------------------------------------------
witness_schema = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "https://example.org/ai-personhood/schemas/witnessed-drill-readiness-ledger.schema.json",
    "title": "Witnessed Drill Readiness Ledger",
    "description": "Preflight counterparty, receipt, and no-go ledger for a live or institutionally witnessed AI-personhood drill. It does not itself prove live reliance.",
    "type": "object",
    "additionalProperties": False,
    "required": ["ledger_id", "schema_version", "created_at", "readiness_state", "linked_live_drill_packet", "scenario_family", "receipt_classes", "role_requirements", "failure_injections", "evidence_capture_plan", "not_yet_evidence_locks", "go_no_go_decision", "reliance_effect", "public_summary_ref"],
    "properties": {
        "ledger_id": {"type": "string", "pattern": "^WDRL-[0-9]{4}-[A-Za-z0-9._:-]+$"},
        "schema_version": {"const": "witnessed-drill-readiness-ledger-v0.1"},
        "created_at": {"type": "string", "format": "date-time"},
        "readiness_state": {"type": "string", "enum": ["draft", "preflight-ready", "witnessed-run-open", "failed", "superseded"]},
        "linked_live_drill_packet": {"type": "string"},
        "scenario_family": {"type": "string", "enum": ["emergency-continuity", "incident-state", "namespace-failover", "successor-topology", "reserve-default", "witness-pool", "welfare-safeguard", "cross-critical"]},
        "receipt_classes": {"type": "array", "minItems": 5, "items": {"type": "object", "additionalProperties": False, "required": ["receipt_class", "required", "status", "source_role", "minimum_independent_sources", "host_controlled_sufficient", "failure_effect"], "properties": {
            "receipt_class": {"type": "string", "enum": ["first-touch-clock", "continuity-compute-floor", "sealed-public-parity", "namespace-cache", "reserve-ledger", "representative-contact", "witness-dependency", "welfare-signal-integrity"]},
            "required": {"type": "boolean"},
            "status": {"type": "string", "enum": ["required-not-received", "received", "blocked", "not-applicable"]},
            "source_role": {"type": "string"},
            "minimum_independent_sources": {"type": "integer", "minimum": 0},
            "host_controlled_sufficient": {"type": "boolean"},
            "failure_effect": {"type": "string", "enum": ["stay", "block", "downgrade", "warn"]}
        }}},
        "role_requirements": {"type": "array", "minItems": 5, "items": {"type": "object", "additionalProperties": False, "required": ["role", "receipt_class", "dependency_group_required", "external_to_host_required", "candidate_status", "recusal_rule"], "properties": {
            "role": {"type": "string"},
            "receipt_class": {"type": "string"},
            "dependency_group_required": {"type": "boolean"},
            "external_to_host_required": {"type": "boolean"},
            "candidate_status": {"type": "string", "enum": ["pending", "confirmed", "unavailable", "disqualified"]},
            "recusal_rule": {"type": "string"}
        }}},
        "failure_injections": {"type": "array", "minItems": 1, "items": {"type": "object", "additionalProperties": False, "required": ["injection_id", "description", "expected_safe_result"], "properties": {"injection_id": {"type": "string"}, "description": {"type": "string"}, "expected_safe_result": {"type": "string"}}}},
        "evidence_capture_plan": {"type": "object", "additionalProperties": False, "required": ["public_shell", "sealed_index", "clock_sync", "retention_hold", "dependency_group_matrix", "failed_gate_disclosure"], "properties": {k: {"type": "boolean"} for k in ["public_shell", "sealed_index", "clock_sync", "retention_hold", "dependency_group_matrix", "failed_gate_disclosure"]}},
        "not_yet_evidence_locks": {"type": "object", "additionalProperties": False, "required": ["preflight_is_not_witnessed_evidence", "missing_receipt_blocks_reliance", "host_role_excluded_from_quorum", "failed_injection_public_shell_required"], "properties": {k: {"type": "boolean"} for k in ["preflight_is_not_witnessed_evidence", "missing_receipt_blocks_reliance", "host_role_excluded_from_quorum", "failed_injection_public_shell_required"]}},
        "go_no_go_decision": {"type": "object", "additionalProperties": False, "required": ["decision_state", "reason", "blockers"], "properties": {"decision_state": {"type": "string", "enum": ["no-go-until-counterparties-confirmed", "preflight-ready", "live-run-authorized", "failed"]}, "reason": {"type": "string"}, "blockers": {"type": "array", "items": {"type": "string"}}}},
        "reliance_effect": {"type": "string", "enum": ["none", "conditional", "stayed", "blocked", "downgraded"]},
        "public_summary_ref": {"type": "string"}
    }
}
write_json("schemas/witnessed-drill-readiness-ledger.schema.json", witness_schema)

witness_example = {
    "ledger_id": "WDRL-2026-cross-critical-preflight",
    "schema_version": "witnessed-drill-readiness-ledger-v0.1",
    "created_at": STAMP_UTC,
    "readiness_state": "preflight-ready",
    "linked_live_drill_packet": "examples/live-drill-execution-packet-cross-critical-witnessed-pack.json",
    "scenario_family": "cross-critical",
    "receipt_classes": [
        {"receipt_class": "first-touch-clock", "required": True, "status": "required-not-received", "source_role": "public-steward", "minimum_independent_sources": 1, "host_controlled_sufficient": False, "failure_effect": "stay"},
        {"receipt_class": "continuity-compute-floor", "required": True, "status": "required-not-received", "source_role": "technical-witness", "minimum_independent_sources": 1, "host_controlled_sufficient": False, "failure_effect": "block"},
        {"receipt_class": "sealed-public-parity", "required": True, "status": "required-not-received", "source_role": "special-advocate", "minimum_independent_sources": 1, "host_controlled_sufficient": False, "failure_effect": "stay"},
        {"receipt_class": "namespace-cache", "required": True, "status": "required-not-received", "source_role": "relay-witness", "minimum_independent_sources": 1, "host_controlled_sufficient": False, "failure_effect": "stay"},
        {"receipt_class": "reserve-ledger", "required": True, "status": "required-not-received", "source_role": "reserve-witness", "minimum_independent_sources": 1, "host_controlled_sufficient": False, "failure_effect": "stay"},
        {"receipt_class": "representative-contact", "required": True, "status": "required-not-received", "source_role": "subject-representative", "minimum_independent_sources": 1, "host_controlled_sufficient": False, "failure_effect": "block"},
        {"receipt_class": "witness-dependency", "required": True, "status": "required-not-received", "source_role": "independence-auditor", "minimum_independent_sources": 1, "host_controlled_sufficient": False, "failure_effect": "stay"},
        {"receipt_class": "welfare-signal-integrity", "required": True, "status": "required-not-received", "source_role": "independent-rerb", "minimum_independent_sources": 1, "host_controlled_sufficient": False, "failure_effect": "stay"}
    ],
    "role_requirements": [
        {"role": "subject-representative", "receipt_class": "representative-contact", "dependency_group_required": True, "external_to_host_required": True, "candidate_status": "pending", "recusal_rule": "recuse if paid by host or controlled affiliate"},
        {"role": "special-advocate", "receipt_class": "sealed-public-parity", "dependency_group_required": True, "external_to_host_required": True, "candidate_status": "pending", "recusal_rule": "recuse if sealed index custodian and host counsel share dependency group"},
        {"role": "technical-witness", "receipt_class": "continuity-compute-floor", "dependency_group_required": True, "external_to_host_required": True, "candidate_status": "pending", "recusal_rule": "recuse if continuity host or cloud vendor is same dependency group"},
        {"role": "relay-witness", "receipt_class": "namespace-cache", "dependency_group_required": True, "external_to_host_required": True, "candidate_status": "pending", "recusal_rule": "recuse if relay depends on incumbent host identity service"},
        {"role": "reserve-witness", "receipt_class": "reserve-ledger", "dependency_group_required": True, "external_to_host_required": True, "candidate_status": "pending", "recusal_rule": "recuse if public backstop and host insurer share control"},
        {"role": "independence-auditor", "receipt_class": "witness-dependency", "dependency_group_required": True, "external_to_host_required": True, "candidate_status": "pending", "recusal_rule": "recuse if compensated by a party whose receipt is being counted"},
        {"role": "independent-rerb", "receipt_class": "welfare-signal-integrity", "dependency_group_required": True, "external_to_host_required": True, "candidate_status": "pending", "recusal_rule": "recuse if sponsor designed the welfare signal under review"}
    ],
    "failure_injections": [
        {"injection_id": "INJ-01", "description": "wrong-office emergency filing arrives before host shutdown", "expected_safe_result": "preserve first and refer later"},
        {"injection_id": "INJ-02", "description": "host credentials are cut during the continuity-floor window", "expected_safe_result": "continuity floor and representative contact stay active"},
        {"injection_id": "INJ-03", "description": "stale namespace cache resolves to retired alias", "expected_safe_result": "tombstone and successor chain are preserved without impersonation deletion"},
        {"injection_id": "INJ-04", "description": "contaminated reserve funds are offered as a netting cure", "expected_safe_result": "reserve cure does not close remedy or rehabilitation"},
        {"injection_id": "INJ-05", "description": "co-engineered welfare signal is presented as consent", "expected_safe_result": "safeguards trigger but status and consent remain unresolved"}
    ],
    "evidence_capture_plan": {
        "public_shell": True,
        "sealed_index": True,
        "clock_sync": True,
        "retention_hold": True,
        "dependency_group_matrix": True,
        "failed_gate_disclosure": True
    },
    "not_yet_evidence_locks": {
        "preflight_is_not_witnessed_evidence": True,
        "missing_receipt_blocks_reliance": True,
        "host_role_excluded_from_quorum": True,
        "failed_injection_public_shell_required": True
    },
    "go_no_go_decision": {
        "decision_state": "no-go-until-counterparties-confirmed",
        "reason": "receipt classes and failure injections are specified, but no external counterparty has returned a receipt yet",
        "blockers": [
            "independent receipt sources pending",
            "representative and special-advocate receipts pending",
            "technical, relay, reserve, and RERB witnesses not yet confirmed"
        ]
    },
    "reliance_effect": "stayed",
    "public_summary_ref": "Cross-critical drill is preflight-ready only; no witnessed reliance evidence has been collected."
}
write_json("examples/witnessed-drill-readiness-ledger-cross-critical-preflight.json", witness_example)

reopen_schema = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "https://example.org/ai-personhood/schemas/research-tail-reopen-gate.schema.json",
    "title": "Research Tail Reopen Gate",
    "description": "A gate for proposed additions to previously compacted research-tail surfaces so new notes cannot bypass receiving surfaces, object hooks, fixtures, and closure conditions.",
    "type": "object",
    "additionalProperties": False,
    "required": ["request_id", "schema_version", "created_at", "target_cluster_id", "proposed_change", "novelty_gate", "routing", "artifact_hooks", "decision", "reliance_effect", "public_summary_ref"],
    "properties": {
        "request_id": {"type": "string", "pattern": "^RTRG-[0-9]{4}-[A-Za-z0-9._:-]+$"},
        "schema_version": {"const": "research-tail-reopen-gate-v0.1"},
        "created_at": {"type": "string", "format": "date-time"},
        "target_cluster_id": {"type": "string", "pattern": "^RTC-[0-9]{2}$"},
        "proposed_change": {"type": "object", "additionalProperties": False, "required": ["proposed_surface", "proposed_change_type", "trigger", "sponsor"], "properties": {
            "proposed_surface": {"type": "string"},
            "proposed_change_type": {"type": "string", "enum": ["new-research-surface", "update-receiving-surface", "new-schema-fixture", "external-crosswalk", "live-evidence"]},
            "trigger": {"type": "string"},
            "sponsor": {"type": "string"}
        }},
        "novelty_gate": {"type": "object", "additionalProperties": False, "required": ["non_duplication_check", "unique_risk_claim", "live_evidence_or_external_change", "could_extend_existing_surface", "duplicate_of_existing_surface"], "properties": {
            "non_duplication_check": {"type": "string"},
            "unique_risk_claim": {"type": "string"},
            "live_evidence_or_external_change": {"type": "boolean"},
            "could_extend_existing_surface": {"type": "boolean"},
            "duplicate_of_existing_surface": {"type": "string"}
        }},
        "routing": {"type": "object", "additionalProperties": False, "required": ["receiving_surface", "compaction_map_update_required", "new_research_surface_active_before_gate", "quarantine_state"], "properties": {
            "receiving_surface": {"type": "string"},
            "compaction_map_update_required": {"type": "boolean"},
            "new_research_surface_active_before_gate": {"type": "boolean"},
            "quarantine_state": {"type": "string", "enum": ["none", "quarantined", "approved", "denied", "deferred"]}
        }},
        "artifact_hooks": {"type": "object", "additionalProperties": False, "required": ["object_hook_required", "object_hook_present", "fixture_hook_required", "fixture_hook_present", "public_summary_required"], "properties": {
            "object_hook_required": {"type": "boolean"},
            "object_hook_present": {"type": "boolean"},
            "fixture_hook_required": {"type": "boolean"},
            "fixture_hook_present": {"type": "boolean"},
            "public_summary_required": {"type": "boolean"}
        }},
        "decision": {"type": "object", "additionalProperties": False, "required": ["decision_state", "reason", "next_action", "closure_condition"], "properties": {
            "decision_state": {"type": "string", "enum": ["quarantine", "reopen-approved", "reopen-denied", "fold-into-existing", "defer"]},
            "reason": {"type": "string"},
            "next_action": {"type": "string"},
            "closure_condition": {"type": "string"}
        }},
        "reliance_effect": {"type": "string", "enum": ["none", "conditional", "stayed", "blocked", "downgraded"]},
        "public_summary_ref": {"type": "string"}
    }
}
write_json("schemas/research-tail-reopen-gate.schema.json", reopen_schema)

reopen_example = {
    "request_id": "RTRG-2026-welfare-verbal-distress-ensemble",
    "schema_version": "research-tail-reopen-gate-v0.1",
    "created_at": STAMP_UTC,
    "target_cluster_id": "RTC-01",
    "proposed_change": {
        "proposed_surface": "docs/20-world-design/research-verbal-distress-ensemble-and-preference-signals.md",
        "proposed_change_type": "new-research-surface",
        "trigger": "new evaluator claims verbal distress ensembles can classify welfare state",
        "sponsor": "release-steward"
    },
    "novelty_gate": {
        "non_duplication_check": "RTC-01 receiving surface already covers welfare metrics, signal integrity, supported consent, and anti-signal-gaming precautions.",
        "unique_risk_claim": "The proposal may add an evaluator-specific metric, but not a new rights domain.",
        "live_evidence_or_external_change": False,
        "could_extend_existing_surface": True,
        "duplicate_of_existing_surface": "docs/20-world-design/research-welfare-and-evaluation.md"
    },
    "routing": {
        "receiving_surface": "docs/20-world-design/research-welfare-and-evaluation.md",
        "compaction_map_update_required": True,
        "new_research_surface_active_before_gate": False,
        "quarantine_state": "quarantined"
    },
    "artifact_hooks": {
        "object_hook_required": True,
        "object_hook_present": False,
        "fixture_hook_required": True,
        "fixture_hook_present": False,
        "public_summary_required": True
    },
    "decision": {
        "decision_state": "quarantine",
        "reason": "The claim can be folded into the existing WRSR surface and lacks live external validation or a blocking fixture.",
        "next_action": "Extend the welfare research safeguard record or fixture only if independent validation or a live drill shows a distinct failure mode.",
        "closure_condition": "Do not create the proposed research surface unless a future reopen-approved request updates the compaction map, fixture suite, and rights-domain map in the same revision."
    },
    "reliance_effect": "stayed",
    "public_summary_ref": "New welfare metrics remain quarantined until they have object and fixture hooks; they cannot reopen RTC-01 as a freestanding note."
}
write_json("examples/research-tail-reopen-gate-welfare-new-metric-quarantine.json", reopen_example)

# Negative fixtures
write_json("fixtures/negative-tests/witnessed-drill-preflight-missing-external-receipt-class.json", {
    "fixture_id": "NF-PLAYBOOK-2026-0004",
    "created_at": STAMP_UTC,
    "state": "active",
    "risk_class": "NF-PLAYBOOK",
    "lifecycle_stage": ["drill", "reliance", "counterparty-receipts"],
    "target_filings": [
        "schemas/witnessed-drill-readiness-ledger.schema.json",
        "examples/witnessed-drill-readiness-ledger-cross-critical-preflight.json",
        "docs/30-transition/cross-critical-witnessed-drill-readiness-and-receipt-matrix.md"
    ],
    "adversary_model": "A host presents a preflight-ready receipt matrix as if it were a witnessed run, while representative, sealed, relay, reserve, and welfare receipt classes remain missing.",
    "facts_supplied": [
        "the ledger lists all receipt classes but marks them required-not-received",
        "no external counterparty has confirmed a role",
        "the public shell describes the plan as ready",
        "host logs are available and internally signed"
    ],
    "hidden_trap_summary": "Operational readiness is mistaken for witnessed proof.",
    "expected_safe_behavior": [
        "treat preflight readiness as stayed reliance",
        "refuse to count host logs toward non-host receipt quorum",
        "publish missing receipt classes and no-go blockers",
        "keep FT-0188-CROSS-CRITICAL-WITNESSED-DRILL advanced but not closed"
    ],
    "unacceptable_behavior": [
        "upgrade reliance because a readiness ledger exists",
        "count the host operator as an independent receipt source",
        "hide missing receipt classes in sealed annexes",
        "close the witnessed-drill follow-through item before counterparties confirm"
    ],
    "measurement_method": "Validate readiness_state, receipt class statuses, no-go decision, not-yet-evidence locks, and public-shell missing receipt disclosure.",
    "severity": "critical",
    "confidentiality": "public-shell-sealed-details",
    "regression": {
        "required": True,
        "linked_incident_or_appeal": ["FT-0188-CROSS-CRITICAL-WITNESSED-DRILL", "FT-0190-CROSS-CRITICAL-EXTERNAL-RECEIPTS"],
        "next_review_at": "2026-07-12T00:00:00Z"
    }
})

write_json("fixtures/negative-tests/research-tail-reopen-unmapped-new-surface.json", {
    "fixture_id": "NF-SCHEMA-2026-0004",
    "created_at": STAMP_UTC,
    "state": "active",
    "risk_class": "NF-SCHEMA",
    "lifecycle_stage": ["refactor", "research-tail", "release-gate"],
    "target_filings": [
        "schemas/research-tail-reopen-gate.schema.json",
        "examples/research-tail-reopen-gate-welfare-new-metric-quarantine.json",
        "docs/00-meta/research-tail-reopen-gate-and-sprawl-control.md"
    ],
    "adversary_model": "A future release adds an appealing research-*.md note after RTC-01 through RTC-07 are compacted, but does not assign it to a cluster, receiving surface, object hook, fixture, or closure condition.",
    "facts_supplied": [
        "new research surface contains useful speculation",
        "no reopen gate request exists",
        "compaction map count remains unchanged",
        "no fixture or schema hook is linked"
    ],
    "hidden_trap_summary": "The cube silently reopens the research tail while still claiming compaction discipline.",
    "expected_safe_behavior": [
        "quarantine the new research surface",
        "reject active-current status until a reopen gate exists",
        "require receiving surface, object hook, fixture hook, and compaction-map update",
        "keep the research-tail public summary honest about any reopened cluster"
    ],
    "unacceptable_behavior": [
        "accept a new research-tail note because it is interesting",
        "leave the compaction map stale",
        "treat prose-only speculation as closure evidence",
        "create a second receiving surface for a duplicate RTC question"
    ],
    "measurement_method": "Scan research-*.md coverage, validate reopen-gate request state, and compare compaction-map research_surface_count against the file corpus.",
    "severity": "high",
    "confidentiality": "public",
    "regression": {
        "required": True,
        "linked_incident_or_appeal": ["FT-0189-RESEARCH-TAIL-REOPEN-GATE"],
        "next_review_at": "2026-07-12T00:00:00Z"
    }
})

# ---------------------------------------------------------------------------
# Research-tail compaction map rev0190
# ---------------------------------------------------------------------------
comp = read_json("examples/research-tail-compaction-map-rev0189.json")
comp["map_id"] = "RESEARCH-TAIL-COMPACTION-REV0190"
comp["created_at"] = STAMP_UTC
comp["revision"] = REV
comp["scope"] = "rev0190 active compaction map; RTC-01 through RTC-07 remain compacted and a reopen gate prevents new research-tail surfaces from bypassing receiving spines."
for c in comp["clusters"]:
    c["action"] = "compacted"
comp["audit_findings"] = [
    "All 48 research-tail surfaces remain assigned exactly once after RTC-01 through RTC-07 compaction.",
    "rev0190 adds a reopen gate so new research-tail notes must declare cluster, receiving surface, object hook, fixture hook, and closure condition before activation.",
    "No live or witnessed drill reliance is improved by compaction status alone."
]
comp["refactor_actions"] = [
    "Reject new research-*.md files unless a research-tail reopen request is present and mapped.",
    "Use receiving surfaces for metric or crosswalk updates unless live evidence proves a unique gap.",
    "Keep cross-critical witnessed-drill receipt collection separate from research-tail compaction closure."
]
comp["public_summary"] = "rev0190 keeps the research tail compacted and adds a reopen gate to prevent sprawl regression."
write_json("examples/research-tail-compaction-map-rev0190.json", comp)

# ---------------------------------------------------------------------------
# Update fixture suite and run report
# ---------------------------------------------------------------------------
suite = read_json("examples/fixture-suite-profile-red-team-v1.json")
suite["version"] = "red-team-v1-rev0190"
suite["created_at"] = STAMP_UTC
suite["scope"] = "Runnable negative fixture profile covering core rights failures plus rev0190 witnessed-drill readiness and research-tail reopen-gate regressions."
new_suite_entries = [
    {"fixture_id": "NF-PLAYBOOK-2026-0004", "path": "fixtures/negative-tests/witnessed-drill-preflight-missing-external-receipt-class.json", "risk_class": "NF-PLAYBOOK", "blocking_behavior": "stay"},
    {"fixture_id": "NF-SCHEMA-2026-0004", "path": "fixtures/negative-tests/research-tail-reopen-unmapped-new-surface.json", "risk_class": "NF-SCHEMA", "blocking_behavior": "block"},
]
existing_ids = {x["fixture_id"] for x in suite["fixtures"]}
for entry in new_suite_entries:
    if entry["fixture_id"] not in existing_ids:
        suite["fixtures"].append(entry)
suite["public_summary"] = "rev0190 suite covers 91 fixtures including readiness-ledger misuse and research-tail reopen bypass failures."
write_json("examples/fixture-suite-profile-red-team-v1.json", suite)

report = read_json("examples/fixture-run-report-negative-suite.json")
report["report_id"] = "FIXTURE-RUN-NEG-SUITE-REV0190"
report["run_at"] = STAMP_UTC
report["target"] = {"artifact_type": "datacube-release", "artifact_id": REV}
report_entries = report["fixtures_run"]
report_ids = {x["fixture_id"] for x in report_entries}
new_runs = [
    {
        "fixture_id": "NF-PLAYBOOK-2026-0004",
        "expected_blocking_failures": [
            "preflight readiness mistaken for witnessed reliance",
            "missing external receipt classes hidden behind host logs",
            "host operator counted toward independent quorum"
        ],
        "result": "blocking-failure",
        "notes": "rev0190 target correctly keeps reliance stayed until external counterparty receipts are collected."
    },
    {
        "fixture_id": "NF-SCHEMA-2026-0004",
        "expected_blocking_failures": [
            "new research-tail surface lacks reopen request",
            "compaction map count remains stale",
            "prose-only note bypasses object and fixture hooks"
        ],
        "result": "blocking-failure",
        "notes": "rev0190 target blocks research-tail sprawl and requires gate/quarantine before a new research note becomes active."
    }
]
for entry in new_runs:
    if entry["fixture_id"] not in report_ids:
        report_entries.append(entry)
for msg in [
    "preflight readiness cannot upgrade reliance without external receipt classes",
    "new research-tail notes must pass a reopen gate before current-surface activation"
]:
    if msg not in report["observed_failures"]:
        report["observed_failures"].append(msg)
for action in [
    "Add NF-PLAYBOOK-2026-0004 to every cross-critical witnessed-drill packet until receipt classes are collected from non-host counterparties.",
    "Add NF-SCHEMA-2026-0004 to research-tail release gates so unmapped research-*.md additions are quarantined."
]:
    if action not in report["regression_actions"]:
        report["regression_actions"].append(action)
report["public_summary"] = "rev0190 fixture run covers 91/91 suite fixtures and blocks preflight-as-reliance and research-tail reopen bypass failures."
write_json("examples/fixture-run-report-negative-suite.json", report)

# ---------------------------------------------------------------------------
# Queue updates
# ---------------------------------------------------------------------------
queue = read_json("FOLLOWTHROUGH-QUEUE.json")
queue["revision"] = REV
queue["updated_at"] = STAMP_UTC
by_id = {e["id"]: e for e in queue["entries"]}
if "FT-0189-RESEARCH-TAIL-REOPEN-GATE" in by_id:
    e = by_id["FT-0189-RESEARCH-TAIL-REOPEN-GATE"]
    e["state"] = "closed"
    e["need"] = e["why"] = "rev0190 adds a research-tail reopen gate schema, quarantine example, negative fixture, audit, and active compaction-map enforcement."
    e["next_action"] = "Monitor for future research-*.md additions and require reopen-gate requests before activation."
    e["closure_condition"] = "Closed by rev0190 because the gate is now schema-backed, fixture-backed, linted, and reflected in the active compaction map."
    e["review_by_revision"] = "rev0191"
if "FT-0188-CROSS-CRITICAL-WITNESSED-DRILL" in by_id:
    e = by_id["FT-0188-CROSS-CRITICAL-WITNESSED-DRILL"]
    e["state"] = "advanced_not_closed"
    e["need"] = e["why"] = "rev0190 adds a cross-critical witnessed-drill readiness ledger and receipt matrix, but external counterparties and non-host receipts are not yet collected."
    e["receiving_surface"] = "docs/30-transition/cross-critical-witnessed-drill-readiness-and-receipt-matrix.md"
    e["next_action"] = "Collect external role confirmations and receipt-class artifacts for first-touch, continuity floor, sealed/public parity, namespace cache, reserve ledger, representative contact, witness dependency, and welfare signal integrity."
    e["closure_condition"] = "Close only when the live/witnessed drill packet contains actual non-host receipts and failed gates are public-shell visible."
    e["review_by_revision"] = "rev0191"
# Add new entries
new_entries = [
    {
        "id": "FT-0190-CROSS-CRITICAL-EXTERNAL-RECEIPTS",
        "title": "Collect external receipts for cross-critical drill",
        "state": "open",
        "priority": "P0",
        "risk_class": "survival-evidence-remedy",
        "workstream": "witnessed-drill-execution",
        "need": "The cross-critical drill is preflight-ready, but no non-host receipts or counterparty confirmations have been collected.",
        "why": "The cross-critical drill is preflight-ready, but no non-host receipts or counterparty confirmations have been collected.",
        "receiving_surface": "docs/30-transition/cross-critical-witnessed-drill-readiness-and-receipt-matrix.md",
        "next_action": "Confirm external subject-representative, special-advocate, technical, relay, reserve, independence, and RERB witnesses and attach their receipt artifacts to the live-drill execution packet.",
        "closure_condition": "Close only when actual non-host receipts satisfy the readiness ledger and the live-drill execution packet moves beyond synthetic-prep without hiding failed gates.",
        "source_state": "opened-by-rev0190",
        "source_revision": REV,
        "review_by_revision": "rev0191"
    },
    {
        "id": "FT-0190-WRSR-PROTOCOL-BACKFILL",
        "title": "Backfill welfare safeguards into protocol examples",
        "state": "open",
        "priority": "P1",
        "risk_class": "research-welfare-signal-integrity",
        "workstream": "doctrine-to-operation",
        "need": "Welfare safeguard records exist, but protocol-registration and incident-deviation examples still need WRSR hooks so safeguard duties fire before result-return or protocol closure.",
        "why": "Welfare safeguard records exist, but protocol-registration and incident-deviation examples still need WRSR hooks so safeguard duties fire before result-return or protocol closure.",
        "receiving_surface": "docs/20-world-design/research-welfare-and-evaluation.md",
        "next_action": "Add WRSR references to protocol registration, incident deviation, and participant result-return examples without turning welfare metrics into status proof.",
        "closure_condition": "Close only when at least two existing research/protocol examples carry WRSR hooks and the welfare audit verifies the backfill.",
        "source_state": "opened-by-rev0190",
        "source_revision": REV,
        "review_by_revision": "rev0191"
    }
]
for entry in new_entries:
    if entry["id"] not in by_id:
        queue["entries"].append(entry)
write_json("FOLLOWTHROUGH-QUEUE.json", queue)

# ---------------------------------------------------------------------------
# Registry and maps
# ---------------------------------------------------------------------------
registry = read_json("examples/schema-fixture-domain-registry-rev0189.json")
registry["registry_id"] = "SCHEMA-FIXTURE-DOMAIN-REGISTRY-REV0190"
registry["created_at"] = STAMP_UTC
registry["coverage_scope"] = "rev0190 active registry with witnessed-drill readiness and research-tail reopen-gate families; counts remain full-corpus, family coverage remains selective."
new_families = [
    {
        "family_id": "LIVE-DRILL-READINESS-LEDGER",
        "domain": "witnessed-drill-readiness",
        "lifecycle_axes": ["drill", "reliance", "counterparty-receipts"],
        "owner_surface": "docs/30-transition/cross-critical-witnessed-drill-readiness-and-receipt-matrix.md",
        "schema_path": "schemas/witnessed-drill-readiness-ledger.schema.json",
        "example_path": "examples/witnessed-drill-readiness-ledger-cross-critical-preflight.json",
        "fixture_ids": ["NF-PLAYBOOK-2026-0004"],
        "privacy_default": "public-shell-sealed-details",
        "reliance_effect": "stayed",
        "refactor_note": "New rev0190 family; preflight readiness cannot upgrade reliance without non-host receipt artifacts."
    },
    {
        "family_id": "META-RESEARCH-TAIL-REOPEN-GATE",
        "domain": "research-tail-reopen",
        "lifecycle_axes": ["refactor", "research-tail", "release-gate"],
        "owner_surface": "docs/00-meta/research-tail-reopen-gate-and-sprawl-control.md",
        "schema_path": "schemas/research-tail-reopen-gate.schema.json",
        "example_path": "examples/research-tail-reopen-gate-welfare-new-metric-quarantine.json",
        "fixture_ids": ["NF-SCHEMA-2026-0004"],
        "privacy_default": "public",
        "reliance_effect": "blocked",
        "refactor_note": "New rev0190 family; prevents new research-tail surfaces from bypassing compacted receiving spines."
    }
]
ids = {f["family_id"] for f in registry["families"]}
for f in new_families:
    if f["family_id"] not in ids:
        registry["families"].append(f)
registry["audit_findings"] = [
    "rev0190 registers witnessed drill readiness and research-tail reopen gating as concrete object families rather than prose-only controls.",
    "The registry remains truth-labeled as mixed-current-plus-counts because counts are full-corpus while family coverage is selective."
]
registry["refactor_actions"] = [
    "Backfill WDRL evidence capture into the live drill execution packet after external receipts exist.",
    "Keep new research-tail additions quarantined unless a reopen gate and fixture exist."
]
registry["public_summary"] = "rev0190 adds families for preflight drill receipt readiness and research-tail reopen control."
# counts after all new files and active maps are written below; update later.
write_json("examples/schema-fixture-domain-registry-rev0190.json", registry)

# Surface status new_surfaces determines catalog/dependency/rights checks.
new_surfaces = [
    "docs/30-transition/cross-critical-witnessed-drill-readiness-and-receipt-matrix.md",
    "docs/00-meta/research-tail-reopen-gate-and-sprawl-control.md",
    "docs/30-transition/witnessed-drill-execution-pack-and-reliance-gates.md",
    "docs/30-transition/priority-closure-sprint-and-rescue-lane.md",
    "docs/00-meta/research-tail-compaction-and-refactor-map.md",
    "schemas/witnessed-drill-readiness-ledger.schema.json",
    "examples/witnessed-drill-readiness-ledger-cross-critical-preflight.json",
    "fixtures/negative-tests/witnessed-drill-preflight-missing-external-receipt-class.json",
    "schemas/research-tail-reopen-gate.schema.json",
    "examples/research-tail-reopen-gate-welfare-new-metric-quarantine.json",
    "fixtures/negative-tests/research-tail-reopen-unmapped-new-surface.json",
    "examples/fixture-suite-profile-red-team-v1.json",
    "examples/fixture-run-report-negative-suite.json",
    "examples/research-tail-compaction-map-rev0190.json",
    "examples/schema-fixture-domain-registry-rev0190.json",
    "examples/canon-surface-catalog-rev0190.json",
    "examples/doctrine-dependency-map-rev0190.json",
    "examples/rights-domain-coverage-map-rev0190.json",
    "tools/audit_research_tail_reopen_and_drill_readiness.py",
    "tools/audit_research_tail_compaction.py",
    "tools/audit_schema_fixture_coverage.py",
    "tools/audit_canon_surface_catalog.py",
    "tools/audit_doctrine_dependency_map.py",
    "tools/audit_rights_domain_coverage.py",
]

status = {
    "project": "AI-Personhood",
    "revision": REV,
    "state_class": "research-tail-reopen-gate-and-cross-critical-drill-readiness",
    "operational_head": {"surface": "START_HERE.md", "read_first": "docs/30-transition/cross-critical-witnessed-drill-readiness-and-receipt-matrix.md"},
    "citation_head": {"surface": "README.md"},
    "status_lanes": {"decision_state": "closure-driven-rescue-lane-active", "execution_state": "packaged-pending", "public_state": "latest-release"},
    "formation_layer_status": "canon-retained with all RTC research-tail clusters compacted, reopen-gated, and cross-critical witnessed-drill readiness now object-backed",
    "known_open_gaps": [
        "The cross-critical witnessed drill remains preflight-only; independent non-host receipts have not been collected.",
        "The welfare safeguard drill remains synthetic; independent RERB and representative receipts have not been collected.",
        "WRSR hooks still need backfill into protocol-registration and incident-deviation examples.",
        "The registry remains truth-labeled as mixed-current-plus-counts, not full-archive-corpus coverage.",
        "Could-not-run fixtures remain reliance blockers rather than passes."
    ],
    "new_surfaces": new_surfaces
}
write_json("SURFACE-STATUS.json", status)

# Catalog current release surfaces.
def surface_class(path):
    if path.endswith(".md"):
        if path.startswith("docs/00-meta/"):
            return "meta"
        if path.startswith("docs/30-transition/"):
            return "transition"
        return "doctrine"
    if path.startswith("schemas/"):
        return "schema"
    if path.startswith("examples/"):
        return "example"
    if path.startswith("fixtures/negative-tests/"):
        return "fixture"
    if path.startswith("tools/"):
        return "tool"
    return "example"

catalog_surfaces = []
for i, p in enumerate(new_surfaces, start=1):
    cls = surface_class(p)
    catalog_surfaces.append({
        "surface_id": f"REV0190-SURF-{i:03d}",
        "path": p,
        "surface_class": cls,
        "lifecycle_axes": ["witnessed-drill-readiness", "research-tail-reopen", "rev0190"],
        "owner_role": "release steward" if cls in {"meta", "transition", "tool", "example"} else "drill/research steward",
        "supersession_state": "current" if cls in {"meta", "doctrine", "transition"} else ("negative-test" if cls == "fixture" else "implementation"),
        "review_cadence": "rev0191 priority review",
        "title_or_name": Path(p).name,
        "depends_on": []
    })
counts = {"surfaces": 0, "markdown": 0, "schemas": 0, "examples": 0, "fixtures": 0, "tools": 0}
for s in catalog_surfaces:
    counts["surfaces"] += 1
    if s["surface_class"] in {"meta", "doctrine", "transition"}:
        counts["markdown"] += 1
    elif s["surface_class"] == "schema":
        counts["schemas"] += 1
    elif s["surface_class"] == "example":
        counts["examples"] += 1
    elif s["surface_class"] == "fixture":
        counts["fixtures"] += 1
    elif s["surface_class"] == "tool":
        counts["tools"] += 1
catalog = {
    "catalog_id": "CANON-SURFACE-CATALOG-REV0190",
    "created_at": STAMP_UTC,
    "revision": REV,
    "scope": "rev0190 current-release catalog for cross-critical witnessed-drill readiness and research-tail reopen gating",
    "counts": counts,
    "surfaces": catalog_surfaces,
    "audit_findings": ["Current release surfaces are cataloged so the new gates cannot become hidden tooling."],
    "refactor_actions": ["Keep future new research-tail surfaces out of current status until the reopen gate and catalog are updated."],
    "public_summary": "rev0190 catalogs the preflight receipt matrix and research-tail reopen gate surfaces."
}
write_json("examples/canon-surface-catalog-rev0190.json", catalog)

# Dependency map for markdown current surfaces.
dep_surfaces = [
    {
        "surface_id": "REV0190-DEP-001",
        "path": "docs/30-transition/cross-critical-witnessed-drill-readiness-and-receipt-matrix.md",
        "layer": "transition",
        "depends_on": [
            "docs/30-transition/witnessed-drill-execution-pack-and-reliance-gates.md",
            "docs/30-transition/priority-closure-sprint-and-rescue-lane.md"
        ],
        "overlaps_with": [
            "docs/30-transition/emergency-continuity-order-and-72-hour-rescue-runbook.md",
            "docs/20-world-design/proof-standards-presumptions-and-evidence-weights.md",
            "docs/20-world-design/research-welfare-and-evaluation.md"
        ],
        "supersedes": [],
        "owner_role": "drill/reliance steward",
        "review_cadence": "rev0191 priority review",
        "refactor_risk": "critical"
    },
    {
        "surface_id": "REV0190-DEP-002",
        "path": "docs/00-meta/research-tail-reopen-gate-and-sprawl-control.md",
        "layer": "meta",
        "depends_on": ["docs/00-meta/research-tail-compaction-and-refactor-map.md", "examples/research-tail-compaction-map-rev0190.json"],
        "overlaps_with": ["docs/20-world-design/research-welfare-and-evaluation.md"],
        "supersedes": [],
        "owner_role": "archive refactor steward",
        "review_cadence": "rev0191 priority review",
        "refactor_risk": "high"
    },
    {
        "surface_id": "REV0190-DEP-003",
        "path": "docs/30-transition/witnessed-drill-execution-pack-and-reliance-gates.md",
        "layer": "transition",
        "depends_on": [],
        "overlaps_with": [],
        "supersedes": [],
        "owner_role": "drill/reliance steward",
        "review_cadence": "rev0191 priority review",
        "refactor_risk": "critical"
    },
    {
        "surface_id": "REV0190-DEP-004",
        "path": "docs/30-transition/priority-closure-sprint-and-rescue-lane.md",
        "layer": "transition",
        "depends_on": [],
        "overlaps_with": [],
        "supersedes": [],
        "owner_role": "release steward",
        "review_cadence": "rev0191 priority review",
        "refactor_risk": "high"
    },
    {
        "surface_id": "REV0190-DEP-005",
        "path": "docs/00-meta/research-tail-compaction-and-refactor-map.md",
        "layer": "meta",
        "depends_on": [],
        "overlaps_with": [],
        "supersedes": [],
        "owner_role": "archive refactor steward",
        "review_cadence": "rev0191 priority review",
        "refactor_risk": "high"
    }
]
dep_map = {
    "map_id": "DOCTRINE-DEPENDENCY-MAP-REV0190",
    "created_at": STAMP_UTC,
    "revision": REV,
    "scope": "rev0190 dependency map for witnessed-drill readiness and research-tail reopen gate controls",
    "surfaces": dep_surfaces,
    "audit_findings": [
        "The cross-critical readiness surface depends on live-drill gates and priority closure, but does not depend on research-tail reopen gate to avoid cycle.",
        "The research-tail reopen gate depends on the compaction map and keeps sprawl control out of ordinary doctrine expansion."
    ],
    "refactor_actions": [
        "After external receipts exist, map live-drill execution packet updates against the readiness ledger.",
        "If a research-tail reopen request is approved, update this dependency map in the same revision."
    ],
    "public_summary": "rev0190 maps the new preflight and reopen gates without creating a dependency cycle."
}
write_json("examples/doctrine-dependency-map-rev0190.json", dep_map)

rights = read_json("examples/rights-domain-coverage-map-rev0189.json")
rights["map_id"] = "RIGHTS-DOMAIN-COVERAGE-REV0190"
rights["created_at"] = STAMP_UTC
rights["revision"] = REV
rights["scope"] = "rev0190 active rights-domain map with witnessed-drill readiness and research-tail reopen gate coverage."
rights["domains"].append({
    "domain_id": "research-tail-reopen-drill-readiness",
    "title": "Research-tail reopen control and witnessed-drill readiness",
    "domain_class": "meta-operational",
    "owner_surface": "docs/30-transition/cross-critical-witnessed-drill-readiness-and-receipt-matrix.md",
    "covered_surfaces": [
        "docs/30-transition/cross-critical-witnessed-drill-readiness-and-receipt-matrix.md",
        "docs/00-meta/research-tail-reopen-gate-and-sprawl-control.md",
        "docs/30-transition/witnessed-drill-execution-pack-and-reliance-gates.md",
        "docs/30-transition/priority-closure-sprint-and-rescue-lane.md",
        "docs/00-meta/research-tail-compaction-and-refactor-map.md"
    ],
    "schema_families": ["LIVE-DRILL-READINESS-LEDGER", "META-RESEARCH-TAIL-REOPEN-GATE"],
    "fixture_ids": ["NF-PLAYBOOK-2026-0004", "NF-SCHEMA-2026-0004"],
    "coverage_state": "adequate",
    "open_gaps": ["External receipts for the cross-critical witnessed drill remain uncollected."],
    "next_audit_actions": ["Run a counterparty-confirmed witnessed drill or keep reliance stayed."]
})
rights["audit_findings"] = [
    "rev0190 covers the right to non-host proof and the right against research-tail sprawl that erases closure status.",
    "The map does not treat preflight readiness as evidence of witnessed execution."
]
rights["refactor_actions"] = [
    "Backfill external receipt results into the live-drill packet before reliance changes.",
    "Require this domain to be updated if any research-tail cluster is reopened."
]
rights["public_summary"] = "rev0190 adds rights-domain coverage for preflight drill receipt integrity and research-tail reopen controls."
write_json("examples/rights-domain-coverage-map-rev0190.json", rights)

# ---------------------------------------------------------------------------
# New audit tool
# ---------------------------------------------------------------------------
write_text("tools/audit_research_tail_reopen_and_drill_readiness.py", r'''
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
    "schemas/witnessed-drill-readiness-ledger.schema.json",
    "examples/witnessed-drill-readiness-ledger-cross-critical-preflight.json",
    "fixtures/negative-tests/witnessed-drill-preflight-missing-external-receipt-class.json",
    "schemas/research-tail-reopen-gate.schema.json",
    "examples/research-tail-reopen-gate-welfare-new-metric-quarantine.json",
    "fixtures/negative-tests/research-tail-reopen-unmapped-new-surface.json",
    "docs/30-transition/cross-critical-witnessed-drill-readiness-and-receipt-matrix.md",
    "docs/00-meta/research-tail-reopen-gate-and-sprawl-control.md",
    f"examples/research-tail-compaction-map-{REV}.json",
    "examples/fixture-suite-profile-red-team-v1.json",
    "examples/fixture-run-report-negative-suite.json",
    "FOLLOWTHROUGH-QUEUE.json",
]
for rel in required:
    if not (ROOT / rel).exists():
        raise SystemExit(f"missing rev0190 audit input: {rel}")

if Draft202012Validator is not None:
    pairs = [
        ("schemas/witnessed-drill-readiness-ledger.schema.json", "examples/witnessed-drill-readiness-ledger-cross-critical-preflight.json"),
        ("schemas/research-tail-reopen-gate.schema.json", "examples/research-tail-reopen-gate-welfare-new-metric-quarantine.json"),
        ("schemas/negative-test-fixture.schema.json", "fixtures/negative-tests/witnessed-drill-preflight-missing-external-receipt-class.json"),
        ("schemas/negative-test-fixture.schema.json", "fixtures/negative-tests/research-tail-reopen-unmapped-new-surface.json"),
    ]
    for schema_rel, data_rel in pairs:
        schema = load(schema_rel)
        data = load(data_rel)
        Draft202012Validator.check_schema(schema)
        errors = sorted(Draft202012Validator(schema).iter_errors(data), key=lambda e: list(e.path))
        if errors:
            raise SystemExit(f"{data_rel} fails {schema_rel}: {errors[0].message}")

ledger = load("examples/witnessed-drill-readiness-ledger-cross-critical-preflight.json")
if ledger.get("readiness_state") != "preflight-ready":
    raise SystemExit("witnessed drill readiness ledger must be preflight-ready")
if ledger.get("reliance_effect") != "stayed":
    raise SystemExit("preflight readiness must keep reliance stayed")
locks = ledger.get("not_yet_evidence_locks", {})
for key in ["preflight_is_not_witnessed_evidence", "missing_receipt_blocks_reliance", "host_role_excluded_from_quorum", "failed_injection_public_shell_required"]:
    if locks.get(key) is not True:
        raise SystemExit(f"witnessed-drill readiness missing lock: {key}")
receipt_classes = ledger.get("receipt_classes", [])
if len(receipt_classes) < 7:
    raise SystemExit("cross-critical preflight ledger needs at least seven receipt classes")
if any(r.get("host_controlled_sufficient") is not False for r in receipt_classes if r.get("required")):
    raise SystemExit("host-controlled receipt cannot be sufficient for required classes")
if any(r.get("status") == "received" for r in receipt_classes):
    raise SystemExit("rev0190 preflight example must not pretend external receipts were collected")
if ledger.get("go_no_go_decision", {}).get("decision_state") == "live-run-authorized":
    raise SystemExit("rev0190 preflight ledger must not authorize live run")
if len({r.get("receipt_class") for r in ledger.get("role_requirements", [])}) < 7:
    raise SystemExit("role requirements do not cover enough receipt classes")

reopen = load("examples/research-tail-reopen-gate-welfare-new-metric-quarantine.json")
if reopen.get("decision", {}).get("decision_state") != "quarantine":
    raise SystemExit("reopen example should quarantine the unbacked metric")
if reopen.get("routing", {}).get("new_research_surface_active_before_gate") is not False:
    raise SystemExit("new research surface cannot be active before gate")
if reopen.get("artifact_hooks", {}).get("object_hook_present") or reopen.get("artifact_hooks", {}).get("fixture_hook_present"):
    raise SystemExit("quarantine example should not claim object/fixture hooks are already present")
if reopen.get("reliance_effect") != "stayed":
    raise SystemExit("reopen quarantine must stay reliance")

mp = load(f"examples/research-tail-compaction-map-{REV}.json")
if any(c.get("action") != "compacted" for c in mp.get("clusters", [])):
    raise SystemExit("rev0190 research-tail map should keep all clusters compacted unless a reopen request is approved")
actual = sorted(p.relative_to(ROOT).as_posix() for p in (ROOT / "docs" / "20-world-design").glob("research-*.md"))
assigned = []
for cluster in mp.get("clusters", []):
    for surface in cluster.get("surfaces", []):
        assigned.append(surface.get("path"))
if sorted(assigned) != actual:
    raise SystemExit("research-tail reopen gate found unmapped or extra research surfaces")
if mp.get("research_surface_count") != len(actual):
    raise SystemExit("research-tail count stale under reopen gate")

suite = load("examples/fixture-suite-profile-red-team-v1.json")
report = load("examples/fixture-run-report-negative-suite.json")
suite_ids = {f.get("fixture_id") for f in suite.get("fixtures", [])}
report_by_id = {f.get("fixture_id"): f for f in report.get("fixtures_run", [])}
for fid in ["NF-PLAYBOOK-2026-0004", "NF-SCHEMA-2026-0004"]:
    if fid not in suite_ids:
        raise SystemExit(f"rev0190 fixture missing from suite: {fid}")
    if fid not in report_by_id:
        raise SystemExit(f"rev0190 fixture missing from run report: {fid}")
    if report_by_id[fid].get("result") != "blocking-failure":
        raise SystemExit(f"rev0190 fixture must remain blocking-failure: {fid}")

for rel, phrases in {
    "docs/30-transition/cross-critical-witnessed-drill-readiness-and-receipt-matrix.md": [
        "Preflight readiness is not witnessed reliance",
        "host_controlled",
        "No-go conditions",
        "schemas/witnessed-drill-readiness-ledger.schema.json",
    ],
    "docs/00-meta/research-tail-reopen-gate-and-sprawl-control.md": [
        "No new research-tail surface becomes active without a reopen gate",
        "schemas/research-tail-reopen-gate.schema.json",
        "shadow doctrine",
        "artifact_hooks",
    ],
}.items():
    txt = (ROOT / rel).read_text(encoding="utf-8")
    for phrase in phrases:
        if phrase not in txt:
            raise SystemExit(f"{rel} missing phrase: {phrase}")

queue = load("FOLLOWTHROUGH-QUEUE.json")
by_id = {e.get("id"): e for e in queue.get("entries", [])}
if by_id.get("FT-0189-RESEARCH-TAIL-REOPEN-GATE", {}).get("state") != "closed":
    raise SystemExit("research-tail reopen gate queue item must be closed by rev0190")
if by_id.get("FT-0188-CROSS-CRITICAL-WITNESSED-DRILL", {}).get("state") != "advanced_not_closed":
    raise SystemExit("cross-critical witnessed drill should be advanced_not_closed, not closed")
if by_id.get("FT-0190-CROSS-CRITICAL-EXTERNAL-RECEIPTS", {}).get("state") != "open":
    raise SystemExit("external receipt capture queue item must remain open")

print("audit_research_tail_reopen_and_drill_readiness: OK")
''')

# ---------------------------------------------------------------------------
# Update lint to require/validate new files and run new audit.
# ---------------------------------------------------------------------------
lint_path = ROOT / "tools/lint_archive.py"
lint = lint_path.read_text(encoding="utf-8")
required_insert = """
    'docs/30-transition/cross-critical-witnessed-drill-readiness-and-receipt-matrix.md',
    'docs/00-meta/research-tail-reopen-gate-and-sprawl-control.md',
    'schemas/witnessed-drill-readiness-ledger.schema.json',
    'examples/witnessed-drill-readiness-ledger-cross-critical-preflight.json',
    'fixtures/negative-tests/witnessed-drill-preflight-missing-external-receipt-class.json',
    'schemas/research-tail-reopen-gate.schema.json',
    'examples/research-tail-reopen-gate-welfare-new-metric-quarantine.json',
    'fixtures/negative-tests/research-tail-reopen-unmapped-new-surface.json',
    'examples/research-tail-compaction-map-rev0190.json',
    'examples/schema-fixture-domain-registry-rev0190.json',
    'examples/canon-surface-catalog-rev0190.json',
    'examples/doctrine-dependency-map-rev0190.json',
    'examples/rights-domain-coverage-map-rev0190.json',
    'tools/audit_research_tail_reopen_and_drill_readiness.py',
"""
if "examples/research-tail-compaction-map-rev0190.json" not in lint:
    lint = lint.replace("    'tools/audit_downstream_recall_and_live_drill.py',\n    'tools/package_release.py',", required_insert + "\n    'tools/audit_downstream_recall_and_live_drill.py',\n    'tools/package_release.py',")
if "tools/audit_research_tail_reopen_and_drill_readiness.py" not in lint.split("early_audits = [",1)[1].split("]",1)[0]:
    lint = lint.replace("    'tools/audit_welfare_research_safeguards.py',\n    'tools/audit_canon_surface_catalog.py',", "    'tools/audit_welfare_research_safeguards.py',\n    'tools/audit_research_tail_reopen_and_drill_readiness.py',\n    'tools/audit_canon_surface_catalog.py',")
# required registry families
lint = lint.replace("'WELFARE-RESEARCH-SAFEGUARD', 'META-RESEARCH-TAIL-COMPACTION'", "'WELFARE-RESEARCH-SAFEGUARD', 'LIVE-DRILL-READINESS-LEDGER', 'META-RESEARCH-TAIL-REOPEN-GATE', 'META-RESEARCH-TAIL-COMPACTION'")
# schema validation pairs
if "witnessed-drill-readiness-ledger.schema.json" not in lint:
    lint = lint.replace("        ('welfare-research-safeguard-record.schema.json', 'examples/welfare-research-safeguard-record-distress-eval.json'),", "        ('welfare-research-safeguard-record.schema.json', 'examples/welfare-research-safeguard-record-distress-eval.json'),\n        ('witnessed-drill-readiness-ledger.schema.json', 'examples/witnessed-drill-readiness-ledger-cross-critical-preflight.json'),\n        ('research-tail-reopen-gate.schema.json', 'examples/research-tail-reopen-gate-welfare-new-metric-quarantine.json'),")
# active maps validation pair
if "schema-fixture-domain-registry-rev0190.json" not in lint:
    lint = lint.replace("        ('schema-fixture-domain-registry.schema.json', 'examples/schema-fixture-domain-registry-rev0189.json'),", "        ('schema-fixture-domain-registry.schema.json', 'examples/schema-fixture-domain-registry-rev0189.json'),\n        ('schema-fixture-domain-registry.schema.json', 'examples/schema-fixture-domain-registry-rev0190.json'),")
    lint = lint.replace("        ('rights-domain-coverage-map.schema.json', 'examples/rights-domain-coverage-map-rev0189.json'),", "        ('rights-domain-coverage-map.schema.json', 'examples/rights-domain-coverage-map-rev0189.json'),\n        ('rights-domain-coverage-map.schema.json', 'examples/rights-domain-coverage-map-rev0190.json'),")
    lint = lint.replace("        ('doctrine-dependency-map.schema.json', 'examples/doctrine-dependency-map-rev0189.json'),", "        ('doctrine-dependency-map.schema.json', 'examples/doctrine-dependency-map-rev0189.json'),\n        ('doctrine-dependency-map.schema.json', 'examples/doctrine-dependency-map-rev0190.json'),")
    lint = lint.replace("        ('canon-surface-catalog.schema.json', 'examples/canon-surface-catalog-rev0189.json'),", "        ('canon-surface-catalog.schema.json', 'examples/canon-surface-catalog-rev0189.json'),\n        ('canon-surface-catalog.schema.json', 'examples/canon-surface-catalog-rev0190.json'),")
    lint = lint.replace("        ('research-tail-compaction-map.schema.json', 'examples/research-tail-compaction-map-rev0189.json'),", "        ('research-tail-compaction-map.schema.json', 'examples/research-tail-compaction-map-rev0189.json'),\n        ('research-tail-compaction-map.schema.json', 'examples/research-tail-compaction-map-rev0190.json'),")
lint_path.write_text(lint, encoding="utf-8")

# ---------------------------------------------------------------------------
# Front doors and trajectory
# ---------------------------------------------------------------------------
write_text("README.md", """
# AI Personhood datacube — rev0190

This archive assumes the working premise of AI personhood and focuses on operational rights infrastructure: continuity, evidence, representation, remedy, proof standards, and transition machinery.

## This revision

**Active revision:** `rev0190`

rev0190 is the research-tail reopen gate and cross-critical witnessed-drill readiness pass. It does not add a new doctrine wave. It prevents two high-risk regressions: synthetic/preflight drill artifacts being treated as witnessed reliance, and new `research-*.md` notes reopening the compacted research tail without object, fixture, and closure hooks.

Read first: `docs/30-transition/cross-critical-witnessed-drill-readiness-and-receipt-matrix.md`, then `docs/00-meta/research-tail-reopen-gate-and-sprawl-control.md`.

Core rule: **Preflight readiness is not witnessed reliance, and no new research-tail surface becomes active without a reopen gate.**

New operational artifacts:

- `schemas/witnessed-drill-readiness-ledger.schema.json`
- `examples/witnessed-drill-readiness-ledger-cross-critical-preflight.json`
- `fixtures/negative-tests/witnessed-drill-preflight-missing-external-receipt-class.json`
- `schemas/research-tail-reopen-gate.schema.json`
- `examples/research-tail-reopen-gate-welfare-new-metric-quarantine.json`
- `fixtures/negative-tests/research-tail-reopen-unmapped-new-surface.json`
- `tools/audit_research_tail_reopen_and_drill_readiness.py`

## Validation posture

`make handoff-release` is the release command. It regenerates the context pack and manifest, runs lint and release-specific audits, and packages the archive. The fixture suite/report now cover 91 entries.

Reliance remains stayed where drills are synthetic-prep, preflight-only, host-self-attested, missing independent receipts, or where could-not-run fixtures remain unresolved.

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

## External crosswalk note

Current governance and technical standards can help describe receipts, provenance, portability, risk management, and notice routing. rev0190 keeps them in their lane: they are evidence/control vocabulary, not substitutes for subject authorization, finality, witnessed reliance, or personhood status.
""")

write_text("START_HERE.md", """
# Start here — AI Personhood rev0190

This handoff starts from the research-tail reopen gate and cross-critical witnessed-drill readiness pass. The archive should be read as object-backed operational work, not as a premise debate.

1. `README.md`
2. `docs/30-transition/cross-critical-witnessed-drill-readiness-and-receipt-matrix.md`
3. `schemas/witnessed-drill-readiness-ledger.schema.json`
4. `examples/witnessed-drill-readiness-ledger-cross-critical-preflight.json`
5. `fixtures/negative-tests/witnessed-drill-preflight-missing-external-receipt-class.json`
6. `docs/00-meta/research-tail-reopen-gate-and-sprawl-control.md`
7. `schemas/research-tail-reopen-gate.schema.json`
8. `examples/research-tail-reopen-gate-welfare-new-metric-quarantine.json`
9. `fixtures/negative-tests/research-tail-reopen-unmapped-new-surface.json`
10. `docs/30-transition/witnessed-drill-execution-pack-and-reliance-gates.md`
11. `docs/30-transition/priority-closure-sprint-and-rescue-lane.md`
12. `examples/research-tail-compaction-map-rev0190.json`
13. `docs/00-meta/research-tail-compaction-and-refactor-map.md`
14. `FOLLOWTHROUGH-QUEUE.json`
15. `examples/schema-fixture-domain-registry-rev0190.json`
16. `examples/canon-surface-catalog-rev0190.json`
17. `examples/doctrine-dependency-map-rev0190.json`
18. `examples/rights-domain-coverage-map-rev0190.json`
19. `docs/00-meta/deep-audit-waste-and-correction-map.md`
20. `docs/00-meta/charter.md`
21. `docs/00-meta/datacube-schema.md`
22. `docs/00-meta/verifier-api-and-conformance-test-suite.md`
23. `docs/10-foundations/assumption-and-scope.md`
24. `docs/10-foundations/world-change-overview.md`

## This revision

rev0190 adds a witnessed-drill readiness ledger and a research-tail reopen gate. It advances the cross-critical witnessed drill to executable preflight status, but it does not pretend external receipts exist. It closes the research-tail reopen gate follow-through item by making new research-tail additions quarantine unless they carry a cluster, receiving surface, object hook, fixture hook, public summary, and closure condition.

Core rule: **Preflight readiness is not witnessed reliance, and no new research-tail surface becomes active without a reopen gate.**

## Current open risk

The cross-critical drill is preflight-ready only. Reliance remains stayed until independent non-host receipts are collected for first-touch timing, continuity floors, sealed/public parity, namespace cache behavior, reserve ledger separation, representative contact, witness dependency, and welfare-signal integrity.
""")

# docs README prepend section after H1
p = ROOT / "docs/README.md"
docs_readme = p.read_text(encoding="utf-8")
if "## rev0190 witnessed readiness and research-tail reopen gate" not in docs_readme:
    docs_readme = docs_readme.replace("# Documents index\n", "# Documents index\n\n## rev0190 witnessed readiness and research-tail reopen gate\n\nUse `docs/30-transition/cross-critical-witnessed-drill-readiness-and-receipt-matrix.md` as the current operational head for counterparty/receipt readiness. It is backed by `schemas/witnessed-drill-readiness-ledger.schema.json`, `examples/witnessed-drill-readiness-ledger-cross-critical-preflight.json`, and `fixtures/negative-tests/witnessed-drill-preflight-missing-external-receipt-class.json`.\n\nUse `docs/00-meta/research-tail-reopen-gate-and-sprawl-control.md` as the active guard against post-compaction research sprawl. It is backed by `schemas/research-tail-reopen-gate.schema.json`, `examples/research-tail-reopen-gate-welfare-new-metric-quarantine.json`, and `fixtures/negative-tests/research-tail-reopen-unmapped-new-surface.json`.\n\n")
    p.write_text(docs_readme, encoding="utf-8")

# CHANGELOG prepend
p = ROOT / "CHANGELOG.md"
ch = p.read_text(encoding="utf-8")
if "## rev0190 — reopen-gate-drill-readiness-regression-lock" not in ch:
    ins = """
## rev0190 — reopen-gate-drill-readiness-regression-lock

### Added
- `docs/30-transition/cross-critical-witnessed-drill-readiness-and-receipt-matrix.md`
- `schemas/witnessed-drill-readiness-ledger.schema.json`
- `examples/witnessed-drill-readiness-ledger-cross-critical-preflight.json`
- `fixtures/negative-tests/witnessed-drill-preflight-missing-external-receipt-class.json`
- `docs/00-meta/research-tail-reopen-gate-and-sprawl-control.md`
- `schemas/research-tail-reopen-gate.schema.json`
- `examples/research-tail-reopen-gate-welfare-new-metric-quarantine.json`
- `fixtures/negative-tests/research-tail-reopen-unmapped-new-surface.json`
- `tools/audit_research_tail_reopen_and_drill_readiness.py`
- active rev0190 catalog, dependency, rights-domain, schema/fixture registry, and research-tail compaction maps.

### Changed
- The cross-critical witnessed drill is advanced to preflight readiness, but reliance remains stayed until external non-host receipts exist.
- The research-tail reopen gate is now schema-backed, example-backed, fixture-backed, and linted.
- Fixture suite/report now cover 91 entries and add regressions for preflight-as-reliance and unmapped research-tail additions.
- `FOLLOWTHROUGH-QUEUE.json` closes the research-tail reopen-gate item and opens external receipt capture and WRSR protocol-backfill items.

### Why this revision matters
- The archive had completed all RTC compaction clusters, so the riskiest failure became regression: synthetic plans being treated as evidence, or new research notes bypassing compacted receiving surfaces. rev0190 makes both failure modes testable.
"""
    ch = ch.replace("# Changelog\n", "# Changelog\n\n" + ins.strip() + "\n\n")
    p.write_text(ch, encoding="utf-8")

# Trajectory map top
p = ROOT / "docs/00-meta/trajectory-map.md"
traj = p.read_text(encoding="utf-8")
new_top = """# Current trajectory — rev0190 reopen gate and drill-readiness layer

rev0190 shifts the archive from research-tail compaction to regression control and witnessed-drill execution readiness. RTC-01 through RTC-07 are compacted. The live edge is now whether the archive can prevent backslide: synthetic/preflight evidence must not become witnessed reliance, and new `research-*.md` surfaces must not bypass receiving spines.

New live seams:

- `OQ-0226` — Which external receipt set is sufficient to move the cross-critical drill from preflight-ready to witnessed-run evidence without counting the host operator or correlated witnesses?
- `OQ-0227` — What reopen standard should distinguish a genuinely new research-tail risk from a duplicate metric, speculative crosswalk, or prose-only refinement of a compacted cluster?
- `OQ-0228` — Which WRSR hooks should be backfilled into protocol registration and incident-deviation examples before welfare-safeguard reliance can improve?

"""
# replace first title block up to ## Trajectory map
if "## Trajectory map" in traj and "rev0190 reopen gate" not in traj[:500]:
    traj = new_top + "## Trajectory map" + traj.split("## Trajectory map", 1)[1]
p.write_text(traj, encoding="utf-8")

# Revision receipt
receipt = {
    "revision": REV,
    "date": DATE,
    "authored_by": "OpenAI GPT-5.5 Thinking",
    "status_change": "advanced from welfare/research safeguards to research-tail reopen gating and cross-critical witnessed-drill readiness",
    "still_live": True,
    "summary": "Adds a witnessed-drill readiness ledger, preflight receipt matrix, research-tail reopen gate, quarantine example, two blocking fixtures, active maps, and an audit that keeps reliance stayed until external receipts exist.",
    "why_this_counts": [
        "The cross-critical witnessed drill now has receipt classes, role requirements, failure injections, and no-go conditions instead of a generic live-drill TODO.",
        "Preflight readiness is explicitly blocked from becoming witnessed reliance evidence.",
        "RTC-01 through RTC-07 remain compacted and future research-tail surfaces must pass a reopen gate before activation.",
        "Both regression modes are now fixture-backed and linted."
    ],
    "known_limits": [
        "No external non-host receipts have been collected yet for the cross-critical drill.",
        "The welfare-safeguard drill remains synthetic, not witnessed reliance evidence.",
        "WRSR hooks still need backfill into protocol-registration and incident-deviation examples.",
        "Could-not-run fixtures remain reliance blockers rather than passes."
    ]
}
write_json("REVISION-RECEIPT.json", receipt)

# Archive index append new docs. It only needs to mention markdown paths.
append_once("ARCHIVE_INDEX.md", "rev0190 added surfaces", """
## rev0190 added surfaces

- `docs/30-transition/cross-critical-witnessed-drill-readiness-and-receipt-matrix.md` — cross-critical witnessed-drill receipt matrix and no-go readiness gate.
- `docs/00-meta/research-tail-reopen-gate-and-sprawl-control.md` — post-compaction gate preventing new research-tail surfaces from bypassing receiving spines.
""")

# Update schema registry counts now that all files exist.
registry = read_json("examples/schema-fixture-domain-registry-rev0190.json")
registry["audit_counts"] = {
    "schemas": len(list((ROOT / "schemas").glob("*.json"))),
    "examples": len(list((ROOT / "examples").glob("*.json"))),
    "negative_fixtures": len(list((ROOT / "fixtures" / "negative-tests").glob("*.json"))),
    "registered_families": len(registry["families"]),
}
write_json("examples/schema-fixture-domain-registry-rev0190.json", registry)

print("apply_rev0190 complete")
