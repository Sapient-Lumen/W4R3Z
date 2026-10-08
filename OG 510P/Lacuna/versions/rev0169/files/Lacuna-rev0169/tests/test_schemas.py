from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

from tests._schema_support import Draft202012Validator, ValidationError

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from lacuna.store import OPERATION_FIELDS
from lacuna.turns import DIRECTOR_TURN_OPERATIONS


class ExchangeSchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.all_exchange_schemas = {
            path.name: json.loads(path.read_text(encoding="utf-8"))
            for path in sorted((ROOT / "schemas").glob("*.schema.json"))
        }
        cls.change_schema = json.loads(
            (ROOT / "schemas" / "change-set.v1.schema.json").read_text(encoding="utf-8")
        )
        cls.turn_schema = json.loads(
            (ROOT / "schemas" / "turn-proposal.v2.schema.json").read_text(encoding="utf-8")
        )
        cls.seal_opening_schema = json.loads(
            (ROOT / "schemas" / "seal-opening.v1.schema.json").read_text(encoding="utf-8")
        )
        cls.seal_receipt_schema = json.loads(
            (ROOT / "schemas" / "seal-receipt.v1.schema.json").read_text(encoding="utf-8")
        )
        cls.model_brief_schema = json.loads(
            (ROOT / "schemas" / "model-brief.v1.schema.json").read_text(encoding="utf-8")
        )
        cls.artifact_audit_schema = json.loads(
            (ROOT / "schemas" / "artifact-audit.v1.schema.json").read_text(encoding="utf-8")
        )
        cls.turn_run_schemas = {
            name: json.loads((ROOT / "schemas" / name).read_text(encoding="utf-8"))
            for name in (
                "turn-run.v1.schema.json",
                "turn-run.v2.schema.json",
                "turn-preparation.v1.schema.json",
                "turn-receipt.v3.schema.json",
                "turn-request.v2.schema.json",
                "turn-request.v3.schema.json",
                "turn-request.v4.schema.json",
                "agent-dispatch.v1.schema.json",
                "play-start.v1.schema.json",
            )
        }
        cls.orchestration_schemas = {
            name: json.loads((ROOT / "schemas" / name).read_text(encoding="utf-8"))
            for name in (
                "orchestration-plan.v1.schema.json",
                "turn-task-card.v1.schema.json",
                "planner-return.v1.schema.json",
                "narrator-return.v1.schema.json",
                "verifier-return.v1.schema.json",
            )
        }
        cls.checkpoint_schemas = {
            name: json.loads((ROOT / "schemas" / name).read_text(encoding="utf-8"))
            for name in (
                "checkpoint-request.v1.schema.json",
                "checkpoint-task-card.v1.schema.json",
                "checkpoint-candidates.v1.schema.json",
                "checkpoint-judgment.v1.schema.json",
                "checkpoint-compression.v1.schema.json",
                "checkpoint-proposal.v1.schema.json",
                "checkpoint-verifier-return.v1.schema.json",
                "checkpoint-review.v1.schema.json",
                "checkpoint-commit-receipt.v1.schema.json",
                "checkpoint-agent-dispatch.v1.schema.json",
                "checkpoint-run.v1.schema.json",
                "checkpoint-run-agent-dispatch.v1.schema.json",
                "checkpoint-invocation-receipt.v1.schema.json",
                "checkpoint-narrator-capsule.v1.schema.json",
                "checkpoint-continuation-dispatch.v1.schema.json",
                "checkpoint-continuation-dispatch.v2.schema.json",
                "public-history.v1.schema.json",
                "public-history.v2.schema.json",
                "public-history-view.v1.schema.json",
                "public-history-view.v2.schema.json",
            )
        }
        cls.scenario_schemas = {
            name: json.loads((ROOT / "schemas" / name).read_text(encoding="utf-8"))
            for name in (
                "scenario-capsule.v1.schema.json",
                "scenario-run.v1.schema.json",
                "scenario-run.v2.schema.json",
                "scenario-run.v3.schema.json",
                "scenario-assignment.v1.schema.json",
                "scenario-cell-driver.v1.schema.json",
                "scenario-cell-driver.v2.schema.json",
                "scenario-contamination-plan.v1.schema.json",
                "scenario-contamination-scan.v1.schema.json",
                "scenario-cell-return.v1.schema.json",
                "scenario-cell-receipt.v1.schema.json",
                "scenario-blind-rating-packet.v1.schema.json",
                "scenario-rating.v1.schema.json",
                "scenario-masking-assessment.v1.schema.json",
                "scenario-report.v1.schema.json",
                "scenario-report.v2.schema.json",
                "scenario-report.v3.schema.json",
                "scenario-bundle-plan.v1.schema.json",
                "scenario-bundle-schedule.v1.schema.json",
                "scenario-bundle-commitment.v1.schema.json",
                "scenario-bundle.v1.schema.json",
                "scenario-bundle.v2.schema.json",
                "scenario-bundle-witness.v1.schema.json",
                "scenario-bundle-block-seal.v1.schema.json",
                "scenario-bundle-block-seal.v2.schema.json",
                "scenario-bundle-block-seal.v3.schema.json",
                "scenario-bundle-report.v1.schema.json",
                "scenario-bundle-report.v2.schema.json",
                "scenario-bundle-report.v3.schema.json",
            )
        }

    @unittest.skipUnless(
        Draft202012Validator is not None,
        "jsonschema test extra is not installed",
    )
    def test_exchange_schemas_validate_against_draft_2020_12(self) -> None:
        assert Draft202012Validator is not None
        self.assertEqual(len(self.all_exchange_schemas), 72)
        for name, schema in self.all_exchange_schemas.items():
            with self.subTest(schema=name):
                Draft202012Validator.check_schema(schema)

    def test_change_set_operation_contract_matches_runtime(self) -> None:
        variants = self.change_schema["properties"]["operations"]["items"]["oneOf"]
        schema_operations = [item["properties"]["op"]["const"] for item in variants]
        self.assertEqual(len(schema_operations), len(set(schema_operations)))
        self.assertEqual(set(schema_operations), set(OPERATION_FIELDS))
        for variant in variants:
            operation = variant["properties"]["op"]["const"]
            self.assertEqual(set(variant["properties"]), OPERATION_FIELDS[operation])

    def test_turn_operation_enum_matches_runtime(self) -> None:
        turn_operations = set(
            self.turn_schema["properties"]["operations"]["items"]["properties"]["op"][
                "enum"
            ]
        )
        self.assertEqual(turn_operations, DIRECTOR_TURN_OPERATIONS)
        self.assertTrue(
            {"seal_precommitment", "reveal_precommitment", "void_precommitment"}.isdisjoint(
                turn_operations
            )
        )

    @unittest.skipUnless(
        Draft202012Validator is not None,
        "jsonschema test extra is not installed",
    )
    def test_seal_exchange_contracts_validate_and_reject_float_openings(self) -> None:
        assert Draft202012Validator is not None
        change = {
            "schema": "lacuna.change-set.v1",
            "actor_id": "user",
            "expected_head": "0" * 64,
            "operations": [
                {
                    "op": "seal_precommitment",
                    "seal_id": "seal_case",
                    "commitment_sha256": "a" * 64,
                    "scheme": "lacuna.salted-sha256-json.v1",
                    "label": "Case culprit",
                    "purpose": "mystery",
                    "visibility": "restricted",
                    "audience": ["player"],
                    "source_id": None,
                }
            ],
        }
        Draft202012Validator(self.change_schema).validate(change)
        opening = {
            "event": "lacuna.seal.opening.prepared",
            "schema": "lacuna.seal-opening.v1",
            "scheme": "lacuna.salted-sha256-json.v1",
            "cube_id": "cube_case",
            "seal_id": "seal_case",
            "commitment_sha256": "a" * 64,
            "nonce": "b" * 64,
            "payload": {"culprit": "Ada", "chapter": 7},
            "custody_warning": "Keep outside the cube.",
        }
        validator = Draft202012Validator(self.seal_opening_schema)
        validator.validate(opening)
        opening["payload"] = {"probability": 0.5}
        with self.assertRaises(ValidationError):
            validator.validate(opening)
        opening["payload"] = {"bad": "\ud800"}
        with self.assertRaises(ValidationError):
            validator.validate(opening)
        opening["payload"] = {"\udfff": "bad key"}
        with self.assertRaises(ValidationError):
            validator.validate(opening)

    @unittest.skipUnless(
        Draft202012Validator is not None,
        "jsonschema test extra is not installed",
    )
    def test_fair_play_receipt_schema_enforces_lifecycle_shape(self) -> None:
        assert Draft202012Validator is not None
        commitment_event = {
            "seq": 4,
            "event_id": "evt_seal",
            "event_hash": "1" * 64,
            "prev_hash": "0" * 64,
            "recorded_at": "2026-06-23T12:00:00Z",
            "change_after_head": "1" * 64,
        }
        immutable_seal = {
            "seal_id": "seal_case",
            "scheme": "lacuna.salted-sha256-json.v1",
            "commitment_sha256": "a" * 64,
            "label": "Case culprit",
            "purpose": "mystery",
            "visibility": "public",
            "audience": [],
            "created_seq": 4,
        }
        receipt_core = {
            "schema": "lacuna.fair-play-seal-receipt-core.v1",
            "cube_id": "cube_case",
            "seal": immutable_seal,
            "commitment_event": commitment_event,
        }
        receipt = {
            "event": "lacuna.fair-play-seal.receipt",
            "schema": "lacuna.fair-play-seal-receipt.v1",
            "cube_id": "cube_case",
            "current_head": "1" * 64,
            "receipt_sha256": "b" * 64,
            "receipt_core": receipt_core,
            "seal": {
                **immutable_seal,
                "revealed_seq": None,
                "voided_seq": None,
                "status": "sealed",
            },
            "commitment_event": commitment_event,
            "opening": None,
            "resolution": None,
            "nonclaims": ["one", "two", "three"],
            "access": {"mode": "planner", "agent_id": None, "privileged": True},
        }
        validator = Draft202012Validator(self.seal_receipt_schema)
        validator.validate(receipt)
        receipt["seal"]["status"] = "revealed"
        with self.assertRaises(ValidationError):
            validator.validate(receipt)

    @unittest.skipUnless(
        Draft202012Validator is not None,
        "jsonschema test extra is not installed",
    )
    def test_replacement_schema_accepts_generated_ids_and_rejects_bad_digest(self) -> None:
        assert Draft202012Validator is not None
        document = {
            "schema": "lacuna.change-set.v1",
            "change_id": "chg_repair_schema",
            "actor_id": "user",
            "expected_head": "0" * 64,
            "message": "Exercise the consequence replacement exchange contract.",
            "operations": [
                {
                    "op": "replace_consequence",
                    "replaces_consequence_id": "csq_old",
                    "premise_assignment_id": "asn_new",
                    "dependent_kind": "question",
                    "dependent_id": "qst_open",
                    "relation": "motivates",
                    "severity": "material",
                    "source_id": None,
                    "rationale": "The revised premise now motivates the open question.",
                    "expected_repair_sha256": "a" * 64,
                    "reason": "Replace obsolete consequence custody.",
                }
            ],
        }
        validator = Draft202012Validator(self.change_schema)
        validator.validate(document)

        document["operations"][0]["expected_repair_sha256"] = "not-a-digest"
        with self.assertRaises(ValidationError):
            validator.validate(document)


if __name__ == "__main__":
    unittest.main()
