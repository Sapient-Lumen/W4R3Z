# AnonSync work after rev0874

## 1. Receiver-side effect ownership

Implement a narrow receiver owner that admits one canonical authenticated
message, materializes payload bytes into a private temporary object, publishes a
visible filesystem effect atomically, and emits one terminal receipt bound to
the exact effect and actor epoch. Duplicate delivery must return the same
terminal result without replaying the effect.

## 2. Authentication and key epochs

Define actor public-key identities, signed operation/message envelopes,
membership/key epochs, rotation, revocation, recovery, and treatment of old
epochs. Do not use local unkeyed digests as malicious-writer defenses.

## 3. Complete retry policy

Add a failure taxonomy, bounded deterministic backoff with policy-owned jitter,
maximum attempt count and age, poison/dead-letter states, operator authority,
and an indexed durable wake queue. Preserve exact failure/decision evidence.

## 4. Differential incremental owner

Retain the current O(history) owner as an oracle. Add an indexed point-read
implementation and run generated traces, migrations, tamper cases, and crash
frontiers through both. Require periodic full re-attestation and an explicit
repair protocol.

## 5. Clock trust decision

Decide whether host/kernel time is an accepted product trust boundary. If not,
design authenticated time or witness evidence, rollback-resistant key/counter
ownership, recovery semantics, and availability behavior before extending lease
claims across machines.

## 6. State-machine generation and migration fuzzing

Generate long traces across clock observations, claims, renewals, settlement,
retry release, recovery, policy replacement, restart, and schema migration.
Differentially compare pure state, SQLite state, canonical bytes, and cutpoint
digests. Add failure injection at every publication frontier.

## 7. Resource and privacy models

Bind CPU, memory, WAL, filesystem bytes, network bytes, retained identities,
dependency fanout, timer wake work, and peer fairness to measurable physical
limits. Define the transport and observable metadata before making anonymity or
unlinkability claims.
