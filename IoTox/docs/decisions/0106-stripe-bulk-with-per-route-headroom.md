# ADR 0106: stripe bulk with per-route headroom

- Status: accepted construction policy; product scheduler pending
- Date: 2026-08-21
- Scope: forced-TCP Ratox and finite-file coexistence
- Depends on: ADR 0059, ADR 0060, ADR 0070, and ADR 0105

## Context

The patched provider services sixteen forced-TCP files fairly on one route, but one route delivers
data for only 17 of 32 admitted transfers. Four independently keyed routes deliver 32 aggregate
streams while Ratox remains exact. Raising the four-route population exposes multiple stalls even
though admission succeeds.

## Decision

1. Treat each Tox instance as an independent route and bind its transport identity to the same stable
   IoTox principal. Distinct Tox friendship is transport, never an authority grant.
2. Stripe finite-file work across routes; do not split or reorder frozen Ratox frames across them.
   Route zero remains the observed Ratox route and may carry only its bounded bulk share.
3. Qualify eight active bulk streams per forced-TCP route on this host. Admission above eight is not
   evidence of usable capacity: 40 is not repeatable and 48/56/64 violate terminal or lifecycle
   bounds.
4. Require every route to be explicitly confirmed and recorded. No silent route substitution,
   transparent rebonding, or fallback is implied.
5. Before product integration, add bounded route retry/backoff and a lane-loss gate that defines
   whether work pauses, cancels, or is reassigned without duplicating effects or starving Ratox.

## Evidence

`.sandwurm/exports/pairs/pair.hb491hc_` independently verifies four distinct forced-TCP routes,
32/32 active and progressed transfers, 40/40 exact terminal renders, zero 250 ms misses, and an empty
transfer set after one cancellation round. A prior four-route 32 proof independently passed the same
workload. Diagnostic 40/48/56/64 failures and the three-of-four convergence miss are retained in the
bulk evidence note without retaining private disks.

## Consequences

- The one-route 17/32 boundary no longer blocks construction-scale 32-stream bulk work.
- The product does not yet expose transparent bonding or a multi-route scheduler.
- Eight streams per route is a conservative measured point, not a universal toxcore constant.
- Route convergence and failure semantics precede the 1,000-sample Ratox matrix and sync transport
  integration.
