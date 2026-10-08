from __future__ import annotations

import copy
import json
import os
import stat
import sys
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from lacuna.campaigns import CampaignLibrary
from lacuna.entrance import describe_model_reference
from lacuna.errors import LacunaError
from lacuna.store import Cube
from lacuna.turnruns import (
    ARTIFACT_FILES,
    NEXT_FILE,
    RUN_LOCK_FILE,
    RUN_MANIFEST_FILE,
    accept_turn_run_artifact,
    audit_turn_run,
    begin_turn_run,
    commit_turn_run,
)
from lacuna.turns import build_turn_packet, commit_prepared_turn
from lacuna.util import atomic_write_json, canonical_json, sha256_text


class TurnRunTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.library_path = self.root / "library"
        self.run_root = self.root / "runs"
        library = CampaignLibrary.ensure(self.library_path)
        self.campaign = library.create_campaign(
            slug="mirror-lake",
            title="Mirror Lake",
            summary="A campaign for request-scoped turn run tests.",
        )
        self.target = describe_model_reference(self.library_path)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def begin(
        self,
        *,
        mode: str = "auto",
        director: bool = True,
        allow_anchor: bool = False,
        player_input: str = "I listen at the greenhouse door.",
    ) -> dict:
        with Cube.open(self.target["resolved_cube_path"]) as cube:
            return begin_turn_run(
                cube,
                reference=self.target["reference"],
                resolved_cube_path=self.target["resolved_cube_path"],
                root=self.run_root,
                player_input=player_input,
                audience_id="player",
                actor_id="narrator",
                director=director,
                world_id=None,
                allow_anchor=allow_anchor,
                mode=mode,
                include_planner_context_on_commit=director,
            )

    @staticmethod
    def read_json(run: dict, key: str) -> dict:
        return json.loads(
            (Path(run["run_path"]) / ARTIFACT_FILES[key]).read_text(encoding="utf-8")
        )

    def planner_return(self, run: dict) -> dict:
        card = self.read_json(run, "planner_card")
        result = copy.deepcopy(card["output_contract"]["template"])
        result["observable_plan"] = [
            "An irregular metallic tap is audible beyond the greenhouse door."
        ]
        result["preserved_unknowns"] = ["The source of the tapping remains unknown."]
        return result

    def narrator_return(self, run: dict) -> dict:
        card = self.read_json(run, "narrator_card")
        result = copy.deepcopy(card["output_contract"]["template"])
        result["narration"] = (
            "Beyond the sealed glass, metal touches metal once—then, after an uneven pause, once again."
        )
        result["directly_observable_facts"] = [
            "An irregular metallic tapping is audible beyond the door."
        ]
        return result

    def advance_to_proposal_stage(self, run: dict) -> dict:
        run = accept_turn_run_artifact(run["run_path"], self.planner_return(run))
        run = accept_turn_run_artifact(run["run_path"], self.narrator_return(run))
        return run

    @staticmethod
    def verifier_return(run_path: str | Path, *, status: str) -> dict:
        card = json.loads(
            (Path(run_path) / ARTIFACT_FILES["verifier_card"]).read_text(
                encoding="utf-8"
            )
        )
        result = copy.deepcopy(card["output_contract"]["template"])
        result["status"] = status
        if status == "pass":
            result["findings"] = []
            result["recommended_action"] = "commit-the-exact-reviewed-proposal"
        else:
            result["findings"] = [
                {
                    "code": "continuity-review-refused",
                    "severity": "blocker",
                    "path": "$.narration",
                    "message": "The independent reviewer is not satisfied with continuity.",
                }
            ]
            result["recommended_action"] = "do-not-commit-start-a-fresh-run"
        return result


    def ready_pair(self) -> dict:
        run = self.begin(mode="pair")
        run = self.advance_to_proposal_stage(run)
        proposal = self.read_json(run, "proposal_draft")
        return accept_turn_run_artifact(run["run_path"], proposal)

    def test_ready_state_contains_exact_rollback_preparation_without_mutation(self) -> None:
        with Cube.open(self.target["resolved_cube_path"]) as cube:
            before = cube.event_count()
        run = self.ready_pair()
        self.assertEqual(run["status"], "ready-to-commit")
        preparation = self.read_json(run, "preparation")
        self.assertEqual(preparation["schema"], "lacuna.turn-preparation.v1")
        self.assertEqual(preparation["change"]["after_head"], preparation["head"])
        self.assertEqual(
            preparation["change"]["event_ids"],
            [event["event_id"] for event in preparation["event_chain"]],
        )
        self.assertEqual(run["next_action"]["input_path"], str(Path(run["run_path"]) / ARTIFACT_FILES["preparation"]))
        with Cube.open(self.target["resolved_cube_path"]) as cube:
            # Only build_turn_packet's request-source event is durable; preparation rolled back.
            self.assertEqual(cube.event_count(), before + 1)
            self.assertIsNone(cube.committed_change(preparation["proposal_id"]))

    def test_kernel_invalid_proposal_never_becomes_ready(self) -> None:
        run = self.begin(mode="solo")
        proposal = self.read_json(run, "proposal_draft")
        proposal["narration"] = "The greenhouse remains quiet."
        proposal["operations"] = [
            {
                "op": "set_world_status",
                "world_id": "wld_missing",
                "status": "live",
                "reason": "Exercise fail-closed preflight.",
            }
        ]
        with Cube.open(self.target["resolved_cube_path"]) as cube:
            before = cube.event_count()
        with self.assertRaises(LacunaError) as caught:
            accept_turn_run_artifact(run["run_path"], proposal)
        self.assertIn(caught.exception.code, {"unknown-world", "turn-world-scope-violation"})
        audited = audit_turn_run(run["run_path"])
        self.assertEqual(audited["status"], "awaiting-solo-proposal")
        self.assertIsNone(audited["artifacts"]["proposal"])
        self.assertIsNone(audited["artifacts"]["preparation"])
        with Cube.open(self.target["resolved_cube_path"]) as cube:
            self.assertEqual(cube.event_count(), before)

    def test_commit_retry_recovers_exact_change_after_later_head(self) -> None:
        run = self.ready_pair()
        proposal = self.read_json(run, "proposal")
        preparation = self.read_json(run, "preparation")
        with Cube.open(self.target["resolved_cube_path"]) as cube:
            direct = commit_prepared_turn(
                cube,
                proposal,
                preparation,
                include_planner_context=True,
            )
            committed_count = cube.event_count()
            self.assertEqual(direct["delivery"]["mode"], "direct")
        # Simulate a later successful command after the DB commit but before this
        # run's sidecar receipt/manifest transition was written.
        with Cube.open(self.target["resolved_cube_path"]) as cube:
            build_turn_packet(
                cube,
                audience_id="player",
                actor_id="narrator",
                player_input="A later request advances the durable head.",
            )
            later_count = cube.event_count()
        self.assertGreater(later_count, committed_count)
        self.assertEqual(audit_turn_run(run["run_path"])["status"], "ready-to-commit")
        recovered = commit_turn_run(run["run_path"])
        self.assertEqual(recovered["delivery"]["mode"], "recovered")
        self.assertTrue(recovered["delivery"]["historical_snapshot_used"])
        with Cube.open(self.target["resolved_cube_path"]) as cube:
            self.assertEqual(cube.event_count(), later_count)
        self.assertEqual(audit_turn_run(run["run_path"])["status"], "committed")

    def test_recovery_rejects_rehashed_forged_prepared_context(self) -> None:
        run = self.ready_pair()
        run_path = Path(run["run_path"])
        proposal = self.read_json(run, "proposal")
        preparation = self.read_json(run, "preparation")
        with Cube.open(self.target["resolved_cube_path"]) as cube:
            commit_prepared_turn(
                cube,
                proposal,
                preparation,
                include_planner_context=True,
            )
        preparation["audience_context"]["forged"] = True
        atomic_write_json(run_path / ARTIFACT_FILES["preparation"], preparation)
        manifest = json.loads((run_path / RUN_MANIFEST_FILE).read_text(encoding="utf-8"))
        manifest["artifacts"]["preparation"]["sha256"] = sha256_text(canonical_json(preparation))
        atomic_write_json(run_path / RUN_MANIFEST_FILE, manifest)
        with self.assertRaises(LacunaError) as caught:
            commit_turn_run(run_path)
        self.assertEqual(caught.exception.code, "turn-preparation-context-mismatch")

    @unittest.skipIf(os.name == "nt", "POSIX flock and symlink semantics")
    def test_run_lock_rejects_contention_and_symlink_substitution(self) -> None:
        import fcntl

        run = self.begin(mode="pair")
        run_path = Path(run["run_path"])
        lock_path = run_path / RUN_LOCK_FILE
        with lock_path.open("r+") as handle:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            with self.assertRaises(LacunaError) as caught:
                audit_turn_run(run_path)
            self.assertEqual(caught.exception.code, "turn-run-busy")
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)

        target = self.root / "lock-target"
        target.write_text("do not touch", encoding="utf-8")
        lock_path.unlink()
        lock_path.symlink_to(target)
        with self.assertRaises(LacunaError) as caught:
            audit_turn_run(run_path)
        self.assertEqual(caught.exception.code, "turn-run-lock-unsafe")
        self.assertEqual(target.read_text(encoding="utf-8"), "do not touch")

    def test_pair_run_preserves_exact_input_advances_and_commits(self) -> None:
        exact_input = "I say '$HOME'; then `wait`.\r\nDo not normalize this line."
        with Cube.open(self.target["resolved_cube_path"]) as cube:
            before = cube.event_count()
        run = self.begin(player_input=exact_input)
        self.assertEqual(run["selected_mode"], "pair")
        self.assertEqual(run["status"], "awaiting-planner")
        run_path = Path(run["run_path"])
        self.assertEqual(
            stat.S_IMODE(run_path.stat().st_mode),
            stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR,
        )
        with (run_path / ARTIFACT_FILES["player_input"]).open(
            "r", encoding="utf-8", newline=""
        ) as handle:
            self.assertEqual(handle.read(), exact_input)
        packet = self.read_json(run, "packet")
        self.assertEqual(packet["player_input"], exact_input)
        self.assertEqual(packet["player_input_sha256"], sha256_text(exact_input))
        self.assertIn("Owner: **lacuna-planner**", (run_path / NEXT_FILE).read_text())
        self.assertIn("lacuna_planner", (run_path / NEXT_FILE).read_text())
        with Cube.open(self.target["resolved_cube_path"]) as cube:
            self.assertEqual(cube.event_count(), before + 1)

        run = self.advance_to_proposal_stage(run)
        self.assertEqual(run["status"], "awaiting-pair-proposal")
        draft = self.read_json(run, "proposal_draft")
        self.assertEqual(draft["operations"], [])
        self.assertEqual(draft["revealed_assertion_ids"], [])
        self.assertNotEqual(draft["narration"], "Write only what the audience experiences now.")
        with Cube.open(self.target["resolved_cube_path"]) as cube:
            self.assertEqual(cube.event_count(), before + 1)

        run = accept_turn_run_artifact(run["run_path"], draft)
        self.assertEqual(run["status"], "ready-to-commit")
        receipt = commit_turn_run(run["run_path"])
        self.assertEqual(receipt["overall_status"], "pass")
        self.assertEqual(receipt["narration"], draft["narration"])
        committed = audit_turn_run(run["run_path"])
        self.assertEqual(committed["status"], "committed")
        self.assertEqual(committed["next_action"]["owner"], "parent-coordinator")
        self.assertIn(
            "passing receipt narration may now be presented",
            committed["next_action"]["player_visibility"],
        )

    def test_full_run_requires_independent_pass_and_refusal_is_terminal(self) -> None:
        refused = self.begin(mode="full", allow_anchor=True)
        refused = self.advance_to_proposal_stage(refused)
        self.assertEqual(refused["status"], "awaiting-proposal-builder")
        proposal = copy.deepcopy(
            self.read_json(refused, "proposal_builder_card")["output_contract"]["template"]
        )
        refused = accept_turn_run_artifact(refused["run_path"], proposal)
        self.assertEqual(refused["status"], "awaiting-verifier")
        refusal = self.verifier_return(refused["run_path"], status="refuse")
        refused = accept_turn_run_artifact(refused["run_path"], refusal)
        self.assertEqual(refused["status"], "verifier-refused")
        with self.assertRaises(LacunaError) as caught:
            commit_turn_run(refused["run_path"])
        self.assertEqual(caught.exception.code, "turn-run-not-ready")
        with self.assertRaises(LacunaError) as caught:
            accept_turn_run_artifact(refused["run_path"], refusal)
        self.assertEqual(caught.exception.code, "turn-run-verifier-refused")

        passed = self.begin(mode="full", allow_anchor=True)
        passed = self.advance_to_proposal_stage(passed)
        proposal = copy.deepcopy(
            self.read_json(passed, "proposal_builder_card")["output_contract"]["template"]
        )
        passed = accept_turn_run_artifact(passed["run_path"], proposal)
        passed = accept_turn_run_artifact(
            passed["run_path"], self.verifier_return(passed["run_path"], status="pass")
        )
        self.assertEqual(passed["status"], "ready-to-commit")
        self.assertEqual(commit_turn_run(passed["run_path"])["overall_status"], "pass")

    def test_placeholder_stale_head_and_cross_turn_returns_fail_closed(self) -> None:
        solo = self.begin(mode="solo", director=False)
        unchanged = self.read_json(solo, "proposal_draft")
        with self.assertRaises(LacunaError) as caught:
            accept_turn_run_artifact(solo["run_path"], unchanged)
        self.assertEqual(caught.exception.code, "unreplaced-narration-template")
        self.assertEqual(audit_turn_run(solo["run_path"])["status"], "awaiting-solo-proposal")
        self.assertIn("response_contract proposal template", solo["next_action"]["action"])
        self.assertTrue(solo["next_action"]["input_path"].endswith("10-turn-packet.json"))

        proposal = copy.deepcopy(unchanged)
        proposal["narration"] = "Rain ticks once against the greenhouse glass."
        solo = accept_turn_run_artifact(solo["run_path"], proposal)
        with Cube.open(self.target["resolved_cube_path"]) as cube:
            build_turn_packet(
                cube,
                audience_id="player",
                actor_id="narrator",
                player_input="A separate request advances the cube head.",
            )
        with self.assertRaises(LacunaError) as caught:
            commit_turn_run(solo["run_path"])
        self.assertEqual(caught.exception.code, "stale-head")
        audited = audit_turn_run(solo["run_path"])
        self.assertEqual(audited["status"], "ready-to-commit")
        self.assertIsNone(audited["artifacts"]["receipt"])

        first = self.begin(mode="pair")
        second = self.begin(mode="pair")
        with self.assertRaises(LacunaError) as caught:
            accept_turn_run_artifact(second["run_path"], self.planner_return(first))
        self.assertEqual(caught.exception.code, "handoff-binding-mismatch")
        self.assertEqual(audit_turn_run(second["run_path"])["status"], "awaiting-planner")

    def test_audit_detects_artifact_next_pointer_and_topology_tampering(self) -> None:
        run = self.begin(mode="pair")
        run_path = Path(run["run_path"])
        packet_path = run_path / ARTIFACT_FILES["packet"]
        packet = json.loads(packet_path.read_text(encoding="utf-8"))
        packet["player_input"] += " altered"
        atomic_write_json(packet_path, packet)
        with self.assertRaises(LacunaError) as caught:
            audit_turn_run(run_path)
        self.assertEqual(caught.exception.code, "turn-run-artifact-digest-mismatch")

        fresh = self.begin(mode="pair")
        fresh_path = Path(fresh["run_path"])
        (fresh_path / NEXT_FILE).write_text("wrong next action\n", encoding="utf-8")
        with self.assertRaises(LacunaError) as caught:
            audit_turn_run(fresh_path)
        self.assertEqual(caught.exception.code, "turn-run-next-pointer-mismatch")

        topology = self.begin(mode="pair")
        topology_path = Path(topology["run_path"])
        impossible = {"note": "a valid JSON file in an impossible stage"}
        atomic_write_json(topology_path / ARTIFACT_FILES["proposal_builder_card"], impossible)
        manifest_path = topology_path / RUN_MANIFEST_FILE
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["artifacts"]["proposal_builder_card"] = {
            "path": ARTIFACT_FILES["proposal_builder_card"],
            "sha256": sha256_text(canonical_json(impossible)),
            "media_type": "application/json",
            "schema": "lacuna.turn-task-card.v1",
            "role": "lacuna-proposal-builder",
        }
        atomic_write_json(manifest_path, manifest)
        with self.assertRaises(LacunaError) as caught:
            audit_turn_run(topology_path)
        self.assertEqual(caught.exception.code, "turn-run-artifact-topology-mismatch")

    def test_begin_refuses_cube_path_not_bound_to_open_cube_before_publication(self) -> None:
        other = self.root / "other-cube"
        with Cube.init(other):
            pass
        with Cube.open(self.target["resolved_cube_path"]) as cube:
            with self.assertRaises(LacunaError) as caught:
                begin_turn_run(
                    cube,
                    reference=str(other),
                    resolved_cube_path=str(other.resolve()),
                    root=self.run_root,
                    player_input="This must not bind to the wrong cube.",
                    audience_id="player",
                    actor_id="narrator",
                    director=False,
                    world_id=None,
                    allow_anchor=False,
                    mode="solo",
                    include_planner_context_on_commit=False,
                )
        self.assertEqual(caught.exception.code, "turn-run-cube-path-mismatch")
        self.assertFalse(self.run_root.exists())

    def test_failed_initial_turn_publication_leaves_no_visible_or_staged_run(self) -> None:
        with patch("lacuna.turnruns._write_manifest", side_effect=RuntimeError("synthetic publication failure")):
            with self.assertRaises(RuntimeError):
                self.begin(mode="solo", director=False)
        self.assertTrue(self.run_root.is_dir())
        self.assertEqual(list(self.run_root.iterdir()), [])

    def test_audit_rejects_artifact_role_metadata_relabeling(self) -> None:
        run = self.begin(mode="pair")
        manifest_path = Path(run["run_path"]) / RUN_MANIFEST_FILE
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["artifacts"]["planner_card"]["role"] = "lacuna-narrator"
        atomic_write_json(manifest_path, manifest)
        with self.assertRaises(LacunaError) as caught:
            audit_turn_run(run["run_path"])
        self.assertEqual(caught.exception.code, "turn-run-artifact-metadata-mismatch")


if __name__ == "__main__":
    unittest.main()
