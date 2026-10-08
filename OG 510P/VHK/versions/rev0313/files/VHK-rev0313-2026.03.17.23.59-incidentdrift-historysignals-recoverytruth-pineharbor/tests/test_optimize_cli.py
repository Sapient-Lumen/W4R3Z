from __future__ import annotations

from pathlib import Path

import yaml
from typer.testing import CliRunner

from vhk.cli import app


runner = CliRunner()


def test_optimize_compacts_recording(tmp_path: Path):
    macro = tmp_path / "m.yaml"
    macro.write_text(
        yaml.safe_dump(
            {
                "name": "m",
                "steps": [
                    {"type": "Delay", "ms": 10},
                    {"type": "Delay", "ms": 20},
                    # Redundant mouse moves.
                    {"type": "MouseMove", "x": 1, "y": 2},
                    {"type": "MouseMove", "x": 3, "y": 4},
                    {"type": "MouseMove", "x": 3, "y": 4},
                    {"type": "Log", "message": "sep"},
                    # Click sequence.
                    {"type": "MouseMove", "x": 10, "y": 10},
                    {"type": "MouseClick", "button": 1, "down": True},
                    {"type": "Delay", "ms": 50},
                    {"type": "MouseMove", "x": 11, "y": 10},
                    {"type": "MouseClick", "button": 1, "up": True},
                    # Chord sequence.
                    {"type": "KeyDown", "key": "ctrl"},
                    {"type": "KeyDown", "key": "l"},
                    {"type": "KeyUp", "key": "l"},
                    {"type": "KeyUp", "key": "ctrl"},
                    # Simple keypress.
                    {"type": "KeyDown", "key": "a"},
                    {"type": "Delay", "ms": 10},
                    {"type": "KeyUp", "key": "a"},
                ],
            }
        )
    )

    result = runner.invoke(app, ["optimize", str(macro), "--quiet"])
    assert result.exit_code == 0, result.output
    out = yaml.safe_load(result.output)
    assert isinstance(out, dict)
    steps = out["steps"]

    # Delay merged.
    assert steps[0] == {"type": "Delay", "ms": 30}

    # MouseMove run squashed to the last move.
    assert steps[1] == {"type": "MouseMove", "x": 3, "y": 4}

    # Click compacted.
    assert {"type": "MouseClickAt", "x": 10, "y": 10, "button": 1} in steps

    # Chord + keypress compacted.
    assert {"type": "Key", "keys": "ctrl+l"} in steps
    assert {"type": "Key", "keys": "a"} in steps


def test_optimize_can_collapse_text_into_typetext(tmp_path: Path):
    macro = tmp_path / "t.yaml"
    macro.write_text(
        yaml.safe_dump(
            {
                "name": "t",
                "steps": [
                    {"type": "Key", "keys": "h"},
                    {"type": "Delay", "ms": 10},
                    {"type": "Key", "keys": "i"},
                    {"type": "Delay", "ms": 15},
                    {"type": "Key", "keys": "!"},
                    {"type": "Log", "message": "after"},
                ],
            }
        )
    )

    result = runner.invoke(app, ["optimize", str(macro), "--compress-text", "--quiet"])
    assert result.exit_code == 0, result.output
    out = yaml.safe_load(result.output)
    steps = out["steps"]
    assert steps[0]["type"] == "TypeText"
    assert steps[0]["text"] == "hi!"
    assert steps[0]["backend"] == "native"
    assert steps[1] == {"type": "Log", "message": "after"}


def test_optimize_can_collapse_shifted_text_into_typetext(tmp_path: Path):
    macro = tmp_path / "shifted.yaml"
    macro.write_text(
        yaml.safe_dump(
            {
                "name": "shifted",
                "steps": [
                    {"type": "KeyDown", "key": "shift"},
                    {"type": "KeyDown", "key": "h"},
                    {"type": "KeyUp", "key": "h"},
                    {"type": "KeyUp", "key": "shift"},
                    {"type": "Delay", "ms": 10},
                    {"type": "KeyDown", "key": "e"},
                    {"type": "KeyUp", "key": "e"},
                    {"type": "Delay", "ms": 10},
                    {"type": "KeyDown", "key": "l"},
                    {"type": "KeyUp", "key": "l"},
                    {"type": "Delay", "ms": 10},
                    {"type": "KeyDown", "key": "l"},
                    {"type": "KeyUp", "key": "l"},
                    {"type": "Delay", "ms": 10},
                    {"type": "KeyDown", "key": "o"},
                    {"type": "KeyUp", "key": "o"},
                    {"type": "Delay", "ms": 10},
                    {"type": "KeyDown", "key": "shift"},
                    {"type": "KeyDown", "key": "1"},
                    {"type": "KeyUp", "key": "1"},
                    {"type": "KeyUp", "key": "shift"},
                    {"type": "Log", "message": "after"},
                ],
            }
        )
    )

    result = runner.invoke(app, ["optimize", str(macro), "--compress-text", "--quiet"])
    assert result.exit_code == 0, result.output
    out = yaml.safe_load(result.output)
    steps = out["steps"]
    assert steps[0]["type"] == "TypeText"
    assert steps[0]["text"] == "Hello!"
    assert steps[0]["backend"] == "native"
    assert steps[1] == {"type": "Log", "message": "after"}


def test_optimize_can_collapse_edited_text_with_backspace(tmp_path: Path):
    macro = tmp_path / "edited.yaml"
    macro.write_text(
        yaml.safe_dump(
            {
                "name": "edited",
                "steps": [
                    {"type": "Key", "keys": "h"},
                    {"type": "Delay", "ms": 10},
                    {"type": "Key", "keys": "e"},
                    {"type": "Delay", "ms": 10},
                    {"type": "Key", "keys": "x"},
                    {"type": "Delay", "ms": 10},
                    {"type": "Key", "keys": "backspace"},
                    {"type": "Delay", "ms": 10},
                    {"type": "Key", "keys": "l"},
                    {"type": "Delay", "ms": 10},
                    {"type": "Key", "keys": "l"},
                    {"type": "Delay", "ms": 10},
                    {"type": "Key", "keys": "o"},
                    {"type": "Log", "message": "after"},
                ],
            }
        )
    )

    result = runner.invoke(app, ["optimize", str(macro), "--compress-text", "--quiet"])
    assert result.exit_code == 0, result.output
    out = yaml.safe_load(result.output)
    steps = out["steps"]
    assert steps[0]["type"] == "TypeText"
    assert steps[0]["text"] == "hello"
    assert steps[0]["backend"] == "native"
    assert steps[0]["comment"] == "optimized from edited key stream"
    assert steps[1] == {"type": "Log", "message": "after"}


def test_optimize_can_collapse_cursor_navigation_edit_runs(tmp_path: Path):
    macro = tmp_path / "nav_edit.yaml"
    macro.write_text(
        yaml.safe_dump(
            {
                "name": "nav_edit",
                "steps": [
                    {"type": "Key", "keys": "h"},
                    {"type": "Delay", "ms": 10},
                    {"type": "Key", "keys": "e"},
                    {"type": "Delay", "ms": 10},
                    {"type": "Key", "keys": "l"},
                    {"type": "Delay", "ms": 10},
                    {"type": "Key", "keys": "o"},
                    {"type": "Delay", "ms": 10},
                    {"type": "Key", "keys": "left"},
                    {"type": "Delay", "ms": 10},
                    {"type": "Key", "keys": "left"},
                    {"type": "Delay", "ms": 10},
                    {"type": "Key", "keys": "l"},
                    {"type": "Delay", "ms": 10},
                    {"type": "Key", "keys": "right"},
                    {"type": "Delay", "ms": 10},
                    {"type": "Key", "keys": "right"},
                    {"type": "Log", "message": "after"},
                ],
            }
        )
    )

    result = runner.invoke(app, ["optimize", str(macro), "--compress-text", "--quiet"])
    assert result.exit_code == 0, result.output
    out = yaml.safe_load(result.output)
    steps = out["steps"]
    assert steps[0]["type"] == "TypeText"
    assert steps[0]["text"] == "hello"
    assert steps[0]["backend"] == "native"
    assert steps[0]["comment"] == "optimized from edited key stream"
    assert steps[1] == {"type": "Log", "message": "after"}


def test_optimize_can_collapse_home_delete_cleanup_runs(tmp_path: Path):
    macro = tmp_path / "home_delete.yaml"
    macro.write_text(
        yaml.safe_dump(
            {
                "name": "home_delete",
                "steps": [
                    {"type": "Key", "keys": "x"},
                    {"type": "Delay", "ms": 10},
                    {"type": "Key", "keys": "h"},
                    {"type": "Delay", "ms": 10},
                    {"type": "Key", "keys": "e"},
                    {"type": "Delay", "ms": 10},
                    {"type": "Key", "keys": "l"},
                    {"type": "Delay", "ms": 10},
                    {"type": "Key", "keys": "l"},
                    {"type": "Delay", "ms": 10},
                    {"type": "Key", "keys": "o"},
                    {"type": "Delay", "ms": 10},
                    {"type": "Key", "keys": "home"},
                    {"type": "Delay", "ms": 10},
                    {"type": "Key", "keys": "delete"},
                    {"type": "Delay", "ms": 10},
                    {"type": "Key", "keys": "end"},
                ],
            }
        )
    )

    result = runner.invoke(app, ["optimize", str(macro), "--compress-text", "--quiet"])
    assert result.exit_code == 0, result.output
    out = yaml.safe_load(result.output)
    steps = out["steps"]
    assert steps == [
        {
            "type": "TypeText",
            "text": "hello",
            "delay_ms_per_char": 10,
            "backend": "native",
            "comment": "optimized from edited key stream",
        }
    ]


def test_optimize_keeps_cursor_navigation_when_final_caret_position_matters(tmp_path: Path):
    macro = tmp_path / "caret.yaml"
    macro.write_text(
        yaml.safe_dump(
            {
                "name": "caret",
                "steps": [
                    {"type": "Key", "keys": "a"},
                    {"type": "Delay", "ms": 10},
                    {"type": "Key", "keys": "b"},
                    {"type": "Delay", "ms": 10},
                    {"type": "Key", "keys": "c"},
                    {"type": "Delay", "ms": 10},
                    {"type": "Key", "keys": "left"},
                ],
            }
        )
    )

    result = runner.invoke(app, ["optimize", str(macro), "--compress-text", "--quiet"])
    assert result.exit_code == 0, result.output
    out = yaml.safe_load(result.output)
    assert out["steps"] == [
        {"type": "Key", "keys": "a"},
        {"type": "Delay", "ms": 10},
        {"type": "Key", "keys": "b"},
        {"type": "Delay", "ms": 10},
        {"type": "Key", "keys": "c"},
        {"type": "Delay", "ms": 10},
        {"type": "Key", "keys": "left"},
    ]


def test_optimize_can_collapse_text_with_enter_and_tab(tmp_path: Path):
    macro = tmp_path / "multiline.yaml"
    macro.write_text(
        yaml.safe_dump(
            {
                "name": "multiline",
                "steps": [
                    {"type": "Key", "keys": "a"},
                    {"type": "Delay", "ms": 10},
                    {"type": "Key", "keys": "enter"},
                    {"type": "Delay", "ms": 10},
                    {"type": "Key", "keys": "tab"},
                    {"type": "Delay", "ms": 10},
                    {"type": "Key", "keys": "b"},
                ],
            }
        )
    )

    result = runner.invoke(app, ["optimize", str(macro), "--compress-text", "--quiet"])
    assert result.exit_code == 0, result.output
    out = yaml.safe_load(result.output)
    steps = out["steps"]
    assert steps == [{"type": "TypeText", "text": "a\n	b", "delay_ms_per_char": 10, "backend": "native"}]


def test_optimize_keeps_non_text_shortcuts_as_keys(tmp_path: Path):
    macro = tmp_path / "shortcut.yaml"
    macro.write_text(
        yaml.safe_dump(
            {
                "name": "shortcut",
                "steps": [
                    {"type": "KeyDown", "key": "ctrl"},
                    {"type": "KeyDown", "key": "shift"},
                    {"type": "KeyDown", "key": "p"},
                    {"type": "KeyUp", "key": "p"},
                    {"type": "KeyUp", "key": "shift"},
                    {"type": "KeyUp", "key": "ctrl"},
                ],
            }
        )
    )

    result = runner.invoke(app, ["optimize", str(macro), "--compress-text", "--quiet"])
    assert result.exit_code == 0, result.output
    out = yaml.safe_load(result.output)
    steps = out["steps"]
    assert steps == [{"type": "Key", "keys": "ctrl+shift+p"}]


def test_optimize_can_collapse_shift_selection_replacement_runs(tmp_path: Path):
    macro = tmp_path / "selection_replace.yaml"
    macro.write_text(
        yaml.safe_dump(
            {
                "name": "selection_replace",
                "steps": [
                    {"type": "Key", "keys": "h"},
                    {"type": "Delay", "ms": 10},
                    {"type": "Key", "keys": "e"},
                    {"type": "Delay", "ms": 10},
                    {"type": "Key", "keys": "l"},
                    {"type": "Delay", "ms": 10},
                    {"type": "Key", "keys": "l"},
                    {"type": "Delay", "ms": 10},
                    {"type": "Key", "keys": "p"},
                    {"type": "Delay", "ms": 10},
                    {"type": "Key", "keys": "shift+left"},
                    {"type": "Delay", "ms": 10},
                    {"type": "Key", "keys": "o"},
                ],
            }
        )
    )

    result = runner.invoke(app, ["optimize", str(macro), "--compress-text", "--quiet"])
    assert result.exit_code == 0, result.output
    out = yaml.safe_load(result.output)
    assert out["steps"] == [
        {
            "type": "TypeText",
            "text": "hello",
            "delay_ms_per_char": 10,
            "backend": "native",
            "comment": "optimized from edited key stream",
        }
    ]


def test_optimize_keeps_text_when_selection_is_still_active(tmp_path: Path):
    macro = tmp_path / "selection_active.yaml"
    macro.write_text(
        yaml.safe_dump(
            {
                "name": "selection_active",
                "steps": [
                    {"type": "Key", "keys": "h"},
                    {"type": "Delay", "ms": 10},
                    {"type": "Key", "keys": "e"},
                    {"type": "Delay", "ms": 10},
                    {"type": "Key", "keys": "l"},
                    {"type": "Delay", "ms": 10},
                    {"type": "Key", "keys": "l"},
                    {"type": "Delay", "ms": 10},
                    {"type": "Key", "keys": "o"},
                    {"type": "Delay", "ms": 10},
                    {"type": "Key", "keys": "shift+left"},
                ],
            }
        )
    )

    result = runner.invoke(app, ["optimize", str(macro), "--compress-text", "--quiet"])
    assert result.exit_code == 0, result.output
    out = yaml.safe_load(result.output)
    assert out["steps"] == [
        {"type": "Key", "keys": "h"},
        {"type": "Delay", "ms": 10},
        {"type": "Key", "keys": "e"},
        {"type": "Delay", "ms": 10},
        {"type": "Key", "keys": "l"},
        {"type": "Delay", "ms": 10},
        {"type": "Key", "keys": "l"},
        {"type": "Delay", "ms": 10},
        {"type": "Key", "keys": "o"},
        {"type": "Delay", "ms": 10},
        {"type": "Key", "keys": "shift+left"},
    ]


def test_optimize_can_collapse_word_delete_cleanup_runs(tmp_path: Path):
    macro = tmp_path / "word_delete.yaml"
    macro.write_text(
        yaml.safe_dump(
            {
                "name": "word_delete",
                "steps": [
                    {"type": "Key", "keys": "h"},
                    {"type": "Delay", "ms": 10},
                    {"type": "Key", "keys": "e"},
                    {"type": "Delay", "ms": 10},
                    {"type": "Key", "keys": "l"},
                    {"type": "Delay", "ms": 10},
                    {"type": "Key", "keys": "l"},
                    {"type": "Delay", "ms": 10},
                    {"type": "Key", "keys": "o"},
                    {"type": "Delay", "ms": 10},
                    {"type": "Key", "keys": "space"},
                    {"type": "Delay", "ms": 10},
                    {"type": "Key", "keys": "w"},
                    {"type": "Delay", "ms": 10},
                    {"type": "Key", "keys": "r"},
                    {"type": "Delay", "ms": 10},
                    {"type": "Key", "keys": "o"},
                    {"type": "Delay", "ms": 10},
                    {"type": "Key", "keys": "n"},
                    {"type": "Delay", "ms": 10},
                    {"type": "Key", "keys": "g"},
                    {"type": "Delay", "ms": 10},
                    {"type": "Key", "keys": "ctrl+backspace"},
                    {"type": "Delay", "ms": 10},
                    {"type": "Key", "keys": "w"},
                    {"type": "Delay", "ms": 10},
                    {"type": "Key", "keys": "o"},
                    {"type": "Delay", "ms": 10},
                    {"type": "Key", "keys": "r"},
                    {"type": "Delay", "ms": 10},
                    {"type": "Key", "keys": "l"},
                    {"type": "Delay", "ms": 10},
                    {"type": "Key", "keys": "d"},
                ],
            }
        )
    )

    result = runner.invoke(app, ["optimize", str(macro), "--compress-text", "--quiet"])
    assert result.exit_code == 0, result.output
    out = yaml.safe_load(result.output)
    assert out["steps"] == [
        {
            "type": "TypeText",
            "text": "hello world",
            "delay_ms_per_char": 10,
            "backend": "native",
            "comment": "optimized from edited key stream",
        }
    ]




def test_optimize_can_collapse_ctrl_delete_cleanup_runs(tmp_path: Path):
    macro = tmp_path / "ctrl_delete.yaml"
    macro.write_text(
        yaml.safe_dump(
            {
                "name": "ctrl_delete",
                "steps": [
                    {"type": "Key", "keys": "x"},
                    {"type": "Delay", "ms": 10},
                    {"type": "Key", "keys": "h"},
                    {"type": "Delay", "ms": 10},
                    {"type": "Key", "keys": "e"},
                    {"type": "Delay", "ms": 10},
                    {"type": "Key", "keys": "l"},
                    {"type": "Delay", "ms": 10},
                    {"type": "Key", "keys": "l"},
                    {"type": "Delay", "ms": 10},
                    {"type": "Key", "keys": "o"},
                    {"type": "Delay", "ms": 10},
                    {"type": "Key", "keys": "home"},
                    {"type": "Delay", "ms": 10},
                    {"type": "Key", "keys": "ctrl+delete"},
                    {"type": "Delay", "ms": 10},
                    {"type": "Key", "keys": "h"},
                    {"type": "Delay", "ms": 10},
                    {"type": "Key", "keys": "e"},
                    {"type": "Delay", "ms": 10},
                    {"type": "Key", "keys": "l"},
                    {"type": "Delay", "ms": 10},
                    {"type": "Key", "keys": "l"},
                    {"type": "Delay", "ms": 10},
                    {"type": "Key", "keys": "o"},
                ],
            }
        )
    )

    result = runner.invoke(app, ["optimize", str(macro), "--compress-text", "--quiet"])
    assert result.exit_code == 0, result.output
    out = yaml.safe_load(result.output)
    assert out["steps"] == [
        {
            "type": "TypeText",
            "text": "hello",
            "delay_ms_per_char": 10,
            "backend": "native",
            "comment": "optimized from edited key stream",
        }
    ]
def test_optimize_can_collapse_shift_end_replacement_runs(tmp_path: Path):
    macro = tmp_path / "shift_end_replace.yaml"
    macro.write_text(
        yaml.safe_dump(
            {
                "name": "shift_end_replace",
                "steps": [
                    {"type": "Key", "keys": "h"},
                    {"type": "Delay", "ms": 10},
                    {"type": "Key", "keys": "e"},
                    {"type": "Delay", "ms": 10},
                    {"type": "Key", "keys": "l"},
                    {"type": "Delay", "ms": 10},
                    {"type": "Key", "keys": "l"},
                    {"type": "Delay", "ms": 10},
                    {"type": "Key", "keys": "x"},
                    {"type": "Delay", "ms": 10},
                    {"type": "Key", "keys": "home"},
                    {"type": "Delay", "ms": 10},
                    {"type": "Key", "keys": "right"},
                    {"type": "Delay", "ms": 10},
                    {"type": "Key", "keys": "right"},
                    {"type": "Delay", "ms": 10},
                    {"type": "Key", "keys": "right"},
                    {"type": "Delay", "ms": 10},
                    {"type": "Key", "keys": "right"},
                    {"type": "Delay", "ms": 10},
                    {"type": "Key", "keys": "shift+end"},
                    {"type": "Delay", "ms": 10},
                    {"type": "Key", "keys": "o"},
                ],
            }
        )
    )

    result = runner.invoke(app, ["optimize", str(macro), "--compress-text", "--quiet"])
    assert result.exit_code == 0, result.output
    out = yaml.safe_load(result.output)
    assert out["steps"] == [
        {
            "type": "TypeText",
            "text": "hello",
            "delay_ms_per_char": 10,
            "backend": "native",
            "comment": "optimized from edited key stream",
        }
    ]


def test_optimize_can_promote_long_literal_typetext_to_clipboard(tmp_path: Path):
    macro = tmp_path / "paste_promote.yaml"
    macro.write_text(
        yaml.safe_dump(
            {
                "name": "paste_promote",
                "steps": [
                    {
                        "type": "TypeText",
                        "text": "This is a deliberately long literal text block for paste promotion.",
                        "backend": "native",
                    },
                    {"type": "Log", "message": "after"},
                ],
            }
        )
    )

    result = runner.invoke(
        app,
        [
            "optimize",
            str(macro),
            "--promote-paste-text",
            "--paste-text-min-chars",
            "20",
            "--quiet",
        ],
    )
    assert result.exit_code == 0, result.output
    out = yaml.safe_load(result.output)
    steps = out["steps"]
    assert steps[0]["type"] == "TypeText"
    assert steps[0]["backend"] == "clipboard"
    assert steps[0]["selection"] == "clipboard"
    assert steps[0]["preserve_clipboard"] is True
    assert steps[0]["paste_shortcut"] == "auto"
    assert steps[0]["comment"] == "optimized for paste-friendly text"
    assert steps[1] == {"type": "Log", "message": "after"}



def test_optimize_does_not_promote_dynamic_typetext_to_clipboard(tmp_path: Path):
    macro = tmp_path / "dynamic_paste.yaml"
    macro.write_text(
        yaml.safe_dump(
            {
                "name": "dynamic_paste",
                "steps": [
                    {
                        "type": "TypeText",
                        "text": "${email_body}",
                        "backend": "native",
                    },
                ],
            }
        )
    )

    result = runner.invoke(
        app,
        [
            "optimize",
            str(macro),
            "--promote-paste-text",
            "--paste-text-min-chars",
            "5",
            "--quiet",
        ],
    )
    assert result.exit_code == 0, result.output
    out = yaml.safe_load(result.output)
    assert out["steps"] == [{"type": "TypeText", "text": "${email_body}", "backend": "native"}]



def test_optimize_does_not_promote_tab_or_enter_text_to_clipboard(tmp_path: Path):
    macro = tmp_path / "tabbed.yaml"
    macro.write_text(
        yaml.safe_dump(
            {
                "name": "tabbed",
                "steps": [
                    {
                        "type": "TypeText",
                        "text": "name\tvalue\nnext",
                        "backend": "native",
                    },
                ],
            }
        )
    )

    result = runner.invoke(
        app,
        [
            "optimize",
            str(macro),
            "--promote-paste-text",
            "--paste-text-min-chars",
            "5",
            "--quiet",
        ],
    )
    assert result.exit_code == 0, result.output
    out = yaml.safe_load(result.output)
    assert out["steps"] == [{"type": "TypeText", "text": "name\tvalue\nnext", "backend": "native"}]



def test_optimize_can_promote_compressed_text_runs_to_clipboard(tmp_path: Path):
    macro = tmp_path / "compressed_promote.yaml"
    macro.write_text(
        yaml.safe_dump(
            {
                "name": "compressed_promote",
                "steps": [
                    {"type": "Key", "keys": "h"},
                    {"type": "Key", "keys": "e"},
                    {"type": "Key", "keys": "l"},
                    {"type": "Key", "keys": "l"},
                    {"type": "Key", "keys": "o"},
                    {"type": "Key", "keys": "space"},
                    {"type": "Key", "keys": "w"},
                    {"type": "Key", "keys": "o"},
                    {"type": "Key", "keys": "r"},
                    {"type": "Key", "keys": "l"},
                    {"type": "Key", "keys": "d"},
                ],
            }
        )
    )

    result = runner.invoke(
        app,
        [
            "optimize",
            str(macro),
            "--compress-text",
            "--promote-paste-text",
            "--paste-text-min-chars",
            "5",
            "--quiet",
        ],
    )
    assert result.exit_code == 0, result.output
    out = yaml.safe_load(result.output)
    assert out["steps"] == [
        {
            "type": "TypeText",
            "text": "hello world",
            "delay_ms_per_char": 0,
            "backend": "clipboard",
            "selection": "clipboard",
            "preserve_clipboard": True,
            "paste_shortcut": "auto",
            "comment": "optimized for paste-friendly text",
        }
    ]


def test_optimize_can_segment_structured_text_into_hybrid_paste_lane(tmp_path: Path):
    macro = tmp_path / "segmented.yaml"
    macro.write_text(
        yaml.safe_dump(
            {
                "name": "segmented",
                "steps": [
                    {
                        "type": "TypeText",
                        "text": "Name:\tAlexandra Example Person\nNotes:\tLonger field body here",
                        "backend": "native",
                    },
                ],
            }
        )
    )

    result = runner.invoke(
        app,
        [
            "optimize",
            str(macro),
            "--segment-paste-text",
            "--segment-paste-min-chars",
            "12",
            "--quiet",
        ],
    )
    assert result.exit_code == 0, result.output
    out = yaml.safe_load(result.output)
    assert out["steps"] == [
        {
            "type": "TypeText",
            "text": "Name:",
            "backend": "native",
            "comment": "optimized into hybrid text/paste lanes",
        },
        {"type": "Key", "keys": "tab"},
        {
            "type": "TypeText",
            "text": "Alexandra Example Person",
            "backend": "clipboard",
            "selection": "clipboard",
            "preserve_clipboard": True,
            "paste_shortcut": "auto",
        },
        {"type": "Key", "keys": "enter"},
        {
            "type": "TypeText",
            "text": "Notes:",
            "backend": "native",
        },
        {"type": "Key", "keys": "tab"},
        {
            "type": "TypeText",
            "text": "Longer field body here",
            "backend": "clipboard",
            "selection": "clipboard",
            "preserve_clipboard": True,
            "paste_shortcut": "auto",
        },
    ]


def test_optimize_does_not_segment_interpolated_structured_text(tmp_path: Path):
    macro = tmp_path / "segmented_dynamic.yaml"
    macro.write_text(
        yaml.safe_dump(
            {
                "name": "segmented_dynamic",
                "steps": [
                    {
                        "type": "TypeText",
                        "text": "Name:\t${person.name}",
                        "backend": "native",
                    },
                ],
            }
        )
    )

    result = runner.invoke(
        app,
        [
            "optimize",
            str(macro),
            "--segment-paste-text",
            "--segment-paste-min-chars",
            "5",
            "--quiet",
        ],
    )
    assert result.exit_code == 0, result.output
    out = yaml.safe_load(result.output)
    assert out["steps"] == [{"type": "TypeText", "text": "Name:\t${person.name}", "backend": "native"}]
