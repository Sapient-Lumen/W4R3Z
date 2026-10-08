# Rebuild explanation upstream fit — 2026-03-08

## Main judgment

Cargo now has enough official rebuild-analysis substrate that the missing value is **not another recorder, another dashboard, or another vague performance crate**.

The missing value is the **stable receipt / diff / redaction / support-bundle layer** above Cargo’s evolving report and session surfaces.

## Current substrate we should treat as real

- Cargo unstable docs already expose `-Zbuild-analysis` plus `cargo report sessions`, `cargo report rebuilds`, and `cargo report timings`.
- The Cargo changelog now records `-Zbuild-analysis` as persisted build metrics with report commands, not as a vague someday idea.
- The tracking issue is still open and explicitly marked as waiting on feedback, with unresolved questions around schema and wording.
- Cargo has long carried demand for better rebuild diagnostics; the old “why crates are rebuilt” issue is not a new complaint.
- The 2025 State of Rust survey still places compile-time / resource-usage pain among the main productivity limits.
- The current project goals around “Relink don’t Rebuild” and build-dir layout show that rebuild fanout, locking, and reuse are still active frontiers rather than solved background noise.

## Planning rule

When a future pass touches Cargo rebuild performance, it must say whether the missing value is primarily:

1. a **per-run support bundle** for one incident (**P-0469**),
2. a **historical warehouse / regression-adjudication layer** (**P-0035**),
3. a **resolver / graph cause-chain layer** (**P-0468**),
4. a **tool-only parity / fallback layer** (**P-0494**),
5. or a **live lock/contention witness** (**P-0490**).

For this archive, the best current move is (1), and that move should import from the others instead of absorbing them.

## What future passes should prefer

- tiny fixture corpora,
- stable cause vocabulary,
- import/freeze behavior for Cargo sessions,
- optional overlays for fingerprint logs,
- and redaction/support-handoff planning.

They should **not** drift into:

- a new performance dashboard,
- a replacement for Cargo timing HTML,
- a parallel session recorder,
- or a giant “Cargo doctor” that claims to solve every build mystery at once.

## Implementation stance for P-0469

Treat three evidence lanes as first-class:

1. **Imported Cargo reports** — the preferred substrate when nightly build-analysis is available.
2. **Live capture** — the stable-first path capturing command/env/wrapper/config context.
3. **Fingerprint overlays** — optional deeper evidence, not the MVP contract.

The crate should freeze those lanes into one small bundle:

- `rebuild-context.toml`
- `unit-rebuilds.json`
- `rebuild.receipt.json`

with optional overlays:

- `fingerprint-delta.json`
- `cache-conflict.report.json`
- `timings-pointer.json`

## Sources

- Cargo unstable docs (`-Zbuild-analysis`): https://doc.rust-lang.org/cargo/reference/unstable.html#build-analysis
- Cargo changelog: https://doc.rust-lang.org/cargo/CHANGELOG.html
- Tracking issue for `-Zbuild-analysis`: https://github.com/rust-lang/cargo/issues/15844
- Cargo issue “Provide better diagnostics for why crates are rebuilt”: https://github.com/rust-lang/cargo/issues/2904
- 2025 State of Rust survey results: https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Relink don’t Rebuild goal: https://rust-lang.github.io/rust-project-goals/2025h2/relink-dont-rebuild.html
- Cargo build-dir layout goal: https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-dir-layout.html
