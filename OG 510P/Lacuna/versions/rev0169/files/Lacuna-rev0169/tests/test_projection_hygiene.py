from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from lacuna.store import Cube


class ParticleProjectionHygieneTests(unittest.TestCase):
    def test_orphan_particle_rows_are_detected_and_rebuild_removes_them(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            cube = Cube.init(Path(temporary) / "cube")
            try:
                head = cube.head()
                # Simulate a private extension writing event-owned projection state
                # without the corresponding immutable particle.updated event.
                cube.conn.execute("PRAGMA foreign_keys = OFF")
                cube.conn.execute(
                    """INSERT INTO particle_updates(
                           update_id, evidence_assertion_id, method,
                           prior_bank_sha256, posterior_bank_sha256,
                           prior_weight_sum, normalization_constant,
                           prior_effective_sample_size, posterior_effective_sample_size,
                           prior_entropy_nats, posterior_entropy_nats,
                           information_gain_nats, reason, created_seq
                       ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        "upd_unsupported",
                        "ast_missing",
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
                        "No origin event owns this row.",
                        1,
                    ),
                )
                cube.conn.commit()
                cube.conn.execute("PRAGMA foreign_keys = ON")

                verification = cube.verify()
                self.assertEqual(verification["overall_status"], "fail")
                self.assertIn(
                    "particle-update-origin-event",
                    {item["code"] for item in verification["errors"]},
                )

                rebuilt = cube.rebuild_projections()
                self.assertEqual(rebuilt["overall_status"], "pass")
                self.assertEqual(cube.head(), head)
                self.assertEqual(
                    cube.conn.execute("SELECT COUNT(*) FROM particle_updates").fetchone()[0],
                    0,
                )
            finally:
                cube.close()


if __name__ == "__main__":
    unittest.main()
