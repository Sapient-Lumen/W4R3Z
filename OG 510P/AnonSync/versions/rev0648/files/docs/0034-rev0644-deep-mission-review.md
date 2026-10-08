# rev0644 deep mission review

## The heart of the mission

The cube's durable core is not “anonymous sync.” It is a **reproducible authorization-to-effect boundary**:

> Given one transport-authenticated actor, one exact semantic operation, one authenticated policy/contract snapshot, and one operator-selected execution profile, decide whether an effect may begin, reserve that effect once, and preserve evidence sufficient to recover without duplicating or fabricating the outcome.

That mission has four inseparable properties:

1. **Interpretation:** distinct wire encodings must not become accidentally equivalent, and one signed meaning must not decode into two operations.
2. **Authorization:** identity, token, contract, policy, time, and operator configuration must come from the correct trust domains and be bound into the decision.
3. **One-time effect:** retries, redelivery, crashes, and restore must converge on one semantic reservation/effect identity.
4. **Recovery:** prepared, claimed, applied, rejected, and unknown outcomes must remain distinguishable after interruption.

The code already contains substantial machinery for those properties: normalized OpenAPI/AsyncAPI cases, claim and contract binding, JWT/event replay identities, effect idempotency, SQLite ledger chains, an outbox, leases, signed terminal transitions, snapshot/restore verification, and a service-shaped ingress path. The mission becomes clearer when those are treated as one state machine rather than a collection of revision features.

## What had gone severely wrong

### 1. “Authenticated” identity was caller-authored

Through rev0643, `authenticated_context` lived inside caller-controlled JSON. The sender signed its own assertion of principal and authenticator. That can prove key possession, but not that a trusted transport authenticated the asserted identity. This was the most serious active boundary error because the labels and reports suggested a guarantee the architecture did not provide.

Rev0644 separates the typed context and rejects body-side identity injection. The remaining obligation is deployment: only a listener, mTLS terminator, DPoP verifier, or securely authenticated proxy adapter may construct that context.

### 2. The public library API allowed policy construction

The old public config object exposed mutable security fields. A library caller could disable sender verification or substitute trust material. Rev0644 exposes only a path-plus-digest operator handle and reloads policy internally.

### 3. A valid nonce can be consumed without a reservation

The replay cache commits before profile authorization and ledger append, in a different SQLite file. A later failure burns the nonce; retry then fails, while no durable authorization/effect reservation exists. This is both an availability problem and an evidence mismatch. The report is now honest, but the architecture remains P0.

SQLite documents that WAL-mode transactions spanning attached database files remain atomic only within each individual file during a crash. A separate-cache design therefore cannot be promoted into a cross-file exactly-once claim by adding checks. The proof identity and reservation/outbox must share one authoritative transaction or an explicit recoverable protocol.

### 4. Undefined behavior existed in a shared decoder

The Base64url decoder shifted a signed `int` across arbitrarily long input. That can overflow and invoke undefined behavior. Because this primitive serves signature/JWK paths, it was broader than the ingress endpoint. Rev0644 uses unsigned arithmetic and adds a long-input regression.

### 5. Historical validation sometimes proved self-consistency, not meaning

Rev0618 persisted an empty `contract_digest_sha256` in 326 accepted rows while its chain and tests passed. The validator counted rows and checked replay/head behavior; it did not compare durable fields to verified claims. Rev0619 corrected it.

Rev0631 also left newline-concatenated security tuples ambiguous; rev0632 reproduced a deterministic semantic collision and migrated key material to length-prefix framing. These are the same methodological failure: a hash, signature, counter, or format label is not evidence unless the encoded semantic mapping is adversarially one-to-one and round-tripped.

### 6. Claims outran retention semantics

The prior nonce wording implied uniqueness without a horizon, but replay rows are pruned by issued time. Rev0644 calls the guarantee retained-window scoped. A complete policy still needs retention, rotation, conflict, and distributed ownership semantics.

### 7. Durability settings and permission changes were requested but not always proven

The replay cache asked SQLite for WAL/FULL behavior without checking returned state, and workspace permission errors were ignored. Rev0644 verifies WAL and `synchronous=FULL`, applies a bounded busy timeout and SQLite limits, and fails closed if private permissions cannot be established.

## What is missing

### A. A real authentication ingress

The typed context is necessary but not sufficient. A deployed boundary needs one of:

- mTLS client authentication/certificate-bound tokens, with secure handling when TLS terminates at a proxy;
- DPoP-style application proof binding to method, target URI, creation time, unique proof id, key, and—where relevant—access-token hash;
- another equivalently explicit authenticated transport with principal derivation and revocation/rotation rules.

The current proof does not bind an HTTP method or target URI and the CLI context file is not authentication. RFC 9449 also emphasizes that a valid DPoP proof alone is not an authorization decision.

### B. One authoritative ingress transaction/state machine

All non-mutating parsing, cryptographic verification, profile loading, policy evaluation, and contract resolution should happen before mutation. Then one transaction should atomically record:

- proof/request identity and replay disposition;
- authenticated principal and verifier provenance;
- exact policy/contract/config digests;
- authorization outcome;
- semantic effect-idempotency key;
- reservation and outbox row, if allowed;
- a terminal rejected state when policy intentionally consumes a one-time proof.

The API then returns a stable decision/reservation id. Retries query that state rather than re-running ambiguous partial work.

### C. A real downstream adapter and unknown-outcome protocol

The local SQLite downstream journal is a useful deterministic harness, not delivery proof. One production adapter should be implemented end to end with:

- downstream-native idempotency key;
- timeout/unknown result state;
- authoritative reconciliation query;
- retry budget/backoff;
- crash injection before send, after send, after downstream commit, and before local terminal transition;
- operator-owned adapter identity and credentials.

### D. Authenticated operator control plane

Digest-pinned local JSON catches accidental mutation only when the expected digest is already trusted. The cube still needs signed, versioned, rollback-resistant bundles for profiles, contracts, capabilities, trust roots, key rotations, retention policy, and adapter configuration. Key domains should be separated for tokens, policy, transitions, snapshots, releases, relay, and downstream authentication.

### E. Cross-language canonical protocol

The parser is safer, but the in-memory numeric model remains binary64 and canonical JSON is a custom implementation. Adopt an explicit I-JSON/JCS-compatible wire and signing profile, publish cross-language golden vectors, reject duplicate members at the generic parser boundary, and remove remaining legacy newline materials through versioned migration.

### F. Distributed replay and retention policy

Local uniqueness does not define behavior across replicas, cache loss, failover, backup, restore, or window expiry. The design needs a single owner or consensus-backed replay authority, explicit TTL/horizon, cache migration protocol, conflict semantics, and a statement of what happens when an old proof is presented after pruning.

### G. Independent evidence and software provenance

A local hash chain and self-authored manifest can be rewritten together. Publish signed checkpoints to an independently administered witness. Build artifacts should have reproducible or hermetic build instructions, SBOM, signed provenance bound to artifact digests, and verification policy. SLSA's model is useful here because it asks who built an artifact, by what process, and from which inputs.

### H. Real fuzzing and resource governance

Targets named `anonsync_fuzz_*` currently run fixed deterministic cases. True coverage-guided fuzzing should expose in-process entry points, seed corpora, sanitizer builds, and persistent crash artifacts. LLVM describes libFuzzer as coverage-guided and evolutionary, mutating a corpus to maximize reached code; the current launchers do not meet that description.

Add depth, member-count, string, decoded-key, database-growth, per-principal quota, and request-rate limits in addition to current byte ceilings.

### I. Privacy model

The name suggests anonymity, but the active system stores principals, token/event identities, operation ids, hashes, timestamps, and durable evidence. Define whether privacy is actually a goal. If it is, specify data minimization, pseudonymization, retention/deletion, witness disclosure, tenant isolation, and operator access. Otherwise rename the product around authorization/idempotency evidence to avoid a misleading promise.

## Waste and review drag that should be corrected

1. **Historical binaries:** eleven old executables consumed about 18 MiB uncompressed while historical audits were only a few hundred KiB. Rev0644 keeps one current binary and retains source/evidence.
2. **Monolithic files:** `reporting_selftests.cpp`, `sqlite_replay_ledger.cpp`, and `runner.cpp` concentrate unrelated trust domains. Split production ingress, replay store, report schema, restore, relay, and tests into review-sized modules.
3. **Boolean-manifest accretion:** capability manifests contain hundreds of flags. Replace clusters with versioned schemas plus a small set of externally meaningful guarantees and explicit negative claims.
4. **Revision strings everywhere:** duplicated format/revision literals drifted historically. Generate one active-version header/schema and validate lineage from a single source.
5. **“Fuzz” naming without fuzzing:** rename deterministic launchers to boundary/corpus selftests until coverage-guided engines exist.
6. **Fixture repetition:** preserve a small immutable golden corpus and generate bulk cases from compact seeds with generator provenance.
7. **Evidence-before-interface sequencing:** substantial restore, snapshot, and terminal-transition sophistication accumulated before the external identity boundary was trustworthy. Future revisions should follow attack paths from ingress through effect before adding more forensic surface.
8. **Report duplication:** hand-built JSON report strings in large functions are brittle. Use typed report models plus one serializer/schema and round-trip tests.

## Ordered roadmap

### P0

1. Merge proof replay, authorization outcome, effect reservation, and outbox into one authoritative transaction/state machine; preserve a regression for the rev0644 nonce-burn exploit.
2. Build one actual listener/authenticator adapter that alone constructs `IngressTransportContext`; bind proof to concrete HTTP/event transport semantics.
3. Implement one real downstream adapter with idempotency and unknown-outcome reconciliation.
4. Move profiles/contracts/capabilities into a signed operator bundle with rollback/rotation rules.

### P1

1. Standardize canonical signed JSON and cross-language vectors.
2. Define distributed replay ownership, retention, backup/restore, and expiry semantics.
3. Add quotas, depth/count/decoded-size limits, observability, and privacy/retention policy.
4. Publish independently witnessed ledger checkpoints.

### P2

1. Split the monolith and typed reports; reduce the capability matrix.
2. Add coverage-guided sanitizer fuzzing and persistent corpora.
3. Produce SBOM and signed build provenance; automate fresh-extraction/source rebuild verification.
4. Rename/reposition the project around its actual product promise.

## Speculation, clearly labeled

- **Likely product shape:** this wants to become a small sidecar/library that sits immediately before irreversible work, not a general synchronization platform.
- **Likely development incentive:** the cube optimized for accumulating evidence artifacts because those are easy to freeze per revision; the harder deployment boundary remained simulated. That explains sophisticated local recovery beside a caller-authored “authenticated” context.
- **Best use of the cloudtainer:** an evolutionary security laboratory where each revision contains one exploit, one invariant, one regression, and one smaller active artifact. It becomes counterproductive when history, binaries, and Boolean claims overshadow the active attack path.
- **Renaming hypothesis:** “AnonSync” is probably historical. “Authorization Reservation Kernel,” “Effect Gate,” or “Decision Ledger” would describe the current mission more honestly unless an explicit anonymity/privacy design is added.

## External reference points

- OAuth DPoP, RFC 9449: https://www.rfc-editor.org/info/rfc9449
- OAuth mutual TLS, RFC 8705: https://www.rfc-editor.org/info/rfc8705
- OAuth 2.0 Security BCP, RFC 9700: https://www.rfc-editor.org/info/rfc9700
- JSON, I-JSON, and JCS: https://www.rfc-editor.org/info/rfc8259 ; https://www.rfc-editor.org/info/rfc7493 ; https://www.rfc-editor.org/info/rfc8785
- SQLite open flags: https://sqlite.org/c3ref/open.html
- SQLite attached-database transaction limits: https://sqlite.org/lang_attach.html
- SQLite synchronous/WAL behavior: https://sqlite.org/pragma.html
- Transactional outbox pattern: https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html
- LLVM libFuzzer: https://llvm.org/docs/LibFuzzer.html
- SLSA build provenance/levels: https://slsa.dev/spec/v1.2/build-requirements ; https://slsa.dev/spec/v1.1/levels
