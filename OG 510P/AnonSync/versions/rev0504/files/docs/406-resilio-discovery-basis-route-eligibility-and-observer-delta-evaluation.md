# Resilio discovery-basis, route-eligibility, and observer-delta evaluation

## What current official docs still make clear

Another current Resilio pass again strengthens the main archive conclusion rather than weakening it.

Current official docs still show real product substance:

- a live v3 line with `3.1.2.1076`
- explicit admission that peers may be found through tracker, LAN discovery, or predefined hosts
- explicit admission that tracker learns share identity plus local/public endpoint facts so peers can attempt direct connection
- explicit admission that LAN discovery multicasts share identity and `IP:port` on port `3838`
- explicit admission that predefined hosts are a real first-class path in high-security networks and may be used when tracker and LAN search are impossible or prohibited
- explicit admission that direct connection is preferred for speed, relay is fallback, relay can slow transfer, and the peer list can say when a peer is actually relayed
- explicit admission that tracker/relay location itself depends on fetching `sync.conf`
- explicit admission that route success can still depend on listening-port reachability, NAT/firewall posture, proxy behavior, multicast allowance, and whether peers share any common protocol set
- explicit admission that a `LAN only` posture may still keep syncing over Internet until remembered global endpoints are cleared and the client restarted

That is not fake candor.
It is very useful operator truth.

## What still should not be cloned

The ordinary operator answer is still fragmented.
Current docs still require cross-reading at least seven places to answer four basic questions:

1. **How are these peers actually finding each other right now?**
2. **Which service, subnet, or pinned endpoint currently learns what about this share-seat relationship?**
3. **Why is this pair direct, relayed, or not connectable at all?**
4. **What least-widening repair would restore connectivity or directness without casually widening disclosure?**

Resilio still has strong ideas here.
It still does **not** earn direct interface cloning.

The reason is the same clone-veto rule now applied to another seam:

> one ordinary operator question should have one stable page answer.

Current Resilio still spreads the ordinary transport answer across key flow, folder preferences, ports/protocols, relay explanation, privacy/disclosure prose, LAN-only instructions, power-user preferences, slow-speed troubleshooting, and `Peers aren't connecting`.
So the product idea stays strong while the page contract still fails.

## Why this matters for AnonSync

AnonSync should borrow four important habits directly:

- **say how discovery is currently happening**
- **say when public infrastructure is participating**
- **say when relay is a speed/privacy trade and not just a neutral connected badge**
- **say when remembered endpoints keep a wider route posture alive**

But AnonSync should refuse four weaker habits:

- preference-only route truth
- troubleshooting-shaped explanations for why a pair is relayed or unreachable
- LAN-only instructions that only later reveal remembered public endpoint residue
- disclosure answers that require hopping between security prose, tracker notes, and connectivity troubleshooting

## Replacement pages added for this seam

This revision therefore adds four narrower replacement pages:

- `407` — Reachability basis
- `408` — Peer route
- `409` — Connectivity repair
- `410` — Exposure widening review

These pages keep the Resilio candor and reject the preference-plus-troubleshooting reconstruction path.

## Sharper non-clone line after this pass

The archive now has one tighter sentence for this seam:

> borrow Resilio's candor about tracker, LAN discovery, predefined hosts, relay fallback, and cached-route residue; refuse any interface contract where `how are these peers finding each other, who currently learns what, and what least-widening repair exists` still depends on reading settings docs, security prose, and troubleshooting articles together.

