# Current dossier: Package Intake + Release Boundary Review

## Identity
- candidate: **Package Intake + Release Boundary Review**
- macro-program: **Package Intake + Release Boundary Review**
- current archive posture: `advance`

## Why this candidate is still load-bearing
- crates.io now offers Trusted Publishing only mode and blocks risky GitHub triggers in trusted publishing.
  https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- The same update notes provider-specific caveats, such as current GitLab.com support and not self-hosted GitLab yet.
  https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- The March 2026 Cargo advisory says crates.io mitigated the public-registry case and audited historical crates, but alternate registries must verify their own exposure.
  https://blog.rust-lang.org/2026/03/21/cve-2026-33056/
- The 2026 flagships still keep adjacent supply-chain work such as SBOM and public/private dependencies in the strategic core.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html

## Current working judgment
This is still one of the clearest operator-shaped `advance` seams.
The right build remains local-first boundary review, not a universal trust oracle.

## Next concrete move
Write or refresh one **live packet** for a boundary-review kit that includes:
- intake brief;
- quarantine / waiver / escalation receipts;
- route-specific checks;
- alternate-registry caveat handling;
- and a replay drill corpus for recent classes of incidents.

## Earned proof
- service behavior is concrete and current;
- incident posture is current;
- the kernel stays valuable even without ecosystem-wide policy power.

## Missing proof
- stronger multi-registry normalization;
- proof that local-first route review works across a broader set of release workflows.

## Owner shape / upkeep reality
- first owner shape: operator-owned security-adjacent team
- upkeep tax: incident replay, route-policy drift, registry-specific caveats, waiver review

## Refused larger forms
- universal trust score
- central policy engine covering every registry
- removing local operator judgment from the loop

## Reissue triggers
- crates.io or Cargo materially changes publish/extract/security behavior
- alternate registries become more standardized
- the build starts making claims beyond local-first route review

## Source candor
- crates.io development update: concrete service-behavior evidence
- Cargo advisory: incident evidence with explicit alternate-registry caveat
- flagships: directional support, not proof of current operator workflow
