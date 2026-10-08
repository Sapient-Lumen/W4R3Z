# Native call ledger

The call ledger prevents restart drift.  It records that a native shadow was observed, but that the actual route remains `python_fallback` and the Python result is authoritative.

This is deliberately sticky protocol memory, not logging.  A later restart must not reinterpret native shadow evidence as permission to run or select native code.
