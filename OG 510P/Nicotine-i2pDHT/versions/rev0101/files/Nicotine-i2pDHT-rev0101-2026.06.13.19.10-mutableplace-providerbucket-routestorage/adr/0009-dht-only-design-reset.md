# ADR 0009 — DHT-only design reset

Decision: rev0003 treats the project as a generic DHT over I2P. Future
application consumers are out of scope.

Rationale: the DHT core must get routing, records, validators, mutability,
identity, and testing right before application semantics distort it.

Consequence: package renamed to `i2p_dht_lab`; old app names are retained only in
the artifact lineage.
