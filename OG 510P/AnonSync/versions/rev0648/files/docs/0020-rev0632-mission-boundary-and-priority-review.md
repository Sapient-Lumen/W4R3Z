# Rev0632 mission, boundary, and priority review

## Executive finding

The heart of AnonSync is not backup, reporting, anonymity, or synchronization. The strongest mission supported by the code is:

> Make an authorization decision reproducible at the execution boundary, bind it to a specific operation contract and identity context, durably reserve the resulting effect, and prevent the same one-time authority from becoming effective twice across retry, restart, and local restore.

The cube contains useful pieces of that mission: deterministic normalization, JWT and signed-policy checks, operation-contract matching, replay reservations, SQLite/WAL persistence, local backup/restore verification, and terminal-effect evidence. Yet it is strongest in the place furthest from actual execution: local recovery. It remains a hermetic corpus runner in which one controls file supplies the trust root, policy, evaluation clock, proof secret, requests, and expected answers. There is no deployed gateway/broker adapter and no downstream worker that turns an authorization reservation into an externally observed effect.

Rev0632 therefore changes priority. Rather than adding another restore or transition feature, it closes a reproduced ingress ambiguity that invalidated the advertised proof/effect binding, corrects a backend asymmetry, removes a predictable entropy fallback, and makes the remaining boundary explicit.

## Mission invariants

A future production system should preserve five linked invariants:

1. **Interpretation.** HTTP and event inputs map to one unambiguous typed security context. Duplicate metadata, encoding alternatives, parser loss, and cross-field concatenation cannot change meaning.
2. **Authorization.** A separately administered trust configuration, verified sender identity/possession, policy, tenant, operation contract, and runtime clock agree on a decision.
3. **Reservation.** Before external work begins, a durable, unique effect reservation exists for the semantic operation—not merely for a test case or token string.
4. **Execution.** Exactly one idempotent worker owns the reservation and records terminal state from downstream truth. A positive decision alone is not evidence that an effect happened.
5. **Recovery and audit.** Restart and restore preserve reservations and terminal states without rollback or substitution, and externally anchored evidence makes wholesale local rewriting detectable.

The current cube is relatively mature at local invariant 5, has useful local mechanics for invariant 3, tests portions of invariants 1 and 2, and does not implement invariant 4.

## Severe failure reproduced in the incoming revision

### Newline-delimited proof material was not injective

Rev0631 formed proof-binding material from labeled lines. A field value could itself contain a newline and another field label. These two distinct CloudEvents identities produced the same legacy byte string when all other fields were equal:

- Envelope A: `source = "A\ncloud_event_id=B"`, `id = "C"`
- Envelope B: `source = "A"`, `id = "B\ncloud_event_id=C"`

Both serialize to the same relevant suffix:

```text
cloud_event_source=A
cloud_event_id=B
cloud_event_id=C
```

The validator reproduced one shared legacy HMAC-SHA256 digest:

```text
8fedb159920d09f7909364e17ee53c48653493f60b4969fbbcba332779eb6ec8
```

The incoming binary accepted each distinct envelope in a fresh ledger when supplied that same digest. This breaks the semantic claim that the proof digest binds the caller to one exact event identity. It is not merely a theoretical hash collision; it is deterministic ambiguity in the preimage construction.

The same pair also collided in legacy effect-idempotency material. A separate raw identity construction, `source + "\n" + id`, collapsed these pairs:

- `source = "A\nB"`, `id = "C"`
- `source = "A"`, `id = "B\nC"`

That second collision can misclassify distinct events as duplicates, suppressing one event or aliasing local replay state.

### Why this matters even though the cube is not deployed

The packaged HMAC is fixture evidence rather than a production proof-of-possession protocol, so the finding is not evidence of a breached live service. It is still severe within the cube’s own claims:

- a proof created for one semantic event can validate another crafted event;
- two distinct effects can share one reservation identifier;
- two distinct events can share one replay identity;
- counters and an internally consistent ledger can still look correct;
- the risk was already documented, demonstrating a prioritization failure rather than an unknown primitive.

The likely operational effects would range from proof substitution to false duplicate suppression, reservation confusion, and incorrect audit attribution, depending on where a valid digest became observable and how downstream work used the effect key.

### The warning existed six revisions earlier

The rev0619 risk register explicitly said to replace custom newline signing inputs with a canonical, length-delimited construction. Revisions rev0626 through rev0631 then invested in terminal transition chains, pending recovery reports, prepared-row binding, signed transition intents, raw-API closure, and ledger-instance binding while leaving this ingress ambiguity intact.

Those later changes were not intrinsically useless. The waste was sequencing: deep recovery evidence was added on top of an identity/proof construction that did not uniquely identify the operation being recovered.

## What rev0632 changes

### Unambiguous typed framing

The new helper `anonsync-length-prefixed-tuple-v1` frames every component by decimal byte length:

```text
fixed-prefix || LEN(domain) ":" domain ||
LEN(field-name) ":" field-name || LEN(field-value) ":" field-value || ...
```

The domain and every field name are included, so the same values in a different protocol or field order do not share material. Lengths are byte lengths, allowing arbitrary UTF-8 bytes without relying on a separator that may occur inside a value.

Rev0632 applies separate domains to:

- `anonsync-proof-binding-v2`
- `anonsync-effect-idempotency-v2`
- `anonsync-cloud-event-identity-v2`
- `anonsync-effect-idempotency-legacy-v1` for pre-normalized compatibility callers
- `anonsync-sqlite-ledger-instance-v2` for new ledger identity derivation

This construction is inspired by the reason DSSE uses pre-authentication encoding: multiple signed fields need an unambiguous byte representation. It is not a claim that the custom tuple format is DSSE or that it has received equivalent review.

### Fail-closed metadata normalization

- The JSON parser already rejected exact duplicate object keys.
- Normalization now rejects case-insensitive duplicates such as `Authorization` and `authorization` instead of silently retaining one.
- ASCII C0 controls and DEL are rejected in security metadata keys/values, HTTP method/path, event channel/action, and CloudEvents source/id.
- The exact collision envelopes are quarantined before proof acceptance or ledger append on both JSONL and SQLite/WAL.

Framing is the cryptographic fix. Control rejection is defense in depth and keeps transport metadata within a safer textual subset.

### Backend symmetry restored

The first implementation pass exposed another drift: JSONL’s pre-normalized effect-key fallback used framed legacy-v1 material, while SQLite still used legacy newline composition. Rev0632 makes both derive the same key and adds a shared backend selftest. Security semantics should not depend on the persistence implementation.

### Ledger identity initialization fails closed

The incoming SQLite path attempted `/dev/urandom` but silently fell back to a digest of PID, current second, and path if entropy reads failed. That fallback could create predictable or repeated ledger identities in constrained or faulted environments. New identities now use OpenSSL `RAND_bytes`; initialization throws if the CSPRNG fails. The path and random bytes are then length-framed and hashed under the v2 ledger-instance domain.

This still does not distinguish byte-for-byte clones: a clone carries the already stored identity. The protection is against using an intent on a differently initialized ledger, not against copied storage with identical state.

### Claims and lineage made more honest

The incoming C++ README described rev0629, not rev0631. Its active capability manifest claimed parent `rev0629`, while the package manifest claimed rev0631 descended from rev0630. Its purpose said a signed intent could not close work on a “cloned ledger,” although another field correctly admitted that byte-for-byte clone replay remained possible.

Rev0632 updates the documentation, uses parent `rev0631`, and consistently states the clone limitation. Capability v27 also says what it does not cover: other legacy newline materials, deployed enforcement, proof-of-possession, downstream delivery, independent witnessing, and authenticated provenance.

## A prior severe failure shows the recurring pattern

Rev0619 documented that rev0618’s SQLite path persisted an empty `contract_digest_sha256` in 326 positive rows while all tests passed. The chain faithfully hashed the empty value, so it was internally consistent but did not bind the decision to the contract it purported to preserve. The validator had checked counts and replay behavior, not row semantics.

Rev0632’s collision is the same class of methodological failure at a different layer: the system verified a digest and reported counters without proving that the digest construction was one-to-one over valid semantic inputs.

The corrective testing principle should be permanent:

> Every security binding needs adversarial semantic round trips, not only happy-path signatures, row counts, format strings, or chain-head changes.

For serialization, that means collision pairs, duplicate keys, alternate encodings, type confusion, boundary lengths, malformed Unicode, and cross-backend equivalence. For persistence, it means independently decoding the trusted input and comparing each durable security field. For restore, it means checking source identity and state before, during, and after copying.

## What is still missing

### 1. A real execution boundary

The public `run()` path processes a caller-selected controls bundle and fixture stream, stages decisions, commits a report, and exits. It is not a narrow per-request service API integrated into a reverse proxy, API gateway, service mesh, broker consumer, or effect worker.

The next code-bearing milestone should expose a small production interface with an operator-selected immutable configuration and a durable reservation transaction. The adapter—not the request—must choose policy, trust, clock, contract set, and ledger.

### 2. Authorization-to-effect atomicity

Batch mode can stage positive decisions and commit at the end. That is acceptable for a hermetic report. It is unsafe as a production pattern if external work occurs before the reservation is durable. A crash could leave a real effect with no authoritative replay marker.

Use a transactional outbox or equivalent protocol:

1. normalize and authorize;
2. atomically create `PREPARED` reservation;
3. return/queue the reservation identifier;
4. have one worker perform an idempotent downstream operation;
5. reconcile `APPLIED`, `FAILED`, or `COMPENSATED` from downstream truth;
6. recover abandoned reservations by querying that same truth.

The existing transition chain can become evidence for this protocol, but it is not the protocol by itself.

### 3. Independent operator trust and real time

The controls file contains the JWK, issuer/audience expectations, fixture evaluation time, signed policy, proof HMAC secret, request corpus, expected outcomes, and failure switches. A passing run proves bundle self-consistency. It does not prove that an independent operator trusted the correct root at the correct real time.

Trust roots and accepted profiles must be authenticated and selected outside request data. The production path needs a trusted clock, rotation/revocation behavior, and distinct keys for token verification, policy signing, transition authorization, snapshot signing, and release provenance.

### 4. Sender proof-of-possession

A shared fixture HMAC demonstrates object binding only inside the test bundle. It does not show that a caller possesses a private key. DPoP is an application-level sender-constraining mechanism that binds signed proofs to HTTP requests and detects token replay; OAuth mTLS can bind access tokens to a client certificate. One of those models—or a carefully profiled equivalent—should replace the fixture proof before any external claim.

### 5. Authenticated operation contracts

The operation table includes a root/digest label and the runner compares it with local policy, but the trust relationship remains inside one bundle. The loader should deterministically recompute the table digest/root and verify it against separately signed release metadata. The contract table should be immutable for a configuration generation and its digest should travel into every reservation and effect record.

### 6. Complete serialization migration

Rev0632 intentionally does not silently rewrite historical ledger formats. Remaining custom newline-delimited inputs include at least:

- JSONL/SQLite replay entry hash material;
- effect-transition hash material;
- effect-transition intent signing input;
- snapshot-manifest signing input.

Some fields are currently constrained enough to reduce easy ambiguity; that is not a substitute for an explicit typed encoding. A migration needs new material/schema versions, old-ledger read policy, conversion tooling, adversarial tests, and a rule against adding new custom concatenations.

For structured JSON that is signed as JSON, use a documented canonicalization profile such as JCS where applicable. JCS constrains data to I-JSON and defines deterministic serialization, including property sorting and number/string rules. The cube’s `canonical_json()` helper is local and should not be described as JCS-compatible without conformance tests.

### 7. Exact parsing and resource limits

Security timestamps, sequences, and counters are parsed into `double` and later cast to `long long`. Fractional values can truncate; large values can lose precision or cross conversion limits. Store the original number representation or use a parser with checked integer types, then reject non-integral and out-of-range values.

The parser has a nesting limit, but the production boundary also needs explicit limits for total bytes, string length, object members, arrays, JWT size, body/event payload, metadata count, manifest size, and database/snapshot size. TUF’s threat model explicitly includes “endless data” attacks; local validation should have similarly concrete ceilings.

CloudEvents specifies that `source + id` identifies a distinct event, that `id` is nonempty, and that `source` is a nonempty URI-reference. The cube enforces local nonempty identity at append time and now rejects controls, but it does not fully validate the URI-reference semantics.

### 8. External tamper evidence

A local unkeyed hash chain detects accidental corruption and constrained row edits. An actor able to replace the database and its metadata can recompute the entire chain. Publish periodic signed checkpoints to an independently administered witness, transparency service, or operator-controlled append-only store. Define how clients detect rollback, split view, and stale checkpoints.

### 9. Release provenance

The package contains source, a binary, a capability manifest, and self-authored audit JSON. That is useful working evidence but not authenticated provenance. SLSA describes provenance as verifiable information about where, when, and how an artifact was produced, and notes that provenance only helps when a verifier checks it against expectations.

A release path should include source revision identity, hermetic/reproducible build instructions, dependency identities, SBOM, artifact digests, builder identity, signed provenance, and a verification policy rooted outside the package. Existing historical audits often point to absolute logs that are not packaged; current revisions should carry the relevant logs or make every check reproducible.

## Where effort is wasteful or misallocated

### Restore depth is ahead of ingress and execution

The cube has rollback guards, signed manifests, trust-profile pins, staged replacement, locks, write gates, prefix checks, hostile snapshot corpora, pending-effect reports, signed terminal intents, and per-ledger identity. These are thoughtful local controls. Their marginal value is low until there is a real request adapter, sender possession, durable pre-effect reservation, and downstream worker.

Future restore work should be justified by a deployment recovery objective rather than revision momentum.

### Two files dominate review

After rev0632, the nine production `.cpp` files contain about 9,052 lines. `reporting_selftests.cpp` and `sqlite_replay_ledger.cpp` contain about 6,523—roughly 72%. They mix production code, test-only key generation, report rendering, process orchestration, filesystem fault injection, SQLite schemas, restore logic, and corpora. This concentration makes trust boundaries hard to audit and increases the chance of backend drift like the fallback mismatch found this turn.

Split production persistence, snapshot verification, transition intents, and test helpers into narrowly owned units. Keep cryptographic material constructors centralized and versioned.

### “Fuzz” is a misleading label

The three files under `fuzz/` total six lines and call deterministic selftests. They do not expose `LLVMFuzzerTestOneInput`, preserve a corpus, measure coverage, or mutate inputs. Rename them to boundary selftest launchers or replace them with real coverage-guided targets. Mislabeling reduces confidence because it suggests assurance that does not exist.

### Generated bytes dominate attention

The fixture cases, replay corpus, and contract table are more than two megabytes before counting the packaged binary. Large repeated tokens and generated rows make diff review harder while adding little new semantic coverage. Preserve a small immutable golden set, generate the bulk corpus from concise seeds, and package generator source plus provenance.

### Boolean capabilities are evidence proxies

The manifest contains many booleans describing what code “requires.” The runner checks them, but the package authors also write the manifest. A flag can gate execution; it cannot independently prove implementation. Reduce this to a smaller authenticated profile and generate a claim-to-test map that names the exact executable test, adversarial vector, result, and artifact digest.

### Revision accretion can create false motion

Many source comments, test stems, fixture paths, and audit files preserve old revision numbers. Some history is useful, but stale labels and inaccessible log paths weaken traceability. The incoming package itself demonstrated this with a rev0629 C++ README and inconsistent parent lineage. A revision should update active metadata in one generated step and preserve history only where it supports compatibility or a live regression.

## Recommended build order

### Phase 1 — production boundary

- Define one typed request/event context and one `authorize_and_reserve` API.
- Load an operator-authenticated immutable configuration by generation/digest.
- Commit reservation before returning a positive external decision.
- Integrate one real adapter and one idempotent fake/controlled downstream service.
- Add crash tests at every boundary between reserve, dispatch, downstream response, and terminal record.

### Phase 2 — possession and trust

- Implement DPoP or mTLS token binding, including proof replay and proxy rules.
- Use trusted runtime time, key separation, rotation, and revocation.
- Recompute and authenticate operation contracts.
- Define replay/effect retention and multi-worker ownership.

### Phase 3 — migrate and witness

- Version all remaining signed/hash material with typed encoding.
- Add checked integers and resource limits.
- Publish signed checkpoints to an independent witness.
- Add real fuzzing and hostile cross-implementation serialization tests.

### Phase 4 — supply chain and recovery objectives

- Produce SBOM and signed provenance, with an external verification policy.
- Measure and document recovery point/recovery time objectives.
- Add restore features only when required by those objectives and the deployed storage architecture.

## Speculation, clearly labeled

### Likely product shape

The code suggests the eventual product should be a small authorization-and-idempotency sidecar or service placed between a gateway/broker and effect workers. It should not become a monolithic gateway or a bespoke transparency platform. Its differentiating value would be a durable, operation-bound authorization reservation that survives retries and supports auditable reconciliation.

### Likely process failure

The revision cadence appears to reward locally provable additions: another version, flag, report, lock, or restore test can be completed entirely inside the cube. The hardest work—operator ownership, deployment integration, sender possession, and downstream reconciliation—requires an external boundary and therefore remained postponed. That incentive can produce an “evidence-rich, boundary-poor” system.

The solution is not to stop evidence work. It is to make every new revision attach to one end-to-end threat path and refuse local sophistication that does not strengthen that path.

### Name and mission drift

“AnonSync” suggests anonymity and multi-node synchronization, but the retained code implements neither. The name may be historical, or the original mission may have been lost as the cube converged on authorization/replay evidence. Either rename the component to match its current role or write an explicit higher-level architecture showing where anonymity and synchronization live. Ambiguous naming encourages ambiguous claims.

### The cube as an evolutionary proof laboratory

The cloudtainer may be most valuable as a compact security laboratory: each revision freezes a discovered invariant, its exploit, and a regression. That can work well if production code is separated from evidence code, active claims are small, and tests challenge semantic equivalence rather than only internal consistency. Rev0618’s empty digest and rev0631’s tuple collision are strong lessons for that model.

## Online standards and primary references used

- OAuth 2.0 Demonstrating Proof of Possession (DPoP), RFC 9449: https://www.rfc-editor.org/rfc/rfc9449
- OAuth 2.0 Mutual-TLS Client Authentication and Certificate-Bound Access Tokens, RFC 8705: https://www.rfc-editor.org/rfc/rfc8705
- OAuth 2.0 Security Best Current Practice, RFC 9700: https://www.rfc-editor.org/rfc/rfc9700
- CloudEvents specification: https://github.com/cloudevents/spec/blob/main/cloudevents/spec.md
- DSSE background and pre-authentication encoding rationale: https://github.com/secure-systems-lab/dsse/blob/master/background.md
- DSSE envelope/PAE definition: https://github.com/secure-systems-lab/dsse/blob/master/envelope.proto
- JSON Canonicalization Scheme, RFC 8785: https://www.rfc-editor.org/rfc/rfc8785
- The Update Framework specification: https://theupdateframework.github.io/specification/latest/
- SLSA provenance v1.2: https://slsa.dev/spec/v1.2/provenance
- SLSA artifact verification: https://slsa.dev/spec/v1.0/verifying-artifacts
- SQLite online backup C API: https://sqlite.org/capi3ref.html#sqlite3_backup_init
