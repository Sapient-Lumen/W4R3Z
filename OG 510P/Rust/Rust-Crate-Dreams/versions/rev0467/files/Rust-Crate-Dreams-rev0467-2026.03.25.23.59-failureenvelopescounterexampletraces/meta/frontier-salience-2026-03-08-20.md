# Frontier salience scan — 2026-03-08 (twentieth pass)

## Main judgment

This pass **did not** add a new top-level proposal.

Instead, it made a stronger repo-level judgment:

- **P-0469 Cargo Rebuild Explanation Kit** is the highest-value near-term incubation target for the archive’s current Cargo frontier,
- and the best next work is now **implementation-shaping** (schemas, scenario bundles, evidence-lane boundaries, CLI scope), not more Cargo performance proposal count.

## Ranked frontier after this pass

1. **P-0469 Cargo Rebuild Explanation Kit**
2. **P-0468 Cargo Resolver Explanation Kit**
3. **P-0503 Assurance Case Workbench Kit**
4. **P-0504 Linker Lane Contract & Diagnosis Kit**
5. **P-0494 Cargo Compile-Time-Deps Workflow Kit**
6. **P-0505 Cargo Host/Target Scope Contract Kit**
7. **P-0486 Debuggability Support Contract Kit**
8. **P-0433 MC/DC Coverage Workbench Kit**
9. **P-0453 Safety Contract Consumer Kit**
10. **P-0490 Cargo Lock Contention Witness Kit**

## Why P-0469 is even stronger now

Five current facts sharpen it:

- Cargo’s unstable docs now document persisted build-analysis sessions plus `cargo report sessions`, `cargo report rebuilds`, and `cargo report timings`.
- The Cargo changelog records `-Zbuild-analysis` as real, current substrate rather than only a plan.
- The tracking issue is still marked as waiting on feedback and still lists unresolved schema/wording questions, which means downstream stable contracts are still a legitimate missing layer.
- The 2025 State of Rust survey still names resource usage / slow compile times as a top productivity problem.
- Rust’s current project goals still explicitly target rebuild fanout (`Relink don’t Rebuild`) and build-dir locking/shared-cache pain.

## What changed in the archive

Added:

- `meta/rebuild-explanation-upstream-fit-2026-03-08.md`
- `meta/frontier-salience-2026-03-08-20.md`
- `fixtures/cargo-rebuild-why-kit/fingerprint-delta.schema.json`
- `fixtures/cargo-rebuild-why-kit/cache-conflict.report.schema.json`
- `fixtures/cargo-rebuild-why-kit/scenarios/check_then_build_workspace/*`
- `fixtures/cargo-rebuild-why-kit/scenarios/wrapper_rustflags_drift/*`
- `fixtures/cargo-rebuild-why-kit/scenarios/shared_target_lock_hint/*`
- `entries/2026-03-08-143.md`

Updated:

- `proposals/cargo-rebuild-explanation-kit.md`
- `fixtures/cargo-rebuild-why-kit/README.md`
- `README.md`
- `INDEX.md`
- `meta/roadmap.md`
- `meta/research-ledger.md`
- `meta/territory-map.md`
- `meta/llm-hygiene.md`

## What should happen next

The best next passes should prefer:

1. schema freeze for `fingerprint-delta` and `cache-conflict.report`,
2. small scenario bundles proving `tool_invocation_drift_possible`, `wrapper_or_flags_changed`, and `cache_conflict_possible`,
3. import/freeze workflows for Cargo session IDs,
4. and one conservative CLI shape (`capture`, `freeze-session`, `compare`, `explain`) rather than a dashboard.

They should **not** drift into:

- another generic Cargo performance crate,
- another timing visualizer,
- a historical warehouse that really belongs to P-0035,
- or a mega “doctor” that collapses rebuilds, resolver causes, host/target scope, and lock contention into one tool.

## Sources

- Cargo unstable docs (`-Zbuild-analysis`): https://doc.rust-lang.org/cargo/reference/unstable.html#build-analysis
- Cargo changelog: https://doc.rust-lang.org/cargo/CHANGELOG.html
- Tracking issue for `-Zbuild-analysis`: https://github.com/rust-lang/cargo/issues/15844
- 2025 State of Rust survey results: https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Relink don’t Rebuild goal: https://rust-lang.github.io/rust-project-goals/2025h2/relink-dont-rebuild.html
- Cargo build-dir layout goal: https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-dir-layout.html
