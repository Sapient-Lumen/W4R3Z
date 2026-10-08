# Epic proposal: Dependency Review Stack (`cargo dep-review`, `dependency-review-pack/v0`)

## One-line thesis
Build a thin stack-level Rust companion layer for **dependency intake and upgrade review** that links **trust-decision evidence**, **effect-audit evidence**, **runtime-capability evidence**, and **artifact/binary linkage** into one portable review boundary without collapsing them into one score or verdict.

## Why this is now worth doing
Rust has real pieces of the dependency-review puzzle, but they still live in different planes:
- crates.io and RustSec can tell you about advisories and publisher posture;
- Cargo Vet can tell you about imported audits, criteria, and smallest useful diffs;
- Cargo Scan can focus human attention on dangerous effects and caller-checked contexts;
- capability analysis can estimate the powers code would need if it runs;
- `cargo-auditable` and Cargo-native inventory work can tie review to shipped artifacts.

What is still missing is the **stack-level boundary that says one dependency subject was reviewed with these imported truths, these caveats, these local decisions, and this bounded handoff to consumers**.

## Working name
- CLI: `cargo dep-review`
- primary artifact: `dependency-review-pack/v0`

## Scope
### This epic should own
- dependency-review subject identity
- imported trust/effect/capability/inventory attachments
- diffable review points across versions / lockfiles / releases
- bounded PR / security / release / policy / assistant handoffs
- verification of pack integrity and import references

### This epic should not own
- advisory database curation
- registry hosting or malware response
- replacing Cargo Vet or Cargo Scan
- universal sandbox generation
- universal SBOM / binary inventory formats
- a one-number dependency score

## Candidate artifact family
### `dependency-review-brief/v0`
Why the review exists, intended consumer set, freshness budget, and review status.

### `dependency-review-subject/v0`
The exact crate/version/lockfile/release/binary slice under review, including subject kind, source, and comparison base.

### `dependency-review-pack/v0`
The portable review bundle linking:
- trust-decision attachments
- effect-review attachments
- optional capability-analysis attachments
- optional binary / inventory attachments
- local notes, waivers, and caveats
- integrity metadata

### `dependency-review-diff/v0`
What changed between two review points, with separate sections for trust, effects, capabilities, artifact linkage, and final bounded conclusions.

### `dependency-review-handoff/v0`
Bounded consumer summaries for:
- PR review
- security review
- release review
- policy/governance review
- assistant/editor rendering

## Recommended rollout
1. lockfile / version-bump review lane
2. effect-attached review lane
3. capability-attached review lane
4. artifact / binary attachment lane
5. bounded consumer handoff lane

This should be driven by [`design/dependency-review-pilot-program.md`](../design/dependency-review-pilot-program.md).

## What makes this epic “epic” rather than incremental
A merely incremental tool would improve one lane:
- nicer advisory summaries,
- better Cargo Vet UI,
- nicer effect-analysis output,
- better capability diffs,
- or better binary inventory export.

An epic contribution here instead gives Rust one **portable dependency review contract** above those lanes.
That is strategically different because it can:
- make PR/release/security reviews share the same subject and evidence boundary;
- let experimental lanes participate honestly without claiming universal coverage;
- make artifact linkage and shipped-binary review part of dependency intake instead of a separate afterthought;
- and provide a bounded surface that registry/search/assistant consumers can import without re-scraping the world.

## Design principles
- **No fake single score.**
- **Imported evidence stays imported.**
- **Partial coverage is explicit, not embarrassing.**
- **Review points are diffable.**
- **Consumer summaries are lossy on purpose and say so.**
- **The stack remains thin.**

## Success conditions
This epic is succeeding when Rust teams can say:
- “we reviewed this dependency change,”
- “here is the exact subject,”
- “here are the trust, dangerous-code, authority, and artifact facts we imported,”
- “here are the local waivers or unknowns,”
- “here is what changed from the prior review,”
- and “here is what this PR/release/policy consumer may safely conclude,”

without inventing a bespoke review format for every repository.

## Read this with
- `gaps/dependency-review-effect-capability-and-intake-truth.md`
- `design/dependency-review-stack.md`
- `design/dependency-review-pilot-program.md`
- `design/trust-decision-stack.md`
- `design/runtime-capability-kit.md`
- `design/sbom-evidence-kit.md`
