from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from unittest import mock
from pathlib import Path

from tests._schema_support import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from lacuna.campaigns import CampaignLibrary
from lacuna.entrance import describe_model_reference
from lacuna.errors import LacunaError
from lacuna.store import Cube
from lacuna.turnruns import (
    ARTIFACT_FILES,
    NEXT_FILE,
    RUN_MANIFEST_FILE,
    audit_turn_run,
    begin_turn_run,
    build_turn_run_dispatch,
    recover_turn_run,
    turn_run_dispatch_markdown,
)
from lacuna.util import atomic_write_json, canonical_json, sha256_text


class TurnRunHandoffAndIntegrityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.library_path = self.root / "library"
        self.run_root = self.root / "runs"
        library = CampaignLibrary.ensure(self.library_path)
        library.create_campaign(
            slug="glass-house",
            title="Glass House",
            summary="Exercise exact delegated handoffs and sidecar integrity.",
        )
        self.target = describe_model_reference(self.library_path)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def begin(self, *, mode: str = "pair", input_kind: str = "session-control") -> dict:
        with Cube.open(self.target["resolved_cube_path"]) as cube:
            return begin_turn_run(
                cube,
                reference=self.target["reference"],
                resolved_cube_path=self.target["resolved_cube_path"],
                root=self.run_root,
                player_input="Will you DM?",
                input_kind=input_kind,
                audience_id="player",
                actor_id="narrator",
                director=True,
                world_id=None,
                allow_anchor=False,
                mode=mode,
                include_planner_context_on_commit=False,
            )

    def test_dispatch_embeds_exact_card_and_provider_route(self) -> None:
        run = self.begin()
        run_path = Path(run["run_path"])
        card = json.loads(
            (run_path / ARTIFACT_FILES["planner_card"]).read_text(encoding="utf-8")
        )

        dispatch = build_turn_run_dispatch(run_path, provider="chatgpt")
        self.assertEqual(dispatch["schema"], "lacuna.agent-dispatch.v1")
        self.assertEqual(dispatch["provider"], "chatgpt")
        self.assertEqual(dispatch["role"], "lacuna-planner")
        self.assertEqual(dispatch["agent_name"], "role-dedicated planner context")
        self.assertEqual(dispatch["input_kind"], "session-control")
        self.assertEqual(dispatch["input_document"], card)
        self.assertEqual(
            dispatch["input_artifact"]["sha256"],
            sha256_text(canonical_json(card)),
        )
        self.assertEqual(
            dispatch["return_contract"]["schema"],
            card["output_contract"]["schema"],
        )
        self.assertIn("turn run accept", dispatch["return_contract"]["accept_command"])
        self.assertIn("commit a turn or mutate the cube", dispatch["authority"]["worker_may_not"])

        markdown = turn_run_dispatch_markdown(dispatch)
        self.assertIn("perform the named role", markdown)
        self.assertIn("## Complete task card", markdown)
        self.assertIn(card["task_id"], markdown)
        self.assertIn(card["objective"], markdown)
        self.assertIn("does not need local file access", markdown)
        self.assertIn("Parent coordinator only", markdown)

        if Draft202012Validator is not None:
            schema = json.loads(
                (ROOT / "schemas" / "agent-dispatch.v1.schema.json").read_text(
                    encoding="utf-8"
                )
            )
            Draft202012Validator(schema).validate(dispatch)

    def test_dispatch_refuses_parent_owned_stage_and_unknown_provider(self) -> None:
        run = self.begin(mode="solo")
        with self.assertRaises(LacunaError) as caught:
            build_turn_run_dispatch(run["run_path"])
        self.assertEqual(caught.exception.code, "turn-run-not-delegated-stage")

        with self.assertRaises(LacunaError) as caught:
            build_turn_run_dispatch(run["run_path"], provider="mystery-model")
        self.assertEqual(caught.exception.code, "unknown-turn-run-provider")

    def test_recover_rewrites_only_the_deterministic_pointer(self) -> None:
        run = self.begin()
        run_path = Path(run["run_path"])
        manifest_path = run_path / RUN_MANIFEST_FILE
        next_path = run_path / NEXT_FILE
        authoritative_before = {
            path.name: path.read_bytes()
            for path in run_path.iterdir()
            if path.name not in {NEXT_FILE, ".run.lock"}
        }
        manifest_before = manifest_path.read_bytes()
        next_path.unlink()

        recovered = recover_turn_run(run_path)
        self.assertEqual(recovered, audit_turn_run(run_path))
        self.assertEqual(manifest_path.read_bytes(), manifest_before)
        authoritative_after = {
            path.name: path.read_bytes()
            for path in run_path.iterdir()
            if path.name not in {NEXT_FILE, ".run.lock"}
        }
        self.assertEqual(authoritative_after, authoritative_before)
        self.assertIn(run["run_id"], next_path.read_text(encoding="utf-8"))

    def test_recover_refuses_when_an_authoritative_member_is_tampered(self) -> None:
        run = self.begin()
        run_path = Path(run["run_path"])
        next_path = run_path / NEXT_FILE
        next_path.unlink()
        packet_path = run_path / ARTIFACT_FILES["packet"]
        packet = json.loads(packet_path.read_text(encoding="utf-8"))
        packet["player_input"] += " altered"
        atomic_write_json(packet_path, packet)

        with self.assertRaises(LacunaError) as caught:
            recover_turn_run(run_path)
        self.assertEqual(caught.exception.code, "turn-run-artifact-digest-mismatch")
        self.assertFalse(next_path.exists())

    @unittest.skipIf(os.name == "nt", "POSIX symlink semantics")
    def test_manifest_and_artifact_symlink_substitution_are_refused(self) -> None:
        artifact_run = self.begin()
        artifact_path = Path(artifact_run["run_path"])
        packet_path = artifact_path / ARTIFACT_FILES["packet"]
        packet_target = self.root / "packet-target.json"
        packet_target.write_bytes(packet_path.read_bytes())
        packet_path.unlink()
        packet_path.symlink_to(packet_target)
        with self.assertRaises(LacunaError) as caught:
            audit_turn_run(artifact_path)
        self.assertEqual(caught.exception.code, "turn-run-member-unsafe")

        manifest_run = self.begin()
        manifest_path = Path(manifest_run["run_path"])
        run_json = manifest_path / RUN_MANIFEST_FILE
        manifest_target = self.root / "manifest-target.json"
        manifest_target.write_bytes(run_json.read_bytes())
        run_json.unlink()
        run_json.symlink_to(manifest_target)
        with self.assertRaises(LacunaError) as caught:
            audit_turn_run(manifest_path)
        self.assertEqual(caught.exception.code, "turn-run-member-unsafe")

    @unittest.skipIf(os.name == "nt", "POSIX hard-link semantics")
    def test_hardlinked_artifact_is_refused_even_when_bytes_and_digest_match(self) -> None:
        run = self.begin()
        run_path = Path(run["run_path"])
        packet_path = run_path / ARTIFACT_FILES["packet"]
        external = self.root / "hardlinked-packet.json"
        packet_path.rename(external)
        os.link(external, packet_path)
        self.assertEqual(packet_path.read_bytes(), external.read_bytes())
        self.assertGreater(packet_path.stat().st_nlink, 1)

        with self.assertRaises(LacunaError) as caught:
            audit_turn_run(run_path)
        self.assertEqual(caught.exception.code, "turn-run-member-unsafe")

    def test_oversized_authoritative_member_is_refused_before_parsing(self) -> None:
        run = self.begin()
        run_path = Path(run["run_path"])
        packet_path = run_path / ARTIFACT_FILES["packet"]
        with packet_path.open("wb") as handle:
            handle.truncate(16 * 1024 * 1024 + 1)

        with self.assertRaises(LacunaError) as caught:
            audit_turn_run(run_path)
        self.assertEqual(caught.exception.code, "turn-run-member-too-large")
        self.assertEqual(caught.exception.details["limit"], 16 * 1024 * 1024)

    def test_descriptor_path_substitution_reports_structured_refusal(self) -> None:
        run = self.begin()
        run_path = Path(run["run_path"])
        packet_path = run_path / ARTIFACT_FILES["packet"]
        real_lstat = os.lstat
        calls = 0

        def changing_lstat(path: os.PathLike[str] | str):
            nonlocal calls
            result = real_lstat(path)
            if Path(path) == packet_path:
                calls += 1
                if calls >= 2:
                    values = list(result)
                    values[1] = result.st_ino + 1
                    return os.stat_result(values)
            return result

        with mock.patch("lacuna.sidecars.os.lstat", side_effect=changing_lstat):
            with self.assertRaises(LacunaError) as caught:
                audit_turn_run(run_path)
        self.assertEqual(caught.exception.code, "turn-run-member-unsafe")
        self.assertIn("substituted during read", caught.exception.message)

    @unittest.skipIf(os.name == "nt", "POSIX symlink semantics")
    def test_next_pointer_symlink_is_refused_but_explicit_recovery_replaces_it(self) -> None:
        run = self.begin()
        run_path = Path(run["run_path"])
        next_path = run_path / NEXT_FILE
        target = self.root / "external-next.md"
        original = next_path.read_bytes()
        target.write_bytes(original)
        next_path.unlink()
        next_path.symlink_to(target)

        with self.assertRaises(LacunaError) as caught:
            audit_turn_run(run_path)
        self.assertEqual(caught.exception.code, "turn-run-member-unsafe")

        recovered = recover_turn_run(run_path)
        self.assertEqual(recovered["run_id"], run["run_id"])
        self.assertFalse(next_path.is_symlink())
        self.assertEqual(target.read_bytes(), original)
        self.assertEqual(audit_turn_run(run_path)["status"], "awaiting-planner")


if __name__ == "__main__":
    unittest.main()
