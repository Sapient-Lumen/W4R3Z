# Research notes — rev0017

The external teachers still point in the same direction.

## Provider sweeps

The libp2p/Kad-DHT Reprovide Sweep idea remains a strong garden-node clue: group provider records by XOR keyspace region and reprovide by region instead of performing a full DHT lookup per key. This supports the new `RegionLedger` surface.

## Disjoint lookup paths

S/Kademlia remains the main old teacher for path-diverse lookup pressure: use multiple disjoint paths and avoid collapsing routing into a single adversary-influenced candidate soup. This supports the adaptive alpha/beta surface.

## I2P transport assumptions

SAM remains the likely Python/non-Java API, but SAM 3.3 primary/subsession convenience cannot be assumed for i2pd bundle-first work. The cube keeps SAM shadows and adaptive lookup logic separate from live router integration.

## Floodfill/garden warning

I2P floodfill routers are useful capacity nodes but hostile/unreliable floodfills can return bad/no responses or influence keyspace visibility. Garden nodes should keep the same constraint: capacity and evidence, not authority.

## Tombstones

Tombstone/revocation memory is the next mutability pressure surface. The cube should keep testing resurrection, rollback, fork, and stale-cache interactions before it claims any production mutable naming behavior.
