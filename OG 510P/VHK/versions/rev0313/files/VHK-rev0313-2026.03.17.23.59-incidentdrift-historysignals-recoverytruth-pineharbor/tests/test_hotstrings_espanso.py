from __future__ import annotations

import json
from pathlib import Path

import yaml
from typer.testing import CliRunner

from vhk.cli import app


runner = CliRunner()


def _make_project(tmp_path: Path) -> Path:
    proj = tmp_path / "p"
    (proj / "macros").mkdir(parents=True)

    (proj / "macros" / "sig.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "sig",
                "steps": [
                    {"type": "Return", "value_expr": '"Best,\\nJane"', "out_var": "return_value"},
                ],
            }
        )
    )

    (proj / "project.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "p",
                "macros": {"sig": "macros/sig.yaml"},
                "hotstrings": [
                    {
                        "trigger": ":sig",
                        "macro": "sig",
                        "description": "Insert signature",
                        "mode": "return",
                        "force_mode": "clipboard",
                    }
                ],
            }
        )
    )
    return proj


def test_run_print_return_outputs_only_return_value(tmp_path: Path):
    proj = _make_project(tmp_path)

    result = runner.invoke(app, ["run", str(proj), "sig", "--print-return"])
    assert result.exit_code == 0, result.output

    # No trailing newline (stdout should be clean for integrations)
    assert result.output == "Best,\nJane"


def test_gen_espanso_json_includes_shell_cmd(tmp_path: Path):
    proj = _make_project(tmp_path)

    result = runner.invoke(app, ["gen-espanso", str(proj), "--json"])
    assert result.exit_code == 0, result.output

    payload = json.loads(result.output)
    assert "matches" in payload
    assert len(payload["matches"]) == 1

    m = payload["matches"][0]
    assert m["trigger"] == ":sig"
    assert m["replace"] == "{{output}}"
    assert m["label"] == "Insert signature"
    assert m["force_mode"] == "clipboard"

    cmd = m["vars"][0]["params"]["cmd"]
    assert "vhk" in cmd
    assert "run" in cmd
    assert "--quiet" in cmd
    assert "--print-return" in cmd
    assert "--return-var" in cmd


def test_gen_espanso_includes_form_when_layout_provided(tmp_path: Path):
    proj = tmp_path / "p"
    (proj / "macros").mkdir(parents=True)

    (proj / "macros" / "hello.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "hello",
                "steps": [
                    {"type": "Return", "value_expr": '"Hello " + name', "out_var": "return_value"},
                ],
            }
        )
    )

    (proj / "project.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "p",
                "macros": {"hello": "macros/hello.yaml"},
                "hotstrings": [
                    {
                        "trigger": ":hello",
                        "macro": "hello",
                        "description": "Hello prompt",
                        "mode": "return",
                        "form_layout": "Hello [[name]]",
                    }
                ],
            }
        )
    )

    result = runner.invoke(app, ["gen-espanso", str(proj), "--json"])
    assert result.exit_code == 0, result.output

    payload = json.loads(result.output)
    m = payload["matches"][0]
    assert m["trigger"] == ":hello"
    assert len(m["vars"]) == 2
    assert m["vars"][0]["type"] == "form"
    assert "layout" in m["vars"][0]["params"]
    cmd = m["vars"][1]["params"]["cmd"]
    # form variables should be injected into the JSON passed to --vars
    assert "--vars" in cmd
    assert "{{form1.name}}" in cmd


def test_gen_espanso_package_dir_groups_scoped_hotstrings(tmp_path: Path):
    proj = tmp_path / "p"
    (proj / "macros").mkdir(parents=True)

    (proj / "macros" / "a.yaml").write_text(yaml.safe_dump({"name": "a", "steps": [{"type": "Return", "value_expr": '"A"'}]}))
    (proj / "macros" / "b.yaml").write_text(yaml.safe_dump({"name": "b", "steps": [{"type": "Return", "value_expr": '"B"'}]}))

    (proj / "project.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "p",
                "macros": {"a": "macros/a.yaml", "b": "macros/b.yaml"},
                "hotstrings": [
                    {"trigger": ":a", "macro": "a", "mode": "return"},
                    {"trigger": ":b", "macro": "b", "mode": "return", "when": {"class": "Firefox"}},
                ],
            }
        )
    )

    out_dir = tmp_path / "espanso"
    result = runner.invoke(app, ["gen-espanso", str(proj), "--package-dir", str(out_dir)])
    assert result.exit_code == 0, result.output

    # Global match file should exist (no underscore).
    global_file = out_dir / "match" / "vhk_p.yml"
    assert global_file.exists()
    global_payload = yaml.safe_load(global_file.read_text())
    assert any(m["trigger"] == ":a" for m in global_payload.get("matches", []))

    # There should be a scoped match file + config file.
    scoped_files = list((out_dir / "match").glob("_vhk_p__*.yml"))
    assert len(scoped_files) == 1
    scoped_payload = yaml.safe_load(scoped_files[0].read_text())
    assert any(m["trigger"] == ":b" for m in scoped_payload.get("matches", []))

    cfg_files = list((out_dir / "config").glob("vhk_p__*.yml"))
    assert len(cfg_files) == 1
    cfg = yaml.safe_load(cfg_files[0].read_text())
    assert "filter_class" in cfg
    assert "Firefox" in cfg["filter_class"]
    assert "extra_includes" in cfg


def test_gen_espanso_package_dir_adds_composite_config_for_overlapping_scopes(tmp_path: Path):
    proj = tmp_path / "p"
    (proj / "macros").mkdir(parents=True)

    (proj / "macros" / "firefox.yaml").write_text(yaml.safe_dump({"name": "firefox", "steps": [{"type": "Return", "value_expr": '"F"'}]}))
    (proj / "macros" / "inbox.yaml").write_text(yaml.safe_dump({"name": "inbox", "steps": [{"type": "Return", "value_expr": '"I"'}]}))

    (proj / "project.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "p",
                "macros": {"firefox": "macros/firefox.yaml", "inbox": "macros/inbox.yaml"},
                "hotstrings": [
                    {"trigger": ":ff", "macro": "firefox", "mode": "return", "when": {"class": "Firefox"}},
                    {"trigger": ":in", "macro": "inbox", "mode": "return", "when": {"title": "Inbox"}},
                ],
            }
        )
    )

    out_dir = tmp_path / "espanso"
    result = runner.invoke(app, ["gen-espanso", str(proj), "--package-dir", str(out_dir)])
    assert result.exit_code == 0, result.output

    cfg_files = sorted((out_dir / "config").glob("vhk_p__*.yml"))
    assert len(cfg_files) == 3

    match_files = sorted((out_dir / "match").glob("_vhk_p__*.yml"))
    first_cfg = yaml.safe_load(cfg_files[0].read_text())
    assert first_cfg["filter_class"] == "Firefox"
    assert first_cfg["filter_title"] == "Inbox"
    includes = set(first_cfg["extra_includes"])
    assert len(includes) == 2
    assert includes == {f"../match/{item.name}" for item in match_files}

    manifest = json.loads((out_dir / "pack.json").read_text())
    assert manifest["synthetic_config_count"] == 1
    assert any(item["synthetic"] for item in manifest["configs"])

    readme = (out_dir / "README.md").read_text()
    assert "only one app-specific config" in readme
    assert "synthetic composite" in readme


def test_gen_espanso_package_dir_specific_config_includes_less_specific_match_file(tmp_path: Path):
    proj = tmp_path / "p"
    (proj / "macros").mkdir(parents=True)

    (proj / "macros" / "base.yaml").write_text(yaml.safe_dump({"name": "base", "steps": [{"type": "Return", "value_expr": '"B"'}]}))
    (proj / "macros" / "narrow.yaml").write_text(yaml.safe_dump({"name": "narrow", "steps": [{"type": "Return", "value_expr": '"N"'}]}))

    (proj / "project.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "p",
                "macros": {"base": "macros/base.yaml", "narrow": "macros/narrow.yaml"},
                "hotstrings": [
                    {"trigger": ":base", "macro": "base", "mode": "return", "when": {"class": "Firefox"}},
                    {"trigger": ":narrow", "macro": "narrow", "mode": "return", "when": {"class": "Firefox", "title": "Inbox"}},
                ],
            }
        )
    )

    out_dir = tmp_path / "espanso"
    result = runner.invoke(app, ["gen-espanso", str(proj), "--package-dir", str(out_dir)])
    assert result.exit_code == 0, result.output

    cfg_files = sorted((out_dir / "config").glob("vhk_p__*.yml"))
    match_files = sorted((out_dir / "match").glob("_vhk_p__*.yml"))
    first_cfg = yaml.safe_load(cfg_files[0].read_text())
    assert first_cfg["filter_class"] == "Firefox"
    assert first_cfg["filter_title"] == "Inbox"
    includes = set(first_cfg["extra_includes"])
    assert len(includes) == 2
    assert includes == {f"../match/{item.name}" for item in match_files}
