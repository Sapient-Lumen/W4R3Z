# Research Agenda (Source-Backed)

This agenda converts current literature and tooling references into an executable program for Concord.

Primary bibliography: [docs/RESEARCH_SOURCES.md](RESEARCH_SOURCES.md).

## Strategic Direction

Concord should operate as a deterministic evidence engine for repeated-game science, with three hard boundaries:

1. Rust owns simulation semantics and artifact truth.
2. Formal solvers own mathematically checkable invariants.
3. Python owns orchestration, scheduling, and human-facing reports.

This direction is supported by:
- ZD/memory-one theory and evolutionary caveats (`RS-IPD-001`..`RS-IPD-004`).
- Benchmark ecosystem references (`RS-IPD-005`..`RS-IPD-007`).
- Golden-Rule-adjacent mechanisms: longer memory, fair resistance, partner choice, restart/rematch contract design, search-friction / market-thickness effects, universalisation, strategy-space completeness, mixed direct/indirect reciprocity, group-boundary competition / mobility, collective-vs-individual reputation scope, and reputation-governance topology / centralized-score caution, monitoring / need-burden economics, and sanction metanorm / enforcer-governance design, speech-act governance, risk / fallback design, concurrent-portfolio / cross-lane-linkage design, and encounter-topology / homophily / rewiring design, plus harm-accounting / delayed-damage / threshold-semantics design, and private-solution / outside-option / self-reliance design (`RS-GR-001`..`RS-GR-198`).
- Solver and verification interfaces (`RS-FM-001`..`RS-FM-010`).
- Reproducibility operations and benchmarking controls (`RS-OPS-001`..`RS-OPS-005`).

## Core Research Questions

1. Which strategy families remain robust under noise, horizon variation, and opponent shift?
2. Which analytic claims can be proven via SMT/model checking versus only estimated empirically?
3. How much solver disagreement exists on shared properties, and which property classes are unstable?
4. Which orchestration/reporting layers preserve deterministic replay while keeping throughput high?
5. What minimum artifact package is required to reproduce any published claim?
6. Which rematch-world effects are simple dead-time taxes versus genuine matching-market / assortment effects?

## Golden-Rule Expansion Questions

1. When should a strategy answer betrayal with defection, with exit, or with a repair channel?
2. What minimum memory depth is needed to stay forgiving under noise without becoming exploitable?
3. Which partner-choice or institutional mechanics rescue cooperation that fails in dyadic fixed-pair worlds?
4. Which score metrics distinguish fair resistance to extortion from merely high self-payoff against weak opponents?
5. Which conclusions survive when candidate strategies are evaluated against simpler and richer opponent spaces rather than one fixed space?
6. How should rematch-world canonicalization be recomputed when suspicious starters, noise, or outside-option semantics reopen previously unreachable states?
7. Does the current proxy's cheap invalidation gate — initial `D` support on round one — survive in noisy and endogenous-rematch worlds, or does later reachability dominate there?
8. How should rematch worlds assign roles, rematch state, and seat symmetry once asymmetric strategies or asymmetric environments are admitted?
9. Which conclusions about leave/rematch robustness survive once rematch delay or search friction stops being a hidden constant and becomes a swept world parameter?
10. How should endogenous rematch worlds separate rematch delay from market thickness / matching efficiency so faster rematching is not modeled only as fewer dead rounds?
11. Which rematch-world rank changes are genuine within-match improvements versus raw occupancy / tempo artifacts?
12. Which conclusions survive when the interaction lane changes from simultaneous play to disclosed-action / leader-follower play with explicit move-order asymmetry (`RS-GR-133`)?
13. In partner-choice worlds, how much apparent cooperation is observable reputation play versus unobserved partner-maintenance help (`RS-GR-134`)?
14. Which reputation results survive when assessment is private and update priority rules differ (`RS-GR-135`)?
15. Which cooperation claims survive when sparse observation and fading / `Unknown` reputation states are modeled separately rather than as one imperfect-information knob (`RS-GR-136`)?
16. Which gossip regimes stabilize cooperation under private reputation, and when does copied judgment become a distortion rather than a help (`RS-GR-137`)?
17. How much do conclusions about forgiveness or deterrence depend on binary versus graded reputation states and one-step versus flip-style updates (`RS-GR-141`)?
18. When sanctions fade or records expire, does visible proximity to rehabilitation create end-of-sentence opportunism that would disappear under hidden or stochastic expiry (`RS-GR-142`)?
19. In hybrid human/AI reciprocity worlds, how much changes because artificial agents alter reputation consensus or are judged under different assessment rules than humans (`RS-GR-143`, `RS-GR-145`)?
20. In hybrid reputation worlds, what happens when failures attach to an individual agent versus a model family, provider, or all AIs (`RS-GR-144`, `RS-GR-145`)?
21. How much of a reputation result is really about opinion synchronization / consensus infrastructure rather than about the action policy itself (`RS-GR-150`)?
22. When agents weigh private experience against public reputation differently, which worlds stabilize cooperation and which drift into polarization or fragmentation (`RS-GR-151`)?
23. When does a centralized scalar score reduce trust and cooperation relative to revisable local reputation (`RS-GR-152`)?
24. How much of an apparent trust gain is really a monitoring-economy change caused by costly observation or reduced evidence transfer rather than a better reciprocity policy (`RS-GR-153`, `RS-GR-154`)?
25. How often are non-help events misread because worlds collapse unwillingness, inability, overload, and recipient burden into one evaluative channel (`RS-GR-155`, `RS-GR-156`)?
26. Which cooperation results depend on local metanorms about whether observers should ignore, gossip about, exclude, confront, or materially punish norm violations (`RS-GR-166`, `RS-GR-167`, `RS-GR-168`)?
27. How much of a sanction result is really driven by enforcer incentives, retaliation exposure, or higher-order oversight rather than by the base reciprocity policy on targets (`RS-GR-168`, `RS-GR-169`, `RS-GR-170`, `RS-GR-171`)?

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
13. Define rematch-world role-assignment and persistent-state contracts.
14. Define outside-option timing / rematch-delay policy as explicit world semantics rather than a hidden benchmark constant.
15. Define separate world fields for rematch delay, market thickness / matching efficiency, and unmatched-state accounting.
16. Define explicit visibility / observability fields for help channels so reputation-facing help can be separated from hidden partner-maintenance help.
17. Define explicit reputation-update semantics (public/private state, donor/recipient update targets, conflict priority rule, and latency/noise posture).
18. Define separate world fields for sparse observation versus fading / `Unknown` reputation states.
19. Define explicit gossip-diffusion semantics (cadence, fan-in, trust/merge rule, and independent-judgment posture).
20. Define explicit agent-type assessment semantics for hybrid worlds (shared versus class-specific norms; action-only versus intention-aware judgment).
21. Define explicit reputation-scope semantics for hybrid worlds (individual, family, provider, or category-level spillover).
22. Define explicit reputation-governance-topology semantics (private opinions, synchronization cadence, source weighting, public consensus, or centralized score authority).
23. Define explicit direct-experience override and fresh-behavior repair semantics for any centralized-score lane.
24. Define explicit sanction metanorm semantics (admissible observer responses, non-enforcement obligations, and anti-social / excessive-punishment treatment).
25. Define explicit enforcer-governance semantics (sanctioner incentives, retaliation exposure, and higher-order oversight / replacement rights).

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
13. Add an engine-level rematch world with explicit role policy, rematch delay, post-rematch state reset semantics, and explicit matched/unmatched market accounting.

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
11. Add a static Rust surface inventory + Python-shadow workflow so blocked toolchains still leave deterministic navigation artifacts and bounded provisional progress.

## Immediate Recommendations (Next 2 Cycles)

1. Implement dual-SMT adapter lane (Z3 + cvc5) before expanding strategy search breadth.
2. Promote holdout robustness suites ahead of leaderboard-style reports.
3. Add typed Rust-to-Python FFI for certification-critical hot paths.
4. Add probabilistic model-checking pilot on one small stochastic world.
5. Tighten claim-reporting templates so every claim declares evidence class.
6. Treat Rust-blocked sessions as a first-class workflow: regenerate the static Rust surface inventory, advance Python shadow checks, and defer runtime claims rather than pausing the program.

## Golden-Rule-Specific Recommendations (Next 2 Cycles)

1. Add an anti-vampire scorecard that records own payoff, payoff gap, mutual-cooperation recovery, and exploitability under apology/repair channels.
2. Add at least one opt-out / leave-and-rematch world before expanding search over larger strategy families.
   - Current local evidence suggests unilateral exit alone is too easy to game and is not yet a partner-choice benchmark.
   - The new focal rematch proxy shows why this matters: nice-start exit policies become competitive once rematching exists, so world mechanics now look tranche-critical rather than optional.
   - The proxy also compresses the deterministic `memory_one_exit` surface from 243 raw codes to 63 support-distinct families under the current pool, so rematch-enabled search should canonicalize unreachable exit-tail parameters before ranking.
   - Cache that canonicalization with a world-aware key, not a universal entrant-signature key: in the current proxy, opponent/bilateral tremble each collapse to one exact quotient regime, focal tremble to two, and only zero-noise keeps many distinct regimes.
   - Compile a provisional canonicalization planner for each rematch world rather than defaulting to full-signature keying plus a legacy horizon: the current proxy needs only `17/1/2/1` cache buckets and exact horizons `3/2/2/1` across `{none, opponent, focal, bilateral}` noise modes.
   - Expose rematch delay / search friction as an explicit world field and rerun leave/rematch claims across a delay sweep; the current proxy already shows delay acts like a real tax on exit-heavy policies.
   - Expose rematch role policy as world data, not prose; once asymmetric strategies or environments are admitted, fixed-role and role-swapped companion runs should both exist.
   - Require occupancy accounting in rematch reports (`matched_round_share`, `dead_round_share`, `in_match_avg_payoff`) so welfare gains are not confounded with mere increases in time spent productively matched.
   - Do not treat temporary-partnership persistence and rematch/search delay as one generic friction knob; future worlds should expose match persistence/separation separately from rematch dead-time.
   - Publish `avg_match_length` or an equivalent turnover metric in every rematch-world benchmark, because the same nominal delay becomes a much larger occupancy tax when partnerships churn quickly.
   - Publish paired rematch leaderboards (`overall_avg_payoff` and occupancy-normalized `in_match_avg_payoff` or equivalent); if only the raw leaderboard flips, treat that as an occupancy/tempo artifact until stronger evidence appears.
   - Do not report a single-delay rematch winner without a delay sweep, pairwise crossover thresholds, or an explicit robustness interval over the deployed friction band.
   - Before widening rematch delay sweeps, publish a compact live contender artifact (dominated policies, tested-band leader set, winner margins, and frontier intervals where needed); in the current proxy there are multiple below-top pairwise flips but only one tested leader flip.
   - Attach winner-certification metadata to the top-vs-runner-up gap; if a leader flip fails a paired-seed uncertainty gate, keep it provisional rather than promoting it into a stable ranking claim.
  - Add budget-aware winner triage for unresolved panels: publish an approximate additional-budget-to-certify field, and allow a near-tie / indifference label when certifying a microscopic flip would require orders of magnitude more paired seeds than the baseline budget.
   - Declare a smallest effect of interest for rematch top gaps and publish practical-equivalence status alongside winner certification; a statistically certified winner can still be too small to matter, and an uncertified flip can already be a practical tie.
   - Publish per-panel delta frontiers (`largest_material_delta_supported`, `smallest_equivalence_delta_supported`) so future inheritors can apply any declared smallest effect of interest without rerunning or storing bulky multi-delta classification tables.
   - Publish a compact delta-budget frontier over the plausible smallest-effect band so inheritors can see how indifference-zone choices change unresolved residue and extra paired-seed closure cost without hiding budget pressure inside one arbitrary `delta`.
   - Publish leader-gap hazard bands or an equivalent no-knife-edge buffer over the plausible smallest-effect band; in the current proxy, dense-grid closure cost above `10000` extra paired seeds is confined to eight tiny neighborhoods around observed top-gap means, so coarse delta grids alone can miss fragile threshold choices.
   - Publish budget-admissible delta bands (plus one anchor per band) for declared extra-budget caps; in the current proxy, a `+10` paired-seed cap leaves only two admissible bands over `[0, 0.02]`, so future inheritors should choose from stable intervals rather than naked knife-edge deltas.
3. Add a small longer-memory baseline family (reactive-2 or recency-weighted) to test whether memory depth improves forgiveness without naivete.
4. Add one explicit heterogeneous-space benchmark slice (unconditional/reactive/memory-one or equivalent) before interpreting memory-depth wins.
5. Once leave/rematch is live, rerun TFT / WSLS / Grim inside one noisy voluntary-repetition slice before assuming fixed-dyad classics transfer (`RS-GR-132`).
6. Add one explicit simultaneous-vs-disclosed-action companion lane and publish move-order / visibility metadata before claiming institutional robustness (`RS-GR-133`).
7. In the first leave/rematch + reputation lane, split observable-help metrics from unobserved partner-maintenance metrics so performative reciprocity cannot hide inside one cooperation number (`RS-GR-134`).
8. In the first private-reputation lane, publish the assessment-update rule explicitly rather than treating reputation as an on/off switch (`RS-GR-135`).
9. In the first private-reputation lane, keep sparse observation and fading / `Unknown` reputation states as separate knobs, and compare at least one punishment-off / punishment-on pair before generalizing enforcement claims (`RS-GR-136`).
10. If gossip is enabled, publish gossip cadence / fan-in / trust-weight / merge semantics and compare against a no-gossip baseline before treating convergence as a property of reputation itself (`RS-GR-137`).
11. In any sanction / exclusion lane, publish rehabilitation and re-entry semantics (duration, re-entry rule, apology availability, and signal visibility / trackability) before generalizing punishment results (`RS-GR-138`, `RS-GR-139`).
12. If apology, emotion, or other repair signals are enabled, publish signal vocabulary / timing / audience semantics plus one no-signal baseline and one follow-through or abuse metric (`RS-GR-139`, `RS-GR-140`).
13. In the first richer reputation lane, publish the reputation alphabet and transition granularity explicitly, and keep one binary baseline before generalizing from graded/ternary reputation (`RS-GR-141`).
14. If exclusion or trust enforcement uses bounded memory or expiring records, publish record-retention length and rehabilitation legibility, and compare at least one visible-countdown versus hidden-countdown variant before generalizing from exclusion (`RS-GR-142`).
15. Add one explicit universalisation/Kantian benchmark policy even if it starts as a simple heuristic rather than a solved equilibrium concept.
16. Before any hybrid human/AI reciprocity benchmark, publish agent-type assessment symmetry and keep one human-only baseline (`RS-GR-143`, `RS-GR-145`).
17. In any hybrid reputation world, publish whether failures attach to individuals, model families, providers, or all AIs, and compare against at least one no-class-spillover baseline (`RS-GR-144`, `RS-GR-145`).
18. In any heterogeneous-resource or public-goods lane, publish whether inequality reflects luck, merit, endowment, productivity, or aligned combinations, and compare at least one luck-framed versus merit-framed inequality baseline before generalizing from cooperation shifts (`RS-GR-161`, `RS-GR-162`).
19. In any scarce-help, redistribution, or collective-good lane, publish allocator authority and allocation rule (equality / need / merit / reciprocity-history or equivalent), and compare at least one automatic baseline against one planner or third-party-allocation lane before generalizing from prosocial performance (`RS-GR-163`, `RS-GR-164`, `RS-GR-165`).
18. In any trust or reputation lane, publish monitoring cadence / cost and evidence-transfer friction, and keep one low-friction baseline before attributing gains to reciprocity policy (`RS-GR-153`, `RS-GR-154`).
19. In any helping or partner-choice lane, publish willingness-versus-ability semantics and recipient need / burden metadata before interpreting refusal, exclusion, or blame as principled reciprocity (`RS-GR-155`, `RS-GR-156`).
20. In any reputation, sanction, or leave/rematch lane, publish identity-reset rights, newcomer priors, and history-carryover semantics before interpreting resilience to bad actors or suspicion of newcomers as policy quality (`RS-GR-157`, `RS-GR-158`).
21. In any cooperation or reputation lane, publish actor identifiability separately from action visibility, including the type and timing of identity cues, before treating disclosure effects as evidence of stronger reciprocity (`RS-GR-159`, `RS-GR-160`).

22. In any communication-enabled lane, publish whether preplay commitments, pledges, or vows exist and whether later action scoring is conditional on commitment state; compare at least one no-commitment baseline against one explicit commitment-stage lane (`RS-GR-172`, `RS-GR-173`, `RS-GR-175`).
23. In any repair / communication lane, publish the cost and scoring semantics of post-hoc self-signals, and keep at least one no-signal or signal-cost comparison so cheap impression management does not masquerade as moral improvement (`RS-GR-174`, `RS-GR-175`).
24. In any stochastic helping, mutual-aid, or public-goods lane, publish shock structure (individual vs correlated vs collective), shock timing, and pooling / side-transfer rights, and compare at least one idiosyncratic-risk baseline against one shared-shock lane before attributing gains to reciprocity (`RS-GR-176`, `RS-GR-177`).
25. In any aid, fallback, or solidarity lane, publish formal-insurance availability, ex-ante eligibility, unused-protection knowledge, and whether informal help tops up or substitutes for formal protection before interpreting generosity shifts as moral improvement (`RS-GR-178`, `RS-GR-179`).
26. In any repeated, helping, or allocation lane with multiple simultaneous obligations, publish partner-portfolio width, same-partner versus different-partner concurrency, and per-lane payoff salience; keep at least one single-channel baseline before attributing gains to reciprocity (`RS-GR-180`, `RS-GR-181`).
27. In any concurrent or multi-domain reciprocity lane, publish whether channels are isolated, intentionally linked, or subject to crosstalk, and keep at least one channel-isolated baseline beside any spillover lane before interpreting retaliation or forgiveness results (`RS-GR-181`, `RS-GR-182`).
28. In any networked reciprocity, trust, or helping lane, publish encounter topology, degree heterogeneity / assortativity, and whether cooperative or defective roles can concentrate at hubs or bridges; keep at least one well-mixed or degree-neutral baseline before treating cooperation gains as policy wins (`RS-GR-183`, `RS-GR-184`).
29. In any dynamic-network or endogenous-relationship lane, publish tie-formation, tie-dissolution, homophily, and prior-acquaintance rules, and keep at least one forced-mixing or no-homophily baseline before treating stable cooperation as reciprocity rather than sorting (`RS-GR-185`, `RS-GR-186`).
30. In any helping, public-goods, or prevention lane, publish whether the world is framed as producing benefits or avoiding harms, and whether payoffs are gains, losses, or mixed-sign; keep at least one sign-swapped or help-versus-harm companion baseline before attributing cooperation changes to reciprocity (`RS-GR-187`, `RS-GR-188`).
31. In any public-bad, collective-risk, or threshold lane, publish harm latency, threshold certainty, and aggregation technology (summation, weakest-link, or equivalent), and compare at least one immediate-harm or certain-threshold baseline before treating coordination changes as Golden-Rule progress (`RS-GR-189`, `RS-GR-190`).

32. In any triadic or other small-group reciprocity lane, publish the local interdependence pattern and whether third-party action can stabilize or destabilize pairwise relations, and keep at least one dyadic companion baseline before interpreting gains as reciprocity rather than architecture (`RS-GR-191`).
33. In any communication, coalition, or delegated-coordination lane, publish who may speak or coordinate for others, whether coalition/selection stages exist, and how representatives or leaders are chosen; keep at least one no-delegation and one all-participants companion baseline before attributing gains to Golden-Rule progress (`RS-GR-192`, `RS-GR-193`, `RS-GR-194`).
34. In any collective-action, climate, or solidarity lane with both public and private solutions, publish whether private protection exists, who can access it, and its relative efficacy/cost; keep at least one no-private-solution baseline before attributing cooperation changes to reciprocity (`RS-GR-195`, `RS-GR-196`, `RS-GR-198`).
35. In any outside-option or self-reliance lane, publish loner externality and group-formation flexibility, and keep at least one fixed-group or no-outside-option baseline before reading optimism or cooperation changes as moral improvement (`RS-GR-197`, `RS-GR-198`).
36. In any helping, mutual-aid, or partner-support lane, publish need observability, explicit ask rights, unsolicited-offer rights, and whether an ask makes need common knowledge; keep at least one auto-visible-need or no-ask companion baseline before treating unmet need as moral failure (`RS-GR-199`, `RS-GR-202`).
37. In any support-request or mutual-aid lane, publish request audience, visibility, and recognition semantics, including subgroup asymmetries, and keep at least one private-request baseline beside any public or recognized-request lane before attributing cooperation changes to Golden-Rule progress (`RS-GR-200`, `RS-GR-201`, `RS-GR-202`).
38. In any future-facing lane, publish whether beneficiaries are abstract future people, own descendants, or caregiver-linked successors, and keep at least one matched-cost universal-beneficiary baseline beside any child / grandchild / family-anchored future frame before attributing gains to Golden-Rule progress (`RS-GR-229`, `RS-GR-230`).
39. In any intergenerational dialogue or stewardship lane, publish voice symmetry, dialogue leadership, and influence direction explicitly, and keep at least one one-way-instruction baseline beside any youth-led or reciprocal-contact lane before attributing gains to Golden-Rule progress (`RS-GR-231`, `RS-GR-232`, `RS-GR-233`).

40. In any stewardship, remediation, or decommissioning lane, publish provisional-closure, conditional-closure, and final-release triggers plus post-closure monitoring-window semantics, and keep one early-release baseline beside one extended-verification baseline before attributing gains to Golden-Rule progress (`RS-GR-297`, `RS-GR-298`, `RS-GR-299`, `RS-GR-304`).
41. In any long-horizon liability lane, publish who holds residual risk after nominal closure, under what conditions that risk can transfer, and what insolvency / orphan-backstop waterfall applies; keep one operator-liable baseline beside one transfer or pooled-backstop variant before attributing gains to Golden-Rule progress (`RS-GR-297`, `RS-GR-300`, `RS-GR-301`, `RS-GR-302`, `RS-GR-303`).

81. In any archive, provenance, or successor-trust lane, publish the immutable subject identifier used for each artifact, whether names / tags / URLs are mutable aliases or signed bindings, how attestations / receipts / statuses / supersessions correlate to that subject, and whether verification survives dead resolvers or moved hosting; and keep one same-behavior companion lane where only subject-binding, alias mutability, or resolver-independence architecture changes before attributing gains to Golden-Rule progress (`RS-GR-369`, `RS-GR-370`, `RS-GR-371`, `RS-GR-372`, `RS-GR-373`, `RS-GR-374`).

## Deliverables Produced In This Research Pass

1. Source registry with verified links and per-source implications.
2. Source-backed strategic direction for Rust/Python/formal separation.
3. Broad tranche queue spanning theory, implementation, formal checks, and release hygiene.
38. In any sanction, allocation, or governance lane, publish whether rules are endogenously chosen, exogenously imposed, or only nominally voted on, and keep one imposed baseline beside any endogenous-choice lane before attributing cooperation changes to Golden-Rule progress (`RS-GR-203`, `RS-GR-204`, `RS-GR-206`).
39. In any institution-choice lane, publish electorate, decision rule, and binding scope, and keep one complete all-members baseline beside any subgroup-binding or partial-franchise variant before attributing cooperation changes to the norm rather than the constitution (`RS-GR-204`, `RS-GR-205`).
40. In any intergenerational, stewardship, or successor-world lane, publish whether current agents can bind successors, for how long, on which action dimensions, and through what escape or reversal procedure; keep one fully revisable or no-binding baseline beside any lock-in lane before attributing sustainability gains to Golden-Rule progress (`RS-GR-207`).
41. In any intergenerational, climate, or stewardship lane, publish how absent future beneficiaries are represented and socially scoped (proxy / guardian / future-person role; universal versus ingroup / outgroup framing), and keep one no-proxy and one universal-beneficiary baseline beside any represented or socially narrowed variant before attributing cooperation gains to Golden-Rule progress (`RS-GR-208`, `RS-GR-209`, `RS-GR-210`).

42. In any intergenerational, stewardship, or future-facing lane, publish beneficiary horizon depth explicitly (next cohort, medium horizon, remote generations, or weighted mixture), and keep at least one nearer-horizon and one farther-horizon companion baseline before attributing gains to Golden-Rule progress (`RS-GR-211`).
43. In any future-facing lane, publish whether future beneficiaries are made psychologically proximal through intertemporal links, continuity cues, or future-self imagination, and keep one low-link / low-vividness baseline beside any proximal variant before attributing gains to reciprocity (`RS-GR-212`, `RS-GR-213`, `RS-GR-214`).
44. In any future-facing, stewardship, or climate lane, publish the duty frame explicitly (responsibility to future generations, responsibility to mitigate present harms, neutral payoff language, or another frame), and keep one alternate-frame or no-frame baseline beside any future-responsibility variant before attributing gains to Golden-Rule progress (`RS-GR-215`, `RS-GR-216`).
45. In any future-facing policy or institution lane, publish actual support, perceived support, and whether support norms are disclosed, corrected, or left hidden, and keep one no-norm-correction baseline beside any support-salience variant before attributing uptake gains to reciprocity (`RS-GR-217`).
46. In any future-facing lane using legacy prompts, letters, or descendant / future-self exercises, publish whether the mechanism is impact legacy, reputation legacy, or both, whether action is publicly visible, and whether effects persist after delay, and keep one no-legacy baseline plus one delayed follow-up before attributing durable gains to Golden-Rule progress (`RS-GR-218`, `RS-GR-219`).
47. In any future-facing, stewardship, or climate-action lane, publish whether agents are given positive, negative, mixed, or no future visions; whether those visions emphasize desirability, possibility, collective efficacy, or explicit achievability; and whether emotional benefits of action are cued, with at least one no-vision / no-efficacy baseline before attributing gains to Golden-Rule progress (`RS-GR-220`, `RS-GR-221`, `RS-GR-222`).
48. In any future-facing worry, urgency, or burden lane, publish distress-induction level, available action channels, and any meaning-focused or efficacy-based coping scaffolds, and keep at least one low-scaffold and one agency-supported companion baseline before attributing action changes to Golden-Rule progress (`RS-GR-223`, `RS-GR-224`).
49. In any future-facing, stewardship, or climate-sacrifice lane, publish whether action for future beneficiaries competes with, aligns with, or is measured alongside present-day costly helping, and keep one matched-cost present-beneficiary companion baseline before attributing gains to Golden-Rule progress (`RS-GR-225`, `RS-GR-226`).
50. In any burden-sharing or future-facing policy lane, publish which fairness reference groups are salient (household, local community, broad society, vulnerable subgroup, future generations), at what scale burdens are felt, and keep one same-payoff comparison where fairness-to-whom changes without changing aggregate efficiency (`RS-GR-227`, `RS-GR-228`).
51. In any future-facing policy or institutional lane, publish whether future interests enter through nominal recognition, future-design role play, soft advisory institutions, or stronger throughput-accountability machinery, and keep one no-voice baseline plus one soft-advice-only baseline beside any stronger future-voice lane before attributing gains to Golden-Rule progress (`RS-GR-234`, `RS-GR-235`, `RS-GR-236`, `RS-GR-237`).
52. In any sustainability, stewardship, or transition lane, publish sectoral / geographical / temporal problem-shifting and whether protection depends on rolling successor maintenance versus lower-dependence passive safety, and keep one low-problem-shift or low-maintenance baseline beside any open-ended stewardship lane before attributing gains to Golden-Rule progress (`RS-GR-238`, `RS-GR-239`).
53. In any future-voice or long-term-governance lane, publish stakeholder presence, deliberative depth, and institutional teeth separately, and keep one seat-rich / low-deliberation baseline plus one deliberation-rich / low-teeth baseline beside any empowered future-voice design before attributing gains to Golden-Rule progress (`RS-GR-240`, `RS-GR-241`).
54. In any long-horizon, stewardship, or transition lane, publish whether uncertainty includes disputed future values and whether the world is single-path, laddered, or portfolio-based, and keep one single-path lock-in baseline beside any option-preserving or portfolio lane before attributing gains to Golden-Rule progress (`RS-GR-242`, `RS-GR-243`).
55. In any future-facing or long-horizon policy lane, publish whether benefits arrive within the acting cohort's lifetime, near the lifespan boundary, or mainly beyond it, and keep one matched-benefit within-lifetime baseline beside any beyond-lifetime world before attributing gains to Golden-Rule progress (`RS-GR-244`, `RS-GR-245`).
56. In any stewardship, resilience, or long-horizon risk lane, publish significant-harm floors, tipping-point categories, trigger indicators, and who can reopen or switch the pathway when thresholds are approached or crossed; keep one smooth-tradeoff / no-trigger baseline beside any floor-constrained or trigger-driven world before attributing gains to Golden-Rule progress (`RS-GR-246`, `RS-GR-247`, `RS-GR-248`, `RS-GR-249`).
57. In any future-voice, youth-representation, or proxy-governance lane, publish who is speaking for future beneficiaries, how they were selected or authorized, what cohort-balance / diversity constraints apply, and how their representative claims can be challenged or replaced; keep one same-power companion lane where only representative source or selection route changes before attributing gains to Golden-Rule progress (`RS-GR-250`, `RS-GR-251`, `RS-GR-252`, `RS-GR-253`).
58. In any anticipatory-governance, stewardship, or future-participation lane, publish whether the institution is one-off, periodic, permanent, sunsetted, or auto-renewing; whether an institutional anchor preserves records and know-how; and how recommendations travel across policy-cycle stages and political cycles; keep one ad-hoc / no-anchor baseline beside any durable cross-cycle-memory world before attributing gains to Golden-Rule progress (`RS-GR-254`, `RS-GR-255`, `RS-GR-256`, `RS-GR-257`).

59. In any future-facing governance, stewardship, or policy-evaluation lane, publish whether future impacts are forced into ex-ante assessment, comparable trade-off tables, written responses, recurring audits, or scheduled progress reports, and keep one no-future-accounting baseline beside any world with explicit future checks or public reasons before attributing gains to Golden-Rule progress (`RS-GR-258`, `RS-GR-259`, `RS-GR-260`, `RS-GR-261`, `RS-GR-262`).
60. In any long-horizon welfare, climate, or public-investment lane, publish the valuation rule explicitly — constant versus declining discount schedule, capital treatment, demographic assumptions, future-bias assumptions, and any non-discounted harm floors — and keep one same-behavior companion lane where only valuation architecture changes before attributing gains to Golden-Rule progress (`RS-GR-263`, `RS-GR-264`, `RS-GR-265`).

61. In any future-facing legal, governance, or review lane, publish whether future beneficiaries are treated as interests, rights-holders, or proxy-represented claimants; who has standing to act for them; what evidentiary barriers apply; and what remedy classes are available, and keep one declaration-only or no-standing baseline beside any implementation-forcing or broad-standing world before attributing gains to Golden-Rule progress (`RS-GR-266`, `RS-GR-267`, `RS-GR-268`, `RS-GR-269`, `RS-GR-270`).
62. In any long-horizon risk, climate, contamination, or resilience lane, publish the uncertainty default explicitly — wait-for-proof, permissive precaution, mandatory precaution, or another stance — along with the harm threshold, science standard, and burden of proving safety or controllability; keep one same-behavior companion lane where only precaution default or proof burden changes before attributing gains to Golden-Rule progress (`RS-GR-270`, `RS-GR-271`, `RS-GR-272`, `RS-GR-273`).


63. In any future-facing stewardship, restoration, or transition lane, publish the harm-handling order explicitly — avoid, minimize, restore, compensate / offset, or full restoration — along with the spatial / temporal scale of reversibility and any non-substitutable losses; keep one same-choice companion lane where only avoidance priority or substitutability assumptions change before attributing gains to Golden-Rule progress (`RS-GR-274`, `RS-GR-275`, `RS-GR-276`, `RS-GR-277`).
64. In any long-horizon planning, resilience, or adaptation lane, publish whether the policy is reference-scenario optimal, robust across scenarios, no-regret / low-regret, or adaptive-pathway based; publish explicit vulnerabilities and option-preservation devices; and keep one same-behavior companion lane where only robustness / regret architecture changes before attributing gains to Golden-Rule progress (`RS-GR-278`, `RS-GR-279`, `RS-GR-280`, `RS-GR-281`).

65. In any future-facing policy, stewardship, or governance lane, publish whether the intervention is one-shot, piloted, temporary-experimental, staged, or permanently enacted from the start; publish scale-up / rollback criteria and what remains reversible after implementation; and keep one same-behavior companion lane where only pilotability / reversibility architecture changes before attributing gains to Golden-Rule progress (`RS-GR-282`, `RS-GR-283`, `RS-GR-284`).
66. In any future-facing institution, monitoring, or review lane, publish whether rules expire automatically, require affirmative reauthorization, auto-renew, or persist until repeal; publish the evidence standard for extension / retirement and the implementation load added to the standing policy stock; and keep one same-behavior companion lane where only sunset / reauthorization / policy-stock-retirement semantics change before attributing gains to Golden-Rule progress (`RS-GR-285`, `RS-GR-286`, `RS-GR-287`).


67. In any stewardship, infrastructure, decommissioning, or successor-burden lane, publish whether long-horizon liabilities are pay-as-you-go, partially prefunded, fully prefunded, bonded / insured, or backed by a ring-fenced reserve; publish reserve governance, cost-estimate confidence level, update cadence, and who absorbs shortfalls; and keep one same-behavior companion lane where only prefunding / assurance architecture changes before attributing gains to Golden-Rule progress (`RS-GR-288`, `RS-GR-289`, `RS-GR-290`, `RS-GR-291`).
68. In any stewardship, infrastructure, or public-asset lane, publish asset inventory completeness, condition metrics, depreciation / backlog logic, maintenance-versus-new-build splits, lifecycle-cost estimates, and any funding-adequacy ratio such as ASI; and keep one same-behavior companion lane where only deferred-maintenance visibility / asset-ledger architecture changes before attributing gains to Golden-Rule progress (`RS-GR-292`, `RS-GR-293`, `RS-GR-294`, `RS-GR-295`, `RS-GR-296`).

69. In any stewardship, closure, or successor-protection lane, publish whether evidence is operator self-report, independent audit, joint monitoring, or adversarially contestable; whether outsiders can access data, inspect, comment, or trigger review; and whether audit rationales are public, and keep one same-behavior companion lane where only verification independence or contestability changes before attributing gains to Golden-Rule progress (`RS-GR-305`, `RS-GR-306`, `RS-GR-307`, `RS-GR-308`).
70. In any deep-time stewardship, closure, or successor-burden lane, publish whether future stewards receive raw records only, indexed records, an essential-records set, or a concise key-information package; whether renewal, translation, or media-migration instructions exist; and whether new evidence can reopen assessment, with one same-behavior companion lane where only knowledge-package or renewal semantics change before attributing gains to Golden-Rule progress (`RS-GR-309`, `RS-GR-310`, `RS-GR-311`, `RS-GR-312`).

71. In any deep-time stewardship, successor-burden, or transfer lane, publish staffing depth, role redundancy, named-succession coverage, mission-critical knowledge preservation, targeted training cadence, and geographic / site-proximity assumptions; keep one same-behavior companion lane where only capability continuity changes before attributing gains to Golden-Rule progress (`RS-GR-313`, `RS-GR-314`, `RS-GR-315`).
72. In any long-horizon emergency, stewardship, or resilient-operations lane, publish whether critical roles, interfaces, and contingencies are only documented, specifically trained, periodically drilled, or exercise-validated with after-action correction; keep one same-behavior companion lane where only rehearsal / validation architecture changes before attributing gains to Golden-Rule progress (`RS-GR-316`, `RS-GR-317`, `RS-GR-318`).

73. In any archive, record-transfer, or long-horizon stewardship lane, publish whether formats, schemas, identifiers, and interfaces are open / interoperable or bespoke / captive; publish export fidelity, API / sync paths, and practical vendor-exit rights; and keep one same-behavior companion lane where only interoperability / anti-lock-in semantics change before attributing gains to Golden-Rule progress (`RS-GR-319`, `RS-GR-320`, `RS-GR-321`, `RS-GR-325`).
74. In any long-horizon resilience, service, or stewardship lane, publish whether failures produce graceful degradation, manual fallback, alternate information flows, alternate facilities, or hard outage; publish essential-record and communications survivability under fallback; and keep one same-behavior companion lane where only degraded-operations / alternate-procedure semantics change before attributing gains to Golden-Rule progress (`RS-GR-322`, `RS-GR-323`, `RS-GR-324`, `RS-GR-325`).


75. In any archive, repository, or long-horizon stewardship lane, publish whether integrity is checked only at ingest or also through recurring fixity audits, repair / replacement duties, format-risk review, and preservation action plans for unsustainable formats; and keep one same-behavior companion lane where only fixity-refresh / format-migration architecture changes before attributing gains to Golden-Rule progress (`RS-GR-326`, `RS-GR-327`, `RS-GR-328`).
76. In any archive, identity, or long-horizon trust lane, publish whether cryptography is static or migration-ready; publish inventory / planning, algorithm-transition, validation / monitoring, and future-migration semantics; and keep one same-behavior companion lane where only crypto-agility / algorithm-transition architecture changes before attributing gains to Golden-Rule progress (`RS-GR-329`, `RS-GR-330`, `RS-GR-331`).
77. In any archive, repository, or successor-trust lane, publish trust-anchor lifetime / cryptoperiod, in-band versus out-of-band update path, delegation / threshold topology, and compromise-recovery / revocation semantics; and keep one same-behavior companion lane where only trust-root rotation / delegation / recovery architecture changes before attributing gains to Golden-Rule progress (`RS-GR-332`, `RS-GR-333`, `RS-GR-334`, `RS-GR-335`).
78. In any archive, provenance, or successor-trust lane, publish whether claims are merely signed or also registered in append-only transparency services; publish inclusion-proof, consistency-proof, monitor / auditor coverage, multi-service redundancy, and selective-submission / undiscoverable-receipt semantics; and keep one same-behavior companion lane where only tamper-evident logging or transparency-service plurality changes before attributing gains to Golden-Rule progress (`RS-GR-336`, `RS-GR-337`, `RS-GR-338`, `RS-GR-339`, `RS-GR-340`).
79. In any archive, provenance, or successor-trust lane, publish witness topology, witness-discovery / onboarding path, quorum rule, client self-audit / gossip behavior, and split-view evidence-handling / escalation semantics; and keep one same-behavior companion lane where only checkpoint witnessing or cross-perspective consistency architecture changes before attributing gains to Golden-Rule progress (`RS-GR-341`, `RS-GR-342`, `RS-GR-343`, `RS-GR-344`, `RS-GR-345`).
80. In any archive, provenance, or successor-trust lane, publish freshness windows, time-source / attested-time trust path, publication-latency bounds, timestamp- or evidence-renewal policy, and stale-proof / clock-failure response semantics; and keep one same-behavior companion lane where only temporal-validity, secure-time, or renewable-evidence architecture changes before attributing gains to Golden-Rule progress (`RS-GR-336`, `RS-GR-346`, `RS-GR-347`, `RS-GR-348`, `RS-GR-349`, `RS-GR-350`).
81. In any archive, provenance, or successor-trust lane, publish exactly which verification bytes are retained locally, which checks can be completed fully offline, whether receipt / bundle formats remain cross-client readable, whether already-issued evidence can be re-registered or re-anchored under successor services, and what happens when original dependencies disappear; and keep one same-behavior companion lane where only portable-evidence-packet or offline-verification architecture changes before attributing gains to Golden-Rule progress (`RS-GR-351`, `RS-GR-352`, `RS-GR-353`, `RS-GR-354`, `RS-GR-355`, `RS-GR-356`).
82. In any archive, provenance, or successor-trust lane, publish the verifier rulebook used to turn evidence into a verdict: trust roots, delegations, accepted signer identities / issuers, claim predicates, witness / freshness thresholds, and pass / warn / reject disposition rules; retain a versioned policy snapshot beside each decision; and keep one same-behavior companion lane where only verifier-policy snapshot or deterministic-appraisal architecture changes before attributing gains to Golden-Rule progress (`RS-GR-357`, `RS-GR-358`, `RS-GR-359`, `RS-GR-360`, `RS-GR-361`, `RS-GR-362`).
83. In any archive, provenance, or successor-trust lane, publish the status vocabulary and change model explicitly: revocation, suspension, hold, unknown, expiry, end-of-life, redirection / supersession, and compromise-time semantics; publish the freshness and authority of status evidence and how clients treat unknown or unavailable status; retain negative-evidence snapshots beside positive receipts; and keep one same-behavior companion lane where only status-semantics / supersession-history architecture changes before attributing gains to Golden-Rule progress (`RS-GR-363`, `RS-GR-364`, `RS-GR-365`, `RS-GR-366`, `RS-GR-367`, `RS-GR-368`).

84. In any archive, attestation, or successor-trust lane, publish the exact protected representation layer — raw bytes, canonical JSON, deterministic CBOR, canonical RDF dataset, or opaque envelope — along with which transformations preserve validity, which require re-signing, and how payload type / schema semantics are bound; and keep one same-behavior companion lane where only canonicalization-boundary / transform-semantics architecture changes before attributing gains to Golden-Rule progress (`RS-GR-375`, `RS-GR-376`, `RS-GR-377`, `RS-GR-378`, `RS-GR-379`, `RS-GR-380`).


85. In any archive, attestation, or successor-trust lane, publish the interpretation contract that turns verified bytes into meaning — media type, statement / predicate type, schema dialect, specVersion, context / vocabulary bundle, extension registry, and unknown-term handling — and keep one same-behavior companion lane where only schema-pinning / vocabulary-continuity / semantic-survival architecture changes before attributing gains to Golden-Rule progress (`RS-GR-381`, `RS-GR-382`, `RS-GR-383`, `RS-GR-384`, `RS-GR-385`, `RS-GR-386`).

86. In any archive, attestation, or successor-trust lane, publish the authority contract that makes a statement admissible: issuer / functionary / workload identity, delegated role or registration entry, subject-namespace or path scope, purpose / predicate / step scope, audience or relying-party scope, and any trust-domain / parent-identity / selector constraints; retain the policy snapshot that granted this standing at decision time; and keep one same-behavior companion lane where only authority-scope / designated-speaker / namespace-custody architecture changes before attributing gains to Golden-Rule progress (`RS-GR-387`, `RS-GR-388`, `RS-GR-389`, `RS-GR-390`, `RS-GR-391`, `RS-GR-392`, `RS-GR-393`).
87. In any archive, attestation, or successor-trust lane, publish the concurrence contract that decides when a claim has enough independent support: exact threshold or quorum rule, the unit of distinctness that counts toward it (key, functionary, person, organization, witness, transparency service, or admin domain), any separation-of-duty or same-domain exclusions, and whether quorum failure blocks, degrades, or reroutes verification; keep one same-behavior companion lane where only quorum-semantics / signer-independence / concurrence-profile architecture changes before attributing gains to Golden-Rule progress (`RS-GR-394`, `RS-GR-395`, `RS-GR-396`, `RS-GR-397`, `RS-GR-398`, `RS-GR-399`).
88. In any archive, attestation, or successor-trust lane, publish the conflict-resolution profile that decides what happens when valid-looking support points in different directions: delegation or policy precedence order, any terminating or veto-capable roles, whether same-subject support sources compose as `AND`, `OR`, threshold, or issuer-inclusion filters, whether threshold requires agreement on the same underlying facts, and how no-match / abstention / disagreement cases are handled; keep one same-behavior companion lane where only conflict-resolution / precedence-profile architecture changes before attributing gains to Golden-Rule progress (`RS-GR-400`, `RS-GR-401`, `RS-GR-402`, `RS-GR-403`, `RS-GR-404`, `RS-GR-405`, `RS-GR-406`).

89. In any archive, attestation, or successor-trust lane, publish the decision-replay record that explains why a verdict was reached: verifier implementation / build identity, loaded policy or bundle revision, stable request / decision id, determining or matched rules / policies, whether the outcome came from explicit allow / deny logic versus default / no-match / skip-on-error fallback, and any attached obligations / advice / remediation hints; retain one compact explanation receipt beside each material verdict; and keep one same-behavior companion lane where only decision-trace / replay-diagnostic architecture changes before attributing gains to Golden-Rule progress (`RS-GR-407`, `RS-GR-408`, `RS-GR-409`, `RS-GR-410`, `RS-GR-411`, `RS-GR-412`, `RS-GR-413`).

90. In any archive, attestation, or successor-trust lane, publish the appraisal-input baseline that turned the retained evidence into a verdict: reference-value corpus, endorsement set, trust-root / trust-anchor material, policy-data bundle, input-selection or collection scope, and missing / stale / unreachable-baseline fallback semantics; retain one compact digested snapshot or pin for each material verdict; and keep one same-behavior companion lane where only reference-baseline / endorsement-set / appraisal-input continuity architecture changes before attributing gains to Golden-Rule progress (`RS-GR-414`, `RS-GR-415`, `RS-GR-416`, `RS-GR-417`, `RS-GR-418`, `RS-GR-419`, `RS-GR-420`).

91. In any archive, attestation, or successor-trust lane, publish the evidence-acquisition contract that produced the retained evidence: acquisition topology (challenge/response, passport, background-check, uni-directional, streaming, brokered, cached, or another named pattern), freshness handle / nonce / trusted-timestamp origin and binding, claim- or event-log-selection scope, intermediary trust assumptions, concrete observation fields captured, and stale / partial / filtered-evidence fallback semantics; retain one compact acquisition receipt or pin beside each material verdict; and keep one same-behavior companion lane where only evidence-acquisition topology / challenge-binding / observation-scope architecture changes before attributing gains to Golden-Rule progress (`RS-GR-421`, `RS-GR-422`, `RS-GR-423`, `RS-GR-424`, `RS-GR-425`, `RS-GR-426`, `RS-GR-427`).

92. In any archive, presentation, or successor-trust lane, publish the disclosure contract that determined what a verifier could learn and keep: disclosure profile (full, selective, derived-predicate, unlinkable, or another named mode), mandatory versus optional claim classes, issuer-defined disclosure bounds, omission semantics for absent fields, holder-binding / anti-forwarding requirements for disclosed subsets, and retention-intent / discard expectations; retain one compact disclosure receipt or pin beside each material verdict; and keep one same-behavior companion lane where only disclosure-profile / omission-semantic / retention-intent architecture changes before attributing gains to Golden-Rule progress (`RS-GR-428`, `RS-GR-429`, `RS-GR-430`, `RS-GR-431`, `RS-GR-432`, `RS-GR-433`).

93. In any archive, presentation, or successor-trust lane, publish the request contract that determined what counted as a valid answer: exact query language and version, claim-set / credential-set / submission-requirement alternatives, verifier preference ordering versus hard requirement, any best-effort value filters or holder-discretion points, satisfaction-witness mapping from returned objects back to request elements, and any federation or policy rule constraining what the verifier was authorized to ask; retain one compact request / satisfaction receipt or pin beside each material verdict; and keep one same-behavior companion lane where only request-contract / satisfaction-mapping / authorized-ask architecture changes before attributing gains to Golden-Rule progress (`RS-GR-434`, `RS-GR-435`, `RS-GR-436`, `RS-GR-437`, `RS-GR-438`, `RS-GR-439`, `RS-GR-440`).
94. In any archive, presentation, or successor-trust lane, publish the verifier-targeting contract that makes a proof admissible for one relying party and one session rather than merely valid in the abstract: intended verifier identity / audience / `client_id` / origin, transaction nonce or wallet nonce, authenticated session-transcript or handover fields, response URI / method / endpoint binding, any proof-option `domain` / `challenge` or DPoP-style request binding, holder / key-binding requirement, and stale / missing / mismatched binding fallback; retain one compact targeting / replay-scope receipt beside each material verdict; and keep one same-behavior companion lane where only verifier-targeting / session-binding / replay-scope architecture changes before attributing gains to Golden-Rule progress (`RS-GR-441`, `RS-GR-442`, `RS-GR-443`, `RS-GR-444`, `RS-GR-445`, `RS-GR-446`, `RS-GR-447`).

95. In any archive, presentation, or successor-trust lane, publish the participant-metadata resolution contract that made counterparts, endpoints, keys, and capability surfaces admissible: identifier-prefix or discovery mode, fetched metadata sources, trust-chain or signed-metadata material, metadata-policy application, validation results, version / cache state, and stale / invalid / unresolved fallback; retain one compact metadata-resolution receipt or pin beside each material verdict; and keep one same-behavior companion lane where only metadata-resolution / federation-chain / capability-continuity architecture changes before attributing gains to Golden-Rule progress (`RS-GR-448`, `RS-GR-449`, `RS-GR-450`, `RS-GR-451`, `RS-GR-452`, `RS-GR-453`, `RS-GR-454`, `RS-GR-455`).
96. In any archive, presentation, issuance, or successor-trust lane, publish the capability-negotiation contract that selected one concrete profile from many supported ones: advertised format / proof / response-mode / client-id-prefix / algorithm / encryption capability sets, which dimensions were required versus preferred versus optional, the exact chosen profile, and whether weaker or unsupported alternatives were rejected, retried, or silently tolerated; retain one compact negotiation receipt or pin beside each material verdict; and keep one same-behavior companion lane where only capability-negotiation / downgrade-resistance / chosen-profile architecture changes before attributing gains to Golden-Rule progress (`RS-GR-456`, `RS-GR-457`, `RS-GR-458`, `RS-GR-459`, `RS-GR-460`, `RS-GR-461`, `RS-GR-462`, `RS-GR-463`).
97. In any archive, presentation, issuance, or successor-trust lane, publish the authenticator-assurance contract behind each proof: UP / UV or equivalent user-control signals, authentication-intent semantics, key-container class, device-bound versus syncable / backup-eligible posture, attestation presence or absence, authenticator-class identifiers or certifications, and whether cryptographic holder binding or key-bound attestation was required, optional, or waived; retain one compact authenticator-assurance receipt or pin beside each material verdict; and keep one same-behavior companion lane where only authenticator-assurance / user-presence / device-binding architecture changes before attributing gains to Golden-Rule progress (`RS-GR-464`, `RS-GR-465`, `RS-GR-466`, `RS-GR-467`, `RS-GR-468`, `RS-GR-469`, `RS-GR-470`).
98. In any archive, presentation, authorization, or successor-trust lane, publish the transaction-intent contract behind each material approval: exact `authorization_details` / `transaction_data` / document-set or payment context, whether the approval object traveled unsigned, as a signed Request Object, by pushed-request reference, or under another integrity regime, the granted subset or reduced / enriched result, any transaction-data hashes or other proof linkage, and the comparison rule for later replay; retain one compact approval-intent receipt or pin beside each material verdict; and keep one same-behavior companion lane where only transaction-intent-binding / approval-object-integrity / granted-subset architecture changes before attributing gains to Golden-Rule progress (`RS-GR-471`, `RS-GR-472`, `RS-GR-473`, `RS-GR-474`, `RS-GR-475`, `RS-GR-476`, `RS-GR-477`).

99. In any archive, presentation, or successor-trust lane, publish the correlation contract behind each material presentation: identifier-stability scope (global, ecosystem, sector, verifier, session, or one-time), which parties can intentionally link repeated presentations, proof-family linkability posture, status-check privacy path, side-channel / metadata correlation surface, and any padding / decoy / omission-hardening semantics; retain one compact correlation-scope receipt or pin beside each material verdict; and keep one same-behavior companion lane where only correlation-scope / pairwise-pseudonym / linkability-boundary architecture changes before attributing gains to Golden-Rule progress (`RS-GR-478`, `RS-GR-479`, `RS-GR-480`, `RS-GR-481`, `RS-GR-482`, `RS-GR-483`, `RS-GR-484`, `RS-GR-485`).

100. In any archive, presentation, authorization, or successor-trust lane, publish the delivery-path contract behind each material request and response: which request elements traveled by value through front-channel URLs versus by `request_uri` or another reference, whether JAR / PAR or another protected backchannel carried the authoritative ask, whether responses returned by redirect, form-post, `direct_post`, `direct_post.jwt`, or another route, which browsers / frontends / backends / relays / reverse proxies / wallet callbacks could observe plaintext, and what redirect-bound response-code or equivalent mechanism closed any out-of-band session-fixation gap; retain one compact delivery-path receipt or pin beside each material verdict; and keep one same-behavior companion lane where only delivery-path / transport-confidentiality / intermediary-visibility architecture changes before attributing gains to Golden-Rule progress (`RS-GR-486`, `RS-GR-487`, `RS-GR-488`, `RS-GR-489`, `RS-GR-490`, `RS-GR-491`, `RS-GR-492`).


101. In any archive, presentation, authorization, or successor-trust lane, publish the approval-rendering contract behind each material user-facing ceremony: the exact authoritative approval object or digest, which fields and order were actually shown, locale / language / formatting inputs, which labels / icons / descriptive strings came from issuer metadata versus verifier or merchant input, whether the final render happened in user-agent chrome, wallet-native UI, authorization-server UI, merchant-controlled content, or another named surface, and what anti-redressing / mismatch checks protected the human-visible approval from framing, spoofing, or silent pre-consent leakage; retain one compact rendering receipt or pin beside each material verdict; and keep one same-behavior companion lane where only approval-rendering / locale / trusted-display architecture changes before attributing gains to Golden-Rule progress (`RS-GR-493`, `RS-GR-494`, `RS-GR-495`, `RS-GR-496`, `RS-GR-497`, `RS-GR-498`, `RS-GR-499`, `RS-GR-500`).


102. In any archive, presentation, authorization, authentication, or successor-trust lane, publish the ceremony-topology contract behind each material user journey: whether the interaction was same-device, cross-device, or hybrid; which device rendered the request, stored keys or credentials, and returned the response; whether invocation happened by untargeted QR/deep-link scan, targeted `authorization_endpoint`, claimed HTTPS link, private-use URI scheme, loopback callback, or another named route; what app-identity or destination-binding guarantees existed for that invocation path; and what proximity, co-presence, or claimant-participation evidence closed the gap between displayed request and responding device; retain one compact ceremony-topology receipt or pin beside each material verdict; and keep one same-behavior companion lane where only device-split / invocation-route / proximity-proof architecture changes before attributing gains to Golden-Rule progress (`RS-GR-501`, `RS-GR-502`, `RS-GR-503`, `RS-GR-504`, `RS-GR-505`, `RS-GR-506`, `RS-GR-507`, `RS-GR-508`).

103. In any archive, presentation, authorization, authentication, or successor-trust lane, content-address each durable successor-safe ceremony receipt by publishing a deterministic-canonicalization profile, SHA-256 digest, canonical byte length, and one stable hash-named locator (for example an `ni` URI) beside the receipt path; cite that locator in downstream notes unless the ceremony contract changed; and keep one same-behavior companion lane where only canonicalization / locator / citation discipline changes before attributing gains to Golden-Rule progress (`RS-GR-509`, `RS-GR-510`).

104. In any archive, presentation, authorization, authentication, or successor-trust lane, run a fail-closed assessment over each durable successor-safe ceremony receipt that checks for scaffold placeholders, explicit verifier / audience naming, explicit session or replay binding, request-integrity posture for any `request_uri` indirection, explicit `direct_post` session-mapping material, named cross-device participation or proximity evidence, dispatch-assurance posture for custom-scheme versus claimed-HTTPS invocation, trusted-renderer identification, and digest-bearing retained-evidence references; retain one tiny assessment report beside the receipt and locator so inheritors can tell “valid but weak” from “valid and successor-ready” without rereading standards prose (`RS-GR-505`, `RS-GR-511`, `RS-GR-512`, `RS-GR-513`).

105. In any archive, presentation, authorization, authentication, or successor-trust lane, collapse each successor-safe ceremony receipt assessment into one explicit archive disposition that says whether the receipt is claim-ready citable, provisional locator-only, or held for remediation; name the residual risk response (accept versus mitigate), the open finding codes, and the required actions; and keep one same-behavior companion lane where only assessment-to-disposition handling changes before attributing gains to Golden-Rule progress (`RS-GR-514`, `RS-GR-515`).

106. In any archive, presentation, authorization, authentication, or successor-trust lane, collapse each warned or failed successor-safe ceremony receipt disposition into one tiny remediation plan that points at the receipt locator, names each open finding as a blocking or warning work item, lists the exact receipt paths to repair, states one concrete closure test for each item, and declares the promotion gate for returning to claim-ready citation; keep one same-behavior companion lane where only assessment-to-remediation closure discipline changes before attributing gains to Golden-Rule progress (`RS-GR-516`, `RS-GR-517`).

107. In any archive, presentation, authorization, authentication, or successor-trust lane, collapse each current successor-safe ceremony receipt package into one explicit authorization decision that says whether claim-ready citation is authorized now, records the minimal basis checks behind that decision (current green assessment, no open blocking remediation, claim-ready archive admission, and locator-only copy-forward posture), names any failed basis codes, and carries terms and conditions plus a review trigger; keep one same-behavior companion lane where only authorization-gating discipline changes before attributing gains to Golden-Rule progress (`RS-GR-518`, `RS-GR-519`).

108. In any archive, presentation, authorization, authentication, or successor-trust lane, preserve one tiny promotion record whenever a successor-safe ceremony receipt package changes materially: cite the prior and current receipt locators, preserve prior versus current assessment / authorization status, list which findings closed, carried, or newly opened, and state whether the package truly promoted to claim-ready citation; keep one same-behavior companion lane where only reassessment-to-promotion proof discipline changes before attributing gains to Golden-Rule progress (`RS-GR-519`, `RS-GR-520`, `RS-GR-521`).

105. In any archive, presentation, authorization, authentication, or successor-trust lane, once a successor-safe ceremony receipt package becomes claim-ready, retain one tiny review watch that binds the current locator, authorization decision, promotion state, reviewed-on date, no-later-than review interval, reopen-trigger codes, and required regeneration sequence, so future stewards can tell when a once-green package has crossed a freshness boundary without copying the full receipt forward (`RS-GR-522`, `RS-GR-523`).

109. In any archive, presentation, authorization, authentication, or successor-trust lane, collapse each evaluation of a successor-safe ceremony receipt review watch into one tiny review verdict that cites the watched locator, records the as-of date, lists any observed and matched reopen-trigger codes, states whether claim-ready citation continues or must be suspended pending regeneration, and carries the regeneration sequence only when reopening is required; keep one same-behavior companion lane where only watch-to-verdict freshness discipline changes before attributing gains to Golden-Rule progress (`RS-GR-524`, `RS-GR-525`).

110. In any archive, presentation, authorization, authentication, or successor-trust lane, collapse each successor-safe ceremony receipt review verdict into one tiny citation advisory that cites the reviewed locator, preserves the as-of review decision, states whether the reviewed locator remains citable or is withdrawn from claim-ready use, tells future stewards what to do with existing citations and new citations, and carries the regeneration sequence only when the reviewed locator has been withdrawn; keep one same-behavior companion lane where only review-to-advisory handling changes before attributing gains to Golden-Rule progress (`RS-GR-526`, `RS-GR-527`).

111. In any archive, presentation, authorization, authentication, or successor-trust lane, collapse each current successor-safe ceremony receipt package into one tiny package manifest that cites the active locator and current claim status, names the current authorization / promotion / review / advisory decisions, enumerates the authoritative component roles and file paths, and attaches one file-level digest and byte count for each component, so future stewards can recover package membership and fixity without reconstructing it from neighboring snapshots (`RS-GR-528`, `RS-GR-529`, `RS-GR-530`).

112. In any archive, presentation, authorization, authentication, or successor-trust lane, collapse each refresh of a successor-safe ceremony receipt package manifest into one tiny supersession record that cites the prior and current package manifests by path and fixity, states whether the active receipt locator stayed the same or rotated, lists the authoritative component roles that changed, gives compact replacement reason codes, and tells future stewards which manifest is now authoritative for downstream citation (`RS-GR-531`, `RS-GR-532`, `RS-GR-533`).


112. In any archive that keeps successor-safe ceremony package manifests and supersession records over time, publish one compact lineage record naming the authoritative package head, the ordered manifest chain, the ordered supersession chain, locator continuity across the line, and the current review/advisory basis that keeps the head authoritative; retain the pairwise supersession records for audit, but do not make future inheritors reconstruct the authoritative chain from filenames and timestamps alone (`RS-GR-534`, `RS-GR-535`, `RS-GR-536`).


113. In any archive that keeps successor-safe ceremony package lineages over time, publish one compact package-head pointer that names the current authoritative package manifest, cites the lineage record that backs that head, points at the live review-verdict and citation-advisory status artifacts, and uses registered version-navigation relation names so future stewards can discover the live package root immediately instead of opening the full lineage object first (`RS-GR-537`, `RS-GR-538`, `RS-GR-539`).

114. In any archive that keeps successor-safe ceremony package heads over time, publish one compact package-status card that the head can expose as its live `status` resource: cite the authoritative manifest and active locator digest, collapse the current review window, as-of review verdict, citation guidance, and current citable/not-citable result into one machine-checkable object, and carry the regeneration sequence only when the package is suspended pending regeneration (`RS-GR-540`, `RS-GR-541`, `RS-GR-542`).

115. In any archive that keeps superseded successor-safe ceremony package manifests around for audit, publish one compact package-redirect artifact that starts from the superseded manifest and points at the preferred current package-reference target, the successor manifest, and the live package-status-card resource using registered relation semantics such as `cite-as`, `successor-version`, `latest-version`, `status`, and `describedby`, so future stewards do not have to reconstruct replacement and current-citation posture from several neighboring files (`RS-GR-543`, `RS-GR-544`, `RS-GR-545`).


116. In any archive that retains more than one successor-safe ceremony receipt package family or more than one superseded package root over time, publish one compact package catalog listing the live package head for each family plus any retained superseded-package redirects, using collection/member and typed-link semantics so future inheritors can discover the current package roots from one archive entry point instead of browsing lineage and redirect files family by family (`RS-GR-546`, `RS-GR-547`, `RS-GR-548`).

117. In any archive, presentation, authorization, authentication, or successor-trust lane, publish one compact package verification report beside each live successor-safe ceremony package head that names the authoritative manifest under test, the local validation profile, the pass / blocked / fail result for each executed check, and the environment boundary when local execution stopped; keep one same-behavior companion lane where only verification-profile / environment-boundary reporting changes before attributing gains to Golden-Rule progress (`RS-GR-549`, `RS-GR-550`).

118. In any archive, presentation, authorization, authentication, or successor-trust lane, publish one compact package claim-scope artifact beside each live successor-safe ceremony receipt package head that cites the authoritative manifest, live status card, and verification report, then states which downstream claim classes are allowed, which remain restricted, what qualifiers must accompany use, and what follow-up steps would justify broader claims; keep one same-behavior companion lane where only verification-to-claim-scope discipline changes before attributing gains to Golden-Rule progress (`RS-GR-551`, `RS-GR-552`).

119. In any archive, presentation, authorization, authentication, or successor-trust lane, publish one compact package reliance card beside each live successor-safe ceremony receipt package head that cites the authoritative manifest, live status card, verification report, and claim-scope artifact, then states one reliance decision, the current citable/not-citable result, the allowed and restricted claim classes, the qualifiers that must accompany use, and the exact broader-claim steps that remain blocked; keep one same-behavior companion lane where only status/verification/claim-scope collapse-to-reliance discipline changes before attributing gains to Golden-Rule progress (`RS-GR-553`, `RS-GR-554`, `RS-GR-555`).
