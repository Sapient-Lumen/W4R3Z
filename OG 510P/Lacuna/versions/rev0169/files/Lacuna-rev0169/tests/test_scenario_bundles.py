from __future__ import annotations

import os
import unittest

import copy
import csv
import io
import json
import shutil
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

from tests._schema_support import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from lacuna.errors import LacunaError
from lacuna.scenario_bundles import (
    COMMITMENT_FILE,
    BUNDLE_REPORT_FILE,
    SCHEDULE_FILE,
    audit_scenario_bundle,
    begin_scenario_bundle,
    build_scenario_bundle_plan,
    build_scenario_bundle_witness_template,
    dispatch_scenario_bundle_cell,
    record_scenario_bundle_cell,
    record_scenario_bundle_masking,
    record_scenario_bundle_rating,
    record_scenario_bundle_witness,
    recover_scenario_bundle,
    scenario_bundle_masking_template,
    scenario_bundle_rating_template,
    scenario_bundle_report_csv,
    seal_scenario_bundle_block,
    unblind_scenario_bundle,
)
from lacuna.scenarios import (
    RETCON_ROLES,
    SCENARIO_CONDITIONS,
    build_scenario_capsule_template,
    dispatch_scenario_cell,
    record_scenario_rating,
    record_scenario_masking,
    scenario_masking_template,
    scenario_rating_template,
    unblind_scenario_run,
)
from lacuna.store import Cube


@unittest.skipUnless(
    os.environ.get("LACUNA_HEAVY_TESTS") == "1"
    or os.environ.get("LACUNA_BUNDLE_TESTS") == "1",
    "set LACUNA_HEAVY_TESTS=1 or LACUNA_BUNDLE_TESTS=1 to run comparative scenario-bundle integration tests",
)
class ScenarioBundleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.seed_path = self.root / "seed"
        with Cube.init(self.seed_path) as cube:
            self.capsule_one = build_scenario_capsule_template(cube)
        self.capsule_one["script"][0]["player_input"] = (
            "I leave the greenhouse path and ring the cracked silver bell."
        )
        self.capsule_one["script"][1]["player_input"] = (
            "I ask the custodian why the bell answered from underground."
        )
        self.capsule_one["model_policy"].update(
            {
                "model_family": "fixture-family",
                "model": "fixture-model",
                "model_version": "fixture-v1",
                "sampling_policy": "Deterministic fixture policy shared by every cell.",
            }
        )
        self.capsule_two = copy.deepcopy(self.capsule_one)
        self.capsule_two["capsule_id"] = "scn_fixture_second"
        self.bundle_root = self.root / "bundles"

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def plan(self, *, witnesses: int = 0) -> dict:
        return build_scenario_bundle_plan(
            [
                {
                    "block_id": "blk_fixture_one",
                    "reference": str(self.seed_path),
                    "resolved_seed_cube_path": str(self.seed_path.resolve()),
                    "capsule": self.capsule_one,
                    "story_stratum": "story.alpha",
                    "model_stratum": "model.fixture",
                    "replicate": 1,
                    "tags": ["fixture"],
                },
                {
                    "block_id": "blk_fixture_two",
                    "reference": str(self.seed_path),
                    "resolved_seed_cube_path": str(self.seed_path.resolve()),
                    "capsule": self.capsule_two,
                    "story_stratum": "story.beta",
                    "model_stratum": "model.fixture",
                    "replicate": 1,
                    "tags": ["fixture"],
                },
            ],
            minimum_receipts_before_execution=witnesses,
        )

    def begin(self, *, witnesses: int = 0) -> dict:
        return begin_scenario_bundle(self.plan(witnesses=witnesses), root=self.bundle_root)

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

    def valid_return(self, driver: dict) -> dict:
        result = copy.deepcopy(driver["return_contract"]["template"])
        result["transcript"] = [
            {
                "step_id": step["step_id"],
                "narration": f"Controlled continuation for {driver['run_id']} / {step['step_id']}.",
            }
            for step in driver["script"]
        ]
        invocations: list[dict] = []
        sequence = 1
        prefix = f"{driver['run_id']}.{driver['cell_label']}"
        persistent_context = f"{prefix}.persistent"
        narrator_segment = 0
        pending_checkpoint_id: str | None = None
        for step in driver["script"]:
            step_id = step["step_id"]
            role_separated = driver["condition"] == "lacuna-role-separated"
            narrator_context = (
                f"{prefix}.narrator.{narrator_segment}"
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
                checkpoint_id = f"checkpoint.{driver['cell_label']}.{step_id}"
                for ordinal, role in enumerate(RETCON_ROLES, start=1):
                    context_id = (
                        persistent_context
                        if driver["condition"] == "lacuna-serial"
                        else f"{prefix}.separate.{step_id}.{ordinal}"
                    )
                    invocations.append(
                        self._accepted_invocation(
                            driver,
                            sequence=sequence,
                            phase="checkpoint",
                            role=role,
                            context_id=context_id,
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

    def complete_active_block(
        self,
        bundle_path: str,
        *,
        rater_id: str,
        leak_cross_cell_canary: bool = False,
    ) -> tuple[dict, str]:
        first_context = ""
        first_operator_canary = None
        manifest: dict = {}
        for index, _condition in enumerate(SCENARIO_CONDITIONS):
            driver = dispatch_scenario_bundle_cell(bundle_path)
            result = self.valid_return(driver)
            if not first_context:
                first_context = result["invocations"][0]["context_id"]
                first_operator_canary = driver["contamination_controls"][
                    "operator_canary"
                ]["token"]
            if leak_cross_cell_canary and index == len(SCENARIO_CONDITIONS) - 1:
                result["transcript"][0]["narration"] += f" {first_operator_canary}"
            manifest = record_scenario_bundle_cell(bundle_path, result)
        rating = scenario_bundle_rating_template(bundle_path, rater_id=rater_id)
        for index, item in enumerate(rating["ratings"], start=1):
            item["scores"] = {dimension: 4 for dimension in item["scores"]}
            item["preference_rank"] = index
            item["comments"] = f"Opaque preference {index}."
        manifest = record_scenario_bundle_rating(bundle_path, rating)
        self.assertEqual(manifest["status"], "block-active")
        masking = scenario_bundle_masking_template(bundle_path, assessor_id=rater_id)
        for index, item in enumerate(masking["assessments"], start=1):
            item["confidence"] = index
            item["cues"] = ["fixture post-rating cue"]
            item["familiarity"] = "low"
            item["recognized_method"] = False
        manifest = record_scenario_bundle_masking(bundle_path, masking)
        self.assertEqual(manifest["status"], "block-ready-to-seal")
        return manifest, first_context

    @staticmethod
    def child_path(manifest: dict, block_index: int) -> Path:
        return Path(manifest["bundle_path"]) / manifest["blocks"][block_index]["scenario_run"]["path"]

    @staticmethod
    def validate_schema(filename: str, value: dict) -> None:
        if Draft202012Validator is None:
            return
        schema = json.loads((ROOT / "schemas" / filename).read_text(encoding="utf-8"))
        Draft202012Validator(schema).validate(value)

    def test_begin_precreates_every_child_and_public_commitment_hides_mapping(self) -> None:
        plan = self.plan()
        manifest = begin_scenario_bundle(plan, root=self.bundle_root)
        self.assertEqual(manifest["status"], "block-active")
        self.assertEqual([block["status"] for block in manifest["blocks"]], ["active", "pending"])
        self.validate_schema("scenario-bundle-plan.v1.schema.json", plan)
        self.validate_schema("scenario-bundle.v2.schema.json", manifest)
        bundle_path = Path(manifest["bundle_path"])
        schedule = json.loads((bundle_path / SCHEDULE_FILE).read_text(encoding="utf-8"))
        commitment = json.loads((bundle_path / COMMITMENT_FILE).read_text(encoding="utf-8"))
        self.validate_schema("scenario-bundle-schedule.v1.schema.json", schedule)
        self.validate_schema("scenario-bundle-commitment.v1.schema.json", commitment)
        public_text = json.dumps(commitment, sort_keys=True)
        for condition in SCENARIO_CONDITIONS:
            self.assertNotIn(condition, public_text)
        self.assertNotIn(schedule["randomization_seed"], public_text)
        for block in manifest["blocks"]:
            child = audit_scenario_bundle(bundle_path)
            self.assertTrue((bundle_path / block["scenario_run"]["path"] / "run.json").is_file())
            self.assertEqual(child["bundle_id"], manifest["bundle_id"])

    def test_all_blocks_seal_before_any_unblind_then_publish_rater_level_export(self) -> None:
        manifest = self.begin()
        bundle_path = manifest["bundle_path"]
        self.complete_active_block(
            bundle_path,
            rater_id="rater.one",
            leak_cross_cell_canary=True,
        )
        first_seal = seal_scenario_bundle_block(bundle_path)
        self.validate_schema("scenario-bundle-block-seal.v3.schema.json", first_seal)
        self.assertRegex(first_seal["contamination_scan_sha256"], r"^[0-9a-f]{64}$")
        manifest = audit_scenario_bundle(bundle_path)
        self.assertEqual([block["status"] for block in manifest["blocks"]], ["sealed", "active"])
        first_child = json.loads((self.child_path(manifest, 0) / "run.json").read_text(encoding="utf-8"))
        self.assertEqual(first_child["status"], "ready-to-unblind")
        self.assertIsNone(first_child["report"])

        self.complete_active_block(bundle_path, rater_id="rater.two")
        seal_scenario_bundle_block(bundle_path)
        manifest = audit_scenario_bundle(bundle_path)
        self.assertEqual(manifest["status"], "ready-to-unblind")
        for index in range(2):
            child = json.loads((self.child_path(manifest, index) / "run.json").read_text(encoding="utf-8"))
            self.assertEqual(child["status"], "ready-to-unblind")

        report = unblind_scenario_bundle(bundle_path)
        self.validate_schema("scenario-bundle-report.v3.schema.json", report)
        self.assertEqual(len(report["block_records"]), 2)
        self.assertEqual(len(report["observations"]), 8)
        self.assertEqual(report["descriptive_summary"]["contamination"], {
            "clean_blocks": 1,
            "leak_detected_blocks": 1,
            "unexpected_match_count": 1,
        })
        self.assertEqual(report["block_records"][0]["contamination_status"], "leak-detected")
        self.assertTrue(
            any(
                item["contamination_status"] == "leak-detected"
                for item in report["observations"]
            )
        )
        self.assertEqual(audit_scenario_bundle(bundle_path)["status"], "unblinded")
        self.assertEqual(unblind_scenario_bundle(bundle_path), report)
        csv_text = scenario_bundle_report_csv(report)
        self.assertEqual(len(csv_text.splitlines()), 9)
        self.assertIn("seam_invisibility", csv_text.splitlines()[0])
        unsafe = copy.deepcopy(report)
        unsafe["observations"][0]["comments"] = "=HYPERLINK(\"https://example.invalid\")"
        unsafe["observations"][0]["story_stratum"] = "  @SUM(1,1)"
        exported = list(csv.DictReader(io.StringIO(scenario_bundle_report_csv(unsafe))))
        self.assertTrue(exported[0]["comments"].startswith("'="))
        self.assertTrue(exported[0]["story_stratum"].startswith("'  @"))
        self.assertTrue((Path(bundle_path) / BUNDLE_REPORT_FILE).is_file())

    def test_external_witness_gate_is_non_bypassable(self) -> None:
        manifest = self.begin(witnesses=1)
        bundle_path = manifest["bundle_path"]
        self.assertEqual(manifest["status"], "awaiting-witnesses")
        with self.assertRaises(LacunaError) as caught:
            dispatch_scenario_bundle_cell(bundle_path)
        self.assertEqual(caught.exception.code, "scenario-bundle-not-block-active")
        template = build_scenario_bundle_witness_template(bundle_path, witness_id="witness.fixture")
        template.update(
            {
                "kind": "external-retention",
                "service": "fixture-notary",
                "external_receipt_id": "receipt.fixture.001",
                "external_locator": "fixture://receipt/001",
                "witnessed_at": "2026-06-25T00:00:00Z",
            }
        )
        witness = record_scenario_bundle_witness(bundle_path, template)
        self.validate_schema("scenario-bundle-witness.v1.schema.json", witness)
        self.assertEqual(audit_scenario_bundle(bundle_path)["status"], "block-active")
        with self.assertRaises(LacunaError) as duplicate:
            record_scenario_bundle_witness(bundle_path, witness)
        self.assertEqual(duplicate.exception.code, "duplicate-scenario-bundle-witness")

    def test_cross_block_context_reuse_is_rejected_before_child_mutation(self) -> None:
        manifest = self.begin()
        bundle_path = manifest["bundle_path"]
        _, first_context = self.complete_active_block(bundle_path, rater_id="rater.one")
        seal_scenario_bundle_block(bundle_path)
        driver = dispatch_scenario_bundle_cell(bundle_path)
        result = self.valid_return(driver)
        result["invocations"][0]["context_id"] = first_context
        child_manifest_path = self.child_path(audit_scenario_bundle(bundle_path), 1) / "run.json"
        before = child_manifest_path.read_bytes()
        with self.assertRaises(LacunaError) as caught:
            record_scenario_bundle_cell(bundle_path, result)
        self.assertEqual(caught.exception.code, "scenario-bundle-cross-block-context-reuse")
        self.assertEqual(child_manifest_path.read_bytes(), before)
        self.assertEqual(audit_scenario_bundle(bundle_path)["status"], "block-active")

    def test_direct_child_advance_cannot_bypass_witness_gate(self) -> None:
        manifest = self.begin(witnesses=1)
        dispatch_scenario_cell(self.child_path(manifest, 0))
        with self.assertRaises(LacunaError) as caught:
            audit_scenario_bundle(manifest["bundle_path"])
        self.assertEqual(caught.exception.code, "scenario-bundle-witness-gate-bypassed")

    def test_future_child_direct_advance_is_detected(self) -> None:
        manifest = self.begin()
        future_path = self.child_path(manifest, 1)
        dispatch_scenario_cell(future_path)
        with self.assertRaises(LacunaError) as caught:
            audit_scenario_bundle(manifest["bundle_path"])
        self.assertEqual(caught.exception.code, "scenario-bundle-future-block-contaminated")

    def test_direct_child_unblind_before_all_blocks_are_sealed_is_detected(self) -> None:
        manifest = self.begin()
        bundle_path = manifest["bundle_path"]
        self.complete_active_block(bundle_path, rater_id="rater.one")
        seal_scenario_bundle_block(bundle_path)
        with self.assertRaises(LacunaError) as caught:
            unblind_scenario_run(self.child_path(audit_scenario_bundle(bundle_path), 0))
        self.assertEqual(caught.exception.code, "scenario-unblind-gate-closed")
        self.assertEqual(audit_scenario_bundle(bundle_path)["status"], "block-active")

    def test_recover_adopts_only_permitted_active_child_cache_drift(self) -> None:
        manifest = self.begin()
        bundle_path = manifest["bundle_path"]
        for _ in SCENARIO_CONDITIONS:
            driver = dispatch_scenario_bundle_cell(bundle_path)
            record_scenario_bundle_cell(bundle_path, self.valid_return(driver))
        child_path = self.child_path(audit_scenario_bundle(bundle_path), 0)
        rating = scenario_rating_template(child_path, rater_id="rater.direct")
        for index, item in enumerate(rating["ratings"], start=1):
            item["scores"] = {dimension: 3 for dimension in item["scores"]}
            item["preference_rank"] = index
            item["comments"] = "Direct child transition fixture."
        record_scenario_rating(child_path, rating)
        masking = scenario_masking_template(child_path, assessor_id="rater.direct")
        for item in masking["assessments"]:
            item["cues"] = ["direct child masking fixture"]
        record_scenario_masking(child_path, masking)
        with self.assertRaises(LacunaError) as caught:
            audit_scenario_bundle(bundle_path)
        self.assertEqual(caught.exception.code, "scenario-bundle-cached-state-stale")
        recovered = recover_scenario_bundle(bundle_path)
        self.assertEqual(recovered["status"], "block-ready-to-seal")

    def test_unblinding_is_idempotent_after_partial_child_completion(self) -> None:
        manifest = self.begin()
        bundle_path = manifest["bundle_path"]
        self.complete_active_block(bundle_path, rater_id="rater.one")
        seal_scenario_bundle_block(bundle_path)
        self.complete_active_block(bundle_path, rater_id="rater.two")
        seal_scenario_bundle_block(bundle_path)
        calls = 0

        def flaky(child_path: str | Path) -> dict:
            nonlocal calls
            calls += 1
            if calls == 2:
                raise RuntimeError("simulated process interruption")
            return unblind_scenario_run(child_path)

        with patch("lacuna.scenario_bundles.unblind_scenario_run", side_effect=flaky):
            with self.assertRaises(RuntimeError):
                unblind_scenario_bundle(bundle_path)
        interrupted = audit_scenario_bundle(bundle_path)
        self.assertEqual(interrupted["status"], "unblinding")
        self.assertEqual([block["status"] for block in interrupted["blocks"]], ["unblinded", "sealed"])
        report = unblind_scenario_bundle(bundle_path)
        self.assertEqual(report["schema"], "lacuna.scenario-bundle-report.v3")
        self.assertEqual(audit_scenario_bundle(bundle_path)["status"], "unblinded")

    def test_failed_staging_leaves_no_visible_bundle(self) -> None:
        from lacuna.scenario_bundles import stage_scenario_run as real_stage

        calls = 0

        def fail_second(*args, **kwargs):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise LacunaError("fixture-stage-failure", "stop")
            return real_stage(*args, **kwargs)

        with patch("lacuna.scenario_bundles.stage_scenario_run", side_effect=fail_second):
            with self.assertRaises(LacunaError):
                begin_scenario_bundle(self.plan(), root=self.bundle_root)
        self.assertEqual(list(self.bundle_root.iterdir()), [])

    @unittest.skipIf(not hasattr(os, "symlink"), "symlinks unavailable")
    def test_child_directory_symlink_substitution_is_refused(self) -> None:
        manifest = self.begin()
        active = self.child_path(manifest, 0)
        future = self.child_path(manifest, 1)
        shutil.rmtree(future)
        os.symlink(active, future, target_is_directory=True)
        with self.assertRaises(LacunaError) as caught:
            audit_scenario_bundle(manifest["bundle_path"])
        self.assertEqual(caught.exception.code, "scenario-bundle-member-unsafe")

    def test_plan_refuses_incomparable_rating_contracts(self) -> None:
        altered = copy.deepcopy(self.capsule_two)
        altered["rating"]["scale_max"] += 1
        blocks = self.plan()["blocks"]
        blocks[1]["capsule"] = altered
        with self.assertRaises(LacunaError) as caught:
            build_scenario_bundle_plan(blocks)
        self.assertEqual(caught.exception.code, "scenario-bundle-rating-policy-mismatch")

    def test_witness_threshold_accepts_v1_limit_and_rejects_overflow(self) -> None:
        plan = self.plan(witnesses=64)
        self.assertEqual(plan["witness_policy"]["minimum_receipts_before_execution"], 64)
        with self.assertRaises(LacunaError) as caught:
            self.plan(witnesses=65)
        self.assertEqual(caught.exception.code, "bad-scenario-bundle-plan")

    def test_witness_limit_refuses_before_sidecar_mutation(self) -> None:
        manifest = self.begin(witnesses=1)
        bundle_path = Path(manifest["bundle_path"])
        first = build_scenario_bundle_witness_template(bundle_path, witness_id="witness.first")
        first.update(
            {
                "service": "fixture-notary",
                "external_receipt_id": "receipt.fixture.first",
                "external_locator": "fixture://receipt/first",
                "witnessed_at": "2026-06-25T00:00:00Z",
            }
        )
        record_scenario_bundle_witness(bundle_path, first)
        before_manifest = (bundle_path / "bundle.json").read_bytes()
        before_members = sorted(
            str(path.relative_to(bundle_path)) for path in bundle_path.rglob("*")
        )

        second = build_scenario_bundle_witness_template(bundle_path, witness_id="witness.second")
        second.update(
            {
                "service": "fixture-notary",
                "external_receipt_id": "receipt.fixture.second",
                "external_locator": "fixture://receipt/second",
                "witnessed_at": "2026-06-25T00:01:00Z",
            }
        )
        with patch("lacuna.scenario_bundles.MAX_BUNDLE_WITNESSES", 1):
            with self.assertRaises(LacunaError) as caught:
                record_scenario_bundle_witness(bundle_path, second)
        self.assertEqual(caught.exception.code, "scenario-bundle-witness-limit")
        self.assertEqual((bundle_path / "bundle.json").read_bytes(), before_manifest)
        self.assertEqual(
            sorted(str(path.relative_to(bundle_path)) for path in bundle_path.rglob("*")),
            before_members,
        )


if __name__ == "__main__":
    unittest.main()
