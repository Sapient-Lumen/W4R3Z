# Storage-lane admission-history model frontier

Current revision: rev0055

`StorageLaneAdmissionHistoryModelOracle` is the fake-provider model companion for `StorageLaneAdmissionHistoryRunner`.

It models:

- watermark admission;
- sticky congestion and low-watermark recovery;
- manual held leases used by tests;
- provider-health rejection and recovery;
- critical bypass;
- hard-limit rejection;
- successful provider mutation;
- failed admitted operations with no provider mutation;
- rejection no-mutation accounting.

The model proof is `scheduler:storage-lane-admission-model-proof`. The coherence audit is `facility:storage-lane-admission-model-contract-audit`.

Why this exists: isolated proofs are not enough. The admission-history wrapper composes multiple governors, so future sessions need generated histories and real/model comparison before OPFS/browser provider proofs are attempted.

Important boundary: this is not an OPFS proof, not a browser Worker proof, not a production overload-governance claim, and not formal verification. It is a release-tier fake-provider model oracle that makes the next earned stair safer.
