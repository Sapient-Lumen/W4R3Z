# Risk Register

Generated from `specs/risk_register.yaml`.

- total_risks: 15

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
