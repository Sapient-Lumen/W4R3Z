# rev0004 power-user DHT dream: `powerloom-hotpath-quorumdream`

This revision accepts the user's instruction: stay in design space, keep only deep guesses, and forget any near-term application integration.  The subject is now a generic DHT that lives above I2P and is written in Python first so the algorithmic pieces can be simulated, falsified, and rewritten cheaply.

## Central guess

A DHT above I2P should not be a thin clone of Mainline DHT.  It should be a **three-plane substrate**:

1. **Routing plane**: Kademlia-like 256-bit XOR routing, destination/key/work-bound identities, old-contact preference, replacement caches, disjoint lookup paths.
2. **Record plane**: small validated records only: immutable blobs, provider records, mutable slots, contact/invite records, and future namespace-specific validators.
3. **Power plane**: voluntary contribution roles for sticky operators: gate, scout, archivist, sentinel, mirror, publisher.  These roles are hints and budgets, never authority.

The power plane is the new part of rev0004.  It is not a supernode plan.  It is a way to let high-uptime users contribute more storage, reannounce work, monitoring, and bootstrap help without turning them into trusted coordinators.

## Why this differs from a simple Kademlia port

I2P changes the economics:

- lookups are slower and more expensive than LAN/UDP BitTorrent lookups;
- latency is noisy and tunnel-dependent;
- IP-prefix diversity is unavailable;
- stable Destinations are valuable for stickiness but create linkability;
- datagrams are attractive but Streaming is easier to prototype and debug;
- a popular DHT will be attacked by Sybils, semantic falsehoods, empty responses, stale mutable heads, and hot-key overload.

So this revision makes four guesses:

1. **Never trust a single lookup path.** Use path-isolated queues and avoid merging all returned candidates into one global soup too early.
2. **Do not stop provider lookups merely because enough provider-looking answers arrived.** Finish path diversity first unless the user explicitly chooses a fast/unsafe mode.
3. **Reannounce by keyspace region, not by FIFO key list.** Power users with large indexes need sweep scheduling and batchable region work.
4. **Store hot keys canonically and sloppily.** Canonical k-closest placement remains the truth layer; sloppy breadcrumbs and hot caches are the liveness layer.

## New Python scaffolding

- `lookup.py` — disjoint lookup path planner and quorum decision helper.
- `sweep.py` — region-grouped provider/mutable reannounce scheduling.
- `sloppy.py` — canonical plus sloppy replica placement.
- `power.py` — contribution profiles and role hints.
- `adversary.py` — tiny observation/readout helpers for chaos tests.
- `mutable_family.py` — mutable slot families beyond single-writer heads.

These are not production implementation claims.  They are executable guess surfaces.

## Immediate design invariant

The DHT should be useful for quiet leaves, but the network should become dramatically better when power users turn on contribution roles.  A healthy power user should be able to say:

> I will keep a persistent I2P identity, keep my router warm, carry more records, sweep reannouncements smoothly, cache hot provider records, cross-check suspicious lookups, and provide bootstrap hints — without becoming a central authority.

## Nonclaim

rev0004 has no live SAM transport, no live churn measurements, no production security guarantee, and no claim that the chosen algorithms are correct.  The value is that the guesses are now documented and partially executable.
