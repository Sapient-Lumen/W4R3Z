# 543 — Official voter-information platform media remembered-resume aliases, history re-entry, and full-object-default discipline

**Track:** Shared

This document gives the recent platform-media chain layer one more compact rule.

It exists because the archive already knows how to separate:
- the underlying media object itself (`369` and `528–529`),
- explicit `Start at` / current-time entrypoint routes (`539`),
- reminder or email carriers (`540–541`),
- and installed-app launch/container shifts (`542`).

A smaller ambiguity still remains:
**what should the archive do when the same media object comes back through platform memory of prior viewing — watch history, a Continue Watching row, a recent-videos card, or remembered progress — and that re-entry path starts to look like the controlling current route even though the office did not publish a new route at all?**

This document answers that narrow question.

It composes with:
- `docs/163-artifact-reference-conventions.md`
- `docs/173-canonical-evidence-envelopes-and-packets.md`
- `docs/223-public-surface-capture-notes-and-reproducibility.md`
- `docs/369-official-voter-information-videos-livestreams-and-clip-context-discipline.md`
- `docs/506-official-voter-information-platform-watch-history-continue-watching-recent-videos-and-resume-state-authority-boundary-discipline.md`
- `docs/523-official-voter-information-platform-media-boundary-quickmap-and-duplicate-firewall.md`
- `docs/528-official-voter-information-platform-media-same-object-transition-chains-packet-stitching-and-resnapshot-threshold-discipline.md`
- `docs/529-official-voter-information-platform-media-chain-heads-current-control-and-closeout-discipline.md`
- `docs/530-official-voter-information-platform-media-chain-citations-head-first-reference-and-historical-leg-scoping-discipline.md`
- `docs/533-official-voter-information-platform-media-no-public-head-states-headless-chain-notes-and-fallback-anchor-discipline.md`
- `docs/539-official-voter-information-platform-media-entrypoint-offset-aliases-current-time-start-at-routes-and-full-object-default-discipline.md`
- `docs/542-official-voter-information-platform-media-app-launch-aliases-open-in-app-deep-links-and-browser-default-retention-discipline.md`
- `docs/544-official-voter-information-platform-media-in-player-moment-jump-aliases-transcript-chapter-picks-and-route-stability-retention-discipline.md`

## Why this exists (bounded)

Current platform help already shows that a same-object media path can come back through **remembered progress or history-shaped re-entry** without minting a new publication route.
YouTube says the video progress bar shows where the viewer left off and that a partially watched video will usually restart from where the viewer was.
Vimeo says the Continue Watching row lets viewers resume a previously started video exactly where they left off, that it appears on web, mobile, and TV apps, and that it follows the same account across devices.
Microsoft says the Clipchamp homepage in Microsoft 365 helps people find videos and Teams meeting recordings and quickly pick up where they left off.
(xref: `youtube_video_progress_bar_help_page`; xref: `vimeo_continue_watching_row_help_page`; xref: `microsoft_clipchamp_video_capabilities_help_page`)

That means one same-object chain can truthfully contain all of the following at once:
- one current controlling head,
- one history- or continue-watching re-entry surface that really existed,
- one remembered resume position that really affected what the viewer saw next,
- and no new office-published route at all.

Without a compact rule here, reviewers tend to make one of four mistakes:
- they treat remembered resume state as if the office intentionally published a new current route,
- they collapse remembered re-entry into `539` even though no explicit offset alias was shared or encoded in the URL,
- they let a history card or Continue Watching row quietly become the citation-safe present-tense default,
- or they restate the whole issue as generic platform history behavior even though the important truth is **how the same object was reopened and what remembered position or re-entry wrapper shaped first view on return**.

This document fixes that bounded ambiguity.
It standardizes one small note for **remembered-resume aliases + full-object-default discipline** inside a same-object media chain.

## This is not the same thing as `506`, `539`, `542`, `496`, or `497`

`506` says watch history, Continue Watching, recents, and resume-state are a bounded **surface family** that must stay subordinate to the current written/help lane.

`539` says how to record an explicit same-object `Start at` / current-time route whose landing point is encoded in the route itself.

`542` says how to record that the same object launched through an installed app, open-in-app prompt, universal link, or other app-preferred handoff.

`544` says how to record transcript clicks, chapter picks, and other player-internal moment selections when the same object stays current without an explicit offset route.

`496` says how autoplay, end screens, cards, and play-next surfaces can push the viewer onward into another item.

`497` says how saved shelves, Watch Later, playlists, and offline libraries keep already-open media around for later.

`543` is different.
It says that once `506` has already identified the history/resume surface and `528–529` have already identified the same-object chain and current head, reviewers sometimes still need one bounded note saying:
- which same object came back through remembered viewing state,
- whether the re-entry landed at a remembered or platform-selected position,
- and that **remembered progress or history memory alone does not create a new head, an explicit offset alias, or a safer public default than the current head**.

If the decisive issue is the history/Continue Watching surface itself as a first-contact public-answer lane, use `506`.
If the decisive issue is an explicit `Start at` or current-time URL, use `539`.
If the decisive issue is that the same object launched in-app or through an app-preferred container, use `542`.
Use `543` only when the history/resume surface is already understood but the archive still needs to classify the **same-object remembered re-entry path** inside an already-governed media chain.

## Default rule: preserve remembered re-entry truth, but let control stay with the head

Inside one `528` same-object chain, reviewers MAY keep a compact **remembered-resume alias note** when all of the following hold:

1. **The underlying object is still the same.**
   The reopened route still resolves to the same office-controlled event, recording, or published media answer.
2. **The practical difference is remembered re-entry, not a new route publication.**
   The decisive fact is that history, Continue Watching, recents, or remembered progress changed how the viewer came back to the object.
3. **Treating the re-entry path as just another public alias would mislead.**
   A reader could mistake a history card or remembered resume point for the archive's citation-safe ordinary-public default.
4. **A better present-tense default still exists or the chain is honestly headless.**
   `529` and `530` can still name the current head, or `533` can honestly say no public media head exists and point to the best fallback anchor instead.
5. **The remembered re-entry fact still matters.**
   The archive would lose useful truth if it omitted how the same object resurfaced, which re-entry wrapper was involved, or whether the viewer skipped past the opening context because of remembered progress.

When those conditions hold, keep the head/default under `529–530`, keep any explicit encoded offset under `539`, keep any app/container rule under `542`, and add one `543` remembered-resume note.
Do **not** silently promote the history/re-entry path into the chain's current head.

## Minimal remembered-resume grammar

When a same-object chain has a current head or fallback anchor plus a meaningful memory-shaped re-entry path, reviewers SHOULD prefer one line in this shape:

`chain=<stable object label>; head=<current tuple|none>; resume_aliases=<route family>; resume_class=<history_reopen|continue_watching_row|recent_videos_card|remembered_progress_resume|cross_device_resume>; resume_position=<remembered_offset|row_reentry_no_offset|platform_selected>; cite_default=<head|fallback anchor>; cite_resume_when=<reentry-path, skipped-context, or remembered-position claim>; promote_resume=<no>; basis=<why the memory-shaped return mattered without becoming the public default>`

This is a compact note contract, not a new schema field.
It exists so packet notes can preserve **how the same object came back** without making every history card, Continue Watching row, or remembered resume point sound like a fresh route publication or a safer citation target than the head.

## When to use a remembered-resume note

Typical uses include:

1. **Same public recording reopened from remembered progress**
   The current head still controls, but the reopened experience matters because the viewer returned near the previously watched point and skipped the opening context.
2. **Cross-device Continue Watching return to the same object**
   The same object is reopened through a platform memory row on another device, but that row should not replace the browser/public default in the chain.
3. **Recent-videos or homepage re-entry card for the same object**
   The resurfaced card matters for reproduction or first-view-on-return claims, but the card does not become the archive's present-tense control object.
4. **Resume-state intertwined with app launch, explicit offset, or player-internal jump**
   The archive may need both `543` and `542`, both `543` and `539`, or both `543` and `544`, when a memory-shaped return also launched the object in-app, also preserved an explicit offset route, or also immediately jumped within the player to a selected section. Keep those facts separate instead of letting one compact note absorb the others.

## Citation rule

By default, later notes SHOULD still cite the **current controlling head** under `530`, or the fallback anchor if the chain is headless under `533`.
A `543` remembered-resume alias SHOULD be cited only when the later claim is specifically about:
- how the viewer came back through history, Continue Watching, recents, or remembered progress,
- whether remembered progress skipped past a caveat, date cue, or correction context,
- whether the same object resurfaced across devices through platform memory,
- or why the archive refused to let a memory-shaped re-entry path outrank the head-first citation rule.

That means `543` preserves one honest remembered-reentry exception to head-first citation without letting watch-history, Continue Watching, or resume-state memory quietly become the archive's present-tense authority object.

## When not to use this

Do **not** use `543` when:
- the decisive issue is the history/Continue Watching surface itself as a bounded public-answer lane — use `506`,
- the decisive issue is an explicit encoded `Start at` / current-time route — use `539`,
- the decisive issue is a clip/highlight/excerpt surface — use `495`,
- the decisive issue is autoplay, play-next, or another onward handoff into a different item — use `496`,
- the decisive issue is a saved shelf, playlist, or offline library — use `497`,
- the decisive issue is that the same object launched in-app or through an app-preferred container — use `542`,
- the decisive issue is that the same object stayed current but the viewer immediately selected a transcript/chapter/table-of-contents jump rather than resuming through memory — use `544`,
- or the archive is trying to preserve individualized watch-history exhaust, account analytics, or fine-grained behavioral telemetry.

If deleting the remembered-reentry fact would erase **how the same object was reopened or why the viewer resumed partway through**, `543` is probably the right companion.
If deleting the remembered-reentry fact would erase the whole route or publication story, the problem probably belongs elsewhere.

## Examples

- `chain=county_board_deadline_explainer_mar_2026; head=public YouTube watch-page packet; resume_aliases=YouTube progress-bar reopen on signed-in devices; resume_class=remembered_progress_resume; resume_position=remembered_offset; cite_default=head; cite_resume_when=proving that return viewing skipped the opening deadline caveat; promote_resume=no; basis=the same public answer came back partway through, but the watch page remained the archive's citation-safe default`
- `chain=regional_town_hall_replay_mar_2026; head=public Vimeo replay packet; resume_aliases=Vimeo OTT Continue Watching row across web/mobile/TV; resume_class=cross_device_resume; resume_position=remembered_offset; cite_default=head; cite_resume_when=proving that the same replay resurfaced on a TV app after prior mobile viewing; promote_resume=no; basis=the platform memory row changed how the same replay returned without publishing a new route`
- `chain=city_clerk_recording_apr_2026; head=published Microsoft 365 recording packet; resume_aliases=Clipchamp homepage recent-video re-entry; resume_class=recent_videos_card; resume_position=platform_selected; cite_default=head; cite_resume_when=proving that the recording was reopened through Microsoft 365's remembered recent-video surface; promote_resume=no; basis=the recent-card return path mattered for reproduction, not for present-tense route control`

## Tie-breaker when reviewers ask “if people actually came back through Continue Watching, why isn't that the head?”

Ask three questions:
- does the memory-shaped re-entry prove **how the same object returned** rather than **what the archive says controls for the ordinary public now**,
- would a head-first summary become less accurate if it defaulted to the history/resume surface,
- and is the missing fact really the remembered re-entry path rather than an explicit offset route, a saved shelf, an app-launch handoff, or a new onward object?

If yes, keep current control under `529–530`, preserve any explicit offset or app/container fact under `539` or `542`, preserve any player-internal jump under `544`, and record the memory-shaped return under `543`.
Do **not** let the remembered-resume path absorb chain control.

## Promotion rule

Future media additions should usually **not** be promoted just because the same object resurfaced through watch history, Continue Watching, recents, or remembered progress.
Tighten `543` first.
Only add another numbered surface when the ambiguity is really about a new route class, a new carrier class, or a new control object rather than about **memory-shaped re-entry inside an already-governed same-object media chain**.

## Minimal artifact

This document is intentionally doc-only.
Do **not** add a checklist or payload template for it unless the archive later proves that remembered-resume cases still drift between `506`, `539`, `542`, and `544` after this compact note contract exists.
