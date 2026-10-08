from __future__ import annotations

import json
import math
import os
import re
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Callable, Iterable, Iterator

from . import __version__
from .commitment import (
    COMMITMENT_BASES,
    COMMITMENT_ORDER,
    HARD_COMMITMENT_BASES,
    SOURCE_EXPECTED_BASES,
    WRITABLE_COMMITMENT_BASES,
    CONSEQUENCE_DEPENDENT_KINDS,
    CONSEQUENCE_RELATIONS,
    CONSEQUENCE_SEVERITIES,
    REVISION_GRAPH_MAX_DEPTH,
    REVISION_GRAPH_MAX_NODES,
    assignment_cycle_path,
    calculate_revision_burden,
    is_adjacent_raise,
    is_strict_raise,
)
from .errors import LacunaError
from .logic import (
    RELATION_DESCRIPTIONS,
    RELATION_KINDS,
    cardinality_conflict,
    cardinality_description,
    normalize_relation_endpoints,
    pair_conflict,
)
from .particles import (
    PARTICLE_EPOCH_BOUNDARY_EVENTS,
    PARTICLE_RECONCILIATION_METHOD,
    PARTICLE_RECONCILIATION_POLICY,
    PARTICLE_UPDATE_METHOD,
    build_particle_bank,
    build_particle_bank_from_records,
    compute_factor_reconciliation,
    compute_likelihood_update,
    distribution_statistics,
    factor_reconciliation_blockers,
    particle_bank_sha256,
    particle_factor_set_sha256,
    particle_reconciliation_review_sha256,
    valuation_likelihood_divergence_groups,
)
from .seals import (
    SEAL_PURPOSES,
    SEAL_SCHEME,
    SEAL_VISIBILITIES,
    opening_matches_commitment,
    parse_seal_opening,
    validate_seal_nonce,
    validate_seal_payload,
)
from .util import (
    GENESIS_HASH,
    SHA256_RE,
    canonical_json,
    deterministic_claim_id,
    intervals_overlap,
    new_id,
    normalize_audience,
    optional_id,
    optional_probability,
    optional_string,
    optional_tick,
    pretty_json,
    require_enum,
    require_id,
    require_list,
    require_mapping,
    require_string,
    require_weight,
    sha256_text,
    utc_now,
)

DATABASE_SCHEMA_VERSION = 8
EVENT_SCHEMA_VERSION = 1
SUPPORTED_EVENT_SCHEMA_VERSIONS = {EVENT_SCHEMA_VERSION}
CUBE_CONFIG = "cube.json"
DATABASE_NAME = "lacuna.sqlite3"
CONSEQUENCE_REPAIR_POLICY = "lacuna.consequence-repair.v1"

AGENT_KINDS = {"human", "character", "narrator", "model", "tool", "system", "organization", "other"}
SOURCE_KINDS = {"scene", "utterance", "document", "sensor", "model", "user", "tool", "other"}
CLAIM_SCOPES = {"world", "event", "belief", "meta"}
STANCES = {"true", "false", "unknown"}
BASES = {"observation", "testimony", "inference", "belief", "hypothesis", "commitment", "metadata"}
STANDINGS = {"reported", "accepted", "anchored"}
VISIBILITIES = {"public", "private", "restricted"}
WORLD_STATUSES = {"live", "selected", "pruned", "archived"}
COMMITMENTS = set(COMMITMENT_ORDER)
EVIDENCE_RELATIONS = {"supports", "refutes", "explains", "contextualizes"}
EVENT_TYPES = {
    "cube.created",
    "agent.registered",
    "source.added",
    "claim.declared",
    "claim_relation.declared",
    "claim_relation.retired",
    "cardinality.declared",
    "cardinality.retired",
    "assertion.recorded",
    "assertion.superseded",
    "world.created",
    "world.assigned",
    "world.revised",
    "world.commitment_raised",
    "world.weight_set",
    "world.status_set",
    "particle.updated",
    "particle.reconciled",
    "evidence.linked",
    "consequence.linked",
    "consequence.replaced",
    "consequence.retired",
    "precommitment.sealed",
    "precommitment.revealed",
    "precommitment.voided",
    "question.opened",
    "question.closed",
}

CUBE_CONFIG_FIELDS = {"schema", "project", "project_version", "cube_id", "created_at", "database"}
CHANGESET_FIELDS = {"schema", "change_id", "actor_id", "expected_head", "message", "operations"}
OPERATION_FIELDS: dict[str, set[str]] = {
    "register_agent": {"op", "agent_id", "kind", "label", "metadata"},
    "add_source": {"op", "source_id", "kind", "label", "locator", "content_sha256", "metadata"},
    "declare_claim": {"op", "claim_id", "subject", "predicate", "object", "scope"},
    "declare_relation": {
        "op", "relation_id", "left_claim_id", "right_claim_id", "relation", "source_id", "rationale",
    },
    "retire_relation": {"op", "relation_id", "reason"},
    "declare_cardinality": {
        "op", "constraint_id", "label", "claim_ids", "min_true", "max_true", "source_id", "rationale",
    },
    "retire_cardinality": {"op", "constraint_id", "reason"},
    "record_assertion": {
        "op", "assertion_id", "claim_id", "assertor_id", "perspective_id", "source_id",
        "stance", "basis", "standing", "confidence", "visibility", "audience",
        "timeline_id", "valid_from", "valid_to", "note", "supersedes_id",
    },
    "supersede_assertion": {"op", "assertion_id", "reason"},
    "create_world": {"op", "world_id", "label", "parent_world_id", "status", "weight", "rationale"},
    "assign_world": {
        "op", "assignment_id", "world_id", "claim_id", "truth", "commitment",
        "commitment_basis", "commitment_source_id", "confidence", "rationale", "source_assertion_id",
        "timeline_id", "valid_from", "valid_to",
    },
    "revise_world": {
        "op", "assignment_id", "revises_assignment_id", "truth", "commitment",
        "commitment_basis", "commitment_source_id", "confidence", "rationale", "source_assertion_id",
        "expected_impact_sha256", "reason",
    },
    "raise_commitment": {
        "op", "transition_id", "assignment_id", "commitment", "basis",
        "source_id", "rationale",
    },
    "set_world_weight": {"op", "world_id", "weight", "reason"},
    "set_world_status": {"op", "world_id", "status", "reason"},
    "update_particle_bank": {
        "op", "update_id", "evidence_assertion_id", "expected_bank_sha256",
        "assessments", "reason",
    },
    "reconcile_particle_bank": {
        "op", "reconciliation_id", "expected_reconciliation_sha256", "reason",
    },
    "link_evidence": {
        "op", "link_id", "evidence_assertion_id", "target_claim_id", "world_id",
        "relation", "strength", "rationale",
    },
    "link_consequence": {
        "op", "consequence_id", "premise_assignment_id", "dependent_kind",
        "dependent_id", "relation", "severity", "source_id", "rationale",
    },
    "replace_consequence": {
        "op", "repair_id", "consequence_id", "replaces_consequence_id",
        "premise_assignment_id", "dependent_kind", "dependent_id", "relation",
        "severity", "source_id", "rationale", "expected_repair_sha256", "reason",
    },
    "retire_consequence": {"op", "consequence_id", "reason"},
    "seal_precommitment": {
        "op", "seal_id", "commitment_sha256", "scheme", "label", "purpose",
        "visibility", "audience", "source_id",
    },
    "reveal_precommitment": {"op", "seal_id", "nonce", "payload", "reason"},
    "void_precommitment": {"op", "seal_id", "reason"},
    "open_question": {
        "op", "question_id", "text", "about_claim_id", "opened_by", "visibility", "audience",
    },
    "close_question": {"op", "question_id", "resolution_assertion_id", "reason"},
}

SCHEMA_SQL = """
PRAGMA user_version = 8;

CREATE TABLE IF NOT EXISTS meta (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS schema_migrations (
    target_version INTEGER PRIMARY KEY,
    source_version INTEGER NOT NULL,
    applied_at TEXT NOT NULL,
    runtime_version TEXT NOT NULL,
    migration_sha256 TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS events (
    seq INTEGER PRIMARY KEY,
    event_id TEXT NOT NULL UNIQUE,
    change_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    schema_version INTEGER NOT NULL,
    actor_id TEXT NOT NULL,
    recorded_at TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    prev_hash TEXT NOT NULL,
    event_hash TEXT NOT NULL UNIQUE
);

CREATE INDEX IF NOT EXISTS events_change_idx ON events(change_id, seq);
CREATE INDEX IF NOT EXISTS events_type_idx ON events(event_type, seq);

CREATE TABLE IF NOT EXISTS changesets (
    change_id TEXT PRIMARY KEY,
    actor_id TEXT NOT NULL,
    message TEXT,
    expected_head TEXT NOT NULL,
    before_head TEXT NOT NULL,
    after_head TEXT NOT NULL,
    operation_count INTEGER NOT NULL,
    applied_at TEXT NOT NULL,
    payload_sha256 TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS agents (
    agent_id TEXT PRIMARY KEY,
    kind TEXT NOT NULL,
    label TEXT NOT NULL,
    metadata_json TEXT NOT NULL,
    created_seq INTEGER NOT NULL,
    retired_seq INTEGER
);

CREATE TABLE IF NOT EXISTS sources (
    source_id TEXT PRIMARY KEY,
    kind TEXT NOT NULL,
    label TEXT NOT NULL,
    locator TEXT,
    content_sha256 TEXT,
    metadata_json TEXT NOT NULL,
    created_seq INTEGER NOT NULL,
    retired_seq INTEGER
);

CREATE TABLE IF NOT EXISTS claims (
    claim_id TEXT PRIMARY KEY,
    subject TEXT NOT NULL,
    predicate TEXT NOT NULL,
    object_json TEXT NOT NULL,
    scope TEXT NOT NULL,
    created_seq INTEGER NOT NULL,
    UNIQUE(subject, predicate, object_json, scope)
);

CREATE TABLE IF NOT EXISTS claim_relations (
    relation_id TEXT PRIMARY KEY,
    left_claim_id TEXT NOT NULL REFERENCES claims(claim_id),
    right_claim_id TEXT NOT NULL REFERENCES claims(claim_id),
    relation TEXT NOT NULL,
    source_id TEXT REFERENCES sources(source_id),
    rationale TEXT,
    created_seq INTEGER NOT NULL,
    ended_seq INTEGER,
    retirement_reason TEXT
);

CREATE INDEX IF NOT EXISTS claim_relations_left_idx
    ON claim_relations(left_claim_id, ended_seq);
CREATE INDEX IF NOT EXISTS claim_relations_right_idx
    ON claim_relations(right_claim_id, ended_seq);
CREATE UNIQUE INDEX IF NOT EXISTS claim_relations_active_unique_idx
    ON claim_relations(left_claim_id, right_claim_id, relation)
    WHERE ended_seq IS NULL;

CREATE TABLE IF NOT EXISTS cardinality_constraints (
    constraint_id TEXT PRIMARY KEY,
    label TEXT NOT NULL,
    min_true INTEGER NOT NULL,
    max_true INTEGER NOT NULL,
    member_count INTEGER NOT NULL,
    definition_sha256 TEXT NOT NULL,
    source_id TEXT REFERENCES sources(source_id),
    rationale TEXT NOT NULL,
    created_seq INTEGER NOT NULL,
    ended_seq INTEGER,
    retirement_reason TEXT
);

CREATE UNIQUE INDEX IF NOT EXISTS cardinality_constraints_active_unique_idx
    ON cardinality_constraints(definition_sha256)
    WHERE ended_seq IS NULL;

CREATE TABLE IF NOT EXISTS cardinality_members (
    constraint_id TEXT NOT NULL REFERENCES cardinality_constraints(constraint_id),
    claim_id TEXT NOT NULL REFERENCES claims(claim_id),
    ordinal INTEGER NOT NULL,
    created_seq INTEGER NOT NULL,
    PRIMARY KEY(constraint_id, claim_id),
    UNIQUE(constraint_id, ordinal)
);

CREATE INDEX IF NOT EXISTS cardinality_members_claim_idx
    ON cardinality_members(claim_id, constraint_id);

CREATE TABLE IF NOT EXISTS assertions (
    assertion_id TEXT PRIMARY KEY,
    claim_id TEXT NOT NULL REFERENCES claims(claim_id),
    assertor_id TEXT NOT NULL REFERENCES agents(agent_id),
    perspective_id TEXT NOT NULL REFERENCES agents(agent_id),
    source_id TEXT REFERENCES sources(source_id),
    stance TEXT NOT NULL,
    basis TEXT NOT NULL,
    standing TEXT NOT NULL,
    confidence REAL,
    visibility TEXT NOT NULL,
    audience_json TEXT NOT NULL,
    timeline_id TEXT NOT NULL,
    valid_from INTEGER,
    valid_to INTEGER,
    note TEXT,
    supersedes_id TEXT REFERENCES assertions(assertion_id),
    created_seq INTEGER NOT NULL,
    ended_seq INTEGER
);

CREATE INDEX IF NOT EXISTS assertions_claim_idx ON assertions(claim_id, ended_seq);
CREATE INDEX IF NOT EXISTS assertions_perspective_idx ON assertions(perspective_id, ended_seq);
CREATE INDEX IF NOT EXISTS assertions_standing_idx ON assertions(standing, ended_seq);

CREATE TABLE IF NOT EXISTS worlds (
    world_id TEXT PRIMARY KEY,
    label TEXT NOT NULL,
    parent_world_id TEXT REFERENCES worlds(world_id),
    status TEXT NOT NULL,
    weight REAL NOT NULL,
    rationale TEXT,
    created_seq INTEGER NOT NULL
);

CREATE INDEX IF NOT EXISTS worlds_status_idx ON worlds(status, weight DESC);

CREATE TABLE IF NOT EXISTS world_assignments (
    assignment_id TEXT PRIMARY KEY,
    world_id TEXT NOT NULL REFERENCES worlds(world_id),
    claim_id TEXT NOT NULL REFERENCES claims(claim_id),
    truth TEXT NOT NULL,
    commitment TEXT NOT NULL,
    commitment_basis TEXT NOT NULL,
    commitment_source_id TEXT REFERENCES sources(source_id),
    confidence REAL,
    rationale TEXT,
    source_assertion_id TEXT REFERENCES assertions(assertion_id),
    timeline_id TEXT NOT NULL,
    valid_from INTEGER,
    valid_to INTEGER,
    inherited_from_assignment_id TEXT,
    revision_of_assignment_id TEXT REFERENCES world_assignments(assignment_id),
    revision_reason TEXT,
    revision_impact_sha256 TEXT,
    created_seq INTEGER NOT NULL,
    ended_seq INTEGER
);

CREATE INDEX IF NOT EXISTS world_assignments_current_idx
    ON world_assignments(world_id, claim_id, ended_seq);
CREATE INDEX IF NOT EXISTS world_assignments_revision_idx
    ON world_assignments(revision_of_assignment_id);

CREATE TABLE IF NOT EXISTS commitment_transitions (
    transition_id TEXT PRIMARY KEY,
    assignment_id TEXT NOT NULL REFERENCES world_assignments(assignment_id),
    from_commitment TEXT NOT NULL,
    to_commitment TEXT NOT NULL,
    basis TEXT NOT NULL,
    source_id TEXT REFERENCES sources(source_id),
    rationale TEXT NOT NULL,
    created_seq INTEGER NOT NULL
);

CREATE INDEX IF NOT EXISTS commitment_transitions_assignment_idx
    ON commitment_transitions(assignment_id, created_seq);

CREATE TABLE IF NOT EXISTS evidence_links (
    link_id TEXT PRIMARY KEY,
    evidence_assertion_id TEXT NOT NULL REFERENCES assertions(assertion_id),
    target_claim_id TEXT NOT NULL REFERENCES claims(claim_id),
    world_id TEXT REFERENCES worlds(world_id),
    relation TEXT NOT NULL,
    strength REAL,
    rationale TEXT,
    created_seq INTEGER NOT NULL,
    ended_seq INTEGER
);

CREATE INDEX IF NOT EXISTS evidence_target_idx ON evidence_links(target_claim_id, world_id, ended_seq);

CREATE TABLE IF NOT EXISTS particle_updates (
    update_id TEXT PRIMARY KEY,
    evidence_assertion_id TEXT NOT NULL REFERENCES assertions(assertion_id),
    method TEXT NOT NULL,
    prior_bank_sha256 TEXT NOT NULL,
    posterior_bank_sha256 TEXT NOT NULL,
    prior_weight_sum REAL NOT NULL,
    normalization_constant REAL NOT NULL,
    prior_effective_sample_size REAL NOT NULL,
    posterior_effective_sample_size REAL NOT NULL,
    prior_entropy_nats REAL NOT NULL,
    posterior_entropy_nats REAL NOT NULL,
    information_gain_nats REAL NOT NULL,
    reason TEXT NOT NULL,
    created_seq INTEGER NOT NULL
);

CREATE INDEX IF NOT EXISTS particle_updates_evidence_idx
    ON particle_updates(evidence_assertion_id, created_seq);
CREATE UNIQUE INDEX IF NOT EXISTS particle_updates_evidence_unique_idx
    ON particle_updates(evidence_assertion_id);

CREATE TABLE IF NOT EXISTS particle_update_members (
    update_id TEXT NOT NULL REFERENCES particle_updates(update_id),
    world_id TEXT NOT NULL REFERENCES worlds(world_id),
    ordinal INTEGER NOT NULL,
    world_status TEXT NOT NULL,
    prior_weight REAL NOT NULL,
    prior_probability REAL NOT NULL,
    likelihood REAL NOT NULL,
    unnormalized_weight REAL NOT NULL,
    posterior_probability REAL NOT NULL,
    rationale TEXT,
    valuation_sha256 TEXT NOT NULL,
    custody_sha256 TEXT NOT NULL,
    PRIMARY KEY(update_id, world_id),
    UNIQUE(update_id, ordinal)
);

CREATE INDEX IF NOT EXISTS particle_update_members_world_idx
    ON particle_update_members(world_id, update_id);

CREATE TABLE IF NOT EXISTS particle_reconciliations (
    reconciliation_id TEXT PRIMARY KEY,
    method TEXT NOT NULL,
    baseline_update_id TEXT NOT NULL REFERENCES particle_updates(update_id),
    boundary_seq INTEGER,
    prior_bank_sha256 TEXT NOT NULL,
    baseline_bank_sha256 TEXT NOT NULL,
    posterior_bank_sha256 TEXT NOT NULL,
    factor_set_sha256 TEXT NOT NULL,
    review_sha256 TEXT NOT NULL,
    base_weight_sum REAL NOT NULL,
    log_normalization_constant REAL NOT NULL,
    base_effective_sample_size REAL NOT NULL,
    current_effective_sample_size REAL NOT NULL,
    posterior_effective_sample_size REAL NOT NULL,
    base_entropy_nats REAL NOT NULL,
    current_entropy_nats REAL NOT NULL,
    posterior_entropy_nats REAL NOT NULL,
    information_gain_from_base_nats REAL NOT NULL,
    current_to_posterior_total_variation REAL NOT NULL,
    reason TEXT NOT NULL,
    created_seq INTEGER NOT NULL
);

CREATE INDEX IF NOT EXISTS particle_reconciliations_created_idx
    ON particle_reconciliations(created_seq, reconciliation_id);

CREATE TABLE IF NOT EXISTS particle_reconciliation_factors (
    reconciliation_id TEXT NOT NULL REFERENCES particle_reconciliations(reconciliation_id),
    update_id TEXT NOT NULL REFERENCES particle_updates(update_id),
    ordinal INTEGER NOT NULL,
    disposition TEXT NOT NULL,
    evidence_assertion_id TEXT NOT NULL REFERENCES assertions(assertion_id),
    evidence_ended_seq INTEGER,
    exclusion_reason TEXT,
    PRIMARY KEY(reconciliation_id, update_id),
    UNIQUE(reconciliation_id, ordinal)
);

CREATE INDEX IF NOT EXISTS particle_reconciliation_factors_update_idx
    ON particle_reconciliation_factors(update_id, reconciliation_id);

CREATE TABLE IF NOT EXISTS particle_reconciliation_members (
    reconciliation_id TEXT NOT NULL REFERENCES particle_reconciliations(reconciliation_id),
    world_id TEXT NOT NULL REFERENCES worlds(world_id),
    ordinal INTEGER NOT NULL,
    world_status TEXT NOT NULL,
    current_weight REAL NOT NULL,
    current_probability REAL NOT NULL,
    base_weight REAL NOT NULL,
    base_probability REAL NOT NULL,
    log_factor_sum REAL,
    extinguished_by_update_id TEXT REFERENCES particle_updates(update_id),
    posterior_probability REAL NOT NULL,
    valuation_sha256 TEXT NOT NULL,
    custody_sha256 TEXT NOT NULL,
    PRIMARY KEY(reconciliation_id, world_id),
    UNIQUE(reconciliation_id, ordinal)
);

CREATE INDEX IF NOT EXISTS particle_reconciliation_members_world_idx
    ON particle_reconciliation_members(world_id, reconciliation_id);

CREATE TABLE IF NOT EXISTS consequence_links (
    consequence_id TEXT PRIMARY KEY,
    premise_assignment_id TEXT NOT NULL REFERENCES world_assignments(assignment_id),
    dependent_kind TEXT NOT NULL,
    dependent_id TEXT NOT NULL,
    relation TEXT NOT NULL,
    severity TEXT NOT NULL,
    source_id TEXT REFERENCES sources(source_id),
    rationale TEXT NOT NULL,
    created_seq INTEGER NOT NULL,
    ended_seq INTEGER,
    retirement_reason TEXT
);

CREATE INDEX IF NOT EXISTS consequence_links_premise_idx
    ON consequence_links(premise_assignment_id, ended_seq);
CREATE INDEX IF NOT EXISTS consequence_links_dependent_idx
    ON consequence_links(dependent_kind, dependent_id, ended_seq);
CREATE UNIQUE INDEX IF NOT EXISTS consequence_links_active_unique_idx
    ON consequence_links(
        premise_assignment_id, dependent_kind, dependent_id, relation
    ) WHERE ended_seq IS NULL;

CREATE TABLE IF NOT EXISTS consequence_repairs (
    repair_id TEXT PRIMARY KEY,
    predecessor_consequence_id TEXT NOT NULL REFERENCES consequence_links(consequence_id),
    successor_consequence_id TEXT NOT NULL REFERENCES consequence_links(consequence_id),
    reason TEXT NOT NULL,
    review_sha256 TEXT NOT NULL,
    created_seq INTEGER NOT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS consequence_repairs_predecessor_unique_idx
    ON consequence_repairs(predecessor_consequence_id);
CREATE UNIQUE INDEX IF NOT EXISTS consequence_repairs_successor_unique_idx
    ON consequence_repairs(successor_consequence_id);

CREATE TABLE IF NOT EXISTS fair_play_seals (
    seal_id TEXT PRIMARY KEY,
    scheme TEXT NOT NULL,
    commitment_sha256 TEXT NOT NULL UNIQUE,
    label TEXT NOT NULL,
    purpose TEXT NOT NULL,
    visibility TEXT NOT NULL,
    audience_json TEXT NOT NULL,
    source_id TEXT REFERENCES sources(source_id),
    created_seq INTEGER NOT NULL,
    revealed_seq INTEGER,
    reveal_payload_json TEXT,
    reveal_nonce TEXT,
    reveal_reason TEXT,
    voided_seq INTEGER,
    void_reason TEXT
);

CREATE INDEX IF NOT EXISTS fair_play_seals_status_idx
    ON fair_play_seals(revealed_seq, voided_seq, created_seq);

CREATE TABLE IF NOT EXISTS questions (
    question_id TEXT PRIMARY KEY,
    text TEXT NOT NULL,
    about_claim_id TEXT REFERENCES claims(claim_id),
    opened_by TEXT NOT NULL REFERENCES agents(agent_id),
    visibility TEXT NOT NULL,
    audience_json TEXT NOT NULL,
    status TEXT NOT NULL,
    resolution_assertion_id TEXT REFERENCES assertions(assertion_id),
    created_seq INTEGER NOT NULL,
    closed_seq INTEGER
);

CREATE INDEX IF NOT EXISTS questions_status_idx ON questions(status, created_seq);
"""

MIGRATION_1_TO_2_STATEMENTS = (
    """CREATE TABLE IF NOT EXISTS schema_migrations (
           target_version INTEGER PRIMARY KEY,
           source_version INTEGER NOT NULL,
           applied_at TEXT NOT NULL,
           runtime_version TEXT NOT NULL,
           migration_sha256 TEXT NOT NULL
       )""",
    """CREATE TABLE claim_relations (
           relation_id TEXT PRIMARY KEY,
           left_claim_id TEXT NOT NULL REFERENCES claims(claim_id),
           right_claim_id TEXT NOT NULL REFERENCES claims(claim_id),
           relation TEXT NOT NULL,
           source_id TEXT REFERENCES sources(source_id),
           rationale TEXT,
           created_seq INTEGER NOT NULL,
           ended_seq INTEGER,
           retirement_reason TEXT
       )""",
    "CREATE INDEX claim_relations_left_idx ON claim_relations(left_claim_id, ended_seq)",
    "CREATE INDEX claim_relations_right_idx ON claim_relations(right_claim_id, ended_seq)",
    """CREATE UNIQUE INDEX claim_relations_active_unique_idx
       ON claim_relations(left_claim_id, right_claim_id, relation)
       WHERE ended_seq IS NULL""",
)
MIGRATION_1_TO_2_SHA256 = sha256_text(canonical_json(MIGRATION_1_TO_2_STATEMENTS))

MIGRATION_2_TO_3_STATEMENTS = (
    """CREATE TABLE cardinality_constraints (
           constraint_id TEXT PRIMARY KEY,
           label TEXT NOT NULL,
           min_true INTEGER NOT NULL,
           max_true INTEGER NOT NULL,
           member_count INTEGER NOT NULL,
           definition_sha256 TEXT NOT NULL,
           source_id TEXT REFERENCES sources(source_id),
           rationale TEXT NOT NULL,
           created_seq INTEGER NOT NULL,
           ended_seq INTEGER,
           retirement_reason TEXT
       )""",
    """CREATE UNIQUE INDEX cardinality_constraints_active_unique_idx
       ON cardinality_constraints(definition_sha256)
       WHERE ended_seq IS NULL""",
    """CREATE TABLE cardinality_members (
           constraint_id TEXT NOT NULL REFERENCES cardinality_constraints(constraint_id),
           claim_id TEXT NOT NULL REFERENCES claims(claim_id),
           ordinal INTEGER NOT NULL,
           created_seq INTEGER NOT NULL,
           PRIMARY KEY(constraint_id, claim_id),
           UNIQUE(constraint_id, ordinal)
       )""",
    "CREATE INDEX cardinality_members_claim_idx ON cardinality_members(claim_id, constraint_id)",
)
MIGRATION_2_TO_3_SHA256 = sha256_text(canonical_json(MIGRATION_2_TO_3_STATEMENTS))

MIGRATION_3_TO_4_STATEMENTS = (
    "ALTER TABLE world_assignments ADD COLUMN commitment_basis TEXT NOT NULL DEFAULT 'legacy'",
    "ALTER TABLE world_assignments ADD COLUMN commitment_source_id TEXT REFERENCES sources(source_id)",
    "ALTER TABLE world_assignments ADD COLUMN revision_of_assignment_id TEXT REFERENCES world_assignments(assignment_id)",
    "ALTER TABLE world_assignments ADD COLUMN revision_reason TEXT",
    "ALTER TABLE world_assignments ADD COLUMN revision_impact_sha256 TEXT",
    "CREATE INDEX world_assignments_revision_idx ON world_assignments(revision_of_assignment_id)",
    """CREATE TABLE commitment_transitions (
           transition_id TEXT PRIMARY KEY,
           assignment_id TEXT NOT NULL REFERENCES world_assignments(assignment_id),
           from_commitment TEXT NOT NULL,
           to_commitment TEXT NOT NULL,
           basis TEXT NOT NULL,
           source_id TEXT REFERENCES sources(source_id),
           rationale TEXT NOT NULL,
           created_seq INTEGER NOT NULL
       )""",
    """CREATE INDEX commitment_transitions_assignment_idx
       ON commitment_transitions(assignment_id, created_seq)""",
    """CREATE TABLE consequence_links (
           consequence_id TEXT PRIMARY KEY,
           premise_assignment_id TEXT NOT NULL REFERENCES world_assignments(assignment_id),
           dependent_kind TEXT NOT NULL,
           dependent_id TEXT NOT NULL,
           relation TEXT NOT NULL,
           severity TEXT NOT NULL,
           source_id TEXT REFERENCES sources(source_id),
           rationale TEXT NOT NULL,
           created_seq INTEGER NOT NULL,
           ended_seq INTEGER,
           retirement_reason TEXT
       )""",
    """CREATE INDEX consequence_links_premise_idx
       ON consequence_links(premise_assignment_id, ended_seq)""",
    """CREATE INDEX consequence_links_dependent_idx
       ON consequence_links(dependent_kind, dependent_id, ended_seq)""",
    """CREATE UNIQUE INDEX consequence_links_active_unique_idx
       ON consequence_links(
           premise_assignment_id, dependent_kind, dependent_id, relation
       ) WHERE ended_seq IS NULL""",
)
MIGRATION_3_TO_4_SHA256 = sha256_text(canonical_json(MIGRATION_3_TO_4_STATEMENTS))

MIGRATION_4_TO_5_STATEMENTS = (
    """CREATE TABLE consequence_repairs (
           repair_id TEXT PRIMARY KEY,
           predecessor_consequence_id TEXT NOT NULL REFERENCES consequence_links(consequence_id),
           successor_consequence_id TEXT NOT NULL REFERENCES consequence_links(consequence_id),
           reason TEXT NOT NULL,
           review_sha256 TEXT NOT NULL,
           created_seq INTEGER NOT NULL
       )""",
    """CREATE UNIQUE INDEX consequence_repairs_predecessor_unique_idx
       ON consequence_repairs(predecessor_consequence_id)""",
    """CREATE UNIQUE INDEX consequence_repairs_successor_unique_idx
       ON consequence_repairs(successor_consequence_id)""",
)
MIGRATION_4_TO_5_SHA256 = sha256_text(canonical_json(MIGRATION_4_TO_5_STATEMENTS))

MIGRATION_5_TO_6_STATEMENTS = (
    """CREATE TABLE fair_play_seals (
           seal_id TEXT PRIMARY KEY,
           scheme TEXT NOT NULL,
           commitment_sha256 TEXT NOT NULL UNIQUE,
           label TEXT NOT NULL,
           purpose TEXT NOT NULL,
           visibility TEXT NOT NULL,
           audience_json TEXT NOT NULL,
           source_id TEXT REFERENCES sources(source_id),
           created_seq INTEGER NOT NULL,
           revealed_seq INTEGER,
           reveal_payload_json TEXT,
           reveal_nonce TEXT,
           reveal_reason TEXT,
           voided_seq INTEGER,
           void_reason TEXT
       )""",
    """CREATE INDEX fair_play_seals_status_idx
       ON fair_play_seals(revealed_seq, voided_seq, created_seq)""",
)
MIGRATION_5_TO_6_SHA256 = sha256_text(canonical_json(MIGRATION_5_TO_6_STATEMENTS))

# Schema 6 was released from the fair-play branch while a sibling experimental
# branch independently claimed the same version for particle projections.  The
# official schema-6 lineage retains fair-play custody; schema 7 canonically owns
# particle updates and repairs the version collision without rewriting events.
MIGRATION_6_TO_7_STATEMENTS = (
    "DROP TABLE IF EXISTS particle_update_members",
    "DROP TABLE IF EXISTS particle_updates",
    """CREATE TABLE particle_updates (
           update_id TEXT PRIMARY KEY,
           evidence_assertion_id TEXT NOT NULL REFERENCES assertions(assertion_id),
           method TEXT NOT NULL,
           prior_bank_sha256 TEXT NOT NULL,
           posterior_bank_sha256 TEXT NOT NULL,
           prior_weight_sum REAL NOT NULL,
           normalization_constant REAL NOT NULL,
           prior_effective_sample_size REAL NOT NULL,
           posterior_effective_sample_size REAL NOT NULL,
           prior_entropy_nats REAL NOT NULL,
           posterior_entropy_nats REAL NOT NULL,
           information_gain_nats REAL NOT NULL,
           reason TEXT NOT NULL,
           created_seq INTEGER NOT NULL
       )""",
    """CREATE INDEX particle_updates_evidence_idx
       ON particle_updates(evidence_assertion_id, created_seq)""",
    """CREATE UNIQUE INDEX particle_updates_evidence_unique_idx
       ON particle_updates(evidence_assertion_id)""",
    """CREATE TABLE particle_update_members (
           update_id TEXT NOT NULL REFERENCES particle_updates(update_id),
           world_id TEXT NOT NULL REFERENCES worlds(world_id),
           ordinal INTEGER NOT NULL,
           world_status TEXT NOT NULL,
           prior_weight REAL NOT NULL,
           prior_probability REAL NOT NULL,
           likelihood REAL NOT NULL,
           unnormalized_weight REAL NOT NULL,
           posterior_probability REAL NOT NULL,
           rationale TEXT,
           valuation_sha256 TEXT NOT NULL,
           custody_sha256 TEXT NOT NULL,
           PRIMARY KEY(update_id, world_id),
           UNIQUE(update_id, ordinal)
       )""",
    """CREATE INDEX particle_update_members_world_idx
       ON particle_update_members(world_id, update_id)""",
)
MIGRATION_6_TO_7_SHA256 = sha256_text(canonical_json(MIGRATION_6_TO_7_STATEMENTS))

MIGRATION_7_TO_8_STATEMENTS = (
    """CREATE TABLE particle_reconciliations (
           reconciliation_id TEXT PRIMARY KEY,
           method TEXT NOT NULL,
           baseline_update_id TEXT NOT NULL REFERENCES particle_updates(update_id),
           boundary_seq INTEGER,
           prior_bank_sha256 TEXT NOT NULL,
           baseline_bank_sha256 TEXT NOT NULL,
           posterior_bank_sha256 TEXT NOT NULL,
           factor_set_sha256 TEXT NOT NULL,
           review_sha256 TEXT NOT NULL,
           base_weight_sum REAL NOT NULL,
           log_normalization_constant REAL NOT NULL,
           base_effective_sample_size REAL NOT NULL,
           current_effective_sample_size REAL NOT NULL,
           posterior_effective_sample_size REAL NOT NULL,
           base_entropy_nats REAL NOT NULL,
           current_entropy_nats REAL NOT NULL,
           posterior_entropy_nats REAL NOT NULL,
           information_gain_from_base_nats REAL NOT NULL,
           current_to_posterior_total_variation REAL NOT NULL,
           reason TEXT NOT NULL,
           created_seq INTEGER NOT NULL
       )""",
    """CREATE INDEX particle_reconciliations_created_idx
       ON particle_reconciliations(created_seq, reconciliation_id)""",
    """CREATE TABLE particle_reconciliation_factors (
           reconciliation_id TEXT NOT NULL REFERENCES particle_reconciliations(reconciliation_id),
           update_id TEXT NOT NULL REFERENCES particle_updates(update_id),
           ordinal INTEGER NOT NULL,
           disposition TEXT NOT NULL,
           evidence_assertion_id TEXT NOT NULL REFERENCES assertions(assertion_id),
           evidence_ended_seq INTEGER,
           exclusion_reason TEXT,
           PRIMARY KEY(reconciliation_id, update_id),
           UNIQUE(reconciliation_id, ordinal)
       )""",
    """CREATE INDEX particle_reconciliation_factors_update_idx
       ON particle_reconciliation_factors(update_id, reconciliation_id)""",
    """CREATE TABLE particle_reconciliation_members (
           reconciliation_id TEXT NOT NULL REFERENCES particle_reconciliations(reconciliation_id),
           world_id TEXT NOT NULL REFERENCES worlds(world_id),
           ordinal INTEGER NOT NULL,
           world_status TEXT NOT NULL,
           current_weight REAL NOT NULL,
           current_probability REAL NOT NULL,
           base_weight REAL NOT NULL,
           base_probability REAL NOT NULL,
           log_factor_sum REAL,
           extinguished_by_update_id TEXT REFERENCES particle_updates(update_id),
           posterior_probability REAL NOT NULL,
           valuation_sha256 TEXT NOT NULL,
           custody_sha256 TEXT NOT NULL,
           PRIMARY KEY(reconciliation_id, world_id),
           UNIQUE(reconciliation_id, ordinal)
       )""",
    """CREATE INDEX particle_reconciliation_members_world_idx
       ON particle_reconciliation_members(world_id, reconciliation_id)""",
)
MIGRATION_7_TO_8_SHA256 = sha256_text(canonical_json(MIGRATION_7_TO_8_STATEMENTS))

PROJECTION_TABLES = [
    "particle_reconciliation_members",
    "particle_reconciliation_factors",
    "particle_reconciliations",
    "particle_update_members",
    "particle_updates",
    "fair_play_seals",
    "consequence_repairs",
    "consequence_links",
    "commitment_transitions",
    "evidence_links",
    "questions",
    "world_assignments",
    "worlds",
    "assertions",
    "cardinality_members",
    "cardinality_constraints",
    "claim_relations",
    "claims",
    "sources",
    "agents",
]

_EXPECTED_DATABASE_SHAPE: dict[str, Any] | None = None


def _quoted_identifier(value: str) -> str:
    return '"' + value.replace('"', '""') + '"'


def _normalize_schema_sql(value: str | None) -> str:
    """Normalize SQLite-owned DDL enough to compare equivalent definitions."""
    return re.sub(r"\s+", " ", value or "").strip().lower()


def _catalog_database_shape(conn: sqlite3.Connection) -> dict[str, Any]:
    """Return the deterministic structural contract visible through SQLite.

    Defaults are deliberately excluded: schema-3 migration gives the new
    ``commitment_basis`` column a ``legacy`` default so historical rows can be
    upgraded in place, while newly initialized current-schema cubes always write the
    field explicitly. Types, nullability, keys, foreign keys, named indexes,
    uniqueness, partiality, and indexed columns remain authoritative.
    """
    table_names = sorted(
        str(row["name"])
        for row in conn.execute(
            """SELECT name FROM sqlite_master
               WHERE type = 'table' AND name NOT LIKE 'sqlite_%'
               ORDER BY name"""
        ).fetchall()
    )
    tables: dict[str, Any] = {}
    for table_name in table_names:
        quoted = _quoted_identifier(table_name)
        columns = {
            str(row["name"]): {
                "type": str(row["type"]).upper(),
                "notnull": bool(row["notnull"]),
                "pk": int(row["pk"]),
            }
            for row in conn.execute(f"PRAGMA table_info({quoted})").fetchall()
        }
        foreign_keys = sorted(
            (
                str(row["from"]),
                str(row["table"]),
                str(row["to"]),
                str(row["on_update"]),
                str(row["on_delete"]),
                str(row["match"]),
            )
            for row in conn.execute(f"PRAGMA foreign_key_list({quoted})").fetchall()
        )
        tables[table_name] = {
            "columns": columns,
            "foreign_keys": foreign_keys,
        }

    explicit_index_rows = conn.execute(
        """SELECT name, tbl_name, sql FROM sqlite_master
           WHERE type = 'index' AND sql IS NOT NULL
           ORDER BY name"""
    ).fetchall()
    indexes: dict[str, Any] = {}
    index_catalog_by_table: dict[str, dict[str, sqlite3.Row]] = {}
    for table_name in table_names:
        quoted = _quoted_identifier(table_name)
        index_catalog_by_table[table_name] = {
            str(row["name"]): row
            for row in conn.execute(f"PRAGMA index_list({quoted})").fetchall()
        }
    for row in explicit_index_rows:
        index_name = str(row["name"])
        table_name = str(row["tbl_name"])
        index_meta = index_catalog_by_table.get(table_name, {}).get(index_name)
        if index_meta is None:
            continue
        quoted_index = _quoted_identifier(index_name)
        columns = [
            str(item["name"])
            for item in conn.execute(f"PRAGMA index_info({quoted_index})").fetchall()
        ]
        indexes[index_name] = {
            "table": table_name,
            "unique": bool(index_meta["unique"]),
            "partial": bool(index_meta["partial"]),
            "columns": columns,
            # Column lists and the partial flag are insufficient: an index with
            # ``WHERE ended_seq IS NOT NULL`` would otherwise impersonate the
            # canonical active-row uniqueness guard.
            "sql": _normalize_schema_sql(row["sql"]),
        }

    auxiliary_objects = [
        {
            "type": str(row["type"]),
            "name": str(row["name"]),
            "table": str(row["tbl_name"]),
            "sql": _normalize_schema_sql(row["sql"]),
        }
        for row in conn.execute(
            """SELECT type, name, tbl_name, sql FROM sqlite_master
               WHERE type IN ('trigger', 'view')
               ORDER BY type, name"""
        ).fetchall()
    ]
    return {
        "tables": tables,
        "indexes": indexes,
        "auxiliary_objects": auxiliary_objects,
    }


def _expected_database_shape() -> dict[str, Any]:
    global _EXPECTED_DATABASE_SHAPE
    if _EXPECTED_DATABASE_SHAPE is None:
        expected = sqlite3.connect(":memory:")
        expected.row_factory = sqlite3.Row
        expected.execute("PRAGMA foreign_keys = ON")
        try:
            expected.executescript(SCHEMA_SQL)
            _EXPECTED_DATABASE_SHAPE = _catalog_database_shape(expected)
        finally:
            expected.close()
    return _EXPECTED_DATABASE_SHAPE


def _database_shape_errors(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """Compare a live cube against the runtime's canonical schema contract."""
    expected = _expected_database_shape()
    actual = _catalog_database_shape(conn)
    errors: list[dict[str, Any]] = []

    expected_tables = set(expected["tables"])
    actual_tables = set(actual["tables"])
    for table_name in sorted(expected_tables - actual_tables):
        errors.append({"kind": "missing-table", "table": table_name})
    for table_name in sorted(actual_tables - expected_tables):
        errors.append({"kind": "unexpected-table", "table": table_name})

    for table_name in sorted(expected_tables & actual_tables):
        expected_table = expected["tables"][table_name]
        actual_table = actual["tables"][table_name]
        expected_columns = set(expected_table["columns"])
        actual_columns = set(actual_table["columns"])
        missing_columns = sorted(expected_columns - actual_columns)
        unexpected_columns = sorted(actual_columns - expected_columns)
        if missing_columns or unexpected_columns:
            errors.append(
                {
                    "kind": "column-set",
                    "table": table_name,
                    "missing": missing_columns,
                    "unexpected": unexpected_columns,
                }
            )
        for column_name in sorted(expected_columns & actual_columns):
            expected_column = expected_table["columns"][column_name]
            actual_column = actual_table["columns"][column_name]
            if expected_column != actual_column:
                errors.append(
                    {
                        "kind": "column-shape",
                        "table": table_name,
                        "column": column_name,
                        "expected": expected_column,
                        "actual": actual_column,
                    }
                )
        if expected_table["foreign_keys"] != actual_table["foreign_keys"]:
            errors.append(
                {
                    "kind": "foreign-key-set",
                    "table": table_name,
                    "expected": expected_table["foreign_keys"],
                    "actual": actual_table["foreign_keys"],
                }
            )

    expected_indexes = set(expected["indexes"])
    actual_indexes = set(actual["indexes"])
    for index_name in sorted(expected_indexes - actual_indexes):
        errors.append({"kind": "missing-index", "index": index_name})
    for index_name in sorted(actual_indexes - expected_indexes):
        errors.append({"kind": "unexpected-index", "index": index_name})
    for index_name in sorted(expected_indexes & actual_indexes):
        if expected["indexes"][index_name] != actual["indexes"][index_name]:
            errors.append(
                {
                    "kind": "index-shape",
                    "index": index_name,
                    "expected": expected["indexes"][index_name],
                    "actual": actual["indexes"][index_name],
                }
            )

    expected_auxiliary = expected["auxiliary_objects"]
    actual_auxiliary = actual["auxiliary_objects"]
    if expected_auxiliary != actual_auxiliary:
        errors.append(
            {
                "kind": "auxiliary-schema-objects",
                "expected": expected_auxiliary,
                "actual": actual_auxiliary,
            }
        )
    return errors


def _row_dict(row: sqlite3.Row | None) -> dict[str, Any] | None:
    return dict(row) if row is not None else None


def _json_load(text: str) -> Any:
    return json.loads(text)


def _event_hash_core(
    *,
    seq: int,
    event_id: str,
    change_id: str,
    event_type: str,
    actor_id: str,
    recorded_at: str,
    payload: dict[str, Any],
    prev_hash: str,
    schema_version: int = EVENT_SCHEMA_VERSION,
) -> dict[str, Any]:
    return {
        "seq": seq,
        "event_id": event_id,
        "change_id": change_id,
        "event_type": event_type,
        "schema_version": schema_version,
        "actor_id": actor_id,
        "recorded_at": recorded_at,
        "payload": payload,
        "prev_hash": prev_hash,
    }


def consequence_repair_review_sha256(
    *,
    cube_id: str,
    head: str,
    target: dict[str, Any],
    known_successors: dict[str, Any],
    blockers: list[dict[str, Any]],
) -> str:
    """Hash the complete authorization surface for one consequence replacement.

    Turn issuance needs to rebind a review after appending only its immutable
    request-source custody. Keeping the digest constructor here prevents the turn
    adapter and storage validator from drifting onto subtly different contracts.
    """
    return sha256_text(
        canonical_json(
            {
                "policy": CONSEQUENCE_REPAIR_POLICY,
                "cube_id": cube_id,
                "head": head,
                "target": target,
                "known_successors": known_successors,
                "blockers": blockers,
            }
        )
    )


def _same_interval_sql(prefix: str = "") -> str:
    p = f"{prefix}." if prefix else ""
    return (
        f"{p}timeline_id = ? AND "
        f"(({p}valid_from = ?) OR ({p}valid_from IS NULL AND ? IS NULL)) AND "
        f"(({p}valid_to = ?) OR ({p}valid_to IS NULL AND ? IS NULL))"
    )


class Cube:
    def __init__(self, root: Path, conn: sqlite3.Connection, config: dict[str, Any]):
        self.root = root
        self.conn = conn
        self.config = config

    @classmethod
    def init(cls, root: str | os.PathLike[str], *, owner_id: str = "user", owner_label: str = "User") -> "Cube":
        path = Path(root).expanduser().resolve()
        if path.exists() and any(path.iterdir() if path.is_dir() else [path]):
            raise LacunaError("cube-exists", f"refusing to initialize nonempty path: {path}")
        path.mkdir(parents=True, exist_ok=True)
        owner_id = require_id(owner_id, "owner_id")
        owner_label = require_string(owner_label, "owner_label", max_len=512)
        if owner_id == "system":
            raise LacunaError("reserved-owner-id", "owner_id 'system' is reserved for the Lacuna runtime")
        cube_id = new_id("cube")
        created_at = utc_now()
        config = {
            "schema": "lacuna.cube.v1",
            "project": "Lacuna",
            "project_version": __version__,
            "cube_id": cube_id,
            "created_at": created_at,
            "database": DATABASE_NAME,
        }
        (path / CUBE_CONFIG).write_text(pretty_json(config) + "\n", encoding="utf-8")
        conn = cls._connect(path / DATABASE_NAME)
        conn.executescript(SCHEMA_SQL)
        conn.execute("BEGIN IMMEDIATE")
        try:
            for key, value in {
                "cube_id": cube_id,
                "project": "Lacuna",
                "project_version": __version__,
                "schema_version": str(DATABASE_SCHEMA_VERSION),
                "created_at": created_at,
                "head": GENESIS_HASH,
            }.items():
                conn.execute("INSERT INTO meta(key, value) VALUES (?, ?)", (key, value))
            conn.execute(
                """INSERT INTO schema_migrations(
                       target_version, source_version, applied_at, runtime_version, migration_sha256
                   ) VALUES (?, ?, ?, ?, ?)""",
                (
                    DATABASE_SCHEMA_VERSION,
                    0,
                    created_at,
                    __version__,
                    sha256_text(canonical_json({"initialized_schema": DATABASE_SCHEMA_VERSION})),
                ),
            )
            cube = cls(path, conn, config)
            change_id = new_id("chg")
            before = GENESIS_HASH
            event_ids: list[str] = []
            first = cube._append_event(
                change_id=change_id,
                event_type="cube.created",
                actor_id="system",
                recorded_at=created_at,
                payload={"cube_id": cube_id, "project_version": __version__},
            )
            event_ids.append(first["event_id"])
            for agent in [
                {"agent_id": "system", "kind": "system", "label": "Lacuna", "metadata": {}},
                {"agent_id": owner_id, "kind": "human", "label": owner_label, "metadata": {}},
            ]:
                event_type, payload = cube._prepare_operation({"op": "register_agent", **agent})
                event = cube._append_event(
                    change_id=change_id,
                    event_type=event_type,
                    actor_id="system",
                    recorded_at=created_at,
                    payload=payload,
                )
                event_ids.append(event["event_id"])
            after = cube.head()
            conn.execute(
                """INSERT INTO changesets(
                       change_id, actor_id, message, expected_head, before_head, after_head,
                       operation_count, applied_at, payload_sha256
                   ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    change_id,
                    "system",
                    "cube initialization",
                    before,
                    before,
                    after,
                    len(event_ids),
                    created_at,
                    sha256_text(canonical_json(config)),
                ),
            )
            conn.commit()
        except Exception:
            conn.rollback()
            conn.close()
            raise
        return cls(path, conn, config)

    @classmethod
    def _load_config(
        cls,
        root: str | os.PathLike[str],
    ) -> tuple[Path, dict[str, Any], Path]:
        path = Path(root).expanduser().resolve()
        config_path = path / CUBE_CONFIG
        if not config_path.is_file():
            raise LacunaError("not-a-cube", f"missing {CUBE_CONFIG} under {path}")
        try:
            config = json.loads(config_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise LacunaError("bad-cube-config", f"cannot read {config_path}: {exc}") from exc
        if not isinstance(config, dict):
            raise LacunaError("bad-cube-config", "cube config root must be an object")
        unexpected_fields = sorted(set(config) - CUBE_CONFIG_FIELDS)
        if unexpected_fields:
            raise LacunaError(
                "unexpected-cube-field",
                "cube config contains unrecognized fields",
                {"fields": unexpected_fields},
            )
        if config.get("schema") != "lacuna.cube.v1":
            raise LacunaError("bad-cube-schema", "unsupported cube config schema")
        if config.get("project") != "Lacuna":
            raise LacunaError("bad-cube-config", "cube project must be 'Lacuna'")
        try:
            require_id(config.get("cube_id"), "cube_id")
            require_string(config.get("project_version"), "project_version", max_len=64)
            require_string(config.get("created_at"), "created_at", max_len=128)
        except ValueError as exc:
            raise LacunaError("bad-cube-config", str(exc)) from exc
        database = config.get("database")
        if database != DATABASE_NAME:
            raise LacunaError("bad-cube-config", f"database must be {DATABASE_NAME!r}")
        db_path = path / database
        if not db_path.is_file():
            raise LacunaError("missing-database", f"missing cube database: {db_path}")
        return path, config, db_path

    @classmethod
    def open(cls, root: str | os.PathLike[str]) -> "Cube":
        path, config, db_path = cls._load_config(root)
        conn = cls._connect(db_path)
        cube = cls(path, conn, config)
        user_version = int(conn.execute("PRAGMA user_version").fetchone()[0])
        if user_version < DATABASE_SCHEMA_VERSION:
            cube.close()
            raise LacunaError(
                "database-migration-required",
                f"database schema {user_version} must be migrated to {DATABASE_SCHEMA_VERSION}",
                {
                    "database_schema_version": user_version,
                    "runtime_schema_version": DATABASE_SCHEMA_VERSION,
                    "command": f"lacuna migrate {path}",
                },
            )
        if user_version > DATABASE_SCHEMA_VERSION:
            cube.close()
            raise LacunaError(
                "database-schema-too-new",
                f"database schema {user_version} is newer than runtime schema {DATABASE_SCHEMA_VERSION}",
            )
        db_schema_version = cube.meta("schema_version")
        if db_schema_version != str(DATABASE_SCHEMA_VERSION):
            cube.close()
            raise LacunaError(
                "database-schema-mismatch",
                "database metadata and PRAGMA user_version disagree",
                {"pragma": user_version, "metadata": db_schema_version},
            )
        shape_errors = _database_shape_errors(conn)
        if shape_errors:
            cube.close()
            raise LacunaError(
                "database-schema-shape-mismatch",
                "database objects do not match the runtime schema contract",
                {"errors": shape_errors},
            )
        db_cube_id = cube.meta("cube_id")
        if db_cube_id != config.get("cube_id"):
            cube.close()
            raise LacunaError("cube-identity-mismatch", "cube.json and database disagree on cube_id")
        return cube

    @classmethod
    def migrate(cls, root: str | os.PathLike[str]) -> dict[str, Any]:
        """Apply supported forward database migrations without rewriting the event ledger."""
        path, config, db_path = cls._load_config(root)
        conn = cls._connect(db_path)
        applied_at = utc_now()
        try:
            user_version = int(conn.execute("PRAGMA user_version").fetchone()[0])
            meta_row = conn.execute("SELECT value FROM meta WHERE key = 'schema_version'").fetchone()
            if meta_row is None:
                raise LacunaError("missing-meta", "missing metadata key 'schema_version'")
            metadata_version = int(meta_row["value"])
            cube_id_row = conn.execute("SELECT value FROM meta WHERE key = 'cube_id'").fetchone()
            if cube_id_row is None or cube_id_row["value"] != config.get("cube_id"):
                raise LacunaError("cube-identity-mismatch", "cube.json and database disagree on cube_id")
            head_row = conn.execute("SELECT value FROM meta WHERE key = 'head'").fetchone()
            if head_row is None:
                raise LacunaError("missing-meta", "missing metadata key 'head'")
            before_head = str(head_row["value"])

            if user_version == DATABASE_SCHEMA_VERSION:
                if metadata_version != DATABASE_SCHEMA_VERSION:
                    raise LacunaError(
                        "database-schema-mismatch",
                        "database metadata and PRAGMA user_version disagree",
                        {"pragma": user_version, "metadata": metadata_version},
                    )
                shape_errors = _database_shape_errors(conn)
                if shape_errors:
                    raise LacunaError(
                        "database-schema-shape-mismatch",
                        "database objects do not match the runtime schema contract",
                        {"errors": shape_errors},
                    )
                return {
                    "event": "lacuna.database.migrated",
                    "schema": "lacuna.migration-receipt.v1",
                    "overall_status": "pass",
                    "cube_id": config["cube_id"],
                    "changed": False,
                    "source_version": user_version,
                    "target_version": DATABASE_SCHEMA_VERSION,
                    "head": before_head,
                    "steps": [],
                    "applied_at": applied_at,
                }
            if user_version > DATABASE_SCHEMA_VERSION:
                raise LacunaError(
                    "database-schema-too-new",
                    f"database schema {user_version} is newer than runtime schema {DATABASE_SCHEMA_VERSION}",
                )
            if metadata_version != user_version or user_version not in {1, 2, 3, 4, 5, 6, 7}:
                raise LacunaError(
                    "unsupported-database-migration",
                    "this runtime can migrate only a coherent schema-1 through schema-7 cube to schema 8",
                    {"pragma": user_version, "metadata": metadata_version},
                )
            integrity = conn.execute("PRAGMA integrity_check").fetchone()[0]
            if integrity != "ok":
                raise LacunaError("migration-preflight-failed", f"SQLite integrity check failed: {integrity}")
            foreign_rows = conn.execute("PRAGMA foreign_key_check").fetchall()
            if foreign_rows:
                raise LacunaError(
                    "migration-preflight-failed",
                    "foreign-key violations must be repaired before migration",
                    {"violation_count": len(foreign_rows)},
                )

            # Schema 6 shipped dormant, event-unowned particle projection tables in
            # its fresh schema while its official migration path did not create them.
            # Schema 7 replaces either shape with canonical event-owned tables. Never
            # discard pre-existing rows silently: they have no official ledger custody
            # and require an explicit rebuild or forensic export by the operator.
            if user_version == 6:
                particle_rows: dict[str, int] = {}
                for table_name in ("particle_updates", "particle_update_members"):
                    table_exists = conn.execute(
                        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?",
                        (table_name,),
                    ).fetchone()
                    if table_exists is not None:
                        particle_rows[table_name] = int(
                            conn.execute(
                                f"SELECT COUNT(*) FROM {_quoted_identifier(table_name)}"
                            ).fetchone()[0]
                        )
                if any(particle_rows.values()):
                    raise LacunaError(
                        "migration-preflight-failed",
                        "schema-6 lineage repair refuses to discard event-unowned particle projection rows",
                        {
                            "code": "unowned-particle-projection-rows",
                            "row_counts": particle_rows,
                            "repair": "export the rows for forensics, then run the schema-6 runtime rebuild before migration",
                        },
                    )

            def apply_ddl(statements: tuple[str, ...]) -> None:
                """Apply deterministic migration DDL while tolerating forward-provisioned objects.

                A cube may have been partially provisioned by a newer packaging layer while its
                migration custody still names an older coherent schema. Existing columns, tables,
                or indexes are accepted here; post-migration shape and invariant checks remain
                authoritative and will reject incompatible objects.
                """
                for statement in statements:
                    try:
                        conn.execute(statement)
                    except sqlite3.OperationalError as exc:
                        message = str(exc).lower()
                        if "duplicate column name" in message or "already exists" in message:
                            continue
                        raise

            source_version = user_version
            steps: list[dict[str, Any]] = []
            conn.execute("BEGIN IMMEDIATE")
            try:
                if user_version == 1:
                    apply_ddl(MIGRATION_1_TO_2_STATEMENTS)
                    conn.execute(
                        """INSERT INTO schema_migrations(
                               target_version, source_version, applied_at, runtime_version, migration_sha256
                           ) VALUES (?, ?, ?, ?, ?)""",
                        (2, 1, applied_at, __version__, MIGRATION_1_TO_2_SHA256),
                    )
                    steps.append(
                        {
                            "source_version": 1,
                            "target_version": 2,
                            "migration_sha256": MIGRATION_1_TO_2_SHA256,
                        }
                    )
                    user_version = 2
                if user_version == 2:
                    apply_ddl(MIGRATION_2_TO_3_STATEMENTS)
                    conn.execute(
                        """INSERT INTO schema_migrations(
                               target_version, source_version, applied_at, runtime_version, migration_sha256
                           ) VALUES (?, ?, ?, ?, ?)""",
                        (3, 2, applied_at, __version__, MIGRATION_2_TO_3_SHA256),
                    )
                    steps.append(
                        {
                            "source_version": 2,
                            "target_version": 3,
                            "migration_sha256": MIGRATION_2_TO_3_SHA256,
                        }
                    )
                    user_version = 3
                if user_version == 3:
                    apply_ddl(MIGRATION_3_TO_4_STATEMENTS)
                    conn.execute(
                        """INSERT INTO schema_migrations(
                               target_version, source_version, applied_at, runtime_version, migration_sha256
                           ) VALUES (?, ?, ?, ?, ?)""",
                        (4, 3, applied_at, __version__, MIGRATION_3_TO_4_SHA256),
                    )
                    steps.append(
                        {
                            "source_version": 3,
                            "target_version": 4,
                            "migration_sha256": MIGRATION_3_TO_4_SHA256,
                        }
                    )
                    user_version = 4
                if user_version == 4:
                    apply_ddl(MIGRATION_4_TO_5_STATEMENTS)
                    conn.execute(
                        """INSERT INTO schema_migrations(
                               target_version, source_version, applied_at, runtime_version, migration_sha256
                           ) VALUES (?, ?, ?, ?, ?)""",
                        (5, 4, applied_at, __version__, MIGRATION_4_TO_5_SHA256),
                    )
                    steps.append(
                        {
                            "source_version": 4,
                            "target_version": 5,
                            "migration_sha256": MIGRATION_4_TO_5_SHA256,
                        }
                    )
                    user_version = 5
                if user_version == 5:
                    apply_ddl(MIGRATION_5_TO_6_STATEMENTS)
                    conn.execute(
                        """INSERT INTO schema_migrations(
                               target_version, source_version, applied_at, runtime_version, migration_sha256
                           ) VALUES (?, ?, ?, ?, ?)""",
                        (6, 5, applied_at, __version__, MIGRATION_5_TO_6_SHA256),
                    )
                    steps.append(
                        {
                            "source_version": 5,
                            "target_version": 6,
                            "migration_sha256": MIGRATION_5_TO_6_SHA256,
                        }
                    )
                    user_version = 6
                if user_version == 6:
                    apply_ddl(MIGRATION_6_TO_7_STATEMENTS)
                    conn.execute(
                        """INSERT INTO schema_migrations(
                               target_version, source_version, applied_at, runtime_version, migration_sha256
                           ) VALUES (?, ?, ?, ?, ?)""",
                        (7, 6, applied_at, __version__, MIGRATION_6_TO_7_SHA256),
                    )
                    steps.append(
                        {
                            "source_version": 6,
                            "target_version": 7,
                            "migration_sha256": MIGRATION_6_TO_7_SHA256,
                        }
                    )
                    user_version = 7
                if user_version == 7:
                    apply_ddl(MIGRATION_7_TO_8_STATEMENTS)
                    conn.execute(
                        """INSERT INTO schema_migrations(
                               target_version, source_version, applied_at, runtime_version, migration_sha256
                           ) VALUES (?, ?, ?, ?, ?)""",
                        (8, 7, applied_at, __version__, MIGRATION_7_TO_8_SHA256),
                    )
                    steps.append(
                        {
                            "source_version": 7,
                            "target_version": 8,
                            "migration_sha256": MIGRATION_7_TO_8_SHA256,
                        }
                    )
                    user_version = 8
                shape_errors = _database_shape_errors(conn)
                if shape_errors:
                    raise LacunaError(
                        "database-schema-shape-mismatch",
                        "migration produced objects that do not match the runtime schema contract",
                        {"errors": shape_errors},
                    )
                conn.execute(
                    "UPDATE meta SET value = ? WHERE key = 'schema_version'",
                    (str(DATABASE_SCHEMA_VERSION),),
                )
                conn.execute(
                    "UPDATE meta SET value = ? WHERE key = 'project_version'",
                    (__version__,),
                )
                conn.execute(f"PRAGMA user_version = {DATABASE_SCHEMA_VERSION}")
                conn.commit()
            except Exception:
                conn.rollback()
                raise

            after_head_row = conn.execute("SELECT value FROM meta WHERE key = 'head'").fetchone()
            after_head = str(after_head_row["value"])
            if after_head != before_head:
                raise LacunaError(
                    "migration-ledger-rewrite",
                    "database migration unexpectedly changed the event-ledger head",
                    {"before_head": before_head, "after_head": after_head},
                )
            combined_digest = sha256_text(canonical_json(steps))
            return {
                "event": "lacuna.database.migrated",
                "schema": "lacuna.migration-receipt.v1",
                "overall_status": "pass",
                "cube_id": config["cube_id"],
                "changed": True,
                "source_version": source_version,
                "target_version": DATABASE_SCHEMA_VERSION,
                "migration_sha256": combined_digest,
                "steps": steps,
                "before_head": before_head,
                "after_head": after_head,
                "applied_at": applied_at,
            }
        finally:
            try:
                conn.execute("PRAGMA busy_timeout = 250")
                conn.execute("PRAGMA wal_checkpoint(PASSIVE)")
            except (sqlite3.OperationalError, sqlite3.ProgrammingError):
                pass
            finally:
                conn.close()

    @staticmethod
    def _connect(path: Path) -> sqlite3.Connection:
        fast_test_io = os.environ.get("LACUNA_FAST_TEST_IO") == "1"
        timeout = 5.0 if fast_test_io else 30.0
        conn = sqlite3.connect(path, timeout=timeout, isolation_level=None)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute(f"PRAGMA busy_timeout = {5000 if fast_test_io else 30000}")
        conn.execute("PRAGMA journal_mode = WAL")
        conn.execute("PRAGMA synchronous = OFF" if fast_test_io else "PRAGMA synchronous = FULL")
        return conn

    def close(self) -> None:
        """Close the cube safely; repeated close calls are harmless.

        Context-manager teardown and failed migrations can converge on the same
        connection.  Resource cleanup should not turn an earlier, useful Lacuna
        error into a secondary ``sqlite3.ProgrammingError``.  Close-time WAL
        cleanup is deliberately non-blocking: a truncating checkpoint can wait
        behind another fixture, subprocess, or reader connection even after all
        story work is complete.  A passive checkpoint preserves durability while
        avoiding teardown stalls; later opens can continue normal WAL recovery.
        """
        try:
            self.conn.execute("PRAGMA busy_timeout = 250")
            self.conn.execute("PRAGMA wal_checkpoint(PASSIVE)")
        except sqlite3.ProgrammingError as exc:
            if "closed database" not in str(exc).lower():
                raise
            return
        except sqlite3.OperationalError:
            pass
        finally:
            try:
                self.conn.close()
            except sqlite3.ProgrammingError:
                pass

    def __enter__(self) -> "Cube":
        return self

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        self.close()

    def meta(self, key: str) -> str:
        row = self.conn.execute("SELECT value FROM meta WHERE key = ?", (key,)).fetchone()
        if row is None:
            raise LacunaError("missing-meta", f"missing metadata key {key!r}")
        return str(row["value"])

    def head(self) -> str:
        return self.meta("head")

    def event_count(self) -> int:
        return int(self.conn.execute("SELECT COUNT(*) AS n FROM events").fetchone()["n"])

    def event_sequence(self, head: str) -> int:
        """Return the immutable event sequence for one ledger head.

        The genesis hash is sequence zero. Every other accepted head must name
        exactly one immutable event in this cube. This small query centralizes
        chronological ancestry checks for host-side artifacts without exposing
        raw SQL throughout the orchestration modules.
        """
        if not isinstance(head, str) or not SHA256_RE.fullmatch(head):
            raise LacunaError("bad-ledger-head", "head must be a lowercase SHA-256 digest")
        if head == GENESIS_HASH:
            return 0
        row = self.conn.execute("SELECT seq FROM events WHERE event_hash = ?", (head,)).fetchone()
        if row is None:
            raise LacunaError(
                "unknown-ledger-head",
                "head is not present in this cube's immutable event ledger",
                {"head": head},
            )
        return int(row["seq"])

    def _exists(self, table: str, key: str, value: str, *, active_column: str | None = None) -> bool:
        sql = f"SELECT 1 FROM {table} WHERE {key} = ?"
        if active_column:
            sql += f" AND {active_column} IS NULL"
        return self.conn.execute(sql, (value,)).fetchone() is not None

    def has_active_agent(self, agent_id: str) -> bool:
        """Return whether an agent identity exists and has not been retired."""
        try:
            agent_id = require_id(agent_id, "agent_id")
        except ValueError:
            return False
        return self._exists("agents", "agent_id", agent_id, active_column="retired_seq")

    def _require_agent(self, agent_id: str, field: str) -> None:
        if not self.has_active_agent(agent_id):
            raise LacunaError("unknown-agent", f"{field} references unknown or retired agent {agent_id!r}")

    def _require_source(self, source_id: str, field: str) -> None:
        if not self._exists("sources", "source_id", source_id, active_column="retired_seq"):
            raise LacunaError("unknown-source", f"{field} references unknown or retired source {source_id!r}")

    def _require_claim(self, claim_id: str) -> None:
        if not self._exists("claims", "claim_id", claim_id):
            raise LacunaError("unknown-claim", f"unknown claim {claim_id!r}")

    def _require_relation(self, relation_id: str, *, active: bool = False) -> dict[str, Any]:
        sql = "SELECT * FROM claim_relations WHERE relation_id = ?"
        if active:
            sql += " AND ended_seq IS NULL"
        row = self.conn.execute(sql, (relation_id,)).fetchone()
        if row is None:
            qualifier = "active " if active else ""
            raise LacunaError("unknown-claim-relation", f"unknown {qualifier}claim relation {relation_id!r}")
        return dict(row)

    def _require_cardinality(self, constraint_id: str, *, active: bool = False) -> dict[str, Any]:
        sql = "SELECT * FROM cardinality_constraints WHERE constraint_id = ?"
        if active:
            sql += " AND ended_seq IS NULL"
        row = self.conn.execute(sql, (constraint_id,)).fetchone()
        if row is None:
            qualifier = "active " if active else ""
            raise LacunaError(
                "unknown-cardinality-constraint",
                f"unknown {qualifier}cardinality constraint {constraint_id!r}",
            )
        return dict(row)

    def _require_assertion(self, assertion_id: str, *, active: bool = False) -> None:
        if not self._exists("assertions", "assertion_id", assertion_id, active_column="ended_seq" if active else None):
            qualifier = "active " if active else ""
            raise LacunaError("unknown-assertion", f"unknown {qualifier}assertion {assertion_id!r}")

    def _require_world(self, world_id: str) -> dict[str, Any]:
        row = self.conn.execute("SELECT * FROM worlds WHERE world_id = ?", (world_id,)).fetchone()
        if row is None:
            raise LacunaError("unknown-world", f"unknown world {world_id!r}")
        return dict(row)

    def _require_world_assignment(
        self,
        assignment_id: str,
        *,
        active: bool = False,
    ) -> dict[str, Any]:
        sql = "SELECT * FROM world_assignments WHERE assignment_id = ?"
        if active:
            sql += " AND ended_seq IS NULL"
        row = self.conn.execute(sql, (assignment_id,)).fetchone()
        if row is None:
            qualifier = "active " if active else ""
            raise LacunaError(
                "unknown-world-assignment",
                f"unknown {qualifier}world assignment {assignment_id!r}",
            )
        return dict(row)

    def _require_consequence(
        self,
        consequence_id: str,
        *,
        active: bool = False,
    ) -> dict[str, Any]:
        sql = "SELECT * FROM consequence_links WHERE consequence_id = ?"
        if active:
            sql += " AND ended_seq IS NULL"
        row = self.conn.execute(sql, (consequence_id,)).fetchone()
        if row is None:
            qualifier = "active " if active else ""
            raise LacunaError(
                "unknown-consequence",
                f"unknown {qualifier}consequence {consequence_id!r}",
            )
        return dict(row)

    def _require_consequence_repair(self, repair_id: str) -> dict[str, Any]:
        row = self.conn.execute(
            "SELECT * FROM consequence_repairs WHERE repair_id = ?", (repair_id,)
        ).fetchone()
        if row is None:
            raise LacunaError(
                "unknown-consequence-repair",
                f"unknown consequence repair {repair_id!r}",
            )
        return dict(row)

    def _require_seal(self, seal_id: str, *, unresolved: bool = False) -> dict[str, Any]:
        sql = "SELECT * FROM fair_play_seals WHERE seal_id = ?"
        if unresolved:
            sql += " AND revealed_seq IS NULL AND voided_seq IS NULL"
        row = self.conn.execute(sql, (seal_id,)).fetchone()
        if row is None and unresolved:
            resolved = self.conn.execute(
                "SELECT revealed_seq, voided_seq FROM fair_play_seals WHERE seal_id = ?",
                (seal_id,),
            ).fetchone()
            if resolved is not None:
                status = "revealed" if resolved["revealed_seq"] is not None else "voided"
                raise LacunaError(
                    "resolved-precommitment-seal",
                    f"precommitment seal {seal_id!r} is already {status}",
                    {"seal_id": seal_id, "status": status},
                )
        if row is None:
            qualifier = "unresolved " if unresolved else ""
            raise LacunaError(
                "unknown-precommitment-seal",
                f"unknown {qualifier}precommitment seal {seal_id!r}",
            )
        return dict(row)

    def _execute_changeset(
        self,
        document: dict[str, Any],
        *,
        recorded_at: str | None = None,
        event_ids: list[str] | None = None,
        persist: bool,
        after_apply: Callable[[], Any] | None = None,
    ) -> tuple[dict[str, Any], Any]:
        """Execute one exact change envelope, optionally rolling it back.

        Preview and commit deliberately share this path.  A preparation can freeze
        the timestamp and event identifiers produced during a rollback rehearsal,
        then replay that same envelope at commit.  ``after_apply`` runs while the
        transaction and projected post-state are still visible; any exception it
        raises rolls the entire change back.
        """
        doc = require_mapping(document, "change-set")
        unexpected_fields = sorted(set(doc) - CHANGESET_FIELDS)
        if unexpected_fields:
            raise LacunaError(
                "unexpected-change-field",
                "change-set contains unrecognized fields",
                {"fields": unexpected_fields},
            )
        if doc.get("schema") != "lacuna.change-set.v1":
            raise LacunaError("bad-change-schema", "schema must be 'lacuna.change-set.v1'")
        change_id = require_id(doc.get("change_id") or new_id("chg"), "change_id")
        actor_id = require_id(doc.get("actor_id"), "actor_id")
        expected_head = require_string(doc.get("expected_head"), "expected_head", max_len=64)
        if not SHA256_RE.fullmatch(expected_head):
            raise LacunaError("bad-expected-head", "expected_head must be a lowercase SHA-256 digest")
        message = optional_string(doc.get("message"), "message", max_len=4096)
        operations = require_list(doc.get("operations"), "operations")
        if not operations:
            raise LacunaError("empty-change-set", "operations must contain at least one operation")
        if len(operations) > 1000:
            raise LacunaError("change-set-too-large", "a change-set may contain at most 1000 operations")

        payload_sha256 = sha256_text(canonical_json(doc))
        if recorded_at is None:
            applied_at = utc_now()
        else:
            applied_at = require_string(recorded_at, "recorded_at", max_len=128)

        prepared_event_ids: list[str] | None = None
        if event_ids is not None:
            if len(event_ids) != len(operations):
                raise LacunaError(
                    "prepared-event-count-mismatch",
                    "prepared event identifier count must equal operation count",
                    {"expected": len(operations), "actual": len(event_ids)},
                )
            prepared_event_ids = [
                require_id(value, f"event_ids[{index}]")
                for index, value in enumerate(event_ids)
            ]
            if len(set(prepared_event_ids)) != len(prepared_event_ids):
                raise LacunaError(
                    "duplicate-prepared-event-id",
                    "prepared event identifiers must be unique",
                )

        self.conn.execute("BEGIN IMMEDIATE")
        before = self.head()
        try:
            if before != expected_head:
                raise LacunaError(
                    "stale-head",
                    "expected_head does not match the cube head",
                    {"expected_head": expected_head, "actual_head": before},
                )
            if self._exists("changesets", "change_id", change_id):
                raise LacunaError("duplicate-change-id", f"change_id {change_id!r} already exists")
            self._require_agent(actor_id, "actor_id")
            committed_event_ids: list[str] = []
            for index, raw_operation in enumerate(operations):
                try:
                    operation = require_mapping(raw_operation, f"operations[{index}]")
                    event_type, payload = self._prepare_operation(
                        operation, review_head=before
                    )
                    event = self._append_event(
                        change_id=change_id,
                        event_type=event_type,
                        actor_id=actor_id,
                        recorded_at=applied_at,
                        payload=payload,
                        event_id=(
                            None
                            if prepared_event_ids is None
                            else prepared_event_ids[index]
                        ),
                    )
                    committed_event_ids.append(event["event_id"])
                except LacunaError as exc:
                    details = dict(exc.details or {})
                    details["operation_index"] = index
                    details["operation"] = raw_operation
                    raise LacunaError(exc.code, exc.message, details) from exc
                except ValueError as exc:
                    raise LacunaError(
                        "invalid-operation",
                        str(exc),
                        {"operation_index": index, "operation": raw_operation},
                    ) from exc
            after = self.head()
            self.conn.execute(
                """INSERT INTO changesets(
                       change_id, actor_id, message, expected_head, before_head, after_head,
                       operation_count, applied_at, payload_sha256
                   ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    change_id,
                    actor_id,
                    message,
                    expected_head,
                    before,
                    after,
                    len(operations),
                    applied_at,
                    payload_sha256,
                ),
            )
            receipt = {
                "event": "lacuna.change.applied",
                "schema": "lacuna.change-receipt.v1",
                "overall_status": "pass",
                "cube_id": self.meta("cube_id"),
                "change_id": change_id,
                "actor_id": actor_id,
                "message": message,
                "before_head": before,
                "after_head": after,
                "operation_count": len(operations),
                "event_ids": committed_event_ids,
                "applied_at": applied_at,
            }
            inspection = after_apply() if after_apply is not None else None
            if persist:
                self.conn.commit()
            else:
                self.conn.rollback()
            return receipt, inspection
        except Exception:
            self.conn.rollback()
            raise

    def apply_changeset(self, document: dict[str, Any]) -> dict[str, Any]:
        receipt, _ = self._execute_changeset(document, persist=True)
        return receipt

    def preview_changeset(
        self,
        document: dict[str, Any],
        *,
        recorded_at: str,
        event_ids: list[str],
        after_apply: Callable[[], Any] | None = None,
    ) -> tuple[dict[str, Any], Any]:
        """Run the kernel's exact mutation path and roll back unconditionally."""
        return self._execute_changeset(
            document,
            recorded_at=recorded_at,
            event_ids=event_ids,
            persist=False,
            after_apply=after_apply,
        )

    def apply_prepared_changeset(
        self,
        document: dict[str, Any],
        *,
        recorded_at: str,
        event_ids: list[str],
        after_apply: Callable[[], Any] | None = None,
    ) -> tuple[dict[str, Any], Any]:
        """Commit an envelope whose timestamp and event identifiers were frozen."""
        return self._execute_changeset(
            document,
            recorded_at=recorded_at,
            event_ids=event_ids,
            persist=True,
            after_apply=after_apply,
        )

    def change_event_chain(self, change_id: str) -> list[dict[str, Any]]:
        change_id = require_id(change_id, "change_id")
        rows = self.conn.execute(
            "SELECT * FROM events WHERE change_id = ? ORDER BY seq",
            (change_id,),
        ).fetchall()
        return [
            {
                "seq": int(row["seq"]),
                "event_id": str(row["event_id"]),
                "change_id": str(row["change_id"]),
                "event_type": str(row["event_type"]),
                "schema_version": int(row["schema_version"]),
                "actor_id": str(row["actor_id"]),
                "recorded_at": str(row["recorded_at"]),
                "payload": json.loads(row["payload_json"]),
                "prev_hash": str(row["prev_hash"]),
                "event_hash": str(row["event_hash"]),
            }
            for row in rows
        ]

    def committed_change(self, change_id: str) -> dict[str, Any] | None:
        """Return the durable receipt and exact event chain for one change."""
        change_id = require_id(change_id, "change_id")
        row = self.conn.execute(
            "SELECT * FROM changesets WHERE change_id = ?",
            (change_id,),
        ).fetchone()
        if row is None:
            return None
        event_chain = self.change_event_chain(change_id)
        receipt = {
            "event": "lacuna.change.applied",
            "schema": "lacuna.change-receipt.v1",
            "overall_status": "pass",
            "cube_id": self.meta("cube_id"),
            "change_id": str(row["change_id"]),
            "actor_id": str(row["actor_id"]),
            "message": row["message"],
            "before_head": str(row["before_head"]),
            "after_head": str(row["after_head"]),
            "operation_count": int(row["operation_count"]),
            "event_ids": [item["event_id"] for item in event_chain],
            "applied_at": str(row["applied_at"]),
        }
        return {
            "payload_sha256": str(row["payload_sha256"]),
            "change": receipt,
            "event_chain": event_chain,
        }

    @contextmanager
    def snapshot_at_head(self, head: str) -> Iterator["Cube"]:
        """Yield an isolated, verified historical cube at a change boundary.

        The live database is copied through SQLite's backup API.  Later events and
        change receipts are removed only from the in-memory copy, then every
        projection is deterministically rebuilt from the retained ledger prefix.
        This is intended for recovery/audit comparisons, not for historical write
        authority.
        """
        head = require_string(head, "head", max_len=64)
        if not SHA256_RE.fullmatch(head):
            raise LacunaError("bad-head", "head must be a lowercase SHA-256 digest")
        boundary = self.conn.execute(
            "SELECT change_id FROM changesets WHERE after_head = ?",
            (head,),
        ).fetchone()
        if boundary is None:
            raise LacunaError(
                "unknown-historical-head",
                "historical snapshots require an exact change boundary",
                {"head": head},
            )
        target_change_id = str(boundary["change_id"])
        target = self.conn.execute(
            "SELECT seq, event_hash FROM events WHERE change_id = ? ORDER BY seq DESC LIMIT 1",
            (target_change_id,),
        ).fetchone()
        if target is None or str(target["event_hash"]) != head:
            raise LacunaError(
                "invalid-historical-boundary",
                "change receipt does not terminate at its recorded after_head",
                {"change_id": target_change_id, "head": head},
            )
        target_seq = int(target["seq"])

        conn = sqlite3.connect(":memory:", isolation_level=None)
        conn.row_factory = sqlite3.Row
        snapshot: Cube | None = None
        try:
            self.conn.backup(conn)
            conn.execute("PRAGMA foreign_keys = OFF")
            conn.execute("BEGIN IMMEDIATE")
            try:
                later_change_ids = [
                    str(row["change_id"])
                    for row in conn.execute(
                        "SELECT DISTINCT change_id FROM events WHERE seq > ?",
                        (target_seq,),
                    ).fetchall()
                ]
                for table in PROJECTION_TABLES:
                    conn.execute(f"DELETE FROM {table}")
                if later_change_ids:
                    placeholders = ",".join("?" for _ in later_change_ids)
                    conn.execute(
                        f"DELETE FROM changesets WHERE change_id IN ({placeholders})",
                        later_change_ids,
                    )
                conn.execute("DELETE FROM events WHERE seq > ?", (target_seq,))
                conn.execute("UPDATE meta SET value = ? WHERE key = 'head'", (head,))
                conn.commit()
            except Exception:
                conn.rollback()
                raise
            conn.execute("PRAGMA foreign_keys = ON")
            conn.execute("PRAGMA busy_timeout = 30000")
            snapshot = Cube(self.root, conn, dict(self.config))
            rebuilt = snapshot.rebuild_projections()
            if rebuilt["overall_status"] != "pass" or snapshot.head() != head:
                raise LacunaError(
                    "historical-snapshot-verification-failed",
                    "historical ledger prefix did not rebuild to the requested head",
                    {"head": head, "rebuild": rebuilt},
                )
            yield snapshot
        finally:
            try:
                conn.close()
            except sqlite3.ProgrammingError:
                pass

    def apply_operations(self, *, actor_id: str, operations: list[dict[str, Any]], message: str | None = None) -> dict[str, Any]:
        return self.apply_changeset(
            {
                "schema": "lacuna.change-set.v1",
                "change_id": new_id("chg"),
                "actor_id": actor_id,
                "expected_head": self.head(),
                "message": message,
                "operations": operations,
            }
        )

    def _append_event(
        self,
        *,
        change_id: str,
        event_type: str,
        actor_id: str,
        recorded_at: str,
        payload: dict[str, Any],
        event_id: str | None = None,
    ) -> dict[str, Any]:
        row = self.conn.execute("SELECT COALESCE(MAX(seq), 0) + 1 AS next_seq FROM events").fetchone()
        seq = int(row["next_seq"])
        prev_hash = self.head()
        event_id = new_id("evt") if event_id is None else require_id(event_id, "event_id")
        core = _event_hash_core(
            seq=seq,
            event_id=event_id,
            change_id=change_id,
            event_type=event_type,
            actor_id=actor_id,
            recorded_at=recorded_at,
            payload=payload,
            prev_hash=prev_hash,
        )
        event_hash = sha256_text(canonical_json(core))
        self.conn.execute(
            """INSERT INTO events(
                   seq, event_id, change_id, event_type, schema_version, actor_id,
                   recorded_at, payload_json, prev_hash, event_hash
               ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                seq,
                event_id,
                change_id,
                event_type,
                EVENT_SCHEMA_VERSION,
                actor_id,
                recorded_at,
                canonical_json(payload),
                prev_hash,
                event_hash,
            ),
        )
        self._apply_projection(event_type, payload, seq=seq, event_id=event_id)
        self.conn.execute("UPDATE meta SET value = ? WHERE key = 'head'", (event_hash,))
        return {"seq": seq, "event_id": event_id, "event_hash": event_hash}

    def _prepare_operation(
        self,
        operation: dict[str, Any],
        *,
        review_head: str | None = None,
    ) -> tuple[str, dict[str, Any]]:
        op = require_enum(
            operation.get("op"),
            "op",
            set(OPERATION_FIELDS),
        )
        unexpected_fields = sorted(set(operation) - OPERATION_FIELDS[op])
        if unexpected_fields:
            raise LacunaError(
                "unexpected-operation-field",
                f"operation {op!r} contains unrecognized fields",
                {"fields": unexpected_fields},
            )
        if op == "register_agent":
            return self._prepare_register_agent(operation)
        if op == "add_source":
            return self._prepare_add_source(operation)
        if op == "declare_claim":
            return self._prepare_declare_claim(operation)
        if op == "declare_relation":
            return self._prepare_declare_relation(operation)
        if op == "retire_relation":
            return self._prepare_retire_relation(operation)
        if op == "declare_cardinality":
            return self._prepare_declare_cardinality(operation)
        if op == "retire_cardinality":
            return self._prepare_retire_cardinality(operation)
        if op == "record_assertion":
            return self._prepare_record_assertion(operation)
        if op == "supersede_assertion":
            return self._prepare_supersede_assertion(operation)
        if op == "create_world":
            return self._prepare_create_world(operation)
        if op == "assign_world":
            return self._prepare_assign_world(operation)
        if op == "revise_world":
            return self._prepare_revise_world(operation, review_head=review_head)
        if op == "raise_commitment":
            return self._prepare_raise_commitment(operation)
        if op == "set_world_weight":
            return self._prepare_set_world_weight(operation)
        if op == "set_world_status":
            return self._prepare_set_world_status(operation)
        if op == "update_particle_bank":
            return self._prepare_update_particle_bank(operation)
        if op == "reconcile_particle_bank":
            return self._prepare_reconcile_particle_bank(
                operation,
                review_head=review_head,
            )
        if op == "link_evidence":
            return self._prepare_link_evidence(operation)
        if op == "link_consequence":
            return self._prepare_link_consequence(operation)
        if op == "replace_consequence":
            return self._prepare_replace_consequence(operation, review_head=review_head)
        if op == "retire_consequence":
            return self._prepare_retire_consequence(operation)
        if op == "seal_precommitment":
            return self._prepare_seal_precommitment(operation)
        if op == "reveal_precommitment":
            return self._prepare_reveal_precommitment(operation)
        if op == "void_precommitment":
            return self._prepare_void_precommitment(operation)
        if op == "open_question":
            return self._prepare_open_question(operation)
        if op == "close_question":
            return self._prepare_close_question(operation)
        raise AssertionError(op)

    def _prepare_register_agent(self, operation: dict[str, Any]) -> tuple[str, dict[str, Any]]:
        agent_id = require_id(operation.get("agent_id") or new_id("agt"), "agent_id")
        if self._exists("agents", "agent_id", agent_id):
            raise LacunaError("duplicate-agent", f"agent {agent_id!r} already exists")
        payload = {
            "agent_id": agent_id,
            "kind": require_enum(operation.get("kind", "other"), "kind", AGENT_KINDS),
            "label": require_string(operation.get("label", agent_id), "label", max_len=512),
            "metadata": require_mapping(operation.get("metadata", {}), "metadata"),
        }
        return "agent.registered", payload

    def _prepare_add_source(self, operation: dict[str, Any]) -> tuple[str, dict[str, Any]]:
        source_id = require_id(operation.get("source_id") or new_id("src"), "source_id")
        if self._exists("sources", "source_id", source_id):
            raise LacunaError("duplicate-source", f"source {source_id!r} already exists")
        content_sha256 = optional_string(operation.get("content_sha256"), "content_sha256", max_len=64)
        if content_sha256 is not None and not SHA256_RE.fullmatch(content_sha256):
            raise LacunaError("bad-content-digest", "content_sha256 must be a lowercase SHA-256 digest")
        payload = {
            "source_id": source_id,
            "kind": require_enum(operation.get("kind", "other"), "kind", SOURCE_KINDS),
            "label": require_string(operation.get("label", source_id), "label", max_len=512),
            "locator": optional_string(operation.get("locator"), "locator", max_len=4096),
            "content_sha256": content_sha256,
            "metadata": require_mapping(operation.get("metadata", {}), "metadata"),
        }
        return "source.added", payload

    def _prepare_declare_claim(self, operation: dict[str, Any]) -> tuple[str, dict[str, Any]]:
        subject = require_string(operation.get("subject"), "subject", max_len=1024)
        predicate = require_string(operation.get("predicate"), "predicate", max_len=1024)
        if "object" not in operation:
            raise LacunaError("missing-object", "declare_claim requires object")
        object_value = operation["object"]
        canonical_json(object_value)
        scope = require_enum(operation.get("scope", "world"), "scope", CLAIM_SCOPES)
        expected_id = deterministic_claim_id(subject, predicate, object_value, scope)
        supplied_id = operation.get("claim_id")
        if supplied_id is not None and require_id(supplied_id, "claim_id") != expected_id:
            raise LacunaError(
                "claim-id-mismatch",
                "claim_id must equal the deterministic identity of subject/predicate/object/scope",
                {"expected_claim_id": expected_id},
            )
        existing = self.conn.execute(
            "SELECT claim_id FROM claims WHERE subject = ? AND predicate = ? AND object_json = ? AND scope = ?",
            (subject, predicate, canonical_json(object_value), scope),
        ).fetchone()
        if existing is not None:
            raise LacunaError("duplicate-claim", f"claim already exists as {existing['claim_id']}")
        payload = {
            "claim_id": expected_id,
            "subject": subject,
            "predicate": predicate,
            "object": object_value,
            "scope": scope,
        }
        return "claim.declared", payload

    def _prepare_declare_relation(self, operation: dict[str, Any]) -> tuple[str, dict[str, Any]]:
        relation_id = require_id(operation.get("relation_id") or new_id("rel"), "relation_id")
        if self._exists("claim_relations", "relation_id", relation_id):
            raise LacunaError("duplicate-claim-relation", f"claim relation {relation_id!r} already exists")
        relation = require_enum(operation.get("relation"), "relation", RELATION_KINDS)
        left_claim_id = require_id(operation.get("left_claim_id"), "left_claim_id")
        right_claim_id = require_id(operation.get("right_claim_id"), "right_claim_id")
        self._require_claim(left_claim_id)
        self._require_claim(right_claim_id)
        if left_claim_id == right_claim_id:
            raise LacunaError("self-claim-relation", "a claim relation requires two distinct claims")
        left_claim_id, right_claim_id = normalize_relation_endpoints(
            relation, left_claim_id, right_claim_id
        )
        duplicate = self.conn.execute(
            """SELECT relation_id FROM claim_relations
               WHERE left_claim_id = ? AND right_claim_id = ? AND relation = ? AND ended_seq IS NULL""",
            (left_claim_id, right_claim_id, relation),
        ).fetchone()
        if duplicate is not None:
            raise LacunaError(
                "duplicate-active-claim-relation",
                "an identical active relation already exists",
                {"relation_id": duplicate["relation_id"]},
            )
        source_id = optional_id(operation.get("source_id"), "source_id")
        if source_id is not None:
            self._require_source(source_id, "source_id")
        payload = {
            "relation_id": relation_id,
            "left_claim_id": left_claim_id,
            "right_claim_id": right_claim_id,
            "relation": relation,
            "source_id": source_id,
            "rationale": require_string(operation.get("rationale"), "rationale", max_len=16384),
        }
        self._reject_relation_introduced_conflicts(payload)
        return "claim_relation.declared", payload

    def _prepare_retire_relation(self, operation: dict[str, Any]) -> tuple[str, dict[str, Any]]:
        relation_id = require_id(operation.get("relation_id"), "relation_id")
        self._require_relation(relation_id, active=True)
        return "claim_relation.retired", {
            "relation_id": relation_id,
            "reason": require_string(operation.get("reason"), "reason", max_len=4096),
        }

    def _prepare_declare_cardinality(self, operation: dict[str, Any]) -> tuple[str, dict[str, Any]]:
        constraint_id = require_id(operation.get("constraint_id") or new_id("crd"), "constraint_id")
        if self._exists("cardinality_constraints", "constraint_id", constraint_id):
            raise LacunaError(
                "duplicate-cardinality-constraint",
                f"cardinality constraint {constraint_id!r} already exists",
            )
        raw_claim_ids = require_list(operation.get("claim_ids"), "claim_ids")
        if not 2 <= len(raw_claim_ids) <= 256:
            raise LacunaError(
                "bad-cardinality-members",
                "claim_ids must contain between 2 and 256 distinct claims",
            )
        claim_ids: list[str] = []
        seen: set[str] = set()
        for index, value in enumerate(raw_claim_ids):
            claim_id = require_id(value, f"claim_ids[{index}]")
            self._require_claim(claim_id)
            if claim_id in seen:
                raise LacunaError(
                    "duplicate-cardinality-member",
                    f"claim {claim_id!r} appears more than once in claim_ids",
                )
            seen.add(claim_id)
            claim_ids.append(claim_id)
        claim_ids.sort()

        min_true = operation.get("min_true")
        max_true = operation.get("max_true")
        if isinstance(min_true, bool) or not isinstance(min_true, int):
            raise LacunaError("bad-cardinality-bound", "min_true must be an integer")
        if isinstance(max_true, bool) or not isinstance(max_true, int):
            raise LacunaError("bad-cardinality-bound", "max_true must be an integer")
        if not 0 <= min_true <= max_true <= len(claim_ids):
            raise LacunaError(
                "bad-cardinality-bound",
                "bounds must satisfy 0 <= min_true <= max_true <= number of members",
                {"min_true": min_true, "max_true": max_true, "member_count": len(claim_ids)},
            )
        if min_true == 0 and max_true == len(claim_ids):
            raise LacunaError(
                "vacuous-cardinality-constraint",
                "the requested bounds permit every valuation and constrain nothing",
            )
        source_id = optional_id(operation.get("source_id"), "source_id")
        if source_id is not None:
            self._require_source(source_id, "source_id")
        definition_sha256 = sha256_text(
            canonical_json(
                {"claim_ids": claim_ids, "min_true": min_true, "max_true": max_true}
            )
        )
        duplicate = self.conn.execute(
            """SELECT constraint_id FROM cardinality_constraints
               WHERE definition_sha256 = ? AND ended_seq IS NULL""",
            (definition_sha256,),
        ).fetchone()
        if duplicate is not None:
            raise LacunaError(
                "duplicate-active-cardinality-constraint",
                "an equivalent active cardinality constraint already exists",
                {"constraint_id": duplicate["constraint_id"]},
            )
        payload = {
            "constraint_id": constraint_id,
            "label": require_string(operation.get("label"), "label", max_len=512),
            "claim_ids": claim_ids,
            "min_true": min_true,
            "max_true": max_true,
            "definition_sha256": definition_sha256,
            "source_id": source_id,
            "rationale": require_string(operation.get("rationale"), "rationale", max_len=16384),
        }
        self._reject_cardinality_introduced_conflicts(payload)
        return "cardinality.declared", payload

    def _prepare_retire_cardinality(self, operation: dict[str, Any]) -> tuple[str, dict[str, Any]]:
        constraint_id = require_id(operation.get("constraint_id"), "constraint_id")
        self._require_cardinality(constraint_id, active=True)
        return "cardinality.retired", {
            "constraint_id": constraint_id,
            "reason": require_string(operation.get("reason"), "reason", max_len=4096),
        }

    def _normalize_interval(self, operation: dict[str, Any]) -> tuple[str, int | None, int | None]:
        timeline_id = require_id(operation.get("timeline_id", "main"), "timeline_id")
        valid_from = optional_tick(operation.get("valid_from"), "valid_from")
        valid_to = optional_tick(operation.get("valid_to"), "valid_to")
        if valid_from is not None and valid_to is not None and valid_from > valid_to:
            raise LacunaError("bad-valid-interval", "valid_from must be less than or equal to valid_to")
        return timeline_id, valid_from, valid_to

    def _prepare_record_assertion(self, operation: dict[str, Any]) -> tuple[str, dict[str, Any]]:
        assertion_id = require_id(operation.get("assertion_id") or new_id("ast"), "assertion_id")
        if self._exists("assertions", "assertion_id", assertion_id):
            raise LacunaError("duplicate-assertion", f"assertion {assertion_id!r} already exists")
        claim_id = require_id(operation.get("claim_id"), "claim_id")
        self._require_claim(claim_id)
        assertor_id = require_id(operation.get("assertor_id"), "assertor_id")
        perspective_id = require_id(operation.get("perspective_id", assertor_id), "perspective_id")
        self._require_agent(assertor_id, "assertor_id")
        self._require_agent(perspective_id, "perspective_id")
        source_id = optional_id(operation.get("source_id"), "source_id")
        if source_id is not None:
            self._require_source(source_id, "source_id")
        stance = require_enum(operation.get("stance"), "stance", STANCES)
        basis = require_enum(operation.get("basis"), "basis", BASES)
        standing = require_enum(operation.get("standing", "reported"), "standing", STANDINGS)
        confidence = optional_probability(operation.get("confidence"), "confidence")
        visibility = require_enum(operation.get("visibility", "private"), "visibility", VISIBILITIES)
        audience = normalize_audience(operation.get("audience"))
        for audience_id in audience:
            self._require_agent(audience_id, "audience")
        if visibility == "restricted" and not audience:
            raise LacunaError("empty-restricted-audience", "restricted assertions require at least one audience agent")
        if visibility != "restricted" and audience:
            raise LacunaError("unexpected-audience", "audience is permitted only when visibility is restricted")
        timeline_id, valid_from, valid_to = self._normalize_interval(operation)
        note = optional_string(operation.get("note"), "note", max_len=16384)
        supersedes_id = optional_id(operation.get("supersedes_id"), "supersedes_id")
        if supersedes_id is not None:
            self._require_assertion(supersedes_id, active=True)
            old = self.conn.execute(
                "SELECT claim_id, standing FROM assertions WHERE assertion_id = ?",
                (supersedes_id,),
            ).fetchone()
            if old["claim_id"] != claim_id:
                raise LacunaError("cross-claim-supersession", "an assertion may supersede only the same claim")
            if old["standing"] == "anchored":
                raise LacunaError(
                    "anchor-immutable",
                    "anchored assertions cannot be superseded; add an interpretation or fork custody instead",
                )
        if standing == "anchored" and stance == "unknown":
            raise LacunaError("unknown-anchor", "an anchored assertion cannot have unknown stance")
        if standing == "anchored":
            self._reject_anchor_conflicts(
                assertion_id=assertion_id,
                claim_id=claim_id,
                stance=stance,
                timeline_id=timeline_id,
                valid_from=valid_from,
                valid_to=valid_to,
            )
        payload = {
            "assertion_id": assertion_id,
            "claim_id": claim_id,
            "assertor_id": assertor_id,
            "perspective_id": perspective_id,
            "source_id": source_id,
            "stance": stance,
            "basis": basis,
            "standing": standing,
            "confidence": confidence,
            "visibility": visibility,
            "audience": audience,
            "timeline_id": timeline_id,
            "valid_from": valid_from,
            "valid_to": valid_to,
            "note": note,
            "supersedes_id": supersedes_id,
        }
        return "assertion.recorded", payload

    def _active_relation_rows(self) -> list[dict[str, Any]]:
        return [
            dict(row)
            for row in self.conn.execute(
                "SELECT * FROM claim_relations WHERE ended_seq IS NULL ORDER BY created_seq, relation_id"
            ).fetchall()
        ]

    def _active_cardinality_rows(self) -> list[dict[str, Any]]:
        rows = [
            dict(row)
            for row in self.conn.execute(
                """SELECT * FROM cardinality_constraints
                   WHERE ended_seq IS NULL ORDER BY created_seq, constraint_id"""
            ).fetchall()
        ]
        if not rows:
            return []
        members: dict[str, list[str]] = {str(row["constraint_id"]): [] for row in rows}
        for row in self.conn.execute(
            """SELECT cm.constraint_id, cm.claim_id
               FROM cardinality_members cm
               JOIN cardinality_constraints cc ON cc.constraint_id = cm.constraint_id
               WHERE cc.ended_seq IS NULL
               ORDER BY cm.constraint_id, cm.ordinal"""
        ).fetchall():
            members[str(row["constraint_id"])].append(str(row["claim_id"]))
        for row in rows:
            row["claim_ids"] = members[str(row["constraint_id"])]
        return rows

    def _first_cardinality_conflict(
        self,
        records: list[dict[str, Any]],
        *,
        constraints: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any] | None:
        for constraint in constraints if constraints is not None else self._active_cardinality_rows():
            conflict = cardinality_conflict(constraint, records)
            if conflict is not None:
                return conflict
        return None

    def _active_anchor_rows(self) -> list[dict[str, Any]]:
        return [
            dict(row)
            for row in self.conn.execute(
                """SELECT assertion_id, claim_id, stance, timeline_id, valid_from, valid_to
                   FROM assertions
                   WHERE standing = 'anchored' AND stance IN ('true', 'false') AND ended_seq IS NULL
                   ORDER BY created_seq, assertion_id"""
            ).fetchall()
        ]

    def _active_world_assignment_rows(
        self,
        *,
        world_id: str | None = None,
        active_worlds_only: bool = False,
    ) -> list[dict[str, Any]]:
        sql = """SELECT wa.assignment_id, wa.world_id, wa.claim_id, wa.truth,
                        wa.timeline_id, wa.valid_from, wa.valid_to
                 FROM world_assignments wa"""
        params: list[Any] = []
        conditions = ["wa.ended_seq IS NULL", "wa.truth IN ('true', 'false')"]
        if active_worlds_only:
            sql += " JOIN worlds w ON w.world_id = wa.world_id"
            conditions.append("w.status IN ('live', 'selected')")
        if world_id is not None:
            conditions.append("wa.world_id = ?")
            params.append(world_id)
        sql += " WHERE " + " AND ".join(conditions)
        sql += " ORDER BY wa.world_id, wa.created_seq, wa.assignment_id"
        return [dict(row) for row in self.conn.execute(sql, params).fetchall()]

    @staticmethod
    def _intervals_overlap_records(left: dict[str, Any], right: dict[str, Any]) -> bool:
        return intervals_overlap(
            str(left.get("timeline_id", "main")),
            left.get("valid_from"),
            left.get("valid_to"),
            str(right.get("timeline_id", "main")),
            right.get("valid_from"),
            right.get("valid_to"),
        )

    def _record_conflict(
        self,
        left: dict[str, Any],
        right: dict[str, Any],
        *,
        relations: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any] | None:
        if not self._intervals_overlap_records(left, right):
            return None
        left_truth = str(left.get("truth", left.get("stance")))
        right_truth = str(right.get("truth", right.get("stance")))
        left_claim_id = str(left["claim_id"])
        right_claim_id = str(right["claim_id"])
        if left_claim_id == right_claim_id:
            return pair_conflict(
                left_claim_id=left_claim_id,
                left_truth=left_truth,
                right_claim_id=right_claim_id,
                right_truth=right_truth,
            )
        for relation in relations if relations is not None else self._active_relation_rows():
            conflict = pair_conflict(
                left_claim_id=left_claim_id,
                left_truth=left_truth,
                right_claim_id=right_claim_id,
                right_truth=right_truth,
                relation=relation,
            )
            if conflict is not None:
                return conflict
        return None

    @staticmethod
    def _record_reference(record: dict[str, Any]) -> dict[str, Any]:
        for field in ("assertion_id", "assignment_id"):
            if record.get(field) is not None:
                return {field: record[field]}
        return {}

    def _reject_anchor_conflicts(
        self,
        *,
        assertion_id: str,
        claim_id: str,
        stance: str,
        timeline_id: str,
        valid_from: int | None,
        valid_to: int | None,
    ) -> None:
        candidate = {
            "candidate_kind": "assertion",
            "candidate_id": assertion_id,
            "claim_id": claim_id,
            "stance": stance,
            "timeline_id": timeline_id,
            "valid_from": valid_from,
            "valid_to": valid_to,
        }
        relations = self._active_relation_rows()
        anchors = self._active_anchor_rows()
        for existing in anchors:
            conflict = self._record_conflict(candidate, existing, relations=relations)
            if conflict is None:
                continue
            details = {**conflict, **self._record_reference(existing)}
            code = "anchor-contradiction" if claim_id == existing["claim_id"] else "anchor-relation-contradiction"
            raise LacunaError(
                code,
                "new anchor conflicts with an active anchor over an overlapping valid interval",
                details,
            )

        assignments = self._active_world_assignment_rows(active_worlds_only=True)
        for existing in assignments:
            conflict = self._record_conflict(candidate, existing, relations=relations)
            if conflict is None:
                continue
            raise LacunaError(
                "anchor-world-conflict",
                "new anchor conflicts with a live world; prune or revise that world first",
                {**conflict, **self._record_reference(existing), "world_id": existing["world_id"]},
            )

        constraints = self._active_cardinality_rows()
        if constraints:
            conflict = self._first_cardinality_conflict(
                [*anchors, candidate], constraints=constraints
            )
            if conflict is not None:
                raise LacunaError(
                    "anchor-cardinality-contradiction",
                    "new anchor makes an active cardinality constraint impossible",
                    conflict,
                )
            by_world: dict[str, list[dict[str, Any]]] = {}
            for assignment in assignments:
                by_world.setdefault(str(assignment["world_id"]), []).append(assignment)
            for world_id, records in by_world.items():
                conflict = self._first_cardinality_conflict(
                    [*anchors, candidate, *records], constraints=constraints
                )
                if conflict is not None:
                    raise LacunaError(
                        "anchor-world-cardinality-conflict",
                        "new anchor would make a live world violate a cardinality constraint",
                        {**conflict, "world_id": world_id},
                    )

    def _reject_world_assignment_conflicts(
        self,
        candidate: dict[str, Any],
        *,
        replaces_assignment_id: str | None = None,
    ) -> None:
        if candidate["truth"] == "unknown":
            return
        candidate_record = {
            **candidate,
            "candidate_kind": "world_assignment",
            "candidate_id": candidate["assignment_id"],
        }
        relations = self._active_relation_rows()
        anchors = self._active_anchor_rows()
        for anchor in anchors:
            conflict = self._record_conflict(candidate_record, anchor, relations=relations)
            if conflict is not None:
                raise LacunaError(
                    "world-contradicts-anchor",
                    "live worlds may not conflict with an anchored assertion over an overlapping valid interval",
                    {**conflict, "assertion_id": anchor["assertion_id"]},
                )

        existing_assignments = self._active_world_assignment_rows(world_id=candidate["world_id"])
        remaining_assignments: list[dict[str, Any]] = []
        for existing in existing_assignments:
            if existing["assignment_id"] == replaces_assignment_id:
                continue
            remaining_assignments.append(existing)
            conflict = self._record_conflict(candidate_record, existing, relations=relations)
            if conflict is not None:
                raise LacunaError(
                    "world-internal-conflict",
                    "candidate assignment conflicts with another active assignment in the same world",
                    {**conflict, "assignment_id": existing["assignment_id"], "world_id": candidate["world_id"]},
                )

        cardinality = self._first_cardinality_conflict(
            [*anchors, *remaining_assignments, candidate_record]
        )
        if cardinality is not None:
            raise LacunaError(
                "world-cardinality-conflict",
                "candidate assignment makes the world violate a cardinality constraint",
                {**cardinality, "world_id": candidate["world_id"]},
            )

    def _reject_relation_introduced_conflicts(self, relation: dict[str, Any]) -> None:
        claim_ids = (relation["left_claim_id"], relation["right_claim_id"])
        anchors = [
            dict(row)
            for row in self.conn.execute(
                """SELECT assertion_id, claim_id, stance, timeline_id, valid_from, valid_to
                   FROM assertions
                   WHERE standing = 'anchored' AND stance IN ('true', 'false') AND ended_seq IS NULL
                     AND claim_id IN (?, ?)""",
                claim_ids,
            ).fetchall()
        ]
        assignments = [
            dict(row)
            for row in self.conn.execute(
                """SELECT wa.assignment_id, wa.world_id, wa.claim_id, wa.truth,
                          wa.timeline_id, wa.valid_from, wa.valid_to
                   FROM world_assignments wa
                   JOIN worlds w ON w.world_id = wa.world_id
                   WHERE wa.ended_seq IS NULL AND wa.truth IN ('true', 'false')
                     AND w.status IN ('live', 'selected') AND wa.claim_id IN (?, ?)""",
                claim_ids,
            ).fetchall()
        ]

        def violation(left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any] | None:
            if left["claim_id"] == right["claim_id"]:
                return None
            return self._record_conflict(left, right, relations=[relation])

        for index, left in enumerate(anchors):
            for right in anchors[index + 1 :]:
                conflict = violation(left, right)
                if conflict is not None:
                    raise LacunaError(
                        "relation-introduces-conflict",
                        "relation would make existing anchors inconsistent",
                        {
                            **conflict,
                            "left_assertion_id": left["assertion_id"],
                            "right_assertion_id": right["assertion_id"],
                        },
                    )
        by_world: dict[str, list[dict[str, Any]]] = {}
        for assignment in assignments:
            by_world.setdefault(str(assignment["world_id"]), []).append(assignment)
        for world_id, records in by_world.items():
            for index, left in enumerate(records):
                for right in records[index + 1 :]:
                    conflict = violation(left, right)
                    if conflict is not None:
                        raise LacunaError(
                            "relation-introduces-conflict",
                            "relation would make an active candidate world internally inconsistent",
                            {
                                **conflict,
                                "world_id": world_id,
                                "left_assignment_id": left["assignment_id"],
                                "right_assignment_id": right["assignment_id"],
                            },
                        )
            for assignment in records:
                for anchor in anchors:
                    conflict = violation(assignment, anchor)
                    if conflict is not None:
                        raise LacunaError(
                            "relation-introduces-conflict",
                            "relation would make an active candidate world conflict with an anchor",
                            {
                                **conflict,
                                "world_id": world_id,
                                "assignment_id": assignment["assignment_id"],
                                "assertion_id": anchor["assertion_id"],
                            },
                        )

    def _reject_cardinality_introduced_conflicts(self, constraint: dict[str, Any]) -> None:
        anchors = self._active_anchor_rows()
        conflict = cardinality_conflict(constraint, anchors)
        if conflict is not None:
            raise LacunaError(
                "cardinality-introduces-conflict",
                "constraint would make existing anchors inconsistent",
                conflict,
            )
        assignments = self._active_world_assignment_rows(active_worlds_only=True)
        by_world: dict[str, list[dict[str, Any]]] = {}
        for assignment in assignments:
            by_world.setdefault(str(assignment["world_id"]), []).append(assignment)
        for world_id, records in by_world.items():
            conflict = cardinality_conflict(constraint, [*anchors, *records])
            if conflict is not None:
                raise LacunaError(
                    "cardinality-introduces-conflict",
                    "constraint would make an active candidate world inconsistent",
                    {**conflict, "world_id": world_id},
                )

    def _validate_world_consistency(self, world_id: str) -> None:
        relations = self._active_relation_rows()
        assignments = self._active_world_assignment_rows(world_id=world_id)
        for index, left in enumerate(assignments):
            for right in assignments[index + 1 :]:
                conflict = self._record_conflict(left, right, relations=relations)
                if conflict is not None:
                    raise LacunaError(
                        "world-reactivation-conflict",
                        "world cannot return to active consideration while internally inconsistent",
                        {
                            **conflict,
                            "world_id": world_id,
                            "left_assignment_id": left["assignment_id"],
                            "right_assignment_id": right["assignment_id"],
                        },
                    )
        anchors = self._active_anchor_rows()
        for assignment in assignments:
            for anchor in anchors:
                conflict = self._record_conflict(assignment, anchor, relations=relations)
                if conflict is not None:
                    raise LacunaError(
                        "world-reactivation-conflict",
                        "world cannot return to active consideration while it conflicts with an anchor",
                        {
                            **conflict,
                            "world_id": world_id,
                            "assignment_id": assignment["assignment_id"],
                            "assertion_id": anchor["assertion_id"],
                        },
                    )
        cardinality = self._first_cardinality_conflict([*anchors, *assignments])
        if cardinality is not None:
            raise LacunaError(
                "world-reactivation-cardinality-conflict",
                "world cannot return to active consideration while it violates a cardinality constraint",
                {**cardinality, "world_id": world_id},
            )

    def _prepare_supersede_assertion(self, operation: dict[str, Any]) -> tuple[str, dict[str, Any]]:
        assertion_id = require_id(operation.get("assertion_id"), "assertion_id")
        self._require_assertion(assertion_id, active=True)
        row = self.conn.execute(
            "SELECT standing FROM assertions WHERE assertion_id = ?",
            (assertion_id,),
        ).fetchone()
        if row["standing"] == "anchored":
            raise LacunaError(
                "anchor-immutable",
                "anchored assertions cannot be superseded; add an interpretation or fork custody instead",
            )
        reason = require_string(operation.get("reason"), "reason", max_len=4096)
        return "assertion.superseded", {"assertion_id": assertion_id, "reason": reason}

    def _prepare_create_world(self, operation: dict[str, Any]) -> tuple[str, dict[str, Any]]:
        world_id = require_id(operation.get("world_id") or new_id("wld"), "world_id")
        if self._exists("worlds", "world_id", world_id):
            raise LacunaError("duplicate-world", f"world {world_id!r} already exists")
        parent_world_id = optional_id(operation.get("parent_world_id"), "parent_world_id")
        if parent_world_id is not None:
            parent = self._require_world(parent_world_id)
            if parent["status"] in {"pruned", "archived"}:
                raise LacunaError("inactive-parent-world", "cannot fork a pruned or archived world")
        payload = {
            "world_id": world_id,
            "label": require_string(operation.get("label", world_id), "label", max_len=512),
            "parent_world_id": parent_world_id,
            "status": require_enum(operation.get("status", "live"), "status", WORLD_STATUSES),
            "weight": require_weight(operation.get("weight", 1.0)),
            "rationale": optional_string(operation.get("rationale"), "rationale", max_len=16384),
        }
        return "world.created", payload

    def _exact_active_world_assignment(
        self,
        *,
        world_id: str,
        claim_id: str,
        timeline_id: str,
        valid_from: int | None,
        valid_to: int | None,
    ) -> dict[str, Any] | None:
        interval_sql = _same_interval_sql()
        row = self.conn.execute(
            f"""SELECT * FROM world_assignments
                WHERE world_id = ? AND claim_id = ? AND {interval_sql} AND ended_seq IS NULL""",
            (
                world_id,
                claim_id,
                timeline_id,
                valid_from,
                valid_from,
                valid_to,
                valid_to,
            ),
        ).fetchone()
        return dict(row) if row is not None else None

    def _validate_commitment_provenance(
        self,
        *,
        commitment: str,
        basis: str,
        source_id: str | None,
    ) -> None:
        if basis not in WRITABLE_COMMITMENT_BASES:
            raise LacunaError(
                "reserved-legacy-commitment-basis",
                "legacy commitment custody may be created only by migration or ledger replay",
                {"basis": basis, "writable_bases": sorted(WRITABLE_COMMITMENT_BASES)},
            )
        if source_id is not None:
            self._require_source(source_id, "commitment_source_id")
        if commitment == "hard" and basis not in HARD_COMMITMENT_BASES:
            raise LacunaError(
                "hard-commitment-needs-durable-basis",
                "hard commitment requires authored, evidence, disclosure, or precommitment custody",
                {
                    "commitment": commitment,
                    "basis": basis,
                    "allowed_bases": sorted(HARD_COMMITMENT_BASES),
                },
            )
        if basis in SOURCE_EXPECTED_BASES and source_id is None:
            raise LacunaError(
                "commitment-source-required",
                f"commitment basis {basis!r} requires commitment_source_id",
                {"basis": basis},
            )
        if basis == "precommitment" and commitment != "hard":
            raise LacunaError(
                "invalid-precommitment",
                "precommitment is reserved for deliberately hard commitments",
            )

    def _active_consequence_rows(self) -> list[dict[str, Any]]:
        return [
            dict(row)
            for row in self.conn.execute(
                """SELECT * FROM consequence_links
                   WHERE ended_seq IS NULL ORDER BY created_seq, consequence_id"""
            ).fetchall()
        ]

    def _consequence_assignment_edges(
        self,
        *,
        exclude_consequence_id: str | None = None,
    ) -> list[tuple[str, str]]:
        sql = """SELECT premise_assignment_id, dependent_id
                 FROM consequence_links
                 WHERE ended_seq IS NULL AND dependent_kind = 'world_assignment'"""
        params: list[Any] = []
        if exclude_consequence_id is not None:
            sql += " AND consequence_id <> ?"
            params.append(exclude_consequence_id)
        sql += " ORDER BY created_seq, consequence_id"
        return [
            (str(row["premise_assignment_id"]), str(row["dependent_id"]))
            for row in self.conn.execute(sql, params).fetchall()
        ]

    def _validate_consequence_target(
        self,
        kind: str,
        dependent_id: str,
        *,
        active: bool = True,
    ) -> None:
        """Validate a typed consequence endpoint without creating orphan custody."""
        if kind == "assertion":
            self._require_assertion(dependent_id, active=active)
            return
        if kind == "world_assignment":
            self._require_world_assignment(dependent_id, active=active)
            return
        if kind == "question":
            sql = "SELECT 1 FROM questions WHERE question_id = ?"
            if active:
                sql += " AND status = 'open'"
            row = self.conn.execute(sql, (dependent_id,)).fetchone()
            if row is None:
                qualifier = "open " if active else ""
                raise LacunaError(
                    "unknown-question",
                    f"unknown {qualifier}question {dependent_id!r}",
                )
            return
        raise AssertionError(kind)

    def _consequence_dependent_state(self, kind: str, dependent_id: str) -> dict[str, Any]:
        """Return lifecycle state for a typed consequence target."""
        if kind == "assertion":
            row = self.conn.execute(
                "SELECT claim_id, ended_seq FROM assertions WHERE assertion_id = ?",
                (dependent_id,),
            ).fetchone()
            if row is None:
                return {"exists": False, "active": False, "state": "missing", "claim_id": None}
            return {
                "exists": True,
                "active": row["ended_seq"] is None,
                "state": "active" if row["ended_seq"] is None else "ended",
                "claim_id": row["claim_id"],
            }
        if kind == "world_assignment":
            row = self.conn.execute(
                "SELECT claim_id, world_id, ended_seq FROM world_assignments WHERE assignment_id = ?",
                (dependent_id,),
            ).fetchone()
            if row is None:
                return {
                    "exists": False,
                    "active": False,
                    "state": "missing",
                    "claim_id": None,
                    "world_id": None,
                }
            return {
                "exists": True,
                "active": row["ended_seq"] is None,
                "state": "active" if row["ended_seq"] is None else "ended",
                "claim_id": row["claim_id"],
                "world_id": row["world_id"],
            }
        if kind == "question":
            row = self.conn.execute(
                "SELECT about_claim_id, status FROM questions WHERE question_id = ?",
                (dependent_id,),
            ).fetchone()
            if row is None:
                return {"exists": False, "active": False, "state": "missing", "claim_id": None}
            return {
                "exists": True,
                "active": row["status"] == "open",
                "state": str(row["status"]),
                "claim_id": row["about_claim_id"],
            }
        raise AssertionError(kind)

    def _consequence_closure(self, assignment_id: str) -> dict[str, Any]:
        """Traverse explicit assignment consequences with deterministic hard bounds."""
        rows = self._active_consequence_rows()
        by_premise: dict[str, list[dict[str, Any]]] = {}
        for row in rows:
            by_premise.setdefault(str(row["premise_assignment_id"]), []).append(row)

        queue: list[tuple[str, int, list[str]]] = [(assignment_id, 0, [assignment_id])]
        expanded: set[str] = set()
        seen_nodes = {f"world_assignment:{assignment_id}"}
        links: list[dict[str, Any]] = []
        truncation_reasons: list[str] = []

        while queue:
            premise_id, depth, path = queue.pop(0)
            if premise_id in expanded:
                continue
            expanded.add(premise_id)
            outgoing = by_premise.get(premise_id, [])
            if depth >= REVISION_GRAPH_MAX_DEPTH and outgoing:
                if "max-depth" not in truncation_reasons:
                    truncation_reasons.append("max-depth")
                continue
            for row in outgoing:
                dependent_kind = str(row["dependent_kind"])
                dependent_id = str(row["dependent_id"])
                node_key = f"{dependent_kind}:{dependent_id}"
                if node_key not in seen_nodes and len(seen_nodes) >= REVISION_GRAPH_MAX_NODES:
                    if "max-nodes" not in truncation_reasons:
                        truncation_reasons.append("max-nodes")
                    continue
                seen_nodes.add(node_key)
                item = {
                    "consequence_id": str(row["consequence_id"]),
                    "premise_assignment_id": premise_id,
                    "dependent_kind": dependent_kind,
                    "dependent_id": dependent_id,
                    "relation": str(row["relation"]),
                    "severity": str(row["severity"]),
                    "source_id": row["source_id"],
                    "rationale": str(row["rationale"]),
                    "direction": "outgoing",
                    "depth": depth + 1,
                    "path": [*path, dependent_id],
                }
                links.append(item)
                if dependent_kind == "world_assignment" and dependent_id not in expanded:
                    queue.append((dependent_id, depth + 1, [*path, dependent_id]))

        links.sort(key=lambda item: (int(item["depth"]), str(item["consequence_id"])))
        return {
            "complete": not truncation_reasons,
            "truncation_reasons": truncation_reasons,
            "expanded_assignment_count": len(expanded),
            "node_count": len(seen_nodes),
            "limits": {
                "max_depth": REVISION_GRAPH_MAX_DEPTH,
                "max_nodes": REVISION_GRAPH_MAX_NODES,
            },
            "links": links,
        }

    def _revision_consequence_scope(self, assignment_id: str) -> dict[str, Any]:
        """Return the one authoritative consequence scope for revision policy.

        Outgoing links are traversed transitively because changing a premise can
        invalidate consequences reached through intermediate world assignments.
        Incoming links are incident only: changing this assignment invalidates the
        authored edge that points at it, but does not imply that every ancestor of
        that edge must itself be revised.
        """
        closure = self._consequence_closure(assignment_id)
        incoming_links = [
            {
                "consequence_id": str(row["consequence_id"]),
                "premise_assignment_id": str(row["premise_assignment_id"]),
                "dependent_kind": "world_assignment",
                "dependent_id": assignment_id,
                "relation": str(row["relation"]),
                "severity": str(row["severity"]),
                "source_id": row["source_id"],
                "rationale": str(row["rationale"]),
                "direction": "incoming",
                "depth": 0,
                "path": [str(row["premise_assignment_id"]), assignment_id],
            }
            for row in self.conn.execute(
                """SELECT * FROM consequence_links
                   WHERE dependent_kind = 'world_assignment' AND dependent_id = ?
                     AND ended_seq IS NULL
                   ORDER BY created_seq, consequence_id""",
                (assignment_id,),
            ).fetchall()
        ]
        explicit_consequences = sorted(
            [*incoming_links, *closure["links"]],
            key=lambda item: (
                0 if item["direction"] == "incoming" else 1,
                int(item["depth"]),
                str(item["consequence_id"]),
            ),
        )

        def counts(items: Iterable[dict[str, Any]]) -> dict[str, int]:
            result = {severity: 0 for severity in sorted(CONSEQUENCE_SEVERITIES)}
            for item in items:
                result[str(item["severity"])] += 1
            return result

        direct_outgoing = [
            item
            for item in explicit_consequences
            if item["direction"] == "outgoing" and int(item["depth"]) == 1
        ]
        direct_incoming = [
            item for item in explicit_consequences if item["direction"] == "incoming"
        ]
        return {
            "traversal": {key: value for key, value in closure.items() if key != "links"},
            "explicit_consequences": explicit_consequences,
            "direct_outgoing_counts": counts(direct_outgoing),
            "direct_incoming_counts": counts(direct_incoming),
            "reachable_counts": counts(explicit_consequences),
            "binding_consequence_ids": sorted(
                str(item["consequence_id"])
                for item in explicit_consequences
                if item["severity"] == "binding"
            ),
        }

    def _active_assignment_revision_successors(self, assignment_id: str) -> list[str]:
        """Return active descendants in the explicit revision lineage, nearest first."""
        queue = [assignment_id]
        seen = {assignment_id}
        active: list[tuple[int, int, str]] = []
        depth = 0
        while queue:
            next_queue: list[str] = []
            for parent_id in queue:
                rows = self.conn.execute(
                    """SELECT assignment_id, created_seq, ended_seq
                       FROM world_assignments
                       WHERE revision_of_assignment_id = ?
                       ORDER BY created_seq, assignment_id""",
                    (parent_id,),
                ).fetchall()
                for row in rows:
                    child_id = str(row["assignment_id"])
                    if child_id in seen:
                        continue
                    seen.add(child_id)
                    next_queue.append(child_id)
                    if row["ended_seq"] is None:
                        active.append((depth + 1, int(row["created_seq"]), child_id))
            queue = next_queue
            depth += 1
        return [item[2] for item in sorted(active)]

    def _active_assertion_successors(self, assertion_id: str) -> list[str]:
        """Return active descendants in assertion supersession custody, nearest first."""
        queue = [assertion_id]
        seen = {assertion_id}
        active: list[tuple[int, int, str]] = []
        depth = 0
        while queue:
            next_queue: list[str] = []
            for parent_id in queue:
                rows = self.conn.execute(
                    """SELECT assertion_id, created_seq, ended_seq
                       FROM assertions WHERE supersedes_id = ?
                       ORDER BY created_seq, assertion_id""",
                    (parent_id,),
                ).fetchall()
                for row in rows:
                    child_id = str(row["assertion_id"])
                    if child_id in seen:
                        continue
                    seen.add(child_id)
                    next_queue.append(child_id)
                    if row["ended_seq"] is None:
                        active.append((depth + 1, int(row["created_seq"]), child_id))
            queue = next_queue
            depth += 1
        return [item[2] for item in sorted(active)]

    def consequence_repair_review(
        self,
        consequence_id: str,
        *,
        _digest_head: str | None = None,
    ) -> dict[str, Any]:
        """Return a current-head receipt for replacing one consequence link.

        The review does not choose a successor or claim that a replacement preserves
        causality. It exposes lifecycle state and known explicit successor lineages so
        a human or planner can author a replacement deliberately.
        """
        consequence_id = require_id(consequence_id, "consequence_id")
        self._require_consequence(consequence_id)
        link = next(
            item
            for item in self.consequence_links(include_retired=True)
            if item["consequence_id"] == consequence_id
        )
        blockers: list[dict[str, Any]] = []
        if link["ended_seq"] is not None:
            blockers.append(
                {
                    "code": "consequence-inactive",
                    "message": "only an active consequence may be replaced",
                }
            )
        if link.get("replacement_consequence_id") is not None:
            blockers.append(
                {
                    "code": "consequence-already-replaced",
                    "message": "the consequence already has a recorded successor",
                    "replacement_consequence_id": link["replacement_consequence_id"],
                }
            )

        premise_successors = self._active_assignment_revision_successors(
            str(link["premise_assignment_id"])
        )
        dependent_successors: list[str] = []
        dependent_kind = str(link["dependent_kind"])
        if dependent_kind == "world_assignment":
            dependent_successors = self._active_assignment_revision_successors(
                str(link["dependent_id"])
            )
        elif dependent_kind == "assertion":
            dependent_successors = self._active_assertion_successors(
                str(link["dependent_id"])
            )

        target = {
            key: link.get(key)
            for key in (
                "consequence_id",
                "premise_assignment_id",
                "premise_world_id",
                "premise_claim_id",
                "premise_active",
                "dependent_kind",
                "dependent_id",
                "dependent_claim_id",
                "dependent_active",
                "dependent_state",
                "relation",
                "severity",
                "source_id",
                "rationale",
                "created_seq",
                "ended_seq",
                "repair_required",
                "originating_repair_id",
                "replaces_consequence_id",
                "replacement_repair_id",
                "replacement_consequence_id",
                "lineage_state",
            )
        }
        digest_head = self.head() if _digest_head is None else _digest_head
        known_successors = {
            "premise_assignment_ids": premise_successors,
            "dependent_kind": dependent_kind,
            "dependent_ids": dependent_successors,
        }
        digest_core = {
            "policy": CONSEQUENCE_REPAIR_POLICY,
            "cube_id": self.meta("cube_id"),
            "head": digest_head,
            "target": target,
            "known_successors": known_successors,
            "blockers": blockers,
        }
        review_sha256 = consequence_repair_review_sha256(
            cube_id=str(digest_core["cube_id"]),
            head=digest_head,
            target=target,
            known_successors=known_successors,
            blockers=blockers,
        )
        return {
            "event": "lacuna.consequence-repair-review",
            "schema": "lacuna.consequence-repair-review.v1",
            **digest_core,
            "repair_review_sha256": review_sha256,
            "review": {
                "replaceable": not blockers,
                "required_operation": "replace_consequence",
                "expected_repair_sha256": review_sha256,
                "mode": "orphan-repair" if link["repair_required"] else "semantic-replacement",
            },
            "nonclaims": [
                "Known successors are lineage candidates, not automatic semantic equivalents.",
                "Replacing a consequence records authored custody; it does not prove causality.",
                "The digest is bound to a change-set base head; any separately committed intervening change makes it stale.",
            ],
        }

    def revision_impact(
        self,
        assignment_id: str,
        *,
        _digest_head: str | None = None,
    ) -> dict[str, Any]:
        """Return a digest-bound planner review of revising one recorded assignment.

        Ambient exposure is conservative proximity, not inferred causality. Only
        explicit consequence links claim authored dependence, and only binding
        links plus hard commitment prevent in-place revision.
        """
        assignment_id = require_id(assignment_id, "assignment_id")
        assignment = self._require_world_assignment(assignment_id)
        world = self._require_world(str(assignment["world_id"]))
        claim_id = str(assignment["claim_id"])
        interval_record = {
            "timeline_id": str(assignment["timeline_id"]),
            "valid_from": assignment["valid_from"],
            "valid_to": assignment["valid_to"],
        }

        assertions: list[dict[str, Any]] = []
        assertion_counts = {"public": 0, "restricted": 0, "private": 0}
        anchored_count = 0
        assertion_rows = self.conn.execute(
            """SELECT assertion_id, stance, basis, standing, visibility,
                      timeline_id, valid_from, valid_to, created_seq, ended_seq
               FROM assertions WHERE claim_id = ?
               ORDER BY created_seq, assertion_id""",
            (claim_id,),
        ).fetchall()
        for row in assertion_rows:
            item = dict(row)
            if not self._intervals_overlap_records(interval_record, item):
                continue
            visibility = str(item["visibility"])
            assertion_counts[visibility] += 1
            if item["standing"] == "anchored" and item["ended_seq"] is None:
                anchored_count += 1
            assertions.append(
                {
                    "assertion_id": str(item["assertion_id"]),
                    "stance": str(item["stance"]),
                    "basis": str(item["basis"]),
                    "standing": str(item["standing"]),
                    "visibility": visibility,
                    "timeline_id": str(item["timeline_id"]),
                    "valid_from": item["valid_from"],
                    "valid_to": item["valid_to"],
                    "active": item["ended_seq"] is None,
                }
            )

        evidence_links: list[dict[str, Any]] = []
        evidence_rows = self.conn.execute(
            """SELECT el.*, ea.claim_id AS evidence_claim_id
               FROM evidence_links el
               JOIN assertions ea ON ea.assertion_id = el.evidence_assertion_id
               WHERE el.target_claim_id = ? OR ea.claim_id = ?
               ORDER BY el.created_seq, el.link_id""",
            (claim_id, claim_id),
        ).fetchall()
        for row in evidence_rows:
            item = dict(row)
            if item["world_id"] is not None and item["world_id"] != assignment["world_id"]:
                continue
            evidence_links.append(
                {
                    "link_id": str(item["link_id"]),
                    "relation": str(item["relation"]),
                    "world_id": item["world_id"],
                    "role": "target" if item["target_claim_id"] == claim_id else "evidence",
                    "active": item["ended_seq"] is None,
                }
            )

        questions = [
            {
                "question_id": str(row["question_id"]),
                "status": str(row["status"]),
                "visibility": str(row["visibility"]),
            }
            for row in self.conn.execute(
                """SELECT question_id, status, visibility FROM questions
                   WHERE about_claim_id = ? ORDER BY created_seq, question_id""",
                (claim_id,),
            ).fetchall()
        ]
        relations = [
            {
                "relation_id": str(row["relation_id"]),
                "relation": str(row["relation"]),
            }
            for row in self.conn.execute(
                """SELECT relation_id, relation FROM claim_relations
                   WHERE ended_seq IS NULL AND (left_claim_id = ? OR right_claim_id = ?)
                   ORDER BY created_seq, relation_id""",
                (claim_id, claim_id),
            ).fetchall()
        ]
        cardinalities = [
            {
                "constraint_id": str(row["constraint_id"]),
                "label": str(row["label"]),
            }
            for row in self.conn.execute(
                """SELECT cc.constraint_id, cc.label
                   FROM cardinality_members cm
                   JOIN cardinality_constraints cc ON cc.constraint_id = cm.constraint_id
                   WHERE cm.claim_id = ? AND cc.ended_seq IS NULL
                   ORDER BY cc.created_seq, cc.constraint_id""",
                (claim_id,),
            ).fetchall()
        ]

        inherited_live_assignments: list[dict[str, Any]] = []
        pending = [assignment_id]
        seen = {assignment_id}
        while pending:
            parent_id = pending.pop(0)
            child_rows = self.conn.execute(
                """SELECT wa.assignment_id, wa.world_id, wa.inherited_from_assignment_id,
                          wa.ended_seq, w.status AS world_status
                   FROM world_assignments wa
                   JOIN worlds w ON w.world_id = wa.world_id
                   WHERE wa.inherited_from_assignment_id = ?
                   ORDER BY wa.created_seq, wa.assignment_id""",
                (parent_id,),
            ).fetchall()
            for row in child_rows:
                item = dict(row)
                child_id = str(item["assignment_id"])
                if child_id in seen:
                    continue
                seen.add(child_id)
                pending.append(child_id)
                if item["ended_seq"] is None and item["world_status"] in {"live", "selected"}:
                    inherited_live_assignments.append(
                        {
                            "assignment_id": child_id,
                            "world_id": str(item["world_id"]),
                            "world_status": str(item["world_status"]),
                            "inherited_from_assignment_id": str(item["inherited_from_assignment_id"]),
                        }
                    )

        interval_sql = _same_interval_sql("wa")
        consensus_rows = self.conn.execute(
            f"""SELECT wa.world_id
                FROM world_assignments wa
                JOIN worlds w ON w.world_id = wa.world_id
                WHERE wa.claim_id = ? AND wa.truth = ? AND {interval_sql}
                  AND wa.ended_seq IS NULL AND w.status IN ('live', 'selected')
                ORDER BY wa.world_id""",
            (
                claim_id,
                assignment["truth"],
                assignment["timeline_id"],
                assignment["valid_from"],
                assignment["valid_from"],
                assignment["valid_to"],
                assignment["valid_to"],
            ),
        ).fetchall()
        consensus_world_ids = [str(row["world_id"]) for row in consensus_rows]

        consequence_scope = self._revision_consequence_scope(assignment_id)
        explicit_consequences = consequence_scope["explicit_consequences"]
        traversal = consequence_scope["traversal"]
        blockers: list[dict[str, Any]] = []
        if assignment["ended_seq"] is not None:
            blockers.append(
                {"code": "assignment-inactive", "message": "only an active assignment may be revised"}
            )
        if assignment["commitment"] == "hard":
            blockers.append(
                {
                    "code": "hard-commitment",
                    "message": "hard commitments require a world fork or explicit custody repair",
                }
            )
        binding_ids = consequence_scope["binding_consequence_ids"]
        if binding_ids:
            blockers.append(
                {
                    "code": "binding-consequence",
                    "message": "active binding consequences must be retired or repaired before revision",
                    "consequence_ids": binding_ids,
                }
            )
        if not traversal["complete"]:
            blockers.append(
                {
                    "code": "impact-traversal-truncated",
                    "message": "revision impact exceeded deterministic safety bounds",
                    "reasons": traversal["truncation_reasons"],
                }
            )

        burden = calculate_revision_burden(
            commitment=str(assignment["commitment"]),
            world_status=str(world["status"]),
            public_assertions=assertion_counts["public"],
            restricted_assertions=assertion_counts["restricted"],
            private_assertions=assertion_counts["private"],
            anchored_assertions=anchored_count,
            evidence_links=len(evidence_links),
            open_questions=sum(1 for item in questions if item["status"] == "open"),
            structural_constraints=len(relations) + len(cardinalities),
            inherited_live_assignments=len(inherited_live_assignments),
            consensus_world_count=len(consensus_world_ids),
            consequence_severities=[str(item["severity"]) for item in explicit_consequences],
            blocker_count=len(blockers),
        )
        target = {
            "assignment_id": assignment_id,
            "world_id": str(assignment["world_id"]),
            "world_status": str(world["status"]),
            "claim_id": claim_id,
            "truth": str(assignment["truth"]),
            "commitment": str(assignment["commitment"]),
            "commitment_basis": str(assignment["commitment_basis"]),
            "timeline_id": str(assignment["timeline_id"]),
            "valid_from": assignment["valid_from"],
            "valid_to": assignment["valid_to"],
            "active": assignment["ended_seq"] is None,
        }
        footprint = {
            "assertions": assertions,
            "evidence_links": evidence_links,
            "questions": questions,
            "claim_relations": relations,
            "cardinality_constraints": cardinalities,
            "inherited_live_assignments": inherited_live_assignments,
            "consensus_world_ids": consensus_world_ids,
        }
        digest_core = {
            "policy": "lacuna.governed-revision.v1",
            "cube_id": self.meta("cube_id"),
            "head": self.head() if _digest_head is None else _digest_head,
            "target": target,
            "explicit_consequences": explicit_consequences,
            "derived_footprint": footprint,
            "traversal": traversal,
            "blockers": blockers,
            "burden": burden,
        }
        impact_sha256 = sha256_text(canonical_json(digest_core))
        return {
            "event": "lacuna.revision-impact",
            "schema": "lacuna.revision-impact.v1",
            **digest_core,
            "impact_sha256": impact_sha256,
            "review": {
                "revisable": not blockers,
                "required_operation": "revise_world",
                "expected_impact_sha256": impact_sha256,
                "incident_consequence_disposition": {
                    "policy": (
                        "nonbinding links remain active as explicit repair obligations; "
                        "retire or relink them deliberately"
                    ),
                    "retained_consequence_ids": sorted(
                        {
                            str(item["consequence_id"])
                            for item in explicit_consequences
                            if int(item["depth"]) <= 1
                            and (
                                item["premise_assignment_id"] == assignment_id
                                or (
                                    item["dependent_kind"] == "world_assignment"
                                    and item["dependent_id"] == assignment_id
                                )
                            )
                        }
                    ),
                },
            },
            "nonclaims": [
                "This report measures recorded revision custody, not objective narrative value.",
                "Derived footprint records proximity and exposure; only explicit consequence links claim dependence.",
                "The digest is bound to a change-set base head; any separately committed intervening change makes it stale.",
            ],
        }

    def revision_guards(self, *, world_id: str | None = None) -> list[dict[str, Any]]:
        """Return planner guards derived from the same scope as revision_impact."""
        params: list[Any] = []
        sql = """SELECT wa.assignment_id, wa.world_id, wa.claim_id, wa.truth,
                        wa.commitment, wa.commitment_basis, wa.timeline_id,
                        wa.valid_from, wa.valid_to, w.status AS world_status
                 FROM world_assignments wa JOIN worlds w ON w.world_id = wa.world_id
                 WHERE wa.ended_seq IS NULL AND w.status IN ('live', 'selected')"""
        if world_id is not None:
            self._require_world(world_id)
            sql += " AND wa.world_id = ?"
            params.append(world_id)
        sql += " ORDER BY wa.world_id, wa.created_seq, wa.assignment_id"

        guards: list[dict[str, Any]] = []
        for row in self.conn.execute(sql, params).fetchall():
            item = dict(row)
            assignment_id = str(item["assignment_id"])
            scope = self._revision_consequence_scope(assignment_id)
            blocker_codes: list[str] = []
            if item["commitment"] == "hard":
                blocker_codes.append("hard-commitment")
            if scope["binding_consequence_ids"]:
                blocker_codes.append("binding-consequence")
            if not scope["traversal"]["complete"]:
                blocker_codes.append("impact-traversal-truncated")
            direct_incident_counts = {
                severity: (
                    scope["direct_outgoing_counts"][severity]
                    + scope["direct_incoming_counts"][severity]
                )
                for severity in sorted(CONSEQUENCE_SEVERITIES)
            }
            guards.append(
                {
                    **item,
                    "outgoing_consequence_counts": scope["direct_outgoing_counts"],
                    "incoming_consequence_counts": scope["direct_incoming_counts"],
                    "incident_consequence_counts": direct_incident_counts,
                    "reachable_consequence_counts": scope["reachable_counts"],
                    "binding_consequence_ids": scope["binding_consequence_ids"],
                    "impact_traversal_complete": scope["traversal"]["complete"],
                    "revision_blockers": blocker_codes,
                    "revision_blocked": bool(blocker_codes),
                }
            )
        return guards

    def _prepare_assign_world(self, operation: dict[str, Any]) -> tuple[str, dict[str, Any]]:
        assignment_id = require_id(operation.get("assignment_id") or new_id("asn"), "assignment_id")
        if self._exists("world_assignments", "assignment_id", assignment_id):
            raise LacunaError("duplicate-assignment", f"assignment {assignment_id!r} already exists")
        world_id = require_id(operation.get("world_id"), "world_id")
        world = self._require_world(world_id)
        if world["status"] in {"pruned", "archived"}:
            raise LacunaError("inactive-world", "cannot assign facts to a pruned or archived world")
        claim_id = require_id(operation.get("claim_id"), "claim_id")
        self._require_claim(claim_id)
        truth = require_enum(operation.get("truth"), "truth", STANCES)
        commitment = require_enum(operation.get("commitment", "tentative"), "commitment", COMMITMENTS)
        commitment_basis = require_enum(
            operation.get("commitment_basis", "planning"),
            "commitment_basis",
            COMMITMENT_BASES,
        )
        commitment_source_id = optional_id(
            operation.get("commitment_source_id"), "commitment_source_id"
        )
        self._validate_commitment_provenance(
            commitment=commitment,
            basis=commitment_basis,
            source_id=commitment_source_id,
        )
        confidence = optional_probability(operation.get("confidence"), "confidence")
        source_assertion_id = optional_id(operation.get("source_assertion_id"), "source_assertion_id")
        if source_assertion_id is not None:
            self._require_assertion(source_assertion_id)
        timeline_id, valid_from, valid_to = self._normalize_interval(operation)
        occupied = self._exact_active_world_assignment(
            world_id=world_id,
            claim_id=claim_id,
            timeline_id=timeline_id,
            valid_from=valid_from,
            valid_to=valid_to,
        )
        if occupied is not None:
            raise LacunaError(
                "assignment-slot-occupied",
                "assign_world cannot replace an active assignment; review and use revise_world",
                {
                    "current_assignment_id": occupied["assignment_id"],
                    "next_operation": "revision-impact",
                },
            )
        payload = {
            "assignment_id": assignment_id,
            "world_id": world_id,
            "claim_id": claim_id,
            "truth": truth,
            "commitment": commitment,
            "commitment_basis": commitment_basis,
            "commitment_source_id": commitment_source_id,
            "confidence": confidence,
            "rationale": optional_string(operation.get("rationale"), "rationale", max_len=16384),
            "source_assertion_id": source_assertion_id,
            "timeline_id": timeline_id,
            "valid_from": valid_from,
            "valid_to": valid_to,
        }
        self._reject_world_assignment_conflicts(payload)
        return "world.assigned", payload

    def _prepare_revise_world(
        self,
        operation: dict[str, Any],
        *,
        review_head: str | None = None,
    ) -> tuple[str, dict[str, Any]]:
        assignment_id = require_id(operation.get("assignment_id") or new_id("asn"), "assignment_id")
        if self._exists("world_assignments", "assignment_id", assignment_id):
            raise LacunaError("duplicate-assignment", f"assignment {assignment_id!r} already exists")
        old_id = require_id(operation.get("revises_assignment_id"), "revises_assignment_id")
        previous = self._require_world_assignment(old_id, active=True)
        world = self._require_world(str(previous["world_id"]))
        if world["status"] in {"pruned", "archived"}:
            raise LacunaError("inactive-world", "cannot revise facts in a pruned or archived world")
        expected_impact = require_string(
            operation.get("expected_impact_sha256"), "expected_impact_sha256", max_len=64
        )
        if not SHA256_RE.fullmatch(expected_impact):
            raise LacunaError(
                "bad-impact-digest", "expected_impact_sha256 must be a lowercase SHA-256 digest"
            )
        impact = self.revision_impact(old_id, _digest_head=review_head)
        if expected_impact != impact["impact_sha256"]:
            raise LacunaError(
                "stale-revision-impact",
                "revision impact receipt does not match current custody",
                {
                    "expected": impact["impact_sha256"],
                    "provided": expected_impact,
                    "review_head": impact["head"],
                    "current_head": self.head(),
                },
            )
        if impact["blockers"]:
            raise LacunaError(
                "revision-blocked",
                "recorded commitment or consequences block in-place revision",
                {"assignment_id": old_id, "blockers": impact["blockers"]},
            )
        truth = require_enum(operation.get("truth"), "truth", STANCES)
        if truth == previous["truth"]:
            raise LacunaError("revision-unchanged", "revised truth must differ from the current truth")
        commitment = require_enum(operation.get("commitment", "tentative"), "commitment", COMMITMENTS)
        if commitment not in {"tentative", "soft"}:
            raise LacunaError(
                "revision-overcommitted",
                "a revised assignment may begin only tentative or soft; raise commitment separately",
            )
        commitment_basis = require_enum(
            operation.get("commitment_basis", "planning"),
            "commitment_basis",
            COMMITMENT_BASES,
        )
        commitment_source_id = optional_id(
            operation.get("commitment_source_id"), "commitment_source_id"
        )
        self._validate_commitment_provenance(
            commitment=commitment,
            basis=commitment_basis,
            source_id=commitment_source_id,
        )
        if commitment_basis == "precommitment":
            raise LacunaError(
                "invalid-precommitment",
                "precommitment cannot be retroactively attached during revision",
            )
        source_assertion_id = optional_id(operation.get("source_assertion_id"), "source_assertion_id")
        if source_assertion_id is not None:
            self._require_assertion(source_assertion_id)
        payload = {
            "assignment_id": assignment_id,
            "world_id": str(previous["world_id"]),
            "claim_id": str(previous["claim_id"]),
            "truth": truth,
            "commitment": commitment,
            "commitment_basis": commitment_basis,
            "commitment_source_id": commitment_source_id,
            "confidence": optional_probability(operation.get("confidence"), "confidence"),
            "rationale": optional_string(operation.get("rationale"), "rationale", max_len=16384),
            "source_assertion_id": source_assertion_id,
            "timeline_id": str(previous["timeline_id"]),
            "valid_from": previous["valid_from"],
            "valid_to": previous["valid_to"],
            "revision_of_assignment_id": old_id,
            "revision_reason": require_string(operation.get("reason"), "reason", max_len=4096),
            "revision_impact_sha256": expected_impact,
        }
        self._reject_world_assignment_conflicts(payload, replaces_assignment_id=old_id)
        return "world.revised", payload

    def _prepare_raise_commitment(self, operation: dict[str, Any]) -> tuple[str, dict[str, Any]]:
        transition_id = require_id(
            operation.get("transition_id") or new_id("cmt"), "transition_id"
        )
        if self._exists("commitment_transitions", "transition_id", transition_id):
            raise LacunaError(
                "duplicate-commitment-transition",
                f"commitment transition {transition_id!r} already exists",
            )
        assignment_id = require_id(operation.get("assignment_id"), "assignment_id")
        assignment = self._require_world_assignment(assignment_id, active=True)
        target = require_enum(operation.get("commitment"), "commitment", COMMITMENTS)
        previous = str(assignment["commitment"])
        if not is_strict_raise(previous, target):
            raise LacunaError(
                "commitment-not-raised",
                "commitment transitions must move strictly upward; lowering requires a world fork or an explicit future repair protocol",
                {"from": previous, "to": target},
            )
        if not is_adjacent_raise(previous, target):
            raise LacunaError(
                "commitment-transition-not-adjacent",
                "commitment raises must cross one review boundary at a time",
                {"from": previous, "to": target},
            )
        basis = require_enum(operation.get("basis"), "basis", COMMITMENT_BASES)
        source_id = optional_id(operation.get("source_id"), "source_id")
        self._validate_commitment_provenance(
            commitment=target,
            basis=basis,
            source_id=source_id,
        )
        return "world.commitment_raised", {
            "transition_id": transition_id,
            "assignment_id": assignment_id,
            "from_commitment": previous,
            "to_commitment": target,
            "basis": basis,
            "source_id": source_id,
            "rationale": require_string(operation.get("rationale"), "rationale", max_len=16384),
        }

    def _prepare_link_consequence(self, operation: dict[str, Any]) -> tuple[str, dict[str, Any]]:
        consequence_id = require_id(
            operation.get("consequence_id") or new_id("csq"), "consequence_id"
        )
        if self._exists("consequence_links", "consequence_id", consequence_id):
            raise LacunaError(
                "duplicate-consequence", f"consequence {consequence_id!r} already exists"
            )
        premise_id = require_id(operation.get("premise_assignment_id"), "premise_assignment_id")
        self._require_world_assignment(premise_id, active=True)
        dependent_kind = require_enum(
            operation.get("dependent_kind"),
            "dependent_kind",
            CONSEQUENCE_DEPENDENT_KINDS,
        )
        dependent_id = require_id(operation.get("dependent_id"), "dependent_id")
        self._validate_consequence_target(dependent_kind, dependent_id, active=True)
        if dependent_kind == "world_assignment":
            cycle = assignment_cycle_path(
                self._consequence_assignment_edges(),
                proposed_premise=premise_id,
                proposed_dependent=dependent_id,
            )
            if cycle is not None:
                raise LacunaError(
                    "consequence-cycle",
                    "assignment consequence links must remain acyclic",
                    {"cycle": cycle},
                )
        relation = require_enum(operation.get("relation"), "relation", CONSEQUENCE_RELATIONS)
        duplicate = self.conn.execute(
            """SELECT consequence_id FROM consequence_links
               WHERE premise_assignment_id = ? AND dependent_kind = ?
                 AND dependent_id = ? AND relation = ? AND ended_seq IS NULL""",
            (premise_id, dependent_kind, dependent_id, relation),
        ).fetchone()
        if duplicate is not None:
            raise LacunaError(
                "duplicate-active-consequence",
                "an equivalent active consequence link already exists",
                {"consequence_id": duplicate["consequence_id"]},
            )
        source_id = optional_id(operation.get("source_id"), "source_id")
        if source_id is not None:
            self._require_source(source_id, "source_id")
        return "consequence.linked", {
            "consequence_id": consequence_id,
            "premise_assignment_id": premise_id,
            "dependent_kind": dependent_kind,
            "dependent_id": dependent_id,
            "relation": relation,
            "severity": require_enum(
                operation.get("severity", "material"), "severity", CONSEQUENCE_SEVERITIES
            ),
            "source_id": source_id,
            "rationale": require_string(operation.get("rationale"), "rationale", max_len=16384),
        }

    def _prepare_replace_consequence(
        self,
        operation: dict[str, Any],
        *,
        review_head: str | None = None,
    ) -> tuple[str, dict[str, Any]]:
        repair_id = require_id(operation.get("repair_id") or new_id("cpr"), "repair_id")
        if self._exists("consequence_repairs", "repair_id", repair_id):
            raise LacunaError(
                "duplicate-consequence-repair",
                f"consequence repair {repair_id!r} already exists",
            )
        successor_id = require_id(
            operation.get("consequence_id") or new_id("csq"), "consequence_id"
        )
        if self._exists("consequence_links", "consequence_id", successor_id):
            raise LacunaError(
                "duplicate-consequence",
                f"consequence {successor_id!r} already exists",
            )
        predecessor_id = require_id(
            operation.get("replaces_consequence_id"), "replaces_consequence_id"
        )
        predecessor = self._require_consequence(predecessor_id)

        expected_review = require_string(
            operation.get("expected_repair_sha256"),
            "expected_repair_sha256",
            max_len=64,
        )
        if not SHA256_RE.fullmatch(expected_review):
            raise LacunaError(
                "bad-repair-digest",
                "expected_repair_sha256 must be a lowercase SHA-256 digest",
            )
        review = self.consequence_repair_review(
            predecessor_id, _digest_head=review_head
        )
        current_review = str(review["repair_review_sha256"])
        if expected_review != current_review:
            raise LacunaError(
                "stale-consequence-repair-review",
                "consequence repair review does not match current custody",
                {
                    "expected": current_review,
                    "provided": expected_review,
                    "review_head": review["head"],
                    "current_head": self.head(),
                },
            )
        if review["blockers"]:
            raise LacunaError(
                "consequence-repair-blocked",
                "recorded custody blocks this consequence replacement",
                {
                    "consequence_id": predecessor_id,
                    "blockers": review["blockers"],
                },
            )
        if predecessor["ended_seq"] is not None:
            raise LacunaError(
                "unknown-consequence",
                f"unknown active consequence {predecessor_id!r}",
            )
        existing_repair = self.conn.execute(
            """SELECT repair_id, successor_consequence_id FROM consequence_repairs
               WHERE predecessor_consequence_id = ?""",
            (predecessor_id,),
        ).fetchone()
        if existing_repair is not None:
            raise LacunaError(
                "consequence-already-replaced",
                "a consequence may have only one recorded replacement successor",
                dict(existing_repair),
            )

        premise_id = require_id(
            operation.get("premise_assignment_id"), "premise_assignment_id"
        )
        self._require_world_assignment(premise_id, active=True)
        dependent_kind = require_enum(
            operation.get("dependent_kind"),
            "dependent_kind",
            CONSEQUENCE_DEPENDENT_KINDS,
        )
        dependent_id = require_id(operation.get("dependent_id"), "dependent_id")
        self._validate_consequence_target(dependent_kind, dependent_id, active=True)
        relation = require_enum(operation.get("relation"), "relation", CONSEQUENCE_RELATIONS)
        severity = require_enum(
            operation.get("severity"), "severity", CONSEQUENCE_SEVERITIES
        )
        source_id = optional_id(operation.get("source_id"), "source_id")
        if source_id is not None:
            self._require_source(source_id, "source_id")
        rationale = require_string(operation.get("rationale"), "rationale", max_len=16384)
        reason = require_string(operation.get("reason"), "reason", max_len=4096)

        candidate = {
            "premise_assignment_id": premise_id,
            "dependent_kind": dependent_kind,
            "dependent_id": dependent_id,
            "relation": relation,
            "severity": severity,
            "source_id": source_id,
            "rationale": rationale,
        }
        previous_semantics = {
            key: predecessor[key]
            for key in (
                "premise_assignment_id",
                "dependent_kind",
                "dependent_id",
                "relation",
                "severity",
                "source_id",
                "rationale",
            )
        }
        if candidate == previous_semantics:
            raise LacunaError(
                "consequence-replacement-unchanged",
                "replacement must change an endpoint or recorded semantic field",
            )

        duplicate = self.conn.execute(
            """SELECT consequence_id FROM consequence_links
               WHERE premise_assignment_id = ? AND dependent_kind = ?
                 AND dependent_id = ? AND relation = ? AND ended_seq IS NULL
                 AND consequence_id <> ?""",
            (premise_id, dependent_kind, dependent_id, relation, predecessor_id),
        ).fetchone()
        if duplicate is not None:
            raise LacunaError(
                "duplicate-active-consequence",
                "an equivalent active consequence link already exists",
                {"consequence_id": duplicate["consequence_id"]},
            )
        if dependent_kind == "world_assignment":
            cycle = assignment_cycle_path(
                self._consequence_assignment_edges(
                    exclude_consequence_id=predecessor_id
                ),
                proposed_premise=premise_id,
                proposed_dependent=dependent_id,
            )
            if cycle is not None:
                raise LacunaError(
                    "consequence-cycle",
                    "replacement would make assignment consequence links cyclic",
                    {"cycle": cycle},
                )

        return "consequence.replaced", {
            "repair_id": repair_id,
            "predecessor_consequence_id": predecessor_id,
            "successor_consequence_id": successor_id,
            **candidate,
            "reason": reason,
            "repair_review_sha256": expected_review,
            "repair_review_head": str(review["head"]),
        }

    def _prepare_retire_consequence(self, operation: dict[str, Any]) -> tuple[str, dict[str, Any]]:
        consequence_id = require_id(operation.get("consequence_id"), "consequence_id")
        self._require_consequence(consequence_id, active=True)
        return "consequence.retired", {
            "consequence_id": consequence_id,
            "reason": require_string(operation.get("reason"), "reason", max_len=4096),
        }

    def _prepare_set_world_weight(self, operation: dict[str, Any]) -> tuple[str, dict[str, Any]]:
        world_id = require_id(operation.get("world_id"), "world_id")
        self._require_world(world_id)
        return "world.weight_set", {
            "world_id": world_id,
            "weight": require_weight(operation.get("weight")),
            "reason": require_string(operation.get("reason"), "reason", max_len=4096),
        }

    def _prepare_set_world_status(self, operation: dict[str, Any]) -> tuple[str, dict[str, Any]]:
        world_id = require_id(operation.get("world_id"), "world_id")
        current = self._require_world(world_id)
        status = require_enum(operation.get("status"), "status", WORLD_STATUSES)
        if current["status"] == status:
            raise LacunaError("world-status-unchanged", f"world {world_id!r} is already {status}")
        if status in {"live", "selected"} and current["status"] in {"pruned", "archived"}:
            self._validate_world_consistency(world_id)
        return "world.status_set", {
            "world_id": world_id,
            "status": status,
            "reason": require_string(operation.get("reason"), "reason", max_len=4096),
        }

    def _particle_world_rows(self) -> list[dict[str, Any]]:
        rows = self.conn.execute(
            """SELECT * FROM worlds
               WHERE status IN ('live', 'selected')
               ORDER BY world_id"""
        ).fetchall()
        result: list[dict[str, Any]] = []
        for row in rows:
            item = dict(row)
            item["assignments"] = self.world_assignments(str(item["world_id"]))
            result.append(item)
        return result

    def _particle_factor_epoch(self) -> dict[str, Any]:
        """Return the latest structurally coherent particle-factor epoch.

        Candidate-world population, custody, or authored-prior mutations start a
        new epoch. Particle updates and reconciliations do not: they are the
        factor ledger and its derived replay. This intentionally conservative
        boundary prevents a likelihood assessed against one hidden-world shape
        from being replayed across a later semantic mutation.
        """
        placeholders = ",".join("?" for _ in PARTICLE_EPOCH_BOUNDARY_EVENTS)
        boundary_row = self.conn.execute(
            f"""SELECT seq, event_id, event_type
                  FROM events
                 WHERE event_type IN ({placeholders})
                 ORDER BY seq DESC
                 LIMIT 1""",
            tuple(sorted(PARTICLE_EPOCH_BOUNDARY_EVENTS)),
        ).fetchone()
        boundary = (
            None
            if boundary_row is None
            else {
                "seq": int(boundary_row["seq"]),
                "event_id": str(boundary_row["event_id"]),
                "event_type": str(boundary_row["event_type"]),
            }
        )
        after_seq = 0 if boundary is None else int(boundary["seq"])
        rows = self.conn.execute(
            """SELECT pu.update_id, pu.evidence_assertion_id, pu.created_seq,
                      pu.prior_bank_sha256, pu.posterior_bank_sha256,
                      a.ended_seq AS evidence_ended_seq
                 FROM particle_updates pu
                 JOIN assertions a ON a.assertion_id = pu.evidence_assertion_id
                WHERE pu.created_seq > ?
                ORDER BY pu.created_seq, pu.update_id""",
            (after_seq,),
        ).fetchall()
        factors: list[dict[str, Any]] = []
        for row in rows:
            factor = dict(row)
            factor["evidence_status"] = (
                "active" if factor["evidence_ended_seq"] is None else "superseded"
            )
            factor["assessments"] = [
                dict(member)
                for member in self.conn.execute(
                    """SELECT * FROM particle_update_members
                         WHERE update_id = ? ORDER BY ordinal""",
                    (factor["update_id"],),
                ).fetchall()
            ]
            factors.append(factor)
        return {
            "boundary": boundary,
            "factor_updates": factors,
        }

    def _particle_baseline_bank(
        self,
        baseline_factor: dict[str, Any],
    ) -> dict[str, Any]:
        labels = {
            str(row["world_id"]): str(row["label"])
            for row in self.conn.execute("SELECT world_id, label FROM worlds").fetchall()
        }
        records = [
            {
                "world_id": str(member["world_id"]),
                "label": labels.get(str(member["world_id"]), str(member["world_id"])),
                "status": str(member["world_status"]),
                "raw_weight": float(member["prior_weight"]),
                "valuation_sha256": str(member["valuation_sha256"]),
                "custody_sha256": str(member["custody_sha256"]),
                "assignment_count": None,
            }
            for member in baseline_factor["assessments"]
        ]
        return build_particle_bank_from_records(records)

    def _build_particle_reconciliation_review(
        self,
        *,
        head: str,
    ) -> dict[str, Any]:
        current_bank = build_particle_bank(self._particle_world_rows())
        epoch = self._particle_factor_epoch()
        factors = list(epoch["factor_updates"])
        blockers: list[dict[str, Any]] = []
        baseline_factor: dict[str, Any] | None = factors[0] if factors else None
        baseline_bank: dict[str, Any] | None = None
        included_factors: list[dict[str, Any]] = []
        excluded_factors: list[dict[str, Any]] = []
        calculation: dict[str, Any] | None = None
        posterior_bank: dict[str, Any] | None = None

        if baseline_factor is None:
            blockers.append(
                {
                    "code": "no-replayable-particle-factor-epoch",
                    "message": (
                        "no particle update exists after the latest candidate-world "
                        "population, custody, status, or manual-weight boundary"
                    ),
                }
            )
        else:
            baseline_bank = self._particle_baseline_bank(baseline_factor)
            if baseline_bank["bank_sha256"] != baseline_factor["prior_bank_sha256"]:
                blockers.append(
                    {
                        "code": "particle-reconciliation-baseline-digest-mismatch",
                        "baseline_update_id": baseline_factor["update_id"],
                        "expected": baseline_factor["prior_bank_sha256"],
                        "reconstructed": baseline_bank["bank_sha256"],
                    }
                )
            for factor in factors:
                if factor["evidence_status"] == "active":
                    included_factors.append(factor)
                else:
                    excluded = dict(factor)
                    excluded["exclusion_reason"] = "evidence-superseded"
                    excluded_factors.append(excluded)
            blockers.extend(
                factor_reconciliation_blockers(
                    baseline_bank=baseline_bank,
                    current_bank=current_bank,
                    included_factors=included_factors,
                )
            )
            if not blockers:
                try:
                    calculation = compute_factor_reconciliation(
                        baseline_bank=baseline_bank,
                        current_bank=current_bank,
                        included_factors=included_factors,
                    )
                except ValueError as exc:
                    blockers.append(
                        {
                            "code": "particle-reconciliation-calculation-failed",
                            "message": str(exc),
                        }
                    )
            if calculation is not None:
                posterior_bank = build_particle_bank_from_records(
                    {
                        "world_id": member["world_id"],
                        "label": next(
                            item["label"]
                            for item in current_bank["particles"]
                            if item["world_id"] == member["world_id"]
                        ),
                        "status": member["world_status"],
                        "raw_weight": member["posterior_probability"],
                        "valuation_sha256": member["valuation_sha256"],
                        "custody_sha256": member["custody_sha256"],
                        "assignment_count": None,
                    }
                    for member in calculation["members"]
                )

        factor_set_sha256 = (
            None
            if baseline_factor is None
            else particle_factor_set_sha256(
                baseline_update_id=str(baseline_factor["update_id"]),
                boundary=epoch["boundary"],
                included_factors=included_factors,
                excluded_factors=excluded_factors,
            )
        )
        if factor_set_sha256 is not None and posterior_bank is not None:
            prior_reconciliation = self.conn.execute(
                """SELECT reconciliation_id, posterior_bank_sha256, created_seq
                     FROM particle_reconciliations
                    WHERE factor_set_sha256 = ?
                    ORDER BY created_seq DESC, reconciliation_id DESC
                    LIMIT 1""",
                (factor_set_sha256,),
            ).fetchone()
            if (
                prior_reconciliation is not None
                and str(prior_reconciliation["posterior_bank_sha256"])
                == current_bank["bank_sha256"]
                == posterior_bank["bank_sha256"]
            ):
                blockers.append(
                    {
                        "code": "particle-factor-ledger-already-reconciled",
                        "reconciliation_id": str(
                            prior_reconciliation["reconciliation_id"]
                        ),
                        "created_seq": int(prior_reconciliation["created_seq"]),
                        "factor_set_sha256": factor_set_sha256,
                    }
                )

        factor_summary = lambda item: {
            "update_id": str(item["update_id"]),
            "evidence_assertion_id": str(item["evidence_assertion_id"]),
            "created_seq": int(item["created_seq"]),
            "evidence_status": str(item["evidence_status"]),
            "evidence_ended_seq": (
                None
                if item["evidence_ended_seq"] is None
                else int(item["evidence_ended_seq"])
            ),
            **(
                {"exclusion_reason": str(item["exclusion_reason"])}
                if item.get("exclusion_reason") is not None
                else {}
            ),
        }
        result_summary: dict[str, Any] | None = None
        if calculation is not None and posterior_bank is not None:
            result_summary = {
                "posterior_bank_sha256": posterior_bank["bank_sha256"],
                "log_normalization_constant": calculation["log_normalization_constant"],
                "base_effective_sample_size": calculation["base_effective_sample_size"],
                "current_effective_sample_size": calculation[
                    "current_effective_sample_size"
                ],
                "posterior_effective_sample_size": calculation[
                    "posterior_effective_sample_size"
                ],
                "base_entropy_nats": calculation["base_entropy_nats"],
                "current_entropy_nats": calculation["current_entropy_nats"],
                "posterior_entropy_nats": calculation["posterior_entropy_nats"],
                "information_gain_from_base_nats": calculation[
                    "information_gain_from_base_nats"
                ],
                "current_to_posterior_total_variation": calculation[
                    "current_to_posterior_total_variation"
                ],
                "extinguished_world_count": calculation["extinguished_world_count"],
                "members": calculation["members"],
            }
        review_core = {
            "schema": "lacuna.particle-reconciliation-review-core.v1",
            "boundary": epoch["boundary"],
            "baseline_update_id": (
                None if baseline_factor is None else str(baseline_factor["update_id"])
            ),
            "baseline_bank_sha256": (
                None if baseline_bank is None else baseline_bank["bank_sha256"]
            ),
            "current_bank_sha256": current_bank["bank_sha256"],
            "factor_set_sha256": factor_set_sha256,
            "included_factors": [factor_summary(item) for item in included_factors],
            "excluded_factors": [factor_summary(item) for item in excluded_factors],
            "blockers": blockers,
            "result": result_summary,
        }
        digest = particle_reconciliation_review_sha256(
            cube_id=self.meta("cube_id"),
            head=head,
            review_core=review_core,
        )
        return {
            "event": "lacuna.particle-reconciliation-review",
            "schema": "lacuna.particle-reconciliation-review.v1",
            "policy": PARTICLE_RECONCILIATION_POLICY,
            "cube_id": self.meta("cube_id"),
            "head": head,
            "reconciliation_review_sha256": digest,
            "expected_reconciliation_sha256": digest,
            "review_core": review_core,
            "ready": not blockers,
            "rule": (
                "Replay every still-active factor in the latest structurally coherent epoch "
                "from its immutable prior; retain superseded factors as excluded history."
            ),
            "nonclaim": (
                "Reconciliation repairs factor arithmetic and custody only. It does not certify "
                "likelihood calibration, evidence independence, causal agency, or world truth."
            ),
        }

    def _require_unused_particle_evidence(
        self, evidence_assertion_id: str
    ) -> dict[str, Any]:
        """Return active evidence custody only when it has not been factored before."""
        self._require_assertion(evidence_assertion_id, active=True)
        assertion_row = self.conn.execute(
            "SELECT * FROM assertions WHERE assertion_id = ? AND ended_seq IS NULL",
            (evidence_assertion_id,),
        ).fetchone()
        assert assertion_row is not None
        assertion = dict(assertion_row)
        prior_factor = self.conn.execute(
            "SELECT update_id FROM particle_updates WHERE evidence_assertion_id = ?",
            (evidence_assertion_id,),
        ).fetchone()
        if prior_factor is not None:
            raise LacunaError(
                "particle-evidence-already-applied",
                "an evidence assertion may contribute to the particle bank only once",
                {
                    "evidence_assertion_id": evidence_assertion_id,
                    "prior_update_id": prior_factor["update_id"],
                    "repair": "record a superseding assertion or rebuild weights from an explicit factor ledger",
                },
            )
        return assertion

    def _prepare_update_particle_bank(
        self,
        operation: dict[str, Any],
    ) -> tuple[str, dict[str, Any]]:
        update_id = require_id(operation.get("update_id") or new_id("pup"), "update_id")
        if self._exists("particle_updates", "update_id", update_id):
            raise LacunaError("duplicate-particle-update", f"particle update {update_id!r} already exists")

        evidence_assertion_id = require_id(
            operation.get("evidence_assertion_id"), "evidence_assertion_id"
        )
        self._require_unused_particle_evidence(evidence_assertion_id)
        expected_bank = require_string(
            operation.get("expected_bank_sha256"), "expected_bank_sha256", max_len=64
        )
        if not SHA256_RE.fullmatch(expected_bank):
            raise LacunaError(
                "bad-particle-bank-digest",
                "expected_bank_sha256 must be a lowercase SHA-256 digest",
            )

        population = self._particle_world_rows()
        bank = build_particle_bank(population)
        if not population:
            raise LacunaError(
                "empty-particle-bank",
                "at least one live or selected candidate world is required",
            )
        if expected_bank != bank["bank_sha256"]:
            raise LacunaError(
                "stale-particle-bank",
                "particle-bank receipt does not match the current live population",
                {
                    "expected": bank["bank_sha256"],
                    "provided": expected_bank,
                    "world_count": bank["world_count"],
                },
            )
        if bank["normalization_status"] != "normalized":
            raise LacunaError(
                "zero-prior-mass",
                "live candidate worlds must have positive total weight before evidence updating",
                {"raw_weight_sum": bank["raw_weight_sum"]},
            )

        raw_assessments = require_list(operation.get("assessments"), "assessments")
        if not raw_assessments:
            raise LacunaError("empty-particle-assessments", "assessments must not be empty")
        if len(raw_assessments) > 1000:
            raise LacunaError(
                "particle-assessment-limit",
                "a particle update may assess at most 1000 worlds",
                {"assessment_count": len(raw_assessments)},
            )
        assessments: dict[str, dict[str, Any]] = {}
        for index, raw in enumerate(raw_assessments):
            item = require_mapping(raw, f"assessments[{index}]")
            unexpected = sorted(set(item) - {"world_id", "likelihood", "rationale"})
            if unexpected:
                raise LacunaError(
                    "unexpected-particle-assessment-field",
                    "particle assessment contains unrecognized fields",
                    {"assessment_index": index, "fields": unexpected},
                )
            world_id = require_id(item.get("world_id"), f"assessments[{index}].world_id")
            if world_id in assessments:
                raise LacunaError(
                    "duplicate-particle-assessment",
                    f"world {world_id!r} is assessed more than once",
                    {"world_id": world_id},
                )
            likelihood = optional_probability(
                item.get("likelihood"), f"assessments[{index}].likelihood"
            )
            if likelihood is None:
                raise ValueError(f"assessments[{index}].likelihood is required")
            assessments[world_id] = {
                "likelihood": likelihood,
                "rationale": optional_string(
                    item.get("rationale"),
                    f"assessments[{index}].rationale",
                    max_len=4096,
                ),
            }

        population_ids = {str(item["world_id"]) for item in population}
        assessment_ids = set(assessments)
        missing = sorted(population_ids - assessment_ids)
        extra = sorted(assessment_ids - population_ids)
        if missing or extra:
            raise LacunaError(
                "incomplete-particle-assessments",
                "likelihoods must cover every live or selected world exactly once",
                {"missing_world_ids": missing, "extra_world_ids": extra},
            )

        try:
            update = compute_likelihood_update(bank, assessments)
        except ValueError as exc:
            code = "zero-posterior-mass" if "posterior" in str(exc) else "invalid-particle-update"
            raise LacunaError(code, str(exc)) from exc

        posterior_by_world = {
            str(item["world_id"]): float(item["posterior_probability"])
            for item in update["members"]
        }
        posterior_population: list[dict[str, Any]] = []
        for world in population:
            item = dict(world)
            item["weight"] = posterior_by_world[str(item["world_id"])]
            posterior_population.append(item)
        posterior_bank = build_particle_bank(posterior_population)

        return "particle.updated", {
            "update_id": update_id,
            "evidence_assertion_id": evidence_assertion_id,
            "method": PARTICLE_UPDATE_METHOD,
            "prior_bank_sha256": bank["bank_sha256"],
            "posterior_bank_sha256": posterior_bank["bank_sha256"],
            "prior_weight_sum": bank["raw_weight_sum"],
            "normalization_constant": update["normalization_constant"],
            "prior_effective_sample_size": update["prior_effective_sample_size"],
            "posterior_effective_sample_size": update["posterior_effective_sample_size"],
            "prior_entropy_nats": update["prior_entropy_nats"],
            "posterior_entropy_nats": update["posterior_entropy_nats"],
            "information_gain_nats": update["information_gain_nats"],
            "zero_likelihood_world_count": update["zero_likelihood_world_count"],
            "valuation_likelihood_divergence_groups": update[
                "valuation_likelihood_divergence_groups"
            ],
            "assessments": update["members"],
            "reason": require_string(operation.get("reason"), "reason", max_len=4096),
        }

    def _prepare_reconcile_particle_bank(
        self,
        operation: dict[str, Any],
        *,
        review_head: str | None = None,
    ) -> tuple[str, dict[str, Any]]:
        reconciliation_id = require_id(
            operation.get("reconciliation_id") or new_id("prc"),
            "reconciliation_id",
        )
        if self._exists(
            "particle_reconciliations",
            "reconciliation_id",
            reconciliation_id,
        ):
            raise LacunaError(
                "duplicate-particle-reconciliation",
                f"particle reconciliation {reconciliation_id!r} already exists",
            )
        expected = require_string(
            operation.get("expected_reconciliation_sha256"),
            "expected_reconciliation_sha256",
            max_len=64,
        )
        if not SHA256_RE.fullmatch(expected):
            raise LacunaError(
                "bad-particle-reconciliation-digest",
                "expected_reconciliation_sha256 must be a lowercase SHA-256 digest",
            )
        authorization_head = review_head or self.head()
        review = self._build_particle_reconciliation_review(head=authorization_head)
        actual = str(review["reconciliation_review_sha256"])
        if expected != actual:
            raise LacunaError(
                "stale-particle-reconciliation-review",
                "particle reconciliation review no longer matches the factor ledger and current bank",
                {
                    "expected": actual,
                    "provided": expected,
                    "review_head": authorization_head,
                },
            )
        core = review["review_core"]
        blockers = list(core["blockers"])
        if blockers:
            raise LacunaError(
                "particle-reconciliation-blocked",
                "particle factor ledger cannot be reconciled from the reviewed epoch",
                {"blockers": blockers},
            )
        result = core["result"]
        assert isinstance(result, dict)
        baseline_update_id = core["baseline_update_id"]
        baseline_bank_sha256 = core["baseline_bank_sha256"]
        factor_set_sha256 = core["factor_set_sha256"]
        assert isinstance(baseline_update_id, str)
        assert isinstance(baseline_bank_sha256, str)
        assert isinstance(factor_set_sha256, str)
        boundary = core["boundary"]
        return "particle.reconciled", {
            "reconciliation_id": reconciliation_id,
            "method": PARTICLE_RECONCILIATION_METHOD,
            "baseline_update_id": baseline_update_id,
            "boundary": boundary,
            "prior_bank_sha256": core["current_bank_sha256"],
            "baseline_bank_sha256": baseline_bank_sha256,
            "posterior_bank_sha256": result["posterior_bank_sha256"],
            "factor_set_sha256": factor_set_sha256,
            "reconciliation_review_sha256": actual,
            "reconciliation_review_head": authorization_head,
            "base_weight_sum": math.fsum(
                float(item["base_weight"]) for item in result["members"]
            ),
            "log_normalization_constant": result["log_normalization_constant"],
            "base_effective_sample_size": result["base_effective_sample_size"],
            "current_effective_sample_size": result[
                "current_effective_sample_size"
            ],
            "posterior_effective_sample_size": result[
                "posterior_effective_sample_size"
            ],
            "base_entropy_nats": result["base_entropy_nats"],
            "current_entropy_nats": result["current_entropy_nats"],
            "posterior_entropy_nats": result["posterior_entropy_nats"],
            "information_gain_from_base_nats": result[
                "information_gain_from_base_nats"
            ],
            "current_to_posterior_total_variation": result[
                "current_to_posterior_total_variation"
            ],
            "extinguished_world_count": result["extinguished_world_count"],
            "included_factors": core["included_factors"],
            "excluded_factors": core["excluded_factors"],
            "members": result["members"],
            "reason": require_string(operation.get("reason"), "reason", max_len=4096),
        }

    def _prepare_link_evidence(self, operation: dict[str, Any]) -> tuple[str, dict[str, Any]]:
        link_id = require_id(operation.get("link_id") or new_id("evl"), "link_id")
        if self._exists("evidence_links", "link_id", link_id):
            raise LacunaError("duplicate-evidence-link", f"evidence link {link_id!r} already exists")
        evidence_assertion_id = require_id(operation.get("evidence_assertion_id"), "evidence_assertion_id")
        self._require_assertion(evidence_assertion_id)
        target_claim_id = require_id(operation.get("target_claim_id"), "target_claim_id")
        self._require_claim(target_claim_id)
        world_id = optional_id(operation.get("world_id"), "world_id")
        if world_id is not None:
            self._require_world(world_id)
        payload = {
            "link_id": link_id,
            "evidence_assertion_id": evidence_assertion_id,
            "target_claim_id": target_claim_id,
            "world_id": world_id,
            "relation": require_enum(operation.get("relation"), "relation", EVIDENCE_RELATIONS),
            "strength": optional_probability(operation.get("strength"), "strength"),
            "rationale": optional_string(operation.get("rationale"), "rationale", max_len=16384),
        }
        return "evidence.linked", payload

    def _prepare_seal_precommitment(
        self, operation: dict[str, Any]
    ) -> tuple[str, dict[str, Any]]:
        seal_id = require_id(operation.get("seal_id") or new_id("seal"), "seal_id")
        if self._exists("fair_play_seals", "seal_id", seal_id):
            raise LacunaError(
                "duplicate-precommitment-seal",
                f"precommitment seal {seal_id!r} already exists",
            )
        scheme = require_enum(
            operation.get("scheme", SEAL_SCHEME),
            "scheme",
            {SEAL_SCHEME},
        )
        commitment_sha256 = require_string(
            operation.get("commitment_sha256"),
            "commitment_sha256",
            max_len=64,
        )
        if not SHA256_RE.fullmatch(commitment_sha256):
            raise LacunaError(
                "bad-seal-commitment",
                "commitment_sha256 must be a lowercase SHA-256 digest",
            )
        duplicate = self.conn.execute(
            "SELECT seal_id FROM fair_play_seals WHERE commitment_sha256 = ?",
            (commitment_sha256,),
        ).fetchone()
        if duplicate is not None:
            raise LacunaError(
                "duplicate-seal-commitment",
                "the same commitment digest is already registered",
                {"existing_seal_id": duplicate["seal_id"]},
            )
        visibility = require_enum(
            operation.get("visibility", "public"),
            "visibility",
            SEAL_VISIBILITIES,
        )
        audience = normalize_audience(operation.get("audience"))
        for audience_id in audience:
            self._require_agent(audience_id, "audience")
        if visibility == "restricted" and not audience:
            raise LacunaError(
                "empty-restricted-audience",
                "restricted seals require at least one audience agent",
            )
        if visibility != "restricted" and audience:
            raise LacunaError(
                "unexpected-audience",
                "audience is permitted only when seal visibility is restricted",
            )
        source_id = optional_id(operation.get("source_id"), "source_id")
        if source_id is not None:
            self._require_source(source_id, "source_id")
        return "precommitment.sealed", {
            "seal_id": seal_id,
            "scheme": scheme,
            "commitment_sha256": commitment_sha256,
            "label": require_string(operation.get("label", seal_id), "label", max_len=512),
            "purpose": require_enum(operation.get("purpose", "other"), "purpose", SEAL_PURPOSES),
            "visibility": visibility,
            "audience": audience,
            "source_id": source_id,
        }

    def _assert_seal_phase_committed(self, seal: dict[str, Any]) -> None:
        origin = self.conn.execute(
            "SELECT change_id FROM events WHERE seq = ?",
            (seal["created_seq"],),
        ).fetchone()
        if origin is None:
            raise LacunaError(
                "seal-origin-missing",
                "precommitment seal has no immutable origin event",
                {"seal_id": seal["seal_id"]},
            )
        committed = self.conn.execute(
            "SELECT 1 FROM changesets WHERE change_id = ?",
            (origin["change_id"],),
        ).fetchone()
        if committed is None:
            raise LacunaError(
                "seal-phase-not-committed",
                "a seal must be committed in an earlier change-set before it can be revealed or voided",
                {"seal_id": seal["seal_id"]},
            )

    def _prepare_reveal_precommitment(
        self, operation: dict[str, Any]
    ) -> tuple[str, dict[str, Any]]:
        seal_id = require_id(operation.get("seal_id"), "seal_id")
        seal = self._require_seal(seal_id, unresolved=True)
        self._assert_seal_phase_committed(seal)
        nonce = validate_seal_nonce(operation.get("nonce"))
        if "payload" not in operation:
            raise LacunaError("missing-seal-payload", "reveal_precommitment requires payload")
        payload = validate_seal_payload(operation["payload"])
        if not opening_matches_commitment(
            cube_id=self.meta("cube_id"),
            seal_id=seal_id,
            commitment_sha256=str(seal["commitment_sha256"]),
            payload=payload,
            nonce=nonce,
            scheme=str(seal["scheme"]),
        ):
            raise LacunaError(
                "seal-opening-mismatch",
                "payload and nonce do not open the recorded precommitment seal",
                {
                    "seal_id": seal_id,
                    "commitment_sha256": seal["commitment_sha256"],
                },
            )
        return "precommitment.revealed", {
            "seal_id": seal_id,
            "scheme": seal["scheme"],
            "commitment_sha256": seal["commitment_sha256"],
            "nonce": nonce,
            "payload": payload,
            "reason": require_string(operation.get("reason"), "reason", max_len=4096),
        }

    def _prepare_void_precommitment(
        self, operation: dict[str, Any]
    ) -> tuple[str, dict[str, Any]]:
        seal_id = require_id(operation.get("seal_id"), "seal_id")
        seal = self._require_seal(seal_id, unresolved=True)
        self._assert_seal_phase_committed(seal)
        return "precommitment.voided", {
            "seal_id": seal_id,
            "commitment_sha256": seal["commitment_sha256"],
            "reason": require_string(operation.get("reason"), "reason", max_len=4096),
        }

    def _prepare_open_question(self, operation: dict[str, Any]) -> tuple[str, dict[str, Any]]:
        question_id = require_id(operation.get("question_id") or new_id("qst"), "question_id")
        if self._exists("questions", "question_id", question_id):
            raise LacunaError("duplicate-question", f"question {question_id!r} already exists")
        opened_by = require_id(operation.get("opened_by"), "opened_by")
        self._require_agent(opened_by, "opened_by")
        about_claim_id = optional_id(operation.get("about_claim_id"), "about_claim_id")
        if about_claim_id is not None:
            self._require_claim(about_claim_id)
        visibility = require_enum(operation.get("visibility", "private"), "visibility", VISIBILITIES)
        audience = normalize_audience(operation.get("audience"))
        for audience_id in audience:
            self._require_agent(audience_id, "audience")
        if visibility == "restricted" and not audience:
            raise LacunaError("empty-restricted-audience", "restricted questions require at least one audience agent")
        if visibility != "restricted" and audience:
            raise LacunaError("unexpected-audience", "audience is permitted only when visibility is restricted")
        payload = {
            "question_id": question_id,
            "text": require_string(operation.get("text"), "text", max_len=4096),
            "about_claim_id": about_claim_id,
            "opened_by": opened_by,
            "visibility": visibility,
            "audience": audience,
        }
        return "question.opened", payload

    def _prepare_close_question(self, operation: dict[str, Any]) -> tuple[str, dict[str, Any]]:
        question_id = require_id(operation.get("question_id"), "question_id")
        row = self.conn.execute(
            "SELECT status, about_claim_id FROM questions WHERE question_id = ?",
            (question_id,),
        ).fetchone()
        if row is None:
            raise LacunaError("unknown-question", f"unknown question {question_id!r}")
        if row["status"] != "open":
            raise LacunaError("question-not-open", f"question {question_id!r} is not open")
        resolution_assertion_id = optional_id(operation.get("resolution_assertion_id"), "resolution_assertion_id")
        if resolution_assertion_id is not None:
            self._require_assertion(resolution_assertion_id)
            resolution = self.conn.execute(
                "SELECT claim_id FROM assertions WHERE assertion_id = ?",
                (resolution_assertion_id,),
            ).fetchone()
            if row["about_claim_id"] is not None and resolution["claim_id"] != row["about_claim_id"]:
                raise LacunaError(
                    "question-resolution-mismatch",
                    "resolution assertion must concern the claim named by the question",
                )
        return "question.closed", {
            "question_id": question_id,
            "resolution_assertion_id": resolution_assertion_id,
            "reason": require_string(operation.get("reason"), "reason", max_len=4096),
        }

    def _apply_projection(self, event_type: str, payload: dict[str, Any], *, seq: int, event_id: str) -> None:
        if event_type == "cube.created":
            return
        if event_type == "agent.registered":
            self.conn.execute(
                "INSERT INTO agents(agent_id, kind, label, metadata_json, created_seq) VALUES (?, ?, ?, ?, ?)",
                (payload["agent_id"], payload["kind"], payload["label"], canonical_json(payload["metadata"]), seq),
            )
            return
        if event_type == "source.added":
            self.conn.execute(
                """INSERT INTO sources(
                       source_id, kind, label, locator, content_sha256, metadata_json, created_seq
                   ) VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    payload["source_id"],
                    payload["kind"],
                    payload["label"],
                    payload["locator"],
                    payload["content_sha256"],
                    canonical_json(payload["metadata"]),
                    seq,
                ),
            )
            return
        if event_type == "claim.declared":
            self.conn.execute(
                """INSERT INTO claims(claim_id, subject, predicate, object_json, scope, created_seq)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    payload["claim_id"],
                    payload["subject"],
                    payload["predicate"],
                    canonical_json(payload["object"]),
                    payload["scope"],
                    seq,
                ),
            )
            return
        if event_type == "claim_relation.declared":
            self.conn.execute(
                """INSERT INTO claim_relations(
                       relation_id, left_claim_id, right_claim_id, relation,
                       source_id, rationale, created_seq
                   ) VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    payload["relation_id"],
                    payload["left_claim_id"],
                    payload["right_claim_id"],
                    payload["relation"],
                    payload["source_id"],
                    payload["rationale"],
                    seq,
                ),
            )
            return
        if event_type == "claim_relation.retired":
            self.conn.execute(
                """UPDATE claim_relations
                   SET ended_seq = ?, retirement_reason = ?
                   WHERE relation_id = ? AND ended_seq IS NULL""",
                (seq, payload["reason"], payload["relation_id"]),
            )
            return
        if event_type == "cardinality.declared":
            self.conn.execute(
                """INSERT INTO cardinality_constraints(
                       constraint_id, label, min_true, max_true, member_count,
                       definition_sha256, source_id, rationale, created_seq
                   ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    payload["constraint_id"],
                    payload["label"],
                    payload["min_true"],
                    payload["max_true"],
                    len(payload["claim_ids"]),
                    payload["definition_sha256"],
                    payload["source_id"],
                    payload["rationale"],
                    seq,
                ),
            )
            for ordinal, claim_id in enumerate(payload["claim_ids"]):
                self.conn.execute(
                    """INSERT INTO cardinality_members(
                           constraint_id, claim_id, ordinal, created_seq
                       ) VALUES (?, ?, ?, ?)""",
                    (payload["constraint_id"], claim_id, ordinal, seq),
                )
            return
        if event_type == "cardinality.retired":
            self.conn.execute(
                """UPDATE cardinality_constraints
                   SET ended_seq = ?, retirement_reason = ?
                   WHERE constraint_id = ? AND ended_seq IS NULL""",
                (seq, payload["reason"], payload["constraint_id"]),
            )
            return
        if event_type == "assertion.recorded":
            if payload["supersedes_id"] is not None:
                self.conn.execute(
                    "UPDATE assertions SET ended_seq = ? WHERE assertion_id = ? AND ended_seq IS NULL",
                    (seq, payload["supersedes_id"]),
                )
                self.conn.execute(
                    "UPDATE evidence_links SET ended_seq = ? WHERE evidence_assertion_id = ? AND ended_seq IS NULL",
                    (seq, payload["supersedes_id"]),
                )
            self.conn.execute(
                """INSERT INTO assertions(
                       assertion_id, claim_id, assertor_id, perspective_id, source_id,
                       stance, basis, standing, confidence, visibility, audience_json,
                       timeline_id, valid_from, valid_to, note, supersedes_id, created_seq
                   ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    payload["assertion_id"],
                    payload["claim_id"],
                    payload["assertor_id"],
                    payload["perspective_id"],
                    payload["source_id"],
                    payload["stance"],
                    payload["basis"],
                    payload["standing"],
                    payload["confidence"],
                    payload["visibility"],
                    canonical_json(payload["audience"]),
                    payload["timeline_id"],
                    payload["valid_from"],
                    payload["valid_to"],
                    payload["note"],
                    payload["supersedes_id"],
                    seq,
                ),
            )
            return
        if event_type == "assertion.superseded":
            self.conn.execute(
                "UPDATE assertions SET ended_seq = ? WHERE assertion_id = ? AND ended_seq IS NULL",
                (seq, payload["assertion_id"]),
            )
            self.conn.execute(
                "UPDATE evidence_links SET ended_seq = ? WHERE evidence_assertion_id = ? AND ended_seq IS NULL",
                (seq, payload["assertion_id"]),
            )
            return
        if event_type == "world.created":
            self.conn.execute(
                """INSERT INTO worlds(
                       world_id, label, parent_world_id, status, weight, rationale, created_seq
                   ) VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    payload["world_id"],
                    payload["label"],
                    payload["parent_world_id"],
                    payload["status"],
                    payload["weight"],
                    payload["rationale"],
                    seq,
                ),
            )
            if payload["parent_world_id"] is not None:
                rows = self.conn.execute(
                    """SELECT * FROM world_assignments
                       WHERE world_id = ? AND ended_seq IS NULL
                       ORDER BY created_seq, assignment_id""",
                    (payload["parent_world_id"],),
                ).fetchall()
                for row in rows:
                    inherited_id = "asn_" + sha256_text(
                        canonical_json(
                            {
                                "child_world_id": payload["world_id"],
                                "source_assignment_id": row["assignment_id"],
                                "created_seq": seq,
                            }
                        )
                    )
                    self.conn.execute(
                        """INSERT INTO world_assignments(
                               assignment_id, world_id, claim_id, truth, commitment,
                               commitment_basis, commitment_source_id, confidence,
                               rationale, source_assertion_id, timeline_id, valid_from, valid_to,
                               inherited_from_assignment_id, revision_of_assignment_id,
                               revision_reason, revision_impact_sha256, created_seq
                           ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, NULL, NULL, NULL, ?)""",
                        (
                            inherited_id,
                            payload["world_id"],
                            row["claim_id"],
                            row["truth"],
                            row["commitment"],
                            row["commitment_basis"],
                            row["commitment_source_id"],
                            row["confidence"],
                            row["rationale"],
                            row["source_assertion_id"],
                            row["timeline_id"],
                            row["valid_from"],
                            row["valid_to"],
                            row["assignment_id"],
                            seq,
                        ),
                    )
            return
        if event_type == "world.assigned":
            # Replaying pre-v4 ledgers must preserve their historical last-write
            # projection. New writes cannot reach this replacement path because
            # _prepare_assign_world refuses occupied slots.
            interval_sql = _same_interval_sql()
            params = (
                payload["world_id"],
                payload["claim_id"],
                payload["timeline_id"],
                payload["valid_from"],
                payload["valid_from"],
                payload["valid_to"],
                payload["valid_to"],
            )
            self.conn.execute(
                f"""UPDATE world_assignments SET ended_seq = ?
                    WHERE world_id = ? AND claim_id = ? AND {interval_sql} AND ended_seq IS NULL""",
                (seq, *params),
            )
            self.conn.execute(
                """INSERT INTO world_assignments(
                       assignment_id, world_id, claim_id, truth, commitment,
                       commitment_basis, commitment_source_id, confidence,
                       rationale, source_assertion_id, timeline_id, valid_from, valid_to,
                       inherited_from_assignment_id, revision_of_assignment_id,
                       revision_reason, revision_impact_sha256, created_seq
                   ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, NULL, NULL, NULL, NULL, ?)""",
                (
                    payload["assignment_id"],
                    payload["world_id"],
                    payload["claim_id"],
                    payload["truth"],
                    payload["commitment"],
                    payload.get("commitment_basis", "legacy"),
                    payload.get("commitment_source_id"),
                    payload["confidence"],
                    payload["rationale"],
                    payload["source_assertion_id"],
                    payload["timeline_id"],
                    payload["valid_from"],
                    payload["valid_to"],
                    seq,
                ),
            )
            return
        if event_type == "world.revised":
            self.conn.execute(
                """UPDATE world_assignments SET ended_seq = ?
                   WHERE assignment_id = ? AND ended_seq IS NULL""",
                (seq, payload["revision_of_assignment_id"]),
            )
            self.conn.execute(
                """INSERT INTO world_assignments(
                       assignment_id, world_id, claim_id, truth, commitment,
                       commitment_basis, commitment_source_id, confidence,
                       rationale, source_assertion_id, timeline_id, valid_from, valid_to,
                       inherited_from_assignment_id, revision_of_assignment_id,
                       revision_reason, revision_impact_sha256, created_seq
                   ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, NULL, ?, ?, ?, ?)""",
                (
                    payload["assignment_id"],
                    payload["world_id"],
                    payload["claim_id"],
                    payload["truth"],
                    payload["commitment"],
                    payload["commitment_basis"],
                    payload.get("commitment_source_id"),
                    payload["confidence"],
                    payload["rationale"],
                    payload["source_assertion_id"],
                    payload["timeline_id"],
                    payload["valid_from"],
                    payload["valid_to"],
                    payload["revision_of_assignment_id"],
                    payload["revision_reason"],
                    payload["revision_impact_sha256"],
                    seq,
                ),
            )
            return
        if event_type == "world.commitment_raised":
            self.conn.execute(
                """INSERT INTO commitment_transitions(
                       transition_id, assignment_id, from_commitment, to_commitment,
                       basis, source_id, rationale, created_seq
                   ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    payload["transition_id"],
                    payload["assignment_id"],
                    payload["from_commitment"],
                    payload["to_commitment"],
                    payload["basis"],
                    payload["source_id"],
                    payload["rationale"],
                    seq,
                ),
            )
            self.conn.execute(
                """UPDATE world_assignments
                   SET commitment = ?, commitment_basis = ?, commitment_source_id = ?
                   WHERE assignment_id = ? AND ended_seq IS NULL""",
                (
                    payload["to_commitment"],
                    payload["basis"],
                    payload["source_id"],
                    payload["assignment_id"],
                ),
            )
            return
        if event_type == "world.weight_set":
            self.conn.execute("UPDATE worlds SET weight = ? WHERE world_id = ?", (payload["weight"], payload["world_id"]))
            return
        if event_type == "world.status_set":
            self.conn.execute("UPDATE worlds SET status = ? WHERE world_id = ?", (payload["status"], payload["world_id"]))
            return
        if event_type == "particle.updated":
            self.conn.execute(
                """INSERT INTO particle_updates(
                       update_id, evidence_assertion_id, method, prior_bank_sha256,
                       posterior_bank_sha256, prior_weight_sum, normalization_constant,
                       prior_effective_sample_size, posterior_effective_sample_size,
                       prior_entropy_nats, posterior_entropy_nats, information_gain_nats,
                       reason, created_seq
                   ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    payload["update_id"],
                    payload["evidence_assertion_id"],
                    payload["method"],
                    payload["prior_bank_sha256"],
                    payload["posterior_bank_sha256"],
                    payload["prior_weight_sum"],
                    payload["normalization_constant"],
                    payload["prior_effective_sample_size"],
                    payload["posterior_effective_sample_size"],
                    payload["prior_entropy_nats"],
                    payload["posterior_entropy_nats"],
                    payload["information_gain_nats"],
                    payload["reason"],
                    seq,
                ),
            )
            for ordinal, member in enumerate(payload["assessments"]):
                self.conn.execute(
                    """INSERT INTO particle_update_members(
                           update_id, world_id, ordinal, world_status, prior_weight, prior_probability,
                           likelihood, unnormalized_weight, posterior_probability, rationale,
                           valuation_sha256, custody_sha256
                       ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        payload["update_id"],
                        member["world_id"],
                        ordinal,
                        member["world_status"],
                        member["prior_weight"],
                        member["prior_probability"],
                        member["likelihood"],
                        member["unnormalized_weight"],
                        member["posterior_probability"],
                        member.get("rationale"),
                        member["valuation_sha256"],
                        member["custody_sha256"],
                    ),
                )
                self.conn.execute(
                    "UPDATE worlds SET weight = ? WHERE world_id = ?",
                    (member["posterior_probability"], member["world_id"]),
                )
            return
        if event_type == "particle.reconciled":
            boundary = payload.get("boundary")
            boundary_seq = None if boundary is None else int(boundary["seq"])
            self.conn.execute(
                """INSERT INTO particle_reconciliations(
                       reconciliation_id, method, baseline_update_id, boundary_seq,
                       prior_bank_sha256, baseline_bank_sha256, posterior_bank_sha256,
                       factor_set_sha256, review_sha256, base_weight_sum,
                       log_normalization_constant, base_effective_sample_size,
                       current_effective_sample_size, posterior_effective_sample_size,
                       base_entropy_nats, current_entropy_nats, posterior_entropy_nats,
                       information_gain_from_base_nats,
                       current_to_posterior_total_variation, reason, created_seq
                   ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    payload["reconciliation_id"],
                    payload["method"],
                    payload["baseline_update_id"],
                    boundary_seq,
                    payload["prior_bank_sha256"],
                    payload["baseline_bank_sha256"],
                    payload["posterior_bank_sha256"],
                    payload["factor_set_sha256"],
                    payload["reconciliation_review_sha256"],
                    payload["base_weight_sum"],
                    payload["log_normalization_constant"],
                    payload["base_effective_sample_size"],
                    payload["current_effective_sample_size"],
                    payload["posterior_effective_sample_size"],
                    payload["base_entropy_nats"],
                    payload["current_entropy_nats"],
                    payload["posterior_entropy_nats"],
                    payload["information_gain_from_base_nats"],
                    payload["current_to_posterior_total_variation"],
                    payload["reason"],
                    seq,
                ),
            )
            factor_ordinal = 0
            for disposition, factors in (
                ("included", payload["included_factors"]),
                ("excluded", payload["excluded_factors"]),
            ):
                for factor in factors:
                    self.conn.execute(
                        """INSERT INTO particle_reconciliation_factors(
                               reconciliation_id, update_id, ordinal, disposition,
                               evidence_assertion_id, evidence_ended_seq, exclusion_reason
                           ) VALUES (?, ?, ?, ?, ?, ?, ?)""",
                        (
                            payload["reconciliation_id"],
                            factor["update_id"],
                            factor_ordinal,
                            disposition,
                            factor["evidence_assertion_id"],
                            factor.get("evidence_ended_seq"),
                            factor.get("exclusion_reason"),
                        ),
                    )
                    factor_ordinal += 1
            for ordinal, member in enumerate(payload["members"]):
                self.conn.execute(
                    """INSERT INTO particle_reconciliation_members(
                           reconciliation_id, world_id, ordinal, world_status,
                           current_weight, current_probability, base_weight,
                           base_probability, log_factor_sum, extinguished_by_update_id,
                           posterior_probability, valuation_sha256, custody_sha256
                       ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        payload["reconciliation_id"],
                        member["world_id"],
                        ordinal,
                        member["world_status"],
                        member["current_weight"],
                        member["current_probability"],
                        member["base_weight"],
                        member["base_probability"],
                        member.get("log_factor_sum"),
                        member.get("extinguished_by_update_id"),
                        member["posterior_probability"],
                        member["valuation_sha256"],
                        member["custody_sha256"],
                    ),
                )
                self.conn.execute(
                    "UPDATE worlds SET weight = ? WHERE world_id = ?",
                    (member["posterior_probability"], member["world_id"]),
                )
            return
        if event_type == "evidence.linked":
            self.conn.execute(
                """INSERT INTO evidence_links(
                       link_id, evidence_assertion_id, target_claim_id, world_id,
                       relation, strength, rationale, created_seq
                   ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    payload["link_id"],
                    payload["evidence_assertion_id"],
                    payload["target_claim_id"],
                    payload["world_id"],
                    payload["relation"],
                    payload["strength"],
                    payload["rationale"],
                    seq,
                ),
            )
            return
        if event_type == "consequence.linked":
            self.conn.execute(
                """INSERT INTO consequence_links(
                       consequence_id, premise_assignment_id, dependent_kind,
                       dependent_id, relation, severity, source_id, rationale, created_seq
                   ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    payload["consequence_id"],
                    payload["premise_assignment_id"],
                    payload["dependent_kind"],
                    payload["dependent_id"],
                    payload["relation"],
                    payload["severity"],
                    payload["source_id"],
                    payload["rationale"],
                    seq,
                ),
            )
            return
        if event_type == "consequence.replaced":
            self.conn.execute(
                """UPDATE consequence_links
                   SET ended_seq = ?, retirement_reason = ?
                   WHERE consequence_id = ? AND ended_seq IS NULL""",
                (
                    seq,
                    payload["reason"],
                    payload["predecessor_consequence_id"],
                ),
            )
            self.conn.execute(
                """INSERT INTO consequence_links(
                       consequence_id, premise_assignment_id, dependent_kind,
                       dependent_id, relation, severity, source_id, rationale, created_seq
                   ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    payload["successor_consequence_id"],
                    payload["premise_assignment_id"],
                    payload["dependent_kind"],
                    payload["dependent_id"],
                    payload["relation"],
                    payload["severity"],
                    payload["source_id"],
                    payload["rationale"],
                    seq,
                ),
            )
            self.conn.execute(
                """INSERT INTO consequence_repairs(
                       repair_id, predecessor_consequence_id, successor_consequence_id,
                       reason, review_sha256, created_seq
                   ) VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    payload["repair_id"],
                    payload["predecessor_consequence_id"],
                    payload["successor_consequence_id"],
                    payload["reason"],
                    payload["repair_review_sha256"],
                    seq,
                ),
            )
            return
        if event_type == "consequence.retired":
            self.conn.execute(
                """UPDATE consequence_links
                   SET ended_seq = ?, retirement_reason = ?
                   WHERE consequence_id = ? AND ended_seq IS NULL""",
                (seq, payload["reason"], payload["consequence_id"]),
            )
            return
        if event_type == "precommitment.sealed":
            self.conn.execute(
                """INSERT INTO fair_play_seals(
                       seal_id, scheme, commitment_sha256, label, purpose, visibility,
                       audience_json, source_id, created_seq
                   ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    payload["seal_id"],
                    payload["scheme"],
                    payload["commitment_sha256"],
                    payload["label"],
                    payload["purpose"],
                    payload["visibility"],
                    canonical_json(payload["audience"]),
                    payload["source_id"],
                    seq,
                ),
            )
            return
        if event_type == "precommitment.revealed":
            cursor = self.conn.execute(
                """UPDATE fair_play_seals
                   SET revealed_seq = ?, reveal_payload_json = ?, reveal_nonce = ?, reveal_reason = ?
                   WHERE seal_id = ? AND revealed_seq IS NULL AND voided_seq IS NULL""",
                (
                    seq,
                    canonical_json(payload["payload"]),
                    payload["nonce"],
                    payload["reason"],
                    payload["seal_id"],
                ),
            )
            if cursor.rowcount != 1:
                raise LacunaError(
                    "invalid-seal-lifecycle",
                    f"cannot project reveal for unresolved seal {payload['seal_id']!r}",
                )
            return
        if event_type == "precommitment.voided":
            cursor = self.conn.execute(
                """UPDATE fair_play_seals
                   SET voided_seq = ?, void_reason = ?
                   WHERE seal_id = ? AND revealed_seq IS NULL AND voided_seq IS NULL""",
                (seq, payload["reason"], payload["seal_id"]),
            )
            if cursor.rowcount != 1:
                raise LacunaError(
                    "invalid-seal-lifecycle",
                    f"cannot project void for unresolved seal {payload['seal_id']!r}",
                )
            return
        if event_type == "question.opened":
            self.conn.execute(
                """INSERT INTO questions(
                       question_id, text, about_claim_id, opened_by, visibility,
                       audience_json, status, created_seq
                   ) VALUES (?, ?, ?, ?, ?, ?, 'open', ?)""",
                (
                    payload["question_id"],
                    payload["text"],
                    payload["about_claim_id"],
                    payload["opened_by"],
                    payload["visibility"],
                    canonical_json(payload["audience"]),
                    seq,
                ),
            )
            return
        if event_type == "question.closed":
            self.conn.execute(
                """UPDATE questions
                   SET status = 'closed', resolution_assertion_id = ?, closed_seq = ?
                   WHERE question_id = ? AND status = 'open'""",
                (payload["resolution_assertion_id"], seq, payload["question_id"]),
            )
            return
        raise LacunaError("unknown-event-type", f"cannot project event type {event_type!r}")

    def verify(self, *, include_projections: bool = True) -> dict[str, Any]:
        errors: list[dict[str, Any]] = []

        def finite_number(value: Any) -> float | None:
            """Parse projected numeric custody without allowing audit to crash."""
            if isinstance(value, bool):
                return None
            try:
                number = float(value)
            except (TypeError, ValueError):
                return None
            return number if math.isfinite(number) else None

        for shape_error in _database_shape_errors(self.conn):
            errors.append({"code": "database-schema-shape", **shape_error})
        database_schema_version = int(self.conn.execute("PRAGMA user_version").fetchone()[0])
        if database_schema_version != DATABASE_SCHEMA_VERSION:
            errors.append(
                {
                    "code": "database-schema-version",
                    "expected": DATABASE_SCHEMA_VERSION,
                    "actual": database_schema_version,
                }
            )
        try:
            metadata_schema_version = int(self.meta("schema_version"))
        except (LacunaError, ValueError):
            metadata_schema_version = -1
        if metadata_schema_version != database_schema_version:
            errors.append(
                {
                    "code": "database-schema-metadata",
                    "pragma": database_schema_version,
                    "metadata": metadata_schema_version,
                }
            )
        migration_rows = {
            int(row["target_version"]): row
            for row in self.conn.execute("SELECT * FROM schema_migrations").fetchall()
        }
        current_migration = migration_rows.get(DATABASE_SCHEMA_VERSION)
        if current_migration is None:
            errors.append({"code": "missing-schema-migration-custody", "target_version": DATABASE_SCHEMA_VERSION})
        expected_migration_digests = {
            (1, 2): MIGRATION_1_TO_2_SHA256,
            (2, 3): MIGRATION_2_TO_3_SHA256,
            (3, 4): MIGRATION_3_TO_4_SHA256,
            (4, 5): MIGRATION_4_TO_5_SHA256,
            (5, 6): MIGRATION_5_TO_6_SHA256,
            (6, 7): MIGRATION_6_TO_7_SHA256,
            (7, 8): MIGRATION_7_TO_8_SHA256,
        }
        for (source_version, target_version), expected_digest in expected_migration_digests.items():
            row = migration_rows.get(target_version)
            if row is None or int(row["source_version"]) != source_version:
                continue
            if row["migration_sha256"] != expected_digest:
                errors.append({"code": "schema-migration-digest", "target_version": target_version})
        integrity = self.conn.execute("PRAGMA integrity_check").fetchone()[0]
        if integrity != "ok":
            errors.append({"code": "sqlite-integrity", "message": integrity})
        all_foreign_rows = self.conn.execute("PRAGMA foreign_key_check").fetchall()
        foreign_rows = all_foreign_rows if include_projections else []
        for row in foreign_rows:
            errors.append({"code": "foreign-key", "row": list(row)})

        expected_seq = 1
        previous_hash = GENESIS_HASH
        last_hash = GENESIS_HASH
        rows = self.conn.execute("SELECT * FROM events ORDER BY seq").fetchall()
        event_rows_by_seq = {int(row["seq"]): row for row in rows}
        event_payloads_by_seq: dict[int, dict[str, Any]] = {}
        for row in rows:
            if row["schema_version"] not in SUPPORTED_EVENT_SCHEMA_VERSIONS:
                errors.append(
                    {
                        "code": "event-schema-version",
                        "seq": row["seq"],
                        "supported": sorted(SUPPORTED_EVENT_SCHEMA_VERSIONS),
                        "actual": row["schema_version"],
                    }
                )
            if row["event_type"] not in EVENT_TYPES:
                errors.append(
                    {"code": "unknown-event-type", "seq": row["seq"], "event_type": row["event_type"]}
                )
            if row["seq"] != expected_seq:
                errors.append(
                    {"code": "sequence-gap", "expected": expected_seq, "actual": row["seq"]}
                )
                expected_seq = row["seq"]
            if row["prev_hash"] != previous_hash:
                errors.append(
                    {
                        "code": "previous-hash-mismatch",
                        "seq": row["seq"],
                        "expected": previous_hash,
                        "actual": row["prev_hash"],
                    }
                )
            try:
                payload = json.loads(row["payload_json"])
            except json.JSONDecodeError as exc:
                errors.append({"code": "bad-event-json", "seq": row["seq"], "message": str(exc)})
                payload = None
            if payload is not None:
                if isinstance(payload, dict):
                    event_payloads_by_seq[int(row["seq"])] = payload
                core = _event_hash_core(
                    seq=row["seq"],
                    event_id=row["event_id"],
                    change_id=row["change_id"],
                    event_type=row["event_type"],
                    actor_id=row["actor_id"],
                    recorded_at=row["recorded_at"],
                    payload=payload,
                    prev_hash=row["prev_hash"],
                    schema_version=row["schema_version"],
                )
                actual_hash = sha256_text(canonical_json(core))
                if actual_hash != row["event_hash"]:
                    errors.append(
                        {
                            "code": "event-hash-mismatch",
                            "seq": row["seq"],
                            "expected": actual_hash,
                            "actual": row["event_hash"],
                        }
                    )
            previous_hash = row["event_hash"]
            last_hash = row["event_hash"]
            expected_seq += 1
        events_by_change: dict[str, list[sqlite3.Row]] = {}
        for row in rows:
            events_by_change.setdefault(row["change_id"], []).append(row)
        change_rows = {
            row["change_id"]: row
            for row in self.conn.execute("SELECT * FROM changesets").fetchall()
        }
        for change_id, change_events in events_by_change.items():
            receipt = change_rows.get(change_id)
            if receipt is None:
                errors.append({"code": "missing-change-receipt", "change_id": change_id})
                continue
            seqs = [int(row["seq"]) for row in change_events]
            if seqs[-1] - seqs[0] + 1 != len(seqs):
                errors.append({"code": "noncontiguous-change-events", "change_id": change_id, "seqs": seqs})
            if int(receipt["operation_count"]) != len(change_events):
                errors.append(
                    {
                        "code": "change-operation-count",
                        "change_id": change_id,
                        "receipt": receipt["operation_count"],
                        "events": len(change_events),
                    }
                )
            if receipt["before_head"] != change_events[0]["prev_hash"]:
                errors.append({"code": "change-before-head", "change_id": change_id})
            if receipt["expected_head"] != receipt["before_head"]:
                errors.append({"code": "change-expected-head", "change_id": change_id})
            if receipt["after_head"] != change_events[-1]["event_hash"]:
                errors.append({"code": "change-after-head", "change_id": change_id})
            if any(row["actor_id"] != receipt["actor_id"] for row in change_events):
                errors.append({"code": "change-actor-mismatch", "change_id": change_id})
            if any(row["recorded_at"] != receipt["applied_at"] for row in change_events):
                errors.append({"code": "change-time-mismatch", "change_id": change_id})
            if not SHA256_RE.fullmatch(str(receipt["payload_sha256"])):
                errors.append({"code": "change-payload-digest", "change_id": change_id})
        for change_id in sorted(set(change_rows) - set(events_by_change)):
            errors.append({"code": "orphan-change-receipt", "change_id": change_id})

        if self.head() != last_hash:
            errors.append({"code": "head-mismatch", "meta_head": self.head(), "event_head": last_hash})
        if self.config.get("cube_id") != self.meta("cube_id"):
            errors.append({"code": "cube-id-mismatch"})

        conflicts: list[dict[str, Any]] = []
        if include_projections:
            agent_ids = {row["agent_id"] for row in self.conn.execute("SELECT agent_id FROM agents").fetchall()}
            for row in rows:
                if row["actor_id"] not in agent_ids:
                    errors.append(
                        {"code": "unknown-event-actor", "seq": row["seq"], "actor_id": row["actor_id"]}
                    )
            for change_id, receipt in change_rows.items():
                if receipt["actor_id"] not in agent_ids:
                    errors.append(
                        {"code": "unknown-change-actor", "change_id": change_id, "actor_id": receipt["actor_id"]}
                    )
            conflicts = self.conflicts()
            for conflict in conflicts:
                if conflict["severity"] == "invariant":
                    errors.append({"code": "projection-invariant", "conflict": conflict})

            assignment_rows = [
                dict(row)
                for row in self.conn.execute(
                    "SELECT * FROM world_assignments ORDER BY created_seq, assignment_id"
                ).fetchall()
            ]
            assignments_by_id = {
                str(row["assignment_id"]): row for row in assignment_rows
            }
            revision_children: dict[str, list[str]] = {}
            for row in assignment_rows:
                assignment_id = str(row["assignment_id"])
                commitment = str(row["commitment"])
                basis = str(row["commitment_basis"])
                if commitment not in COMMITMENTS:
                    errors.append(
                        {
                            "code": "assignment-commitment-enum",
                            "assignment_id": assignment_id,
                            "actual": commitment,
                        }
                    )
                if basis not in COMMITMENT_BASES:
                    errors.append(
                        {
                            "code": "assignment-commitment-basis-enum",
                            "assignment_id": assignment_id,
                            "actual": basis,
                        }
                    )
                if commitment == "hard" and basis not in HARD_COMMITMENT_BASES | {"legacy"}:
                    errors.append(
                        {
                            "code": "hard-commitment-basis",
                            "assignment_id": assignment_id,
                            "basis": basis,
                        }
                    )
                if basis in SOURCE_EXPECTED_BASES and row["commitment_source_id"] is None:
                    errors.append(
                        {
                            "code": "commitment-source-required",
                            "assignment_id": assignment_id,
                            "basis": basis,
                        }
                    )
                if row["ended_seq"] is not None and int(row["ended_seq"]) < int(row["created_seq"]):
                    errors.append(
                        {
                            "code": "assignment-negative-custody-interval",
                            "assignment_id": assignment_id,
                        }
                    )
                predecessor_id = row["revision_of_assignment_id"]
                if predecessor_id is None:
                    continue
                predecessor_id = str(predecessor_id)
                revision_children.setdefault(predecessor_id, []).append(assignment_id)
                predecessor = assignments_by_id.get(predecessor_id)
                if predecessor is None:
                    errors.append(
                        {
                            "code": "revision-missing-predecessor",
                            "assignment_id": assignment_id,
                            "predecessor_id": predecessor_id,
                        }
                    )
                    continue
                identity_fields = (
                    "world_id",
                    "claim_id",
                    "timeline_id",
                    "valid_from",
                    "valid_to",
                )
                mismatches = [
                    field
                    for field in identity_fields
                    if row[field] != predecessor[field]
                ]
                if mismatches:
                    errors.append(
                        {
                            "code": "revision-slot-mismatch",
                            "assignment_id": assignment_id,
                            "predecessor_id": predecessor_id,
                            "fields": mismatches,
                        }
                    )
                if predecessor["ended_seq"] != row["created_seq"]:
                    errors.append(
                        {
                            "code": "revision-custody-gap",
                            "assignment_id": assignment_id,
                            "predecessor_id": predecessor_id,
                            "predecessor_ended_seq": predecessor["ended_seq"],
                            "successor_created_seq": row["created_seq"],
                        }
                    )
                digest = row["revision_impact_sha256"]
                if digest is None or not SHA256_RE.fullmatch(str(digest)):
                    errors.append(
                        {
                            "code": "revision-impact-digest",
                            "assignment_id": assignment_id,
                        }
                    )
                if not row["revision_reason"]:
                    errors.append(
                        {
                            "code": "revision-reason-missing",
                            "assignment_id": assignment_id,
                        }
                    )
            for predecessor_id, children in sorted(revision_children.items()):
                if len(children) > 1:
                    errors.append(
                        {
                            "code": "revision-branch-within-world",
                            "predecessor_id": predecessor_id,
                            "successor_ids": sorted(children),
                        }
                    )

            transition_rows = [
                dict(row)
                for row in self.conn.execute(
                    "SELECT * FROM commitment_transitions ORDER BY assignment_id, created_seq, transition_id"
                ).fetchall()
            ]
            transitions_by_assignment: dict[str, list[dict[str, Any]]] = {}
            for row in transition_rows:
                transition_id = str(row["transition_id"])
                assignment_id = str(row["assignment_id"])
                transitions_by_assignment.setdefault(assignment_id, []).append(row)
                assignment = assignments_by_id.get(assignment_id)
                if assignment is None:
                    errors.append(
                        {
                            "code": "transition-missing-assignment",
                            "transition_id": transition_id,
                            "assignment_id": assignment_id,
                        }
                    )
                    continue
                previous = str(row["from_commitment"])
                target = str(row["to_commitment"])
                if previous not in COMMITMENTS or target not in COMMITMENTS:
                    errors.append(
                        {
                            "code": "transition-commitment-enum",
                            "transition_id": transition_id,
                            "from": previous,
                            "to": target,
                        }
                    )
                elif not is_adjacent_raise(previous, target):
                    errors.append(
                        {
                            "code": "transition-not-adjacent",
                            "transition_id": transition_id,
                            "from": previous,
                            "to": target,
                        }
                    )
                if str(row["basis"]) not in WRITABLE_COMMITMENT_BASES:
                    errors.append(
                        {
                            "code": "transition-basis-enum",
                            "transition_id": transition_id,
                            "basis": row["basis"],
                        }
                    )
                if int(row["created_seq"]) < int(assignment["created_seq"]):
                    errors.append(
                        {
                            "code": "transition-before-assignment",
                            "transition_id": transition_id,
                        }
                    )
                if assignment["ended_seq"] is not None and int(row["created_seq"]) >= int(
                    assignment["ended_seq"]
                ):
                    errors.append(
                        {
                            "code": "transition-after-assignment-ended",
                            "transition_id": transition_id,
                        }
                    )
            for assignment_id, transition_chain in sorted(transitions_by_assignment.items()):
                for previous_row, next_row in zip(transition_chain, transition_chain[1:]):
                    if previous_row["to_commitment"] != next_row["from_commitment"]:
                        errors.append(
                            {
                                "code": "transition-chain-gap",
                                "assignment_id": assignment_id,
                                "left_transition_id": previous_row["transition_id"],
                                "right_transition_id": next_row["transition_id"],
                            }
                        )
                assignment = assignments_by_id.get(assignment_id)
                if assignment is not None and transition_chain:
                    if transition_chain[-1]["to_commitment"] != assignment["commitment"]:
                        errors.append(
                            {
                                "code": "transition-current-commitment-mismatch",
                                "assignment_id": assignment_id,
                                "transition_commitment": transition_chain[-1]["to_commitment"],
                                "assignment_commitment": assignment["commitment"],
                            }
                        )

            particle_update_rows = [
                dict(row)
                for row in self.conn.execute(
                    "SELECT * FROM particle_updates ORDER BY created_seq, update_id"
                ).fetchall()
            ]
            projected_particle_update_ids: set[str] = set()
            particle_float_fields = (
                "prior_weight_sum",
                "normalization_constant",
                "prior_effective_sample_size",
                "posterior_effective_sample_size",
                "prior_entropy_nats",
                "posterior_entropy_nats",
                "information_gain_nats",
            )
            member_float_fields = (
                "prior_weight",
                "prior_probability",
                "likelihood",
                "unnormalized_weight",
                "posterior_probability",
            )
            member_fields = (
                "world_id",
                "world_status",
                *member_float_fields,
                "rationale",
                "valuation_sha256",
                "custody_sha256",
            )
            for update_row in particle_update_rows:
                update_id = str(update_row["update_id"])
                projected_particle_update_ids.add(update_id)
                seq = int(update_row["created_seq"])
                event_row = event_rows_by_seq.get(seq)
                payload = event_payloads_by_seq.get(seq)
                if event_row is None or event_row["event_type"] != "particle.updated":
                    errors.append(
                        {
                            "code": "particle-update-origin-event",
                            "update_id": update_id,
                            "created_seq": seq,
                        }
                    )
                    continue
                if payload is None or payload.get("update_id") != update_id:
                    errors.append(
                        {
                            "code": "particle-update-payload-identity",
                            "update_id": update_id,
                            "created_seq": seq,
                        }
                    )
                    continue
                if update_row["method"] != PARTICLE_UPDATE_METHOD:
                    errors.append(
                        {
                            "code": "particle-update-method",
                            "update_id": update_id,
                            "actual": update_row["method"],
                        }
                    )
                scalar_fields = (
                    "evidence_assertion_id",
                    "method",
                    "prior_bank_sha256",
                    "posterior_bank_sha256",
                    "reason",
                )
                for field in scalar_fields:
                    if payload.get(field) != update_row[field]:
                        errors.append(
                            {
                                "code": "particle-update-projection-mismatch",
                                "update_id": update_id,
                                "field": field,
                            }
                        )
                for digest_field in ("prior_bank_sha256", "posterior_bank_sha256"):
                    if not SHA256_RE.fullmatch(str(update_row[digest_field])):
                        errors.append(
                            {
                                "code": "particle-update-bank-digest-format",
                                "update_id": update_id,
                                "field": digest_field,
                            }
                        )

                update_numbers: dict[str, float] = {}
                update_numbers_valid = True
                for field in particle_float_fields:
                    event_value = finite_number(payload.get(field))
                    projection_value = finite_number(update_row[field])
                    if projection_value is None:
                        update_numbers_valid = False
                        errors.append(
                            {
                                "code": "particle-update-nonfinite-number",
                                "update_id": update_id,
                                "field": field,
                                "surface": "projection",
                            }
                        )
                    else:
                        update_numbers[field] = projection_value
                    if event_value is None:
                        errors.append(
                            {
                                "code": "particle-update-nonfinite-number",
                                "update_id": update_id,
                                "field": field,
                                "surface": "event",
                            }
                        )
                    if (
                        event_value is None
                        or projection_value is None
                        or not math.isclose(
                            event_value,
                            projection_value,
                            rel_tol=1e-12,
                            abs_tol=1e-15,
                        )
                    ):
                        errors.append(
                            {
                                "code": "particle-update-projection-mismatch",
                                "update_id": update_id,
                                "field": field,
                            }
                        )

                if not self._exists(
                    "assertions", "assertion_id", str(update_row["evidence_assertion_id"])
                ):
                    errors.append(
                        {
                            "code": "particle-update-missing-evidence",
                            "update_id": update_id,
                            "evidence_assertion_id": update_row["evidence_assertion_id"],
                        }
                    )

                members = [
                    dict(row)
                    for row in self.conn.execute(
                        """SELECT * FROM particle_update_members
                           WHERE update_id = ? ORDER BY ordinal""",
                        (update_id,),
                    ).fetchall()
                ]
                event_members = payload.get("assessments")
                if not isinstance(event_members, list) or len(event_members) != len(members):
                    errors.append(
                        {
                            "code": "particle-update-member-count",
                            "update_id": update_id,
                            "projection_count": len(members),
                            "event_count": len(event_members) if isinstance(event_members, list) else None,
                        }
                    )
                    event_members = []
                if not members:
                    errors.append({"code": "particle-update-empty", "update_id": update_id})
                    continue

                member_numbers: list[dict[str, float]] = []
                member_numbers_valid = True
                for ordinal, member in enumerate(members):
                    try:
                        stored_ordinal = int(member["ordinal"])
                    except (TypeError, ValueError, OverflowError):
                        stored_ordinal = -1
                    if stored_ordinal != ordinal:
                        errors.append(
                            {
                                "code": "particle-update-member-ordinal",
                                "update_id": update_id,
                                "world_id": member["world_id"],
                            }
                        )
                    parsed_numbers: dict[str, float] = {}
                    for field in member_float_fields:
                        number = finite_number(member[field])
                        if number is None:
                            member_numbers_valid = False
                            errors.append(
                                {
                                    "code": "particle-update-member-nonfinite-number",
                                    "update_id": update_id,
                                    "world_id": member["world_id"],
                                    "field": field,
                                    "surface": "projection",
                                }
                            )
                        else:
                            parsed_numbers[field] = number
                    member_numbers.append(parsed_numbers)

                    if ordinal < len(event_members) and isinstance(event_members[ordinal], dict):
                        event_member = event_members[ordinal]
                        for field in member_fields:
                            left = member[field]
                            right = event_member.get(field)
                            if field in member_float_fields:
                                left_number = parsed_numbers.get(field)
                                right_number = finite_number(right)
                                if right_number is None:
                                    errors.append(
                                        {
                                            "code": "particle-update-member-nonfinite-number",
                                            "update_id": update_id,
                                            "world_id": member["world_id"],
                                            "field": field,
                                            "surface": "event",
                                        }
                                    )
                                equal = (
                                    left_number is not None
                                    and right_number is not None
                                    and math.isclose(
                                        left_number,
                                        right_number,
                                        rel_tol=1e-12,
                                        abs_tol=1e-15,
                                    )
                                )
                            else:
                                equal = left == right
                            if not equal:
                                errors.append(
                                    {
                                        "code": "particle-update-member-projection-mismatch",
                                        "update_id": update_id,
                                        "world_id": member["world_id"],
                                        "field": field,
                                    }
                                )
                    if member["world_status"] not in {"live", "selected"}:
                        errors.append(
                            {
                                "code": "particle-update-member-status",
                                "update_id": update_id,
                                "world_id": member["world_id"],
                                "status": member["world_status"],
                            }
                        )
                    for digest_field in ("valuation_sha256", "custody_sha256"):
                        if not SHA256_RE.fullmatch(str(member[digest_field])):
                            errors.append(
                                {
                                    "code": "particle-update-member-digest",
                                    "update_id": update_id,
                                    "world_id": member["world_id"],
                                    "field": digest_field,
                                }
                            )
                    likelihood = parsed_numbers.get("likelihood")
                    if likelihood is not None and not 0.0 <= likelihood <= 1.0:
                        errors.append(
                            {
                                "code": "particle-update-likelihood-range",
                                "update_id": update_id,
                                "world_id": member["world_id"],
                            }
                        )
                    for field in (
                        "prior_weight",
                        "prior_probability",
                        "unnormalized_weight",
                        "posterior_probability",
                    ):
                        value = parsed_numbers.get(field)
                        if value is not None and value < 0.0:
                            errors.append(
                                {
                                    "code": "particle-update-member-negative-number",
                                    "update_id": update_id,
                                    "world_id": member["world_id"],
                                    "field": field,
                                }
                            )

                if not update_numbers_valid or not member_numbers_valid:
                    continue

                prior_sum = math.fsum(item["prior_weight"] for item in member_numbers)
                prior_probability_sum = math.fsum(
                    item["prior_probability"] for item in member_numbers
                )
                posterior_probability_sum = math.fsum(
                    item["posterior_probability"] for item in member_numbers
                )
                normalization = math.fsum(
                    item["prior_probability"] * item["likelihood"]
                    for item in member_numbers
                )
                if not math.isclose(
                    prior_sum,
                    update_numbers["prior_weight_sum"],
                    rel_tol=1e-12,
                    abs_tol=1e-15,
                ):
                    errors.append({"code": "particle-update-prior-weight-sum", "update_id": update_id})
                if not math.isclose(prior_probability_sum, 1.0, rel_tol=1e-12, abs_tol=1e-12):
                    errors.append(
                        {"code": "particle-update-prior-probability-sum", "update_id": update_id}
                    )
                if not math.isclose(posterior_probability_sum, 1.0, rel_tol=1e-12, abs_tol=1e-12):
                    errors.append(
                        {"code": "particle-update-posterior-probability-sum", "update_id": update_id}
                    )
                if normalization <= 0.0 or not math.isclose(
                    normalization,
                    update_numbers["normalization_constant"],
                    rel_tol=1e-12,
                    abs_tol=1e-15,
                ):
                    errors.append(
                        {"code": "particle-update-normalization", "update_id": update_id}
                    )
                    # Avoid dividing by an invalid normalization while preserving audit output.
                    continue

                for member, numbers in zip(members, member_numbers):
                    expected_unnormalized = (
                        numbers["prior_probability"] * numbers["likelihood"]
                    )
                    if not math.isclose(
                        expected_unnormalized,
                        numbers["unnormalized_weight"],
                        rel_tol=1e-12,
                        abs_tol=1e-15,
                    ):
                        errors.append(
                            {
                                "code": "particle-update-unnormalized-weight",
                                "update_id": update_id,
                                "world_id": member["world_id"],
                            }
                        )
                    expected_posterior = expected_unnormalized / normalization
                    if not math.isclose(
                        expected_posterior,
                        numbers["posterior_probability"],
                        rel_tol=1e-12,
                        abs_tol=1e-15,
                    ):
                        errors.append(
                            {
                                "code": "particle-update-posterior",
                                "update_id": update_id,
                                "world_id": member["world_id"],
                            }
                        )

                prior_stats = distribution_statistics(
                    item["prior_probability"] for item in member_numbers
                )
                posterior_stats = distribution_statistics(
                    item["posterior_probability"] for item in member_numbers
                )
                calculated = {
                    "prior_effective_sample_size": prior_stats["effective_sample_size"],
                    "posterior_effective_sample_size": posterior_stats["effective_sample_size"],
                    "prior_entropy_nats": prior_stats["entropy_nats"],
                    "posterior_entropy_nats": posterior_stats["entropy_nats"],
                    "information_gain_nats": math.fsum(
                        item["posterior_probability"]
                        * math.log(
                            item["posterior_probability"] / item["prior_probability"]
                        )
                        for item in member_numbers
                        if item["posterior_probability"] > 0.0
                        and item["prior_probability"] > 0.0
                    ),
                }
                for field, expected_value in calculated.items():
                    if not math.isclose(
                        expected_value,
                        update_numbers[field],
                        rel_tol=1e-12,
                        abs_tol=1e-15,
                    ):
                        errors.append(
                            {
                                "code": "particle-update-statistic",
                                "update_id": update_id,
                                "field": field,
                            }
                        )

                zero_count = sum(1 for item in member_numbers if item["likelihood"] == 0.0)
                if payload.get("zero_likelihood_world_count") != zero_count:
                    errors.append(
                        {
                            "code": "particle-update-zero-count",
                            "update_id": update_id,
                        }
                    )
                expected_divergence = valuation_likelihood_divergence_groups(
                    [
                        {
                            **member,
                            "likelihood": numbers["likelihood"],
                        }
                        for member, numbers in zip(members, member_numbers)
                    ]
                )
                if payload.get("valuation_likelihood_divergence_groups") != expected_divergence:
                    errors.append(
                        {
                            "code": "particle-update-divergence-groups",
                            "update_id": update_id,
                        }
                    )

                prior_particles = [
                    {
                        "world_id": member["world_id"],
                        "status": member["world_status"],
                        "raw_weight": numbers["prior_weight"],
                        "valuation_sha256": member["valuation_sha256"],
                        "custody_sha256": member["custody_sha256"],
                    }
                    for member, numbers in zip(members, member_numbers)
                ]
                posterior_particles = [
                    {
                        "world_id": member["world_id"],
                        "status": member["world_status"],
                        "raw_weight": numbers["posterior_probability"],
                        "valuation_sha256": member["valuation_sha256"],
                        "custody_sha256": member["custody_sha256"],
                    }
                    for member, numbers in zip(members, member_numbers)
                ]
                if particle_bank_sha256(prior_particles) != update_row["prior_bank_sha256"]:
                    errors.append({"code": "particle-update-prior-digest", "update_id": update_id})
                if particle_bank_sha256(posterior_particles) != update_row["posterior_bank_sha256"]:
                    errors.append(
                        {"code": "particle-update-posterior-digest", "update_id": update_id}
                    )

            for seq, event_row in event_rows_by_seq.items():
                if event_row["event_type"] != "particle.updated":
                    continue
                payload = event_payloads_by_seq.get(seq)
                update_id = payload.get("update_id") if isinstance(payload, dict) else None
                if not isinstance(update_id, str) or update_id not in projected_particle_update_ids:
                    errors.append(
                        {
                            "code": "particle-update-missing-projection",
                            "seq": seq,
                            "update_id": update_id,
                        }
                    )

            reconciliation_rows = [
                dict(row)
                for row in self.conn.execute(
                    """SELECT * FROM particle_reconciliations
                       ORDER BY created_seq, reconciliation_id"""
                ).fetchall()
            ]
            projected_reconciliation_ids: set[str] = set()
            reconciliation_float_fields = (
                "base_weight_sum",
                "log_normalization_constant",
                "base_effective_sample_size",
                "current_effective_sample_size",
                "posterior_effective_sample_size",
                "base_entropy_nats",
                "current_entropy_nats",
                "posterior_entropy_nats",
                "information_gain_from_base_nats",
                "current_to_posterior_total_variation",
            )
            reconciliation_member_float_fields = (
                "current_weight",
                "current_probability",
                "base_weight",
                "base_probability",
                "posterior_probability",
            )
            reconciliation_member_fields = (
                "world_id",
                "world_status",
                *reconciliation_member_float_fields,
                "log_factor_sum",
                "extinguished_by_update_id",
                "valuation_sha256",
                "custody_sha256",
            )
            for reconciliation_row in reconciliation_rows:
                reconciliation_id = str(reconciliation_row["reconciliation_id"])
                projected_reconciliation_ids.add(reconciliation_id)
                seq = int(reconciliation_row["created_seq"])
                event_row = event_rows_by_seq.get(seq)
                payload = event_payloads_by_seq.get(seq)
                if event_row is None or event_row["event_type"] != "particle.reconciled":
                    errors.append(
                        {
                            "code": "particle-reconciliation-origin-event",
                            "reconciliation_id": reconciliation_id,
                            "created_seq": seq,
                        }
                    )
                    continue
                if payload is None or payload.get("reconciliation_id") != reconciliation_id:
                    errors.append(
                        {
                            "code": "particle-reconciliation-payload-identity",
                            "reconciliation_id": reconciliation_id,
                            "created_seq": seq,
                        }
                    )
                    continue

                if reconciliation_row["method"] != PARTICLE_RECONCILIATION_METHOD:
                    errors.append(
                        {
                            "code": "particle-reconciliation-method",
                            "reconciliation_id": reconciliation_id,
                            "actual": reconciliation_row["method"],
                        }
                    )
                scalar_pairs = (
                    ("method", "method"),
                    ("baseline_update_id", "baseline_update_id"),
                    ("prior_bank_sha256", "prior_bank_sha256"),
                    ("baseline_bank_sha256", "baseline_bank_sha256"),
                    ("posterior_bank_sha256", "posterior_bank_sha256"),
                    ("factor_set_sha256", "factor_set_sha256"),
                    ("review_sha256", "reconciliation_review_sha256"),
                    ("reason", "reason"),
                )
                for projection_field, event_field in scalar_pairs:
                    if reconciliation_row[projection_field] != payload.get(event_field):
                        errors.append(
                            {
                                "code": "particle-reconciliation-projection-mismatch",
                                "reconciliation_id": reconciliation_id,
                                "field": projection_field,
                            }
                        )
                for digest_field in (
                    "prior_bank_sha256",
                    "baseline_bank_sha256",
                    "posterior_bank_sha256",
                    "factor_set_sha256",
                    "review_sha256",
                ):
                    if not SHA256_RE.fullmatch(str(reconciliation_row[digest_field])):
                        errors.append(
                            {
                                "code": "particle-reconciliation-digest-format",
                                "reconciliation_id": reconciliation_id,
                                "field": digest_field,
                            }
                        )

                projected_numbers: dict[str, float] = {}
                numbers_valid = True
                for field in reconciliation_float_fields:
                    projection_value = finite_number(reconciliation_row[field])
                    event_value = finite_number(payload.get(field))
                    if projection_value is None:
                        numbers_valid = False
                        errors.append(
                            {
                                "code": "particle-reconciliation-nonfinite-number",
                                "reconciliation_id": reconciliation_id,
                                "field": field,
                                "surface": "projection",
                            }
                        )
                    else:
                        projected_numbers[field] = projection_value
                    if event_value is None:
                        errors.append(
                            {
                                "code": "particle-reconciliation-nonfinite-number",
                                "reconciliation_id": reconciliation_id,
                                "field": field,
                                "surface": "event",
                            }
                        )
                    if (
                        projection_value is None
                        or event_value is None
                        or not math.isclose(
                            projection_value,
                            event_value,
                            rel_tol=1e-12,
                            abs_tol=1e-15,
                        )
                    ):
                        errors.append(
                            {
                                "code": "particle-reconciliation-projection-mismatch",
                                "reconciliation_id": reconciliation_id,
                                "field": field,
                            }
                        )

                boundary = payload.get("boundary")
                boundary_seq = reconciliation_row["boundary_seq"]
                if boundary is None:
                    if boundary_seq is not None:
                        errors.append(
                            {
                                "code": "particle-reconciliation-boundary-mismatch",
                                "reconciliation_id": reconciliation_id,
                            }
                        )
                    expected_boundary = None
                    epoch_start_seq = 0
                else:
                    if not isinstance(boundary, dict):
                        errors.append(
                            {
                                "code": "particle-reconciliation-boundary-shape",
                                "reconciliation_id": reconciliation_id,
                            }
                        )
                        expected_boundary = None
                        epoch_start_seq = 0
                    else:
                        try:
                            epoch_start_seq = int(boundary["seq"])
                        except (KeyError, TypeError, ValueError, OverflowError):
                            epoch_start_seq = 0
                        expected_boundary = event_rows_by_seq.get(epoch_start_seq)
                        if boundary_seq is None or int(boundary_seq) != epoch_start_seq:
                            errors.append(
                                {
                                    "code": "particle-reconciliation-boundary-mismatch",
                                    "reconciliation_id": reconciliation_id,
                                }
                            )
                        if (
                            expected_boundary is None
                            or expected_boundary["event_id"] != boundary.get("event_id")
                            or expected_boundary["event_type"] != boundary.get("event_type")
                            or expected_boundary["event_type"]
                            not in PARTICLE_EPOCH_BOUNDARY_EVENTS
                            or epoch_start_seq >= seq
                        ):
                            errors.append(
                                {
                                    "code": "particle-reconciliation-boundary-event",
                                    "reconciliation_id": reconciliation_id,
                                }
                            )
                placeholders = ",".join("?" for _ in PARTICLE_EPOCH_BOUNDARY_EVENTS)
                latest_boundary = self.conn.execute(
                    f"""SELECT seq, event_id, event_type FROM events
                         WHERE seq < ? AND event_type IN ({placeholders})
                         ORDER BY seq DESC LIMIT 1""",
                    (seq, *sorted(PARTICLE_EPOCH_BOUNDARY_EVENTS)),
                ).fetchone()
                latest_boundary_summary = (
                    None
                    if latest_boundary is None
                    else {
                        "seq": int(latest_boundary["seq"]),
                        "event_id": str(latest_boundary["event_id"]),
                        "event_type": str(latest_boundary["event_type"]),
                    }
                )
                if boundary != latest_boundary_summary:
                    errors.append(
                        {
                            "code": "particle-reconciliation-not-latest-boundary",
                            "reconciliation_id": reconciliation_id,
                        }
                    )

                change_row = self.conn.execute(
                    "SELECT before_head FROM changesets WHERE change_id = ?",
                    (event_row["change_id"],),
                ).fetchone()
                if (
                    change_row is None
                    or payload.get("reconciliation_review_head")
                    != change_row["before_head"]
                ):
                    errors.append(
                        {
                            "code": "particle-reconciliation-review-head",
                            "reconciliation_id": reconciliation_id,
                        }
                    )

                factor_rows = [
                    dict(row)
                    for row in self.conn.execute(
                        """SELECT * FROM particle_reconciliation_factors
                           WHERE reconciliation_id = ? ORDER BY ordinal""",
                        (reconciliation_id,),
                    ).fetchall()
                ]
                event_included = payload.get("included_factors")
                event_excluded = payload.get("excluded_factors")
                if not isinstance(event_included, list):
                    event_included = []
                    errors.append(
                        {
                            "code": "particle-reconciliation-included-factor-shape",
                            "reconciliation_id": reconciliation_id,
                        }
                    )
                if not isinstance(event_excluded, list):
                    event_excluded = []
                    errors.append(
                        {
                            "code": "particle-reconciliation-excluded-factor-shape",
                            "reconciliation_id": reconciliation_id,
                        }
                    )
                event_factor_pairs = [
                    ("included", factor) for factor in event_included
                ] + [("excluded", factor) for factor in event_excluded]
                if len(factor_rows) != len(event_factor_pairs):
                    errors.append(
                        {
                            "code": "particle-reconciliation-factor-count",
                            "reconciliation_id": reconciliation_id,
                            "projection_count": len(factor_rows),
                            "event_count": len(event_factor_pairs),
                        }
                    )
                for ordinal, factor_row in enumerate(factor_rows):
                    if int(factor_row["ordinal"]) != ordinal:
                        errors.append(
                            {
                                "code": "particle-reconciliation-factor-ordinal",
                                "reconciliation_id": reconciliation_id,
                                "update_id": factor_row["update_id"],
                            }
                        )
                    if ordinal >= len(event_factor_pairs):
                        continue
                    disposition, event_factor = event_factor_pairs[ordinal]
                    if not isinstance(event_factor, dict):
                        errors.append(
                            {
                                "code": "particle-reconciliation-factor-shape",
                                "reconciliation_id": reconciliation_id,
                                "ordinal": ordinal,
                            }
                        )
                        continue
                    expected_projection = {
                        "disposition": disposition,
                        "update_id": event_factor.get("update_id"),
                        "evidence_assertion_id": event_factor.get(
                            "evidence_assertion_id"
                        ),
                        "evidence_ended_seq": event_factor.get("evidence_ended_seq"),
                        "exclusion_reason": event_factor.get("exclusion_reason"),
                    }
                    for field, expected_value in expected_projection.items():
                        if factor_row[field] != expected_value:
                            errors.append(
                                {
                                    "code": "particle-reconciliation-factor-projection-mismatch",
                                    "reconciliation_id": reconciliation_id,
                                    "update_id": factor_row["update_id"],
                                    "field": field,
                                }
                            )

                historical_factor_rows = [
                    dict(row)
                    for row in self.conn.execute(
                        """SELECT pu.update_id, pu.evidence_assertion_id,
                                  pu.created_seq, a.ended_seq AS evidence_ended_seq
                             FROM particle_updates pu
                             JOIN assertions a
                               ON a.assertion_id = pu.evidence_assertion_id
                            WHERE pu.created_seq > ? AND pu.created_seq < ?
                            ORDER BY pu.created_seq, pu.update_id""",
                        (epoch_start_seq, seq),
                    ).fetchall()
                ]
                expected_included: list[dict[str, Any]] = []
                expected_excluded: list[dict[str, Any]] = []
                for factor in historical_factor_rows:
                    ended_seq = factor["evidence_ended_seq"]
                    active_at_reconciliation = ended_seq is None or int(ended_seq) >= seq
                    summary = {
                        "update_id": str(factor["update_id"]),
                        "evidence_assertion_id": str(factor["evidence_assertion_id"]),
                        "created_seq": int(factor["created_seq"]),
                        "evidence_status": (
                            "active" if active_at_reconciliation else "superseded"
                        ),
                        "evidence_ended_seq": (
                            None if active_at_reconciliation else int(ended_seq)
                        ),
                    }
                    if active_at_reconciliation:
                        expected_included.append(summary)
                    else:
                        summary["exclusion_reason"] = "evidence-superseded"
                        expected_excluded.append(summary)
                if event_included != expected_included or event_excluded != expected_excluded:
                    errors.append(
                        {
                            "code": "particle-reconciliation-factor-ledger-selection",
                            "reconciliation_id": reconciliation_id,
                        }
                    )
                if not historical_factor_rows:
                    errors.append(
                        {
                            "code": "particle-reconciliation-empty-epoch",
                            "reconciliation_id": reconciliation_id,
                        }
                    )
                elif reconciliation_row["baseline_update_id"] != historical_factor_rows[0]["update_id"]:
                    errors.append(
                        {
                            "code": "particle-reconciliation-baseline-factor",
                            "reconciliation_id": reconciliation_id,
                        }
                    )

                expected_factor_set = None
                if historical_factor_rows:
                    expected_factor_set = particle_factor_set_sha256(
                        baseline_update_id=str(historical_factor_rows[0]["update_id"]),
                        boundary=latest_boundary_summary,
                        included_factors=expected_included,
                        excluded_factors=expected_excluded,
                    )
                    if expected_factor_set != reconciliation_row["factor_set_sha256"]:
                        errors.append(
                            {
                                "code": "particle-reconciliation-factor-set-digest",
                                "reconciliation_id": reconciliation_id,
                            }
                        )

                members = [
                    dict(row)
                    for row in self.conn.execute(
                        """SELECT * FROM particle_reconciliation_members
                           WHERE reconciliation_id = ? ORDER BY ordinal""",
                        (reconciliation_id,),
                    ).fetchall()
                ]
                event_members = payload.get("members")
                if not isinstance(event_members, list) or len(event_members) != len(members):
                    errors.append(
                        {
                            "code": "particle-reconciliation-member-count",
                            "reconciliation_id": reconciliation_id,
                            "projection_count": len(members),
                            "event_count": (
                                len(event_members) if isinstance(event_members, list) else None
                            ),
                        }
                    )
                    event_members = []
                if not members:
                    errors.append(
                        {
                            "code": "particle-reconciliation-empty",
                            "reconciliation_id": reconciliation_id,
                        }
                    )
                    continue

                parsed_members: list[dict[str, Any]] = []
                members_valid = True
                for ordinal, member in enumerate(members):
                    if int(member["ordinal"]) != ordinal:
                        errors.append(
                            {
                                "code": "particle-reconciliation-member-ordinal",
                                "reconciliation_id": reconciliation_id,
                                "world_id": member["world_id"],
                            }
                        )
                    parsed: dict[str, Any] = {
                        "world_id": str(member["world_id"]),
                        "world_status": str(member["world_status"]),
                        "extinguished_by_update_id": member[
                            "extinguished_by_update_id"
                        ],
                        "valuation_sha256": str(member["valuation_sha256"]),
                        "custody_sha256": str(member["custody_sha256"]),
                    }
                    for field in reconciliation_member_float_fields:
                        number = finite_number(member[field])
                        if number is None:
                            members_valid = False
                            errors.append(
                                {
                                    "code": "particle-reconciliation-member-nonfinite-number",
                                    "reconciliation_id": reconciliation_id,
                                    "world_id": member["world_id"],
                                    "field": field,
                                }
                            )
                        else:
                            parsed[field] = number
                    log_factor_sum = member["log_factor_sum"]
                    if log_factor_sum is None:
                        parsed["log_factor_sum"] = None
                    else:
                        parsed_log = finite_number(log_factor_sum)
                        if parsed_log is None:
                            members_valid = False
                            errors.append(
                                {
                                    "code": "particle-reconciliation-member-nonfinite-number",
                                    "reconciliation_id": reconciliation_id,
                                    "world_id": member["world_id"],
                                    "field": "log_factor_sum",
                                }
                            )
                        parsed["log_factor_sum"] = parsed_log
                    parsed_members.append(parsed)

                    if ordinal < len(event_members) and isinstance(
                        event_members[ordinal], dict
                    ):
                        event_member = event_members[ordinal]
                        for field in reconciliation_member_fields:
                            left = member[field]
                            right = event_member.get(field)
                            if field in reconciliation_member_float_fields or field == "log_factor_sum":
                                if left is None or right is None:
                                    equal = left is None and right is None
                                else:
                                    left_number = finite_number(left)
                                    right_number = finite_number(right)
                                    equal = (
                                        left_number is not None
                                        and right_number is not None
                                        and math.isclose(
                                            left_number,
                                            right_number,
                                            rel_tol=1e-12,
                                            abs_tol=1e-15,
                                        )
                                    )
                            else:
                                equal = left == right
                            if not equal:
                                errors.append(
                                    {
                                        "code": "particle-reconciliation-member-projection-mismatch",
                                        "reconciliation_id": reconciliation_id,
                                        "world_id": member["world_id"],
                                        "field": field,
                                    }
                                )

                if not numbers_valid or not members_valid:
                    continue
                base_records = [
                    {
                        "world_id": item["world_id"],
                        "status": item["world_status"],
                        "raw_weight": item["base_weight"],
                        "valuation_sha256": item["valuation_sha256"],
                        "custody_sha256": item["custody_sha256"],
                    }
                    for item in parsed_members
                ]
                current_records = [
                    {
                        "world_id": item["world_id"],
                        "status": item["world_status"],
                        "raw_weight": item["current_weight"],
                        "valuation_sha256": item["valuation_sha256"],
                        "custody_sha256": item["custody_sha256"],
                    }
                    for item in parsed_members
                ]
                posterior_records = [
                    {
                        "world_id": item["world_id"],
                        "status": item["world_status"],
                        "raw_weight": item["posterior_probability"],
                        "valuation_sha256": item["valuation_sha256"],
                        "custody_sha256": item["custody_sha256"],
                    }
                    for item in parsed_members
                ]
                try:
                    baseline_bank = build_particle_bank_from_records(base_records)
                    current_bank = build_particle_bank_from_records(current_records)
                    posterior_bank = build_particle_bank_from_records(posterior_records)
                except ValueError:
                    errors.append(
                        {
                            "code": "particle-reconciliation-invalid-bank",
                            "reconciliation_id": reconciliation_id,
                        }
                    )
                    continue
                digest_expectations = {
                    "baseline_bank_sha256": baseline_bank["bank_sha256"],
                    "prior_bank_sha256": current_bank["bank_sha256"],
                    "posterior_bank_sha256": posterior_bank["bank_sha256"],
                }
                for field, expected_digest in digest_expectations.items():
                    if reconciliation_row[field] != expected_digest:
                        errors.append(
                            {
                                "code": "particle-reconciliation-bank-digest",
                                "reconciliation_id": reconciliation_id,
                                "field": field,
                            }
                        )
                if not math.isclose(
                    math.fsum(item["base_weight"] for item in parsed_members),
                    projected_numbers["base_weight_sum"],
                    rel_tol=1e-12,
                    abs_tol=1e-15,
                ):
                    errors.append(
                        {
                            "code": "particle-reconciliation-base-weight-sum",
                            "reconciliation_id": reconciliation_id,
                        }
                    )

                full_included_factors: list[dict[str, Any]] = []
                for factor in expected_included:
                    update_row = self.conn.execute(
                        "SELECT * FROM particle_updates WHERE update_id = ?",
                        (factor["update_id"],),
                    ).fetchone()
                    assessments = [
                        dict(row)
                        for row in self.conn.execute(
                            """SELECT * FROM particle_update_members
                               WHERE update_id = ? ORDER BY ordinal""",
                            (factor["update_id"],),
                        ).fetchall()
                    ]
                    if update_row is None:
                        errors.append(
                            {
                                "code": "particle-reconciliation-missing-factor",
                                "reconciliation_id": reconciliation_id,
                                "update_id": factor["update_id"],
                            }
                        )
                        continue
                    full_factor = dict(factor)
                    full_factor["assessments"] = assessments
                    full_included_factors.append(full_factor)
                if len(full_included_factors) != len(expected_included):
                    continue
                try:
                    calculated = compute_factor_reconciliation(
                        baseline_bank=baseline_bank,
                        current_bank=current_bank,
                        included_factors=full_included_factors,
                    )
                except ValueError as exc:
                    errors.append(
                        {
                            "code": "particle-reconciliation-replay-failed",
                            "reconciliation_id": reconciliation_id,
                            "message": str(exc),
                        }
                    )
                    continue
                calculated_fields = (
                    "log_normalization_constant",
                    "base_effective_sample_size",
                    "current_effective_sample_size",
                    "posterior_effective_sample_size",
                    "base_entropy_nats",
                    "current_entropy_nats",
                    "posterior_entropy_nats",
                    "information_gain_from_base_nats",
                    "current_to_posterior_total_variation",
                )
                for field in calculated_fields:
                    if not math.isclose(
                        float(calculated[field]),
                        projected_numbers[field],
                        rel_tol=1e-12,
                        abs_tol=1e-15,
                    ):
                        errors.append(
                            {
                                "code": "particle-reconciliation-statistic",
                                "reconciliation_id": reconciliation_id,
                                "field": field,
                            }
                        )
                if payload.get("extinguished_world_count") != calculated[
                    "extinguished_world_count"
                ]:
                    errors.append(
                        {
                            "code": "particle-reconciliation-extinguished-count",
                            "reconciliation_id": reconciliation_id,
                        }
                    )
                calculated_by_world = {
                    str(item["world_id"]): item for item in calculated["members"]
                }
                for member in parsed_members:
                    expected_member = calculated_by_world.get(member["world_id"])
                    if expected_member is None:
                        errors.append(
                            {
                                "code": "particle-reconciliation-replay-member",
                                "reconciliation_id": reconciliation_id,
                                "world_id": member["world_id"],
                            }
                        )
                        continue
                    for field in (
                        "current_probability",
                        "base_probability",
                        "log_factor_sum",
                        "posterior_probability",
                    ):
                        left = member[field]
                        right = expected_member[field]
                        if left is None or right is None:
                            equal = left is None and right is None
                        else:
                            equal = math.isclose(
                                float(left),
                                float(right),
                                rel_tol=1e-12,
                                abs_tol=1e-15,
                            )
                        if not equal:
                            errors.append(
                                {
                                    "code": "particle-reconciliation-replay-member",
                                    "reconciliation_id": reconciliation_id,
                                    "world_id": member["world_id"],
                                    "field": field,
                                }
                            )
                    if member["extinguished_by_update_id"] != expected_member[
                        "extinguished_by_update_id"
                    ]:
                        errors.append(
                            {
                                "code": "particle-reconciliation-replay-member",
                                "reconciliation_id": reconciliation_id,
                                "world_id": member["world_id"],
                                "field": "extinguished_by_update_id",
                            }
                        )

                result_summary = {
                    "posterior_bank_sha256": payload.get("posterior_bank_sha256"),
                    "log_normalization_constant": payload.get(
                        "log_normalization_constant"
                    ),
                    "base_effective_sample_size": payload.get(
                        "base_effective_sample_size"
                    ),
                    "current_effective_sample_size": payload.get(
                        "current_effective_sample_size"
                    ),
                    "posterior_effective_sample_size": payload.get(
                        "posterior_effective_sample_size"
                    ),
                    "base_entropy_nats": payload.get("base_entropy_nats"),
                    "current_entropy_nats": payload.get("current_entropy_nats"),
                    "posterior_entropy_nats": payload.get("posterior_entropy_nats"),
                    "information_gain_from_base_nats": payload.get(
                        "information_gain_from_base_nats"
                    ),
                    "current_to_posterior_total_variation": payload.get(
                        "current_to_posterior_total_variation"
                    ),
                    "extinguished_world_count": payload.get(
                        "extinguished_world_count"
                    ),
                    "members": payload.get("members"),
                }
                review_core = {
                    "schema": "lacuna.particle-reconciliation-review-core.v1",
                    "boundary": payload.get("boundary"),
                    "baseline_update_id": payload.get("baseline_update_id"),
                    "baseline_bank_sha256": payload.get("baseline_bank_sha256"),
                    "current_bank_sha256": payload.get("prior_bank_sha256"),
                    "factor_set_sha256": payload.get("factor_set_sha256"),
                    "included_factors": payload.get("included_factors"),
                    "excluded_factors": payload.get("excluded_factors"),
                    "blockers": [],
                    "result": result_summary,
                }
                review_head = payload.get("reconciliation_review_head")
                if isinstance(review_head, str):
                    expected_review_digest = particle_reconciliation_review_sha256(
                        cube_id=self.meta("cube_id"),
                        head=review_head,
                        review_core=review_core,
                    )
                    if expected_review_digest != payload.get(
                        "reconciliation_review_sha256"
                    ):
                        errors.append(
                            {
                                "code": "particle-reconciliation-review-digest",
                                "reconciliation_id": reconciliation_id,
                            }
                        )

            for seq, event_row in event_rows_by_seq.items():
                if event_row["event_type"] != "particle.reconciled":
                    continue
                payload = event_payloads_by_seq.get(seq)
                reconciliation_id = (
                    payload.get("reconciliation_id")
                    if isinstance(payload, dict)
                    else None
                )
                if (
                    not isinstance(reconciliation_id, str)
                    or reconciliation_id not in projected_reconciliation_ids
                ):
                    errors.append(
                        {
                            "code": "particle-reconciliation-missing-projection",
                            "seq": seq,
                            "reconciliation_id": reconciliation_id,
                        }
                    )

            consequence_rows = [
                dict(row)
                for row in self.conn.execute(
                    "SELECT * FROM consequence_links ORDER BY created_seq, consequence_id"
                ).fetchall()
            ]
            active_assignment_edges: list[tuple[str, str]] = []
            dependent_tables = {
                "assertion": ("assertions", "assertion_id"),
                "world_assignment": ("world_assignments", "assignment_id"),
                "question": ("questions", "question_id"),
            }
            for row in consequence_rows:
                consequence_id = str(row["consequence_id"])
                premise_id = str(row["premise_assignment_id"])
                kind = str(row["dependent_kind"])
                dependent_id = str(row["dependent_id"])
                if premise_id not in assignments_by_id:
                    errors.append(
                        {
                            "code": "consequence-missing-premise",
                            "consequence_id": consequence_id,
                            "premise_assignment_id": premise_id,
                        }
                    )
                if kind not in CONSEQUENCE_DEPENDENT_KINDS:
                    errors.append(
                        {
                            "code": "consequence-dependent-kind-enum",
                            "consequence_id": consequence_id,
                            "dependent_kind": kind,
                        }
                    )
                else:
                    table, field = dependent_tables[kind]
                    if not self._exists(table, field, dependent_id):
                        errors.append(
                            {
                                "code": "consequence-missing-dependent",
                                "consequence_id": consequence_id,
                                "dependent_kind": kind,
                                "dependent_id": dependent_id,
                            }
                        )
                if str(row["relation"]) not in CONSEQUENCE_RELATIONS:
                    errors.append(
                        {
                            "code": "consequence-relation-enum",
                            "consequence_id": consequence_id,
                            "relation": row["relation"],
                        }
                    )
                if str(row["severity"]) not in CONSEQUENCE_SEVERITIES:
                    errors.append(
                        {
                            "code": "consequence-severity-enum",
                            "consequence_id": consequence_id,
                            "severity": row["severity"],
                        }
                    )
                if row["ended_seq"] is not None and int(row["ended_seq"]) < int(row["created_seq"]):
                    errors.append(
                        {
                            "code": "consequence-negative-custody-interval",
                            "consequence_id": consequence_id,
                        }
                    )
                if row["ended_seq"] is None and kind == "world_assignment":
                    active_assignment_edges.append((premise_id, dependent_id))

            consequence_by_id = {
                str(row["consequence_id"]): row for row in consequence_rows
            }
            repair_rows = [
                dict(row)
                for row in self.conn.execute(
                    "SELECT * FROM consequence_repairs ORDER BY created_seq, repair_id"
                ).fetchall()
            ]
            for repair in repair_rows:
                repair_id = str(repair["repair_id"])
                predecessor_id = str(repair["predecessor_consequence_id"])
                successor_id = str(repair["successor_consequence_id"])
                predecessor = consequence_by_id.get(predecessor_id)
                successor = consequence_by_id.get(successor_id)
                if predecessor_id == successor_id:
                    errors.append(
                        {
                            "code": "consequence-repair-self-replacement",
                            "repair_id": repair_id,
                            "consequence_id": predecessor_id,
                        }
                    )
                if predecessor is None:
                    errors.append(
                        {
                            "code": "consequence-repair-missing-predecessor",
                            "repair_id": repair_id,
                            "predecessor_consequence_id": predecessor_id,
                        }
                    )
                if successor is None:
                    errors.append(
                        {
                            "code": "consequence-repair-missing-successor",
                            "repair_id": repair_id,
                            "successor_consequence_id": successor_id,
                        }
                    )
                if not SHA256_RE.fullmatch(str(repair["review_sha256"])):
                    errors.append(
                        {
                            "code": "consequence-repair-review-digest",
                            "repair_id": repair_id,
                        }
                    )
                repair_seq = int(repair["created_seq"])
                if predecessor is not None:
                    if predecessor["ended_seq"] != repair_seq:
                        errors.append(
                            {
                                "code": "consequence-repair-predecessor-boundary",
                                "repair_id": repair_id,
                                "predecessor_consequence_id": predecessor_id,
                            }
                        )
                    if predecessor["retirement_reason"] != repair["reason"]:
                        errors.append(
                            {
                                "code": "consequence-repair-reason-mismatch",
                                "repair_id": repair_id,
                            }
                        )
                if successor is not None:
                    if int(successor["created_seq"]) != repair_seq:
                        errors.append(
                            {
                                "code": "consequence-repair-successor-boundary",
                                "repair_id": repair_id,
                                "successor_consequence_id": successor_id,
                            }
                        )
                if predecessor is not None and successor is not None:
                    if int(predecessor["created_seq"]) >= int(successor["created_seq"]):
                        errors.append(
                            {
                                "code": "consequence-repair-lineage-order",
                                "repair_id": repair_id,
                            }
                        )

                event_row = event_rows_by_seq.get(repair_seq)
                event_payload = event_payloads_by_seq.get(repair_seq)
                if event_row is None or event_row["event_type"] != "consequence.replaced":
                    errors.append(
                        {
                            "code": "consequence-repair-origin-event",
                            "repair_id": repair_id,
                            "created_seq": repair_seq,
                        }
                    )
                elif event_payload is None:
                    errors.append(
                        {
                            "code": "consequence-repair-origin-payload",
                            "repair_id": repair_id,
                            "created_seq": repair_seq,
                        }
                    )
                else:
                    expected_projection = {
                        "repair_id": repair_id,
                        "predecessor_consequence_id": predecessor_id,
                        "successor_consequence_id": successor_id,
                        "reason": repair["reason"],
                        "repair_review_sha256": repair["review_sha256"],
                    }
                    if successor is not None:
                        expected_projection.update(
                            {
                                "premise_assignment_id": successor["premise_assignment_id"],
                                "dependent_kind": successor["dependent_kind"],
                                "dependent_id": successor["dependent_id"],
                                "relation": successor["relation"],
                                "severity": successor["severity"],
                                "source_id": successor["source_id"],
                                "rationale": successor["rationale"],
                            }
                        )
                    mismatches = {
                        key: {"event": event_payload.get(key), "projection": value}
                        for key, value in expected_projection.items()
                        if event_payload.get(key) != value
                    }
                    if mismatches:
                        errors.append(
                            {
                                "code": "consequence-repair-projection-mismatch",
                                "repair_id": repair_id,
                                "mismatches": mismatches,
                            }
                        )
                    review_head = event_payload.get("repair_review_head")
                    if not isinstance(review_head, str) or not SHA256_RE.fullmatch(
                        review_head
                    ):
                        errors.append(
                            {
                                "code": "consequence-repair-review-head",
                                "repair_id": repair_id,
                                "actual": review_head,
                            }
                        )
                    change_receipt = change_rows.get(str(event_row["change_id"]))
                    if (
                        change_receipt is not None
                        and review_head != change_receipt["before_head"]
                    ):
                        errors.append(
                            {
                                "code": "consequence-repair-review-head-mismatch",
                                "repair_id": repair_id,
                                "event_review_head": review_head,
                                "change_before_head": change_receipt["before_head"],
                            }
                        )

            projected_repair_ids = {str(row["repair_id"]) for row in repair_rows}
            for seq, event_row in event_rows_by_seq.items():
                if event_row["event_type"] != "consequence.replaced":
                    continue
                payload = event_payloads_by_seq.get(seq)
                if payload is None:
                    continue
                repair_id = payload.get("repair_id")
                if not isinstance(repair_id, str) or repair_id not in projected_repair_ids:
                    errors.append(
                        {
                            "code": "consequence-replacement-missing-projection",
                            "seq": seq,
                            "repair_id": repair_id,
                        }
                    )

            seal_rows = [
                dict(row)
                for row in self.conn.execute(
                    "SELECT * FROM fair_play_seals ORDER BY created_seq, seal_id"
                ).fetchall()
            ]
            seal_by_id = {str(row["seal_id"]): row for row in seal_rows}
            for seal_row in seal_rows:
                seal_id = str(seal_row["seal_id"])
                created_seq = int(seal_row["created_seq"])
                if seal_row["scheme"] != SEAL_SCHEME:
                    errors.append(
                        {
                            "code": "seal-scheme",
                            "seal_id": seal_id,
                            "actual": seal_row["scheme"],
                        }
                    )
                if seal_row["purpose"] not in SEAL_PURPOSES:
                    errors.append(
                        {
                            "code": "seal-purpose-enum",
                            "seal_id": seal_id,
                            "actual": seal_row["purpose"],
                        }
                    )
                if seal_row["visibility"] not in SEAL_VISIBILITIES:
                    errors.append(
                        {
                            "code": "seal-visibility-enum",
                            "seal_id": seal_id,
                            "actual": seal_row["visibility"],
                        }
                    )
                if not SHA256_RE.fullmatch(str(seal_row["commitment_sha256"])):
                    errors.append({"code": "seal-commitment-digest", "seal_id": seal_id})
                try:
                    audience = json.loads(str(seal_row["audience_json"]))
                except (json.JSONDecodeError, TypeError) as exc:
                    audience = None
                    errors.append(
                        {
                            "code": "seal-audience-json",
                            "seal_id": seal_id,
                            "message": str(exc),
                        }
                    )
                if not isinstance(audience, list) or any(
                    not isinstance(agent_id, str) for agent_id in (audience or [])
                ):
                    errors.append({"code": "seal-audience-shape", "seal_id": seal_id})
                elif (seal_row["visibility"] == "restricted") != bool(audience):
                    errors.append(
                        {
                            "code": "seal-audience-visibility",
                            "seal_id": seal_id,
                        }
                    )

                revealed_seq = seal_row["revealed_seq"]
                voided_seq = seal_row["voided_seq"]
                if revealed_seq is not None and voided_seq is not None:
                    errors.append({"code": "seal-double-resolution", "seal_id": seal_id})
                if revealed_seq is None:
                    if any(
                        seal_row[field] is not None
                        for field in ("reveal_payload_json", "reveal_nonce", "reveal_reason")
                    ):
                        errors.append(
                            {"code": "seal-incomplete-reveal-custody", "seal_id": seal_id}
                        )
                elif any(
                    seal_row[field] is None
                    for field in ("reveal_payload_json", "reveal_nonce", "reveal_reason")
                ):
                    errors.append(
                        {"code": "seal-incomplete-reveal-custody", "seal_id": seal_id}
                    )
                if voided_seq is None and seal_row["void_reason"] is not None:
                    errors.append({"code": "seal-incomplete-void-custody", "seal_id": seal_id})
                if voided_seq is not None and seal_row["void_reason"] is None:
                    errors.append({"code": "seal-incomplete-void-custody", "seal_id": seal_id})

                origin_event = event_rows_by_seq.get(created_seq)
                origin_payload = event_payloads_by_seq.get(created_seq)
                if origin_event is None or origin_event["event_type"] != "precommitment.sealed":
                    errors.append(
                        {
                            "code": "seal-origin-event",
                            "seal_id": seal_id,
                            "created_seq": created_seq,
                        }
                    )
                elif origin_payload is None:
                    errors.append({"code": "seal-origin-payload", "seal_id": seal_id})
                else:
                    expected_origin = {
                        "seal_id": seal_id,
                        "scheme": seal_row["scheme"],
                        "commitment_sha256": seal_row["commitment_sha256"],
                        "label": seal_row["label"],
                        "purpose": seal_row["purpose"],
                        "visibility": seal_row["visibility"],
                        "audience": audience,
                        "source_id": seal_row["source_id"],
                    }
                    if origin_payload != expected_origin:
                        errors.append(
                            {
                                "code": "seal-origin-projection-mismatch",
                                "seal_id": seal_id,
                            }
                        )

                if revealed_seq is not None:
                    reveal_seq = int(revealed_seq)
                    reveal_event = event_rows_by_seq.get(reveal_seq)
                    reveal_payload = event_payloads_by_seq.get(reveal_seq)
                    if reveal_seq <= created_seq:
                        errors.append({"code": "seal-reveal-order", "seal_id": seal_id})
                    if (
                        reveal_event is None
                        or reveal_event["event_type"] != "precommitment.revealed"
                        or reveal_payload is None
                    ):
                        errors.append(
                            {
                                "code": "seal-reveal-event",
                                "seal_id": seal_id,
                                "revealed_seq": reveal_seq,
                            }
                        )
                    else:
                        if (
                            origin_event is not None
                            and reveal_event["change_id"] == origin_event["change_id"]
                        ):
                            errors.append(
                                {"code": "seal-phase-collapse", "seal_id": seal_id}
                            )
                        try:
                            projected_payload = json.loads(
                                str(seal_row["reveal_payload_json"])
                            )
                        except (json.JSONDecodeError, TypeError) as exc:
                            projected_payload = None
                            errors.append(
                                {
                                    "code": "seal-reveal-json",
                                    "seal_id": seal_id,
                                    "message": str(exc),
                                }
                            )
                        expected_reveal = {
                            "seal_id": seal_id,
                            "scheme": seal_row["scheme"],
                            "commitment_sha256": seal_row["commitment_sha256"],
                            "nonce": seal_row["reveal_nonce"],
                            "payload": projected_payload,
                            "reason": seal_row["reveal_reason"],
                        }
                        if reveal_payload != expected_reveal:
                            errors.append(
                                {
                                    "code": "seal-reveal-projection-mismatch",
                                    "seal_id": seal_id,
                                }
                            )
                        try:
                            valid_opening = opening_matches_commitment(
                                cube_id=self.meta("cube_id"),
                                seal_id=seal_id,
                                commitment_sha256=str(seal_row["commitment_sha256"]),
                                payload=projected_payload,
                                nonce=str(seal_row["reveal_nonce"]),
                                scheme=str(seal_row["scheme"]),
                            )
                        except LacunaError:
                            valid_opening = False
                        if not valid_opening:
                            errors.append({"code": "seal-reveal-digest", "seal_id": seal_id})

                if voided_seq is not None:
                    void_seq = int(voided_seq)
                    void_event = event_rows_by_seq.get(void_seq)
                    void_payload = event_payloads_by_seq.get(void_seq)
                    if void_seq <= created_seq:
                        errors.append({"code": "seal-void-order", "seal_id": seal_id})
                    if (
                        void_event is None
                        or void_event["event_type"] != "precommitment.voided"
                        or void_payload is None
                    ):
                        errors.append(
                            {
                                "code": "seal-void-event",
                                "seal_id": seal_id,
                                "voided_seq": void_seq,
                            }
                        )
                    else:
                        if (
                            origin_event is not None
                            and void_event["change_id"] == origin_event["change_id"]
                        ):
                            errors.append({"code": "seal-phase-collapse", "seal_id": seal_id})
                        expected_void = {
                            "seal_id": seal_id,
                            "commitment_sha256": seal_row["commitment_sha256"],
                            "reason": seal_row["void_reason"],
                        }
                        if void_payload != expected_void:
                            errors.append(
                                {
                                    "code": "seal-void-projection-mismatch",
                                    "seal_id": seal_id,
                                }
                            )

            for seq, event_row in event_rows_by_seq.items():
                if event_row["event_type"] not in {
                    "precommitment.sealed",
                    "precommitment.revealed",
                    "precommitment.voided",
                }:
                    continue
                payload = event_payloads_by_seq.get(seq)
                if payload is None:
                    continue
                seal_id = payload.get("seal_id")
                seal_row = seal_by_id.get(str(seal_id))
                if seal_row is None:
                    errors.append(
                        {
                            "code": "precommitment-event-missing-projection",
                            "seq": seq,
                            "seal_id": seal_id,
                        }
                    )
                    continue
                if event_row["event_type"] == "precommitment.sealed" and int(
                    seal_row["created_seq"]
                ) != seq:
                    errors.append({"code": "seal-origin-sequence", "seal_id": seal_id})
                if event_row["event_type"] == "precommitment.revealed" and seal_row[
                    "revealed_seq"
                ] != seq:
                    errors.append({"code": "seal-reveal-sequence", "seal_id": seal_id})
                if event_row["event_type"] == "precommitment.voided" and seal_row[
                    "voided_seq"
                ] != seq:
                    errors.append({"code": "seal-void-sequence", "seal_id": seal_id})

            adjacency: dict[str, list[str]] = {}
            for left, right in active_assignment_edges:
                adjacency.setdefault(left, []).append(right)
            for values in adjacency.values():
                values.sort()
            state: dict[str, int] = {}
            stack: list[str] = []
            cycle_witness: list[str] | None = None

            def visit_assignment(node: str) -> bool:
                nonlocal cycle_witness
                state[node] = 1
                stack.append(node)
                for neighbor in adjacency.get(node, []):
                    if state.get(neighbor, 0) == 0:
                        if visit_assignment(neighbor):
                            return True
                    elif state.get(neighbor) == 1:
                        index = stack.index(neighbor)
                        cycle_witness = [*stack[index:], neighbor]
                        return True
                stack.pop()
                state[node] = 2
                return False

            for node in sorted(set(adjacency) | {n for values in adjacency.values() for n in values}):
                if state.get(node, 0) == 0 and visit_assignment(node):
                    break
            if cycle_witness is not None:
                errors.append(
                    {
                        "code": "active-consequence-cycle",
                        "cycle": cycle_witness,
                    }
                )

        return {
            "event": "lacuna.verify",
            "schema": "lacuna.verify.v1",
            "overall_status": "pass" if not errors else "fail",
            "scope": "full" if include_projections else "ledger",
            "cube_id": self.meta("cube_id"),
            "head": self.head(),
            "database_schema_version": database_schema_version,
            "supported_event_schema_versions": sorted(SUPPORTED_EVENT_SCHEMA_VERSIONS),
            "event_count": len(rows),
            "sqlite_integrity": integrity,
            "foreign_key_error_count": len(foreign_rows),
            "ignored_projection_foreign_key_error_count": 0 if include_projections else len(all_foreign_rows),
            "error_count": len(errors),
            "errors": errors,
            "nonclaim": "the hash chain detects internal mutation under the current verifier; it is not an external signature or hostile-host guarantee",
        }

    def rebuild_projections(self) -> dict[str, Any]:
        verification = self.verify(include_projections=False)
        if verification["overall_status"] != "pass":
            raise LacunaError("cannot-rebuild-invalid-ledger", "event ledger verification failed", verification)
        rows = self.conn.execute("SELECT seq, event_id, event_type, payload_json FROM events ORDER BY seq").fetchall()
        self.conn.execute("BEGIN IMMEDIATE")
        try:
            for table in PROJECTION_TABLES:
                self.conn.execute(f"DELETE FROM {table}")
            for row in rows:
                self._apply_projection(
                    row["event_type"],
                    json.loads(row["payload_json"]),
                    seq=row["seq"],
                    event_id=row["event_id"],
                )
            self.conn.commit()
        except Exception:
            self.conn.rollback()
            raise
        post = self.verify()
        return {
            "event": "lacuna.projections.rebuilt",
            "schema": "lacuna.rebuild.v1",
            "overall_status": post["overall_status"],
            "cube_id": self.meta("cube_id"),
            "head": self.head(),
            "replayed_event_count": len(rows),
            "verification": post,
        }

    def _normalize_seal_row(self, row: sqlite3.Row | dict[str, Any]) -> dict[str, Any]:
        item = dict(row)
        item["audience"] = json.loads(item.pop("audience_json"))
        reveal_payload_json = item.pop("reveal_payload_json")
        item["reveal_payload"] = (
            None if reveal_payload_json is None else json.loads(reveal_payload_json)
        )
        if item["revealed_seq"] is not None:
            item["status"] = "revealed"
        elif item["voided_seq"] is not None:
            item["status"] = "voided"
        else:
            item["status"] = "sealed"
        return item

    def seal_visible_to(self, seal: dict[str, Any], agent_id: str) -> bool:
        return seal["visibility"] == "public" or agent_id in seal["audience"]

    def seals(
        self,
        *,
        agent_id: str | None = None,
        status: str | None = None,
    ) -> list[dict[str, Any]]:
        if agent_id is not None:
            self._require_agent(agent_id, "agent_id")
        if status is not None and status not in {"sealed", "revealed", "voided"}:
            raise LacunaError(
                "bad-seal-status",
                "seal status must be sealed, revealed, or voided",
                {"actual": status},
            )
        rows = self.conn.execute(
            "SELECT * FROM fair_play_seals ORDER BY created_seq, seal_id"
        ).fetchall()
        result: list[dict[str, Any]] = []
        for row in rows:
            item = self._normalize_seal_row(row)
            if status is not None and item["status"] != status:
                continue
            if agent_id is not None and not self.seal_visible_to(item, agent_id):
                continue
            if agent_id is not None:
                # A perspective receives the published commitment and opening, not
                # privileged source-graph linkage. The receipt remains independently
                # useful without naming hidden provenance records.
                item.pop("source_id", None)
            result.append(item)
        return result

    def seal(self, seal_id: str, *, agent_id: str | None = None) -> dict[str, Any]:
        row = self._require_seal(seal_id)
        item = self._normalize_seal_row(row)
        if agent_id is not None:
            self._require_agent(agent_id, "agent_id")
            if not self.seal_visible_to(item, agent_id):
                raise LacunaError(
                    "seal-not-visible",
                    "the requested fair-play seal is not visible to this perspective",
                    {"seal_id": seal_id, "agent_id": agent_id},
                )
            item.pop("source_id", None)
        return item

    def seal_receipt(
        self,
        seal_id: str,
        *,
        agent_id: str | None = None,
    ) -> dict[str, Any]:
        item = self.seal(seal_id, agent_id=agent_id)
        origin = self._event_at_seq(int(item["created_seq"]))
        if origin is None or origin["event_type"] != "precommitment.sealed":
            raise LacunaError(
                "seal-origin-missing",
                "fair-play seal has no matching immutable origin event",
                {"seal_id": seal_id},
            )
        change = self.conn.execute(
            "SELECT after_head FROM changesets WHERE change_id = ?",
            (origin["change_id"],),
        ).fetchone()
        if change is None:
            raise LacunaError(
                "seal-origin-uncommitted",
                "fair-play seal origin has no committed change receipt",
                {"seal_id": seal_id},
            )
        public_seal = {
            key: value
            for key, value in item.items()
            if key
            not in {
                "source_id",
                "reveal_payload",
                "reveal_nonce",
                "reveal_reason",
                "void_reason",
            }
        }
        # The externally anchorable receipt core must never change as the seal moves
        # from sealed to revealed or voided. Keep lifecycle fields in the live view,
        # but hash only metadata fixed by the origin event.
        immutable_seal = {
            key: item[key]
            for key in (
                "seal_id",
                "scheme",
                "commitment_sha256",
                "label",
                "purpose",
                "visibility",
                "audience",
                "created_seq",
            )
        }
        opening = None
        if item["status"] == "revealed":
            opening = {
                "nonce": item["reveal_nonce"],
                "payload": item["reveal_payload"],
                "reason": item["reveal_reason"],
                "revealed_seq": item["revealed_seq"],
            }
        resolution = None
        if item["status"] == "voided":
            resolution = {
                "status": "voided",
                "reason": item["void_reason"],
                "voided_seq": item["voided_seq"],
            }
        commitment_event = {
            "seq": origin["seq"],
            "event_id": origin["event_id"],
            "event_hash": origin["event_hash"],
            "prev_hash": origin["prev_hash"],
            "recorded_at": origin["recorded_at"],
            "change_after_head": str(change["after_head"]),
        }
        receipt_core = {
            "schema": "lacuna.fair-play-seal-receipt-core.v1",
            "cube_id": self.meta("cube_id"),
            "seal": immutable_seal,
            "commitment_event": commitment_event,
        }
        receipt = {
            "event": "lacuna.fair-play-seal.receipt",
            "schema": "lacuna.fair-play-seal-receipt.v1",
            "cube_id": self.meta("cube_id"),
            "current_head": self.head(),
            "receipt_sha256": sha256_text(canonical_json(receipt_core)),
            "receipt_core": receipt_core,
            "seal": public_seal,
            "commitment_event": commitment_event,
            "opening": opening,
            "resolution": resolution,
            "nonclaims": [
                "This receipt proves only that one byte-stable opening matches the recorded salted digest.",
                "It does not prove that the payload is true, complete, authored at the stated real-world time, or the only secret the host considered.",
                "The internal hash chain is not an external timestamp, signature, or non-equivocation service; retain the receipt or anchor its digest outside the cube before relying on it against a hostile host.",
            ],
        }
        if agent_id is not None:
            receipt["access"] = {
                "mode": "perspective",
                "agent_id": agent_id,
                "privileged": False,
            }
        else:
            receipt["access"] = {"mode": "planner", "agent_id": None, "privileged": True}
        return receipt

    def verify_seal_opening(
        self,
        opening_document: Any,
        *,
        agent_id: str | None = None,
    ) -> dict[str, Any]:
        opening = parse_seal_opening(opening_document)
        seal_id = opening["seal_id"]
        item = self.seal(seal_id, agent_id=agent_id)
        cube_matches = opening["cube_id"] == self.meta("cube_id")
        digest_matches = opening["commitment_sha256"] == item["commitment_sha256"]
        cryptographic_match = False
        if cube_matches:
            cryptographic_match = opening_matches_commitment(
                cube_id=self.meta("cube_id"),
                seal_id=seal_id,
                commitment_sha256=item["commitment_sha256"],
                payload=opening["payload"],
                nonce=opening["nonce"],
                scheme=item["scheme"],
            )
        revealed_match: bool | None = None
        if item["status"] == "revealed":
            revealed_match = (
                item["reveal_nonce"] == opening["nonce"]
                and item["reveal_payload"] == opening["payload"]
            )
        overall = cube_matches and digest_matches and cryptographic_match
        if revealed_match is False:
            overall = False
        return {
            "event": "lacuna.fair-play-seal.opening-verification",
            "schema": "lacuna.fair-play-seal-opening-verification.v1",
            "overall_status": "pass" if overall else "fail",
            "cube_id": self.meta("cube_id"),
            "head": self.head(),
            "seal_id": seal_id,
            "record_status": item["status"],
            "checks": {
                "cube_id_matches": cube_matches,
                "commitment_digest_matches": digest_matches,
                "opening_matches_recorded_commitment": cryptographic_match,
                "opening_matches_recorded_reveal": revealed_match,
            },
            "nonclaim": (
                "A passing opening verifies byte continuity under the recorded scheme; "
                "it does not establish narrative truth, authorship, completeness, or an external timestamp."
            ),
        }

    def status(self) -> dict[str, Any]:
        def count(sql: str, params: Iterable[Any] = ()) -> int:
            return int(self.conn.execute(sql, tuple(params)).fetchone()[0])

        conflicts = self.conflicts()
        particle_bank = self.particle_bank()
        return {
            "event": "lacuna.status",
            "schema": "lacuna.status.v1",
            "project": "Lacuna",
            "project_version": __version__,
            "database_schema_version": int(self.conn.execute("PRAGMA user_version").fetchone()[0]),
            "event_schema_versions": sorted(SUPPORTED_EVENT_SCHEMA_VERSIONS),
            "cube_id": self.meta("cube_id"),
            "head": self.head(),
            "event_count": count("SELECT COUNT(*) FROM events"),
            "change_count": count("SELECT COUNT(*) FROM changesets"),
            "agent_count": count("SELECT COUNT(*) FROM agents WHERE retired_seq IS NULL"),
            "source_count": count("SELECT COUNT(*) FROM sources WHERE retired_seq IS NULL"),
            "claim_count": count("SELECT COUNT(*) FROM claims"),
            "active_claim_relation_count": count(
                "SELECT COUNT(*) FROM claim_relations WHERE ended_seq IS NULL"
            ),
            "active_cardinality_constraint_count": count(
                "SELECT COUNT(*) FROM cardinality_constraints WHERE ended_seq IS NULL"
            ),
            "active_assertion_count": count("SELECT COUNT(*) FROM assertions WHERE ended_seq IS NULL"),
            "anchored_assertion_count": count(
                "SELECT COUNT(*) FROM assertions WHERE ended_seq IS NULL AND standing = 'anchored'"
            ),
            "live_world_count": count("SELECT COUNT(*) FROM worlds WHERE status IN ('live', 'selected')"),
            "particle_update_count": count("SELECT COUNT(*) FROM particle_updates"),
            "particle_reconciliation_count": count(
                "SELECT COUNT(*) FROM particle_reconciliations"
            ),
            "particle_bank": {
                "normalization_status": particle_bank["normalization_status"],
                "effective_sample_size": particle_bank["effective_sample_size"],
                "entropy_nats": particle_bank["entropy_nats"],
                "duplicate_valuation_group_count": particle_bank[
                    "duplicate_valuation_group_count"
                ],
                "applied_factor_count": particle_bank["applied_factor_count"],
                "reweighting_debt_count": particle_bank["reweighting_debt_count"],
            },
            "active_world_assignment_count": count(
                "SELECT COUNT(*) FROM world_assignments WHERE ended_seq IS NULL"
            ),
            "hard_world_assignment_count": count(
                "SELECT COUNT(*) FROM world_assignments WHERE ended_seq IS NULL AND commitment = 'hard'"
            ),
            "world_revision_count": count(
                "SELECT COUNT(*) FROM world_assignments WHERE revision_of_assignment_id IS NOT NULL"
            ),
            "commitment_transition_count": count("SELECT COUNT(*) FROM commitment_transitions"),
            "active_consequence_count": count(
                "SELECT COUNT(*) FROM consequence_links WHERE ended_seq IS NULL"
            ),
            "active_binding_consequence_count": count(
                "SELECT COUNT(*) FROM consequence_links WHERE ended_seq IS NULL AND severity = 'binding'"
            ),
            "consequence_repair_count": count("SELECT COUNT(*) FROM consequence_repairs"),
            "sealed_precommitment_count": count(
                "SELECT COUNT(*) FROM fair_play_seals WHERE revealed_seq IS NULL AND voided_seq IS NULL"
            ),
            "revealed_precommitment_count": count(
                "SELECT COUNT(*) FROM fair_play_seals WHERE revealed_seq IS NOT NULL"
            ),
            "voided_precommitment_count": count(
                "SELECT COUNT(*) FROM fair_play_seals WHERE voided_seq IS NOT NULL"
            ),
            "orphaned_consequence_count": sum(
                1 for item in conflicts if item.get("kind") == "orphaned-consequence"
            ),
            "open_question_count": count("SELECT COUNT(*) FROM questions WHERE status = 'open'"),
            "conflict_count": len(conflicts),
        }

    def changes(self) -> list[dict[str, Any]]:
        rows = self.conn.execute(
            """SELECT cs.*, MIN(e.seq) AS first_seq, MAX(e.seq) AS last_seq
               FROM changesets cs JOIN events e ON e.change_id = cs.change_id
               GROUP BY cs.change_id
               ORDER BY first_seq"""
        ).fetchall()
        return [dict(row) for row in rows]

    def events(self, *, limit: int | None = None, since_seq: int = 0) -> list[dict[str, Any]]:
        sql = "SELECT * FROM events WHERE seq > ? ORDER BY seq"
        params: list[Any] = [since_seq]
        if limit is not None:
            sql += " LIMIT ?"
            params.append(limit)
        rows = self.conn.execute(sql, params).fetchall()
        result: list[dict[str, Any]] = []
        for row in rows:
            item = dict(row)
            item["payload"] = json.loads(item.pop("payload_json"))
            result.append(item)
        return result

    def claims(self) -> list[dict[str, Any]]:
        rows = self.conn.execute("SELECT * FROM claims ORDER BY created_seq, claim_id").fetchall()
        result = []
        for row in rows:
            item = dict(row)
            item["object"] = json.loads(item.pop("object_json"))
            result.append(item)
        return result

    def claim_relations(self, *, include_retired: bool = False) -> list[dict[str, Any]]:
        sql = """SELECT cr.*,
                        lc.subject AS left_subject, lc.predicate AS left_predicate,
                        lc.object_json AS left_object_json, lc.scope AS left_scope,
                        rc.subject AS right_subject, rc.predicate AS right_predicate,
                        rc.object_json AS right_object_json, rc.scope AS right_scope
                 FROM claim_relations cr
                 JOIN claims lc ON lc.claim_id = cr.left_claim_id
                 JOIN claims rc ON rc.claim_id = cr.right_claim_id"""
        if not include_retired:
            sql += " WHERE cr.ended_seq IS NULL"
        sql += " ORDER BY cr.created_seq, cr.relation_id"
        result: list[dict[str, Any]] = []
        for row in self.conn.execute(sql).fetchall():
            item = dict(row)
            item["description"] = RELATION_DESCRIPTIONS[item["relation"]]
            item["left_claim"] = {
                "claim_id": item["left_claim_id"],
                "subject": item.pop("left_subject"),
                "predicate": item.pop("left_predicate"),
                "object": json.loads(item.pop("left_object_json")),
                "scope": item.pop("left_scope"),
            }
            item["right_claim"] = {
                "claim_id": item["right_claim_id"],
                "subject": item.pop("right_subject"),
                "predicate": item.pop("right_predicate"),
                "object": json.loads(item.pop("right_object_json")),
                "scope": item.pop("right_scope"),
            }
            result.append(item)
        return result

    def cardinality_constraints(self, *, include_retired: bool = False) -> list[dict[str, Any]]:
        sql = "SELECT * FROM cardinality_constraints"
        if not include_retired:
            sql += " WHERE ended_seq IS NULL"
        sql += " ORDER BY created_seq, constraint_id"
        constraints = [dict(row) for row in self.conn.execute(sql).fetchall()]
        if not constraints:
            return []
        constraint_ids = [str(item["constraint_id"]) for item in constraints]
        placeholders = ",".join("?" for _ in constraint_ids)
        member_rows = self.conn.execute(
            f"""SELECT cm.constraint_id, cm.ordinal, c.*
                FROM cardinality_members cm
                JOIN claims c ON c.claim_id = cm.claim_id
                WHERE cm.constraint_id IN ({placeholders})
                ORDER BY cm.constraint_id, cm.ordinal""",
            constraint_ids,
        ).fetchall()
        members: dict[str, list[dict[str, Any]]] = {constraint_id: [] for constraint_id in constraint_ids}
        for row in member_rows:
            item = dict(row)
            constraint_id = str(item.pop("constraint_id"))
            item.pop("ordinal")
            item["object"] = json.loads(item.pop("object_json"))
            members[constraint_id].append(item)
        for item in constraints:
            item_members = members[str(item["constraint_id"])]
            item["claim_ids"] = [member["claim_id"] for member in item_members]
            item["members"] = item_members
            item["description"] = cardinality_description(
                int(item["min_true"]), int(item["max_true"]), int(item["member_count"])
            )
        return constraints

    def _event_at_seq(self, seq: int | None) -> dict[str, Any] | None:
        if seq is None:
            return None
        row = self.conn.execute("SELECT * FROM events WHERE seq = ?", (seq,)).fetchone()
        if row is None:
            return None
        item = dict(row)
        item["payload"] = json.loads(item.pop("payload_json"))
        return item

    def _explain_target(self, target_id: str) -> tuple[str, dict[str, Any]]:
        candidates: list[tuple[str, dict[str, Any]]] = []
        table_specs = (
            ("agent", "agents", "agent_id"),
            ("source", "sources", "source_id"),
            ("claim", "claims", "claim_id"),
            ("claim_relation", "claim_relations", "relation_id"),
            ("cardinality_constraint", "cardinality_constraints", "constraint_id"),
            ("assertion", "assertions", "assertion_id"),
            ("world", "worlds", "world_id"),
            ("world_assignment", "world_assignments", "assignment_id"),
            ("commitment_transition", "commitment_transitions", "transition_id"),
            ("evidence_link", "evidence_links", "link_id"),
            ("particle_update", "particle_updates", "update_id"),
            (
                "particle_reconciliation",
                "particle_reconciliations",
                "reconciliation_id",
            ),
            ("consequence_link", "consequence_links", "consequence_id"),
            ("consequence_repair", "consequence_repairs", "repair_id"),
            ("fair_play_seal", "fair_play_seals", "seal_id"),
            ("question", "questions", "question_id"),
            ("event", "events", "event_id"),
            ("change", "changesets", "change_id"),
        )
        for kind, table, field in table_specs:
            row = self.conn.execute(
                f"SELECT * FROM {table} WHERE {field} = ?", (target_id,)
            ).fetchone()
            if row is not None:
                candidates.append((kind, dict(row)))
        if not candidates:
            raise LacunaError("unknown-explain-target", f"no ledger record has id {target_id!r}")
        if len(candidates) > 1:
            raise LacunaError(
                "ambiguous-explain-target",
                f"id {target_id!r} occurs in more than one namespace",
                {"kinds": [kind for kind, _ in candidates]},
            )
        return candidates[0]

    def _normalize_explain_record(self, kind: str, record: dict[str, Any]) -> dict[str, Any]:
        item = dict(record)
        if "metadata_json" in item:
            item["metadata"] = json.loads(item.pop("metadata_json"))
        if "object_json" in item:
            item["object"] = json.loads(item.pop("object_json"))
        if "audience_json" in item:
            item["audience"] = json.loads(item.pop("audience_json"))
        if "payload_json" in item:
            item["payload"] = json.loads(item.pop("payload_json"))
        if "reveal_payload_json" in item:
            raw_reveal_payload = item.pop("reveal_payload_json")
            item["reveal_payload"] = (
                None if raw_reveal_payload is None else json.loads(raw_reveal_payload)
            )
        if kind == "fair_play_seal":
            if item.get("revealed_seq") is not None:
                item["status"] = "revealed"
            elif item.get("voided_seq") is not None:
                item["status"] = "voided"
            else:
                item["status"] = "sealed"
        if kind == "claim_relation":
            item["description"] = RELATION_DESCRIPTIONS.get(item["relation"])
        if kind == "cardinality_constraint":
            member_rows = self.conn.execute(
                """SELECT claim_id FROM cardinality_members
                   WHERE constraint_id = ? ORDER BY ordinal""",
                (item["constraint_id"],),
            ).fetchall()
            item["claim_ids"] = [str(row["claim_id"]) for row in member_rows]
            item["description"] = cardinality_description(
                int(item["min_true"]), int(item["max_true"]), int(item["member_count"])
            )
        if kind == "particle_update":
            item["assessments"] = [
                dict(row)
                for row in self.conn.execute(
                    """SELECT * FROM particle_update_members
                       WHERE update_id = ? ORDER BY ordinal""",
                    (item["update_id"],),
                ).fetchall()
            ]
        if kind == "particle_reconciliation":
            item["boundary"] = self._event_at_seq(item.pop("boundary_seq"))
            factors = [
                dict(row)
                for row in self.conn.execute(
                    """SELECT * FROM particle_reconciliation_factors
                       WHERE reconciliation_id = ? ORDER BY ordinal""",
                    (item["reconciliation_id"],),
                ).fetchall()
            ]
            item["included_factors"] = [
                factor for factor in factors if factor["disposition"] == "included"
            ]
            item["excluded_factors"] = [
                factor for factor in factors if factor["disposition"] == "excluded"
            ]
            item["members"] = [
                dict(row)
                for row in self.conn.execute(
                    """SELECT * FROM particle_reconciliation_members
                       WHERE reconciliation_id = ? ORDER BY ordinal""",
                    (item["reconciliation_id"],),
                ).fetchall()
            ]
        return item

    def _historical_assertions(self) -> list[dict[str, Any]]:
        rows = self.conn.execute(
            """SELECT a.*, c.subject, c.predicate, c.object_json, c.scope
               FROM assertions a JOIN claims c ON c.claim_id = a.claim_id
               ORDER BY a.created_seq, a.assertion_id"""
        ).fetchall()
        result: list[dict[str, Any]] = []
        for row in rows:
            item = dict(row)
            item["audience"] = json.loads(item.pop("audience_json"))
            item["object"] = json.loads(item.pop("object_json"))
            result.append(item)
        return result

    def _historical_questions(self) -> list[dict[str, Any]]:
        result: list[dict[str, Any]] = []
        for row in self.conn.execute(
            "SELECT * FROM questions ORDER BY created_seq, question_id"
        ).fetchall():
            item = dict(row)
            item["audience"] = json.loads(item.pop("audience_json"))
            result.append(item)
        return result

    def _assert_explain_access(
        self,
        kind: str,
        record: dict[str, Any],
        agent_id: str | None,
    ) -> dict[str, Any]:
        if agent_id is None:
            return {"mode": "planner", "privileged": True, "agent_id": None, "visible": True}
        self._require_agent(agent_id, "agent_id")
        privileged_kinds = {
            "claim_relation",
            "cardinality_constraint",
            "world",
            "world_assignment",
            "commitment_transition",
            "evidence_link",
            "particle_update",
            "particle_reconciliation",
            "consequence_link",
            "consequence_repair",
            "event",
            "change",
        }
        if kind in privileged_kinds:
            raise LacunaError(
                "explanation-not-visible",
                f"{kind} custody is privileged planner state",
                {"target_kind": kind, "agent_id": agent_id},
            )
        visible = True
        if kind == "assertion":
            assertion = self._normalize_explain_record(kind, record)
            visible = self.assertion_visible_to(assertion, agent_id)
        elif kind == "question":
            question = self._normalize_explain_record(kind, record)
            visible = self.question_visible_to(question, agent_id)
        elif kind == "fair_play_seal":
            seal = self._normalize_explain_record(kind, record)
            visible = self.seal_visible_to(seal, agent_id)
        elif kind == "claim":
            visible_assertion = any(
                item["claim_id"] == record["claim_id"]
                and self.assertion_visible_to(item, agent_id)
                for item in self._historical_assertions()
            )
            visible_question = any(
                item.get("about_claim_id") == record["claim_id"]
                and self.question_visible_to(item, agent_id)
                for item in self._historical_questions()
            )
            visible = visible_assertion or visible_question
        elif kind == "source":
            visible = any(
                item.get("source_id") == record["source_id"]
                and self.assertion_visible_to(item, agent_id)
                for item in self._historical_assertions()
            )
        if not visible:
            raise LacunaError(
                "explanation-not-visible",
                "the requested record is not visible to this perspective",
                {"target_kind": kind, "agent_id": agent_id},
            )
        return {"mode": "perspective", "privileged": False, "agent_id": agent_id, "visible": True}

    def _explanation_link_visible(
        self,
        kind: str,
        target_id: str,
        agent_id: str | None,
    ) -> bool:
        if agent_id is None:
            return True
        try:
            target_kind, record = self._explain_target(target_id)
            if target_kind != kind:
                return False
            self._assert_explain_access(target_kind, record, agent_id)
            return True
        except LacunaError:
            return False

    def _sanitize_explain_record(
        self,
        kind: str,
        record: dict[str, Any],
        agent_id: str | None,
    ) -> dict[str, Any]:
        item = self._normalize_explain_record(kind, record)
        if agent_id is None:
            return item
        if kind == "agent":
            item.pop("metadata", None)
        elif kind == "source":
            item.pop("metadata", None)
            item.pop("locator", None)
        elif kind == "assertion":
            supersedes_id = item.get("supersedes_id")
            if supersedes_id is not None and not self._explanation_link_visible(
                "assertion", str(supersedes_id), agent_id
            ):
                item["supersedes_id"] = None
        elif kind == "question":
            resolution_id = item.get("resolution_assertion_id")
            if resolution_id is not None and not self._explanation_link_visible(
                "assertion", str(resolution_id), agent_id
            ):
                item["resolution_assertion_id"] = None
        elif kind == "fair_play_seal":
            source_id = item.get("source_id")
            if source_id is not None and not self._explanation_link_visible(
                "source", str(source_id), agent_id
            ):
                item["source_id"] = None
        return item

    @staticmethod
    def _safe_event_envelope(event: dict[str, Any] | None) -> dict[str, Any] | None:
        if event is None:
            return None
        return {
            "seq": event["seq"],
            "event_id": event["event_id"],
            "event_type": event["event_type"],
            "recorded_at": event["recorded_at"],
            "event_hash": event["event_hash"],
        }

    def _explanation_links(
        self,
        kind: str,
        record: dict[str, Any],
        *,
        agent_id: str | None = None,
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        dependencies: list[dict[str, Any]] = []
        dependents: list[dict[str, Any]] = []

        def add_dependency(link_kind: str, target_id: Any, role: str) -> None:
            if target_id is None:
                return
            normalized_id = str(target_id)
            if self._explanation_link_visible(link_kind, normalized_id, agent_id):
                dependencies.append({"kind": link_kind, "id": normalized_id, "role": role})

        def add_dependent(link_kind: str, target_id: Any, role: str) -> None:
            if target_id is None:
                return
            normalized_id = str(target_id)
            if self._explanation_link_visible(link_kind, normalized_id, agent_id):
                dependents.append({"kind": link_kind, "id": normalized_id, "role": role})

        if kind == "claim_relation":
            add_dependency("claim", record["left_claim_id"], "left_endpoint")
            add_dependency("claim", record["right_claim_id"], "right_endpoint")
            add_dependency("source", record.get("source_id"), "declared_from")
        elif kind == "cardinality_constraint":
            for row in self.conn.execute(
                """SELECT claim_id FROM cardinality_members
                   WHERE constraint_id = ? ORDER BY ordinal""",
                (record["constraint_id"],),
            ).fetchall():
                add_dependency("claim", row["claim_id"], "member")
            add_dependency("source", record.get("source_id"), "declared_from")
        elif kind == "assertion":
            add_dependency("claim", record["claim_id"], "asserts")
            add_dependency("agent", record["assertor_id"], "asserted_by")
            add_dependency("agent", record["perspective_id"], "held_by")
            add_dependency("source", record.get("source_id"), "sourced_from")
            add_dependency("assertion", record.get("supersedes_id"), "supersedes")
        elif kind == "world":
            add_dependency("world", record.get("parent_world_id"), "forked_from")
        elif kind == "world_assignment":
            add_dependency("world", record["world_id"], "belongs_to")
            add_dependency("claim", record["claim_id"], "assigns")
            add_dependency("assertion", record.get("source_assertion_id"), "supported_by")
            add_dependency("source", record.get("commitment_source_id"), "commitment_source")
            add_dependency(
                "world_assignment", record.get("inherited_from_assignment_id"), "inherited_from"
            )
            add_dependency(
                "world_assignment", record.get("revision_of_assignment_id"), "revises"
            )
        elif kind == "commitment_transition":
            add_dependency("world_assignment", record["assignment_id"], "raises")
            add_dependency("source", record.get("source_id"), "commitment_source")
        elif kind == "evidence_link":
            add_dependency("assertion", record["evidence_assertion_id"], "evidence")
            add_dependency("claim", record["target_claim_id"], "target")
            add_dependency("world", record.get("world_id"), "scoped_to")
        elif kind == "particle_update":
            add_dependency(
                "assertion", record["evidence_assertion_id"], "evidence_update"
            )
            for row in self.conn.execute(
                """SELECT world_id FROM particle_update_members
                   WHERE update_id = ? ORDER BY ordinal""",
                (record["update_id"],),
            ).fetchall():
                add_dependency("world", row["world_id"], "assessed_particle")
        elif kind == "particle_reconciliation":
            add_dependency(
                "particle_update", record["baseline_update_id"], "baseline_factor"
            )
            for row in self.conn.execute(
                """SELECT update_id, disposition
                     FROM particle_reconciliation_factors
                    WHERE reconciliation_id = ? ORDER BY ordinal""",
                (record["reconciliation_id"],),
            ).fetchall():
                add_dependency(
                    "particle_update",
                    row["update_id"],
                    f"{row['disposition']}_factor",
                )
            for row in self.conn.execute(
                """SELECT world_id FROM particle_reconciliation_members
                   WHERE reconciliation_id = ? ORDER BY ordinal""",
                (record["reconciliation_id"],),
            ).fetchall():
                add_dependency("world", row["world_id"], "reconciled_particle")
        elif kind == "consequence_link":
            add_dependency(
                "world_assignment", record["premise_assignment_id"], "premise"
            )
            add_dependency(
                str(record["dependent_kind"]), record["dependent_id"], "dependent"
            )
            add_dependency("source", record.get("source_id"), "declared_from")
            repaired_from = self.conn.execute(
                """SELECT repair_id FROM consequence_repairs
                   WHERE successor_consequence_id = ?""",
                (record["consequence_id"],),
            ).fetchone()
            if repaired_from is not None:
                add_dependency(
                    "consequence_repair", repaired_from["repair_id"], "created_by_repair"
                )
        elif kind == "consequence_repair":
            add_dependency(
                "consequence_link",
                record["predecessor_consequence_id"],
                "predecessor",
            )
            add_dependency(
                "consequence_link",
                record["successor_consequence_id"],
                "successor",
            )
        elif kind == "fair_play_seal":
            add_dependency("source", record.get("source_id"), "declared_from")
        elif kind == "question":
            add_dependency("claim", record.get("about_claim_id"), "about")
            add_dependency("agent", record["opened_by"], "opened_by")
            add_dependency("assertion", record.get("resolution_assertion_id"), "resolved_by")
        elif kind == "event":
            add_dependency("change", record["change_id"], "member_of")
            add_dependency("agent", record["actor_id"], "recorded_by")

        if kind == "claim":
            claim_id = record["claim_id"]
            queries = (
                ("assertion", "assertions", "assertion_id", "claim_id", "asserted_as"),
                ("world_assignment", "world_assignments", "assignment_id", "claim_id", "assigned_in"),
                ("evidence_link", "evidence_links", "link_id", "target_claim_id", "evidence_target"),
                ("question", "questions", "question_id", "about_claim_id", "questioned_by"),
            )
            for link_kind, table, id_field, match_field, role in queries:
                for row in self.conn.execute(
                    f"SELECT {id_field} FROM {table} WHERE {match_field} = ? ORDER BY {id_field}",
                    (claim_id,),
                ).fetchall():
                    add_dependent(link_kind, row[id_field], role)
            for row in self.conn.execute(
                """SELECT relation_id FROM claim_relations
                   WHERE left_claim_id = ? OR right_claim_id = ? ORDER BY relation_id""",
                (claim_id, claim_id),
            ).fetchall():
                add_dependent("claim_relation", row["relation_id"], "constrained_by")
            for row in self.conn.execute(
                """SELECT constraint_id FROM cardinality_members
                   WHERE claim_id = ? ORDER BY constraint_id""",
                (claim_id,),
            ).fetchall():
                add_dependent(
                    "cardinality_constraint", row["constraint_id"], "cardinality_constrained_by"
                )
        elif kind == "assertion":
            assertion_id = record["assertion_id"]
            for row in self.conn.execute(
                "SELECT link_id FROM evidence_links WHERE evidence_assertion_id = ? ORDER BY link_id",
                (assertion_id,),
            ).fetchall():
                add_dependent("evidence_link", row["link_id"], "used_as_evidence")
            for row in self.conn.execute(
                "SELECT assertion_id FROM assertions WHERE supersedes_id = ? ORDER BY assertion_id",
                (assertion_id,),
            ).fetchall():
                add_dependent("assertion", row["assertion_id"], "superseded_by")
            for row in self.conn.execute(
                "SELECT update_id FROM particle_updates WHERE evidence_assertion_id = ? ORDER BY update_id",
                (assertion_id,),
            ).fetchall():
                add_dependent("particle_update", row["update_id"], "used_to_reweight")
            for row in self.conn.execute(
                "SELECT assignment_id FROM world_assignments WHERE source_assertion_id = ? ORDER BY assignment_id",
                (assertion_id,),
            ).fetchall():
                add_dependent("world_assignment", row["assignment_id"], "supports_assignment")
            for row in self.conn.execute(
                """SELECT consequence_id FROM consequence_links
                   WHERE dependent_kind = 'assertion' AND dependent_id = ?
                   ORDER BY consequence_id""",
                (assertion_id,),
            ).fetchall():
                add_dependent("consequence_link", row["consequence_id"], "explicit_consequence")
        elif kind == "particle_update":
            for row in self.conn.execute(
                """SELECT reconciliation_id, disposition
                     FROM particle_reconciliation_factors
                    WHERE update_id = ? ORDER BY reconciliation_id""",
                (record["update_id"],),
            ).fetchall():
                add_dependent(
                    "particle_reconciliation",
                    row["reconciliation_id"],
                    f"{row['disposition']}_by_reconciliation",
                )
        elif kind == "question":
            for row in self.conn.execute(
                """SELECT consequence_id FROM consequence_links
                   WHERE dependent_kind = 'question' AND dependent_id = ?
                   ORDER BY consequence_id""",
                (record["question_id"],),
            ).fetchall():
                add_dependent("consequence_link", row["consequence_id"], "explicit_consequence")
        elif kind == "source":
            source_id = record["source_id"]
            queries = (
                ("assertion", "assertions", "assertion_id", "sourced_assertion"),
                ("claim_relation", "claim_relations", "relation_id", "sourced_relation"),
                (
                    "cardinality_constraint",
                    "cardinality_constraints",
                    "constraint_id",
                    "sourced_cardinality",
                ),
                (
                    "commitment_transition",
                    "commitment_transitions",
                    "transition_id",
                    "sourced_commitment_transition",
                ),
                ("consequence_link", "consequence_links", "consequence_id", "sourced_consequence"),
                ("fair_play_seal", "fair_play_seals", "seal_id", "sourced_seal"),
            )
            for link_kind, table, id_field, role in queries:
                for row in self.conn.execute(
                    f"SELECT {id_field} FROM {table} WHERE source_id = ? ORDER BY {id_field}",
                    (source_id,),
                ).fetchall():
                    add_dependent(link_kind, row[id_field], role)
            for row in self.conn.execute(
                """SELECT assignment_id FROM world_assignments
                   WHERE commitment_source_id = ? ORDER BY assignment_id""",
                (source_id,),
            ).fetchall():
                add_dependent("world_assignment", row["assignment_id"], "commitment_source")
        elif kind == "world":
            world_id = record["world_id"]
            for row in self.conn.execute(
                "SELECT assignment_id FROM world_assignments WHERE world_id = ? ORDER BY assignment_id",
                (world_id,),
            ).fetchall():
                add_dependent("world_assignment", row["assignment_id"], "contains")
            for row in self.conn.execute(
                """SELECT update_id FROM particle_update_members
                   WHERE world_id = ? ORDER BY update_id""",
                (world_id,),
            ).fetchall():
                add_dependent("particle_update", row["update_id"], "assessed_by")
            for row in self.conn.execute(
                """SELECT reconciliation_id FROM particle_reconciliation_members
                   WHERE world_id = ? ORDER BY reconciliation_id""",
                (world_id,),
            ).fetchall():
                add_dependent(
                    "particle_reconciliation",
                    row["reconciliation_id"],
                    "reconciled_by",
                )
            for row in self.conn.execute(
                "SELECT world_id FROM worlds WHERE parent_world_id = ? ORDER BY world_id",
                (world_id,),
            ).fetchall():
                add_dependent("world", row["world_id"], "parent_of")
        elif kind == "world_assignment":
            assignment_id = record["assignment_id"]
            for row in self.conn.execute(
                """SELECT assignment_id FROM world_assignments
                   WHERE revision_of_assignment_id = ? ORDER BY assignment_id""",
                (assignment_id,),
            ).fetchall():
                add_dependent("world_assignment", row["assignment_id"], "revised_by")
            for row in self.conn.execute(
                """SELECT assignment_id FROM world_assignments
                   WHERE inherited_from_assignment_id = ? ORDER BY assignment_id""",
                (assignment_id,),
            ).fetchall():
                add_dependent("world_assignment", row["assignment_id"], "inherited_by")
            for row in self.conn.execute(
                """SELECT transition_id FROM commitment_transitions
                   WHERE assignment_id = ? ORDER BY created_seq, transition_id""",
                (assignment_id,),
            ).fetchall():
                add_dependent("commitment_transition", row["transition_id"], "commitment_history")
            for row in self.conn.execute(
                """SELECT consequence_id FROM consequence_links
                   WHERE premise_assignment_id = ? OR
                         (dependent_kind = 'world_assignment' AND dependent_id = ?)
                   ORDER BY consequence_id""",
                (assignment_id, assignment_id),
            ).fetchall():
                add_dependent("consequence_link", row["consequence_id"], "explicit_consequence")
        elif kind == "consequence_link":
            for row in self.conn.execute(
                """SELECT repair_id FROM consequence_repairs
                   WHERE predecessor_consequence_id = ? ORDER BY repair_id""",
                (record["consequence_id"],),
            ).fetchall():
                add_dependent("consequence_repair", row["repair_id"], "replaced_by")
        return dependencies[:250], dependents[:250]

    def explain(self, target_id: str, *, agent_id: str | None = None) -> dict[str, Any]:
        """Return recorded custody and visible dependency links, never proof of truth."""
        target_id = require_id(target_id, "target_id")
        kind, raw = self._explain_target(target_id)
        access = self._assert_explain_access(kind, raw, agent_id)
        record = self._sanitize_explain_record(kind, raw, agent_id)
        created_seq: int | None
        ended_seq: int | None
        if kind == "event":
            created_seq = int(raw["seq"])
            ended_seq = None
        elif kind == "change":
            seq_row = self.conn.execute(
                "SELECT MIN(seq) AS first_seq, MAX(seq) AS last_seq FROM events WHERE change_id = ?",
                (raw["change_id"],),
            ).fetchone()
            created_seq = int(seq_row["first_seq"]) if seq_row["first_seq"] is not None else None
            ended_seq = int(seq_row["last_seq"]) if seq_row["last_seq"] is not None else None
        else:
            created_seq = int(raw["created_seq"]) if raw.get("created_seq") is not None else None
            if kind == "fair_play_seal":
                end_value = raw.get("revealed_seq") or raw.get("voided_seq")
            else:
                end_value = raw.get("ended_seq", raw.get("closed_seq", raw.get("retired_seq")))
            ended_seq = int(end_value) if end_value is not None else None
        dependencies, dependents = self._explanation_links(kind, raw, agent_id=agent_id)
        created_event = self._event_at_seq(created_seq)
        ended_event = self._event_at_seq(ended_seq) if ended_seq != created_seq else None
        if agent_id is not None:
            created_event = self._safe_event_envelope(created_event)
            ended_event = self._safe_event_envelope(ended_event)
        return {
            "event": "lacuna.explanation",
            "schema": "lacuna.explanation.v1",
            "cube_id": self.meta("cube_id"),
            "head": self.head(),
            "access": access,
            "link_scope": "visible-only" if agent_id is not None else "planner-full",
            "target": {"id": target_id, "kind": kind, "record": record},
            "custody": {
                "created_by_event": created_event,
                "ended_by_event": ended_event,
                "active": ended_seq is None,
            },
            "dependencies": dependencies,
            "dependents": dependents,
            "nonclaim": (
                "This is a trace of recorded origin, visibility, and structural dependence. "
                "It is not a logical proof that the target is true, fair, or narratively justified."
            ),
        }

    @staticmethod
    def assertion_visible_to(assertion: dict[str, Any], agent_id: str) -> bool:
        audience = assertion.get("audience", [])
        return bool(
            assertion.get("visibility") == "public"
            or assertion.get("perspective_id") == agent_id
            or assertion.get("assertor_id") == agent_id
            or (assertion.get("visibility") == "restricted" and agent_id in audience)
        )

    @staticmethod
    def question_visible_to(question: dict[str, Any], agent_id: str) -> bool:
        audience = question.get("audience", [])
        return bool(
            question.get("visibility") == "public"
            or question.get("opened_by") == agent_id
            or (question.get("visibility") == "restricted" and agent_id in audience)
        )

    def assertion(self, assertion_id: str, *, active: bool = False) -> dict[str, Any]:
        self._require_assertion(assertion_id, active=active)
        sql = """SELECT a.*, c.subject, c.predicate, c.object_json, c.scope
                 FROM assertions a JOIN claims c ON c.claim_id = a.claim_id
                 WHERE a.assertion_id = ?"""
        if active:
            sql += " AND a.ended_seq IS NULL"
        row = self.conn.execute(sql, (assertion_id,)).fetchone()
        if row is None:
            raise LacunaError("unknown-assertion", f"unknown assertion {assertion_id!r}")
        item = dict(row)
        item["audience"] = json.loads(item.pop("audience_json"))
        item["object"] = json.loads(item.pop("object_json"))
        return item

    def active_assertions(self) -> list[dict[str, Any]]:
        rows = self.conn.execute(
            """SELECT a.*, c.subject, c.predicate, c.object_json, c.scope
               FROM assertions a JOIN claims c ON c.claim_id = a.claim_id
               WHERE a.ended_seq IS NULL ORDER BY a.created_seq, a.assertion_id"""
        ).fetchall()
        result = []
        for row in rows:
            item = dict(row)
            item["audience"] = json.loads(item.pop("audience_json"))
            item["object"] = json.loads(item.pop("object_json"))
            result.append(item)
        return result

    def worlds(self) -> list[dict[str, Any]]:
        rows = self.conn.execute("SELECT * FROM worlds ORDER BY status, weight DESC, created_seq").fetchall()
        worlds: list[dict[str, Any]] = []
        for row in rows:
            item = dict(row)
            item["assignments"] = self.world_assignments(item["world_id"])
            worlds.append(item)
        return worlds

    def world_assignments(self, world_id: str) -> list[dict[str, Any]]:
        self._require_world(world_id)
        rows = self.conn.execute(
            """SELECT wa.*, c.subject, c.predicate, c.object_json, c.scope
               FROM world_assignments wa JOIN claims c ON c.claim_id = wa.claim_id
               WHERE wa.world_id = ? AND wa.ended_seq IS NULL
               ORDER BY wa.created_seq, wa.assignment_id""",
            (world_id,),
        ).fetchall()
        result = []
        for row in rows:
            item = dict(row)
            item["object"] = json.loads(item.pop("object_json"))
            result.append(item)
        return result

    def assignment_history(
        self,
        *,
        world_id: str | None = None,
        claim_id: str | None = None,
    ) -> list[dict[str, Any]]:
        """Return active and ended assignments with revision and inheritance custody."""
        clauses: list[str] = []
        params: list[Any] = []
        if world_id is not None:
            self._require_world(world_id)
            clauses.append("wa.world_id = ?")
            params.append(world_id)
        if claim_id is not None:
            self._require_claim(claim_id)
            clauses.append("wa.claim_id = ?")
            params.append(claim_id)
        sql = """SELECT wa.*, c.subject, c.predicate, c.object_json, c.scope
                 FROM world_assignments wa JOIN claims c ON c.claim_id = wa.claim_id"""
        if clauses:
            sql += " WHERE " + " AND ".join(clauses)
        sql += " ORDER BY wa.created_seq, wa.assignment_id"
        result: list[dict[str, Any]] = []
        for row in self.conn.execute(sql, params).fetchall():
            item = dict(row)
            item["object"] = json.loads(item.pop("object_json"))
            item["active"] = item["ended_seq"] is None
            result.append(item)
        return result

    def commitment_transitions(
        self,
        *,
        assignment_id: str | None = None,
    ) -> list[dict[str, Any]]:
        if assignment_id is not None:
            self._require_world_assignment(assignment_id)
        sql = "SELECT * FROM commitment_transitions"
        params: list[Any] = []
        if assignment_id is not None:
            sql += " WHERE assignment_id = ?"
            params.append(assignment_id)
        sql += " ORDER BY created_seq, transition_id"
        return [dict(row) for row in self.conn.execute(sql, params).fetchall()]

    def consequence_links(
        self,
        *,
        include_retired: bool = False,
        premise_assignment_id: str | None = None,
    ) -> list[dict[str, Any]]:
        """Return consequence custody with premise/dependent lifecycle diagnostics."""
        if premise_assignment_id is not None:
            self._require_world_assignment(premise_assignment_id)
        clauses: list[str] = []
        params: list[Any] = []
        if not include_retired:
            clauses.append("cl.ended_seq IS NULL")
        if premise_assignment_id is not None:
            clauses.append("cl.premise_assignment_id = ?")
            params.append(premise_assignment_id)
        sql = """SELECT cl.*, wa.world_id AS premise_world_id,
                        wa.claim_id AS premise_claim_id,
                        wa.ended_seq AS premise_ended_seq,
                        outgoing.repair_id AS replacement_repair_id,
                        outgoing.successor_consequence_id AS replacement_consequence_id,
                        incoming.repair_id AS originating_repair_id,
                        incoming.predecessor_consequence_id AS replaces_consequence_id
                 FROM consequence_links cl
                 JOIN world_assignments wa
                   ON wa.assignment_id = cl.premise_assignment_id
                 LEFT JOIN consequence_repairs outgoing
                   ON outgoing.predecessor_consequence_id = cl.consequence_id
                 LEFT JOIN consequence_repairs incoming
                   ON incoming.successor_consequence_id = cl.consequence_id"""
        if clauses:
            sql += " WHERE " + " AND ".join(clauses)
        sql += " ORDER BY cl.created_seq, cl.consequence_id"
        result: list[dict[str, Any]] = []
        for row in self.conn.execute(sql, params).fetchall():
            item = dict(row)
            dependent = self._consequence_dependent_state(
                str(item["dependent_kind"]), str(item["dependent_id"])
            )
            item["premise_active"] = item.pop("premise_ended_seq") is None
            item["dependent_state"] = dependent["state"]
            item["dependent_active"] = dependent["active"]
            item["dependent_claim_id"] = dependent.get("claim_id")
            if dependent.get("world_id") is not None:
                item["dependent_world_id"] = dependent["world_id"]
            item["repair_required"] = bool(
                item["ended_seq"] is None
                and (not item["premise_active"] or not item["dependent_active"])
            )
            has_predecessor = item["replaces_consequence_id"] is not None
            has_successor = item["replacement_consequence_id"] is not None
            if has_predecessor and has_successor:
                item["lineage_state"] = "middle"
            elif has_successor:
                item["lineage_state"] = "replaced"
            elif has_predecessor:
                item["lineage_state"] = "replacement"
            elif item["ended_seq"] is not None:
                item["lineage_state"] = "retired"
            else:
                item["lineage_state"] = "original"
            result.append(item)
        return result

    def consequence_repairs(self) -> list[dict[str, Any]]:
        """Return immutable predecessor/successor custody for consequence replacement."""
        rows = self.conn.execute(
            """SELECT cr.*,
                      origin.event_id AS origin_event_id,
                      origin.change_id AS change_id,
                      receipt.before_head AS review_head,
                      predecessor.premise_assignment_id AS predecessor_premise_assignment_id,
                      predecessor.dependent_kind AS predecessor_dependent_kind,
                      predecessor.dependent_id AS predecessor_dependent_id,
                      successor.premise_assignment_id AS successor_premise_assignment_id,
                      successor.dependent_kind AS successor_dependent_kind,
                      successor.dependent_id AS successor_dependent_id
               FROM consequence_repairs cr
               JOIN events origin ON origin.seq = cr.created_seq
               JOIN changesets receipt ON receipt.change_id = origin.change_id
               JOIN consequence_links predecessor
                 ON predecessor.consequence_id = cr.predecessor_consequence_id
               JOIN consequence_links successor
                 ON successor.consequence_id = cr.successor_consequence_id
               ORDER BY cr.created_seq, cr.repair_id"""
        ).fetchall()
        return [dict(row) for row in rows]

    def consequence_repair_frontier(
        self,
        *,
        world_id: str | None = None,
    ) -> list[dict[str, Any]]:
        """Return current review receipts for active consequence repair debt.

        This is the shared human/model entrance used by planner context and the
        CLI.  It intentionally excludes semantic replacements of healthy links:
        the frontier is debt, not a suggestion to rewrite every active edge.
        """
        if world_id is not None:
            self._require_world(world_id)
        links = [
            item
            for item in self.consequence_links()
            if item["repair_required"]
            and (
                world_id is None
                or item.get("premise_world_id") == world_id
                or item.get("dependent_world_id") == world_id
            )
        ]
        return [
            self.consequence_repair_review(str(item["consequence_id"]))
            for item in links
        ]

    def particle_bank(self) -> dict[str, Any]:
        """Return the current normalized planning distribution and factor custody.

        The bank projection distinguishes historical factors from factors that still
        belong to the current structural epoch. Superseded evidence creates repair
        debt only while its factor is still in that epoch and has not been explicitly
        excluded by a later reconciliation.
        """
        bank = build_particle_bank(self._particle_world_rows())
        epoch = self._particle_factor_epoch()
        boundary = epoch["boundary"]
        boundary_seq = 0 if boundary is None else int(boundary["seq"])
        factor_rows = self.conn.execute(
            """SELECT pu.update_id, pu.evidence_assertion_id, pu.created_seq,
                      a.ended_seq AS evidence_ended_seq
                 FROM particle_updates pu
                 JOIN assertions a ON a.assertion_id = pu.evidence_assertion_id
                ORDER BY pu.created_seq, pu.update_id"""
        ).fetchall()
        applied_factors: list[dict[str, Any]] = []
        reweighting_debt: list[dict[str, Any]] = []
        for row in factor_rows:
            created_seq = int(row["created_seq"])
            evidence_ended_seq = (
                None if row["evidence_ended_seq"] is None else int(row["evidence_ended_seq"])
            )
            evidence_status = "active" if evidence_ended_seq is None else "superseded"
            resolution = None
            ledger_status: str
            if created_seq <= boundary_seq:
                ledger_status = "epoch-retired"
                if boundary is not None:
                    resolution = {
                        "kind": "structural-boundary",
                        "event_id": boundary["event_id"],
                        "event_type": boundary["event_type"],
                        "seq": boundary_seq,
                    }
            elif evidence_status == "active":
                ledger_status = "active-in-current-epoch"
            else:
                resolved_row = self.conn.execute(
                    """SELECT pr.reconciliation_id, pr.created_seq
                         FROM particle_reconciliation_factors prf
                         JOIN particle_reconciliations pr
                           ON pr.reconciliation_id = prf.reconciliation_id
                        WHERE prf.update_id = ?
                          AND prf.disposition = 'excluded'
                          AND pr.created_seq >= ?
                        ORDER BY pr.created_seq DESC, pr.reconciliation_id DESC
                        LIMIT 1""",
                    (row["update_id"], evidence_ended_seq),
                ).fetchone()
                if resolved_row is None:
                    ledger_status = "reconciliation-required"
                else:
                    ledger_status = "reconciled-excluded"
                    resolution = {
                        "kind": "particle-reconciliation",
                        "reconciliation_id": str(resolved_row["reconciliation_id"]),
                        "seq": int(resolved_row["created_seq"]),
                    }
            item = {
                "update_id": str(row["update_id"]),
                "evidence_assertion_id": str(row["evidence_assertion_id"]),
                "created_seq": created_seq,
                "evidence_status": evidence_status,
                "evidence_ended_seq": evidence_ended_seq,
                "ledger_status": ledger_status,
                "resolution": resolution,
            }
            applied_factors.append(item)
            if ledger_status == "reconciliation-required":
                reweighting_debt.append(item)

        latest_reconciliation = self.conn.execute(
            """SELECT reconciliation_id, factor_set_sha256, posterior_bank_sha256,
                      created_seq
                 FROM particle_reconciliations
                ORDER BY created_seq DESC, reconciliation_id DESC LIMIT 1"""
        ).fetchone()
        return {
            "event": "lacuna.particle-bank",
            "cube_id": self.meta("cube_id"),
            "head": self.head(),
            **bank,
            "factor_epoch_boundary": boundary,
            "applied_factor_count": len(applied_factors),
            "applied_factors": applied_factors,
            "reweighting_debt_count": len(reweighting_debt),
            "reweighting_debt": reweighting_debt,
            "particle_reconciliation_count": int(
                self.conn.execute("SELECT COUNT(*) FROM particle_reconciliations").fetchone()[0]
            ),
            "latest_reconciliation": (
                None if latest_reconciliation is None else dict(latest_reconciliation)
            ),
        }

    def particle_reconciliation_review(self) -> dict[str, Any]:
        """Issue a head-bound review for deterministic factor-ledger replay."""
        return self._build_particle_reconciliation_review(head=self.head())

    def particle_reconciliations(
        self,
        *,
        reconciliation_id: str | None = None,
    ) -> list[dict[str, Any]]:
        """Return immutable reconciliation custody, factors, and per-world replay."""
        sql = """SELECT pr.*, e.event_id AS origin_event_id, e.change_id,
                        cs.before_head AS review_head, cs.after_head AS committed_head
                   FROM particle_reconciliations pr
                   JOIN events e ON e.seq = pr.created_seq
                   JOIN changesets cs ON cs.change_id = e.change_id"""
        params: list[Any] = []
        if reconciliation_id is not None:
            reconciliation_id = require_id(reconciliation_id, "reconciliation_id")
            sql += " WHERE pr.reconciliation_id = ?"
            params.append(reconciliation_id)
        sql += " ORDER BY pr.created_seq, pr.reconciliation_id"
        result: list[dict[str, Any]] = []
        for row in self.conn.execute(sql, params).fetchall():
            item = dict(row)
            item["boundary"] = self._event_at_seq(item.pop("boundary_seq"))
            factors = [
                dict(factor)
                for factor in self.conn.execute(
                    """SELECT * FROM particle_reconciliation_factors
                         WHERE reconciliation_id = ? ORDER BY ordinal""",
                    (item["reconciliation_id"],),
                ).fetchall()
            ]
            item["included_factors"] = [
                factor for factor in factors if factor["disposition"] == "included"
            ]
            item["excluded_factors"] = [
                factor for factor in factors if factor["disposition"] == "excluded"
            ]
            item["members"] = [
                dict(member)
                for member in self.conn.execute(
                    """SELECT * FROM particle_reconciliation_members
                         WHERE reconciliation_id = ? ORDER BY ordinal""",
                    (item["reconciliation_id"],),
                ).fetchall()
            ]
            item["nonclaim"] = (
                "Factor reconciliation repairs arithmetic and factor custody only; "
                "it does not certify likelihood calibration, independence, causation, or truth."
            )
            result.append(item)
        return result

    def particle_update_review(self, evidence_assertion_id: str) -> dict[str, Any]:
        """Issue the complete bank receipt needed to authorize evidence reweighting."""
        evidence = self._require_unused_particle_evidence(evidence_assertion_id)
        claim_row = self.conn.execute(
            "SELECT * FROM claims WHERE claim_id = ?", (evidence["claim_id"],)
        ).fetchone()
        assert claim_row is not None
        claim = dict(claim_row)
        bank = self.particle_bank()
        return {
            "event": "lacuna.particle-update-review",
            "schema": "lacuna.particle-update-review.v1",
            "cube_id": self.meta("cube_id"),
            "head": self.head(),
            "evidence": {
                "assertion_id": evidence_assertion_id,
                "claim_id": evidence["claim_id"],
                "subject": claim["subject"],
                "predicate": claim["predicate"],
                "object": json.loads(claim["object_json"]),
                "scope": claim["scope"],
                "stance": evidence["stance"],
                "basis": evidence["basis"],
                "standing": evidence["standing"],
                "source_id": evidence["source_id"],
            },
            "expected_bank_sha256": bank["bank_sha256"],
            "particle_bank": bank,
            "required_assessment_world_ids": [
                item["world_id"] for item in bank["particles"]
            ],
            "rule": (
                "Assess every live or selected world exactly once. Applying the update "
                "changes weights only; it does not select, prune, or canonize a world."
            ),
        }

    def particle_updates(self, *, update_id: str | None = None) -> list[dict[str, Any]]:
        """Return immutable evidence-update custody and per-world calculations."""
        sql = """SELECT pu.*, e.event_id AS origin_event_id, e.change_id,
                        cs.before_head AS review_head, cs.after_head AS committed_head,
                        a.claim_id AS evidence_claim_id, a.stance AS evidence_stance,
                        a.basis AS evidence_basis, a.standing AS evidence_standing,
                        a.ended_seq AS evidence_ended_seq,
                        c.subject AS evidence_subject, c.predicate AS evidence_predicate,
                        c.object_json AS evidence_object_json, c.scope AS evidence_scope
                 FROM particle_updates pu
                 JOIN events e ON e.seq = pu.created_seq
                 JOIN changesets cs ON cs.change_id = e.change_id
                 JOIN assertions a ON a.assertion_id = pu.evidence_assertion_id
                 JOIN claims c ON c.claim_id = a.claim_id"""
        params: list[Any] = []
        if update_id is not None:
            update_id = require_id(update_id, "update_id")
            sql += " WHERE pu.update_id = ?"
            params.append(update_id)
        sql += " ORDER BY pu.created_seq, pu.update_id"
        updates: list[dict[str, Any]] = []
        for row in self.conn.execute(sql, params).fetchall():
            item = dict(row)
            item["evidence_object"] = json.loads(item.pop("evidence_object_json"))
            item["evidence_status"] = (
                "active" if item["evidence_ended_seq"] is None else "superseded"
            )
            member_rows = self.conn.execute(
                """SELECT * FROM particle_update_members
                   WHERE update_id = ? ORDER BY ordinal""",
                (item["update_id"],),
            ).fetchall()
            item["assessments"] = [dict(member) for member in member_rows]
            item["zero_likelihood_world_count"] = sum(
                1 for member in item["assessments"] if member["likelihood"] == 0.0
            )
            item["valuation_likelihood_divergence_groups"] = (
                valuation_likelihood_divergence_groups(item["assessments"])
            )
            item["nonclaim"] = (
                "Likelihoods and resulting weights are authored planning quantities; "
                "this receipt does not certify statistical calibration or world truth."
            )
            updates.append(item)
        return updates

    def evidence_links(self, *, world_id: str | None = None) -> list[dict[str, Any]]:
        if world_id is not None:
            self._require_world(world_id)
        sql = """SELECT el.*,
                        ea.claim_id AS evidence_claim_id, ea.assertor_id, ea.perspective_id,
                        ea.source_id, ea.stance AS evidence_stance, ea.basis AS evidence_basis,
                        ea.standing AS evidence_standing,
                        ec.subject AS evidence_subject, ec.predicate AS evidence_predicate,
                        ec.object_json AS evidence_object_json, ec.scope AS evidence_scope,
                        tc.subject AS target_subject, tc.predicate AS target_predicate,
                        tc.object_json AS target_object_json, tc.scope AS target_scope
                 FROM evidence_links el
                 JOIN assertions ea ON ea.assertion_id = el.evidence_assertion_id
                 JOIN claims ec ON ec.claim_id = ea.claim_id
                 JOIN claims tc ON tc.claim_id = el.target_claim_id
                 WHERE el.ended_seq IS NULL"""
        params: list[Any] = []
        if world_id is not None:
            sql += " AND (el.world_id IS NULL OR el.world_id = ?)"
            params.append(world_id)
        sql += " ORDER BY el.created_seq, el.link_id"
        result: list[dict[str, Any]] = []
        for row in self.conn.execute(sql, params).fetchall():
            item = dict(row)
            item["evidence_object"] = json.loads(item.pop("evidence_object_json"))
            item["target_object"] = json.loads(item.pop("target_object_json"))
            result.append(item)
        return result

    def perspective(self, agent_id: str) -> dict[str, Any]:
        self._require_agent(agent_id, "agent_id")
        visible = [
            assertion
            for assertion in self.active_assertions()
            if self.assertion_visible_to(assertion, agent_id)
        ]
        questions = []
        rows = self.conn.execute("SELECT * FROM questions WHERE status = 'open' ORDER BY created_seq").fetchall()
        for row in rows:
            item = dict(row)
            item["audience"] = json.loads(item.pop("audience_json"))
            if self.question_visible_to(item, agent_id):
                questions.append(item)
        return {
            "event": "lacuna.perspective",
            "schema": "lacuna.perspective.v1",
            "cube_id": self.meta("cube_id"),
            "head": self.head(),
            "agent_id": agent_id,
            "assertions": visible,
            "open_questions": questions,
            "fair_play_seals": self.seals(agent_id=agent_id),
            "rule": "public records plus records held, asserted, or explicitly shared with this agent",
        }

    def canon(self) -> dict[str, Any]:
        anchors = [a for a in self.active_assertions() if a["standing"] == "anchored"]
        live_worlds = [w for w in self.worlds() if w["status"] in {"live", "selected"}]
        consensus: list[dict[str, Any]] = []
        if live_worlds:
            by_world: dict[str, dict[tuple[Any, ...], dict[str, Any]]] = {}
            for world in live_worlds:
                mapping: dict[tuple[Any, ...], dict[str, Any]] = {}
                for assignment in world["assignments"]:
                    key = (
                        assignment["claim_id"],
                        assignment["timeline_id"],
                        assignment["valid_from"],
                        assignment["valid_to"],
                    )
                    mapping[key] = assignment
                by_world[world["world_id"]] = mapping
            common_keys = set.intersection(*(set(mapping) for mapping in by_world.values())) if by_world else set()
            for key in sorted(common_keys, key=str):
                assignments = [by_world[w["world_id"]][key] for w in live_worlds]
                truths = {a["truth"] for a in assignments}
                if len(truths) == 1 and "unknown" not in truths:
                    sample = dict(assignments[0])
                    sample["world_count"] = len(live_worlds)
                    sample["world_ids"] = [w["world_id"] for w in live_worlds]
                    sample["minimum_commitment"] = min(
                        (a["commitment"] for a in assignments),
                        key=lambda value: ["tentative", "soft", "firm", "hard"].index(value),
                    )
                    consensus.append(sample)
        return {
            "event": "lacuna.canon",
            "schema": "lacuna.canon.v1",
            "cube_id": self.meta("cube_id"),
            "head": self.head(),
            "anchors": anchors,
            "cross_world_consensus": consensus,
            "live_world_count": len(live_worlds),
            "nonclaim": "consensus is shared current assignment across live worlds; it does not convert reports, beliefs, or absent records into truth",
        }

    def unknowns(self) -> dict[str, Any]:
        canon = self.canon()
        settled_claims = {a["claim_id"] for a in canon["anchors"]}
        settled_claims.update(a["claim_id"] for a in canon["cross_world_consensus"])
        unknown_claims = [claim for claim in self.claims() if claim["claim_id"] not in settled_claims]
        rows = self.conn.execute("SELECT * FROM questions WHERE status = 'open' ORDER BY created_seq").fetchall()
        questions = []
        for row in rows:
            item = dict(row)
            item["audience"] = json.loads(item.pop("audience_json"))
            questions.append(item)
        return {
            "event": "lacuna.unknowns",
            "schema": "lacuna.unknowns.v1",
            "cube_id": self.meta("cube_id"),
            "head": self.head(),
            "unsettled_claims": unknown_claims,
            "open_questions": questions,
            "rule": "absence of settlement remains unknown, never false",
        }

    def conflicts(self) -> list[dict[str, Any]]:
        relations = self._active_relation_rows()
        cardinalities = self._active_cardinality_rows()
        assertions = [
            item for item in self.active_assertions() if item["stance"] in {"true", "false"}
        ]
        conflicts: list[dict[str, Any]] = []

        for index, left in enumerate(assertions):
            for right in assertions[index + 1 :]:
                conflict = self._record_conflict(left, right, relations=relations)
                if conflict is None:
                    continue
                both_anchors = left["standing"] == right["standing"] == "anchored"
                same_committed_perspective = (
                    left["perspective_id"] == right["perspective_id"]
                    and {left["standing"], right["standing"]} <= {"accepted", "anchored"}
                )
                if not (both_anchors or same_committed_perspective):
                    continue
                kind = (
                    "anchor-contradiction"
                    if both_anchors and conflict["kind"] == "opposite-stances"
                    else "anchor-relation-contradiction"
                    if both_anchors
                    else "perspective-contradiction"
                    if conflict["kind"] == "opposite-stances"
                    else "perspective-relation-contradiction"
                )
                conflicts.append(
                    {
                        **conflict,
                        "kind": kind,
                        "severity": "invariant" if both_anchors else "attention",
                        "claim_id": conflict.get("claim_id", left["claim_id"]),
                        "claim_ids": sorted({left["claim_id"], right["claim_id"]}),
                        "left_assertion_id": left["assertion_id"],
                        "right_assertion_id": right["assertion_id"],
                        "perspective_id": None if both_anchors else left["perspective_id"],
                    }
                )

        # A perspective may hold a set of accepted assertions that collectively
        # violates a hidden cardinality constraint even when no pair is sufficient
        # to expose the problem. This remains a planner-only diagnostic.
        by_perspective: dict[str, list[dict[str, Any]]] = {}
        for assertion in assertions:
            if assertion["standing"] in {"accepted", "anchored"}:
                by_perspective.setdefault(str(assertion["perspective_id"]), []).append(assertion)
        for perspective_id, records in by_perspective.items():
            for constraint in cardinalities:
                conflict = cardinality_conflict(constraint, records)
                if conflict is None:
                    continue
                assertion_ids = [
                    item.get("id")
                    for item in conflict["witness_records"]
                    if item.get("kind") == "assertion" and item.get("id") is not None
                ]
                conflicts.append(
                    {
                        **conflict,
                        "kind": "perspective-cardinality-contradiction",
                        "severity": "attention",
                        "perspective_id": perspective_id,
                        "claim_ids": conflict["witness_claim_ids"],
                        "assertion_ids": assertion_ids,
                    }
                )

        assignments = self._active_world_assignment_rows(active_worlds_only=True)
        by_world: dict[str, list[dict[str, Any]]] = {}
        for assignment in assignments:
            by_world.setdefault(str(assignment["world_id"]), []).append(assignment)

        for world_id, records in by_world.items():
            for index, left in enumerate(records):
                for right in records[index + 1 :]:
                    conflict = self._record_conflict(left, right, relations=relations)
                    if conflict is None:
                        continue
                    conflicts.append(
                        {
                            **conflict,
                            "kind": (
                                "world-internal-contradiction"
                                if conflict["kind"] == "opposite-stances"
                                else "world-relation-contradiction"
                            ),
                            "severity": "invariant",
                            "claim_id": conflict.get("claim_id", left["claim_id"]),
                            "claim_ids": sorted({left["claim_id"], right["claim_id"]}),
                            "world_id": world_id,
                            "left_assignment_id": left["assignment_id"],
                            "right_assignment_id": right["assignment_id"],
                        }
                    )

        anchors = [item for item in assertions if item["standing"] == "anchored"]
        for assignment in assignments:
            for anchor in anchors:
                conflict = self._record_conflict(assignment, anchor, relations=relations)
                if conflict is None:
                    continue
                conflicts.append(
                    {
                        **conflict,
                        "kind": (
                            "world-anchor-contradiction"
                            if conflict["kind"] == "opposite-stances"
                            else "world-anchor-relation-contradiction"
                        ),
                        "severity": "invariant",
                        "claim_id": conflict.get("claim_id", assignment["claim_id"]),
                        "claim_ids": sorted({assignment["claim_id"], anchor["claim_id"]}),
                        "world_id": assignment["world_id"],
                        "assignment_id": assignment["assignment_id"],
                        "assertion_id": anchor["assertion_id"],
                    }
                )

        anchor_cardinality_ids: set[str] = set()
        for constraint in cardinalities:
            conflict = cardinality_conflict(constraint, anchors)
            if conflict is None:
                continue
            anchor_cardinality_ids.add(str(constraint["constraint_id"]))
            conflicts.append(
                {
                    **conflict,
                    "kind": "anchor-cardinality-contradiction",
                    "severity": "invariant",
                    "claim_ids": conflict["witness_claim_ids"],
                    "assertion_ids": [
                        item.get("id")
                        for item in conflict["witness_records"]
                        if item.get("kind") == "assertion" and item.get("id") is not None
                    ],
                }
            )
        for world_id, records in by_world.items():
            combined = [*anchors, *records]
            for constraint in cardinalities:
                conflict = cardinality_conflict(constraint, combined)
                if conflict is None:
                    continue
                assignment_ids = [
                    item.get("id")
                    for item in conflict["witness_records"]
                    if item.get("kind") == "world_assignment" and item.get("id") is not None
                ]
                if not assignment_ids and str(constraint["constraint_id"]) in anchor_cardinality_ids:
                    continue
                conflicts.append(
                    {
                        **conflict,
                        "kind": "world-cardinality-contradiction",
                        "severity": "invariant",
                        "world_id": world_id,
                        "claim_ids": conflict["witness_claim_ids"],
                        "assignment_ids": assignment_ids,
                        "assertion_ids": [
                            item.get("id")
                            for item in conflict["witness_records"]
                            if item.get("kind") == "assertion" and item.get("id") is not None
                        ],
                    }
                )
        # Consequences are not silently erased when a premise or dependent ends.
        # They remain inspectable repair obligations until explicitly retired or relinked.
        for link in self.consequence_links():
            reasons: list[str] = []
            if not link["premise_active"]:
                reasons.append("premise-ended")
            if not link["dependent_active"]:
                reasons.append("dependent-ended")
            if not reasons:
                continue
            claim_ids = sorted(
                {
                    str(claim_id)
                    for claim_id in (
                        link.get("premise_claim_id"),
                        link.get("dependent_claim_id"),
                    )
                    if claim_id is not None
                }
            )
            conflicts.append(
                {
                    "kind": "orphaned-consequence",
                    "severity": "attention",
                    "consequence_id": link["consequence_id"],
                    "premise_assignment_id": link["premise_assignment_id"],
                    "dependent_kind": link["dependent_kind"],
                    "dependent_id": link["dependent_id"],
                    "relation": link["relation"],
                    "consequence_severity": link["severity"],
                    "reasons": reasons,
                    "world_id": link.get("premise_world_id"),
                    "claim_ids": claim_ids,
                    "repair": (
                        "request a consequence-repair-review, then replace the link with explicit "
                        "successor custody or retire it as obsolete"
                    ),
                }
            )
        return conflicts

    def snapshot(self) -> dict[str, Any]:
        agents = []
        for row in self.conn.execute("SELECT * FROM agents ORDER BY created_seq, agent_id").fetchall():
            item = dict(row)
            item["metadata"] = json.loads(item.pop("metadata_json"))
            agents.append(item)
        sources = []
        for row in self.conn.execute("SELECT * FROM sources ORDER BY created_seq, source_id").fetchall():
            item = dict(row)
            item["metadata"] = json.loads(item.pop("metadata_json"))
            sources.append(item)
        evidence = self.evidence_links()
        questions = []
        for row in self.conn.execute("SELECT * FROM questions ORDER BY created_seq").fetchall():
            item = dict(row)
            item["audience"] = json.loads(item.pop("audience_json"))
            questions.append(item)
        return {
            "schema": "lacuna.snapshot.v1",
            "cube_id": self.meta("cube_id"),
            "head": self.head(),
            "agents": agents,
            "sources": sources,
            "claims": self.claims(),
            "claim_relations": self.claim_relations(include_retired=True),
            "cardinality_constraints": self.cardinality_constraints(include_retired=True),
            "active_assertions": self.active_assertions(),
            "worlds": self.worlds(),
            "particle_bank": self.particle_bank(),
            "particle_updates": self.particle_updates(),
            "particle_reconciliations": self.particle_reconciliations(),
            "world_assignment_history": self.assignment_history(),
            "commitment_transitions": self.commitment_transitions(),
            "consequence_links": self.consequence_links(include_retired=True),
            "consequence_repairs": self.consequence_repairs(),
            "fair_play_seals": self.seals(),
            "evidence_links": evidence,
            "questions": questions,
            "conflicts": self.conflicts(),
        }
