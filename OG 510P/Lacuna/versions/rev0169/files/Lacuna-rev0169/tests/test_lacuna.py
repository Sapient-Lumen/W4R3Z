from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from lacuna.cli import demo_operations
from lacuna.errors import LacunaError
from lacuna.render import context_markdown
from lacuna.store import Cube
from lacuna.util import deterministic_claim_id


class LacunaTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "cube"
        cube = Cube.init(self.root)
        cube.close()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_initial_cube_verifies(self) -> None:
        with Cube.open(self.root) as cube:
            report = cube.verify()
            self.assertEqual(report["overall_status"], "pass")
            self.assertEqual(report["event_count"], 3)
            self.assertEqual(cube.status()["agent_count"], 2)

    def test_close_is_idempotent_and_cube_reopens_cleanly(self) -> None:
        cube = Cube.open(self.root)
        cube.close()
        cube.close()
        with Cube.open(self.root) as reopened:
            self.assertEqual(reopened.verify()["overall_status"], "pass")

    def test_stale_change_set_is_atomic(self) -> None:
        with Cube.open(self.root) as cube:
            before_head = cube.head()
            before_count = cube.event_count()
            with self.assertRaises(LacunaError) as caught:
                cube.apply_changeset(
                    {
                        "schema": "lacuna.change-set.v1",
                        "actor_id": "user",
                        "expected_head": "0" * 64,
                        "operations": [
                            {
                                "op": "register_agent",
                                "agent_id": "mira",
                                "kind": "character",
                                "label": "Mira",
                            }
                        ],
                    }
                )
            self.assertEqual(caught.exception.code, "stale-head")
            self.assertEqual(cube.head(), before_head)
            self.assertEqual(cube.event_count(), before_count)
            self.assertFalse(cube._exists("agents", "agent_id", "mira"))

    def test_anchor_blocks_incompatible_world_assignment(self) -> None:
        claim_id = deterministic_claim_id("door", "is_open", True, "world")
        with Cube.open(self.root) as cube:
            cube.apply_operations(
                actor_id="user",
                operations=[
                    {"op": "register_agent", "agent_id": "narrator", "kind": "narrator", "label": "Narrator"},
                    {
                        "op": "declare_claim",
                        "claim_id": claim_id,
                        "subject": "door",
                        "predicate": "is_open",
                        "object": True,
                        "scope": "world",
                    },
                    {
                        "op": "record_assertion",
                        "assertion_id": "ast.door",
                        "claim_id": claim_id,
                        "assertor_id": "narrator",
                        "stance": "true",
                        "basis": "observation",
                        "standing": "anchored",
                        "visibility": "public",
                    },
                    {"op": "create_world", "world_id": "world.one", "label": "One"},
                ],
            )
            count = cube.event_count()
            with self.assertRaises(LacunaError) as caught:
                cube.apply_operations(
                    actor_id="user",
                    operations=[
                        {
                            "op": "assign_world",
                            "world_id": "world.one",
                            "claim_id": claim_id,
                            "truth": "false",
                            "commitment": "soft",
                        }
                    ],
                )
            self.assertEqual(caught.exception.code, "world-contradicts-anchor")
            self.assertEqual(cube.event_count(), count)
            self.assertEqual(cube.world_assignments("world.one"), [])

    def test_consensus_is_intersection_of_live_worlds(self) -> None:
        claim_id = deterministic_claim_id("lantern", "is_lit", True, "world")
        with Cube.open(self.root) as cube:
            cube.apply_operations(
                actor_id="user",
                operations=[
                    {
                        "op": "declare_claim",
                        "claim_id": claim_id,
                        "subject": "lantern",
                        "predicate": "is_lit",
                        "object": True,
                        "scope": "world",
                    },
                    {"op": "create_world", "world_id": "world.a", "label": "A"},
                    {"op": "create_world", "world_id": "world.b", "label": "B"},
                    {"op": "assign_world", "world_id": "world.a", "claim_id": claim_id, "truth": "true"},
                    {"op": "assign_world", "world_id": "world.b", "claim_id": claim_id, "truth": "true"},
                ],
            )
            canon = cube.canon()
            self.assertEqual(len(canon["cross_world_consensus"]), 1)
            self.assertEqual(canon["cross_world_consensus"][0]["claim_id"], claim_id)
            current = cube.world_assignments("world.b")[0]
            impact = cube.revision_impact(current["assignment_id"])
            cube.apply_operations(
                actor_id="user",
                operations=[
                    {
                        "op": "revise_world",
                        "assignment_id": "asn.world-b.revised",
                        "revises_assignment_id": current["assignment_id"],
                        "truth": "false",
                        "expected_impact_sha256": impact["impact_sha256"],
                        "reason": "Split the candidate worlds for the consensus test.",
                    }
                ],
            )
            self.assertEqual(cube.canon()["cross_world_consensus"], [])

    def test_private_belief_is_perspective_scoped(self) -> None:
        claim_id = deterministic_claim_id("key", "is_cursed", True, "belief")
        with Cube.open(self.root) as cube:
            cube.apply_operations(
                actor_id="user",
                operations=[
                    {"op": "register_agent", "agent_id": "alice", "kind": "character", "label": "Alice"},
                    {"op": "register_agent", "agent_id": "bob", "kind": "character", "label": "Bob"},
                    {
                        "op": "declare_claim",
                        "claim_id": claim_id,
                        "subject": "key",
                        "predicate": "is_cursed",
                        "object": True,
                        "scope": "belief",
                    },
                    {
                        "op": "record_assertion",
                        "assertion_id": "ast.alice.key",
                        "claim_id": claim_id,
                        "assertor_id": "alice",
                        "perspective_id": "alice",
                        "stance": "true",
                        "basis": "belief",
                        "standing": "accepted",
                        "visibility": "private",
                    },
                ],
            )
            alice = cube.perspective("alice")
            bob = cube.perspective("bob")
            self.assertEqual(len(alice["assertions"]), 1)
            self.assertEqual(len(bob["assertions"]), 0)

    def test_supersession_ends_without_deleting_history(self) -> None:
        claim_id = deterministic_claim_id("clock", "is_stopped", True, "world")
        with Cube.open(self.root) as cube:
            cube.apply_operations(
                actor_id="user",
                operations=[
                    {
                        "op": "declare_claim",
                        "claim_id": claim_id,
                        "subject": "clock",
                        "predicate": "is_stopped",
                        "object": True,
                        "scope": "world",
                    },
                    {
                        "op": "record_assertion",
                        "assertion_id": "ast.clock.old",
                        "claim_id": claim_id,
                        "assertor_id": "user",
                        "stance": "true",
                        "basis": "inference",
                        "standing": "accepted",
                        "visibility": "private",
                    },
                    {
                        "op": "record_assertion",
                        "assertion_id": "ast.clock.new",
                        "claim_id": claim_id,
                        "assertor_id": "user",
                        "stance": "false",
                        "basis": "observation",
                        "standing": "accepted",
                        "visibility": "private",
                        "supersedes_id": "ast.clock.old",
                    },
                ],
            )
            active_ids = {item["assertion_id"] for item in cube.active_assertions()}
            self.assertEqual(active_ids, {"ast.clock.new"})
            old = cube.conn.execute("SELECT ended_seq FROM assertions WHERE assertion_id = 'ast.clock.old'").fetchone()
            self.assertIsNotNone(old["ended_seq"])
            event_types = [event["event_type"] for event in cube.events()]
            self.assertEqual(event_types.count("assertion.recorded"), 2)

    def test_rebuild_is_semantically_stable(self) -> None:
        with Cube.open(self.root) as cube:
            cube.apply_operations(actor_id="user", operations=demo_operations(), message="demo")
            before = json.dumps(cube.snapshot(), sort_keys=True)
            report = cube.rebuild_projections()
            after = json.dumps(cube.snapshot(), sort_keys=True)
            self.assertEqual(report["overall_status"], "pass")
            self.assertEqual(before, after)


    def test_unknown_operation_field_is_refused_atomically(self) -> None:
        with Cube.open(self.root) as cube:
            before = cube.event_count()
            with self.assertRaises(LacunaError) as caught:
                cube.apply_operations(
                    actor_id="user",
                    operations=[
                        {
                            "op": "register_agent",
                            "agent_id": "mira",
                            "kind": "character",
                            "label": "Mira",
                            "lable": "typo must not be ignored",
                        }
                    ],
                )
            self.assertEqual(caught.exception.code, "unexpected-operation-field")
            self.assertEqual(cube.event_count(), before)
            self.assertFalse(cube._exists("agents", "agent_id", "mira"))

    def test_anchor_is_immutable(self) -> None:
        claim_id = deterministic_claim_id("bell", "was_heard", True, "event")
        with Cube.open(self.root) as cube:
            cube.apply_operations(
                actor_id="user",
                operations=[
                    {
                        "op": "declare_claim",
                        "claim_id": claim_id,
                        "subject": "bell",
                        "predicate": "was_heard",
                        "object": True,
                        "scope": "event",
                    },
                    {
                        "op": "record_assertion",
                        "assertion_id": "ast.bell.anchor",
                        "claim_id": claim_id,
                        "assertor_id": "user",
                        "stance": "true",
                        "basis": "observation",
                        "standing": "anchored",
                        "visibility": "public",
                    },
                ],
            )
            before = cube.event_count()
            with self.assertRaises(LacunaError) as caught:
                cube.apply_operations(
                    actor_id="user",
                    operations=[
                        {
                            "op": "supersede_assertion",
                            "assertion_id": "ast.bell.anchor",
                            "reason": "convenient retcon",
                        }
                    ],
                )
            self.assertEqual(caught.exception.code, "anchor-immutable")
            self.assertEqual(cube.event_count(), before)
            self.assertEqual(
                {item["assertion_id"] for item in cube.active_assertions()},
                {"ast.bell.anchor"},
            )

    def test_reactivating_world_that_conflicts_with_anchor_is_refused(self) -> None:
        claim_id = deterministic_claim_id("door", "is_open", True, "world")
        with Cube.open(self.root) as cube:
            cube.apply_operations(
                actor_id="user",
                operations=[
                    {
                        "op": "declare_claim",
                        "claim_id": claim_id,
                        "subject": "door",
                        "predicate": "is_open",
                        "object": True,
                        "scope": "world",
                    },
                    {"op": "create_world", "world_id": "world.closed", "label": "Closed"},
                    {
                        "op": "assign_world",
                        "world_id": "world.closed",
                        "claim_id": claim_id,
                        "truth": "false",
                    },
                    {
                        "op": "set_world_status",
                        "world_id": "world.closed",
                        "status": "pruned",
                        "reason": "set aside before observation",
                    },
                    {
                        "op": "record_assertion",
                        "assertion_id": "ast.door.open",
                        "claim_id": claim_id,
                        "assertor_id": "user",
                        "stance": "true",
                        "basis": "observation",
                        "standing": "anchored",
                        "visibility": "public",
                    },
                ],
            )
            before = cube.event_count()
            with self.assertRaises(LacunaError) as caught:
                cube.apply_operations(
                    actor_id="user",
                    operations=[
                        {
                            "op": "set_world_status",
                            "world_id": "world.closed",
                            "status": "live",
                            "reason": "try to revive it",
                        }
                    ],
                )
            self.assertEqual(caught.exception.code, "world-reactivation-conflict")
            self.assertEqual(cube.event_count(), before)
            self.assertEqual(cube._require_world("world.closed")["status"], "pruned")

    def test_perspective_context_does_not_leak_hidden_worlds_or_claims(self) -> None:
        claim_id = deterministic_claim_id("vault", "contains", "crown", "world")
        with Cube.open(self.root) as cube:
            cube.apply_operations(
                actor_id="user",
                operations=[
                    {"op": "register_agent", "agent_id": "alice", "kind": "character", "label": "Alice"},
                    {"op": "register_agent", "agent_id": "bob", "kind": "character", "label": "Bob"},
                    {
                        "op": "declare_claim",
                        "claim_id": claim_id,
                        "subject": "vault",
                        "predicate": "contains",
                        "object": "crown",
                        "scope": "world",
                    },
                    {
                        "op": "record_assertion",
                        "assertion_id": "ast.alice.secret",
                        "claim_id": claim_id,
                        "assertor_id": "alice",
                        "perspective_id": "alice",
                        "stance": "true",
                        "basis": "belief",
                        "standing": "accepted",
                        "visibility": "private",
                    },
                    {
                        "op": "create_world",
                        "world_id": "world.secret",
                        "label": "Crown conspiracy",
                    },
                    {
                        "op": "assign_world",
                        "world_id": "world.secret",
                        "claim_id": claim_id,
                        "truth": "true",
                    },
                ],
            )
            bob_context = context_markdown(cube, agent_id="bob")
            self.assertNotIn("vault", bob_context)
            self.assertNotIn("crown", bob_context.lower())
            self.assertNotIn("world.secret", bob_context)
            omniscient_context = context_markdown(cube)
            self.assertIn("vault", omniscient_context)
            self.assertIn("world.secret", omniscient_context)

    def test_world_fork_inherits_then_diverges(self) -> None:
        claim_id = deterministic_claim_id("lantern", "is_lit", True, "world")
        with Cube.open(self.root) as cube:
            cube.apply_operations(
                actor_id="user",
                operations=[
                    {
                        "op": "declare_claim",
                        "claim_id": claim_id,
                        "subject": "lantern",
                        "predicate": "is_lit",
                        "object": True,
                        "scope": "world",
                    },
                    {"op": "create_world", "world_id": "world.parent", "label": "Parent"},
                    {
                        "op": "assign_world",
                        "assignment_id": "asn.parent.lantern",
                        "world_id": "world.parent",
                        "claim_id": claim_id,
                        "truth": "true",
                        "commitment": "soft",
                    },
                    {
                        "op": "create_world",
                        "world_id": "world.child",
                        "label": "Child",
                        "parent_world_id": "world.parent",
                    },
                ],
            )
            inherited = cube.world_assignments("world.child")
            self.assertEqual(len(inherited), 1)
            self.assertEqual(inherited[0]["truth"], "true")
            self.assertEqual(inherited[0]["inherited_from_assignment_id"], "asn.parent.lantern")
            impact = cube.revision_impact(inherited[0]["assignment_id"])
            cube.apply_operations(
                actor_id="user",
                operations=[
                    {
                        "op": "revise_world",
                        "assignment_id": "asn.child.lantern.revised",
                        "revises_assignment_id": inherited[0]["assignment_id"],
                        "truth": "false",
                        "expected_impact_sha256": impact["impact_sha256"],
                        "reason": "The child candidate diverges from its inherited premise.",
                    }
                ],
            )
            self.assertEqual(cube.world_assignments("world.child")[0]["truth"], "false")
            self.assertEqual(cube.world_assignments("world.parent")[0]["truth"], "true")

    def test_nonoverlapping_opposite_anchors_are_temporally_valid(self) -> None:
        claim_id = deterministic_claim_id("door", "is_open", True, "world")
        with Cube.open(self.root) as cube:
            cube.apply_operations(
                actor_id="user",
                operations=[
                    {
                        "op": "declare_claim",
                        "claim_id": claim_id,
                        "subject": "door",
                        "predicate": "is_open",
                        "object": True,
                        "scope": "world",
                    },
                    {
                        "op": "record_assertion",
                        "assertion_id": "ast.door.early",
                        "claim_id": claim_id,
                        "assertor_id": "user",
                        "stance": "true",
                        "basis": "observation",
                        "standing": "anchored",
                        "visibility": "public",
                        "valid_from": 1,
                        "valid_to": 5,
                    },
                    {
                        "op": "record_assertion",
                        "assertion_id": "ast.door.late",
                        "claim_id": claim_id,
                        "assertor_id": "user",
                        "stance": "false",
                        "basis": "observation",
                        "standing": "anchored",
                        "visibility": "public",
                        "valid_from": 6,
                        "valid_to": 10,
                    },
                ],
            )
            self.assertEqual(len(cube.canon()["anchors"]), 2)
            self.assertEqual(cube.verify()["overall_status"], "pass")


    def test_demo_keeps_evidence_world_scoped(self) -> None:
        with Cube.open(self.root) as cube:
            cube.apply_operations(actor_id="user", operations=demo_operations(), message="demo")
            links = cube.evidence_links()
            self.assertEqual({item["link_id"] for item in links}, {"evl.voice.heir", "evl.voice.spy"})
            self.assertEqual({item["world_id"] for item in links}, {"world.heir", "world.spy"})
            heir_links = cube.evidence_links(world_id="world.heir")
            self.assertEqual([item["link_id"] for item in heir_links], ["evl.voice.heir"])
            privileged = context_markdown(cube)
            player = context_markdown(cube, agent_id="player")
            self.assertIn("evl.voice.heir", privileged)
            self.assertNotIn("evl.voice.heir", player)
            self.assertIn("privileged planner state", player)


    def test_rebuild_repairs_projection_corruption_from_valid_ledger(self) -> None:
        claim_id = deterministic_claim_id("door", "is_open", True, "world")
        with Cube.open(self.root) as cube:
            cube.apply_operations(
                actor_id="user",
                operations=[
                    {
                        "op": "declare_claim",
                        "claim_id": claim_id,
                        "subject": "door",
                        "predicate": "is_open",
                        "object": True,
                        "scope": "world",
                    },
                    {
                        "op": "record_assertion",
                        "assertion_id": "ast.door.anchor",
                        "claim_id": claim_id,
                        "assertor_id": "user",
                        "stance": "true",
                        "basis": "observation",
                        "standing": "anchored",
                        "visibility": "public",
                    },
                    {"op": "create_world", "world_id": "world.valid", "label": "Valid"},
                    {
                        "op": "assign_world",
                        "world_id": "world.valid",
                        "claim_id": claim_id,
                        "truth": "true",
                    },
                ],
            )
            cube.conn.execute(
                "UPDATE world_assignments SET truth = 'false' WHERE world_id = 'world.valid'"
            )
            self.assertEqual(cube.verify()["overall_status"], "fail")
            self.assertEqual(cube.verify(include_projections=False)["overall_status"], "pass")
            rebuilt = cube.rebuild_projections()
            self.assertEqual(rebuilt["overall_status"], "pass")
            self.assertEqual(cube.world_assignments("world.valid")[0]["truth"], "true")

    def test_superseding_assertion_ends_its_evidence_links(self) -> None:
        evidence_claim = deterministic_claim_id("mira", "was_seen", True, "event")
        target_claim = deterministic_claim_id("mira", "is_nearby", True, "world")
        with Cube.open(self.root) as cube:
            cube.apply_operations(
                actor_id="user",
                operations=[
                    {
                        "op": "declare_claim",
                        "claim_id": evidence_claim,
                        "subject": "mira",
                        "predicate": "was_seen",
                        "object": True,
                        "scope": "event",
                    },
                    {
                        "op": "declare_claim",
                        "claim_id": target_claim,
                        "subject": "mira",
                        "predicate": "is_nearby",
                        "object": True,
                        "scope": "world",
                    },
                    {
                        "op": "record_assertion",
                        "assertion_id": "ast.mira.report",
                        "claim_id": evidence_claim,
                        "assertor_id": "user",
                        "stance": "true",
                        "basis": "testimony",
                        "standing": "reported",
                        "visibility": "private",
                    },
                    {
                        "op": "link_evidence",
                        "link_id": "evl.mira.nearby",
                        "evidence_assertion_id": "ast.mira.report",
                        "target_claim_id": target_claim,
                        "relation": "supports",
                    },
                ],
            )
            self.assertEqual(len(cube.evidence_links()), 1)
            cube.apply_operations(
                actor_id="user",
                operations=[
                    {
                        "op": "supersede_assertion",
                        "assertion_id": "ast.mira.report",
                        "reason": "the report was withdrawn",
                    }
                ],
            )
            self.assertEqual(cube.evidence_links(), [])
            row = cube.conn.execute(
                "SELECT ended_seq FROM evidence_links WHERE link_id = 'evl.mira.nearby'"
            ).fetchone()
            self.assertIsNotNone(row["ended_seq"])

    def test_question_resolution_must_concern_the_named_claim(self) -> None:
        first = deterministic_claim_id("cup", "was_signaled", True, "world")
        second = deterministic_claim_id("storm", "will_arrive", True, "world")
        with Cube.open(self.root) as cube:
            cube.apply_operations(
                actor_id="user",
                operations=[
                    {
                        "op": "declare_claim",
                        "claim_id": first,
                        "subject": "cup",
                        "predicate": "was_signaled",
                        "object": True,
                        "scope": "world",
                    },
                    {
                        "op": "declare_claim",
                        "claim_id": second,
                        "subject": "storm",
                        "predicate": "will_arrive",
                        "object": True,
                        "scope": "world",
                    },
                    {
                        "op": "record_assertion",
                        "assertion_id": "ast.storm",
                        "claim_id": second,
                        "assertor_id": "user",
                        "stance": "true",
                        "basis": "inference",
                        "visibility": "private",
                    },
                    {
                        "op": "open_question",
                        "question_id": "qst.cup.test",
                        "text": "Was the cup a signal?",
                        "about_claim_id": first,
                        "opened_by": "user",
                        "visibility": "private",
                    },
                ],
            )
            before = cube.event_count()
            with self.assertRaises(LacunaError) as caught:
                cube.apply_operations(
                    actor_id="user",
                    operations=[
                        {
                            "op": "close_question",
                            "question_id": "qst.cup.test",
                            "resolution_assertion_id": "ast.storm",
                            "reason": "wrong answer",
                        }
                    ],
                )
            self.assertEqual(caught.exception.code, "question-resolution-mismatch")
            self.assertEqual(cube.event_count(), before)
            self.assertEqual(cube.unknowns()["open_questions"][0]["question_id"], "qst.cup.test")

    def test_change_receipt_tampering_is_detected(self) -> None:
        with Cube.open(self.root) as cube:
            cube.apply_operations(
                actor_id="user",
                operations=[
                    {"op": "register_agent", "agent_id": "mira", "kind": "character", "label": "Mira"}
                ],
            )
            cube.conn.execute(
                "UPDATE changesets SET operation_count = operation_count + 1 WHERE actor_id = 'user'"
            )
            report = cube.verify()
            self.assertEqual(report["overall_status"], "fail")
            self.assertIn("change-operation-count", {item["code"] for item in report["errors"]})


if __name__ == "__main__":
    unittest.main()
