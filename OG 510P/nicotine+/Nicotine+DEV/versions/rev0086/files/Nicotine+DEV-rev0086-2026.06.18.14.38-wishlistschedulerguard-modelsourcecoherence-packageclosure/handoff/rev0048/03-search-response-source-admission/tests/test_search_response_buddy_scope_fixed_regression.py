"""
Fixed-behavior regression for SEARCH-RESP-01B buddy-scoped search response admission.
"""
from __future__ import annotations

from types import SimpleNamespace

import pynicotine.search as search_mod
import pynicotine.slskmessages as slskmessages
from pynicotine.search import Search, SearchRequest


class DummyNetworkFilter:
    def is_user_ignored(self, username):
        return False

    def is_user_ip_ignored(self, username, ip_address):
        return False

    def get_country_code(self, ip_address):
        return None


class DummyPluginHandler:
    def outgoing_buddy_search_event(self, search_term):
        return None

    def outgoing_global_search_event(self, search_term):
        return None

    def outgoing_room_search_event(self, room, search_term):
        return None

    def outgoing_user_search_event(self, users, search_term):
        return None

    def outgoing_wishlist_search_event(self, search_term):
        return None


def _install_dummy_network_filter():
    search_mod.core.network_filter = DummyNetworkFilter()


def _allow_token_for_legacy_handler(token):
    allowed = getattr(slskmessages, "SEARCH_TOKENS_ALLOWED", None)
    if allowed is not None:
        allowed.clear()
        allowed.add(token)


def _make_search_request(token, mode, room=None, users=None, is_ignored=False):
    kwargs = dict(
        token=token,
        term="rareprobe",
        term_sanitized="rareprobe",
        term_transmitted="rareprobe",
        included_words=["rareprobe"],
        excluded_words=[],
        mode=mode,
        room=room,
        users=users,
    )
    try:
        return SearchRequest(**kwargs, is_ignored=is_ignored)
    except TypeError:
        return SearchRequest(**kwargs)


def _msg(token, username):
    return SimpleNamespace(
        token=token,
        username=username,
        addr=("203.0.113.91", 4999),
        list=[(1, "rareprobe\\spoof.flac", 1234, None, [])],
        privatelist=[],
        freeulslots=True,
        ulspeed=0,
        inqueue=0,
    )


def _dispatch(search, msg):
    _install_dummy_network_filter()
    _allow_token_for_legacy_handler(search.token)
    fake_search_component = SimpleNamespace(searches={search.token: search})
    Search._file_search_response(fake_search_component, msg)
    return msg


def _make_component(token=520000):
    component = object.__new__(Search)
    for name, value in {
        "searches": {},
        "excluded_phrases": [],
        "token": token,
        "wishlist_interval": 0,
        "_own_tokens": set(),
        "_wishlist_timer_id": None,
        "wishlist": {},
        "wishlist_file_path": "",
        "_allow_saving_wishlist": False,
    }.items():
        try:
            setattr(component, name, value)
        except AttributeError:
            pass
    return component


def _install_do_search_environment(monkeypatch, buddy_users):
    sent_messages = []
    network_messages = []
    emitted_events = []

    def send_message_to_server(msg):
        sent_messages.append(msg)

    def send_message_to_network_thread(msg):
        network_messages.append(msg)

    dummy_core = SimpleNamespace(
        buddies=SimpleNamespace(users=list(buddy_users)),
        users=SimpleNamespace(login_username="local_user"),
        pluginhandler=DummyPluginHandler(),
        send_message_to_server=send_message_to_server,
        send_message_to_network_thread=send_message_to_network_thread,
    )
    monkeypatch.setattr(search_mod, "core", dummy_core)

    monkeypatch.setattr(search_mod, "events", SimpleNamespace(emit=lambda *args, **kwargs: emitted_events.append((args, kwargs))))

    search_mod.config.sections.setdefault("searches", {})
    monkeypatch.setitem(search_mod.config.sections["searches"], "enable_history", False)
    monkeypatch.setitem(search_mod.config.sections["searches"], "history", [])

    return sent_messages, network_messages, emitted_events


def test_buddy_scoped_response_from_unrequested_peer_is_rejected():
    token = 520001
    search = _make_search_request(token, mode="buddies", users=["buddy_a", "buddy_b"])
    msg = _msg(token, username="not_a_buddy")
    _dispatch(search, msg)
    assert msg.token is None


def test_buddy_scoped_response_from_requested_buddy_is_preserved():
    token = 520002
    search = _make_search_request(token, mode="buddies", users=["buddy_a", "buddy_b"])
    msg = _msg(token, username="buddy_b")
    _dispatch(search, msg)
    assert msg.token == token


def test_buddy_scoped_response_without_source_snapshot_is_rejected_closed():
    token = 520003
    search = _make_search_request(token, mode="buddies", users=[])
    msg = _msg(token, username="buddy_a")
    _dispatch(search, msg)
    assert msg.token is None


def test_buddy_search_captures_source_snapshot_and_sends_to_same_users(monkeypatch):
    component = _make_component(token=520100)
    sent_messages, _network_messages, _emitted_events = _install_do_search_environment(
        monkeypatch, buddy_users=["buddy_a", "buddy_b"]
    )

    component.do_search("rareprobe", mode="buddies", switch_page=False)

    created = next(iter(component.searches.values()))
    assert created.mode == "buddies"
    assert list(created.users or []) == ["buddy_a", "buddy_b"]
    assert [getattr(msg, "search_username", None) for msg in sent_messages] == ["buddy_a", "buddy_b"]


def test_buddy_snapshot_not_current_buddy_list_controls_response_admission():
    token = 520004
    search = _make_search_request(token, mode="buddies", users=["buddy_before"])

    accepted = _msg(token, username="buddy_before")
    _dispatch(search, accepted)
    assert accepted.token == token

    later_added = _msg(token, username="buddy_after")
    _dispatch(search, later_added)
    assert later_added.token is None


def test_user_scoped_response_from_requested_peer_still_passes():
    token = 520005
    search = _make_search_request(token, mode="user", users=["expected_peer"])
    msg = _msg(token, username="expected_peer")
    _dispatch(search, msg)
    assert msg.token == token


def test_global_search_response_remains_broad_source_compatible():
    token = 520006
    search = _make_search_request(token, mode="global")
    msg = _msg(token, username="any_peer")
    _dispatch(search, msg)
    assert msg.token == token


def test_room_search_response_remains_split_to_compatibility_backlog():
    token = 520007
    search = _make_search_request(token, mode="rooms", room="room-alpha")
    msg = _msg(token, username="room_peer")
    _dispatch(search, msg)
    assert msg.token == token
