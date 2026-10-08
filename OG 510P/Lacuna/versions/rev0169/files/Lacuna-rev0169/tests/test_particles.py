from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from lacuna.context import build_context
from lacuna.errors import LacunaError
from lacuna.store import Cube
from lacuna.turns import build_turn_packet, commit_turn_proposal, normalize_turn_operations
from lacuna.util import deterministic_claim_id


class ParticleBankTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name) / "cube"
        self.cube = Cube.init(self.root)

    def tearDown(self) -> None:
        if self.cube is not None:
            self.cube.close()
        self.temporary.cleanup()

    def seed(self, *, weights: tuple[float, ...] = (1.0, 1.0)) -> tuple[str, list[str]]:
        evidence_claim = deterministic_claim_id(
            "threshold", "left_red_dust", True, "event"
        )
        operations = [
            {
                "op": "declare_claim",
                "claim_id": evidence_claim,
                "subject": "threshold",
                "predicate": "left_red_dust",
                "object": True,
                "scope": "event",
            },
            {
                "op": "record_assertion",
                "assertion_id": "ast.red-dust",
                "claim_id": evidence_claim,
                "assertor_id": "user",
                "stance": "true",
                "basis": "observation",
                "standing": "accepted",
                "confidence": 0.95,
                "visibility": "private",
                "note": "Red dust is visible on the threshold.",
            },
        ]
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
                    "rationale": "A deliberately unresolved explanation.",
                }
            )
        self.cube.apply_operations(actor_id="user", operations=operations)
        return "ast.red-dust", world_ids

    def apply_update(
        self,
        evidence_id: str,
        likelihoods: dict[str, float],
        *,
        update_id: str = "pup.red-dust",
    ) -> dict:
        bank = self.cube.particle_bank()
        return self.cube.apply_operations(
            actor_id="user",
            operations=[
                {
                    "op": "update_particle_bank",
                    "update_id": update_id,
                    "evidence_assertion_id": evidence_id,
                    "expected_bank_sha256": bank["bank_sha256"],
                    "assessments": [
                        {
                            "world_id": world_id,
                            "likelihood": likelihood,
                            "rationale": f"Authored likelihood for {world_id}.",
                        }
                        for world_id, likelihood in sorted(likelihoods.items())
                    ],
                    "reason": "Redistribute planning attention after recorded evidence.",
                }
            ],
        )

    def test_bank_normalizes_without_mutation_and_reports_valuation_duplicates(self) -> None:
        _, worlds = self.seed(weights=(1.0, 3.0))
        latent_claim = deterministic_claim_id("visitor", "arrived_by", "river", "world")
        self.cube.apply_operations(
            actor_id="user",
            operations=[
                {
                    "op": "declare_claim",
                    "claim_id": latent_claim,
                    "subject": "visitor",
                    "predicate": "arrived_by",
                    "object": "river",
                    "scope": "world",
                },
                *[
                    {
                        "op": "assign_world",
                        "assignment_id": f"asn.{world_id}",
                        "world_id": world_id,
                        "claim_id": latent_claim,
                        "truth": "true",
                        "commitment": "tentative",
                        "rationale": "Same proposition, separately custodied.",
                    }
                    for world_id in worlds
                ],
            ],
        )
        bank = self.cube.particle_bank()
        self.assertEqual(bank["normalization_status"], "normalized")
        self.assertEqual([item["probability"] for item in bank["particles"]], [0.25, 0.75])
        self.assertAlmostEqual(bank["effective_sample_size"], 1.6)
        self.assertEqual(bank["duplicate_valuation_group_count"], 1)
        self.assertEqual(
            bank["particles"][0]["valuation_sha256"],
            bank["particles"][1]["valuation_sha256"],
        )
        self.assertNotEqual(
            bank["particles"][0]["custody_sha256"],
            bank["particles"][1]["custody_sha256"],
        )
        stored = {
            row["world_id"]: row["weight"]
            for row in self.cube.conn.execute("SELECT world_id, weight FROM worlds")
        }
        self.assertEqual(stored, {worlds[0]: 1.0, worlds[1]: 3.0})

    def test_evidence_update_is_complete_atomic_and_does_not_select_or_prune(self) -> None:
        evidence_id, worlds = self.seed()
        before_statuses = {item["world_id"]: item["status"] for item in self.cube.worlds()}
        self.apply_update(evidence_id, {worlds[0]: 0.9, worlds[1]: 0.1})
        bank = self.cube.particle_bank()
        self.assertAlmostEqual(bank["particles"][0]["probability"], 0.9)
        self.assertAlmostEqual(bank["particles"][1]["probability"], 0.1)
        after_statuses = {item["world_id"]: item["status"] for item in self.cube.worlds()}
        self.assertEqual(after_statuses, before_statuses)
        update = self.cube.particle_updates()[0]
        self.assertEqual(update["method"], "likelihood-reweight-v1")
        self.assertAlmostEqual(update["normalization_constant"], 0.5)
        self.assertAlmostEqual(update["posterior_effective_sample_size"], 1 / 0.82)
        self.assertEqual(len(update["assessments"]), 2)
        self.assertEqual(self.cube.verify()["overall_status"], "pass")

    def test_incomplete_stale_and_zero_posterior_updates_leave_no_trace(self) -> None:
        evidence_id, worlds = self.seed()
        review = self.cube.particle_update_review(evidence_id)
        before_head = self.cube.head()
        before_count = self.cube.event_count()
        with self.assertRaises(LacunaError) as incomplete:
            self.cube.apply_operations(
                actor_id="user",
                operations=[
                    {
                        "op": "update_particle_bank",
                        "evidence_assertion_id": evidence_id,
                        "expected_bank_sha256": review["expected_bank_sha256"],
                        "assessments": [{"world_id": worlds[0], "likelihood": 1.0}],
                        "reason": "Incomplete on purpose.",
                    }
                ],
            )
        self.assertEqual(incomplete.exception.code, "incomplete-particle-assessments")
        self.assertEqual(self.cube.head(), before_head)
        self.assertEqual(self.cube.event_count(), before_count)

        with self.assertRaises(LacunaError) as zero:
            self.cube.apply_operations(
                actor_id="user",
                operations=[
                    {
                        "op": "update_particle_bank",
                        "evidence_assertion_id": evidence_id,
                        "expected_bank_sha256": review["expected_bank_sha256"],
                        "assessments": [
                            {"world_id": world_id, "likelihood": 0.0}
                            for world_id in worlds
                        ],
                        "reason": "All zero on purpose.",
                    }
                ],
            )
        self.assertEqual(zero.exception.code, "zero-posterior-mass")
        self.assertEqual(self.cube.event_count(), before_count)

        self.cube.apply_operations(
            actor_id="user",
            operations=[
                {
                    "op": "set_world_weight",
                    "world_id": worlds[0],
                    "weight": 2.0,
                    "reason": "Invalidate the reviewed population.",
                }
            ],
        )
        with self.assertRaises(LacunaError) as stale:
            self.cube.apply_operations(
                actor_id="user",
                operations=[
                    {
                        "op": "update_particle_bank",
                        "evidence_assertion_id": evidence_id,
                        "expected_bank_sha256": review["expected_bank_sha256"],
                        "assessments": [
                            {"world_id": world_id, "likelihood": 0.5}
                            for world_id in worlds
                        ],
                        "reason": "Stale on purpose.",
                    }
                ],
            )
        self.assertEqual(stale.exception.code, "stale-particle-bank")

    def test_pruned_world_is_excluded_but_not_deleted(self) -> None:
        evidence_id, worlds = self.seed(weights=(1.0, 1.0, 1.0))
        self.cube.apply_operations(
            actor_id="user",
            operations=[
                {
                    "op": "set_world_status",
                    "world_id": worlds[2],
                    "status": "pruned",
                    "reason": "Explicit human pruning, independent of evidence update.",
                }
            ],
        )
        bank = self.cube.particle_bank()
        self.assertEqual([item["world_id"] for item in bank["particles"]], worlds[:2])
        self.apply_update(evidence_id, {worlds[0]: 0.8, worlds[1]: 0.2})
        pruned = self.cube._require_world(worlds[2])
        self.assertEqual(pruned["status"], "pruned")
        self.assertEqual(pruned["weight"], 1.0)

    def test_superseded_evidence_cannot_authorize_a_new_update(self) -> None:
        evidence_id, _ = self.seed()
        self.cube.apply_operations(
            actor_id="user",
            operations=[
                {
                    "op": "supersede_assertion",
                    "assertion_id": evidence_id,
                    "reason": "The observation was withdrawn.",
                }
            ],
        )
        with self.assertRaises(LacunaError) as caught:
            self.cube.particle_update_review(evidence_id)
        self.assertEqual(caught.exception.code, "unknown-assertion")

    def test_evidence_factor_is_single_use_and_supersession_surfaces_debt(self) -> None:
        evidence_id, worlds = self.seed()
        self.apply_update(evidence_id, {worlds[0]: 0.7, worlds[1]: 0.3})

        bank = self.cube.particle_bank()
        self.assertEqual(bank["applied_factor_count"], 1)
        self.assertEqual(bank["reweighting_debt_count"], 0)
        self.assertEqual(bank["applied_factors"][0]["evidence_status"], "active")

        with self.assertRaises(LacunaError) as reviewed_again:
            self.cube.particle_update_review(evidence_id)
        self.assertEqual(
            reviewed_again.exception.code, "particle-evidence-already-applied"
        )

        with self.assertRaises(LacunaError) as reused:
            self.apply_update(
                evidence_id,
                {worlds[0]: 0.6, worlds[1]: 0.4},
                update_id="pup.red-dust.reused",
            )
        self.assertEqual(reused.exception.code, "particle-evidence-already-applied")
        self.assertEqual(len(self.cube.particle_updates()), 1)

        self.cube.apply_operations(
            actor_id="user",
            operations=[
                {
                    "op": "supersede_assertion",
                    "assertion_id": evidence_id,
                    "reason": "The observation was later withdrawn.",
                }
            ],
        )
        bank = self.cube.particle_bank()
        self.assertEqual(bank["reweighting_debt_count"], 1)
        self.assertEqual(bank["reweighting_debt"][0]["update_id"], "pup.red-dust")
        self.assertEqual(bank["reweighting_debt"][0]["evidence_status"], "superseded")
        update = self.cube.particle_updates()[0]
        self.assertEqual(update["evidence_status"], "superseded")
        self.assertIsNotNone(update["evidence_ended_seq"])
        self.assertEqual(self.cube.verify()["overall_status"], "pass")

    def test_same_change_double_factor_refuses_atomically(self) -> None:
        evidence_id, worlds = self.seed()
        bank = self.cube.particle_bank()
        before_head = self.cube.head()
        before_count = self.cube.event_count()
        operation = {
            "op": "update_particle_bank",
            "evidence_assertion_id": evidence_id,
            "expected_bank_sha256": bank["bank_sha256"],
            "assessments": [
                {"world_id": worlds[0], "likelihood": 0.7},
                {"world_id": worlds[1], "likelihood": 0.3},
            ],
            "reason": "Apply one evidence factor exactly once.",
        }
        with self.assertRaises(LacunaError) as caught:
            self.cube.apply_operations(
                actor_id="user",
                operations=[
                    {**operation, "update_id": "pup.atomic.first"},
                    {**operation, "update_id": "pup.atomic.second"},
                ],
            )
        self.assertEqual(caught.exception.code, "particle-evidence-already-applied")
        self.assertEqual(self.cube.head(), before_head)
        self.assertEqual(self.cube.event_count(), before_count)
        self.assertEqual(self.cube.particle_updates(), [])
        self.assertEqual(
            [item["raw_weight"] for item in self.cube.particle_bank()["particles"]],
            [1.0, 1.0],
        )

    def test_projection_tamper_is_detected_and_rebuild_restores_receipt(self) -> None:
        evidence_id, worlds = self.seed()
        self.apply_update(evidence_id, {worlds[0]: 0.7, worlds[1]: 0.3})
        self.cube.conn.execute(
            "UPDATE particle_update_members SET likelihood = 0.2 WHERE update_id = 'pup.red-dust' AND world_id = ?",
            (worlds[0],),
        )
        self.cube.conn.commit()
        report = self.cube.verify()
        self.assertEqual(report["overall_status"], "fail")
        codes = {item["code"] for item in report["errors"]}
        self.assertIn("particle-update-member-projection-mismatch", codes)
        self.assertEqual(self.cube.rebuild_projections()["overall_status"], "pass")
        restored = self.cube.particle_updates()[0]["assessments"][0]
        self.assertEqual(restored["likelihood"], 0.7)

    def test_equivalent_valuations_with_different_likelihoods_are_surfaced(self) -> None:
        evidence_id, worlds = self.seed()
        latent_claim = deterministic_claim_id("visitor", "arrived_by", "river", "world")
        self.cube.apply_operations(
            actor_id="user",
            operations=[
                {
                    "op": "declare_claim",
                    "claim_id": latent_claim,
                    "subject": "visitor",
                    "predicate": "arrived_by",
                    "object": "river",
                    "scope": "world",
                },
                *[
                    {
                        "op": "assign_world",
                        "assignment_id": f"asn.same.{index}",
                        "world_id": world_id,
                        "claim_id": latent_claim,
                        "truth": "true",
                        "commitment": "tentative",
                        "rationale": "Same explicit valuation with distinct custody.",
                    }
                    for index, world_id in enumerate(worlds, start=1)
                ],
            ],
        )
        self.apply_update(evidence_id, {worlds[0]: 0.9, worlds[1]: 0.2})
        update = self.cube.particle_updates()[0]
        groups = update["valuation_likelihood_divergence_groups"]
        self.assertEqual(len(groups), 1)
        self.assertEqual(groups[0]["world_ids"], worlds)
        self.assertEqual(groups[0]["likelihoods"], [0.2, 0.9])
        self.assertEqual(self.cube.verify()["overall_status"], "pass")

    def test_particle_update_explanation_is_planner_only_and_traces_population(self) -> None:
        evidence_id, worlds = self.seed()
        self.apply_update(evidence_id, {worlds[0]: 0.6, worlds[1]: 0.4})
        explanation = self.cube.explain("pup.red-dust")
        self.assertEqual(explanation["target"]["kind"], "particle_update")
        links = {
            (item["kind"], item["id"], item["role"])
            for item in explanation["dependencies"]
        }
        self.assertIn(("assertion", evidence_id, "evidence_update"), links)
        for world_id in worlds:
            self.assertIn(("world", world_id, "assessed_particle"), links)
        with self.assertRaises(LacunaError) as caught:
            self.cube.explain("pup.red-dust", agent_id="user")
        self.assertEqual(caught.exception.code, "explanation-not-visible")

    def test_nonfinite_projection_tamper_is_reported_without_crashing_audit(self) -> None:
        evidence_id, worlds = self.seed()
        self.apply_update(evidence_id, {worlds[0]: 0.7, worlds[1]: 0.3})
        self.cube.conn.execute(
            """UPDATE particle_update_members
               SET posterior_probability = 'NaN'
               WHERE update_id = 'pup.red-dust' AND world_id = ?""",
            (worlds[0],),
        )
        self.cube.conn.commit()
        report = self.cube.verify()
        self.assertEqual(report["overall_status"], "fail")
        codes = {item["code"] for item in report["errors"]}
        self.assertIn("particle-update-member-nonfinite-number", codes)
        self.assertEqual(self.cube.rebuild_projections()["overall_status"], "pass")

    def test_context_firewall_exposes_bank_only_to_unscoped_planner(self) -> None:
        self.seed()
        audience = build_context(self.cube, agent_id="user")
        planner = build_context(self.cube)
        scoped = build_context(self.cube, world_id="world.1")
        self.assertIsNone(audience["particle_bank"])
        self.assertIn("particle_bank", audience["omitted"])
        self.assertEqual(planner["particle_bank"]["world_count"], 2)
        self.assertIsNone(scoped["particle_bank"])
        self.assertIn("complete-population", scoped["omitted"]["particle_bank"])

    def test_nested_world_aliases_are_resolved_for_model_proposals(self) -> None:
        operations, aliases = normalize_turn_operations(
            [
                {
                    "op": "create_world",
                    "as": "new.world",
                    "label": "New candidate",
                    "weight": 1.0,
                },
                {
                    "op": "update_particle_bank",
                    "as": "weight.update",
                    "evidence_assertion_id": "@evidence",
                    "expected_bank_sha256": "0" * 64,
                    "assessments": [
                        {"world_id": "@new.world", "likelihood": 0.4}
                    ],
                    "reason": "Alias normalization only.",
                },
            ],
            initial_aliases={"evidence": "ast.evidence"},
        )
        self.assertEqual(operations[1]["assessments"][0]["world_id"], aliases["new.world"])
        self.assertEqual(operations[1]["update_id"], aliases["weight.update"])
        self.assertEqual(operations[1]["evidence_assertion_id"], "ast.evidence")

    def test_unscoped_director_turn_can_apply_reviewed_particle_update(self) -> None:
        evidence_id, worlds = self.seed()
        packet = build_turn_packet(
            self.cube,
            audience_id="user",
            actor_id="user",
            player_input="Study the dust without collapsing the mystery.",
            director=True,
        )
        bank = packet["planner_context"]["particle_bank"]
        self.assertEqual(bank["head"], packet["expected_head"])
        proposal = dict(packet["response_contract"]["proposal_template"])
        proposal["narration"] = "The dust catches in the side-light, red as old brick."
        proposal["revealed_assertion_ids"] = []
        proposal["operations"] = [
            {
                "op": "update_particle_bank",
                "as": "dust.update",
                "evidence_assertion_id": evidence_id,
                "expected_bank_sha256": bank["bank_sha256"],
                "assessments": [
                    {"world_id": worlds[0], "likelihood": 0.75},
                    {"world_id": worlds[1], "likelihood": 0.25},
                ],
                "reason": "Use the observed dust to redistribute planning attention.",
            }
        ]
        receipt = commit_turn_proposal(self.cube, proposal)
        self.assertIn("dust.update", receipt["bindings"])
        probabilities = {
            item["world_id"]: item["probability"]
            for item in self.cube.particle_bank()["particles"]
        }
        self.assertEqual(probabilities, {worlds[0]: 0.75, worlds[1]: 0.25})

    def test_world_scoped_director_turn_cannot_mutate_global_particle_bank(self) -> None:
        evidence_id, worlds = self.seed()
        packet = build_turn_packet(
            self.cube,
            audience_id="user",
            actor_id="user",
            player_input="Remain inside one branch.",
            director=True,
            world_id=worlds[0],
        )
        proposal = dict(packet["response_contract"]["proposal_template"])
        proposal["narration"] = "The branch remains local."
        proposal["revealed_assertion_ids"] = []
        proposal["operations"] = [
            {
                "op": "update_particle_bank",
                "evidence_assertion_id": evidence_id,
                "expected_bank_sha256": self.cube.particle_bank()["bank_sha256"],
                "assessments": [
                    {"world_id": worlds[0], "likelihood": 0.5},
                    {"world_id": worlds[1], "likelihood": 0.5},
                ],
                "reason": "This should be refused by the scoped grant.",
            }
        ]
        with self.assertRaises(LacunaError) as caught:
            commit_turn_proposal(self.cube, proposal)
        self.assertEqual(caught.exception.code, "turn-world-scope-violation")

    def test_schema_five_migration_reaches_schema_seven_without_rewriting_head(self) -> None:
        before_head = self.cube.head()
        self.cube.close()
        self.cube = None
        db_path = self.root / "lacuna.sqlite3"
        conn = sqlite3.connect(db_path)
        try:
            conn.execute("DROP INDEX particle_update_members_world_idx")
            conn.execute("DROP TABLE particle_update_members")
            conn.execute("DROP INDEX particle_updates_evidence_idx")
            conn.execute("DROP TABLE particle_updates")
            conn.execute("DELETE FROM schema_migrations WHERE target_version >= 6")
            conn.execute("PRAGMA user_version = 5")
            conn.execute("UPDATE meta SET value = '5' WHERE key = 'schema_version'")
            conn.commit()
        finally:
            conn.close()
        receipt = Cube.migrate(self.root)
        self.assertEqual(receipt["source_version"], 5)
        self.assertEqual(receipt["target_version"], 8)
        self.assertEqual(receipt["before_head"], before_head)
        self.assertEqual(receipt["after_head"], before_head)
        self.cube = Cube.open(self.root)
        tables = {
            row["name"]
            for row in self.cube.conn.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            ).fetchall()
        }
        self.assertIn("particle_updates", tables)
        self.assertIn("particle_update_members", tables)
        self.assertEqual(self.cube.verify()["overall_status"], "pass")


if __name__ == "__main__":
    unittest.main()
