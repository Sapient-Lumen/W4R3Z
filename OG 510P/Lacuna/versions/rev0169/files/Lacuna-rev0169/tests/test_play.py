from __future__ import annotations

import copy
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from tests._schema_support import Draft202012Validator

import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from lacuna.campaigns import CampaignLibrary
from lacuna.errors import LacunaError
from lacuna.play import start_play
from lacuna.store import Cube
from lacuna.turnruns import ARTIFACT_FILES, accept_turn_run_artifact, audit_turn_run, commit_turn_run


class DirectPlayStartTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_literal_will_you_dm_bootstraps_typed_control_without_fictionalizing_it(self) -> None:
        result = start_play(
            self.root / "game",
            root=self.root / "runs",
            player_input="Will you DM?",
            profile="orchestrated",
            bootstrap=True,
        )
        self.assertEqual(result["schema"], "lacuna.play-start.v1")
        self.assertEqual(result["input_kind"], "session-control")
        self.assertEqual(result["run"]["selected_mode"], "pair")
        run_path = Path(result["run"]["run_path"])
        packet = json.loads((run_path / "10-turn-packet.json").read_text(encoding="utf-8"))
        self.assertEqual(packet["player_input"], "Will you DM?")
        self.assertEqual(packet["input_kind"], "session-control")
        self.assertIn("session-control", json.dumps(json.loads((run_path / "20-planner-card.json").read_text())))
        with Cube.open(result["resolved_cube_path"]) as cube:
            self.assertEqual(len(cube.active_assertions()), 0)
            self.assertEqual(cube.verify()["overall_status"], "pass")
            row = cube.conn.execute(
                "SELECT COUNT(*) AS n FROM sources WHERE source_id = ?",
                (packet["request_source_id"],),
            ).fetchone()
            self.assertEqual(row["n"], 1)

        if Draft202012Validator is not None:
            schema = json.loads((ROOT / "schemas" / "play-start.v1.schema.json").read_text())
            Draft202012Validator(schema).validate(result)

    def test_cli_one_command_start_then_chatgpt_dispatch_and_pointer_recovery(self) -> None:
        game = self.root / "cli-game"
        runs = self.root / "cli-runs"
        started = subprocess.run(
            [
                str(ROOT / "lacuna"),
                "play",
                "start",
                str(game),
                "--root",
                str(runs),
                "--bootstrap",
                "--profile",
                "orchestrated",
                "--format",
                "json",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(started.returncode, 0, started.stderr)
        result = json.loads(started.stdout)
        self.assertEqual(result["input_kind"], "session-control")
        run_path = Path(result["run"]["run_path"])

        dispatched = subprocess.run(
            [
                str(ROOT / "lacuna"),
                "turn",
                "run",
                "dispatch",
                str(run_path),
                "--provider",
                "chatgpt",
                "--format",
                "json",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(dispatched.returncode, 0, dispatched.stderr)
        envelope = json.loads(dispatched.stdout)
        self.assertEqual(envelope["provider"], "chatgpt")
        self.assertEqual(envelope["input_kind"], "session-control")
        self.assertEqual(envelope["input_document"]["schema"], "lacuna.turn-task-card.v1")

        (run_path / "NEXT.md").unlink()
        recovered = subprocess.run(
            [
                str(ROOT / "lacuna"),
                "turn",
                "run",
                "recover",
                str(run_path),
                "--format",
                "json",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(recovered.returncode, 0, recovered.stderr)
        self.assertEqual(json.loads(recovered.stdout)["run_id"], result["run"]["run_id"] )
        self.assertTrue((run_path / "NEXT.md").is_file())

    def test_direct_session_control_can_complete_a_pair_run_and_present_only_receipt_narration(self) -> None:
        result = start_play(
            self.root / "complete-game",
            root=self.root / "complete-runs",
            profile="orchestrated",
            bootstrap=True,
        )
        run = result["run"]
        run_path = Path(run["run_path"])

        planner_card = json.loads(
            (run_path / ARTIFACT_FILES["planner_card"]).read_text(encoding="utf-8")
        )
        planner = copy.deepcopy(planner_card["output_contract"]["template"])
        planner["observable_plan"] = [
            "Open with a low-commitment invitation to choose a character and immediate approach."
        ]
        planner["preserved_unknowns"] = [
            "Setting details and hidden causes remain uncommitted until the player chooses."
        ]
        run = accept_turn_run_artifact(run_path, planner)
        self.assertEqual(run["status"], "awaiting-narrator")

        narrator_card = json.loads(
            (run_path / ARTIFACT_FILES["narrator_card"]).read_text(encoding="utf-8")
        )
        narrator = copy.deepcopy(narrator_card["output_contract"]["template"])
        narrator["narration"] = (
            "Yes. Choose one: the night archivist with a stolen key, or the courier who was never meant to arrive."
        )
        narrator["directly_observable_facts"] = []
        run = accept_turn_run_artifact(run_path, narrator)
        self.assertEqual(run["status"], "awaiting-pair-proposal")

        proposal = json.loads(
            (run_path / ARTIFACT_FILES["proposal_draft"]).read_text(encoding="utf-8")
        )
        self.assertEqual(proposal["operations"], [])
        run = accept_turn_run_artifact(run_path, proposal)
        self.assertEqual(run["status"], "ready-to-commit")

        receipt = commit_turn_run(run_path)
        self.assertEqual(receipt["overall_status"], "pass")
        self.assertEqual(receipt["narration"], narrator["narration"])
        self.assertEqual(audit_turn_run(run_path)["status"], "committed")
        with Cube.open(result["resolved_cube_path"]) as cube:
            self.assertEqual(cube.active_assertions(), [])
            self.assertEqual(cube.verify()["overall_status"], "pass")

    def test_foreign_nonempty_bootstrap_path_refuses_without_overlay(self) -> None:
        foreign = self.root / "foreign"
        foreign.mkdir()
        marker = foreign / "keep.txt"
        marker.write_text("do not touch", encoding="utf-8")
        before = {path.name: path.read_bytes() for path in foreign.iterdir()}
        with self.assertRaises(LacunaError) as caught:
            start_play(
                foreign,
                root=self.root / "runs",
                bootstrap=True,
            )
        self.assertEqual(caught.exception.code, "unsafe-play-bootstrap-path")
        self.assertEqual({path.name: path.read_bytes() for path in foreign.iterdir()}, before)
        self.assertFalse((foreign / "lacuna-library.json").exists())

    def test_unselected_single_campaign_is_selected_but_multiple_are_not_guessed(self) -> None:
        library_path = self.root / "library"
        library = CampaignLibrary.ensure(library_path)
        first = library.create_campaign(slug="first", title="First")
        library.config["selected_campaign_id"] = None
        library._write_config()
        result = start_play(
            library_path,
            root=self.root / "runs-one",
            profile="workspace",
        )
        self.assertIn(f"selected-campaign:{first['campaign_id']}", result["bootstrap_actions"])
        self.assertEqual(result["run"]["selected_mode"], "solo")

        library.create_campaign(slug="second", title="Second")
        library.config["selected_campaign_id"] = None
        library._write_config()
        before_events = {}
        for campaign in library.campaigns():
            with Cube.open(campaign["path"]) as cube:
                before_events[campaign["campaign_id"]] = cube.event_count()
        with self.assertRaises(LacunaError) as caught:
            start_play(library_path, root=self.root / "runs-many")
        self.assertEqual(caught.exception.code, "ambiguous-play-campaign")
        for campaign in library.campaigns():
            with Cube.open(campaign["path"]) as cube:
                self.assertEqual(cube.event_count(), before_events[campaign["campaign_id"]])


if __name__ == "__main__":
    unittest.main()
