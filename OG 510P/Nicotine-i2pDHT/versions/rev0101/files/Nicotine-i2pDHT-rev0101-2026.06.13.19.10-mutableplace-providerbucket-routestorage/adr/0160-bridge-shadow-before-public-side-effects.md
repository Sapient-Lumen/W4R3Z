# ADR 0160 — Bridge shadow before public side effects

Accepted for rev0048.

A publication guard, ledger, and quench report are still not a public bridge side effect.  rev0048 adds a signed no-network bridge-shadow plan that binds the exact intent, payload digest, scope, request, component digests, sequence, previous digest, and family/path hints before a future transport or mutable-record write may proceed.

This keeps dry-run acceptance separate from actual I2P/SAM or DHT publication.
