# Current decision packet: Package Intake + Release Boundary Review (`advance`)

Status: **live current-decision packet**

## Identity
- candidate: **Package Intake + Release Boundary Review**
- macro-program: **Package Intake + Release Boundary Review**
- packet role: `live-decision-packet/v0`
- requested verdict now: `advance`

## Why now
- crates.io now has a Security tab backed by RustSec data.
  https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- crates.io has expanded trusted publishing to GitLab CI/CD and added trusted-publishing-only mode.
  https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- The March 2026 Cargo advisory says crates.io deployed a mitigation and audited all crates on the public registry, while alternate-registry users must verify their own exposure.
  https://blog.rust-lang.org/2026/03/21/cve-2026-33056/
- The challenges framing still says crate trust and crate selection remain real issues.
  https://blog.rust-lang.org/2026/03/20/rust-challenges/

## Practical decision improved
An operator or release steward can answer:
- whether a candidate package crosses a local intake boundary,
- what route-specific risk checks were run,
- whether quarantine, waiver, or escalation is needed,
- and how release-boundary review differs between crates.io and alternate registries.

## Bounded next move
Advance one local-first operator family:
- intake brief
- waiver receipt
- quarantine receipt
- route-specific escalation note
- release-boundary review checklist

The first proving grounds should be local drills and synthetic replays, not broad ecosystem policy.

## Earned proof
- public registry and alternate-registry differences are explicit;
- crates.io has current provenance and security signals worth importing;
- the contribution can start as a narrow operator-owned review boundary.

## Missing proof / blockers
- alternate-registry coverage remains heterogeneous;
- package-intake review still needs richer replay fixtures and operator drills;
- this does not yet justify a generalized ecosystem policy layer.

## Negative states and caveats
- public crates.io conditions do not generalize to every registry;
- security and provenance signals help but do not replace human review;
- operator waivers and route-specific exceptions remain irreducible.

## Owner shape / upkeep
- best first owner: operator or supply-chain review team
- upkeep tax: incident replay refresh, waiver discipline, registry-route caveat tracking

## Refused larger forms
- universal package trust score
- centralized policy platform
- pretending one registry's posture solves all package-intake reality

## Reissue triggers
- a new advisory materially changes the package-boundary story
- trusted-publishing support widens materially
- alternate-registry practice becomes better standardized

## Source candor
- crates.io update: concrete current features and platform posture
- Cargo advisory: route-real operator evidence
- challenges writeup: broad trust/selection framing only

## Decision rationale
`advance` is the honest verdict because there is enough real operator substrate to build a narrow local-first review boundary now, without pretending to solve ecosystem-wide trust in one move.
