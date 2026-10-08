# AnonSync rev0846 deep audit

## Executive verdict

AnonSync's strongest implemented law remains:

> A transition may consume only authority frozen from the exact bytes, object,
> identity, incarnation, generation, lifetime, namespace, policy, resource
> budget, and durability facts that the transition will actually use.

Rev0846 adds a missing word to that law: **thread lifetime**. Rev0845 made local
JSONL directory and namespace proof failure sticky, but the owners contained
mutable revocation, descriptor, and lock state without an executable rule about
which thread could use, move, release, or destroy them. Sequential use from a
foreign thread could therefore reach state designed around one implicit owner;
concurrent use could become an ordinary C++ data race. SQLite already carried a
private monotonic thread generation for its recursive-mutex contracts, but that
capability was unavailable to the filesystem boundary.

The revision extracts one dependency-light, opaque thread-incarnation leaf and
binds the selected mutable owners to the exact process **and** exact C++ thread
lifetime that created them. Wrong-thread throwing operations reject before
protected state or kernel resources are touched. Wrong-thread `noexcept`
operations, moves, releases, and destruction fail stopped because silently
closing or transferring another thread's descriptor/lock capability is not a
recoverable condition.

This is a meaningful authority correction and useful cross-subsystem refactor.
It is not synchronization, shared ownership, ThreadSanitizer evidence,
distributed convergence, or anonymity.

## The missing authority dimension

`LocalJsonlReplayDirectoryAuthority` and `LocalJsonlReplayNamespace` are not
pure immutable values. They own descriptors, lock state, path attestations, and
sticky revocation bits. `LocalJsonlReplayOpenFile` additionally owns one exact
open descriptor and write/flush/close lifecycle. Rev0845 bound these owners to a
process incarnation but did not prevent a second thread from invoking them.

That omission had two distinct failure modes:

1. sequential cross-thread use violated the intended capability lifetime even
   when no simultaneous access occurred; and
2. simultaneous use, move, or destruction could race ordinary non-atomic C++
   state, making behavior undefined before any fail-closed policy could help.

Rev0846 freezes `SyncThreadIncarnation` at construction. Throwing entry points
prove the process first and the thread second, before inspecting revocation,
bytes, descriptors, or path state. Rejection on a foreign thread does not revoke
or consume the owner; the originating thread can continue using the unchanged
capability. `noexcept` operations cannot communicate an affinity error, so they
terminate through the existing process-capability fail-stop path without C++
unwinding or teardown hooks.

The ordering is deliberate. An inherited child must fail as a process-authority
violation rather than being misclassified as merely another thread. Inside the
same process, an exact-thread mismatch is reported to throwing callers without
mutating the protected owner.

## Why `std::thread::id` was not enough

The C++ specification permits a thread ID value to be reused after the thread
terminates. A stored native or standard-library ID is therefore an observation,
not proof of one exact lifetime. A later thread can legitimately receive the
same observable identifier.

`SyncThreadIncarnation` instead receives a monotonically allocated, nonzero
process-local generation. The public type:

- has no integer constructor or integer conversion;
- is non-trivially-copyable, blocking ordinary `std::bit_cast` manufacture;
- remains standard-layout and one machine word for cheap carriage;
- supports only validity and exact typed equality; and
- is documented as process-local evidence, not a row, wire, or persistence
  format.

This is domain separation against accidental evidence confusion, not a security
boundary against hostile code already executing in the same address space.
Owners continue to pair the thread proof with `SyncProcessIncarnation`; the
thread number alone is not promoted to cross-process identity.

## The first extraction was still fork-unsafe

The audit found and corrected two defects in the initial refactor before the
revision was sealed.

First, the generation allocator was a function-local static. If a
multithreaded process forked while another thread performed first-use dynamic
initialization, the child could inherit an initialization guard owned by a
thread that no longer existed. The final allocator is namespace-scope,
constant-initialized, and `static_assert`-required to use an always-lock-free
64-bit atomic. Allocation is a bounded compare/exchange loop with explicit
zero/wrap fail-stop.

Second, placing the opaque public token itself in `constinit thread_local`
storage did not eliminate runtime machinery. Because the token intentionally
has a non-trivial destructor, GCC emitted a TLS guard, a TLS destructor, and
`__cxa_thread_atexit`; the compiler was entitled to do so. A post-fork child
refresh could then enter copied runtime registration state before replacing the
inherited token.

The final implementation keeps only two raw, trivially copyable and trivially
destructible words in namespace-scope TLS: the process-incarnation
representation and thread-generation representation. It constructs the opaque
public value only on return. Object inspection of the final GCC 14 and Clang 17
objects finds no TLS guard, TLS destructor, or `__cxa_thread_atexit` reference.
The source audits pin the raw/trivial design; the object logs pin the emitted
result for these toolchains.

Fork copies the TLS bytes, but the process-incarnation word changes in an
ordinary tracked child. The first child lookup therefore allocates a new thread
generation instead of accepting the parent's exact thread proof.

## SQLite refactor and compatibility

SQLite recursive-mutex ownership already required a same-thread capability.
Rev0846 removes its private allocator and aliases
`SyncSqliteThreadIncarnation` to the generic type. Existing SQLite wrapper names
and error text remain stable while delegating to the new leaf, so connection,
transaction, write-gate, and retained-mutex owners acquire domain separation
without a broad API rewrite.

Making the token opaque intentionally caused stale integer initialization and
comparison sites to fail compilation. Those failures identified every place
that had treated capability evidence as an ordinary number; the corrected code
uses typed default construction, `.valid()`, and exact token equality.

The 70-obligation SQLite mutex-capability audit now checks both the retained
SQLite sentinel invariants and the generic thread leaf, including raw TLS,
lock-free allocation, no function-local static, and no public representation
bridge. The focused SQLite connection authority corpus remains 133/133 under
GCC, Clang `-Werror`, and the sanitizer lane.

## Audit of the inherited-process audits

A separate audit defect was more severe than a stale expected count. The raw
fork and inherited-process tools trusted handpicked consumer lists, so a target
could call the shared child-process owner yet remain invisible to the supposed
complete inventory. Two descriptor-authority child probes had exactly that
shape.

Rev0846 establishes one exact CMake inventory of all 11 inherited-state
consumer targets. The source tools independently discover all wrapper call
sites and compare discovered translation units and linked targets against that
inventory in both directions. The result is:

- 11 inherited consumer translation units;
- 20 shared-wrapper spawn sites;
- one raw `fork()` call, centralized in `tests/inherited_test_process.cpp`;
- zero production raw-fork calls; and
- seven fresh-image campaigns that use the separate exec owner.

The raw-fork audit passes 11/11, inherited-process audit 15/15, and self-exec
audit 36/36. The generic thread test and filesystem death probes now inherit the
shared owner's bounded deadline, process-group cleanup, and exact-reap rules
instead of adding ad hoc process control.

This is an improvement over a longer static list, but the CMake list is still
manually maintained. The independent discovery makes staleness fail closed;
a future generated target-property mechanism could make the relationship less
verbose.

## Direct executable evidence

The final focused boundary reports **319 checks** across six executables:

- generic thread incarnation: 14;
- local JSONL directory authority: 26;
- local JSONL composed namespace: 64;
- local JSONL backend namespace integration: 30;
- local JSONL crash state machine: 52; and
- SQLite connection authority: 133.

The thread corpus proves stable same-lifetime identity, empty-proof rejection,
foreign-thread rejection without consumption, 32 concurrent unique tokens, 64
sequential joined-thread generations without resurrection, post-fork refresh,
and fail-stop for a foreign-thread `noexcept` violation. The registered thread
test also passes 100 consecutive executions.

Directory and namespace tests prove foreign-thread rejection occurs before
observation or mutation, preserves sticky-revocation and owner state, preserves
exact bytes in an open temporary file, and fail-stops foreign-thread release.
Existing process-inheritance and crash-state tests remain green.

## Complete validation interpretation

The registered inventory contains **143 tests**. Exact, non-overlapping ranges
1–25, 26–34, 35–50, 51–57, 58–63, 64–75, 76–100, 101–125, and 126–143 all
passed. Tests 35–75 are all **41 registered source/architecture audits** and all
passed.

The final source also passed:

- a GCC 14.2 Debug all-target build;
- a final Ninja dependency closure with no compile or link work;
- Clang 17 `-Werror` focused build and 319/319 runtime checks; and
- GCC 14 ASan+UBSan with leak detection and 319/319 runtime checks.

The sanitizer lane is focused and does not include ThreadSanitizer. The
revision does not claim one uninterrupted 143-test invocation; exact completed
ranges are the release accounting unit.

## What thread affinity does not prove

The name “thread incarnation” must not be read as a lock or race detector.

- Concurrent access to one owner can still be a C++ data race before or while a
  token is read.
- Concurrent move, release, or destruction remains an object-lifetime error.
- The owner must not be handed to another thread for destruction; such misuse
  intentionally fails stopped.
- An opaque one-word token prevents supported numeric construction, not hostile
  memory forgery by code already inside the process.
- The allocator's always-lock-free 64-bit atomic requirement is a deliberate
  portability constraint.
- Object-symbol evidence covers GCC 14 and Clang 17 on the recorded ELF/x86-64
  toolchains, not every compiler ABI.
- Ordinary tracked `fork()` refresh is tested, but `_Fork()` or process creation
  that bypasses the registered process-incarnation hook remains outside the
  proof.
- POSIX still restricts arbitrary child-side library activity after a
  multithreaded fork. The capability refresh is narrow evidence, not permission
  to resume the application in the child.

A design that needs concurrent callers should add an explicit serialized owner
or broker rather than treating the affinity proof as implicit synchronization.

## Waste and change amplification

The revision adds 200 production lines for the generic thread leaf, 221 direct
test lines, and a 401-line dedicated source audit. That ratio is defensible for
a sensitive primitive, but it also illustrates the cube's rising proof cost.
There are now 42 `audit_*.py` tools totaling 18,307 lines.

The largest concentration points remain:

- `src/sync_domain.cpp`: 15,287 lines;
- `src/sync_domain_selftests.cpp`: 9,348 lines;
- `src/sqlite_replay_ledger.cpp`: 4,527 lines;
- `src/reporting_selftests.cpp`: 4,992 lines;
- `CMakeLists.txt`: 2,527 lines;
- `src/persistence/local_jsonl_replay_namespace.cpp`: 1,146 lines; and
- `REVISION_EVIDENCE`: about 25.7 MB before final indexing and recursive
  packaging.

The audit repair also demonstrates why hand-maintained “complete” inventories
are dangerous: a green check can be incomplete rather than merely stale.
Independent discovery plus exact set equality is better; generated build data
or semantic test oracles would be better still.

Historical evidence remains several times larger than the active first-party
implementation. Content-addressed evidence with a compact lineage index would
preserve forensic continuity while reducing hashing, manifest, verification,
transfer, and review cost.

## Product-level mission still missing

Thread-affine local authority makes the integrity kernel more coherent, but it
does not advance the product-defining distributed semantics by itself. AnonSync
still needs:

- an executable operation algebra for update, delete, recreation, rename,
  duplicate delivery, causal gaps, concurrency, schema epochs, and key epochs;
- a deterministic reference model compared with C++ under reorder, retry,
  partition, crash, and restart histories;
- one cross-resource crash oracle spanning SQLite, WAL/checkpoints, files,
  directories, manifests, receipts, and external effects;
- hostile-input interpretation in disposable, resource-limited workers; and
- a device/key/privacy protocol for membership, rotation, revocation, state
  loss, forward secrecy, post-compromise recovery, metadata leakage, backup
  custody, rollback resistance, and realistic erasure limits.

Authentication and thread ownership do not establish anonymity. Local
recoverability and exact authority do not establish distributed convergence.
Those distinctions remain explicit in the release gate.

## Speculative destination

The local persistence plane increasingly resembles a set of narrow capabilities
that want one serialized executor. A small broker or event loop could own the
sealed directory and database handles, accept bounded typed commands, and emit
recovery receipts. That would make single-thread execution structural rather
than repeated per-object convention, while also creating a natural sandbox and
resource-control boundary.

At the distributed layer, a coherent architecture still points toward an
encrypted content-addressed data plane plus a compact authenticated control
plane carrying causal operations, object/key epochs, revocation facts,
authority capsules, and explicit convergence semantics. The local capability
kernel can support that architecture, but it cannot substitute for its
operation model or privacy protocol.
