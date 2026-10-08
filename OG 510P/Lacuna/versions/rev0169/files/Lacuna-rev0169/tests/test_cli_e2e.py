from __future__ import annotations

import os
import unittest

import json
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LACUNA = ROOT / "lacuna"


@unittest.skipUnless(
    os.environ.get("LACUNA_E2E_TESTS") == "1",
    "set LACUNA_E2E_TESTS=1 to run launcher subprocess end-to-end tests",
)
class CliEndToEndTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.library = Path(self.temporary.name) / "library"

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def run_lacuna(self, *arguments: str, expected: int = 0) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(
            [str(LACUNA), *arguments],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
            timeout=30,
        )
        self.assertEqual(
            result.returncode,
            expected,
            msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}",
        )
        return result

    def create_campaign(self) -> dict:
        result = self.run_lacuna(
            "campaign",
            "create",
            str(self.library),
            "glass-house",
            "--title",
            "The Glass House",
        )
        return json.loads(result.stdout)

    def test_launcher_ignores_ambient_sitecustomize(self) -> None:
        trap = Path(self.temporary.name) / "ambient-site"
        trap.mkdir()
        marker = Path(self.temporary.name) / "sitecustomize-ran"
        (trap / "sitecustomize.py").write_text(
            f"from pathlib import Path\nPath({str(marker)!r}).write_text('ran')\n",
            encoding="utf-8",
        )
        environment = os.environ.copy()
        environment["PYTHONPATH"] = str(trap)
        result = subprocess.run(
            [str(LACUNA), "--help"],
            cwd=ROOT,
            env=environment,
            text=True,
            capture_output=True,
            check=False,
            timeout=30,
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertFalse(marker.exists())

    def test_launcher_reports_package_version_without_subcommand(self) -> None:
        result = self.run_lacuna("--version")
        self.assertEqual(result.stdout.strip(), "lacuna 0.169.0")

    def test_checkpoint_run_help_exposes_fresh_narrator_continuation(self) -> None:
        result = self.run_lacuna("checkpoint", "run", "--help")
        self.assertIn("narrator-capsule", result.stdout)
        self.assertIn("information bottleneck", result.stdout)
        self.assertIn("next-turn", result.stdout)
        self.assertIn("continuation", result.stdout)
        self.assertIn("narrator handoff", result.stdout)

    def test_library_to_turn_round_trip_through_executable(self) -> None:
        created = self.create_campaign()
        self.assertTrue(created["campaign"]["selected"])
        listing = self.run_lacuna("campaign", "list", str(self.library)).stdout
        self.assertIn("glass-house", listing)
        status = json.loads(self.run_lacuna("status", str(self.library)).stdout)
        self.assertEqual(status["agent_count"], 4)

        packet = json.loads(
            self.run_lacuna(
                "turn",
                "packet",
                str(self.library),
                "--player-input",
                "I study the rain on the windows.",
            ).stdout
        )
        template = packet["response_contract"]["proposal_template"]
        proposal = dict(template)
        proposal["narration"] = "Rain threads silver paths down the glass."
        proposal["operations"] = []
        proposal["revealed_assertion_ids"] = []
        proposal_path = Path(self.temporary.name) / "proposal.json"
        proposal_path.write_text(json.dumps(proposal), encoding="utf-8")
        receipt = json.loads(
            self.run_lacuna(
                "turn",
                "commit",
                str(self.library),
                str(proposal_path),
            ).stdout
        )
        self.assertEqual(receipt["narration"], proposal["narration"])
        self.assertEqual(receipt["head"], receipt["change"]["after_head"])
        verification = json.loads(self.run_lacuna("verify", str(self.library)).stdout)
        self.assertEqual(verification["overall_status"], "pass")

    def test_cli_exact_input_file_and_request_scoped_run_round_trip(self) -> None:
        self.create_campaign()
        exact_input = "I whisper '$HOME' and `wait`.\r\nKeep this exact second line."
        input_path = Path(self.temporary.name) / "player-input.txt"
        input_path.write_bytes(exact_input.encode("utf-8"))

        packet = json.loads(
            self.run_lacuna(
                "turn",
                "packet",
                str(self.library),
                "--player-input-file",
                str(input_path),
            ).stdout
        )
        self.assertEqual(packet["player_input"], exact_input)

        run_root = Path(self.temporary.name) / "turn-runs"
        manifest = json.loads(
            self.run_lacuna(
                "turn",
                "run",
                "begin",
                str(self.library),
                "--root",
                str(run_root),
                "--player-input-file",
                str(input_path),
                "--mode",
                "solo",
            ).stdout
        )
        self.assertEqual(manifest["status"], "awaiting-solo-proposal")
        self.assertEqual(manifest["selected_mode"], "solo")
        run_path = Path(manifest["run_path"])
        with (run_path / "00-player-input.txt").open(
            "r", encoding="utf-8", newline=""
        ) as handle:
            self.assertEqual(handle.read(), exact_input)
        status = json.loads(
            self.run_lacuna("turn", "run", "status", str(run_path)).stdout
        )
        self.assertEqual(status["next_action"]["expected_schema"], "lacuna.turn-proposal.v2")
        self.assertTrue((run_path / "NEXT.md").is_file())


    def test_cli_comparative_scenario_template_begin_status_and_dispatch(self) -> None:
        self.create_campaign()
        capsule = json.loads(
            self.run_lacuna("scenario", "template", str(self.library)).stdout
        )
        capsule["script"][0]["player_input"] = (
            "I leave the greenhouse path and ring the cracked silver bell."
        )
        capsule["script"][1]["player_input"] = (
            "I ask the custodian why the bell answered from underground."
        )
        capsule["model_policy"].update(
            {
                "model_family": "fixture-family",
                "model": "fixture-model",
                "model_version": "fixture-v1",
                "sampling_policy": "One fixed fixture policy for all cells.",
                "sampling_seed": "fixture-seed",
            }
        )
        capsule_path = Path(self.temporary.name) / "scenario-capsule.json"
        capsule_path.write_text(json.dumps(capsule), encoding="utf-8")
        run_root = Path(self.temporary.name) / "scenario-runs"
        manifest = json.loads(
            self.run_lacuna(
                "scenario",
                "begin",
                str(self.library),
                str(capsule_path),
                "--root",
                str(run_root),
                "--format",
                "json",
            ).stdout
        )
        run_path = Path(manifest["run_path"])
        self.assertEqual(manifest["status"], "collecting-results")
        self.assertTrue((run_path / "20-PRIVATE-assignment.json").is_file())
        status = json.loads(
            self.run_lacuna(
                "scenario", "status", str(run_path), "--format", "json"
            ).stdout
        )
        self.assertEqual(status["next_action"]["owner"], "experiment-owner")
        driver = json.loads(
            self.run_lacuna(
                "scenario", "dispatch", str(run_path), "--format", "json"
            ).stdout
        )
        self.assertEqual(driver["schema"], "lacuna.scenario-cell-driver.v2")
        self.assertEqual(driver["cell_label"], manifest["cells"][0]["label"])
        self.assertEqual(
            json.loads((run_path / "run.json").read_text(encoding="utf-8"))["cells"][0]["status"],
            "active",
        )

    def test_cli_scenario_bundle_preregistration_commitment_and_witness_gate(self) -> None:
        self.create_campaign()
        capsule = json.loads(
            self.run_lacuna("scenario", "template", str(self.library)).stdout
        )
        capsule["script"][0]["player_input"] = (
            "I leave the greenhouse path and ring the cracked silver bell."
        )
        capsule["script"][1]["player_input"] = (
            "I ask the custodian why the bell answered from underground."
        )
        capsule["model_policy"].update(
            {
                "model_family": "fixture-family",
                "model": "fixture-model",
                "model_version": "fixture-v1",
                "sampling_policy": "One fixed fixture policy for every planned block.",
                "sampling_seed": "fixture-seed",
            }
        )
        capsule_path = Path(self.temporary.name) / "bundle-capsule.json"
        capsule_path.write_text(json.dumps(capsule), encoding="utf-8")
        plan = json.loads(
            self.run_lacuna(
                "scenario",
                "bundle",
                "template",
                "--block",
                str(self.library),
                str(capsule_path),
                "--block",
                str(self.library),
                str(capsule_path),
                "--minimum-witnesses",
                "1",
            ).stdout
        )
        self.assertEqual(plan["schema"], "lacuna.scenario-bundle-plan.v1")
        self.assertEqual(len(plan["blocks"]), 2)
        plan_path = Path(self.temporary.name) / "bundle-plan.json"
        plan_path.write_text(json.dumps(plan), encoding="utf-8")
        root = Path(self.temporary.name) / "scenario-bundles"
        manifest = json.loads(
            self.run_lacuna(
                "scenario",
                "bundle",
                "begin",
                str(plan_path),
                "--root",
                str(root),
                "--format",
                "json",
            ).stdout
        )
        bundle_path = Path(manifest["bundle_path"])
        self.assertEqual(manifest["status"], "awaiting-witnesses")
        self.assertEqual(
            [block["status"] for block in manifest["blocks"]],
            ["active", "pending"],
        )
        commitment = json.loads(
            self.run_lacuna(
                "scenario", "bundle", "commitment", str(bundle_path)
            ).stdout
        )
        public_text = json.dumps(commitment, sort_keys=True)
        for condition in (
            "forward-only",
            "prompt-only-retcon",
            "lacuna-serial",
            "lacuna-role-separated",
        ):
            self.assertNotIn(condition, public_text)
        witness = json.loads(
            self.run_lacuna(
                "scenario",
                "bundle",
                "witness-template",
                str(bundle_path),
                "--witness-id",
                "witness.fixture",
            ).stdout
        )
        self.assertEqual(witness["commitment_sha256"], manifest["commitment"]["sha256"])
        status = json.loads(
            self.run_lacuna(
                "scenario", "bundle", "status", str(bundle_path), "--format", "json"
            ).stdout
        )
        self.assertEqual(status["next_action"]["expected_schema"], "lacuna.scenario-bundle-witness.v1")

    def test_cli_managed_checkpoint_run_routes_dispatch_and_failure_receipt(self) -> None:
        self.create_campaign()
        run_root = Path(self.temporary.name) / "managed-checkpoints"
        manifest = json.loads(
            self.run_lacuna(
                "checkpoint",
                "run",
                "begin",
                str(self.library),
                "--root",
                str(run_root),
                "--trigger",
                "Compare bounded futures before committing hidden state.",
                "--candidate-count",
                "2",
                "--rollout-horizon-turns",
                "2",
                "--compression-max-chars",
                "1000",
                "--max-operations",
                "2",
                "--provider",
                "portable",
                "--generator-provider",
                "chatgpt",
                "--judge-provider",
                "codex",
                "--compressor-provider",
                "claude-code",
                "--verifier-provider",
                "gemini-cli",
                "--format",
                "json",
            ).stdout
        )
        run_path = Path(manifest["run_path"])
        self.assertEqual(manifest["status"], "awaiting-generator")
        self.assertEqual(
            manifest["provider_routes"]["lacuna-retcon-generator"],
            "chatgpt",
        )
        dispatch = json.loads(
            self.run_lacuna(
                "checkpoint",
                "run",
                "dispatch",
                str(run_path),
                "--format",
                "json",
            ).stdout
        )
        self.assertEqual(dispatch["provider"], "chatgpt")
        self.assertEqual(dispatch["role"], "lacuna-retcon-generator")
        self.assertEqual(dispatch["input_card"]["checkpoint_id"], manifest["checkpoint_identity"]["checkpoint_id"])

        failed = json.loads(
            self.run_lacuna(
                "checkpoint",
                "run",
                "record-failure",
                str(run_path),
                "--failure-class",
                "timeout",
                "--failure-message",
                "No valid JSON was returned.",
                "--model",
                "host-declared-fixture",
            ).stdout
        )
        self.assertEqual(failed["status"], "awaiting-generator")
        self.assertEqual(len(failed["invocations"]), 1)
        invocation = json.loads(
            (run_path / failed["invocations"][0]["path"]).read_text(encoding="utf-8")
        )
        self.assertEqual(invocation["outcome"], "failed")
        self.assertEqual(invocation["failure_class"], "timeout")

    def test_cli_source_bound_checkpoint_round_trip(self) -> None:
        self.create_campaign()
        artifact_root = Path(self.temporary.name) / "checkpoint"
        artifact_root.mkdir()

        def write(name: str, value: object) -> Path:
            path = artifact_root / name
            path.write_text(json.dumps(value), encoding="utf-8")
            return path

        request = json.loads(
            self.run_lacuna(
                "checkpoint",
                "begin",
                str(self.library),
                "--trigger",
                "Compare two bounded explanations before the next reveal.",
                "--candidate-count",
                "2",
                "--rollout-horizon-turns",
                "2",
                "--compression-max-chars",
                "1000",
                "--max-operations",
                "2",
            ).stdout
        )
        request_path = write("request.json", request)

        generator = json.loads(
            self.run_lacuna(
                "checkpoint",
                "card",
                str(request_path),
                "--role",
                "lacuna-retcon-generator",
            ).stdout
        )
        candidates = generator["output_contract"]["template"]
        prototype = candidates["candidates"][0]
        candidates["candidates"] = []
        for ordinal in (1, 2):
            item = json.loads(json.dumps(prototype))
            item["candidate_id"] = f"candidate.{ordinal}"
            item["title"] = f"Bounded explanation {ordinal}"
            item["hypothesis_card"] = f"Tentative hidden state {ordinal}."
            item["story_so_far_explanation"] = "Explains observations without changing them."
            item["future_arc_summary"] = "Produces reversible pressure and preserves agency."
            item["rollout"]["summary"] = "Two-turn bounded rollout."
            item["provenance"]["provider"] = "test"
            item["provenance"]["model"] = f"fixture-{ordinal}"
            candidates["candidates"].append(item)
        candidates_path = write("candidates.json", candidates)

        judge = json.loads(
            self.run_lacuna(
                "checkpoint",
                "card",
                str(request_path),
                "--role",
                "lacuna-retcon-judge",
                "--candidates",
                str(candidates_path),
            ).stdout
        )
        judgment = judge["output_contract"]["template"]
        score = judgment["scores"][0]
        judgment["scores"] = []
        for ordinal, value in ((1, 90), (2, 80)):
            item = json.loads(json.dumps(score))
            item["candidate_id"] = f"candidate.{ordinal}"
            item["eligible"] = True
            item["disqualifiers"] = []
            item["dimensions"] = {key: value for key in item["dimensions"]}
            item["weighted_score"] = value * 100
            item["rationale"] = "Preserves canon and leaves meaningful choices."
            judgment["scores"].append(item)
        judgment["selected_candidate_id"] = "candidate.1"
        judgment["selection_rationale"] = "Highest weighted eligible score."
        judgment["assessor"]["provider"] = "test"
        judgment["assessor"]["model"] = "fixture-judge"
        judgment_path = write("judgment.json", judgment)

        compressor = json.loads(
            self.run_lacuna(
                "checkpoint",
                "card",
                str(request_path),
                "--role",
                "lacuna-retcon-compressor",
                "--candidates",
                str(candidates_path),
                "--judgment",
                str(judgment_path),
            ).stdout
        )
        compression = compressor["output_contract"]["template"]
        compression["state_card"] = "One tentative hidden-state card with a reversible pressure."
        compression["narration"] = "Rain ticks against the glass while the locked room waits."
        compression_path = write("compression.json", compression)

        proposal = json.loads(
            self.run_lacuna(
                "checkpoint",
                "assemble",
                str(request_path),
                str(candidates_path),
                str(judgment_path),
                str(compression_path),
            ).stdout
        )
        proposal_path = write("proposal.json", proposal)

        verifier_card = json.loads(
            self.run_lacuna(
                "checkpoint",
                "card",
                str(request_path),
                "--role",
                "lacuna-retcon-verifier",
                "--proposal",
                str(proposal_path),
            ).stdout
        )
        verifier = verifier_card["output_contract"]["template"]
        verifier["status"] = "pass"
        verifier["checks"] = {key: True for key in verifier["checks"]}
        verifier["findings"] = []
        verifier["recommended_action"] = "commit"
        verifier_path = write("verifier.json", verifier)

        review = json.loads(
            self.run_lacuna(
                "checkpoint",
                "review",
                str(self.library),
                str(request_path),
                str(candidates_path),
                str(judgment_path),
                str(proposal_path),
                str(verifier_path),
            ).stdout
        )
        self.assertEqual(review["mechanical_status"], "pass")
        review_path = write("review.json", review)
        receipt = json.loads(
            self.run_lacuna(
                "checkpoint",
                "commit",
                str(self.library),
                str(request_path),
                str(candidates_path),
                str(judgment_path),
                str(proposal_path),
                str(verifier_path),
                str(review_path),
            ).stdout
        )
        self.assertEqual(receipt["overall_status"], "accepted")
        self.assertEqual(receipt["narration"], compression["narration"])
        self.assertEqual(
            json.loads(self.run_lacuna("verify", str(self.library)).stdout)["overall_status"],
            "pass",
        )

    def test_cli_particle_review_update_and_audit_round_trip(self) -> None:
        self.create_campaign()
        claim = json.loads(
            self.run_lacuna(
                "claim-add",
                str(self.library),
                "--subject",
                "threshold",
                "--predicate",
                "shows_red_dust",
                "--object-json",
                "true",
                "--scope",
                "event",
            ).stdout
        )["claim_id"]
        self.run_lacuna(
            "assert",
            str(self.library),
            "--assertion-id",
            "ast_red_dust",
            "--claim-id",
            claim,
            "--assertor-id",
            "user",
            "--stance",
            "true",
            "--basis",
            "observation",
            "--standing",
            "accepted",
        )
        for world_id in ("wld_river", "wld_road"):
            self.run_lacuna(
                "world-add",
                str(self.library),
                "--world-id",
                world_id,
                "--label",
                world_id,
            )
        review = json.loads(
            self.run_lacuna(
                "particle-update-review", str(self.library), "ast_red_dust"
            ).stdout
        )
        self.assertEqual(review["required_assessment_world_ids"], ["wld_river", "wld_road"])
        self.run_lacuna(
            "particle-update",
            str(self.library),
            "ast_red_dust",
            "--update-id",
            "pup_red_dust",
            "--expected-bank-sha256",
            review["expected_bank_sha256"],
            "--assessment",
            "wld_river=0.8",
            "--assessment",
            "wld_road=0.2",
            "--reason",
            "The river candidate predicts red dust more strongly.",
        )
        bank = json.loads(
            self.run_lacuna("particle-bank", str(self.library)).stdout
        )
        probabilities = {
            item["world_id"]: item["probability"] for item in bank["particles"]
        }
        self.assertEqual(probabilities, {"wld_river": 0.8, "wld_road": 0.2})
        custody = json.loads(
            self.run_lacuna(
                "particle-updates", str(self.library), "--update-id", "pup_red_dust"
            ).stdout
        )
        self.assertEqual(custody["update_count"], 1)
        self.assertEqual(custody["updates"][0]["evidence_assertion_id"], "ast_red_dust")
        self.assertEqual(
            json.loads(self.run_lacuna("verify", str(self.library)).stdout)["overall_status"],
            "pass",
        )

    def test_cli_particle_factor_reconciliation_round_trip(self) -> None:
        self.create_campaign()
        claim = json.loads(
            self.run_lacuna(
                "claim-add",
                str(self.library),
                "--subject",
                "lantern",
                "--predicate",
                "casts_double_shadow",
                "--object-json",
                "true",
                "--scope",
                "event",
            ).stdout
        )["claim_id"]
        self.run_lacuna(
            "assert",
            str(self.library),
            "--assertion-id",
            "ast_double_shadow",
            "--claim-id",
            claim,
            "--assertor-id",
            "user",
            "--stance",
            "true",
            "--basis",
            "observation",
            "--standing",
            "accepted",
        )
        for world_id in ("wld_mirror", "wld_intruder"):
            self.run_lacuna(
                "world-add",
                str(self.library),
                "--world-id",
                world_id,
                "--label",
                world_id,
            )
        update_review = json.loads(
            self.run_lacuna(
                "particle-update-review", str(self.library), "ast_double_shadow"
            ).stdout
        )
        self.run_lacuna(
            "particle-update",
            str(self.library),
            "ast_double_shadow",
            "--update-id",
            "pup_double_shadow",
            "--expected-bank-sha256",
            update_review["expected_bank_sha256"],
            "--assessment",
            "wld_mirror=0.9",
            "--assessment",
            "wld_intruder=0.1",
            "--reason",
            "A mirror fault predicts the doubled shadow more strongly.",
        )
        self.run_lacuna(
            "assertion-supersede",
            str(self.library),
            "ast_double_shadow",
            "--reason",
            "The observer found a split windowpane that invalidated the report.",
        )
        stale_bank = json.loads(
            self.run_lacuna("particle-bank", str(self.library)).stdout
        )
        self.assertEqual(stale_bank["reweighting_debt_count"], 1)

        review = json.loads(
            self.run_lacuna(
                "particle-reconciliation-review", str(self.library)
            ).stdout
        )
        self.assertTrue(review["ready"], review["review_core"]["blockers"])
        receipt = json.loads(
            self.run_lacuna(
                "particle-reconcile",
                str(self.library),
                "--reconciliation-id",
                "prc_double_shadow",
                "--expected-reconciliation-sha256",
                review["expected_reconciliation_sha256"],
                "--reason",
                "Replay active factors and retain the withdrawn factor as excluded custody.",
            ).stdout
        )
        self.assertEqual(receipt["reconciliation_id"], "prc_double_shadow")
        repaired_bank = json.loads(
            self.run_lacuna("particle-bank", str(self.library)).stdout
        )
        probabilities = {
            item["world_id"]: item["probability"]
            for item in repaired_bank["particles"]
        }
        self.assertEqual(probabilities, {"wld_intruder": 0.5, "wld_mirror": 0.5})
        self.assertEqual(repaired_bank["reweighting_debt_count"], 0)
        custody = json.loads(
            self.run_lacuna(
                "particle-reconciliations",
                str(self.library),
                "--reconciliation-id",
                "prc_double_shadow",
            ).stdout
        )
        self.assertEqual(custody["reconciliation_count"], 1)
        self.assertEqual(
            custody["reconciliations"][0]["excluded_factors"][0]["update_id"],
            "pup_double_shadow",
        )
        self.assertEqual(
            json.loads(self.run_lacuna("verify", str(self.library)).stdout)["overall_status"],
            "pass",
        )

    def test_cli_context_firewall_returns_structured_refusal(self) -> None:
        self.create_campaign()
        self.run_lacuna(
            "world-add",
            str(self.library),
            "--world-id",
            "wld_hidden",
            "--label",
            "Hidden",
        )
        refused = self.run_lacuna(
            "context",
            str(self.library),
            "--agent-id",
            "player",
            "--world-id",
            "wld_hidden",
            expected=2,
        )
        body = json.loads(refused.stderr)
        self.assertEqual(body["code"], "unsafe-context-scope")

    def test_cli_cardinality_lifecycle_refuses_then_retires_cleanly(self) -> None:
        self.create_campaign()
        claim_ids = []
        for suspect in ("Ada", "Basil", "Cora"):
            declared = json.loads(
                self.run_lacuna(
                    "claim-add",
                    str(self.library),
                    "--subject",
                    "mystery",
                    "--predicate",
                    "culprit_is",
                    "--object-json",
                    json.dumps(suspect),
                ).stdout
            )
            claim_ids.append(declared["claim_id"])

        arguments = [
            "cardinality-add",
            str(self.library),
            "--constraint-id",
            "crd_culprit",
            "--label",
            "Exactly one culprit",
            "--min-true",
            "1",
            "--max-true",
            "1",
            "--rationale",
            "The authored mystery has one culprit.",
        ]
        for claim_id in claim_ids:
            arguments.extend(["--claim-id", claim_id])
        declared_constraint = json.loads(self.run_lacuna(*arguments).stdout)
        self.assertEqual(declared_constraint["constraint_id"], "crd_culprit")

        listed = json.loads(self.run_lacuna("cardinalities", str(self.library)).stdout)
        self.assertEqual(listed["constraint_count"], 1)
        self.assertEqual(listed["constraints"][0]["claim_ids"], sorted(claim_ids))

        self.run_lacuna(
            "world-add",
            str(self.library),
            "--world-id",
            "wld_case",
            "--label",
            "Case",
        )
        self.run_lacuna(
            "world-assign",
            str(self.library),
            "--world-id",
            "wld_case",
            "--claim-id",
            claim_ids[0],
            "--truth",
            "true",
        )
        refused = self.run_lacuna(
            "world-assign",
            str(self.library),
            "--world-id",
            "wld_case",
            "--claim-id",
            claim_ids[1],
            "--truth",
            "true",
            expected=2,
        )
        body = json.loads(refused.stderr)
        self.assertEqual(body["code"], "world-cardinality-conflict")
        self.assertEqual(body["details"]["violation"], "upper-bound-exceeded")

        self.run_lacuna(
            "cardinality-retire",
            str(self.library),
            "crd_culprit",
            "--reason",
            "The authored scenario now permits accomplices.",
        )
        self.run_lacuna(
            "world-assign",
            str(self.library),
            "--world-id",
            "wld_case",
            "--claim-id",
            claim_ids[1],
            "--truth",
            "true",
        )
        historical = json.loads(
            self.run_lacuna(
                "cardinalities",
                str(self.library),
                "--include-retired",
            ).stdout
        )
        self.assertEqual(historical["constraint_count"], 1)
        self.assertIsNotNone(historical["constraints"][0]["ended_seq"])
        verification = json.loads(self.run_lacuna("verify", str(self.library)).stdout)
        self.assertEqual(verification["overall_status"], "pass")

    def test_cli_fair_play_seal_round_trip_keeps_opening_outside_cube_until_reveal(self) -> None:
        self.create_campaign()
        payload_path = Path(self.temporary.name) / "seal-payload.json"
        payload_path.write_text(
            json.dumps({"culprit": "Ada", "method": "glass key"}),
            encoding="utf-8",
        )
        prepared = self.run_lacuna(
            "seal",
            "prepare",
            str(self.library),
            str(payload_path),
            "--seal-id",
            "seal_case_culprit",
            "--nonce",
            "ab" * 32,
        )
        opening = json.loads(prepared.stdout)
        opening_path = Path(self.temporary.name) / "seal-opening.json"
        opening_path.write_text(prepared.stdout, encoding="utf-8")

        created = self.run_lacuna(
            "seal",
            "create",
            str(self.library),
            str(opening_path),
            "--label",
            "Case culprit",
            "--purpose",
            "mystery",
        )
        self.assertNotIn("glass key", created.stdout)
        listed = json.loads(
            self.run_lacuna("seal", "list", str(self.library)).stdout
        )
        self.assertEqual(listed["seal_count"], 1)
        self.assertEqual(listed["seals"][0]["status"], "sealed")
        self.assertIsNone(listed["seals"][0]["reveal_payload"])
        opening_check = json.loads(
            self.run_lacuna(
                "seal", "verify", str(self.library), str(opening_path)
            ).stdout
        )
        self.assertEqual(opening_check["overall_status"], "pass")

        revealed = json.loads(
            self.run_lacuna(
                "seal",
                "reveal",
                str(self.library),
                str(opening_path),
                "--reason",
                "The players completed the fair investigation.",
            ).stdout
        )
        self.assertEqual(
            revealed["receipt"]["opening"]["payload"], opening["payload"]
        )
        verification = json.loads(
            self.run_lacuna("verify", str(self.library)).stdout
        )
        self.assertEqual(verification["overall_status"], "pass")

    def test_cli_governed_revision_repairs_consequence_with_explicit_lineage(self) -> None:
        self.create_campaign()
        claim_ids = []
        for predicate in ("signal_is_red", "guard_waits"):
            declared = json.loads(
                self.run_lacuna(
                    "claim-add",
                    str(self.library),
                    "--subject",
                    "crossing",
                    "--predicate",
                    predicate,
                    "--object-json",
                    "true",
                ).stdout
            )
            claim_ids.append(declared["claim_id"])

        self.run_lacuna(
            "world-add",
            str(self.library),
            "--world-id",
            "wld_crossing",
            "--label",
            "Crossing",
        )
        for assignment_id, claim_id in zip(("asn_signal", "asn_guard"), claim_ids, strict=True):
            self.run_lacuna(
                "world-assign",
                str(self.library),
                "--assignment-id",
                assignment_id,
                "--world-id",
                "wld_crossing",
                "--claim-id",
                claim_id,
                "--truth",
                "true",
            )

        self.run_lacuna(
            "consequence-link",
            str(self.library),
            "asn_signal",
            "world_assignment",
            "asn_guard",
            "constrains",
            "--consequence-id",
            "csq_signal_guard",
            "--severity",
            "material",
            "--rationale",
            "The guard waits because the signal is red.",
        )
        listed = json.loads(self.run_lacuna("consequences", str(self.library)).stdout)
        self.assertEqual(listed["consequence_count"], 1)
        self.assertFalse(listed["consequences"][0]["repair_required"])

        stale_impact = json.loads(
            self.run_lacuna("revision-impact", str(self.library), "asn_signal").stdout
        )
        self.assertTrue(stale_impact["review"]["revisable"])
        self.run_lacuna(
            "world-weight",
            str(self.library),
            "wld_crossing",
            "0.8",
            "--reason",
            "Exercise head-bound revision custody.",
        )
        refused = self.run_lacuna(
            "world-revise",
            str(self.library),
            "asn_signal",
            "false",
            "--assignment-id",
            "asn_signal_revised",
            "--expected-impact-sha256",
            stale_impact["impact_sha256"],
            "--reason",
            "The observed signal state was reinterpreted.",
            expected=2,
        )
        self.assertEqual(json.loads(refused.stderr)["code"], "stale-revision-impact")

        fresh_impact = json.loads(
            self.run_lacuna("revision-impact", str(self.library), "asn_signal").stdout
        )
        self.run_lacuna(
            "world-revise",
            str(self.library),
            "asn_signal",
            "false",
            "--assignment-id",
            "asn_signal_revised",
            "--expected-impact-sha256",
            fresh_impact["impact_sha256"],
            "--reason",
            "The observed signal state was reinterpreted.",
        )
        status = json.loads(self.run_lacuna("status", str(self.library)).stdout)
        self.assertEqual(status["world_revision_count"], 1)
        self.assertEqual(status["orphaned_consequence_count"], 1)

        repair_debt = json.loads(
            self.run_lacuna("consequences", str(self.library)).stdout
        )["consequences"][0]
        self.assertTrue(repair_debt["repair_required"])
        self.assertFalse(repair_debt["premise_active"])
        frontier = json.loads(
            self.run_lacuna(
                "consequence-repair-frontier",
                str(self.library),
                "--world-id",
                "wld_crossing",
            ).stdout
        )
        self.assertEqual(frontier["repair_required_count"], 1)
        self.assertEqual(
            frontier["reviews"][0]["target"]["consequence_id"],
            "csq_signal_guard",
        )
        review = json.loads(
            self.run_lacuna(
                "consequence-repair-review",
                str(self.library),
                "csq_signal_guard",
            ).stdout
        )
        self.assertEqual(review["review"]["mode"], "orphan-repair")
        self.assertEqual(
            review["known_successors"]["premise_assignment_ids"],
            ["asn_signal_revised"],
        )
        self.run_lacuna(
            "consequence-replace",
            str(self.library),
            "csq_signal_guard",
            "asn_signal_revised",
            "world_assignment",
            "asn_guard",
            "constrains",
            "--consequence-id",
            "csq_signal_guard_repaired",
            "--repair-id",
            "cpr_signal_guard",
            "--severity",
            "material",
            "--rationale",
            "The guard's continuing wait is now constrained by the revised signal premise.",
            "--expected-repair-sha256",
            review["repair_review_sha256"],
            "--reason",
            "Relink the downstream custody rather than erasing it.",
        )
        active = json.loads(self.run_lacuna("consequences", str(self.library)).stdout)
        self.assertEqual(active["consequence_count"], 1)
        self.assertEqual(
            active["consequences"][0]["consequence_id"],
            "csq_signal_guard_repaired",
        )
        self.assertFalse(active["consequences"][0]["repair_required"])
        historical = json.loads(
            self.run_lacuna(
                "consequences", str(self.library), "--include-retired"
            ).stdout
        )
        self.assertEqual(historical["consequence_count"], 2)
        by_id = {item["consequence_id"]: item for item in historical["consequences"]}
        self.assertIsNotNone(by_id["csq_signal_guard"]["ended_seq"])
        self.assertEqual(by_id["csq_signal_guard"]["lineage_state"], "replaced")
        self.assertEqual(
            by_id["csq_signal_guard_repaired"]["lineage_state"],
            "replacement",
        )
        repairs = json.loads(
            self.run_lacuna("consequence-repairs", str(self.library)).stdout
        )
        self.assertEqual(repairs["repair_count"], 1)
        self.assertEqual(repairs["repairs"][0]["repair_id"], "cpr_signal_guard")
        self.assertEqual(repairs["repairs"][0]["review_head"], review["head"])
        empty_frontier = json.loads(
            self.run_lacuna(
                "consequence-repair-frontier",
                str(self.library),
                "--world-id",
                "wld_crossing",
            ).stdout
        )
        self.assertEqual(empty_frontier["repair_required_count"], 0)
        verification = json.loads(self.run_lacuna("verify", str(self.library)).stdout)
        self.assertEqual(verification["overall_status"], "pass")


    def test_cli_model_brief_is_read_only_and_profile_explicit(self) -> None:
        self.create_campaign()
        before = json.loads(self.run_lacuna("head", str(self.library)).stdout)["head"]
        brief = json.loads(
            self.run_lacuna(
                "model",
                "brief",
                str(self.library),
                "--profile",
                "orchestrated",
                "--format",
                "json",
            ).stdout
        )
        after = json.loads(self.run_lacuna("head", str(self.library)).stdout)["head"]
        self.assertEqual(before, after)
        self.assertEqual(brief["schema"], "lacuna.model-brief.v1")
        self.assertTrue(brief["readiness"]["cube_ready_for_governed_turn"])
        self.assertTrue(
            brief["readiness"]["selected_profile_can_start_without_bridge"]
        )
        self.assertTrue(brief["delegation"]["enabled_by_profile"])
        self.assertEqual(len(brief["delegation"]["roles"]), 4)

        rendered = self.run_lacuna(
            "model",
            "brief",
            str(self.library),
            "--profile",
            "chat",
            "--format",
            "markdown",
        ).stdout
        self.assertIn("This profile can start governed play without a bridge: **no**", rendered)
        self.assertIn("./lacuna turn run begin", rendered)
        self.assertIn("./lacuna turn run accept", rendered)
        self.assertIn("./lacuna turn run commit", rendered)
        self.assertEqual(
            json.loads(self.run_lacuna("head", str(self.library)).stdout)["head"],
            before,
        )


if __name__ == "__main__":
    unittest.main()
