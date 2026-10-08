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
from lacuna.store import Cube
from lacuna.util import deterministic_claim_id


class ClaimRelationTests(unittest.TestCase):
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
        self.left = self.declare("mystery", "culprit_is", "Ada")
        self.right = self.declare("mystery", "culprit_is", "Basil")

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

    def add_relation(self, kind: str = "excludes", relation_id: str = "rel_culprit") -> None:
        self.cube.apply_operations(
            actor_id="user",
            operations=[
                {
                    "op": "declare_relation",
                    "relation_id": relation_id,
                    "left_claim_id": self.left,
                    "right_claim_id": self.right,
                    "relation": kind,
                    "source_id": None,
                    "rationale": "The authored mystery permits at most one of these identities.",
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

    def anchor(self, claim_id: str, stance: str, assertion_id: str) -> None:
        self.cube.apply_operations(
            actor_id="user",
            operations=[
                {
                    "op": "record_assertion",
                    "assertion_id": assertion_id,
                    "claim_id": claim_id,
                    "assertor_id": "user",
                    "perspective_id": "user",
                    "source_id": None,
                    "stance": stance,
                    "basis": "commitment",
                    "standing": "anchored",
                    "confidence": 1.0,
                    "visibility": "private",
                    "audience": [],
                    "timeline_id": "main",
                    "valid_from": None,
                    "valid_to": None,
                    "note": "test anchor",
                    "supersedes_id": None,
                }
            ],
        )

    def test_excludes_blocks_two_true_assignments_in_one_world(self) -> None:
        self.add_relation()
        self.add_world()
        self.assign(self.left, "true", assignment_id="asn_left")
        head = self.cube.head()
        count = self.cube.event_count()
        with self.assertRaises(LacunaError) as caught:
            self.assign(self.right, "true", assignment_id="asn_right")
        self.assertEqual(caught.exception.code, "world-internal-conflict")
        self.assertEqual(self.cube.head(), head)
        self.assertEqual(self.cube.event_count(), count)
        self.assertEqual(len(self.cube.world_assignments("wld_case")), 1)

    def test_entailment_checks_compatibility_without_materializing_truth(self) -> None:
        self.add_relation("entails")
        self.add_world()
        self.assign(self.left, "false", assignment_id="asn_left_false")
        self.assign(self.right, "false", assignment_id="asn_right_false")
        self.assertEqual(len(self.cube.world_assignments("wld_case")), 2)

        self.add_world("wld_bad")
        self.assign(self.left, "true", world_id="wld_bad", assignment_id="asn_left_true")
        with self.assertRaises(LacunaError) as caught:
            self.assign(self.right, "false", world_id="wld_bad", assignment_id="asn_right_bad")
        self.assertEqual(caught.exception.code, "world-internal-conflict")
        # No closure: assigning the antecedent did not create a consequent row.
        self.assertEqual(len(self.cube.world_assignments("wld_bad")), 1)

    def test_relation_declaration_refuses_to_retroactively_break_live_world(self) -> None:
        self.add_world()
        self.assign(self.left, "true", assignment_id="asn_left")
        self.assign(self.right, "true", assignment_id="asn_right")
        head = self.cube.head()
        with self.assertRaises(LacunaError) as caught:
            self.add_relation()
        self.assertEqual(caught.exception.code, "relation-introduces-conflict")
        self.assertEqual(self.cube.head(), head)
        self.assertEqual(self.cube.claim_relations(), [])

    def test_relation_applies_across_anchors(self) -> None:
        self.add_relation()
        self.anchor(self.left, "true", "ast_left")
        with self.assertRaises(LacunaError) as caught:
            self.anchor(self.right, "true", "ast_right")
        self.assertEqual(caught.exception.code, "anchor-relation-contradiction")

    def test_overlapping_same_claim_contradiction_is_rejected_and_exact_change_is_governed(self) -> None:
        self.add_world()
        self.assign(self.left, "true", assignment_id="asn_original", valid_from=0, valid_to=10)
        with self.assertRaises(LacunaError) as caught:
            self.assign(self.left, "false", assignment_id="asn_overlap", valid_from=5, valid_to=15)
        self.assertEqual(caught.exception.code, "world-internal-conflict")

        impact = self.cube.revision_impact("asn_original")
        self.cube.apply_operations(
            actor_id="user",
            operations=[
                {
                    "op": "revise_world",
                    "assignment_id": "asn_replacement",
                    "revises_assignment_id": "asn_original",
                    "truth": "false",
                    "commitment": "soft",
                    "expected_impact_sha256": impact["impact_sha256"],
                    "reason": "Exercise explicit replacement custody.",
                }
            ],
        )
        assignments = self.cube.world_assignments("wld_case")
        self.assertEqual([item["assignment_id"] for item in assignments], ["asn_replacement"])
        self.assertEqual(assignments[0]["truth"], "false")

    def test_retiring_relation_preserves_custody_and_loosens_constraint(self) -> None:
        self.add_relation()
        self.cube.apply_operations(
            actor_id="user",
            operations=[
                {"op": "retire_relation", "relation_id": "rel_culprit", "reason": "Author revised the premise."}
            ],
        )
        self.add_world()
        self.assign(self.left, "true", assignment_id="asn_left")
        self.assign(self.right, "true", assignment_id="asn_right")
        self.assertEqual(self.cube.claim_relations(), [])
        history = self.cube.claim_relations(include_retired=True)
        self.assertEqual(len(history), 1)
        self.assertIsNotNone(history[0]["ended_seq"])
        rebuilt = self.cube.rebuild_projections()
        self.assertEqual(rebuilt["overall_status"], "pass")
        self.assertEqual(len(self.cube.claim_relations(include_retired=True)), 1)

    def test_planner_context_contains_relations_and_perspective_context_omits_them(self) -> None:
        self.add_relation()
        planner = build_context(self.cube)
        audience = build_context(self.cube, agent_id="player")
        self.assertEqual(len(planner["claim_relations"]), 1)
        self.assertEqual(audience["claim_relations"], [])
        self.assertIn("claim_relations", audience["omitted"])

    def test_explanation_traces_origin_and_respects_visibility(self) -> None:
        self.cube.apply_operations(
            actor_id="user",
            operations=[
                {
                    "op": "add_source",
                    "source_id": "src_scene",
                    "kind": "scene",
                    "label": "Scene one",
                    "locator": "scene:1",
                    "content_sha256": None,
                    "metadata": {},
                },
                {
                    "op": "record_assertion",
                    "assertion_id": "ast_seen",
                    "claim_id": self.left,
                    "assertor_id": "user",
                    "perspective_id": "player",
                    "source_id": "src_scene",
                    "stance": "true",
                    "basis": "observation",
                    "standing": "accepted",
                    "confidence": 1.0,
                    "visibility": "private",
                    "audience": [],
                    "timeline_id": "main",
                    "valid_from": 1,
                    "valid_to": 1,
                    "note": "The player saw it.",
                    "supersedes_id": None,
                },
            ],
        )
        explanation = self.cube.explain("ast_seen", agent_id="player")
        self.assertEqual(explanation["target"]["kind"], "assertion")
        self.assertEqual(explanation["custody"]["created_by_event"]["event_type"], "assertion.recorded")
        roles = {item["role"] for item in explanation["dependencies"]}
        self.assertTrue({"asserts", "asserted_by", "held_by", "sourced_from"} <= roles)
        self.add_relation()
        with self.assertRaises(LacunaError) as caught:
            self.cube.explain("rel_culprit", agent_id="player")
        self.assertEqual(caught.exception.code, "explanation-not-visible")

    def test_schema_one_cube_migrates_without_changing_ledger_head(self) -> None:
        before_head = self.cube.head()
        self.cube.close()
        self.cube = None
        db_path = self.root / "lacuna.sqlite3"
        conn = sqlite3.connect(db_path)
        try:
            conn.execute("DROP TABLE cardinality_members")
            conn.execute("DROP TABLE cardinality_constraints")
            conn.execute("DROP TABLE claim_relations")
            conn.execute("DROP TABLE schema_migrations")
            conn.execute("PRAGMA user_version = 1")
            conn.execute("UPDATE meta SET value = '1' WHERE key = 'schema_version'")
            conn.commit()
        finally:
            conn.close()

        with self.assertRaises(LacunaError) as caught:
            Cube.open(self.root)
        self.assertEqual(caught.exception.code, "database-migration-required")
        receipt = Cube.migrate(self.root)
        self.assertTrue(receipt["changed"])
        self.assertEqual(receipt["before_head"], before_head)
        self.assertEqual(receipt["after_head"], before_head)
        self.cube = Cube.open(self.root)
        self.assertEqual(self.cube.head(), before_head)
        self.assertEqual(self.cube.verify()["overall_status"], "pass")


if __name__ == "__main__":
    unittest.main()
