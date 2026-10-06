# Validation slice — storage-lane admission model

Current revision: rev0054

Slice id: `scheduler:storage-lane-admission-model-proof`

The slice runs targeted and generated fake-provider histories around `StorageLaneAdmissionHistoryRunner` and compares the real runner to `StorageLaneAdmissionHistoryModelOracle` after every command.

Required evidence:

- deterministic replay matches for a generated seed;
- real/model agreement after every generated command;
- success under admission;
- transient retry under admission;
- watermark rejection with no provider mutation;
- critical bypass under congestion;
- provider-health rejection and recovery;
- hard-limit rejection with no provider mutation;
- held admission lease and release accounting;
- final empty accounting;
- trace events from both model and real runner.

Artifact: `artifacts/validation/REV0044-STORAGE-LANE-ADMISSION-MODEL-PROBE.json`.

Non-claims: No OPFS storage-lane admission-history model proof. No browser Worker storage-lane admission-history model proof. No production overload-governance or performance claim. No exhaustive model checking or formal verification claim.
