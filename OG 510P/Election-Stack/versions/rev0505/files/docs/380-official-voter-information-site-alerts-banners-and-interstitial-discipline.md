# 380 — Official voter-information site alerts, banners, and interstitial discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **official voter-information site alerts, emergency/status bars, in-page alert blocks, homepage alert modules, and any modal/interstitial notice the public must pass through to reach action-changing voting information**.

It does **not** replace the underlying voter-question families in `292–343`.
It does **not** replace:
- `305`, which governs the authoritative office/help route,
- `308`, which governs election-calendar and key-date surfaces,
- `366`, which governs outbound broadcast alerts and social posts,
- `372`, which governs physical-site signage and wayfinding,
- `374`, which governs interactive routers,
- `375`, which governs site-search discovery,
- `379`, which governs stale-link recovery,
- or `378`, which governs file-download / viewer handoff.

It adds one narrow rule:
**if an election office expects voters to rely on an on-site alert bar, sitewide banner, in-page alert, or interstitial to catch action-changing voting information, that alert surface should be prominent but bounded, clearly dated/scoped, linked to the current official destination, tested for accessibility in context, and should avoid unnecessary interruptions that block task completion.**

## Why this is a distinct surface

Current official guidance is enough to justify a bounded control here.

EAC's current **Effective Design for the Administration of Federal Elections** says online voter-information materials should be clear, understandable, accessible, usable, and accurate.
USWDS's current **Site alert** component says a site alert prominently displays critical, time-sensitive warnings or directions across every page so users see it whenever they visit the site, and it recommends prominent placement near the top of the page while avoiding stacked site alerts.
USWDS's current **Alert** component says alerts keep users informed of important and sometimes time-sensitive changes.
USWDS's current **Alert accessibility tests** say agencies must test alerts in the context of their own site, and that headings, consistent identification, zoom behavior, and screen-reader announcements cannot be assumed from the component alone.
Digital.gov's current **IT warning banners** guidance—grounded in M-23-22—says agencies should avoid unnecessary pop-ups, modals, overlays, interstitials, and other interruptive messages that impede task completion.
And the current **Content timeliness indicator** draft standard at Federal website standards says announcements and alerts should include publication dates and, where applicable, effective and expiration dates. (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`; xref: `uswds_site_alert_component_page`; xref: `uswds_alert_component_page`; xref: `uswds_alert_accessibility_tests_page`; xref: `digital_gov_it_warning_banners_page`; xref: `federal_website_standards_content_timeliness_indicator_page`)

That means the on-site alert layer is not just decoration.
It is often the **prominence and interruption layer** that decides whether the public actually sees a changed deadline, moved polling place, outage workaround, rights/safety pointer, or emergency notice before acting on stale page content below it.

## Alerts are prominence layers, not hidden rule sources

A sitewide or page-scoped alert MAY make urgent information visible.
It MUST NOT become a hidden authority layer that replaces the current controlling page, office/help route, or current editioned notice without making the underlying destination recoverable.

The controlling artifact remains the current official page, notice, office/help route, or current surface that the jurisdiction actually stands behind.
The alert layer should only do enough to:
- make urgent state visible,
- say what changed,
- show where the voter should go next,
- and preserve the current official destination rather than trapping the user inside a generic banner or modal.

## Sitewide alert, page alert, and interstitial are different classes

The archive should not flatten every alert into one generic banner.

There are at least four materially different alert classes:

1. **Current sitewide alert** — urgent information relevant across large portions of the public site and expected to appear on every page.
2. **Current page-scoped alert** — an alert attached to a specific page, form, FAQ, or tool because the change is narrower in scope.
3. **Expiring / superseding alert state** — an alert that has a publication/effective/expiration window or that supersedes an earlier alert.
4. **Interruptive interstitial / modal state** — a stronger blocking pattern that should be used only when the interruption is necessary to the design of the experience and not merely to add friction or generic warnings.

The official sources above imply that these classes should not be conflated.
A sitewide urgent alert is not the same thing as a contextual note on a single page.
And an interruptive modal is not just a louder version of a banner. (xref: `uswds_site_alert_component_page`; xref: `uswds_alert_component_page`; xref: `digital_gov_it_warning_banners_page`)

## Avoid unnecessary interruption

Digital.gov's current warning-banner guidance gives a clean boundary:
avoid unnecessary pop-ups, modals, overlays, interstitials, and other interruptive messages that impede the user from completing a task. (xref: `digital_gov_it_warning_banners_page`)

For election information, that means a blocking interstitial should be comparatively rare.
Most urgent public messages can and should be carried by:
- a sitewide alert,
- an in-page alert with a current link,
- a prominent notice module,
- or a current help route.

Use stronger interruption only when the design truly requires it—such as forcing acknowledgement of a materially changed path before a voter continues through a high-risk action flow—and not just because the message feels important.

## Prominence and stacking discipline

USWDS's current site-alert guidance says to place site alerts prominently near the top of the page and to avoid stacking multiple site alerts; when multiple urgent messages exist, use links inside a single site alert instead of piling banners on banners. (xref: `uswds_site_alert_component_page`)

That matters because stacked or inconsistent alert treatments can blur priority rather than clarify it.
So the archive should treat prominence itself as a bounded design variable:
- urgent sitewide changes get one clear sitewide treatment,
- narrower issues stay page-scoped,
- multiple items are grouped or linked rather than stacked into visual noise,
- and the current official destination remains obvious.

## Timeliness and expiration discipline

The current Federal website standards draft on timeliness indicators is especially useful here because it treats announcements and alerts as content that should carry publication dates and, where applicable, effective and expiration dates. (xref: `federal_website_standards_content_timeliness_indicator_page`)

For election information, that supports a straightforward rule:
- alert surfaces should make timing visible,
- alerts that no longer control should expire or clear,
- superseding alerts should not leave prior banners silently active,
- and users should not be forced to guess whether a visible banner still controls this election, this day, or this page.

A stale alert that remains prominent after it expired is a public-answer failure, not just a cosmetic issue.

## Accessibility and implementation-in-context discipline

USWDS's current alert accessibility tests say implementers must test alerts in the context of their own site.
The component alone does not guarantee the right heading quality, consistent meaning across pages, zoom/reflow behavior, or screen-reader announcements. (xref: `uswds_alert_accessibility_tests_page`)

That means a voter-information alert surface should be judged in real context:
- whether the heading is clear,
- whether the same alert treatment means the same thing across pages,
- whether the alert remains usable at zoom,
- whether assistive technology announces it correctly,
- and whether the alert's link text actually tells the voter where the current official path now lives.

## Minimal alert-state taxonomy

A small state taxonomy is enough:

1. **current_sitewide_alert**
2. **current_page_scoped_alert**
3. **expiring_or_superseding_alert**
4. **interruptive_alert_used_only_when_necessary**
5. **cleared_or_archived_alert_state**

That taxonomy is usually more useful than a long style-guide catalog of banner variants.

## Bounded alert-trace minimum

The archive does **not** need indefinite user-level dismissal logs for every banner.
But it should be possible to reconstruct what alert state the public encountered for action-changing notices.

At minimum, the bounded trace should make it possible to reconstruct:
- which alert-surface policy version was in force,
- which alert class the public saw,
- where the alert was placed,
- what publication/effective/expiration state it carried,
- which current official destination or help route it pointed to,
- whether the alert was sitewide or page-scoped,
- and when that state was in force.

Prefer **policy versions, alert-state classes, timing fields, placement class, target refs, and timestamps** over indefinite per-user dismissal telemetry, behavior logs, or modal-interruption traces.

## Privacy and minimization floor

Alert surfaces can quietly become analytics surfaces when every dismissal, close action, or interstitial pass-through is treated as behavioral data.
That does not mean the archive should default to retaining raw interaction trails.

So the alert layer should default to minimization:
- do not retain detailed per-user alert interaction logs longer than the published policy requires,
- do not use dismissal telemetry as a shadow profiling surface for sensitive voter-help topics,
- do not require extra tracking merely to let users continue to the current official destination,
- and keep the current official help path visible so record-specific or rights-sensitive matters move to the right channel.

## Minimal claim-set

A jurisdiction can publish a compact, verifiable claim-set:

1. **Official alert-surface claim:** the office identified one or more sitewide/page-scoped/interstitial alert surfaces as official for scope `E`.
2. **Prominence claim:** urgent sitewide information uses a consistent prominent treatment, and narrower messages stay page-scoped.
3. **Interruption-boundary claim:** blocking modals/interstitials are used only when necessary to the design of the experience.
4. **Timeliness claim:** alerts carry publication/effective/expiration state when relevant and are cleared or superseded when they stop controlling.
5. **Accessibility-in-context claim:** the alert treatment has been tested in the implementing site for clarity, consistency, zoom, and assistive-technology behavior.
6. **Destination-recovery claim:** the alert keeps the current official destination or help route recoverable.
7. **Trace-minimization claim:** action-changing alert states are reconstructible through bounded policy/state evidence without indefinite user-level interaction retention.

## Canonical digest artifacts

Publish **digests of alert policy and state**, not full user-level interaction telemetry.

- **Alert Surface Digest (ASD):** digest of the bounded public alert-surface payload for a scope.
- **Alert State Policy Digest (ASPD):** digest of the current alert classification, timing, and interruption policy.
- **Alert Snapshot Digest (ASD-Snap):** optional digest proving what bounded alert state a documented page or route carried at time `T`.

## What belongs in the public alert payload

Keep the payload **small, current-state-aware, and prominence-oriented**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `alert_surface_label`
- `alert_modalities[]`
- `covered_surface_refs[]`
- `official_source_anchors[]`
- `placement_policy_note`
- `interruption_policy_note`
- `timeliness_indicator_policy_note`
- `stacking_policy_note`
- `alert_destination_policy_note`
- `result_state_classes[]`
- `alert_trace_policy`
- `routing_fallback_uri`
- `routing_fallback_phone`
- `rights_escalation_uri`
- `latest_notice_uri`
- `last_verified_at`
- supersedes / superseded-by pointers

Do **not** publish by default:
- raw per-user alert close events,
- modal dwell-time logs,
- invasive interaction analytics,
- or draft alert copy that is not needed for bounded public-answer reconstruction.

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:
- Which official alert surface was in force at time `T`?
- Was the alert sitewide, page-scoped, interruptive, or already superseded?
- Did the alert carry enough timing information to tell whether it still controlled?
- Did the alert link to the correct current official destination or help route?
- Were multiple messages stacked in a way that obscured priority?
- Was a modal/interstitial really necessary, or was it just friction?
- Could a third party reconstruct the bounded alert state without invasive user-level telemetry?

## How this fits the family map

A site alert, status bar, or interstitial is **not** a new canonical voter-question family bucket.
It is a prominence/interruption layer in front of the same underlying voter questions already modeled in `292–343`.

So the underlying question remains:
- where to vote,
- which office is authoritative,
- which date or deadline controls,
- which route is currently open,
- whether a file or tool is safe to use,
- or where the voter should escalate when ordinary help fails.

This document only says that, if a jurisdiction relies on site alerts or interstitials to carry action-changing voting information, that alert layer should stay prominent but bounded, clearly timed, destination-linked, accessible in context, and later-reconstructible instead of functioning as a silent source of friction or stale-notice drift.

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/official-voter-information-site-alert-surface-payload.json`
- Operator quickcheck: `artifacts/checklists/official-voter-information-site-alert-surface-checklist.md`

## Sources (pinned IDs / lockfile IDs)

- EAC: Effective Design for the Administration of Federal Elections (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`)
- USWDS: Site alert component (xref: `uswds_site_alert_component_page`)
- USWDS: Alert component (xref: `uswds_alert_component_page`)
- USWDS: Alert accessibility tests (xref: `uswds_alert_accessibility_tests_page`)
- Digital.gov: IT warning banners / reduce user friction by limiting warnings (xref: `digital_gov_it_warning_banners_page`)
- Federal website standards: Content timeliness indicator (xref: `federal_website_standards_content_timeliness_indicator_page`)
