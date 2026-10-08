#!/usr/bin/env python3
"""Apply the rev0074 PB-01 origin-aware research experiment."""
from pathlib import Path
import sys


def replace_once(text, old, new, label):
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one source pattern, found {count}")
    return text.replace(old, new, 1)


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: apply_pb01_origin_aware_patch_rev0074.py SOURCE_ROOT")
    path = Path(sys.argv[1]).resolve() / "pynicotine" / "slskproto.py"
    text = path.read_text(encoding="utf-8")
    old = '''    def _replace_existing_connection(self, init):\n\n        username = init.target_user\n        conn_type = init.conn_type\n\n        if username == self._server_username:\n            return\n\n        prev_init = self._username_init_msgs.pop(username + conn_type, None)\n\n        if prev_init is None or prev_init.sock is None:\n            return\n\n        log.add_conn("Discarding existing connection of type %s to user %s", (init.conn_type, username))\n\n        init.outgoing_msgs = prev_init.outgoing_msgs\n        prev_init.outgoing_msgs = []\n\n        self._close_connection(self._conns[prev_init.sock])\n'''
    new = '''    def _replace_existing_connection(self, init):\n\n        username = init.target_user\n        conn_type = init.conn_type\n\n        if username == self._server_username:\n            return True\n\n        init_key = username + conn_type\n        prev_init = self._username_init_msgs.pop(init_key, None)\n\n        if prev_init is None or prev_init.sock is None:\n            return True\n\n        prev_conn = self._conns.get(prev_init.sock)\n\n        if prev_conn is None:\n            return True\n\n        if prev_conn.is_established and prev_conn.response_token is None:\n            self._username_init_msgs[init_key] = prev_init\n            log.add_conn(\n                "Rejecting replacement connection of type %s to user %s, "\n                "since an established non-response primary already exists",\n                (conn_type, username)\n            )\n            return False\n\n        log.add_conn("Discarding existing connection of type %s to user %s", (init.conn_type, username))\n\n        init.outgoing_msgs = prev_init.outgoing_msgs\n        prev_init.outgoing_msgs = []\n\n        self._close_connection(prev_conn)\n        return True\n'''
    text = replace_once(text, old, new, "replace-existing-connection")
    old_call = '''            init = msg\n            self._replace_existing_connection(init)\n'''
    new_call = '''            init = msg\n\n            if not self._replace_existing_connection(init):\n                return None\n'''
    text = replace_once(text, old_call, new_call, "peer-init-call")
    path.write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
