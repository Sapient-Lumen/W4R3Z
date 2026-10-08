from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from lacuna.context import build_context
from lacuna.errors import LacunaError
from lacuna.render import render_context_markdown
from lacuna.store import Cube
from lacuna.turns import normalize_turn_operations
from lacuna.util import deterministic_claim_id, utc_now


class CardinalityConstraintTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name) / "cube"
        self.cube = Cube.init(self.root, owner_id="user", owner_label="User")
        self.cube.apply_operations(
            actor_id="user",
            operations=[
                {
                    "op": "register_agent",
                    "agent_id": "player",
                    "kind": "human",
                    "label": "Player",
                    "metadata": {},
                }
            ],
        )
        self.ada = self.declare("mystery", "culprit_is", "Ada")
        self.basil = self.declare("mystery", "culprit_is", "Basil")
        self.cora = self.declare("mystery", "culprit_is", "Cora")

    def tearDown(self) -> None:
        if self.cube is not None:
            self.cube.close()
        self.temporary.cleanup()

    def declare(self, subject: str, predicate: str, obj: object) -> str:
        claim_id = deterministic_claim_id(subject, predicate, obj, "world")
        self.cube.apply_operations(
            actor_id="user",
            operations=[
                {
                    "op": "declare_claim",
                    "claim_id": claim_id,
                    "subject": subject,
                    "predicate": predicate,
                    "object": obj,
                    "scope": "world",
                }
            ],
        )
        return claim_id

    def constrain(
        self,
        *,
        claim_ids: list[str] | None = None,
        min_true: int = 1,
        max_true: int = 1,
        constraint_id: str = "crd_culprit",
    ) -> None:
        self.cube.apply_operations(
            actor_id="user",
            operations=[
                {
                    "op": "declare_cardinality",
                    "constraint_id": constraint_id,
                    "label": "Culprit count",
                    "claim_ids": claim_ids or [self.ada, self.basil, self.cora],
                    "min_true": min_true,
                    "max_true": max_true,
                    "source_id": None,
                    "rationale": "The authored mystery has a bounded number of culprits.",
                }
            ],
        )

    def add_world(self, world_id: str = "wld_case") -> None:
        self.cube.apply_operations(
            actor_id="user",
            operations=[
                {
                    "op": "create_world",
                    "world_id": world_id,
                    "label": world_id,
                    "parent_world_id": None,
                    "status": "live",
                    "weight": 1.0,
                    "rationale": "test world",
                }
            ],
        )

    def assign(
        self,
        claim_id: str,
        truth: str,
        *,
        world_id: str = "wld_case",
        assignment_id: str | None = None,
        valid_from: int | None = None,
        valid_to: int | None = None,
    ) -> None:
        self.cube.apply_operations(
            actor_id="user",
            operations=[
                {
                    "op": "assign_world",
                    "assignment_id": assignment_id,
                    "world_id": world_id,
                    "claim_id": claim_id,
                    "truth": truth,
                    "commitment": "soft",
                    "confidence": 0.8,
                    "rationale": "test assignment",
                    "source_assertion_id": None,
                    "timeline_id": "main",
                    "valid_from": valid_from,
                    "valid_to": valid_to,
                }
            ],
        )

    def assertion(
        self,
        claim_id: str,
        stance: str,
        assertion_id: str,
        *,
        standing: str = "accepted",
        perspective_id: str = "player",
        visibility: str = "public",
    ) -> None:
        self.cube.apply_operations(
            actor_id="user",
            operations=[
                {
                    "op": "record_assertion",
                    "assertion_id": assertion_id,
                    "claim_id": claim_id,
                    "assertor_id": "user",
                    "perspective_id": perspective_id,
                    "source_id": None,
                    "stance": stance,
                    "basis": "commitment",
                    "standing": standing,
                    "confidence": 1.0,
                    "visibility": visibility,
                    "audience": [],
                    "timeline_id": "main",
                    "valid_from": None,
                    "valid_to": None,
                    "note": "test assertion",
                    "supersedes_id": None,
                }
            ],
        )

    def test_exactly_one_rejects_second_true_without_materializing_unknowns(self) -> None:
        self.constrain()
        self.add_world()
        self.assign(self.ada, "true", assignment_id="asn_ada")
        assignments = self.cube.world_assignments("wld_case")
        self.assertEqual([item["claim_id"] for item in assignments], [self.ada])

        head = self.cube.head()
        with self.assertRaises(LacunaError) as caught:
            self.assign(self.basil, "true", assignment_id="asn_basil")
        self.assertEqual(caught.exception.code, "world-cardinality-conflict")
        self.assertEqual(caught.exception.details["violation"], "upper-bound-exceeded")
        self.assertEqual(self.cube.head(), head)
        self.assertEqual(len(self.cube.world_assignments("wld_case")), 1)

    def test_lower_bound_waits_for_explicit_falsehood_and_never_closes_the_world(self) -> None:
        self.constrain()
        self.add_world()
        self.assign(self.ada, "false", assignment_id="asn_ada_false")
        self.assign(self.basil, "false", assignment_id="asn_basil_false")
        self.assertEqual(len(self.cube.world_assignments("wld_case")), 2)
        self.assertNotIn(self.cora, {item["claim_id"] for item in self.cube.world_assignments("wld_case")})

        with self.assertRaises(LacunaError) as caught:
            self.assign(self.cora, "false", assignment_id="asn_cora_false")
        self.assertEqual(caught.exception.code, "world-cardinality-conflict")
        self.assertEqual(caught.exception.details["violation"], "lower-bound-impossible")
        self.assertEqual(caught.exception.details["unresolved_count"], 0)

    def test_temporal_witness_distinguishes_touching_from_nonoverlapping_truths(self) -> None:
        self.constrain(claim_ids=[self.ada, self.basil], min_true=0, max_true=1)
        self.add_world("wld_nonoverlap")
        self.assign(
            self.ada,
            "true",
            world_id="wld_nonoverlap",
            assignment_id="asn_a_nonoverlap",
            valid_from=0,
            valid_to=4,
        )
        self.assign(
            self.basil,
            "true",
            world_id="wld_nonoverlap",
            assignment_id="asn_b_nonoverlap",
            valid_from=5,
            valid_to=9,
        )
        self.assertEqual(len(self.cube.world_assignments("wld_nonoverlap")), 2)

        self.add_world("wld_touching")
        self.assign(
            self.ada,
            "true",
            world_id="wld_touching",
            assignment_id="asn_a_touching",
            valid_from=0,
            valid_to=4,
        )
        with self.assertRaises(LacunaError) as caught:
            self.assign(
                self.basil,
                "true",
                world_id="wld_touching",
                assignment_id="asn_b_touching",
                valid_from=4,
                valid_to=9,
            )
        details = caught.exception.details
        self.assertEqual(caught.exception.code, "world-cardinality-conflict")
        self.assertEqual(details["witness_tick"], 4)
        self.assertEqual(details["witness_valid_from"], 4)
        self.assertEqual(details["witness_valid_to"], 4)

    def test_anchor_and_world_are_evaluated_as_one_partial_valuation(self) -> None:
        self.constrain(claim_ids=[self.ada, self.basil], min_true=1, max_true=1)
        self.assertion(self.ada, "true", "ast_ada", standing="anchored", perspective_id="user")
        self.add_world()
        with self.assertRaises(LacunaError) as caught:
            self.assign(self.basil, "true", assignment_id="asn_basil")
        self.assertEqual(caught.exception.code, "world-cardinality-conflict")
        kinds = {item["kind"] for item in caught.exception.details["witness_records"]}
        self.assertEqual(kinds, {"assertion", "world_assignment"})

    def test_declaration_cannot_retroactively_break_a_live_world(self) -> None:
        self.add_world()
        self.assign(self.ada, "true", assignment_id="asn_ada")
        self.assign(self.basil, "true", assignment_id="asn_basil")
        before_head = self.cube.head()
        before_count = self.cube.event_count()
        with self.assertRaises(LacunaError) as caught:
            self.constrain(claim_ids=[self.ada, self.basil], min_true=0, max_true=1)
        self.assertEqual(caught.exception.code, "cardinality-introduces-conflict")
        self.assertEqual(self.cube.head(), before_head)
        self.assertEqual(self.cube.event_count(), before_count)
        self.assertEqual(self.cube.cardinality_constraints(), [])

    def test_retirement_preserves_custody_and_rebuilds(self) -> None:
        self.constrain(claim_ids=[self.ada, self.basil], min_true=0, max_true=1)
        self.cube.apply_operations(
            actor_id="user",
            operations=[
                {
                    "op": "retire_cardinality",
                    "constraint_id": "crd_culprit",
                    "reason": "The scenario now permits accomplices.",
                }
            ],
        )
        self.add_world()
        self.assign(self.ada, "true", assignment_id="asn_ada")
        self.assign(self.basil, "true", assignment_id="asn_basil")
        self.assertEqual(self.cube.cardinality_constraints(), [])
        history = self.cube.cardinality_constraints(include_retired=True)
        self.assertEqual(len(history), 1)
        self.assertIsNotNone(history[0]["ended_seq"])
        self.assertEqual(history[0]["claim_ids"], sorted([self.ada, self.basil]))
        self.assertEqual(self.cube.rebuild_projections()["overall_status"], "pass")
        self.assertEqual(len(self.cube.cardinality_constraints(include_retired=True)), 1)

    def test_context_firewall_hides_constraint_ontology_and_derived_diagnostics(self) -> None:
        self.assertion(self.ada, "true", "ast_ada")
        self.assertion(self.basil, "true", "ast_basil")
        self.constrain(claim_ids=[self.ada, self.basil], min_true=0, max_true=1)

        planner = build_context(self.cube)
        audience = build_context(self.cube, agent_id="player")
        self.assertEqual(len(planner["cardinality_constraints"]), 1)
        self.assertTrue(any(item.get("constraint_id") for item in planner["conflicts"]))
        self.assertEqual(audience["cardinality_constraints"], [])
        self.assertFalse(any(item.get("constraint_id") for item in audience["conflicts"]))
        self.assertIn("constraint_derived_conflicts", audience["omitted"])
        rendered = render_context_markdown(audience)
        self.assertIn("Cardinality constraints", rendered)
        self.assertIn("Omitted:", rendered)
        self.assertNotIn("crd_culprit", rendered)

    def test_explanation_is_custodied_and_planner_only(self) -> None:
        self.constrain()
        explanation = self.cube.explain("crd_culprit")
        self.assertEqual(explanation["target"]["kind"], "cardinality_constraint")
        self.assertEqual(explanation["custody"]["created_by_event"]["event_type"], "cardinality.declared")
        member_links = [item for item in explanation["dependencies"] if item["role"] == "member"]
        self.assertEqual({item["id"] for item in member_links}, {self.ada, self.basil, self.cora})
        with self.assertRaises(LacunaError) as caught:
            self.cube.explain("crd_culprit", agent_id="player")
        self.assertEqual(caught.exception.code, "explanation-not-visible")

    def test_turn_alias_normalization_resolves_constraint_member_lists(self) -> None:
        operations = [
            {
                "op": "declare_claim",
                "as": "culprit.ada",
                "subject": "mystery",
                "predicate": "culprit_is",
                "object": "Dara",
                "scope": "world",
            },
            {
                "op": "declare_claim",
                "as": "culprit.basil",
                "subject": "mystery",
                "predicate": "culprit_is",
                "object": "Eli",
                "scope": "world",
            },
            {
                "op": "declare_cardinality",
                "as": "culprit.rule",
                "label": "One culprit",
                "claim_ids": ["@culprit.ada", "@culprit.basil"],
                "min_true": 1,
                "max_true": 1,
                "source_id": None,
                "rationale": "Exactly one culprit is selected in this authored mystery.",
            },
        ]
        normalized, aliases = normalize_turn_operations(operations, initial_aliases={})
        self.assertEqual(normalized[2]["claim_ids"], [aliases["culprit.ada"], aliases["culprit.basil"]])
        self.assertEqual(normalized[2]["constraint_id"], aliases["culprit.rule"])

    def test_schema_two_cube_migrates_without_rewriting_the_ledger(self) -> None:
        before_head = self.cube.head()
        self.cube.close()
        self.cube = None
        db_path = self.root / "lacuna.sqlite3"
        conn = sqlite3.connect(db_path)
        try:
            conn.execute("DROP TABLE cardinality_members")
            conn.execute("DROP TABLE cardinality_constraints")
            conn.execute("DELETE FROM schema_migrations")
            conn.execute(
                """INSERT INTO schema_migrations(
                       target_version, source_version, applied_at, runtime_version, migration_sha256
                   ) VALUES (2, 0, ?, '0.147.0', ?)""",
                (utc_now(), "0" * 64),
            )
            conn.execute("PRAGMA user_version = 2")
            conn.execute("UPDATE meta SET value = '2' WHERE key = 'schema_version'")
            conn.commit()
        finally:
            conn.close()

        with self.assertRaises(LacunaError) as caught:
            Cube.open(self.root)
        self.assertEqual(caught.exception.code, "database-migration-required")
        receipt = Cube.migrate(self.root)
        self.assertTrue(receipt["changed"])
        self.assertEqual(receipt["source_version"], 2)
        self.assertEqual(receipt["target_version"], 8)
        self.assertEqual(receipt["before_head"], before_head)
        self.assertEqual(receipt["after_head"], before_head)
        self.cube = Cube.open(self.root)
        self.assertEqual(self.cube.head(), before_head)
        self.assertEqual(self.cube.verify()["overall_status"], "pass")


if __name__ == "__main__":
    unittest.main()
