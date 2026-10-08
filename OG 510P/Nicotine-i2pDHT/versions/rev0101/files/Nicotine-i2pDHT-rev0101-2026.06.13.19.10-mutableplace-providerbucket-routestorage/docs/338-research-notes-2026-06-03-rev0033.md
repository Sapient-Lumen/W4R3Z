# Research notes — 2026-06-03 — rev0033

This turn did not add live external dependencies. The design remains guided by the same prior teachers:

- Kademlia/S-Kademlia style path pressure motivates not trusting fast compatibility claims alone.
- libp2p/Kad-DHT validator language motivates keeping validation/admission before dispatch.
- BEP44-style mutable heads motivate keeping small signed records but not treating them as latest without local memory.
- I2P/SAM remains the likely future non-Java integration seam, but this revision intentionally stays before live SAM side effects.

New local intuition:

```text
Protocol negotiation and state migration are both attack surfaces that look like chores.
```
