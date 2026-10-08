# Rev0866 audit

## Mission finding

AnonSync's heart is an evidence-authorized convergence engine, not a file-copy
loop and not a deterministic-winner function. A real operation must have one
canonical identity, exact causal predecessors, authenticated actor authority,
one durable publication cutpoint, bounded dissemination, and a deterministic
projection from retained evidence plus trust state. Equivalent authorized
evidence must produce equivalent active and visible state after delay,
duplication, reordering, crash, disconnection, and adversarial input.

Rev0865 had a serious semantic shortcut: a vector-clock claim could imply that
predecessor history was possessed even when the exact predecessor operations
were absent. A coherent-looking successor could become active and authorize
later local work before the evidence needed to justify that frontier existed.
That is not merely incomplete anti-entropy; it confuses a summary with proof.

## Correction implemented

Rev0866 adds a canonical bounded operation envelope whose SHA-256 identity binds
folder, path, value kind and metadata, actor/epoch/counter dot, sorted causal
context, and sorted immediate predecessor operation IDs. Decode checks every
count and length against both global limits and remaining bytes before reserve,
then rejects truncation, trailing material, unsorted or duplicate collections,
and alternate encodings.

A pure projector now owns classification of the immutable evidence set. It
derives active nodes, missing-dependency pending nodes, same-dot forks,
transitively invalid dependents, invalid causal envelopes, and dependency
cycles. Exact parent closure must equal the claimed vector context. Direct
parents must form a minimal causal antichain. Fork evidence is retained and both
branches are selected out, independent of arrival order; late forks can revoke
previously active descendants.

The mutable replica model now stores operation payloads exactly once and keeps
active state as an ID set. Its observed context is derived from exact graph
heads. Durable state stores every retained envelope plus the exact locally
authorized operation ID for each local counter. Restore validates those
bindings and recomputes the projection instead of trusting cached active flags.

## Exception-safety finding and repair

The first recovered implementation inserted local evidence before staging the
allocating local-counter-to-operation-ID vector. A later allocation failure
could therefore return an error while retaining the supposedly failed
operation. Rev0866 reserves and stages all allocating work before no-throw
publication and erases any provisional evidence on failure. Remote admission
has the corresponding rollback boundary.

An exhaustive global throwing-`new` harness discovers 182 successful-path local
mint allocation cutpoints and 160 remote-admission cutpoints. Every injected
failure must leave the durable state, evidence set, active projection, visible
state, local counter, and result authority unchanged.

## Waste removed

The projector originally duplicated every active payload, repeatedly rehashed
already-admitted envelopes, rescanned by graph depth, and compared every parent
pair. Rev0866 removes the active payload clone, validates identity at admission
and restore boundaries, propagates dependency verdicts with a worklist, and
uses a top-two distinct-coverage aggregate for parent minimality. The optimized
classifier is checked against a deliberately slow independent oracle over 192
generated branching candidates.

The simulator now moves values into single-destination messages, avoids copying
an operation again during delivery, accounts for exact predecessor IDs in the
semantic-byte budget, exchanges all retained evidence rather than only active
state, and compares evidence-set convergence in addition to active and visible
digests.

A release-harness audit found another ownership defect: the very large
sync-domain integration selftest owns process, SQLite, filesystem, socket,
daemon, and temporary-path fixtures but was allowed to overlap unrelated CTest
work. It stalled in an eight-way registry despite passing quickly alone.
Declaring that test `RUN_SERIAL` makes fixture ownership explicit. The same
166-test registry then passes in one 29.19-second parallel invocation without
reducing assertions, timeouts, or corpora.

## What remains severely missing

The new graph is still an unauthenticated in-memory oracle. SHA-256 commits
bytes but does not prove that an actor was authorized. A hostile peer can forge
a same-dot branch and cause honest evidence and descendants to be quarantined,
so the current fork rule is an obvious denial-of-service surface outside the
honest-authority model.

The production manifest, SQLite schema, outbox, peer wire, payload store, and
filesystem publisher do not yet carry this envelope. There is no single
transaction that reserves a dot, freezes and authenticates bytes, inserts
parent edges, replaces heads, and publishes retry intent. There is no real
head/dependency protocol, no authenticated two-process convergence test, and no
payload/chunk commitment connected to final filesystem publication.

Full reprojection on every admission, full-evidence anti-entropy, full durable
export, and visible-state history scans are reference-oracle choices. They are
valuable as deterministic truth but superlinear or amplification-prone as a
daemon architecture. Production needs an incremental affected-subgraph index,
peer/storage quotas, stable frontier semantics, and compaction only after those
semantics are differentially proved against this oracle.

The name still overclaims privacy. There is no demonstrated anonymity,
unlinkable discovery, metadata-minimizing membership, relay threat model,
traffic-analysis defense, cover traffic, forward secrecy, post-compromise
security, or secure erasure. Those claims remain false until a concrete
adversary and observable-metadata model exists.

## Verification

- Active patch: 13 files, 3,181 insertions, 1,062 deletions.
- Active projection: 325 files, 18,332,739 bytes, SHA-256
  `07eaad264ad625ac87ea15c93a4e62e0cf460d7fefbe4c9b136bcad58a8dddc2`.
- Source replay from sealed rev0865: 325/325 active files, zero mismatches.
- GCC 14.2 Debug: all targets closed with zero remaining Ninja work.
- Full registry: 166/166 in one invocation; registered audits: 49/49.
- Focused runtime: 2,050 assertions, including 342 allocation failpoints.
- Clang 17 `-Werror`: 3/3 focused executables.
- GCC 14 ASan+UBSan: 3/3 focused executables with leak detection and
  halt-on-error; 10/10 compile and 3/3 link commands carry both sanitizers.
- Clang static analyzer: four changed production translation units, zero
  diagnostics.
- Parent: 26/26 ZIP and 22/22 directory checks.

## Conclusion

Rev0866 changes the causal oracle from arrival-authorized dotted metadata into
an exact evidence graph with deterministic projection and rollback-tested
mutation. That is a meaningful semantic foundation, but the highest-value next
move is vertical: authenticate and persist one such operation in one SQLite
transaction, exchange it over one real peer channel, restore it after crash,
and publish its payload under the same identity while continuously comparing
with this oracle.
