# 367 — Official voter-information press releases, media advisories, and spokesperson quote discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **official voter-information materials distributed through press releases, public statements, media advisories, press briefings, and spokesperson quotes that are expected to shape what voters do next**.

It is not trying to turn every interview clip or newsroom mention into a full evidence packet.
It is trying to keep a specific public-risk seam from going soft:
**what happens when operational voter guidance travels to the public through media-facing official statements, and the quoted or clipped version starts acting like the rulebook even when the controlling page, notice, FAQ, or office path lives somewhere else.**

It composes with:
- `docs/186-incident-communications-as-evidence.md`
- `docs/194-synthetic-media-and-comms-authenticity-minimum-controls.md`
- `docs/195-rumor-control-and-status-boards-as-verifiable-public-surfaces.md`
- `docs/199-official-surface-security-snapshots.md`
- `docs/201-public-surface-parity-snapshots.md`
- `docs/203-official-channel-directory-as-evidence.md`
- `docs/205-cache-and-freshness-controls-for-public-surfaces.md`
- `docs/223-public-surface-capture-notes-and-reproducibility.md`
- `docs/248-accessibility-usability-and-language-access-as-integrity.md`
- `docs/305-election-office-contact-directories-office-hours-and-change-notices-as-evidence-surfaces.md`
- `docs/307-voting-issue-reporting-civil-rights-escalation-and-change-notices-as-evidence-surfaces.md`
- `docs/310-voter-facing-public-answer-surfaces-family-map-and-promotion-rules.md`
- `docs/364-official-voter-help-hotlines-call-center-script-packets-and-answer-version-discipline.md`
- `docs/365-official-voter-faqs-knowledge-base-articles-and-answer-edition-discipline.md`
- `docs/366-official-voter-information-broadcast-alerts-social-posts-and-linkback-discipline.md`
- `artifacts/checklists/official-voter-information-media-release-checklist.md`
- `artifacts/templates/official-voter-information-media-release-payload.json`

## Why this exists (bounded)

The archive already treats official webpages, FAQs, hotlines, automated assistants, and short-form alerts as governed voter-information surfaces.
That still leaves a durable gap: **many action-changing public answers are first encountered through a press release, a quoted spokesperson line, a media advisory, or a press-conference clip.**
Those materials are often screenshotted, excerpted, syndicated, or retold by reporters and campaigns long after the office published them.

Current official guidance is concrete enough to justify a narrow control here.
EAC's current **Communications 101** guidance distinguishes between **press releases**, which announce important developments through official authoritative documents that emphasize facts and detailed information, **public statements**, which respond to external events in a briefer spokesperson voice, and **media advisories**, which invite journalists to events such as press conferences, town halls, and forums.
The same guidance says election officials should use plain language, consider objective/audience/tactics, stay on message, and prefer proactive planning over reactive catch-up.
The current EAC/CISA **Election Infrastructure Incident Response Communications Guide** adds the operational edge: election offices should identify an official spokesperson, draft initial talking points, issue an initial public statement or press release, keep a regular update cadence, and update talking points for media interactions as conditions change.
That guide's holding-statement and public-information-release templates are even more explicit that, during active voting periods, public-facing statements should include clear instructions to affected voters, use the most current and accurate information, tailor detail to public consumption, and send the public back to the election office website and official contact path for more detail.
EAC's current design guidance reinforces the maintainability rule behind all of this by treating voter-information materials as communication products that should be clear, understandable, accessible, and plain-language, including online materials and post-election materials.
Meanwhile NASS's current `#TrustedInfo2026` initiative still points the public toward election officials as the trusted sources of election information rather than toward unaffiliated retellings.
(xref: `eac_communications_101_2023_pdf`; xref: `eac_communications_101_page`; xref: `eac_incident_response_comms_guide_pdf`; xref: `eac_effective_design_for_the_administration_of_federal_elections_page`; xref: `nass_trustedinfo_2026_page`)

So the bounded problem is not “make the press office authoritative,” and it is not “archive every article about an election.”
The bounded problem is simpler:
**if a jurisdiction uses media-facing official statements to tell voters what changed, how does it keep those materials subordinate to the current controlling official page/notice/help path, and how does it keep quoted or clipped statements from becoming stale standalone law?**

## What this adds (and what it does not)

This document adds a compact **media-release + quote-discipline layer** for official voter-information communications.

It does **not** require every jurisdiction to maintain a formal press office.
It does **not** require collecting media-monitoring analytics, clipping every article, or archiving entire interview recordings by default.
It does **not** replace:
- the official-channel directory in `203`,
- PublicNotice and incident bulletin objects in `186` and `290`,
- the anti-impersonation / comms-authenticity controls in `194`,
- the underlying voter-question family in `292–343`,
- the office-routing surface in `305`,
- the rights/safety escalation lane in `307`,
- the hotline script-packet discipline in `364`,
- the FAQ/help answer-edition discipline in `365`, or
- the short-form broadcast-alert discipline in `366`.

It adds one narrow rule:
**if voters, journalists, campaigns, partner organizations, or hotline staff are expected to rely on a press release, public statement, media advisory, or spokesperson quote for action-changing election information, that material should point back to the current controlling official destination and should not be the only place where the operative instruction exists.**

## Document-type boundaries

Keep four media-facing artifact types distinct:

1. **Press release** — the office's authoritative written announcement of a development, with enough factual detail and routing information to stand on its own as a bounded public update.
2. **Public statement / holding statement** — a shorter official reaction while facts are still developing; useful for acknowledging an incident, setting expectations, and routing people to the current official detail path.
3. **Media advisory** — an invitation or logistical notice for journalists about an event or briefing. It should not quietly become the only public home for an action-changing voter instruction.
4. **Spokesperson quote / briefing answer** — attributable voice and explanation from an official speaker. It can clarify, but it should not become a quote-only policy lane detached from the written official current-state surface.

The archive does not need separate numbered docs for each of those.
It needs a rule that keeps them from collapsing into one another.

## No quote-only rule changes

If a material voter instruction changes, the office should not rely on **a quoted spokesperson line, a livestream answer, or a press conference clip** as the only durable public expression of that change.

When a press interaction produces action-changing guidance — for example:
- a site closure or move,
- a same-day operational reroute,
- a deadline extension or court-driven exception,
- a changed absentee return instruction,
- a revised help path,
- a change in continuity measures during active voting,
- or a clarification that materially changes what affected voters should do now,

that guidance should also appear in a current official page, signed notice, FAQ/help article, hotline packet update, or equivalent written official destination that ordinary users can reach without depending on a reporter's summary.

The press-facing artifact may be the fastest delivery lane.
It should not be the only durable rule surface.

## Minimal message shape for action-changing media releases

A press release or public statement that may affect voter behavior should usually make six things legible:

1. **what changed or what incident is being addressed,**
2. **which election / jurisdiction / locations / voters are in scope,**
3. **when the statement was issued,**
4. **where the current controlling official detail lives,**
5. **what affected voters should do right now, if anything,** and
6. **where to get help or ask official follow-up questions.**

During active voting periods, the incident-response guidance is explicit that public-facing statements should include clear instructions to affected voters about how the incident may or may not affect election operations.
(xref: `eac_incident_response_comms_guide_pdf`)

That does not mean every release must become a giant FAQ.
It means the release should never leave the reader guessing whether the next authoritative step lives on the official website, in a signed notice, in the office-contact directory, or with a help line.

## Media advisory discipline

A media advisory is not a hidden rulebook.
If an advisory announces a press conference about a disruption, deadline, or location problem, it may summarize the topic.
But the operative voter instruction should still live in the current official page/notice/help path.

So a media advisory should usually:
- identify the event and purpose,
- point journalists and the public toward the current official information page,
- avoid burying a material voting instruction only inside the event invitation,
- and make clear when a later release, statement, or webpage will carry the controlling written update.

## Spokesperson and talking-points discipline

Current official guidance already expects offices to identify an official spokesperson and to update talking points for media interactions as incidents evolve.
That is the right abstraction here.

Operationally, that means:
- designate which spokesperson roles may speak for the office on voter-impacting incidents,
- keep current talking points aligned with the latest official page/notice/help state,
- avoid speculative answer drift in interviews and briefings,
- distinguish confirmed current instructions from still-developing facts,
- and route record-specific or legally sensitive edge cases back to the official help/secure channel instead of litigating them in an interview scrum.

A spokesperson is a delivery layer for the office's current state.
A spokesperson should not become a second, unsynchronized policy engine.

## Press briefing / conference capture floor

The archive does **not** require default archiving of full raw recordings.
But if a public briefing, interview, livestream, or press conference carries action-changing voter guidance, the office should preserve a **bounded durable written trail** of what controlled.

That usually means one of:
- a follow-up press release,
- a written public statement,
- an updated official webpage or FAQ/help article,
- a signed notice,
- or a compact transcript/summary page that quotes the operative instruction and links back to the controlling official destination.

The goal is simple: later reviewers should not need a third-party clip compilation to reconstruct the office's official public answer at time `T`.

## Correction, superseding, and stale-release discipline

Media releases persist.
They get mirrored, quoted, indexed by search engines, and copied into newsletters, blogs, broadcasts, and AI answers.
So when a material public answer changes, the correction should be **explicit**.

That means:
- publish a superseding release or linked correction when the earlier media-facing statement no longer controls,
- update the newsroom or press page so ordinary readers can find the current state,
- avoid silent copy edits that erase what the public was previously told,
- and preserve a bounded correction trail so later reviewers can reconstruct which statement controlled when.

Deletion may still be appropriate for accidental duplicates or obvious clerical mistakes.
But an action-changing release should not disappear into “we updated the page” ambiguity if people were expected to act on it.

## Accessibility, language access, and channel parity floor

A media-facing release is only operationally real if the public can use it.
That means:
- plain-language summaries rather than jargon-heavy crisis prose,
- accessible HTML or accessible document publication,
- captions or transcripts when the controlling update is delivered through live or recorded video,
- no material instruction hidden only inside a graphic or lower-third,
- and parity across the linked page/notice/help article and any translated or accessible companion surfaces the office maintains.

Do not let the press lane outrun the voter-help lane.
If the release tells the press one thing while the FAQ/help page, hotline packet, or office directory still says another, the public state is already forked.

## Canonical digest artifacts

Publish **small digests of the media-release surface**, not whole media-monitoring systems.

- **Media Release Surface Digest (MRSD):** digest of the bounded newsroom / press-surface policy payload.
- **Media Release Message Digest (MRMD):** digest of a release, statement, or written briefing summary state that carried action-changing voter information.
- **Media Release Superseding Digest (MRSD-2):** digest of the explicit correction or superseding release event.
- **Media Parity Snapshot (MPS):** optional digest tying the media-facing update to the linked webpage / FAQ / hotline packet / signed notice state.

## What belongs in the public media-release payload

Keep the payload **small, current-state oriented, and delivery-layer specific**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `media_release_family_label`
- `delivery_role_note`
- `channel_refs[]`
- `supported_document_types[]`
- `action_sensitive_topics[]`
- `canonical_destination_policy`
- `spokesperson_and_quote_policy`
- `briefing_capture_policy`
- `correction_and_superseding_behavior`
- `media_inquiry_contact`
- `public_help_route_uri`
- `public_help_route_phone`
- `rights_escalation_uri`
- `latest_notice_uri`
- `last_verified_at`
- supersedes / superseded-by pointers

Do **not** publish by default:
- reporter contact lists,
- private press inquiries,
- unpublished draft talking points,
- raw full-length recordings when a bounded written artifact is sufficient,
- or media-monitoring analytics.

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:
- Which official newsroom / press-release / spokesperson lane was in scope at time `T`?
- Did the action-changing media-facing statement point to the current controlling official destination?
- Was the operative voter instruction also reachable in an ordinary written official page/notice/help surface, or only through quoted remarks?
- Did the office clearly distinguish a media advisory from a current rule update?
- Were later corrections explicit, or did the office rely on quiet edits and disappearing clips?
- Could an ordinary reader tell what to do next and where to get official help?

## How this fits the family map

An official press release, media advisory, public statement, or spokesperson quote is **not** a new canonical voter-question family bucket.
It is a delivery layer in front of the same underlying voter questions already modeled in `292–343`.

So the underlying question remains:
- where to vote,
- which deadline matters,
- which office/help path controls,
- how a ballot path changed,
- what special-case rule applies,
- or where rights/safety escalation begins.

This document only says that, if a jurisdiction uses media-facing official communications to deliver those answers, the press/media lane should stay subordinate to the current written official destination and preserve a bounded correction trail.

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/official-voter-information-media-release-payload.json`
- Operator quickcheck: `artifacts/checklists/official-voter-information-media-release-checklist.md`

## Sources (pinned IDs / lockfile IDs)

- EAC: Communications 101 page (xref: `eac_communications_101_page`)
- EAC: Communications 101 booklet PDF (xref: `eac_communications_101_2023_pdf`)
- EAC/CISA: Election Infrastructure Incident Response Communications Guide (xref: `eac_incident_response_comms_guide_pdf`)
- EAC: Effective Design for the Administration of Federal Elections (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`)
- NASS: #TrustedInfo2026 (xref: `nass_trustedinfo_2026_page`)
