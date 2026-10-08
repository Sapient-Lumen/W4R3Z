# 329. Voter-facing public-answer surface registry and duplicate firewall

**Track:** Shared

This document turns the voter-facing public-answer surfaces named in `artifacts/tables/voter-facing-public-answer-surfaces.csv` into a **maintainable registry contract** instead of a loose sequence of one-off additions.

It exists to do six things:

1. make `artifacts/tables/voter-facing-public-answer-surfaces.csv` the canonical compact registry for the family,
2. force future additions to prove they are **distinct** rather than adjacent restatements,
3. give the release gate a small mechanical firewall against missing template/checklist wiring,
4. keep the current family-tail surfaces visible in the core entrypoints where readers and maintainers first look, including top-level maintainer entrypoints like `README.md` and `ARCHIVE_INDEX.md`,
5. keep recent promoted family-tail docs tied to lockfile-backed official-public anchors instead of drifting into uncited prose, and
6. keep future growth in **registry rows + short docs + short checklists**, not drifting FAQ prose.

It composes with:
- `docs/227-refactor-and-growth-protocol.md`
- `docs/229-experiment-to-spec-promotion-protocol.md`
- `docs/310-voter-facing-public-answer-surfaces-family-map-and-promotion-rules.md`
- `artifacts/tables/voter-facing-public-answer-surfaces.csv`
- `scripts/check_voter_facing_public_answer_surfaces.py`
- `docs/330-voter-facing-public-answer-surface-triplet-coherence-and-orphan-control.md`
- `scripts/check_voter_facing_surface_range_references.py`
- `scripts/check_voter_facing_surface_entrypoint_coverage.py`
- `scripts/check_voter_facing_surface_anchor_lock_coverage.py`
- `scripts/check_voter_facing_surface_structure_minimums.py`
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

## Registry contract

The family registry is:

- `artifacts/tables/voter-facing-public-answer-surfaces.csv`

Each row records only the minimum fields needed to keep the family navigable and machine-checkable:

- `doc_id`
- `surface_slug`
- `family_bucket`
- `canonical_question`
- `action_window`
- `doc_path`
- `template_path`
- `checklist_path`
- optional `control_tags` for family-level firewalls that should follow the row (for example `special_case_high_risk`)

That is intentionally small.
The registry is **not** a fifty-state legal digest, a source catalog, or a place to duplicate the prose from the numbered voter-facing surface docs.
It is the family’s compact control plane.

## Duplicate-firewall questions

Before adding another voter-facing surface, maintainers SHOULD be able to answer **yes** to all of these:

1. **Different next action:** does the new question change what the voter must do next in a way no existing row already captures?
2. **Different action window:** is the timing state materially different (for example: before ballot request, after ballot issuance, live same-day routing, post-cast status, special-circumstances planning)?
3. **Different public artifact shape:** would official channels usually publish a distinct page/PDF/hotline script rather than a paragraph inside an existing surface?
4. **Different correction semantics:** if two official channels disagreed here, would the dispute be materially different from disputes already modeled by adjacent rows?
5. **Different checklist burden:** would an operator need a short but distinct checklist rather than a minor checklist extension on an existing surface?
6. **Net anti-bloat gain:** does this addition reduce confusion more than it expands the family?

If any answer is “no,” do one of these instead:

- tighten an overlap rule in `docs/310-*`,
- refine an existing template or checklist,
- add a note to the registry row’s surrounding doc,
- or log the candidate in `docs/207-research-agenda-and-revision-ledger.md` until the boundary is sharper.

## Required wiring for a new family surface

A new voter-facing family surface is not considered integrated unless the same revision includes all of the following:

- a numbered canonical doc,
- one registry row in `artifacts/tables/voter-facing-public-answer-surfaces.csv`,
- one payload template,
- one checklist,
- one update to `docs/310-*` explaining overlap or placement,
- and navigation updates where maintainers/readers would reasonably look first.

This keeps the archive from accumulating orphaned prose.

## Mechanical release-gate firewall

The release gate SHOULD reject voter-facing family drift when any of the following occur:

- duplicate `doc_id` or `surface_slug` rows,
- missing doc/template/checklist files,
- rows out of numeric order,
- malformed canonical questions,
- missing core-entrypoint mentions for promoted family-tail docs,
- unknown `family_bucket` values,
- or promoted family-tail docs that lost their lockfile-backed official anchors,
- or promoted family-tail docs and any newer `special_case_high_risk` rows below `323` that lost the standard bounded-surface sections keeping routing, freshness, and verification guidance explicit.

The checker for this is:

- `scripts/check_voter_facing_public_answer_surfaces.py`
- `docs/330-voter-facing-public-answer-surface-triplet-coherence-and-orphan-control.md`
- `scripts/check_voter_facing_surface_range_references.py`
- `scripts/check_voter_facing_surface_entrypoint_coverage.py`
- `scripts/check_voter_facing_surface_anchor_lock_coverage.py`
- `scripts/check_voter_facing_surface_structure_minimums.py`
- `docs/331-special-case-voter-facing-surfaces-subfamily-and-authority-anchor-minimums.md`

The goal is modest: catch wiring failures, obvious duplicate drift, stale hardcoded family-range references, newly promoted family-tail docs that never make it into the archive's canonical entrypoints (including top-level maintainer entrypoints like `README.md` and `ARCHIVE_INDEX.md`), and family-tail docs plus any newer `special_case_high_risk` rows below `323` that quietly lose the standard bounded-surface section shape, without turning the family registry into a heavyweight schema system.

For the next layer — making sure the family has no half-integrated docs/templates/checklists or orphan residue — see `docs/330-voter-facing-public-answer-surface-triplet-coherence-and-orphan-control.md`.
For the tighter rule that applies only to the newest high-risk special-case subfamily — the rows tagged `special_case_high_risk` in `artifacts/tables/voter-facing-public-answer-surfaces.csv` (currently `317–328` and `335–343`) — see `docs/331-special-case-voter-facing-surfaces-subfamily-and-authority-anchor-minimums.md`.
For the companion rule that those same docs must also say clearly which adjacent surfaces are still different, see `docs/332-special-case-voter-facing-surface-nonoverlap-declarations-and-misrouting-firewall.md`. For the further rule that they must also say when to switch to the `305` ordinary-help lane or the `307` rights/safety lane, see `docs/333-special-case-voter-facing-surface-safe-fallback-and-escalation-boundaries.md`. For the companion rule that they must also say these rules are time-sensitive, jurisdiction-specific, and unsafe to port across states/counties/facilities without current official verification, see `docs/334-special-case-voter-facing-surface-temporal-volatility-freshness-and-no-cross-jurisdiction-inference.md`. For the further companion rule that they must also say the current official state/local election-office source controls over national/archive summaries, see `docs/345-special-case-voter-facing-surface-authority-hierarchy-and-official-routing-precedence.md`. For the further companion rule that they must also tell the reader how to identify the current controlling official notice when older material remains visible, see `docs/346-special-case-voter-facing-surface-current-state-visibility-and-superseding-notice-discipline.md`. For the further companion rule that they must also stop on unresolved official conflict instead of synthesizing an answer from fragments, see `docs/347-special-case-voter-facing-surface-unresolved-conflict-stop-and-no-synthesis-rule.md`. For the further companion rule that they must also carry at least two direct jurisdiction-specific official-public governing examples rather than leaning only on national routing pages or generalized official explainers, see `docs/348-special-case-voter-facing-surface-direct-jurisdiction-anchor-floor-and-national-routing-nonsubstitution.md`. For the further companion rule that they must also expose a concrete official help/contact path rather than stopping at abstract “contact the office” prose, see `docs/349-special-case-voter-facing-surface-direct-help-route-and-contactability-floor.md`. For the further companion rule that they must also identify which official office role actually owns the case rather than exposing an undifferentiated help route, see `docs/350-special-case-voter-facing-surface-responsible-office-specificity-and-jurisdiction-match-floor.md`. For the further companion rule that they must also name an official secure channel for sensitive records and warn against oversharing on public or unverified paths, see `docs/351-special-case-voter-facing-surface-official-secure-channel-and-minimum-disclosure-floor.md`. For the further companion rule that they must also say how to verify that the named office/path is still open and operating right now under same-day or near-cutoff pressure, see `docs/352-special-case-voter-facing-surface-operability-now-and-deadline-imminence-floor.md`.

## Maintenance posture

When this family grows, prefer the following order of operations:

1. **tighten `docs/310` first,**
2. **extend an existing surface second,**
3. **add a registry/checklist refinement third,**
4. **add a new numbered surface last.**

That order is the archive’s anti-sprawl posture for voter-facing answer work.
