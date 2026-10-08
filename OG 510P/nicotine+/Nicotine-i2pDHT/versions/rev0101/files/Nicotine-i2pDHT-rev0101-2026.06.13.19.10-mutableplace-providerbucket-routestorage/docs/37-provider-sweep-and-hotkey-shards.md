# Provider sweep and hot-key shards

## Problem

A power user may have thousands, millions, or more provider-style advertisements.  A naive DHT client that reannounces each key independently will spend most of its time doing repeated lookups into the same keyspace neighborhoods.  On I2P, that is especially expensive.

## Guess: region sweep

Group advertisements by the high bits of their DHT key.  Sweep regions evenly across the reannounce interval.  For each region, discover the closest nodes once and batch the records that belong to that region.

This creates smoother traffic, avoids startup bursts, and makes contribution mode feel less like a denial-of-service against the user's own router.

## Starting constants to test, not freeze

```text
provider republish interval: 22h-ish starting guess
provider expiration:        48h-ish starting guess
region_prefix_bits:         8 to 12 in a mature network, smaller in lab
batch max weight:           role/profile dependent
```

These are not I2P measurements.  They are borrowed starting points from IPFS/libp2p practice and should be retuned after real I2P experiments.

## Hot keys

Hot records should not live only on the mathematically closest nodes.  For hot provider keys and important mutable heads:

1. Store at canonical k-closest nodes.
2. Store short-lived sloppy copies along successful lookup paths.
3. Let power-user mirrors carry hot sets voluntarily.
4. Tag sloppy copies as sloppy so they help discovery but do not override canonical validation.

## Python surface

- `sweep.py` models keyspace-region reannounce batching.
- `sloppy.py` models canonical plus sloppy placement.
