from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from lacuna.campaigns import CampaignLibrary, resolve_cube_reference
from lacuna.errors import LacunaError
from lacuna.store import Cube


class CampaignLibraryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name) / "stories"

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_first_campaign_is_selected_and_is_a_real_cube(self) -> None:
        library = CampaignLibrary.ensure(self.root)
        campaign = library.create_campaign(
            slug="lantern-room",
            title="The Lantern Room",
            summary="Three explanations survive the bell.",
        )
        self.assertTrue(campaign["selected"])
        self.assertEqual(resolve_cube_reference(self.root), Path(campaign["path"]))
        with Cube.open(campaign["path"]) as cube:
            status = cube.status()
            self.assertEqual(status["agent_count"], 4)
            perspective = cube.perspective("player")
            self.assertEqual(perspective["agent_id"], "player")
            cube._require_agent("narrator", "narrator")
            self.assertEqual(cube.verify()["overall_status"], "pass")

    def test_campaigns_are_pickable_by_slug_and_selection_changes_resolution(self) -> None:
        library = CampaignLibrary.ensure(self.root)
        first = library.create_campaign(slug="first", title="First")
        second = library.create_campaign(slug="second", title="Second")
        self.assertEqual(library.resolve()["campaign_id"], first["campaign_id"])
        receipt = library.select("second")
        self.assertEqual(receipt["campaign"]["campaign_id"], second["campaign_id"])
        reopened = CampaignLibrary.open(self.root)
        self.assertEqual(reopened.resolve()["slug"], "second")
        self.assertEqual(resolve_cube_reference(self.root), Path(second["path"]))

    def test_bad_slug_cannot_escape_campaign_directory(self) -> None:
        library = CampaignLibrary.ensure(self.root)
        with self.assertRaises(LacunaError) as caught:
            library.create_campaign(slug="../escape", title="No")
        self.assertEqual(caught.exception.code, "bad-campaign-input")
        self.assertFalse((self.root.parent / "escape").exists())

    def test_library_refuses_nonempty_overlay(self) -> None:
        self.root.mkdir(parents=True)
        (self.root / "unrelated.txt").write_text("do not clobber", encoding="utf-8")
        with self.assertRaises(LacunaError) as caught:
            CampaignLibrary.ensure(self.root)
        self.assertEqual(caught.exception.code, "not-a-library")

    def test_unknown_manifest_fields_are_refused(self) -> None:
        library = CampaignLibrary.ensure(self.root)
        campaign = library.create_campaign(slug="clean", title="Clean")
        manifest_path = Path(campaign["path"]) / "campaign.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["mystery_typo"] = True
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        with self.assertRaises(LacunaError) as caught:
            CampaignLibrary.open(self.root).campaigns()
        self.assertEqual(caught.exception.code, "unexpected-campaign-field")


if __name__ == "__main__":
    unittest.main()
