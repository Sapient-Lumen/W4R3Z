# Identity and Sybil-light controls

Strong Sybil resistance is not solved here. The design uses cheap, local,
low-regret controls.

## Identity pieces

- I2P Destination: reachability and pseudonymous endpoint.
- DHT Ed25519 key: signs records and RPCs.
- Work nonce: optional admission friction.
- Node id: hash-bound to Destination + key + nonce.

## Low-hanging controls

- Reject arbitrary node ids; recompute them from public identity material.
- Require signed RPC envelopes and signed mutable/provider records.
- Challenge peers over their advertised I2P Destination before giving them
  valuable routing-table slots.
- Use replacement caches and failure accounting.
- Use disjoint lookup paths.
- Keep reputation local.
- Keep public seed lists diverse and signed, but not mandatory.
- Offer easy entrance modes; apply higher friction only to storage/seed roles.

## Work tiers

The prototype has deliberately tiny work tiers:

```text
open:        0 bits
contributor: 8 bits
storage:    10 bits
seed:       12 bits
```

These are placeholders for tests and demos, not production settings.
