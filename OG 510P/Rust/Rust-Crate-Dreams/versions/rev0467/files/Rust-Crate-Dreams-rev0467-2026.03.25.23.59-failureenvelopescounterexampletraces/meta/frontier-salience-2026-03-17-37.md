# Frontier salience scan — 2026-03-17 (crate persistence surfaces promoted as the durable-bytes / recovery-truth lane)

This pass added a new top-level proposal: **P-0522 Crate Persistence Surface Pack Kit**.
It sharpens the archive’s crate-ecosystem frontier by adding a fourteenth distinct supportiveness lane next to **P-0509** (task-first crate choice), **P-0510** (producer-side capability contracts), **P-0511** (shared interop profiles), **P-0512** (compile-time / early-failure guidance), **P-0513** (runtime handoff/support bundles), **P-0514** (release-to-release upgrade packs), **P-0515** (deprecation/successor off-ramp packs), **P-0516** (configuration/setup scenarios), **P-0517** (performance envelopes), **P-0518** (observability surfaces), **P-0519** (authority surfaces), **P-0520** (lifecycle surfaces), and **P-0521** (resource surfaces).

## Main judgment

The strongest new cross-cutting contribution here is not:

- another serializer crate,
- another embedded database,
- another migration runner,
- another schema-reflection helper,
- or another storage-engine README.

It is the boring crate that can hand other people:

- one **persistence pack**,
- one **persistence-surface receipt**,
- one **format-compat report**,
- one **durability-boundary report**,
- one **recovery-posture report**,
- one **migration-recipe manifest**,
- one **compatibility-window report**,
- one **persistence-check report**,
- and one **persistence diff**.

## Broad ranking after this pass

1. **P-0468 Cargo Resolver Explanation Kit**
2. **P-0035 cargo-build-insights**
3. **P-0469 Cargo Rebuild Explanation Kit**
4. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit**
5. **P-0514 Crate Upgrade Pack Kit**
6. **P-0516 Crate Configuration Scenario Pack Kit**
7. **P-0517 Crate Performance Envelope Pack Kit**
8. **P-0522 Crate Persistence Surface Pack Kit**
9. **P-0521 Crate Resource Surface Pack Kit**
10. **P-0520 Crate Lifecycle Surface Pack Kit**
11. **P-0518 Crate Observability Surface Pack Kit**
12. **P-0519 Crate Authority Surface Pack Kit**
13. **P-0512 Crate Guidance Pack Kit**
14. **P-0513 Crate Runtime Handoff Pack Kit**
15. **P-0515 Crate Off-Ramp Pack Kit**
16. **P-0510 Crate Capability Contract & Interop Profile Kit**
17. **P-0511 Crate Interop Profile Pack Kit**
18. **P-0429 rustc_public Analysis Workbench Kit**

## Why P-0522 moved up

Fresh official and ecosystem signals line up around six sharper truths:

- The December 2025 vision-doc work explicitly recommends **supportive interfaces from crates**, which makes persistence truth a plausible crate support surface rather than a backend implementation footnote.
- The 2025 survey says **docs and code** remain the main learning surfaces, so persisted-state behavior should not be left to folklore and incident archaeology.
- `std::fs::File` already distinguishes durability-relevant boundaries like `sync_data` and `sync_all`, which means even the standard library already exposes more nuance than most crate docs summarize.
- Serde already exposes compatibility knobs like defaults, aliases, unknown-field policy, and enum representation choices, which means schema compatibility is often partly encoded in the crate today even when the support artifact is missing.
- `serde-reflection`, Postcard, `revision`, and redb show the ecosystem already has format-description, stable-wire-format, version-history, and crash-recovery substrate.
- Real user pain is rarely “Rust cannot serialize or persist anything”; it is “what exactly does this crate promise about the bytes it leaves behind, and how do those promises change?”

That means the lane is both:

- **timely** — because the substrate is real enough to support a contract layer now,
- and **distinct** — because the missing value is a crate-authored persistence surface above primitives and below domain-specific format ecosystems.

## What changed in the archive

Added:
- `proposals/crate-persistence-surface-pack-kit.md`
- `meta/crate-persistence-surface-lanes-2026-03-17.md`
- `meta/frontier-salience-2026-03-17-37.md`
- `fixtures/crate-persistence-surface-pack-kit/`
- `entries/2026-03-17-208.md`

Updated:
- `README.md`
- `INDEX.md`
- `meta/crate-frontier-map-2026-03-16.md`
- `meta/known-existing.md`
- `meta/roadmap.md`
- `meta/research-ledger.md`
- `meta/llm-hygiene.md`

## What this pass deliberately did not do

It did **not** collapse:

- upgrade packs,
- setup/configuration scenarios,
- authority posture,
- lifecycle/shutdown truth,
- resource/saturation truth,
- generic serializers,
- embedded storage engines,
- domain schema workbenches,
- and receiver-facing persistence contracts

into one fake “better storage/migration docs” story.

## Sources

- https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://doc.rust-lang.org/std/fs/struct.File.html
- https://serde.rs/
- https://serde.rs/container-attrs.html
- https://serde.rs/field-attrs.html
- https://docs.rs/serde-reflection/latest/serde_reflection/
- https://docs.rs/postcard/latest/postcard/
- https://docs.rs/redb/latest/redb/struct.Database.html
- https://docs.rs/revision/latest/revision/attr.revisioned.html
