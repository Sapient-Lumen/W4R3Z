# Public API readiness lane boundaries — 2026-03-19

Purpose: keep **P-0483 Public API Readiness Bundle Kit** focused on the missing joined release-review artifact instead of collapsing adjacent analysis lanes into one fake “API quality” crate.

## The four adjacent lanes

### 1. P-0244 — SemVer API Diff Evidence Kit
This lane answers:

- what changed semver-wise,
- which verdicts are backed by witnesses,
- and which breakage claims are still manual-review territory.

It is the **breakage-evidence substrate**.
It is not the whole release bundle.

### 2. P-0431 — Public Dependency Boundary Kit
This lane answers:

- which dependencies are public,
- why they are public/private/ambiguous,
- and what manifest or API cleanup would change that boundary.

It is the **boundary-classification substrate**.
It is not the full release verdict.

### 3. P-0483 — Public API Readiness Bundle Kit
This lane should answer:

- what public contract we are shipping,
- how it changed,
- which public dependencies now matter,
- what docs/example debt is relevant to that surface,
- what waivers are still carrying the release,
- and whether the release is ready, ready-with-waivers, not-ready, or manual-review-only.

It is the **joined release-review layer**.

### 4. P-0451 — CFG Availability Ledger Kit
This lane answers:

- which public items exist under which cfg/target conditions,
- what docs-only or platform-specific availability assumptions apply,
- and where item-level availability itself is ambiguous.

It is the **item-availability substrate**.
It may be imported by P-0483, but should remain separate.

## What P-0483 should own

P-0483 should own:

- bundle-level release review,
- waiver handling with expiry and owner,
- joined verdicts across semver / public-deps / docs readiness,
- explicit provenance for measured vs imported vs inferred facts,
- and release-to-release readiness diffs.

## What P-0483 should not own

P-0483 should **not** become:

- the semver-diff engine itself,
- the public/private dependency migration tool itself,
- the item-level cfg/availability matrix itself,
- or a general docs portal / changelog / quality dashboard.

## Sanity-check questions for future passes

Before deepening **P-0483**, ask:

1. Is the new value really about a **joined release decision**?
2. Or is it really about **breakage evidence** (P-0244)?
3. Or about **dependency boundary classification/migration** (P-0431)?
4. Or about **item-level conditional availability** (P-0451)?
5. Or about **generic docs tooling** that should stay elsewhere entirely?

If the answer is not “joined release decision,” the work probably belongs in another lane.
