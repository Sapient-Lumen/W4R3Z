# Schema Reference (Best-Effort)

This is a human-readable index of Concord’s JSON “interfaces”: inputs, outputs, and run-directory artifacts.

Source of truth is the code (Rust structs / Python writers). This page is a convenience map for operators and agents.

Repo-level governance schemas:

- `schemas/spec_ledger.schema.json` (spec-gap/question/assumption ledger)
- `schemas/release_manifest.schema.json` (release manifest contract)
- `schemas/claim_classes.schema.json` (claim taxonomy contract)
- `schemas/claim_register.schema.json` (claim register contract)
- `schemas/risk_register.schema.json` (risk register contract)

## Engine: Task + Match

- **TaskSpec** (input to `gr-engine run-task`)
  - Code: `crates/gr_engine/src/spec.rs` (`TaskSpec`)
  - Examples: `examples/experiments/*.json` (grlab experiment specs), `runs/<run_id>/tasks/*.task.json`
  - Key fields:
    - `schema_version`, `task_id`
    - `world` (`WorldSpec`)
    - `strategy_a`, `strategy_b` (`StrategySpec`)
    - `match_seed`
    - `trace_rounds`
- **MatchArtifact** (output of `gr-engine run-task`)
  - Code: `crates/gr_engine/src/artifact.rs` (`MatchArtifact`)
  - Key fields:
    - `engine_version`, `input_hash`
    - `world_id`, `world_seed`
    - `strategy_a_id`, `strategy_b_id`
    - `seed_streams` (derived RNG streams; determinism debugging)
    - `stats` (payoffs + cooperation rates)
    - optional `trace` (per-round intended/executed/observed actions)

## Engine: Worlds + Strategies (embedded in TaskSpec / ProbeSpec)

- **WorldSpec**
  - Code: `crates/gr_engine/src/spec.rs` (`WorldSpec`)
  - Examples: `examples/worlds/*.json`
  - Current fields (Stage 1/2): `game`, `noise`, `termination`, `seed`
- **StrategySpec**
  - Code: `crates/gr_engine/src/spec.rs` (`StrategySpec`)
  - Examples: `examples/strategies/*.json`
  - Current families:
    - `builtin` (`always_c`, `always_d`, `tit_for_tat`, `win_stay_lose_shift`, `random`)
    - `memory_one`
    - `memory_one_exit`

## Engine: Probes (scenario tests)

- **ProbeSpec / ProbeRegistrySpec / ProbeSuiteSpec**
  - Code: `crates/gr_engine/src/probe.rs`
  - Examples: `examples/probes/*.json`, `examples/probes/registry_*.json`, `examples/probes/suites/*.json`
  - Notes:
    - Each `ProbeSpec` deterministically expands into one or more `TaskSpec` items.
    - `probe_hash` is computed from the canonical serialized spec (independent of JSON formatting).
- **ProbeResultArtifact / ProbeSuiteResultArtifact**
  - Code: `crates/gr_engine/src/probe.rs`
  - Output commands:
    - `gr-engine run-probe`
    - `gr-engine run-probe-suite`

## Engine: Metamorphic checks (oracle-free invariants)

- **MetamorphicCheckSpec / MetamorphicRegistrySpec / MetamorphicSuiteSpec**
  - Code: `crates/gr_engine/src/metamorphic.rs`
  - Examples: `examples/metamorphic/*.json`, `examples/metamorphic/registry_*.json`, `examples/metamorphic/suites/*.json`
- **MetamorphicResultArtifact / MetamorphicSuiteResultArtifact**
  - Code: `crates/gr_engine/src/metamorphic.rs`
  - Output commands:
    - `gr-engine run-metamorphic`
    - `gr-engine run-metamorphic-suite`

## Engine: Snapshots (definition hash bundles)

- **SnapshotSpec / SnapshotArtifact / SnapshotSummary**
  - Code: `crates/gr_engine/src/snapshot.rs`
  - Examples: `examples/snapshots/*.json`
  - Notes:
    - A snapshot can include registries/suites for probes/metamorphic checks/worlds/scorecards.
    - Each included definition is hashed (stable sha256 over canonical JSON bytes).
- **SnapshotRunArtifact**
  - Code: `crates/gr_engine/src/run_snapshot.rs`
  - Output command: `gr-engine run-snapshot`

## Engine: Scorecards (promotion gates + confidence banners)

- **ScorecardDef / ScorecardSpec / ScorecardResultArtifact**
  - Code: `crates/gr_engine/src/scorecard.rs`
  - Output command: `gr-engine run-scorecard`
- **ScorecardRegistrySpec / ScorecardSuiteSpec / ScorecardSuiteResultArtifact**
  - Code: `crates/gr_engine/src/scorecard_suite.rs`
  - Examples: `examples/scorecards/*.json`, `examples/scorecards/suites/*.json`
  - Output command: `gr-engine run-scorecard-suite`

## Engine: Drift diffs (artifacts about artifacts)

Each diff has:
- an input spec (points at “a” and “b” artifacts),
- and an output diff artifact (what changed, and where).

Code map:
- Match diffs: `crates/gr_engine/src/matchdiff.rs`
- Probe diffs: `crates/gr_engine/src/probediff.rs`
- Metamorphic diffs: `crates/gr_engine/src/metadiff.rs`
- Scorecard diffs: `crates/gr_engine/src/scorecarddiff.rs`
- Scorecard-suite diffs: `crates/gr_engine/src/scorecard_suitediff.rs`
- Snapshot diffs: `crates/gr_engine/src/defdiff.rs`
- Snapshot-run diffs: `crates/gr_engine/src/snapshotrun_diff.rs`

## grlab: run directory artifacts

Run directories live under `runs/<run_id>/`.

- `manifest.json` (run plan + definitions)
  - Writer: `grlab/cli.py` (`cmd_run`)
  - Includes: `definitions` (world + strategies hashes), `definitions_hash`, and a list of planned tasks and artifact paths.
- `tasks/*.task.json` (TaskSpec inputs)
  - Writer: `grlab/cli.py` (`cmd_run`)
- `artifacts/*.artifact.json` (MatchArtifact outputs)
  - Producer: `gr-engine run-task` (invoked by `grlab`)
- `queue.sqlite3` (durable queue + artifact index, optional)
  - Code: `grlab/queue.py`
  - CLI: `python3 -m grlab queue-*`
- `report.json` (summary table)
  - CLI: `python3 -m grlab report`
  - Notes: not a provenance authority; see `docs/PROVENANCE.md`.
- `attestation.json` (integrity record)
  - CLI: `python3 -m grlab attest`, `python3 -m grlab verify`
  - Code: `grlab/attest.py`, `grlab/verify.py`
