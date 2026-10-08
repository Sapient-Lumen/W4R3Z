# 357. Special-case voter-facing surface boundary/portability checklist backstop

**Track:** Shared / Public surfaces

## Why this exists (bounded)

The archive already has compact numbered controls for the highest-risk voter-facing special-case rows tagged `special_case_high_risk` in `artifacts/tables/voter-facing-public-answer-surfaces.csv` (currently `317–328` and `335–343`) requiring:

- explicit adjacent-surface non-overlap declarations in `docs/332-*`,
- explicit safe fallback / escalation boundaries in `docs/333-*`, and
- explicit temporal-volatility / freshness / no-cross-jurisdiction warnings in `docs/334-*`.

The archive also now propagates later high-risk controls into the linked triplet via `docs/353-*`, `docs/354-*`, and `docs/356-*`.

That still leaves one narrow operator-workflow seam.
A maintainer can start from the linked checklist and still miss the earlier boundary controls that live mainly in the numbered doc: which adjacent surfaces this page must not absorb, when the case has moved into `305` ordinary-help confirmation or `307` rights/safety escalation, and why another state's, county's, facility's, or older notice's answer is not portable here.

For this subfamily, that matters because current official voter-information posture remains routing-based. EAC says the best source of practical registration and voting information is the local elections office; NASS's Can I Vote links directly to state election websites and trusted resources; and Vote.gov emphasizes official `.gov` / HTTPS channels and sharing sensitive information only on official secure sites. A checklist that preserves the later payload fields but forgets the earlier scope and portability boundaries can still push maintainers toward an unsafe high-risk artifact under deadline pressure. (xref: `eac_voter_faqs_page`; xref: `nass_can_i_vote_page`; xref: `vote_gov_home_page`)

## What this adds (and what it does not)

This document adds a compact **checklist boundary/portability backstop** for the `special_case_high_risk` subfamily.

It does **not** replace:

- the numbered-doc non-overlap rule in `docs/332-*`,
- the numbered-doc safe fallback / escalation rule in `docs/333-*`,
- the numbered-doc temporal-volatility / no-cross-jurisdiction rule in `docs/334-*`,
- the later routing/control checklist propagation rule in `docs/353-*`,
- the later freshness/current-state/conflict checklist propagation rule in `docs/354-*`, or
- the payload verification-timestamp discipline in `docs/356-*`.

It only says that the linked high-risk operator checklist should carry one compact section that keeps the earlier **scope boundary + portability** controls visible in the workflow maintainers actually use.

## Checklist backstop floor

For each row tagged `special_case_high_risk`, the linked checklist should preserve, in substance, all of the following:

1. at least two adjacent numbered-surface references drawn from the numbered doc's non-overlap section,
2. a reminder that when the case has moved beyond this page's bounded niche, `305` remains the ordinary-help / current-office confirmation lane and `307` remains the rights/safety escalation lane, and
3. a reminder to verify the current official source, prefer dated / last-updated material, and avoid cross-jurisdiction or cross-facility portability by analogy.

The point is not to turn every checklist into a second essay.
The point is to keep the maintainer's operational skeleton honest about **what this surface is not**, **when to change lanes**, and **why another jurisdiction's answer is not safely portable**.

## What this is meant to catch

This checklist backstop is meant to catch bounded failures such as:

- a high-risk surface whose numbered doc still distinguishes adjacent surfaces while the linked checklist no longer reminds the maintainer where those boundaries are,
- a checklist that preserves the later contactability and review-window fields but forgets to say when the question should move to `305` or `307`,
- a checklist that sounds current but no longer reminds the maintainer to prefer the current dated official notice,
- a checklist that quietly nudges maintainers to reuse a neighboring county/state/facility pattern by analogy, or
- a future cleanup that keeps the numbered control docs intact while letting the earlier non-overlap / boundary / no-portability rules disappear from the operator workflow.

## Mechanical check

The release gate should reject the archive if any current `special_case_high_risk` checklist is missing the dedicated boundary/portability section, fails to echo at least two adjacent numbered-surface refs from the linked numbered doc, or omits the `305` / `307` / current-official / no-cross-jurisdiction backstop language.

That check is implemented by:

- `scripts/check_voter_facing_special_case_boundary_portability_checklists.py`
- `scripts/release_gate.py`

## Why this stays narrow

This is a **checklist-workflow integrity** control, not a new payload schema.
It adds one numbered doc plus one checker and backfills one short checklist section across the current `special_case_high_risk` rows.

If the archive later reshapes or removes this bounded high-risk subfamily, this checklist backstop can disappear with the same boundedness as the rest of the `330–357` maintainer-control family.

## Cross-references

- `docs/330-voter-facing-public-answer-surface-triplet-coherence-and-orphan-control.md`
- `docs/332-special-case-voter-facing-surface-nonoverlap-declarations-and-misrouting-firewall.md`
- `docs/333-special-case-voter-facing-surface-safe-fallback-and-escalation-boundaries.md`
- `docs/334-special-case-voter-facing-surface-temporal-volatility-freshness-and-no-cross-jurisdiction-inference.md`
- `docs/353-special-case-voter-facing-surface-triplet-propagation-and-doc-only-drift-firewall.md`
- `docs/354-special-case-voter-facing-surface-freshness-current-state-and-conflict-field-propagation.md`
- `docs/355-special-case-voter-facing-surface-control-stack-reference-closure-and-navigation-firewall.md`
- `docs/356-special-case-voter-facing-surface-payload-verification-timestamp-discipline-and-review-window-coherence.md`
- `scripts/check_voter_facing_special_case_boundary_portability_checklists.py`

For the canonical ordered current control-stack map that keeps newer tail controls discoverable from anywhere in this maintainer subfamily, see `docs/355-special-case-voter-facing-surface-control-stack-reference-closure-and-navigation-firewall.md`.

## Sources (pinned IDs / lockfile IDs)

- EAC: Voter FAQs (xref: `eac_voter_faqs_page`)
- EAC: Register and Vote in Your State (xref: `eac_register_and_vote_in_your_state_page`)
- NASS: Can I Vote (xref: `nass_can_i_vote_page`)
- NASS: #TrustedInfo2026 (xref: `nass_trustedinfo_2026_page`)
- Vote.gov: Home / official secure-site marker (xref: `vote_gov_home_page`)
