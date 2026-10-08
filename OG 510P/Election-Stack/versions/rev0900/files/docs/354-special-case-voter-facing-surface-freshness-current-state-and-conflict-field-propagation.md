# 354. Special-case voter-facing surface freshness/current-state/conflict field propagation

**Track:** Shared / Public surfaces

## Why this exists (bounded)

The archive already has compact numbered controls for the highest-risk voter-facing special-case rows tagged `special_case_high_risk` in `artifacts/tables/voter-facing-public-answer-surfaces.csv` (currently `317–328` and `335–343`) requiring:

- a bounded release-date freshness floor and source-review window (`docs/344-*`),
- explicit authority hierarchy and official-routing precedence (`docs/345-*`),
- explicit current-state visibility and superseding-notice discipline (`docs/346-*`), and
- an unresolved-conflict stop and no-synthesis rule (`docs/347-*`).

The archive also now has a separate triplet-propagation firewall (`docs/353-*`) for the newer high-risk help-route / office-identity / secure-channel / operability fields.

That still leaves a narrow but real drift seam: a numbered doc can say the right thing about freshness, current official control, superseding notices, and unresolved conflict while the linked template or checklist stays too thin for the operator workflow that actually carries the public artifact.

## What this adds (and what it does not)

This document adds a compact **field-propagation floor** for the `docs/344-*` through `docs/347-*` control cluster.

It does **not** replace:

- the underlying release-freshness check itself in `docs/344-*`,
- the prose-level authority-hierarchy rule in `docs/345-*`,
- the prose-level superseding-notice rule in `docs/346-*`,
- the prose-level unresolved-conflict stop rule in `docs/347-*`,
- the later help-route / office-identity / secure-channel / operability propagation rule in `docs/353-*`,
- the payload verification-timestamp discipline in `docs/356-*`, or
- any requirement to keep direct jurisdiction-specific official anchors under `docs/348-*`.

It only says that a small set of already-required high-risk control notes must also appear in the linked template/checklist pair so they are harder to silently drop during future maintenance.

## Propagation floor

For each row tagged `special_case_high_risk`, the linked template and checklist should preserve, in substance, all of the following bounded control fields:

- `last_verified_at`,
- `source_review_window_days`,
- `latest_notice_uri`,
- `current_official_controls_note`,
- `superseding_notice_note`, and
- `unresolved_conflict_stop_note`.

The point is not to turn every public artifact into a long policy packet.
The point is to keep the minimum viable high-risk public artifact shape honest about **when it was last reviewed, how fresh the review window is, which current official instruction controls, how to spot a superseding notice, and when unresolved conflict means stop rather than synthesize**.

## What this is meant to catch

This propagation floor is meant to catch bounded failures such as:

- a numbered doc that says the current official source controls while the linked template still sounds like the archive summary is the final answer,
- a high-risk template that keeps `last_verified_at` but drops any explicit `source_review_window_days` field,
- a current-state / superseding-notice rule that exists only in prose while the operator checklist no longer reminds maintainers to carry a `latest_notice_uri`,
- an unresolved-conflict stop rule that exists only in a numbered doc while the checklist still nudges maintainers toward best-effort synthesis under pressure, or
- a future cleanup that preserves the triplet formally but lets the older freshness/current-state/conflict backstop live only in the numbered essay.

## Mechanical check

The release gate should reject the archive if any current `special_case_high_risk` surface is missing the required template/checklist fields or the dedicated high-risk freshness/current-state/conflict checklist section.

That check is implemented by:

- `scripts/check_voter_facing_special_case_freshness_current_state_conflict_propagation.py`
- `scripts/release_gate.py`

## Why this stays narrow

This is still a **triplet hygiene** control, not a new doctrine layer.
It only touches three things for a bounded high-risk subfamily:

- the numbered doc,
- the payload template, and
- the operator checklist.

If a future simplification removes or reshapes these high-risk surfaces, this propagation rule can be removed with the same boundedness as the rest of the `330–356` family.

## Cross-references

- `docs/330-voter-facing-public-answer-surface-triplet-coherence-and-orphan-control.md`
- `docs/344-special-case-voter-facing-surface-release-freshness-floor-and-source-review-window.md`
- `docs/345-special-case-voter-facing-surface-authority-hierarchy-and-official-routing-precedence.md`
- `docs/346-special-case-voter-facing-surface-current-state-visibility-and-superseding-notice-discipline.md`
- `docs/347-special-case-voter-facing-surface-unresolved-conflict-stop-and-no-synthesis-rule.md`
- `docs/353-special-case-voter-facing-surface-triplet-propagation-and-doc-only-drift-firewall.md`
- `docs/356-special-case-voter-facing-surface-payload-verification-timestamp-discipline-and-review-window-coherence.md`
- `scripts/check_voter_facing_special_case_freshness_current_state_conflict_propagation.py`

For the canonical ordered current control-stack map that keeps newer tail controls discoverable from anywhere in this maintainer subfamily, see `docs/355-special-case-voter-facing-surface-control-stack-reference-closure-and-navigation-firewall.md`. For the companion checklist-workflow rule that keeps the earlier non-overlap / lane-change / no-portability controls visible in the linked high-risk checklist instead of only in the numbered doc, see `docs/357-special-case-voter-facing-surface-boundary-portability-checklist-backstop.md`.

## Sources (pinned IDs / lockfile IDs)

- EAC: Voter FAQs (xref: `eac_voter_faqs_page`)
- EAC: Register and Vote in Your State (xref: `eac_register_and_vote_in_your_state_page`)
- NASS: Can I Vote (xref: `nass_can_i_vote_page`)
- NASS: #TrustedInfo2026 (xref: `nass_trustedinfo_2026_page`)
- Vote.gov: Register to vote / update registration (xref: `vote_gov_register_page`)
