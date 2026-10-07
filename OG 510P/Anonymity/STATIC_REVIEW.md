# Static archival review: Anonymity rev0162, rev0502, rev0900

Review date: 2026-10-06 UTC. Scope: restoration, fixity, bounded passive inspection, provenance/rights notes, and reading guides for the three supplied ZIPs.

## Result

All three originals match their expected SHA-256 hashes. They contain 1,902 regular files in total. Every member was read to the end, validating ZIP CRC, and extracted into a separate version tree after path/type checks. No archive member was executed.

The main inherited integrity exceptions are one manifest self-entry in rev0162 and four report digests in rev0502. Rev0900 has no mismatches among its 977 listed file digests. These findings are preserved, not silently repaired.

The latest snapshot contains scientific corrections and explicit Hold decisions. Archive publication must not be described as certifying the papers, rerunning their tests, clearing Hold, granting a reuse license, or proving a deployment is anonymous.

## Original identity

- rev0162: 16,509,573 ZIP bytes; 224 files; 18,803,977 expanded file bytes. SHA-256 `9f71ed89426d49aa727729c6c34de6f24a2cd0a13558b6d6dbba39e1273e945c`.
- rev0502: 15,793,075 ZIP bytes; 700 files; 31,806,864 expanded file bytes. SHA-256 `cfe9af79e9bb0fd4b8c24414ad834cd05252f280b3a6fb6912babe32b261cd8b`.
- rev0900: 3,672,458 ZIP bytes; 978 files; 13,048,191 expanded file bytes. SHA-256 `792c50ada3f452d130264e74bcd2e2c009a65a721eea84b98545820dcadb9116`.

Original ZIP bytes and extracted member bytes are unchanged. The review's inventories and guides are separate derived files. Git does not represent empty directories: rev0502's two empty directory entries remain recorded in the original ZIP and inventory; no placeholder files have been added.

## Archive structure and passive checks

Confirmed for all three ZIPs:

- No absolute or traversal paths, backslash paths, control-character names, duplicate names, or case/Unicode-normalization collisions were found.
- No symlink, special-file, or encrypted entry was found.
- The intake's bounded member-count, per-file size, cumulative size, and compression-ratio checks passed.
- Every ZIP member passed decompression and CRC validation.
- Every extracted regular file has an independently computed SHA-256 in its version inventory.
- All 492 ordinary JSON files parsed without duplicate object keys.
- All 129 Python files parsed as syntax trees. Parsing did not import or run those files.
- No selected token/private-key pattern was found in the inspected UTF-8 text, including the seven bounded-decompressed JSON payloads. This is a pattern-only finding, not a guarantee that the archive is free of secrets.
- No selected native-executable magic or TeX file/process-access lexical indicator was found.
- All 74 PDFs parsed during passive dictionary/action inspection with no selected active-action or embedded-file indicator. Two raw byte-token matches were resolved as non-findings by the structured inspection. PDF files were not rendered or executed.

The local tooling includes subprocess-based build/verification code and dynamically loaded local modules. That warrants ordinary untrusted-code precautions before any future execution. This review did not establish the behavior of every possible execution path.

The inspected materials are chiefly research papers, mathematical controls, receipts, and archive/build/governance tools. The bounded inspection did not identify an operational third-party exploitation workflow. This is not a full malware audit, security certification, or endorsement of executing the supplied tools.

## Internal manifest findings

### rev0162

`MANIFEST.json` has 224 entries and covers all 224 files. 223 hashes match. The sole mismatch is its self-entry:

- Path: `MANIFEST.json`
- Declared SHA-256: `666d631003d79e852cd3dea2e62e30cb0f68b858fc85029324e2579d14fe8646`
- Actual SHA-256: `bdcb06af50234225c97417d74d052205b7690f1be8c02b08f8d973b171177e35`

The review does not infer the exact cause from that discrepancy alone.

### rev0502

`MANIFEST.json` lists all 700 files. `MANIFEST.sha256` lists 699 paths, excluding itself. 695 hashes match; four differ:

1. `reports/archive_invariants.json`
   - Declared: `1dadd038bc01d89f8db3d2c822972166f5e96bc4ebf53326d55ec75accf6c51a`
   - Actual: `b6caa3e83266c7f9f7ceda174d7517fdf7a86ff6c8f60d2bccd5cd8dbf88b4dc`
2. `reports/archive_surface_coherence.json`
   - Declared: `792b722388a49ac80e4a9cbbee9bb4d1f6ce0a900848940b7effa8e1bb4219f4`
   - Actual: `e0d7e7de9ebc171db526d078cdfb0a2332e9924e120af5c0ceb45b4ce57f3e39`
3. `reports/context_pack_contract.json`
   - Declared: `64dc57bd5f022e3256af206bdb0406243cfe8a0235ac1b96f00aa79303949742`
   - Actual: `b412b7b0dd220c279e833633ab12158b11efac67e56aabcc343f8ef9a52ed252`
4. `reports/lifecycle_gate_status.json`
   - Declared: `1410659743585b74b1850f649928f6d877e0d0914de03c332f95bbfd73f0ecfc`
   - Actual: `f87fb0d4555682c4e7ffbe33965acc4d93ae50bc131559df2adba712fe742405`

These discrepancies are carried from the supplied archive. No file is missing from either manifest's declared coverage.

### rev0900

`MANIFEST.json` lists all 978 files. All 977 hashes in `MANIFEST.sha256` match; the checksum file itself is its only unlisted file. This establishes consistency of the supplied bytes with that internal checksum list, not authorship, scientific validity, or independent endorsement.

## Compressed payloads and provenance

Rev0900 has seven gzip-compressed JSON payloads in Paper 17's `artifacts/offloaded_payloads/`. Each was read within a 32 MiB expanded-size cap, passing gzip CRC, UTF-8 decoding, and JSON parsing. No payload was executed or substituted into the preserved extracted tree. Expanded sizes and hashes are recorded in [machine/provenance-and-payloads.json](machine/provenance-and-payloads.json); the broader token-pattern scan is in [machine/risk-triage-rev0900.json](machine/risk-triage-rev0900.json).

All 199 subjects in rev0900's `release_provenance.intoto.jsonl` match their local file digests. The source describes this as an unsigned local attestation. Its recorded build commands were not run.

The bundled `signing/package_attestation_public_key.pem` is a public-key PEM with SHA-256:

`9015959ef93385a5e9e4cdfdc8e70f9752d6ad9a9ca4ef0a7f6f0a27e20f8b81`

That matches the source pin. It is not a private signing key and does not itself provide a signature. No package DSSE signature envelope was found in these supplied ZIPs. Rev0900's README, startup guide, and external-review packet also state that package signing and an external hostile-review countersignature remain missing.

Hashes establish fixity relative to the supplied inputs. They do not authenticate who authored the papers, who controlled prior builds, or whether the intermediate revision chain is complete. The two earlier snapshots and rev0900 are separated by unprovided intermediate revisions.

## Scientific and publication limitations

Rev0900 explicitly corrects the inference from scalar reveal probabilities to an independent-erasure channel, adds model-binding requirements, repairs active consumers, and moves four Boss Fight papers to Hold. Its proof-carrying verdict is limited to `VALID-UNDER-MODEL(d_M)`.

The snapshot's `published/CITATION_HEADS.md` also carries rev0897 and rev0898 partial-claim withdrawals for the immutable calibration head. Frozen or historically published bytes must be read together with those corrections.

No uploaded validator, “hostile vector,” shell script, TeX compiler flow, or live network experiment ran during this intake. Stored reports, compile witnesses, and fixed-point claims remain claims of the supplied archive. This review is not the independent external countersignature requested by the archive.

Historical `publication_authorized=false` and no-publication records are preserved as source metadata. They describe the original paper-release posture. Making the historical archive available under current owner authorization is a separate action and does not change that posture or validate its scientific content.

## Rights

No standalone license/notice file was found in rev0162 or rev0502. Rev0900's `LICENSE` explicitly grants no general public reuse license without separate rights-holder permission, and `CITATION.cff` records `LicenseRef-PermissionRequired`. The notice and restrictive placeholder are retained unchanged.

This review does not assign an open-source or permissive license. Public archival availability is not a new grant of reuse rights.

## Deliverables

- [PROJECT_READING_GUIDE.md](README.md): project orientation and cross-version cautions.
- [REV0162_GUIDE.md](versions/rev0162/README.md), [REV0502_GUIDE.md](versions/rev0502/README.md), [REV0900_GUIDE.md](versions/rev0900/README.md): version-specific reading routes.
- `machine/inventory-rev*.json`: every member path, size, original ZIP metadata, CRC, and computed file SHA-256.
- `machine/intake-summary.json`: archive-level fixity and structure.
- `machine/static-summary.json` and `machine/static-rev*.json`: manifest results and passive parsing.
- [machine/provenance-and-payloads.json](machine/provenance-and-payloads.json): unsigned-statement subject results, public-key identity, and gzip payload hashes.
- `machine/risk-triage-rev*.json` and `machine/pdf-passive-inspection.json`: bounded risk-triage detail.

The public review copies omit transfer-account identifiers and local workspace paths.

