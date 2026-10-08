# 497 — Official voter-information platform Watch Later, saved playlists, offline downloads, and smart-download authority-boundary discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **platform-managed saved-media surfaces attached to already-open official voter-information recordings**:
Watch Later saves,
saved playlists,
offline video downloads inside the platform app,
auto-filled download libraries such as Smart Downloads,
and similar account- or device-bound media stashes that let the voter revisit an official recording later without returning through the live current official page/help lane first.

It does not try to ban ordinary saving behavior.
It adds one narrow control:
**when a platform lets the voter save an already-open official recording into a personal watch-later, playlist, or offline library, that saved-media surface should stay visibly subordinate to the current recording edition and the current written help lane instead of quietly becoming a shadow private library of “still-current official answers.”**

It composes with:
- `docs/369-official-voter-information-videos-livestreams-and-clip-context-discipline.md`
- `docs/410-official-voter-information-third-party-dependencies-embeds-and-external-origin-fail-open-discipline.md`
- `docs/413-official-voter-information-external-destinations-non-federal-handoffs-and-new-context-fail-open-discipline.md`
- `docs/490-official-voter-information-browser-managed-reading-lists-offline-saved-pages-and-web-archive-authority-boundary-discipline.md`
- `docs/495-official-voter-information-platform-clips-highlights-and-shareable-segment-authority-boundary-discipline.md`
- `docs/496-official-voter-information-platform-autoplay-end-screens-cards-and-play-next-authority-boundary-discipline.md`
- `docs/498-official-voter-information-platform-follows-subscriptions-and-live-event-reminder-authority-boundary-discipline.md`
- `artifacts/checklists/official-voter-information-platform-saved-media-surface-checklist.md`
- `artifacts/templates/official-voter-information-platform-saved-media-surface-payload.json`

## Why this exists (bounded)

The archive already covers the office recording lane itself (`369`), browser-kept page copies (`490`), portable clips/highlights (`495`), and autoplay / next-step handoffs (`496`).
That still leaves a small but distinct layer:
**platform-managed saved-media surfaces that let the voter carry the recording forward in a personal library, queue, or offline stash that may later feel more current, more deliberate, or more officially packaged than it really is.**

Current platform guidance is specific enough to justify this as a bounded control.
YouTube’s current Watch Later help says viewers can add a video or Short to Watch Later while browsing or from the watch page.
Its current playlist help says videos can be saved to playlists, that “Save” can default to the last playlist or Watch Later, and that playlists can be created with privacy settings.
Its current offline help says certain videos can be downloaded in the mobile app for offline viewing and that the app must later reconnect to check whether the video or its availability changed.
YouTube’s current offline FAQ says downloaded videos are stored encrypted on the device and can only be watched in the YouTube app.
Its current Smart Downloads help says recommended videos are automatically added to a viewer’s downloads.
Vimeo’s current Watch Later help says public videos can be added to a private Watch Later page and that the owner may disable Watch Later for public videos.
Vimeo’s current app guidance says videos can be saved to an offline playlist for no-network playback, and that offline videos stay inside the Vimeo app and cannot be exported to other apps.
(xref: `youtube_watch_later_help_page`; xref: `youtube_create_manage_playlists_help_page`; xref: `youtube_watch_videos_offline_mobile_help_page`; xref: `youtube_videos_offline_faq_help_page`; xref: `youtube_smart_downloads_help_page`; xref: `vimeo_about_watch_later_help_page`; xref: `vimeo_viewer_features_android_help_page`)

So the bounded question is not “should voters ever save a video for later?”
Of course they will.
The bounded question is smaller:
**once an official recording has been saved into Watch Later, a playlist, or an offline library, does that platform-managed stash start to behave like a durable, still-current official reference shelf even after the live answer lane has changed?**

## This is not the same thing as the recording lane, browser saved-copy lane, clip lane, or play-next lane

`369` asks whether the **published official recording lane itself** carries enough recording-date, scope, correction, and linkback discipline.

`490` asks whether the **browser kept a copy of the page** around the recording and whether that captured page still tells the truth when reopened later.

`495` asks whether **portable clips or highlights** turned one slice of the recording into a mini-publication.

`496` asks whether **autoplay, cards, end screens, or more-videos surfaces** quietly hand the voter into another route.

`502` asks whether **detached playback modes such as picture-in-picture, popout, or background play** keep the already-open recording running after the source-page context falls away.

`497` asks a different question:
**once the voter deliberately or semi-automatically saves the already-open official recording into a platform-managed library, does that saved-media surface begin to look like a stable current official shelf even though it is only a viewer-managed stash with its own ordering, retention, and adjacency behavior?**

If the distinct problem is **follow/subscription state or reminder registration for future official media events rather than a saved-media shelf**, use `498`.
If the distinct problem is **history-driven resurfacing, continue-watching rows, recent-videos shelves, or remembered resume-state rather than an explicit save or offline library**, use `506`.
If the distinct problem is **not the saved-media surface itself but the same-object chain question of how the recording later came back through Watch Later, a saved playlist entry, or an offline-library reopen path**, use `553`.
If the distinct problem is **an office-curated channel home, featured-video slot, playlist landing page, or collection surface rather than the voter's saved-media shelf**, use `507`.
If the distinct problem is **the public upcoming-event shell that preceded the recording rather than a later save into the voter's library**, use `508`.

A route may pass `369`, `490`, `495`, and `496` and still fail `497` if:
- a saved official recording is reopened from Watch Later after deadlines or locations changed,
- a playlist containing the official recording also contains older or unrelated videos that now look like the same answer lane,
- an offline copy survives long enough that the voter treats it as current simply because it still opens cleanly,
- Smart Downloads or similar features add neighboring videos into the same download library and the voter experiences that library as one official set,
- or the office never distinguishes “the voter saved this in the platform” from “the office intentionally published a durable current portable edition.”

## Platform-managed saved-media libraries are convenience stashes, not current official editions

The public-safe posture is simple:
**Watch Later items, saved playlists, offline downloads, and auto-filled download shelves are convenience stashes, not proof that the saved item still carries current authority, freshness, or jurisdictional scope.**

At minimum, keep these layers distinct:
1. the current official recording and its linked current written help lane,
2. any office-reviewed portable edition the office intentionally publishes,
3. the voter’s platform-managed saved-media shelf,
4. and any additional videos the platform or viewer placed beside the official recording.

That distinction matters because saved-media surfaces feel intentional.
A voter often experiences “I saved this official video” as stronger evidence than “I once viewed this route in passing.”
If the archive lets those layers collapse into one story, later observers cannot tell whether the voter relied on:
- the current official recording,
- a viewer-managed saved copy that was once correct,
- a mixed playlist or saved queue,
- or a platform-managed offline library that had already drifted from the current written answer lane.

## Offline availability is not the same thing as freshness

Offline capability often increases trust because the item still opens when network access is poor.
But that operability can hide staleness.
YouTube’s current offline help says the app reconnects later to check for changes to the video or its availability, and its FAQ says downloads remain encrypted on the device and only play in the app.
Vimeo’s current app guidance likewise says offline videos stay inside the app and cannot be exported.
(xref: `youtube_watch_videos_offline_mobile_help_page`; xref: `youtube_videos_offline_faq_help_page`; xref: `vimeo_viewer_features_android_help_page`)

For `497`, that means:
- the fact that a video still opens offline does **not** prove it is still the current answer,
- the platform’s later freshness check is **not** the same thing as an office-reviewed correction path,
- and in-app offline availability should stay subordinate to the current written help lane for deadlines, locations, eligibility, or emergency-change questions.

## Saved playlists can reshape sequence and adjacency

Playlists are not just neutral filing folders.
They can alter sequence, mix videos from different contexts, and make one official recording look like part of a larger curated set.
YouTube’s current playlist help says videos can be saved to playlists, playlists can have privacy settings, and playlist items can be reordered or temporarily hidden.
(xref: `youtube_create_manage_playlists_help_page`)

That means `497` should not treat “saved to a playlist” as equivalent to “the office reviewed this exact continuation context.”
A saved playlist can combine:
- the correct official explainer,
- older election videos,
- media commentary,
- county- and state-level recordings with different scopes,
- or unrelated civic content that simply sat nearby in a viewer-managed library.

So the archive should keep at least these states separate:
- **single official recording saved for later**
- **official recording saved into mixed personal playlist**
- **official recording saved into office-authored playlist**
- **official recording present in offline library only**
- **official recording absent because the platform or owner disabled the save path**

## Smart downloads and auto-filled offline shelves compose with play-next risk

`496` covers next-step handoffs while the recording is being watched.
`497` covers what happens **after** the recording has been saved into a later-viewing or offline shelf.
The distinction matters because YouTube’s current Smart Downloads help says recommended videos are automatically added to the viewer’s downloads.
(xref: `youtube_smart_downloads_help_page`)

That means a voter can experience an offline library as though it were one coherent official packet when in fact it may contain:
- one intentionally saved official recording,
- several platform-recommended neighboring videos,
- and no current written recovery lane at all.

So `497` should compose with `496` but stay separate from it:
- `496` asks whether the player silently hands the voter onward,
- `497` asks whether the saved/offline library later turns that handoff residue into a durable seeming official shelf.

## Watch Later and saved-media presence are provenance signals, not authority signals

A video appearing in Watch Later or a saved library says something small but real:
**the viewer or platform preserved access to it for later.**
It does **not** say:
- the office still stands behind it as current guidance,
- the surrounding saved context is reviewed,
- the save date matches the current election window,
- or the platform preserved the office’s intended scope and recovery cues.

Vimeo’s current Watch Later help even says owners can disable Watch Later for public videos.
That is a reminder that the availability of the save surface is itself platform- and owner-shaped, not a durable legal or official-publication guarantee.
(xref: `vimeo_about_watch_later_help_page`)

## High-risk voter questions should bias toward “recheck the live route” before acting

Some topics are especially unsafe to answer from a saved-media library alone:
- polling-place, drop-box, early-voting, or satellite-office locations and hours,
- registration or ballot-status explanations,
- ID rules close to the deadline,
- cure instructions,
- weather/disaster contingencies,
- and any route whose safe next step is really `305` ordinary office/help recovery.

For those topics, `497` does not require the platform save surface to be perfect.
It requires the archive to make sure the saved-media posture points clearly back to the current written route before the voter acts.

## Minimal state taxonomy

Keep at least these states separate:
- **saved to Watch Later only**
- **saved to viewer-managed playlist**
- **saved to office-authored playlist**
- **downloaded for offline use inside platform app**
- **offline item now stale or outside current election window**
- **auto-filled / recommended download present beside official item**
- **save or offline path unavailable / disabled**

The point is not to track every viewer library.
The point is to keep the public explanation honest about which saved-media surfaces existed and which ones the office actually reviewed or intended.

## Bounded saved-media trace minimum

A small public digest should make it possible to reconstruct:
- which recordings were reviewed for Watch Later, playlist, or offline-library behavior,
- whether the save surface was viewer-managed, office-authored, platform-shaped, or mixed,
- whether offline reopening could occur without revisiting the current written help lane,
- whether auto-filled or recommended downloads could sit beside the official item,
- where the current written recovery lane lived,
- and when the route was last verified.

It should **not** require per-viewer account exports, watch history, recommendation dumps, or copies of private playlists.

## Minimal claim-set

1. **Saved-media boundary claim:** Watch Later, playlists, and offline libraries stay subordinate to the current recording and the current written help lane.
2. **Provenance claim:** the office distinguishes viewer-managed saves, office-authored playlists, and platform-shaped auto-filled download shelves.
3. **Freshness claim:** the fact that a saved or offline item still opens does not automatically prove it is current.
4. **Adjacency claim:** mixed playlists or auto-filled download libraries do not inherit the authority of one official saved item.
5. **Recovery claim:** the voter can recover the current official page, FAQ/help entry, or named office lane before acting on time-sensitive guidance discovered from a saved-media surface.

## Canonical digest artifacts

Publish **small digests of saved-media posture**, not private library exports.

- **Saved-Media Surface Digest (SMSD):** digest of routes reviewed for Watch Later, playlist, and offline-library behavior.
- **Saved-Media Provenance Note (SMPN):** optional note identifying which saved-media contexts were viewer-managed, office-authored, platform-shaped, or disabled.
- **Saved-Media Recovery Boundary Note (SMRBN):** optional note identifying how saved-media routes point back to the current written help lane.

## What belongs in the public saved-media payload

Keep the payload **small, route-aware, and explicit about library provenance, offline behavior, and recovery**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `saved_media_surface_label`
- `delivery_role_note`
- `covered_surface_refs[]`
- `official_source_anchors[]`
- `reviewed_saved_media_contexts[]`
- `saved_media_provenance_note`
- `offline_freshness_boundary_note`
- `playlist_and_library_adjacency_note`
- `auto_filled_downloads_note`
- `current_help_recovery_note`
- `latest_notice_uri`
- `last_verified_at`
- `supersedes[]`
- `superseded_by[]`

## References

- YouTube Help — Add & remove videos from Watch later. (xref: `youtube_watch_later_help_page`)
- YouTube Help — Create & manage playlists. (xref: `youtube_create_manage_playlists_help_page`)
- YouTube Help — Watch videos offline on mobile in select countries & regions. (xref: `youtube_watch_videos_offline_mobile_help_page`)
- YouTube Help — YouTube videos offline FAQs. (xref: `youtube_videos_offline_faq_help_page`)
- YouTube Help — Use Smart Downloads with YouTube Premium. (xref: `youtube_smart_downloads_help_page`)
- Vimeo Help Center — About Watch Later. (xref: `vimeo_about_watch_later_help_page`)
- Vimeo Help Center — Viewer features available on the Vimeo app for Android. (xref: `vimeo_viewer_features_android_help_page`)
