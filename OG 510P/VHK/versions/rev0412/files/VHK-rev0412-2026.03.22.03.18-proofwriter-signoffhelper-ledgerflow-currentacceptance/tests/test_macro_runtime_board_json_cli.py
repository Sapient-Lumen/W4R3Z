from __future__ import annotations

from pathlib import Path
import json
import os

import yaml
from typer.testing import CliRunner

from vhk.cli import app
from vhk.project.macro_proof_contract import summarize_macro_proof_contract


runner = CliRunner()


def _make_project(tmp_path: Path) -> Path:
    proj = tmp_path / "p"
    (proj / "macros").mkdir(parents=True)
    (proj / "logs").mkdir(parents=True)

    (proj / "macros" / "ready.yaml").write_text(
        yaml.safe_dump({"name": "ready", "steps": [{"type": "TypeText", "text": "ready"}]})
    )
    (proj / "macros" / "candidate.yaml").write_text(
        yaml.safe_dump({"name": "candidate", "steps": [{"type": "TypeText", "text": "candidate"}]})
    )
    (proj / "macros" / "prompty.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "prompty",
                "steps": [
                    {"type": "PromptForm", "fields": [{"name": "name", "label": "Name"}]},
                    {"type": "TypeText", "text": "hi"},
                ],
            }
        )
    )
    (proj / "macros" / "stale.yaml").write_text(
        yaml.safe_dump({"name": "stale", "steps": [{"type": "TypeText", "text": "stale"}]})
    )

    (proj / "project.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "p",
                "settings": {"event_log": True, "log_dir": "logs"},
                "macros": {
                    "ready": "macros/ready.yaml",
                    "candidate": "macros/candidate.yaml",
                    "prompty": "macros/prompty.yaml",
                    "stale": "macros/stale.yaml",
                },
            }
        )
    )

    sidecar_payload = {"segments": [{"selector_kind": "stable", "transition_reason": "focus", "anchor": {"mode": "window"}}]}
    for name, ts in [("ready", 3000), ("candidate", 3000), ("prompty", 3000)]:
        sidecar = proj / "macros" / f"{name}.window-context.yaml"
        sidecar.write_text(yaml.safe_dump(sidecar_payload, sort_keys=False))
        os.utime(sidecar, (ts, ts))
        os.utime(proj / "macros" / f"{name}.yaml", (ts, ts))
    os.utime(proj / "macros" / "stale.yaml", (3000, 3000))

    with (proj / "logs" / "run_ready.jsonl").open("w", encoding="utf-8") as fh:
        fh.write(json.dumps({"type": "run_start", "macro": "ready", "run_id": "run-ready", "ts": 1.0, "macro_proof_contract": summarize_macro_proof_contract(proj, "ready")}) + "\n")
        fh.write(json.dumps({"type": "run_end", "macro": "ready", "run_id": "run-ready", "ts": 2.0, "ok": True}) + "\n")

    return proj


def test_macro_runtime_board_json_reports_execution_posture(tmp_path: Path):
    proj = _make_project(tmp_path)

    res = runner.invoke(app, ["macro-runtime-board-json", str(proj)])
    assert res.exit_code == 0, res.output
    payload = json.loads(res.stdout)

    assert payload["stack_kind"] == "vhk.project.macro_runtime_board"
    assert payload["project"]["macro_count"] == 4
    assert payload["project"]["resident_runtime_macro_count"] == 2
    assert payload["summary"]["primary_macro_name"] == "ready"
    assert payload["summary"]["primary_posture_id"] == "warm_dispatch_ready"
    assert payload["summary"]["counts_by_posture_id"]["warm_dispatch_ready"] == 1
    assert payload["summary"]["counts_by_posture_id"]["warm_dispatch_candidate"] == 1
    assert payload["summary"]["counts_by_posture_id"]["direct_run_only"] == 1
    assert payload["summary"]["counts_by_posture_id"]["stabilize_first"] == 1

    assert [item["name"] for item in payload["macros"]] == ["ready", "candidate", "prompty", "stale"]

    ready = payload["macros"][0]
    assert ready["runtime_posture"]["id"] == "warm_dispatch_ready"
    assert ready["runtime_posture"]["dispatch_safe_now"] is True
    assert ready["preferred_execution_mode"] == "warm_runtime_dispatch"
    assert ready["preferred_entrypoints"]["warm_runtime"] == "dispatch_macro.sh ready"
    assert ready["preferred_entrypoints"]["warm_runtime_checked"] == "dispatch_macro_checked.sh ready"
    assert ready["preferred_entrypoints"]["warm_runtime_gate"] == "macro_dispatch_gate_json.sh ready"

    candidate = payload["macros"][1]
    assert candidate["runtime_posture"]["id"] == "warm_dispatch_candidate"
    assert candidate["recording"]["freshness_status"] == "aligned"
    assert candidate["latest_run_context"]["scope"] == "none"
    assert candidate["latest_run_context"]["replay_posture_id"] == "unverified"

    prompty = payload["macros"][2]
    assert prompty["runtime_posture"]["id"] == "direct_run_only"
    assert prompty["preferred_execution_mode"] == "direct_run"
    assert prompty["preferred_entrypoints"]["direct_run"] == "run_macro.sh prompty"

    stale = payload["macros"][3]
    assert stale["runtime_posture"]["id"] == "stabilize_first"
    assert stale["runtime_posture"]["command"] == "record_macro.sh stale 5000"
