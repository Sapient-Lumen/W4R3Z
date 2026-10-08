# 587 — Official voter-information platform media authenticity-cue lifecycle, timing drift, and non-retroactive inference firewall

**Track:** Shared / Public surfaces

This document defines a bounded control for **the same official voter-information media route when supportive authenticity-adjacent cues appear, disappear, expire, are revoked, or are backfilled over time and later readers start treating one observed cue state as timeless proof about the route**:
source-identity cues such as bylines, handles, badges, uploader cards, and profile names,
platform context/policy wrappers such as election panels, publisher-context boxes, disclosure labels, ratings, sensitivity cues, and protection banners,
and provenance/origin-history signals such as Content Credentials / C2PA disclosures, “How this content was made,” “captured with a camera,” or similar metadata-backed indicators.

It does not create a new authenticity timeline.
It adds one narrow rule:
**when supportive authenticity-adjacent cues on the same official media route change over time, the archive should preserve that cue lifecycle as a timestamped observation rather than quietly treating one momentary cue state as the route’s permanent proof of authority, currentness, or falsity.**

It composes with:
- `docs/194-synthetic-media-and-comms-authenticity-minimum-controls.md`
- `docs/203-official-channel-directory-as-evidence.md`
- `docs/305-election-office-contact-directories-office-hours-and-change-notices-as-evidence-surfaces.md`
- `docs/369-official-voter-information-videos-livestreams-and-clip-context-discipline.md`
- `docs/515-official-voter-information-platform-processing-pending-optimization-and-not-yet-fully-ready-media-surface-authority-boundary-discipline.md`
- `docs/520-official-voter-information-platform-channel-bylines-profile-names-handles-verification-badges-and-source-identity-wrapper-authority-boundary-discipline.md`
- `docs/521-official-voter-information-platform-information-panels-context-boxes-disclosure-labels-and-policy-wrapper-authority-boundary-discipline.md`
- `docs/523-official-voter-information-platform-media-boundary-quickmap-and-duplicate-firewall.md`
- `docs/529-official-voter-information-platform-media-chain-heads-current-control-and-closeout-discipline.md`
- `docs/530-official-voter-information-platform-media-chain-citations-head-first-reference-and-historical-leg-scoping-discipline.md`
- `docs/583-official-voter-information-platform-media-stacked-authenticity-cues-identity-context-provenance-ordering-and-non-collapse-firewall.md`
- `docs/584-official-voter-information-platform-media-provenance-signals-content-credentials-and-non-substitutive-authenticity-discipline.md`
- `docs/585-official-voter-information-platform-media-authenticity-cue-transport-cross-route-divergence-and-absence-non-inference-firewall.md`
- `docs/586-official-voter-information-platform-media-authenticity-cue-tension-aspect-separation-and-non-cancellation-firewall.md`
- `docs/588-official-voter-information-platform-media-authenticity-cue-attachment-points-scope-boundaries-and-non-inheritance-firewall.md`
- `docs/589-official-voter-information-platform-media-authenticity-cue-inspection-gates-expanded-details-and-non-ambient-visibility-firewall.md`
- `docs/590-official-voter-information-platform-media-authenticity-cue-viewer-state-variance-eligibility-conditions-and-non-universality-firewall.md`
- `docs/591-official-voter-information-platform-media-authenticity-cue-observation-assembly-cross-state-composites-and-no-faux-single-state-firewall.md`

## Why this exists (bounded)

The archive already distinguishes:
`520` for source identity,
`521` for context/policy wrappers,
`583` for same-route stacking,
`584` for provenance signals,
`585` for cross-route cue transport,
and `586` for same-route cue tension.
A smaller but still important seam remains:
**the same route can show different supportive authenticity-adjacent cue states at different times, and later readers can start using one captured moment as if it retroactively or permanently settled what the route proved.**

Current primary-source guidance is specific enough to justify a compact bridge.
YouTube’s current verified-channel help says verification distinguishes an official channel from similar names, is not an endorsement, stays verified unless the channel name changes, and can also be revoked for policy or Terms-of-Service reasons.
Its current election-information help says election-related features are only available during election cycles in limited countries/regions, may vary by election cycle, and election-results panels will stop surfacing after elections conclude.
Its current “How this content was made” help says disclosures can arise from creator disclosure, YouTube generative-AI tools, or valid Content Credentials data, and may show in the player or description.
Its current altered/synthetic disclosure help says YouTube may proactively apply a label that creators cannot remove and that some viewer-facing disclosure placements are currently limited to mobile devices or tablets, with more prominent player labels possible for sensitive topics including elections.
Its current “captured with a camera” help says the disclosure requires compatible C2PA-enabled capture, can be broken by later handling or unsupported edits, and missing disclosure does not prove the content was altered.
The current C2PA FAQ says metadata may be stripped from media and that associated Content Credentials can sometimes be rediscovered through durable bindings.
(xref: `youtube_verified_channels_help_page`; xref: `youtube_election_information_panels_help_page`; xref: `youtube_how_this_content_was_made_disclosures_help_page`; xref: `youtube_altered_synthetic_content_disclosures_help_page`; xref: `youtube_captured_with_a_camera_disclosure_help_page`; xref: `c2pa_faq_page`)

So the bounded question is not whether these cues are useful.
They often are.
The bounded question is smaller:
**when one official media route shows a badge, panel, disclosure, or provenance indicator at one time and not at another, does the archive start treating that observed cue state like timeless proof rather than a dated observation about a supportive cue?**

## This is not the same thing as `515`, `520`, `521`, `583`, `584`, `585`, or `586`

`515` asks whether the media surface is still processing, pending, or otherwise not fully ready.

`520` asks whether identity cues start acting like the whole proof that a route is official or current.

`521` asks whether context/policy wrappers start acting like the whole explanation of authority, currentness, or legal effect.

`583` asks whether several supportive cue families stacked on the same route started acting like compound proof.

`584` asks whether provenance/origin-history signals started acting like the whole proof of authenticity or current authority.

`585` asks whether supportive cues were preserved or stripped differently across routes and wrappers.

`586` asks whether same-route supportive cues were wrongly treated as cancelling one another.

`587` asks a different question:
**when the same route’s supportive cue state changes over time, how should the archive preserve that lifecycle without letting one observation retroactively rewrite the route’s whole authenticity history?**

If one cue family clearly governs, use that family doc.
If the harder problem is mere same-route co-presence, use `583`.
If the harder problem is cross-route divergence, use `585`.
If the harder problem is cue attachment-point scope rather than timing drift, use `588`.
If the harder problem is same-route non-cancellation, use `586`.
If the harder problem is same-route discoverability — ambient versus inspectable detail on the same route — use `589`.
If the harder problem is same-route viewer conditionality — different viewers saw different cue states because of bounded viewer conditions — use `590`.
If the harder problem is not timing drift itself but a later note, deck, or screenshot set fused observations from different times, routes, viewers, or interaction states into one faux simultaneous posture, use `591`.
Use `587` only when the decisive fact is that **cue timing on the same route changed what later readers thought the route proved because they overread one observation as permanent, original, or retroactive.**

## Default rule: keep current control with the head; timestamp the cue observation; forbid retroactive inference

By default, later notes SHOULD still cite the current controlling head under `530`, or the fallback anchor if the chain is headless.
A cue-lifecycle note exists only to explain one bounded timing problem around that head.

Use this triage order:
1. if the decisive claim is really about source identity, use `520`;
2. if the decisive claim is really about a context/policy wrapper, use `521`;
3. if the decisive claim is really about provenance/origin-history signaling, use `584`;
4. if the decisive claim is that several supportive cues merely stacked and cumulatively over-signaled trust, use `583`;
5. if the decisive claim is that a route or wrapper change altered which cues were visible, use `585`;
6. if the decisive claim is that reviewers were inheriting a cue to the wrong object or wrapper scope, use `588`;
7. if the decisive claim is that same-route cues were treated as cancelling one another, use `586`;
8. if the decisive claim is that different viewers on the same route saw different cue states because of bounded viewer conditions, use `590`;
9. use `587` only when the decisive claim is that **one same-route cue state was later overread as timeless rather than time-bound**.

This means `587` is not a new preferred citation lane.
It is a compact bridge for cases where a badge, panel, disclosure, or provenance indicator on the same route changed over time and later readers forgot the observation itself had a date.

## Keep cue observation time distinct from current office control

At minimum, keep these layers separate:
1. **current office control** — whether the office’s written/help lane and the current media head still control (`194`, `369`, `529`, `530`);
2. **cue family** — whether the observed change belongs mainly to identity (`520`), context/policy (`521`), provenance (`584`), or a mixed bundle (`583`/`586`);
3. **observation time** — when the cue state was actually seen on that route;
4. **lifecycle cause** — rename/revocation, cycle expiry, platform-applied disclosure, handling breakage, durable rediscovery, or unknown;
5. **retroactive inference ban** — no single observed cue state silently rewrites earlier or later route state unless separately evidenced.

That separation matters because the public can easily do informal time collapse:
- an old verified badge screenshot can be overread as if the badge persisted after a rename or revocation,
- an election information panel can be overread as if it should still exist after the election-cycle window closes,
- a newly surfaced disclosure can be overread as if it was always present,
- and a later missing provenance cue can be overread as proof that the underlying media was always suspicious.

`587` exists to stop that time collapse from turning into archive logic.

## Minimal cue-lifecycle note grammar

When same-route cue timing itself matters, reviewers SHOULD prefer one compact line in this shape:

`head=<current tuple|none>; cue_lifecycle_state=<revoked_or_renamed|cycle_expired|platform_applied_or_backfilled|device_scoped_visibility|handling_broken_or_stripped|durably_rediscovered|mixed_or_unknown>; cue_family=<520|521|584|mixed>; observation_time=<timestamp or bounded window>; retroactive_inference=<forbid>; cite_default=<head|fallback anchor>; cite_lifecycle_when=<claim about same-route cue timing>; promote_lifecycle=<no>; basis=<why the cue lifecycle mattered without becoming a new proof object>`

This is a note contract, not a new schema.
It exists so packet notes can say “this supportive cue state changed on the same route over time” without minting a new head, a new evidence kind, or a permanent authenticity status.

## Typical uses

1. **Identity cue changed later**
   The same head still controls, but a verified badge or related source-identity cue later disappeared because the channel name changed or platform status changed, and old captures are being cited as if the earlier cue state persisted indefinitely.
2. **Cycle-bound context panel expired**
   The same head still controls, but an election panel or similar context wrapper later stopped surfacing after the election-cycle window ended, and the earlier panel presence is being treated like a permanent property of the route.
3. **Disclosure later appears or gains salience**
   The same head still controls, but a creator/platform disclosure later becomes visible or more prominent on the same route, and later readers start projecting that cue backward as if it was always there.
4. **Provenance later breaks or is rediscovered**
   The same head still controls, but later handling strips or suppresses provenance visibility, or durable binding helps rediscover an associated credential, and observers start treating that later state as if it settled the route’s whole history.

## When not to use this

Do **not** use `587` when:
- only one of `520`, `521`, or `584` matters and there is no bounded timing problem;
- the real issue is simply that several supportive cues appeared together — use `583`;
- the real issue is that supportive cues traveled unevenly across routes — use `585`;
- the real issue is that same-route cues were speaking to different aspects and wrongly cancelling one another — use `586`;
- the decisive issue is still the media object’s date, scope, currentness, or correction status — use `369`/`529`/`530`;
- or the only reason to cite `587` is general unease about platform mutability without a specific same-route timing claim.

If deleting the timing fact would erase **why one cue observation was being overread as timeless**, `587` is probably right.
If deleting that timing fact would still leave a plain single-family claim, a stacked-cues claim, a route-transport claim, or a same-route tension claim, use the narrower doc and omit `587`.

## Examples

- `head=county_board_watch_packet; cue_lifecycle_state=revoked_or_renamed; cue_family=520; observation_time=2026-03-23T14:10Z/2026-03-23T18:20Z; retroactive_inference=forbid; cite_default=head; cite_lifecycle_when=proving that an earlier verified-channel screenshot should not be cited as if the same badge necessarily persisted after a later channel-name change; promote_lifecycle=no; basis=identity cue state changed on the same route over time`
- `head=state_results_replay_packet; cue_lifecycle_state=cycle_expired; cue_family=521; observation_time=2026-11-05/2026-12-01; retroactive_inference=forbid; cite_default=head; cite_lifecycle_when=proving that an election-results panel visible during the cycle should not be cited as a permanent route property after the panel window closed; promote_lifecycle=no; basis=context wrapper timing mattered more than route identity`
- `head=town_hall_archive_packet; cue_lifecycle_state=handling_broken_or_stripped; cue_family=584; observation_time=2026-03-23T16:00Z/2026-03-24T09:00Z; retroactive_inference=forbid; cite_default=head; cite_lifecycle_when=proving that later missing camera/provenance cues after ordinary handling should not be cited as proof that the earlier route never carried provenance support; promote_lifecycle=no; basis=provenance visibility changed over time on the same route`

## Tie-breaker when reviewers ask “which cue state is the real one?”

Ask four questions:
- which state is actually observed and when,
- whether the underlying office-controlled media object or written/help head changed,
- whether the cue change is identity, context/policy, provenance, or mixed,
- and whether the later claim really needs a timing fact or is just overreading a support cue.

If the answer is that the head stayed stable and only the supportive cue state changed over time, **the real rule is to preserve the dated observation and forbid retroactive inference**.
Keep current control anchored elsewhere and use `587` only to preserve that cue lifecycle.

## Promotion rule

Future media additions should usually **not** be promoted just because supportive authenticity-adjacent cues changed over time on the same route.
Tighten `520`, `521`, `583`, `584`, `585`, `586`, or `587` first.
Only add another numbered surface when the archive proves that one narrower cue family or one narrower route class still causes repeated misrouting after this lifecycle bridge exists.

## Minimal artifact

This document is intentionally doc-only.
Do **not** add a checklist or payload template for it unless same-route cue-lifecycle notes still drift after this compact bridge exists.
