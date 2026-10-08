# 620 — Official voter-information platform media authenticity-cue packet notifications, activity feeds, and non-governing wrapper-event-state firewall

**Track:** Shared / Public surfaces

This document covers a narrow packet-wrapper problem:
**later packets can preserve notification cards, activity feeds, alert digests, “shared with you” notices, “someone changed this file” banners, or similar visible wrapper event-state layers around same-route detached derivatives, and later readers can start mistaking that event posture for official publication, current source change, endorsed distribution, or the packet's governing member.**

It composes with:
- `docs/194-synthetic-media-and-comms-authenticity-minimum-controls.md`
- `docs/490-official-voter-information-browser-managed-reading-lists-offline-saved-pages-and-web-archive-authority-boundary-discipline.md`
- `docs/512-official-voter-information-platform-unavailable-private-age-gated-region-blocked-and-playback-restricted-surface-authority-boundary-discipline.md`
- `docs/523-official-voter-information-platform-media-boundary-quickmap-and-duplicate-firewall.md`
- `docs/529-official-voter-information-platform-media-chain-heads-current-control-and-closeout-discipline.md`
- `docs/530-official-voter-information-platform-media-chain-citations-head-first-reference-and-historical-leg-scoping-discipline.md`
- `docs/535-official-voter-information-platform-media-audience-scoped-current-aliases-scope-labels-and-public-default-retention-discipline.md`
- `docs/591-official-voter-information-platform-media-authenticity-cue-observation-assembly-cross-state-composites-and-no-faux-single-state-firewall.md`
- `docs/595-official-voter-information-platform-media-authenticity-cue-text-extracts-transcript-caption-ocr-derivatives-and-non-carried-cue-firewall.md`
- `docs/598-official-voter-information-platform-media-authenticity-cue-metadata-extracts-title-description-chapter-list-derivatives-and-non-carried-cue-firewall.md`
- `docs/600-official-voter-information-platform-media-authenticity-cue-detached-derivative-family-quickmap-mixed-packets-and-anti-fragmentation-firewall.md`
- `docs/602-official-voter-information-platform-media-authenticity-cue-packet-synopses-forwarding-comments-speaker-notes-and-non-governing-wrapper-summary-firewall.md`
- `docs/616-official-voter-information-platform-media-authenticity-cue-packet-review-threads-comment-replies-and-non-governing-wrapper-discourse-firewall.md`
- `docs/617-official-voter-information-platform-media-authenticity-cue-packet-tracked-changes-suggestions-redlines-and-non-governing-wrapper-revision-state-firewall.md`
- `docs/618-official-voter-information-platform-media-authenticity-cue-packet-version-history-named-versions-restore-points-and-non-governing-wrapper-history-state-firewall.md`
- `docs/619-official-voter-information-platform-media-authenticity-cue-packet-sharing-permissions-link-access-and-non-governing-wrapper-access-state-firewall.md`

## What this is for

Use `620` when a later packet preserves or reenacts a **wrapper event-state layer** around same-route detached derivatives:
- notification-bell cards,
- activity sidebars,
- email alerts or digests,
- “shared with you” or “document delivered” notices,
- “someone changed this file while you were away” banners,
- review-invitation notices,
- comment/reply alert cards,
- or similar visible workflow-event posture.

Those event surfaces are real packet facts and should be preserved honestly.
But they are still **later wrapper-added event posture**, not automatic proof of:
- official publication,
- current source wording,
- accepted source revision,
- current public reach,
- or the packet's governing member.

`620` exists so maintainers can say:
**this packet preserved a later notification/activity layer around a same-route detached derivative, and that layer mattered for how later readers interpreted the packet, but the event layer itself does not govern the packet and does not silently rewrite source provenance, current control, or current distribution scope.**

Google and Microsoft both distinguish activity panes and configurable notifications from the underlying file itself, while Adobe describes notifications as updates about document-status and workflow activity rather than as the governing document state. That is enough for one bounded firewall here. (xref: `google_drive_check_activity_file_versions_help_page`; xref: `google_docs_manage_your_notifications_help_page`; xref: `microsoft_get_notified_when_members_update_shared_file_help_page`; xref: `microsoft_create_alert_get_notified_file_folder_changes_sharepoint_help_page`; xref: `adobe_acrobat_notifications_help_page`)

## Why this is distinct

`619` asks whether a later packet preserved **current wrapper access posture** — link scopes, role matrices, request-access state, password gates, or similar permissions state.

`618` asks whether a later packet preserved **history posture** — named versions, restore candidates, prior-version lists, or compare-old-vs-new state.

`617` asks whether a later packet preserved **revision proposals** — tracked changes, suggestions, redlines, or similar in-place edit posture.

`616` asks whether a later packet preserved **review discourse** — comment threads, replies, and similar attached discussion.

`602` asks whether later wrapper summaries or forwarding prose are being overread.

`620` asks a different question:
**did a later packet add or preserve a visible notification/activity layer — alert cards, workflow-event digests, “shared with you” notices, or “changes while you were away” banners — and did later readers start overreading that layer as if it proved official publication, current source change, endorsed distribution, or the packet's governing member?**

If the real problem is the current permissions state, use `619`.
If the real problem is version history or restore posture, use `618`.
If the real problem is revision proposals, use `617`.
If the real problem is review discourse, use `616`.
If the real problem is wrapper summary prose, use `602`.
Use `620` only when the missing distinction is **wrapper event-state posture itself**.

## Decision test

Use `620` when all three conditions hold:

1. later evidence preserves or reenacts a **visible notification/activity layer** around same-route detached derivatives — for example an activity sidebar, notification-bell card, alert email, “shared with you” notice, “document delivered” event, or “someone changed this file” banner;
2. that layer is **later wrapper-added event state**, not proof that the underlying source route itself newly published, adopted, endorsed, or publicly distributed the content in that same way; and
3. later readers are drifting toward treating that layer as if it proved **official publication, current source change, current endorsement, current public reach, or the governing member**.

If any condition fails, keep the packet under the narrower doc that already owns the real problem.
If the surviving packet is still mainly copied source text or copied source metadata with some activity/notification posture around it, keep the detached derivative in `595–600`, keep any review-discourse fact in `616`, keep any revision-proposal fact in `617`, keep any history-state fact in `618`, keep any access-state fact in `619`, and add one bounded `620` event-state note.

## Keep source-derived content, current state, and wrapper-added event state separate

At minimum, keep these layers separate:
1. **current office control** — the current written/help lane and current media head (`194`, `529`, `530`);
2. **surviving detached derivative** — which `595–599` member, if any, the packet actually preserved;
3. **family routing** — whether the packet needed `600` because no single detached derivative dominated;
4. **source-derived text** — transcript/caption/OCR or other copied route text (`595`);
5. **source-derived metadata** — labels copied from the official route itself (`598`);
6. **wrapper-added summary prose** — forwarding comments, share messages, memo-body summaries, or similar later packet narrative (`602`);
7. **wrapper-added review discourse** — comment-thread bodies, replies, or similar later attached discussion (`616`);
8. **wrapper-added revision state** — tracked changes, suggestions, redlines, or similar proposal posture (`617`);
9. **wrapper-added history state** — version-history panes, named versions, restore candidates, or similar prior-version posture (`618`);
10. **wrapper-added access state** — link scopes, share roles, request-access posture, passwords, expiration dates, or similar later packet permissions (`619`);
11. **wrapper-added event state** — activity feeds, alert cards, notification emails, “shared with you” notices, document-delivered events, or similar later workflow-event posture (`620`);
12. **carrier wrapper** — slide deck, PDF memo, doc shell, saved page, web archive, issue ticket, or other transport context (`490`, `600`);
13. **assembly state** — whether later materials also fused several observations into one stronger-looking posture (`591`).

That separation matters because later packets can otherwise make two different mistakes:
- treating a notification or activity item as if it proved the current source route itself newly published, officially changed, or publicly distributed the content, or
- letting the existence of an alert/event card become evidence that the packet itself governs the source route.

`620` exists so the archive can keep that later visible event layer **truthful but non-governing**.

## Minimal wrapper-event-state note grammar

When wrapper event state matters, reviewers SHOULD prefer one compact line in this shape:

`head=<current tuple|none>; governing_member=<595|596|597|598|599|600|none>; wrapper_event_kind=<activity_feed|notification_card|email_alert|digest|shared_with_you_notice|document_delivered_notice|changed_while_away_banner|review_invite_notice|comment_activity_notice|mixed|unknown>; event_anchor_relation=<whole_member|member_region|slide|page|object|message|mixed|unknown>; wrapper_event_origin=<later_wrapper_added|editor_notification_system|storage_activity_feed|workflow_alerting|imported_alert_capture|mixed|unknown>; publication_proved=<forbid>; source_change_proved=<forbid>; endorsed_distribution_proved=<forbid>; current_public_reach_proved=<forbid>; treat_event_state_as_governing_member=<forbid>; carrier_wrapper=<notification_email|activity_panel|doc_shell|slide_deck|pdf_memo|saved_page|web_archive|ticket|none>; cite_default=<head|fallback anchor>; use_620_when=<event_state_changed_reading>; promote_wrapper_event_state=<no>; basis=<why the later visible event layer needed one bounded note>`

This is a note contract, not a new schema.
It exists so packets and summaries can say “this later packet also carried visible workflow-event posture” without minting a new detached-derivative member or silently rewriting publication, current change, distribution, or governance.

## Typical uses

1. **Shared-with-you overread**
   A later packet shows a “shared with you” or delivery-style notice and later readers start retelling that notification as if the underlying source route was officially published or broadly distributed to the public.
2. **Changed-while-away overread**
   A later packet shows a banner that someone changed the file while a viewer was away and later readers start treating that alert as if it proved an official source revision rather than wrapper event reporting.
3. **Activity-feed overread**
   A later packet captures an activity sidebar showing share/unshare, rename, or comment events and later readers start narrating that event list as if it displaced current source text or current route control.
4. **Notification-email overread**
   A later packet preserves an alert email or digest and later readers start treating that email as the governing publication artifact rather than a later wrapper notice about the artifact.
5. **Review-invite overread**
   A later packet shows a review invitation or comment-activity notification and later readers start treating the invitation/event itself as if it proved source endorsement, current approval, or the packet's governing member.

## When not to use this

Do **not** use `620` when:
- the decisive issue is still packet synopsis or forwarding summary prose (`602`),
- the decisive issue is still wrapper-added review discourse (`616`),
- the decisive issue is still wrapper-added revision-state posture (`617`),
- the decisive issue is still wrapper-added history-state posture (`618`),
- the decisive issue is still wrapper-added access-state posture (`619`),
- the decisive issue is still copied source text (`595`),
- the decisive issue is still copied source metadata (`598`),
- the decisive issue is still a mixed detached-derivative packet with no dominant member (`600`),
- the decisive problem is still print/save/offline/web-archive authority or portability (`490`),
- or the decisive problem is still cross-state composite assembly (`591`).

If deleting the visible event layer leaves an ordinary review-discourse problem, revision-state problem, history-state problem, access-state problem, or mixed-packet problem, use the narrower doc and omit `620`.
If deleting it would erase **why a later notification / activity / alert layer changed the way the packet was being read or retold**, `620` is probably right.

## Promotion rule

Future media additions should usually **not** be promoted just because a later packet carried notification cards, activity panes, alert emails, digests, or “shared with you” workflow notices.
Tighten `602`, `616`, `617`, `618`, `619`, `600`, or `620` first.
Only add another numbered doc when repeated event-state mistakes still cannot be expressed as:
- one governing `595–599` member,
- or a mixed-packet routing note under `600`,
- plus one bounded wrapper-event-state note under `620`.

## Minimal artifact

This document is intentionally doc-only.
Do **not** add a checklist or payload template for it unless wrapper-event-state drift still persists after this compact bridge exists.

## Sources

- Google Drive Help — Check activity & file versions. (xref: `google_drive_check_activity_file_versions_help_page`)
- Google Docs Editors Help — Manage your notifications. (xref: `google_docs_manage_your_notifications_help_page`)
- Microsoft Support — Get notified when members of your team update your shared file. (xref: `microsoft_get_notified_when_members_update_shared_file_help_page`)
- Microsoft Support — Create an alert to get notified when a file or folder changes in SharePoint. (xref: `microsoft_create_alert_get_notified_file_folder_changes_sharepoint_help_page`)
- Adobe Acrobat Help — Acrobat notifications. (xref: `adobe_acrobat_notifications_help_page`)
