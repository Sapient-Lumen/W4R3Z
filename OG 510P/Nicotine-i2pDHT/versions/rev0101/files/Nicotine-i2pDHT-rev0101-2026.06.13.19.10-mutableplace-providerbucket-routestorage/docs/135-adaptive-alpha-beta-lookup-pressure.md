# Adaptive alpha/beta lookup pressure

The cube has been distrustful of greedy lookup speed for several revisions. rev0017 makes that distrust adaptive.

A Kademlia-like DHT often starts with a constant `alpha`: how many peers to query in parallel. That is elegant but dangerous on an I2P-shaped substrate. Latency is high, path behavior is uneven, and a captured family can answer quickly while slow honest families arrive later.

`adaptivealpha.py` does not optimize a real network. It consumes existing `LookupTranscript` objects and emits next-round knobs:

```text
alpha
beta
timeout_ms
target_success_families
target_success_paths
require_new_family
```

The current local rules are deliberately conservative:

- **fast-window capture** widens alpha, raises beta, increases family/path targets, and refuses acceptance;
- **bad-response pressure** quarantines convenient answers and asks elsewhere;
- **timeout pressure** increases concurrency and patience without removing family caps;
- **useful refusals** cause a hold/backoff posture rather than treating overload as failure;
- **slow honest success** encourages more patience before greedy acceptance;
- **diverse success without pressure** can accept.

This is not a magical independence oracle. Family IDs are still local hints. The important test shape is that a valid fast answer does not automatically beat diverse slower evidence.
