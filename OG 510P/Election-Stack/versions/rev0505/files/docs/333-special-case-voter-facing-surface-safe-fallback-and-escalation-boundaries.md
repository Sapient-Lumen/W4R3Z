# 333. Special-case voter-facing surface safe fallback and escalation boundaries

**Track:** Shared

This document is a compact companion to `docs/310-voter-facing-public-answer-surfaces-family-map-and-promotion-rules.md`, `docs/331-special-case-voter-facing-surfaces-subfamily-and-authority-anchor-minimums.md`, and `docs/332-special-case-voter-facing-surface-nonoverlap-declarations-and-misrouting-firewall.md`.

It answers a narrower question:

**“Once a high-risk special-case surface exists, does it also say clearly when the voter should stop reading that page and move to the ordinary help lane or the rights/safety escalation lane?”**

The archive already checks that the high-risk special-case subfamily — the rows tagged `special_case_high_risk` in the family registry, currently `317–328` and `335–343` — is distinct, fully wired, well-anchored in official-public sources, and explicit about adjacent-surface non-overlap.
This companion adds one more small control: each of those docs should also carry an explicit **safe default routing boundary**.

It composes with:
- `docs/305-election-office-contact-directories-office-hours-and-change-notices-as-evidence-surfaces.md`
- `docs/307-voting-issue-reporting-civil-rights-escalation-and-change-notices-as-evidence-surfaces.md`
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
- `docs/331-special-case-voter-facing-surfaces-subfamily-and-authority-anchor-minimums.md`
- `docs/332-special-case-voter-facing-surface-nonoverlap-declarations-and-misrouting-firewall.md`
- `scripts/check_voter_facing_special_case_fallback_escalation.py`

## Why this exists

The docs in the `special_case_high_risk` subfamily cover questions where a wrong answer is not merely inconvenient.
A bad answer can tell a voter to use the wrong emergency-ballot path, the wrong youth-registration or primary-eligibility path, the wrong registration path, expose a protected address, mis-handle custody or facility logistics, or leave a person with an urgent rights problem reading a page that no longer safely answers the real question.

Those docs therefore need a uniform answer to two fallback questions:

1. **When should the voter stop relying on the special-case page and use the authoritative office/help directory lane instead?**
2. **When should the voter stop treating this as an ordinary help question and use the rights/safety escalation lane instead?**

Without that boundary, even a well-sourced niche page can still fail operationally by keeping the voter in the wrong lane too long.

## Bounded subfamily

For this fallback/escalation rule, the bounded subfamily is still the same highest-risk cluster:

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

## Safe fallback floor

Each doc in the `special_case_high_risk` subfamily should contain a short section with an explicit heading that names both:

- `305` as the **authoritative ordinary-help / office-routing fallback**, and
- `307` as the **rights, intimidation, discrimination, safety, or urgent-escalation fallback**.

That section should not restate the full contents of `305` or `307`.
It should simply tell the reader when the special-case surface stops being enough.

Minimum expectation:

- if the voter mainly needs the correct office, clerk, county board, registrar, or election-help contact for a time-sensitive but ordinary uncertainty, the doc should point to `305`;
- if the voter is facing denial despite likely eligibility, coercion, intimidation, discrimination, unsafe exposure, obstruction by an institution, or another issue where rights/safety escalation matters, the doc should point to `307`.

This keeps the special-case cluster from pretending to be self-sufficient.
The archive should not require a voter to infer those lane changes from scattered overlap prose.

## What this rule does and does not do

This rule **does** help catch these mistakes:

- a special-case surface that explains the niche rule but never says what to do when uncertainty remains,
- a surface that names ordinary adjacent docs but forgets the office/help fallback,
- a surface that treats a rights or safety problem as if it were only an FAQ or clerical issue,
- or drift where one special-case page carries escalation guidance but the others do not.

This rule **does not** replace:

- the family map and overlap rules in `docs/310-*`,
- the registry and duplicate firewall in `docs/329-*`,
- the triplet/orphan check in `docs/330-*`,
- the authority-anchor minimums in `docs/331-*`,
- or the adjacent-surface non-overlap declarations in `docs/332-*`,
- or the temporal-volatility / no-cross-jurisdiction rule in `docs/334-*`,
- or the authority-hierarchy / official-routing-precedence rule in `docs/345-*`,
- or the current-state / superseding-notice discipline in `docs/346-*`.

It is a companion control for **safe default routing**, not a substitute for the other firewalls, including the unresolved-conflict stop / no-synthesis rule in `docs/347-*`, the direct-jurisdiction anchor floor in `docs/348-*`, the direct-help-route / contactability floor in `docs/349-*`, or the responsible-office specificity / jurisdiction-match floor in `docs/350-*`.

## Mechanical check

The release gate should reject the archive if any doc in the `special_case_high_risk` subfamily is missing a required safe-fallback heading or fails to name both `305` and `307` inside that section.

The checker for this is:

- `scripts/check_voter_facing_special_case_fallback_escalation.py`

## Maintainer posture

When tightening or adding another high-risk special-case voter-facing surface adjacent to the `special_case_high_risk` subfamily, maintainers should prefer this order:

1. prove distinctness in `docs/310-*`,
2. confirm triplet/registry wiring via `docs/329-*` and `docs/330-*`,
3. prove repeated official-public grounding via `docs/331-*`,
4. make adjacent-surface non-overlap explicit via `docs/332-*`,
5. and then make the safe default lane change explicit via this document,
6. and then make temporal volatility / freshness / no-cross-jurisdiction portability explicit via `docs/334-*`,
7. make the authority hierarchy explicit via `docs/345-*`, then make current-state / superseding-notice visibility explicit via `docs/346-*`, then make the unresolved-conflict stop / no-synthesis rule explicit via `docs/347-*`, then confirm the doc still carries at least two direct jurisdiction-specific official-public governing examples via `docs/348-*`, then make the direct office-help route / contactability floor explicit via `docs/349-*`, and then make the responsible-office specificity / jurisdiction-match floor explicit via `docs/350-*`.

That keeps the special-case cluster small, grounded, and safer to use under uncertainty.
For the canonical ordered current control-stack map that keeps newer tail controls discoverable from anywhere in this maintainer subfamily, see `docs/355-special-case-voter-facing-surface-control-stack-reference-closure-and-navigation-firewall.md`.
