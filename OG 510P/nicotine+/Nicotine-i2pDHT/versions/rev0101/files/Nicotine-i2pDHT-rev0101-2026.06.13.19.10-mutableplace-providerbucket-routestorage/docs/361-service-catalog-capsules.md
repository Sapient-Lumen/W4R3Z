# Service catalog capsules

A start profile says `leaf`, `garden`, `bridge`, or `offline_design`; a service catalog says what a giving node is actually offering this epoch. rev0036 makes that a signed local capsule.

The catalog binds:

- issuer node id and DHT public key,
- sequence and validity window,
- accepted start-profile digest,
- accepted start-matrix report digest,
- accepted router-harness report/profile digest,
- service descriptors such as `seed_gate`, `head_watch`, `witness_query`, `region_reprovide`, `bulk_provider`, `wake_courier`, `bridge_gateway`, and `diagnostic_mirror`.

A catalog can fail even when signed. It is quarantined for replay, sequence rollback, same-sequence fork, binding drift, bad signature, future/expired time windows, bridge drift, or non-power capacity overclaim.

Design guess: garden nodes should be allowed to be powerful, but their power must be described as current service capacity, not as truth authority.
