# 539 — Official voter-information platform media entrypoint-offset aliases, current-time/start-at routes, and full-object-default discipline

**Track:** Shared

This document adds one bounded rule to the recent `523–538` platform-media chain layer:
once `528` has stitched several observations into one same-object media chain, `529` has named the current controlling head, `534` has separated fully public sibling aliases, `535` has separated audience-scoped routes, `537` has separated capability-bearing paths, and `538` has separated player-host render shells, **how should the archive record still-current links that land at a specific moment inside the same recording without letting those entrypoint offsets quietly become a new current head, a disguised clip, or the ordinary-public default?**

This document answers that narrow question.

It composes with:
- `docs/163-artifact-reference-conventions.md`
- `docs/173-canonical-evidence-envelopes-and-packets.md`
- `docs/223-public-surface-capture-notes-and-reproducibility.md`
- `docs/369-official-voter-information-videos-livestreams-and-clip-context-discipline.md`
- `docs/495-official-voter-information-platform-clips-highlights-and-shareable-segment-authority-boundary-discipline.md`
- `docs/511-official-voter-information-platform-share-panels-copy-links-timestamp-links-and-embed-export-authority-boundary-discipline.md`
- `docs/523-official-voter-information-platform-media-boundary-quickmap-and-duplicate-firewall.md`
- `docs/528-official-voter-information-platform-media-same-object-transition-chains-packet-stitching-and-resnapshot-threshold-discipline.md`
- `docs/529-official-voter-information-platform-media-chain-heads-current-control-and-closeout-discipline.md`
- `docs/530-official-voter-information-platform-media-chain-citations-head-first-reference-and-historical-leg-scoping-discipline.md`
- `docs/533-official-voter-information-platform-media-no-public-head-states-headless-chain-notes-and-fallback-anchor-discipline.md`
- `docs/534-official-voter-information-platform-media-co-current-aliases-sibling-routes-and-canonical-head-with-alias-discipline.md`
- `docs/535-official-voter-information-platform-media-audience-scoped-current-aliases-scope-labels-and-public-default-retention-discipline.md`
- `docs/537-official-voter-information-platform-media-capability-bearing-current-aliases-link-secret-routes-and-redaction-default-discipline.md`
- `docs/538-official-voter-information-platform-media-player-host-render-aliases-direct-embed-routes-and-watch-page-default-discipline.md`
- `docs/540-official-voter-information-platform-media-notification-carriers-reminder-pointers-and-route-carrier-separation-discipline.md`

## Why this exists (bounded)

Current official platform help already shows that some still-current routes are best understood as **entrypoint-offset aliases** rather than as separate clips, separate public heads, or generic public aliases.
YouTube says the Share panel can create a `Start at` link for a chosen moment in the same video.
Vimeo says a shared URL can begin at a specific time and that a start-and-end segment link still lets the recipient switch to watching the full video.
Microsoft says a video or audio file can be shared with `Copy link at current time`, which creates a link to the current time in the same file.
(xref: `youtube_share_videos_channels_help_page`; xref: `vimeo_share_video_segment_help_page`; xref: `microsoft_share_video_audio_m365_help_page`)

That means the chain layer needs one compact distinction:
- some portable routes are really **new excerpt or clip-like surfaces** and belong in `495`,
- some routes mainly reflect the **share/export boundary** that generated them and belong in `511`,
- some routes remain the same current object but only differ by an **entrypoint offset** and belong here,
- some surfaces merely **carry** an offset or full-object link to the recipient and belong in `540`,
- some routes remain fully public aliases and belong in `534`,
- some routes remain audience-scoped and belong in `535`,
- some routes mainly work because the holder has the full bearer-style path and belong in `537`,
- and some routes mainly differ because they are rendered through a player host or embed shell and belong in `538`.

Without that distinction, reviewers tend to make one of three mistakes:
- they treat a `Start at` or current-time link as if it were a separate current head,
- they treat a same-object offset link as if it were a true clip/highlight surface,
- or they let one quoted moment silently replace the full-object default for present-tense public guidance.

This document fixes that bounded ambiguity.
It standardizes one small note for **same-object offset aliases + full-object-default discipline**.

## This is not the same thing as `495`, `511`, `534`, `535`, `537`, `538`, or `369`

`495` controls **portable clips, highlights, and shareable excerpt surfaces** that behave like a bounded mini-publication.

`511` controls the **share/export boundary** that generated a copied link, current-time link, or similar portable handoff.

`534` covers fully public co-current aliases.

`535` covers current routes that remain valid for a defined audience subset.

`537` covers routes that mainly work because the holder possesses the full unlisted, privacy-hash-bearing, or other token-bearing path.

`538` covers routes whose decisive difference is that they are played through a direct player-host or embed-render shell.

`369` still governs the underlying recording, livestream, or published media object itself.

`539` is different.
It says that sometimes one same-object chain should keep:
- one full-object current head or fallback anchor,
- plus one or more **entrypoint-offset aliases** such as `Start at` / current-time routes,
- while recording that those routes change where playback begins rather than replacing the full-object default.

## Default rule: classify offset aliases explicitly and keep the full object as the public default

Inside one `528` same-object chain, reviewers MAY keep one full-object canonical head under `529` while also recording one or more **entrypoint-offset aliases** when all of the following hold:

1. **The underlying object is still the same.**
   The route still resolves to the same office-controlled event, recording, or published media answer.
2. **The main difference is the landing point, not the object.**
   The route changes where the viewer enters the media rather than minting a distinct clip or replacing the current public route.
3. **Treating the route as a full new surface would mislead.**
   A reader could mistake an offset link for a new controlling answer, a new clip, or a co-equal public default.
4. **The full object remains recoverable.**
   The archive can still name the full-object head under `529`, or the fallback anchor under `533` if the chain is headless.
5. **The offset still matters for reproduction or quoted-moment claims.**
   The archive would lose useful truth if it ignored that the viewer landed at a specific moment.

When those conditions hold, record the route as an offset alias.
Do **not** let a same-object `Start at` / current-time route silently promote one moment into the archive's ordinary-public default.

## Minimal offset-alias grammar

When a same-object chain has a full-object head or fallback anchor plus a still-current offset route, reviewers SHOULD prefer one line in this shape:

`chain=<stable object label>; head=<full-object current tuple|none>; offset_aliases=<route family>; offset_mode=<start_only|current_time|bounded_segment>; route_scope=<ordinary_public_offset|scoped_offset|capability_offset|render_offset>; object_default=<full_object>; cite_default=<head|fallback anchor>; cite_offset_when=<arrival-path reproduction or quoted-moment claim>; promote_offset=<no>; basis=<why the offset matters without replacing the full-object default>`

This is a compact note contract, not a new schema field.
It exists so packet notes can preserve same-object offset behavior without making every start-at/current-time link sound like a new portable publication.

## When to use an offset-alias note

Typical uses include:

1. **Same public recording, different arrival point**
   The same full-object head still controls now, but a copied `Start at` or current-time route matters because many viewers are likely to land midstream.
2. **Offset route with scoped or capability-bearing access**
   The route still matters because viewers encountered the same object through a moment-specific link, but the access bucket still belongs to `535` or `537`; this document adds the offset fact without collapsing it into those buckets.
3. **Bounded segment link that still preserves same-object recovery**
   A start-and-end route may still matter as an offset-style arrival path when the decisive point is that the recipient can still switch back to the same full object and the archive is not treating the segment as a standalone mini-publication. If the excerpt itself is the real portable answer surface, use `495` instead.

## Citation defaults

By default, later notes SHOULD still cite the full-object head under `530`, or the fallback anchor if the chain is headless under `533`.
An offset alias SHOULD be cited only when the later claim is specifically about:
- how the viewer arrived at a particular moment,
- how a quoted or reproduced claim depended on the playback starting point,
- or why the archive refused to treat an offset route like a new head or clip.

If the offset route is also audience-scoped, capability-bearing, or render-shell-specific, keep that bucket explicit with `535`, `537`, or `538` instead of letting `539` swallow the access or rendering rule.

## When not to use this

Do **not** use `539` when:
- the route is really a clip, highlight, or standalone segment surface — use `495`,
- the main task is to govern how the link was copied/exported in the first place — use `511`,
- the route is simply a full co-current public alias — use `534`,
- the route stays current only for a defined audience subset — use `535`,
- the route mainly works because the holder possesses the full bearer-style path — use `537`,
- the route mainly differs because it is rendered through a player-host or embed shell — use `538`,
- the route only matters historically and no longer works now — use `530` historical-leg scoping,
- or the main task is to decide whether several observations belong to the same chain at all — use `528`.

If no ordinary-public media head exists, the chain should normally still be governed by `533` for present-tense public guidance, with `539` only describing the still-relevant offset route inside that headless posture.

## Examples

- `chain=county_results_briefing; head=public replay page; offset_aliases=youtube start-at route; offset_mode=start_only; route_scope=ordinary_public_offset; object_default=full_object; cite_default=head; cite_offset_when=explaining that many viewers landed on the quoted certification moment; promote_offset=no; basis=the same replay answer still controls, but the link begins at a later point inside the full recording`
- `chain=city_budget_town_hall_recording; head=attendee recording page; offset_aliases=m365 copy-link-at-current-time route; offset_mode=current_time; route_scope=scoped_offset; object_default=full_object; cite_default=head; cite_offset_when=showing how attendees were dropped directly into the question-answer segment; promote_offset=no; basis=the same attendee recording still controls, but the copied link changes the entrypoint rather than the underlying object`

## Tie-breaker when reviewers ask “if the link opens on that moment, why isn’t it just a clip?”

Ask three questions:
- does the route still preserve recovery to the same full object,
- is the main difference the landing point rather than a separately treated excerpt surface,
- and is the claim really about how the viewer entered the same answer rather than about a mini-publication that now travels on its own?

If the answer points to a same-object landing point, use `539` and keep the default citation anchored to the full object.
If the answer points to a portable excerpt that behaves like its own publication surface, use `495`.

## Promotion rule

Future media additions should usually **not** be promoted just because the same official recording can also be reached by `Start at`, current-time, or similar same-object offset links.
Tighten `539` first.
Only add another numbered surface when the ambiguity is really about a new excerpt object, a new share/export boundary, or a new wrapper family rather than about **entrypoint-offset classification inside an already-known chain**.

## Minimal artifact

This document is intentionally doc-only.
Do **not** add a checklist or payload template for it unless the archive later proves that same-object offset routes still drift between `495`, `511`, `534`, `535`, `537`, and `538` after this compact note contract exists.
