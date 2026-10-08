# 538 — Official voter-information platform media player-host render aliases, direct-embed routes, and watch-page-default discipline

**Track:** Shared

This document adds one bounded rule to the recent platform-media chain layer:
once `528` has stitched several observations into one same-object media chain, `529` has named the current controlling head, `534` has separated fully public sibling aliases, `535` has separated audience-scoped routes, and `537` has separated capability-bearing paths, **how should the archive record still-current routes that exist mainly as direct player-host or embed-render shells without letting those render paths silently become the ordinary-public default?**

This document answers that narrow question.

It composes with:
- `docs/163-artifact-reference-conventions.md`
- `docs/173-canonical-evidence-envelopes-and-packets.md`
- `docs/223-public-surface-capture-notes-and-reproducibility.md`
- `docs/369-official-voter-information-videos-livestreams-and-clip-context-discipline.md`
- `docs/511-official-voter-information-platform-share-panels-copy-links-timestamp-links-and-embed-export-authority-boundary-discipline.md`
- `docs/512-official-voter-information-platform-unavailable-private-age-gated-region-blocked-and-playback-restricted-surface-authority-boundary-discipline.md`
- `docs/518-official-voter-information-platform-registration-forms-invite-only-join-links-and-audience-gated-media-authority-boundary-discipline.md`
- `docs/523-official-voter-information-platform-media-boundary-quickmap-and-duplicate-firewall.md`
- `docs/526-official-voter-information-platform-media-re-anchor-ladder-canonical-recovery-targets-and-wrapper-exit-discipline.md`
- `docs/528-official-voter-information-platform-media-same-object-transition-chains-packet-stitching-and-resnapshot-threshold-discipline.md`
- `docs/529-official-voter-information-platform-media-chain-heads-current-control-and-closeout-discipline.md`
- `docs/530-official-voter-information-platform-media-chain-citations-head-first-reference-and-historical-leg-scoping-discipline.md`
- `docs/533-official-voter-information-platform-media-no-public-head-states-headless-chain-notes-and-fallback-anchor-discipline.md`
- `docs/534-official-voter-information-platform-media-co-current-aliases-sibling-routes-and-canonical-head-with-alias-discipline.md`
- `docs/535-official-voter-information-platform-media-audience-scoped-current-aliases-scope-labels-and-public-default-retention-discipline.md`
- `docs/536-official-voter-information-platform-media-route-scope-transitions-widening-narrowing-and-alias-rebucketing-discipline.md`
- `docs/537-official-voter-information-platform-media-capability-bearing-current-aliases-link-secret-routes-and-redaction-default-discipline.md`
- `docs/539-official-voter-information-platform-media-entrypoint-offset-aliases-current-time-start-at-routes-and-full-object-default-discipline.md`
- `docs/585-official-voter-information-platform-media-authenticity-cue-transport-cross-route-divergence-and-absence-non-inference-firewall.md`

## Why this exists (bounded)

Current official platform help already shows that some still-current routes are best understood as **player-host or embed-render shells** rather than as ordinary watch pages, public sibling aliases, or secret-bearing routes.
YouTube says embedding generates HTML code for the YouTube embedded player, that Privacy Enhanced Mode changes the embed domain to `youtube-nocookie.com`, and that some age-restricted videos redirect viewers back to YouTube when played from most third-party websites.
Vimeo says the Share flow can generate embed code, that later changes apply automatically to the embedded player, and its player-parameter help shows direct `player.vimeo.com/video/...` render paths inside embed code.
Microsoft says video and audio files can be shared through embed code and that viewers with access permissions can view them through the embedded experience.
(xref: `youtube_embed_videos_playlists_help_page`; xref: `vimeo_embed_my_video_help_page`; xref: `vimeo_autoplay_loop_embed_code_help_page`; xref: `microsoft_share_video_audio_m365_help_page`)

That means the chain layer needs one compact distinction:
- some co-current routes are ordinary public aliases and belong in `534`,
- some routes remain current only for a defined audience subset and belong in `535`,
- some routes work mainly because the holder has the full token-bearing path and belong in `537`,
- some chains have no public media head and belong in `533`,
- and some routes are still-current **render shells** whose main function is to play the same object through a player host or embed path and they belong here.

Without that distinction, reviewers tend to make one of three mistakes:
- they treat a direct embed/player-host route as if it were an ordinary public watch-page alias,
- they mistake a render shell for a new current head just because the same media is still reachable there,
- or they let path-specific player behavior dominate ordinary-public guidance when the watch page or fallback anchor should still control.

This document fixes that bounded ambiguity.
It standardizes one small note for **render-only current aliases + watch-page-default discipline**.

## This is not the same thing as `511`, `512`, `518`, `533`, `534`, `535`, `537`, or `369`

`511` controls the **share/export boundary** that generated or carried an embed wrapper out of the source page.

`512` controls the first-contact restriction or unavailable shell when playback is denied, blocked, or redirected into an access warning.

`518` controls registration, invite-only, approval, membership, and similar audience-selection shells.

`533` covers the bounded case where no ordinary-public media head currently exists.

`534` covers fully public co-current aliases.

`535` covers current routes that remain valid for a defined audience subset.

`537` covers routes that mainly work because the holder possesses the full unlisted, privacy-hash-bearing, or other token-bearing path.

`369` still governs the underlying recording, livestream, or published media object itself.

`539` covers the nearby but different case where the same current object is reached through a `Start at`, current-time, or other landing-point offset and the real question is full-object-default discipline rather than render-shell classification.

`542` covers the nearby but different case where the same current object launches through an installed app, open-in-app prompt, or other app-preferred deep-link handoff and the real question is app-container classification rather than direct player-host rendering.

If the distinct problem is that **the render shell kept the same object but authenticity-adjacent cues were preserved, suppressed, or restated differently between the watch page and the render path and reviewers started treating that cue transport drift like proof that the object itself changed**, use `585`.

`538` is different.
It says that sometimes one same-object chain should keep:
- one ordinary-public head or fallback anchor,
- plus one or more **player-host render aliases** such as a direct embed/player path,
- while recording that those paths exist mainly to render the same object in an embedded or player-host experience rather than to replace the ordinary-public default.

## Default rule: classify render paths explicitly and keep them out of the ordinary-public default

Inside one `528` same-object chain, reviewers MAY keep one ordinary-public canonical head under `529` while also recording one or more **player-host render aliases** when all of the following hold:

1. **The underlying object is still the same.**
   The route still resolves to the same office-controlled event, recording, or published media answer.
2. **The route exists mainly as a render shell.**
   The path is chiefly a player-host or embed-render route rather than the ordinary watch-page or office-default route.
3. **Treating the route as just another public alias would mislead.**
   A reader could mistake the render shell for the same kind of public recovery target as the watch page, replay page, or written fallback anchor.
4. **The ordinary public still has a better default anchor or else no public head exists.**
   `526` and `529` can still name the ordinary-public default, or `533` can honestly say there is no ordinary-public media head.
5. **The render path still matters for reproduction or host-path claims.**
   The archive would lose useful truth if it ignored how the same answer appeared through the player-host or embed-render route.

When those conditions hold, record the route as a render alias.
Do **not** let direct playback through the player host silently promote that path into the archive's ordinary-public default.

## Minimal render-alias grammar

When a same-object chain has a public head or fallback anchor plus a still-current render path, reviewers SHOULD prefer one line in this shape:

`chain=<stable object label>; head=<ordinary public current tuple|none>; render_aliases=<route family>; render_host=<youtube_embed|youtube_nocookie|player_vimeo|clipchamp_embed|other bounded class>; route_scope=<ordinary_public_render|scoped_render|capability_render>; cite_default=<head|fallback anchor>; cite_render_when=<host-path reproduction or embed-specific claim>; promote_render=<no>; basis=<why the render shell matters without becoming the public default>`

This is a compact note contract, not a new schema field.
It exists so packet notes can preserve direct player-host evidence without making every embed path sound like a co-equal watch page.

## When to use a render-alias note

Typical uses include:

1. **Public watch page plus direct player-host render path**
   The same answer still has an ordinary-public head, but a direct embed/player-host route remains current and reproducible for path-specific testing or evidence capture.
2. **Render shell with scoped or capability-bearing access**
   The route still matters because viewers encountered the object through an embedded/player-host path, but the scope question still belongs to `535` or `537`; this document adds the render-path fact without collapsing it into either bucket.
3. **Host-path claim without promoting the path**
   The archive needs to explain that a player-host or nocookie render route displayed the same answer, but the decisive fact is the render-shell class, not that the path replaced the ordinary-public head.

## Citation defaults

By default, later notes SHOULD still cite the ordinary-public head under `530`, or the fallback anchor if the chain is headless under `533`.
A render alias SHOULD be cited only when the later claim is specifically about:
- how the object behaved through the embedded/player-host path,
- how the viewer encountered the same answer through a direct render shell,
- or why the render path should not be mistaken for an ordinary public alias, a subset-delivery path, or a capability-bearing secret route.

If the render path is also audience-scoped or capability-bearing, keep that bucket explicit with `535` or `537` instead of letting `538` swallow the access rule.

## When not to use this

Do **not** use `538` when:
- the route is simply the ordinary public head or a truly co-current public alias — use `529` or `534`,
- the route mainly matters because it was copied, exported, or embedded outward — use `511`,
- the route stays current only because a defined audience subset is admitted — use `535`,
- the route mainly works because the holder possesses the full bearer-style path — use `537`,
- the decisive issue is that playback is blocked, redirected, or unavailable — use `512`,
- the route only matters historically and no longer works now — use `530` historical-leg scoping,
- or the main task is to record widening/narrowing between buckets across time — use `536`.

If no ordinary-public media head exists, the chain should normally still be governed by `533` for present-tense public guidance, with `538` only describing the still-relevant render shell.

## Examples

- `chain=county_board_results_stream; head=public replay page; render_aliases=youtube-nocookie embed route; render_host=youtube_nocookie; route_scope=ordinary_public_render; cite_default=head; cite_render_when=explaining the behavior of the embedded render shell seen in evidence capture; promote_render=no; basis=the same replay answer was viewable through the privacy-enhanced embedded player, but the replay page still controls ordinary-public recovery`
- `chain=regional_town_hall_recording; head=attendee post-event recording page; render_aliases=third-party Clipchamp embed route; render_host=clipchamp_embed; route_scope=scoped_render; cite_default=head; cite_render_when=explaining how the same attendee-visible recording appeared in an embedded player path; promote_render=no; basis=the render shell matters for reproduction, but the current route remains scope-bound rather than an ordinary-public alias`

## Tie-breaker when reviewers ask “if the same thing plays there, why isn’t it just another public alias?”

Ask three questions:
- is the path mainly the ordinary watch-page/replay route or mainly a player-host/render shell,
- would an ordinary reader know to recover the official answer through that player-host path rather than the watch page or fallback anchor,
- and is the claim really about the same answer being embedded/rendered, rather than about a new public default route?

If the answer points to a render shell, use `538` and keep the default citation anchored elsewhere.

## Promotion rule

Future media additions should usually **not** be promoted just because the same object was also reachable through a direct embed/player-host route.
Tighten `538` first.
Only add another numbered surface when the ambiguity is really about a new gate object, a new restriction shell, or a new portability/export boundary rather than about **player-host render-path classification inside an already-known chain**.

## Minimal artifact

This document is intentionally doc-only.
Do **not** add a checklist or payload template for it unless the archive later proves that direct embed/player-host routes still drift between `511`, `533`, `534`, `535`, and `537` after this compact note contract exists.
