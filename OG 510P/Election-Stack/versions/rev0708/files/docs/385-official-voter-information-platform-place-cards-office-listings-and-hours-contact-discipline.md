# 385 — Official voter-information platform place cards, office listings, and hours/contact discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **official election-office place cards, business/profile listings, map/search office cards, and similar third-party platform shells where the public first sees office identity, hours, phone, directions, and “official website” links before reaching the jurisdiction’s own site**.

It does **not** replace the underlying voter-question families in `292–343`.
It does **not** replace:
- `203`, which governs the official-channel directory,
- `305`, which governs the authoritative office/help route,
- `376`, which governs official maps, geolocation helpers, and directions links,
- `379`, which governs stale-link recovery,
- `382`, which governs external web-search result presentation,
- `383`, which governs social-profile shells,
- or `384`, which governs mobile-app store listings.

It adds one narrow rule:
**if an election office expects voters to rely on third-party place cards or office listings for phone, hours, directions, or the first click into an official website, those listings should be claimed or otherwise controlled where feasible, clearly tied back to current official domains/help, updated when hours or location state changes, and preserved as bounded reconstructible routing shells rather than hidden rule sources.**

## Why this is a distinct surface

Current official and platform guidance is enough to justify a bounded control here.

EAC's current **Effective Design for the Administration of Federal Elections** says online voter-information materials should be clear, understandable, accessible, usable, and accurate.
EAC's current **Voter Education Topics: Editable Content Document** keeps election-office phone/TTY information, website links, voting-location finders, and “call the election office” recovery inside the live voter-information lane.
Digital.gov's current `.gov` guidance says `.gov` or `.mil` domains increase trust, security, and accountability, and that public trust depends on clear and consistent use of recognizable official domains.
Vote.gov's current trust marker says official websites use `.gov` and secure sites use HTTPS, and its About page says Vote.gov is a trusted official source that routes voters to state election websites for state-specific information.
Google's current Business Profile help says verified owners can edit address, hours, contact info, and photos so customers can find and learn more about a location; it separately says special hours should be used for holidays and other temporary changes, and that verification is what gives the office ownership and the ability to keep business info accurate.
Apple's current Business Connect guidance says place-card details such as hours appear to customers on Maps and across Siri, Spotlight, Wallet, and more; its location-attributes guide says standard and special hours appear on the Place Card and, whenever possible, should match the hours published on the official website; and its location-edit guidance says location information should be kept updated often so customers can see the latest hours of operation and similar public-facing details. (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`; xref: `eac_voter_education_topics_editable_content_document_2024_pdf`; xref: `digital_gov_requirements_registration_use_gov_domains_page`; xref: `vote_gov_home_page`; xref: `vote_gov_about_us_page`; xref: `google_business_profile_edit_business_profile_page`; xref: `google_business_profile_special_hours_page`; xref: `google_business_profile_verify_business_page`; xref: `apple_business_connect_support_guides_faq_page`; xref: `apple_business_connect_configure_location_attributes_page`; xref: `apple_business_connect_edit_or_remove_location_page`)

That is enough to treat platform office cards as a real public-answer delivery layer.
They are not just marketing fluff.
They are often the first practical answer a voter sees about **which office is official, whether it is open, which phone number to call, where to drive, and which website link to trust**.

## Place-card shells are routing aids, not hidden authorities

A platform place card MAY help a voter find the right office quickly.
It MUST NOT become a hidden authority layer that silently outranks the jurisdiction’s own current office/help page, closure notice, or rights/escalation lane.

The controlling artifact remains the current official office directory, help page, notice, or other authoritative destination the jurisdiction actually stands behind.
The place-card layer should only do enough to:
- make the office recognizable,
- expose current practical routing details,
- point back to the official domain/help path,
- and keep stale or duplicate platform cards from quietly becoming the trusted answer.

## Claimed / controlled listing state matters

Google's current guidance makes the ownership boundary explicit: verification gives the organization ownership of the Business Profile so it can edit name, hours, and related information and keep that information accurate.
Apple's current Business Connect guidance similarly assumes company verification and privileges before location changes are made. (xref: `google_business_profile_verify_business_page`; xref: `apple_business_connect_support_guides_faq_page`; xref: `apple_business_connect_edit_or_remove_location_page`)

For election offices, that supports a bounded rule:
- if the office is going to rely on a major platform place card,
- it should claim, verify, or otherwise control that listing where the platform supports it,
- and it should know who can update the listing before an election-week closure, move, or routing change forces a fast correction.

An unclaimed or ownerless office card is not automatically false.
But it is a weaker trust and recovery posture than a controlled listing that the office can actually update.

## Hours, special-hours, and holiday / emergency-state discipline

The most common public failure here is not the name of the office.
It is the **hours state**.

Google's current Business Profile guidance says special hours should be used when hours change temporarily for holidays, events, or exceptional circumstances, and explicitly says it is a good idea to confirm holiday hours so customers know the listing is accurate.
Apple's current Business Connect guidance says standard hours are displayed on the Place Card, that special hours can be added for holidays or special events, and that place-card hours should match the hours published on the official website whenever possible. (xref: `google_business_profile_special_hours_page`; xref: `apple_business_connect_configure_location_attributes_page`)

For election offices, that implies a clear floor:
- regular office hours and special/temporary hours should be treated as controlled public-routing data,
- holiday closures, emergency closures, and temporary service windows should not live only on the official site if the office is also relying on platform cards,
- and the platform card should not present “open now” or stale holiday state when the current official closure notice says otherwise.

This matters acutely around:
- registration deadlines,
- absentee request/return cutoffs,
- early-voting windows,
- election-day office support,
- weather/disaster closures,
- and same-day cure or escalation paths.

## Phone, website, and directions are part of the answer surface

EAC's current editable voter-education content keeps office phone/TTY and website links inside the core information package.
Google's current Business Profile help treats address, hours, and contact info as editable fields that help customers find and learn more about the location.
Apple's current support guidance says physical-location details on Maps display across several Apple surfaces. (xref: `eac_voter_education_topics_editable_content_document_2024_pdf`; xref: `google_business_profile_edit_business_profile_page`; xref: `apple_business_connect_support_guides_faq_page`)

So a place card should usually keep three routing cues synchronized with the current official lane:
1. **Phone state** — the listed number should reach the actual current office/help path or clearly recorded fallback.
2. **Website state** — the website action should point to a current recognizable official domain/help destination, not a stale campaign-style microsite, contractor page, or retired subdomain.
3. **Directions/location state** — the address and map pin should reflect the actual public-facing office or service point the office expects voters to use.

A correct `.gov` link on the office website does not rescue a stale platform phone number or wrong office address if the voter never gets past the place card.

## Duplicate, moved, and legacy office-card recovery

Platform place-card surfaces create a special kind of drift:
- duplicate listings,
- old office addresses,
- relocated offices,
- seasonal satellite offices left visible after the season ended,
- and retired contact cards that still look official because of old branding or proximity in search/maps results.

That means the archive should require a compact recovery policy:
- if an office moved, the old place card should point to the current office or clearly show relocation/closure state,
- if duplicate cards exist, the office should know which one is canonical and how duplicates are handled,
- if a temporary office or election-only service point is retired, the platform state should not silently keep routing voters there,
- and when certainty about a listing is low, the public recovery path should route back to the official domain/help lane instead of asking voters to trust the ambiguous card.

Use `379` for the general stale-link and expired-page recovery story.
Use this document for the bounded **platform listing / office-card** layer that can remain stale even when the official site has already been corrected.

## Official-domain legibility still matters

Digital.gov's current domain guidance and Vote.gov's current trust markers make the recovery baseline straightforward: users should be able to recognize an official government destination by `.gov`/HTTPS cues, and trusted public services should route people back to official election websites for state-specific information. (xref: `digital_gov_requirements_registration_use_gov_domains_page`; xref: `vote_gov_home_page`; xref: `vote_gov_about_us_page`)

So the platform card should not be allowed to float as a detached identity shell.
Its website action, help link, or recovery note should preserve a visible path back to the official domain the jurisdiction actually stands behind.

## Minimal platform-listing state taxonomy

A small taxonomy is enough:

1. **current_verified_listing_with_current_official_domain_and_help_route**
2. **current_listing_with_temporary_or_special_hours_clearly_stated**
3. **relocated_or_duplicate_listing_with_successor_recovery**
4. **temporarily_unavailable_listing_with_official_fallback**
5. **uncertain_or_unclaimed_listing_routed_back_to_official_domain_help**

That is usually more useful than trying to mirror every platform-specific status string.

## Preserve bounded reconstruction, not platform analytics exhaust

This archive does **not** need ad-tech dashboards, heatmaps, or individualized map-click logs.
What matters is bounded reconstruction of the public-facing office-card shell.

Prefer preserving:
- listing refs,
- platform name,
- office name and category state,
- address, phone, website, and hours snapshots,
- special-hours / closure refs,
- duplicate/relocation transition refs,
- and timestamps,

over:
- individualized map usage histories,
- per-user directions telemetry,
- call-detail logs tied to named voters,
- or platform engagement analytics that exceed the bounded routing problem.

## Minimal claim-set

A jurisdiction can publish a compact, verifiable claim-set:

1. **Official listing claim:** one or more named platform office listings are official or endorsed public routing shells for scope `E`.
2. **Control claim:** the office can claim, verify, or otherwise manage those listings where the platform supports it, or else it explicitly treats the listing as uncertain and routes people back to the official domain/help lane.
3. **Hours/contact claim:** listed office hours, special-hours state, phone numbers, and website actions are materially current for the period in scope.
4. **Recovery claim:** relocated, duplicate, closed, or stale listings preserve visible successor or official-domain recovery.
5. **Domain-legibility claim:** platform website actions point to recognizable current official domains/help destinations.
6. **Trace-minimization claim:** bounded reconstruction is possible without individualized platform telemetry.

## Canonical digest artifacts

Publish **small digests of the place-card surface**, not platform analytics exports.

- **Place Card Surface Digest (PCSD):** digest of the bounded office-card payload for a scope.
- **Place Card Hours Snapshot Digest (PHSD):** digest of the currently published regular/special-hours state across named platform listings.
- **Office Listing Transition Digest (OLTD):** digest of relocation, closure, duplicate-resolution, or successor-listing events.

## What belongs in the public place-card payload

Keep the payload **small, platform-agnostic, office-legible, and recovery-capable**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `place_card_surface_label`
- `official_place_listings[]`
- `covered_surface_refs[]`
- `official_source_anchors[]`
- `delivery_role_note`
- `platform_identity_policy_note`
- `listing_claim_verification_policy_note`
- `hours_sync_policy_note`
- `contact_sync_policy_note`
- `duplicate_listing_policy_note`
- `relocation_recovery_policy_note`
- `official_domain_policy_note`
- `office_listing_state_classes[]`
- `place_card_trace_policy`
- `routing_fallback_uri`
- `routing_fallback_phone`
- `rights_escalation_uri`
- `latest_notice_uri`
- `last_verified_at`
- supersedes / superseded-by pointers

Do **not** publish by default:
- individualized directions telemetry,
- raw caller-identification logs,
- ad-platform audience exports,
- per-user map interaction traces,
- or anything that turns the place-card layer into a shadow case-management system.

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:
- Which platform office listings were official or endorsed at time `T`?
- Could the office actually control or verify those listings?
- What phone number, website, address, and hours state did the public see there?
- Did special-hours or closure state match the current official website/help posture?
- If the listing was stale, duplicate, moved, or uncertain, what official recovery path did the office preserve?
- Could a third party reconstruct the bounded office-card surface without individualized platform telemetry?

## Sources (pinned IDs / lockfile IDs)

- EAC: Effective Design for the Administration of Federal Elections (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`)
- EAC: Voter Education Topics: Editable Content Document (xref: `eac_voter_education_topics_editable_content_document_2024_pdf`)
- Digital.gov: Requirements for the registration and use of .gov domains in the federal government (xref: `digital_gov_requirements_registration_use_gov_domains_page`)
- Vote.gov: homepage + About (xref: `vote_gov_home_page`; xref: `vote_gov_about_us_page`)
- Google Business Profile Help: Edit your Business Profile (xref: `google_business_profile_edit_business_profile_page`)
- Google Business Profile Help: How to set Special hours (xref: `google_business_profile_special_hours_page`)
- Google Business Profile Help: Verify your business on Google (xref: `google_business_profile_verify_business_page`)
- Apple Business Connect Support Guides & FAQs (xref: `apple_business_connect_support_guides_faq_page`)
- Apple Business Connect: Configure location attributes (xref: `apple_business_connect_configure_location_attributes_page`)
- Apple Business Connect: Edit or remove a location (xref: `apple_business_connect_edit_or_remove_location_page`)
