# Definitions (how we keep meaning stable while changing things)

Concord is designed for fast iteration, but its results only remain meaningful if *definitions are explicit artifacts*.

This repo is early-stage; the workflow below is the target shape.

## Principles

- Definitions are versioned: probes, suites, scorecards, holdouts.
- Runs record definition hashes (so “better” claims are scoped correctly).
- New failures become probes (append-only growth, with explicit version bumps).

## Probe artifacts

Stage 2 introduces a versioned `ProbeSpec` format in the engine:
- `ProbeSpec` expands deterministically into a list of `TaskSpec` items.
- `ProbeSpec` has a stable `probe_hash` (hash of the canonical serialized spec), independent of JSON formatting.

Code:
- `crates/gr_engine/src/probe.rs`

## Registries and suites

Also introduced (minimal shells for now):
- `ProbeRegistrySpec`: a versioned list of probes (unique ids)
- `ProbeSuiteSpec`: a versioned list of probe ids (non-empty)
 - `ProbeSuiteResultArtifact`: suite execution output (per-probe results + suite-level pass/fail)
 - `MetamorphicRegistrySpec`: a versioned list of metamorphic checks (unique ids)
 - `MetamorphicSuiteSpec`: a versioned list of metamorphic check ids (non-empty)
 - `MetamorphicSuiteResultArtifact`: suite execution output (per-check results + suite-level pass/fail)

Long-run intent:
- keep a small “frozen” probe suite that changes rarely
- maintain a `holdout` suite that search never touches

## World datasheets (world suites)

World suites are versioned definition artifacts with required datasheet-style metadata to keep “what world are we evaluating in?” explicit and reviewable.

Stage 2 foundation includes:
- `WorldRegistrySpec`: a versioned list of `WorldSpec` worlds (unique ids)
- `WorldSuiteSpec`: a versioned list of world ids + required `WorldDatasheet`

Code:
- `crates/gr_engine/src/worldsheet.rs`

## Metamorphic checks (oracle-free)

Metamorphic relations are definition artifacts too: they encode invariants we expect to hold.

Stage 2 foundation includes a first check:
- `player_swap_symmetry`: in eligible deterministic/no-noise scenarios, swapping player roles should swap per-player stats.
- `scaling_prefix_stability`: for the same seed, extending the match horizon should not change the first N rounds (trace prefix invariance).

Code:
- `crates/gr_engine/src/metamorphic.rs`

## Scorecards (promotion gates + confidence banner)

Scorecards are versioned artifacts that combine multiple suite results into a single “confidence banner”.

Stage 2 foundation includes a minimal `ScorecardSpec` → `ScorecardResultArtifact` runner that:
- requires probe and/or metamorphic suite results (configurable)
- checks that suite definition hashes match an attached snapshot summary (optional gate)
- emits a short banner with counts + pass/fail

Code:
- `crates/gr_engine/src/scorecard.rs`
- `crates/gr_engine/src/scorecard_suite.rs`

## Shrinking (minimization)

Shrinking takes a failing artifact/spec and tries to produce a smaller counterexample.

Stage 2 foundation includes a minimal shrinker:
- `shrink_probe_rounds`: scans for the smallest fixed horizon (rounds) where a probe still fails.
- `shrink_probe_matchups`: shrinks a multi-matchup probe to just the failing matchup.
- `shrink_probe_replications`: scans for the smallest replication count that still fails for a target matchup.
- `shrink_probe_pipeline`: composes matchups → rounds → replications shrinking into one artifact.

Code:
- `crates/gr_engine/src/shrink.rs`

## Result diffs (drift detection)

Result diffs are artifacts too: they help detect and explain behavioral drift across engine changes.

Stage 2 foundation includes:
- `MatchArtifactDiffSpec` → `MatchDiffArtifact` (diff two Stage 1 match artifacts)
- `ProbeResultArtifactDiffSpec` → `ProbeResultDiffArtifact` (diff two probe result artifacts)
- `ProbeSuiteResultArtifactDiffSpec` → `ProbeSuiteDiffArtifact` (diff two probe suite result artifacts)
- `ScorecardResultArtifactDiffSpec` → `ScorecardResultDiffArtifact` (diff two scorecard result artifacts)
- `MetamorphicResultArtifactDiffSpec` → `MetamorphicResultDiffArtifact` (diff two metamorphic result artifacts)
- `MetamorphicSuiteResultArtifactDiffSpec` → `MetamorphicSuiteDiffArtifact` (diff two metamorphic suite result artifacts)
- `ScorecardSuiteResultArtifactDiffSpec` → `ScorecardSuiteDiffArtifact` (diff two scorecard suite result artifacts)
- `SnapshotRunArtifactDiffSpec` → `SnapshotRunDiffArtifact` (diff two snapshot run artifacts; composes nested diffs)

Code:
- `crates/gr_engine/src/matchdiff.rs`
- `crates/gr_engine/src/probediff.rs`
- `crates/gr_engine/src/scorecarddiff.rs`
- `crates/gr_engine/src/metadiff.rs`
- `crates/gr_engine/src/scorecard_suitediff.rs`
- `crates/gr_engine/src/snapshotrun_diff.rs`

## Snapshot diffs

Definition diffs help keep comparisons honest after changing probes/suites.

Stage 2 foundation includes:
- `SnapshotDiffSpec` → `SnapshotDiffArtifact`
- `SnapshotArtifactDiffSpec` → `SnapshotDiffArtifact` (diff prebuilt snapshots)

Code:
- `crates/gr_engine/src/defdiff.rs`

Code:

## Schema evolution

Both `TaskSpec` and `MatchArtifact` carry `schema_version` to support safe evolution without silent drift.

Code:
- `crates/gr_engine/src/spec.rs`
- `crates/gr_engine/src/artifact.rs`

## Definition snapshots (hash bundles)

Stage 2 foundation includes a `SnapshotSpec` → `SnapshotArtifact` helper that bundles hashes of definition artifacts (registries/suites) into a single reproducibility token.
Snapshots can optionally include world definitions and scorecard definitions (single scorecard, or scorecard registry/suite) as hashed defs.

Code:
- `crates/gr_engine/src/snapshot.rs`

## Snapshot runs

`run-snapshot` evaluates the suites embedded in a `SnapshotSpec` and emits one artifact that includes the snapshot hashes plus suite results.

Code:
- `crates/gr_engine/src/run_snapshot.rs`
