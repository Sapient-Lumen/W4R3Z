# AnonSync rev0850 next work

## 1. One SQLite callback registry

Unify busy handler, progress handler, authorizer, and future retained callback
slots under one exact-generation connection registry. Give each singleton slot
an explicit generation, typed installation token, executable identity proof
where possible, and one dependency-ordered close transition. Eliminate raw
internal teardown hooks once the registry is structurally owned by the database
handle slot.

## 2. Race-oriented teardown model

Specify the allowed interleavings among connection borrows, callback execution,
replacement, transaction boundaries, and close. Add deterministic scheduling
probes and a ThreadSanitizer lane where the environment supports it. Distinguish
fail-stop detection of misuse from a proof that no data race occurs.

## 3. Policy-context ownership

The connection-authority API accepts `void* policy_context`, while production
currently supplies `nullptr`. Replace ambient external lifetime with a stable
owned policy object or an explicitly borrowed generation. Add death probes for
premature policy-context destruction before enabling non-null production use.

## 4. Reduce monolithic validation cost

`sync_domain.cpp`, broad selftest translation units, and repeated static-library
link fan-out remain major change amplifiers. Measure rebuild dependency edges,
extract narrow ABI-stable libraries, generate repetitive CMake registration
from checked data, and retire lexical audits after equivalent typed or
model-based boundaries exist.

## 5. Make convergence executable

Define the operation algebra for create, update, delete, recreation, rename,
concurrent mutation, schema/key epoch change, and external effects. Build a
small deterministic reference model, generate reordered/duplicated/partitioned
histories, and compare every replica's final state and recovery receipts.

## 6. Cross-resource crash oracle

Model SQLite transactions, WAL/checkpoints, manifests, files, directories,
receipts, and downstream effects as one cutpoint state machine. Recovery must
complete exactly one authorized transition or preserve the prior state. Include
failures around callback detachment, transaction rollback, and connection close.

## 7. Hostile-input isolation and privacy protocol

Move untrusted SQLite/document interpretation into disposable workers with
bounded framing and operating-system resource controls. Separately specify
payload encryption, membership, device/key epochs, rotation and revocation,
metadata leakage, forward secrecy, post-compromise recovery, backup custody,
and realistic erasure limits before treating the project name as an anonymity
claim.
