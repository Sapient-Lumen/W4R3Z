# 348. Special-case voter-facing surface direct-jurisdiction anchor floor and national-routing non-substitution

**Track:** Shared

This document is a compact companion to `docs/331-*`, `docs/332-*`, `docs/333-*`, `docs/334-*`, `docs/344-*`, `docs/345-*`, `docs/346-*`, and `docs/347-*` for the highest-risk voter-facing special-case cluster: the `special_case_high_risk` rows in `artifacts/tables/voter-facing-public-answer-surfaces.csv` (currently `317–328` and `335–343`).

It exists to answer one bounded maintainer question:

**“Even when a high-risk voter-facing edge-case surface says the current state/local source controls, does the doc itself actually carry direct jurisdiction-specific official examples, or is it still leaning only on national routing pages and generalized official explainers?”**

## Why this exists (bounded)

The archive already does eight important things for the `special_case_high_risk` subfamily:

1. requires repeated official-public grounding (`docs/331-*`),
2. requires explicit adjacent-surface non-overlap (`docs/332-*`),
3. requires safe fallback / escalation boundaries (`docs/333-*`),
4. requires an explicit statement that the rule is jurisdiction-specific, time-sensitive, and unsafe to port without current verification (`docs/334-*`),
5. requires a bounded recent review of official-public examples before release (`docs/344-*`),
6. requires an explicit statement that the current official state/local election-office source controls over national/archive summaries (`docs/345-*`),
7. requires an explicit statement telling the reader how to identify the current controlling official notice or instruction when older material remains visible (`docs/346-*`), and
8. requires an explicit unresolved-conflict stop / no-synthesis / office-confirmation rule (`docs/347-*`).

That still leaves one quiet source-mix failure mode.

A doc can satisfy all eight and still be weakly grounded if its actual cited examples are mostly or entirely national routing pages, generalized federal explainers, or archive summaries, while the prose merely says that a state or local source controls. For the highest-risk edge-case cluster, that is not enough. The doc should not only *say* that a direct jurisdiction-specific source controls; it should actually carry repeated direct-jurisdiction official-public examples of the governing answer surface.

Current official public routing supports that floor. EAC says election administration is highly decentralized and that the best source of practical voting information is the local elections office. Vote.gov routes voters to state-specific registration, update, and status pages. NASS's `Can I Vote` says it links directly to state election websites and trusted resources, and `#TrustedInfo2026` frames state and local election officials as trusted sources. If that is the public routing model, a high-risk edge-case doc should not be sourced as though national routing pages alone can stand in for the governing jurisdictional examples. (xref: `eac_voter_faqs_page`; xref: `eac_best_practices_faqs_election_officials_page`; xref: `vote_gov_register_page`; xref: `nass_can_i_vote_page`; xref: `nass_trustedinfo_2026_page`)

## What this adds (and what it does not)

This document adds a compact **direct-jurisdiction official-anchor floor** for docs in the `special_case_high_risk` subfamily.

It does **not** replace:
- the three-anchor official minimum in `docs/331-*`,
- the explicit adjacent-surface declarations required by `docs/332-*`,
- the fallback / escalation boundary required by `docs/333-*`,
- the temporal-volatility / no-cross-jurisdiction warning required by `docs/334-*`,
- the release-date freshness floor in `docs/344-*`,
- the authority-hierarchy rule in `docs/345-*`,
- the current-state / superseding-notice discipline in `docs/346-*`, or
- the unresolved-conflict stop / no-synthesis / office-confirmation rule in `docs/347-*`.

It only adds one more bounded rule: **a high-risk special-case doc should carry at least two direct jurisdiction-specific official-public anchors that show governing examples from real election-administration authorities, not just national routing pages or generalized official explainers.**

The direct-help-route / contactability floor from `docs/349-*` still matters too, because a high-risk edge-case doc can name the right governing authority while failing to expose a concrete reachable help path under deadline pressure. The responsible-office specificity / jurisdiction-match floor from `docs/350-*` matters too, because a high-risk edge-case doc can expose a help path while leaving the reader unsure which official office actually owns the case.

## Direct-jurisdiction official-anchor floor

For each doc whose row in `artifacts/tables/voter-facing-public-answer-surfaces.csv` is tagged `special_case_high_risk`, the release gate should require all of the following:

1. the doc cites at least three distinct lockfile-backed official-public source IDs as already required by `docs/331-*`,
2. at least **two** of those official-public source IDs point to direct jurisdiction-specific governing examples rather than national routing pages or generalized federal explainers, and
3. the doc contains a dedicated section that says, in substance, that direct state/local/tribal/county/registrar/clerk/board/court-governed official examples are required for this topic and that national routing pages, federal explainers, and archive summaries are not substitutes for those jurisdiction-specific governing examples.

For this rule, a “direct jurisdiction-specific governing example” means a lockfile-backed official-public source that directly reflects the governing answer surface for at least one real jurisdiction — for example a state election office page, county board page, registrar or clerk page, tribal election/government page, county or city election page, or another official public source that directly governs the voter’s case.

The point is not to ban national routing pages or federal rights explainers. The point is to prevent the archive from shipping a high-risk edge-case surface whose practical examples are still all generic while the doc merely asserts that the real answer lives somewhere else.

## What this is meant to catch

This check is intentionally narrow. It is meant to catch bounded but meaningful failures such as:

- a high-risk doc with three official anchors that are all national routing or generalized official pages,
- a doc that says the local office controls but never actually cites direct jurisdiction-specific governing examples,
- a surface that relies on EAC / Vote.gov / NASS routing pages plus one generalized federal rights explainer but no repeated state/local/tribal governing examples,
- or a release where the prose sounds jurisdiction-specific while the cited evidence remains mostly national and non-governing.

## Mechanical check

The release gate should reject the archive if any doc in the `special_case_high_risk` subfamily:

- lacks the required direct-jurisdiction heading,
- fails to say, in substance, that direct jurisdiction-specific official examples are required and that national routing pages / federal explainers / archive summaries are not substitutes, or
- has fewer than **two** distinct direct-jurisdiction official-public anchors after excluding national routing/general sources.

The checker for this is:

- `scripts/check_voter_facing_special_case_direct_jurisdiction_anchors.py`

## Maintainer order of operations

When tightening or adding another high-risk special-case voter-facing surface adjacent to the `special_case_high_risk` cluster, maintainers should prefer this order:

1. decide whether the surface is actually distinct via `docs/310-*`,
2. wire the doc/template/checklist triplet and family registry via `docs/329-*` and `docs/330-*`,
3. prove repeated official-public grounding via `docs/331-*`,
4. confirm at least two direct jurisdiction-specific official-public governing examples via this document,
5. make adjacent-surface non-overlap explicit via `docs/332-*`,
6. make the `305` / `307` lane switch explicit via `docs/333-*`,
7. make temporal volatility / no-cross-jurisdiction portability explicit via `docs/334-*`,
8. confirm bounded recent official-source review before release via `docs/344-*`,
9. make the authority hierarchy explicit via `docs/345-*`,
10. make the current-state / superseding-notice discipline explicit via `docs/346-*`, and then
11. make the unresolved-conflict stop / no-synthesis / office-confirmation rule explicit via `docs/347-*`, and then
12. make the direct-help-route / contactability floor explicit via `docs/349-*`, and then
13. make the responsible-office specificity / jurisdiction-match floor explicit via `docs/350-*`.

That keeps the special-case cluster small, jurisdictionally grounded, and harder to source with only national routing material.

For the canonical ordered current control-stack map that keeps newer tail controls discoverable from anywhere in this maintainer subfamily, see `docs/355-special-case-voter-facing-surface-control-stack-reference-closure-and-navigation-firewall.md`.

## Sources (pinned IDs / lockfile IDs)

- EAC: Voter FAQs (xref: `eac_voter_faqs_page`)
- EAC: Best Practices: FAQs for Election Officials (xref: `eac_best_practices_faqs_election_officials_page`)
- Vote.gov: Register to vote / update registration (xref: `vote_gov_register_page`)
- NASS: Can I Vote (xref: `nass_can_i_vote_page`)
- NASS: #TrustedInfo2026 (xref: `nass_trustedinfo_2026_page`)
