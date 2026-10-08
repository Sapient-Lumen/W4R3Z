# 545 — Nuclear emergency preparedness: COP clock, operational-period handoff, and decision-trace firebreak

Rev0338 addresses the shared failure mode above the branch proof spines: many packets can be locally plausible while the common operating picture is stale, internally inconsistent, or not carried forward during an operational-period handoff.

## Hard rule

Public NIMS, ICS, EOC, COP, Community Lifelines, REP, Appendix E, public dashboard, public meeting, public AAR, map screenshot, IAP form, situation report, source ID, or duplicate source URL can create a demand, clock, cap, contradiction, or reopen signal. **It cannot close local emergency-readiness evidence.**

A complete-looking COP packet is only a candidate for adjudication. It still needs branch reconciliation, stale-clock review, conflict handling, CAP/retest/verifier linkage, sensitive-annex split, public-safe surrogate mapping, and public-claim gating.

## Evidence route

`branch packet -> source clock -> COP situation board -> map-layer provenance -> decision conflict ledger -> mission/task board -> IAP/ICS integrity -> operational-period handoff -> CAP/retest/verifier -> public claim gate`

## What this prevents

The false green board: an EOC, EOF, JIC, or county/status board that says a function is ready while a branch clock is stale, a map layer is unverified, a mission task is unassigned, a public message references a superseded PAD/PAR, a field reading contradicts the plume model, a route is closed by lifeline damage, a hospital or CRC packet is capped by water/power/fuel, or the next operational period receives no explicit owner for remaining P0 defects.

## New proof surfaces

Rev0338 adds packet requirements for COP proof ladder, situation board fields, operational-period handoff, stale data clocks, decision conflicts, IAP/form integrity, mission/task board fields, GIS/map-layer provenance, JIC/COP synchronization, cross-jurisdiction COP conflicts, branch dependency caps, and open workorders.

## Claim boundary

No real-site readiness or unreadiness claim. REAL_BVPS_PUBLIC_ONLY remains public-context-only.
