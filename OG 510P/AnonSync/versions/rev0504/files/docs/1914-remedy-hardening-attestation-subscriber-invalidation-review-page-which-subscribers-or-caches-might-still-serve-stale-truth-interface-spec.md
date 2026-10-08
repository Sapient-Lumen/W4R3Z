# Remedy-hardening-attestation subscriber-invalidation review page — which subscribers or caches might still serve stale truth?

## Review question

Given that the case's governing receipt or audience-safe sentence has changed, which subscribers, caches, structured exports, or derived machine consumers might still render the stale truth, for how long are they allowed to do so, and what exact successor pointer or tombstone must they serve instead?

## Review panels

### 1) Subscriber inventory review

Force the operator to enumerate every subscriber class that can receive, cache, relay, or derive a machine-readable claim from this case.
The review must preserve at least these distinctions:

- push subscriber versus pull subscriber
- durable export mirror versus ephemeral session cache
- internal consumer versus external consumer
- named subscriber versus structurally unknown historical consumer
- authoritative consumer versus historical-snapshot-only consumer

### 2) Freshness-lease review

For each subscriber class require the operator to score:

- whether it may cache at all
- whether it must revalidate on every read or only after a bounded lease window
- whether it may pin a historical version for audit or replay purposes
- whether it must stop serving entirely on supersession until a successor is accepted

### 3) Invalidation and tombstone review

The page must compute and show:

- which subscribers require push invalidation now
- which subscribers only learn on next pull and therefore need a must-revalidate boundary
- which prior artifacts must turn into tombstone-with-successor rather than silently disappearing
- whether any public or external feed must freeze until invalidation evidence catches up

### 4) Residual stale-serving review

The review must preserve and score:

- subscribers still inside an authorized stale window
- subscribers already outside lease and therefore non-compliant if still serving
- unknown historical consumers for whom only a ceiling can be stated
- whether a historical snapshot is safely marked non-authoritative or still dangerously ambiguous

## Required outcomes

The page must support outcomes such as:

- `publish successor immediately and require revalidation for all pull consumers`
- `push invalidation confirmed for named internal dashboards; external feed frozen pending closure`
- `historical snapshot retained for audit, but tombstone pointer required on every replay surface`
- `browser sessions may keep prior wording only until lease expiry, then must reload or show tombstone`
- `stale serving structurally possible for unknown copied packet; stronger machine sentence remains blocked`

## Mandatory review discipline

The review must reject any path that tries to treat these as equivalent:

- surface recall and subscriber invalidation
- cache expiry and explicit tombstone publication
- historical snapshot and current authority
- push fanout initiated and push fanout confirmed
- no stale consumer observed and no stale consumer possible

## Required warnings

The page must render plain warnings when:

- a subscriber class has no explicit freshness lease
- a public or external feed still serves a version with no successor pointer
- a pull consumer can continue reading stale data past the allowed lease window
- a copied structured artifact still looks current because it lacks non-authoritative markings
- a broader machine-consumable sentence is being considered while unknown historical consumers still exist
