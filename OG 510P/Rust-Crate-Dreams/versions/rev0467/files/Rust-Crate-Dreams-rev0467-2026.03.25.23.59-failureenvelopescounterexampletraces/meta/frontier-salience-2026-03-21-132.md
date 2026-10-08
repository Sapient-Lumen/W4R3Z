# Frontier salience snapshot — 2026-03-21-132

This pass did **not** add another generic Cargo doctor, timing HTML viewer, or build dashboard.
It sharpened **P-0035 cargo-build-insights** into a more buildable historical-build lane.

## Why this frontier moved up

Cargo's build-analysis substrate is now strong enough that the sharper missing layer is increasingly obvious:

- the build-analysis goal says Cargo wants to record build metadata across invocations, explain rebuilds, and enable historical analysis, but it also keeps the prototyping phase unstable and opt-in;
- the current unstable Cargo docs document JSONL logs in `$CARGO_HOME/log/` and `cargo report sessions`, `cargo report timings`, and `cargo report rebuilds`;
- the Cargo 1.94 development-cycle update says `cargo report sessions` was added specifically to find ids for the other report commands and that `cargo report timings` kept gaining missing functionality;
- the compiler performance survey says build satisfaction averaged 6/10, that workflows differ widely, and that users want tooling that explains what was recompiled and why;
- the 2025 State of Rust survey still names slow compile times and storage/resource usage as a leading productivity problem.

That combination means the missing crate is no longer “some day Cargo should record more data.”
The missing crate is now a **stable imported-session warehouse with honest comparison windows, series splits, exactness receipts, and exportable review bundles**.

## Main conclusion

Promote **P-0035** back upward, but keep it tightly scoped.
The worthy crate is not another per-run rebuild explainer and not another hosted metrics UI.

It should stay focused on:

1. freezing imported unstable Cargo sessions into a stable downstream schema,
2. making **comparison-window truth** explicit,
3. making **series-split / comparability truth** explicit,
4. preserving unknown fields and provenance,
5. and exporting small review bundles another human or tool can inspect.

## Ranked near-term frontier from this pass

1. **P-0035 cargo-build-insights** — promoted because compile-time pain remains broad while the recorder/report substrate is now real enough to support a stable historical layer.
2. **P-0469 Cargo Rebuild Explanation Kit** — still unusually strong because one-run support incidents remain the daily entry point into build pain.
3. **P-0468 Cargo Resolver Explanation Kit** — still strong because duplicate builds and feature/version choice often sit adjacent to rebuild and history stories.
4. **P-0494 Cargo Compile-Time-Deps Workflow Kit** — still strong because editor/tool-oriented builds often distort naive comparisons.
5. **P-0490 Cargo Lock Contention Witness Kit** — still strong because waiting stories can masquerade as regressions if they are not separated.

## Keep these boundaries sharp

- **P-0035** is the historical warehouse / regression-adjudication layer.
- **P-0469** is the per-run support bundle.
- **P-0468** is graph-cause explanation.
- **P-0494** is tool-workflow parity.
- **P-0490** is live contention evidence.

Do not let “Cargo build performance” flatten those into one fake crate.
