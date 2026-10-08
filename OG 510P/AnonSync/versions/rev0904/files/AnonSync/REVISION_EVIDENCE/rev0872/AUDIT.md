# AnonSync rev0872 audit summary

## Heart of the mission

AnonSync is building a fail-closed local correctness kernel for replicated
state. Durable operation evidence is the fact owner. Projections, mint maps,
outbox intents, attempt receipts, retry schedules, generations, structural
digests, and liveness observations are subordinate authorities. They must be
exactly scoped, persisted, restored, and re-attested before publication. Time
may revoke authority; it must not manufacture evidence, resurrect an expired
attempt, or silently rewrite history.

## Defect closed

Rev0871 made expiry decisive only relative to the timestamp supplied to one
call. The SQLite owner did not remember time already accepted. A later caller
could therefore move the epoch backwards and make a receipt that had already
expired appear live again after restart or within the same owner.

Rev0872 adds an exact schema-v3 singleton outbox clock row with a digest bound
to folder identity, local actor identity/epoch, and the retained high-water
epoch. Valid scheduler and exact-current-receipt observations advance it in the
same `BEGIN IMMEDIATE` transaction as the lease transition. A lower observation
fails closed. Exact matching expiry commits revocation before returning
`ExpiredClaim`; missing or stale receipts do not gain clock authority.

The clock is deliberately separate from canonical evidence and
`state_generation`. A clock-only observation can change liveness authority
without pretending that a new replicated fact exists.

## Audit/refactor correction

The pure lease validator previously accepted an unreachable durable state:
`dispatch_attempts > 0` with neither an active claim nor positive retry
schedule. The API never mints that row, but restore would accept it and make it
immediately claimable, laundering corrupt history. Rev0872 rejects it in current
restore and exact-v2 migration.

The SQLite owner now shares one cutpoint-field appender between v2 and v3
digest material, reducing duplicated positional encoding while preserving
version-domain separation. Clock SQL is `main.`-qualified, precommit restoration
reattests the staged clock, TEMP shadowing and trigger corruption are tested,
and a self-exec crash probe kills the process after clock UPDATE but before
COMMIT to prove rollback to the prior fence.

## Evidence

- 174/174 registered tests covered with no failures: 173 in the main lane and
  declared serial test 31 in isolation. One uninterrupted invocation is not
  claimed.
- 53/53 registered source/structure audits.
- 2,263 focused checks in GCC 14 Debug, Clang 17 Release `-Werror`, and GCC 14
  ASan/UBSan; bundled SQLite is instrumented in the sanitizer lane.
- 20/20 SQLite-owner stress iterations, 2,820/2,820 repeated checks.
- Revision audits: 23/23 pure lease and 44/44 SQLite owner.
- Clang analyzer: three default-interprocedural production translation units
  plus one explicitly shallow/no-IPA SQLite-owner unit, zero diagnostics.
- Exact patch replay across all 337 active files; 10 modifications, no active
  additions or removals.

## Severe remaining gaps

The fence remembers accepted caller time; it does not authenticate that time.
A far-future observation can persistently deny service. There is no trusted
clock owner, boot identity, cross-reboot monotonicity model, forward-jump
quarantine, uncertainty bound, automatic wake/heartbeat scheduler, receiver
terminal record, receiver idempotency/effect owner, authenticated transport,
key lifecycle, causal compaction, or anonymity/privacy protocol. The reference
SQLite owner also reloads and reprojects full history and is an oracle, not a
production-scale point-read implementation.
