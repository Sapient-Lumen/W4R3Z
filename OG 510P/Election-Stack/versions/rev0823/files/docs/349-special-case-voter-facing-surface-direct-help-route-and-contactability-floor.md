# 349. Special-case voter-facing surface direct-help route and contactability floor

**Track:** Shared

This document is a compact companion to `docs/331-*`, `docs/332-*`, `docs/333-*`, `docs/334-*`, `docs/344-*`, `docs/345-*`, `docs/346-*`, `docs/347-*`, and `docs/348-*` for the highest-risk voter-facing special-case cluster: the `special_case_high_risk` rows in `artifacts/tables/voter-facing-public-answer-surfaces.csv` (currently `317–328` and `335–343`).

It exists to answer one bounded maintainer question:

**“Even when a high-risk voter-facing edge-case surface says ‘contact the right office,’ does it actually expose a concrete, reachable official help path the voter can use before the deadline closes?”**

## Why this exists (bounded)

The archive already does nine important things for the `special_case_high_risk` subfamily:

1. requires repeated official-public grounding (`docs/331-*`),
2. requires explicit adjacent-surface non-overlap (`docs/332-*`),
3. requires safe fallback / escalation boundaries (`docs/333-*`),
4. requires an explicit statement that the rule is jurisdiction-specific, time-sensitive, and unsafe to port without current verification (`docs/334-*`),
5. requires a bounded recent review of official-public examples before release (`docs/344-*`),
6. requires an explicit statement that the current official state/local election-office source controls over national/archive summaries (`docs/345-*`),
7. requires an explicit statement telling the reader how to identify the current controlling official notice or instruction when older material remains visible (`docs/346-*`),
8. requires an explicit unresolved-conflict stop / no-synthesis / office-confirmation rule (`docs/347-*`), and
9. requires at least two direct jurisdiction-specific official-public governing examples rather than only national routing pages or generalized official explainers (`docs/348-*`).

That still leaves one quiet operational failure mode.

A doc can satisfy all nine and still be weak at the exact moment a voter needs it most if it only says “contact your local election office” in the abstract while failing to expose a concrete current help/contact path. For this high-risk edge-case cluster, that is not enough. A same-day problem about replacement ballots, assignment, provisional routing, emergency absentee delivery, jail voting, confidentiality, or challenged-voter procedures often turns on whether the voter can quickly reach the right county board, registrar, clerk, tribal election office, or other governing official help route before a cut-off, pickup window, office closing time, or handoff deadline passes.

Current official public routing supports that tighter floor. EAC says election administration is highly decentralized and that the best source of practical registration and voting information is the local elections office, and EAC's state-routing tool exists to help voters reach those official state/local channels. NASS's `Can I Vote` says it links directly to state election websites and trusted resources, and NASS's `#TrustedInfo2026` posture reinforces that state and local election officials are the trusted operational source. Vote.gov likewise routes voters to state-specific official pages for registration and updates rather than treating a national explainer as the operational endpoint. (xref: `eac_voter_faqs_page`; xref: `eac_register_and_vote_in_your_state_page`; xref: `eac_best_practices_faqs_election_officials_page`; xref: `nass_can_i_vote_page`; xref: `nass_trustedinfo_2026_page`; xref: `vote_gov_register_page`)

## What this adds (and what it does not)

This document adds a compact **direct-help-route and contactability floor** for docs in the `special_case_high_risk` subfamily.

It does **not** replace:
- the repeated official-anchor minimum in `docs/331-*`,
- the explicit non-overlap declarations required by `docs/332-*`,
- the `305` / `307` lane-switch rule in `docs/333-*`,
- the temporal-volatility / no-cross-jurisdiction rule in `docs/334-*`,
- the release-date freshness floor in `docs/344-*`,
- the authority-hierarchy rule in `docs/345-*`,
- the current-state / superseding-notice rule in `docs/346-*`,
- the unresolved-conflict stop / no-synthesis rule in `docs/347-*`, or
- the direct-jurisdiction governing-example floor in `docs/348-*`.

It only adds one more bounded rule: **a high-risk special-case doc should expose a concrete official help/contact path the voter can actually use, not just abstract prose saying the right office exists somewhere.** The responsible-office specificity / jurisdiction-match floor in `docs/350-*` still matters too, because a reachable phone number or help page is not the same thing as naming which official office role actually owns the case.

## Direct-help-route and contactability floor

For each doc whose row in `artifacts/tables/voter-facing-public-answer-surfaces.csv` is tagged `special_case_high_risk`, the release gate should require all of the following:

1. the doc contains a dedicated section that says, in substance, that the public answer must expose a real official help/contact path — for example a current office/help page, local office directory, or phone/help number — rather than stopping at abstract advice to “contact the election office,”
2. that section says the contact/help path matters for same-day, deadline-near, or other time-sensitive case-specific confirmation,
3. that section preserves `305` as the ordinary-help lane for case-specific or deadline-near clarification and preserves `307` when the problem has crossed into intimidation, discrimination, wrongful denial despite likely eligibility, unsafe disclosure, or another rights/safety issue, and
4. the doc's public artifact skeleton contains `authoritative_help_uri` and/or `authoritative_help_phone` so the archive's captured public-answer object has a bounded place to carry a real official help route.

The point is not to force every jurisdiction into a single contact mechanism. Some official surfaces are best represented by a county office page; others by a registrar page, board page, tribal election office page, clerk page, or official phone/help line. The point is to prevent the archive from shipping a high-risk edge-case surface that says “ask the right office” while never actually demanding a concrete help/contact route in the public-answer shape.

## What this is meant to catch

This check is intentionally narrow. It is meant to catch bounded but meaningful failures such as:

- a high-risk doc that repeatedly says the local office controls but never exposes a concrete help/contact path,
- a doc that routes the reader to `305` in prose but leaves the public artifact skeleton without any bounded help URI or help phone field,
- a surface that carries strong jurisdiction-specific governing examples but still leaves deadline-near voters to hunt manually for how to reach the responsible office,
- or a release where the archive talks correctly about official routing but still ships a page that is not operationally actionable under time pressure.

## Mechanical check

The release gate should reject the archive if any doc in the `special_case_high_risk` subfamily:

- lacks the required direct-help-route heading,
- fails to say, in substance, that a real official help/contact path is required,
- fails to say that same-day / deadline-near / time-sensitive confirmation is part of why that route matters,
- fails to preserve `305` for ordinary-help routing and `307` for rights/safety escalation, or
- lacks both `authoritative_help_uri` and `authoritative_help_phone` in the doc body.

The checker for this is:

- `scripts/check_voter_facing_special_case_contactability.py`

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
11. make the unresolved-conflict stop / no-synthesis / office-confirmation rule explicit via `docs/347-*`, and then
12. make the direct-help-route and contactability floor explicit via this document, and then
13. make the responsible-office specificity / jurisdiction-match floor explicit via `docs/350-*`.

That keeps the special-case cluster not only well-anchored and jurisdiction-specific, but operationally usable when the voter must reach a real official office under time pressure.

For the canonical ordered current control-stack map that keeps newer tail controls discoverable from anywhere in this maintainer subfamily, see `docs/355-special-case-voter-facing-surface-control-stack-reference-closure-and-navigation-firewall.md`.

## Sources (pinned IDs / lockfile IDs)

- EAC: Voter FAQs (xref: `eac_voter_faqs_page`)
- EAC: Register and Vote in Your State (xref: `eac_register_and_vote_in_your_state_page`)
- EAC: Best Practices: FAQs for Election Officials (xref: `eac_best_practices_faqs_election_officials_page`)
- NASS: Can I Vote (xref: `nass_can_i_vote_page`)
- NASS: #TrustedInfo2026 (xref: `nass_trustedinfo_2026_page`)
- Vote.gov: Register to vote / update registration (xref: `vote_gov_register_page`)
