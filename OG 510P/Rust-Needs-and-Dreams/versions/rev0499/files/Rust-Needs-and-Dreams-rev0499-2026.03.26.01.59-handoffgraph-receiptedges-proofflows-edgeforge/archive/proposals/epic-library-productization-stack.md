# Epic Proposal: Library Productization Stack (`cargo libcheck` + `library-pack/v0`)

## Why this is worthy
Rust’s ecosystem increasingly asks maintainers and downstream users to treat a crate version like a long-lived public product:
- publish is effectively permanent;
- public/private dependencies and semver checking are active upstream priorities;
- Cargo now records richer publish-time source-package truth;
- docs.rs behavior is a real part of user experience;
- ownership and trusted-publishing posture shape release authority;
- support and docs are still consumed as canonical reference.

But the ecosystem still has no single honest handoff for **crate-as-product truth**.

That means reviewers, downstream users, and tools still have to reconstruct the answer from:
- API diffs;
- manifest state;
- docs.rs settings and failures;
- release pages and registry records;
- CI logs;
- README prose;
- and ad hoc trust/policy overlays.

The missing contribution is a thin portable layer above those pieces, not another replacement for them.

## Proposal
Define a **Library Productization Stack** with:
- a reference aggregation CLI, `cargo libcheck`;
- a thin linked bundle, `library-pack/v0`;
- imported evidence from:
  - `api-pack/v0`
  - manifest/dependency/feature reports
  - release/signing/provenance attachments
  - `support-pack/v0`
  - `doc-pack/v0`
  - optional trust/policy/inventory imports
- stable diff and observation artifacts:
  - `library-envelope/v0`
  - `library-observation-report/v0`
  - `library-diff-report/v0`

## Reference CLI shape
- `cargo libcheck export`
  - emit `library-envelope/v0` for one selected package/release subject
- `cargo libcheck observe`
  - emit `library-observation-report/v0` from imported API / manifest / release / support inputs
- `cargo libcheck diff --against <ref|version|path>`
  - emit `library-diff-report/v0`
- `cargo libcheck pack`
  - produce `library-pack/v0`
- `cargo libcheck verify-pack <path>`
  - verify schema versions, checksums, and imported-attachment integrity

This should stay a **thin composition layer**.
It should not replace the lower-layer kits.

## What `library-pack/v0` should contain
- `manifest.json`
- `library-envelope.json`
- `library-observation-report.json`
- optional `library-diff-report.json`
- imported `api-pack` pointer or embedded attachment
- imported manifest/dependency reports
- imported release/signing/provenance attachments
- imported support/docs attachments
- checksums, provenance, and generator identity
- optional trust/policy/inventory import pointers

## Design principles
- **Crate as product, not just package metadata.**
- **Thin imports over new truth engines.**
- **Public API, manifest, release, and support remain distinct truths.**
- **Support/docs posture must be attachable, not inferred from prose.**
- **Release provenance must be visible without becoming a trust score.**
- **Diff product drift, not only item-level API drift.**

## Early implementation order
1. single-crate library release pack
2. docs.rs + feature/default support lane
3. public-dependency + native/build-script lane
4. library drift reports across releases
5. policy/trust/migration/atlas consumer imports

## Non-goals
- a prettier registry frontend;
- a universal crate quality score;
- replacing Cargo publish or docs.rs;
- replacing Public API Kit, Manifest Truth Stack, Release Truth Stack, Support Envelope, or DocProof;
- making package-admission or policy decisions inside the pack itself.

## Success bar
This becomes worthy when a maintainer, downstream user, or tool can answer:
- what this library version publicly exposes;
- what package/feature/docs posture belongs to the supported release;
- what was actually published and with what provenance;
- what docs/examples/support claims were checked;
- and what changed between versions as a library product,

without scraping five different systems and guessing which pieces matter.

## Read this with
- `gaps/library-crates-public-contract-release-and-support-contracts.md`
- `design/library-productization-stack.md`
- `design/library-productization-pilot-program.md`
- `design/public-api-kit.md`
- `design/manifest-truth-stack.md`
- `design/support-envelope-kit.md`
- `design/docproof-kit.md`
