# Remedy-hardening-attestation subscriber-invalidation contract sheet page — freshness lease, invalidation fanout, and tombstone policy

## Purpose

This page is the compact contract for a case whose audience-facing surfaces are already governed, but whose structured consumers, caches, sessions, copied packets, or feeds still need an explicit freshness and invalidation answer.
It exists so the product can distinguish `current sentence changed`, `subscriber still within lease`, `must revalidate now`, `tombstone must be served`, and `stale serving still structurally possible`.

## Core fields

- case identifier
- source surface-claim-governance receipt identifier
- current governing receipt identifier
- current subscriber-invalidation class
- current authoritative version token
- superseded version token set
- subscriber cohort count
- subscriber cohort fully enumerated count
- cache-bearing surface count
- push-invalidation required count
- push-invalidation confirmed count
- pull-revalidation required count
- pull-revalidation completed count
- pinned-historical-subscriber count
- stale-serve suspicion count
- tombstone-required flag
- tombstone-published count
- successor-pointer coverage class
- freshness-lease class
- must-revalidate deadline
- longest authorized stale window
- freeze-public-machine-feed flag
- historical-snapshot permission class
- strongest blocked machine-consumable sentence
- next evidence that upgrades invalidation closure confidence
- next evidence that forces freeze, tombstone, or escalation now

## Subscriber-invalidation classes

The page must model at least these distinct classes:

- subscriber inventory incomplete
- inventory known, lease policy incomplete
- current version issued, invalidation not yet fanned out
- push invalidation sent, confirmations incomplete
- pull revalidation required on next read
- stale serving allowed only within bounded lease
- stale serving blocked and tombstone required
- successor pointer published for all required machine consumers
- historical snapshot allowed but non-authoritative
- public machine feed frozen pending closure
- invalidation closure achieved for named subscriber cohort only
- broader machine-consumable sentence blocked

## Subscriber classes

The page must support at least these subscriber types:

- browser session
- desktop UI cache
- WebUI session
- mobile notification or local notification cache
- API poller
- webhook or push subscriber
- exported receipt mirror
- copied structured packet or bundle
- internal dashboard or report cache
- external dependent feed
- offline replica or intermittently connected consumer
- unknown historical machine consumer

## Freshness-lease classes

For every subscriber or cache-bearing artifact the page must preserve at least these classes:

- no caching allowed
- serve-once then must-revalidate
- bounded TTL with mandatory revalidation
- pinned-to-explicit-version only
- historical snapshot allowed, non-authoritative
- tombstone-only after supersession
- suspended until successor receipt accepted
- structurally unverifiable freshness

## Fixed rendering order

Every subscriber-invalidation contract sheet must render the same sections in the same order:

1. **Strongest currently machine-safe sentence**
2. **Current authoritative version and freshness lease**
3. **Subscriber inventory and invalidation fanout**
4. **Tombstone, successor pointer, and stale-serve blockers**
5. **Blocked stronger machine-consumable sentences**

## Hard rules

The page must never silently upgrade:

- `UI updated` into `all machine consumers updated`
- `cache lease exists` into `cache still safe after downgrade`
- `entry disappeared from one history surface` into `all stale derivatives invalidated`
- `notification synchronized` into `subscriber acknowledged successor`
- `old export remains downloadable` into `old export remains authoritative`
- `public feed still online` into `public feed still entitled to strongest current sentence`

## Minimum operator questions answered

The page must let a later operator answer, without hunting across other pages:

- which subscriber classes can still serve this case's sentence
- which exact version token is authoritative now
- how long any stale rendering is still authorized, if at all
- who must revalidate, who must accept push invalidation, and who must receive a tombstone
- whether historical snapshots remain allowed and under what non-authoritative markings
- exactly which broader machine-consumable sentence remains blocked and why
