# Research notes — rev0030

Design reminders used this turn:

- Kademlia's old-contact preference and least-recently-seen eviction rule remain a warning against replacing stable local memory with novelty just because fresh contacts appear.
- Peer stores need TTLs, provenance, and persistence discipline; an address book is a routing memory boundary, not a random cache.
- Set reconciliation ideas such as PinSketch/minisketch are useful future teachers, but rev0030 deliberately implements only exact toy digest sketches to test semantics before optimizing.
- Negative answers in adversarial DHTs deserve first-class treatment. Empty results are not neutral; they can stop discovery.


Additional branchlet-fold reminders:

- Bootstrap is also set reconciliation: many entrances are useful only if channel, introducer, live-probe, and egress metadata surfaces do not collapse together.
- Key crisis work is most dangerous at restart/checkpoint boundaries; a plausible recovery record must not launder away tombstones or revocations.
- Delta repair should privilege negative hard evidence first. Tombstones, compromise markers, and revocations deserve repair priority over ordinary provider convenience.
