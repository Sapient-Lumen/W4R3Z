# Native load re-entry request

`nativeloadreentry.py` joins rev0091 re-entry journal evidence with relaunch-gate evidence. The accepted result is `accept_load_gate_request_only`.

That wording is intentional. The report says:

- load-gate request is ready;
- route-to-load-gate is the only allowed next edge;
- native load is still forbidden;
- native dispatch is still forbidden;
- Python fallback remains active;
- tombstone, quarantine, crash, re-entry, relaunch, oracle, and fallback memory must be preserved.

The high-risk bug being pinned is the shortcut where a relaunch candidate or preflight marker becomes load permission by accident.
