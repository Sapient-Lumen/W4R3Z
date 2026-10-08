# rev0005 garden-node dream

`garden node` is the word.

A garden node is a voluntary high-resource node that gives to the DHT: storage, bandwidth, uptime, routing freshness, repair labor, bootstrap help, and patient reannouncement.  It is a supernode in the practical sense, but not a ruler.  It has no special right to define truth, censor, rank the world, or become a mandatory entrance.

The emotional model is useful: a garden node cultivates.  It tends regions.  It remembers which paths were healthy.  It replants records before they expire.  It gives young nodes a place to enter.  It prunes obviously rotten contacts from its own local view.  It waters hot keys with sloppy replicas.  It warns itself and nearby clients when a region smells poisoned.

## Core guess

A good I2P-hosted DHT should have **many ordinary leaves** and **some generous gardens**.  The DHT should benefit from gardens without depending on any one garden.  Gardens should advertise what they are willing to do, and leaves should choose gardens through local observation, path diversity, and signed capabilities rather than through a central registry.

The key is to design garden power as *service capacity*, not *authority*.

```text
bad supernode:  accepts users, defines truth, owns lookup path, becomes mandatory

garden node:    stores/answers/repairs/witnesses, can be ignored, can be replaced,
                is selected locally, and is constantly cross-checked
```

## Why gardens belong here

Pure egalitarian overlays pretend all nodes can answer and store equally.  Real anonymous networks do not look like that.  Some users have fiber, spare disks, servers, and a desire to contribute.  Some users are intermittent laptops.  Some are mobile.  Some only wake briefly.  A DHT that does not admit this will either punish weak nodes or waste strong ones.

I2P itself already demonstrates a version of this shape: floodfill routers are a subset of routers that accept netDb stores and answer netDb queries, selected from higher-capacity routers with health checks.  That is not a reason to copy I2P netDb into the application DHT, but it is a reason to be honest that contribution tiers are natural.

## Garden-node law

1. **Give, do not govern.** Garden nodes can donate work; they cannot define truth.
2. **Advertise budgets.** A garden must say what it can actually afford: disk, RAM, bandwidth, mutable watches, provider records, maximum concurrent lookups.
3. **Prefer local curation.** No global reputation ledger is needed for v1.  Each node keeps its own encounter memory.
4. **Cross-check gardens.** Every garden service that can lie must be checked through disjoint paths or multiple gardens.
5. **Let gardens rest.** Load shedding is not failure.  A good garden refuses gracefully before it starts lying.
6. **Make contribution visible.** Garden operators should see what their node is helping with: records refreshed, stale heads repaired, lookups answered, bad regions detected.
7. **Keep metadata modes explicit.** Some garden services are high-metadata.  Do not smuggle them into a quiet default.

## The non-obvious reciprocal bargain

A garden gives to leaves, but it is not purely altruistic in the operational sense.  Serving others improves the garden's own DHT health:

- answering lookups refreshes routing buckets;
- accepting provider batches teaches which keyspace regions are hot;
- stewarding mutable heads teaches which publishers are stable;
- running sentinel checks teaches which peers lie, lag, or poison;
- serving bootstrap invites increases peer diversity;
- batching reprovide work protects the garden from bursty self-inflicted load;
- local gratitude/receipt signals can make the operator feel useful without creating a global authority.

That last point matters for growth.  A garden node should feel like a public library, not like a hidden daemon burning bandwidth for mysterious reasons.

## What rev0005 adds

- `src/i2p_dht_lab/garden.py` defines garden services, budgets, service planning, local encounter salience, and reciprocal benefit accounting.
- `tests/test_garden.py` checks that gardens are helpers, not authorities; that strong budgets unlock service offers; that false/stale behavior loses salience; and that helping creates useful local knowledge.
- `docs/43-garden-node-service-functions.md` names the services.
- `docs/44-autocuration-salience-engine.md` sketches local node encounter curation.
- `docs/45-supernodes-that-give.md` states the supernode posture directly.
- `docs/46-garden-node-protocol-sketch.md` starts the record/RPC vocabulary.

## Strongest current guess

The garden layer should be born as an **advisory service plane** over the DHT, not as a separate privileged DHT.  Garden advertisements are records.  Garden services are RPCs.  Garden selection is local.  Garden claims are cross-checked.

If this works, a future power user can say:

```text
I will contribute 2 GB of disk, 2 Mbps of upload, 12 hours/day of uptime,
10k mutable watches, 500k provider records, and sentinel checks for the regions
I naturally encounter.
```

The DHT then becomes more alive because it knows how to spend that gift.
