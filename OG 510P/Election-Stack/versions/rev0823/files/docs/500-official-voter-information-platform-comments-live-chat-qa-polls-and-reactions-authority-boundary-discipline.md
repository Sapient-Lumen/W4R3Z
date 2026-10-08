# 500 — Official voter-information platform comments, live chat, Q&A, polls, and reactions authority-boundary discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **official voter-information routes whose already-open recording, watch page, or event page also exposes a platform-native social interaction layer**:
viewer comments,
pinned comments,
live chat,
chat replay,
live Q&A,
live polls,
likes or reactions,
and similar audience-response surfaces that sit beside the official recording without being the recording itself.

It does not ban interaction.
It adds one narrow rule:
**when a platform-native interaction layer sits beside already-open official media, that conversational layer should stay visibly subordinate to the full recording, any current written notice/help lane, and the office-controlled recovery route instead of quietly becoming the practical help desk, correction lane, or current instruction surface.**

It composes with:
- `docs/305-election-office-contact-directories-office-hours-and-change-notices-as-evidence-surfaces.md`
- `docs/369-official-voter-information-videos-livestreams-and-clip-context-discipline.md`
- `docs/471-official-voter-information-copy-share-controls-clipboard-write-truthfulness-and-native-share-handoff-discipline.md`
- `docs/494-official-voter-information-platform-chapter-markers-key-moments-and-shareable-chapter-list-authority-boundary-discipline.md`
- `docs/495-official-voter-information-platform-clips-highlights-and-shareable-segment-authority-boundary-discipline.md`
- `docs/496-official-voter-information-platform-autoplay-end-screens-cards-and-play-next-authority-boundary-discipline.md`
- `docs/498-official-voter-information-platform-follows-subscriptions-and-live-event-reminder-authority-boundary-discipline.md`
- `docs/499-official-voter-information-platform-ai-video-summaries-ask-this-video-and-answer-module-authority-boundary-discipline.md`
- `docs/516-official-voter-information-platform-live-edge-behind-live-state-latency-and-watch-live-recovery-authority-boundary-discipline.md`
- `docs/558-official-voter-information-platform-media-interaction-pane-states-social-tab-focus-and-head-default-retention-discipline.md`
- `artifacts/checklists/official-voter-information-platform-social-layer-surface-checklist.md`
- `artifacts/templates/official-voter-information-platform-social-layer-surface-payload.json`

## Why this exists (bounded)

The archive already covers the recording lane itself (`369`), chapter maps (`494`), clipped excerpts (`495`), autoplay adjacency (`496`), follow/reminder state (`498`), and AI-over-video answer modules (`499`).
A smaller but distinct seam remains:
**the official recording is already open, but the platform adds a social layer where viewers can comment, react, ask questions, vote in polls, or replay the conversation around the media.**

That is not just the recording.
It is not just a reminder or a clip.
It is a second, semi-conversational surface that can feel like the easiest way to ask what the office "really means," spot the latest update, or infer the safe next step from audience chatter, pinned replies, or moderator action.

Current platform guidance is specific enough to justify a compact control here.
YouTube’s current live-chat guidance says live chat is on by default for eligible streams, is archived with the live stream, supports Top Chat filtering, reactions, live Q&A, and AI-generated chat summaries for some viewers.
Its Premiere guidance says a public watch page exists before the premiere begins, where viewers can leave comments or chat, and chat replay remains available after the premiere.
Its comment guidance says comments can be on, paused, or off, and a channel can pin a comment at the top of the watch page.
Vimeo’s current guidance says comments appear on the video page, can be linked directly, and can be downloaded from video settings; live-event pages can expose chat, polls, and Q&A controlled by the organizer; live chat can remain active even before the stream begins and only the most recent 100 messages are shown in-browser; moderated Q&A can approve, archive, anonymize, and show selected questions on scene.
Microsoft’s current Clipchamp guidance says owners can toggle comments and reactions for all viewers on the player page, and the player supports liking and commenting on a video.
(xref: `youtube_live_chat_help_page`; xref: `youtube_premiere_new_video_help_page`; xref: `youtube_comment_settings_help_page`; xref: `youtube_review_reply_comments_help_page`; xref: `vimeo_use_comments_help_page`; xref: `vimeo_manage_comments_video_help_page`; xref: `vimeo_live_event_chat_poll_qa_help_page`; xref: `vimeo_live_chat_moderation_web_studio_help_page`; xref: `vimeo_live_event_qa_moderation_help_page`; xref: `microsoft_clipchamp_video_settings_toggle_help_page`; xref: `microsoft_clipchamp_video_capabilities_help_page`; xref: `microsoft_clipchamp_screen_reader_play_videos_help_page`)

So the bounded question is not "should an office never allow platform comments or live chat?"
Of course not.
The bounded question is smaller:
**once a social layer sits beside already-open official media, does that layer start to look like a reviewed official FAQ, correction feed, or current instruction desk even though it is only a platform-managed interaction surface?**

## This is not the same thing as follow state, AI answers, clips, or the recording lane

`369` asks whether the **official recording or livestream lane itself** carries enough date, scope, correction, and transcript/linkback discipline.

`498` asks whether a **platform-managed follow, subscription, or reminder relationship** starts to feel like a durable official notice service.

`499` asks whether a **player-native AI summary or question-answer module** starts to feel like an official briefing.

`508` asks whether a **public pre-start event shell** begins to feel like the current official answer page before the event has even started.

`509` asks whether a **post-live replay shell or ended-event route** begins to feel like the current official answer after the event has already ended.

`516` asks whether a **still-live event can place a viewer materially behind the true live edge while chat, Q&A, or other companion panes reflect a later moment**.

`519` asks whether **views, concurrent-viewer counts, likes, registrations, attendance totals, or similar metrics around the same media start sounding like proof of authority or currentness even apart from what anyone actually said in chat or comments**.

`558` asks the chain-layer follow-on question: once `500` already governs the social layer and the same media object still controls, should the archive preserve that comments were open, Top Chat rather than Live Chat was selected, a Q&A pane was foregrounded, or one interaction feed/tab was visible **without** treating that pane state like a new route, a reviewed official answer, or a safer citation target than the head?

`500` asks a different question:
**once comments, chat, Q&A, polls, or reactions sit beside official media, does that social layer begin to feel like the office’s current help desk or correction lane even though the platform decides who can speak, what is highlighted, what is filtered, and what survives replay or sharing?**

A route may pass `369`, `498`, and `499` and still fail `500` if:
- a pinned comment reads like the controlling update but is harder to trace back to the current written page than the office intended,
- live-chat replay makes audience guesses or moderator banter look like part of the enduring official explanation,
- a poll result or Q&A card is interpreted as binding operational guidance rather than an engagement tool,
- copied or linked comments travel farther than the full recording and lose surrounding qualifiers,
- or likes/reactions/social proof make one audience interpretation feel like the endorsed answer even when no office notice changed.

## Social interaction layers are conversation surfaces, not automatic official guidance

The public-safe posture is simple:
**comments, live chat, Q&A, polls, and reactions are interaction surfaces around the official media, not proof that the office reviewed, adopted, or currently stands behind everything visible there.**

At minimum, keep these layers distinct:
1. the full official recording and its date/scope/correction posture;
2. the current written page, FAQ/help entry, or named office contact that still controls operational questions;
3. the platform-managed interaction surface where viewers, moderators, or organizers can talk about the recording;
4. and any highlighted, pinned, replayed, linked, or summarized fragment of that interaction layer.

## Pinned, highlighted, or approved items carry extra authority risk

The highest-risk items are usually not the raw stream of messages.
They are the parts the platform or organizer elevates:
- pinned comments,
- Top Chat filtering,
- approved Q&A cards,
- highlighted/featured comments,
- copied comment links,
- chat replay,
- or visible reaction counts.

Those cues can make one sentence feel closer to an official annotation or endorsed update than it really is.
YouTube explicitly supports pinned watch-page comments and filters live chat through Top Chat.
Vimeo explicitly supports approving/archive states for Q&A, highlighting some comments on profile pages, direct links to comments, and export/download of comment or chat data.
(xref: `youtube_review_reply_comments_help_page`; xref: `youtube_live_chat_help_page`; xref: `vimeo_use_comments_help_page`; xref: `vimeo_manage_comments_video_help_page`; xref: `vimeo_live_event_qa_moderation_help_page`; xref: `vimeo_profile_page_featured_comments_faq_page`)

So `500` should review not only whether interaction exists, but also whether the platform can make one message, question, or result feel like the settled answer.

## Replay, copying, and limited windows change what survives

This surface also matters because the interaction layer does not always survive or travel in the same way as the recording.
YouTube says live chat is archived with the stream and Premiere chat replay remains available after the event, while live polls do not appear in chat replays.
Vimeo says browser chat only shows the 100 most recent messages during the event, chat may stay active even before the stream begins, comment links can deep-link to a specific comment, and comments or chats can be downloaded/exported from some management surfaces.
(xref: `youtube_live_chat_help_page`; xref: `youtube_premiere_new_video_help_page`; xref: `vimeo_use_comments_help_page`; xref: `vimeo_manage_comments_video_help_page`; xref: `vimeo_live_chat_moderation_web_studio_help_page`)

So the office should not assume:
- the social layer is ephemeral just because it began as chat,
- the replay or copied fragment preserves enough surrounding context,
- or that what survives in replay is a complete record of what users saw live.

## AI or translation layered onto chat stays inside `500` only as social-layer compression

Some platforms now add transformations to the interaction layer itself.
YouTube says new viewers may see an AI-generated summary of the current chat and notes it may be inaccurate or inappropriate.
YouTube also supports creator-side automatic chat translation on some mobile live streams.
Those features matter here only because they **compress or reframe the interaction layer**.
They do not turn the conversation into a reviewed office publication.
(xref: `youtube_live_chat_help_page`)

So if an interaction layer is further summarized, translated, or filtered, `500` keeps the same boundary:
**the transformed social layer still stays subordinate to the official recording plus the current written recovery lane.**

## Minimal public evidence for this surface

A small public payload is enough.
It should preserve:
- which official media routes were reviewed for comments/chat/Q&A/polls/reactions,
- whether elevated interaction states such as pinned comments, Top Chat, approved Q&A, or comment links were present,
- whether replay, copying, or export existed,
- what current written route or named office contact controlled when interaction became ambiguous,
- and when the review was last performed.

It should not preserve:
- per-user comment histories,
- private moderation logs,
- reaction telemetry tied to individuals,
- or full chat exports unless another evidence obligation independently requires them.

## What this surface should prove

1. **Authority-boundary claim:** comments, chat, Q&A, polls, and reactions do not outrank the full recording or the current office/help lane.
2. **Elevation-control claim:** pinned, highlighted, filtered, replayed, or approved interaction fragments do not silently become stand-alone official instructions.
3. **Replay/copy honesty claim:** replay, deep links, copied comments, and exported interaction artifacts are treated as context-limited conversation fragments rather than automatic official records.
4. **Recovery claim:** high-risk or time-sensitive questions still recover to the current written page, reviewed FAQ/help entry, or named office contact.
5. **Moderation-boundary claim:** organizer moderation, platform filtering, and social proof signals are visible interaction controls, not proof that the remaining visible content is the full or endorsed official answer.

## When to use `500`

Use `500` when the right official recording, watch page, or live-event page is already open, but a platform-native interaction layer can still make audience conversation, pinned messages, moderator choices, or social proof feel more authoritative than the office intended.

Use instead:
- `498` for follow/subscription/reminder relationships,
- `499` for player-native AI summaries or answer modules,
- `495` for clipped excerpts or highlights,
- `494` for chapter maps and key moments,
- and `471` for generic copy/share control truthfulness outside this media-social seam.

## Sources

- YouTube Help: Learn about Live Chat (xref: `youtube_live_chat_help_page`)
- YouTube Help: Premiere a new video (xref: `youtube_premiere_new_video_help_page`)
- YouTube Help: Learn about comment settings (xref: `youtube_comment_settings_help_page`)
- YouTube Help: Review and reply to comments (xref: `youtube_review_reply_comments_help_page`)
- Vimeo Help Center: How to use comments (xref: `vimeo_use_comments_help_page`)
- Vimeo Help Center: How to manage comments on my video (xref: `vimeo_manage_comments_video_help_page`)
- Vimeo Help Center: Participate in a live event chat, poll, or Q&A session (xref: `vimeo_live_event_chat_poll_qa_help_page`)
- Vimeo Help Center: How to activate, deactivate, and moderate live chat from the web studio (xref: `vimeo_live_chat_moderation_web_studio_help_page`)
- Vimeo Help Center: How can I moderate Q&A for a live event? (xref: `vimeo_live_event_qa_moderation_help_page`)
- Vimeo Help Center: Profile page FAQ (xref: `vimeo_profile_page_featured_comments_faq_page`)
- Microsoft Support: Turn video settings on or off (xref: `microsoft_clipchamp_video_settings_toggle_help_page`)
- Microsoft Support: Learn more about the Clipchamp video capabilities in Microsoft 365 (xref: `microsoft_clipchamp_video_capabilities_help_page`)
- Microsoft Support: Use a screen reader to play videos in Microsoft Clipchamp (xref: `microsoft_clipchamp_screen_reader_play_videos_help_page`)
