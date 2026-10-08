from __future__ import annotations

from pathlib import Path
import json

import yaml
from typer.testing import CliRunner

from vhk.cli import app


runner = CliRunner()


def _make_project(tmp_path: Path) -> Path:
    proj = tmp_path / "contract"
    (proj / "macros").mkdir(parents=True)
    (proj / "macros" / "deploy.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "deploy",
                "group": "ops",
                "tags": ["shell", "ops"],
                "voice_phrases": ["deploy now"],
                "presets": [
                    {
                        "name": "staging",
                        "vars": {"env": "staging", "confirm": False},
                        "prompt_form": {
                            "profile_key": "deploy.staging",
                            "fields": [
                                {"name": "ticket", "kind": "text", "label": "Ticket", "remember": True},
                                {"name": "window", "kind": "choice", "choices": ["blue", "green"]},
                            ],
                        },
                    }
                ],
                "steps": [
                    {"type": "PromptForm", "profile_key": "deploy.run", "fields": [{"name": "reason", "kind": "multiline"}]},
                    {"type": "RunShell", "command": "echo deploy"},
                    {"type": "Return", "value_expr": '"ok"', "out_var": "return_value"},
                ],
            }
        )
    )
    (proj / "project.yaml").write_text(
        yaml.safe_dump({"name": "contract", "macros": {"deploy": "macros/deploy.yaml"}})
    )
    return proj


def test_macro_contract_json_reports_invocation_shape(tmp_path: Path):
    proj = _make_project(tmp_path)
    res = runner.invoke(app, ["macro-contract-json", str(proj), "deploy", "--no-pretty"])
    assert res.exit_code == 0, res.output
    payload = json.loads(res.stdout)
    assert payload["stack_kind"] == "vhk.project.macro_contract"
    assert payload["macro"]["name"] == "deploy"
    assert payload["macro"]["hints"]["has_interactive_inputs"] is True
    assert set(payload["macro"]["hints"]["capability_tags"]) >= {"network_process", "prompts"}
    assert payload["invocation"]["direct_run"]["argv"][:4] == ["vhk", "run", str(proj.resolve()), "deploy"]
    assert "--preset <name>" in payload["invocation"]["direct_run"]["common_options"]
    assert payload["invocation"]["generated_stack"]["contract_wrapper"] == "macro_contract_json.sh deploy"
    assert payload["invocation"]["generated_stack"]["author_loop_wrapper"] == "macro_author_loop_json.sh deploy"
    assert payload["invocation"]["generated_stack"]["recording_review_wrapper"] == "macro_recording_json.sh deploy"
    assert payload["invocation"]["warm_runtime_dispatch"]["bus_payload_minimal"] == {"macro": "deploy"}
    assert payload["macro"]["desktop_target"]["selector_source_id"] == "none"
    assert payload["authoring"]["workflow"]["generated_stack_examples"]["author_loop"] == "macro_author_loop_json.sh deploy"
    assert payload["preset_names"] == ["staging"]
    assert payload["preset_var_keys"] == ["confirm", "env"]
    preset = payload["macro"]["presets"][0]
    assert preset["prompt_form"]["profile_key"] == "deploy.staging"
    assert preset["prompt_form"]["fields"][1]["choices"] == ["blue", "green"]
    prompt_step = payload["macro"]["prompt_steps"][0]
    assert prompt_step["type"] == "PromptForm"
    assert prompt_step["profile_key"] == "deploy.run"


def test_macro_contract_json_rejects_unknown_macro(tmp_path: Path):
    proj = _make_project(tmp_path)
    res = runner.invoke(app, ["macro-contract-json", str(proj), "missing"])
    assert res.exit_code != 0
    assert "Unknown macro 'missing'" in res.output
