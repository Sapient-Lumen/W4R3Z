import subprocess
import unittest
from pathlib import Path


class StatusCliTests(unittest.TestCase):
    def test_status_uses_scientific_labels(self) -> None:
        proc = subprocess.run(
            ["python3", "-m", "grlab", "status"],
            cwd=str(Path(__file__).resolve().parents[2]),
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0)
        self.assertIn("Candidates:", proc.stdout)
        self.assertIn("Adversaries:", proc.stdout)


if __name__ == "__main__":
    unittest.main()
