# ADR 0011 — Destination/key/work-bound node identity

Decision: preferred node id is derived from I2P Destination hash, DHT Ed25519
public key, and optional work nonce.

Rationale: arbitrary node-id selection makes routing-table pollution and eclipse
attempts cheaper. Binding to reachability and key material is low-regret.

Consequence: this is not strong Sybil resistance, but it gives us deterministic
validation and a place to add admission tiers.
