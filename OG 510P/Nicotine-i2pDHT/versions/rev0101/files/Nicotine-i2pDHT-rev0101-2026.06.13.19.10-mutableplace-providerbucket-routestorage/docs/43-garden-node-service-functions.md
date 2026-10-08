# Garden-node service functions

Garden services are optional advertised capabilities.  They should be small enough to test and combine.  A garden node may offer some services and refuse others.

## Service table

| Service | Helps leaves by | Helps the garden by | Risk |
|---|---|---|---|
| Seed gate | Giving fresh bootstrap contacts and invite entry points | Improves peer diversity and bucket freshness | capture if a leaf trusts only one gate |
| Region gardener | Reannouncing provider/mutable records by keyspace region | Makes heavy contribution predictable and amortized | learns which regions are hot |
| Mutable steward | Watching signed mutable heads, repairing stale replicas, noticing rollbacks | Builds publisher stability priors and hot-head cache | metadata around subscriptions |
| Sloppy-cache mirror | Holding short-lived breadcrumbs for hot keys outside canonical k | Increases cache hit rate and reduces repeated long lookups | can serve stale/biased breadcrumbs |
| Path scout | Maintaining diverse contacts for lookup path isolation | Improves own routing table and latency knowledge | could steer if not cross-checked |
| Sentinel witness | Cross-checking false providers, stale heads, empty clusters | Learns bad local peers and poisoned regions | may become de facto trust source if overused |
| Wake courier | Temporarily holding delegated records for sleeping nodes | Stable relationships and bounded storage contracts | can learn mobile/sleep patterns |
| Invite bridge | Storing one-time rendezvous hints or blinded contact envelopes | Brings fresh honest peers into the garden's view | abuse/spam and social metadata |
| Bulk reprovider | Accepting batched provider announcements from high-volume publishers | Avoids one-lookup-per-key churn; learns batch regions | can be spammed by fake inventories |
| Diagnostic mirror | Returning signed transcripts of what it saw for a lookup/store | Better self-debugging and community bug reports | transcript metadata must be bounded |

## Salient unobvious functions

### 1. Garden-assisted region sweep

A high-volume publisher should not perform one expensive lookup per key forever.  It can group advertisements by keyspace region and ask several gardens to help place or refresh that region.  The garden does not need to own the records; it just becomes a scheduler, validator, and polite bulk writer.

Unobvious benefit to garden: it gets **predictable work** instead of random bursts.  Predictable work is easier to rate-limit, easier to account for, and easier to expose in a UI.

### 2. Mutable-head stewardship

Mutable slots are fragile because they change, expire, and can be eclipsed.  A garden can watch a bounded number of heads, remember the highest validated sequence, and re-verify through multiple paths.

Unobvious benefit to garden: mutable heads become a high-quality signal about which nodes publish responsibly.  That signal is local and operational, not a global reputation score.

### 3. Sloppy breadcrumbs, not content hoarding

A garden should usually store locator breadcrumbs, not arbitrary content.  This follows the Coral-style lesson: the DHT should help find copies and caches, not become an unbounded content warehouse.

Unobvious benefit to garden: breadcrumbs give high cache leverage per byte.  They also let a garden spend tiny disk on huge reachability improvement.

### 4. Sentinel checks as self-defense

A garden that serves many lookups will see contradictions.  It can maintain a local anomaly map: these contacts often return false providers, these regions have stale mutable heads, these paths go empty together.

Unobvious benefit to garden: sentinel work protects its own future lookups and lets it shed load from peers that waste its resources.

### 5. Wake courier contracts

Intermittent nodes can delegate small signed records to a garden for a short TTL.  The garden holds them, republishes them, and deletes them on expiry.  The leaf gains continuity.  The garden gains a stable peer relationship and bounded work.

Unobvious benefit to garden: sleeping-node contracts make contribution emotionally legible.  The operator can see: "I kept 392 peers reachable while they were offline."  That is sticky.

### 6. Invite bridge with blinded envelopes

A garden can hold one-time invite packets without knowing their eventual app meaning.  The packet can be addressed by a random invite key, encrypted to the recipient, and garbage-collected quickly.

Unobvious benefit to garden: invite traffic brings new peers through the garden, improving diversity, but should be rate-limited hard because it is a spam surface.

## Service refusal is a feature

Garden nodes should advertise refusal states:

```text
accepting: yes
load_shed: provider_bulk
reason: storage_budget_80_percent
retry_after: 3600 seconds
```

A garden that refuses honestly is more valuable than a garden that accepts and lies.
