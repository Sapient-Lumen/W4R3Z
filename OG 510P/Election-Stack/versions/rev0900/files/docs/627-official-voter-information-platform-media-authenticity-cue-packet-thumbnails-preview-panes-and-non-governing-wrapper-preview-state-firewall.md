# 627 — Official voter-information platform media authenticity-cue packet thumbnails preview panes and non-governing wrapper-preview-state firewall

**Track:** Shared / Public surfaces

This document covers a narrow packet-wrapper problem:
**later packets can preserve thumbnails, preview panes, preview-mode shells, partial/full previews, filmstrip-like preview strips, or similar visible wrapper preview-state layers around same-route detached derivatives, and later readers can start mistaking that preview posture for source-native frames, source-native default render state, settled content state, or the packet's governing member.**

It composes with:
- `docs/194-synthetic-media-and-comms-authenticity-minimum-controls.md`
- `docs/437-official-voter-information-portable-records-print-save-to-pdf-and-off-screen-fidelity-fail-open-discipline.md`
- `docs/490-official-voter-information-browser-managed-reading-lists-offline-saved-pages-and-web-archive-authority-boundary-discipline.md`
- `docs/523-official-voter-information-platform-media-boundary-quickmap-and-duplicate-firewall.md`
- `docs/529-official-voter-information-platform-media-chain-heads-current-control-and-closeout-discipline.md`
- `docs/530-official-voter-information-platform-media-chain-citations-head-first-reference-and-historical-leg-scoping-discipline.md`
- `docs/591-official-voter-information-platform-media-authenticity-cue-observation-assembly-cross-state-composites-and-no-faux-single-state-firewall.md`
- `docs/597-official-voter-information-platform-media-authenticity-cue-still-image-extracts-frame-grabs-poster-exports-and-non-carried-cue-firewall.md`
- `docs/600-official-voter-information-platform-media-authenticity-cue-detached-derivative-family-quickmap-mixed-packets-and-anti-fragmentation-firewall.md`
- `docs/613-official-voter-information-platform-media-authenticity-cue-packet-view-state-zoom-open-page-and-non-governing-wrapper-viewport-firewall.md`
- `docs/615-official-voter-information-platform-media-authenticity-cue-packet-selection-state-active-thumbnails-and-non-governing-wrapper-focus-firewall.md`
- `docs/624-official-voter-information-platform-media-authenticity-cue-packet-details-panes-properties-owner-location-and-non-governing-wrapper-information-state-firewall.md`
- `docs/625-official-voter-information-platform-media-authenticity-cue-packet-file-lists-sort-filters-groups-and-non-governing-wrapper-listing-state-firewall.md`
- `docs/626-official-voter-information-platform-media-authenticity-cue-packet-command-bars-context-menus-and-non-governing-wrapper-action-state-firewall.md`

## What this is for

Use `627` when a later packet preserves or reenacts a **visible wrapper preview-state layer** around same-route detached derivatives:
- thumbnail tiles or thumbnail sidebars,
- a preview pane or details-side preview,
- preview mode in the same tab,
- partial versus full preview states,
- preview-first file-manager or document-library shells,
- or similar later packet render/posture that shows a derivative through a preview surface.

Those preview surfaces are real packet facts and should be preserved honestly.
But they are still **later wrapper-added preview posture**, not automatic proof of:
- source-native default frames,
- source-native default render state,
- settled content state,
- official priority,
- or the packet's governing member.

Current primary-source guidance is already enough to justify one bounded preview-state bridge.
Google Drive distinguishes opening files in Drive and opening PDFs in preview mode in the same tab.
Microsoft documents preview and thumbnail images for hundreds of file types in OneDrive and SharePoint, and separately documents thumbnail-specific view behavior in OneDrive.
Adobe documents a right-pane file preview that can show a snapshot, file information, and available commands, plus a fuller preview mode when the name or thumbnail is opened.
That is enough for one bounded firewall here.
(xref: `google_drive_view_open_files_help_page`; xref: `microsoft_file_types_supported_previewing_files_onedrive_sharepoint_teams_help_page`; xref: `microsoft_onedrive_thumbnails_help_page`; xref: `adobe_acrobat_preview_files_help_page`)

`627` exists so maintainers can say:
**this packet preserved a later thumbnail/preview layer around same-route detached derivatives, and that layer mattered for how later readers interpreted the packet, but the preview layer itself does not govern the packet and does not silently prove source-native frames, default render state, settled content state, official priority, or the governing member.**

## Why this is distinct

`597` asks whether a later artifact carried a **detached still-image derivative** — a frame grab, poster, thumbnail export, or other still carried as its own derivative object.

`613` asks whether a later packet preserved **view-state posture** — open page, initial viewport, zoom level, or fit mode.

`624` asks whether a later packet preserved **information posture** — owner/location/size/type fields, info cards, details panes, or properties dialogs.

`625` asks whether a later packet preserved **listing posture** — file lists, sort order, filters, group headers, or shown/hidden columns.

`626` asks whether a later packet preserved **action posture** — command bars, quick actions, context menus, or disabled commands.

`627` asks a different question:
**did a later packet add or preserve a visible preview layer — thumbnail tiles, preview panes, preview-mode shells, or partial/full previews — and did later readers start overreading that layer as if it proved source-native frames, source-native default render state, settled content state, official priority, or the packet's governing member?**

If the real problem is a detached still image carried on its own, use `597`.
If the real problem is mainly zoom/open-page posture, use `613`.
If the real problem is mainly details-pane metadata, file-list posture, or visible commands, use `624`, `625`, or `626`.
Use `627` only when the missing distinction is **wrapper preview-state posture itself**.

## Decision test

Use `627` when all three conditions hold:

1. later evidence preserves or reenacts a **visible preview layer** around same-route detached derivatives — for example thumbnail tiles, a preview pane, same-tab preview mode, or a partial/full preview shell;
2. that layer is **later wrapper-added preview state**, not proof that the underlying source route itself canonically chose the same frame, same still, same default render, or the same current content posture; and
3. later readers are drifting toward treating that layer as if it proved **source-native frames, source-native default render state, settled content state, official priority, or the governing member**.

If any condition fails, keep the packet under the narrower doc that already owns the real problem.
If the surviving packet is still mainly a detached still-image, view-state, information-state, listing-state, or action-state problem with some preview posture around it, keep the governing note in `597`, `613`, `624`, `625`, or `626` and add one bounded `627` preview-state note only if the visible preview layer itself changed the reading.

## Keep still-image, view, information, listing, action, and preview state separate

At minimum, keep these layers separate:
1. **current office control** — the current written/help lane and current media head (`194`, `529`, `530`);
2. **surviving detached derivative** — which `595–599` member, if any, the packet actually preserved;
3. **family routing** — whether the packet needed `600` because no single detached derivative dominated;
4. **wrapper-added still-image carry** — any detached frame grab, poster, thumbnail export, or other still carried as its own derivative object (`597`);
5. **wrapper-added view state** — open page, zoom level, initial viewport, fit mode, or restored first-view posture (`613`);
6. **wrapper-added information state** — owner, location, size, type, details-pane, info-card, or properties-dialog posture (`624`);
7. **wrapper-added listing state** — sort keys, filters, grouping, shown/hidden columns, saved views, or list/tile modes (`625`);
8. **wrapper-added action state** — command bars, more-action menus, context menus, quick-action buttons, or disabled commands (`626`);
9. **wrapper-added preview state** — thumbnail tiles, preview panes, preview-mode shells, or partial/full previews (`627`);
10. **carrier wrapper** — slide deck, PDF memo, doc shell, saved page, web archive, issue ticket, or other transport context (`437`, `490`, `600`);
11. **assembly state** — whether later materials also fused several observations into one stronger-looking posture (`591`).

That separation matters because later packets can otherwise make two different mistakes:
- treating a preview tile, preview pane, or preview-mode shell as if it were the source's own chosen frame, canonical render, or settled current content, or
- letting a file-manager or document-library preview surface become evidence that the packet itself governs what the derivative “really is.”

`627` exists so the archive can keep that later visible preview layer **truthful but non-governing**.

## Minimal wrapper-preview-state note grammar

When wrapper preview state matters, reviewers SHOULD prefer one compact line in this shape:

`head=<current tuple|none>; governing_member=<595|596|597|598|599|600|none>; wrapper_preview_kind=<thumbnail_tile|thumbnail_sidebar|preview_pane|same_tab_preview|full_preview|partial_preview|mixed|unknown>; preview_anchor_relation=<whole_member|member_link|attachment|slide|page|object|message|collection|mixed|unknown>; preview_scope=<single_item|selected_item|collection|mixed|unknown>; preview_origin=<later_wrapper_added|file_manager_ui|document_library_ui|desktop_client|web_app_ui|mixed|unknown>; frame_choice_proved=<forbid>; render_default_proved=<forbid>; settled_content_state_proved=<forbid>; official_priority_proved=<forbid>; treat_preview_state_as_governing_member=<forbid>; carrier_wrapper=<doc_shell|file_manager|document_library|desktop_client|slide_deck|pdf_memo|saved_page|web_archive|ticket|email_thread|none>; cite_default=<head|fallback anchor>; use_627_when=<preview_state_changed_reading>; promote_wrapper_preview_state=<no>; basis=<why the later thumbnail/preview layer needed one bounded note>`

This is a note contract, not a new schema.
It exists so packets and summaries can say “this later packet also carried a visible preview layer” without minting a new detached-derivative member or silently rewriting frames, render defaults, currentness, or governance.

## Typical uses

1. **Thumbnail primacy overread**
   A later packet preserves thumbnail tiles or a thumbnail strip and later readers start retelling one preview image as if it were the source's chosen still, governing member, or canonical first frame.
2. **Preview-pane overread**
   A later packet preserves a right-pane or side-pane preview and later readers start retelling that visible preview as if it fixed the source's current content posture or default render state.
3. **Same-tab preview overread**
   A later packet preserves preview mode in the same tab and later readers start retelling that wrapper preview shell as if it were the whole current route or the source-native presentation contract.
4. **Partial/full preview overread**
   A later packet preserves both a compact preview and a fuller preview state and later readers start retelling those wrapper transitions as if they proved content adoption, content finality, or source-native prominence.
5. **Preview-vs-details confusion**
   A later packet preserves a preview pane with neighboring details or actions and later readers start treating the combined shell as if preview, metadata, and commands all came from the source object itself rather than from a later wrapper.

## When not to use this

Do **not** use `627` when:
- the decisive issue is still a detached still-image derivative (`597`),
- the decisive issue is still viewport/open-page posture (`613`),
- the decisive issue is still information, listing, or action posture (`624–626`),
- the decisive issue is still a mixed detached-derivative packet with no dominant member (`600`),
- the decisive issue is still print/save/offline/web-archive authority or portability (`437`, `490`),
- or the decisive issue is still cross-state composite assembly (`591`).

If deleting the visible preview layer leaves an ordinary still-image, view-state, information-state, listing-state, or action-state problem, use the narrower doc and omit `627`.
If deleting it would erase **why a later thumbnail/preview shell changed the way the packet was being read or retold**, `627` is probably right.

## Promotion rule

Future media additions should usually **not** be promoted just because a later packet carried thumbnail tiles, a preview pane, same-tab preview mode, or partial/full preview shells.
Tighten `597`, `613`, `624–627`, or `600` first.
Only add another numbered doc when repeated wrapper-preview-state mistakes still cannot be expressed as:
- one governing `595–599` member,
- or a mixed-packet routing note under `600`,
- plus one bounded wrapper-preview-state note under `627`.

## Minimal artifact

This document is intentionally doc-only.
Do **not** add a checklist or payload template for it unless wrapper-preview-state drift still persists after this compact bridge exists.

## Sources

- Google Drive Help — View & open files. (xref: `google_drive_view_open_files_help_page`)
- Microsoft Support — File types supported for previewing files in OneDrive, SharePoint, and Teams. (xref: `microsoft_file_types_supported_previewing_files_onedrive_sharepoint_teams_help_page`)
- Microsoft Support — OneDrive Thumbnails. (xref: `microsoft_onedrive_thumbnails_help_page`)
- Adobe Acrobat Help — Preview files. (xref: `adobe_acrobat_preview_files_help_page`)
