# Specimen: Package Intake + Release Boundary Review packet (`advance`)

Status: **illustrative specimen, not a live portfolio verdict**

## Identity
- candidate: **Package Intake + Release Boundary Review**
- macro-program: **Package Intake + Release Boundary Review**
- specimen role: `review-packet/v0`
- requested verdict: `advance`

## Why now
- crates.io now exposes a Security tab with RustSec advisories on crate pages.
  https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- crates.io added Trusted Publishing support for GitLab CI/CD, trusted-publishing-only mode, blocked risky GitHub triggers, and publication-time data in the index.
  https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- The malicious-crate notification policy now favors RustSec advisories for routine malware removals and reserves blog amplification for cases with real usage or exploitation.
  https://blog.rust-lang.org/2026/02/13/crates.io-malicious-crate-update/
- The March 2026 Cargo advisory shows that package extraction remains a real boundary: crates.io mitigated public-registry uploads and audited historical crates, but alternate registries must verify their own exposure.
  https://blog.rust-lang.org/2026/03/21/cve-2026-33056/
- The 2026 flagships keep public/private dependencies and SBOM support in the strategic core.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html

## Kernel and artifact family
- kernel: **local-first intake/release boundary review with replay, quarantine, waiver, and escalation receipts**
- first artifact family:
  - `package-intake-brief/v0`
  - `boundary-review-receipt/v0`
  - `quarantine-waiver-log/v0`

## Stage / proof status
- current stage: **kernel proof with strong route realism**
- earned proof:
  - concrete service behavior and incident response exist now;
  - the seam is boundary-shaped and operator-shaped rather than hypothetical.
- missing proof:
  - broader ecosystem policy should still stay secondary to local route value;
  - alternate-registry coverage remains heterogeneous.

## Practical decision improved
A package steward or release operator can answer:
- whether a dependency should pass, be quarantined, or need manual review;
- what route-specific evidence was examined;
- and what escalation receipt should accompany the decision.

## Proving grounds
- dependency intake for a real workspace
- publish/release boundary drills
- replay of recent malicious-package or extraction-boundary scenarios
- alternate-registry checklists where applicable

## Negative states
- crates.io improvements do not universalize to all registries;
- a boundary-review tool cannot promise full malware detection;
- broad ecosystem policy claims remain refused until local-first value is proven repeatedly.

## Owner shape / upkeep
- first owner shape: **operator-owned or security-adjacent team**
- upkeep reality: route-specific policy drift, replay fixtures, waiver review, incident updates, registry-specific caveats

## Adjacency / refused larger forms
- beats: generic supply-chain portal rhetoric with no operator workflow
- remains adjacent to: crates.io service work, RustSec, SBOM/public-private dependency evolution
- refuses:
  - one universal trust score
  - central policy engine pretending to cover every registry
  - decoupling the review packet from local operator judgment

## Bounded v0
A worthy v0 is:
- one local intake command or workflow,
- one review brief,
- one receipt family for quarantine/waiver/escalation,
- and one replay drill corpus.

## Expiry / reissue triggers
Reissue this packet if:
- crates.io or Cargo materially changes publish/extract/security behavior;
- alternate-registry support becomes more standardized;
- or the tool starts making claims beyond local-first route review.

## Source candor
- crates.io development update: **service-behavior evidence for public registry features**
- malicious-crate policy update: **communication-policy and notification-lane evidence**
- Cargo advisory: **incident/mitigation evidence, with explicit alternate-registry caveat**
- flagships: **directional support for adjacent supply-chain work, not proof of current service behavior**

## Packet judgment
Why `advance` instead of `deepen`:
- the boundary, operator, and artifact story are already concrete enough for a bounded local-first v0.
Why not `hold`:
- current service and incident signals make the seam too concrete to justify waiting for another abstract synthesis.
