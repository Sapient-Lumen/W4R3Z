# AnonSync rev0895 primary-source research record

Accessed 2026-07-25. This record separates source-backed observations from design speculation.

## Dependency currency

SQLite 3.53.4 was released 2026-07-24 and its release log states that it fixes problems still present in 3.53.0 through 3.53.3. The official archive is `sqlite-amalgamation-3530400.zip`; the published archive SHA3-256 is `628a44cfe82c66aed1ccbbe85a562d2e33ebe64b3288981ed76285612227934e`, and the published `sqlite3.c` SHA3-256 is `67f423e9ebbbdc473cbc4772c872ee6b89f31fde4ed0279a5c25d5f65c043a16`. The archive could not be acquired through this cloudtainer's available network/download paths, so the bundled dependency remains 3.53.3.

- https://sqlite.org/releaselog/3_53_4.html
- https://sqlite.org/download.html

## File synchronization semantics

Syncthing's BEP uses TLS 1.3 or later, certificate-derived device identity in the reference implementation, explicit file metadata and tombstones, versioning, and block exchange. It supports the current authenticated-channel baseline while highlighting missing directory/type/delete/chunk/index product semantics.

- https://docs.syncthing.net/specs/bep-v1.html

## Capability-private partial synchronization

Willow Confidential Sync and Private Interest Overlap treat partial synchronization, capability-authorized read access, private overlap discovery, limits, and transport independence as first-class concerns. This is the strongest reference for a plausible near-term meaning of “Anon”: disclose and replicate only authorized overlap, rather than claiming that encrypted direct transport is anonymous.

- https://willowprotocol.org/specs/confidential-sync/index.html
- https://willowprotocol.org/specs/pio/index.html

## Transport and key-evolution inputs

Noise offers reviewed authenticated key-exchange patterns and some handshake identity hiding, while explicitly not solving IP-address, timing, traffic-shape, or application-payload leakage. MLS contributes epoch, authenticated membership-change, forward-secrecy, and post-compromise-security concepts, but neither framework supplies filesystem causality, effects, reachability, or receipt authority.

- https://noiseprotocol.org/noise.html
- https://www.rfc-editor.org/rfc/rfc9420.html

## Product and provenance framing

Local-first work emphasizes offline capability, user ownership, longevity, privacy, and understandable collaboration; AnonSync is stronger in low-level authority accounting than in operator/user experience. SLSA distinguishes an artifact from external provenance about inputs, builder, and process; in-tree manifests and logs are valuable but are not independent signed attestation.

- https://www.inkandswitch.com/essay/local-first/
- https://slsa.dev/spec/v1.2/build-provenance
- https://slsa.dev/spec/v1.2/distributing-provenance

## Design speculation

A defensible future mission is: a local-first, capability-authorized replication engine that converges exact causal evidence and filesystem effects while minimizing disclosure of identity, interests, and metadata to the least required by each peer relationship. Privacy negotiation should feed immutable capability projections into the authority kernel, not bypass it. Optional endpoint-hiding transports should remain outside that kernel.
