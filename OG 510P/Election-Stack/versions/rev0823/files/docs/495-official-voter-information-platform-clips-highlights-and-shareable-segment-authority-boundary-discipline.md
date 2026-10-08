# 495 — Official voter-information platform clips, highlights, and shareable-segment authority-boundary discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **player- or platform-level clipped excerpts derived from already-open official voter-information media**:
viewer-created clips,
office-created highlights,
share-a-segment links,
looping excerpt pages,
and similar platform-supported mini-surfaces that break one official recording into a smaller portable segment.

It is not trying to turn every recording into a litigation hold.
It is trying to keep one practical public-risk seam from going soft:
**what happens when a platform lets the office or the public carve a short, public, reusable excerpt out of an already-open official recording and that excerpt begins to travel like the settled answer instead of a bounded slice of a larger recording.**

It composes with:
- `docs/305-election-office-contact-directories-office-hours-and-change-notices-as-evidence-surfaces.md`
- `docs/369-official-voter-information-videos-livestreams-and-clip-context-discipline.md`
- `docs/471-official-voter-information-copy-share-controls-clipboard-write-truthfulness-and-native-share-handoff-discipline.md`
- `docs/493-official-voter-information-platform-transcript-panes-searchable-transcripts-and-clip-jump-authority-boundary-discipline.md`
- `docs/494-official-voter-information-platform-chapter-markers-key-moments-and-shareable-chapter-list-authority-boundary-discipline.md`
- `docs/539-official-voter-information-platform-media-entrypoint-offset-aliases-current-time-start-at-routes-and-full-object-default-discipline.md`
- `artifacts/checklists/official-voter-information-platform-clips-surface-checklist.md`
- `artifacts/templates/official-voter-information-platform-clips-surface-payload.json`

## Why this exists (bounded)

The archive already covers the official recording lane itself (`369`), transcript panes/search (`493`), and chapter/key-moment jump maps (`494`).
That still leaves a smaller but distinct layer: **portable clipped excerpts and segment shares created from the already-open recording**.
Current platforms let viewers create public clips from a portion of a video or livestream, let creators or offices publish shorter highlights from a live stream, and let share links open directly to a bounded segment of a longer video with an option to jump back to the full recording.
YouTube’s current Clips help says clips are public, can be watched by anyone with access to the clip who can also watch the original video, are turned on by default, run 5–60 seconds, and can be shared by embed, social networks, email, or copied link.
The same help also says clips can appear on select search, discovery, and analytics surfaces and that channels can expose a public “Top community clips” section.
YouTube’s current live-stream Highlights help says creators can trim a shorter edited version of a live stream and that the created highlight is automatically published.
Vimeo’s current segment-sharing help says a URL can be amended with start and end parameters so the recipient can view the video clip on its own, with an option to switch to the full video.
(xref: `youtube_create_manage_clips_help_page`; xref: `youtube_create_highlight_help_page`; xref: `vimeo_share_video_segment_help_page`)

So the bounded question is not “are clips bad?”
Of course not.
The bounded question is smaller:
**when the voter is already on an official recording, do clipped excerpts, highlights, or share-a-segment links begin to behave like a portable stand-alone answer surface that outruns the office’s current written guidance, qualifiers, and correction lane?**

## This is not the same thing as the recording lane, transcript-pane lane, chapter lane, or play-next lane

`369` asks whether the office’s **published recording lane** has enough recording-date, edition, correction, and linkback discipline.

`493` asks whether a **transcript pane** turns the recording into a searchable, copyable, line-by-line text surface.

`494` asks whether **chapter markers, key moments, or chapter lists** turn the recording into a titled jump map.

`495` asks a different question:
**once the recording is already open, do platform-created clips, highlights, or shareable segment links turn one slice of that recording into a portable mini-publication whose surrounding qualifiers are easy to lose?**

If the distinct problem is **autoplay, end screens, cards, or player-driven next-step pivots that steer the voter onward from the recording rather than carving out one portable excerpt from it**, use `496`.
If the distinct problem is **player-native AI summaries or ask-this-video modules that generate a new answer layer over the recording rather than merely excerpting one segment**, use `499`.

A route may pass `369`, `493`, and `494` and still fail `495` if:
- the recording is current, but a 20-second clip strips away the scope qualifier that came 15 seconds earlier,
- a highlight title sounds universal even though the full briefing framed the answer as county-specific or election-specific,
- a clipped segment link opens on its own and the viewer never sees the page or portion of the recording that says “recheck before acting,”
- or a public clip shelf begins circulating the excerpt as though the clip itself is the office’s reviewed portable publication.

## Clipped excerpts are portable convenience surfaces, not automatic current editions

The public-safe posture is simple:
**a clip, highlight, or segment share can help a voter revisit part of an official recording, but it is not automatically the office’s reviewed current text edition or portable stand-alone rule surface.**

At minimum, keep these layers distinct:
1. the full official recording,
2. any office-reviewed FAQ, notice, transcript, summary, or page the office actually publishes as current guidance,
3. clipped or segmented media surfaces created by the platform or by users,
4. and the current written destination/help lane the office still wants voters to use when an excerpt is too narrow, stale, or decontextualized.

That distinction matters because clips are sparse by design.
They usually begin after some context has already been spoken and end before the next qualifier or recovery step appears.
Looped excerpts sharpen that effect because the voter can watch the segment repeatedly without the surrounding setup.
A share-a-segment URL is safer than a fake reupload, but it still creates a smaller surface that can feel complete when it is only partial.

## Publicity, discoverability, and default-on behavior change the risk

A clip surface is not just a private note-to-self.
Current platform guidance explicitly treats clips and highlights as public and shareable.
YouTube says clipping is turned on by default, clips are public, and clips can appear on select search, discovery, and analytics surfaces.
It also says a “Top community clips” section can be displayed publicly on a channel home tab.
YouTube’s highlight flow separately says the highlight is automatically published.
Vimeo’s segment-sharing guidance says the recipient can watch the segment on its own and then switch to the full video.
(xref: `youtube_create_manage_clips_help_page`; xref: `youtube_create_highlight_help_page`; xref: `vimeo_share_video_segment_help_page`)

That means the archive should not treat clip creation as a hidden user-side convenience.
A voter may encounter the clip first and the full recording second — or never.
So `495` should bias toward a modest discipline:
- keep the full recording and current written help lane recoverable from the excerpt,
- do not imply that a clipped excerpt is automatically the office’s current portable edition,
- and be honest about whether the excerpt was created by the office, by the platform, or by the public.

## Provenance honesty matters: office-created, viewer-created, and platform-shaped excerpts are not the same

The archive does **not** require offices to disable clips or highlights.
It requires the office to keep excerpt provenance honest.

The minimum distinction is:
- **office-created highlights or excerpt videos**,
- **viewer-created public clips from the official recording**,
- **share-a-segment links that still point into the original recording**,
- **public clip shelves or discovery surfaces**, and
- **no portable excerpt surface available**.

That distinction matters because the public may reasonably treat those surfaces differently.
An office-authored highlight might be an intentional public communication choice.
A viewer-created clip is still about the official recording, but the title, share context, and circulation path may not have been reviewed by the office.
A segment link that jumps into the original video preserves more provenance than a separately published clip, yet it can still behave like a stand-alone answer when separated from the full context.
If the later ambiguity is no longer about whether the excerpt behaved like a mini-publication but about whether a `Start at` or current-time route should still count as the same full object, use `539`.

If the archive lets those layers collapse into one story, later observers cannot tell whether a voter relied on:
- the full recording,
- an office-published highlight,
- a viewer-created clip,
- a share-a-segment URL,
- or a public clip/discovery shelf the office never directly authored.

## Excerpt surfaces need durable recovery to the full recording and the written help lane

The archive does **not** require every clip to repeat an entire FAQ.
It does require honest recovery.

For `495`, the public-safe posture is:
- a clipped segment should not be the only place a decisive instruction lives,
- the office should keep the full recording, current official page, or named help lane easy to recover,
- volatile topics should bias toward “recheck the current written route before acting,”
- and corrected or superseded excerpts should not keep circulating with no visible recovery path.

This matters especially for excerpts about:
- deadlines,
- polling-place or drop-box locations,
- ID or witness rules,
- ballot return instructions,
- cure, challenge, or provisional-ballot procedures,
- and any answer whose safe meaning depends on county, election date, or voter category.

## Clip titles and share context can overstate more than the media itself

A clip is not only the audio/video segment.
It also travels with:
- a clip title,
- a link-preview title or thumbnail,
- a share context supplied by the person forwarding it,
- and sometimes a public clip shelf or discovery label.

That bundle can overstate the answer faster than the excerpt itself.
A clip titled “Bring ID” or “Ballots due Tuesday” can feel like the whole rule even if the underlying excerpt was more careful.
So `495` should not quietly rely on the clip title to carry the same trust weight as the office’s reviewed FAQ or notice headline.

## Minimal state taxonomy

Keep at least these states separate:
- **office-created highlight published**
- **viewer-created public clips enabled**
- **viewer-created public clips disabled**
- **share-a-segment deep links available**
- **clip/discovery shelf publicly visible**
- **excerpt superseded or corrected**
- **no portable excerpt surface available**

The point is not to log every watcher or share recipient.
The point is to keep the public explanation honest about which excerpt surfaces existed and which ones the office actually stood behind.

## Bounded clip-surface trace minimum

A small public digest should make it possible to reconstruct:
- which official media routes were reviewed for clip/highlight/segment behavior,
- whether viewer-created clips were enabled,
- whether the office itself published shorter highlights,
- whether share-a-segment links or public clip shelves were in scope,
- where the full recording and current written help lane lived,
- and when the route was last verified.

It should **not** require storing individualized watch history, audience analytics, or all copied share messages.

## Minimal claim-set

1. **Excerpt-surface subordination claim:** clips, highlights, and shareable segment links stay subordinate to the full recording and the current written help lane.
2. **Excerpt-provenance claim:** the office distinguishes office-created highlights from viewer-created public clips and from share-a-segment deep links.
3. **Qualifier-loss claim:** clipped segments are reviewed for missing scope, date, jurisdiction, or correction context before they are treated as safe public-answer fragments.
4. **Portable-publication honesty claim:** a clip or shareable segment is not automatically treated as a reviewed official portable publication unless the office separately publishes and stands behind that edition.
5. **Recovery claim:** the excerpt surface keeps a durable path back to the full recording and current official help route for action-changing questions.

## Canonical digest artifacts

Publish **small digests of clip-surface posture**, not watch-history or full media archives by default.

- **Clip Surface Digest (CLSD):** digest of routes reviewed for clip/highlight/share-a-segment behavior.
- **Clip Provenance Note (CPN):** optional note identifying which excerpt surfaces the office authored, tolerated, or disabled.
- **Clip Recovery Boundary Note (CRBN):** optional note identifying how portable excerpts stay subordinate to the full recording and current written help lane.

## What belongs in the public clip-surface payload

Keep the payload **small, route-aware, and explicit about excerpt provenance and recovery**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `clip_surface_label`
- `delivery_role_note`
- `covered_surface_refs[]`
- `official_source_anchors[]`
- `reviewed_clip_contexts[]`
- `clip_generation_and_provenance_note`
- `publicity_and_discovery_note`
- `excerpt_boundary_note`
- `full_recording_recovery_note`
- `current_help_recovery_note`
- `latest_notice_uri`
- `last_verified_at`
- `supersedes[]`
- `superseded_by[]`

## References

- YouTube Help — Create & manage Clips. (xref: `youtube_create_manage_clips_help_page`)
- YouTube Help — Create a highlight. (xref: `youtube_create_highlight_help_page`)
- Vimeo Help Center — How to share a segment of a video. (xref: `vimeo_share_video_segment_help_page`)
