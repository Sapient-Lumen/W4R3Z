# 439 — Official voter-information history restore, hidden return, and parallel-tab state freshness discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **official voter-information routes that may remain open while a voter presses Back/Forward, backgrounds the tab or app, restores a suspended session, duplicates a tab, or returns later from browser/session history**:
status lookups,
registration or ballot-help flows,
polling-place or hours answers,
submission and cure dashboards,
appointment or case-status routes,
and similar official pages where the answer may be current when first displayed but quietly become stale, contradictory, or unrecoverable when the user returns to the already-open route instead of starting over.

It does **not** replace the underlying voter-question families in `292–343`.
It does **not** replace:
- `404`, which governs first-load cache freshness and stale-content recovery,
- `409`, which governs sign-in boundaries and session-expiry recovery,
- `429`, which governs multi-step state preservation through staged workflows,
- `431`, which governs inactivity timeouts and advance-warning/lossless-expiry recovery,
- `438`, which governs whether the current URL can be safely bookmarked, copied, forwarded, or later revisited as a kept link,
- `437`, which governs whether a kept record remains faithful once it leaves the live page,
- `465`, which governs whether same-document `pushState()`/`replaceState()` behavior keeps the browser history stack truthful while the route is already open,
- or `476`, which governs leave-page warnings and unsaved-changes truthfulness at the moment the voter tries to leave/reload rather than what happens when the page later reappears.

It adds one narrow rule:
**if an official voter-information route may remain open across Back/Forward navigation, hidden-tab/app return, frozen-session restore, or parallel-tab reuse, the route should either revalidate and visibly recover the controlling answer state or clearly warn that the visible answer may no longer be current.**

## Why this is a distinct surface

The EAC’s current **Effective Design for the Administration of Federal Elections** treats online voter-information materials as core election communications. Digital.gov’s current digital-first public-experience requirements say public digital services should be accessible, authoritative, secure by design/default, and user-centered. USWDS’s current **Keep a record** guidance says successful public-service flows should help people preserve the information they need later. W3C WAI’s current multi-page forms guidance says users need orientation and continuity across staged routes. MDN’s current documentation on `pageshow`, `popstate`, `visibilitychange`, the Page Visibility API, `beforeunload`, browser-history state, and not-restored reasons makes clear that modern routes can reappear from browser history, background/foreground transitions, or back/forward cache without behaving like a full fresh load. (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`; xref: `digital_gov_requirements_digital_first_public_experience_page`; xref: `uswds_keep_a_record_page`; xref: `w3c_wai_multi_page_forms_page`; xref: `mdn_working_with_history_api_page`; xref: `mdn_pageshow_event_page`; xref: `mdn_popstate_event_page`; xref: `mdn_visibilitychange_event_page`; xref: `mdn_page_visibility_api_page`; xref: `mdn_beforeunload_event_page`; xref: `mdn_not_restored_reason_details_reason_page`)

That is enough to justify a compact control here.
A route may pass `404`, `431`, and `438` yet still fail the public because:
- a polling-place answer remains visible after the user returns from another app even though the route should have revalidated freshness,
- Back/Forward restores an earlier step or result shell whose visible answer no longer matches the current official state,
- duplicating a tab produces two conflicting copies of the same case or status page,
- a hidden tab resumes with expired or superseded answer content and no visible warning,
- the route depends on `beforeunload` folklore for safety even though that signal is unreliable and may block better restore behavior,
- or the page restores from bfcache/session history without checking whether the controlling answer, deadline, or eligibility posture changed while it was hidden.

## This is not the same thing as cache freshness, timeout recovery, or share-safe URLs

`404` asks whether a route loads fresh enough instead of serving stale cached content on arrival.

`431` asks whether a time-limited route discloses inactivity limits and preserves work or recovery when the session expires.

`438` asks whether the URL itself can be safely kept, copied, or later revisited.

`439` asks a different question:
**once the page is already open, what happens when the voter returns through browser history, tab restore, app switching, or a duplicated/parallel tab?**

A route may pass the earlier controls and still fail `439` if:
- the initial load was fresh but a restored page never re-checks current state,
- the URL is safely shareable yet an existing hidden tab shows obsolete answer content,
- the route handles session expiry but not conflicting parallel-tab edits or state drift,
- or the visible page resumes from history without telling the user whether the answer was revalidated.

## Return-state classes matter

This archive should not flatten all returns into one bucket. At least five distinct classes matter here:

1. **Back/Forward history return** — the user navigates through session history and expects the route to restore a meaningful prior state.
2. **Hidden-tab or app-switch return** — the route remains open while focus leaves and later returns.
3. **Frozen/session-restore or bfcache return** — the browser revives an existing page instance rather than doing a full network reload.
4. **Parallel-tab or duplicate-tab divergence** — two open copies of the same route may drift or overwrite each other.
5. **Not-restored fallback** — the browser cannot restore the prior page instance and instead performs a different navigation path.

Those are different operational states.
An official route may behave correctly on one class and fail another.
The evidence posture should preserve which classes were reviewed and what recovery or warning posture controlled each.

## Hidden return should not silently preserve stale official answers

MDN’s current `pageshow` and visibility guidance makes clear that a page can reappear after having been hidden or restored without behaving like a newly loaded document. (xref: `mdn_pageshow_event_page`; xref: `mdn_visibilitychange_event_page`; xref: `mdn_page_visibility_api_page`)

For this archive, if the controlling answer can change with time, authentication posture, jurisdictional state, or backend review results, then returning to an already-open page should not silently preserve a maybe-current answer forever.
If the page restores meaningful progress yet the governing public basis has materially changed, `470` governs the expected-head / re-review boundary rather than `439` silently implying that fresh-enough rendering also means unchanged authority.
A route should review whether it:
- revalidates current answer state when the page becomes visible again,
- marks the answer as still current, stale, pending refresh, or needing re-entry,
- preserves enough route context that a refresh or re-check does not dump the voter into a generic home page,
- and distinguishes ordinary hidden-tab return from a truly new visit when that difference matters to safety.

The archive does **not** require constant polling or telemetry-heavy presence tracking.
It does require that the office not let hidden-return behavior turn an official answer into an accidental screenshot of the past.

## Browser-history recovery should preserve meaning, not just pixels

MDN’s current History API and `popstate` guidance makes clear that modern applications can update visible content without full navigation and can later move through those states via browser history. (xref: `mdn_working_with_history_api_page`; xref: `mdn_popstate_event_page`)

For `439`, that means Back/Forward should not merely repaint an old shell.
The route should review whether history return:
- restores a meaningful step/result state,
- keeps current-step and review context coherent,
- warns or refreshes when the underlying answer may have changed,
- and avoids leaving the voter in a contradictory state where the page chrome says one thing while the controlling answer now says another.

## Parallel tabs need bounded divergence rules

Official routes often end up open in more than one place: a helper duplicates a tab, a voter opens the same flow from a texted link, or a browser restores multiple previous tabs at once.
`439` treats that as a bounded integrity problem rather than a vague frontend annoyance.

For this archive, a route should decide whether parallel tabs are:
- harmless read-only mirrors,
- allowed but revalidated on focus/return,
- warning-worthy when edits or submissions in one tab affect the other,
- or intentionally unsupported with an explicit recover-safe restart path.

What fails `439` is not “multiple tabs exist.”
What fails `439` is silent contradiction between open official answers with no visible recovery cue.

## Do not rely on fragile unload folklore for integrity

MDN’s current `beforeunload` documentation says the event has reliability and performance limitations and should be used sparingly. MDN’s not-restored-reason documentation makes clear that unload-related behavior can interact with page restore outcomes. (xref: `mdn_beforeunload_event_page`; xref: `mdn_not_restored_reason_details_reason_page`)

For this archive, that means official routes should not treat “we warned on close” or “we clean up on unload” as the primary integrity control for return-state correctness.
Where freshness, state revalidation, or divergence warnings matter, the safer posture is to review visible return/recovery behavior itself rather than assuming unload hooks will run exactly when needed.

## When the answer cannot stay current on return, say so clearly

Some official routes are inherently fragile across time.
A queue position, temporary review status, or authenticated case page may not remain current after backgrounding or restoration.
That is acceptable if the route says so clearly enough that the voter does not mistake preserved pixels for current truth.

Good bounded substitutes include:
- a visible “last checked” timestamp,
- a “refresh required to confirm current status” cue,
- a stable re-entry or re-authentication path,
- a reference number or kept record that remains useful even if the live page must be revalidated,
- or the authoritative help lane when the route can no longer safely assert current state.

## Preserve bounded evidence, not session-replay exhaust

The evidence posture here is about reconstructing whether return-state behavior was reviewed and bounded.
The archive should preserve:
- which routes were tested for Back/Forward, hidden-return, restore, and parallel-tab behavior,
- whether the route revalidated, warned, or restarted on each return-state class,
- what freshness or “last checked” cue controlled,
- whether parallel-tab divergence was harmless, warned, or unsupported,
- what help or re-entry path applied when current state could not be trusted,
- and when the review last occurred.

It should **not** require preserving:
- full session-replay video,
- detailed tab-visibility telemetry tied to named voters,
- raw browser-history exports,
- per-user background/foreground analytics,
- or individualized restore traces when bounded policy reconstruction is sufficient.

## Canonical digest artifacts

Publish **small digests of return-state policy**, not raw interaction exhaust.

- **History-Restore Surface Digest (HRSD):** digest of the bounded return-state policy payload for the official route.
- **Parallel-Tab Divergence Policy Digest (PTDPD):** optional digest describing whether duplicate/open-parallel tabs are harmless, warned, or unsupported.
- **Freshness-on-Return Policy Digest (FRPD):** optional digest describing when a route revalidates, warns, or requires refresh/re-entry after hidden or restored return.

## What belongs in the public return-state payload

Keep the payload **small, route-aware, and return-state focused**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `history_restore_surface_label`
- `delivery_role_note`
- `covered_surface_refs[]`
- `official_source_anchors[]`
- `critical_return_routes[]`
- `return_state_classes[]`
- `return_freshness_policy_note`
- `history_navigation_alignment_note`
- `hidden_tab_restore_policy_note`
- `parallel_tab_divergence_policy_note`
- `last_checked_cue_note`
- `safe_reentry_or_help_note`
- `last_verified_at`
- supersedes / superseded-by pointers

Do **not** publish by default:
- user-level session-replay logs,
- named-user visibility telemetry,
- browser-history dumps,
- raw restore diagnostics tied to a real voter,
- or individualized multi-tab traces.

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:
- Did the office review what happens when an official route is revisited through Back/Forward, tab restore, app switching, or hidden-tab return?
- If the controlling answer might have changed, did the route revalidate or visibly warn instead of silently showing preserved stale content?
- Did browser-history return keep the step/result meaning coherent rather than merely repainting an obsolete shell?
- Did the office decide what duplicate or parallel tabs mean and expose a bounded divergence/recovery posture?
- When current state could not safely be trusted on return, did the route provide a bounded re-entry, reference, refresh, or help path?
- Did the archive preserve bounded policy evidence without collecting session-replay exhaust from real users?

## How this fits the family map

History restore, hidden return, and parallel-tab freshness is **not** a new underlying voter-question family bucket.
It is a delivery-layer control over official routes that already answer substantive voter questions elsewhere in the stack.

This document only says that, if an official answer remains open across browser-history movement, background/foreground transitions, restore events, or duplicated tabs, the route should not silently present uncertain state as current official truth.

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/official-voter-information-history-restore-surface-payload.json`
- Operator checklist: `artifacts/checklists/official-voter-information-history-restore-surface-checklist.md`
