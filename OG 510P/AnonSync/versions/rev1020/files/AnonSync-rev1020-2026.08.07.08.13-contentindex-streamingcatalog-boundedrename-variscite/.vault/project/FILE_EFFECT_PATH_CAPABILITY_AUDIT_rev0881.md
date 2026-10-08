# File-Effect Path Capability Audit — rev0881

## Executive finding

AnonSync’s newest causal/effect path is trying to make one promise precise:
**exact authorized history may name an intended file, but only a live,
receiver-owned effect capability may decide whether that identity can be
materialized on a particular filesystem.** Those are related decisions, not the
same decision.

Rev0880 violated that separation at one narrow but load-bearing frontier. A
canonical operation could contain a path component that was valid under the
portable model and wire budget yet longer than the retained destination
filesystem could name. The receiver would first persist the payload in its
file-effect SQLite owner, then admit causal evidence, and only later discover
`ENAMETOOLONG` while attempting namespace publication. The result was an
irrecoverable-looking retry loop with retained bytes and causal/effect state for
an effect the receiver could already have proven impossible before either form
of authority was acquired.

Rev0881 adds a receiver-local component-byte preflight before durable effect
admission, a typed `EffectPathBlocked` receipt that carries neither effect nor
causal authority, and sender-side exact retry release governed by local owned
clock policy. It also binds retained directory authority to the calling
thread’s live Linux mount namespace and consolidates two previously divergent
Linux boot-ID readers into one strict leaf owner.

The most important negative design decision is equally deliberate: rev0881
does **not** persist boot UUID or mount ID as mandatory durable root identity.
Doing so without a rebind ceremony would turn an ordinary reboot into a
permanent effect-database lockout. Runtime-ephemeral observations are useful
for live authority and clock fencing; they are not automatically durable
storage identity.

This audit is an implementation and architecture review, not a claim of a
complete product path. The newer causal, delivery, and retained-root effect
owners remain a correctness island that is not yet the shipped
`anonsync_core` executable path.

## The heart of the mission

The heart of AnonSync remains authority accounting:

> Exact canonical evidence owns identity and causality. A receiver-owned live
> capability owns local materialization. A sender-owned clock owns retry.
> Summaries, paths, transport responses, kernel version numbers, and ephemeral
> namespace identifiers are observations, never replacement authority.

For file delivery this becomes a chain of independently reviewable questions:

1. Is the operation canonical and exactly bound to its payload digest and size?
2. Is this exact dispatch attempt authenticated to the intended peer and
   channel binding?
3. Can the receiver retain the payload under its bounded effect budget?
4. Can the receiver’s retained destination capability represent the canonical
   path at all?
5. Can causal evidence be admitted at an exact cutpoint?
6. Is the operation the one unambiguous active primary at that cutpoint?
7. Can the immutable file be published and durably re-proved under the retained
   root?
8. Does the terminal receipt bind the exact request, effect, evidence cutpoint,
   and authenticated channel?
9. Does only that terminal receipt retire sender outbox intent?

Rev0881 corrects question 4. Previously it was deferred until question 7, after
questions 3 and 5 could already mutate durable state.

## Canonical identity versus local effect capability

A canonical AnonSync path is a portable operation identifier. Its grammar and
wire/model budget must be deterministic across replicas. A receiver-local
filesystem ceiling is different: it depends on the destination capability and
may differ across operating systems, mounts, filesystems, or administrative
configuration.

POSIX exposes `{NAME_MAX}` as the component limit and allows applications to
query path-associated limits with `pathconf()` or `fpathconf()`. Operations may
fail with `ENAMETOOLONG` when a component exceeds `{NAME_MAX}`. Relevant
standards and manual references include:

- The Open Group `fpathconf()` interface and configurable path limits:
  https://pubs.opengroup.org/onlinepubs/009696799/functions/fpathconf.html
- POSIX Issue 8 conformance language for components longer than `{NAME_MAX}`:
  https://pubs.opengroup.org/onlinepubs/9799919799/basedefs/V1_chap02.html
- POSIX Issue 8 `open()` error semantics:
  https://pubs.opengroup.org/onlinepubs/9799919799/functions/open.html
- Linux `pathconf(3)` / `fpathconf(3)` behavior, including an indeterminate
  limit returning `-1` without changing `errno`:
  https://man7.org/linux/man-pages/man3/pathconf.3.html

Rev0881 therefore keeps two validators:

- `validate_sync_relative_path()` remains canonical identity validation.
- `validate_sync_relative_path_component_byte_limit()` first reuses canonical
  validation and then applies one receiver-local encoded-byte ceiling.

The local function counts bytes between `/` separators. It does not count
Unicode scalar values, grapheme clusters, or display columns. This matches the
byte-oriented effect boundary used by the POSIX filesystem APIs in this code
path. A multibyte UTF-8 component can therefore exceed a byte ceiling with
fewer visible characters than an ASCII component.

The function is deliberately not folded into canonical operation validation.
Doing that would make the operation’s global validity depend on whichever
receiver happened to validate it. Two replicas with different destination
filesystems could then disagree about operation identity, which would violate
the project’s deterministic-history mission.

## The corrected receiver frontier

`SyncReplicaFileEffectSqliteOwner::stage_or_throw()` now performs the following
order:

1. Re-prove retained root authority.
2. Begin an immediate SQLite transaction and load/attest exact effect state.
3. Validate canonical operation structure and folder/kind ownership.
4. Validate payload size and SHA-256 against the operation.
5. Canonically encode the exact operation.
6. Observe the retained root’s frozen component ceiling.
7. Reject a provably unrepresentable path with
   `DestinationPathBlocked` after another root proof and an unchanged
   transaction commit.
8. Only then inspect duplicate identity, capacity, generation, and insertion.

The local ceiling is the conservative minimum of the retained root’s
`statvfs().f_namemax` observation and a positive `_PC_NAME_MAX` value from
`fpathconf()`. If neither produces a positive limit, rev0881 does not invent a
number and leaves the later syscall path authoritative. This is a bounded
improvement, not a universal proof that every possible filesystem will behave
identically to the root observation.

The blocked result does not insert an effect row, retain payload bytes,
increment generation, or touch the destination namespace. The focused runtime
test records the complete effect snapshot before the attempt and requires exact
snapshot equality afterward. It also proves that a component exactly at the
observed byte ceiling can acquire normal staged effect authority.

### Why the unchanged transaction is intentional

The owner still opens and attests an immediate transaction before returning the
blocked result. That is not needed to write data; it is needed to prove what the
receipt means. The receipt says that this request was evaluated against an
exact receiver effect cutpoint and did not change it. Skipping the transaction
would make the cutpoint an unaudited loose observation.

This remains a local SQLite serialization point, not a transaction across the
effect database, causal database, and filesystem. The project should continue
to name those independent frontiers rather than call them atomic.

## Typed pre-effect receipt

The wire protocol adds numeric disposition `EffectPathBlocked = 9` without
renumbering any prior disposition and explicitly advances the outer file-delivery
protocol and structural digest domains to version 2. Older readers therefore
reject the frame version before they can reinterpret or partially process the new
outcome. Treating the extension as version 1 would have been a compatibility lie.

`EffectCapacityBlocked` and `EffectPathBlocked` share a new predicate:
`sync_replica_file_delivery_receipt_precedes_effect_authority()`.
A receipt in this class:

- binds the folder, sender, receiver, operation, exact claim ID, attempt count,
  request digest, authenticated channel binding, receiver effect generation,
  and receiver effect cutpoint digest;
- carries no inner causal evidence receipt; and
- carries no effect ID.

Protocol validation rejects either kind of residue. The receiver is not allowed
to claim a staged effect or admitted evidence while simultaneously reporting a
pre-effect denial.

The delivery service maps `DestinationPathBlocked` to `EffectPathBlocked`
before calling the inner evidence delivery service. Runtime coverage requires
that repeated delivery of the same exact request reproduces the same typed,
no-mutation receipt and leaves both receiver databases unchanged.

This is an important semantic distinction from `DestinationConflict`.
A conflict says the receiver acquired effect/evidence authority but found an
existing incompatible namespace entry. A path-policy denial says no local
effect identity was ever acquired because the requested name cannot be
represented under the retained destination capability.

## Sender retry authority

Rev0880’s sender-side nonterminal logic had become stale relative to the newer
outbox owner. It inspected a snapshot to classify stale/missing/expired claims
but otherwise left a current nonterminal attempt occupying its original lease.
That was safe from false settlement but wasteful: a receiver could answer
immediately, yet the sender would wait until lease expiry before retrying.

Rev0881 routes every validated nonterminal file receipt through
`release_outbox_for_retry_or_throw()`. The exact destination, operation, and
claim ID are required. The owner’s clock computes the retry cutpoint; the
receiver supplies classification only and never supplies a deadline.

The policy is explicit, strictly positive, and bounded by
`kSyncReplicaOutboxMaxRetryDelaySeconds`. Zero is rejected so a configuration
mistake cannot turn a durable nonterminal receipt into an immediate claim/release
spin. Path-policy denial defaults to a long local backoff because repeated
immediate delivery cannot change a fixed local filename ceiling. This is still
not a complete retry system: there is no jitter, dead-letter state, operator
replay ceremony, or destination-capability epoch.

The same exact release is now used when failure occurs after a claim has been
minted but before a frame escapes:

- payload callback throws;
- payload callback moves or invalidates the live channel authority;
- post-callback channel reproof fails;
- request validation or encoding fails; or
- request digest construction fails.

The original exception is rethrown only after the exact claim is durably
released. If release cannot prove the same live attempt—for example because the
callback advanced the owned clock through lease expiry—the service combines the
original failure with the release contradiction and fails closed. It does not
fabricate retry provenance.

This refactor corrects a real efficiency defect while preserving the central
rule: only `Published` or `AlreadyPublished` may settle the sender intent.

## Live mount-namespace authority

Rev0880 fenced descendant mount crossing with `openat2(RESOLVE_NO_XDEV)` when
available and re-proved mount identity with `statx()` when available. That
still left a context gap: a thread can call `unshare()` or `setns()` and change
its mount namespace while retaining an open descriptor captured in the old
namespace.

Linux documents `/proc/pid/ns/*` entries as namespace handles. Keeping the file
descriptor open keeps the namespace alive, and processes in the same namespace
have matching `st_dev` and `st_ino` for the corresponding namespace file:
https://man7.org/linux/man-pages/man7/namespaces.7.html

Rev0881 introduces `SyncPosixMountNamespaceAuthority`:

- on Linux it opens and retains `/proc/thread-self/ns/mnt`;
- freezes the handle’s `st_dev`/`st_ino` identity;
- on every proof, re-stats the retained handle and compares it with a freshly
  opened current-thread handle;
- treats inability to observe the Linux handle as a fatal failure rather than a
  kernel-version downgrade; and
- permanently revokes itself after any failed proof.

`SyncDirectoryAuthority::open_or_throw()` captures this authority before any
pathname traversal. `verify_or_throw()` re-proves the mount namespace before
retained-descriptor and visible-path proofs. The composed directory authority
also remains sticky-revoked after failure.

The runtime test forks a child and attempts
`unshare(CLONE_NEWUSER | CLONE_NEWNS)`. Where the cloudtainer permits that
witness, both the primitive namespace authority and the retained directory
authority detect the change and remain revoked. Where the host denies the
operation, the test records an explicit skip instead of claiming the negative
path executed.

This does not protect against a privileged adversary that can interfere with
the process, procfs, or kernel. It also does not make the ephemeral namespace
inode a restart-stable identifier.

## Reboot-ephemeral evidence is not durable root identity

A draft during this revision attempted to persist a boot UUID and mount ID in
the file-effect metadata row and require exact equality on every reopen. That
looked like stronger root identity, but it was structurally wrong without a
rebind protocol.

Linux documents `boot_id` as a UUID generated for the running kernel and
unchanging during that kernel epoch:
https://docs.kernel.org/admin-guide/sysctl/kernel.html

Linux documents `STATX_MNT_ID_UNIQUE` as guaranteed not to be reused **while
the system is running**, not across reboots:
https://man7.org/linux/man-pages/man2/statx.2.html

Persisting either as mandatory permanent identity would therefore reject an
otherwise exact database after a normal reboot. The database would have no
authorized way to distinguish “same retained root after reboot” from “wrong
root,” and no operator ceremony to resolve the state. That is fail-closed in a
superficial sense but operationally destructive: every reboot becomes a
lockout.

The draft schema change was removed. The effect schema remains version 2, and
boot UUID/mount number are not persisted as mandatory root identity.

A future restart-rebind design needs explicit evidence and policy, potentially:

1. durable root attestation and database identity from the prior epoch;
2. a fresh retained-root capability under the new kernel epoch;
3. exact re-attestation of all published effects and bounded staged payloads;
4. an operator or device-key-authorized rebind record;
5. rollback protection for the rebind sequence; and
6. a recovery path when the old root is absent, replaced, or only partially
   available.

Until that exists, live namespace and mount observations should remain live
proof inputs rather than permanent durable identity.

## Shared system-epoch observation refactor

The process identity owner and Linux outbox clock each carried a separate
reader/parser for `/proc/sys/kernel/random/boot_id`. Their policies had already
diverged: one trimmed repeated CR/LF terminators, while the other bounded bytes
but did not share exactly the same framing semantics. That is a classic
assurance waste: two security-relevant readers for the same kernel evidence,
each requiring separate review and capable of silently accepting different
inputs.

Rev0881 introduces `sync_system_epoch_identity.{hpp,cpp}` as a narrow leaf:

- `open()` uses `O_NOFOLLOW`, `O_CLOEXEC`, and a fixed observation cap;
- `ENOENT`, `EACCES`, and `EPERM` become typed unavailable observations;
- unexpected open failures remain fatal;
- the source must be a regular file;
- reads are bounded and `EINTR`-aware;
- exactly one canonical lowercase UUID is accepted, optionally followed by one
  LF or one CRLF; and
- whitespace, repeated terminators, NUL bytes, uppercase, or malformed UUIDs
  are rejected.

Both the process identity code and outbox clock now reuse this owner. The clock
still samples boot identity before and after its time-namespace/clock readings
to reject a cross-epoch sample.

The name “system epoch” is intentionally broader than a durable identity claim.
The current implementation exposes a Linux boot observation only. It does not
bind filesystem roots, authorize effects, or promise cross-platform epoch
parity.

### Boot-ID unavailability still escapes durable clock evidence

The shared observer preserves `ENOENT`, `EACCES`, and `EPERM` as typed source
observations. The Linux outbox-clock adapter cannot yet carry those types into
its durable evidence, however. Its current observation codec requires exactly
one canonical 36-byte boot UUID, so the adapter throws before the SQLite owner
can publish a quarantine record. This is weaker than the time-namespace path,
where unavailable identity becomes explicit synchronization-unknown evidence
owned by the database.

A future clock format must represent boot-source kind separately from boot-ID
bytes and define how unavailable boot identity affects synchronization,
recovery, and cross-restart comparison. Merely substituting an empty UUID or a
synthetic constant would collapse distinct evidence and could authorize leases
across an unobserved reboot. Rev0881 consolidates the reader and exposes the
gap; it does not claim to close it.

## Audit/refactor assessment

### Corrected waste

The revision removes two duplicated boot-ID readers and one stale
snapshot-only nonterminal classification path. The replacement code is smaller
in semantic ownership even though the total file count increases:

- one strict boot observation leaf;
- one live mount-namespace authority;
- one receiver-local component validator;
- one shared pre-effect receipt classifier; and
- one exact retry-release transition for both receiver nonterminal responses
  and local pre-dispatch failure.

The independent sanitizer lane exposed another build-graph duplication cost:
`anonsync_system_epoch_identity_test` was present in the manual sanitizer
compile-target inventory but absent from the separate link-target inventory.
The leaf library was instrumented, so the standalone test failed at link with
missing ASan/UBSan runtime symbols. Rev0881 adds the missing link policy and a
source-audit check that requires the test in both inventories. This is not a
runtime memory defect; it is evidence that duplicated declarative target lists
are a correctness surface. A future CMake refactor should derive sanitizer link
coverage from executable targets that receive sanitizer compilation rather
than maintain parallel hand-edited lists.

### Corrected severe path

Before rev0881, an impossible destination component could consume:

- effect database row capacity;
- retained payload-byte capacity;
- effect generation;
- causal receiver evidence; and
- sender lease time across repeated failures.

The receiver could prove the name was too long from its retained root
attestation before any of those mutations. Deferring that proof was both wrong
and wasteful.

### Rejected overreach

The discarded schema-v3 boot/mount binding is worth retaining in the design
record because it illustrates a recurring AnonSync hazard: more frozen fields
do not necessarily mean more authority. An observation with a shorter lifetime
than the state it guards needs an authorized transition ceremony, not merely a
new NOT NULL column.

## Legacy staged poison remains a repair concern

Rev0881 prevents new locally impossible operations from entering the effect
database through the revised owner. It does not yet provide an offline repair
or migration ceremony for a rev0878–rev0880 database that already contains a
staged row whose component exceeds the destination filesystem limit.

That legacy state can include retained payload bytes and may already have a
corresponding admitted causal operation. Returning `EffectPathBlocked` for a
new duplicate request prevents further mutation, but it does not reclaim the
old row or reconcile the causal/effect mismatch.

Automatic deletion would be unsafe without more design work. The row may be
part of an attested cutpoint, and removing it would need explicit repair
authority, evidence about whether any visible file was ever published, and a
policy for corresponding causal history. A future repair command should likely:

1. open both causal and effect databases under exclusive operator authority;
2. attest current root and causal/effect cutpoints;
3. classify each impossible staged row;
4. prove that no exact final file exists under the retained root;
5. write an append-only repair record naming old and new cutpoints;
6. decide whether payload bytes are exported, retained, or deleted; and
7. provide a deterministic receiver receipt policy for later duplicate
   deliveries.

Until that exists, packages should not claim rev0881 repairs already-poisoned
state. It prevents recurrence.

## Additional limitations and speculative next changes

### Per-directory limit variation

The preflight uses the retained root’s frozen limit. POSIX associates
`fpathconf()` with a specific descriptor/path, and unusual filesystems may vary
behavior by directory. Rev0880’s no-cross-mount policy reduces variation, but
rev0881 does not prove that every descendant directory has exactly the root’s
limit. Atomic publication remains authoritative and can still fail closed.

A stronger design could traverse the existing parent chain under the retained
root and query each descriptor. That would need to define behavior for missing
parents and preserve race-safe retained descriptors through publication. It
must not turn transient lookup failure into canonical path invalidity.

### Capability-negative caching

A one-hour retry delay is only a policy placeholder. A path that exceeds a
stable local component limit will not become representable merely because an
hour elapsed. Repeated retries waste channel, SQLite, and clock work.

A future receiver could issue an authenticated, durable **effect capability
epoch** containing a digest of relevant local policy (not raw filesystem
secrets), and the sender could suppress retries for the exact destination and
operation until that epoch changes or an operator overrides it. That receipt
must remain destination-local and must never alter canonical operation
identity. It would also need bounded expiry or revocation to avoid permanent
denial from stale or malicious capability reports.

### Repair versus renaming

Automatically shortening, hashing, escaping, or case-folding the destination
name would be a semantic error unless the transformed path itself is part of
canonical operation identity. A local hidden mapping could make two distinct
operations collide or make replicas publish different visible paths.

A separate policy-controlled projection layer could intentionally map canonical
paths into local storage names, but then the mapping table, collision rules,
case/normalization behavior, and reverse lookup become durable effect authority.
That is a new subsystem, not a safe fallback inside `stage_or_throw()`.

### Windows parity

The new component-byte policy is POSIX-only. Windows path component, reserved
name, normalization, alternate stream, device namespace, and long-path rules
are not equivalent to POSIX `{NAME_MAX}`. The project should add a typed Windows
local-path-capability owner rather than reusing this byte ceiling.

### Retry system completion

The exact release path is a sound primitive, but production policy still needs
jitter, attempt-age/count budgets, due-time indexes, wake scheduling,
dead-letter state, operator replay authority, and a clear distinction between
stable policy denial and transient capacity pressure.

### Post-callback claim authority is re-attested locally

The sender now finishes arbitrary payload code before acquiring a scope-bound
`SyncReplicaSqliteOutboxDispatchGuard`. The owner restores the complete
cutpoint under `BEGIN IMMEDIATE`, proves the original destination, operation,
claim ID, retained canonical operation, and owned-clock liveness, then allows
only a nondecreasing same-claim renewal. Missing, settled, released, replaced,
or expired callback results cannot escape as a frame. Bounded validation,
encoding, and digest construction run while competing SQLite writers are
excluded; guard destruction precedes exact retry release on failure.

This resolves the ambient-owner callback race identified by the first rev0881
audit pass. Runtime tests execute callback-owned release, settlement, exact
expiry, valid renewal, malformed payload, competing-writer, and TEMP-trigger
cases. The reusable full-cutpoint attestation and retry-release error matrix were
also refactored into single helpers rather than copied into a second authority
path. `OUTBOX_DISPATCH_GUARD_AUDIT_rev0881.md` records the detailed reasoning.

### Network first-byte dispatch remains a separate authority frontier

The guard commits before returning the in-memory outbound frame. A caller can
therefore queue or delay that frame until its claim expires or is superseded.
SQLite cannot atomically commit with a socket, and a successful local `send()`
does not prove receiver delivery or durable effect. A production transport must
re-attest immediately before first-byte dispatch or own a separate durable frame
state machine with renewal, cancellation, receiver idempotency, and
channel-bound terminal receipts. Rev0881 does not hide that later frontier under
the word “dispatch.”

### Executable composition

The largest product gap remains unchanged: the shipped executable does not yet
use the newer causal SQLite owner, authenticated file delivery service, and
retained-root effect owner as one production path. Further oracle hardening is
valuable, but the next major milestone should expose one narrow executable
file operation through the complete path and crash-inject every boundary.

## Evidence expected for rev0881

The revision gate should include:

- GCC Debug focused and full registered tests;
- Clang Release C++ `-Werror` focused tests;
- GCC ASan/UBSan focused tests including bundled SQLite where relevant;
- repeated stress of the path-policy, delivery service, mount namespace, and
  boot-identity tests;
- updated existing file-delivery lexical audit;
- the dedicated rev0881 path-capability and outbox-dispatch-guard lexical audits;
- exact parent-to-child source patch;
- compact active implementation projection and lineage; and
- final directory and ZIP package verification.

A host-denied mount-namespace `unshare()` witness must be reported as skipped,
not silently counted as an executed negative test.

## Nonclaims

Rev0881 does not claim:

- that every POSIX descendant directory shares the root’s observed component
  limit;
- that already-staged legacy poison is repaired;
- that boot UUID or mount IDs are restart-stable root identity;
- that a mount namespace handle defeats a privileged or same-process attacker;
- Windows path-policy parity;
- a complete retry/dead-letter scheduler;
- that a returned in-memory frame remains authorized until first-byte network
  dispatch;
- durable quarantine evidence when Linux boot identity is unavailable;
- atomicity across causal SQLite, effect SQLite, filesystem, and sender state;
- production use by `anonsync_core`;
- confidentiality, anonymity, unlinkability, endpoint hiding, or traffic
  analysis resistance; or
- formal proof.

## Lexical audits are not semantic proof

The new source audit inventories expected files, names, dependency direction,
and coarse ordering. It can catch deletion, accidental renumbering, stale audit
assumptions, and obvious authority-flow regressions. It cannot prove that the
kernel follows the expected semantics, that no race exists, that exceptions
preserve all invariants, or that a compiler produced the intended machine code.
Runtime, sanitizer, stress, crash-frontier, and eventually differential/formal
evidence remain load-bearing.
