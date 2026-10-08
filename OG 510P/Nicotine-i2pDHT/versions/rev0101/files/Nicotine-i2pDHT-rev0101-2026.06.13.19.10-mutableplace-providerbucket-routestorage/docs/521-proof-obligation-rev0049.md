# Proof obligation — rev0049

Show that a public bridge side effect cannot advance merely because rev0048 component reports passed.

Required demonstrations:

- outbox entries reject component digest drift
- outbox entries reject action/scope/request/payload drift
- same-sequence outbox forks are quarantined
- idempotency conflicts are quarantined while same-effect replays become watchful idempotent replays
- watch debt and hard-negative redress pressure do not silently become clean queue entries
- audit-gap repair/withdraw planning needs exact-scope signals, diversity, and a staged outbox when repair is requested
- outboxfold sees rev0049 from public pointers, docs, fold map, fold registry, and surface ledger
