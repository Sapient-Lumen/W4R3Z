from __future__ import annotations

from collections import deque
from typing import Any, Iterable

COMMITMENT_ORDER = ("tentative", "soft", "firm", "hard")
COMMITMENT_RANK = {value: index for index, value in enumerate(COMMITMENT_ORDER)}
COMMITMENT_BASES = {
    "legacy",
    "planning",
    "authored",
    "evidence",
    "disclosure",
    "precommitment",
}
WRITABLE_COMMITMENT_BASES = COMMITMENT_BASES - {"legacy"}

HARD_COMMITMENT_BASES = {"authored", "evidence", "disclosure", "precommitment"}
SOURCE_EXPECTED_BASES = {"evidence", "disclosure"}

CONSEQUENCE_RELATIONS = {
    "causes",
    "explains",
    "discloses",
    "motivates",
    "promises",
    "constrains",
}
CONSEQUENCE_SEVERITIES = {"notice", "material", "binding"}
CONSEQUENCE_DEPENDENT_KINDS = {"assertion", "world_assignment", "question"}

COMMITMENT_POINTS = {
    "tentative": 0,
    "soft": 2,
    "firm": 6,
    "hard": 13,
}
CONSEQUENCE_POINTS = {
    "notice": 1,
    "material": 4,
    "binding": 12,
}

REVISION_GRAPH_MAX_DEPTH = 32
REVISION_GRAPH_MAX_NODES = 512


def is_strict_raise(previous: str, target: str) -> bool:
    """Return whether target is strictly more committed than previous."""
    return COMMITMENT_RANK[target] > COMMITMENT_RANK[previous]


def is_adjacent_raise(previous: str, target: str) -> bool:
    """Return whether target is exactly one commitment step above previous."""
    return COMMITMENT_RANK[target] == COMMITMENT_RANK[previous] + 1


def burden_class(score: int, *, blocked: bool) -> str:
    if blocked:
        return "blocked"
    if score <= 4:
        return "low"
    if score <= 11:
        return "moderate"
    if score <= 24:
        return "high"
    return "severe"


def calculate_revision_burden(
    *,
    commitment: str,
    world_status: str,
    public_assertions: int,
    restricted_assertions: int,
    private_assertions: int,
    anchored_assertions: int,
    evidence_links: int,
    open_questions: int,
    structural_constraints: int,
    inherited_live_assignments: int,
    consensus_world_count: int,
    consequence_severities: Iterable[str],
    blocker_count: int,
) -> dict[str, Any]:
    """Apply a transparent ordinal policy; this is not a causal truth metric."""
    severities = list(consequence_severities)
    components = {
        "commitment": COMMITMENT_POINTS[commitment],
        "selected_world": 4 if world_status == "selected" else 0,
        "public_assertion_history": public_assertions * 4,
        "restricted_assertion_history": restricted_assertions * 3,
        "private_assertion_history": private_assertions,
        "anchored_assertions": anchored_assertions * 8,
        "evidence_links": evidence_links * 2,
        "open_questions": open_questions,
        "structural_constraints": structural_constraints,
        "inherited_live_assignments": inherited_live_assignments * 3,
        "cross_world_consensus": 5 if consensus_world_count > 1 else 0,
        "explicit_consequences": sum(CONSEQUENCE_POINTS[value] for value in severities),
    }
    total = sum(components.values())
    blocked = blocker_count > 0
    return {
        "policy": "lacuna.revision-burden.v1",
        "components": components,
        "total": total,
        "class": burden_class(total, blocked=blocked),
        "blocked": blocked,
        "nonclaim": (
            "The score is an inspectable review policy over recorded custody. It is not a "
            "probability, utility, proof of causality, or certificate of narrative fairness."
        ),
    }


def assignment_cycle_path(
    edges: Iterable[tuple[str, str]],
    *,
    proposed_premise: str,
    proposed_dependent: str,
) -> list[str] | None:
    """Return a deterministic cycle witness if premise -> dependent would close a cycle."""
    adjacency: dict[str, list[str]] = {}
    for left, right in edges:
        adjacency.setdefault(left, []).append(right)
    for values in adjacency.values():
        values.sort()

    queue: deque[tuple[str, list[str]]] = deque([(proposed_dependent, [proposed_dependent])])
    seen = {proposed_dependent}
    while queue:
        node, path = queue.popleft()
        if node == proposed_premise:
            return [proposed_premise, *path]
        for neighbor in adjacency.get(node, []):
            if neighbor in seen:
                continue
            seen.add(neighbor)
            queue.append((neighbor, [*path, neighbor]))
    return None
