# Rev0619 mission and integrity review

## The heart of the mission

The strongest coherent mission visible in this cube is:

> Make an authorization decision reproducible at the execution boundary, bind it to a specific operation contract and identity context, and prevent the same one-time authorization from becoming effective twice—even across process restart and local restore.

That mission has four linked invariants:

1. **Interpretation:** HTTP and event inputs normalize to one unambiguous security context.
2. **Authorization:** a verified issuer, policy, role/scope, tenant, proof key, and operation contract agree on the decision.
3. **One-time effect:** an accepted token or event identity cannot be consumed twice.
4. **Recovery:** backup and restore cannot silently roll the replay state backward or substitute an incompatible ledger profile.

The cube is strongest at invariant 4 and increasingly strong at local invariant 3. It is still mostly a hermetic conformance environment for invariants 1 and 2, not an independently operated enforcement point.

## What went severely wrong

### 1. The SQLite hash chain omitted the contract digest in practice

Rev0618 validated each JWT claim `contract_digest_sha256`, but the SQLite backend populated its persisted row from `tc["contract_digest_sha256"]`. The normalized case did not contain that field. The result was 326 persisted rows with an empty digest in the positive fixture run.

This was severe because the entry hash was calculated over the empty value. The chain could therefore be internally consistent while failing to bind the authorization record to the contract digest it claimed to preserve. The JSONL backend did use verified claims, so the two backends did not implement the same security material.

Rev0619 makes this a format break: SQLite schema v3 and entry material `anonsync-replay-ledger-entry-v2-verified-claims` source both `operation_id` and `contract_digest_sha256` from verified JWT claims. Empty/noncanonical digests and legacy schema-v2 profiles fail closed. The validator decodes every positive fixture JWT and compares all 326 database rows with its verified-claim pair.

### 2. The previous validator tested counters, not the claimed row semantics

The rev0618 validator proved that 326 entries existed and replays were rejected. It never inspected the security fields in those entries. That is why every test could pass while the digest field was empty.

The correction is methodological: every persistence claim now needs a semantic round trip. For each row, validation asks whether the durable representation equals the already verified input, not merely whether a row count or head hash changed.

### 3. Capability version parsing accepted ambiguous suffixes

The parser used `std::stoi` on the suffix, which accepts a numeric prefix. A format such as `anonsync-ledger-backend-capabilities-v1junk` could be interpreted as version 1. Rev0619 requires the entire suffix to be decimal digits and adds a regression test.

### 4. Generated metadata had drifted from the active revision

The host capability report still identified itself as rev0616 inside a rev0618 cube. This did not change execution, but it weakened audit traceability. Rev0619 corrects the emitted revision and validates it.

### 5. Expected restore failures leaked SQLite handles

LeakSanitizer found that the prefix-continuity query attempted to close its SQLite connection while a prepared statement was still alive. `sqlite3_close()` therefore returned `SQLITE_BUSY`; the handle was then lost on the exception path. A command-line selftest hid the operational risk because the process exited immediately, but a long-lived service repeatedly rejecting hostile or rollback snapshots could accumulate handles and memory.

Rev0619 scopes the statement so it is finalized before connection close and retains `sqlite3_close_v2()` cleanup on exceptional exits. The full 15-test suite passes under AddressSanitizer, UndefinedBehaviorSanitizer, and LeakSanitizer after the correction.

## What is missing

### Independent trust

The controls file supplies the JWK, issuer/audience expectations, evaluation time, signed policy, request corpus, failure switches, and expected outcomes. A passing run proves that one bundle is self-consistent. It does not prove that a separately administered gateway trusted the right root or evaluated real traffic at the real time.

The next boundary should be an operator-owned signed configuration whose digest is pinned outside request data. Test-only controls must be structurally impossible to select from a client request.

### Proof-of-possession

The current “proof” compares an input header key identifier with JWT `cnf.kid`. A matching string does not show that the caller possesses the corresponding private key or that a proof was signed for this method, URI, and moment. Use a request-bound signed proof or certificate-bound access token, and replay-protect that proof.

### Event identity replay

JWT `jti` uniqueness does not replace CloudEvents identity. A broker retry or duplicated event may carry a fresh token while preserving the same `(source,id)`. The ledger needs a separately named event identity key and retention policy.

### Authorization-to-side-effect atomicity

Batch mode stages allows and commits at the end of the run. In a production adapter, a crash or commit failure after an external side effect could permit replay because the durable marker never became authoritative. The durable reservation must precede the side effect, with an explicit committed/aborted/reconciliation state machine.

### Authenticated operation contracts

The contract table exposes `operation_contract_root_sha256`, and policy compares against that value, but the loader does not recompute a root over the rows. The root is therefore a self-declared label unless the complete table is authenticated elsewhere. Recompute a deterministic Merkle/root digest or sign the canonical table itself.

### Parser and clock hardening

Case-insensitive duplicate headers can collapse silently. Security timestamps and sequence values pass through JSON numbers represented as `double`. The evaluation clock is fixture-provided. These are all acceptable test conveniences only when they cannot cross into the production adapter.

### External tamper evidence and release provenance

The SQLite chain is unkeyed and local. An actor able to rewrite the database can rewrite entries, metadata, and hashes together. Add externally published signed checkpoints or a separate witness. Also ship an SBOM, binary digest manifest, reproducible build instructions, and signed provenance; a bundled executable alone is not a supply-chain claim.

## Where effort has become wasteful

1. **Restore sophistication is ahead of ingress reality.** Rollback guards, staged replacement, multiple locks, trust-profile pins, and hostile restore corpora are useful, but the project still lacks a deployable request boundary and proof-of-possession. New restore features should pause until the authorization-to-effect path exists.
2. **Two translation units carry too much responsibility.** `reporting_selftests.cpp` and `sqlite_replay_ledger.cpp` contain production helpers, key generation, report rendering, subprocess tests, lock tests, restore tests, and corpus logic. This raises review cost and hides trust transitions.
3. **The “fuzz” executables are deterministic wrappers.** Their names imply coverage-guided fuzzing, but they invoke fixed selftests. Rename them or replace them with actual fuzz harnesses and corpora.
4. **Generated fixtures dominate the retained payload.** The positive and replay files repeat large signed tokens. Keep a small immutable golden corpus, but regenerate bulk cases from concise seeds and record generator provenance rather than treating repeated bytes as product code.
5. **The capability manifest is self-asserted and boolean-heavy.** It is useful as executable configuration validation, but dozens of flags do not create assurance unless the manifest is operator-authenticated and mapped to tests. Prefer a smaller versioned profile plus machine-linked evidence.
6. **No-op revision scripts and stale audits create false motion.** Rev0619 removes the no-op applier and regenerates only current audit evidence.
7. **A directory-name/file-count definition of “slim” is gameable.** Measure source concentration, generated-byte ratio, build reproducibility, test-to-claim linkage, and operator configuration surface instead.

## Recommended build order

1. **Operator root and real adapter:** separate immutable operator configuration from request data; expose one narrow decision/reservation API.
2. **Possession and identity:** DPoP or mTLS binding, CloudEvents `(source,id)` replay keys, duplicate-header rejection, and trusted runtime time.
3. **Durable effect protocol:** reserve before side effect; finalize/abort/reconcile with idempotent downstream calls.
4. **Contract authenticity:** canonical table digest/root recomputation and key-domain separation.
5. **External evidence:** signed checkpoints/witness, SBOM/provenance, real fuzzing, and descriptor-relative filesystem hardening.
6. **Then deepen restore:** only in response to a deployment threat model and recovery objective.

## Speculation, clearly labeled

The name **AnonSync** suggests anonymity and synchronization, but the present cube implements neither an anonymity system nor a multi-node synchronization protocol. It may be that the deeper intended mission is to coordinate sensitive actions without allowing identity ambiguity or replay. If so, the best product shape is likely a small, independently trusted authorization-and-idempotency service used by gateways and brokers—not a monolithic gateway, archive, or bespoke transparency system.

The “cloudtainer” may also be serving as an evolutionary proof laboratory: each revision freezes one security property and carries it forward. That approach can work, but only when every claimed property is tested at its semantic boundary. Rev0618’s empty digest demonstrates why counters and self-consistent fixtures are not enough.

## Standards alignment used for this review

The next design should align with the proof-binding model in OAuth DPoP (RFC 9449) or OAuth mutual-TLS client authentication (RFC 8705), JWT deployment guidance in RFC 8725, canonical JSON guidance in RFC 8785, CloudEvents identity semantics for `source` plus `id`, TUF-style rollback/freeze thinking for trusted metadata, DSSE’s length-delimited pre-authentication encoding rationale, SQLite’s documented transaction/backup behavior, Linux descriptor-relative path resolution where available, and SLSA provenance concepts.
