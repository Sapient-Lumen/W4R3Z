# rev0502 reading guide

## Identity

- Bundle: `Anonymity-rev0502-2026.03.22.02.13-verifierbundlecutover-checkerversion-capdrift.zip`
- SHA-256: `cfe9af79e9bb0fd4b8c24414ad834cd05252f280b3a6fb6912babe32b261cd8b`
- ZIP contents: 700 files and 151 explicit directory entries; 31,806,864 uncompressed file bytes.
- [REVISION_RECEIPT.json](files/REVISION_RECEIPT.json) records the timestamp as 2026-03-22T02:13:00-04:00. This is source metadata, not external time attestation.

## What to read

Paths are relative to this snapshot.

1. [README.md](files/README.md) and [START_HERE.md](files/START_HERE.md) for the operator and archive map.
2. [REVISION_RECEIPT.json](files/REVISION_RECEIPT.json) and [release_queue/LATEST_DECISION.json](files/release_queue/LATEST_DECISION.json) for this revision's bounded change.
3. [series/bossfight_series/paperC_proof_carrying_budgets/paper.tex](files/series/bossfight_series/paperC_proof_carrying_budgets/paper.tex).
4. [release_queue/published_ready/2026.03.17-paperC-proof-carrying-budgets-published-ready.md](files/release_queue/published_ready/2026.03.17-paperC-proof-carrying-budgets-published-ready.md) for the historical review posture.
5. [PUBLISHING.md](files/PUBLISHING.md), [published/PUBLICATION_CLASSIFICATION.md](files/published/PUBLICATION_CLASSIFICATION.md), and [published/CITATION_HEADS.md](files/published/CITATION_HEADS.md) for the distinction between old public heads, frozen files, and queued work.

The featured change makes a verifier's declared checker and schema identities part of its replay contract. Reusing numeric results does not preserve the same verifier claim when that contract changes.

Rev0900 later identifies the deeper model-binding problem and moves this paper to Hold. Do not treat rev0502's Published-ready classification as the latest supplied assessment.

## Structure and historical posture

Paper families now sit under [series/](files/series/). Governance lives in [publishing/](files/publishing/) and [release_queue/](files/release_queue/); [reports/](files/reports/), [schemas/](files/schemas/), and [index/](files/index/) support the archive. The snapshot still includes seven PDFs and 36 PNG review renders.

The source records 6 Candidate, 22 Published-ready, and 52 Hold entries, with no post-policy Anonymity publication action in this revision. These are historical metadata, not a fresh release decision.

## Integrity caveat

The original ZIP hash matches the expected intake hash, and all member CRCs and path checks pass. [MANIFEST.json](files/MANIFEST.json) inventories all 700 files. [MANIFEST.sha256](files/MANIFEST.sha256) has 699 file-digest entries and does not list itself.

695 digest entries match; four do not:

- [reports/archive_invariants.json](files/reports/archive_invariants.json)
- [reports/archive_surface_coherence.json](files/reports/archive_surface_coherence.json)
- [reports/context_pack_contract.json](files/reports/context_pack_contract.json)
- [reports/lifecycle_gate_status.json](files/reports/lifecycle_gate_status.json)

Exact declared and actual hashes are in [STATIC_REVIEW.md](../../STATIC_REVIEW.md) and the machine-readable manifest findings. These are inherited discrepancies in the supplied ZIP; the review did not regenerate or repair those files.

Stored “pass” reports are historical artifacts. Their existence is not evidence that the checks were rerun during this intake.

## Limits and rights

No standalone license or notice file was found. No permissive license is inferred. No uploaded Python, shell helper, or TeX source was executed. The archive's no-publication decision is preserved as historical context; public archival availability does not promote these papers or validate their claims.

