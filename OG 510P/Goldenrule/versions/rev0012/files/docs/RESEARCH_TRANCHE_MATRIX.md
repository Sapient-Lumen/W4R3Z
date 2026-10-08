# Research Tranche Matrix

This matrix operationalizes [docs/RESEARCH_AGENDA.md](/workspace/docs/RESEARCH_AGENDA.md) into concrete tranche IDs with source traceability and verification signals.

Legend:
- `class`: `theory` | `engine` | `formal` | `orchestration` | `benchmark` | `stats` | `ops`
- `verify`: minimum command or artifact proving tranche completion

| tranche_id | class | work package | source_ids | verify |
|---|---|---|---|---|
| RT-001 | theory | Canonicalize world families and payoff contracts in specs | RS-IPD-001, RS-IPD-008 | `make test-spec-ledger` + schema diff |
| RT-002 | theory | Define memory-one parameter constraints in machine schema | RS-IPD-001 | schema validation + fixture tests |
| RT-003 | theory | Define robustness-first claim taxonomy | RS-IPD-002, RS-IPD-003, RS-IPD-009 | claim schema + report validator |
| RT-004 | theory | Define formal obligation ladder per claim type | RS-FM-001..RS-FM-007 | new spec section + gate checks |
| RT-005 | theory | Define assumption sunset triggers for unresolved claims | RS-OPS-003 | spec ledger validation |
| RT-006 | engine | Add stable transition event IDs in Rust trace output | RS-OPS-001 | artifact diff stability test |
| RT-007 | engine | Add replay executor that validates event chain integrity | RS-OPS-001 | replay tests + seed artifact |
| RT-008 | engine | Add deterministic noise channel partitioning policy | RS-IPD-001 | determinism/property tests |
| RT-009 | engine | Add platform byte-stability checks for core artifacts | RS-OPS-002 | cross-platform fixture hashes |
| RT-010 | engine | Add benchmark fixture suite for classic strategy families | RS-IPD-005, RS-IPD-008 | fixture tests + catalog update |
| RT-011 | engine | Add profile-guided microbench lane for hot paths | RS-OPS-004 | criterion artifact report |
| RT-012 | engine | Add failure-state invariants for impossible transitions | RS-FM-008, RS-FM-009 | invariant/property tests |
| RT-013 | formal | Implement SMT-LIB emitter for memory-one constraints | RS-FM-001 | solver fixture snapshots |
| RT-014 | formal | Implement Z3 adapter for satisfiable/unsat obligations | RS-FM-002, RS-FM-003 | `artifacts/formal/z3_*.json` |
| RT-015 | formal | Implement cvc5 adapter with shared contracts | RS-FM-004, RS-FM-005 | `artifacts/formal/cvc5_*.json` |
| RT-016 | formal | Add cross-solver agreement checker | RS-FM-001..RS-FM-005 | agreement report + gate check |
| RT-017 | formal | Add solver divergence triage artifact schema | RS-FM-001 | schema + validator |
| RT-018 | formal | Add unsat-core persistence and replay support | RS-FM-002, RS-FM-004 | replay command + test fixtures |
| RT-019 | formal | Add solver-timeout deterministic fallback policy | RS-FM-002, RS-FM-004 | timeout tests + spec entry |
| RT-020 | formal | Add formal claim verifier with required-proof IDs | RS-FM-001..RS-FM-010 | claim validator |
| RT-021 | formal | Add PRISM adapter for stochastic property checks | RS-FM-006 | adapter smoke artifacts |
| RT-022 | formal | Add STORM adapter for cross-tool stochastic checks | RS-FM-007 | cross-tool comparison artifact |
| RT-023 | formal | Add simulation-vs-model-check bound comparison | RS-FM-006, RS-FM-007 | bound delta report |
| RT-024 | formal | Add strict-gate promotion rules for formal evidence | RS-OPS-003 | `make gate-strict` control test |
| RT-025 | orchestration | Add deterministic DAG run-plan compiler | RS-OPS-001 | DAG artifact + unit tests |
| RT-026 | orchestration | Add run sharding with stable ordering guarantees | RS-OPS-001, RS-OPS-005 | shard determinism tests |
| RT-027 | orchestration | Add typed Rust kernel FFI via PyO3 | RS-RP-001 | CLI smoke + ABI tests |
| RT-028 | orchestration | Build Python wheel workflow via maturin | RS-RP-002 | reproducible wheel checks |
| RT-029 | orchestration | Add artifact lineage map per run node | RS-OPS-002 | lineage artifact + validator |
| RT-030 | orchestration | Add failure replay bundle command | RS-OPS-001, RS-OPS-002 | one-command replay test |
| RT-031 | orchestration | Add priority queues with deterministic tie-break rules | RS-OPS-005 | scheduler tests |
| RT-032 | orchestration | Add environment metadata lock on every run | RS-OPS-003 | metadata completeness test |
| RT-033 | orchestration | Add report claim typing (estimate/proof/assumption) | RS-OPS-003 | report schema + validation |
| RT-034 | orchestration | Add mission templates for holdout and robustness sweeps | RS-IPD-002, RS-IPD-003 | template smoke runs |
| RT-035 | benchmark | Add canonical Axelrod-compatible baseline suite | RS-IPD-005 | baseline suite artifact |
| RT-036 | benchmark | Add OpenSpiel compatibility harness for selected games | RS-IPD-006, RS-IPD-007 | adapter parity report |
| RT-037 | benchmark | Add noise/horizon robustness matrix suite | RS-IPD-001..RS-IPD-004 | robustness matrix artifact |
| RT-038 | benchmark | Add population-dynamics stress suites | RS-IPD-003, RS-IPD-009 | population artifact + tests |
| RT-039 | benchmark | Add negative-control suites with expected no-dominance | RS-IPD-002, RS-IPD-003 | control report |
| RT-040 | benchmark | Add benchmark drift and bump protocol tests | RS-OPS-002 | drift checker + policy entry |
| RT-041 | benchmark | Add vulnerability-oriented holdouts for exploitability | RS-IPD-001, RS-IPD-004 | holdout artifact set |
| RT-042 | benchmark | Add cross-suite calibration for certification alignment | RS-IPD-001, RS-FM-001 | calibration report |
| RT-043 | benchmark | Add benchmark provenance manifest schema | RS-OPS-003 | schema validation |
| RT-044 | benchmark | Add benchmark impact report generator | RS-OPS-004 | report artifact |
| RT-045 | stats | Add mandatory interval/effect-size reporting policy | RS-OPS-003 | report schema validation |
| RT-046 | stats | Add deterministic bootstrap routines for sweep summaries | RS-OPS-003 | reproducible bootstrap test |
| RT-047 | stats | Add uncertainty decomposition (seed/opponent/model) | RS-IPD-002, RS-OPS-003 | decomposition artifact |
| RT-048 | stats | Add optional stopping safeguards in orchestrator | RS-OPS-003 | policy validator |
| RT-049 | stats | Add claim confidence-tier rules to report pipeline | RS-OPS-003 | confidence-tier checks |
| RT-050 | stats | Add outlier and failed-run handling policy checks | RS-OPS-003 | policy + tests |
| RT-051 | stats | Add power-planning metadata for expensive studies | RS-OPS-003 | metadata completeness test |
| RT-052 | stats | Add reproducibility-grade publication table builder | RS-OPS-001, RS-OPS-003 | publication bundle artifact |
| RT-053 | ops | Add reproducibility bundle schema v2 | RS-OPS-001, RS-OPS-002 | schema + validator |
| RT-054 | ops | Add offline replay verifier tool for bundles | RS-OPS-001 | replay verifier tests |
| RT-055 | ops | Add dependency tranche cadence checker | RS-OPS-002 | cadence artifact |
| RT-056 | ops | Add no-network deterministic CI lane | RS-OPS-001 | CI workflow validation |
| RT-057 | ops | Add benchmark baseline policy with criterion artifacts | RS-OPS-004 | baseline drift report |
| RT-058 | ops | Add nextest profile classes for quick/full/soak | RS-OPS-005 | profile tests |
| RT-059 | ops | Add release evidence manifest signatures | RS-OPS-003 | signature verification check |
| RT-060 | ops | Add release claim audit summary (assumptions retired/resolved) | RS-OPS-003 | release artifact completeness |

## Sequencing Notes

1. Execute `RT-001`..`RT-005` before broad formal or orchestration expansion.
2. Execute `RT-013`..`RT-020` before strict formal gate promotion.
3. Execute `RT-035`..`RT-044` before public benchmark claims.
4. Execute `RT-053`..`RT-060` before release-candidate publication.
