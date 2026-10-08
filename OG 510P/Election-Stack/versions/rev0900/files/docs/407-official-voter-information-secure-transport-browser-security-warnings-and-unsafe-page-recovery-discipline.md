# 407 — Official voter-information secure transport, browser security warnings, and unsafe-page recovery discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **browser-trust and transport safety** on official voter-information pages:
whether a current official page is served over HTTPS cleanly;
whether certificate, hostname, or HSTS posture can turn an ordinary visit into a hard-stop warning;
whether mixed content or insecure third-party resources can partially break the page while making it appear secure;
and whether the office has a bounded recovery lane when browsers or Google warn users away from the page because of malware, phishing, or other unsafe content.

It does **not** replace the underlying voter-question families in `292–343`.
It does **not** replace:
- `305`, which governs the authoritative office/help lane,
- `307`, which governs formal problem-report and escalation routing,
- `380`, which governs official alert/interstitial posture,
- `392`, which governs public source identity signals,
- `398`, which governs host and domain transitions,
- `399`, which governs Search Console control-plane continuity,
- `401`, which governs page-level indexed/live diagnosis,
- `403`, which governs degraded-client recovery,
- `404`, which governs cache freshness and stale-answer eviction,
- or `405`, which governs anti-bot challenges and fail-open access posture.

It adds one narrow rule:
**if an election office expects voters to rely on a current official web page for time-sensitive instructions, that page should reach users through secure transport without mixed-content drift, should not ask users to click through browser security warnings, and should preserve a bounded official recovery lane if malware, phishing, certificate, or unsafe-resource failures cause browsers or Google to warn users away from the page.**

## Why this is a distinct surface

Vote.gov's current trust marker says official websites use `.gov` and that secure `.gov` websites use HTTPS, with the instruction to share sensitive information only on official, secure websites. The current web.dev **Enable HTTPS on your servers** guidance treats HTTPS migration as an operational discipline rather than a cosmetic flag: it recommends QA before production cutover, mixed-content detection, HTTPS redirects, and warns that HSTS clients can hard-fail on certificate mistakes. MDN's current `Strict-Transport-Security` reference says HSTS tells browsers to use HTTPS for the host and not allow users to bypass secure-connection errors such as an invalid certificate. MDN's current mixed-content guidance says mixed content and mixed downloads remain unsafe; browsers auto-upgrade only some resource types and block others, which can still leave a page partially broken. Google Search Central's current security guidance says Chrome may display a **"Deceptive site ahead"** warning for social-engineering pages, that malware/security problems are surfaced through Search Console's Security Issues report, and that security threats can produce warning or interstitial states that reduce Search traffic. (xref: `vote_gov_home_page`; xref: `web_dev_enable_https_article`; xref: `mdn_strict_transport_security_header_page`; xref: `mdn_mixed_content_page`; xref: `google_search_central_social_engineering_page`; xref: `google_search_central_malware_page`; xref: `google_search_central_prevent_malware_page`; xref: `google_search_central_debug_search_traffic_drops_page`)

That is enough to treat secure transport and unsafe-page warnings as a **public-answer integrity surface**.
A voter page can be current, indexed, fast, challenge-free, and variant-stable — yet still fail the voter because the browser shows a certificate warning, blocks key subresources, or refuses to load the page without an unsafe clickthrough.

## This surface is about first-contact trust, not generic hardening theater

The archive already has channel-hardening material elsewhere.
`407` is narrower.
It cares about the public moment when a voter reaches a current official answer page and the browser itself becomes the gatekeeper.
The bounded questions are:
- did the page arrive over secure transport without obvious browser distrust signals,
- did subresources keep the page inside a coherent secure context,
- and if not, did the office provide a safe, official recovery path instead of training the voter to ignore security warnings.

## Do not normalize clickthrough on security warnings

MDN's current HSTS reference says that if a TLS warning or error occurs for an HSTS host, the browser does not offer the user a way to proceed, because doing so would undermine strict security. The current web.dev HTTPS guidance likewise warns that clients with HSTS state are likely to hard-fail if the site later serves an expired or otherwise invalid certificate. (xref: `mdn_strict_transport_security_header_page`; xref: `web_dev_enable_https_article`)

For election information, that means the safe recovery rule is **not** "tell users to click through the warning."
The safe rule is:
- repair the secure transport failure,
- keep alternate official channels visible (`305`, `380`, `398`),
- and preserve a current official notice or help route on a still-trusted channel if the main page is temporarily unsafe.

## Mixed content can silently turn a secure-looking page into a broken answer surface

MDN's current mixed-content guidance says insecure subresources on an HTTPS page may be auto-upgraded for some media types but blocked for others, and that mixed content is still unsafe because insecure resources can be viewed or modified in transit. The current web.dev HTTPS guidance specifically recommends detecting mixed content during migration and fixing intrasite URLs, stylesheet/script references, redirects, link tags, and related declarations instead of assuming the HTML alone is enough. (xref: `mdn_mixed_content_page`; xref: `web_dev_enable_https_article`)

That matters for voter-information pages because blocked scripts, styles, maps, forms, or document viewers can make the page look officially reachable while hiding the actual instructions.
So this archive should treat mixed-content drift as a public-answer failure, not a mere console-warning nuisance.

## Third-party content can inherit the office's trust without deserving it

Google Search Central's current social-engineering guidance says embedded third-party content can cause a host page to be treated as social engineering, including pop-ups, redirections, or deceptive components that appear on an otherwise benign site. Its malware-prevention guidance also recommends choosing third-party providers carefully and monitoring site health through Search Console, `site:` checks, and Security Issues reporting. (xref: `google_search_central_social_engineering_page`; xref: `google_search_central_prevent_malware_page`)

That gives this archive a compact boundary:
critical public-answer pages should know which third-party scripts, embeds, and download paths are load-bearing;
and if a third-party dependency can trigger warnings, misleading prompts, or invisible redirect chains, the office should have a way to disable or replace that dependency without withdrawing the underlying voter-help lane.

## Browser warnings and Search warnings are different symptoms of the same public failure

Google Search Central's current traffic-drop debugging guidance says security threats such as malware or phishing can trigger warnings or interstitial pages before users reach the site, reducing Search traffic. The social-engineering and malware docs say Security Issues reporting is the place to check for these classes of problems. (xref: `google_search_central_debug_search_traffic_drops_page`; xref: `google_search_central_social_engineering_page`; xref: `google_search_central_malware_page`)

For this archive, the point is not to build a giant malware-response program inside the public-surface family.
The point is smaller:
if public voter-information pages can be blocked by browser or Google safety warnings, the office should treat that as an immediate first-contact answer failure with a bounded review/recovery lane, not as an ordinary SEO fluctuation or webmaster issue.

## Keep the official recovery/help lane stable when the primary page is unsafe

A compromised or warning-bearing page should not strand the voter.
If the main answer page is under repair, the office should keep a still-trusted official fallback visible through:
- a current help/contact page,
- a status or alert page on a trusted host,
- and other already-modeled official channels such as `370`, `380`, `383`, or `385`.

The bounded rule here is not to multiply channels.
It is to make sure that a browser-warning incident does not erase the ordinary official recovery path.

## Minimal state taxonomy

A compact policy can usually classify this surface with states such as:

- **critical_answer_routes_https_only**
- **http_to_https_redirects_present_for_public_entry_urls**
- **hsts_posture_reviewed_for_public_answer_hosts**
- **certificate_validity_monitoring_present**
- **mixed_content_zero_tolerance_for_critical_routes**
- **third_party_dependency_inventory_current_for_public_routes**
- **security_issues_monitoring_current**
- **browser_or_google_warning_recovery_lane_defined**
- **unsafe_clickthrough_instructions_not_used**
- **transport_warning_review_current**

## Bounded reconstruction minimum

A public reconstruction should keep only enough detail to answer:

- which public answer routes were expected to be HTTPS-only,
- whether HTTP entry URLs redirected cleanly to HTTPS,
- whether HSTS / certificate posture for the public host had been reviewed,
- whether critical routes were checked for mixed content or insecure downloads,
- whether load-bearing third-party dependencies were known,
- whether Search Console / browser-warning monitoring was checked,
- whether a current official recovery/help lane existed,
- and when the posture was last reviewed.

That is enough to reconstruct whether the office treated browser security warnings as a bounded public-answer problem.
It is not a reason to publish private certificate-management consoles, raw malware forensics, full scanner output, or giant endpoint inventories when smaller proofs are enough.

## Minimal claim-set

A jurisdiction can publish a compact, verifiable claim-set:

1. **Secure-transport claim:** critical public-answer routes are intended to be served only over HTTPS, with HTTP entry URLs redirected cleanly.
2. **Certificate/HSTS claim:** the office reviews certificate validity and strict-transport posture for official public-answer hosts rather than assuming users can click through failures.
3. **Mixed-content claim:** critical routes are reviewed so insecure subresources or downloads do not quietly hollow out the secure page.
4. **Third-party boundary claim:** load-bearing third-party components on critical routes are known and can be disabled or replaced if they trigger warnings or deceptive behavior.
5. **Unsafe-page recovery claim:** browser/Google unsafe warnings are treated as first-contact answer failures with a bounded review path and an alternate official recovery lane.
6. **No-clickthrough claim:** the public recovery posture does not rely on instructing users to bypass browser security warnings.

## Canonical digest artifacts

Publish **digests of transport/warning posture**, not full security telemetry.

- **Secure Transport Surface Digest (STSD):** digest of the bounded HTTPS / warning posture for public voter-information routes.
- **Mixed Content Review Digest (MCRD):** optional digest proving mixed-content review state for critical routes.
- **Unsafe Page Recovery Digest (UPRD):** optional digest proving the official recovery lane and latest controlling notice when a warning-bearing page is under repair.
- **Security Warning Review Digest (SWRD):** optional digest proving warning-monitoring review time and controlling state.

## What belongs in the public payload

Keep the payload **small, route-scoped, and non-sensitive**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id`
- human `secure_transport_surface_label`
- `delivery_role_note`
- `covered_surface_refs[]`
- `official_source_anchors[]`
- `critical_answer_routes[]`
- `https_only_boundary_note`
- `http_redirect_entrypoint_note`
- `hsts_and_certificate_posture_note`
- `mixed_content_zero_tolerance_note`
- `mixed_download_boundary_note`
- `third_party_dependency_boundary_note`
- `browser_warning_recovery_note`
- `security_issues_monitoring_note`
- `no_clickthrough_bypass_note`
- `alternate_official_notice_lane_note`
- `feature_state_classes[]`
- `feature_trace_policy`
- `routing_fallback_uri`
- `routing_fallback_phone`
- `latest_notice_uri`
- `last_verified_at`
- optional `supersedes` / `superseded_by`

## Evidence to preserve

Preserve only what is needed to reconstruct policy:
- route labels,
- HTTPS-only / redirect posture,
- HSTS/certificate review state,
- mixed-content review state,
- third-party dependency boundary state,
- warning-monitoring state,
- official recovery-lane state,
- and review time.

Do **not** preserve private TLS keys, raw certificate-management dashboards, full malware samples, giant vulnerability scanner exports, or detailed attack telemetry when bounded public-answer reconstruction is sufficient.

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:

- Which public answer routes were supposed to be reachable only through HTTPS?
- Would an ordinary HTTP entry attempt land cleanly on the HTTPS route?
- Had the office reviewed certificate/HSTS posture for the host rather than assuming users could bypass warnings?
- Could mixed content or mixed downloads silently break the page while leaving the URL looking official?
- Which third-party dependencies on critical routes could trigger warnings or deceptive behavior?
- If users or Google saw an unsafe warning/interstitial, what was the official recovery/help lane and latest controlling notice?
- Did the public posture avoid telling users to ignore or bypass browser security warnings?

## How this fits the family map

This is **not** a generic cybersecurity operations manual.
It is a bounded public-answer control.
Use it when the browser-security layer itself can stop a voter from receiving the current official answer even though the underlying content exists.

The substantive voter question still lives in the ordinary surface families.
`407` only governs whether the current official page can reach the voter without transport distrust, unsafe-resource breakage, or warning-page first contact.

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/official-voter-information-secure-transport-surface-payload.json`
- Operator quickcheck: `artifacts/checklists/official-voter-information-secure-transport-surface-checklist.md`

## Sources (pinned IDs / lockfile IDs)

- Vote.gov: home page trust marker (xref: `vote_gov_home_page`)
- web.dev: Enable HTTPS on your servers (xref: `web_dev_enable_https_article`)
- MDN: `Strict-Transport-Security` header (xref: `mdn_strict_transport_security_header_page`)
- MDN: Mixed content (xref: `mdn_mixed_content_page`)
- Google Search Central: Social engineering (phishing and deceptive sites) (xref: `google_search_central_social_engineering_page`)
- Google Search Central: Malware and unwanted software (xref: `google_search_central_malware_page`)
- Google Search Central: Preventing malware infection (xref: `google_search_central_prevent_malware_page`)
- Google Search Central: Debugging search traffic drops (xref: `google_search_central_debug_search_traffic_drops_page`)
