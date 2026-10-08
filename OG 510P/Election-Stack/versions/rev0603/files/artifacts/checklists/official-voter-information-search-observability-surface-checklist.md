# Official voter-information search observability checklist

Use this quickcheck when an election office needs a bounded way to notice whether current voter-information pages have become harder to find in Google Search.

## Monitoring scope

- Monitor a small set of critical voter-task query/page clusters rather than a generic SEO keyword list.
- Include the exact official pages that should answer those tasks.
- Include translated-language query/page clusters when the jurisdiction serves them as equivalent official paths.
- Keep the office/help route in scope so there is always a monitored recovery lane.

## Comparison and slicing

- Start with the main Performance chart, then compare against a prior period and a longer seasonal window.
- Slice the change by query, page, country, device, and search appearance before deciding what kind of failure happened.
- Do not rely only on property totals if the concern is a specific current page or voter task.
- Remember that chart totals and table totals can differ when aggregation changes.

## Preliminary data and anomalies

- Check whether the newest data is still preliminary before over-reading a same-day movement.
- If using API pulls, check incomplete-date or incomplete-hour metadata when recent data is included.
- Remember the API's incomplete-data metadata uses the America/Los_Angeles timezone.
- Check the Search Console data-anomalies page before treating a dip or bump as a real public incident.

## Interpreting the drop

- Separate a broad property drop from a narrow page/query loss.
- Separate a real discoverability loss from a search-appearance mix shift.
- If only CTR drops, review title/snippet/search-appearance issues before assuming the page disappeared.
- If a specific page or page class is implicated, move to the page-diagnosis lane.

## AI-feature measurement

- Treat AI Overviews and AI Mode traffic as part of the ordinary Web search measurement surface.
- Do not create a separate mystery dashboard just because the user may have seen AI features.
- Use page/query/search-appearance slices to understand the change inside the Web search view.

## Evidence posture

- Preserve only monitored cluster labels, comparison-window class, slice categories checked, preliminary-data state, anomaly-check state, concentration class, and last review time.
- Do not preserve full Search Console exports, raw query exhaust, large dashboards, or user-identifying logs when bounded policy reconstruction is sufficient.
