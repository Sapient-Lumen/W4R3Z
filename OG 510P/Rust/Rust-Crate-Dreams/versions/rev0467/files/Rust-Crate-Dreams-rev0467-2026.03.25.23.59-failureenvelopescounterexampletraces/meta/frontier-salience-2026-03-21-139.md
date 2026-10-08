# Frontier salience snapshot — 2026-03-21-139

This pass did **not** open another generic Cargo migration helper or cache-adjacent tool.
It sharpened **P-0489 Cargo Build-Dir Consumer Transition Kit** around **adapter-viability windows**.

## Why this frontier moved up again

Cargo's March 13, 2026 **Build Dir Layout v2** testing post made the downstream gap more concrete than it was even a week earlier:

- Cargo still says the build-dir layout is internal and asks people to test anything touching build-dir or target-dir under `-Zbuild-dir-new-layout`;
- the post names concrete failure families instead of vague tooling risk;
- it gives version-windowed advice like `std::env::var_os("CARGO_BIN_EXE_*")` for Cargo 1.94+ with fallback pressure for older Cargo;
- and it lists real library support status, which means maintainers now need issue-grade receipts instead of improvised screenshots.

The build-cache docs reinforce the same split: final artifacts live in target-dir, intermediate artifacts live in build-dir, and the build-dir layout is still internal to Cargo.
Cargo's 1.94 changelog also notes that Cargo's own testsuite was reworked to use `CARGO_BIN_EXE_*`, which upgrades that adapter from loose folklore into a stronger authority class.

That combination means the sharper missing crate is not just an audit of who scrapes `target/`.
It is now an audit that can also say **whether the proposed adapter is actually viable in the caller's Cargo window**, **whether fallback is still required**, and **whether dual-layout support must remain for a migration period**.

## Main conclusion

Promote **P-0489** upward again, but keep it narrow.
The next worthy move is not a stable public filesystem API for Cargo internals.

It should stay focused on:

1. classifying consumer failure families,
2. suggesting adapters conservatively,
3. publishing **adapter-viability windows** as first-class receipts,
4. keeping fallback and dual-support pressure explicit,
5. and attaching one compact transition bundle to CI reviews and upstream issues.

## Ranked near-term frontier from this pass

1. **P-0489 Cargo Build-Dir Consumer Transition Kit** — strengthened because the official Cargo migration story now contains named failure families and version-windowed adapter advice.
2. **P-0055 Cargo Workspace Toolchain Manifest Kit** — still strong because route authority and workspace tool provenance remain real unmet needs.
3. **P-0035 cargo-build-insights** — still strong because historical build analysis is becoming a concrete downstream workflow.
4. **P-0480 Cargo Global Cache Policy & GC Receipt Kit** — still strong because storage pressure and recovery posture remain broad operational pain.
5. **P-0490 Cargo Lock Contention Witness Kit** — still strong because shared-cache contention remains adjacent but distinct from layout migration.

## Keep these boundaries sharp

- **P-0489** is consumer inventory + path contracts + adapter-viability windows + transition receipts.
- **P-0471** is final artifact handoff.
- **P-0490** is live contention.
- **P-0055** is workspace tool route authority.
- **P-0035** is historical build analysis.

Do not let “Cargo transition tooling” flatten those lanes into one fake crate.
