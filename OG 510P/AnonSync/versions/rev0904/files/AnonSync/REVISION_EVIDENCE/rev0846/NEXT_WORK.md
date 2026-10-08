# AnonSync rev0846 next work

## P0 — make convergence executable

Define a compact operation algebra and deterministic reference implementation
for update, delete, recreation, rename, duplicate delivery, causal gaps,
concurrent mutation, schema epochs, object incarnations, and key epochs. Generate
reordered, retried, partitioned, restarted, and concurrent histories; compare
every C++ transition, rejection, state digest, and receipt against the model.

This remains the highest-leverage work because it converts “convergence” from a
name and intention into a falsifiable protocol property.

## P0 — build one cross-resource crash oracle

Model SQLite transaction/WAL/checkpoint state, JSONL files, directories,
manifests, receipts, checkpoint ownership, and downstream effects as one
recovery machine. Enumerate persisted cut sets permitted by an explicit storage
model, not only exception checkpoints in a running process. Preserve the current
fail-closed rule: uncertain residue receives no deletion or transition
authority.

## P1 — make execution ownership architectural

1. Decide whether local mutable persistence is permanently single-threaded. If
   so, route it through one broker/event-loop owner and make cross-thread calls
   bounded messages rather than adding locks to every descriptor capability.
2. Introduce a dependency-light execution-incarnation value that freezes the
   process/thread pair together only if it reduces forgotten-check risk without
   reintroducing non-trivial TLS, runtime registration, or representation
   leakage.
3. Add a ThreadSanitizer lane on a modern supported host. Treat it as defect
   detection, not proof. Add deterministic lifetime tests around handoff,
   shutdown, cancellation, and attempted concurrent destruction.
4. Extend explicit thread-affinity review to every move-only owner with mutable
   revocation, descriptor, lock, SQLite mutex, transaction, or publication
   state. Do not blanket-apply the token to immutable values.
5. Turn the GCC/Clang object-symbol TLS check into a build-time executable audit
   for supported ABIs, with a clearly named fallback where object inspection is
   unavailable.

## P1 — strengthen the process and filesystem boundary

- Prefer immediate exec or fail-stop for production children of multithreaded
  processes; do not infer general child-side safety from the narrow incarnation
  refresh path.
- Add an optional modern-Linux backend using `openat2` beneath/no-symlink/
  no-magic-link policy and `statx` mount IDs where available. Keep the current
  portable fallback distinctly named and independently tested.
- Move ledger-family mutations into a narrow broker holding sealed descriptors,
  with bounded commands, dropped ambient descriptors/capabilities, resource
  ceilings, and layered filesystem/syscall restrictions.
- Design an operator-visible, non-destructive quarantine workflow for staging
  and pre-journal residue.

## P1 — define privacy, devices, and keys

Specify device membership, key epochs, rotation, revocation, lost-device and
state-loss recovery, forward secrecy, post-compromise recovery, payload
confidentiality, metadata leakage, delivery-service assumptions, backup custody,
rollback resistance, and realistic erasure limits before treating “Anon” as an
implemented property.

## P2 — reduce proof cost

Generate repetitive CMake targets and CTest registrations from checked data.
Derive inherited-process consumer inventories from explicit target properties
rather than duplicated source text. Replace lexical source audits with typed
dependencies, target-graph checks, property tests, and model oracles as those
become available. Store historical revision evidence content-addressably rather
than recursively copying thousands of unchanged files into each handoff.
