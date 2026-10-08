# Pilot program: Library Productization Stack

## Goal
Exercise the smallest set of library-facing lanes that prove the archive’s proposed **Library Productization Stack** is real and useful: public contract truth, package/feature/docs posture, release/provenance truth, and support/docs truth.

This pilot program should produce reusable artifacts and comparison notes.
It should not try to standardize all of crates.io or all release automation.

## Pilot artifact families
- imported `api-pack/v0`
- imported manifest/dependency reports
- imported release/signing/provenance attachments
- imported `support-pack/v0` / `doc-pack/v0` attachments where used
- `library-envelope/v0`
- `library-observation-report/v0`
- `library-diff-report/v0`
- `library-pack/v0`

## Ranked pilot lanes

### Pilot 1: single library release lane
**Why first:**
It proves the narrowest serious case: one crate release should be able to carry its public contract, package posture, release provenance, and docs/support posture together.

**Candidate substrates:**
- one mature library crate with stable docs and release flow;
- one crate already using `cargo-semver-checks` or explicit API review;
- one crate with clear docs.rs metadata and `rust-version` posture.

**What to export:**
- imported `api-pack/v0`;
- feature/default summary and selected manifest/product fields;
- release identity and provenance attachments;
- docs.rs/support/docs evidence attachments;
- `library-envelope/v0` tying the pieces together.

**Success condition:**
A reviewer can answer “what is this library release actually promising?” without scraping rustdoc, Cargo.toml, CI, docs.rs, and GitHub releases separately.

### Pilot 2: docs.rs + feature/default posture lane
**Why second:**
Library users encounter docs and feature defaults before they understand the rest of the release machinery.
This is where many real support misunderstandings begin.

**Candidate substrates:**
- crate with nontrivial feature matrix;
- crate using `[package.metadata.docs.rs]`;
- crate with examples or doctests that materially depend on feature selection.

**What to export:**
- docs.rs metadata summary;
- selected features/defaults relevant to the public contract;
- docs-build check evidence;
- distinction between checked support docs and illustrative examples only;
- drift notes when docs posture and release posture disagree.

**Success condition:**
A reviewer can distinguish “documented somewhere” from “checked and supported in this published product posture.”

### Pilot 3: public-dependency + native/build-script posture lane
**Why third:**
Many library releases look pure-Rust until users cross a feature gate, native provider, or build-script path.
This is exactly where package and public-contract truth start to diverge.

**Candidate substrates:**
- crate with declared/inferred public dependencies;
- crate with optional native/provider lanes;
- crate whose docs or public types expose dependency types conditionally.

**What to export:**
- public/private dependency posture;
- declared-vs-inferred exposure drift;
- build-script / `links` / native-provider notes where relevant;
- support labels for which lanes are truly part of the library product.

**Success condition:**
A reviewer can tell which dependency and native assumptions are part of the supported crate surface versus implementation detail or partial lane.

### Pilot 4: support and release drift lane
**Why fourth:**
The stack matters only if it can compare releases honestly.
Library versions often keep the same crate name while changing docs posture, feature defaults, support targets, release provenance, or package metadata materially.

**Candidate substrates:**
- two adjacent releases of one crate;
- one release published differently or with changed docs.rs/support posture;
- one release with MSRV or feature-default changes.

**What to export:**
- `library-diff-report/v0`;
- public API drift imported from `api-pack`;
- feature/default/docs/support/release drift;
- explicit widened/narrowed/partial support notes;
- optional waiver attachment.

**Success condition:**
A reviewer can see what changed in the crate as a product, not just in the Rust items it exports.

### Pilot 5: downstream-consumer lane
**Why fifth:**
The stack matters only if other archive surfaces can import it.

**Candidate consumers:**
- Package Admission Stack;
- Trust Decision Stack;
- Migration Truth Stack;
- Canonical Learning / Atlas consumers;
- other productization stacks that depend on library crates.

**What to export:**
- one package-admission/policy consumer import;
- one learning/atlas/assistant import;
- one release or migration import;
- consumer-specific notes on what remained unknown or intentionally ignored.

**Success condition:**
A consumer can reuse library-productization facts without re-describing the crate from scratch.

## Comparison questions the pilots should answer
- Which facts are public-contract facts versus package-surface facts?
- Which feature/default/docs.rs choices are part of the supported product boundary?
- Which release/provenance facts are visible and reviewable enough for downstream users?
- Which docs/examples are checked support evidence versus teaching-only material?
- Which support drifts deserve migration/release/policy attention even when semver diff is small?

## Early artifacts worth standardizing
- `library-envelope/v0`
- `library-observation-report/v0`
- `library-diff-report/v0`
- `library-pack/v0`

These are enough to prove the seam without freezing a giant schema too early.

## What this pilot program should resist
- becoming a crates.io clone;
- becoming a universal crate score;
- pretending every manifest field is equally product-relevant;
- calling README prose “support truth” without checked evidence;
- conflating trust/policy decisions with the underlying library facts they import.

## Recommended first implementation order
1. single-crate library release lane
2. docs.rs + feature/default lane
3. public-dependency + native/build-script lane
4. release/support drift lane
5. downstream consumer import lane

## Expected archive follow-ons
- Promote Library Productization Stack in frontier and priority docs.
- Add library-specific amnesia resistance language.
- Make future package-admission, trust, migration, atlas, and release revisions import library-productization facts instead of re-deriving them.
