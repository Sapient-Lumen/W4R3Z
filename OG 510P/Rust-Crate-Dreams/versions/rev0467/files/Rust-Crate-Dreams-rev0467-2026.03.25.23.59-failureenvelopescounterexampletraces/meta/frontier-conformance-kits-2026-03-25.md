# Frontier conformance kits — 2026-03-25

This note keeps the frontier broadly stable **while making promise quality more operational**.

The archive no longer needs more sector inflation.
It needs sharper answers to:
- what a crate is actually claiming,
- how another team reviews that claim,
- and what rerun loop keeps the claim honest.

## Main judgment

The strongest missing Rust contributions are still mostly **receiver-facing control-plane kits**.
But many of the leading lanes should now be planned as shipping **conformance kits / promise-tier kits** rather than only packets or reports.

## Conformance-leverage board

### 1. P-0472 + P-0484
**Role:** support-envelope / docs-build-target-toolchain conformance ring

Why first under this lens:
- docs.rs and target/toolchain surfaces are already machine-usable enough to ground honest claims;
- Rust target tiers provide a real model for bounded support semantics;
- and a support-envelope lane is the most natural place to define reusable claim vocabulary.

What the crate should provide:
- a per-dimension support claim,
- basis fields for where the claim came from,
- raw receipts from hosted and local evidence,
- a short support summary,
- and named non-claims.

### 2. P-0509 + P-0536 + minimal P-0535
**Role:** selection / knowledge / continuity front door

Why second:
- it remains the main adoption surface for humans;
- but its best future shape is to **consume** conformance kits from the support ring and continuity ring;
- it should rank crates partly by the quality and freshness of their conformance basis, not only by narrative heuristics.

What the crate should provide:
- comparison packets enriched with imported conformance claims,
- basis locks that freeze those claims,
- recheck tickets when support claims drift,
- and a human-readable explanation of what is merely declared versus what was replayed or exercised.

### 3. P-0486
**Role:** debugger support conformance kit

Why third:
- the need remains clear and official Rust material explicitly highlights debugger / OS / version variance;
- but the matrix burden is heavier, so the first release should stay narrow and extremely explicit.

What the crate should provide:
- debugger matrix profiles,
- probe receipts kept separate from final claims,
- degraded and refused states when the matrix is incomplete,
- and reproducible corpus scenarios for tricky async / pretty-printer / expression-evaluation cases.

### 4. P-0431 + P-0496 + P-0125
**Role:** continuity / parity / carry-forward conformance ring

Why fourth:
- recent registry and advisory realities keep showing that source parity and carry-forward posture are not binary;
- this ring is where claims about mirrors, source availability, inventory, and public-boundary continuity should become reviewable.

What the crate should provide:
- parity claims with source basis,
- carry-forward receipts across releases,
- clear unknown/refused states for alternate-registry gaps,
- and recheck triggers tied to new releases, advisory events, and registry changes.

### 5. P-0537
**Role:** compile/build iteration truth

Why fifth:
- build-analysis substrate is getting stronger,
- but claim vocabulary should be shaped after the support-envelope lane proves a stable pattern first.

### 6. P-0538
**Role:** concurrency semantics comparison

Why sixth:
- very important,
- but its claim vocabulary should likely borrow the same conformance doctrine only after more scenario work.

## Conformance doctrine in one sentence

A worthy crate should increasingly answer **“how supported is this, on which surface, at what evidence tier, as of which basis?”** rather than only **“does it work?”**

## Promotion rule after this pass

Do not call a lane conformance-ready until the archive can name:
1. the claim dimensions,
2. the tier vocabulary,
3. the raw receipt stream,
4. the human summary surface,
5. the recheck trigger set,
6. and the refusal / unknown states.

## Sources

- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- https://blog.rust-lang.org/2026/02/13/crates.io-malicious-crate-update/
- https://blog.rust-lang.org/2026/03/21/cve-2026-33056/
- https://blog.rust-lang.org/2026/03/13/call-for-testing-build-dir-layout-v2/
- https://blog.rust-lang.org/2025/10/16/docsrs-changed-default-targets/
- https://blog.rust-lang.org/2025/10/30/Rust-1.91.0/
- https://docs.rs/about/builds
- https://docs.rs/about/metadata
- https://docs.rs/about/rustdoc-json
- https://docs.rs/about/download
- https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
- https://rust-lang.github.io/rust-project-goals/2025h1/libtest-json.html
- https://rust-lang.github.io/rust-project-goals/2025h1/pub-priv.html
- https://rust-lang.github.io/rust-project-goals/2025h1/cargo-semver-checks.html
