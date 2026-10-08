# Portable evidence packets, offline verification, and dependency survival are world contracts, not just live-service validation

Recent provenance work adds one more missing layer beneath signatures, logs, witnesses, and time for any successor-facing archive or trust lane.

- `RS-GR-351` shows that inclusion proofs and consistency proofs are verified against signed tree heads, so a verifier can carry a compact proof object plus checkpoint instead of re-downloading or blindly trusting the whole log every time.
- `RS-GR-352` shows that COSE receipts exist to prove properties of a verifiable data structure and explicitly provide concise encodings for Merkle inclusion and consistency proofs, so portable transparency evidence can be standardized rather than ad hoc.
- `RS-GR-353` shows that a SCITT receipt is an offline, universally verifiable proof of registration, that enough information must be retrievable from audit APIs or included in the receipt to reproduce registration checks, and that a transparent statement can be registered on another transparency service with a second receipt over the first.
- `RS-GR-354` shows that a Sigstore bundle is everything required to verify a signature on an artifact and can embed verification material such as transparency-log entries, timestamps, inclusion proof data, and checkpoints.
- `RS-GR-355` shows that keyless Sigstore blob signing requires storing the bundle for later verification and that the bundle format is being standardized across Sigstore clients rather than left as one tool's private scratch output.
- `RS-GR-356` shows that modern Sigstore clients already expose signing and verification of bundles, online and offline verification with Rekor, TUF support, and custom trusted roots, so dependency-light verification is an operational design choice rather than a theoretical extra.
- Together, these sources warn that a benchmark can look more successor-safe because it changed **portable evidence packet design, offline-verification coverage, retained trust-root posture, or service-loss survivability** — not because the underlying Golden-Rule disposition improved.

A future benchmark should not treat successful verification against a still-live service endpoint as a complete provenance design.

At minimum, it should distinguish between:

1. a world where verification works only while the original log, identity, or trust service is reachable;
2. a world with detached signatures or receipts but without the full retained materials needed for later verification;
3. a world with a self-contained receipt or bundle but no declared local trust-root / trust-policy survival path;
4. a world with self-contained receipts or bundles plus a declared offline-verification path and retained trust roots;
5. a world with self-contained receipts or bundles plus a declared re-registration, re-anchoring, or successor-service migration path if the first service disappears.

These are different worlds.
They change whether future inheritors can merely re-contact the original ecosystem, verify a claim after dormancy or vendor loss, or carry the evidence forward into a successor trust environment without bloating the archive with whole external corpora.

So portable evidence packets and offline verification belong in the world contract.

## Minimum contract to publish

Any Golden Rule benchmark that claims durable provenance, successor-safe authenticity, or long-horizon verifiability should publish at least:

1. exactly which bytes must be retained locally for future verification: signature, certificate, receipt, inclusion proof, consistency proof, checkpoint, timestamp, trust-root set, and any policy metadata;
2. which verification steps can be completed fully offline and which still require live log access, DID / PKI resolution, timestamp authority access, or other network dependencies;
3. whether the retained receipt / bundle format is standardized and cross-client readable or only works with one toolchain version;
4. whether already-issued evidence can be re-registered, re-anchored, or nested under successor transparency services when the original service rekeys, disappears, or is no longer trusted;
5. what the verifier should do when dependencies vanish: reject, warn, trust cached roots, verify stale-but-self-contained evidence, or require re-anchoring under a successor service.

Without that compact contract, future inheritors can mistake dependency survival or portable proof packaging for Golden-Rule progress.
