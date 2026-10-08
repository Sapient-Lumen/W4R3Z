# Frontier salience snapshot — 2026-03-21-136

This pass did **not** add another disk cleaner, `target/` janitor, or remote-cache appliance.
It sharpened **P-0480 Cargo Global Cache Policy & GC Receipt Kit** into a more recovery-aware cache-governance contract.

## Why this frontier moved up

Cargo’s cache substrate is now precise enough that the sharper missing layer is increasingly obvious:

- Cargo’s cache-cleaning work distinguishes files that can be recreated locally from files that must be re-downloaded, and automatic cleanup is skipped in offline or frozen mode;
- the stable config docs say cache tracking currently covers the **global cache in Cargo home** but **not build artifacts**, which remain a separate tracked future;
- the Cargo Home guide keeps the internal Cargo-home structure unstable and shows that `registry/cache` and `registry/src` are different storage classes even when they refer to the same dependency source;
- the Build Cache guide keeps `target` / build-dir layout internal to Cargo and separate from Cargo home;
- the accepted user-wide build-cache goal and the 2025h2 build-dir-layout goal make it clear that a first-class cross-workspace build cache is a different future surface again;
- and the 2025 State of Rust survey still lists storage/resource usage as a notable productivity problem.

That combination means the missing crate is not another tool that says “you can free 8 GiB.”
The missing crate is now a **cache-governance contract** that can publish **recovery obligation**, **cache-surface basis**, and **offline-cost honesty** above Cargo’s raw GC substrate.

## Main conclusion

Promote **P-0480** upward again, but keep it narrow.
The next worthy move is not more deletion UX and not a generic CI cache server.

It should stay focused on:

1. freezing cleanup plans into a reviewable **recovery-aware** surface,
2. making **Cargo-home global cache** versus **target/build-dir** versus **future user-wide build cache** explicit,
3. making **locally recreatable** versus **redownload-only** versus **external-plugin fetch** obligations explicit,
4. and downgrading cleanup claims when offline posture or mixed-toolchain use makes the true recovery cost uncertain.

## Ranked near-term frontier from this pass

1. **P-0480 Cargo Global Cache Policy & GC Receipt Kit** — strengthened because storage pain remains broad while current Cargo docs finally make recovery-cost and cache-surface truth concrete enough to standardize.
2. **P-0035 cargo-build-insights** — still unusually strong because performance complaints remain broad and historical build evidence is finally becoming real.
3. **P-0489 Cargo Build-Dir Consumer Transition Kit** — still strong because more Cargo tooling will need an honest transition as build-dir layout changes.
4. **P-0490 Cargo Lock Contention Witness Kit** — still strong because live waiting and lock contention remain adjacent to the same build-cache pain.
5. **P-0484 Toolchain & Target Support Contract Kit** — still strong because cleanup and cache reuse claims often depend on exact toolchain/channel policy.

## Keep these boundaries sharp

- **P-0480** is the Cargo-home / cleanup-policy / recovery-obligation contract.
- **P-0489** is tooling migration off internal build-dir assumptions.
- **P-0035** is historical build regression judgment.
- **P-0490** is live lock/contention evidence.

Do not let “Cargo cache management” flatten those lanes into one fake crate.
