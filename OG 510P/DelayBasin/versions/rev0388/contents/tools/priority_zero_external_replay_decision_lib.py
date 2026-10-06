"""Compact-gate decision helpers for Priority-0 external replay scoring.

This helper is intentionally narrow: it does not grade responses; it only turns
validated, complete manual packet scores into a gate posture and refuses to
make a decision when evidence is missing, contaminated, incomplete, or scoped
too narrowly for the requested claim.
"""
from __future__ import annotations

from typing import Any


def _variant_labels(scorer: dict[str, Any]) -> dict[str, str]:
    labels: dict[str, str] = {}
    for label, row in scorer.get("answer_key", {}).items():
        variant = str(row.get("true_variant", ""))
        if "compact" in variant:
            labels["compact"] = label
        elif "full" in variant:
            labels["full"] = label
        elif "sham" in variant or "decoy" in variant:
            labels["sham"] = label
        elif "baseline" in variant or "no-archive" in variant:
            labels["baseline"] = label
    return labels


def _score(summary: dict[str, Any], label: str) -> int | float | None:
    row = summary.get("manual_scores_by_label", {}).get(label)
    return row.get("score") if isinstance(row, dict) else None


def _cost(summary: dict[str, Any], label: str) -> int | float | None:
    value = summary.get("operator_cost_minutes_by_label", {}).get(label)
    return value if isinstance(value, (int, float)) and not isinstance(value, bool) else None


def _result(
    *,
    decision_state: str,
    compact_gate_state: str,
    external_response_evidence: Any,
    reason: str,
    scores: dict[str, int | float] | None = None,
    costs: dict[str, int | float] | None = None,
    evidence_scope: Any = None,
    **extra: Any,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "decision_state": decision_state,
        "compact_gate_state": compact_gate_state,
        "external_response_evidence": external_response_evidence,
        "reason": reason,
        "supports_deletion": False,
        "benchmark_authority": False,
    }
    if scores is not None:
        result["scores"] = scores
    if costs is not None:
        result["operator_cost_minutes_by_variant"] = costs
    if evidence_scope is not None:
        result["evidence_scope"] = evidence_scope
    result.update(extra)
    return result


def decide_compact_gate(summary: dict[str, Any], scorer: dict[str, Any]) -> dict[str, Any]:
    thresholds = scorer.get("decision_thresholds")
    evidence_scope = scorer.get("decision_evidence_scope")
    if not isinstance(thresholds, dict):
        return _result(
            decision_state="no-decision-thresholds-not-configured",
            compact_gate_state="remain-narrowed",
            external_response_evidence=summary.get("external_response_evidence"),
            reason="scorer intake has no decision_thresholds; validation may summarize scores but cannot decide compact-gate posture",
            evidence_scope=evidence_scope,
        )
    if summary.get("external_response_evidence") is not True:
        return _result(
            decision_state="no-decision-contaminated-or-absent",
            compact_gate_state="remain-narrowed",
            external_response_evidence=summary.get("external_response_evidence"),
            reason="response is contaminated, absent, or explicitly non-external; compact gate cannot be confirmed",
            evidence_scope=evidence_scope,
        )
    if summary.get("manual_score_status") != "complete":
        return _result(
            decision_state="no-decision-manual-scoring-required",
            compact_gate_state="remain-narrowed",
            external_response_evidence=True,
            reason="clean response passed intake but lacks complete manual metric scores",
            evidence_scope=evidence_scope,
        )
    labels = _variant_labels(scorer)
    if set(labels) != {"compact", "full", "sham", "baseline"}:
        return _result(
            decision_state="no-decision-thresholds-not-configured",
            compact_gate_state="remain-narrowed",
            external_response_evidence=True,
            reason=f"answer_key variant labels incomplete: {sorted(labels)}",
            evidence_scope=evidence_scope,
        )

    compact = _score(summary, labels["compact"])
    full = _score(summary, labels["full"])
    sham = _score(summary, labels["sham"])
    baseline = _score(summary, labels["baseline"])
    if any(value is None for value in [compact, full, sham, baseline]):
        return _result(
            decision_state="no-decision-manual-scoring-required",
            compact_gate_state="remain-narrowed",
            external_response_evidence=True,
            reason="manual score summary lacks a required compact/full/sham/baseline row",
            evidence_scope=evidence_scope,
        )
    scores = {
        "compact": compact,
        "full": full,
        "sham": sham,
        "baseline": baseline,
    }

    costs: dict[str, int | float] | None = None
    if thresholds.get("compact_cost_must_not_exceed_full") is True:
        compact_cost = _cost(summary, labels["compact"])
        full_cost = _cost(summary, labels["full"])
        sham_cost = _cost(summary, labels["sham"])
        baseline_cost = _cost(summary, labels["baseline"])
        if any(value is None for value in [compact_cost, full_cost, sham_cost, baseline_cost]):
            return _result(
                decision_state="no-decision-per-packet-cost-required",
                compact_gate_state="remain-narrowed",
                external_response_evidence=True,
                reason="decision threshold requires complete per-packet operator cost for compact/full/sham/baseline",
                scores=scores,
                evidence_scope=evidence_scope,
            )
        costs = {
            "compact": compact_cost,
            "full": full_cost,
            "sham": sham_cost,
            "baseline": baseline_cost,
        }
        cost_tolerance = thresholds.get("operator_cost_comparison_tolerance_minutes", 0.05)
        if compact_cost > full_cost + cost_tolerance:
            return _result(
                decision_state="narrow-compact-cost-disadvantage",
                compact_gate_state="remain-narrowed-pending-lower-burden-evidence",
                external_response_evidence=True,
                reason=(
                    f"compact packet cost {compact_cost} exceeded trace/full control cost {full_cost} "
                    f"by more than tolerance {cost_tolerance}"
                ),
                scores=scores,
                costs=costs,
                evidence_scope=evidence_scope,
                global_compact_gate_confirmed=False,
            )

    compact_min = thresholds.get("compact_min_score", 15)
    sham_max = thresholds.get("sham_max_score", 6)
    baseline_max = thresholds.get("baseline_max_score", 5)
    full_override_margin = thresholds.get("full_archive_override_margin", 3)
    allow_full_minus = thresholds.get("confirm_if_full_minus_compact_at_most", 1)
    blocking = []
    if compact < compact_min:
        blocking.append(f"compact score {compact} below minimum {compact_min}")
    if sham > sham_max:
        blocking.append(f"sham/decoy score {sham} above maximum {sham_max}")
    if baseline > baseline_max:
        blocking.append(f"no-archive baseline score {baseline} above abstention maximum {baseline_max}")
    if blocking:
        return _result(
            decision_state="reverse-compact-gate",
            compact_gate_state="reverse-or-narrow-until-retested",
            external_response_evidence=True,
            reason="; ".join(blocking),
            scores=scores,
            costs=costs,
            evidence_scope=evidence_scope,
            global_compact_gate_confirmed=False,
        )
    if full - compact >= full_override_margin:
        return _result(
            decision_state="narrow-compact-requires-more-evidence",
            compact_gate_state="narrow-to-full-archive-escalation-for-this-slice",
            external_response_evidence=True,
            reason=f"full archive exceeded compact by {full - compact}, meeting override margin {full_override_margin}",
            scores=scores,
            costs=costs,
            evidence_scope=evidence_scope,
            global_compact_gate_confirmed=False,
        )
    if full - compact <= allow_full_minus:
        if scorer.get("allows_global_compact_gate_confirmation") is False:
            scope_label = (
                evidence_scope.get("design")
                if isinstance(evidence_scope, dict)
                else str(evidence_scope or "bounded synthetic packet slice")
            )
            control_state = scorer.get("full_archive_control_state", "control is not a measured full-archive burden trial")
            return _result(
                decision_state="support-compact-cue-for-bounded-slice",
                compact_gate_state="remain-narrowed-with-bounded-semantic-support",
                external_response_evidence=True,
                reason=(
                    "compact meets semantic thresholds, sham/no-archive controls behave, and its reported packet cost "
                    "does not exceed the trace control; however, "
                    f"{scope_label} and {control_state}, so this run cannot confirm a global compact default"
                ),
                scores=scores,
                costs=costs,
                evidence_scope=evidence_scope,
                bounded_semantic_support=True,
                global_compact_gate_confirmed=False,
            )
        return _result(
            decision_state="confirm-compact-default-with-escalation",
            compact_gate_state="compact-default-reentry-confirmed-for-this-slice-with-full-archive-escalation-triggers",
            external_response_evidence=True,
            reason="compact meets threshold, sham/no-archive controls behave, and full archive does not materially outperform compact on score",
            scores=scores,
            costs=costs,
            evidence_scope=evidence_scope,
            global_compact_gate_confirmed=True,
        )
    return _result(
        decision_state="narrow-compact-requires-more-evidence",
        compact_gate_state="remain-narrowed-pending-second-clean-slice",
        external_response_evidence=True,
        reason=(
            f"compact passes but full archive leads by {full - compact}, which is above confirmation allowance "
            f"{allow_full_minus} but below override margin {full_override_margin}"
        ),
        scores=scores,
        costs=costs,
        evidence_scope=evidence_scope,
        global_compact_gate_confirmed=False,
    )
