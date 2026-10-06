# Realm-builder-style hermetic component tests (Fuchsia lesson)

DeriveBSD already wants **unit manifests** (`derive.unit`) to be the single declaration surface for:
- capability routing
- contract digests
- resource budgets
- health checks
- supervision / restart receipts

The missing piece to make this *operationally cheap* is a **first-class testing topology** story.

Fuchsia’s *Realm Builder* is a great steal: build a component topology **in code** for tests and route
capabilities explicitly to children. The key ergonomic win is that **dependency injection becomes capability routing**.

References:
- Realm Builder (Fuchsia): https://fuchsia.dev/fuchsia-src/development/testing/components/realm_builder
- Integration testing topologies (Fuchsia): https://fuchsia.dev/fuchsia-src/development/testing/components/integration_testing

## The DeriveBSD goal

Make the “integration test harness” a derived artifact:

- **author**: `derive.testrealm` (or a `tests:` block inside `derive.unit`)
- **compile** → `testrealm.plan` (topology + routes + stubs + fixtures)
- **execute** → `testrealm.receipt` (results + logs/trace refs + contract digests + capability grants used)

This keeps tests from becoming ambient authority snowflakes and lets promotion gates depend on **receipted** test results.

## Design sketch

### 1) Test realms are small topologies

A test realm is a *temporary* topology containing:
- the unit-under-test
- its declared dependencies (real, stubbed, or recorded-replay)
- optional “test-only” capabilities (assertion sinks, fake time, fault injection)

Everything is wired via **capability routes**, not environment variables.

### 2) Dependency injection is routing

For each dependency in `derive.unit` (`uses:`):
- the test declares where the capability comes from:
  - `real:` wire to an actual provider unit
  - `stub:` wire to a test harness component
  - `replay:` wire to a recorded transcript fixture (deterministic)

This can be compiled to `caproute.json` just like production, but with an explicit **test label** so it never ships as-is.

### 3) Contract conformance is a gateable surface

Every routed RPC endpoint is bound to a **contract digest** (already a DeriveBSD theme).

A test realm should record:
- which contract digests were exercised
- which method-level expectations failed
- optional “compat window” policy (old+new digests allowed during transitions)

This enables:
- *conformance suites* for services (“does your new build still speak Contract X?”)
- fleet gating (“don’t roll if contract digest drift breaks consumers”)

### 4) Deterministic fixtures by default

A greenfield OS can bake in one opinionated pattern:

- any “outside world” dependency used by tests must be either:
  - a stub capability, or
  - a replayable transcript captured as evidence

That keeps tests reproducible and makes “works on my laptop” a policy violation.

### 5) Test receipts land in the evidence spine

`testrealm.receipt` should reference:
- build artifact digests under test
- contract digests exercised
- traces/logs (budgeted) captured for failures
- any fault injection knobs used
- resource budgets observed (so tests can feed “learned budgets” lanes)

## Why bake this in now

If the ecosystem grows without this, integration tests will become:
- bespoke scripts,
- with ambient network access,
- with ad-hoc dependency injection,
- and unverifiable “success”.

Realm-builder-style test topologies turn testing into a **reviewable, capability-routed, receipted** artifact lane.
