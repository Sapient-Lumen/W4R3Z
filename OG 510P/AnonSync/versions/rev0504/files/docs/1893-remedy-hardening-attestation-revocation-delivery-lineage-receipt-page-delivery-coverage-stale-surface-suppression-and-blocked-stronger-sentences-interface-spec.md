# Remedy-hardening-attestation-revocation-delivery lineage receipt page — delivery coverage, stale-surface suppression, and blocked stronger sentences

## Purpose

This page is the durable receipt that captures what level of revocation delivery and closure was honestly achieved for a case at a specific time.
It must survive later review and show not merely that a corrective wave existed, but what cohort was truly reached, what stale surfaces were suppressed, what residual risk remained, and which stronger closure sentence the product refused to make.

## Receipt header

The receipt must print:

- receipt identifier
- case identifier
- source reliance receipt identifier
- corrective-wave identifier
- current governing receipt identifier
- current delivery-governance class
- current stale-surface class
- current closure threshold class
- receipt issuance time

## Receipt body

The receipt must always include:

- strongest speakable closure sentence
- strongest blocked global all-clear sentence
- strongest blocked historical-only-everywhere sentence
- reachable dependent count
- delivery-confirmed count
- acknowledgement-complete count for required cohort
- stale-surface suppressed count
- residual-live-surface count
- unreachable-dependent count
- escalation owner
- exact reason broader closure is blocked

## Mandatory distinctions preserved by the receipt

The receipt must preserve at least these distinctions:

- wave opened versus delivered
- delivered versus acknowledged
- acknowledged versus successor-bound
- successor-bound versus stale surface suppressed
- named-cohort closure versus global closure
- residual risk preserved versus residual risk absent

## Example speakable sentences

The receipt should support outputs such as:

- `corrective wave opened; callback coverage incomplete`
- `delivered to all reachable dependents; acknowledgement still pending for one required human consumer`
- `all required internal dependents acknowledged and all internal stale surfaces suppressed`
- `named cohort closed; one external exported artifact remains live without callback path`
- `historical only for the required cohort, not historical only everywhere`

## Claim ceilings

The receipt must block false upgrades such as:

- `everyone got the correction`
- `nothing stale remains`
- `the old ruling is dead everywhere`
- `global closure achieved`

unless the receipt actually carries the evidence needed for those stronger statements.
