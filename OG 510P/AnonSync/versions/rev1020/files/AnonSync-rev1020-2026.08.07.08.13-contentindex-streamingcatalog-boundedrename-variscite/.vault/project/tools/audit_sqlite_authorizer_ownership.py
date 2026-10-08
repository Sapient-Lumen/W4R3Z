#!/usr/bin/env python3
"""Compatibility entry point for the focused SQLite authorizer-owner audit.

The historical audit accumulated a second, stale inventory of client-data and
callback ownership rules. Keep its command-line name for external callers, but
route all current checks through the registered rev0850 audit so the two proof
surfaces cannot drift again.
"""

from audit_sqlite_authorizer_owner import main

if __name__ == "__main__":
    raise SystemExit(main())
