# I2P transport assumptions

The DHT is above I2P. I2P's own netDb is not the application DHT.

## Prototype transport posture

- Python talks to a local I2P router through SAM.
- SAM Streaming is the easiest first live transport because it looks TCP-like.
- SAM Datagrams are attractive for Kademlia RPC efficiency, but the implementation
  matrix and SAM 3.3 feature differences mean they should not block the DHT core.
- The DHT RPC envelope should be transport-neutral so both can be tested later.

## What a contact means

A contact is not an IP/port. It is:

```text
node_id
I2P Destination
DHT public key
capabilities
last seen / failure state
optional work bits
```

## Runtime challenge

Before a contact becomes routing-table-important, the live implementation should
challenge it over its I2P Destination and verify a DHT-key signature. This proves
that the remote endpoint reachable at the Destination also controls the DHT key,
without needing the storage node to trust an external directory.
