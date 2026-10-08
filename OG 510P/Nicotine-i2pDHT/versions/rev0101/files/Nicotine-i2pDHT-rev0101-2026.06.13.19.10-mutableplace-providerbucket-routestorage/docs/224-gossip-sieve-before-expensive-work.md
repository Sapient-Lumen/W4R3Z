# Gossip sieve before expensive work

Gossip is useful because it can repair stale local knowledge without a central entrance. Gossip is dangerous because a captured source can flood plausible route contacts, provider hints, witness hints, seed gates, range-sketch hints, and relay catalogs.

`gossipsieve.py` adds signed `GossipStatement` objects and a local sieve. The sieve checks:

- source signature;
- allowed gossip kind;
- scope prefix;
- replay memory;
- source/subject/kind sequence rollback;
- same-sequence fork pressure;
- time-window freshness via clock guard;
- family caps and family monoculture.

The result is not truth. It is an admitted set of hints for later validation, probing, route repair, or witness gathering.

Design rule:

```text
Signed gossip can enter the waiting room; it cannot self-authorize expensive work.
```
