# AnonSync rev0852 audit

## Audit target

Rev0852 audits the public type-and-lifetime boundary feeding SQLite's retained
authorizer callback. The reviewed transition is:

1. receive an exact `std::shared_ptr<T>` and a compile-time callback value;
2. reject unsupported context or callback forms before runtime erasure;
3. prove that the callback is invocable with the exact `T&` and SQLite argument
   shape and that its result is exactly `int`;
4. preserve the original stored pointer, ownership group, cv-qualification, and
   custom deleter in one process-bound typed capsule;
5. erase only the capsule interface presented to non-templated connection code;
6. install the stable C bridge and exact-generation callback lifetime claim;
7. invoke only through the capsule, with exceptions translated to fail-closed
   denial at the C boundary;
8. revoke SQLite's callback before retiring the capsule; and
9. leave SQLite's connection mutex before releasing application ownership.

## Heart of the finding

Rev0851 corrected a real lifetime defect by replacing borrowed non-null `void*`
policy state with shared ownership. It still exposed the C callback and
`std::shared_ptr<void>` as two independent public arguments. Those values could
be individually valid while disagreeing about the object type. The connection
could therefore keep the bytes alive and still authorize a callback to
interpret them as an unrelated object, creating undefined behavior inside an
authorization decision.

This is an important mission-level distinction: **lifetime authority does not
imply interpretation authority**. A boundary is not sealed while callers can
separately choose the referent and the cast that gives it meaning.

## Findings corrected

### Critical: callback/context type agreement was conventional

The context-bearing constructor has been removed. Non-null state now enters via
`make_sync_sqlite_owned_authorizer_policy<Policy>(std::shared_ptr<T>)`. C++20
constraints prove the exact invocation relationship before the callback and
context cross the type-erasure boundary. The runtime representation contains
one capsule object rather than a function pointer plus an erased owner.

### High: generic invocation admitted more authority than the contract intended

A first constrained draft used `std::invoke` as the only admissibility test.
That would also accept member pointers and arbitrary structural callback objects.
The factory now separately admits only non-null free/static function pointers
or empty structural class values. Member pointers, null function pointers, and
stateful compile-time adapters are rejected even when `std::invoke` could call
them.

### High: erasing to `shared_ptr<void>` could alter supported ownership shapes

The final capsule stores the exact `std::shared_ptr<T>`. It therefore supports
const contexts and preserves aliasing stored pointers, the original ownership
control block, and custom deleter behavior. Tests exercise a shared owner whose
stored pointer names a subobject and confirm both exact pointer identity and
one-time deletion of the owning object.

### Medium: an integrated negative test stopped testing the raw ABI

After migration, one rejection test still passed a typed callback through the
legacy context-free API. That tested an accidental signature mismatch rather
than the intended rule that raw compatibility callbacks receive only null
context. The fixture now has a dedicated raw-ABI callback, preserving the actual
negative contract without weakening the typed factory.

### Medium: process-test topology inventories drifted

The child-local provenance case added a second reviewed inherited-process spawn
in the focused policy test. The first complete registry run passed all runtime
tests but failed two exact process inventories. The inventories were corrected
in the same source patch. Raw `fork()` remains centralized in exactly one
translation unit; the final inventory is 13 inherited-state consumer
translation units, 24 wrapper spawn sites, seven fresh-image campaigns, and 31
inherited/fresh-image process-test sites.

## Refactor assessment

The new edge is materially simpler to reason about:

- caller-visible type erasure is gone for context-bearing policies;
- the policy and exact owner cannot be mixed and matched after construction;
- source-first move validation and process-incarnation checks remain in one
  move-only capability;
- context-free compatibility remains allocation-free and always receives
  `nullptr`; and
- the existing composed authorizer audit was expanded rather than creating a
  second overlapping lexical audit.

This is not a generic callback registry. Busy, progress, authorizer, client-data,
and other C APIs have different replacement, synchronization, and teardown
semantics. A future connection-level orchestrator should compose their focused
owners while retaining those API-specific proofs.

## Validation result

- typed policy owner: **30/30**;
- raw authorizer owner: **20/20**;
- integrated connection authority: **153/153**;
- transaction exception composition: **37/37**;
- transaction allocator-fault campaign: **642/642**;
- process/fork authority: **44/44**;
- peer schema authority: **66/66**;
- focused runtime total in each GCC, Clang, and sanitizer lane: **992/992**;
- focused repeatability: **250/250**;
- focused structural audits: **362/362**;
- complete registered gate: **148/148 in one uninterrupted invocation**,
  including **43/43** registered audits;
- exact source-patch replay: **276/276** active files; and
- final all-target dependency closure: zero compile or link work.

## What remains unproved

The factory proves a C++ invocation shape and exact result type. It does not
prove that a policy is semantically correct, deterministic, pure, race-free, or
non-throwing. Shared ownership does not synchronize mutable policy state. A
child-created owner cannot prove that an arbitrary supplied shared-pointer
control block was itself created after `fork()`. SQLite exposes no authorizer
getter, so foreign raw replacement between nonce challenges remains constrained
by exact source inventory rather than continuous runtime observation.

General concurrent close/use safety, ThreadSanitizer, full-project sanitizers,
bundled SQLite instrumentation, Windows runtime behavior, and Release-mode
all-target behavior remain outside this revision. At the product level,
distributed convergence, hostile-input process isolation, and the privacy,
device, and key protocol remain the largest missing proofs.
