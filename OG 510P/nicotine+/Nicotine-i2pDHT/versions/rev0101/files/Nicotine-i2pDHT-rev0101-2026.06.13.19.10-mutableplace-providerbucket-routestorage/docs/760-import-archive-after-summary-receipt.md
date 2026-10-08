# Import archive after summary receipt

Summary receipt is not import-archive permission.

`importarchive.py` turns accepted summary receipt into restart-sticky import archive markers.  Required classes are:

```text
summary_receipt_marker
summary_lineage_marker
handoff_import_marker
contradiction_memory
redacted_summary_memory
local_archive_state
```

The archive is intentionally compact and redacted.  It preserves the fact that handoff/import/summary state existed without turning raw boundary or payload material into exported memory.
