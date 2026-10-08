# Official voter-information page-performance checklist

Use this quickcheck when an election office needs a bounded way to keep current voter-information pages usable on ordinary mobile conditions rather than merely online.

## Critical page scope

- Identify a small set of critical voter-task page classes rather than treating the whole site as one undifferentiated score.
- Keep the office/help recovery lane in the critical set.
- Include the mobile path a voter is most likely to use for those tasks.
- Re-check the critical set when a new election workflow or emergency fallback page is introduced.

## Budgets and review lanes

- Declare budgets or release thresholds for the critical page classes before shipping major changes.
- Keep field posture and release-preflight posture separate in the review notes.
- Check the mobile slice before deciding that the page is healthy enough.
- Treat map embeds, consent layers, analytics tags, translation widgets, and alert/banner additions as possible regression sources.

## Critical-content availability

- Confirm that the major answer text appears without depending on a fragile client-side waterfall.
- Confirm that the office/help fallback remains reachable when richer widgets degrade.
- Check that alert banners or interstitials do not delay the first actionable content beyond what policy allows.
- Prefer a plain-language fallback over a spinner-only or blank-shell failure mode.

## Release decisions

- Hold or roll back releases that push critical pages beyond declared thresholds unless a bounded waiver exists.
- If a waiver is used, record the waiver class, fallback plan, and review window rather than arguing the threshold after the fact.
- Re-check critical pages after template, CMS, localization, or script-vendor changes.
- Keep a current public notice or help route available when a degraded experience is knowingly in service.

## Evidence posture

- Preserve only critical page-class labels, mobile-review state, field-review state, lab-review state, budget-threshold class, release-decision class, hydration/fallback state, and last review time.
- Do not preserve full analytics dashboards, raw user telemetry, or bulky synthetic-run archives when bounded policy reconstruction is sufficient.
