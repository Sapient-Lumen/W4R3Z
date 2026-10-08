# 533 — Official voter-information platform media no-public-head states, headless-chain notes, and fallback-anchor discipline

**Track:** Shared

This document adds one bounded rule to the recent platform-media chain layer:
once `528` has stitched several observations into one same-object media chain, `529` can choose a current head when one exists, `530` can cite that head cleanly, `531` can explain a supersession, and `532` can warn that a current head is still provisional, **what should the archive say when the chain currently has no public media head at all?**

This document answers that narrow question.

It composes with:
- `docs/173-canonical-evidence-envelopes-and-packets.md`
- `docs/218-epistemic-status-tags-and-confidence-rubric.md`
- `docs/223-public-surface-capture-notes-and-reproducibility.md`
- `docs/369-official-voter-information-videos-livestreams-and-clip-context-discipline.md`
- `docs/512-official-voter-information-platform-unavailable-private-age-gated-region-blocked-and-playback-restricted-surface-authority-boundary-discipline.md`
- `docs/518-official-voter-information-platform-registration-forms-invite-only-join-links-and-audience-gated-media-authority-boundary-discipline.md`
- `docs/523-official-voter-information-platform-media-boundary-quickmap-and-duplicate-firewall.md`
- `docs/526-official-voter-information-platform-media-re-anchor-ladder-canonical-recovery-targets-and-wrapper-exit-discipline.md`
- `docs/528-official-voter-information-platform-media-same-object-transition-chains-packet-stitching-and-resnapshot-threshold-discipline.md`
- `docs/529-official-voter-information-platform-media-chain-heads-current-control-and-closeout-discipline.md`
- `docs/530-official-voter-information-platform-media-chain-citations-head-first-reference-and-historical-leg-scoping-discipline.md`
- `docs/531-official-voter-information-platform-media-head-supersession-notes-trigger-codes-and-demotion-discipline.md`
- `docs/532-official-voter-information-platform-media-head-volatility-labels-provisional-current-notes-and-review-window-discipline.md`
- `docs/534-official-voter-information-platform-media-co-current-aliases-sibling-routes-and-canonical-head-with-alias-discipline.md`
- `docs/535-official-voter-information-platform-media-audience-scoped-current-aliases-scope-labels-and-public-default-retention-discipline.md`
- `docs/536-official-voter-information-platform-media-route-scope-transitions-widening-narrowing-and-alias-rebucketing-discipline.md`
- `docs/537-official-voter-information-platform-media-capability-bearing-current-aliases-link-secret-routes-and-redaction-default-discipline.md`

## Why this exists (bounded)

Current official platform help already shows that one office-controlled media object can leave a useful historical chain behind while **no public media route currently controls**.
YouTube says live-stream archives can later have their privacy changed, including being made private, or be deleted.
Vimeo says video privacy can be set so only certain viewers may watch, and its privacy modes can keep a video out of ordinary public discovery or viewing.
Microsoft says attendees get a town-hall recording link only **if** organizers publish a recording.
(xref: `youtube_archive_live_streams_help_page`; xref: `youtube_change_video_privacy_settings_help_page`; xref: `vimeo_about_video_privacy_settings_help_page`; xref: `microsoft_attend_town_hall_help_page`)

That means a same-object media chain can be perfectly real while still having **no current public media head**.
Examples include:
- a live or replay route that used to be public but is now private or deleted,
- an event that has ended but whose recording has not yet been published,
- a chain whose only surviving media route is currently restricted to a gated audience,
- or a packet set whose historical legs are still useful evidence but no longer describe what an ordinary voter can reach now.

Without a bounded rule for that posture, reviewers tend to make one of two mistakes:
- they keep the **last known public media leg** sounding current even though the public can no longer use it, or
- they collapse the whole incident into a generic `512` restriction shell and lose the fact that a same-object chain already exists behind that shell.

This document fixes that narrow ambiguity.
It standardizes one small note for **headless media chains + current fallback anchors**.

## This is not the same thing as `512`, `518`, `529`, `532`, or `534`

`512` controls the current first-contact shell when the public hits an unavailable, private, age-gated, region-blocked, or playback-restricted media route.

`518` controls registration, invite-only, approval, or audience-gated entry workflows.

`529` chooses a current head when a public media packet still legitimately controls.

`532` warns when a current head is still provisional and likely to change soon.

`534` covers the bounded opposite case where a current head still exists and more than one public route is simultaneously valid for that same answer.

`535` covers the nearby but different case where a current ordinary-public head still exists while one or more narrower audience-scoped routes remain current for a defined subset.

`537` covers the nearby but different case where a bearer-style unlisted, privacy-hash, or other token-bearing route may still exist, but that capability path does not by itself create an ordinary-public head.

`533` is different.
It says that sometimes the chain should have **no current public media head at all**.
In that case the archive SHOULD:
- keep older media packets only as historical legs,
- record the current restriction or absence through the controlling adjacent doc such as `512` or `518`,
- and name the best current written/help fallback anchor rather than letting the last visible media leg keep sounding current.

## Default rule: if no public media route currently controls, set `head=none`

Inside a `528` same-object chain, reviewers SHOULD set the media head to **none** when all of the following hold:

1. **The chain is still real.**
   The packets still describe the same office-controlled media object or event lifecycle.
2. **No current public media packet should control.**
   No chained media packet still gives an ordinary public user the best current office-controlled answer route.
3. **The current situation is better described by absence, restriction, or withheld publication.**
   The present-tense answer is now carried by a restriction shell, a no-recording-yet posture, or a non-media help/update lane.
4. **Keeping the old head would mislead later readers.**
   Treating the most recent historical media leg as still current would overstate present public access.

When those conditions hold, do **not** keep a stale live, replay, or archive packet as the head just because it was the last public leg anyone captured.
Use a headless-chain note instead.

## Minimal headless-chain grammar

When a chain currently has no public media head, reviewers SHOULD prefer one line in this shape:

`chain=<stable object label>; head=none; historical=<most recent historical leg(s)>; head_mode=<no_public_head>; current_surface=<512|518|other controlling adjacent doc>; fallback_anchor=<best current written/help route>; status=<open|closed>; basis=<why no public media packet should control now>`

This is a compact note contract, not a new schema.
It exists so later summaries stop citing yesterday's media leg as though it were still the present public answer.

## When to use a headless-chain note

Reviewers SHOULD prefer a `533` note when any of these are true:

1. **Withdrawn or restricted archive**
   A once-public replay/archive route is now private, deleted, domain-denied, members-only, or otherwise not a valid current public answer.
2. **Recording not yet published**
   The live event has ended, but the organizer-controlled durable recording route does not yet exist publicly.
3. **Gated-only continuation**
   The same object continues behind a registration, invite, or limited-audience wall such that no ordinary public media head currently controls.
4. **Capability-only continuation**
   The same object still has a bearer-style unlisted, privacy-hash, or other token-bearing path, but no rediscoverable ordinary-public media route should control now. Pair this with `537` if the capability path itself matters to the claim.
5. **Fallback lane now wins**
   The archive's best current answer must now be a written page, update notice, directory entry, or contact/help lane rather than any currently reachable media packet.

The point is not to say the event disappeared from history.
The point is to stop a historical media leg from masquerading as the current public route.

## How `533` works with `512`, `526`, and `530`

Use this order:

1. **Use `512` or `518` to describe the present first-contact shell** if the public now hits restriction, privacy, gating, or withheld-entry behavior.
2. **Use `533` to say the media chain has no current public head.**
3. **Use `526` to choose the best current fallback anchor** outside the missing or restricted media route.
4. **Use `530` so later prose cites that fallback anchor for present-tense guidance** and cites the historical media leg only when speaking historically.

That keeps the archive from making a restriction shell sound like the office's only answer while still refusing to pretend that an older public replay or live leg remains current.

## Open vs closed headless chains

A headless chain may be either **open** or **closed**.

Use `status=open` when a later public media head still seems plausible, such as:
- a recording may still be published,
- a temporary restriction may still lift,
- or the organizer may expose a new durable route.

Use `status=closed` when the archive has enough basis to say no later public media head is expected and the current durable answer really is the fallback written/help lane.

If the chain is open and a likely next trigger is visible, pair `533` with the provisional-review logic from `532` rather than leaving the absence note timeless and vague.

## Relationship to head supersession

Sometimes a `531` head-supersession note will say that one packet displaced another packet.
Sometimes the real result is stricter: the prior head was demoted and **no public media head replaced it**.

When that happens:
- let `531` record the trigger that demoted the old head,
- let `533` record that the chain is now headless,
- and let `526` / `530` move current-answer prose to the fallback anchor.

That sequence is preferable to forcing `529` to keep a stale head just because the chain still exists.
If the route later widens back into ordinary-public reach, use `536` to record the re-bucketing rather than pretending the headless period and the later public return belong to unrelated chains.

## Examples

- `chain=county_budget_stream_mar_2026; head=none; historical=509 replay tuple on watch URL; head_mode=no_public_head; current_surface=512; fallback_anchor=county election updates page; status=open; basis=the replay archive existed historically but the route is now private, so the current public answer must anchor to the office update page until a public replacement appears`
- `chain=city_town_hall_mar_2026; head=none; historical=516 live attendee tuple; head_mode=no_public_head; current_surface=other controlling adjacent doc; fallback_anchor=city town hall recap page; status=open; basis=the event ended, but attendees only receive a recording link if organizers publish one and no public recording head exists yet`
- `chain=regional_candidate_forum; head=none; historical=508 pre-start tuple, 516 live tuple, 509 replay tuple; head_mode=no_public_head; current_surface=518; fallback_anchor=official registration/help page; status=closed; basis=the continuing route is audience-gated and the office now directs ordinary public users to the non-media help lane rather than to a public recording`

## Tie-breaker when reviewers want to keep the last visible media packet as current “for continuity”

Ask:
- can an ordinary public user still rely on that packet as the best current official media answer,
- does a present-tense citation to that packet still help more than it misleads,
- and would a written/help fallback anchor now be more honest about what the public can actually do?

If the answer favors the fallback anchor, do **not** keep the last visible media packet as the current head.
Mark it historical and use `533`.

## Promotion rule

Future media additions should usually **not** be promoted just because a same-object chain persists historically while its current public media head disappears.
Tighten `533` first.
Only add another numbered surface when the real ambiguity is about a new first-contact boundary or a new restriction/gating object, not about chain governance after the media head has gone dark.

## Minimal artifact

This document is intentionally doc-only.
Do **not** add a checklist or payload template for it unless the archive later proves that reviewers still leave withdrawn or unpublished media chains sounding current after `512`, `518`, `523`, and `528–533` are used together.
