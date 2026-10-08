# 396 — Official voter-information publication dates, last-updated cues, and byline discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **official voter-information page freshness signals as they appear to the public before and after click-through**:
user-visible publication/update labels,
search-result byline-date cues,
structured date fields that help search systems infer publication or significant-update time,
time/timezone precision,
the boundary between a page's freshness date and the election event date described on the page,
and historical-page handling so archived materials do not look newly operative.

It does **not** replace the underlying voter-question families in `292–343`.
It does **not** replace:
- `308`, which governs substantive election calendars and key-date answers,
- `365`, which governs official FAQ/help pages whose visible answers still control,
- `369`, which governs video/livestream context and replay-date recovery,
- `382`, which governs title-link/snippet/canonical search-result presentation,
- `389`, which governs calendar objects and reminder semantics,
- `391`, which governs crawlability and indexability,
- `393`, which governs structured-data eligibility for breadcrumb/FAQ features,
- `394`, which governs stale-result removal and durable deindexing,
- or `395`, which governs snippet/preview excerpt ceilings.

It adds one narrow rule:
**if an election office wants current official voter-information pages to look current for the right reason—and historical or superseded pages to stop looking current for the wrong reason—it should treat publication/update dates and byline-date cues as one bounded public-answer control rather than as incidental CMS chrome.**

## Why this is a distinct surface

Current official guidance is enough to justify a bounded control here.

EAC's current **Effective Design for the Administration of Federal Elections** says online voter-information materials are part of the election office's communication responsibility and should be clear, understandable, accessible, usable, and accurate.
Google Search Central's current **Influence your byline dates in Google Search** guidance says Google may expose a byline date in search results when it can estimate when a page was published or significantly updated, that Google does not rely on a single date factor, and that site owners can help by giving the page a prominent visible date plus structured data.
Google's current date guidance also says dates and times should be consistent between visible and structured values, should use the correct timezone when specified, should not be future dates, and should describe the publication or update date of the page rather than the date of the action described on the page.
Google's current event structured-data guidance separately treats event dates as their own machine-readable object.
That is enough to treat freshness/date cues as a distinct public-answer surface rather than an implementation detail of the CMS theme. (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`; xref: `google_search_central_publication_dates_page`; xref: `google_search_best_date_page`; xref: `google_search_event_structured_data_page`)

This matters because election pages often carry at least **three different dates** at once:
- the page publication/update date,
- the date of the election or deadline described on the page,
- and the date of an older notice, PDF, or embedded artifact still visible nearby.

If those dates are ambiguous, contradictory, or unlabeled, the public can misread page freshness, and search systems may surface a result-date cue that looks authoritative even when it is describing the wrong thing.
That is not the same problem as `308`, which is about the substantive calendar answer.
This document is about **how the page signals its own freshness and how that signal interacts with search-result byline dates**.

## Page freshness is not the same thing as the election date

Google's current byline-date guidance says the page dates should describe the publication or update date of the page, **not the stories or events described on the page**, and says event markup can separately describe the activities listed on the page. (xref: `google_search_central_publication_dates_page`; xref: `google_search_event_structured_data_page`)

That creates a clean election-site boundary:
- **page freshness date** = when this page was published or significantly updated,
- **election/event date** = the date of registration cutoff, early voting, Election Day, canvass, cure deadline, office hours window, or other civic event the page describes.

Those dates can be related.
They are not interchangeable.
A page about an April 2 registration deadline may be correctly updated on March 28.
A result that shows only one date can mislead unless the page itself is explicit about which date is which.

## Visible labeled dates are part of the public answer, not decorative metadata

Google's current guidance says site owners should add a **user-visible date to the page**, feature it prominently, and label it appropriately such as “Published” or “Last updated.” (xref: `google_search_central_publication_dates_page`)

For official voter-information pages, that means freshness dates should not be left to:
- an unlabeled footer timestamp,
- a template-generated “posted” string with no context,
- or an undifferentiated cluster of dates near a headline.

The public needs to tell, quickly:
- whether the page itself was updated recently,
- whether a visible deadline belongs to the election content rather than the page revision,
- and whether a historical notice is being preserved as archive material rather than as today's controlling answer.

So a bounded policy should require **prominent, labeled freshness cues** on volatile official pages.

## Search byline dates are inferred, not manually guaranteed

Google's current guidance says Google does not depend on a single date factor and instead looks at several factors to estimate when a page was published or significantly updated.
It also says following the guidance can help Google find and process the information, but it does **not** guarantee that a byline date will be shown in search results. (xref: `google_search_central_publication_dates_page`)

Election offices should therefore avoid two opposite mistakes:
- pretending the search-result date is fully under manual control,
- or pretending date cues do not matter because display is not guaranteed.

The safer bounded rule is:
- make the page's freshness signal unambiguous,
- keep visible and machine-readable signals consistent,
- and preserve a trustworthy page/help lane even when search chooses not to show a byline date.

## Consistency beats cleverness

Google's current guidance says visible and structured dates should match, and recommends including time and timezone in markup for added precision even though time is not required. (xref: `google_search_central_publication_dates_page`; xref: `google_search_best_date_page`)

For election materials, that means the office should prefer **one coherent freshness signal** over multiple partially conflicting ones.
For example:
- the visible “Last updated” stamp,
- the structured `dateModified`,
- the page header,
- and any machine-readable page metadata
should all point at the same freshness story.

A page with a visible “Updated Nov. 1” label but structured data suggesting October 28 is a smaller implementation bug in ordinary content settings.
For action-changing voter information close to a deadline, it becomes a public-answer integrity problem.

## Time and timezone precision matter near election cutoffs

Google's current date guidance recommends providing time and timezone in markup for added precision and says timezones should be correct, including daylight-saving time where appropriate. (xref: `google_search_central_publication_dates_page`; xref: `google_search_best_date_page`)

That does **not** mean every election page needs a visible timestamp to the minute.
But it does mean maintainers should treat timezone precision as part of the bounded policy for pages where a same-day change matters:
- extended office hours,
- emergency polling-place moves,
- late weather/disaster notices,
- cure windows,
- and end-of-day return deadlines.

The page can keep the visible label simple while the machine-readable layer carries a more precise timestamp.
The key is that the signals should describe the **page update**, not silently drift into describing the event itself.

## Historical and superseded pages need explicit freshness posture

Google's current guidance says not to specify future dates and not to use the date of the action described on the page as the page date.
It also says that if incorrect dates are being selected, maintainers should consider minimizing other dates on the page. (xref: `google_search_central_publication_dates_page`)

That is especially important for archived election pages.
A historical page often contains:
- the old election date,
- the page's original publication date,
- later archive or migration timestamps,
- and maybe an embedded PDF or video with still more dates.

Without explicit archive posture, a superseded page can look newly current because a template/footer changed, a migration happened, or a media embed refreshed.
So a bounded policy should distinguish:
- **current operational page**,
- **current evergreen help page**,
- **historical archive page**,
- and **superseded page that should route to a current notice/help lane**.

## “Last updated” should reflect meaningful page change, not cosmetic churn

Google's byline-date guidance focuses on when a page was published or **significantly updated**. (xref: `google_search_central_publication_dates_page`)

For election offices, that supports a bounded anti-drift rule:
cosmetic template edits, analytics-tag changes, or generic footer changes should not be allowed to create a misleading fresh-looking operational page.

The archive does not need a universal legal definition of “significant.”
It only needs a bounded operational discipline:
if the visible freshness cue changes, it should correspond to a material update that the public would reasonably treat as a refreshed answer.

## Event markup and page freshness markup should not compete

Google's current guidance explicitly separates page publication/update dates from event dates, and Google's event structured-data guidance separately models event start/end information. (xref: `google_search_central_publication_dates_page`; xref: `google_search_event_structured_data_page`)

So this surface should require maintainers to check whether a page that advertises election events, deadlines, public meetings, or office-hour windows is keeping two machine-readable stories distinct:
- **when the page changed**, and
- **when the event happens**.

That boundary matters for pages like:
- “Election Day voting hours,”
- “Early voting this weekend,”
- “Ballot curing ends Friday,”
- or “Public test scheduled for Tuesday.”

The event date may be the voter-action date.
The freshness date is the page-trust date.
Both are useful, but conflating them produces bad first-contact cues.

## Minimal state taxonomy

A small taxonomy is enough:

1. **current_operational_page_with_prominent_last_updated_label**
2. **current_evergreen_help_page_with_stable_update_policy**
3. **event_page_with_page_freshness_and_event_date_separated**
4. **volatile_notice_page_with_precise_machine_readable_update_time**
5. **historical_archive_page_with_explicit_archive_posture**
6. **superseded_page_routed_to_current_notice_or_help_lane**
7. **date_signal_conflict_under_review_not_safe_to_treat_as_freshness_hint**

## Bounded freshness/byline trace minimum

The archive does **not** need Search Console screenshots, click logs, or per-query dating experiments.
But it should be possible to reconstruct the bounded policy that governed how official voter-information pages signaled freshness.

At minimum, the bounded trace should make it possible to reconstruct:
- which page classes were in scope,
- whether the page carried a visible publication date, a visible last-updated label, or both,
- whether structured date fields were used,
- whether event dates were kept separate from page freshness dates,
- whether historical pages carried archive posture,
- which current help/notice lane remained controlling if the page was superseded,
- and when that policy state was last verified.

Prefer **policy versions, page classes, date-signal classes, bounded verification notes, and timestamps** over webmaster exports or personalized telemetry.

## Minimal claim-set

A jurisdiction can publish a compact, verifiable claim-set:

1. **Visible-date claim:** the office uses labeled visible freshness dates on page classes where page currentness materially affects voter action.
2. **Consistency claim:** visible and machine-readable date signals are intended to tell the same freshness story.
3. **Page-versus-event claim:** page freshness dates are kept distinct from election/event dates described on the page.
4. **Timezone claim:** pages with same-day or near-cutoff volatility preserve correct timezone-aware machine-readable freshness where precision matters.
5. **Historical-page claim:** archive and superseded pages do not rely on accidental template dates to imply current operational status.
6. **Meaningful-update claim:** visible freshness changes are reserved for material answer changes rather than cosmetic churn.
7. **Fallback claim:** a current official notice/help lane remains visible and actionable when a superseded page is still reachable.

## Canonical digest artifacts

Publish **digests of freshness/byline policy**, not private console evidence.

- **Date Cue Surface Digest (DCSD):** digest of the bounded freshness/byline policy payload for a scope.
- **Freshness Signal Class Digest (FSCD):** optional digest proving the date-signal class assignment for page classes.
- **Archive Posture Digest (APD):** optional digest proving how historical/superseded pages are labeled and routed.
- **Event-vs-Page Date Boundary Digest (EPDBD):** optional digest proving that event dates and page freshness dates were reviewed as distinct signals.

## What belongs in the public date-cue payload

Keep the payload **small, state-aware, and page-class oriented**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id`
- human `date_cue_surface_label`
- `delivery_role_note`
- `covered_surface_refs`
- `official_source_anchors`
- `page_classes`
- `default_date_signal_state_class`
- `visible_date_policy_note`
- `structured_date_policy_note`
- `page_vs_event_date_boundary_note`
- `timezone_precision_note`
- `historical_archive_posture_note`
- `meaningful_update_policy_note`
- `feature_state_classes`
- `feature_trace_policy`
- `routing_fallback_uri`
- `routing_fallback_phone`
- `latest_notice_uri`
- `last_verified_at`
- optional `supersedes` / `superseded_by`

## Evidence to preserve

Preserve only what is needed to reconstruct policy:
- the freshness/date-cue policy version,
- affected page classes,
- whether visible publication or update labels were intended,
- whether structured date fields were in use,
- whether event dates were reviewed separately,
- whether archive posture changed,
- and when the policy was last checked.

Do **not** preserve private webmaster exports, individualized search telemetry, or operator screenshots when bounded public-policy reconstruction is sufficient.

## Relationship to the rest of the stack

Use this document when the problem is:
- whether the page looks current for the right reason,
- whether a visible update label is needed,
- whether page freshness and event dates are being conflated,
- whether a historical page still looks operationally current,
- or whether structured date cues need tighter discipline near deadline-sensitive changes.

Use nearby controls when the problem is instead:
- the substantive date/deadline answer itself (`308`),
- calendar/reminder objects that leave the page (`389`),
- general search-result legibility and canonical routing (`382`),
- crawlability/indexability (`391`),
- snippet/excerpt ceilings (`395`),
- or stale-result removal from search entirely (`394`).

That boundary keeps `396` compact.
It is not “freshness in general.”
It is the bounded publication/update/date-cue layer for official voter-information pages.
