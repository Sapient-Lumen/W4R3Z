# Retention GC after export

`retentiongc.py` models compaction after an export has actually been receipted.  It allows soft working-set cleanup while preserving required marker classes:

- closure seal marker;
- retention proof marker;
- export receipt marker;
- redacted export summary;
- contradiction memory when contradiction was previously carried;
- hard-negative marker when live hard-negative memory exists.

The lane deliberately treats garbage collection as a protocol boundary.  GC that drops contradiction memory, live tombstone/revocation-style hard negatives, or exact-boundary markers quarantines rather than accepting convenience cleanup.

Needle: retention GC.
