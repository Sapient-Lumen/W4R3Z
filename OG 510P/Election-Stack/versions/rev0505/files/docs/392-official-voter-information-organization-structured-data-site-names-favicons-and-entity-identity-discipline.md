# 392 — Official voter-information organization structured data, site names, favicons, and entity-identity discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for the **official public identity signals** that a voter-information site emits to search and answer systems: organization structured data, home-page site-name markup, favicon signals, and closely related organization/contact metadata that may shape how the source is identified in search results, knowledge panels, attribution surfaces, and other first-contact layers.

It does **not** replace the underlying voter-question families in `292–343`.
It does **not** replace:
- `305`, which governs the authoritative office/help route,
- `362`, which governs office-discovery ladders and routing divergence,
- `382`, which governs external search-result presentation,
- `383`, which governs official social-profile shells,
- `385`, which governs platform place cards and office listings,
- `386`, which governs off-platform AI answer surfaces and citation handoff,
- or `391`, which governs crawlability, indexability, canonical discovery, and sitemap posture.

It adds one narrow rule:
**if an official voter-information site publishes organization/site identity signals that search or answer systems may reuse, those signals should consistently identify the right official source, hostname scope, help/contact lane, and public-facing name/logo/icon without blurring office responsibility or quietly preserving stale identity after a migration, split, or emergency replacement.**

## Why this is a distinct surface

Current official election-administration guidance still treats online voter information as a core public responsibility. The EAC's current **Effective Design for the Administration of Federal Elections** says election officials and partners are responsible for creating clear, understandable, and accessible **online voter information materials**. That obligation does not stop at page copy. It also applies to the public source cues that help a voter recognize which office or official site they are actually looking at. (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`)

Current Google Search documentation makes clear that these cues are operationally real. Google's current **Visual Elements Gallery** identifies site names and favicons as visible search-result elements. Its current **Site names in Google Search** guidance says site names are generated automatically, but that `WebSite` structured data on the home page is the most important way to indicate a preferred site name. Its current **Organization structured data** guide says organization markup can provide address, contact, URL, logo, and related administrative details that can show up in knowledge panels and other visual elements. Google's current structured-data introduction also says Google uses structured data to understand page content and information about the web and the world more generally. (xref: `google_search_central_visual_elements_gallery_page`; xref: `google_search_central_site_names_page`; xref: `google_search_central_organization_structured_data_page`; xref: `google_search_central_intro_structured_data_page`)

That is enough to justify a bounded public-surface control here.
The source identity layer is not just branding.
If a county election office, state election division, clerk, registrar, or emergency replacement site is identified ambiguously or inconsistently, the wrong office may look official first.

## Identity hints are real, but they are not guaranteed display contracts

Google's current general structured-data guidance says correctly marked-up structured data does **not** guarantee that a feature will appear in Search results. The same guidance says structured data must represent visible page content, stay up to date, avoid misleading or hidden content, and must not be blocked from crawling. (xref: `google_search_central_structured_data_guidelines_page`)

That means this archive should treat organization/site identity metadata as a **bounded hint surface**, not as a magical override.
The safe goal is not “force Google to show exactly this.”
The safe goal is:
- make the official source identity as legible and internally consistent as possible,
- keep it aligned with what voters can actually see on the page,
- and preserve enough policy trace to explain what identity signals the office emitted at time `T`.

## Home-page and hostname scope are load-bearing

Google's current site-name guidance says Google Search supports one site name per site, where a site is defined by the **domain or subdomain**, not the subdirectory; it also says `WebSite` structured data for site names must live on the home page of that domain or subdomain. Google's current favicon guidance likewise says Google Search supports one favicon per site, where a site is defined by the hostname, and not by subdirectory. (xref: `google_search_central_site_names_page`; xref: `google_search_central_favicon_in_search_page`)

For election sites, that is a real boundary:
- `county.example.invalid/elections/` cannot safely assume it has its own independent site-name layer if the supported scope is only the parent hostname,
- `elections.county.example.invalid/` may need its own home-page identity signals if it is intended to stand as a distinct public voter-information site,
- and emergency or vendor-hosted subdomains should not inherit ambiguous identity by accident.

So this surface should keep explicit track of:
- which hostname is supposed to carry the voter-information identity,
- whether the election office is a subdirectory section or a distinct subdomain,
- and how identity should behave when a public-help lane moves between them.

## Duplicate home pages and migrations should not fork identity

Google's current site-name guidance says if a site has duplicate home pages for the same content, the same structured data should be used on all duplicates, not only on the canonical page. It also says the `url` in `WebSite` structured data should point to the canonical home page. (xref: `google_search_central_site_names_page`)

That matters during:
- `www` / non-`www` migrations,
- HTTPS cutovers,
- subdomain launches,
- county-site redesigns,
- emergency replacement pages,
- and retirements of old election microsites.

Identity drift during those moments can leave search and answer systems with mixed cues about which office/site is current.
So the archive should treat duplicate-home-page consistency as part of the public answer posture, not as cosmetic metadata cleanup.

## Organization metadata should make the responsible office more legible, not less

Google's current organization-markup guide says Google recognizes organization properties such as `name`, `alternateName`, `address`, `contactPoint`, `telephone`, `url`, `logo`, and `sameAs`; it also says the `url` helps Google uniquely identify the organization and that the organization `name` and `alternateName` should match the site name. The guide recommends using the most specific schema.org subtype of `Organization` that matches the organization. (xref: `google_search_central_organization_structured_data_page`)

For election information, that means organization metadata should not blur together:
- a county government's generic shell,
- the specific election office/help lane that controls the answer,
- a vendor/operator shell,
- or a stale legacy election brand from a prior cycle.

This archive does **not** require every office to create a separate knowledge-graph entity for each voter-information subpage.
It requires only that the emitted public identity cues not contradict the actual responsible office and current official help path.

## Contact metadata and help lanes should converge

Google's current organization-markup guide says `contactPoint` should provide the best way for a user to contact the organization and should include available support methods. (xref: `google_search_central_organization_structured_data_page`)

For this archive, that means the identity layer should not point voters toward a generic or stale contact route if the authoritative help lane for election questions is elsewhere.
If the public voter-help path is a county election department, board of elections, clerk, registrar, or state election unit, then the visible page and emitted organization/contact cues should not quietly demote that help lane beneath a generic government shell.

## sameAs links are identity bridges, not authority inflation

Google's current organization-markup guide says `sameAs` URLs can point to pages on other websites that contain additional information about the organization. (xref: `google_search_central_organization_structured_data_page`)

That means `sameAs` belongs here as a bounded identity-control field.
Use it to connect the official site to the same organization on official or clearly attributable platforms.
Do **not** use it to inflate authority with:
- unofficial fan copies,
- campaign sites,
- stale legacy accounts,
- unrelated departments,
- or vendor pages that merely host or republish election content.

## Favicons and logos should help recognition without becoming stale carryovers

Google's current favicon guidance says the favicon should be visually representative of the website's brand and that Googlebot-Image must be able to crawl the favicon file while Googlebot can crawl the home page. Google's current organization-markup guide says a representative `logo` can help Google understand which logo to show in Search results and knowledge panels. (xref: `google_search_central_favicon_in_search_page`; xref: `google_search_central_organization_structured_data_page`)

Election offices should therefore treat logo/icon changes as public-answer risk when:
- the office renames,
- a state and county co-brand a temporary site,
- an emergency replacement site appears,
- or a prior election-cycle microsite is retired.

The point is not aesthetic consistency for its own sake.
The point is helping a voter quickly recognize the correct official source and notice when they have landed on a stale or unofficial shell.

## Structured-data truthfulness is load-bearing for public trust

Google's current general structured-data guidance says markup must be a true representation of visible page content, must stay up to date for time-sensitive information, and must not deceive, impersonate, or misrepresent ownership, affiliation, or primary purpose. (xref: `google_search_central_structured_data_guidelines_page`)

That aligns directly with this archive's authority-boundary posture.
An election office or partner should not let structured metadata claim a cleaner or more authoritative identity than the public page actually presents.
If the page visibly routes to one office, but the metadata names another, or if the page still carries an outdated election brand after responsibility moved, that is not harmless markup drift.
It is public identity ambiguity.

## This is upstream of result cards, place cards, and AI attribution

Read this document as an **upstream identity layer** for `382`, `385`, and `386`.
Search-result site names, favicons, knowledge-panel organization details, office-card attributions, and cited-answer source labels are downstream consumers of the site's own public identity signals.
If those signals are split, stale, or contradictory, later public-answer layers may inherit the confusion.

This is not a promise that every platform will render every field.
It is a bounded requirement that the official site emit coherent identity signals before those layers try to interpret them.

## Claims this surface should support

1. **Host-scope identity claim:** the archive can reconstruct which domain/subdomain was supposed to carry the voter-information identity at time `T`.
2. **Site-name claim:** the preferred public site name, alternates, and canonical home-page relationship were coherent enough that the official source did not identify itself one way in markup and another way on-page.
3. **Organization identity claim:** organization name, logo, URL, contact, and related metadata identified the responsible office or official shell consistently enough for external systems to recognize the source without avoidable ambiguity.
4. **sameAs / cross-platform identity claim:** linked off-site identity profiles were bounded to the same organization rather than inflating or confusing authority.
5. **Migration claim:** duplicate home pages, hostname moves, emergency replacements, or rebrands did not silently leave stale identity signals as equally current public answer anchors.
6. **Truthfulness claim:** structured metadata remained representative of visible page content and current public responsibility, rather than implying outdated or misleading authority.

## Canonical digest artifacts

Publish **digests of public identity policy**, not private webmaster dashboards or platform-specific admin records.

- **Identity Surface Digest (ISD):** digest of organization/site identity policy for the official voter-information surface.
- **Host Identity Transition Digest (HITD):** optional digest for hostname/subdomain migrations, emergency replacements, or rebrands.
- **Cross-Platform Identity Mapping Digest (CPIMD):** optional digest of bounded `sameAs` and related identity mappings used for public recognition.

## What belongs in the public payload

Keep the payload **small, hostname-aware, and reconstructible**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id`
- `public_identity_surface_label`
- `covered_surface_refs[]`
- `official_source_anchors[]`
- `preferred_site_name_note`
- `site_name_alternates_note`
- `hostname_scope_note`
- `canonical_homepage_policy_note`
- `duplicate_homepage_consistency_note`
- `organization_identity_note`
- `contact_point_alignment_note`
- `logo_and_favicon_policy_note`
- `same_as_mapping_note`
- `subdomain_or_microsite_boundary_note`
- `migration_or_rebrand_note`
- `truthfulness_and_visible_content_note`
- `identity_state_classes[]`
- `identity_trace_policy`
- `routing_fallback_uri`
- `routing_fallback_phone`
- `latest_notice_uri`
- `last_verified_at`
- supersedes / superseded-by pointers

Do **not** publish by default:
- private Search Console records,
- platform-claim tokens,
- webmaster verification secrets,
- analytics tied to individual users,
- or internal admin dashboards that are not needed to reconstruct the public identity posture.

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:
- Which hostname/domain/subdomain was meant to be the official voter-information source at time `T`?
- What site name and visible organization identity was the office asking external systems to associate with that site?
- Did the emitted identity cues point to the same responsible office/help lane the page visibly presented?
- Did favicons, logos, and `sameAs` mappings reinforce the current official source or preserve stale/confusing shells?
- During a migration or emergency replacement, were duplicate home pages and legacy hosts kept identity-consistent enough to avoid split recognition?
- Were structured-data claims representative of the visible page and current responsibility?

## How this fits the family map

This is **not** a general branding guide.
It is a bounded public-answer control.
Use it when the official site's organization/site identity cues may influence how voters recognize, trust, and follow official election information across search, answer engines, maps/listings, or emergency site transitions.

The underlying voter question is still handled by the substantive surface families.
This document only governs whether the official source can identify itself coherently before other systems restate or route to it.

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/official-voter-information-identity-surface-payload.json`
- Operator quickcheck: `artifacts/checklists/official-voter-information-identity-surface-checklist.md`

## Sources (pinned IDs / lockfile IDs)

- EAC: Effective Design for the Administration of Federal Elections (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`)
- Google Search Central: Introduction to structured data markup in Google Search (xref: `google_search_central_intro_structured_data_page`)
- Google Search Central: General structured data guidelines (xref: `google_search_central_structured_data_guidelines_page`)
- Google Search Central: Organization structured data (xref: `google_search_central_organization_structured_data_page`)
- Google Search Central: Site names in Google Search (xref: `google_search_central_site_names_page`)
- Google Search Central: Define website favicon for Search results (xref: `google_search_central_favicon_in_search_page`)
- Google Search Central: Visual Elements Gallery of Google Search (xref: `google_search_central_visual_elements_gallery_page`)
