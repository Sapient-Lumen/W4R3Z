from __future__ import annotations

import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from lacuna import __version__


REQUIRED_ENTRANCES = (
    "PLAY_NOW.md",
    "FOR_GWERN.md",
    "OPERATE_LACUNA.md",
    "START_HERE.md",
    "README.md",
)


class ReleaseSurfaceTests(unittest.TestCase):
    def test_required_gift_entrances_exist_and_are_manifested(self) -> None:
        manifest_path = ROOT / "MANIFEST.sha256"
        self.assertTrue(manifest_path.is_file(), "release manifest is missing")
        manifested = {
            line.split("  ", 1)[1]
            for line in manifest_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        }
        for relative in REQUIRED_ENTRANCES:
            with self.subTest(relative=relative):
                self.assertTrue((ROOT / relative).is_file())
                self.assertIn(relative, manifested)

    def test_start_here_routes_player_researcher_and_operator_before_reference(self) -> None:
        text = (ROOT / "START_HERE.md").read_text(encoding="utf-8")
        player = text.index("PLAY_NOW.md")
        researcher = text.index("FOR_GWERN.md")
        operator = text.index("OPERATE_LACUNA.md")
        reference = text.index("## One-sentence model")
        self.assertLess(max(player, researcher, operator), reference)

    def test_revision_runtime_and_artifact_identity_agree(self) -> None:
        revision = json.loads((ROOT / "REVISION.json").read_text(encoding="utf-8"))
        self.assertEqual(revision["revision"], "rev0169")
        self.assertEqual(revision["version"], __version__)
        self.assertEqual(revision["artifact_root"], "Lacuna-rev0169/")
        filename = revision["artifact_filename"]
        self.assertRegex(
            filename,
            r"^Lacuna-rev0169-\d{4}\.\d{2}\.\d{2}-[a-z0-9-]+\.zip$",
        )
        self.assertNotRegex(filename, re.compile(r"(?:candidate|preliminary)", re.I))


    def test_root_readme_current_revision_summary_is_not_stale(self) -> None:
        revision = json.loads((ROOT / "REVISION.json").read_text(encoding="utf-8"))
        text = (ROOT / "README.md").read_text(encoding="utf-8")
        opening = text.split("## Governing distinctions", 1)[0]
        self.assertIn(revision["revision"], opening)
        self.assertNotIn("Rev0166 makes", opening)
        self.assertNotIn("rev0165’s stronger", opening)
        self.assertIn("send-ready polish", opening.lower())

    def test_release_acceptance_contains_no_pending_package_markers(self) -> None:
        acceptance = json.loads(
            (ROOT / "docs" / "acceptance" / "ACCEPTANCE_rev0169.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(acceptance["status"], "pass")
        serialized = json.dumps(acceptance, sort_keys=True).lower()
        self.assertNotIn("pending final package verification", serialized)
        self.assertNotIn("pending final clean-extraction", serialized)


if __name__ == "__main__":
    unittest.main()
