# 535 — Official voter-information platform media audience-scoped current aliases, scope labels, and public-default-retention discipline

**Track:** Shared

This document adds one bounded rule to the recent platform-media chain layer:
once `528` has stitched several observations into one same-object media chain, `529` has named the current controlling head, `530` has told later notes to cite that head by default, and `534` has covered fully public co-current aliases, **how should the archive record routes that are still current only for a defined audience subset without letting those subset routes displace the ordinary public default?**

This document answers that narrow question.

It composes with:
- `docs/163-artifact-reference-conventions.md`
- `docs/173-canonical-evidence-envelopes-and-packets.md`
- `docs/206-digest-cards-and-low-bandwidth-publication.md`
- `docs/223-public-surface-capture-notes-and-reproducibility.md`
- `docs/369-official-voter-information-videos-livestreams-and-clip-context-discipline.md`
- `docs/518-official-voter-information-platform-registration-forms-invite-only-join-links-and-audience-gated-media-authority-boundary-discipline.md`
- `docs/523-official-voter-information-platform-media-boundary-quickmap-and-duplicate-firewall.md`
- `docs/526-official-voter-information-platform-media-re-anchor-ladder-canonical-recovery-targets-and-wrapper-exit-discipline.md`
- `docs/527-official-voter-information-platform-media-control-tuple-one-line-normalization-contract-and-packet-comparison-discipline.md`
- `docs/528-official-voter-information-platform-media-same-object-transition-chains-packet-stitching-and-resnapshot-threshold-discipline.md`
- `docs/529-official-voter-information-platform-media-chain-heads-current-control-and-closeout-discipline.md`
- `docs/530-official-voter-information-platform-media-chain-citations-head-first-reference-and-historical-leg-scoping-discipline.md`
- `docs/533-official-voter-information-platform-media-no-public-head-states-headless-chain-notes-and-fallback-anchor-discipline.md`
- `docs/534-official-voter-information-platform-media-co-current-aliases-sibling-routes-and-canonical-head-with-alias-discipline.md`
- `docs/536-official-voter-information-platform-media-route-scope-transitions-widening-narrowing-and-alias-rebucketing-discipline.md`
- `docs/537-official-voter-information-platform-media-capability-bearing-current-aliases-link-secret-routes-and-redaction-default-discipline.md`
- `docs/540-official-voter-information-platform-media-notification-carriers-reminder-pointers-and-route-carrier-separation-discipline.md`

## Why this exists (bounded)

Current official platform help already shows that one office-controlled media answer can have an **ordinary public route** while also remaining reachable through a narrower audience-scoped route.
YouTube says a Premiere creates a public watch page whose URL can be shared before the event begins.
Microsoft says that if a town-hall recording is published, attendees automatically receive an email with a link to the recording, and that attendee-facing post-event views can also expose the recording.
Current platform help also shows that some routes can instead become private or access-limited, which means the archive must not confuse a subset-only route with a generally public one.
(xref: `youtube_premiere_new_video_help_page`; xref: `microsoft_attend_town_hall_help_page`; xref: `youtube_change_video_privacy_settings_help_page`; xref: `vimeo_about_video_privacy_settings_help_page`)

That means the chain layer needs one compact distinction:
- some co-current aliases are still valid for the **ordinary public** and belong in `534`,
- some routes are still valid only for a **defined audience subset** and belong here,
- and some chains have **no public media head at all** and belong in `533`.

Without that distinction, reviewers tend to make one of three mistakes:
- they treat an attendee-only or other subset-only route as if it were the ordinary public head,
- they force a subset route into `534` even though `534` is for fully public sibling aliases,
- or they collapse the whole posture into `533` even though a public head still exists and only the extra route is scoped.

This document fixes that bounded ambiguity.
It standardizes one small note for **audience-scoped current aliases that do not displace the public default**.

## This is not the same thing as `518`, `533`, `534`, or `537`

`518` controls the first-contact gate itself: registration forms, invite-only joins, approvals, memberships, and similar audience-selection shells.

`533` covers the opposite bounded case where **no public media head currently exists**.

`534` covers the case where more than one **fully public** route is still current for the same controlling answer.

`537` covers the nearby but different case where the route mainly works because the holder possesses the full unlisted, privacy-hash, or other token-bearing path rather than because a named audience subset is admitted.

`535` is different.
It says that sometimes one same-object chain should keep:
- one **ordinary-public canonical head**,
- plus one or more **current but audience-scoped aliases** for a defined subset such as attendees, registrants, or invited viewers.

Those scoped aliases are not new heads, not historical legs, and not proof that the public default changed.
But they also should not be described as if they were available to everyone.
If a scoped alias is delivered through an email, reminder, or inbox surface, keep the route in `535` and use `540` only for the carrier note.

## Default rule: keep the public head, label the scoped alias

Inside one `528` same-object chain, reviewers MAY keep one ordinary-public canonical head under `529` while also recording one or more **audience-scoped current aliases** when all of the following hold:

1. **The underlying object is still the same.**
   The routes still resolve to the same office-controlled event, recording, or published media answer.
2. **The subset route is current now for a defined audience.**
   The route is not merely historical; it still works for a named subset such as attendees, registrants, or other admitted viewers.
3. **The ordinary public still has a better default current route.**
   `526` can still name one cleaner ordinary-public anchor that should remain the archive's default recovery target.
4. **Describing the subset route as simply “current” would mislead.**
   A general reader could mistake the subset route for the answer available to everyone.
5. **The subset route still matters for reproduction or audience-path claims.**
   The archive would lose useful truth if it ignored how that subset actually reached the same answer.

When those conditions hold, keep the public head and label the subset route as a scoped alias.
Do **not** let the subset route silently replace the public default.

## Minimal scoped-alias grammar

When a same-object chain has one ordinary-public head plus a current subset route, reviewers SHOULD prefer one line in this shape:

`chain=<stable object label>; head=<ordinary public current tuple or packet>; scoped_aliases=<subset route(s)>; alias_scope=<attendees|registrants|invited_viewers|other named subset>; cite_default=<head>; cite_scoped_when=<audience-path or scoped reproduction claim>; basis=<why the subset route is current but not the public default>`

This is a compact note contract, not a new schema field.

## When to use a scoped-alias note

Typical uses include:

1. **Public recording plus attendee-only delivery path**
   The ordinary public can already use a stable office-controlled recording route, but attendees also receive or retain a narrower path to that same recording.
2. **Public event or replay route plus participant-only convenience path**
   A subset can still reach the same answer through an email-delivered, portal-only, or admitted-viewer route that should remain reproducible without becoming the archive's ordinary-public default.
3. **Current same-answer route with audience scoping that matters to the claim**
   The subset path is necessary to explain what a particular audience saw or received, even though `526` can still name a better public anchor for everyone else.

## When not to use this

Do **not** use `535` when:
- there is no ordinary-public media head at all — use `533`,
- the sibling route is fully public and current for everyone — use `534`,
- the decisive issue is still the pre-access gate itself — use `518`,
- the subset route is only historical and no longer current — use `530` historical-leg scoping,
- the route mainly changed buckets across time and the real task is to record a widening/narrowing reclassification under `536`,
- the route mainly works because the viewer possesses the full bearer-style path rather than because a named subset is admitted — use `537`,
- the real ambiguity is not the scoped route but the notification, reminder, or email that carried it — keep the route here and use `540` for the carrier note,
- or the head itself truly changed — use `531`.

If the subset route becomes the only surviving route and the ordinary public no longer has a valid current media head, the chain should normally move to `533` rather than stay in `535`.

## Citation rule

By default, later notes SHOULD still cite the ordinary-public head under `530`.
A scoped alias SHOULD be cited only when the later claim is specifically about:
- what a defined audience segment actually received,
- how that segment reproduced the same answer,
- or why a subset-only route should not be mistaken for the archive's ordinary-public default.

That means `535` preserves one honest exception to head-first citation without letting audience-specific convenience paths quietly replace the public route.

## Examples

- `chain=city_budget_town_hall_mar_2026; head=published recording packet on office-controlled public route; scoped_aliases=attendee email recording link, attendee portal recording route; alias_scope=attendees; cite_default=head; cite_scoped_when=explaining what admitted attendees received after publication; basis=the same recording answer is current, but the attendee-only delivery paths should not replace the ordinary public anchor`
- `chain=county_results_briefing; head=public replay packet; scoped_aliases=invited viewer portal route to the same replay; alias_scope=invited_viewers; cite_default=head; cite_scoped_when=reproducing the route promised to invitees; basis=the scoped route stays current for that subset, but the public replay route still controls ordinary guidance`

## Tie-breaker when reviewers ask “if the subset route is current, why isn't it another head?”

Ask three questions:
- does the route stay current only for a named subset rather than for the ordinary public,
- can `526` still name one better public default without lying about the subset path,
- and would a general reader be misled if the subset route were described without scope?

If yes, keep one ordinary-public head and record the subset route under `535`.
Do **not** promote a scoped alias into a competing head.

## Promotion rule

Future media additions should usually **not** be promoted just because one same-object chain has both an ordinary-public head and a narrower still-current delivery path for a subset.
Tighten `535` first.
Only add another numbered surface when the ambiguity is really about a new first-contact gate, a new restriction object, or a new public-route boundary rather than about subset-scoped currentness inside an already-known chain.

## Minimal artifact

This document is intentionally doc-only.
Do **not** add a checklist or payload template for it unless the archive later proves that subset-scoped current aliases still drift between `518`, `533`, and `534` after this compact note contract exists.
