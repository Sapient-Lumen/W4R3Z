#!/usr/bin/env python3
from pathlib import Path
import sys

root = Path(sys.argv[1])
path = root / 'pynicotine' / 'slskproto.py'
text = path.read_text()
old_replace = '''    def _replace_existing_connection(self, init):\n\n        username = init.target_user\n        conn_type = init.conn_type\n\n        if username == self._server_username:\n            return\n\n        prev_init = self._username_init_msgs.pop(username + conn_type, None)\n\n        if prev_init is None or prev_init.sock is None:\n            return\n\n        log.add_conn("Discarding existing connection of type %s to user %s", (init.conn_type, username))\n\n        init.outgoing_msgs = prev_init.outgoing_msgs\n        prev_init.outgoing_msgs = []\n\n        self._close_connection(self._conns[prev_init.sock])\n'''
new_replace = '''    def _replace_existing_connection(self, init):\n\n        username = init.target_user\n        conn_type = init.conn_type\n\n        if username == self._server_username:\n            return True\n\n        init_key = username + conn_type\n        prev_init = self._username_init_msgs.pop(init_key, None)\n\n        if prev_init is None or prev_init.sock is None:\n            return True\n\n        prev_conn = self._conns.get(prev_init.sock)\n\n        if prev_conn is None:\n            return True\n\n        if prev_conn.is_established:\n            self._username_init_msgs[init_key] = prev_init\n            log.add_conn(\n                "Rejecting replacement connection of type %s to user %s, "\n                "since an established primary connection already exists",\n                (conn_type, username)\n            )\n            return False\n\n        log.add_conn("Discarding existing connection of type %s to user %s", (init.conn_type, username))\n\n        init.outgoing_msgs = prev_init.outgoing_msgs\n        prev_init.outgoing_msgs = []\n\n        self._close_connection(prev_conn)\n        return True\n'''
if old_replace not in text:
    raise SystemExit('replace_existing_connection pattern not found')
text = text.replace(old_replace, new_replace)
old_call = '''            init = msg\n            self._replace_existing_connection(init)\n'''
new_call = '''            init = msg\n\n            if not self._replace_existing_connection(init):\n                return None\n'''
if old_call not in text:
    raise SystemExit('peer init call pattern not found')
text = text.replace(old_call, new_call)
old_promote = '''        if conn.sock is not None and init.sock is not conn.sock:\n            log.add_conn("Received message on secondary connection of type %s to user %s, "\n                         "promoting to primary connection", (init.conn_type, init.target_user))\n            init.sock = conn.sock\n'''
new_promote = '''        if conn.sock is not None and init.sock is not conn.sock:\n            primary_conn = self._conns.get(init.sock)\n\n            if init.sock is None or primary_conn is None or not primary_conn.is_established:\n                log.add_conn("Received message on secondary connection of type %s to user %s, "\n                             "promoting to primary connection", (init.conn_type, init.target_user))\n                init.sock = conn.sock\n            else:\n                log.add_conn("Received message on secondary connection of type %s to user %s, "\n                             "keeping established primary connection", (init.conn_type, init.target_user))\n'''
if old_promote not in text:
    raise SystemExit('secondary promotion pattern not found')
text = text.replace(old_promote, new_promote)
path.write_text(text)
