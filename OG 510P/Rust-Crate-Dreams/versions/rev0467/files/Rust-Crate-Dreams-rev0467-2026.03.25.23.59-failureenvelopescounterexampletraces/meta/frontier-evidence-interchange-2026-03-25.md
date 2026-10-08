# Frontier evidence-interchange board — 2026-03-25

This pass keeps the broad frontier stable, but changes what the archive should now ask of the leading lanes:

**Which lane can define a shared evidence-exchange contract that other lanes can import instead of each inventing their own packet format?**

## Main judgment

The next practical build slice should be ranked by **interchange leverage**:

1. how much official machine-usable substrate the lane can already import;
2. how cleanly it can define versioned reviewed bundles versus raw receipts;
3. how many other lanes could reuse its profile and verifier semantics;
4. and how honestly it can state downgrade / refusal / unknown behavior.

## Evidence-interchange leverage board

### 1. P-0472 + P-0484
**Role:** support-envelope protocol-defining ring

Why first under this lens:
- it already sits closest to docs/build/target/toolchain truth;
- it can import official machine-usable surfaces with less policy inflation than other lanes;
- and it is the cleanest place to define a first shared bundle schema.

What the crate should provide:
- profile manifests for named receiver postures,
- exchange bundles for docs/build/target/toolchain claims,
- verifier output that checks bundle/schema/basis compatibility,
- and stable separation between raw receipts and reviewed claims.

### 2. P-0509 + P-0536 + minimal P-0535
**Role:** selection / knowledge / continuity consumer front door

Why second:
- it is still the main human adoption surface;
- but its best shape is to **consume and freeze** exchanged bundles from the support ring and continuity ring;
- it should reward reusable protocol-shaped evidence over bespoke narrative.

What the crate should provide:
- decision packets that import exchange bundles,
- basis locks that pin imported bundle versions,
- compatibility warnings when bundle profiles drift,
- and handoff summaries that distinguish imported truth from archive inference.

### 3. P-0431 + P-0496 + P-0125
**Role:** continuity / parity / carry-forward exchange ring

Why third:
- mirror, source, and carry-forward work already depends on portable evidence and basis continuity;
- recent registry/security realities reward reviewable parity bundles rather than prose claims;
- and this lane is the strongest next place to prove that the same interchange doctrine survives time and distribution changes.

What the crate should provide:
- parity and carry-forward bundles,
- registry/mirror/source basis pointers,
- exchange verification against prior bundles,
- and clear supersession and expiry rules.

### 4. P-0486
**Role:** debugger matrix exchange kit

Why fourth:
- very important,
- but the matrix surface is heavier and should borrow the shared profile/verifier doctrine once the support ring proves it.

What the crate should provide:
- matrix-profile manifests,
- debug claim bundles,
- probe receipts kept separate from reviewed posture,
- and downgraded/refused outputs for incomplete matrix coverage.

### 5. P-0537
**Role:** compile/build iteration exchange

Why fifth:
- build-analysis substrate is becoming more machine-usable;
- but the exchange doctrine should be proven on support truth before iteration truth borrows it.

### 6. P-0538
**Role:** concurrency semantics comparison

Why sixth:
- still highly salient,
- but should not invent a portable interchange protocol until its scenario semantics are more stable.

## Interchange doctrine in one sentence

A worthy crate should increasingly answer **“what bundle can another tool validate and reuse?”** rather than only **“what report can this CLI print?”**

## Promotion rule after this pass

Do not call a lane interchange-ready until the archive can name:
1. the receiver profiles,
2. the reviewed bundle schema,
3. the raw receipt stream,
4. the verifier output,
5. the schema/version policy,
6. and the downgrade / refusal states.

## Sources

- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- https://docs.rs/about/rustdoc-json
- https://docs.rs/about/metadata
- https://docs.rs/about/download
- https://doc.rust-lang.org/rustc/target-tier-policy.html
- https://rust-lang.github.io/rust-project-goals/2025h1/cargo-semver-checks.html
- https://rust-lang.github.io/rust-project-goals/2025h1/libtest-json.html
- https://rust-lang.github.io/rust-project-goals/2025h1/verification-and-mirroring.html
- https://rust-lang.github.io/rust-project-goals/2025h2/open-namespaces.html
- https://rust-lang.github.io/rust-project-goals/2025h2/pub-priv.html
- https://rust-lang.github.io/rust-project-goals/2025h1/stable-mir.html
