# 352. Special-case voter-facing surface operability-now and deadline-imminence floor

**Track:** Shared

This document is a compact companion to `docs/331-*`, `docs/332-*`, `docs/333-*`, `docs/334-*`, `docs/344-*`, `docs/345-*`, `docs/346-*`, `docs/347-*`, `docs/348-*`, `docs/349-*`, `docs/350-*`, and `docs/351-*` for the highest-risk voter-facing special-case cluster: the `special_case_high_risk` rows in `artifacts/tables/voter-facing-public-answer-surfaces.csv` (currently `317–328` and `335–343`).

It exists to answer one bounded maintainer question:

**“Even when a high-risk voter-facing edge-case surface names the right office, help path, and secure channel, does it also say whether that path is still usable right now under same-day or near-deadline conditions?”**

## Why this exists (bounded)

The archive already does twelve important things for the `special_case_high_risk` subfamily:

1. requires repeated official-public grounding (`docs/331-*`),
2. requires explicit adjacent-surface non-overlap (`docs/332-*`),
3. requires safe fallback / escalation boundaries (`docs/333-*`),
4. requires an explicit statement that the rule is jurisdiction-specific, time-sensitive, and unsafe to port without current verification (`docs/334-*`),
5. requires a bounded recent review of official-public examples before release (`docs/344-*`),
6. requires an explicit statement that the current official state/local election-office source controls over national/archive summaries (`docs/345-*`),
7. requires an explicit statement telling the reader how to identify the current controlling official notice or instruction when older material remains visible (`docs/346-*`),
8. requires an explicit unresolved-conflict stop / no-synthesis / office-confirmation rule (`docs/347-*`),
9. requires at least two direct jurisdiction-specific official-public governing examples rather than only national routing pages or generalized official explainers (`docs/348-*`),
10. requires a concrete official help/contact path instead of abstract advice to “contact the office” (`docs/349-*`),
11. requires the public answer to identify which official office role actually owns the case (`docs/350-*`), and
12. requires the public answer to say how to reach that office through an official secure path without oversharing sensitive records (`docs/351-*`).

That still leaves one quiet last-mile failure mode.

A doc can satisfy all twelve and still fail the voter at the exact moment of need if it names the correct office and channel but never says whether that path is still operable *right now*. The highest-risk edge-case surfaces are the ones most likely to collide with same-day cutoffs, final office-hours windows, office closings, holiday schedules, bad-weather or disaster disruption, facility access changes, emergency courier windows, portal outages, or other operational changes that invalidate yesterday’s “correct” route. Current official public routing supports making that explicit. EAC’s voter FAQ says election administration in the United States is highly decentralized and that the best source of practical registration and voting information is the local elections office. Vote.gov says registration deadlines vary by state and territory and routes voters to current state-specific official pages. NASS’s `Can I Vote` says it links directly to state election websites and trusted resources rather than serving as the final operational endpoint. EAC’s disaster-recovery voter guidance likewise points readers back to current state/local election information because disaster conditions can change the practical path quickly. (xref: `eac_voter_faqs_page`; xref: `vote_gov_register_page`; xref: `nass_can_i_vote_page`; xref: `eac_disaster_recovery_response_page`; xref: `eac_register_and_vote_in_your_state_page`)

## What this adds (and what it does not)

This document adds a compact **operability-now and deadline-imminence floor** for docs in the `special_case_high_risk` subfamily.

It does **not** replace:
- the authority-anchor minimums from `docs/331-*`,
- the explicit non-overlap rules from `docs/332-*`,
- the fallback / escalation boundaries from `docs/333-*`,
- the temporal-volatility and no-cross-jurisdiction rule from `docs/334-*`,
- the release-freshness floor from `docs/344-*`,
- the authority-hierarchy rule from `docs/345-*`,
- the current-state / superseding-notice rule from `docs/346-*`,
- the unresolved-conflict stop from `docs/347-*`,
- the direct-jurisdiction anchor floor from `docs/348-*`,
- the concrete help-route floor from `docs/349-*`,
- the responsible-office specificity floor from `docs/350-*`, or
- the official secure-channel / minimum-disclosure floor from `docs/351-*`.

It adds one narrower question on top of them:

**When the voter is same-day, deadline-near, or already inside the final office-hours window, does the public answer tell them how to confirm that the nominal path is still live right now and what to do if it is not?**

## Maintainer rule

For rows tagged `special_case_high_risk` in `artifacts/tables/voter-facing-public-answer-surfaces.csv`, each public-answer doc must carry a dedicated section with the exact heading:

`## Operability-now, live availability, and deadline-imminence floor`

That section must say, in substance:

1. **Live availability matters.**  
   The reader must be told to verify that the responsible office, portal, site, delivery window, or other named official path is still open and operating right now when the issue is same-day, deadline-near, or already inside the final office-hours window.

2. **Current notice beats stale summary.**  
   The reader must be warned not to assume that an older FAQ, calendar, PDF, screenshot, packet insert, cached office-hours page, or generalized directory still reflects today’s office-closing time, holiday closure, bad-weather or disaster disruption, facility-access restriction, portal outage, staffing limitation, or emergency procedural change.

3. **The public artifact must carry explicit operability notes.**  
   The payload must keep both `operability_now_note` and `deadline_imminence_note` populated so the artifact states:
   - how to confirm current live availability, and
   - what immediate fallback, next-step, or confirmation rule applies if the original path is no longer operable or the cutoff may already have passed.

4. **Lane discipline still applies.**  
   Preserve `305` for ordinary office-hours, live-availability, and closure-status confirmation. Preserve `307` when the disruption itself has become a rights/safety problem, likely wrongful denial, intimidation/coercion issue, discriminatory access failure, or another formal escalation case.

## Release-gate expectation

The release gate should reject the archive if any current `special_case_high_risk` surface doc fails to:
- carry the exact required heading,
- say the reader should verify that the path is open and operating right now under same-day or deadline-near conditions,
- warn against relying on stale hours/closure/cached-summary material,
- preserve `305` and `307` lane discipline, or
- reference the payload fields `operability_now_note` and `deadline_imminence_note`.

The corresponding check is:

- `scripts/check_voter_facing_special_case_operability_now.py`

and it should run as part of:

- `scripts/release_gate.py`

## Why this stays narrow

This does **not** require the archive to become a live status board, scraper, or nationwide office-hours cache.
It only requires the highest-risk niche edge-case pages to say plainly that:
- the nominally correct path may no longer be usable right now,
- same-day and near-cutoff readers must verify operability using the latest official local signal,
- stale visible material is not enough, and
- fallback / escalation discipline still applies when the live path is gone.

That is a bounded integrity rule, not a new product surface.

## Minimal examples maintainers should look for

Good signals in the public answer include short phrases such as:
- “verify that the office or portal is open and operating right now using the latest official hours/closure notice or verified office phone,”
- “do not rely on an older PDF, cached hours page, or generic directory when the cutoff is same-day or near,”
- “if the path is no longer operable or the cutoff may already have passed, use the stated fallback or immediate office-confirmation path,” and
- “move to `307` when the disruption itself has become likely wrongful denial, unsafe exposure, or another rights/safety problem.”

## Cross-references

- `docs/305-election-office-contact-directories-office-hours-and-change-notices-as-evidence-surfaces.md`
- `docs/307-voting-issue-reporting-civil-rights-escalation-and-change-notices-as-evidence-surfaces.md`
- `docs/331-special-case-voter-facing-surfaces-subfamily-and-authority-anchor-minimums.md`
- `docs/333-special-case-voter-facing-surface-safe-fallback-and-escalation-boundaries.md`
- `docs/344-special-case-voter-facing-surface-release-freshness-floor-and-source-review-window.md`
- `docs/346-special-case-voter-facing-surface-current-state-visibility-and-superseding-notice-discipline.md`
- `docs/349-special-case-voter-facing-surface-direct-help-route-and-contactability-floor.md`
- `docs/350-special-case-voter-facing-surface-responsible-office-specificity-and-jurisdiction-match-floor.md`
- `docs/351-special-case-voter-facing-surface-official-secure-channel-and-minimum-disclosure-floor.md`
- `scripts/check_voter_facing_special_case_operability_now.py`
For the canonical ordered current control-stack map that keeps newer tail controls discoverable from anywhere in this maintainer subfamily, see `docs/355-special-case-voter-facing-surface-control-stack-reference-closure-and-navigation-firewall.md`.
