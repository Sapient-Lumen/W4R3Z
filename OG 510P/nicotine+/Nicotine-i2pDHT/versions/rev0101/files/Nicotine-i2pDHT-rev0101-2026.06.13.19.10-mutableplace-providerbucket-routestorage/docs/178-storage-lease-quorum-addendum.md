# Storage-lease quorum addendum — rev0019

`storeflight.py` answers garden admission and custody-receipt pressure. `storagelease.py` answers a different question: after a record was admitted, is there enough live lease evidence to keep treating it as locally durable?

The local rule is:

```text
exact digest + live lease window + enough storage-node families + no same-sequence lease fork + no live tombstone = usable storage lease quorum
```

The word quorum is still local. It is not consensus, not global deletion truth, and not proof that a storage node will keep data forever. It is a pressure gate before higher layers say “this head/provider/tombstone/contact lease has enough storage life to be relied on.”

Risk tested in `tests/test_rev0019_storeflight_leasequorum_readrepair.py`:

- live diverse storage leases are accepted;
- short lease horizons become renew-soon pressure;
- same-node same-sequence divergent lease receipts quarantine the lease set;
- live tombstones block otherwise convenient lease evidence.

This is intentionally separate from `leasequorum.py`, which is about entrance/contact-lease source diversity. `leasequorum.py` asks “are my entrances captured?” `storagelease.py` asks “is this stored record still lease-backed?”
