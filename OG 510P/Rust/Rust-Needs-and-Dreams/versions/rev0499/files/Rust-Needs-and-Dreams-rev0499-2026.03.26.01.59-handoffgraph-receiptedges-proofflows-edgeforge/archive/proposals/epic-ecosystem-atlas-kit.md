# Epic proposal: Ecosystem Atlas Kit

## Thesis
One of the most worthy non-language contributions Rust could make now is a **portable atlas for reference stacks**.

Not a new registry. Not another recommendation blog. Not one centrally blessed page.

A real artifact system for saying, in a reviewable way:
- what domain we are talking about,
- what lanes exist,
- which slots matter,
- which crates fill those slots,
- which shared seams those stacks rely on,
- why those choices were made,
- who is making the recommendation,
- how the stack composes,
- how local overlays differ,
- and when the recommendation has gone stale.

That would give Rust a way to help users get oriented in the ecosystem without flattening the ecosystem into a winner-take-all leaderboard.

## Why now
The signals are unusually aligned:
- The Rust project’s own 2025 vision work says users need help navigating crates.io, that there is no clear place to get advice on a “starter set” of crates, and that smoother interop plus shared building blocks are part of the answer.
- The 2025 State of Rust survey says online docs remain the canonical reference, maintainers support is an explicit concern, and LLM tooling is increasingly part of how people learn Rust.
- crates.io now exposes richer recommendation inputs: advisories, trusted-publishing controls, SLOC, and `pubtime`.
- Cargo’s own development notes keep stressing that plugins matter because Cargo cannot be everything to everyone, which argues for a companion atlas layer rather than expecting Cargo to become a full recommendation engine.
- Foundation-backed work is already targeting rustdoc search discoverability and crates.io search experience.
- Maintainer-fund work makes explicit that maintenance is multiplicative but often invisible, which means recommendation systems need to surface sustainability signals instead of only momentum.

This combination means the missing piece is not raw data or community desire. It is the **reviewable layer above them**.

Sources:
- https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- https://blog.rust-lang.org/inside-rust/2025/10/01/this-development-cycle-in-cargo-1.90/
- https://rustfoundation.org/media/announcing-the-rust-foundations-2024-fellows/
- https://blog.rust-lang.org/inside-rust/2026/01/12/what-is-maintenance-anyway/

## What should be built
A first credible version should ship:
1. canonical schemas for `atlas-domain`, `stack-lane`, `stack-slot-map`, `interop-seam-map`, `selection-evidence`, `alternative-set`, `curator-record`, `freshness-budget`, `atlas-overlay`, `atlas-check-report`, and `atlas-pack`
2. adapters for crates.io metadata, `pubtime`, Security-tab signals, Trusted Publishing posture, docs.rs, and existing archive kits like Trust Signals / Lifecycle Ledger / Support Envelope
3. renderer outputs for:
   - human-readable domain guides,
   - compact starter-stack summaries,
   - org overlay views,
   - bounded assistant contexts derived from the canonical artifacts
4. diff support for recommendation drift:
   - changed defaults,
   - changed interop posture,
   - degraded maintenance or trust posture,
   - expired freshness budgets,
   - widened native/runtime assumptions
5. explicit references to Interop Commons artifacts when a neutral shared seam exists, and explicit “missing commons” notes when it does not
6. several domain pilots proving the system can support multiple philosophies without collapsing into one official answer
7. a ranked atlas-pilot program with explicit domain briefs, evidence budgets, governance profiles, and success scorecards so the first pilots do not silently become permanent global defaults

## Initial pilots
Start with a ranked pilot program instead of trying to cover every Rust domain at once:
1. **CLI atlas** with conservative, richer-terminal, and low-footprint lanes
2. **Web service atlas** with explicit runtime / HTTP / middleware / auth / config / database slots
3. **Client-app atlas** with Tauri-oriented, native-UI, and bridge-heavy lanes
4. **Safety-oriented lane** showing how maintenance/trust/support evidence can be weighted more heavily than popularity
5. **Wasm component / plugin pilot** only after the earlier pilots prove the mechanics

Cross-cutting pilot requirements:
- one **Commons-aware pilot** where Atlas references `http` / Tower-style neutral seams instead of pretending stack coherence is magic
- one **Assistant pilot** showing how atlas-derived contexts improve starter guidance and reduce stale “just use crate X” cargo-culting
- a concrete pilot scorecard and governance profile for each pilot, as laid out in [`design/atlas-pilot-program.md`](../design/atlas-pilot-program.md)

## Milestones
### Milestone 1: Canonical artifacts + pilot scaffolding
- publish schemas and examples
- make curator identity, slot choices, evidence, freshness, overlays, and derived outputs all explicit
- publish pilot-domain briefs, evidence budgets, governance profiles, and success scorecards

### Milestone 2: Evidence adapters
- consume crates.io/docs.rs/trust/lifecycle/support signals
- treat community curation as importable input with provenance, not hidden gospel

### Milestone 3: Commons-aware renderers and diffs
- generate guides and assistant contexts from canonical artifacts
- diff recommendation drift and freshness failures cleanly
- let lanes point to shared building-block evidence where relevant

### Milestone 4: Multi-curator adoption
- demonstrate at least two distinct curator groups and several domains using the system without converging on one philosophy

## Success metrics
- New Rust teams bootstrap faster with less re-litigation.
- Interop and migration costs become visible earlier.
- Recommendation freshness becomes auditable instead of folkloric.
- Internal platform teams stop rebuilding bespoke starter-stack spreadsheets from scratch.
- LLM/tooling guidance becomes more bounded and less stale.
- Alternatives remain visible, instead of getting erased by prestige defaults.
- Atlas lanes point to explicit common seams where they exist and explicitly mark where they do not.

## Archive fit
This proposal sits at a strategic junction:
- **Interop Commons** provides the neutral shared seams that good stack guidance should reference.
- **Trust Signals** provides portable trust evidence.
- **Lifecycle Ledger** provides lifecycle and succession truth.
- **Support Envelope** provides support claims.
- **Policy Kit** can consume atlas outputs for org enforcement.
- **Semantic Context Kit** can help generate bounded, machine-usable derivations without becoming the recommendation truth source.
- **Domain kits** provide the deeper technical contracts that an atlas should reference instead of re-explaining.

What none of those owns is **ecosystem orientation itself**.

That is why this could be an epic contribution. It would turn “what should we use?” from a recurring social ritual into a reviewable artifact family — one that respects plurality, preserves evidence, and composes with the rest of the ecosystem rather than trying to rule it.
