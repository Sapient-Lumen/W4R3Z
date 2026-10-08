from __future__ import annotations

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

import sys

from tests._schema_support import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from lacuna.campaigns import CampaignLibrary
from lacuna.entrance import (
    build_model_brief,
    describe_model_reference,
    model_brief_markdown,
)
from lacuna.errors import LacunaError
from lacuna.store import Cube
from lacuna.turns import build_turn_packet, commit_turn_proposal


class ModelEntranceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.library_path = Path(self.temporary.name) / "library"
        library = CampaignLibrary.ensure(self.library_path)
        self.campaign = library.create_campaign(
            slug="glass-house",
            title="The Glass House",
            summary="A low-commitment test campaign.",
        )

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def build_brief(self, profile: str) -> tuple[dict, str, int]:
        target = describe_model_reference(self.library_path)
        with Cube.open(target["resolved_cube_path"]) as cube:
            before_head = cube.head()
            before_events = cube.event_count()
            brief = build_model_brief(
                cube,
                reference=target["reference"],
                resolved_cube_path=target["resolved_cube_path"],
                reference_kind=target["reference_kind"],
                campaign=target["campaign"],
                profile=profile,
            )
            self.assertEqual(cube.head(), before_head)
            self.assertEqual(cube.event_count(), before_events)
        return brief, before_head, before_events

    def test_library_brief_uses_campaign_roles_and_is_read_only(self) -> None:
        brief, _, _ = self.build_brief("workspace")
        self.assertEqual(brief["schema"], "lacuna.model-brief.v1")
        self.assertEqual(brief["reference_kind"], "campaign-library")
        self.assertEqual(brief["campaign"]["slug"], "glass-house")
        self.assertEqual(brief["roles"]["audience_id"], "player")
        self.assertEqual(brief["roles"]["actor_id"], "narrator")
        self.assertTrue(brief["readiness"]["cube_ready_for_governed_turn"])
        self.assertTrue(brief["profile_contract"]["governed_one_message_start"])
        begin_step = next(
            item for item in brief["operator_loop"] if item["action"] == "begin-request-scoped-turn-run"
        )
        self.assertIn("--director", begin_step["command"])
        self.assertIn("${PLAYER_INPUT:?", begin_step["command"])
        self.assertIn("--player-input-file", begin_step["command"])
        self.assertIn("--input-kind", begin_step["command"])
        self.assertIn("LACUNA_INPUT_KIND", begin_step["command"])
        self.assertIn("session-control", begin_step["command"])
        self.assertIn("--mode solo", begin_step["command"])
        self.assertNotIn("--include-planner-context", begin_step["command"])
        self.assertIn("run_path/run.json", begin_step["output"])
        self.assertTrue(brief["readiness"]["checks"]["ledger_verified"])

    def test_chat_profile_is_honest_about_the_missing_host_loop(self) -> None:
        brief, _, _ = self.build_brief("chat")
        contract = brief["profile_contract"]
        self.assertFalse(contract["governed_one_message_start"])
        self.assertTrue(contract["chat_only_immediate_start"])
        self.assertTrue(contract["ready_if_bridge_is_present"])
        self.assertIn("not yet committed", brief["first_response"]["chat_without_bridge"])

    def test_orchestrated_profile_emits_least_privilege_roles(self) -> None:
        brief, _, _ = self.build_brief("orchestrated")
        delegation = brief["delegation"]
        self.assertTrue(delegation["enabled_by_profile"])
        roles = {item["role"]: item for item in delegation["roles"]}
        self.assertEqual(
            set(roles),
            {
                "lacuna-planner",
                "lacuna-narrator",
                "lacuna-proposal-builder",
                "lacuna-verifier",
            },
        )
        self.assertNotIn("planner_context", roles["lacuna-narrator"]["receives"])
        self.assertIn("planner_context", roles["lacuna-narrator"]["withhold"])
        self.assertTrue(all(not role["may_commit"] for role in roles.values()))
        self.assertEqual(roles["lacuna-planner"]["provider_aliases"]["codex"], "lacuna_planner")
        self.assertEqual(roles["lacuna-narrator"]["provider_aliases"]["chatgpt"], "role-dedicated narrator context")
        self.assertIn("run turn run status", delegation["parent_only_actions"])
        self.assertIn("run turn run recover", delegation["parent_only_actions"])
        self.assertIn("run turn run dispatch", delegation["parent_only_actions"])
        self.assertIn("run turn run commit", delegation["parent_only_actions"])
        begin_step = next(
            item
            for item in brief["operator_loop"]
            if item["action"] == "begin-request-scoped-turn-run"
        )
        self.assertIn("--mode auto", begin_step["command"])
        handoff_step = next(
            item
            for item in brief["operator_loop"]
            if item["action"] == "follow-the-exact-next-action"
        )
        self.assertIn("run.json.next_action", handoff_step["input"])
        self.assertIn("complete generated card unchanged", handoff_step["note"])
        self.assertIn("./lacuna turn run status", handoff_step["command"])
        dispatch_step = next(
            item
            for item in brief["operator_loop"]
            if item["action"] == "render-stage-bound-provider-dispatch"
        )
        self.assertIn("LACUNA_PROVIDER", dispatch_step["command"])
        self.assertIn("turn run dispatch", dispatch_step["command"])
        self.assertIn("lacuna.agent-dispatch.v1", dispatch_step["output"])
        self.assertIn("embedded input_document", dispatch_step["note"])
        commit_step = next(
            item
            for item in brief["operator_loop"]
            if item["action"] == "commit-ready-run-atomically"
        )
        self.assertIn("revalidates authority", commit_step["note"])
        self.assertIn("historical ledger custody", commit_step["note"])
        recovery = {item["condition"]: item["action"] for item in brief["recovery"]}
        self.assertIn("missing-or-stale-NEXT.md", recovery)
        self.assertIn(
            "ledger-commit-succeeded-but-sidecar-receipt-is-missing",
            recovery,
        )
        self.assertIn(
            "later turns have advanced",
            recovery["ledger-commit-succeeded-but-sidecar-receipt-is-missing"],
        )

    def test_bare_cube_reports_missing_roles_without_mutation(self) -> None:
        path = Path(self.temporary.name) / "bare"
        with Cube.init(path, owner_id="owner", owner_label="Owner") as cube:
            head = cube.head()
            events = cube.event_count()
            target = describe_model_reference(path)
            brief = build_model_brief(
                cube,
                reference=target["reference"],
                resolved_cube_path=target["resolved_cube_path"],
                reference_kind=target["reference_kind"],
                campaign=target["campaign"],
                profile="workspace",
            )
            self.assertFalse(brief["readiness"]["cube_ready_for_governed_turn"])
            self.assertEqual(
                [item["code"] for item in brief["readiness"]["blockers"]],
                ["audience-agent-missing", "actor-agent-missing"],
            )
            self.assertEqual(cube.head(), head)
            self.assertEqual(cube.event_count(), events)

    def test_markdown_is_directly_operational_not_an_essay(self) -> None:
        brief, _, _ = self.build_brief("orchestrated")
        rendered = model_brief_markdown(brief)
        self.assertIn("use this brief; do not merely summarize it", rendered)
        self.assertIn("Will you DM?", rendered)
        self.assertIn("./lacuna turn run begin", rendered)
        self.assertIn("./lacuna turn run status", rendered)
        self.assertIn("./lacuna turn run dispatch", rendered)
        self.assertIn("./lacuna turn run accept", rendered)
        self.assertIn("./lacuna turn run commit", rendered)
        self.assertIn("Only the parent/coordinator may run `turn run commit`", rendered)
        self.assertIn('"schema": "lacuna.model-brief.v1"', rendered)

    @unittest.skipUnless(
        Draft202012Validator is not None,
        "jsonschema test extra is not installed",
    )
    def test_generated_brief_validates_against_exchange_schema(self) -> None:
        brief, _, _ = self.build_brief("orchestrated")
        schema = json.loads(
            (ROOT / "schemas" / "model-brief.v1.schema.json").read_text(
                encoding="utf-8"
            )
        )
        assert Draft202012Validator is not None
        Draft202012Validator(schema).validate(brief)

    def test_unknown_profile_is_refused(self) -> None:
        target = describe_model_reference(self.library_path)
        with Cube.open(target["resolved_cube_path"]) as cube:
            with self.assertRaises(LacunaError) as caught:
                build_model_brief(
                    cube,
                    reference=target["reference"],
                    resolved_cube_path=target["resolved_cube_path"],
                    reference_kind=target["reference_kind"],
                    campaign=target["campaign"],
                    profile="magic",
                )
        self.assertEqual(caught.exception.code, "unknown-model-profile")

    def test_failed_cube_verification_blocks_governed_start_without_leaking_details(self) -> None:
        target = describe_model_reference(self.library_path)
        with Cube.open(target["resolved_cube_path"]) as cube:
            cube.conn.execute(
                "UPDATE changesets SET operation_count = operation_count + 1 WHERE actor_id = ?",
                ("system",),
            )
            cube.conn.commit()
            brief = build_model_brief(
                cube,
                reference=target["reference"],
                resolved_cube_path=target["resolved_cube_path"],
                reference_kind=target["reference_kind"],
                campaign=target["campaign"],
                profile="workspace",
            )
        self.assertFalse(brief["readiness"]["checks"]["ledger_verified"])
        self.assertFalse(brief["readiness"]["cube_ready_for_governed_turn"])
        self.assertEqual(
            brief["readiness"]["blockers"][0]["code"],
            "cube-verification-failed",
        )
        self.assertNotIn("change-operation-count", str(brief["readiness"]))

    def test_unknown_reference_kind_is_refused(self) -> None:
        target = describe_model_reference(self.library_path)
        with Cube.open(target["resolved_cube_path"]) as cube:
            with self.assertRaises(LacunaError) as caught:
                build_model_brief(
                    cube,
                    reference=target["reference"],
                    resolved_cube_path=target["resolved_cube_path"],
                    reference_kind="guess",
                    campaign=target["campaign"],
                    profile="workspace",
                )
        self.assertEqual(caught.exception.code, "unknown-model-reference-kind")

    def test_operator_loop_uses_actual_receipt_shape(self) -> None:
        brief, _, _ = self.build_brief("workspace")
        final_step = brief["operator_loop"][-1]
        self.assertEqual(final_step["action"], "present-only-accepted-narration")
        self.assertIn("top-level narration field", final_step["source"])
        self.assertNotIn("receipt.narration", str(brief))

    def test_generated_run_command_fails_closed_and_preserves_shell_metacharacters(self) -> None:
        brief, _, _ = self.build_brief("workspace")
        begin_step = next(
            item
            for item in brief["operator_loop"]
            if item["action"] == "begin-request-scoped-turn-run"
        )
        command = begin_step["command"]
        injected_path = Path("/tmp/lacuna-model-entrance-injected")
        injected_path.unlink(missing_ok=True)
        run_root = Path(self.temporary.name) / "generated-runs"

        with Cube.open(self.campaign["path"]) as cube:
            before_events = cube.event_count()

        unset_env = os.environ.copy()
        unset_env.pop("PLAYER_INPUT", None)
        unset_env["LACUNA_RUN_ROOT"] = str(run_root)
        refused = subprocess.run(
            ["bash", "-c", command],
            cwd=ROOT,
            env=unset_env,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertNotEqual(refused.returncode, 0)
        self.assertFalse(run_root.exists())
        with Cube.open(self.campaign["path"]) as cube:
            self.assertEqual(cube.event_count(), before_events)

        exact_input = "I say 'hello'; $(touch /tmp/lacuna-model-entrance-injected)\nthen wait."
        set_env = os.environ.copy()
        set_env["PLAYER_INPUT"] = exact_input
        set_env["LACUNA_INPUT_KIND"] = "session-control"
        set_env["LACUNA_RUN_ROOT"] = str(run_root)
        accepted = subprocess.run(
            ["bash", "-c", command],
            cwd=ROOT,
            env=set_env,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(accepted.returncode, 0, accepted.stderr)
        manifest = json.loads(accepted.stdout)
        run_path = Path(manifest["run_path"])
        self.assertEqual(run_path.parent, run_root.resolve())
        self.assertFalse(manifest["include_planner_context_on_commit"])
        self.assertEqual(
            (run_path / "00-player-input.txt").read_text(encoding="utf-8"),
            exact_input,
        )
        packet = json.loads((run_path / "10-turn-packet.json").read_text(encoding="utf-8"))
        self.assertEqual(packet["player_input"], exact_input)
        self.assertEqual(packet["input_kind"], "session-control")
        self.assertFalse(injected_path.exists())
        with Cube.open(self.campaign["path"]) as cube:
            self.assertEqual(cube.event_count(), before_events + 1)

        injected_path.unlink(missing_ok=True)

    def test_generated_run_command_rejects_unknown_input_kind_before_mutation(self) -> None:
        brief, _, _ = self.build_brief("workspace")
        command = next(
            item["command"]
            for item in brief["operator_loop"]
            if item["action"] == "begin-request-scoped-turn-run"
        )
        run_root = Path(self.temporary.name) / "invalid-kind-runs"
        with Cube.open(self.campaign["path"]) as cube:
            before_events = cube.event_count()
        env = os.environ.copy()
        env["PLAYER_INPUT"] = "Will you DM?"
        env["LACUNA_INPUT_KIND"] = "fiction-ish"
        env["LACUNA_RUN_ROOT"] = str(run_root)
        refused = subprocess.run(
            ["bash", "-c", command],
            cwd=ROOT,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(refused.returncode, 2)
        self.assertIn("must be play-turn or session-control", refused.stderr)
        self.assertFalse(run_root.exists())
        with Cube.open(self.campaign["path"]) as cube:
            self.assertEqual(cube.event_count(), before_events)

    def test_turn_template_is_safe_and_committable_as_narration_only(self) -> None:
        with Cube.open(self.campaign["path"]) as cube:
            packet = build_turn_packet(
                cube,
                audience_id="player",
                actor_id="narrator",
                player_input="Will you DM?",
                director=True,
            )
            template = packet["response_contract"]["proposal_template"]
            self.assertEqual(template["operations"], [])
            self.assertEqual(template["revealed_assertion_ids"], [])
            self.assertNotIn("replace.me", str(packet))
            template["narration"] = "Rain stipples the dark glass above an unopened door."
            receipt = commit_turn_proposal(
                cube,
                template,
                include_planner_context=True,
            )
            self.assertEqual(receipt["narration"], template["narration"])
            self.assertEqual(receipt["revealed_assertion_ids"], [])
            self.assertEqual(receipt["change"]["operation_count"], 1)
            self.assertEqual(cube.verify()["overall_status"], "pass")


if __name__ == "__main__":
    unittest.main()
