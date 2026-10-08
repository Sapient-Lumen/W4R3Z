from __future__ import annotations

import json

from typer.testing import CliRunner

from vhk.cli import app


runner = CliRunner()


def test_doctor_json_exposes_session_and_hotkey_helpers(monkeypatch):
    monkeypatch.setenv("XDG_SESSION_TYPE", "wayland")
    monkeypatch.setenv("WAYLAND_DISPLAY", "wayland-1")

    result = runner.invoke(app, ["doctor", "--json"])
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)

    assert "XDG_SESSION_TYPE" in payload["env"]
    assert "WAYLAND_DISPLAY" in payload["env"]
    assert "intercept" in payload["helpers"]
    assert "uinput" in payload["helpers"]
    assert "evtest" in payload["helpers"]
    assert "xinput" in payload["helpers"]
    assert "wmctrl" in payload["helpers"]
    assert "rofi" in payload["helpers"]
    assert "wofi" in payload["helpers"]
    assert "fuzzel" in payload["helpers"]
    assert "tofi" in payload["helpers"]
    assert "chooser" in payload["modules"]


def _mkexe(tmp_path, name: str):
    p = tmp_path / name
    p.write_text("#!/bin/sh\nexit 0\n")
    p.chmod(0o755)
    return p


def test_doctor_json_includes_clear_stuck_keys_hint_on_x11(tmp_path, monkeypatch):
    _mkexe(tmp_path, "x11vnc")
    monkeypatch.setenv("PATH", str(tmp_path))
    monkeypatch.setenv("DISPLAY", ":0")
    monkeypatch.setenv("XAUTHORITY", "/tmp/Xauthority")
    monkeypatch.setenv("XDG_SESSION_TYPE", "x11")
    monkeypatch.delenv("WAYLAND_DISPLAY", raising=False)

    result = runner.invoke(app, ["doctor", "--json"])
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)

    hint = payload["recovery"]["clear_stuck_keys"]
    assert hint["backend"] == "x11"
    assert hint["available"] is True
    assert "x11vnc -deny_all -clear_keys -timeout 1" in hint["command"]
    assert "DISPLAY=:0" in hint["command"]
    assert "XAUTHORITY=/tmp/Xauthority" in hint["command"]


def test_doctor_json_reports_no_at_bridge_disabling_a11y(monkeypatch):
    monkeypatch.setenv("NO_AT_BRIDGE", "1")

    result = runner.invoke(app, ["doctor", "--json"])
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)

    assert payload["env"]["NO_AT_BRIDGE"] == "1"
    assert payload["a11y"]["disabled_by_env"] is True
    assert payload["a11y"]["status"] == "disabled_by_env"
    assert any(item["topic"] == "accessibility" for item in payload["advice"])


def test_doctor_json_probes_accessibility_bus_via_busctl(tmp_path, monkeypatch):
    _mkexe(tmp_path, "busctl")
    monkeypatch.setenv("PATH", str(tmp_path))

    import vhk.system.doctor as doctor_mod

    def fake_run(cmd, capture_output=True, text=True, timeout=3):
        class R:
            def __init__(self, returncode=0, stdout="", stderr=""):
                self.returncode = returncode
                self.stdout = stdout
                self.stderr = stderr

        if cmd[:2] == [str(tmp_path / "busctl"), "--user"]:
            return R(stdout='s "unix:path=/run/user/1000/at-spi/bus"\n')
        if cmd[:2] == [str(tmp_path / "busctl"), "--address=unix:path=/run/user/1000/at-spi/bus"]:
            return R(stdout="NAME PID PROCESS USER CONNECTION UNIT SESSION DESCRIPTION\norg.a11y.atspi.Registry - - - - - - -\n")
        return R(stdout="")

    monkeypatch.setattr(doctor_mod.subprocess, "run", fake_run)

    result = runner.invoke(app, ["doctor", "--json"])
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)

    assert payload["a11y"]["probe_tool"] == "busctl"
    assert payload["a11y"]["status"] == "ok"
    assert payload["a11y"]["address"] == "unix:path=/run/user/1000/at-spi/bus"
    assert payload["a11y"]["registry_available"] is True


def test_doctor_json_probes_x11_extensions_and_xkb_layout(tmp_path, monkeypatch):
    _mkexe(tmp_path, "xdpyinfo")
    _mkexe(tmp_path, "setxkbmap")
    monkeypatch.setenv("PATH", str(tmp_path))
    monkeypatch.setenv("DISPLAY", ":0")
    monkeypatch.setenv("XDG_SESSION_TYPE", "x11")
    monkeypatch.delenv("WAYLAND_DISPLAY", raising=False)

    import vhk.system.doctor as doctor_mod

    def fake_run(cmd, capture_output=True, text=True, timeout=3):
        class R:
            def __init__(self, returncode=0, stdout="", stderr=""):
                self.returncode = returncode
                self.stdout = stdout
                self.stderr = stderr

        exe = cmd[0]
        if exe == str(tmp_path / "xdpyinfo"):
            return R(stdout="""name of display:    :0
number of extensions:    3
    XTEST  (opcode: 132)
    MIT-SHM  (opcode: 130)
    XInputExtension  (opcode: 131)
screen #0:
""")
        if exe == str(tmp_path / "setxkbmap"):
            return R(stdout="""rules:      evdev
model:      pc105
layout:     us,de
variant:    ,nodeadkeys
options:    grp:alt_shift_toggle
""")
        return R(stdout="")

    monkeypatch.setattr(doctor_mod.subprocess, "run", fake_run)

    result = runner.invoke(app, ["doctor", "--json"])
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)

    assert payload["x11"]["status"] == "ok"
    assert payload["x11"]["xtest_available"] is True
    assert payload["x11"]["record_available"] is False
    assert payload["x11"]["xinput_available"] is True
    assert payload["xkb"]["status"] == "ok"
    assert payload["xkb"]["layout"] == "us,de"
    assert payload["xkb"]["options"] == "grp:alt_shift_toggle"
    assert any(item["topic"] == "x11-recorder" for item in payload["advice"])


def test_doctor_json_probes_i3_ipc(monkeypatch):
    import vhk.system.doctor as doctor_mod

    class FakeConn:
        def __init__(self, socket_path=None, timeout=2.0):
            self.socket_path = socket_path
            self.timeout = timeout

        def get_workspaces(self):
            return [{"name": "1"}, {"name": "2"}]

    monkeypatch.setattr(doctor_mod, "discover_socket_path", lambda: "/run/user/1000/i3/ipc-socket.1234")
    monkeypatch.setattr(doctor_mod, "I3Connection", FakeConn)

    result = runner.invoke(app, ["doctor", "--json"])
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)

    assert payload["i3"]["status"] == "ok"
    assert payload["i3"]["wm"] == "i3"
    assert payload["i3"]["workspace_count"] == 2


def test_doctor_json_runs_screenshot_self_test(monkeypatch, tmp_path):
    import vhk.cli as cli_mod
    import vhk.system.screenshot as screenshot_mod

    backend = screenshot_mod.ScreenshotBackend(name="scrot", exe=str(tmp_path / "scrot"))
    monkeypatch.setenv("DISPLAY", ":0")
    monkeypatch.setenv("XDG_SESSION_TYPE", "x11")
    monkeypatch.delenv("WAYLAND_DISPLAY", raising=False)
    monkeypatch.setattr(cli_mod, "screenshot_backend", lambda: backend)
    monkeypatch.setattr(screenshot_mod, "choose_backend", lambda: backend)

    def fake_capture(path, region=None):
        path.write_bytes(b"PNG")
        return path

    monkeypatch.setattr(screenshot_mod, "capture", fake_capture)

    result = runner.invoke(app, ["doctor", "--json"])
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)

    assert payload["screenshot_probe"]["status"] == "ok"
    assert payload["screenshot_probe"]["bytes"] == 3



def test_doctor_json_probes_tesseract_languages_with_warnings(tmp_path, monkeypatch):
    tesseract = tmp_path / "tesseract"
    tesseract.write_text("#!/bin/sh\nif [ \"$1\" = \"--version\" ]; then echo 'tesseract 5.4.0'; exit 0; fi\nexit 0\n")
    tesseract.chmod(0o755)
    monkeypatch.setenv("PATH", str(tmp_path))

    import vhk.system.doctor as doctor_mod

    def fake_run(cmd, capture_output=True, text=True, timeout=3):
        class R:
            def __init__(self, returncode=0, stdout="", stderr=""):
                self.returncode = returncode
                self.stdout = stdout
                self.stderr = stderr

        if cmd == [str(tesseract), "--list-langs"]:
            return R(
                returncode=1,
                stdout="List of available languages (2):\neng\nosd\n",
                stderr="Error opening data file /tmp/eng.traineddata\n",
            )
        return R(stdout="")

    monkeypatch.setattr(doctor_mod.subprocess, "run", fake_run)

    result = runner.invoke(app, ["doctor", "--json"])
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)

    assert payload["tesseract"]["status"] == "ok_with_warnings"
    assert payload["tesseract"]["languages"] == ["eng", "osd"]
    assert payload["tesseract"]["has_eng"] is True
    assert payload["tesseract"]["warning"] == "Error opening data file /tmp/eng.traineddata"



def test_doctor_json_probes_xrandr_display_geometry(tmp_path, monkeypatch):
    _mkexe(tmp_path, "xrandr")
    monkeypatch.setenv("PATH", str(tmp_path))
    monkeypatch.setenv("DISPLAY", ":0")
    monkeypatch.setenv("XDG_SESSION_TYPE", "x11")
    monkeypatch.delenv("WAYLAND_DISPLAY", raising=False)

    import vhk.system.doctor as doctor_mod

    def fake_run(cmd, capture_output=True, text=True, timeout=3):
        class R:
            def __init__(self, returncode=0, stdout="", stderr=""):
                self.returncode = returncode
                self.stdout = stdout
                self.stderr = stderr

        exe = cmd[0]
        if exe == str(tmp_path / "xrandr") and cmd[1:] == ["--query"]:
            return R(stdout="""Screen 0: minimum 320 x 200, current 5760 x 1440, maximum 16384 x 16384
DP-1 connected primary 2560x1440+0+0 (normal left inverted right x axis y axis) 597mm x 336mm
HDMI-1 connected 3200x1800+2560+0 (normal left inverted right x axis y axis) 294mm x 165mm
""")
        if exe == str(tmp_path / "xrandr") and cmd[1:] == ["--listmonitors"]:
            return R(stdout="""Monitors: 2
 0: +*DP-1 2560/597x1440/336+0+0  DP-1
 1: +HDMI-1 3200/294x1800/165+2560+0  HDMI-1
""")
        return R(stdout="")

    monkeypatch.setattr(doctor_mod.subprocess, "run", fake_run)

    result = runner.invoke(app, ["doctor", "--json"])
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)

    assert payload["displays"]["status"] == "ok"
    assert payload["displays"]["screen"]["current_width"] == 5760
    assert payload["displays"]["monitor_count"] == 2
    assert payload["displays"]["mixed_dpi"] is True
    assert payload["displays"]["monitors"][0]["name"] == "DP-1"
    assert payload["displays"]["monitors"][1]["estimated_scale_vs_96dpi"] > 1.7
    assert any(item["topic"] == "display-geometry" for item in payload["advice"])


def test_doctor_includes_uinput_probe_and_advice_when_needed(tmp_path, monkeypatch):
    # Make ydotool appear installed so doctor considers uinput relevant.
    def _mkexe(name: str):
        p = tmp_path / name
        p.write_text("#!/bin/sh\nexit 0\n")
        p.chmod(0o755)
        return p

    _mkexe("ydotool")
    monkeypatch.setenv("PATH", str(tmp_path))

    import vhk.cli as cli_mod

    monkeypatch.setattr(
        cli_mod,
        "probe_uinput",
        lambda: {
            "path": "/dev/uinput",
            "exists": True,
            "status": "permission_denied",
            "mode": "0o600",
            "gid": 0,
            "group": "root",
            "can_write": False,
        },
    )

    result = runner.invoke(app, ["doctor", "--json"])
    assert result.exit_code == 0, result.stdout

    payload = json.loads(result.stdout)
    assert payload["uinput"]["status"] == "permission_denied"
    assert any(item["topic"] == "uinput" for item in payload["advice"])


def test_doctor_json_reports_portal_capability_matrix_and_config(tmp_path, monkeypatch):
    busctl = _mkexe(tmp_path, "busctl")
    monkeypatch.setenv("PATH", str(tmp_path))
    monkeypatch.setenv("XDG_SESSION_TYPE", "wayland")
    monkeypatch.setenv("WAYLAND_DISPLAY", "wayland-1")
    monkeypatch.setenv("XDG_CURRENT_DESKTOP", "KDE")
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "cfg"))

    cfg_dir = tmp_path / "cfg" / "xdg-desktop-portal"
    cfg_dir.mkdir(parents=True)
    (cfg_dir / "kde-portals.conf").write_text(
        """[preferred]
default=gtk
org.freedesktop.impl.portal.ScreenCast=gnome
org.freedesktop.impl.portal.RemoteDesktop=gnome
org.freedesktop.impl.portal.GlobalShortcuts=kde
org.freedesktop.impl.portal.InputCapture=gnome
"""
    )

    import vhk.system.doctor as doctor_mod

    def fake_run(cmd, capture_output=True, text=True, timeout=3):
        class R:
            def __init__(self, returncode=0, stdout="", stderr=""):
                self.returncode = returncode
                self.stdout = stdout
                self.stderr = stderr

        if cmd[0] == str(busctl) and cmd[1:3] == ["--user", "get-property"]:
            interface = cmd[5]
            prop = cmd[6]
            mapping = {
                ("org.freedesktop.portal.Screenshot", "version"): "u 2\n",
                ("org.freedesktop.portal.ScreenCast", "version"): "u 5\n",
                ("org.freedesktop.portal.ScreenCast", "AvailableSourceTypes"): "u 3\n",
                ("org.freedesktop.portal.ScreenCast", "AvailableCursorModes"): "u 6\n",
                ("org.freedesktop.portal.GlobalShortcuts", "version"): "u 1\n",
                ("org.freedesktop.portal.RemoteDesktop", "version"): "u 2\n",
                ("org.freedesktop.portal.RemoteDesktop", "AvailableDeviceTypes"): "u 3\n",
                ("org.freedesktop.portal.InputCapture", "version"): "u 2\n",
                ("org.freedesktop.portal.InputCapture", "SupportedCapabilities"): "u 3\n",
            }
            out = mapping.get((interface, prop))
            if out is None:
                return R(returncode=1, stderr="No such interface")
            return R(stdout=out)
        return R(stdout="")

    monkeypatch.setattr(doctor_mod.subprocess, "run", fake_run)

    result = runner.invoke(app, ["doctor", "--json"])
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)

    assert payload["xdg_portal_screencast"]["status"] == "ok"
    assert payload["xdg_portal_screencast"]["available_source_type_names"] == ["monitor", "window"]
    assert payload["xdg_portal_remote_desktop"]["available_device_type_names"] == ["keyboard", "pointer"]
    assert payload["xdg_portal_input_capture"]["supported_capability_names"] == ["keyboard", "pointer"]
    assert payload["xdg_portal_backend_config"]["status"] == "ok"
    assert payload["xdg_portal_backend_config"]["config_path"].endswith("kde-portals.conf")

    caps = payload["capability_matrix"]
    assert caps["screen_capture"]["status"] == "ok"
    assert "portal:Screenshot" in caps["screen_capture"]["mechanisms"]
    assert caps["screen_capture"]["portal_backends"] == ["gtk"]
    assert caps["text_injection"]["status"] == "limited"
    assert "portal:RemoteDesktop(keyboard)" in caps["text_injection"]["mechanisms"]
    assert caps["global_hotkeys"]["portal_backends"] == ["kde"]
    assert caps["input_capture"]["status"] == "ok"
    assert caps["input_capture"]["portal_backends"] == ["gnome"]


def test_doctor_json_discovers_portal_backend_manifests_and_uses_them_for_fallbacks(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_SESSION_TYPE", "wayland")
    monkeypatch.setenv("WAYLAND_DISPLAY", "wayland-1")
    monkeypatch.setenv("XDG_CURRENT_DESKTOP", "sway")
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "data"))

    portals_dir = tmp_path / "data" / "xdg-desktop-portal" / "portals"
    portals_dir.mkdir(parents=True)
    (portals_dir / "gtk.portal").write_text(
        """[portal]
DBusName=org.freedesktop.impl.portal.desktop.gtk
Interfaces=org.freedesktop.impl.portal.Screenshot;org.freedesktop.impl.portal.FileChooser
UseIn=gnome;kde
"""
    )
    (portals_dir / "wlr.portal").write_text(
        """[portal]
DBusName=org.freedesktop.impl.portal.desktop.wlr
Interfaces=org.freedesktop.impl.portal.Screenshot;org.freedesktop.impl.portal.ScreenCast
UseIn=wlroots;sway;wayfire;river;phosh
"""
    )
    (portals_dir / "luminous.portal").write_text(
        """[portal]
DBusName=org.freedesktop.impl.portal.desktop.luminous
Interfaces=org.freedesktop.impl.portal.Screenshot;org.freedesktop.impl.portal.ScreenCast
UseIn=sway;wayfire;river;wlroots
"""
    )

    result = runner.invoke(app, ["doctor", "--json"])
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)

    catalog = payload["xdg_portal_backend_manifests"]
    assert catalog["status"] == "ok"
    backends = {item["backend"]: item for item in catalog["backends"]}
    assert {"gtk", "wlr", "luminous"}.issubset(backends)
    assert backends["wlr"]["usable_on_current_desktop"] is True
    assert backends["luminous"]["usable_on_current_desktop"] is True
    assert backends["gtk"]["usable_on_current_desktop"] is False

    screenshot_entries = catalog["interfaces"]["org.freedesktop.impl.portal.Screenshot"]
    by_backend = {item["backend"]: item for item in screenshot_entries}
    assert by_backend["luminous"]["usable_on_current_desktop"] is True
    assert by_backend["gtk"]["usable_on_current_desktop"] is False

    caps = payload["capability_matrix"]
    assert "luminous" in caps["screen_capture"]["portal_backends"]
    assert "wlr" in caps["screen_capture"]["portal_backends"]



def test_doctor_portal_advice_mentions_manifest_mismatch_and_missing_configured_backend(tmp_path, monkeypatch):
    busctl = _mkexe(tmp_path, "busctl")
    monkeypatch.setenv("PATH", str(tmp_path))
    monkeypatch.setenv("XDG_SESSION_TYPE", "wayland")
    monkeypatch.setenv("WAYLAND_DISPLAY", "wayland-1")
    monkeypatch.setenv("XDG_CURRENT_DESKTOP", "Hyprland")
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "cfg"))
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "data"))

    cfg_dir = tmp_path / "cfg" / "xdg-desktop-portal"
    cfg_dir.mkdir(parents=True)
    (cfg_dir / "hyprland-portals.conf").write_text(
        """[preferred]
default=gtk
org.freedesktop.impl.portal.RemoteDesktop=ghost;kde
"""
    )

    portals_dir = tmp_path / "data" / "xdg-desktop-portal" / "portals"
    portals_dir.mkdir(parents=True)
    (portals_dir / "kde.portal").write_text(
        """[portal]
DBusName=org.freedesktop.impl.portal.desktop.kde
Interfaces=org.freedesktop.impl.portal.RemoteDesktop;org.freedesktop.impl.portal.GlobalShortcuts
UseIn=kde
"""
    )
    (portals_dir / "gtk.portal").write_text(
        """[portal]
DBusName=org.freedesktop.impl.portal.desktop.gtk
Interfaces=org.freedesktop.impl.portal.Screenshot
UseIn=gnome
"""
    )

    import vhk.system.doctor as doctor_mod

    def fake_run(cmd, capture_output=True, text=True, timeout=3):
        class R:
            def __init__(self, returncode=0, stdout="", stderr=""):
                self.returncode = returncode
                self.stdout = stdout
                self.stderr = stderr

        if cmd[0] == str(busctl) and cmd[1:3] == ["--user", "get-property"]:
            return R(returncode=1, stderr="No such interface")
        return R(stdout="")

    monkeypatch.setattr(doctor_mod.subprocess, "run", fake_run)

    result = runner.invoke(app, ["doctor", "--json"])
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)

    portal_advice = [item["summary"] for item in payload["advice"] if item["topic"] == "portals"]
    assert any("UseIn rules do not match the current desktop" in summary and "kde" in summary for summary in portal_advice)
    assert any("not discovered in the installed .portal manifests" in summary and "ghost" in summary for summary in portal_advice)



def test_doctor_json_flags_dotoolc_without_daemon(tmp_path, monkeypatch):
    _mkexe(tmp_path, "dotoolc")
    monkeypatch.setenv("PATH", str(tmp_path))
    monkeypatch.setenv("XDG_SESSION_TYPE", "wayland")
    monkeypatch.setenv("WAYLAND_DISPLAY", "wayland-1")

    import vhk.cli as cli_mod

    monkeypatch.setattr(cli_mod, "probe_uinput", lambda: {"status": "ok", "can_write": True})
    monkeypatch.setattr(cli_mod, "probe_wayland_protocols", lambda: {"status": "ok", "virtual_keyboard": False})

    result = runner.invoke(app, ["doctor", "--json"])
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)

    assert payload["dotoold"]["status"] == "daemon_required"
    assert payload["capability_matrix"]["text_injection"]["recommended"] is None
    assert any("dotoold daemon is not ready" in note for note in payload["capability_matrix"]["text_injection"]["notes"])
    assert any(item["topic"] == "dotool" for item in payload["advice"])



def test_doctor_json_prefers_dotoolc_when_daemon_is_active(tmp_path, monkeypatch):
    _mkexe(tmp_path, "dotool")
    _mkexe(tmp_path, "dotoolc")
    _mkexe(tmp_path, "dotoold")
    _mkexe(tmp_path, "systemctl")
    monkeypatch.setenv("PATH", str(tmp_path))
    monkeypatch.setenv("XDG_SESSION_TYPE", "wayland")
    monkeypatch.setenv("WAYLAND_DISPLAY", "wayland-1")

    import vhk.cli as cli_mod
    import vhk.system.doctor as doctor_mod

    monkeypatch.setattr(cli_mod, "probe_uinput", lambda: {"status": "ok", "can_write": True})
    monkeypatch.setattr(cli_mod, "probe_wayland_protocols", lambda: {"status": "ok", "virtual_keyboard": False})

    def fake_run(cmd, capture_output=True, text=True, timeout=3):
        class R:
            def __init__(self, returncode=0, stdout="", stderr=""):
                self.returncode = returncode
                self.stdout = stdout
                self.stderr = stderr

        exe = cmd[0]
        if exe == str(tmp_path / "systemctl") and "show" in cmd and "dotoold.service" in cmd:
            return R(stdout="""Id=dotoold.service
LoadState=loaded
ActiveState=active
SubState=running
UnitFileState=enabled
""")
        return R(stdout="")

    monkeypatch.setattr(doctor_mod.subprocess, "run", fake_run)

    result = runner.invoke(app, ["doctor", "--json"])
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)

    assert payload["dotoold"]["status"] == "ok"
    assert payload["dotoold"]["daemon_ready"] is True
    assert payload["capability_matrix"]["text_injection"]["recommended"] == "dotoolc"
    assert "dotoolc" in payload["capability_matrix"]["text_injection"]["mechanisms"]
    assert payload["capability_matrix"]["pointer_injection"]["recommended"] == "dotoolc"
