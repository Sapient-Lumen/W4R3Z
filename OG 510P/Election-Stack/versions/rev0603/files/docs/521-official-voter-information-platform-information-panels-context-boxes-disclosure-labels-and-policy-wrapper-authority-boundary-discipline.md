# 521 — Official voter-information platform information panels, context boxes, disclosure labels, and policy-wrapper authority-boundary discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **official voter-information media routes whose platform, player, file-hosting layer, or sharing shell adds context panels, disclosure labels, classification cues, or other policy wrappers that can start sounding like part of the office's controlling public answer**:
publisher-context panels,
topical or election information panels,
AI-generated or AI-enhanced disclosure labels,
content-rating or advertisement labels,
sensitivity/classification labels,
rights/protection banners,
and similar platform- or policy-supplied wrapper cues attached to the same official media route.

It does **not** ban those wrappers.
It adds one narrow control:
**when official voter-information media carries third-party context panels, policy labels, or classification/protection wrappers, those wrappers should stay visibly subordinate to the current written/help lane instead of quietly becoming the office's whole proof of currentness, legal effect, or safe next-step guidance.**

It composes with:
- `docs/369-official-voter-information-videos-livestreams-and-clip-context-discipline.md`
- `docs/499-official-voter-information-platform-ai-video-summaries-ask-this-video-and-answer-module-authority-boundary-discipline.md`
- `docs/510-official-voter-information-platform-search-results-homepage-recommendations-and-browse-feed-authority-boundary-discipline.md`
- `docs/512-official-voter-information-platform-unavailable-private-age-gated-region-blocked-and-playback-restricted-surface-authority-boundary-discipline.md`
- `docs/514-official-voter-information-platform-titles-descriptions-thumbnails-posters-and-metadata-wrapper-authority-boundary-discipline.md`
- `docs/520-official-voter-information-platform-channel-bylines-profile-names-handles-verification-badges-and-source-identity-wrapper-authority-boundary-discipline.md`
- `artifacts/checklists/official-voter-information-platform-context-policy-wrapper-surface-checklist.md`
- `artifacts/templates/official-voter-information-platform-context-policy-wrapper-surface-payload.json`

## Why this exists (bounded)

The archive already covers the recording lane itself (`369`), generated answer modules over the player (`499`), platform-ranked discovery (`510`), availability/restriction shells (`512`), mutable metadata wrappers (`514`), and surrounding source-identity wrappers (`520`).
A smaller but distinct seam still remains:
**the same official media route can carry platform-added context or policy wrappers that feel authoritative enough to displace the office's own current written/help lane, even when the wrapper is third-party-sourced, policy-driven, conditional, or only partially visible across routes.**

Current platform guidance is specific enough to justify a compact control here.
YouTube's current publisher-context help says some watch pages may show an information panel explaining how a news publisher is funded, linking to Wikipedia, and that the panel is based on Wikipedia and other independent third-party sources rather than being a comment by YouTube on the publisher's editorial direction.
Its topical-context help says some search or watch surfaces may show information panels sourced from independent third-party partners.
Its election-information help says voting, results, topic, candidate, and party panels may appear during election cycles, may link to vetted non-partisan third-party sources, and can vary by election, country, or search term.
Vimeo's current AI-disclosure help says realistic altered or synthetic media must be labeled and that the disclosure label can appear on the video page and in the embedded player, though embedded visibility can vary when the title is hidden.
Its content-ratings help says ratings inform viewers about the material, can affect discoverability, and in some regions unrated public videos or live events may require sign-in to watch.
Microsoft's current SharePoint video guidance says videos in Microsoft 365 are stored like ordinary files, its sharing guidance says sensitivity labels appear below an item's name and can be hovered to learn more, and its IRM help says rights-managed permissions are stored in the file itself.
(xref: `youtube_publisher_context_information_panel_help_page`; xref: `youtube_topical_context_information_panel_help_page`; xref: `youtube_election_information_panels_help_page`; xref: `vimeo_ai_generated_or_enhanced_disclosure_help_page`; xref: `vimeo_content_ratings_help_page`; xref: `microsoft_using_videos_sharepoint_pages_help_page`; xref: `microsoft_sharing_files_sensitivity_labels_help_page`; xref: `microsoft_open_restricted_permissions_file_help_page`)

So the bounded question is not “may a platform or policy layer add context or classification around official media?”
Of course it may.
The bounded question is smaller:
**once a platform context box, disclosure label, or protection/classification cue appears beside official election media, does that wrapper start sounding like the controlling answer, the official warning, or the definitive explanation of what the voter should do next?**

## This is not the same thing as AI answer modules, discovery ranking, restriction shells, metadata wrappers, or source identity wrappers

`499` asks whether **player-native AI summaries or question-answer modules over the already-open recording** begin acting like a shadow help desk.

`510` asks whether **platform search, recommendation, homepage, or browse surfaces** become the practical first-contact router before the voter opens the media route.

`512` asks whether **the route is blocked, private, age-gated, region-blocked, sign-in-gated, or otherwise presented as unavailable or restricted**.

`514` asks whether **titles, descriptions, thumbnails, posters, or other mutable metadata wrappers** begin acting like the controlling currentness claim or scope summary.

`520` asks whether **bylines, handles, badges, profile photos, creator URLs, uploader names, or profile cards** start sounding like the whole proof that the route is official and current.

`521` asks a different question:
**once the same media route carries platform-added context panels, disclosure labels, ratings, sensitivity cues, or protection banners, do those wrappers start sounding like the office's whole authoritative explanation of the route, its currentness, or the public's next step even though the wrapper may be third-party-sourced, policy-derived, or only conditionally visible?**

If the distinct problem is **the office or organizer itself can restyle the shell with banners, logos, colors, layout modes, trailers, latest-video substitutions, or hidden live-status cues and that presentation layer starts sounding like proof that the route is current, live, or newly authoritative**, use `522`.

A route can pass `499`, `510`, `512`, `514`, and `520` and still fail `521` if:
- an office assumes a YouTube election information panel makes the underlying recording self-sufficient without an explicit written/help recovery path;
- a Vimeo AI-generated disclosure label becomes the only visible qualification on an official clip and the office never reviews how the same clip appears when embedded elsewhere;
- a content-rating or sign-in implication is allowed to act like the office's entire public-access policy even though the current official written/help lane offers another lawful public route;
- a SharePoint-hosted video inherits a sensitivity label or file-protection wrapper that the public interprets as the office's full instruction about who should rely on the route;
- or a third-party context panel appears under one copied route but not another, and the office never reviews how that divergence affects the perceived authority of the media.

## Context and policy wrappers are not the office's whole answer

The public-safe posture is simple:
**platform-added context or policy wrappers are wrappers around one official media route; they are not the office's complete current instruction surface, superseding notice, or legal-effect statement.**

At minimum, keep these layers distinct:
1. the current written page, FAQ/help entry, official notice, or office contact that still controls action-changing next steps;
2. the underlying official recording, livestream, or file-hosted media route;
3. the platform- or policy-supplied wrapper, such as a topical context panel, election information panel, AI-generated label, mature-content rating, sensitivity label, or protection banner;
4. the upstream source or rule behind that wrapper, such as a third-party data partner, platform policy, or file-protection configuration;
5. and any separate recovery path the office provides when the wrapper changes access, visibility, or interpretation.

That distinction matters because wrapper cues feel explanatory.
A voter, journalist, or partner may infer that the wrapper itself means:
- this must be the current controlling answer,
- this warning or context text must have been written by the office,
- this label must explain the entire trust or access posture of the route,
- or this panel must substitute for checking the office's current written/help lane.

But the vendor documentation points the other way.
Some panels are sourced from third parties, some labels are policy-driven, some are automatically applied, and some appear differently across native pages, embeds, search results, or file-sharing flows.
For `521`, the bounded rule is simply to stop the archive from treating those wrappers as if they were self-explaining proof objects.

## Presence, absence, and visibility can vary by route, policy, and wrapper

YouTube says publisher-context panels are not shown in search results and may not be available in all countries/regions and languages.
Its election-information panels are limited to election cycles and vary by election, country/region, data partner, and search/query context.
Vimeo says AI-generated disclosure labels can appear on the video page and in the embed, but embedded visibility changes when the title is hidden, and its content-rating rules note that local regulations can affect whether unrated public content requires sign-in.
Microsoft says sensitivity labels appear in sharing flows and that permissions can be stored in the file itself, which matters because Microsoft 365 video routes can be ordinary file-hosted media rather than a wholly separate video-only surface.
(xref: `youtube_publisher_context_information_panel_help_page`; xref: `youtube_election_information_panels_help_page`; xref: `vimeo_ai_generated_or_enhanced_disclosure_help_page`; xref: `vimeo_content_ratings_help_page`; xref: `microsoft_sharing_files_sensitivity_labels_help_page`; xref: `microsoft_open_restricted_permissions_file_help_page`; xref: `microsoft_using_videos_sharepoint_pages_help_page`)

That means the same official media can present materially different wrapper state across:
- native watch pages,
- search-result contexts,
- embeds,
- file-sharing flows,
- page builders or collection wrappers,
- and copied or mirrored routes.

For `521`, offices should review whether the public could mistake the presence or absence of one wrapper for proof that the office changed the underlying answer, endorsed the wrapper's exact wording, or intentionally limited who should rely on the route.

## Keep wrapper provenance and recovery explicit

The office does not need to strip away platform context or policy labels.
It does need to prevent those wrappers from becoming a hidden authority shortcut.

For this narrow surface, that usually means:
- the office identifies whether the wrapper is office-authored, platform-authored, policy-generated, or third-party-sourced;
- the current written/help lane remains recoverable even when the wrapper looks self-sufficient;
- the office reviews native-page versus embed versus copied-route wrapper differences when those differences materially alter public understanding;
- and the office does not treat wrapper presence or absence as the whole proof that a route is current, official, or lawfully dispositive.

## Minimum review artifacts

For this surface, preserve bounded evidence of:
- the media route reviewed;
- the exact wrapper state shown there (for example context panel, label text, rating, sensitivity cue, or protection banner);
- whether the wrapper appeared to be office-authored, platform-authored, policy-generated, or third-party-sourced;
- whether the current written/help lane remained recoverable from that route;
- whether materially different wrapper states appeared across native, embedded, file-sharing, or copied routes;
- and when that review was last verified.

Prefer screenshots, route captures, and compact wrapper-state notes over partner telemetry, private moderation history, or internal policy console dumps.

## What good looks like

A public-safe route in this lane usually has these properties:
- the office can say what the wrapper is and is not — context aid, disclosure label, rating, classification cue, or restriction notice — without pretending it is the whole current answer;
- the current written/help lane remains reachable even if the wrapper sounds important or cautionary;
- native, embedded, and copied routes are reviewed when wrapper visibility materially changes;
- and later observers can distinguish the media object from the platform- or policy-supplied wrapper layered around it.

## Related artifacts

- Template payload: `artifacts/templates/official-voter-information-platform-context-policy-wrapper-surface-payload.json`
- Operator quickcheck: `artifacts/checklists/official-voter-information-platform-context-policy-wrapper-surface-checklist.md`

## Source pointers

- YouTube Help: Information panel providing publisher context (xref: `youtube_publisher_context_information_panel_help_page`)
- YouTube Help: Topical context in information panel (xref: `youtube_topical_context_information_panel_help_page`)
- YouTube Help: Election information panels (xref: `youtube_election_information_panels_help_page`)
- Vimeo Help Center: About disclosing videos as AI-generated or AI-enhanced (xref: `vimeo_ai_generated_or_enhanced_disclosure_help_page`)
- Vimeo Help Center: About content ratings (xref: `vimeo_content_ratings_help_page`)
- Microsoft Support: Using videos on SharePoint pages (xref: `microsoft_using_videos_sharepoint_pages_help_page`)
- Microsoft Support: Sharing files, folders, and list items (xref: `microsoft_sharing_files_sensitivity_labels_help_page`)
- Microsoft Support: Open a file that has restricted permissions (xref: `microsoft_open_restricted_permissions_file_help_page`)
