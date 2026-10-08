# 347. Special-case voter-facing surface unresolved-conflict stop and no-synthesis rule

**Track:** Shared

This document is a compact companion to `docs/331-*`, `docs/332-*`, `docs/333-*`, `docs/334-*`, `docs/344-*`, `docs/345-*`, and `docs/346-*` for the highest-risk voter-facing special-case cluster: the `special_case_high_risk` rows in `artifacts/tables/voter-facing-public-answer-surfaces.csv` (currently `317–328` and `335–343`).

It exists to answer one bounded maintainer question:

**“Even after authority, freshness, and superseding-notice rules are in place, what should a high-risk edge-case surface say when the visible official materials are still materially conflicting or incomplete and no current controlling answer is yet clear?”**

## Why this exists (bounded)

The archive already does seven important things for the `special_case_high_risk` subfamily:

1. requires repeated official-public grounding (`docs/331-*`),
2. requires explicit adjacent-surface non-overlap (`docs/332-*`),
3. requires safe fallback / escalation boundaries (`docs/333-*`),
4. requires an explicit statement that the rule is jurisdiction-specific, time-sensitive, and unsafe to port without current verification (`docs/334-*`),
5. requires a bounded recent review of official-public examples before release (`docs/344-*`),
6. requires an explicit statement that the current official state/local election-office source controls over national/archive summaries (`docs/345-*`), and
7. requires an explicit statement telling the reader how to identify the current controlling official notice or instruction when older material remains visible (`docs/346-*`).

That still leaves one quiet but important failure mode.

A doc can satisfy all seven and still mislead when multiple visible official-public artifacts remain **materially inconsistent, incomplete, or unresolved** and the doc silently synthesizes a controlling answer by combining fragments, copying the majority pattern, or inferring what the office "probably meant." For the highest-risk edge-case cluster, that is unsafe. These are exactly the topics where small wording differences can change whether a voter uses the right site, the right ballot-request path, the right helper or bearer rule, the right custody or facility workflow, or the right rights-preserving fallback.

Current public routing guidance supports a stricter stop rule. EAC says election administration is highly decentralized and that the best practical source of voting information is the local elections office. Vote.gov routes voters to their own state or territory page for registration, updates, and status. NASS's `Can I Vote` directs users to state election websites and trusted resources, and NASS's `#TrustedInfo2026` posture likewise pushes the public back to election officials rather than generalized summaries. When that is the public routing model, a high-risk edge-case doc should not pretend it can safely synthesize a controlling answer after official materials still conflict. (xref: `eac_voter_faqs_page`; xref: `vote_gov_register_page`; xref: `nass_can_i_vote_page`; xref: `nass_trustedinfo_2026_page`)

## What this adds (and what it does not)

This document adds a compact **unresolved-conflict stop / no-synthesis / office-confirmation** rule for docs in the `special_case_high_risk` subfamily.

It does **not** replace:
- the official-anchor count minimum in `docs/331-*`,
- the explicit adjacent-surface declarations required by `docs/332-*`,
- the fallback / escalation boundary required by `docs/333-*`,
- the temporal-volatility / no-cross-jurisdiction warning required by `docs/334-*`,
- the release-date freshness floor in `docs/344-*`,
- the authority-hierarchy rule in `docs/345-*`,
- the current-state / superseding-notice discipline in `docs/346-*`,
- the direct-jurisdiction anchor floor in `docs/348-*`, and
- the direct-help-route / contactability floor in `docs/349-*`, and
- the responsible-office specificity / jurisdiction-match floor in `docs/350-*`.

It only adds one more bounded rule: **if the remaining official-public materials still materially conflict or leave a controlling gap after the reader already checked authority and superseding cues, the doc should say plainly to stop and obtain current case-specific confirmation rather than synthesizing an answer from fragments.**

## Unresolved-conflict stop floor

For each doc whose row in `artifacts/tables/voter-facing-public-answer-surfaces.csv` is tagged `special_case_high_risk`, the doc should contain a dedicated section that says, in substance, all of the following:

1. official-public materials can still conflict, disagree, or leave a material gap even after checking dates and superseding notices,
2. if no current controlling official instruction is clear, the reader should **not synthesize, combine, average, or infer** a controlling answer from partial artifacts, neighboring-jurisdiction examples, or archive summaries,
3. unresolved conflict itself is a **stop condition** rather than a prompt to guess,
4. the reader should use the current authoritative state or local election office, registrar, clerk, county board, or the office/help path named in `305` to obtain case-specific confirmation before acting, and
5. if the unresolved conflict is paired with denial despite likely eligibility, intimidation, discrimination, unsafe disclosure, or another rights/safety problem, the reader should move to `307`.

The point is not to require every jurisdiction to publish one perfect “official conflict resolved” banner. The point is to prevent the archive from quietly improvising a controlling answer in exactly the situations where a stressed voter most needs the archive to say **stop guessing and get the authoritative office to confirm what controls now**.

## What this is meant to catch

This check is intentionally narrow. It is meant to catch bounded but meaningful failures such as:

- a disaster-relocation page that correctly names the office and freshness cues but still merges partially conflicting county and state notices into one inferred answer,
- a custody or facility page that recognizes stale handouts but still improvises a rule when the public packet, registrar FAQ, and facility instructions remain unresolved,
- a bearer/agent or challenged-voter page that treats “most sources say X” as enough even though the currently controlling official instruction is not actually clear,
- or a high-risk special-case doc that correctly says national summaries are not controlling yet still writes as though the archive may safely synthesize the missing jurisdiction-specific answer itself.

## Mechanical check

The release gate should reject the archive if any doc in the `special_case_high_risk` subfamily is missing a required unresolved-conflict heading or fails to say, in substance, all of the following inside that section:

- official-public materials can still conflict / disagree / remain unresolved,
- the reader should **not synthesize / combine / infer / average** a controlling answer from partial artifacts,
- unresolved conflict is a stop condition,
- the current authoritative office or `305` help path should be used for case-specific confirmation, and
- `307` remains the rights/safety lane when unresolved conflict is paired with a rights or safety problem.

The checker for this is:

- `scripts/check_voter_facing_special_case_unresolved_conflict_stop.py`

## Maintainer order of operations

When tightening or adding another high-risk special-case voter-facing surface adjacent to the `special_case_high_risk` cluster, maintainers should prefer this order:

1. decide whether the surface is actually distinct via `docs/310-*`,
2. wire the doc/template/checklist triplet and family registry via `docs/329-*` and `docs/330-*`,
3. prove repeated official-public grounding via `docs/331-*`,
4. make adjacent-surface non-overlap explicit via `docs/332-*`,
5. make the `305` / `307` lane switch explicit via `docs/333-*`,
6. make temporal volatility / no-cross-jurisdiction portability explicit via `docs/334-*`,
7. confirm bounded recent official-source review before release via `docs/344-*`,
8. make the authority hierarchy explicit via `docs/345-*`,
9. make the current-state / superseding-notice discipline explicit via `docs/346-*`, and then
10. make the unresolved-conflict stop / no-synthesis / office-confirmation rule explicit via this document, and then
11. confirm the doc still carries at least two direct jurisdiction-specific official-public governing examples via `docs/348-*`, and then
12. make the direct office-help route / contactability floor explicit via `docs/349-*`, and then
13. make the responsible-office specificity / jurisdiction-match floor explicit via `docs/350-*`.

That keeps the special-case cluster small, current, and less likely to bluff past unresolved official disagreement.

For the canonical ordered current control-stack map that keeps newer tail controls discoverable from anywhere in this maintainer subfamily, see `docs/355-special-case-voter-facing-surface-control-stack-reference-closure-and-navigation-firewall.md`.

## Sources (pinned IDs / lockfile IDs)

- EAC: Voter FAQs (xref: `eac_voter_faqs_page`)
- Vote.gov: Register to vote / update registration (xref: `vote_gov_register_page`)
- NASS: Can I Vote (xref: `nass_can_i_vote_page`)
- NASS: #TrustedInfo2026 (xref: `nass_trustedinfo_2026_page`)
