from __future__ import annotations

import pytest

from micromax_editor import Editor
from micromax_editor.__main__ import _screen_dump_payload, main, run_headless_repl
from micromax_editor.screen_budget import (
    SCREEN_MAX_CELLS,
    ScreenBudgetError,
    checked_screen_dimensions,
)
from micromax_editor.screen_contract import screen_contract_v1


def test_shared_screen_budget_accepts_boundary_and_rejects_bad_shapes() -> None:
    assert checked_screen_dimensions(256, 256) == (256, 256)
    assert 256 * 256 == SCREEN_MAX_CELLS

    for lines, cols, message in (
        (0, 80, "lines must be between"),
        (257, 80, "lines must be between"),
        (24, 0, "cols must be between"),
        (24, 513, "cols must be between"),
        (256, 512, "exceeds cell budget"),
        (True, 80, "must be integers"),
        (24.5, 80, "must be integers"),
        ("24", 80, "must be integers"),
    ):
        with pytest.raises(ScreenBudgetError, match=message):
            checked_screen_dimensions(lines, cols)


def test_contract_rejects_dimensions_before_calling_a_source_builder() -> None:
    class PoisonSource:
        def _screen_contract_source_model(self, *, lines: int, cols: int) -> object:
            raise AssertionError("source traversal should not begin")

    with pytest.raises(ScreenBudgetError, match="exceeds cell budget"):
        screen_contract_v1(PoisonSource(), lines=256, cols=512)


def test_diagnostic_dump_rejects_dimensions_before_model_traversal() -> None:
    class PoisonEditor:
        def screen_model(self, *, lines: int, cols: int) -> object:
            raise AssertionError("diagnostic traversal should not begin")

    with pytest.raises(ScreenBudgetError, match="lines must be between"):
        _screen_dump_payload(  # type: ignore[arg-type]
            PoisonEditor(),
            lines=0,
            cols=80,
            detail="diagnostic",
        )


def test_cli_screen_preflight_happens_before_runtime_startup(monkeypatch, capsys) -> None:
    def poison_runtime(**_kwargs: object) -> object:
        raise AssertionError("startup should not begin")

    monkeypatch.setattr("micromax_editor.__main__.create_editor_runtime", poison_runtime)
    with pytest.raises(SystemExit) as excinfo:
        main(["--dump-screen", "256", "512"])

    assert excinfo.value.code == 2
    assert "exceeds cell budget" in capsys.readouterr().err


def test_repl_bad_screen_shape_is_visible_and_does_not_kill_session(capsys) -> None:
    editor = Editor()
    editor.new_buffer("*scratch*", "")
    commands = iter([":screen 256 512", ":q"])

    rc = run_headless_repl(
        editor,
        input_fn=lambda _prompt: next(commands),
        stdin_isatty=False,
    )

    assert rc == 0
    assert editor.should_quit is True
    assert "exceeds cell budget" in capsys.readouterr().out
