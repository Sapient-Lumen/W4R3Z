# SPDX-License-Identifier: GPL-3.0-or-later
"""Current-behavior witness for SEARCH-SEND-POLICY-01.

This test intentionally documents the current behavior observed during audit.  It
is not a proposed fixed-behavior test: maintainers can invert the assertions when
choosing a compatible policy for search-request admission, IP/geoblock handling,
and plugin notification order.
"""

from types import SimpleNamespace

import pytest


class FakeLog:
    def __init__(self):
        self.search_entries = []

    def add_search(self, *args, **kwargs):
        self.search_entries.append((args, kwargs))


class FakePluginHandler:
    def __init__(self):
        self.search_notifications = []
        self.distrib_notifications = []

    def search_request_notification(self, searchterm, username, token):
        self.search_notifications.append((searchterm, username, token))

    def distrib_search_notification(self, searchterm, username, token):
        self.distrib_notifications.append((searchterm, username, token))


class FakeUploads:
    pending_shutdown = False
    upload_speed = 1234

    def is_new_upload_accepted(self):
        return True

    def get_upload_queue_size(self, username):
        return 0


class FakeUsers:
    login_username = "local_user"


class FakeShares:
    def __init__(self, permission_level_public, permission_level_banned, *, mode="public_unless_ip"):
        self.permission_level_public = permission_level_public
        self.permission_level_banned = permission_level_banned
        self.mode = mode
        self.permission_calls = []
        self.file_path_index = ("Music\\needle.mp3",)
        self.share_dbs = {
            "words": {"needle": [0]},
            "public_files": {"Music\\needle.mp3": ("Music\\needle.mp3", 1024, "mp3", [])},
            "buddy_files": {},
            "trusted_files": {},
        }

    def check_user_permission(self, username, ip_address=None):
        self.permission_calls.append((username, ip_address))

        if self.mode == "always_banned":
            return self.permission_level_banned, "blocked"

        if self.mode == "public_unless_ip" and ip_address == "203.0.113.44":
            return self.permission_level_banned, "geo/ip blocked in witness policy"

        return self.permission_level_public, ""


class FakeCore:
    def __init__(self, shares, pluginhandler):
        self.users = FakeUsers()
        self.uploads = FakeUploads()
        self.shares = shares
        self.pluginhandler = pluginhandler
        self.sent_peer_messages = []

    def send_message_to_peer(self, username, message):
        self.sent_peer_messages.append((username, message))


class FakeConfig:
    def __init__(self, *, search_results=True, maxresults=10, min_search_chars=1):
        self.sections = {
            "searches": {
                "search_results": search_results,
                "maxresults": maxresults,
                "min_search_chars": min_search_chars,
            },
            "transfers": {
                "reveal_buddy_shares": False,
                "reveal_trusted_shares": False,
            },
        }


@pytest.fixture()
def harness(monkeypatch):
    import pynicotine.search as search_mod

    def _make(*, search_results=True, maxresults=10, min_search_chars=1, share_mode="public_unless_ip"):
        shares = FakeShares(
            search_mod.PermissionLevel.PUBLIC,
            search_mod.PermissionLevel.BANNED,
            mode=share_mode,
        )
        pluginhandler = FakePluginHandler()
        fake_core = FakeCore(shares, pluginhandler)

        monkeypatch.setattr(search_mod, "config", FakeConfig(
            search_results=search_results,
            maxresults=maxresults,
            min_search_chars=min_search_chars,
        ))
        monkeypatch.setattr(search_mod, "core", fake_core)
        monkeypatch.setattr(search_mod, "log", FakeLog())

        search = search_mod.Search.__new__(search_mod.Search)

        # The audited lanes differ slightly in Search.__slots__.  Set only
        # attributes present in the current source lane.
        initial_values = {
            "searches": {},
            "excluded_phrases": [],
            "token": 0,
            "wishlist": {},
            "wishlist_file_path": "",
            "wishlist_interval": 0,
            "_own_tokens": set(),
            "_allow_saving_wishlist": False,
            "_wishlist_timer_id": None,
        }

        for attr, value in initial_values.items():
            try:
                setattr(search, attr, value)
            except AttributeError:
                # Attribute is not present in older lane slots and is not needed
                # for the incoming-search request path under test.
                pass

        return search, fake_core

    return _make


def test_server_search_request_permission_check_has_no_requester_ip_context(harness):
    search, fake_core = harness()
    msg = SimpleNamespace(
        searchterm="needle",
        search_username="geo_blocked_requester",
        token=1001,
        # The current Server Code 26 handler ignores any such side-channel field;
        # this field documents the policy we would have applied if an address had
        # been available/bound to the request.
        addr=("203.0.113.44", 2234),
    )

    search._file_search_request_server(msg)

    assert fake_core.shares.permission_calls == [("geo_blocked_requester", None)]
    assert len(fake_core.sent_peer_messages) == 1
    username, response = fake_core.sent_peer_messages[0]
    assert username == "geo_blocked_requester"
    assert response.token == 1001
    assert response.list == [("Music\\needle.mp3", 1024, "mp3", [])]


def test_distributed_search_request_permission_check_has_no_source_ip_context(harness):
    search, fake_core = harness()
    msg = SimpleNamespace(
        searchterm="needle",
        search_username="geo_blocked_requester",
        token=1002,
        addr=("203.0.113.44", 2234),
    )

    search._file_search_request_distributed(msg)

    assert fake_core.shares.permission_calls == [("geo_blocked_requester", None)]
    assert len(fake_core.sent_peer_messages) == 1
    assert fake_core.sent_peer_messages[0][0] == "geo_blocked_requester"


def test_server_plugin_notification_fires_when_core_search_responses_are_disabled(harness):
    search, fake_core = harness(search_results=False)
    msg = SimpleNamespace(searchterm="needle", search_username="requester", token=2001)

    search._file_search_request_server(msg)

    assert fake_core.sent_peer_messages == []
    assert fake_core.shares.permission_calls == []
    assert fake_core.pluginhandler.search_notifications == [("needle", "requester", 2001)]


def test_server_plugin_notification_fires_when_core_permission_rejects(harness):
    search, fake_core = harness(share_mode="always_banned")
    msg = SimpleNamespace(searchterm="needle", search_username="banned_requester", token=2002)

    search._file_search_request_server(msg)

    assert fake_core.shares.permission_calls == [("banned_requester", None)]
    assert fake_core.sent_peer_messages == []
    assert fake_core.pluginhandler.search_notifications == [("needle", "banned_requester", 2002)]


def test_server_plugin_notification_fires_when_core_min_length_rejects(harness):
    search, fake_core = harness(min_search_chars=99)
    msg = SimpleNamespace(searchterm="needle", search_username="requester", token=2003)

    search._file_search_request_server(msg)

    assert fake_core.shares.permission_calls == []
    assert fake_core.sent_peer_messages == []
    assert fake_core.pluginhandler.search_notifications == [("needle", "requester", 2003)]


def test_distributed_plugin_notification_fires_when_core_search_responses_are_disabled(harness):
    search, fake_core = harness(search_results=False)
    msg = SimpleNamespace(searchterm="needle", search_username="requester", token=3001)

    search._file_search_request_distributed(msg)

    assert fake_core.sent_peer_messages == []
    assert fake_core.shares.permission_calls == []
    assert fake_core.pluginhandler.distrib_notifications == [("needle", "requester", 3001)]
