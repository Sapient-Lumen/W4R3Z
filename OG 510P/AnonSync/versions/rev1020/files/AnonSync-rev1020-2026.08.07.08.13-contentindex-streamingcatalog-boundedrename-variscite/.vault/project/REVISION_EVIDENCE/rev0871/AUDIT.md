# AnonSync rev0871 audit summary

## Heart of the mission

AnonSync is building a fail-closed local correctness kernel for replicated,
eventually transported state. The durable operation evidence is the fact
owner. Every projection, local mint counter, destination intent, lease,
receipt, retry schedule, generation, and digest is subordinate authority that
must be derived from, bound to, and re-attested against that fact owner before
publication. Time may revoke authority, but must never create it.

## Defect closed

Rev0870 bound settlement to a fresh per-attempt receipt, but its deadline only
controlled reclaim. The old worker could still settle or release after expiry
until a replacement claim committed. Rev0871 makes the interval exclusive:
the exact current receipt and `now < lease_expires_at_epoch` are jointly
required for settlement, retry release, and renewal. Exact deadline equality is
expired.

A heartbeat now extends the same attempt without changing receipt, worker, or
attempt count. It cannot shorten, revive, or exceed the 24-hour cumulative
claim-lifetime ceiling. Persisted active state that exceeds that lifetime is
rejected on restore, closing a state that the API would not mint but the old
loader would accept.

## Audit/refactor correction

Entropy for a new claim is acquired before `BEGIN IMMEDIATE`, so CSPRNG latency
does not occupy SQLite's one-writer slot. Exact outbox lookup uses canonical
`std::lower_bound` rather than repeated linear scans. Claim, renewal, and
release share one exact-prior-row publication helper that advances generation,
recomputes digests, reloads and re-attests the staged database, and only then
commits.

The audit also found a delayed delivery-protocol side branch rewriting the
mutable worktree after an earlier residue scan. It introduced unintegrated wire
APIs, new protocol files, CMake targets, and eventually a declaration/definition
mismatch. That work was not shipped. The final tree was reconstructed from the
sealed parent and the nine-file heartbeat patch, then rebuilt and tested from
scratch. This is both a correctness correction and a scope-economy correction:
an untested authority surface is negative progress.

## Evidence

- 174 registered tests covered with no failures. The main command window
  observed 173 passes and had started the declared serial test; that remaining
  test passed in isolation. No uninterrupted 174-test command is claimed.
- 53/53 registered audits.
- 2,232 focused checks in each of GCC Debug, Clang 17 Release `-Werror`, and GCC
  14 ASan/UBSan; bundled SQLite was instrumented in the sanitizer lane.
- 20/20 SQLite-owner stress runs, 2,260 checks.
- Revision audits: 21/21 pure lease and 40/40 SQLite owner.
- Clang analyzer: three default-interprocedural production translation units
  and one explicitly shallow/no-IPA owner translation unit, zero diagnostics.
- Exact 337-file active-projection replay from rev0870, with nine modifications,
  no additions, no removals.

## Nonclaims

This remains a correctness/reference owner, not a production transport. It has
no authenticated receiver receipt, receiver effect/idempotency owner, trusted
monotonic clock, automatic heartbeat scheduler, wake scheduler, batch path,
production-scale incremental projector, causal-stability/compaction protocol,
remote peer authentication, anonymity protocol, or physical resource proof.
The retry-delay ceiling is proven when the public release API mints state; the
schema does not retain release time, so restore cannot independently reconstruct
that original delay proof.
