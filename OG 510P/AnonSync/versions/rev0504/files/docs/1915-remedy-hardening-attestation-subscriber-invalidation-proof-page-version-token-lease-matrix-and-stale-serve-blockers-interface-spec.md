# Remedy-hardening-attestation subscriber-invalidation proof page — version token, lease matrix, and stale-serve blockers

## Purpose

This page is the durable proof that the product did not stop at recalling human-visible wording, but also controlled which machine consumers could still serve each version and under what freshness rules.
It must let a later verifier see not only the current authoritative version token, but which subscribers were allowed to cache, how long their leases lasted, and what happened when those leases ended.

## Sections

### 1) Invalidation-governance header

Publish:

- case identifier
- source surface-claim-governance receipt identifier
- current governing receipt identifier
- current subscriber-invalidation class
- current authoritative version token
- strongest machine-safe sentence in force

### 2) Subscriber-by-lease matrix

For each subscriber or cache-bearing artifact print:

- subscriber identifier or class
- subscriber type
- latest known served version token
- freshness-lease class
- lease start time
- lease expiry or must-revalidate time
- push or pull invalidation path class
- current compliance status
- historical-snapshot permission class

### 3) Invalidation event summary

For each downgrade, supersession, or freeze event print:

- superseded version token
- successor version token
- push fanout issued time
- push confirmations received
- pull revalidation completion count
- tombstone publication status
- public-feed freeze status if any

### 4) Residual stale-serving block

The proof must score every still-risky machine consumer:

- subscriber class or artifact identifier
- stale-serving risk reason
- whether still inside lease or already out of bounds
- strongest sentence it may still serve, if any
- blocker preventing broader machine-safe closure

### 5) Closure summary

The page must compute and print:

- current authoritative version token
- named-subscriber invalidation coverage
- stale-serving still authorized count
- stale-serving now non-compliant count
- tombstone coverage status
- strongest blocked broader machine-consumable sentence

## Mandatory proof distinctions

The proof must preserve at least these distinctions:

- current version token versus historically retained version token
- active cache lease versus expired lease
- explicit tombstone publication versus silent disappearance
- push-confirmed invalidation versus next-read revalidation only
- historical snapshot allowed versus stale serving allowed
- no evidence of stale serve versus proof of stale-serve impossibility

## Claim ceilings

The proof must never permit these sentences without direct support:

- `all subscribers are current because the main UI is current`
- `TTL elapsed, therefore no stale copy can still be served`
- `historical export stayed online but could not mislead`
- `notification sync implies cache invalidation closure`
- `old machine-readable payload disappeared from one surface, therefore every consumer got the tombstone`
- `public machine feed may speak the strongest current sentence despite open invalidation debt`
