# 371 — Official voter-information community-partner distribution, co-branding, and relay-boundary discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **official voter-information redistributed through community partners**:
schools,
libraries,
colleges,
community organizations,
faith-based organizations,
local businesses,
municipal partners,
and similar trusted third parties that help carry official election information to voters.

It is not trying to turn every partner relationship into a giant governance framework.
It is trying to keep one practical public-risk seam from going soft:
**what happens when an election office asks outside partners to relay official voter guidance, but the relayed copy starts looking like the partner’s own rulebook, drifts out of date, or keeps circulating after the controlling official page changed.**

It composes with:
- `docs/186-incident-communications-as-evidence.md`
- `docs/194-synthetic-media-and-comms-authenticity-minimum-controls.md`
- `docs/203-official-channel-directory-as-evidence.md`
- `docs/205-cache-and-freshness-controls-for-public-surfaces.md`
- `docs/248-accessibility-usability-and-language-access-as-integrity.md`
- `docs/305-election-office-contact-directories-office-hours-and-change-notices-as-evidence-surfaces.md`
- `docs/310-voter-facing-public-answer-surfaces-family-map-and-promotion-rules.md`
- `docs/366-official-voter-information-broadcast-alerts-social-posts-and-linkback-discipline.md`
- `docs/368-official-voter-information-printable-handouts-flyers-postcards-and-edition-linkback-discipline.md`
- `docs/370-official-voter-information-emails-newsletters-reminders-and-forward-context-discipline.md`
- `artifacts/checklists/official-voter-information-community-partner-distribution-checklist.md`
- `artifacts/templates/official-voter-information-community-partner-distribution-payload.json`

## Why this exists (bounded)

The archive now treats web pages, FAQs, hotlines, short-form alerts, media releases, print artifacts, videos, and official emails as governed delivery layers.
That still leaves a real operating lane: **official voter information redistributed through outside trusted voices**.
In practice, election offices often ask community partners to help distribute registration reminders, location changes, rights information, language-access materials, campus guidance, poll-worker recruitment notices, or incident updates.
Those relayed copies move through newsletters, bulletin boards, social feeds, campus channels, front desks, events, and hand-carried materials that the election office does not fully control after handoff.

Current official guidance is specific enough to justify a bounded control here.
EAC's current **Building Community Partnerships** quick-start guide says election officials often reach out to community organizations to augment limited resources and gives examples ranging from language-minority outreach to civic organizations hosting polling locations and community newsletters carrying election-related calls.
The current EAC/CISA **Enhancing Election Security Through Public Communications** guide says election officials should develop relationships with external validators and community partners who can help share and amplify communication to a wide range of voters, and it lists community organizations, faith-based organizations, schools, colleges, universities, service businesses, and government partners as examples.
EAC's current **Voter Education Report** says election officials use a toolbox that includes collaborations with government and community partners and highlights investment in those partnerships as a current statewide pattern.
EAC's current **Trust, Transparency, and Observer Resources for New Election Officials** sheet tells offices to cultivate relationships that can help educate the public and highlights a current best-practice example where government units, local businesses, and municipalities distributed accurate voter information together.
(xref: `eac_building_community_partnerships_quick_start_guide_pdf`; xref: `eac_enhancing_election_security_public_comms_2024_pdf`; xref: `eac_voter_education_report_2024_pdf`; xref: `eac_trust_transparency_observer_resources_new_election_officials_2024_pdf`)

So the bounded problem is simple:
**if a jurisdiction relies on partner redistribution to move voters toward action, how does it keep partner-carried material visibly official, current-linking, and revocable when the underlying answer changes?**

## What this adds (and what it does not)

This document adds a compact **attribution + approved-asset + co-branding + refresh/revocation discipline** for official voter-information distributed through community partners.

It does **not** require every jurisdiction to run a formal partnership program.
It does **not** require publishing exhaustive partner rosters, contracts, or audience analytics.
It does **not** replace:
- the underlying voter-question family in `292–343`,
- the office-routing lane in `305`,
- the short-form alert lane in `366`,
- the print/download lane in `368`, or
- the email/newsletter lane in `370`.

It adds one narrow rule:
**if outside partners are asked to relay action-changing election information, the relayed artifact should visibly identify the official source, point back to the current official destination, stay inside approved modification boundaries, and carry a bounded refresh/withdrawal path when it stops controlling.**

## Distinct boundary

A community-partner distribution lane is a distinct delivery layer because the information moves through a **non-office audience holder** with its own trust, branding, timing, and distribution habits.
That is not the same thing as the election office's own social account, press release, print handout, or email list.
The office may approve the message, but after handoff the copy can be reposted, reformatted, translated informally, co-branded, screenshotted, or left standing in a partner channel long after the originating office changed its own page.

## Attribution and authority floor

A partner-relayed voter-information artifact should make the authority boundary easy to see.
Operationally, that usually means four things stay legible:
- which election office is the authoritative source,
- which partner is only relaying or hosting the material,
- where the current official destination lives now,
- and where the voter should go for official help if the relayed copy is incomplete.

Do not let a campus post, library flyer, church bulletin item, or city-partner newsletter look like the partner itself has independent authority to redefine a voting rule.

## Approved-asset and co-branding boundary

If partners are redistributing action-changing election information, the office should define whether the partner is allowed to use:
- an unchanged official asset,
- a bounded co-branded asset,
- or a partner-written relay that must preserve specific official language and linkback.

That boundary should be explicit.
Safe partner amplification is usually **not** “say anything roughly similar.”
It is closer to: use the approved official asset or approved message frame, keep the official source and help path visible, and do not mutate the key action-changing instruction without office approval.

## Canonical-link and relay-context floor

A partner-relayed artifact should do one of two things:

1. **carry a bounded official fact and point directly to the current controlling official page / notice / FAQ / office-help path**, or
2. **route the voter to the official help path without pretending the partner artifact is the complete rulebook.**

This matters especially for deadlines, location changes, registration/update windows, campus-specific guidance, accessibility/language announcements, and incident updates.
The partner channel may be how the voter first hears the message.
The controlling answer should still live on the official election side.

## Refresh, withdrawal, and revocation discipline

Partner distribution has a persistence problem similar to print and email, but with weaker direct control.
Old campus posts linger.
Old community-newsletter issues stay online.
Old handouts remain on counters.
A well-meaning partner keeps sharing the older graphic because it still looks official.

So when the underlying public answer changes, the office should make the correction **explicit**.
That means:
- identify how partners learn a relayed asset or message is stale,
- publish a superseding or corrected official destination,
- ask partners to remove, stale-mark, or replace action-changing material when practical,
- and keep a bounded record of which partner-distribution packet or approved asset family was withdrawn or superseded.

## Accessibility, language, and audience-fit floor

A partner lane is only operationally real if the target audience can use it.
That means:
- plain language,
- no crucial action-changing content trapped only inside inaccessible images,
- language parity where the jurisdiction maintains it,
- and audience-fit without letting partner tailoring break the official rule.

A campus explainer can sound like it was written for students.
A community-language handout can be tailored for a neighborhood audience.
But the tailored copy should still converge on the same current official answer and help route.

## Canonical digest artifacts

Publish **small digests of the partner-distribution lane**, not complete partner-relationship archives.

- **Partner Distribution Surface Digest (PDSD):** digest of the bounded policy payload for the community-partner relay lane.
- **Partner Asset Family Digest (PAFD):** digest of an approved partner asset/message family used for relaying official voter information.
- **Partner Withdrawal / Superseding Digest (PWSD):** digest of an explicit refresh, revocation, or superseding event for partner-relayed materials.
- **Partner/Official Parity Snapshot (POPS):** optional digest tying the partner-relayed artifact to the current official page / notice / help route.

## What belongs in the public partner-distribution payload

Keep the payload **small, current-state oriented, and relay-aware**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `partner_distribution_family_label`
- `delivery_role_note`
- `partner_classes[]`
- `approved_asset_families[]`
- `action_sensitive_topics[]`
- `attribution_and_authority_policy`
- `co_branding_policy`
- `partner_modification_policy`
- `canonical_destination_policy`
- `refresh_and_withdrawal_behavior`
- `accessibility_and_language_note`
- `public_help_route_uri`
- `public_help_route_phone`
- `latest_notice_uri`
- `last_verified_at`
- supersedes / superseded-by pointers

Do **not** publish by default:
- exhaustive partner directories,
- private contact lists,
- audience analytics,
- informal internal coordination notes,
- or every one-off redistribution event.

## Verification questions for third parties

A verifier, journalist, observer, community partner, or court should be able to answer:
- Which partner-distribution lane or approved asset family was official at time `T`?
- Could an ordinary voter tell which election office was authoritative and which outside partner was only relaying?
- Did the relayed artifact point back to a current official page/help path, or did it act like a standalone rulebook?
- Were partner modifications bounded and visible enough to avoid authority confusion?
- When the underlying answer changed, was there an explicit refresh or withdrawal path for partner-carried materials?
- Did tailored variants stay aligned with the office's current official answer across language, accessibility, and audience-specific adaptations?

## How this fits the family map

Official voter information carried by community partners is **not** a new canonical voter-question family bucket.
It is a relay layer in front of the same underlying voter questions already modeled in `292–343`.

This document only says that, if a jurisdiction uses outside trusted partners to help distribute those answers, the relayed artifact should remain visibly official in source, bounded in modification, linked back to the current official destination, and explicitly refreshable when stale.

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/official-voter-information-community-partner-distribution-payload.json`
- Operator quickcheck: `artifacts/checklists/official-voter-information-community-partner-distribution-checklist.md`

## Sources (pinned IDs / lockfile IDs)

- EAC: Building Community Partnerships quick-start guide (xref: `eac_building_community_partnerships_quick_start_guide_pdf`)
- EAC/CISA: Enhancing Election Security Through Public Communications (xref: `eac_enhancing_election_security_public_comms_2024_pdf`)
- EAC: Voter Education Report (xref: `eac_voter_education_report_2024_pdf`)
- EAC: Trust, Transparency, and Observer Resources for New Election Officials (xref: `eac_trust_transparency_observer_resources_new_election_officials_2024_pdf`)
