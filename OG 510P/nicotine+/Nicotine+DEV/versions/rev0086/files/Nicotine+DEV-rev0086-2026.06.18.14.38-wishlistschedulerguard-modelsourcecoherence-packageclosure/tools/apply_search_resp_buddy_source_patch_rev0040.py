#!/usr/bin/env python3
"""Apply rev0040 SEARCH-RESP-01B buddy-scope snapshot/admission guard.

The patch is intentionally stacked on the rev0039 user-scope admission guard:
- direct user searches only accept one of SearchRequest.users;
- buddy searches store a request-time buddy snapshot and only accept that snapshot;
- legacy/manual buddy SearchRequest objects without a snapshot remain broad-source compatible.
"""
from __future__ import annotations

import argparse
from pathlib import Path


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected 1 occurrence, found {count}")
    return text.replace(old, new, 1)


def patch_search_py(path: Path) -> None:
    text = path.read_text()

    # Record a buddy recipient snapshot during search-term processing. This shared
    # anchor covers legacy process_search_term() and master _process_search_term().
    old = '''        elif mode == "buddies":\n            feedback = core.pluginhandler.outgoing_buddy_search_event(search_term)\n\n            if feedback is not None:\n                search_term = feedback[0]\n'''
    new = '''        elif mode == "buddies":\n            feedback = core.pluginhandler.outgoing_buddy_search_event(search_term)\n\n            if feedback is not None:\n                search_term = feedback[0]\n\n            users = tuple(core.buddies.users)\n'''
    text = replace_once(text, old, new, "buddy process snapshot")

    if "def do_buddies_search(self, text):" in text:
        # 3.3.10 / 3.3.x legacy sender shape.
        old = '''        elif mode == "buddies":\n            self.do_buddies_search(search.term_transmitted)\n'''
        new = '''        elif mode == "buddies":\n            self.do_buddies_search(search.term_transmitted, search.users)\n'''
        text = replace_once(text, old, new, "legacy do_search buddy call")

        old = '''    def do_buddies_search(self, text):\n        for username in core.buddies.users:\n            core.send_message_to_server(UserSearch(username, self.token, text))\n'''
        new = '''    def do_buddies_search(self, text, users=None):\n        if users is None:\n            users = tuple(core.buddies.users)\n\n        for username in users:\n            core.send_message_to_server(UserSearch(username, self.token, text))\n'''
        text = replace_once(text, old, new, "legacy buddy sender")

        old = '''        username = msg.username\n        ip_address, _port = msg.addr\n'''
        new = '''        username = msg.username\n\n        if search.mode == "user":\n            expected_users = search.users or ()\n\n            if username not in expected_users:\n                msg.token = None\n                return\n\n        elif search.mode == "buddies" and search.users is not None:\n            if username not in search.users:\n                msg.token = None\n                return\n\n        ip_address, _port = msg.addr\n'''
        text = replace_once(text, old, new, "legacy search-response handler guards")

    else:
        # master sender shape.
        old = '''    def _send_buddies_search_request(self, search):\n        for username in core.buddies.users:\n            core.send_message_to_server(UserSearch(username, search.token, search.term_transmitted))\n'''
        new = '''    def _send_buddies_search_request(self, search):\n        users = search.users if search.users is not None else tuple(core.buddies.users)\n\n        for username in users:\n            core.send_message_to_server(UserSearch(username, search.token, search.term_transmitted))\n'''
        text = replace_once(text, old, new, "master buddy sender")

        old = '''        if isinstance(search, WishSearchRequest) and (search.is_ignored or username in search.ignored_users):\n            msg.token = None\n            return\n'''
        new = '''        if search.mode == "user":\n            expected_users = search.users or ()\n\n            if username not in expected_users:\n                msg.token = None\n                return\n\n        elif search.mode == "buddies" and search.users is not None:\n            if username not in search.users:\n                msg.token = None\n                return\n\n        if isinstance(search, WishSearchRequest) and (search.is_ignored or username in search.ignored_users):\n            msg.token = None\n            return\n'''
        text = replace_once(text, old, new, "master search-response handler guards")

    path.write_text(text)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("checkout", type=Path)
    args = parser.parse_args()
    patch_search_py(args.checkout / "pynicotine" / "search.py")
    print(f"patched {args.checkout / 'pynicotine' / 'search.py'}")


if __name__ == "__main__":
    main()
