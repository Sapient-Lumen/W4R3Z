# Risk Register

Generated from `specs/risk_register.yaml`.

- total_risks: 30

| id | status | domain | severity | likelihood | owner | review_date | summary |
|---|---|---|---|---|---|---|---|
| `RK-001` | `open` | `formal` | `high` | `medium` | `@root` | `2026-03-21` | Solver disagreement can invalidate strong formal claims. |
| `RK-002` | `open` | `benchmark` | `high` | `medium` | `@root` | `2026-03-21` | Leaderboard overfitting can hide poor out-of-distribution behavior. |
| `RK-003` | `open` | `ops` | `high` | `low` | `@root` | `2026-03-28` | Artifact or manifest incompleteness can break reproducibility claims. |
| `RK-004` | `open` | `governance` | `medium` | `medium` | `@root` | `2026-03-14` | Assumption backlog growth can create hidden policy debt. |
| `RK-005` | `open` | `performance` | `medium` | `medium` | `@root` | `2026-03-28` | Slow local loops reduce feedback quality and can hide regressions. |
| `RK-006` | `open` | `benchmark` | `high` | `medium` | `@root` | `2026-03-21` | Uncontrolled strategy-space expansion can create misleading progress signals and hide fairness/regret failures. |
| `RK-007` | `open` | `benchmark` | `medium` | `high` | `@root` | `2026-03-27` | Raw rematch-world discovery counts can be inflated by behaviorally identical exit-policy aliases. |
| `RK-008` | `open` | `benchmark` | `medium` | `medium` | `@root` | `2026-03-27` | Hard-coding a rematch-world canonical quotient from a cooperative-starting pool can under-deduplicate richer entrant pools and distort discovery counts. |
| `RK-009` | `open` | `benchmark` | `medium` | `medium` | `@root` | `2026-03-27` | Reusing a cooperative-start rematch canonicalization cache after the entrant pool gains first-move D support can silently under-deduplicate discoveries. |
| `RK-010` | `open` | `benchmark` | `medium` | `medium` | `@root` | `2026-03-27` | Reusing a zero-noise rematch canonicalization cache under nonzero action-tremble semantics can silently under-deduplicate discoveries and distort search rankings. |
| `RK-011` | `open` | `benchmark` | `medium` | `high` | `@root` | `2026-03-27` | Using one universal rematch canonicalization cache policy across noise topologies can either under-deduplicate discoveries or waste search budget on needless recomputation. |
| `RK-012` | `open` | `benchmark` | `medium` | `medium` | `@root` | `2026-03-27` | Keeping an unvalidated global reachability horizon for rematch canonicalization can either waste search budget or merge distinct families when the world semantics change. |
| `RK-013` | `open` | `performance` | `medium` | `high` | `@root` | `2026-03-27` | Naive rematch canonicalization plans that key on full entrant signatures and a legacy global horizon can waste orders of magnitude of search budget and slow local iteration. |
| `RK-014` | `open` | `governance` | `low` | `medium` | `@root` | `2026-03-27` | Vendoring the current zero-noise rematch dispatch as a bulky flat support-signature table can hide semantic structure, amplify diff noise, and make stale planner embeddings harder to audit. |
| `RK-015` | `open` | `governance` | `low` | `medium` | `@root` | `2026-03-27` | An interim zero-noise planner embedding can silently drift from the regenerated regime map if the ordered-rule artifact is copied without schema and contract validation. |
| `RK-016` | `open` | `benchmark` | `medium` | `medium` | `@root` | `2026-03-27` | Leaving rematch-role assignment implicit can make asymmetric restart-world results incomparable and can hide seat-specific exploitability. |
| `RK-017` | `open` | `benchmark` | `medium` | `medium` | `@root` | `2026-03-27` | Conflating exogenous-pool rematch delay with full matching-market efficiency can overstate how generally the current proxy's welfare conclusions transfer. |
| `RK-018` | `open` | `benchmark` | `medium` | `medium` | `@root` | `2026-03-27` | Reporting only aggregate welfare in rematch worlds can hide whether gains come from better conduct within matches or simply from spending more time productively matched. |
| `RK-019` | `open` | `benchmark` | `medium` | `medium` | `@root` | `2026-03-27` | Comparing identical rematch-delay settings across worlds without partnership-tempo metrics can hide that one world pays a much larger effective delay tax simply because its relationships churn faster. |
| `RK-020` | `open` | `benchmark` | `medium` | `medium` | `@root` | `2026-03-27` | Publishing only raw aggregate rematch leaderboards can misread occupancy-tax-induced rank flips as genuine within-match strategy-quality changes. |
| `RK-021` | `open` | `benchmark` | `medium` | `medium` | `@root` | `2026-03-27` | Reporting a rematch winner at one delay value without delay-robustness metadata can overstate institution-sensitive raw orderings as if they were universal strategy rankings. |
| `RK-022` | `open` | `benchmark` | `medium` | `medium` | `@root` | `2026-03-27` | Wide rematch delay tables that do not prune dead contenders or report leader margins can bloat the archive while still obscuring the actual decision-relevant winner fragility. |
| `RK-023` | `open` | `benchmark` | `medium` | `medium` | `@root` | `2026-03-27` | Point-estimate rematch leader flips that ignore simulation uncertainty can be archived as stable ranking reversals even when the top-vs-runner-up gap is statistically unresolved. |
| `RK-024` | `open` | `benchmark` | `medium` | `medium` | `@root` | `2026-03-27` | Unresolved rematch near-ties can consume disproportionate simulation budget if the archive treats every uncertified winner flip as a mandatory rerun target. |
| `RK-025` | `open` | `benchmark` | `medium` | `medium` | `@root` | `2026-03-27` | Rematch leaderboards can archive statistically certified but practically negligible top-gap differences as if they were meaningful strategy advantages when no smallest effect of interest is declared. |
| `RK-026` | `open` | `benchmark` | `medium` | `medium` | `@root` | `2026-03-27` | Reporting rematch materiality only at one or two ad hoc delta values can hide threshold sensitivity and encourage post hoc cherry-picking of the indifference zone. |
| `RK-027` | `open` | `benchmark` | `medium` | `medium` | `@root` | `2026-03-27` | Reporting rematch materiality and budget only at one arbitrary delta can hide how indifference-zone choices change closure cost and can invite either oversampling or post hoc threshold shopping. |
| `RK-028` | `open` | `benchmark` | `medium` | `medium` | `@root` | `2026-03-27` | Treating rematch delta-budget frontiers as smooth coarse-grid objects can hide narrow knife-edge neighborhoods near observed top-gap means where closure cost explodes and where post hoc threshold choices become especially fragile. |
| `RK-029` | `open` | `benchmark` | `medium` | `medium` | `@root` | `2026-03-27` | Declaring one rematch practical margin without budget-admissible bands can hide that nearby SESOI values have radically different closure costs and can enable post hoc threshold shopping around knife-edge leader gaps. |
| `RK-030` | `open` | `benchmark` | `medium` | `medium` | `@root` | `2026-03-27` | Publishing one anchor delta per rematch admissible band can still hide materially different panel-label summaries when the same parent band contains multiple distinct closure topologies. |
