# Epic Proposal: Package Admission Stack (`cargo package-admission` + `package-admission-pack/v0`)

## Why this is worthy
Rust increasingly needs **package publication to be reviewable as an evidence-backed admission decision instead of a pile of loosely related checks**.

The ecosystem signals are unusually aligned:
- Rust’s 2026 flagship roadmap keeps **Secure your supply chain** active and explicitly names **public/private dependencies** and **SBOM generation** as milestones. That means the publish boundary is now upstream strategy, not only downstream enterprise policy.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- The public/private dependencies goal exists specifically to help users catch accidental implementation-detail exposure and help tooling determine what constitutes an API. That is exactly the kind of signal a package-admission layer should import instead of re-deriving.
  https://rust-lang.github.io/rust-project-goals/2025h1/pub-priv.html
  https://doc.rust-lang.org/cargo/reference/unstable.html
- `cargo-semver-checks` remains on the path toward Cargo / publish integration, and its goal text explicitly frames publish-time SemVer checking as part of the desired workflow. That makes public-contract review part of the publication boundary rather than a purely optional afterthought.
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-semver-checks.html
  https://rust-lang.github.io/rust-project-goals/2024h2/cargo-semver-checks.html
- Cargo packaging docs say `Cargo.lock` is always included in packaged crates unless explicitly excluded, that `.cargo_vcs_info.json` is only best-effort and not verified provenance, and that `cargo package --list` has an unstable machine-readable JSON mode. That is a strong reminder that package publication already carries real payload truth, but the ecosystem still lacks one review boundary above it.
  https://doc.rust-lang.org/cargo/commands/cargo-package.html
- The Cargo Book’s features reference says crates.io limits newly published crates or versions to **300 features** unless an exception is granted. That is not just a registry implementation quirk; it means manifest and feature posture already participate in publication realism.
  https://doc.rust-lang.org/cargo/reference/features.html
- The Cargo Book’s publishing reference says crates.io is intended to be a permanent archive and that yanking is the reversible mechanism, not deletion. That means publication is durable enough to deserve a first-class review layer.
  https://doc.rust-lang.org/cargo/reference/publishing.html
- crates.io’s January 2026 development update added **Trusted Publishing Only Mode**, blocked risky GitHub triggers for Trusted Publishing, and added the `pubtime` field to the index. Those are strong package-admission ingredients, but they still do not add up to one explainable publish bundle.
  https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- crates.io’s February 2026 malicious-crate notification update says routine malware removals will always get a RustSec advisory and that blog-post escalation is reserved for materially used or exploited cases. That makes advisory and registry signals more regular inputs into package review rather than rare exceptional artifacts.
  https://blog.rust-lang.org/2026/02/13/crates.io-malicious-crate-update/

But the ecosystem still has no single honest handoff for **package-admission truth** above publish-set facts and below broader release/install consumers.

That means maintainers, registries, downstream packagers, and policy tools still have to reconstruct the story from:
- selected package sets, packaged payloads, verification controls, and index receipts;
- chosen dependency graphs and feature posture;
- public-contract drift and semver evidence;
- SBOM / inventory artifacts with differing scopes and lossiness;
- publisher, freshness, and name-risk signals;
- CI-specific publish policy and waivers;
- and registry-side security or moderation cues.

The missing contribution is a thin composition layer above those pieces, not a publish wrapper, registry score, or another universal release platform.

## Proposal
Define a **Package Admission Stack** with:
- a reference companion CLI, `cargo package-admission`;
- a thin linked bundle, `package-admission-pack/v0`;
- imported evidence from:
  - `publish-pack/v0`,
  - dependency-control reports,
  - `api-pack/v0`,
  - `inventory-pack/v0`,
  - `trust-pack/v0`,
  - `policy-pack/v0`,
  - optional raw attachments such as normalized packaged manifests, lockfile snapshots, feature catalogs, registry summary data, and RustSec/advisory imports;
- stable package-admission-facing artifacts:
  - `package-subject/v0`
  - `package-graph-report/v0`
  - `package-exposure-report/v0`
  - `package-admission-brief/v0`
  - `package-release-handoff/v0`
  - `package-admission-pack/v0`

## Reference CLI shape
- `cargo package-admission graph`
  - emit `package-subject/v0` and `package-graph-report/v0` from imported `publish-pack/v0` plus dependency-control inputs, including selected package set, selected versions, sources, features, public/private posture, and lock/publish-time notes
- `cargo package-admission exposure`
  - emit `package-exposure-report/v0` from imported public-API evidence
- `cargo package-admission review`
  - emit `package-admission-brief/v0` from publish-set, graph, exposure, inventory, trust, and policy imports
- `cargo package-admission handoff --for <release|registry|downstream|support|assistant>`
  - emit `package-release-handoff/v0`
- `cargo package-admission pack`
  - produce `package-admission-pack/v0`
- `cargo package-admission verify-pack <path>`
  - verify schema versions, checksums, imported-attachment integrity, and explicit package-vs-release boundary markers

This should stay a **thin composition layer**.
It should not replace Cargo, crates.io moderation, RustSec, cargo-vet, binary-release tooling, or downstream distro-specific review systems.

## What `package-admission-pack/v0` should contain
- `manifest.json`
- `package-subject.json`
- `package-graph-report.json`
- `package-exposure-report.json`
- `package-admission-brief.json`
- optional `package-release-handoff.json`
- imported `publish-pack`, `api-pack`, `inventory-pack`, `trust-pack`, and `policy-pack` pointers or embedded attachments
- optional normalized packaged `Cargo.toml` and `Cargo.lock` attachments or checksummed pointers
- checksums, provenance, freshness, registry identity, and generator identity
- visible import-lossiness and `INCONCLUSIVE` markers

## Design principles
- **Publish-set truth comes first.** If the package cannot say which package(s), payload, checks, and receipts were under review, later admission claims are already suspect.
- **Graph truth comes next.** If the package cannot say what versions, sources, features, and public/private choices it actually published against, later review is already suspect.
- **Exposure is not the same as inventory.** Public API drift and component presence are related but not interchangeable.
- **Trust signals are inputs, not verdicts.** Publisher, freshness, name-risk, and advisory data should feed review without silently turning into one score.
- **Package scope is not release scope.** A `.crate` upload is not the same thing as signed binaries, installers, or support statements.
- **Durability matters.** Package publication is persistent enough that waivers and incompleteness must be reviewable later.
- **Companion-tool success is real success.** Becoming a reusable companion to Cargo and crates.io is already a worthwhile outcome.
- **Downstream consumers get bounded handoffs.** Registries, distro packagers, support pages, and assistants should import explicit summaries instead of freelancing from raw artifacts.

## Early implementation order
1. single-crate publish-review lane
2. workspace publish-group lane
3. proc-macro / build-lane scrutiny lane
4. package-to-release handoff lane
5. registry / downstream consumer lane

That order follows the real pressure gradient: first make ordinary publication reviewable, then handle multi-crate reality, then sharpen the highest-risk package classes, then preserve the release boundary, and only after that widen into thinner consumers.

## Non-goals
- a universal crate-risk score;
- a crates.io moderation replacement;
- a new monopoly `cargo publish` wrapper;
- a binary-release umbrella that swallows package truth;
- a trust or policy engine that hides waivers and uncertainty;
- a dashboard that pretends package upload alone settles downstream installation or operational risk.

## Success bar
This becomes worthy when a maintainer, registry, or downstream consumer can answer:
- what graph and feature posture was actually admitted;
- what public contract changed and why it matters;
- what inventory evidence exists and what remains lossy;
- what publisher / freshness / advisory / name-risk signals were visible;
- what rule set and waivers produced the decision;
- what still belongs to later release or distribution layers;
- and what changed since the last admission,

without reconstructing the story from raw manifests, CI glue, registry metadata, and issue threads.

## Read this with
- `design/package-admission-stack.md`
- `design/package-admission-pilot-program.md`
- `design/dependency-control-stack.md`
- `design/public-api-kit.md`
- `design/sbom-evidence-kit.md`
- `design/trust-signals-kit.md`
- `design/policy-kit.md`
- `design/release-pipeline-kit.md`
