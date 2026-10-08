# Gap: library crates still lack one honest product boundary

Rust has many strong lower-level ingredients for shipping libraries, but it still lacks a **portable productization layer for a crate as a product**.

Today, serious library maintainers have to assemble the truth out of separate pieces:
- public API diffs and semver checks;
- feature/default/optional/public-dependency posture in `Cargo.toml`;
- docs.rs metadata and whether docs actually build there;
- `rust-version` / MSRV claims;
- release and publish provenance;
- ownership and trusted-publishing posture;
- support language hidden in README prose, examples, release notes, and issue comments.

Those are all real surfaces, but the ecosystem still tends to collapse them into one vague statement:
> “the crate is published and documented, so it is ready.”

That is not good enough anymore.

## Why this now matters more
Several current signals make the missing seam clearer than it used to be:

- The 2025 State of Rust survey says online documentation is still the canonical reference even while LLM/editor workflows rise. That means **crate-facing documentation and support claims are not side channels**; they are part of the product boundary.
- Rust’s 2026 flagships explicitly frame supply-chain work around **public/private dependencies, breaking-change detection, and SBOM generation**. That is already library-facing product work, just without one higher-level library contract joining the parts.
- Cargo’s publishing docs still emphasize that publishing is effectively permanent. Once a version is on crates.io, that release becomes part of the ecosystem’s long-lived public surface.
- Cargo now always includes `Cargo.lock` in published crates, which is another sign that producer-time release truth is becoming richer and more reviewable.
- Cargo features on crates.io are capped at 300 unless an exception is granted. That is a strong signal that feature catalogs are part of the public package surface, not an internal implementation detail.
- docs.rs explicitly documents both per-crate metadata and the need to test docs.rs builds in CI because docs may succeed locally and fail on docs.rs. That means hosted documentation behavior is part of the support surface.
- Cargo owners and crates.io trusted publishing make publisher identity and release authority part of the real package boundary rather than an afterthought.
- Public/private dependencies are an explicit Cargo goal because the ecosystem needs a better answer to “what dependencies are part of the public contract?”

Taken together, the missing problem is no longer “can Rust publish libraries at all?”
The missing problem is:

**what can a Rust library honestly claim to publish, expose, support, document, and evolve?**

## What is missing
The ecosystem needs a portable layer that keeps these truths distinct but composable:

1. **Public contract truth**
   - exposed API surface
   - semver-relevant change evidence
   - MSRV claims and verification
   - public dependency exposure

2. **Manifest and package truth**
   - feature catalog and defaults
   - optional dependency posture
   - build-script / native-provider / `links` posture where relevant
   - docs.rs metadata and target/docs configuration
   - edition / resolver / package metadata

3. **Release truth**
   - what source package was published
   - what release attachments or signatures exist
   - how it was published (local token vs trusted publishing)
   - who owns and can update the crate

4. **Support + docs truth**
   - what docs/examples/tutorials are part of support
   - whether docs.rs is a real supported lane or just a best-effort mirror
   - supported targets / runtime floors / native prerequisites
   - what is promised versus merely shown in examples

5. **Consumer-facing import truth**
   - what downstream users, distros, auditors, CI systems, and assistants are allowed to conclude
   - what remains partial, inferred, unsupported, or waived

## What this should not become
This should **not** become:
- a prettier crates.io page;
- another semver-diff wrapper;
- one more manifest linter;
- a universal “crate quality score”;
- an attempt to replace docs.rs, crates.io, or Cargo publishing;
- a package-admission or trust engine that silently swallows support and docs truth.

The missing contribution is a **reviewable crate-as-product boundary** above the existing point tools.

## What a worthy contribution would look like
A real contribution here would define a thin artifact family and workflow that can:
- import `api-pack`, manifest/dependency evidence, release evidence, support/docs evidence, and optional trust/policy imports;
- produce one honest library-facing pack for release review and downstream consumption;
- diff two releases without flattening API, feature, support, and release provenance into one score;
- let tools answer questions like:
  - “what changed in the crate’s supported public contract?”
  - “did docs/support drift from the actual published release?”
  - “is this public dependency exposure intentional?”
  - “what feature/default/MSRV/docs.rs posture is part of the product?”
  - “what exactly was published, by whom, and with what provenance?”

## Likely shape of the solution
The strongest path is an explicit **Library Productization Stack** that composes:
- **Public API Kit** for public-contract and semver truth;
- **Manifest Surface Kit + Dependency Control Stack** for package/feature/dependency posture;
- **Release Truth Stack** for source-release and provenance truth;
- **Support Envelope + DocProof** for docs/support/target truth;
- optional imports from **Publisher & Source Identity**, **Package Admission**, **Trust Signals**, and **Inventory Evidence** when a consumer needs them.

This would finally let the ecosystem talk about a crate release as a **productized library** rather than a pile of partially-related surfaces.

## Why this belongs in the archive now
The archive already has strong lower layers here.
What it did **not** have yet was the explicit synthesis saying that the next worthy contribution is likely **not** another lower-layer tool at all.
It is the layer that joins those tools into one honest contract for what library users actually bet on.

## References (signals)
- 2025 State of Rust survey:
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Rust in 2026 flagships:
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- Publishing on crates.io:
  https://doc.rust-lang.org/cargo/reference/publishing.html
- Cargo changelog (`Cargo.lock` included in published crates):
  https://doc.rust-lang.org/cargo/CHANGELOG.html
- Cargo features reference:
  https://doc.rust-lang.org/cargo/reference/features.html
- docs.rs metadata:
  https://docs.rs/about/metadata
- docs.rs builds:
  https://docs.rs/about/builds
- Cargo owners:
  https://doc.rust-lang.org/cargo/commands/cargo-owner.html
- crates.io trusted publishing:
  https://crates.io/docs/trusted-publishing
- public/private dependencies goal:
  https://rust-lang.github.io/rust-project-goals/2025h1/pub-priv.html
