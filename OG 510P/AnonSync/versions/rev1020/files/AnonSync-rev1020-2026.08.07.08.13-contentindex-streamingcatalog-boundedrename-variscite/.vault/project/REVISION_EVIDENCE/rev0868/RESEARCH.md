# Research notes: AnonSync rev0868

Access date for all online sources: **2026-07-21**.

These sources are design inputs and analogies. None is treated as proof that the
rev0868 C++ model is a production protocol or that a proposed architecture is
secure.

## Explicit blocked and overload states

### QUIC flow control

IETF RFC 9000 models connection and stream flow control explicitly and includes
`DATA_BLOCKED` and `STREAM_DATA_BLOCKED` frames. The relevant lesson is
categorical rather than mechanical: temporary resource unavailability is a
protocol state, not evidence that otherwise valid data is malformed.

- RFC 9000, section 4.1:
  https://datatracker.ietf.org/doc/html/rfc9000#section-4.1

Rev0868 follows that category distinction by separating
`CapacityBlocked` from malformed-envelope exceptions and deterministic evidence
quarantine. It does not implement QUIC flow control.

### HTTP temporary overload and retry metadata

HTTP distinguishes malformed/unacceptable requests from temporary service
unavailability. RFC 9110 defines `Retry-After` and status semantics including
413 and 503. RFC 6585 defines 429 and notes that generating overload responses
can itself consume resources during attack.

- RFC 9110:
  https://datatracker.ietf.org/doc/html/rfc9110
- RFC 6585, section 4:
  https://datatracker.ietf.org/doc/html/rfc6585#section-4

The speculative AnonSync implication is a bounded authenticated pressure
response with coarse retry information. It must be cheap, rate-limited, and
must not require a full rejected envelope to remain resident at the receiver.

## Evidence-retention exhaustion

“Memory-Exhaustion Attack on the Blocklace Byzantine-Repelling CRDT” was
submitted to arXiv on 16 July 2026 and analyzes a memory attack based on fresh
identities and eager retention of Byzantine evidence.

- arXiv:2607.15185:
  https://arxiv.org/abs/2607.15185

This is a very recent preprint, so rev0868 treats it as a warning rather than
settled authority. It reinforces concerns already present in the codebase:
folder-global byte ceilings do not provide fairness, unauthenticated fresh
identities can consume work and storage, and retaining all hostile evidence can
itself become an availability vulnerability.

Potential follow-up mechanisms include authenticated identity scope,
per-principal quotas, bounded unknown-identity work, reserved recovery capacity,
interest-driven evidence acquisition, and compact misconduct proofs. None is
implemented in rev0868.

## Anti-entropy efficiency

“Efficient Synchronization of State-based CRDTs” analyzes redundant full-state
propagation and delta synchronization.

- arXiv:1803.02750:
  https://arxiv.org/abs/1803.02750

“ConflictSync” explores digest-driven set reconciliation and reports transfer
reductions in its evaluated settings.

- arXiv:2505.01144:
  https://arxiv.org/abs/2505.01144

These sources support replacing the simulator's full retained-set replay with a
bounded exact-ID reconciliation layer. They do not justify treating a digest or
summary as authority. AnonSync should use summaries only to locate candidate
missing nodes, then fetch and validate exact canonical operation bytes and
exact parent IDs.

For background on delta-state CRDTs:

- Almeida, Shoker, and Baquero, “Delta State Replicated Data Types,”
  arXiv:1410.2803:
  https://arxiv.org/abs/1410.2803

## Design synthesis

The researched systems point toward four independent verdict dimensions:

1. canonical envelope validity;
2. authenticated trust/admission policy;
3. graph applicability/projection state; and
4. local retention availability.

Rev0868 implements only a reference-model separation between the first, third,
and fourth dimensions. Authenticated trust, durable retry, fairness,
anti-entropy reconciliation, and privacy remain future work.
