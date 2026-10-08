# 489 — Official voter-information browser-integrated read-aloud, listen-to-page, and page-audio narration boundary discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **official voter-information routes that voters may consume through browser-integrated read-aloud, listen-to-page, reader-view narration, or similar page-audio features while the official page is already open**:
Safari “Listen to Page”,
Firefox Reader View read aloud,
Edge Read Aloud / Immersive Reader narration,
Chrome “Listen to this page” standard playback,
Chrome “Listen to this page” AI playback,
and similar browser- or app-integrated features that turn the current page into a serial audio stream rather than merely showing the page visually.

It does **not** replace the underlying voter-question families in `292–343`.
It does **not** replace:
- `305`, which governs the controlling office/help lane,
- `307`, which governs source labels, answer verifiability, and escalation when a compact public surface is not enough,
- `418`, which governs screen-reader semantics, live-update accessibility, and assistive-technology structure more broadly,
- `440`, which governs reader mode / simplified view / main-content extraction as a visual reading surface,
- `486`, which governs browser-integrated page summaries and same-page page-context AI sidebars,
- `487`, which governs browser-integrated page translation and selected-text translation,
- `488`, which governs browser-integrated OCR, image text extraction, and scanned-PDF text layers that may become upstream text before later audio playback,
- `492`, which governs generated live captions and translated subtitles over already-open official media rather than narration of already-authored page text,
- or ordinary OS-level speech features that speak arbitrary on-screen content outside a browser-defined page-audio lane.

It adds one narrow rule:
**if an official voter-information route may be consumed through browser-integrated read-aloud or page-audio narration, the office should keep the controlling current-state/scope/help cues reconstructible in serial audio, should keep an easy route back to the visible official page, and should not let convenience narration — especially conversational or AI playback — quietly become a shadow official briefing above the page itself.**

## Why this is a distinct surface

The EAC’s current election-design guidance treats online voter-information materials as core public communications whose clarity, structure, accessibility, and usability matter operationally. Digital.gov’s current digital-first public-experience guidance likewise treats understandable, authoritative public digital delivery as an operational requirement rather than a presentation preference. Apple’s current Safari guidance says users can have supported webpages read aloud with **Listen to Page**. Mozilla’s current Firefox Reader View guidance says Reader View can **Read aloud** an article when text-to-speech information is available in the article’s language. Microsoft’s current Edge guidance says Immersive Reader simplifies the page, offers **Read Aloud**, and can also be opened from selected text. Google’s current Chrome guidance says **Listen to this page** can use **Standard playback**, which reads all the words on the page, or **AI playback**, which generates podcast-like conversations from the page; it also says the feature is not available on all websites and that AI playback availability depends on settings and language posture. W3C’s current guidance for **Info and Relationships** says structure and relationships should remain programmatically determinable or explicit when content is read nonvisually, and WAI’s current page-structure and tables guidance says headings and header/data relationships carry real meaning rather than decorative formatting. (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`; xref: `digital_gov_requirements_digital_first_public_experience_page`; xref: `apple_support_iphone_listen_to_webpage_page`; xref: `firefox_reader_view_help_page`; xref: `microsoft_support_edge_immersive_reader_page`; xref: `google_chrome_help_listen_to_this_page_page`; xref: `w3c_wcag21_info_and_relationships_page`; xref: `w3c_wai_page_structure_headings_page`; xref: `w3c_wai_tutorials_tables_page`)

That is enough to justify a compact control here.
A route may pass ordinary page review, reader-mode review, and even summary/translation review yet still fail first contact because:
- the crucial qualifier is technically present on the page but arrives too late or too quietly in audio for the listener to keep attached to the operative sentence,
- a table, footnote, heading, or grouped warning loses force once the browser reads the page as a flat serial stream,
- the listener starts playback and then locks the screen, changes tabs, or stops looking at the page, losing the visible office/scope/help cues,
- a browser offers conversational or AI playback that sounds more like a complete briefing than a subordinate rendering of the current page,
- or the narration works only for some browsers, sites, languages, or settings, but office assumptions treat it as universal.

## This is not the same thing as screen readers, reader mode, or summaries

`418` asks whether the page has the semantics, focus discipline, live-update behavior, and assistive-technology compatibility needed for screen readers and related accessibility tools more broadly.

`440` asks whether the browser can produce a simplified **visual** reading surface that still preserves the controlling answer and action boundary.

`486` asks whether the browser compresses or restates the page into a summary or answer layer.

`489` asks a different question:
**once the voter already has the official page open, does browser-integrated audio narration of that page still keep the current official answer, qualifiers, and help lane reconstructible when consumed as time-based audio rather than as a stable visible layout?**

A route may pass `418`, `440`, and `486` and still fail `489` if:
- the structure is technically accessible, yet the browser’s page-audio path makes a late exception easy to miss,
- reader mode shows the page cleanly, but the narrated version flattens the heading/table/footnote relationships that made the answer safe,
- the page summary is disabled, but a read-aloud or AI playback feature still makes the page sound like a settled official briefing,
- or the page is correct while visible, yet background playback detaches the answer from the on-screen recovery/help cues.

## Time-based narration changes what the voter can keep in working memory

An official page is not only words; it is also order, grouping, emphasis, labels, headings, tables, and nearby recovery routes.
Read-aloud features convert that designed surface into a sequence over time.
That can be helpful, but it changes failure modes.
The voter may hear:
- a deadline before the exception,
- a location rule before the district qualifier,
- a table row without enough table-header context,
- a “bring ID” sentence before the alternatives or cure path,
- or a help number after the point where the listener already acted on the earlier sentence.

For `489`, the page should assume that some users will consume the answer as audio first and visuals second.
If the answer is not safely portable through that serial audio path, the route should say so plainly and move the listener back to the visible official help lane.

## AI playback is a sharper boundary than ordinary read aloud

Ordinary page narration is already a transformed surface.
AI playback can be more aggressive still because it may sound like a polished conversation or briefing rather than a faithful reading of the page.
Google’s current Chrome guidance makes this difference explicit by separating **Standard playback** from **AI playback** and saying AI playback generates podcast-like conversations from the page. (xref: `google_chrome_help_listen_to_this_page_page`)

That means `489` should keep at least three states separate:
- **Verbatim-like read aloud** of the currently open page text,
- **Reader-view narration** of a simplified reading surface,
- and **AI/conversational page-audio playback** derived from the page.

Those are not the same authority posture.
A route that is safe for straightforward narration may still be unsafe for conversational playback that compresses, reorders, or smooths away qualifiers.

## Availability varies; do not build policy on the feature being present

Apple’s Safari guidance limits **Listen to Page** to supported webpages. Mozilla’s Reader View guidance says read aloud appears only when the operating system has text-to-speech information in the article’s language. Edge’s read-aloud path depends on Immersive Reader support or the browser’s read-aloud tooling. Chrome’s current guidance says **Listen to this page** is not available yet on all websites and that playback mode availability depends on settings and language posture. (xref: `apple_support_iphone_listen_to_webpage_page`; xref: `firefox_reader_view_help_page`; xref: `microsoft_support_edge_immersive_reader_page`; xref: `google_chrome_help_listen_to_this_page_page`)

So the public-safe posture is:
- the authoritative answer still lives on the page/help lane itself,
- browser page-audio features are convenience surfaces rather than required delivery channels,
- office copy should not assume every voter can or will use them,
- and absence of narration should degrade to the visible official page rather than to a broken or context-poor route.

## Background playback and reduced visual attention raise distinct risks

Google’s current Chrome guidance says users can continue to browse the current website or switch to other tabs while listening, and can keep listening even if the screen is locked. That convenience is good for accessibility and multitasking, but it means the visible recovery cues may no longer be in front of the user when the decisive sentence arrives. (xref: `google_chrome_help_listen_to_this_page_page`)

For `489`, that means:
- route identity should be stated clearly enough in the narrated material,
- the page should keep critical office/scope/help cues close to the operative answer,
- and the route should not assume the listener is continuously looking at the screen while audio plays.

## High-risk topics should bias toward routing, not audio-only confidence

The most dangerous failures are the same topics already treated as risky under `305`, `307`, `311`, `317–343`, and related public-answer surfaces:
- polling-place, drop-box, and early-voting location/hour changes,
- deadline and receipt-rule distinctions,
- ID alternatives and cure paths,
- disability, language, jail/facility, disaster, or new-citizen edge cases,
- and any answer that should move the voter into ordinary help or rights/safety escalation.

For those topics, `489` does **not** ask the browser’s narration to become perfect.
It asks the office to keep the **safe official routing answer** audible and recoverable enough that page-audio playback remains a convenience layer rather than the de facto complete instruction.

## Minimal state taxonomy

A small taxonomy is enough:

1. **page_read_aloud_available_source_page_recoverable**
2. **reader_view_narration_available_visual_structure_recoverable**
3. **background_or_screen_locked_playback_possible_recovery_required**
4. **ai_page_audio_available_not_safe_as_complete_answer**
5. **translated_or_extracted_text_audio_subordinate_to_source**
6. **feature_unavailable_language_not_supported_or_blocked**
7. **narration_conflict_under_review_route_to_official_help**

## Bounded page-audio trace minimum

The archive does **not** need per-user listening logs, playback durations, highlighted-word transcripts, or voice-selection telemetry.
But a voter-information page-audio surface should preserve a bounded trace for action-changing outputs.

At minimum, that trace should make it possible to reconstruct:
- which official routes were reviewed for browser-integrated read-aloud or page-audio behavior,
- which narration classes were reviewed (ordinary read aloud, reader-view narration, AI playback, background playback, and similar),
- whether the reviewed path kept visible source-page recovery and official help anchors,
- whether a high-risk topic warning or audio-not-complete-answer boundary controlled,
- and when the review was last performed.

Prefer **route identifiers, reviewed narration-context labels, recovery/help anchors, policy notes, and timestamps** over audio recordings, synthetic speech outputs, or individualized playback histories.

## Minimal claim-set

A jurisdiction can publish a compact, verifiable claim-set:

1. **Page-audio surface claim:** the office reviewed one or more official voter-information routes for browser-integrated read-aloud or page-audio behavior.
2. **Subordination claim:** browser narration remains subordinate to the current official page and named help lane.
3. **Serial-audio claim:** the office evaluated whether decisive qualifiers, timing cues, and route identity remain reconstructible when consumed as serial audio.
4. **AI-playback claim:** conversational or AI playback, when present, is not silently treated as a complete official answer.
5. **Recovery claim:** the voter can recover the visible source page and current official help lane without guesswork.
6. **Availability-honesty claim:** unsupported languages, unsupported pages, disabled features, or blocked environments are treated honestly rather than as hidden failures.
7. **Privacy-minimization claim:** the office does not retain individualized listening histories when bounded policy evidence is enough.

## Canonical digest artifacts

Publish **digests of page-audio review posture**, not recordings.

- **Page Audio Surface Digest (PASD):** digest of the bounded public page-audio posture payload for a scope.
- **Narration Context Review Digest (NCRD):** optional digest proving which narration contexts were reviewed for a route class.
- **Source Page Recovery Digest (SPRD):** optional digest proving how the voter can recover the visible source page or current official help lane after audio playback.
- **AI Playback Boundary Digest (AIPBD):** optional digest proving the current policy posture when conversational playback is available but not safe as a complete answer.

## What belongs in the public page-audio payload

Keep the payload **small, bounded, and explicit about audio non-equivalence**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id`
- human `browser_page_audio_surface_label`
- `delivery_role_note`
- `covered_surface_refs`
- `official_source_anchors`
- `reviewed_narration_contexts[]`
- `authority_boundary_note`
- `serial_audio_boundary_note`
- `ai_playback_boundary_note`
- `background_playback_note`
- `source_page_recovery_note`
- `high_risk_topic_routing_note`
- `privacy_minimization_note`
- `latest_notice_uri`
- `last_verified_at`
- optional `supersedes` / `superseded_by`

Do **not** publish by default:
- recorded browser narration,
- synthetic audio exports,
- word-by-word playback transcripts,
- per-user listening histories,
- or large captured audio artifacts merely to prove the posture was reviewed.

## How this fits the family map

Use `489` when the right official page is already open, but a browser-integrated read-aloud or listen-to-page feature can still make the answer behave differently once it becomes time-based audio.

Use nearby controls when the problem is instead:
- whether assistive-technology semantics, landmarks, labels, or live updates are present broadly (`418`),
- how reader mode or simplified view extracts ordinary visual content (`440`),
- whether a browser summary or page-context AI layer compresses the already-open page (`486`),
- whether a browser translation layer rewrites the already-open page or selected text (`487`),
- whether OCR or image-text extraction creates the upstream text layer before narration (`488`),
- or whether the browser/platform is generating captions or translated subtitles over already-open official media rather than narrating page text (`492`),
- or whether the answer leaves the live page entirely as a saved or printed artifact (`437`, `368`).

## Minimal operator artifacts in this archive

- Template payload: `artifacts/templates/official-voter-information-browser-page-audio-surface-payload.json`
- Operator quickcheck: `artifacts/checklists/official-voter-information-browser-page-audio-surface-checklist.md`
