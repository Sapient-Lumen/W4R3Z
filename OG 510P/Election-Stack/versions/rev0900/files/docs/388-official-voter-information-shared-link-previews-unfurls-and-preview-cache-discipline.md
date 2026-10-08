# 388 — Official voter-information shared-link previews, unfurls, and preview-cache discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **shared-link preview surfaces that may summarize or visually frame official voter information before a voter opens the underlying page**: chat/link unfurls, preview cards in messaging and collaboration tools, rich social-share cards, and similar title-description-image snippets created when someone pastes or forwards an official link.

It does **not** replace the underlying voter-question families in `292–343`.
It does **not** replace:
- `305`, which governs the authoritative office/help route,
- `366`, which governs official outbound alerts, texts, app notifications, and social posts,
- `378`, which governs file-download and embedded-viewer handoff after click-through,
- `379`, which governs stale-link and expired-page recovery once the voter lands on an older URL,
- `382`, which governs general web-search result presentation,
- `383`, which governs the persistent official social-profile shell,
- or `386`, which governs broader off-platform AI answer surfaces.

It adds one narrow rule:
**if voters may encounter an official link first as a preview card in chat, social sharing, or collaborative messaging, the preview should stay clearly official, clearly scoped, current-state-aware enough to avoid misleading compression, and easy to recover from when cached or detached cards go stale.**

## Why this is a distinct surface

Current official and primary technical guidance is enough to justify a bounded control here.

EAC's current voter and election-official guidance still says practical voting information is decentralized and that the best practical source is the local election office or the current state/local election site. Vote.gov's current trust posture likewise emphasizes official `.gov` and HTTPS routing. That matters here because a voter may meet the office first not through the full page, but through a card someone pasted into a group chat, a forwarded message, or a social-share preview that visually compresses the official page into a few fields. (xref: `eac_voter_faqs_page`; xref: `eac_best_practices_faqs_election_officials_page`; xref: `vote_gov_home_page`; xref: `vote_gov_about_us_page`)

Primary platform documentation shows that this compression layer is operationally real. The Open Graph protocol defines a shared metadata model in which pages expose fields such as `og:title`, `og:image`, `og:url`, `og:description`, locale, and site name for rich representation. Slack's current link-unfurling docs say Slack generates content previews by default and, absent an app-specific unfurl, falls back to classic behavior by crawling the URL, looking for common Open Graph and X Card metadata, and rendering a preview. Google's current Chat preview docs say a chat app can attach a preview card when someone shares a matching URL and that the card is visible to all users in the space. Microsoft's current Teams link-unfurling docs say pasted URLs can render preview cards before send, that zero-install unfurling is possible, and that unfurl results are cached for 30 minutes unless the app sets cache policy. (xref: `open_graph_protocol_page`; xref: `slack_unfurling_links_in_messages_page`; xref: `google_chat_preview_links_page`; xref: `microsoft_teams_link_unfurling_page`)

That is enough to treat shared-link previews as a real voter-information surface rather than as decorative metadata.
The office does not control every platform's rendering behavior.
But the voter may still trust the preview card first.
So the underlying official source needs to make that first-contact layer safe.

## Preview cards compress context differently from search results or official posts

A shared-link preview is neither the same as a search result nor the same as an official outbound post.
A search result is created by a search engine and typically appears in a search context (`382`).
An official post is itself authored and published by the office (`366`).
A shared-link preview sits in between: someone shares an official link, and the platform generates a small card that may outlive the sharer's explanation and may be viewed by people who never open the page.

That means the bounded control here is not “optimize every social platform.”
It is:
- keep the previewed page clearly official,
- keep canonical identity and destination class legible,
- keep volatile topics from relying only on timeless teaser text or stale imagery,
- and keep recovery obvious once the voter opens the page or notices the preview may be outdated.

## The preview card is a handoff layer, not a rule source

A rich preview card MAY help a voter recognize an official destination faster.
It MUST NOT become the controlling authority for jurisdiction-specific election rules.

The controlling artifact remains the current official page, signed notice, directory entry, or direct office confirmation that the jurisdiction itself stands behind.
So the preview layer should do only enough to:
- identify the office or official destination clearly,
- avoid implying that a one-card summary is the whole legal answer,
- preserve a route into the current page/notice/help lane,
- and recover safely when a forwarded card, cached preview, or stale image continues circulating after the underlying answer changed.

## Preview identity should make the destination recognizable before click-through

The Open Graph protocol makes title, canonical URL, description, locale, and site name part of the shareable object representation. Slack's current classic unfurling behavior explicitly depends on common Open Graph and X Card metadata, and Teams' current link-unfurling docs say Teams can render a preview card from a pasted URL before the message is sent. (xref: `open_graph_protocol_page`; xref: `slack_unfurling_links_in_messages_page`; xref: `microsoft_teams_link_unfurling_page`)

So pages likely to circulate for action-changing voter information should keep the preview layer recognizable at a glance.
That usually means a shared-link-safe page should make at least some combination of these stable in its preview metadata:
- responsible office or jurisdiction identity,
- destination class (office page, FAQ/help answer, notice, directory, lookup tool, file wrapper, etc.),
- election/date scope when material,
- a short description that helps the voter decide whether they still need to open the current page,
- and a canonical destination that points to the current official landing point rather than to a stale campaign-cycle artifact when a stable current page exists.

## Current-state cues matter because preview cards detach easily from time context

A voter may see a preview card hours or days after it was first generated, in a different conversation, or with little surrounding explanation.
Teams' current documentation makes the cache problem explicit by saying unfurl results are cached for 30 minutes unless cache policy is changed. Google Chat's current preview docs say cards can be attached to shared messages and remain visible to everyone in the space. Slack's current docs say previewing falls back to crawler-based unfurls for ordinary links. (xref: `microsoft_teams_link_unfurling_page`; xref: `google_chat_preview_links_page`; xref: `slack_unfurling_links_in_messages_page`)

So for volatile topics, preview-safe official pages should not rely only on generic evergreen teaser text.
They should prefer metadata and landing pages that make it easier to recover current state, such as:
- current cycle labeling when material,
- language that distinguishes a current lookup/help page from an archived advisory,
- descriptions that name the actual task (“check polling place,” “office hours,” “mail-ballot help”) instead of vague promotion copy,
- and landing pages that expose current official status or route quickly into the current notice/help layer.

The goal is not to put every deadline into preview metadata.
The goal is to reduce the chance that a stale preview card frames the wrong page as the current practical answer.

## Preview caches and forwarded cards need explicit recovery paths

A preview card can become stale even when the link itself still resolves correctly.
The title, description, image, or card body may reflect older state, while the underlying page has moved on.
That is why this surface composes directly with `379`.

A safe pattern is:
- let the preview point at a stable current official destination where possible,
- make the landing page immediately say what it is and whether the voter needs fresher or more specific facts,
- and keep the office/help lane obvious when the shared card was only a coarse routing cue.

This archive does **not** need platform-specific cache-purge playbooks.
It only needs a bounded policy saying that preview-card drift is a known first-contact risk and that the click-through page must recover from it cleanly.

## Cross-platform variation is normal; identity and recovery still have to hold

Slack's docs describe crawler-based classic unfurls using page metadata. Google Chat previewing depends on registered host/path patterns and can attach cards to a shared message. Teams can unfurl before send and can even do zero-install unfurling. These platforms do not expose exactly the same controls, the same card shapes, or the same user expectations. (xref: `slack_unfurling_links_in_messages_page`; xref: `google_chat_preview_links_page`; xref: `microsoft_teams_link_unfurling_page`)

So the bounded rule is:
- do not assume every platform renders the same preview fields,
- do not make operational correctness depend on one platform-specific card affordance,
- and do make the underlying official page recognizable and recovery-rich even when the preview is absent, truncated, or oddly cached.

## Accessibility and descriptive-link discipline still apply

USWDS's current link guidance says links are navigational elements, that too many links can overwhelm, that external destinations should be identified clearly, and that teams should avoid generic text like “read more” or “link.” That guidance is written for pages, but it points in the same direction here: link-associated text should help people understand where they will go and why. (xref: `uswds_link_component_page`)

So even though a platform may auto-generate the preview card, the office should still prefer page titles/descriptions and surrounding public language that make the destination understandable instead of forcing the preview to act like a mysterious teaser.

## Minimal shared-link-preview state taxonomy

A small taxonomy is enough:

1. **preview_card_with_clear_official_identity**
2. **preview_card_needing_clickthrough_for_scope_or_date**
3. **cached_or_forwarded_preview_recovered_by_current_page**
4. **preview_missing_or_truncated_but_official_link_still_legible**
5. **high_risk_question_routed_to_help_lane_after_clickthrough**

That is usually more useful than pretending every chat platform needs its own theory chapter.

## Bounded trace minimum

The archive does **not** need platform message logs, user-share telemetry, private analytics, or full social/chat crawler traces.
But for accountability and later reconstruction, it is still useful to preserve a bounded **shared-link preview policy trace** for action-changing official pages.

At minimum, a jurisdiction should be able to reconstruct:
- which official pages were expected to circulate as shared links for volatile topics,
- which metadata/canonical-destination policy governed those pages,
- which help/notice route was supposed to recover stale preview cards,
- and when the office last reviewed preview-facing destination classes.

That gives the archive enough to evaluate whether the preview layer was safely bounded without turning the archive into a communications-surveillance sink.

## Proof obligations

If a jurisdiction claims to operate this surface responsibly, it should be able to prove at least:

1. **Authority-boundary claim:** shared-link previews are treated as handoff layers, not as controlling rule sources.
2. **Official-identity claim:** likely-to-circulate pages expose enough preview identity to be recognized as current official destinations.
3. **Current-state claim:** volatile topics do not rely solely on stale teaser text, detached images, or misleading evergreen blurbs.
4. **Recovery claim:** click-through pages or notices visibly recover from cached or forwarded preview drift.
5. **Trace-minimization claim:** bounded reconstruction is possible without retaining individualized chat/share telemetry.

## Canonical digest artifacts

Publish **digests of preview policy and destination class state**, not platform telemetry.

- **Shared Link Preview Surface Digest (SLPSD):** digest of the bounded public payload for shared-link preview readiness.
- **Preview Metadata Policy Digest (PMPD):** digest of the policy describing title/description/canonical/current-state expectations for pages likely to circulate.
- **Preview Recovery State Digest (PRSD):** optional digest proving what stale-preview recovery cues a landing page class was supposed to expose at time `T`.

## What belongs in the public payload

Keep the payload **small, preview-aware, and authority-boundary explicit**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `link_preview_surface_label`
- `covered_surface_refs[]`
- `official_source_anchors[]`
- `authority_boundary_note`
- `preview_metadata_policy_note`
- `preview_image_policy_note`
- `canonical_destination_policy_note`
- `preview_cache_recovery_policy_note`
- `current_state_cue_policy_note`
- `cross_platform_variation_note`
- `link_preview_state_classes[]`
- `link_preview_trace_policy`
- `routing_fallback_uri`
- `routing_fallback_phone`
- `latest_notice_uri`
- `last_verified_at`
- supersedes / superseded-by pointers

Do **not** publish by default:
- message-level share logs,
- platform-private crawler/debugger traces,
- user identity tied to who shared an official link,
- or synthetic engagement scores that do not help reconstruct the bounded public handoff policy.

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:
- Which official pages were intended to be safe shared-link destinations at time `T`?
- Did the preview-facing metadata and canonical destination make the office and page class recognizable before click-through?
- Could a voter safely recover when a cached or forwarded preview card lagged behind the current answer?
- Was there a visible route from the previewed page into the current official notice/help lane for high-risk topics?
- Did the jurisdiction preserve a bounded preview-policy trace without collecting unnecessary share telemetry?

## How this fits the family map

Shared-link previews and unfurls are **not** a new canonical voter-question family bucket.
They are a first-contact delivery layer that may visually summarize an existing voter-information surface before the voter opens the actual page.

So the underlying question remains:
- where to vote,
- which office is authoritative,
- whether the office is open right now,
- which help page or notice controls,
- or where the voter should escalate when ordinary self-service fails.

This document only says that, if voters may meet the official link first through an unfurl or preview card, the preview layer should stay clearly official, minimally scoped, current-state-aware enough to avoid obvious misrouting, and recovery-rich instead of quietly becoming the trusted answer.

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/official-voter-information-link-preview-surface-payload.json`
- Operator quickcheck: `artifacts/checklists/official-voter-information-link-preview-surface-checklist.md`

## Sources (pinned IDs / lockfile IDs)

- EAC: Voter FAQs (xref: `eac_voter_faqs_page`)
- EAC: Best Practices: FAQs for Election Officials (xref: `eac_best_practices_faqs_election_officials_page`)
- Vote.gov: Home / trust marker (xref: `vote_gov_home_page`)
- Vote.gov: About Vote.gov (xref: `vote_gov_about_us_page`)
- Open Graph protocol (xref: `open_graph_protocol_page`)
- Slack Developer Docs: Unfurling links in messages (xref: `slack_unfurling_links_in_messages_page`)
- Google for Developers: Preview links in Google Chat messages (xref: `google_chat_preview_links_page`)
- Microsoft Learn: Link unfurling in Teams (xref: `microsoft_teams_link_unfurling_page`)
- USWDS: Link component (xref: `uswds_link_component_page`)
