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
from lacuna.util import deterministic_claim_id


class CommitmentGovernanceTests(unittest.TestCase):
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

    def add_world(self, world_id: str = "wld_case") -> None:
        self.cube.apply_operations(
            actor_id="user",
            operations=[{"op": "create_world", "world_id": world_id, "label": world_id}],
        )

    def assign(
        self,
        claim_id: str,
        *,
        assignment_id: str,
        world_id: str = "wld_case",
        truth: str = "true",
        commitment: str = "tentative",
        commitment_basis: str = "planning",
        commitment_source_id: str | None = None,
    ) -> None:
        operation = {
            "op": "assign_world",
            "assignment_id": assignment_id,
            "world_id": world_id,
            "claim_id": claim_id,
            "truth": truth,
            "commitment": commitment,
            "commitment_basis": commitment_basis,
        }
        if commitment_source_id is not None:
            operation["commitment_source_id"] = commitment_source_id
        self.cube.apply_operations(actor_id="user", operations=[operation])

    def add_question(self, question_id: str = "qst_outcome") -> None:
        self.cube.apply_operations(
            actor_id="user",
            operations=[
                {
                    "op": "open_question",
                    "question_id": question_id,
                    "text": "What follows from this premise?",
                    "opened_by": "user",
                    "visibility": "private",
                }
            ],
        )

    def link_question_consequence(
        self,
        assignment_id: str,
        *,
        consequence_id: str,
        severity: str,
        question_id: str = "qst_outcome",
    ) -> None:
        self.cube.apply_operations(
            actor_id="user",
            operations=[
                {
                    "op": "link_consequence",
                    "consequence_id": consequence_id,
                    "premise_assignment_id": assignment_id,
                    "dependent_kind": "question",
                    "dependent_id": question_id,
                    "relation": "motivates",
                    "severity": severity,
                    "rationale": "The question exists because this latent premise was adopted.",
                }
            ],
        )

    def test_assign_world_cannot_silently_replace_an_occupied_slot(self) -> None:
        claim_id = self.add_claim("door")
        self.add_world()
        self.assign(claim_id, assignment_id="asn_original")
        before_head = self.cube.head()
        before_count = self.cube.event_count()

        with self.assertRaises(LacunaError) as caught:
            self.assign(
                claim_id,
                assignment_id="asn_silent_replacement",
                truth="false",
            )

        self.assertEqual(caught.exception.code, "assignment-slot-occupied")
        self.assertEqual(self.cube.head(), before_head)
        self.assertEqual(self.cube.event_count(), before_count)
        self.assertEqual(self.cube.world_assignments("wld_case")[0]["assignment_id"], "asn_original")

    def test_revision_requires_a_fresh_digest_bound_to_the_current_head(self) -> None:
        claim_id = self.add_claim("lamp")
        self.add_world()
        self.assign(claim_id, assignment_id="asn_lamp")
        impact = self.cube.revision_impact("asn_lamp")
        self.assertEqual(impact["head"], self.cube.head())
        self.assertTrue(impact["review"]["revisable"])

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
        after_intervening = self.cube.head()
        with self.assertRaises(LacunaError) as caught:
            self.cube.apply_operations(
                actor_id="user",
                operations=[
                    {
                        "op": "revise_world",
                        "assignment_id": "asn_lamp_revised",
                        "revises_assignment_id": "asn_lamp",
                        "truth": "false",
                        "expected_impact_sha256": impact["impact_sha256"],
                        "reason": "Try to use stale review custody.",
                    }
                ],
            )
        self.assertEqual(caught.exception.code, "stale-revision-impact")
        self.assertEqual(self.cube.head(), after_intervening)

        fresh = self.cube.revision_impact("asn_lamp")
        self.cube.apply_operations(
            actor_id="user",
            operations=[
                {
                    "op": "revise_world",
                    "assignment_id": "asn_lamp_revised",
                    "revises_assignment_id": "asn_lamp",
                    "truth": "false",
                    "expected_impact_sha256": fresh["impact_sha256"],
                    "reason": "Use a current review receipt.",
                }
            ],
        )
        history = self.cube.assignment_history(world_id="wld_case")
        self.assertEqual([item["assignment_id"] for item in history], ["asn_lamp", "asn_lamp_revised"])
        self.assertFalse(history[0]["active"])
        self.assertTrue(history[1]["active"])
        self.assertEqual(history[1]["revision_of_assignment_id"], "asn_lamp")

    def test_revision_review_survives_unrelated_provenance_in_one_atomic_change(self) -> None:
        claim_id = self.add_claim("window")
        self.add_world()
        self.assign(claim_id, assignment_id="asn_window")
        review = self.cube.revision_impact("asn_window")
        base_head = self.cube.head()

        self.cube.apply_changeset(
            {
                "schema": "lacuna.change-set.v1",
                "change_id": "chg_source_then_revision",
                "actor_id": "user",
                "expected_head": base_head,
                "message": "Attach provenance and apply one reviewed revision.",
                "operations": [
                    {
                        "op": "add_source",
                        "source_id": "src_revision_note",
                        "kind": "document",
                        "label": "Revision note",
                    },
                    {
                        "op": "revise_world",
                        "assignment_id": "asn_window_revised",
                        "revises_assignment_id": "asn_window",
                        "truth": "false",
                        "expected_impact_sha256": review["impact_sha256"],
                        "reason": "The source and reviewed transition share one transaction.",
                    },
                ],
            }
        )
        self.assertEqual(
            [item["assignment_id"] for item in self.cube.assignment_history(world_id="wld_case")],
            ["asn_window", "asn_window_revised"],
        )

    def test_revision_review_detects_prior_semantic_change_in_same_atomic_change(self) -> None:
        claim_id = self.add_claim("gate")
        self.add_world()
        self.assign(claim_id, assignment_id="asn_gate")
        self.add_question("qst_gate")
        review = self.cube.revision_impact("asn_gate")
        base_head = self.cube.head()
        before_events = self.cube.event_count()

        with self.assertRaises(LacunaError) as caught:
            self.cube.apply_changeset(
                {
                    "schema": "lacuna.change-set.v1",
                    "change_id": "chg_link_then_revision",
                    "actor_id": "user",
                    "expected_head": base_head,
                    "message": "A new dependency must invalidate the older impact surface.",
                    "operations": [
                        {
                            "op": "link_consequence",
                            "consequence_id": "csq_gate_question",
                            "premise_assignment_id": "asn_gate",
                            "dependent_kind": "question",
                            "dependent_id": "qst_gate",
                            "relation": "motivates",
                            "severity": "notice",
                            "rationale": "The gate premise now motivates an explicit question.",
                        },
                        {
                            "op": "revise_world",
                            "assignment_id": "asn_gate_revised",
                            "revises_assignment_id": "asn_gate",
                            "truth": "false",
                            "expected_impact_sha256": review["impact_sha256"],
                            "reason": "This must not use a review that predates the new edge.",
                        },
                    ],
                }
            )
        self.assertEqual(caught.exception.code, "stale-revision-impact")
        self.assertEqual(caught.exception.details["review_head"], base_head)
        self.assertNotEqual(caught.exception.details["current_head"], base_head)
        self.assertEqual(self.cube.head(), base_head)
        self.assertEqual(self.cube.event_count(), before_events)
        self.assertEqual(self.cube.consequence_links(), [])

    def test_hard_commitment_is_a_stop_sign_and_requires_durable_basis(self) -> None:
        claim_id = self.add_claim("culprit")
        self.add_world()
        with self.assertRaises(LacunaError) as caught:
            self.assign(
                claim_id,
                assignment_id="asn_bad_hard",
                commitment="hard",
                commitment_basis="planning",
            )
        self.assertEqual(caught.exception.code, "hard-commitment-needs-durable-basis")

        self.assign(
            claim_id,
            assignment_id="asn_precommitted",
            commitment="hard",
            commitment_basis="precommitment",
        )
        impact = self.cube.revision_impact("asn_precommitted")
        self.assertFalse(impact["review"]["revisable"])
        self.assertIn("hard-commitment", {item["code"] for item in impact["blockers"]})
        with self.assertRaises(LacunaError) as caught:
            self.cube.apply_operations(
                actor_id="user",
                operations=[
                    {
                        "op": "revise_world",
                        "assignment_id": "asn_illegal_revision",
                        "revises_assignment_id": "asn_precommitted",
                        "truth": "false",
                        "expected_impact_sha256": impact["impact_sha256"],
                        "reason": "This should require a fork, not mutation.",
                    }
                ],
            )
        self.assertEqual(caught.exception.code, "revision-blocked")

    def test_commitment_rises_one_boundary_at_a_time_and_records_custody(self) -> None:
        claim_id = self.add_claim("bridge")
        self.add_world()
        self.assign(claim_id, assignment_id="asn_bridge")

        with self.assertRaises(LacunaError) as caught:
            self.cube.apply_operations(
                actor_id="user",
                operations=[
                    {
                        "op": "raise_commitment",
                        "assignment_id": "asn_bridge",
                        "commitment": "firm",
                        "basis": "authored",
                        "rationale": "Attempt to skip soft review.",
                    }
                ],
            )
        self.assertEqual(caught.exception.code, "commitment-transition-not-adjacent")

        transitions = [
            ("cmt_soft", "soft", "planning"),
            ("cmt_firm", "firm", "authored"),
            ("cmt_hard", "hard", "authored"),
        ]
        for transition_id, target, basis in transitions:
            self.cube.apply_operations(
                actor_id="user",
                operations=[
                    {
                        "op": "raise_commitment",
                        "transition_id": transition_id,
                        "assignment_id": "asn_bridge",
                        "commitment": target,
                        "basis": basis,
                        "rationale": f"Governed transition to {target}.",
                    }
                ],
            )
        current = self.cube.world_assignments("wld_case")[0]
        self.assertEqual(current["commitment"], "hard")
        self.assertEqual(current["commitment_basis"], "authored")
        self.assertEqual(
            [item["to_commitment"] for item in self.cube.commitment_transitions(assignment_id="asn_bridge")],
            ["soft", "firm", "hard"],
        )
        with self.assertRaises(LacunaError) as caught:
            self.cube.apply_operations(
                actor_id="user",
                operations=[
                    {
                        "op": "raise_commitment",
                        "assignment_id": "asn_bridge",
                        "commitment": "firm",
                        "basis": "authored",
                        "rationale": "Attempt a downgrade.",
                    }
                ],
            )
        self.assertEqual(caught.exception.code, "commitment-not-raised")

    def test_legacy_commitment_basis_is_reserved_for_migration_and_replay(self) -> None:
        claim_id = self.add_claim("legacy-marker")
        self.add_world()
        before_head = self.cube.head()
        before_count = self.cube.event_count()
        with self.assertRaises(LacunaError) as caught:
            self.assign(
                claim_id,
                assignment_id="asn_false_legacy",
                commitment="tentative",
                commitment_basis="legacy",
            )
        self.assertEqual(caught.exception.code, "reserved-legacy-commitment-basis")
        self.assertEqual(self.cube.head(), before_head)
        self.assertEqual(self.cube.event_count(), before_count)
        self.assertEqual(self.cube.world_assignments("wld_case"), [])

    def test_evidence_and_disclosure_commitment_bases_require_sources(self) -> None:
        claim_id = self.add_claim("signal")
        self.add_world()
        with self.assertRaises(LacunaError) as caught:
            self.assign(
                claim_id,
                assignment_id="asn_unsourced",
                commitment="soft",
                commitment_basis="evidence",
            )
        self.assertEqual(caught.exception.code, "commitment-source-required")

        self.cube.apply_operations(
            actor_id="user",
            operations=[
                {
                    "op": "add_source",
                    "source_id": "src_signal",
                    "kind": "sensor",
                    "label": "Signal trace",
                }
            ],
        )
        self.assign(
            claim_id,
            assignment_id="asn_sourced",
            commitment="soft",
            commitment_basis="evidence",
            commitment_source_id="src_signal",
        )
        self.assertEqual(
            self.cube.world_assignments("wld_case")[0]["commitment_source_id"],
            "src_signal",
        )

    def test_revision_guards_match_transitive_binding_impact_policy(self) -> None:
        premise_claim = self.add_claim("premise")
        bridge_claim = self.add_claim("bridge")
        self.add_world()
        self.assign(premise_claim, assignment_id="asn_premise")
        self.assign(bridge_claim, assignment_id="asn_bridge")
        self.add_question("qst_binding_outcome")
        self.cube.apply_operations(
            actor_id="user",
            operations=[
                {
                    "op": "link_consequence",
                    "consequence_id": "csq_premise_bridge",
                    "premise_assignment_id": "asn_premise",
                    "dependent_kind": "world_assignment",
                    "dependent_id": "asn_bridge",
                    "relation": "causes",
                    "severity": "notice",
                    "rationale": "The premise establishes the intermediate assignment.",
                },
                {
                    "op": "link_consequence",
                    "consequence_id": "csq_bridge_outcome",
                    "premise_assignment_id": "asn_bridge",
                    "dependent_kind": "question",
                    "dependent_id": "qst_binding_outcome",
                    "relation": "promises",
                    "severity": "binding",
                    "rationale": "The intermediate assignment creates a binding promise.",
                },
            ],
        )

        impact = self.cube.revision_impact("asn_premise")
        self.assertFalse(impact["review"]["revisable"])
        self.assertIn("csq_bridge_outcome", impact["blockers"][0]["consequence_ids"])
        guard = next(
            item
            for item in self.cube.revision_guards()
            if item["assignment_id"] == "asn_premise"
        )
        self.assertTrue(guard["revision_blocked"])
        self.assertIn("binding-consequence", guard["revision_blockers"])
        self.assertEqual(guard["incident_consequence_counts"]["binding"], 0)
        self.assertEqual(guard["reachable_consequence_counts"]["binding"], 1)
        context_guard = next(
            item
            for item in build_context(self.cube)["revision_guards"]
            if item["assignment_id"] == "asn_premise"
        )
        self.assertEqual(context_guard["revision_blockers"], guard["revision_blockers"])

    def test_binding_consequence_blocks_revision_until_explicitly_retired(self) -> None:
        claim_id = self.add_claim("oath")
        self.add_world()
        self.assign(claim_id, assignment_id="asn_oath")
        self.add_question()
        self.link_question_consequence(
            "asn_oath", consequence_id="csq_binding", severity="binding"
        )

        blocked = self.cube.revision_impact("asn_oath")
        self.assertIn("binding-consequence", {item["code"] for item in blocked["blockers"]})
        with self.assertRaises(LacunaError) as caught:
            self.cube.apply_operations(
                actor_id="user",
                operations=[
                    {
                        "op": "revise_world",
                        "assignment_id": "asn_oath_revised",
                        "revises_assignment_id": "asn_oath",
                        "truth": "false",
                        "expected_impact_sha256": blocked["impact_sha256"],
                        "reason": "Binding consequences should prevent this.",
                    }
                ],
            )
        self.assertEqual(caught.exception.code, "revision-blocked")

        self.cube.apply_operations(
            actor_id="user",
            operations=[
                {
                    "op": "retire_consequence",
                    "consequence_id": "csq_binding",
                    "reason": "Repair plan accepted before premise revision.",
                }
            ],
        )
        impact = self.cube.revision_impact("asn_oath")
        self.assertTrue(impact["review"]["revisable"])
        self.cube.apply_operations(
            actor_id="user",
            operations=[
                {
                    "op": "revise_world",
                    "assignment_id": "asn_oath_revised",
                    "revises_assignment_id": "asn_oath",
                    "truth": "false",
                    "expected_impact_sha256": impact["impact_sha256"],
                    "reason": "Binding custody was explicitly discharged.",
                }
            ],
        )
        retired = self.cube.consequence_links(include_retired=True)[0]
        self.assertIsNotNone(retired["ended_seq"])
        self.assertFalse(retired["repair_required"])

    def test_material_consequence_survives_revision_as_visible_repair_debt(self) -> None:
        claim_id = self.add_claim("secret_passage")
        self.add_world()
        self.assign(claim_id, assignment_id="asn_passage")
        self.add_question()
        self.link_question_consequence(
            "asn_passage", consequence_id="csq_material", severity="material"
        )
        impact = self.cube.revision_impact("asn_passage")
        self.assertTrue(impact["review"]["revisable"])
        self.assertIn(
            "csq_material",
            impact["review"]["incident_consequence_disposition"]["retained_consequence_ids"],
        )

        self.cube.apply_operations(
            actor_id="user",
            operations=[
                {
                    "op": "revise_world",
                    "assignment_id": "asn_passage_revised",
                    "revises_assignment_id": "asn_passage",
                    "truth": "false",
                    "expected_impact_sha256": impact["impact_sha256"],
                    "reason": "Change the hidden premise while preserving its downstream debt.",
                }
            ],
        )
        link = self.cube.consequence_links()[0]
        self.assertTrue(link["repair_required"])
        self.assertFalse(link["premise_active"])
        orphaned = [
            item for item in self.cube.conflicts() if item["kind"] == "orphaned-consequence"
        ]
        self.assertEqual([item["consequence_id"] for item in orphaned], ["csq_material"])
        status = self.cube.status()
        self.assertEqual(status["orphaned_consequence_count"], 1)
        self.assertEqual(self.cube.verify()["overall_status"], "pass")

        before = self.cube.snapshot()
        rebuilt = self.cube.rebuild_projections()
        self.assertEqual(rebuilt["overall_status"], "pass")
        after = self.cube.snapshot()
        self.assertEqual(before, after)

    def test_repair_review_replaces_orphaned_consequence_with_auditable_lineage(self) -> None:
        claim_id = self.add_claim("hidden_bridge")
        self.add_world()
        self.assign(claim_id, assignment_id="asn_bridge")
        self.add_question("qst_bridge_effect")
        self.link_question_consequence(
            "asn_bridge",
            consequence_id="csq_bridge_effect",
            severity="material",
            question_id="qst_bridge_effect",
        )

        impact = self.cube.revision_impact("asn_bridge")
        self.cube.apply_operations(
            actor_id="user",
            operations=[
                {
                    "op": "revise_world",
                    "assignment_id": "asn_bridge_revised",
                    "revises_assignment_id": "asn_bridge",
                    "truth": "false",
                    "expected_impact_sha256": impact["impact_sha256"],
                    "reason": "The bridge was never present in this candidate world.",
                }
            ],
        )

        stale_review = self.cube.consequence_repair_review("csq_bridge_effect")
        self.assertEqual(stale_review["review"]["mode"], "orphan-repair")
        self.assertTrue(stale_review["review"]["replaceable"])
        self.assertEqual(
            stale_review["known_successors"]["premise_assignment_ids"],
            ["asn_bridge_revised"],
        )

        self.cube.apply_operations(
            actor_id="user",
            operations=[
                {
                    "op": "add_source",
                    "source_id": "src_intervening_repair",
                    "kind": "document",
                    "label": "Intervening repair custody",
                }
            ],
        )
        before_head = self.cube.head()
        before_count = self.cube.event_count()
        with self.assertRaises(LacunaError) as caught:
            self.cube.apply_operations(
                actor_id="user",
                operations=[
                    {
                        "op": "replace_consequence",
                        "repair_id": "cpr_bridge_effect",
                        "consequence_id": "csq_bridge_effect_repaired",
                        "replaces_consequence_id": "csq_bridge_effect",
                        "premise_assignment_id": "asn_bridge_revised",
                        "dependent_kind": "question",
                        "dependent_id": "qst_bridge_effect",
                        "relation": "motivates",
                        "severity": "material",
                        "rationale": "The absence of the bridge now motivates the same open question.",
                        "expected_repair_sha256": stale_review["repair_review_sha256"],
                        "reason": "Relink the consequence to the revised premise.",
                    }
                ],
            )
        self.assertEqual(caught.exception.code, "stale-consequence-repair-review")
        self.assertEqual(self.cube.head(), before_head)
        self.assertEqual(self.cube.event_count(), before_count)

        review = self.cube.consequence_repair_review("csq_bridge_effect")
        # An unrelated provenance operation may precede the replacement in the
        # same atomic change; review authority remains bound to the change's
        # initial head rather than becoming stale after operation zero.
        self.cube.apply_operations(
            actor_id="user",
            operations=[
                {
                    "op": "add_source",
                    "source_id": "src_repair_note",
                    "kind": "document",
                    "label": "Repair note",
                },
                {
                    "op": "replace_consequence",
                    "repair_id": "cpr_bridge_effect",
                    "consequence_id": "csq_bridge_effect_repaired",
                    "replaces_consequence_id": "csq_bridge_effect",
                    "premise_assignment_id": "asn_bridge_revised",
                    "dependent_kind": "question",
                    "dependent_id": "qst_bridge_effect",
                    "relation": "motivates",
                    "severity": "material",
                    "source_id": "src_repair_note",
                    "rationale": "The absence of the bridge now motivates the same open question.",
                    "expected_repair_sha256": review["repair_review_sha256"],
                    "reason": "Relink the consequence to the revised premise.",
                },
            ],
        )

        links = {
            item["consequence_id"]: item
            for item in self.cube.consequence_links(include_retired=True)
        }
        predecessor = links["csq_bridge_effect"]
        successor = links["csq_bridge_effect_repaired"]
        self.assertIsNotNone(predecessor["ended_seq"])
        self.assertEqual(predecessor["lineage_state"], "replaced")
        self.assertEqual(
            predecessor["replacement_consequence_id"],
            "csq_bridge_effect_repaired",
        )
        self.assertIsNone(successor["ended_seq"])
        self.assertEqual(successor["lineage_state"], "replacement")
        self.assertEqual(successor["replaces_consequence_id"], "csq_bridge_effect")
        self.assertFalse(successor["repair_required"])
        self.assertTrue(successor["premise_active"])

        repairs = self.cube.consequence_repairs()
        self.assertEqual(len(repairs), 1)
        self.assertEqual(repairs[0]["repair_id"], "cpr_bridge_effect")
        self.assertEqual(repairs[0]["review_sha256"], review["repair_review_sha256"])
        self.assertEqual(self.cube.status()["consequence_repair_count"], 1)
        self.assertEqual(self.cube.status()["orphaned_consequence_count"], 0)
        self.assertFalse(
            any(item["kind"] == "orphaned-consequence" for item in self.cube.conflicts())
        )

        explanation = self.cube.explain("cpr_bridge_effect")
        self.assertEqual(explanation["target"]["kind"], "consequence_repair")
        self.assertEqual(
            {(item["kind"], item["id"], item["role"]) for item in explanation["dependencies"]},
            {
                ("consequence_link", "csq_bridge_effect", "predecessor"),
                ("consequence_link", "csq_bridge_effect_repaired", "successor"),
            },
        )
        with self.assertRaises(LacunaError) as caught:
            self.cube.explain("cpr_bridge_effect", agent_id="user")
        self.assertEqual(caught.exception.code, "explanation-not-visible")
        perspective = build_context(self.cube, agent_id="user")
        self.assertEqual(perspective["consequence_repairs"], [])
        self.assertIn("consequence_repairs", perspective["omitted"])
        serialized = json.dumps(perspective, sort_keys=True)
        self.assertNotIn("cpr_bridge_effect", serialized)
        self.assertNotIn("csq_bridge_effect_repaired", serialized)

        before = self.cube.snapshot()
        self.assertEqual(self.cube.verify()["overall_status"], "pass")
        rebuilt = self.cube.rebuild_projections()
        self.assertEqual(rebuilt["overall_status"], "pass")
        self.assertEqual(before, self.cube.snapshot())

    def test_consequence_replacement_refuses_cycles_and_unchanged_successors(self) -> None:
        claim_ids = [self.add_claim(name) for name in ("cause_a", "cause_b", "cause_c")]
        self.add_world()
        for assignment_id, claim_id in zip(
            ("asn_a", "asn_b", "asn_c"), claim_ids, strict=True
        ):
            self.assign(claim_id, assignment_id=assignment_id)
        self.cube.apply_operations(
            actor_id="user",
            operations=[
                {
                    "op": "link_consequence",
                    "consequence_id": "csq_a_b",
                    "premise_assignment_id": "asn_a",
                    "dependent_kind": "world_assignment",
                    "dependent_id": "asn_b",
                    "relation": "causes",
                    "severity": "material",
                    "rationale": "A currently causes B.",
                },
                {
                    "op": "link_consequence",
                    "consequence_id": "csq_b_c",
                    "premise_assignment_id": "asn_b",
                    "dependent_kind": "world_assignment",
                    "dependent_id": "asn_c",
                    "relation": "causes",
                    "severity": "material",
                    "rationale": "B currently causes C.",
                },
            ],
        )
        review = self.cube.consequence_repair_review("csq_a_b")
        before_head = self.cube.head()
        before_count = self.cube.event_count()
        with self.assertRaises(LacunaError) as caught:
            self.cube.apply_operations(
                actor_id="user",
                operations=[
                    {
                        "op": "replace_consequence",
                        "repair_id": "cpr_cycle",
                        "consequence_id": "csq_c_b",
                        "replaces_consequence_id": "csq_a_b",
                        "premise_assignment_id": "asn_c",
                        "dependent_kind": "world_assignment",
                        "dependent_id": "asn_b",
                        "relation": "causes",
                        "severity": "material",
                        "rationale": "This would make B and C cyclic.",
                        "expected_repair_sha256": review["repair_review_sha256"],
                        "reason": "Attempt a cyclic rewrite.",
                    }
                ],
            )
        self.assertEqual(caught.exception.code, "consequence-cycle")
        self.assertEqual(self.cube.head(), before_head)
        self.assertEqual(self.cube.event_count(), before_count)

        fresh = self.cube.consequence_repair_review("csq_a_b")
        with self.assertRaises(LacunaError) as caught:
            self.cube.apply_operations(
                actor_id="user",
                operations=[
                    {
                        "op": "replace_consequence",
                        "repair_id": "cpr_unchanged",
                        "consequence_id": "csq_a_b_clone",
                        "replaces_consequence_id": "csq_a_b",
                        "premise_assignment_id": "asn_a",
                        "dependent_kind": "world_assignment",
                        "dependent_id": "asn_b",
                        "relation": "causes",
                        "severity": "material",
                        "rationale": "A currently causes B.",
                        "expected_repair_sha256": fresh["repair_review_sha256"],
                        "reason": "Attempt a no-op replacement.",
                    }
                ],
            )
        self.assertEqual(caught.exception.code, "consequence-replacement-unchanged")
        self.assertEqual(self.cube.head(), before_head)
        self.assertEqual(self.cube.event_count(), before_count)

    def test_assignment_consequence_graph_refuses_cycles_atomically(self) -> None:
        left = self.add_claim("left")
        right = self.add_claim("right")
        self.add_world()
        self.assign(left, assignment_id="asn_left")
        self.assign(right, assignment_id="asn_right")
        self.cube.apply_operations(
            actor_id="user",
            operations=[
                {
                    "op": "link_consequence",
                    "consequence_id": "csq_left_right",
                    "premise_assignment_id": "asn_left",
                    "dependent_kind": "world_assignment",
                    "dependent_id": "asn_right",
                    "relation": "causes",
                    "severity": "material",
                    "rationale": "Left entails a downstream assignment in this authored hypothesis.",
                }
            ],
        )
        before_head = self.cube.head()
        before_count = self.cube.event_count()
        with self.assertRaises(LacunaError) as caught:
            self.cube.apply_operations(
                actor_id="user",
                operations=[
                    {
                        "op": "link_consequence",
                        "consequence_id": "csq_right_left",
                        "premise_assignment_id": "asn_right",
                        "dependent_kind": "world_assignment",
                        "dependent_id": "asn_left",
                        "relation": "causes",
                        "severity": "material",
                        "rationale": "This would close a causal cycle.",
                    }
                ],
            )
        self.assertEqual(caught.exception.code, "consequence-cycle")
        self.assertEqual(self.cube.head(), before_head)
        self.assertEqual(self.cube.event_count(), before_count)
        self.assertEqual(len(self.cube.consequence_links()), 1)

    def test_context_firewall_hides_commitment_and_consequence_custody(self) -> None:
        claim_id = self.add_claim("hidden_identity")
        self.add_world("wld_hidden")
        self.assign(
            claim_id,
            assignment_id="asn_hidden_identity",
            world_id="wld_hidden",
            commitment="soft",
            commitment_basis="authored",
        )
        self.add_question("qst_hidden_effect")
        self.link_question_consequence(
            "asn_hidden_identity",
            consequence_id="csq_hidden_effect",
            severity="material",
            question_id="qst_hidden_effect",
        )

        planner = build_context(self.cube, world_id="wld_hidden")
        self.assertEqual(planner["consequence_links"][0]["consequence_id"], "csq_hidden_effect")
        self.assertEqual(planner["revision_guards"][0]["assignment_id"], "asn_hidden_identity")

        perspective = build_context(self.cube, agent_id="user")
        self.assertEqual(perspective["consequence_links"], [])
        self.assertEqual(perspective["revision_guards"], [])
        self.assertIn("consequence_links", perspective["omitted"])
        self.assertIn("revision_guards", perspective["omitted"])
        serialized = json.dumps(perspective, sort_keys=True)
        self.assertNotIn("csq_hidden_effect", serialized)
        self.assertNotIn("asn_hidden_identity", serialized)
        self.assertNotIn("wld_hidden", serialized)

    def test_explanations_include_governed_revision_and_consequence_edges(self) -> None:
        claim_id = self.add_claim("mask")
        self.add_world()
        self.assign(claim_id, assignment_id="asn_mask")
        self.add_question()
        self.link_question_consequence(
            "asn_mask", consequence_id="csq_mask_question", severity="material"
        )
        explanation = self.cube.explain("asn_mask")
        self.assertIn(
            ("consequence_link", "csq_mask_question", "explicit_consequence"),
            {(item["kind"], item["id"], item["role"]) for item in explanation["dependents"]},
        )
        with self.assertRaises(LacunaError) as caught:
            self.cube.explain("csq_mask_question", agent_id="user")
        self.assertEqual(caught.exception.code, "explanation-not-visible")

    def test_open_refuses_triggers_views_and_wrong_partial_index_predicates(self) -> None:
        self.cube.close()
        db_path = self.root / "lacuna.sqlite3"
        conn = sqlite3.connect(db_path)
        try:
            conn.execute("DROP INDEX consequence_links_active_unique_idx")
            conn.execute(
                """CREATE UNIQUE INDEX consequence_links_active_unique_idx
                   ON consequence_links(
                       premise_assignment_id, dependent_kind, dependent_id, relation
                   ) WHERE ended_seq IS NOT NULL"""
            )
            conn.execute(
                "CREATE VIEW hidden_assignment_count AS SELECT COUNT(*) AS count FROM world_assignments"
            )
            conn.execute(
                """CREATE TRIGGER rewrite_world_weight AFTER INSERT ON worlds
                   BEGIN UPDATE worlds SET weight = 0.5 WHERE world_id = NEW.world_id; END"""
            )
            conn.commit()
        finally:
            conn.close()

        with self.assertRaises(LacunaError) as caught:
            Cube.open(self.root)
        self.assertEqual(caught.exception.code, "database-schema-shape-mismatch")
        errors = caught.exception.details["errors"]
        self.assertIn("index-shape", {item["kind"] for item in errors})
        auxiliary = next(
            item for item in errors if item["kind"] == "auxiliary-schema-objects"
        )
        self.assertEqual(
            {(item["type"], item["name"]) for item in auxiliary["actual"]},
            {("trigger", "rewrite_world_weight"), ("view", "hidden_assignment_count")},
        )
        self.cube = Cube.init(Path(self.temporary.name) / "replacement")

    def test_schema_three_migration_adds_governance_without_rewriting_head(self) -> None:
        before_head = self.cube.head()
        self.cube.close()
        db_path = self.root / "lacuna.sqlite3"
        conn = sqlite3.connect(db_path)
        try:
            conn.execute("PRAGMA foreign_keys = OFF")
            conn.execute("DROP TABLE consequence_links")
            conn.execute("DROP TABLE commitment_transitions")
            conn.execute("DROP INDEX world_assignments_revision_idx")
            conn.execute("ALTER TABLE world_assignments RENAME TO world_assignments_v4")
            conn.execute(
                """CREATE TABLE world_assignments (
                       assignment_id TEXT PRIMARY KEY,
                       world_id TEXT NOT NULL REFERENCES worlds(world_id),
                       claim_id TEXT NOT NULL REFERENCES claims(claim_id),
                       truth TEXT NOT NULL,
                       commitment TEXT NOT NULL,
                       confidence REAL,
                       rationale TEXT,
                       source_assertion_id TEXT REFERENCES assertions(assertion_id),
                       timeline_id TEXT NOT NULL,
                       valid_from INTEGER,
                       valid_to INTEGER,
                       inherited_from_assignment_id TEXT,
                       created_seq INTEGER NOT NULL,
                       ended_seq INTEGER
                   )"""
            )
            conn.execute(
                """INSERT INTO world_assignments(
                       assignment_id, world_id, claim_id, truth, commitment,
                       confidence, rationale, source_assertion_id, timeline_id,
                       valid_from, valid_to, inherited_from_assignment_id, created_seq, ended_seq
                   ) SELECT assignment_id, world_id, claim_id, truth, commitment,
                            confidence, rationale, source_assertion_id, timeline_id,
                            valid_from, valid_to, inherited_from_assignment_id, created_seq, ended_seq
                     FROM world_assignments_v4"""
            )
            conn.execute("DROP TABLE world_assignments_v4")
            conn.execute(
                "CREATE INDEX world_assignments_current_idx ON world_assignments(world_id, claim_id, ended_seq)"
            )
            conn.execute("DELETE FROM schema_migrations WHERE target_version >= 4")
            conn.execute("PRAGMA user_version = 3")
            conn.execute("UPDATE meta SET value = '3' WHERE key = 'schema_version'")
            conn.commit()
        finally:
            conn.close()

        receipt = Cube.migrate(self.root)
        self.assertEqual(receipt["source_version"], 3)
        self.assertEqual(receipt["target_version"], 8)
        self.assertEqual(receipt["before_head"], before_head)
        self.assertEqual(receipt["after_head"], before_head)
        self.cube = Cube.open(self.root)
        columns = {
            row["name"]
            for row in self.cube.conn.execute("PRAGMA table_info(world_assignments)").fetchall()
        }
        self.assertTrue(
            {
                "commitment_basis",
                "commitment_source_id",
                "revision_of_assignment_id",
                "revision_reason",
                "revision_impact_sha256",
            }
            <= columns
        )
        self.assertEqual(self.cube.verify()["overall_status"], "pass")

    def test_migration_rejects_forward_provisioned_objects_with_the_wrong_shape(self) -> None:
        malformed_root = Path(self.temporary.name) / "malformed"
        malformed = Cube.init(malformed_root)
        before_head = malformed.head()
        malformed.close()
        db_path = malformed_root / "lacuna.sqlite3"
        conn = sqlite3.connect(db_path)
        try:
            conn.execute("PRAGMA foreign_keys = OFF")
            conn.execute("DROP TABLE consequence_links")
            conn.execute(
                """CREATE TABLE consequence_links (
                       consequence_id TEXT PRIMARY KEY,
                       premise_assignment_id TEXT NOT NULL,
                       dependent_kind TEXT NOT NULL,
                       dependent_id TEXT NOT NULL,
                       relation TEXT NOT NULL,
                       severity TEXT NOT NULL,
                       source_id TEXT,
                       rationale INTEGER NOT NULL,
                       created_seq INTEGER NOT NULL,
                       ended_seq INTEGER,
                       retirement_reason TEXT
                   )"""
            )
            conn.execute("DELETE FROM schema_migrations WHERE target_version >= 4")
            conn.execute("PRAGMA user_version = 3")
            conn.execute("UPDATE meta SET value = '3' WHERE key = 'schema_version'")
            conn.commit()
        finally:
            conn.close()

        with self.assertRaises(LacunaError) as caught:
            Cube.migrate(malformed_root)
        self.assertEqual(caught.exception.code, "database-schema-shape-mismatch")
        kinds = {item["kind"] for item in caught.exception.details["errors"]}
        self.assertIn("column-shape", kinds)
        self.assertIn("foreign-key-set", kinds)

        conn = sqlite3.connect(db_path)
        try:
            self.assertEqual(conn.execute("PRAGMA user_version").fetchone()[0], 3)
            self.assertEqual(
                conn.execute("SELECT value FROM meta WHERE key = 'schema_version'").fetchone()[0],
                "3",
            )
            self.assertEqual(
                conn.execute("SELECT value FROM meta WHERE key = 'head'").fetchone()[0],
                before_head,
            )
            self.assertEqual(
                conn.execute(
                    "SELECT COUNT(*) FROM schema_migrations WHERE target_version = 4"
                ).fetchone()[0],
                0,
            )
        finally:
            conn.close()


if __name__ == "__main__":
    unittest.main()
