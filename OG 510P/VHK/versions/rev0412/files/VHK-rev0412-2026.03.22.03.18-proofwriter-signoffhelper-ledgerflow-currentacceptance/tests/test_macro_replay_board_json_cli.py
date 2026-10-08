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

    for name in ["ready", "warny", "broken", "fresh"]:
        (proj / "macros" / f"{name}.yaml").write_text(
            yaml.safe_dump({"name": name, "steps": [{"type": "TypeText", "text": name}]})
        )
        os.utime(proj / "macros" / f"{name}.yaml", (3000, 3000))

    (proj / "project.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "p",
                "settings": {"event_log": True, "log_dir": "logs"},
                "macros": {
                    "ready": "macros/ready.yaml",
                    "warny": "macros/warny.yaml",
                    "broken": "macros/broken.yaml",
                    "fresh": "macros/fresh.yaml",
                },
            }
        )
    )

    ready_contract = summarize_macro_proof_contract(proj, "ready")
    warny_contract = summarize_macro_proof_contract(proj, "warny")
    broken_contract = summarize_macro_proof_contract(proj, "broken")

    (proj / "logs" / "run_ready.jsonl").write_text(
        "\n".join(
            [
                json.dumps({"type": "run_start", "ts": 1.0, "run_id": "run-ready", "macro": "ready", "macro_proof_contract": ready_contract}),
                json.dumps({"type": "run_end", "ts": 2.0, "run_id": "run-ready", "macro": "ready", "ok": True}),
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (proj / "logs" / "run_warn.jsonl").write_text(
        "\n".join(
            [
                json.dumps({"type": "run_start", "ts": 3.0, "run_id": "run-warn", "macro": "warny", "macro_proof_contract": warny_contract}),
                json.dumps({"type": "wait_start", "kind": "image", "ts": 3.1}),
                json.dumps({"type": "wait_end", "kind": "image", "ts": 6.5, "ok": True}),
                json.dumps({"type": "run_end", "ts": 7.0, "run_id": "run-warn", "macro": "warny", "ok": True}),
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (proj / "logs" / "run_broken.jsonl").write_text(
        "\n".join(
            [
                json.dumps({"type": "run_start", "ts": 8.0, "run_id": "run-broken", "macro": "broken", "macro_proof_contract": broken_contract}),
                json.dumps({"type": "step_end", "ts": 8.4, "step_id": "s1", "step_type": "Click", "ok": False, "duration_ms": 100, "error": "boom", "error_type": "AssertionError"}),
                json.dumps({"type": "run_end", "ts": 9.0, "run_id": "run-broken", "macro": "broken", "ok": False}),
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return proj


def test_macro_replay_board_json_reports_per_macro_latest_run_truth(tmp_path: Path):
    proj = _make_project(tmp_path)

    res = runner.invoke(app, ["macro-replay-board-json", str(proj)])
    assert res.exit_code == 0, res.output
    payload = json.loads(res.stdout)

    assert payload["stack_kind"] == "vhk.project.macro_replay_board"
    assert payload["project"]["macro_count"] == 4
    assert payload["project"]["verified_recent_macro_count"] == 1
    assert payload["summary"]["primary_macro_name"] == "ready"
    assert payload["summary"]["primary_posture_id"] == "verified_recent"
    assert payload["summary"]["counts_by_posture_id"]["verified_recent"] == 1
    assert payload["summary"]["counts_by_posture_id"]["warning_recent"] == 1
    assert payload["summary"]["counts_by_posture_id"]["failed_recent"] == 1
    assert payload["summary"]["counts_by_posture_id"]["unverified"] == 1

    assert [item["name"] for item in payload["macros"]] == ["ready", "warny", "broken", "fresh"]

    ready = payload["macros"][0]
    assert ready["replay_posture"]["id"] == "verified_recent"
    assert ready["latest_run_context"]["scope"] == "matching_macro"
    assert ready["latest_run_context"]["latest_run"]["run_id"] == "run-ready"
    assert ready["latest_run_context"]["latest_run_health"]["verdict"] == "healthy"

    warny = payload["macros"][1]
    assert warny["replay_posture"]["id"] == "warning_recent"
    assert warny["latest_run_context"]["latest_run_health"]["verdict"] == "warn"

    broken = payload["macros"][2]
    assert broken["replay_posture"]["id"] == "failed_recent"
    assert broken["latest_run_context"]["latest_run_health"]["verdict"] == "fail"

    fresh = payload["macros"][3]
    assert fresh["replay_posture"]["id"] == "unverified"
    assert fresh["latest_run_context"]["scope"] == "none"
    assert fresh["latest_run_context"]["latest_run"] is None



def test_macro_replay_board_json_reports_stale_contract_runs(tmp_path: Path):
    proj = _make_project(tmp_path)
    contract = summarize_macro_proof_contract(proj, 'ready')
    (proj / 'logs' / 'run_ready.jsonl').write_text(
        "\n".join(
            [
                json.dumps({"type": "run_start", "ts": 1.0, "run_id": "run-ready", "macro": "ready", "macro_proof_contract": contract}),
                json.dumps({"type": "run_end", "ts": 2.0, "run_id": "run-ready", "macro": "ready", "ok": True}),
            ]
        ) + "\n",
        encoding='utf-8',
    )
    (proj / 'macros' / 'ready.yaml').write_text(yaml.safe_dump({"name": "ready", "steps": [{"type": "TypeText", "text": "changed"}]}), encoding='utf-8')

    res = runner.invoke(app, ['macro-replay-board-json', str(proj), '--pretty'])
    assert res.exit_code == 0, res.output
    payload = json.loads(res.stdout)
    ready = next(item for item in payload['macros'] if item['name'] == 'ready')
    assert ready['replay_posture']['id'] == 'stale_contract'
    assert ready['latest_run_context']['latest_run_health']['verdict'] == 'stale'
    assert payload['summary']['counts_by_posture_id']['stale_contract'] == 1


def test_macro_replay_board_json_reports_stale_session_runs(tmp_path: Path):
    proj = _make_project(tmp_path)
    (proj / "logs" / "run_ready.jsonl").write_text(
        "\n".join(
            [
                json.dumps({
                    "type": "run_start",
                    "ts": 1.0,
                    "run_id": "run-ready",
                    "macro": "ready",
                    "macro_proof_contract": summarize_macro_proof_contract(proj, "ready"),
                    "desktop_session_contract": {
                        "display": ":0",
                        "xauthority": "/tmp/xauth0",
                        "i3sock": "/tmp/i3-0.sock",
                        "session_type": "x11",
                        "current_desktop": "i3",
                    },
                }),
                json.dumps({"type": "run_end", "ts": 2.0, "run_id": "run-ready", "macro": "ready", "ok": True}),
            ]
        ) + "\n",
        encoding="utf-8",
    )

    env = {**os.environ, "DISPLAY": ":1", "XAUTHORITY": "/tmp/xauth1", "I3SOCK": "/tmp/i3-1.sock", "XDG_SESSION_TYPE": "x11", "XDG_CURRENT_DESKTOP": "i3"}
    res = runner.invoke(app, ["macro-replay-board-json", str(proj), "--pretty"], env=env)
    assert res.exit_code == 0, res.output
    payload = json.loads(res.stdout)
    ready = next(item for item in payload["macros"] if item["name"] == "ready")
    assert ready["replay_posture"]["id"] == "stale_contract"
    assert ready["latest_run_context"]["latest_run_health"]["desktop_session_contract"]["i3sock_changed"] is True
