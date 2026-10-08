# Design: Publishable library default lane

## Thesis
The defaults corpus currently helps **application teams** more than it helps **crate authors**.
That is now the biggest gap inside the maintained corpus.

A publishable Rust library needs a default lane that is less about framework choice and more about:
- manifest truth,
- public API boundary truth,
- docs.rs truth,
- semver/release truth,
- and supply-chain / package-identity hygiene.

In other words:
the missing contribution is not “another great library”.
It is a **reviewable boring-default lane for crates that intend to be reused and published**.

Read with:
- `design/reviewable-lane-defaults-corpus.md`
- `design/lane-default-evaluation-framework.md`
- `design/lane-default-evidence-bundle.md`
- `design/lane-default-renewal-receipts.md`
- `defaults/conservative-publishable-library-2026Q1.md`
- `evidence/conservative-publishable-library-2026Q1-renewal-2026-03-22.md`

## Why this now
Several current official signals converge unusually hard on this seam.

1. Rust’s March 20, 2026 challenges post still says ecosystem navigation suffers from **choice paralysis** and **tacit knowledge**.
   https://blog.rust-lang.org/2026/03/20/rust-challenges/

2. The 2025 State of Rust survey says online docs remain the preferred canonical reference even while LLM/editor-mediated learning rises.
   https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/

3. The 2026 goals page explicitly treats **public/private dependencies** and **Cargo SBOM precursor** as “Secure your supply chain” work, which makes library API boundary discipline a current Rust priority rather than a niche concern.
   https://rust-lang.github.io/rust-project-goals/2026/flagships.html

4. The `cargo-semver-checks` merge path is now official enough that “semver gate before publish” is no longer just a nice extra. It is part of Cargo’s visible future direction.
   https://rust-lang.github.io/rust-project-goals/2024h2/cargo-semver-checks.html

5. crates.io now exposes stronger public review surfaces — Security tab, Trusted Publishing only mode, SLOC, `pubtime`, and Browse source links — which makes a reviewable publishable-library lane much more plausible than it used to be.
   https://blog.rust-lang.org/2026/01/21/crates-io-development-update/

6. docs.rs has a clearer documented build/config surface than many teams remember: automatic builds for crates.io releases, `[package.metadata.docs.rs]`, and the `cargo docs-rs` helper for CI.
   https://docs.rs/about/builds
   https://docs.rs/about/metadata
   https://docs.rs/crate/cargo-docs-rs/latest

Taken together, this says the next worthy corpus move is not another app-card first.
It is a **publishable library lane**.

## The missing problem
Rust teams routinely know how to write a reusable crate, but still lack a boring, portable answer to:
- what should every publishable crate prove before release?
- what belongs in the manifest versus CI folklore?
- what should be treated as public API surface rather than “internal detail”?
- when should serialization, error types, runtime choices, and dependency names be treated as part of the contract?
- how should docs.rs behavior be tested before publish rather than after breakage?

Existing advice is usually split across:
- general Cargo docs,
- SemVer lore,
- release automation blogs,
- and maintainer memory.

The defaults corpus can do something better:
**one reviewable lane card plus one readable receipt**.

## What the default lane should optimize for
This lane is for crates that value:
- boring reuse,
- conservative public API evolution,
- canonical documentation,
- and reviewable release discipline.

It should optimize for:
- explicit `Cargo.toml` contract shape;
- docs that survive docs.rs;
- release gates that check compatibility before publish;
- low-confusion dependency / package identity;
- and visible caveats when a crate’s API intentionally exposes external types.

It should not optimize for:
- the cleverest macro story,
- the smallest possible manifest,
- or maximum short-term release velocity.

## Proposed lane shape
The lane should keep six truths separate.

### 1. Manifest truth
The crate should declare:
- `rust-version`;
- basic package metadata needed for reuse (`license`, repository/docs/readme fields as applicable);
- explicit feature shape;
- and any docs.rs-specific metadata needed for documentation builds.

Canon:
- https://doc.rust-lang.org/cargo/reference/manifest.html
- https://doc.rust-lang.org/cargo/reference/rust-version.html
- https://doc.rust-lang.org/cargo/reference/features.html
- https://docs.rs/about/metadata

### 2. Docs truth
The lane should treat docs.rs as part of the public contract, not a best-effort afterthought.
That means:
- docs should build on docs.rs;
- `cargo docs-rs` belongs in CI when docs.rs metadata or `cfg(docsrs)` behavior matters;
- and docs-facing features should be deliberate, not accidental.

Canon:
- https://docs.rs/about/builds
- https://docs.rs/crate/cargo-docs-rs/latest

### 3. Public API boundary truth
A reusable library must decide which types, errors, and dependency-shaped surfaces are actually public.
This is where the lane should push authors toward:
- deliberate public error types;
- conservative exposure of foreign dependency types;
- and explicit watchfulness around public/private dependency posture.

Canon:
- https://doc.rust-lang.org/cargo/reference/semver.html
- https://doc.rust-lang.org/cargo/reference/unstable.html
- https://rust-lang.github.io/rust-project-goals/2026/flagships.html

### 4. Semver gate truth
Semver should be checked before publish, not only explained afterward.
The lane should therefore normalize:
- `cargo-semver-checks` in release review for publishable crates;
- manifest-sensitive compatibility thinking, not only rustdoc-JSON-only thinking;
- and an explicit override posture when a crate knowingly breaks.

Canon:
- https://rust-lang.github.io/rust-project-goals/2024h2/cargo-semver-checks.html
- https://crates.io/crates/cargo-semver-checks
- https://doc.rust-lang.org/cargo/reference/semver.html

### 5. Registry / supply-chain truth
The lane should import:
- Security-tab state;
- exact crate identity;
- Trusted Publishing posture where available;
- SLOC/source-link/publication-time review inputs;
- and package-admission consequences when dependencies are intentionally public.

Canon:
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- https://rustsec.org/advisories/

### 6. Renewal receipt truth
The lane should produce a readable receipt that says:
- why the card still stands;
- what was rechecked;
- what remains caveated;
- and whether the judgment is lane-level or package-level.

Canon:
- `design/lane-default-renewal-receipts.md`
- `evidence/conservative-publishable-library-2026Q1-renewal-2026-03-22.md`

## A thin companion-tool shape
If this became a tool contribution, the right shape would be thin:
- `cargo library-lane`
- or `publishable-library-pack/v0`

It should do boring import-and-check work:
- read manifest truth;
- inspect docs.rs metadata;
- run `cargo docs-rs` when configured;
- run `cargo-semver-checks` against the last published baseline or selected tag;
- capture exact dependency identifiers;
- and emit a readable receipt.

It should **not** become:
- a full release bot;
- a crates.io replacement;
- a universal library-quality score;
- or a one-click “publish safely” brand.

## MVP for this archive
The archive does not need the tool first.
The MVP is:
1. a design note for the lane;
2. a default card;
3. a first receipt;
4. frontier updates so later revisions renew it rather than forget it.

## Why this is worthy
This would be a worthy Rust ecosystem contribution because it would:
- improve one of the most common cross-project Rust activities: publishing reusable crates;
- translate current Cargo/crates.io/docs.rs direction into something teams can actually adopt;
- reduce repeated errors around semver, docs.rs, and public dependency exposure;
- and create a bridge between the defaults corpus and the archive’s older **Package Admission**, **Canonical Learning**, and **Maintenance Reality** work.

It also learns the right lesson from the present moment:
the ecosystem is not merely missing more crates.
It is missing more **reviewable contract defaults** around the crates people publish.

## Non-goals
- choosing a universal release automation tool;
- treating every library like a crates.io package from day zero;
- forcing `serde` or `thiserror` into every public crate;
- pretending one card replaces package-admission or support-envelope review;
- or saying the library lane is more important than the archive’s long-running Build-State Evidence frontier.
