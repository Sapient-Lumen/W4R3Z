# wake from amnesia rev0069

Start here after a restart:

1. rev0068 audited closure after archive/prune replay.
2. rev0069 adds a closure seal so the audit is compact but not forgetful.
3. Retention proof checks the evidence classes that must survive compaction.
4. Audit export prepares redacted summaries without network side effects.
5. The most important invariant is: contradiction memory must survive every step.

Do not treat `auditexport.py` as a live publication layer. It is a no-network boundary and metadata-leak pressure surface.
