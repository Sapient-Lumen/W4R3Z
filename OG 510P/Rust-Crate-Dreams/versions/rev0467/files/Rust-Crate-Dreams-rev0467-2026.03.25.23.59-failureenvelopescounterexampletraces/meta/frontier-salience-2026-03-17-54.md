# Frontier salience snapshot — 2026-03-17 (54)

This pass did **not** promote a new lane.
It sharpened an existing high-value cross-cutting proposal:

- **P-0524 Crate Example Surface Pack Kit** — because the archive still needed a more reviewable answer to the common state where a user has chosen a crate, but still does not know the smallest official path to first success, what that path requires, or what evidence proves it still works.

## Main judgment

The next worthy move here was **not** another docs portal, another tutorial CMS, another snapshot harness, another transcript renderer, or another template generator.
Those tools already exist in partial form.

The sharper missing layer is the **crate-authored first-success contract** above them:

- explicit quickstart support levels,
- explicit prerequisite-origin receipts,
- explicit success-witness receipts,
- explicit scenario-coverage reports,
- explicit docs/example linkage checks,
- and explicit release diffs for first-success drift.

That move is better grounded now because:

- Rust’s 2025 vision work explicitly argues for more supportive interfaces from crates;
- the 2025 State of Rust survey still says online documentation is the preferred canonical reference and studying the code itself is next;
- the API Guidelines explicitly warn that example code is often copied verbatim by users;
- Cargo still gives `examples/` first-class target status and compiles them under `cargo test` by default to protect them from bit-rot;
- rustdoc scraped examples can bridge `examples/` back into docs, but they remain unstable;
- docs.rs metadata and sandbox policy can materially change the visible docs/example story;
- `trycmd` already covers a real CLI example-testing slice;
- `term-transcript` already covers a real transcript-rendering slice;
- `mdBook` already covers guide/book publishing;
- and `cargo-generate` already covers project templating.

So the gap is no longer “Rust has no examples” or “Rust has no onboarding tools”.
The gap is that maintainers still rarely publish a **reviewable first-success / prerequisite / witness / scenario-coverage contract** above those pieces.

## Broad portfolio ranking after this pass

1. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit** — still the clearest cross-domain answer to “what should we actually reach for?”
2. **P-0520 Crate Lifecycle Surface Pack Kit** — still one of the strongest support-truth lanes once a crate is chosen.
3. **P-0484 Toolchain & Target Support Contract Kit** — still one of the strongest “real machines, real targets” support lanes.
4. **P-0519 Crate Authority Surface Pack Kit** — still one of the strongest ambient-power review lanes.
5. **P-0451 Cfg Availability Ledger Kit** — still one of the highest-leverage conditional-API truth lanes.
6. **P-0510 Crate Capability Contract & Interop Profile Kit** — still the strongest producer-side fact surface for a single crate.
7. **P-0524 Crate Example Surface Pack Kit** — now more believable as a first-success contract because prerequisite origin, success witness, and scenario coverage are separate review objects instead of one vague “the README has examples” story.
8. **P-0525 Crate Diagnosis Surface Pack Kit** — still the strongest steady-state troubleshooting lane once a user is past first success.
9. **P-0513 Crate Runtime Handoff Pack Kit** — still the strongest post-failure support-bundle lane.
10. **P-0512 Crate Guidance Pack Kit** — still the strongest compile-time recovery lane.

## Why this won over adjacent candidates right now

- It beat **more diagnosis follow-ons** because the archive had already made “when things go wrong” more concrete than “how a new adopter gets to success.”
- It beat **more docs.rs parity follow-ons** because hosted-docs fidelity is not the same question as first-success support.
- It beat **more test-surface follow-ons** because downstream testing support still does not tell users which example path is official.
- It beat **more template/tutorial work** because scaffolding a new project and publishing a book are adjacent but different from validating a chosen crate’s first supported path.

## What changed in the archive

Added:
- `meta/frontier-salience-2026-03-17-54.md`
- `entries/2026-03-17-234.md`
- `fixtures/crate-example-surface-pack-kit/prerequisite-origin.receipt.schema.json`
- `fixtures/crate-example-surface-pack-kit/success-witness.receipt.schema.json`
- `fixtures/crate-example-surface-pack-kit/scenario-coverage.report.schema.json`
- `fixtures/crate-example-surface-pack-kit/readme_quickstart_hidden_feature_origin/`
- `fixtures/crate-example-surface-pack-kit/scraped_example_present_but_no_official_success_witness/`
- `fixtures/crate-example-surface-pack-kit/credentialed_service_only_path_needs_scenario_honesty/`

Updated:
- `proposals/crate-example-surface-pack-kit.md`
- `meta/crate-example-surface-product-plan-2026-03-17.md`
- `README.md`
- `INDEX.md`
- `meta/roadmap.md`
- `meta/research-ledger.md`
- `meta/known-existing.md`
- `meta/decision-log.md`
- `meta/llm-hygiene.md`

## What this pass deliberately did not do

It did **not** collapse:

- README examples,
- rustdoc examples,
- docs.rs surfaced examples,
- test harnesses,
- transcript renderers,
- templates,
- and tutorial books

into one fake “example support” story.

## Sources

- https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://rust-lang.github.io/api-guidelines/documentation.html
- https://doc.rust-lang.org/cargo/reference/cargo-targets.html
- https://doc.rust-lang.org/rustdoc/scraped-examples.html
- https://docs.rs/about/metadata
- https://docs.rs/about/builds
- https://docs.rs/trycmd/latest/trycmd/
- https://docs.rs/term-transcript/latest/term_transcript/
- https://docs.rs/crate/mdbook/latest
- https://docs.rs/crate/cargo-generate/latest
