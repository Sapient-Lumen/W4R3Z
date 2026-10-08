# 537 — Official voter-information platform media capability-bearing current aliases, link-secret routes, and redaction-default discipline

**Track:** Shared

This document adds one bounded rule to the recent platform-media chain layer:
once `528` has stitched several observations into one same-object media chain, `529` has named the current controlling head, `534` has separated fully public sibling aliases, and `535` has separated audience-scoped routes, **how should the archive record still-current routes whose practical access is carried mainly by possession of the full URL or token-bearing path itself without letting those routes silently become the ordinary-public default?**

This document answers that narrow question.

It composes with:
- `docs/163-artifact-reference-conventions.md`
- `docs/173-canonical-evidence-envelopes-and-packets.md`
- `docs/189-sensitive-material-and-secrets.md`
- `docs/223-public-surface-capture-notes-and-reproducibility.md`
- `docs/225-redaction-logs-and-transformation-accountability.md`
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

## Why this exists (bounded)

Current official platform help already shows that some still-current routes are neither fully public in the ordinary sense nor identity-scoped to a named audience subset.
YouTube says unlisted videos and playlists can be seen and shared by anyone with the link, do not appear in the channel's Videos tab, and do not appear in search results unless someone adds the unlisted video to a public playlist.
Vimeo says unlisted videos can be accessed and shared by anyone who has the video's unique URL, and that when a video is changed to Unlisted a privacy hash is added to the URL and must be included for sharing and embeds to work.
Microsoft says town-hall attendees can receive an emailed recording link after publication, which is a useful contrast because that route is better described as an audience-scoped delivery path under `535` unless the link itself is doing the main access work.
(xref: `youtube_change_video_privacy_settings_help_page`; xref: `vimeo_about_video_privacy_settings_help_page`; xref: `microsoft_attend_town_hall_help_page`)

That means the chain layer needs one compact distinction:
- some co-current aliases are still current for the ordinary public and belong in `534`,
- some current routes stay valid only for a defined audience subset and belong in `535`,
- some routes are best understood as **capability-bearing** because possession of the full path, token, or privacy-hash-bearing URL is what makes them work and they belong here,
- and some chains still have **no public media head at all** and belong in `533`.

Without that distinction, reviewers tend to make one of three mistakes:
- they treat a bearer-style unlisted or privacy-hash route as if it were an ordinary public alias,
- they blur a capability-bearing route into an audience-membership rule even when the main fact is possession of the full link,
- or they reproduce more of the route than the archive needs, turning a classification note into a secret-handling mistake.

This document fixes that bounded ambiguity.
It standardizes one small note for **capability-bearing current aliases + redaction-first recording discipline**.

## This is not the same thing as `511`, `512`, `518`, `533`, `534`, `535`, `536`, or `538`

`511` controls share panels, copy-link UI, timestamp links, and embed-export shells.

`512` controls the first-contact restriction or unavailable shell.

`518` controls registration, invite-only, approval, memberships, and similar audience-selection shells.

`533` covers the bounded case where no ordinary-public media head currently exists.

`534` covers fully public co-current aliases.

`535` covers current routes that remain valid for a defined audience subset.

`536` records later widening, narrowing, and re-bucketing when a route moves between those buckets across time.

`538` covers the nearby but different case where the same object is still being rendered through a direct player-host or embed path and the main question is render-shell classification rather than possession of a secret-bearing path.

`537` is different.
It says that sometimes one same-object chain should keep:
- one ordinary-public head or fallback anchor,
- plus one or more **capability-bearing current aliases** whose practical use depends mainly on possession of the full URL or token-bearing route,
- while recording the route class without silently promoting it into the archive's ordinary-public default.

## Default rule: classify bearer-style routes explicitly and keep them out of the public default

Inside one `528` same-object chain, reviewers MAY keep one ordinary-public canonical head under `529` while also recording one or more **capability-bearing current aliases** when all of the following hold:

1. **The underlying object is still the same.**
   The route still resolves to the same office-controlled event, recording, or published media answer.
2. **The route works mainly because the holder has the full path.**
   Access depends chiefly on possession of the unlisted URL, privacy-hash-bearing URL, or similarly tokenized route rather than on public discoverability.
3. **Treating the route as simply public would mislead.**
   A general reader could mistake a bearer-style route for an ordinary public route that can be rediscovered safely without the full path.
4. **The ordinary public still has a better default anchor or else no public head exists.**
   `526` and `529` can still name the ordinary-public default, or `533` can honestly say there is no ordinary-public media head.
5. **The capability route still matters for reproduction or path-class claims.**
   The archive would lose useful truth if it ignored how the same answer remained reachable through the bearer-style path.

When those conditions hold, record the route as a capability-bearing alias.
Do **not** let easy resharing or possession-based access quietly turn that route into the archive's ordinary-public default.

## Minimal capability-alias grammar

When a same-object chain has a public head or fallback anchor plus a still-current capability-bearing route, reviewers SHOULD prefer one line in this shape:

`chain=<stable object label>; head=<ordinary public current tuple|none>; capability_aliases=<route family>; capability_class=<unlisted_link|privacy_hash_url|tokenized_route|other bounded class>; public_status=<ordinary_public_head|no_public_head>; cite_default=<head|fallback anchor>; cite_capability_when=<path-specific reproduction or route-class claim>; record_secret=<redacted|truncated|nonreproduced>; basis=<why possession of the route matters without making it the public default>`

This is a compact note contract, not a new schema field.
It exists so packet notes can describe bearer-style routes without turning the archive into a capability-link repeater.

## When to use a capability-bearing note

Typical uses include:

1. **Public head plus unlisted convenience route**
   The same answer still has an ordinary-public head, but an unlisted or privacy-hash-bearing route remains current and reproducible for people who already possess it.
2. **Headless public posture plus still-live bearer path**
   No ordinary-public media head should control, but the chain still needs to note that a bearer-style route exists for people who already hold it. In that case pair `537` with `533` rather than pretending the bearer route is an ordinary-public head.
3. **Route-class claim without secret replay**
   The archive needs to explain that the same answer was reachable through a token-bearing path, but the decisive fact is the route class, not the full secret-bearing URL.

## Redaction and citation defaults

By default, later notes SHOULD still cite the ordinary-public head under `530`, or the fallback anchor if the chain is headless under `533`.
A capability-bearing alias SHOULD be cited only when the later claim is specifically about:
- how the bearer-style route class worked,
- how a user who already possessed the route reached the same answer,
- or why the route should not be mistaken for a fully public alias or an identity-scoped audience path.

Reviewers SHOULD record only the minimum route detail needed to preserve reproducibility and classification.
Prefer route labels, redacted forms, truncated suffixes, or other non-full reproductions over copying the full capability-bearing path into ordinary summaries.
Use the archive's existing sensitive-material and redaction controls rather than inventing a new exception here.

## When not to use this

Do **not** use `537` when:
- the route is fully public and current for everyone — use `534`,
- the route stays current only because a named audience subset is admitted or mailed a delivery path — use `535`,
- the main fact is that the path is a player-host or embed-render shell rather than a bearer-style secret route — use `538`,
- the decisive issue is still the current restriction or gating shell — use `512` or `518`,
- the route only matters historically and no longer works now — use `530` historical-leg scoping,
- the main task is to record widening/narrowing between buckets across time — use `536`,
- or the route is just a copy/share UI issue without a same-object chain question — use `511`.

If a bearer-style route is the only route left and no ordinary public media head exists, the chain should normally still be governed by `533` for present-tense public guidance, with `537` only describing the non-default capability path.

## Examples

- `chain=county_board_video_briefing; head=public replay packet; capability_aliases=unlisted direct watch URL; capability_class=unlisted_link; public_status=ordinary_public_head; cite_default=head; cite_capability_when=explaining the bearer-style route seen in evidence capture; record_secret=redacted; basis=the same replay answer remained reachable through an unlisted path, but the public replay packet still controls ordinary guidance`
- `chain=regional_results_stream; head=none; capability_aliases=privacy-hash archive URL family; capability_class=privacy_hash_url; public_status=no_public_head; cite_default=fallback written update page; cite_capability_when=explaining why holders of the hashed route could still reach the archive; record_secret=nonreproduced; basis=no ordinary-public media head remains, so the bearer-style path is real evidence but not the public default`

## Tie-breaker when reviewers ask “if anyone with the link can use it, why isn't it just public?”

Ask three questions:
- can an ordinary user safely rediscover the route without already possessing the full path,
- is the present fact mainly public discoverability or mainly possession of the exact token-bearing URL,
- and would reproducing the full route add more operational risk than evidentiary value?

If the answer points to possession of the full path, keep the public/default classification separate and use `537`.
Do **not** let “reshareable” automatically collapse into “ordinary public.”

## Promotion rule

Future media additions should usually **not** be promoted just because a same-object chain has a bearer-style unlisted or privacy-hash route alongside a public head or a fallback anchor.
Tighten `537` first.
Only add another numbered surface when the ambiguity is really about a new gate object, a new restriction shell, or a new portability/export boundary rather than about **capability-bearing route classification inside an already-known chain**.

## Minimal artifact

This document is intentionally doc-only.
Do **not** add a checklist or payload template for it unless the archive later proves that bearer-style current routes still drift between `511`, `533`, `534`, `535`, and `536` after this compact note contract exists.
