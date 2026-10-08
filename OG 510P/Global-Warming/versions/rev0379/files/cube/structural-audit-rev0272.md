
# Structural Audit — rev0272

Date: 2026-05-21 11:20 America/New_York

## Summary

rev0272 adds a recovery-rail layer to the datacube. The archive previously made service floors and hidden rails visible; this pass asks whether those services can be restored after the first response period. The new rail family covers emergency energy inputs, repair markets, claims and disaster-assistance cashflow, floodwater management, local markets, community bridges, agrifood inputs, and proof capacity.

## New canon files

- 323 — emergency fuel, black-start, critical charging, and energy inputs
- 324 — repair, inspection, contractors, materials, and permits
- 325 — insurance, disaster assistance, loss proof, and claims handling
- 326 — stormwater, drainage, culverts, dams, levees, and floodways
- 327 — small businesses, local markets, and essential enterprises
- 328 — community organizations, trusted intermediaries, volunteers, and mutual aid
- 329 — seed, fertilizer, feed, veterinary services, cold chain, and producer credit
- 330 — labs, inspection, sampling, permits, and environmental monitoring

## New cube artifacts

- `cube/recovery-rails-readiness.csv`
- `cube/restoration-bottleneck-register.csv`
- `cube/structural-audit-rev0272.md`

## Repairs

- Repaired the rev0271 open-question section by adding a dedicated rev0271 heading and renumbering its hidden-rail questions to 74–76.
- Added rev0272 open questions 77–84.
- Extended `cube/index.csv`, `cube/interdependency-matrix.csv`, `cube/service-floor-checklist.csv`, and `cube/hidden-rails-readiness.csv`.
- Added S576–S586 to the source register and routed each new source into numbered notes.

## Cube rule added

A service floor is not fully cube-ready unless it can identify its recovery rail and proof rail. For each packet, ask:

1. What keeps it alive during immediate degradation?
2. What restores it after failure?
3. What proves safety, completion, or eligibility?
4. What local-market or community bridge makes it reachable?
5. What scarce restoration rail will be contested by other services?

## Validation target

- Numbered markdown should run continuously from 00 through 330.
- `cube/index.csv` should contain 331 numbered rows.
- All bracketed source IDs used by numbered notes should resolve in `sources/register.md`.
- New source IDs S576–S586 should be cited at least once.
- Numeric `routes_to` targets should resolve to existing numbered files.

---
Citations point to `sources/register.md`.
