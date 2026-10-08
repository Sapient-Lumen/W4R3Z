# Official voter-information calendar/reminder surface checklist

Use this quickcheck when an office exposes election dates or service windows through `.ics` downloads, subscription-calendar URLs, add-to-calendar links, or similar reminder artifacts that can outlive the page that created them.

## Before publishing a calendar/reminder artifact

- Confirm the linked HTML page is still the right **current official destination** for the date or service window.
- Confirm the calendar/reminder artifact clearly identifies the responsible office or jurisdiction.
- Confirm the artifact is labeled as a calendar/download/subscription action, not disguised as ordinary page navigation.
- Confirm the election scope or cycle is visible enough that old reminders will not look evergreen by accident.
- Confirm the landing page still gives a quick route to the current help/contact path.

## Date/time semantics

- Check whether the artifact represents an **all-day civic date** or a **timed local service window**.
- Check that local-time semantics are explicit for timed entries.
- Avoid pseudo-midnight placeholders for all-day dates when the intent is “this date matters,” not “the office opens at 12:00 AM.”
- Check recurring entries carefully; do not let a recurrence rule quietly roll into a new election cycle without review.
- Re-check timezone and daylight-saving behavior for any timed public event or office-hour reminder.

## Recovery and rollover

- Assume some voters will import a one-time `.ics` file that never refreshes.
- Assume some subscribers may not refresh on the same cadence or may suppress alerts.
- Make sure the linked current page or notice can correct a stale imported/subscribed reminder without guesswork.
- Re-review calendar/reminder artifacts at election rollover, major schedule changes, and office-closure changes.
- Treat deadline reminders, office-hour windows, and special-election/runoff dates as stale-reminder risks.

## Link disclosure and minimization

- Disclose non-HTML calendar handoffs clearly.
- Prefer a durable official HTML explanation page with the calendar action as an optional convenience.
- Do not retain subscriber lists or individualized reminder telemetry just to prove the calendar policy existed.
- Preserve only the bounded trace needed to reconstruct file/feed policy, timing semantics, rollover posture, and fallback routing.
