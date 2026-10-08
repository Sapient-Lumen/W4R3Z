"""Small shared fixtures for buddy recipient/admission research."""
from types import SimpleNamespace

import pynicotine.search as search_mod
from pynicotine.search import Search


class DummyPluginHandler:
    def outgoing_buddy_search_event(self, _term):
        return None


def make_component(token=530000):
    component = object.__new__(Search)
    component.searches = {}
    component.token = token
    return component


def install_environment(monkeypatch, users):
    sent = []
    core = SimpleNamespace(
        buddies=SimpleNamespace(users=list(users)),
        users=SimpleNamespace(login_username="local_user"),
        pluginhandler=DummyPluginHandler(),
        send_message_to_server=sent.append,
    )
    monkeypatch.setattr(search_mod, "core", core)
    monkeypatch.setattr(search_mod, "events", SimpleNamespace(emit=lambda *_args: None))
    search_mod.config.sections.setdefault("searches", {})
    monkeypatch.setitem(search_mod.config.sections["searches"], "enable_history", False)
    monkeypatch.setitem(search_mod.config.sections["searches"], "history", [])
    return core, sent


def recipient_names(messages):
    return [message.search_username for message in messages]
