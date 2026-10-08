from __future__ import annotations

from dataclasses import asdict, dataclass
from math import comb
from typing import Any, Mapping, Sequence

from .counter_response import GUARDED_COUNTER_AXIS
from .population_counterprobe import REPAIR_COUNTER_AXIS
from .terminal_mechanisms import to_float, to_int


@dataclass(frozen=True)
class PairIntegritySummary:
    rows: int
    pair_keys: int
    complete_pairs: int
    incomplete_pairs: int
    duplicate_policy_pairs: int
    seed_mismatches: int
    context_mismatches: int
    broad_pool_eligible_rows: int
    candidate_pool_eligible_rows: int
    passed: bool

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PairedSignSummary:
    label: str
    rows: int
    pairs: int
    candidate_better_pairs: int
    guard_better_pairs: int
    same_score_pairs: int
    non_tie_pairs: int
    candidate_mean_delta: float
    tie_share: float
    one_sided_p_candidate_worse: float
    one_sided_p_candidate_better: float
    alpha: float
    family_tests: int
    adjusted_alpha: float
    point_negative_transfer: bool
    negative_transfer_familywise_supported: bool
    candidate_dominance_familywise_supported: bool
    status: str

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class TieMechanismSummary:
    label: str
    pairs: int
    same_score_pairs: int
    same_score_same_mechanism_pairs: int
    same_score_mechanism_flip_pairs: int
    same_score_loss_reason_flip_pairs: int
    tie_share: float
    mechanism_flip_share_of_ties: float
    life_to_library_flips: int
    library_to_life_flips: int
    tie_equivalence_warning: bool

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class MechanismDriftSummary:
    label: str
    rows: int
    pairs: int
    same_score_pairs: int
    score_and_mechanism_equivalent_pairs: int
    same_score_mechanism_flip_pairs: int
    life_to_library_flips: int
    library_to_life_flips: int
    other_mechanism_flips: int
    directional_flip_pairs: int
    one_sided_p_candidate_library_shift: float
    one_sided_p_candidate_life_shift: float
    alpha: float
    family_tests: int
    adjusted_alpha: float
    candidate_library_shift_familywise_supported: bool
    candidate_life_shift_familywise_supported: bool
    mechanism_equivalence_share: float
    same_score_flip_share: float
    status: str

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def _complete_pair(row: Mapping[str, object]) -> bool:
    value = row.get("complete_pair")
    return value is True or str(value).strip().lower() == "true"


def binomial_tail_at_least(successes: int, trials: int) -> float:
    """Exact upper tail P[X >= successes] for X~Binomial(trials, 0.5)."""

    successes_i = int(successes)
    trials_i = int(trials)
    if trials_i < 0:
        raise ValueError("trials must be non-negative")
    if successes_i <= 0:
        return 1.0
    if successes_i > trials_i:
        return 0.0
    return sum(comb(trials_i, k) for k in range(successes_i, trials_i + 1)) / float(2**trials_i)


def paired_sign_summary(
    rows: Sequence[Mapping[str, object]],
    *,
    label: str,
    alpha: float = 0.05,
    family_tests: int = 1,
) -> PairedSignSummary:
    complete = [row for row in rows if _complete_pair(row)]
    pairs = len(complete)
    candidate_better = sum(1 for row in complete if row.get("comparison") == "candidate_better")
    guard_better = sum(1 for row in complete if row.get("comparison") == "guard_better")
    same = sum(1 for row in complete if row.get("comparison") == "same_score")
    non_tie = candidate_better + guard_better
    deltas = [to_float(row.get("candidate_minus_baseline_score"), 0.0) for row in complete]
    mean_delta = sum(deltas) / pairs if pairs else 0.0
    tie_share = same / pairs if pairs else 0.0
    p_worse = binomial_tail_at_least(guard_better, non_tie) if non_tie else 1.0
    p_better = binomial_tail_at_least(candidate_better, non_tie) if non_tie else 1.0
    adjusted = alpha / max(1, int(family_tests))
    point_negative = guard_better > candidate_better or mean_delta < 0.0
    negative_supported = guard_better > candidate_better and mean_delta < 0.0 and p_worse <= adjusted
    dominance_supported = candidate_better > guard_better and mean_delta > 0.0 and p_better <= adjusted
    if negative_supported:
        status = "candidate_quarantined_exact_sign_negative_transfer"
    elif dominance_supported:
        status = "candidate_transfer_dominates_exact_sign"
    elif point_negative:
        status = "candidate_quarantined_point_negative_not_familywise_significant"
    elif candidate_better == 0 and guard_better == 0:
        status = "candidate_indistinguishable_all_ties"
    else:
        status = "candidate_mixed_or_underpowered_exact_sign"
    return PairedSignSummary(
        label=label,
        rows=len(rows),
        pairs=pairs,
        candidate_better_pairs=candidate_better,
        guard_better_pairs=guard_better,
        same_score_pairs=same,
        non_tie_pairs=non_tie,
        candidate_mean_delta=mean_delta,
        tie_share=tie_share,
        one_sided_p_candidate_worse=p_worse,
        one_sided_p_candidate_better=p_better,
        alpha=alpha,
        family_tests=int(family_tests),
        adjusted_alpha=adjusted,
        point_negative_transfer=point_negative,
        negative_transfer_familywise_supported=negative_supported,
        candidate_dominance_familywise_supported=dominance_supported,
        status=status,
    )


def grouped_sign_summary_rows(
    rows: Sequence[Mapping[str, object]],
    *,
    group_axes: Sequence[str],
    alpha: float = 0.05,
    family_tests: int = 1,
) -> list[dict[str, Any]]:
    groups: dict[tuple[str, ...], list[Mapping[str, object]]] = {}
    for row in rows:
        if not _complete_pair(row):
            continue
        key = tuple(str(row.get(axis, "")) for axis in group_axes)
        groups.setdefault(key, []).append(row)
    out: list[dict[str, Any]] = []
    for key, group in sorted(groups.items()):
        label = "|".join(f"{axis}={value}" for axis, value in zip(group_axes, key))
        payload = paired_sign_summary(group, label=label, alpha=alpha, family_tests=family_tests).as_dict()
        for axis, value in zip(group_axes, key):
            payload[axis] = value
        payload["group_axes"] = "+".join(group_axes)
        out.append(payload)
    return out


def tie_mechanism_summary(rows: Sequence[Mapping[str, object]], *, label: str) -> TieMechanismSummary:
    complete = [row for row in rows if _complete_pair(row)]
    same_rows = [row for row in complete if row.get("comparison") == "same_score"]
    same_mechanism = 0
    mechanism_flip = 0
    loss_flip = 0
    life_to_library = 0
    library_to_life = 0
    for row in same_rows:
        baseline_mech = str(row.get("baseline_mechanism", ""))
        candidate_mech = str(row.get("candidate_mechanism", ""))
        if baseline_mech == candidate_mech:
            same_mechanism += 1
        else:
            mechanism_flip += 1
            if baseline_mech == "life_total" and candidate_mech == "library_out":
                life_to_library += 1
            if baseline_mech == "library_out" and candidate_mech == "life_total":
                library_to_life += 1
        if str(row.get("baseline_loss_reason", "")) != str(row.get("candidate_loss_reason", "")):
            loss_flip += 1
    pairs = len(complete)
    return TieMechanismSummary(
        label=label,
        pairs=pairs,
        same_score_pairs=len(same_rows),
        same_score_same_mechanism_pairs=same_mechanism,
        same_score_mechanism_flip_pairs=mechanism_flip,
        same_score_loss_reason_flip_pairs=loss_flip,
        tie_share=len(same_rows) / pairs if pairs else 0.0,
        mechanism_flip_share_of_ties=mechanism_flip / len(same_rows) if same_rows else 0.0,
        life_to_library_flips=life_to_library,
        library_to_life_flips=library_to_life,
        tie_equivalence_warning=mechanism_flip > 0,
    )


def mechanism_flip_direction(row: Mapping[str, object]) -> str:
    baseline = str(row.get("baseline_mechanism", ""))
    candidate = str(row.get("candidate_mechanism", ""))
    if baseline == candidate:
        return "same_mechanism"
    if baseline == "life_total" and candidate == "library_out":
        return "life_to_library"
    if baseline == "library_out" and candidate == "life_total":
        return "library_to_life"
    return f"{baseline}_to_{candidate}" if baseline or candidate else "unknown_flip"


def same_score_mechanism_flip_rows(rows: Sequence[Mapping[str, object]]) -> list[dict[str, Any]]:
    """Return row-level same-score pairs whose terminal mechanism differs.

    A score tie is not necessarily behavioral equivalence.  This compact row set
    lets audits distinguish true score+mechanism equivalence from ties that land
    on a different terminal cause, without shipping any raw transition logs.
    """

    out: list[dict[str, Any]] = []
    for row in rows:
        if not _complete_pair(row) or row.get("comparison") != "same_score":
            continue
        baseline = str(row.get("baseline_mechanism", ""))
        candidate = str(row.get("candidate_mechanism", ""))
        if baseline == candidate:
            continue
        payload = {
            "pair_key": row.get("pair_key", ""),
            "sampling_design": row.get("sampling_design", ""),
            "size_axis": row.get("size_axis", ""),
            "starting_life": to_int(row.get("starting_life"), -1),
            "threat_policy_axis": row.get("threat_policy_axis", ""),
            "target_seat": to_int(row.get("target_seat"), -1),
            "starting_player": to_int(row.get("starting_player"), -1),
            "rep": to_int(row.get("rep"), -1),
            "paired_seed": to_int(row.get("paired_seed"), -1),
            "baseline_score": to_float(row.get("baseline_score"), 0.5),
            "candidate_score": to_float(row.get("candidate_score"), 0.5),
            "baseline_mechanism": baseline,
            "candidate_mechanism": candidate,
            "mechanism_direction": mechanism_flip_direction(row),
            "baseline_loss_reason": row.get("baseline_loss_reason", ""),
            "candidate_loss_reason": row.get("candidate_loss_reason", ""),
        }
        out.append(payload)
    return out


def mechanism_drift_summary(
    rows: Sequence[Mapping[str, object]],
    *,
    label: str,
    alpha: float = 0.05,
    family_tests: int = 1,
) -> MechanismDriftSummary:
    complete = [row for row in rows if _complete_pair(row)]
    same_rows = [row for row in complete if row.get("comparison") == "same_score"]
    same_mechanism = 0
    life_to_library = 0
    library_to_life = 0
    other = 0
    for row in same_rows:
        direction = mechanism_flip_direction(row)
        if direction == "same_mechanism":
            same_mechanism += 1
        elif direction == "life_to_library":
            life_to_library += 1
        elif direction == "library_to_life":
            library_to_life += 1
        else:
            other += 1
    flips = life_to_library + library_to_life + other
    directional = life_to_library + library_to_life
    p_library = binomial_tail_at_least(life_to_library, directional) if directional else 1.0
    p_life = binomial_tail_at_least(library_to_life, directional) if directional else 1.0
    adjusted = alpha / max(1, int(family_tests))
    library_supported = life_to_library > library_to_life and p_library <= adjusted
    life_supported = library_to_life > life_to_library and p_life <= adjusted
    if library_supported:
        status = "candidate_same_score_shift_toward_library_out_supported"
    elif life_supported:
        status = "candidate_same_score_shift_toward_life_total_supported"
    elif flips:
        status = "same_score_mechanism_drift_detected_not_familywise_directional"
    else:
        status = "score_ties_are_mechanism_equivalent"
    pairs = len(complete)
    return MechanismDriftSummary(
        label=label,
        rows=len(rows),
        pairs=pairs,
        same_score_pairs=len(same_rows),
        score_and_mechanism_equivalent_pairs=same_mechanism,
        same_score_mechanism_flip_pairs=flips,
        life_to_library_flips=life_to_library,
        library_to_life_flips=library_to_life,
        other_mechanism_flips=other,
        directional_flip_pairs=directional,
        one_sided_p_candidate_library_shift=p_library,
        one_sided_p_candidate_life_shift=p_life,
        alpha=alpha,
        family_tests=int(family_tests),
        adjusted_alpha=adjusted,
        candidate_library_shift_familywise_supported=library_supported,
        candidate_life_shift_familywise_supported=life_supported,
        mechanism_equivalence_share=same_mechanism / pairs if pairs else 0.0,
        same_score_flip_share=flips / len(same_rows) if same_rows else 0.0,
        status=status,
    )


def grouped_mechanism_drift_rows(
    rows: Sequence[Mapping[str, object]],
    *,
    group_axes: Sequence[str],
    alpha: float = 0.05,
    family_tests: int = 1,
) -> list[dict[str, Any]]:
    groups: dict[tuple[str, ...], list[Mapping[str, object]]] = {}
    for row in rows:
        if not _complete_pair(row):
            continue
        key = tuple(str(row.get(axis, "")) for axis in group_axes)
        groups.setdefault(key, []).append(row)
    out: list[dict[str, Any]] = []
    for key, group in sorted(groups.items()):
        label = "|".join(f"{axis}={value}" for axis, value in zip(group_axes, key))
        payload = mechanism_drift_summary(group, label=label, alpha=alpha, family_tests=family_tests).as_dict()
        for axis, value in zip(group_axes, key):
            payload[axis] = value
        payload["group_axes"] = "+".join(group_axes)
        out.append(payload)
    return out


def grouped_tie_mechanism_rows(rows: Sequence[Mapping[str, object]], *, group_axes: Sequence[str]) -> list[dict[str, Any]]:
    groups: dict[tuple[str, ...], list[Mapping[str, object]]] = {}
    for row in rows:
        if not _complete_pair(row):
            continue
        key = tuple(str(row.get(axis, "")) for axis in group_axes)
        groups.setdefault(key, []).append(row)
    out: list[dict[str, Any]] = []
    for key, group in sorted(groups.items()):
        label = "|".join(f"{axis}={value}" for axis, value in zip(group_axes, key))
        payload = tie_mechanism_summary(group, label=label).as_dict()
        for axis, value in zip(group_axes, key):
            payload[axis] = value
        payload["group_axes"] = "+".join(group_axes)
        out.append(payload)
    return out


def pair_integrity_rows(
    game_rows: Sequence[Mapping[str, object]],
    *,
    baseline_axis: str = GUARDED_COUNTER_AXIS,
    candidate_axis: str = REPAIR_COUNTER_AXIS,
) -> list[dict[str, Any]]:
    by_pair: dict[str, list[Mapping[str, object]]] = {}
    for row in game_rows:
        pair_key = str(row.get("pair_key", ""))
        if pair_key:
            by_pair.setdefault(pair_key, []).append(row)
    out: list[dict[str, Any]] = []
    seed_fields = ("seed", "transition_seed", "agent_seed", "paired_seed")
    context_fields = ("sampling_design", "size_axis", "starting_life", "target_seat", "starting_player", "rep", "threat_policy_axis")
    for pair_key, rows in sorted(by_pair.items()):
        axes = [str(row.get("counter_policy_axis", "")) for row in rows]
        unique_axes = sorted(set(axes))
        duplicate_policy = len(axes) != len(unique_axes)
        complete = len(rows) == 2 and set(unique_axes) == {baseline_axis, candidate_axis}
        seed_mismatch_fields: list[str] = []
        context_mismatch_fields: list[str] = []
        if rows:
            for field in seed_fields:
                if len({str(row.get(field, "")) for row in rows}) > 1:
                    seed_mismatch_fields.append(field)
            for field in context_fields:
                if len({str(row.get(field, "")) for row in rows}) > 1:
                    context_mismatch_fields.append(field)
        broad_pool_rows = sum(str(row.get("broad_pool_eligible", "")).strip().lower() == "true" or row.get("broad_pool_eligible") is True for row in rows)
        candidate_pool_rows = sum(str(row.get("candidate_pool_eligible", "")).strip().lower() == "true" or row.get("candidate_pool_eligible") is True for row in rows)
        out.append(
            {
                "pair_key": pair_key,
                "rows": len(rows),
                "complete_pair": complete,
                "present_policies": ";".join(unique_axes),
                "duplicate_policy_pair": duplicate_policy,
                "seed_mismatch": bool(seed_mismatch_fields),
                "seed_mismatch_fields": ";".join(seed_mismatch_fields),
                "context_mismatch": bool(context_mismatch_fields),
                "context_mismatch_fields": ";".join(context_mismatch_fields),
                "broad_pool_eligible_rows": broad_pool_rows,
                "candidate_pool_eligible_rows": candidate_pool_rows,
                "starting_life": to_int(rows[0].get("starting_life"), -1) if rows else -1,
                "sampling_design": rows[0].get("sampling_design", "") if rows else "",
                "size_axis": rows[0].get("size_axis", "") if rows else "",
                "threat_policy_axis": rows[0].get("threat_policy_axis", "") if rows else "",
            }
        )
    return out


def summarize_pair_integrity(rows: Sequence[Mapping[str, object]]) -> PairIntegritySummary:
    pairs = list(rows)
    complete = sum(1 for row in pairs if row.get("complete_pair") is True or str(row.get("complete_pair", "")).lower() == "true")
    incomplete = len(pairs) - complete
    duplicate = sum(1 for row in pairs if row.get("duplicate_policy_pair") is True or str(row.get("duplicate_policy_pair", "")).lower() == "true")
    seed_mismatch = sum(1 for row in pairs if row.get("seed_mismatch") is True or str(row.get("seed_mismatch", "")).lower() == "true")
    context_mismatch = sum(1 for row in pairs if row.get("context_mismatch") is True or str(row.get("context_mismatch", "")).lower() == "true")
    broad_pool = sum(to_int(row.get("broad_pool_eligible_rows"), 0) for row in pairs)
    candidate_pool = sum(to_int(row.get("candidate_pool_eligible_rows"), 0) for row in pairs)
    passed = incomplete == 0 and duplicate == 0 and seed_mismatch == 0 and context_mismatch == 0 and broad_pool == 0 and candidate_pool == 0
    return PairIntegritySummary(
        rows=sum(to_int(row.get("rows"), 0) for row in pairs),
        pair_keys=len(pairs),
        complete_pairs=complete,
        incomplete_pairs=incomplete,
        duplicate_policy_pairs=duplicate,
        seed_mismatches=seed_mismatch,
        context_mismatches=context_mismatch,
        broad_pool_eligible_rows=broad_pool,
        candidate_pool_eligible_rows=candidate_pool,
        passed=passed,
    )


__all__ = [
    "PairIntegritySummary",
    "PairedSignSummary",
    "TieMechanismSummary",
    "MechanismDriftSummary",
    "binomial_tail_at_least",
    "grouped_sign_summary_rows",
    "grouped_mechanism_drift_rows",
    "grouped_tie_mechanism_rows",
    "mechanism_drift_summary",
    "mechanism_flip_direction",
    "paired_sign_summary",
    "pair_integrity_rows",
    "same_score_mechanism_flip_rows",
    "summarize_pair_integrity",
    "tie_mechanism_summary",
]
