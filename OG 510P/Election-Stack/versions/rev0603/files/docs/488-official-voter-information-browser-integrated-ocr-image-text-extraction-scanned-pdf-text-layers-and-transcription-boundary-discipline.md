# 488 — Official voter-information browser-integrated OCR, image text extraction, scanned-PDF text layers, and transcription-boundary discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **official voter-information routes, notices, images, or documents that voters may consume through browser-integrated OCR, image text extraction, or inferred searchable text layers while the original official artifact is already open**:
Chrome PDF-viewer OCR for scanned PDFs,
Firefox text recognition for webpage images,
Safari Live Text on images inside the page,
and similar browser- or platform-integrated features that make text selectable, searchable, copyable, translatable, or action-triggering even when the office originally published that information only as an image or scan.

It does **not** replace the underlying voter-question families in `292–343`.
It does **not** replace:
- `305`, which governs the controlling office/help lane,
- `368`, which governs detached printable artifacts, forwarded PDFs, photographed handouts, and stale-stock retirement **after** the artifact leaves the live page,
- `378`, which governs document downloads, embedded viewers, and file-delivery boundaries,
- `440`, which governs reader mode / simplified view / main-content extraction without OCR-derived transcription,
- `486`, which governs browser-integrated summaries or page-context AI answers from the already-open page,
- `487`, which governs browser-integrated translation and selected-text translation of the already-open page,
- `489`, which governs browser-integrated read aloud, listen-to-page, and page-audio narration once the text layer is spoken aloud,
- `491`, which governs browser-generated image descriptions when the browser infers non-text visual meaning rather than extracting words from the image,
- or `418`, which governs broader screen-reader semantics and nonvisual structure on the route itself.

It adds one narrow rule:
**if an official voter-information route may be consumed through browser-integrated OCR or image/scanned-document text extraction, the office should keep the original artifact and current official help lane recoverable, should not let inferred extracted text masquerade as a reviewed official transcription, and should avoid putting decisive public instructions only inside image text when ordinary text could safely carry them.**

## Why this is a distinct surface

The archive already treats accessibility, language access, and public digital delivery as integrity issues rather than polish. The EAC’s current election-design guidance treats online voter-information materials as core public communications whose clarity, usability, accessibility, and accuracy matter operationally. Federal accessibility guidance already pushes in the same direction: Section 508’s current **Create Accessible PDFs** guidance says agencies should generally prioritize HTML and use PDFs when necessary, while W3C’s current WCAG 2.2 understanding guidance for **Images of Text** says authors should use text rather than pictures of text when the technology can achieve the presentation. Section508.gov’s current alternative-text guidance also says essential text content must live in the main page content rather than only in skipped/background placements. Browser and platform vendors now add a second fact: Chrome’s current PDF guidance says scanned PDFs opened in the Chrome PDF viewer are automatically converted on-device to searchable/selectable text with OCR; Firefox’s current text-recognition guidance says users can copy text from supported webpage images; and Apple’s current Safari guidance says Live Text lets users select, copy, translate, search, and act on text found in a picture on the page. (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`; xref: `section508_create_accessible_pdfs_page`; xref: `w3c_wai_wcag22_images_of_text_page`; xref: `section508_authoring_meaningful_alternative_text_page`; xref: `google_chrome_help_manage_pdfs_page`; xref: `mozilla_support_firefox_text_recognition_page`; xref: `apple_support_safari_interact_with_text_in_picture_page`)

That is enough to justify a compact control here.
A route may pass file-delivery review, printable-artifact review, and even ordinary content review yet still fail first contact because:
- a scanned PDF becomes searchable and the voter copies one extracted line without the table header, footnote, or neighboring exception that gave it meaning,
- an image flyer or infographic exposes text extraction but the extracted text no longer preserves which office, election, or scope label controlled the instruction,
- a browser turns an address, phone number, email, or website inside an image into an immediate action affordance even though the image never carried enough nearby context to make that detached action safe,
- the extracted text is later translated, summarized, searched, or pasted elsewhere and starts to look like an official reviewed text transcript,
- or the office relied on image-only wording for a decisive deadline, location, or exception because it assumed the image itself would always be read as designed.

## This is not the same thing as file delivery or detached print artifacts

`378` asks whether the public can safely cross the boundary into a file or embedded viewer and still know what artifact they received, whether it is current, and where the HTML/help fallback lives.

`368` asks what happens when a postcard, flyer, brochure, infographic, or PDF becomes detached from the live page and keeps circulating as an artifact in its own right.

`488` asks a different question:
**once the original official artifact is already open, does the browser’s own OCR or image-text-extraction layer generate a second, inferred text surface that still keeps the source artifact, scope cues, and safe help route reconstructible?**

A route may pass `368` and `378` and still fail `488` if:
- the PDF link is labeled correctly and current, but the viewer-generated text layer detaches one answer from the rest of the page,
- the infographic is editioned correctly, but its most decisive words exist only as image text that users copy out without the controlling caption or footer,
- or the file is current and downloadable, yet the practical first-contact surface becomes browser-extracted text rather than the authored layout the office reviewed.

## Extracted text is a convenience transcription, not a reviewed official text edition

`488` is about words the browser thinks it can recover from an image or scan. If the browser instead generates a scene/object description for a non-text image, map, photo, or icon-heavy panel, use `491` so inferred visual explanation does not get blurred into OCR-derived transcription.


The boundary here is not whether OCR or image-text extraction is useful.
It often is, especially for accessibility and recoverability.
The boundary is whether the extracted text becomes a hidden second publication track.

For `488`, the public-safe posture is:
- the original page, image, or scanned document remains the source artifact the office actually published,
- any authored HTML or reviewed text equivalent the office provides remains the preferred authoritative text lane,
- browser-generated extracted text remains subordinate to the source artifact plus the current official help lane,
- and unresolved ambiguity routes the voter back to the original artifact or ordinary help rather than pretending the inferred text layer settled the matter.

This matters most where OCR or image extraction can flatten away:
- table columns and row headers,
- captions, side notes, and figure keys,
- visual grouping that distinguished statewide from local rules,
- highlighted warnings or superseding notices,
- footnotes and exception markers,
- or the difference between a heading, an example, and the controlling instruction.

## Image-only decisive text is especially risky

W3C’s current guidance for **Images of Text** says authors should use text instead of pictures of text when the technology can achieve the same presentation. Section508.gov’s current alternative-text guidance likewise says essential text content belongs in the main page content, not only in images or skipped/background placements. (xref: `w3c_wai_wcag22_images_of_text_page`; xref: `section508_authoring_meaningful_alternative_text_page`)

So `488` does **not** require offices to eliminate every screenshot, map, scanned signature block, poster, or infographic.
It does require a narrow discipline:
**do not place action-changing voting instructions only inside image text when ordinary text on the page could safely carry the same meaning.**

A route fails `488` when:
- the deadline itself appears only inside a flyer image,
- the “only at this office” qualifier lives only in a graphic badge,
- the cure or ID exception is visible only inside an image of a table,
- or the image contains the operative phone number or address while the surrounding page text stays too vague to stand on its own.

## Layout-dependent meaning is where extraction most often goes wrong

Browser OCR and image text extraction can make a scan newly searchable or selectable, but they do not guarantee that the extracted text preserves the original reading order, grouping, or weight of the visual layout.
That is especially risky for election materials where meaning often depends on:
- row/column relationships,
- address-specific tables,
- county-vs-state splits,
- deadline plus exception pairs,
- or warnings visually placed close to a button, map, or highlighted block.

For `488`, the page should assume that a voter may copy only the extracted words, not the whole designed layout.
If the answer is not safe in that form, the route should expose a nearby official text/help lane that makes the controlling scope and next step explicit.

## OCR-derived text can become upstream to translation, summary, and action affordances

Once the browser turns image or scan content into selectable text, other layers can immediately act on it.
Safari’s current Live Text guidance says text found in an image can be copied, translated, searched, shared, or used to launch maps, email, and website actions. Chrome’s scanned-PDF OCR guidance says the resulting text can be highlighted, searched, copied, pasted, and found within the document. Firefox’s text-recognition guidance says extracted text is copied to the clipboard and can also be partially selected. Once that extracted text exists, browser-integrated narration layers can speak it aloud as a later convenience surface too. (xref: `apple_support_safari_interact_with_text_in_picture_page`; xref: `google_chrome_help_manage_pdfs_page`; xref: `mozilla_support_firefox_text_recognition_page`)

That makes `488` upstream of nearby controls.
A voter may:
- OCR a scanned PDF,
- copy one line,
- translate, summarize, or have it read aloud,
- search the web for it,
- or launch an address/phone/email action directly from the extracted text.

So `488` is the bounded place where the archive says the inferred text layer itself must remain subordinate **before** later `486` summary behavior, `487` translation behavior, or `489` page-audio behavior can be trusted not to drift further.

## Scanned PDFs need recovery and text-equivalent discipline, not magical trust

Section 508’s current PDF guidance is already the right caution sign: agencies should prefer HTML when possible and use PDFs when needed. Chrome’s OCR guidance is helpful because it can recover searchability and selection for scanned PDFs, but it does not turn every scan into a reviewed, layout-faithful, complete official text edition. (xref: `section508_create_accessible_pdfs_page`; xref: `google_chrome_help_manage_pdfs_page`)

For `488`, that means:
- keep a current HTML/help lane visible when the PDF mostly serves as a printable or portable artifact,
- avoid making the scanned PDF the only place decisive rules live when a normal text lane could exist,
- and do not treat viewer-generated text extraction as proof that the document is now operationally equivalent to a properly authored text page.

## High-risk topics should bias toward routing, not extracted-text confidence

The most dangerous failures are the same topics already treated as risky under `305`, `307`, `311`, `317–343`, and related public-answer surfaces:
- polling-place, drop-box, and early-voting location/hour changes,
- deadline and receipt-rule distinctions,
- ID alternatives and cure paths,
- disability, language, jail/facility, disaster, or new-citizen edge cases,
- and any answer that should move the voter into ordinary help or rights/safety escalation.

For those topics, `488` does not ask the browser’s OCR to become perfect.
It asks the office to keep the **safe official routing answer** visible enough that extracted text remains a convenience layer rather than a shadow transcript carrying more authority than it deserves.

## Minimal state taxonomy

A small taxonomy is enough:

1. **official_text_equivalent_available_extracted_text_subordinate**
2. **scanned_pdf_ocr_available_original_artifact_recoverable**
3. **image_text_extraction_available_not_safe_as_complete_answer**
4. **layout_dependent_meaning_not_portable_through_extraction**
5. **ocr_derived_translation_or_summary_subordinate_to_source**
6. **extraction_feature_blocked_disabled_or_unavailable**
7. **extraction_conflict_under_review_route_to_official_help**

## Bounded OCR / text-extraction trace minimum

The archive does **not** need per-user OCR logs, copied extracted text transcripts, or telemetry about exactly what a voter highlighted.
But a voter-information OCR/extraction surface should preserve a bounded trace for action-changing outputs.

At minimum, that trace should make it possible to reconstruct:
- which official routes or artifacts were reviewed for OCR/image-text-extraction behavior,
- whether a reviewed authored text equivalent existed separately,
- whether the reviewed context was scanned-PDF OCR, image text extraction, or both,
- what source-artifact recovery or official help lane the page exposed,
- what layout-dependency or non-equivalence warning controlled,
- and when the review was last performed.

Prefer **route identifiers, artifact identifiers, reviewed extraction-context labels, text-equivalent availability notes, recovery/help anchors, policy notes, and timestamps** over copied OCR output, individualized clipboard history, or collections of extracted text fragments.

## Minimal claim-set

A jurisdiction can publish a compact, verifiable claim-set:

1. **OCR/extraction surface claim:** the office reviewed one or more official voter-information routes or artifacts for browser-integrated OCR or image-text-extraction behavior.
2. **Subordination claim:** extracted text remains subordinate to the original artifact plus any reviewed authored text/help lane.
3. **Text-equivalent claim:** when decisive information exists in a scan or image, the office evaluated whether a safe authored text equivalent or help path is available.
4. **Layout-dependency claim:** contexts where layout, table structure, or nearby warnings are necessary are not silently treated as portable plain text.
5. **Downstream-transform claim:** OCR-derived text is not silently promoted into an official translation, summary, or complete answer merely because later browser features can act on it.
6. **Recovery claim:** the voter can recover the original artifact and current official help lane without guesswork.
7. **Privacy-minimization claim:** the office does not retain individualized OCR outputs or clipboard histories when bounded policy evidence is enough.

## Canonical digest artifacts

Publish **digests of OCR / extraction review posture**, not extracted-text dumps.

- **OCR Surface Digest (OSD):** digest of the bounded public OCR/extraction posture payload for a scope.
- **Extraction Context Review Digest (ECRD):** optional digest proving which extraction contexts were reviewed for a route class.
- **Original Artifact Recovery Digest (OARD):** optional digest proving how the voter can recover the source artifact or current official help lane.
- **Layout Dependency Warning Digest (LDWD):** optional digest proving the current warning/routing posture when extracted text is not safe to treat as complete.

## What belongs in the public OCR / extraction payload

Keep the payload **small, bounded, and explicit about non-equivalence**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id`
- human `browser_ocr_surface_label`
- `delivery_role_note`
- `covered_surface_refs`
- `official_source_anchors`
- `reviewed_extraction_contexts[]`
- `official_text_equivalent_note`
- `extraction_boundary_note`
- `layout_dependency_note`
- `downstream_transform_boundary_note`
- `original_artifact_recovery_note`
- `high_risk_topic_routing_note`
- `privacy_minimization_note`
- `latest_notice_uri`
- `last_verified_at`
- optional `supersedes` / `superseded_by`

Do **not** publish by default:
- copied OCR transcripts,
- per-user clipboard histories,
- raw OCR confidence logs,
- shadow text editions generated only by the browser,
- or large image/PDF dumps merely to prove the posture was reviewed.

## How this fits the family map

Use `488` when the right official page, image, or scan is already open, but a browser-integrated OCR or image-text-extraction layer can still make inferred plain text look more authoritative, more portable, or more complete than the office intended.

Use nearby controls when the problem is instead:
- how a printable/downloadable artifact behaves once it circulates as its own object (`368`),
- how a file or embedded viewer is handed off and labeled (`378`),
- how reader mode or simplified view extracts ordinary HTML text (`440`),
- whether a browser summary or page-context AI layer compresses the already-open page (`486`),
- whether a browser translation layer rewrites the already-open page or extracted text (`487`),
- whether a browser read-aloud or page-audio layer speaks the already-open page or extracted text (`489`),
- or whether the voter must escalate to ordinary help or rights/safety routing (`305`, `307`).

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/official-voter-information-browser-ocr-surface-payload.json`
- Operator quickcheck: `artifacts/checklists/official-voter-information-browser-ocr-surface-checklist.md`

## Sources (pinned IDs / lockfile IDs)

- EAC: Effective Design for the Administration of Federal Elections (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`)
- Section 508: Create Accessible PDFs (xref: `section508_create_accessible_pdfs_page`)
- W3C WAI: Understanding SC 1.4.5 Images of Text (xref: `w3c_wai_wcag22_images_of_text_page`)
- Section508.gov: Authoring Meaningful Alternative Text (xref: `section508_authoring_meaningful_alternative_text_page`)
- Google Chrome Help: Manage PDFs in Chrome (xref: `google_chrome_help_manage_pdfs_page`)
- Mozilla Support: Copy text from images on Firefox for MacOS (xref: `mozilla_support_firefox_text_recognition_page`)
- Apple Support: Interact with text in a picture in Safari on Mac (xref: `apple_support_safari_interact_with_text_in_picture_page`)
