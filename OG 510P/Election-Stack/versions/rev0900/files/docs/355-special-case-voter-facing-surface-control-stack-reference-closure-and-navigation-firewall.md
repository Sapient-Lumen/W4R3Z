# 355. Special-case voter-facing surface control-stack reference closure and navigation firewall

**Track:** Shared / Public surfaces

## Why this exists (bounded)

The archive now has a substantial but still intentionally compact `special_case_high_risk` control stack for the highest-risk voter-facing edge-case surfaces in `artifacts/tables/voter-facing-public-answer-surfaces.csv` (currently `317–328` and `335–343`).

That stack has grown in a disciplined way across `docs/344-*` through `docs/361-*`, including newer secure-channel, operability, propagation, payload-timestamp-discipline, checklist-backstop, overview-inheritance, citation-scope-inheritance, surface-doc current-stack-pointer, and current-range-label-inheritance controls.

A narrow maintenance seam still remains even when the release gate passes: older control docs can keep their own substantive rule while quietly falling out of date as **navigation surfaces** for the rest of the current stack. A maintainer reading one control doc can then miss newer companion controls even though those later controls exist and are enforced elsewhere.

## What this adds (and what it does not)

This document adds a compact **control-stack reference-closure** rule for the special-case high-risk maintainer-control docs.

It does **not** add a new voter-facing doctrine layer. It does **not** replace:

- the bounded surface-family map in `docs/310-*`,
- the family registry / duplicate / triplet firewalls in `docs/329-*` and `docs/330-*`,
- the high-risk authority / non-overlap / fallback / temporal-volatility controls in `docs/331-*` through `docs/334-*`,
- the release-freshness / authority-hierarchy / current-state / unresolved-conflict controls in `docs/344-*` through `docs/347-*`,
- the direct-jurisdiction / contactability / office-specificity / secure-channel / operability controls in `docs/348-*` through `docs/352-*`, or
- the two propagation firewalls in `docs/353-*` and `docs/354-*`,
- the payload verification-timestamp discipline and review-window coherence rule in `docs/356-*`,
- the boundary/portability checklist backstop in `docs/357-*`, or
- the overview-doc current-stack inheritance and stale-summary firewall in `docs/358-*`, or
- the backticked lockfile citation-scope inheritance and stale-target firewall in `docs/359-*`, or
- the surface-doc current-stack pointer and stale-companion-list firewall in `docs/360-*`, or
- the current-stack range-label inheritance and stale-perimeter firewall in `docs/361-*`.

It only says that the current maintainer-control docs for this high-risk stack must keep a live pointer to a single canonical navigation page so the newest controls do not become discoverable only from top-level entrypoints or release-gate code.
That canonical navigation page is this document itself: `docs/355-special-case-voter-facing-surface-control-stack-reference-closure-and-navigation-firewall.md`.

## Canonical current control stack

As of this revision, the current ordered special-case high-risk control stack is:

1. `docs/344-special-case-voter-facing-surface-release-freshness-floor-and-source-review-window.md`
2. `docs/345-special-case-voter-facing-surface-authority-hierarchy-and-official-routing-precedence.md`
3. `docs/346-special-case-voter-facing-surface-current-state-visibility-and-superseding-notice-discipline.md`
4. `docs/347-special-case-voter-facing-surface-unresolved-conflict-stop-and-no-synthesis-rule.md`
5. `docs/348-special-case-voter-facing-surface-direct-jurisdiction-anchor-floor-and-national-routing-nonsubstitution.md`
6. `docs/349-special-case-voter-facing-surface-direct-help-route-and-contactability-floor.md`
7. `docs/350-special-case-voter-facing-surface-responsible-office-specificity-and-jurisdiction-match-floor.md`
8. `docs/351-special-case-voter-facing-surface-official-secure-channel-and-minimum-disclosure-floor.md`
9. `docs/352-special-case-voter-facing-surface-operability-now-and-deadline-imminence-floor.md`
10. `docs/353-special-case-voter-facing-surface-triplet-propagation-and-doc-only-drift-firewall.md`
11. `docs/354-special-case-voter-facing-surface-freshness-current-state-and-conflict-field-propagation.md`
12. `docs/355-special-case-voter-facing-surface-control-stack-reference-closure-and-navigation-firewall.md`
13. `docs/356-special-case-voter-facing-surface-payload-verification-timestamp-discipline-and-review-window-coherence.md`
14. `docs/357-special-case-voter-facing-surface-boundary-portability-checklist-backstop.md`
15. `docs/358-special-case-voter-facing-surface-overview-doc-current-stack-inheritance-and-stale-summary-firewall.md`
16. `docs/359-special-case-voter-facing-surface-backticked-lockfile-citation-scope-inheritance-and-stale-target-firewall.md`
17. `docs/360-special-case-voter-facing-surface-doc-current-stack-pointer-and-stale-companion-list-firewall.md`
18. `docs/361-special-case-voter-facing-surface-current-stack-range-label-inheritance-and-stale-perimeter-firewall.md`

The point of this ordered list is not ceremonial numbering.
It is to give maintainers one bounded place to re-find the **current** control perimeter when older companion docs were written before the newest tail controls existed.

## Closure rule

The current maintainer-control docs for this stack should preserve an explicit pointer to this document so that a reader entering anywhere in the control family can reach the canonical current-stack list without needing to reconstruct it from changelog archaeology or release-gate code.

For this bounded firewall, the release gate should cover:

- `docs/330-*`,
- `docs/331-*`,
- `docs/332-*`,
- `docs/333-*`,
- `docs/334-*`, and
- `docs/344-*` through `docs/361-*`.

## What this is meant to catch

This rule is meant to catch small but real maintenance failures such as:

- a control doc that still reads correctly in isolation but no longer points maintainers toward the newer secure-channel / operability / propagation controls,
- a future edit that preserves top-level entrypoints while an older companion doc quietly becomes a stale map of the stack,
- or a release where the numbered controls still exist and pass their own checkers, but the control family becomes harder to navigate under time pressure because newer tail controls are discoverable only from `README.md`, `docs/START_HERE.md`, or `scripts/release_gate.py`.

## Mechanical check

The release gate should reject the archive if any covered special-case maintainer-control doc no longer carries a pointer to this canonical stack-reference page, or if this page stops naming the current `344–361` ordered stack in the canonical stack section itself.

That check is implemented by:

- `scripts/check_voter_facing_special_case_control_stack_reference_closure.py`
- `scripts/release_gate.py`

## Why this stays narrow

This is a **navigation and maintainability** firewall, not a new source, payload, or doctrinal burden.
It adds one numbered doc plus one checker, and it lets the older control docs stay compact by pointing to a canonical current-stack map instead of repeating the full tail of the control family everywhere.

## Cross-references

- `docs/330-voter-facing-public-answer-surface-triplet-coherence-and-orphan-control.md`
- `docs/331-special-case-voter-facing-surfaces-subfamily-and-authority-anchor-minimums.md`
- `docs/332-special-case-voter-facing-surface-nonoverlap-declarations-and-misrouting-firewall.md`
- `docs/333-special-case-voter-facing-surface-safe-fallback-and-escalation-boundaries.md`
- `docs/334-special-case-voter-facing-surface-temporal-volatility-freshness-and-no-cross-jurisdiction-inference.md`
- `docs/344-special-case-voter-facing-surface-release-freshness-floor-and-source-review-window.md`
- `docs/345-special-case-voter-facing-surface-authority-hierarchy-and-official-routing-precedence.md`
- `docs/346-special-case-voter-facing-surface-current-state-visibility-and-superseding-notice-discipline.md`
- `docs/347-special-case-voter-facing-surface-unresolved-conflict-stop-and-no-synthesis-rule.md`
- `docs/348-special-case-voter-facing-surface-direct-jurisdiction-anchor-floor-and-national-routing-nonsubstitution.md`
- `docs/349-special-case-voter-facing-surface-direct-help-route-and-contactability-floor.md`
- `docs/350-special-case-voter-facing-surface-responsible-office-specificity-and-jurisdiction-match-floor.md`
- `docs/351-special-case-voter-facing-surface-official-secure-channel-and-minimum-disclosure-floor.md`
- `docs/352-special-case-voter-facing-surface-operability-now-and-deadline-imminence-floor.md`
- `docs/353-special-case-voter-facing-surface-triplet-propagation-and-doc-only-drift-firewall.md`
- `docs/354-special-case-voter-facing-surface-freshness-current-state-and-conflict-field-propagation.md`
- `docs/356-special-case-voter-facing-surface-payload-verification-timestamp-discipline-and-review-window-coherence.md`
- `docs/357-special-case-voter-facing-surface-boundary-portability-checklist-backstop.md`
- `docs/358-special-case-voter-facing-surface-overview-doc-current-stack-inheritance-and-stale-summary-firewall.md`
- `docs/359-special-case-voter-facing-surface-backticked-lockfile-citation-scope-inheritance-and-stale-target-firewall.md`
- `docs/360-special-case-voter-facing-surface-doc-current-stack-pointer-and-stale-companion-list-firewall.md`
- `docs/361-special-case-voter-facing-surface-current-stack-range-label-inheritance-and-stale-perimeter-firewall.md`
- `scripts/check_voter_facing_special_case_control_stack_reference_closure.py`

## Sources (pinned IDs / lockfile IDs)

- EAC: Voter FAQs (xref: `eac_voter_faqs_page`)
- EAC: Best Practices: FAQs for Election Officials (xref: `eac_best_practices_faqs_election_officials_page`)
- EAC: Register and Vote in Your State (xref: `eac_register_and_vote_in_your_state_page`)
- NASS: Can I Vote (xref: `nass_can_i_vote_page`)
- NASS: #TrustedInfo2026 (xref: `nass_trustedinfo_2026_page`)
- Vote.gov: Register to vote / update registration (xref: `vote_gov_register_page`)
- Vote.gov: Home / official secure-site marker (xref: `vote_gov_home_page`)
