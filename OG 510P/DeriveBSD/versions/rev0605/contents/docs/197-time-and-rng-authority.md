# Time + entropy as authority (determinism, testing, and replay)

Time and randomness are two of the biggest sources of "ambient impurity":

- builds become unreproducible because they read wall clock
- tests become flaky because they depend on real time passing
- incident artifacts leak secrets via entropy/state
- record/replay debugging needs stable time/entropy semantics

DeriveBSD should treat **wall clock** and **entropy** like other privileged inputs: policy-governed, auditable, and (when needed) virtualizable.


## Secure time sources (optional lane)

For deployments that treat time as a security boundary (public channels, transparency verification), see:
- `200-secure-time-bootstrapping.md` (NTS + Roughtime shaped secure time, with evidence bundles)
- `227-time-discipline-and-trustworthy-timestamps-as-evidence.md` (operational clock discipline: inventories, plans, snapshots, receipts, events)

## Baseline

- **Monotonic time** is always available (cheap, reliable) for internal timeouts.
- **Wall clock** (UTC/local time) is considered an *external input* and can be policy-gated.
- **Entropy** is an external input; deterministic modes exist for builds/tests.

## Lane: time authority grants (optional, but should exist day-1)

A `time.authority.grant` is a leased, signed capability that describes what kind of time/entropy a process may observe:

- wall clock: deny / read / bounded-approx
- monotonic: read (always) with optional offset virtualization
- entropy: real / deterministic / recorded

The grant is bound to a plan + policy decision record.

### Why a grant object?

Because "I can read wall clock" is a form of authority:

- it affects reproducibility
- it affects policy evaluation (expiry windows)
- it can leak scheduling/timing side information across compartments

## Virtual clocks (testing + determinism)

DeriveBSD can support a **virtual clock per compartment** (jail/microVM), defined as an affine transform of a monotonic reference clock.

- deterministic builds: frozen or fixed-offset wall clock
- scenario tests: controllable time progression
- replay capsules: record the clock profile and restore it

Linux time namespaces and Fuchsia clock objects show two concrete design paths:

- time namespaces: per-namespace clock offsets
- clock objects: a privileged maintainer adjusts a shared clock observed by clients

## Entropy modes

- `real`: kernel RNG
- `deterministic`: derived seed bound to the plan digest + policy snapshot (logged)
- `recorded`: record/replay captures the entropy stream into a capsule

The goal is not to eliminate entropy, but to make its use explicit and debuggable.

## Evidence object: time snapshots

For deterministic tests and replay, emit `time.snapshot` objects that bind:

- capset / workload instance identity
- clock profile digest
- entropy mode and seed digest (if deterministic)
- any wall-clock adjustments/slews that occurred

This supports "why did this test behave differently?" style explainability.

## Integration points

- `docs/142-trustworthy-time-roughtime.md`: trustworthy wall clock for *verification* operations
- `docs/188-scenario-tests-multimachine.md`: scenario harness can drive virtual time
- `docs/194-debugging-by-lease-and-replay-capsules.md`: replay capsules should include time/entropy profile
- `docs/195-deterministic-redaction-transforms.md`: deterministic seeds help ensure redaction artifacts are stable

See RFC-0132.

Last updated: 2026-02-24
