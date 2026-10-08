from __future__ import annotations

import json
from pathlib import Path

import yaml
from typer.testing import CliRunner

from vhk.cli import app
from vhk.project.autokey_pack import build_autokey_entries, write_autokey_pack
from vhk.project.loader import load_project


runner = CliRunner()


def _make_project(tmp_path: Path) -> Path:
    project_dir = tmp_path / "proj"
    (project_dir / "macros").mkdir(parents=True)
    (project_dir / "macros" / "sig.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "sig",
                "steps": [{"type": "Return", "value_expr": '"Best,\\nJane"', "out_var": "return_value"}],
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    (project_dir / "macros" / "open.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "open",
                "steps": [{"type": "Log", "message": "open"}],
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    (project_dir / "macros" / "scoped.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "scoped",
                "steps": [{"type": "Log", "message": "scoped"}],
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    (project_dir / "project.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "proj",
                "macros": {
                    "sig": "macros/sig.yaml",
                    "open": "macros/open.yaml",
                    "scoped": "macros/scoped.yaml",
                },
                "hotstrings": [
                    {
                        "trigger": ":sig",
                        "macro": "sig",
                        "description": "Insert signature",
                        "mode": "return",
                        "force_mode": "clipboard",
                        "when": {"class": "Firefox"},
                    },
                    {
                        "trigger": ":skip",
                        "macro": "scoped",
                        "description": "Too specific for AutoKey regex export",
                        "mode": "side_effect",
                        "when": {"class": "Firefox", "title": "Docs"},
                    },
                    {
                        "trigger": ":off",
                        "macro": "sig",
                        "mode": "return",
                        "enabled": False,
                    },
                ],
                "bindings": [
                    {
                        "keys": "ctrl+shift+o",
                        "macro": "open",
                        "description": "Open thing",
                        "when": {"title": "Project Board", "title_regex": True},
                    },
                    {
                        "keys": "alt_gr+s",
                        "macro": "open",
                        "description": "Unsupported altgr",
                    },
                ],
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    return project_dir


def _make_invalid_regex_project(tmp_path: Path) -> Path:
    project_dir = tmp_path / "badregex"
    (project_dir / "macros").mkdir(parents=True)
    (project_dir / "macros" / "open.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "open",
                "steps": [{"type": "Log", "message": "open"}],
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    (project_dir / "project.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "badregex",
                "macros": {"open": "macros/open.yaml"},
                "bindings": [
                    {
                        "keys": "ctrl+o",
                        "macro": "open",
                        "when": {"title": "(", "title_regex": True},
                    }
                ],
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    return project_dir


def test_build_autokey_entries_defaults_to_honest_skips_for_window_filters(tmp_path: Path) -> None:
    project = load_project(_make_project(tmp_path))
    entries, skipped = build_autokey_entries(project, command="python -m vhk.cli")
    assert entries == []
    assert {item.trigger or item.hotkey: item.skip_reason for item in skipped} == {
        ":off": "hotstring disabled",
        ":sig": (
            "AutoKey window filter cannot express selector fields honestly: "
            "AutoKey window filters match window title OR class with one regex; export requires approximation: class=Firefox"
        ),
        ":skip": "AutoKey window filter cannot express selector fields honestly: class+title intersection",
        "ctrl+shift+o": (
            "AutoKey window filter cannot express selector fields honestly: "
            "AutoKey window filters match window title OR class with one regex; export requires approximation: title~=Project Board"
        ),
        "alt_gr+s": "AutoKey hotkey export only supports simple keys/modifiers: alt_gr",
    }


def test_build_autokey_entries_allows_window_filter_approximation(tmp_path: Path) -> None:
    project = load_project(_make_project(tmp_path))
    entries, skipped = build_autokey_entries(
        project,
        command="python -m vhk.cli",
        allow_window_filter_approximation=True,
    )
    assert [(item.kind, item.macro, item.trigger or item.hotkey) for item in entries] == [
        ("binding", "open", "ctrl+shift+o"),
        ("hotstring", "sig", ":sig"),
    ]
    sig = next(item for item in entries if item.kind == "hotstring")
    assert sig.argv[:3] == ("python", "-m", "vhk.cli")
    assert sig.argv[-2:] == ("--return-var", "return_value")
    assert sig.window_filter_regex == "Firefox"
    assert sig.window_filter_label == "class≈Firefox"
    assert sig.approximate_window_filter is True
    binding = next(item for item in entries if item.kind == "binding")
    assert binding.window_filter_label == "title≈~=Project Board"
    assert binding.approximate_window_filter is True
    assert {item.trigger or item.hotkey: item.skip_reason for item in skipped} == {
        ":off": "hotstring disabled",
        ":skip": "AutoKey window filter cannot express selector fields honestly: class+title intersection",
        "alt_gr+s": "AutoKey hotkey export only supports simple keys/modifiers: alt_gr",
    }


def test_build_autokey_entries_skips_invalid_title_regex(tmp_path: Path) -> None:
    project = load_project(_make_invalid_regex_project(tmp_path))
    entries, skipped = build_autokey_entries(project, allow_window_filter_approximation=True)
    assert entries == []
    assert len(skipped) == 1
    assert skipped[0].skip_reason.startswith(
        "AutoKey window filter cannot express selector fields honestly: invalid title regex:"
    )


def test_write_autokey_pack_writes_scripts_metadata_and_manifest(tmp_path: Path) -> None:
    project = load_project(_make_project(tmp_path))
    out_dir = tmp_path / "autokey"
    manifest = write_autokey_pack(
        project,
        out_dir=out_dir,
        return_send_mode="shift-insert",
        allow_window_filter_approximation=True,
    )
    assert manifest.readme_path.exists()
    assert manifest.manifest_path.exists()
    assert len(manifest.entries) == 2
    payload = json.loads(manifest.manifest_path.read_text(encoding="utf-8"))
    assert payload["project"] == "proj"
    assert payload["entry_count"] == 2
    assert payload["skipped_count"] == 3
    assert payload["allow_window_filter_approximation"] is True
    assert payload["approximate_window_filter_count"] == 2
    sig_entry = next(item for item in manifest.entries if item.kind == "hotstring")
    script_text = sig_entry.script_path.read_text(encoding="utf-8")
    assert "system.exec_command(command, getOutput=True)" in script_text
    assert "Keyboard.SendMode.CB_SHIFT_INSERT" in script_text
    metadata = json.loads(sig_entry.metadata_path.read_text(encoding="utf-8"))
    assert metadata["type"] == "script"
    assert metadata["abbreviation"]["abbreviations"] == [":sig"]
    assert metadata["windowInfoRegex"] == "Firefox"
    binding_entry = next(item for item in manifest.entries if item.kind == "binding")
    binding_metadata = json.loads(binding_entry.metadata_path.read_text(encoding="utf-8"))
    assert binding_metadata["hotkey"] == {"modifiers": ["<ctrl>", "<shift>"], "hotKey": "o"}
    assert binding_metadata["windowInfoRegex"] == "Project Board"
    readme = manifest.readme_path.read_text(encoding="utf-8")
    assert "allow-window-filter-approximation" in readme
    assert "approximate AutoKey title-or-class scope" in readme


def test_gen_autokey_pack_cli_json_and_include_disabled(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)
    out_dir = tmp_path / "pack"
    result = runner.invoke(
        app,
        [
            "gen-autokey-pack",
            str(project_dir),
            str(out_dir),
            "--command",
            "python -m vhk.cli",
            "--return-send-mode",
            "ctrl-v",
            "--include-disabled",
            "--allow-window-filter-approximation",
            "--json",
        ],
    )
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["entry_count"] == 3
    assert payload["skipped_count"] == 2
    assert payload["return_send_mode"] == "ctrl-v"
    assert payload["allow_window_filter_approximation"] is True
    assert payload["approximate_window_filter_count"] == 2
    script_paths = [Path(item["script_path"]) for item in payload["entries"]]
    assert all(path.exists() for path in script_paths)
    disabled_script = next(Path(item["script_path"]) for item in payload["entries"] if item["trigger"] == ":off")
    assert "Keyboard.SendMode.CB_CTRL_V" in disabled_script.read_text(encoding="utf-8")
