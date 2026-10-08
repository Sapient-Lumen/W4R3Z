# 364. Official voter-help hotlines, call-center script packets, and answer-version discipline

**Track:** Shared / Public surfaces

This document treats the **public answer surface for “what did the official phone/help line tell voters at time `T`, through which script/version, and what happened when the answer was uncertain, stale, or the line was degraded?”** as an **evidence surface**.

The goal is not to publish raw call recordings, internal CRM tickets, staff rosters, private extensions, or full case notes.
The goal is to make six things hard to fake after the fact:

1. **Which public voter-help number or hotline the jurisdiction identified as official** for election scope `E`,
2. **Which answer script packet / FAQ packet / quick-reference sheet was in force** for action-changing questions,
3. **Which topics required exact scripted language, warm transfer, or stop-on-conflict behavior**,
4. **Whether hotline answers stayed aligned with the current official pages, signed notices, and office-routing surface**,
5. **When the script, hours, service state, or fallback path changed**, and
6. **Whether the jurisdiction can later prove what the hotline was supposed to say without relying on operator memory.**

It composes with:
- `docs/186-incident-communications-as-evidence.md`
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
- `docs/363-automated-voter-information-assistants-no-authority-lift-and-answer-trace-discipline.md`
- `artifacts/checklists/voter-help-hotline-script-packet-checklist.md`
- `artifacts/templates/voter-help-hotline-script-packet-payload.json`

## Why this exists (bounded)

The archive already treats websites, signed notices, directories, FAQ pages, rumor-control pages, and special-case voter-help pages as public answer surfaces. But many real voter journeys still pass through **a phone number staffed by election-office workers, temporary call-center staff, poll-worker help desks, or other official public-facing teams answering the phones**.

Current official guidance is enough to justify a narrow control here. EAC's current voter FAQ reiterates that election administration is highly decentralized and that the best practical registration and voting information comes from the local elections office. EAC's current communications clearinghouse likewise frames public communication as an operational discipline, highlighting FAQ resources, communication toolkits, incident-response communications guidance, and accessible-communications guidance in one current maintainer lane. EAC's current FAQ toolkit says local election officials are the best source of trusted information and explicitly treats website FAQs and associated public messaging as a maintained official answer surface rather than improvised prose. EAC's current voter-education topics document goes one step more operational: it says voter-information materials should include the election office contact information, including phone and TTY, and should tell voters how to find assigned or nearby voting locations. EAC's provisional-voting best-practices guidance makes the phone/help lane explicit too: it says jurisdictions should use election-office web and social media sites for helpful voting information and should also provide a toll-free number voters can use to contact election offices directly with questions. NASS's current `#TrustedInfo2026` posture keeps the legitimacy baseline simple by promoting state and local election officials as the trusted sources of election information. (xref: `eac_voter_faqs_page`; xref: `eac_clearinghouse_resources_communications_page`; xref: `eac_best_practices_faqs_election_officials_page`; xref: `eac_voter_education_topics_editable_content_document_2024_pdf`; xref: `eac_best_practices_provisional_voting_2023_pdf`; xref: `nass_trustedinfo_2026_page`)

Incident guidance makes the same point from the failure side. The current EAC/CISA incident-response communications guide says staff should be kept appropriately informed so they can respond to questions effectively, tells jurisdictions to distribute talking points to public-facing teams such as the team answering the phones, and says official websites, social-media channels, text messages, and smartphone applications should be used in concert with other non-digital communication channels. The same guide's holding-statement templates require current contact information and, during active voting periods, clear instructions for affected voters. If the public hotline is answering action-changing election questions, it is not an informal courtesy layer. It is part of the effective official answer surface. (xref: `eac_incident_response_comms_guide_pdf`)

Accessibility and language access remain load-bearing. EAC's current accessibility checklist explicitly covers in-person conversations and meetings, including telephone interactions, and says auxiliary aids and services should be provided for people who have communication disabilities, including TTY text telephones. That means a hotline surface is not trustworthy if it is phone-only without relay/accessibility disclosure, if it quietly lacks a usable accommodation path, or if the office's accessible communications discipline stops at the website while the live help line becomes the inaccessible exception. (xref: `eac_accessibility_checklist_accessible_communications_2024_pdf`)

So the bounded problem here is not “record every call” and it is not “build a universal national script.”
The bounded problem is simpler:
**if a jurisdiction exposes an official voter-help hotline or phone-answer lane, how does it prove what that lane was supposed to tell the public, and how does it keep that lane synchronized with the current official answer surfaces that actually govern the result?**

## What this adds (and what it does not)

This document adds a compact **script-packet + answer-version discipline** for official voter-help hotlines and other public phone-answer lanes.

It does **not** require every jurisdiction to run a hotline.
It does **not** require publishing raw recordings or full transcripts.
It does **not** require a heavyweight call-center platform.
It does **not** replace:
- the office-routing surface in `305`,
- the rights/safety escalation lane in `307`,
- the underlying voter-question families in `292–343`, or
- the no-authority-lift / answer-trace rules for automated assistants in `363`.

It only adds one narrow rule:
**if the public is expected to rely on an official phone/help number for action-changing voting answers, the office should maintain a bounded, versioned script packet and be able to show which version controlled at time `T`.**

## Script-packet floor

If a hotline, call center, election-day help desk, or office phone tree is an official public-help channel, the jurisdiction should maintain a compact **script packet** (or equivalent FAQ/talking-points packet) for action-changing topics.

That packet may be a short document, controlled FAQ card set, or approved quick-reference sheet.
It does not need to be ornate.
But it should be versioned and bounded enough to answer:
- which public number/path this packet governs,
- which election scope it covers,
- which official anchors it depends on,
- which topics are safe to answer directly,
- which topics require exact phrasing,
- which topics require transfer or escalation,
- and when the packet was last verified.

## Action-changing answer-version rule

For action-changing questions, a public-facing staff answer should be traceable to a **current approved packet version** or to an explicit real-time confirmation from the responsible office.

This matters especially for:
- dates and deadline semantics,
- polling-place, vote-center, early-voting, or drop-box locations and hours,
- voter-ID requirements and alternatives,
- registration status/update/same-day-registration paths,
- absentee or replacement-ballot request/return rules,
- special-case voter paths,
- office closures, emergency reroutes, or degraded-service incidents,
- and any question whose next step depends on the currently responsible office.

The hotline should not depend on tribal memory, a stale laminated sheet, or “what we told callers yesterday.”
If the answer changes what the voter should do next, the hotline should be able to say which current packet version or official notice it is following.

## Conflict, uncertainty, and transfer discipline

A public phone/help lane should inherit the archive's broader conflict discipline rather than improvising through ambiguity.

If the current official materials are incomplete, stale, or materially conflicting, the correct move is not a confident synthetic answer.
The correct move is to:
- stop on the conflict,
- identify the controlling office/path that can resolve it now,
- hand the caller to the right office or rights/safety lane when needed,
- and update the packet after the conflict is resolved.

This is especially important for emergency closures, same-day office moves, court-order changes, and niche special-case questions where the wrong answer can cause a missed voting window.

## Incident and degraded-service posture

Phone/help lanes become more—not less—important when normal operations are unstable.

So when an incident affects election operations, jurisdictions should treat hotline materials as a change-controlled public-surface artifact:
- updated talking points should be distributed to the teams answering the phones,
- holding statements should give clear instructions to affected voters when active voting is underway,
- hotline outage or overload conditions should produce an alternate official path,
- and service-state changes should be explicit instead of leaving callers to infer whether the old number, old hours, or old instructions still control.

## Accessibility, language access, and after-hours honesty

A public help number is not operationally real unless the office is candid about how it can actually be used.

Minimum publishable facts include:
- the public phone/help number,
- hours and timezone semantics,
- whether a TTY / relay / accessible path exists,
- languages available or the official alternate language-help path,
- what happens after hours,
- and which office/path controls if the line is unavailable or overloaded.

Do not imply a live-answer capability that does not exist.
Do not advertise “contact us” as the fallback while hiding that the line is closed until after the deadline passes.

## Minimal claim-set

A jurisdiction can publish a compact, verifiable claim-set:

1. **Official hotline claim:** the jurisdiction identified one or more public phone/help numbers or answer lanes as official for scope `E`.
2. **Script-version claim:** action-changing answers were governed by a bounded versioned packet, FAQ card set, or talking-points bundle.
3. **Anchor claim:** the packet identified the current official pages, notices, or office-routing artifacts it relied on.
4. **Transfer/escalation claim:** the packet distinguished direct-answer topics from topics that require warm transfer, office routing, or `307`-style escalation.
5. **Service-state claim:** hours, after-hours behavior, outages, or degraded-service fallback paths were explicit.
6. **Change-log claim:** material script changes, emergency reroutes, and hotline service changes produced explicit superseding events rather than silent edits.
7. **Parity/accessibility claim:** the website, FAQ surface, hotline script packet, and signed notices converged on the same effective public state in accessible and, where required, language-appropriate form.

## Canonical digest artifacts

Publish **digests of the public hotline/help surface**, not raw call records.

- **Voter Help Hotline Surface Digest (VHHSD):** digest of the bounded public hotline/help payload for a scope.
- **Hotline Script Packet Digest (HSPD):** digest of the current approved script/talking-points packet for action-changing topics.
- **Hotline Script Change Notice Digest (HSCND):** per-event digest when the script packet changes because the public answer changed.
- **Hotline Service Availability Snapshot (HSAS):** optional digest for bounded facts about hotline outage, overload, hours change, callback delay, or alternate official path.
- **Hotline Parity Snapshot (HPS):** optional digest binding hotline guidance to the current website / FAQ / notice state.

## What belongs in the public hotline/help payload

Keep the payload **small, action-relevant, and current-state oriented**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `hotline_label`
- `hotline_public_number`
- `public_hours`
- `time_zone`
- `relay_or_tty_path`
- `languages_available`
- `official_source_anchors[]`
- `script_packet_version`
- `script_packet_digest`
- `action_sensitive_topics[]`
- `required_transfer_rules[]`
- `degraded_service_fallback`
- `service_state`
- `latest_notice_uri`
- `last_verified_at`
- supersedes / superseded-by pointers

Do **not** publish by default:
- raw call recordings or transcripts,
- internal extension trees,
- personal staff numbers,
- CRM ticket IDs or case notes,
- staffing rosters,
- threat-report details,
- or internal coaching notes that do not change the public answer.

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:
- Which official public help number or hotline was in force at time `T`?
- Can we reconstruct what the office intended that lane to say for action-changing topics at time `T`?
- Which packet/version or official notice controlled the answer?
- Did hotline guidance match the current website / FAQ / signed notice state?
- Were conflicts, outages, or after-hours limits explicit, or hidden behind generic “contact us” language?
- Was there a usable accessible / relay / language-help path for callers who could not use the default line?

## How this fits the family map

A hotline script packet is **not** a new canonical voter-question family bucket.
It is a delivery surface that sits in front of the existing question families already modeled in `292–343`.

So the family question remains:
- `292` asks where the polling place is,
- `304` asks how to request a mail ballot,
- `305` asks which office is authoritative and reachable,
- `307` asks where to escalate when ordinary help fails,
- `323–343` ask the narrow special-case questions,
- and `363` governs automated assistants that may sit beside or in front of those same answer paths.

This document only says that, if a human phone/help lane is part of the official public answer path, it should be versioned, synchronized, and later-reconstructible rather than living only in operator recollection.

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/voter-help-hotline-script-packet-payload.json`
- Operator quickcheck: `artifacts/checklists/voter-help-hotline-script-packet-checklist.md`

## Sources (pinned IDs / lockfile IDs)

- EAC: Voter FAQs (xref: `eac_voter_faqs_page`)
- EAC: Clearinghouse Resources on Communications (xref: `eac_clearinghouse_resources_communications_page`)
- EAC: Best Practices: FAQs for Election Officials (xref: `eac_best_practices_faqs_election_officials_page`)
- EAC: Voter Education Topics: Editable Content Document (xref: `eac_voter_education_topics_editable_content_document_2024_pdf`)
- EAC: Best Practices: Provisional Voting (xref: `eac_best_practices_provisional_voting_2023_pdf`)
- EAC/CISA: Election Infrastructure Incident Response Communications Guide (xref: `eac_incident_response_comms_guide_pdf`)
- EAC: Accessibility Checklist: Accessible Communications (xref: `eac_accessibility_checklist_accessible_communications_2024_pdf`)
- NASS: #TrustedInfo2026 (xref: `nass_trustedinfo_2026_page`)
