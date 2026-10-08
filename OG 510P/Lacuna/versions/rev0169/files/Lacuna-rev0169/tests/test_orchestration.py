from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tests._schema_support import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from lacuna.campaigns import CampaignLibrary
from lacuna.errors import LacunaError
from lacuna.orchestration import (
    NARRATOR_RETURN_SCHEMA,
    ORCHESTRATION_PLAN_SCHEMA,
    PLANNER_RETURN_SCHEMA,
    TURN_TASK_CARD_SCHEMA,
    VERIFIER_RETURN_SCHEMA,
    build_orchestration_plan,
    build_turn_task_card,
    orchestration_plan_markdown,
    turn_packet_sha256,
    turn_task_card_markdown,
    validate_narrator_return,
    validate_planner_return,
    validate_proposal_binding,
    validate_turn_packet,
    validate_verifier_return,
)
from lacuna.store import Cube
from lacuna.turns import build_turn_packet


class TurnOrchestrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.library_path = Path(self.temporary.name) / "library"
        library = CampaignLibrary.ensure(self.library_path)
        self.campaign = library.create_campaign(
            slug="mirror-lake",
            title="Mirror Lake",
            summary="A test campaign for exact least-context handoffs.",
        )

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def packet(
        self,
        *,
        director: bool = True,
        allow_anchor: bool = False,
        input_kind: str = "play-turn",
        player_input: str = "I listen at the sealed greenhouse door.",
    ) -> dict:
        with Cube.open(self.campaign["path"]) as cube:
            return build_turn_packet(
                cube,
                audience_id="player",
                actor_id="narrator",
                player_input=player_input,
                input_kind=input_kind,
                director=director,
                allow_anchor=allow_anchor,
            )

    @staticmethod
    def planner_return(packet: dict, *, plan: list[str] | None = None) -> dict:
        card = build_turn_task_card(packet, role="lacuna-planner")
        result = copy.deepcopy(card["output_contract"]["template"])
        result["observable_plan"] = plan or [
            "The player hears one irregular metallic tap beyond the greenhouse door."
        ]
        result["preserved_unknowns"] = ["The source and intent of the tap remain unknown."]
        return result

    @staticmethod
    def narrator_return(packet: dict, planner: dict) -> dict:
        card = build_turn_task_card(
            packet,
            role="lacuna-narrator",
            planner_return=planner,
        )
        result = copy.deepcopy(card["output_contract"]["template"])
        result["narration"] = (
            "Beyond the sealed glass, metal touches metal once—then, after an uneven pause, once again."
        )
        result["directly_observable_facts"] = [
            "An irregular metallic tapping is audible beyond the door."
        ]
        return result

    def test_typed_session_control_survives_least_context_handoffs(self) -> None:
        packet = self.packet(
            input_kind="session-control",
            player_input="Will you DM?",
        )
        planner_card = build_turn_task_card(packet, role="lacuna-planner")
        self.assertIn("session-control", " ".join(planner_card["instructions"]))
        planner = self.planner_return(
            packet,
            plan=["Offer one reversible opening-scene choice."],
        )
        narrator_card = build_turn_task_card(
            packet,
            role="lacuna-narrator",
            planner_return=planner,
        )
        self.assertEqual(
            narrator_card["input"]["player_input"]["kind"],
            "session-control",
        )
        self.assertIn(
            "not an in-world action",
            " ".join(narrator_card["instructions"]),
        )

    def test_legacy_v2_and_v3_packets_default_to_play_without_digest_rewrite(self) -> None:
        packet = self.packet()

        legacy_v3 = copy.deepcopy(packet)
        legacy_v3["schema"] = "lacuna.turn-request.v3"
        legacy_v3.pop("request_purpose")
        audited_v3 = validate_turn_packet(legacy_v3)
        self.assertEqual(audited_v3, legacy_v3)

        legacy_v2 = copy.deepcopy(legacy_v3)
        legacy_v2["schema"] = "lacuna.turn-request.v2"
        legacy_v2.pop("input_kind")
        audited_v2 = validate_turn_packet(legacy_v2)
        self.assertEqual(audited_v2, legacy_v2)
        planner = self.planner_return(legacy_v2)
        narrator_card = build_turn_task_card(
            legacy_v2,
            role="lacuna-narrator",
            planner_return=planner,
        )
        self.assertEqual(narrator_card["input"]["player_input"]["kind"], "play-turn")

        malformed = copy.deepcopy(packet)
        malformed.pop("input_kind")
        with self.assertRaises(LacunaError) as caught:
            validate_turn_packet(malformed)
        self.assertEqual(caught.exception.code, "bad-turn-packet")

    def test_packet_audit_binds_exact_body_context_grant_and_safe_template(self) -> None:
        packet = self.packet()
        audited = validate_turn_packet(packet)
        self.assertEqual(audited, packet)
        self.assertEqual(len(turn_packet_sha256(packet)), 64)

        cases: list[tuple[str, dict, str]] = []
        changed_input = copy.deepcopy(packet)
        changed_input["player_input"] += " altered"
        cases.append(("input", changed_input, "turn-packet-input-digest-mismatch"))

        changed_context = copy.deepcopy(packet)
        changed_context["audience_context"]["head"] = "0" * 64
        cases.append(("context", changed_context, "turn-packet-context-mismatch"))

        changed_grant = copy.deepcopy(packet)
        changed_grant["response_contract"]["allowed_operations"] = []
        cases.append(("grant", changed_grant, "turn-packet-grant-mismatch"))

        changed_template = copy.deepcopy(packet)
        changed_template["response_contract"]["proposal_template"]["expected_head"] = "0" * 64
        cases.append(("template", changed_template, "turn-packet-template-mismatch"))

        unsafe_template = copy.deepcopy(packet)
        unsafe_template["response_contract"]["proposal_template"]["operations"] = [
            {"op": "declare_claim"}
        ]
        cases.append(("unsafe-template", unsafe_template, "unsafe-turn-template"))

        for label, document, code in cases:
            with self.subTest(label=label):
                with self.assertRaises(LacunaError) as caught:
                    validate_turn_packet(document)
                self.assertEqual(caught.exception.code, code)

    def test_auto_topology_uses_solo_pair_and_full_only_from_explicit_packet_signals(self) -> None:
        audience = build_orchestration_plan(self.packet(director=False), mode="auto")
        self.assertEqual(audience["selected_mode"], "solo")
        self.assertEqual(audience["spawn_policy"], "do-not-spawn-by-default")

        ordinary_director = build_orchestration_plan(self.packet(), mode="auto")
        self.assertEqual(ordinary_director["selected_mode"], "pair")
        self.assertTrue(ordinary_director["risk_summary"]["privileged_context_present"])

        anchor_director = build_orchestration_plan(
            self.packet(allow_anchor=True),
            mode="auto",
        )
        self.assertEqual(anchor_director["selected_mode"], "full")
        self.assertTrue(anchor_director["risk_summary"]["high_impact_custody_present"])
        self.assertEqual(
            [stage["role"] for stage in anchor_director["stages"]],
            [
                "lacuna-planner",
                "lacuna-narrator",
                "lacuna-proposal-builder",
                "lacuna-verifier",
            ],
        )
        self.assertTrue(all(not stage["may_commit"] for stage in anchor_director["stages"]))
        commands = [stage["card_command"] for stage in anchor_director["stages"]]
        self.assertIn("--role lacuna-planner", commands[0])
        self.assertIn("--planner-return PLANNER_RETURN.json", commands[1])
        self.assertIn("--narrator-return NARRATOR_RETURN.json", commands[2])
        self.assertIn("--proposal PROPOSAL.json", commands[3])

    def test_narrator_card_contains_only_perspective_context_and_observable_plan(self) -> None:
        packet = self.packet()
        planner = self.planner_return(packet)
        planner["private_notes"] = "SECRET-WORLD-RATIONALE"
        planner["candidate_operations"] = [
            {
                "op": "open_question",
                "question_id": "qst.tap",
                "text": "What made the tap?",
                "opened_by": "player",
                "visibility": "public",
            }
        ]
        card = build_turn_task_card(
            packet,
            role="lacuna-narrator",
            planner_return=planner,
        )
        self.assertEqual(card["schema"], TURN_TASK_CARD_SCHEMA)
        self.assertEqual(card["role"], "lacuna-narrator")
        self.assertNotIn("packet", card["input"])
        self.assertNotIn("planner_context", card["input"])
        self.assertNotIn("private_notes", card["input"])
        self.assertNotIn("candidate_operations", card["input"])
        self.assertNotIn("SECRET-WORLD-RATIONALE", json.dumps(card))
        self.assertEqual(
            card["input"]["approved_observable_plan"],
            planner["observable_plan"],
        )
        audience = card["input"]["audience_context"]
        self.assertFalse(audience["access"]["privileged"])
        self.assertEqual(audience["candidate_worlds"], [])
        self.assertIsNone(audience["particle_bank"])
        self.assertIn("planner_context", card["information_boundary"]["withheld"])

    def test_handoff_digests_refuse_cross_turn_or_edited_upstream_artifacts(self) -> None:
        first = self.packet()
        second = self.packet()
        planner = self.planner_return(first)

        with self.assertRaises(LacunaError) as caught:
            build_turn_task_card(
                second,
                role="lacuna-narrator",
                planner_return=planner,
            )
        self.assertEqual(caught.exception.code, "handoff-binding-mismatch")

        edited = copy.deepcopy(planner)
        original_card = build_turn_task_card(
            first,
            role="lacuna-narrator",
            planner_return=planner,
        )
        narrator = copy.deepcopy(original_card["output_contract"]["template"])
        narrator["narration"] = "A sound crosses the glass."
        edited["observable_plan"].append("A hidden edit after narrator issuance.")
        with self.assertRaises(LacunaError) as caught:
            validate_narrator_return(narrator, first, edited)
        self.assertEqual(caught.exception.code, "handoff-binding-mismatch")

    def test_full_card_chain_builds_exact_proposal_and_fail_closed_verifier(self) -> None:
        packet = self.packet(allow_anchor=True)
        planner = self.planner_return(packet)
        narrator_card = build_turn_task_card(
            packet,
            role="lacuna-narrator",
            planner_return=planner,
        )
        with self.assertRaises(LacunaError) as caught:
            validate_narrator_return(
                narrator_card["output_contract"]["template"],
                packet,
                planner,
            )
        self.assertEqual(caught.exception.code, "unreplaced-narration-template")

        narrator = self.narrator_return(packet, planner)
        builder = build_turn_task_card(
            packet,
            role="lacuna-proposal-builder",
            planner_return=planner,
            narrator_return=narrator,
        )
        proposal = builder["output_contract"]["template"]
        self.assertEqual(proposal["narration"], narrator["narration"])
        self.assertEqual(proposal["expected_head"], packet["expected_head"])
        self.assertEqual(proposal["operations"], planner["candidate_operations"])
        validate_proposal_binding(proposal, packet)

        verifier = build_turn_task_card(
            packet,
            role="lacuna-verifier",
            proposal=proposal,
        )
        default_return = verifier["output_contract"]["template"]
        self.assertEqual(default_return["status"], "refuse")
        self.assertEqual(default_return["findings"][0]["code"], "unperformed-review")
        validate_verifier_return(default_return, packet, proposal)

        cosmetic_pass = copy.deepcopy(default_return)
        cosmetic_pass["status"] = "pass"
        cosmetic_pass["findings"][0]["severity"] = "info"
        cosmetic_pass["recommended_action"] = "commit"
        with self.assertRaises(LacunaError) as caught:
            validate_verifier_return(cosmetic_pass, packet, proposal)
        self.assertEqual(caught.exception.code, "bad-verifier-return")

        self.assertNotIn("turn commit", json.dumps(verifier["instructions"]).lower())
        self.assertFalse(verifier["may_commit"])

    def test_proposal_preflight_rejects_binding_and_ungranted_operation_without_claiming_commit(self) -> None:
        packet = self.packet(director=False)
        proposal = copy.deepcopy(packet["response_contract"]["proposal_template"])
        proposal["narration"] = "The greenhouse glass holds a dull reflection."
        validate_proposal_binding(proposal, packet)

        changed = copy.deepcopy(proposal)
        changed["request_id"] = "trq_other"
        with self.assertRaises(LacunaError) as caught:
            validate_proposal_binding(changed, packet)
        self.assertEqual(caught.exception.code, "proposal-packet-binding-mismatch")

        ungranted = copy.deepcopy(proposal)
        ungranted["operations"] = [{"op": "create_world", "world_id": "wld.hidden"}]
        with self.assertRaises(LacunaError) as caught:
            validate_proposal_binding(ungranted, packet)
        self.assertEqual(caught.exception.code, "proposal-operation-not-granted")

    def test_task_ids_are_deterministic_and_change_with_upstream_content(self) -> None:
        packet = self.packet()
        first = build_turn_task_card(packet, role="lacuna-planner")
        second = build_turn_task_card(copy.deepcopy(packet), role="lacuna-planner")
        self.assertEqual(first["task_id"], second["task_id"])

        planner_a = self.planner_return(packet, plan=["A soft scrape is audible."])
        planner_b = self.planner_return(packet, plan=["A sharp tap is audible."])
        narrator_a = build_turn_task_card(
            packet,
            role="lacuna-narrator",
            planner_return=planner_a,
        )
        narrator_b = build_turn_task_card(
            packet,
            role="lacuna-narrator",
            planner_return=planner_b,
        )
        self.assertNotEqual(narrator_a["task_id"], narrator_b["task_id"])

    def test_markdown_surfaces_operational_commands_and_exact_return_contracts(self) -> None:
        packet = self.packet()
        plan = build_orchestration_plan(packet)
        rendered_plan = orchestration_plan_markdown(plan)
        self.assertIn("Use this plan operationally", rendered_plan)
        self.assertIn("./lacuna turn card", rendered_plan)
        self.assertIn(plan["packet_sha256"], rendered_plan)

        card = build_turn_task_card(packet, role="lacuna-planner")
        rendered_card = turn_task_card_markdown(card)
        self.assertIn("Do not run tools or commit", rendered_card)
        self.assertIn('"schema": "lacuna.planner-return.v1"', rendered_card)
        self.assertIn(card["task_id"], rendered_card)

    @unittest.skipUnless(
        Draft202012Validator is not None,
        "jsonschema test extra is not installed",
    )
    def test_plans_cards_and_role_returns_validate_against_exchange_schemas(self) -> None:
        assert Draft202012Validator is not None
        packet = self.packet(allow_anchor=True)
        plan = build_orchestration_plan(packet)
        planner_card = build_turn_task_card(packet, role="lacuna-planner")
        planner = self.planner_return(packet)
        narrator_card = build_turn_task_card(
            packet,
            role="lacuna-narrator",
            planner_return=planner,
        )
        narrator = self.narrator_return(packet, planner)
        proposal_card = build_turn_task_card(
            packet,
            role="lacuna-proposal-builder",
            planner_return=planner,
            narrator_return=narrator,
        )
        proposal = proposal_card["output_contract"]["template"]
        verifier_card = build_turn_task_card(
            packet,
            role="lacuna-verifier",
            proposal=proposal,
        )
        verifier = verifier_card["output_contract"]["template"]

        artifacts = [
            ("orchestration-plan.v1.schema.json", plan, ORCHESTRATION_PLAN_SCHEMA),
            ("turn-task-card.v1.schema.json", planner_card, TURN_TASK_CARD_SCHEMA),
            ("turn-task-card.v1.schema.json", narrator_card, TURN_TASK_CARD_SCHEMA),
            ("turn-task-card.v1.schema.json", proposal_card, TURN_TASK_CARD_SCHEMA),
            ("turn-task-card.v1.schema.json", verifier_card, TURN_TASK_CARD_SCHEMA),
            ("planner-return.v1.schema.json", planner, PLANNER_RETURN_SCHEMA),
            ("narrator-return.v1.schema.json", narrator, NARRATOR_RETURN_SCHEMA),
            ("verifier-return.v1.schema.json", verifier, VERIFIER_RETURN_SCHEMA),
        ]
        for filename, artifact, expected_schema in artifacts:
            with self.subTest(schema=expected_schema):
                schema = json.loads((ROOT / "schemas" / filename).read_text(encoding="utf-8"))
                Draft202012Validator(schema).validate(artifact)

    def test_cli_plan_and_planner_card_are_read_only_and_digest_identical(self) -> None:
        packet = self.packet()
        packet_path = Path(self.temporary.name) / "packet.json"
        packet_path.write_text(json.dumps(packet), encoding="utf-8")
        with Cube.open(self.campaign["path"]) as cube:
            before_head = cube.head()
            before_events = cube.event_count()

        plan_result = subprocess.run(
            ["./lacuna", "turn", "plan", str(packet_path), "--mode", "auto"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(plan_result.returncode, 0, plan_result.stderr)
        plan = json.loads(plan_result.stdout)

        card_result = subprocess.run(
            [
                "./lacuna",
                "turn",
                "card",
                str(packet_path),
                "--role",
                "lacuna-planner",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(card_result.returncode, 0, card_result.stderr)
        card = json.loads(card_result.stdout)
        self.assertEqual(plan["packet_sha256"], card["turn_identity"]["packet_sha256"])

        with Cube.open(self.campaign["path"]) as cube:
            self.assertEqual(cube.head(), before_head)
            self.assertEqual(cube.event_count(), before_events)

    def test_public_active_agent_predicate_is_read_only_and_retirement_aware(self) -> None:
        with Cube.open(self.campaign["path"]) as cube:
            head = cube.head()
            events = cube.event_count()
            self.assertTrue(cube.has_active_agent("player"))
            self.assertFalse(cube.has_active_agent("missing"))
            self.assertFalse(cube.has_active_agent("not a valid id"))
            self.assertEqual(cube.head(), head)
            self.assertEqual(cube.event_count(), events)


if __name__ == "__main__":
    unittest.main()
