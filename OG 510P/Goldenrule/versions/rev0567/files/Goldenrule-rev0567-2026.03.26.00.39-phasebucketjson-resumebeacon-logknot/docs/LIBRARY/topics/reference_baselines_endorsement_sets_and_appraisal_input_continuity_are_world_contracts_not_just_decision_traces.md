# Reference baselines, endorsement sets, and appraisal-input continuity are world contracts, not just decision traces

Portable evidence packets, policy snapshots, and replay diagnostics are still not enough for any successor-facing archive if future inheritors cannot also reconstruct **which reference values, endorsements, trust roots, and policy data were actually in force when the verdict was produced**.

- `RS-GR-414` shows that RFC 9334 defines Reference Values as the set of values against which claims are compared and Endorsements as verifier-consumed secure statements about an Attester's capabilities, which means an Attestation Result can survive while the appraisal inputs that made it possible do not.
- `RS-GR-415` shows that the current CoRIM draft says Reference Values and Endorsements are required for verifier reconciliation and that matched reference values add the CoRIM issuer's authority into the reconciled appraisal claims set, which means the baseline corpus is part of the trust-bearing record rather than a disposable lookup.
- `RS-GR-416` shows that the current RATS endorsements draft distinguishes actual state from reference state, supports conditional endorsements, treats the trust-anchor store as reference state, and allows multiple endorsers for different layers, which means the same evidence can appraise differently when the reference corpus or endorsed-layer bindings change.
- `RS-GR-417` shows that the current RATS reference-interaction draft treats Reference Values, Endorsements, and Appraisal Policy for Evidence as mandatory verifier inputs and allows claim-selection filters over the evidence that is collected, which means verdict replay also depends on the baseline-input scope and collection contract.
- `RS-GR-418` shows that Sigstore's current security model says the Sigstore Trust Root secures the keys and certificates used to verify Fulcio certificates and Rekor entries, which means a future verifier inherits not just signatures and receipts but also a concrete trust-root corpus.
- `RS-GR-419` shows that current Sigstore policy-controller documentation lets TrustRoots come from a remote TUF root that auto-updates, a serialized air-gap repository that must be rotated manually, or out-of-band keys / certificates, which means the same verification policy can behave differently depending on how the reference corpus is sourced and refreshed.
- `RS-GR-420` shows that current OPA bundle documentation says policy and related data are loaded from bundles and enforced immediately once loaded, which means even when the rule language is unchanged, changing the bundled data can silently change what a verifier accepts.
- Together, these sources warn that a benchmark can look more successor-safe because it changed **reference-value corpus, endorsement set, trust-root repository, policy-data bundle, or baseline refresh path** — not because the underlying Golden-Rule disposition improved.

A future benchmark should not treat a saved decision trace as proof that replay conditions are complete.

At minimum, it should distinguish between:

1. a world where the final verdict and explanation survive, but the known-good / known-bad baseline values do not;
2. a world where reference values survive, but the endorsement set, trust roots, or issuer bindings that made those values admissible do not;
3. a world where baseline corpora survive only as live URLs or service lookups, so replay fails once those services drift or disappear;
4. a world where the archive preserves digested, versioned snapshots of the exact reference-value, endorsement, trust-root, and policy-data inputs used for each decision;
5. a world where future inheritors can compare the historical baseline corpus to the current one and tell whether a verdict changed because the cooperative problem changed or because the appraisal baseline changed.

These are different worlds.
They change whether future inheritors can merely observe an old result, replay the same rulebook against the same baseline inputs, or separate moral / institutional progress from silent baseline drift.

So reference baselines, endorsement sets, and appraisal-input continuity belong in the world contract.

## Minimum contract to publish

Any Golden Rule benchmark that claims durable provenance, successor-safe authenticity, or replayable long-horizon verification should publish at least:

1. the exact baseline-input artifacts retained or pinned for each material verdict: reference values, endorsement sets, trust-root / trust-anchor material, and any policy-data bundle that affected evaluation;
2. a stable identifier and digest for each baseline artifact, plus who issued or curated it and what subject / layer / namespace / relying-party scope it covered;
3. whether each baseline artifact was loaded locally, fetched from a remote mirror, relayed by an intermediary, or supplied out of band, and what freshness / rotation / expiration semantics governed it;
4. what the verifier did when one baseline artifact was missing, stale, unreachable, or inconsistent with the others;
5. whether the archive retains only the historical baseline corpus, only the current baseline corpus, or both, and how disagreements between them should be reported.

Without that compact contract, future inheritors can mistake baseline drift for Golden-Rule progress.
