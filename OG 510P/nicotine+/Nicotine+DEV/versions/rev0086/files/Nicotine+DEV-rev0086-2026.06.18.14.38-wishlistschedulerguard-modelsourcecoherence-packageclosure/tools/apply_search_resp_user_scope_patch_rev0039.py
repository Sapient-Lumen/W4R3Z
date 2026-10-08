#!/usr/bin/env python3
"""Apply the rev0039 SEARCH-RESP-01A user-scope admission guard."""
from __future__ import annotations
import pathlib
import sys

LEGACY_OLD = '''        username = msg.username
        ip_address, _port = msg.addr
'''
LEGACY_NEW = '''        username = msg.username

        if search.mode == "user":
            expected_users = search.users or ()

            if username not in expected_users:
                msg.token = None
                return

        ip_address, _port = msg.addr
'''
MASTER_OLD = '''        if search is None:
            msg.token = None
            return

        if isinstance(search, WishSearchRequest) and (search.is_ignored or username in search.ignored_users):
'''
MASTER_NEW = '''        if search is None:
            msg.token = None
            return

        if search.mode == "user":
            expected_users = search.users or ()

            if username not in expected_users:
                msg.token = None
                return

        if isinstance(search, WishSearchRequest) and (search.is_ignored or username in search.ignored_users):
'''

def apply(root: pathlib.Path) -> None:
    path = root / "pynicotine" / "search.py"
    text = path.read_text(encoding="utf-8")
    if LEGACY_NEW in text or MASTER_NEW in text:
        print(f"already patched: {path}")
        return
    if LEGACY_OLD in text:
        path.write_text(text.replace(LEGACY_OLD, LEGACY_NEW, 1), encoding="utf-8")
        print(f"patched legacy-style handler: {path}")
        return
    if MASTER_OLD in text:
        path.write_text(text.replace(MASTER_OLD, MASTER_NEW, 1), encoding="utf-8")
        print(f"patched master-style handler: {path}")
        return
    raise SystemExit(f"anchor not found in {path}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: apply_search_resp_user_scope_patch_rev0039.py /path/to/nicotine-plus")
    apply(pathlib.Path(sys.argv[1]))
