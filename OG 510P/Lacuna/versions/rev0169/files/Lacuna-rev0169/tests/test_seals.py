from __future__ import annotations

import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from lacuna.context import build_context
from lacuna.errors import LacunaError
from lacuna.seals import parse_seal_opening, prepare_seal_opening, seal_commitment_sha256
from lacuna.store import Cube
from lacuna.turns import build_turn_packet, commit_turn_proposal
from lacuna.util import canonical_json, sha256_text


class FairPlaySealTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name) / "cube"
        self.cube: Cube | None = Cube.init(self.root)

    def tearDown(self) -> None:
        if self.cube is not None:
            self.cube.close()
        self.temporary.cleanup()

    @property
    def live_cube(self) -> Cube:
        assert self.cube is not None
        return self.cube

    def opening(
        self,
        *,
        seal_id: str = "seal_culprit",
        payload: object | None = None,
        nonce: str = "01" * 32,
    ) -> dict:
        return prepare_seal_opening(
            cube_id=self.live_cube.meta("cube_id"),
            seal_id=seal_id,
            payload={"culprit": "Ada", "method": "glass key"}
            if payload is None
            else payload,
            nonce=nonce,
        )

    def seal_operation(
        self,
        opening: dict,
        *,
        visibility: str = "public",
        audience: list[str] | None = None,
        source_id: str | None = None,
    ) -> dict:
        return {
            "op": "seal_precommitment",
            "seal_id": opening["seal_id"],
            "commitment_sha256": opening["commitment_sha256"],
            "scheme": opening["scheme"],
            "label": "Authored culprit",
            "purpose": "mystery",
            "visibility": visibility,
            "audience": audience or [],
            "source_id": source_id,
        }

    def test_commitment_is_domain_bound_and_rejects_nonportable_payloads(self) -> None:
        payload = {"answer": ["Ada", 7, True, None]}
        digest = seal_commitment_sha256(
            cube_id=self.live_cube.meta("cube_id"),
            seal_id="seal_a",
            payload=payload,
            nonce="ab" * 32,
        )
        self.assertNotEqual(
            digest,
            seal_commitment_sha256(
                cube_id=self.live_cube.meta("cube_id"),
                seal_id="seal_b",
                payload=payload,
                nonce="ab" * 32,
            ),
        )
        with self.assertRaises(LacunaError) as float_error:
            self.opening(payload={"probability": 0.5})
        self.assertEqual(float_error.exception.code, "seal-payload-float")
        with self.assertRaises(LacunaError) as integer_error:
            self.opening(payload={"number": 2**53})
        self.assertEqual(integer_error.exception.code, "seal-payload-unsafe-integer")
        with self.assertRaises(LacunaError) as string_error:
            self.opening(payload={"bad": "\ud800"})
        self.assertEqual(string_error.exception.code, "seal-payload-unicode-scalar")
        with self.assertRaises(LacunaError) as key_error:
            self.opening(payload={"\udfff": "bad key"})
        self.assertEqual(key_error.exception.code, "seal-payload-unicode-scalar")

    def test_opening_parser_requires_the_full_custody_envelope(self) -> None:
        opening = self.opening()
        self.assertEqual(parse_seal_opening(opening)["payload"], opening["payload"])
        for field in ("event", "custody_warning"):
            malformed = dict(opening)
            malformed.pop(field)
            with self.assertRaises(LacunaError) as caught:
                parse_seal_opening(malformed)
            self.assertEqual(caught.exception.code, "bad-seal-opening")
        wrong_event = dict(opening)
        wrong_event["event"] = "lacuna.seal.opening.forged"
        with self.assertRaises(LacunaError) as caught:
            parse_seal_opening(wrong_event)
        self.assertEqual(caught.exception.code, "bad-seal-opening")

    def test_seal_and_reveal_cannot_collapse_into_one_change_and_no_secret_is_stored(self) -> None:
        opening = self.opening()
        before_head = self.live_cube.head()
        before_count = self.live_cube.event_count()
        with self.assertRaises(LacunaError) as caught:
            self.live_cube.apply_operations(
                actor_id="user",
                operations=[
                    self.seal_operation(opening),
                    {
                        "op": "reveal_precommitment",
                        "seal_id": opening["seal_id"],
                        "nonce": opening["nonce"],
                        "payload": opening["payload"],
                        "reason": "An invalid immediate reveal.",
                    },
                ],
            )
        self.assertEqual(caught.exception.code, "seal-phase-not-committed")
        self.assertEqual(self.live_cube.head(), before_head)
        self.assertEqual(self.live_cube.event_count(), before_count)
        self.assertEqual(self.live_cube.seals(), [])

        self.live_cube.apply_operations(
            actor_id="user", operations=[self.seal_operation(opening)]
        )
        sealed_event = self.live_cube.events()[-1]
        self.assertEqual(sealed_event["event_type"], "precommitment.sealed")
        self.assertNotIn("nonce", sealed_event["payload"])
        self.assertNotIn("payload", sealed_event["payload"])
        serialized_ledger = json.dumps(self.live_cube.events(), sort_keys=True)
        self.assertNotIn("glass key", serialized_ledger)
        row = self.live_cube.conn.execute(
            "SELECT * FROM fair_play_seals WHERE seal_id = ?", (opening["seal_id"],)
        ).fetchone()
        assert row is not None
        self.assertIsNone(row["reveal_payload_json"])
        self.assertIsNone(row["reveal_nonce"])
        receipt = self.live_cube.seal_receipt(opening["seal_id"])
        self.assertIsNone(receipt["opening"])
        self.assertNotIn("glass key", json.dumps(receipt, sort_keys=True))
        self.assertEqual(
            receipt["receipt_sha256"],
            sha256_text(canonical_json(receipt["receipt_core"])),
        )

    def test_wrong_opening_refuses_then_exact_opening_reveals_and_verifies(self) -> None:
        opening = self.opening()
        self.live_cube.apply_operations(
            actor_id="user", operations=[self.seal_operation(opening)]
        )
        wrong = self.opening(payload={"culprit": "Basil"}, nonce="02" * 32)
        report = self.live_cube.verify_seal_opening(wrong)
        self.assertEqual(report["overall_status"], "fail")
        self.assertFalse(report["checks"]["commitment_digest_matches"])
        with self.assertRaises(LacunaError) as caught:
            self.live_cube.apply_operations(
                actor_id="user",
                operations=[
                    {
                        "op": "reveal_precommitment",
                        "seal_id": wrong["seal_id"],
                        "nonce": wrong["nonce"],
                        "payload": wrong["payload"],
                        "reason": "Try the wrong answer.",
                    }
                ],
            )
        self.assertEqual(caught.exception.code, "seal-opening-mismatch")

        anchored_receipt = self.live_cube.seal_receipt(opening["seal_id"])
        self.live_cube.apply_operations(
            actor_id="user",
            operations=[
                {
                    "op": "reveal_precommitment",
                    "seal_id": opening["seal_id"],
                    "nonce": opening["nonce"],
                    "payload": opening["payload"],
                    "reason": "The investigation reached its authored reveal.",
                }
            ],
        )
        seal = self.live_cube.seal(opening["seal_id"])
        self.assertEqual(seal["status"], "revealed")
        self.assertEqual(seal["reveal_payload"], opening["payload"])
        report = self.live_cube.verify_seal_opening(opening)
        self.assertEqual(report["overall_status"], "pass")
        self.assertTrue(report["checks"]["opening_matches_recorded_reveal"])
        receipt = self.live_cube.seal_receipt(opening["seal_id"])
        self.assertEqual(receipt["opening"]["payload"], opening["payload"])
        self.assertEqual(receipt["receipt_sha256"], anchored_receipt["receipt_sha256"])
        self.assertEqual(receipt["receipt_core"], anchored_receipt["receipt_core"])
        self.assertEqual(
            receipt["commitment_event"]["event_hash"],
            self.live_cube.events(since_seq=3)[0]["event_hash"],
        )
        status = self.live_cube.status()
        self.assertEqual(status["revealed_precommitment_count"], 1)
        self.assertEqual(status["sealed_precommitment_count"], 0)
        self.assertEqual(self.live_cube.verify()["overall_status"], "pass")

    def test_restricted_visibility_crosses_context_but_not_hidden_source_graph(self) -> None:
        self.live_cube.apply_operations(
            actor_id="user",
            operations=[
                {
                    "op": "register_agent",
                    "agent_id": "player",
                    "kind": "human",
                    "label": "Player",
                },
                {
                    "op": "register_agent",
                    "agent_id": "outsider",
                    "kind": "human",
                    "label": "Outsider",
                },
                {
                    "op": "add_source",
                    "source_id": "src_secret_notes",
                    "kind": "document",
                    "label": "Private author notes",
                    "locator": "file:///private/culprit.txt",
                    "metadata": {"sensitive": True},
                },
            ],
        )
        opening = self.opening()
        self.live_cube.apply_operations(
            actor_id="user",
            operations=[
                self.seal_operation(
                    opening,
                    visibility="restricted",
                    audience=["player"],
                    source_id="src_secret_notes",
                )
            ],
        )
        player = self.live_cube.perspective("player")
        outsider = self.live_cube.perspective("outsider")
        self.assertEqual([item["seal_id"] for item in player["fair_play_seals"]], ["seal_culprit"])
        self.assertEqual(outsider["fair_play_seals"], [])
        self.assertNotIn("source_id", player["fair_play_seals"][0])
        context = build_context(self.live_cube, agent_id="player")
        self.assertEqual(context["fair_play_seals"][0]["status"], "sealed")
        self.assertEqual(build_context(self.live_cube, agent_id="outsider")["fair_play_seals"], [])
        explanation = self.live_cube.explain("seal_culprit", agent_id="player")
        self.assertIsNone(explanation["target"]["record"]["source_id"])
        self.assertEqual(explanation["dependencies"], [])
        with self.assertRaises(LacunaError) as caught:
            self.live_cube.explain("seal_culprit", agent_id="outsider")
        self.assertEqual(caught.exception.code, "explanation-not-visible")
        planner = self.live_cube.explain("seal_culprit")
        self.assertEqual(planner["target"]["record"]["source_id"], "src_secret_notes")
        self.assertEqual(planner["dependencies"][0]["id"], "src_secret_notes")

    def test_void_is_terminal_and_preserves_reason_without_opening(self) -> None:
        opening = self.opening()
        self.live_cube.apply_operations(
            actor_id="user", operations=[self.seal_operation(opening)]
        )
        self.live_cube.apply_operations(
            actor_id="user",
            operations=[
                {
                    "op": "void_precommitment",
                    "seal_id": opening["seal_id"],
                    "reason": "The scenario was retired before play.",
                }
            ],
        )
        self.assertEqual(self.live_cube.seal(opening["seal_id"])["status"], "voided")
        with self.assertRaises(LacunaError) as caught:
            self.live_cube.apply_operations(
                actor_id="user",
                operations=[
                    {
                        "op": "reveal_precommitment",
                        "seal_id": opening["seal_id"],
                        "nonce": opening["nonce"],
                        "payload": opening["payload"],
                        "reason": "Too late.",
                    }
                ],
            )
        self.assertEqual(caught.exception.code, "resolved-precommitment-seal")
        receipt = self.live_cube.seal_receipt(opening["seal_id"])
        self.assertIsNone(receipt["opening"])
        self.assertEqual(receipt["resolution"]["status"], "voided")
        self.assertEqual(self.live_cube.status()["voided_precommitment_count"], 1)

    def test_projection_tamper_is_detected_and_rebuild_restores_opening(self) -> None:
        opening = self.opening()
        self.live_cube.apply_operations(
            actor_id="user", operations=[self.seal_operation(opening)]
        )
        self.live_cube.apply_operations(
            actor_id="user",
            operations=[
                {
                    "op": "reveal_precommitment",
                    "seal_id": opening["seal_id"],
                    "nonce": opening["nonce"],
                    "payload": opening["payload"],
                    "reason": "Reveal.",
                }
            ],
        )
        head = self.live_cube.head()
        self.live_cube.conn.execute(
            "UPDATE fair_play_seals SET reveal_payload_json = ? WHERE seal_id = ?",
            (json.dumps({"culprit": "Basil"}), opening["seal_id"]),
        )
        self.live_cube.conn.commit()
        verification = self.live_cube.verify()
        self.assertEqual(verification["overall_status"], "fail")
        codes = {item["code"] for item in verification["errors"]}
        self.assertTrue(
            {"seal-reveal-projection-mismatch", "seal-reveal-digest"} <= codes
        )
        rebuilt = self.live_cube.rebuild_projections()
        self.assertEqual(rebuilt["overall_status"], "pass")
        self.assertEqual(self.live_cube.head(), head)
        self.assertEqual(
            self.live_cube.seal(opening["seal_id"])["reveal_payload"],
            opening["payload"],
        )

    def test_schema_five_migration_adds_seals_without_rewriting_head(self) -> None:
        before_head = self.live_cube.head()
        self.live_cube.close()
        self.cube = None
        db_path = self.root / "lacuna.sqlite3"
        conn = sqlite3.connect(db_path)
        try:
            conn.execute("DROP INDEX fair_play_seals_status_idx")
            conn.execute("DROP TABLE fair_play_seals")
            conn.execute("DELETE FROM schema_migrations WHERE target_version >= 6")
            conn.execute("PRAGMA user_version = 5")
            conn.execute("UPDATE meta SET value = '5' WHERE key = 'schema_version'")
            conn.commit()
        finally:
            conn.close()

        with self.assertRaises(LacunaError) as caught:
            Cube.open(self.root)
        self.assertEqual(caught.exception.code, "database-migration-required")
        receipt = Cube.migrate(self.root)
        self.assertEqual(receipt["source_version"], 5)
        self.assertEqual(receipt["target_version"], 8)
        self.assertEqual(receipt["before_head"], before_head)
        self.assertEqual(receipt["after_head"], before_head)
        self.cube = Cube.open(self.root)
        tables = {
            row["name"]
            for row in self.live_cube.conn.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            ).fetchall()
        }
        self.assertIn("fair_play_seals", tables)
        self.assertEqual(self.live_cube.verify()["overall_status"], "pass")

    def test_director_turn_is_not_a_secret_custodian(self) -> None:
        self.live_cube.apply_operations(
            actor_id="user",
            operations=[
                {
                    "op": "register_agent",
                    "agent_id": "player",
                    "kind": "human",
                    "label": "Player",
                },
                {
                    "op": "register_agent",
                    "agent_id": "narrator",
                    "kind": "narrator",
                    "label": "Narrator",
                },
            ],
        )
        packet = build_turn_packet(
            self.live_cube,
            audience_id="player",
            actor_id="narrator",
            player_input="Begin the mystery.",
            director=True,
        )
        self.assertNotIn("seal_precommitment", packet["write_grant"]["allowed_operations"])
        proposal = dict(packet["response_contract"]["proposal_template"])
        proposal["narration"] = "The case begins."
        proposal["revealed_assertion_ids"] = []
        proposal["operations"] = [
            {
                "op": "seal_precommitment",
                "seal_id": "seal_illicit",
                "commitment_sha256": "a" * 64,
                "label": "Illicit model seal",
                "purpose": "mystery",
            }
        ]
        with self.assertRaises(LacunaError) as caught:
            commit_turn_proposal(self.live_cube, proposal)
        self.assertEqual(caught.exception.code, "turn-operation-not-granted")
        self.assertEqual(self.live_cube.seals(), [])


if __name__ == "__main__":
    unittest.main()
