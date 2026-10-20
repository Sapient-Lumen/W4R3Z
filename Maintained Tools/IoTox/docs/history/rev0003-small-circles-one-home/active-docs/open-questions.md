# IoTox open questions

Accepted decisions live under `docs/decisions/`. This file holds questions that remain
unsettled. A convincing prototype is evidence; it is not automatically a permanent
protocol decision.

## Priority 0: real Tox gate

1. Which exact c-toxcore revision and build recipe should IoTox pin?
2. Should production link toxcore directly, ship a compatible shared library beside
   the binary, or retain only runtime loading? What does each choice mean for packaging,
   licensing, sandboxing, and “just werx” deployment?
3. How should a deterministic local bootstrap/TCP-relay fixture be built?
4. What is the correct typed configuration surface for bootstrap nodes and relays?
5. How does real toxcore behave across savedata restart, relay-only operation, packet
   duplication, network loss, and reconnect?
6. What are the memory, wakeup, idle traffic, and power costs on target-class hardware?

## RecallRoot and owner re-entry

1. Which KDF derives subkeys from the 32-byte RecallRoot, and what exact domain labels
   are permanent?
2. Which application signing primitive should represent the owner root and delegated
   controllers?
3. Should the owner controller Tox secret key be deterministic from RecallRoot, or
   should RecallRoot sign a new replaceable route endpoint during re-entry?
4. How is Tox no-spam state handled so a reconstructed controller remains reachable
   without weakening unsolicited-request protection?
5. How does an owner find device endpoints from memory alone: deterministic owner
   endpoint, owner-operated directory, device rendezvous, stored contacts on devices,
   or a combination?
6. What challenge-response proves owner authority without sending the phrase or root?
7. How are ownership epochs bound to the re-entry transcript?
8. What happens when both the legitimate owner and a phrase thief race to transition
   the root?
9. Which device classes require local physical confirmation or quorum for root changes?
10. How should a future RecallRoot-v2 migrate without silently changing v1?

## Authorization ledger

1. What is the canonical record encoding?
2. How are owner roots, delegated controllers, roles, individual capabilities, expiry,
   and revocation represented?
3. Which capabilities are primitive rather than derived?
4. Can capability grants be delegated, and how is delegation depth bounded?
5. How are ownership and ledger epochs stored with rollback resistance on ordinary
   Linux hardware and on constrained devices?
6. How are concurrent owner or membership changes resolved?
7. How does a device recover from a partially written ledger or full filesystem?
8. What audit evidence is retained, and how are sensitive details excluded?
9. How do route endpoint rotations preserve application authorization?
10. How does a local Unix client receive only the capabilities it needs?

## Command and durable queue semantics

1. Which database or append-only store best fits durable inbox/outbox records?
2. Can a caller-visible timeout ever execute later? The final answer must be explicit.
3. What are the cancellation and shutdown state machines?
4. How are message IDs generated across restart without relying on a correct clock?
5. Which operations are idempotent by definition, conditionally idempotent, or
   explicitly non-idempotent?
6. How long are completed command IDs/results retained?
7. How are queue priority, admission, quotas, and backpressure exposed?
8. What does `RECEIVED` promise about disk durability?
9. How do sleeping controllers receive terminal results later?
10. How are full disk, corrupt records, and rollback handled?

## IoTox protocol

1. Is CBOR the right payload encoding, and which constrained/canonical subset is used?
2. Are current message numbers retained or replaced before protocol major 1 freezes?
3. How are required versus optional features negotiated?
4. How are clocks, relative TTL, boot epochs, and replay windows combined?
5. Which messages receive independent application signatures?
6. What is the maximum acceptable parser work per packet?
7. How are protocol errors rate-limited without hiding diagnostics?
8. How are large state snapshots chunked or transferred?
9. What compatibility promise applies to older appliances?
10. How are malformed authenticated messages distinguished from unauthenticated noise?

## Device identity and physical claim

1. Is there a stable device application key distinct from every Tox endpoint?
2. Is the key software-stored, secure-element-backed, or product-class dependent?
3. What one-time factory material supports initial claim without becoming a permanent
   universal master password?
4. How does the permanent owner phrase interact with physical claim?
5. What is retained across factory reset: hardware attestation, application identity,
   neither, or a product-class choice?
6. What ownership-transfer ceremony supports resale?
7. Which physical reset methods are safe for indoor, outdoor, installed, and portable
   products?
8. How are replacement boards and repaired devices represented?

## Mutorr membership

1. What exact signed membership-epoch record constructs a Cube?
2. Who may advance membership: one owner, threshold owners, namespace administrators,
   or application-specific policy?
3. How are concurrent or partitioned membership changes resolved?
4. Should topology transitions overlap old and new circles to prevent temporary
   partitions?
5. Are storage-only custodians included in the same ring as readers/writers?
6. How are member capabilities and capacity classes represented?
7. Can a namespace have more than one circle or region for locality?
8. How are removed members prevented from receiving future objects?
9. How long may an old member serve previously authorized encrypted data?
10. How are membership records replicated when the data plane itself depends on them?

## Mutorr topology and placement

1. Is four neighbors the right default under realistic sleeping and correlated failure?
2. Should gossip degree adapt to Cube size, online fraction, or device class?
3. Should gossip neighbors and storage custodians be selected independently?
4. Which cryptographic or keyed function replaces the current research mixer?
5. How is identity grinding prevented when membership is federated or loosely governed?
6. Should rendezvous placement support capacity weights, and how can weights avoid
   instability or gaming?
7. How are temporarily offline custodians repaired or substituted?
8. When a member joins or leaves, how quickly should object placement converge?
9. What are acceptable duplicate traffic and convergence targets for 30, 100, and 1,000
   devices?
10. Does a ring remain preferable to random regular graphs, kademlia-like neighbors,
   or owner-defined hubs after simulation?

## Mutable heads and multi-writer state

1. Should `previous` identify the prior content root or the digest of the complete prior
   head?
2. Is generation per writer sufficient, or is an explicit writer epoch needed after
   restore/rotation?
3. How is a signed same-generation fork recorded and surfaced?
4. Can a writer legitimately republish identical content with different metadata?
5. What head fields bind membership epoch and encryption/key epoch?
6. How are missing intermediate heads requested and bounded?
7. How much history must every member or custodian retain?
8. For multi-writer streams, is the first target append-only feeds, an observed-remove
   set, another CRDT, or application-specific merging?
9. How are deleted/tombstoned objects represented?
10. How does an owner repair a namespace after a compromised writer equivocated?

## Immutable objects and confidentiality

1. Is the object ID a hash of plaintext, ciphertext, or a canonical encrypted envelope?
2. Which cryptographic digest and authenticated-encryption implementation are used?
3. Does deterministic encryption leak unacceptable equality information?
4. How are namespace content keys derived, stored, and rotated?
5. How are reader key envelopes encoded and updated?
6. How are chunks and Merkle manifests sized for Tox file transfer and target storage?
7. What metadata remains visible to storage-only custodians?
8. What are quota, eviction, pinning, retention, and garbage-collection rules?
9. How are tombstones and deletion requests propagated to offline devices?
10. What can IoTox honestly promise after a formerly authorized reader kept plaintext?

## Tox file transfer

1. How are application transfer IDs mapped to Tox friend/file numbers across restart?
2. Can transfers resume reliably after reconnect and process restart?
3. How are storage reservations and size limits enforced before acceptance?
4. How are content integrity, authorization, cancellation, and timeout represented?
5. How are concurrent transfers scheduled fairly?
6. How are diagnostic files, OTA artifacts, and Mutorr objects separated by policy?
7. What happens when a source offers the right digest but wrong declared metadata?
8. How are unknown-size streams handled safely?

## Tox/Tor and Tox/I2P

1. Can one Tox instance safely switch route modes, or are separate instances required?
2. How are native UDP, local discovery, DNS, and fallback disabled and verified?
3. Which bootstrap and TCP relay endpoints work within each overlay?
4. Are route-specific Tox identities required for unlinkability?
5. How does RecallRoot reconstruct or authorize those route identities?
6. What latency, resource, and reconnect costs are acceptable?
7. Can an owner run all required infrastructure without IoTox services?
8. How are route failures surfaced rather than hidden behind automatic fallback?
9. Should routes dial in parallel or sequentially?
10. How are peer and object deduplication handled if the same application identity is
    reachable through several Tox endpoints?

## Ratox-style local surface

1. Is Unix `SOCK_SEQPACKET` available on every target, or is a framed stream required?
2. What local schema and subscription model remains small enough to feel Unix-native?
3. Which ratox filenames/FIFO behaviors are worth compatibility?
4. How are FIFO writers given structured results?
5. How are slow local readers prevented from blocking toxcore or exhausting queues?
6. What filesystem permissions and peer-credential checks apply?
7. Can Home Assistant or other bridges remain separate processes?
8. What observability is useful without leaking peer identities, phrases, or data?

## Product scope and side-project posture

1. What is the first actual device class worth controlling safely?
2. Is the first useful deliverable a generic agent, a Tox service toolkit, a home hub,
   or a specific appliance?
3. Which pieces should be contributed upstream versus retained in IoTox?
4. What licensing model is compatible with c-toxcore distribution and the intended
   product?
5. How does every datacube remain buildable and understandable if the project stops?
6. Which claims must be removed if target hardware or network tests fail?
7. What is the smallest ratox successor that would still be worth releasing?
8. What does “decent to bring back” mean in measurable terms: code, server capacity,
   tests, fixes, documents, or a working product slice?
