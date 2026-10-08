# rev0770 — SQLite client-data incarnation and authorizer lease

Rev0770 turns the peer-ingress SQLite attestation from a raw-pointer promise
into a use-time capability check.

- Connection incarnation lives in SQLite 3.44+ client data and is destroyed by
  SQLite when the connection closes.
- Every deliberate authorizer reinstall advances an exact generation.
- A prepare-time nonce challenge detects replacement or disablement of
  SQLite's single authorizer callback.
- A `FULLMUTEX` lease remains held through prepare, step, commit/rollback, and
  statement teardown.
- All peer-ingress lifecycle call sites retain the lease with rollback-safe
  declaration order.
- A dedicated adversarial suite and a fail-closed source audit guard the seam.

This evidence is process-local only. Durable receipt/claim/schema-recipe
binding and a canonical full checkpoint-cohost manifest remain future work.
