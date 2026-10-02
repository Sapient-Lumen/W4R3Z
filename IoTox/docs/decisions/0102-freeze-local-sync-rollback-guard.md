# ADR 0102: freeze the local synchronization rollback guard

- Status: accepted and implemented as a local primitive
- Date: 2026-08-20
- Scope: restart comparison of published, accepted, activated, and retained root heads
- Depends on: ADRs 0097 through 0101

## Context

All persisted roots are authenticated and share one transaction, but each complete older signed file
can be replayed independently after restart. A crash-safe local witness must distinguish the only two
valid states around an atomic root replacement without claiming hardware monotonicity.

## Decision

1. Represent each root as an exact `(counter, record digest)` pair: generation plus complete signed
   publication digest, generation plus accepted record, generation plus activated accepted-record
   identity, and retention mutation plus complete signed snapshot digest.
2. Persist one canonical 496-byte guard containing magic/version, namespace, stable device key, four
   committed roots, an optional four-root pending successor, and a signature over the exact body under
   `iotox-sync-rollback-guard-signature-v1`.
3. Use `begin(current,next) -> atomic state replace -> finish(next)` under the namespace transaction.
   On restart, committed means the state replace did not land; pending means it landed. Either exact
   side is reconciled and every third head fails closed.
4. Refuse a missing guard beside nonempty current roots. A first transition may establish a guard only
   from the exactly empty root set; there is no implicit adoption of preexisting state.
5. Require a private real root and guard directory plus an owner-owned mode-0600 single-link no-follow
   guard file. Foreign keys, malformed encodings, and signature changes fail closed.
6. Do not add deletion and do not describe this local guard as an independent monotonic witness.

## Consequences

- The primitive can detect isolated root rollback, deletion, or fork and recover either power-cut side.
- Every mutation path must still be wired to the begin/finish protocol before the guard protects live
  product transitions.
- Coordinated replay of a matching old guard and all old roots remains possible. Preventing it requires
  hardware monotonic state or an external owner/replica witness.
- Garbage collection remains prohibited.
