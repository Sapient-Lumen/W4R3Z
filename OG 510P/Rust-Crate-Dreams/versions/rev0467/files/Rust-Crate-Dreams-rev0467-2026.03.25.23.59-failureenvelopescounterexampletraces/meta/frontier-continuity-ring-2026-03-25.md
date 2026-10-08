# Frontier continuity ring — 2026-03-25

This note makes one missing layer explicit:

The front door is not enough.
A team that chooses a crate also needs a compact, reviewable way to keep that answer valid over time.

That sharper missing layer is the **continuity ring**.

## What belongs in the continuity ring

### Primary lanes

1. **P-0535 Dependency Lifecycle Transition Kit**
   - recheck triggers
   - decision revalidation
   - replacement/off-ramp packets
   - downgrade / successor / retirement explanations

2. **P-0496 Cargo Vendor & Source Parity Kit**
   - vendor / mirror / offline parity
   - alternate-source caveats
   - source replacement drift
   - restricted-delivery explainability

3. **P-0431 Public Dependency Boundary Kit**
   - public/private boundary changes
   - semver-relevant exposure drift
   - “what became part of our promise?” answers

4. **P-0125 Cargo SBOM Precursor Workbench Kit** *(supporting lane)*
   - carry-forward dependency inventory
   - release-to-release precursor deltas
   - exportable inputs to later SBOM / policy systems

## Why this ring got stronger now

Because the official ecosystem substrate increasingly exposes:
- trust and timing signals (`Security` tab, Trusted Publishing posture, SLOC, `pubtime`),
- machine-usable docs/build/type surfaces (docs.rs download, rustdoc JSON, metadata),
- and emerging Cargo/report infrastructure.

At the same time, recent ecosystem realities remind us that post-adoption continuity matters:
- malicious crate handling is increasingly advisory-first rather than blog-noise-first,
- the March 2026 Cargo advisory explicitly distinguishes crates.io from alternate-registry realities,
- and build-dir migration work shows how many tools still depend on internal details.

So a worthy crate contribution increasingly needs to help other teams survive **time**, **drift**, **mirroring**, and **boundary change**, not only initial selection.

## What this ring should provide other people

A continuity-ring crate family should let another team answer:

1. **Is our old answer still valid?**
2. **What exactly changed since the last accepted answer?**
3. **Is the new signal advisory, support, policy, target, source, or public-boundary drift?**
4. **Does our mirror/vendor/offline route still mean the same thing as the public route?**
5. **Did the crate’s public promise widen or narrow?**
6. **What is the least-destructive safe next move: keep, pin, exception, re-evaluate, migrate, or replace?**

## Minimum artifact family for a real `0.1`

A practical first slice should export at least:

- `trigger-intake.receipt.json`
- `decision-revalidation.report.json`
- `transition-plan.json`
- `source-parity.report.json`
- `mirror-readiness.report.json`
- `public-boundary.report.json`
- `sbom-precursor.delta.json`
- `continuity-summary.md`

Not every lane needs every artifact in `0.1`.
But the ring as a whole should cover this family.

## Suggested CLI / library shape

### CLI

- `cargo continuity intake`
- `cargo continuity revalidate`
- `cargo continuity parity`
- `cargo continuity boundary`
- `cargo continuity transition`
- `cargo continuity summary`

### Library

- `continuity::intake`
- `continuity::revalidate`
- `continuity::source_parity`
- `continuity::public_boundary`
- `continuity::transition`
- `continuity::render`

## Trust ceiling / refusal boundary

This ring should **not** claim:
- perfect malware detection,
- universal offline reproducibility,
- complete provenance attestation,
- universal semver judgment without imported evidence,
- or full enterprise policy approval.

It should instead claim:
- repeatable intake,
- preserved older basis,
- explicit drift categories,
- bounded parity checks,
- and reviewable transition recommendations.

## Practical build order inside the ring

1. **P-0535** — revalidation and off-ramp core
2. **P-0496** — source/mirror parity reports
3. **P-0431** — public-boundary drift imports
4. **P-0125** — SBOM precursor carry-forward once the first three can freeze their inputs

## One-sentence takeaway

A worthy ecosystem crate should increasingly help teams keep a decision honest over time, not only make the decision once.
