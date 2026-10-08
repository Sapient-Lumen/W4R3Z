# 361. Special-case voter-facing current-stack range-label inheritance and stale-perimeter firewall

**Track:** Shared / Public surfaces

## Why this exists (bounded)

The archive now has one canonical ordered current-stack map for the highest-risk voter-facing special-case controls in `docs/355-*`.

That already closes the larger navigation seams: bounded maintainer-control docs point back to the canonical map, overview docs inherit from it, the bounded recent backticked-citation checker inherits its scope from it, and the numbered high-risk surface docs themselves carry a compact pointer back to it.

A smaller but still real seam remained. Some current maintainer docs still spelled out the **current** special-case control perimeter with a hard-coded range label from an earlier revision. When a new tail control landed, those docs could keep the right pointer to `docs/355-*` and still carry a stale explicit range label in nearby prose. That is a small wording bug, but it is exactly the kind of stale perimeter cue that can mislead a maintainer skimming under time pressure.

For this subfamily, that matters because current official voter-information posture remains routing-first: EAC says the best source of practical registration and voting information is the local elections office, NASS's Can I Vote links directly to state election websites and trusted resources, NASS's `#TrustedInfo2026` campaign promotes state and local election officials as the trusted sources of election information, and Vote.gov emphasizes official `.gov` / HTTPS channels. The archive should not keep a live canonical map while nearby maintainer entrypoints quietly advertise an older current perimeter. (xref: `eac_voter_faqs_page`; xref: `nass_can_i_vote_page`; xref: `nass_trustedinfo_2026_page`; xref: `vote_gov_home_page`)

## What this adds (and what it does not)

This document adds one narrow rule: bounded maintainer docs that still spell out the **current** `special_case_high_risk` control tail by an explicit range label should keep that label synchronized with the canonical current-stack map in `docs/355-*`.

It does **not** require every doc to expose a range label at all. It does **not** replace:

- the canonical stack-reference page in `docs/355-*`,
- the overview-doc inheritance rule in `docs/358-*`,
- the bounded citation-scope inheritance rule in `docs/359-*`, or
- the surface-doc current-stack pointer rule in `docs/360-*`.

It only closes the smaller stale-perimeter seam where a doc can keep the right canonical pointer but still advertise yesterday's current range in surrounding prose.

## Bounded rule

For this bounded firewall:

- `docs/355-*` remains the source of truth for the current ordered special-case control stack,
- bounded maintainer docs may omit an explicit range label entirely and simply point to `docs/355-*`, but
- if they do spell out the current tail as a range, that explicit current range should match the live canonical perimeter.

At this revision, that live canonical perimeter is `344–361`.

## What this is meant to catch

This rule is meant to catch small but real maintenance failures such as:

- a doc like `docs/242-*` or `docs/START_HERE.md` still describing the current tail with a one-revision-old range label after later controls already landed,
- a release-gate doc or artifact-index note that keeps an older current-range label even while its neighboring pointers and checkers already moved forward,
- or a future release where the canonical map is current but several bounded entrypoints still teach one revision-old perimeter labels by habit.

## Mechanical check

The release gate should reject the archive if bounded current-entrypoint docs still carry an explicit `344–…` special-case current-tail range label that does not match the live canonical current-stack range derived from `docs/355-*`.

That check is implemented by:

- `scripts/_shared/special_case_control_stack.py`
- `scripts/check_voter_facing_special_case_current_stack_range_labels.py`
- `scripts/release_gate.py`

## Why this stays narrow

This is a **label-drift** firewall, not a new doctrine layer.
It adds one numbered doc plus one small checker and keeps the scope bounded to current maintainer entrypoints that still choose to spell out the current tail explicitly.

## Cross-references

- `docs/13-artifact-index.md`
- `docs/162-release-and-ci-evidence-pipeline.md`
- `docs/242-audience-reading-paths-and-what-to-ignore.md`
- `docs/355-special-case-voter-facing-surface-control-stack-reference-closure-and-navigation-firewall.md`
- `docs/358-special-case-voter-facing-surface-overview-doc-current-stack-inheritance-and-stale-summary-firewall.md`
- `docs/359-special-case-voter-facing-surface-backticked-lockfile-citation-scope-inheritance-and-stale-target-firewall.md`
- `docs/360-special-case-voter-facing-surface-doc-current-stack-pointer-and-stale-companion-list-firewall.md`
- `docs/START_HERE.md`
- `scripts/check_voter_facing_special_case_current_stack_range_labels.py`

## Sources (pinned IDs / lockfile IDs)

- EAC: Voter FAQs (xref: `eac_voter_faqs_page`)
- NASS: Can I Vote (xref: `nass_can_i_vote_page`)
- NASS: #TrustedInfo2026 (xref: `nass_trustedinfo_2026_page`)
- Vote.gov: Home / official secure-site marker (xref: `vote_gov_home_page`)
