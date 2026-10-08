
# Research notes — mutable heads and distributed control planes

These notes are intentionally selective and speculative.

- **BEP44** is still the core small-head teacher: Ed25519 public key, optional salt, sequence number, signature, value-size limit, CAS, expiration/republish semantics. Its limitation is also useful: a 1000-byte mutable value pushes us toward pointers and manifests, not fat records.
- **BEP46** generalizes beautifully: a mutable slot can point to the current torrent infohash. That pattern can become release channels, sync snapshots, search shard roots, or seed portfolios.
- **IPNS** is another pointer-shaped teacher: cryptographically verifiable mutable names point at content-addressed data and carry sequence/TTL/validity semantics.
- **Willow** argues that mutable, structured, local-first data deserves first-class treatment rather than being treated as an embarrassment beside content addressing.
- **Tahoe-LAFS** is the garden-storage teacher: untrusted storage servers can hold shares and mutable structures while capabilities/signatures/encryption preserve authority elsewhere.
- **Hypercore and SSB** are feed teachers: signed append-only logs make multiwriter sync easier when each writer owns a feed, and mutable heads point to feed tips.
- **CONIKS/Sigsum-style transparency** suggests a way to think about mutable-head witnessing: detection and evidence, not magical prevention.
- **UCAN/object capability systems** are a likely future input for delegated writers, garden work grants, bridge permissions, and revocation heads.
- **IPFS provider reprovide/sweep work** keeps reminding us that refresh scheduling is not a boring implementation detail. It is a scaling property.

Open guess: the I2P DHT should have a small number of primitive record kinds, but a very rich vocabulary of signed mutable heads above them.
