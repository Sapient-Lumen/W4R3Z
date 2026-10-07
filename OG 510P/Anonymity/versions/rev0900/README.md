# rev0900 reading guide

## Identity

- Bundle: `Anonymity-rev0900-2026.06.18.11.54-obschannel-counterexamples-modelbinding-validatorcut.zip`
- SHA-256: `792c50ada3f452d130264e74bcd2e2c009a65a721eea84b98545820dcadb9116`
- ZIP contents: 978 files; 13,048,191 uncompressed file bytes.
- The 2026-06-18 11:54 timestamp is the snapshot's own metadata, not an independently verified time claim.

## Central correction

This is the latest of the three supplied snapshots. It says scalar reveal rates and equal contact marginals do not establish the joint observation channel required by the former privacy claims. It also distinguishes retrospective accounting from prospective privacy filters, and separate tier observations from their joint leakage.

The proof-carrying boundary becomes `VALID-UNDER-MODEL(d_M)`: arithmetic may be correct under a named model while evidence connecting the model to a deployment is absent.

This intake explains that correction from the source documents. It does not independently prove the research results or reproduce the archive's executable mathematical controls.

## What to read

Paths are relative to this snapshot.

1. [README.md](files/README.md), [START_HERE.md](files/START_HERE.md), and [REVISION_RECEIPT.json](files/REVISION_RECEIPT.json).
2. [release_queue/LATEST_DECISION.json](files/release_queue/LATEST_DECISION.json) and its linked decision note.
3. The four sources below [series/bossfight_series/](files/series/bossfight_series/):
   - [paperA_bossfight_budgets/paper.tex](files/series/bossfight_series/paperA_bossfight_budgets/paper.tex)
   - [paperB_anondht_dial_sheet/paper.tex](files/series/bossfight_series/paperB_anondht_dial_sheet/paper.tex)
   - [paperB_addendum_evidence_tables/paper.tex](files/series/bossfight_series/paperB_addendum_evidence_tables/paper.tex)
   - [paperC_proof_carrying_budgets/paper.tex](files/series/bossfight_series/paperC_proof_carrying_budgets/paper.tex)
4. [series/synthesis/paper11_observation_attenuation/paper.tex](files/series/synthesis/paper11_observation_attenuation/paper.tex) and [series/synthesis/paper15_tiered_observation_vectors/paper.tex](files/series/synthesis/paper15_tiered_observation_vectors/paper.tex).
5. The repaired consumers: [series/evaluation_series/paper2_advantage_contracts_stealth_audits/paper.tex](files/series/evaluation_series/paper2_advantage_contracts_stealth_audits/paper.tex) and [series/synthesis/paper17_worked_example_receipt_interlock/paper.tex](files/series/synthesis/paper17_worked_example_receipt_interlock/paper.tex).
6. [published/CITATION_HEADS.md](files/published/CITATION_HEADS.md), especially its rev0897 and rev0898 partial-claim withdrawal notices.
7. [release_queue/EXTERNAL_HOSTILE_REVIEW_PACKET.md](files/release_queue/EXTERNAL_HOSTILE_REVIEW_PACKET.md) for the explicitly unfinished independent-review requirements.

The four Boss Fight papers are on Hold. The historical queue records 5 Candidate, 8 Published-ready, 61 Hold, and 7 Published. This does not imply all claims in the seven frozen heads remain supported; the citation-head correction notices are essential.

## Fixity and compressed payloads

The original ZIP digest matches the expected intake value. All 977 entries in [MANIFEST.sha256](files/MANIFEST.sha256) match. Its only unlisted file is the checksum file itself; [MANIFEST.json](files/MANIFEST.json) inventories all 978 files.

Seven `.json.gz` payloads remain compressed in the preserved tree. Passive intake inspection decompressed them within a 32 MiB-per-file limit, verified gzip CRC, parsed UTF-8 JSON, and performed a bounded secret-pattern scan without executing content. Their expanded hashes are in the machine-readable review.

## Provenance and rights

All 199 subjects in [release_provenance.intoto.jsonl](files/release_provenance.intoto.jsonl) match their local file digests. The statement explicitly says it is unsigned. [signing/package_attestation_public_key.pem](files/signing/package_attestation_public_key.pem) is a public key, and its SHA-256 matches the pin recorded in [NOTICE](files/NOTICE):

`9015959ef93385a5e9e4cdfdc8e70f9752d6ad9a9ca4ef0a7f6f0a27e20f8b81`

A pinned public key is not a signature. The README and startup guide say the package signature envelope and external hostile-review countersignature remain missing. Their absence was not repaired or replaced by this review.

[LICENSE](files/LICENSE) grants no general public reuse license. That restrictive placeholder, [NOTICE](files/NOTICE), historical no-publication flags, and the source papers remain unchanged. Publishing this historical archive does not independently authorize reuse or certify a scientific release.

## Verification boundary

No uploaded validator, build script, or TeX document ran during intake. The archive's stored validator results, compile witnesses, fixed-point claims, and research conclusions remain attributed to the supplied snapshot.

