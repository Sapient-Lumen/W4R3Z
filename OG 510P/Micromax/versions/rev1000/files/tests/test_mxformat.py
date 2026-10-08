from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _load_mxformat_module():
    spec = importlib.util.spec_from_file_location("mxformat_test_module", ROOT / "tools" / "mxformat.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_mxformat_skips_bootstrap_caches_and_generated_artifacts(tmp_path, monkeypatch) -> None:
    module = _load_mxformat_module()
    monkeypatch.setattr(module, "ROOT", tmp_path)

    skipped = tmp_path / ".venv" / "lib" / "site-packages" / "dep.py"
    skipped.parent.mkdir(parents=True)
    skipped.write_text("third party whitespace \n", encoding="utf-8")

    archive = tmp_path / "Micromax-rev0000-test.zip"
    archive.write_text("generated whitespace \n", encoding="utf-8")

    egg_info = tmp_path / "src" / "micromax.egg-info" / "SOURCES.txt"
    egg_info.parent.mkdir(parents=True)
    egg_info.write_text("generated wheel metadata whitespace \n", encoding="utf-8")

    assert module.whitespace_format() == 0
    assert skipped.read_text(encoding="utf-8") == "third party whitespace \n"
    assert archive.read_text(encoding="utf-8") == "generated whitespace \n"
    assert egg_info.read_text(encoding="utf-8") == "generated wheel metadata whitespace \n"


def test_mxformat_formats_repo_text_files(tmp_path, monkeypatch) -> None:
    module = _load_mxformat_module()
    monkeypatch.setattr(module, "ROOT", tmp_path)

    note = tmp_path / "docs" / "note.md"
    note.parent.mkdir(parents=True)
    note.write_text("hello \r\nworld", encoding="utf-8")

    assert module.whitespace_format() == 0
    assert note.read_text(encoding="utf-8") == "hello\nworld\n"
