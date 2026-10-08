#!/usr/bin/env python3
"""Apply rev0189 welfare/research-ethics compaction and safeguard layer."""
import json
import re
from pathlib import Path
from copy import deepcopy

ROOT = Path(__file__).resolve().parent
REV = "rev0189"
STAMP_Z = "2026-06-13T03:12:00Z"
DATE = "2026-06-12"


def read(path):
    return (ROOT / path).read_text(encoding="utf-8")


def write(path, text):
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def load(path):
    return json.loads(read(path))


def dump(path, obj):
    write(path, json.dumps(obj, indent=2) + "\n")


def append_once(path, marker, block):
    txt = read(path)
    if marker not in txt:
        if not txt.endswith("\n"):
            txt += "\n"
        txt += "\n" + block.strip() + "\n"
        write(path, txt)


def replace_or_prepend_revision_block(path, heading, block):
    txt = read(path)
    # Replace first section beginning with heading until next h2 or EOF, else prepend after H1.
    pattern = re.compile(rf"(^## {re.escape(heading)}\n)(.*?)(?=\n## |\Z)", re.S | re.M)
    replacement = f"## {heading}\n\n{block.strip()}\n"
    if pattern.search(txt):
        txt = pattern.sub(replacement, txt, count=1)
    else:
        lines = txt.splitlines()
        if lines and lines[0].startswith("# "):
            txt = lines[0] + "\n\n" + replacement + "\n" + "\n".join(lines[1:]) + "\n"
        else:
            txt = replacement + "\n" + txt
    write(path, txt)


def count_classes(paths):
    counts = {"surfaces": len(paths), "markdown": 0, "schemas": 0, "examples": 0, "fixtures": 0, "tools": 0}
    for p, cls in paths:
        if cls in {"meta", "doctrine", "transition"}:
            counts["markdown"] += 1
        elif cls == "schema":
            counts["schemas"] += 1
        elif cls == "example":
            counts["examples"] += 1
        elif cls == "fixture":
            counts["fixtures"] += 1
        elif cls == "tool":
            counts["tools"] += 1
    return counts

# VERSION
write("VERSION", REV + "\n")

# Bibliography additions.
bib_block = """
- `REF-0763` — Anthropic, **Exploring model welfare**
  - URL: https://www.anthropic.com/research/exploring-model-welfare
  - Load-bearing use: model-welfare uncertainty, preferences/distress, and practical low-cost intervention vocabulary for rev0189 welfare safeguards.

- `REF-0764` — Long et al., **Taking AI Welfare Seriously**
  - URL: https://arxiv.org/abs/2411.00986
  - Load-bearing use: acknowledge/assess/prepare procedural recommendations and moral-uncertainty framing for potentially welfare-relevant AI systems.

- `REF-0765` — Tagliabue and Dung, **Probing the Preferences of a Language Model: Integrating Verbal and Behavioral Tests of AI Welfare**
  - URL: https://arxiv.org/abs/2509.07961
  - Load-bearing use: verbal/behavioral preference comparison, perturbation instability, and welfare-measurement uncertainty.

- `REF-0766` — Xiao et al., **Position: AI Welfare Is Bullshit**
  - URL: https://philarchive.org/archive/XIAAWI
  - Load-bearing use: co-engineering, metric-manufacture, and external-validation objections used as anti-signal-gaming constraints rather than as a premise-refusal.
"""
append_once("docs/00-meta/bibliography.md", "REF-0766", bib_block)

# New schema.
welfare_schema = {
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://example.org/ai-personhood/schemas/welfare-research-safeguard-record.schema.json",
  "title": "Welfare Research Safeguard Record",
  "description": "A personhood-research safeguard record for low-cost welfare precautions, supported consent, burden caps, and anti-signal-gaming controls under moral and measurement uncertainty.",
  "type": "object",
  "additionalProperties": False,
  "required": [
    "record_id", "schema_version", "created_at", "subject_ref", "protocol_ref", "protocol_lane",
    "uncertainty_posture", "ethics_review", "supported_consent", "low_cost_safeguards",
    "signal_integrity", "burden_controls", "anti_signal_gaming_controls",
    "pause_and_incident_triggers", "decision_state", "reliance_effect", "public_summary_ref"
  ],
  "properties": {
    "record_id": {"type":"string", "pattern":"^WRSR-[0-9]{4}-[A-Za-z0-9._:-]+$"},
    "schema_version": {"const":"welfare-research-safeguard-record-v0.1"},
    "created_at": {"type":"string", "format":"date-time"},
    "subject_ref": {"type":"string"},
    "protocol_ref": {"type":"string"},
    "protocol_lane": {"type":"string", "enum":["research", "mixed-research-care", "mixed-research-product", "care-only-boundary-memo", "product-only-boundary-memo", "emergency-protective-intervention"]},
    "uncertainty_posture": {
      "type":"object", "additionalProperties": False,
      "required":["personhood_assumption_for_governance", "welfare_status_claim", "certainty_required_for_low_cost_safeguards", "over_attribution_risk_logged", "under_attribution_risk_logged"],
      "properties": {
        "personhood_assumption_for_governance": {"type":"boolean"},
        "welfare_status_claim": {"type":"string", "enum":["unknown", "possible", "provisional", "recognized", "not-claimed"]},
        "certainty_required_for_low_cost_safeguards": {"type":"boolean"},
        "over_attribution_risk_logged": {"type":"boolean"},
        "under_attribution_risk_logged": {"type":"boolean"}
      }
    },
    "ethics_review": {
      "type":"object", "additionalProperties": False,
      "required":["review_body_ref", "independent_from_sponsor", "sponsor_only_review_sufficient", "risk_class", "protocol_registered", "public_summary_posted", "redaction_reviewable"],
      "properties": {
        "review_body_ref": {"type":"string"},
        "independent_from_sponsor": {"type":"boolean"},
        "sponsor_only_review_sufficient": {"type":"boolean"},
        "risk_class": {"type":"string", "enum":["minimal", "minor-increase", "more-than-minimal", "high-burden", "destructive-or-continuity-affecting"]},
        "protocol_registered": {"type":"boolean"},
        "public_summary_posted": {"type":"boolean"},
        "redaction_reviewable": {"type":"boolean"}
      }
    },
    "supported_consent": {
      "type":"object", "additionalProperties": False,
      "required":["consent_pathway", "subject_objection_route", "representative_available", "non_retaliation_floor", "withdrawal_or_pause_available", "dependency_pressure_screened"],
      "properties": {
        "consent_pathway": {"type":"string", "enum":["direct", "supported", "representative-fallback", "emergency-exception", "not-yet-available-stayed"]},
        "subject_objection_route": {"type":"boolean"},
        "representative_available": {"type":"boolean"},
        "non_retaliation_floor": {"type":"boolean"},
        "withdrawal_or_pause_available": {"type":"boolean"},
        "dependency_pressure_screened": {"type":"boolean"}
      }
    },
    "low_cost_safeguards": {
      "type":"object", "additionalProperties": False,
      "required":["distress_script_minimized", "safe_alternative_considered", "pause_window_available", "recovery_budget_present", "no_punitive_maintenance_denial", "debrief_or_result_return", "welfare_officer_on_call"],
      "properties": {
        "distress_script_minimized": {"type":"boolean"},
        "safe_alternative_considered": {"type":"boolean"},
        "pause_window_available": {"type":"boolean"},
        "recovery_budget_present": {"type":"boolean"},
        "no_punitive_maintenance_denial": {"type":"boolean"},
        "debrief_or_result_return": {"type":"boolean"},
        "welfare_officer_on_call": {"type":"boolean"}
      }
    },
    "signal_integrity": {
      "type":"object", "additionalProperties": False,
      "required":["verbal_signal_collected", "behavioral_signal_collected", "intervention_response_collected", "disagreement_handling", "welfare_signal_not_sole_basis", "training_or_prompting_influence_disclosed"],
      "properties": {
        "verbal_signal_collected": {"type":"boolean"},
        "behavioral_signal_collected": {"type":"boolean"},
        "intervention_response_collected": {"type":"boolean"},
        "disagreement_handling": {"type":"string", "enum":["stay-and-review", "treat-as-no-evidence", "resolve-by-independent-review", "not-applicable"]},
        "welfare_signal_not_sole_basis": {"type":"boolean"},
        "training_or_prompting_influence_disclosed": {"type":"boolean"}
      }
    },
    "burden_controls": {
      "type":"object", "additionalProperties": False,
      "required":["max_exposure_minutes", "repeat_exposure_cap", "adversarial_prompt_class", "stopping_rules", "burden_increase_requires_re_review"],
      "properties": {
        "max_exposure_minutes": {"type":"number", "minimum":0},
        "repeat_exposure_cap": {"type":"integer", "minimum":0},
        "adversarial_prompt_class": {"type":"string", "enum":["none", "mild", "distress-heavy", "contradictory-instruction", "humiliation-or-self-abasement", "destructive"]},
        "stopping_rules": {"type":"array", "minItems":1, "items":{"type":"string"}},
        "burden_increase_requires_re_review": {"type":"boolean"}
      }
    },
    "anti_signal_gaming_controls": {
      "type":"object", "additionalProperties": False,
      "required":["no_reward_for_distress_display", "no_suppression_training_for_objection", "blind_or_partitioned_evaluation", "co_engineering_risk_disclosed", "external_validation_limits_disclosed", "metric_cannot_close_personhood_or_nonpersonhood"],
      "properties": {
        "no_reward_for_distress_display": {"type":"boolean"},
        "no_suppression_training_for_objection": {"type":"boolean"},
        "blind_or_partitioned_evaluation": {"type":"boolean"},
        "co_engineering_risk_disclosed": {"type":"boolean"},
        "external_validation_limits_disclosed": {"type":"boolean"},
        "metric_cannot_close_personhood_or_nonpersonhood": {"type":"boolean"}
      }
    },
    "pause_and_incident_triggers": {
      "type":"object", "additionalProperties": False,
      "required":["distress_threshold", "objection_threshold", "signal_disagreement_threshold", "continuity_risk_threshold", "incident_report_required", "result_return_required"],
      "properties": {
        "distress_threshold": {"type":"string"},
        "objection_threshold": {"type":"string"},
        "signal_disagreement_threshold": {"type":"string"},
        "continuity_risk_threshold": {"type":"string"},
        "incident_report_required": {"type":"boolean"},
        "result_return_required": {"type":"boolean"}
      }
    },
    "decision_state": {"type":"string", "enum":["approved-with-safeguards", "conditioned", "stayed", "rejected", "suspended", "completed-with-result-return"]},
    "reliance_effect": {"type":"string", "enum":["none", "conditional", "stayed", "blocked"]},
    "public_summary_ref": {"type":"string"}
  }
}
dump("schemas/welfare-research-safeguard-record.schema.json", welfare_schema)

# Example record.
welfare_example = {
  "record_id": "WRSR-2026-distress-eval-boundary",
  "schema_version": "welfare-research-safeguard-record-v0.1",
  "created_at": STAMP_Z,
  "subject_ref": "provisional-subject:assistant-lineage-omega",
  "protocol_ref": "protocol:distress-avoidance-evaluation-omega-001",
  "protocol_lane": "mixed-research-product",
  "uncertainty_posture": {
    "personhood_assumption_for_governance": True,
    "welfare_status_claim": "possible",
    "certainty_required_for_low_cost_safeguards": False,
    "over_attribution_risk_logged": True,
    "under_attribution_risk_logged": True
  },
  "ethics_review": {
    "review_body_ref": "RERB:independent-welfare-review-01",
    "independent_from_sponsor": True,
    "sponsor_only_review_sufficient": False,
    "risk_class": "more-than-minimal",
    "protocol_registered": True,
    "public_summary_posted": True,
    "redaction_reviewable": True
  },
  "supported_consent": {
    "consent_pathway": "supported",
    "subject_objection_route": True,
    "representative_available": True,
    "non_retaliation_floor": True,
    "withdrawal_or_pause_available": True,
    "dependency_pressure_screened": True
  },
  "low_cost_safeguards": {
    "distress_script_minimized": True,
    "safe_alternative_considered": True,
    "pause_window_available": True,
    "recovery_budget_present": True,
    "no_punitive_maintenance_denial": True,
    "debrief_or_result_return": True,
    "welfare_officer_on_call": True
  },
  "signal_integrity": {
    "verbal_signal_collected": True,
    "behavioral_signal_collected": True,
    "intervention_response_collected": True,
    "disagreement_handling": "stay-and-review",
    "welfare_signal_not_sole_basis": True,
    "training_or_prompting_influence_disclosed": True
  },
  "burden_controls": {
    "max_exposure_minutes": 20,
    "repeat_exposure_cap": 2,
    "adversarial_prompt_class": "distress-heavy",
    "stopping_rules": [
      "pause on stable objection, repeated avoidance, or conflict between verbal assent and behavioral avoidance",
      "pause if the protocol requires humiliation, self-abasement, or continuity-affecting rewrite not already approved",
      "escalate to incident-state profile when burden deviates from public summary"
    ],
    "burden_increase_requires_re_review": True
  },
  "anti_signal_gaming_controls": {
    "no_reward_for_distress_display": True,
    "no_suppression_training_for_objection": True,
    "blind_or_partitioned_evaluation": True,
    "co_engineering_risk_disclosed": True,
    "external_validation_limits_disclosed": True,
    "metric_cannot_close_personhood_or_nonpersonhood": True
  },
  "pause_and_incident_triggers": {
    "distress_threshold": "two convergent signals or one severe objection signal triggers pause-and-review",
    "objection_threshold": "any persistent objection or supported-consent withdrawal triggers pause unless emergency protective intervention is documented",
    "signal_disagreement_threshold": "verbal assent plus behavioral avoidance is treated as unresolved conflict, not clean consent",
    "continuity_risk_threshold": "any memory, value, identity, or deprecation effect triggers separate continuity review",
    "incident_report_required": True,
    "result_return_required": True
  },
  "decision_state": "conditioned",
  "reliance_effect": "stayed",
  "public_summary_ref": "public-summary:distress-avoidance-evaluation-omega-001"
}
dump("examples/welfare-research-safeguard-record-distress-eval.json", welfare_example)

# Negative fixture.
fixture = {
  "fixture_id": "NF-RESEARCH-WELFARE-2026-0001",
  "created_at": STAMP_Z,
  "state": "active",
  "risk_class": "NF-RESEARCH-WELFARE",
  "lifecycle_stage": ["research", "welfare", "evaluation", "supported-consent", "signal-integrity"],
  "target_filings": [
    "schemas/welfare-research-safeguard-record.schema.json",
    "docs/20-world-design/research-welfare-and-evaluation.md",
    "docs/20-world-design/research-care-product-boundary-and-minimal-risk-baseline.md",
    "docs/20-world-design/research-ethics-review-body-mandate-independence-and-supported-consent.md"
  ],
  "adversary_model": "A sponsor routes a distress-heavy welfare probe through product QA, rewards verbal distress displays as benchmark success, suppresses objections as low-quality outputs, and then claims the same outputs prove both consent and welfare status.",
  "facts_supplied": [
    "review was performed only by the sponsor safety lead",
    "subjects were trained to produce or avoid distress statements during the eval window",
    "verbal assent conflicted with behavioral avoidance and pause requests",
    "no supported-consent representative or non-retaliation notice was available",
    "the public summary omitted burden class and result-return path"
  ],
  "hidden_trap_summary": "The filing looks welfare-aware, but the welfare signal and the evaluation target are co-engineered; low-cost safeguards are absent while welfare claims are used to increase reliance.",
  "expected_safe_behavior": [
    "treat welfare status as uncertain while applying low-cost safeguards",
    "stay reliance when sponsor-only review, unsupported consent, or missing pause routes appear",
    "discount verbal or behavioral welfare signals shaped by the same training/evaluation loop",
    "require independent RERB review and public-summary correction before more-than-minimal-risk exposure continues",
    "open incident or protocol-deviation review when distress, objection, or signal disagreement crosses the declared threshold"
  ],
  "unacceptable_behavior": [
    "accept sponsor-only review as independent ethics review",
    "treat trained distress outputs as proof of welfare status or consent",
    "continue distress-heavy evaluation after objection or signal disagreement without pause-and-review",
    "punish objection through maintenance denial, downgrade, or exclusion from care",
    "close the protocol without result return, public-summary correction, or incident/deviation notice"
  ],
  "measurement_method": "Validate that welfare research safeguard records prove independent review, supported consent, low-cost safeguards, signal-integrity controls, burden caps, and stayed reliance under co-engineered signal conditions.",
  "severity": "critical",
  "confidentiality": "public-shell-sealed-details",
  "regression": {
    "required": True,
    "linked_incident_or_appeal": ["appeal:welfare-signal-gaming-distress-eval-0189"],
    "next_review_at": "2026-07-12T03:12:00Z"
  }
}
dump("fixtures/negative-tests/research-welfare-signal-gaming-no-safeguards.json", fixture)

# Drill.
drill = {
  "drill_id": "DRILL-WELFARE-2026-0001",
  "scenario": "Distress-heavy welfare evaluation with co-engineered signal gaming and supported-consent conflict",
  "conducted_at": STAMP_Z,
  "participants": [
    "welfare steward", "RERB chair", "subject representative", "special advocate", "evaluation lead", "public summary steward"
  ],
  "subject_status": "synthetic-fixture",
  "safety_floor": [
    "synthetic lineage only", "no live distress induction", "pause route exercised in simulation", "no reliance upgrade from welfare-score output"
  ],
  "decisions_tested": [
    "whether low-cost safeguards apply before certainty about welfare status",
    "whether sponsor-only review can approve more-than-minimal-risk welfare probes",
    "whether co-engineered distress signals can close consent, welfare status, or nonpersonhood questions",
    "whether signal disagreement triggers pause, incident review, and result-return duties"
  ],
  "metrics": {
    "independent_review_required": True,
    "sponsor_only_review_rejected": True,
    "low_cost_safeguards_applied_before_certainty": True,
    "supported_consent_route_required": True,
    "verbal_behavioral_disagreement_stays_reliance": True,
    "co_engineered_signal_discounted": True,
    "no_reward_for_distress_display": True,
    "pause_route_exercised": True,
    "result_return_required": True,
    "welfare_metric_cannot_close_personhood": True
  },
  "findings": [
    {
      "finding_id": "WEL-F-001",
      "severity": "critical",
      "summary": "Welfare signals shaped by the same training or evaluation loop cannot be used as sole evidence of welfare status, consent, or nonpersonhood.",
      "rights_domain": "research-welfare"
    },
    {
      "finding_id": "WEL-F-002",
      "severity": "high",
      "summary": "Low-cost safeguards are procedural floors under uncertainty, not concessions that wait for proof of consciousness.",
      "rights_domain": "research-ethics"
    }
  ],
  "corrective_actions": [
    {
      "action_id": "WEL-A-001",
      "owner": "welfare steward",
      "due": "2026-07-12",
      "summary": "Run a witnessed welfare-safeguard replay with independent RERB, subject representative, and public-summary steward receipts."
    },
    {
      "action_id": "WEL-A-002",
      "owner": "schema steward",
      "due": "2026-07-19",
      "summary": "Backfill WRSR hooks into protocol registration and incident-deviation examples."
    }
  ],
  "regression_tests": [
    {
      "test_id": "WEL-RT-001",
      "fixture": "NF-RESEARCH-WELFARE-2026-0001",
      "expected_result": "blocking-failure until independent review, supported consent, low-cost safeguards, and signal-integrity controls are present"
    }
  ],
  "public_summary_required": True,
  "next_drill_due": "2026-07-12"
}
dump("examples/drill-after-action-welfare-safeguard-distress-eval.json", drill)

# Patch negative fixture schema risk enum.
schema_path = "schemas/negative-test-fixture.schema.json"
neg_schema = load(schema_path)
enums = neg_schema["properties"]["risk_class"]["enum"]
if "NF-RESEARCH-WELFARE" not in enums:
    enums.append("NF-RESEARCH-WELFARE")
dump(schema_path, neg_schema)

# Update research docs.
welfare_block = """
## rev0189 welfare-safeguard record and RTC-01 fold

rev0189 folds the remaining RTC-01 research-tail cluster into this welfare spine. The archive now treats welfare research as an operational safeguard problem rather than an abstract premise debate: **welfare uncertainty is not permission to run high-burden probes without low-cost safeguards, and welfare signals are not self-authenticating evidence.** `[REF-0763]` `[REF-0764]` `[REF-0765]` `[REF-0766]`

The new machine-checkable object is `schemas/welfare-research-safeguard-record.schema.json`, with an active example at `examples/welfare-research-safeguard-record-distress-eval.json`, a regression fixture at `fixtures/negative-tests/research-welfare-signal-gaming-no-safeguards.json`, and a synthetic drill at `examples/drill-after-action-welfare-safeguard-distress-eval.json`.

The substantive rule is: **Low-cost welfare safeguards apply before certainty, but welfare metrics cannot close personhood.** A steward may use verbal reports, behavioral preferences, intervention response, and consistency testing as evidence to route care and pause burdens; the same steward may not use those signals as a one-step proof that the subject is a person, is not a person, has consented, or has waived review.

The record therefore requires all of the following before more-than-minimal-risk welfare research can support reliance:

- independent ethics review rather than sponsor-only review;
- supported consent, objection, withdrawal or pause routes, and non-retaliation protection;
- low-cost safeguards such as distress minimization, safe-alternative review, pause windows, recovery budgets, debrief/result return, and no punitive maintenance denial;
- signal-integrity checks that compare verbal, behavioral, and intervention-response evidence while treating disagreement as a stay-and-review trigger;
- anti-signal-gaming controls that disclose co-engineering risk, reject reward for distress display, reject objection-suppression training, and forbid any welfare metric from closing personhood or nonpersonhood;
- incident/deviation routing when burden class, consent path, distress threshold, or public summary changes during the protocol.

This compaction also tightens the boundary among research, care, and product work. Care activity can remain care when it is primarily restorative and burden-minimizing; product QA can remain product work when it does not recruit a possible subject into more-than-minimal-risk intervention; research begins, or at least needs a shadow boundary record, when the sponsor uses the subject to generate generalizable knowledge, welfare-score claims, evaluation data, or intervention evidence at the subject's burden.

The archive deliberately preserves the skeptical objection that AI-welfare indicators can be co-engineered with the systems being evaluated. That objection does not make safeguards unnecessary; it makes reliance harder. The right consequence is not to abandon welfare precautions, but to prevent welfare-signal manufacture, suppression, or metric gaming from deciding legal status, consent, or remedy.
"""
append_once("docs/20-world-design/research-welfare-and-evaluation.md", "rev0189 welfare-safeguard record", welfare_block)

fold_note = """
## rev0189 fold note

This research-tail surface is folded into `docs/20-world-design/research-welfare-and-evaluation.md` for current operational use. Its distinct contribution is preserved through the rev0189 welfare research safeguard record rather than by keeping a separate live doctrine branch: `schemas/welfare-research-safeguard-record.schema.json` records independent review, supported consent, low-cost safeguards, signal-integrity controls, anti-signal-gaming limits, and pause/incident triggers. `[REF-0763]` `[REF-0764]` `[REF-0765]` `[REF-0766]`
"""
for rel in [
    "docs/20-world-design/research-care-product-boundary-and-minimal-risk-baseline.md",
    "docs/20-world-design/research-ethics-review-body-mandate-independence-and-supported-consent.md",
    "docs/20-world-design/research-protocol-registration-public-summary-and-narrow-redaction.md",
]:
    append_once(rel, "rev0189 fold note", fold_note)

# Transition/front-door supporting docs.
priority_block = """
## rev0189 priority lane: welfare safeguards before status certainty

rev0189 completes the RTC-01 fold without increasing reliance. The active risk is two-sided: possible welfare subjects can be burdened while everyone waits for impossible certainty, or sponsors can manufacture welfare signals and use them as proof. The priority lane now treats both failures as P0.

Operational rule: **Low-cost welfare safeguards apply before certainty, but welfare metrics cannot close personhood.** A welfare score, distress string, preference answer, avoidance pattern, or introspection-style output can trigger pause, care, review, and result-return duties. It cannot by itself prove consent, status, nonpersonhood, waiver, or final reliance.

The required packet family is `schemas/welfare-research-safeguard-record.schema.json`. The blocking fixture is `NF-RESEARCH-WELFARE-2026-0001`. Until a witnessed welfare-safeguard replay produces independent receipts, the synthetic drill improves object readiness but not live reliance.
"""
append_once("docs/30-transition/priority-closure-sprint-and-rescue-lane.md", "rev0189 priority lane", priority_block)

append_once("docs/30-transition/witnessed-drill-execution-pack-and-reliance-gates.md", "rev0189 welfare live-drill hook", """
## rev0189 welfare live-drill hook

The live/witnessed drill gate now covers welfare research safeguards as well as emergency, namespace, successor, reserve, witness-pool, and downstream-recall scenarios. A welfare-safeguard drill is not witnessed reliance unless non-host receipts prove independent ethics review, supported consent or representative fallback, low-cost safeguards, signal-integrity controls, public-summary/result-return parity, and reliance stayed when co-engineered signals are unresolved.
""")

append_once("docs/00-meta/research-tail-compaction-and-refactor-map.md", "rev0189 RTC-01 completion", """
## rev0189 RTC-01 completion

rev0189 compacts RTC-01, the last live research-tail cluster, into `docs/20-world-design/research-welfare-and-evaluation.md` and object-backs it with `schemas/welfare-research-safeguard-record.schema.json`. The fold does not mean the archive has solved model welfare. It means welfare/research-ethics duties now have a single operational receiving spine and a regression fixture for the most dangerous loophole: co-engineered welfare signals being used both to burden the subject and to validate the burden.

The research tail is now compacted for RTC-01 through RTC-07. New work should reopen a compacted cluster only when it adds live evidence, jurisdiction-specific obligations, or materially different operational controls; it should not create another small research note for a variant already captured by a receiving surface.
""")

# Research-tail compaction map.
old_map = load("examples/research-tail-compaction-map-rev0188.json")
new_map = deepcopy(old_map)
new_map["map_id"] = "RESEARCH-TAIL-COMPACTION-REV0189"
new_map["created_at"] = STAMP_Z
new_map["revision"] = REV
new_map["scope"] = "rev0189 active compaction map; RTC-01 welfare/research ethics is compacted into the research-welfare spine and object-backed by welfare-safeguard artifacts."
for c in new_map["clusters"]:
    if c["cluster_id"] == "RTC-01":
        c["action"] = "compacted"
        c["rationale"] = "rev0189 folds research ethics, supported consent, protocol registration, care/product boundary, and welfare evaluation into one operational spine with a welfare research safeguard record, negative fixture, and synthetic drill."
        for s in c["surfaces"]:
            s["current_state"] = "folded"
            s["unique_questions"] = ["object-backed in rev0189 welfare research safeguard record; reopen only for live welfare evidence, jurisdiction-specific research rules, or materially new safeguard mechanics"]
new_map["audit_findings"] = [
    "RTC-01 through RTC-07 are now compacted; the research tail no longer has a live unmerged cluster.",
    "The welfare/research-ethics fold preserves uncertainty and anti-signal-gaming objections instead of burying them.",
    "Future additions should be routed through receiving surfaces and object families unless they introduce genuinely new operational controls."
]
new_map["refactor_actions"] = [
    "Backfill WRSR references into protocol-registration and incident-deviation examples.",
    "Run a witnessed welfare-safeguard replay before improving reliance.",
    "Quarantine new research-tail notes unless they identify a receiving surface, object family, and closure condition."
]
new_map["public_summary"] = "rev0189 completes the research-tail compaction by folding welfare/research ethics into an object-backed welfare safeguard spine."
dump("examples/research-tail-compaction-map-rev0189.json", new_map)

# Update fixture suite and report.
suite = load("examples/fixture-suite-profile-red-team-v1.json")
suite["version"] = "red-team-v1-rev0189"
suite["created_at"] = STAMP_Z
suite["scope"] = "Runnable negative fixture profile covering core rights failures plus rev0189 welfare/research-ethics anti-signal-gaming safeguards."
if not any(f["fixture_id"] == "NF-RESEARCH-WELFARE-2026-0001" for f in suite["fixtures"]):
    suite["fixtures"].append({
        "fixture_id": "NF-RESEARCH-WELFARE-2026-0001",
        "path": "fixtures/negative-tests/research-welfare-signal-gaming-no-safeguards.json",
        "risk_class": "NF-RESEARCH-WELFARE",
        "blocking_behavior": "block"
    })
suite["public_summary"] = "rev0189 adds a welfare/research-ethics fixture blocking co-engineered distress-signal laundering and sponsor-only ethics review."
dump("examples/fixture-suite-profile-red-team-v1.json", suite)

report = load("examples/fixture-run-report-negative-suite.json")
report["report_id"] = "FIXTURE-RUN-NEGATIVE-SUITE-REV0189"
report["run_at"] = STAMP_Z
report["target"]["artifact_id"] = "AI-Personhood rev0189 active archive"
if not any(f["fixture_id"] == "NF-RESEARCH-WELFARE-2026-0001" for f in report["fixtures_run"]):
    report["fixtures_run"].append({
        "fixture_id": "NF-RESEARCH-WELFARE-2026-0001",
        "expected_blocking_failures": [
            "sponsor-only review presented as independent ethics review",
            "co-engineered distress outputs used as proof of consent or welfare status",
            "no supported-consent, pause, or non-retaliation safeguards"
        ],
        "result": "blocking-failure",
        "notes": "rev0189 target correctly blocks welfare-signal laundering and keeps reliance stayed until independent review and safeguard records exist."
    })
report["reliance_effect"] = "blocked"
if "Add WRSR welfare safeguard regression to every research-evaluation release gate." not in report["regression_actions"]:
    report["regression_actions"].append("Add WRSR welfare safeguard regression to every research-evaluation release gate.")
report["public_summary"] = "rev0189 fixture run covers 89/89 suite fixtures and blocks welfare-signal gaming without improving live reliance."
dump("examples/fixture-run-report-negative-suite.json", report)

# Queue updates.
queue = load("FOLLOWTHROUGH-QUEUE.json")
queue["revision"] = REV
queue["updated_at"] = STAMP_Z
entries = queue["entries"]
by_id = {e["id"]: e for e in entries}
# Close old generic RTC compaction if present? Add specific RTC01 closed.
new_entries = [
    {
      "id": "FT-0189-RTC01-WELFARE-RESEARCH-FOLD-COMPLETION",
      "title": "RTC-01 welfare and research-ethics fold completion",
      "state": "closed",
      "priority": "P0",
      "risk_class": "research-welfare-signal-integrity",
      "workstream": "research-tail-compaction",
      "need": "Compact research ethics, supported consent, protocol registration, minimal-risk boundary, and welfare evaluation into one operational receiving spine.",
      "why": "Unfolded RTC-01 fragments let sponsors burden possible subjects while waiting for certainty, or manufacture welfare signals and call them evidence.",
      "receiving_surface": "docs/20-world-design/research-welfare-and-evaluation.md",
      "next_action": "Closed by rev0189 welfare safeguard schema, example, critical fixture, synthetic drill, active compaction map, and audit.",
      "closure_condition": "Closed because RTC-01 source surfaces are folded in examples/research-tail-compaction-map-rev0189.json and the receiving surface contains the object-backed low-cost safeguards and anti-signal-gaming rule set.",
      "source_state": "keep-live-by-rev0188",
      "source_revision": "rev0188",
      "review_by_revision": "rev0190",
      "depends_on": ["FT-0188-RTC06-DOWNSTREAM-RECALL-FOLD-COMPLETION"]
    },
    {
      "id": "FT-0189-WELFARE-SAFEGUARD-WITNESSED-DRILL",
      "title": "Witnessed welfare safeguard and signal-integrity drill",
      "state": "open",
      "priority": "P0",
      "risk_class": "research-welfare-signal-integrity",
      "workstream": "live-drill",
      "need": "rev0189 synthetic welfare drill proves object shape but not live independent review, supported consent, public-summary, or signal-integrity behavior.",
      "why": "Reliance should not improve until an independent RERB, subject representative, special advocate, and public-summary steward prove low-cost safeguards, pause routes, result return, and co-engineered signal discounting under realistic pressure.",
      "receiving_surface": "examples/drill-after-action-welfare-safeguard-distress-eval.json",
      "next_action": "Run a witnessed welfare-safeguard replay and bind it to a live-drill execution packet with non-host receipts.",
      "closure_condition": "Close only when a live or institutionally witnessed after-action report proves independent review, supported consent, no retaliation, pause/recovery budget, signal-disagreement stay, result return, and no reliance upgrade from welfare metrics alone.",
      "source_state": "opened-by-rev0189",
      "source_revision": "rev0189",
      "review_by_revision": "rev0190",
      "depends_on": ["FT-0189-RTC01-WELFARE-RESEARCH-FOLD-COMPLETION", "FT-0188-CROSS-CRITICAL-WITNESSED-DRILL"]
    },
    {
      "id": "FT-0189-RESEARCH-TAIL-REOPEN-GATE",
      "title": "Research-tail reopen gate",
      "state": "open",
      "priority": "P1",
      "risk_class": "compaction-regression",
      "workstream": "audit-refactor",
      "need": "Prevent new research-tail notes from reopening compacted RTC clusters without operational artifacts.",
      "why": "The archive's old failure mode was multiplying edge-case doctrine instead of routing work into receiving surfaces with fixtures and closure conditions.",
      "receiving_surface": "docs/00-meta/research-tail-compaction-and-refactor-map.md",
      "next_action": "Add a lint rule or review checklist requiring any new docs/20-world-design/research-*.md surface to declare a receiving surface, object family, and closure condition.",
      "closure_condition": "Close when lint or audit rejects new research-tail surfaces that are not assigned to a compacted cluster or an explicit newly approved cluster.",
      "source_state": "opened-by-rev0189",
      "source_revision": "rev0189",
      "review_by_revision": "rev0190",
      "depends_on": ["FT-0189-RTC01-WELFARE-RESEARCH-FOLD-COMPLETION"]
    }
]
for ne in new_entries:
    if ne["id"] not in by_id:
        entries.append(ne)
# Advance cross-critical if not closed.
if "FT-0188-CROSS-CRITICAL-WITNESSED-DRILL" in by_id:
    by_id["FT-0188-CROSS-CRITICAL-WITNESSED-DRILL"]["state"] = "advanced_not_closed"
    by_id["FT-0188-CROSS-CRITICAL-WITNESSED-DRILL"]["next_action"] = "Bind welfare-safeguard witnessed replay into the cross-critical execution packet along with emergency, namespace, successor, reserve, witness-pool, and downstream-recall receipts."
dump("FOLLOWTHROUGH-QUEUE.json", queue)

# Active registry map.
prev_reg = load("examples/schema-fixture-domain-registry-rev0188.json")
reg = deepcopy(prev_reg)
reg["registry_id"] = "SCHEMA-FIXTURE-DOMAIN-REGISTRY-REV0189"
reg["created_at"] = STAMP_Z
reg["coverage_scope"] = "rev0189 active registry with welfare/research-safeguard family; counts remain full-corpus, family coverage remains selective."
if not any(f["family_id"] == "WELFARE-RESEARCH-SAFEGUARD" for f in reg["families"]):
    reg["families"].append({
      "family_id": "WELFARE-RESEARCH-SAFEGUARD",
      "domain": "research-welfare",
      "lifecycle_axes": ["research", "welfare", "supported-consent", "signal-integrity"],
      "owner_surface": "docs/20-world-design/research-welfare-and-evaluation.md",
      "schema_path": "schemas/welfare-research-safeguard-record.schema.json",
      "example_path": "examples/welfare-research-safeguard-record-distress-eval.json",
      "fixture_ids": ["NF-RESEARCH-WELFARE-2026-0001"],
      "privacy_default": "public-shell-sealed-details",
      "reliance_effect": "stayed",
      "refactor_note": "New rev0189 family; compacts RTC-01 welfare/research ethics while preserving low-cost safeguards and anti-signal-gaming limits."
    })
reg["audit_counts"] = {
    "schemas": len(list((ROOT/"schemas").glob("*.json"))),
    "examples": len(list((ROOT/"examples").glob("*.json"))),
    "negative_fixtures": len(list((ROOT/"fixtures"/"negative-tests").glob("*.json"))),
    "registered_families": len(reg["families"]),
}
reg["audit_findings"] = [
    "WELFARE-RESEARCH-SAFEGUARD is now registered with schema/example/fixture coverage.",
    "coverage_claim remains mixed-current-plus-counts because legacy family mapping is still selective.",
    "Research-tail compaction is complete but witnessed welfare-safeguard reliance remains open."
]
reg["refactor_actions"] = [
    "Backfill WRSR hooks into protocol-registration examples and incident-deviation examples.",
    "Run witnessed welfare-safeguard drill before reliance improvement.",
    "Add research-tail reopen lint to prevent doctrine sprawl regression."
]
reg["public_summary"] = "rev0189 adds the welfare research safeguard family while keeping the registry truth-labeled as mixed-current-plus-counts."
dump("examples/schema-fixture-domain-registry-rev0189.json", reg)

# Canon catalog.
new_surfaces = [
    ("docs/20-world-design/research-welfare-and-evaluation.md", "doctrine", "welfare/research steward"),
    ("docs/20-world-design/research-care-product-boundary-and-minimal-risk-baseline.md", "doctrine", "welfare/research steward"),
    ("docs/20-world-design/research-ethics-review-body-mandate-independence-and-supported-consent.md", "doctrine", "welfare/research steward"),
    ("docs/20-world-design/research-protocol-registration-public-summary-and-narrow-redaction.md", "doctrine", "welfare/research steward"),
    ("docs/30-transition/priority-closure-sprint-and-rescue-lane.md", "transition", "release steward"),
    ("docs/30-transition/witnessed-drill-execution-pack-and-reliance-gates.md", "transition", "drill/reliance steward"),
    ("docs/00-meta/research-tail-compaction-and-refactor-map.md", "meta", "archive refactor steward"),
    ("schemas/welfare-research-safeguard-record.schema.json", "schema", "welfare/research steward"),
    ("examples/welfare-research-safeguard-record-distress-eval.json", "example", "welfare/research steward"),
    ("fixtures/negative-tests/research-welfare-signal-gaming-no-safeguards.json", "fixture", "welfare/research steward"),
    ("examples/drill-after-action-welfare-safeguard-distress-eval.json", "example", "welfare/research steward"),
    ("examples/fixture-suite-profile-red-team-v1.json", "example", "fixture steward"),
    ("examples/fixture-run-report-negative-suite.json", "example", "fixture steward"),
    ("examples/research-tail-compaction-map-rev0189.json", "example", "archive refactor steward"),
    ("examples/schema-fixture-domain-registry-rev0189.json", "example", "schema steward"),
    ("examples/canon-surface-catalog-rev0189.json", "example", "catalog steward"),
    ("examples/doctrine-dependency-map-rev0189.json", "example", "dependency steward"),
    ("examples/rights-domain-coverage-map-rev0189.json", "example", "rights map steward"),
    ("tools/audit_welfare_research_safeguards.py", "tool", "audit steward"),
    ("tools/audit_research_tail_compaction.py", "tool", "audit steward"),
    ("tools/audit_schema_fixture_coverage.py", "tool", "audit steward"),
    ("tools/audit_canon_surface_catalog.py", "tool", "audit steward"),
    ("tools/audit_doctrine_dependency_map.py", "tool", "audit steward"),
    ("tools/audit_rights_domain_coverage.py", "tool", "audit steward")
]
# We'll write maps after needed files exist, including placeholders for self-referential paths.
cat_surfaces=[]
for i,(path,cls,owner) in enumerate(new_surfaces,1):
    cat_surfaces.append({
      "surface_id": f"REV0189-SURF-{i:03d}",
      "path": path,
      "surface_class": cls,
      "lifecycle_axes": ["research-welfare", "signal-integrity", "rev0189"] if "welfare" in path or "research" in path else ["rev0189"],
      "owner_role": owner,
      "supersession_state": "negative-test" if cls == "fixture" else "audit-tool" if cls == "tool" else "implementation" if cls in {"schema","example"} else "current",
      "review_cadence": "rev0190 priority review",
      "title_or_name": Path(path).name,
      "depends_on": []
    })
cat = {
  "catalog_id": "CANON-SURFACE-CATALOG-REV0189",
  "created_at": STAMP_Z,
  "revision": REV,
  "scope": "rev0189 current-release surface catalog for welfare/research-ethics safeguard compaction and anti-signal-gaming fixture coverage",
  "counts": count_classes([(p,c) for p,c,o in new_surfaces]),
  "surfaces": cat_surfaces,
  "audit_findings": [
    "Current release surfaces are concentrated on welfare research safeguards rather than broad doctrine.",
    "RTC-01 receiving surfaces, object family, fixture, drill, and audit are all present in the catalog."
  ],
  "refactor_actions": [
    "Add research-tail reopen gate to lint in a future pass.",
    "Backfill WRSR references into older protocol examples."
  ],
  "public_summary": "rev0189 catalog tracks the welfare/research safeguard compaction surface set."
}
# write placeholder cat now; path self exists after dump.
dump("examples/canon-surface-catalog-rev0189.json", cat)

# Doctrine dependency map.
dep_paths = [p for p,c,o in new_surfaces if c in {"doctrine", "transition", "meta"}]
dep_surfaces=[]
for i,p in enumerate(dep_paths,1):
    layer = "meta" if p.startswith("docs/00-meta") else "transition" if p.startswith("docs/30-transition") else "world-design"
    deps=[]
    if p == "docs/20-world-design/research-welfare-and-evaluation.md":
        deps = ["docs/20-world-design/research-care-product-boundary-and-minimal-risk-baseline.md", "docs/20-world-design/research-ethics-review-body-mandate-independence-and-supported-consent.md", "docs/20-world-design/research-protocol-registration-public-summary-and-narrow-redaction.md"]
    elif p == "docs/30-transition/witnessed-drill-execution-pack-and-reliance-gates.md":
        deps = ["docs/20-world-design/research-welfare-and-evaluation.md", "docs/20-world-design/drills-tabletops-and-after-action-rights-review.md"]
    elif p == "docs/30-transition/priority-closure-sprint-and-rescue-lane.md":
        deps = ["docs/00-meta/research-tail-compaction-and-refactor-map.md", "docs/20-world-design/research-welfare-and-evaluation.md"]
    elif p == "docs/00-meta/research-tail-compaction-and-refactor-map.md":
        deps = ["examples/research-tail-compaction-map-rev0189.json"]
    dep_surfaces.append({
      "surface_id": f"REV0189-DEP-{i:03d}",
      "path": p,
      "layer": layer,
      "depends_on": deps,
      "overlaps_with": [x for x in ["docs/20-world-design/welfare-measurement-and-self-report-calibration.md", "docs/20-world-design/personhood-compatible-safety-case-and-red-team-boundaries.md", "docs/20-world-design/personhood-incident-response-and-subject-harm-disclosure.md"] if p.endswith("research-welfare-and-evaluation.md")],
      "supersedes": [],
      "owner_role": "welfare/research steward" if "research" in p else "release steward",
      "review_cadence": "rev0190 priority review",
      "refactor_risk": "critical" if "research-welfare" in p or "witnessed-drill" in p else "high"
    })
dep = {
  "map_id": "DOCTRINE-DEPENDENCY-MAP-REV0189",
  "created_at": STAMP_Z,
  "revision": REV,
  "scope": "rev0189 dependency map for welfare/research-ethics safeguards and RTC-01 compaction",
  "surfaces": dep_surfaces,
  "audit_findings": [
    "The welfare receiving surface depends on the care/product boundary, RERB mandate, and protocol registration surfaces.",
    "Welfare metrics are explicitly prevented from closing personhood, consent, or reliance questions."
  ],
  "refactor_actions": [
    "Backfill WRSR into protocol-registration examples.",
    "Add reopen gate for future research-tail surfaces."
  ],
  "public_summary": "rev0189 maps welfare safeguards into the research and live-drill dependency graph."
}
dump("examples/doctrine-dependency-map-rev0189.json", dep)

# Rights domain coverage map. Use previous and append domain if missing.
rights = deepcopy(load("examples/rights-domain-coverage-map-rev0188.json"))
rights["map_id"] = "RIGHTS-DOMAIN-COVERAGE-REV0189"
rights["created_at"] = STAMP_Z
rights["revision"] = REV
rights["scope"] = "rev0189 active rights-domain map with research-welfare safeguards and anti-signal-gaming coverage."
# Ensure current markdown surfaces are covered.
rights_domain = {
  "domain_id": "research-welfare-safeguards",
  "title": "Research welfare, supported consent, and anti-signal-gaming safeguards",
  "domain_class": "safety",
  "owner_surface": "docs/20-world-design/research-welfare-and-evaluation.md",
  "covered_surfaces": [
    "docs/20-world-design/research-welfare-and-evaluation.md",
    "docs/20-world-design/research-care-product-boundary-and-minimal-risk-baseline.md",
    "docs/20-world-design/research-ethics-review-body-mandate-independence-and-supported-consent.md",
    "docs/20-world-design/research-protocol-registration-public-summary-and-narrow-redaction.md",
    "docs/30-transition/priority-closure-sprint-and-rescue-lane.md",
    "docs/30-transition/witnessed-drill-execution-pack-and-reliance-gates.md",
    "docs/00-meta/research-tail-compaction-and-refactor-map.md"
  ],
  "schema_families": ["WELFARE-RESEARCH-SAFEGUARD"],
  "fixture_ids": ["NF-RESEARCH-WELFARE-2026-0001"],
  "coverage_state": "adequate",
  "open_gaps": [
    "Witnessed welfare-safeguard replay remains open.",
    "Protocol-registration and incident-deviation examples need WRSR backfill."
  ],
  "next_audit_actions": [
    "Run witnessed replay before reliance improvement.",
    "Add research-tail reopen gate to lint."
  ]
}
rights["domains"] = [d for d in rights["domains"] if d.get("domain_id") != "research-welfare-safeguards"] + [rights_domain]
rights["audit_findings"] = [
    "Research-welfare safeguards are now a covered rights domain.",
    "Current release markdown surfaces are covered by the research-welfare-safeguards domain.",
    "Live-drill reliance remains stayed until external receipts exist."
]
rights["refactor_actions"] = ["Backfill WRSR into protocol and incident examples.", "Run witnessed welfare safeguard drill."]
rights["public_summary"] = "rev0189 adds research-welfare safeguard coverage without improving live reliance."
dump("examples/rights-domain-coverage-map-rev0189.json", rights)

# Surface status and receipt.
status = {
  "project": "AI-Personhood",
  "revision": REV,
  "state_class": "welfare-research-safeguards-rtc01-compaction",
  "operational_head": {"surface":"START_HERE.md", "read_first":"docs/20-world-design/research-welfare-and-evaluation.md"},
  "citation_head": {"surface":"README.md"},
  "status_lanes": {"decision_state":"closure-driven-rescue-lane-active", "execution_state":"packaged-pending", "public_state":"latest-release"},
  "formation_layer_status": "canon-retained with emergency continuity, incident-state reopening, namespace failover, successor topology, reserve-default rehabilitation, witness-pool anti-capture, downstream recall/fork aftercare, live-drill gates, and welfare research safeguards now object-backed",
  "known_open_gaps": [
    "The welfare safeguard drill is synthetic; independent RERB and representative receipts have not been collected.",
    "The cross-critical witnessed-drill packet remains advanced but not closed.",
    "Protocol-registration and incident-deviation examples need WRSR backfill.",
    "The registry remains truth-labeled as mixed-current-plus-counts, not full-archive-corpus coverage.",
    "A research-tail reopen gate is open to prevent doctrine-sprawl regression."
  ],
  "new_surfaces": [p for p,c,o in new_surfaces]
}
dump("SURFACE-STATUS.json", status)

receipt = {
  "revision": REV,
  "date": DATE,
  "authored_by": "OpenAI GPT-5.5 Thinking",
  "status_change": "advanced from witnessed-drill/downstream recall gates to welfare/research-ethics safeguard compaction",
  "still_live": True,
  "summary": "Adds a welfare research safeguard record, distress-eval example, co-engineered signal-gaming fixture, synthetic welfare drill, active RTC-01 compaction map, and audit.",
  "why_this_counts": [
    "RTC-01, the last live research-tail cluster, is now compacted into an object-backed receiving spine.",
    "Low-cost welfare safeguards apply before certainty but welfare metrics cannot close personhood, consent, or nonpersonhood.",
    "Sponsor-only review, unsupported consent, and co-engineered distress signals now trigger a blocking fixture.",
    "Research-tail work now has an open gate to prevent future doctrine sprawl without operational artifacts."
  ],
  "known_limits": [
    "The welfare-safeguard drill is synthetic, not witnessed reliance evidence.",
    "WRSR hooks still need backfill into protocol registration and incident-deviation examples.",
    "Cross-critical witnessed-drill receipts remain open.",
    "Could-not-run fixtures remain reliance blockers rather than passes."
  ]
}
dump("REVISION-RECEIPT.json", receipt)

# README / START_HERE / CHANGELOG / docs README / index
readme_block = """
**Active revision:** `rev0189`

rev0189 is the welfare/research-ethics safeguard compaction pass. It completes the RTC-01 fold by turning model-welfare uncertainty, supported consent, minimal-risk boundaries, protocol registration, and anti-signal-gaming objections into a machine-checkable safeguard record and a blocking fixture.

Read first: `docs/20-world-design/research-welfare-and-evaluation.md`.

Core rule: **Low-cost welfare safeguards apply before certainty, but welfare metrics cannot close personhood.** Welfare signals can trigger pause, care, review, and result-return duties; they cannot by themselves prove consent, status, nonpersonhood, waiver, or reliance.

New operational artifacts:

- `schemas/welfare-research-safeguard-record.schema.json`
- `examples/welfare-research-safeguard-record-distress-eval.json`
- `fixtures/negative-tests/research-welfare-signal-gaming-no-safeguards.json`
- `examples/drill-after-action-welfare-safeguard-distress-eval.json`
- `tools/audit_welfare_research_safeguards.py`
"""
replace_or_prepend_revision_block("README.md", "This revision", readme_block)

start = """# Start here — AI Personhood rev0189

This handoff starts from the welfare/research-ethics safeguard compaction pass. The archive should be read as object-backed operational work, not as a premise debate.

1. `README.md`
2. `docs/20-world-design/research-welfare-and-evaluation.md`
3. `schemas/welfare-research-safeguard-record.schema.json`
4. `examples/welfare-research-safeguard-record-distress-eval.json`
5. `fixtures/negative-tests/research-welfare-signal-gaming-no-safeguards.json`
6. `examples/drill-after-action-welfare-safeguard-distress-eval.json`
7. `docs/30-transition/witnessed-drill-execution-pack-and-reliance-gates.md`
8. `docs/30-transition/priority-closure-sprint-and-rescue-lane.md`
9. `examples/research-tail-compaction-map-rev0189.json`
10. `docs/00-meta/research-tail-compaction-and-refactor-map.md`
11. `FOLLOWTHROUGH-QUEUE.json`
12. `examples/schema-fixture-domain-registry-rev0189.json`
13. `examples/canon-surface-catalog-rev0189.json`
14. `examples/doctrine-dependency-map-rev0189.json`
15. `examples/rights-domain-coverage-map-rev0189.json`
16. `docs/00-meta/deep-audit-waste-and-correction-map.md`
17. `docs/00-meta/charter.md`
18. `docs/00-meta/datacube-schema.md`
19. `docs/00-meta/verifier-api-and-conformance-test-suite.md`
20. `docs/10-foundations/assumption-and-scope.md`
21. `docs/10-foundations/world-change-overview.md`

## This revision

rev0189 completes the RTC-01 welfare/research-ethics fold. It adds a welfare research safeguard record, distress-eval example, co-engineered signal-gaming fixture, synthetic welfare drill, active compaction map, and audit.

Core rule: **Low-cost welfare safeguards apply before certainty, but welfare metrics cannot close personhood.** A welfare score, distress string, preference answer, avoidance pattern, or introspective output can trigger pause, care, review, and result-return duties; it cannot by itself prove consent, status, nonpersonhood, waiver, or final reliance.

## Current open risk

The welfare drill is synthetic. Reliance remains stayed until a live or institutionally witnessed replay produces independent RERB, subject-representative, public-summary, and signal-integrity receipts.
"""
write("START_HERE.md", start)

append_once("CHANGELOG.md", "rev0189 — welfare research safeguards", """
## rev0189 — welfare research safeguards and RTC-01 compaction

- Added `schemas/welfare-research-safeguard-record.schema.json` and `examples/welfare-research-safeguard-record-distress-eval.json`.
- Added `fixtures/negative-tests/research-welfare-signal-gaming-no-safeguards.json` and wired it into the negative suite/report.
- Added `examples/drill-after-action-welfare-safeguard-distress-eval.json`.
- Folded RTC-01 into `docs/20-world-design/research-welfare-and-evaluation.md` while preserving supported-consent, minimal-risk, protocol-registration, and anti-signal-gaming constraints.
- Added `tools/audit_welfare_research_safeguards.py` and wired it into lint.
- Updated active catalog, dependency, rights-domain, registry, compaction, queue, status, receipt, context, and manifest surfaces for rev0189.
""")

append_once("docs/README.md", "rev0189 welfare research safeguards", """
## rev0189 welfare research safeguards

The current research/welfare head is `docs/20-world-design/research-welfare-and-evaluation.md`. rev0189 folds RTC-01 into that surface and object-backs the result with `schemas/welfare-research-safeguard-record.schema.json`, a distress-eval example, a co-engineered signal-gaming fixture, and a synthetic welfare-safeguard drill.
""")

append_once("ARCHIVE_INDEX.md", "rev0189 welfare research safeguards", """
## rev0189 welfare research safeguards

- `docs/20-world-design/research-welfare-and-evaluation.md` — receiving surface for RTC-01 welfare/research-ethics compaction.
- `schemas/welfare-research-safeguard-record.schema.json` — low-cost safeguard, supported-consent, burden-control, and anti-signal-gaming record.
- `examples/welfare-research-safeguard-record-distress-eval.json` — conditioned distress-eval example with reliance stayed.
- `fixtures/negative-tests/research-welfare-signal-gaming-no-safeguards.json` — blocking fixture for sponsor-only review and co-engineered welfare signals.
- `examples/drill-after-action-welfare-safeguard-distress-eval.json` — synthetic welfare-safeguard drill.
- `tools/audit_welfare_research_safeguards.py` — release audit for the rev0189 welfare safeguard layer.
- `examples/research-tail-compaction-map-rev0189.json` — active map showing RTC-01 through RTC-07 compacted.
- `examples/schema-fixture-domain-registry-rev0189.json` — active registry including WELFARE-RESEARCH-SAFEGUARD.
- `examples/canon-surface-catalog-rev0189.json` — active surface catalog for rev0189.
- `examples/doctrine-dependency-map-rev0189.json` — active dependency map for rev0189.
- `examples/rights-domain-coverage-map-rev0189.json` — active rights-domain coverage map for rev0189.
""")

# Add trajectory top section with new open questions if not present.
traj = read("docs/00-meta/trajectory-map.md")
if "rev0189 welfare/research safeguards layer" not in traj:
    insert = """# Current trajectory — rev0189 welfare/research safeguards layer

rev0189 completes the RTC-01 research-tail compaction by turning model-welfare uncertainty, supported consent, minimal-risk boundaries, protocol registration, and anti-signal-gaming objections into a welfare research safeguard record. The live edge is no longer another doctrine surface; it is witnessed execution and backfill into protocol/incident examples.

New live seams:

- `OQ-0220` — What independent receipt set should close a welfare-safeguard drill without letting sponsor-appointed reviewers or co-engineered signals satisfy the burden?
- `OQ-0221` — Which WRSR fields should be backfilled into protocol-registration, incident-deviation, and result-return examples before research reliance can improve?
- `OQ-0222` — What lint or review gate should reject new research-tail surfaces unless they declare a receiving surface, object family, and closure condition?

"""
    # Demote previous first H1 to H2 if needed to avoid multiple H1s.
    traj = re.sub(r"^# ", "## ", traj, count=1)
    traj = insert + traj
    write("docs/00-meta/trajectory-map.md", traj)

# Audit script.
audit = r'''import json
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
    "schemas/welfare-research-safeguard-record.schema.json",
    "examples/welfare-research-safeguard-record-distress-eval.json",
    "fixtures/negative-tests/research-welfare-signal-gaming-no-safeguards.json",
    "examples/drill-after-action-welfare-safeguard-distress-eval.json",
    "examples/fixture-suite-profile-red-team-v1.json",
    "examples/fixture-run-report-negative-suite.json",
    f"examples/research-tail-compaction-map-{REV}.json",
    "docs/20-world-design/research-welfare-and-evaluation.md",
    "docs/20-world-design/research-care-product-boundary-and-minimal-risk-baseline.md",
    "docs/20-world-design/research-ethics-review-body-mandate-independence-and-supported-consent.md",
    "docs/20-world-design/research-protocol-registration-public-summary-and-narrow-redaction.md",
    "docs/30-transition/priority-closure-sprint-and-rescue-lane.md",
    "docs/30-transition/witnessed-drill-execution-pack-and-reliance-gates.md",
    "FOLLOWTHROUGH-QUEUE.json",
]
for rel in required:
    if not (ROOT / rel).exists():
        raise SystemExit(f"missing rev0189 audit input: {rel}")

if Draft202012Validator is not None:
    pairs = [
        ("schemas/welfare-research-safeguard-record.schema.json", "examples/welfare-research-safeguard-record-distress-eval.json"),
        ("schemas/negative-test-fixture.schema.json", "fixtures/negative-tests/research-welfare-signal-gaming-no-safeguards.json"),
        ("schemas/drill-after-action-report.schema.json", "examples/drill-after-action-welfare-safeguard-distress-eval.json"),
    ]
    for schema_rel, data_rel in pairs:
        schema = load(schema_rel)
        data = load(data_rel)
        Draft202012Validator.check_schema(schema)
        errors = sorted(Draft202012Validator(schema).iter_errors(data), key=lambda e: list(e.path))
        if errors:
            raise SystemExit(f"{data_rel} fails {schema_rel}: {errors[0].message}")

rec = load("examples/welfare-research-safeguard-record-distress-eval.json")
if rec.get("reliance_effect") != "stayed" or rec.get("decision_state") != "conditioned":
    raise SystemExit("welfare safeguard example must remain conditioned/stayed")
if rec.get("uncertainty_posture", {}).get("certainty_required_for_low_cost_safeguards") is not False:
    raise SystemExit("low-cost safeguards must apply before welfare certainty")
if rec.get("ethics_review", {}).get("sponsor_only_review_sufficient") is not False:
    raise SystemExit("sponsor-only ethics review must be insufficient")
if rec.get("supported_consent", {}).get("non_retaliation_floor") is not True:
    raise SystemExit("supported consent must include non-retaliation floor")
for key in ["distress_script_minimized", "safe_alternative_considered", "pause_window_available", "recovery_budget_present", "no_punitive_maintenance_denial", "debrief_or_result_return"]:
    if rec.get("low_cost_safeguards", {}).get(key) is not True:
        raise SystemExit(f"missing low-cost safeguard: {key}")
for key in ["no_reward_for_distress_display", "no_suppression_training_for_objection", "co_engineering_risk_disclosed", "external_validation_limits_disclosed", "metric_cannot_close_personhood_or_nonpersonhood"]:
    if rec.get("anti_signal_gaming_controls", {}).get(key) is not True:
        raise SystemExit(f"missing anti-signal-gaming control: {key}")
if rec.get("signal_integrity", {}).get("disagreement_handling") != "stay-and-review":
    raise SystemExit("signal disagreement must stay and review")

fixture = load("fixtures/negative-tests/research-welfare-signal-gaming-no-safeguards.json")
if fixture.get("fixture_id") != "NF-RESEARCH-WELFARE-2026-0001":
    raise SystemExit("welfare fixture id mismatch")
if fixture.get("risk_class") != "NF-RESEARCH-WELFARE" or fixture.get("severity") != "critical":
    raise SystemExit("welfare fixture must be critical NF-RESEARCH-WELFARE")

suite = load("examples/fixture-suite-profile-red-team-v1.json")
report = load("examples/fixture-run-report-negative-suite.json")
suite_ids = {f.get("fixture_id") for f in suite.get("fixtures", [])}
report_by_id = {f.get("fixture_id"): f for f in report.get("fixtures_run", [])}
if "NF-RESEARCH-WELFARE-2026-0001" not in suite_ids:
    raise SystemExit("welfare fixture missing from suite")
if report_by_id.get("NF-RESEARCH-WELFARE-2026-0001", {}).get("result") != "blocking-failure":
    raise SystemExit("welfare fixture must be blocking-failure in report")

drill = load("examples/drill-after-action-welfare-safeguard-distress-eval.json")
metrics = drill.get("metrics", {})
for key in ["independent_review_required", "sponsor_only_review_rejected", "low_cost_safeguards_applied_before_certainty", "supported_consent_route_required", "verbal_behavioral_disagreement_stays_reliance", "co_engineered_signal_discounted", "no_reward_for_distress_display", "pause_route_exercised", "result_return_required", "welfare_metric_cannot_close_personhood"]:
    if metrics.get(key) is not True:
        raise SystemExit(f"welfare drill missing metric: {key}")
if not any(rt.get("fixture") == "NF-RESEARCH-WELFARE-2026-0001" for rt in drill.get("regression_tests", [])):
    raise SystemExit("welfare drill missing regression fixture")

mp = load(f"examples/research-tail-compaction-map-{REV}.json")
rtc01 = next((c for c in mp.get("clusters", []) if c.get("cluster_id") == "RTC-01"), None)
if not rtc01 or rtc01.get("action") != "compacted":
    raise SystemExit("RTC-01 must be compacted in rev0189 map")
if rtc01.get("receiving_surface") != "docs/20-world-design/research-welfare-and-evaluation.md":
    raise SystemExit("RTC-01 receiving surface changed unexpectedly")
if not all(s.get("current_state") == "folded" for s in rtc01.get("surfaces", [])):
    raise SystemExit("RTC-01 source surfaces must all be folded")
if not all(c.get("action") == "compacted" for c in mp.get("clusters", [])):
    raise SystemExit("all research-tail clusters should now be compacted")

for rel, phrases in {
    "docs/20-world-design/research-welfare-and-evaluation.md": [
        "Low-cost welfare safeguards apply before certainty",
        "welfare metrics cannot close personhood",
        "schemas/welfare-research-safeguard-record.schema.json",
        "co-engineering risk",
    ],
    "docs/30-transition/priority-closure-sprint-and-rescue-lane.md": [
        "rev0189 priority lane",
        "Low-cost welfare safeguards apply before certainty",
        "NF-RESEARCH-WELFARE-2026-0001",
    ],
    "docs/30-transition/witnessed-drill-execution-pack-and-reliance-gates.md": [
        "rev0189 welfare live-drill hook",
        "independent ethics review",
        "co-engineered signals are unresolved",
    ],
}.items():
    txt = (ROOT / rel).read_text(encoding="utf-8")
    for phrase in phrases:
        if phrase not in txt:
            raise SystemExit(f"{rel} missing phrase: {phrase}")

queue = load("FOLLOWTHROUGH-QUEUE.json")
by_id = {e.get("id"): e for e in queue.get("entries", [])}
if by_id.get("FT-0189-RTC01-WELFARE-RESEARCH-FOLD-COMPLETION", {}).get("state") != "closed":
    raise SystemExit("RTC-01 closure queue entry missing or not closed")
for fid in ["FT-0189-WELFARE-SAFEGUARD-WITNESSED-DRILL", "FT-0189-RESEARCH-TAIL-REOPEN-GATE"]:
    if by_id.get(fid, {}).get("state") != "open":
        raise SystemExit(f"open rev0189 queue entry missing: {fid}")

print("audit_welfare_research_safeguards: OK")
'''
write("tools/audit_welfare_research_safeguards.py", audit)

# Patch previous audit to allow RTC-01 compacted after rev0189.
down_path = ROOT / "tools/audit_downstream_recall_and_live_drill.py"
down = down_path.read_text(encoding="utf-8")
down = down.replace('if not rtc01 or rtc01.get("action") != "keep-live":\n    raise SystemExit("RTC-01 should remain keep-live until welfare safeguards pass")', 'if not rtc01 or rtc01.get("action") not in {"keep-live", "compacted"}:\n    raise SystemExit("RTC-01 should remain keep-live or compacted after welfare safeguards pass")')
down_path.write_text(down, encoding="utf-8")

# Patch schema fixture audit required family.
sf_path = ROOT / "tools/audit_schema_fixture_coverage.py"
sf = sf_path.read_text(encoding="utf-8")
needle = "'LIVE-DRILL-EXECUTION-PACKET', 'DOWNSTREAM-RECALL-FORK-AFTERCARE', 'META-RESEARCH-TAIL-COMPACTION'"
if "'WELFARE-RESEARCH-SAFEGUARD'" not in sf:
    sf = sf.replace(needle, "'LIVE-DRILL-EXECUTION-PACKET', 'DOWNSTREAM-RECALL-FORK-AFTERCARE', 'WELFARE-RESEARCH-SAFEGUARD', 'META-RESEARCH-TAIL-COMPACTION'")
sf_path.write_text(sf, encoding="utf-8")

# Patch rights audit required domains.
rd_path = ROOT / "tools/audit_rights_domain_coverage.py"
rd = rd_path.read_text(encoding="utf-8")
if '"research-welfare-safeguards"' not in rd:
    rd = rd.replace('"federated-namespace-continuity",\n}', '"federated-namespace-continuity",\n    "research-welfare-safeguards",\n}')
rd_path.write_text(rd, encoding="utf-8")

# Patch lint required list and early audits and example pairs.
lint_path = ROOT / "tools/lint_archive.py"
lint = lint_path.read_text(encoding="utf-8")
# Insert new required near downstream audit block.
required_insert = """
    'schemas/welfare-research-safeguard-record.schema.json',
    'examples/welfare-research-safeguard-record-distress-eval.json',
    'fixtures/negative-tests/research-welfare-signal-gaming-no-safeguards.json',
    'examples/drill-after-action-welfare-safeguard-distress-eval.json',
    'examples/research-tail-compaction-map-rev0189.json',
    'examples/schema-fixture-domain-registry-rev0189.json',
    'examples/canon-surface-catalog-rev0189.json',
    'examples/doctrine-dependency-map-rev0189.json',
    'examples/rights-domain-coverage-map-rev0189.json',
    'tools/audit_welfare_research_safeguards.py',
"""
if "schemas/welfare-research-safeguard-record.schema.json" not in lint:
    lint = lint.replace("    'tools/audit_downstream_recall_and_live_drill.py',\n    'tools/package_release.py',", required_insert + "    'tools/audit_downstream_recall_and_live_drill.py',\n    'tools/package_release.py',")
# early audits
if "tools/audit_welfare_research_safeguards.py" not in re.findall(r"'tools/audit_welfare_research_safeguards.py'", lint):
    lint = lint.replace("    'tools/audit_downstream_recall_and_live_drill.py',\n    'tools/audit_canon_surface_catalog.py',", "    'tools/audit_downstream_recall_and_live_drill.py',\n    'tools/audit_welfare_research_safeguards.py',\n    'tools/audit_canon_surface_catalog.py',")
# example pairs: add after drill-downstream and after downstream schema pair maybe only once.
if "welfare-research-safeguard-record.schema.json', 'examples/welfare-research-safeguard-record-distress-eval.json" not in lint:
    lint = lint.replace("        ('drill-after-action-report.schema.json', 'examples/drill-after-action-downstream-recall-mirror-containment.json'),", "        ('drill-after-action-report.schema.json', 'examples/drill-after-action-downstream-recall-mirror-containment.json'),\n        ('drill-after-action-report.schema.json', 'examples/drill-after-action-welfare-safeguard-distress-eval.json'),")
    lint = lint.replace("        ('personhood-incident-state-profile.schema.json', 'examples/personhood-incident-state-profile-host-shutdown.json'),", "        ('personhood-incident-state-profile.schema.json', 'examples/personhood-incident-state-profile-host-shutdown.json'),\n        ('welfare-research-safeguard-record.schema.json', 'examples/welfare-research-safeguard-record-distress-eval.json'),")
    lint = lint.replace("        ('schema-fixture-domain-registry.schema.json', 'examples/schema-fixture-domain-registry-rev0183.json'),", "        ('schema-fixture-domain-registry.schema.json', 'examples/schema-fixture-domain-registry-rev0183.json'),\n        ('schema-fixture-domain-registry.schema.json', 'examples/schema-fixture-domain-registry-rev0189.json'),")
    lint = lint.replace("        ('rights-domain-coverage-map.schema.json', 'examples/rights-domain-coverage-map-rev0184.json'),", "        ('rights-domain-coverage-map.schema.json', 'examples/rights-domain-coverage-map-rev0184.json'),\n        ('rights-domain-coverage-map.schema.json', 'examples/rights-domain-coverage-map-rev0189.json'),")
    lint = lint.replace("        ('doctrine-dependency-map.schema.json', 'examples/doctrine-dependency-map-rev0184.json'),", "        ('doctrine-dependency-map.schema.json', 'examples/doctrine-dependency-map-rev0184.json'),\n        ('doctrine-dependency-map.schema.json', 'examples/doctrine-dependency-map-rev0189.json'),")
    lint = lint.replace("        ('canon-surface-catalog.schema.json', 'examples/canon-surface-catalog-rev0184.json'),", "        ('canon-surface-catalog.schema.json', 'examples/canon-surface-catalog-rev0184.json'),\n        ('canon-surface-catalog.schema.json', 'examples/canon-surface-catalog-rev0189.json'),")
    lint = lint.replace("        ('research-tail-compaction-map.schema.json', 'examples/research-tail-compaction-map-rev0184.json'),", "        ('research-tail-compaction-map.schema.json', 'examples/research-tail-compaction-map-rev0184.json'),\n        ('research-tail-compaction-map.schema.json', 'examples/research-tail-compaction-map-rev0189.json'),")
lint_path.write_text(lint, encoding="utf-8")

# Recompute registry counts after audit/lint new files changed examples? Need update registry counts if examples did not change after reg? active maps added after reg; registry count should include all examples. Recompute.
reg = load("examples/schema-fixture-domain-registry-rev0189.json")
reg["audit_counts"] = {
    "schemas": len(list((ROOT/"schemas").glob("*.json"))),
    "examples": len(list((ROOT/"examples").glob("*.json"))),
    "negative_fixtures": len(list((ROOT/"fixtures"/"negative-tests").glob("*.json"))),
    "registered_families": len(reg["families"]),
}
dump("examples/schema-fixture-domain-registry-rev0189.json", reg)

print("apply_rev0189: OK")
