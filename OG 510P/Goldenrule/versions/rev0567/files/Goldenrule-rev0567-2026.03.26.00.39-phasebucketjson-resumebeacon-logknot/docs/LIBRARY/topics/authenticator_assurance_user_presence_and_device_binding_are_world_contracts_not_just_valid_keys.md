# Authenticator assurance, user presence, and device binding are world contracts, not just valid keys

Portable evidence, request contracts, verifier targeting, metadata-resolution receipts, and chosen-profile continuity are still not enough for any successor-facing archive if future inheritors cannot also reconstruct **what kind of authenticator or key container stood behind the proof, whether the user was merely present or locally verified, whether the key was syncable or device-bound, and whether those properties were attested or only inferred**.

- `RS-GR-464` shows that WebAuthn Level 3 places `User Present` (UP) and `User Verified` (UV) bits directly in authenticator data and also carries backup-eligibility / backup-state bits, which means one cryptographically valid assertion can encode materially different user-control and syncability semantics.
- `RS-GR-465` shows that WebAuthn Level 3 says a relying party MAY use the AAGUID to infer authenticator properties such as certification level and strength of key protection, but that the AAGUID is not provably authentic without attestation, which means authenticator-class inference and authenticator-class proof are separate contracts.
- `RS-GR-466` shows that the current NIST SP 800-63B guidance says verifiers should inspect WebAuthn UP / UV flags, treat UV as the difference between single-factor and multi-factor cryptographic authenticators, and use the backup-eligibility flag to distinguish device-bound authenticators from ones that may be synced, which means local user-control and exportability state are first-class assurance facts rather than implementation trivia.
- `RS-GR-467` shows that the current NIST SP 800-63B guidance says AAL3 requires a phishing-resistant cryptographic authenticator with a non-exportable private key, requires authentication intent, and says syncable authenticators shall not be used at AAL3, which means a future inheritor may need to know whether a proof came from a syncable convenience key path or a non-exportable high-assurance one.
- `RS-GR-468` shows that OpenID4VCI 1.0 key attestations can carry `attested_keys`, `key_storage`, `user_authentication`, freshness nonce, and status information, which means issuance can preserve device or security-element assurances and local-authentication resistance claims rather than collapsing all holder keys into one bucket.
- `RS-GR-469` shows that OpenID4VCI 1.0 and the current HAIP profile separate bare proof-of-possession from explicit key-attestation proof types and require wallet support for key attestations in high-assurance interoperability settings, which means a valid bound key and an attested bound key are different worlds.
- `RS-GR-470` shows that OpenID4VP 1.0 explicitly allows some requests to proceed without cryptographic holder binding and warns that a verifier accepting such a presentation accepts replay risk, which means future inheritors must preserve whether holder binding, proof-of-possession, or key-bound attestation was required, optional, or waived.
- Together, these sources warn that a benchmark can look more successor-safe because it changed **authenticator class, local user-verification requirements, exportability / syncability, attestation posture, or holder-binding strictness** — not because the underlying Golden-Rule disposition improved.

A future benchmark should not treat “a valid proof was produced with the right key” as replay-complete.

At minimum, it should distinguish between:

1. a world where the same proof format is signed by a software-held or otherwise weakly characterized key with no preserved attestation about storage or local user authentication;
2. a world where the verifier saw UP but not UV, so the event showed user participation without proving a second factor or local user verification;
3. a world where UV was achieved but the key remained backup-eligible or syncable, so possession may no longer be device-unique;
4. a world where the key was device-bound, non-exportable, attested, and tied to a named authenticator class or certified storage / user-authentication profile;
5. a world where holder binding itself was optional or waived, so replay risk changed even though the disclosed claims and verifier target stayed fixed.

These are different worlds.
They change whether future inheritors can tell if an apparently improved provenance result came from a stronger authenticator path, tighter user-presence or user-verification policy, stricter anti-syncability rules, richer attestation, or a real change in the underlying cooperative institution.

So authenticator assurance, user presence, and device-binding continuity belong in the world contract.

## Minimum contract to publish

Any Golden Rule benchmark that claims durable provenance, replayable presentation / issuance, or successor-safe authenticity should publish at least:

1. the authenticator-event facts that mattered: UP / UV or equivalent local user-control signals, authentication-intent semantics, and whether explicit user action was required per transaction;
2. the key-container posture: software-held, hardware-backed, device-bound, non-exportable, backup-eligible, backup-state, or another named exportability / residency class;
3. the authenticator-class evidence: attestation presence or absence, AAGUID or equivalent device-class identifier, certification claims, and whether any class inference was verified or merely heuristic;
4. the binding requirement: whether cryptographic holder binding, proof-of-possession, key-bound attestation, or another designated mechanism was required, optional, or waived;
5. the issuance or presentation attestation payload retained for replay: attested keys, key-storage claims, user-authentication claims, freshness nonce, status or revocation path, and trust-chain material when relevant;
6. the policy consequence of each assurance tier: which authenticator or key states were admissible, which were downgraded, and which were rejected as too weak, too syncable, or too weakly attested.

Without that compact contract, future inheritors can mistake stronger device binding, stricter user-verification requirements, high-assurance key attestation, or removal of syncable authenticators for Golden-Rule progress.
