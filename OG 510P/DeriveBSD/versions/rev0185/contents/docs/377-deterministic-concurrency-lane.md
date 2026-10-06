# Deterministic concurrency lane (optional): make multithreaded bugs reproducible

Shared-memory concurrency is a reliability tax:
- the same input can produce different interleavings
- crashes can be non-reproducible
- tests pass until they don’t

Greenfield advantage: DeriveBSD can treat **deterministic scheduling** as an *optional lane* that plugs into the evidence spine and replay workflows.

This is not “make everything deterministic forever.” It is:
- a **debug/test mode**
- a **receipt-bearing knob**
- with explicit costs (performance, scheduling constraints)

References:
- DMP (Deterministic Multiprocessing): https://homes.cs.washington.edu/~luisceze/publications/asplos004-devietti.pdf
- Dthreads (Efficient deterministic multithreading): https://people.cs.umass.edu/~emery/pubs/dthreads-sosp11.pdf

## Where determinism helps most

### 1) Replay capsules get smaller

If thread interleavings are deterministic, record/replay can focus on:
- inputs
- I/O boundaries
- nondeterministic authorities (time, RNG, network)

That reduces capture surface area and makes “reproduce this crash” cheaper.

See: `docs/194-debugging-by-lease-and-replay-capsules.md`, `docs/197-time-and-rng-authority.md`.

### 2) CI can catch heisenbugs without “1000 runs”

A deterministic scheduler lane makes it feasible to:
- run the same test N times and expect identical behavior
- bisect regressions with less noise
- turn flaky tests into actionable diffs

### 3) Fuzzing + determinism is a force multiplier

Fuzzers find inputs.
Determinism makes the resulting failure reproducible.

DeriveBSD can bind this lane to the existing parser registry story:
- fuzz targets reference `parser.registry` ids
- failures produce replayable artifacts (inputs + schedule receipts)

See: `docs/376-parser-surface-registry-and-fuzz-gates.md`, `docs/274-continuous-fuzzing-farm.md`.

## DeriveBSD mapping (proposal)

### Deterministic execution as an explicit authority

Determinism is an operational mode that changes semantics.
Treat it like other “powerful knobs”:
- enabled by policy
- bounded by leases
- produces receipts

A simple shape:
- input: `sched.policy` (select deterministic mode, scope, limits)
- output: `sched.receipt` (what mode ran, and what was enforced)

(These are concepts; schemas can follow once the lane is proven.)

### Scope options (pragmatic)

- **per-process**: run a test binary under deterministic threading
- **per-jail**: deterministic scheduling inside a service jail
- **per-microVM**: deterministic scheduling inside a debug microVM

DeriveBSD can start with the least invasive scope (per-process) and expand.

### Interaction with time and I/O

Determinism is only useful if the remaining nondeterminism is explicit:
- time/RNG are already modeled as authorities (`docs/197-time-and-rng-authority.md`)
- network and filesystem side effects should be brokered or captured for replay

## Guardrails

- Deterministic mode must be **opt-in** and **visible** (receipted), to avoid “works in deterministic mode, fails in prod” surprises.
- Deterministic mode must not silently widen authority.
- Deterministic mode must have a clear exit strategy: tests that rely on it should be labeled.

Last updated: 2026-02-27r107
