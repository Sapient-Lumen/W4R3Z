# Rev0859 next work

## 1. Budget specialized chunk consumers

Inventory the scheduling, receipt, transfer, repair, and sidecar-query paths
that consume subsets of `sync_session_manifest_chunks`. Give each a narrow
purpose-owned maximum row and byte budget. Do not force them through the
complete-entry decoder when they do not need lineage or full coverage.

## 2. Bind validated reconstruction to identity by type

Return a non-forgeable frozen entry capability carrying the exact resource
usage and identity digests. Diff planning, scheduling, staging, and recovery
should accept that capability rather than a broad `SyncManifestEntry` plus a
convention that validation happened earlier.

## 3. Move the boundary ahead of SQLite ownership

Use a row/event interface that exposes bounded borrowed values and declared
shape to the owner before constructing scalar `std::string` objects. The
current scalar copies are individually small and bounded, but a complete
boundary would make even those ownership transitions explicit.

## 4. Isolate hostile interpretation

Move database and wire interpretation into disposable workers with CPU, memory,
wall-clock, output, descriptor, namespace, filesystem, and syscall limits.
Treat worker results as observations requiring principal-process validation.

## 5. Complete the convergence algebra

Extend the deterministic reference model beyond conflict winner selection to
rename, delete versus recreation, object epochs, causal history, membership and
key epochs, retries, partitions, restart, external effects, and multi-peer
propagation.

## 6. Specify the “Anon” protocol

Define payload encryption, authenticated membership, device generations, key
epochs, rotation, revocation, lost-device recovery, forward secrecy,
post-compromise recovery, backup custody, rollback resistance, metadata
leakage, and realistic erasure limits before anonymity is a product claim.

## 7. Reduce change amplification

Continue extracting invariant-owned leaves from the 15,108-line domain unit.
Replace lexical source audits with typed interfaces or executable semantic
oracles as boundaries mature. Generate repetitive CMake registration from
checked declarative inventories.
