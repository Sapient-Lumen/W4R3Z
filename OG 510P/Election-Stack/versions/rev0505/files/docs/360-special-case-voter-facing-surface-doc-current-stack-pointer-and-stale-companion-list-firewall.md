# 360. Special-case voter-facing surface-doc current-stack pointer and stale-companion-list firewall

**Track:** Shared / Public surfaces

## Why this exists (bounded)

The archive now has a compact but meaningful `special_case_high_risk` control stack for the highest-risk voter-facing edge-case surfaces in `artifacts/tables/voter-facing-public-answer-surfaces.csv` (currently `317–328` and `335–343`).

Recent revisions already closed stale-tail drift in three maintainer layers:

- the canonical current-stack map itself in `docs/355-*`,
- bounded overview / family-map docs in `docs/358-*`, and
- bounded checker scope in `docs/359-*`.

A narrower but still real seam remained: maintainers often enter this cluster through the numbered **surface doc they are editing**, not through a family map or release-gate script. Many of those current high-risk surface docs still carried only an older partial companion-control list such as `331–345`, or no live current-stack pointer at all. A reader could therefore land on the correct surface, see a stale local control snapshot, and miss later propagation / payload / checklist / overview / checker-scope controls that the release gate already enforced.

For a control family built around current official routing, current-state visibility, unresolved-conflict stops, secure official channels, and deadline-near operability, that is the wrong maintenance posture. The surface doc itself should preserve one bounded route back to the canonical current control stack.

## What this adds (and what it does not)

This document adds one narrow rule: every current `special_case_high_risk` numbered surface doc should carry a compact pointer to the canonical current-stack map in `docs/355-*`.

It does **not** require every surface doc to inline the full current control tail. It does **not** replace:

- the authority-anchor minimum in `docs/331-*`,
- the non-overlap / fallback / temporal-volatility controls in `docs/332-*` through `docs/334-*`,
- the later release-freshness / current-state / conflict / routing / contactability / secure-channel / operability controls in `docs/344-*` through `docs/352-*`,
- the propagation and checklist/payload backstops in `docs/353-*`, `docs/354-*`, `docs/356-*`, and `docs/357-*`,
- the overview-doc inheritance rule in `docs/358-*`, or
- the checker-scope inheritance rule in `docs/359-*`.

It only closes the smaller seam where the actual numbered high-risk surface docs could remain local stale entrypoints even after the maintainer-control docs and overview docs were fixed.

## Bounded rule

For this bounded firewall:

- every current `special_case_high_risk` surface doc should include an explicit pointer to `docs/355-*`,
- that pointer should function as the surface-doc route back to the canonical current control perimeter, and
- maintainers should prefer that canonical map over any older partial companion list embedded in a surface doc's historical prose.

That means future additions to the current `344–361` control tail do not require twenty-one high-risk surface docs to be rewritten with a new inline tail list just to keep the current perimeter discoverable.
For the companion rule that bounded maintainer docs which still spell out the current tail by range label must keep that label synchronized with the live canonical stack instead of silently freezing an older perimeter, see `docs/361-special-case-voter-facing-surface-current-stack-range-label-inheritance-and-stale-perimeter-firewall.md`.

## What this is meant to catch

This rule is meant to catch small but real maintenance failures such as:

- a maintainer entering through `docs/317-*`, `docs/323-*`, or another high-risk surface doc and only seeing an older partial companion-control list,
- a later control such as `docs/356-*`, `docs/357-*`, `docs/358-*`, `docs/359-*`, or a future tail doc being enforced by the release gate but becoming practically invisible to editors who start from the surface doc,
- or a release where family maps are current but the actual high-risk numbered surface docs still act as stale local maps of the companion controls.

## Mechanical effect

The release gate should reject the archive if any current row tagged `special_case_high_risk` in `artifacts/tables/voter-facing-public-answer-surfaces.csv` loses its explicit pointer to `docs/355-*`.

That check is implemented by:

- `scripts/check_voter_facing_special_case_surface_doc_current_stack_pointer.py`
- `scripts/release_gate.py`

## Why this stays narrow

This is a surface-doc entrypoint firewall, not a new voter-facing doctrine layer. It adds one compact numbered doc, one checker, and one small pointer paragraph per current high-risk surface doc. It keeps those surface docs compact by routing maintainers back to one canonical current-stack map instead of forcing every surface doc to inline the entire later control tail.

## Cross-references

- `docs/331-special-case-voter-facing-surfaces-subfamily-and-authority-anchor-minimums.md`
- `docs/332-special-case-voter-facing-surface-nonoverlap-declarations-and-misrouting-firewall.md`
- `docs/333-special-case-voter-facing-surface-safe-fallback-and-escalation-boundaries.md`
- `docs/334-special-case-voter-facing-surface-temporal-volatility-freshness-and-no-cross-jurisdiction-inference.md`
- `docs/355-special-case-voter-facing-surface-control-stack-reference-closure-and-navigation-firewall.md`
- `docs/358-special-case-voter-facing-surface-overview-doc-current-stack-inheritance-and-stale-summary-firewall.md`
- `docs/359-special-case-voter-facing-surface-backticked-lockfile-citation-scope-inheritance-and-stale-target-firewall.md`
- `docs/361-special-case-voter-facing-surface-current-stack-range-label-inheritance-and-stale-perimeter-firewall.md`
- `scripts/check_voter_facing_special_case_surface_doc_current_stack_pointer.py`

## Sources (pinned IDs / lockfile IDs)

- EAC: Voter FAQs (xref: `eac_voter_faqs_page`)
- EAC: Register and Vote in Your State (xref: `eac_register_and_vote_in_your_state_page`)
- NASS: Can I Vote (xref: `nass_can_i_vote_page`)
- NASS: #TrustedInfo2026 (xref: `nass_trustedinfo_2026_page`)
- Vote.gov: Home / official secure-site marker (xref: `vote_gov_home_page`)
