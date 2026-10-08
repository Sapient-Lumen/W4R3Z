from __future__ import annotations

from pathlib import Path

import yaml

from vhk.core.runner import Runner
from vhk.project.loader import load_project
from vhk.system import notify as notify_mod


def _write_project(tmp_path: Path, manifest: dict, macros: dict[str, dict]) -> Path:
    proj = tmp_path / "proj"
    (proj / "macros").mkdir(parents=True)
    for name, data in macros.items():
        (proj / "macros" / f"{name}.yaml").write_text(yaml.safe_dump(data), encoding="utf-8")
    (proj / "project.yaml").write_text(yaml.safe_dump(manifest), encoding="utf-8")
    return proj


def test_notify_send_builds_notify_send_command_and_parses_id(monkeypatch) -> None:
    calls: list[list[str]] = []

    class Proc:
        returncode = 0
        stdout = "42\nopen_logs\n"
        stderr = ""

    monkeypatch.setattr(notify_mod, "choose_backend", lambda: notify_mod.NotifyBackend(name="notify-send", exe="/usr/bin/notify-send"))
    monkeypatch.setattr(notify_mod.subprocess, "run", lambda cmd, **kw: calls.append(list(cmd)) or Proc())

    result = notify_mod.send(
        "Sync complete",
        body="Uploaded logs",
        urgency="critical",
        app_name="VHK",
        icon="dialog-information",
        category="transfer.complete",
        timeout_ms=5000,
        replace_id=7,
        transient=True,
        progress=65,
        actions=[("open_logs", "Open logs")],
        wait=True,
        print_id=True,
    )

    assert result.backend == "notify-send"
    assert result.notification_id == 42
    assert result.action_id == "open_logs"
    assert calls == [[
        "/usr/bin/notify-send",
        "--app-name", "VHK",
        "--urgency", "critical",
        "--icon", "dialog-information",
        "--category", "transfer.complete",
        "--expire-time", "5000",
        "--replace-id", "7",
        "--transient",
        "--hint", "INT:value:65",
        "--action", "open_logs=Open logs",
        "--print-id",
        "--wait",
        "Sync complete",
        "Uploaded logs",
    ]]


def test_notify_send_builds_dunstify_command_and_transient_hint(monkeypatch) -> None:
    calls: list[list[str]] = []

    class Proc:
        returncode = 0
        stdout = "99\nretry\n"
        stderr = ""

    monkeypatch.setattr(notify_mod, "choose_backend", lambda: notify_mod.NotifyBackend(name="dunstify", exe="/usr/bin/dunstify"))
    monkeypatch.setattr(notify_mod.subprocess, "run", lambda cmd, **kw: calls.append(list(cmd)) or Proc())

    result = notify_mod.send(
        "Volume",
        body="80%",
        urgency="normal",
        app_name="VHK",
        icon="audio-volume-high",
        category="device",
        timeout_ms=1200,
        replace_id=41,
        transient=True,
        progress=80,
        actions=[("retry", "Retry")],
        wait=True,
        print_id=True,
    )

    assert result.backend == "dunstify"
    assert result.notification_id == 99
    assert result.action_id == "retry"
    assert calls == [[
        "/usr/bin/dunstify",
        "--appname", "VHK",
        "--urgency", "normal",
        "--icon", "audio-volume-high",
        "--category", "device",
        "--timeout", "1200",
        "--replace", "41",
        "--hints", "BOOLEAN:transient:true",
        "--hints", "INT:value:80",
        "--action", "retry,Retry",
        "--printid",
        "--block",
        "Volume",
        "80%",
    ]]


def test_notify_step_captures_selected_action_and_progress(tmp_path: Path, monkeypatch) -> None:
    proj = _write_project(
        tmp_path,
        {"name": "p", "settings": {"event_log": False}, "macros": {"m": "macros/m.yaml"}},
        {
            "m": {
                "name": "m",
                "steps": [
                    {
                        "type": "Notify",
                        "summary": "Transfer ready",
                        "body": "Choose what to do with ${file}",
                        "progress": "${percent}",
                        "actions": [
                            {"id": "open", "label": "Open ${file}"},
                            {"id": "dismiss", "label": "Dismiss"},
                        ],
                        "out_action": "selected_action",
                    },
                ],
            }
        },
    )

    import vhk.core.runner as runner_mod

    calls: list[dict[str, object]] = []

    def fake_send(summary, body=None, urgency="normal", **kwargs):
        payload = {"summary": summary, "body": body, "urgency": urgency, **kwargs}
        calls.append(payload)
        return notify_mod.NotifyResult(backend="dunstify", action_id="open")

    monkeypatch.setattr(runner_mod.notify_mod, "send", fake_send)

    res = Runner(load_project(proj)).run("m", initial_vars={"file": "bundle.zip", "percent": 73})
    assert res.ok
    assert res.vars["selected_action"] == "open"
    assert res.vars["last_notification_action"] == "open"
    assert calls[0]["progress"] == 73
    assert calls[0]["wait"] is True
    assert calls[0]["actions"] == [("open", "Open bundle.zip"), ("dismiss", "Dismiss")]



def test_notify_step_round_trips_notification_id_into_later_replace_id(tmp_path: Path, monkeypatch) -> None:
    proj = _write_project(
        tmp_path,
        {"name": "p", "settings": {"event_log": False}, "macros": {"m": "macros/m.yaml"}},
        {
            "m": {
                "name": "m",
                "steps": [
                    {
                        "type": "Notify",
                        "summary": "Upload started",
                        "body": "Sending ${file}",
                        "app_name": "VHK",
                        "category": "transfer.progress",
                        "timeout_ms": 1500,
                        "transient": True,
                        "out_id": "upload_notice_id",
                    },
                    {
                        "type": "Notify",
                        "summary": "Upload finished",
                        "body": "Sent ${file}",
                        "replace_id": "${upload_notice_id}",
                        "icon": "dialog-information",
                    },
                ],
            }
        },
    )

    import vhk.core.runner as runner_mod

    calls: list[dict[str, object]] = []
    ids = iter([77, None])

    def fake_send(summary, body=None, urgency="normal", **kwargs):
        payload = {"summary": summary, "body": body, "urgency": urgency, **kwargs}
        calls.append(payload)
        return notify_mod.NotifyResult(backend="notify-send", notification_id=next(ids))

    monkeypatch.setattr(runner_mod.notify_mod, "send", fake_send)

    res = Runner(load_project(proj)).run("m", initial_vars={"file": "logs.tar.zst"})
    assert res.ok
    assert res.vars["upload_notice_id"] == 77
    assert res.vars["last_notification_id"] == 77
    assert calls[0]["summary"] == "Upload started"
    assert calls[0]["body"] == "Sending logs.tar.zst"
    assert calls[0]["app_name"] == "VHK"
    assert calls[0]["category"] == "transfer.progress"
    assert calls[0]["timeout_ms"] == 1500
    assert calls[0]["transient"] is True
    assert calls[0]["print_id"] is True
    assert calls[1]["summary"] == "Upload finished"
    assert calls[1]["body"] == "Sent logs.tar.zst"
    assert calls[1]["replace_id"] == 77
    assert calls[1]["icon"] == "dialog-information"
    assert calls[1]["print_id"] is False
