# Official voter-information API surface checklist

Use this quickcheck when an office exposes voter-information APIs, structured data feeds, public query endpoints, or machine-readable widget backends that may be reused by first-party or third-party public consumers.

## Before publishing or changing the machine-readable surface

- Confirm the linked HTML page is still the right **current official destination** for the underlying voter question.
- Confirm the machine-readable surface identifies the responsible office or jurisdiction clearly enough for downstream consumers.
- Confirm the public answer is explicitly tied to the right election scope or supported-election window.
- Confirm the current help/contact route is visible for consumers and users when the machine-readable layer cannot safely resolve the answer.
- Confirm any endorsed widget/app/embed preserves the direct official landing page rather than acting like a free-floating answer.

## Scope, freshness, and cache behavior

- Check whether the response is valid only for a specific election ID, election scope, or live-election window.
- Check that freshness semantics are explicit enough for clients, caches, and republishers.
- Check cache headers and any documented maximum cache age for voter-information responses.
- Treat polling-place, early-voting, office-hours, and deadline-related API outputs as stale-data risks.
- Re-review machine-readable public surfaces after schedule changes, office changes, and election rollover.

## Ambiguity, source precedence, and no-data handling

- Make sure multiple-election states do not silently collapse into a guessed answer.
- Make sure official-source preference or official-only behavior is documented strongly enough for public consumers.
- Do not let no-data, unsupported-election, or quality-withheld states read like “you are not eligible” or “no voting path exists.”
- Route incomplete or contested results to the current official help lane.
- Preserve enough bounded trace to reconstruct what source/freshness/fallback policy controlled the public answer.

## Minimization and evidence posture

- Do not retain raw user query logs or individualized address lookup histories just to prove the public API/feed policy existed.
- Preserve only the bounded trace needed to reconstruct election scope, freshness/cache posture, source precedence, and fallback routing.
- Keep API keys, secrets, and internal debugging artifacts out of publishable evidence.
