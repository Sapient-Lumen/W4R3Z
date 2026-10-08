# 405 — Official voter-information anti-bot challenges, CAPTCHA, WAF, and human-verification fail-open discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for the **abuse-protection layer** around official voter-information websites:
whether current public-answer pages are allowed to sit behind CAPTCHA walls, managed bot challenges, or aggressive WAF/rate-limit interstitials,
whether crawler access and challenge responses are explicit enough that search does not quietly lose the official page,
and whether a jurisdiction keeps an accessible human-help lane when abuse controls trip on a real voter.

It does **not** replace the underlying voter-question families in `292–343`.
It does **not** replace:
- `305`, which governs the authoritative office/help lane,
- `307`, which governs formal problem-report and escalation routing,
- `373`, which governs public forms/applications/affidavits and version-acceptance discipline,
- `375`, which governs official site-search surfaces,
- `391`, which governs crawlability, indexability, and canonical discovery,
- `401`, which governs page-level indexed/live/render diagnosis,
- `403`, which governs progressive enhancement and degraded-client recovery,
- or `404`, which governs cache freshness and stale-answer eviction.

It adds one narrow rule:
**if an election office expects voters to rely on current official web pages for time-sensitive answers, generic read-only answer pages should not quietly disappear behind anti-bot challenge walls, abuse controls should be scoped more aggressively to write or abuse-sensitive actions than to basic public information, unavoidable human-verification steps should keep an accessible fallback and a visible official help lane, crawler verification/allow posture should be explicit rather than accidental, and the archive should preserve only bounded challenge-state evidence rather than raw bot telemetry or invasive fingerprints.**

## Why this is a distinct surface

The EAC's current **Effective Design for the Administration of Federal Elections** says online voter-information materials are a core responsibility for election officials and partners, and frames usability, clarity, and accuracy as central design concerns for those materials. (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`)

Current accessibility and search guidance is enough to justify a compact control here.
Section508.gov's current **Guide to Accessible Web Design & Development** says that if a CAPTCHA is used it should have a text alternative describing its purpose and an alternate form using a different modality, warns teams to choose CAPTCHA providers that are already 508-conformant and not image-reliant, and says complete processes and non-interference rules still apply.
W3C WAI's current **Introduction to “Inaccessibility of CAPTCHA”** says CAPTCHA-style robot tests block many humans with disabilities, not just bots.
Google Search Central's current **Google Search technical requirements** says Google can only index pages that are publicly accessible to Googlebot and not blocked from crawling.
Google Search Central's current **Googlebot** documentation says operators should verify problematic traffic before blocking it and can do that through reverse DNS lookup or Googlebot IP ranges.
Google Search Central's current **Crawling December: CDNs and crawling** post says overprotective CDNs can block wanted crawlers in WAFs, challenge interstitials may be all the crawler sees, and recommends returning `503` to automated clients for temporary bot-verification interstitials so content is not automatically dropped from the index. (xref: `section508_guide_accessible_web_design_development_page`; xref: `w3c_wai_intro_inaccessibility_of_captcha_page`; xref: `google_search_central_technical_requirements_page`; xref: `google_search_central_googlebot_page`; xref: `google_search_central_crawling_december_cdns_page`)

That is enough to treat anti-bot controls as a **public-answer integrity surface**.
A page can be current, indexed in principle, fast, JavaScript-resilient, and cache-correct — yet still fail the voter because the visible experience is only a challenge screen, a retry loop, or a blocked request.

## Read-only public answers and abuse-sensitive actions should not inherit the same challenge posture

Election offices often need some abuse controls.
Forms can be spammed.
Lookups can be scraped.
Search endpoints can be hammered.
That does **not** mean every current-answer page should inherit the same challenge wall.

For this archive, the compact distinction is:
- homepage, deadline page, early-voting page, polling-place page, office/help page, and other ordinary read-only public answer pages are **basic public-answer routes**,
- while search submissions, report/problem forms, contact forms, lookup-heavy endpoints, or repeat-write actions may be **abuse-sensitive routes**.

Those classes should not share one invisible default.
If basic public-answer routes are challenge-gated by default, the office has turned abuse control into a first-contact access control on public election information.

## If CAPTCHA is used, accessibility is not optional

Section508.gov's current guide is direct: if a CAPTCHA is used, it should have a text alternative describing its purpose and an alternate form using a different modality, and teams should prefer providers that are already 508-conformant and do not rely on images. (xref: `section508_guide_accessible_web_design_development_page`)

W3C WAI's CAPTCHA introduction adds the harder truth: many of these tests are designed to block software robots, but they also block humans who are blind, deaf, hard of hearing, low-vision, or who have some cognitive/intellectual disabilities. (xref: `w3c_wai_intro_inaccessibility_of_captcha_page`)

For election information, that means a challenge step is not a neutral inconvenience.
It can become the moment a voter loses independent access to a deadline-critical answer.
So this document does **not** say “never mitigate abuse.”
It says that when human verification is unavoidable, the office should preserve:
- a bounded accessible alternative,
- a visible direct help/contact lane,
- and a small enough scope that a generic public answer page is not casually treated like a hostile write endpoint.

## Complete-process and non-interference logic still matter

Section508.gov's current guide also says complete processes must conform across all pages in the process, and technologies that are not relied upon for conformance should not block access to the rest of the page. (xref: `section508_guide_accessible_web_design_development_page`)

That matters because election sites often put challenge logic in front of a larger flow without treating the challenge step as part of the public service itself.
Operationally, it is part of the service.
If the challenge fails, the voter never reaches the answer, form, or help route.
So a compact archive posture should record whether anti-bot controls preserve the process or break it.

## Search and crawler access should be explicit, not accidental collateral damage

Google Search Central's technical requirements say a page must be accessible to Googlebot and not blocked if it is going to be indexed. (xref: `google_search_central_technical_requirements_page`)
Google's current Googlebot documentation says operators should verify that suspicious traffic really is Googlebot before blocking it. (xref: `google_search_central_googlebot_page`)

That is especially important when a CDN or WAF is learning automatically.
If a challenge system treats wanted crawlers as suspicious by default, the search layer stops being a discovery path to current official answers.
For this archive, a jurisdiction should know:
- whether the crawlers it relies on for public discovery are verified,
- whether those crawlers are intentionally allowlisted or otherwise protected from accidental challenge flows where appropriate,
- and whether the office can distinguish malicious scraping from the ordinary crawler traffic it actually depends on.

## Bot-verification interstitials should not masquerade as successful page fetches

Google Search Central's current CDN guidance says challenge interstitials may be all a crawler sees, and recommends sending `503` to automated clients like crawlers when the block is temporary so the content is not removed from the index automatically. It also warns that random error pages returned with HTTP `200` can be particularly damaging. (xref: `google_search_central_crawling_december_cdns_page`)

That gives this archive a compact rule:
- a temporary challenge state for an automated client should look like temporary unavailability, not like a successful fetch of the official answer page,
- and a generic challenge/interstitial page should not quietly become the crawl-visible representation of the URL.

This document does **not** prescribe one vendor-specific WAF recipe.
It does say the operator should understand whether challenge pages are being returned with semantically wrong success status codes.

## Prefer scoped throttling and read/write separation over universal challenge walls

The safest anti-bot posture for public voter information is usually not “challenge everything.”
It is usually some combination of:
- lighter or no challenge on basic public-answer routes,
- stronger protection on abuse-sensitive write or high-volume lookup routes,
- and a clear human-help fallback when a real voter is caught anyway.

That keeps the abuse-control layer subordinate to the public-service mission.
A voter should not need to prove humanity just to read the current official office hours, deadline, or polling-place change notice unless the office can explain why that extraordinary posture is temporarily necessary.

## Keep the office/help lane visible when challenge state is in force

A challenge surface does not become the authority source.
The authority source remains the current official page, notice, or office/help route.
This document only governs whether anti-bot controls prevent access to that authority source.

So the archive should preserve only enough trace to show:
- which critical public-answer routes are challenge-exempt or minimally challenged,
- which abuse-sensitive routes may invoke stronger controls,
- whether accessible alternatives exist when CAPTCHA is used,
- whether official help/contact recovery is visible from challenge state,
- whether crawler verification/allow posture exists,
- whether temporary challenge states return semantically correct non-`200` responses to crawlers,
- and when that posture was last reviewed.

It should not preserve raw WAF logs, device fingerprints, browser-fingerprint recipes, IP blocklists for the whole public, or full anti-abuse telemetry streams when bounded policy reconstruction is enough.

## Minimal state taxonomy

A compact policy can usually classify this surface with states such as:

- **basic_public_answer_routes_classified**
- **abuse_sensitive_routes_classified**
- **basic_public_answer_routes_not_default_challenge_gated**
- **captcha_accessible_alternative_present**
- **official_help_recovery_visible_from_challenge_state**
- **crawler_identity_verification_runbook_present**
- **wanted_crawlers_not_accidentally_waf_blocked**
- **temporary_bot_interstitial_returns_503_to_crawlers**
- **challenge_200_soft_block_risk_detected**
- **challenge_trigger_review_current**

## Bounded challenge-trace minimum

A public, bounded reconstruction should keep only enough detail to answer:
- which routes are treated as basic public answers versus abuse-sensitive actions,
- whether challenge gating is absent or tightly constrained on basic public-answer routes,
- whether accessible alternatives exist when human verification is used,
- whether the office/help lane is visible from challenge state,
- whether wanted crawler verification/allow posture exists,
- whether temporary crawler challenge responses avoid misleading `200` success semantics,
- and when the review happened.

That is enough to reconstruct whether the office treated anti-bot controls as a bounded integrity problem.
It is not a reason to publish raw anti-abuse telemetry.

## Minimal claim-set

A jurisdiction can publish a compact, verifiable claim-set:

1. **Route-classification claim:** the office identified a small set of basic public-answer routes and a smaller set of abuse-sensitive routes instead of challenge-gating everything by accident.
2. **Public-answer access claim:** basic read-only public-answer routes are not defaulted into opaque human-verification walls without explicit review.
3. **Accessibility claim:** when CAPTCHA or similar human-verification steps are used, accessible alternatives and a direct official help lane exist.
4. **Crawler-access claim:** the office can verify the crawlers it depends on and does not leave them subject to accidental WAF/CDN challenge drift.
5. **Status-code claim:** temporary bot-verification interstitials for crawlers do not masquerade as successful `200` fetches of the official answer page.
6. **Review-discipline claim:** anti-bot trigger posture and fallback paths are reviewed on a bounded cadence and after major CDN/WAF or traffic-shaping changes.

## Canonical digest artifacts

Publish **digests of challenge posture**, not raw bot telemetry.

- **Challenge Posture Surface Digest (CPSD):** digest of the bounded anti-bot/challenge policy payload.
- **Crawler Access Posture Digest (CAPD):** optional digest proving crawler verification and allow posture.
- **Accessible Challenge Recovery Digest (ACRD):** optional digest proving challenge-state fallback/help posture.
- **Temporary Challenge Response Digest (TCRD):** optional digest proving non-`200` temporary-interstitial posture for automated clients.

## What belongs in the public payload

Keep the payload **small, challenge-aware, and role-aware**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id`
- human `anti_bot_surface_label`
- `delivery_role_note`
- `covered_surface_refs[]`
- `official_source_anchors[]`
- `basic_public_answer_routes[]`
- `abuse_sensitive_routes[]`
- `challenge_scope_policy_note`
- `captcha_accessibility_note`
- `human_recovery_help_note`
- `crawler_verification_note`
- `wanted_crawler_allow_posture_note`
- `temporary_interstitial_status_note`
- `rate_limit_and_retry_note`
- `feature_state_classes[]`
- `feature_trace_policy`
- `routing_fallback_uri`
- `routing_fallback_phone`
- `latest_notice_uri`
- `last_verified_at`
- optional `supersedes` / `superseded_by`

## Evidence to preserve

Preserve only what is needed to reconstruct policy:
- basic-public-route labels,
- abuse-sensitive route labels,
- challenge-scope policy state,
- accessible-alternative state,
- help-lane visibility state,
- crawler verification/allow posture,
- temporary interstitial response posture,
- and review time.

Do **not** preserve raw WAF logs, device-fingerprint recipes, full IP blocklists, browser fingerprint data, session replays, or giant vendor debug exports when bounded policy reconstruction is sufficient.

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:
- Which official voter-information routes were treated as basic public answers rather than abuse-sensitive routes?
- Were basic public-answer routes left reachable without opaque challenge walls?
- If human verification was used, what accessible alternative and direct help path existed?
- Could the office verify and protect the crawlers it depended on for public discovery?
- Did temporary crawler challenge states return semantically correct non-`200` responses?
- When was the anti-bot posture last reviewed after WAF/CDN changes or traffic spikes?

## How this fits the family map

This is **not** a general bot-management handbook or anti-scraping manifesto.
It is a bounded public-answer control for the narrow anti-bot decisions that determine whether current official voter-information pages stay reachable to humans and discoverable to search.

Use it when the page is current, maybe even otherwise healthy, but the visible first contact is a challenge wall, retry loop, or accidental crawler block rather than the current official answer.

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/official-voter-information-anti-bot-challenge-surface-payload.json`
- Operator quickcheck: `artifacts/checklists/official-voter-information-anti-bot-challenge-surface-checklist.md`

## Sources (pinned IDs / lockfile IDs)

- EAC: Effective Design for the Administration of Federal Elections (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`)
- Section508.gov: Guide to Accessible Web Design & Development (xref: `section508_guide_accessible_web_design_development_page`)
- W3C WAI: Introduction to “Inaccessibility of CAPTCHA” (xref: `w3c_wai_intro_inaccessibility_of_captcha_page`)
- Google Search Central: Google Search technical requirements (xref: `google_search_central_technical_requirements_page`)
- Google Search Central: Googlebot (xref: `google_search_central_googlebot_page`)
- Google Search Central Blog: Crawling December — CDNs and crawling (xref: `google_search_central_crawling_december_cdns_page`)
