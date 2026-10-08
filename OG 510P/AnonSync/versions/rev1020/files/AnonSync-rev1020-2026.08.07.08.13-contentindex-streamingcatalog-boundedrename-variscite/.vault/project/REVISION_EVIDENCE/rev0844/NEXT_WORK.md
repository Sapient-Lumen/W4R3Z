# AnonSync rev0844 next work

## Immediate local correctness

1. State and enforce the writer-exclusive parent-directory contract. At minimum,
   attest ownership/mode/mount assumptions; preferably move ledger-family
   mutations into a narrowly privileged helper that receives a sealed directory
   descriptor and bounded command.
2. Design a non-destructive residue workflow. Staging-only and pre-journal
   temporaries are intentionally preserved; operator tooling should inventory,
   attest, quarantine, and remove them without turning filename patterns into
   deletion authority.
3. Split `LocalJsonlReplayNamespace` into smaller typed capabilities: directory
   traversal/identity, lock ownership, immutable member observation, journal
   publication, and replacement mutation. Keep one top-level state-machine owner
   composing them.
4. Build a filesystem crash oracle beyond exception checkpoints. Exercise
   journal publication, directory barriers, rename, and retirement against
   dm-flakey/loopback or an equivalent persisted-state fault harness on kernels
   that permit it.
5. Add an `openat2` lane on a modern Linux host using explicit `RESOLVE_BENEATH`,
   no-symlink, no-magic-link, and mount-crossing policy, while retaining a
   separately named weaker fallback.

## Make convergence executable

Define a compact deterministic reference model for update, delete, recreation,
rename, duplicate delivery, causal gaps, concurrent operations, schema epochs,
and key epochs. Generate reordered, retried, partitioned, restarted, and
concurrent histories and compare each production transition and receipt with the
model.

## Define the privacy and device protocol

Specify device membership, key epochs, rotation, revocation, lost-device and
state-loss recovery, forward secrecy, post-compromise recovery, payload
confidentiality, metadata leakage, delivery-service assumptions, backup custody,
rollback resistance, and realistic erasure limits before treating “Anon” as an
implemented property.

## Reduce proof cost

Generate repetitive CMake registrations from checked data. Replace lexical
audits with typed dependencies, property tests, and model oracles as those become
available. Move historical handoff evidence into content-addressed archives
rather than recursively copying it into routine revisions.
