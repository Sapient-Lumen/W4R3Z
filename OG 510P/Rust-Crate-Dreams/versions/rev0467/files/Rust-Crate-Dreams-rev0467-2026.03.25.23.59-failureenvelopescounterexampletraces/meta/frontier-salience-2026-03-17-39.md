# Frontier salience snapshot — 2026-03-17 (39)

This pass promoted a new cross-cutting crate lane:

- **P-0524 Crate Example Surface Pack Kit** — because the archive still had no good receiver-facing artifact for the most ordinary adoption question after crate choice: *what is the smallest officially supported path to first success, and which example should a user trust?*

## Main judgment

The next worthy crate in the supportiveness frontier was **not** another docs portal, tutorial CMS, or generic example-testing helper.
Those pieces already exist in partial form.
The sharper missing layer is the **crate-authored contract** for example support:

- official quickstarts,
- support-level taxonomy,
- environment assumptions,
- docs/example linkage,
- expected success signals,
- and release-to-release diffs of that surface.

That move is now better grounded because:

- the Rust vision-doc explicitly argues for more supportive interfaces from crates,
- the 2025 State of Rust survey says docs and code remain the main learning surfaces while debugging still matters,
- Rust API Guidelines say example code is often copied verbatim by users,
- Cargo gives `examples/` first-class targets and compiles them by default with `cargo test`,
- rustdoc and RFC 3123 already try to bridge documentation and examples,
- docs.rs gives crates metadata hooks and a constrained docs build environment,
- and tools like `trycmd`, `trybuild`, and `skeptic` already cover slices of executable or checked examples.

So the gap is no longer “Rust has no examples”.
The gap is that crates still rarely publish a **reviewable onboarding / quickstart / example-support contract** above that substrate.

## Broad portfolio ranking after this pass

1. **P-0524 Crate Example Surface Pack Kit** — strongest cross-domain adoption / first-success artifact now missing.
2. **P-0484 Toolchain & Target Support Contract Kit** — still one of the sharpest practical support-truth lanes for real users on real machines.
3. **P-0451 Cfg Availability Ledger Kit** — still a deeply leverageful way to make portability and conditional API truth reviewable.
4. **P-0472 Docs.rs Build Parity Evidence Kit** — critical adjacent lane, but narrower than the full example-surface contract.
5. **P-0121 FFI Boundary & Bindings Conformance Kit** — still a high-value bridge for Rust↔foreign adoption.
6. **P-0197 Text Layout Conformance Kit** — still a large missing boring default outside Cargo-heavy work.
7. **P-0200 WebAuthn & Passkeys Interop + Device Lab Kit** — still a standout domain-specific workbench with very real ecosystem pain.

## Why this won over adjacent candidates right now

- It beat **toolchain-support** follow-ons because first-success confusion remains a more universal blocker than one more environment-specific support receipt.
- It beat **docs.rs parity** follow-ons because docs.rs is one slice of the problem, not the full receiver-facing example surface.
- It beat **availability-ledger** follow-ons because users often get lost before conditional-support truth even becomes the next question.
- It beat several strong **FFI/domain workbenches** because this lane multiplies value across almost every crate family rather than one domain at a time.

## What changed in the archive

Added:
- `proposals/crate-example-surface-pack-kit.md`
- `meta/crate-example-surface-lanes-2026-03-17.md`
- `meta/frontier-salience-2026-03-17-39.md`
- `entries/2026-03-17-210.md`
- `fixtures/crate-example-surface-pack-kit/`

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

- task-first crate choice,
- failure-path guidance,
- setup/configuration scenarios,
- downstream test support,
- docs.rs parity / hosting,
- tutorial publishing,
- and receiver-facing quickstart / example-surface contracts

into one fake “better Rust docs” story.

## Sources

- https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://rust-lang.github.io/api-guidelines/documentation.html
- https://doc.rust-lang.org/cargo/reference/cargo-targets.html
- https://rust-lang.github.io/rfcs/3123-rustdoc-scrape-examples.html
- https://doc.rust-lang.org/rustdoc/scraped-examples.html
- https://docs.rs/about/metadata
- https://docs.rs/about/builds
- https://docs.rs/trycmd/latest/trycmd/
- https://docs.rs/trybuild/latest/trybuild/
- https://docs.rs/skeptic/latest/skeptic/
