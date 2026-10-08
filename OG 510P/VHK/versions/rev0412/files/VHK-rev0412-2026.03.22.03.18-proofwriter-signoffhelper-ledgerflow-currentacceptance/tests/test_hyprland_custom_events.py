from __future__ import annotations


def test_iter_wm_events_hyprland_custom(monkeypatch):
    import vhk.system.wm_events as wm

    # Force hyprland path.
    monkeypatch.setattr(wm, "detect_compositor", lambda: "hyprland")
    monkeypatch.setattr(wm, "_hypr_socket2_path", lambda: "/tmp/fake.sock")

    def fake_lines(path):
        assert path == "/tmp/fake.sock"
        yield "custom>>vhk:test"

    monkeypatch.setattr(wm, "_iter_hypr_socket2_lines", fake_lines)

    it = wm.iter_wm_events(kinds={"custom"})
    ev = next(it)
    assert ev.wm == "hyprland"
    assert ev.kind == "custom"
    assert ev.name == "custom"
    assert ev.data == "vhk:test"
    it.close()
