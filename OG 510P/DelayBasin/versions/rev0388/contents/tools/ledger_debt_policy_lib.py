import re
from typing import Any

LEDGER_DEBT_POLICIES: dict[str, dict[str, Any]] = {
    "FOLLOWTHROUGH-QUEUE.json": {
        "state_key": "state",
        "state_mirror_keys": ("followthrough_state",),
        "live_state": "queued",
        "budget": 180,
        "minimum_headroom": 16,
        "transition_key": "expiry_revision",
        "transition_state": "expired",
        "min_cumulative_transitions": 29,
        "risk_id": "AE-RISK-0003",
        "risk_label": "queued_followthrough_headroom_below_reserve",
        "repair": "burn down or batch-close stale followthrough rows before opening new governance loops",
    },
    "ASSUMPTION-LEDGER.json": {
        "state_key": "state",
        "state_mirror_keys": ("assumption_state",),
        "live_state": "active",
        "budget": 180,
        "minimum_headroom": 16,
        "transition_key": "retirement_revision",
        "transition_state": "retired",
        "min_cumulative_transitions": 27,
        "risk_id": "AE-RISK-0006",
        "risk_label": "active_assumptions_headroom_below_reserve",
        "repair": "retire stale non-current assumptions before adding new assumption witnesses",
    },
    "OBLIGATION-LEDGER.json": {
        "state_key": "state",
        "state_mirror_keys": ("obligation_state",),
        "live_state": "open",
        "budget": 180,
        "minimum_headroom": 16,
        "transition_key": "retirement_revision",
        "transition_state": "retired",
        "min_cumulative_transitions": 29,
        "risk_id": "AE-RISK-0007",
        "risk_label": "open_obligations_headroom_below_reserve",
        "repair": "retire or satisfy stale non-current obligations before adding new evidence-debt rows",
    },
    "RETROSPECTIVE-QUEUE.json": {
        "state_key": "state",
        "state_mirror_keys": ("retrospective_state", "cooling_state"),
        "live_state": "cooling",
        "budget": 180,
        "minimum_headroom": 16,
        "transition_key": "retirement_revision",
        "transition_state": "expired",
        "min_cumulative_transitions": 20,
        "risk_id": "AE-RISK-0008",
        "risk_label": "cooling_retrospectives_headroom_below_reserve",
        "repair": "expire stale cooling retrospective rows before opening new cooldown loops",
    },
}


def revision_ordinal(value: Any) -> int | None:
    if not isinstance(value, str):
        return None
    match = re.fullmatch(r"rev(?P<ordinal>\d{4})", value)
    return int(match.group("ordinal")) if match else None


def live_rows(items: list[dict[str, Any]], policy: dict[str, Any]) -> list[dict[str, Any]]:
    key = str(policy["state_key"])
    state = policy["live_state"]
    return [row for row in items if row.get(key, row.get("state")) == state]


def row_revision(row: dict[str, Any]) -> str | None:
    value = row.get("origin_revision") or row.get("revision")
    return value if isinstance(value, str) else None


def state_mirror_mismatches(
    items: list[dict[str, Any]], policy: dict[str, Any]
) -> list[dict[str, str]]:
    """Return stale duplicate-state fields that disagree with the canonical state key.

    The ledgers accumulated compatibility mirrors such as ``assumption_state`` and
    ``cooling_state``.  Consumers still encounter them, so leaving a transitioned
    row with an old mirror value creates two public answers about whether the row
    is live.  Missing mirror fields remain allowed; present mirrors must agree.
    """

    canonical_key = str(policy["state_key"])
    mirrors = tuple(str(key) for key in policy.get("state_mirror_keys", ()))
    problems: list[dict[str, str]] = []
    for row in items:
        canonical = row.get(canonical_key, row.get("state"))
        for mirror in mirrors:
            if mirror in row and row.get(mirror) != canonical:
                problems.append(
                    {
                        "id": str(row.get("id", "missing-id")),
                        "canonical_key": canonical_key,
                        "canonical_state": str(canonical),
                        "mirror_key": mirror,
                        "mirror_state": str(row.get(mirror)),
                    }
                )
    return problems


def live_retrospectives_with_nonlive_obligations(
    retrospectives: list[dict[str, Any]], obligations: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Find cooling retrospectives whose paired same-origin obligation is closed.

    Since rev0105, retrospective and obligation rows are emitted as one revision
    cohort.  A cooling retrospective whose only paired obligation is no longer
    open is orphaned waiting-state residue, not live work.
    """

    obligations_by_revision: dict[str, list[dict[str, Any]]] = {}
    for obligation in obligations:
        revision = row_revision(obligation)
        if revision:
            obligations_by_revision.setdefault(revision, []).append(obligation)

    problems: list[dict[str, Any]] = []
    for retrospective in retrospectives:
        if retrospective.get("state") != "cooling":
            continue
        revision = row_revision(retrospective)
        paired = obligations_by_revision.get(revision or "", [])
        if paired and all(row.get("state") != "open" for row in paired):
            problems.append(
                {
                    "retrospective_id": retrospective.get("id"),
                    "origin_revision": revision,
                    "paired_obligations": [
                        {"id": row.get("id"), "state": row.get("state")} for row in paired
                    ],
                }
            )
    return problems


def live_debt_snapshot(items: list[dict[str, Any]], policy: dict[str, Any], current_revision: str) -> dict[str, Any]:
    live = live_rows(items, policy)
    budget = int(policy["budget"])
    minimum_headroom = int(policy.get("minimum_headroom", 0))
    headroom = budget - len(live)
    current_ordinal = revision_ordinal(current_revision)
    oldest = live[0] if live else None
    oldest_revision = None
    if oldest:
        oldest_revision = oldest.get("origin_revision") or oldest.get("revision")
    oldest_ordinal = revision_ordinal(oldest_revision)
    age = current_ordinal - oldest_ordinal if current_ordinal is not None and oldest_ordinal is not None else None
    return {
        "live_state": policy["live_state"],
        "live_count": len(live),
        "budget": budget,
        "minimum_headroom": minimum_headroom,
        "admission_limit": budget - minimum_headroom,
        "headroom": headroom,
        "at_budget": len(live) >= budget,
        "reserve_breached": headroom < minimum_headroom,
        "oldest_live_id": oldest.get("id") if oldest else None,
        "oldest_live_revision": oldest_revision,
        "oldest_live_age_revisions": age,
    }
