# Key compartment boundaries

The guessed production rule is simple:

```text
public keys are cheap; authority collapse is expensive later.
```

A DHT-over-I2P node should be comfortable carrying multiple keys:

| Role | Future reason |
|---|---|
| root/profile key | slow-moving local profile root |
| operator key | human/operator control, pause, resume, recovery |
| router Destination key | I2P reachability and tunnel identity |
| DHT node key | routing and signed contact cards |
| service signer | garden service catalogs, tickets, receipts |
| witness signer | local evidence receipts |
| mutable publisher | mutable heads, manifests, feeds |
| metrics signer | veiled diagnostics |

rev0043 does not store private keys. It models signed public-key binding capsules and asks whether a specific key may be used for a specific role in a specific scope.

The risky default is to reject suspicious dual-use pairs unless a later design deliberately allows a pair inside a narrow binding. In this cube, operator/service dual use, router/service dual use, operator/mutable-publisher dual use, and witness/mutable-publisher dual use all become quarantine pressure.

The open design question remains how strict production should be. A tiny leaf node might want fewer keys; a garden node should probably default to more compartments because it carries more authority, memory, service capacity, and metadata exposure.
