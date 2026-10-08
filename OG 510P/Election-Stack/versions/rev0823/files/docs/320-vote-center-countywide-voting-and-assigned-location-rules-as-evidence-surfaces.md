# 320. Vote-center, countywide-voting, and assigned-location rules as evidence surfaces

**Track:** Shared / Public surfaces

This document treats the **public answer surface for “for this phase of voting, may I vote at any vote center in my county, only at one assigned early-voting center, or only at my designated precinct/poll site, and which notice controls if that answer changed?”** as an **evidence surface**.
The goal is not to publish internal site-selection memos, staffing plans, or full county election-administration manuals. The goal is to make seven things hard to fake after the fact:

1. **Which official public model controlled location eligibility** for the relevant phase of voting,
2. **Whether the model differed by phase** (for example early voting vs. Election Day),
3. **Whether the voter could use any site in a county, only a subset of assigned centers, or only one assigned precinct/poll site**, 
4. **Which geographic scope and voter class the rule applied to**,
5. **Which lookup or assignment tool, if any, actually bound the voter to the controlling location answer**,
6. **Whether a change in the model or assigned-site rule was published as an explicit superseding event**, and
7. **Whether directories, PDFs, lookup tools, hotline/help scripts, and at-poll fallback guidance stayed consistent about the controlling location-eligibility answer**.

It composes with:
- `docs/186-incident-communications-as-evidence.md`
- `docs/195-rumor-control-and-status-boards-as-verifiable-public-surfaces.md`
- `docs/199-official-surface-security-snapshots.md`
- `docs/200-publicnotice-feeds-and-mirror-index.md`
- `docs/201-public-surface-parity-snapshots.md`
- `docs/203-official-channel-directory-as-evidence.md`
- `docs/205-cache-and-freshness-controls-for-public-surfaces.md`
- `docs/223-public-surface-capture-notes-and-reproducibility.md`
- `docs/290-public-incident-bulletin-with-digest-references.md`
- `docs/292-polling-place-directory-and-change-notices-as-evidence-surfaces.md`
- `docs/297-early-voting-site-hours-and-change-notices-as-evidence-surfaces.md`
- `docs/299-polling-place-live-status-queue-advisories-and-reroute-notices-as-evidence-surfaces.md`
- `docs/305-election-office-contact-directories-office-hours-and-change-notices-as-evidence-surfaces.md`
- `docs/315-precinct-district-and-jurisdiction-lookups-and-assignment-change-notices-as-evidence-surfaces.md`
- `docs/321-provisional-ballot-issuance-reasons-partial-count-rules-and-voter-instructions-as-evidence-surfaces.md`
- `docs/331-special-case-voter-facing-surfaces-subfamily-and-authority-anchor-minimums.md`
- `docs/332-special-case-voter-facing-surface-nonoverlap-declarations-and-misrouting-firewall.md`
- `docs/333-special-case-voter-facing-surface-safe-fallback-and-escalation-boundaries.md`
- `docs/334-special-case-voter-facing-surface-temporal-volatility-freshness-and-no-cross-jurisdiction-inference.md`
- `docs/345-special-case-voter-facing-surface-authority-hierarchy-and-official-routing-precedence.md`

## Why this exists (bounded)

Official election authorities already publish **location-eligibility model** as a distinct public answer, not merely as a side-effect of a site directory. Texas’s current **Where to Vote** page says that during early voting registered voters may vote at any early-voting location in their county of residence, while on Election Day voters may vote at any location only if the county participates in the Countywide Polling Place Program and otherwise must vote in their assigned precinct. Indiana’s current **Vote Center Information** page says vote centers allow voters to cast a ballot at any county location of their choosing on Election Day as an alternative to traditional precinct-based voting. Clark County, Nevada’s current **Election Day Vote Centers** page says voters may vote on Election Day at any vote center in the county rather than one assigned polling place. New York State’s current **Early Voting** page says voters may visit any of their assigned early-voting centers in their county, except in New York City where voters are assigned to one early-voting site; New York City’s current **How to Vote** page likewise tells voters to make sure they are at the correct polling site and election district for their address. Sacramento County’s current **What is a Vote Center** page says voters have the opportunity to vote at any vote center located throughout Sacramento County, including before Election Day. (xref: `texas_where_to_vote_page`, `indiana_vote_center_information_page`, `clark_county_vote_centers_election_day_page`, `new_york_early_voting_page`, `new_york_city_how_to_vote_page`, `sacramento_what_is_a_vote_center_page`)

That is a real public-answer boundary, not just another location page. `docs/292` answers **which sites the jurisdiction designated**. `docs/297` answers **when early-voting sites are open**. `docs/315` answers **which precincts, districts, and local jurisdictions apply**. `docs/321` answers **what fail-safe ballot path may still exist once the voter is already being routed away from a regular ballot**. None of those, by themselves, fully capture the bounded public fact of **location eligibility model**: whether a voter may use any countywide site, only a designated subset, or one assigned location for the current phase; whether a lookup result is exclusive or merely one lawful option; and which superseding notice controls when that answer changes.

Because a wrong answer here can wrongly send a voter to the wrong site, wrongly convince the voter that a listed location is lawful when it is not, or conceal when the next step is an ordinary help escalation versus a fail-safe ballot question, this surface now sits inside the archive's `special_case_high_risk` control perimeter and should continue to satisfy the companion firewalls in `docs/331-*`, `docs/332-*`, `docs/333-*`, `docs/334-*`, `docs/345-*`, and `docs/344-*`.

This document stays intentionally bounded. It is **not** a vote-center procurement manual, a statewide statutory digest, or a site-operations handbook. It is a claim that election offices should be able to prove which public location-eligibility model controlled the voter answer when a person asked, **“Can I vote here, or do I need a different site for this phase?”**

For the canonical current `special_case_high_risk` control-stack map that keeps the full companion-control perimeter discoverable from the surface doc itself instead of freezing an older partial list, see `docs/355-special-case-voter-facing-surface-control-stack-reference-closure-and-navigation-firewall.md`.

## Minimal claim-set

A jurisdiction can publish a compact, verifiable claim-set:

1. **Authoritative location-model claim:** for election scope `E`, the jurisdiction identified one authoritative public surface that stated the current location-eligibility model.
2. **Phase-specific model claim:** the public surface stated whether the model differed across early voting, Election Day, special-election windows, runoff windows, or other bounded phases.
3. **Eligibility-scope claim:** the public surface stated whether the voter could use any countywide site, any vote center, an assigned subset of centers, or only one assigned precinct/poll site.
4. **Lookup-binding claim:** if a site lookup or poll-site finder was required, the public surface stated how that lookup bound the voter to the controlling location answer.
5. **Change/supersession claim:** changed vote-center availability, changed countywide-participation status, or changed assigned-site rules were published as explicit superseding events rather than silent edits.
6. **Fallback/help claim:** the public surface named the authoritative help path when the voter’s location eligibility could not be safely inferred from stale or contradictory materials.
7. **Parity claim:** web pages, PDFs, “find my site” tools, hotline/help scripts, and public notices converged on the same effective location-eligibility answer.

## Canonical digest artifacts

Publish **digests of the public location-eligibility surface**, not internal site contracts or staffing plans.

- **Location Eligibility Model Surface Digest (LEMSD):** digest of the authoritative public payload defining vote-center / countywide / assigned-location rules for an election scope.
- **Location Eligibility Change Notice Digest (LECND):** per-event digest for a public notice changing countywide-voting status, assigned-center rules, precinct-only instructions, or another bounded location-eligibility rule.
- **Location Eligibility Lookup Binding Digest (LELBD):** optional digest binding a poll-site finder or site-assignment tool to the controlling model statement.
- **Location Eligibility Parity Snapshot (LEPS):** optional snapshot binding the effective public state across site lists, lookup tools, hotline/help scripts, and notices.
- **Location Eligibility Help Path Digest (LEHPD):** optional digest of the fallback path when a voter cannot determine whether a given site is lawful for the current phase.

## What belongs in the public location-eligibility payload

Keep the payload **small, phase-specific, and action-oriented**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `authoritative_model_uri`
- optional `authoritative_site_lookup_uri`
- optional `authoritative_site_list_uri`
- `authoritative_help_uri` and/or `authoritative_help_phone`
- `effective_from` and optional `effective_until`
- `freshness_note`
- `last_verified_at`
- supersedes / superseded-by pointers
- pointer to the latest signed correction or advisory notice

Recommended `phases[]` fields:
- `phase_id`
- `phase_kind` (`early_voting`, `election_day`, `special_election_window`, `runoff_window`, `other`)
- `location_eligibility_model` (`countywide_any_site`, `countywide_any_vote_center`, `assigned_center_subset`, `precinct_based_only`, `assigned_site_only`, `hybrid`, `other`)
- `geographic_scope_note`
- optional `applicable_voter_scope`
- optional `lookup_binding_note`
- optional `site_lookup_uri`
- optional `site_list_uri`
- optional `exception_notes[]`
- bounded `plain_language`
- `notice_uri`

Recommended bounded vocabularies for `exception_notes[]`:
- `new_york_city_assigned_early_voting_exception`
- `countywide_program_optional_by_county`
- `special_election_district_only`
- `party_specific_or_ballot_style_constraint`
- `polling_place_reassignment`
- `other_bounded_public_exception`

Do **not** publish by default:
- internal site-selection scoring or lease negotiations
- staffing levels or detailed security layouts
- full county election manuals when a bounded public rule statement plus pointer will do
- raw voter-check-in data
- silent “same as last election” assumptions without an explicit current public statement when the model can differ by election or phase

## Relationship to adjacent surfaces and non-overlap rules

### `292` and `320` are adjacent but not interchangeable

- `292` answers: **which site or sites did the jurisdiction designate?**
- `320` answers: **may this voter lawfully use any designated site, a designated subset, or only one assigned site for the current phase?**

A complete site directory can still fail voters if it omits whether countywide voting or assigned-site rules control. The reverse can also happen.

### `297` and `320` are adjacent but not interchangeable

- `297` answers: **when are early-voting sites open?**
- `320` answers: **which of those sites the voter may lawfully use for the current phase, and whether the model differs from Election Day.**

A jurisdiction can publish correct early-voting hours while still failing to say whether the voter may use any site, only assigned centers, or one designated site.

### `315` and `320` are adjacent but not interchangeable

- `315` answers: **which precinct, districts, and local election jurisdiction apply?**
- `320` answers: **how those assignments translate into countywide-voting, vote-center, or assigned-location rules for the public-facing act of showing up to vote.**

A jurisdiction can publish a correct precinct/district assignment while still misdescribing whether the voter may use any county site or must appear at one assigned location. The reverse can also happen.

### `299`, `320`, and `321` are adjacent but not interchangeable

- `299` answers: **whether a listed site is currently open, delayed, long-line, relocated, or temporarily unavailable.**
- `320` answers: **whether the voter may lawfully cast the ballot at that site at all for the current phase.**
- `321` answers: **which fail-safe ballot path may still apply once the voter is being rerouted or denied a regular ballot.**

A live-status page can correctly say a vote center is open while the public location-eligibility answer is wrong about whether this voter may use it. A provisional-ballot page can also be correct while the jurisdiction still failed to say whether a regular ballot remained available at another lawful site.

Do not merge these surfaces. A public location-eligibility page is not interchangeable with a site directory, hours page, assignment lookup, live-status page, or provisional-ballot page just because all of them touch the same trip to the polls.

## Safe fallback and escalation boundaries

Use this surface when the decisive question is **whether the voter may lawfully vote at any countywide site, any vote center, only assigned centers, or one designated site for the current phase, and which current official notice controls that answer**.

Move to `docs/305-election-office-contact-directories-office-hours-and-change-notices-as-evidence-surfaces.md` when the remaining problem is ordinary but time-sensitive office routing: the voter needs the correct county board, registrar, clerk, or official help line to confirm whether a lookup result is exclusive, whether a superseding location notice changed the allowed site, whether a district-only exception applies, or whether the poll-site finder and posted list have drifted.

Move to `docs/307-voting-issue-reporting-civil-rights-escalation-and-change-notices-as-evidence-surfaces.md` when the problem is no longer just a public-information ambiguity — for example, the public surface says the voter may use any county site but poll workers refuse to honor it, the voter is being threatened or obstructed while trying to reach a lawful location, the office is selectively giving contradictory location answers, or a wrong-site rule is being applied in a way that raises civil-rights, intimidation, discrimination, access, or safety concerns.

The point is not to make `320` self-sufficient. The point is to keep the location-eligibility surface bounded while still naming the ordinary-help lane and the rights/safety lane explicitly.

## Temporal volatility, freshness, and no-cross-jurisdiction rules

Vote-center, countywide-voting, and assigned-location rules are **jurisdiction-specific** and often vary by state, county, municipality, election phase, election type, whether the county participates in a countywide program, whether a city is carved out as a special exception, and whether a site finder is advisory or binding. Do **not infer** that another state, another county, or another jurisdiction uses the same location-eligibility model just because the words “vote center” or “polling place” appear on both pages. These rules are **not portable** across jurisdictions without current official verification.

Treat this surface as **time-sensitive**. Prefer a current official page, lookup tool, FAQ, or notice with a **dated**, **last updated**, or **as-of** signal when one is available, and verify the current **official** state or local source before routing a voter based on memory, an old flyer, or a copied county explainer. Check for updates when a county recently changed participation in a countywide program, reassigned early-voting centers, or published a late superseding notice.

This matters especially where one jurisdiction allows any county vote center on Election Day, another allows any assigned early-voting site but only one Election Day precinct, another carves out a city-specific early-voting exception, and another treats the lookup tool as the only binding answer. The archive should make those distinctions explicit rather than implying that one jurisdiction’s model is safely reusable somewhere else.

## Authority hierarchy, official-routing precedence, and national-summary ceiling

For this topic, the controlling answer is the current official state or local election-office source for the voter’s jurisdiction and election, including the county board, registrar, clerk, ballot instructions, cure notice, or other official public instruction that directly governs the case. National routing pages, this archive, and other generalized explainers are routing aids, not substitutes for the controlling jurisdiction-specific official source. If a national, statewide, county, facility, or archive summary conflicts with the most current official instruction that directly governs the voter’s case, prefer the most current official source for the relevant jurisdiction and election.


## Direct-jurisdiction official examples and national-routing non-substitution

These high-risk edge-case rules should be grounded in direct jurisdiction-specific official-public examples, such as the current state election office, county board, registrar, clerk, tribal government or tribal election office, court-governed public instruction, or another official public source that directly governs the voter’s case. National routing pages, federal explainers, this archive, and other generalized summaries can help the reader find the right office, but they are not substitutes for jurisdiction-specific governing examples. Maintain at least two direct-jurisdiction official-public anchors for this topic so the surface is not supported only by national routing material or generalized official summaries.

## Current-state visibility, superseding notices, and stale-material rules

These rules often move through advisories, packet inserts, correction notices, updated FAQs, replacement forms, or other official-public instructions while older pages, PDFs, screenshots, mirrored copies, or reposted summaries remain visible. The public answer should tell the reader which current official notice, form edition, packet instruction, advisory, or office page currently controls, whether it supersedes, corrects, updates, amends, or replaces an older public instruction, and where the dated / effective / last-updated / as-of marker appears when one is published. Do not treat an archived page, stale PDF, older screenshot, or generalized summary as controlling if a newer official instruction directly governing the case exists. If multiple official materials remain visible, prefer the latest official instruction that directly governs the voter’s case, especially where the newer item says it supersedes, corrects, updates, amends, or replaces the earlier one.

## Unresolved official conflict, no-synthesis, and office-confirmation rule

These rules sometimes appear in multiple official-public artifacts that are incomplete, materially inconsistent, or still unresolved even after checking dates and superseding notices. If multiple official materials still conflict, disagree, or leave a material gap and no current controlling official instruction is clear, do not synthesize, combine, average, or infer a controlling answer from fragments, older summaries, neighboring-jurisdiction examples, or partly matching forms. Treat that unresolved conflict itself as a stop condition. Use the current authoritative state or local election office, registrar, clerk, county board, or the office/help path named in `305` to obtain case-specific confirmation before acting. If the unresolved conflict is paired with denial despite likely eligibility, intimidation, discrimination, unsafe disclosure, or another rights/safety problem, move to `307`.

## Direct office-help route and contactability floor

These rules often become operationally real only when the voter can reach the correct official office quickly. The public answer should not stop at abstract advice to “contact your election office.” It should expose a real official help/contact path — for example a current office/help page, local office directory, or phone/help number — that the voter can use the same day or before a deadline closes. Keep `authoritative_help_uri` and/or `authoritative_help_phone` populated for this surface, and say clearly when `305` is the correct ordinary-help lane for deadline-near or case-specific confirmation. National routing pages, federal explainers, and generalized summaries can help the reader find the right office, but they are not substitutes for a concrete jurisdiction-specific help/contact path. If the issue has crossed into coercion, intimidation, discrimination, wrongful denial despite likely eligibility, unsafe disclosure, or another rights/safety problem, preserve `307` as the escalation lane rather than treating an ordinary help number as enough.

## Responsible office specificity and jurisdiction-match floor

A concrete help page or help phone is still not enough if the public answer leaves the voter guessing which official office actually owns this case. The public answer should say which office role controls for this issue — for example the county board, registrar, clerk, city/township office, tribal election office, state elections division, or another jurisdiction-specific official office named by the governing source — and should keep that office identity matched to the voter's actual jurisdiction and election scope. Do not treat a neighboring county example, another campus/facility workflow, a state-level summary, or a generalized national explainer as proof that the same office controls every voter's case. Keep `authoritative_office_name` and `authoritative_office_scope` populated for this surface so the public artifact states not only how to ask for help, but which official office is responsible. Use `305` when the voter needs help locating or confirming the correct office or directory path for the case. If the wrong-office routing itself is tied to intimidation, discrimination, wrongful denial despite likely eligibility, unsafe disclosure, or another rights/safety problem, preserve `307` as the escalation lane.

## Official secure-channel and minimum-disclosure floor

These high-risk cases often require the voter to discuss sensitive personal facts or submit documents. The public answer should tell the reader to use only the named official website, secure HTTPS form, verified local office directory, official office phone, or in-person office path for sensitive case details and documents. Do not disclose more personal information than the current official process requires, and do not post or send full Social Security numbers, driver's license numbers, dates of birth, confidential residence details, court papers, custody records, safety-program materials, citizenship documents, or other sensitive identifiers through public, unverified, or generalized channels. If the current public instructions do not show a secure submission path, use `305` to reach the responsible official office first and confirm the correct secure channel before transmitting records. Keep `official_secure_channel_note` and `minimum_necessary_disclosure_note` populated for this surface so the public artifact states both how to reach the office and how to avoid oversharing. If the disclosure risk itself is tied to intimidation, coercion, discrimination, unsafe exposure, wrongful denial despite likely eligibility, or another rights/safety problem, preserve `307` as the escalation lane.

## Operability-now, live availability, and deadline-imminence floor

These high-risk cases often fail at the last mile because the nominally correct official path may not still be usable right now. When the issue is same-day, deadline-near, or already inside the final office-hours window, the public answer should tell the reader to verify that the responsible office, portal, site, delivery window, or other named official path is still open and operating right now using the latest official notice, current hours/closure page, verified office phone, or same-day update channel. Do not rely on an older FAQ, calendar, PDF, screenshot, cached office-hours page, or generic directory when today's office-closing time, holiday closure, bad-weather or disaster disruption, facility-access restriction, portal outage, staffing limitation, or emergency procedural change may control. Keep `operability_now_note` and `deadline_imminence_note` populated for this surface so the public artifact says both how to confirm current live availability and what immediate fallback, next-step, or confirmation rule applies if the original path is no longer operable or the cutoff may already have passed. Use `305` for ordinary office-hours, live-availability, and closure-status confirmation. Preserve `307` when the disruption itself has become a rights/safety problem, likely wrongful denial, intimidation/coercion issue, discriminatory access failure, or another formal escalation case.

## Accessibility, language, and next-step clarity

The public location-eligibility surface should say the decisive routing fact in plain language first: **can this voter vote here now, or is another site legally required for this phase?**

When jurisdictions publish translated pages, accessible lookup tools, printable handouts, hotline scripts, or correction notices, captures should preserve those variants alongside the main web surface. If the decisive instruction is only present in a PDF, lookup result, FAQ tab, or hotline script rather than the main “where to vote” page, that should be recorded as part of the effective public state.

The surface should avoid making voters reconstruct the answer from multiple pages. Terms such as “vote center,” “countywide polling place program,” “assigned site,” or “Election District” should be paired with the immediate voter-facing consequence and the next official place to verify or follow up.

## Verification questions for captures and audits

When capturing or auditing this surface, ask:

1. Which authoritative public page, notice, lookup tool, or FAQ defined the location-eligibility model in force for the election?
2. Did the surface say whether the voter could use any county site, an assigned subset, or only one designated site for the current phase?
3. Did it explain whether the answer changed between early voting and Election Day?
4. Did it say whether a lookup result was binding, optional, or only one lawful site among several?
5. Did it say what help path controlled if the voter saw conflicting site lists, lookup results, or notices?
6. Did website text, lookup tools, PDFs, hotline scripts, and posted notices converge on the same effective answer?
7. If the rule changed, was the change published as an explicit superseding event rather than a silent edit?

## Minimal artifacts in this archive

Use the compact artifact pair already associated with this surface:

- `artifacts/templates/location-eligibility-model-surface-payload.json`
- `artifacts/checklists/location-eligibility-model-surface-checklist.md`

That pair should stay small. The template captures the bounded public routing facts; the checklist keeps capture and review work focused on phase, lawful site scope, lookup binding, supersession, and next-step clarity.

## Sources (authoritative public examples)

- Texas Secretary of State / VoteTexas: Where to Vote (xref: `texas_where_to_vote_page`)
- Indiana Secretary of State: Vote Center Information (xref: `indiana_vote_center_information_page`)
- Clark County, Nevada Election Department: Election Day Vote Centers Have Replaced Assigned Polling Places (xref: `clark_county_vote_centers_election_day_page`)
- New York State Board of Elections: Early Voting (xref: `new_york_early_voting_page`)
- New York City Board of Elections: How to Vote (xref: `new_york_city_how_to_vote_page`)
- Sacramento County Voter Registration & Elections: What is a Vote Center (xref: `sacramento_what_is_a_vote_center_page`)
