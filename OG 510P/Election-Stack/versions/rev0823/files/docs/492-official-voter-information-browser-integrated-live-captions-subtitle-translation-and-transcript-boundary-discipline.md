# 492 — Official voter-information browser-integrated live captions, subtitle translation, and transcript-boundary discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **official voter-information routes whose already-open audio or video may be captioned, subtitled, or lightly transcripted by the browser or platform itself while the voter is consuming that media**:
recorded explainers,
livestream replays,
embedded briefings,
audio-first recordings,
short clips,
and similar official media where the underlying recording may be current while a browser or device turns speech into a new text surface.

It is not primarily about whether the office published captions in the first place.
It is about what happens when **generated captions or translated subtitles begin to look like the reviewed official transcript of the current recording**.

It composes with:
- `369`, which governs the office-published video / livestream / clip delivery lane itself,
- `377`, which governs official language selectors, locale fallback, and machine-translation boundaries,
- `418`, which governs authored screen-reader semantics for webpages,
- `487`, which governs browser-integrated translation of already-authored page text,
- `489`, which governs browser-integrated narration of already-authored page text,
- `491`, which governs browser- or platform-generated descriptions of images on the already-open page,
- `493`, which governs player- or platform-level transcript panes, searchable transcripts, timestamp jumps, and downloadable/copyable transcript sidecars for the already-open recording,
- `501`, which governs alternate spoken tracks such as dubbed audio or audio description over the already-open recording rather than generated text over that recording,
- and `305`, which governs the office/help lane the voter should be able to recover when media-derived text becomes ambiguous.

The narrow rule is:
**if an official voter-information recording may be consumed through browser- or platform-generated live captions, translated subtitles, or copied caption text, the office should not let that generated text masquerade as the reviewed official transcript or translated publication, and should keep the current official written destination/help lane reconstructible without trusting the generated text alone.**

## Why this is a distinct surface

`369` already says official recordings, clips, captions, and transcripts are a real voter-information delivery lane.
But a newer seam now matters even when the office did everything “normally”:
- the recording is already open,
- the player is already rendering,
- and the browser or platform itself produces captions, translations, or transcript-like text over that media.

That creates a distinct public-answer risk.
The office may have published:
- reviewed captions,
- no captions,
- one reviewed transcript,
- or only a brief summary plus a help route.

Yet the voter may still encounter a second text layer generated at playback time.
That layer can flatten qualifiers, speaker identity, timing, election scope, or correction status.
And because it appears as synchronized on-screen text, it can feel more authoritative than the office ever intended.

Current official browser/platform guidance is specific enough to justify a bounded control here.
W3C’s current WCAG guidance for **Captions (Prerecorded)** and **Captions (Live)** treats captions as a real accessibility requirement for synchronized media, and W3C’s current transcript guidance says descriptive transcripts are needed for some users and remain a distinct accessibility support. Chrome’s current caption guidance says the browser can generate captions for videos, podcasts, games, live streams, video calls, and other audio media; its caption processing is local, while caption translation can send captions to Google for translation. Microsoft’s current Windows guidance says Live Captions can turn audio passing through the PC into a caption experience across apps, can work offline for captions, and supports translation in some environments. Apple’s current guidance says Live Captions can transcribe spoken audio in apps and around the user, but availability varies and accuracy should not be relied on in high-risk or emergency situations. (xref: `w3c_wcag22_captions_prerecorded_page`; xref: `w3c_wcag21_captions_live_page`; xref: `w3c_wai_transcripts_page`; xref: `google_chrome_manage_captions_and_translations_page`; xref: `microsoft_windows_live_captions_page`; xref: `apple_support_live_captions_iphone_page`; xref: `apple_support_live_captions_mac_page`)

So the bounded question is not “can generated captions ever be useful?”
Of course they can.
The bounded question is smaller:
**when the browser or platform captions already-open official media, does the voter still have a clear route back to the current official source, reviewed transcript/caption if one exists, and the current help lane when generated text is incomplete, mistranslated, delayed, or overconfident?**

## This is not the same thing as official captions, transcript panes, page translation, or page-audio narration

`369` asks whether the office’s **published** recording lane has enough edition, correction, transcript, and linkback discipline.

`487` asks whether the browser translates **page text** from the already-open official page.

`489` asks whether the browser narrates **page text** from the already-open official page.

`493` asks whether a **transcript pane or transcript sidecar** turns the already-open recording into a searchable, copyable, jumpable text surface.

`545` asks a different, narrower same-object chain question: whether a **player-native selected caption/subtitle track or embed-default text-track state** should be recorded as a bounded rendering note without being mistaken for a new route, a reviewed translated edition, or the citation-safe current head.

`501` asks whether a **different spoken track** over the already-open recording begins to sound like a reviewed translated or descriptive official edition.

`492` asks a different question:
**once the voter is already consuming official media, does browser- or platform-generated caption text become a shadow transcript or translated publication that outruns what the office actually reviewed and currently stands behind?**

A route may pass `369`, `377`, `487`, and `489` and still fail `492` if:
- an embedded official briefing has reviewed captions in one place but the browser shows a different generated caption surface to the voter,
- a translated subtitle overlay sounds more definitive than the reviewed official translated help lane,
- copied caption text loses recording date, correction context, or speaker attribution,
- or the generated text becomes the only practical way a voter thinks they “read” the recording.

## Generated captions are support text, not automatic official transcripts

The public-safe posture is simple:
**generated captions are support text for consuming media, not automatic proof that the office published or reviewed that exact wording.**

That means the office should keep at least four things distinct:
1. the official recording itself,
2. any office-reviewed captions/subtitles/transcript the office actually publishes,
3. browser- or platform-generated captions/subtitles shown at playback time,
4. and the current written destination/help route that still controls when meaning, timing, or correction status matters.

If those layers collapse into one story, disputes become harder.
A later observer can no longer tell whether the voter relied on:
- reviewed official subtitles,
- an unreviewed generated caption string,
- a copied excerpt,
- or a translated overlay produced by a device setting the office never saw.

## Subtitle translation is a sharper boundary than same-language captions

Same-language live captions can already flatten punctuation, names, or speaker turns.
Translated subtitles raise the stakes further.
They can:
- change modality (“may” vs. “must”),
- smooth away exceptions,
- mis-handle place names or office names,
- or make a contingent rule sound universal.

So `492` should bias toward a modest discipline:
- do not let translated generated subtitles be the only multilingual explanation for action-changing instructions,
- keep the original recording context and any reviewed official translated lane easy to recover,
- and keep a visible help route for voters who encounter a doubtful caption or translation.

The archive does **not** ask the office to preempt every user-controlled caption setting.
It asks the office not to mistake convenience subtitle generation for a reviewed multilingual publication.

## Live captions can flatten speaker, timing, and correction state

Official election recordings often carry timing and role cues that matter:
- whether a statement came from the election director, call-center lead, accessibility coordinator, or partner,
- whether a sentence described current operations or historical background,
- whether the clip was a live emergency briefing, a replay, or an evergreen explainer,
- and whether a correction or superseding note already exists.

Generated captions can weaken those cues.
They may omit speaker names.
They may lag.
They may split or merge sentences oddly.
They may survive in copied text after the recording has been corrected or superseded.

For `492`, that means the office should not rely on generated caption text alone to carry:
- current-state authority,
- superseding status,
- recording date,
- office identity,
- or the help route the voter should use when the media is not enough.

## Availability, privacy, and retention vary by platform

Current browser and platform implementations are materially different.
Chrome says caption generation is local, but translation can send captions to Google. Windows says captions can work across apps and offline for captions, while some translation behavior depends on supported environments. Apple says availability varies by device, language, country, and region, and warns against relying on Live Captions in high-risk or emergency situations; some call-caption settings also change whether text can be copied or retained briefly. (xref: `google_chrome_manage_captions_and_translations_page`; xref: `microsoft_windows_live_captions_page`; xref: `apple_support_live_captions_iphone_page`; xref: `apple_support_live_captions_mac_page`)

So the office should not pretend:
- every voter sees the same captions,
- every browser keeps caption text local,
- every device supports the same language pairs,
- or every caption window behaves like an official transcript archive.

The safest public stance is:
- generated captions/subtitles are optional support layers,
- availability and privacy posture vary,
- copied caption text is not automatically an official portable record,
- and volatile or corrected topics should always point back to the current official written destination/help lane.

## High-risk topics should bias toward written recovery, not caption confidence

Some topics are too consequential to leave resting on generated subtitle quality alone:
- same-day polling-place changes,
- ballot-return deadline semantics,
- cure instructions,
- rights-restoration or special-case eligibility explanations,
- emergency outage or incident instructions,
- and any correction to an earlier public statement.

For those topics, `492` does **not** require generated captions to become perfect.
It requires the recording page, description, pinned note, adjacent FAQ, or linked current notice to keep the controlling written answer easy to recover.

If the official recording is action-changing, the office should prefer:
- a reviewed transcript or summary when practical,
- visible recording-date and still-current cues,
- a linked current destination for operational detail,
- and a help lane that stays stable when the caption text is wrong, late, or absent.

## Minimal state taxonomy

Keep at least these states separate:
- **reviewed official caption/transcript available**
- **generated same-language captions only**
- **generated translated subtitles active**
- **caption text copied/exported by the user but not office-reviewed**
- **no caption support available**
- **caption support available but volatile / high-risk topic requires written recovery**
- **recording superseded or corrected**

The point is not to log each user’s state.
The point is to keep the public explanation honest about which state the office actually stands behind.

## Bounded browser-caption trace minimum

A small public digest should make it possible to reconstruct:
- which official media routes were reviewed for generated caption/subtitle behavior,
- whether reviewed official captions/transcripts existed,
- whether generated subtitle translation was in scope for review,
- where the current official written destination/help lane lived,
- whether copied/generated caption text was treated as subordinate rather than authoritative,
- and when the route was last verified.

It should **not** require storing individualized caption windows, full per-user transcripts, microphone captures, or device-specific accessibility fingerprints.

## Minimal claim-set

1. **Generated-caption subordination claim:** browser- or platform-generated caption text stays subordinate to the official recording, any office-reviewed transcript/caption, and the current official written destination/help lane.
2. **Translation-boundary claim:** translated generated subtitles are not treated as equivalent to a reviewed official translated publication unless the office actually publishes and stands behind that translated text.
3. **Recovery claim:** high-risk or corrected media routes keep a durable written recovery path to the current official answer/help lane.
4. **Variance honesty claim:** the office states that availability, privacy posture, language support, and retention differ across browsers, operating systems, and device settings.
5. **Portable-record honesty claim:** copied/generated caption text is not automatically treated as a current official portable record or transcript edition.

## Canonical digest artifacts

Publish **small digests of browser-caption posture**, not individualized caption logs.

- **Browser Caption Surface Digest (BCSD):** digest of routes reviewed for generated captions/subtitles on already-open official media.
- **Caption Translation Boundary Digest (CTBD):** optional digest of routes where translated subtitle behavior was explicitly reviewed.
- **Transcript Recovery Note (TRN):** optional note identifying where reviewed official transcript/caption/help recovery lives for action-changing recordings.

## What belongs in the public browser-caption payload

Keep the payload **small, route-aware, and explicit about generated-text subordination**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `browser_caption_surface_label`
- `delivery_role_note`
- `covered_surface_refs[]`
- `official_source_anchors[]`
- `reviewed_media_caption_contexts[]`
- `official_caption_or_transcript_note`
- `subtitle_translation_boundary_note`
- `generated_caption_variance_note`
- `privacy_and_retention_note`
- `portable_record_boundary_note`
- `current_help_recovery_note`
- `last_verified_at`
- supersedes / superseded-by pointers

Do **not** publish by default:
- individualized generated caption transcripts,
- copied caption strings from actual users,
- call or microphone transcripts tied to identifiable people,
- device or assistive-technology fingerprints,
- or exhaustive per-platform caption-behavior matrices when a compact public posture is sufficient.

## How this fits the family map

Generated live captions and translated subtitles are **not** a new underlying voter-question family bucket.
They are a delivery/control layer over already-existing public-answer surfaces.

Use `492` when the right official recording or embedded media is already open, but caption or subtitle generation by the browser or platform can still create a shadow transcript or translated publication.
Keep using:
- `369` for the office-published video/livestream/clip lane itself,
- `377` for official language-selector and reviewed translation-routing posture,
- `487` for translation of already-authored page text,
- `489` for narration of already-authored page text,
- `491` for generated descriptions of images on the already-open page,
- and `305` for the controlling office/help lane.

This document only says that, if the browser or platform captions the already-open official recording, the office should not quietly let generated caption text become the only trustworthy-looking transcript of what the voter just heard.

## Minimal operator artifacts in this archive

- Checklist: `artifacts/checklists/official-voter-information-browser-live-captions-surface-checklist.md`
- Template payload: `artifacts/templates/official-voter-information-browser-live-captions-surface-payload.json`

## Sources (pinned IDs / lockfile IDs)

- W3C WAI: Understanding WCAG 2.2 Captions (Prerecorded) (xref: `w3c_wcag22_captions_prerecorded_page`)
- W3C WAI: Understanding SC 1.2.4 Captions (Live) (xref: `w3c_wcag21_captions_live_page`)
- W3C WAI: Transcripts guidance (xref: `w3c_wai_transcripts_page`)
- Google Chrome Help: Manage captions and translations in Chrome (xref: `google_chrome_manage_captions_and_translations_page`)
- Microsoft Support: Use live captions to better understand audio (xref: `microsoft_windows_live_captions_page`)
- Apple Support: Get live captions of spoken audio on iPhone (xref: `apple_support_live_captions_iphone_page`)
- Apple Support: Get live captions of spoken audio on Mac (xref: `apple_support_live_captions_mac_page`)
