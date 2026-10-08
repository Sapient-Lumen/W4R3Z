from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[1]


def test_sandclaude_installer_writes_isolated_chrome_for_testing_manifest(tmp_path: Path) -> None:
    env = os.environ.copy()
    env["HOME"] = os.fspath(tmp_path)
    result = subprocess.run(
        [os.fspath(ROOT / "scripts" / "install-sandclaude.sh")],
        cwd=ROOT,
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )
    manifest_path = (
        tmp_path
        / ".config"
        / "google-chrome-for-testing"
        / "NativeMessagingHosts"
        / "com.glasstty.bridge.json"
    )
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["name"] == "com.glasstty.bridge"
    assert manifest["path"] == os.fspath(ROOT / "scripts" / "native-host-entrypoint.sh")
    assert manifest["allowed_origins"] == [
        "chrome-extension://afmmlmjnbbcapinmhhhhbcoanfckdbfh/"
    ]
    assert "GlassTTY native host ready" in result.stdout


def test_project_cli_runs_without_package_install() -> None:
    result = subprocess.run(
        [os.fspath(ROOT / "glassttyd"), "--help"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    assert "ask" in result.stdout
    assert "first-flight" in result.stdout
