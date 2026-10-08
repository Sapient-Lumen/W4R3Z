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
    (proj / "macros" / "sig.yaml").write_text(yaml.safe_dump({"name": "sig", "steps": []}))
    (proj / "macros" / "alt.yaml").write_text(yaml.safe_dump({"name": "alt", "steps": []}))
    (proj / "project.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "p",
                "settings": {"event_log": True, "log_dir": "logs"},
                "macros": {"sig": "macros/sig.yaml", "alt": "macros/alt.yaml"},
            }
        )
    )
    return proj


def _write_log(path: Path, *, project_root: Path | None = None, run_id: str, macro: str, ok: bool, end_ts: float, wait_kind: str | None = None) -> None:
    run_start = {"type": "run_start", "ts": end_ts - 1.0, "run_id": run_id, "macro": macro}
    if project_root is not None:
        run_start["macro_proof_contract"] = summarize_macro_proof_contract(project_root, macro)
    events = [json.dumps(run_start)]
    if wait_kind:
        events.append(json.dumps({"type": "wait_attempt", "ts": end_ts - 0.6, "kind": wait_kind}))
    events.append(json.dumps({"type": "run_end", "ts": end_ts, "run_id": run_id, "macro": macro, "ok": ok}))
    path.write_text("\n".join(events) + "\n", encoding="utf-8")


def test_macro_latest_run_json_is_macro_scoped_not_project_latest(tmp_path: Path):
    proj = _make_project(tmp_path)
    _write_log(proj / "logs" / "run_sig.jsonl", project_root=proj, run_id="sig-run", macro="sig", ok=True, end_ts=2.0, wait_kind="image")
    _write_log(proj / "logs" / "run_alt.jsonl", project_root=proj, run_id="alt-run", macro="alt", ok=False, end_ts=3.0)

    res = runner.invoke(app, ["macro-latest-run-json", str(proj), "sig", "--no-pretty"])
    assert res.exit_code == 0, res.output
    payload = json.loads(res.stdout)
    assert payload["stack_kind"] == "vhk.project.macro_latest_run"
    assert payload["macro"]["name"] == "sig"
    assert payload["latest_run"]["macro"] == "sig"
    assert payload["latest_run"]["run_id"] == "sig-run"
    assert payload["latest_run_health"]["verdict"] == "healthy"
    assert payload["replay_posture"]["id"] == "verified_recent"
    assert payload["default_trace_out"]["relative_to_project"] == "build/traces/sig.latest.trace.json"
    assert payload["preferred_entrypoints"]["latest_report"] == "macro_report_latest.sh sig"


def test_macro_latest_run_json_handles_missing_matching_history(tmp_path: Path):
    proj = _make_project(tmp_path)
    _write_log(proj / "logs" / "run_alt.jsonl", project_root=proj, run_id="alt-run", macro="alt", ok=True, end_ts=3.0)

    res = runner.invoke(app, ["macro-latest-run-json", str(proj), "sig", "--no-pretty"])
    assert res.exit_code == 0, res.output
    payload = json.loads(res.stdout)
    assert payload["latest_run"] is None
    assert payload["latest_run_health"] is None
    assert payload["replay_posture"]["id"] == "unverified"
    assert payload["next_step"]["command"] == "run_macro.sh sig"


def test_macro_latest_run_json_rejects_unknown_macro(tmp_path: Path):
    proj = _make_project(tmp_path)
    res = runner.invoke(app, ["macro-latest-run-json", str(proj), "missing"])
    assert res.exit_code != 0
    assert "Unknown macro 'missing'" in res.output



def test_macro_latest_run_json_marks_replay_stale_after_source_change(tmp_path: Path):
    proj = _make_project(tmp_path)
    contract = summarize_macro_proof_contract(proj, 'sig')
    log_path = proj / 'logs' / 'run_sig.jsonl'
    log_path.write_text(
        "\n".join(
            [
                json.dumps({"type": "run_start", "ts": 1.0, "run_id": "sig-run", "macro": "sig", "macro_proof_contract": contract}),
                json.dumps({"type": "run_end", "ts": 2.0, "run_id": "sig-run", "macro": "sig", "ok": True}),
            ]
        ) + "\n",
        encoding='utf-8',
    )
    (proj / 'macros' / 'sig.yaml').write_text(yaml.safe_dump({"name": "sig", "steps": [{"type": "TypeText", "text": "changed"}]}), encoding='utf-8')

    res = runner.invoke(app, ['macro-latest-run-json', str(proj), 'sig', '--no-pretty'])
    assert res.exit_code == 0, res.output
    payload = json.loads(res.stdout)
    assert payload['latest_run_health']['verdict'] == 'stale'
    assert payload['replay_posture']['id'] == 'stale_contract'
    assert payload['latest_run_health']['next_step']['id'] == 'rerun_after_contract_change'
    assert payload['latest_run_health']['proof_contract']['in_sync'] is False
    assert payload['latest_run_health']['proof_contract']['source_changed'] is True


def test_macro_latest_run_json_marks_replay_stale_after_session_change(tmp_path: Path):
    proj = _make_project(tmp_path)
    log_path = proj / "logs" / "run_sig.jsonl"
    log_path.write_text(
        "\n".join(
            [
                json.dumps({
                    "type": "run_start",
                    "ts": 1.0,
                    "run_id": "sig-run",
                    "macro": "sig",
                    "macro_proof_contract": summarize_macro_proof_contract(proj, "sig"),
                    "desktop_session_contract": {
                        "display": ":0",
                        "xauthority": "/tmp/xauth0",
                        "i3sock": "/tmp/i3-0.sock",
                        "session_type": "x11",
                        "current_desktop": "i3",
                    },
                }),
                json.dumps({"type": "run_end", "ts": 2.0, "run_id": "sig-run", "macro": "sig", "ok": True}),
            ]
        ) + "\n",
        encoding="utf-8",
    )

    env = {**os.environ, "DISPLAY": ":1", "XAUTHORITY": "/tmp/xauth1", "I3SOCK": "/tmp/i3-1.sock", "XDG_SESSION_TYPE": "x11", "XDG_CURRENT_DESKTOP": "i3"}
    res = runner.invoke(app, ["macro-latest-run-json", str(proj), "sig", "--no-pretty"], env=env)
    assert res.exit_code == 0, res.output
    payload = json.loads(res.stdout)
    assert payload["latest_run_health"]["verdict"] == "stale"
    assert payload["replay_posture"]["id"] == "stale_contract"
    assert payload["latest_run_health"]["next_step"]["id"] == "rerun_after_session_change"
    assert payload["latest_run_health"]["desktop_session_contract"]["display_changed"] is True



def test_macro_latest_run_json_marks_healthy_run_with_selector_but_no_probe_as_target_unproven(tmp_path: Path):
    from vhk.project.desktop_session_contract import summarize_desktop_session_contract

    proj = _make_project(tmp_path)
    (proj / "macros" / "sig.yaml").write_text(yaml.safe_dump({"name": "sig", "when": {"class": "Alacritty", "workspace": "2"}, "steps": []}), encoding="utf-8")
    log_path = proj / "logs" / "run_sig.jsonl"
    log_path.write_text(
        "\n".join(
            [
                json.dumps({
                    "type": "run_start",
                    "ts": 1.0,
                    "run_id": "sig-run",
                    "macro": "sig",
                    "macro_proof_contract": summarize_macro_proof_contract(proj, "sig"),
                    "desktop_session_contract": summarize_desktop_session_contract(),
                }),
                json.dumps({"type": "run_end", "ts": 2.0, "run_id": "sig-run", "macro": "sig", "ok": True}),
            ]
        ) + "\n",
        encoding="utf-8",
    )

    res = runner.invoke(app, ["macro-latest-run-json", str(proj), "sig", "--no-pretty"])
    assert res.exit_code == 0, res.output
    payload = json.loads(res.stdout)
    assert payload["latest_run_health"]["verdict"] == "healthy"
    assert payload["latest_run_health"]["target_authority"]["status_id"] == "weak_replay_target_authority"
    assert payload["replay_posture"]["id"] == "verified_recent_target_unproven"
    assert payload["replay_posture"]["target_authority_status_id"] == "weak_replay_target_authority"
    assert payload["next_step"]["id"] == "inspect_partial_target_proof"
    assert payload["next_step"]["command"] == "macro_dispatch_gate_json.sh sig"
