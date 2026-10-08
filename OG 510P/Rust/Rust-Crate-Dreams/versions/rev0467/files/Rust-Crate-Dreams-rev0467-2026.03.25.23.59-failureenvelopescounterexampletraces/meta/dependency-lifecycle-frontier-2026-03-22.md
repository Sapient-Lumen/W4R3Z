# Dependency lifecycle frontier — 2026-03-22

This note maps the newly sharpened territory around **P-0535 Dependency Lifecycle Transition Kit**.

## Why this territory matters now

The official safety-critical write-up is unusually explicit that Rust teams often:
- use crates early,
- track them carefully,
- shrink them for higher-criticality parts,
- or hide them behind abstraction layers and replace them later.

That is not well served by today’s tooling split.
We have graph import, trust signals, MSRV policy, and off-ramp support, but we still do not have one compact artifact for **where a dependency is allowed to live and how it is supposed to leave**.

## Neighboring lanes P-0535 should reuse, not duplicate

- **P-0036** for MSRV and lockfile floors.
- **P-0017** for trust/risk import.
- **P-0011** for maintenance/support posture.
- **P-0515** for successor-specific off-ramp recipes.
- **P-0484** for toolchain/target support posture where platform restrictions affect a dependency plan.

## Best near-term shape

The strongest first build is not a grand safety platform.
It is a portable contract with:
- lane snapshot,
- criticality boundary report,
- seam receipts,
- replacement readiness,
- lifecycle drift diff.

## Good proving grounds

- firmware/control vs diagnostics split,
- CLI/tooling vs reusable library split,
- owned fork or vendored stabilization lane,
- regulated subsystem with explicit third-party restrictions.

## Sources

- https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
- https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
