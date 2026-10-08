from __future__ import annotations

import pytest

from micromax_editor.editor import Editor
from micromax_editor.micromax_bridge import install_editor_hostcalls


def _hostcall(ed: Editor, name: str, *args: object) -> object:
    vm = ed.vm
    vm.stack.clear()
    for arg in args:
        vm.stack.append(arg)
    vm.stack.append(name)
    vm.eval("hostcall")
    assert vm.stack
    return vm.stack.pop()


def test_help_docs_explicit_paths_are_limited_to_docs_root(tmp_path) -> None:
    ed = Editor()
    ed.new_buffer("scratch", "")
    install_editor_hostcalls(ed)
    secret = tmp_path / "secret.md"
    secret.write_text("SECRET HELP BYPASS\n", encoding="utf-8")

    # Direct/interactive help should not treat arbitrary paths as docs.
    assert ed.exec_command_line(f"help docs {secret}") is False
    assert "SECRET HELP BYPASS" not in ed.cur().buf.get_text()

    # Script-originated command and direct help hostcall must be denied too;
    # otherwise `help` + `ed.text` becomes a cap.fs-read bypass.
    assert _hostcall(ed, "ed.command", f"help docs {secret}") == 0
    assert "SECRET HELP BYPASS" not in ed.cur().buf.get_text()
    assert _hostcall(ed, "ed.help-doc", str(secret)) == 0
    assert "SECRET HELP BYPASS" not in ed.cur().buf.get_text()

    # Repo-root and docs-root relative markdown paths still work for real docs.
    assert ed.open_help_doc("docs/00-vision.md") is True
    assert ed.cur().name.startswith("help:vision")
    assert ed.open_help_doc("00-vision.md") is True
    assert ed.cur().name.startswith("help:vision")


def test_docs_catalog_ignores_symlinks_escaping_docs_root(tmp_path, monkeypatch) -> None:
    root = tmp_path / "docs"
    root.mkdir()
    inside = root / "01-inside.md"
    inside.write_text("# Inside\n\nVisible doc.\n", encoding="utf-8")
    outside = tmp_path / "outside.md"
    outside.write_text("# Outside\n\nSECRET VIA SYMLINK\n", encoding="utf-8")
    link = root / "02-link.md"
    try:
        link.symlink_to(outside)
    except (OSError, NotImplementedError):
        pytest.skip("symlink not supported on this host")

    monkeypatch.setenv("MICROMAX_DOCS", str(root))
    ed = Editor()

    rows = ed.doc_prompt_rows()
    topics = {str(row[0]) for row in rows}
    assert "inside" in topics
    assert "link" not in topics
    assert ed.open_help_doc("inside") is True
    assert "Visible doc" in ed.cur().buf.get_text()
    assert ed.open_help_doc("link") is False
    assert "SECRET VIA SYMLINK" not in ed.cur().buf.get_text()
    assert ed.open_help_doc(str(link)) is False
    assert "SECRET VIA SYMLINK" not in ed.cur().buf.get_text()


def test_helpfollow_relative_link_cannot_escape_docs_root(tmp_path, monkeypatch) -> None:
    root = tmp_path / "docs"
    root.mkdir()
    inside = root / "01-inside.md"
    inside.write_text("# Inside\n\n[escape](../outside.md)\n", encoding="utf-8")
    outside = tmp_path / "outside.md"
    outside.write_text("# Outside\n\nSECRET FOLLOW BYPASS\n", encoding="utf-8")

    monkeypatch.setenv("MICROMAX_DOCS", str(root))
    ed = Editor()

    assert ed.open_help_doc("inside") is True
    cur = ed.cur().cursors[ed.cur().primary]
    cur.line = 2
    cur.col = 2

    assert ed.exec_command_line("helpfollow") is False
    assert ed.cur().name.startswith("help:inside")
    assert "SECRET FOLLOW BYPASS" not in ed.cur().buf.get_text()
    assert ed.status_model()["last_message"] == "help docs: no such doc: ../outside.md"
