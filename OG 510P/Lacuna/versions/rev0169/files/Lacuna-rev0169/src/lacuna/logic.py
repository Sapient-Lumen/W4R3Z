from __future__ import annotations

from typing import Any

RELATION_KINDS = {"excludes", "negates", "entails", "equivalent"}
SYMMETRIC_RELATIONS = {"excludes", "negates", "equivalent"}
RELATION_DESCRIPTIONS = {
    "excludes": "At most one endpoint may be true; this does not assert that either is true.",
    "negates": "When both endpoints are known, their truth values must differ.",
    "entails": "The left endpoint may not be true while the right endpoint is false.",
    "equivalent": "When both endpoints are known, their truth values must agree.",
}


def normalize_relation_endpoints(
    relation: str,
    left_claim_id: str,
    right_claim_id: str,
) -> tuple[str, str]:
    """Canonicalize endpoint order only for symmetric relation kinds."""
    if relation in SYMMETRIC_RELATIONS and right_claim_id < left_claim_id:
        return right_claim_id, left_claim_id
    return left_claim_id, right_claim_id


def relation_conflicts(relation: str, left_truth: str, right_truth: str) -> bool:
    """Return whether two explicit truth assignments violate a relation.

    Unknown deliberately carries no closed-world consequence. This function checks
    compatibility; it does not infer or materialize another assignment.
    """
    if left_truth == "unknown" or right_truth == "unknown":
        return False
    if relation == "excludes":
        return left_truth == "true" and right_truth == "true"
    if relation == "negates":
        return left_truth == right_truth
    if relation == "entails":
        return left_truth == "true" and right_truth == "false"
    if relation == "equivalent":
        return left_truth != right_truth
    raise ValueError(f"unknown claim relation: {relation!r}")


def pair_conflict(
    *,
    left_claim_id: str,
    left_truth: str,
    right_claim_id: str,
    right_truth: str,
    relation: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    """Describe an explicit inconsistency between two assignments, if any."""
    if "unknown" in {left_truth, right_truth}:
        return None
    if left_claim_id == right_claim_id:
        if left_truth != right_truth:
            return {
                "kind": "opposite-stances",
                "claim_id": left_claim_id,
                "left_truth": left_truth,
                "right_truth": right_truth,
            }
        return None
    if relation is None:
        return None

    relation_left = str(relation["left_claim_id"])
    relation_right = str(relation["right_claim_id"])
    if left_claim_id == relation_left and right_claim_id == relation_right:
        oriented_left_truth, oriented_right_truth = left_truth, right_truth
    elif left_claim_id == relation_right and right_claim_id == relation_left:
        oriented_left_truth, oriented_right_truth = right_truth, left_truth
    else:
        return None

    relation_kind = str(relation["relation"])
    if not relation_conflicts(relation_kind, oriented_left_truth, oriented_right_truth):
        return None
    return {
        "kind": "claim-relation-violation",
        "relation_id": relation.get("relation_id"),
        "relation": relation_kind,
        "left_claim_id": relation_left,
        "right_claim_id": relation_right,
        "left_truth": oriented_left_truth,
        "right_truth": oriented_right_truth,
    }


def cardinality_description(min_true: int, max_true: int, member_count: int) -> str:
    """Render a precise, non-inferential description of a cardinality bound."""
    if min_true == max_true:
        return f"Exactly {min_true} of {member_count} members must be true."
    if min_true == 0:
        return f"At most {max_true} of {member_count} members may be true."
    if max_true == member_count:
        return f"At least {min_true} of {member_count} members must be true."
    return f"Between {min_true} and {max_true} of {member_count} members must be true."


def _record_truth(record: dict[str, Any]) -> str:
    return str(record.get("truth", record.get("stance", "unknown")))


def _record_identity(record: dict[str, Any]) -> dict[str, Any]:
    if record.get("assertion_id") is not None:
        return {"kind": "assertion", "id": str(record["assertion_id"])}
    if record.get("assignment_id") is not None:
        return {"kind": "world_assignment", "id": str(record["assignment_id"])}
    candidate_kind = record.get("candidate_kind")
    candidate_id = record.get("candidate_id")
    if candidate_kind is not None:
        result = {"kind": str(candidate_kind), "candidate": True}
        if candidate_id is not None:
            result["id"] = str(candidate_id)
        return result
    return {"kind": "record", "candidate": True}


def _record_sort_key(record: dict[str, Any]) -> tuple[str, str, int, int]:
    identity = _record_identity(record)
    return (
        str(identity.get("kind", "record")),
        str(identity.get("id", "")),
        -10**18 if record.get("valid_from") is None else int(record["valid_from"]),
        10**18 if record.get("valid_to") is None else int(record["valid_to"]),
    )


def _active_at(record: dict[str, Any], timeline_id: str, tick: int) -> bool:
    if str(record.get("timeline_id", "main")) != timeline_id:
        return False
    valid_from = record.get("valid_from")
    valid_to = record.get("valid_to")
    return (valid_from is None or int(valid_from) <= tick) and (
        valid_to is None or tick <= int(valid_to)
    )


def _intersection(records: list[dict[str, Any]]) -> tuple[int | None, int | None]:
    finite_starts = [int(item["valid_from"]) for item in records if item.get("valid_from") is not None]
    finite_ends = [int(item["valid_to"]) for item in records if item.get("valid_to") is not None]
    return (max(finite_starts) if finite_starts else None, min(finite_ends) if finite_ends else None)


def cardinality_conflict(
    constraint: dict[str, Any],
    records: list[dict[str, Any]],
) -> dict[str, Any] | None:
    """Return one deterministic witness that a partial valuation is unsatisfiable.

    Missing assignments and explicit ``unknown`` values remain unresolved. A lower
    bound is violated only when enough members are explicitly false that no
    completion could satisfy the bound. An upper bound is violated only when too
    many members are explicitly true. The function never derives or materializes
    the truth value of an unresolved member.
    """
    members = tuple(str(item) for item in constraint["claim_ids"])
    member_set = set(members)
    min_true = int(constraint["min_true"])
    max_true = int(constraint["max_true"])
    relevant = [
        item
        for item in records
        if str(item.get("claim_id")) in member_set and _record_truth(item) in {"true", "false"}
    ]
    if not relevant:
        return None

    timelines = sorted({str(item.get("timeline_id", "main")) for item in relevant})
    for timeline_id in timelines:
        timeline_records = [
            item for item in relevant if str(item.get("timeline_id", "main")) == timeline_id
        ]
        points = {
            int(value)
            for item in timeline_records
            for value in (item.get("valid_from"), item.get("valid_to"))
            if value is not None
        }
        if not points:
            points = {0}
        for tick in sorted(points):
            active_by_claim: dict[str, dict[str, list[dict[str, Any]]]] = {}
            for record in timeline_records:
                if not _active_at(record, timeline_id, tick):
                    continue
                claim_id = str(record["claim_id"])
                truth = _record_truth(record)
                active_by_claim.setdefault(claim_id, {"true": [], "false": []})[truth].append(record)

            true_claims: list[str] = []
            false_claims: list[str] = []
            representative: dict[tuple[str, str], dict[str, Any]] = {}
            for claim_id in members:
                states = active_by_claim.get(claim_id)
                if not states:
                    continue
                has_true = bool(states["true"])
                has_false = bool(states["false"])
                # A same-claim contradiction is handled by the pairwise engine. Do
                # not double-count an already inconsistent member in either bound.
                if has_true == has_false:
                    continue
                truth = "true" if has_true else "false"
                collection = sorted(states[truth], key=_record_sort_key)
                representative[(claim_id, truth)] = collection[0]
                (true_claims if truth == "true" else false_claims).append(claim_id)

            violation: str | None = None
            witness_truth: str | None = None
            witness_claim_ids: list[str] = []
            if len(true_claims) > max_true:
                violation = "upper-bound-exceeded"
                witness_truth = "true"
                witness_claim_ids = sorted(true_claims)[: max_true + 1]
            elif len(false_claims) > len(members) - min_true:
                violation = "lower-bound-impossible"
                witness_truth = "false"
                witness_claim_ids = sorted(false_claims)[: len(members) - min_true + 1]
            if violation is None or witness_truth is None:
                continue

            witness_records = [
                representative[(claim_id, witness_truth)] for claim_id in witness_claim_ids
            ]
            valid_from, valid_to = _intersection(witness_records)
            return {
                "kind": "cardinality-constraint-violation",
                "violation": violation,
                "constraint_id": constraint.get("constraint_id"),
                "label": constraint.get("label"),
                "min_true": min_true,
                "max_true": max_true,
                "member_count": len(members),
                "known_true_count": len(true_claims),
                "known_false_count": len(false_claims),
                "unresolved_count": len(members) - len(true_claims) - len(false_claims),
                "timeline_id": timeline_id,
                "witness_tick": tick,
                "witness_valid_from": valid_from,
                "witness_valid_to": valid_to,
                "witness_truth": witness_truth,
                "witness_claim_ids": witness_claim_ids,
                "witness_records": [_record_identity(item) for item in witness_records],
                "nonclaim": (
                    "This witness shows that the recorded partial valuation cannot satisfy the bound. "
                    "It does not derive truth values for unresolved members."
                ),
            }
    return None
