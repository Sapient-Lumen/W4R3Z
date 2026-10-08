# 604 — Official voter-information platform media authenticity-cue packet redactions, hidden content, and non-governing wrapper-concealment firewall

**Track:** Shared / Public surfaces

This document defines a bounded control for **later packet-level concealment around same-route detached derivatives**:
redacted text,
redacted images,
cropped-away packet regions used to hide part of a page,
hidden slides,
hidden page objects,
or similar later wrapper-added concealment that changes what a packet visibly shows without proving that the official source route itself lacked that content.

It does not create a new authenticity cue family.
It adds one narrow rule:
**when a later packet hides, redacts, or suppresses part of same-route detached derivatives, the archive should preserve that wrapper-concealment fact honestly and should not quietly treat the concealed region as if it were source-level absence, source-native redaction, or the packet's governing member.**

It composes with:
- `docs/194-synthetic-media-and-comms-authenticity-minimum-controls.md`
- `docs/437-official-voter-information-portable-records-print-save-to-pdf-and-off-screen-fidelity-fail-open-discipline.md`
- `docs/490-official-voter-information-browser-managed-reading-lists-offline-saved-pages-and-web-archive-authority-boundary-discipline.md`
- `docs/523-official-voter-information-platform-media-boundary-quickmap-and-duplicate-firewall.md`
- `docs/530-official-voter-information-platform-media-chain-citations-head-first-reference-and-historical-leg-scoping-discipline.md`
- `docs/591-official-voter-information-platform-media-authenticity-cue-observation-assembly-cross-state-composites-and-no-faux-single-state-firewall.md`
- `docs/594-official-voter-information-platform-media-authenticity-cue-observation-windows-clipped-captures-and-non-totality-firewall.md`
- `docs/595-official-voter-information-platform-media-authenticity-cue-text-extracts-transcript-caption-ocr-derivatives-and-non-carried-cue-firewall.md`
- `docs/597-official-voter-information-platform-media-authenticity-cue-still-image-extracts-frame-grabs-poster-exports-and-non-carried-cue-firewall.md`
- `docs/598-official-voter-information-platform-media-authenticity-cue-metadata-extracts-title-description-chapter-list-derivatives-and-non-carried-cue-firewall.md`
- `docs/600-official-voter-information-platform-media-authenticity-cue-detached-derivative-family-quickmap-mixed-packets-and-anti-fragmentation-firewall.md`
- `docs/601-official-voter-information-platform-media-authenticity-cue-packet-labels-filenames-subject-lines-and-non-governing-wrapper-narrative-firewall.md`
- `docs/602-official-voter-information-platform-media-authenticity-cue-packet-synopses-forwarding-comments-speaker-notes-and-non-governing-wrapper-summary-firewall.md`
- `docs/603-official-voter-information-platform-media-authenticity-cue-packet-markup-highlights-arrows-and-non-governing-wrapper-emphasis-firewall.md`

## Why this exists (bounded)

The archive already distinguishes detached stills (`597`), copied text (`595`), copied metadata (`598`), clipped observation windows (`594`), mixed detached-derivative packets (`600`), short wrapper labels (`601`), longer wrapper summaries (`602`), and wrapper-added emphasis markup (`603`).
A smaller but still important seam remains:
**a later packet can hide part of what it preserved — by redaction, crop-hide, hidden-slide posture, hidden-object posture, or similar wrapper concealment — and later readers can start narrating that concealment as if the official source route itself lacked, withdrew, or natively masked the hidden material.**

Current primary-source guidance is specific enough to justify one compact bridge here.
Apple's current Preview guidance says a PDF annotation workflow includes redaction and a crop tool that can hide part of a PDF.
Microsoft's current PowerPoint guidance says a slide can be hidden without being deleted.
Microsoft's current Selection Pane guidance says an object can be hidden while remaining in the file but no longer visible on the document or slide.
(xref: `apple_preview_annotate_pdf_mac_help_page`; xref: `microsoft_hide_or_show_slide_help_page`; xref: `microsoft_selection_pane_manage_objects_help_page`)

That is enough to support one bounded maintainer rule:
**later packet concealment is still only later packet concealment.**
A redacted transcript excerpt, a blacked-out frame grab, a crop-hidden PDF region, a hidden slide, or a hidden page object can honestly be part of the packet that later readers saw while still failing to prove that the source route itself lacked, withdrew, or natively concealed the hidden material.
`604` exists so the archive can preserve that concealment fact without quietly promoting packet-level suppression into source-level absence.

## This is not the same thing as `594`, `597`, `595`, `600`, `603`, `601`, `602`, `591`, `437`, or `490`

`594` asks whether a later screenshot, crop, clipped embed, or other narrow observation window preserved only part of the route.

`597` asks whether the decisive surviving artifact is the detached still-image derivative itself.

`595` asks whether the decisive surviving artifact is copied source text.

`600` asks how to route a mixed same-route packet when several detached derivatives coexist and no single `595–599` member clearly dominates.

`603` asks whether later wrapper-added markup or emphasis such as highlight boxes, arrows, circles, underlines, comment anchors, zoom callouts, or ink starts sounding like source-native emphasis or like the packet's governing member.

`601` asks whether later packet titles, filenames, subject lines, memo headings, or similar short wrapper-added labels were mistaken for source metadata or for the governing member.

`602` asks whether later forwarding comments, share messages, speaker notes, memo-body summaries, or similar longer wrapper-added prose were mistaken for copied source language, copied metadata, or for the governing member.

`591` asks whether later materials fused observations from different routes, times, viewer conditions, or interaction states into one faux simultaneous posture.

`437` and `490` ask whether print/save/offline/web-archive carriers changed the authority or portability posture of the already-open route.

`604` asks a different question:
**did a later packet add its own concealment layer around same-route detached derivatives, and did later readers start overreading that hidden region as if it proved source-level absence, source-native redaction, or the packet's governing member?**

If the real problem is the clipped observation window itself, use `594`.
If the real problem is the detached still itself, use `597`.
If the real problem is copied source text, use `595`.
If the real problem is mixed detached-derivative routing, use `600`.
If the real problem is wrapper-added emphasis, use `603`.
If the real problem is a short wrapper-added label, use `601`.
If the real problem is wrapper-added summary prose, use `602`.
If the real problem is later composite assembly across states, use `591`.
If the real problem is print/save/offline/web-archive authority or portability, use `437` or `490`.
Use `604` only when the decisive ambiguity is **wrapper-added concealment or suppression inside the packet** rather than copied source content.

## Default rule: classify the surviving derivative first; treat later wrapper concealment as descriptive unless provenance proves otherwise

By default, later notes SHOULD still cite the current controlling head under `530`, or the fallback anchor if the chain is headless.
A `604` note exists only to explain one bounded concealment mistake around that head.

Use this triage order:
1. if the decisive issue is still copied source text, use `595`;
2. if the decisive issue is still a detached still-image derivative, use `597`;
3. if the decisive issue is still copied source metadata, use `598`;
4. if the decisive issue is still a mixed detached-derivative packet with no dominant member, use `600`;
5. if the decisive issue is still short wrapper-added labeling, use `601`;
6. if the decisive issue is still longer wrapper-added summary prose, use `602`;
7. if the decisive issue is still wrapper-added emphasis or annotation, use `603`;
8. if the decisive issue is still cross-state composite assembly, use `591`;
9. if the decisive issue is still saved-page / print / offline portability or authority boundary, use `437` or `490`;
10. use `604` only when the decisive issue is that **a later wrapper redaction, hidden slide, hidden object, crop-hide, or similar concealment changed what the packet visibly exposed and later retellings started treating that concealment as source fact.**

That means `604` is not a new citation lane.
It is a compact bridge for one bounded sentence saying that the packet carried later wrapper concealment and that this concealment should not be silently upgraded into source absence, source-native redaction, or governing-member proof.

## Keep source-derived content and wrapper-added concealment separate

At minimum, keep these layers separate:
1. **current office control** — the current written/help lane and current media head (`194`, `369`, `529`, `530`);
2. **surviving detached derivative** — which `595–599` member, if any, the packet actually preserved;
3. **family routing** — whether the packet needed `600` because no single detached derivative dominated;
4. **source-derived text** — transcript/caption/OCR or other copied route text (`595`);
5. **source-derived metadata** — labels copied from the official route itself (`598`);
6. **wrapper-added packet label** — filename, subject line, slide title, memo heading, or similar short later-added narrative (`601`);
7. **wrapper-added summary prose** — forwarding comments, share messages, speaker notes, memo-body summaries, or similar longer later packet narrative (`602`);
8. **wrapper-added markup/emphasis** — highlight boxes, circles, arrows, underlines, comment anchors, zoom lenses, ink, or similar later visual emphasis (`603`);
9. **wrapper-added concealment/suppression** — redactions, crop-hidden regions, hidden slides, hidden objects, or similar later visual withholding (`604`);
10. **carrier wrapper** — slide deck, PDF memo, annotated screenshot, chat export, saved page, web archive, issue ticket, or other transport context (`437`, `490`, `600`);
11. **assembly state** — whether later materials also fused several observations into one stronger-looking posture (`591`).

That separation matters because later packets can otherwise make two opposite mistakes:
- treating wrapper-added concealment as if it proved source-level absence or source-native redaction, or
- letting the concealment layer become the governing member instead of first classifying the surviving detached derivative.

`604` exists so the archive can keep that later withholding layer **truthful but non-governing**.

## Minimal wrapper-concealment note grammar

When wrapper-concealment overread itself matters, reviewers SHOULD prefer one compact line in this shape:

`head=<current tuple|none>; governing_member=<595|596|597|598|599|600|none>; wrapper_concealment_kind=<redaction|crop_hide|hidden_slide|hidden_object|hidden_page_region|mixed|unknown>; wrapper_concealment_origin=<later_wrapper_added|copied_from_source|mixed|unknown>; treat_concealment_as_source_absence=<forbid>; treat_concealment_as_source_redaction=<forbid>; treat_concealment_as_governing_member=<forbid>; carrier_wrapper=<slide_deck|pdf_memo|annotated_screenshot|chat_export|saved_page|web_archive|ticket|email_thread|doc_comment_layer|none>; cite_default=<head|fallback anchor>; use_604_when=<wrapper_concealment_changed_visible_packet_scope>; promote_wrapper_concealment=<no>; basis=<why the later concealment needed one bounded note>`

This is a note contract, not a new schema.
It exists so packets and summaries can say “this packet later hid part of what it preserved” without minting a new detached-derivative member or silently rewriting source provenance.

## Typical uses

1. **Redaction overread**
   A packet preserves a transcript excerpt but later redacts one line, and later readers start retelling the packet as if the source route itself omitted that line.
2. **Crop-hide overread**
   A PDF packet preserves a same-route still-image derivative but later crops away one corner, and later readers start treating the missing corner as if it were disproved absent on the source route.
3. **Hidden-slide overread**
   A presentation packet preserves several same-route derivatives but later hides one slide, and later readers start treating the visible deck as if the source packet never included that material.
4. **Hidden-object overread**
   A later presentation copy hides one arrow, textbox, or image object and later readers start treating that invisibility as if the original packet lacked it.
5. **Mixed concealment overread**
   A packet uses both redaction and hidden-object posture, and later readers start treating the resulting visible subset as if it were the source route's whole preserved derivative record.

## When not to use this

Do **not** use `604` when:
- the decisive issue is still copied source text (`595`),
- the decisive issue is still the detached still-image derivative itself (`597`),
- the decisive issue is still copied source metadata (`598`),
- the decisive issue is still a mixed detached-derivative packet with no dominant member (`600`),
- the decisive issue is still a short wrapper-added label (`601`),
- the decisive issue is still longer wrapper-added summary prose (`602`),
- the decisive issue is still wrapper-added emphasis or annotation (`603`),
- the decisive problem is still print/save/offline/web-archive authority or portability (`437`, `490`),
- or the decisive problem is still cross-state composite assembly (`591`).

If deleting the concealment leaves an ordinary text derivative, still-image derivative, metadata derivative, mixed packet, label problem, summary-prose problem, markup problem, saved-page issue, or composite-assembly claim, use the narrower doc and omit `604`.
If deleting it would erase **why a later redaction, hidden slide, hidden object, or crop-hide layer changed the way the packet was being routed or retold**, `604` is probably right.

## Promotion rule

Future media additions should usually **not** be promoted just because a later packet used redaction, crop-hide, hidden-slide, hidden-object, or similar wrapper-added concealment around same-route detached derivatives.
Tighten `594`, `595`, `597`, `600`, `603`, or `604` first.
Only add another numbered doc when repeated concealment mistakes still cannot be expressed as:
- one governing `595–599` member,
- or a mixed-packet routing note under `600`,
- plus one bounded wrapper-label note under `601`,
- plus one bounded wrapper-summary note under `602`,
- plus one bounded wrapper-markup note under `603`,
- plus one bounded wrapper-concealment note under `604`.

## Minimal artifact

This document is intentionally doc-only.
Do **not** add a checklist or payload template for it unless wrapper-concealment drift still persists after this compact bridge exists.

## Sources

- Apple Support — Annotate a PDF in Preview on Mac. (xref: `apple_preview_annotate_pdf_mac_help_page`)
- Microsoft Support — Hide or show a slide. (xref: `microsoft_hide_or_show_slide_help_page`)
- Microsoft Support — Use the Selection pane to manage objects in documents. (xref: `microsoft_selection_pane_manage_objects_help_page`)
