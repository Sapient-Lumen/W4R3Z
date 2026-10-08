# AnonSync rev0889 audit

## Mission heart

AnonSync remains an authority-accounting system before it is a transport or
file-copy utility. Canonical authorized evidence owns identity, causality,
durable receiver admission, visible publication, retry, receipt, and
settlement. Derived summaries, readiness observations, local TLS completion,
and cached counters may accelerate or diagnose that history but may not mint
new authority.

Rev0889 applies that rule at two previously incomplete boundaries:

1. one accepted Linux socket/TLS/member/session owner now spans pre-byte
   authentication through one terminal receiver conversation; and
2. file-effect capacity is now isolated by stable `device_id` aggregation across
   actor epochs, with exact schema-v2-to-v3 migration and rollback evidence.

## Corrections and refactors

### Receiver transport ownership

A move-only listener capability proves one live nonblocking, close-on-exec
listening socket. A one-shot accepted-session owner consumes the child socket,
server `SSL`, bounded handshake, verified-SPKI membership mapping, receiver
session, exact request/receipt cutpoints, and terminal close. Local receipt
completion remains distinct from peer receipt or sender settlement.

Shared `sync_stream_socket_deadline_poll` and socket-policy leaves replace
repeated polling/descriptor logic. The review also narrowed a catch that had
misclassified local allocation failure as hostile peer behavior and corrected a
moved-from listener fail-stop ordering defect.

### Exact device capacity and migration

Schema v3 adds per-device retained-effect and payload-byte limits while
preserving folder limits as the aggregate boundary. Usage is rederived from the
entire canonical row closure, sorted by actor epoch and device. Compact device
witnesses and limits are bound into the cutpoint; cached counters are not
admission authority.

An exact v2 database migrates inside one `BEGIN IMMEDIATE` transaction. The
owner re-attests v2 policy and rows before DDL, replaces only metadata, inserts
v3 metadata, verifies exact schema, reloads, and compares state before commit.
A SQLite authorizer fault after table replacement proves transactional rollback
to exact v2, followed by successful clean retry.

### Copy frontier

The recovered capacity delta initially copied a newly authorized payload and
canonical record through multiple temporary objects and built public effect
projections during internal attestations. Rev0889 now:

- encodes directly into one `StoredEffect`;
- moves the stored effect into the sorted closure;
- moves derived actor/device vectors and digests;
- uses `AuthorityOnly` projection for constructor, stage, materialization, and
  attestation; and
- materializes record views only for the public snapshot, moving validated
  records into that return value.

The service also moves its decoded payload-bearing request after durable stage.
This removes redundant full-payload copies without weakening the
full-history-oracle invariant.

### Audit maintenance

Three stale lexical audits had equated the file-effect owner with schema v2 or
searched retired source shapes. They now recognize exact v2/v3 boundaries and
actual semantic definitions. Lexical checks remain hygiene rather than proof;
compiled migration, restart, TLS, and fault-injection tests are load-bearing.

The pre-seal evidence self-audit also found that an ignored `__pycache__` file
had been included in a candidate active projection. It was removed, the
projection and parent delta were recomputed from the clean release
inventory, and generated Python bytecode is excluded from the package.

## Validation

- GCC 14 Debug out-of-tree all-target graph completed, followed by `ninja: no
  work to do` on the exact final source.
- 206/206 registered tests passed in one final invocation.
- 78/78 audit and policy tests passed.
- The changed owner/service boundary passed 108 + 122 = 230 assertions under
  GCC Debug, Clang 17 Release C++ `-Werror`, and GCC ASan/UBSan with leak
  detection and bundled SQLite instrumentation.
- The real TLS transport path passed 1,903 assertions independently in those
  same three lanes.
- Completed stress: 30 Debug owner/service iterations, 6,900 assertions; 10
  ASan/UBSan iterations, 2,300 assertions.
- Eight selected source audits passed 212/212 checks, plus both release path and
  release-verifier policy matrices.

An earlier full-suite invocation reached 205/206 before an outer execution limit
while another cloudtainer session held the same legacy sync-domain fixture. The
last test then passed independently at 611/611, and after the competing process
exited the full suite passed 206/206 in one 30.38-second invocation. The
interrupted transcript is retained rather than hidden.

## Severe remaining risks

1. **Production composition gap.** The shipped `anonsync_core` executable still
   does not make the causal SQLite/file/TLS receiver path its sole durable
   replica authority.
2. **Permanent staging starvation.** Published and staged payloads consume
   durable global budgets without stable-principal fairness, protected reserve,
   expiry, dead-letter ownership, causal-stability compaction, or garbage
   collection. Authorized churn can starve unrelated peers indefinitely.
3. **O(history) oracle cost.** The file-effect owner reloads and rehashes retained
   payload history for every public operation. This is valuable as an oracle but
   unsuitable as the final production index.
4. **Listener pressure.** The one-shot accepted owner lacks a bounded production
   accept pool, per-peer handshake budgets, connection-rate policy, graceful
   drain, and persistent overload telemetry.
5. **Identity lifecycle.** Device aggregation does not define enrollment,
   membership-principal identity, key rotation, revocation, recovery, rollback
   protection, or offline-device policy.
6. **Privacy overclaim risk.** Authenticated encrypted transport is not anonymity,
   unlinkability, metadata privacy, endpoint hiding, or traffic-analysis
   resistance.
7. **Build structure.** The project now has roughly 86 literal libraries, 100
   executables, and 209 tests, while `sync_domain.cpp` remains over 15,000 lines.
   Link-target proliferation has not yet produced equivalent semantic
   decomposition.

## Recommended next implementation

Persist a versioned membership-principal quota policy and idempotent operation
reservations, with a protected reserve for other principals. Keep the current
full-history owner as a differential oracle while adding a separately indexed
production owner. Then compose a small bounded listener service around the
one-shot accepted session, with explicit accept/handshake concurrency, pressure
telemetry, graceful drain, retry/dead-letter ownership, and crash injection at
every transport, SQLite, payload, publication, receipt, settlement, and close
frontier.

Safe payload retirement must follow causal stability and explicit rejoin policy,
not wall-clock age alone.

## Nonclaims

This revision does not claim a production daemon, internet deployment safety,
exactly-once network execution, atomicity across independent databases,
complete retry/dead-letter policy, fair scheduling, stable membership
principal, garbage collection, compaction/rejoin, certificate lifecycle,
ThreadSanitizer coverage, formal proof, anonymity, unlinkability, endpoint
hiding, traffic-analysis resistance, or externally trusted signed provenance.
