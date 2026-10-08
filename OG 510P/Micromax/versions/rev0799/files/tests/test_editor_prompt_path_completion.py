from __future__ import annotations

from micromax_editor.cmdline import parse_cmdline
from micromax_editor.editor import Editor

import os


def test_prompt_complete_open_path_unique_file(tmp_path, monkeypatch) -> None:
    (tmp_path / "alpha.txt").write_text("x")
    (tmp_path / "beta.txt").write_text("y")
    monkeypatch.chdir(tmp_path)

    ed = Editor()
    ed.enter_prompt("command", prefill="open a")
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    assert ed.prompt.text == "open alpha.txt "


def test_prompt_complete_open_path_unique_dir_no_trailing_space(tmp_path, monkeypatch) -> None:
    (tmp_path / "srcdir").mkdir()
    (tmp_path / "alpha.txt").write_text("x")
    monkeypatch.chdir(tmp_path)

    ed = Editor()
    ed.enter_prompt("command", prefill="open s")
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    assert ed.prompt.text == f"open srcdir{os.sep}"
    # portable assertion: should not end with a space (dirs are navigational)
    assert not ed.prompt.text.endswith(" ")


def test_prompt_complete_open_path_multiple_matches_starts_session_and_cycles(tmp_path, monkeypatch) -> None:
    (tmp_path / "a.txt").write_text("x")
    (tmp_path / "ab.txt").write_text("y")
    monkeypatch.chdir(tmp_path)

    ed = Editor()
    ed.enter_prompt("command", prefill="open a")
    assert ed.prompt is not None

    # first call should start a session (multiple candidates)
    assert ed.prompt_complete(direction=1)
    assert len(ed.prompt.suggestions) >= 2
    assert ed.prompt.suggest_base == "open a"

    # next call applies first suggestion
    assert ed.prompt_complete(direction=1)
    assert ed.prompt.text == "open " + ed.prompt.suggestions[0]

    # and cycles
    assert ed.prompt_complete(direction=1)
    assert ed.prompt.text == "open " + ed.prompt.suggestions[1]


def test_prompt_complete_open_path_autoquotes_space_filename(tmp_path, monkeypatch) -> None:
    (tmp_path / "alpha beta.txt").write_text("x")
    monkeypatch.chdir(tmp_path)

    ed = Editor()
    ed.enter_prompt("command", prefill="open a")
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    assert ed.prompt.text == 'open "alpha beta.txt" '


def test_prompt_complete_open_path_autoquotes_space_dir_keeps_quote_open(tmp_path, monkeypatch) -> None:
    d = tmp_path / "alpha dir"
    d.mkdir()
    (d / "x.txt").write_text("x")
    monkeypatch.chdir(tmp_path)

    ed = Editor()
    ed.enter_prompt("command", prefill="open a")
    assert ed.prompt is not None

    # Directory completion uses an opening quote so we can continue completing.
    assert ed.prompt_complete(direction=1)
    assert ed.prompt.text == f'open "alpha dir{os.sep}'
    assert not ed.prompt.text.endswith('"')

    # Completing again should enter the dir and complete the file, closing the quote.
    assert ed.prompt_complete(direction=1)
    assert ed.prompt.text == f'open "alpha dir{os.sep}x.txt" '


def test_prompt_complete_open_path_preserves_user_quote_closure_for_dirs(tmp_path, monkeypatch) -> None:
    (tmp_path / "alpha dir").mkdir()
    monkeypatch.chdir(tmp_path)

    ed = Editor()
    # User already typed a closing quote; we preserve it.
    ed.enter_prompt("command", prefill='open "a"')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    assert ed.prompt.text == f'open "alpha dir{os.sep}"'


def test_prompt_complete_open_path_autoquotes_double_quote_in_name(tmp_path, monkeypatch) -> None:
    (tmp_path / 'a"b.txt').write_text('x')
    monkeypatch.chdir(tmp_path)

    ed = Editor()
    ed.enter_prompt("command", prefill='open a')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    # Escaped quote inside double quotes.
    assert ed.prompt.text == 'open "a\\"b.txt" '


def test_prompt_complete_open_path_suggestion_rows_include_file_kinds(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / 'alpha.txt').write_text('x')
    (tmp_path / 'alpha dir').mkdir()

    ed = Editor()
    ed.enter_prompt('command', prefill='open a')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    rows = ed.prompt_suggestion_rows()
    row_by_insert = {r[0]: r for r in rows}
    assert row_by_insert['"alpha dir/'][1] == 'dir'
    assert row_by_insert['alpha.txt '][1] == 'file'


def test_prompt_complete_open_path_autoquotes_single_quote_filename_for_parse(tmp_path, monkeypatch) -> None:
    (tmp_path / "alpha's.txt").write_text("x")
    monkeypatch.chdir(tmp_path)

    ed = Editor()
    ed.enter_prompt("command", prefill="open a")
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    assert ed.prompt.text == "open \"alpha's.txt\" "
    parsed = parse_cmdline(ed.prompt.text)
    assert parsed is not None
    assert parsed.args == ["alpha's.txt"]


def test_prompt_complete_open_path_autoquotes_backslash_filename_for_parse(tmp_path, monkeypatch) -> None:
    (tmp_path / "alpha\\beta.txt").write_text("x")
    monkeypatch.chdir(tmp_path)

    ed = Editor()
    ed.enter_prompt("command", prefill="open a")
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    assert ed.prompt.text == 'open "alpha\\\\beta.txt" '
    parsed = parse_cmdline(ed.prompt.text)
    assert parsed is not None
    assert parsed.args == ["alpha\\beta.txt"]

def test_prompt_complete_open_path_switches_single_quote_when_needed(tmp_path, monkeypatch) -> None:
    (tmp_path / "alpha's.txt").write_text("x")
    monkeypatch.chdir(tmp_path)

    ed = Editor()
    ed.enter_prompt("command", prefill="open 'a")
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    assert ed.prompt.text == "open \"alpha's.txt\" "
    parsed = parse_cmdline(ed.prompt.text)
    assert parsed is not None
    assert parsed.args == ["alpha's.txt"]



def test_prompt_complete_open_path_continues_inside_backslash_dir(tmp_path, monkeypatch) -> None:
    dirname = 'alpha\\dir'
    d = tmp_path / dirname
    d.mkdir()
    (d / 'z.txt').write_text('x')
    monkeypatch.chdir(tmp_path)

    ed = Editor()
    ed.enter_prompt('command', prefill='open a')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    assert ed.prompt.text == 'open "alpha\\\\dir/'

    assert ed.prompt_complete(direction=1)
    assert ed.prompt.text == 'open "alpha\\\\dir/z.txt" '
    parsed = parse_cmdline(ed.prompt.text)
    assert parsed is not None
    assert parsed.args == [f'{dirname}/z.txt']


def test_prompt_complete_open_path_continues_inside_double_quote_dir(tmp_path, monkeypatch) -> None:
    dirname = 'alpha"dir'
    d = tmp_path / dirname
    d.mkdir()
    (d / 'z.txt').write_text('x')
    monkeypatch.chdir(tmp_path)

    ed = Editor()
    ed.enter_prompt('command', prefill='open a')
    assert ed.prompt is not None

    assert ed.prompt_complete(direction=1)
    assert ed.prompt.text == 'open "alpha\\"dir/'

    assert ed.prompt_complete(direction=1)
    assert ed.prompt.text == 'open "alpha\\"dir/z.txt" '
    parsed = parse_cmdline(ed.prompt.text)
    assert parsed is not None
    assert parsed.args == [f'{dirname}/z.txt']
