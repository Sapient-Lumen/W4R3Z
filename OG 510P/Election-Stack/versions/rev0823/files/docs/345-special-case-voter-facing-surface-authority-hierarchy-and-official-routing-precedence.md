# 345. Special-case voter-facing surface authority hierarchy and official-routing precedence

**Track:** Shared

This document is a compact companion to `docs/331-*`, `docs/332-*`, `docs/333-*`, `docs/334-*`, `docs/344-*`, and `docs/346-*` for the highest-risk voter-facing special-case cluster: the `special_case_high_risk` rows in `artifacts/tables/voter-facing-public-answer-surfaces.csv` (currently `317–328` and `335–343`).

It exists to answer one bounded maintainer question:

**“Even when a high-risk voter-facing edge-case surface is well-anchored, freshness-checked, and explicit about overlap, does it also say clearly which source actually controls when a voter must act?”**

## Why this exists (bounded)

The archive already does five important things for the `special_case_high_risk` subfamily:

1. requires repeated official-public grounding (`docs/331-*`),
2. requires explicit adjacent-surface non-overlap (`docs/332-*`),
3. requires safe fallback / escalation boundaries (`docs/333-*`),
4. requires an explicit statement that the rule is jurisdiction-specific, time-sensitive, and unsafe to port without current verification (`docs/334-*`), and
5. requires a bounded recent review of official-public examples before release (`docs/344-*`).

That is necessary, but still leaves one quiet failure mode.

A doc can satisfy all five and still mislead if it never says plainly that **the controlling answer is the current official state or local election-office source for the voter’s actual jurisdiction and election**. Without that explicit hierarchy, a reader can over-trust a federal routing page, a statewide summary, a county example from somewhere else, or even this archive’s bounded explanatory prose as if all of them carried the same authority. For the highest-risk special-case surfaces, that is not a small wording issue. It can change whether the voter uses the right site, the right ballot-delivery model, the right helper or agent rule, the right challenge/oath path, or the right emergency or rights-escalation route.

Current official public-information routing strongly supports making that hierarchy explicit. EAC’s current voter FAQ says election administration is highly decentralized and that the best practical source of voting information is the local election office. EAC’s current state-routing page directs voters to state election-office websites, local office directories, and state-specific registration/update/status paths. Vote.gov’s current registration/update flow likewise sends the voter to the state or territory page for the operative rules. NASS’s current Can I Vote page says it links directly to state election websites and trusted resources rather than acting as the final rule-text itself, and `#TrustedInfo2026` explicitly promotes state and local election officials as the trusted sources of election information. (xref: `eac_voter_faqs_page`; xref: `eac_register_and_vote_in_your_state_page`; xref: `vote_gov_register_page`; xref: `nass_can_i_vote_page`; xref: `nass_trustedinfo_2026_page`)

## What this adds (and what it does not)

This document adds a compact **authority-hierarchy / official-routing-precedence** rule for docs in the `special_case_high_risk` subfamily.

It does **not** replace:
- the official-anchor count minimum in `docs/331-*`,
- the explicit adjacent-surface declarations required by `docs/332-*`,
- the fallback / escalation boundary required by `docs/333-*`,
- the temporal-volatility / no-cross-jurisdiction warning required by `docs/334-*`,
- the release-date freshness floor in `docs/344-*`,
- the current-state / superseding-notice discipline in `docs/346-*`, or
- the ordinary office/help lane in `docs/305-*`.

It is only a compact prose-control rule: a way to stop a high-risk niche voter surface from sounding more nationally portable or self-sufficient than it really is, not a substitute for the unresolved-conflict stop / no-synthesis rule in `docs/347-*` or the direct-jurisdiction anchor floor in `docs/348-*` or the direct-help-route / contactability floor in `docs/349-*` or the responsible-office specificity / jurisdiction-match floor in `docs/350-*`.

## Authority hierarchy floor

For each doc whose row in `artifacts/tables/voter-facing-public-answer-surfaces.csv` is tagged `special_case_high_risk`, the doc should contain a dedicated section that says, in substance, all of the following:

1. the **controlling answer** is the current official state or local election-office source for the voter’s jurisdiction and election,
2. the relevant controlling source may be a county board, registrar, clerk, state election-office page, ballot packet, cure notice, or other official public instruction that directly governs the voter’s case,
3. national routing pages, this archive, and other generalized explainers are **routing aids**, not substitutes for that controlling jurisdiction-specific official source, and
4. if those materials differ, the reader should prefer the **most current official instruction that directly governs the case**.

The point is not to diminish federal/statewide routing tools or compact explanatory docs. It is to make the hierarchy explicit before a voter treats a summary like a binding operational answer.

## What this is meant to catch

This check is intentionally narrow. It is meant to catch bounded but meaningful failures such as:

- a disaster-displacement page that says “rules vary by jurisdiction” but never says the current county or state official page actually controls,
- a custody or facility page that names examples but leaves the reader thinking the archive’s prose is the operative instruction,
- a helper / bearer / challenged-voter page that explains the edge case well but never says that the current official form, notice, or office instruction is controlling if details differ,
- or a high-risk special-case doc whose sources are recent and official but whose text still reads like a generalized national answer.

## Mechanical check

The release gate should reject the archive if any doc in the `special_case_high_risk` subfamily is missing a required authority-hierarchy heading or fails to say, in substance, all of the following inside that section:

- the **current official** source controls,
- the controlling source is the voter’s **state/local election-office** or directly governing official instruction,
- national/generalized/archive summaries are **routing aids** or **not substitutes**, and
- if materials differ or conflict, prefer the **most current official** instruction that directly governs the case.

The checker for this is:

- `scripts/check_voter_facing_special_case_official_routing_precedence.py`

## Maintainer order of operations

When tightening or adding another high-risk special-case voter-facing surface adjacent to the `special_case_high_risk` cluster, maintainers should prefer this order:

1. decide whether the surface is actually distinct via `docs/310-*`,
2. wire the doc/template/checklist triplet and family registry via `docs/329-*` and `docs/330-*`,
3. prove repeated official-public grounding via `docs/331-*`,
4. make adjacent-surface non-overlap explicit via `docs/332-*`,
5. make the `305` / `307` lane switch explicit via `docs/333-*`,
6. make temporal volatility / no-cross-jurisdiction portability explicit via `docs/334-*`,
7. make the authority hierarchy explicit via this document, and then
8. confirm that at least two official-public anchors for the surface were reviewed within the bounded release window defined in `docs/344-*`, and then
9. make the current-state / superseding-notice discipline explicit via `docs/346-*`, and then
10. make the unresolved-conflict stop / no-synthesis rule explicit via `docs/347-*`, and then
11. confirm the doc still carries at least two direct jurisdiction-specific official-public governing examples via `docs/348-*`, and then
12. make the direct office-help route / contactability floor explicit via `docs/349-*`, and then
13. make the responsible-office specificity / jurisdiction-match floor explicit via `docs/350-*`.

That keeps the special-case cluster small, current, and clearer about which public source actually controls when the question becomes real.

For the canonical ordered current control-stack map that keeps newer tail controls discoverable from anywhere in this maintainer subfamily, see `docs/355-special-case-voter-facing-surface-control-stack-reference-closure-and-navigation-firewall.md`.

## Sources (pinned IDs / lockfile IDs)

- EAC: Voter FAQs (xref: `eac_voter_faqs_page`)
- EAC: Register and Vote in Your State (xref: `eac_register_and_vote_in_your_state_page`)
- Vote.gov: Register to vote / update registration (xref: `vote_gov_register_page`)
- NASS: Can I Vote (xref: `nass_can_i_vote_page`)
- NASS: #TrustedInfo2026 (xref: `nass_trustedinfo_2026_page`)
