# 370 — Official voter-information emails, newsletters, reminders, and forward-context discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **official outbound voter-information email artifacts**:
newsletters,
deadline reminders,
incident-related public email updates,
and similar messages sent from official election-office accounts or officially published mailing lanes.

It is not trying to archive every inbox event.
It is trying to keep one practical public-risk seam from going soft:
**what happens when a voter acts on a forwarded, screenshotted, printed, or attachment-only official email after the current controlling webpage, FAQ/help entry, notice, or office instruction has changed.**

It composes with:
- `docs/186-incident-communications-as-evidence.md`
- `docs/194-synthetic-media-and-comms-authenticity-minimum-controls.md`
- `docs/195-rumor-control-and-status-boards-as-verifiable-public-surfaces.md`
- `docs/199-official-surface-security-snapshots.md`
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
- `docs/368-official-voter-information-printable-handouts-flyers-postcards-and-edition-linkback-discipline.md`
- `artifacts/checklists/official-voter-information-email-surface-checklist.md`
- `artifacts/templates/official-voter-information-email-surface-payload.json`

## Why this exists (bounded)

The archive already treats webpages, FAQs, hotlines, broadcast alerts, press releases, print artifacts, and videos as governed voter-information delivery layers.
Email is the remaining obvious lane.
Inbox-delivered voter information behaves differently from a webpage or social post:
people forward it,
screenshot it,
print it,
keep attachments long after a deadline moved,
and may reply expecting the mailbox to function as real official help.

Current official guidance is specific enough to justify a bounded control here.
The current EAC/CISA **Enhancing Election Security Through Public Communications** guide says an effective communications plan can include **sending an email newsletter**, and its audience/format guidance explicitly lists **send newsletters and reminders by email** and **establish and monitor a general email account to answer questions** as election-office communication activities.
The same guide says election officials should communicate consistently throughout the year, keep voters aware of key deadlines and changes, and transition official email accounts to `.gov`.
The current EAC/CISA **Election Infrastructure Incident Response Communications Guide** separately treats email as an operational public-update channel by providing an email template for incident acknowledgement and saying further updates will be communicated through channels such as email, website, social media, and press releases.
EAC's current **Accessibility Checklist: Accessible Communications** says electronic documents include emails and emphasizes plain language plus accessible document practices.
EAC's current **Toolkits** page also makes the cross-channel point directly: messaging and graphics prepared for official election outreach may be reused for **emails, websites, flyers, posters, and other communications**.
And NASS's current `#TrustedInfo2026` posture still keeps election officials and their official materials as the trusted source voters should follow when information is timely or action-changing.
(xref: `eac_enhancing_election_security_public_comms_2024_pdf`; xref: `eac_incident_response_comms_guide_pdf`; xref: `eac_accessibility_checklist_accessible_communications_2024_pdf`; xref: `eac_toolkits_page`; xref: `nass_trustedinfo_2026_page`)

So the bounded problem is simple:
**if a jurisdiction expects the public to rely on official voter-information emails, how does it keep those emails subordinate to the current controlling official destination, and how does it later prove which emailed edition the public actually received?**

## What this adds (and what it does not)

This document adds a compact **sender-identity + canonical-link + forward-context + correction discipline** for official voter-information email surfaces.

It does **not** require every jurisdiction to run a newsletter.
It does **not** require publishing recipient lists, open/click metrics, or full delivery telemetry.
It does **not** replace:
- the underlying voter-question family in `292–343`,
- the office-routing lane in `305`,
- the escalation lane in `307`,
- the hotline/script discipline in `364`,
- the FAQ/help article discipline in `365`,
- the short-form alert discipline in `366`, or
- the portable print/download discipline in `368`.

It adds one narrow rule:
**if the public is expected to rely on official email newsletters, reminders, or update messages for action-changing election guidance, those emails should visibly identify the sending office, their scope and issue time, the current official destination that controls the answer, and the correction/superseding path when inbox copies stop controlling.**

## Distinct boundary

An official voter-information email surface is a distinct delivery layer because it is pushed directly into a recipient-controlled inbox, easy to forward out of context, likely to carry attachments, and likely to invite direct replies.
It is not the same thing as a short-form alert (`366`), a hotline (`364`), a printable/downloadable artifact (`368`), or ordinary one-off casework email about an individual record.

## Sender-identity and official-account floor

If an office is using email to move voters toward action, the sender identity should be legible and plausibly official.
Current EAC/CISA guidance explicitly tells offices to transition official email accounts to `.gov`.
(xref: `eac_enhancing_election_security_public_comms_2024_pdf`)

Operationally, an action-changing email surface should usually make four things stable:
- the official sending office name,
- the sender address or domain,
- the official reply/help route,
- and the linked official destination where the current answer lives now.

Do not make voters reverse-engineer whether a forwarded reminder came from a real office, an approved vendor lane, or something impersonating the office.

## Canonical-link floor

An action-changing voter-information email should do one of two things:

1. **state a bounded fact and point directly to the current controlling official page / notice / FAQ-help path / office route**, or
2. **route the reader to the official help path without pretending the email itself carries the full rule.**

This matters especially for deadline reminders, registration/update windows, polling-place or office changes, vote-by-mail instructions, accessibility/language announcements, incident updates, and any email likely to be forwarded after the local facts changed.

Do not let an old inbox copy become the **only** place a material instruction lives.
The email may be the first thing a voter sees.
The linked official page, notice, FAQ/help entry, or office-routing path should still carry the fuller controlling answer.

## Minimal message shape for action-changing emails

An official email does not need to be long, but it should usually make these things legible:
- what question, reminder, or change it covers,
- which election / jurisdiction / voters / locations are in scope,
- when it was issued,
- whether it is a reminder, operational update, incident notice, or evergreen guidance,
- where the current official detail lives now,
- and where to get official help if the email is not enough.

What it should not be is a floating forwarded email or screenshot with no date, no scope, no help route, and no way to tell whether the reader is holding a current answer or historical inbox residue.

## Attachments and forward-context discipline

Email surfaces are unusually prone to detached context.
A recipient may forward only the body text.
A screenshot may crop away the footer.
An attachment may be downloaded and recirculated without the email that introduced it.
An inline graphic may hold the key fact while the text stays vague.

So an action-changing email surface should keep the forward context **inside the artifact**, not only around it.
That means:
- do not hide crucial action-changing facts only inside inaccessible images,
- keep attachment editions or issue dates visible when attachments are meant to be relied on,
- point attachments and graphics back to the current official destination when practical,
- and make the core scope/time/help path visible enough that a forwarded copy still leaves the reader a safe next step.

This composes directly with `368`: a printable attachment should not become a detached mini-rulebook with no edition or linkback path.

## Correction and superseding discipline

Inbox copies linger.
So when a material public answer changes, the correction should be **explicit**.

That means:
- send or publish a superseding update when a prior action-changing email no longer controls,
- make the current official page/help destination easy to find from the corrected message,
- avoid relying only on silently updated web copy while the stale email remains in the wild,
- and preserve a bounded note about which email edition or campaign packet was superseded.

## Reply handling and casework boundaries

Current official guidance is clear enough to support a bounded boundary here.
The EAC/CISA public-communications guide says jurisdictions may establish and monitor a general email account to answer questions, and the incident guide includes explicit points of contact in its public email template.
(xref: `eac_enhancing_election_security_public_comms_2024_pdf`; xref: `eac_incident_response_comms_guide_pdf`)

So a published reply/help address can be real and monitored.
But action-changing answers should stay synchronized with the current FAQ/help page, hotline packet, and controlling official page, and record-specific, rights-sensitive, or time-critical matters should move to the correct official help/escalation lane rather than drifting inside a shared newsletter mailbox.

## Accessibility, language access, and parity floor

A voter-information email is only operationally real if people can actually use it.
EAC's accessibility checklist says electronic documents include emails, stresses plain language, and says inaccessible documents should be accompanied by an equivalent accessible text version, alternative file format, or the text in the email body itself.
(xref: `eac_accessibility_checklist_accessible_communications_2024_pdf`)

That means:
- plain language,
- accessible electronic-document practice,
- no crucial rule content trapped only inside inaccessible attachments,
- language-parity support where the jurisdiction otherwise maintains it,
- and convergence between the email, linked page/notice, FAQ/help article, hotline packet, and any attached portable artifact.

## Canonical digest artifacts

Publish **small digests of the email-surface lane**, not mailing-list exhaust.

- **Email Surface Digest (ESD):** digest of the bounded policy payload for the official voter-information email lane.
- **Email Edition Digest (EED):** digest of a specific action-changing newsletter / reminder / public-update edition.
- **Email Correction / Superseding Digest (ECSD):** digest of an explicit correction or superseding event for an emailed public update.
- **Email/Web Parity Snapshot (EWPS):** optional digest tying an email edition to the linked page / FAQ / hotline state.

## What belongs in the public email-surface payload

Keep the payload **small, current-state oriented, and forward-aware**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `email_family_label`
- `delivery_role_note`
- `sender_identities[]`
- `list_refs[]`
- `action_sensitive_topics[]`
- `sender_identity_policy`
- `canonical_destination_policy`
- `forward_context_policy`
- `attachment_policy`
- `correction_and_superseding_behavior`
- `reply_and_casework_boundary`
- `accessibility_and_language_note`
- `routing_fallback_uri`
- `routing_fallback_email`
- `routing_fallback_phone`
- `latest_notice_uri`
- `last_verified_at`
- supersedes / superseded-by pointers

Do **not** publish by default:
- recipient lists,
- individualized delivery logs,
- open/click analytics,
- full CRM or marketing-platform exports,
- sensitive reply content,
- or private record-specific correspondence.

## Verification questions for third parties

A verifier, journalist, observer, community partner, or court should be able to answer:
- Which official voter-information email lane was active at time `T`?
- Could an ordinary recipient tell which office sent the email and what scope it covered?
- Did the email point back to the current official destination, or pretend to be a standalone rulebook?
- If an attachment or forwarded copy detached from the webpage, did enough scope/time/help context survive for a safe next step?
- Was a later correction explicit?
- Did the email stay aligned with the linked page/notice, FAQ/help article, hotline packet, and other official help lanes?

## How this fits the family map

An official newsletter, reminder, or public-update email is **not** a new canonical voter-question family bucket.
It is a delivery layer in front of the same underlying voter questions already modeled in `292–343`.

So the underlying question remains:
- where to vote,
- which date or deadline controls,
- which office/help path is authoritative,
- how to request or return a ballot,
- what special-case path applies,
- or where rights/safety escalation begins.

This document only says that, if a jurisdiction uses official voter-information email lanes to deliver those answers, the inbox artifact should stay subordinate to the controlling official page/notice/help path and preserve a bounded correction trail.

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/official-voter-information-email-surface-payload.json`
- Operator quickcheck: `artifacts/checklists/official-voter-information-email-surface-checklist.md`

## Sources (pinned IDs / lockfile IDs)

- EAC/CISA: Enhancing Election Security Through Public Communications (xref: `eac_enhancing_election_security_public_comms_2024_pdf`)
- EAC/CISA: Election Infrastructure Incident Response Communications Guide (xref: `eac_incident_response_comms_guide_pdf`)
- EAC: Accessibility Checklist: Accessible Communications (xref: `eac_accessibility_checklist_accessible_communications_2024_pdf`)
- EAC: Toolkits (xref: `eac_toolkits_page`)
- NASS: #TrustedInfo2026 (xref: `nass_trustedinfo_2026_page`)
