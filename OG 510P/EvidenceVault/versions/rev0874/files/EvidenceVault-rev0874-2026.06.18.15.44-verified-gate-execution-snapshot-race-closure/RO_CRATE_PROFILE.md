# RO-Crate metadata bridge

This file is the exact human-facing companion to `ro-crate-metadata.json`.
The bridge exposes selected EvidenceVault core archive surfaces as compact JSON-LD research-object metadata without replacing `RELEASE_MANIFEST.json`, `MANIFEST.sha256`, or `INDEX/files.*` as governing inventory surfaces.

- Context: `https://w3id.org/ro/crate/1.2/context`
- Descriptor: `ro-crate-metadata.json`
- Conforms to: `https://w3id.org/ro/crate/1.2`
- Root entity: `./`
- Root version: `rev0826`
- Date published: `2026-05-25`
- Identifier: `EvidenceVault-rev0826-2026.05.25.19.36-release-artifact-embedded-command-runner-sequence-verifier-audit-refactor-hardening`
- Root license: `NOASSERTION`
- Required hasPart entries: `25`
- Digest-checked file entities: `19`

## Required root hasPart entries

- `RELEASE_MANIFEST.json`
- `REVISION_RECEIPT.json`
- `REVISION_ANCHORS.json`
- `VALIDATION_INDEX.json`
- `CLAIM_OBLIGATION_MAP.json`
- `PUBLIC_STATUS.json`
- `TOOLCHAIN_LOCK.json`
- `COMMAND_RUNNER_SEQUENCE.json`
- `SOURCE_INDEX.json`
- `ARCHIVE_INDEX.json`
- `CONTROL_SURFACES.json`
- `LIFECYCLE_GATES.json`
- `papers/EXTRACTION_MAP.json`
- `published/PUBLIC_SURFACE.json`
- `MANIFEST.sha256`
- `INDEX/files.json`
- `ev_acceptability_kernel.pdf`
- `ev_interpretation_profiles.pdf`
- `ev_streamfold.pdf`
- `ev_zkrtp.pdf`
- `ev_pact_ocf.pdf`
- `sources/`
- `artifacts/`
- `certs/`
- `published/`

## Digest-checked file entities

- `RELEASE_MANIFEST.json` — size `7673` — sha256 `be53351cfce5fa30ee0daf53b0e61cd75db8929f3a3e5ac6be16b02a2eb9cfc3`
- `REVISION_RECEIPT.json` — size `4205` — sha256 `0b49e28538f4d3c5aaa7f87386d689fad03a5493f20669ad45ea49dac7baadf6`
- `REVISION_ANCHORS.json` — size `7988` — sha256 `07c3f006be2aa5cc0b377b3cdae6e40b6e73fc9f1e8cd212fabc3dbb1189d2a8`
- `VALIDATION_INDEX.json` — size `61380` — sha256 `b84ad466ba7793a0d070b3333542b66ccd37c479ac47a2250203432d13b8ab62`
- `CLAIM_OBLIGATION_MAP.json` — size `34135` — sha256 `f87d8384e8f3c9e33ede13f2440d4418219b847b6d096e29bbf1a67c47461829`
- `PUBLIC_STATUS.json` — size `4417` — sha256 `dbb0465b317ee87568462ce35cc8e9b56553a5ba69a55843c7951cfd5bc2f670`
- `TOOLCHAIN_LOCK.json` — size `4330` — sha256 `0b85f9a233d01b9de378e9fb41b91e7e41afb1ec078f7737b9403420af25fa4c`
- `COMMAND_RUNNER_SEQUENCE.json` — size `17826` — sha256 `70c7d0d4d3a258cead66540ad9d3d6adf867bd8539798bc7c9a42df34a3b6462`
- `SOURCE_INDEX.json` — size `5684` — sha256 `3415024b59d544b78e593f1eb95a36338db156089f2fcd8ae0eba9c853f31134`
- `ARCHIVE_INDEX.json` — size `136917` — sha256 `6ca7a8f59968a4a180c0710aa6dbf43a0db999f43f257f6deafbf21671b6a47e`
- `CONTROL_SURFACES.json` — size `44911` — sha256 `aa2cba6df96333a97abe9c8f60507b1be482ceaf63804bdf63ce0d4d948204fe`
- `LIFECYCLE_GATES.json` — size `15615` — sha256 `e9fbe6b9c1be791e1c335fe6781ab48c32d4c18f90c99fb47d12ed7d7a108a4c`
- `papers/EXTRACTION_MAP.json` — size `18004` — sha256 `abf8e8be2708e664b61b62e49dc3d6a7506d0adaf86b569ccba27027d3a251ed`
- `published/PUBLIC_SURFACE.json` — size `1206` — sha256 `04f8aebf31f45649629c29686cf421081c93513373db253abff9541841287581`
- `ev_acceptability_kernel.pdf` — size `249005` — sha256 `665c2f68b0e3c9a43783e88aaf39ebf120f7cdd864d9d93b00b326256df0d914`
- `ev_interpretation_profiles.pdf` — size `249321` — sha256 `7e6baf39d9c64b37344d3c8ebfd03fdf5b64f4542267c8d2e5bad5a76fed1bc8`
- `ev_streamfold.pdf` — size `138610` — sha256 `c9e44fc2e390f416a6fc6dae10a09eb77bab826fe402bd323786a579dd28c0b9`
- `ev_zkrtp.pdf` — size `166145` — sha256 `e5a8d8b4c9da31c35565181a17c47adaac03a362008cbd1c5be44b4b589a4488`
- `ev_pact_ocf.pdf` — size `128134` — sha256 `14228720f27c385d3b02f26e91680c604cd47ac6c338372d65b7ebc565c5c9cf`

## Self-referential inventory entries

`MANIFEST.sha256` and `INDEX/files.json` are listed as core inventory surfaces but their own size/hash are omitted from this bridge to avoid a metadata/manifest digest cycle. Their governing verification remains `make manifest-check`.

## Directory entities

- `artifacts/`
- `certs/`
- `published/`
- `sources/`
