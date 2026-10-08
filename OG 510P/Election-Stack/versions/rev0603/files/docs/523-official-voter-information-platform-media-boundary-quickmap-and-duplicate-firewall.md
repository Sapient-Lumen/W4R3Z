# 523 — Official voter-information platform media boundary quickmap and duplicate firewall

**Track:** Shared

This document turns the recent **official voter-information platform media stack** into a compact, maintainable neighbor map instead of a serial pile of almost-adjacent additions.

It exists to do five things:

1. give maintainers and reviewers one fast place to decide **which existing media-surface doc actually controls**;
2. stop future adjacent media-growth from restating a nearby wrapper, route, or state distinction in slightly different words;
3. keep the archive biased toward **overlap tightening, checklist/template refinement, and cross-link repair** before adding another numbered surface;
4. make mixed media incidents easier to describe as **one primary surface plus secondary wrappers** rather than as a synthetic mega-surface;
5. keep this family compact enough that it still helps operators under pressure.

It composes with:
- `docs/227-refactor-and-growth-protocol.md`
- `docs/310-voter-facing-public-answer-surfaces-family-map-and-promotion-rules.md`
- `docs/369-official-voter-information-videos-livestreams-and-clip-context-discipline.md`
- `docs/496-official-voter-information-platform-autoplay-end-screens-cards-and-play-next-authority-boundary-discipline.md`
- `docs/507-official-voter-information-platform-channel-home-featured-videos-playlists-and-collection-pages-authority-boundary-discipline.md`
- `docs/508-official-voter-information-platform-upcoming-event-pages-premiere-watch-pages-and-pre-live-countdown-authority-boundary-discipline.md`
- `docs/509-official-voter-information-platform-post-live-archive-replay-and-ended-event-surface-authority-boundary-discipline.md`
- `docs/510-official-voter-information-platform-search-results-homepage-recommendations-and-browse-feed-authority-boundary-discipline.md`
- `docs/511-official-voter-information-platform-share-panels-copy-links-timestamp-links-and-embed-export-authority-boundary-discipline.md`
- `docs/512-official-voter-information-platform-unavailable-private-age-gated-region-blocked-and-playback-restricted-surface-authority-boundary-discipline.md`
- `docs/513-official-voter-information-platform-playback-quality-adaptive-bitrate-resolution-selectors-and-data-saver-authority-boundary-discipline.md`
- `docs/514-official-voter-information-platform-titles-descriptions-thumbnails-posters-and-metadata-wrapper-authority-boundary-discipline.md`
- `docs/515-official-voter-information-platform-processing-pending-optimization-and-not-yet-fully-ready-media-surface-authority-boundary-discipline.md`
- `docs/516-official-voter-information-platform-live-edge-behind-live-state-latency-and-watch-live-recovery-authority-boundary-discipline.md`
- `docs/517-official-voter-information-platform-simulcast-mirrors-multi-route-live-events-and-redirect-chain-authority-boundary-discipline.md`
- `docs/518-official-voter-information-platform-registration-forms-invite-only-join-links-and-audience-gated-media-authority-boundary-discipline.md`
- `docs/519-official-voter-information-platform-view-counts-concurrent-viewers-likes-and-audience-metrics-wrapper-authority-boundary-discipline.md`
- `docs/520-official-voter-information-platform-channel-bylines-profile-names-handles-verification-badges-and-source-identity-wrapper-authority-boundary-discipline.md`
- `docs/521-official-voter-information-platform-information-panels-context-boxes-disclosure-labels-and-policy-wrapper-authority-boundary-discipline.md`
- `docs/522-official-voter-information-platform-event-theming-branded-player-chrome-and-live-status-label-authority-boundary-discipline.md`
- `docs/524-official-voter-information-platform-media-route-state-lexicon-badge-normalization-and-capture-order-discipline.md`
- `docs/525-official-voter-information-platform-media-mutation-classes-first-contact-evidence-pack-and-snapshot-minimization-discipline.md`
- `docs/526-official-voter-information-platform-media-re-anchor-ladder-canonical-recovery-targets-and-wrapper-exit-discipline.md`
- `docs/527-official-voter-information-platform-media-control-tuple-one-line-normalization-contract-and-packet-comparison-discipline.md`
- `docs/528-official-voter-information-platform-media-same-object-transition-chains-packet-stitching-and-resnapshot-threshold-discipline.md`
- `docs/529-official-voter-information-platform-media-chain-heads-current-control-and-closeout-discipline.md`
- `docs/530-official-voter-information-platform-media-chain-citations-head-first-reference-and-historical-leg-scoping-discipline.md`
- `docs/531-official-voter-information-platform-media-head-supersession-notes-trigger-codes-and-demotion-discipline.md`
- `docs/532-official-voter-information-platform-media-head-volatility-labels-provisional-current-notes-and-review-window-discipline.md`
- `docs/533-official-voter-information-platform-media-no-public-head-states-headless-chain-notes-and-fallback-anchor-discipline.md`
- `docs/534-official-voter-information-platform-media-co-current-aliases-sibling-routes-and-canonical-head-with-alias-discipline.md`
- `docs/535-official-voter-information-platform-media-audience-scoped-current-aliases-scope-labels-and-public-default-retention-discipline.md`
- `docs/536-official-voter-information-platform-media-route-scope-transitions-widening-narrowing-and-alias-rebucketing-discipline.md`
- `docs/537-official-voter-information-platform-media-capability-bearing-current-aliases-link-secret-routes-and-redaction-default-discipline.md`
- `docs/538-official-voter-information-platform-media-player-host-render-aliases-direct-embed-routes-and-watch-page-default-discipline.md`
- `docs/539-official-voter-information-platform-media-entrypoint-offset-aliases-current-time-start-at-routes-and-full-object-default-discipline.md`
- `docs/540-official-voter-information-platform-media-notification-carriers-reminder-pointers-and-route-carrier-separation-discipline.md`

## The anti-bloat rule for this family

For this subfamily, maintainers SHOULD prefer the following order of operations:

1. tighten an existing doc's **overlap / not-the-same-as** section,
2. refine an existing checklist or payload template,
3. repair entrypoint or cross-link wiring,
4. add one short quickmap note here,
5. map the route through `524` if the problem is mostly state vocabulary or capture-order drift,
6. use `525` if the problem is mostly packet size, first-contact capture discipline, or wrapper-mutation note quality,
7. use `526` if the problem is mostly re-anchor-target precedence or wrapper-exit choice,
8. use `527` if the problem is mostly summary-shape drift or packet-to-packet comparability,
9. use `528` if the problem is mostly same-object continuity, append-vs-split choice, or resnapshot thresholds across time,
10. use `529` if the problem is mostly chain-head choice, current-control legibility, or closeout discipline inside an existing media chain,
11. use `530` if the problem is mostly head-vs-leg citation drift or ambiguous chain references in later notes,
12. use `531` if the problem is mostly why a current head changed, what got demoted, or how to explain the supersession without packet archaeology,
13. use `532` if the problem is mostly that a current head is valid now but likely transient, and later summaries need one bounded provisional-current note plus a next-review trigger,
14. use `533` if the problem is mostly that the chain still exists historically but no public media packet should remain current,
15. use `534` if the problem is mostly that one current controlling answer still has more than one simultaneously valid public route and reviewers keep mistaking sibling aliases for supersession or historical legs,
16. use `535` if the problem is mostly that one ordinary-public current head coexists with a still-current route for a defined subset and reviewers keep blurring audience-scoped convenience with the public default,
17. use `536` if the problem is mostly that the same route or answer family moved between public, audience-scoped, alias, or headless buckets across time and reviewers keep mistaking scope drift for supersession or a new object,
18. use `537` if the problem is mostly that a current route works because the viewer possesses the full unlisted, privacy-hash, or other token-bearing path and reviewers keep mistaking bearer-style access for an ordinary-public alias or a named audience scope,
19. use `538` if the problem is mostly that a direct player-host or embed-render path keeps being mistaken for an ordinary watch-page alias or a new current head,
20. use `539` if the problem is mostly that a same-object `Start at`, current-time, or other entrypoint-offset link keeps being mistaken for a new head, a true clip surface, or the ordinary-public default,
21. use `540` if the problem is mostly that a reminder, notification, inbox entry, or delivery email keeps being mistaken for the same-object route it merely points to,
22. add a new numbered surface **last**.

A new adjacent numbered media surface should be the last resort, not the default move.

## First split: is the problem the media object, or a platform wrapper around it?

Use `369` when the decisive issue is still the **official recording, livestream, clip, captioned replay, or audiovisual publication lane itself**:
what the media said,
what scope/date/correction posture it carried,
and whether the media object should be treated as a controlling public answer at all.

Use the `496` / `507–522` stack when the decisive issue is a **platform-native wrapper, route, state, or portability layer around already-official media**.
That stack is for cases where the same underlying media object starts sounding more authoritative, more current, more complete, or more portable because of what the platform wrapped around it.

A useful maintainer shortcut is:
- **media content / publication question** → start at `369`;
- **platform wrapper / route-state / handoff question** → start in this quickmap;
- **once the controlling doc is chosen but the exact event-state wording still feels slippery** → use `524` to normalize the state note and capture order;
- **once the packet starts sprawling because several wrapper classes are visible at once** → use `525` to keep the evidence pack small and mutation-focused;
- **once the boundary and state are clear but the right authoritative recovery target is still drifting across packets** → use `526`;
- **once the boundary, state, mutation, and recovery target are all known but reviewers keep summarizing them in incompatible prose** → use `527`;
- **once two or more observations may belong to the same evolving official event and reviewers are unsure whether to append, fork, or split** → use `528`;
- **once a same-object chain exists but reviewers are unsure which packet is the current controlling head or whether the chain is now closed** → use `529`;
- **once the head is known but later notes keep citing the chain or a historical leg as if it were the current answer** → use `530`;
- **once reviewers agree that the head changed but later readers still have to reconstruct why the previous head was demoted or what trigger caused the switch** → use `531`;
- **once reviewers agree which packet controls now but it is still obviously part of a likely near-term state crossing or publication step** → use `532`;
- **once reviewers agree there is still one current controlling answer but more than one public route remains simultaneously valid for it** → use `534`;
- **once reviewers agree the object is still the same but the route's scope bucket changed across time** → use `536`;
- **once the same-object chain still has a bearer-style unlisted, privacy-hash, or other token-bearing route and the real question is possession-of-path rather than public discoverability or named-audience membership** → use `537`;
- **once the same-object chain still has a direct player-host or embed-render path and the real question is render-shell classification rather than public aliasing, audience scope, or bearer-path secrecy** → use `538`;
- **once the same-object chain still has a `Start at`, current-time, or similar landing-point variant and the real question is whether that offset route is just another way into the same full object rather than a new clip or head** → use `539`;
- **once the same-object chain still has a reminder, notification, inbox entry, or delivery email that merely points at the real current route and the real question is route-versus-carrier separation** → use `540`.

## Quickmap: choose the controlling boundary

| If the decisive problem is... | Use | Not primarily... | Why this is the controlling split |
|---|---|---|---|
| the already-open recording silently hands viewers into another asset through autoplay, cards, end screens, or play-next controls | `496` | `507`, `510`, `511` | the platform is steering onward from the current player rather than the office curating a collection, a ranked discovery surface, or a copied/exported wrapper |
| the office arranges many official recordings into a channel home, playlist, showcase, or featured collection | `507` | `496`, `510`, `514` | the office-authored collection page itself is the practical router |
| a public event page exists before the media begins and the countdown / waiting-room shell starts to feel like the answer | `508` | `509`, `516`, `522` | the route is decisively **pre-start** rather than replay-like, behind-live, or merely restyled |
| an ended-event page, archive, or replay shell keeps acting like the current answer after the live moment ended | `509` | `508`, `516`, `369` | the decisive problem is **post-live persistence** rather than pre-start posture, still-live lag, or the recording lane in general |
| the voter first meets the media through platform search, recommendations, homepage rows, or browse feeds | `510` | `507`, `511`, `520` | the platform-ranked discovery layer, not the office collection, copied wrapper, or identity chrome, did the routing |
| one official media object travels through copy-link, timestamp-link, share-panel, QR/share, or embed-export wrappers | `511` | `495`, `507`, `517` | the office did not mint a new clip and did not necessarily create a second live route; the issue is portability |
| the route says the media is unavailable, private, age-gated, blocked, sign-in-limited, or unplayable here | `512` | `518`, `410`, `413` | the public first hits a restriction shell rather than a deliberate registration / audience-selection workflow or a broader external-handoff failure |
| the media still plays, but practical comprehension changes because quality, bitrate, resolution, or data-saver state changed | `513` | `512`, `515` | the route remains playable; the decisive issue is fidelity loss, not outright restriction or not-yet-ready derivatives |
| mutable titles, descriptions, thumbnails, posters, or playlist-local labels start sounding like the controlling answer | `514` | `520`, `521`, `522` | the risk lives in mutable metadata wrappers rather than identity wrappers, policy/context wrappers, or event-shell chrome |
| the route is public now, but derivatives, higher qualities, transcripts, or replay affordances are still processing or incomplete | `515` | `512`, `513`, `509` | the decisive issue is **not-yet-fully-ready** state, not restriction, quality choice, or settled replay posture |
| the event is still live, but the viewer may be materially behind the true live edge and needs Watch Live / catch-up recovery | `516` | `508`, `509`, `505` | the route is still-live but mixed-currentness has opened between the player and the true live moment |
| the same official live event exists on several official routes or continuation handoffs at once | `517` | `511`, `508`, `509` | the archive needs primary-vs-mirror and route-set legibility, not merely one copied link or one pre/post-live shell |
| entry itself is fronted by registration, approval, invitation, members-only logic, or another audience gate | `518` | `512`, `389`, `409` | the decisive issue is the gate that decides who enters, not a generic unavailable shell, reminder/calendar handoff, or public-read boundary on the office site |
| view counts, concurrent viewers, likes, registrations, attendance totals, or similar numbers start acting like proof of authority | `519` | `500`, `510`, `520` | the wrapper signal is a count/metric, not a conversational layer, ranked placement, or identity cue |
| bylines, handles, badges, profile names, profile photos, or uploader identity cues start sounding like the whole proof of officialness | `520` | `514`, `521`, `522` | the decisive wrapper is source identity, not metadata wording, policy context, or organizer restyling |
| the platform adds information panels, election context boxes, disclosure labels, ratings, sensitivity cues, or protection banners | `521` | `514`, `520`, `522` | the decisive wrapper is platform-added policy/context, not office-authored metadata, source identity, or event chrome |
| banners, logos, colors, trailers, layout modes, latest-video substitutions, or hidden live badges restyle the same official route | `522` | `508`, `509`, `520` | the decisive issue is organizer-controlled shell presentation rather than route timing alone or source-identity proof |

## Mixed incidents: record one primary surface and a small set of secondary wrappers

Many real incidents span more than one row.
That does **not** mean the archive needs a synthetic umbrella surface.

Prefer this pattern instead:
1. identify the **primary surface** that most directly changed what the voter thought the route was;
2. record only the secondary wrappers needed to reconstruct the confusion;
3. keep the write-up in the vocabulary of existing docs.

Examples:
- A public Premiere page found through recommendations and then copied into chat is usually `508` primary, with `510` and `511` secondary.
- A replay page with a large view count and a reassuring verification badge is usually `509` primary, with `519` and `520` secondary.
- A live event whose badge is hidden and whose attendee-facing shell is heavily branded is usually `522` primary, with `516` secondary if live-edge confusion also mattered.
- A blocked embed that would have worked for admitted viewers after registration is usually `518` primary when the gate is the real boundary; use `512` only when the public first hits a restriction shell that is not really a registration workflow.

## Duplicate-firewall questions before adding any `540+` media surface

Before promoting another platform-media surface, maintainers SHOULD be able to answer **yes** to all of these:

1. **Different controlling object:** does the new proposal center a different first-contact object than the docs above (for example: collection page, event shell, replay shell, copied wrapper, restriction shell, identity wrapper)?
2. **Different route-state question:** would the reader need to answer a materially different question about pre-live / live / behind-live / ended / replay / restricted / copied state?
3. **Different public proof shape:** would the review capture new minimum evidence rather than reusing an existing checklist with one added row?
4. **Different correction semantics:** if two official channels disagreed here, would the dispute be materially different from disputes already modeled by `369`, `496`, or `507–522`?
5. **Different operator burden:** would an operator truly run a distinct checklist rather than an expanded checklist for an adjacent surface?
6. **Net anti-bloat gain:** will a new numbered doc reduce confusion more than tightening this quickmap and adjacent overlap rules would?

If any answer is "no," do one of these instead:
- tighten the adjacent docs' **not-the-same-as** sections,
- add one compact example or note here,
- refine an existing checklist/template,
- route the packet through `525` if the real problem is first-contact capture scope or wrapper-mutation note quality,
- route the packet through `533` if the real problem is that the chain still exists historically but no public media packet should remain current,
- route the packet through `537` if the real problem is that the route only works because the viewer already possesses the full token-bearing or unlisted path,
- route the packet through `538` if the real problem is that a direct player-host or embed-render path is being mistaken for an ordinary watch-page alias or a new head,
- route the packet through `539` if the real problem is that a same-object `Start at`, current-time, or other entrypoint-offset link is being mistaken for a new head, a clip, or the public default,
- route the packet through `540` if the real problem is that a reminder, notification, inbox entry, or delivery email is being mistaken for the route it merely carries,
- or log the candidate in `docs/207-research-agenda-and-revision-ledger.md` until the boundary is sharper.

## Required wiring for any future media-surface promotion

A future media-surface addition after this quickmap/lexicon/mutation-pack layer is not considered integrated unless the same revision also includes:
- the numbered canonical doc,
- the matching checklist,
- the matching payload template,
- at least two tightened adjacency declarations in nearby docs,
- one changelog entry and version bump,
- and navigation updates where readers and maintainers actually look first (`docs/13-*`, `docs/START_HERE.md`, and `docs/207-*`).

That rule is intentionally stricter than "write another doc."
The family is now large enough that growth without rewiring is more dangerous than slow growth.

## Minimal artifact

This quickmap is intentionally the only new artifact in this revision.
Do **not** add a second registry, matrix file, or checklist for the quickmap itself unless the archive later proves that the table here is no longer enough.
