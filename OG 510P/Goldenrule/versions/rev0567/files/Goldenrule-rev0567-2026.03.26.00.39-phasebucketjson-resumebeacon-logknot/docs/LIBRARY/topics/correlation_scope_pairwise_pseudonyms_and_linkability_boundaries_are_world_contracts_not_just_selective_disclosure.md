# Correlation scope, pairwise pseudonyms, and linkability boundaries are world contracts, not just selective disclosure

Portable evidence, disclosure profiles, request contracts, verifier targeting, authenticator-assurance receipts, and transaction-intent bindings are still not enough for any successor-facing archive if future inheritors cannot also reconstruct **who could correlate which presentations with which others, over what scope, using what identifiers, proof families, status paths, or metadata side channels**.

- `RS-GR-478` shows that OpenID Connect Core says pairwise Subject Identifiers must be unique for each Sector Identifier and must not be reversible by any party other than the OpenID Provider, which means an archive must distinguish globally stable identifiers from verifier-cluster or sector-scoped pseudonyms.
- `RS-GR-479` shows that OpenID Connect Dynamic Client Registration says a `sector_identifier_uri` lets a group of sites under single administrative control share consistent pairwise `sub` values independent of their domain names, which means “pairwise” can still license cross-site linkage inside one declared sector.
- `RS-GR-480` shows that the W3C Data Integrity BBS Cryptosuites specification says BBS signatures provide selective disclosure and unlinkable derived proofs, which means some proof families preserve presentation privacy by design rather than merely by withholding fields.
- `RS-GR-481` shows that the W3C Data Integrity ECDSA Cryptosuites specification explicitly says its suites do **not** support unlinkable disclosure and points implementers to BBS if unlinkability is desired, which means the same revealed facts can carry different cross-presentation linkability depending on proof family.
- `RS-GR-482` shows that RFC 9901 says decoy digests trade off payload size against holder privacy, which means omission privacy depends not only on what is disclosed but also on whether undisclosed structure was padded against inference.
- `RS-GR-483` shows that RFC 9901 says an issuer issuing only one type of SD-JWT can have privacy implications because the type and claim names can then be determined, which means a presentation can stay selectively disclosed while still leaking category or issuer-based correlation cues.
- `RS-GR-484` shows that W3C Bitstring Status List v1.0 defines a privacy-preserving, space-efficient mechanism for status publication, which means the archive should distinguish privacy-preserving status lookup from phone-home or singleton-status designs that can correlate use.
- `RS-GR-485` shows that the current W3C Threat Model for Decentralized Credentials treats **Verifiable**, **Minimal**, and **Unlinkable** as distinct privacy properties for credential presentation, which means a proof can be valid and minimal yet still fail the unlinkability contract.
- Together, these sources warn that a benchmark can look more successor-safe or more Golden-Rule aligned because it changed **identifier stability, sector-scoped pseudonymity, proof-family linkability, issuer / type leakage, or status-lookup privacy** — not because the underlying cooperative institution improved.

A future benchmark should not treat “we used selective disclosure” as replay-complete.

At minimum, it should distinguish between:

1. a world where the same holder identifier is globally stable across verifiers and sessions;
2. a world where identifiers are pairwise only up to a shared sector, so multiple sites still intentionally learn the same pseudonym;
3. a world where fields are selectively disclosed but proof-family choice still makes repeated presentations linkable;
4. a world where unlinkable derived proofs exist but status lookup, issuer specialization, or metadata side channels still permit correlation;
5. a world where the archive preserves the intended correlation boundary explicitly: global, ecosystem, sector, verifier, session, one-time, or another named scope.

These are different worlds.
They change whether future inheritors can tell if an apparently improved provenance result came from a better cooperative institution or merely from tighter privacy engineering and narrower correlation scope.

So correlation scope, pairwise pseudonyms, and linkability boundaries belong in the world contract.

## Minimum contract to publish

Any Golden Rule benchmark that claims privacy-respecting provenance, durable replayability, or successor-safe presentation should publish at least:

1. the identifier-stability contract: public, ecosystem-stable, sector-pairwise, verifier-pairwise, session-ephemeral, one-time, or another named identifier scope;
2. the correlation boundary: who can intentionally link repeated presentations — same verifier, sites under one sector, issuer, wallet, status service, federation, or no intended correlator;
3. the proof-family linkability posture: unlinkable derived proof, linkable signed object, stable holder-binding key reuse, or another named mode;
4. the side-channel / metadata correlation posture: issuer specialization, claim-name leakage, resolver lookups, trust-chain reuse, or other category-revealing metadata that remain even when disclosed fields are minimized;
5. the status-check privacy path: privacy-preserving list, direct online check, cached snapshot, or another named status architecture;
6. the padding / decoy / omission-hardening posture for undisclosed claims or hidden structure;
7. the replay exception list: cases where policy intentionally permits broader linkage than the default contract.

Without that compact contract, future inheritors can mistake narrower correlation scope, stronger unlinkability, or more privacy-preserving status checks for Golden-Rule progress.
