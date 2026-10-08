from __future__ import annotations

from pathlib import Path

from micromax_editor.editor import Editor
from micromax_editor.micromax_bridge import install_editor_hostcalls


def test_filetype_extension_detection(tmp_path: Path) -> None:
    p = tmp_path / 'hello.py'
    p.write_text('print(1)\n', encoding='utf-8')

    ed = Editor()
    install_editor_hostcalls(ed)
    ed.open_file(str(p))

    assert ed.filetype() == 'python'
    st = ed.status_model()
    assert st['filetype'] == 'python'


def test_filetype_shebang_detection(tmp_path: Path) -> None:
    p = tmp_path / 'script'
    p.write_text('#!/usr/bin/env python\nprint(2)\n', encoding='utf-8')

    ed = Editor()
    install_editor_hostcalls(ed)
    ed.open_file(str(p))

    assert ed.filetype() == 'python'
