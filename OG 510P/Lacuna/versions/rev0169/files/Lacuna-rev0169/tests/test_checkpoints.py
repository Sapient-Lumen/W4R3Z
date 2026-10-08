from __future__ import annotations

import os
import unittest

import copy
import json
import tempfile
from pathlib import Path

from tests._schema_support import Draft202012Validator

import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from lacuna.checkpoints import (
    CHECKPOINT_CHECKS,
    CHECKPOINT_ROLES,
    CHECKPOINT_SCORE_DIMENSIONS,
    assemble_checkpoint_proposal,
    build_checkpoint_dispatch,
    build_checkpoint_request,
    build_checkpoint_task_card,
    checkpoint_candidates_sha256,
    checkpoint_compression_sha256,
    checkpoint_judgment_sha256,
    checkpoint_proposal_sha256,
    checkpoint_request_sha256,
    commit_checkpoint,
    review_checkpoint,
    validate_checkpoint_candidates,
    validate_checkpoint_compression,
    validate_checkpoint_dispatch,
    validate_checkpoint_judgment,
    validate_checkpoint_proposal,
    validate_checkpoint_review,
    validate_checkpoint_task_card,
    validate_checkpoint_verifier,
)
from lacuna.errors import LacunaError
from lacuna.providers import PROVIDERS, provider_alias
from lacuna.store import Cube
from lacuna.util import canonical_json, sha256_text


@unittest.skipUnless(
    os.environ.get("LACUNA_HEAVY_TESTS") == "1",
    "set LACUNA_HEAVY_TESTS=1 to run retcon checkpoint digest/schema tests",
)
class RetconCheckpointTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name) / "cube"
        self.cube = Cube.init(self.root, owner_id="user", owner_label="User")
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
            message="checkpoint participants and one protected unknown",
        )

    def tearDown(self) -> None:
        self.cube.close()
        self.temporary.cleanup()

    def request(self, **overrides: object) -> dict:
        options = {
            "audience_id": "player",
            "actor_id": "narrator",
            "trigger": "The causal structure is thin; compare bounded latent explanations.",
            "candidate_count": 2,
            "rollout_horizon_turns": 3,
            "compression_max_chars": 1000,
            "max_operations": 4,
        }
        options.update(overrides)
        return build_checkpoint_request(self.cube, **options)  # type: ignore[arg-type]

    def candidates(self, request: dict) -> dict:
        card = build_checkpoint_task_card(request, role="lacuna-retcon-generator")
        result = copy.deepcopy(card["output_contract"]["template"])
        template = result["candidates"][0]
        result["candidates"] = []
        for ordinal, title in ((1, "Custodian bargain"), (2, "Storm interlock")):
            item = copy.deepcopy(template)
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
                        "provider": "test",
                        "model": f"fixture-{ordinal}",
                        "model_version": None,
                        "invocation_id": None,
                        "notes": None,
                    },
                }
            )
            item["rollout"]["turns"] = [
                f"Turn {turn_number}: preserve agency while testing {title}."
                for turn_number in range(1, request["policy"]["rollout_horizon_turns"] + 1)
            ]
            item["rollout"]["summary"] = "A bounded rollout that preserves player agency."
            result["candidates"].append(item)
        return validate_checkpoint_candidates(result, request)

    def judgment(self, request: dict, candidates: dict, *, tie: bool = False) -> dict:
        card = build_checkpoint_task_card(
            request,
            role="lacuna-retcon-judge",
            candidates_value=candidates,
        )
        result = copy.deepcopy(card["output_contract"]["template"])
        result["assessor"] = {
            "provider": "test",
            "model": "fixture-judge",
            "model_version": None,
            "invocation_id": None,
            "notes": None,
        }
        result["scores"] = []
        weights = request["policy"]["score_weights"]
        for ordinal, value in ((1, 90), (2, 90 if tie else 80)):
            dimensions = {dimension: value for dimension in CHECKPOINT_SCORE_DIMENSIONS}
            result["scores"].append(
                {
                    "candidate_id": f"candidate.{ordinal}",
                    "eligible": True,
                    "disqualifiers": [],
                    "dimensions": dimensions,
                    "weighted_score": sum(
                        dimensions[dimension] * weights[dimension]
                        for dimension in CHECKPOINT_SCORE_DIMENSIONS
                    ),
                    "rationale": "The hypothesis preserves canon and leaves meaningful choices.",
                }
            )
        result["selected_candidate_id"] = "candidate.1"
        result["selection_rationale"] = "Highest weighted eligible score; ties use lexical ID order."
        return validate_checkpoint_judgment(result, request, candidates)

    def compression(self, request: dict, candidates: dict, judgment: dict) -> dict:
        card = build_checkpoint_task_card(
            request,
            role="lacuna-retcon-compressor",
            candidates_value=candidates,
            judgment_value=judgment,
        )
        result = copy.deepcopy(card["output_contract"]["template"])
        result["state_card"] = (
            "The custodian made a contingent bargain. Preserve the locked-door question; "
            "press the player with a reversible choice rather than a reveal."
        )
        result["narration"] = (
            "Rain threads down the greenhouse glass. The custodian waits beside the locked door."
        )
        return validate_checkpoint_compression(result, request, candidates, judgment)

    def workflow(self) -> tuple[dict, dict, dict, dict, dict, dict]:
        request = self.request()
        candidates = self.candidates(request)
        judgment = self.judgment(request, candidates)
        compression = self.compression(request, candidates, judgment)
        proposal = assemble_checkpoint_proposal(request, candidates, judgment, compression)
        verifier_card = build_checkpoint_task_card(
            request,
            role="lacuna-retcon-verifier",
            proposal_value=proposal,
        )
        verifier = copy.deepcopy(verifier_card["output_contract"]["template"])
        verifier["status"] = "pass"
        verifier["checks"] = {check: True for check in CHECKPOINT_CHECKS}
        verifier["findings"] = []
        verifier["recommended_action"] = "commit"
        verifier = validate_checkpoint_verifier(verifier, request, proposal)
        return request, candidates, judgment, compression, proposal, verifier

    def test_end_to_end_review_commit_and_exact_retry_recovery(self) -> None:
        request, candidates, judgment, _compression, proposal, verifier = self.workflow()
        before_review = self.cube.event_count()
        review = review_checkpoint(
            self.cube,
            request,
            candidates,
            judgment,
            proposal,
            verifier,
        )
        self.assertEqual(review["mechanical_status"], "pass")
        self.assertEqual(self.cube.event_count(), before_review)

        receipt = commit_checkpoint(
            self.cube,
            request,
            candidates,
            judgment,
            proposal,
            verifier,
            review,
        )
        after_commit = self.cube.event_count()
        self.assertEqual(receipt["overall_status"], "accepted")
        self.assertEqual(receipt["turn_receipt"]["overall_status"], "pass")
        self.assertEqual(after_commit - before_review, 2)
        self.assertEqual(receipt["narration"], proposal["turn_proposal"]["narration"])

        recovered = commit_checkpoint(
            self.cube,
            request,
            candidates,
            judgment,
            proposal,
            verifier,
            review,
        )
        self.assertEqual(self.cube.event_count(), after_commit)
        self.assertEqual(recovered["turn_receipt"]["delivery"]["mode"], "recovered")
        self.assertFalse(recovered["turn_receipt"]["delivery"]["historical_snapshot_used"])
        self.assertEqual(self.cube.verify()["overall_status"], "pass")

    def test_retry_after_later_head_recovers_historical_receipt_without_duplicate_events(self) -> None:
        request, candidates, judgment, _compression, proposal, verifier = self.workflow()
        review = review_checkpoint(
            self.cube,
            request,
            candidates,
            judgment,
            proposal,
            verifier,
        )
        committed = commit_checkpoint(
            self.cube,
            request,
            candidates,
            judgment,
            proposal,
            verifier,
            review,
        )
        self.assertEqual(committed["turn_receipt"]["delivery"]["mode"], "direct")

        self.cube.apply_operations(
            actor_id="user",
            operations=[
                {
                    "op": "add_source",
                    "source_id": "src_after_checkpoint",
                    "kind": "other",
                    "label": "Later unrelated source",
                    "locator": None,
                    "content_sha256": None,
                    "metadata": {},
                }
            ],
            message="advance beyond the checkpoint commit",
        )
        after_later_change = self.cube.event_count()

        recovered = commit_checkpoint(
            self.cube,
            request,
            candidates,
            judgment,
            proposal,
            verifier,
            review,
        )
        self.assertEqual(self.cube.event_count(), after_later_change)
        self.assertEqual(recovered["turn_receipt"]["delivery"]["mode"], "recovered")
        self.assertTrue(recovered["turn_receipt"]["delivery"]["historical_snapshot_used"])
        self.assertEqual(self.cube.verify()["overall_status"], "pass")

    def test_checkpoint_request_is_v4_source_bound_and_least_authority(self) -> None:
        request = self.request()
        packet = request["turn_packet"]
        grant = packet["write_grant"]
        self.assertEqual(packet["schema"], "lacuna.turn-request.v4")
        self.assertEqual(packet["request_purpose"], "checkpoint")
        self.assertEqual(packet["input_kind"], "session-control")
        self.assertEqual(grant["schema"], "lacuna.turn-grant.v2")
        self.assertEqual(grant["profile"], "checkpoint")
        self.assertEqual(grant["max_reveals"], 0)
        self.assertEqual(grant["world_scope"], None)
        for forbidden in (
            "record_assertion",
            "close_question",
            "update_particle_bank",
            "reconcile_particle_bank",
            "set_world_weight",
            "set_world_status",
            "raise_commitment",
            "reveal_precommitment",
        ):
            self.assertNotIn(forbidden, grant["allowed_operations"])
        self.assertEqual(request["protected_state"]["unknown_ids"], ["question:qst_locked_door"])
        self.assertEqual(len(checkpoint_request_sha256(request)), 64)

    def test_generator_must_preserve_exact_unknown_set_and_candidate_count(self) -> None:
        request = self.request()
        candidates = self.candidates(request)
        missing_unknown = copy.deepcopy(candidates)
        missing_unknown["candidates"][0]["preserved_unknown_ids"] = []
        with self.assertRaises(LacunaError) as caught:
            validate_checkpoint_candidates(missing_unknown, request)
        self.assertEqual(caught.exception.code, "bad-checkpoint-candidates")

        short = copy.deepcopy(candidates)
        short["candidates"].pop()
        with self.assertRaises(LacunaError):
            validate_checkpoint_candidates(short, request)

        missing_beat = copy.deepcopy(candidates)
        missing_beat["candidates"][0]["rollout"]["turns"].pop()
        with self.assertRaises(LacunaError) as caught:
            validate_checkpoint_candidates(missing_beat, request)
        self.assertEqual(caught.exception.code, "bad-checkpoint-candidates")
        self.assertIn("exactly one ordered beat", caught.exception.message)

        summary_only = copy.deepcopy(candidates)
        summary_only["candidates"][0]["rollout"].pop("turns")
        with self.assertRaises(LacunaError):
            validate_checkpoint_candidates(summary_only, request)

    def test_generator_supports_policy_sized_exact_rollouts(self) -> None:
        request = self.request(candidate_count=4, rollout_horizon_turns=7)
        card = build_checkpoint_task_card(request, role="lacuna-retcon-generator")
        template_candidates = card["output_contract"]["template"]["candidates"]
        self.assertEqual(len(template_candidates), 4)
        self.assertEqual(
            [item["candidate_id"] for item in template_candidates],
            ["candidate.1", "candidate.2", "candidate.3", "candidate.4"],
        )
        self.assertTrue(all(len(item["rollout"]["turns"]) == 7 for item in template_candidates))

        result = copy.deepcopy(card["output_contract"]["template"])
        for ordinal, item in enumerate(result["candidates"], start=1):
            item["provenance"]["provider"] = "test"
            item["provenance"]["model"] = f"fixture-{ordinal}"
        candidates = validate_checkpoint_candidates(result, request)
        self.assertTrue(
            all(len(candidate["rollout"]["turns"]) == 7 for candidate in candidates["candidates"])
        )

        judge = build_checkpoint_task_card(
            request,
            role="lacuna-retcon-judge",
            candidates_value=candidates,
        )
        self.assertEqual(
            [item["candidate_id"] for item in judge["output_contract"]["template"]["scores"]],
            ["candidate.1", "candidate.2", "candidate.3", "candidate.4"],
        )

    def test_judge_receives_blind_candidate_view_and_deterministic_ties(self) -> None:
        request = self.request()
        candidates = self.candidates(request)
        card = build_checkpoint_task_card(
            request,
            role="lacuna-retcon-judge",
            candidates_value=candidates,
        )
        rendered = json.dumps(card["input_payload"]["candidate_view"], sort_keys=True)
        self.assertNotIn("provenance", rendered)
        self.assertNotIn("fixture-1", rendered)
        self.assertNotIn("generation_notes", rendered)
        self.assertTrue(card["input_payload"]["blinding"]["provenance_removed"])

        judgment = self.judgment(request, candidates, tie=True)
        self.assertEqual(judgment["selected_candidate_id"], "candidate.1")
        forged = copy.deepcopy(judgment)
        forged["selected_candidate_id"] = "candidate.2"
        with self.assertRaises(LacunaError) as caught:
            validate_checkpoint_judgment(forged, request, candidates)
        self.assertIn("deterministic rule", caught.exception.message)

        bad_score = copy.deepcopy(judgment)
        bad_score["scores"][0]["weighted_score"] -= 1
        with self.assertRaises(LacunaError):
            validate_checkpoint_judgment(bad_score, request, candidates)

    def test_compressor_cannot_use_director_only_or_commitment_hardening_operations(self) -> None:
        request = self.request()
        candidates = self.candidates(request)
        judgment = self.judgment(request, candidates)
        compression = self.compression(request, candidates, judgment)

        for operation in (
            {"op": "close_question", "question_id": "qst_locked_door", "resolution_assertion_id": None, "reason": "No."},
            {"op": "update_particle_bank"},
            {"op": "add_source"},
        ):
            forged = copy.deepcopy(compression)
            forged["operations"] = [operation]
            with self.assertRaises(LacunaError):
                validate_checkpoint_compression(forged, request, candidates, judgment)

        hard = copy.deepcopy(compression)
        hard["operations"] = [
            {
                "op": "assign_world",
                "assignment_id": "asn_hard",
                "world_id": "wld_hidden",
                "claim_id": "clm_hidden",
                "truth": "true",
                "commitment": "hard",
            }
        ]
        with self.assertRaises(LacunaError) as caught:
            validate_checkpoint_compression(hard, request, candidates, judgment)
        self.assertIn("cannot harden", caught.exception.message)

    def test_compression_budget_and_unknown_preservation_fail_closed(self) -> None:
        request = self.request(compression_max_chars=256)
        candidates = self.candidates(request)
        judgment = self.judgment(request, candidates)
        compression = self.compression(request, candidates, judgment)
        over = copy.deepcopy(compression)
        over["state_card"] = "x" * 257
        with self.assertRaises(LacunaError) as caught:
            validate_checkpoint_compression(over, request, candidates, judgment)
        self.assertIn("compression budget", caught.exception.message)

        erased = copy.deepcopy(compression)
        erased["preserved_unknown_ids"] = []
        with self.assertRaises(LacunaError):
            validate_checkpoint_compression(erased, request, candidates, judgment)

    def test_assembled_proposal_retains_exact_compressor_artifact_and_custody_source(self) -> None:
        request, candidates, judgment, compression, proposal, _verifier = self.workflow()
        self.assertEqual(proposal["compression_artifact"], compression)
        self.assertEqual(
            proposal["compression_sha256"],
            checkpoint_compression_sha256(compression, request, candidates, judgment),
        )
        first = proposal["turn_proposal"]["operations"][0]
        self.assertEqual(first["op"], "add_source")
        self.assertEqual(first["as"], "checkpoint_selection")
        self.assertEqual(first["content_sha256"], proposal["selection_evidence_sha256"])
        selected = next(
            item
            for item in candidates["candidates"]
            if item["candidate_id"] == judgment["selected_candidate_id"]
        )
        selected_sha = sha256_text(canonical_json(selected))
        self.assertEqual(
            proposal["selection_evidence"]["selected_candidate_sha256"],
            selected_sha,
        )
        self.assertEqual(
            first["metadata"]["selected_candidate_sha256"],
            selected_sha,
        )

        forged = copy.deepcopy(proposal)
        forged["compression_artifact"]["nonclaims"].append("silent drift")
        with self.assertRaises(LacunaError):
            validate_checkpoint_proposal(
                forged,
                request_value=request,
                candidates_value=candidates,
                judgment_value=judgment,
            )

        source_tamper = copy.deepcopy(proposal)
        source_tamper["turn_proposal"]["operations"][0]["content_sha256"] = "0" * 64
        with self.assertRaises(LacunaError):
            validate_checkpoint_proposal(
                source_tamper,
                request_value=request,
                candidates_value=candidates,
                judgment_value=judgment,
            )

    def test_verifier_is_advisory_and_fail_closed(self) -> None:
        request, candidates, judgment, _compression, proposal, verifier = self.workflow()
        card = build_checkpoint_task_card(
            request,
            role="lacuna-retcon-verifier",
            proposal_value=proposal,
        )
        refusal = copy.deepcopy(card["output_contract"]["template"])
        validated = validate_checkpoint_verifier(refusal, request, proposal)
        self.assertEqual(validated["status"], "refuse")

        fake_pass = copy.deepcopy(refusal)
        fake_pass["status"] = "pass"
        fake_pass["recommended_action"] = "commit"
        with self.assertRaises(LacunaError):
            validate_checkpoint_verifier(fake_pass, request, proposal)

        review = review_checkpoint(
            self.cube,
            request,
            candidates,
            judgment,
            proposal,
            verifier,
        )
        with self.assertRaises(LacunaError) as caught:
            validate_checkpoint_review(
                review,
                request,
                candidates,
                judgment,
                proposal,
                validated,
            )
        self.assertEqual(caught.exception.code, "checkpoint-verifier-refused")

    def test_stale_cube_refuses_review_without_committing_checkpoint(self) -> None:
        request, candidates, judgment, _compression, proposal, verifier = self.workflow()
        before = self.cube.event_count()
        self.cube.apply_operations(
            actor_id="user",
            operations=[
                {
                    "op": "add_source",
                    "source_id": "src_intervening",
                    "kind": "other",
                    "label": "Intervening source",
                    "locator": None,
                    "content_sha256": None,
                    "metadata": {},
                }
            ],
            message="advance head",
        )
        with self.assertRaises(LacunaError) as caught:
            review_checkpoint(self.cube, request, candidates, judgment, proposal, verifier)
        self.assertEqual(caught.exception.code, "stale-head")
        self.assertEqual(self.cube.event_count(), before + 1)
        self.assertIsNone(self.cube.committed_change(proposal["turn_proposal"]["proposal_id"]))

    def test_every_provider_has_all_checkpoint_roles_and_dispatch_is_card_exact(self) -> None:
        request = self.request()
        card = build_checkpoint_task_card(request, role="lacuna-retcon-generator")
        for provider in PROVIDERS:
            for role in CHECKPOINT_ROLES:
                self.assertTrue(provider_alias(role, provider))
            dispatch = build_checkpoint_dispatch(card, provider=provider)
            self.assertEqual(dispatch["input_card"], card)
            self.assertEqual(dispatch["agent_name"], provider_alias(card["role"], provider))
            self.assertEqual(dispatch["return_contract"]["schema"], "lacuna.checkpoint-candidates.v1")
            self.assertEqual(validate_checkpoint_dispatch(dispatch), dispatch)

        tampered_alias = build_checkpoint_dispatch(card, provider="chatgpt")
        tampered_alias["agent_name"] = "unregistered-context"
        with self.assertRaises(LacunaError) as caught:
            validate_checkpoint_dispatch(tampered_alias)
        self.assertEqual(caught.exception.code, "bad-checkpoint-dispatch")

        tampered_card = build_checkpoint_dispatch(card, provider="codex")
        tampered_card["input_card"]["objective"] += " Hidden extra authority."
        with self.assertRaises(LacunaError):
            validate_checkpoint_dispatch(tampered_card)

    def test_task_card_validator_recomputes_identity_and_role_contract(self) -> None:
        request = self.request()
        card = build_checkpoint_task_card(request, role="lacuna-retcon-generator")

        forged_task = copy.deepcopy(card)
        forged_task["task_id"] = "ctk_000000000000000000000000"
        forged_task["output_contract"]["template"]["task_id"] = forged_task["task_id"]
        with self.assertRaises(LacunaError) as caught:
            validate_checkpoint_task_card(forged_task)
        self.assertIn("deterministic digest-bound identity", caught.exception.message)

        forged_upstream = copy.deepcopy(card)
        forged_upstream["upstream"] = [
            {
                "kind": "checkpoint-candidates",
                "schema": "lacuna.checkpoint-candidates.v1",
                "sha256": "0" * 64,
            }
        ]
        with self.assertRaises(LacunaError) as caught:
            validate_checkpoint_task_card(forged_upstream)
        self.assertIn("role contract", caught.exception.message)

        forged_contract = copy.deepcopy(card)
        forged_contract["output_contract"]["schema"] = "lacuna.checkpoint-judgment.v1"
        forged_contract["output_contract"]["template"]["schema"] = "lacuna.checkpoint-judgment.v1"
        with self.assertRaises(LacunaError) as caught:
            validate_checkpoint_task_card(forged_contract)
        self.assertIn("output_contract.schema", caught.exception.message)

    @unittest.skipUnless(Draft202012Validator is not None, "jsonschema test extra is not installed")
    def test_exchange_schemas_accept_complete_workflow_artifacts(self) -> None:
        assert Draft202012Validator is not None
        request, candidates, judgment, compression, proposal, verifier = self.workflow()
        review = review_checkpoint(self.cube, request, candidates, judgment, proposal, verifier)
        receipt = commit_checkpoint(
            self.cube,
            request,
            candidates,
            judgment,
            proposal,
            verifier,
            review,
        )
        generator_card = build_checkpoint_task_card(request, role="lacuna-retcon-generator")
        dispatch = build_checkpoint_dispatch(generator_card, provider="chatgpt")
        artifacts = {
            "turn-request.v4.schema.json": request["turn_packet"],
            "checkpoint-request.v1.schema.json": request,
            "checkpoint-task-card.v1.schema.json": generator_card,
            "checkpoint-candidates.v1.schema.json": candidates,
            "checkpoint-judgment.v1.schema.json": judgment,
            "checkpoint-compression.v1.schema.json": compression,
            "checkpoint-proposal.v1.schema.json": proposal,
            "checkpoint-verifier-return.v1.schema.json": verifier,
            "checkpoint-review.v1.schema.json": review,
            "checkpoint-commit-receipt.v1.schema.json": receipt,
            "checkpoint-agent-dispatch.v1.schema.json": dispatch,
            "turn-preparation.v1.schema.json": review["turn_preparation"],
            "turn-receipt.v3.schema.json": receipt["turn_receipt"],
        }
        for filename, artifact in artifacts.items():
            schema = json.loads((ROOT / "schemas" / filename).read_text(encoding="utf-8"))
            with self.subTest(schema=filename):
                Draft202012Validator(schema).validate(artifact)

    def test_digest_chain_changes_when_each_upstream_artifact_changes(self) -> None:
        request, candidates, judgment, compression, proposal, _verifier = self.workflow()
        self.assertEqual(len(checkpoint_candidates_sha256(candidates, request)), 64)
        self.assertEqual(len(checkpoint_judgment_sha256(judgment, request, candidates)), 64)
        self.assertEqual(len(checkpoint_proposal_sha256(proposal, request_value=request)), 64)

        changed = copy.deepcopy(candidates)
        changed["candidates"][0]["title"] = "Changed title"
        changed = validate_checkpoint_candidates(changed, request)
        self.assertNotEqual(
            checkpoint_candidates_sha256(changed, request),
            checkpoint_candidates_sha256(candidates, request),
        )
        # The old judgment is bound to the prior candidate digest and cannot be replayed.
        with self.assertRaises(LacunaError):
            validate_checkpoint_judgment(judgment, request, changed)
        self.assertEqual(proposal["compression_artifact"], compression)


if __name__ == "__main__":
    unittest.main()
