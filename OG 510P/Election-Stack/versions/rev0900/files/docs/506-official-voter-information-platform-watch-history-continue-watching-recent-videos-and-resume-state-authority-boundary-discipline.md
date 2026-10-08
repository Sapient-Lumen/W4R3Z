# 506 — Official voter-information platform watch history, continue-watching rows, recent-videos, and resume-state authority-boundary discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **platform-native re-entry surfaces attached to already-open official voter-information recordings**:
watch history,
continue-watching rows,
recent-videos or recently viewed lists,
resume-from-last-position state,
cross-device “pick up where you left off” behavior,
and similar platform- or account-managed resurfacing that brings a previously watched official recording back into view later.

It does not try to ban ordinary history or resume features.
It adds one narrow control:
**when a platform resurfaces a previously watched official recording through history, continue-watching, recent-videos, or resume-state, that re-entry surface should stay visibly subordinate to the current recording edition and the current written help lane instead of quietly becoming a shadow “still-current official return path.”**

It composes with:
- `docs/305-election-office-contact-directories-office-hours-and-change-notices-as-evidence-surfaces.md`
- `docs/369-official-voter-information-videos-livestreams-and-clip-context-discipline.md`
- `docs/496-official-voter-information-platform-autoplay-end-screens-cards-and-play-next-authority-boundary-discipline.md`
- `docs/497-official-voter-information-platform-watch-later-saved-playlists-offline-downloads-and-smart-download-authority-boundary-discipline.md`
- `docs/498-official-voter-information-platform-follows-subscriptions-and-live-event-reminder-authority-boundary-discipline.md`
- `docs/505-official-voter-information-platform-playback-speed-scrubbing-skipping-and-seek-authority-boundary-discipline.md`
- `docs/543-official-voter-information-platform-media-remembered-resume-aliases-history-reentry-and-full-object-default-discipline.md`
- `artifacts/checklists/official-voter-information-platform-history-resume-surface-checklist.md`
- `artifacts/templates/official-voter-information-platform-history-resume-surface-payload.json`

## Why this exists (bounded)

The archive already covers the recording lane itself (`369`), immediate autoplay / play-next continuity (`496`), explicit saved-media shelves (`497`), follow and reminder state (`498`), and scan posture inside the player (`505`).
That still leaves a small but distinct layer:
**the voter watched the official recording before, and the platform later offers it back through history, continue-watching, recents, or remembered progress in a way that can feel current, deliberate, and complete even though the office never reviewed that resurfacing layer as the controlling answer lane.**

Current platform guidance is specific enough to justify this as a bounded control.
YouTube’s current recommendations help says watch history can influence Home recommendations, Watch Next, search results, in-app notifications, and other YouTube experiences, and that users can turn off watch history if they do not want watches to influence future recommendations.
Its current recommendations overview says watch history helps give better recommendations, **remember where you left off**, and more.
Its current watch-history help says viewers can search their watch history and browse it by date range.
Vimeo OTT’s current Continue Watching help says the Continue Watching row appears on web, mobile, and TV apps, follows the same account across devices, shows in-progress items with time remaining, and can also surface the next video in a playlist or series collection.
Microsoft’s current Clipchamp-for-work guidance says users can find and get back to recent videos, including shared ones, from the Clipchamp homepage in Microsoft 365.
And Microsoft’s current recent-files guidance says recently opened files can appear from any of a user’s devices and that the recent list can synchronize across devices, including cases where older or unexpected files reappear after synchronization.
(xref: `youtube_manage_recommendations_search_results_help_page`; xref: `youtube_how_recommendations_work_help_page`; xref: `youtube_watch_history_help_page`; xref: `vimeo_continue_watching_row_help_page`; xref: `microsoft_clipchamp_video_capabilities_help_page`; xref: `microsoft_recent_files_list_help_page`)

So the bounded question is not “should platforms remember what a voter watched?”
Of course they will.
The bounded question is smaller:
**once a previously watched official recording resurfaces through history or resume state, does that re-entry lane start to feel like a still-current official answer shelf even though it is only a platform memory of past viewing?**

## This is not the same thing as autoplay, explicit saves, follows, or scan posture

`496` asks whether the platform silently keeps the voter moving **forward** from the already-open recording into another item through autoplay, end screens, cards, or play-next surfaces.

`497` asks whether the voter or platform created a more durable **saved-media shelf** such as Watch Later, playlists, or offline downloads.

`498` asks whether the platform recorded a **relationship or future reminder state** such as a follow, subscription, or live-event reminder.

`505` asks whether the voter consumed the recording through a **fragmentary scan posture** such as seeking, scrubbing, rewinding, or accelerated playback.

`506` asks a different question:
**after the recording has already been watched at least once, does the platform’s history, continue-watching, recents, or resume-state surface re-offer it in a way that feels like the current official return path, even though the office only reviewed the recording together with its live written/help route?**

If the distinct problem is **immediate next-step continuation while the session is still underway**, use `496`.
If the distinct problem is **an explicit save into Watch Later, playlists, or offline libraries**, use `497`.
If the distinct problem is **follow/subscription state or reminder registration for future media events**, use `498`.
If the distinct problem is **an office-curated channel home, featured-video slot, playlist, or collection page rather than platform memory of prior viewing**, use `507`.
If the distinct problem is **the public upcoming-event shell that existed before playback started rather than later history-driven resurfacing**, use `508`.
If the distinct problem is **not whether history/Continue Watching exists as a surface at all, but how one same-object media chain should record a remembered re-entry path without promoting it into the current head or confusing it with an explicit offset route**, use `543`.

A route may pass `496`, `497`, `498`, and `505` and still fail `506` if:
- a voter reopens an official explainer from watch history after deadlines, locations, or cure instructions changed;
- a continue-watching row offers the next item in a series collection and the voter experiences that resurfaced sequence as still-current official continuity;
- remembered progress resumes mid-recording, so the voter re-enters near the part previously watched and misses the newer caveat or correction route;
- cross-device sync brings an older official recording back into a recent-videos shelf that now looks endorsed because it is easy to reopen;
- or the office never distinguishes “the platform remembered that you watched this” from “the office intentionally published this as the current way back in.”

## Watch history is memory, not proof of current authority

The public-safe posture is simple:
**history, continue-watching, recent-videos, and resume-state surfaces are memory and convenience layers, not proof that the resurfaced recording still carries current authority, freshness, or enough context to act safely without the current written/help lane.**

At minimum, keep these layers distinct:
1. the current official recording and its linked current written/help lane;
2. the platform’s memory that the voter watched or partially watched the recording before;
3. any remembered resume position, cross-device sync, or “continue watching” ranking state;
4. and any neighboring or next-in-series videos the platform places beside that resurfaced item.

That distinction matters because re-entry surfaces feel earned.
A voter often experiences “this came back because I was already watching it” as stronger evidence than “this was merely recommended.”
If the archive lets those layers collapse into one story, later observers cannot tell whether the voter relied on:
- the current official route,
- a resurfaced previously watched recording,
- a remembered mid-stream resume point,
- or a series/playlist continuation that only looked like the same official answer lane.

## Remembered progress can hide the parts that carried the caveat

Resume-state is useful precisely because it avoids replaying what the viewer already saw.
That same convenience can hide the parts that carried the critical qualifier.
YouTube says watch history helps remember where the viewer left off.
Vimeo says in-progress videos appear in the Continue Watching row with minutes remaining.
(xref: `youtube_how_recommendations_work_help_page`; xref: `vimeo_continue_watching_row_help_page`)

For `506`, offices should review whether:
- re-entry lands near the right explanatory segment **and** still leaves the current written/help lane recoverable;
- the remembered position skips past the date, scope, correction, or escalation note;
- and the office’s public wording accidentally treats “resume where you left off” as equivalent to “you are back in the current controlling answer.”

## Cross-device and synchronized recents are especially easy to overread

Current platform guidance also makes clear that re-entry state is not confined to one screen.
Vimeo says the same Continue Watching row can follow the same account across web, mobile, and TV apps.
Microsoft says recent files can appear from any of a user’s devices and that synchronization can cause older or unexpected files to reappear.
(xref: `vimeo_continue_watching_row_help_page`; xref: `microsoft_recent_files_list_help_page`)

For `506`, that means:
- the office should not imply that a resurfaced recording is current merely because it reappeared on a different device;
- the office should review whether TV, mobile, desktop, and work-suite recents expose different context, titles, or recovery affordances;
- and a synchronized recent list should stay subordinate to the current official written/help lane, especially when old election-cycle recordings are still reachable.

## History-shaped recommendations can quietly look like continuity

History does not only preserve a lookup list.
It can also shape what the platform shows next time.
YouTube says watch history can influence Home recommendations, Watch Next, search results, in-app notifications, and other experiences.
Vimeo’s Continue Watching help says the row can also surface the **next** video in a playlist or series collection.
(xref: `youtube_manage_recommendations_search_results_help_page`; xref: `vimeo_continue_watching_row_help_page`)

That means `506` should review not just “is the prior official video listed somewhere?”
but also whether history-driven resurfacing begins to feel like a coherent official continuation path because:
- the same official video returns on Home,
- a recent-videos shelf makes older recordings feel endorsed,
- or a continue-watching row quietly advances the viewer into another item that inherits the appearance of current official continuity.

## Preserve practical recovery to the current route

For `506`, the bounded rule is not to abolish memory or resume features.
It is to make sure the office still tells the truth after the platform remembers prior viewing.
At minimum:
- a resurfaced recording should still point back to the current written page, notice, FAQ/help entry, or named office contact for action-changing questions;
- offices should be explicit that history/resume convenience is not the same thing as currentness review;
- volatile or corrected topics should trigger “recheck the current route” language rather than “continue watching the old recording”; and
- if the office intentionally relies on series continuity, it should still expose the current controlling destination outside the platform memory layer.

## Keep history-driven resurfacing distinct from deliberate publication decisions

The most important non-overlap rule is small:
**history or continue-watching state is not itself a publication decision by the office.**

So for `506`, keep these seams explicit:
- **immediate autoplay / end-screen / card continuation**, use `496`;
- **explicit saves, Watch Later, playlists, or offline downloads**, use `497`;
- **follows, subscriptions, or event reminders**, use `498`;
- **playback-speed, scrubbing, skipping, or seek posture**, use `505`.

A route can compose several of those at once.
`506` only asks whether **past viewing memory** turned the resurfaced recording into a shadow return path that now looks current because the platform remembered it.
If the archive already knows the surface family is `506` and only needs one compact same-object chain note for how that memory-shaped return should be cited and kept subordinate to the head, use `543`.

## Minimal public proof posture

If an office relies materially on official media that may resurface through history or continue-watching layers, it should be able to publish a compact proof bundle that says:
- which recording or watch route was reviewed;
- which history / continue-watching / recent-videos / resume contexts were actually tested;
- how the route pointed back to the current written/help lane when reopened later;
- whether re-entry behavior varied across device classes or account states;
- and when that review was last verified.

Do **not** publish individualized watch histories or account logs.
The goal is a compact public record of the reviewed resurfacing posture, not behavioral surveillance.

## Verification questions for third parties

1. Did the official recording reappear through history, continue-watching, recents, or resume-state after the initial viewing session?
2. When reopened that way, was the current official written/help lane still practically recoverable before action-changing reliance?
3. Did remembered progress or partial-view state skip past the segment that carried date, scope, correction, or escalation cues?
4. Did cross-device sync, series continuation, or recommendation shaping make older or adjacent videos look like the current official route?
5. Can the office show a small review record for the actual re-entry contexts it expected voters to encounter?

## Artifacts and companion references

- Template payload: `artifacts/templates/official-voter-information-platform-history-resume-surface-payload.json`
- Operator quickcheck: `artifacts/checklists/official-voter-information-platform-history-resume-surface-checklist.md`
- Nearby boundaries: `496`, `497`, `498`, `505`
