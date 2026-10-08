from __future__ import annotations

import copy
from typing import Any

from .errors import LacunaError
from .orchestration import (
    turn_packet_sha256,
    validate_proposal_binding,
    validate_turn_packet,
)
from .providers import CHECKPOINT_AGENT_ROLES, PROVIDERS, provider_alias, provider_aliases
from .store import Cube
from .turns import (
    CHECKPOINT_TURN_OPERATIONS,
    TURN_NARRATION_PLACEHOLDER,
    TURN_PREPARATION_SCHEMA,
    build_turn_packet,
    commit_prepared_turn,
    prepare_turn_proposal,
    recover_prepared_turn_receipt,
    validate_turn_preparation,
    validate_turn_receipt,
)
from .util import (
    SHA256_RE,
    canonical_json,
    new_id,
    pretty_json,
    require_id,
    require_list,
    require_mapping,
    require_string,
    sha256_text,
    utc_now,
)

CHECKPOINT_REQUEST_SCHEMA = "lacuna.checkpoint-request.v1"
CHECKPOINT_TASK_CARD_SCHEMA = "lacuna.checkpoint-task-card.v1"
CHECKPOINT_CANDIDATES_SCHEMA = "lacuna.checkpoint-candidates.v1"
CHECKPOINT_JUDGMENT_SCHEMA = "lacuna.checkpoint-judgment.v1"
CHECKPOINT_COMPRESSION_SCHEMA = "lacuna.checkpoint-compression.v1"
CHECKPOINT_PROPOSAL_SCHEMA = "lacuna.checkpoint-proposal.v1"
CHECKPOINT_VERIFIER_SCHEMA = "lacuna.checkpoint-verifier-return.v1"
CHECKPOINT_REVIEW_SCHEMA = "lacuna.checkpoint-review.v1"
CHECKPOINT_COMMIT_SCHEMA = "lacuna.checkpoint-commit-receipt.v1"
CHECKPOINT_DISPATCH_SCHEMA = "lacuna.checkpoint-agent-dispatch.v1"

CHECKPOINT_ROLES = CHECKPOINT_AGENT_ROLES
CHECKPOINT_SELECTION_RULE = "highest-weighted-eligible-then-lexicographic-candidate-id"
CHECKPOINT_SCORE_DIMENSIONS = (
    "coherence",
    "player_agency",
    "genre_fit",
    "character_believability",
    "payoff_density",
    "novelty",
    "coincidence_sanity",
)
DEFAULT_SCORE_WEIGHTS = {
    "coherence": 20,
    "player_agency": 15,
    "genre_fit": 10,
    "character_believability": 15,
    "payoff_density": 15,
    "novelty": 10,
    "coincidence_sanity": 15,
}
CHECKPOINT_CHECKS = (
    "observed_canon_untouched",
    "exposed_consequences_respected",
    "fair_play_evidence_not_retconned",
    "all_existing_unknowns_preserved",
    "selection_evidence_internally_consistent",
    "compression_within_budget",
    "custody_source_exact",
    "operation_surface_within_checkpoint_grant",
    "narration_does_not_present_hidden_state_as_observation",
)
CHECKPOINT_DISQUALIFIERS = {
    "observed-canon-contradiction",
    "exposed-consequence-rewrite",
    "fair-play-evidence-retcon",
    "unbounded-coincidence",
    "identity-drift",
    "compression-impossible",
    "other",
}

CHECKPOINT_ROLE_OUTPUT_SCHEMAS = {
    "lacuna-retcon-generator": CHECKPOINT_CANDIDATES_SCHEMA,
    "lacuna-retcon-judge": CHECKPOINT_JUDGMENT_SCHEMA,
    "lacuna-retcon-compressor": CHECKPOINT_COMPRESSION_SCHEMA,
    "lacuna-retcon-verifier": CHECKPOINT_VERIFIER_SCHEMA,
}
CHECKPOINT_ROLE_UPSTREAM = {
    "lacuna-retcon-generator": (),
    "lacuna-retcon-judge": (("checkpoint-candidates", CHECKPOINT_CANDIDATES_SCHEMA),),
    "lacuna-retcon-compressor": (
        ("checkpoint-candidates", CHECKPOINT_CANDIDATES_SCHEMA),
        ("checkpoint-judgment", CHECKPOINT_JUDGMENT_SCHEMA),
    ),
    "lacuna-retcon-verifier": (("checkpoint-proposal", CHECKPOINT_PROPOSAL_SCHEMA),),
}

REQUEST_FIELDS = {
    "event",
    "schema",
    "checkpoint_id",
    "created_at",
    "cube_id",
    "expected_head",
    "trigger_sha256",
    "turn_packet_sha256",
    "turn_packet",
    "policy",
    "protected_state",
    "protected_state_sha256",
    "workflow",
    "nonclaims",
}
POLICY_FIELDS = {
    "schema",
    "candidate_count",
    "rollout_horizon_turns",
    "compression_max_chars",
    "max_operations",
    "score_dimensions",
    "score_weights",
    "selection_rule",
    "blind_judging",
    "preserve_all_existing_unknowns",
    "forbid_observed_canon_mutation",
    "forbid_aesthetic_particle_weighting",
}
CARD_FIELDS = {
    "event",
    "schema",
    "role",
    "task_id",
    "checkpoint_id",
    "request_sha256",
    "upstream",
    "provider_aliases",
    "objective",
    "input_payload",
    "instructions",
    "forbidden_context",
    "output_contract",
    "authority",
    "next_command",
    "nonclaims",
}
CANDIDATES_FIELDS = {
    "schema",
    "task_id",
    "checkpoint_id",
    "request_sha256",
    "candidates",
    "generation_notes",
    "nonclaims",
}
CANDIDATE_FIELDS = {
    "candidate_id",
    "title",
    "hypothesis_card",
    "story_so_far_explanation",
    "future_arc_summary",
    "preserved_unknown_ids",
    "promoted_incidental_details",
    "commitment_risks",
    "fair_play_risks",
    "identity_drift_risks",
    "rollout",
    "provenance",
}
ROLLOUT_FIELDS = {"horizon_turns", "turns", "summary"}
PROVENANCE_FIELDS = {"provider", "model", "model_version", "invocation_id", "notes"}
JUDGMENT_FIELDS = {
    "schema",
    "task_id",
    "checkpoint_id",
    "request_sha256",
    "candidates_sha256",
    "blind_review",
    "assessor",
    "scores",
    "selected_candidate_id",
    "selection_rule",
    "selection_rationale",
    "nonclaims",
}
SCORE_FIELDS = {
    "candidate_id",
    "eligible",
    "disqualifiers",
    "dimensions",
    "weighted_score",
    "rationale",
}
COMPRESSION_FIELDS = {
    "schema",
    "task_id",
    "checkpoint_id",
    "request_sha256",
    "candidates_sha256",
    "judgment_sha256",
    "selected_candidate_id",
    "state_card",
    "retained_elements",
    "omitted_elements",
    "preserved_unknown_ids",
    "forbidden_contradictions",
    "next_pressures",
    "narration",
    "operations",
    "message",
    "nonclaims",
}
PROPOSAL_FIELDS = {
    "event",
    "schema",
    "checkpoint_id",
    "request_sha256",
    "candidates_sha256",
    "judgment_sha256",
    "compression_sha256",
    "selected_candidate_id",
    "compression_artifact",
    "compression",
    "selection_evidence",
    "selection_evidence_sha256",
    "turn_proposal",
    "nonclaims",
}
VERIFIER_FIELDS = {
    "schema",
    "task_id",
    "checkpoint_id",
    "request_sha256",
    "proposal_sha256",
    "status",
    "checks",
    "findings",
    "recommended_action",
    "nonclaims",
}
FINDING_FIELDS = {"severity", "code", "message", "evidence_paths"}
REVIEW_FIELDS = {
    "event",
    "schema",
    "reviewed_at",
    "checkpoint_id",
    "cube_id",
    "request_sha256",
    "candidates_sha256",
    "judgment_sha256",
    "proposal_sha256",
    "verifier_sha256",
    "selection_evidence_sha256",
    "mechanical_status",
    "mechanical_checks",
    "turn_preparation",
    "turn_preparation_sha256",
    "nonclaims",
}
COMMIT_FIELDS = {
    "event",
    "schema",
    "overall_status",
    "checkpoint_id",
    "cube_id",
    "selected_candidate_id",
    "selection_evidence_sha256",
    "checkpoint_review_sha256",
    "turn_receipt",
    "narration",
    "nonclaims",
}
CHECKPOINT_COMMIT_NONCLAIMS = [
    "The receipt proves the exact typed ledger transition, not that the selected latent world is metaphysically true or aesthetically best.",
    "Rejected rollouts remain noncanon even when their digests are retained externally.",
    "A recovered receipt confirms an exact already-committed change and does not append duplicate events.",
]
DISPATCH_FIELDS = {
    "event",
    "schema",
    "checkpoint_id",
    "task_id",
    "provider",
    "role",
    "agent_name",
    "input_card_sha256",
    "input_card",
    "return_contract",
    "instructions",
    "authority",
    "nonclaims",
}


def _fail(code: str, message: str, details: dict[str, Any] | None = None) -> None:
    raise LacunaError(code, message, details)


def _strict(value: Any, field: str, fields: set[str], *, code: str) -> dict[str, Any]:
    try:
        document = require_mapping(value, field)
    except ValueError as exc:
        raise LacunaError(code, str(exc)) from exc
    unexpected = sorted(set(document) - fields)
    missing = sorted(fields - set(document))
    if unexpected or missing:
        _fail(code, f"{field} has an invalid field set", {"unexpected": unexpected, "missing": missing})
    return document


def _digest(value: Any, *, code: str, label: str) -> str:
    try:
        return sha256_text(canonical_json(value))
    except (TypeError, ValueError) as exc:
        raise LacunaError(code, f"{label} is not canonical JSON: {exc}") from exc


def _sha(value: Any, field: str, *, code: str) -> str:
    if not isinstance(value, str) or not SHA256_RE.fullmatch(value):
        _fail(code, f"{field} must be a lowercase SHA-256 digest")
    return value


def _integer(value: Any, field: str, *, minimum: int, maximum: int, code: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not minimum <= value <= maximum:
        _fail(code, f"{field} must be an integer from {minimum} through {maximum}")
    return value


def _string_list(
    value: Any,
    field: str,
    *,
    code: str,
    max_items: int = 500,
    max_len: int = 10000,
    unique: bool = False,
) -> list[str]:
    try:
        raw = require_list(value, field)
    except ValueError as exc:
        raise LacunaError(code, str(exc)) from exc
    if len(raw) > max_items:
        _fail(code, f"{field} exceeds {max_items} items")
    result: list[str] = []
    for index, item in enumerate(raw):
        try:
            result.append(require_string(item, f"{field}[{index}]", allow_empty=False, max_len=max_len))
        except ValueError as exc:
            raise LacunaError(code, str(exc)) from exc
    if unique and len(result) != len(set(result)):
        _fail(code, f"{field} must not contain duplicates")
    return result


def _optional_string(value: Any, field: str, *, code: str, max_len: int = 4096) -> str | None:
    if value is None:
        return None
    try:
        return require_string(value, field, allow_empty=True, max_len=max_len)
    except ValueError as exc:
        raise LacunaError(code, str(exc)) from exc


def _provenance(value: Any, field: str, *, code: str) -> dict[str, Any]:
    document = _strict(value, field, PROVENANCE_FIELDS, code=code)
    try:
        provider = require_string(document.get("provider"), f"{field}.provider", max_len=256)
        model = require_string(document.get("model"), f"{field}.model", max_len=512)
    except ValueError as exc:
        raise LacunaError(code, str(exc)) from exc
    return {
        "provider": provider,
        "model": model,
        "model_version": _optional_string(document.get("model_version"), f"{field}.model_version", code=code, max_len=512),
        "invocation_id": _optional_string(document.get("invocation_id"), f"{field}.invocation_id", code=code, max_len=512),
        "notes": _optional_string(document.get("notes"), f"{field}.notes", code=code, max_len=10000),
    }


def _unknown_ids(protected_state: dict[str, Any]) -> list[str]:
    result: list[str] = []
    for item in protected_state.get("open_questions", []):
        if isinstance(item, dict) and isinstance(item.get("question_id"), str):
            result.append(f"question:{item['question_id']}")
    for item in protected_state.get("unsettled_claims", []):
        if isinstance(item, dict) and isinstance(item.get("claim_id"), str):
            result.append(f"claim:{item['claim_id']}")
    return sorted(set(result))


def _protected_state(packet: dict[str, Any]) -> dict[str, Any]:
    audience = packet["audience_context"]
    planner = packet["planner_context"]
    assert isinstance(audience, dict)
    assert isinstance(planner, dict)
    state = {
        "schema": "lacuna.checkpoint-protected-state.v1",
        "audience_assertions": copy.deepcopy(audience.get("assertions", [])),
        "anchors": copy.deepcopy(planner.get("anchors", [])),
        "cross_world_consensus": copy.deepcopy(planner.get("cross_world_consensus", [])),
        "fair_play_seals": copy.deepcopy(planner.get("fair_play_seals", [])),
        "claim_relations": copy.deepcopy(planner.get("claim_relations", [])),
        "cardinality_constraints": copy.deepcopy(planner.get("cardinality_constraints", [])),
        "consequence_links": copy.deepcopy(planner.get("consequence_links", [])),
        "revision_guards": copy.deepcopy(planner.get("revision_guards", [])),
        "open_questions": copy.deepcopy(planner.get("open_questions", [])),
        "unsettled_claims": copy.deepcopy(planner.get("unsettled_claims", [])),
    }
    state["unknown_ids"] = _unknown_ids(state)
    return state


def _workflow() -> dict[str, Any]:
    return {
        "schema": "lacuna.checkpoint-workflow.v1",
        "mode": "generator-judge-compressor-verifier",
        "stages": [
            {
                "ordinal": 1,
                "role": "lacuna-retcon-generator",
                "requires": ["checkpoint-request"],
                "returns": CHECKPOINT_CANDIDATES_SCHEMA,
                "context": "privileged planner context",
            },
            {
                "ordinal": 2,
                "role": "lacuna-retcon-judge",
                "requires": ["checkpoint-request", "checkpoint-candidates"],
                "returns": CHECKPOINT_JUDGMENT_SCHEMA,
                "context": "blind candidate view plus protected state",
            },
            {
                "ordinal": 3,
                "role": "lacuna-retcon-compressor",
                "requires": ["checkpoint-request", "checkpoint-candidates", "checkpoint-judgment"],
                "returns": CHECKPOINT_COMPRESSION_SCHEMA,
                "context": "selected candidate, protected state, and narrow write grant",
            },
            {
                "ordinal": 4,
                "role": "lacuna-retcon-verifier",
                "requires": ["assembled checkpoint proposal"],
                "returns": CHECKPOINT_VERIFIER_SCHEMA,
                "context": "complete proposal and anti-rubber-reality checklist",
            },
        ],
        "provider_aliases": {role: provider_aliases(role) for role in CHECKPOINT_ROLES},
        "host_directive": [
            "A capable parent should delegate each generated card to one role-dedicated context and provide exactly the card, not the cube or run directory.",
            "A host without subagents may execute the cards serially in one context, but must not claim context isolation.",
            "Only the parent invokes assemble, review, or commit. Worker outputs are untrusted advisory artifacts until exact validation passes.",
        ],
    }


def _policy(
    *,
    candidate_count: int,
    rollout_horizon_turns: int,
    compression_max_chars: int,
    max_operations: int,
) -> dict[str, Any]:
    return {
        "schema": "lacuna.checkpoint-policy.v1",
        "candidate_count": candidate_count,
        "rollout_horizon_turns": rollout_horizon_turns,
        "compression_max_chars": compression_max_chars,
        "max_operations": max_operations,
        "score_dimensions": list(CHECKPOINT_SCORE_DIMENSIONS),
        "score_weights": dict(DEFAULT_SCORE_WEIGHTS),
        "selection_rule": CHECKPOINT_SELECTION_RULE,
        "blind_judging": True,
        "preserve_all_existing_unknowns": True,
        "forbid_observed_canon_mutation": True,
        "forbid_aesthetic_particle_weighting": True,
    }


def validate_checkpoint_policy(value: Any) -> dict[str, Any]:
    code = "bad-checkpoint-policy"
    policy = _strict(value, "checkpoint policy", POLICY_FIELDS, code=code)
    if policy.get("schema") != "lacuna.checkpoint-policy.v1":
        _fail(code, "checkpoint policy schema is invalid")
    candidate_count = _integer(policy.get("candidate_count"), "candidate_count", minimum=2, maximum=12, code=code)
    rollout_horizon = _integer(policy.get("rollout_horizon_turns"), "rollout_horizon_turns", minimum=1, maximum=20, code=code)
    compression_max = _integer(policy.get("compression_max_chars"), "compression_max_chars", minimum=256, maximum=20000, code=code)
    max_operations = _integer(policy.get("max_operations"), "max_operations", minimum=1, maximum=99, code=code)
    if policy.get("score_dimensions") != list(CHECKPOINT_SCORE_DIMENSIONS):
        _fail(code, "score_dimensions must be the supported exact ordered list")
    weights = _strict(policy.get("score_weights"), "score_weights", set(CHECKPOINT_SCORE_DIMENSIONS), code=code)
    normalized_weights: dict[str, int] = {}
    for dimension in CHECKPOINT_SCORE_DIMENSIONS:
        normalized_weights[dimension] = _integer(
            weights.get(dimension),
            f"score_weights.{dimension}",
            minimum=0,
            maximum=100,
            code=code,
        )
    if sum(normalized_weights.values()) != 100:
        _fail(code, "score_weights must sum to 100")
    if policy.get("selection_rule") != CHECKPOINT_SELECTION_RULE:
        _fail(code, "selection_rule is unsupported")
    for field in (
        "blind_judging",
        "preserve_all_existing_unknowns",
        "forbid_observed_canon_mutation",
        "forbid_aesthetic_particle_weighting",
    ):
        if policy.get(field) is not True:
            _fail(code, f"{field} must be true")
    return {
        "schema": "lacuna.checkpoint-policy.v1",
        "candidate_count": candidate_count,
        "rollout_horizon_turns": rollout_horizon,
        "compression_max_chars": compression_max,
        "max_operations": max_operations,
        "score_dimensions": list(CHECKPOINT_SCORE_DIMENSIONS),
        "score_weights": normalized_weights,
        "selection_rule": CHECKPOINT_SELECTION_RULE,
        "blind_judging": True,
        "preserve_all_existing_unknowns": True,
        "forbid_observed_canon_mutation": True,
        "forbid_aesthetic_particle_weighting": True,
    }


def build_checkpoint_request(
    cube: Cube,
    *,
    audience_id: str,
    actor_id: str,
    trigger: str,
    candidate_count: int = 4,
    rollout_horizon_turns: int = 4,
    compression_max_chars: int = 6000,
    max_operations: int = 32,
) -> dict[str, Any]:
    """Open one narrow source-backed retcon checkpoint request."""
    try:
        trigger = require_string(trigger, "trigger", max_len=50000)
    except ValueError as exc:
        raise LacunaError("bad-checkpoint-trigger", str(exc)) from exc
    policy = validate_checkpoint_policy(
        _policy(
            candidate_count=candidate_count,
            rollout_horizon_turns=rollout_horizon_turns,
            compression_max_chars=compression_max_chars,
            max_operations=max_operations,
        )
    )
    verification = cube.verify()
    if verification["overall_status"] != "pass":
        _fail("cube-verification-failed", "refusing to open a checkpoint from a cube that does not pass deterministic verification")
    packet = build_turn_packet(
        cube,
        audience_id=audience_id,
        actor_id=actor_id,
        player_input=trigger,
        input_kind="session-control",
        director=True,
        world_id=None,
        allow_anchor=False,
        request_purpose="checkpoint",
    )
    packet = validate_turn_packet(packet)
    protected = _protected_state(packet)
    return {
        "event": "lacuna.checkpoint.requested",
        "schema": CHECKPOINT_REQUEST_SCHEMA,
        "checkpoint_id": new_id("chk"),
        "created_at": utc_now(),
        "cube_id": packet["cube_id"],
        "expected_head": packet["expected_head"],
        "trigger_sha256": packet["player_input_sha256"],
        "turn_packet_sha256": turn_packet_sha256(packet),
        "turn_packet": packet,
        "policy": policy,
        "protected_state": protected,
        "protected_state_sha256": _digest(protected, code="bad-checkpoint-request", label="protected state"),
        "workflow": _workflow(),
        "nonclaims": [
            "The checkpoint request opens a narrow source-backed mutation capability; it does not call a model or choose a story.",
            "Candidate rollouts, scores, and selection remain noncanon advisory artifacts unless a later exact checkpoint commit succeeds.",
            "The scoring dimensions are an experimental rubric, not objective narrative truth.",
            "The checkpoint grant cannot publish observations, close unknowns, harden commitments, alter particle weights, select or prune worlds, or access seal openings.",
        ],
    }


def validate_checkpoint_request(value: Any) -> dict[str, Any]:
    code = "bad-checkpoint-request"
    request = _strict(value, "checkpoint request", REQUEST_FIELDS, code=code)
    if request.get("event") != "lacuna.checkpoint.requested" or request.get("schema") != CHECKPOINT_REQUEST_SCHEMA:
        _fail(code, "checkpoint request event or schema is invalid")
    try:
        checkpoint_id = require_id(request.get("checkpoint_id"), "checkpoint_id")
        cube_id = require_id(request.get("cube_id"), "cube_id")
        require_string(request.get("created_at"), "created_at", max_len=128)
    except ValueError as exc:
        raise LacunaError(code, str(exc)) from exc
    expected_head = _sha(request.get("expected_head"), "expected_head", code=code)
    trigger_sha = _sha(request.get("trigger_sha256"), "trigger_sha256", code=code)
    packet_sha = _sha(request.get("turn_packet_sha256"), "turn_packet_sha256", code=code)
    protected_sha = _sha(request.get("protected_state_sha256"), "protected_state_sha256", code=code)
    packet = validate_turn_packet(request.get("turn_packet"))
    if packet.get("request_purpose") != "checkpoint" or packet.get("input_kind") != "session-control":
        _fail(code, "checkpoint request must contain a v4 checkpoint/session-control turn packet")
    if packet["access_mode"] != "director" or packet["write_grant"]["profile"] != "checkpoint":
        _fail(code, "checkpoint turn packet does not carry the narrow checkpoint grant")
    if set(packet["write_grant"]["allowed_operations"]) != CHECKPOINT_TURN_OPERATIONS:
        _fail(code, "checkpoint turn packet operation grant is not exact")
    mismatches = {}
    for field, expected, actual in (
        ("cube_id", cube_id, packet["cube_id"]),
        ("expected_head", expected_head, packet["expected_head"]),
        ("trigger_sha256", trigger_sha, packet["player_input_sha256"]),
        ("turn_packet_sha256", packet_sha, turn_packet_sha256(packet)),
    ):
        if expected != actual:
            mismatches[field] = {"expected": expected, "actual": actual}
    if mismatches:
        _fail(code, "checkpoint request identity does not match its turn packet", {"mismatches": mismatches})
    policy = validate_checkpoint_policy(request.get("policy"))
    protected = request.get("protected_state")
    expected_protected = _protected_state(packet)
    if protected != expected_protected:
        _fail(code, "protected_state is not the exact projection-derived checkpoint boundary")
    if protected_sha != _digest(expected_protected, code=code, label="protected state"):
        _fail(code, "protected_state_sha256 does not match protected_state")
    if request.get("workflow") != _workflow():
        _fail(code, "checkpoint workflow is not the supported exact role walk")
    _string_list(request.get("nonclaims"), "nonclaims", code=code, max_items=20, max_len=10000)
    _digest(request, code=code, label="checkpoint request")
    result = copy.deepcopy(request)
    result["checkpoint_id"] = checkpoint_id
    result["policy"] = policy
    result["turn_packet"] = packet
    return result


def checkpoint_request_sha256(value: Any) -> str:
    return _digest(validate_checkpoint_request(value), code="bad-checkpoint-request", label="checkpoint request")


def _task_id(request_sha256: str, role: str, upstream: list[dict[str, str]]) -> str:
    material = {
        "schema": "lacuna.checkpoint-task-identity.v1",
        "request_sha256": request_sha256,
        "role": role,
        "upstream": upstream,
    }
    return "ctk_" + sha256_text(canonical_json(material))[:24]


def _candidate_judge_view(candidates: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "candidate_id": item["candidate_id"],
            "title": item["title"],
            "hypothesis_card": item["hypothesis_card"],
            "story_so_far_explanation": item["story_so_far_explanation"],
            "future_arc_summary": item["future_arc_summary"],
            "preserved_unknown_ids": item["preserved_unknown_ids"],
            "promoted_incidental_details": item["promoted_incidental_details"],
            "commitment_risks": item["commitment_risks"],
            "fair_play_risks": item["fair_play_risks"],
            "identity_drift_risks": item["identity_drift_risks"],
            "rollout": item["rollout"],
        }
        for item in sorted(candidates["candidates"], key=lambda candidate: candidate["candidate_id"])
    ]


def _upstream(kind: str, schema: str, digest: str) -> dict[str, str]:
    return {"kind": kind, "schema": schema, "sha256": digest}


def _generator_candidate_template(request: dict[str, Any], ordinal: int) -> dict[str, Any]:
    """Return one fully shaped, policy-sized candidate slot for a generator card."""
    return {
        "candidate_id": f"candidate.{ordinal}",
        "title": f"Distinct hypothesis {ordinal}",
        "hypothesis_card": "Small latent-world state card.",
        "story_so_far_explanation": "Why the observed history makes sense under this hypothesis.",
        "future_arc_summary": "A bounded plausible continuation, not a committed plot.",
        "preserved_unknown_ids": list(request["protected_state"]["unknown_ids"]),
        "promoted_incidental_details": [],
        "commitment_risks": [],
        "fair_play_risks": [],
        "identity_drift_risks": [],
        "rollout": {
            "horizon_turns": request["policy"]["rollout_horizon_turns"],
            "turns": [
                f"Turn {turn_number}: a bounded pressure, consequence, payoff, or complication that preserves player agency and does not commit the plot."
                for turn_number in range(1, request["policy"]["rollout_horizon_turns"] + 1)
            ],
            "summary": "Bounded rollout summary.",
        },
        "provenance": {
            "provider": "unknown",
            "model": "unknown",
            "model_version": None,
            "invocation_id": None,
            "notes": None,
        },
    }


def _judge_score_template(candidate_id: str) -> dict[str, Any]:
    """Return one complete score slot so workers need not infer array cardinality."""
    return {
        "candidate_id": candidate_id,
        "eligible": False,
        "disqualifiers": ["other"],
        "dimensions": {dimension: 0 for dimension in CHECKPOINT_SCORE_DIMENSIONS},
        "weighted_score": 0,
        "rationale": "Perform the review before changing eligible to true.",
    }


def build_checkpoint_task_card(
    request_value: Any,
    *,
    role: str,
    candidates_value: Any | None = None,
    judgment_value: Any | None = None,
    proposal_value: Any | None = None,
) -> dict[str, Any]:
    request = validate_checkpoint_request(request_value)
    if role not in CHECKPOINT_ROLES:
        _fail("unknown-checkpoint-role", f"role must be one of {list(CHECKPOINT_ROLES)}")
    request_sha = checkpoint_request_sha256(request)
    upstream: list[dict[str, str]] = []
    candidates = None
    judgment = None
    proposal = None

    if role == "lacuna-retcon-generator":
        if any(item is not None for item in (candidates_value, judgment_value, proposal_value)):
            _fail("unexpected-checkpoint-upstream", "generator cards accept no upstream artifacts")
        objective = "Generate several genuinely distinct latent-world explanations and bounded future rollouts without changing canon."
        input_payload = {
            "checkpoint_id": request["checkpoint_id"],
            "policy": request["policy"],
            "protected_state": request["protected_state"],
            "planner_context": request["turn_packet"]["planner_context"],
        }
        instructions = [
            "Treat every candidate and rollout as noncanon advisory material.",
            "Generate exactly policy.candidate_count candidates; vary causal explanation, motives, pressures, and payoffs rather than paraphrasing one idea.",
            "Preserve every protected_state.unknown_ids entry exactly in each candidate.",
            "Do not rewrite audience assertions, anchors, fair-play evidence, exposed consequences, or hard commitments.",
            "Do not select a winner, mutate the cube, call checkpoint assemble/review/commit, or present hidden state to the player.",
            "For each candidate, produce exactly policy.rollout_horizon_turns ordered future beats in rollout.turns. Each beat must describe a plausible next-turn pressure or consequence, not committed canon.",
            "Use the bounded rollout to test whether a hypothesis can produce a plausible future without turning every incidental detail into foreshadowing.",
            "Record model/provider labels honestly; they are self-reported provenance, not attestation.",
            "Return exactly one JSON object matching output_contract; no prose or code fence.",
        ]
        forbidden = ["audience-facing narration", "winner selection", "cube mutation", "fair-play seal openings"]
        output_template = {
            "schema": CHECKPOINT_CANDIDATES_SCHEMA,
            "task_id": "TASK_ID",
            "checkpoint_id": request["checkpoint_id"],
            "request_sha256": request_sha,
            "candidates": [
                _generator_candidate_template(request, ordinal)
                for ordinal in range(1, request["policy"]["candidate_count"] + 1)
            ],
            "generation_notes": "How diversity was maintained.",
            "nonclaims": ["Candidates and rollouts are noncanon."],
        }
        output_schema = CHECKPOINT_CANDIDATES_SCHEMA
        next_command = "./lacuna checkpoint card REQUEST.json --role lacuna-retcon-judge --candidates CANDIDATES.json > JUDGE-CARD.json"
    elif role == "lacuna-retcon-judge":
        if candidates_value is None or judgment_value is not None or proposal_value is not None:
            _fail("missing-checkpoint-upstream", "judge cards require candidates and no later artifact")
        candidates = validate_checkpoint_candidates(candidates_value, request)
        candidates_sha = checkpoint_candidates_sha256(candidates, request)
        upstream.append(_upstream("checkpoint-candidates", CHECKPOINT_CANDIDATES_SCHEMA, candidates_sha))
        objective = "Blindly score every candidate under one declared rubric and select deterministically among eligible candidates."
        input_payload = {
            "checkpoint_id": request["checkpoint_id"],
            "policy": request["policy"],
            "protected_state": request["protected_state"],
            "blinding": {
                "provenance_removed": True,
                "generation_notes_removed": True,
                "candidate_order": "lexicographic-candidate-id",
                "not_claimed": ["semantic anonymity", "independent model identity", "randomized ordering"],
            },
            "candidate_view": _candidate_judge_view(candidates),
        }
        instructions = [
            "Review every candidate exactly once and every score dimension exactly once.",
            "The card deliberately omits generator provenance and sorts by candidate ID. This is provenance-blind, not semantic anonymity; do not infer or reward provider identity.",
            "Mark a candidate ineligible when it contradicts observed canon, rewrites exposed consequences or fair-play evidence, depends on unbounded coincidence, destroys character identity, or cannot fit the compression budget.",
            "weighted_score must equal the integer sum of dimension_score × policy.score_weights[dimension].",
            "Select the eligible candidate with the highest weighted score; break a tie by lexicographically smallest candidate_id.",
            "Do not change candidates, generate a new candidate, mutate the cube, or present a winner as canon.",
            "Return exactly one JSON object matching output_contract; no prose or code fence.",
        ]
        forbidden = ["generator provenance", "provider preference", "cube mutation", "player presentation"]
        output_template = {
            "schema": CHECKPOINT_JUDGMENT_SCHEMA,
            "task_id": "TASK_ID",
            "checkpoint_id": request["checkpoint_id"],
            "request_sha256": request_sha,
            "candidates_sha256": candidates_sha,
            "blind_review": True,
            "assessor": {
                "provider": "unknown",
                "model": "unknown",
                "model_version": None,
                "invocation_id": None,
                "notes": None,
            },
            "scores": [
                _judge_score_template(candidate["candidate_id"])
                for candidate in sorted(candidates["candidates"], key=lambda item: item["candidate_id"])
            ],
            "selected_candidate_id": candidates["candidates"][0]["candidate_id"],
            "selection_rule": CHECKPOINT_SELECTION_RULE,
            "selection_rationale": "Explain the rubric result without claiming objective quality.",
            "nonclaims": [
                "Scores are assessor judgments, not ledger truth.",
                "blind_review means generator provenance and generation notes were removed; it does not prove semantic anonymity or assessor independence.",
            ],
        }
        output_schema = CHECKPOINT_JUDGMENT_SCHEMA
        next_command = "./lacuna checkpoint card REQUEST.json --role lacuna-retcon-compressor --candidates CANDIDATES.json --judgment JUDGMENT.json > COMPRESSOR-CARD.json"
    elif role == "lacuna-retcon-compressor":
        if candidates_value is None or judgment_value is None or proposal_value is not None:
            _fail("missing-checkpoint-upstream", "compressor cards require candidates and judgment")
        candidates = validate_checkpoint_candidates(candidates_value, request)
        judgment = validate_checkpoint_judgment(judgment_value, request, candidates)
        candidates_sha = checkpoint_candidates_sha256(candidates, request)
        judgment_sha = checkpoint_judgment_sha256(judgment, request, candidates)
        upstream.extend(
            [
                _upstream("checkpoint-candidates", CHECKPOINT_CANDIDATES_SCHEMA, candidates_sha),
                _upstream("checkpoint-judgment", CHECKPOINT_JUDGMENT_SCHEMA, judgment_sha),
            ]
        )
        selected = _candidate_by_id(candidates, judgment["selected_candidate_id"])
        objective = "Compress the selected noncanon candidate into a bounded state card and a narrow hidden-state turn proposal body."
        input_payload = {
            "checkpoint_id": request["checkpoint_id"],
            "policy": request["policy"],
            "protected_state": request["protected_state"],
            "selected_candidate": selected,
            "judgment": judgment,
            "turn_identity_template": request["turn_packet"]["response_contract"]["proposal_template"],
            "allowed_operations": request["turn_packet"]["write_grant"]["allowed_operations"],
        }
        instructions = [
            "Compress only the selected candidate; do not silently blend rejected candidates.",
            "Keep state_card within policy.compression_max_chars and preserve every protected unknown ID exactly.",
            "Operations may affect hidden hypothesis custody only. Do not add sources; checkpoint assemble will prepend the exact selection-custody source.",
            "Do not publish assertions, close questions, change particle weights, select or prune worlds, raise commitments, or touch fair-play seal custody.",
            "New or revised world assignments must remain tentative or soft. Aesthetic scores are not evidence.",
            "Narration may continue play, but it must not expose the selected hidden hypothesis as an observed fact.",
            "Empty operations are valid when the useful output is only a bounded planning card.",
            "Return exactly one JSON object matching output_contract; no prose or code fence.",
        ]
        forbidden = ["add_source operation", "revealed assertions", "world selection", "particle reweighting", "hardening commitments", "seal openings"]
        output_template = {
            "schema": CHECKPOINT_COMPRESSION_SCHEMA,
            "task_id": "TASK_ID",
            "checkpoint_id": request["checkpoint_id"],
            "request_sha256": request_sha,
            "candidates_sha256": candidates_sha,
            "judgment_sha256": judgment_sha,
            "selected_candidate_id": judgment["selected_candidate_id"],
            "state_card": selected["hypothesis_card"],
            "retained_elements": [],
            "omitted_elements": [],
            "preserved_unknown_ids": list(request["protected_state"]["unknown_ids"]),
            "forbidden_contradictions": [],
            "next_pressures": [],
            "narration": "Continue with only what the player can experience now.",
            "operations": [],
            "message": "apply one reviewed retcon checkpoint",
            "nonclaims": ["The compressed state card remains a planning artifact until exact commit."],
        }
        output_schema = CHECKPOINT_COMPRESSION_SCHEMA
        next_command = "./lacuna checkpoint assemble REQUEST.json CANDIDATES.json JUDGMENT.json COMPRESSION.json > PROPOSAL.json"
    else:
        if proposal_value is None or candidates_value is not None or judgment_value is not None:
            _fail("missing-checkpoint-upstream", "verifier cards require one assembled proposal and no raw upstream arguments")
        proposal = validate_checkpoint_proposal(proposal_value, request_value=request)
        proposal_sha = checkpoint_proposal_sha256(proposal, request_value=request)
        upstream.append(_upstream("checkpoint-proposal", CHECKPOINT_PROPOSAL_SCHEMA, proposal_sha))
        objective = "Independently refuse or pass the assembled checkpoint proposal under the anti-rubber-reality contract."
        input_payload = {
            "checkpoint_request": request,
            "checkpoint_proposal": proposal,
            "mechanical_expectations": {
                "narrow_allowed_operations": sorted(CHECKPOINT_TURN_OPERATIONS),
                "all_unknown_ids": request["protected_state"]["unknown_ids"],
                "selection_rule": CHECKPOINT_SELECTION_RULE,
            },
        }
        instructions = [
            "Begin from refuse. Set pass only after every check is actually reviewed and true.",
            "Reject narration that tells the player hidden state merely because the selected candidate contains it.",
            "Reject evidential retcon, changed observed canon, erased exposed consequences, collapsed unknowns, or aesthetic scores used as world probability.",
            "Reject operations outside the source-backed checkpoint grant or any attempt to harden hidden assignments beyond soft.",
            "The exact custody source must bind request, candidates, judgment, protected state, selected candidate, and compressed state-card digests.",
            "Check only the proposal-visible selection-evidence consistency. The parent kernel, not this least-context verifier, revalidates the raw candidates, judgment, and deterministic winner before review and commit.",
            "Do not call review or commit. The parent performs mechanical kernel preparation after this advisory return.",
            "Return exactly one JSON object matching output_contract; no prose or code fence.",
        ]
        forbidden = ["cube mutation", "rewriting proposal", "claiming kernel acceptance", "player presentation"]
        output_template = {
            "schema": CHECKPOINT_VERIFIER_SCHEMA,
            "task_id": "TASK_ID",
            "checkpoint_id": request["checkpoint_id"],
            "request_sha256": request_sha,
            "proposal_sha256": proposal_sha,
            "status": "refuse",
            "checks": {check: False for check in CHECKPOINT_CHECKS},
            "findings": [
                {
                    "severity": "blocking",
                    "code": "unperformed-review",
                    "message": "Perform every check before changing status.",
                    "evidence_paths": [],
                }
            ],
            "recommended_action": "refuse",
            "nonclaims": ["A verifier pass is advisory and cannot commit the cube."],
        }
        output_schema = CHECKPOINT_VERIFIER_SCHEMA
        next_command = "./lacuna checkpoint review CUBE REQUEST.json CANDIDATES.json JUDGMENT.json PROPOSAL.json VERIFIER.json > REVIEW.json"

    task_id = _task_id(request_sha, role, upstream)
    output_template["task_id"] = task_id
    card = {
        "event": "lacuna.checkpoint.tasked",
        "schema": CHECKPOINT_TASK_CARD_SCHEMA,
        "role": role,
        "task_id": task_id,
        "checkpoint_id": request["checkpoint_id"],
        "request_sha256": request_sha,
        "upstream": upstream,
        "provider_aliases": provider_aliases(role),
        "objective": objective,
        "input_payload": input_payload,
        "instructions": instructions,
        "forbidden_context": forbidden,
        "output_contract": {
            "schema": output_schema,
            "format": "exact-json-object",
            "template": output_template,
        },
        "authority": {
            "worker_may": ["read this complete card", "return the exact contracted JSON object"],
            "worker_may_not": ["inspect unrelated files", "mutate the cube", "accept another worker output", "invoke checkpoint review or commit"],
            "parent_only": ["capture exact artifacts", "assemble proposal", "run kernel review", "commit", "present accepted narration"],
        },
        "next_command": next_command,
        "nonclaims": [
            "This card is a digest-bound least-context prompt artifact, not provider attestation or semantic proof.",
            "Provider aliases are routing metadata; the host must enforce any claimed context or tool isolation.",
        ],
    }
    return validate_checkpoint_task_card(card)


def validate_checkpoint_task_card(value: Any) -> dict[str, Any]:
    code = "bad-checkpoint-task-card"
    card = _strict(value, "checkpoint task card", CARD_FIELDS, code=code)
    if card.get("event") != "lacuna.checkpoint.tasked" or card.get("schema") != CHECKPOINT_TASK_CARD_SCHEMA:
        _fail(code, "checkpoint task card event or schema is invalid")
    role = card.get("role")
    if role not in CHECKPOINT_ROLES:
        _fail(code, f"role must be one of {list(CHECKPOINT_ROLES)}")
    try:
        require_id(card.get("task_id"), "task_id")
        require_id(card.get("checkpoint_id"), "checkpoint_id")
        require_string(card.get("objective"), "objective", max_len=10000)
        require_string(card.get("next_command"), "next_command", max_len=10000)
    except ValueError as exc:
        raise LacunaError(code, str(exc)) from exc
    request_sha = _sha(card.get("request_sha256"), "request_sha256", code=code)
    try:
        input_payload = require_mapping(card.get("input_payload"), "input_payload")
    except ValueError as exc:
        raise LacunaError(code, str(exc)) from exc
    _digest(input_payload, code=code, label="input_payload")

    try:
        upstream = require_list(card.get("upstream"), "upstream")
    except ValueError as exc:
        raise LacunaError(code, str(exc)) from exc
    normalized_upstream: list[dict[str, str]] = []
    for index, item in enumerate(upstream):
        entry = _strict(item, f"upstream[{index}]", {"kind", "schema", "sha256"}, code=code)
        for field in ("kind", "schema"):
            try:
                require_string(entry.get(field), f"upstream[{index}].{field}", max_len=256)
            except ValueError as exc:
                raise LacunaError(code, str(exc)) from exc
        normalized_upstream.append(
            {
                "kind": entry["kind"],
                "schema": entry["schema"],
                "sha256": _sha(entry.get("sha256"), f"upstream[{index}].sha256", code=code),
            }
        )
    expected_upstream = CHECKPOINT_ROLE_UPSTREAM[role]
    actual_upstream = tuple((item["kind"], item["schema"]) for item in normalized_upstream)
    if actual_upstream != expected_upstream:
        _fail(
            code,
            "upstream artifact kinds or order do not match the role contract",
            {"role": role, "expected": [list(item) for item in expected_upstream], "actual": [list(item) for item in actual_upstream]},
        )
    expected_task_id = _task_id(request_sha, role, normalized_upstream)
    if card.get("task_id") != expected_task_id:
        _fail(
            code,
            "task_id is not the deterministic digest-bound identity for this request, role, and upstream chain",
            {"expected": expected_task_id, "actual": card.get("task_id")},
        )
    if card.get("provider_aliases") != provider_aliases(role):
        _fail(code, "provider_aliases do not match the central provider registry")
    _string_list(card.get("instructions"), "instructions", code=code, max_items=50, max_len=10000)
    _string_list(card.get("forbidden_context"), "forbidden_context", code=code, max_items=50, max_len=10000)
    output_contract = _strict(card.get("output_contract"), "output_contract", {"schema", "format", "template"}, code=code)
    expected_output_schema = CHECKPOINT_ROLE_OUTPUT_SCHEMAS[role]
    if output_contract.get("schema") != expected_output_schema:
        _fail(code, "output_contract.schema does not match the role contract", {"expected": expected_output_schema, "actual": output_contract.get("schema")})
    if output_contract.get("format") != "exact-json-object":
        _fail(code, "output_contract.format must be exact-json-object")
    try:
        template = require_mapping(output_contract.get("template"), "output_contract.template")
    except ValueError as exc:
        raise LacunaError(code, str(exc)) from exc
    template_bindings = {
        "schema": expected_output_schema,
        "task_id": card["task_id"],
        "checkpoint_id": card["checkpoint_id"],
        "request_sha256": request_sha,
    }
    mismatches = {
        field: {"expected": expected, "actual": template.get(field)}
        for field, expected in template_bindings.items()
        if template.get(field) != expected
    }
    if mismatches:
        _fail(code, "output_contract.template is not bound to this exact task card", {"mismatches": mismatches})
    _digest(template, code=code, label="output_contract.template")

    authority = _strict(card.get("authority"), "authority", {"worker_may", "worker_may_not", "parent_only"}, code=code)
    for field in ("worker_may", "worker_may_not", "parent_only"):
        values = _string_list(authority.get(field), f"authority.{field}", code=code, max_items=30, max_len=10000, unique=True)
        if not values:
            _fail(code, f"authority.{field} must not be empty")
    _string_list(card.get("nonclaims"), "nonclaims", code=code, max_items=20, max_len=10000)
    _digest(card, code=code, label="checkpoint task card")
    return copy.deepcopy(card)


def checkpoint_task_card_sha256(value: Any) -> str:
    return _digest(validate_checkpoint_task_card(value), code="bad-checkpoint-task-card", label="checkpoint task card")


def validate_checkpoint_candidates(value: Any, request_value: Any) -> dict[str, Any]:
    code = "bad-checkpoint-candidates"
    request = validate_checkpoint_request(request_value)
    document = _strict(value, "checkpoint candidates", CANDIDATES_FIELDS, code=code)
    if document.get("schema") != CHECKPOINT_CANDIDATES_SCHEMA:
        _fail(code, "checkpoint candidates schema is invalid")
    request_sha = _digest(request, code=code, label="checkpoint request")
    expected = {
        "task_id": _task_id(request_sha, "lacuna-retcon-generator", []),
        "checkpoint_id": request["checkpoint_id"],
        "request_sha256": request_sha,
    }
    mismatches = {field: {"expected": expected_value, "actual": document.get(field)} for field, expected_value in expected.items() if document.get(field) != expected_value}
    if mismatches:
        _fail(code, "checkpoint candidates do not bind the generator card", {"mismatches": mismatches})
    candidates_raw = require_list(document.get("candidates"), "candidates")
    if len(candidates_raw) != request["policy"]["candidate_count"]:
        _fail(code, "candidate count does not match checkpoint policy", {"expected": request["policy"]["candidate_count"], "actual": len(candidates_raw)})
    expected_unknowns = request["protected_state"]["unknown_ids"]
    candidates: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, raw in enumerate(candidates_raw):
        field = f"candidates[{index}]"
        item = _strict(raw, field, CANDIDATE_FIELDS, code=code)
        try:
            candidate_id = require_id(item.get("candidate_id"), f"{field}.candidate_id")
            title = require_string(item.get("title"), f"{field}.title", max_len=512)
            hypothesis_card = require_string(item.get("hypothesis_card"), f"{field}.hypothesis_card", max_len=20000)
            explanation = require_string(item.get("story_so_far_explanation"), f"{field}.story_so_far_explanation", max_len=20000)
            future = require_string(item.get("future_arc_summary"), f"{field}.future_arc_summary", max_len=20000)
        except ValueError as exc:
            raise LacunaError(code, str(exc)) from exc
        if candidate_id in seen:
            _fail(code, "candidate IDs must be unique", {"candidate_id": candidate_id})
        seen.add(candidate_id)
        preserved = _string_list(item.get("preserved_unknown_ids"), f"{field}.preserved_unknown_ids", code=code, max_items=1000, max_len=256, unique=True)
        if preserved != expected_unknowns:
            _fail(code, "each candidate must preserve the exact ordered existing unknown set", {"candidate_id": candidate_id, "expected": expected_unknowns, "actual": preserved})
        rollout = _strict(item.get("rollout"), f"{field}.rollout", ROLLOUT_FIELDS, code=code)
        horizon = _integer(rollout.get("horizon_turns"), f"{field}.rollout.horizon_turns", minimum=1, maximum=20, code=code)
        if horizon != request["policy"]["rollout_horizon_turns"]:
            _fail(code, "rollout horizon does not match checkpoint policy", {"candidate_id": candidate_id})
        rollout_turns = _string_list(
            rollout.get("turns"),
            f"{field}.rollout.turns",
            code=code,
            max_items=20,
            max_len=10000,
        )
        if len(rollout_turns) != horizon:
            _fail(
                code,
                "rollout must contain exactly one ordered beat per horizon turn",
                {"candidate_id": candidate_id, "expected": horizon, "actual": len(rollout_turns)},
            )
        try:
            rollout_summary = require_string(rollout.get("summary"), f"{field}.rollout.summary", max_len=20000)
        except ValueError as exc:
            raise LacunaError(code, str(exc)) from exc
        candidates.append(
            {
                "candidate_id": candidate_id,
                "title": title,
                "hypothesis_card": hypothesis_card,
                "story_so_far_explanation": explanation,
                "future_arc_summary": future,
                "preserved_unknown_ids": preserved,
                "promoted_incidental_details": _string_list(item.get("promoted_incidental_details"), f"{field}.promoted_incidental_details", code=code, max_items=100, max_len=5000, unique=True),
                "commitment_risks": _string_list(item.get("commitment_risks"), f"{field}.commitment_risks", code=code, max_items=100, max_len=5000),
                "fair_play_risks": _string_list(item.get("fair_play_risks"), f"{field}.fair_play_risks", code=code, max_items=100, max_len=5000),
                "identity_drift_risks": _string_list(item.get("identity_drift_risks"), f"{field}.identity_drift_risks", code=code, max_items=100, max_len=5000),
                "rollout": {
                    "horizon_turns": horizon,
                    "turns": rollout_turns,
                    "summary": rollout_summary,
                },
                "provenance": _provenance(item.get("provenance"), f"{field}.provenance", code=code),
            }
        )
    generation_notes = _optional_string(document.get("generation_notes"), "generation_notes", code=code, max_len=20000)
    nonclaims = _string_list(document.get("nonclaims"), "nonclaims", code=code, max_items=20, max_len=10000)
    result = {
        "schema": CHECKPOINT_CANDIDATES_SCHEMA,
        "task_id": document["task_id"],
        "checkpoint_id": document["checkpoint_id"],
        "request_sha256": document["request_sha256"],
        "candidates": candidates,
        "generation_notes": generation_notes,
        "nonclaims": nonclaims,
    }
    _digest(result, code=code, label="checkpoint candidates")
    return result


def checkpoint_candidates_sha256(value: Any, request_value: Any) -> str:
    return _digest(validate_checkpoint_candidates(value, request_value), code="bad-checkpoint-candidates", label="checkpoint candidates")


def _weighted_score(dimensions: dict[str, int], weights: dict[str, int]) -> int:
    return sum(dimensions[dimension] * weights[dimension] for dimension in CHECKPOINT_SCORE_DIMENSIONS)


def validate_checkpoint_judgment(value: Any, request_value: Any, candidates_value: Any) -> dict[str, Any]:
    code = "bad-checkpoint-judgment"
    request = validate_checkpoint_request(request_value)
    candidates = validate_checkpoint_candidates(candidates_value, request)
    document = _strict(value, "checkpoint judgment", JUDGMENT_FIELDS, code=code)
    if document.get("schema") != CHECKPOINT_JUDGMENT_SCHEMA:
        _fail(code, "checkpoint judgment schema is invalid")
    request_sha = _digest(request, code=code, label="checkpoint request")
    candidates_sha = _digest(candidates, code=code, label="checkpoint candidates")
    judge_upstream = [_upstream("checkpoint-candidates", CHECKPOINT_CANDIDATES_SCHEMA, candidates_sha)]
    expected = {
        "task_id": _task_id(request_sha, "lacuna-retcon-judge", judge_upstream),
        "checkpoint_id": request["checkpoint_id"],
        "request_sha256": request_sha,
        "candidates_sha256": candidates_sha,
        "blind_review": True,
        "selection_rule": CHECKPOINT_SELECTION_RULE,
    }
    mismatches = {field: {"expected": expected_value, "actual": document.get(field)} for field, expected_value in expected.items() if document.get(field) != expected_value}
    if mismatches:
        _fail(code, "checkpoint judgment does not bind the judge card", {"mismatches": mismatches})
    candidate_ids = [item["candidate_id"] for item in candidates["candidates"]]
    scores_raw = require_list(document.get("scores"), "scores")
    if len(scores_raw) != len(candidate_ids):
        _fail(code, "judgment must score every candidate exactly once")
    scores: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, raw in enumerate(scores_raw):
        field = f"scores[{index}]"
        item = _strict(raw, field, SCORE_FIELDS, code=code)
        try:
            candidate_id = require_id(item.get("candidate_id"), f"{field}.candidate_id")
            rationale = require_string(item.get("rationale"), f"{field}.rationale", max_len=10000)
        except ValueError as exc:
            raise LacunaError(code, str(exc)) from exc
        if candidate_id not in candidate_ids or candidate_id in seen:
            _fail(code, "scores must name each candidate exactly once", {"candidate_id": candidate_id})
        seen.add(candidate_id)
        if not isinstance(item.get("eligible"), bool):
            _fail(code, f"{field}.eligible must be boolean")
        disqualifiers = _string_list(item.get("disqualifiers"), f"{field}.disqualifiers", code=code, max_items=20, max_len=128, unique=True)
        unknown_disqualifiers = sorted(set(disqualifiers) - CHECKPOINT_DISQUALIFIERS)
        if unknown_disqualifiers:
            _fail(code, "judgment contains unsupported disqualifiers", {"values": unknown_disqualifiers})
        if item["eligible"] and disqualifiers:
            _fail(code, "an eligible candidate cannot carry disqualifiers", {"candidate_id": candidate_id})
        if not item["eligible"] and not disqualifiers:
            _fail(code, "an ineligible candidate must state at least one disqualifier", {"candidate_id": candidate_id})
        dimensions_raw = _strict(item.get("dimensions"), f"{field}.dimensions", set(CHECKPOINT_SCORE_DIMENSIONS), code=code)
        dimensions = {
            dimension: _integer(dimensions_raw.get(dimension), f"{field}.dimensions.{dimension}", minimum=0, maximum=100, code=code)
            for dimension in CHECKPOINT_SCORE_DIMENSIONS
        }
        expected_weighted = _weighted_score(dimensions, request["policy"]["score_weights"])
        actual_weighted = _integer(item.get("weighted_score"), f"{field}.weighted_score", minimum=0, maximum=10000, code=code)
        if actual_weighted != expected_weighted:
            _fail(code, "weighted_score does not match the declared integer rubric", {"candidate_id": candidate_id, "expected": expected_weighted, "actual": actual_weighted})
        scores.append(
            {
                "candidate_id": candidate_id,
                "eligible": item["eligible"],
                "disqualifiers": disqualifiers,
                "dimensions": dimensions,
                "weighted_score": actual_weighted,
                "rationale": rationale,
            }
        )
    selected = document.get("selected_candidate_id")
    try:
        selected = require_id(selected, "selected_candidate_id")
    except ValueError as exc:
        raise LacunaError(code, str(exc)) from exc
    eligible_scores = [item for item in scores if item["eligible"]]
    if not eligible_scores:
        _fail(code, "judgment has no eligible candidate; regenerate or revise candidates instead of selecting a refused one")
    expected_selected = min(
        (item for item in eligible_scores if item["weighted_score"] == max(score["weighted_score"] for score in eligible_scores)),
        key=lambda item: item["candidate_id"],
    )["candidate_id"]
    if selected != expected_selected:
        _fail(code, "selected_candidate_id does not follow the declared deterministic rule", {"expected": expected_selected, "actual": selected})
    try:
        selection_rationale = require_string(document.get("selection_rationale"), "selection_rationale", max_len=20000)
    except ValueError as exc:
        raise LacunaError(code, str(exc)) from exc
    result = {
        "schema": CHECKPOINT_JUDGMENT_SCHEMA,
        "task_id": document["task_id"],
        "checkpoint_id": document["checkpoint_id"],
        "request_sha256": document["request_sha256"],
        "candidates_sha256": document["candidates_sha256"],
        "blind_review": True,
        "assessor": _provenance(document.get("assessor"), "assessor", code=code),
        "scores": scores,
        "selected_candidate_id": selected,
        "selection_rule": CHECKPOINT_SELECTION_RULE,
        "selection_rationale": selection_rationale,
        "nonclaims": _string_list(document.get("nonclaims"), "nonclaims", code=code, max_items=20, max_len=10000),
    }
    _digest(result, code=code, label="checkpoint judgment")
    return result


def checkpoint_judgment_sha256(value: Any, request_value: Any, candidates_value: Any) -> str:
    return _digest(
        validate_checkpoint_judgment(value, request_value, candidates_value),
        code="bad-checkpoint-judgment",
        label="checkpoint judgment",
    )


def _checkpoint_operation_rules(operations: list[Any], *, max_operations: int, code: str) -> list[dict[str, Any]]:
    if len(operations) > max_operations:
        _fail(code, "compression operations exceed checkpoint policy", {"max_operations": max_operations, "actual": len(operations)})
    result: list[dict[str, Any]] = []
    for index, raw in enumerate(operations):
        try:
            operation = require_mapping(raw, f"operations[{index}]")
        except ValueError as exc:
            raise LacunaError(code, str(exc)) from exc
        op = operation.get("op")
        if op not in CHECKPOINT_TURN_OPERATIONS - {"add_source"}:
            _fail(code, "compressor operations must remain inside the non-source checkpoint surface", {"operation_index": index, "op": op})
        if operation.get("as") == "checkpoint_selection":
            _fail(code, "alias checkpoint_selection is reserved for the assembled custody source", {"operation_index": index})
        if op in {"assign_world", "revise_world"}:
            commitment = operation.get("commitment", "tentative")
            if commitment not in {"tentative", "soft"}:
                _fail(code, "checkpoint assignments cannot harden beyond soft", {"operation_index": index, "commitment": commitment})
        if op == "create_world":
            status = operation.get("status", "live")
            weight = operation.get("weight", 1.0)
            if status != "live" or isinstance(weight, bool) or weight not in {1, 1.0}:
                _fail(code, "checkpoint-created worlds must begin live with neutral weight 1", {"operation_index": index})
        result.append(copy.deepcopy(operation))
    return result


def validate_checkpoint_compression(
    value: Any,
    request_value: Any,
    candidates_value: Any,
    judgment_value: Any,
) -> dict[str, Any]:
    code = "bad-checkpoint-compression"
    request = validate_checkpoint_request(request_value)
    candidates = validate_checkpoint_candidates(candidates_value, request)
    judgment = validate_checkpoint_judgment(judgment_value, request, candidates)
    document = _strict(value, "checkpoint compression", COMPRESSION_FIELDS, code=code)
    if document.get("schema") != CHECKPOINT_COMPRESSION_SCHEMA:
        _fail(code, "checkpoint compression schema is invalid")
    request_sha = _digest(request, code=code, label="checkpoint request")
    candidates_sha = _digest(candidates, code=code, label="checkpoint candidates")
    judgment_sha = _digest(judgment, code=code, label="checkpoint judgment")
    compressor_upstream = [
        _upstream("checkpoint-candidates", CHECKPOINT_CANDIDATES_SCHEMA, candidates_sha),
        _upstream("checkpoint-judgment", CHECKPOINT_JUDGMENT_SCHEMA, judgment_sha),
    ]
    expected = {
        "task_id": _task_id(request_sha, "lacuna-retcon-compressor", compressor_upstream),
        "checkpoint_id": request["checkpoint_id"],
        "request_sha256": request_sha,
        "candidates_sha256": candidates_sha,
        "judgment_sha256": judgment_sha,
        "selected_candidate_id": judgment["selected_candidate_id"],
    }
    mismatches = {field: {"expected": expected_value, "actual": document.get(field)} for field, expected_value in expected.items() if document.get(field) != expected_value}
    if mismatches:
        _fail(code, "checkpoint compression does not bind the selected candidate walk", {"mismatches": mismatches})
    try:
        state_card = require_string(document.get("state_card"), "state_card", max_len=20000)
        narration = require_string(document.get("narration"), "narration", max_len=50000)
        message = require_string(document.get("message"), "message", allow_empty=True, max_len=4096)
    except ValueError as exc:
        raise LacunaError(code, str(exc)) from exc
    if len(state_card) > request["policy"]["compression_max_chars"]:
        _fail(code, "state_card exceeds the checkpoint compression budget", {"max_chars": request["policy"]["compression_max_chars"], "actual_chars": len(state_card)})
    if narration == TURN_NARRATION_PLACEHOLDER:
        _fail(code, "compression narration retains the fail-closed placeholder")
    preserved = _string_list(document.get("preserved_unknown_ids"), "preserved_unknown_ids", code=code, max_items=1000, max_len=256, unique=True)
    if preserved != request["protected_state"]["unknown_ids"]:
        _fail(code, "compression must preserve the exact ordered existing unknown set", {"expected": request["protected_state"]["unknown_ids"], "actual": preserved})
    operations_raw = require_list(document.get("operations"), "operations")
    operations = _checkpoint_operation_rules(operations_raw, max_operations=request["policy"]["max_operations"], code=code)
    # Reuse the ordinary packet preflight on a temporary body before assembly.
    template = copy.deepcopy(request["turn_packet"]["response_contract"]["proposal_template"])
    template.update(
        {
            "narration": narration,
            "revealed_assertion_ids": [],
            "operations": operations,
            "message": message,
        }
    )
    validate_proposal_binding(template, request["turn_packet"])
    result = {
        "schema": CHECKPOINT_COMPRESSION_SCHEMA,
        "task_id": document["task_id"],
        "checkpoint_id": document["checkpoint_id"],
        "request_sha256": document["request_sha256"],
        "candidates_sha256": document["candidates_sha256"],
        "judgment_sha256": document["judgment_sha256"],
        "selected_candidate_id": document["selected_candidate_id"],
        "state_card": state_card,
        "retained_elements": _string_list(document.get("retained_elements"), "retained_elements", code=code, max_items=500, max_len=5000),
        "omitted_elements": _string_list(document.get("omitted_elements"), "omitted_elements", code=code, max_items=500, max_len=5000),
        "preserved_unknown_ids": preserved,
        "forbidden_contradictions": _string_list(document.get("forbidden_contradictions"), "forbidden_contradictions", code=code, max_items=500, max_len=5000),
        "next_pressures": _string_list(document.get("next_pressures"), "next_pressures", code=code, max_items=500, max_len=5000),
        "narration": narration,
        "operations": operations,
        "message": message,
        "nonclaims": _string_list(document.get("nonclaims"), "nonclaims", code=code, max_items=20, max_len=10000),
    }
    _digest(result, code=code, label="checkpoint compression")
    return result


def checkpoint_compression_sha256(value: Any, request_value: Any, candidates_value: Any, judgment_value: Any) -> str:
    return _digest(
        validate_checkpoint_compression(value, request_value, candidates_value, judgment_value),
        code="bad-checkpoint-compression",
        label="checkpoint compression",
    )


def _candidate_by_id(candidates: dict[str, Any], candidate_id: str) -> dict[str, Any]:
    for candidate in candidates["candidates"]:
        if candidate["candidate_id"] == candidate_id:
            return candidate
    _fail(
        "bad-checkpoint-selection",
        "selected candidate is absent from the validated candidate artifact",
        {"selected_candidate_id": candidate_id},
    )
    raise AssertionError("unreachable")


def _selection_evidence(
    request: dict[str, Any],
    candidates: dict[str, Any],
    judgment: dict[str, Any],
    compression: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema": "lacuna.checkpoint-selection-evidence.v1",
        "checkpoint_id": request["checkpoint_id"],
        "request_sha256": checkpoint_request_sha256(request),
        "candidates_sha256": checkpoint_candidates_sha256(candidates, request),
        "judgment_sha256": checkpoint_judgment_sha256(judgment, request, candidates),
        "selected_candidate_id": judgment["selected_candidate_id"],
        "selected_candidate_sha256": _digest(
            _candidate_by_id(candidates, judgment["selected_candidate_id"]),
            code="bad-checkpoint-selection",
            label="selected checkpoint candidate",
        ),
        "protected_state_sha256": request["protected_state_sha256"],
        "state_card_sha256": sha256_text(compression["state_card"]),
    }


def _custody_source_operation(request: dict[str, Any], evidence: dict[str, Any], evidence_sha: str) -> dict[str, Any]:
    checkpoint_id = request["checkpoint_id"]
    return {
        "op": "add_source",
        "source_id": None,
        "kind": "tool",
        "label": f"Retcon checkpoint selection {checkpoint_id}",
        "locator": f"lacuna:checkpoint:{checkpoint_id}:selection",
        "content_sha256": evidence_sha,
        "metadata": {
            "protocol": "lacuna.checkpoint-selection.v1",
            "checkpoint_id": checkpoint_id,
            "request_sha256": evidence["request_sha256"],
            "candidates_sha256": evidence["candidates_sha256"],
            "judgment_sha256": evidence["judgment_sha256"],
            "selected_candidate_id": evidence["selected_candidate_id"],
            "selected_candidate_sha256": evidence["selected_candidate_sha256"],
            "protected_state_sha256": evidence["protected_state_sha256"],
            "state_card_sha256": evidence["state_card_sha256"],
            "candidate_rollouts_noncanon": True,
            "score_provenance_unattested": True,
        },
        "as": "checkpoint_selection",
    }


def assemble_checkpoint_proposal(
    request_value: Any,
    candidates_value: Any,
    judgment_value: Any,
    compression_value: Any,
) -> dict[str, Any]:
    request = validate_checkpoint_request(request_value)
    candidates = validate_checkpoint_candidates(candidates_value, request)
    judgment = validate_checkpoint_judgment(judgment_value, request, candidates)
    compression = validate_checkpoint_compression(compression_value, request, candidates, judgment)
    evidence = _selection_evidence(request, candidates, judgment, compression)
    evidence_sha = _digest(evidence, code="bad-checkpoint-proposal", label="selection evidence")
    turn_proposal = copy.deepcopy(request["turn_packet"]["response_contract"]["proposal_template"])
    turn_proposal.update(
        {
            "narration": compression["narration"],
            "revealed_assertion_ids": [],
            "operations": [
                _custody_source_operation(request, evidence, evidence_sha),
                *copy.deepcopy(compression["operations"]),
            ],
            "message": compression["message"],
        }
    )
    validate_proposal_binding(turn_proposal, request["turn_packet"])
    proposal = {
        "event": "lacuna.checkpoint.proposed",
        "schema": CHECKPOINT_PROPOSAL_SCHEMA,
        "checkpoint_id": request["checkpoint_id"],
        "request_sha256": checkpoint_request_sha256(request),
        "candidates_sha256": checkpoint_candidates_sha256(candidates, request),
        "judgment_sha256": checkpoint_judgment_sha256(judgment, request, candidates),
        "compression_sha256": checkpoint_compression_sha256(compression, request, candidates, judgment),
        "selected_candidate_id": judgment["selected_candidate_id"],
        "compression_artifact": copy.deepcopy(compression),
        "compression": {
            "budget_chars": request["policy"]["compression_max_chars"],
            "char_count": len(compression["state_card"]),
            "state_card": compression["state_card"],
            "state_card_sha256": evidence["state_card_sha256"],
            "retained_elements": compression["retained_elements"],
            "omitted_elements": compression["omitted_elements"],
            "preserved_unknown_ids": compression["preserved_unknown_ids"],
            "forbidden_contradictions": compression["forbidden_contradictions"],
            "next_pressures": compression["next_pressures"],
        },
        "selection_evidence": evidence,
        "selection_evidence_sha256": evidence_sha,
        "turn_proposal": turn_proposal,
        "nonclaims": [
            "The selected candidate, state card, score, and rollout remain noncanon planning custody.",
            "Assembly computes digests and binds the narrow source-backed turn; it does not run the kernel or commit.",
            "The selection-custody source proves exact artifact identity only, not model identity, evaluator validity, or narrative quality.",
        ],
    }
    return validate_checkpoint_proposal(
        proposal,
        request_value=request,
        candidates_value=candidates,
        judgment_value=judgment,
        compression_value=compression,
    )


def validate_checkpoint_proposal(
    value: Any,
    *,
    request_value: Any,
    candidates_value: Any | None = None,
    judgment_value: Any | None = None,
    compression_value: Any | None = None,
) -> dict[str, Any]:
    code = "bad-checkpoint-proposal"
    request = validate_checkpoint_request(request_value)
    proposal = _strict(value, "checkpoint proposal", PROPOSAL_FIELDS, code=code)
    if proposal.get("event") != "lacuna.checkpoint.proposed" or proposal.get("schema") != CHECKPOINT_PROPOSAL_SCHEMA:
        _fail(code, "checkpoint proposal event or schema is invalid")
    try:
        require_id(proposal.get("checkpoint_id"), "checkpoint_id")
        require_id(proposal.get("selected_candidate_id"), "selected_candidate_id")
    except ValueError as exc:
        raise LacunaError(code, str(exc)) from exc
    for field in (
        "request_sha256",
        "candidates_sha256",
        "judgment_sha256",
        "compression_sha256",
        "selection_evidence_sha256",
    ):
        _sha(proposal.get(field), field, code=code)
    if proposal["checkpoint_id"] != request["checkpoint_id"] or proposal["request_sha256"] != checkpoint_request_sha256(request):
        _fail(code, "checkpoint proposal does not bind its request")

    candidates = validate_checkpoint_candidates(candidates_value, request) if candidates_value is not None else None
    judgment = (
        validate_checkpoint_judgment(judgment_value, request, candidates)
        if judgment_value is not None and candidates is not None
        else None
    )
    if any(item is not None for item in (candidates_value, judgment_value)) and not all(
        item is not None for item in (candidates_value, judgment_value)
    ):
        _fail(code, "proposal validation requires candidates and judgment together")
    embedded_compression = proposal.get("compression_artifact")
    if compression_value is not None and candidates is None:
        _fail(code, "external compression validation requires candidates and judgment")
    compression_source = compression_value if compression_value is not None else embedded_compression
    compression = (
        validate_checkpoint_compression(compression_source, request, candidates, judgment)
        if candidates is not None and judgment is not None
        else None
    )
    if compression is None:
        if not isinstance(embedded_compression, dict):
            _fail(code, "checkpoint proposal must retain its exact compression artifact")
        if proposal.get("compression_sha256") != _digest(
            embedded_compression,
            code=code,
            label="embedded checkpoint compression",
        ):
            _fail(code, "embedded compression artifact does not match compression_sha256")
    else:
        if embedded_compression != compression:
            _fail(code, "embedded compression artifact is not the exact validated compressor return")
    if candidates is not None and judgment is not None and compression is not None:
        expected_digests = {
            "candidates_sha256": checkpoint_candidates_sha256(candidates, request),
            "judgment_sha256": checkpoint_judgment_sha256(judgment, request, candidates),
            "compression_sha256": checkpoint_compression_sha256(compression, request, candidates, judgment),
            "selected_candidate_id": judgment["selected_candidate_id"],
        }
        mismatches = {field: {"expected": expected, "actual": proposal.get(field)} for field, expected in expected_digests.items() if proposal.get(field) != expected}
        if mismatches:
            _fail(code, "checkpoint proposal upstream digests disagree", {"mismatches": mismatches})
        expected_evidence = _selection_evidence(request, candidates, judgment, compression)
    else:
        expected_evidence = proposal.get("selection_evidence")

    evidence = _strict(
        proposal.get("selection_evidence"),
        "selection_evidence",
        {
            "schema",
            "checkpoint_id",
            "request_sha256",
            "candidates_sha256",
            "judgment_sha256",
            "selected_candidate_id",
            "selected_candidate_sha256",
            "protected_state_sha256",
            "state_card_sha256",
        },
        code=code,
    )
    if evidence != expected_evidence:
        _fail(code, "selection_evidence is not the exact artifact binding")
    evidence_sha = _digest(evidence, code=code, label="selection evidence")
    if evidence_sha != proposal["selection_evidence_sha256"]:
        _fail(code, "selection_evidence_sha256 does not match selection_evidence")

    compression_block = _strict(
        proposal.get("compression"),
        "compression",
        {
            "budget_chars",
            "char_count",
            "state_card",
            "state_card_sha256",
            "retained_elements",
            "omitted_elements",
            "preserved_unknown_ids",
            "forbidden_contradictions",
            "next_pressures",
        },
        code=code,
    )
    try:
        state_card = require_string(compression_block.get("state_card"), "compression.state_card", max_len=20000)
    except ValueError as exc:
        raise LacunaError(code, str(exc)) from exc
    if compression_block.get("budget_chars") != request["policy"]["compression_max_chars"] or compression_block.get("char_count") != len(state_card):
        _fail(code, "compression budget or char_count is inconsistent")
    if len(state_card) > request["policy"]["compression_max_chars"]:
        _fail(code, "compressed state card exceeds its budget")
    state_sha = sha256_text(state_card)
    if compression_block.get("state_card_sha256") != state_sha or evidence.get("state_card_sha256") != state_sha:
        _fail(code, "state-card digest binding is inconsistent")
    preserved = _string_list(compression_block.get("preserved_unknown_ids"), "compression.preserved_unknown_ids", code=code, max_items=1000, max_len=256, unique=True)
    if preserved != request["protected_state"]["unknown_ids"]:
        _fail(code, "assembled proposal does not preserve the exact unknown set")
    for field in ("retained_elements", "omitted_elements", "forbidden_contradictions", "next_pressures"):
        _string_list(compression_block.get(field), f"compression.{field}", code=code, max_items=500, max_len=5000)

    turn_proposal = validate_proposal_binding(proposal.get("turn_proposal"), request["turn_packet"])
    if turn_proposal.get("revealed_assertion_ids") != []:
        _fail(code, "checkpoint turn proposals cannot reveal assertions")
    operations = turn_proposal["operations"]
    if not operations:
        _fail(code, "checkpoint turn proposal is missing its selection-custody source")
    expected_source = _custody_source_operation(request, evidence, evidence_sha)
    if operations[0] != expected_source:
        _fail(code, "first operation is not the exact selection-custody source")
    _checkpoint_operation_rules(
        operations[1:],
        max_operations=request["policy"]["max_operations"],
        code=code,
    )
    _string_list(proposal.get("nonclaims"), "nonclaims", code=code, max_items=20, max_len=10000)
    result = copy.deepcopy(proposal)
    result["turn_proposal"] = turn_proposal
    _digest(result, code=code, label="checkpoint proposal")
    return result


def checkpoint_proposal_sha256(value: Any, *, request_value: Any) -> str:
    return _digest(
        validate_checkpoint_proposal(value, request_value=request_value),
        code="bad-checkpoint-proposal",
        label="checkpoint proposal",
    )


def validate_checkpoint_verifier(value: Any, request_value: Any, proposal_value: Any) -> dict[str, Any]:
    code = "bad-checkpoint-verifier"
    request = validate_checkpoint_request(request_value)
    proposal = validate_checkpoint_proposal(proposal_value, request_value=request)
    document = _strict(value, "checkpoint verifier return", VERIFIER_FIELDS, code=code)
    if document.get("schema") != CHECKPOINT_VERIFIER_SCHEMA:
        _fail(code, "checkpoint verifier schema is invalid")
    request_sha = _digest(request, code=code, label="checkpoint request")
    proposal_sha = _digest(proposal, code=code, label="checkpoint proposal")
    verifier_upstream = [_upstream("checkpoint-proposal", CHECKPOINT_PROPOSAL_SCHEMA, proposal_sha)]
    expected = {
        "task_id": _task_id(request_sha, "lacuna-retcon-verifier", verifier_upstream),
        "checkpoint_id": request["checkpoint_id"],
        "request_sha256": request_sha,
        "proposal_sha256": proposal_sha,
    }
    mismatches = {field: {"expected": expected_value, "actual": document.get(field)} for field, expected_value in expected.items() if document.get(field) != expected_value}
    if mismatches:
        _fail(code, "checkpoint verifier return does not bind its card", {"mismatches": mismatches})
    status = document.get("status")
    if status not in {"pass", "refuse"}:
        _fail(code, "verifier status must be pass or refuse")
    checks = _strict(document.get("checks"), "checks", set(CHECKPOINT_CHECKS), code=code)
    if any(not isinstance(checks.get(check), bool) for check in CHECKPOINT_CHECKS):
        _fail(code, "every verifier check must be boolean")
    findings_raw = require_list(document.get("findings"), "findings")
    findings: list[dict[str, Any]] = []
    for index, raw in enumerate(findings_raw):
        field = f"findings[{index}]"
        finding = _strict(raw, field, FINDING_FIELDS, code=code)
        severity = finding.get("severity")
        if severity not in {"info", "warning", "blocking"}:
            _fail(code, f"{field}.severity is invalid")
        try:
            finding_code = require_string(finding.get("code"), f"{field}.code", max_len=128)
            message = require_string(finding.get("message"), f"{field}.message", max_len=10000)
        except ValueError as exc:
            raise LacunaError(code, str(exc)) from exc
        findings.append(
            {
                "severity": severity,
                "code": finding_code,
                "message": message,
                "evidence_paths": _string_list(finding.get("evidence_paths"), f"{field}.evidence_paths", code=code, max_items=100, max_len=1000, unique=True),
            }
        )
    recommended = document.get("recommended_action")
    if recommended not in {"commit", "refuse", "regenerate"}:
        _fail(code, "recommended_action is invalid")
    blocking = any(item["severity"] == "blocking" for item in findings)
    if status == "pass":
        if not all(checks.values()) or blocking or recommended != "commit":
            _fail(code, "verifier pass requires every check true, no blocking finding, and recommended_action commit")
    else:
        if recommended == "commit":
            _fail(code, "verifier refusal cannot recommend commit")
    result = {
        "schema": CHECKPOINT_VERIFIER_SCHEMA,
        "task_id": document["task_id"],
        "checkpoint_id": document["checkpoint_id"],
        "request_sha256": document["request_sha256"],
        "proposal_sha256": document["proposal_sha256"],
        "status": status,
        "checks": {check: checks[check] for check in CHECKPOINT_CHECKS},
        "findings": findings,
        "recommended_action": recommended,
        "nonclaims": _string_list(document.get("nonclaims"), "nonclaims", code=code, max_items=20, max_len=10000),
    }
    _digest(result, code=code, label="checkpoint verifier return")
    return result


def checkpoint_verifier_sha256(value: Any, request_value: Any, proposal_value: Any) -> str:
    return _digest(
        validate_checkpoint_verifier(value, request_value, proposal_value),
        code="bad-checkpoint-verifier",
        label="checkpoint verifier return",
    )


def review_checkpoint(
    cube: Cube,
    request_value: Any,
    candidates_value: Any,
    judgment_value: Any,
    proposal_value: Any,
    verifier_value: Any,
) -> dict[str, Any]:
    request = validate_checkpoint_request(request_value)
    candidates = validate_checkpoint_candidates(candidates_value, request)
    judgment = validate_checkpoint_judgment(judgment_value, request, candidates)
    proposal = validate_checkpoint_proposal(
        proposal_value,
        request_value=request,
        candidates_value=candidates,
        judgment_value=judgment,
    )
    verifier = validate_checkpoint_verifier(verifier_value, request, proposal)
    if verifier["status"] != "pass":
        _fail("checkpoint-verifier-refused", "checkpoint review requires a passing advisory verifier", {"recommended_action": verifier["recommended_action"]})
    if cube.meta("cube_id") != request["cube_id"]:
        _fail("checkpoint-cube-mismatch", "checkpoint request belongs to another cube")
    preparation = prepare_turn_proposal(cube, proposal["turn_proposal"], include_planner_context=False)
    return {
        "event": "lacuna.checkpoint.reviewed",
        "schema": CHECKPOINT_REVIEW_SCHEMA,
        "reviewed_at": utc_now(),
        "checkpoint_id": request["checkpoint_id"],
        "cube_id": request["cube_id"],
        "request_sha256": checkpoint_request_sha256(request),
        "candidates_sha256": checkpoint_candidates_sha256(candidates, request),
        "judgment_sha256": checkpoint_judgment_sha256(judgment, request, candidates),
        "proposal_sha256": checkpoint_proposal_sha256(proposal, request_value=request),
        "verifier_sha256": checkpoint_verifier_sha256(verifier, request, proposal),
        "selection_evidence_sha256": proposal["selection_evidence_sha256"],
        "mechanical_status": "pass",
        "mechanical_checks": {
            "source_bound_checkpoint_grant": True,
            "artifact_digest_chain": True,
            "deterministic_candidate_selection": True,
            "compression_budget": True,
            "unknown_preservation": True,
            "selection_custody_source": True,
            "turn_binding_preflight": True,
            "kernel_exact_rollback_preparation": True,
        },
        "turn_preparation": preparation,
        "turn_preparation_sha256": _digest(preparation, code="bad-checkpoint-review", label="turn preparation"),
        "nonclaims": [
            "Mechanical review proves local artifact and kernel consistency, not aesthetic quality, model identity, or fair play in the broader authored work.",
            "The preparation is exact replay custody and not a reservation of the cube head.",
            "Only checkpoint commit or exact receipt recovery changes or confirms the ledger.",
        ],
    }


def validate_checkpoint_review(
    value: Any,
    request_value: Any,
    candidates_value: Any,
    judgment_value: Any,
    proposal_value: Any,
    verifier_value: Any,
    *,
    cube: Cube | None = None,
) -> dict[str, Any]:
    code = "bad-checkpoint-review"
    request = validate_checkpoint_request(request_value)
    candidates = validate_checkpoint_candidates(candidates_value, request)
    judgment = validate_checkpoint_judgment(judgment_value, request, candidates)
    proposal = validate_checkpoint_proposal(
        proposal_value,
        request_value=request,
        candidates_value=candidates,
        judgment_value=judgment,
    )
    verifier = validate_checkpoint_verifier(verifier_value, request, proposal)
    if verifier["status"] != "pass":
        _fail(
            "checkpoint-verifier-refused",
            "checkpoint review validation requires a passing advisory verifier",
            {"recommended_action": verifier["recommended_action"]},
        )
    review = _strict(value, "checkpoint review", REVIEW_FIELDS, code=code)
    if review.get("event") != "lacuna.checkpoint.reviewed" or review.get("schema") != CHECKPOINT_REVIEW_SCHEMA:
        _fail(code, "checkpoint review event or schema is invalid")
    try:
        require_string(review.get("reviewed_at"), "reviewed_at", max_len=128)
        require_id(review.get("checkpoint_id"), "checkpoint_id")
        require_id(review.get("cube_id"), "cube_id")
    except ValueError as exc:
        raise LacunaError(code, str(exc)) from exc
    expected = {
        "checkpoint_id": request["checkpoint_id"],
        "cube_id": request["cube_id"],
        "request_sha256": checkpoint_request_sha256(request),
        "candidates_sha256": checkpoint_candidates_sha256(candidates, request),
        "judgment_sha256": checkpoint_judgment_sha256(judgment, request, candidates),
        "proposal_sha256": checkpoint_proposal_sha256(proposal, request_value=request),
        "verifier_sha256": checkpoint_verifier_sha256(verifier, request, proposal),
        "selection_evidence_sha256": proposal["selection_evidence_sha256"],
        "mechanical_status": "pass",
    }
    mismatches = {field: {"expected": expected_value, "actual": review.get(field)} for field, expected_value in expected.items() if review.get(field) != expected_value}
    if mismatches:
        _fail(code, "checkpoint review does not bind the exact artifact chain", {"mismatches": mismatches})
    expected_checks = {
        "source_bound_checkpoint_grant": True,
        "artifact_digest_chain": True,
        "deterministic_candidate_selection": True,
        "compression_budget": True,
        "unknown_preservation": True,
        "selection_custody_source": True,
        "turn_binding_preflight": True,
        "kernel_exact_rollback_preparation": True,
    }
    if review.get("mechanical_checks") != expected_checks:
        _fail(code, "mechanical_checks are not the exact passing set")
    if cube is None:
        _fail(
            code,
            "a passing checkpoint review requires the bound cube for exact preparation replay",
        )
    if cube.meta("cube_id") != request["cube_id"]:
        _fail("checkpoint-cube-mismatch", "checkpoint request belongs to another cube")
    preparation = validate_turn_preparation(
        cube,
        review.get("turn_preparation"),
        proposal["turn_proposal"],
        include_planner_context=False,
    )
    preparation_sha = _digest(preparation, code=code, label="turn preparation")
    if review.get("turn_preparation_sha256") != preparation_sha:
        _fail(code, "turn_preparation_sha256 does not match turn_preparation")
    if preparation.get("schema") != TURN_PREPARATION_SCHEMA or preparation.get("cube_id") != request["cube_id"]:
        _fail(code, "turn preparation does not belong to the checkpoint cube")
    _string_list(review.get("nonclaims"), "nonclaims", code=code, max_items=20, max_len=10000)
    result = copy.deepcopy(review)
    result["turn_preparation"] = preparation
    _digest(result, code=code, label="checkpoint review")
    return result


def _checkpoint_commit_document(
    request: dict[str, Any],
    proposal: dict[str, Any],
    review: dict[str, Any],
    turn_receipt: dict[str, Any],
) -> dict[str, Any]:
    return {
        "event": "lacuna.checkpoint.committed",
        "schema": CHECKPOINT_COMMIT_SCHEMA,
        "overall_status": "accepted",
        "checkpoint_id": request["checkpoint_id"],
        "cube_id": request["cube_id"],
        "selected_candidate_id": proposal["selected_candidate_id"],
        "selection_evidence_sha256": proposal["selection_evidence_sha256"],
        "checkpoint_review_sha256": _digest(
            review,
            code="bad-checkpoint-review",
            label="checkpoint review",
        ),
        "turn_receipt": turn_receipt,
        "narration": turn_receipt["narration"],
        "nonclaims": list(CHECKPOINT_COMMIT_NONCLAIMS),
    }


def _validate_checkpoint_commit_receipt_document(
    value: Any,
    request: dict[str, Any],
    proposal: dict[str, Any],
    review: dict[str, Any],
    *,
    cube: Cube,
) -> dict[str, Any]:
    """Authenticate a receipt after the caller validates the complete checkpoint chain.

    This package-internal boundary keeps committed-run audit and commit from replaying
    the expensive exact preparation twice. Public callers use
    ``validate_checkpoint_commit_receipt``, which validates the complete chain first.
    """
    code = "bad-checkpoint-commit-receipt"
    document = _strict(value, "checkpoint commit receipt", COMMIT_FIELDS, code=code)
    expected_scalars = {
        "event": "lacuna.checkpoint.committed",
        "schema": CHECKPOINT_COMMIT_SCHEMA,
        "overall_status": "accepted",
        "checkpoint_id": request["checkpoint_id"],
        "cube_id": request["cube_id"],
        "selected_candidate_id": proposal["selected_candidate_id"],
        "selection_evidence_sha256": proposal["selection_evidence_sha256"],
        "checkpoint_review_sha256": _digest(
            review,
            code="bad-checkpoint-review",
            label="checkpoint review",
        ),
        "nonclaims": CHECKPOINT_COMMIT_NONCLAIMS,
    }
    mismatches = {
        field: {"expected": expected, "actual": document.get(field)}
        for field, expected in expected_scalars.items()
        if document.get(field) != expected
    }
    if mismatches:
        _fail(code, "checkpoint receipt does not bind the exact reviewed chain", {"mismatches": mismatches})
    turn_receipt = validate_turn_receipt(
        document.get("turn_receipt"),
        proposal["turn_proposal"],
        review["turn_preparation"],
    )
    if document.get("narration") != turn_receipt["narration"]:
        _fail(code, "checkpoint narration differs from the exact turn receipt")
    if cube.meta("cube_id") != request["cube_id"]:
        _fail("checkpoint-cube-mismatch", "checkpoint request belongs to another cube")
    verification = cube.verify()
    if verification["overall_status"] != "pass":
        _fail(
            "cube-verification-failed",
            "committed checkpoint points at a cube that fails verification",
            verification,
        )
    preparation = review["turn_preparation"]
    committed = cube.committed_change(preparation["proposal_id"])
    if committed is None:
        _fail(code, "checkpoint receipt names a change absent from the durable ledger")
    durable_expected = {
        "payload_sha256": preparation["change_payload_sha256"],
        "change": preparation["change"],
        "event_chain": preparation["event_chain"],
    }
    if canonical_json(committed) != canonical_json(durable_expected):
        _fail(
            code,
            "durable checkpoint change differs from the exact preparation",
            {
                "expected_sha256": _digest(durable_expected, code=code, label="expected durable change"),
                "actual_sha256": _digest(committed, code=code, label="durable change"),
            },
        )
    result = copy.deepcopy(document)
    result["turn_receipt"] = turn_receipt
    _digest(result, code=code, label="checkpoint commit receipt")
    return result


def validate_checkpoint_commit_receipt(
    value: Any,
    request_value: Any,
    candidates_value: Any,
    judgment_value: Any,
    proposal_value: Any,
    verifier_value: Any,
    review_value: Any,
    *,
    cube: Cube,
) -> dict[str, Any]:
    """Authenticate a checkpoint receipt against its full sidecar and durable change."""
    request = validate_checkpoint_request(request_value)
    candidates = validate_checkpoint_candidates(candidates_value, request)
    judgment = validate_checkpoint_judgment(judgment_value, request, candidates)
    proposal = validate_checkpoint_proposal(
        proposal_value,
        request_value=request,
        candidates_value=candidates,
        judgment_value=judgment,
    )
    verifier = validate_checkpoint_verifier(verifier_value, request, proposal)
    review = validate_checkpoint_review(
        review_value,
        request,
        candidates,
        judgment,
        proposal,
        verifier,
        cube=cube,
    )
    return _validate_checkpoint_commit_receipt_document(
        value,
        request,
        proposal,
        review,
        cube=cube,
    )


def commit_checkpoint(
    cube: Cube,
    request_value: Any,
    candidates_value: Any,
    judgment_value: Any,
    proposal_value: Any,
    verifier_value: Any,
    review_value: Any,
) -> dict[str, Any]:
    request = validate_checkpoint_request(request_value)
    candidates = validate_checkpoint_candidates(candidates_value, request)
    judgment = validate_checkpoint_judgment(judgment_value, request, candidates)
    proposal = validate_checkpoint_proposal(
        proposal_value,
        request_value=request,
        candidates_value=candidates,
        judgment_value=judgment,
    )
    verifier = validate_checkpoint_verifier(verifier_value, request, proposal)
    review = validate_checkpoint_review(
        review_value,
        request,
        candidates,
        judgment,
        proposal,
        verifier,
        cube=cube,
    )
    if cube.meta("cube_id") != request["cube_id"]:
        _fail("checkpoint-cube-mismatch", "checkpoint request belongs to another cube")
    preparation = review["turn_preparation"]
    proposal_id = proposal["turn_proposal"]["proposal_id"]
    if cube.committed_change(proposal_id) is None:
        turn_receipt = commit_prepared_turn(cube, proposal["turn_proposal"], preparation)
    else:
        turn_receipt = recover_prepared_turn_receipt(cube, proposal["turn_proposal"], preparation)
    receipt = _checkpoint_commit_document(request, proposal, review, turn_receipt)
    return _validate_checkpoint_commit_receipt_document(
        receipt,
        request,
        proposal,
        review,
        cube=cube,
    )


def _checkpoint_dispatch_document(card: dict[str, Any], provider: str) -> dict[str, Any]:
    output = card["output_contract"]
    return {
        "event": "lacuna.checkpoint.agent-dispatch",
        "schema": CHECKPOINT_DISPATCH_SCHEMA,
        "checkpoint_id": card["checkpoint_id"],
        "task_id": card["task_id"],
        "provider": provider,
        "role": card["role"],
        "agent_name": provider_alias(card["role"], provider),
        "input_card_sha256": checkpoint_task_card_sha256(card),
        "input_card": card,
        "return_contract": {
            "schema": output["schema"],
            "format": output["format"],
            "next_command": card["next_command"],
        },
        "instructions": [
            f"Create or invoke exactly one {card['role']} context using provider alias {provider_alias(card['role'], provider)!r}.",
            "Give that worker the complete input_card and no unrelated cube or workspace context.",
            "Require exactly one JSON object matching input_card.output_contract; reject prose, fences, or extra roots.",
            "Save the exact return bytes before invoking the card's next_command.",
            "The parent alone validates, assembles, reviews, commits, recovers, and presents narration.",
        ],
        "authority": card["authority"],
        "nonclaims": [
            "This envelope does not invoke, authenticate, isolate, or attest any provider or subagent.",
            "The provider alias is routing metadata, not authority or proof of model identity.",
            "A syntactically valid worker return remains untrusted until the next Lacuna command validates it.",
        ],
    }


def build_checkpoint_dispatch(card_value: Any, *, provider: str = "portable") -> dict[str, Any]:
    card = validate_checkpoint_task_card(card_value)
    if provider not in PROVIDERS:
        _fail("unknown-checkpoint-provider", f"provider must be one of {list(PROVIDERS)}")
    return validate_checkpoint_dispatch(_checkpoint_dispatch_document(card, provider))


def validate_checkpoint_dispatch(value: Any) -> dict[str, Any]:
    """Validate a self-contained provider routing envelope by exact recomputation."""
    code = "bad-checkpoint-dispatch"
    dispatch = _strict(value, "checkpoint dispatch", DISPATCH_FIELDS, code=code)
    if dispatch.get("event") != "lacuna.checkpoint.agent-dispatch":
        _fail(code, "checkpoint dispatch event is invalid")
    if dispatch.get("schema") != CHECKPOINT_DISPATCH_SCHEMA:
        _fail(code, "checkpoint dispatch schema is invalid")
    provider = dispatch.get("provider")
    if provider not in PROVIDERS:
        _fail(code, f"provider must be one of {list(PROVIDERS)}")
    card = validate_checkpoint_task_card(dispatch.get("input_card"))
    expected = _checkpoint_dispatch_document(card, provider)
    if dispatch != expected:
        differing = sorted(
            field for field in DISPATCH_FIELDS if dispatch.get(field) != expected.get(field)
        )
        _fail(
            code,
            "checkpoint dispatch is not the exact envelope recomputed from its embedded task card and provider",
            {"differing_fields": differing},
        )
    _digest(dispatch, code=code, label="checkpoint dispatch")
    return copy.deepcopy(dispatch)


def checkpoint_task_card_markdown(card_value: Any) -> str:
    card = validate_checkpoint_task_card(card_value)
    lines = [
        f"# {card['role']}",
        "",
        f"- Task: `{card['task_id']}`",
        f"- Checkpoint: `{card['checkpoint_id']}`",
        f"- Required return: `{card['output_contract']['schema']}`",
        "",
        "## Objective",
        "",
        card["objective"],
        "",
        "## Next parent command",
        "",
        f"```bash\n{card['next_command']}\n```",
        "",
        "## Complete machine-readable card",
        "",
        "```json",
        pretty_json(card),
        "```",
        "",
    ]
    return "\n".join(lines)


def checkpoint_dispatch_markdown(dispatch_value: Any) -> str:
    dispatch = validate_checkpoint_dispatch(dispatch_value)
    lines = [
        "# Lacuna checkpoint dispatch",
        "",
        f"- Provider: **{dispatch['provider']}**",
        f"- Role: **{dispatch['role']}**",
        f"- Provider alias: `{dispatch['agent_name']}`",
        f"- Task: `{dispatch['task_id']}`",
        f"- Return schema: `{dispatch['return_contract']['schema']}`",
        "",
        "Give the worker exactly the embedded input card. The parent keeps assemble, review, commit, recovery, and presentation authority.",
        "",
        "## Complete dispatch envelope",
        "",
        "```json",
        pretty_json(dispatch),
        "```",
        "",
    ]
    return "\n".join(lines)
