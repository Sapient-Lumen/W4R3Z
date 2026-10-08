# 629 — Official voter-information platform media authenticity-cue packet presence avatars cursors participants and non-governing wrapper-participation-state firewall

**Track:** Shared / Public surfaces

This document covers a narrow packet-wrapper problem:
**later packets can preserve collaborator avatars, anonymous-animal / guest chips, presence cursors, “who’s here now” indicators, reviewer-participant lists, review-status badges, or similar visible wrapper participation-state layers around same-route detached derivatives, and later readers can start mistaking that participation posture for source authorship, official approval, current office attention, governing participation, or the packet's governing member.**

It composes with:
- `docs/194-synthetic-media-and-comms-authenticity-minimum-controls.md`
- `docs/523-official-voter-information-platform-media-boundary-quickmap-and-duplicate-firewall.md`
- `docs/529-official-voter-information-platform-media-chain-heads-current-control-and-closeout-discipline.md`
- `docs/530-official-voter-information-platform-media-chain-citations-head-first-reference-and-historical-leg-scoping-discipline.md`
- `docs/591-official-voter-information-platform-media-authenticity-cue-observation-assembly-cross-state-composites-and-no-faux-single-state-firewall.md`
- `docs/600-official-voter-information-platform-media-authenticity-cue-detached-derivative-family-quickmap-mixed-packets-and-anti-fragmentation-firewall.md`
- `docs/616-official-voter-information-platform-media-authenticity-cue-packet-review-threads-comment-replies-and-non-governing-wrapper-discourse-firewall.md`
- `docs/619-official-voter-information-platform-media-authenticity-cue-packet-sharing-permissions-link-access-and-non-governing-wrapper-access-state-firewall.md`
- `docs/620-official-voter-information-platform-media-authenticity-cue-packet-notifications-activity-feeds-and-non-governing-wrapper-event-state-firewall.md`
- `docs/624-official-voter-information-platform-media-authenticity-cue-packet-details-panes-properties-owner-location-and-non-governing-wrapper-information-state-firewall.md`

## What this is for

Use `629` when a later packet preserves or reenacts a **visible wrapper participation-state layer** around same-route detached derivatives:
- collaborator avatars or named participant chips,
- anonymous-animal / anonymous-viewer / guest indicators,
- presence cursors, edit-location flags, or “currently here” markers,
- reviewer-participant lists or review-status badges,
- active-collaborator counts,
- or similar later packet presence / participation posture.

Those participation surfaces are real packet facts and should be preserved honestly.
But they are still **later wrapper-added participation posture**, not automatic proof of:
- source authorship,
- source endorsement,
- official approval,
- current office attention,
- governing participation,
- or the packet's governing member.

Current primary-source guidance is already enough to justify one bounded participation-state bridge.
Google Docs Editors help explains that viewers in a shared file may appear by name or as anonymous animals and that multiple anonymous animals can appear for reasons that do not cleanly identify a unique present collaborator.
Microsoft Support explains that collaborative Microsoft 365 files can show who else is in the document and where they are working through presence indicators.
Adobe Acrobat help explains that review workflows can show participants and review status while comments and review progress continue around the shared file.
That is enough for one bounded firewall here.
(xref: `google_docs_anonymous_or_unknown_people_in_a_file_help_page`; xref: `microsoft_collaborate_with_others_help_page`; xref: `adobe_acrobat_send_pdf_to_others_for_review_help_page`)

`629` exists so maintainers can say:
**this packet preserved a later participation-state layer around same-route detached derivatives, and that layer mattered for how later readers interpreted the packet, but the participation layer itself does not govern the packet and does not silently prove source authorship, official approval, current office attention, governing participation, or the governing member.**

## Why this is distinct

`616` asks whether a later packet preserved **review discourse** — comment threads, replies, task-like notes, or resolved-comment history.

`619` asks whether a later packet preserved **access posture** — share dialogs, link scopes, role matrices, or permission settings.

`620` asks whether a later packet preserved **event posture** — notification cards, activity feeds, or alert emails.

`624` asks whether a later packet preserved **information posture** — details panes, info cards, owner/location/size/type fields, or similar file-information blocks.

`629` asks a different question:
**did a later packet add or preserve a visible participation layer — avatars, anonymous-viewer chips, presence cursors, reviewer-participant lists, or review-status badges — and did later readers start overreading that layer as if it proved source authorship, official approval, current office attention, governing participation, or the packet's governing member?**

If the real problem is review discussion content, use `616`.
If the real problem is permissions or audience scope, use `619`.
If the real problem is notifications or activity delivery, use `620`.
If the real problem is owner/location/type metadata, use `624`.
Use `629` only when the missing distinction is **wrapper participation-state posture itself**.

## Decision test

Use `629` when all three conditions hold:

1. later evidence preserves or reenacts a **visible participation layer** around same-route detached derivatives — for example collaborator avatars, anonymous-viewer markers, presence cursors, or reviewer-status chips;
2. that layer is **later wrapper-added participation state**, not proof that the underlying source route itself authoritatively names the present participants, approves the packet, or adopts the visible participation state as a governing fact; and
3. later readers are drifting toward treating that layer as if it proved **source authorship, official approval, current office attention, governing participation, or the governing member**.

If any condition fails, keep the packet under the narrower doc that already owns the real problem.
If the surviving packet is still mainly an access, event, review-discourse, or file-information problem with some visible participant cues around it, keep access in `619`, keep event posture in `620`, keep review discourse in `616`, keep information posture in `624`, and add one bounded `629` participation-state note only if the visible participant layer itself changed the reading.

## Keep access, event, discourse, information, and participation state separate

At minimum, keep these layers separate:
1. **current office control** — the current written/help lane and current media head (`194`, `529`, `530`);
2. **surviving detached derivative** — which `595–599` member, if any, the packet actually preserved;
3. **family routing** — whether the packet needed `600` because no single detached derivative dominated;
4. **wrapper-added review discourse** — comments, replies, note threads, or resolved-comment history (`616`);
5. **wrapper-added access state** — permissions, link scope, viewer/editor roles, or request-access posture (`619`);
6. **wrapper-added event state** — notifications, activity feeds, or alert delivery posture (`620`);
7. **wrapper-added information state** — owner/location/type/details panes or file cards (`624`);
8. **wrapper-added participation state** — avatars, anonymous-viewer markers, presence cursors, participant lists, or review-status chips (`629`);
9. **carrier wrapper** — slide deck, PDF memo, doc shell, saved page, web archive, issue ticket, or other transport context (`437`, `490`, `600`);
10. **assembly state** — whether later materials also fused several observations into one stronger-looking posture (`591`).

That separation matters because later packets can otherwise make two different mistakes:
- treating a visible participant roster or cursor/presence layer as if it proved who authored, approved, or currently governs the packet, or
- letting a transient guest / anonymous-viewer / participant-status layer become evidence that the packet itself is official, adopted, or currently under office attention.

`629` exists so the archive can keep that later visible participation layer **truthful but non-governing**.

## Minimal wrapper-participation-state note grammar

When wrapper participation state matters, reviewers SHOULD prefer one compact line in this shape:

`head=<current tuple|none>; governing_member=<595|596|597|598|599|600|none>; wrapper_participation_kind=<named_avatar|anonymous_viewer|guest_badge|presence_cursor|active_collaborator_count|participant_list|review_status|mixed|unknown>; participation_scope=<viewing|editing|reviewing|commenting|mixed|unknown>; participant_identity_certainty=<named|partially_named|anonymous_or_pseudonymous|mixed|unknown>; source_authorship_proved=<forbid>; official_approval_proved=<forbid>; current_office_attention_proved=<forbid>; governing_member_from_participation_state=<forbid>; carrier_wrapper=<doc_shell|review_shell|document_library|desktop_client|browser_shell|slide_deck|pdf_memo|saved_page|web_archive|ticket|email_thread|none>; cite_default=<head|fallback anchor>; use_629_when=<participation_state_changed_reading>; promote_wrapper_participation_state=<no>; basis=<why the later participant/presence layer needed one bounded note>`

This is a note contract, not a new schema.
It exists so packets and summaries can say “this later packet also carried visible participant / presence posture” without minting a new detached-derivative member or silently rewriting authorship, approval, governance, or current office attention.

## Typical uses

1. **Anonymous-viewer overread**
   A later packet shows anonymous animals, guest chips, or unnamed viewers and later readers start retelling that presence layer as if it proved a specific present participant, outside actor, or office observer.
2. **Named-avatar overread**
   A later packet shows named collaborator avatars and later readers start retelling those names as if they proved authorship, adoption, or official approval of the underlying detached derivative.
3. **Presence-cursor overread**
   A later packet shows where someone is editing and later readers start retelling that cursor/presence posture as if it proved sustained office attention, final review, or packet governance.
4. **Participant-list overread**
   A later packet shows participant rosters or review-status badges and later readers start retelling those wrapper facts as if they proved official sign-off, reviewer agreement, or a governing decision.
5. **Mixed participation-state overread**
   A later packet mixes named avatars, anonymous viewers, and review-status cues, and later readers start collapsing that mixed presence layer into one stronger authorship or approval claim than the packet can support.

## When not to use this

Do **not** use `629` when:
- the decisive issue is still review discourse (`616`),
- the decisive issue is still access or permission scope (`619`),
- the decisive issue is still notifications or activity delivery (`620`),
- the decisive issue is still owner/location/type/details metadata (`624`),
- the decisive issue is still a mixed detached-derivative packet with no dominant member (`600`),
- or the decisive issue is still cross-state composite assembly (`591`).

If deleting the visible participant layer leaves an ordinary discourse, access, event, or information problem, use the narrower doc and omit `629`.
If deleting it would erase **why a later avatar, anonymous-viewer, cursor, or participant-status layer changed the way the packet was being read or retold**, `629` is probably right.

## Promotion rule

Future media additions should usually **not** be promoted just because a later packet carried collaborator avatars, anonymous-viewer chips, presence cursors, or reviewer-participant status.
Tighten `616`, `619–620`, `624`, `629`, or `600` first.
Only add another numbered doc when repeated wrapper-participation-state mistakes still cannot be expressed as:
- one governing `595–599` member,
- or a mixed-packet routing note under `600`,
- plus one bounded wrapper-participation-state note under `629`.

## Minimal artifact

This document is intentionally doc-only.
Do **not** add a checklist or payload template for it unless wrapper-participation-state drift still persists after this compact bridge exists.

## Sources

- Google Docs Editors Help — Anonymous or unknown people in a file. (xref: `google_docs_anonymous_or_unknown_people_in_a_file_help_page`)
- Microsoft Support — Collaborate with others. (xref: `microsoft_collaborate_with_others_help_page`)
- Adobe Acrobat Help — Send your PDF to others for review. (xref: `adobe_acrobat_send_pdf_to_others_for_review_help_page`)
