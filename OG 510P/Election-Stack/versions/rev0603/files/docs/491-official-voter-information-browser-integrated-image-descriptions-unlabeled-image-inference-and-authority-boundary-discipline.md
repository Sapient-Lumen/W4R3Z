# 491 — Official voter-information browser-integrated image descriptions, unlabeled-image inference, and authority-boundary discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **official voter-information routes whose already-open page may be interpreted through browser- or platform-integrated generated image descriptions for unlabeled or weakly labeled images**:
polling-place or drop-box photos,
map snapshots,
infographics,
icon-heavy status cards,
ID-example images,
ballot-envelope examples,
step diagrams,
and similar official routes where the live page may be current but a browser or assistive layer can still synthesize a descriptive caption that starts to look like reviewed official explanatory text.

It does **not** replace the underlying voter-question families in `292–343`.
It does **not** replace:
- `305`, which governs the authoritative office/help lane,
- `418`, which governs authored screen-reader semantics, landmarks, labels, and live-update announcements,
- `440`, which governs reader-mode / simplified extraction of authored page content,
- `488`, which governs OCR, image text extraction, and scanned-document transcription boundaries,
- `489`, which governs browser-integrated page-audio narration of already-authored page text,
- or `492`, which governs browser- or platform-generated live captions and translated subtitles over already-open official media.
- or `489`, which governs browser-integrated page-audio narration of already-authored page text.

It adds one narrow rule:
**if an official voter-information route may be encountered through browser-integrated generated image descriptions, the office should not let inferred image captions masquerade as reviewed official alt text or explanatory copy, and should avoid putting decisive public meaning only inside images when ordinary text or authored text alternatives can safely carry it.**

## Why this is a distinct surface

The EAC’s current **Effective Design for the Administration of Federal Elections** treats online voter-information materials as core election communications and emphasizes clarity, understandability, and accessibility. Digital.gov’s current digital-first public-experience guidance says public digital services should be accessible and easy to understand. W3C’s current WCAG 2.2 understanding guidance for **Non-text Content** says information conveyed by non-text content should have a text alternative serving the equivalent purpose. Section508.gov’s current alternative-text guidance says alt text should convey the meaning of the image for users who rely on screen readers. At the same time, current browser/platform support now turns missing or weak image descriptions into a live generated surface: Chrome can provide image descriptions from Google for screen-reader users and says those descriptions may not be fully accurate; Edge can detect unlabeled images and generate descriptions for screen readers on any website; Apple says VoiceOver Recognition can describe images in apps and on the web when support such as alt text or ARIA labels is missing, and Apple’s Mac VoiceOver guidance says those on-device descriptions should not be relied upon in high-risk situations. (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`; xref: `digital_gov_requirements_digital_first_public_experience_page`; xref: `w3c_wcag22_non_text_content_page`; xref: `section508_authoring_meaningful_alternative_text_page`; xref: `google_chrome_get_image_descriptions_page`; xref: `microsoft_support_edge_accessibility_features_page`; xref: `apple_support_voiceover_recognition_iphone_ipad_page`; xref: `apple_support_voiceover_recognition_settings_mac_page`)

That is enough to justify a compact control here.
A route may pass ordinary accessibility, OCR, and portable-record review yet still fail the public because:
- the decisive meaning lives in a map, legend, icon set, or photo that never got a trustworthy authored text equivalent,
- the browser invents a plausible caption for an unlabeled image and that caption sounds more definite than the office ever reviewed,
- a generated description names the wrong object, relationship, or emphasis and starts to act like the page’s official explanation,
- the image has text-free visual meaning that OCR will not catch but the voter still needs,
- or a helper hears a screen-reader-generated image description and reasonably treats it as official when the office only intended the surrounding page text to control.

## This is not the same thing as screen-reader semantics or OCR

`418` asks whether the office authored a nonvisual path with usable landmarks, labels, names, relationships, and live-update announcements.

`488` asks whether browsers can extract **text** from an image, scan, or PDF and let that extracted text start acting like a reviewed transcript.

`491` asks a different question:
**when the browser or platform generates a descriptive caption for a non-text image on the already-open official page, does that inferred description remain visibly subordinate to the page’s reviewed official text and help lane?**

A route may pass `418` and `488` and still fail `491` if:
- landmarks and labels are fine, but the critical polling-place photo or entrance diagram has no trustworthy authored text equivalent,
- OCR can read the words inside an infographic, but not the relationship shown by arrows, color keys, or object placement,
- the browser announces an inferred description that sounds authoritative even though it was never reviewed by the office,
- or the page relies on visual evidence (“use this entrance,” “look for this envelope,” “the accessible route is here”) that was never made durable in ordinary text.

## Generated image descriptions are a convenience layer, not reviewed official explanatory copy

For this archive, browser-generated image descriptions should be treated like a convenience accessibility layer:
useful, sometimes necessary, but not a substitute for authored official explanation.

That means an office should not let critical meaning depend only on:
- unlabeled photos of entrances, drop boxes, or polling places,
- icon-only status or warning cards,
- infographic arrows, color keys, or layout relationships,
- sample-envelope or sample-ID images with no parallel textual explanation,
- or maps/screenshots whose controlling takeaway is visible but never written out.

If an image changes what the voter should do now, the controlling meaning should be recoverable in ordinary page text or authored text alternatives rather than only through browser inference.

## High-risk image classes deserve explicit review

The most dangerous failures are not decorative.
They are images whose description can change the voter’s next action.
For `491`, review at least these classes when they appear on official routes:
- polling-place, curbside, or accessible-entrance photos,
- drop-box location photos or facility approach images,
- maps, directional diagrams, and parking/entrance wayfinding graphics,
- sample ballot-envelope, secrecy-sleeve, or curing-document images,
- ID-example or document-example panels,
- infographic process diagrams or icon-based step sequences,
- and warning/status graphics where color, symbol, or placement changes the meaning.

This does **not** require every decorative image to become a mini policy packet.
It requires the office to notice when the image is carrying operational meaning that a generated description might distort.

## Availability, privacy, and accuracy vary by platform

Current browser/platform implementations are not uniform.
Chrome says image descriptions may be available only to screen-reader users and may not be fully accurate. Edge says generated descriptions are for unlabeled images and can be read aloud by screen readers. Apple ties VoiceOver Recognition to supported devices/settings and warns against relying on generated descriptions in high-risk situations. (xref: `google_chrome_get_image_descriptions_page`; xref: `microsoft_support_edge_accessibility_features_page`; xref: `apple_support_voiceover_recognition_iphone_ipad_page`; xref: `apple_support_voiceover_recognition_settings_mac_page`)

So the public-safe posture is:
- the authoritative explanation still lives in the office’s reviewed page text and help lane,
- generated image descriptions are optional/browser-specific accessibility aids rather than required delivery channels,
- the office should not assume every voter hears the same description or hears one at all,
- and missing support should degrade to the surrounding official text/help route, not to a silent visual-only dependency.

## Keep the official answer reconstructible without trusting model-generated captions

The archive does **not** need to prove that every generated description will be correct.
That would be the wrong target.
The right target is smaller:
**keep the official answer reconstructible even when generated image descriptions differ, fail, or overstate the image’s meaning.**

That usually means:
- put the controlling instruction in adjacent ordinary text,
- keep office identity, scope, and help routing near the image,
- avoid icon-only or photo-only critical meaning where text could safely carry it,
- and treat generated descriptions as subordinate hints rather than the office’s official caption.

## Claims this control should support

1. **Generated-caption subordination claim:** browser-generated image descriptions remain subordinate to the page’s reviewed official text and help lane.
2. **Non-text-content equivalence claim:** action-changing images have enough authored surrounding text or text alternatives that the official meaning does not depend on model inference alone.
3. **Availability/variance honesty claim:** the office does not assume generated image-description features are universal, identical across browsers, or always enabled.
4. **High-risk-image review claim:** images carrying operational meaning were reviewed as a distinct surface rather than treated as decorative residue.
5. **Boundary clarity claim:** failures in this lane stay distinct from authored screen-reader semantics (`418`), OCR/transcription (`488`), reader mode (`440`), and page-audio narration (`489`).

## Canonical digest artifacts

Publish **small digests of generated-image-description posture**, not per-user description logs.

- **Browser Image Description Surface Digest (BIDSD):** digest of routes reviewed for browser-generated image-description boundaries.
- **High-Risk Image Equivalence Digest (HRIED):** optional digest of routes where critical images were paired with durable authored text or alt-text improvements.
- **Generated-Description Variance Note (GDVN):** optional note that browser/platform availability, accuracy, privacy posture, or language support varies across environments.

## What belongs in the public image-description payload

Keep the payload **small, route-aware, and explicit about inferred-description subordination**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `browser_image_description_surface_label`
- `delivery_role_note`
- `covered_surface_refs[]`
- `official_source_anchors[]`
- `reviewed_image_description_contexts[]`
- `authority_boundary_note`
- `high_risk_image_classes[]`
- `authored_text_equivalence_note`
- `generated_description_variance_note`
- `privacy_and_processing_note`
- `current_help_recovery_note`
- `last_verified_at`
- supersedes / superseded-by pointers

Do **not** publish by default:
- individualized generated image-description transcripts,
- user-assistive-technology fingerprints,
- raw screenshots collected only to show that an unlabeled image existed,
- or per-browser behavioral telemetry about which voters invoked generated descriptions.

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:
- Which current official routes were reviewed for browser-generated image-description risk?
- If generated descriptions are absent, different, or partially wrong, does the official page still expose the controlling meaning in authored text or help routing?
- Are maps, photos, diagrams, and icon-heavy panels that change voter action treated as high-risk images rather than decorative artwork?
- Does the public posture say clearly that generated descriptions are optional/browser-specific and not the office’s reviewed caption text?
- Is the failure really about inferred description of non-text content, rather than OCR of words, reader-mode extraction, or authored screen-reader markup?

## Quarantine boundary: no pseudo-provenance for generated captions yet

This document does **not** assume standardized provenance for generated image descriptions, stable model/version identifiers across browsers, or a portable way to reconstruct exactly what descriptive caption every user heard.
If trustworthy cross-browser provenance later emerges, that may justify a future narrow control.
For now, keep it in quarantine.
The canon here is smaller:
keep decisive official meaning out of browser-generated guesswork when authored text can safely carry it.

## How this fits the family map

Browser-generated image descriptions are **not** a new underlying voter-question family bucket.
They are a shared public-surface control that applies when the official page is already open but a browser or platform can still narrate unlabeled visual content as if it were reviewed explanatory text.

Use `491` when the right official page exists and is already open, but unlabeled or weakly labeled images can still become a shadow explanatory surface through browser-integrated description features.
Keep using:
- `418` for authored screen-reader semantics and live updates,
- `440` for reader-mode / simplified main-content extraction,
- `488` for OCR and scanned-document text extraction,
- `489` for browser-integrated read-aloud of authored page text,
- `492` for browser-generated live captions / translated subtitles over already-open official media,
- and `305` for the controlling office/help lane.

This document only says that, if modern browsers can describe images on the current official page, the office should not quietly let that generated description become the only way a voter can recover the page’s decisive meaning.

## Sources (current anchors)

- EAC: Effective election design guidance (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`)
- Digital.gov: requirements for delivering a digital-first public experience (xref: `digital_gov_requirements_digital_first_public_experience_page`)
- W3C WAI: Understanding WCAG 2.2 Non-text Content (xref: `w3c_wcag22_non_text_content_page`)
- Section508.gov: Authoring meaningful alternative text (xref: `section508_authoring_meaningful_alternative_text_page`)
- Google Chrome Help: Get image descriptions on Chrome (xref: `google_chrome_get_image_descriptions_page`)
- Microsoft Support: Accessibility features in Microsoft Edge (xref: `microsoft_support_edge_accessibility_features_page`)
- Apple Support: Use VoiceOver Recognition on iPhone or iPad (xref: `apple_support_voiceover_recognition_iphone_ipad_page`)
- Apple Support: Change VoiceOver Recognition settings in VoiceOver Utility on Mac (xref: `apple_support_voiceover_recognition_settings_mac_page`)

## Companion artifacts

- Template payload: `artifacts/templates/official-voter-information-browser-image-description-surface-payload.json`
- Operator quickcheck: `artifacts/checklists/official-voter-information-browser-image-description-surface-checklist.md`
