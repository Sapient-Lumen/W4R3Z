# Research notes — 2026-05-31 sovereignty / bridge / ban pass

These notes are a research memory, not final truth.

## Legacy network shape

The aioslsk protocol notes describe classic Soulseek/Nicotine-style login as a TCP connection to a server, a listening peer port, a login message, status/listen/share-count advertisements, and regular server pings.
That confirms the central server is deeply involved in login/presence while peer connections still exist as a separate path.

The old Soulseek technical note says the search distribution network is a simple client hierarchy with child/parent relationships, dynamically constructed by the server to push search work off itself.
That matters: the legacy network already used clients as infrastructure.
The DHT design should do the same more explicitly and less centrally.

Nicotine+ currently has an open issue requesting I2P support, which makes I2P integration a plausible future PR topic rather than a wholly imaginary user desire.

## I2P substrate notes

SAM is still the likely Python-facing API.
The SAM docs show Destination key generation and explicitly say the default DSA_SHA1 signature type is not what most applications want; applications should specify `SIGNATURE_TYPE=7`.
That reinforces persistent Ed25519-ish identity planning at the application edge.

I2P floodfill routers are an important teacher for garden nodes.
I2P docs describe floodfill as a simple distributed storage mechanism using XOR closeness, with no central authority or consensus.
They also state floodfill is automatically enabled only for routers with sufficient configured bandwidth and health.
That supports the cube's garden-node model: service capacity, not truth authority.

The I2P threat model explicitly calls out starvation, flooding, CPU load, and floodfill DoS issues, including bad or missing lookup responses from hostile floodfills.
That supports disjoint paths, policy capsules for official surfaces, and local autocuration rather than one trusted supernode.

## Bridge distribution analogy

Tor bridges are relays that help users circumvent censorship, and the Tor site lists multiple bridge-distribution paths such as email, Telegram, and browser-integrated flows.
The useful analogy here is not Tor's directory authority model.
It is the idea that entrances need many distribution channels.
Our contact-card plane should be multi-channel by design.

## Peer scoring and local curation

Gossipsub v1.1 uses peer scores, pruning, random retention, and opportunistic grafting to improve underperforming meshes and recover from Sybil-poisoned pools.
The DHT should steal the local-scoring instinct, not the exact mechanism.
Semantic lies should weigh more heavily than latency.
Some randomness must remain so good new nodes can enter.

## Mutable authority notes

BEP44's mutable item model remains the compact reference point: immutable items by content hash, mutable items by Ed25519 public key plus optional salt, sequence, signature, and small value.
This is why policy capsules, contact card feeds, seed lists, and mutable sync heads can all be modeled as signed mutable records rather than special protocol gods.

IPNS is also a useful pointer model: signed records with sequence/validity/TTL map a stable name to changing content.
That further supports the DHT as a signed mutable control plane.
