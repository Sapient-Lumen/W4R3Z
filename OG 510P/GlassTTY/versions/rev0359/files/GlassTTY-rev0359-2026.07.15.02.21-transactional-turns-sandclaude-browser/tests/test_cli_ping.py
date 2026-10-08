from __future__ import annotations

import json
from pathlib import Path

import pytest

from glassttyd.broker import BrokerServer
from glassttyd.cli import build_parser


def test_ping_requires_a_live_broker(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GLASSTTY_HOME", str(tmp_path))
    args = build_parser().parse_args(["ping", "--timeout", "0.1"])

    with pytest.raises(SystemExit, match="broker socket not found"):
        args.func(args)


def test_ping_proves_broker_round_trip(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setenv("GLASSTTY_HOME", str(tmp_path))
    socket_path = tmp_path / "run" / "daemon.sock"
    server = BrokerServer(
        socket_path,
        emit_to_extension=lambda _message: None,
        status_provider=lambda: {"owner": "test-native-host"},
    )
    server.start()
    try:
        args = build_parser().parse_args(["ping", "--timeout", "1"])
        assert args.func(args) == 0
    finally:
        server.stop()

    report = json.loads(capsys.readouterr().out)
    assert report["ok"] is True
    assert report["mode"] == "broker-round-trip"
    assert report["socket_path"] == str(socket_path)
    assert report["broker"]["ok"] is True
    assert report["broker"]["owner"] == "test-native-host"
