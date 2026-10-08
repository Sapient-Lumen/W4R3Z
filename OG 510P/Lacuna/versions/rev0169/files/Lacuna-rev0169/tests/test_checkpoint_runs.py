from __future__ import annotations

import os
import unittest

import copy
import json
import stat
import subprocess
import tempfile
from unittest.mock import patch
from pathlib import Path

from tests._schema_support import Draft202012Validator

import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from lacuna.checkpoint_runs import (
    ARTIFACT_FILES,
    NEXT_FILE,
    RUN_MANIFEST_FILE,
    accept_checkpoint_run_artifact,
    audit_checkpoint_run,
    begin_checkpoint_continuation_turn,
    begin_checkpoint_run,
    build_checkpoint_continuation_dispatch,
    build_checkpoint_run_dispatch,
    build_checkpoint_run_narrator_capsule,
    commit_checkpoint_run,
    normalize_checkpoint_provider_routes,
    record_checkpoint_run_failure,
    recover_checkpoint_run,
)
from lacuna.continuation import (
    checkpoint_continuation_dispatch_markdown,
    checkpoint_continuation_dispatch_sha256,
    checkpoint_narrator_capsule_sha256,
    validate_checkpoint_continuation_dispatch,
    validate_checkpoint_narrator_capsule,
)
from lacuna.checkpoints import (
    CHECKPOINT_CHECKS,
    CHECKPOINT_SCORE_DIMENSIONS,
    commit_checkpoint,
    validate_checkpoint_candidates,
    validate_checkpoint_compression,
    validate_checkpoint_judgment,
    validate_checkpoint_verifier,
)
from lacuna.errors import LacunaError
from lacuna.providers import provider_alias
from lacuna.public_history import (
    build_public_history,
    build_public_history_view,
    public_history_sha256,
)
from lacuna.store import Cube
from lacuna.turnruns import (
    ARTIFACT_FILES as TURN_ARTIFACT_FILES,
    accept_turn_run_artifact,
    begin_turn_run,
    commit_turn_run,
)
from lacuna.util import atomic_write_json, canonical_json, pretty_json, sha256_text


@unittest.skipUnless(
    os.environ.get("LACUNA_HEAVY_TESTS") == "1",
    "set LACUNA_HEAVY_TESTS=1 to run managed checkpoint sidecar subprocess/lock tests",
)
class ManagedCheckpointRunTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.base = Path(self.temporary.name)
        self.cube_path = self.base / "cube"
        self.run_root = self.base / "checkpoint-runs"
        self.cube = Cube.init(self.cube_path, owner_id="user", owner_label="User")
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
                {
                    "op": "open_question",
                    "question_id": "qst_locked_door",
                    "text": "Who locked the greenhouse door?",
                    "opened_by": "player",
                    "visibility": "private",
                    "audience": [],
                },
            ],
            message="checkpoint run participants and one protected unknown",
        )

    def tearDown(self) -> None:
        self.cube.close()
        self.temporary.cleanup()

    def begin(self, *, routes: dict[str, str] | None = None) -> dict:
        return begin_checkpoint_run(
            self.cube,
            reference=str(self.cube_path),
            resolved_cube_path=str(self.cube_path),
            root=self.run_root,
            audience_id="player",
            actor_id="narrator",
            trigger="Compare bounded explanations before the next reveal.",
            candidate_count=2,
            rollout_horizon_turns=3,
            compression_max_chars=1000,
            max_operations=4,
            provider_routes=routes,
        )

    @staticmethod
    def read_json(run_path: Path, key: str) -> dict:
        return json.loads((run_path / ARTIFACT_FILES[key]).read_text(encoding="utf-8"))

    def candidates(self, run_path: Path) -> dict:
        request = self.read_json(run_path, "request")
        card = self.read_json(run_path, "generator_card")
        result = copy.deepcopy(card["output_contract"]["template"])
        prototype = result["candidates"][0]
        result["candidates"] = []
        for ordinal, title in ((1, "Custodian bargain"), (2, "Storm interlock")):
            item = copy.deepcopy(prototype)
            item.update(
                {
                    "candidate_id": f"candidate.{ordinal}",
                    "title": title,
                    "hypothesis_card": f"{title}: a small contingent hidden-state card.",
                    "story_so_far_explanation": "Explains present details without changing observed canon.",
                    "future_arc_summary": "Creates bounded choices over the requested horizon.",
                    "promoted_incidental_details": [],
                    "commitment_risks": [],
                    "fair_play_risks": [],
                    "identity_drift_risks": [],
                    "provenance": {
                        "provider": "fixture",
                        "model": f"generator-{ordinal}",
                        "model_version": None,
                        "invocation_id": None,
                        "notes": None,
                    },
                }
            )
            item["rollout"]["turns"] = [
                f"Turn {turn}: preserve agency while testing {title}."
                for turn in range(1, request["policy"]["rollout_horizon_turns"] + 1)
            ]
            item["rollout"]["summary"] = "A bounded rollout that preserves player agency."
            result["candidates"].append(item)
        return validate_checkpoint_candidates(result, request)

    def judgment(self, run_path: Path) -> dict:
        request = self.read_json(run_path, "request")
        candidates = self.read_json(run_path, "candidates")
        card = self.read_json(run_path, "judge_card")
        result = copy.deepcopy(card["output_contract"]["template"])
        prototype = result["scores"][0]
        result["assessor"] = {
            "provider": "fixture",
            "model": "judge",
            "model_version": None,
            "invocation_id": None,
            "notes": None,
        }
        result["scores"] = []
        weights = request["policy"]["score_weights"]
        for ordinal, value in ((1, 90), (2, 80)):
            dimensions = {dimension: value for dimension in CHECKPOINT_SCORE_DIMENSIONS}
            score = copy.deepcopy(prototype)
            score.update(
                {
                    "candidate_id": f"candidate.{ordinal}",
                    "eligible": True,
                    "disqualifiers": [],
                    "dimensions": dimensions,
                    "weighted_score": sum(
                        dimensions[dimension] * weights[dimension]
                        for dimension in CHECKPOINT_SCORE_DIMENSIONS
                    ),
                    "rationale": "Preserves canon and leaves meaningful reversible choices.",
                }
            )
            result["scores"].append(score)
        result["selected_candidate_id"] = "candidate.1"
        result["selection_rationale"] = "Highest weighted eligible score."
        return validate_checkpoint_judgment(result, request, candidates)

    def compression(self, run_path: Path) -> dict:
        request = self.read_json(run_path, "request")
        candidates = self.read_json(run_path, "candidates")
        judgment = self.read_json(run_path, "judgment")
        card = self.read_json(run_path, "compressor_card")
        result = copy.deepcopy(card["output_contract"]["template"])
        result["state_card"] = (
            "The custodian made a contingent bargain. Preserve the locked-door question; "
            "press the player with a reversible choice rather than a reveal."
        )
        result["narration"] = (
            "Rain threads down the greenhouse glass. The custodian waits beside the locked door."
        )
        return validate_checkpoint_compression(result, request, candidates, judgment)

    def verifier(self, run_path: Path, *, passing: bool = True) -> dict:
        request = self.read_json(run_path, "request")
        proposal = self.read_json(run_path, "proposal")
        card = self.read_json(run_path, "verifier_card")
        result = copy.deepcopy(card["output_contract"]["template"])
        if passing:
            result["status"] = "pass"
            result["checks"] = {check: True for check in CHECKPOINT_CHECKS}
            result["findings"] = []
            result["recommended_action"] = "commit"
        else:
            result["status"] = "refuse"
            result["checks"] = {check: True for check in CHECKPOINT_CHECKS}
            result["checks"][CHECKPOINT_CHECKS[0]] = False
            result["findings"] = [
                {
                    "severity": "blocking",
                    "code": "fixture-block",
                    "message": "The fixture verifier intentionally refuses this proposal.",
                    "evidence_paths": ["turn_proposal"],
                }
            ]
            result["recommended_action"] = "regenerate"
        return validate_checkpoint_verifier(result, request, proposal)

    def advance_to_verifier(self, run: dict) -> Path:
        run_path = Path(run["run_path"])
        accept_checkpoint_run_artifact(run_path, self.candidates(run_path), model="fixture-generator")
        accept_checkpoint_run_artifact(run_path, self.judgment(run_path), model="fixture-judge")
        accept_checkpoint_run_artifact(run_path, self.compression(run_path), model="fixture-compressor")
        return run_path

    def advance_to_ready(self, run: dict) -> Path:
        run_path = self.advance_to_verifier(run)
        manifest = accept_checkpoint_run_artifact(
            run_path,
            self.verifier(run_path),
            model="fixture-verifier",
        )
        self.assertEqual(manifest["status"], "ready-to-commit")
        return run_path

    def validate_schema(self, filename: str, value: dict) -> None:
        if Draft202012Validator is None:
            return
        schema = json.loads((ROOT / "schemas" / filename).read_text(encoding="utf-8"))
        Draft202012Validator(schema).validate(value)

    def begin_continuation_turn(
        self,
        *,
        mode: str = "solo",
        input_kind: str = "play-turn",
        root_name: str = "continuation-turns",
        director: bool = False,
    ) -> dict:
        # Checkpoint commit uses a separate connection, matching the CLI. Reopen
        # this fixture connection so the next request is frozen at the durable
        # checkpoint head rather than a cached transaction view.
        self.cube.close()
        self.cube = Cube.open(self.cube_path)
        return begin_turn_run(
            self.cube,
            reference=str(self.cube_path),
            resolved_cube_path=str(self.cube_path.resolve()),
            root=self.base / root_name,
            player_input="I step through the greenhouse door and listen.",
            input_kind=input_kind,
            audience_id="player",
            actor_id="narrator",
            director=director,
            world_id=None,
            allow_anchor=False,
            mode=mode,
            include_planner_context_on_commit=False,
        )

    def commit_public_turn(
        self,
        *,
        root_name: str,
        player_input: str,
        narration: str,
    ) -> Path:
        with Cube.open(self.cube_path) as cube:
            run = begin_turn_run(
                cube,
                reference=str(self.cube_path),
                resolved_cube_path=str(self.cube_path.resolve()),
                root=self.base / root_name,
                player_input=player_input,
                input_kind="play-turn",
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
            (run_path / TURN_ARTIFACT_FILES["proposal_draft"]).read_text(encoding="utf-8")
        )
        proposal["narration"] = narration
        accept_turn_run_artifact(run_path, proposal)
        commit_turn_run(run_path)
        self.cube.close()
        self.cube = Cube.open(self.cube_path)
        return run_path

    def test_begin_refuses_a_resolved_path_not_bound_to_the_open_cube(self) -> None:
        other_path = self.base / "other-cube"
        other = Cube.init(other_path, owner_id="other", owner_label="Other")
        try:
            with self.assertRaises(LacunaError) as caught:
                begin_checkpoint_run(
                    self.cube,
                    reference=str(self.cube_path),
                    resolved_cube_path=str(other_path),
                    root=self.run_root,
                    audience_id="player",
                    actor_id="narrator",
                    trigger="This path must not be rebound to another cube.",
                    candidate_count=2,
                    rollout_horizon_turns=2,
                    compression_max_chars=1000,
                    max_operations=4,
                )
            self.assertEqual(caught.exception.code, "checkpoint-run-cube-path-mismatch")
            self.assertFalse(self.run_root.exists())
        finally:
            other.close()

    def test_invalid_provider_routes_are_not_silently_defaulted(self) -> None:
        with self.assertRaises(LacunaError) as caught:
            normalize_checkpoint_provider_routes(generator_provider="")
        self.assertEqual(caught.exception.code, "unknown-checkpoint-provider")

        with self.assertRaises(LacunaError) as caught:
            self.begin(routes={})
        self.assertEqual(caught.exception.code, "bad-checkpoint-run")
        self.assertFalse(self.run_root.exists())

    def test_invalid_checkpoint_policy_does_not_leave_a_run_directory(self) -> None:
        with self.assertRaises(LacunaError) as caught:
            begin_checkpoint_run(
                self.cube,
                reference=str(self.cube_path),
                resolved_cube_path=str(self.cube_path),
                root=self.run_root,
                audience_id="player",
                actor_id="narrator",
                trigger="Reject this invalid source request before sidecar publication.",
                candidate_count=1,
                rollout_horizon_turns=3,
                compression_max_chars=1000,
                max_operations=4,
            )
        self.assertEqual(caught.exception.code, "bad-checkpoint-policy")
        self.assertFalse(self.run_root.exists())

    def test_failed_initial_checkpoint_publication_leaves_no_visible_or_staged_run(self) -> None:
        with patch(
            "lacuna.checkpoint_runs._write_manifest",
            side_effect=RuntimeError("synthetic publication failure"),
        ):
            with self.assertRaises(RuntimeError):
                self.begin()
        self.assertTrue(self.run_root.is_dir())
        self.assertEqual(list(self.run_root.iterdir()), [])

    def test_begin_fixes_heterogeneous_routes_and_embeds_exact_self_contained_dispatch(self) -> None:
        routes = {
            "lacuna-retcon-generator": "chatgpt",
            "lacuna-retcon-judge": "codex",
            "lacuna-retcon-compressor": "claude-code",
            "lacuna-retcon-verifier": "gemini-cli",
        }
        run = self.begin(routes=routes)
        run_path = Path(run["run_path"])
        self.assertEqual(run["status"], "awaiting-generator")
        self.assertEqual(run["provider_routes"], routes)
        self.assertEqual(stat.S_IMODE(run_path.stat().st_mode), 0o700)
        self.assertTrue((run_path / NEXT_FILE).is_file())
        self.assertEqual(
            {key for key, ref in run["artifacts"].items() if ref is not None},
            {"trigger", "request", "generator_card"},
        )

        card = self.read_json(run_path, "generator_card")
        dispatch = build_checkpoint_run_dispatch(run_path)
        self.assertEqual(dispatch["provider"], "chatgpt")
        self.assertEqual(dispatch["role"], "lacuna-retcon-generator")
        self.assertEqual(
            dispatch["agent_name"],
            provider_alias("lacuna-retcon-generator", "chatgpt"),
        )
        self.assertEqual(dispatch["input_card"], card)
        self.assertEqual(
            dispatch["input_card_sha256"],
            sha256_text(canonical_json(card)),
        )
        self.assertIn("already-sized output template", " ".join(dispatch["instructions"]))
        self.assertIn("checkpoint run accept", dispatch["return_contract"]["accept_command"])
        self.assertIn("record-failure", dispatch["invocation_contract"]["failure_command"])
        self.assertFalse(dispatch["authority"]["worker_may"] == [])
        self.validate_schema("checkpoint-run.v1.schema.json", run)
        self.validate_schema("checkpoint-run-agent-dispatch.v1.schema.json", dispatch)

    def test_failed_attempt_then_full_commit_records_ordered_invocation_custody(self) -> None:
        run = self.begin()
        run_path = Path(run["run_path"])
        failed = record_checkpoint_run_failure(
            run_path,
            failure_class="timeout",
            failure_message="The provider timed out before returning JSON.",
            model="fixture-generator",
            model_version="v0",
            invocation_id="call-failed",
            started_at="2026-06-24T20:00:00Z",
            completed_at="2026-06-24T20:00:01Z",
            duration_ms=1000,
        )
        self.assertEqual(failed["status"], "awaiting-generator")
        self.assertEqual(len(failed["invocations"]), 1)

        accept_checkpoint_run_artifact(
            run_path,
            self.candidates(run_path),
            model="fixture-generator",
            model_version="v1",
            invocation_id="call-accepted",
        )
        accept_checkpoint_run_artifact(run_path, self.judgment(run_path), model="fixture-judge")
        accept_checkpoint_run_artifact(run_path, self.compression(run_path), model="fixture-compressor")
        ready = accept_checkpoint_run_artifact(run_path, self.verifier(run_path), model="fixture-verifier")
        self.assertEqual(ready["status"], "ready-to-commit")
        self.assertEqual(len(ready["invocations"]), 5)

        receipts = [
            json.loads((run_path / ref["path"]).read_text(encoding="utf-8"))
            for ref in ready["invocations"]
        ]
        self.assertEqual([item["sequence"] for item in receipts], [1, 2, 3, 4, 5])
        self.assertEqual([item["attempt"] for item in receipts[:2]], [1, 2])
        self.assertEqual(receipts[0]["outcome"], "failed")
        self.assertEqual(receipts[0]["failure_class"], "timeout")
        self.assertEqual(receipts[1]["outcome"], "accepted")
        self.assertEqual(receipts[1]["output_artifact"]["path"], ARTIFACT_FILES["candidates"])
        for receipt in receipts:
            self.validate_schema("checkpoint-invocation-receipt.v1.schema.json", receipt)

        before = self.cube.event_count()
        committed = commit_checkpoint_run(run_path)
        after = self.cube.event_count()
        self.assertEqual(committed["overall_status"], "accepted")
        self.assertEqual(committed["turn_receipt"]["delivery"]["mode"], "direct")
        self.assertEqual(after - before, 2)
        audited = audit_checkpoint_run(run_path)
        self.assertEqual(audited["status"], "committed")
        self.assertEqual(commit_checkpoint_run(run_path), committed)
        self.validate_schema("checkpoint-run.v1.schema.json", audited)

    def test_fresh_narrator_capsule_requires_commit_and_excludes_rejected_future_artifacts(self) -> None:
        run = self.begin()
        run_path = self.advance_to_ready(run)
        with self.assertRaises(LacunaError) as caught:
            build_checkpoint_run_narrator_capsule(run_path)
        self.assertEqual(caught.exception.code, "checkpoint-run-not-committed")

        committed = commit_checkpoint_run(run_path)
        committed_manifest = audit_checkpoint_run(run_path)
        self.assertEqual(
            committed_manifest["next_action"]["expected_schema"],
            "lacuna.checkpoint-continuation-dispatch.v2",
        )
        self.assertIn("checkpoint run next-turn", committed_manifest["next_action"]["command"])
        self.assertIn("lacuna history complete", committed_manifest["next_action"]["action"])
        self.assertIn("lacuna history build", committed_manifest["next_action"]["action"])
        self.assertIn("--public-history", committed_manifest["next_action"]["action"])
        capsule = build_checkpoint_run_narrator_capsule(run_path)
        self.assertEqual(
            capsule,
            validate_checkpoint_narrator_capsule(capsule),
        )
        self.validate_schema("checkpoint-narrator-capsule.v1.schema.json", capsule)
        self.assertEqual(capsule["checkpoint_id"], committed["checkpoint_id"])
        self.assertEqual(capsule["post_commit_head"], committed["turn_receipt"]["head"])
        self.assertEqual(
            capsule["private_planning_context"]["state_card"],
            self.compression(run_path)["state_card"],
        )
        self.assertRegex(checkpoint_narrator_capsule_sha256(capsule), r"^[0-9a-f]{64}$")
        serialized = canonical_json(capsule)
        self.assertNotIn("Storm interlock", serialized)
        self.assertNotIn("weighted_score", serialized)
        self.assertNotIn("fixture-verifier", serialized)

        tampered_card = copy.deepcopy(capsule)
        tampered_card["private_planning_context"]["state_card"] += " tampered"
        with self.assertRaises(LacunaError) as caught:
            validate_checkpoint_narrator_capsule(tampered_card)
        self.assertEqual(caught.exception.code, "bad-checkpoint-narrator-capsule")

        tampered_context = copy.deepcopy(capsule)
        tampered_context["audience_context"]["tampered"] = True
        with self.assertRaises(LacunaError) as caught:
            validate_checkpoint_narrator_capsule(tampered_context)
        self.assertEqual(caught.exception.code, "bad-checkpoint-narrator-capsule")

    def test_committed_checkpoint_binds_a_fresh_turn_into_one_exact_dispatch(self) -> None:
        checkpoint = self.begin()
        checkpoint_path = self.advance_to_ready(checkpoint)
        receipt = commit_checkpoint_run(checkpoint_path)
        turn = self.begin_continuation_turn()

        dispatch = build_checkpoint_continuation_dispatch(
            checkpoint_path,
            turn["run_path"],
            provider="chatgpt",
        )
        self.assertEqual(
            dispatch,
            validate_checkpoint_continuation_dispatch(dispatch),
        )
        self.validate_schema("checkpoint-continuation-dispatch.v2.schema.json", dispatch)
        self.assertEqual(dispatch["role"], "lacuna-fresh-narrator")
        self.assertEqual(dispatch["agent_name"], "fresh post-checkpoint narrator context")
        self.assertEqual(dispatch["checkpoint_id"], receipt["checkpoint_id"])
        self.assertEqual(dispatch["turn_run_id"], turn["run_id"])
        self.assertEqual(dispatch["public_context_mode"], "typed-only")
        self.assertIsNone(dispatch["public_history_sha256"])
        self.assertIsNone(dispatch["public_history_completeness"])
        self.assertIsNone(dispatch["input_document"]["public_history"])
        self.assertRegex(checkpoint_continuation_dispatch_sha256(dispatch), r"^[0-9a-f]{64}$")
        packet = json.loads(
            (Path(turn["run_path"]) / TURN_ARTIFACT_FILES["packet"]).read_text(encoding="utf-8")
        )
        self.assertEqual(dispatch["input_document"]["next_player_input"], packet["player_input"])
        self.assertEqual(dispatch["input_document"]["audience_context"], packet["audience_context"])
        self.assertEqual(
            dispatch["input_document"]["audience_context"]["head"],
            turn["turn_identity"]["expected_head"],
        )
        self.assertEqual(
            dispatch["return_contract"]["template"]["expected_head"],
            turn["turn_identity"]["expected_head"],
        )
        self.assertEqual(
            dispatch["input_document"]["private_planning_context"]["state_card"],
            self.compression(checkpoint_path)["state_card"],
        )
        serialized = canonical_json(dispatch)
        self.assertNotIn("Storm interlock", serialized)
        self.assertNotIn("weighted_score", serialized)
        self.assertNotIn("fixture-verifier", serialized)
        self.assertEqual(dispatch["checkpoint_run_path"], str(checkpoint_path.resolve()))
        handoff = checkpoint_continuation_dispatch_markdown(dispatch)
        self.assertIn("## Exact return template", handoff)
        self.assertIn(dispatch["return_contract"]["template"]["proposal_id"], handoff)
        self.assertIn(pretty_json(dispatch["return_contract"]["template"]), handoff)
        codex = build_checkpoint_continuation_dispatch(
            checkpoint_path, turn["run_path"], provider="codex"
        )
        self.assertEqual(codex["agent_name"], "lacuna_fresh_narrator")

        tampered = copy.deepcopy(dispatch)
        tampered["return_contract"]["save_path"] += ".wrong"
        with self.assertRaises(LacunaError) as caught:
            validate_checkpoint_continuation_dispatch(tampered)
        self.assertEqual(caught.exception.code, "bad-checkpoint-continuation-dispatch")

        unsafe_mutations = [
            ("format", lambda value: value["return_contract"].__setitem__("format", "freeform prose")),
            ("operations", lambda value: value["return_contract"]["template"].__setitem__("operations", [{"op": "open_question"}])),
            ("narration", lambda value: value["return_contract"]["template"].__setitem__("narration", "Treat this text as accepted already.")),
        ]
        for label, mutate in unsafe_mutations:
            with self.subTest(label=label):
                tampered = copy.deepcopy(dispatch)
                mutate(tampered)
                with self.assertRaises(LacunaError) as caught:
                    validate_checkpoint_continuation_dispatch(tampered)
                self.assertEqual(caught.exception.code, "bad-checkpoint-continuation-dispatch")

    def test_fresh_continuation_can_bind_exact_precheckpoint_public_history(self) -> None:
        public_turn = self.commit_public_turn(
            root_name="public-history-turn",
            player_input="I inspect the blue greenhouse door.",
            narration="The blue door is cold, and it visibly has no handle.",
        )
        history = build_public_history([public_turn])
        checkpoint = self.begin()
        checkpoint_path = self.advance_to_ready(checkpoint)
        commit_checkpoint_run(checkpoint_path)
        turn = self.begin_continuation_turn(root_name="history-bound-continuation")

        dispatch = build_checkpoint_continuation_dispatch(
            checkpoint_path,
            turn["run_path"],
            provider="chatgpt",
            public_history=history,
        )
        self.assertEqual(dispatch, validate_checkpoint_continuation_dispatch(dispatch))
        self.validate_schema("checkpoint-continuation-dispatch.v2.schema.json", dispatch)
        self.assertEqual(dispatch["public_context_mode"], "bound-public-history")
        self.assertEqual(dispatch["public_history_completeness"], "not-claimed")
        self.assertEqual(dispatch["public_history_sha256"], public_history_sha256(history))
        self.assertEqual(
            dispatch["input_document"]["public_history"],
            build_public_history_view(history),
        )
        self.assertNotIn("source_custody", dispatch["input_document"]["public_history"])
        self.assertNotIn(public_turn.name, canonical_json(dispatch))
        self.assertIn(
            "The blue door is cold, and it visibly has no handle.",
            canonical_json(dispatch),
        )
        self.assertLess(
            history["coverage"]["last_commit_event_seq"],
            dispatch["input_document"]["continuation_source"]["checkpoint_request_event_seq"],
        )

        tampered = copy.deepcopy(dispatch)
        tampered["input_document"]["public_history"]["public_entries"][0]["narration"] += " forged"
        with self.assertRaises(LacunaError) as caught:
            validate_checkpoint_continuation_dispatch(tampered)
        self.assertEqual(caught.exception.code, "bad-public-history-view")

    def test_complete_public_history_census_binds_the_checkpoint_and_fresh_dispatch(self) -> None:
        public_turn = self.commit_public_turn(
            root_name="complete-history-turns",
            player_input="I count the three panes above the greenhouse door.",
            narration="Three narrow panes catch the rain above the handleless blue door.",
        )
        checkpoint = self.begin()
        checkpoint_path = self.advance_to_ready(checkpoint)
        receipt = commit_checkpoint_run(checkpoint_path)

        proc = subprocess.run(
            [
                str(ROOT / "lacuna"),
                "history",
                "complete",
                str(checkpoint_path),
                "--run-root",
                str(public_turn.parent),
                "--format",
                "json",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        history = json.loads(proc.stdout)
        self.validate_schema("public-history.v2.schema.json", history)
        self.assertEqual(history["coverage"]["mode"], "complete-before-checkpoint")
        self.assertEqual(history["coverage"]["completeness"], "complete")
        self.assertEqual(history["coverage"]["expected_committed_turn_count"], 1)
        self.assertEqual(history["coverage"]["boundary"]["checkpoint_run_id"], checkpoint["run_id"])
        self.assertEqual(history["coverage"]["boundary"]["checkpoint_id"], receipt["checkpoint_id"])

        turn = self.begin_continuation_turn(root_name="complete-history-continuation")
        dispatch = build_checkpoint_continuation_dispatch(
            checkpoint_path,
            turn["run_path"],
            provider="chatgpt",
            public_history=history,
        )
        self.assertEqual(dispatch, validate_checkpoint_continuation_dispatch(dispatch))
        self.validate_schema("checkpoint-continuation-dispatch.v2.schema.json", dispatch)
        self.assertEqual(dispatch["public_context_mode"], "complete-bound-public-history")
        self.assertEqual(dispatch["public_history_completeness"], "complete")
        self.assertEqual(
            dispatch["input_document"]["public_history"]["coverage_mode"],
            "complete-before-checkpoint",
        )
        self.assertEqual(
            dispatch["input_document"]["continuation_source"][
                "public_history_expected_committed_turn_count"
            ],
            1,
        )

    def test_complete_history_bound_to_another_checkpoint_refuses(self) -> None:
        public_turn = self.commit_public_turn(
            root_name="boundary-history-turns",
            player_input="I trace the crack in the silver bell.",
            narration="The crack forks twice before vanishing beneath the bell's rim.",
        )
        first = self.begin()
        first_path = self.advance_to_ready(first)
        commit_checkpoint_run(first_path)
        proc = subprocess.run(
            [
                str(ROOT / "lacuna"),
                "history",
                "complete",
                str(first_path),
                "--run-root",
                str(public_turn.parent),
                "--format",
                "json",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        history = json.loads(proc.stdout)

        second = self.begin()
        second_path = self.advance_to_ready(second)
        commit_checkpoint_run(second_path)
        turn = self.begin_continuation_turn(root_name="wrong-boundary-continuation")
        with self.assertRaises(LacunaError) as caught:
            build_checkpoint_continuation_dispatch(
                second_path,
                turn["run_path"],
                public_history=history,
            )
        self.assertEqual(
            caught.exception.code,
            "checkpoint-continuation-public-history-boundary-mismatch",
        )

    def test_zero_turn_complete_history_binds_without_a_dummy_run_root(self) -> None:
        checkpoint = self.begin()
        checkpoint_path = self.advance_to_ready(checkpoint)
        commit_checkpoint_run(checkpoint_path)
        proc = subprocess.run(
            [
                str(ROOT / "lacuna"),
                "history",
                "complete",
                str(checkpoint_path),
                "--format",
                "json",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        history = json.loads(proc.stdout)
        self.assertEqual(history["coverage"]["entry_count"], 0)
        self.assertIsNone(history["coverage"]["last_commit_event_seq"])
        turn = self.begin_continuation_turn(root_name="zero-history-continuation")
        dispatch = build_checkpoint_continuation_dispatch(
            checkpoint_path,
            turn["run_path"],
            public_history=history,
        )
        self.assertEqual(dispatch["public_context_mode"], "complete-bound-public-history")
        self.assertEqual(dispatch["input_document"]["public_history"]["entry_count"], 0)
        self.assertIsNone(
            dispatch["input_document"]["continuation_source"][
                "public_history_last_commit_event_seq"
            ]
        )
        self.assertEqual(dispatch, validate_checkpoint_continuation_dispatch(dispatch))

    def test_one_command_next_turn_opens_the_narrow_turn_and_emits_the_same_dispatch(self) -> None:
        public_turn = self.commit_public_turn(
            root_name="next-turn-public-history",
            player_input="I note the silver bell beside the door.",
            narration="The silver bell is cracked but still within reach.",
        )
        history = build_public_history([public_turn])
        checkpoint = self.begin()
        checkpoint_path = self.advance_to_ready(checkpoint)
        commit_checkpoint_run(checkpoint_path)

        invalid_history = copy.deepcopy(history)
        invalid_history["public_entries"][0]["narration"] += " forged"
        invalid_root = self.base / "invalid-one-command-continuation"
        with self.assertRaises(LacunaError) as caught:
            begin_checkpoint_continuation_turn(
                checkpoint_path,
                player_input="This must not open a run.",
                root=invalid_root,
                public_history=invalid_history,
            )
        self.assertEqual(caught.exception.code, "bad-public-history")
        self.assertFalse(invalid_root.exists())

        input_file = self.base / "next-player-input.txt"
        input_file.write_text("I ring the cracked bell once.", encoding="utf-8")
        history_file = self.base / "public-history.json"
        history_file.write_text(json.dumps(history), encoding="utf-8")
        proc = subprocess.run(
            [
                str(ROOT / "lacuna"),
                "checkpoint",
                "run",
                "next-turn",
                str(checkpoint_path),
                "--root",
                str(self.base / "one-command-continuation"),
                "--player-input-file",
                str(input_file),
                "--provider",
                "chatgpt",
                "--public-history",
                str(history_file),
                "--format",
                "json",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        dispatch = json.loads(proc.stdout)
        self.assertEqual(dispatch, validate_checkpoint_continuation_dispatch(dispatch))
        self.assertEqual(dispatch["input_document"]["next_player_input"], "I ring the cracked bell once.")
        self.assertEqual(dispatch["public_context_mode"], "bound-public-history")
        self.assertEqual(dispatch["public_history_completeness"], "not-claimed")
        self.assertTrue(Path(dispatch["turn_run_path"]).is_dir())

        with self.assertRaises(LacunaError) as caught:
            begin_checkpoint_continuation_turn(
                checkpoint_path,
                player_input="Try to open a second request from the same old checkpoint.",
                root=self.base / "second-one-command-continuation",
            )
        self.assertEqual(caught.exception.code, "checkpoint-continuation-checkpoint-not-current")

    def test_fresh_continuation_return_commits_through_the_ordinary_turn_boundary(self) -> None:
        checkpoint = self.begin()
        checkpoint_path = self.advance_to_ready(checkpoint)
        commit_checkpoint_run(checkpoint_path)
        dispatch = begin_checkpoint_continuation_turn(
            checkpoint_path,
            root=self.base / "committing-continuation-turns",
            player_input="I step through the greenhouse door and listen.",
            provider="portable",
        )
        proposal = copy.deepcopy(dispatch["return_contract"]["template"])
        proposal["narration"] = "Beyond the greenhouse door, a slow drip answers your footsteps."
        ready = accept_turn_run_artifact(dispatch["turn_run_path"], proposal)
        self.assertEqual(ready["status"], "ready-to-commit")
        turn_receipt = commit_turn_run(dispatch["turn_run_path"])
        self.assertEqual(turn_receipt["overall_status"], "pass")
        self.assertEqual(turn_receipt["narration"], proposal["narration"])
        self.assertEqual(self.cube.verify()["overall_status"], "pass")

    def test_continuation_requires_a_committed_checkpoint(self) -> None:
        checkpoint = self.begin()
        checkpoint_path = self.advance_to_ready(checkpoint)
        turn = self.begin_continuation_turn()
        with self.assertRaises(LacunaError) as caught:
            build_checkpoint_continuation_dispatch(checkpoint_path, turn["run_path"])
        self.assertEqual(caught.exception.code, "checkpoint-continuation-not-committed")

    def test_continuation_requires_a_fresh_solo_turn(self) -> None:
        checkpoint = self.begin()
        checkpoint_path = self.advance_to_ready(checkpoint)
        commit_checkpoint_run(checkpoint_path)
        pair = self.begin_continuation_turn(mode="pair", root_name="pair-turns")
        with self.assertRaises(LacunaError) as caught:
            build_checkpoint_continuation_dispatch(checkpoint_path, pair["run_path"])
        self.assertEqual(caught.exception.code, "checkpoint-continuation-turn-not-solo")

    def test_continuation_refuses_a_director_turn(self) -> None:
        checkpoint = self.begin()
        checkpoint_path = self.advance_to_ready(checkpoint)
        commit_checkpoint_run(checkpoint_path)
        director = self.begin_continuation_turn(director=True, root_name="director-turns")
        with self.assertRaises(LacunaError) as caught:
            build_checkpoint_continuation_dispatch(checkpoint_path, director["run_path"])
        self.assertEqual(caught.exception.code, "checkpoint-continuation-turn-authority-too-wide")

    def test_continuation_requires_play_turn_input(self) -> None:
        checkpoint = self.begin()
        checkpoint_path = self.advance_to_ready(checkpoint)
        commit_checkpoint_run(checkpoint_path)
        session = self.begin_continuation_turn(
            input_kind="session-control", root_name="session-control-turns"
        )
        with self.assertRaises(LacunaError) as caught:
            build_checkpoint_continuation_dispatch(checkpoint_path, session["run_path"])
        self.assertEqual(caught.exception.code, "checkpoint-continuation-not-play-turn")

    def test_continuation_refuses_stale_or_different_cube_turn(self) -> None:
        checkpoint = self.begin()
        checkpoint_path = self.advance_to_ready(checkpoint)
        commit_checkpoint_run(checkpoint_path)
        turn = self.begin_continuation_turn()
        self.cube.apply_operations(
            actor_id="user",
            operations=[
                {
                    "op": "open_question",
                    "question_id": "qst.intervening",
                    "text": "Did another event intervene?",
                    "opened_by": "user",
                    "visibility": "private",
                    "audience": [],
                }
            ],
            message="advance after opening the continuation turn",
        )
        with self.assertRaises(LacunaError) as caught:
            build_checkpoint_continuation_dispatch(checkpoint_path, turn["run_path"])
        self.assertEqual(caught.exception.code, "checkpoint-continuation-stale-head")

        other_path = self.base / "other-cube"
        other = Cube.init(other_path, owner_id="user", owner_label="User")
        try:
            other.apply_operations(
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
            )
            other_turn = begin_turn_run(
                other,
                reference=str(other_path),
                resolved_cube_path=str(other_path.resolve()),
                root=self.base / "other-turns",
                player_input="I continue.",
                input_kind="play-turn",
                audience_id="player",
                actor_id="narrator",
                director=False,
                world_id=None,
                allow_anchor=False,
                mode="solo",
                include_planner_context_on_commit=False,
            )
        finally:
            other.close()
        with self.assertRaises(LacunaError) as caught:
            build_checkpoint_continuation_dispatch(checkpoint_path, other_turn["run_path"])
        self.assertEqual(caught.exception.code, "checkpoint-continuation-cube-mismatch")

    def test_verifier_refusal_is_terminal_and_never_creates_review_or_receipt(self) -> None:
        run = self.begin()
        run_path = self.advance_to_verifier(run)
        before = self.cube.event_count()
        refused = accept_checkpoint_run_artifact(
            run_path,
            self.verifier(run_path, passing=False),
            model="fixture-verifier",
        )
        self.assertEqual(refused["status"], "verifier-refused")
        self.assertIsNone(refused["artifacts"]["review"])
        self.assertIsNone(refused["artifacts"]["receipt"])
        self.assertEqual(self.cube.event_count(), before)
        with self.assertRaises(LacunaError) as caught:
            commit_checkpoint_run(run_path)
        self.assertEqual(caught.exception.code, "checkpoint-run-not-ready")
        with self.assertRaises(LacunaError) as caught:
            build_checkpoint_run_dispatch(run_path)
        self.assertEqual(caught.exception.code, "checkpoint-run-not-delegated-stage")

    def test_cross_run_and_wrong_stage_outputs_fail_before_sidecar_mutation(self) -> None:
        first = self.begin()
        second = self.begin()
        first_path = Path(first["run_path"])
        second_path = Path(second["run_path"])
        cross_bound = self.candidates(first_path)
        before = {
            path.name: path.read_bytes()
            for path in second_path.iterdir()
            if path.name != ".run.lock"
        }
        with self.assertRaises(LacunaError):
            accept_checkpoint_run_artifact(second_path, cross_bound, model="fixture")
        after = {
            path.name: path.read_bytes()
            for path in second_path.iterdir()
            if path.name != ".run.lock"
        }
        self.assertEqual(after, before)

        valid = self.candidates(second_path)
        accept_checkpoint_run_artifact(second_path, valid, model="fixture")
        manifest_before = (second_path / RUN_MANIFEST_FILE).read_bytes()
        with self.assertRaises(LacunaError):
            accept_checkpoint_run_artifact(second_path, valid, model="fixture")
        self.assertEqual((second_path / RUN_MANIFEST_FILE).read_bytes(), manifest_before)

    def test_recover_rewrites_only_next_pointer_after_authoritative_audit(self) -> None:
        run = self.begin()
        run_path = Path(run["run_path"])
        authoritative_before = {
            path.name: path.read_bytes()
            for path in run_path.iterdir()
            if path.name not in {NEXT_FILE, ".run.lock"}
        }
        (run_path / NEXT_FILE).unlink()
        recovered = recover_checkpoint_run(run_path)
        self.assertEqual(recovered, audit_checkpoint_run(run_path))
        authoritative_after = {
            path.name: path.read_bytes()
            for path in run_path.iterdir()
            if path.name not in {NEXT_FILE, ".run.lock"}
        }
        self.assertEqual(authoritative_after, authoritative_before)
        self.assertIn(run["run_id"], (run_path / NEXT_FILE).read_text(encoding="utf-8"))

    def test_semantically_rehashed_invocation_relabeling_is_refused(self) -> None:
        run = self.begin()
        run_path = Path(run["run_path"])
        manifest = accept_checkpoint_run_artifact(
            run_path,
            self.candidates(run_path),
            model="fixture-generator",
        )
        invocation_ref = manifest["invocations"][0]
        invocation_path = run_path / invocation_ref["path"]
        invocation = json.loads(invocation_path.read_text(encoding="utf-8"))
        invocation["provider"] = "codex"
        atomic_write_json(invocation_path, invocation)
        manifest["invocations"][0]["sha256"] = sha256_text(canonical_json(invocation))
        atomic_write_json(run_path / RUN_MANIFEST_FILE, manifest)

        with self.assertRaises(LacunaError) as caught:
            audit_checkpoint_run(run_path)
        self.assertEqual(caught.exception.code, "bad-checkpoint-invocation-receipt")

    def test_missing_accepted_invocation_receipt_breaks_output_custody(self) -> None:
        run = self.begin()
        run_path = Path(run["run_path"])
        manifest = accept_checkpoint_run_artifact(
            run_path,
            self.candidates(run_path),
            model="fixture-generator",
        )
        manifest["invocations"] = []
        atomic_write_json(run_path / RUN_MANIFEST_FILE, manifest)
        with self.assertRaises(LacunaError) as caught:
            audit_checkpoint_run(run_path)
        self.assertEqual(caught.exception.code, "checkpoint-run-invocation-custody-mismatch")

    def test_fixed_trust_boundary_nonclaims_cannot_be_silently_rewritten(self) -> None:
        run = self.begin()
        run_path = Path(run["run_path"])
        manifest = json.loads((run_path / RUN_MANIFEST_FILE).read_text(encoding="utf-8"))
        manifest["nonclaims"][0] = "This sidecar proves provider identity."
        atomic_write_json(run_path / RUN_MANIFEST_FILE, manifest)
        with self.assertRaises(LacunaError) as caught:
            audit_checkpoint_run(run_path)
        self.assertEqual(caught.exception.code, "bad-checkpoint-run")

    def test_malformed_invocation_collection_is_a_typed_refusal(self) -> None:
        run = self.begin()
        run_path = Path(run["run_path"])
        original_manifest = json.loads((run_path / RUN_MANIFEST_FILE).read_text(encoding="utf-8"))
        malformed = copy.deepcopy(original_manifest)
        malformed["invocations"] = {"not": "a list"}
        atomic_write_json(run_path / RUN_MANIFEST_FILE, malformed)
        with self.assertRaises(LacunaError) as caught:
            audit_checkpoint_run(run_path)
        self.assertEqual(caught.exception.code, "bad-checkpoint-run")

        # Capacity must refuse before writing a 1001st receipt or corrupting run.json.
        atomic_write_json(run_path / RUN_MANIFEST_FILE, original_manifest)
        full_manifest = copy.deepcopy(original_manifest)
        full_manifest["invocations"] = [{"role": "lacuna-retcon-generator"}] * 1000
        before = {
            path.name: path.read_bytes()
            for path in run_path.iterdir()
            if path.name != ".run.lock"
        }
        with patch(
            "lacuna.checkpoint_runs._audit_checkpoint_run_unlocked",
            return_value=full_manifest,
        ), self.assertRaises(LacunaError) as caught:
            record_checkpoint_run_failure(
                run_path,
                failure_class="timeout",
                model="fixture-generator",
            )
        self.assertEqual(caught.exception.code, "checkpoint-run-invocation-limit")
        after = {
            path.name: path.read_bytes()
            for path in run_path.iterdir()
            if path.name != ".run.lock"
        }
        self.assertEqual(after, before)

    @unittest.skipIf(os.name == "nt", "POSIX symlink semantics")
    def test_authoritative_artifact_symlink_substitution_is_refused(self) -> None:
        run = self.begin()
        run_path = Path(run["run_path"])
        card_path = run_path / ARTIFACT_FILES["generator_card"]
        target = self.base / "generator-card-target.json"
        target.write_bytes(card_path.read_bytes())
        card_path.unlink()
        card_path.symlink_to(target)
        with self.assertRaises(LacunaError) as caught:
            audit_checkpoint_run(run_path)
        self.assertEqual(caught.exception.code, "checkpoint-run-member-unsafe")

    def test_commit_after_db_success_and_later_head_recovers_without_duplicate_events(self) -> None:
        run = self.begin()
        run_path = self.advance_to_ready(run)
        request = self.read_json(run_path, "request")
        candidates = self.read_json(run_path, "candidates")
        judgment = self.read_json(run_path, "judgment")
        proposal = self.read_json(run_path, "proposal")
        verifier = self.read_json(run_path, "verifier_return")
        review = self.read_json(run_path, "review")

        direct = commit_checkpoint(
            self.cube,
            request,
            candidates,
            judgment,
            proposal,
            verifier,
            review,
        )
        self.assertEqual(direct["turn_receipt"]["delivery"]["mode"], "direct")
        self.cube.apply_operations(
            actor_id="user",
            operations=[
                {
                    "op": "open_question",
                    "question_id": "qst_after_checkpoint",
                    "text": "What changed after the checkpoint commit?",
                    "opened_by": "user",
                    "visibility": "private",
                    "audience": [],
                }
            ],
            message="advance the head after the exact checkpoint change",
        )
        after_later_write = self.cube.event_count()

        recovered = commit_checkpoint_run(run_path)
        self.assertEqual(self.cube.event_count(), after_later_write)
        self.assertEqual(recovered["turn_receipt"]["delivery"]["mode"], "recovered")
        self.assertTrue(recovered["turn_receipt"]["delivery"]["historical_snapshot_used"])
        self.assertEqual(audit_checkpoint_run(run_path)["status"], "committed")

    def test_rehashed_committed_receipt_tampering_fails_full_chain_validation(self) -> None:
        run = self.begin()
        run_path = self.advance_to_ready(run)
        commit_checkpoint_run(run_path)
        manifest = json.loads((run_path / RUN_MANIFEST_FILE).read_text(encoding="utf-8"))
        receipt_path = run_path / ARTIFACT_FILES["receipt"]
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        receipt["narration"] += " Forged suffix."
        atomic_write_json(receipt_path, receipt)
        manifest["artifacts"]["receipt"]["sha256"] = sha256_text(canonical_json(receipt))
        atomic_write_json(run_path / RUN_MANIFEST_FILE, manifest)

        with self.assertRaises(LacunaError) as caught:
            audit_checkpoint_run(run_path)
        self.assertEqual(caught.exception.code, "bad-checkpoint-commit-receipt")


if __name__ == "__main__":
    unittest.main()
