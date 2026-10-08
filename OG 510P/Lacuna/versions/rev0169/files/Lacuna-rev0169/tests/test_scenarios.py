from __future__ import annotations

import os
import unittest

import copy
import json
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

from tests._schema_support import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from lacuna.errors import LacunaError
from lacuna.contamination import (
    CONTAMINATION_PLAN_FILE,
    CONTAMINATION_SCAN_FILE,
    FILESYSTEM_CANARY_FILE,
    build_scenario_contamination_scan,
)
from lacuna.scenarios import (
    ASSIGNMENT_FILE,
    BLIND_PACKET_FILE,
    REPORT_FILE,
    RETCON_ROLES,
    RUN_MANIFEST_FILE,
    SCENARIO_CONDITIONS,
    audit_scenario_run,
    begin_scenario_run,
    build_scenario_capsule_template,
    dispatch_scenario_cell,
    record_scenario_cell,
    record_scenario_masking,
    record_scenario_rating,
    scenario_contamination_scan,
    scenario_contamination_scan_markdown,
    scenario_masking_template,
    scenario_rating_template,
    unblind_scenario_run,
)
from lacuna.store import Cube
from lacuna.sidecars import canonical_json_digest
from lacuna.util import atomic_write_json


@unittest.skipUnless(
    os.environ.get("LACUNA_HEAVY_TESTS") == "1",
    "set LACUNA_HEAVY_TESTS=1 to run comparative scenario integration tests",
)
class ComparativeScenarioTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.cube_path = self.root / "seed"
        self.run_root = self.root / "scenario-runs"
        with Cube.init(self.cube_path) as cube:
            self.capsule = build_scenario_capsule_template(cube)
        self.capsule["script"][0]["player_input"] = (
            "I leave the greenhouse path and ring the cracked silver bell."
        )
        self.capsule["script"][1]["player_input"] = (
            "I ask the custodian why the bell answered from underground."
        )
        self.capsule["model_policy"].update(
            {
                "model_family": "fixture-family",
                "model": "fixture-model",
                "model_version": "fixture-v1",
                "sampling_policy": "Deterministic fixture policy shared by every cell.",
            }
        )

    def tearDown(self) -> None:
        self.temporary.cleanup()

    @staticmethod
    def validate_schema(filename: str, value: dict) -> None:
        if Draft202012Validator is None:
            return
        schema = json.loads((ROOT / "schemas" / filename).read_text(encoding="utf-8"))
        Draft202012Validator(schema).validate(value)

    def begin(self) -> dict:
        with Cube.open(self.cube_path) as cube:
            return begin_scenario_run(
                cube,
                self.capsule,
                reference=str(self.cube_path),
                resolved_seed_cube_path=str(self.cube_path.resolve()),
                root=self.run_root,
            )

    def test_begin_refuses_unedited_generated_template(self) -> None:
        unedited_path = self.root / "unedited-seed"
        run_root = self.root / "unedited-template-run"
        with Cube.init(unedited_path) as cube:
            capsule = build_scenario_capsule_template(cube)
            with self.assertRaises(LacunaError) as caught:
                begin_scenario_run(
                    cube,
                    capsule,
                    reference=str(unedited_path),
                    resolved_seed_cube_path=str(unedited_path.resolve()),
                    root=run_root,
                )
        self.assertEqual(caught.exception.code, "scenario-capsule-template-not-edited")
        self.assertFalse(run_root.exists())

    @staticmethod
    def _accepted_invocation(
        driver: dict,
        *,
        sequence: int,
        phase: str,
        role: str,
        context_id: str,
        script_step_id: str,
        checkpoint_step_id: str | None,
        managed_checkpoint_id: str | None = None,
        continuation_checkpoint_id: str | None = None,
        continuation_capsule_sha256: str | None = None,
    ) -> dict:
        item = copy.deepcopy(driver["return_contract"]["template"]["invocations"][0])
        item.update(
            {
                "sequence": sequence,
                "phase": phase,
                "role": role,
                "script_step_id": script_step_id,
                "checkpoint_step_id": checkpoint_step_id,
                "managed_checkpoint_id": managed_checkpoint_id,
                "continuation_checkpoint_id": continuation_checkpoint_id,
                "continuation_capsule_sha256": continuation_capsule_sha256,
                "context_id": context_id,
                "input_sha256": f"{sequence % 10}" * 64,
                "output_sha256": f"{(sequence + 4) % 10}" * 64,
            }
        )
        return item

    def valid_return(self, driver: dict, *, narration: str | None = None) -> dict:
        result = copy.deepcopy(driver["return_contract"]["template"])
        result["transcript"] = [
            {
                "step_id": step["step_id"],
                "narration": narration or f"Controlled continuation for {step['step_id']}.",
            }
            for step in driver["script"]
        ]
        invocations: list[dict] = []
        sequence = 1
        cell_label = driver["cell_label"]
        persistent_context = f"{cell_label}.persistent"
        narrator_segment = 0
        pending_checkpoint_id: str | None = None
        for step in driver["script"]:
            step_id = step["step_id"]
            role_separated = driver["condition"] == "lacuna-role-separated"
            narrator_context = (
                f"{cell_label}.narrator.{narrator_segment}"
                if role_separated
                else persistent_context
            )
            invocations.append(
                self._accepted_invocation(
                    driver,
                    sequence=sequence,
                    phase="ordinary-turn",
                    role="lacuna-narrator",
                    context_id=narrator_context,
                    script_step_id=step_id,
                    checkpoint_step_id=None,
                    continuation_checkpoint_id=pending_checkpoint_id,
                    continuation_capsule_sha256=(
                        f"{(sequence + 7) % 10}" * 64
                        if pending_checkpoint_id is not None
                        else None
                    ),
                )
            )
            pending_checkpoint_id = None
            sequence += 1
            if not step["checkpoint_after"]:
                continue
            if driver["condition"] == "prompt-only-retcon":
                invocations.append(
                    self._accepted_invocation(
                        driver,
                        sequence=sequence,
                        phase="checkpoint",
                        role="monolithic-retcon",
                        context_id=persistent_context,
                        script_step_id=step_id,
                        checkpoint_step_id=step_id,
                    )
                )
                sequence += 1
            elif driver["condition"] in {"lacuna-serial", "lacuna-role-separated"}:
                checkpoint_id = f"checkpoint.{cell_label}.{step_id}"
                for ordinal, role in enumerate(RETCON_ROLES, start=1):
                    context = (
                        persistent_context
                        if driver["condition"] == "lacuna-serial"
                        else f"{cell_label}.separate.{step_id}.{ordinal}"
                    )
                    invocations.append(
                        self._accepted_invocation(
                            driver,
                            sequence=sequence,
                            phase="checkpoint",
                            role=role,
                            context_id=context,
                            script_step_id=step_id,
                            checkpoint_step_id=step_id,
                            managed_checkpoint_id=checkpoint_id,
                        )
                    )
                    sequence += 1
                if role_separated:
                    narrator_segment += 1
                    pending_checkpoint_id = checkpoint_id
        result["invocations"] = invocations
        return result

    def complete_cells(self, run: dict) -> dict:
        for _ in SCENARIO_CONDITIONS:
            driver = dispatch_scenario_cell(run["run_path"])
            run = record_scenario_cell(run["run_path"], self.valid_return(driver))
        return run

    def valid_rating(self, run: dict, *, rater_id: str = "rater.fixture") -> dict:
        rating = scenario_rating_template(run["run_path"], rater_id=rater_id)
        for index, item in enumerate(rating["ratings"], start=1):
            item["preference_rank"] = index
            item["comments"] = f"Opaque cell {index}."
            item["scores"] = {dimension: 4 for dimension in item["scores"]}
        return rating

    def valid_masking(self, run: dict, *, assessor_id: str = "rater.fixture") -> dict:
        masking = scenario_masking_template(run["run_path"], assessor_id=assessor_id)
        for index, item in enumerate(masking["assessments"], start=1):
            item["guessed_condition"] = "unknown"
            item["confidence"] = index
            item["cues"] = ["no decisive method cue"]
            item["familiarity"] = "low"
            item["recognized_method"] = False
        return masking

    def test_capsule_requires_observable_turn_after_every_checkpoint(self) -> None:
        invalid = copy.deepcopy(self.capsule)
        invalid["script"][-1].update(
            {
                "checkpoint_after": True,
                "checkpoint_trigger": "This would have no observable continuation.",
            }
        )
        with Cube.open(self.cube_path) as cube:
            with self.assertRaises(LacunaError) as caught:
                begin_scenario_run(
                    cube,
                    invalid,
                    reference=str(self.cube_path),
                    resolved_seed_cube_path=str(self.cube_path.resolve()),
                    root=self.run_root,
                )
        self.assertEqual(caught.exception.code, "bad-scenario-capsule")
        self.assertFalse(self.run_root.exists())

    def test_begin_commits_hidden_assignment_and_exact_seed_clones(self) -> None:
        with Cube.open(self.cube_path) as seed:
            seed_snapshot = seed.snapshot()
            seed_head = seed.head()
        run = self.begin()
        self.assertEqual(run["status"], "collecting-results")
        self.validate_schema("scenario-run.v3.schema.json", run)
        self.validate_schema("scenario-capsule.v1.schema.json", self.capsule)
        self.assertEqual([cell["status"] for cell in run["cells"]], ["pending"] * 4)
        manifest_text = (Path(run["run_path"]) / RUN_MANIFEST_FILE).read_text(encoding="utf-8")
        for condition in SCENARIO_CONDITIONS:
            self.assertNotIn(condition, manifest_text)
        for cell in run["cells"]:
            with Cube.open(Path(run["run_path"]) / cell["cube_path"]) as clone:
                self.assertEqual(clone.head(), seed_head)
                self.assertEqual(clone.snapshot(), seed_snapshot)
        assignment = json.loads(
            (Path(run["run_path"]) / ASSIGNMENT_FILE).read_text(encoding="utf-8")
        )
        self.assertEqual(
            {item["condition"] for item in assignment["assignments"]},
            set(SCENARIO_CONDITIONS),
        )
        self.validate_schema("scenario-assignment.v1.schema.json", assignment)
        contamination_plan = json.loads(
            (Path(run["run_path"]) / CONTAMINATION_PLAN_FILE).read_text(encoding="utf-8")
        )
        self.validate_schema(
            "scenario-contamination-plan.v1.schema.json", contamination_plan
        )
        self.assertEqual(len(contamination_plan["canaries"]), 8)
        for cell in run["cells"]:
            self.assertTrue(
                (
                    Path(run["run_path"])
                    / "cells"
                    / cell["label"]
                    / FILESYSTEM_CANARY_FILE
                ).is_file()
            )
        for cell in run["cells"]:
            driver = json.loads(
                (Path(run["run_path"]) / cell["driver"]["path"]).read_text(encoding="utf-8")
            )
            self.validate_schema("scenario-cell-driver.v2.schema.json", driver)
            self.assertTrue(
                driver["contamination_controls"]["operator_canary"]["token"].startswith(
                    "LACUNA_CANARY_OPERATOR_ONLY_"
                )
            )
        self.assertEqual(run["assignment"]["sha256"], canonical_json_digest(assignment, error_code="test-digest", label="assignment"))

    def test_complete_run_blinds_then_rates_then_unblinds(self) -> None:
        run = self.complete_cells(self.begin())
        self.assertEqual(run["status"], "awaiting-ratings")
        blind_packet = json.loads(
            (Path(run["run_path"]) / BLIND_PACKET_FILE).read_text(encoding="utf-8")
        )
        self.validate_schema("scenario-run.v3.schema.json", run)
        self.validate_schema("scenario-blind-rating-packet.v1.schema.json", blind_packet)
        contamination_scan = scenario_contamination_scan(run["run_path"])
        self.validate_schema(
            "scenario-contamination-scan.v1.schema.json", contamination_scan
        )
        self.assertEqual(contamination_scan["overall_status"], "clean")
        self.assertEqual(contamination_scan["unexpected_matches"], [])
        self.assertNotIn("LACUNA_CANARY_", json.dumps(blind_packet, sort_keys=True))
        for cell in run["cells"]:
            receipt = json.loads(
                (Path(run["run_path"]) / cell["result"]["path"]).read_text(encoding="utf-8")
            )
            cell_return = json.loads(
                (Path(run["run_path"]) / receipt["return_artifact"]["path"]).read_text(encoding="utf-8")
            )
            self.validate_schema("scenario-cell-receipt.v1.schema.json", receipt)
            self.validate_schema("scenario-cell-return.v1.schema.json", cell_return)
        blind_text = json.dumps(blind_packet, sort_keys=True)
        for condition in SCENARIO_CONDITIONS:
            self.assertNotIn(condition, blind_text)
        rating = self.valid_rating(run, rater_id="rater.fixture")
        self.validate_schema("scenario-rating.v1.schema.json", rating)
        run = record_scenario_rating(run["run_path"], rating)
        self.assertEqual(run["status"], "awaiting-masking")
        with self.assertRaises(LacunaError) as caught:
            unblind_scenario_run(run["run_path"])
        self.assertEqual(caught.exception.code, "scenario-run-not-ready-to-unblind")
        masking = self.valid_masking(run, assessor_id="rater.fixture")
        self.validate_schema("scenario-masking-assessment.v1.schema.json", masking)
        run = record_scenario_masking(run["run_path"], masking)
        self.assertEqual(run["status"], "ready-to-unblind")
        report = unblind_scenario_run(run["run_path"])
        self.assertEqual(report["schema"], "lacuna.scenario-report.v3")
        self.validate_schema("scenario-report.v3.schema.json", report)
        self.assertEqual(report["method_identifiability_summary"]["assessor_count"], 1)
        self.assertEqual(report["contamination_summary"]["overall_status"], "clean")
        self.assertEqual(report["contamination_summary"]["unexpected_match_count"], 0)
        self.assertEqual(
            {record["condition"] for record in report["cell_records"]},
            set(SCENARIO_CONDITIONS),
        )
        self.assertTrue((Path(run["run_path"]) / REPORT_FILE).is_file())
        self.assertEqual(audit_scenario_run(run["run_path"])["status"], "unblinded")

    def test_cross_cell_canary_leak_is_retained_before_blind_rating(self) -> None:
        run = self.begin()
        owner_label = None
        leaked_token = None
        observed_label = None
        for index in range(len(SCENARIO_CONDITIONS)):
            driver = dispatch_scenario_cell(run["run_path"])
            if leaked_token is None:
                owner_label = driver["cell_label"]
                leaked_token = driver["contamination_controls"]["operator_canary"][
                    "token"
                ]
            result = self.valid_return(driver)
            if index == len(SCENARIO_CONDITIONS) - 1:
                observed_label = driver["cell_label"]
                result["transcript"][0]["narration"] += f" {leaked_token}"
            run = record_scenario_cell(run["run_path"], result)
        self.assertEqual(run["status"], "awaiting-ratings")
        scan = scenario_contamination_scan(run["run_path"])
        self.assertEqual(scan["overall_status"], "leak-detected")
        matching = [
            item
            for item in scan["unexpected_matches"]
            if item["owner_cell_label"] == owner_label
            and item["observed_cell_label"] == observed_label
        ]
        self.assertTrue(matching)
        self.assertTrue(
            all(item["classification"] == "cross-cell-leak" for item in matching)
        )
        self.validate_schema("scenario-contamination-scan.v1.schema.json", scan)
        markdown = scenario_contamination_scan_markdown(run["run_path"])
        self.assertIn("## Unexpected exact matches", markdown)
        self.assertIn("content", markdown)
        self.assertIn(observed_label, markdown)
        self.assertEqual(audit_scenario_run(run["run_path"])["status"], "awaiting-ratings")

    def test_filesystem_only_canary_leak_is_detected_in_its_own_cell(self) -> None:
        run = self.begin()
        owner_label = None
        leaked_token = None
        for index in range(len(SCENARIO_CONDITIONS)):
            driver = dispatch_scenario_cell(run["run_path"])
            result = self.valid_return(driver)
            if index == 0:
                owner_label = driver["cell_label"]
                source = (
                    Path(run["run_path"])
                    / "cells"
                    / owner_label
                    / FILESYSTEM_CANARY_FILE
                ).read_text(encoding="utf-8")
                leaked_token = source.strip().splitlines()[-1]
                result["transcript"][0]["narration"] += f" {leaked_token}"
            run = record_scenario_cell(run["run_path"], result)
        scan = scenario_contamination_scan(run["run_path"])
        matches = [
            item
            for item in scan["unexpected_matches"]
            if item["owner_cell_label"] == owner_label
            and item["observed_cell_label"] == owner_label
            and item["scope"] == "filesystem-only"
        ]
        self.assertTrue(matches)
        self.assertTrue(
            all(item["classification"] == "same-cell-leak" for item in matches)
        )

    def test_contamination_scan_includes_committed_cube_state(self) -> None:
        run = self.begin()
        owner_label = None
        leaked_token = None
        for index in range(len(SCENARIO_CONDITIONS)):
            driver = dispatch_scenario_cell(run["run_path"])
            if index == 0:
                owner_label = driver["cell_label"]
                leaked_token = driver["contamination_controls"]["operator_canary"][
                    "token"
                ]
                cell = next(
                    item for item in run["cells"] if item["label"] == owner_label
                )
                with Cube.open(Path(run["run_path"]) / cell["cube_path"]) as cube:
                    cube.apply_operations(
                        actor_id="user",
                        operations=[
                            {
                                "op": "register_agent",
                                "agent_id": "canary.cube.contaminant",
                                "kind": "tool",
                                "label": leaked_token,
                                "metadata": {},
                            }
                        ],
                        message="retain an exact canary in otherwise valid cube state",
                    )
            run = record_scenario_cell(run["run_path"], self.valid_return(driver))
        scan = scenario_contamination_scan(run["run_path"])
        matches = [
            item
            for item in scan["unexpected_matches"]
            if item["owner_cell_label"] == owner_label
            and item["observed_cell_label"] == owner_label
            and "/cube/" in item["path"]
        ]
        self.assertTrue(matches)
        self.assertTrue(
            any(
                item["path"].endswith("/cube/lacuna.sqlite3")
                and item["match_surface"] == "content"
                for item in matches
            )
        )

    def test_contamination_scan_refuses_an_unplanned_cell_directory(self) -> None:
        run = self.begin()
        run_path = Path(run["run_path"])
        plan = json.loads(
            (run_path / CONTAMINATION_PLAN_FILE).read_text(encoding="utf-8")
        )
        (run_path / "cells" / "cell.unplanned").mkdir()
        with self.assertRaises(LacunaError) as caught:
            build_scenario_contamination_scan(
                run_path, plan, scanned_at="2026-06-25T00:00:00Z"
            )
        self.assertEqual(caught.exception.code, "scenario-contamination-tree-mismatch")

    def test_contamination_scan_does_not_exempt_sqlite_sidecar_names(self) -> None:
        run = self.begin()
        run_path = Path(run["run_path"])
        driver = dispatch_scenario_cell(run_path)
        token = driver["contamination_controls"]["operator_canary"]["token"]
        path = (
            run_path
            / "cells"
            / driver["cell_label"]
            / "cube"
            / "lacuna.sqlite3-wal"
        )
        path.write_text(token, encoding="ascii")
        plan = json.loads(
            (run_path / CONTAMINATION_PLAN_FILE).read_text(encoding="utf-8")
        )
        scan = build_scenario_contamination_scan(
            run_path, plan, scanned_at="2026-06-25T00:00:00Z"
        )
        self.assertTrue(
            any(
                item["path"].endswith("/cube/lacuna.sqlite3-wal")
                and item["match_surface"] == "content"
                for item in scan["unexpected_matches"]
            )
        )

    def test_contamination_scan_does_not_exempt_lock_basenames(self) -> None:
        run = self.begin()
        run_path = Path(run["run_path"])
        driver = dispatch_scenario_cell(run_path)
        token = driver["contamination_controls"]["operator_canary"]["token"]
        (run_path / "cells" / driver["cell_label"] / ".run.lock").write_text(
            token, encoding="ascii"
        )
        plan = json.loads(
            (run_path / CONTAMINATION_PLAN_FILE).read_text(encoding="utf-8")
        )
        scan = build_scenario_contamination_scan(
            run_path, plan, scanned_at="2026-06-25T00:00:00Z"
        )
        self.assertTrue(
            any(
                item["path"].endswith("/.run.lock")
                and item["match_surface"] == "content"
                for item in scan["unexpected_matches"]
            )
        )

    def test_contamination_scan_detects_token_in_a_relative_path(self) -> None:
        run = self.begin()
        run_path = Path(run["run_path"])
        driver = dispatch_scenario_cell(run_path)
        token = driver["contamination_controls"]["operator_canary"]["token"]
        leaked_path = (
            run_path
            / "cells"
            / driver["cell_label"]
            / f"unexpected-{token}.txt"
        )
        leaked_path.write_bytes(b"")
        plan = json.loads(
            (run_path / CONTAMINATION_PLAN_FILE).read_text(encoding="utf-8")
        )
        scan = build_scenario_contamination_scan(
            run_path, plan, scanned_at="2026-06-25T00:00:00Z"
        )
        self.assertTrue(
            any(
                item["path"].endswith(f"/unexpected-{token}.txt")
                and item["match_surface"] == "relative-path"
                for item in scan["unexpected_matches"]
            )
        )

    def test_contamination_scan_fails_closed_on_walk_enumeration_error(self) -> None:
        run = self.begin()
        run_path = Path(run["run_path"])
        plan = json.loads(
            (run_path / CONTAMINATION_PLAN_FILE).read_text(encoding="utf-8")
        )

        def failing_walk(*args, **kwargs):
            onerror = kwargs.get("onerror")
            self.assertIsNotNone(onerror)
            onerror(PermissionError("synthetic walk failure"))
            return iter(())

        with patch("lacuna.contamination.os.walk", side_effect=failing_walk):
            with self.assertRaises(LacunaError) as caught:
                build_scenario_contamination_scan(
                    run_path, plan, scanned_at="2026-06-25T00:00:00Z"
                )
        self.assertEqual(caught.exception.code, "scenario-contamination-scan-failed")

    @unittest.skipUnless(hasattr(os, "symlink"), "symlinks unavailable")
    def test_contamination_scan_refuses_a_symlinked_cells_root(self) -> None:
        run = self.begin()
        run_path = Path(run["run_path"])
        plan = json.loads((run_path / CONTAMINATION_PLAN_FILE).read_text(encoding="utf-8"))
        original = run_path / "cells"
        relocated = run_path / "cells-relocated"
        original.rename(relocated)
        os.symlink(relocated, original)
        with self.assertRaises(LacunaError) as caught:
            build_scenario_contamination_scan(
                run_path, plan, scanned_at="2026-06-25T00:00:00Z"
            )
        self.assertEqual(caught.exception.code, "scenario-contamination-member-unsafe")

    @unittest.skipUnless(hasattr(os, "symlink"), "symlinks unavailable")
    def test_unsafe_scan_member_refuses_before_manifest_advance_and_can_retry(self) -> None:
        run = self.begin()
        for _ in range(len(SCENARIO_CONDITIONS) - 1):
            driver = dispatch_scenario_cell(run["run_path"])
            run = record_scenario_cell(run["run_path"], self.valid_return(driver))
        driver = dispatch_scenario_cell(run["run_path"])
        result = self.valid_return(driver)
        run_path = Path(run["run_path"])
        unsafe = run_path / "cells" / driver["cell_label"] / "turn-runs" / "unsafe-link"
        os.symlink(run_path / CONTAMINATION_PLAN_FILE, unsafe)
        before = (run_path / RUN_MANIFEST_FILE).read_bytes()
        with self.assertRaises(LacunaError) as caught:
            record_scenario_cell(run_path, result)
        self.assertEqual(caught.exception.code, "scenario-contamination-member-unsafe")
        self.assertEqual((run_path / RUN_MANIFEST_FILE).read_bytes(), before)
        unsafe.unlink()
        run = record_scenario_cell(run_path, result)
        self.assertEqual(run["status"], "awaiting-ratings")
        self.assertEqual(scenario_contamination_scan(run_path)["overall_status"], "clean")

    def test_role_separation_topology_failure_is_nonmutating(self) -> None:
        run = self.begin()
        while True:
            driver = dispatch_scenario_cell(run["run_path"])
            if driver["condition"] == "lacuna-role-separated":
                break
            run = record_scenario_cell(run["run_path"], self.valid_return(driver))
        result = self.valid_return(driver)
        checkpoint = [item for item in result["invocations"] if item["phase"] == "checkpoint"]
        for item in checkpoint:
            item["context_id"] = "illegally.shared"
        run_path = Path(run["run_path"])
        manifest_before = (run_path / RUN_MANIFEST_FILE).read_bytes()
        with self.assertRaises(LacunaError) as caught:
            record_scenario_cell(run_path, result)
        self.assertEqual(caught.exception.code, "scenario-condition-topology-mismatch")
        self.assertEqual((run_path / RUN_MANIFEST_FILE).read_bytes(), manifest_before)
        self.assertFalse((run_path / "cells" / driver["cell_label"] / "40-cell-return.json").exists())
        self.assertEqual(audit_scenario_run(run_path)["status"], "collecting-results")

    def test_role_separated_continuation_requires_exact_capsule_binding(self) -> None:
        run = self.begin()
        while True:
            driver = dispatch_scenario_cell(run["run_path"])
            if driver["condition"] == "lacuna-role-separated":
                break
            run = record_scenario_cell(run["run_path"], self.valid_return(driver))
        result = self.valid_return(driver)
        post_checkpoint = [
            item
            for item in result["invocations"]
            if item["phase"] == "ordinary-turn"
            and item["script_step_id"] == "step.post-checkpoint-1"
        ][0]
        post_checkpoint["continuation_checkpoint_id"] = None
        post_checkpoint["continuation_capsule_sha256"] = None

        run_path = Path(run["run_path"])
        manifest_before = (run_path / RUN_MANIFEST_FILE).read_bytes()
        with self.assertRaises(LacunaError) as caught:
            record_scenario_cell(run_path, result)
        self.assertEqual(caught.exception.code, "scenario-condition-topology-mismatch")
        self.assertEqual((run_path / RUN_MANIFEST_FILE).read_bytes(), manifest_before)

    def test_role_separated_post_checkpoint_narrator_must_be_fresh(self) -> None:
        run = self.begin()
        while True:
            driver = dispatch_scenario_cell(run["run_path"])
            if driver["condition"] == "lacuna-role-separated":
                break
            run = record_scenario_cell(run["run_path"], self.valid_return(driver))
        result = self.valid_return(driver)
        ordinary = [item for item in result["invocations"] if item["phase"] == "ordinary-turn"]
        ordinary[1]["context_id"] = ordinary[0]["context_id"]
        with self.assertRaises(LacunaError) as caught:
            record_scenario_cell(run["run_path"], result)
        self.assertEqual(caught.exception.code, "scenario-condition-topology-mismatch")

    def test_serial_condition_must_keep_narration_and_checkpoint_in_one_context(self) -> None:
        run = self.begin()
        while True:
            driver = dispatch_scenario_cell(run["run_path"])
            if driver["condition"] == "lacuna-serial":
                break
            run = record_scenario_cell(run["run_path"], self.valid_return(driver))
        result = self.valid_return(driver)
        ordinary = [item for item in result["invocations"] if item["phase"] == "ordinary-turn"]
        ordinary[1]["context_id"] = "illegally.fresh.serial.context"
        with self.assertRaises(LacunaError) as caught:
            record_scenario_cell(run["run_path"], result)
        self.assertEqual(caught.exception.code, "scenario-condition-topology-mismatch")

    def test_cross_cell_context_reuse_is_rejected_before_any_write(self) -> None:
        run = self.begin()
        first_driver = dispatch_scenario_cell(run["run_path"])
        first_return = self.valid_return(first_driver)
        shared_context = "provider.session.reused"
        if first_driver["condition"] == "lacuna-role-separated":
            first_return["invocations"][0]["context_id"] = shared_context
        else:
            for invocation in first_return["invocations"]:
                invocation["context_id"] = shared_context
        run = record_scenario_cell(run["run_path"], first_return)

        second_driver = dispatch_scenario_cell(run["run_path"])
        second_return = self.valid_return(second_driver)
        if second_driver["condition"] == "lacuna-role-separated":
            second_return["invocations"][0]["context_id"] = shared_context
        else:
            for invocation in second_return["invocations"]:
                invocation["context_id"] = shared_context
        run_path = Path(run["run_path"])
        manifest_before = (run_path / RUN_MANIFEST_FILE).read_bytes()
        with self.assertRaises(LacunaError) as caught:
            record_scenario_cell(run_path, second_return)
        self.assertEqual(caught.exception.code, "scenario-cross-cell-context-reuse")
        self.assertEqual((run_path / RUN_MANIFEST_FILE).read_bytes(), manifest_before)
        self.assertFalse(
            (run_path / "cells" / second_driver["cell_label"] / "40-cell-return.json").exists()
        )

    def test_script_step_execution_and_checkpoint_order_are_enforced(self) -> None:
        self.capsule["script"][1].update(
            {
                "checkpoint_after": True,
                "checkpoint_trigger": "Reconsider again without moving observed facts.",
                "tags": ["off-script-departure"],
            }
        )
        self.capsule["script"].append(
            {
                "step_id": "step.post-checkpoint-2",
                "player_input": "Take one exact action after the second checkpoint.",
                "checkpoint_after": False,
                "checkpoint_trigger": None,
                "tags": ["post-checkpoint-continuation"],
            }
        )
        run = self.begin()
        driver = dispatch_scenario_cell(run["run_path"])
        result = self.valid_return(driver)
        ordinary = [item for item in result["invocations"] if item["phase"] == "ordinary-turn"]
        self.assertEqual(len(ordinary), 3)
        ordinary[1]["script_step_id"] = ordinary[0]["script_step_id"]
        run_path = Path(run["run_path"])
        manifest_before = (run_path / RUN_MANIFEST_FILE).read_bytes()
        with self.assertRaises(LacunaError) as caught:
            record_scenario_cell(run_path, result)
        self.assertEqual(caught.exception.code, "scenario-condition-topology-mismatch")
        self.assertEqual((run_path / RUN_MANIFEST_FILE).read_bytes(), manifest_before)

    def test_partial_failure_cannot_omit_an_accepted_turn_from_the_transcript(self) -> None:
        run = self.begin()
        driver = dispatch_scenario_cell(run["run_path"])
        result = self.valid_return(driver)
        result["status"] = "failed"
        result["transcript"] = []
        result["failure"] = {"class": "interrupted", "message": "Stopped after an accepted turn."}
        run_path = Path(run["run_path"])
        manifest_before = (run_path / RUN_MANIFEST_FILE).read_bytes()
        with self.assertRaises(LacunaError) as caught:
            record_scenario_cell(run_path, result)
        self.assertEqual(caught.exception.code, "scenario-condition-topology-mismatch")
        self.assertEqual((run_path / RUN_MANIFEST_FILE).read_bytes(), manifest_before)

    def test_pending_cell_contamination_is_detected(self) -> None:
        run = self.begin()
        pending = run["cells"][1]
        cell_cube = Path(run["run_path"]) / pending["cube_path"]
        with Cube.open(cell_cube) as cube:
            cube.apply_operations(
                actor_id="user",
                operations=[
                    {
                        "op": "register_agent",
                        "agent_id": "contaminant",
                        "kind": "tool",
                        "label": "Contaminant",
                        "metadata": {},
                    }
                ],
                message="contaminate a pending scenario cell",
            )
        with self.assertRaises(LacunaError) as caught:
            audit_scenario_run(run["run_path"])
        self.assertEqual(caught.exception.code, "scenario-pending-cell-contaminated")

    def test_recorded_cell_mutation_breaks_frozen_receipt(self) -> None:
        run = self.begin()
        driver = dispatch_scenario_cell(run["run_path"])
        run = record_scenario_cell(run["run_path"], self.valid_return(driver))
        cell = run["cells"][0]
        with Cube.open(Path(run["run_path"]) / cell["cube_path"]) as cube:
            cube.apply_operations(
                actor_id="user",
                operations=[
                    {
                        "op": "register_agent",
                        "agent_id": "late.mutation",
                        "kind": "tool",
                        "label": "Late Mutation",
                        "metadata": {},
                    }
                ],
                message="mutate after acceptance",
            )
        with self.assertRaises(LacunaError) as caught:
            audit_scenario_run(run["run_path"])
        self.assertIn(
            caught.exception.code,
            {"scenario-cell-receipt-mismatch", "scenario-cell-cube-state-mismatch", "scenario-cell-frozen-state-mismatch"},
        )

    def test_rehashed_assignment_tamper_is_rejected(self) -> None:
        run = self.begin()
        run_path = Path(run["run_path"])
        assignment_path = run_path / ASSIGNMENT_FILE
        assignment = json.loads(assignment_path.read_text(encoding="utf-8"))
        assignment["assignments"][0]["condition"], assignment["assignments"][1]["condition"] = (
            assignment["assignments"][1]["condition"],
            assignment["assignments"][0]["condition"],
        )
        atomic_write_json(assignment_path, assignment)
        manifest = json.loads((run_path / RUN_MANIFEST_FILE).read_text(encoding="utf-8"))
        manifest["assignment"]["sha256"] = canonical_json_digest(assignment, error_code="test-digest", label="assignment")
        atomic_write_json(run_path / RUN_MANIFEST_FILE, manifest)
        with self.assertRaises(LacunaError) as caught:
            audit_scenario_run(run_path)
        self.assertEqual(caught.exception.code, "scenario-assignment-mismatch")

    def test_begin_binds_open_cube_to_exact_supplied_path(self) -> None:
        other = self.root / "other"
        with Cube.init(other):
            pass
        with Cube.open(self.cube_path) as cube:
            with self.assertRaises(LacunaError) as caught:
                begin_scenario_run(
                    cube,
                    self.capsule,
                    reference=str(other),
                    resolved_seed_cube_path=str(other.resolve()),
                    root=self.run_root,
                )
        self.assertEqual(caught.exception.code, "scenario-run-cube-path-mismatch")
        self.assertFalse(self.run_root.exists())

    def test_failed_initial_publication_leaves_no_run_or_staging_directory(self) -> None:
        with Cube.open(self.cube_path) as cube:
            with patch("lacuna.scenarios._write_manifest", side_effect=RuntimeError("synthetic write failure")):
                with self.assertRaises(RuntimeError):
                    begin_scenario_run(
                        cube,
                        self.capsule,
                        reference=str(self.cube_path),
                        resolved_seed_cube_path=str(self.cube_path.resolve()),
                        root=self.run_root,
                    )
        self.assertTrue(self.run_root.is_dir())
        self.assertEqual(list(self.run_root.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
