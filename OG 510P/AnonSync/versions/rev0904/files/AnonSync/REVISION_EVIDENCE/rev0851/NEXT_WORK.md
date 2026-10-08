# AnonSync work after rev0851

## 1. Unify retained callbacks at the connection boundary

Busy, progress, and authorizer owners are individually hardened, but their
close ordering is still composed by several layers. Introduce one exact
connection-generation callback registry with named slots, explicit dependency
edges, and a single revoke-all-before-close transition. Keep each callback's
focused owner, but centralize lifecycle orchestration and executable state
inspection.

## 2. Replace type-erased policy context at the public edge

Add a typed factory that accepts `shared_ptr<T>` and a noncapturing policy
adapter, preserving a stable C bridge while making callback/context type
agreement compile-time visible. Decide whether aliasing shared pointers and
custom deleters are part of the supported contract. Document and test
post-fork provenance rules.

## 3. Add race-oriented validation

Run ThreadSanitizer on system SQLite or another fully instrumented SQLite build,
then generate close/replace/prepare interleavings around all callback slots.
The current exact mutex and generation proofs do not establish general
concurrent teardown safety.

## 4. Make convergence executable

Build a small deterministic reference model for create, update, delete,
recreation, rename, schema/key epoch changes, and external effects. Generate
histories with duplicates, reordering, partitions, concurrency, retries,
restart, and crash recovery. Compare every replica and the C++ implementation
against the model.

## 5. Isolate hostile interpretation

Move hostile SQLite/document parsing into disposable workers with sealed
descriptors, CPU/memory/output/time limits, restricted filesystem view, and a
small bounded protocol. Seccomp and Landlock can be layers, not standalone
proofs.

## 6. Reduce cube change amplifiers

Extract invariant-owned components from the 15,000-line domain translation
unit, generate repetitive CMake declarations from checked data, and retire
source-spelling audits when typed APIs or behavioral oracles supersede them.
Stop recursively expanding historical evidence in ordinary handoffs.

## 7. Specify privacy and device/key semantics

Define payload encryption, device generations, key epochs, membership,
rotation, revocation, lost-device recovery, rollback resistance, forward
secrecy, post-compromise recovery, metadata leakage, backup custody, and
realistic erasure limits before treating “Anon” as an implemented property.
