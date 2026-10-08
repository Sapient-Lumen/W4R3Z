# test-run-artifact-standard-kit lane boundaries — 2026-03-21

This note keeps **P-0106 Test Run Artifact Standard Kit** from collapsing into adjacent lanes.

## What this lane is for

This lane is for a **reviewable portable test-run bundle contract** over one executed or imported run.
It should answer:

- what identified the run,
- what selection basis produced it,
- what retry/stress/fail-fast/process model shaped it,
- and whether the resulting bundle is safe to share.

## Keep this distinct from nearby lanes

### Distinct from `cargo-nextest`

Nextest is runner substrate with powerful native recording/replay features.
`P-0106` is the cross-runner artifact contract above it.

### Distinct from JUnit/XUnit exporters

JUnit is an interchange surface.
`P-0106` is about the meaning, exactness, and sensitivity posture of the run artifact itself.

### Distinct from flaky-test detection or benchmarking crates

This lane is not a flake classifier or a benchmark database.
It should preserve retry/stress truth so those systems can reason honestly later.

### Distinct from runtime handoff / incident bundle crates

Runtime crash/support bundles and test-run bundles are adjacent, but not the same thing.
This lane stays specific to **executed test run artifacts**.

## Four truths this lane must keep separate

1. **run identity** — which runner/harness/import route produced this artifact;
2. **selection basis** — which packages/targets/tests/filters/profiles/platforms defined the run;
3. **attempt topology** — retries, fail-fast, stress loops, process model, and setup-script semantics;
4. **bundle sensitivity** — whether outputs/metadata are portable only, internal-shareable, or export-safe.

## Ordinary mistakes future passes must resist

Do not let the archive treat any of the following as interchangeable:

- a libtest-looking harness and the built-in libtest contract,
- a JUnit export and a full-fidelity run bundle,
- a final pass/fail verdict and the full retry/stress topology,
- a portable archive and a public-safe archive,
- console logs and a replayable selection basis.

## Preferred artifact vocabulary

- `run-identity.receipt`
- `selection-basis.receipt`
- `attempt-topology.report`
- `bundle-sensitivity.receipt`
- `testrun-bundle.manifest`

If a future pass adds more detail, it should extend one of those objects before inventing a vague new umbrella.
