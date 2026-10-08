# 344. Special-case voter-facing surface release-freshness floor and source-review window

**Track:** Shared

This document is a compact companion to `docs/331-*`, `docs/332-*`, `docs/333-*`, `docs/334-*`, `docs/345-*`, and `docs/346-*` for the highest-risk voter-facing special-case cluster: the `special_case_high_risk` rows in `artifacts/tables/voter-facing-public-answer-surfaces.csv` (currently `317–328` and `335–343`).

It exists to answer one bounded maintainer question:

**“What minimum release-time freshness check should the archive apply before it ships a high-risk voter-facing edge-case surface that already has official anchors and a temporal-volatility warning?”**

## Why this exists (bounded)

The archive already does six important things for the `special_case_high_risk` subfamily:

1. requires repeated official-public grounding (`docs/331-*`),
2. requires explicit adjacent-surface non-overlap (`docs/332-*`),
3. requires safe fallback / escalation boundaries (`docs/333-*`), and
4. requires an explicit statement that the rule is jurisdiction-specific, time-sensitive, and unsafe to port without current verification (`docs/334-*`), and
5. requires an explicit statement that the current official state/local election-office source controls over national/archive summaries (`docs/345-*`), and
6. requires an explicit statement that the doc tells the reader how to identify the current controlling official notice or instruction when older material remains visible (`docs/346-*`).

That is necessary, but not quite sufficient.

A doc can satisfy all six and still drift into a weak release posture if every cited official example was last checked long before the current release. For this subfamily, that matters more than it does for many other docs, because these surfaces routinely answer questions where stale public guidance can change the voter's next lawful action: whether a moved voter must go to a different site, whether an inactive record still leaves a live path to vote, whether a voter in custody or a facility needs a special handoff model, whether a challenge can still be cured with an oath, or whether a bearer / agent rule changed. The archive should therefore make one small thing mechanically true at release time: **at least some of the official-public examples for each high-risk special-case doc were reviewed recently relative to the release itself**.

This is also consistent with current public-information routing from election authorities. EAC's voter FAQ and state-routing materials direct voters to current election-official sources rather than one generalized national answer page, and NASS's current `#TrustedInfo2026` posture reinforces that official-election-site routing discipline. (xref: `eac_voter_faqs_page`; xref: `eac_register_and_vote_in_your_state_page`; xref: `nass_trustedinfo_2026_page`)

## What this adds (and what it does not)

This document adds a **release-date freshness floor** for lockfile-backed official anchors used by docs in the `special_case_high_risk` subfamily.

It does **not** replace:
- the official-anchor count minimum in `docs/331-*`,
- the explicit temporal-volatility prose required by `docs/334-*`,
- the explicit authority-hierarchy prose required by `docs/345-*`,
- the explicit current-state / superseding-notice prose required by `docs/346-*`,
- the general lockfile hygiene rules in `docs/151-*`, `docs/191-*`, and `docs/228-*`, or
- election-specific operational review discipline that may need tighter refresh cycles near a real election.

It is only a compact, deterministic release gate: a way to prevent a clearly high-risk edge-case doc from being shipped with nothing but stale official examples, not a substitute for the unresolved-conflict stop / no-synthesis rule in `docs/347-*` or the direct-jurisdiction anchor floor in `docs/348-*` or the direct-help-route / contactability floor in `docs/349-*` or the responsible-office specificity / jurisdiction-match floor in `docs/350-*`.

## Release-date freshness floor

For each doc whose row in `artifacts/tables/voter-facing-public-answer-surfaces.csv` is tagged `special_case_high_risk`, the release gate should require all of the following:

1. the doc cites at least two distinct lockfile-backed official-public source IDs,
2. at least two of those official-public source IDs carry a valid `retrieved` date in `evidence/lock/external-sources.toml`, and
3. at least two of those official-public source IDs were retrieved **no more than 90 days before the release date recorded at the head of `CHANGELOG.md`**.

The release-date anchor is intentionally the archive's own top changelog date rather than wall-clock “today,” so the check stays deterministic inside a revisioned archive.

The point is not to guarantee that every cited source changed recently. The point is to guarantee that each high-risk special-case surface had a bounded, recent review of current official-public examples before release.

## Why 90 days

`90 days` is a compact floor, not a claim that quarterly review is always enough.

It is tight enough to make “we shipped a time-volatile high-risk voter surface using only old official captures” mechanically harder, while still loose enough to avoid turning ordinary release work into a constant-source-refresh exercise. When a real election is close, maintainers should often do better than this floor — for example, the archive's source-lock guidance already prefers more frequent review in the 60 days before an election. This document does not weaken that expectation; it only adds a minimal release-time floor for this especially fragile subfamily.

## Failure modes this is meant to catch

This check is intentionally small. It is meant to catch bounded but meaningful failures such as:

- a high-risk special-case doc that still cites official sources, but none reviewed recently relative to the release,
- a last-minute surface promotion where the prose was updated but the official examples were not re-checked,
- a source-lock-clean doc whose official examples are all real but old enough that the release should pause for review,
- or a release pass where the archive says “current official verification matters” but does not itself demonstrate any recent official verification for the surface being shipped.

## Release-gate rule

The release gate should reject the archive if any doc in the `special_case_high_risk` subfamily lacks at least two distinct official-public anchors with `retrieved` dates no more than 90 days older than the top release date in `CHANGELOG.md`.

That check should operate in addition to, not instead of:
- `scripts/check_voter_facing_special_case_authority_minimums.py`,
- `scripts/check_voter_facing_special_case_nonoverlap.py`,
- `scripts/check_voter_facing_special_case_fallback_escalation.py`, and
- `scripts/check_voter_facing_special_case_temporal_volatility.py`, and
- `scripts/check_voter_facing_special_case_official_routing_precedence.py`.

## Maintainer order of operations

When tightening or adding another high-risk special-case voter-facing surface adjacent to the `special_case_high_risk` cluster, maintainers should prefer this order:

1. decide whether the surface is actually distinct via `docs/310-*`,
2. wire the doc/template/checklist triplet and family registry via `docs/329-*` and `docs/330-*`,
3. prove repeated official-public grounding via `docs/331-*`,
4. make adjacent-surface non-overlap explicit via `docs/332-*`,
5. make the `305` / `307` lane switch explicit via `docs/333-*`,
6. make temporal volatility / no-cross-jurisdiction portability explicit via `docs/334-*`,
7. confirm that at least two official-public anchors for the surface were reviewed within the bounded release window defined here,
8. make the authority hierarchy explicit via `docs/345-*`, and then
9. make the current-state / superseding-notice discipline explicit via `docs/346-*`, and then
10. make the unresolved-conflict stop / no-synthesis rule explicit via `docs/347-*`, and then
11. confirm the doc still carries at least two direct jurisdiction-specific official-public governing examples via `docs/348-*`, and then
12. make the direct office-help route / contactability floor explicit via `docs/349-*`, and then
13. make the responsible-office specificity / jurisdiction-match floor explicit via `docs/350-*`.

That keeps the special-case cluster small, current, harder to ship in a stale-but-plausible state, and less likely to rely only on national routing material.

For the companion rule that the linked payload template's own `last_verified_at` must stay parseable, nonfuture, and still inside its declared `source_review_window_days` window relative to the release, see `docs/356-special-case-voter-facing-surface-payload-verification-timestamp-discipline-and-review-window-coherence.md`.

For the canonical ordered current control-stack map that keeps newer tail controls discoverable from anywhere in this maintainer subfamily, see `docs/355-special-case-voter-facing-surface-control-stack-reference-closure-and-navigation-firewall.md`.

## Sources (pinned IDs / lockfile IDs)

- EAC: Voter FAQs (xref: `eac_voter_faqs_page`)
- EAC: Register and Vote in Your State (xref: `eac_register_and_vote_in_your_state_page`)
- NASS: #TrustedInfo2026 (xref: `nass_trustedinfo_2026_page`)
