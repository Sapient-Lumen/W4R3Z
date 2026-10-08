# Redaction archive restart memory

`redactionarchive.py` turns redaction-witness acceptance into restart-sticky local evidence.  The archive requires markers for summary publication, redaction witness, import-prune audit, and contradiction memory.

This prevents a later restart or compaction lane from remembering only “redaction passed” while forgetting why it passed, what boundary it applied to, or which contradiction evidence survived.

redaction archive lower-case audit needle.
