# 590 — Official voter-information platform media authenticity-cue viewer-state variance, eligibility conditions, and non-universality firewall

**Track:** Shared / Public surfaces

This document defines a bounded control for **official voter-information media routes where a supportive authenticity-adjacent cue is same-route and contemporaneous but not uniformly visible to every viewer** because of bounded viewer conditions such as:
country/region or language availability,
app/device or supported-surface differences,
organization-controlled profile/identity settings,
or similar eligibility conditions that do **not** by themselves mean the underlying current media head changed.

It does not create a new authenticity score.
It does not turn every viewer-conditional cue into a new route.
It adds one narrow rule:
**when the same official media route shows a supportive authenticity-adjacent cue to some viewers but not others because of bounded viewer conditions, the archive should preserve that condition without treating one viewer's observation as the route's universal cue state.**

It composes with:
- `docs/108-language-device-parity-and-ui-integrity.md`
- `docs/194-synthetic-media-and-comms-authenticity-minimum-controls.md`
- `docs/224-request-context-and-variant-probing-for-public-surfaces.md`
- `docs/369-official-voter-information-videos-livestreams-and-clip-context-discipline.md`
- `docs/406-official-voter-information-request-context-variance-personalization-and-experiment-boundary-discipline.md`
- `docs/512-official-voter-information-platform-unavailable-private-age-gated-region-blocked-and-playback-restricted-surface-authority-boundary-discipline.md`
- `docs/520-official-voter-information-platform-channel-bylines-profile-names-handles-verification-badges-and-source-identity-wrapper-authority-boundary-discipline.md`
- `docs/521-official-voter-information-platform-information-panels-context-boxes-disclosure-labels-and-policy-wrapper-authority-boundary-discipline.md`
- `docs/523-official-voter-information-platform-media-boundary-quickmap-and-duplicate-firewall.md`
- `docs/530-official-voter-information-platform-media-chain-citations-head-first-reference-and-historical-leg-scoping-discipline.md`
- `docs/583-official-voter-information-platform-media-stacked-authenticity-cues-identity-context-provenance-ordering-and-non-collapse-firewall.md`
- `docs/584-official-voter-information-platform-media-provenance-signals-content-credentials-and-non-substitutive-authenticity-discipline.md`
- `docs/585-official-voter-information-platform-media-authenticity-cue-transport-cross-route-divergence-and-absence-non-inference-firewall.md`
- `docs/586-official-voter-information-platform-media-authenticity-cue-tension-aspect-separation-and-non-cancellation-firewall.md`
- `docs/587-official-voter-information-platform-media-authenticity-cue-lifecycle-timing-drift-and-non-retroactive-inference-firewall.md`
- `docs/588-official-voter-information-platform-media-authenticity-cue-attachment-points-scope-boundaries-and-non-inheritance-firewall.md`
- `docs/589-official-voter-information-platform-media-authenticity-cue-inspection-gates-expanded-details-and-non-ambient-visibility-firewall.md`
- `docs/591-official-voter-information-platform-media-authenticity-cue-observation-assembly-cross-state-composites-and-no-faux-single-state-firewall.md`
- `docs/593-official-voter-information-platform-media-authenticity-cue-player-state-occlusion-reduced-context-suppression-and-non-absence-inference-firewall.md`

## Why this exists (bounded)

The archive already knows how to handle:
- one supportive cue family at a time (`520`, `521`, `584`),
- several cue families stacked together on one route (`583`),
- supportive cues drifting across native, embedded, mirrored, search, share, or file-style routes (`585`),
- same-route cue tension (`586`),
- same-route cue timing drift (`587`),
- cue attachment scope (`588`),
- and same-route inspection gates (`589`).

A smaller but still important seam remains:
**the same route can be stable while the cue state is not universal across viewers.**
One viewer on a supported device, in a supported country/region or language, or under one organization profile policy can see a supportive cue that another viewer on the same route at roughly the same time does not see.

Current primary-source guidance is enough to justify a compact bridge.
YouTube's current election-information help says election-related features are only available during election cycles in limited countries/regions, available features may vary by election cycle, and some election panels are only available on the YouTube mobile app or on a computer.
Its current publisher-context help says those panels may not be available in all countries/regions and languages.
Microsoft's current profile-card help says the card may look different depending on which app a viewer is in and that if an administrator has disabled or not synced certain information, that information will not display.
(xref: `youtube_election_information_panels_help_page`; xref: `youtube_publisher_context_information_panel_help_page`; xref: `microsoft_profile_cards_m365_help_page`)

That is enough to create a bounded review problem:
- one viewer's supported-surface capture can get retold as if every viewer on the route saw the same cue,
- one unsupported-viewer or differently configured viewer's absence capture can get retold as if the route lacked the cue globally,
- and same-route disagreements can get misclassified as cross-route drift or authenticity failure even though the head, object, and time window stayed basically the same.

`590` exists to keep that conditionality honest without spawning a new proof family.

## This is not the same thing as `520`, `521`, `584`, `585`, `587`, `589`, `406`, or `512`

`520` asks whether source-identity cues start acting like the whole proof that a route is official or current.

`521` asks whether context/policy wrappers start acting like the whole explanation of authority, currentness, or legal effect.

`584` asks whether provenance/origin-history signals start acting like the whole proof of authenticity or current authority.

`585` asks whether supportive cues traveled unevenly across different routes, wrappers, embeds, mirrors, or file-style legs.

`587` asks whether one same-route cue state later appeared, disappeared, expired, or was backfilled and then got overread as timeless.

`589` asks whether the same viewer needed to expand, click, tap, hover, or open details to discover the cue on the same route.

`406` asks the broader website question of same-URL answer variance on official election websites.

`512` asks whether the route itself is unavailable, sign-in-gated, private, age-gated, region-blocked, or otherwise access-restricted.

`590` asks a different question:
**on the same route and in roughly the same time window, did different viewers get different supportive cue states because of bounded viewer conditions, and are later readers now treating one viewer's cue state as universal?**

If one cue family clearly governs, use that family doc.
If the harder problem is that the whole route was blocked or access-restricted, use `512`.
If the harder problem is different route legs, use `585`.
If the harder problem is same-route timing drift, use `587`.
If the harder problem is same-route click/expand/hover inspection, use `589`.
If the harder problem is not viewer-conditionality itself but a later summary fused observations from different viewers with route/time/interaction observations into one faux simultaneous posture, use `591`.
If the harder problem is not viewer variance but the same viewer saw surrounding cues disappear only because the current object moved into a reduced-context player state, use `593`.
Use `590` only when the decisive fact is that **the same route stayed the same but cue visibility was viewer-conditional rather than universal.**

## Default rule: keep current control with the head; classify viewer-conditional cue state

By default, later notes SHOULD still cite the current controlling head under `530`, or the fallback anchor if the chain is headless.
A viewer-conditional note exists only to explain one bounded non-universality problem around that head.

Use this triage order:
1. if the decisive claim is really about source identity, use `520`;
2. if the decisive claim is really about a context/policy wrapper, use `521`;
3. if the decisive claim is really about provenance/origin-history signaling, use `584`;
4. if the decisive claim is that several supportive cues stacked together and over-signaled trust, use `583`;
5. if the decisive claim is that supportive cues traveled unevenly across routes, use `585`;
6. if the decisive claim is that one same-route cue state later changed over time, use `587`;
7. if the decisive claim is that the same viewer had to inspect/expand/click/hover to discover the cue, use `589`;
8. use `590` only when the decisive claim is that **different viewers on the same route, at roughly the same time, saw different cue states because of bounded viewer conditions.**

This means `590` is not a new preferred citation lane.
It is a compact bridge for cases where a route-level cue claim needs one more sentence: *for whom, on which supported surface, under which bounded viewing condition, was this cue actually visible?*

## Keep route identity distinct from viewer condition

At minimum, keep these layers separate:
1. **current office control** — the current written/help lane and the current media head (`194`, `369`, `529`, `530`);
2. **cue family and attachment** — whether the cue belongs to source identity, context/policy, or provenance, and which object it belongs to (`520`, `521`, `584`, `588`);
3. **route identity and time window** — whether the URL/player/file leg and observation time stayed the same (`585`, `587`);
4. **viewer condition** — which bounded condition mattered, such as `country_or_language`, `app_or_device`, `org_policy`, or `mixed_or_unclear`;
5. **observed cue state for that condition** — what this viewer could actually see without overstating it as universal.

That separation matters because the archive can otherwise make two opposite mistakes:
- elevating one viewer's supported capture into universal route proof, or
- elevating one unsupported/configured-away absence capture into universal route absence.

`590` exists to stop both mistakes.

## Minimal viewer-condition note grammar

When same-route viewer-conditionality itself matters, reviewers SHOULD prefer one compact line in this shape:

`head=<current tuple|none>; cue_condition_state=<viewer_universal|country_or_language_bound|app_or_device_bound|org_policy_bound|mixed_or_unclear>; cue_family=<520|521|584|mixed>; treat_seen_by_one_viewer_as_universal=<forbid>; treat_missing_for_one_viewer_as_global_absence=<forbid>; cite_default=<head|fallback anchor>; cite_condition_when=<claim that cue presence/absence depended on viewer condition rather than route/time>; promote_condition=<no>; basis=<why conditional visibility mattered without minting a new proof object>`

This is a note contract, not a new schema.
It exists so packet notes can say “the cue was same-route but not viewer-universal” without minting a new head, a new route, or a global absence claim.

## Typical uses

1. **Country/language-bounded context panel**
   The same head still controls, but one viewer's capture of an election or publisher-context panel is being retold as if every viewer in every country/region/language would have seen that same wrapper.
2. **App/device-bounded context panel**
   The same head still controls, but a cue available on the YouTube mobile app or on a computer is being narrated as if it were universal across every viewing surface.
3. **Organization-policy-bounded identity detail**
   The same file-hosted or app-hosted official media route still controls, but profile-card identity detail differs because an organization disabled or did not sync some fields, and later readers are flattening one app/org configuration into the universal wrapper state.
4. **Mixed or unclear viewer-conditionality**
   The same head still controls, but later notes know that different viewers saw different cue states and need to preserve that bounded fact honestly even before the exact split is fully resolved.

## When not to use this

Do **not** use `590` when:
- only one of `520`, `521`, or `584` matters and there is no viewer-conditionality mistake;
- the route itself changed — use `585` or the controlling route doc;
- the cue changed later in time on the same route — use `587`;
- the same viewer simply needed expand/click/tap/hover/details inspection — use `589`;
- the whole route was unavailable, sign-in-gated, private, age-gated, or region-blocked rather than one supportive cue varying — use `512`;
- or the decisive issue is still the media object's date, scope, currentness, or correction status — use `369`/`529`/`530`.

If deleting the viewer-condition fact would erase **why two same-route captures disagree without implying a route change**, `590` is probably right.
If deleting that fact would still leave an ordinary single-family claim, a cross-route claim, a timing claim, an inspection-gate claim, or an access-restriction claim, use the narrower doc and omit `590`.
If deleting the assembly fact would erase why a later narrative fused several viewer-conditioned observations into one apparent universal state, use `591` instead of overloading `590`.

## Examples

- `head=state_board_results_watch_packet; cue_condition_state=country_or_language_bound; cue_family=521; treat_seen_by_one_viewer_as_universal=forbid; treat_missing_for_one_viewer_as_global_absence=forbid; cite_default=head; cite_condition_when=proving that an election-information panel was documented for supported countries/regions and should not be narrated as if every same-route viewer would have seen it; promote_condition=no; basis=the route and time window stayed stable but the cue was not viewer-universal`
- `head=county_clerk_archive_stream_packet; cue_condition_state=app_or_device_bound; cue_family=521; treat_seen_by_one_viewer_as_universal=forbid; treat_missing_for_one_viewer_as_global_absence=forbid; cite_default=head; cite_condition_when=proving that a same-route context panel was available on the YouTube mobile app or on a computer and later notes should not silently generalize that supported-surface state to every player environment; promote_condition=no; basis=the cue split was about supported viewing surface rather than route drift`
- `head=clerk_sharepoint_recording_packet; cue_condition_state=org_policy_bound; cue_family=520; treat_seen_by_one_viewer_as_universal=forbid; treat_missing_for_one_viewer_as_global_absence=forbid; cite_default=head; cite_condition_when=proving that profile-card identity detail varied by app and organization settings and should not be narrated as the route's universal source-identity wrapper state; promote_condition=no; basis=the same route remained current but the identity cue depended on viewer/app/organization configuration`

## Tie-breaker when reviewers ask “which capture should we trust?”

Ask four questions:
- did the same route/object still control,
- were the observations close enough in time that timing drift is not the main explanation,
- did the disagreement come from viewer conditions rather than from a different route or a click/expand interaction,
- and did the current office-controlled head actually change.

If the answer is that the head stayed stable and the main dispute is **which viewers could see which supportive cue state on the same route**, keep current control anchored elsewhere and use `590` only to preserve that viewer-conditionality fact.

## Promotion rule

Future media additions should usually **not** be promoted just because a supportive authenticity-adjacent cue was not viewer-universal.
Tighten `520`, `521`, `584`, `585`, `587`, `589`, or `590` first.
Only add another numbered surface when the archive proves that repeated same-route viewer-conditional cue mistakes still cause misrouting after this compact bridge exists.

## Minimal artifact

This document is intentionally doc-only.
Do **not** add a checklist or payload template for it unless viewer-conditional cue notes still drift after this compact bridge exists.
