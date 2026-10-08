# Disclosure profiles, omission semantics, and retention intent are world contracts, not just smaller payloads

Portable evidence, policy snapshots, appraisal baselines, decision traces, and acquisition receipts are still not enough for any successor-facing archive if future inheritors cannot also reconstruct **what was deliberately disclosed, what stayed hidden, what absence means, and whether a verifier was told it may retain the revealed data**.

- `RS-GR-428` shows that RFC 9901 defines selective disclosure for JWT payload elements, validates only the Holder-selected Disclosures that are actually presented, supports decoy digests to hide the original number or conditional presence of claims, and forbids making authenticity- or validity-critical content selectively disclosable, which means omission semantics are part of the trust contract rather than an accidental side effect of compact encoding.
- `RS-GR-429` shows that the current SD-JWT VC draft says a Holder can decide which claims to release within issuer-defined bounds, which means future inheritors must preserve not only what was revealed but also the issuer-imposed disclosure boundary that constrained holder choice.
- `RS-GR-430` shows that Verifiable Credentials Data Model v2.0 supports derived credentials and zero-knowledge proofs so a holder can prove properties such as age thresholds without revealing the underlying value, says selective disclosure should let the holder provide precisely what the verifier needs and nothing more, and describes the ideal privacy-respecting verifier as one that records only that the disclosure requirement was met and discards sensitive data, which means retention posture and redaction granularity are first-class world semantics.
- `RS-GR-431` shows that Verifiable Credential Data Integrity 1.0 expects applications to choose cryptography suites according to whether they need full, selective, or unlinkable disclosure, which means disclosure profile is part of the application contract rather than a generic proof-format detail.
- `RS-GR-432` shows that the BBS cryptosuite separates mandatory from non-mandatory statements, carries `mandatoryIndexes` and `selectiveIndexes` inside derived proof processing, and aims for unlinkable proof artifacts, which means future inheritors need a replayable answer to which statements were always revealed, which were optionally disclosed, and what correlation properties the presentation was supposed to avoid.
- `RS-GR-433` shows that OpenID for Verifiable Presentations 1.0 defines explicit claims-query and claim-selection logic, treats a value-restricted claim that does not match as if it did not exist in the credential, and includes an `intent_to_retain` flag for ISO mdoc claim requests, which means missing fields can encode request-policy semantics, holder choice, or verifier retention expectations rather than mere nonexistence.
- Together, these sources warn that a benchmark can look more successor-safe because it changed **how much was disclosed, what absence means, which claims were mandatory versus optional, whether decoys concealed hidden structure, whether retention was authorized, or whether unlinkability / holder-binding changed**, not because the underlying Golden-Rule disposition improved.

A future benchmark should not treat “the proof got smaller” or “the verifier only saw a subset” as self-explanatory.

At minimum, it should distinguish between:

1. a world where a field is absent because it was never issued;
2. a world where a field is absent because it was issued but not requested;
3. a world where a field is absent because it was requested but withheld by holder choice or value-filter mismatch;
4. a world where a field is absent because decoy structure or derived predicates intentionally conceal whether a field exists at all;
5. a world where the verifier may check a claim transiently but is not authorized to retain the underlying disclosed value;
6. a world where future inheritors can compare two equally valid presentations and tell whether auditability changed because the cooperative problem changed or because the disclosure / retention contract changed.

These are different worlds.
They change whether future inheritors can replay the same privacy boundary, compare like with like across time, and interpret omission without inventing facts that were never actually revealed.

So disclosure profiles, omission semantics, and retention intent belong in the world contract.

## Minimum contract to publish

Any Golden Rule benchmark that claims durable provenance, privacy-respecting replay, or successor-safe authenticity should publish at least:

1. the disclosure profile used for each material verdict: full disclosure, selective disclosure, derived predicate / threshold proof, unlinkable presentation, or another explicitly named mode;
2. which claims or statement classes were mandatory, which were optional, which were always hidden, and which were conditionally disclosable only within issuer-defined bounds;
3. what absence means for each relevant field: never issued, not requested, request-filter mismatch, holder withheld, decoy-concealed, redacted after presentation, or unknown;
4. whether the verifier required holder binding, audience / nonce binding, or other anti-forwarding constraints for the disclosed subset;
5. whether the verifier declared or was constrained by any retention intent, discard expectation, or “check but do not archive” rule for sensitive disclosures;
6. what unlinkability / correlation posture the presentation mode was supposed to provide, and what identifiers, mandatory claims, or retention choices could still re-link sessions in practice.

Without that compact contract, future inheritors can mistake privacy-boundary drift or omission-policy drift for Golden-Rule progress.
