# Top-lane interchange profiles — 2026-03-25

This pass assumes the archive’s frontier remains broadly stable.
The new question is:

**Which leading lanes should define or consume the shared evidence-interchange contract first?**

## 1. P-0472 + P-0484
**Role:** support-envelope interchange foundation

Why first:
- it can already import docs.rs build metadata, rustdoc JSON, docs download archives, local replay receipts, and target-tier semantics;
- it is the cleanest place to define stable profile and bundle semantics without overclaiming;
- and many later lanes can reuse its verifier and profile vocabulary.

What the crate should provide:
- `profile-manifest.json` for support postures,
- `exchange-bundle.json` for docs/build/target/toolchain claims,
- `receipt-stream.jsonl` for imported and replayed evidence,
- `bundle-verify.json` for profile/schema/basis checks,
- and `support-summary.md` for human review.

Likely `0.1` package family:
- `support-envelope-core`
- `support-envelope-schema`
- `support-envelope-verify`
- `cargo-support-envelope`
- bounded docs.rs / rustc / cargo adapters

## 2. P-0509 + P-0536 + minimal P-0535
**Role:** selection and handoff consumer

Why second:
- it remains the main front door for people;
- but its strongest future shape is to import exchanged support/continuity bundles rather than create a private packet universe;
- and it is where bundle compatibility should meet real review and adoption decisions.

What the crate should provide:
- decision packets that embed imported exchange bundles by reference or snapshot,
- basis locks that pin bundle/profile/schema versions,
- compatibility warnings when imports drift,
- and short handoff summaries that keep imported evidence distinct from archive inference.

Likely `0.1` package family:
- `pathfinder-core`
- `pathfinder-schema`
- `pathfinder-import`
- `cargo-pathfinder`
- `pathfinder-verify`

## 3. P-0431 + P-0496 + P-0125
**Role:** continuity and parity exchange ring

Why third:
- mirror/source/carry-forward work already needs portable evidence across releases and environments;
- it can prove that the same bundle doctrine survives time and distribution changes;
- and recent registry/security work makes portable parity claims more valuable.

What the crate should provide:
- parity bundles,
- carry-forward bundles,
- mirror/source basis pointers,
- supersession receipts,
- and advisory/release-triggered recheck semantics.

Likely `0.1` package family:
- `continuity-core`
- `continuity-schema`
- `continuity-verify`
- `cargo-continuity`
- bounded registry/mirror adapters

## 4. P-0486
**Role:** debugger matrix exchange borrower

Why fourth:
- strong receiver need;
- but it should borrow profile/verifier semantics after the support ring proves them;
- matrix churn argues for a narrower first contract.

What the crate should provide:
- matrix-profile manifests,
- debug support bundles,
- raw probe receipts,
- degraded/refused outputs,
- and explicit compatibility limits by debugger, OS, version, and async surface.

## 5. P-0537
**Role:** build-analysis exchange later

Why fifth:
- build-analysis work is promising,
- but the support ring should define the first shared verifier and profile vocabulary.

What the crate should provide later:
- build-observation bundles,
- rebuild-reason receipts,
- compatibility reports across runs,
- and CI/cache-friendly exchange surfaces.

## 6. P-0538
**Role:** scenario-heavy semantics lane

Why sixth:
- still highly salient,
- but it should borrow rather than define the first portable bundle doctrine.

What the crate should provide later:
- scenario-anchored semantic bundles,
- raw witness traces,
- matrix/profile manifests,
- and explicit unknown/refusal ceilings.

## Shared rule after this pass

The archive should now prefer:
- **one shared interchange doctrine**
over
- six barely compatible packet families.

A later lane may specialize the doctrine, but it should not re-invent it without a concrete reason.

## Sources

- https://docs.rs/about/rustdoc-json
- https://docs.rs/about/builds
- https://docs.rs/about/metadata
- https://docs.rs/about/download
- https://doc.rust-lang.org/rustc/target-tier-policy.html
- https://rust-lang.github.io/rust-project-goals/2025h1/cargo-semver-checks.html
- https://rust-lang.github.io/rust-project-goals/2025h1/libtest-json.html
- https://rust-lang.github.io/rust-project-goals/2025h1/verification-and-mirroring.html
- https://rust-lang.github.io/rust-project-goals/2025h2/pub-priv.html
- https://rust-lang.github.io/rust-project-goals/2025h1/stable-mir.html
