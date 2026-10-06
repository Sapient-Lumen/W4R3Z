# ADR-0122: hardware support qualification freshness boundary

Date: 2026-03-17
Status: Accepted

## Context

`adrs/ADR-0118-hardware-support-matrix-and-bundled-admission-boundary.md` fixed **where** supported-hardware claims live: `hw.support.matrix` is the digest-bound catalog artifact.
`adrs/ADR-0119-hardware-support-promotion-and-qualification-boundary.md` fixed that positive entries must carry a typed `qualification` summary.
`adrs/ADR-0120-hardware-support-qualification-receipt-boundary.md` fixed that the summary must point at a typed `hw.support.qualification.receipt`.
`adrs/ADR-0121-hardware-support-qualification-profile-boundary.md` fixed that receipts must point at a typed `hw.support.qualification.profile` so the support lane has a stable standard/proof split.

That still left one expensive ambiguity: the archive could say **which** standard and **which** proof backed a support claim, but not **when that proof stopped counting as fresh**.
In practice that means “recently verified” stays a prose judgement instead of a typed contract.
That is exactly how release-qualified support silently degrades into “someone ran the playlist some months ago on a slightly different kernel/firmware stack.”

Real ecosystems do not leave freshness entirely implicit.
Android positions CTS as part of the daily workflow and continuous build discipline for keeping compatibility intact across ongoing changes.
Canonical describes certified hardware as continuously tested throughout the Ubuntu release lifecycle.
Windows compatibility keeps qualification bound to official HLK playlists that advance with release trains.

## Decision

Accept a new typed freshness boundary for hardware support qualification.

1. **`hw.support.qualification.profile` now defines the freshness policy.**
   Profiles must carry `freshness.max_age_days_by_stage` and `freshness.reverify_on` (`reverify_on`).
   This makes “how old is too old?” part of the typed qualification standard instead of a lab note.

2. **`hw.support.qualification.receipt` now records the concrete freshness bound.**
   Receipts must carry `freshness.fresh_until` and `freshness.reverify_on`.
   `fresh_until` is derived from `qualification.last_verified_at` plus the profile's stage-specific freshness window.

3. **Preflight/reporting gets an explicit stale finding.**
   `hw.compat.report` may now emit `qualification-stale` when a matched support claim is backed by a receipt whose typed freshness window has elapsed or whose invalidating change class has landed.

4. **The matrix stays compact.**
   `hw.support.matrix.entries[].qualification` keeps `last_verified_at` as a compact promotion summary, but freshness authority lives in the receipt/profile pair and the target-specific report.
   The matrix does not become a live recertification service.

## Consequences

Good:
- B/workstation trusted-UI support can now say not just *what was qualified* but *whether that qualification is still fresh enough to count*.
- D/appliance bundles can ship support catalog + receipt + profile + freshness bound offline.
- A/fleet rollout gates can stop treating months-old lab evidence as equivalent to fresh qualification after kernel/firmware movement.
- The archive gains a small typed answer for the already-existing “recently verified recovery path” pressure.

Trade-offs:
- The support lane gets one more small contract surface.
- The archive still does not define a universal lab scheduler, certification portal, or automated replacement/publication service.

## Follow-up

This ADR does **not** decide:
- the full automation/notification workflow after sustained field regressions (the receipt-status semantics themselves now live in `adrs/ADR-0123-hardware-support-qualification-status-boundary.md`),
- the exact UX for showing `qualification-stale` on trusted-UI surfaces,
- or how broad qualification replay automation should become.

It only fixes the freshness boundary so the existing support catalog / proof / standard lane remains reviewable.
