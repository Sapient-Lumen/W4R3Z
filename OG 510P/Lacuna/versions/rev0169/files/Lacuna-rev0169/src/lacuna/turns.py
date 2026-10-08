from __future__ import annotations

import json
import re
from typing import Any

from .context import build_context
from .entrance import TURN_NARRATION_PLACEHOLDER, build_turn_response_contract
from .errors import LacunaError
from .particles import particle_reconciliation_review_sha256
from .store import EVENT_SCHEMA_VERSION, OPERATION_FIELDS, Cube, consequence_repair_review_sha256
from .util import (
    SHA256_RE,
    canonical_json,
    deterministic_claim_id,
    new_id,
    normalize_audience,
    optional_id,
    optional_string,
    require_id,
    require_list,
    require_mapping,
    require_string,
    sha256_text,
    utc_now,
)

TURN_REQUEST_SCHEMA_V2 = "lacuna.turn-request.v2"
TURN_REQUEST_SCHEMA_V3 = "lacuna.turn-request.v3"
TURN_REQUEST_SCHEMA = "lacuna.turn-request.v4"
SUPPORTED_TURN_REQUEST_SCHEMAS = (
    TURN_REQUEST_SCHEMA_V2,
    TURN_REQUEST_SCHEMA_V3,
    TURN_REQUEST_SCHEMA,
)
TURN_PROPOSAL_SCHEMA = "lacuna.turn-proposal.v2"
TURN_PREPARATION_SCHEMA = "lacuna.turn-preparation.v1"
TURN_RECEIPT_SCHEMA = "lacuna.turn-receipt.v3"
TURN_GRANT_SCHEMA_V1 = "lacuna.turn-grant.v1"
TURN_GRANT_SCHEMA = "lacuna.turn-grant.v2"
TURN_REQUEST_SOURCE_PROTOCOL_V1 = "lacuna.turn-request-source.v1"
TURN_REQUEST_SOURCE_PROTOCOL_V2 = "lacuna.turn-request-source.v2"
TURN_REQUEST_SOURCE_PROTOCOL = "lacuna.turn-request-source.v3"
TURN_INPUT_KINDS = ("play-turn", "session-control")
TURN_REQUEST_PURPOSES = ("play", "checkpoint")

TURN_PROPOSAL_FIELDS = {
    "schema",
    "request_id",
    "request_source_id",
    "proposal_id",
    "actor_id",
    "expected_head",
    "player_input_sha256",
    "audience_id",
    "narration_source_id",
    "narration",
    "revealed_assertion_ids",
    "operations",
    "message",
}
TURN_REQUEST_METADATA_FIELDS_V1 = {
    "protocol",
    "request_schema",
    "request_id",
    "proposal_id",
    "actor_id",
    "audience_id",
    "narration_source_id",
    "player_input_sha256",
    "input_trust",
    "access_mode",
    "world_id",
    "write_grant",
    "base_head",
    "issued_at",
    "content_retained_by_lacuna",
}
TURN_REQUEST_METADATA_FIELDS_V2 = TURN_REQUEST_METADATA_FIELDS_V1 | {"input_kind"}
TURN_REQUEST_METADATA_FIELDS = TURN_REQUEST_METADATA_FIELDS_V2 | {"request_purpose"}
TURN_NARRATION_METADATA_FIELDS = {
    "proposal_id",
    "request_id",
    "request_source_id",
    "request_head",
    "player_input_sha256",
    "audience_id",
    "access_mode",
    "world_scope",
    "grant_profile",
    "presentation_only",
    "content_retained_by_lacuna",
}
TURN_GRANT_FIELDS = {
    "schema",
    "profile",
    "allowed_operations",
    "allow_anchored_assertions",
    "require_audience_visible_writes",
    "world_scope",
    "max_operations",
    "max_reveals",
}

TURN_PREPARATION_FIELDS = {
    "event",
    "schema",
    "overall_status",
    "cube_id",
    "prepared_at",
    "proposal_sha256",
    "include_planner_context",
    "request_id",
    "request_source_id",
    "request_head",
    "player_input_sha256",
    "proposal_id",
    "actor_id",
    "audience_id",
    "access_mode",
    "write_grant",
    "narration_source_id",
    "narration_sha256",
    "narration",
    "revealed_assertion_ids",
    "bindings",
    "change_set",
    "change_payload_sha256",
    "change",
    "event_chain",
    "head",
    "audience_context",
    "planner_context",
    "nonclaims",
}
TURN_RECEIPT_FIELDS = {
    "event",
    "schema",
    "overall_status",
    "cube_id",
    "preparation_sha256",
    "prepared_at",
    "request_id",
    "request_source_id",
    "request_head",
    "player_input_sha256",
    "proposal_id",
    "actor_id",
    "audience_id",
    "access_mode",
    "write_grant",
    "narration_source_id",
    "narration_sha256",
    "narration",
    "revealed_assertion_ids",
    "bindings",
    "change",
    "head",
    "audience_context",
    "planner_context",
    "delivery",
    "nonclaims",
}
CHANGE_RECEIPT_FIELDS = {
    "event",
    "schema",
    "overall_status",
    "cube_id",
    "change_id",
    "actor_id",
    "message",
    "before_head",
    "after_head",
    "operation_count",
    "event_ids",
    "applied_at",
}
EVENT_CHAIN_FIELDS = {
    "seq",
    "event_id",
    "change_id",
    "event_type",
    "schema_version",
    "actor_id",
    "recorded_at",
    "payload",
    "prev_hash",
    "event_hash",
}
DELIVERY_FIELDS = {"mode", "materialized_at", "historical_snapshot_used"}
TURN_PREPARATION_NONCLAIMS = [
    "Preparation is an exact local kernel rehearsal rolled back before publication; it is not a committed turn or a head reservation.",
    "The frozen timestamp, event identifiers, event chain, receipt, and contexts are replay material, not provider or model attestations.",
    "A preparation remains commit-capable only while its request head is current; recovery authenticates an already committed matching change from historical ledger state.",
]
TURN_RECEIPT_NONCLAIMS = [
    "Lacuna stored the player-input and narration digests plus provenance metadata, not either content body.",
    "Lacuna validated request identity, least-authority write scope, disclosure linkage, visibility, and exact prepared replay; it did not prove that the prose semantically entails exactly those assertions.",
    "A committed input or narration source is not itself a claim or an anchor.",
    "Delivery mode reports how this sidecar receipt was materialized; both direct and recovered receipts are bound to the same durable ledger change.",
]

ALIAS_RE = re.compile(r"^[A-Za-z][A-Za-z0-9._:-]{0,63}$")
CREATOR_IDS: dict[str, tuple[str, str]] = {
    "register_agent": ("agent_id", "agt"),
    "add_source": ("source_id", "src"),
    "declare_relation": ("relation_id", "rel"),
    "declare_cardinality": ("constraint_id", "crd"),
    "record_assertion": ("assertion_id", "ast"),
    "create_world": ("world_id", "wld"),
    "assign_world": ("assignment_id", "asn"),
    "revise_world": ("assignment_id", "asn"),
    "raise_commitment": ("transition_id", "cmt"),
    "update_particle_bank": ("update_id", "pup"),
    "reconcile_particle_bank": ("reconciliation_id", "prc"),
    "link_evidence": ("link_id", "evl"),
    "link_consequence": ("consequence_id", "csq"),
    "replace_consequence": ("consequence_id", "csq"),
    "open_question": ("question_id", "qst"),
}
SECONDARY_CREATOR_IDS: dict[str, tuple[str, str]] = {
    "replace_consequence": ("repair_id", "cpr"),
}
REFERENCE_FIELDS: dict[str, set[str]] = {
    "record_assertion": {
        "claim_id",
        "assertor_id",
        "perspective_id",
        "source_id",
        "supersedes_id",
    },
    "supersede_assertion": {"assertion_id"},
    "declare_relation": {"left_claim_id", "right_claim_id", "source_id"},
    "retire_relation": {"relation_id"},
    "declare_cardinality": {"source_id"},
    "retire_cardinality": {"constraint_id"},
    "create_world": {"parent_world_id"},
    "assign_world": {
        "world_id", "claim_id", "source_assertion_id", "commitment_source_id",
    },
    "revise_world": {
        "revises_assignment_id", "source_assertion_id", "commitment_source_id",
    },
    "raise_commitment": {"assignment_id", "source_id"},
    "set_world_weight": {"world_id"},
    "set_world_status": {"world_id"},
    "update_particle_bank": {"evidence_assertion_id"},
    "link_evidence": {"evidence_assertion_id", "target_claim_id", "world_id"},
    "link_consequence": {"premise_assignment_id", "dependent_id", "source_id"},
    "replace_consequence": {
        "replaces_consequence_id", "premise_assignment_id", "dependent_id", "source_id",
    },
    "retire_consequence": {"consequence_id"},
    "open_question": {"about_claim_id", "opened_by"},
    "close_question": {"question_id", "resolution_assertion_id"},
}
REFERENCE_LIST_FIELDS: dict[str, set[str]] = {
    "declare_cardinality": {"claim_ids"},
    "record_assertion": {"audience"},
    "open_question": {"audience"},
}

HOST_CUSTODY_OPERATIONS = {
    "seal_precommitment",
    "reveal_precommitment",
    "void_precommitment",
}

AUDIENCE_TURN_OPERATIONS = {
    "declare_claim",
    "record_assertion",
    "supersede_assertion",
    "open_question",
    "close_question",
}
# A director may reason about visible seal receipts, but cannot create, open, or
# void them through an ordinary LLM turn. Those operations cross a secret-custody
# boundary and require the explicit host/CLI entrance.
DIRECTOR_TURN_OPERATIONS = set(OPERATION_FIELDS) - HOST_CUSTODY_OPERATIONS

# A retcon checkpoint is a hidden-state planning boundary, not an alternate
# route for publishing observations or treating aesthetic preference as
# evidence. Its immutable source-backed grant is deliberately narrower than an
# ordinary director turn; the normal kernel still validates every operation.
CHECKPOINT_TURN_OPERATIONS = {
    "add_source",
    "declare_claim",
    "declare_relation",
    "declare_cardinality",
    "create_world",
    "assign_world",
    "revise_world",
    "link_consequence",
    "open_question",
}


def _require_alias(value: Any, field: str = "as") -> str:
    if not isinstance(value, str) or not ALIAS_RE.fullmatch(value):
        raise LacunaError(
            "bad-turn-alias",
            f"{field} must match {ALIAS_RE.pattern}",
        )
    return value


def _resolve_reference(value: Any, *, aliases: dict[str, str], field: str) -> Any:
    if isinstance(value, str) and value.startswith("@"):
        alias = value[1:]
        if alias not in aliases:
            raise LacunaError(
                "unknown-turn-alias",
                f"{field} references unknown or forward alias {value!r}",
            )
        return aliases[alias]
    return value


def _turn_generated_id(seed: str, prefix: str, index: int, field: str) -> str:
    digest = sha256_text(
        canonical_json(
            {
                "protocol": "lacuna.turn-generated-id.v1",
                "seed": seed,
                "prefix": prefix,
                "operation_index": index,
                "field": field,
            }
        )
    )
    return f"{prefix}_{digest[:24]}"


def normalize_turn_operations(
    operations: list[Any],
    *,
    initial_aliases: dict[str, str],
    id_seed: str | None = None,
) -> tuple[list[dict[str, Any]], dict[str, str]]:
    """Expand sequential @aliases into strict kernel change-set operations."""
    aliases = dict(initial_aliases)
    normalized: list[dict[str, Any]] = []
    for index, raw in enumerate(operations):
        operation = require_mapping(raw, f"operations[{index}]")
        op = operation.get("op")
        if not isinstance(op, str) or op not in OPERATION_FIELDS:
            raise LacunaError(
                "unknown-operation",
                f"operations[{index}].op must be one of {sorted(OPERATION_FIELDS)}",
                {"operation_index": index},
            )
        unexpected = sorted(set(operation) - OPERATION_FIELDS[op] - {"as"})
        if unexpected:
            raise LacunaError(
                "unexpected-turn-operation-field",
                f"turn operation {op!r} contains unrecognized fields",
                {"operation_index": index, "fields": unexpected},
            )
        item = {key: value for key, value in operation.items() if key != "as"}
        for field in REFERENCE_FIELDS.get(op, set()):
            if field in item and item[field] is not None:
                item[field] = _resolve_reference(item[field], aliases=aliases, field=field)
        for field in REFERENCE_LIST_FIELDS.get(op, set()):
            if field not in item or item[field] is None:
                continue
            values = require_list(item[field], f"operations[{index}].{field}")
            item[field] = [
                _resolve_reference(
                    value,
                    aliases=aliases,
                    field=f"operations[{index}].{field}[{position}]",
                )
                for position, value in enumerate(values)
            ]

        if op == "update_particle_bank" and "assessments" in item:
            raw_assessments = require_list(
                item["assessments"], f"operations[{index}].assessments"
            )
            resolved_assessments: list[dict[str, Any]] = []
            for position, raw_assessment in enumerate(raw_assessments):
                assessment = require_mapping(
                    raw_assessment,
                    f"operations[{index}].assessments[{position}]",
                )
                resolved = dict(assessment)
                if resolved.get("world_id") is not None:
                    resolved["world_id"] = _resolve_reference(
                        resolved["world_id"],
                        aliases=aliases,
                        field=f"operations[{index}].assessments[{position}].world_id",
                    )
                resolved_assessments.append(resolved)
            item["assessments"] = resolved_assessments

        if op == "declare_claim":
            if "object" not in item:
                raise LacunaError(
                    "missing-object",
                    "declare_claim requires object",
                    {"operation_index": index},
                )
            subject = require_string(item.get("subject"), "subject", max_len=1024)
            predicate = require_string(item.get("predicate"), "predicate", max_len=1024)
            scope = item.get("scope", "world")
            if not isinstance(scope, str):
                raise LacunaError("invalid-operation", "scope must be a string")
            generated_id = deterministic_claim_id(subject, predicate, item["object"], scope)
            if item.get("claim_id") is None:
                item["claim_id"] = generated_id
        elif op in CREATOR_IDS:
            id_field, prefix = CREATOR_IDS[op]
            if item.get(id_field) is None:
                item[id_field] = (
                    new_id(prefix)
                    if id_seed is None
                    else _turn_generated_id(id_seed, prefix, index, id_field)
                )
        if op in SECONDARY_CREATOR_IDS:
            id_field, prefix = SECONDARY_CREATOR_IDS[op]
            if item.get(id_field) is None:
                item[id_field] = (
                    new_id(prefix)
                    if id_seed is None
                    else _turn_generated_id(id_seed, prefix, index, id_field)
                )

        alias_value = operation.get("as")
        if alias_value is not None:
            alias = _require_alias(alias_value, f"operations[{index}].as")
            if alias in aliases:
                raise LacunaError(
                    "duplicate-turn-alias",
                    f"alias {alias!r} is already bound",
                    {"operation_index": index},
                )
            if op == "declare_claim":
                bound_id = item["claim_id"]
            elif op in CREATOR_IDS:
                bound_id = item[CREATOR_IDS[op][0]]
            else:
                raise LacunaError(
                    "alias-on-noncreator",
                    f"operation {op!r} cannot bind an alias",
                    {"operation_index": index},
                )
            aliases[alias] = require_id(bound_id, f"operations[{index}] bound id")
        normalized.append(item)
    return normalized, aliases


def normalize_turn_input_kind(value: Any) -> str:
    try:
        kind = require_string(value, "input_kind", max_len=64)
    except ValueError as exc:
        raise LacunaError("bad-turn-input-kind", str(exc)) from exc
    if kind not in TURN_INPUT_KINDS:
        raise LacunaError(
            "bad-turn-input-kind",
            f"input_kind must be one of {list(TURN_INPUT_KINDS)}",
        )
    return kind


def _make_turn_grant(
    *,
    director: bool,
    world_id: str | None,
    allow_anchor: bool,
    request_purpose: str,
) -> dict[str, Any]:
    if request_purpose == "checkpoint":
        if not director or world_id is not None or allow_anchor:
            raise LacunaError(
                "unsafe-checkpoint-grant",
                "checkpoint requests require unscoped director context and cannot grant anchored assertions",
            )
        return {
            "schema": TURN_GRANT_SCHEMA,
            "profile": "checkpoint",
            "allowed_operations": sorted(CHECKPOINT_TURN_OPERATIONS),
            "allow_anchored_assertions": False,
            "require_audience_visible_writes": False,
            "world_scope": None,
            "max_operations": 100,
            "max_reveals": 0,
        }
    return {
        "schema": TURN_GRANT_SCHEMA,
        "profile": "director" if director else "audience",
        "allowed_operations": sorted(
            DIRECTOR_TURN_OPERATIONS if director else AUDIENCE_TURN_OPERATIONS
        ),
        "allow_anchored_assertions": bool(allow_anchor),
        "require_audience_visible_writes": not director,
        "world_scope": world_id,
        "max_operations": 999,
        "max_reveals": 500,
    }


def validate_turn_grant(value: Any) -> dict[str, Any]:
    grant = require_mapping(value, "write_grant")
    unexpected = sorted(set(grant) - TURN_GRANT_FIELDS)
    missing = sorted(TURN_GRANT_FIELDS - set(grant))
    if unexpected or missing:
        raise LacunaError(
            "bad-turn-grant",
            "write grant has an invalid field set",
            {"unexpected": unexpected, "missing": missing},
        )
    schema = grant.get("schema")
    if schema not in {TURN_GRANT_SCHEMA_V1, TURN_GRANT_SCHEMA}:
        raise LacunaError(
            "bad-turn-grant",
            f"write_grant.schema must be {TURN_GRANT_SCHEMA_V1!r} or {TURN_GRANT_SCHEMA!r}",
        )
    profile = grant.get("profile")
    allowed_profiles = (
        {"audience", "director"}
        if schema == TURN_GRANT_SCHEMA_V1
        else {"audience", "director", "checkpoint"}
    )
    if profile not in allowed_profiles:
        raise LacunaError(
            "bad-turn-grant",
            f"write_grant.profile must be one of {sorted(allowed_profiles)}",
        )
    if profile == "director":
        expected_operations = sorted(DIRECTOR_TURN_OPERATIONS)
    elif profile == "checkpoint":
        expected_operations = sorted(CHECKPOINT_TURN_OPERATIONS)
    else:
        expected_operations = sorted(AUDIENCE_TURN_OPERATIONS)
    if grant.get("allowed_operations") != expected_operations:
        raise LacunaError(
            "bad-turn-grant",
            "write_grant.allowed_operations does not match its profile",
        )
    if not isinstance(grant.get("allow_anchored_assertions"), bool):
        raise LacunaError("bad-turn-grant", "allow_anchored_assertions must be boolean")
    expected_visible = profile == "audience"
    if grant.get("require_audience_visible_writes") is not expected_visible:
        raise LacunaError(
            "bad-turn-grant",
            "require_audience_visible_writes does not match the grant profile",
        )
    world_scope = grant.get("world_scope")
    if world_scope is not None:
        try:
            require_id(world_scope, "write_grant.world_scope")
        except ValueError as exc:
            raise LacunaError("bad-turn-grant", str(exc)) from exc
        if profile != "director":
            raise LacunaError("bad-turn-grant", "only director grants may name a world scope")
    expected_limits = (100, 0) if profile == "checkpoint" else (999, 500)
    if (grant.get("max_operations"), grant.get("max_reveals")) != expected_limits:
        raise LacunaError(
            "bad-turn-grant",
            "unsupported turn grant limits",
            {"expected": expected_limits},
        )
    if profile == "checkpoint" and grant.get("allow_anchored_assertions") is not False:
        raise LacunaError(
            "bad-turn-grant",
            "checkpoint grants cannot allow anchored assertions",
        )
    return dict(grant)


def _rebind_context_head(context: dict[str, Any], head: str) -> None:
    """Bind a preflight context and its embedded review receipts to one issued head.

    Opening a turn adds only the request provenance source.  The context was
    collected immediately before that append, so its epistemic projections stay
    unchanged; head-bound authorization receipts must nevertheless be rehashed.
    """
    context["head"] = head
    particle_bank = context.get("particle_bank")
    if isinstance(particle_bank, dict):
        particle_bank["head"] = head
    reconciliation_review = context.get("particle_reconciliation_review")
    if isinstance(reconciliation_review, dict):
        reconciliation_review["head"] = head
        review_core = reconciliation_review.get("review_core")
        if isinstance(review_core, dict):
            digest = particle_reconciliation_review_sha256(
                cube_id=str(reconciliation_review["cube_id"]),
                head=head,
                review_core=review_core,
            )
            reconciliation_review["reconciliation_review_sha256"] = digest
            reconciliation_review["expected_reconciliation_sha256"] = digest

    for review in context.get("consequence_repair_frontier", []):
        review["head"] = head
        digest = consequence_repair_review_sha256(
            cube_id=str(review["cube_id"]),
            head=head,
            target=review["target"],
            known_successors=review["known_successors"],
            blockers=review["blockers"],
        )
        review["repair_review_sha256"] = digest
        review["review"]["expected_repair_sha256"] = digest


def build_turn_packet(
    cube: Cube,
    *,
    audience_id: str,
    actor_id: str,
    player_input: str,
    input_kind: str = "play-turn",
    director: bool = False,
    world_id: str | None = None,
    allow_anchor: bool = False,
    request_purpose: str = "play",
) -> dict[str, Any]:
    """Open a source-backed turn request and emit its model/human packet.

    Opening a turn is a ledger mutation: the exact player-input digest, the
    audience/actor binding, and a least-authority write grant are committed as
    one provenance source. The returned expected_head is the hash of that event.
    """
    audience_id = require_id(audience_id, "audience_id")
    actor_id = require_id(actor_id, "actor_id")
    player_input = require_string(player_input, "player_input", max_len=50000)
    input_kind = normalize_turn_input_kind(input_kind)
    if request_purpose not in TURN_REQUEST_PURPOSES:
        raise LacunaError(
            "bad-turn-request-purpose",
            f"request_purpose must be one of {list(TURN_REQUEST_PURPOSES)}",
        )
    if request_purpose == "checkpoint" and input_kind != "session-control":
        raise LacunaError(
            "bad-checkpoint-input-kind",
            "checkpoint requests must classify their trigger as session-control",
        )
    cube._require_agent(audience_id, "audience_id")
    cube._require_agent(actor_id, "actor_id")
    if world_id is not None:
        world_id = require_id(world_id, "world_id")
        if not director:
            raise LacunaError(
                "unsafe-turn-scope",
                "a candidate world may be requested only for an explicit director packet",
            )
        cube._require_world(world_id)

    base_head = cube.head()
    audience_context = build_context(cube, agent_id=audience_id)
    planner_context = build_context(cube, world_id=world_id) if director else None

    request_id = new_id("trq")
    request_source_id = new_id("src")
    proposal_id = new_id("prp")
    narration_source_id = new_id("src")
    issued_at = utc_now()
    player_input_digest = sha256_text(player_input)
    write_grant = _make_turn_grant(
        director=director,
        world_id=world_id,
        allow_anchor=allow_anchor,
        request_purpose=request_purpose,
    )
    request_metadata = {
        "protocol": TURN_REQUEST_SOURCE_PROTOCOL,
        "request_schema": TURN_REQUEST_SCHEMA,
        "request_id": request_id,
        "proposal_id": proposal_id,
        "actor_id": actor_id,
        "audience_id": audience_id,
        "narration_source_id": narration_source_id,
        "player_input_sha256": player_input_digest,
        "input_trust": "untrusted-player-data",
        "input_kind": input_kind,
        "request_purpose": request_purpose,
        "access_mode": "director" if director else "audience",
        "world_id": world_id,
        "write_grant": write_grant,
        "base_head": base_head,
        "issued_at": issued_at,
        "content_retained_by_lacuna": False,
    }
    request_change = cube.apply_changeset(
        {
            "schema": "lacuna.change-set.v1",
            "change_id": request_id,
            "actor_id": audience_id,
            "expected_head": base_head,
            "message": f"open turn request {request_id}",
            "operations": [
                {
                    "op": "add_source",
                    "source_id": request_source_id,
                    "kind": "user",
                    "label": f"Player input for {request_id}",
                    "locator": f"lacuna:turn:{request_id}:input",
                    "content_sha256": player_input_digest,
                    "metadata": request_metadata,
                }
            ],
        }
    )
    expected_head = request_change["after_head"]
    # The request source changes custody but no assertion/world/question projection.
    # Rebinding the already-built contexts to its event hash avoids a race between
    # context collection and issuance while keeping every packet internally head-equal.
    _rebind_context_head(audience_context, expected_head)
    if planner_context is not None:
        _rebind_context_head(planner_context, expected_head)

    response_contract = build_turn_response_contract(
        proposal_schema=TURN_PROPOSAL_SCHEMA,
        request_id=request_id,
        request_source_id=request_source_id,
        proposal_id=proposal_id,
        actor_id=actor_id,
        expected_head=expected_head,
        player_input_sha256=player_input_digest,
        audience_id=audience_id,
        narration_source_id=narration_source_id,
        allowed_operations=list(write_grant["allowed_operations"]),
    )
    return {
        "event": "lacuna.turn.requested",
        "schema": TURN_REQUEST_SCHEMA,
        "request_id": request_id,
        "request_source_id": request_source_id,
        "cube_id": cube.meta("cube_id"),
        "expected_head": expected_head,
        "created_at": issued_at,
        "player_input_sha256": player_input_digest,
        "input_trust": "untrusted-player-data",
        "input_kind": input_kind,
        "request_purpose": request_purpose,
        "audience_id": audience_id,
        "actor_id": actor_id,
        "access_mode": "director" if director else "audience",
        "player_input": player_input,
        "write_grant": write_grant,
        "audience_context": audience_context,
        "planner_context": planner_context,
        "response_contract": response_contract,
        "nonclaim": (
            "The packet supplies state and a source-backed least-authority mutation contract for its declared purpose. "
            "Lacuna stored the player-input digest and grant, not the input body; it does not choose plot, "
            "score drama, or call a language model."
        ),
    }


def _load_turn_request(cube: Cube, request_source_id: str) -> dict[str, Any]:
    row = cube.conn.execute(
        """SELECT s.source_id, s.kind, s.label, s.locator, s.content_sha256,
                  s.metadata_json, s.created_seq,
                  e.seq, e.event_id, e.event_type, e.schema_version,
                  e.actor_id AS event_actor_id, e.recorded_at, e.payload_json,
                  e.prev_hash, e.event_hash, e.change_id,
                  cs.before_head, cs.after_head, cs.operation_count
           FROM sources s
           JOIN events e ON e.seq = s.created_seq
           JOIN changesets cs ON cs.change_id = e.change_id
           WHERE s.source_id = ? AND s.retired_seq IS NULL""",
        (request_source_id,),
    ).fetchone()
    if row is None:
        raise LacunaError(
            "unknown-turn-request",
            f"request_source_id {request_source_id!r} is not an active source-backed turn request",
        )
    if row["kind"] != "user" or row["event_type"] != "source.added":
        raise LacunaError("invalid-turn-request", "request source has the wrong provenance kind")
    try:
        metadata = json.loads(row["metadata_json"])
        event_payload = json.loads(row["payload_json"])
    except json.JSONDecodeError as exc:
        raise LacunaError(
            "invalid-turn-request",
            "request source metadata or issuing event payload is not valid JSON",
        ) from exc
    if not isinstance(event_payload, dict):
        raise LacunaError("invalid-turn-request", "request source event payload must be an object")
    event_core = {
        "seq": row["seq"],
        "event_id": row["event_id"],
        "change_id": row["change_id"],
        "event_type": row["event_type"],
        "schema_version": row["schema_version"],
        "actor_id": row["event_actor_id"],
        "recorded_at": row["recorded_at"],
        "payload": event_payload,
        "prev_hash": row["prev_hash"],
    }
    if sha256_text(canonical_json(event_core)) != row["event_hash"]:
        raise LacunaError(
            "invalid-turn-request",
            "the issuing event does not match its recorded hash",
        )
    projected_payload = {
        "source_id": row["source_id"],
        "kind": row["kind"],
        "label": row["label"],
        "locator": row["locator"],
        "content_sha256": row["content_sha256"],
        "metadata": metadata,
    }
    if canonical_json(event_payload) != canonical_json(projected_payload):
        raise LacunaError(
            "invalid-turn-request",
            "request-source projection does not match its immutable issuing event",
        )
    if not isinstance(metadata, dict):
        raise LacunaError("invalid-turn-request", "request source metadata must be an object")
    protocol = metadata.get("protocol")
    request_schema = metadata.get("request_schema")
    if protocol == TURN_REQUEST_SOURCE_PROTOCOL_V1 and request_schema == TURN_REQUEST_SCHEMA_V2:
        expected_metadata_fields = TURN_REQUEST_METADATA_FIELDS_V1
        input_kind = "play-turn"
        request_purpose = "play"
    elif protocol == TURN_REQUEST_SOURCE_PROTOCOL_V2 and request_schema == TURN_REQUEST_SCHEMA_V3:
        expected_metadata_fields = TURN_REQUEST_METADATA_FIELDS_V2
        input_kind = metadata.get("input_kind")
        request_purpose = "play"
    elif protocol == TURN_REQUEST_SOURCE_PROTOCOL and request_schema == TURN_REQUEST_SCHEMA:
        expected_metadata_fields = TURN_REQUEST_METADATA_FIELDS
        input_kind = metadata.get("input_kind")
        request_purpose = metadata.get("request_purpose")
    else:
        raise LacunaError(
            "invalid-turn-request",
            "source is not a supported Lacuna turn-request capability",
            {
                "protocol": protocol,
                "request_schema": request_schema,
                "supported": [
                    [TURN_REQUEST_SOURCE_PROTOCOL_V1, TURN_REQUEST_SCHEMA_V2],
                    [TURN_REQUEST_SOURCE_PROTOCOL_V2, TURN_REQUEST_SCHEMA_V3],
                    [TURN_REQUEST_SOURCE_PROTOCOL, TURN_REQUEST_SCHEMA],
                ],
            },
        )
    unexpected = sorted(set(metadata) - expected_metadata_fields)
    missing = sorted(expected_metadata_fields - set(metadata))
    if unexpected or missing:
        raise LacunaError(
            "invalid-turn-request",
            "request source metadata has an invalid field set",
            {"unexpected": unexpected, "missing": missing},
        )
    if input_kind not in TURN_INPUT_KINDS:
        raise LacunaError("invalid-turn-request", "request source input_kind is invalid")
    if request_purpose not in TURN_REQUEST_PURPOSES:
        raise LacunaError("invalid-turn-request", "request source request_purpose is invalid")
    if request_purpose == "checkpoint" and input_kind != "session-control":
        raise LacunaError(
            "invalid-turn-request",
            "checkpoint request source must use session-control input",
        )
    if metadata.get("content_retained_by_lacuna") is not False:
        raise LacunaError("invalid-turn-request", "request source retention marker is invalid")
    if metadata.get("input_trust") != "untrusted-player-data":
        raise LacunaError("invalid-turn-request", "request source trust class is invalid")
    try:
        require_string(metadata.get("issued_at"), "issued_at", max_len=128)
    except ValueError as exc:
        raise LacunaError("invalid-turn-request", str(exc)) from exc
    if row["label"] != f"Player input for {metadata.get('request_id')}":
        raise LacunaError("invalid-turn-request", "request source label is not protocol canonical")
    if row["locator"] != f"lacuna:turn:{metadata.get('request_id')}:input":
        raise LacunaError("invalid-turn-request", "request source locator is not protocol canonical")
    player_input_sha256 = metadata.get("player_input_sha256")
    if not isinstance(player_input_sha256, str) or not SHA256_RE.fullmatch(player_input_sha256):
        raise LacunaError("invalid-turn-request", "request player_input_sha256 is invalid")
    if row["content_sha256"] != player_input_sha256:
        raise LacunaError("invalid-turn-request", "request source digest and metadata disagree")
    for field in ("request_id", "proposal_id", "actor_id", "audience_id", "narration_source_id"):
        try:
            require_id(metadata.get(field), field)
        except ValueError as exc:
            raise LacunaError("invalid-turn-request", str(exc)) from exc
    world_id = metadata.get("world_id")
    if world_id is not None:
        try:
            require_id(world_id, "world_id")
        except ValueError as exc:
            raise LacunaError("invalid-turn-request", str(exc)) from exc
    access_mode = metadata.get("access_mode")
    if access_mode not in {"audience", "director"}:
        raise LacunaError("invalid-turn-request", "request access_mode is invalid")
    if world_id is not None and access_mode != "director":
        raise LacunaError("invalid-turn-request", "an audience request cannot carry a world scope")
    grant = validate_turn_grant(metadata.get("write_grant"))
    expected_grant_profile = "checkpoint" if request_purpose == "checkpoint" else access_mode
    if grant["profile"] != expected_grant_profile or grant["world_scope"] != world_id:
        raise LacunaError("invalid-turn-request", "request access mode, world scope, and grant disagree")
    base_head = metadata.get("base_head")
    if not isinstance(base_head, str) or not SHA256_RE.fullmatch(base_head):
        raise LacunaError("invalid-turn-request", "request base_head is invalid")
    if (
        row["prev_hash"] != base_head
        or row["before_head"] != base_head
        or row["after_head"] != row["event_hash"]
        or row["operation_count"] != 1
        or row["change_id"] != metadata["request_id"]
        or row["event_actor_id"] != metadata["audience_id"]
    ):
        raise LacunaError(
            "invalid-turn-request",
            "request source is not a one-event, head-bound issuance",
        )
    result = dict(metadata)
    result["input_kind"] = input_kind
    result["request_purpose"] = request_purpose
    result["request_source_id"] = request_source_id
    result["request_head"] = row["event_hash"]
    result["write_grant"] = grant
    return result


def durable_turn_public_custody(
    cube: Cube,
    narration_source_id: str,
) -> dict[str, Any]:
    """Authenticate one committed turn's public ledger boundary.

    The exact player-input and narration bodies live outside the cube. This
    helper authenticates the durable identities and content digests that a
    retained managed run must match: the source-backed request, the canonical
    narration source, the proposal changeset, and their immutable event
    positions. It is shared by public-history authentication and completeness
    census work so those two paths cannot silently drift.
    """
    try:
        narration_source_id = require_id(
            narration_source_id,
            "narration_source_id",
        )
    except ValueError as exc:
        raise LacunaError("invalid-turn-narration-custody", str(exc)) from exc

    row = cube.conn.execute(
        """SELECT s.source_id, s.kind, s.label, s.locator, s.content_sha256,
                  s.metadata_json, s.created_seq,
                  e.seq, e.event_id, e.event_type, e.schema_version,
                  e.actor_id AS event_actor_id, e.recorded_at, e.payload_json,
                  e.prev_hash, e.event_hash, e.change_id,
                  cs.actor_id AS change_actor_id, cs.expected_head,
                  cs.before_head, cs.after_head, cs.operation_count
           FROM sources s
           JOIN events e ON e.seq = s.created_seq
           JOIN changesets cs ON cs.change_id = e.change_id
           WHERE s.source_id = ?""",
        (narration_source_id,),
    ).fetchone()
    if row is None:
        raise LacunaError(
            "unknown-turn-narration-source",
            f"narration_source_id {narration_source_id!r} is not present",
        )
    if row["kind"] != "utterance" or row["event_type"] != "source.added":
        raise LacunaError(
            "invalid-turn-narration-custody",
            "turn narration source has the wrong provenance kind",
        )
    try:
        metadata = require_mapping(
            json.loads(row["metadata_json"]),
            "turn narration source metadata",
        )
        event_payload = require_mapping(
            json.loads(row["payload_json"]),
            "turn narration source event payload",
        )
    except (TypeError, ValueError, json.JSONDecodeError) as exc:
        raise LacunaError(
            "invalid-turn-narration-custody",
            "turn narration source metadata or event payload is invalid",
        ) from exc

    unexpected = sorted(set(metadata) - TURN_NARRATION_METADATA_FIELDS)
    missing = sorted(TURN_NARRATION_METADATA_FIELDS - set(metadata))
    if unexpected or missing:
        raise LacunaError(
            "invalid-turn-narration-custody",
            "turn narration source metadata has an invalid field set",
            {"unexpected": unexpected, "missing": missing},
        )

    event_core = {
        "seq": row["seq"],
        "event_id": row["event_id"],
        "change_id": row["change_id"],
        "event_type": row["event_type"],
        "schema_version": row["schema_version"],
        "actor_id": row["event_actor_id"],
        "recorded_at": row["recorded_at"],
        "payload": event_payload,
        "prev_hash": row["prev_hash"],
    }
    if sha256_text(canonical_json(event_core)) != row["event_hash"]:
        raise LacunaError(
            "invalid-turn-narration-custody",
            "turn narration issuing event does not match its recorded hash",
        )
    projected_payload = {
        "source_id": row["source_id"],
        "kind": row["kind"],
        "label": row["label"],
        "locator": row["locator"],
        "content_sha256": row["content_sha256"],
        "metadata": metadata,
    }
    if canonical_json(event_payload) != canonical_json(projected_payload):
        raise LacunaError(
            "invalid-turn-narration-custody",
            "turn narration source projection does not match its immutable event",
        )

    try:
        proposal_id = require_id(metadata.get("proposal_id"), "proposal_id")
        request_id = require_id(metadata.get("request_id"), "request_id")
        request_source_id = require_id(
            metadata.get("request_source_id"),
            "request_source_id",
        )
        audience_id = require_id(metadata.get("audience_id"), "audience_id")
    except ValueError as exc:
        raise LacunaError("invalid-turn-narration-custody", str(exc)) from exc
    for field in ("request_head", "player_input_sha256"):
        value = metadata.get(field)
        if not isinstance(value, str) or not SHA256_RE.fullmatch(value):
            raise LacunaError(
                "invalid-turn-narration-custody",
                f"turn narration metadata {field} is not a SHA-256 digest",
            )
    request = _load_turn_request(cube, request_source_id)
    expected_metadata = {
        "proposal_id": request["proposal_id"],
        "request_id": request["request_id"],
        "request_source_id": request_source_id,
        "request_head": request["request_head"],
        "player_input_sha256": request["player_input_sha256"],
        "audience_id": request["audience_id"],
        "access_mode": request["access_mode"],
        "world_scope": request["write_grant"]["world_scope"],
        "grant_profile": request["write_grant"]["profile"],
        "presentation_only": True,
        "content_retained_by_lacuna": False,
    }
    mismatched = {
        field: {"expected": expected, "actual": metadata.get(field)}
        for field, expected in expected_metadata.items()
        if metadata.get(field) != expected
    }
    if mismatched:
        raise LacunaError(
            "invalid-turn-narration-custody",
            "turn narration metadata disagrees with its source-backed request",
            {"mismatched": mismatched},
        )
    if proposal_id != request["proposal_id"] or request_id != request["request_id"]:
        raise LacunaError(
            "invalid-turn-narration-custody",
            "turn narration proposal or request identity is inconsistent",
        )
    if audience_id != request["audience_id"]:
        raise LacunaError(
            "invalid-turn-narration-custody",
            "turn narration audience is inconsistent",
        )
    if request["narration_source_id"] != narration_source_id:
        raise LacunaError(
            "invalid-turn-narration-custody",
            "turn request names a different narration source",
        )
    if row["label"] != f"Narration for {proposal_id}":
        raise LacunaError(
            "invalid-turn-narration-custody",
            "turn narration source label is not protocol canonical",
        )
    if row["locator"] != f"lacuna:turn:{proposal_id}:narration":
        raise LacunaError(
            "invalid-turn-narration-custody",
            "turn narration source locator is not protocol canonical",
        )
    narration_sha256 = row["content_sha256"]
    if not isinstance(narration_sha256, str) or not SHA256_RE.fullmatch(
        narration_sha256
    ):
        raise LacunaError(
            "invalid-turn-narration-custody",
            "turn narration source content digest is invalid",
        )

    request_event_seq = cube.event_sequence(request["request_head"])
    commit_event_seq = cube.event_sequence(row["after_head"])
    if (
        row["change_id"] != proposal_id
        or row["change_actor_id"] != request["actor_id"]
        or row["event_actor_id"] != request["actor_id"]
        or row["expected_head"] != request["request_head"]
        or row["before_head"] != request["request_head"]
        or row["prev_hash"] != request["request_head"]
        or int(row["created_seq"]) != request_event_seq + 1
        or int(row["seq"]) != request_event_seq + 1
        or commit_event_seq
        != request_event_seq + int(row["operation_count"])
        or int(row["operation_count"]) < 1
    ):
        raise LacunaError(
            "invalid-turn-narration-custody",
            "turn narration source is not the first event of one exact source-bound proposal change",
        )

    return {
        "request_id": request["request_id"],
        "request_source_id": request_source_id,
        "narration_source_id": narration_source_id,
        "proposal_id": proposal_id,
        "actor_id": request["actor_id"],
        "audience_id": request["audience_id"],
        "input_kind": request["input_kind"],
        "request_purpose": request["request_purpose"],
        "player_input_sha256": request["player_input_sha256"],
        "narration_sha256": narration_sha256,
        "request_head": request["request_head"],
        "post_commit_head": row["after_head"],
        "request_event_seq": request_event_seq,
        "commit_event_seq": commit_event_seq,
    }


def durable_play_turn_census(
    cube: Cube,
    *,
    audience_id: str,
    before_event_seq: int,
) -> list[dict[str, Any]]:
    """List every committed ordinary turn visible to one audience before a boundary.

    The census is ledger-complete for Lacuna turn proposals under the supplied
    immutable event boundary. It deliberately says nothing about chat messages
    that were never committed through Lacuna or exact transcript bodies whose
    sidecars were not retained.
    """
    try:
        audience_id = require_id(audience_id, "audience_id")
    except ValueError as exc:
        raise LacunaError("bad-turn-census", str(exc)) from exc
    if (
        isinstance(before_event_seq, bool)
        or not isinstance(before_event_seq, int)
        or before_event_seq < 1
    ):
        raise LacunaError(
            "bad-turn-census",
            "before_event_seq must be a positive integer",
        )
    rows = cube.conn.execute(
        """SELECT source_id
           FROM sources
           WHERE kind = 'utterance'
             AND label LIKE 'Narration for %'
             AND locator LIKE 'lacuna:turn:%:narration'
             AND created_seq < ?
           ORDER BY created_seq, source_id""",
        (before_event_seq,),
    ).fetchall()
    records: list[dict[str, Any]] = []
    previous_commit = 0
    for row in rows:
        record = durable_turn_public_custody(cube, row["source_id"])
        if record["request_purpose"] != "play":
            continue
        if record["audience_id"] != audience_id:
            continue
        if record["commit_event_seq"] >= before_event_seq:
            raise LacunaError(
                "bad-turn-census",
                "a committed play turn crosses the requested census boundary",
                {
                    "proposal_id": record["proposal_id"],
                    "commit_event_seq": record["commit_event_seq"],
                    "before_event_seq": before_event_seq,
                },
            )
        if record["request_event_seq"] <= previous_commit:
            raise LacunaError(
                "bad-turn-census",
                "committed play-turn boundaries overlap or are out of order",
                {"proposal_id": record["proposal_id"]},
            )
        previous_commit = record["commit_event_seq"]
        records.append(record)
    return records


def _normalize_reveals(values: list[Any], aliases: dict[str, str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for index, value in enumerate(values):
        resolved = _resolve_reference(value, aliases=aliases, field=f"revealed_assertion_ids[{index}]")
        assertion_id = require_id(resolved, f"revealed_assertion_ids[{index}]")
        if assertion_id not in seen:
            result.append(assertion_id)
            seen.add(assertion_id)
    return result


def _operation_assertion_view(operation: dict[str, Any]) -> dict[str, Any]:
    assertor_id = require_id(operation.get("assertor_id"), "assertor_id")
    perspective_id = require_id(operation.get("perspective_id", assertor_id), "perspective_id")
    visibility = operation.get("visibility", "private")
    audience = normalize_audience(operation.get("audience"))
    return {
        "assertion_id": require_id(operation.get("assertion_id"), "assertion_id"),
        "assertor_id": assertor_id,
        "perspective_id": perspective_id,
        "visibility": visibility,
        "audience": audience,
        "source_id": optional_id(operation.get("source_id"), "source_id"),
    }


def _operation_question_view(operation: dict[str, Any]) -> dict[str, Any]:
    return {
        "question_id": require_id(operation.get("question_id"), "question_id"),
        "opened_by": require_id(operation.get("opened_by"), "opened_by"),
        "visibility": operation.get("visibility", "private"),
        "audience": normalize_audience(operation.get("audience")),
    }


def _question(cube: Cube, question_id: str, *, open_only: bool = False) -> dict[str, Any]:
    sql = "SELECT * FROM questions WHERE question_id = ?"
    if open_only:
        sql += " AND status = 'open'"
    row = cube.conn.execute(sql, (question_id,)).fetchone()
    if row is None:
        qualifier = "open " if open_only else ""
        raise LacunaError("unknown-question", f"unknown {qualifier}question {question_id!r}")
    item = dict(row)
    item["audience"] = json.loads(item.pop("audience_json"))
    return item


def _validate_turn_write_grant(
    cube: Cube,
    *,
    grant: dict[str, Any],
    audience_id: str,
    operations: list[dict[str, Any]],
) -> None:
    allowed_operations = set(grant["allowed_operations"])
    profile = grant["profile"]
    scoped_world = grant.get("world_scope")
    scoped_worlds: set[str] = {scoped_world} if scoped_world is not None else set()
    pending_assignment_worlds: dict[str, str] = {}
    pending_consequence_premises: dict[str, str] = {}

    def assignment_world(assignment_id: str) -> str:
        if assignment_id in pending_assignment_worlds:
            return pending_assignment_worlds[assignment_id]
        return str(cube._require_world_assignment(assignment_id)["world_id"])

    for index, operation in enumerate(operations):
        op = operation["op"]
        if op not in allowed_operations:
            raise LacunaError(
                "turn-operation-not-granted",
                f"write grant profile {profile!r} does not authorize operation {op!r}",
                {"operation_index": index, "operation": op},
            )

        if op == "record_assertion":
            if operation.get("standing", "reported") == "anchored" and not grant[
                "allow_anchored_assertions"
            ]:
                raise LacunaError(
                    "turn-anchor-not-granted",
                    "this turn request did not grant authority to create anchored assertions",
                    {"operation_index": index},
                )
            if grant["require_audience_visible_writes"]:
                view = _operation_assertion_view(operation)
                if not Cube.assertion_visible_to(view, audience_id):
                    raise LacunaError(
                        "hidden-turn-write",
                        "an audience-profile turn may not create an assertion hidden from its audience",
                        {"operation_index": index, "assertion_id": view["assertion_id"]},
                    )
                supersedes_id = operation.get("supersedes_id")
                if supersedes_id is not None:
                    old = cube.assertion(require_id(supersedes_id, "supersedes_id"), active=True)
                    if not Cube.assertion_visible_to(old, audience_id):
                        raise LacunaError(
                            "hidden-turn-write",
                            "an audience-profile turn may not supersede a hidden assertion",
                            {"operation_index": index, "assertion_id": supersedes_id},
                        )

        elif op == "supersede_assertion" and grant["require_audience_visible_writes"]:
            assertion_id = require_id(operation.get("assertion_id"), "assertion_id")
            assertion = cube.assertion(assertion_id, active=True)
            if not Cube.assertion_visible_to(assertion, audience_id):
                raise LacunaError(
                    "hidden-turn-write",
                    "an audience-profile turn may not supersede a hidden assertion",
                    {"operation_index": index, "assertion_id": assertion_id},
                )

        elif op == "open_question" and grant["require_audience_visible_writes"]:
            view = _operation_question_view(operation)
            if not Cube.question_visible_to(view, audience_id):
                raise LacunaError(
                    "hidden-turn-write",
                    "an audience-profile turn may not open a question hidden from its audience",
                    {"operation_index": index, "question_id": view["question_id"]},
                )

        elif op == "close_question" and grant["require_audience_visible_writes"]:
            question_id = require_id(operation.get("question_id"), "question_id")
            question = _question(cube, question_id, open_only=True)
            if not Cube.question_visible_to(question, audience_id):
                raise LacunaError(
                    "hidden-turn-write",
                    "an audience-profile turn may not close a hidden question",
                    {"operation_index": index, "question_id": question_id},
                )
            resolution_assertion_id = operation.get("resolution_assertion_id")
            if resolution_assertion_id is not None:
                resolution = cube.assertion(
                    require_id(resolution_assertion_id, "resolution_assertion_id"),
                    active=True,
                )
                if not Cube.assertion_visible_to(resolution, audience_id):
                    raise LacunaError(
                        "hidden-turn-write",
                        "an audience-profile turn may not close a question with a hidden resolution",
                        {
                            "operation_index": index,
                            "resolution_assertion_id": resolution_assertion_id,
                        },
                    )

        if profile == "director" and scoped_world is not None:
            if op in {"update_particle_bank", "reconcile_particle_bank"}:
                raise LacunaError(
                    "turn-world-scope-violation",
                    "particle-bank updates and reconciliations govern the complete live population and require an unscoped director grant",
                    {"operation_index": index, "world_scope": scoped_world},
                )
            if op == "create_world":
                parent_world_id = operation.get("parent_world_id")
                if parent_world_id is None or parent_world_id not in scoped_worlds:
                    raise LacunaError(
                        "turn-world-scope-violation",
                        "a world-scoped director turn may create only descendants of its scoped world",
                        {"operation_index": index, "world_scope": scoped_world},
                    )
                scoped_worlds.add(require_id(operation.get("world_id"), "world_id"))
            elif op in {"assign_world", "set_world_weight", "set_world_status"}:
                target_world = require_id(operation.get("world_id"), "world_id")
                if target_world not in scoped_worlds:
                    raise LacunaError(
                        "turn-world-scope-violation",
                        "director operation targets a world outside the request grant",
                        {
                            "operation_index": index,
                            "world_id": target_world,
                            "world_scope": scoped_world,
                        },
                    )
                if op == "assign_world":
                    pending_assignment_worlds[
                        require_id(operation.get("assignment_id"), "assignment_id")
                    ] = target_world
            elif op == "revise_world":
                predecessor_id = require_id(
                    operation.get("revises_assignment_id"), "revises_assignment_id"
                )
                target_world = assignment_world(predecessor_id)
                if target_world not in scoped_worlds:
                    raise LacunaError(
                        "turn-world-scope-violation",
                        "governed revision targets an assignment outside the request grant",
                        {
                            "operation_index": index,
                            "world_id": target_world,
                            "world_scope": scoped_world,
                        },
                    )
                pending_assignment_worlds[
                    require_id(operation.get("assignment_id"), "assignment_id")
                ] = target_world
            elif op == "raise_commitment":
                assignment_id = require_id(operation.get("assignment_id"), "assignment_id")
                target_world = assignment_world(assignment_id)
                if target_world not in scoped_worlds:
                    raise LacunaError(
                        "turn-world-scope-violation",
                        "commitment transition targets an assignment outside the request grant",
                        {
                            "operation_index": index,
                            "world_id": target_world,
                            "world_scope": scoped_world,
                        },
                    )
            elif op in {"link_consequence", "replace_consequence"}:
                premise_id = require_id(
                    operation.get("premise_assignment_id"), "premise_assignment_id"
                )
                target_world = assignment_world(premise_id)
                if target_world not in scoped_worlds:
                    raise LacunaError(
                        "turn-world-scope-violation",
                        "consequence premise is outside the request grant",
                        {
                            "operation_index": index,
                            "world_id": target_world,
                            "world_scope": scoped_world,
                        },
                    )
                if op == "replace_consequence":
                    predecessor_id = require_id(
                        operation.get("replaces_consequence_id"),
                        "replaces_consequence_id",
                    )
                    if predecessor_id in pending_consequence_premises:
                        raise LacunaError(
                            "unreviewable-pending-consequence",
                            "a consequence created in this turn has no base-head repair review",
                            {
                                "operation_index": index,
                                "consequence_id": predecessor_id,
                            },
                        )
                    old_premise_id = str(
                        cube._require_consequence(predecessor_id)["premise_assignment_id"]
                    )
                    old_world = assignment_world(old_premise_id)
                    if old_world not in scoped_worlds:
                        raise LacunaError(
                            "turn-world-scope-violation",
                            "consequence replacement targets predecessor custody outside the request grant",
                            {
                                "operation_index": index,
                                "world_id": old_world,
                                "world_scope": scoped_world,
                            },
                        )
                if operation.get("dependent_kind") == "world_assignment":
                    dependent_id = require_id(operation.get("dependent_id"), "dependent_id")
                    dependent_world = assignment_world(dependent_id)
                    if dependent_world not in scoped_worlds:
                        raise LacunaError(
                            "turn-world-scope-violation",
                            "assignment consequence crosses outside the request grant",
                            {
                                "operation_index": index,
                                "world_id": dependent_world,
                                "world_scope": scoped_world,
                            },
                        )
                pending_consequence_premises[
                    require_id(operation.get("consequence_id"), "consequence_id")
                ] = premise_id
            elif op == "retire_consequence":
                consequence_id = require_id(operation.get("consequence_id"), "consequence_id")
                if consequence_id in pending_consequence_premises:
                    premise_id = pending_consequence_premises[consequence_id]
                else:
                    premise_id = str(
                        cube._require_consequence(consequence_id)["premise_assignment_id"]
                    )
                target_world = assignment_world(premise_id)
                if target_world not in scoped_worlds:
                    raise LacunaError(
                        "turn-world-scope-violation",
                        "consequence retirement targets custody outside the request grant",
                        {
                            "operation_index": index,
                            "world_id": target_world,
                            "world_scope": scoped_world,
                        },
                    )
            elif op == "link_evidence":
                target_world = operation.get("world_id")
                if target_world is None or target_world not in scoped_worlds:
                    raise LacunaError(
                        "turn-world-scope-violation",
                        "a world-scoped director turn may link evidence only inside its scoped world or descendants",
                        {
                            "operation_index": index,
                            "world_id": target_world,
                            "world_scope": scoped_world,
                        },
                    )



def _validate_disclosures(
    cube: Cube,
    *,
    audience_id: str,
    narration_source_id: str,
    operations: list[dict[str, Any]],
    reveals: list[str],
) -> None:
    new_assertions: dict[str, dict[str, Any]] = {}
    ended_assertions: set[str] = set()
    narration_visible_assertions: set[str] = set()
    for operation in operations:
        if operation["op"] == "record_assertion":
            view = _operation_assertion_view(operation)
            assertion_id = view["assertion_id"]
            new_assertions[assertion_id] = view
            if operation.get("supersedes_id") is not None:
                ended_assertions.add(require_id(operation["supersedes_id"], "supersedes_id"))
            if (
                view["source_id"] == narration_source_id
                and Cube.assertion_visible_to(view, audience_id)
            ):
                narration_visible_assertions.add(assertion_id)
        elif operation["op"] == "supersede_assertion":
            ended_assertions.add(require_id(operation.get("assertion_id"), "assertion_id"))

    reveal_set = set(reveals)
    missing_declarations = narration_visible_assertions - reveal_set
    if missing_declarations:
        raise LacunaError(
            "undeclared-narration-disclosure",
            "audience-visible assertions sourced from narration must be declared in revealed_assertion_ids",
            {"assertion_ids": sorted(missing_declarations)},
        )

    for assertion_id in reveals:
        if assertion_id in ended_assertions:
            raise LacunaError(
                "ended-disclosure",
                f"revealed assertion {assertion_id!r} is ended by the same turn",
            )
        if assertion_id in new_assertions:
            assertion = new_assertions[assertion_id]
            if assertion["source_id"] != narration_source_id:
                raise LacunaError(
                    "unbound-narration-disclosure",
                    "a newly revealed assertion must cite the narration source",
                    {"assertion_id": assertion_id, "expected_source_id": narration_source_id},
                )
        else:
            assertion = cube.assertion(assertion_id, active=True)
        if not Cube.assertion_visible_to(assertion, audience_id):
            raise LacunaError(
                "invisible-narration-disclosure",
                "revealed assertion is not visible to the named audience",
                {"assertion_id": assertion_id, "audience_id": audience_id},
            )


def _strict_turn_mapping(
    value: Any,
    *,
    label: str,
    fields: set[str],
    code: str,
) -> dict[str, Any]:
    try:
        document = require_mapping(value, label)
    except ValueError as exc:
        raise LacunaError(code, str(exc)) from exc
    unexpected = sorted(set(document) - fields)
    missing = sorted(fields - set(document))
    if unexpected or missing:
        raise LacunaError(
            code,
            f"{label} has an invalid field set",
            {"unexpected": unexpected, "missing": missing},
        )
    return document


def _build_turn_change_material(
    cube: Cube,
    document: dict[str, Any],
    *,
    include_planner_context: bool,
) -> dict[str, Any]:
    """Validate a proposal and derive its one deterministic kernel change-set."""
    proposal = require_mapping(document, "turn proposal")
    unexpected = sorted(set(proposal) - TURN_PROPOSAL_FIELDS)
    if unexpected:
        raise LacunaError(
            "unexpected-turn-field",
            "turn proposal contains unrecognized fields",
            {"fields": unexpected},
        )
    if proposal.get("schema") != TURN_PROPOSAL_SCHEMA:
        raise LacunaError(
            "bad-turn-schema",
            f"schema must be {TURN_PROPOSAL_SCHEMA!r}; legacy v1 proposals are intentionally not accepted because they carry no source-backed write grant",
        )

    request_id = require_id(proposal.get("request_id"), "request_id")
    request_source_id = require_id(proposal.get("request_source_id"), "request_source_id")
    request = _load_turn_request(cube, request_source_id)
    proposal_id = require_id(proposal.get("proposal_id"), "proposal_id")
    actor_id = require_id(proposal.get("actor_id"), "actor_id")
    audience_id = require_id(proposal.get("audience_id"), "audience_id")
    narration_source_id = require_id(proposal.get("narration_source_id"), "narration_source_id")
    expected_head = require_string(proposal.get("expected_head"), "expected_head", max_len=64)
    player_input_sha256 = require_string(
        proposal.get("player_input_sha256"), "player_input_sha256", max_len=64
    )
    if not SHA256_RE.fullmatch(expected_head):
        raise LacunaError("bad-expected-head", "expected_head must be a lowercase SHA-256 digest")
    if not SHA256_RE.fullmatch(player_input_sha256):
        raise LacunaError(
            "bad-player-input-digest",
            "player_input_sha256 must be a lowercase SHA-256 digest",
        )

    bound_fields = {
        "request_id": request_id,
        "request_source_id": request_source_id,
        "proposal_id": proposal_id,
        "actor_id": actor_id,
        "audience_id": audience_id,
        "narration_source_id": narration_source_id,
        "player_input_sha256": player_input_sha256,
    }
    expected_fields = {
        "request_id": request["request_id"],
        "request_source_id": request_source_id,
        "proposal_id": request["proposal_id"],
        "actor_id": request["actor_id"],
        "audience_id": request["audience_id"],
        "narration_source_id": request["narration_source_id"],
        "player_input_sha256": request["player_input_sha256"],
    }
    mismatches = {
        field: {"expected": expected_fields[field], "actual": value}
        for field, value in bound_fields.items()
        if value != expected_fields[field]
    }
    if mismatches:
        raise LacunaError(
            "turn-request-binding-mismatch",
            "proposal identity or authority fields do not match the source-backed turn request",
            {"mismatches": mismatches},
        )
    if expected_head != request["request_head"]:
        raise LacunaError(
            "turn-request-head-mismatch",
            "proposal expected_head is not the event hash that issued its turn request",
            {"expected_request_head": request["request_head"], "actual": expected_head},
        )
    if cube.head() != expected_head:
        raise LacunaError(
            "stale-head",
            "turn proposal expected_head does not match the cube head",
            {"expected_head": expected_head, "actual_head": cube.head()},
        )
    if include_planner_context and request["access_mode"] != "director":
        raise LacunaError(
            "planner-context-not-granted",
            "an audience-profile request cannot return privileged planner context",
        )

    cube._require_agent(actor_id, "actor_id")
    cube._require_agent(audience_id, "audience_id")
    narration = require_string(proposal.get("narration"), "narration", max_len=50000)
    if narration == TURN_NARRATION_PLACEHOLDER:
        raise LacunaError(
            "unreplaced-narration-template",
            "turn proposal still contains the fail-closed narration placeholder",
        )
    message = optional_string(proposal.get("message"), "message", max_len=4096)
    raw_operations = require_list(proposal.get("operations"), "operations")
    grant = request["write_grant"]
    if len(raw_operations) > grant["max_operations"]:
        raise LacunaError(
            "turn-too-large",
            f"this turn grant permits at most {grant['max_operations']} operations plus its narration source",
        )
    raw_reveals = require_list(proposal.get("revealed_assertion_ids"), "revealed_assertion_ids")
    if len(raw_reveals) > grant["max_reveals"]:
        raise LacunaError(
            "too-many-disclosures",
            f"this turn grant permits at most {grant['max_reveals']} revealed assertions",
        )
    if cube._exists("sources", "source_id", narration_source_id):
        raise LacunaError("duplicate-source", f"source {narration_source_id!r} already exists")

    initial_aliases = {
        "input": request_source_id,
        "narration": narration_source_id,
        "audience": audience_id,
        "actor": actor_id,
    }
    operations, aliases = normalize_turn_operations(
        raw_operations,
        initial_aliases=initial_aliases,
        id_seed=proposal_id,
    )
    reveals = _normalize_reveals(raw_reveals, aliases)
    _validate_disclosures(
        cube,
        audience_id=audience_id,
        narration_source_id=narration_source_id,
        operations=operations,
        reveals=reveals,
    )
    _validate_turn_write_grant(
        cube,
        grant=grant,
        audience_id=audience_id,
        operations=operations,
    )

    narration_digest = sha256_text(narration)
    source_operation = {
        "op": "add_source",
        "source_id": narration_source_id,
        "kind": "utterance",
        "label": f"Narration for {proposal_id}",
        "locator": f"lacuna:turn:{proposal_id}:narration",
        "content_sha256": narration_digest,
        "metadata": {
            "proposal_id": proposal_id,
            "request_id": request_id,
            "request_source_id": request_source_id,
            "request_head": request["request_head"],
            "player_input_sha256": player_input_sha256,
            "audience_id": audience_id,
            "access_mode": request["access_mode"],
            "world_scope": grant["world_scope"],
            "grant_profile": grant["profile"],
            "presentation_only": True,
            "content_retained_by_lacuna": False,
        },
    }
    change_set = {
        "schema": "lacuna.change-set.v1",
        "change_id": proposal_id,
        "actor_id": actor_id,
        "expected_head": expected_head,
        "message": message or f"commit narrated turn {proposal_id}",
        "operations": [source_operation, *operations],
    }
    return {
        "proposal": proposal,
        "proposal_sha256": sha256_text(canonical_json(proposal)),
        "request": request,
        "request_id": request_id,
        "request_source_id": request_source_id,
        "request_head": request["request_head"],
        "player_input_sha256": player_input_sha256,
        "proposal_id": proposal_id,
        "actor_id": actor_id,
        "audience_id": audience_id,
        "access_mode": request["access_mode"],
        "write_grant": grant,
        "narration_source_id": narration_source_id,
        "narration_sha256": narration_digest,
        "narration": narration,
        "revealed_assertion_ids": reveals,
        "bindings": aliases,
        "change_set": change_set,
        "change_payload_sha256": sha256_text(canonical_json(change_set)),
        "include_planner_context": bool(include_planner_context),
    }


def _turn_contexts(cube: Cube, material: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any] | None]:
    audience_context = build_context(cube, agent_id=material["audience_id"])
    planner_context = (
        build_context(cube, world_id=material["write_grant"]["world_scope"])
        if material["include_planner_context"] and material["access_mode"] == "director"
        else None
    )
    return audience_context, planner_context


def _validate_prepared_event_chain(
    preparation: dict[str, Any],
) -> list[str]:
    change = _strict_turn_mapping(
        preparation.get("change"),
        label="turn preparation change receipt",
        fields=CHANGE_RECEIPT_FIELDS,
        code="bad-turn-preparation",
    )
    if (
        change.get("event") != "lacuna.change.applied"
        or change.get("schema") != "lacuna.change-receipt.v1"
        or change.get("overall_status") != "pass"
    ):
        raise LacunaError("bad-turn-preparation", "prepared change receipt contract is invalid")
    event_ids = require_list(change.get("event_ids"), "change.event_ids")
    normalized_event_ids = [
        require_id(value, f"change.event_ids[{index}]")
        for index, value in enumerate(event_ids)
    ]
    if len(set(normalized_event_ids)) != len(normalized_event_ids):
        raise LacunaError("bad-turn-preparation", "prepared change event identifiers are not unique")
    if change.get("change_id") != preparation.get("proposal_id"):
        raise LacunaError("bad-turn-preparation", "prepared change_id differs from proposal_id")
    if change.get("actor_id") != preparation.get("actor_id"):
        raise LacunaError("bad-turn-preparation", "prepared change actor differs from the proposal actor")
    if change.get("cube_id") != preparation.get("cube_id"):
        raise LacunaError("bad-turn-preparation", "prepared change cube differs from the preparation")
    if change.get("before_head") != preparation.get("request_head"):
        raise LacunaError("bad-turn-preparation", "prepared change begins at the wrong request head")
    if change.get("after_head") != preparation.get("head"):
        raise LacunaError("bad-turn-preparation", "prepared change receipt and head disagree")
    if change.get("applied_at") != preparation.get("prepared_at"):
        raise LacunaError("bad-turn-preparation", "prepared change timestamp is not frozen")
    operation_count = change.get("operation_count")
    if isinstance(operation_count, bool) or not isinstance(operation_count, int) or operation_count < 1:
        raise LacunaError("bad-turn-preparation", "prepared operation_count must be a positive integer")
    if operation_count != len(normalized_event_ids):
        raise LacunaError("bad-turn-preparation", "prepared operation and event counts disagree")

    raw_chain = require_list(preparation.get("event_chain"), "event_chain")
    if len(raw_chain) != len(normalized_event_ids):
        raise LacunaError("bad-turn-preparation", "prepared event chain length is invalid")
    previous_hash = preparation["request_head"]
    previous_seq: int | None = None
    for index, raw_event in enumerate(raw_chain):
        event = _strict_turn_mapping(
            raw_event,
            label=f"event_chain[{index}]",
            fields=EVENT_CHAIN_FIELDS,
            code="bad-turn-preparation",
        )
        seq = event.get("seq")
        if isinstance(seq, bool) or not isinstance(seq, int) or seq < 1:
            raise LacunaError("bad-turn-preparation", f"event_chain[{index}].seq must be positive")
        if previous_seq is not None and seq != previous_seq + 1:
            raise LacunaError("bad-turn-preparation", "prepared event sequence is not contiguous")
        previous_seq = seq
        if event.get("event_id") != normalized_event_ids[index]:
            raise LacunaError("bad-turn-preparation", "prepared event identifiers are out of order")
        require_id(event.get("event_id"), f"event_chain[{index}].event_id")
        if event.get("change_id") != preparation["proposal_id"]:
            raise LacunaError("bad-turn-preparation", "prepared event belongs to another change")
        if event.get("actor_id") != preparation["actor_id"]:
            raise LacunaError("bad-turn-preparation", "prepared event actor differs from the proposal actor")
        if event.get("schema_version") != EVENT_SCHEMA_VERSION:
            raise LacunaError("bad-turn-preparation", "prepared event schema version is unsupported")
        if event.get("recorded_at") != preparation["prepared_at"]:
            raise LacunaError("bad-turn-preparation", "prepared event timestamp is not frozen")
        if not isinstance(event.get("event_type"), str) or not event["event_type"]:
            raise LacunaError("bad-turn-preparation", "prepared event type is invalid")
        if not isinstance(event.get("payload"), dict):
            raise LacunaError("bad-turn-preparation", "prepared event payload must be an object")
        if event.get("prev_hash") != previous_hash:
            raise LacunaError("bad-turn-preparation", "prepared event hash chain is discontinuous")
        event_hash = event.get("event_hash")
        if not isinstance(event_hash, str) or not SHA256_RE.fullmatch(event_hash):
            raise LacunaError("bad-turn-preparation", "prepared event hash is invalid")
        core = {key: event[key] for key in EVENT_CHAIN_FIELDS if key != "event_hash"}
        if sha256_text(canonical_json(core)) != event_hash:
            raise LacunaError("bad-turn-preparation", "prepared event does not match its hash")
        previous_hash = event_hash
    if previous_hash != preparation["head"]:
        raise LacunaError("bad-turn-preparation", "prepared event chain does not terminate at head")
    return normalized_event_ids


def _compare_exact(label: str, expected: Any, actual: Any, code: str) -> None:
    if canonical_json(expected) != canonical_json(actual):
        raise LacunaError(
            code,
            f"{label} differs from the exact kernel rehearsal",
            {
                "expected_sha256": sha256_text(canonical_json(expected)),
                "actual_sha256": sha256_text(canonical_json(actual)),
            },
        )


def _validate_turn_preparation_at_request_head(
    cube: Cube,
    preparation: dict[str, Any],
    proposal: dict[str, Any],
    *,
    include_planner_context: bool,
) -> dict[str, Any]:
    material = _build_turn_change_material(
        cube,
        proposal,
        include_planner_context=include_planner_context,
    )
    expected_fields = {
        "cube_id": cube.meta("cube_id"),
        "proposal_sha256": material["proposal_sha256"],
        "include_planner_context": bool(include_planner_context),
        "request_id": material["request_id"],
        "request_source_id": material["request_source_id"],
        "request_head": material["request_head"],
        "player_input_sha256": material["player_input_sha256"],
        "proposal_id": material["proposal_id"],
        "actor_id": material["actor_id"],
        "audience_id": material["audience_id"],
        "access_mode": material["access_mode"],
        "write_grant": material["write_grant"],
        "narration_source_id": material["narration_source_id"],
        "narration_sha256": material["narration_sha256"],
        "narration": material["narration"],
        "revealed_assertion_ids": material["revealed_assertion_ids"],
        "bindings": material["bindings"],
        "change_set": material["change_set"],
        "change_payload_sha256": material["change_payload_sha256"],
        "nonclaims": TURN_PREPARATION_NONCLAIMS,
    }
    mismatches = {
        field: {
            "expected_sha256": sha256_text(canonical_json(expected)),
            "actual_sha256": sha256_text(canonical_json(preparation.get(field))),
        }
        for field, expected in expected_fields.items()
        if canonical_json(preparation.get(field)) != canonical_json(expected)
    }
    if mismatches:
        raise LacunaError(
            "turn-preparation-binding-mismatch",
            "turn preparation is not bound to the exact proposal and request grant",
            {"mismatches": mismatches},
        )
    prepared_at = require_string(preparation.get("prepared_at"), "prepared_at", max_len=128)
    if not isinstance(preparation.get("include_planner_context"), bool):
        raise LacunaError("bad-turn-preparation", "include_planner_context must be boolean")
    if not isinstance(preparation.get("audience_context"), dict):
        raise LacunaError("bad-turn-preparation", "audience_context must be an object")
    if preparation.get("planner_context") is not None and not isinstance(
        preparation.get("planner_context"), dict
    ):
        raise LacunaError("bad-turn-preparation", "planner_context must be an object or null")
    event_ids = _validate_prepared_event_chain(preparation)

    def inspect() -> dict[str, Any]:
        audience_context, planner_context = _turn_contexts(cube, material)
        return {
            "event_chain": cube.change_event_chain(material["proposal_id"]),
            "audience_context": audience_context,
            "planner_context": planner_context,
        }

    receipt, inspection = cube.preview_changeset(
        material["change_set"],
        recorded_at=prepared_at,
        event_ids=event_ids,
        after_apply=inspect,
    )
    _compare_exact(
        "prepared change receipt",
        receipt,
        preparation["change"],
        "turn-preparation-change-mismatch",
    )
    _compare_exact(
        "prepared event chain",
        inspection["event_chain"],
        preparation["event_chain"],
        "turn-preparation-event-chain-mismatch",
    )
    _compare_exact(
        "prepared audience context",
        inspection["audience_context"],
        preparation["audience_context"],
        "turn-preparation-context-mismatch",
    )
    _compare_exact(
        "prepared planner context",
        inspection["planner_context"],
        preparation["planner_context"],
        "turn-preparation-context-mismatch",
    )
    if preparation.get("head") != receipt["after_head"]:
        raise LacunaError("bad-turn-preparation", "preparation head differs from rehearsed after_head")
    if cube.head() != material["request_head"]:
        raise LacunaError(
            "turn-preview-leaked-mutation",
            "rollback rehearsal changed the cube head",
            {"expected": material["request_head"], "actual": cube.head()},
        )
    return preparation


def validate_turn_preparation(
    cube: Cube,
    document: dict[str, Any],
    proposal: dict[str, Any],
    *,
    include_planner_context: bool,
) -> dict[str, Any]:
    """Authenticate a preparation by replaying it on the request-head ledger prefix."""
    preparation = _strict_turn_mapping(
        document,
        label="turn preparation",
        fields=TURN_PREPARATION_FIELDS,
        code="bad-turn-preparation",
    )
    if (
        preparation.get("event") != "lacuna.turn.prepared"
        or preparation.get("schema") != TURN_PREPARATION_SCHEMA
        or preparation.get("overall_status") != "pass"
    ):
        raise LacunaError("bad-turn-preparation", "turn preparation contract is invalid")
    if preparation.get("cube_id") != cube.meta("cube_id"):
        raise LacunaError("turn-preparation-cube-mismatch", "preparation belongs to another cube")
    for field in ("proposal_sha256", "player_input_sha256", "change_payload_sha256", "request_head", "head"):
        digest = preparation.get(field)
        if not isinstance(digest, str) or not SHA256_RE.fullmatch(digest):
            raise LacunaError("bad-turn-preparation", f"{field} must be a lowercase SHA-256 digest")
    proposal_mapping = require_mapping(proposal, "turn proposal")
    expected_head = require_string(proposal_mapping.get("expected_head"), "expected_head", max_len=64)
    if cube.head() == expected_head:
        return _validate_turn_preparation_at_request_head(
            cube,
            preparation,
            proposal_mapping,
            include_planner_context=include_planner_context,
        )
    with cube.snapshot_at_head(expected_head) as historical:
        return _validate_turn_preparation_at_request_head(
            historical,
            preparation,
            proposal_mapping,
            include_planner_context=include_planner_context,
        )


def prepare_turn_proposal(
    cube: Cube,
    document: dict[str, Any],
    *,
    include_planner_context: bool = False,
) -> dict[str, Any]:
    """Rehearse one exact turn through the kernel and roll the transaction back."""
    material = _build_turn_change_material(
        cube,
        document,
        include_planner_context=include_planner_context,
    )
    prepared_at = utc_now()
    event_ids = [new_id("evt") for _ in material["change_set"]["operations"]]

    def inspect() -> dict[str, Any]:
        audience_context, planner_context = _turn_contexts(cube, material)
        return {
            "event_chain": cube.change_event_chain(material["proposal_id"]),
            "audience_context": audience_context,
            "planner_context": planner_context,
        }

    change_receipt, inspection = cube.preview_changeset(
        material["change_set"],
        recorded_at=prepared_at,
        event_ids=event_ids,
        after_apply=inspect,
    )
    preparation = {
        "event": "lacuna.turn.prepared",
        "schema": TURN_PREPARATION_SCHEMA,
        "overall_status": "pass",
        "cube_id": cube.meta("cube_id"),
        "prepared_at": prepared_at,
        "proposal_sha256": material["proposal_sha256"],
        "include_planner_context": bool(include_planner_context),
        "request_id": material["request_id"],
        "request_source_id": material["request_source_id"],
        "request_head": material["request_head"],
        "player_input_sha256": material["player_input_sha256"],
        "proposal_id": material["proposal_id"],
        "actor_id": material["actor_id"],
        "audience_id": material["audience_id"],
        "access_mode": material["access_mode"],
        "write_grant": material["write_grant"],
        "narration_source_id": material["narration_source_id"],
        "narration_sha256": material["narration_sha256"],
        "narration": material["narration"],
        "revealed_assertion_ids": material["revealed_assertion_ids"],
        "bindings": material["bindings"],
        "change_set": material["change_set"],
        "change_payload_sha256": material["change_payload_sha256"],
        "change": change_receipt,
        "event_chain": inspection["event_chain"],
        "head": change_receipt["after_head"],
        "audience_context": inspection["audience_context"],
        "planner_context": inspection["planner_context"],
        "nonclaims": TURN_PREPARATION_NONCLAIMS,
    }
    return validate_turn_preparation(
        cube,
        preparation,
        material["proposal"],
        include_planner_context=include_planner_context,
    )


def _turn_receipt_from_preparation(
    preparation: dict[str, Any],
    *,
    delivery_mode: str,
    historical_snapshot_used: bool,
) -> dict[str, Any]:
    return {
        "event": "lacuna.turn.committed",
        "schema": TURN_RECEIPT_SCHEMA,
        "overall_status": "pass",
        "cube_id": preparation["cube_id"],
        "preparation_sha256": sha256_text(canonical_json(preparation)),
        "prepared_at": preparation["prepared_at"],
        "request_id": preparation["request_id"],
        "request_source_id": preparation["request_source_id"],
        "request_head": preparation["request_head"],
        "player_input_sha256": preparation["player_input_sha256"],
        "proposal_id": preparation["proposal_id"],
        "actor_id": preparation["actor_id"],
        "audience_id": preparation["audience_id"],
        "access_mode": preparation["access_mode"],
        "write_grant": preparation["write_grant"],
        "narration_source_id": preparation["narration_source_id"],
        "narration_sha256": preparation["narration_sha256"],
        "narration": preparation["narration"],
        "revealed_assertion_ids": preparation["revealed_assertion_ids"],
        "bindings": preparation["bindings"],
        "change": preparation["change"],
        "head": preparation["head"],
        "audience_context": preparation["audience_context"],
        "planner_context": preparation["planner_context"],
        "delivery": {
            "mode": delivery_mode,
            "materialized_at": utc_now(),
            "historical_snapshot_used": bool(historical_snapshot_used),
        },
        "nonclaims": TURN_RECEIPT_NONCLAIMS,
    }


def validate_turn_receipt(
    document: dict[str, Any],
    proposal: dict[str, Any],
    preparation: dict[str, Any],
) -> dict[str, Any]:
    receipt = _strict_turn_mapping(
        document,
        label="turn receipt",
        fields=TURN_RECEIPT_FIELDS,
        code="bad-turn-receipt",
    )
    expected = _turn_receipt_from_preparation(
        preparation,
        delivery_mode=(receipt.get("delivery") or {}).get("mode", "invalid")
        if isinstance(receipt.get("delivery"), dict)
        else "invalid",
        historical_snapshot_used=(receipt.get("delivery") or {}).get(
            "historical_snapshot_used", False
        )
        if isinstance(receipt.get("delivery"), dict)
        else False,
    )
    # Materialization time is intentionally fresh; compare every other field.
    expected["delivery"] = receipt.get("delivery")
    mismatches = {
        key: {
            "expected_sha256": sha256_text(canonical_json(value)),
            "actual_sha256": sha256_text(canonical_json(receipt.get(key))),
        }
        for key, value in expected.items()
        if canonical_json(value) != canonical_json(receipt.get(key))
    }
    if mismatches:
        raise LacunaError(
            "turn-receipt-binding-mismatch",
            "turn receipt is not bound to its exact preparation",
            {"mismatches": mismatches},
        )
    if sha256_text(canonical_json(proposal)) != preparation["proposal_sha256"]:
        raise LacunaError("turn-receipt-binding-mismatch", "proposal digest differs from preparation")
    delivery = _strict_turn_mapping(
        receipt.get("delivery"),
        label="delivery",
        fields=DELIVERY_FIELDS,
        code="bad-turn-receipt",
    )
    if delivery.get("mode") not in {"direct", "recovered"}:
        raise LacunaError("bad-turn-receipt", "delivery.mode must be direct or recovered")
    require_string(delivery.get("materialized_at"), "delivery.materialized_at", max_len=128)
    if not isinstance(delivery.get("historical_snapshot_used"), bool):
        raise LacunaError("bad-turn-receipt", "historical_snapshot_used must be boolean")
    if delivery["mode"] == "direct" and delivery["historical_snapshot_used"]:
        raise LacunaError("bad-turn-receipt", "direct delivery cannot use historical recovery")
    return receipt


def commit_prepared_turn(
    cube: Cube,
    document: dict[str, Any],
    preparation: dict[str, Any],
    *,
    include_planner_context: bool = False,
) -> dict[str, Any]:
    proposal = require_mapping(document, "turn proposal")
    prepared = validate_turn_preparation(
        cube,
        preparation,
        proposal,
        include_planner_context=include_planner_context,
    )
    if cube.head() != prepared["request_head"]:
        raise LacunaError(
            "stale-head",
            "prepared turn no longer begins at the current cube head",
            {"expected_head": prepared["request_head"], "actual_head": cube.head()},
        )
    if cube.committed_change(prepared["proposal_id"]) is not None:
        raise LacunaError(
            "duplicate-change-id",
            f"change_id {prepared['proposal_id']!r} already exists; use recovery instead of reapplying it",
        )
    event_ids = [event["event_id"] for event in prepared["event_chain"]]

    def inspect_and_bind() -> dict[str, Any]:
        committed = cube.committed_change(prepared["proposal_id"])
        if committed is None:
            raise LacunaError("prepared-change-missing", "prepared change was not visible inside its transaction")
        _compare_exact(
            "committed change payload digest",
            prepared["change_payload_sha256"],
            committed["payload_sha256"],
            "prepared-change-mismatch",
        )
        _compare_exact(
            "committed change receipt",
            prepared["change"],
            committed["change"],
            "prepared-change-mismatch",
        )
        _compare_exact(
            "committed event chain",
            prepared["event_chain"],
            committed["event_chain"],
            "prepared-change-mismatch",
        )
        material = {
            "audience_id": prepared["audience_id"],
            "include_planner_context": prepared["include_planner_context"],
            "access_mode": prepared["access_mode"],
            "write_grant": prepared["write_grant"],
        }
        audience_context, planner_context = _turn_contexts(cube, material)
        _compare_exact(
            "committed audience context",
            prepared["audience_context"],
            audience_context,
            "prepared-post-state-mismatch",
        )
        _compare_exact(
            "committed planner context",
            prepared["planner_context"],
            planner_context,
            "prepared-post-state-mismatch",
        )
        return {"audience_context": audience_context, "planner_context": planner_context}

    change_receipt, _ = cube.apply_prepared_changeset(
        prepared["change_set"],
        recorded_at=prepared["prepared_at"],
        event_ids=event_ids,
        after_apply=inspect_and_bind,
    )
    _compare_exact(
        "committed change receipt",
        prepared["change"],
        change_receipt,
        "prepared-change-mismatch",
    )
    receipt = _turn_receipt_from_preparation(
        prepared,
        delivery_mode="direct",
        historical_snapshot_used=False,
    )
    return validate_turn_receipt(receipt, proposal, prepared)


def recover_prepared_turn_receipt(
    cube: Cube,
    document: dict[str, Any],
    preparation: dict[str, Any],
    *,
    include_planner_context: bool = False,
) -> dict[str, Any]:
    """Materialize a sidecar receipt after the exact prepared DB commit survived."""
    proposal = require_mapping(document, "turn proposal")
    verification = cube.verify()
    if verification["overall_status"] != "pass":
        raise LacunaError(
            "cube-verification-failed",
            "cannot recover a turn receipt from a cube that fails verification",
            verification,
        )
    prepared = validate_turn_preparation(
        cube,
        preparation,
        proposal,
        include_planner_context=include_planner_context,
    )
    committed = cube.committed_change(prepared["proposal_id"])
    if committed is None:
        raise LacunaError(
            "prepared-change-not-committed",
            "the prepared change is not present in the durable ledger",
            {"proposal_id": prepared["proposal_id"]},
        )
    _compare_exact(
        "recovered change payload digest",
        prepared["change_payload_sha256"],
        committed["payload_sha256"],
        "prepared-change-mismatch",
    )
    _compare_exact(
        "recovered change receipt",
        prepared["change"],
        committed["change"],
        "prepared-change-mismatch",
    )
    _compare_exact(
        "recovered event chain",
        prepared["event_chain"],
        committed["event_chain"],
        "prepared-change-mismatch",
    )
    receipt = _turn_receipt_from_preparation(
        prepared,
        delivery_mode="recovered",
        historical_snapshot_used=cube.head() != prepared["head"],
    )
    return validate_turn_receipt(receipt, proposal, prepared)


def commit_turn_proposal(
    cube: Cube,
    document: dict[str, Any],
    *,
    include_planner_context: bool = False,
) -> dict[str, Any]:
    """Compatibility entrance: prepare by rollback, then commit the exact envelope."""
    preparation = prepare_turn_proposal(
        cube,
        document,
        include_planner_context=include_planner_context,
    )
    return commit_prepared_turn(
        cube,
        document,
        preparation,
        include_planner_context=include_planner_context,
    )

