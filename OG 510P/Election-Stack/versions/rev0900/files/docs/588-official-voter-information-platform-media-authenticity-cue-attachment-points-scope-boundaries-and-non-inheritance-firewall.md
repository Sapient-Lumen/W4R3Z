# 588 — Official voter-information platform media authenticity-cue attachment points, scope boundaries, and non-inheritance firewall

**Track:** Shared / Public surfaces

This document defines a bounded control for **official voter-information media routes where supportive authenticity-adjacent cues are visually near the same route but do not all attach to the same thing**:
channel/account identity cues,
route-local context/policy wrappers,
media-object or file-level provenance/origin-history signals,
derivative-local restatements,
and inspection handoffs that expose details about one of those layers.

It does not create a new proof family.
It adds one narrow rule:
**when supportive authenticity-adjacent cues are visually bundled around the same official media route, the archive should record which object each cue actually belongs to and should not silently inherit that cue across channel, route, object, sibling, or derivative boundaries without separate evidence.**

It composes with:
- `docs/194-synthetic-media-and-comms-authenticity-minimum-controls.md`
- `docs/203-official-channel-directory-as-evidence.md`
- `docs/305-election-office-contact-directories-office-hours-and-change-notices-as-evidence-surfaces.md`
- `docs/369-official-voter-information-videos-livestreams-and-clip-context-discipline.md`
- `docs/507-official-voter-information-platform-channel-home-featured-videos-playlists-and-collection-pages-authority-boundary-discipline.md`
- `docs/511-official-voter-information-platform-share-panels-copy-links-timestamp-links-and-embed-export-authority-boundary-discipline.md`
- `docs/520-official-voter-information-platform-channel-bylines-profile-names-handles-verification-badges-and-source-identity-wrapper-authority-boundary-discipline.md`
- `docs/521-official-voter-information-platform-information-panels-context-boxes-disclosure-labels-and-policy-wrapper-authority-boundary-discipline.md`
- `docs/523-official-voter-information-platform-media-boundary-quickmap-and-duplicate-firewall.md`
- `docs/530-official-voter-information-platform-media-chain-citations-head-first-reference-and-historical-leg-scoping-discipline.md`
- `docs/551-official-voter-information-platform-media-successor-object-handoffs-autoplay-queue-progression-and-head-noninheritance-discipline.md`
- `docs/583-official-voter-information-platform-media-stacked-authenticity-cues-identity-context-provenance-ordering-and-non-collapse-firewall.md`
- `docs/584-official-voter-information-platform-media-provenance-signals-content-credentials-and-non-substitutive-authenticity-discipline.md`
- `docs/585-official-voter-information-platform-media-authenticity-cue-transport-cross-route-divergence-and-absence-non-inference-firewall.md`
- `docs/586-official-voter-information-platform-media-authenticity-cue-tension-aspect-separation-and-non-cancellation-firewall.md`
- `docs/587-official-voter-information-platform-media-authenticity-cue-lifecycle-timing-drift-and-non-retroactive-inference-firewall.md`
- `docs/589-official-voter-information-platform-media-authenticity-cue-inspection-gates-expanded-details-and-non-ambient-visibility-firewall.md`
- `docs/590-official-voter-information-platform-media-authenticity-cue-viewer-state-variance-eligibility-conditions-and-non-universality-firewall.md`
- `docs/591-official-voter-information-platform-media-authenticity-cue-observation-assembly-cross-state-composites-and-no-faux-single-state-firewall.md`
- `docs/592-official-voter-information-platform-media-authenticity-cue-preview-shells-open-target-separation-and-noninheritance-firewall.md`
- `docs/593-official-voter-information-platform-media-authenticity-cue-player-state-occlusion-reduced-context-suppression-and-non-absence-inference-firewall.md`

## Why this exists (bounded)

The archive already distinguishes several supportive cue families one at a time and now also distinguishes same-route stacking (`583`), cross-route cue transport (`585`), same-route non-cancellation (`586`), and same-route cue lifecycle (`587`).
A smaller ambiguity still remains:
**the same watch page, file view, embed wrapper, or showcase can visually present several supportive cues at once even though one cue belongs to the channel/account, another belongs to the route context, and another belongs to the media object itself.**

Current primary-source guidance is specific enough to justify a compact bridge here.
YouTube’s current verified-channel help says a verification badge helps distinguish the official channel of a creator, brand, company, or public figure rather than endorsing every proposition around the route.
Its current publisher-context help says a publisher-context panel may be displayed on the watch page of videos on that channel.
Its current election-information help says election panels may show when you search for or watch election-related videos.
Its current “How this content was made” and “captured with a camera” help says those disclosures describe how a specific piece of content was made or whether compatible capture/provenance tooling was used for that content.
Vimeo’s current profile-page help says the profile page is what viewers see when they click the profile photo displayed on one of the creator’s videos, and its current showcase-customization help says profile pictures and profile names can be shown or hidden in showcase-specific views.
Microsoft’s current profile-card help says selecting a person’s name or picture opens a profile card with information about that person.
(xref: `youtube_verified_channels_help_page`; xref: `youtube_publisher_context_information_panel_help_page`; xref: `youtube_election_information_panels_help_page`; xref: `youtube_how_this_content_was_made_disclosures_help_page`; xref: `youtube_captured_with_a_camera_disclosure_help_page`; xref: `vimeo_manage_profile_page_help_page`; xref: `vimeo_customize_showcase_videos_help_page`; xref: `microsoft_profile_cards_m365_help_page`)

That current guidance is enough to support one bounded maintainer rule:
**visual adjacency is not the same thing as attachment scope.**
A channel badge can sit beside one video without becoming a property of every derivative.
A context panel can sit under one watch route without becoming a permanent property of the channel.
A provenance disclosure can describe one media object without becoming a channel-wide or sibling-object fact.

## This is not the same thing as `520`, `521`, `583`, `584`, `585`, `586`, `587`, or `551`

`520` asks whether source-identity cues start acting like the whole proof that a route is official or current.

`521` asks whether context/policy wrappers start acting like the whole explanation of authority, currentness, or legal effect.

`583` asks whether several supportive cue families stacked on the same route started acting like compound proof.

`584` asks whether provenance/origin-history signals started acting like the whole proof of authenticity or current authority.

`585` asks whether supportive cues were preserved or stripped differently across routes and wrappers.

`586` asks whether same-route supportive cues were wrongly treated as cancelling one another.

`587` asks whether one same-route cue state later appeared, disappeared, expired, or was backfilled and was then overread as timeless.

`551` asks whether autoplay, queueing, or another next-item mechanic moved the viewer into a different media object and reviewers then inherited the earlier head/currentness across objects.

`588` asks a different question:
**when supportive authenticity-adjacent cues are visually near the same official media route, which cue belongs to the channel/account, which belongs to the route context, which belongs to the media object or file, and which should be forbidden from silently inheriting to siblings, derivatives, or neighboring objects?**

If one cue family clearly governs, use that family doc.
If the harder problem is same-route coexistence, use `583`.
If the harder problem is cross-route transport divergence, use `585`.
If the harder problem is same-route non-cancellation, use `586`.
If the harder problem is same-route cue timing, use `587`.
If the harder problem is cross-object successor inheritance, use `551`.
If the harder problem is same-route discoverability — whether the cue was ambient or only inspectable after interaction — use `589`.
If the harder problem is same-route viewer conditionality — different viewers on the same route saw different cue states because of bounded viewer conditions — use `590`.
If the harder problem is not attachment scope itself but a later packet or summary fused observations from different routes, times, viewers, or interaction states into one apparent single-state posture, use `591`.
If the harder problem is that a search card, playlist row, queue slot, end-screen/info-card target, file tile, or similar preview shell was treated as if it shared one cue posture with the opened target, use `592`.
If the harder problem is not attachment scope but the same current object entered a reduced-context player state that hid surrounding cues, use `593`.
Use `588` only when the decisive fact is that **reviewers were reading a supportive cue as if it attached to a broader or different object than it actually did.**

## Default rule: keep current control with the head; classify cue attachment; forbid silent inheritance

By default, later notes SHOULD still cite the current controlling head under `530`, or the fallback anchor if the chain is headless.
An attachment-point note exists only to explain one bounded scope problem around that head.

Use this triage order:
1. if the decisive claim is really about source identity, use `520`;
2. if the decisive claim is really about a context/policy wrapper, use `521`;
3. if the decisive claim is really about provenance/origin-history signaling, use `584`;
4. if the decisive claim is that several supportive cues merely stacked and cumulatively over-signaled trust, use `583`;
5. if the decisive claim is that supportive cues traveled unevenly across routes, use `585`;
6. if the decisive claim is that same-route cues were wrongly treated as cancelling one another, use `586`;
7. if the decisive claim is that one observed same-route cue state was later overread as timeless, use `587`;
8. if the decisive claim is that a same-route cue required deliberate inspection and later notes flattened that into ambient visibility or absence, use `589`;
9. if the decisive claim is that different viewers on the same route saw different cue states because of bounded viewer conditions, use `590`;
10. use `588` only when the decisive claim is that **one supportive cue was inherited to the wrong scope or neighboring object.**

This means `588` is not a new preferred citation lane.
It is a compact bridge for the cases where a cue looked route-wide or channel-wide only because the interface bundled several objects together.

## Keep visual adjacency distinct from attachment scope

At minimum, keep these layers separate:
1. **current office control** — the current written/help lane and the current media head (`194`, `369`, `529`, `530`);
2. **channel/account shell** — byline, badge, handle, avatar, profile-card, or owner shell (`520`);
3. **route-context wrapper** — search/watch/share/embed/showcase/disclosure/policy wrapper (`521`, `511`, `507`);
4. **media object or file** — the actual recording, clip, or file-backed object plus any object-level provenance signal (`369`, `584`);
5. **derivative or adjacent object** — clips, screenshots, reuploads, sibling uploads, or neighboring items in a collection;
6. **inspection handoff** — the place where a viewer opens more details about one cue without changing which object that cue belongs to.

That separation matters because interfaces encourage over-inheritance:
- a verified uploader badge beside one video can look like proof that every nearby video, clip, or repost inherits the same status,
- an election or publisher panel under one watch route can look like a permanent property of the entire channel,
- a provenance disclosure on one media object can look like a statement about all sibling uploads,
- and a profile card or showcase-local identity display can look like a property of the file itself rather than one wrapper around it.

`588` exists to stop that scope inflation from turning into archive logic.

## Minimal attachment-point note grammar

When cue attachment scope itself matters, reviewers SHOULD prefer one compact line in this shape:

`head=<current tuple|none>; cue_attachment_state=<channel_or_account|route_or_wrapper|media_object_or_file|derivative_or_adjacent_object|inspection_handoff|mixed_or_unclear>; cue_family=<520|521|584|mixed>; inherit_across_boundaries=<forbid>; cite_default=<head|fallback anchor>; cite_attachment_when=<claim about which object the supportive cue actually belonged to>; promote_attachment=<no>; basis=<why attachment-point separation mattered without creating a new proof object>`

This is a note contract, not a new schema.
It exists so packet notes can say “this cue belonged to the channel, route, object, derivative, or inspection layer” without minting a new head, a new evidence kind, or a broader authenticity score.

## Typical uses

1. **Channel cue over-inherited to the object family**
   The same head still controls, but a byline, handle, badge, or profile card was read as if it attached to every sibling upload, excerpt, or repost instead of to the account shell.
2. **Route-context cue over-inherited to the channel**
   The same head still controls, but an election panel, publisher-context panel, or disclosure wrapper visible on one search/watch route was later cited as if it were a permanent property of the whole channel or all routes to the object.
3. **Object-level provenance over-inherited to neighbors**
   The same head still controls, but a provenance disclosure on one asset was later cited as if it described every derivative, sibling upload, or account-level identity state.
4. **Wrapper-local identity display mistaken for file/object truth**
   The same head still controls, but a showcase-local profile-name/photo display or a profile-card popover was later treated as if it were a file-level authenticity fact rather than one wrapper’s rendering choice.

## When not to use this

Do **not** use `588` when:
- only one of `520`, `521`, or `584` matters and there is no attachment-scope mistake;
- the real issue is simply that several supportive cues appeared together — use `583`;
- the real issue is that supportive cues traveled unevenly across routes — use `585`;
- the real issue is that same-route cues were speaking to different aspects and wrongly cancelling one another — use `586`;
- the real issue is that one cue state later appeared, disappeared, expired, or was backfilled on the same route — use `587`;
- the real issue is that the viewer was carried into a different media object and head/currentness was wrongly inherited there — use `551`;
- or the decisive issue is still the media object’s date, scope, currentness, or correction status — use `369`/`529`/`530`.

If deleting the attachment-point fact would erase **why one supportive cue was being inherited to the wrong object**, `588` is probably right.
If deleting that fact would still leave a plain single-family claim, a stacked-cues claim, a transport claim, a tension claim, a lifecycle claim, or a successor-object inheritance claim, use the narrower doc and omit `588`.

## Examples

- `head=county_board_video_packet; cue_attachment_state=channel_or_account; cue_family=520; inherit_across_boundaries=forbid; cite_default=head; cite_attachment_when=proving that a verified-channel badge beside one watch page should not be cited as if every clipped excerpt or neighboring upload inherited the same cue; promote_attachment=no; basis=the supportive cue belonged to the account shell rather than each adjacent object`
- `head=state_results_stream_packet; cue_attachment_state=route_or_wrapper; cue_family=521; inherit_across_boundaries=forbid; cite_default=head; cite_attachment_when=proving that an election-information panel shown under one watch/search route should not be cited as a permanent property of the whole channel or every derivative; promote_attachment=no; basis=the supportive cue belonged to the route context rather than the channel globally`
- `head=town_hall_recording_packet; cue_attachment_state=media_object_or_file; cue_family=584; inherit_across_boundaries=forbid; cite_default=head; cite_attachment_when=proving that a provenance disclosure on one asset should not be cited as if it automatically described sibling uploads or every repost; promote_attachment=no; basis=the supportive cue belonged to the object rather than the broader account shell`

## Tie-breaker when reviewers ask “what does this cue actually belong to?”

Ask four questions:
- what exact object or wrapper did the viewer have open,
- which cue family it belongs to,
- whether the cue is being inherited to a broader or neighboring scope without separate evidence,
- and whether the current office-controlled head actually changed.

If the answer is that the head stayed stable and the main dispute is **what object the supportive cue attached to**, keep current control anchored elsewhere and use `588` only to preserve that scope boundary.

## Promotion rule

Future media additions should usually **not** be promoted just because a supportive authenticity-adjacent cue looked broader than it really was.
Tighten `520`, `521`, `583`, `584`, `585`, `586`, `587`, or `588` first.
Only add another numbered surface when the archive proves that one narrower cue family or one narrower wrapper class still causes repeated misrouting after this attachment-point bridge exists.

## Minimal artifact

This document is intentionally doc-only.
Do **not** add a checklist or payload template for it unless attachment-point notes still drift after this compact bridge exists.
