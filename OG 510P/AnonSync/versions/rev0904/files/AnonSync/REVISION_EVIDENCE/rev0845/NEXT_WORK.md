# AnonSync rev0845 next work

## P0 — make convergence executable

Define a compact operation algebra and deterministic reference implementation
for update, delete, recreation, rename, duplicate delivery, causal gaps,
concurrent mutation, schema epochs, object incarnations, and key epochs. Generate
reordered, retried, partitioned, restarted, and concurrent histories; compare
every C++ transition, rejection, state digest, and receipt against the model.

This is the highest-leverage work because it converts “convergence” from a name
and design intention into a falsifiable protocol property.

## P0 — build one cross-resource crash oracle

Model SQLite transaction/WAL/checkpoint state, JSONL files, directories,
manifests, receipts, checkpoint ownership, and downstream effects as one
recovery machine. Enumerate persisted cut sets permitted by an explicit storage
model, not only exception checkpoints in a running process. Preserve the current
fail-closed rule: uncertain residue receives no deletion or transition
authority.

## P1 — strengthen the directory boundary

1. Add an optional modern-Linux backend using `openat2` with beneath-only,
   no-symlink, no-magic-link, and explicit mount-crossing policy; use `statx`
   mount IDs where available. Keep the current fallback distinctly named and
   independently tested.
2. Move ledger-family mutations into a narrow broker process holding a sealed
   directory descriptor. Drop ambient descriptors and capabilities; use bounded
   commands, wall-clock/CPU/memory/output limits, and layered filesystem/syscall
   restrictions.
3. Define the thread-safety contract of directory and namespace owners. Either
   make them explicitly single-thread-affine or add serialized proof/mutation
   tests that prevent races in sticky revocation state.
4. Extract the repeated POSIX descriptor RAII primitive shared by the directory,
   namespace, reader, and test support without hiding process-incarnation rules.
5. Design an operator-visible, non-destructive quarantine workflow for staging
   and pre-journal residue.

## P1 — define privacy, devices, and keys

Specify device membership, key epochs, rotation, revocation, lost-device and
state-loss recovery, forward secrecy, post-compromise recovery, payload
confidentiality, metadata leakage, delivery-service assumptions, backup custody,
rollback resistance, and realistic erasure limits before treating “Anon” as an
implemented property.

## P2 — reduce proof cost

Generate repetitive CMake targets and CTest registrations from checked data.
Replace lexical source audits with typed dependencies, target-graph checks,
property tests, and model oracles as those become available. Store historical
revision evidence content-addressably rather than recursively copying thousands
of unchanged files into every routine handoff.
