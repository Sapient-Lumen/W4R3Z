from __future__ import annotations

import json
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
from lacuna.util import deterministic_claim_id, sha256_text


class TurnContractTests(unittest.TestCase):
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
                },
                {
                    "op": "register_agent",
                    "agent_id": "narrator",
                    "kind": "narrator",
                    "label": "Narrator",
                    "metadata": {},
                },
            ],
            message="turn participants",
        )

    def tearDown(self) -> None:
        self.cube.close()
        self.temporary.cleanup()

    def proposal(self, packet: dict, *, narration: str = "The bell rings once.") -> dict:
        return {
            "schema": "lacuna.turn-proposal.v2",
            "request_id": packet["request_id"],
            "request_source_id": packet["request_source_id"],
            "proposal_id": packet["response_contract"]["proposal_template"]["proposal_id"],
            "actor_id": packet["actor_id"],
            "expected_head": packet["expected_head"],
            "player_input_sha256": packet["player_input_sha256"],
            "audience_id": packet["audience_id"],
            "narration_source_id": packet["response_contract"]["proposal_template"]["narration_source_id"],
            "narration": narration,
            "revealed_assertion_ids": ["@bell.fact"],
            "operations": [
                {
                    "op": "declare_claim",
                    "as": "bell.claim",
                    "subject": "lantern-room.bell",
                    "predicate": "rang_count",
                    "object": 1,
                    "scope": "event",
                },
                {
                    "op": "record_assertion",
                    "as": "bell.fact",
                    "claim_id": "@bell.claim",
                    "assertor_id": "@actor",
                    "perspective_id": "@audience",
                    "source_id": "@narration",
                    "stance": "true",
                    "basis": "observation",
                    "standing": "accepted",
                    "confidence": 1.0,
                    "visibility": "private",
                    "audience": [],
                    "timeline_id": "main",
                    "valid_from": 1,
                    "valid_to": 1,
                    "note": "The player directly hears one ring.",
                    "supersedes_id": None,
                },
            ],
            "message": "ring the bell",
        }

    def test_session_control_is_source_bound_without_becoming_fiction(self) -> None:
        before_assertions = len(self.cube.active_assertions())
        packet = build_turn_packet(
            self.cube,
            audience_id="player",
            actor_id="narrator",
            player_input="Will you DM?",
            input_kind="session-control",
            director=True,
        )
        self.assertEqual(packet["schema"], "lacuna.turn-request.v4")
        self.assertEqual(packet["request_purpose"], "play")
        self.assertEqual(packet["input_kind"], "session-control")
        self.assertEqual(len(self.cube.active_assertions()), before_assertions)
        source = self.cube.conn.execute(
            "SELECT metadata_json FROM sources WHERE source_id = ?",
            (packet["request_source_id"],),
        ).fetchone()
        metadata = json.loads(source["metadata_json"])
        self.assertEqual(metadata["protocol"], "lacuna.turn-request-source.v3")
        self.assertEqual(metadata["request_purpose"], "play")
        self.assertEqual(metadata["input_kind"], "session-control")

        proposal = dict(packet["response_contract"]["proposal_template"])
        proposal["narration"] = (
            "The table is ready. Shall we begin at the rain-dark greenhouse?"
        )
        receipt = commit_turn_proposal(self.cube, proposal)
        self.assertEqual(receipt["overall_status"], "pass")
        self.assertEqual(len(self.cube.active_assertions()), before_assertions)

    def test_invalid_input_kind_refuses_before_opening_a_request(self) -> None:
        before_head = self.cube.head()
        before_events = self.cube.event_count()
        with self.assertRaises(LacunaError) as caught:
            build_turn_packet(
                self.cube,
                audience_id="player",
                actor_id="narrator",
                player_input="Will you DM?",
                input_kind="maybe-control",
                director=True,
            )
        self.assertEqual(caught.exception.code, "bad-turn-input-kind")
        self.assertEqual(self.cube.head(), before_head)
        self.assertEqual(self.cube.event_count(), before_events)

    def test_context_firewall_refuses_perspective_plus_hidden_world(self) -> None:
        self.cube.apply_operations(
            actor_id="user",
            operations=[
                {
                    "op": "create_world",
                    "world_id": "wld_secret",
                    "label": "Secret",
                    "parent_world_id": None,
                    "status": "live",
                    "weight": 1.0,
                    "rationale": "hidden",
                }
            ],
        )
        with self.assertRaises(LacunaError) as caught:
            build_context(self.cube, agent_id="player", world_id="wld_secret")
        self.assertEqual(caught.exception.code, "unsafe-context-scope")

    def test_hidden_anchor_does_not_settle_a_visible_claim_by_omission(self) -> None:
        claim_id = deterministic_claim_id("cellar.door", "is_locked", True, "world")
        self.cube.apply_operations(
            actor_id="user",
            operations=[
                {
                    "op": "register_agent",
                    "agent_id": "keeper",
                    "kind": "character",
                    "label": "Keeper",
                    "metadata": {},
                },
                {
                    "op": "declare_claim",
                    "claim_id": claim_id,
                    "subject": "cellar.door",
                    "predicate": "is_locked",
                    "object": True,
                    "scope": "world",
                },
                {
                    "op": "record_assertion",
                    "assertion_id": "ast_player_report",
                    "claim_id": claim_id,
                    "assertor_id": "player",
                    "perspective_id": "player",
                    "source_id": None,
                    "stance": "true",
                    "basis": "testimony",
                    "standing": "reported",
                    "confidence": 0.6,
                    "visibility": "private",
                    "audience": [],
                    "timeline_id": "main",
                    "valid_from": None,
                    "valid_to": None,
                    "note": "The player was told the door is locked.",
                    "supersedes_id": None,
                },
                {
                    "op": "record_assertion",
                    "assertion_id": "ast_keeper_anchor",
                    "claim_id": claim_id,
                    "assertor_id": "keeper",
                    "perspective_id": "keeper",
                    "source_id": None,
                    "stance": "true",
                    "basis": "observation",
                    "standing": "anchored",
                    "confidence": 1.0,
                    "visibility": "private",
                    "audience": [],
                    "timeline_id": "main",
                    "valid_from": None,
                    "valid_to": None,
                    "note": "Hidden from the player.",
                    "supersedes_id": None,
                },
            ],
            message="create a hidden settlement side-channel test",
        )

        audience = build_context(self.cube, agent_id="player")
        planner = build_context(self.cube)
        self.assertIn(claim_id, {item["claim_id"] for item in audience["unsettled_claims"]})
        self.assertNotIn(
            "ast_keeper_anchor",
            {item["assertion_id"] for item in audience["assertions"]},
        )
        self.assertNotIn(claim_id, {item["claim_id"] for item in planner["unsettled_claims"]})

    def test_director_packet_separates_audience_and_planner_views(self) -> None:
        self.cube.apply_operations(
            actor_id="user",
            operations=[
                {
                    "op": "create_world",
                    "world_id": "wld_secret",
                    "label": "Secret culprit",
                    "parent_world_id": None,
                    "status": "live",
                    "weight": 1.0,
                    "rationale": "hidden",
                }
            ],
        )
        packet = build_turn_packet(
            self.cube,
            audience_id="player",
            actor_id="narrator",
            player_input="I listen at the door.",
            director=True,
        )
        self.assertFalse(packet["audience_context"]["access"]["privileged"])
        self.assertEqual(packet["audience_context"]["candidate_worlds"], [])
        self.assertTrue(packet["planner_context"]["access"]["privileged"])
        self.assertEqual(packet["planner_context"]["candidate_worlds"][0]["world_id"], "wld_secret")

    def test_alias_turn_commit_hashes_narration_and_commits_visible_assertion(self) -> None:
        packet = build_turn_packet(
            self.cube,
            audience_id="player",
            actor_id="narrator",
            player_input="I pull the bell rope.",
        )
        proposal = self.proposal(packet)
        before_count = self.cube.event_count()
        receipt = commit_turn_proposal(self.cube, proposal)
        self.assertEqual(receipt["narration"], "The bell rings once.")
        self.assertEqual(receipt["narration_sha256"], sha256_text("The bell rings once."))
        self.assertGreater(self.cube.event_count(), before_count)
        assertion_id = receipt["bindings"]["bell.fact"]
        self.assertEqual(receipt["revealed_assertion_ids"], [assertion_id])
        visible_ids = {item["assertion_id"] for item in self.cube.perspective("player")["assertions"]}
        self.assertIn(assertion_id, visible_ids)
        source = self.cube.conn.execute(
            "SELECT content_sha256, metadata_json FROM sources WHERE source_id = ?",
            (receipt["narration_source_id"],),
        ).fetchone()
        self.assertEqual(source["content_sha256"], receipt["narration_sha256"])
        self.assertNotIn("The bell rings once.", source["metadata_json"])
        stored_bytes = b"".join(
            candidate.read_bytes()
            for candidate in self.root.iterdir()
            if candidate.is_file()
        )
        self.assertNotIn(b"The bell rings once.", stored_bytes)
        self.assertEqual(self.cube.verify()["overall_status"], "pass")

    def test_narration_only_turn_is_valid_but_does_not_create_claims(self) -> None:
        packet = build_turn_packet(
            self.cube,
            audience_id="player",
            actor_id="narrator",
            player_input="I wait.",
        )
        proposal = self.proposal(packet, narration="Rain ticks against the shutter.")
        proposal["operations"] = []
        proposal["revealed_assertion_ids"] = []
        before_claims = len(self.cube.claims())
        receipt = commit_turn_proposal(self.cube, proposal)
        self.assertEqual(len(self.cube.claims()), before_claims)
        self.assertEqual(receipt["change"]["operation_count"], 1)

    def test_stale_turn_is_atomic_and_does_not_add_source(self) -> None:
        packet = build_turn_packet(
            self.cube,
            audience_id="player",
            actor_id="narrator",
            player_input="I pull the rope.",
        )
        proposal = self.proposal(packet)
        self.cube.apply_operations(
            actor_id="user",
            operations=[
                {
                    "op": "register_agent",
                    "agent_id": "witness",
                    "kind": "character",
                    "label": "Witness",
                    "metadata": {},
                }
            ],
        )
        head = self.cube.head()
        count = self.cube.event_count()
        with self.assertRaises(LacunaError) as caught:
            commit_turn_proposal(self.cube, proposal)
        self.assertEqual(caught.exception.code, "stale-head")
        self.assertEqual(self.cube.head(), head)
        self.assertEqual(self.cube.event_count(), count)
        self.assertFalse(
            self.cube._exists("sources", "source_id", proposal["narration_source_id"])
        )

    def test_new_narration_assertion_must_be_declared_as_revealed(self) -> None:
        packet = build_turn_packet(
            self.cube,
            audience_id="player",
            actor_id="narrator",
            player_input="I pull the rope.",
        )
        proposal = self.proposal(packet)
        proposal["revealed_assertion_ids"] = []
        head = self.cube.head()
        with self.assertRaises(LacunaError) as caught:
            commit_turn_proposal(self.cube, proposal)
        self.assertEqual(caught.exception.code, "undeclared-narration-disclosure")
        self.assertEqual(self.cube.head(), head)

    def test_revealed_new_assertion_must_cite_narration_source(self) -> None:
        packet = build_turn_packet(
            self.cube,
            audience_id="player",
            actor_id="narrator",
            player_input="I pull the rope.",
        )
        proposal = self.proposal(packet)
        proposal["operations"].insert(
            0,
            {
                "op": "add_source",
                "as": "other.source",
                "source_id": "src_other",
                "kind": "document",
                "label": "Other",
                "locator": None,
                "content_sha256": None,
                "metadata": {},
            },
        )
        proposal["operations"][2]["source_id"] = "@other.source"
        with self.assertRaises(LacunaError) as caught:
            commit_turn_proposal(self.cube, proposal)
        self.assertEqual(caught.exception.code, "unbound-narration-disclosure")

    def test_forward_alias_is_refused_before_mutation(self) -> None:
        packet = build_turn_packet(
            self.cube,
            audience_id="player",
            actor_id="narrator",
            player_input="I pull the rope.",
        )
        proposal = self.proposal(packet)
        proposal["operations"] = list(reversed(proposal["operations"]))
        head = self.cube.head()
        with self.assertRaises(LacunaError) as caught:
            commit_turn_proposal(self.cube, proposal)
        self.assertEqual(caught.exception.code, "unknown-turn-alias")
        self.assertEqual(self.cube.head(), head)

    def test_turn_projections_rebuild_stably(self) -> None:
        packet = build_turn_packet(
            self.cube,
            audience_id="player",
            actor_id="narrator",
            player_input="I pull the rope.",
        )
        commit_turn_proposal(self.cube, self.proposal(packet))
        before = self.cube.snapshot()
        rebuilt = self.cube.rebuild_projections()
        after = self.cube.snapshot()
        self.assertEqual(rebuilt["overall_status"], "pass")
        self.assertEqual(before, after)

    def test_director_turn_can_consume_embedded_consequence_repair_review(self) -> None:
        claim_id = deterministic_claim_id("bridge", "exists", True, "world")
        self.cube.apply_operations(
            actor_id="user",
            operations=[
                {
                    "op": "declare_claim",
                    "claim_id": claim_id,
                    "subject": "bridge",
                    "predicate": "exists",
                    "object": True,
                    "scope": "world",
                },
                {
                    "op": "create_world",
                    "world_id": "wld_bridge",
                    "label": "Bridge hypothesis",
                },
                {
                    "op": "assign_world",
                    "assignment_id": "asn_bridge",
                    "world_id": "wld_bridge",
                    "claim_id": claim_id,
                    "truth": "true",
                    "commitment": "tentative",
                    "commitment_basis": "planning",
                },
                {
                    "op": "open_question",
                    "question_id": "qst_crossing",
                    "text": "How can the player cross the gorge?",
                    "opened_by": "user",
                    "visibility": "private",
                    "audience": [],
                },
                {
                    "op": "link_consequence",
                    "consequence_id": "csq_bridge_crossing",
                    "premise_assignment_id": "asn_bridge",
                    "dependent_kind": "question",
                    "dependent_id": "qst_crossing",
                    "relation": "motivates",
                    "severity": "material",
                    "rationale": "The bridge premise shapes the crossing question.",
                },
            ],
        )
        impact = self.cube.revision_impact("asn_bridge")
        self.cube.apply_operations(
            actor_id="user",
            operations=[
                {
                    "op": "revise_world",
                    "assignment_id": "asn_bridge_absent",
                    "revises_assignment_id": "asn_bridge",
                    "truth": "false",
                    "expected_impact_sha256": impact["impact_sha256"],
                    "reason": "The hidden bridge hypothesis was revised.",
                }
            ],
        )

        packet = build_turn_packet(
            self.cube,
            audience_id="player",
            actor_id="narrator",
            player_input="I search for another crossing.",
            director=True,
            world_id="wld_bridge",
        )
        self.assertIn("replace_consequence", packet["write_grant"]["allowed_operations"])
        self.assertEqual(packet["audience_context"]["consequence_repair_frontier"], [])
        self.assertIn("consequence_repair_frontier", packet["audience_context"]["omitted"])
        frontier = packet["planner_context"]["consequence_repair_frontier"]
        self.assertEqual(len(frontier), 1)
        review = frontier[0]
        self.assertEqual(review["head"], packet["expected_head"])
        self.assertEqual(review["target"]["consequence_id"], "csq_bridge_crossing")
        self.assertEqual(
            review["known_successors"]["premise_assignment_ids"],
            ["asn_bridge_absent"],
        )

        proposal = self.proposal(
            packet,
            narration="No bridge emerges from the mist; the gorge still demands another answer.",
        )
        proposal["operations"] = [
            {
                "op": "replace_consequence",
                "as": "crossing.repaired",
                "replaces_consequence_id": "csq_bridge_crossing",
                "premise_assignment_id": "asn_bridge_absent",
                "dependent_kind": "question",
                "dependent_id": "qst_crossing",
                "relation": "motivates",
                "severity": "material",
                "source_id": "@narration",
                "rationale": "The absent bridge now motivates the unresolved crossing question.",
                "expected_repair_sha256": review["repair_review_sha256"],
                "reason": "Repair consequence custody while narrating the failed search.",
            }
        ]
        proposal["revealed_assertion_ids"] = []
        receipt = commit_turn_proposal(
            self.cube,
            proposal,
            include_planner_context=True,
        )
        successor_id = receipt["bindings"]["crossing.repaired"]
        links = {
            item["consequence_id"]: item
            for item in self.cube.consequence_links(include_retired=True)
        }
        self.assertEqual(links["csq_bridge_crossing"]["lineage_state"], "replaced")
        self.assertEqual(links[successor_id]["lineage_state"], "replacement")
        self.assertFalse(links[successor_id]["repair_required"])
        repairs = self.cube.consequence_repairs()
        self.assertEqual(len(repairs), 1)
        self.assertEqual(repairs[0]["successor_consequence_id"], successor_id)
        self.assertEqual(self.cube.status()["orphaned_consequence_count"], 0)
        self.assertEqual(receipt["planner_context"]["consequence_repair_frontier"], [])
        self.assertEqual(self.cube.verify()["overall_status"], "pass")


if __name__ == "__main__":
    unittest.main()
