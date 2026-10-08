# Capability negotiation, downgrade resistance, and chosen-profile continuity are world contracts, not just supported features

Portable evidence, request contracts, verifier targeting, and metadata-resolution receipts are still not enough for any successor-facing archive if future inheritors cannot also reconstruct **which concrete capability profile was actually chosen from the parties' advertised support sets, what weaker fallbacks were available, and whether downgrade or unsupported-extension cases were rejected or silently tolerated**.

- `RS-GR-456` shows that OpenID4VP 1.0 defines `vp_formats_supported` as required Wallet metadata and lets Wallets and Verifiers publish format-specific parameters such as supported algorithms, proof types, cryptosuites, and Client Identifier Prefixes, which means a future inheritor must preserve not only participant metadata but also the supported negotiation surface from which one profile was selected.
- `RS-GR-457` shows that OpenID4VP 1.0 lets a Wallet declare supported request-object signing algorithms and request / response encryption algorithms, requires Request URI processing through a signed request object, and requires `wallet_nonce` continuity when that path is used, which means the chosen request-protection profile is part of the replay contract rather than optional transport flavor.
- `RS-GR-458` shows that OpenID4VP 1.0 requires Wallets to return an error when `expected_origins` does not match and to reject unauthorized `transaction_data` types as unsupported, which means unsupported or downgraded capability requests can be hard failures rather than best-effort fallbacks.
- `RS-GR-459` shows that RFC 8414 publishes capability metadata such as `response_types_supported`, `response_modes_supported`, and `grant_types_supported`, which means the response path a client actually used is only one point inside a wider advertised capability lattice.
- `RS-GR-460` shows that RFC 8725 says applications and libraries must verify algorithms against an application-specified allowlist and recommends explicit typing for new JWT uses, which means the selected cryptographic and token-type profile is an application decision that must not be silently driven by attacker-chosen headers.
- `RS-GR-461` shows that RFC 9101 applies explicit typing to request objects and recommends distinct key-management regimes to prevent cross-JWT confusion, which means a future inheritor may need to know not merely that a request object verified but which protected request profile and key regime made it admissible.
- `RS-GR-462` shows that OpenID4VCI 1.0 publishes credential-request / response encryption requirements and `credential_configurations_supported` objects containing format, signing algorithms, cryptographic binding methods, proof types, and optional key-attestation constraints, which means issuance and presentation compatibility depend on a concrete chosen profile rather than on a generic claim that "the issuer supports this credential".
- `RS-GR-463` shows that OpenID4VCI 1.0 defines fail-closed errors such as `unknown_credential_configuration`, `invalid_proof`, and `invalid_encryption_parameters`, and says request encryption must be used in deferred issuance to prevent substitution when response encryption parameters are involved, which means downgrade and mismatch handling are part of the contract rather than incidental implementation detail.
- Together, these sources warn that a benchmark can look more successor-safe because it changed **which format / proof / algorithm / response-mode / encryption profile was selected, whether weaker fallbacks were tolerated, or whether unsupported capability asks caused hard failure** — not because the underlying Golden-Rule disposition improved.

A future benchmark should not treat “the participants supported these features” as replay-complete.

At minimum, it should distinguish between:

1. a world where participants advertise many formats, algorithms, and response modes, but the archive keeps only the finally observed message;
2. a world where the chosen profile is preserved, but unsupported or weaker alternatives are silently retried until something works;
3. a world where stricter encryption, signing, or request-object protection was available, but the archive does not say whether it was required, preferred, or bypassed;
4. a world where capability mismatches fail closed with named errors and no best-effort downgrade path;
5. a world where future inheritors can replay the full compact negotiation receipt — advertised support sets, chosen format / proof / algorithm / binding / response-mode / encryption profile, preference versus requirement, and downgrade / unsupported-capability fallback.

These are different worlds.
They change whether future inheritors can tell if an apparently improved provenance result came from stronger negotiation posture, tighter downgrade resistance, a different selected profile, or a real change in the underlying cooperative institution.

So capability negotiation, downgrade resistance, and chosen-profile continuity belong in the world contract.

## Minimum contract to publish

Any Golden Rule benchmark that claims durable provenance, replayable presentation / issuance, or successor-safe authenticity should publish at least:

1. the advertised capability sets that were in play: supported formats, proof types, response modes, client-id / discovery modes, cryptographic algorithms, and optional encryption or attestation requirements;
2. the exact chosen profile: format, proof type, cryptographic binding method, signing / encryption algorithms, response mode, request-object protection mode, and any key-attestation or session-binding adjuncts;
3. whether each capability dimension was required, preferred, optional, or best-effort, and which candidate alternatives were considered but rejected;
4. the downgrade posture: fail-closed, retry-with-weaker-profile, local-priority override, or another named policy;
5. the unsupported-capability semantics: which mismatches produced named hard errors, which were ignored, and which were silently dropped or transformed;
6. whether replay under a different but still mutually supported profile is rejected, tolerated as equivalent, or logged as drift.

Without that compact contract, future inheritors can mistake capability narrowing, safer default-profile selection, stricter unsupported-feature rejection, or silent downgrade tolerance for Golden-Rule progress.
