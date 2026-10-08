# 381 — Official voter-information QR codes, short URLs, and printed-to-digital handoff discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **official voter-information QR codes, short URLs, vanity paths, printed or posted scannable codes, and other public handoff tokens that bridge a voter from print/signage/social/video surfaces into a live digital destination**.

It does **not** replace the underlying voter-question families in `292–343`.
It does **not** replace:
- `305`, which governs the authoritative office/help route,
- `366`, which governs short-form alerts, social posts, texts, and app notifications,
- `368`, which governs printable handouts, postcards, flyers, and brochures,
- `372`, which governs physical-site signage and wayfinding,
- `374`, which governs interactive routers,
- `378`, which governs file-download / viewer handoff,
- `379`, which governs stale-link recovery,
- or `380`, which governs on-site alerts and interstitials.

It adds one narrow rule:
**if an election office expects voters to act through a QR code, short URL, or vanity path, that handoff should stay inside a trusted official domain posture where possible, preserve a human-readable fallback, resolve to the current official destination rather than a hidden surprise action, and remain recoverable when the original printed or posted carrier goes stale.**

## Why this is a distinct surface

Current official guidance is enough to justify a bounded control here.

Digital.gov's current **Introduction to QR codes** says QR codes bridge the online and offline worlds, are not right for every context, may introduce security issues, and in some cases should give way to another tool such as a URL shortener.  
Section508.gov's current **Accessible QR Code Implementation** says QR codes used as electronic content can be treated as ICT, need an equivalent text alternative, should include a nearby text link or URL, should avoid automatic actions like immediate downloads or texts, and should be tested with assistive technology.  
Digital.gov's current guidance on **.gov domains** says `.gov` domains increase security, trust, and accountability; that official government information, communications, and services should use `.gov` or `.mil`; and that good government domain names should be memorable, concise, and clearly describe the service.  
Vote.gov's current trust marker says official websites use `.gov`, secure `.gov` websites use HTTPS, and sensitive information should be shared only on official, secure websites.  
USWDS's current **Link** guidance adds that government sites should use meaningful link text, link directly to the most relevant page, identify external links clearly, and avoid disruptive notifications.  
And EAC's current **Effective Design for the Administration of Federal Elections** says voter-information materials should be clear, understandable, accessible, usable, and accurate. (xref: `digital_gov_introduction_to_qr_codes_page`; xref: `section508_accessible_qr_code_implementation_page`; xref: `digital_gov_requirements_registration_use_gov_domains_page`; xref: `vote_gov_home_page`; xref: `uswds_link_component_page`; xref: `eac_effective_design_for_the_administration_of_federal_elections_page`)

That is enough to treat QR/shortlink handoffs as a real public-answer control surface.
They are not mere decoration on top of a page.
They often decide **which destination a voter reaches first, whether the user can verify the destination before following it, and whether an old printed/poster/social artifact quietly remains the operative path long after the target changed**.

## QR and shortlink layers are bridges, not hidden rule sources

A QR code or short URL MAY help a voter reach the right place quickly.
It MUST NOT become a hidden authority layer that silently replaces the underlying current page, notice, office/help route, or superseding recovery path.

The controlling artifact remains the current official destination that the jurisdiction actually stands behind.
The handoff layer should only do enough to:
- move the voter from a constrained carrier into the current official destination,
- make the destination class legible,
- preserve a fallback a human can read or type,
- and remain recoverable if the printed/poster/video/social carrier survives longer than the first destination mapping.

## Printed QR, digital QR, and short URL are different classes

The archive should not flatten all scannable or short-link handoffs into one generic link bucket.

At least five materially different classes matter here:

1. **Printed QR with visible fallback text** — a poster, postcard, flyer, ballot packet insert, or sign that contains a QR code plus a readable fallback URL or office/help route.
2. **Short URL / vanity path** — a memorable URL spoken aloud, printed in mail, read on radio, shown on video, or copied from a social post.
3. **Digital QR image** — a QR code shown inside a PDF, slide, video, or page where accessibility rules for digital content still apply.
4. **Superseded or stale handoff state** — an old code, vanity path, or screenshot that still circulates after the destination changed.
5. **Resolver / analytics layer** — the infrastructure that maps the QR or short URL to a destination and can quietly introduce tracking, external-domain drift, or wrong-page routing.

Those classes overlap, but they are not the same problem.
A printed sign with a QR code has carrier fragility and accessibility issues that a typed vanity URL does not.
And a memorable short path can still fail if its resolver points at the wrong election, the wrong county, or a stale PDF. (xref: `digital_gov_introduction_to_qr_codes_page`; xref: `section508_accessible_qr_code_implementation_page`; xref: `digital_gov_requirements_registration_use_gov_domains_page`)

## Do not make QR the only path

Section508.gov's current QR guidance is especially useful because it says QR users need an equivalent alternative and that agencies should include a text alternative or nearby URL, including in print. (xref: `section508_accessible_qr_code_implementation_page`)

For election information, that supports a strict floor:
- do not make a QR code the only public path to action-changing information,
- do not require scanning when a typed or spoken URL, office/help route, or printed instruction can also be provided,
- and do not assume every voter has the device, dexterity, vision, connectivity, or familiarity needed to scan successfully.

A printed voter-facing artifact that is effectively **QR-only** is not just inconvenient.
It is a public-answer accessibility and resilience failure.

## Trusted-domain and recognizable-path discipline

Digital.gov's current `.gov` guidance says official government information, communications, publications, services, and digital products should use `.gov` or `.mil`, and that good government domain names should be memorable, concise, and clearly describe the service.  
Vote.gov reinforces the same trust posture with the current `.gov` and HTTPS marker. (xref: `digital_gov_requirements_registration_use_gov_domains_page`; xref: `vote_gov_home_page`)

That makes a strong default rule available:
- keep public QR and shortlink handoffs inside official, recognizable government domains where possible,
- prefer concise, human-checkable official paths over opaque third-party resolvers,
- and avoid sending voters through a domain posture that is harder to verify than the destination it is supposedly helping them reach.

Sometimes a short or memorable path is exactly the right tool.
But the resolver should strengthen official recognition, not weaken it.

## Destination legibility beats opaque convenience

USWDS link guidance says to use meaningful link text and link directly to the most relevant page.  
Section508's QR guidance says descriptive labels should explain what scanning will do. (xref: `uswds_link_component_page`; xref: `section508_accessible_qr_code_implementation_page`)

So a public handoff token should make the destination class legible:
- where the voter is going,
- whether the path is current and official,
- and whether the token lands on a page, office/help route, or clearly signposted next-step screen.

Avoid using a QR/shortlink handoff as an excuse for opaque copy like “scan here” or “go now” with no destination context.
A voter should not have to guess whether the code opens the county polling-place tool, the statewide FAQ, a PDF, a help desk, or a complaint path.

## Avoid hidden auto-actions and forced downloads

Section508.gov's current QR guidance says QR codes that automatically send a text or initiate a download can be intrusive and that codes should prefer a page with a clear call to action so users decide when and whether to proceed. (xref: `section508_accessible_qr_code_implementation_page`)

For this archive, that implies a narrow but important rule:
- prefer a current web destination with a clear next step,
- avoid encoding a forced app install, forced file download, auto-SMS, or other surprise action as the primary handoff,
- and keep the user's choice point visible before any higher-risk action occurs.

A QR code that jumps straight into a download or other hidden action can quietly become both an accessibility problem and a trust problem.

## Short links and QR codes are not excuses for covert tracking

A QR or shortlink resolver can quietly become a tracking surface.
That does not mean the archive should forbid every bounded aggregate metric.
It does mean the public voter-help layer should default to minimization.

So the handoff layer should avoid:
- per-voter or per-household tracking tokens in ordinary public-help QR codes,
- unique destination URLs that quietly encode a specific recipient when a shared public path would do,
- retention of raw scan logs longer than the published policy requires,
- and resolver designs that make the code materially less trustworthy merely to collect campaign-style analytics.

Prefer **shared public tokens, bounded aggregate metrics, and clearly documented resolver policy** over individualized scan trails.

## Staleness and printed-artifact persistence

Printed posters, mailers, signs, screenshots, slides, and replayed videos frequently outlive the first destination they point to.
That is exactly why this surface belongs next to `379`.

A good QR/shortlink program should assume that:
- old flyers will remain on bulletin boards,
- old screenshots will keep circulating,
- old videos will keep being replayed,
- and a memorable short URL may still be typed weeks later.

So stale handoffs need explicit recovery:
- preserve the short path or code mapping when possible,
- redirect to the current official destination when that can be done safely,
- use a help-rich tombstone or replacement page when direct redirection would mislead,
- and never let a stale print artifact silently resolve to a wrong-election or wrong-jurisdiction page. (xref: `digital_gov_introduction_to_qr_codes_page`; xref: `uswds_link_component_page`; xref: `eac_effective_design_for_the_administration_of_federal_elections_page`)

## Accessibility-in-context discipline

Section508.gov's current QR guidance says agencies should test QR implementations across devices and assistive technologies, provide descriptive labels/alt text, and include alternatives in digital and print contexts. (xref: `section508_accessible_qr_code_implementation_page`)

That means this surface should be judged in real context:
- whether the QR image has an accessible name or nearby description,
- whether the fallback URL is readable and usable,
- whether contrast and print size support successful scanning,
- whether the code can be used on the devices the public is likely to have,
- and whether a user who cannot or does not scan still gets the same actionable path.

## Minimal handoff-state taxonomy

A small taxonomy is enough:

1. **current_shared_qr_with_visible_fallback**
2. **current_short_or_vanity_url_to_current_official_destination**
3. **digital_qr_with_accessible_equivalent**
4. **stale_handoff_recovered_by_redirect_or_tombstone**
5. **tracking_minimized_shared_public_handoff**

That is usually better than a style-guide catalog of every creative QR placement.

## Bounded handoff-trace minimum

The archive does **not** need indefinite per-scan telemetry.
But it should be possible to reconstruct what a public handoff token was supposed to do.

At minimum, the bounded trace should make it possible to reconstruct:
- which handoff-surface policy version was in force,
- which carrier class was used,
- what visible fallback text or memorable path was published,
- which resolver mapping or destination ref controlled,
- whether the destination was current, superseded, redirected, or tombstoned,
- and when that state was in force.

Prefer **policy versions, carrier classes, visible fallback values, mapping versions, destination refs, supersession states, and timestamps** over raw scan-by-scan behavioral logs.

## Minimal claim-set

A jurisdiction can publish a compact, verifiable claim-set:

1. **Official handoff-surface claim:** the office identified one or more QR/shortlink handoff surfaces as official for scope `E`.
2. **Fallback claim:** public QR handoffs keep a readable fallback URL or office/help route recoverable.
3. **Trusted-domain claim:** handoff tokens use a recognizable official domain posture where possible.
4. **Destination-legibility claim:** the token or its nearby label makes the destination class intelligible.
5. **User-control claim:** the handoff does not rely on surprise auto-actions as the primary public path.
6. **Accessibility-equivalence claim:** users who cannot scan can still reach the same actionable destination.
7. **Stale-recovery claim:** old codes or short paths recover into current official state rather than generic or wrong-jurisdiction drift.
8. **Trace-minimization claim:** bounded public-answer reconstruction is possible without individualized scan surveillance.

## Canonical digest artifacts

Publish **digests of handoff policy and mapping state**, not raw scan histories.

- **Handoff Surface Digest (HSD):** digest of the bounded public QR/shortlink payload for a scope.
- **Handoff Resolution Policy Digest (HRPD):** digest of resolver, fallback, and stale-recovery policy.
- **Handoff Snapshot Digest (HSD-Snap):** optional digest proving what bounded handoff state a specific public artifact or path represented at time `T`.

## What belongs in the public handoff payload

Keep the payload **small, current-state-aware, and bridge-oriented**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `handoff_surface_label`
- `handoff_modalities[]`
- `covered_surface_refs[]`
- `official_source_anchors[]`
- `trusted_domain_policy_note`
- `qr_text_fallback_policy_note`
- `short_url_policy_note`
- `auto_action_boundary_note`
- `stale_recovery_policy_note`
- `analytics_minimization_note`
- `result_state_classes[]`
- `handoff_trace_policy`
- `routing_fallback_uri`
- `routing_fallback_phone`
- `rights_escalation_uri`
- `latest_notice_uri`
- `last_verified_at`
- supersedes / superseded-by pointers

Do **not** publish by default:
- raw per-scan logs,
- individualized recipient tokens for ordinary public-help distribution,
- opaque third-party tracking identifiers that are not needed for public recovery,
- or direct-secret deep links that bypass the current official help page without explanation.

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:
- Was this QR code or short URL an official public handoff token?
- Could a voter who did not scan still recover the same destination?
- Did the token resolve inside a recognizable official domain posture?
- Did the token land on the most relevant current official destination, or on a confusing intermediate hop?
- Did the code surprise the user with an auto-download or other hidden action?
- Was the printed/poster/social artifact stale, and if so, was the recovery explicit?
- Could the public handoff state be reconstructed without individualized scan telemetry?

## How this fits the family map

A QR code, short URL, or vanity path is **not** a new canonical voter-question family bucket.
It is a bridge into the same underlying voter questions already modeled in `292–343`.

So the underlying question remains:
- where to vote,
- which office is authoritative,
- which deadline controls,
- whether a file or tool is current,
- or where the voter should escalate when ordinary help fails.

This document only says that, if a jurisdiction relies on QR codes or short URLs to carry action-changing voter information, that bridge should stay official-looking, accessible, fallback-rich, recovery-capable, and later-reconstructible instead of functioning as a silent source of opaque redirects, forced actions, or covert tracking drift.

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/official-voter-information-qr-shortlink-surface-payload.json`
- Operator quickcheck: `artifacts/checklists/official-voter-information-qr-shortlink-surface-checklist.md`

## Sources (pinned IDs / lockfile IDs)

- Digital.gov: Introduction to QR codes (xref: `digital_gov_introduction_to_qr_codes_page`)
- Section508.gov: Accessible QR Code Implementation (xref: `section508_accessible_qr_code_implementation_page`)
- Digital.gov: Requirements for the registration and use of `.gov` domains in the federal government (xref: `digital_gov_requirements_registration_use_gov_domains_page`)
- Vote.gov: home / official secure-site marker (xref: `vote_gov_home_page`)
- USWDS: Link component (xref: `uswds_link_component_page`)
- EAC: Effective Design for the Administration of Federal Elections (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`)
