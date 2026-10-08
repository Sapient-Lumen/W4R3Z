"""
Fixed-behavior regression for SEARCH-RESP-01C room-scoped search response admission.

The room fix is intentionally narrower than a blanket source gate: room responses
are constrained only when a request-time joined-room membership snapshot exists.
If no local room membership snapshot is available, room searches remain broad-
source compatible to avoid silently breaking server-mediated RoomSearch behavior.
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
        addr=("203.0.113.92", 4999),
        list=[(1, "rareprobe\\room.flac", 1234, None, [])],
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


def _make_component(token=530000):
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


def _install_do_search_environment(monkeypatch, room_users=None):
    sent_messages = []
    network_messages = []
    emitted_events = []

    def send_message_to_server(msg):
        sent_messages.append(msg)

    def send_message_to_network_thread(msg):
        network_messages.append(msg)

    joined_rooms = {}
    if room_users is not None:
        joined_rooms["room-alpha"] = SimpleNamespace(users=list(room_users))

    dummy_core = SimpleNamespace(
        buddies=SimpleNamespace(users=[]),
        chatrooms=SimpleNamespace(joined_rooms=joined_rooms),
        users=SimpleNamespace(login_username="local_user"),
        pluginhandler=DummyPluginHandler(),
        send_message_to_server=send_message_to_server,
        send_message_to_network_thread=send_message_to_network_thread,
    )
    monkeypatch.setattr(search_mod, "core", dummy_core)

    monkeypatch.setattr(
        search_mod,
        "events",
        SimpleNamespace(emit=lambda *args, **kwargs: emitted_events.append((args, kwargs))),
    )

    search_mod.config.sections.setdefault("searches", {})
    monkeypatch.setitem(search_mod.config.sections["searches"], "enable_history", False)
    monkeypatch.setitem(search_mod.config.sections["searches"], "history", [])

    return sent_messages, network_messages, emitted_events


def test_room_scoped_response_from_peer_outside_request_snapshot_is_rejected():
    token = 530001
    search = _make_search_request(token, mode="rooms", room="room-alpha", users=("room_a", "room_b"))
    msg = _msg(token, username="not_in_room_snapshot")
    _dispatch(search, msg)
    assert msg.token is None


def test_room_scoped_response_from_snapshot_member_is_preserved():
    token = 530002
    search = _make_search_request(token, mode="rooms", room="room-alpha", users=("room_a", "room_b"))
    msg = _msg(token, username="room_b")
    _dispatch(search, msg)
    assert msg.token == token


def test_room_scoped_response_without_snapshot_remains_broad_source_compatible():
    token = 530003
    search = _make_search_request(token, mode="rooms", room="room-alpha", users=None)
    msg = _msg(token, username="peer_not_in_local_snapshot")
    _dispatch(search, msg)
    assert msg.token == token


def test_room_search_captures_membership_snapshot_when_joined_room_has_users(monkeypatch):
    component = _make_component(token=530100)
    sent_messages, _network_messages, _emitted_events = _install_do_search_environment(
        monkeypatch, room_users=["room_a", "room_b"]
    )

    component.do_search("rareprobe", mode="rooms", room="room-alpha", switch_page=False)

    created = next(iter(component.searches.values()))
    assert created.mode == "rooms"
    assert created.room == "room-alpha"
    assert tuple(created.users or ()) == ("room_a", "room_b")
    assert len(sent_messages) == 1
    assert getattr(sent_messages[0], "room", None) == "room-alpha"


def test_room_search_without_known_membership_snapshot_keeps_users_unset(monkeypatch):
    component = _make_component(token=530101)
    sent_messages, _network_messages, _emitted_events = _install_do_search_environment(monkeypatch, room_users=None)

    component.do_search("rareprobe", mode="rooms", room="room-alpha", switch_page=False)

    created = next(iter(component.searches.values()))
    assert created.mode == "rooms"
    assert created.room == "room-alpha"
    assert created.users is None
    assert len(sent_messages) == 1


def test_room_snapshot_not_later_membership_controls_response_admission():
    token = 530004
    search = _make_search_request(token, mode="rooms", room="room-alpha", users=("room_before",))

    accepted = _msg(token, username="room_before")
    _dispatch(search, accepted)
    assert accepted.token == token

    later_added = _msg(token, username="room_after")
    _dispatch(search, later_added)
    assert later_added.token is None


def test_user_and_buddy_source_guards_remain_compatible_with_requested_sources():
    user_token = 530005
    user_search = _make_search_request(user_token, mode="user", users=("expected_peer",))
    user_msg = _msg(user_token, username="expected_peer")
    _dispatch(user_search, user_msg)
    assert user_msg.token == user_token

    buddy_token = 530006
    buddy_search = _make_search_request(buddy_token, mode="buddies", users=("buddy_a", "buddy_b"))
    buddy_msg = _msg(buddy_token, username="buddy_b")
    _dispatch(buddy_search, buddy_msg)
    assert buddy_msg.token == buddy_token


def test_global_search_response_remains_broad_source_compatible():
    token = 530007
    search = _make_search_request(token, mode="global")
    msg = _msg(token, username="any_peer")
    _dispatch(search, msg)
    assert msg.token == token
