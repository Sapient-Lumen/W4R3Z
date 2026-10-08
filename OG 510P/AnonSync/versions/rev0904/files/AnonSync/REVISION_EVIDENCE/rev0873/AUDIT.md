# AnonSync rev0873 audit summary

## Heart of the mission

AnonSync is constructing a fail-closed, evidence-authorized convergence kernel.
Exact canonical operation bytes and exact validated causal evidence are the fact
owners. Projections, counters, mint maps, digests, retry deadlines, lease
receipts, clocks, indexes, and scheduler observations are subordinate
coordination authorities. They may accelerate or constrain work, but they must
never silently manufacture history, widen an actor's authority, revive an
expired attempt, or convert a missing observation into a remembered fact.

The project is not yet an anonymity system merely because it is named AnonSync.
The eventual mission also requires authenticated actor and membership epochs,
receiver effect ownership, bounded dissemination, key lifecycle, metadata threat
modeling, and an explicit privacy adversary.

## Defect closed

Rev0872 durably retained `retry_not_before_epoch` but discarded the accepted
release observation that minted it. The live transition checked the 24-hour
ceiling, yet restart could no longer prove whether a retained deadline came from
a legal delay. The state was operationally useful but evidentially incomplete.

Rev0873 changes the release API from caller-computed absolute deadline to a
relative delay. The policy owner performs bounded, overflow-checked addition and
persists both the deadline and `retry_released_at_epoch`, tagged `Exact`.
Schema v4 binds the pair and its provenance into outbox digest v3 and cutpoint
digest v4. SQL insert, exact update/delete, restore, and staged precommit
attestation all bind the fields.

Historical v1/v2/v3 rows are migrated transactionally without invented history.
A released row whose old schema did not retain the exact observation is labeled
`LegacyUnproven` with release epoch zero. Its exact deadline remains operative;
the next claim clears inherited retry state, and the next release can mint exact
provenance. A conservative migration lower bound is never relabeled as an exact
observation.

## Audit/refactor correction

The rev0872 anti-rollback primitive had no claim, receipt, token, or retry
semantics, yet lived inside the lease translation unit. It is now a separately
owned time-fence library and test. This narrows the policy surface and creates a
place for future boot identity, clock source, uncertainty, and anomaly policy.

A build-graph audit found the separated time-fence test registered with CTest
but absent from sanitizer compile/link target lists. Rev0873 instruments the
library and test in the GCC ASan/UBSan lane. This closes an evidence-coverage
hole rather than merely reorganizing code.

## Evidence

- 175/175 registered tests covered with no failures: 174 in the parallel main
  lane and declared serial test 32 in isolation. One uninterrupted invocation is
  not claimed.
- 53/53 registered source/structure audits.
- Eight focused executables and 2,291 runtime checks in GCC 14 Debug, Clang 17
  Release `-Werror`, and GCC 14 ASan/UBSan. Bundled SQLite is instrumented in the
  sanitizer lane.
- 20/20 SQLite-owner stress iterations and 3,220/3,220 repeated checks.
- Revision audits: 24/24 pure lease and 44/44 SQLite owner.
- Clang analyzer: four default-interprocedural production translation units and
  one explicitly shallow/no-IPA SQLite-owner translation unit, zero diagnostics.
- Exact patch replay across all 340 active files; 13 active changes, including
  three additions and no removals.

## Severe remaining gaps

Caller-supplied epoch time is still not authenticated. The high-water fence
blocks rollback but can turn one bad far-future value into persistent denial of
service. There is no owned clock source, boot/session identity, uncertainty
bound, forward-jump quarantine, recovery protocol, automatic wake scheduler, or
heartbeat owner.

Retry provenance proves when one local deadline was minted, not why a failure
was retryable. There is no failure taxonomy, deterministic backoff/jitter,
maximum attempt age/count, poison state, dead-letter policy, indexed wake queue,
or operator remediation protocol.

There is no terminal authenticated receiver record, idempotent receiver effect
owner, atomic visible-file publication, production peer transport, complete key
lifecycle, authenticated local store, causal stability/compaction, metadata
hiding, or anonymity protocol. The SQLite owner remains a full-history
correctness oracle rather than a production-scale point-read implementation.
