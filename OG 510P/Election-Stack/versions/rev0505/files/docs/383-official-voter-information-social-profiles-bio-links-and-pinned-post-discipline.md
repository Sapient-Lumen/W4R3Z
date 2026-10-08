# 383 — Official voter-information social profiles, bio links, and pinned-post discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **official voter-information social-profile surfaces**:
platform account names,
handles,
display names,
profile images or banners where they materially signal office identity,
biography/about fields,
profile-level contact cues,
link-in-bio destinations,
pinned posts,
and similar persistent account-level elements that many voters encounter before or instead of an ordinary webpage.

It does **not** replace the underlying voter-question families in `292–343`.
It does **not** replace:
- `194`, which governs communications authenticity minimums,
- `203`, which governs official channel directories,
- `305`, which governs the authoritative office/help route,
- `366`, which governs individual short-form alerts and posts,
- `370`, which governs official email/newsletter surfaces,
- `371`, which governs partner redistribution,
- `381`, which governs QR / shortlink printed-to-digital handoffs,
- or `382`, which governs external search-result presentation.

It adds one narrow rule:
**if an election office expects voters to recognize, trust, or act through a persistent social-media profile surface, that profile should make the official office identity legible, keep its bio link and pinned item subordinate to current official destinations, and remain recoverable when handles, platforms, or pinned content drift stale.**

## Why this is a distinct surface

Current official guidance is enough to justify a bounded control here.

Digital.gov's current **Social media** topic page says agencies use social media to strengthen connection with the public, promote transparency, respond to audience needs, and communicate during emergencies.  
EAC's current **Election Official Social Media Toolkit** is operational rather than decorative: it includes sample post variants that point readers to an inserted official link or “the link in our bio,” provides alt text, and treats community management as part of trusted public communication.  
Digital.gov's current **Improving the Accessibility of Social Media in Government** says agencies have a responsibility to ensure their social-media content is accessible, and that content managers need to stay abreast of usability issues and continually test content as platforms change.  
USWDS's current **Footer** guidance says agencies should avoid stale social-media accounts and link only to accounts they update frequently or use to communicate with customers.  
Digital.gov's current **Social media cyber-vandalism toolkit** says agencies should train staff before account use and add official accounts to the U.S. Digital Registry to verify authenticity of ownership.  
Digital.gov's current **An introduction to content** says content includes social-media posts, should be kept current, and should demonstrate authoritativeness.  
And current Digital.gov/Vote.gov trust guidance says official government communications and services should stay on recognizable `.gov` / secure official-domain footing where possible. (xref: `digital_gov_social_media_topic_page`; xref: `eac_election_official_social_media_toolkit_2024_pdf`; xref: `digital_gov_accessibility_social_media_in_government_page`; xref: `uswds_footer_component_page`; xref: `digital_gov_social_media_cyber_vandalism_toolkit_page`; xref: `digital_gov_introduction_to_content_page`; xref: `digital_gov_requirements_registration_use_gov_domains_page`; xref: `vote_gov_home_page`)

That is enough to treat the profile layer as a real public-answer surface.
It is not the same thing as an individual social post.
A profile page often determines **which account the voter decides is official, which persistent link they follow first, which pinned item they treat as the current summary, and whether a stale handle or stale profile shell quietly stays operative after the office changed its routing.**

## The profile layer is a persistent routing shell, not a floating brand wrapper

A profile surface MAY help voters find the right office quickly.
It MUST NOT become a hidden rule source that silently outranks the current official webpage, notice, FAQ/help entry, or office directory.

The controlling artifact remains the current official destination that the jurisdiction stands behind.
The profile layer should only do enough to:
- make the official office identity recognizable,
- point people into the current official destination or help lane,
- preserve a recoverable persistent handoff even when individual posts roll by,
- and avoid leaving stale pinned/profile cues behind after the underlying answer changes.

## Distinct classes inside the profile surface

The archive should not flatten every account-level cue into “social media.”
At least six different profile-level classes matter:

1. **Handle / account-name state** — the username, display name, verification posture, and recognizable office identity.
2. **Bio/about text** — the short persistent description that tells people which office this is and what scope it covers.
3. **Profile-level link target** — the “website” or link-in-bio destination, including any profile-level link hub.
4. **Pinned post / featured post** — the persistent post many users encounter before ordinary feed chronology.
5. **Highlight / featured-media rail** — stories, collections, reels, or similar quasi-persistent featured items.
6. **Identity transition state** — handle changes, successor accounts, deprecated accounts, merged county/city/state channels, or platform exits.

Those are related, but not identical problems.
A bio link can be current while the pinned post is stale.
A handle can still look official while the profile bio under-specifies which county or jurisdiction it serves.
And an office can migrate accounts while screenshots of the old handle keep circulating.

## Separate the persistent profile from per-post alerting

`366` governs short-form posts and linkback discipline.
This document governs the persistent account shell that outlives any one post.

That means:
- do not assume a clean alert discipline automatically fixes the profile,
- do not assume a correct profile means the pinned post is current,
- and do not treat the bio link as a substitute for the current controlling webpage.

A voter may never see the post that communications staff thought mattered.
They may see only the handle, display name, avatar, bio, pinned item, and link button that a platform surfaces by default.

## Official identity floor

A voter-facing social profile should make the authoritative office easy to recognize.
Operationally, that usually means the profile should keep four things legible:
- which election office it belongs to,
- which jurisdiction or scope it serves,
- where the current official website/help route lives now,
- and whether the account is current, legacy, or only a relay shell.

Avoid profile shells that read like generic campaign copy, personal staff accounts, or ambiguous “elections update” handles with no office/jurisdiction anchor.
If a voter cannot tell whether a profile is the county board of elections, the city clerk, the state elections division, or a contractor/community partner relay, the profile surface is already failing before any post is read.

## Bio text should identify the office, not only the mission slogan

Digital.gov's content guidance says content should be audience-focused, current, and authoritative. (xref: `digital_gov_introduction_to_content_page`)
For this narrow surface, that means the profile biography/about field should usually make the office identity and scope obvious:
- office name,
- jurisdiction,
- whether the profile is a general office/help lane or a specialized voter-info lane,
- and where the official website/help destination lives.

Mission slogans or civic encouragement can still be present.
But a voter should not have to infer the office identity from a logo alone.

## Bio-link discipline

A bio link is often the single highest-leverage routing control on a social profile.
If it is wrong, vague, or stale, the whole profile becomes a drift amplifier.

Current `.gov`/trust guidance says official communications and services should use recognizable official domains, while Vote.gov reinforces `.gov` + HTTPS as the trust marker. (xref: `digital_gov_requirements_registration_use_gov_domains_page`; xref: `vote_gov_home_page`)
USWDS link guidance and Digital.gov content guidance together support a simple floor: destination context should be understandable and current. (xref: `uswds_link_component_page`; xref: `digital_gov_introduction_to_content_page`)

So the default posture should be:
- prefer a direct official-domain destination,
- keep the bio link human-checkable and current,
- use a profile-level link hub only when it materially improves routing and remains legibly official,
- and avoid opaque third-party routing layers when one stable official link would do.

A profile bio link should usually land on one of four things:
1. the current official voter-information homepage,
2. the authoritative office/help/contact route,
3. a current notice/landing page for a live operational condition,
4. or a stable official hub that clearly routes to current action-changing destinations.

It should not point to an expired election microsite, an unlabeled PDF, an unofficial campaign-style landing page, or a generic aggregator whose authority is harder to evaluate than the office website itself.

## Pinned-post discipline

Pinned posts are a distinct risk because they look authoritative and persistent even when they are just old feed items frozen near the top.
A pinned post can quietly become the effective answer long after the office changed the underlying page.

So a pinned item should usually be one of two things:
1. **a stable evergreen routing post** that tells users where current official information/help lives, or
2. **a dated, explicitly scoped operational post** that is reviewed, stale-marked, replaced, or unpinned when it stops controlling.

Do not leave an election-specific pinned post in place after its date/scope passed unless it is visibly historical and visibly routes to the current official destination.
If the pinned item is about a registration deadline, polling-place change, emergency relocation, vote-by-mail rule, or similar action-changing fact, the office should treat it like a timed public-answer surface rather than ornamental profile furniture.

## Highlight / featured-media discipline

Many platforms now let offices feature stories, reels, or grouped media on the profile itself.
Those can become quasi-persistent answer surfaces.

If the office uses them for voter information:
- keep issue dates or election scope legible,
- do not trap crucial action-changing instructions only inside inaccessible image/video frames,
- pair them with the current official destination or help route,
- and review them when the election cycle or operational state changes.

A profile highlight rail is closer to a miniature public archive than to ephemeral chat.
Treat it accordingly.

## Stale-profile and legacy-account recovery

USWDS says agencies should avoid stale social-media accounts. (xref: `uswds_footer_component_page`)
That principle extends beyond the website footer.
If an election office retires a social account, changes handles, merges channels, or moves to a successor account, the public still needs a recovery path.

That means:
- keep the legacy profile visibly marked as legacy when the platform allows,
- point users toward the successor official profile and official website/help route,
- update pinned items and bio text before or during migration,
- and preserve a bounded record of handle/account transitions for later public reconstruction.

Deleting a profile without a recovery trace can strand screenshots, bookmarks, old embeds, and search results.
A stale or legacy account should not silently masquerade as current simply because the old handle still looks familiar.

## Platform authenticity and ownership boundary

The cyber-vandalism toolkit says agencies should train staff before account use and add official accounts to the U.S. Digital Registry to verify authenticity of ownership. (xref: `digital_gov_social_media_cyber_vandalism_toolkit_page`)
That is a useful bounded lesson even outside the federal registry context:
- define which accounts are official,
- keep an official directory or equivalent office-owned list of them,
- maintain account-ownership continuity,
- and make profile authenticity legible enough that third parties can distinguish the office account from lookalikes.

This document does not require publishing privileged account-recovery details.
It does require not treating the identity layer as someone else's problem.

## Accessibility floor

Digital.gov's social-media accessibility guidance says agencies are responsible for accessible social content and should continue testing as platforms change.  
EAC's toolkit includes alt text directly inside the workflow for election-official social content. (xref: `digital_gov_accessibility_social_media_in_government_page`; xref: `eac_election_official_social_media_toolkit_2024_pdf`)

For the profile lane, that supports a strict floor:
- do not put critical routing facts only into profile images or inaccessible story/highlight media,
- use alt text, captions, and accessible content practices for pinned or featured media,
- and re-check accessibility after platform template changes or new profile features are adopted.

## Bounded trace, not individualized audience surveillance

A jurisdiction may need to reconstruct which persistent profile state was in force at time `T`.
It does not need to turn profile traffic into individualized surveillance to do that.

At minimum, bounded reconstruction should make it possible to recover:
- which official handle/display-name set was in force,
- which bio text version was current,
- which profile-level link target was current,
- which pinned/featured item was active,
- whether the account was current, legacy, transitional, or relay-only,
- and when that state changed.

Prefer **profile snapshots, handle-transition records, bio-link destination refs, pinned-item refs, and timestamps** over follower-by-follower or click-by-click telemetry.

## Minimal claim-set

A jurisdiction can publish a compact, verifiable claim-set:

1. **Official profile claim:** one or more named social profiles are official public voter-information profile surfaces for scope `E`.
2. **Identity-legibility claim:** display name, bio text, and account cues make the authoritative office and jurisdiction recognizable.
3. **Bio-link claim:** the profile-level link routes to a current official destination or help lane.
4. **Pinned-item claim:** pinned/featured items are either evergreen routing aids or explicitly dated/scoped and reviewed when they stop controlling.
5. **Transition claim:** handle/account migrations produce explicit legacy-to-successor recovery.
6. **Accessibility claim:** pinned/featured profile content follows accessible-content minimums and is re-checked as platforms change.
7. **Trace-minimization claim:** bounded reconstruction is possible without individualized audience surveillance.

## Canonical digest artifacts

Publish **small digests of the profile surface**, not full platform analytics exports.

- **Social Profile Surface Digest (SPSD):** digest of the bounded profile-surface policy payload for a scope.
- **Pinned Item Mapping Digest (PIMD):** digest of which pinned/featured item family was current for a profile at time `T`.
- **Account Identity Transition Digest (AITD):** digest of handle/account migration, legacy marking, or successor-account declaration.
- **Profile/Bio Link Snapshot Digest (PBSD):** optional digest tying the profile's visible bio link to the current official destination or office/help lane.

## What belongs in the public profile-surface payload

Keep the payload **small, official-identity-forward, current-state-aware, and recovery-capable**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `profile_surface_label`
- `official_profile_handles[]`
- `covered_surface_refs[]`
- `official_source_anchors[]`
- `display_name_policy_note`
- `bio_identity_policy_note`
- `bio_link_policy_note`
- `pinned_item_policy_note`
- `featured_media_policy_note`
- `identity_transition_policy_note`
- `profile_state_classes[]`
- `profile_trace_policy`
- `routing_fallback_uri`
- `routing_fallback_phone`
- `rights_escalation_uri`
- `latest_notice_uri`
- `last_verified_at`
- supersedes / superseded-by pointers

Do **not** publish by default:
- individualized follower lists,
- direct-message archives,
- per-user click telemetry,
- private moderation notes,
- or account-recovery secrets.

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:
- Which profiles were official at time `T`?
- Did the profile make the office and jurisdiction legible?
- Where did the bio link point, and was it an official current destination?
- Which item was pinned or featured at the time, and was it current or stale?
- Did a handle/account migration provide a visible recovery path?
- Could a third party reconstruct the bounded profile state without individualized audience surveillance?

## How this fits the family map

A social profile shell is **not** a new canonical voter-question family bucket.
It is a persistent recognition and routing layer that sits around many different voter-help topics.

So the underlying question remains:
- which office is authoritative,
- where the current voter-information homepage or FAQ lives,
- what notice or form edition is current,
- which hotline or office/help route should control,
- or where the voter should escalate when ordinary self-service fails.

This document only says that, if an office expects the public to rely on a social profile shell to recognize or reach official voter information, the profile's handle/bio/link/pinned layer should remain current-state-aware, clearly official, recoverable, and later reconstructible instead of acting as a stale or ambiguous authority shell.
