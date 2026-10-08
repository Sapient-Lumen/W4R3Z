# Autocuration salience engine

Autocuration is local memory about nodes we encounter.  It is not global reputation and not a blacklist.

The engine asks: **which contacts have been saliently useful or harmful to this node's own DHT life?**

## What to remember

Store compact encounter facts:

```text
node_id
first_seen / last_seen
successful_queries
successful_stores
validated_records_returned
mutable_freshness_hits
provider_truth_hits
false_provider_events
stale_mutable_events
empty_path_events
avg_rtt_ms
path_diversity_tag
service_capability_tags
load_shed_events
```

The record should age.  Old sins and old virtues decay unless repeated.

## Salience, not virtue

A high salience score means "locally useful for this kind of operation."  It does not mean honest in the universal sense.

A node can be:

- a great bootstrap seed but a poor mutable steward;
- a slow but reliable archivist;
- a fast but dangerous false-provider source;
- useful for one keyspace region and unknown elsewhere.

The UI should not show a moral badge.  It should show operational language:

```text
good for: bootstrap, provider sweep
weak for: mutable freshness
risk flags: stale-head repeats
```

## Scoring guess

A first scoring guess:

```text
score =
  + 5 * validated_records
  + 4 * successful_stores
  + 3 * successful_queries
  + 2 * path_diversity_bonus
  + 2 * uptime_bucket
  + 1 * graceful_refusals
  - 8 * false_provider_events
  - 7 * stale_mutable_events
  - 4 * empty_path_events
  - 2 * overload_without_refusal
  - 1 * high_latency_bucket
```

The exact numbers are placeholders.  The important rule is that *semantic lies cost more than slowness*.  Slow nodes can still be useful.  False providers and stale mutable heads are poison.

## Garden selection

When choosing gardens, use **portfolio selection**, not top-one selection.

A leaf should prefer:

- at least three gardens for important mutable/provider lookups;
- different path-diversity tags;
- different service specialties;
- no more than one garden from a locally suspected cluster;
- some random exploration even when favorites exist.

This creates a pressure where garden nodes become useful by serving well, but no single garden becomes mandatory.

## Receipts without global authority

Gardens may issue small signed receipts:

```text
I accepted N records in region R at time T under budget B.
I answered lookup transcript digest D.
I refused service S due to budget limit L.
```

Receipts are diagnostic and local.  They are not global reputation coins.  They can help a client remember who helped, help a maintainer debug, and help an operator see contribution impact.

## Privacy guardrail

Autocuration must be scoped by mode.  Quiet clients should store less and share nothing.  Garden operators may store more because they explicitly chose contribution mode.  No client should upload its encounter ledger by default.
