# Anonymity archive: reading guide

This collection preserves three supplied research snapshots: rev0162, rev0502, and rev0900. Start with rev0900 for the latest supplied corrections, then use the earlier snapshots to study how the papers and review machinery developed.

Making these snapshots available as an archive does not validate their mathematical claims, certify an anonymous-network deployment, or promote a historical paper out of Hold. Historical release decisions and restrictive license notices are retained unchanged.

## What the collection contains

The research concerns anonymity and metadata leakage in overlay and distributed-hash-table systems: scheduling and padding, state and congestion assumptions, observation models, privacy accounting, deterministic receipts, and the evidence needed to connect a calculation to an implementation. The files include papers, worked examples, machine-readable artifacts, governance records, and local validation/build tooling.

Version guides: [rev0162](versions/rev0162/README.md), [rev0502](versions/rev0502/README.md), [rev0900](versions/rev0900/README.md).

The three snapshots have different shapes:

- **rev0162, 2026-03-05:** 224 files, including 67 TeX papers and 67 PDFs. Paper families live directly below the root. The highlighted change separates long-lived deployment state from a per-contact semantic interface and gives the latter a digest identity.
- **rev0502, 2026-03-22:** 700 files. Paper families move under [series/](versions/rev0502/files/series/); publication policy, queue notes, schemas, and reports become prominent. The highlighted change tightens the declared contract around a replayable verifier when checker or schema versions change.
- **rev0900, 2026-06-18:** 978 files. The latest supplied snapshot corrects an observation-model assumption and moves four Boss Fight papers to Hold. The archive also includes later governance and provenance machinery. It is not a fully verified release.

The smaller rev0900 ZIP is not evidence of less research: it drops shipped PDFs/render clutter and retains seven compressed JSON payloads.

## Short reading route

All paths below are relative to the selected snapshot.

1. In **rev0900**, read [README.md](versions/rev0900/files/README.md), [START_HERE.md](versions/rev0900/files/START_HERE.md), and [REVISION_RECEIPT.json](versions/rev0900/files/REVISION_RECEIPT.json). These explain the correction and its scope.
2. Read [release_queue/LATEST_DECISION.json](versions/rev0900/files/release_queue/LATEST_DECISION.json) and the four relevant notes in [release_queue/hold/](versions/rev0900/files/release_queue/hold/). These record the historical review state.
3. Read [series/bossfight_series/paperA_bossfight_budgets/paper.tex](versions/rev0900/files/series/bossfight_series/paperA_bossfight_budgets/paper.tex) for the observation-model issue, then [series/bossfight_series/paperC_proof_carrying_budgets/paper.tex](versions/rev0900/files/series/bossfight_series/paperC_proof_carrying_budgets/paper.tex) for the model-binding boundary.
4. Read [published/CITATION_HEADS.md](versions/rev0900/files/published/CITATION_HEADS.md) before using any frozen public paper. It carries later corrections and partial-claim withdrawals that the immutable paper bytes do not absorb.
5. Read the version guides linked above and [STATIC_REVIEW.md](STATIC_REVIEW.md) before treating an old report's “pass” as fresh evidence.

For historical context, follow rev0162's [SERIES_INDEX.tex](versions/rev0162/files/SERIES_INDEX.tex) and the opening of [PATCH_NOTES.md](versions/rev0162/files/PATCH_NOTES.md); then read rev0502's [REVISION_RECEIPT.json](versions/rev0502/files/REVISION_RECEIPT.json) and [release_queue/LATEST_DECISION.json](versions/rev0502/files/release_queue/LATEST_DECISION.json).

## Three distinctions to retain

### A scalar rate is not a full observation model

Rev0900 identifies an invalid inference from an average or per-secret reveal probability to an independent-erasure channel. Equal reveal rates do not establish the conditional output distribution. Contact dependence, branch selection, and joint tier observations also matter.

The examples and quantitative values in this archive are research claims and model controls. This intake did not independently reproduce the mathematical proofs or run their validators.

### Checking arithmetic does not establish model validity

The latest proof-carrying formulation limits its verdict to `VALID-UNDER-MODEL(d_M)`. Source identities and deterministic replay are useful, but a deployment claim still needs evidence that the implementation and observer projection realize the stated model.

### Frozen, historically published, and currently supported are different

Rev0900 records five legacy public citation heads and seven post-policy heads, as well as one frozen-only entry. That is the archive's historical classification; it was not checked against an external publication service.

In particular, [published/CITATION_HEADS.md](versions/rev0900/files/published/CITATION_HEADS.md) preserves rev0897 and rev0898 partial-claim withdrawals affecting the calibration head. Read those correction notices alongside the immutable snapshot.

## Integrity, rights, and provenance

The three supplied ZIP hashes match the expected intake values, and every ZIP member passed CRC and path checks. Internal checksums have inherited exceptions in rev0162 and rev0502; rev0900's 977 listed file hashes match. See [STATIC_REVIEW.md](STATIC_REVIEW.md) for exact results.

Rev0900 contains an unsigned in-toto statement and a public verification key. Matching statement subjects and a pinned public-key digest do not constitute a valid signature or independent review. The snapshot says its external hostile-review countersignature and package signature envelope remain missing.

No permissive license is inferred. Rev0900's restrictive [LICENSE](versions/rev0900/files/LICENSE) and [NOTICE](versions/rev0900/files/NOTICE) are preserved; no standalone license file was found in the two earlier snapshots. Archive publication and permission for downstream reuse are separate matters.

## What this intake did

It restored and isolated the originals; independently checked archive structure, CRCs, file hashes, manifests, JSON parsing, and selected static risk indicators; and prepared these guides. It did not run uploaded Python or shell scripts, compile TeX, contact live systems, sign a package, change historical queue states, or validate an anonymity deployment.


## Preserved originals and extracted snapshots

- [rev0162 original ZIP](originals/Anonymity-rev0162-2026.03.05.01.08-contactsurfaceid-schemaexcerpt-pinrule-topaz.zip) · [rev0162 reading guide](versions/rev0162/README.md) · [extracted files](versions/rev0162/files/)
- [rev0502 original ZIP](originals/Anonymity-rev0502-2026.03.22.02.13-verifierbundlecutover-checkerversion-capdrift.zip) · [rev0502 reading guide](versions/rev0502/README.md) · [extracted files](versions/rev0502/files/)
- [rev0900 original ZIP](originals/Anonymity-rev0900-2026.06.18.11.54-obschannel-counterexamples-modelbinding-validatorcut.zip) · [rev0900 reading guide](versions/rev0900/README.md) · [extracted files](versions/rev0900/files/)
