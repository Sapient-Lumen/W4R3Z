# ADR 0103: wrap synchronization root mutations in the rollback guard

- Status: accepted and implemented
- Date: 2026-08-20
- Scope: local publication, acceptance, activation, retention, and stored reachability
- Supersedes: the mutation-wiring deferral in ADR 0102

## Context

ADR 0102 froze a crash-recoverable signed guard but deliberately left it beside, rather than around,
the live root stores. The primitive could therefore prove its own transitions without protecting a
product mutation. Stored reachability also had no obligation to compare its four authenticated roots
with the guard before reporting evidence.

## Decision

1. Load the published, accepted, activated, and retained roots under one namespace transaction and
   derive their exact rollback head before every root-file replacement.
2. For every non-duplicate publication, accepted-HEAD advance, activation pointer, retention pin, and
   retention unpin, write a signed pending successor, atomically replace exactly one root file, then
   finalize that successor while retaining the transaction.
3. Leave pending state intact when the root commit reports failure. Atomic replacement can have
   become durable before a late synchronization error; the next mutation must inspect the actual
   roots and reconcile the exact before or after side instead of guessing.
4. Make stored reachability perform a non-mutating guard check under the same transaction as root
   loading and object inventory. Either exact pending side is valid crash evidence, but read-only
   planning does not repair it because it does not possess the device signing identity.
5. Add a fresh-process oracle that independently restores an older publication root and an older
   guard, proves each mixed snapshot is refused, restores the coherent current pair, and advances.
6. Keep object deletion absent.

## Consequences

- Every implemented local root mutation is protected against isolated deletion, rollback, or fork.
- A crash before or after an atomic root replacement remains recoverable on the next signed mutation;
  read-only reachability can safely identify either exact side without changing state.
- The guard does not make local storage monotonic. An attacker who restores one complete coherent old
  guard together with all four matching roots can still replay that snapshot.
- Destructive garbage collection remains blocked pending an explicit external/hardware witness policy
  and separate collection semantics.
