# 389 — Official voter-information calendar subscriptions, `.ics` downloads, and reminder-handoff discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **calendar-style voter-information handoff surfaces that may continue to represent official election dates or service windows after a voter leaves the official page**: downloadable `.ics` files, published calendar URLs / subscription calendars, “add to calendar” links, search/event-card calendar-like representations, and similar reminder objects that can persist in a personal calendar app.

It does **not** replace the underlying voter-question families in `292–343`.
It does **not** replace:
- `308`, which governs the substantive authoritative election-calendar and key-date surface,
- `305`, which governs the authoritative office/help route,
- `366`, which governs outbound alerts, texts, and app notifications,
- `370`, which governs email reminders and newsletter editions,
- `378`, which governs non-HTML file/download and embedded-viewer boundary discipline,
- `379`, which governs stale-link and expired-page recovery after arrival,
- `382`, which governs general search-result presentation,
- or `388`, which governs preview cards and unfurls before click-through.

It adds one narrow rule:
**if a voter may carry official election timing information forward as a calendar object or reminder artifact, that artifact should stay clearly official, clear about date/time semantics, subordinate to the current controlling official page/notice/help lane, and easy to recover from when subscriptions lag, imported files persist, or old reminders survive into a new election cycle.**

## Why this is a distinct surface

Current official and primary platform guidance is enough to justify a bounded control here.

Current EAC voter-education guidance still treats **relevant dates** as a core public-information responsibility: election day, registration deadlines, and other action-changing dates are explicitly part of the content voters need. EAC’s broader voter and election-official posture still routes people back to the current state/local official source rather than to detached summary artifacts. That matters because many offices publish date-heavy information in forms that are tempting to export into reminders or calendars. (xref: `eac_voter_education_topics_editable_content_document_2024_pdf`; xref: `eac_voter_faqs_page`; xref: `vote_gov_home_page`)

Primary platform documentation shows that detached calendar objects are operationally real. Google Calendar’s current help says users can add a **public calendar from a URL** and that the added calendar then appears under “Other calendars.” Apple’s current Calendar documentation says users can subscribe from a link on the internet or from an email, that the events shown in a subscription calendar are **controlled by the provider**, and that subscribers can choose auto-refresh behavior and whether alerts are ignored. Apple’s current iCloud subscription guidance separately tells users to **trust the source** of the calendar before subscribing. (xref: `google_calendar_public_calendar_from_url_help_page`; xref: `apple_calendar_subscribe_to_calendars_mac_page`; xref: `apple_calendar_add_subscription_calendar_page`)

That is enough to treat calendar/reminder handoff as a distinct voter-information surface rather than as just one more copy of `308`.
The office may publish one authoritative date page.
But a voter may act on the imported calendar object instead.
So the archive needs a small control for how that detached object stays bounded.

## Calendar objects are persistent derivatives, not the controlling rule source

A subscribed calendar, imported `.ics` file, or machine-readable event card MAY help a voter remember a key date.
It MUST NOT become the controlling authority for jurisdiction-specific election rules.

The controlling artifact remains the current official page, signed notice, directory entry, or direct office confirmation that the jurisdiction itself stands behind.
So the calendar/reminder layer should do only enough to:
- identify the office or jurisdiction clearly,
- preserve the basic event/date semantics needed for reminders,
- point back to the current official destination that controls the answer,
- and recover safely when an imported or subscribed calendar object outlives the state that originally made it correct.

## Subscription calendars detach state from the page that created them

Apple’s current Mac Calendar guide says subscription calendars can be added from links on the internet or from email, that the provider controls the events shown in the subscribed calendar, and that subscribers can set auto-refresh cadence and ignore alerts. Google Calendar’s current help likewise says users can add a public calendar from a URL. (xref: `apple_calendar_subscribe_to_calendars_mac_page`; xref: `google_calendar_public_calendar_from_url_help_page`)

That means the office should assume at least some voters will encounter election timing information as:
- an ongoing subscription calendar they no longer remember subscribing to,
- a one-time imported `.ics` file that does not auto-refresh,
- a reminder generated from a search/event-style card,
- or a shared calendar link forwarded without the surrounding explanation.

So the bounded control here is not “publish a perfect calendar product.”
It is:
- keep the subscription/import object clearly official,
- keep date/time semantics legible enough that the object does not silently lie,
- keep rollover / supersession behavior explicit,
- and keep the current official page/help lane one click or one tap away.

## Timezone, all-day, and recurrence semantics are load-bearing

Google’s current event structured-data guidance says event start/end values should follow explicit date-and-time rules, including correct UTC offsets, and that all-day events should be represented as day-long dates rather than as fake midnight-to-23:59 placeholders. Google Calendar’s current events guide likewise distinguishes **timed** events from **all-day** events, says the timezone field has no significance for all-day events, and says recurring events require a single timezone in order to expand the recurrence. Google’s date guidance separately says visible and machine-readable dates should stay consistent and use the correct timezone, including daylight-saving changes. (xref: `google_search_event_structured_data_page`; xref: `google_calendar_events_and_calendars_page`; xref: `google_search_best_date_page`)

For election information, that makes this surface operationally important rather than fussy metadata.
A reminder that is off by a timezone, represented as a pseudo-midnight timestamp, or carried forward under a stale recurrence rule can shift a voter’s real-world action even if the underlying official page was correct.

So a safe calendar/reminder surface should keep at least these distinctions explicit:
- **all-day civic dates** versus **timed service windows**,
- **local election-office time** versus generic UTC-looking timestamps,
- **single-instance reminders** versus **recurring subscriptions**,
- and **current-cycle entries** versus artifacts that need to expire or supersede when a new cycle begins.

## Non-HTML `.ics` and calendar links still need clear disclosure

USWDS’s current link guidance says teams should indicate file type and size for links to non-HTML content and should prefer HTML when possible. That guidance is not about election calendars specifically, but it points directly at the right bounded rule here: a voter should know whether a click opens the current official page, downloads a file, or subscribes them to a calendar-like object that may persist beyond today. (xref: `uswds_link_component_page`)

So if an office exposes calendar downloads or subscription links, it should prefer patterns like:
- a current official HTML page that explains the date,
- a clearly labeled optional `.ics` or subscription action,
- and a visible fallback into the authoritative current date/help page.

This archive does **not** need a giant compatibility matrix for every calendar client.
It only needs a bounded policy saying that subscription/download objects are persistence-prone non-HTML derivatives and should be labeled as such.

## Reminder convenience should not outrun current-state recovery

A date reminder is valuable only if the voter can still recover the current practical answer when conditions changed.
That matters especially for:
- registration/update deadlines,
- early-voting windows,
- office closure or holiday adjustments,
- special election / runoff rollovers,
- and service windows that are local-time specific rather than all-day statewide facts.

So a safe pattern is:
- put the authoritative explanation on a durable official page,
- let the reminder artifact carry only the minimum timing/help context,
- and make the linked landing page immediately expose current-state or superseding-notice cues.

The goal is not to squeeze every legal caveat into a calendar title.
The goal is to stop a detached reminder artifact from silently becoming the whole rulebook.

## Rollover and supersession discipline matter because old reminders survive

Subscription calendars can refresh, but imported files and manually added reminders often do not.
Apple’s current guidance shows that subscribers can choose refresh cadence for subscription calendars and can suppress alerts; that is useful for users, but it also means the office cannot assume identical refresh or notification behavior across clients. (xref: `apple_calendar_subscribe_to_calendars_mac_page`)

So the bounded rule here is:
- do not rely on subscriber refresh timing for correctness,
- do not leave cycle-specific election reminders looking evergreen when they are not,
- and do preserve a clear superseding route when the prior reminder object is no longer safe to trust.

This composes directly with `379`.
A stale calendar object is just another stale first-contact artifact.
The click-through page has to recover from it cleanly.

## Minimal calendar/reminder state taxonomy

A small taxonomy is enough:

1. **subscription_calendar_linked_to_current_official_page**
2. **downloadable_ics_with_clear_scope_and_timezone_semantics**
3. **all_day_date_safe_for_reminder_but_not_full_rule_source**
4. **timed_service_window_with_explicit_local_time_semantics**
5. **imported_or_stale_reminder_recovered_by_current_page_or_notice**
6. **high_risk_date_question_routed_to_help_lane_after_clickthrough**

That is usually more useful than pretending every calendar client needs its own theory chapter.

## Bounded trace minimum

The archive does **not** need subscriber lists, individualized reminder telemetry, invite acceptance logs, or per-user calendar analytics.
But for accountability and later reconstruction, it is still useful to preserve a bounded **calendar/reminder policy trace** for action-changing public date artifacts.

At minimum, a jurisdiction should be able to reconstruct:
- which official pages exposed calendar-download or subscription actions for volatile topics,
- which calendar feed / `.ics` policy version governed those actions,
- which timezone / all-day / recurrence conventions were intended,
- which superseding page or notice was supposed to recover stale reminders,
- and when the office last reviewed the calendar-facing artifacts for the current cycle.

That gives the archive enough to evaluate whether the calendar handoff layer was safely bounded without turning the archive into a reminder-surveillance sink.

## Proof obligations

If a jurisdiction claims to operate this surface responsibly, it should be able to prove at least:

1. **Authority-boundary claim:** calendar/reminder artifacts are treated as convenience handoffs, not as controlling rule sources.
2. **Official-identity claim:** calendar downloads/subscriptions clearly identify the responsible office or jurisdiction.
3. **Date-semantics claim:** all-day, timed, timezone, and recurrence semantics are explicit enough to avoid silent misinterpretation.
4. **Supersession claim:** stale imported/subscribed reminders can be corrected through a current official page, notice, or help route.
5. **Trace-minimization claim:** bounded reconstruction is possible without retaining individualized subscriber telemetry.

## Canonical digest artifacts

Publish **digests of calendar/reminder policy and destination state**, not subscriber data.

- **Calendar Reminder Surface Digest (CRSD):** digest of the bounded public payload for official calendar/reminder handoff readiness.
- **Calendar Feed Policy Digest (CFPD):** digest of the policy describing `.ics` / subscription / add-to-calendar semantics for a given surface class.
- **Calendar Rollover Recovery Digest (CRRD):** optional digest proving what superseding or current-state recovery cues a linked official page was supposed to expose at time `T`.

## What belongs in the public payload

Keep the payload **small, timing-aware, and authority-boundary explicit**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `calendar_reminder_surface_label`
- `covered_surface_refs[]`
- `official_source_anchors[]`
- `authority_boundary_note`
- `subscription_calendar_policy_note`
- `downloadable_ics_policy_note`
- `event_card_policy_note`
- `timezone_policy_note`
- `all_day_vs_timed_policy_note`
- `recurrence_rollover_policy_note`
- `calendar_link_disclosure_note`
- `current_state_recovery_policy_note`
- `calendar_state_classes[]`
- `calendar_trace_policy`
- `routing_fallback_uri`
- `routing_fallback_phone`
- `latest_notice_uri`
- `last_verified_at`
- supersedes / superseded-by pointers

Do **not** publish by default:
- subscriber email addresses,
- acceptance / RSVP state,
- individualized reminder-delivery logs,
- private analytics about who imported which file,
- or raw client-specific debug traces that do not help reconstruct the bounded public policy.

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:
- Which official pages or notices were intended to expose calendar-style reminder artifacts at time `T`?
- Did the download/subscription object make the responsible office and election scope recognizable?
- Were all-day versus timed and timezone semantics represented safely enough for the dates in question?
- Could a voter safely recover when an imported `.ics`, subscribed calendar, or old reminder outlived the current answer?
- Did the jurisdiction preserve a bounded calendar-policy trace without collecting unnecessary subscriber telemetry?

## How this fits the family map

Calendar subscriptions, `.ics` downloads, and reminder artifacts are **not** a new canonical voter-question family bucket.
They are a first-contact and persistent-memory delivery layer that may carry forward an existing voter-information surface after the voter leaves the official page.

So the underlying question remains:
- when a deadline really closes,
- whether a date is all-day or tied to office hours,
- where the current authoritative calendar page or notice lives,
- or where the voter should escalate when a reminder object and the current official page no longer agree.

This document only says that, if voters may carry official election timing information into subscription calendars, `.ics` files, or similar reminder objects, that derivative layer should stay clearly official, semantically legible, subordinate to the current official page/notice/help lane, and recovery-rich instead of quietly becoming the trusted answer.

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/official-voter-information-calendar-reminder-surface-payload.json`
- Operator quickcheck: `artifacts/checklists/official-voter-information-calendar-reminder-surface-checklist.md`

## Sources (pinned IDs / lockfile IDs)

- EAC: Voter Education Topics editable content document (xref: `eac_voter_education_topics_editable_content_document_2024_pdf`)
- EAC: Voter FAQs (xref: `eac_voter_faqs_page`)
- Vote.gov home / trust posture (xref: `vote_gov_home_page`)
- Google Search Central: Event structured data (xref: `google_search_event_structured_data_page`)
- Google Search Central Blog: best-date / timezone guidance (xref: `google_search_best_date_page`)
- Google Calendar Help: add public calendar from URL (xref: `google_calendar_public_calendar_from_url_help_page`)
- Apple Support: add subscription calendar (xref: `apple_calendar_add_subscription_calendar_page`)
- Apple Calendar User Guide: subscribe to calendars on Mac (xref: `apple_calendar_subscribe_to_calendars_mac_page`)
- USWDS: Link component guidance (xref: `uswds_link_component_page`)
