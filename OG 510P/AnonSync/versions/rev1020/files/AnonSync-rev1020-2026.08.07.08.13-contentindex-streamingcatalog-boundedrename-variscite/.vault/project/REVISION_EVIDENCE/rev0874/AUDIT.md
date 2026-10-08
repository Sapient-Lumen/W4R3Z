# AnonSync rev0874 audit summary

## Heart of the mission

AnonSync is building an evidence-authorized, crash-consistent, bounded
convergence kernel. Exact canonical operation bytes and exact validated causal
history are the fact owners. Digests, clocks, projections, retry schedules,
leases, counters, indexes, and scheduler observations are subordinate authority:
they may accelerate or constrain work, but they may not silently create history,
widen identity, revive expired work, or convert missing evidence into fact.

The name is not yet a privacy claim. A real anonymity system still needs an
explicit adversary, authenticated actor and membership epochs, key lifecycle,
receiver-side effect ownership, transport metadata analysis, bounded
anti-entropy, and a concrete unlinkability design.

## Severe authority defects corrected

### Stale samples could outlive the SQLite writer wait

The interrupted owned-clock implementation sampled before `BEGIN IMMEDIATE`.
That reduced time spent in SQLite's single-writer critical section, but it also
allowed the sample to age behind another writer. A matching receipt could then
be settled or renewed after real expiry using stale pre-lock time, even when no
database generation changed.

Rev0874 leaves only claim entropy outside the lock. Every authoritative clock
sample now occurs after successful immediate-writer acquisition, typed writer
authority verification, and full exact-state restore. Settlement, renewal, and
retry release reject missing or stale row identity before sampling. A
deterministic two-connection clock probe requires the writer slot to be held
inside the callback and fails if sampling is moved outside the transaction.

### Pairwise drift limits forgot cumulative history

Checking only the latest pair of samples permits many individually legal steps
or stalls to accumulate into an unbounded wall-clock discontinuity. The clock
state now retains an initialization/recovery anchor and compares every accepted
observation with that fixed anchor, including endpoint uncertainty and durable
policy allowance. Ordinary observations cannot advance the anchor. Only
explicit generation-fenced recovery can establish a new one.

### Caller epoch time was mislabeled as owner authority

The production outbox API no longer accepts caller-provided time. One injected
`SyncReplicaOutboxClockSource` supplies source ID, boot ID, calling-thread time
namespace ID, realtime, `CLOCK_BOOTTIME`, uncertainty, and synchronization
quality. The Linux implementation double-samples boot and namespace identity,
uses `/proc/thread-self/ns/time`, brackets `adjtimex` with boottime, and refuses
to mint healthy authority from restricted fallback evidence.

### Migration and assurance graphs were incomplete

Schema v5 stores bounded canonical complete clock state plus structural digest
and independent durable policy. Exact schema-v1 through schema-v4 restore and
attestation precede migration. Historical caller-time state becomes sticky
`LegacyUnbound` quarantine rather than fabricated source/boot/namespace evidence.
A new exact v4 fixture proves rev0873 retry-release provenance survives migration
byte-for-byte and proves malformed provenance is rejected before publication.

The retired rev0873 time-fence files are removed. CMake, sanitizer targets,
structural audits, and the package verifier now name the owned clock boundary.
The verifier keeps the historical time-fence requirement scoped to exact
rev0873 packages so sealed parents remain valid.

## Authority and crash model

The SQLite owner deliberately restores and re-attests the entire retained
cutpoint before every write. The operation sequence is:

1. acquire a typed immediate writer transaction;
2. restore schema, operations, parent edges, local counters, projections,
   outbox, retry provenance, clock state, policies, and digests;
3. reject stale row identity before liveness sampling where applicable;
4. sample and apply the pure clock/lease transition;
5. publish exact prior-state-conditional SQL changes;
6. independently restore the staged cutpoint; and
7. commit only on exact equality.

A clock anomaly is itself durable evidence. The owner commits quarantine before
reporting the user operation failure, so restart cannot erase rejected clock
history. The complete accepted and rejected observations, anomaly, high water,
drift anchor, observation generation, and recovery generation survive restart.

This full-history owner is intentionally expensive. It is a reference oracle,
migration verifier, crash scaffold, and future repair authority—not a production
throughput claim. An incremental owner should be added beside it and
differentially tested against it rather than weakening this cutpoint.

## Exact evidence executed

- GCC 14 Debug: all targets built; final dependency-closure rebuild was no-work.
- One complete registered CTest invocation: 176/176 passed.
- Revision-focused Debug runtime: 43 clock + 37 lease + 185 owner = 265 checks.
- Owner stress: 20/20 iterations, 3,700/3,700 repeated checks.
- Structural audits: 21 clock + 19 lease + 38 owner = 78 checks.
- Clang 17 Release C++ `-Werror`: all three focused boundaries built and all 265
  runtime checks passed. Bundled SQLite remained a GCC-compiled C dependency; a
  warning from that amalgamation is not represented as Clang C++ `-Werror`
  coverage.
- GCC 14 ASan/UBSan Debug: all 265 focused checks passed with leak detection,
  halt-on-error, and bundled SQLite instrumentation enabled.
- Clang static analyzer: three new/refactored production translation units under
  default interprocedural analysis plus the large SQLite owner under explicitly
  shallow/no-IPA analysis; zero diagnostics. Default-IPA owner analysis is not
  claimed.
- The rev0874 patch applied to the verified rev0873 parent reproduces all 342
  active implementation paths and bytes exactly: 18,932,565 bytes and projection
  SHA-256 `d4d701e97413d599a37f97e882d1f4469872713fa1da2c9c51921048171038f8`.

## Remaining mission gaps

The host kernel and time discipline remain trusted. The clock and cutpoint seals
are unkeyed structural digests, not protection against a privileged attacker who
can rewrite and rehash the store. There is no authenticated network time, secure
hardware counter, remote witness, cross-node time agreement, or automatic
quarantine recovery.

The sender lacks complete failure classification, bounded backoff/jitter,
maximum attempt age/count, poison/dead-letter state, operator replay authority,
and a production indexed wake scheduler. There is no authenticated
sender/receiver vertical slice, receiver-side idempotency/effect owner,
payload/chunk materializer, atomic visible-file publication, or signed terminal
receiver receipt. Exactly-once delivery is not claimed.

Actor signatures, membership epochs, key rotation/revocation/recovery, causal
stability, compaction, tombstone collection, rejoin policy, physical resource
governance, Sybil-resistant fairness, and a privacy threat model remain open.

## Highest-leverage next change

Build one authenticated local sender-to-receiver vertical slice that terminates
in an idempotent receiver effect and signed terminal receipt. Keep it narrow:
canonical message framing, actor/key epoch binding, exact duplicate handling,
crash-consistent payload publication, and receipt-bound sender settlement. That
slice will reveal which current local abstractions genuinely compose and which
are still isolated assurance artifacts.
