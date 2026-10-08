# Garden-node protocol sketch

This is not a wire spec yet.  It is a vocabulary for future fake-transport tests.

## Garden advertisement record

A garden advertisement is a signed mutable-ish record under the garden node's own identity or a delegated garden key.

```text
garden_ad.v1 = {
  node_id: bytes32,
  destination: i2p_destination_or_hash,
  garden_key: ed25519_pubkey,
  seq: uint64,
  expires_at: unix_seconds,
  services: [service_offer],
  budgets: budget_vector,
  modes: [metadata_mode],
  refusal_policy: {...},
  signature: sig(garden_key, canonical_payload)
}
```

The advertisement is not proof of honesty.  It is a menu.

## Service offer

```text
service_offer = {
  kind: seed_gate | region_gardener | mutable_steward | sloppy_cache |
        path_scout | sentinel | wake_courier | invite_bridge | bulk_reprovider,
  max_items: uint32,
  max_bytes: uint64,
  ttl_floor: seconds,
  ttl_ceiling: seconds,
  accepted_namespaces: [string],
  metadata_cost: quiet | connective | index | lab,
  load: low | medium | high | shedding
}
```

## Garden RPC candidates

```text
GARDEN_HELLO(ad_digest)
GARDEN_OFFER(service_filter)
GARDEN_REFUSE(service, reason, retry_after)
GARDEN_BULK_PROVIDE(region, provider_records[])
GARDEN_WATCH_MUTABLE(slot, last_seq_seen)
GARDEN_REPAIR_MUTABLE(slot, signed_head)
GARDEN_FIND_PATHS(target, diversity_requirements)
GARDEN_SENTINEL_CHECK(target, evidence_digest)
GARDEN_WAKE_STORE(delegated_record, ttl)
GARDEN_INVITE_PUT(invite_key, encrypted_envelope, ttl)
GARDEN_INVITE_GET(invite_key)
GARDEN_RECEIPT(transcript_digest, service, outcome)
```

## Validation order

A garden must validate before storing or helping:

1. canonical encoding valid;
2. namespace allowed;
3. size budget not exceeded;
4. TTL within range;
5. signature valid;
6. mutable sequence/CAS sane;
7. service-specific quota available;
8. local refusal policy not triggered.

## Selection order for leaves

A leaf should select gardens by portfolio:

1. must support the requested service;
2. not overloaded or refusing;
3. locally salient for this service;
4. diverse from other selected gardens;
5. not the only path to the target;
6. include some exploration/randomness.

## Receipts

Receipt payload:

```text
receipt.v1 = {
  garden_node_id,
  service,
  target_or_region_digest,
  request_digest,
  outcome: accepted | refused | repaired | answered | no_data,
  observed_seq: optional,
  count: optional,
  issued_at,
  signature
}
```

Receipts help debugging and local memory.  They do not become global currency in this cube.
