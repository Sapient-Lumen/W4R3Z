# Design: Library Productization Stack (Public API + Manifest Truth + Release Truth + Support Envelope + DocProof)

## Goal
Turn Rust libraries into a **portable productization stack** instead of leaving each crate to express its public contract as a tangle of API diffs, feature flags, docs.rs settings, publish jobs, ownership settings, support prose, and README folklore.

The stack should **not** replace Cargo, crates.io, docs.rs, `cargo-semver-checks`, manifest tooling, release tooling, or policy/trust systems.
It should make them compose better and make supported library behavior reviewable.

## Why this note is needed now
Rust’s current library signals say the missing problem is no longer “can Rust share crates at all?”
They say the missing problem is **what a Rust library can honestly claim to publish, expose, support, and evolve**:
- the 2025 State of Rust survey still says online docs are the canonical reference, even while LLM/editor workflows rise;
- Rust’s 2026 flagships explicitly frame supply-chain progress around public/private dependencies, breaking-change detection, and SBOM generation;
- publishing docs still emphasize that a publish is effectively permanent;
- Cargo now includes `Cargo.lock` in published crates, which strengthens source-release truth;
- crates.io enforces a 300-feature limit for new crates/versions unless granted an exception, proving feature catalogs are ecosystem-facing surfaces;
- docs.rs explicitly documents both metadata-controlled builds and the need to test docs.rs builds in CI because docs can work locally and still fail on docs.rs;
- Cargo owners and crates.io trusted publishing make publisher authority and release provenance real package surfaces;
- the public/private dependencies goal exists because Rust needs a better answer to what dependencies are intentionally part of a library’s public contract.

Together, those signals argue that the missing contribution is **not** another semver checker, manifest linter, registry dashboard, release bot, or docs host.
It is the **boring portable boundary above the ingredients**.

## Stack layers

### 1) Public API Kit: exposed Rust contract truth
Public API owns the **declared and observed public contract**:
- exported surface;
- semver-relevant diffs;
- witness-based compatibility evidence where needed;
- MSRV verification;
- declared-vs-inferred public dependency exposure.

This layer answers questions like:
- “What part of this crate is public contract versus implementation detail?”
- “Which changes are additive, breaking, ambiguous, or waived?”
- “Which dependencies are intentionally exposed through the API?”

Design rule: **public contract truth must not remain trapped in rustdoc pages, release notes, or one-off CI logs**.

### 2) Manifest Truth: feature, dependency, and package posture
Manifest Truth owns the **package-facing author intent surface**:
- package identity and metadata;
- feature catalogs, defaults, optional dependencies, and resolver posture;
- docs.rs metadata and target/docs configuration;
- build-script / native-provider / `links` posture where relevant;
- publisher/source identity imports where needed.

This layer answers questions like:
- “What feature/default matrix is part of the supported library surface?”
- “Which package metadata and docs.rs knobs materially affect user experience?”
- “Which native/build-script assumptions belong to the published crate?”

Design rule: **package truth must not hide inside `Cargo.toml` trivia or generated registry metadata**.

### 3) Release Truth: what was actually published and how
Release Truth owns the **producer-side release boundary**:
- source-package identity and checksums;
- published release provenance;
- trusted-publishing or token-based publish posture;
- signatures, attestations, and artifact attachments where present;
- owner/authority attachments when relevant.

This layer answers questions like:
- “What source package and release evidence correspond to this library version?”
- “How was it published, and what provenance can downstream users inspect?”
- “What changed between candidate and shipped release?”

Design rule: **library release truth must not be inferred from a tag name, a GitHub release page, or a registry timestamp alone**.

### 4) Support Envelope + DocProof: docs/support truth
Support Envelope and DocProof together own:
- supported targets and runtime floors where they matter for the library;
- docs.rs / hosted docs posture;
- checked examples, guides, doctests, transcript or compile-fail teaching evidence;
- support-level language and known partial lanes;
- support-facing distinctions between promised, observed, best-effort, experimental, and docs-only lanes.

This layer answers questions like:
- “Are docs.rs and local docs the same support lane?”
- “Which examples are checked and part of support versus illustrative only?”
- “What target/native/runtime assumptions are actually promised to users?”

Design rule: **one successful local `cargo doc` is not a support contract**.

### 5) Downstream consumers
The stack matters when real consumers can import it honestly:
- **package-admission / policy / trust / inventory** consumers can import library-facing facts without redefining them;
- **migration / release / downstream packaging** consumers can reason about support drift, feature drift, and API drift together without flattening them;
- **atlas / learning / assistant** consumers can describe a crate honestly instead of guessing from README prose and registry metadata;
- **service / client / web / firmware / model / extension** stacks can import library-facing dependencies and support posture without re-describing crate release truth from scratch.

Design rule: **consumers import selected library-productization facts; they do not redefine the stack**.

## What an epic contribution should look like in practice
A worthy contribution here is not “the one true crate dashboard.”
It is a portable boring stack with clear boundaries:

1. **public-contract truth first**
   - prove exported API, semver reasoning, public-dependency exposure, and MSRV truth can travel together for one real crate release;
2. **manifest/package truth second**
   - prove feature/default/docs.rs/package posture can be attached without pretending every manifest field is equally public;
3. **release/provenance truth third**
   - prove source package identity, publish posture, and release attachments can be imported without replacing Cargo or crates.io;
4. **support/docs truth fourth**
   - prove docs.rs, examples, support levels, and target/native assumptions can be checked and attached honestly;
5. **consumer imports fifth**
   - prove package-admission, trust/policy, migration, release, atlas, and assistant consumers can reuse the same facts.

An eventual aggregate artifact may exist, but it should be a **thin linked pack of imported artifacts**, not a mega-schema that erases API truth, manifest truth, release truth, and support truth.

## Proposed aggregate artifact family
A plausible aggregate lane is:
- `library-envelope/v0`
  - subject identity, selected version, imported artifact pointers, and declared product boundary;
- `library-observation-report/v0`
  - what was actually checked or imported for this release;
- `library-diff-report/v0`
  - public/API/feature/docs/support/release drift between two versions;
- `library-pack/v0`
  - thin bundle linking:
    - `api-pack/v0`
    - manifest/dependency reports
    - release-provenance attachments
    - support/docs attachments
    - optional trust/policy/inventory imports

The point is not one new truth engine.
The point is a **reviewable crate-as-product handoff**.

## Ranked first execution lanes
1. **single library release lane**
   - best first exporter because it proves one crate release can carry API, manifest, docs, and release truth together.
2. **docs.rs + feature/default lane**
   - proves hosted docs, docs.rs metadata, and feature/default posture are real product surfaces.
3. **public-dependency + native/build-script lane**
   - proves library-facing dependency and native/provider posture belong in the contract.
4. **support and release drift lane**
   - proves a later release can widen/narrow support/docs posture without hiding behind “same crate, new version”.
5. **consumer lane**
   - proves package-admission, trust, migration, release, and assistant/atlas consumers can import library-productization facts honestly.

## Non-goals
- one giant crates.io score or badge;
- replacing Public API Kit, Manifest Truth Stack, Release Truth Stack, Support Envelope, or DocProof;
- declaring every manifest key to be product-contract truth;
- pretending release provenance automatically proves support;
- flattening public API, feature posture, docs/support, and release authority into one fake “crate quality” number.

## Archive implications
- The archive should now treat **Public API Kit + Manifest Truth Stack + Release Truth Stack + Support Envelope Kit + DocProof Kit** as a coupled **Library Productization Stack** in frontier and priority discussions.
- Future revisions should prefer **public-contract truth, feature/package truth, release/provenance truth, and docs/support truth** over another semver wrapper, manifest linter, registry dashboard, or release bot.
- When Package Admission, Trust, Migration, Atlas, Learning, Release, or downstream productization stacks touch library-facing crate readiness, they should import library-productization artifacts rather than re-describe crate behavior from scratch.

## Read this together with
- `design/public-api-kit.md`
- `design/manifest-truth-stack.md`
- `design/release-pipeline-kit.md`
- `design/distribution-contract-stack.md`
- `design/support-envelope-kit.md`
- `design/docproof-kit.md`
- `design/package-admission-stack.md`
- `design/trust-decision-stack.md`

## References (signals)
- 2025 State of Rust survey:
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Rust in 2026 flagships:
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- Publishing on crates.io:
  https://doc.rust-lang.org/cargo/reference/publishing.html
- Cargo features reference:
  https://doc.rust-lang.org/cargo/reference/features.html
- Cargo changelog:
  https://doc.rust-lang.org/cargo/CHANGELOG.html
- docs.rs metadata:
  https://docs.rs/about/metadata
- docs.rs builds:
  https://docs.rs/about/builds
- Cargo owner:
  https://doc.rust-lang.org/cargo/commands/cargo-owner.html
- crates.io trusted publishing:
  https://crates.io/docs/trusted-publishing
- public/private dependencies goal:
  https://rust-lang.github.io/rust-project-goals/2025h1/pub-priv.html
