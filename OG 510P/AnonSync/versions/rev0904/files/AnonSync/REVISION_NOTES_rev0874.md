# AnonSync rev0874 revision notes

## Owned outbox time, writer-linearized sampling, cumulative drift, and schema v5

Rev0874 removes caller-supplied epoch time from the SQLite outbox owner. Lease
claim, settlement, renewal, retry release, and clock recovery now acquire time
through one injected `SyncReplicaOutboxClockSource`. The production Linux source
binds each observation to source ID, boot UUID, the calling thread's time
namespace, realtime, `CLOCK_BOOTTIME`, uncertainty, and kernel synchronization
state.

The owner retains the complete accepted/rejected clock state, not only a scalar
high-water mark. Rollback, source change, reboot, time-namespace change,
unsynchronized quality, excessive uncertainty, excessive cumulative forward
step, and excessive cumulative realtime lag produce sticky durable quarantine.
Recovery is explicit, generation-fenced, forward-only relative to durable high
water, and establishes a fresh drift anchor.

## Critical audit correction: sample after writer authority

An early implementation sampled the host clock before `BEGIN IMMEDIATE` to keep
clock I/O out of SQLite's single-writer critical section. That was incorrect. A
sample could age while another connection held the writer transaction, allowing
a receipt to be accepted after real expiry even though no database generation had
changed.

Rev0874 keeps only CSPRNG claim entropy outside the lock. Authoritative clock
sampling occurs after:

1. successful `BEGIN IMMEDIATE`;
2. typed writer-authority verification; and
3. complete exact-state restoration.

Settlement, renewal, and retry release also compare exact intent/claim identity
before sampling, so missing or stale receipts cannot ratchet or quarantine the
clock. A deterministic two-connection probe requires the writer slot to be held
inside the clock callback and will fail if a future refactor reintroduces
pre-lock sampling.

## Critical audit correction: cumulative, not pairwise, drift

A pairwise-only drift check can be bypassed by many individually small realtime
steps or stalls. `SyncReplicaOutboxClockState` now retains a recovery anchor.
Every later accepted observation is compared with that fixed anchor, including
endpoint uncertainty and durable policy allowance. The anchor advances only on
initialization or explicit recovery.

Policy replacement reproves retained accepted evidence under the replacement
uncertainty, forward-step, and realtime-lag ceilings before committing.

## Linux observation source

The Linux source:

- reads bounded boot ID evidence before and after sampling;
- reads `/proc/thread-self/ns/time`, not process-leader `/proc/self`, before and
  after sampling;
- brackets `adjtimex` realtime with `CLOCK_BOOTTIME`;
- adds acquisition span to kernel error bounds;
- rejects boot, namespace, or boottime changes during acquisition; and
- labels restricted fallback observations `Unknown`, which cannot become healthy
  time authority.

`CLOCK_BOOTTIME` includes suspend, which is the intended local lease-aging
behavior. The source is explicitly Linux-first; non-Linux observation fails
rather than inventing portable semantics.

## Schema v5 and migration

Schema v5 adds durable clock policy fields and replaces the high-water-only clock
row with bounded canonical clock-state bytes plus an identity-bound unkeyed
structural digest.

Exact schema-v1 through schema-v4 databases are completely restored and attested
before migration. Historical caller-derived time becomes `LegacyUnbound`
quarantine while preserving the strongest durable high-water floor. Migration
does not fabricate source, boot, namespace, uncertainty, synchronization, or
anchor evidence.

A new exact v4 fixture proves that rev0873 retry deadline, release observation,
and provenance survive v5 migration byte-for-byte. A malformed v4 provenance row
is rejected before schema publication. Explicit recovery is required before the
migrated owner can mint new liveness decisions.

## Build, audit, and refactor corrections

The retired rev0873 `SyncReplicaOutboxTimeFence` implementation and test are
removed. CMake now registers the owned-clock library, runtime, structural audit,
and sanitizer targets. The release verifier requires the old files only for an
exact rev0873 package and requires the owned-clock implementation, tests, audit,
and design record for rev0874 and later.

The clock, lease, and SQLite structural audits now require writer-linearized
sampling, exact stale-receipt behavior, cumulative anchors, schema v5, exact
v1-v4 migration, full clock-row compare/update, and complete staged
re-attestation.

## Focused proof surface

The final focused Debug slice reports:

- owned clock runtime: 43 checks;
- pure lease runtime: 37 checks;
- SQLite owner runtime: 185 checks;
- owner stress: 20/20 iterations and 3,700/3,700 checks;
- owned clock structural audit: 21/21;
- lease structural audit: 19/19; and
- SQLite owner structural audit: 38/38.

The full Debug registry reports 176/176 tests passed. In-archive evidence
retains the Clang warning, ASan/UBSan, static-analyzer, lineage,
active-projection, and hygiene lanes, summarized by `RELEASE_GATE.json`. Final
directory and ZIP verifier reports are emitted alongside the sealed artifact;
they cannot be embedded in the bytes they attest without invalidating that
attestation.

## Heart of the mission

AnonSync remains an evidence-authorized, crash-consistent, bounded convergence
engine under construction:

> Exact history is authority; summaries are acceleration.

A lease decision must remain answerable to the exact receipt, serialized
cutpoint, clock observation, identity binding, uncertainty, and durable policy
that authorized it. Rev0874 moves that evidence into one owner and makes anomaly
history survive restart.

## Remaining gaps

The host kernel and time discipline remain trusted. Clock and cutpoint digests
are unkeyed. There is no malicious-host defense, authenticated network time,
secure hardware counter, or remote time witness.

The sender still lacks a complete retry classifier, bounded backoff/jitter,
maximum attempt age/count, poison/dead-letter state, and production indexed wake
scheduler.

There is no authenticated sender/receiver vertical slice, receiver-side
idempotency/effect owner, payload materializer, atomic visible-file publication,
or signed terminal receipt. Sender settlement is not exactly-once delivery.

The SQLite owner deliberately restores and re-attests full retained history. It
is a reference oracle and repair scaffold, not a production scaling claim. A
future incremental owner should be differential-tested against it rather than
weakening its cutpoint and clock boundaries.

Membership and actor key lifecycle, causal stability, compaction, complete
physical resource governance, Sybil-resistant fairness, and a privacy threat
model remain future work.

See `OWNED_OUTBOX_CLOCK_AUDIT_rev0874.md` for the full authority analysis,
linearization argument, state machine, migration table, waste audit, primary
source research, speculation, roadmap, and deliberate nonclaims.
