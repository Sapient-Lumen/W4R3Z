# Contact cards and entrance seeding

A DHT above I2P needs entrances.
I2P already has its own network bootstrap and netDb, but the application DHT needs application-layer contacts: nodes that speak this DHT, advertise useful capabilities, and can introduce more nodes.

## Contact-card fields

```text
version/domain
I2P Destination or b32 address
DHT public key
node id = H(domain || destination_hash || public_key || work_nonce)
work nonce / work bits
issued_at
expires_at
capabilities
bootstrap hints
previous_card_hash, optional
signature
```

The point of binding node id to Destination + key is to prevent arbitrary keyspace placement without changing identity material.
This is not real Sybil resistance, but it blocks the cheapest lie.

## Entrance channels

| Channel | Use | Metadata cost | Why it matters |
|---|---|---:|---|
| Direct invite | Friend sends a contact file/link | Low | Most trustworthy cold start |
| Buddy exchange | Existing relationship leaks DHT card | Medium | Sticky, socially anchored |
| Room gossip | Public-ish room advertises cards | Medium/high | Fast growth |
| Search-result hint | Result includes optional DHT contact | High | Very high growth and leakage |
| Central side-load | Connected clients exchange cards while classic server exists | Medium | Transitional sovereignty ramp |
| Public seed list | Shipped or fetched signed defaults | Medium | Fast first run |
| Garden seed gate | High-uptime garden gives fresh contacts | Medium | Better diversity than static seeds |
| Cached last-good | Local memory of successful peers | Low | Makes restarts resilient |

The cube's guess is to allow these in modes rather than hide them.
Users who choose connective modes knowingly trade more metadata for faster network growth.

## Cache discipline

A good entrance cache is not just a bag of contacts.
It should preserve:

```text
freshness
channel diversity
garden diversity
key diversity
region/keyspace diversity
successful prior answers
policy refusals
semantic lies
```

A contact should decay, but a validated long-lived garden should not be thrown away just because a new random contact appears.
Freshness and usefulness both matter.

## What legacy clients can contribute

A legacy-network-aware client can contribute without becoming a garden:

```text
publish own signed contact card to buddies
accept contact cards from buddies
cache DHT entrances seen through rooms/searches
relay a tiny number of fresh garden contacts
export/import invite files
report invalid cards locally
```

This is mutual aid at leaf scale.
Every user does a little seeding.
Garden nodes do a lot of seeding.

## What contact cards must not become

They must not become a global identity registry, a permanent public profile, or a mandatory social graph.
They should be compact, expiring, signed entrance objects.
If a future app wants profiles, that is a different record layer.
