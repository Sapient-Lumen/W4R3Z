# Python DHT research notes

## Libraries worth cribbing from

| Project | Why inspect it | Caveat |
|---|---|---|
| `bmuller/kademlia` | compact asyncio Kademlia shape; good reference implementation feel | UDP/IP assumptions, not I2P, not mutable-record rich |
| `aiobtdht` | asyncio BitTorrent DHT and KRPC layering | small project; BitTorrent-specific, UDP |
| `nitmir/btdht` | BitTorrent DHT crawler/extension lessons | crawler orientation, mainline assumptions |
| `py-libp2p` / Kad-DHT issues | provider records, validators, peer routing vocabulary | Python DHT support appears evolving; don't depend on it as finished substrate |
| `webtorrent/bittorrent-dht` | not Python, but strong BEP44 test culture and robust offline tests | JavaScript, UDP, mainline DHT constraints |

## Cribbing decisions

- Use `bmuller/kademlia` as a mental model for small asyncio-first routing code.
- Use BitTorrent DHT specs for record-size discipline, mutable slots, and compact
  canonical wire ideas.
- Use libp2p's validator/provider vocabulary, not its whole stack.
- Use WebTorrent's test posture: offline tests, deterministic vectors, compact
  fixtures.

## Avoid for now

- Do not make py-libp2p a dependency for the first prototype.
- Do not clone Mainline DHT exactly; the I2P substrate changes transport and
  identity assumptions.
- Do not build crawler/indexing features before the record validator layer is
  explicit.
