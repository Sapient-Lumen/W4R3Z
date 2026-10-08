from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from lacuna import __version__
from lacuna.artifact import audit_release_artifact


class ArtifactAuditTests(unittest.TestCase):
    def build_release(self, parent: Path) -> Path:
        root = parent / "Lacuna-test"
        (root / "src/lacuna").mkdir(parents=True)
        (root / "docs").mkdir()
        files = {
            "pyproject.toml": (
                "[project]\n"
                f'name = "lacuna-test"\nversion = "{__version__}"\n'
            ),
            "src/lacuna/__init__.py": f'__version__ = "{__version__}"\n',
            "REVISION.json": json.dumps(
                {
                    "revision": "revtest",
                    "version": __version__,
                    "artifact_root": "Lacuna-test/",
                },
                sort_keys=True,
            )
            + "\n",
            "README.md": "# Test\n\n[Operator](docs/OPERATOR.md)\n",
            "docs/OPERATOR.md": "# Operator\n\n[Back](../README.md)\n",
            "sample.json": '{"ok": true}\n',
            "sample.toml": "ok = true\n",
            "tool.py": "answer = 42\n",
            "lacuna": (
                "#!/bin/sh\n"
                "set -eu\n"
                "export PYTHONDONTWRITEBYTECODE=1\n"
                "exec python3 -S -m lacuna.cli \"$@\"\n"
            ),
        }
        for relative, text in files.items():
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
        (root / "lacuna").chmod(0o755)
        lines = []
        for relative in sorted(files):
            digest = hashlib.sha256((root / relative).read_bytes()).hexdigest()
            lines.append(f"{digest}  {relative}")
        (root / "MANIFEST.sha256").write_text("\n".join(lines) + "\n", encoding="utf-8")
        return root

    def test_pristine_minimal_release_passes_strict_audit(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = self.build_release(Path(directory))
            report = audit_release_artifact(root, strict_members=True)
        self.assertEqual(report["overall_status"], "pass")
        self.assertEqual(report["counts"]["manifest_members"], 9)
        self.assertEqual(report["counts"]["markdown_relative_targets"], 2)

    def test_launcher_without_executable_mode_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = self.build_release(Path(directory))
            (root / "lacuna").chmod(0o644)
            report = audit_release_artifact(root, strict_members=True)
        self.assertEqual(report["overall_status"], "fail")
        launcher = next(item for item in report["checks"] if item["name"] == "launcher-contract")
        self.assertIn("owner-executable", " ".join(launcher["details"]["errors"]))

    def test_manifest_mismatch_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = self.build_release(Path(directory))
            (root / "README.md").write_text("changed\n", encoding="utf-8")
            report = audit_release_artifact(root, strict_members=True)
        self.assertEqual(report["overall_status"], "fail")
        member_check = next(item for item in report["checks"] if item["name"] == "manifest-members")
        self.assertIn("README.md", member_check["details"]["mismatched"])

    def test_unlisted_file_is_warning_by_default_and_failure_in_strict_mode(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = self.build_release(Path(directory))
            (root / "notes.txt").write_text("operator note\n", encoding="utf-8")
            relaxed = audit_release_artifact(root, strict_members=False)
            strict = audit_release_artifact(root, strict_members=True)
        self.assertEqual(relaxed["overall_status"], "pass")
        self.assertTrue(relaxed["warnings"])
        self.assertEqual(strict["overall_status"], "fail")


if __name__ == "__main__":
    unittest.main()
