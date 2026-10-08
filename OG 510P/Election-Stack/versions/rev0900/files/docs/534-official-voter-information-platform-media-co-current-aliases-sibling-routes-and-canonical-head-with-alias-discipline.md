# 534 — Official voter-information platform media co-current aliases, sibling routes, and canonical-head-with-alias discipline

**Track:** Shared

This document adds one bounded rule to the recent platform-media chain layer:
once `528` has stitched several observations into one same-object media chain, `529` has named the current controlling head, and `530` has told later notes to cite that head by default, **how should the archive record cases where more than one public route is simultaneously valid for that same current answer without mistaking those sibling routes for supersession or historical-leg drift?**

This document answers that narrow question.

It composes with:
- `docs/163-artifact-reference-conventions.md`
- `docs/173-canonical-evidence-envelopes-and-packets.md`
- `docs/206-digest-cards-and-low-bandwidth-publication.md`
- `docs/223-public-surface-capture-notes-and-reproducibility.md`
- `docs/369-official-voter-information-videos-livestreams-and-clip-context-discipline.md`
- `docs/517-official-voter-information-platform-simulcast-mirrors-multi-route-live-events-and-redirect-chain-authority-boundary-discipline.md`
- `docs/523-official-voter-information-platform-media-boundary-quickmap-and-duplicate-firewall.md`
- `docs/526-official-voter-information-platform-media-re-anchor-ladder-canonical-recovery-targets-and-wrapper-exit-discipline.md`
- `docs/527-official-voter-information-platform-media-control-tuple-one-line-normalization-contract-and-packet-comparison-discipline.md`
- `docs/528-official-voter-information-platform-media-same-object-transition-chains-packet-stitching-and-resnapshot-threshold-discipline.md`
- `docs/529-official-voter-information-platform-media-chain-heads-current-control-and-closeout-discipline.md`
- `docs/530-official-voter-information-platform-media-chain-citations-head-first-reference-and-historical-leg-scoping-discipline.md`
- `docs/531-official-voter-information-platform-media-head-supersession-notes-trigger-codes-and-demotion-discipline.md`
- `docs/533-official-voter-information-platform-media-no-public-head-states-headless-chain-notes-and-fallback-anchor-discipline.md`
- `docs/535-official-voter-information-platform-media-audience-scoped-current-aliases-scope-labels-and-public-default-retention-discipline.md`
- `docs/536-official-voter-information-platform-media-route-scope-transitions-widening-narrowing-and-alias-rebucketing-discipline.md`
- `docs/537-official-voter-information-platform-media-capability-bearing-current-aliases-link-secret-routes-and-redaction-default-discipline.md`

## Why this exists (bounded)

Current official platform help already shows that one office-controlled media answer can remain reachable through more than one lawful public route at the same time.
Vimeo says viewers of a recurring event can watch past streams from the event page inside the event player, while each archived live event also has its own unique video URL after the stream ends.
(xref: `vimeo_watch_past_streams_recurring_event_help_page`; xref: `vimeo_share_archived_live_event_help_page`)

That means a same-object chain can sometimes have:
- one **current controlling answer**,
- but more than one **currently valid public route** to that same answer.

Without a bounded rule for that posture, reviewers tend to make one of three mistakes:
- they emit a false `531` supersession note even though nothing controlling actually changed,
- they demote one still-current sibling route into a historical leg even though it remains live now,
- or they let two co-current routes sound like two separate heads.

This document fixes that bounded ambiguity.
It standardizes one small note for **canonical head + co-current alias routes**.

## This is not the same thing as `517`, `529`, `530`, `531`, `533`, `535`, `537`, or `538`

`517` controls genuinely multi-route live events, mirrors, and redirect chains where the platform or office is routing across distinct simultaneous event lanes.

`529` decides which packet is the current controlling head.

`530` decides how later prose should cite the head, a historical leg, or the chain.

`531` records a real head change.

`533` records the opposite bounded case where no public media head currently exists.

`535` covers the nearby but different case where one ordinary-public head still exists while a narrower audience-scoped route remains current only for a defined subset.

`537` covers the nearby but different case where the route mainly works because the holder already possesses the full unlisted, privacy-hash, or other token-bearing path.

`538` covers the nearby but different case where the same object is still being rendered through a direct player-host or embed path and the real question is render-shell classification rather than whether the public has another ordinary watch-page alias.

`534` is different.
It says that sometimes the archive should keep **one canonical head** while also recording one or more **co-current alias routes** that are still valid now.
Those aliases are not new heads, not historical legs, and not proof that supersession happened.

## Default rule: one head may have co-current aliases

Inside one `528` same-object chain, reviewers MAY keep exactly one current canonical head under `529` while also recording one or more **co-current aliases** when all of the following hold:

1. **The underlying object is still the same.**
   The routes still resolve to the same office-controlled event, recording, or published media answer.
2. **The present-tense answer is materially the same.**
   A voter following either route gets the same controlling event or recording rather than a meaningfully different state, gate, mirror, or successor.
3. **Both routes are public and current now.**
   The sibling route is not merely historical, withdrawn, gated, or hypothetical.
4. **The difference is route form, packaging, or entry path.**
   The alias differs by portal, player wrapper, shared video URL, or other packaging layer, not by a controlling answer change.
5. **One route is still the better canonical default.**
   `526` can still name the winning default recovery/anchor target even though another lawful route remains current.

When those conditions hold, keep one canonical head and note the other route as a co-current alias.
Do **not** create a second head just because the same answer is reachable two ways.

## Minimal alias grammar

When a same-object chain has one canonical current head plus other still-current sibling routes, reviewers SHOULD prefer one line in this shape:

`chain=<stable object label>; head=<canonical current tuple or packet>; aliases=<co-current route(s)>; alias_mode=co_current; cite_default=<head>; cite_alias_when=<path-specific reproduction or audience-path claim>; basis=<why the alias is still current but not the canonical head>`

This is a compact note contract, not a new schema.
It exists so packet notes and revision summaries stop flipping between false supersession and false historical-leg labeling.

## When to use a co-current alias note

Reviewers SHOULD prefer a `534` note when any of these are true:

1. **Event-page + archive URL coexist**
   A recurring or event-shell page still exposes the same archived stream while the archive also has its own direct video URL.
2. **Canonical route + convenience route coexist**
   One route is the archive's best default anchor under `526`, but another public route remains current enough that later repro notes may still need to name it explicitly.

The note is not needed just because two screenshots look visually different.
It is only for cases where one answer is genuinely still current across more than one public route.

## Canonical-head rule

A co-current alias note does **not** replace `529`.
`529` still names the one canonical head.

The head SHOULD be the route that best satisfies the archive's ordinary default rules:
- best office-controlled recovery target,
- best present-tense citation target,
- best first-contact re-anchor for an ordinary public user,
- and least ambiguity about currentness.

The alias remains current, but it SHOULD not displace the canonical head unless one of those controlling facts actually changes.
If a later packet really changes the winning default route, emit a `531` supersession note instead of stretching `534` past its limit.

## Citation rule

By default, later notes SHOULD still cite the canonical head under `530`.
A co-current alias SHOULD be cited only when the later claim is specifically about:
- how a user reached the same answer,
- which fully public sibling route a viewer actually used,
- or how to reproduce the same current answer from that sibling path.

That means `534` preserves one honest exception to head-first citation without letting the alias sound like a competing current answer.

## When not to use `534`

Do **not** use `534` when:
- the sibling route is only historical and no longer current,
- the sibling route is gated, restricted, or missing for the ordinary public now,
- the sibling route is current only for a defined audience subset and belongs in `535`,
- the sibling route mainly works because the holder possesses the full bearer-style path and belongs in `537`,
- the sibling route is mainly a player-host or direct embed-render path and belongs in `538`,
- the route moved between public and scoped buckets across time and the real task is to record that reclassification under `536`,
- the route is a genuinely different simultaneous event lane or mirror that belongs in `517`,
- the controlling answer actually changed and needs `531`,
- or no public media head exists at all and the chain should be governed by `533`.

If two routes look similar but one is no longer current, prefer historical-leg scoping under `530` or headless-chain handling under `533` rather than alias labeling.

## Examples

- `chain=county_board_recurring_event_mar_2026; head=direct archive packet on unique video URL; aliases=event page playlist route for the same archived stream; alias_mode=co_current; cite_default=head; cite_alias_when=explaining how the viewer stayed inside the recurring event player; basis=both routes are still current and public for the same archived stream, but the direct archive URL is the clearer default citation target`

## Tie-breaker when reviewers say “if two routes are current, they must both be heads”

Ask:
- do both routes still resolve to the same present-tense official answer,
- would a voter following either route get materially the same office-controlled recording or event state,
- and can `526` still name one cleaner canonical default without lying about the other route's currentness?

If yes, keep one head and mark the sibling route as a co-current alias.
If no, the case probably belongs in `517`, `531`, or `533` instead.

## Promotion rule

Future media additions should usually **not** be promoted just because a same-object chain still has one controlling answer but several public route forms remain simultaneously valid.
Tighten `534` first.
Only add another numbered surface when the ambiguity is really about a new first-contact boundary, a new mirror/simulcast class, or a new restriction object rather than about sibling-route governance inside an already-known chain.

## Minimal artifact

This document is intentionally doc-only.
Do **not** add a checklist or payload template for it unless the archive later proves that `529–534` still leave current sibling routes drifting between false supersession and false historical-leg labels.
