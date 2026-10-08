# Hot substrate watchcard: Package + release boundary substrate (2026-03)

## Lane
- package-boundary / release-boundary watch
- drift horizon: **hot**

## Authoritative sources
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- https://blog.rust-lang.org/inside-rust/2026/03/25/project-director-update/
- https://mozilla.github.io/cargo-vet/
- https://embarkstudios.github.io/cargo-deny/checks/index.html
- https://rustsec.org/

## Imported truths
- crates.io service truth for vulnerability visibility is getting richer;
- official Rust work is naming capability analysis and vulnerability surfacing explicitly;
- package-intake remains a split-home seam across service truth, advisory truth, and companion review tooling.

## Non-claims
- package intake is not solved;
- crates.io does not thereby become the whole admit/quarantine/waive product;
- local review artifacts remain necessary.

## Current implication
Future assistants should keep Package Intake + Release Boundary Review as a leading `advance` lane and separate service truth from local review truth.

## Downstream assets most likely to care
- `design/package-intake-gateway-execution-blueprint-2026Q1.md`
- `packets/top-band-v0/package-intake.advance.current.md`
- `kernels/top-band-v0/package-intake-review-kit.v0.md`

## Reissue triggers
- material crates.io security-tab or trusted-publishing change;
- capability-analysis vehicle/scope change;
- major advisory-routing change affecting review-kit design.

## What did not change
- the broad ladder;
- package-intake still looks companion-first over imported service truth.
