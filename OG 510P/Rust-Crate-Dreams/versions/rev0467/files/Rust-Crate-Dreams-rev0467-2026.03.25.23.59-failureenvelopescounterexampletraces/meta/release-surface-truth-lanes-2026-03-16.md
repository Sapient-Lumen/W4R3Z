# Release-surface truth lanes — 2026-03-16

This note exists to stop future passes from collapsing three related but distinct crate ideas into one fake “public API tooling” result.

The archive now has at least three neighboring lanes that need to stay separate:

1. **P-0244 SemVer API Diff Evidence Kit**
2. **P-0431 Public Dependency Boundary Kit**
3. **P-0483 Public API Readiness Bundle Kit**

They are adjacent, but they are not interchangeable.

## Core distinction

### P-0244 — SemVer evidence / witness substrate
This lane is about:
- old/new public-API snapshots,
- item matching,
- witness plans and witness results,
- semver judgments with confidence,
- and publish-facing breakage evidence.

It should answer:
- “Is this public API change backward compatible?”
- “What evidence decided that?”

It is **not** the place to become the general release dashboard.

### P-0431 — public dependency boundary truth
This lane is about:
- which dependencies are actually public,
- why they are public/private/ambiguous,
- reexport and type-reference reasons,
- manifest migration plans,
- and workspace/stabilization limitations.

It should answer:
- “Why is this dependency part of my public contract?”
- “How do I move from accidental to explicit boundary intent?”

It is **not** the place to decide the whole release or run all semver policy.

### P-0483 — joined release-review bundle
This lane is about:
- combining imported semver verdicts,
- public dependency facts,
- docs debt,
- waivers,
- and one release-review artifact.

It should answer:
- “Is this release ready for our public API contract?”

It should mostly **import** the sharper artifacts produced by the other lanes.

## Why this separation matters now

Current official Rust direction sharpens all three lanes at once:

- Cargo wants semver checking on the publish path.
- Witness-generation work makes P-0244 less hypothetical.
- Public/private dependency stabilization work makes P-0431 more urgent.
- The 2026 flagships frame both breaking-change detection and public API dependency control as supply-chain-adjacent priorities.

That makes it tempting to mush them together.
That would be a mistake.

## Working rule

When a future pass touches release-surface tooling, ask first:

1. Is the new value mainly about **breakage evidence**?
   - then it belongs primarily in **P-0244**.
2. Is the new value mainly about **which dependencies are public and why**?
   - then it belongs primarily in **P-0431**.
3. Is the new value mainly about **joining multiple signals for release signoff**?
   - then it belongs primarily in **P-0483**.

If a change seems to span all three, prefer strengthening:
- the foundational evidence/boundary crates first,
- and let the release bundle import them later.

## Anti-patterns to avoid

- Do **not** let P-0244 silently become the public dependency migration crate.
- Do **not** let P-0431 silently become the semver witness engine.
- Do **not** let P-0483 reimplement every lower-level analyzer instead of importing them.
- Do **not** flatten unstable/nightly precision work into fake stable certainty.

## Current frontier judgment

The stronger near-term move is still **foundation before aggregation**:
- witness/evidence contracts,
- boundary reason taxonomies,
- compact fixture packs,
- and explicit import boundaries.

That gives the repo something other people could actually build on.
