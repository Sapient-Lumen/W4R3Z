from __future__ import annotations

import json
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
from lacuna.turns import build_turn_packet, commit_turn_proposal
from lacuna.util import deterministic_claim_id


class ConsequenceRepairTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name) / "cube"
        self.cube = Cube.init(self.root)

    def tearDown(self) -> None:
        self.cube.close()
        self.temporary.cleanup()

    def add_claim(self, name: str) -> str:
        claim_id = deterministic_claim_id(name, "is_true", True, "world")
        self.cube.apply_operations(
            actor_id="user",
            operations=[
                {
                    "op": "declare_claim",
                    "claim_id": claim_id,
                    "subject": name,
                    "predicate": "is_true",
                    "object": True,
                    "scope": "world",
                }
            ],
        )
        return claim_id

    def add_assignment(
        self,
        name: str,
        assignment_id: str,
        *,
        world_id: str = "wld_case",
    ) -> str:
        claim_id = self.add_claim(name)
        if not self.cube._exists("worlds", "world_id", world_id):
            self.cube.apply_operations(
                actor_id="user",
                operations=[
                    {
                        "op": "create_world",
                        "world_id": world_id,
                        "label": world_id,
                    }
                ],
            )
        self.cube.apply_operations(
            actor_id="user",
            operations=[
                {
                    "op": "assign_world",
                    "assignment_id": assignment_id,
                    "world_id": world_id,
                    "claim_id": claim_id,
                    "truth": "true",
                    "commitment": "tentative",
                    "commitment_basis": "planning",
                }
            ],
        )
        return claim_id

    def link_assignment(
        self,
        premise_id: str,
        dependent_id: str,
        *,
        consequence_id: str,
        relation: str = "causes",
        severity: str = "material",
        rationale: str | None = None,
    ) -> None:
        self.cube.apply_operations(
            actor_id="user",
            operations=[
                {
                    "op": "link_consequence",
                    "consequence_id": consequence_id,
                    "premise_assignment_id": premise_id,
                    "dependent_kind": "world_assignment",
                    "dependent_id": dependent_id,
                    "relation": relation,
                    "severity": severity,
                    "rationale": rationale or f"{premise_id} explicitly governs {dependent_id}.",
                }
            ],
        )

    def replacement_operation(
        self,
        review: dict,
        *,
        predecessor_id: str,
        successor_id: str,
        premise_id: str,
        dependent_kind: str,
        dependent_id: str,
        relation: str,
        severity: str = "material",
        rationale: str = "Reviewed successor dependency.",
        repair_id: str = "cpr_successor",
        reason: str = "Replace obsolete dependency custody.",
    ) -> dict:
        return {
            "op": "replace_consequence",
            "repair_id": repair_id,
            "consequence_id": successor_id,
            "replaces_consequence_id": predecessor_id,
            "premise_assignment_id": premise_id,
            "dependent_kind": dependent_kind,
            "dependent_id": dependent_id,
            "relation": relation,
            "severity": severity,
            "rationale": rationale,
            "expected_repair_sha256": review["repair_review_sha256"],
            "reason": reason,
        }

    def test_orphan_repair_review_and_replacement_preserve_lineage(self) -> None:
        premise_claim = self.add_assignment("premise", "asn_premise")
        self.add_assignment("dependent", "asn_dependent")
        self.link_assignment(
            "asn_premise",
            "asn_dependent",
            consequence_id="csq_old",
            relation="constrains",
        )

        impact = self.cube.revision_impact("asn_premise")
        self.cube.apply_operations(
            actor_id="user",
            operations=[
                {
                    "op": "revise_world",
                    "assignment_id": "asn_premise_v2",
                    "revises_assignment_id": "asn_premise",
                    "truth": "false",
                    "expected_impact_sha256": impact["impact_sha256"],
                    "reason": "The latent premise was reconsidered.",
                }
            ],
        )
        self.assertEqual(
            self.cube._require_world_assignment("asn_premise_v2")["claim_id"],
            premise_claim,
        )
        old = self.cube.consequence_links(include_retired=True)[0]
        self.assertTrue(old["repair_required"])
        self.assertEqual(self.cube.status()["orphaned_consequence_count"], 1)

        review = self.cube.consequence_repair_review("csq_old")
        self.assertEqual(review["review"]["mode"], "orphan-repair")
        self.assertTrue(review["review"]["replaceable"])
        self.assertEqual(
            review["known_successors"]["premise_assignment_ids"],
            ["asn_premise_v2"],
        )
        self.cube.apply_operations(
            actor_id="user",
            operations=[
                self.replacement_operation(
                    review,
                    predecessor_id="csq_old",
                    successor_id="csq_new",
                    premise_id="asn_premise_v2",
                    dependent_kind="world_assignment",
                    dependent_id="asn_dependent",
                    relation="constrains",
                    repair_id="cpr_premise_v2",
                )
            ],
        )

        links = {
            item["consequence_id"]: item
            for item in self.cube.consequence_links(include_retired=True)
        }
        self.assertEqual(links["csq_old"]["lineage_state"], "replaced")
        self.assertEqual(links["csq_old"]["replacement_consequence_id"], "csq_new")
        self.assertIsNotNone(links["csq_old"]["ended_seq"])
        self.assertEqual(links["csq_new"]["lineage_state"], "replacement")
        self.assertEqual(links["csq_new"]["replaces_consequence_id"], "csq_old")
        self.assertIsNone(links["csq_new"]["ended_seq"])
        repair = self.cube.consequence_repairs()[0]
        self.assertEqual(repair["repair_id"], "cpr_premise_v2")
        self.assertEqual(repair["predecessor_consequence_id"], "csq_old")
        self.assertEqual(repair["successor_consequence_id"], "csq_new")
        self.assertEqual(repair["review_head"], review["head"])
        self.assertTrue(repair["origin_event_id"].startswith("evt_"))
        self.assertTrue(repair["change_id"].startswith("chg_"))
        self.assertEqual(self.cube.status()["orphaned_consequence_count"], 0)
        self.assertEqual(self.cube.status()["consequence_repair_count"], 1)
        self.assertEqual(self.cube.verify()["overall_status"], "pass")

    def test_stale_repair_review_refuses_without_partial_mutation(self) -> None:
        self.add_assignment("premise", "asn_premise")
        self.add_assignment("dependent", "asn_dependent")
        self.link_assignment("asn_premise", "asn_dependent", consequence_id="csq_old")
        review = self.cube.consequence_repair_review("csq_old")
        self.cube.apply_operations(
            actor_id="user",
            operations=[
                {
                    "op": "add_source",
                    "source_id": "src_intervening",
                    "kind": "document",
                    "label": "Intervening custody",
                }
            ],
        )
        before_head = self.cube.head()
        before_events = self.cube.event_count()

        with self.assertRaises(LacunaError) as caught:
            self.cube.apply_operations(
                actor_id="user",
                operations=[
                    self.replacement_operation(
                        review,
                        predecessor_id="csq_old",
                        successor_id="csq_new",
                        premise_id="asn_premise",
                        dependent_kind="world_assignment",
                        dependent_id="asn_dependent",
                        relation="causes",
                        severity="binding",
                    )
                ],
            )
        self.assertEqual(caught.exception.code, "stale-consequence-repair-review")
        self.assertEqual(self.cube.head(), before_head)
        self.assertEqual(self.cube.event_count(), before_events)
        self.assertEqual(self.cube.consequence_repairs(), [])
        self.assertEqual(
            [item["consequence_id"] for item in self.cube.consequence_links()],
            ["csq_old"],
        )

    def test_atomic_batch_validates_reviews_against_shared_base_head(self) -> None:
        self.add_assignment("premise", "asn_premise")
        self.add_assignment("dependent", "asn_dependent")
        self.link_assignment("asn_premise", "asn_dependent", consequence_id="csq_old")
        review = self.cube.consequence_repair_review("csq_old")
        base_head = self.cube.head()
        self.cube.apply_changeset(
            {
                "schema": "lacuna.change-set.v1",
                "change_id": "chg_reviewed_batch",
                "actor_id": "user",
                "expected_head": base_head,
                "message": "Record provenance and reviewed repair atomically.",
                "operations": [
                    {
                        "op": "add_source",
                        "source_id": "src_batch",
                        "kind": "document",
                        "label": "Repair decision record",
                    },
                    self.replacement_operation(
                        review,
                        predecessor_id="csq_old",
                        successor_id="csq_new",
                        premise_id="asn_premise",
                        dependent_kind="world_assignment",
                        dependent_id="asn_dependent",
                        relation="causes",
                        severity="binding",
                    ),
                ],
            }
        )
        events = [
            item["event_type"]
            for item in self.cube.events()
            if item["change_id"] == "chg_reviewed_batch"
        ]
        self.assertEqual(events, ["source.added", "consequence.replaced"])
        self.assertEqual(self.cube.consequence_repairs()[0]["review_sha256"], review["repair_review_sha256"])

    def test_shared_base_head_does_not_hide_prior_semantic_mutation(self) -> None:
        self.add_assignment("premise", "asn_premise")
        self.add_assignment("dependent", "asn_dependent")
        self.link_assignment("asn_premise", "asn_dependent", consequence_id="csq_old")
        review = self.cube.consequence_repair_review("csq_old")
        before_head = self.cube.head()
        before_events = self.cube.event_count()

        with self.assertRaises(LacunaError) as caught:
            self.cube.apply_changeset(
                {
                    "schema": "lacuna.change-set.v1",
                    "change_id": "chg_mutate_then_repair",
                    "actor_id": "user",
                    "expected_head": before_head,
                    "message": "An earlier semantic mutation must stale the receipt.",
                    "operations": [
                        {
                            "op": "retire_consequence",
                            "consequence_id": "csq_old",
                            "reason": "End the reviewed predecessor first.",
                        },
                        self.replacement_operation(
                            review,
                            predecessor_id="csq_old",
                            successor_id="csq_new",
                            premise_id="asn_premise",
                            dependent_kind="world_assignment",
                            dependent_id="asn_dependent",
                            relation="causes",
                            severity="binding",
                        ),
                    ],
                }
            )
        self.assertEqual(caught.exception.code, "stale-consequence-repair-review")
        self.assertEqual(caught.exception.details["review_head"], before_head)
        self.assertNotEqual(caught.exception.details["current_head"], before_head)
        self.assertEqual(self.cube.head(), before_head)
        self.assertEqual(self.cube.event_count(), before_events)
        self.assertIsNone(self.cube.consequence_links()[0]["ended_seq"])

    def test_post_replacement_cycle_check_excludes_predecessor_edge(self) -> None:
        self.add_assignment("a", "asn_a")
        self.add_assignment("b", "asn_b")
        self.link_assignment("asn_a", "asn_b", consequence_id="csq_ab")
        review = self.cube.consequence_repair_review("csq_ab")
        self.cube.apply_operations(
            actor_id="user",
            operations=[
                self.replacement_operation(
                    review,
                    predecessor_id="csq_ab",
                    successor_id="csq_ba",
                    premise_id="asn_b",
                    dependent_kind="world_assignment",
                    dependent_id="asn_a",
                    relation="causes",
                    rationale="The reviewed direction is B to A.",
                )
            ],
        )
        active = self.cube.consequence_links()
        self.assertEqual(
            [(item["premise_assignment_id"], item["dependent_id"]) for item in active],
            [("asn_b", "asn_a")],
        )

    def test_true_post_replacement_cycle_is_refused_atomically(self) -> None:
        self.add_assignment("a", "asn_a")
        self.add_assignment("b", "asn_b")
        self.add_assignment("c", "asn_c")
        self.link_assignment("asn_a", "asn_b", consequence_id="csq_ab")
        self.link_assignment("asn_b", "asn_c", consequence_id="csq_bc")
        review = self.cube.consequence_repair_review("csq_ab")
        before_head = self.cube.head()
        before_events = self.cube.event_count()
        with self.assertRaises(LacunaError) as caught:
            self.cube.apply_operations(
                actor_id="user",
                operations=[
                    self.replacement_operation(
                        review,
                        predecessor_id="csq_ab",
                        successor_id="csq_cb",
                        premise_id="asn_c",
                        dependent_kind="world_assignment",
                        dependent_id="asn_b",
                        relation="causes",
                        rationale="This would create B→C→B.",
                    )
                ],
            )
        self.assertEqual(caught.exception.code, "consequence-cycle")
        self.assertEqual(caught.exception.details["cycle"], ["asn_c", "asn_b", "asn_c"])
        self.assertEqual(self.cube.head(), before_head)
        self.assertEqual(self.cube.event_count(), before_events)
        self.assertEqual(self.cube.consequence_repairs(), [])

    def test_new_consequences_refuse_already_ended_targets(self) -> None:
        self.add_assignment("premise", "asn_premise")
        claim_id = self.add_claim("reported_effect")
        self.cube.apply_operations(
            actor_id="user",
            operations=[
                {
                    "op": "record_assertion",
                    "assertion_id": "ast_old",
                    "claim_id": claim_id,
                    "assertor_id": "user",
                    "stance": "true",
                    "basis": "inference",
                    "standing": "accepted",
                    "visibility": "private",
                },
                {
                    "op": "record_assertion",
                    "assertion_id": "ast_new",
                    "claim_id": claim_id,
                    "assertor_id": "user",
                    "stance": "false",
                    "basis": "observation",
                    "standing": "accepted",
                    "visibility": "private",
                    "supersedes_id": "ast_old",
                },
                {
                    "op": "open_question",
                    "question_id": "qst_closed",
                    "text": "Does the effect persist?",
                    "about_claim_id": claim_id,
                    "opened_by": "user",
                    "visibility": "private",
                },
                {
                    "op": "close_question",
                    "question_id": "qst_closed",
                    "resolution_assertion_id": "ast_new",
                    "reason": "The newer assertion resolves the question.",
                },
            ],
        )

        before_head = self.cube.head()
        for dependent_kind, dependent_id, code in (
            ("assertion", "ast_old", "unknown-assertion"),
            ("question", "qst_closed", "unknown-question"),
        ):
            with self.subTest(dependent_kind=dependent_kind):
                with self.assertRaises(LacunaError) as caught:
                    self.cube.apply_operations(
                        actor_id="user",
                        operations=[
                            {
                                "op": "link_consequence",
                                "consequence_id": f"csq_{dependent_kind}",
                                "premise_assignment_id": "asn_premise",
                                "dependent_kind": dependent_kind,
                                "dependent_id": dependent_id,
                                "relation": "explains",
                                "severity": "notice",
                                "rationale": "A new link may not be born orphaned.",
                            }
                        ],
                    )
                self.assertEqual(caught.exception.code, code)
                self.assertEqual(self.cube.head(), before_head)
        self.assertEqual(self.cube.consequence_links(), [])

    def test_replacement_refuses_semantic_noop_and_duplicate_active_edge(self) -> None:
        self.add_assignment("a", "asn_a")
        self.add_assignment("b", "asn_b")
        self.add_assignment("c", "asn_c")
        self.link_assignment(
            "asn_a",
            "asn_b",
            consequence_id="csq_ab",
            rationale="Original semantics.",
        )
        review = self.cube.consequence_repair_review("csq_ab")
        with self.assertRaises(LacunaError) as caught:
            self.cube.apply_operations(
                actor_id="user",
                operations=[
                    self.replacement_operation(
                        review,
                        predecessor_id="csq_ab",
                        successor_id="csq_ab_copy",
                        premise_id="asn_a",
                        dependent_kind="world_assignment",
                        dependent_id="asn_b",
                        relation="causes",
                        rationale="Original semantics.",
                    )
                ],
            )
        self.assertEqual(caught.exception.code, "consequence-replacement-unchanged")

        self.link_assignment("asn_c", "asn_b", consequence_id="csq_cb")
        review = self.cube.consequence_repair_review("csq_ab")
        with self.assertRaises(LacunaError) as caught:
            self.cube.apply_operations(
                actor_id="user",
                operations=[
                    self.replacement_operation(
                        review,
                        predecessor_id="csq_ab",
                        successor_id="csq_duplicate",
                        premise_id="asn_c",
                        dependent_kind="world_assignment",
                        dependent_id="asn_b",
                        relation="causes",
                    )
                ],
            )
        self.assertEqual(caught.exception.code, "duplicate-active-consequence")
        self.assertEqual(self.cube.consequence_repairs(), [])

    def test_repair_context_explanations_and_rebuild_respect_firewall(self) -> None:
        self.add_assignment("premise", "asn_premise")
        self.add_assignment("dependent", "asn_dependent")
        self.link_assignment("asn_premise", "asn_dependent", consequence_id="csq_old")
        review = self.cube.consequence_repair_review("csq_old")
        self.cube.apply_operations(
            actor_id="user",
            operations=[
                self.replacement_operation(
                    review,
                    predecessor_id="csq_old",
                    successor_id="csq_new",
                    premise_id="asn_premise",
                    dependent_kind="world_assignment",
                    dependent_id="asn_dependent",
                    relation="causes",
                    severity="binding",
                    repair_id="cpr_lineage",
                )
            ],
        )

        planner = build_context(self.cube, world_id="wld_case")
        self.assertEqual(planner["consequence_repairs"][0]["repair_id"], "cpr_lineage")
        perspective = build_context(self.cube, agent_id="user")
        self.assertEqual(perspective["consequence_repairs"], [])
        self.assertIn("consequence_repairs", perspective["omitted"])
        serialized = json.dumps(perspective, sort_keys=True)
        self.assertNotIn("cpr_lineage", serialized)
        self.assertNotIn("csq_old", serialized)
        self.assertNotIn("csq_new", serialized)

        repair_explanation = self.cube.explain("cpr_lineage")
        dependency_edges = {
            (item["kind"], item["id"], item["role"])
            for item in repair_explanation["dependencies"]
        }
        self.assertIn(("consequence_link", "csq_old", "predecessor"), dependency_edges)
        self.assertIn(("consequence_link", "csq_new", "successor"), dependency_edges)
        old_explanation = self.cube.explain("csq_old")
        self.assertIn(
            ("consequence_repair", "cpr_lineage", "replaced_by"),
            {
                (item["kind"], item["id"], item["role"])
                for item in old_explanation["dependents"]
            },
        )
        with self.assertRaises(LacunaError) as caught:
            self.cube.explain("cpr_lineage", agent_id="user")
        self.assertEqual(caught.exception.code, "explanation-not-visible")

        before = json.dumps(self.cube.snapshot(), sort_keys=True)
        self.assertEqual(self.cube.rebuild_projections()["overall_status"], "pass")
        after = json.dumps(self.cube.snapshot(), sort_keys=True)
        self.assertEqual(after, before)

    def test_repair_frontier_is_debt_only_and_world_scoped(self) -> None:
        premise_claim = self.add_assignment("premise", "asn_premise")
        self.add_assignment("dependent", "asn_dependent")
        self.link_assignment("asn_premise", "asn_dependent", consequence_id="csq_old")
        self.assertEqual(self.cube.consequence_repair_frontier(), [])

        impact = self.cube.revision_impact("asn_premise")
        self.cube.apply_operations(
            actor_id="user",
            operations=[
                {
                    "op": "revise_world",
                    "assignment_id": "asn_premise_v2",
                    "revises_assignment_id": "asn_premise",
                    "truth": "false",
                    "expected_impact_sha256": impact["impact_sha256"],
                    "reason": "Create explicit repair debt.",
                },
                {
                    "op": "create_world",
                    "world_id": "wld_elsewhere",
                    "label": "Elsewhere",
                },
            ],
        )
        self.assertEqual(
            self.cube._require_world_assignment("asn_premise_v2")["claim_id"],
            premise_claim,
        )
        all_reviews = self.cube.consequence_repair_frontier()
        self.assertEqual([item["target"]["consequence_id"] for item in all_reviews], ["csq_old"])
        self.assertEqual(
            self.cube.consequence_repair_frontier(world_id="wld_case"),
            all_reviews,
        )
        self.assertEqual(
            self.cube.consequence_repair_frontier(world_id="wld_elsewhere"),
            [],
        )

    def test_chained_replacement_preserves_each_review_and_middle_lineage(self) -> None:
        self.add_assignment("a", "asn_a")
        self.add_assignment("b", "asn_b")
        self.add_assignment("c", "asn_c")
        self.link_assignment("asn_a", "asn_b", consequence_id="csq_0")

        review_0 = self.cube.consequence_repair_review("csq_0")
        self.cube.apply_operations(
            actor_id="user",
            operations=[
                self.replacement_operation(
                    review_0,
                    predecessor_id="csq_0",
                    successor_id="csq_1",
                    premise_id="asn_a",
                    dependent_kind="world_assignment",
                    dependent_id="asn_c",
                    relation="motivates",
                    repair_id="cpr_0_1",
                )
            ],
        )
        review_1 = self.cube.consequence_repair_review("csq_1")
        self.cube.apply_operations(
            actor_id="user",
            operations=[
                self.replacement_operation(
                    review_1,
                    predecessor_id="csq_1",
                    successor_id="csq_2",
                    premise_id="asn_b",
                    dependent_kind="world_assignment",
                    dependent_id="asn_c",
                    relation="constrains",
                    repair_id="cpr_1_2",
                )
            ],
        )
        by_id = {
            item["consequence_id"]: item
            for item in self.cube.consequence_links(include_retired=True)
        }
        self.assertEqual(by_id["csq_0"]["lineage_state"], "replaced")
        self.assertEqual(by_id["csq_1"]["lineage_state"], "middle")
        self.assertEqual(by_id["csq_2"]["lineage_state"], "replacement")
        repairs = self.cube.consequence_repairs()
        self.assertEqual([item["repair_id"] for item in repairs], ["cpr_0_1", "cpr_1_2"])
        self.assertEqual(repairs[0]["review_head"], review_0["head"])
        self.assertEqual(repairs[1]["review_head"], review_1["head"])
        self.assertEqual(self.cube.verify()["overall_status"], "pass")

    def test_verify_binds_repair_projection_to_origin_event(self) -> None:
        self.add_assignment("premise", "asn_premise")
        self.add_assignment("dependent", "asn_dependent")
        self.link_assignment("asn_premise", "asn_dependent", consequence_id="csq_old")
        review = self.cube.consequence_repair_review("csq_old")
        self.cube.apply_operations(
            actor_id="user",
            operations=[
                self.replacement_operation(
                    review,
                    predecessor_id="csq_old",
                    successor_id="csq_new",
                    premise_id="asn_premise",
                    dependent_kind="world_assignment",
                    dependent_id="asn_dependent",
                    relation="causes",
                    repair_id="cpr_lineage",
                )
            ],
        )
        self.cube.conn.execute(
            "UPDATE consequence_repairs SET reason = 'coordinated projection tamper' WHERE repair_id = 'cpr_lineage'"
        )
        self.cube.conn.execute(
            "UPDATE consequence_links SET retirement_reason = 'coordinated projection tamper' WHERE consequence_id = 'csq_old'"
        )
        self.cube.conn.commit()
        verification = self.cube.verify()
        self.assertEqual(verification["overall_status"], "fail")
        self.assertIn(
            "consequence-repair-projection-mismatch",
            {item["code"] for item in verification["errors"]},
        )
        self.assertEqual(self.cube.rebuild_projections()["overall_status"], "pass")
        self.assertEqual(self.cube.consequence_repairs()[0]["reason"], "Replace obsolete dependency custody.")

    def test_schema_four_migration_adds_repair_projection_without_rewriting_head(self) -> None:
        before_head = self.cube.head()
        self.cube.close()
        db_path = self.root / "lacuna.sqlite3"
        conn = sqlite3.connect(db_path)
        try:
            conn.execute("DROP INDEX consequence_repairs_successor_unique_idx")
            conn.execute("DROP INDEX consequence_repairs_predecessor_unique_idx")
            conn.execute("DROP TABLE consequence_repairs")
            conn.execute("DELETE FROM schema_migrations WHERE target_version >= 5")
            conn.execute("PRAGMA user_version = 4")
            conn.execute("UPDATE meta SET value = '4' WHERE key = 'schema_version'")
            conn.commit()
        finally:
            conn.close()

        receipt = Cube.migrate(self.root)
        self.assertEqual(receipt["source_version"], 4)
        self.assertEqual(receipt["target_version"], 8)
        self.assertEqual(receipt["before_head"], before_head)
        self.assertEqual(receipt["after_head"], before_head)
        self.cube = Cube.open(self.root)
        tables = {
            row["name"]
            for row in self.cube.conn.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            ).fetchall()
        }
        self.assertIn("consequence_repairs", tables)
        self.assertEqual(self.cube.verify()["overall_status"], "pass")

    def test_director_turn_can_commit_reviewed_replacement_after_narration_source(self) -> None:
        self.cube.apply_operations(
            actor_id="user",
            operations=[
                {
                    "op": "register_agent",
                    "agent_id": "player",
                    "kind": "human",
                    "label": "Player",
                },
                {
                    "op": "register_agent",
                    "agent_id": "narrator",
                    "kind": "narrator",
                    "label": "Narrator",
                },
            ],
        )
        self.add_assignment("premise", "asn_premise")
        self.add_assignment("dependent", "asn_dependent")
        self.link_assignment("asn_premise", "asn_dependent", consequence_id="csq_old")
        packet = build_turn_packet(
            self.cube,
            audience_id="player",
            actor_id="narrator",
            player_input="Reconsider why the dependent event follows.",
            director=True,
            world_id="wld_case",
        )
        self.assertIn("replace_consequence", packet["write_grant"]["allowed_operations"])
        review = self.cube.consequence_repair_review("csq_old")
        template = packet["response_contract"]["proposal_template"]
        proposal = {
            "schema": "lacuna.turn-proposal.v2",
            "request_id": packet["request_id"],
            "request_source_id": packet["request_source_id"],
            "proposal_id": template["proposal_id"],
            "actor_id": packet["actor_id"],
            "expected_head": packet["expected_head"],
            "player_input_sha256": packet["player_input_sha256"],
            "audience_id": packet["audience_id"],
            "narration_source_id": template["narration_source_id"],
            "narration": "Nothing visible changes while the hidden explanation is reviewed.",
            "revealed_assertion_ids": [],
            "operations": [
                {
                    **self.replacement_operation(
                        review,
                        predecessor_id="csq_old",
                        successor_id="csq_turn_successor",
                        premise_id="asn_premise",
                        dependent_kind="world_assignment",
                        dependent_id="asn_dependent",
                        relation="causes",
                        severity="binding",
                        repair_id="cpr_turn",
                    ),
                    "as": "replacement.edge",
                }
            ],
            "message": "Apply reviewed hidden-world repair.",
        }
        receipt = commit_turn_proposal(
            self.cube,
            proposal,
            include_planner_context=True,
        )
        self.assertEqual(receipt["bindings"]["replacement.edge"], "csq_turn_successor")
        self.assertEqual(receipt["planner_context"]["consequence_repairs"][0]["repair_id"], "cpr_turn")
        event_types = [
            event["event_type"]
            for event in self.cube.events()
            if event["change_id"] == template["proposal_id"]
        ]
        self.assertEqual(event_types, ["source.added", "consequence.replaced"])
        self.assertEqual(self.cube.verify()["overall_status"], "pass")


if __name__ == "__main__":
    unittest.main()
