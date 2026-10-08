# 369 — Official voter-information videos, livestreams, and clip-context discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **official voter-information audiovisual artifacts**:
explainer videos,
livestreams,
recorded briefings,
webinars,
audio-first recordings,
and short clips or excerpts that the office publishes or republishes as part of the public-help lane.

It is not trying to turn every recording into a giant evidence bundle.
It is trying to keep one practical public-risk seam from going soft:
**what happens when a voter acts on a clipped, replayed, reposted, or auto-captioned official video after the current controlling webpage, FAQ, notice, or office instruction has changed.**

It composes with:
- `docs/186-incident-communications-as-evidence.md`
- `docs/194-synthetic-media-and-comms-authenticity-minimum-controls.md`
- `docs/195-rumor-control-and-status-boards-as-verifiable-public-surfaces.md`
- `docs/203-official-channel-directory-as-evidence.md`
- `docs/205-cache-and-freshness-controls-for-public-surfaces.md`
- `docs/223-public-surface-capture-notes-and-reproducibility.md`
- `docs/248-accessibility-usability-and-language-access-as-integrity.md`
- `docs/305-election-office-contact-directories-office-hours-and-change-notices-as-evidence-surfaces.md`
- `docs/310-voter-facing-public-answer-surfaces-family-map-and-promotion-rules.md`
- `docs/365-official-voter-faqs-knowledge-base-articles-and-answer-edition-discipline.md`
- `docs/366-official-voter-information-broadcast-alerts-social-posts-and-linkback-discipline.md`
- `docs/584-official-voter-information-platform-media-provenance-signals-content-credentials-and-non-substitutive-authenticity-discipline.md`
- `docs/367-official-voter-information-press-releases-media-advisories-and-spokesperson-quote-discipline.md`
- `docs/368-official-voter-information-printable-handouts-flyers-postcards-and-edition-linkback-discipline.md`
- `artifacts/checklists/official-voter-information-video-surface-checklist.md`
- `artifacts/templates/official-voter-information-video-surface-payload.json`

## Why this exists (bounded)

The archive already treats webpages, FAQs, hotlines, alerts, media releases, and portable print artifacts as governed public-answer delivery layers.
That still leaves a distinct lane that election offices increasingly use in practice: **official audiovisual voter-information surfaces**.
Election officials now publish explainer videos, livestreamed briefings, webinar walkthroughs, process videos, recorded trainings that the public can watch, and short video clips or excerpts on official channels.
Those artifacts travel differently from ordinary webpages.
They get embedded on third-party platforms, excerpted into shorter clips, screenshotted into quote cards, replayed after the election context changes, mirrored by partners, and consumed through captions or transcripts that may outlive the original page description.

Current official guidance is specific enough to justify a bounded control here.
EAC's current **Clearinghouse Resources on Communications** page treats video as a real communications lane by listing a **Video Training Series: Communications 101** and the current **Communicating Election and Post-Election Processes Toolkit**, which includes educational materials about election processes for observers and the public.
That 2026 toolkit page says election officials can use it to share trustworthy information, combat mis/disinformation, support consistency in what voters read about elections, and it provides a resource-video series explaining how to use the toolkit materials.
EAC's current **Clearinghouse Resources on Accessibility** page separately treats video as an accessibility and communications object by listing an **Accessible Elections** video training series about voting locations, election websites, social media, other communications, and outreach events.
EAC's current **Accessibility Checklist: Accessible Communications** says election offices are required to provide effective communications and that the guide covers accessible practices for videos and virtual meetings, electronic documents, and social media posts.
EAC's current design guidance also says voter-information materials should be clear, understandable, accessible, and written in plain language.
And NASS's current `#TrustedInfo2026` posture still keeps election officials as the trusted source voters should follow when election information is timely or action-changing.
(xref: `eac_clearinghouse_resources_communications_page`; xref: `eac_communicating_election_post_election_toolkit_2026_page`; xref: `eac_clearinghouse_resources_accessibility_page`; xref: `eac_accessibility_checklist_accessible_communications_2024_pdf`; xref: `eac_effective_design_for_the_administration_of_federal_elections_page`; xref: `nass_trustedinfo_2026_page`)

So the bounded problem is not “archive every frame of every livestream” and it is not “treat every YouTube upload as a legal instrument.”
The bounded problem is simpler:
**if a jurisdiction expects the public to rely on official video or livestream artifacts for action-changing voter information, how does it keep those artifacts subordinate to the current controlling written destination, and how does it later prove which recording, clip, or captioned edition the public actually received?**

## What this adds (and what it does not)

This document adds a compact **edition + linkback + clip-context + accessibility discipline** for official voter-information video surfaces.

It does **not** require every jurisdiction to produce videos or host livestreams.
It does **not** require archiving raw chat logs, every viewer comment, or every platform analytics trace.
It does **not** replace:
- the underlying voter-question family in `292–343`,
- the office-routing lane in `305`,
- FAQ/help article controls in `365`,
- short-form alert controls in `366`,
- media-release controls in `367`, or
- print/download controls in `368`.

It adds one narrow rule:
**if the public is expected to rely on an official video, livestream, webinar, recording, or republished clip for action-changing election guidance, that artifact should visibly identify its recording/publication scope, point back to the current official destination, expose whether the recording is still current, and carry an explicit correction/superseding path when it stops controlling.**

If the distinct problem is **browser- or platform-generated live captions / translated subtitles over the already-open recording**, use `492`.
If the distinct problem is **a player- or platform-level transcript pane, transcript search, timestamp-jump transcript, or downloadable/copyable transcript sidecar for the already-open recording**, use `493`.
If the distinct problem is **chapter markers, automatic chapters, key moments, or shareable/copyable chapter lists attached to the already-open recording**, use `494`.
If the distinct problem is **public clips, shorter highlights, or share-a-segment excerpt links derived from the already-open recording**, use `495`.
If the distinct problem is **Watch Later saves, viewer-managed playlists, offline downloads, or other platform-managed saved-media shelves for the already-open recording**, use `497`.
If the distinct problem is **popout playback, picture-in-picture, floating mini-players, or background-play states for the already-open recording**, use `502`.
If the distinct problem is **fullscreen, theater mode, or another immersive same-device player layout that visually downgrades the surrounding page/help context without detaching playback**, use `504`.
If the distinct problem is **playback-speed changes, skip/seek controls, scrubbing, rewinds, or live DVR catch-up over the already-open recording**, use `505`.
If the distinct problem is **history-driven resurfacing, continue-watching rows, recent-videos shelves, or remembered resume-state over the already-open recording**, use `506`.
If the distinct problem is **a publicly reachable official recording or replay that is still processing higher qualities, replay derivatives, or transcript/caption sidecars**, use `515`.
If the distinct problem is **a still-live official event route where the viewer may be materially behind the true live edge because of latency, buffering, pause, or DVR state, and where companion panes may reflect a later moment than the video pane**, use `516`.

If the distinct problem is **the same official live event intentionally exists on more than one official public route at once, or the platform can hand viewers from one official live route into another official route or embedded wrapper**, use `517`.
If the distinct problem is **the official media is fronted by a registration form, invite-only join link, approval workflow, members-only gate, or another platform-native audience-selection shell before the viewer can actually enter**, use `518`.
If the distinct problem is **views, concurrent-viewer numbers, likes, registrations, attendance totals, or similar platform-native audience metrics beside or about the official media start sounding like proof of currentness or authority**, use `519`.
If the distinct problem is **channel bylines, profile names, handles, verification badges, profile photos, creator URLs, uploader names, or profile cards around the official media start sounding like the whole proof that the route is official and current**, use `520`.
If the distinct problem is **context panels, election information boxes, disclosure labels, ratings, sensitivity cues, protection banners, or similar platform-added policy/context wrappers around the official media start sounding like the office's whole explanation of currentness, authority, or legal effect**, use `521`.
If the distinct problem is **Content Credentials, provenance pins, “how this content was made” disclosures, captured-with-a-camera labels, or similar origin/history signals around the same official media start sounding like the whole proof of current authority or still-current instructions**, use `584`.

If the distinct problem is **organizer-controlled banners, logos, colors, layout modes, trailers, latest-video substitutions, or hidden live-status cues around the same official media start sounding like proof that the route is current, live, or newly authoritative**, use `522`.
If the distinct problem is **an office-curated platform channel home, featured-video slot, playlist, showcase, or collection page built from official recordings**, use `507`.
If the distinct problem is **a public upcoming-event page, Premiere watch page, waiting-room shell, or pre-live countdown surface before the recording or livestream has actually started**, use `508`.
If the distinct problem is **a post-live archive page, ended-event shell, recurring-event replay route, or platform surface that keeps the finished event public after the live moment has ended**, use `509`.
If the distinct problem is **a share panel, copied whole-media link, current-time link, or embed export that carries the official media into another wrapper without minting a clip**, use `511`.
If the distinct problem is **a platform-native unavailable, private, age-gated, region-blocked, or not-playable-here shell over the official media route**, use `512`.
If the distinct problem is **the official media remains playable but auto/adaptive quality, data-saver, manual lower-quality selection, or embed-default fidelity changes how much visual detail the voter can actually recover**, use `513`.
If the distinct problem is **mutable platform-native titles, descriptions, thumbnails, posters, or playlist-local metadata wrappers around the same official media start acting like the controlling currentness claim or scope summary**, use `514`.
If the distinct problem is **player-native AI summaries, ask-this-video panels, or transcript-grounded answer modules over the already-open recording**, use `499`.
`369` governs the office-published audiovisual lane itself; `492` governs generated caption/subtitle overlays; `493` governs transcript-pane and transcript-sidecar behavior that can turn the recording into a shadow portable text edition; `494` governs titled chapter/key-moment jump maps that can turn the recording into a shadow answer map or portable excerpt surface; `495` governs portable clipped excerpts and highlights that can turn one slice of the recording into a shadow stand-alone answer surface; `497` governs platform-managed Watch Later / playlist / offline-library behavior that can turn one correct recording into a shadow private shelf of seemingly current answers; `499` governs player-native AI answer modules that can turn the already-open recording into a shadow generated briefing or help-desk surface; `502` governs detached playback modes that can keep one correct recording playing after the source-page date/scope/help context has fallen away; `504` governs same-device fullscreen or theater-style player expansion that can make one correct recording look self-sufficient after the surrounding route has been visually downgraded; `505` governs playback-speed / seek / rewind scan behavior that can make one correct recording feel fully reviewed even when the voter only consumed a compressed or fragmentary slice; `506` governs history, continue-watching, recent-videos, and resume-state behavior that can make one previously watched recording feel like the still-current official return path simply because the platform remembered it; `509` governs post-live archive shells and recurring-event replay routes that can make one finished event keep acting like the current official answer merely because the platform preserved the shell; `511` governs share panels, copied links, current-time entry links, and embed exports that can make one official media object travel into a new wrapper and start acting like a stand-alone current-answer object even though no new clip was minted; `512` governs platform-native unavailable/private/age-gated/region-blocked or playback-denied shells that can make that same object start sounding absent, forbidden, or nonpublic even when the office still owes the public a recoverable written/help lane; and `513` governs platform quality-state variation over that same object so a lower-detail rendition does not quietly become the practical stand-alone answer surface for detail-heavy instructions; and `514` governs mutable titles, descriptions, thumbnails, posters, and other metadata wrappers around that same object so a relabeled or reframed wrapper does not quietly become the controlling currentness claim or scope summary; and `516` governs live-edge / behind-live / latency states over that same object so a delayed live slice does not quietly become interchangeable with the true live current answer; and `517` governs same-event mirror sets, simulcast destinations, embedded live wrappers, and redirect chains over that event so several official routes do not quietly act like interchangeable live answers without an explicit primary/fallback posture; and `518` governs registration forms, invite-only join flows, approval gates, and members-only audience shells over that media so pre-access enrollment or audience-selection layers do not quietly become the office's whole answer about availability or next steps; and `519` governs views, concurrent-viewer counts, likes, registrations, attendance totals, and similar audience metrics over or about that media so impressive-looking numbers do not quietly become proof that a route is the controlling current answer; and `520` governs channel bylines, profile names, handles, verification badges, profile photos, creator URLs, uploader names, and profile-card source cues around that media so identity wrappers do not quietly become the whole proof that a route is official and current; and `521` governs context panels, election information boxes, disclosure labels, ratings, sensitivity cues, protection banners, and similar platform-added policy/context wrappers around that media so those wrapper signals do not quietly become the office's whole explanation of currentness, authority, or legal effect; and `522` governs organizer-controlled banners, logos, colors, layout modes, trailers, latest-video substitutions, and hidden live-status cues around that same media so presentation chrome does not quietly become proof that the route is current, live, or newly authoritative.

## Distinct boundary from alerts, press, and print

An official voter-information video surface is a distinct delivery layer because it is:
- audiovisual rather than text-first,
- often consumed through platform embeds, clips, or reposts away from the originating webpage,
- unusually prone to detached excerpts, timestamped fragments, and auto-caption errors,
- and commonly replayed after the election date, office hours, location, or procedure has changed.

This control is **not** the same thing as:
- a short-form alert or social post (`366`),
- a press release or spokesperson statement (`367`),
- a printable flyer or downloadable brochure (`368`),
- or an internal-only training or meeting recording with no public-answer role.

The video or livestream artifact is a public answer surface fragment with its own drift pattern.
That clipability and replay persistence are exactly why it needs a bounded discipline.

## Canonical-link floor

An action-changing official video should do one of two things:

1. **state a bounded fact and point directly to the current controlling official page / notice / FAQ-help path / office route**, or
2. **route the viewer to the official help path without pretending the recording itself carries the entire rule.**

This matters especially for:
- polling-place changes,
- deadlines and timeline reminders,
- registration and update walkthroughs,
- vote-by-mail request or return instructions,
- accessibility and language-help explainers,
- issue-reporting and rights-escalation videos,
- post-election process education that may shape voter trust,
- and any official clip likely to be reposted without its original page context.

Do not let a replayed video, platform clip, or captioned excerpt become the **only** place a material instruction lives.
The recording may be the first thing a voter sees.
The linked official page, notice, FAQ/help entry, or office-routing path should still carry the fuller controlling answer.

## Minimal message shape for action-changing official videos

A video does not need to be long, but it should usually make seven things legible:

1. **what question or action it covers,**
2. **which election / jurisdiction / voters / locations are in scope,**
3. **when it was recorded or issued,**
4. **whether the recording is live-only, archival, evergreen, or election-specific,**
5. **where the current official detail lives now,**
6. **where to get official help if the recording is not enough,** and
7. **whether captions, transcript, or equivalent text summary are available.**

That can live in the opening slate, title card, page context, description, transcript page, pinned comment, or linked summary block.
What it should not be is a floating replay or short clip with no scope, no date, no help path, and no way to tell whether the viewer is holding a current answer or historical footage.

## Live, archived, and “still current” discipline

Official video surfaces often blur together content with very different time semantics.
A livestreamed emergency briefing, an evergreen “how to register” explainer, a pre-election webinar, and a post-election process video do not age the same way.

So a video surface should make its status explicit.
That means:
- distinguish live briefings from archived replays,
- label whether the recording is intended as an enduring explainer or an election-specific artifact,
- state when a replay is historical background rather than current operational guidance,
- and keep the written destination current even when the video remains visible for historical or transparency reasons.

A still-available replay is not automatically a still-controlling answer.
The archive should not assume “still published” means “still current.”

## Clip-context, captions, and correction discipline

Video surfaces have a clip problem.
Short excerpts travel without the opening explanation.
Timestamped segments get quoted on social platforms.
Auto-generated captions can mangle names, deadlines, or place names.
A platform preview image can make old footage look new.

So when a material public answer changes, the correction should be **explicit**.

That means:
- publish a superseding written destination or linked correction when the earlier recording no longer controls,
- update the video description, pinned note, or adjacent official page when practical,
- avoid treating detached clips as standalone rulebooks,
- review captions or transcript text for action-changing content when the office is relying on them as part of the public answer,
- and keep a bounded note about whether the clip is excerpted from a fuller recording.

Deletion may still be appropriate for accidental duplicates or obvious upload mistakes.
But an action-changing official video that the public was expected to rely on should not silently remain in circulation with no current-state context.

## Accessibility, language access, and platform parity floor

A voter-information video is only operationally real if people can actually use it.
That means:
- captions or equivalent text support,
- transcript or summary support for action-changing recordings,
- plain language,
- accessible embed or playback patterns where the office controls the player,
- translated, interpreted, or language-parity variants where the jurisdiction maintains them,
- and a non-video help path for viewers who cannot use or trust the recording alone.

Do not let the spoken script, captions, transcript, pinned summary, linked FAQ/help page, and hotline/help route drift into different effective answers.

## Canonical digest artifacts

Publish **small digests of the video-surface lane**, not full media archives by default.

- **Video Surface Digest (VSD):** digest of the bounded policy payload for the official voter-information video lane.
- **Video Edition Digest (VED):** digest of a specific action-changing official video or livestream edition.
- **Video Correction / Superseding Digest (VCSD):** digest of an explicit correction or superseding event for a recording, replay, or republished clip.
- **Video/Web Parity Snapshot (VWPS):** optional digest tying a recording or clip to the linked page / FAQ / notice / hotline state.

## What belongs in the public video-surface payload

Keep the payload **small, current-state oriented, and replay-aware**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `video_family_label`
- `delivery_role_note`
- `material_formats[]`
- `distribution_platforms[]`
- `action_sensitive_topics[]`
- `edition_and_scope_policy`
- `canonical_destination_policy`
- `live_archive_status_policy`
- `clip_context_policy`
- `caption_and_transcript_policy`
- `correction_and_superseding_behavior`
- `accessibility_and_language_note`
- `public_help_route_uri`
- `public_help_route_phone`
- `latest_notice_uri`
- `last_verified_at`
- supersedes / superseded-by pointers

Do **not** publish by default:
- raw viewer analytics,
- full comment-thread archives,
- personal direct-message interactions,
- exhaustive platform moderation logs,
- or every frame-level media derivative the office generated internally.

## Verification questions for third parties

A verifier, journalist, observer, community partner, or court should be able to answer:
- Which official video or livestream lane was active at time `T`?
- Could an ordinary viewer tell what election/jurisdiction/scope the recording applied to?
- Did the recording identify when it was issued and whether it was still current?
- Did it point back to the current official page/help route, or did it pretend to be a standalone rulebook?
- Were captions, transcript, or equivalent text support available for the action-changing content?
- When the answer changed, was there an explicit correction or superseding trail visible from the recording or its controlling written destination?

## How this fits the family map

An official voter-information video, livestream, webinar, replay, or republished clip is **not** a new canonical voter-question family bucket.
It is a delivery layer over existing voter-facing questions already captured in `docs/310-*`.

Promote a video-surface issue to an underlying family surface only when the underlying question is distinct.
Examples:
- a video about **where to vote** still belongs to `292`, `297`, `298`, or `299`,
- a video about **which office to contact** still belongs to `305`,
- a video about **how to return a ballot** still belongs to `311`,
- a video about **special-case rights or accommodations** still belongs to the relevant `323–343` surface,
- and a video about **how to escalate a rights problem** still belongs to `307`.

`369` governs the audiovisual delivery layer itself.
It does not create a new substantive voter-question family by itself.

## Sources (pinned IDs / lockfile IDs)

- EAC: Clearinghouse Resources on Communications (xref: `eac_clearinghouse_resources_communications_page`)
- EAC: Communicating Election and Post-Election Processes Toolkit (xref: `eac_communicating_election_post_election_toolkit_2026_page`)
- EAC: Clearinghouse Resources on Accessibility (xref: `eac_clearinghouse_resources_accessibility_page`)
- EAC: Accessibility Checklist: Accessible Communications (xref: `eac_accessibility_checklist_accessible_communications_2024_pdf`)
- EAC: Effective Design for the Administration of Federal Elections (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`)
- NASS: #TrustedInfo2026 (xref: `nass_trustedinfo_2026_page`)
