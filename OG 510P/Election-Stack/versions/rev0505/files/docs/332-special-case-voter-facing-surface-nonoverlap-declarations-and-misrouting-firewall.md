# 332. Special-case voter-facing surface non-overlap declarations and misrouting firewall

**Track:** Shared

This document is a compact companion to `docs/310-voter-facing-public-answer-surfaces-family-map-and-promotion-rules.md`, `docs/329-voter-facing-public-answer-surface-registry-and-duplicate-firewall.md`, `docs/330-voter-facing-public-answer-surface-triplet-coherence-and-orphan-control.md`, and `docs/331-special-case-voter-facing-surfaces-subfamily-and-authority-anchor-minimums.md`.

It exists to answer one more narrow question for the highest-risk voter-facing edge cases:

**“Even if a special-case surface is real and well sourced, does it still say clearly what it is _not_ so a voter is not pushed into the wrong official path?”**

The archive already has three small firewalls for this family:
- `329` asks whether a proposed surface is distinct enough to deserve a registry row.
- `330` asks whether the surface is actually wired as a doc/template/checklist triplet.
- `331` asks whether the newest high-risk special-case surfaces are grounded in repeated official-public authority.

This document adds a fourth, still-small control:
**the high-risk special-case subfamily — the rows tagged `special_case_high_risk` in `artifacts/tables/voter-facing-public-answer-surfaces.csv`, currently `317–328` and `335–343` — must carry explicit adjacent-surface non-overlap declarations in machine-checkable form.**

It composes with:
- `docs/310-voter-facing-public-answer-surfaces-family-map-and-promotion-rules.md`
- `docs/317-mail-ballot-replacement-spoilage-nonreceipt-and-surrender-fallback-as-evidence-surfaces.md`
- `docs/318-voter-registration-updates-address-name-party-and-move-close-to-election-notices-as-evidence-surfaces.md`
- `docs/319-voter-registration-inactive-removed-statuses-and-reactivation-notices-as-evidence-surfaces.md`
- `docs/320-vote-center-countywide-voting-and-assigned-location-rules-as-evidence-surfaces.md`
- `docs/321-provisional-ballot-issuance-reasons-partial-count-rules-and-voter-instructions-as-evidence-surfaces.md`
- `docs/322-emergency-absentee-ballots-hospitalized-incapacitated-and-late-emergency-delivery-paths-as-evidence-surfaces.md`
- `docs/323-felony-conviction-voting-eligibility-restoration-and-reregistration-help-as-evidence-surfaces.md`
- `docs/324-no-fixed-address-homelessness-residence-and-ballot-delivery-as-evidence-surfaces.md`
- `docs/325-confidential-voter-registration-address-confidentiality-and-protected-ballot-paths-as-evidence-surfaces.md`
- `docs/326-in-custody-eligible-voting-jail-detention-and-civil-commitment-ballot-access-as-evidence-surfaces.md`
- `docs/327-long-term-care-assisted-living-residential-facility-and-facility-assisted-voting-as-evidence-surfaces.md`
- `docs/328-college-student-voting-campus-residence-and-home-address-choice-as-evidence-surfaces.md`
- `docs/335-guardianship-conservatorship-and-court-determined-voting-capacity-as-evidence-surfaces.md`
- `docs/336-tribal-community-voting-tribal-ids-reservation-addresses-and-tribal-government-ballot-access-paths-as-evidence-surfaces.md`
- `docs/337-disaster-displacement-evacuation-and-temporary-relocation-voting-paths-as-evidence-surfaces.md`
- `docs/338-new-citizen-and-newly-naturalized-voter-registration-timing-proof-and-post-ceremony-fallback-paths-as-evidence-surfaces.md`
- `docs/339-signature-alternatives-mark-witness-stamp-and-accessible-signature-cure-paths-as-evidence-surfaces.md`
- `docs/340-youth-voter-preregistration-activation-timing-and-primary-before-general-eligibility-as-evidence-surfaces.md`
- `docs/341-voter-assistance-person-of-choice-interpreter-rules-and-restricted-helper-boundaries-as-evidence-surfaces.md`
- `docs/342-ballot-return-by-another-person-designated-agent-or-bearer-rules-and-ballot-handoff-boundaries-as-evidence-surfaces.md`
- `docs/343-challenged-voter-oaths-affidavits-witnesses-and-fail-safe-ballot-rights-as-evidence-surfaces.md`
- `docs/329-voter-facing-public-answer-surface-registry-and-duplicate-firewall.md`
- `docs/330-voter-facing-public-answer-surface-triplet-coherence-and-orphan-control.md`
- `docs/331-special-case-voter-facing-surfaces-subfamily-and-authority-anchor-minimums.md`
- `docs/333-special-case-voter-facing-surface-safe-fallback-and-escalation-boundaries.md`
- `docs/334-special-case-voter-facing-surface-temporal-volatility-freshness-and-no-cross-jurisdiction-inference.md`
- `docs/345-special-case-voter-facing-surface-authority-hierarchy-and-official-routing-precedence.md`
- `scripts/check_voter_facing_special_case_nonoverlap.py`

## Why this exists

The high-risk special-case subfamily — the rows tagged `special_case_high_risk` in the family registry, currently `317–328` and `335–343` — covers voter questions where a wrong answer changes more than wording. That now includes not only replacement, update/move-close-to-election, inactive/reactivation, and provisional-routing traps, but also the separate question of whether the voter may lawfully use this site at all for the current phase.
It can push the voter into the wrong registration/update tool, the wrong youth-registration or primary-eligibility path, the wrong absentee path, the wrong facility workflow, or an unsafe disclosure path.
Those failure modes often happen not because the archive lacks a source, but because two nearby surfaces look similar when read quickly.

That is why these docs should not merely be **bounded** and **sourced**.
They should also state, in a short reusable form, which adjacent numbered surfaces remain different and why.

## Bounded subfamily

For this misrouting firewall, the bounded subfamily is still:

- `317` — mail-ballot replacement, spoilage, nonreceipt, and surrender-fallback
- `318` — voter-registration updates, address/name/party changes, and move-close-to-election rules
- `319` — inactive / removed registration-state semantics and reactivation
- `320` — vote-center / countywide-voting / assigned-location rules
- `321` — provisional-ballot issuance reasons, partial-count rules, and voter instructions
- `322` — emergency absentee / hospitalized-or-incapacitated late-ballot paths
- `323` — conviction-based eligibility, restoration, and re-registration
- `324` — no-fixed-address / homelessness residence and ballot delivery
- `325` — confidential registration / protected-address voting
- `326` — in-custody eligible voting / jail-detention-civil-commitment ballot access
- `327` — long-term-care / residential-facility / facility-assisted voting
- `328` — college-student campus-vs-home residence choice
- `335` — guardianship / conservatorship / court-determined voting capacity
- `336` — tribal-community voting / tribal IDs / reservation-address and tribal-government access paths
- `337` — disaster displacement / evacuation / temporary-relocation voting paths
- `338` — new-citizen / newly naturalized voter registration timing, proof, and post-ceremony fallback paths
- `339` — signature alternatives, mark/witness, stamp, and accessible signature-cure paths
- `340` — youth-voter preregistration, activation timing, and primary-before-general eligibility
- `341` — voter assistance by person of choice, interpreter rules, and restricted-helper boundaries
- `342` — ballot return by another person, designated-agent or bearer rules, and ballot-handoff boundaries
- `343` — challenged-voter oaths, affidavits, witnesses, and fail-safe ballot rights

These docs belong together here because they are all:

1. edge-case voter-facing answer surfaces,
2. adjacent to one or more ordinary voter-information surfaces that look deceptively similar,
3. and unusually vulnerable to harmful public misrouting when the non-overlap boundary is implicit instead of explicit.

## Non-overlap declaration minimum

A doc in this bounded subfamily should not be treated as a fully promoted maintained surface unless it contains a section with the exact heading:

- `## Relationship to adjacent surfaces and non-overlap rules`

Inside that section, the doc should name at least **two distinct adjacent numbered surfaces** and explain why they are not interchangeable.

Why two?

- one comparison is often only enough to show the most obvious nearby boundary,
- two comparisons show that the document is doing real anti-misrouting work rather than only defending against one easy confusion,
- and the cost stays tiny: a few short bullets or mini-subsections.

This requirement is deliberately modest.
It does **not** require a full adjacency matrix.
It does require a bounded, readable statement of **what this doc is not**.

## What this rule catches

This rule helps catch a different class of mistake from the earlier firewalls:

- a doc is well sourced but still silently duplicates `304`, `318`, `322`, or another nearby surface,
- a future editor tightens the prose but deletes the anti-misrouting boundary,
- a niche surface remains in the family even though its only distinctness claim has collapsed back into a more ordinary page,
- or a new edge-case addition looks plausible while still failing to tell a stressed voter which ordinary surface is the wrong one.

This rule does **not** replace:

- the family map and distinctness test in `docs/310-*`,
- the registry / anti-duplicate firewall in `docs/329-*`,
- the triplet/orphan control in `docs/330-*`,
- or the official-authority minimum in `docs/331-*`.

A surface can pass all of those and still be dangerously easy to misread.
That is the gap this document closes.

## Mechanical check

The release gate should reject the archive if any doc in the `special_case_high_risk` subfamily is missing the exact non-overlap heading or names fewer than two distinct adjacent numbered surfaces inside that section.

The checker for this is:

- `scripts/check_voter_facing_special_case_nonoverlap.py`

For the companion requirement that those same docs also name the `305` ordinary-help lane and `307` rights/safety lane in a dedicated fallback section, see `docs/333-special-case-voter-facing-surface-safe-fallback-and-escalation-boundaries.md`. For the further companion requirement that they must also say the rule is time-sensitive, jurisdiction-specific, and unsafe to port across states/counties/facilities without current official verification, see `docs/334-special-case-voter-facing-surface-temporal-volatility-freshness-and-no-cross-jurisdiction-inference.md`. For the further companion requirement that they must also say the current official state/local election-office source controls over national/archive summaries, see `docs/345-special-case-voter-facing-surface-authority-hierarchy-and-official-routing-precedence.md`. For the further companion requirement that they must also tell the reader how to identify the current controlling official notice when older material remains visible, see `docs/346-special-case-voter-facing-surface-current-state-visibility-and-superseding-notice-discipline.md`. For the further companion requirement that they must also stop on unresolved official conflict instead of synthesizing an answer from fragments, see `docs/347-special-case-voter-facing-surface-unresolved-conflict-stop-and-no-synthesis-rule.md`. For the further companion requirement that they must also carry at least two direct jurisdiction-specific official-public governing examples rather than leaning only on national routing pages or generalized official explainers, see `docs/348-special-case-voter-facing-surface-direct-jurisdiction-anchor-floor-and-national-routing-nonsubstitution.md`. For the further companion requirement that they must also expose a concrete official help/contact path rather than stopping at abstract “contact the office” prose, see `docs/349-special-case-voter-facing-surface-direct-help-route-and-contactability-floor.md`. For the further companion requirement that they must also identify which official office role actually owns the case rather than exposing an undifferentiated help route, see `docs/350-special-case-voter-facing-surface-responsible-office-specificity-and-jurisdiction-match-floor.md`.

## Maintainer posture

When revising or proposing another edge-case voter-facing surface adjacent to this cluster, prefer this order:

1. prove distinctness in `docs/310-*`,
2. prove repeated official-public reality in `docs/331-*`,
3. add the registry/triplet wiring from `docs/329-*` and `docs/330-*`,
4. then write the short non-overlap declaration required here,
5. and then make the `305`/`307` lane change explicit via `docs/333-*`,
6. and then make temporal volatility / freshness / no-cross-jurisdiction portability explicit via `docs/334-*`,
7. make the authority hierarchy explicit via `docs/345-*`, then make current-state / superseding-notice visibility explicit via `docs/346-*`, then make the unresolved-conflict stop / no-synthesis rule explicit via `docs/347-*`, then confirm the doc still carries at least two direct jurisdiction-specific official-public governing examples via `docs/348-*`, then make the direct office-help route / contactability floor explicit via `docs/349-*`, and then make the responsible-office specificity / jurisdiction-match floor explicit via `docs/350-*`.

That keeps the archive from turning “special-case” into “easy to misroute.”
For the canonical ordered current control-stack map that keeps newer tail controls discoverable from anywhere in this maintainer subfamily, see `docs/355-special-case-voter-facing-surface-control-stack-reference-closure-and-navigation-firewall.md`.
