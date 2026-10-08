# 406 — Official voter-information request-context variance, personalization, and experiment-boundary discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **same-URL answer variance** on official voter-information websites:
whether a current official page changes meaning based on language hints, country or geolocation inference, cookie state, experiment bucket, client hints, or other request-context dimensions;
whether those dimensions are explicit enough that caches, crawlers, and operators can tell why the page changed;
and whether a jurisdiction keeps critical public-answer fields outside personalization and experimentation systems that can silently produce conflicting first-contact answers.

It does **not** replace the underlying voter-question families in `292–343`.
It does **not** replace:
- `305`, which governs the authoritative office/help lane,
- `307`, which governs formal problem-report and escalation routing,
- `374`, which governs official routers and decision-path trace discipline,
- `376`, which governs map, geolocation, and directions surfaces,
- `377`, which governs language selectors and machine-translation boundaries,
- `391`, which governs crawlability, indexability, and canonical discovery,
- `397`, which governs alternate-language discovery and locale-adaptive crawl posture,
- `400`, which governs search observability,
- `401`, which governs page-level indexed/live/render diagnosis,
- `404`, which governs cache freshness and stale-answer eviction,
- or `405`, which governs anti-bot challenges and crawler-access fail-open posture.

It adds one narrow rule:
**if an election office expects voters to rely on a current official URL for time-sensitive answers, the office should know which request-context dimensions can change that page, treat explicit user choices differently from silent ambient adaptation, keep critical answer semantics out of personalization and experiment systems, declare request-header-dependent variance clearly enough that caches and diagnosis do not guess, and preserve only bounded variant traces rather than raw targeting or tracking exhaust.**

## Why this is a distinct surface

Digital.gov's current **Requirements for delivering a digital-first public experience** says public digital services should provide content that is authoritative and easy to understand, information and services that are discoverable and optimized for search, user-centered and data-driven design, customized and dynamic user experiences, and mobile-first design that scales across device sizes.
Digital.gov's current **An introduction to federal website standards** says it is critical that government websites and digital services are effective and easy to use, and that the standards help agencies provide high-quality, consistent digital experiences for everyone.
Google Search Central's current **How Google crawls locale-adaptive pages** says locale-adaptive pages can return different content based on perceived country or preferred language, that Google might not crawl or index all locale variants, that Googlebot sends requests without `Accept-Language`, and that separate locale URLs with `rel="alternate" hreflang` are recommended.
Google Search Central's current **A/B testing best practices for Search** says operators should not cloak test pages, notes that Googlebot generally does not support cookies and will therefore usually see the no-cookie variant, recommends canonical links for alternate test URLs, recommends `302` rather than `301` redirects for temporary test redirects, and says experiments should run only as long as necessary.
MDN's current **Vary header** reference says the `Vary` response header describes which parts of the request influenced the response and that the same `Vary` value should be used on all responses for a given URL, including `304 Not Modified` responses. (xref: `digital_gov_requirements_digital_first_public_experience_page`; xref: `digital_gov_intro_federal_website_standards_page`; xref: `google_search_central_locale_adaptive_pages_page`; xref: `google_search_central_website_testing_page`; xref: `mdn_vary_header_page`)

That is enough to treat request-context variance as a **public-answer integrity surface**.
A page can be current, indexed, fast, JavaScript-resilient, cache-correct, and challenge-free — yet still fail the voter because the answer silently changes with cookie state, experiment assignment, perceived geography, or other invisible request context.

## Explicit user choice is different from silent ambient adaptation

Not every variant is bad.
A voter deliberately choosing Spanish, a county selector, or an election selector is different from a page silently changing because the edge inferred location, because a consent cookie was present, or because an experiment framework assigned a bucket.

The compact distinction for this archive is:

- **explicit user-choice dimensions** are things the voter can see and intentionally control, such as a visible language selector or jurisdiction/election selector,
- while **ambient variant dimensions** are things the voter usually cannot see directly, such as cookie presence, inferred geography, experiment assignment, user-agent class, or client-hint inputs.

The more a critical answer depends on ambient dimensions, the more likely the office is to create hidden first-contact disagreement.

## Critical public-answer semantics should not become experiment buckets

Google's testing guidance does not ban experiments.
It does, however, draw hard lines around cloaking, temporary redirects, canonical grouping, cookie-visible variants, and running tests longer than necessary. (xref: `google_search_central_website_testing_page`)

For election information, that means experimentation should stay away from the fields that determine what the voter is told to do right now:
- deadline text,
- polling-place or drop-box routing,
- office/help recovery lanes,
- election-scope labels,
- and other action-changing instructions.

Testing button color, layout emphasis, or non-authoritative ornament is different from testing which deadline or route the page presents as controlling.
The archive should record that distinction explicitly.

## The no-cookie / first-visit path matters because it is often what crawlers and many voters see

Google Search Central's current testing guidance says Googlebot generally does not support cookies and will usually see the version accessible to users who do not accept cookies. (xref: `google_search_central_website_testing_page`)

That is a useful public-service constraint even beyond search.
A first-visit voter, a privacy-hardened browser, an in-app webview, or a user who cleared storage may also land on the no-cookie path.
So a compact archive posture should ask whether the **no-cookie / first-visit** variant remains authoritative for critical public answers instead of serving a weaker, stale, or placeholder shell.

## Locale and region variance should be explicit enough that the office can explain what changed

Google Search Central's locale-adaptive guidance says locale-adaptive pages may not be fully crawled or indexed for all locales and recommends separate locale URLs with `hreflang` where possible. (xref: `google_search_central_locale_adaptive_pages_page`)

This document does **not** say that every jurisdiction must create a giant locale matrix.
It does say that when language or region materially changes the official answer, the office should prefer explicit boundaries over hidden guessing:
- stable locale URLs where appropriate,
- visible language/jurisdiction cues,
- and clear fallback when the office cannot safely infer the right variant.

That keeps `397` compact:
`397` is about alternate-language discovery and crawl posture.
`406` is about the broader integrity question of whether the same apparent public URL is secretly serving materially different answers by context.

## If request headers influence the response, caches and diagnosis should not be left to infer that fact

MDN's current `Vary` reference says the header tells caches which parts of the request influenced the response and that the same `Vary` value should be used on all responses for a given URL, including `304` responses. (xref: `mdn_vary_header_page`)

That gives this archive a compact operational rule:
if a response changes because of request headers, the operator should know which dimensions are in play and should not leave caches or later diagnosis to guess.

This document does **not** prescribe a vendor-specific CDN recipe.
It does say the office should be able to name:
- which request dimensions can affect the current official page,
- whether those dimensions are explicit user choices or ambient adaptation,
- and whether the cache/diagnosis surface is told enough to separate those variants cleanly.

## Preserve bounded variant traces, not raw targeting data

This archive already has a compact request-context notation in `224` and bounded divergence bundles in `222`.
`406` keeps that posture.
The office usually does **not** need raw cookies, targeting rules, user identifiers, or full experiment telemetry in the archive to prove that same-URL variance was or was not under control.

What usually matters is smaller:
- which variant dimensions existed,
- whether any were ambient,
- whether critical answer fields were exempt from experimentation,
- whether the no-cookie / first-visit path remained authoritative,
- whether `Vary` or equivalent variance declaration was present where applicable,
- and when the posture was reviewed.

## Keep the office/help lane and current-source anchor invariant across variants

A variant system should not quietly swap out the core recovery lane.
Even where language, routing, or presentational differences exist, the page should preserve a stable path back to the authoritative office/help lane and current notice source.
That reduces the risk that one experiment bucket or geo edge rule strands the voter without the ordinary recovery path.

## Minimal state taxonomy

A compact policy can usually classify this surface with states such as:

- **explicit_user_choice_dimensions_classified**
- **ambient_variant_dimensions_classified**
- **critical_answer_fields_not_subject_to_experiment**
- **no_cookie_first_visit_variant_authoritative**
- **locale_or_region_variants_use_explicit_boundaries**
- **request_header_variant_dimensions_declared**
- **same_vary_posture_used_on_default_and_304_responses**
- **bounded_request_context_trace_available**
- **hidden_cookie_or_geo_semantic_drift_detected**
- **variant_review_current**

## Bounded variant-trace minimum

A public, bounded reconstruction should keep only enough detail to answer:

- which dimensions could change the public answer,
- which of those dimensions were explicit user choices versus ambient adaptation,
- whether critical answer fields were excluded from experimentation or personalization,
- whether the no-cookie / first-visit path remained authoritative,
- whether request-header-dependent variance was declared clearly enough for cache and diagnostic reconstruction,
- whether locale or region differences used explicit boundaries where material,
- and when the review happened.

That is enough to reconstruct whether the office treated same-URL variance as a bounded integrity problem.
It is not a reason to publish cookies, identifiers, raw experiment telemetry, or audience-targeting rules.

## Minimal claim-set

A jurisdiction can publish a compact, verifiable claim-set:

1. **Variant-inventory claim:** the office identified which request-context dimensions can change the page and distinguished explicit user-choice dimensions from ambient variant dimensions.
2. **Authoritative-first-visit claim:** the no-cookie / first-visit path remains authoritative for critical public answers.
3. **Experiment-boundary claim:** critical public-answer fields are not subject to A/B testing, personalization, or silent bucket drift.
4. **Explicit-boundaries claim:** material locale or region differences use explicit routing or visible cues rather than hidden guessing where practicable.
5. **Variance-declaration claim:** request-header-dependent variants are declared clearly enough for cache and diagnostic reconstruction.
6. **Review-discipline claim:** variant posture is re-checked after major edge, experimentation, consent, localization, or routing changes.

## Canonical digest artifacts

Publish **digests of variance posture**, not raw targeting data.

- **Variance Surface Digest (VSD):** digest of the bounded request-context variance policy payload.
- **Variant Boundary Digest (VBD):** optional digest proving which dimensions are explicit user choices versus ambient adaptation.
- **No-Cookie Authoritative Path Digest (NCAPD):** optional digest proving first-visit/no-cookie posture for critical public answers.
- **Variant Review Digest (VRD):** optional digest proving review time and controlling notice.

## What belongs in the public payload

Keep the payload **small, context-aware, and anti-targeting**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id`
- human `variance_surface_label`
- `delivery_role_note`
- `covered_surface_refs[]`
- `official_source_anchors[]`
- `explicit_user_choice_dimensions[]`
- `ambient_variant_dimensions[]`
- `critical_answer_fields_not_subject_to_experiment[]`
- `variant_policy_note`
- `no_cookie_first_visit_note`
- `user_choice_persistence_note`
- `vary_header_note`
- `experiment_boundary_note`
- `crawler_visibility_note`
- `fallback_help_note`
- `feature_state_classes[]`
- `feature_trace_policy`
- `routing_fallback_uri`
- `routing_fallback_phone`
- `latest_notice_uri`
- `last_verified_at`
- optional `supersedes` / `superseded_by`

## Evidence to preserve

Preserve only what is needed to reconstruct policy:
- dimension labels,
- explicit-vs-ambient classification,
- critical-answer-field experiment boundary state,
- first-visit/no-cookie state,
- request-header variance declaration state,
- visible fallback/help-lane state,
- and review time.

Do **not** preserve raw cookies, user identifiers, audience-targeting segments, experiment-assignment logs, full analytics exports, or giant edge-debug dumps when bounded policy reconstruction is sufficient.

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:

- Which request-context dimensions could change the official voter-information page?
- Which dimensions were visible user choices and which were ambient adaptation?
- Could a first-visit or no-cookie user still get the authoritative current answer?
- Were critical answer fields protected from experimentation and personalization drift?
- If locale or region changed the answer materially, were those boundaries explicit and explainable?
- Did the response declare request-header-dependent variance clearly enough that cache and diagnosis did not have to guess?
- When was the variant posture last reviewed after experimentation, localization, consent, or edge-routing changes?

## How this fits the family map

This is **not** a generic personalization playbook or marketing-optimization guide.
It is a bounded public-answer control for the narrow decisions that determine whether the same official URL quietly tells different voters different things for reasons the office can no longer explain.

Use it when the page is current and reachable but two users, two probes, or a crawler and a voter appear to get different first-contact answers from the same public path.

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/official-voter-information-request-context-variance-surface-payload.json`
- Operator quickcheck: `artifacts/checklists/official-voter-information-request-context-variance-surface-checklist.md`

## Sources (pinned IDs / lockfile IDs)

- Digital.gov: Requirements for delivering a digital-first public experience (xref: `digital_gov_requirements_digital_first_public_experience_page`)
- Digital.gov: An introduction to federal website standards (xref: `digital_gov_intro_federal_website_standards_page`)
- Google Search Central: How Google crawls locale-adaptive pages (xref: `google_search_central_locale_adaptive_pages_page`)
- Google Search Central: A/B testing best practices for Search (xref: `google_search_central_website_testing_page`)
- MDN: Vary header (xref: `mdn_vary_header_page`)
