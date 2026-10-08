# AnonSync rev0874 — owned outbox clock and writer-linearization audit

## Executive finding

Rev0874 closes the most important remaining authority gap in the sender outbox:
lease expiry, retry readiness, settlement, renewal, and clock recovery no longer
accept epoch time supplied by a caller. One owner now acquires a bounded Linux
clock observation, retains the exact accepted and rejected evidence, binds that
evidence to boot and calling-thread time-namespace identity, detects rollback and
bounded drift, persists quarantine across restart, and requires an explicit,
generation-fenced recovery.

That change exposed two subtler defects during implementation.

First, an early version sampled the new clock before `BEGIN IMMEDIATE` so that
clock I/O would not occupy SQLite's single writer slot. This looked like a
performance improvement, but it was an authority error. Another connection could
hold the writer transaction until a live receipt had actually expired; the
waiting operation could then acquire the lock and settle or renew using its stale
pre-lock observation. Rev0874 keeps only claim entropy outside the lock. Every
authoritative clock sample occurs after a successful immediate transaction and a
complete restore of the exact cutpoint. A deterministic two-connection test
proves that the clock callback observes the writer lock already held.

Second, a pairwise drift test is insufficient. Repeated wall-clock steps that are
each just below the configured limit can accumulate without any individual pair
violating policy. Rev0874 retains a durable recovery anchor and compares every
later accepted observation with that anchor. The same cumulative rule applies in
both directions: excessive realtime advance relative to boot-relative elapsed
time is a forward-step anomaly; excessive boot-relative advance relative to
realtime is a realtime-lag anomaly. A healthy state cannot be restored under a
policy it no longer satisfies.

Schema v5 persists the complete canonical clock state and its unkeyed structural
digest, plus independent durable uncertainty, forward-step, and realtime-lag
ceilings. Exact schema-v1 through schema-v4 databases are restored and attested
before migration. Because those versions retained caller-derived epoch values but
not a source/boot/namespace observation, migration preserves the strongest time
floor they prove and publishes `LegacyUnbound` quarantine. It does not relabel old
numbers as observations. Exact schema-v4 retry-release provenance is preserved
byte-for-byte, and malformed v4 provenance is rejected before migration.

This is a material correctness correction, not a trusted-time or exactly-once
claim. The Linux host, kernel, procfs view, NTP discipline, process integrity, and
local SQLite file remain within the trust boundary. Digests are unkeyed. A host
administrator or attacker able to rewrite all state and recompute all digests is
not defeated. The implementation is Linux-first and deliberately fails closed
when it cannot bind a usable observation. The SQLite owner remains an O(history)
assurance scaffold rather than a production scaling implementation.

## Heart of the mission

AnonSync is not principally a file-copy program. Its core mission is to make
state transitions answerable to exact evidence and explicit authority, then keep
those boundaries intact through concurrency, crash, replay, partial knowledge,
resource pressure, schema evolution, and hostile or malformed input.

The governing rule is:

> Exact history is authority; summaries are acceleration.

A digest, counter, deadline, lease, projection, index, clock high-water mark, or
receipt can accelerate and coordinate work. None may silently become stronger
than the exact bytes, observation, identity, policy, and serialized cutpoint that
created it.

For the current datacube, that mission decomposes into connected owners:

1. **Canonical operation identity.** Exact operation bytes are frozen and one
   immutable operation ID is derived from them.
2. **Exact causal authority.** Immediate parents are explicit evidence. Compact
   summaries may locate differences but cannot replace the named parent graph.
3. **Actor and membership authority.** Device/key epochs, rotation, revocation,
   recovery, and treatment of old epochs must eventually be authenticated and
   explicit.
4. **Durable publication.** Operation bytes, parent edges, local counter
   bindings, projections, sender intents, leases, retry provenance, clock state,
   and effect state must cross a crash boundary as one attested cutpoint.
5. **Deterministic projection.** Retained evidence remains distinct from active
   and visible state so changes in dependency or trust can be re-evaluated.
6. **Bounded dissemination.** Missing-node exchange, fanout, attempts, retained
   bytes, CPU, identities, dependencies, deadlines, and wake work need explicit
   ceilings and backpressure semantics.
7. **Receiver effect ownership.** A terminal receiver decision must bind one
   authenticated request to one idempotent, crash-consistent filesystem-visible
   effect and one terminal receipt.
8. **Privacy.** Anonymity, unlinkability, and metadata-hiding claims require a
   stated adversary and an observable-traffic model; they cannot be inferred from
   encrypted payloads alone.

Rev0874 belongs to the fourth and sixth owners. A lease deadline is not merely an
integer comparison. It is a claim that one exact observation, under one durable
policy and one serialized state, was allowed to revoke or extend attempt
authority. Prior revisions retained more of that history over time—receipt-bound
attempts, expiry, anti-rollback high water, and retry-release provenance—but the
clock itself was still caller-supplied. Rev0874 moves the observation boundary
inside the owner.

## What was severely wrong

### Caller time was mislabeled as owner authority

Before rev0874, the SQLite owner accepted `now_epoch` through public outbox APIs.
It checked monotonic high water and used bounded arithmetic, but the caller still
selected the value. A caller could submit a far-future epoch. The high-water
fence would then faithfully preserve that bad value and turn one untrusted sample
into durable denial of service. Conversely, a caller that failed to advance time
could postpone expiry or retry readiness.

Anti-rollback is necessary but not sufficient. It answers only, "did this value
move below what was accepted before?" It does not answer:

- what source produced the value;
- whether the host considered that source synchronized;
- how uncertain the sample was;
- whether the machine rebooted;
- whether the calling thread changed time namespace;
- whether realtime jumped far ahead of elapsed boot time;
- whether realtime stalled far behind elapsed boot time; or
- which observation was rejected and why.

Rev0874 removes caller-time parameters from the production owner surface. Tests
inject a clock source object rather than using a privileged overload, so the
same ownership shape is exercised in production and tests.

### Sampling before the writer lock created stale expiry authority

The first owned-clock draft sampled before opening the immediate transaction,
then retried if the restored durable clock generation differed. That pattern
protected against one kind of state race but not against elapsed physical time.
Consider a receipt whose deadline is 100:

1. Connection A samples epoch 99.
2. Connection B holds SQLite's writer transaction.
3. A waits long enough for real epoch 100 or 101.
4. B commits.
5. A acquires the writer slot, restores the unchanged receipt, and uses 99.
6. A settles or renews authority that was already expired in real time.

No generation comparison detects this. Nothing in the database changed while A
waited; only time changed. The optimization moved the observation outside the
very serialization boundary that was supposed to authorize the transition.

Rev0874 establishes the order:

1. validate non-time arguments;
2. acquire claim entropy outside the lock when needed;
3. execute `BEGIN IMMEDIATE` successfully;
4. assert typed writer authority;
5. restore and independently attest the complete current state;
6. for receipt operations, find the exact row and compare the current claim ID;
7. acquire the host clock observation;
8. pass it through the durable clock state machine;
9. apply the lease/retry transition;
10. write exact prior-row-conditional changes;
11. independently restore the complete staged cutpoint;
12. compare it with the intended state; and
13. commit.

The clock sample now lies inside a real SQLite writer transaction and after
restore. If the operation waits for another writer, it waits before the sample.
If post-sample work takes time, the transition can be linearized at the sample
instant while this owner has exclusive writer authority. Later delay only
shortens a new lease relative to wall time; it does not resurrect an expired one.

A `WriterLockClockProbeSource` owns a second SQLite connection. During the clock
callback it attempts `BEGIN IMMEDIATE` on that connection and requires
`SQLITE_BUSY`. If a future refactor moves sampling before writer authority, the
test fails deterministically rather than relying on scheduler timing.

### Pairwise drift checks allowed cumulative laundering

Suppose policy allows at most 300 seconds of unexpected forward step. A pairwise
implementation might accept this sequence, where each observation advances
realtime 299 seconds more than boot-relative elapsed time:

```
anchor:    real=1,000  boot=1,000
sample 1:  real=1,300  boot=1,001
sample 2:  real=1,600  boot=1,002
sample 3:  real=1,900  boot=1,003
```

Each adjacent difference is under the threshold. The aggregate difference from
the original trusted point is nearly 900 seconds. The same problem exists in the
opposite direction: repeated small realtime stalls can postpone all expiry and
retry boundaries indefinitely.

The state now retains an anchor created by initialization or explicit recovery.
Every later accepted observation is compared against that anchor. Informally:

```
elapsed_real = observation.realtime - anchor.realtime
elapsed_boot = observation.boottime - anchor.boottime

forward anomaly when:
  elapsed_real > elapsed_boot
                 + anchor_uncertainty
                 + observation_uncertainty
                 + max_forward_step

lag anomaly when:
  elapsed_boot > elapsed_real
                 + anchor_uncertainty
                 + observation_uncertainty
                 + max_realtime_lag
```

The implementation performs the comparison by subtracting allowances from the
positive excess rather than summing attacker-influenced `uint64_t` values. This
avoids overflow turning a fail-closed limit into an acceptance path.

The anchor is deliberately not rolled forward on every successful sample. Only
explicit recovery establishes a new anchor. A replacement policy must reprove
both the retained anchor and latest accepted observation against the replacement
ceilings before it can commit.

### Process-scoped namespace lookup was the wrong identity boundary

Linux time namespaces are associated with tasks and virtualize boot-relative
clocks. In a multithreaded process, `/proc/self` names the thread-group leader,
whereas `/proc/thread-self` resolves for the calling thread. An outbox operation
running on another thread must bind the namespace of the thread that actually
samples `CLOCK_BOOTTIME`.

Rev0874 uses `/proc/thread-self/ns/time` and reads namespace identity before and
after the clock sample. It similarly reads boot ID before and after. A change
during acquisition aborts the observation rather than mixing identities.

### The build and audit graph still named a retired primitive

The interrupted rev0874 tree had new owned-clock files but still retained build
and audit references to the separated rev0873 `SyncReplicaOutboxTimeFence`.
That mismatch was more than housekeeping: it made it possible for the new
boundary to compile in one local path while the registered assurance graph still
proved the old surface.

Rev0874 removes the retired implementation and test, registers the clock library,
clock runtime, and clock structural audit, updates sanitizer target lists, and
teaches the release verifier to require the old fence only for exact rev0873
packages and the owned-clock slice for rev0874 and later.

### Exact v4 migration lacked a direct fixture

The first schema-v5 migration tests covered v1-v3 and malformed current state,
but not an exact rev0873 schema-v4 row with exact retry-release provenance. That
left a dangerous blind spot: the migration could accidentally preserve the
retry deadline while changing or dropping its release observation/provenance.

Rev0874 constructs an exact v4 database, including its schema text, outbox digest,
clock digest, cutpoint digest, and release fields. The positive test proves the
v4 retry deadline and exact release observation survive v5 migration byte for
byte while the unauthenticated legacy clock becomes `LegacyUnbound`. A negative
test downgrades or corrupts v4 provenance and requires constructor rejection
before any v5 schema is published.

## Authority taxonomy

### Canonical replica evidence

Canonical operations and their parent edges are replicated evidence. Equivalent
authorized evidence and trust state should produce equivalent replica state.
Outbox clock observations are not canonical replica evidence and are not sent to
peers merely because they are durable.

### Local structural evidence

The SQLite owner retains redundant counts, projections, exact local counter
bindings, outbox rows, and unkeyed digests. These make torn publication, casual
edits, shadowed names, malformed migration, and many trigger mutations detectable.
They are local structural evidence, not cryptographic authentication against a
fully privileged store attacker.

### Liveness authority

Clock observations, leases, deadlines, retry release observations, and attempt
receipts govern when local sender work may proceed, be revoked, be delayed, or be
retired. They are durable because restart must not silently recreate authority,
but they are distinct from canonical replica history.

### Clock quality evidence

One observation contains:

- a bounded canonical source ID;
- the kernel boot UUID;
- a digest of the calling thread's time-namespace device/inode identity;
- realtime nanoseconds;
- `CLOCK_BOOTTIME` nanoseconds;
- uncertainty nanoseconds; and
- a synchronization state: unknown, synchronized, or unsynchronized.

The source ID distinguishes `adjtimex` acquisition from the restricted fallback
and distinguishes kernels where time namespace identity is available. The state
machine accepts only `Synchronized`; `Unknown` and `Unsynchronized` quarantine.
The fallback therefore preserves diagnostics but does not silently mint expiry
authority.

### Durable policy

Clock ceilings are independent of evidence-retention and outbox-capacity limits:

- maximum uncertainty;
- maximum cumulative forward step; and
- maximum cumulative realtime lag.

Each has a nonzero hard maximum in code. Configuration cannot disable the
tripwire with zero or create arithmetic hazards with unbounded values.

## Linux observation design

The Linux source performs a bounded, identity-bracketed sample:

1. read `/proc/sys/kernel/random/boot_id` with `O_NOFOLLOW` and a size cap;
2. `stat` `/proc/thread-self/ns/time`;
3. read `CLOCK_BOOTTIME` before;
4. call `adjtimex` in query mode;
5. if query access is unavailable for an allowed reason, read `CLOCK_REALTIME`
   as a diagnostic fallback;
6. read `CLOCK_BOOTTIME` after;
7. re-read time-namespace identity and boot ID;
8. reject identity change or boottime reversal;
9. place the boot-relative observation at the bracket midpoint; and
10. add the acquisition span to uncertainty.

When `adjtimex` succeeds, the source uses the returned kernel realtime and the
larger of `maxerror` and `esterror`, converted from microseconds, plus the sample
span. `TIME_ERROR`, `STA_UNSYNC`, or `STA_CLOCKERR` maps to `Unsynchronized`.
`STA_NANO` controls interpretation of the returned realtime subsecond field; it
does not change the documented microsecond units of the error fields.

`CLOCK_BOOTTIME` is selected over `CLOCK_MONOTONIC` because it includes suspend.
A lease should normally continue aging while a laptop sleeps. This is still a
local policy choice, not a proof of UTC. Time namespaces can offset boottime, so
the namespace identity is part of the accepted source identity and a namespace
change quarantines.

The procfs reads are bounded and symlink substitution is rejected for boot ID.
Integer conversions and uncertainty additions are overflow checked. On non-Linux
platforms the factory returns a source whose observation method fails explicitly;
no portable trusted-time claim is made.

One conservative availability tradeoff remains: on a modern kernel where the
calling thread's time-namespace identity cannot be read, the source refuses to
pretend the namespace is irrelevant. A production port may need a more nuanced
platform capability probe, but weakening the identity binding merely to increase
availability would reopen a correctness hole.

## Clock state machine

### Uninitialized

No high water, generations, anchor, accepted observation, rejected observation,
or anomaly exists. The first synchronized observation within uncertainty policy
becomes both anchor and latest accepted observation. The observation generation
advances from zero to one.

### Healthy

A healthy state retains:

- nonzero high-water epoch equal to the seconds projection of the latest accepted
  realtime observation;
- nonzero observation generation;
- recovery generation not greater than observation generation;
- the anchor;
- the latest synchronized accepted observation;
- no anomaly; and
- no rejected observation.

A byte-identical repeated observation is an accepted no-op and does not advance
generation. A changed accepted observation advances generation and updates the
high water. The anchor remains fixed.

Before acceptance, the state machine checks, in order:

1. synchronization quality;
2. uncertainty ceiling;
3. source identity;
4. boot identity;
5. thread time-namespace identity;
6. boot-relative rollback;
7. realtime rollback;
8. cumulative forward step; and
9. cumulative realtime lag.

An anomalous sample cannot mint a usable epoch.

### Quarantined

Quarantine is sticky. The state retains the previous accepted evidence when one
exists, the exact rejected observation, its anomaly, and an incremented
observation generation. Ordinary observation cannot clear quarantine. Calls that
need time commit the quarantine cutpoint and then report failure, ensuring restart
cannot forget the event merely because the user operation failed.

`LegacyUnbound` is the special migration quarantine. It retains a nonzero durable
high-water epoch but no fabricated accepted/rejected observation or anchor. It
states that older code persisted a time floor but did not retain evidence that
can satisfy the v5 clock contract.

### Explicit recovery

Recovery requires:

- current health is quarantined;
- the caller names the exact current observation generation;
- a fresh synchronized observation within uncertainty policy;
- an epoch not below durable high water; and
- the same writer-transaction and staged re-attestation path as other
  publications.

Recovery intentionally may bind a new source, boot, or namespace: that is the
point at which an operator accepts the changed environment. It increments both
observation and recovery generations and establishes the recovery observation as
a new anchor. A stale recovery request cannot overwrite a newer quarantine or
accepted transition.

The recovery API does not take a caller-provided timestamp. The expected
generation is a compare-and-set fence, not liveness evidence.

## Canonical encoding and structural binding

The complete clock state has a bounded canonical binary encoding. It includes a
versioned domain, health, high water, observation and recovery generations,
optional anchor, optional accepted observation, anomaly, and optional rejected
observation. Optional values use exact 0/1 markers; unsupported enum values,
truncation, trailing bytes, partial states, oversized values, and noncanonical
re-encodings fail closed.

Schema v5 stores:

- `clock_state_bytes`, bounded to 1..512 bytes; and
- `clock_digest`, an unkeyed SHA-256 domain-separated over folder identity,
  local actor identity, and exact canonical state bytes.

Every read decodes and validates the state, re-encodes it to prove uniqueness,
recomputes the digest, and revalidates it under durable clock policy. Every
update compares both prior state bytes and prior digest in the `WHERE` clause and
requires exactly one changed row. A trigger, competing writer, or stale object
cannot silently retarget a clock update.

The clock digest is deliberately not folded into canonical replicated evidence.
The current SQLite cutpoint already binds the outbox and durable policy surfaces;
the separately restored clock row is compared during complete staged
re-attestation. The design preserves the distinction between local liveness
authority and replicated operation evidence.

## Schema v5 and exact migration

Schema text is protocol state. The owner accepts only exact known `sqlite_schema`
objects in `main`, rejects extra or changed objects, rejects attached-database
surfaces, disables trusted schema, requires foreign keys, and qualifies durable
SQL names with `main.` so TEMP shadows cannot redirect authority.

Schema v5 adds three durable policy fields to the meta row:

- `max_outbox_clock_uncertainty_ns_be`;
- `max_outbox_clock_forward_step_seconds_be`; and
- `max_outbox_clock_realtime_lag_seconds_be`.

It replaces the old high-water-only clock row with the complete canonical state.
Retry-release provenance introduced in schema v4 remains intact.

Migration follows the same discipline for v1, v2, v3, and v4:

| source | exact retained time | retry provenance | v5 result |
|---|---|---|---|
| v1 | no separate clock row; lease/retry rows imply a floor | none | derive the strongest conservative floor; publish `LegacyUnbound` |
| v2 | no separate clock row; live lease/retry rows imply a floor | none | preserve rows; publish `LegacyUnbound` |
| v3 | high-water-only clock row | released rows lack exact release observation | preserve the greater of row floor and clock high water; mark old retry provenance honestly; publish `LegacyUnbound` |
| v4 | high-water-only clock row | exact/legacy retry provenance is explicit | preserve every retry field exactly; preserve the time floor; publish `LegacyUnbound` |

The old database is not upgraded by trusting a few rows. It is first restored
under its exact schema definition, exact historical digest domains, and all
redundant projection checks. Only then, inside the same immediate transaction,
are the prior meta/outbox/clock protocol surfaces replaced. The new schema is
verified, rows are inserted, the entire staged v5 cutpoint is independently
restored, and only an exact match commits.

A crash before commit leaves the exact old schema and state. A crash after commit
leaves the exact new schema and state. There is no intended hybrid cutpoint.

Migration quarantine is intentional. An old high-water value is useful evidence
against moving backward, but it cannot establish source, synchronization,
uncertainty, boot, namespace, or drift anchor. First v5 use therefore requires
explicit recovery rather than silently laundering historical caller input into
owned time.

## Receipt and claim linearization

The outbox owner differentiates operations that possess liveness authority from
those that do not.

### Claim

Claim validates worker, optional destination, and lease duration before the
transaction. It obtains CSPRNG entropy before the lock because randomness is not
a statement about current expiry. After writer authority and full restore, it
samples time, accepts or quarantines the clock observation, finds the first
canonical ready intent, and mints a claim ID bound to exact intent scope, prior
lease state, current cutpoint digest, worker, deadline, and entropy.

If no intent is ready, the accepted clock observation is still independently
re-attested and committed. This preserves high water and anomaly detection rather
than making time advancement depend on finding work.

### Settlement

Settlement restores the state and finds the exact destination/operation row.
Missing rows and nonmatching claim IDs return without sampling time. They have no
current receipt authority, so allowing them to ratchet or quarantine the clock
would let arbitrary stale traffic control sender liveness.

A matching claim samples under writer authority. Expiry at the exact deadline is
terminal: the matching receipt returns `ExpiredClaim` after committing any newer
accepted clock observation. A live matching receipt deletes exactly one intent,
updates structural meta state, re-attests the complete cutpoint, and commits.

### Renewal

Renewal follows the same exact-row-before-time rule. It cannot revive an expired
claim, rotate receipt identity, shorten a deadline, or exceed the fixed cumulative
attempt lifetime. A request already covered by the existing deadline is a lease
no-op but may commit a newer valid clock observation.

### Retry release

Release also requires an exact live receipt. It accepts a relative bounded delay,
not an absolute caller-computed timestamp. It derives the retry deadline from the
same accepted owned observation that authorizes the release and retains that
observation as exact retry provenance. Overflow and fixed retry-budget checks are
performed by the policy owner.

## Crash and tamper frontiers

Rev0874's focused owner test exercises:

- constructor restore of complete v5 state;
- clock initialization and restart;
- exact source/boot/namespace/rollback/drift quarantine;
- sticky quarantine and generation-fenced recovery;
- direct clock-state and digest tamper;
- policy replacement against retained accepted evidence;
- TEMP-trigger mutation after a clock update;
- deterministic proof that sampling occurs under writer authority;
- stale and missing receipt paths that must not sample;
- v1, v2, v3, and exact v4 migration;
- malformed v4 retry provenance rejection before migration;
- rollback after failed staged re-attestation;
- process crash after clock-row update but before commit; and
- successful atomic retry after restart.

Clock-only publication uses the same independent staged restore as operation and
outbox mutation. A process-killing SQLite update hook demonstrates that a crash
after the clock update statement but before commit exposes the old complete
cutpoint on restart, never a partially advanced clock row.

## Waste and assurance inversion corrected

### Optimizing the wrong syscall

Moving the clock sample outside the writer lock saved a small amount of lock hold
time while the owner already performs O(history) restore before the sample and
O(history) staged restore before commit. That was an assurance inversion: a tiny
optimization weakened the authority boundary in the least scalable component of
the path. Rev0874 restores correctness first and names the owner as a reference
oracle, not a throughput implementation.

### Pairwise state that forgot history

Pairwise drift logic discarded the very baseline needed to prove the cumulative
policy. The durable anchor adds only three integers but removes an unbounded
laundering path. This is the same mission pattern seen elsewhere in the cube:
when a derived decision survives restart, the exact evidence needed to reprove it
must survive too.

### Duplicate and stale audit vocabulary

The interrupted tree simultaneously described schema v5 clock ownership and
compiled/audited schema-v3 high-water vocabulary. Rev0874 removes the dead
primitive, advances audit formats, and revision-scopes the release verifier so
new requirements do not retroactively invalidate the sealed parent.

### Missing migration specimen

A generic migration test is not enough when schema text, digest domains, and
provenance states are protocol evidence. The direct v4 specimen is more verbose,
but it prevents a false green lane where only older, weaker schemas are tested.

### Full restore is expensive but currently useful

The owner reconstructs the pure model, verifies all projection rows and digests,
scans the retained outbox, and repeats complete restore before commit. That is
wasteful for production traffic, but it is not accidental waste today. It is the
strongest executable oracle available for future incremental work. The harmful
waste would be replacing it with point updates before preserving equivalent
preconditions, exact conditional writes, and periodic full re-attestation.

## Online primary-source research

Research was used to check the implementation boundary, not to import authority
by analogy.

### Linux time namespaces and boot-relative clocks

The Linux `time_namespaces(7)` manual states that time namespaces virtualize
`CLOCK_MONOTONIC` and `CLOCK_BOOTTIME`, and that boottime includes suspended time.
That supports the decision to bind time-namespace identity and use boottime as
the elapsed-time comparator for leases.

- https://man7.org/linux/man-pages/man7/time_namespaces.7.html

The procfs manual states that `/proc/thread-self` resolves to the accessing
thread's `/proc/self/task/tid` directory. This is the correct identity boundary
for a clock sample performed by a specific thread in a multithreaded process.

- https://man7.org/linux/man-pages/man5/proc.5.html

The `adjtimex(2)` manual documents query access to the kernel clock-discipline
state, the returned current time, error estimates, status flags, and `TIME_ERROR`.
Those values provide bounded quality evidence, not a cryptographic guarantee of
UTC.

- https://man7.org/linux/man-pages/man2/adjtimex.2.html

### SQLite writer serialization

SQLite's transaction documentation says `BEGIN IMMEDIATE` starts a write
transaction immediately and can return `SQLITE_BUSY` when another write
transaction is active. The implementation uses successful immediate transaction
acquisition as the local writer serialization boundary before time is sampled.

- https://sqlite.org/lang_transaction.html

This does not make SQLite a physical-time oracle. It supplies the ordering
boundary between competing local durable transitions. The clock source supplies
the observation; the clock state machine supplies quality and continuity policy;
the transaction binds that decision to one exact cutpoint.

### Fixed operation-start time in TUF

The Update Framework specification fixes time at the beginning of an update
workflow for metadata-expiry and freeze-attack checks. The analogy is useful:
within one serialized workflow, inconsistent repeated reads of time can create
self-contradictory decisions. Rev0874 similarly uses one accepted observation for
one outbox transition and its deadline arithmetic.

- https://theupdateframework.github.io/specification/latest/

TUF's signed metadata and repository threat model are substantially different.
AnonSync does not inherit TUF security properties merely by fixing an operation
time.

### Hybrid logical clocks

The HLC paper shows how a logical component can preserve causal ordering while
remaining near physical time and helping consistent snapshots.

- https://cse.buffalo.edu/tech-reports/2014-04.pdf
- https://link.springer.com/chapter/10.1007/978-3-319-14472-6_2

HLC is a plausible future acceleration for causal scheduling and observability.
It is not, by itself, physical lease-expiry authority. A logical counter can keep
advancing through a wall-clock anomaly, but that does not prove a real duration
elapsed. Rev0874 therefore keeps causal evidence and local physical liveness
evidence as separate owners.

## What should change next

### 1. Build the receiver-side vertical slice

The sender now has stronger attempt and time authority, but a live sender receipt
still is not authenticated terminal receiver evidence. The next high-value slice
should bind:

- canonical sender request bytes;
- sender actor/key epoch and membership authorization;
- destination identity;
- operation and payload commitment;
- attempt/receipt identity;
- receiver idempotency key;
- durable receiver decision;
- exact filesystem effect intent;
- atomic visible-file publication; and
- signed terminal receipt.

A sender should settle only a receipt that proves the receiver durably owns the
corresponding terminal effect. Ambiguous network failure must remain retryable
without duplicating the visible effect.

### 2. Introduce authenticated local authority where the threat model needs it

Clock and cutpoint digests detect accidental or partial inconsistency. They do
not stop a privileged local attacker from rewriting all rows and rehashing them.
Potential directions include a hardware-/OS-bound key, append-only authenticated
journal, remote witness, or signed checkpoint chain. Each changes recovery and
availability semantics and must name who owns key rotation and rollback recovery.

### 3. Keep the full owner as an oracle while adding an incremental owner

Production scaling should not delete the current owner first. Add a second
implementation that uses indexed point reads, exact conditional updates, and
incremental projection. Differentially execute both against generated traces and
crash frontiers. Periodically run full re-attestation, and require migration and
repair tools to use the reference restore path.

The incremental design must preserve:

- exact schema and namespace binding;
- writer-linearized clock sampling;
- exact prior-row compares;
- clock quarantine publication on failed user operations;
- operation/outbox/clock atomicity;
- deterministic projection equivalence; and
- a bounded repair path when summaries disagree.

### 4. Make retry policy complete

Retry provenance now proves when a delay was minted, but policy still lacks:

- failure classes;
- retryability rules;
- exponential or other bounded backoff;
- deterministic jitter inputs;
- maximum attempts and maximum attempt age;
- poison/dead-letter state;
- operator replay and deletion authority; and
- indexed wake scheduling.

These fields should be durable and digest-bound. A scheduler should not infer
policy from volatile process state after restart.

### 5. Decide whether the host clock trust boundary is sufficient

For a single-device sender owner, kernel-disciplined local time may be adequate.
If the threat model includes a malicious host administrator, local clock
observation cannot solve the problem. Alternatives could include authenticated
network time, multiple independent time witnesses, a secure hardware counter,
or a lease protocol whose authority is granted by another authenticated party.
These add network-partition and recovery tradeoffs; none should be introduced as
"trusted time" without an explicit adversary model.

### 6. Improve platform capability handling without fail-open behavior

The Linux source should eventually distinguish:

- kernel without time-namespace support;
- kernel built without the feature;
- procfs unavailable or intentionally masked;
- permission-limited `adjtimex`;
- unsynchronized clock discipline; and
- transient I/O failure.

Those distinctions improve operations and recovery. They must not collapse into a
fallback that labels an unbound or unknown observation synchronized.

### 7. Add generated state-machine and migration testing

The hand-written clock tests pin critical boundaries. Property-based generation
could cover long observation sequences, arbitrary policy replacement, codec
round trips, generation exhaustion edges, and migration rows. A useful oracle is
that every accepted healthy sequence remains valid under the same policy after
canonical encode/decode, and every quarantine remains sticky until an exact
recovery generation succeeds.

### 8. Define privacy only after transport metadata is concrete

Clock ownership does not materially improve anonymity. A practical privacy
review needs the eventual connection pattern, peer discovery, routing metadata,
padding, batching, timing, cover traffic, key distribution, and adversary
observation points. Until then, the project should continue to avoid anonymity
claims despite its name.

## Speculation

Several future combinations appear promising, but they are not implemented
claims.

An HLC could annotate causal operations and help prioritize anti-entropy without
being used for expiry. The owned physical clock could remain the sole lease/retry
source, while HLC values remain replicated causal metadata. Separating the two
would avoid a common design mistake in which a monotonic logical value is treated
as proof that real time elapsed.

A signed time-witness quorum could reduce dependence on one host clock, but the
right semantics may be an interval rather than one timestamp. Lease acceptance
would then need to decide whether the entire uncertainty interval is before the
deadline, after it, or overlaps it. Overlap should probably fail closed or require
an explicit liveness policy. This resembles external-consistency designs more
than ordinary NTP use and would add substantial complexity.

The durable anchor could eventually become a chain of periodic checkpoints,
allowing bounded compaction while retaining anomaly evidence. Any compaction rule
must preserve enough history to prove cumulative drift and explain recovery; it
must not merely keep the newest sample and recreate the pairwise laundering bug.

The O(history) owner can become a valuable offline repair authority. If an
incremental summary disagrees, the full owner can reconstruct exact state, emit a
repair plan, and require a new attested cutpoint. That may be a better long-term
role than trying to optimize the reference path itself.

## Validation summary

The current source has passed the following rev0874-focused lanes before
packaging:

- clock state-machine/runtime: 43 checks;
- pure outbox lease/runtime: 37 checks;
- SQLite owner/runtime: 185 checks;
- repeated owner stress: 20 iterations, 3,700 checks;
- clock structural audit: 21 checks;
- lease structural audit: 19 checks;
- SQLite owner structural audit: 38 checks; and
- full Debug registered suite: 176 of 176 tests.

The release evidence records the final compiler-warning, sanitizer, analyzer,
lineage, projection, hygiene, manifest, directory, and ZIP lanes. A test count is
not a proof of the whole system; it is an exact statement about the executed
surface.

## Deliberate nonclaims

Rev0874 does **not** claim:

- trusted or authenticated physical time;
- UTC correctness or cross-node clock agreement;
- cross-reboot monotonic continuity without recovery;
- defense against a privileged kernel, host administrator, or fully rewriting
  local-store attacker;
- authenticated local cutpoint or clock digests;
- a portable non-Linux clock implementation;
- automatic quarantine recovery;
- global liveness during clock uncertainty or partition;
- exactly-once delivery or exactly-once filesystem effects;
- authenticated sender/receiver transport;
- terminal signed receiver receipts;
- payload/chunk materialization or atomic visible-file publication;
- complete actor key lifecycle, membership, rotation, revocation, or recovery;
- arbitrary Byzantine convergence;
- causal stability, compaction, or tombstone garbage collection;
- fair or Sybil-resistant resource allocation;
- complete CPU, memory, disk, WAL, network, or wake-work bounds;
- production-scale incremental projection;
- confidentiality, anonymity, unlinkability, or metadata hiding;
- secure erasure, forward secrecy, or post-compromise security;
- Windows runtime behavior;
- ThreadSanitizer coverage; or
- formal verification.

The correction is narrower and concrete: local outbox time is now acquired,
validated, serialized, retained, migrated, quarantined, recovered, and audited by
one explicit owner instead of being silently delegated to callers or stale
pre-lock samples.
