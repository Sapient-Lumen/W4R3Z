# rev0101 — mutableplace-providerbucket-routestorage

rev0101 continues the post-native-return substrate work from rev0100. The new seam is local placement: after Python-owned record ingress, provider semantic proof, and I2P routing-anchor acceptance, the DHT still must decide whether an observation may enter local mutable-head memory, provider-index buckets, or routing-table storage.

Strong rule: an accepted DHT record is not local state until placement, bucket admission, or route storage preserves the relevant hard-negative memory at the exact boundary.

New surfaces:

- `mutableplacement`: places signed mutable-head observations without claiming latestness.
- `providerbucket`: admits semantic provider claims into bounded provider-index buckets without storing content or claiming truth.
- `routestorage`: stores I2P-bound contacts or replacement-cache entries without letting gardens or introducers become authority.
- `substrateplacementfold`: pins the rev0101 path and rev0100 predecessor.

Nonclaims remain: no live I2P/SAM transport, no production DHT, no production mutable-latest consensus, no production provider-index protocol, no production route-table protocol, no global reputation, no private retrieval guarantee, no Sybil/anonymity guarantee, and no Nicotine+ patch.
