# 398 — Official voter-information site moves, domain migrations, `.gov` transitions, and hostname continuity discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **official voter-information source-host transitions**:
whole-site moves from one domain or subdomain to another,
`.gov` adoption,
emergency replacement hosts,
parallel old/new host periods,
search-console/site-move signaling,
legacy-domain retention,
and the public-routing continuity work needed so voters do not lose the official source when the office’s hostname changes.

It does **not** replace the underlying voter-question families in `292–343`.
It does **not** replace:
- `203`, which governs the official-channel directory,
- `305`, which governs the authoritative office/help route,
- `379`, which governs per-URL stale-link recovery after arrival,
- `381`, which governs QR / shortlink printed-to-digital handoffs,
- `391`, which governs crawlability, indexability, canonical discovery, and sitemap posture in steady state,
- `392`, which governs organization/site identity signals,
- `394`, which governs search removals, `noindex`, and recrawl,
- or `397`, which governs alternate-language discovery after the host relationship is already stable.

It adds one narrow rule:
**if an election office changes the hostname that voters, search engines, assistants, partners, or printed materials use to reach current official voter information, the host-transition layer should preserve one clearly current official source, keep the old host under trusted containment and recovery control, move search/discovery signals with the host, and avoid multiplying semi-official shells during the migration window.**

## Why this is a distinct surface

Current official guidance is enough to justify a bounded control here.

EAC's current **Effective Design for the Administration of Federal Elections** says election officials and partners are responsible for clear, understandable, accessible **online voter information materials**.
Get.gov's current **.Gov for election offices** guidance says `.gov` domains help the public identify official, trusted election information, that `.gov` domains are available only to verified U.S.-based government organizations, and that malicious actors have tried to impersonate election organizations.
Digital.gov's current guidance on `.gov` domains says `.gov` increases security, trust, and accountability and helps the public identify official government information.
Get.gov's current **Moving to .gov** guidance says offices should plan early, keep the current domain, redirect traffic from the old domain to the new one, move email, and develop a communications plan that also updates offline branding such as paper products and signage.
Google Search Central's current **How to move a site** guidance says a site move with URL changes should prepare URL mapping, use server-side permanent redirects, update canonical and alternate-language annotations, submit a Change of Address when moving between domains/subdomains, and submit the new sitemap while monitoring the move.
Google Search Central's current **How To Use Search Console** page says the Change of Address tool tells Google about a move from one domain or subdomain to another and helps migrate Search results.
That is enough to treat host migration as a real voter-information control surface rather than as generic IT housekeeping. (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`; xref: `get_gov_election_offices_page`; xref: `digital_gov_requirements_registration_use_gov_domains_page`; xref: `get_gov_domains_moving_page`; xref: `google_search_central_site_move_with_url_changes_page`; xref: `google_search_central_search_console_start_page`)

This matters because a domain/hostname change rewires **multiple public-answer layers at once**:
- bookmarks and old links,
- search results and indexing history,
- printed URLs / QR destinations,
- official email addresses,
- partner link lists,
- language alternates,
- and the public's own recognition of what looks official.

`379` covers how a stale URL recovers once someone lands.
This document covers the higher-level question of whether the **official source host itself** remained legible and continuous during the move.

## Host migration is not the same thing as ordinary stale-link recovery

A redirect from one old page to one new page MAY be enough for a simple page move.
A source-host migration is broader.
It changes the public shell that voters may trust before they even read the page.

That creates separate responsibilities:
- choosing and declaring the current primary host,
- retaining and defending the legacy host long enough to prevent impersonation or abandonment,
- moving search/discovery signals rather than letting them drift,
- updating identity signals and alternate-language clusters,
- and keeping official communications, partner routing, and printed/offline materials coherent while both hosts may still circulate.

So this document stays above `379`.
It does not micromanage every stale URL.
It governs the **authoritative host continuity** that makes those URL-level recoveries safe.

## `.gov` adoption is a trust transition, not just a registrar task

Get.gov's current guidance for election offices says `.gov` helps the public identify official election information, is available only to verified U.S.-based government organizations, and includes security controls such as required MFA on `.gov` accounts and HSTS preloading for new domains.
Its current moving guidance also tells organizations to plan the transition early, retain the current domain, redirect traffic, move email, and build a communications plan. (xref: `get_gov_election_offices_page`; xref: `get_gov_domains_moving_page`)

That means a move from `.org`, `.us`, a municipal subdomain, or another host into `.gov` should be treated as a **public trust transition**.
The office is not merely changing plumbing.
It is retraining the public, search systems, partner organizations, and its own printed/offline materials to recognize a new authoritative shell.

So the bounded policy should prefer:
- one clearly declared current `.gov` primary host when the move is complete,
- legacy-host retention rather than abandonment,
- explicit public notices and partner updates during the overlap window,
- and recovery from the old host into the new controlling official help lane.

## Keep the old host under trusted containment

Get.gov's current moving guidance says organizations should plan to keep the current domain so it does not fall into the wrong hands, and that if the old domain is used for redirects its TLS certificate should remain current.
It also recommends planning to move email while preserving delivery through aliases where possible. (xref: `get_gov_domains_moving_page`)

That creates a high-value election rule:
**the old host should not simply disappear from control because the office launched the new host.**

For voter information, losing control of the old domain can produce several distinct failures:
- voters still follow old bookmarks or printed materials,
- partner sites still list the old domain,
- legacy email addresses still circulate,
- and an attacker or unrelated registrant may later obtain the abandoned domain.

So even after the new host becomes primary, the legacy host should remain either:
- an active redirect/recovery shell,
- an explicit tombstone/transition notice,
- or a defensively retained inactive domain that is **not** pretending to be current but is still not released.

## Change one big thing at a time

Google Search Central's current site-move guidance recommends changing one thing at a time where possible rather than moving domains, redesigning the CMS, and changing layout all at once.
It also recommends preparing URL mapping before the move. (xref: `google_search_central_site_move_with_url_changes_page`)

That is especially relevant for elections.
If an office changes the domain, redesigns navigation, rewrites titles, changes structured data, and alters language paths all in the same live-election window, it becomes much harder to tell whether a public-routing failure came from the host move, the content reorganization, or the new rendering stack.

So this bounded control should prefer:
- host move first,
- content/system redesign separately when feasible,
- and a reconstructible URL mapping policy that says whether each old path moved one-to-one, consolidated, expired, or now routes to the office/help lane.

## Redirects are necessary, but they are not the whole migration

Google Search Central's current site-move guidance recommends server-side permanent redirects from old URLs to new URLs, warns against redirecting many old URLs to one irrelevant destination such as a homepage, and says redirects should remain in place for as long as possible, generally at least one year. (xref: `google_search_central_site_move_with_url_changes_page`)

That means host continuity should not be reduced to “we turned on some 301s.”
The migration should also preserve:
- canonical pointers on the new host,
- alternate-language annotations updated to the new URLs,
- new sitemaps,
- any official identity signals that still point at the old host,
- and explicit help routing when some old content does **not** map one-to-one.

A host migration with redirects but stale canonicals, stale `hreflang`, stale site-name/contact cues, or stale partner links is only half-moved.

## Search-console/site-move tooling is support evidence, not the rule source

Google's current Search Console guidance says the Change of Address tool tells Google about a move from one domain or subdomain to another and helps migrate Search results.
The site-move guidance separately says both old and new sites should be verified in Search Console, the new sitemap should be submitted, and traffic/indexing should be monitored during the move. (xref: `google_search_central_search_console_start_page`; xref: `google_search_central_site_move_with_url_changes_page`)

That supports a bounded evidence rule:
- preserve the fact that the office intended a host move,
- preserve whether search-side move signaling and sitemap updates were completed,
- but do **not** make private Search Console dashboards the archive's controlling artifact.

The rule source remains the public-facing host continuity policy and the observable official routing behavior.
Private tooling can corroborate that policy.
It does not replace it.

## Emergency replacement hosts should be explicit and temporary-safe

Election offices may need an emergency replacement host during outages, attacks, vendor failures, or urgent `.gov` transition timing.
This document does not require that emergency host to look like the final steady-state architecture.
It does require the office to keep the public state legible.

A safe emergency replacement posture is usually:
- explicit notice that the primary official host is unavailable or transitioning,
- one clearly named temporary current host,
- visible routing back to the ordinary official office/help lane,
- and a plan for the old and replacement hosts once steady state returns.

Avoid a silent condition where both hosts look equally current or where the replacement host has no visible relation to the ordinary official office identity.
That blurs authority at exactly the moment public trust is under stress.

## Printed, partner, and email lanes must move with the host

Get.gov's current moving guidance says organizations should develop a communications plan, move email, and review/update offline branding such as paper products, vehicles, and public signage.
It also notes that transition costs can include replacing printed materials and informing the public. (xref: `get_gov_domains_moving_page`; xref: `get_gov_election_offices_page`)

That means a host migration is not complete when the website resolves.
It is complete only when the office can say, in bounded form:
- which host is current,
- how legacy email reaches the office or is retired safely,
- whether partner organizations and directories were updated,
- whether printed URLs / QR paths still recover safely,
- and whether public notices about the host change remain discoverable.

Without that, the website may be correct while the broader public-answer ecosystem still routes people to the wrong shell.

## Alternate-language, identity, and sitemap layers must move together

Google Search Central's current site-move guidance says new URLs should have self-referencing canonicals, multilingual/multinational `hreflang` annotations should be updated to the new URLs, and new sitemaps should be submitted.
That implies a compact election rule:
if the office moves the host, it should move the **supporting discovery identity layers** too. (xref: `google_search_central_site_move_with_url_changes_page`)

So a bounded migration review should check at minimum:
- canonicals now point to the new host,
- alternate-language clusters now point to the new host,
- the new sitemap is live,
- the old host no longer advertises itself as current except as a recovery shell,
- and organization/site identity cues now reinforce the new host rather than the superseded one.

## Minimal state taxonomy

A small taxonomy is enough:

1. **current_primary_host_stable_and_legacy_host_retained_for_recovery**
2. **planned_domain_migration_in_progress_with_verified_old_to_new_redirects**
3. **gov_transition_with_parallel_old_host_and_public_notice_overlap**
4. **emergency_replacement_host_declared_as_temporary_current_source**
5. **host_split_or_merge_under_review_not_safe_to_treat_as_stable_source_identity**
6. **legacy_host_defensively_retained_but_not_current_authoritative_entry**
7. **legacy_email_print_or_partner_routes_pending_full_host-transition_cleanup**

## Bounded host-transition trace minimum

The archive does **not** need registrar invoices, private dashboard exports, or internal DNS change tickets.
But it should be possible to reconstruct the bounded policy that governed the migration.

At minimum, the bounded trace should make it possible to reconstruct:
- which host was current before the move,
- which host became the new primary official host,
- whether the migration was an ordinary domain move, a `.gov` transition, or an emergency replacement,
- whether old-host control was retained,
- whether redirects were intended one-to-one, consolidated, tombstoned, or office/help-routed,
- whether search-side move signaling and new-sitemap publication were completed,
- whether canonicals and alternate-language declarations were updated,
- whether email / partner / printed-material transition was reviewed,
- and when the migration state was last verified.

Prefer **host labels, migration class, redirect-policy summaries, public-notice URIs, review-state flags, and timestamps** over private platform exports or registrar internals.

## Minimal claim-set

A jurisdiction can publish a compact, verifiable claim-set:

1. **Primary-host claim:** one current official host is declared as the authoritative entrypoint for the covered voter-information scope.
2. **Legacy-host control claim:** the prior host remains under trusted control long enough to prevent abandonment or impersonation risk.
3. **Redirect-policy claim:** old-host URLs either map one-to-one, consolidate with explanation, tombstone explicitly, or route to the office/help lane rather than silently failing.
4. **Search-move-support claim:** search-side move signaling, verification, and sitemap updates were reviewed/completed where applicable, but do not replace public observability.
5. **Identity-layer migration claim:** canonical, alternate-language, and site-identity signals were updated to reinforce the new host.
6. **Communications-overlap claim:** public notices, partner channels, printed materials, QR paths, and legacy email were reviewed so the broader public-answer ecosystem does not keep teaching the old host as current.
7. **Emergency-host honesty claim:** when a temporary replacement host is used, it is explicitly labeled as such and not left as an ambiguous shadow authority.

## Canonical digest artifacts

Publish **digests of host-transition policy**, not registrar internals.

- **Host Transition Surface Digest (HTSD):** digest of the bounded host-transition policy payload for a scope.
- **URL Mapping Policy Digest (UMPD):** optional digest of the migration's URL-mapping class summary.
- **Legacy Host Retention Digest (LHRD):** optional digest proving how the old host remains contained, redirected, or defensively retained.
- **Emergency Replacement Host Digest (ERHD):** optional digest proving the policy and notice state for a temporary replacement host.

## What belongs in the public host-transition payload

Keep the payload **small, state-aware, and source-host oriented**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id`
- human `migration_surface_label`
- `delivery_role_note`
- `covered_surface_refs`
- `official_source_anchors`
- `current_primary_host`
- `legacy_host_set[]`
- `migration_class`
- `url_mapping_policy_note`
- `redirect_policy_note`
- `old_domain_retention_note`
- `search_move_support_note`
- `sitemap_update_note`
- `canonical_update_note`
- `alternate_language_update_note`
- `email_transition_note`
- `partner_channel_update_note`
- `offline_materials_update_note`
- `emergency_replacement_policy_note`
- `feature_state_classes`
- `feature_trace_policy`
- `routing_fallback_uri`
- `routing_fallback_phone`
- `latest_notice_uri`
- `last_verified_at`
- optional `supersedes` / `superseded_by`

## Evidence to preserve

Preserve only what is needed to reconstruct policy:
- the old and new host labels,
- migration class,
- legacy-host retention state,
- redirect-policy class,
- whether search-move support steps were completed,
- whether sitemap/canonical/alternate-language updates were reviewed,
- whether email / partner / printed-material updates were reviewed,
- whether an emergency replacement host existed,
- and when the migration state was last verified.

Do **not** preserve private registrar credentials, full Search Console exports, internal DNS change tickets, or vendor-only migration dashboards when bounded public-policy reconstruction is sufficient.

## Relationship to the rest of the stack

Use this document when the problem is:
- whether the current official host changed,
- whether a `.gov` transition or hostname migration stayed publicly legible,
- whether the old host remained safely contained,
- whether search/discovery signals moved with the host,
- whether an emergency replacement host was explicitly bounded,
- or whether partner/email/printed lanes still teach the wrong host.

Use nearby controls when the problem is instead:
- whether a specific stale URL or expired page recovers safely after arrival (`379`),
- whether crawlability/canonical/sitemap posture is correct in steady state on the current host (`391`),
- whether site names/favicons/organization metadata identify the current official source (`392`),
- whether a page/file should be removed from search or deindexed (`394`),
- whether alternate-language clusters point to the right locale URLs after the host is already stable (`397`),
- or whether QR/shortlink carriers and printed materials need their own handoff constraints (`381`).

That boundary keeps `398` compact.
