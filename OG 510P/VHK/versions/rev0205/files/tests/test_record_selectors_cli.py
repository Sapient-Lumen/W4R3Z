from __future__ import annotations

import json

import yaml
from typer.testing import CliRunner

from vhk.cli import app
from vhk.system.wm_events import WmEvent


runner = CliRunner()


def test_record_selectors_suggests_stable_and_exact(monkeypatch):
    import vhk.cli as cli

    events = [
        WmEvent(wm="i3", kind="focus", name="window", data={"class": "Firefox", "title": "Mozilla Firefox"}),
        WmEvent(wm="i3", kind="focus", name="window", data={"class": "Firefox", "title": "Mozilla Firefox"}),
    ]

    def fake_iter_wm_events(*, kinds, poll_ms):
        for e in events:
            yield e

    monkeypatch.setattr(cli, "iter_wm_events", fake_iter_wm_events)
    monkeypatch.setattr(cli, "window_info_from_event", lambda ev: ev.data)

    result = runner.invoke(app, ["record-selectors", "--max-events", "2"])
    assert result.exit_code == 0, result.output

    payload = json.loads(result.output)
    stable = payload["suggested"]["stable"]
    exact = payload["suggested"]["exact"]

    assert stable["class"] == "Firefox"
    assert "title" not in stable

    assert exact["class"] == "Firefox"
    assert exact["title"] == "Mozilla Firefox"
    assert exact.get("title_regex") is False


def test_record_selectors_title_regex_when_titles_vary(monkeypatch):
    import vhk.cli as cli

    events = [
        WmEvent(wm="i3", kind="focus", name="window", data={"class": "Spotify", "title": "Spotify"}),
        WmEvent(wm="i3", kind="focus", name="window", data={"class": "Spotify", "title": "Spotify Premium"}),
    ]

    def fake_iter_wm_events(*, kinds, poll_ms):
        for e in events:
            yield e

    monkeypatch.setattr(cli, "iter_wm_events", fake_iter_wm_events)
    monkeypatch.setattr(cli, "window_info_from_event", lambda ev: ev.data)

    result = runner.invoke(app, ["record-selectors", "--max-events", "2"])
    assert result.exit_code == 0, result.output

    payload = json.loads(result.output)
    exact = payload["suggested"]["exact"]
    assert exact["class"] == "Spotify"
    assert exact["title_regex"] is True
    assert exact["title"].startswith("^(?:")


def test_record_selectors_no_json_prints_yaml_snippet(monkeypatch):
    import vhk.cli as cli

    events = [WmEvent(wm="i3", kind="focus", name="window", data={"class": "Firefox", "title": "Mozilla Firefox"})]

    def fake_iter_wm_events(*, kinds, poll_ms):
        for e in events:
            yield e

    monkeypatch.setattr(cli, "iter_wm_events", fake_iter_wm_events)
    monkeypatch.setattr(cli, "window_info_from_event", lambda ev: ev.data)

    result = runner.invoke(app, ["record-selectors", "--max-events", "1", "--no-json"])
    assert result.exit_code == 0, result.output
    snippet = yaml.safe_load(result.output)
    assert snippet["class"] == "Firefox"
    assert "title" not in snippet
