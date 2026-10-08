# 358. Special-case voter-facing surface overview-doc current-stack inheritance and stale-summary firewall

**Track:** Shared / Public surfaces

## Why this exists (bounded)

The archive now has one canonical ordered current-stack map for the highest-risk voter-facing special-case controls in `docs/355-*`.

That still leaves a narrow maintainer-entrypoint seam.
Overview docs such as reading paths, family maps, and subfamily maps can quietly keep their own inline tail summary of the `special_case_high_risk` control stack.
When those overview docs are not updated at the same time as the canonical map, they become **stale local summaries**: the release gate may be current, the canonical stack map may be current, but a maintainer can still land on an older overview doc and miss the newest tail controls.

For this subfamily, that matters because current official voter-information posture remains routing-based rather than one-big-summary based. EAC says the best source of practical registration and voting information is the local elections office; NASS's Can I Vote links directly to state election websites and trusted resources; NASS's `#TrustedInfo2026` campaign promotes state and local election officials as the trusted sources of election information; and Vote.gov highlights official `.gov` sites, HTTPS, and sharing sensitive information only on official secure websites. The archive's own maintainer overviews should therefore inherit their current high-risk tail from one live canonical map instead of freezing last revision's stack in three different places. (xref: `eac_voter_faqs_page`; xref: `nass_can_i_vote_page`; xref: `nass_trustedinfo_2026_page`; xref: `vote_gov_home_page`)

## What this adds (and what it does not)

This document adds a compact **overview-doc current-stack inheritance** rule for the `special_case_high_risk` maintainer overviews.

It does **not** replace:

- the canonical stack-reference page in `docs/355-*`,
- the family map in `docs/310-*`,
- the audience reading paths in `docs/242-*`,
- the subfamily authority-anchor minimums in `docs/331-*`, or
- any numbered high-risk control from `docs/344-*` through `docs/357-*`.

It only says that overview docs which summarize or route into this high-risk control family should inherit the current tail from `docs/355-*` instead of freezing their own partial `344–…` snapshots.

## Inheritance rule

For this bounded firewall, overview docs that act as entrypoints into the `special_case_high_risk` control family should do one of two things:

1. **defer directly** to the canonical current-stack map in `docs/355-*`, or
2. **carry the full current tail** in a way that stays synchronized with `docs/355-*`.

In practice, the bounded archive default should be the first option.
That means docs like `docs/242-*`, `docs/310-*`, and the entrypoint section of `docs/331-*` should point to `docs/355-*` for the live `344–361` perimeter instead of repeating a local tail list that can silently stop at an older revision boundary.

## What this is meant to catch

This rule is meant to catch bounded failures such as:

- `docs/242-*` still acting like the high-risk tail ends at `352`,
- `docs/310-*` still summarizing the current companion stack as if newer propagation, payload-timestamp, checklist-backstop, or overview-inheritance controls do not exist,
- `docs/331-*` keeping a stale top-of-file artifact list even while the body references some newer controls,
- or a future release where the canonical map is current but a maintainer who lands on an older overview doc still gets an incomplete picture of the current control perimeter.

## Mechanical check

The release gate should reject the archive if the bounded overview docs for this subfamily lose the canonical pointer to `docs/355-*`, or if they keep stale inline `344–361` tail summaries where the canonical map should be inherited instead.

That check is implemented by:

- `docs/361-special-case-voter-facing-surface-current-stack-range-label-inheritance-and-stale-perimeter-firewall.md`
- `scripts/check_voter_facing_special_case_overview_stack_inheritance.py`
- `scripts/release_gate.py`

## Why this stays narrow

This is an **overview-doc inheritance** firewall, not a new doctrinal burden.
It adds one numbered doc plus one checker and keeps the fix bounded to the maintainer entrypoints that were actually drifting.

## Cross-references

- `docs/242-audience-reading-paths-and-what-to-ignore.md`
- `docs/310-voter-facing-public-answer-surfaces-family-map-and-promotion-rules.md`
- `docs/331-special-case-voter-facing-surfaces-subfamily-and-authority-anchor-minimums.md`
- `docs/355-special-case-voter-facing-surface-control-stack-reference-closure-and-navigation-firewall.md`
- `docs/361-special-case-voter-facing-surface-current-stack-range-label-inheritance-and-stale-perimeter-firewall.md`
- `scripts/check_voter_facing_special_case_overview_stack_inheritance.py`

## Sources (pinned IDs / lockfile IDs)

- EAC: Voter FAQs (xref: `eac_voter_faqs_page`)
- EAC: Register and Vote in Your State (xref: `eac_register_and_vote_in_your_state_page`)
- NASS: Can I Vote (xref: `nass_can_i_vote_page`)
- NASS: #TrustedInfo2026 (xref: `nass_trustedinfo_2026_page`)
- Vote.gov: Home / official secure-site marker (xref: `vote_gov_home_page`)
