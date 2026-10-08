# 536 — Official voter-information platform media route-scope transitions, widening/narrowing, and alias re-bucketing discipline

**Track:** Shared

This document adds one bounded rule to the recent platform-media chain layer:
once `528` has stitched several observations into one same-object media chain, `529` can choose a current head, `533` can mark the chain headless when no public media head exists, `534` can keep one canonical head plus fully public sibling aliases, and `535` can preserve audience-scoped aliases **what should the archive do when the same route or route family changes scope over time without becoming a different object?**

This document answers that narrow question.

It composes with:
- `docs/163-artifact-reference-conventions.md`
- `docs/173-canonical-evidence-envelopes-and-packets.md`
- `docs/206-digest-cards-and-low-bandwidth-publication.md`
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
- `docs/533-official-voter-information-platform-media-no-public-head-states-headless-chain-notes-and-fallback-anchor-discipline.md`
- `docs/534-official-voter-information-platform-media-co-current-aliases-sibling-routes-and-canonical-head-with-alias-discipline.md`
- `docs/535-official-voter-information-platform-media-audience-scoped-current-aliases-scope-labels-and-public-default-retention-discipline.md`
- `docs/537-official-voter-information-platform-media-capability-bearing-current-aliases-link-secret-routes-and-redaction-default-discipline.md`

## Why this exists (bounded)

Current official platform help already shows that one office-controlled media object can move across **route-scope classes** over time without becoming a different underlying object.
YouTube says live-stream archives can later have their privacy changed, including being made private.
Vimeo says the same video can be public, unlisted, hidden from Vimeo, password-protected, or private, and that changing a video to unlisted adds a privacy-hash-bearing URL form needed for sharing and embeds.
Microsoft says a town-hall recording becomes attendee-available only if organizers publish it, and attendees then receive an email link to that recording.
(xref: `youtube_archive_live_streams_help_page`; xref: `youtube_change_video_privacy_settings_help_page`; xref: `vimeo_about_video_privacy_settings_help_page`; xref: `microsoft_attend_town_hall_help_page`)

That means the same-object chain can legitimately see the **same route or answer family** move between buckets such as:
- ordinary-public current head,
- fully public co-current alias,
- audience-scoped current alias,
- capability-bearing current alias,
- or no public media head at all.

Without a bounded rule for that posture, reviewers tend to make one of three mistakes:
- they emit a false `531` supersession note even though the object did not materially change and only the scope did,
- they invent a new chain for what is really the same route becoming wider or narrower,
- or they leave yesterday's bucket label in place even after the route moved from public to scoped, scoped to public, or public to headless.

This document fixes that narrow ambiguity.
It standardizes one compact note for **scope transitions + alias re-bucketing**.

## This is not the same thing as `531`, `533`, `534`, `535`, or `537`

`531` records a real head change or demotion trigger.

`533` records the bounded state where the chain currently has no public media head.

`534` records fully public co-current aliases that are current at the same time.

`535` records current aliases that remain valid only for a defined subset while an ordinary-public head still exists.

`537` records current aliases whose practical use depends mainly on possession of the full bearer-style path.

`536` is different.
It says that sometimes the underlying media object is still the same, but the route posture **moves from one of those buckets into another** over time.
That change should be logged as a **reclassification** unless the controlling answer itself truly changed.

## Default rule: re-bucket the same route before minting a new object

Inside one `528` same-object chain, reviewers SHOULD treat a later scope change as a **re-bucketing event** rather than a new object when all of the following hold:

1. **The underlying object is still the same.**
   The later route still resolves to the same office-controlled event, recording, or durable answer family.
2. **The main change is who can use the route, not what the route means.**
   The object did not become a materially different answer; its availability or audience scope changed.
3. **The chain can still explain the before/after posture cleanly.**
   Reviewers can say whether the route moved into `533`, `534`, `535`, or back to an ordinary-public `529` head.
4. **Treating the change as a whole new object would hide continuity.**
   Later readers would lose the fact that the same route or answer family widened, narrowed, or disappeared from public reach.

When those conditions hold, keep the same-object chain and record the scope transition explicitly.
Do **not** fork a new chain just because a route moved between public, scoped, and headless postures.

## Minimal scope-transition grammar

When one route or answer family changes scope over time, reviewers SHOULD prefer one line in this shape:

`chain=<stable object label>; route=<packet or route label>; scope_transition=<public_to_scoped|scoped_to_public|public_to_headless|headless_to_public|public_alias_to_scoped_alias|scoped_alias_to_public_alias|public_alias_to_capability_alias|capability_alias_to_public_alias|scoped_alias_to_capability_alias|capability_alias_to_scoped_alias|other bounded transition>; previous_bucket=<529_head|534_alias|535_scoped_alias|537_capability_alias|533_headless>; current_bucket=<529_head|534_alias|535_scoped_alias|537_capability_alias|533_headless>; cite_default=<current head|fallback anchor>; trigger=<privacy_change|publication|gate_added|gate_removed|tokenized_share_path|other bounded cause>; basis=<why the object stayed the same while its scope posture changed>`

This is a compact note contract, not a new schema.
It exists so later summaries stop confusing **same-object scope drift** with **new-object supersession**.

## Typical uses

Reviewers SHOULD prefer a `536` note when any of these are true:

1. **Public to scoped**
   A once-public replay or archive becomes passworded, invited, hidden-from-platform, or otherwise no longer an ordinary-public route, while the same object still exists.
2. **Scoped to public**
   A route that was previously available only to attendees, invitees, or holders of a narrower path later becomes the ordinary-public route or a public alias.
3. **Public to headless**
   A route that used to control is withdrawn or unpublished, so the same-object chain remains real but now belongs in `533`.
4. **Scoped alias to head / alias**
   A previously narrower route later widens enough that it should now be treated as the ordinary-public head or as a fully public sibling alias under `534`.
5. **Capability-route re-bucketing**
   A route is still current for the same answer, but its bucket changes between `534`, `535`, and `537` because the main fact became public discoverability, named-audience admission, or possession of the full bearer-style path.
6. **Alias re-bucketing without answer change**
   A route is still current for the same answer, but its bucket changes from `534` to `535`, from `535` to `537`, or from `537` back to `534`, because reach changed without changing the underlying object.

## Re-bucketing order

Use this order:

1. **Confirm same-object continuity under `528`.**
2. **Ask whether the controlling answer actually changed.**
   - If yes, use `531` as needed.
   - If no, continue.
3. **Classify the current scope posture.**
   - ordinary-public current route -> `529` (and `534` if sibling public aliases also exist),
   - current but subset-only route alongside an ordinary-public head -> `535`,
   - current but bearer-style/token-bearing route -> `537`,
   - no public media head -> `533`.
4. **Add one `536` note** recording how the route moved between those buckets.
5. **Let `530` carry the new citation default** so later notes stop citing the route as though its old scope still applied.

## When not to use this

Do **not** use `536` when:
- the later packet is actually a materially different answer and needs `531`,
- the route is merely another simultaneously current public alias and belongs in `534`,
- the route is merely a subset-scoped current alias with no recent bucket change and belongs in `535`,
- the route is merely a capability-bearing current alias with no recent bucket change and belongs in `537`,
- the chain is simply headless now and no transition explanation is needed beyond `533`,
- or the decisive issue is still the current restriction shell itself and belongs in `512` or `518`.

The note is for **transitions between buckets**, not for steady-state bucket labels.

## Citation rule

By default, later notes SHOULD cite the route according to its **current bucket**, not its former bucket.
Use the `536` transition note only when the later claim is specifically about:
- how the route posture changed,
- why an old public citation target no longer controls,
- or why a previously scoped path now counts as public (or vice versa).

That keeps transition history available without letting yesterday's scope leak into present-tense guidance.

## Examples

- `chain=county_board_stream_mar_2026; route=replay packet on direct archive URL; scope_transition=public_to_headless; previous_bucket=529_head; current_bucket=533_headless; cite_default=fallback written update page; trigger=privacy_change; basis=the same recording chain remains historically real, but no ordinary-public media route now controls`
- `chain=city_budget_town_hall; route=attendee recording link family; scope_transition=scoped_to_public; previous_bucket=535_scoped_alias; current_bucket=529_head; cite_default=current head; trigger=publication; basis=the same recording answer widened from attendee-only delivery into the ordinary-public current route`
- `chain=regional_results_briefing; route=direct video URL; scope_transition=public_alias_to_scoped_alias; previous_bucket=534_alias; current_bucket=535_scoped_alias; cite_default=event-page head; trigger=gate_added; basis=the same answer still exists, but this particular sibling route no longer counts as an ordinary-public alias`
- `chain=county_board_video_briefing; route=hashed archive URL family; scope_transition=public_alias_to_capability_alias; previous_bucket=534_alias; current_bucket=537_capability_alias; cite_default=event-page head; trigger=tokenized_share_path; basis=the same answer still exists, but this route now depends mainly on possession of the full bearer-style path rather than ordinary public discoverability`

## Tie-breaker when reviewers ask “isn't a scope change automatically a new head change?”

Ask three questions:
- is the underlying office-controlled object still the same,
- did the route mainly change **who can use it** rather than **what answer it gives**,
- and can the chain still explain the current posture inside `533`, `534`, or `535` without inventing a new object?

If yes, keep the same-object chain and use `536` to re-bucket the route.
If no, the case probably belongs in `531` or a different boundary doc.

## Promotion rule

Future media additions should usually **not** be promoted just because one route widened, narrowed, or disappeared from ordinary-public reach while the same underlying object remained in play.
Tighten `536` first.
Only add another numbered surface when the ambiguity is really about a new restriction shell, a new gate object, or a new media-answer boundary rather than about **scope drift inside an already-known chain**.

## Minimal artifact

This document is intentionally doc-only.
Do **not** add a checklist or payload template for it unless the archive later proves that route-scope transitions still drift between `531`, `533`, `534`, and `535` after this compact re-bucketing contract exists.
