# Assurance-case boundaries — 2026-03-09

This note exists to stop future passes from collapsing too many layers into one fake “certification crate”.

## Main judgment

The sharp stack here is:

1. **evidence producers** (coverage, lint, unsafe-audit, verification-campaign, conformance, reproducibility, specs),
2. **bundle/profile substrate** (**P-0256**),
3. **assurance-case assembly and review** (**P-0503**),
4. optional **GSN / SACM / editor export lanes**,
5. and entirely separate **organization- or regulator-specific lifecycle workflows**.

A good assurance-case crate should live at layer 3.
It may export toward layer 4.
It should not pretend to own layer 5.

## What P-0503 should own

- claim graph assembly
- evidence import / provenance / freshness tracking
- conservative claim status evaluation
- assurance diffing and change-impact reporting
- review-pack generation
- optional standards-shaped exports

## What P-0503 should not own

- primary generation of verification or conformance evidence
- private replacement for bundle substrate
- full requirements / hazard / regulator workflow systems
- “push button certification” claims
- rich graphical editing as the first deliverable

## Review questions for future passes

Before expanding **P-0503**, ask:

1. is this a new evidence producer instead,
2. is this only a bundle/profile concern,
3. is this really an editor / visualization concern,
4. or is this a regulator- and company-specific lifecycle concern that the crate should merely point to?

If the answer is yes, keep it out of the core.

## Practical rule

A worthy P-0503 artifact is allowed to say:

- “the claim graph is structurally complete but top-level status is still `blocked`,"
- “this export is GSN-shaped but preserves stale/manual-review semantics from the internal model,"
- and “this assurance pack is review input, not certification proof.”

That honesty is part of the product.
