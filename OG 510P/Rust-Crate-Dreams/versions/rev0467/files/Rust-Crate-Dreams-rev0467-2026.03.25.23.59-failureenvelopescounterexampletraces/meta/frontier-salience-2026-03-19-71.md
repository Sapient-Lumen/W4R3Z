# Frontier salience snapshot — 2026-03-19 (71)

This pass promoted a new embedded/storage lane:

- **P-0527 LittleFS Native Adoption Kit** — because the ecosystem now has both mature FFI-backed usage and a fresh pure-Rust LittleFS port, but still lacks one shared adoption layer for storage-adapter truth, compatibility witnesses, and power-cut evidence.

## Main judgment

The notable March 2026 change is that a **pure-Rust littlefs path now exists**.
That makes the missing value more specific, not less important.

The sharper gap is no longer:

- “Rust cannot do LittleFS,”
- “someone should someday port the C implementation,”
- or “embedded flash storage is too early to productize.”

The sharper gap is that teams still lack one boring way to answer:

- what backend they are actually using,
- whether their image/operation behavior is compatible with the profile they claim,
- whether their async story is honest,
- and what evidence they have for recovery after interruption.

## Why this moved now

This move is grounded by four current facts:

- upstream `littlefs` still explicitly positions itself around **power-loss resilience**, **wear leveling**, and **bounded RAM/ROM**;
- the current mainstream Rust wrapper path (`littlefs2`) still documents a **C backend**;
- `littlefs2-sys` still exposes C build/link reality and explicitly says a permissively licensed replacement for `string.c` is welcome;
- and the newly published `littlefs-rust` docs now show a **safe Rust API built on a function-by-function Rust port**, which means raw feasibility is no longer the main missing story.

Meanwhile the wider embedded Rust stack now has:

- `embedded-storage-async` for async storage traits,
- Embassy flash utilities and simulated in-memory flash,
- and visible long-running user demand around **async flash / async SPI honesty** for LittleFS-style workloads.

So the best crate idea here is the **adoption kit above the engine**, not just the engine itself.

## Broad portfolio ranking after this pass

1. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit**
2. **P-0525 Crate Diagnosis Surface Pack Kit**
3. **P-0524 Crate Example Surface Pack Kit**
4. **P-0520 Crate Lifecycle Surface Pack Kit**
5. **P-0484 Toolchain & Target Support Contract Kit**
6. **P-0472 Docs.rs Build Parity & Evidence Kit**
7. **P-0027 text-input-kit**
8. **P-0087 UI Accessibility Doctor Kit**
9. **P-0197 Text Layout & Shaping Conformance Kit**
10. **P-0092 GUI Testing & Snapshot Harness Kit**
11. **P-0527 LittleFS Native Adoption Kit**
12. **P-0466 Python Wheel ABI & Free-Threading ShipKit**
13. **P-0168 Rust Android Mobile Kit**
14. **P-0206 Wasm Component Contract & Conformance ShipKit**
15. **P-0467 Apple XCFramework & SwiftPM ShipKit**
16. **P-0499 NuGet Native Interop ShipKit**

## Why this won over adjacent candidates right now

- It beat a generic **embedded persistence** lane because LittleFS now has a concrete substrate story and real review objects.
- It beat a raw **pure-Rust port celebration** because the archive’s job is to identify what is still missing after a new port appears.
- It beat another **foreign-package shipping contract** because the archive still benefits from keeping end-user and firmware product engineering in the portfolio.

## What changed in the archive

Added:
- `entries/2026-03-19-251.md`
- `proposals/littlefs-native-adoption-kit.md`
- `meta/frontier-salience-2026-03-19-71.md`
- `meta/littlefs-native-adoption-product-plan-2026-03-19.md`
- `meta/littlefs-lane-boundaries-2026-03-19.md`
- `fixtures/littlefs-native-adoption-kit/`

Updated:
- `README.md`
- `INDEX.md`
- `meta/known-existing.md`
- `meta/prioritization.md`
- `meta/roadmap.md`
- `meta/research-ledger.md`
- `meta/decision-log.md`
- `meta/llm-hygiene.md`
- `meta/epic-crate-portfolio-2026-03-18.md`

## What this pass deliberately did not do

It did **not** collapse:

- engine implementation,
- flash adapter truth,
- image tooling,
- power-cut evidence,
- and higher-level persistence products

into one fake “embedded filesystem crate.”
