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

from lacuna.checkpoints import build_checkpoint_request
from lacuna.errors import LacunaError
import lacuna.public_history as public_history_module
from lacuna.public_history import (
    authenticate_public_history,
    build_complete_public_history,
    build_public_history,
    build_public_history_view,
    public_history_markdown,
    public_history_sha256,
    public_history_view_sha256,
    validate_public_history,
    validate_public_history_view,
)
from lacuna.sidecars import canonical_json_digest
from lacuna.store import Cube
from lacuna.turns import build_turn_packet, commit_turn_proposal
from lacuna.turnruns import (
    ARTIFACT_FILES,
    accept_turn_run_artifact,
    begin_turn_run,
    commit_turn_run,
)
from lacuna.util import sha256_text


class PublicHistoryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.base = Path(self.temporary.name)
        self.cube_path = self.base / "cube"
        cube = Cube.init(self.cube_path, owner_id="user", owner_label="User")
        cube.apply_operations(
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
            message="public history participants",
        )
        cube.close()

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def commit_turn(
        self,
        *,
        root_name: str,
        player_input: str,
        narration: str,
        input_kind: str = "play-turn",
    ) -> Path:
        with Cube.open(self.cube_path) as cube:
            run = begin_turn_run(
                cube,
                reference=str(self.cube_path),
                resolved_cube_path=str(self.cube_path.resolve()),
                root=self.base / root_name,
                player_input=player_input,
                input_kind=input_kind,
                audience_id="player",
                actor_id="narrator",
                director=False,
                world_id=None,
                allow_anchor=False,
                mode="solo",
                include_planner_context_on_commit=False,
            )
        run_path = Path(run["run_path"])
        proposal = json.loads(
            (run_path / ARTIFACT_FILES["proposal_draft"]).read_text(encoding="utf-8")
        )
        proposal["narration"] = narration
        ready = accept_turn_run_artifact(run_path, proposal)
        self.assertEqual(ready["status"], "ready-to-commit")
        receipt = commit_turn_run(run_path)
        self.assertEqual(receipt["overall_status"], "pass")
        return run_path

    def test_build_validates_and_renders_exact_public_history(self) -> None:
        first = self.commit_turn(
            root_name="turn-one",
            player_input="I touch the blue door.",
            narration="The blue door is cold and visibly has no handle.",
        )
        second = self.commit_turn(
            root_name="turn-two",
            player_input="I ask whether anyone is inside.",
            narration="From beyond the glass, someone whispers, ‘Not yet.’",
        )
        history = build_public_history([first, second])
        self.assertEqual(history, validate_public_history(history))
        with Cube.open(self.cube_path) as cube:
            self.assertEqual(history, authenticate_public_history(cube, history))
        self.assertEqual(history["coverage"]["entry_count"], 2)
        self.assertEqual(history["coverage"]["mode"], "explicit-run-list")
        self.assertEqual(history["coverage"]["completeness"], "not-claimed")
        self.assertEqual(history["public_entries"][0]["player_input"], "I touch the blue door.")
        self.assertEqual(
            history["public_entries"][0]["narration"],
            "The blue door is cold and visibly has no handle.",
        )
        self.assertLess(
            history["source_custody"][0]["commit_event_seq"],
            history["source_custody"][1]["request_event_seq"],
        )
        self.assertRegex(public_history_sha256(history), r"^[0-9a-f]{64}$")
        rendered = public_history_markdown(history)
        self.assertIn("The blue door is cold", rendered)
        self.assertNotIn("planner_context", rendered)
        view = build_public_history_view(history)
        self.assertEqual(view, validate_public_history_view(view))
        self.assertEqual(view["public_entries"], history["public_entries"])
        self.assertEqual(
            view["public_entries_sha256"],
            history["coverage"]["public_entries_sha256"],
        )
        self.assertNotIn("source_custody", view)
        self.assertRegex(public_history_view_sha256(view), r"^[0-9a-f]{64}$")
        if Draft202012Validator is not None:
            schema = json.loads(
                (ROOT / "schemas" / "public-history.v2.schema.json").read_text(
                    encoding="utf-8"
                )
            )
            Draft202012Validator(schema).validate(history)
            view_schema = json.loads(
                (ROOT / "schemas" / "public-history-view.v2.schema.json").read_text(
                    encoding="utf-8"
                )
            )
            Draft202012Validator(view_schema).validate(view)
            continuation_schema = json.loads(
                (
                    ROOT
                    / "schemas"
                    / "checkpoint-continuation-dispatch.v2.schema.json"
                ).read_text(encoding="utf-8")
            )
            embedded_view = continuation_schema["$defs"]["publicHistoryView"]
            for field in ("type", "additionalProperties", "required", "properties"):
                self.assertEqual(view_schema[field], embedded_view[field])

        proc = subprocess.run(
            [str(ROOT / "lacuna"), "history", "build", str(first), str(second)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(json.loads(proc.stdout), history)

    def test_reversed_uncommitted_and_mixed_cube_runs_fail_closed(self) -> None:
        first = self.commit_turn(
            root_name="ordered-one",
            player_input="First.",
            narration="First accepted narration.",
        )
        second = self.commit_turn(
            root_name="ordered-two",
            player_input="Second.",
            narration="Second accepted narration.",
        )
        with self.assertRaises(LacunaError) as caught:
            build_public_history([second, first])
        self.assertEqual(caught.exception.code, "public-history-order-mismatch")

        with Cube.open(self.cube_path) as cube:
            uncommitted = begin_turn_run(
                cube,
                reference=str(self.cube_path),
                resolved_cube_path=str(self.cube_path.resolve()),
                root=self.base / "uncommitted",
                player_input="Not committed.",
                input_kind="play-turn",
                audience_id="player",
                actor_id="narrator",
                director=False,
                world_id=None,
                allow_anchor=False,
                mode="solo",
                include_planner_context_on_commit=False,
            )
        with self.assertRaises(LacunaError) as caught:
            build_public_history([uncommitted["run_path"]])
        self.assertEqual(caught.exception.code, "turn-run-not-committed")

        other_path = self.base / "other-cube"
        other = Cube.init(other_path, owner_id="user", owner_label="User")
        other.apply_operations(
            actor_id="user",
            operations=[
                {"op": "register_agent", "agent_id": "player", "kind": "human", "label": "Player", "metadata": {}},
                {"op": "register_agent", "agent_id": "narrator", "kind": "narrator", "label": "Narrator", "metadata": {}},
            ],
        )
        other.close()
        original = self.cube_path
        self.cube_path = other_path
        try:
            other_run = self.commit_turn(
                root_name="other-run",
                player_input="Elsewhere.",
                narration="A different cube answers.",
            )
        finally:
            self.cube_path = original
        with self.assertRaises(LacunaError) as caught:
            build_public_history([first, other_run])
        self.assertEqual(caught.exception.code, "public-history-cube-mismatch")

    def test_tampering_and_unknown_ledger_heads_are_refused(self) -> None:
        run = self.commit_turn(
            root_name="tamper-turn",
            player_input="Remember this exactly.",
            narration="This sentence is accepted exactly once.",
        )
        history = build_public_history([run])
        tampered = copy.deepcopy(history)
        tampered["public_entries"][0]["narration"] += " forged"
        with self.assertRaises(LacunaError) as caught:
            validate_public_history(tampered)
        self.assertEqual(caught.exception.code, "bad-public-history")

        with Cube.open(self.cube_path) as cube:
            self.assertEqual(cube.event_sequence("0" * 64), 0)
            with self.assertRaises(LacunaError) as caught:
                cube.event_sequence("f" * 64)
            self.assertEqual(caught.exception.code, "unknown-ledger-head")

    def test_self_consistent_rehashed_prose_forgery_fails_ledger_authentication(self) -> None:
        run = self.commit_turn(
            root_name="forgery-turn",
            player_input="Keep the public words bound to the cube.",
            narration="The accepted reply remains exactly this sentence.",
        )
        forged = copy.deepcopy(build_public_history([run]))
        forged_text = "A forged replacement that never reached the cube."
        forged["public_entries"][0]["narration"] = forged_text
        forged["source_custody"][0]["narration_sha256"] = sha256_text(forged_text)
        entries_sha = canonical_json_digest(
            forged["public_entries"],
            error_code="bad-public-history",
            label="public history entries",
        )
        custody_sha = canonical_json_digest(
            forged["source_custody"],
            error_code="bad-public-history",
            label="public history source custody",
        )
        forged["coverage"]["public_entries_sha256"] = entries_sha
        forged["coverage"]["source_custody_sha256"] = custody_sha
        ledger_turns_sha = canonical_json_digest(
            public_history_module._ledger_turns_projection(forged["source_custody"]),
            error_code="bad-public-history",
            label="public history ledger turn custody",
        )
        forged["coverage"]["ledger_turns_sha256"] = ledger_turns_sha
        forged["history_id"] = public_history_module._history_id(
            cube_id=forged["cube_id"],
            audience_id=forged["audience_id"],
            coverage_mode=forged["coverage"]["mode"],
            completeness=forged["coverage"]["completeness"],
            boundary=forged["coverage"]["boundary"],
            public_entries_sha256=entries_sha,
            source_custody_sha256=custody_sha,
            ledger_turns_sha256=ledger_turns_sha,
        )

        self.assertEqual(forged, validate_public_history(forged))
        with Cube.open(self.cube_path) as cube:
            with self.assertRaises(LacunaError) as caught:
                authenticate_public_history(cube, forged)
        self.assertEqual(caught.exception.code, "public-history-ledger-mismatch")

    def checkpoint_boundary(self) -> dict:
        with Cube.open(self.cube_path) as cube:
            request = build_checkpoint_request(
                cube,
                audience_id="player",
                actor_id="narrator",
                trigger="Compare bounded explanations.",
                candidate_count=2,
                rollout_horizon_turns=2,
                compression_max_chars=1000,
                max_operations=4,
            )
            packet = request["turn_packet"]
            return {
                "checkpoint_run_id": "cpr_fixture",
                "checkpoint_id": request["checkpoint_id"],
                "request_source_id": packet["request_source_id"],
                "request_head": request["expected_head"],
                "request_event_seq": cube.event_sequence(request["expected_head"]),
                "cube_id": request["cube_id"],
                "audience_id": packet["audience_id"],
            }

    def test_complete_history_uses_ledger_census_and_refuses_missing_run(self) -> None:
        first = self.commit_turn(
            root_name="complete-one",
            player_input="I count the windows.",
            narration="There are three windows, each clouded from within.",
        )
        second = self.commit_turn(
            root_name="complete-two",
            player_input="I knock on the middle pane.",
            narration="The middle pane answers with one soft knock.",
        )
        boundary = self.checkpoint_boundary()
        with Cube.open(self.cube_path) as cube:
            history = build_complete_public_history(
                cube,
                checkpoint_boundary=boundary,
                run_roots=[first.parent, second.parent],
            )
            self.assertEqual(history, authenticate_public_history(cube, history))
        self.assertEqual(history["coverage"]["mode"], "complete-before-checkpoint")
        self.assertEqual(history["coverage"]["completeness"], "complete")
        self.assertEqual(history["coverage"]["expected_committed_turn_count"], 2)
        self.assertEqual(
            history["coverage"]["boundary"]["checkpoint_id"],
            boundary["checkpoint_id"],
        )
        self.assertEqual(build_public_history_view(history)["entry_count"], 2)

        with Cube.open(self.cube_path) as cube:
            with self.assertRaises(LacunaError) as caught:
                build_complete_public_history(
                    cube,
                    checkpoint_boundary=boundary,
                    run_roots=[first.parent],
                )
        self.assertEqual(caught.exception.code, "public-history-incomplete")

    def test_complete_history_refuses_a_durable_stateless_turn_without_a_managed_run(self) -> None:
        with Cube.open(self.cube_path) as cube:
            packet = build_turn_packet(
                cube,
                audience_id="player",
                actor_id="narrator",
                player_input="I ask the rain whether it remembers me.",
                input_kind="play-turn",
                director=False,
            )
            proposal = copy.deepcopy(packet["response_contract"]["proposal_template"])
            proposal["narration"] = "The rain gives no answer, but the glass shivers once."
            receipt = commit_turn_proposal(cube, proposal)
            self.assertEqual(receipt["overall_status"], "pass")
        boundary = self.checkpoint_boundary()
        with Cube.open(self.cube_path) as cube:
            with self.assertRaises(LacunaError) as caught:
                build_complete_public_history(
                    cube,
                    checkpoint_boundary=boundary,
                    run_roots=[],
                )
        self.assertEqual(caught.exception.code, "public-history-incomplete")
        self.assertEqual(caught.exception.details["missing_count"], 1)

    def test_complete_history_can_prove_zero_precheckpoint_turns(self) -> None:
        boundary = self.checkpoint_boundary()
        with Cube.open(self.cube_path) as cube:
            history = build_complete_public_history(
                cube,
                checkpoint_boundary=boundary,
                run_roots=[],
            )
        self.assertEqual(history["coverage"]["entry_count"], 0)
        self.assertIsNone(history["coverage"]["last_commit_event_seq"])
        view = build_public_history_view(history)
        self.assertEqual(view["entry_count"], 0)
        self.assertEqual(view["completeness"], "complete")


if __name__ == "__main__":
    unittest.main()
