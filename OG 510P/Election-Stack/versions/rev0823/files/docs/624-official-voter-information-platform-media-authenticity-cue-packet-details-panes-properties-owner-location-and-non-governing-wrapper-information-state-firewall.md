# 624 — Official voter-information platform media authenticity-cue packet details panes properties owner location and non-governing wrapper-information-state firewall

**Track:** Shared / Public surfaces

This document covers a narrow packet-wrapper problem:
**later packets can preserve details panes, info cards, properties dialogs, metadata side panels, owner/location/size/type fields, or similar visible wrapper information-state layers around same-route detached derivatives, and later readers can start mistaking that information posture for source-native metadata, official control, canonical location, or the packet's governing member.**

It composes with:
- `docs/194-synthetic-media-and-comms-authenticity-minimum-controls.md`
- `docs/490-official-voter-information-browser-managed-reading-lists-offline-saved-pages-and-web-archive-authority-boundary-discipline.md`
- `docs/523-official-voter-information-platform-media-boundary-quickmap-and-duplicate-firewall.md`
- `docs/529-official-voter-information-platform-media-chain-heads-current-control-and-closeout-discipline.md`
- `docs/530-official-voter-information-platform-media-chain-citations-head-first-reference-and-historical-leg-scoping-discipline.md`
- `docs/591-official-voter-information-platform-media-authenticity-cue-observation-assembly-cross-state-composites-and-no-faux-single-state-firewall.md`
- `docs/595-official-voter-information-platform-media-authenticity-cue-text-extracts-transcript-caption-ocr-derivatives-and-non-carried-cue-firewall.md`
- `docs/598-official-voter-information-platform-media-authenticity-cue-metadata-extracts-title-description-chapter-list-derivatives-and-non-carried-cue-firewall.md`
- `docs/600-official-voter-information-platform-media-authenticity-cue-detached-derivative-family-quickmap-mixed-packets-and-anti-fragmentation-firewall.md`
- `docs/601-official-voter-information-platform-media-authenticity-cue-packet-labels-filenames-subject-lines-and-non-governing-wrapper-narrative-firewall.md`
- `docs/618-official-voter-information-platform-media-authenticity-cue-packet-version-history-named-versions-restore-points-and-non-governing-wrapper-history-state-firewall.md`
- `docs/619-official-voter-information-platform-media-authenticity-cue-packet-sharing-permissions-link-access-and-non-governing-wrapper-access-state-firewall.md`
- `docs/620-official-voter-information-platform-media-authenticity-cue-packet-notifications-activity-feeds-and-non-governing-wrapper-event-state-firewall.md`
- `docs/621-official-voter-information-platform-media-authenticity-cue-packet-trash-recycle-bin-delete-restore-and-non-governing-wrapper-lifecycle-state-firewall.md`
- `docs/622-official-voter-information-platform-media-authenticity-cue-packet-offline-state-sync-status-and-non-governing-wrapper-sync-state-firewall.md`
- `docs/623-official-voter-information-platform-media-authenticity-cue-packet-starred-recents-shortcuts-favorites-and-non-governing-wrapper-organization-state-firewall.md`

## What this is for

Use `624` when a later packet preserves or reenacts a **visible wrapper information-state layer** around same-route detached derivatives:
- a details pane or info sidebar,
- a file card or properties dialog,
- owner, location, size, type, created, or modified fields,
- sharing-summary or activity-summary snippets inside an info view,
- property panels or metadata side panes,
- or similar later packet information posture.

Those information surfaces are real packet facts and should be preserved honestly.
But they are still **later wrapper-added information posture**, not automatic proof of:
- source-native metadata,
- current official control,
- canonical source location,
- endorsed provenance,
- or the packet's governing member.

Current primary-source guidance is already enough to justify one bounded information-state bridge.
Google Drive documents a details view that can show system properties such as document type, size, location, and owner.
Microsoft distinguishes a OneDrive details pane and a SharePoint information pane that show sharing information and editable item properties.
Adobe distinguishes document properties and metadata panels for PDFs.
That is enough for one bounded firewall here.
(xref: `google_drive_screen_reader_details_pane_help_page`; xref: `microsoft_change_views_on_the_onedrive_website_help_page`; xref: `microsoft_doc_library_item_info_help_page`; xref: `adobe_acrobat_document_properties_metadata_overview_help_page`)

`624` exists so maintainers can say:
**this packet preserved a later details/properties layer around a same-route detached derivative, and that layer mattered for how later readers interpreted the packet, but the information layer itself does not govern the packet and does not silently rewrite source-native metadata, route control, or canonical location.**

## Why this is distinct

`598` asks whether later evidence preserved **source-derived metadata** — copied titles, descriptions, chapter lists, or other labels from the official route itself.

`601` asks whether later evidence preserved **wrapper-added labels** — filenames, subject lines, memo headings, or packet titles.

`619` asks whether a later packet preserved **access posture** — link scopes, roles, access requests, or similar permissions state.

`620` asks whether a later packet preserved **event posture** — notifications, activity feeds, or workflow-event state.

`623` asks whether a later packet preserved **organization posture** — starred state, recent-file listings, pinned recents, shortcut placement, favorites, or moved-location cues.

`624` asks a different question:
**did a later packet add or preserve a visible details/properties layer — owner/location/size/type fields, an info card, a details pane, or a properties dialog — and did later readers start overreading that layer as if it proved source-native metadata, official control, canonical location, or the packet's governing member?**

If the real problem is copied source metadata, use `598`.
If the real problem is wrapper-added labels, use `601`.
If the real problem is access, event, or organization posture, use `619`, `620`, or `623`.
Use `624` only when the missing distinction is **wrapper information-state posture itself**.

## Decision test

Use `624` when all three conditions hold:

1. later evidence preserves or reenacts a **visible details/properties layer** around same-route detached derivatives — for example a details pane, info card, properties dialog, metadata side panel, owner/location/size/type field set, or similar information view;
2. that layer is **later wrapper-added information state**, not proof that the underlying source route itself published, endorsed, or canonically fixed those same details in that same way; and
3. later readers are drifting toward treating that layer as if it proved **source-native metadata, official control, canonical location, provenance certainty, or the governing member**.

If any condition fails, keep the packet under the narrower doc that already owns the real problem.
If the surviving packet is still mainly copied source text or copied source metadata with some details/properties posture around it, keep the detached derivative in `595–600`, keep copied source metadata in `598`, keep wrapper-added labels in `601`, keep access/event/organization posture in `619`, `620`, or `623`, and add one bounded `624` information-state note.

## Keep source-derived metadata, wrapper labels, and wrapper-added information state separate

At minimum, keep these layers separate:
1. **current office control** — the current written/help lane and current media head (`194`, `529`, `530`);
2. **surviving detached derivative** — which `595–599` member, if any, the packet actually preserved;
3. **family routing** — whether the packet needed `600` because no single detached derivative dominated;
4. **source-derived text** — transcript/caption/OCR or other copied route text (`595`);
5. **source-derived metadata** — labels copied from the official route itself (`598`);
6. **wrapper-added labels** — filenames, subject lines, and packet titles (`601`);
7. **wrapper-added access state** — link scopes, roles, or request-access posture (`619`);
8. **wrapper-added event state** — notifications or activity posture (`620`);
9. **wrapper-added lifecycle state** — Trash/Recycling/delete-restore posture (`621`);
10. **wrapper-added sync state** — offline/local/pending/conflict posture (`622`);
11. **wrapper-added organization state** — starred, recent, pinned, shortcut, favorite, or moved-location posture (`623`);
12. **wrapper-added information state** — owner, location, size, type, created, modified, details-pane, info-card, or properties-dialog posture (`624`);
13. **carrier wrapper** — slide deck, PDF memo, doc shell, saved page, web archive, issue ticket, or other transport context (`490`, `600`);
14. **assembly state** — whether later materials also fused several observations into one stronger-looking posture (`591`).

That separation matters because later packets can otherwise make two different mistakes:
- treating a visible details/properties pane as if it were the source route's own reviewed metadata or authoritative publication notice, or
- letting a file-manager or document-library info view become evidence that the packet itself governs the source route.

`624` exists so the archive can keep that later visible information layer **truthful but non-governing**.

## Minimal wrapper-information-state note grammar

When wrapper information state matters, reviewers SHOULD prefer one compact line in this shape:

`head=<current tuple|none>; governing_member=<595|596|597|598|599|600|none>; wrapper_information_kind=<details_pane|info_card|properties_dialog|metadata_panel|file_card|inspector|mixed|unknown>; information_fields_seen=<owner|location|type|size|created|modified|sharing_summary|activity_summary|mixed|unknown>; information_anchor_relation=<whole_member|member_link|attachment|slide|page|object|message|mixed|unknown>; wrapper_information_origin=<later_wrapper_added|file_manager_ui|document_library_ui|desktop_client|pdf_viewer_ui|mixed|unknown>; source_metadata_proved=<forbid>; official_control_proved=<forbid>; canonical_location_proved=<forbid>; provenance_certainty_proved=<forbid>; treat_information_state_as_governing_member=<forbid>; carrier_wrapper=<doc_shell|file_manager|document_library|desktop_client|slide_deck|pdf_memo|saved_page|web_archive|ticket|email_thread|none>; cite_default=<head|fallback anchor>; use_624_when=<information_state_changed_reading>; promote_wrapper_information_state=<no>; basis=<why the later visible details/properties layer needed one bounded note>`

This is a note contract, not a new schema.
It exists so packets and summaries can say “this later packet also carried visible details/properties posture” without minting a new detached-derivative member or silently rewriting metadata, control, location, or governance.

## Typical uses

1. **Owner-overread**
   A later packet shows an owner field in a details pane and later readers start retelling that wrapper field as if it proved current office control or reviewed source endorsement.
2. **Location-overread**
   A later packet shows a folder or library location and later readers start treating that wrapper placement as if it proved canonical source-route location.
3. **Properties-dialog overread**
   A later packet shows size, type, created, modified, or similar properties and later readers start treating that wrapper property block as if it were the official source route's own metadata contract.
4. **Info-card overread**
   A later packet shows a file card or details sidebar with mixed sharing/activity/property snippets and later readers start treating that convenience panel as if it governed provenance or current control.
5. **Metadata-panel overread**
   A later packet shows a properties/metadata panel around a detached derivative and later readers start collapsing that wrapper panel into the governing detached-derivative member itself.

## When not to use this

Do **not** use `624` when:
- the decisive issue is still copied source metadata (`598`),
- the decisive issue is still wrapper-added labels (`601`),
- the decisive issue is still wrapper access-state posture (`619`),
- the decisive issue is still wrapper event-state posture (`620`),
- the decisive issue is still wrapper organization-state posture (`623`),
- the decisive issue is still a mixed detached-derivative packet with no dominant member (`600`),
- the decisive issue is still print/save/offline/web-archive authority or portability (`490`),
- or the decisive issue is still cross-state composite assembly (`591`).

If deleting the visible details/properties layer leaves an ordinary copied-metadata problem, label problem, access/event/organization problem, or mixed-packet problem, use the narrower doc and omit `624`.
If deleting it would erase **why a later details pane, info card, or properties dialog changed the way the packet was being read or retold**, `624` is probably right.

## Promotion rule

Future media additions should usually **not** be promoted just because a later packet carried a details pane, info card, owner field, location field, size/type block, or properties dialog.
Tighten `598`, `601`, `619–624`, or `600` first.
Only add another numbered doc when repeated wrapper-information-state mistakes still cannot be expressed as:
- one governing `595–599` member,
- or a mixed-packet routing note under `600`,
- plus one bounded wrapper-information-state note under `624`.

## Minimal artifact

This document is intentionally doc-only.
Do **not** add a checklist or payload template for it unless wrapper-information-state drift still persists after this compact bridge exists.

## Sources

- Google Drive Help — Use Google Drive with a screen reader. (xref: `google_drive_screen_reader_details_pane_help_page`)
- Microsoft Support — Change views on the OneDrive website. (xref: `microsoft_change_views_on_the_onedrive_website_help_page`)
- Microsoft Support — View and edit information about a file, folder, or link in a document library. (xref: `microsoft_doc_library_item_info_help_page`)
- Adobe Acrobat Help — Document properties and metadata overview. (xref: `adobe_acrobat_document_properties_metadata_overview_help_page`)
