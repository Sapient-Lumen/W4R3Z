from __future__ import annotations

import math
import sqlite3
import tempfile
import unittest
from pathlib import Path

import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from lacuna.context import build_context
from lacuna.errors import LacunaError
from lacuna.particles import build_particle_bank_from_records, compute_factor_reconciliation
from lacuna.render import render_context_markdown
from lacuna.store import Cube
from lacuna.turns import build_turn_packet, commit_turn_proposal
from lacuna.util import deterministic_claim_id


class ParticleReconciliationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name) / "cube"
        self.cube = Cube.init(self.root)

    def tearDown(self) -> None:
        if self.cube is not None:
            self.cube.close()
        self.temporary.cleanup()

    def seed(
        self,
        *,
        evidence_count: int = 2,
        weights: tuple[float, ...] = (1.0, 1.0),
    ) -> tuple[list[str], list[str]]:
        operations: list[dict] = []
        evidence_ids: list[str] = []
        for index in range(1, evidence_count + 1):
            claim_id = deterministic_claim_id(
                f"threshold.{index}", "shows_trace", True, "event"
            )
            assertion_id = f"ast.factor.{index}"
            evidence_ids.append(assertion_id)
            operations.extend(
                [
                    {
                        "op": "declare_claim",
                        "claim_id": claim_id,
                        "subject": f"threshold.{index}",
                        "predicate": "shows_trace",
                        "object": True,
                        "scope": "event",
                    },
                    {
                        "op": "record_assertion",
                        "assertion_id": assertion_id,
                        "claim_id": claim_id,
                        "assertor_id": "user",
                        "stance": "true",
                        "basis": "observation",
                        "standing": "accepted",
                        "confidence": 0.9,
                        "visibility": "private",
                        "note": f"Factor observation {index}.",
                    },
                ]
            )
        world_ids: list[str] = []
        for index, weight in enumerate(weights, start=1):
            world_id = f"world.{index}"
            world_ids.append(world_id)
            operations.append(
                {
                    "op": "create_world",
                    "world_id": world_id,
                    "label": f"Candidate {index}",
                    "status": "live",
                    "weight": weight,
                    "rationale": "Keep multiple hidden explanations alive.",
                }
            )
        self.cube.apply_operations(actor_id="user", operations=operations)
        return evidence_ids, world_ids

    def update(
        self,
        assertion_id: str,
        likelihoods: dict[str, float],
        *,
        update_id: str,
    ) -> None:
        bank = self.cube.particle_bank()
        self.cube.apply_operations(
            actor_id="user",
            operations=[
                {
                    "op": "update_particle_bank",
                    "update_id": update_id,
                    "evidence_assertion_id": assertion_id,
                    "expected_bank_sha256": bank["bank_sha256"],
                    "assessments": [
                        {
                            "world_id": world_id,
                            "likelihood": likelihood,
                            "rationale": f"Assessment for {world_id}.",
                        }
                        for world_id, likelihood in sorted(likelihoods.items())
                    ],
                    "reason": f"Apply factor {update_id}.",
                }
            ],
        )

    def supersede(self, assertion_id: str) -> None:
        self.cube.apply_operations(
            actor_id="user",
            operations=[
                {
                    "op": "supersede_assertion",
                    "assertion_id": assertion_id,
                    "reason": "The observation was withdrawn after audit.",
                }
            ],
        )

    def reconcile(self, reconciliation_id: str = "prc.audit") -> dict:
        review = self.cube.particle_reconciliation_review()
        self.assertTrue(review["ready"], review["review_core"]["blockers"])
        self.cube.apply_operations(
            actor_id="user",
            operations=[
                {
                    "op": "reconcile_particle_bank",
                    "reconciliation_id": reconciliation_id,
                    "expected_reconciliation_sha256": review[
                        "expected_reconciliation_sha256"
                    ],
                    "reason": "Replay authorized factors and exclude withdrawn custody.",
                }
            ],
        )
        return self.cube.particle_reconciliations(
            reconciliation_id=reconciliation_id
        )[0]

    def probabilities(self) -> dict[str, float]:
        return {
            item["world_id"]: float(item["probability"])
            for item in self.cube.particle_bank()["particles"]
        }

    def test_withdrawn_factor_is_excluded_without_erasing_history(self) -> None:
        evidence, worlds = self.seed(evidence_count=1)
        self.update(
            evidence[0],
            {worlds[0]: 0.8, worlds[1]: 0.2},
            update_id="pup.factor.1",
        )
        self.supersede(evidence[0])
        self.assertEqual(self.cube.particle_bank()["reweighting_debt_count"], 1)

        reconciliation = self.reconcile()
        probabilities = self.probabilities()
        self.assertAlmostEqual(probabilities[worlds[0]], 0.5)
        self.assertAlmostEqual(probabilities[worlds[1]], 0.5)
        self.assertEqual(reconciliation["included_factors"], [])
        self.assertEqual(
            reconciliation["excluded_factors"][0]["update_id"], "pup.factor.1"
        )
        bank = self.cube.particle_bank()
        self.assertEqual(bank["reweighting_debt_count"], 0)
        self.assertEqual(
            bank["applied_factors"][0]["ledger_status"], "reconciled-excluded"
        )
        self.assertEqual(len(self.cube.particle_updates()), 1)
        explanation = self.cube.explain("prc.audit")
        self.assertEqual(explanation["target"]["kind"], "particle_reconciliation")
        self.assertTrue(
            any(
                item["kind"] == "particle_update"
                and item["id"] == "pup.factor.1"
                for item in explanation["dependencies"]
            )
        )
        with self.assertRaises(LacunaError) as hidden:
            self.cube.explain("prc.audit", agent_id="user")
        self.assertEqual(hidden.exception.code, "explanation-not-visible")
        self.assertEqual(self.cube.verify()["overall_status"], "pass")

    def test_active_factor_is_replayed_after_an_earlier_factor_is_withdrawn(self) -> None:
        evidence, worlds = self.seed(evidence_count=2)
        self.update(
            evidence[0],
            {worlds[0]: 0.9, worlds[1]: 0.1},
            update_id="pup.factor.1",
        )
        self.update(
            evidence[1],
            {worlds[0]: 0.2, worlds[1]: 0.8},
            update_id="pup.factor.2",
        )
        before = self.probabilities()
        self.assertAlmostEqual(before[worlds[0]], 0.18 / 0.26)
        self.supersede(evidence[0])

        reconciliation = self.reconcile()
        after = self.probabilities()
        self.assertAlmostEqual(after[worlds[0]], 0.2)
        self.assertAlmostEqual(after[worlds[1]], 0.8)
        self.assertEqual(
            [item["update_id"] for item in reconciliation["included_factors"]],
            ["pup.factor.2"],
        )
        self.assertEqual(
            [item["update_id"] for item in reconciliation["excluded_factors"]],
            ["pup.factor.1"],
        )

    def test_later_factor_withdrawal_creates_a_new_reconciliation_generation(self) -> None:
        evidence, worlds = self.seed(evidence_count=2)
        self.update(
            evidence[0],
            {worlds[0]: 0.9, worlds[1]: 0.1},
            update_id="pup.factor.1",
        )
        self.update(
            evidence[1],
            {worlds[0]: 0.25, worlds[1]: 0.75},
            update_id="pup.factor.2",
        )

        self.supersede(evidence[0])
        first = self.reconcile("prc.generation.1")
        self.assertEqual(
            [item["update_id"] for item in first["included_factors"]],
            ["pup.factor.2"],
        )
        self.assertEqual(
            [item["update_id"] for item in first["excluded_factors"]],
            ["pup.factor.1"],
        )
        first_bank = self.cube.particle_bank()
        self.assertEqual(first_bank["reweighting_debt_count"], 0)

        self.supersede(evidence[1])
        debt = self.cube.particle_bank()
        status_by_update = {
            item["update_id"]: item["ledger_status"]
            for item in debt["applied_factors"]
        }
        self.assertEqual(status_by_update["pup.factor.1"], "reconciled-excluded")
        self.assertEqual(status_by_update["pup.factor.2"], "reconciliation-required")
        self.assertEqual(debt["reweighting_debt_count"], 1)

        second = self.reconcile("prc.generation.2")
        self.assertEqual(second["included_factors"], [])
        self.assertEqual(
            [item["update_id"] for item in second["excluded_factors"]],
            ["pup.factor.1", "pup.factor.2"],
        )
        self.assertEqual(len(self.cube.particle_reconciliations()), 2)
        final_bank = self.cube.particle_bank()
        self.assertEqual(final_bank["reweighting_debt_count"], 0)
        self.assertTrue(
            all(
                item["ledger_status"] == "reconciled-excluded"
                for item in final_bank["applied_factors"]
            )
        )
        self.assertAlmostEqual(self.probabilities()[worlds[0]], 0.5)
        self.assertAlmostEqual(self.probabilities()[worlds[1]], 0.5)
        self.assertEqual(self.cube.verify()["overall_status"], "pass")

    def test_log_space_replay_recovers_mass_lost_by_sequential_underflow(self) -> None:
        identity = {
            "status": "live",
            "valuation_sha256": "1" * 64,
            "custody_sha256": "2" * 64,
        }
        baseline = build_particle_bank_from_records(
            [
                {"world_id": "world.1", "raw_weight": 1.0, **identity},
                {"world_id": "world.2", "raw_weight": 1.0, **identity},
            ]
        )
        current = build_particle_bank_from_records(
            [
                {"world_id": "world.1", "raw_weight": 1.0, **identity},
                {"world_id": "world.2", "raw_weight": 0.0, **identity},
            ]
        )
        factors = []
        for index in range(140):
            factors.append(
                {
                    "update_id": f"pup.{index:03d}",
                    "assessments": [
                        {
                            "world_id": "world.1",
                            "world_status": "live",
                            "likelihood": 1e-200,
                            "valuation_sha256": "1" * 64,
                            "custody_sha256": "2" * 64,
                        },
                        {
                            "world_id": "world.2",
                            "world_status": "live",
                            "likelihood": 1e-201,
                            "valuation_sha256": "1" * 64,
                            "custody_sha256": "2" * 64,
                        },
                    ],
                }
            )
        result = compute_factor_reconciliation(
            baseline_bank=baseline,
            current_bank=current,
            included_factors=factors,
        )
        posterior = {
            item["world_id"]: item["posterior_probability"]
            for item in result["members"]
        }
        self.assertGreater(posterior["world.2"], 0.0)
        self.assertTrue(
            math.isclose(posterior["world.2"], 1e-140, rel_tol=1e-11, abs_tol=0.0)
        )
        self.assertAlmostEqual(
            result["current_to_posterior_total_variation"], posterior["world.2"]
        )

    def test_review_is_head_bound_atomic_and_repeat_reconciliation_is_refused(self) -> None:
        evidence, worlds = self.seed(evidence_count=1)
        self.update(
            evidence[0],
            {worlds[0]: 0.7, worlds[1]: 0.3},
            update_id="pup.factor.1",
        )
        self.supersede(evidence[0])
        stale_review = self.cube.particle_reconciliation_review()
        self.cube.apply_operations(
            actor_id="user",
            operations=[
                {
                    "op": "add_source",
                    "source_id": "src.unrelated",
                    "kind": "other",
                    "label": "Unrelated provenance",
                    "metadata": {},
                }
            ],
        )
        before_count = self.cube.event_count()
        with self.assertRaises(LacunaError) as stale:
            self.cube.apply_operations(
                actor_id="user",
                operations=[
                    {
                        "op": "reconcile_particle_bank",
                        "reconciliation_id": "prc.stale",
                        "expected_reconciliation_sha256": stale_review[
                            "expected_reconciliation_sha256"
                        ],
                        "reason": "Stale on purpose.",
                    }
                ],
            )
        self.assertEqual(stale.exception.code, "stale-particle-reconciliation-review")
        self.assertEqual(self.cube.event_count(), before_count)
        self.reconcile("prc.fresh")

        repeated = self.cube.particle_reconciliation_review()
        self.assertFalse(repeated["ready"])
        self.assertEqual(
            repeated["review_core"]["blockers"][0]["code"],
            "particle-factor-ledger-already-reconciled",
        )
        before_count = self.cube.event_count()
        with self.assertRaises(LacunaError) as duplicate:
            self.cube.apply_operations(
                actor_id="user",
                operations=[
                    {
                        "op": "reconcile_particle_bank",
                        "reconciliation_id": "prc.repeat",
                        "expected_reconciliation_sha256": repeated[
                            "expected_reconciliation_sha256"
                        ],
                        "reason": "No-op on purpose.",
                    }
                ],
            )
        self.assertEqual(duplicate.exception.code, "particle-reconciliation-blocked")
        self.assertEqual(self.cube.event_count(), before_count)

    def test_structural_boundary_retires_old_factors_instead_of_replaying_them(self) -> None:
        evidence, worlds = self.seed(evidence_count=1)
        self.update(
            evidence[0],
            {worlds[0]: 0.8, worlds[1]: 0.2},
            update_id="pup.factor.1",
        )
        self.supersede(evidence[0])
        self.cube.apply_operations(
            actor_id="user",
            operations=[
                {
                    "op": "set_world_weight",
                    "world_id": worlds[0],
                    "weight": 2.0,
                    "reason": "Begin a new authored-prior epoch.",
                }
            ],
        )
        bank = self.cube.particle_bank()
        self.assertEqual(bank["reweighting_debt_count"], 0)
        self.assertEqual(bank["applied_factors"][0]["ledger_status"], "epoch-retired")
        review = self.cube.particle_reconciliation_review()
        self.assertFalse(review["ready"])
        self.assertEqual(
            review["review_core"]["blockers"][0]["code"],
            "no-replayable-particle-factor-epoch",
        )

    def test_projection_tamper_is_detected_and_rebuild_restores_reconciliation(self) -> None:
        evidence, worlds = self.seed(evidence_count=1)
        self.update(
            evidence[0],
            {worlds[0]: 0.8, worlds[1]: 0.2},
            update_id="pup.factor.1",
        )
        self.supersede(evidence[0])
        self.reconcile()
        self.cube.conn.execute(
            """UPDATE particle_reconciliation_members
               SET posterior_probability = 0.9
               WHERE reconciliation_id = 'prc.audit' AND world_id = ?""",
            (worlds[0],),
        )
        self.cube.conn.commit()
        report = self.cube.verify()
        self.assertEqual(report["overall_status"], "fail")
        self.assertTrue(
            any(
                item["code"].startswith("particle-reconciliation-")
                for item in report["errors"]
            )
        )
        rebuilt = self.cube.rebuild_projections()
        self.assertEqual(rebuilt["overall_status"], "pass")
        self.assertAlmostEqual(self.probabilities()[worlds[0]], 0.5)
        self.assertEqual(len(self.cube.particle_reconciliations()), 1)

    def test_context_firewall_and_turn_entrances_preserve_complete_population_scope(self) -> None:
        evidence, worlds = self.seed(evidence_count=1)
        self.update(
            evidence[0],
            {worlds[0]: 0.8, worlds[1]: 0.2},
            update_id="pup.factor.1",
        )
        self.supersede(evidence[0])
        audience = build_context(self.cube, agent_id="user")
        self.assertIsNone(audience["particle_reconciliation_review"])
        self.assertIn("particle_reconciliations", audience["omitted"])
        audience_markdown = render_context_markdown(audience)
        self.assertIn("Factor-ledger reconciliation", audience_markdown)
        self.assertNotIn("pup.factor.1", audience_markdown)

        planner = build_context(self.cube)
        planner_markdown = render_context_markdown(planner)
        self.assertIn("Current review: **ready**", planner_markdown)
        self.assertIn("pup.factor.1", planner_markdown)

        scoped = build_context(self.cube, world_id=worlds[0])
        self.assertIsNone(scoped["particle_reconciliation_review"])
        self.assertIn("particle_reconciliation_review", scoped["omitted"])

        packet = build_turn_packet(
            self.cube,
            audience_id="user",
            actor_id="user",
            player_input="Correct the factor ledger.",
            director=True,
        )
        proposal = dict(packet["response_contract"]["proposal_template"])
        proposal["narration"] = "The hidden hypotheses are rebalanced without changing the scene."
        proposal["revealed_assertion_ids"] = []
        proposal["operations"] = [
            {
                "op": "reconcile_particle_bank",
                "reconciliation_id": "prc.turn",
                "expected_reconciliation_sha256": packet["planner_context"][
                    "particle_reconciliation_review"
                ]["expected_reconciliation_sha256"],
                "reason": "Apply the packet-bound factor repair.",
            }
        ]
        committed = commit_turn_proposal(self.cube, proposal)
        self.assertEqual(committed["event"], "lacuna.turn.committed")
        self.assertEqual(len(self.cube.particle_reconciliations()), 1)

        # A fresh cube is used for the scoped refusal because this ledger is now repaired.
        self.cube.close()
        self.cube = Cube.init(Path(self.temporary.name) / "scoped")
        evidence, worlds = self.seed(evidence_count=1)
        self.update(
            evidence[0],
            {worlds[0]: 0.8, worlds[1]: 0.2},
            update_id="pup.factor.1",
        )
        self.supersede(evidence[0])
        packet = build_turn_packet(
            self.cube,
            audience_id="user",
            actor_id="user",
            player_input="Repair only this branch.",
            director=True,
            world_id=worlds[0],
        )
        proposal = dict(packet["response_contract"]["proposal_template"])
        proposal["narration"] = "Nothing observable changes."
        proposal["revealed_assertion_ids"] = []
        proposal["operations"] = [
            {
                "op": "reconcile_particle_bank",
                "expected_reconciliation_sha256": "0" * 64,
                "reason": "This must be refused before kernel mutation.",
            }
        ]
        with self.assertRaises(LacunaError) as refused:
            commit_turn_proposal(self.cube, proposal)
        self.assertEqual(refused.exception.code, "turn-world-scope-violation")

    def test_schema_seven_migrates_to_eight_without_rewriting_head(self) -> None:
        evidence, worlds = self.seed(evidence_count=1)
        self.update(
            evidence[0],
            {worlds[0]: 0.6, worlds[1]: 0.4},
            update_id="pup.factor.1",
        )
        before_head = self.cube.head()
        self.cube.close()
        self.cube = None
        db_path = self.root / "lacuna.sqlite3"
        conn = sqlite3.connect(db_path)
        try:
            conn.execute("DROP INDEX particle_reconciliation_members_world_idx")
            conn.execute("DROP TABLE particle_reconciliation_members")
            conn.execute("DROP INDEX particle_reconciliation_factors_update_idx")
            conn.execute("DROP TABLE particle_reconciliation_factors")
            conn.execute("DROP INDEX particle_reconciliations_created_idx")
            conn.execute("DROP TABLE particle_reconciliations")
            conn.execute("DELETE FROM schema_migrations WHERE target_version = 8")
            conn.execute("PRAGMA user_version = 7")
            conn.execute("UPDATE meta SET value = '7' WHERE key = 'schema_version'")
            conn.commit()
        finally:
            conn.close()
        receipt = Cube.migrate(self.root)
        self.assertEqual(receipt["source_version"], 7)
        self.assertEqual(receipt["target_version"], 8)
        self.assertEqual(receipt["before_head"], before_head)
        self.assertEqual(receipt["after_head"], before_head)
        self.cube = Cube.open(self.root)
        self.assertEqual(len(self.cube.particle_updates()), 1)
        self.assertEqual(self.cube.particle_reconciliations(), [])
        self.assertEqual(self.cube.verify()["overall_status"], "pass")


if __name__ == "__main__":
    unittest.main()
