# Rev0864 online research

Access date: 2026-07-20

This research informs the mission/gap analysis. It is not evidence that AnonSync
already implements the cited properties.

## Replication and transport

- Syncthing Block Exchange Protocol v1:
  https://docs.syncthing.net/specs/bep-v1.html
  
  Useful separation: replicated block/model semantics sit above authenticated
  encryption and reliable transport; the documented stack requires TLS 1.3 or
  higher and certificate-based authentication.

- Noise Protocol Framework:
  https://noiseprotocol.org/
  https://noiseprotocol.org/noise.html
  
  Candidate framework for authenticated encrypted handshakes, identity-hiding
  patterns, and forward secrecy when a threat model justifies a custom channel.

- Tor onion services overview:
  https://community.torproject.org/onion-services/overview/
  
  Relevant when the product definition includes peer-location hiding,
  outgoing-only reachability, onion identity, and rendezvous. Not a substitute
  for application metadata or malicious-peer analysis.

## Key lifecycle

- Messaging Layer Security protocol, RFC 9420:
  https://www.rfc-editor.org/rfc/rfc9420.html
- MLS architecture, RFC 9750:
  https://www.rfc-editor.org/info/rfc9750/
  
  MLS is relevant to asynchronous group key epochs, forward secrecy, and
  post-compromise security, while leaving important application infrastructure
  and privacy tradeoffs to the integrating system.

## Convergence and content addressing

- Verifying Strong Eventual Consistency in Distributed Systems:
  https://arxiv.org/pdf/1707.01747
  https://github.com/trvedata/crdt-isabelle
  
  The work's explicit network model is the key lesson for AnonSync: local merge
  determinism is not a whole-protocol convergence proof.

- Merkle-CRDTs:
  https://arxiv.org/abs/2004.00107
  
  A possible future basis for content-addressed anti-entropy and deduplication,
  but not an automatic answer to access control, deletion, privacy, or bounded
  storage.

## Evidence and provenance

- SLSA build requirements v1.2:
  https://slsa.dev/spec/v1.2/build-requirements
- SLSA provenance model:
  https://slsa.dev/spec/v1.0-rc2/provenance
- in-toto:
  https://in-toto.io/
  
  These support compact, content-addressed, signed build lineage and selective
  byproduct retention instead of cumulative copies of every historical log.

## SQLite callback boundaries

- Busy handler: https://sqlite.org/c3ref/busy_handler.html
- Progress handler: https://sqlite.org/c3ref/progress_handler.html
- Authorizer: https://sqlite.org/c3ref/set_authorizer.html
- Threading modes: https://sqlite.org/threadsafe.html

These APIs have distinct invocation opportunities, lifetimes, and blind spots.
They support AnonSync's typed-owner direction but do not provide hostile-input
process isolation.
