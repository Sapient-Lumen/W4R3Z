# Remedy-hardening-attestation subscriber-invalidation lineage receipt page — freshness scope, successor pointer, and blocked machine overstatement

## Purpose

This page is the durable receipt that captures what machine consumers were allowed to serve, cache, or replay for a case at a specific time and under what invalidation rules.
It must survive later review and show not merely that publication changed, but the exact version token, freshness scope, tombstone posture, and remaining stale-serving ceiling that governed machine consumption.

## Receipt header

The receipt must print:

- receipt identifier
- case identifier
- source surface-claim-governance receipt identifier
- current governing receipt identifier
- current subscriber-invalidation class
- issuance time
- current authoritative version token
- strongest blocked broader machine-consumable sentence

## Receipt body

The receipt must always include:

- strongest currently machine-safe sentence
- subscriber inventory coverage class
- freshness-lease class summary
- push invalidation coverage summary
- pull revalidation coverage summary
- historical-snapshot permission summary
- tombstone requirement and publication summary
- exact reason broader machine language remains blocked

## Mandatory distinctions preserved by the receipt

The receipt must preserve at least these distinctions:

- current authoritative version versus previously served version
- cached-within-lease versus stale-beyond-lease
- historical snapshot versus current authority
- invalidation sent versus invalidation confirmed
- tombstone published versus silent absence
- named-subscriber closure versus global machine closure

## Example speakable sentences

The receipt should support outputs such as:

- `human surfaces downgraded; machine consumers still bounded by mixed revalidation paths`
- `named internal dashboards received successor pointers; external historical packets remain tombstone-required`
- `public machine feed frozen above the current floor until stale-serving risk closes`
- `older structured payload retained for audit only and is no longer authoritative`
- `global machine-safe overstatement remains blocked by unknown historical consumers`

## Claim ceilings

The receipt must never let later operators silently say:

- `the dashboard changed, so every consumer changed`
- `lease expired, so stale service became impossible`
- `historical JSON stayed downloadable and therefore stayed current`
- `notifications synchronized, therefore invalidation closed`
- `tombstone published once, therefore all machine consumers now point to the successor`
- `named internal closure means public machine closure`

## Precedence rules

The receipt must make these rules explicit:

- a new stronger machine-safe sentence becomes speakable only through a new receipt that widens machine-consumer budget explicitly
- expiry without successor pointer is not enough when historical artifacts can still be replayed or mirrored
- stale-serving debt remains open until every required subscriber is either current, within an authorized bounded lease, suspended, or tombstoned
- public machine language remains subordinate to permanent blockers such as off-world unknowns and open invalidation debt
