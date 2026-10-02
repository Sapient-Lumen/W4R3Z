# ADR 0239: Bind bounded-range prefixes across daemon restart

Status: accepted with deterministic and genuine direct-UDP/forced-TCP Sandwurm qualification,
2026-08-29.

## Context

ADR 0234 retains exact whole-object prefixes across daemon restart, but deliberately fences every
incomplete range bundle. A range bundle is not a prefix of its target artifact: it is the ordered
concatenation of the target spans missing from one exact local basis under one exact manifest. Its
bytes are unsafe unless the subscriber can prove that a fresh authorized pull derived precisely the
same interpretation.

The durable ATM1 attempt record already has a fixed 96-byte shape. Historical whole-object and
range records use its 32-byte route-key and 64-bit worker fields for forensic carrier binding. Five
record bytes remained reserved and canonically zero.

## Decision

- Canonically encode the exact target, manifest, and basis object records; block size/count;
  reused/missing byte totals; complete basis-offset vector; and ordered missing-range vector.
  Instrumentation-only planner statistics are excluded. Commit that encoding through the fixed
  `initial-v2`/`chunk-v2`/`final-v2` domain-separated BLAKE2b-256 chain with 32 KiB chunks. Every
  chunk commits its prior state, ordinal, and length; the final digest commits total encoded bytes
  and chunk count. This preserves the cryptographic primitive's 64 KiB single-payload ceiling and
  avoids a second plan-sized allocation. The original one-shot v1 construction is retired because
  a useful small-block plan can exceed that ceiling.
- Spend one formerly reserved ATM1 record byte as an explicit binding discriminator. Zero remains
  the historical route/worker interpretation and keeps every old whole-object journal byte
  identical. Value one means the range record's 32-byte field is the plan commitment and its 64-bit
  field is the exact bundle length. ATM1 magic, header, record size, signature domain, and journal
  chain remain unchanged.
- New range attempts always use the plan-bound form. Startup retains only an owner-owned, mode-0600,
  single-link, strict positive prefix shorter than the committed bundle length. A complete bundle,
  zero bytes, missing/unsafe staging, and every legacy route/worker range record are fenced. Whole-
  object recovery is unchanged.
- A fresh pull must reauthorize the publisher, verify its signed candidate HEAD, reverify the exact
  manifest and basis objects, and independently derive the same plan commitment and bundle length.
  A mismatch atomically discards the retained range prefix. An exact match may finish the old signed
  attempt, no-clobber hand the inode to a newly reserved attempt, allocate fresh message/FileId
  identities, and seek to the exact prefix length.
- Full bundle completion, target reconstruction, complete target digest verification, immutable
  commit, accepted-HEAD-last ordering, and explicit activation remain unchanged. Dead jobs, routes,
  workers, epochs, file numbers, FileIds, or request messages are never resurrected.
- `sync-status` adds content-free `range-restart-resumed-attempts` and
  `range-restart-resumed-bytes`, plus the fresh request's `range-message` and exact
  `range-restart-suffix-bytes`. Existing range retained/resumed totals include the same bytes.

## Deterministic evidence

The attempt-store boundary proves that a plan-bound prefix survives startup recovery while a
historical range record is read safely and fenced. A freshly derived different basis commitment
then discards the retained prefix and clears signed active truth.

The full subscriber boundary creates a real range-v1 plan, journals and partially writes its bundle,
runs startup recovery, and starts a distinct authorized pull. That pull reuses the already verified
manifest, derives the identical plan, advances to a fresh attempt/message/FileId, resumes exactly at
half the bundle, receives only the suffix, survives a subsequent ordinary retry, reconstructs the
exact target, accepts the signed generation-2 HEAD last, and leaves no active journal or staging
record. Exact restart-only and aggregate range counters are asserted.

A separate commitment regression encodes more than one 64 KiB hash payload, proves deterministic
output, and proves that changing an offset beyond the first chunk changes the commitment. The
genuine fixture itself exposed and now guards the former one-shot failure
`IoTox domain-separated hash payload is too large`.

## Evidence gate

The separate `sync-file-range-restart-resume` Sandwurm scenario kills the subscriber daemon
after a positive, strict range-bundle prefix; keep guest, Tox, device, and savedata identities stable;
observe startup classify exactly one plan-bound retained range; issue a distinct explicit pull after
authority and range negotiation recover; use fresh attempt/message/FileId identities; retain and
resume the exact same positive byte count; fetch only the suffix; commit the complete target and
manifest; accept the signed HEAD last; and explicitly activate. Direct UDP and forced TCP must each
pass raw verification, compact export, and compact verification before the genuine row is accepted.
Direct-UDP compact proof `pair.xg41pthc` retains/resumes 281,055 bytes and fetches the 767,521-byte
suffix. Forced-TCP compact proof `pair.00992erw` retains/resumes 276,942 bytes and fetches the
771,634-byte suffix. Both pass every required ordering and identity assertion; see
`evidence/2026-08-29-sandwurm-sync-range-restart-resume.md`.

## Consequences

Range-v1 no longer needs to discard trustworthy partial work merely because the local daemon died.
The authority for reuse is the fresh signed HEAD plus exact local plan commitment, never dead
transport state. This adds no wire frame and widens no remote capability.

An interrupted prefix made with the retired one-shot commitment safely mismatches the v2 chain on a
fresh pull and is discarded; this may lose an optimization across that development boundary but
cannot authorize reuse under a different plan.

This does not prove complete-bundle/final-chunk crash recovery, clean-shutdown checkpointing, guest or
kernel power loss, I2P/Tor continuation, repeated late loss, four-plus carrier loss, concurrent
multi-source striping, two physical hosts, or a performance improvement.
