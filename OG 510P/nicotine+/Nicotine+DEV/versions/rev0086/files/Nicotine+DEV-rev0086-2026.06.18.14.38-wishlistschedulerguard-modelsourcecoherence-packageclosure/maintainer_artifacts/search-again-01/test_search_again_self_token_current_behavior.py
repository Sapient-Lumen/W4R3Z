"""Witnesses for the current older-self-search token divergence."""
from __future__ import annotations

import pynicotine.search as search_mod

from search_again_harness import (
    LATEST_TOKEN,
    LOCAL_USER,
    SEARCH_TOKEN,
    make_component,
    make_incoming_core,
    make_outgoing_core,
)


def test_current_resend_records_latest_token_but_sends_search_token(monkeypatch):
    component = make_component()
    server_messages = []
    network_messages = []
    monkeypatch.setattr(search_mod, "core", make_outgoing_core(server_messages, network_messages))

    component.send_search_request(SEARCH_TOKEN)

    assert server_messages[0].token == SEARCH_TOKEN
    assert component._own_tokens == {LATEST_TOKEN}


def test_current_divergence_suppresses_local_request(monkeypatch):
    component = make_component()
    server_messages = []
    network_messages = []
    monkeypatch.setattr(search_mod, "core", make_outgoing_core(server_messages, network_messages))
    component.send_search_request(SEARCH_TOKEN)

    monkeypatch.setattr(search_mod, "core", make_incoming_core())
    monkeypatch.setitem(search_mod.config.sections["searches"], "search_results", True)
    monkeypatch.setitem(search_mod.config.sections["searches"], "maxresults", 0)
    component._process_search_request("rareprobe", LOCAL_USER, SEARCH_TOKEN)

    assert component._own_tokens == {LATEST_TOKEN}


def test_initial_self_search_still_uses_matching_token(monkeypatch):
    component = make_component(latest_token=SEARCH_TOKEN)
    server_messages = []
    network_messages = []
    monkeypatch.setattr(search_mod, "core", make_outgoing_core(server_messages, network_messages))

    component.send_search_request(SEARCH_TOKEN)

    assert server_messages[0].token == SEARCH_TOKEN
    assert component._own_tokens == {SEARCH_TOKEN}
