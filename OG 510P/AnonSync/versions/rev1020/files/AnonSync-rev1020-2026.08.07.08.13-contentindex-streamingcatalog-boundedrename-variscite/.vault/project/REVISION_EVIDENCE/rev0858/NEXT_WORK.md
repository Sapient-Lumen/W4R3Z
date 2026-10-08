# Rev0858 next work

## 1. Move budgets before allocation

Create a streaming or event-driven manifest decoder that consumes the same
`SyncManifestResourceLimits` before reserving vectors or strings. Return one
frozen manifest/usage pair so validation cannot be forgotten between decode and
identity.

## 2. Bind validation to identity at the type level

Introduce a non-forgeable validated-manifest view or owner. Manifest identity,
diff planning, chunk scheduling, and filesystem application should accept that
capability rather than a broad `SyncFolderManifest` and revalidate ad hoc.

## 3. Define the complete convergence algebra

Extend the rev0856 oracle beyond one conflict winner to rename, delete versus
recreation, object epochs, causal histories, membership/key epochs, retries,
partitions, restart, and external effects. Generate reordered, duplicated,
omitted-then-healed, and concurrent histories against a small deterministic
reference model.

## 4. Isolate hostile interpretation

Move wire/persistence decoding and content inspection into disposable workers
with explicit CPU, memory, wall-clock, output, descriptor, filesystem, and
syscall budgets. Treat the worker result as an observation requiring principal
process validation, not as authority.

## 5. Specify the “Anon” protocol

Define payload encryption, authenticated membership, device generations, key
epochs, rotation, revocation, lost-device recovery, forward secrecy,
post-compromise recovery, backup custody, rollback resistance, metadata
leakage, and realistic erasure limits before using anonymity as a product
claim.

## 6. Reduce audit change amplification

Continue extracting invariant-owned leaves from `sync_domain.cpp`; replace
lexical audits with typed interfaces or semantic model oracles as each boundary
matures. Generate repetitive CMake test/audit registration from checked data.
