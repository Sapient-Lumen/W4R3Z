# Rev0865 audit

## Boundary question

Can AnonSync distinguish a unique replicated update from causal history, admit
that update atomically, project concurrent values deterministically without
losing files, and exercise convergence under network/crash schedules without
silently exceeding resource budgets?

## Primary finding: deterministic conflict selection hid identity corruption

The manifest planner treated equal lineage vectors with different version
bytes as an ordinary conflict. Equal vectors claim the same causal frontier;
different bytes beneath that frontier indicate counter reuse, missing event
identity, corruption, shared-writer misuse, or equivocation. Selecting a winner
makes the result deterministic but does not make the history valid.

Rev0865 rejects that state with a repair-required validation failure. The path
is tested in both local/remote orientations and after an earlier candidate plan
entry has already been built.

## Failure-atomic planner publication

The planner previously populated its caller-visible output while iterating.
Rev0865 clears the output, builds a private candidate, validates its final
shape, and publishes only by final move assignment. A late equal-lineage failure
must leave folder/device/digest fields and entry vectors empty.

## Executable dotted-operation oracle

`SyncReplicaModel` now provides a pure C++ semantic reference:

- one immutable operation has folder/path/value, a unique actor-epoch dot, and
  sorted causal context;
- canonical length-framed SHA-256 binds every semantic field;
- local mint is sequential inside one `(device_id, epoch)` authority;
- exact duplicates are idempotent;
- same-dot/different-operation admission fails before mutation;
- remote minting in the local actor namespace and future-local dependencies are
  rejected;
- pairwise cycles and nontransitive observed-predecessor contexts are rejected;
- per-path maximal operations form a multi-value visible set;
- the existing deterministic conflict policy selects a primary while all
  visible nonprimary files remain preservation candidates; and
- durable restore revalidates sorted history, local counter continuity, dot
  uniqueness, and local-future references.

Operation-set and visible-state digests omit local replica identity, allowing
independently named replicas with the same accepted update set to compare exact
semantic projections.

## Network and crash model

`SyncReplicaNetworkSimulator` owns deterministic queued messages, duplicate,
drop, oldest/newest delivery, directional partitions, crash/restart, point
anti-entropy, and full-mesh anti-entropy. Accepted model state is represented as
atomically durable in this oracle; that is a specification cutpoint, not a claim
about current SQLite production integration.

A four-node deterministic scenario executes 720 mixed steps, creates 88
operations, injects partitions, message loss, duplication, reverse delivery,
crashes, and restarts, then heals and runs repeated full-mesh exchange until all
operation-set and visible-state digests are equal.

## Atomicity and resource defects corrected during implementation

1. **Local commit before enqueue:** the first implementation could mutate local
   history and then throw while publishing peer messages. Candidate live state,
   durable state, complete broadcast, message IDs, and charges are now staged
   before a no-throw commit. Queue failure consumes no local dot.
2. **Count-only budget:** queued operations own variable-size contexts, so count
   did not bound memory. A second stable semantic-byte budget now tracks fixed
   scalar widths and every owned string byte.
3. **Post-amplification budget check:** the first byte-bound version built the
   full anti-entropy batch before denial. Cardinality/identifier preflight and
   exact byte accumulation now happen before mesh-sized reserve/copy, followed
   by a defensive publication recheck.
4. **Partial queue insertion:** atomic batch publication erases every inserted
   prefix if map insertion throws and leaves the next message ID unchanged.
5. **Partial bidirectional partition:** the first direction is rolled back if
   allocating the reverse direction fails.
6. **Stale audit contract:** the structural conflict audit expected the old
   equal-lineage conflict behavior. It now requires fail-closed identity
   handling and private candidate publication.

## Scope boundary

The model proves convergence only for coherent operations that eventually reach
the same accepted set. It does not establish Byzantine convergence. Opposite
same-dot forks admitted first at different replicas can still produce different
accepted sets. Missing predecessors are tolerated to model reordering, which
means forged histories can be arrival-order sensitive. Operation IDs are
commitments, not signatures.

There is no production SQLite transaction binding, authenticated remote
transport, key lifecycle, membership protocol, payload/chunk materialization,
Merkle anti-entropy, compaction, causal stability, tombstone garbage collection,
confidentiality, anonymity, or metadata protection. The oracle intentionally
uses simple full-history storage and potentially quadratic scans.

## Strategic implication

The next work should not be another independent local authority leaf. It should
bind this update identity through a full vertical slice: canonical
authenticated operation envelope, transactional SQLite mint/head/outbox state,
deterministic evidence validation/quarantine, dependency-oriented
anti-entropy, exact payload publication, and a real two-process transport tested
against this oracle.

## Mechanical evidence

- GCC 14.2 Debug all-target graph: passed;
- uninterrupted registry: 164/164;
- registered structural audits: 49/49;
- final dependency closure: zero compile/link work;
- focused GCC: 79 model/network checks, 42 manifest checks, source audit 33/33;
- Clang 17 `-Werror`: focused targets and integrated core built; 2/2 focused
  executables passed;
- GCC ASan+UBSan: 2/2 focused executables passed with leak detection and
  halt-on-error; flags proved on 5/5 compile and 2/2 link commands;
- Clang static analyzer: three focused translation units, no diagnostics;
- source patch replay: 319/319 active files, 11 changed, zero mismatch;
- parent verification: 26/26 ZIP and 22/22 directory.
