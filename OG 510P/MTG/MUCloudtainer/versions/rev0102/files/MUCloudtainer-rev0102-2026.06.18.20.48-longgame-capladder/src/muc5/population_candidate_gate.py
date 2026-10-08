from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Iterable, Mapping, Sequence

from .counter_response import GUARDED_COUNTER_AXIS
from .population_counterprobe import REPAIR_COUNTER_AXIS
from .population_pair_forensics import mechanism_drift_summary, paired_sign_summary
from .terminal_mechanisms import to_int, truthy

PRIMARY_LABELS: tuple[str, ...] = ("overall", "selected_cell_holdout", "transfer_panel")
SELECTED_CELL_DESIGN = "selected_cell_seed_disjoint_holdout"
TRANSFER_DESIGN = "adaptive_candidate_transfer_seedpaired"
KNOWN_SAMPLING_DESIGN_LABELS: dict[str, str] = {
    SELECTED_CELL_DESIGN: "selected_cell_holdout",
    TRANSFER_DESIGN: "transfer_panel",
}
REQUIRED_GAME_CONTRACT_COLUMNS: tuple[str, ...] = (
    "counter_policy_axis",
    "sampling_design",
    "pair_key",
    "broad_pool_eligible",
    "candidate_pool_eligible",
    "adaptive_selection_source",
    "adaptive_selection_reason",
)
REQUIRED_DELTA_CONTRACT_COLUMNS: tuple[str, ...] = (
    "sampling_design",
    "complete_pair",
    "comparison",
    "candidate_minus_baseline_score",
    "baseline_mechanism",
    "candidate_mechanism",
)
_FALSE_LITERALS = frozenset({"false", "0", "no", "n", "off"})


@dataclass(frozen=True)
class CandidateGateSummary:
    baseline_axis: str
    candidate_axis: str
    paired_delta_rows: int
    game_rows: int
    primary_component_rows: int
    leak_audit_rows: int
    score_hard_fail_rows: int
    mechanism_hard_fail_rows: int
    pool_leak_fail_rows: int
    point_negative_rows: int
    same_score_mechanism_flip_rows: int
    hard_fail_reasons: tuple[str, ...]
    score_gate_passed: bool
    mechanism_gate_passed: bool
    pool_leak_gate_passed: bool
    candidate_pool_eligible: bool
    broad_pool_eligible: bool
    status: str

    def as_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["hard_fail_reasons"] = list(self.hard_fail_reasons)
        return payload


@dataclass(frozen=True)
class CandidateEvidenceContractSummary:
    game_rows: int
    paired_delta_rows: int
    contract_rows: int
    hard_fail_rows: int
    sampling_design_groups: int
    family_tests_used: int
    passed: bool
    status: str

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def _blank(value: Any) -> bool:
    return value is None or str(value).strip() == ""


def explicitly_false(value: Any) -> bool:
    if value is False:
        return True
    if value is True:
        return False
    if value is None:
        return False
    return str(value).strip().lower() in _FALSE_LITERALS


def _sampling_design_value(row: Mapping[str, object]) -> str:
    design = str(row.get("sampling_design", "")).strip()
    return design if design else "<missing>"


def _sampling_design_label(design: str) -> str:
    return KNOWN_SAMPLING_DESIGN_LABELS.get(design, f"design:{design}")


def candidate_gate_groups(rows: Sequence[Mapping[str, object]]) -> list[dict[str, Any]]:
    """Return the score/mechanism families used by the adaptive-candidate gate.

    rev0087 used a fixed three-row family: overall, selected-cell holdout, and
    transfer panel.  That was correct for the stabilizer data, but future
    adaptive candidates can introduce new sampling designs.  The gate now
    discovers every non-empty/missing sampling-design slice and expands the
    family size automatically so a new design cannot hide inside the overall
    row with an under-corrected alpha.
    """

    materialized = list(rows)
    groups: list[dict[str, Any]] = [
        {
            "label": "overall",
            "group_kind": "overall",
            "sampling_design": "",
            "rows": materialized,
        }
    ]
    designs = sorted({_sampling_design_value(row) for row in materialized})
    for design in designs:
        groups.append(
            {
                "label": _sampling_design_label(design),
                "group_kind": "sampling_design",
                "sampling_design": design,
                "rows": [row for row in materialized if _sampling_design_value(row) == design],
            }
        )
    return groups


def _primary_groups(rows: Sequence[Mapping[str, object]]) -> dict[str, list[Mapping[str, object]]]:
    # Backward-compatible facade for older tests/callers. New gating code uses
    # candidate_gate_groups so additional sampling designs get their own family
    # rows and alpha correction automatically.
    return {str(group["label"]): list(group["rows"]) for group in candidate_gate_groups(rows)}


def candidate_gate_component_rows(
    paired_delta_rows: Sequence[Mapping[str, object]],
    *,
    alpha: float = 0.05,
    primary_family_tests: int = 3,
) -> list[dict[str, Any]]:
    """Return score/mechanism components that gate adaptive counter candidates.

    This is intentionally stricter than the descriptive rev0085/rev0086 audits:
    it converts paired score transfer and same-score mechanism drift into a
    reusable eligibility firewall.  Adaptive candidates may be useful hypotheses,
    but they must not join broad promotion pools merely because score deltas are
    ambiguous or many pairs tie.

    The family is now design-discovered.  With the current rev0084 panel this is
    still exactly the old 3-family set, but a future holdout/transfer design gets
    a new component row and a tighter Bonferroni denominator instead of silently
    riding inside the overall row.
    """

    groups = candidate_gate_groups(paired_delta_rows)
    family_tests = max(1, int(primary_family_tests), len(groups))
    components: list[dict[str, Any]] = []
    for group in groups:
        label = str(group["label"])
        rows = list(group["rows"])
        common = {
            "group_kind": group["group_kind"],
            "sampling_design": group["sampling_design"],
            "family_tests_used": family_tests,
        }
        sign = paired_sign_summary(rows, label=label, alpha=alpha, family_tests=family_tests).as_dict()
        sign_hard_fail = bool(sign["negative_transfer_familywise_supported"])
        components.append(
            {
                **common,
                "label": label,
                "component": "paired_score_transfer",
                "rows": sign["rows"],
                "pairs": sign["pairs"],
                "candidate_better_pairs": sign["candidate_better_pairs"],
                "guard_better_pairs": sign["guard_better_pairs"],
                "same_score_pairs": sign["same_score_pairs"],
                "candidate_mean_delta": sign["candidate_mean_delta"],
                "one_sided_p_candidate_worse": sign["one_sided_p_candidate_worse"],
                "adjusted_alpha": sign["adjusted_alpha"],
                "point_warning": bool(sign["point_negative_transfer"]),
                "hard_fail": sign_hard_fail,
                "hard_fail_reason": "score_transfer_familywise_negative" if sign_hard_fail else "",
                "status": sign["status"],
            }
        )
        drift = mechanism_drift_summary(rows, label=label, alpha=alpha, family_tests=family_tests).as_dict()
        mechanism_hard_fail = bool(drift["candidate_library_shift_familywise_supported"] or drift["candidate_life_shift_familywise_supported"])
        components.append(
            {
                **common,
                "label": label,
                "component": "same_score_mechanism_drift",
                "rows": drift["rows"],
                "pairs": drift["pairs"],
                "same_score_pairs": drift["same_score_pairs"],
                "score_and_mechanism_equivalent_pairs": drift["score_and_mechanism_equivalent_pairs"],
                "same_score_mechanism_flip_pairs": drift["same_score_mechanism_flip_pairs"],
                "life_to_library_flips": drift["life_to_library_flips"],
                "library_to_life_flips": drift["library_to_life_flips"],
                "one_sided_p_candidate_library_shift": drift["one_sided_p_candidate_library_shift"],
                "one_sided_p_candidate_life_shift": drift["one_sided_p_candidate_life_shift"],
                "adjusted_alpha": drift["adjusted_alpha"],
                "point_warning": bool(drift["same_score_mechanism_flip_pairs"]),
                "hard_fail": mechanism_hard_fail,
                "hard_fail_reason": "score_tie_mechanism_drift_familywise_supported" if mechanism_hard_fail else "",
                "status": drift["status"],
            }
        )
    return components


def candidate_pool_leak_rows(
    game_rows: Sequence[Mapping[str, object]],
    *,
    baseline_axis: str = GUARDED_COUNTER_AXIS,
    candidate_axis: str = REPAIR_COUNTER_AXIS,
) -> list[dict[str, Any]]:
    """Summarize whether adaptive candidate games leaked into promotion pools."""

    groups: dict[tuple[str, str, str], list[Mapping[str, object]]] = {}
    for row in game_rows:
        axis = str(row.get("counter_policy_axis", ""))
        design = str(row.get("sampling_design", ""))
        size = str(row.get("size_axis", ""))
        groups.setdefault((axis, design, size), []).append(row)
    out: list[dict[str, Any]] = []
    for (axis, design, size), rows in sorted(groups.items()):
        broad = sum(1 for row in rows if truthy(row.get("broad_pool_eligible")))
        candidate = sum(1 for row in rows if truthy(row.get("candidate_pool_eligible")))
        missing_pool_flags = sum(1 for row in rows if _blank(row.get("broad_pool_eligible")) or _blank(row.get("candidate_pool_eligible")))
        adaptive_sources = sorted({str(row.get("adaptive_selection_source", "")) for row in rows if row.get("adaptive_selection_source")})
        adaptive_reasons = sorted({str(row.get("adaptive_selection_reason", "")) for row in rows if row.get("adaptive_selection_reason")})
        is_candidate = axis == candidate_axis
        out.append(
            {
                "counter_policy_axis": axis,
                "is_baseline_axis": axis == baseline_axis,
                "is_candidate_axis": is_candidate,
                "sampling_design": design,
                "size_axis": size,
                "rows": len(rows),
                "broad_pool_eligible_rows": broad,
                "candidate_pool_eligible_rows": candidate,
                "missing_pool_flag_rows": missing_pool_flags,
                "adaptive_selection_sources": ";".join(adaptive_sources),
                "adaptive_selection_reasons": ";".join(adaptive_reasons),
                "hard_fail": bool(broad or candidate),
                "hard_fail_reason": "adaptive_candidate_pool_leak" if (broad or candidate) else "",
            }
        )
    return out


def candidate_evidence_contract_rows(
    paired_delta_rows: Sequence[Mapping[str, object]],
    game_rows: Sequence[Mapping[str, object]],
) -> list[dict[str, Any]]:
    """Fail-closed row-contract checks for adaptive candidate evidence.

    Pool leakage is not only a truthy value problem.  A future script could omit
    the eligibility flags, add a new sampling design without a family row, or
    produce paired-delta rows with missing comparison/mechanism fields.  These
    compact contract rows catch that before the candidate firewall can be used as
    a false comfort signal.
    """

    games = list(game_rows)
    deltas = list(paired_delta_rows)
    groups = candidate_gate_groups(deltas)
    family_tests = max(1, len(groups))
    design_values = sorted({_sampling_design_value(row) for row in deltas})
    group_designs = sorted(str(group["sampling_design"]) for group in groups if group.get("group_kind") == "sampling_design")
    missing_gate_designs = sorted(set(design_values) - set(group_designs))

    missing_pool_flag_rows = sum(1 for row in games if _blank(row.get("broad_pool_eligible")) or _blank(row.get("candidate_pool_eligible")))
    non_false_pool_flag_rows = sum(
        1
        for row in games
        if not (explicitly_false(row.get("broad_pool_eligible")) and explicitly_false(row.get("candidate_pool_eligible")))
    )
    missing_game_contract_rows = sum(1 for row in games if any(_blank(row.get(column)) for column in REQUIRED_GAME_CONTRACT_COLUMNS))
    missing_delta_contract_rows = sum(1 for row in deltas if any(_blank(row.get(column)) for column in REQUIRED_DELTA_CONTRACT_COLUMNS))

    rows = [
        {
            "contract": "game_pool_flags_explicit_false",
            "rows": len(games),
            "missing_field_rows": missing_pool_flag_rows,
            "nonconforming_rows": non_false_pool_flag_rows,
            "hard_fail": bool(missing_pool_flag_rows or non_false_pool_flag_rows),
            "status": "pool_flags_explicit_false" if not (missing_pool_flag_rows or non_false_pool_flag_rows) else "pool_flags_missing_or_truthy",
        },
        {
            "contract": "game_adaptive_metadata_present",
            "rows": len(games),
            "missing_field_rows": missing_game_contract_rows,
            "nonconforming_rows": missing_game_contract_rows,
            "hard_fail": bool(missing_game_contract_rows),
            "status": "game_metadata_complete" if not missing_game_contract_rows else "game_metadata_missing",
        },
        {
            "contract": "paired_delta_required_fields_present",
            "rows": len(deltas),
            "missing_field_rows": missing_delta_contract_rows,
            "nonconforming_rows": missing_delta_contract_rows,
            "hard_fail": bool(missing_delta_contract_rows),
            "status": "paired_delta_fields_complete" if not missing_delta_contract_rows else "paired_delta_fields_missing",
        },
        {
            "contract": "sampling_designs_have_family_rows",
            "rows": len(deltas),
            "sampling_designs": ";".join(design_values),
            "family_group_labels": ";".join(str(group["label"]) for group in groups),
            "family_tests_used": family_tests,
            "missing_design_groups": ";".join(missing_gate_designs),
            "missing_field_rows": 0,
            "nonconforming_rows": len(missing_gate_designs),
            "hard_fail": bool(missing_gate_designs),
            "status": "all_sampling_designs_family_corrected" if not missing_gate_designs else "sampling_design_not_family_corrected",
        },
    ]
    return rows


def summarize_candidate_evidence_contract(
    contract_rows: Sequence[Mapping[str, object]],
    *,
    paired_delta_rows: int,
    game_rows: int,
    sampling_design_groups: int,
    family_tests_used: int,
) -> CandidateEvidenceContractSummary:
    hard = sum(1 for row in contract_rows if truthy(row.get("hard_fail")))
    return CandidateEvidenceContractSummary(
        game_rows=int(game_rows),
        paired_delta_rows=int(paired_delta_rows),
        contract_rows=len(contract_rows),
        hard_fail_rows=hard,
        sampling_design_groups=int(sampling_design_groups),
        family_tests_used=int(family_tests_used),
        passed=hard == 0,
        status="candidate_evidence_contract_passed" if hard == 0 else "candidate_evidence_contract_failed",
    )


def summarize_candidate_gate(
    component_rows: Sequence[Mapping[str, object]],
    leak_rows: Sequence[Mapping[str, object]],
    *,
    paired_delta_rows: int,
    game_rows: int,
    baseline_axis: str = GUARDED_COUNTER_AXIS,
    candidate_axis: str = REPAIR_COUNTER_AXIS,
) -> CandidateGateSummary:
    score_hard = sum(1 for row in component_rows if row.get("component") == "paired_score_transfer" and truthy(row.get("hard_fail")))
    mechanism_hard = sum(1 for row in component_rows if row.get("component") == "same_score_mechanism_drift" and truthy(row.get("hard_fail")))
    pool_hard = sum(1 for row in leak_rows if truthy(row.get("hard_fail")))
    point_negative = sum(1 for row in component_rows if row.get("component") == "paired_score_transfer" and truthy(row.get("point_warning")))
    mechanism_flips = sum(to_int(row.get("same_score_mechanism_flip_pairs"), 0) for row in component_rows if row.get("component") == "same_score_mechanism_drift")
    reasons = sorted(
        {
            str(row.get("hard_fail_reason"))
            for row in list(component_rows) + list(leak_rows)
            if str(row.get("hard_fail_reason", ""))
        }
    )
    score_pass = score_hard == 0
    mechanism_pass = mechanism_hard == 0
    pool_pass = pool_hard == 0
    eligible = score_pass and mechanism_pass and pool_pass and point_negative == 0
    if not pool_pass:
        status = "candidate_rejected_pool_leak"
    elif mechanism_hard and score_hard:
        status = "candidate_rejected_score_and_mechanism_firewall"
    elif mechanism_hard:
        status = "candidate_rejected_mechanism_firewall"
    elif score_hard:
        status = "candidate_rejected_score_transfer_firewall"
    elif point_negative:
        status = "candidate_quarantined_point_negative_transfer"
    else:
        status = "candidate_eligible_for_nonadaptive_pool_review"
    return CandidateGateSummary(
        baseline_axis=baseline_axis,
        candidate_axis=candidate_axis,
        paired_delta_rows=int(paired_delta_rows),
        game_rows=int(game_rows),
        primary_component_rows=len(component_rows),
        leak_audit_rows=len(leak_rows),
        score_hard_fail_rows=score_hard,
        mechanism_hard_fail_rows=mechanism_hard,
        pool_leak_fail_rows=pool_hard,
        point_negative_rows=point_negative,
        same_score_mechanism_flip_rows=mechanism_flips,
        hard_fail_reasons=tuple(reasons),
        score_gate_passed=score_pass,
        mechanism_gate_passed=mechanism_pass,
        pool_leak_gate_passed=pool_pass,
        candidate_pool_eligible=eligible,
        broad_pool_eligible=eligible,
        status=status,
    )


def build_candidate_gate(
    paired_delta_rows: Sequence[Mapping[str, object]],
    game_rows: Sequence[Mapping[str, object]],
    *,
    alpha: float = 0.05,
    primary_family_tests: int = 3,
    baseline_axis: str = GUARDED_COUNTER_AXIS,
    candidate_axis: str = REPAIR_COUNTER_AXIS,
) -> tuple[CandidateGateSummary, list[dict[str, Any]], list[dict[str, Any]]]:
    components = candidate_gate_component_rows(
        paired_delta_rows,
        alpha=alpha,
        primary_family_tests=primary_family_tests,
    )
    leaks = candidate_pool_leak_rows(game_rows, baseline_axis=baseline_axis, candidate_axis=candidate_axis)
    summary = summarize_candidate_gate(
        components,
        leaks,
        paired_delta_rows=len(paired_delta_rows),
        game_rows=len(game_rows),
        baseline_axis=baseline_axis,
        candidate_axis=candidate_axis,
    )
    return summary, components, leaks


__all__ = [
    "CandidateEvidenceContractSummary",
    "CandidateGateSummary",
    "KNOWN_SAMPLING_DESIGN_LABELS",
    "PRIMARY_LABELS",
    "candidate_evidence_contract_rows",
    "candidate_gate_component_rows",
    "candidate_gate_groups",
    "candidate_pool_leak_rows",
    "explicitly_false",
    "summarize_candidate_evidence_contract",
    "summarize_candidate_gate",
    "build_candidate_gate",
]
