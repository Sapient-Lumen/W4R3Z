# 465 — Official voter-information browser-history entry mutation, push/replace semantics, and back-stack truthfulness discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **official voter-information routes that mutate browser-history entries while the voter stays in the same document**:
single-page application answer routes,
search/filter/result interfaces that synthesize navigation steps,
overlays or drawers that change the current route meaning,
status or details views that switch records without a full page load,
multi-step public flows that rewrite URLs or history state in place,
and similar official routes where the page can be current on-screen yet still fail the public because the browser Back/Forward stack no longer tells the truth about what answer-state each history entry represents.

It does **not** replace the underlying voter-question families in `292–343`.
It does **not** replace:
- `438`, which governs whether the current official URL is safe to bookmark, copy, forward, or later revisit as a kept link,
- `439`, which governs whether an already-open route stays fresh and recoverable when the user returns through Back/Forward, hidden-tab/app switching, session restore, or duplicate tabs,
- `441`, which governs page-title and browser-tab/history-entry naming legibility,
- `442`, which governs same-page fragments and in-page section-target continuity,
- `445`, which governs tab-panel visibility and active-panel continuity,
- `452`, which governs filters/facets and active-scope/subset reset discipline,
- `453`, which governs combobox suggestion commitment,
- `458`, which governs cross-view continuity when list/map/calendar or similar view switchers change the visible answer lane,
- or `459`, which governs answer overlays/dialogs/drawers and close-return continuity,
- or `477`, which governs post-submit redirects and browser repost-prompt truthfulness when a state-changing submit already happened and the next browser-visible page must be safely refreshable without replay ambiguity.

It adds one narrow rule:
**if an official voter-information route uses `pushState()`, `replaceState()`, hash routing, or other same-document history mutation to represent public answer-state changes, the browser history stack should remain truthful enough that Back/Forward, copied current-location cues, and entry-by-entry return behavior correspond to meaningful official states rather than synthetic traps, silent erasure, or contradictory shell transitions.**

## Why this is a distinct surface

The EAC’s current **Effective Design for the Administration of Federal Elections** treats online voter-information materials as core election communications whose organization and clarity affect whether the public can understand and use election information correctly. USWDS’s current **Keep a record** guidance says important public-service flows should preserve a record that includes the URL, date, and next-step/reference context when possible. Digital.gov’s current plain-language guidance on **Links** says links are part of navigation and should help readers find the information they need without confusion. MDN’s current **Working with the History API** guide says single-page applications often update page content without a full page load and use `pushState()` and `replaceState()` to keep browser session history aligned with changing state. MDN’s current `popstate` documentation says history entries created or changed through `pushState()` and `replaceState()` are used to reconstruct dynamically generated pages and that Back/Forward traversal activates those entries. MDN’s current `pageshow` documentation also makes clear that pages can be restored via Back/Forward history, frozen-page restore, or background-tab opening in ways that do not behave like a fresh page load. (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`; xref: `uswds_keep_a_record_page`; xref: `digital_gov_plain_language_links_page`; xref: `mdn_working_with_history_api_page`; xref: `mdn_popstate_event_page`; xref: `mdn_pageshow_event_page`)

That is enough to justify a compact control here.
A route may pass `438`, `439`, `441`, `452`, `458`, and `459` yet still fail the public because:
- an official answer visibly changes, but the app never creates a meaningful history entry for the new state,
- tiny cosmetic UI motions generate many synthetic entries so Back becomes a trap instead of a recovery path,
- `replaceState()` silently erases the last meaningful answer state that a voter expected to recover,
- a drawer, filter, or result swap changes the controlling answer, but Back appears to move through fake intermediate states unrelated to the visible official meaning,
- the browser history entry label/title suggests one answer while the restored same-document state reconstructs another,
- or an SPA shell rewrites route state so aggressively that the voter can no longer tell whether Back/Forward will recover a prior official answer, leave the route entirely, or reopen a stale wrapper whose controlling content has already changed.

## This is not the same thing as share-safe URLs, return freshness, or title legibility

`438` asks whether the current URL itself is safe to keep, copy, share, or later revisit.

`439` asks what happens when an already-open page instance reappears through browser history traversal, hidden return, restore, or duplicate-tab reuse.

`441` asks whether titles and browser-tab/history labels stay specific enough to distinguish current official routes.

`465` asks a different question:
**when the route mutates session-history entries inside the same document, do those entry boundaries truthfully correspond to meaningful public answer states and produce honest Back/Forward behavior?**

A route may pass the earlier controls and still fail `465` if:
- the URL is safe to copy but the current entry stack no longer maps to meaningful answer steps,
- the route revalidates freshness on return but Back still walks through synthetic or contradictory same-document states,
- titles update correctly yet the wrong history entry was added or erased,
- or a visible result/filter/view switch looks like a new official page state while the app quietly chooses a different history mutation model every time.

## History-entry classes matter

This archive should not flatten all same-document history mutations into one bucket. At least five distinct classes matter here:

1. **Meaningful answer-state push** — the route creates a new session-history entry because the controlling public answer, selected official item, or user-recognizable step actually changed.
2. **In-place correction or normalization** — the route updates the current entry to canonicalize parameters, repair an invalid route, or normalize a location without pretending the voter visited a distinct answer state.
3. **Presentation-only mutation** — the route changes sort order, focus target, expansion state, or minor local presentation without enough substantive meaning to deserve a standalone Back-stack step.
4. **Overlay or subview history entry** — the route uses history mutation so closing an overlay, drawer, or details pane can correspond to Back/Forward traversal instead of only an internal close button.
5. **Synthetic redirect/repair entry** — the route inserts or rewrites entries to recover from stale, invalid, or missing state while trying not to strand the user in a dead-end shell.

Those classes are not interchangeable.
`465` exists so the office can say which class a mutation belongs to and why the chosen `push`/`replace`/no-entry behavior tells the truth about what the voter just experienced.

## The browser Back button should not become a public-answer lie detector by accident

MDN’s current History API guidance says the core problem solved by `pushState()`, `replaceState()`, and `popstate` is keeping the browser’s Back/Forward behavior aligned with same-document content changes that otherwise would not create new page loads. (xref: `mdn_working_with_history_api_page`; xref: `mdn_popstate_event_page`)

For this archive, that means an official route should review whether pressing Back after a same-document answer change will:
- recover the prior meaningful answer state,
- leave the route entirely in a way the user would reasonably expect,
- close a details pane or overlay if that pane meaningfully functioned as a route layer,
- or warn/recover safely if the prior state can no longer be reconstructed.

What fails `465` is not “the app uses SPA routing.”
What fails `465` is letting browser-history behavior silently contradict the public meaning of the route.

## `pushState()` and `replaceState()` should encode semantic honesty, not implementation convenience

MDN’s current guide distinguishes `pushState()` adding a new session-history entry from `replaceState()` updating the current one. That is exactly the boundary this archive needs. (xref: `mdn_working_with_history_api_page`)

For `465`, a route should review whether:
- it uses **push** when the voter would reasonably understand the change as a distinct new official answer, record, or step worth returning to,
- it uses **replace** when the route is only correcting, canonicalizing, or tightening the current state rather than creating a new user-meaningful visit,
- and it avoids mixing the two haphazardly such that identical user actions sometimes create recoverable history and sometimes silently erase it.

The archive does **not** require every UI state to become a deep-linkable journey.
It does require that the chosen history-mutation posture tell the truth about whether the user just entered a meaningfully different official answer state.

## Cosmetic churn should not spam the history stack

A public route can look modern and still become unusable if every tiny motion creates a synthetic browser-history entry.
For this archive, the following are warning signs:
- hover/focus/transient state changes that create Back-stack noise,
- rapid filter chips or sort toggles that bury the last meaningful answer state under a pile of reversible presentation tweaks,
- pagination or continuation patterns that create multiple contradictory history steps for one apparent result-set move,
- or animated route transitions that look like one answer change but actually emit several browser-history mutations before the voter can even read the page.

A voter should not need to hit Back eight times just to leave a detail route that looked like one official answer page.

## History mutation should not silently erase the last safe recovery point

`replaceState()` is often exactly right for canonicalization, but it can also erase the user’s last meaningful recovery point if used carelessly.
For this archive, that means official routes should review whether they are replacing:
- the last visible answer state before a consequential lookup result,
- the last safe step before a warning, access boundary, or unsupported branch,
- or the last trustworthy pre-overlay/pre-filter/pre-detail context the voter would expect Back to recover.

A route fails `465` when it uses replace-style mutation so aggressively that the user loses the last intelligible official state without warning and without an equivalent bounded recovery cue.

## Overlay, details-pane, and subview routing need explicit history posture

Some official routes use modal/drawer/details states that are big enough to function like distinct route layers.
That is partly `459`, but `465` asks the narrower session-history question:
if the route lets the overlay or subview behave like a separate public-answer step, does Back close or retreat it truthfully, or does browser history do something unrelated?

Examples that matter here:
- a polling-place details drawer that the user expects Back to close,
- a results view that swaps between county cards or calendar items in-place,
- a search/details pane that changes the controlling official item without leaving the shell,
- or a route that opens a warning/help interstitial using same-document navigation rather than a full new page.

The archive does not force one behavior.
It forces the office to pick a behavior whose Back-stack semantics are understandable and reviewable.

## History-entry truthfulness includes state naming, not just state restoration

MDN’s current `popstate` guidance notes that session-history entries are used to reconstruct dynamic page state, while `441` already governs title/history-entry disambiguation. (xref: `mdn_popstate_event_page`)

So `465` is not only “can the app restore something?”
It is also:
- whether each history step corresponds to a state the voter could describe,
- whether the route avoids collapsing several distinct answer states into one generic shell entry,
- and whether the app avoids manufacturing history steps whose labels and visible meaning diverge.

A truthful history stack should let a reviewer say, in bounded prose, what each step represented.

## Repaired, invalid, or stale route state needs bounded entry policy

Some public routes receive broken parameters, stale item IDs, or obsolete subview state.
When the route repairs that state in-place, `465` asks:
- did the office preserve or replace the current history entry,
- can the user back out to the last meaningful route without falling into an invalid-loop trap,
- and if repair was unavoidable, does the current route say enough for the voter to understand what happened?

This is where `465` connects to `379`, `404`, `438`, and `439` without collapsing into them.
The question here is not merely “did the route recover?” but “did the history-entry mutation model remain truthful while recovery happened?”

## Preserve bounded browser-history review evidence, not raw clickstream exhaust

The evidence posture here is about reconstructing whether the office reviewed browser-history entry truthfulness on important same-document official routes.
The archive should preserve:
- which routes mutate session-history entries,
- which mutation classes were reviewed,
- which user actions create `push`, `replace`, or no-entry behavior,
- what the expected Back/Forward outcome is for each reviewed class,
- where the last safe recovery point sits,
- whether overlays/subviews/details panes participate in history,
- whether invalid/stale-state repair preserves or rewrites history,
- and when the review last occurred.

It should **not** require preserving:
- named-user browser-history dumps,
- raw analytics clickstreams,
- session-replay archives,
- per-user navigation event exhaust,
- or giant client logs when bounded policy reconstruction is sufficient.

## Canonical digest artifacts

Publish **small digests of browser-history posture**, not event-stream exhaust.

- **Browser History Surface Digest (BHSD):** digest of the bounded session-history mutation posture for the official route.
- **Back-Stack Truthfulness Review Digest (BTRD):** optional digest describing which same-document actions create meaningful history steps and why.
- **History Repair Boundary Digest (HRBD):** optional digest describing when canonicalization, invalid-state repair, or overlay/subview transitions use replace/push/no-entry behavior.

## What belongs in the public browser-history payload

Keep the payload **small, route-aware, and entry-semantics focused**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `browser_history_surface_label`
- `delivery_role_note`
- `covered_surface_refs[]`
- `official_source_anchors[]`
- `reviewed_history_mutations[]`
- `history_entry_class_policy_note`
- `push_vs_replace_policy_note`
- `back_stack_truthfulness_note`
- `presentation_only_state_boundary_note`
- `overlay_or_subview_history_note`
- `history_repair_and_canonicalization_note`
- `recovery_point_policy_note`
- `title_alignment_note`
- `last_verified_at`
- supersedes / superseded-by pointers

Do **not** publish by default:
- raw browser-history dumps,
- named-user navigation traces,
- session-replay exports,
- full analytics event catalogs,
- speculative frontend router internals that are not needed for the bounded public record,
- or high-volume instrumentation that exists only to debug one browser build.

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:
- Did the office review which same-document route changes create meaningful session-history entries and which merely update the current entry?
- Does pressing Back/Forward on important official routes correspond to understandable public answer states rather than synthetic traps or silent erasure?
- When the route repairs invalid/stale state or uses overlays/subviews, is the browser-history behavior bounded, truthful, and recoverable?

## Minimal artifacts for this control

- Template payload: `artifacts/templates/official-voter-information-browser-history-surface-payload.json`
- Operator checklist: `artifacts/checklists/official-voter-information-browser-history-surface-checklist.md`
