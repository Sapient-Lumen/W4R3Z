# Route gossip repair and stale-contact eviction

A DHT over I2P will have sticky identities and cached contacts. That stickiness helps cold starts, but it also creates a stale-contact and gossip-capture surface.

`routegossip.py` models a local book of contacts:

```text
RouteContact
RouteGossipBatch
RouteGossipBook
RouteGossipPolicy
RouteGossipReport
```

A contact carries:

```text
node_id
destination_hint
family_id
introduced_by
first_seen_at / last_seen_at
success_count / failure_count / refusal_count
stale_after_seconds
```

The current local decisions are:

```text
accept_repair_contacts
evict_stale_then_repair
continue_low_diversity
quarantine_captured_gossip
empty
```

The key distinction is **family diversity versus introducer diversity**. A captured garden might provide many contacts with different apparent families while still dominating the introduction path. rev0016 therefore tracks both:

```text
contact.family_id       # local path/family hint
contact.introduced_by   # who handed us this contact
```

The tests pin three hard guesses:

1. stale contacts are evicted before repair contacts are accepted;
2. one introducer dominating selected contacts is quarantine pressure;
3. many same-family contacts are not repair diversity.

This is not a routing-table replacement. It is a repair-pressure object that should eventually feed routing buckets, route succession, and garden seed-gate behavior.
