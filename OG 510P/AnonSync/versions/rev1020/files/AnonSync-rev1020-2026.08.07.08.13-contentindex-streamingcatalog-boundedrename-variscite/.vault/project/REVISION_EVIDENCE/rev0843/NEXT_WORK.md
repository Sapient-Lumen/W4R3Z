# AnonSync rev0843 next work

## Immediate local correctness

1. Model the local JSONL replacement as one crash state machine: journal file
   fsync, journal-directory fsync, temp file fsync, ledger rename,
   ledger-directory fsync, journal unlink, journal-directory fsync, and recovery
   at every cut.
2. Introduce a retained directory-descriptor namespace owner. Keep all relative
   open/rename/unlink/fsync operations beneath that authority; add `openat2`
   resolution constraints where the kernel supports them and a deliberately
   weaker, explicit fallback elsewhere.
3. Replace raw borrowed descriptor integers at higher layers with a scoped type
   that documents the caller's no-close/no-reuse lifetime obligation.

## Make convergence executable

Define a small deterministic reference model for update, delete, recreation,
rename, duplicate delivery, causal gaps, concurrent operations, schema epochs,
and key epochs. Generate reordered, retried, partitioned, restarted, and
concurrent histories and compare every production transition with the model.

## Define the privacy/device protocol

Specify device membership, key epochs, rotation, revocation, lost-device and
state-loss recovery, forward secrecy, post-compromise recovery, payload
confidentiality, metadata leakage, delivery-service assumptions, backup custody,
rollback resistance, and realistic erasure limits before treating “Anon” as an
implemented property.

## Reduce proof cost

Continue extracting invariant owners from the large domain, replay, and selftest
translation units. Generate repetitive CMake registrations from checked data.
Retire lexical audits when type structure, dependency constraints, property tests,
or model oracles enforce the same invariant. Move historical handoff evidence to
content-addressed archives rather than recursively copying it into routine
revisions.
