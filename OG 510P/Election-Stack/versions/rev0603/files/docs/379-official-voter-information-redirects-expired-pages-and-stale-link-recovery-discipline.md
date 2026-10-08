# 379 — Official voter-information redirects, expired pages, and stale-link recovery discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **official voter-information URLs that move, expire, or stop resolving cleanly**:
redirects,
retired election pages,
expired microsites,
moved FAQ/help entries,
old PDF/file URLs,
legacy bookmarks,
and not-found recovery pages that still have to get a voter to the right current official destination.

It does **not** replace the underlying voter-question families in `292–343`.
It does **not** replace:
- `305`, which governs the authoritative office/help route,
- `308`, which governs election-calendar and key-date surfaces,
- `365`, which governs official FAQ/help article editioning,
- `366`, which governs short-form alerts that may carry old links,
- `368`, which governs printable/downloadable artifacts that may outlive their original page,
- `372`, which governs site signage and on-site wayfinding,
- `374`, which governs interactive routers and state selectors,
- `375`, which governs site-search discovery,
- or `378`, which governs file-download and embedded-viewer handoff behavior.

It adds one narrow rule:
**if an election office expects the public to arrive through old bookmarks, shared links, QR/shortlink bridges, PDF/file URLs, search-engine results, or stale campaign links, the link-recovery layer should resolve that arrival into an explicit current-state recovery path instead of a silent dead end, a misleading generic homepage redirect, or a wrong-election page that merely looks official.**

## Why this is a distinct surface

Current official guidance is enough to justify a bounded control here.

EAC's current **Effective Design for the Administration of Federal Elections** says online voter-information materials should be clear, understandable, accessible, and accurate.
Vote.gov's current front door still routes people into state-specific official registration and voting flows instead of pretending that one national page can safely hold every local answer.
NASS's current `#TrustedInfo2026` posture still says voters should be driven directly to election officials' websites, social-media pages, and materials for credible, timely election information.
At the government-web layer, USWDS's current **404 page** template says a not-found page should explain the error and tell users what to do next.
Digital.gov's current **An introduction to decommissioning sites** says agencies should implement redirects so bookmarks and search engines do not strand users in 404s.
Digital.gov's current **Optimize your content** page for SearchGov says removed pages should return `404 Not Found` or `301 Moved Permanently`.
Digital.gov's current **Optimizing search during website redesigns** page says to use `301` redirects when a resource moved so searchers do not hit error pages.
And Digital.gov's current **Reduce, remove, remediate: PDFs and government websites** says old PDF URLs can be redirected to the right current place when people follow stale file links. (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`; xref: `vote_gov_home_page`; xref: `nass_trustedinfo_2026_page`; xref: `uswds_404_page_template_page`; xref: `digital_gov_decommissioning_sites_page`; xref: `digital_gov_searchgov_optimize_content_page`; xref: `digital_gov_optimizing_search_during_website_redesigns_page`; xref: `digital_gov_reduce_remove_remediate_pdfs_page`)

That means a stale-link path is not generic CMS housekeeping.
It is often the **recovery boundary** that decides whether a voter who followed last week's flyer, last month's bookmark, or last cycle's PDF reaches the current official answer, an explicit expired-page explanation, or an opaque failure state.

## Link recovery is a recovery layer, not a hidden rule source

A redirect, expired-page tombstone, or 404/help page MAY help a voter recover from a stale URL.
It MUST NOT quietly become a hidden authority layer that overwrites scope, collapses election cycles together, or routes every stale arrival to a generic homepage as if the public question had been safely resolved.

The controlling artifact remains the current official page, notice, office/help route, or current editioned file that the jurisdiction actually stands behind.
The link-recovery layer should only do enough to make the next safe step visible:
- recover a moved current page,
- explain that an older election page expired,
- point to the current official destination or help route,
- and avoid pretending that “somewhere on the site” is close enough.

## Redirects, tombstones, and true misses are different states

The archive should not flatten every stale URL into one generic behavior.

There are at least four materially different states:

1. **Current canonical state** — the URL is still current and resolves directly to the controlling official page or wrapper.
2. **Moved current state** — the resource moved, and a scoped redirect or equivalent recovery path takes the voter to the new current official destination.
3. **Expired / superseded state** — the old page or file belongs to a past election, prior edition, or retired path; the voter gets an explicit tombstone or superseding notice that names the current official route.
4. **True missing / unavailable recovery state** — the resource does not exist or cannot be served right now, so the voter receives a plain-language not-found or temporary-unavailable recovery page with the current official help path.

The official web sources above imply that these states should not be conflated.
A moved page should not behave like a vanished one.
A removed page should not masquerade as if it still exists.
And a temporary failure should not be treated as a permanent disappearance. (xref: `uswds_404_page_template_page`; xref: `digital_gov_searchgov_optimize_content_page`; xref: `digital_gov_optimizing_search_during_website_redesigns_page`; xref: `digital_gov_decommissioning_sites_page`)

## Homepage redirects are usually the wrong recovery class

For election information, a blanket redirect from a stale deep link to the site homepage is often a failure disguised as polish.

That is an inference from the official posture above:
if a moved resource should use `301`, a removed resource should be `404`, and a 404 page should explain what happened and what the user can do next, then silently collapsing a specific stale election URL into a generic homepage usually destroys exactly the state the voter needed to recover.
The voter loses scope, election cycle, office path, and sometimes the fact that the older page expired at all. (xref: `uswds_404_page_template_page`; xref: `digital_gov_searchgov_optimize_content_page`; xref: `digital_gov_optimizing_search_during_website_redesigns_page`)

So when the old target no longer safely maps one-to-one onto the new target, prefer an explicit recovery page or tombstone over a generic home redirect.

## Expired-election pages need explicit cycle boundaries

Election pages age out in ways ordinary government content does not.
A polling-place page from the primary may no longer control for the general.
A registration page for one cycle may no longer match the current deadline window.
A PDF handout for one election may still circulate long after its page moved.

So the link-recovery layer should make expired-cycle state visible:
- identify that the older page belonged to a past election, window, or edition,
- route to the current election page, current FAQ/help entry, or authoritative office/help path,
- and avoid silently swapping in a different election's answer without telling the user that the original link expired.

A voter should not have to reverse-engineer whether they reached a moved current page or a different page for a different election.

## File URLs and detached links still need recovery discipline

A stale file URL is still a public-answer entrypoint.
People reach those links from:
- bookmarked PDFs,
- emailed attachments,
- old newsletters,
- saved browser tabs,
- shared chats,
- QR codes on printed pieces,
- or search results that indexed a file rather than its wrapper page.

Digital.gov's current PDF-remediation guidance is enough to justify a bounded rule here:
when a file URL is retired, the old path can redirect to the right current place rather than leaving voters stranded on a dead link. (xref: `digital_gov_reduce_remove_remediate_pdfs_page`)

That does **not** mean every old file should quietly map to the newest file object.
It means the public should reach a current official wrapper, current file, or explicit superseding notice that explains what now controls.

## 404/help pages should recover the user, not just report failure

USWDS's current 404 template is useful here because it frames the error page as a recovery surface, not a dead-end label.
It says a 404 page should explain the error, identify likely fixes, give actions/links, provide support channels if available, and keep the error code visible. (xref: `uswds_404_page_template_page`)

For election information, that suggests a bounded recovery shape:
- say plainly that the requested page or file could not be found,
- keep a current official search/help path visible,
- keep the authoritative office/help contact visible when practical,
- and offer likely next actions that preserve election scope rather than just saying “try again later.”

A polished 404 page that lacks the current official help route is still a poor election-information recovery surface.

## Search and stale-link recovery should agree

Search and stale-link handling are adjacent control layers.
A jurisdiction should not let site search recover one path while direct stale links recover a different path with a different effective answer.

That means the link-recovery lane should stay aligned with:
- `305` for official office/help routing,
- `308` for current key-date/calendar routing,
- `365` for current FAQ/help article editions,
- `374` for current selector/router destinations,
- `375` for site-search result recovery,
- and `378` for file-wrapper / file URL recovery.

If an old URL says one thing, site search says another, and the current FAQ page says a third, the archive should model that as a real public-answer failure rather than mere web maintenance drift.

## Minimal result-state taxonomy

A small state taxonomy is enough for bounded accountability:

1. **current_canonical** — requested URL still resolves to the current official destination.
2. **moved_with_scoped_redirect** — requested URL recovered to a new current official destination that preserves the same practical question/scope.
3. **expired_with_tombstone_or_superseding_notice** — requested URL belonged to an older election/page/file and now resolves through explicit expired-state context.
4. **not_found_or_unavailable_with_help_recovery** — requested URL cannot safely resolve to current content, so the user receives a bounded not-found / unavailable recovery surface.

That taxonomy is usually more useful than a large catalog of infrastructure-specific HTTP edge cases.

## Bounded link-recovery trace minimum

The archive does **not** need indefinite raw clickstream retention for every stale election URL.
But it should be possible to reconstruct what recovery policy the public encountered for action-changing stale links.

At minimum, the bounded trace should make it possible to reconstruct:
- which link-recovery policy version was in force,
- which requested path or path class was involved,
- what result-state class the user encountered,
- whether the path used a redirect, expired-page tombstone, or help-rich 404/unavailable page,
- what target/help route the recovery surface offered,
- whether the recovery crossed election scope or stayed within the same practical question,
- and when that state was in force.

Prefer **policy versions, path patterns/classes, status families, recovery-state classes, target/help-route refs, and timestamps** over indefinite per-user referral logs, individual click histories, or tracking parameters that are not needed for public-answer accountability.

## Privacy and minimization floor

Stale-link recovery can quietly become a surveillance surface because every bookmark, QR scan, and old share creates a trace.
That does not mean the archive should default to retaining raw user click histories.

So the link-recovery layer should default to minimization:
- do not retain detailed per-user stale-link logs longer than the published policy requires,
- do not bind ordinary public stale-link recovery to voter records absent a separately disclosed authority,
- do not use recovery telemetry as a hidden profiling surface for sensitive voter-help topics,
- and keep the current official help path visible so record-specific or rights-sensitive matters move to the proper channel.

## Minimal claim-set

A jurisdiction can publish a compact, verifiable claim-set:

1. **Official link-recovery-surface claim:** the office identified one or more public redirect / expired-page / 404 recovery surfaces as official for scope `E`.
2. **State-separation claim:** moved, expired, and missing/unavailable states are handled as distinct bounded recovery classes rather than one generic redirect behavior.
3. **Scope-preservation claim:** a recovery path does not silently collapse one election's stale page into a different election's answer without explicit context.
4. **Help-route claim:** not-found or unavailable recovery pages keep a current official search/help or office-contact path visible.
5. **File-URL recovery claim:** stale downloadable-file URLs recover through a current official wrapper, file, or superseding notice instead of a dead end.
6. **Trace-minimization claim:** action-changing recovery states are reconstructible through bounded policy/version/state evidence without indefinite raw clickstream retention.
7. **Superseding claim:** material recovery-path changes produce an explicit updated state instead of invisible drift.

## Canonical digest artifacts

Publish **digests of recovery policy and state**, not full user-level click logs.

- **Link Recovery Surface Digest (LRSD):** digest of the bounded redirect / expired-page / 404 recovery payload for a scope.
- **Recovery State Policy Digest (RSPD):** digest of the current state-separation and scope-preservation policy.
- **Expired Page Notice Digest (EPND):** optional digest proving that a prior election page/file was explicitly tombstoned or superseded instead of silently disappearing.
- **Recovery Snapshot Digest (RSD-Link):** optional digest proving what bounded recovery state a documented stale entrypoint produced at time `T`.

## What belongs in the public link-recovery payload

Keep the payload **small, recovery-oriented, and current-state aware**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `link_recovery_surface_label`
- `entrypoint_patterns[]`
- `covered_surface_refs[]`
- `official_source_anchors[]`
- `canonical_destination_policy`
- `redirect_behavior_note`
- `expired_page_tombstone_policy_note`
- `missing_resource_recovery_policy_note`
- `cross_scope_redirect_policy_note`
- `file_url_recovery_policy_note`
- `result_state_classes[]`
- `link_recovery_trace_policy`
- `routing_fallback_uri`
- `routing_fallback_phone`
- `rights_escalation_uri`
- `latest_notice_uri`
- `last_verified_at`
- supersedes / superseded-by pointers

Do **not** publish by default:
- raw per-user click logs,
- full referrer histories,
- detailed campaign-tracking exports,
- internal server-config secrets,
- or exhaustive URL inventories that are not needed for bounded public-answer recovery.

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:
- Which official redirect / expired-page / 404 recovery surface was in force at time `T`?
- Did a moved resource recover to the correct current official destination?
- Did an expired election page say that it had expired and show what now controlled?
- Were stale file URLs routed to a current file/wrapper/help path instead of a dead end?
- Did the recovery surface preserve election scope instead of silently collapsing into a generic homepage or a different election's page?
- Could a third party reconstruct the bounded recovery state without needing invasive user-level telemetry?

## How this fits the family map

A redirect, expired-page tombstone, or 404 recovery surface is **not** a new canonical voter-question family bucket.
It is a delivery/recovery layer in front of the same underlying voter questions already modeled in `292–343`.

So the underlying question remains:
- where to vote,
- which office is authoritative,
- which date or deadline controls,
- how to request or return a ballot,
- which special-case path applies,
- or where rights/safety escalation begins.

This document only says that, if a jurisdiction relies on redirects, expired-page notices, or 404 recovery pages to catch stale public links, that recovery layer should stay scoped, explicit, help-rich, and later-reconstructible instead of functioning as a silent source of wrong-election drift.

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/official-voter-information-link-recovery-surface-payload.json`
- Operator quickcheck: `artifacts/checklists/official-voter-information-link-recovery-surface-checklist.md`

## Sources (pinned IDs / lockfile IDs)

- EAC: Effective Design for the Administration of Federal Elections (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`)
- Vote.gov: home / state-routing front door (xref: `vote_gov_home_page`)
- NASS: `#TrustedInfo2026` (xref: `nass_trustedinfo_2026_page`)
- USWDS: 404 page template (xref: `uswds_404_page_template_page`)
- Digital.gov: An introduction to decommissioning sites (xref: `digital_gov_decommissioning_sites_page`)
- Digital.gov: Optimize your content / SearchGov (xref: `digital_gov_searchgov_optimize_content_page`)
- Digital.gov: Optimizing search during website redesigns (xref: `digital_gov_optimizing_search_during_website_redesigns_page`)
- Digital.gov: Reduce, remove, remediate: PDFs and government websites (xref: `digital_gov_reduce_remove_remediate_pdfs_page`)
