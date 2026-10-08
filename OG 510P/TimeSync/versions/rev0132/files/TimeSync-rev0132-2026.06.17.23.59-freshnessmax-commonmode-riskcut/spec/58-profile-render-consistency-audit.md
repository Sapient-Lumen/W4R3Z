# 58 — Profile render consistency audit

rev0087 adds a documentation-integrity audit for profile renderings.

## Finding

The rev0086 machine-readable profile catalog correctly listed `portable_digest_binding_policy_summary` as non-satisfying evidence, but the rendered `profiles/P*.md` files omitted that class from their `classes_that_cannot_satisfy_profile_obligations` lines. The normative JSON was correct; the human render drifted.

## Change

The validator now checks that each rendered profile Markdown file includes every evidence class that its catalog entry forbids from satisfying profile obligations. This catches silent divergence between review-facing documents and normative JSON.

## Boundary

This audit does not make Markdown normative. The catalog remains authoritative. The audit prevents stale rendered summaries from misleading a human reviewer.
