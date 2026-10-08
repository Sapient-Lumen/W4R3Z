# 368 — Official voter-information printable handouts, flyers, postcards, and edition/linkback discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **official printable or downloadable voter-information artifacts**:
flyers,
postcards,
brochures,
pocket guides,
booklets,
infographics,
downloadable PDFs,
and similar print-first or print-portable public materials.

It is not trying to turn every handout into a giant archive object.
It is trying to keep one very practical public-risk seam from going soft:
**what happens when a voter acts on a printable artifact that has been detached from the webpage, reposted as an image, left on a counter, forwarded as a PDF, or photographed weeks after the underlying official page changed.**

It composes with:
- `docs/186-incident-communications-as-evidence.md`
- `docs/194-synthetic-media-and-comms-authenticity-minimum-controls.md`
- `docs/195-rumor-control-and-status-boards-as-verifiable-public-surfaces.md`
- `docs/203-official-channel-directory-as-evidence.md`
- `docs/205-cache-and-freshness-controls-for-public-surfaces.md`
- `docs/206-digest-cards-and-low-bandwidth-publication.md`
- `docs/223-public-surface-capture-notes-and-reproducibility.md`
- `docs/248-accessibility-usability-and-language-access-as-integrity.md`
- `docs/305-election-office-contact-directories-office-hours-and-change-notices-as-evidence-surfaces.md`
- `docs/310-voter-facing-public-answer-surfaces-family-map-and-promotion-rules.md`
- `docs/365-official-voter-faqs-knowledge-base-articles-and-answer-edition-discipline.md`
- `docs/366-official-voter-information-broadcast-alerts-social-posts-and-linkback-discipline.md`
- `docs/367-official-voter-information-press-releases-media-advisories-and-spokesperson-quote-discipline.md`
- `artifacts/checklists/official-voter-information-print-material-checklist.md`
- `artifacts/templates/official-voter-information-print-material-payload.json`

## Why this exists (bounded)

The archive already treats webpages, FAQs, hotlines, short-form alerts, and media releases as governed delivery layers.
That still leaves a highly persistent public lane: **official print and print-portable voter-information artifacts**.
In practice, many jurisdictions rely on flyers, postcards, brochures, handouts, pocket guides, infographic cards, or downloadable PDFs to explain deadlines, voting options, locations, ID rules, accessibility help, or where to get official answers.
Those materials persist in ways that are structurally different from ordinary webpages: they get printed in batches, left in racks, photographed, screenshotted, emailed as attachments, mirrored by community partners, and recirculated after the current web answer has moved on.

Current official guidance is specific enough to justify a bounded control here.
EAC's current **Voter Education Design Toolkit** says election officials need best practices and templates for designing effective communication materials across varying jurisdictions.
The current **How to use the templates: Voter Education Toolkit** booklet says the toolkit is used to create flyers, social-media posts, pocket guides, brochures, booklets, postcards, and web content to educate observers and the public.
EAC's current **Election Facts Label Toolkit** describes a customizable infographic for sharing election facts and says it includes templates for both social media and print.
EAC's communications clearinghouse presents those materials as current maintainer resources, not as decorative extras.
EAC's current design guidance also says voter-information materials should be clear, understandable, accessible, and written in plain language.
And NASS's current `#TrustedInfo2026` posture still keeps election officials as the trusted source voters should look to when information is time-sensitive or action-changing.
(xref: `eac_voter_education_design_toolkit_page`; xref: `eac_how_to_use_templates_voter_education_toolkit_2024_pdf`; xref: `eac_election_facts_label_toolkit_2025_pdf`; xref: `eac_clearinghouse_resources_communications_page`; xref: `eac_effective_design_for_the_administration_of_federal_elections_page`; xref: `nass_trustedinfo_2026_page`)

So the bounded problem is not “archive every poster” and it is not “make every PDF a legal instrument.”
The bounded problem is simpler:
**if a jurisdiction uses printable artifacts to move voters toward action, how does it keep those artifacts subordinate to the current controlling official destination, and how does it later prove which edition of the handout or PDF the public actually received?**

## What this adds (and what it does not)

This document adds a compact **edition + linkback + stale-stock discipline** for official voter-information print materials.

It does **not** require every jurisdiction to print handouts, postcards, or booklets.
It does **not** require archiving every physical copy or preserving inventory logs for every stack of paper.
It does **not** replace:
- the underlying voter-question family in `292–343`,
- the office-routing lane in `305`,
- FAQ/help article controls in `365`,
- short-form alert controls in `366`,
- media-release controls in `367`, or
- poll-place-specific signage or statutory notices already governed inside more specific surface docs.

It adds one narrow rule:
**if the public is expected to rely on a printable or downloadable election-information artifact for action-changing guidance, that artifact should visibly identify its edition/time scope, point back to the current official destination, and carry a bounded withdrawal/superseding path when it stops controlling.**

## Distinct boundary from webpages, FAQs, alerts, and signage

A printable voter-information artifact is a distinct delivery layer because it is:
- designed to survive away from the originating webpage,
- often distributed through partners, counters, mailers, events, or front desks,
- regularly consumed as a detached PDF, image, or physical handout,
- and unusually prone to stale reuse after deadlines, office hours, site assignments, or procedures change.

This control is **not** the same thing as:
- a maintained FAQ/help article (`365`),
- a social/text/app alert (`366`),
- a press release or spokesperson statement (`367`),
- or a poll-site operational signage packet attached to a more specific site-status surface.

The printable artifact is a portable public answer surface fragment.
That portability is exactly why it needs a tight edition/linkback rule.

## Canonical-link floor

An action-changing print artifact should do one of two things:

1. **state a bounded fact and point directly to the current controlling official page / office / notice / FAQ/help path**, or
2. **route the reader to the official help path without pretending the printed piece itself carries the entire rule.**

This matters especially for:
- registration and update instructions,
- voting locations and hours,
- absentee request/return instructions,
- deadline reminders,
- accessibility or language-help materials,
- problem-reporting and rights-escalation cards,
- special-population explainers,
- and any community-distributed handout where the next safe step depends on current local facts.

Do not let a detached PDF or handout become the **only** place a material instruction lives.
The portable artifact may be the first thing a voter sees.
The linked official page, help route, or signed notice should still carry the fuller controlling answer.

## Minimal message shape for action-changing print artifacts

A print artifact does not need to be long, but it should usually make six things legible:

1. **what question it answers or what action it covers,**
2. **which election / jurisdiction / voters / locations are in scope,**
3. **which edition or issue date the reader is holding,**
4. **where the current official detail lives now,**
5. **where to get official help if the artifact is not enough,** and
6. **whether the artifact is time-bounded or may expire.**

That can be a footer, version line, QR code, short URL, “as of” stamp, or bounded “for the 2026 General Election only” note.
What it should not be is a floating PDF or photographed card with no scope, no date, no help path, and no way to tell whether it still controls.

## Edition, superseding, and stale-stock discipline

Print artifacts have a physical persistence problem.
Unlike webpages, they do not disappear when the CMS updates.
Old PDF attachments remain in inboxes.
Old postcards sit on counters.
Old flyers stay pinned to bulletin boards.
Community groups keep redistributing the older file because it still looks official.

So when a material public answer changes, the office should make the correction **explicit**.

That means:
- identify a bounded edition or issue date for action-changing print artifacts,
- publish a superseding artifact or linked correction when the earlier one no longer controls,
- withdraw or stale-mark older downloadable files when practical,
- and, where physical distribution matters, document a bounded stale-stock retirement instruction for front desks, partner organizations, or event tables.

Deletion may still be appropriate for accidental duplicates or obvious clerical mistakes.
But an action-changing handout that the public was expected to use should not silently vanish into “we changed the website” ambiguity.

## QR / shortlink / detached-copy discipline

A QR code or short URL can help re-anchor a detached artifact to the current controlling destination, but it should be used carefully.

Operationally, that means:
- the QR or shortlink should land on a current official page or official router path,
- the artifact should still remain understandable if the code cannot be scanned,
- crucial instructions should not be hidden only inside the QR destination,
- and the human-readable fallback help route should stay visible in print.

A printed piece should degrade gracefully.
“Scan here or you are lost” is not a safe election-information posture.

## Accessibility, language access, and partner-distribution parity floor

A print artifact is only operationally real if people can actually use it.
That means:
- readable typography and plain language,
- accessible downloadable variants where the jurisdiction offers downloads,
- translated or community-language parity where the jurisdiction maintains those variants,
- no action-changing content hidden only inside an image without equivalent text,
- and coordination with hotline/help routes so a partner-distributed handout never sends the reader to a dead end.

Do not let the printed postcard, translated flyer, accessible PDF, and linked FAQ/help page drift into different effective answers.

## Canonical digest artifacts

Publish **small digests of the print-material surface**, not warehouse logs.

- **Print Material Surface Digest (PMSD):** digest of the bounded policy payload for the printable voter-information lane.
- **Print Material Edition Digest (PMED):** digest of a specific action-changing printable artifact edition.
- **Print Material Superseding Digest (PMSD-2):** digest of an explicit correction or superseding print-material event.
- **Print/Web Parity Snapshot (PWPS):** optional digest tying the printable artifact to the linked page / FAQ / hotline / notice state.

## What belongs in the public print-material payload

Keep the payload **small, current-state oriented, and edition-aware**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `print_material_family_label`
- `delivery_role_note`
- `material_formats[]`
- `distribution_contexts[]`
- `action_sensitive_topics[]`
- `edition_and_scope_policy`
- `canonical_destination_policy`
- `detached_copy_policy`
- `withdrawal_and_superseding_behavior`
- `stale_stock_retirement_note`
- `accessibility_and_language_note`
- `public_help_route_uri`
- `public_help_route_phone`
- `latest_notice_uri`
- `last_verified_at`
- supersedes / superseded-by pointers

Do **not** publish by default:
- print-vendor internals,
- mailing-house logistics,
- recipient lists,
- analytics about who scanned which code,
- or exhaustive inventory counts for every paper copy.

## Verification questions for third parties

A verifier, journalist, observer, community partner, or court should be able to answer:
- Which printable voter-information lane was official at time `T`?
- Could an ordinary reader tell what jurisdiction/election/scope the artifact applied to?
- Did the artifact visibly identify an edition or issue date?
- Did it point back to the current official page/help route, or did it pretend to be a standalone rulebook?
- When the answer changed, was there an explicit superseding artifact or correction trail?
- Were translated, accessible, and partner-distributed variants kept aligned with the current official state?

## How this fits the family map

An official voter-information flyer, postcard, brochure, pocket guide, booklet, infographic card, or downloadable PDF is **not** a new canonical voter-question family bucket.
It is a delivery layer in front of the same underlying voter questions already modeled in `292–343`.

So the underlying question remains:
- where to vote,
- which deadline matters,
- which office/help path controls,
- how a ballot path works,
- what special-case rule applies,
- or where rights/safety escalation begins.

This document only says that, if a jurisdiction uses portable print artifacts to deliver those answers, the artifact should stay editioned, linked back to the current official destination, and explicit about how stale copies are superseded.

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/official-voter-information-print-material-payload.json`
- Operator quickcheck: `artifacts/checklists/official-voter-information-print-material-checklist.md`

## Sources (pinned IDs / lockfile IDs)

- EAC: Voter Education Design Toolkit page (xref: `eac_voter_education_design_toolkit_page`)
- EAC: How to use the templates — Voter Education Toolkit PDF (xref: `eac_how_to_use_templates_voter_education_toolkit_2024_pdf`)
- EAC: Election Facts Label Toolkit PDF (xref: `eac_election_facts_label_toolkit_2025_pdf`)
- EAC: Communications clearinghouse page (xref: `eac_clearinghouse_resources_communications_page`)
- EAC: Effective Design for the Administration of Federal Elections page (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`)
- NASS: #TrustedInfo2026 (xref: `nass_trustedinfo_2026_page`)
