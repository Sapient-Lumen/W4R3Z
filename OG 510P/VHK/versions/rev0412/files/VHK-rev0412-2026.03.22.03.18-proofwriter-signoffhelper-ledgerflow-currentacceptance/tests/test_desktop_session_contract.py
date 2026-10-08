from __future__ import annotations

from vhk.project.desktop_session_contract import summarize_desktop_session_contract, compare_desktop_session_contract


def test_desktop_session_contract_reports_in_sync():
    observed = summarize_desktop_session_contract({
        "DISPLAY": ":1",
        "XAUTHORITY": "/tmp/xauth",
        "I3SOCK": "/tmp/i3.sock",
        "XDG_SESSION_TYPE": "x11",
        "XDG_CURRENT_DESKTOP": "i3",
    })
    current = summarize_desktop_session_contract({
        "DISPLAY": ":1",
        "XAUTHORITY": "/tmp/xauth",
        "I3SOCK": "/tmp/i3.sock",
        "XDG_SESSION_TYPE": "x11",
        "XDG_CURRENT_DESKTOP": "i3",
    })
    comparison = compare_desktop_session_contract(current, observed)
    assert comparison["in_sync"] is True
    assert comparison["status"] == "in_sync"


def test_desktop_session_contract_reports_x11_i3_drift():
    observed = summarize_desktop_session_contract({
        "DISPLAY": ":0",
        "XAUTHORITY": "/tmp/xauth0",
        "I3SOCK": "/tmp/i3-0.sock",
        "XDG_SESSION_TYPE": "x11",
        "XDG_CURRENT_DESKTOP": "i3",
    })
    current = summarize_desktop_session_contract({
        "DISPLAY": ":1",
        "XAUTHORITY": "/tmp/xauth1",
        "I3SOCK": "/tmp/i3-1.sock",
        "XDG_SESSION_TYPE": "x11",
        "XDG_CURRENT_DESKTOP": "i3",
    })
    comparison = compare_desktop_session_contract(current, observed)
    assert comparison["in_sync"] is False
    assert comparison["status"] == "drifted"
    assert comparison["display_changed"] is True
    assert comparison["xauthority_changed"] is True
    assert comparison["i3sock_changed"] is True
    assert "DISPLAY changed since latest healthy replay" in comparison["reasons"]
