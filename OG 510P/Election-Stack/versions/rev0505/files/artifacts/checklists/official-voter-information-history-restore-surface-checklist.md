# Official voter-information history-restore surface checklist

Use this quickcheck when an election office expects the public to return to an already-open official route through Back/Forward, hidden-tab/app switching, session restore, or duplicate tabs.

## Inventory and scope

- Identify routes where the page may remain open while the voter leaves and later returns.
- Distinguish this from first-load cache freshness, share-safe URLs, and generic timeout handling.
- Re-check routes where a stale-on-return answer could misdirect the voter about location, eligibility, deadline, or status.

## Return-state classes

- Review Back/Forward history return, hidden-tab/app-switch return, restore/bfcache return, and duplicate/parallel-tab behavior separately.
- Decide which classes are harmless, revalidated, warning-worthy, or unsupported.
- Do not assume one good load proves every later return is safe.

## Freshness and recovery

- Check whether the route revalidates or visibly warns when the controlling answer may have changed while the page was hidden or restored.
- Preserve enough route context that refresh/re-entry does not dump the voter into a generic home page.
- Provide a visible last-checked, refresh-required, or re-entry cue when preserved content may no longer be current.

## Parallel-tab divergence

- Review whether duplicate/open-parallel tabs can drift, overwrite each other, or show conflicting status.
- If multi-tab use is unsupported or risky, say so clearly and provide a safe restart/re-entry path.
- Do not leave users with two contradictory official answers and no visible recovery cue.

## Evidence posture

- Preserve tested route labels, reviewed return-state classes, freshness/revalidation posture, divergence policy, safe re-entry/help routing, and last review time.
- Do not preserve user-level session replays, browser-history dumps, named-user visibility telemetry, or individualized restore traces when bounded policy reconstruction is sufficient.
