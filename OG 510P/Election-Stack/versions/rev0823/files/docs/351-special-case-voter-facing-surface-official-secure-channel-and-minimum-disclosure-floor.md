# 351. Special-case voter-facing surface official secure-channel and minimum-disclosure floor

**Track:** Shared

This document is a compact companion to `docs/331-*`, `docs/332-*`, `docs/333-*`, `docs/334-*`, `docs/344-*`, `docs/345-*`, `docs/346-*`, `docs/347-*`, `docs/348-*`, `docs/349-*`, and `docs/350-*` for the highest-risk voter-facing special-case cluster: the `special_case_high_risk` rows in `artifacts/tables/voter-facing-public-answer-surfaces.csv` (currently `317–328` and `335–343`).

It exists to answer one bounded maintainer question:

**“Even when a high-risk voter-facing edge-case surface names the right office and help path, does it also say how to contact that office without oversharing sensitive personal information or using an unverified channel?”**

## Why this exists (bounded)

The archive already does eleven important things for the `special_case_high_risk` subfamily:

1. requires repeated official-public grounding (`docs/331-*`),
2. requires explicit adjacent-surface non-overlap (`docs/332-*`),
3. requires safe fallback / escalation boundaries (`docs/333-*`),
4. requires an explicit statement that the rule is jurisdiction-specific, time-sensitive, and unsafe to port without current verification (`docs/334-*`),
5. requires a bounded recent review of official-public examples before release (`docs/344-*`),
6. requires an explicit statement that the current official state/local election-office source controls over national/archive summaries (`docs/345-*`),
7. requires an explicit statement telling the reader how to identify the current controlling official notice or instruction when older material remains visible (`docs/346-*`),
8. requires an explicit unresolved-conflict stop / no-synthesis / office-confirmation rule (`docs/347-*`),
9. requires at least two direct jurisdiction-specific official-public governing examples rather than only national routing pages or generalized official explainers (`docs/348-*`),
10. requires a concrete official help/contact path instead of abstract advice to “contact the office” (`docs/349-*`), and
11. requires the public answer to identify which official office role actually owns the case (`docs/350-*`).

That still leaves one quiet but material disclosure failure mode.

A doc can satisfy all eleven and still mislead or endanger the reader if it tells them to reach the right office but does not say how to do so safely. These high-risk surfaces routinely involve sensitive personal facts or documents: full or partial Social Security numbers, driver’s-license or state-ID numbers, dates of birth, confidential residential addresses, court orders, custody or facility records, safety-program enrollment materials, citizenship documents, or other records that should not be sprayed into public, generic, or unverified channels. Current official guidance supports tightening that boundary. EAC’s current contact page explicitly tells readers not to include personally identifiable information (PII) when submitting a question or comment. Vote.gov’s current trust marker says official websites use `.gov`, secure `.gov` websites use HTTPS, and sensitive information should be shared only on official, secure websites. EAC’s voter FAQ and state-routing materials still direct voters back to current state and local election offices, and NASS’s `#TrustedInfo2026` posture still frames state and local election officials as the trusted source for election information. (xref: `eac_contact_us_page`; xref: `vote_gov_home_page`; xref: `eac_voter_faqs_page`; xref: `eac_register_and_vote_in_your_state_page`; xref: `nass_trustedinfo_2026_page`)

## What this adds (and what it does not)

This document adds a compact **official secure-channel and minimum-disclosure floor** for docs in the `special_case_high_risk` subfamily.

It does **not** replace:
- the repeated official-anchor minimum in `docs/331-*`,
- the explicit non-overlap declarations in `docs/332-*`,
- the `305` / `307` lane-switch rule in `docs/333-*`,
- the temporal-volatility / no-cross-jurisdiction rule in `docs/334-*`,
- the release-date freshness floor in `docs/344-*`,
- the authority-hierarchy rule in `docs/345-*`,
- the current-state / superseding-notice rule in `docs/346-*`,
- the unresolved-conflict stop / no-synthesis rule in `docs/347-*`,
- the direct-jurisdiction governing-example floor in `docs/348-*`,
- the direct-help-route / contactability floor in `docs/349-*`,
- the responsible-office specificity / jurisdiction-match floor in `docs/350-*`, or
- the general public-artifact secret/PII discipline in `docs/189-*`.

It only adds one more bounded rule: **a high-risk special-case voter-facing doc should say which official secure channel is appropriate for sensitive contact and should tell the reader not to disclose more personal information than the official process actually requires.**

## Official secure-channel and minimum-disclosure floor

For each doc whose row in `artifacts/tables/voter-facing-public-answer-surfaces.csv` is tagged `special_case_high_risk`, the release gate should require all of the following:

1. the doc contains a dedicated section that says, in substance, that the voter should use only the named official website, secure HTTPS form, verified local office directory, official office phone, or in-person office path for sensitive case details or documents,
2. that section says that if the current public instructions do not expose a secure submission path, the voter should use the responsible official office or `305` to confirm the correct secure channel before transmitting records,
3. that section says the voter should not disclose more personal information than the current official process requires and should not post or send sensitive identifiers through public, unverified, or generalized channels,
4. that section preserves `307` when the disclosure risk itself is tied to intimidation, coercion, discrimination, unsafe exposure, wrongful denial despite likely eligibility, or another rights/safety problem, and
5. the doc’s public artifact skeleton contains `official_secure_channel_note` and `minimum_necessary_disclosure_note` so the captured public answer states both how to reach the office and how to avoid oversharing.

The point is not to force every jurisdiction to publish the same digital workflow. Some offices will use secure web forms, some will direct voters to phone first, some will require in-person handling, and some will route sensitive forms through a specific clerk, registrar, county board, or safety-program office. The point is to prevent the archive from shipping a high-risk edge-case page that tells voters to “contact the office” while leaving them to guess whether a generic email, a social-media inbox, a public comment form, or an unverified page is acceptable for sensitive records.

## What this is meant to catch

This check is intentionally narrow. It is meant to catch bounded but meaningful failures such as:

- a high-risk doc that names the right office but never says which secure or official channel is appropriate for sensitive documents,
- a doc that tells the reader to reach out but does not say to call first when no secure upload/submission path is publicly shown,
- a doc that exposes a help URI or phone but never warns against oversharing full SSNs, driver’s-license numbers, dates of birth, confidential addresses, court papers, or similar sensitive records through public or unverified channels,
- a doc whose public artifact skeleton carries office/help fields but no compact disclosure-safety fields,
- or a release where the archive routes a voter into the right office but still leaves them to improvise a risky submission channel.

## Mechanical check

The release gate should reject the archive if any doc in the `special_case_high_risk` subfamily:

- lacks the required secure-channel / minimum-disclosure heading,
- fails to name official or secure channel types in substance,
- fails to say to confirm the correct secure path before transmitting records when the public instructions do not already show one,
- fails to warn against sending more personal information than necessary or against using public/unverified/generalized channels for sensitive identifiers,
- fails to preserve `305` for ordinary secure-path confirmation and `307` for rights/safety escalation, or
- lacks both `official_secure_channel_note` and `minimum_necessary_disclosure_note` in the doc body.

The checker for this is:

- `scripts/check_voter_facing_special_case_secure_channel_and_minimum_disclosure.py`

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
12. make the direct-help-route and contactability floor explicit via `docs/349-*`,
13. make the responsible-office specificity / jurisdiction-match floor explicit via `docs/350-*`, and then
14. make the official secure-channel and minimum-disclosure floor explicit via this document.

That keeps the special-case cluster not only current, reachable, and jurisdiction-matched, but also less likely to misroute voters into oversharing sensitive records on the wrong channel.

For the canonical ordered current control-stack map that keeps newer tail controls discoverable from anywhere in this maintainer subfamily, see `docs/355-special-case-voter-facing-surface-control-stack-reference-closure-and-navigation-firewall.md`.

## Sources (pinned IDs / lockfile IDs)

- EAC: Contact U.S. EAC (xref: `eac_contact_us_page`)
- Vote.gov: Home page / official-site trust marker (xref: `vote_gov_home_page`)
- EAC: Voter FAQs (xref: `eac_voter_faqs_page`)
- EAC: Register and Vote in Your State (xref: `eac_register_and_vote_in_your_state_page`)
- NASS: #TrustedInfo2026 (xref: `nass_trustedinfo_2026_page`)
