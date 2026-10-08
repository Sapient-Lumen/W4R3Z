# 399 — Official voter-information Search Console property coverage, ownership continuity, and emergency control-plane discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for the **search-side control plane** behind official voter-information discovery:
which Search Console properties exist for the current and legacy hosts,
which variants are verified,
who can act on removals / recrawl / move support,
how verification survives host or CMS changes,
and how access is handed over when staff, contractors, or vendors change.

It does **not** replace the underlying voter-question families in `292–343`.
It does **not** replace:
- `379`, which governs stale-link recovery after arrival,
- `391`, which governs crawlability, indexability, canonical discovery, and sitemap posture,
- `394`, which governs search removals, `noindex`, and recrawl policy,
- `398`, which governs source-host transitions and `.gov` moves,
- or `305`, which governs the public office/help route that remains the controlling recovery lane for the voter.

It adds one narrow rule:
**if an election office depends on search-side actions to keep current official voter-information pages discoverable or stale results suppressible, the Search Console control plane should cover the effective host scope, retain durable verified-owner continuity, remove stale ownership tokens during personnel/vendor changes, and stay usable during migrations or emergencies without preserving secret-heavy operator exhaust in the public archive.**

## Why this is a distinct surface

Current official guidance is enough to justify a bounded control here.

EAC's current **Effective Design for the Administration of Federal Elections** still treats clear, understandable, accessible online voter-information materials as a core election-official responsibility.
Google's current **How To Use Search Console** page says Search Console helps site owners understand how Google crawls, indexes, and serves websites and helps them optimize how their site appears in Search.
Google's current **Add a website property to Search Console** help says a property can cover an entire domain or a limited URL prefix, that a domain property spans subdomains and protocols, and that URL-prefix properties are narrower.
Google's current **Verify your site ownership** help says verified owners have the highest level of permissions, that multiple verification methods can be added, that multiple people can verify the same property, that verification lasts only while the token remains valid, and that if all verified owners lose access then all users lose access.
Google's current **Managing owners, users, and permissions** help says a property must have at least one verified owner, distinguishes verified from delegated owners, and shows that owner-grade permissions matter for actions such as Change of Address.
Google's current site-move guidance says old and new sites and their variants should be verified before a move, while its hosting-move guidance says verification must survive the infrastructure change.
Google's current recrawl guidance says you cannot request indexing for URLs you do not manage and that owner or full-user permissions are needed for URL Inspection indexing requests.
That is enough to treat search-side access continuity as a distinct public-answer control rather than as invisible webmaster housekeeping. (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`; xref: `google_search_central_search_console_start_page`; xref: `google_search_console_add_website_property_help_page`; xref: `google_search_console_verify_site_ownership_help_page`; xref: `google_search_console_manage_owners_users_permissions_help_page`; xref: `google_search_central_site_move_with_url_changes_page`; xref: `google_search_central_site_move_no_url_changes_page`; xref: `google_search_central_ask_google_to_recrawl_page`)

This matters because the public webpage is not the only thing that can fail.
A jurisdiction can have the right current page and still lose the ability to:
- request urgent recrawl,
- submit move support for a host change,
- review crawl/index issues on a new host,
- or remove stale owners/tokens after a contractor or staff turnover.

That does not make Search Console the rule source.
It makes Search Console part of the **recovery control plane** for the public-answer surface.

## Control-plane coverage should match the effective public host scope

Google's current property guidance says a **domain property** covers all protocols and subdomains for a domain, while a **URL-prefix property** covers only the exact prefix branch that was added. (xref: `google_search_console_add_website_property_help_page`)

That creates a useful election-office rule.
A bounded search-control-plane policy should not assume that one narrow property automatically covers every public voter-information shell the office actually teaches.

So a safe posture usually keeps explicit track of:
- the current primary host or domain,
- any legacy host still in recovery use,
- any temporary replacement host used in an outage or migration,
- and any narrower URL-prefix property the office relies on for a critical branch or handoff path.

The goal is not to maximize the number of properties.
The goal is to make sure the control plane actually covers the public hostnames and paths the voter may be sent to.

## Durable verified-owner continuity matters more than nominal user access

Google's current ownership help says multiple verification methods can be added and multiple people can verify the same property.
The same help says verification lasts only while the token remains valid and that if all verified owners lose access then all users lose access.
Google's permissions help says a property must have at least one verified owner and that delegated owners depend on that verified-owner substrate. (xref: `google_search_console_verify_site_ownership_help_page`; xref: `google_search_console_manage_owners_users_permissions_help_page`)

That means a bounded policy should prefer durable organizational continuity over single-person convenience.
For an election office, the risky posture is not merely “too few users.”
It is **one fragile verified-owner path** that disappears when a template changes, a DNS record is dropped, or the only verified owner leaves.

So the office should keep enough verified-owner continuity that urgent public-surface recovery does not depend on one person or one brittle token.

## Remove stale ownership tokens when people or vendors change

Google's current permissions help says that when you remove an owner from a property, their verification tokens are not deleted or revoked, and if a deleted owner's token remains for the property, that deleted owner can re-verify ownership. (xref: `google_search_console_manage_owners_users_permissions_help_page`)

That is a high-value, easy-to-miss election-office rule.
Removing a user in the interface is not the same thing as retiring the underlying verification path.

So contractor offboarding, vendor transitions, CMS rebuilds, and emergency agency-to-agency handoffs should review not only visible users but also the underlying verification methods that still exist on the site or in DNS.

## Owner-grade actions should be treated as emergency-response dependencies

Google's current permissions help shows that some sensitive actions—such as **Change of Address** and ownership/user management—are owner-grade actions.
Google's current recrawl guidance says URL Inspection indexing requests require owner or full-user permissions and only work for URLs you manage. (xref: `google_search_console_manage_owners_users_permissions_help_page`; xref: `google_search_central_ask_google_to_recrawl_page`)

That means the search-side emergency lane should not be modeled as “someone probably has access somewhere.”
A bounded policy should know in advance whether the office can actually perform the recovery actions it might need during:
- a stale-result incident,
- a rapid move to a replacement host,
- a broken verification token after a CMS cutover,
- or a post-election cleanup of superseded pages.

## Site and hosting moves can silently break verification

Google's current site-move guidance says offices should verify the old and new sites and all relevant variants before a move.
It also says verification should continue to work after the move and specifically warns that HTML-file or template-based verification artifacts must be preserved in the new copy.
Google's current hosting-move guidance repeats that verification must continue to work after an infrastructure move and says a temporary hostname may also need verification for testing/inspection. (xref: `google_search_central_site_move_with_url_changes_page`; xref: `google_search_central_site_move_no_url_changes_page`)

So this control surface should explicitly track whether verification continuity was reviewed during:
- domain changes,
- subdomain splits or merges,
- CMS rebuilds,
- hosting-provider moves,
- and temporary-host testing.

Otherwise the office can discover the access failure only when it most needs the recovery tool.

## Search Console is a recovery aid, not the public authority

Search Console MAY help an election office diagnose or accelerate recovery on a public surface.
It MUST NOT become the thing the voter is expected to trust or consult directly.

The controlling public artifact remains the current official page, notice, directory entry, or office/help lane.
The search-side control plane is only the bounded operator layer that helps keep those public artifacts legible in search.

So the archive should preserve only enough public-policy trace to show:
- which property classes were intended,
- whether verified-owner continuity existed,
- whether stale tokens were reviewed,
- whether migration/emergency access was tested,
- and when that state was last checked.

It should not preserve secrets, raw console exports, or individualized operational dashboards.

## Minimal state taxonomy

A compact policy can usually classify this control surface with states such as:

- **covered_domain_property_plus_current_prefixes**
- **minimum_viable_verified_owner_continuity_present**
- **single_verified_owner_or_single_token_fragility**
- **legacy_host_or_replacement_host_property_missing**
- **stale_owner_token_cleanup_pending**
- **migration_verification_continuity_review_pending**
- **emergency_recrawl_or_move_action_path_not_rehearsed**
- **control_plane_access_degraded_but_public_host_still_current**

## Bounded control-plane trace minimum

A public, bounded reconstruction should keep only enough detail to answer:
- which property scopes were intended,
- which host classes were covered,
- whether verified-owner continuity existed,
- whether stale-token cleanup was reviewed,
- whether migration/hosting continuity was reviewed,
- whether urgent recovery actions were considered operable,
- and when the control plane was last checked.

That is enough to reconstruct whether the office was ready to keep the public search surface recoverable.
It is not a reason to publish secrets.

## Minimal claim-set

A jurisdiction can publish a compact, verifiable claim-set:

1. **Coverage claim:** Search Console property coverage matches the current host scope the public is actually taught to use.
2. **Continuity claim:** the office maintains durable verified-owner continuity rather than depending on one fragile operator/token path.
3. **Token-retirement claim:** personnel/vendor changes include a review of underlying verification methods, not only visible user removal.
4. **Migration claim:** host or infrastructure moves review whether verification survives into the new environment.
5. **Emergency-action claim:** urgent recrawl / move-support / search-side recovery actions remain operable for managed URLs when needed.
6. **Boundary claim:** search-side control remains subordinate to the current official public page/notice/help lane rather than becoming a hidden authority source.

## Canonical digest artifacts

Publish **digests of control-plane policy**, not secrets.

- **Search Control Plane Surface Digest (SCPSD):** digest of the bounded control-plane policy payload for a scope.
- **Verified Owner Continuity Digest (VOCD):** optional digest proving the owner-continuity class and review state.
- **Verification Method Review Digest (VMRD):** optional digest proving whether stale tokens and fallback methods were reviewed.
- **Migration Verification Continuity Digest (MVCD):** optional digest proving that host/hosting moves checked verification continuity.

## What belongs in the public control-plane payload

Keep the payload **small, role-aware, and non-secret**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id`
- human `search_control_plane_surface_label`
- `delivery_role_note`
- `covered_surface_refs`
- `official_source_anchors`
- `property_scope_set[]`
- `default_property_scope_state_class`
- `verified_owner_continuity_note`
- `verification_method_diversity_note`
- `stale_token_retirement_note`
- `migration_verification_continuity_note`
- `emergency_action_operability_note`
- `feature_state_classes`
- `feature_trace_policy`
- `routing_fallback_uri`
- `routing_fallback_phone`
- `latest_notice_uri`
- `last_verified_at`
- optional `supersedes` / `superseded_by`

## Evidence to preserve

Preserve only what is needed to reconstruct policy:
- intended property scopes,
- host-coverage class,
- verified-owner continuity class,
- stale-token review state,
- migration/hosting continuity review state,
- urgent-action operability state,
- and when the control plane was last checked.

Do **not** preserve raw verification tokens, DNS record values, private admin email lists, full Search Console exports, or operator screenshots when bounded public-policy reconstruction is sufficient.

## Relationship to the rest of the stack

Use this document when the problem is:
- whether the office can still act in the search-side control plane,
- whether old/new/replacement hosts are actually covered by verified properties,
- whether verified-owner continuity is fragile,
- whether stale ownership tokens were retired after personnel/vendor changes,
- or whether a migration or hosting move silently broke recovery access.

Use nearby controls when the problem is instead:
- crawlability, indexing, canonical discovery, or sitemap posture on the public site itself (`391`),
- stale-result removal, `noindex`, or recrawl policy (`394`),
- domain migration / `.gov` transition and public host continuity (`398`),
- the public office/help lane voters should actually trust (`305`),
- or page-level stale-link recovery once someone has already landed (`379`).

That boundary keeps `399` compact.
It is not “webmaster operations in general.”
It is the bounded Search Console property/access continuity layer that keeps official voter-information search recovery usable.
