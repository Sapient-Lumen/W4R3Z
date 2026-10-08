from __future__ import annotations

from typing import Any

from .errors import LacunaError
from .store import Cube

INTERPRETATION_CONTRACT = [
    "Unknown is not false.",
    "A report is not an observation.",
    "A belief is not world truth.",
    "An anchor is not permission to invent its cause.",
    "An explicit claim relation constrains compatibility; it does not manufacture an unstored fact.",
    "A cardinality constraint rejects impossible partial valuations; it does not fill unknown members.",
    "Candidate worlds may disagree without corrupting the ledger.",
    "Particle weights and evidence likelihoods are authored planning quantities, not certified probabilities.",
    "Reweighting does not select, prune, merge, or canonize a candidate world.",
    "A factor reconciliation replays authorized evidence from an immutable baseline; superseded factors remain visible as excluded custody.",
    "Ambient exposure is not explicit dependence; consequence links require authored custody.",
    "Commitment raises are monotone; changing assigned truth creates a revision successor rather than overwriting history.",
    "Recorded consequences survive endpoint revision until explicitly retired or replaced with lineage custody.",
    "A fair-play seal proves continuity of one exact opening, not truth, authorship, completeness, or real-world time.",
    "Narrative meaning may remain flexible after physical consequences become fixed.",
]


def build_context(
    cube: Cube,
    *,
    agent_id: str | None = None,
    world_id: str | None = None,
) -> dict[str, Any]:
    """Build the single authoritative context projection used by every renderer.

    Perspective-scoped packets and hidden-world packets are intentionally mutually
    exclusive. A caller that needs both must request two separately labelled views.
    """
    if agent_id is not None and world_id is not None:
        raise LacunaError(
            "unsafe-context-scope",
            "a perspective-scoped context may not name a candidate world",
            {
                "agent_id": agent_id,
                "world_id": world_id,
                "rule": "request an audience view and a separately labelled privileged planner view",
            },
        )

    canon = cube.canon()
    unknowns = cube.unknowns()
    all_conflicts = cube.conflicts()
    perspective_scoped = agent_id is not None

    if perspective_scoped:
        perspective = cube.perspective(agent_id)
        assertions = perspective["assertions"]
        questions = perspective["open_questions"]
        fair_play_seals = perspective["fair_play_seals"]
        visible_assertion_ids = {item["assertion_id"] for item in assertions}
        visible_claim_ids = {item["claim_id"] for item in assertions}
        visible_claim_ids.update(
            item["about_claim_id"]
            for item in questions
            if item.get("about_claim_id") is not None
        )
        anchors = [
            item for item in canon["anchors"] if item["assertion_id"] in visible_assertion_ids
        ]
        conflicts = [
            item
            for item in all_conflicts
            if item.get("relation_id") is None
            and item.get("constraint_id") is None
            and item.get("consequence_id") is None
            and item.get("left_assertion_id") in visible_assertion_ids
            and item.get("right_assertion_id") in visible_assertion_ids
        ]
        visible_anchor_claim_ids = {item["claim_id"] for item in anchors}
        claims_by_id = {item["claim_id"]: item for item in cube.claims()}
        unsettled = [
            claims_by_id[claim_id]
            for claim_id in sorted(visible_claim_ids)
            if claim_id in claims_by_id and claim_id not in visible_anchor_claim_ids
        ]
        consensus: list[dict[str, Any]] = []
        evidence: list[dict[str, Any]] = []
        relations: list[dict[str, Any]] = []
        cardinalities: list[dict[str, Any]] = []
        consequences: list[dict[str, Any]] = []
        consequence_repairs: list[dict[str, Any]] = []
        consequence_repair_frontier: list[dict[str, Any]] = []
        revision_guards: list[dict[str, Any]] = []
        particle_bank: dict[str, Any] | None = None
        particle_updates: list[dict[str, Any]] = []
        particle_reconciliation_review: dict[str, Any] | None = None
        particle_reconciliations: list[dict[str, Any]] = []
        worlds: list[dict[str, Any]] = []
        omitted = {
            "cross_world_consensus": "hidden-world agreement is privileged planner state",
            "evidence_links": "evidence-link interpretation is privileged planner state",
            "claim_relations": "cross-claim integrity constraints are privileged planner state",
            "cardinality_constraints": "multi-claim integrity constraints are privileged planner state",
            "consequence_links": "explicit latent-world consequence custody is privileged planner state",
            "consequence_repairs": "consequence replacement lineage is privileged planner state",
            "consequence_repair_frontier": "head-bound repair authorization is privileged planner state",
            "revision_guards": "commitment and revision governance is privileged planner state",
            "particle_bank": "candidate-world weights and fingerprints are privileged planner state",
            "particle_updates": "evidence-update rationales and custody are privileged planner state",
            "particle_reconciliation_review": "factor-ledger repair authorization is privileged planner state",
            "particle_reconciliations": "factor-ledger repair custody is privileged planner state",
            "constraint_derived_conflicts": "diagnostics derived from hidden constraints are privileged planner state",
            "candidate_worlds": "latent candidate worlds are privileged planner state",
        }
        access = {
            "mode": "perspective",
            "privileged": False,
            "agent_id": agent_id,
            "world_id": None,
        }
    else:
        assertions = cube.active_assertions()
        questions = unknowns["open_questions"]
        fair_play_seals = cube.seals()
        anchors = canon["anchors"]
        consensus = canon["cross_world_consensus"]
        evidence = cube.evidence_links(world_id=world_id)
        relations = cube.claim_relations()
        cardinalities = cube.cardinality_constraints()
        consequences = [
            item
            for item in cube.consequence_links()
            if world_id is None
            or item.get("premise_world_id") == world_id
            or item.get("dependent_world_id") == world_id
        ]
        visible_consequence_ids = {
            str(item["consequence_id"]) for item in consequences
        }
        consequence_repairs = [
            item
            for item in cube.consequence_repairs()
            if world_id is None
            or item["predecessor_consequence_id"] in visible_consequence_ids
            or item["successor_consequence_id"] in visible_consequence_ids
        ]
        consequence_repair_frontier = cube.consequence_repair_frontier(
            world_id=world_id
        )
        revision_guards = cube.revision_guards(world_id=world_id)
        if world_id is None:
            particle_bank = cube.particle_bank()
            particle_updates = cube.particle_updates()[-20:]
            particle_reconciliation_review = cube.particle_reconciliation_review()
            particle_reconciliations = cube.particle_reconciliations()[-20:]
        else:
            particle_bank = None
            particle_updates = []
            particle_reconciliation_review = None
            particle_reconciliations = []
        conflicts = all_conflicts
        unsettled = unknowns["unsettled_claims"]
        worlds = [
            item
            for item in cube.worlds()
            if item["status"] in {"live", "selected"}
            and (world_id is None or item["world_id"] == world_id)
        ]
        if world_id is not None:
            cube._require_world(world_id)
        omitted = {}
        if world_id is not None:
            omitted.update(
                {
                    "particle_bank": "the particle bank is a complete-population projection and is omitted from world-scoped context",
                    "particle_updates": "global evidence-update custody is omitted from world-scoped context",
                    "particle_reconciliation_review": "complete-population factor repair authorization is omitted from world-scoped context",
                    "particle_reconciliations": "global factor repair custody is omitted from world-scoped context",
                }
            )
        access = {
            "mode": "planner",
            "privileged": True,
            "agent_id": None,
            "world_id": world_id,
        }

    return {
        "event": "lacuna.context",
        "schema": "lacuna.context.v1",
        "cube_id": cube.meta("cube_id"),
        "head": cube.head(),
        "access": access,
        "interpretation_contract": list(INTERPRETATION_CONTRACT),
        "anchors": anchors,
        "cross_world_consensus": consensus,
        "assertions": assertions,
        "fair_play_seals": fair_play_seals,
        "evidence_links": evidence,
        "claim_relations": relations,
        "cardinality_constraints": cardinalities,
        "consequence_links": consequences,
        "consequence_repairs": consequence_repairs,
        "consequence_repair_frontier": consequence_repair_frontier,
        "revision_guards": revision_guards,
        "particle_bank": particle_bank,
        "particle_updates": particle_updates,
        "particle_reconciliation_review": particle_reconciliation_review,
        "particle_reconciliations": particle_reconciliations,
        "candidate_worlds": worlds,
        "open_questions": questions,
        "conflicts": conflicts,
        "unsettled_claims": unsettled,
        "omitted": omitted,
        "nonclaim": (
            "This projection reports recorded epistemic state. It does not certify that generated prose "
            "mentions every visible assertion or that every sentence in prose is represented here."
        ),
    }
