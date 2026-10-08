# 330. Voter-facing public-answer surface triplet coherence and orphan control

**Track:** Shared

This document is a small companion to `docs/329-voter-facing-public-answer-surface-registry-and-duplicate-firewall.md`.

`329` answers **"is this proposed surface distinct enough to exist?"**

`330` answers **"if it exists, is it actually integrated as one bounded family unit rather than scattered prose and leftover files?"**

It exists to keep the voter-facing family from growing by accidental residue:

- a numbered doc with no registry row,
- a registry row with no maintained checklist,
- a payload template that no release path points at,
- or a half-finished addition that leaves future maintainers guessing which file is canonical.
- or a newly promoted family-tail surface that exists in the registry but is missing from the canonical entrypoints where readers first look, including top-level maintainer entrypoints like `README.md` and `ARCHIVE_INDEX.md`.

It composes with:
- `docs/227-refactor-and-growth-protocol.md`
- `docs/229-experiment-to-spec-promotion-protocol.md`
- `docs/310-voter-facing-public-answer-surfaces-family-map-and-promotion-rules.md`
- `docs/329-voter-facing-public-answer-surface-registry-and-duplicate-firewall.md`
- `docs/331-special-case-voter-facing-surfaces-subfamily-and-authority-anchor-minimums.md`
- `docs/332-special-case-voter-facing-surface-nonoverlap-declarations-and-misrouting-firewall.md`
- `docs/333-special-case-voter-facing-surface-safe-fallback-and-escalation-boundaries.md`
- `docs/334-special-case-voter-facing-surface-temporal-volatility-freshness-and-no-cross-jurisdiction-inference.md`
- `docs/345-special-case-voter-facing-surface-authority-hierarchy-and-official-routing-precedence.md`
- `docs/346-special-case-voter-facing-surface-current-state-visibility-and-superseding-notice-discipline.md`
- `docs/347-special-case-voter-facing-surface-unresolved-conflict-stop-and-no-synthesis-rule.md`
- `docs/348-special-case-voter-facing-surface-direct-jurisdiction-anchor-floor-and-national-routing-nonsubstitution.md`
- `docs/349-special-case-voter-facing-surface-direct-help-route-and-contactability-floor.md`
- `docs/350-special-case-voter-facing-surface-responsible-office-specificity-and-jurisdiction-match-floor.md`
- `docs/351-special-case-voter-facing-surface-official-secure-channel-and-minimum-disclosure-floor.md`
- `docs/352-special-case-voter-facing-surface-operability-now-and-deadline-imminence-floor.md`
- `docs/353-special-case-voter-facing-surface-triplet-propagation-and-doc-only-drift-firewall.md`
- `docs/354-special-case-voter-facing-surface-freshness-current-state-and-conflict-field-propagation.md`
- `docs/355-special-case-voter-facing-surface-control-stack-reference-closure-and-navigation-firewall.md`
- `docs/356-special-case-voter-facing-surface-payload-verification-timestamp-discipline-and-review-window-coherence.md`
- `docs/357-special-case-voter-facing-surface-boundary-portability-checklist-backstop.md`
- `docs/358-special-case-voter-facing-surface-overview-doc-current-stack-inheritance-and-stale-summary-firewall.md`
- `docs/359-special-case-voter-facing-surface-backticked-lockfile-citation-scope-inheritance-and-stale-target-firewall.md`
- `docs/360-special-case-voter-facing-surface-doc-current-stack-pointer-and-stale-companion-list-firewall.md`
- `artifacts/tables/voter-facing-public-answer-surfaces.csv`
- `scripts/check_voter_facing_surface_triplets.py`
- `scripts/check_voter_facing_surface_range_references.py`
- `scripts/check_voter_facing_surface_entrypoint_coverage.py`
- `scripts/check_voter_facing_surface_anchor_lock_coverage.py`
- `scripts/check_voter_facing_surface_structure_minimums.py`
- `scripts/check_voter_facing_special_case_triplet_propagation.py`
- `scripts/check_voter_facing_special_case_freshness_current_state_conflict_propagation.py`
- `scripts/check_voter_facing_special_case_payload_review_window.py`

## The triplet rule

Every voter-facing public-answer surface in the numbered family should exist as a **triplet**:

1. one numbered canonical doc,
2. one payload template,
3. one operator checklist,

and that triplet should be wired through exactly one registry row.

For this family, a numbered doc without its template/checklist pair is usually a sign that the archive has drifted back toward essay accretion.
A template/checklist pair without a registry row is usually a sign that a partial experiment was never actually promoted.
A registry row without all three files is usually just broken release wiring.

## What counts as the family boundary

For orphan-control purposes, the bounded voter-facing family is:

- the numbered docs named by `artifacts/tables/voter-facing-public-answer-surfaces.csv`,
- the canonical family registry at `artifacts/tables/voter-facing-public-answer-surfaces.csv`,
- and the template/checklist files named by that registry.

`310` and `329–334` are maintainer-control docs for the family, not family rows.

## Mechanical checks the release gate should enforce

The release gate should reject this family when any of the following occur:

- a numbered surface doc in `292–328` plus `335–343` exists with no registry row,
- a registry row points to a numbered doc outside the bounded family,
- two rows reuse the same template or checklist path,
- a checklist that looks like a voter-facing surface checklist exists but is not registered,
- a payload that looks like a voter-facing surface payload exists but is not registered,
- or the family’s canonical doc IDs have gaps caused by half-finished promotion work,
- or a `special_case_high_risk` triplet keeps the numbered doc but silently drops the latest high-risk help-route / office-identity / secure-channel / operability fields from the linked template or checklist,
- or a `special_case_high_risk` payload keeps the required freshness fields but silently lets `last_verified_at` become malformed, future-dated, or older than its declared review window.

The checker for this is:

- `scripts/check_voter_facing_surface_triplets.py`
- `scripts/check_voter_facing_surface_range_references.py`
- `scripts/check_voter_facing_surface_entrypoint_coverage.py`
- `scripts/check_voter_facing_surface_anchor_lock_coverage.py`
- `scripts/check_voter_facing_surface_structure_minimums.py`
- `scripts/check_voter_facing_special_case_triplet_propagation.py`
- `scripts/check_voter_facing_special_case_freshness_current_state_conflict_propagation.py`
- `scripts/check_voter_facing_special_case_payload_review_window.py`

The point is not perfect filename theology.
The point is to keep future additions **small, explicit, and removable** when needed, while also catching stale hardcoded family-range references in maintainer docs (including top-level maintainer entrypoints like `README.md` and `ARCHIVE_INDEX.md`) and missing core-entrypoint wiring for promoted family-tail docs and family-tail docs plus any newer `special_case_high_risk` rows below `323` that silently lose the standard bounded-surface section shape before they drift out of sync with the registry.

## Maintainer posture

When adding or revising a voter-facing surface, maintainers should prefer this order:

1. decide distinctness in `310` and `329`,
2. wire the registry row,
3. add or tighten the template/checklist pair,
4. only then finalize the numbered doc and release notes.

That keeps the family shaped like a bounded product surface catalog rather than a pile of adjacent essays.
For the additional rule that the newest high-risk special-case surfaces must retain multiple official-public anchors, see `docs/331-special-case-voter-facing-surfaces-subfamily-and-authority-anchor-minimums.md`.
For the companion rule that those same docs must also carry explicit adjacent-surface non-overlap declarations, see `docs/332-special-case-voter-facing-surface-nonoverlap-declarations-and-misrouting-firewall.md`. For the further rule that they must also say when to move from the niche edge-case page to `305` ordinary help or `307` rights/safety escalation, see `docs/333-special-case-voter-facing-surface-safe-fallback-and-escalation-boundaries.md`. For the companion rule that they must also carry a compact freshness / time-sensitivity / no-cross-jurisdiction warning, see `docs/334-special-case-voter-facing-surface-temporal-volatility-freshness-and-no-cross-jurisdiction-inference.md`. For the companion rule that they must also make the authority hierarchy explicit, see `docs/345-special-case-voter-facing-surface-authority-hierarchy-and-official-routing-precedence.md`. For the further companion rule that they must also tell the reader how to identify the current controlling official notice when older material remains visible, see `docs/346-special-case-voter-facing-surface-current-state-visibility-and-superseding-notice-discipline.md`. For the further companion rule that they must also stop on unresolved official conflict instead of synthesizing an answer from fragments, see `docs/347-special-case-voter-facing-surface-unresolved-conflict-stop-and-no-synthesis-rule.md`. For the further companion rule that they must also carry at least two direct jurisdiction-specific official-public governing examples rather than leaning only on national routing pages or generalized official explainers, see `docs/348-special-case-voter-facing-surface-direct-jurisdiction-anchor-floor-and-national-routing-nonsubstitution.md`. For the further companion rule that they must also expose a concrete official help/contact path rather than stopping at abstract “contact the office” prose, see `docs/349-special-case-voter-facing-surface-direct-help-route-and-contactability-floor.md`. For the further companion rule that they must also identify which official office role actually owns the case rather than exposing an undifferentiated help route, see `docs/350-special-case-voter-facing-surface-responsible-office-specificity-and-jurisdiction-match-floor.md`. For the further companion rule that they must also name an official secure channel for sensitive records and warn against oversharing on public or unverified paths, see `docs/351-special-case-voter-facing-surface-official-secure-channel-and-minimum-disclosure-floor.md`. For the further companion rule that they must also say how to verify that the named office/path is still open and operating right now under same-day or near-cutoff pressure, see `docs/352-special-case-voter-facing-surface-operability-now-and-deadline-imminence-floor.md`. For the further propagation rule that those latest high-risk controls must also appear in the linked template and checklist rather than living only in the numbered doc, see `docs/353-special-case-voter-facing-surface-triplet-propagation-and-doc-only-drift-firewall.md`. For the further payload-metadata rule that the linked high-risk template's own `last_verified_at` must stay parseable, nonfuture, and still inside its declared `source_review_window_days` window at release time, see `docs/356-special-case-voter-facing-surface-payload-verification-timestamp-discipline-and-review-window-coherence.md`. For the further checklist-workflow rule that the linked high-risk checklist must also keep adjacent-surface non-overlap refs, `305`/`307` lane-change reminders, and no-cross-jurisdiction portability warnings visible instead of leaving those earlier controls only in the numbered doc, see `docs/357-special-case-voter-facing-surface-boundary-portability-checklist-backstop.md`. For the further overview-doc rule that family maps and reading-path docs must inherit the current tail from one canonical stack map instead of freezing stale inline summaries, see `docs/358-special-case-voter-facing-surface-overview-doc-current-stack-inheritance-and-stale-summary-firewall.md`. For the further release-gate scope rule that the bounded recent backticked-lockfile-citation checker must inherit its control-doc target set from that same canonical stack map instead of freezing a stale manual tail list, see `docs/359-special-case-voter-facing-surface-backticked-lockfile-citation-scope-inheritance-and-stale-target-firewall.md`. For the further surface-doc entrypoint rule that every current `special_case_high_risk` numbered surface must also keep one compact pointer back to that same canonical stack map instead of leaving editors with a stale local companion-control list, see `docs/360-special-case-voter-facing-surface-doc-current-stack-pointer-and-stale-companion-list-firewall.md`.
For the canonical ordered current control-stack map that keeps newer tail controls discoverable from anywhere in this maintainer subfamily, see `docs/355-special-case-voter-facing-surface-control-stack-reference-closure-and-navigation-firewall.md`.
