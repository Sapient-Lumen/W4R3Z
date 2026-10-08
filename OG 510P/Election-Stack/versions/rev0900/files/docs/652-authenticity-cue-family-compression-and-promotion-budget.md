# 652. Authenticity-cue family compression and promotion budget

**Track:** Shared / Public surfaces

This document is a **maintainer compression rule** for the official-voter-information platform-media authenticity-cue family, especially the recent `584–651` run of wrapper-state, detached-derivative, and non-governing packet-state firewalls. It is not a new voter-facing evidence surface, schema, checklist, or template.

The useful invariant in that family is now stable enough to state once: a later viewer, wrapper, packet, platform, or derivative state can be worth recording, but it does not become the authoritative source, governing member, current official answer, publication chronology, or provenance proof for the underlying official media route. C2PA and Content Credentials material remains useful as a compact provenance vocabulary; platform disclosure and camera-capture labels remain useful as observed cues; playback, loop, embed, and replay settings remain useful as viewer-state observations. None of those cue layers should be inflated into a substitute for the current official-public route or the signed evidence member that governs the packet. (xref: `c2pa_content_credentials_spec_2_4_html`; xref: `c2pa_faq_page`; xref: `youtube_how_this_content_was_made_disclosures_help_page`; xref: `youtube_captured_with_a_camera_disclosure_help_page`; xref: `youtube_loop_videos_playlists_help_page`; xref: `vimeo_autoplay_loop_embed_code_help_page`)

## Family invariant

For this family, a packet note should separate five roles before adding prose:

1. **Governing member:** the signed, current, route-level, or source-level member that controls the claim.
2. **Observed cue:** the authenticity, capture, platform, player, or wrapper cue that was actually visible.
3. **Wrapper or derivative carrier:** the later slide, PDF, email, chat export, preview shell, transcript, still, locator, replay control, or other carrier in which the cue was observed.
4. **Non-inference:** the thing the cue must not be used to prove, such as source authority, currentness, chronology, official repetition, endorsement, native provenance, or member scope.
5. **Escalation lane:** the existing doc, registry row, checklist bullet, or note grammar that already covers the case.

When those roles can be named, add the narrowest artifact that preserves the observation. Do not mint a sibling doc simply because a new app, viewer state, exported wrapper, label shape, replay condition, or presentation surface appears.

## Promotion budget for future sibling docs

A future numbered doc in this family should clear all four gates:

- **New governing distinction:** the case cannot be stated as `head + governing_member + wrapper_kind + observed_cue + non_inference` without losing a materially different verifier decision.
- **Source anchor floor:** the case has at least two lock-backed public source anchors or official/platform documentation anchors that make the distinction concrete.
- **Verifier consequence:** the distinction changes packet review, problem-code routing, evidence-object interpretation, or public explanation, rather than only adding another UI adjective.
- **Compression offset:** the change also removes, merges, or family-routes at least one near-duplicate note, checklist bullet, or prospective sibling.

If a case misses one of those gates, route it into an existing family doc (`584`, `600`, `651`), a registry row, a problem-code note, or a checklist sentence.

## Preferred note grammar

Use a single compact note before adding a new document:

`cue_family=<family>; governing_member=<member-or-route>; wrapper_kind=<viewer-or-packet-state>; observed_cue=<cue>; non_inference=<authority|currentness|chronology|provenance|member_scope|official_repetition>; basis=<member-digest-or-capture-id>`

Example shape, with placeholders only:

`cue_family=platform_media_authenticity; governing_member=media_route_head; wrapper_kind=looping_embed_view; observed_cue=repeat_one_control_visible; non_inference=official_repetition; basis=<capture-digest>`

## Brainstorm backlog that should not promote yet

Keep these as backlog labels unless one clears the promotion budget:

- account-personalized trust badges, subscription markers, or login-only platform UI;
- browser or operating-system safe-browsing overlays near official media;
- accessibility-generated summaries, live captions, translations, or audio descriptions that restate an official media object;
- moderation, takedown, age-gate, geo-restriction, or processing-delay labels around an otherwise known official route;
- certificate-chain, secure-enclave, watermark, or camera-capture UI that is present only as a surrounding platform cue.

Those are valuable observations, but the archive already has the machinery to preserve them without turning each wrapper into a separate authority surface.

## Release-gate proposal

A future gate can detect long runs of new `platform-media-authenticity-cue` sibling docs and require a family-compression note when more than a small number are added without a new schema, verifier behavior, or registry row. The gate should warn, not block, until the family map is stable enough to avoid false positives.

## Sources and internal anchors

- C2PA / Content Credentials provenance vocabulary and background (xref: `c2pa_content_credentials_spec_2_4_html`; xref: `c2pa_faq_page`)
- YouTube / platform disclosure and camera-capture cue examples (xref: `youtube_how_this_content_was_made_disclosures_help_page`; xref: `youtube_captured_with_a_camera_disclosure_help_page`)
- Platform loop / embed state examples for repeat-state boundaries (xref: `youtube_loop_videos_playlists_help_page`; xref: `vimeo_autoplay_loop_embed_code_help_page`)
- Internal family anchors: `docs/227-refactor-and-growth-protocol.md`, `docs/584-official-voter-information-platform-media-provenance-signals-content-credentials-and-non-substitutive-authenticity-discipline.md`, `docs/600-official-voter-information-platform-media-authenticity-cue-detached-derivative-family-quickmap-mixed-packets-and-anti-fragmentation-firewall.md`, and `docs/651-official-voter-information-platform-media-authenticity-cue-packet-loop-repeat-replay-cycling-and-non-governing-wrapper-repeat-state-firewall.md`
