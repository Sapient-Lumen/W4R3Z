# Continuity journal restart memory

`continuityjournal.py` is a tiny continuity-specific restart journal.  It does not replace the generic journal/checkpoint lanes; it pins the special replay-memory requirement created by service-continuity reports.

A journal entry carries:

- sequence;
- previous entry digest;
- service and scope;
- continuity report digest;
- accepted/quarantined/withdrawal/hard-negative kind;
- hard-negative digests.

Replay rejects same-sequence forks, previous-link mismatches, old-sequence rollback, duplicate entries, scope/service drift, and hard-negative drops.  Gaps are held as crash-tail pressure rather than accepted as clean memory.
