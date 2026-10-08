import json
import subprocess
import tempfile
import unittest
from pathlib import Path


class CertifyCliTests(unittest.TestCase):
    def test_certify_memory_one_pair(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            a = root / "a.json"
            b = root / "b.json"
            a.write_text(
                json.dumps(
                    {
                        "family": "memory_one",
                        "id": "a",
                        "p0": 1.0,
                        "p_cc": 1.0,
                        "p_cd": 1.0,
                        "p_dc": 1.0,
                        "p_dd": 1.0,
                    }
                ),
                encoding="utf-8",
            )
            b.write_text(
                json.dumps(
                    {
                        "family": "memory_one",
                        "id": "b",
                        "p0": 0.0,
                        "p_cc": 0.0,
                        "p_cd": 0.0,
                        "p_dc": 0.0,
                        "p_dd": 0.0,
                    }
                ),
                encoding="utf-8",
            )

            proc = subprocess.run(
                ["python3", "-m", "grlab", "certify", "--a", str(a), "--b", str(b)],
                cwd=str(Path(__file__).resolve().parents[2]),
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(proc.returncode, 0, msg=proc.stderr)
            payload = json.loads(proc.stdout)
            self.assertAlmostEqual(payload["avg_payoff_a"], 0.0, places=9)
            self.assertAlmostEqual(payload["avg_payoff_b"], 5.0, places=9)


if __name__ == "__main__":
    unittest.main()
