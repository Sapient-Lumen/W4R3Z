# 628 — Official voter-information platform media authenticity-cue packet open with open in app browser desktop defaults and non-governing wrapper-launch-state firewall

**Track:** Shared / Public surfaces

This document covers a narrow packet-wrapper problem:
**later packets can preserve “Open with” menus, “Open in app” choices, browser-versus-desktop preferences, default-app selectors, auto-open/download handlers, or similar visible wrapper launch-state layers around same-route detached derivatives, and later readers can start mistaking that launch posture for source-native format requirements, official route choice, canonical render environment, required software, or the packet's governing member.**

It composes with:
- `docs/194-synthetic-media-and-comms-authenticity-minimum-controls.md`
- `docs/437-official-voter-information-portable-records-print-save-to-pdf-and-off-screen-fidelity-fail-open-discipline.md`
- `docs/490-official-voter-information-browser-managed-reading-lists-offline-saved-pages-and-web-archive-authority-boundary-discipline.md`
- `docs/523-official-voter-information-platform-media-boundary-quickmap-and-duplicate-firewall.md`
- `docs/529-official-voter-information-platform-media-chain-heads-current-control-and-closeout-discipline.md`
- `docs/530-official-voter-information-platform-media-chain-citations-head-first-reference-and-historical-leg-scoping-discipline.md`
- `docs/591-official-voter-information-platform-media-authenticity-cue-observation-assembly-cross-state-composites-and-no-faux-single-state-firewall.md`
- `docs/592-official-voter-information-platform-media-authenticity-cue-preview-shells-open-target-separation-and-noninheritance-firewall.md`
- `docs/600-official-voter-information-platform-media-authenticity-cue-detached-derivative-family-quickmap-mixed-packets-and-anti-fragmentation-firewall.md`
- `docs/612-official-voter-information-platform-media-authenticity-cue-packet-interactivity-hotspots-hyperlinks-and-non-governing-wrapper-navigation-firewall.md`
- `docs/626-official-voter-information-platform-media-authenticity-cue-packet-command-bars-context-menus-and-non-governing-wrapper-action-state-firewall.md`
- `docs/627-official-voter-information-platform-media-authenticity-cue-packet-thumbnails-preview-panes-and-non-governing-wrapper-preview-state-firewall.md`

## What this is for

Use `628` when a later packet preserves or reenacts a **visible wrapper launch-state layer** around same-route detached derivatives:
- an “Open with” picker,
- an “Open in app” or “Open in browser” choice,
- browser-versus-desktop or Teams-versus-browser file-open preferences,
- default-app or default-handler settings,
- auto-open-after-download posture,
- or similar later packet open-target / handler posture.

Those launch surfaces are real packet facts and should be preserved honestly.
But they are still **later wrapper-added launch posture**, not automatic proof of:
- source-native format requirements,
- official route choice,
- canonical render environment,
- required software,
- endorsed handling instructions,
- or the packet's governing member.

Current primary-source guidance is already enough to justify one bounded launch-state bridge.
Google Drive documents both “Open with” app selection and default apps for certain file types, and it separately distinguishes opening some files in Drive from opening others with another app or in a different PDF mode.
Microsoft documents “Open in app” for OneDrive and SharePoint files, plus saved file-open preferences that choose Teams, Desktop App, or Browser for Microsoft 365 file links.
Adobe documents opening PDFs in the browser versus in Acrobat, choosing Acrobat with “Open With,” setting Acrobat as the default PDF program, and automatically opening downloaded PDFs in Acrobat or Reader.
That is enough for one bounded firewall here.
(xref: `google_drive_use_google_drive_apps_help_page`; xref: `google_drive_view_open_files_help_page`; xref: `microsoft_open_onedrive_or_sharepoint_file_in_desktop_app_help_page`; xref: `microsoft_open_file_links_directly_m365_desktop_apps_teams_outlook_help_page`; xref: `adobe_acrobat_opening_pdfs_help_page`; xref: `adobe_acrobat_set_default_pdf_program_help_page`; xref: `adobe_acrobat_automatically_open_pdfs_help_page`)

`628` exists so maintainers can say:
**this packet preserved a later open-target / handler layer around same-route detached derivatives, and that layer mattered for how later readers interpreted the packet, but the launch layer itself does not govern the packet and does not silently prove source-native format requirements, official route choice, canonical render environment, required software, or the governing member.**

## Why this is distinct

`592` asks whether a preview-bearing shell and the opened target were silently treated as if they shared one authenticity-adjacent cue posture.

`612` asks whether later evidence preserved **navigation posture** — hyperlinks, action buttons, hotspots, or internal jumps that move the reader within or between packet members.

`626` asks whether a later packet preserved **action posture** — command bars, quick actions, context menus, or disabled commands.

`627` asks whether a later packet preserved **preview posture** — thumbnail tiles, preview panes, preview-mode shells, or partial/full previews.

`628` asks a different question:
**did a later packet add or preserve a visible launch layer — “Open with,” “Open in app,” browser-versus-desktop preference, default handler, or auto-open posture — and did later readers start overreading that layer as if it proved source-native format requirements, official route choice, canonical render environment, required software, or the packet's governing member?**

If the real problem is preview-shell versus opened-target inheritance, use `592`.
If the real problem is click-path navigation, use `612`.
If the real problem is visible commands or affordances, use `626`.
If the real problem is thumbnail or preview posture, use `627`.
Use `628` only when the missing distinction is **wrapper launch-state posture itself**.

## Decision test

Use `628` when all three conditions hold:

1. later evidence preserves or reenacts a **visible open-target or handler layer** around same-route detached derivatives — for example “Open with,” “Open in app,” browser-versus-desktop preference, default app selection, or auto-open posture;
2. that layer is **later wrapper-added launch state**, not proof that the underlying source route itself canonically required the same application, the same render environment, the same handler, or the same target route; and
3. later readers are drifting toward treating that layer as if it proved **source-native format requirements, official route choice, canonical render environment, required software, or the governing member**.

If any condition fails, keep the packet under the narrower doc that already owns the real problem.
If the surviving packet is still mainly a navigation, action, or preview problem with some open-target posture around it, keep navigation in `612`, keep action posture in `626`, keep preview posture in `627`, and add one bounded `628` launch-state note only if the visible open-target / handler layer itself changed the reading.

## Keep navigation, action, preview, portability, and launch state separate

At minimum, keep these layers separate:
1. **current office control** — the current written/help lane and current media head (`194`, `529`, `530`);
2. **surviving detached derivative** — which `595–599` member, if any, the packet actually preserved;
3. **family routing** — whether the packet needed `600` because no single detached derivative dominated;
4. **wrapper-added navigation state** — links, hotspots, jump targets, or internal click paths (`612`);
5. **wrapper-added action state** — command bars, more-action menus, context menus, quick-action buttons, or disabled commands (`626`);
6. **wrapper-added preview state** — thumbnail tiles, preview panes, preview-mode shells, or partial/full previews (`627`);
7. **wrapper-added launch state** — “Open with,” “Open in app,” browser-versus-desktop preferences, default handlers, or auto-open posture (`628`);
8. **carrier wrapper** — slide deck, PDF memo, doc shell, saved page, web archive, issue ticket, or other transport context (`437`, `490`, `600`);
9. **assembly state** — whether later materials also fused several observations into one stronger-looking posture (`591`).

That separation matters because later packets can otherwise make two different mistakes:
- treating a visible open-target choice or default handler as if it proved what the source route itself canonically is or requires, or
- letting a desktop-app / browser preference or file-handler setting become evidence that the packet itself governs the official route, canonical environment, or required software.

`628` exists so the archive can keep that later visible launch layer **truthful but non-governing**.

## Minimal wrapper-launch-state note grammar

When wrapper launch state matters, reviewers SHOULD prefer one compact line in this shape:

`head=<current tuple|none>; governing_member=<595|596|597|598|599|600|none>; wrapper_launch_kind=<open_with|open_in_app|open_in_browser|open_in_teams|default_handler|file_open_preference|auto_open_download|mixed|unknown>; launch_target=<browser|desktop_app|web_app|teams_shell|native_viewer|external_app|mixed|unknown>; launch_scope=<single_item|file_type|workspace|device|browser|os|mixed|unknown>; launch_selection_origin=<per_open_choice|saved_preference|default_handler|admin_policy|extension_or_plugin|mixed|unknown>; source_required_app_proved=<forbid>; official_route_choice_proved=<forbid>; canonical_render_env_proved=<forbid>; governing_member_from_launch_state=<forbid>; carrier_wrapper=<doc_shell|file_manager|document_library|desktop_client|browser_shell|slide_deck|pdf_memo|saved_page|web_archive|ticket|email_thread|none>; cite_default=<head|fallback anchor>; use_628_when=<launch_state_changed_reading>; promote_wrapper_launch_state=<no>; basis=<why the later open-target or handler layer needed one bounded note>`

This is a note contract, not a new schema.
It exists so packets and summaries can say “this later packet also carried visible open-target / handler posture” without minting a new detached-derivative member or silently rewriting source requirements, canonical environment, route choice, or governance.

## Typical uses

1. **Open-in-app overread**
   A later packet shows “Open in app” and later readers start retelling that wrapper choice as if it proved the source route canonically belongs in the desktop app or requires that app to be authoritative.
2. **Browser-versus-desktop preference overread**
   A later packet shows a saved browser/desktop preference and later readers start retelling that workspace preference as if it were the office's own route choice or the packet's governing environment.
3. **Default-handler overread**
   A later packet shows a default app or handler selection and later readers start retelling that local preference as if it proved the source file type's canonical or officially endorsed software.
4. **Auto-open posture overread**
   A later packet shows downloaded files auto-opening and later readers start retelling that wrapper behavior as if it proved immediate source publication, required tooling, or a canonical open target.
5. **Open-with chooser overread**
   A later packet shows several candidate apps and later readers start treating the visible chooser, rather than the current head, as if it defined what the derivative “really is” or how it must be handled.

## When not to use this

Do **not** use `628` when:
- the decisive issue is still preview-shell / opened-target inheritance (`592`),
- the decisive issue is still navigation (`612`),
- the decisive issue is still action posture (`626`),
- the decisive issue is still preview posture (`627`),
- the decisive issue is still print/save/offline/web-archive authority or portability (`437`, `490`),
- the decisive issue is still a mixed detached-derivative packet with no dominant member (`600`),
- or the decisive issue is still cross-state composite assembly (`591`).

If deleting the visible open-target / handler layer leaves an ordinary navigation, action, preview, or portability problem, use the narrower doc and omit `628`.
If deleting it would erase **why a later “Open with,” “Open in app,” default-handler, or browser-versus-desktop layer changed the way the packet was being read or retold**, `628` is probably right.

## Promotion rule

Future media additions should usually **not** be promoted just because a later packet carried an “Open with” menu, an “Open in app” choice, a browser-versus-desktop preference, a default app selection, or auto-open posture.
Tighten `592`, `612`, `626–628`, or `600` first.
Only add another numbered doc when repeated wrapper-launch-state mistakes still cannot be expressed as:
- one governing `595–599` member,
- or a mixed-packet routing note under `600`,
- plus one bounded wrapper-launch-state note under `628`.

## Minimal artifact

This document is intentionally doc-only.
Do **not** add a checklist or payload template for it unless wrapper-launch-state drift still persists after this compact bridge exists.

## Sources

- Google Drive Help — Use Google Drive apps. (xref: `google_drive_use_google_drive_apps_help_page`)
- Google Drive Help — View & open files. (xref: `google_drive_view_open_files_help_page`)
- Microsoft Support — Open a OneDrive or SharePoint file in the desktop app instead of the browser. (xref: `microsoft_open_onedrive_or_sharepoint_file_in_desktop_app_help_page`)
- Microsoft Support — Open file links directly in Microsoft 365 desktop apps from Teams and classic Outlook. (xref: `microsoft_open_file_links_directly_m365_desktop_apps_teams_outlook_help_page`)
- Adobe Acrobat Help — Opening PDFs. (xref: `adobe_acrobat_opening_pdfs_help_page`)
- Adobe Acrobat Help — Set Acrobat as the default PDF program. (xref: `adobe_acrobat_set_default_pdf_program_help_page`)
- Adobe Acrobat Help — Automatically open PDFs. (xref: `adobe_acrobat_automatically_open_pdfs_help_page`)
