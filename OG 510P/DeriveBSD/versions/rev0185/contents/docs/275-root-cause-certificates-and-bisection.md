# Automated bisection + root-cause certificates: make regressions cheaper than denial

A greenfield OS can bake in something most ecosystems treat as “hero work”:
**automatic regression localization**.

DeriveBSD has a uniquely good substrate for this:
- artifacts are immutable
- Plans and closures are digestable
- test/fuzz/health results can be receipts

So we should treat “what change introduced this failure?” as an automatable pipeline.

Related: `docs/166-test-receipts-and-promotion-gates.md`, `docs/274-continuous-fuzzing-farm.md`,
`docs/102-emergency-grafts.md`, `docs/112-health-gated-updates.md`.

## The concept: `rootcause.certificate`

A **root-cause certificate** is a signed evidence object emitted by a bisection runner that binds:

- `trigger_receipt_digest`
  - the failing `test.receipt`, `fuzz.receipt`/`crash.case`, or health-gate failure
- `good_plan_digest` / `bad_plan_digest`
  - the known-good and known-bad endpoints
- `search_strategy`
  - binary search / delta debugging / hybrid
- `candidate_set_digest`
  - the ordered set of candidate changes (commits, change-sets, module options)
- `culprit_digest`
  - the smallest change-set (or minimal difference) that reproduces the failure
- `reproduction_receipts`
  - receipts for the runs that prove “good stays good” and “culprit triggers bad”
- pointers to artifacts
  - minimized reproducers, logs, environment snapshots, and diffs

This certificate is *not* a human opinion: it is a reproducible claim backed by receipts.

## Two forms of reduction

### 1) Plan bisection (cheap, first)
Binary search over Plan digests:
- build candidate Plans (using existing caches when possible)
- run the trigger suite (or replay the crash case)
- emit receipts for each step

This quickly narrows “badness” to a small interval.

### 2) Difference minimization (ddmin-style, optional)
Once narrowed, minimize the *difference*:
- config/module option deltas
- change-set contents (patch hunks)
- dependency set changes

Goal: produce a culprit that is small enough to:
- patch quickly
- reason about
- backport safely

## Where this fits operationally

### Regression response flow (default)
1) A failure happens and emits a receipt.
2) Policy spawns a bisection job (in a compartment).
3) Output is a `rootcause.certificate`.
4) The certificate can trigger:
   - an automated rollback decision proposal
   - a targeted graft proposal (`docs/102-…`)
   - a “block promotion” gate until fixed

### Security response flow
For security incidents, the root-cause certificate becomes an input to:
- “is an emergency graft warranted?”
- “what is the smallest safe backport?”
- “do we need to quarantine a component class?”

## UX primitives (what the CLI should feel like)

- `derive blame <receipt>`: show the latest `rootcause.certificate` if present
- `derive bisect --good <plan> --bad <plan> --suite <testsuite>`
- `derive ddmin --case <crash.case> --delta <changeset>`

All commands must produce evidence objects, not free-form logs.

## Anti-footguns

- Bisection jobs should default to:
  - no network
  - strict caps
  - deterministic time/entropy (`docs/197-time-and-rng-authority.md`)
- Never silently “pick a culprit” when the failure is flaky:
  - record flakiness statistics
  - emit a “non-deterministic” certificate variant that *does not blame*

## Open questions

- What is the default bisection budget (time/execs) before we degrade to “human triage”?
- How do we represent multi-cause failures (two changes required) without lying?
- How do we store and visualize culprit graphs across releases (recurring patterns)?
