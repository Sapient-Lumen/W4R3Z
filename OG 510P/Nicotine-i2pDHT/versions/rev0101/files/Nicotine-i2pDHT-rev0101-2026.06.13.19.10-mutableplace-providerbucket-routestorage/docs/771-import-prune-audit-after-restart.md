# Import-prune audit after restart

`importpruneaudit.py` joins publication, redaction witness, import archive, and lineage prune state.

The goal is to prevent a later restart or prune lane from accepting a convenient subset of evidence. The audit requires exact-boundary agreement and retained classes for publication, redaction witness, import archive, lineage prune, and contradiction memory.

This is not consensus. It is local restart-memory pressure before a redacted summary can be treated as safe enough to advance.

Audit needle: import-prune audit.
