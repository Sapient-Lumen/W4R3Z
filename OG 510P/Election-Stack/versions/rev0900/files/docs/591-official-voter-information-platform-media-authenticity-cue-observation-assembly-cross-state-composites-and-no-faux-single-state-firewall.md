# 591 — Official voter-information platform media authenticity-cue observation assembly, cross-state composites, and no-faux-single-state firewall

**Track:** Shared / Public surfaces

This document defines a bounded control for **later notes, packets, screenshots, decks, or summaries that assemble several authenticity-adjacent cue observations into one apparent “single state” even though those observations actually came from different routes, times, viewer conditions, or interaction states around the same official media object**.

It does not add a new authenticity cue family.
It adds one narrow rule:
**when later materials combine supportive authenticity-adjacent cue observations from different states, the archive should preserve that assembly honestly without narrating the result as one simultaneously witnessed page posture.**

It composes with:
- `docs/194-synthetic-media-and-comms-authenticity-minimum-controls.md`
- `docs/223-public-surface-capture-notes-and-reproducibility.md`
- `docs/227-refactor-and-growth-protocol.md`
- `docs/369-official-voter-information-videos-livestreams-and-clip-context-discipline.md`
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
- `docs/590-official-voter-information-platform-media-authenticity-cue-viewer-state-variance-eligibility-conditions-and-non-universality-firewall.md`
- `docs/592-official-voter-information-platform-media-authenticity-cue-preview-shells-open-target-separation-and-noninheritance-firewall.md`
- `docs/593-official-voter-information-platform-media-authenticity-cue-player-state-occlusion-reduced-context-suppression-and-non-absence-inference-firewall.md`
- `docs/595-official-voter-information-platform-media-authenticity-cue-text-extracts-transcript-caption-ocr-derivatives-and-non-carried-cue-firewall.md`

## Why this exists (bounded)

The archive now has compact controls for stacked supportive cues on one route (`583`), cross-route cue transport drift (`585`), same-route aspect tension (`586`), cue timing drift (`587`), attachment/scope errors (`588`), interaction-gated discoverability (`589`), and same-route viewer-conditionality (`590`).
A smaller but still important seam remains:
**later notes can silently fuse observations from those different states into one apparent “single page state,” even when nobody actually witnessed all of those cues together at once.**

Current official guidance is enough to justify that bounded bridge.
YouTube verification is an identity cue, election/context panels are route/context cues, and “How this content was made” / “captured with a camera” disclosures are provenance/origin-history cues rather than a universal truth verdict.
Microsoft profile-card detail can vary by app and configuration.
C2PA likewise describes Content Credentials as provenance/history structures that can travel, disappear, or later be rediscovered through durable bindings rather than as a guarantee that every viewing state will expose the same cue posture.
(xref: `youtube_verified_channels_help_page`; xref: `youtube_election_information_panels_help_page`; xref: `youtube_how_this_content_was_made_disclosures_help_page`; xref: `microsoft_profile_cards_m365_help_page`; xref: `c2pa_content_credentials_spec_2_4_html`)

That means a later composite can be assembled from:
- a route where an identity cue was visible,
- another route where a context panel was visible,
- a later time when a provenance cue appeared,
- a different viewer state,
- or an expanded-details capture,

and then retold as if one observer saw all of that on one stable route at one stable time.
`591` exists to stop that faux single-state compression.

## This is not the same thing as `583`, `585`, `587`, `589`, or `590`

`583` asks whether several supportive cue families were genuinely co-present on the same route and started acting like compound proof.

`585` asks whether supportive cues traveled unevenly across different routes, wrappers, embeds, mirrors, or file-style legs.

`587` asks whether one same-route cue state later changed over time and then got overread as timeless.

`589` asks whether the same viewer needed to expand, click, tap, hover, or open details to discover the cue on the same route.

`590` asks whether different viewers on the same route and in roughly the same time window saw different cue states because of bounded viewer conditions.

`592` asks whether a preview-bearing shell and an opened target were later treated as if they shared one cue posture even without a broader cross-state composite.

`595` asks whether later evidence preserved only text extracted from one state and then got overread as if that text derivative carried the route's surrounding authenticity-cue posture.

`591` asks a different question:
**did later notes, packets, or screenshots assemble observations from two or more of those states and then narrate that assembly as if it were one simultaneously witnessed route posture?**

If the real problem is simply route drift, use `585`.
If the real problem is simply cue timing drift, use `587`.
If the real problem is simply click/expand discoverability, use `589`.
If the real problem is simply a partial screenshot or crop being overread as route-total posture, use `594`.
If the real problem is simply viewer-conditionality, use `590`.
If the real problem is simply preview-shell versus opened-target inheritance without a broader composite, use `592`.
If the real problem is simply reduced-context player-state occlusion of surrounding authenticity-adjacent cues without a broader cross-state composite, use `593`.
Use `591` only when the archive needs one bounded sentence saying that **the later narrative is a composite assembly rather than a single-state observation.**

## Default rule: keep current control with the head; label assembly state honestly

By default, later notes SHOULD still cite the current controlling head under `530`, or the fallback anchor if the chain is headless.
An observation-assembly note exists only to explain one bounded cross-state-composite problem around that head.

Use this triage order:
1. if one cue family clearly governs, use that family doc;
2. if the decisive claim is that several supportive cues genuinely coexisted on one route, use `583`;
3. if the decisive claim is that the cues came from different routes, use `585`;
4. if the decisive claim is that the cues came from different times on the same route, use `587`;
5. if the decisive claim is that the cues came from expanded/clicked/hovered details, use `589`;
6. if the decisive claim is that one observation was only a partial screenshot or crop of the same route, use `594`;
7. if the decisive claim is that the cues came from different viewers or eligibility states, use `590`;
8. use `591` only when the decisive claim is that **later retelling assembled those distinct observations into one faux simultaneous state.**

This means `591` is not a new preferred citation lane.
It is a compact bridge for cases where reviewers need to say, in one honest sentence, that a later composite posture was **assembled across states rather than witnessed as one state**.

## Keep state dimensions separate before narrating cue posture

At minimum, keep these dimensions separate:
1. **current office control** — the current written/help lane and current media head (`194`, `369`, `529`, `530`);
2. **cue family and attachment** — identity, context/policy, provenance, and which object each cue belongs to (`520`, `521`, `584`, `588`);
3. **route state** — whether the route leg stayed the same (`585`);
4. **time state** — whether the observation time stayed the same (`587`);
5. **interaction state** — whether the viewer had to expand/click/hover/details-inspect (`589`);
6. **viewer state** — whether the cue depended on country/region, language, device/app, or organization settings (`590`);
7. **assembly state** — whether the later summary is a single observation or a cross-state composite (`591`).

That separation matters because later materials can otherwise make two opposite mistakes:
- compressing several real observations into one fake simultaneous state, or
- discarding a useful composite altogether because it was not a single-state capture.

`591` exists so the archive can preserve the composite **as a composite**.

## Minimal observation-assembly note grammar

When cross-state assembly itself matters, reviewers SHOULD prefer one compact line in this shape:

`head=<current tuple|none>; cue_assembly_state=<single_observation|cross_route_composite|cross_time_composite|cross_viewer_composite|cross_interaction_composite|mixed_or_unclear>; cue_family=<520|521|584|mixed>; treat_composite_as_single_state=<forbid>; cite_default=<head|fallback anchor>; cite_assembly_when=<claim that later narrative fused multiple states into one apparent cue posture>; promote_assembly=<no>; basis=<why the composite matters without recasting it as one witnessed state>`

This is a note contract, not a new schema.
It exists so packets and summaries can say “this was an assembled composite” without minting a new head, a new route, or a new authenticity verdict.

## Typical uses

1. **Cross-route composite**
   One later packet combines a native-route identity cue with an embed-route context panel and narrates both as one page posture.
2. **Cross-time composite**
   One later note combines an earlier no-provenance capture with a later provenance-disclosure capture and narrates the route as if both states were visible together.
3. **Cross-viewer composite**
   One later summary fuses a region-eligible viewer's panel capture with another viewer's no-panel capture and retells the result as one route state.
4. **Cross-interaction composite**
   One later deck combines first-paint route screenshots with expanded-description or hover-card details and narrates the cue posture as if all of it was ambient on first load.
5. **Mixed or unclear composite**
   Later materials clearly assemble several supportive cues into one posture, but the exact state boundaries are not all recoverable; `591` preserves that uncertainty instead of flattening it.

## When not to use this

Do **not** use `591` when:
- a single route/time/viewer/interaction state was actually observed and the note can simply stay in `583`, `585`, `587`, `589`, or `590`;
- the decisive question is still just which cue family or attachment point governs (`520`, `521`, `584`, `588`);
- the issue is ordinary head/currentness/correction/citation scoping (`369`, `529`, `530`);
- or the composite itself is not doing argumentative work and can be dropped without changing the meaning.

If deleting the assembly fact would erase **why the later narrative sounds stronger or more simultaneous than any one observation actually was**, `591` is probably right.
If deleting that fact would leave an ordinary same-route stack, transport drift, timing drift, inspection-gate, partial-window overread, or viewer-conditionality claim, use the narrower doc and omit `591`.

## Examples

- `head=state_board_results_watch_packet; cue_assembly_state=cross_route_composite; cue_family=mixed; treat_composite_as_single_state=forbid; cite_default=head; cite_assembly_when=proving that a later memo fused a native watch-page badge capture with an embedded-player disclosure capture into one apparent route posture; promote_assembly=no; basis=the composite preserved real observations but no single state showed all cues together`
- `head=county_clerk_archive_stream_packet; cue_assembly_state=cross_time_composite; cue_family=584; treat_composite_as_single_state=forbid; cite_default=head; cite_assembly_when=proving that a later summary combined an earlier no-disclosure capture with a later provenance disclosure and should not be narrated as one simultaneous state; promote_assembly=no; basis=the route stayed stable but the cue posture changed over time`
- `head=clerk_sharepoint_recording_packet; cue_assembly_state=cross_interaction_composite; cue_family=520; treat_composite_as_single_state=forbid; cite_default=head; cite_assembly_when=proving that a slide deck combined first-paint route captures with click-open profile-card details and should not be retold as if every identity cue was ambient; promote_assembly=no; basis=the later packet assembled route and inspected states into one stronger narrative`

## Promotion rule

Future media additions should usually **not** be promoted just because later summaries assembled several authenticity-adjacent cue observations into one stronger-looking posture.
Tighten `583`, `585`, `587`, `589`, `590`, or `591` first.
Only add another numbered surface when repeated misrouting still survives after this compact non-simultaneity control exists.

## Minimal artifact

This document is intentionally doc-only.
Do **not** add a checklist or payload template for it unless cross-state cue assembly still drifts after this compact bridge exists.
