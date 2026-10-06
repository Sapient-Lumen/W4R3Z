# RFC-0189: Release capsules and transparency

## Problem

DeriveBSD produces many verifiable artifacts around a release (closures, SBOMs, attestations, policy decisions).
Without a single canonical handle, ecosystems drift toward:

- “release = whatever the channel currently points at”
- missing context for incident response (which policies/evidence applied)
- brittle offline/airgap workflows

## Proposal

Introduce a small, content-addressed **release capsule** artifact:

- New artifact: `release.capsule` (`spec/release.capsule.schema.json`)
- The capsule binds the digests that define “this release”:
  - closure + optional closure manifest
  - trust policy / policy decision record digests
  - SBOM and attestation references
  - optional rollout policy digest
  - optional transparency entry digest

Add an optional release publication transparency artifact:

- New artifact: `release.transparency.entry` (`spec/release.transparency.entry.schema.json`)
- Use the common log proof shape: `spec/transparency.proof.schema.json`

## Why now

- The earlier we standardize the capsule, the less churn across channels, tools, and incident bundles.
- Capsules create a stable anchor for future adapters (full TUF, OCI, offline bundles) without weakening the core verification story.

## Risks / tradeoffs

- Too much in the capsule makes it heavyweight; keep it primarily as a list of digests.
- Transparency adds operational dependencies (log availability); must remain policy-optional.

See also: `docs/257-release-capsules-and-transparency.md`.
