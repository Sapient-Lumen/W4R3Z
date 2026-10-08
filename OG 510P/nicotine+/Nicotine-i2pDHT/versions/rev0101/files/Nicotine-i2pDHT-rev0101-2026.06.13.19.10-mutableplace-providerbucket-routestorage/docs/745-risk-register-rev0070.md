# Risk register rev0070

Risks exercised in this revision:

- redacted export treated as if it were receipt;
- export receipt leaking raw boundary or payload material;
- retention GC deleting contradiction memory;
- retention GC dropping hard-negative markers;
- closure handoff using a mismatched boundary or stale component digest;
- handoff becoming a public leakage surface;
- fold/registry/ledger drift hiding active surfaces.

Nonclaims remain unchanged: no live transport, no production DHT, no production export/handoff protocol, no global reputation, no consensus, no privacy guarantee.
