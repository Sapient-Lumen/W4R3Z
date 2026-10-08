# 350. Special-case voter-facing surface responsible office specificity and jurisdiction-match floor

**Track:** Shared

This document is a compact companion to `docs/331-*`, `docs/332-*`, `docs/333-*`, `docs/334-*`, `docs/344-*`, `docs/345-*`, `docs/346-*`, `docs/347-*`, `docs/348-*`, and `docs/349-*` for the highest-risk voter-facing special-case cluster: the `special_case_high_risk` rows in `artifacts/tables/voter-facing-public-answer-surfaces.csv` (currently `317–328` and `335–343`).

It exists to answer one bounded maintainer question:

**“Even when a high-risk voter-facing edge-case surface exposes a help page or phone number, does it also say which official office actually owns the decision for the voter’s case?”**

## Why this exists (bounded)

The archive already does ten important things for the `special_case_high_risk` subfamily:

1. requires repeated official-public grounding (`docs/331-*`),
2. requires explicit adjacent-surface non-overlap (`docs/332-*`),
3. requires safe fallback / escalation boundaries (`docs/333-*`),
4. requires an explicit statement that the rule is jurisdiction-specific, time-sensitive, and unsafe to port without current verification (`docs/334-*`),
5. requires a bounded recent review of official-public examples before release (`docs/344-*`),
6. requires an explicit statement that the current official state/local election-office source controls over national/archive summaries (`docs/345-*`),
7. requires an explicit statement telling the reader how to identify the current controlling official notice or instruction when older material remains visible (`docs/346-*`),
8. requires an explicit unresolved-conflict stop / no-synthesis / office-confirmation rule (`docs/347-*`),
9. requires at least two direct jurisdiction-specific official-public governing examples rather than only national routing pages or generalized official explainers (`docs/348-*`), and
10. requires a concrete official help/contact path instead of abstract advice to “contact the office” (`docs/349-*`).

That still leaves one quiet routing failure mode.

A doc can satisfy all ten and still mislead the reader if it exposes a help URI or phone number without saying which official office role actually owns the issue. That matters because election administration is decentralized in more than one dimension: states differ, local structures differ inside states, and the controlling office for a given question may be a county board, registrar, parish clerk, city/township clerk, tribal election office, state elections division, or another jurisdiction-specific office. Current EAC guidance says no two states administer elections in the same way, elections are usually administered at the county level though some states use cities or townships, and the best source of practical registration and voting information is the local elections office. NASS’s `Can I Vote` / `#TrustedInfo2026` posture likewise routes voters to state and local election officials’ websites and materials rather than asking them to infer office ownership from generalized summaries. (xref: `eac_voter_faqs_page`; xref: `eac_register_and_vote_in_your_state_page`; xref: `nass_can_i_vote_page`; xref: `nass_trustedinfo_2026_page`; xref: `eac_who_is_in_charge_of_elections_in_my_state_page`)

## What this adds (and what it does not)

This document adds a compact **responsible-office specificity and jurisdiction-match floor** for docs in the `special_case_high_risk` subfamily.

It does **not** replace:
- the repeated official-anchor minimum in `docs/331-*`,
- the explicit non-overlap declarations in `docs/332-*`,
- the `305` / `307` lane-switch rule in `docs/333-*`,
- the temporal-volatility / no-cross-jurisdiction rule in `docs/334-*`,
- the release-date freshness floor in `docs/344-*`,
- the authority-hierarchy rule in `docs/345-*`,
- the current-state / superseding-notice rule in `docs/346-*`,
- the unresolved-conflict stop / no-synthesis rule in `docs/347-*`,
- the direct-jurisdiction governing-example floor in `docs/348-*`, or
- the direct-help-route / contactability floor in `docs/349-*`.

It only adds one more bounded rule: **a high-risk special-case doc should say which office role actually owns the decision for the voter’s case and should carry that office identity as a first-class field in the public artifact shape.**

## Responsible-office specificity and jurisdiction-match floor

For each doc whose row in `artifacts/tables/voter-facing-public-answer-surfaces.csv` is tagged `special_case_high_risk`, the release gate should require all of the following:

1. the doc contains a dedicated section that says, in substance, that the public answer should identify the responsible official office kind or role for the case — for example the county board, registrar, clerk, city/township office, tribal election office, state elections division, or another jurisdiction-specific official office,
2. that section says the responsible office must match the voter’s actual jurisdiction and election scope rather than being inferred from a neighboring county, another campus/facility, a state-level summary, or a generalized national explainer,
3. that section preserves `305` as the ordinary-help lane when the voter needs help locating or confirming the correct office/directory path and preserves `307` when the issue has crossed into intimidation, discrimination, wrongful denial despite likely eligibility, unsafe disclosure, or another rights/safety problem, and
4. the doc’s public artifact skeleton contains `authoritative_office_name` and `authoritative_office_scope` so the archive’s captured public-answer object states not only how to ask for help, but which official office is responsible.

The point is not to force every jurisdiction into one office taxonomy. The point is to stop the archive from shipping a high-risk edge-case surface that says “call this number” while leaving the reader unsure whether the controlling office is a county board, registrar, parish clerk, tribal office, city office, or state division.

## What this is meant to catch

This check is intentionally narrow. It is meant to catch bounded but meaningful failures such as:

- a high-risk doc that exposes a help page or phone number but never says which official office actually owns the case,
- a doc that names the right state but silently assumes the same office type controls every county, city, township, campus, tribal community, jail, or facility context,
- a doc whose public artifact skeleton carries help-contact fields but no bounded office-identity fields,
- or a release where a niche voter-facing page is technically “contactable” yet still easy to misroute because the public answer never identifies the responsible office role.

## Mechanical check

The release gate should reject the archive if any doc in the `special_case_high_risk` subfamily:

- lacks the required responsible-office-specificity heading,
- fails to say, in substance, that a responsible official office kind/role must be identified,
- fails to say the responsible office must match the voter’s jurisdiction/election scope rather than being inferred from nearby or generalized materials,
- fails to preserve `305` for ordinary-help office-location/confirmation and `307` for rights/safety escalation, or
- lacks both `authoritative_office_name` and `authoritative_office_scope` in the doc body.

The checker for this is:

- `scripts/check_voter_facing_special_case_responsible_office_specificity.py`

## Maintainer order of operations

When tightening or adding another high-risk special-case voter-facing surface adjacent to the `special_case_high_risk` cluster, maintainers should prefer this order:

1. decide whether the surface is actually distinct via `docs/310-*`,
2. wire the doc/template/checklist triplet and family registry via `docs/329-*` and `docs/330-*`,
3. prove repeated official-public grounding via `docs/331-*`,
4. confirm at least two direct jurisdiction-specific official-public governing examples via `docs/348-*`,
5. make adjacent-surface non-overlap explicit via `docs/332-*`,
6. make the `305` / `307` lane switch explicit via `docs/333-*`,
7. make temporal volatility / no-cross-jurisdiction portability explicit via `docs/334-*`,
8. confirm bounded recent official-source review before release via `docs/344-*`,
9. make the authority hierarchy explicit via `docs/345-*`,
10. make the current-state / superseding-notice discipline explicit via `docs/346-*`,
11. make the unresolved-conflict stop / no-synthesis / office-confirmation rule explicit via `docs/347-*`,
12. make the direct-help-route and contactability floor explicit via `docs/349-*`, and then
13. make the responsible-office specificity / jurisdiction-match floor explicit via this document.

That keeps the special-case cluster not only well-anchored and reachable, but harder to misroute because the public answer must identify which official office actually owns the voter’s case.

For the canonical ordered current control-stack map that keeps newer tail controls discoverable from anywhere in this maintainer subfamily, see `docs/355-special-case-voter-facing-surface-control-stack-reference-closure-and-navigation-firewall.md`.

## Sources (pinned IDs / lockfile IDs)

- EAC: Voter FAQs (xref: `eac_voter_faqs_page`)
- EAC: Register and Vote in Your State (xref: `eac_register_and_vote_in_your_state_page`)
- NASS: Can I Vote (xref: `nass_can_i_vote_page`)
- NASS: #TrustedInfo2026 (xref: `nass_trustedinfo_2026_page`)
- EAC: Who is in charge of elections in my state? (xref: `eac_who_is_in_charge_of_elections_in_my_state_page`)
