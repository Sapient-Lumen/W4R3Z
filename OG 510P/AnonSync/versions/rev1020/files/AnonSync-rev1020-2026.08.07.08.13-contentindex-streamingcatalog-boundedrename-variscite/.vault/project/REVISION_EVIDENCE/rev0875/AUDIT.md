# AnonSync rev0875 audit summary

## Mission

AnonSync is an authority-accounting system under crash and partial trust. Exact
canonical evidence owns identity, causality, projection, dispatch, retry, receipt,
and visible effect. Summaries, digests, clocks, leases, indexes, and tests are
subordinate and may never silently mint fact.

## Corrected defect

Rev0874 treated Linux 5.6+ as proof that `/proc/thread-self/ns/time` must be
observable. This cloudtainer runs Linux 6.12.13 without that handle, producing
175/176. Rev0875 makes kernel generation a hint only. A bound identity requires a
successful probe; missing or permission-hidden identity becomes explicit Unknown
evidence and durable `synchronization-unknown` quarantine. Unexpected probe errors
remain fatal.

## Composition evidence

Two independent SQLite owners now prove the ambiguous-delivery frontier: receiver
commit, sender crash before settlement, blocked early retry, fresh claim at
expiry, exact receiver duplicate, fresh-receipt settlement, and stale-receipt
rejection. This is a database-owner integration test, not authenticated transport
or filesystem publication.

## Central mission gap

The newer causal replica/outbox/clock/SQLite owner has no production caller. The
shipped executable follows the older domain/peer-ingress/replay-ledger stack. The
highest-leverage next change is one narrow executable sender→authenticated
receiver→idempotent effect→terminal receipt path using the newer owner.

## Waste

Historical revision evidence is roughly 4,473 files / 40 MB before this revision.
CMake has 66 libraries, 89 executables, and 179 literal tests while major semantic
centers remain giant translation units. Many source audits are lexical. Keep the
full-history owner as oracle, externalize bulk signed evidence, split true semantic
monoliths, simplify build wiring, and shift release authority toward executable
composition, typed negative tests, generated state machines, and differential
oracle checks.

See `TIME_NAMESPACE_CAPABILITY_AUDIT_rev0875.md` for the full analysis and online
research.
