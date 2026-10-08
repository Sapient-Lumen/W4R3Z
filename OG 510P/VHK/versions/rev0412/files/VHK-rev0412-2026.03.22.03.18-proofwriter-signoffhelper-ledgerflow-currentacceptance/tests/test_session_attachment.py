from vhk.project.session_attachment import summarize_activation_environment, summarize_runtime_service_environment, summarize_session_attachment


def test_summarize_activation_environment_detects_drift():
    payload = summarize_activation_environment(
        shell_env={
            "DISPLAY": ":0",
            "XAUTHORITY": "/run/user/1000/gdm/Xauthority",
            "XDG_RUNTIME_DIR": "/run/user/1000",
        },
        activation_environment={
            "DISPLAY": ":1",
            "XDG_RUNTIME_DIR": "/run/user/1000",
        },
    )
    assert payload["available"] is True
    assert payload["status"] == "drift"
    assert payload["in_sync"] is False
    assert payload["missing_from_activation"] == ["XAUTHORITY"]
    assert payload["mismatched"][0]["variable"] == "DISPLAY"


def test_summarize_session_attachment_flags_activation_drift_even_when_shell_is_graphical():
    payload = summarize_session_attachment(
        shell_env={
            "DISPLAY": ":0",
            "XAUTHORITY": "/tmp/Xauthority",
            "XDG_RUNTIME_DIR": "/run/user/1000",
            "DBUS_SESSION_BUS_ADDRESS": "unix:path=/run/user/1000/bus",
            "I3SOCK": "/run/user/1000/i3/ipc.sock",
        },
        activation_environment={
            "DISPLAY": ":1",
            "XAUTHORITY": "/tmp/Xauthority",
            "XDG_RUNTIME_DIR": "/run/user/1000",
            "DBUS_SESSION_BUS_ADDRESS": "unix:path=/run/user/1000/bus",
            "I3SOCK": "/run/user/1000/i3/ipc.sock",
        },
        x11_probe={"status": "ok", "xtest_available": True, "record_available": True},
        i3_probe={"status": "ok", "wm": "i3", "workspace_count": 4},
    )
    assert payload["status"] == "activation_environment_drift"
    assert payload["ready"] is False
    assert "activation environment drift" in payload["blockers"]
    assert payload["activation_environment"]["status"] == "drift"
    assert payload["commands"]["sync_activation_environment"].startswith("dbus-update-activation-environment --systemd")


def test_summarize_runtime_service_environment_detects_service_session_drift():
    payload = summarize_runtime_service_environment(
        shell_env={
            "DISPLAY": ":0",
            "XAUTHORITY": "/tmp/live.Xauthority",
            "XDG_RUNTIME_DIR": "/run/user/1000",
            "DBUS_SESSION_BUS_ADDRESS": "unix:path=/run/user/1000/bus",
            "I3SOCK": "/run/user/1000/i3/ipc.sock",
        },
        service_environment={
            "DISPLAY": ":1",
            "XAUTHORITY": "/tmp/stale.Xauthority",
            "XDG_RUNTIME_DIR": "/run/user/1000",
            "DBUS_SESSION_BUS_ADDRESS": "unix:path=/run/user/1000/bus",
        },
    )
    assert payload["available"] is True
    assert payload["status"] == "drift"
    assert payload["in_sync"] is False
    assert payload["missing_from_service"] == ["I3SOCK"]
    assert {item["variable"] for item in payload["mismatched"]} == {"DISPLAY", "XAUTHORITY"}


def test_summarize_session_attachment_flags_service_session_drift_when_runtime_env_differs():
    payload = summarize_session_attachment(
        shell_env={
            "DISPLAY": ":0",
            "XAUTHORITY": "/tmp/live.Xauthority",
            "XDG_RUNTIME_DIR": "/run/user/1000",
            "DBUS_SESSION_BUS_ADDRESS": "unix:path=/run/user/1000/bus",
            "I3SOCK": "/run/user/1000/i3/ipc.sock",
        },
        activation_environment={
            "DISPLAY": ":0",
            "XAUTHORITY": "/tmp/live.Xauthority",
            "XDG_RUNTIME_DIR": "/run/user/1000",
            "DBUS_SESSION_BUS_ADDRESS": "unix:path=/run/user/1000/bus",
            "I3SOCK": "/run/user/1000/i3/ipc.sock",
        },
        service_environment={
            "DISPLAY": ":1",
            "XAUTHORITY": "/tmp/stale.Xauthority",
            "XDG_RUNTIME_DIR": "/run/user/1000",
            "DBUS_SESSION_BUS_ADDRESS": "unix:path=/run/user/1000/bus",
            "I3SOCK": "/run/user/1000/i3/ipc.sock",
        },
        x11_probe={"status": "ok", "xtest_available": True, "record_available": True},
        i3_probe={"status": "ok", "wm": "i3", "workspace_count": 4},
    )
    assert payload["status"] == "service_session_drift"
    assert payload["ready"] is False
    assert "service session drift" in payload["blockers"]
    assert payload["runtime_service_environment"]["status"] == "drift"
