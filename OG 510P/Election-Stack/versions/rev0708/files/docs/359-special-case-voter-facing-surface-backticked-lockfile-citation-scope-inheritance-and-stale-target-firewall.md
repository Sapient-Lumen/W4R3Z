# 359. Special-case voter-facing surface backticked lockfile citation-scope inheritance and stale-target firewall

**Track:** Shared / Public surfaces

## Why this exists (bounded)

The archive now has a compact but meaningful `special_case_high_risk` control stack for the highest-risk voter-facing edge-case surfaces in `artifacts/tables/voter-facing-public-answer-surfaces.csv` (currently `317–328` and `335–343`).

That stack increasingly uses backticked `xref:` / `source:` lockfile citations in the numbered control docs and maintainer entrypoints because the syntax is more readable in dense control prose. A bounded release-gate checker already existed for those backticked citations, but it still depended on a hand-maintained target list. That meant the archive could evolve the canonical current stack in `docs/355-*` while the citation checker quietly continued inspecting an older perimeter.

For a control family built around current official routing, current-state visibility, superseding notices, unresolved-conflict stops, and release freshness, that is the wrong maintenance posture. The citation-coverage scope should move with the canonical current stack instead of lagging it.

## What this adds (and what it does not)

This document adds one narrow rule: the bounded release-gate checker for recent backticked external-source citations should derive the special-case control-doc portion of its scope from the canonical current-stack map in `docs/355-*` rather than from a frozen literal list.

It does **not** turn the recent citation checker into an archive-wide linter. It does **not** replace:

- the canonical stack-reference page in `docs/355-*`,
- the overview-doc inheritance rule in `docs/358-*`,
- the archive-wide lockfile hygiene checker in `scripts/check_external_sources_lockfile.py`, or
- the special-case control-doc reference-closure checker in `scripts/check_voter_facing_special_case_control_stack_reference_closure.py`.

It only closes the stale-target seam where the newest current-stack docs could fall outside bounded backticked-citation coverage even though the rest of the archive already treated them as part of the live control perimeter.

## Bounded rule

For this bounded firewall:

- `docs/355-*` remains the canonical current-stack map for the later `special_case_high_risk` control tail,
- the recent backticked-citation checker should inherit the control-doc target set from that canonical map, and
- the canonical-map closure checker should continue proving that the canonical map itself names the actual current stack rather than a stale subset.

That means future additions to the current `344–361` tail should not require a second hand-edited target list just to bring the new doc under backticked-citation coverage.

## What this is meant to catch

This rule is meant to catch small but real maintenance failures such as:

- the canonical current stack advancing while `scripts/check_recent_backticked_lockfile_citations.py` still inspects an older hand-maintained doc-id set,
- a control doc such as `docs/354-*` or a later tail doc carrying lockfile-looking backticked citations without actually being inside the bounded release-gate scope,
- or a release where the canonical control perimeter is current but the citation-coverage perimeter is one revision behind.

## Mechanical effect

The release gate should treat `docs/355-*` as the source of truth for the current special-case control-stack scope used by the bounded recent backticked-citation checker, while separately checking that `docs/355-*` itself stays aligned with the actual current `special-case-voter-facing-surface-*` control docs.

This is implemented by:

- `scripts/_shared/special_case_control_stack.py`
- `scripts/check_recent_backticked_lockfile_citations.py`
- `scripts/check_voter_facing_special_case_control_stack_reference_closure.py`
- `docs/361-special-case-voter-facing-surface-current-stack-range-label-inheritance-and-stale-perimeter-firewall.md`
- `scripts/check_voter_facing_special_case_overview_stack_inheritance.py`

## Why this stays narrow

This is a release-gate scope-inheritance fix, not a new voter-facing doctrine layer. It adds one numbered doc and one small shared helper, and it reduces future maintenance drift by making multiple checkers consume the same canonical current-stack map instead of retyping their own tail lists.

## Cross-references

- `docs/162-release-and-ci-evidence-pipeline.md`
- `docs/242-audience-reading-paths-and-what-to-ignore.md`
- `docs/330-voter-facing-public-answer-surface-triplet-coherence-and-orphan-control.md`
- `docs/355-special-case-voter-facing-surface-control-stack-reference-closure-and-navigation-firewall.md`
- `docs/358-special-case-voter-facing-surface-overview-doc-current-stack-inheritance-and-stale-summary-firewall.md`
- `scripts/check_external_sources_lockfile.py`
- `scripts/check_recent_backticked_lockfile_citations.py`
- `scripts/check_voter_facing_special_case_control_stack_reference_closure.py`
- `docs/361-special-case-voter-facing-surface-current-stack-range-label-inheritance-and-stale-perimeter-firewall.md`
- `scripts/check_voter_facing_special_case_overview_stack_inheritance.py`

## Sources (pinned IDs / lockfile IDs)

- EAC: Voter FAQs (xref: `eac_voter_faqs_page`)
- EAC: Register and Vote in Your State (xref: `eac_register_and_vote_in_your_state_page`)
- NASS: Can I Vote (xref: `nass_can_i_vote_page`)
- NASS: #TrustedInfo2026 (xref: `nass_trustedinfo_2026_page`)
- Vote.gov: Home / official secure-site marker (xref: `vote_gov_home_page`)
