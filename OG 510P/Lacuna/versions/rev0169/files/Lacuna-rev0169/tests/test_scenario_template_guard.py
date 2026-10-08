from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from lacuna.errors import LacunaError
from lacuna.scenarios import begin_scenario_run, build_scenario_capsule_template
from lacuna.store import Cube


class ScenarioCapsuleTemplateGuardTests(unittest.TestCase):
    def test_begin_refuses_unedited_generated_template_before_run_root_creation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            seed_path = root / "unedited-seed"
            run_root = root / "unedited-template-run"
            with Cube.init(seed_path) as cube:
                capsule = build_scenario_capsule_template(cube)
                with self.assertRaises(LacunaError) as caught:
                    begin_scenario_run(
                        cube,
                        capsule,
                        reference=str(seed_path),
                        resolved_seed_cube_path=str(seed_path.resolve()),
                        root=run_root,
                    )
            self.assertEqual(caught.exception.code, "scenario-capsule-template-not-edited")
            self.assertFalse(run_root.exists())


if __name__ == "__main__":
    unittest.main()
