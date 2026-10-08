# Cargo tool-workflow root lanes — 2026-03-16

Purpose: keep **P-0494 Cargo Compile-Time-Deps Workflow Kit** honest now that Cargo makes `build-dir` / `target-dir` separation and persisted build-analysis sessions more concrete.

## What changed in the substrate

Three adjacent facts are now explicit enough to deserve their own review lanes:

1. Cargo’s March 13, 2026 build-dir-layout-v2 call-for-testing says projects should test anything touching `build-dir` / `target-dir`, because many tools still rely on unspecified layout details.
2. The same post says Cargo 1.91 already lets users separate intermediate build artifacts (`build-dir`) from final artifacts (still in `target-dir`).
3. Cargo’s unstable docs now expose build-analysis sessions (`cargo report sessions`, `cargo report timings`, `cargo report rebuilds`) and say `[build.analysis] enabled = true` is safe to leave in config even on stable because it only warns there.

That means a tool-facing workflow bundle should no longer talk as though `rust-analyzer.cargo.targetDir` is the whole root story.

## The three lanes that must stay separate

### 1. Tool-surface parity
This is still **P-0494**’s core question:
- what command ran,
- what compile surface it covered,
- what selection/target assumptions were in play,
- and when a full build is required.

### 2. Root-lane arrangement
This is new implementation pressure on **P-0494**:
- whether `target-dir` stayed shared or was isolated for the tool lane,
- whether `build-dir` also changed or remained shared,
- whether duplicate artifacts were an explicit trade-off,
- and whether build-dir-layout drift forces manual review.

This is **not** the same as live blocking diagnosis in **P-0490**.
A tool run can have a perfectly understandable root arrangement even when no actual wait happened.

### 3. Optional imported session evidence
Build-analysis session IDs are useful supporting evidence, but they are not the crate’s core contract.
The bundle may say:
- “we linked this tool-facing run to Cargo session XYZ conservatively,”
- “we found candidate sessions only,”
- or “no session link was available.”

This is **not** the same as the historical warehousing lane in **P-0035**, and it is **not** the same as the per-run rebuild explanation lane in **P-0469**.

## What P-0494 should provide now

A sharpened 0.1 for **P-0494** should now be able to export:

- `root-lane.receipt.json`
- `evidence-source.receipt.json`
- `tool-session.link.json`

in addition to the earlier tool-build, parity, fallback, comparison-baseline, override-command, coverage, and workspace-invocation artifacts.

## Anti-patterns to resist

- Do **not** let `targetDir = true` stand in for the whole root policy.
- Do **not** quietly import build-analysis sessions and then treat them as exact proof that the tool-facing run and Cargo session were the same thing.
- Do **not** collapse tool-surface parity, lock contention, build-dir consumer migration, and build-history warehousing into one fake “editor performance” crate.
- Do **not** let this proposal become another live process observer; keep it receipt-first.

## Sources

- Build Dir Layout v2 call for testing: https://blog.rust-lang.org/2026/03/13/call-for-testing-build-dir-layout-v2/
- Cargo unstable docs (`build-analysis`, `build-dir-new-layout`, `compile-time-deps`): https://doc.rust-lang.org/cargo/reference/unstable.html
- rust-analyzer configuration: https://rust-analyzer.github.io/book/configuration
- RFC 3477 (`cargo build` versus `cargo check` guarantee line): https://rust-lang.github.io/rfcs/3477-cargo-check-lang-policy.html
