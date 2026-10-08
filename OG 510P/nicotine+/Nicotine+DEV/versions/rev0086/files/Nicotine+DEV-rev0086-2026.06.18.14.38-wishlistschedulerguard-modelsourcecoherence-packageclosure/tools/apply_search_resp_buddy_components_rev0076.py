#!/usr/bin/env python3
"""Apply only the rev0040 buddy snapshot and claimed-name components.

Research-only. The historical rev0040 helper also stacks the rev0039 direct
user-search guard, which prevents packet-specific attribution. This helper
preserves the historical buddy semantics, including fail-open behavior when
``SearchRequest.users is None``.
"""
from __future__ import annotations

import argparse
from pathlib import Path


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


def patch_search(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    if (
        "users = tuple(core.buddies.users)" in text
        and 'search.mode == "buddies" and search.users is not None' in text
    ):
        return "already-patched"

    old = '''        elif mode == "buddies":\n            feedback = core.pluginhandler.outgoing_buddy_search_event(search_term)\n\n            if feedback is not None:\n                search_term = feedback[0]\n'''
    text = replace_once(
        text,
        old,
        old + '''\n            users = tuple(core.buddies.users)\n''',
        "buddy recipient snapshot",
    )

    if "def do_buddies_search(self, text):" in text:
        lane = "legacy-3.3.x"
        text = replace_once(
            text,
            '''        elif mode == "buddies":\n            self.do_buddies_search(search.term_transmitted)\n''',
            '''        elif mode == "buddies":\n            self.do_buddies_search(search.term_transmitted, search.users)\n''',
            "legacy buddy call",
        )
        text = replace_once(
            text,
            '''    def do_buddies_search(self, text):\n        for username in core.buddies.users:\n            core.send_message_to_server(UserSearch(username, self.token, text))\n''',
            '''    def do_buddies_search(self, text, users=None):\n        if users is None:\n            users = tuple(core.buddies.users)\n\n        for username in users:\n            core.send_message_to_server(UserSearch(username, self.token, text))\n''',
            "legacy buddy sender",
        )
        text = replace_once(
            text,
            '''        username = msg.username\n        ip_address, _port = msg.addr\n''',
            '''        username = msg.username\n\n        if search.mode == "buddies" and search.users is not None:\n            if username not in search.users:\n                msg.token = None\n                return\n\n        ip_address, _port = msg.addr\n''',
            "legacy buddy claimed-name guard",
        )
    else:
        lane = "master"
        text = replace_once(
            text,
            '''    def _send_buddies_search_request(self, search):\n        for username in core.buddies.users:\n            core.send_message_to_server(UserSearch(username, search.token, search.term_transmitted))\n''',
            '''    def _send_buddies_search_request(self, search):\n        users = search.users if search.users is not None else tuple(core.buddies.users)\n\n        for username in users:\n            core.send_message_to_server(UserSearch(username, search.token, search.term_transmitted))\n''',
            "master buddy sender",
        )
        text = replace_once(
            text,
            '''        if isinstance(search, WishSearchRequest) and (search.is_ignored or username in search.ignored_users):\n            msg.token = None\n            return\n''',
            '''        if search.mode == "buddies" and search.users is not None:\n            if username not in search.users:\n                msg.token = None\n                return\n\n        if isinstance(search, WishSearchRequest) and (search.is_ignored or username in search.ignored_users):\n            msg.token = None\n            return\n''',
            "master buddy claimed-name guard",
        )

    path.write_text(text, encoding="utf-8")
    return lane


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("checkout", type=Path)
    args = parser.parse_args()
    path = args.checkout / "pynicotine" / "search.py"
    lane = patch_search(path)
    print(f"patched={path} lane={lane} components=buddy-only")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
