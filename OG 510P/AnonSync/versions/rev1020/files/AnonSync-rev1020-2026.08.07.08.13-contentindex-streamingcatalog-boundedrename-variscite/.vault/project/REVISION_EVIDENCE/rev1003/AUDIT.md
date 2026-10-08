# Rev1003 audit

Rev1003 bounds same-path predecessor content-defined projection to 32 MiB of actual source bytes per reconciliation apply. The process-local partial index survives subsequent applies only while its exact target operation, predecessor operation, source metadata, payload-store authority, and projection continuation remain valid. Completed chunks may accelerate target construction before the predecessor manifest is complete; only a completed exact source projection becomes a retained manifest.

The implementation shares one incremental digest/offset index helper with cross-file projection. Any lower projection failure clears the enclosing predecessor or cross-file state so stale outer offsets cannot survive an inactive inner continuation. A 48 MiB shifted-insertion regression requires two projection steps, proves reuse before complete source indexing, and keeps each apply beneath the shipping 32 MiB predecessor-read frontier.

The acceleration does not replace publication authority. The assembled target is still verified by an exact whole-target SHA-256 pass before publication. That terminal pass remains complete-file I/O and is not restart-durable. A prototype that attempted to carry raw SHA state beside a mutable pathname was rejected because it lacked a separately framed, identity-bound, crash-recoverable authority model.

This revision therefore improves bounded apply latency and early delta reuse without claiming a durable global chunk index, bounded total synchronization I/O, or elimination of final whole-file verification.
