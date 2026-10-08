# 356. Special-case voter-facing surface payload verification-timestamp discipline and review-window coherence

**Track:** Shared / Public surfaces

## Why this exists (bounded)

The archive already has compact numbered controls for the highest-risk voter-facing special-case rows tagged `special_case_high_risk` in `artifacts/tables/voter-facing-public-answer-surfaces.csv` (currently `317–328` and `335–343`) requiring:

- repeated current official-public grounding and a bounded release-date freshness floor in `docs/344-*`,
- explicit authority hierarchy and official-routing precedence in `docs/345-*`,
- explicit current-state visibility and superseding-notice discipline in `docs/346-*`,
- an unresolved-conflict stop and no-synthesis rule in `docs/347-*`, and
- propagation of `last_verified_at` plus `source_review_window_days` into the linked payload/checklist triplet in `docs/354-*`.

That still leaves a narrow but real payload seam: a high-risk template can carry the right field names while the release gate never proves that the payload's own `last_verified_at` is parseable, not future-dated relative to the release, or actually inside the template's declared `source_review_window_days` window.

For this subfamily, that matters because current public voter-information posture remains strongly routing-based. EAC says the best source of practical registration and voting information is the local elections office; NASS's Can I Vote links directly to state election websites and trusted resources; and Vote.gov highlights official `.gov` sites, HTTPS, and sharing sensitive information only on official secure websites. A payload that claims recent verification should therefore be mechanically able to support that claim at release time rather than only sounding current in prose. (xref: `eac_voter_faqs_page`; xref: `nass_can_i_vote_page`; xref: `vote_gov_home_page`)

## What this adds (and what it does not)

This document adds a compact **payload verification-timestamp discipline** rule for the `special_case_high_risk` subfamily.

It does **not** replace:

- the official-source release-freshness floor in `docs/344-*`,
- the field-propagation rule in `docs/354-*`,
- the canonical control-stack map in `docs/355-*`, or
- any tighter human review cadence maintainers may need near an actual election deadline.

It only says that once a high-risk payload template claims a `last_verified_at` timestamp and a declared `source_review_window_days`, the release gate should prove that those two fields are internally coherent relative to the archive's own release date.

## Payload coherence floor

For each row tagged `special_case_high_risk`, the linked payload template should satisfy all of the following:

1. `last_verified_at` is present and parseable as an ISO-style timestamp,
2. `last_verified_at` is not after the release date recorded at the head of `CHANGELOG.md`, and
3. the number of days between `last_verified_at` and that release date does not exceed the payload's declared `source_review_window_days`.

This is intentionally small.
It does not try to prove that every embedded summary sentence is correct.
It only prevents a payload from carrying a formally present but stale or impossible verification timestamp while still looking fresh enough to ship.

## What this is meant to catch

This rule is meant to catch bounded failures such as:

- a high-risk payload template whose `last_verified_at` drifted into an invalid or non-ISO format during an edit,
- a template that was copied forward with a future-dated verification timestamp,
- a template that still declares a review window but whose own verification timestamp is already older than that window at release time, or
- a release where the numbered docs and source lock look current while the payload's metadata silently stops being truthful about when the template was last reviewed.

## Mechanical check

The release gate should reject the archive if any current `special_case_high_risk` payload template has a malformed `last_verified_at`, a `last_verified_at` after the release date, or a `last_verified_at` older than the payload's declared `source_review_window_days`.

That check is implemented by:

- `scripts/check_voter_facing_special_case_payload_review_window.py`
- `scripts/release_gate.py`

## Why this stays narrow

This is a **payload-metadata honesty** control, not a new content doctrine.
It adds one numbered doc plus one checker and stays within the existing high-risk triplet discipline already established by `docs/353-*` and `docs/354-*`.

If the archive later removes or reshapes these high-risk surfaces, this rule can disappear with the same boundedness as the rest of the `330–356` maintainer-control family.

## Cross-references

- `docs/330-voter-facing-public-answer-surface-triplet-coherence-and-orphan-control.md`
- `docs/344-special-case-voter-facing-surface-release-freshness-floor-and-source-review-window.md`
- `docs/354-special-case-voter-facing-surface-freshness-current-state-and-conflict-field-propagation.md`
- `docs/355-special-case-voter-facing-surface-control-stack-reference-closure-and-navigation-firewall.md`
- `scripts/check_voter_facing_special_case_payload_review_window.py`

For the canonical ordered current control-stack map that keeps newer tail controls discoverable from anywhere in this maintainer subfamily, see `docs/355-special-case-voter-facing-surface-control-stack-reference-closure-and-navigation-firewall.md`. For the companion checklist-workflow rule that keeps the earlier non-overlap / lane-change / no-portability controls visible in the linked high-risk checklist instead of only in the numbered doc, see `docs/357-special-case-voter-facing-surface-boundary-portability-checklist-backstop.md`.

## Sources (pinned IDs / lockfile IDs)

- EAC: Voter FAQs (xref: `eac_voter_faqs_page`)
- EAC: Register and Vote in Your State (xref: `eac_register_and_vote_in_your_state_page`)
- NASS: Can I Vote (xref: `nass_can_i_vote_page`)
- NASS: #TrustedInfo2026 (xref: `nass_trustedinfo_2026_page`)
- Vote.gov: Home / official secure-site marker (xref: `vote_gov_home_page`)
