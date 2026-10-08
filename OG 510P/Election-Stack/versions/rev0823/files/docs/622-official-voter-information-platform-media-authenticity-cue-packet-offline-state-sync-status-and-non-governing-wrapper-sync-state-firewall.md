# 622 — Official voter-information platform media authenticity-cue packet offline state, sync status, and non-governing wrapper-sync-state firewall

**Track:** Shared / Public surfaces

This document covers a narrow packet-wrapper problem:
**later packets can preserve available-offline toggles, document-status clouds, locally-available / always-keep-on-device badges, sync-pending indicators, sync-conflict notices, or similar visible sync-state layers around same-route detached derivatives, and later readers can start mistaking that wrapper sync posture for official publication, office acknowledgment, current source stability, or the packet's governing member.**

It composes with:
- `docs/194-synthetic-media-and-comms-authenticity-minimum-controls.md`
- `docs/469-official-voter-information-local-only-saves-queued-background-sync-and-office-acknowledged-state-truthfulness-discipline.md`
- `docs/490-official-voter-information-browser-managed-reading-lists-offline-saved-pages-and-web-archive-authority-boundary-discipline.md`
- `docs/512-official-voter-information-platform-unavailable-private-age-gated-region-blocked-and-playback-restricted-surface-authority-boundary-discipline.md`
- `docs/523-official-voter-information-platform-media-boundary-quickmap-and-duplicate-firewall.md`
- `docs/529-official-voter-information-platform-media-chain-heads-current-control-and-closeout-discipline.md`
- `docs/530-official-voter-information-platform-media-chain-citations-head-first-reference-and-historical-leg-scoping-discipline.md`
- `docs/591-official-voter-information-platform-media-authenticity-cue-observation-assembly-cross-state-composites-and-no-faux-single-state-firewall.md`
- `docs/595-official-voter-information-platform-media-authenticity-cue-text-extracts-transcript-caption-ocr-derivatives-and-non-carried-cue-firewall.md`
- `docs/598-official-voter-information-platform-media-authenticity-cue-metadata-extracts-title-description-chapter-list-derivatives-and-non-carried-cue-firewall.md`
- `docs/600-official-voter-information-platform-media-authenticity-cue-detached-derivative-family-quickmap-mixed-packets-and-anti-fragmentation-firewall.md`
- `docs/601-official-voter-information-platform-media-authenticity-cue-packet-labels-filenames-subject-lines-and-non-governing-wrapper-narrative-firewall.md`
- `docs/602-official-voter-information-platform-media-authenticity-cue-packet-synopses-forwarding-comments-speaker-notes-and-non-governing-wrapper-summary-firewall.md`
- `docs/618-official-voter-information-platform-media-authenticity-cue-packet-version-history-named-versions-restore-points-and-non-governing-wrapper-history-state-firewall.md`
- `docs/619-official-voter-information-platform-media-authenticity-cue-packet-sharing-permissions-link-access-and-non-governing-wrapper-access-state-firewall.md`
- `docs/620-official-voter-information-platform-media-authenticity-cue-packet-notifications-activity-feeds-and-non-governing-wrapper-event-state-firewall.md`
- `docs/621-official-voter-information-platform-media-authenticity-cue-packet-trash-recycle-bin-delete-restore-and-non-governing-wrapper-lifecycle-state-firewall.md`

## What this is for

Use `622` when a later packet preserves or reenacts a **visible wrapper sync-state layer** around same-route detached derivatives:
- “Available offline” toggles,
- document-status readiness clouds,
- locally available / online-only / always-keep-on-device badges,
- sync-pending indicators,
- sync-conflict notices,
- offline-change banners,
- or similar later packet sync posture.

Those sync states are real packet facts and should be preserved honestly.
But they are still **later wrapper-added sync posture**, not automatic proof of:
- official publication,
- office acknowledgment,
- source-route currentness,
- source-route stability,
- or the packet's governing member.

`622` exists so maintainers can say:
**this packet preserved a later sync-state layer around a same-route detached derivative, and that layer mattered for how later readers interpreted the packet, but the sync layer itself does not govern the packet and does not silently rewrite publication, office receipt, current control, or source stability.**

## Why this is distinct

Google's current help distinguishes turning files available offline, checking document status, and seeing whether a document is ready for offline use. Google Drive for desktop separately treats unsynced files as a sync problem between the computer and My Drive. Microsoft distinguishes online-only, locally available, and “Always keep on this device” file states, and separately documents “Sync pending” as its own support condition. Adobe's current cloud-document help says offline changes sync back when a connection returns, and Adobe separately documents sync conflicts when cloud documents are accessed on multiple devices simultaneously.
(xref: `google_docs_work_offline_computer_help_page`; xref: `google_drive_fix_problems_in_drive_for_desktop_help_page`; xref: `microsoft_what_do_the_onedrive_icons_mean_help_page`; xref: `microsoft_onedrive_sync_pending_help_page`; xref: `adobe_cloud_documents_faq_help_page`; xref: `adobe_unable_to_access_cloud_documents_multiple_devices_help_page`)

That is enough to justify one bounded bridge for **wrapper sync-state posture**.

`469` asks whether an office workflow truthfully separated local-only saves, queued background sync, and actual office-acknowledged receipt.

`490` asks whether browser-managed offline copies or saved pages became shadow current editions.

`512` asks whether the public source route itself was unavailable, private, blocked, or otherwise restricted.

`618` asks whether the packet preserved prior-version or restore-point history posture.

`619` asks whether the packet preserved sharing/permissions posture.

`620` asks whether the packet preserved notifications or workflow-event posture.

`621` asks whether the packet preserved delete/recover lifecycle posture.

`622` asks a different question:
**did a later packet add or preserve a visible offline / sync / conflict layer — availability-for-offline use, local-availability badges, sync-pending posture, or conflict-copy posture — and did later readers start overreading that layer as if it proved official publication, office receipt, current source stability, or the packet's governing member?**

If the real problem is official receipt or queued submission truthfulness, use `469`.
If the real problem is browser-kept offline copies becoming shadow editions, use `490`.
If the real problem is the source route itself being blocked or unavailable, use `512`.
If the real problem is version-history posture, use `618`.
If the real problem is sharing posture, use `619`.
If the real problem is notifications/activity posture, use `620`.
If the real problem is delete/restore posture, use `621`.
Use `622` only when the missing distinction is **wrapper sync-state posture itself**.

## Decision test

Use `622` when all three conditions hold:

1. later evidence preserves or reenacts a **visible offline / sync / conflict layer** around same-route detached derivatives — for example an “Available offline” state, document-status readiness cloud, locally-available or always-keep-on-device badge, sync-pending indicator, or sync-conflict notice;
2. that layer is **later wrapper-added sync posture**, not proof that the underlying source route itself was officially published, officially received, currently stable, or governing; and
3. later readers are drifting toward treating that layer as if it proved **official publication, office acknowledgment, current source stability, or the governing member**.

If any condition fails, keep the packet under the narrower doc that already owns the real problem.
If the surviving packet is still mainly copied source text or copied source metadata with some offline/sync posture around it, keep the detached derivative in `595–600`, keep any office-receipt truthfulness question in `469`, keep any source-route restriction fact in `512`, keep any history/access/event/lifecycle fact in `618–621`, and add one bounded `622` sync-state note.

## Keep source-derived content, route-level availability, and wrapper-added sync state separate

At minimum, keep these layers separate:
1. **current office control** — the current written/help lane and current media head (`194`, `529`, `530`);
2. **surviving detached derivative** — which `595–599` member, if any, the packet actually preserved;
3. **family routing** — whether the packet needed `600` because no single detached derivative dominated;
4. **source-derived text** — transcript/caption/OCR or other copied route text (`595`);
5. **source-derived metadata** — labels copied from the official route itself (`598`);
6. **route-level public availability** — whether the public source route itself was reachable, blocked, removed, or otherwise not ordinarily accessible (`512`, `529`, `530`);
7. **office-receipt truthfulness** — whether a workflow really reached office-acknowledged state or only local / queued state (`469`);
8. **wrapper-added summary prose** — forwarding comments, memo-body summaries, or similar later packet narrative (`602`);
9. **wrapper-added history state** — version-history panes, restore points, prior-version labels, or similar source-history posture (`618`);
10. **wrapper-added access state** — share scopes, roles, request-access posture, or similar later permissions state (`619`);
11. **wrapper-added event state** — activity feeds, alert cards, notification emails, or similar later workflow-event posture (`620`);
12. **wrapper-added lifecycle state** — Trash/Recycling/Deleted status, delete-confirmation posture, restore notices, or permanent-delete warnings (`621`);
13. **wrapper-added sync state** — available-offline posture, local-availability badges, sync-pending indicators, sync-conflict notices, or similar later sync posture (`622`);
14. **carrier wrapper** — slide deck, PDF memo, doc shell, saved page, web archive, issue ticket, or other transport context (`490`, `600`);
15. **assembly state** — whether later materials also fused several observations into one stronger-looking posture (`591`).

That separation matters because later packets can otherwise make two different mistakes:
- treating a visible offline/sync badge or conflict warning as if it proved official publication, office acknowledgment, or settled current stability, or
- treating a sync-state layer itself as if it governed the packet or displaced head-first source control.

`622` exists so the archive can keep that later visible sync layer **truthful but non-governing**.

## Minimal wrapper-sync-state note grammar

When wrapper sync state matters, reviewers SHOULD prefer one compact line in this shape:

`head=<current tuple|none>; governing_member=<595|596|597|598|599|600|none>; wrapper_sync_kind=<available_offline|document_status_ready|document_status_not_ready|locally_available|online_only|always_keep_on_device|sync_pending|sync_conflict|offline_changes_waiting|mixed|unknown>; sync_anchor_relation=<whole_member|member_link|attachment|slide|page|object|message|mixed|unknown>; wrapper_sync_origin=<later_wrapper_added|offline_toggle_ui|desktop_sync_ui|cloud_status_ui|conflict_notice_ui|imported_sync_capture|mixed|unknown>; source_publication_proved=<forbid>; office_receipt_proved=<forbid>; source_stability_proved=<forbid>; treat_sync_state_as_governing_member=<forbid>; carrier_wrapper=<doc_shell|desktop_sync_client|slide_deck|pdf_memo|saved_page|web_archive|ticket|email_thread|none>; cite_default=<head|fallback anchor>; use_622_when=<sync_state_changed_reading>; promote_wrapper_sync_state=<no>; basis=<why the later visible offline/sync layer needed one bounded note>`

This is a note contract, not a new schema.
It exists so packets and summaries can say “this later packet also carried visible offline/sync posture” without minting a new detached-derivative member or silently rewriting publication, office receipt, route control, or governance.

## Typical uses

1. **Offline-overread**
   A later packet shows a file marked available offline or locally available, and later readers start retelling that wrapper state as if it proved official publication, safe portability, or a stable governing copy.
2. **Pending-overread**
   A later packet shows sync pending and later readers start treating that later client posture as if it proved office receipt, imminent publication, or unresolved source change.
3. **Conflict-overread**
   A later packet shows a sync conflict or multi-device conflict notice and later readers start treating that wrapper warning as if it settled source authenticity, governing text, or current head control.
4. **Device-presence overread**
   A later packet shows “Always keep on this device” or similar local-presence posture and later readers start narrating that device-specific state as if it proved source-route publicness or authoritative permanence.
5. **Readiness-overread**
   A later packet shows a document-status explanation that a file is or is not ready for offline use, and later readers start treating that readiness posture as if it proved source availability, official adoption, or governing-member status.

## When not to use this

Do **not** use `622` when:
- the decisive issue is still office receipt, local save, or queued background sync truthfulness (`469`),
- the decisive issue is still browser-kept offline copies or saved pages becoming shadow editions (`490`),
- the decisive issue is still the public source route itself being unavailable, private, blocked, or absent (`512`, `529`, `530`),
- the decisive issue is still wrapper summary prose (`602`),
- the decisive issue is still wrapper history-state posture (`618`),
- the decisive issue is still wrapper access-state posture (`619`),
- the decisive issue is still wrapper event-state posture (`620`),
- the decisive issue is still wrapper lifecycle-state posture (`621`),
- the decisive issue is still copied source text (`595`),
- the decisive issue is still copied source metadata (`598`),
- the decisive issue is still a mixed detached-derivative packet with no dominant member (`600`),
- or the decisive problem is still cross-state composite assembly (`591`).

If deleting the visible sync layer leaves an ordinary receipt-truthfulness problem, saved-page authority problem, route-availability problem, history/access/event/lifecycle problem, summary problem, or mixed-packet problem, use the narrower doc and omit `622`.
If deleting it would erase **why a later offline/sync/conflict layer changed the way the packet was being read or retold**, `622` is probably right.

## Promotion rule

Future media additions should usually **not** be promoted just because a later packet carried available-offline state, local-availability badges, sync-pending indicators, or sync-conflict notices.
Tighten `469`, `490`, `512`, `600`, or `618–622` first.
Only add another numbered doc when repeated wrapper-sync-state mistakes still cannot be expressed as:
- one governing `595–599` member,
- or a mixed-packet routing note under `600`,
- plus one bounded wrapper-sync-state note under `622`.

## Minimal artifact

This document is intentionally doc-only.
Do **not** add a checklist or payload template for it unless wrapper-sync-state drift still persists after this compact bridge exists.

## Sources

- Google Docs Editors Help — Work on Google Docs, Sheets, & Slides offline (Computer). (xref: `google_docs_work_offline_computer_help_page`)
- Google Drive Help — Fix problems in Drive for desktop. (xref: `google_drive_fix_problems_in_drive_for_desktop_help_page`)
- Microsoft Support — What do the OneDrive icons mean? (xref: `microsoft_what_do_the_onedrive_icons_mean_help_page`)
- Microsoft Support — OneDrive is stuck on “Sync pending”. (xref: `microsoft_onedrive_sync_pending_help_page`)
- Adobe Creative Cloud Help — Cloud documents FAQ. (xref: `adobe_cloud_documents_faq_help_page`)
- Adobe Creative Cloud Help — Unable to access cloud documents on multiple devices. (xref: `adobe_unable_to_access_cloud_documents_multiple_devices_help_page`)
