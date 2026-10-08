from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from lacuna.errors import LacunaError
from lacuna.store import Cube
from lacuna.util import deterministic_claim_id, utc_now


LEGACY_PARTICLE_TABLES = """
CREATE TABLE particle_updates (
    update_id TEXT PRIMARY KEY,
    evidence_assertion_id TEXT NOT NULL REFERENCES assertions(assertion_id),
    method TEXT NOT NULL,
    prior_bank_sha256 TEXT NOT NULL,
    posterior_bank_sha256 TEXT NOT NULL,
    prior_weight_sum REAL NOT NULL,
    normalization_constant REAL NOT NULL,
    prior_effective_sample_size REAL NOT NULL,
    posterior_effective_sample_size REAL NOT NULL,
    prior_entropy_nats REAL NOT NULL,
    posterior_entropy_nats REAL NOT NULL,
    information_gain_nats REAL NOT NULL,
    reason TEXT NOT NULL,
    created_seq INTEGER NOT NULL
);
CREATE INDEX particle_updates_evidence_idx
    ON particle_updates(evidence_assertion_id, created_seq);
CREATE TABLE particle_update_members (
    update_id TEXT NOT NULL REFERENCES particle_updates(update_id),
    world_id TEXT NOT NULL REFERENCES worlds(world_id),
    ordinal INTEGER NOT NULL,
    prior_weight REAL NOT NULL,
    prior_probability REAL NOT NULL,
    likelihood REAL NOT NULL,
    unnormalized_weight REAL NOT NULL,
    posterior_probability REAL NOT NULL,
    rationale TEXT,
    valuation_sha256 TEXT NOT NULL,
    custody_sha256 TEXT NOT NULL,
    PRIMARY KEY(update_id, world_id),
    UNIQUE(update_id, ordinal)
);
CREATE INDEX particle_update_members_world_idx
    ON particle_update_members(world_id, update_id);
"""


class SchemaLineageTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name) / "cube"
        self.cube = Cube.init(self.root)

    def tearDown(self) -> None:
        if self.cube is not None:
            self.cube.close()
        self.temporary.cleanup()

    def _mark_schema_six(self, conn: sqlite3.Connection) -> None:
        conn.execute("DELETE FROM schema_migrations")
        conn.execute(
            """INSERT INTO schema_migrations(
                   target_version, source_version, applied_at, runtime_version, migration_sha256
               ) VALUES (6, 0, ?, '0.151.0', ?)""",
            (utc_now(), "0" * 64),
        )
        conn.execute("PRAGMA user_version = 6")
        conn.execute("UPDATE meta SET value = '6' WHERE key = 'schema_version'")

    def test_fresh_schema_six_dormant_shape_migrates_to_canonical_schema_seven(self) -> None:
        before_head = self.cube.head()
        self.cube.close()
        self.cube = None
        conn = sqlite3.connect(self.root / "lacuna.sqlite3")
        try:
            conn.execute("DROP TABLE particle_update_members")
            conn.execute("DROP TABLE particle_updates")
            conn.executescript(LEGACY_PARTICLE_TABLES)
            self._mark_schema_six(conn)
            conn.commit()
        finally:
            conn.close()

        receipt = Cube.migrate(self.root)
        self.assertEqual(receipt["source_version"], 6)
        self.assertEqual(receipt["target_version"], 8)
        self.assertEqual(receipt["before_head"], before_head)
        self.assertEqual(receipt["after_head"], before_head)
        self.assertEqual(len(receipt["steps"]), 2)
        self.cube = Cube.open(self.root)
        member_columns = {
            row["name"]
            for row in self.cube.conn.execute(
                "PRAGMA table_info(particle_update_members)"
            ).fetchall()
        }
        self.assertIn("world_status", member_columns)
        indexes = {
            row["name"]
            for row in self.cube.conn.execute(
                "PRAGMA index_list(particle_updates)"
            ).fetchall()
        }
        self.assertIn("particle_updates_evidence_unique_idx", indexes)
        self.assertEqual(self.cube.verify()["overall_status"], "pass")

    def test_migrated_schema_six_without_particle_tables_reaches_seven(self) -> None:
        before_head = self.cube.head()
        self.cube.close()
        self.cube = None
        conn = sqlite3.connect(self.root / "lacuna.sqlite3")
        try:
            conn.execute("DROP TABLE particle_update_members")
            conn.execute("DROP TABLE particle_updates")
            self._mark_schema_six(conn)
            conn.commit()
        finally:
            conn.close()

        receipt = Cube.migrate(self.root)
        self.assertEqual(receipt["source_version"], 6)
        self.assertEqual(receipt["target_version"], 8)
        self.assertEqual(receipt["before_head"], before_head)
        self.assertEqual(receipt["after_head"], before_head)
        self.cube = Cube.open(self.root)
        self.assertEqual(self.cube.verify()["overall_status"], "pass")

    def test_schema_seven_migration_refuses_nonempty_unowned_particle_rows(self) -> None:
        claim_id = deterministic_claim_id("lint", "found", True, "event")
        self.cube.apply_operations(
            actor_id="user",
            operations=[
                {
                    "op": "declare_claim",
                    "claim_id": claim_id,
                    "subject": "lint",
                    "predicate": "found",
                    "object": True,
                    "scope": "event",
                },
                {
                    "op": "record_assertion",
                    "assertion_id": "ast.lint",
                    "claim_id": claim_id,
                    "assertor_id": "user",
                    "stance": "true",
                    "basis": "observation",
                    "standing": "accepted",
                    "visibility": "private",
                },
            ],
        )
        before_head = self.cube.head()
        self.cube.close()
        self.cube = None
        db_path = self.root / "lacuna.sqlite3"
        conn = sqlite3.connect(db_path)
        try:
            conn.execute(
                """INSERT INTO particle_updates(
                       update_id, evidence_assertion_id, method,
                       prior_bank_sha256, posterior_bank_sha256,
                       prior_weight_sum, normalization_constant,
                       prior_effective_sample_size, posterior_effective_sample_size,
                       prior_entropy_nats, posterior_entropy_nats,
                       information_gain_nats, reason, created_seq
                   ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    "pup.unowned",
                    "ast.lint",
                    "private-extension",
                    "1" * 64,
                    "2" * 64,
                    1.0,
                    1.0,
                    1.0,
                    1.0,
                    0.0,
                    0.0,
                    0.0,
                    "Projection row without official event custody.",
                    1,
                ),
            )
            self._mark_schema_six(conn)
            conn.commit()
        finally:
            conn.close()

        with self.assertRaises(LacunaError) as caught:
            Cube.migrate(self.root)
        self.assertEqual(caught.exception.code, "migration-preflight-failed")
        self.assertEqual(caught.exception.details["code"], "unowned-particle-projection-rows")

        conn = sqlite3.connect(db_path)
        try:
            self.assertEqual(conn.execute("PRAGMA user_version").fetchone()[0], 6)
            self.assertEqual(
                conn.execute("SELECT COUNT(*) FROM particle_updates").fetchone()[0],
                1,
            )
            self.assertEqual(
                conn.execute("SELECT value FROM meta WHERE key = 'head'").fetchone()[0],
                before_head,
            )
        finally:
            conn.close()


if __name__ == "__main__":
    unittest.main()
