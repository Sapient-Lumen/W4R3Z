# 643 — Official voter-information platform media authenticity-cue packet CC on/off caption language appearance and non-governing wrapper-caption-state firewall

**Track:** Shared / Public surfaces

This document covers a narrow packet-wrapper problem:
**later packets can preserve captions-on posture, CC-off state, selected caption language, auto-generated-caption defaults, caption appearance customizations, default-on embed caption posture, caption menus, or similar visible wrapper caption-state layers around same-route detached derivatives, and later readers can start mistaking that caption posture for burned-in source text, a reviewed official translation, source-native line breaking or emphasis, source-native accessibility styling, or the packet's governing member.**

It composes with:
- `docs/194-synthetic-media-and-comms-authenticity-minimum-controls.md`
- `docs/492-official-voter-information-browser-integrated-live-captions-subtitle-translation-and-transcript-boundary-discipline.md`
- `docs/523-official-voter-information-platform-media-boundary-quickmap-and-duplicate-firewall.md`
- `docs/529-official-voter-information-platform-media-chain-heads-current-control-and-closeout-discipline.md`
- `docs/530-official-voter-information-platform-media-chain-citations-head-first-reference-and-historical-leg-scoping-discipline.md`
- `docs/545-official-voter-information-platform-media-text-track-selection-states-caption-subtitle-language-picks-and-head-default-retention-discipline.md`
- `docs/591-official-voter-information-platform-media-authenticity-cue-observation-assembly-cross-state-composites-and-no-faux-single-state-firewall.md`
- `docs/595-official-voter-information-platform-media-authenticity-cue-text-extracts-transcript-caption-ocr-derivatives-and-non-carried-cue-firewall.md`
- `docs/600-official-voter-information-platform-media-authenticity-cue-detached-derivative-family-quickmap-mixed-packets-and-anti-fragmentation-firewall.md`
- `docs/637-official-voter-information-platform-media-authenticity-cue-packet-spelling-grammar-autocorrect-proofing-language-and-non-governing-wrapper-proofing-state-firewall.md`
- `docs/638-official-voter-information-platform-media-authenticity-cue-packet-translated-renderings-show-original-and-non-governing-wrapper-translation-state-firewall.md`
- `docs/641-official-voter-information-platform-media-authenticity-cue-packet-transcript-panes-current-line-highlights-search-and-non-governing-wrapper-transcript-state-firewall.md`
- `docs/642-official-voter-information-platform-media-authenticity-cue-packet-auto-quality-data-saver-resolution-picks-and-non-governing-wrapper-rendition-state-firewall.md`

## What this is for

Use `643` when a later packet preserves or reenacts a **visible wrapper caption-state layer** around same-route detached derivatives:
- captions turned on or off,
- selected caption/subtitle language,
- `Always show captions` / include-auto-generated-caption posture,
- caption menu open with one track selected,
- caption appearance customization such as font, size, color, background, or edge style,
- default-on embed text-track posture,
- or similar later packet caption foregrounding.

Those caption surfaces are real packet facts and should be preserved honestly.
But they are still **later wrapper-added caption-display / caption-selection posture**, not automatic proof of:
- source-burned subtitle text,
- a reviewed official translation,
- source-native line breaking or emphasis,
- source-native accessibility styling,
- or the packet's governing member.

Current primary-source guidance is already enough to justify one bounded caption-state bridge.
YouTube Help says viewers can turn captions on or off, always show captions, include auto-generated captions when available, and change default caption font/style/language settings.
Vimeo Help says viewers can turn captions or subtitles on/off, choose among available tracks, and embeds can default a chosen text track while viewers still retain the ability to turn captions off or switch languages.
Microsoft Support says viewers can turn captions on or off, select the available caption language, and customize caption display through Playback settings > Caption settings with choices like size and color that last only for the browser session.
That is enough for one bounded firewall here.
(xref: `youtube_manage_caption_settings_help_page`; xref: `vimeo_viewing_captions_subtitles_help_page`; xref: `vimeo_embed_default_texttrack_help_page`; xref: `microsoft_video_transcripts_and_captions_help_page`)

`643` exists so maintainers can say:
**this packet preserved a later caption on/off/language/style/default layer around same-route detached derivatives, and that layer mattered for how later readers interpreted the packet, but the caption layer itself does not silently prove burned-in source text, a reviewed official translation, source-native line breaking or emphasis, source-native accessibility styling, or the governing member.**

## Why this is distinct

`492` asks whether browser- or platform-generated live captions, subtitle translation, or transcript-like overlays became the real boundary problem.

`545` asks whether the same current media object preserved **selected text-track state** — captions on/off, subtitle language selected, auto-translate chosen, or embed-default text tracks — while the same object still controlled.

`595` asks whether a later packet preserved **detached text extracts** — transcript lines, caption text, OCR text, or downloaded text tracks that survived outside the whole route.

`637` asks whether a later packet preserved **proofing posture** — spelling/grammar underlines, autocorrect replacements, or proofing-language badges.

`638` asks whether a later packet preserved **translation posture** — translated renderings, selected-text translation popups, or show-original posture.

`641` asks whether a later packet preserved **transcript-navigation posture** — transcript panes, current-line highlights, transcript search, or transcript-language/timestamp toggles.

`642` asks whether a later packet preserved **rendition / fidelity posture** — `Auto`, `Data saver`, visible resolution picks, or quality-menu state.

`643` asks a different question:
**did a later packet add or preserve a visible caption-display / caption-selection layer — CC on/off, selected caption language, auto-generated-caption inclusion, caption appearance customization, default-on embed caption posture, or caption-menu state — and did later readers start overreading that layer as if it proved burned-in source text, a reviewed official translation, source-native line breaking or emphasis, source-native accessibility styling, or the packet's governing member?**

If the real problem is browser-generated live captions or subtitle translation, use `492`.
If the real problem is same-object text-track state while the current head still controls, use `545`.
If the real problem is detached caption/transcript text surviving outside the route, use `595`.
If the real problem is proofing, translation, transcript, or rendition posture, use `637`, `638`, `641`, or `642`.
Use `643` only when the missing distinction is **wrapper caption-state posture itself**.

## Decision test

Use `643` when all three conditions hold:

1. later evidence preserves or reenacts a **visible caption layer** around same-route detached derivatives — for example CC-on posture, captions-off state, selected caption language, auto-generated-caption inclusion, caption-menu state, caption appearance customization, or default-on embed captions;
2. that layer is **later wrapper-added caption-display / caption-selection state**, not proof that the underlying source route itself officially burned subtitle text into the source, officially reviewed the selected translation, officially privileged one line break or emphasis choice, officially adopted one accessibility style, or officially made the packet governing; and
3. later readers are drifting toward treating that layer as if it proved **burned-in source text, a reviewed official translation, source-native line breaking or emphasis, source-native accessibility styling, or the governing member**.

If any condition fails, keep the packet under the narrower doc that already owns the real problem.
If the surviving packet is still mainly a browser-generated live-caption problem, same-object text-track-state problem, detached-text-derivative problem, proofing-state problem, translation-state problem, transcript-state problem, or rendition-state problem with some visible caption posture around it, keep browser-generated captioning in `492`, keep same-object text-track state in `545`, keep detached text carry in `595`, keep proofing posture in `637`, keep translation posture in `638`, keep transcript posture in `641`, keep rendition posture in `642`, and add one bounded `643` caption-state note only if the visible caption layer itself changed the reading.

## Keep caption state, text-track state, detached text carry, proofing, translation, transcript, and rendition separate

At minimum, keep these layers separate:
1. **current office control** — the current written/help lane and current media head (`194`, `529`, `530`);
2. **surviving detached derivative** — which `595–599` member, if any, the packet actually preserved;
3. **family routing** — whether the packet needed `600` because no single detached derivative dominated;
4. **browser-generated caption/translation overlays** — live captions or browser subtitle translation that were not merely the platform player's own text-track/caption shell (`492`);
5. **same-object text-track state** — captions on/off, selected caption language, auto-translate, or embed-default text tracks while the same object stayed current (`545`);
6. **detached text carry** — copied transcript/caption/OCR text that survived outside the whole route (`595`);
7. **wrapper-added proofing state** — spelling/grammar marks or proofing-language badges around visible caption text (`637`);
8. **wrapper-added translation state** — show-original posture, translated renderings, or language-pair badges (`638`);
9. **wrapper-added transcript state** — transcript panes, current-line highlights, transcript search, or transcript-language/timestamp toggles (`641`);
10. **wrapper-added rendition state** — visible quality selectors or fidelity posture that changed how captions looked or whether they seemed legible (`642`);
11. **wrapper-added caption state** — CC on/off posture, selected caption language, auto-generated-caption inclusion, caption appearance customization, caption-menu state, or default-on embed captions around detached derivatives (`643`);
12. **carrier wrapper** — slide deck, PDF memo, browser shell, doc shell, saved page, ticket, or email thread (`437`, `490`, `600`);
13. **assembly state** — whether later materials also fused several observations into one stronger-looking posture (`591`).

That separation matters because later packets can otherwise make two different mistakes:
- treating a visible caption shell as if it proved the source itself contained burned-in subtitles, officially reviewed translated text, or source-native emphasis/segmentation; or
- letting a later caption wrapper become evidence that the packet itself is governance-bearing rather than just a later display layer around one preserved derivative.

`643` exists so the archive can keep that later visible caption layer **truthful but non-governing**.

## Minimal wrapper-caption-state note grammar

When wrapper caption state matters, reviewers SHOULD prefer one compact line in this shape:

`head=<current tuple|none>; governing_member=<595|596|597|598|599|600|none>; wrapper_caption_kind=<captions_on|captions_off|caption_language_selected|caption_menu_open|auto_generated_caption_included|caption_style_customized|embed_default_caption_on|mixed|unknown>; caption_basis=<creator_uploaded|auto_generated|translated|unknown>; display_style_scope=<default|viewer_customized|session_customized|unknown>; source_burned_in_text_proved=<forbid>; official_translation_proved=<forbid>; source_line_breaking_proved=<forbid>; source_accessibility_style_proved=<forbid>; governing_member_from_caption_state=<forbid>; carrier_wrapper=<browser_shell|doc_shell|pdf_shell|review_shell|slide_deck|saved_page|ticket|email_thread|none>; cite_default=<head|fallback anchor>; use_643_when=<caption_state_changed_reading>; promote_wrapper_caption_state=<no>; basis=<why the later caption layer needed one bounded note>`

This is a note contract, not a new schema.
It exists so packets and summaries can say “this later packet also carried captions on / off / language / style / default-on embed posture” without minting a new detached-derivative member or silently rewriting source text burn-in, translation authority, source-native emphasis, accessibility styling, or packet governance.

## Typical uses

1. **CC-on screenshot overread**
   A later packet shows captions turned on and later readers start retelling those visible lines as if they were burned into the source video itself rather than as a viewer-side caption layer.
2. **Caption-language overread**
   A later packet shows one selected caption language and later readers start treating that selection as if it were the office's reviewed official translation rather than a later caption-state choice.
3. **Caption-style overread**
   A later packet shows enlarged/high-contrast/customized captions and later readers start treating that style, segmentation, or emphasis as if it were source-native accessibility styling or source-native line breaking.
4. **Default-on embed overread**
   A later packet preserves an embed that defaulted captions on or defaulted one text track and later readers start treating that embed posture as if it were the office's universal or governing presentation choice.

## When not to use this

Do **not** use `643` when:
- the decisive issue is still browser- or platform-generated live captions / subtitle translation (`492`),
- the decisive issue is still same-object text-track selection state (`545`),
- the decisive issue is still detached transcript/caption/OCR text (`595`),
- the decisive issue is still proofing posture around visible text (`637`),
- the decisive issue is still translation / show-original posture (`638`),
- the decisive issue is still transcript-pane or transcript-search posture (`641`),
- the decisive issue is still rendition / quality posture (`642`),
- the decisive issue is still a mixed detached-derivative packet with no dominant member (`600`),
- or the decisive issue is still cross-state composite assembly (`591`).

If deleting the visible caption layer leaves an ordinary browser-generated-caption, same-object text-track, detached-text, proofing-state, translation-state, transcript-state, or rendition-state problem, use the narrower doc and omit `643`.
If deleting it would erase **why a later CC-on/off/language/style/default layer changed the way the packet was being read or retold**, `643` is probably right.

## Promotion rule

Future media additions should usually **not** be promoted just because a later packet carried captions on/off posture, caption language selection, auto-generated-caption inclusion, caption-style customization, default-on embed captions, or a caption menu around same-route detached derivatives.
Tighten `492`, `545`, `595`, `600`, `637`, `638`, `641`, `642`, or `643` first.
Only add another numbered doc when repeated wrapper-caption-state mistakes still cannot be expressed as:
- one governing `595–599` member,
- or a mixed-packet routing note under `600`,
- plus one bounded wrapper-caption-state note under `643`.

## Minimal artifact

This document is intentionally doc-only.
Do **not** add a checklist or payload template for it unless wrapper-caption-state drift still persists after this compact bridge exists.

## Sources

- YouTube Help — Manage caption settings. (xref: `youtube_manage_caption_settings_help_page`)
- Vimeo Help Center — How to enable or disable captions and subtitles while viewing a video. (xref: `vimeo_viewing_captions_subtitles_help_page`)
- Vimeo Help Center — Enable captions and subtitles in embeds by default. (xref: `vimeo_embed_default_texttrack_help_page`)
- Microsoft Support — View, edit, and manage video transcripts and captions. (xref: `microsoft_video_transcripts_and_captions_help_page`)
