# Concord (build in progress)

Concord is an **autonomy-first research lab** for discovering and stress-testing reciprocal strategies across repeated games and richer social dilemmas.

The current source-of-truth specs live in:
- `Original-Starting-Place/00_README.md`
- `Original-Starting-Place/01_Vision_and_Definitions.md`
- `Original-Starting-Place/02_Core_Architecture.md`
- `Original-Starting-Place/03_WorldSpec.md`
- `Original-Starting-Place/04_StrategySpec_and_DSL.md`
- `Original-Starting-Place/05_GoldenRule_Scorecard.md`
- `Original-Starting-Place/06_Red_Team_and_Adversaries.md`
- `Original-Starting-Place/07_Search_and_Optimization.md`
- `Original-Starting-Place/08_Experiment_Orchestration.md`
- `Original-Starting-Place/09_Rust_Engine.md`
- `Original-Starting-Place/10_Reproducibility_Nix.md`
- `Original-Starting-Place/11_Background_Reading.md`
- `Original-Starting-Place/12_GoldenRule_DeepDive.md`
- `Original-Starting-Place/13_TestEnvironments_ProbeSuite.md`
- `Original-Starting-Place/14_Institutions_and_Realism.md`

Implementation docs:
- `docs/README.md` (index)
- `docs/BUCKET.md` (big-ticket gaps + next bricks)

## Stages (short)

See `docs/STAGES.md` for the concrete roadmap.
See `docs/DEFINITIONS.md` for how probes/suites are treated as versioned artifacts.

Stage 1 (implemented here) is intentionally small:
- deterministic Iterated Prisoner’s Dilemma (IPD) match simulator in Rust
- built-in strategies + memory-one strategies
- task-based JSON I/O with atomic artifact writes
- trace semantics: intended vs executed vs observed actions; artifacts record seed streams
- minimal Python orchestrator that runs/resumes match matrices

## Quick start (Stage 1)

Build the engine:
- `cargo build -p gr_engine --bin gr-engine`

Run a single probe (Stage 2 foundation; emits a probe result artifact):
- `target/debug/gr-engine run-probe --probe <probe.json> --out <probe_result.json> --pretty`

Run a metamorphic check (Stage 2 foundation; oracle-free invariants):
- `target/debug/gr-engine run-metamorphic --spec <metamorphic.json> --out <metamorphic_result.json> --pretty`

Run a metamorphic suite (Stage 2 foundation; batch metamorphic checks as an artifact):
- `target/debug/gr-engine run-metamorphic-suite --registry <registry.json> --suite <suite.json> --out <suite_result.json> --pretty`

Run a probe suite (Stage 2 foundation; batch probes as an artifact):
- `target/debug/gr-engine run-probe-suite --registry <registry.json> --suite <suite.json> --out <suite_result.json> --pretty`

Shrink a failing probe (Stage 2 foundation; minimization):
- `target/debug/gr-engine shrink-probe-rounds --spec <shrink.json> --out <shrink_artifact.json> --pretty`
- `target/debug/gr-engine shrink-probe-matchups --spec <shrink.json> --out <shrink_artifact.json> --pretty`
- `target/debug/gr-engine shrink-probe-replications --spec <shrink.json> --out <shrink_artifact.json> --pretty`
- `target/debug/gr-engine shrink-probe-pipeline --spec <shrink.json> --out <shrink_artifact.json> --pretty`

Build a definition snapshot (hashes for registries/suites):
- `target/debug/gr-engine snapshot --spec <snapshot.json> --out <snapshot_artifact.json> --pretty`
  - example: `examples/snapshots/smoke.json`

Run a snapshot (definitions + suites -> one artifact):
- `target/debug/gr-engine run-snapshot --spec <snapshot.json> --out <snapshot_run.json> --pretty`

Run the smoke scorecard suite over the smoke snapshot run:
- `target/debug/gr-engine run-snapshot --spec examples/snapshots/smoke.json --out /tmp/snapshot_run.json --pretty`
- `target/debug/gr-engine run-scorecard-suite --registry examples/scorecards/registry_smoke.json --suite examples/scorecards/suites/smoke.json --snapshot-run /tmp/snapshot_run.json --out /tmp/scorecard_suite.json --pretty`

Run a scorecard (confidence banner over suite results):
- `target/debug/gr-engine run-scorecard --spec <scorecard.json> --out <scorecard_result.json> --pretty`

Run a scorecard suite over a snapshot run:
- `target/debug/gr-engine run-scorecard-suite --registry <registry.json> --suite <suite.json> --snapshot-run <snapshot_run.json> --out <scorecard_suite_result.json> --pretty`

Diff two snapshots (definition diff):
- `target/debug/gr-engine diff-snapshots --spec <defdiff.json> --out <defdiff_artifact.json> --pretty`

Diff two snapshot artifacts (no rebuild):
- `target/debug/gr-engine diff-snapshot-artifacts --a <snapshot_artifact_a.json> --b <snapshot_artifact_b.json> --out <diff.json> --pretty`

Diff two probe result artifacts:
- `target/debug/gr-engine diff-probe-artifacts --a <probe_result_a.json> --b <probe_result_b.json> --out <diff.json> --pretty`

Diff two match artifacts (Stage 1 drift diff):
- `target/debug/gr-engine diff-match-artifacts --a <match_a.json> --b <match_b.json> --out <diff.json> --pretty`

Diff two probe suite result artifacts:
- `target/debug/gr-engine diff-probe-suite-artifacts --a <suite_result_a.json> --b <suite_result_b.json> --out <diff.json> --pretty`

Diff two metamorphic result artifacts:
- `target/debug/gr-engine diff-metamorphic-artifacts --a <metamorphic_result_a.json> --b <metamorphic_result_b.json> --out <diff.json> --pretty`

Diff two metamorphic suite result artifacts:
- `target/debug/gr-engine diff-metamorphic-suite-artifacts --a <suite_result_a.json> --b <suite_result_b.json> --out <diff.json> --pretty`

Diff two scorecard result artifacts:
- `target/debug/gr-engine diff-scorecard-artifacts --a <scorecard_a.json> --b <scorecard_b.json> --out <diff.json> --pretty`

Diff two scorecard suite result artifacts:
- `target/debug/gr-engine diff-scorecard-suite-artifacts --a <suite_a.json> --b <suite_b.json> --out <diff.json> --pretty`

Diff two snapshot run artifacts (composed drift diff):
- `target/debug/gr-engine diff-snapshot-run-artifacts --a <snapshot_run_a.json> --b <snapshot_run_b.json> --out <diff.json> --pretty`

Run a small experiment (resumable):
- `python3 -m grlab run examples/experiments/ipd_smoke.json`
- `python3 -m grlab run examples/experiments/ipd_smoke.json --plan-only --enqueue`

Durable queue (Stage 3 foundation; safe kill/resume):
- `python3 -m grlab queue-init runs/<run_id>`
- `python3 -m grlab queue-import runs/<run_id>`
- `python3 -m grlab queue-status runs/<run_id>`
- `python3 -m grlab queue-reconcile runs/<run_id>`
- `python3 -m grlab queue-index runs/<run_id>`
- `python3 -m grlab queue-list runs/<run_id> --status error --limit 50`
- `python3 -m grlab queue-work runs/<run_id> --workers 4 --retry-errors --max-attempts 5 --retry-backoff-seconds 30 --task-timeout-seconds 600`
- `python3 -m grlab afk runs/<run_id> --workers 4 --retry-errors --max-attempts 5 --retry-backoff-seconds 30 --task-timeout-seconds 600`
- `python3 -m grlab watch runs/<run_id> --interval 2 --errors`

Summarize a run:
- `python3 -m grlab report runs/<run_id>`
- `python3 -m grlab verify runs/<run_id>`
- `python3 -m grlab defdiff runs/<run_a> runs/<run_b>`
- `python3 -m grlab diff-match --a <match_a.json> --b <match_b.json> --out <diff.json> --pretty`
- `python3 -m grlab trace --diff --a <match_a.json> --b <match_b.json> --pretty`
- `python3 -m grlab compare runs/<run_a> runs/<run_b>`
- `python3 -m grlab frontier runs/<run_id>`
- `python3 -m grlab reproduce runs/<run_id> --task-id <task_id>`
- `python3 -m grlab quick --world <world.json> --strategy-a <a.json> --strategy-b <b.json> --match-seed 1 --out <artifact.json>`
- `python3 -m grlab redact runs/<run_id> --out-dir <redacted_dir> --public`
- `python3 -m grlab export runs/<run_id> --out <bundle.tar.gz> --public`
- `python3 -m grlab export runs/<run_id> --out <bundle.tar.gz> --internal`
- `python3 -m grlab attest runs/<run_id> --out <attestation.json> --include-queue-db`
- `python3 -m grlab report runs/<run_id> --use-db`

Validate a run directory:
- `python3 -m grlab validate runs/<run_id> --check-queue`
