from __future__ import annotations

import os
from pathlib import Path

import pytest

from pynicotine.config import config
from pynicotine.core import core
from pynicotine.events import events
from pynicotine.slskmessages import AddAllowedResponse
from pynicotine.slskmessages import FileSearch
from pynicotine.slskmessages import RemoveAllowedResponse
from pynicotine.slskmessages import UserSearch


@pytest.fixture
def started_core(tmp_path: Path):
    config.set_data_folder(str(tmp_path / "data"))
    config.set_config_file(str(tmp_path / "data" / "config"))
    os.makedirs(config.data_folder_path, exist_ok=True)
    core.init_components(enabled_components={"pluginhandler", "search", "shares", "users"})
    core.start()
    try:
        yield
    finally:
        core.quit()


def test_rekey_orders_old_removal_before_new_admission_and_request(started_core):
    network_messages = []
    rekeys = []

    def on_message(message):
        network_messages.append(message)

    def on_rekey(old_token, new_token):
        rekeys.append((old_token, new_token))

    events.connect("queue-network-message", on_message)
    events.connect("rekey-search", on_rekey)
    try:
        core.search.do_search("alpha beta", "global")
        old_token = core.search.token
        search = core.search.searches[old_token]
        network_messages.clear()
        new_token = core.search.repeat_search(old_token)
    finally:
        events.disconnect("queue-network-message", on_message)
        events.disconnect("rekey-search", on_rekey)

    assert core.search.searches[new_token] is search
    assert rekeys == [(old_token, new_token)]
    assert [type(message) for message in network_messages] == [
        RemoveAllowedResponse,
        AddAllowedResponse,
        FileSearch,
    ]
    assert network_messages[0].response_id == old_token
    assert network_messages[1].response_id == new_token
    assert network_messages[2].token == new_token


def test_rekey_preserves_explicit_user_audience(started_core):
    network_messages = []

    def on_message(message):
        network_messages.append(message)

    events.connect("queue-network-message", on_message)
    try:
        core.search.do_search("alpha", "user", users=["alice", "bob"])
        old_token = core.search.token
        network_messages.clear()
        new_token = core.search.repeat_search(old_token)
    finally:
        events.disconnect("queue-network-message", on_message)

    requests = [message for message in network_messages if isinstance(message, UserSearch)]
    assert [(message.search_username, message.token) for message in requests] == [
        ("alice", new_token),
        ("bob", new_token),
    ]
