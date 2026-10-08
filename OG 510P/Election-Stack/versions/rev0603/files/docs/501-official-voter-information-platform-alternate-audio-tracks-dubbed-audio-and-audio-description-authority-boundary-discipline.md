# 501 — Official voter-information platform alternate audio tracks, dubbed audio, and audio-description authority-boundary discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **official voter-information routes whose already-open recording can also be consumed through a platform-native alternate spoken-audio layer**:
original audio,
creator-uploaded dubbed audio,
automatically generated dubbed audio,
audio-description tracks,
commentary tracks,
and similar player-visible audio options that let the viewer hear a materially different spoken rendering of the same official media without leaving the player.

It does not ban alternate audio.
It adds one narrow rule:
**when a platform lets viewers switch the spoken track of already-open official media, that alternate audio should stay visibly subordinate to the full recording, any reviewed official translated/help lane, and the current office-controlled recovery route instead of quietly becoming the practical authoritative spoken edition.**

It composes with:
- `docs/305-election-office-contact-directories-office-hours-and-change-notices-as-evidence-surfaces.md`
- `docs/369-official-voter-information-videos-livestreams-and-clip-context-discipline.md`
- `docs/377-official-voter-information-language-selectors-locale-fallback-and-machine-translation-boundary-discipline.md`
- `docs/492-official-voter-information-browser-integrated-live-captions-subtitle-translation-and-transcript-boundary-discipline.md`
- `docs/497-official-voter-information-platform-watch-later-saved-playlists-offline-downloads-and-smart-download-authority-boundary-discipline.md`
- `docs/499-official-voter-information-platform-ai-video-summaries-ask-this-video-and-answer-module-authority-boundary-discipline.md`
- `artifacts/checklists/official-voter-information-platform-alt-audio-surface-checklist.md`
- `artifacts/templates/official-voter-information-platform-alt-audio-surface-payload.json`

## Why this exists (bounded)

The archive already covers the recording lane itself (`369`), language selector and translation boundaries (`377`), generated captions/subtitles (`492`), saved-media replay (`497`), and AI-over-video answer modules (`499`).
A smaller but distinct seam remains:
**the official recording is already open, but the platform now offers a different spoken track that can sound like a reviewed current official answer in another language or modality.**

That is not just caption text.
It is not just the page’s language selector.
It is a player-native spoken surface that can change what the voter hears while leaving the surrounding watch page almost unchanged.

Current platform guidance is specific enough to justify a compact control here.
YouTube’s current multi-language-audio guidance says creators can add multiple audio tracks to new or existing videos.
Its automatic-dubbing guidance says translated audio tracks can be generated automatically, marked as “auto-dubbed” in the video description, switched by viewers between original and dubbed audio tracks, and may contain errors or be regenerated later.
Its viewer-language guidance says a viewer can change a specific video’s audio track in player settings.
Its audio-description guidance says descriptive audio tracks can also be uploaded as a distinct audio layer.
Vimeo’s current guidance says creators can add multiple audio tracks and classify them as dubbed audio, audio description, or commentary; viewers can switch audio tracks in the player’s settings; and Vimeo AI can translate a video’s audio and subtitles into multiple languages.
Microsoft’s current Clipchamp guidance says video owners can toggle player features for all viewers and lists **Audio files** among the possible player features.
(xref: `youtube_multilanguage_audio_help_page`; xref: `youtube_automatic_dubbing_help_page`; xref: `youtube_watch_preferred_language_help_page`; xref: `youtube_audio_descriptions_help_page`; xref: `vimeo_multiple_audio_tracks_help_page`; xref: `vimeo_change_audio_track_help_page`; xref: `vimeo_ai_translate_audio_subtitles_help_page`; xref: `microsoft_clipchamp_video_settings_toggle_help_page`)

So the bounded question is not “can alternate audio ever improve access?”
Of course it can.
The bounded question is smaller:
**once the official recording is already open, does an alternate spoken track begin to sound like the office’s reviewed current primary answer even though the office may only have reviewed the source-language recording, a separate translated/help lane, or one specific dubbed track?**

## This is not the same thing as language selectors, captions, saved downloads, or AI summaries

`377` asks whether the voter reaches the right **language path or fallback route** on the official site.

`492` asks whether **generated captions or translated subtitles** start to look like a reviewed official transcript or translated publication.

`497` asks whether **saved-media shelves or offline libraries** make an older recording keep looking current after the live route has moved.

`499` asks whether **player-native AI answer modules** start to sound like a reviewed official briefing.

`502` asks whether **detached playback modes such as picture-in-picture, popout, or background play** let the recording keep running after the source-page context fell away.

`501` asks a different question:
**once the official recording is already open, does the platform’s alternate spoken track — original, dubbed, descriptive, or commentary audio — begin to outrun the office’s actual reviewed translation/help posture and current written recovery lane?**

A route may pass `377`, `492`, `497`, and `499` and still fail `501` if:
- the voter hears an auto-dubbed track and assumes it is the office’s reviewed translated edition;
- a manually uploaded dubbed track sounds more current than the written translated help lane that actually controls operational questions;
- an audio-description or commentary track adds framing the office does not want treated as the controlling operational answer;
- the player remembers or suggests a spoken language that does not match the office’s reviewed multilingual route;
- or a viewer switches audio tracks and never rechecks the source-language recording date, correction status, or linked written help lane.

## Alternate spoken tracks are playback options, not automatic official editions

The public-safe posture is simple:
**an alternate audio track is a playback option over the recording, not automatic proof that the office reviewed, endorsed, or currently stands behind that exact spoken wording as the controlling official answer.**

At minimum, keep these layers distinct:
1. the full official recording and its date/scope/correction posture;
2. any office-reviewed translated page, transcript, subtitle file, or written help route;
3. the specific alternate spoken track the player exposes;
4. and the current office-controlled recovery route when the spoken track is incomplete, stale, unclear, or outside the office’s reviewed scope.

## Track provenance matters: original, creator-uploaded dub, auto dub, audio description, commentary

Not all alternate audio tracks carry the same authority posture.
For `501`, offices should distinguish at least:
- the original audio track;
- creator-uploaded dubbed audio;
- automatically generated dubbed audio;
- descriptive audio meant for accessibility rather than policy translation;
- and commentary tracks that may explain or contextualize rather than restate.

Those categories matter because the voter hears all of them as spoken authority, even when their provenance and review state are different.
YouTube explicitly distinguishes uploaded multi-language audio, automatic dubbing, and descriptive audio.
Vimeo explicitly distinguishes dubbed audio, audio description, and commentary track types.
(xref: `youtube_multilanguage_audio_help_page`; xref: `youtube_automatic_dubbing_help_page`; xref: `youtube_audio_descriptions_help_page`; xref: `vimeo_multiple_audio_tracks_help_page`)

So `501` should review not only whether alternate audio exists, but also whether the route makes clear what kind of spoken layer the voter is hearing.

## Automatic dubbing is useful, but its limits stay load-bearing

Automatic dubbing can expand access quickly, but the platforms themselves say it remains error-prone.
YouTube says automatic dubs may contain errors, can struggle with names, idioms, jargon, accents, and background noise, and may be regenerated later with different quality across languages.
Vimeo says AI-translated audio and subtitles can be generated in multiple languages, but if the underlying video is edited later the translations do not update automatically and may need retranslating.
(xref: `youtube_automatic_dubbing_help_page`; xref: `vimeo_ai_translate_audio_subtitles_help_page`)

So for high-risk voter instructions, `501` should bias toward keeping the current written route easy to recover instead of acting as though “the platform spoke it aloud in my language” settles the matter.

## High-risk topics should bias toward explicit written recovery

The risk is greatest when the recording covers questions whose safe answer depends on current state, local fit, or recent correction:
- locations and hours,
- registration or absentee deadlines,
- ID alternatives and cure paths,
- accommodations,
- disaster/outage contingencies,
- and any topic where a translation or summary may age faster than the linked written route.

For those topics, `501` does not require impossible perfect dubbing.
It requires the office to keep the **current written help lane** recoverable and to avoid talking as though every spoken track is the same thing as a reviewed current translated publication.

## Player language preference can silently change what the voter hears

This surface also matters because the player may let the viewer set preferences and then hear different spoken tracks on different visits or videos.
YouTube says viewers can indicate preferred languages for audio, titles, and descriptions, and can also switch audio tracks on a specific video.
Vimeo says viewers can switch audio tracks from the player settings when multiple tracks exist.
(xref: `youtube_automatic_dubbing_help_page`; xref: `youtube_watch_preferred_language_help_page`; xref: `vimeo_change_audio_track_help_page`)

So the office should not assume every voter heard the same spoken track just because they reached the same watch page.

## Minimal public evidence for this surface

A small public payload is enough.
It should preserve:
- which official recordings or watch routes were reviewed for alternate-audio behavior,
- which audio-track classes were present,
- whether any track was auto-generated, manually uploaded, descriptive, or commentary,
- what current written/help route controls when spoken tracks are incomplete or stale,
- and when the review was last performed.

It should not preserve:
- individualized viewer language preferences,
- private watch histories,
- per-user dubbing choices,
- or raw platform analytics the office does not need to prove its boundary posture.

## What this surface should prove

1. **Authority-boundary claim:** alternate spoken tracks do not outrank the full recording, reviewed official translated/help routes, or the current office-controlled recovery lane.
2. **Track-provenance claim:** the office distinguishes original audio, uploaded dubs, auto dubs, descriptive audio, and commentary when those differences matter to what the voter hears.
3. **Recovery claim:** volatile or high-risk questions still route back to the current written page, FAQ/help entry, or named office contact.
4. **Language-honesty claim:** the office does not quietly imply that every spoken language track is a reviewed equivalent official translation.
5. **Portability claim:** switched audio-track state does not silently become a stand-alone durable current edition of the answer.

## When to use `501`

Use `501` when the right official recording is already open, but the player can still change what the voter hears by switching among original audio, dubbed audio, descriptive audio, or commentary tracks.

Use instead:
- `377` for site language selectors and locale fallback before or alongside page arrival,
- `492` for generated captions/subtitles and transcript-boundary issues,
- `497` for saved-media or offline-library replay,
- `499` for AI summaries or answer modules over the recording,
- and `500` for comments, chat, Q&A, polls, or reactions around the recording.

## Sources

- YouTube Help: Add Multi-language features to your videos (xref: `youtube_multilanguage_audio_help_page`)
- YouTube Help: Use automatic dubbing (xref: `youtube_automatic_dubbing_help_page`)
- YouTube Help: Watch videos in your preferred language (xref: `youtube_watch_preferred_language_help_page`)
- YouTube Help: Add audio descriptions (xref: `youtube_audio_descriptions_help_page`)
- Vimeo Help Center: How to add multiple audio tracks to my video (xref: `vimeo_multiple_audio_tracks_help_page`)
- Vimeo Help Center: How to change the audio track of a Vimeo video (xref: `vimeo_change_audio_track_help_page`)
- Vimeo Help Center: How to use Vimeo AI to translate my video's audio and subtitles (xref: `vimeo_ai_translate_audio_subtitles_help_page`)
- Microsoft Support: Turn video settings on or off (xref: `microsoft_clipchamp_video_settings_toggle_help_page`)

## Minimal operator artifacts in this archive

- Template payload: `artifacts/templates/official-voter-information-platform-alt-audio-surface-payload.json`
- Operator quickcheck: `artifacts/checklists/official-voter-information-platform-alt-audio-surface-checklist.md`
