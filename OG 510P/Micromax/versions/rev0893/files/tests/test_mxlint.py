from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _load_mxlint_module():
    spec = importlib.util.spec_from_file_location("mxlint_test_module", ROOT / "tools" / "mxlint.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_mxlint_skips_bootstrap_caches_and_generated_artifacts(tmp_path, monkeypatch) -> None:
    module = _load_mxlint_module()
    monkeypatch.setattr(module, "ROOT", tmp_path)

    noisy_paths = [
        tmp_path / ".venv" / "lib" / "site-packages" / "dep.py",
        tmp_path / ".git" / "config",
        tmp_path / ".pytest_cache" / "v" / "cache" / "nodeids",
        tmp_path / ".mypy_cache" / "bad.json",
        tmp_path / ".ruff_cache" / "bad.txt",
        tmp_path / "__pycache__" / "mod.pyc",
        tmp_path / "build" / "generated.md",
        tmp_path / "dist" / "generated.md",
        tmp_path / "src" / "micromax.egg-info" / "SOURCES.txt",
        tmp_path / ".tmp-mxlint" / "scratch.md",
        tmp_path / "Micromax-rev0000-test.zip",
        tmp_path / ".editorconfig",
    ]
    for path in noisy_paths:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("third party or generated whitespace \n", encoding="utf-8")

    assert module.check_text_files() == 0


def test_mxlint_still_reports_repo_text_issues(tmp_path, monkeypatch, capsys) -> None:
    module = _load_mxlint_module()
    monkeypatch.setattr(module, "ROOT", tmp_path)

    bad = tmp_path / "docs" / "bad.md"
    bad.parent.mkdir(parents=True)
    bad.write_text("real repo whitespace \n", encoding="utf-8")

    assert module.check_text_files() == 1
    captured = capsys.readouterr()
    assert "TRAILING SPACE" in captured.err
    assert "docs" in captured.err
