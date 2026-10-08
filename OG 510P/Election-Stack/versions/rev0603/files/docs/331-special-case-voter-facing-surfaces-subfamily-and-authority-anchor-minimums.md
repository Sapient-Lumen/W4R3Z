# 331. Special-case voter-facing surfaces subfamily and authority-anchor minimums

**Track:** Shared

This document is a compact companion to `docs/310-voter-facing-public-answer-surfaces-family-map-and-promotion-rules.md`, `docs/329-voter-facing-public-answer-surface-registry-and-duplicate-firewall.md`, and `docs/330-voter-facing-public-answer-surface-triplet-coherence-and-orphan-control.md`.

It exists to answer a narrower question:

**“When a voter-facing surface covers a high-risk special case, how much official-public anchoring is enough before the archive treats that surface as a real maintained unit?”**

The archive already has a broad family firewall for duplicate surfaces and half-integrated triplets.
This document adds a tighter rule for a smaller cluster where wrong routing is unusually costly.

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
- `scripts/check_voter_facing_special_case_authority_minimums.py`
- `docs/332-special-case-voter-facing-surface-nonoverlap-declarations-and-misrouting-firewall.md`
- `docs/333-special-case-voter-facing-surface-safe-fallback-and-escalation-boundaries.md`
- `docs/334-special-case-voter-facing-surface-temporal-volatility-freshness-and-no-cross-jurisdiction-inference.md`
- `docs/355-special-case-voter-facing-surface-control-stack-reference-closure-and-navigation-firewall.md`

## Why this exists

The high-risk special-case subfamily — the rows tagged `special_case_high_risk` in the family registry, currently `317–328` and `335–343` — answers public questions where a bad answer does more than confuse.
It can wrongly tell a voter they are ineligible, route them into an unsafe public tool, cause ballot-delivery failure, or collapse a special facility/custody workflow back into an ordinary absentee path that does not actually control.

These are not generic registration FAQs.
They are **special-case public answer surfaces** whose existence depends on repeated official publication patterns across jurisdictions. That includes `317`, where the public answer can directly decide **whether the voter may obtain replacement materials, whether the original ballot must be surrendered or affirmatively voided, and whether the remaining same-election fallback is regular-ballot, provisional-ballot, or no longer available**; `318`, where the public answer can directly decide **whether a moved or updated voter still uses the old site, a new site, a same-day or early-voting correction path, or a provisional fallback because the record did not propagate in time**; `319`, where the public answer can directly decide **whether an inactive or removed record still leaves a lawful path to vote and whether the next step is affirmation, activation, or fresh registration**; `320`, where the public answer can directly decide **whether the voter may lawfully cast a regular ballot at this site at all, whether another site is required, and whether the next question is ordinary rerouting or fail-safe-ballot routing**; `321`, where the public answer can directly decide **whether the voter should receive a provisional ballot at all, whether a regular ballot remains available at another site, and whether the ballot will count in full, only in part, or not at all**; `322`, where the public answer can directly decide whether a late-emergency absentee lane still exists and who may lawfully pick up or transport the ballot under emergency-specific rules; `340`, where the public answer can directly decide **whether a young voter is only pre-registered or already active, and whether age alone permits primary participation before the 18th birthday because the general-election threshold will be met**; and the `341–343` cluster, where the public answer can directly decide **who may personally assist, who may lawfully transport or return ballot materials, and whether a challenged voter keeps a regular ballot or is pushed onto a fail-safe path**.
If a proposed addition can only point to one thin public page, one translated flyer, or one county explainer with no broader official pattern, the safer default is usually:

- tighten an existing surface’s overlap notes,
- add a bounded note to `docs/310-*`,
- or leave the idea in the research queue until a stronger cross-jurisdiction pattern appears.

## Bounded subfamily

For this authority-anchor rule, the bounded subfamily is the set of rows tagged `special_case_high_risk` in `artifacts/tables/voter-facing-public-answer-surfaces.csv`. At this revision that means:

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

These docs are grouped here because they share three properties:

1. the question often arises only for a minority of voters,
2. the wrong public answer can immediately change legal eligibility, safety posture, ballot logistics, whether a replacement ballot can still be lawfully issued, whether a prior packet must be surrendered, whether a voter is still active, whether a listed site is lawful for this voter and phase, whether the remaining fallback is regular-ballot or provisional-ballot, whether a youth voter is merely pre-registered or already active, whether a 17-year-old may participate in a primary before turning 18, access to a late-emergency absentee lane, access to reservation-specific service points, who may lawfully assist or touch ballot materials, or whether a challenged voter keeps a regular ballot instead of shifting to a fail-safe ballot,
3. and jurisdictions often publish the correct answer in a **special page, guide, flyer, directive, or workflow** rather than in the ordinary registration/update/status flow.

## Authority-anchor minimum

A doc in this bounded subfamily should not be treated as a fully promoted maintained surface unless the doc itself contains **at least three distinct official-public authority anchors**.

For this purpose, an authority anchor means a lockfile-backed external-source ID cited in the doc via `source:` or `xref:` where the lock entry is tagged `official_websites`.

Why three?

- one source is often only a local expression of a rule,
- two sources can still be a coincidence or a thin restatement,
- three official anchors is enough to show that the archive is tracking a repeated public-answer pattern rather than inventing a new family member from one corner case.

This rule is intentionally small.
It does **not** require a fifty-state survey.
It does require more than a single anecdotal public page.

## What this rule does and does not do

This rule **does** help catch these mistakes:

- promoting a new niche voter-facing surface from one local page,
- writing a numbered doc whose public-boundary claim is stronger than its official-public support,
- quietly replacing repeated official-public patterns with one advocacy summary,
- or letting a high-risk special-case surface drift away from lockfile-backed official references.

This rule does **not** replace:

- the distinctness test in `docs/310-*`,
- the family registry / anti-duplicate firewall in `docs/329-*`,
- or the doc/template/checklist triplet check in `docs/330-*`.
- or the explicit adjacent-surface misrouting declarations in `docs/332-*`, the safe fallback / escalation boundary declarations in `docs/333-*`, the temporal-volatility / no-cross-jurisdiction rule in `docs/334-*`, the authority-hierarchy / official-routing-precedence rule in `docs/345-*`, the current-state / superseding-notice discipline in `docs/346-*`, the unresolved-conflict stop / no-synthesis rule in `docs/347-*`, the direct-jurisdiction anchor floor in `docs/348-*`, the direct-help-route / contactability floor in `docs/349-*`, the responsible-office specificity / jurisdiction-match floor in `docs/350-*`, or the release-time freshness floor in `docs/344-*`.

A doc can satisfy the authority minimum and still fail the overlap test.
A doc can satisfy the overlap test and still fail the authority minimum.
Both checks matter. The safe fallback / escalation declarations from `docs/333-*` matter too. The temporal-volatility / no-cross-jurisdiction declarations from `docs/334-*` matter as well. The authority-hierarchy / official-routing-precedence rule from `docs/345-*` matters too, because a high-risk edge-case doc can still read like a generalized national answer even when its sources are current. The current-state / superseding-notice discipline from `docs/346-*` matters too, because a high-risk edge-case doc can still point readers into stale visible materials even after it correctly names the controlling authority. The release-time freshness floor from `docs/344-*` matters too, because a high-risk edge-case doc can still ship stale official examples even when its prose correctly says freshness matters. The direct-jurisdiction anchor floor from `docs/348-*` matters too, because a high-risk edge-case doc can still talk like a jurisdiction-specific guide while citing mostly national routing material. The direct-help-route / contactability floor from `docs/349-*` matters too, because a high-risk edge-case doc can still name the right authority while failing to expose a concrete reachable help path under deadline pressure. The responsible-office specificity / jurisdiction-match floor from `docs/350-*` matters too, because a high-risk edge-case doc can still expose a contact path while leaving the reader unsure which official office actually owns the case. The official secure-channel / minimum-disclosure floor from `docs/351-*` matters too, because a high-risk edge-case doc can still point to the right office while leaving the reader to overshare sensitive records on the wrong channel. The operability-now / deadline-imminence floor from `docs/352-*` matters too, because a high-risk edge-case doc can still name the right office and channel while failing to say whether that path is still usable right now under same-day or near-cutoff pressure.

## Mechanical check

The release gate should reject the archive if any doc in the `special_case_high_risk` subfamily has fewer than three distinct official-public authority anchors.

The checker for this is:

- `scripts/check_voter_facing_special_case_authority_minimums.py`

## Maintainer posture

When proposing another special-case voter-facing surface adjacent to this cluster, maintainers should prefer this order:

1. prove distinctness in `docs/310-*`,
2. confirm it is not already absorbed by the current tagged special-case rows,
3. prove repeated official-public reality with at least three official authority anchors,
4. confirm that at least two of those anchors are direct jurisdiction-specific governing examples via `docs/348-*`,
5. make the direct office-help route / contactability floor explicit via `docs/349-*`,
6. make the responsible-office specificity / jurisdiction-match floor explicit via `docs/350-*`,
7. make the official secure-channel / minimum-disclosure floor explicit via `docs/351-*`,
8. make the operability-now / deadline-imminence floor explicit via `docs/352-*`,
8. only then add registry/triplet wiring and numbered prose,
9. and then make the `305`/`307` lane change explicit via `docs/333-*`,
10. and then make temporal volatility / freshness / no-cross-jurisdiction portability explicit via `docs/334-*`,
11. confirm bounded recent official-source review before release via `docs/344-*`,
12. make the authority hierarchy explicit via `docs/345-*`,
13. make current-state / superseding-notice visibility explicit via `docs/346-*`, and then
14. make the unresolved-conflict stop / no-synthesis / office-confirmation rule explicit via `docs/347-*`.

That keeps the archive from turning every unusual voter circumstance into its own weakly grounded numbered surface.
For the canonical ordered current control-stack map that keeps newer tail controls discoverable from anywhere in this maintainer subfamily, see `docs/355-special-case-voter-facing-surface-control-stack-reference-closure-and-navigation-firewall.md`.
