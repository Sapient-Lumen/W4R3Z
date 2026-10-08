# AnonSync rev0906 implementation and release audit

## Mission

AnonSync is an evidence-authorized, crash-consistent, bounded convergence engine.
Exact validated history and explicit live capabilities are authority; summaries,
indexes, clocks, leases, pathnames, transport sessions, counters, and reports may
accelerate or describe work but may not fabricate a newer cutpoint or broader
permission.

## Product increment

Rev0906 adds explicitly bounded `send-batch` and `serve-batch` supervisors over
the existing one-session owners. `send-one` and `serve-one` use the same shared
executors with a bound of one. The sender retains one manifest, existing-only
store set, immutable payload snapshot, fixed endpoint/peer, and TLS context while
creating fresh staged deadlines per session. The receiver retains one listener
and store/TLS set and refreshes anchored membership between sessions. The
maximum is 256 sessions. No daemon, retry/backoff, sleep, or background authority
is introduced.

## Corrected liveness defect

Canonical outbox order by destination and SHA-256 operation ID had become claim
priority. Hash order is deterministic but not causal. A child could repeatedly
sort before its predecessor, receive a correct authenticated evidence-pending
receipt, release its lease, and starve the predecessor. Claim selection now uses
oldest durable `enqueued_generation`, destination, and operation ID while
canonical read/attestation order remains unchanged.

The first scheduler refactor weakened a separate fail-closed property by moving
permanent payload validation behind selection. The full registry exposed that an
oversized committed payload could be bypassed. Final code validates every
matching claimable candidate before any lease, filters availability, then picks
the oldest candidate.

## Validation

- GCC 14.2 Debug complete graph and registry: 226/226.
- Clang 17.0 Debug complete graph and registry: 226/226.
- Clang 17 ASan+UBSan focused owner/service/process lane: 3/3.
- SQLite owner direct result: 250 checks.
- Deployment binding: 27/27.
- Database-open policy: 38/38.
- Bootstrap authority: 25/25.
- Parent rev0905 release: 32/32 under the current verifier.

## Remaining gaps

The largest missing product boundary is one durable supervisor state machine for
scan, evidence minting, catalog exchange, scheduling, transfer, effects, repair,
quarantine, and retention. Complete filesystem semantics, scalable indexed
anti-entropy, safe GC, cross-store protocols, operator recovery, at-rest key
lifecycle, compromise recovery, formal anonymity/metadata goals, external signed
provenance, non-Linux descriptor authority, and ThreadSanitizer coverage remain
outside this revision.

Oldest generation is a repair for the observed local causal starvation, not a
general topological scheduler for arbitrary imported evidence. Batch commands
have a session-count bound and per-session staged deadlines, not a command-wide
absolute runtime budget.
