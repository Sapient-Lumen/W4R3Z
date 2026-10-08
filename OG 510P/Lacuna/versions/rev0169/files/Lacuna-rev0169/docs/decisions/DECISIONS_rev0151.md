# Decisions — rev0151

## D-0151-01 — add optional fair-play seals, not universal fixed lore

**Decision:** permit selected hidden values to be precommitted while leaving the rest of the latent world plastic.

**Why:** universal precommitment defeats adaptive planning; no precommitment permits unverifiable hindsight. Selective rigidity matches different genre promises.

## D-0151-02 — use a salted, domain-separated whole-opening digest for v1

**Decision:** hash one bounded JSON opening with SHA-256, a fresh 256-bit nonce, scheme/domain labels, cube ID, and seal ID.

**Why:** this is simple, auditable, and adequate for exact-opening continuity. Domain and identity binding prevent cross-cube and cross-seal replay.

**Deferred:** Merkle leaves, selective disclosure, signatures, threshold opening, and algorithm agility beyond a future scheme identifier.

## D-0151-03 — keep the opening outside Lacuna until reveal

**Decision:** `seal prepare` emits the payload and nonce without mutating the cube; `seal create` persists only digest and metadata.

**Why:** storing an encrypted or hidden opening inside the same cube would enlarge the confidentiality threat surface and invite model/context leakage. The v1 kernel does not need secret storage.

## D-0151-04 — do not call the current serializer JCS

**Decision:** define the v1 scheme around Lacuna’s tested Python canonical JSON profile and explicitly deny RFC 8785 conformance.

**Why:** cryptographic protocol labels must describe executable bytes, not architectural aspiration. A future JCS implementation requires a new scheme ID and test vectors.

## D-0151-05 — exclude floats and unsafe integers

**Decision:** fair-play payloads accept only null, booleans, strings, safe integers, arrays, and string-keyed objects.

**Why:** eliminating ambiguous number serialization is safer than pretending all language runtimes agree. Exact decimals can be strings.

## D-0151-06 — require a committed phase boundary

**Decision:** reveal and void may occur only after the origin seal’s change-set has committed.

**Why:** a same-transaction commit/reveal is not prior commitment. A generic minimum time or sequence gap remains campaign policy.

## D-0151-07 — keep seal semantics inert

**Decision:** reveal records the opening but does not create claims, assertions, assignments, or anchors.

**Why:** cryptographic continuity and epistemic truth are different predicates. Automatic conversion would smuggle author intent into canon and bypass normal provenance.

## D-0151-08 — make seal lifecycle host-only

**Decision:** direct CLI/Python administration can create, reveal, or void seals; ordinary model turn grants cannot, including director grants.

**Why:** the narrator model should not control the secret-custody boundary it may be asked to narrate or evaluate. This also limits prompt-injection impact.

## D-0151-09 — publish visible receipt metadata but hide provenance linkage

**Decision:** audience-visible seal records carry digest and lifecycle state; perspective projections omit `source_id` and hidden source graph edges.

**Why:** a player can verify a commitment without learning the identity of private author notes or hidden planning records.

## D-0151-10 — hash an immutable receipt core

**Decision:** `receipt_sha256` covers only origin-fixed seal metadata and the commitment event envelope.

**Why:** an externally anchored receipt must remain byte-stable across reveal or void. Current head and lifecycle views remain outside the core.

## D-0151-11 — make nonclaims first-class output

**Decision:** receipts state what they do not prove, including truth, completeness, authorship, uniqueness, trusted time, signatures, and hostile-host non-equivocation.

**Why:** cryptographic vocabulary encourages overclaiming. Machine output should carry its trust boundary with it.

## D-0151-12 — retain legacy particle tables but reject their state

**Decision:** preserve two dormant tables for database-shape compatibility, remove the unimplemented public operation/module, flag any rows, and clear them on rebuild.

**Why:** silently changing historical schema shape would complicate migration and verification, but shipping unowned projection state would be worse. This creates an explicit quarantine until a real event protocol is designed.

## D-0151-13 — add strict opening and receipt schemas

**Decision:** ship Draft 2020-12 exchange schemas and test them against runtime contracts.

**Why:** opening custody and anchorable receipt structure are protocol surfaces, not incidental dictionaries.

## D-0151-14 — keep external anchoring outside the kernel

**Decision:** emit a stable digest and guidance rather than bundling one witness, timestamp, or transparency provider.

**Why:** external trust policy is deployment-specific. The kernel should expose a clean anchor point without absorbing credentials, network assumptions, or vendor lifetime.

## D-0151-15 — refuse non-scalar Unicode before hashing

**Decision:** reject lone UTF-16 surrogate code points in payload strings and object keys.

**Why:** Python can represent such values even though they are not Unicode scalar values and cannot be emitted as ordinary UTF-8. A cryptographic exchange profile must fail deterministically at validation, not leak a language-specific encoder exception.

## D-0151-16 — isolate the bundled executable from ambient Python sites

**Decision:** make the repository launcher a small POSIX wrapper that executes `python3 -S` with only `src/` added to `PYTHONPATH`.

**Why:** Lacuna has zero runtime dependencies. Importing arbitrary system site packages or `sitecustomize` hooks enlarges the trust boundary, makes behavior host-dependent, and imposed extreme startup/memory cost in acceptance. Installed console scripts remain packaging policy; the bundled artifact entrance is deliberately standard-library-only.
