# 589 — Official voter-information platform media authenticity-cue inspection gates, expanded details, and non-ambient visibility firewall

**Track:** Shared / Public surfaces

This document defines a bounded control for **official voter-information media routes where a supportive authenticity-adjacent cue is available on the same route but only after a deliberate inspection step**:
expanded-description provenance sections,
click-through profile or owner cards,
hover-to-learn-more disclosures,
details panes,
and similar interaction-gated cue reveals that do not change the underlying controlling media object.

It does not create a new proof family.
It adds one narrow rule:
**when a supportive authenticity-adjacent cue is present on the same official media route but only after expand/click/tap/hover/details interaction, the archive should record that discoverability state and should not silently treat the cue as either ambient first-paint proof or route-level absence.**

It composes with:
- `docs/194-synthetic-media-and-comms-authenticity-minimum-controls.md`
- `docs/369-official-voter-information-videos-livestreams-and-clip-context-discipline.md`
- `docs/511-official-voter-information-platform-share-panels-copy-links-timestamp-links-and-embed-export-authority-boundary-discipline.md`
- `docs/520-official-voter-information-platform-channel-bylines-profile-names-handles-verification-badges-and-source-identity-wrapper-authority-boundary-discipline.md`
- `docs/521-official-voter-information-platform-information-panels-context-boxes-disclosure-labels-and-policy-wrapper-authority-boundary-discipline.md`
- `docs/523-official-voter-information-platform-media-boundary-quickmap-and-duplicate-firewall.md`
- `docs/530-official-voter-information-platform-media-chain-citations-head-first-reference-and-historical-leg-scoping-discipline.md`
- `docs/583-official-voter-information-platform-media-stacked-authenticity-cues-identity-context-provenance-ordering-and-non-collapse-firewall.md`
- `docs/584-official-voter-information-platform-media-provenance-signals-content-credentials-and-non-substitutive-authenticity-discipline.md`
- `docs/585-official-voter-information-platform-media-authenticity-cue-transport-cross-route-divergence-and-absence-non-inference-firewall.md`
- `docs/587-official-voter-information-platform-media-authenticity-cue-lifecycle-timing-drift-and-non-retroactive-inference-firewall.md`
- `docs/588-official-voter-information-platform-media-authenticity-cue-attachment-points-scope-boundaries-and-non-inheritance-firewall.md`
- `docs/590-official-voter-information-platform-media-authenticity-cue-viewer-state-variance-eligibility-conditions-and-non-universality-firewall.md`
- `docs/591-official-voter-information-platform-media-authenticity-cue-observation-assembly-cross-state-composites-and-no-faux-single-state-firewall.md`
- `docs/593-official-voter-information-platform-media-authenticity-cue-player-state-occlusion-reduced-context-suppression-and-non-absence-inference-firewall.md`

## Why this exists (bounded)

The archive already distinguishes source-identity cues (`520`), context/policy wrappers (`521`), provenance signals (`584`), same-route stacked authenticity cues (`583`), cross-route cue transport (`585`), same-route cue timing (`587`), and cue attachment scope (`588`).
A smaller ambiguity still remains:
**the same route can contain a supportive authenticity-adjacent cue that is real and same-route, but only after the viewer expands a description, clicks a name/photo, opens a card, or hovers for more details.**

Current primary-source guidance is specific enough to justify a compact bridge here.
YouTube's current “How this content was made” help says the information can be found in the video player or description and that the “How this content was made” section in the expanded video description provides further details.
Its current “Captured with a camera” help says that disclosure appears in the “How this content was made” section in the expanded description of some videos.
Vimeo's current profile-page help says a viewer reaches the profile page by clicking the profile photo shown on one of the creator's videos.
Microsoft's current profile-card help says viewers see a profile card by tapping a picture in Outlook mobile or by hovering or clicking a person's photo or name in other apps, and that some information may not display depending on organization settings.
Microsoft's current sharing-files help says sensitivity labels appear below an item's name after Share is opened and that a viewer can hover over the label to learn more.
(xref: `youtube_how_this_content_was_made_disclosures_help_page`; xref: `youtube_captured_with_a_camera_disclosure_help_page`; xref: `vimeo_manage_profile_page_help_page`; xref: `microsoft_profile_cards_m365_help_page`; xref: `microsoft_sharing_files_sensitivity_labels_help_page`)

That guidance is enough to support one bounded maintainer rule:
**same-route presence is not the same thing as ambient visibility.**
A cue can be real, relevant, and same-route while still requiring deliberate inspection.
That matters because later readers often work from screenshots, first-paint captures, or short narrative summaries.
Those habits can produce two opposite errors:
- treating an inspectable cue as if it were always visible and therefore stronger than it really was in the ordinary viewer experience,
- or treating “not visible in this first capture” as if the route lacked the cue altogether.

## This is not the same thing as `520`, `521`, `584`, `585`, `587`, or `588`

`520` asks whether source-identity cues start acting like the whole proof that a route is official or current.

`521` asks whether context/policy wrappers start acting like the whole explanation of authority, currentness, or legal effect.

`584` asks whether provenance/origin-history signals start acting like the whole proof of authenticity or current authority.

`585` asks whether supportive cues were preserved, suppressed, or stripped differently across routes, wrappers, or render paths.

`587` asks whether one same-route cue state later appeared, disappeared, expired, or was backfilled and then overread as timeless.

`588` asks which object or wrapper a supportive cue actually belonged to.

`589` asks a different question:
**on the same route, did the supportive cue require a deliberate interaction step to inspect, and are later readers now treating that same-route cue as if it were either ambient first-paint proof or absent because one capture did not show it?**

If one cue family clearly governs, use that family doc.
If the harder problem is same-route coexistence among several cue families, use `583`.
If the harder problem is cross-route divergence, use `585`.
If the harder problem is timing drift, use `587`.
If the harder problem is which object the cue belonged to, use `588`.
If the harder problem is that different viewers on the same route saw different cue states because of bounded viewer conditions rather than because one viewer failed to inspect, use `590`.
If the harder problem is not inspection gating itself but a later note, deck, or screenshot set fused first-paint and expanded-detail observations into one faux simultaneous posture, use `591`.
If the harder problem is not discoverability but the same current object entered a reduced-context player state that hid surrounding cues without changing the route, use `593`.
If the harder problem is not interaction gating at all but a later screenshot or crop preserved only part of the same route and got overread as route-total posture, use `594`.
Use `589` only when the decisive fact is that **discoverability on the same route was interaction-gated and later readers are overreading or underreading that gate.**

## Default rule: keep current control with the head; classify same-route cue discoverability

By default, later notes SHOULD still cite the current controlling head under `530`, or the fallback anchor if the chain is headless.
A discoverability note exists only to explain one bounded visibility problem around that head.

Use this triage order:
1. if the decisive claim is really about source identity, use `520`;
2. if the decisive claim is really about a context/policy wrapper, use `521`;
3. if the decisive claim is really about provenance/origin-history signaling, use `584`;
4. if the decisive claim is that several supportive cues stacked together and over-signaled trust, use `583`;
5. if the decisive claim is that supportive cues traveled unevenly across routes, use `585`;
6. if the decisive claim is that one observed same-route cue state was later overread as timeless, use `587`;
7. if the decisive claim is that the cue was inherited to the wrong object or wrapper, use `588`;
8. if the decisive claim is that different viewers on the same route saw different cue states because of bounded viewer conditions, use `590`;
9. if the decisive claim is that a later screenshot or crop preserved only part of the same route and got overread as total-route cue posture, use `594`;
10. use `589` only when the decisive claim is that **the cue was same-route but interaction-gated and later notes flattened that discoverability fact into ambient visibility or absence.**

This means `589` is not a new preferred citation lane.
It is a compact bridge for cases where the same route contained the cue, but ordinary first-glance viewing and later inspection were not the same experience.

## Keep attachment scope distinct from discoverability

At minimum, keep these layers separate:
1. **current office control** — the current written/help lane and the current media head (`194`, `369`, `529`, `530`);
2. **cue family and attachment** — whether the supportive cue belongs to source identity, a context/policy wrapper, or provenance, and which object or wrapper it actually belongs to (`520`, `521`, `584`, `588`);
3. **ambient first-paint view** — what a viewer could see without expanding or opening anything;
4. **inspection gate** — the expand/click/tap/hover/details action required to reach more cue information;
5. **expanded detail state** — what the viewer actually learned after taking that interaction step.

That separation matters because interfaces encourage overstatement:
- a first-paint screenshot can make an inspectable disclosure look absent,
- an expanded-description capture can make an inspectable provenance cue look ambient,
- a clicked profile card can make a same-route identity handoff look like it was always on the player surface,
- and a hover-only sensitivity explanation can get retold as if the full wrapper text was always plainly visible.

`589` exists to stop that discoverability inflation or erasure from turning into archive logic.

## Minimal discoverability note grammar

When same-route cue discoverability itself matters, reviewers SHOULD prefer one compact line in this shape:

`head=<current tuple|none>; cue_discovery_state=<ambient_on_route|expanded_description_only|click_or_tap_handoff|hover_or_details_pane_only|mixed_or_unclear>; cue_family=<520|521|584|mixed>; treat_inspectable_as_ambient=<forbid>; treat_not_first_paint_as_absent=<forbid>; cite_default=<head|fallback anchor>; cite_discovery_when=<claim about how the same-route cue was discoverable>; promote_discovery=<no>; basis=<why discoverability state mattered without creating a new proof object>`

This is a note contract, not a new schema.
It exists so packet notes can say “the cue was same-route but only inspectable after this interaction” without minting a new head, a new evidence kind, or a broader authenticity score.

## Typical uses

1. **Expanded-description provenance**
   The same head still controls, but a provenance disclosure or “captured with a camera” cue is being cited as if it were ambient on the player when the published help says the fuller detail lives in the expanded description.
2. **Click-through identity inspection**
   The same head still controls, but later readers are retelling a clicked profile page or profile card as if the full identity detail was always visible on the initial media shell.
3. **Hover/details-only wrapper meaning**
   The same head still controls, but a label or disclosure explanation is only available after hovering or opening a details/share pane and later notes are flattening that into plain first-paint visibility.
4. **First capture overread**
   The same head still controls, but a screenshot or first-glance capture that omitted the interaction step is being used as if it proved the cue was absent from the route altogether.

## When not to use this

Do **not** use `589` when:
- only one of `520`, `521`, or `584` matters and there is no discoverability mistake;
- the real issue is simply that several supportive cues appeared together — use `583`;
- the real issue is that supportive cues traveled unevenly across routes — use `585`;
- the real issue is that one cue state later appeared, disappeared, expired, or was backfilled on the same route — use `587`;
- the real issue is which object or wrapper the cue belonged to — use `588`;
- the real issue is that a later screenshot or crop preserved only part of the same route and got overread as route-total posture — use `594`;
- the real issue is that the viewer moved into a different media object or successor object — use `551`;
- or the decisive issue is still the media object's date, scope, currentness, or correction status — use `369`/`529`/`530`.

If deleting the inspection-gate fact would erase **why a cue was being overstated or understated on the same route**, `589` is probably right.
If deleting that fact would still leave an ordinary single-family claim, a same-route stacking claim, a transport claim, a timing claim, or an attachment-scope claim, use the narrower doc and omit `589`.

## Examples

- `head=county_board_stream_packet; cue_discovery_state=expanded_description_only; cue_family=584; treat_inspectable_as_ambient=forbid; treat_not_first_paint_as_absent=forbid; cite_default=head; cite_discovery_when=proving that a how-this-content-was-made disclosure existed on the same route but required expanded-description inspection rather than first-paint player visibility; promote_discovery=no; basis=the supportive cue was same-route and relevant, but its discoverability state was part of what later readers were overstating`
- `head=state_results_video_packet; cue_discovery_state=click_or_tap_handoff; cue_family=520; treat_inspectable_as_ambient=forbid; treat_not_first_paint_as_absent=forbid; cite_default=head; cite_discovery_when=proving that later readers were citing clicked profile-card details as if the whole identity posture was visible on the initial player shell; promote_discovery=no; basis=the same-route cue required a deliberate identity inspection step`
- `head=clerk_sharepoint_recording_packet; cue_discovery_state=hover_or_details_pane_only; cue_family=521; treat_inspectable_as_ambient=forbid; treat_not_first_paint_as_absent=forbid; cite_default=head; cite_discovery_when=proving that the sensitivity-label explanation required hover or share-pane inspection and should not be narrated as plain always-visible wrapper text; promote_discovery=no; basis=the same-route cue existed, but the interaction gate changed what an ordinary first capture could honestly prove`

## Tie-breaker when reviewers ask “was the cue really there?”

Ask four questions:
- did the same route actually contain the cue,
- what interaction step, if any, was required to reveal it,
- whether later notes are treating inspectable detail like ambient proof or treating one first-glance capture like route-level absence,
- and whether the current office-controlled head actually changed.

If the answer is that the head stayed stable and the main dispute is **how the viewer could discover the cue on the same route**, keep current control anchored elsewhere and use `589` only to preserve that discoverability fact.

## Promotion rule

Future media additions should usually **not** be promoted just because a supportive authenticity-adjacent cue required expansion, clicking, tapping, hovering, or a details pane.
Tighten `520`, `521`, `584`, `585`, `587`, `588`, or `589` first.
Only add another numbered surface when the archive proves that repeated same-route inspection-gate mistakes still cause misrouting after this compact bridge exists.

## Minimal artifact

This document is intentionally doc-only.
Do **not** add a checklist or payload template for it unless discoverability notes still drift after this compact bridge exists.
