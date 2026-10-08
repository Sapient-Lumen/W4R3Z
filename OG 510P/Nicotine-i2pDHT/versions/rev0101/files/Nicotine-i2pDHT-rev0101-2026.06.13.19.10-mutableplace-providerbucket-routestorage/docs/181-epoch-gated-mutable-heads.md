# Epoch-gated mutable heads

`epochgate.py` is the cube's first direct answer to the mutable-naming problem after the IPNS warning.

A signed head is not enough.  A local client/garden needs to know whether a head:

- is signed by the expected authority key;
- belongs to the expected purpose and scope;
- is inside a bounded validity window;
- advances the locally accepted sequence;
- links to the previous accepted digest;
- has enough path/source diversity for the current risk policy;
- conflicts with another same-sequence head;
- tries to roll local memory backward.

This is still not consensus.  The only truth claimed is local monotonic memory plus typed evidence pressure.

Useful future consumers include seed portfolios, policy portfolios, route ledgers, store ledgers, garden catalogs, revocation ledgers, sync heads, and mutable torrent-style update heads.
