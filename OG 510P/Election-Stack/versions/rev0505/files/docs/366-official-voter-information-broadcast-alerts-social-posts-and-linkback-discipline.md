# 366 — Official voter-information broadcast alerts, social posts, and linkback discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **official outbound voter-information alerts** distributed through public social-media accounts, subscriber text lists, smartphone app notifications, and similar short-form broadcast channels.

It is not trying to turn every post into a full evidence packet.
It is trying to keep a very specific public-risk seam from going soft:
**what happens when the first or fastest thing a voter sees is a short-form official alert rather than the full controlling webpage, notice, FAQ article, or office directory entry.**

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
- `artifacts/checklists/official-voter-information-broadcast-alert-checklist.md`
- `artifacts/templates/official-voter-information-broadcast-alert-payload.json`

## Why this exists (bounded)

The archive already treats official webpages, directories, signed notices, FAQ/help articles, hotlines, and automated assistants as public-answer surfaces.
That still leaves a last-mile delivery seam: **many voters encounter official election information through short-form alerts first** — a social post, a text alert, or an app notification that says a site changed, a window opened, a deadline is near, or the office has new instructions.

Current official guidance is specific enough to justify a narrow control here.
The current EAC/CISA **Election Infrastructure Incident Response Communications Guide** says official websites, blogs, social media sites, text messages (SMS), and smartphone applications are effective tools to advise and inform the public at scale, and it says they should be used in concert with other communication channels.
The same guide says jurisdictions should distribute talking points to public-facing teams, keep communication regular as conditions change, and use branding consistently so the public can recognize legitimate official messages.
NASS's current `#TrustedInfo2026` initiative makes the legitimacy baseline simpler still by driving voters directly to election officials' websites, social-media pages, and materials for credible, timely election information.
EAC's current communications clearinghouse treats the **Election Official Social Media Toolkit** and the **Accessibility Checklist: Accessible Communications** as current maintainer resources rather than optional decoration.
That social-media toolkit is not just generic marketing material: it includes sample posts that route people to official voting-location and election-information links, provides alt text, and treats community management as a trust-bearing practice.
Its community-management section says an election office's social-media presence becomes a trusted source of information for constituents, and its FAQ guidance says offices should respond promptly with accurate information or direct users to trusted sources while monitoring comments regularly.
Meanwhile EAC's accessibility checklist explicitly includes social-media posts in the accessible-communications lane.
(xref: `eac_incident_response_comms_guide_pdf`; xref: `nass_trustedinfo_2026_page`; xref: `eac_clearinghouse_resources_communications_page`; xref: `eac_election_official_social_media_toolkit_2024_pdf`; xref: `eac_accessibility_checklist_accessible_communications_2024_pdf`)

So the bounded problem is not “make social media authoritative,” and it is not “archive every platform event.”
The bounded problem is simpler:
**if a jurisdiction uses short-form official alerts to move voters toward action, how does it keep those alerts subordinate to the current controlling official page/notice/office path, and how does it later prove what the public alert actually said?**

## What this adds (and what it does not)

This document adds a compact **linkback + superseding-alert discipline** for official short-form outbound voter-information channels.

It does **not** require every jurisdiction to use social-media accounts, text alerts, or app notifications.
It does **not** require collecting platform analytics or storing direct-message archives.
It does **not** replace:
- the official-channel directory in `203`,
- the anti-impersonation / comms-authenticity controls in `194`,
- the underlying voter-question family in `292–343`,
- the office-routing surface in `305`,
- the rights/safety escalation lane in `307`,
- the hotline script-packet discipline in `364`, or
- the FAQ/help answer-edition discipline in `365`.

It only adds one narrow rule:
**if the public is expected to rely on short-form official alerts for action-changing election information, each alert should stay visibly subordinate to a current official page, signed notice, FAQ/help article, or office-routing path that actually controls the answer.**

## Canonical-link floor

For an action-changing alert, the short-form message should do one of two things:

1. **state a bounded fact and link or point directly to the current controlling official destination**, or
2. **route the user to the official office/help path without pretending the short-form channel itself carries the full rule.**

This matters especially for:
- polling-place, vote-center, early-voting, or drop-box changes,
- office closures or reroutes,
- same-day operational incidents,
- deadline reminders,
- registration/update windows,
- absentee or replacement-ballot instructions,
- accessibility/language announcements, and
- any alert where the next safe step depends on current local facts.

Do not let a platform post become the **only** place the voter can find a material rule change.
The short-form channel is a transport and visibility layer.
The linked official page, signed notice, FAQ/help entry, or office-routing surface is what should carry the fuller controlling instruction.

## Minimal message shape for action-changing alerts

A short-form official alert does not need to be long, but it should usually make five things legible:

1. **what changed or what action window matters,**
2. **which election/jurisdiction/scope it applies to,**
3. **when the alert was issued,**
4. **where the current official detail lives,** and
5. **where to go for help if the alert is not enough.**

For very short channels, that may mean a brief statement plus a canonical official link or controlled vanity path.
For richer channels, it may mean a card/post that includes the bounded fact, official link, and fallback help number.

What it should not mean is compressing a complex legal edge case into a slogan-like post that readers later port outside the intended jurisdiction or time window.

## Correction, superseding, and stale-post discipline

Short-form alerts have a nasty persistence problem: old posts get screenshotted, re-shared, cached, quoted in chat, or left pinned after they stopped controlling.
So when a material public answer changes, the office should make the correction **explicit**.

That means:
- publish a superseding alert, reply, or linked correction when the earlier alert no longer controls,
- point the reader toward the current official page/notice rather than relying on deletion alone,
- retire, unpin, or visibly stale-mark short-lived alerts when practical,
- and preserve a bounded correction trail so later reviewers can reconstruct which public alert was current at time `T`.

Deletion may still be appropriate for duplicates, abuse, or obvious posting mistakes.
But an action-changing alert that materially affected public routing should not be treated as though it never existed.
The public needs a visible “current state now controls here” path.

## Comment, reply, and DM discipline

Where a platform allows comments, replies, or direct messages, the jurisdiction should keep those interactions inside a bounded role.

The current official guidance points in that direction already: respond promptly with accurate information or direct users to trusted sources, monitor comments regularly, and use moderation tools consistently when platform rules are violated.
(xref: `eac_election_official_social_media_toolkit_2024_pdf`)

Operationally, that means:
- do not do record-specific casework in public comments,
- do not invite voters to send sensitive documents, protected-address facts, or personal identifiers through ordinary social DMs,
- route sensitive or record-specific matters to the official secure/help channel,
- and keep comment/reply guidance synchronized with the current FAQ/help articles and hotline script packets.

A short-form broadcast lane should help voters reach the controlling answer.
It should not become a shadow case-management system.

## Accessibility, language access, and parity floor

A short-form alert is only operationally real if it remains usable across the modes the public actually encounters.
That means:
- accessible text or alt text for image-based posts,
- no crucial rule content hidden only inside decorative images,
- parity between the short-form alert and the linked official page/notice,
- language variants where the jurisdiction otherwise provides them or they are required,
- and consistent effective public state across website, FAQ/help article, hotline packet, and short-form alert.

Do not let the image card say one thing, the caption another, the FAQ a third, and the hotline packet a fourth.
If the channel is official, it should converge on the same current public answer.

## Minimal claim-set

A jurisdiction can publish a compact, verifiable claim-set:

1. **Official broadcast-channel claim:** the office identified one or more official short-form broadcast channels for scope `E`.
2. **Linkback claim:** action-changing alerts routed to a current official page, signed notice, FAQ/help entry, or office/help path.
3. **Message-shape claim:** action-changing alerts carried a bounded statement of scope, time, and current official destination.
4. **Superseding claim:** material changes produced an explicit correction/superseding trail rather than only silent disappearance.
5. **Interaction claim:** comment/reply/DM handling stayed inside published trusted-source and secure-channel boundaries.
6. **Parity/accessibility claim:** short-form alert, linked page/notice, FAQ/help article, hotline packet, and other official public-help lanes converged on the same effective public state.

## Canonical digest artifacts

Publish **small digests of the broadcast-alert surface**, not whole platform exports.

- **Broadcast Alert Surface Digest (BASD):** digest of the bounded channel registry + policy payload for the alert surface.
- **Broadcast Message Digest (BMD):** digest of an action-changing alert message state or bounded campaign packet.
- **Broadcast Superseding Notice Digest (BSND):** digest of the explicit correction/superseding event when a material alert changed.
- **Broadcast Parity Snapshot (BAPS):** optional digest that ties the short-form alert to the linked webpage / FAQ / hotline packet state.

## What belongs in the public broadcast-alert payload

Keep the payload **small, current-state oriented, and delivery-layer specific**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `broadcast_family_label`
- `delivery_role_note`
- `channel_refs[]`
- `action_sensitive_topics[]`
- `canonical_destination_policy`
- `message_expiry_policy`
- `correction_and_superseding_behavior`
- `interaction_policy`
- `accessibility_and_language_note`
- `routing_fallback_uri`
- `routing_fallback_phone`
- `rights_escalation_uri`
- `latest_notice_uri`
- `last_verified_at`
- supersedes / superseded-by pointers

Do **not** publish by default:
- raw platform analytics,
- full comment archives,
- private messages,
- staff-device details,
- internal moderation notes,
- or per-user engagement traces.

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:
- Which official short-form channel sent the alert at time `T`?
- Did the action-changing alert point to the current controlling official destination?
- Was a later correction explicit, or did the office rely only on deletion or quiet replacement?
- Did the short-form alert match the linked page/notice, FAQ/help article, and hotline packet state?
- Were replies/DMs kept inside trusted-source and secure-channel boundaries?
- Could an ordinary user tell where to go next when the short-form message was not enough by itself?

## How this fits the family map

An official social post, text alert, or app notification is **not** a new canonical voter-question family bucket.
It is a delivery layer in front of the same underlying voter questions already modeled in `292–343`.

So the underlying question remains:
- where to vote,
- which date or deadline controls,
- which office is authoritative,
- how to request or return a ballot,
- what special-case path applies,
- or where rights/safety escalation begins.

This document only says that, if a jurisdiction uses short-form official broadcast channels to deliver those answers, the channel should stay subordinate to the controlling official page/notice/help path and preserve a bounded correction trail.

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/official-voter-information-broadcast-alert-payload.json`
- Operator quickcheck: `artifacts/checklists/official-voter-information-broadcast-alert-checklist.md`

## Sources (pinned IDs / lockfile IDs)

- EAC: Clearinghouse Resources on Communications (xref: `eac_clearinghouse_resources_communications_page`)
- EAC: Accessibility Checklist: Accessible Communications (xref: `eac_accessibility_checklist_accessible_communications_2024_pdf`)
- EAC/CISA: Election Infrastructure Incident Response Communications Guide (xref: `eac_incident_response_comms_guide_pdf`)
- EAC: Election Official Social Media Toolkit (xref: `eac_election_official_social_media_toolkit_2024_pdf`)
- NASS: #TrustedInfo2026 (xref: `nass_trustedinfo_2026_page`)
