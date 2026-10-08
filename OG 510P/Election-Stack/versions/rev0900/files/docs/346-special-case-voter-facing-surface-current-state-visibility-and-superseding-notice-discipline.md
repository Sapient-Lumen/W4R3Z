# 346. Special-case voter-facing surface current-state visibility and superseding-notice discipline

**Track:** Shared

This document is a compact companion to `docs/331-*`, `docs/332-*`, `docs/333-*`, `docs/334-*`, `docs/344-*`, and `docs/345-*` for the highest-risk voter-facing special-case cluster: the `special_case_high_risk` rows in `artifacts/tables/voter-facing-public-answer-surfaces.csv` (currently `317–328` and `335–343`).

It exists to answer one bounded maintainer question:

**“Even when a high-risk voter-facing edge-case surface is well-anchored, freshness-checked, and explicit about authority, does it also tell the reader how to identify which notice or instruction currently controls when older material is still visible?”**

## Why this exists (bounded)

The archive already does six important things for the `special_case_high_risk` subfamily:

1. requires repeated official-public grounding (`docs/331-*`),
2. requires explicit adjacent-surface non-overlap (`docs/332-*`),
3. requires safe fallback / escalation boundaries (`docs/333-*`),
4. requires an explicit statement that the rule is jurisdiction-specific, time-sensitive, and unsafe to port without current verification (`docs/334-*`),
5. requires a bounded recent review of official-public examples before release (`docs/344-*`), and
6. requires an explicit statement that the current official state/local election-office source controls over national/archive summaries (`docs/345-*`).

That is necessary, but still leaves one quiet failure mode.

A doc can satisfy all six and still mislead if it never says how to resolve the very common public-information state where **older PDFs, screenshots, mirrored pages, packet inserts, or earlier office notices remain visible after a newer official instruction changed the controlling answer**. That matters especially in the highest-risk edge-case cluster because these are the surfaces where a voter often acts under stress: replacement-ballot routing, late move/update questions, custody/facility rules, challenged-voter paths, bearer/agent constraints, disaster relocation, youth timing rules, and similar edge conditions.

The archive already has a general correction/supersession model for signed public notices in `docs/219-*` and `docs/220-*`. This document does not replace that model. It adds one compact reader-facing requirement for the highest-risk voter surfaces: **make it obvious which current notice, form edition, packet instruction, or office page currently controls when stale material still exists in public.**

Current official voter-information routing supports this discipline. EAC's voter FAQ says election administration is highly decentralized and that the best practical source of voting information is the local elections office. EAC's state-routing page and Vote.gov's registration/update flow route voters to current state and local election-office sources rather than one fixed national rule page, and NASS's current `Can I Vote` / `#TrustedInfo2026` posture likewise directs the public to state and local election officials' resources. When that is the public routing model, a high-risk edge-case doc should also tell the reader how to recognize the latest controlling official instruction when multiple public artifacts still circulate. (xref: `eac_voter_faqs_page`; xref: `eac_register_and_vote_in_your_state_page`; xref: `vote_gov_register_page`; xref: `nass_can_i_vote_page`; xref: `nass_trustedinfo_2026_page`)

## What this adds (and what it does not)

This document adds a compact **current-state visibility / superseding-notice discipline** rule for docs in the `special_case_high_risk` subfamily.

It does **not** replace:
- the official-anchor count minimum in `docs/331-*`,
- the explicit adjacent-surface declarations required by `docs/332-*`,
- the fallback / escalation boundary required by `docs/333-*`,
- the temporal-volatility / no-cross-jurisdiction warning required by `docs/334-*`,
- the release-date freshness floor in `docs/344-*`,
- the authority-hierarchy rule in `docs/345-*`, or
- the more general `PublicNotice` correction/supersession machinery in `docs/219-*` and `docs/220-*`.

It is only a compact prose-control rule: a way to stop a high-risk niche voter surface from acting as though the reader can safely infer the "current answer" without being told how to spot the current controlling notice among visible older material. It does not authorize the archive to synthesize an answer when the official materials remain unresolved; that is the narrower job of `docs/347-*`. The archive also still needs the direct-jurisdiction anchor floor from `docs/348-*`, the direct-help-route / contactability floor from `docs/349-*`, and the responsible-office specificity / jurisdiction-match floor from `docs/350-*`.

## Current-state visibility floor

For each doc whose row in `artifacts/tables/voter-facing-public-answer-surfaces.csv` is tagged `special_case_high_risk`, the doc should contain a dedicated section that says, in substance, all of the following:

1. older official-public material may remain visible after the answer changed (for example: an older PDF, packet insert, FAQ page, screenshot, mirrored page, or office notice),
2. the public answer should identify which **current official** notice, form edition, packet instruction, advisory, or office page currently controls,
3. if a newer official item **supersedes, corrects, updates, amends, or replaces** an older one, the reader should follow the newer controlling item,
4. where available, the reader should look for the dated / effective / last-updated / as-of marker that helps identify the current controlling item, and
5. stale screenshots, archived summaries, and older public artifacts should not be treated as controlling if a newer directly governing official instruction exists.

The point is not to require one perfect metadata pattern across every jurisdiction. It is to make the doc say plainly how a voter or helper should distinguish the current controlling official instruction from older public material that may still be discoverable.

## What this is meant to catch

This check is intentionally narrow. It is meant to catch bounded but meaningful failures such as:

- a disaster-relocation page that correctly says "check your local office" but never says how to tell whether a newer evacuation advisory or replacement-ballot notice displaced an older instruction,
- a custody or facility page that names the controlling office but leaves the reader guessing whether the facility handout, the county page, or a later registrar notice currently governs,
- a challenged-voter or bearer/agent page that explains the edge case well but never says to follow the newer official correction or updated form if older instructions remain online,
- or a high-risk special-case doc that correctly names the controlling authority yet still reads as though stale screenshots or mirrored PDFs are safe substitutes for the latest official public instruction.

## Mechanical check

The release gate should reject the archive if any doc in the `special_case_high_risk` subfamily is missing a required current-state heading or fails to say, in substance, all of the following inside that section:

- older public material may remain visible,
- the **current official** notice / form / instruction currently controls,
- a newer official item that **supersedes / corrects / updates / replaces** an older one should be followed,
- the reader should use the dated / effective / last-updated cue when available, and
- stale screenshots / archived summaries / older artifacts are not safe substitutes for the newer directly governing official source.

The checker for this is:

- `scripts/check_voter_facing_special_case_current_state_visibility.py`

## Maintainer order of operations

When tightening or adding another high-risk special-case voter-facing surface adjacent to the `special_case_high_risk` cluster, maintainers should prefer this order:

1. decide whether the surface is actually distinct via `docs/310-*`,
2. wire the doc/template/checklist triplet and family registry via `docs/329-*` and `docs/330-*`,
3. prove repeated official-public grounding via `docs/331-*`,
4. make adjacent-surface non-overlap explicit via `docs/332-*`,
5. make the `305` / `307` lane switch explicit via `docs/333-*`,
6. make temporal volatility / no-cross-jurisdiction portability explicit via `docs/334-*`,
7. confirm bounded recent official-source review before release via `docs/344-*`,
8. make the authority hierarchy explicit via `docs/345-*`, and then
9. make the current-state / superseding-notice discipline explicit via this document, and then
10. make the unresolved-conflict stop / no-synthesis / office-confirmation rule explicit via `docs/347-*`, and then
11. confirm the doc still carries at least two direct jurisdiction-specific official-public governing examples via `docs/348-*`, and then
12. make the direct office-help route / contactability floor explicit via `docs/349-*`, and then
13. make the responsible-office specificity / jurisdiction-match floor explicit via `docs/350-*`.

That keeps the special-case cluster small, current, and clearer about which visible public artifact actually controls when a voter must act.

For the canonical ordered current control-stack map that keeps newer tail controls discoverable from anywhere in this maintainer subfamily, see `docs/355-special-case-voter-facing-surface-control-stack-reference-closure-and-navigation-firewall.md`.

## Sources (pinned IDs / lockfile IDs)

- EAC: Voter FAQs (xref: `eac_voter_faqs_page`)
- EAC: Register and Vote in Your State (xref: `eac_register_and_vote_in_your_state_page`)
- Vote.gov: Register to vote / update registration (xref: `vote_gov_register_page`)
- NASS: Can I Vote (xref: `nass_can_i_vote_page`)
- NASS: #TrustedInfo2026 (xref: `nass_trustedinfo_2026_page`)
