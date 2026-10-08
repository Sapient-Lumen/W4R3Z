from __future__ import annotations

from dataclasses import asdict, dataclass
from random import Random
from typing import Dict, Mapping, Sequence

from .action_budget import action_diversity_key, select_budgeted_action_indices
from .decision import DecisionFrame
from .ranker_policy import counterfactual_ranker_model_path, load_linear_ranker_model
from .public_agents import PublicProfileAgent


@dataclass(frozen=True)
class HybridActionSelection:
    """Budgeted branch-action subset selected by disagreement, diversity, and priors.

    rev0038 showed that public-policy disagreement is a good way to find frames
    worth branching. rev0039 showed that vote-priority alone can drop useful
    diverse actions under tight budgets.  This selector therefore treats the
    branch budget as an allocation problem with three evidence sources:

    * behavior action: always kept, so labels can compare the policy actually used;
    * disagreement votes: public-safe screeners point at plausible alternatives;
    * diversity/ranker prior: prevent the budget from collapsing to near-duplicate
      choices and include at least one action with high cheap prior score.

    The selector is deliberately not a policy. It is an offline label-budget tool
    for deciding which legal actions should receive expensive branch rollouts.
    """

    indices: tuple[int, ...]
    reasons: Mapping[int, str]
    full_action_count: int
    budget: int
    ranker_revision: str
    ranker_available: bool

    @property
    def is_subset(self) -> bool:
        return len(self.indices) < self.full_action_count

    def as_dict(self) -> dict[str, object]:
        d = asdict(self)
        d["reasons"] = {str(k): v for k, v in self.reasons.items()}
        return d


def _normalize_scores(scores: Mapping[int, float]) -> dict[int, float]:
    if not scores:
        return {}
    vals = [float(v) for v in scores.values()]
    lo, hi = min(vals), max(vals)
    if abs(hi - lo) <= 1e-12:
        return {int(k): 0.0 for k in scores}
    return {int(k): (float(v) - lo) / (hi - lo) for k, v in scores.items()}


def _ranker_prior_scores(frame: DecisionFrame, revision: str) -> tuple[dict[int, float], bool]:
    """Return normalized counterfactual-ranker prior scores if available.

    Missing ranker JSON should not make the selector unusable.  Future archives
    may delete heavyweight data, or a new selector revision may run before a new
    ranker exists.  In that case, the hybrid selector falls back to readable
    public-profile priors plus diversity.
    """

    try:
        path = counterfactual_ranker_model_path(revision)
        if not path.exists():
            return {}, False
        model = load_linear_ranker_model(path)
        raw = {idx: float(model.score_action(frame, action)) for idx, action in enumerate(frame.legal_actions)}
        return _normalize_scores(raw), True
    except Exception:
        return {}, False


def _profile_prior_scores(frame: DecisionFrame, profiles: Sequence[str] = ("threat_rush", "counter_happy", "patient")) -> dict[int, float]:
    """Cheap public-readable prior score averaged over inspectable profiles."""

    if frame.action_count <= 0:
        return {}
    totals = {idx: 0.0 for idx in range(frame.action_count)}
    used = 0
    for profile in profiles:
        try:
            agent = PublicProfileAgent(str(profile))
            for idx, action in enumerate(frame.legal_actions):
                totals[idx] += float(agent.score_action(frame.observation, action))
            used += 1
        except Exception:
            continue
    if used <= 0:
        return {idx: 0.0 for idx in range(frame.action_count)}
    return _normalize_scores({idx: val / float(used) for idx, val in totals.items()})


def _append_reason(reasons: dict[int, str], idx: int, reason: str) -> None:
    old = reasons.get(int(idx), "")
    if not old:
        reasons[int(idx)] = reason
    elif reason not in old.split("+"):
        reasons[int(idx)] = f"{old}+{reason}"


def select_hybrid_action_indices(
    frame: DecisionFrame,
    chosen_idx: int,
    voted_indices: Sequence[int],
    *,
    max_actions_per_frame: int,
    branch_action_budget: int | None,
    rng: Random,
    ranker_revision: str = "rev0034",
) -> tuple[tuple[int, ...], dict[int, str], bool, bool, HybridActionSelection | None]:
    """Select a branch subset with behavior + votes + diversity + cheap priors.

    Returns the same four leading values as older selectors, plus a
    ``HybridActionSelection`` metadata object when a menu was actually selected.
    """

    n = int(frame.action_count)
    if n <= 0:
        meta = HybridActionSelection(tuple(), {}, 0, 0, str(ranker_revision), False)
        return tuple(), {}, False, True, meta
    if chosen_idx < 0 or chosen_idx >= n:
        raise ValueError(f"chosen_idx {chosen_idx} outside legal menu of size {n}")
    if n <= int(max_actions_per_frame):
        idxs = tuple(range(n))
        reasons = {i: "full_menu_within_max_actions" for i in idxs}
        meta = HybridActionSelection(idxs, reasons, n, n, str(ranker_revision), False)
        return idxs, reasons, False, False, meta
    if branch_action_budget is None:
        return tuple(), {}, False, True, None

    budget = max(2, min(int(branch_action_budget), n))
    base = select_budgeted_action_indices(frame, int(chosen_idx), budget=budget, rng=rng)
    ranker_scores, ranker_available = _ranker_prior_scores(frame, str(ranker_revision))
    profile_scores = _profile_prior_scores(frame)
    voted_set = {int(v) for v in voted_indices if 0 <= int(v) < n}

    # Combined score is for filling only; mandatory/diversity slots are handled
    # explicitly.  Ranker gets less weight than visible disagreement/diversity so
    # a weak model cannot dominate the label budget.
    combined: dict[int, float] = {}
    base_set = set(int(i) for i in base.indices)
    for idx in range(n):
        combined[idx] = (
            (1.00 if idx in voted_set else 0.0)
            + (0.35 if idx in base_set else 0.0)
            + 0.25 * float(profile_scores.get(idx, 0.0))
            + 0.20 * float(ranker_scores.get(idx, 0.0))
        )

    selected: list[int] = []
    reasons: dict[int, str] = dict(base.reasons)

    def add(idx: int, reason: str) -> None:
        if idx < 0 or idx >= n:
            return
        if idx not in selected and len(selected) < budget:
            selected.append(int(idx))
        _append_reason(reasons, int(idx), reason)

    # 1. Always compare the behavior action.
    add(int(chosen_idx), "behavior_chosen")

    # 2. Keep at most two public-disagreement votes first.  This avoids the
    # rev0039 failure mode where votes can fill the entire budget.
    voted_sorted = sorted(voted_set, key=lambda i: (-combined.get(i, 0.0), i))
    for idx in voted_sorted[: max(1, min(2, budget - 1))]:
        add(idx, "screen_vote")

    # 3. Include one top cheap-prior action if it is not already selected.
    top_prior = sorted(range(n), key=lambda i: (-combined.get(i, 0.0), i))
    if top_prior:
        add(top_prior[0], "hybrid_top_prior")

    # 4. Preserve diversity: one representative per semantic key, ordered by
    # combined score within each group.
    groups: dict[tuple[str, str, str], list[int]] = {}
    for idx, action in enumerate(frame.legal_actions):
        groups.setdefault(action_diversity_key(action), []).append(idx)
    reps = []
    for key, idxs in groups.items():
        best = sorted(idxs, key=lambda i: (-combined.get(i, 0.0), i))[0]
        reps.append((key, best))
    for _key, idx in sorted(reps, key=lambda row: (-combined.get(row[1], 0.0), row[0], row[1])):
        add(idx, "diversity_representative")
        if len(selected) >= budget:
            break

    # 5. Fill remaining slots by combined score with a tiny deterministic random
    # tie-break supplied by caller's seeded RNG.
    leftovers = [i for i in range(n) if i not in selected]
    jitter = {i: rng.random() * 1e-6 for i in leftovers}
    for idx in sorted(leftovers, key=lambda i: (-(combined.get(i, 0.0) + jitter[i]), i)):
        add(idx, "hybrid_score_fill")
        if len(selected) >= budget:
            break

    idxs = tuple(sorted(selected))
    meta = HybridActionSelection(
        indices=idxs,
        reasons={i: reasons.get(i, "selected") for i in idxs},
        full_action_count=n,
        budget=budget,
        ranker_revision=str(ranker_revision),
        ranker_available=bool(ranker_available),
    )
    return idxs, dict(meta.reasons), True, len(idxs) <= 1, meta
