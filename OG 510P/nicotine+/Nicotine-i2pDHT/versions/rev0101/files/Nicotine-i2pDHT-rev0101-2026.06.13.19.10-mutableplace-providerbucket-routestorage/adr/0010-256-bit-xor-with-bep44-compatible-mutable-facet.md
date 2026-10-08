# ADR 0010 — 256-bit XOR with BEP44-compatible mutable facet

Decision: use SHA-256 / 256-bit XOR keyspace for the native DHT, while exposing
BEP44/BEP46 160-bit mutable targets for compatibility reasoning and test vectors.

Rationale: I2P Destination hashes, modern content hashes, and libp2p-like systems
fit naturally in 256 bits. Mutable torrents remain valuable, so BEP44/BEP46
semantics are preserved at the record level.

Consequence: mutable records have `target_i2p256` and `target_bep44`.
