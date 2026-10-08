from __future__ import annotations

from pathlib import Path

from micromax_editor.editor import Editor


def test_cd_expands_tilde_and_reports_errors(tmp_path, monkeypatch) -> None:
    # Make expanduser predictable.
    monkeypatch.setenv("HOME", str(tmp_path))

    proj = tmp_path / "proj"
    proj.mkdir()

    ed = Editor()

    old = Path.cwd()
    try:
        assert ed.exec_command_line("cd ~/proj")
        assert Path.cwd().resolve() == proj.resolve()

        # Missing path should be a clean error (no crash), and cwd should remain.
        assert not ed.exec_command_line("cd ~/missing")
        assert Path.cwd().resolve() == proj.resolve()
    finally:
        try:
            import os

            os.chdir(str(old))
        except Exception:
            pass
