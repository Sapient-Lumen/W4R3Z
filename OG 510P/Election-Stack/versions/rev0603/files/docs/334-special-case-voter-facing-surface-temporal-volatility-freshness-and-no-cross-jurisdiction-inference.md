# 334. Special-case voter-facing surface temporal-volatility, freshness, and no-cross-jurisdiction inference firewall

**Track:** Shared

This document is a compact companion to `docs/331-*`, `docs/332-*`, `docs/333-*`, `docs/345-*`, `docs/346-*`, and `docs/344-*` for the highest-risk voter-facing special-case cluster: the `special_case_high_risk` rows in `artifacts/tables/voter-facing-public-answer-surfaces.csv` (currently `317–328` and `335–343`).

`331` asks **"is this niche surface grounded in repeated official-public reality?"**

`332` asks **"does this doc say clearly what nearby numbered surfaces it is not?"**

`333` asks **"does this doc tell the reader when to leave the niche surface and switch to ordinary help or rights/safety escalation?"**

`334` asks **"does this doc also tell the reader that the rule is time-sensitive, jurisdiction-specific, and unsafe to port from another state, county, campus, jail, facility, or program without current official verification?"**

It exists because the `special_case_high_risk` subfamily — currently `317–328` and `335–343` — is unusually vulnerable to stale, overgeneralized, or cross-jurisdiction copying errors. That includes location-eligibility model pages, where one county’s vote-center rule or early-voting assignment exception can look deceptively portable to another jurisdiction. A surface can be distinct, well sourced, and non-overlapping, and still misroute a voter if it quietly encourages readers to treat one state’s edge-case rule as portable to another state or to trust an undated summary after the underlying official instructions changed.

It composes with:
- `docs/151-authoritative-sources-and-lockfile.md`
- `docs/191-external-source-lockfile-playbook.md`
- `docs/205-cache-and-freshness-controls-for-public-surfaces.md`
- `docs/310-voter-facing-public-answer-surfaces-family-map-and-promotion-rules.md`
- `docs/317-mail-ballot-replacement-spoilage-nonreceipt-and-surrender-fallback-as-evidence-surfaces.md`
- `docs/318-voter-registration-updates-address-name-party-and-move-close-to-election-notices-as-evidence-surfaces.md`
- `docs/319-voter-registration-inactive-removed-statuses-and-reactivation-notices-as-evidence-surfaces.md`
- `docs/320-vote-center-countywide-voting-and-assigned-location-rules-as-evidence-surfaces.md`
- `docs/321-provisional-ballot-issuance-reasons-partial-count-rules-and-voter-instructions-as-evidence-surfaces.md`
- `docs/329-voter-facing-public-answer-surface-registry-and-duplicate-firewall.md`
- `docs/330-voter-facing-public-answer-surface-triplet-coherence-and-orphan-control.md`
- `docs/331-special-case-voter-facing-surfaces-subfamily-and-authority-anchor-minimums.md`
- `docs/332-special-case-voter-facing-surface-nonoverlap-declarations-and-misrouting-firewall.md`
- `docs/333-special-case-voter-facing-surface-safe-fallback-and-escalation-boundaries.md`
- `docs/344-special-case-voter-facing-surface-release-freshness-floor-and-source-review-window.md`
- `docs/345-special-case-voter-facing-surface-authority-hierarchy-and-official-routing-precedence.md`
- `docs/346-special-case-voter-facing-surface-current-state-visibility-and-superseding-notice-discipline.md`
- `scripts/check_voter_facing_special_case_temporal_volatility.py`

## Rule

Every doc in the `special_case_high_risk` subfamily should contain a short section with an explicit heading that tells the reader all of the following:

1. the rule is **jurisdiction-specific** rather than nationally portable,
2. the rule is **time-sensitive** and can change across election windows or after later official updates,
3. the reader should **verify the current official state/local source** rather than rely on memory or a copied summary,
4. a **dated / last-updated / as-of** official source is preferable when available, and
5. a voter should **not infer** that another state, county, campus, jail, facility, or program follows the same rule unless the relevant authority says so now.

The point is not to turn each surface into a legal treatise.
The point is to make stale cross-jurisdiction copying mechanically harder.

## What this rule catches

This rule helps catch several quiet but dangerous failure modes:

- a conviction-rights page that cites official sources but never says restoration rules can change;
- a homelessness or student-residence page that quietly implies a dorm, shelter, or mailing workaround is portable across states;
- a custody or facility page that treats one institution’s ballot-handoff model as if it were a generic nationwide practice;
- or a confidential-registration page that is well anchored but fails to say that readers should prefer the current official instructions, especially when ordinary online registration is expressly disallowed.

## What this rule does not replace

This control does **not** replace:

- the family map and promotion rules in `docs/310-*`,
- the registry and duplicate firewall in `docs/329-*`,
- the triplet/orphan control in `docs/330-*`,
- the authority-anchor minimums in `docs/331-*`,
- the adjacent-surface non-overlap declarations in `docs/332-*`,
- or the safe fallback and escalation boundaries in `docs/333-*`,
- or the authority-hierarchy / official-routing-precedence rule in `docs/345-*`,
- or the current-state / superseding-notice discipline in `docs/346-*`,
- or the release-time freshness floor in `docs/344-*`.

It is a companion control for **temporal volatility and unsafe portability**, not a substitute for the other firewalls, including the unresolved-conflict stop / no-synthesis rule in `docs/347-*`, the direct-jurisdiction anchor floor in `docs/348-*`, the direct-help-route / contactability floor in `docs/349-*`, or the responsible-office specificity / jurisdiction-match floor in `docs/350-*`.

## Mechanical check

The release gate should reject the archive if any doc in the `special_case_high_risk` subfamily is missing a required temporal-volatility heading or fails to say, in substance, all of the following inside that section:

- verify the current **official** source,
- treat the rule as **jurisdiction-specific**,
- prefer a **dated / last-updated / as-of** official source when available,
- and do **not infer** that another state/county/jurisdiction automatically follows the same rule.

The checker for this is:

- `scripts/check_voter_facing_special_case_temporal_volatility.py`

## Maintainer posture

When tightening or adding another high-risk special-case voter-facing surface adjacent to the `special_case_high_risk` subfamily, maintainers should prefer this order:

1. prove distinctness in `docs/310-*`,
2. confirm triplet/registry wiring via `docs/329-*` and `docs/330-*`,
3. prove repeated official-public grounding via `docs/331-*`,
4. make adjacent-surface non-overlap explicit via `docs/332-*`,
5. make the safe default lane change explicit via `docs/333-*`,
6. make temporal volatility / freshness / no-cross-jurisdiction portability explicit via this document,
7. confirm bounded recent official-source review before release via `docs/344-*`,
8. make the authority hierarchy explicit via `docs/345-*`, and
9. make current-state / superseding-notice visibility explicit via `docs/346-*`, and then
10. make the unresolved-conflict stop / no-synthesis rule explicit via `docs/347-*`, and then
11. confirm the doc still carries at least two direct jurisdiction-specific official-public governing examples via `docs/348-*`, and then
12. make the direct office-help route / contactability floor explicit via `docs/349-*`, and then
13. make the responsible-office specificity / jurisdiction-match floor explicit via `docs/350-*`.

That keeps the special-case cluster small, grounded, and safer under stale-information pressure.
For the canonical ordered current control-stack map that keeps newer tail controls discoverable from anywhere in this maintainer subfamily, see `docs/355-special-case-voter-facing-surface-control-stack-reference-closure-and-navigation-firewall.md`.
