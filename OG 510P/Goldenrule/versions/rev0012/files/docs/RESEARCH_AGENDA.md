# Research Agenda (Source-Backed)

This agenda converts current literature and tooling references into an executable program for Concord.

Primary bibliography: [docs/RESEARCH_SOURCES.md](/workspace/docs/RESEARCH_SOURCES.md).

## Strategic Direction

Concord should operate as a deterministic evidence engine for repeated-game science, with three hard boundaries:

1. Rust owns simulation semantics and artifact truth.
2. Formal solvers own mathematically checkable invariants.
3. Python owns orchestration, scheduling, and human-facing reports.

This direction is supported by:
- ZD/memory-one theory and evolutionary caveats (`RS-IPD-001`..`RS-IPD-004`).
- Benchmark ecosystem references (`RS-IPD-005`..`RS-IPD-007`).
- Golden-Rule-adjacent mechanisms: longer memory, fair resistance, partner choice, universalisation, strategy-space completeness, and mixed direct/indirect reciprocity (`RS-GR-001`..`RS-GR-008`).
- Solver and verification interfaces (`RS-FM-001`..`RS-FM-010`).
- Reproducibility operations and benchmarking controls (`RS-OPS-001`..`RS-OPS-005`).

## Core Research Questions

1. Which strategy families remain robust under noise, horizon variation, and opponent shift?
2. Which analytic claims can be proven via SMT/model checking versus only estimated empirically?
3. How much solver disagreement exists on shared properties, and which property classes are unstable?
4. Which orchestration/reporting layers preserve deterministic replay while keeping throughput high?
5. What minimum artifact package is required to reproduce any published claim?

## Golden-Rule Expansion Questions

1. When should a strategy answer betrayal with defection, with exit, or with a repair channel?
2. What minimum memory depth is needed to stay forgiving under noise without becoming exploitable?
3. Which partner-choice or institutional mechanics rescue cooperation that fails in dyadic fixed-pair worlds?
4. Which score metrics distinguish fair resistance to extortion from merely high self-payoff against weak opponents?
5. Which conclusions survive when candidate strategies are evaluated against simpler and richer opponent spaces rather than one fixed space?
6. How should rematch-world canonicalization be recomputed when suspicious starters, noise, or outside-option semantics reopen previously unreachable states?
7. Does the current proxy's cheap invalidation gate — initial `D` support on round one — survive in noisy and endogenous-rematch worlds, or does later reachability dominate there?

## Scientific Posture

1. Favor robustness over leaderboard rank.
2. Favor explicit assumptions over implicit defaults.
3. Favor cross-tool agreement over single-tool confidence.
4. Favor replayable artifacts over narrative summaries.

## Long Tranche Queue

This queue is intentionally broad. It includes theory, formalization, implementation, operations, and publication lanes.

### A) Theory and Spec Tranches

1. Define canonical repeated-game families in spec form (IPD, noisy IPD, finite-horizon variants).
2. Encode memory-one parameter constraints as schema-level invariants.
3. Specify exact noise semantics (actuation vs observation vs both) with deterministic precedence rules.
4. Specify payoff matrix contracts and normalization policy.
5. Define robustness metrics (worst-case regret, CVaR-style tails, holdout delta).
6. Define extortion/generosity operational criteria as computed artifact fields.
7. Specify population-dynamics experiment contract (selection model, mutation schedule, stop criteria).
8. Define deterministic tie-breaking policy for ranking and selection.
9. Add explicit policy for invalid or partially specified strategy definitions.
10. Add claim template requiring source IDs and artifact pointers.
11. Define solver obligation levels per claim type (none, advisory, required).
12. Define model-checking obligation levels for stochastic claims.

### B) Rust Simulation Tranches

1. Refactor world semantics to explicit trait boundaries for deterministic stepping.
2. Add canonical game-state transition logs with hash-chained event IDs.
3. Add strategy-introspection surface for formal translation.
4. Add deterministic stochasticity module with stream partitioning.
5. Add replay executor that validates every logged transition.
6. Add explicit engine conformance tests for filesystem-order independence.
7. Add deterministic floating-point policy (rounding/serialization expectations).
8. Add cross-platform artifact byte-stability tests.
9. Add benchmark fixtures aligned with reference strategy families.
10. Add simulation-safety checks for impossible transitions.
11. Add micro-optimized hot paths with invariant-preserving tests.
12. Add trace compression with losslessness checks.

### C) Formal Solver Tranches

1. Create SMT-LIB emitter for memory-one constraints.
2. Implement Z3 backend adapter with stable query/response artifacting.
3. Implement cvc5 backend adapter with identical artifact contract.
4. Add cross-solver agreement tests for satisfiability class parity.
5. Add model extraction normalizer across solvers.
6. Add unsat-core capture and storage for failing properties.
7. Define solver-timeout policy with deterministic fallback semantics.
8. Add replay runner for solver jobs from saved artifacts.
9. Add property library for symmetry, bounds, and stationary-distribution checks.
10. Add stochastic property handoff to PRISM/STORM for selected world classes.
11. Add discrepancy triage workflow (solver divergence ledger entries + evidence artifacts).
12. Add strict formal gate mode for release-candidate proof obligations.

### D) Probabilistic Model-Checking Tranches

1. Define translation from world spec to model-checking input models.
2. Add PRISM adapter and artifact protocol.
3. Add STORM adapter and artifact protocol.
4. Add probabilistic safety properties (bound violations, convergence behavior).
5. Add expected-value property checks under policy constraints.
6. Add qualitative property checks (eventual cooperation, lock-in states).
7. Add cross-check protocol between simulation estimates and model-checker bounds.
8. Add disagreement dashboard artifact for model-checking vs simulation deltas.
9. Add model-size and state-space metadata to all model-checking artifacts.
10. Add deterministic seed linkage between simulation and model-checking runs.

### E) Python Orchestration Tranches

1. Add DAG-style run-plan abstraction for experiment programs.
2. Add deterministic sharding and resumable chunking.
3. Add priority scheduling policy with stable ordering.
4. Add experiment-template compiler from concise YAML to executable run plans.
5. Add strict input fingerprinting to prevent accidental mixed-definition runs.
6. Add typed FFI layer for Rust kernels via PyO3/maturin.
7. Add queue-level isolation policy for background workers.
8. Add mandatory runtime metadata capture (OS, toolchain, CPU, seed policy).
9. Add failure-capture bundles for one-command replay.
10. Add report builder that separates estimate vs proof vs assumption claims.
11. Add orchestration latency and throughput metrics as first-class artifacts.
12. Add deterministic backfill/retry policies for interrupted runs.

### F) Benchmark and Evaluation Tranches

1. Create canonical baseline suites mirroring classic strategy families.
2. Add adapter layer for importing Axelrod/OpenSpiel strategy definitions where feasible.
3. Add holdout families designed to detect overfit extortion/exploit behaviors.
4. Add robustness sweep matrix across noise, horizon, and opponent distributions.
5. Add ablation suite for memory depth, observation fidelity, and error channels.
6. Add population-dynamics benchmark suite with standardized parameters.
7. Add negative-control suites where no strategy should appear dominant.
8. Add calibration suite for stationary distribution/certification agreement.
9. Add benchmark provenance schema linking source suite, date, and rationale.
10. Add benchmark drift detection and explicit bump protocol.

### G) Statistical and Evidence Tranches

1. Define confidence-reporting policy (interval type, minimum replicates, stopping rules).
2. Add experiment power/planning metadata fields for each claim family.
3. Add bootstrap or exact interval routines with deterministic seeds.
4. Add sequential-analysis guardrails to prevent optional-stopping abuse.
5. Add effect-size-first report templates.
6. Add claim severity levels tied to required evidence strength.
7. Add uncertainty decomposition artifacts (seed variance vs opponent variance vs model variance).
8. Add outlier policy for run failures and heavy-tail outcomes.
9. Add publication table generator from machine-readable evidence bundles.
10. Add claim verifier that checks every statement is backed by artifacts or formal proof IDs.

### H) Reproducibility and Release Tranches

1. Add reproducibility bundle schema v2 with strict required fields.
2. Add one-command bundle verifier for independent replay.
3. Add environment lock capture for Rust and Python dependency graphs.
4. Add periodic dependency tranche workflow with auditable outcomes.
5. Add strict no-network test lane for deterministic CI replay.
6. Add benchmark/performance baselines and drift policy using Criterion + stored baselines.
7. Add nextest profile configurations for quick/full/soak execution classes.
8. Add signed evidence manifest policy for release candidates.
9. Add security-allowlist TTL enforcement with mandatory renewal rationale.
10. Add release note generator that includes assumptions retired/resolved this cycle.

## Immediate Recommendations (Next 2 Cycles)

1. Implement dual-SMT adapter lane (Z3 + cvc5) before expanding strategy search breadth.
2. Promote holdout robustness suites ahead of leaderboard-style reports.
3. Add typed Rust-to-Python FFI for certification-critical hot paths.
4. Add probabilistic model-checking pilot on one small stochastic world.
5. Tighten claim-reporting templates so every claim declares evidence class.

## Golden-Rule-Specific Recommendations (Next 2 Cycles)

1. Add an anti-vampire scorecard that records own payoff, payoff gap, mutual-cooperation recovery, and exploitability under apology/repair channels.
2. Add at least one opt-out / leave-and-rematch world before expanding search over larger strategy families.
   - Current local evidence suggests unilateral exit alone is too easy to game and is not yet a partner-choice benchmark.
   - The new focal rematch proxy shows why this matters: nice-start exit policies become competitive once rematching exists, so world mechanics now look tranche-critical rather than optional.
   - The proxy also compresses the deterministic `memory_one_exit` surface from 243 raw codes to 63 support-distinct families under the current pool, so rematch-enabled search should canonicalize unreachable exit-tail parameters before ranking.
   - Cache that canonicalization with a world-aware key, not a universal entrant-signature key: in the current proxy, opponent/bilateral tremble each collapse to one exact quotient regime, focal tremble to two, and only zero-noise keeps many distinct regimes.
   - Compile a provisional canonicalization planner for each rematch world rather than defaulting to full-signature keying plus a legacy horizon: the current proxy needs only `17/1/2/1` cache buckets and exact horizons `3/2/2/1` across `{none, opponent, focal, bilateral}` noise modes.
3. Add a small longer-memory baseline family (reactive-2 or recency-weighted) to test whether memory depth improves forgiveness without naivete.
4. Add one explicit heterogeneous-space benchmark slice (unconditional/reactive/memory-one or equivalent) before interpreting memory-depth wins.
5. Add one explicit universalisation/Kantian benchmark policy even if it starts as a simple heuristic rather than a solved equilibrium concept.

## Deliverables Produced In This Research Pass

1. Source registry with verified links and per-source implications.
2. Source-backed strategic direction for Rust/Python/formal separation.
3. Broad tranche queue spanning theory, implementation, formal checks, and release hygiene.
