# Substrate DHT architecture

## Layers

| Layer | Responsibility |
|---|---|
| I2P router | private routing, tunnels, netDb, Destinations |
| SAM adapter | Python-accessible STREAM/DATAGRAM transport boundary |
| DHT transport | message framing, timeouts, retries, peer challenge |
| Routing plane | node ids, k-buckets, lookup, disjoint paths |
| Record plane | immutable, provider, mutable, contact records |
| Validation plane | namespace-specific record validators |
| Consumer APIs | future apps ask for providers, records, mutable heads |

## Keyspace

Use a native **256-bit SHA-256 XOR keyspace** for the DHT. Keep a 160-bit
BEP44/BEP46 target facet for mutable-torrent compatibility reasoning, but do not
force the whole DHT into BitTorrent's 160-bit mainline shape.

## Node id

Preferred prototype node id:

```text
node_id = SHA256(domain || destination_hash || dht_public_key || work_nonce)
```

This binds routing identity to I2P reachability and a DHT signing key while
leaving room for low-cost work tickets.

## RPC set

Minimum RPC vocabulary:

```text
PING
FIND_NODE
GET_IMMUTABLE / PUT_IMMUTABLE
GET_MUTABLE / PUT_MUTABLE
ANNOUNCE_PROVIDER / FIND_PROVIDERS
SAMPLE_KEYS      # lab / diagnostics / future indexing with caution
```

`SAMPLE_KEYS` is intentionally suspicious. It is useful for observability and
indexing research, but it can amplify metadata exposure and crawling incentives.
