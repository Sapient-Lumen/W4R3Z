"""Expectations for recording the actual SearchRequest token."""
from __future__ import annotations

import pynicotine.search as search_mod

from search_again_harness import (
    LOCAL_USER,
    SEARCH_TOKEN,
    make_component,
    make_incoming_core,
    make_outgoing_core,
)


def test_older_self_search_records_requested_search_token(monkeypatch):
    component = make_component()
    server_messages = []
    network_messages = []
    monkeypatch.setattr(search_mod, "core", make_outgoing_core(server_messages, network_messages))

    component.send_search_request(SEARCH_TOKEN)

    assert server_messages[0].token == SEARCH_TOKEN
    assert component._own_tokens == {SEARCH_TOKEN}


def test_matching_local_request_consumes_requested_token(monkeypatch):
    component = make_component()
    server_messages = []
    network_messages = []
    monkeypatch.setattr(search_mod, "core", make_outgoing_core(server_messages, network_messages))
    component.send_search_request(SEARCH_TOKEN)

    monkeypatch.setattr(search_mod, "core", make_incoming_core())
    monkeypatch.setitem(search_mod.config.sections["searches"], "search_results", True)
    monkeypatch.setitem(search_mod.config.sections["searches"], "maxresults", 0)
    component._process_search_request("rareprobe", LOCAL_USER, SEARCH_TOKEN)

    assert component._own_tokens == set()


def test_nonself_user_search_does_not_open_local_response_gate(monkeypatch):
    component = make_component(users=["remote_user"])
    server_messages = []
    network_messages = []
    monkeypatch.setattr(search_mod, "core", make_outgoing_core(server_messages, network_messages))

    component.send_search_request(SEARCH_TOKEN)

    assert server_messages[0].token == SEARCH_TOKEN
    assert component._own_tokens == set()
