# DeriveBSD rev0541 session review - mission audit, waste cutline, and real-host proof focus

Generated at: `2026-06-16T15:50:54Z`

Source archive inspected: `DeriveBSD-rev0540-2026.06.13.06.04-authoritytokenreplay-ledgerrefresh-releasegreen-owl(1).zip`

Internal cube cut observed: `2026-06-13r571`

Cloudtainer truth: this session ran on Linux, not on a real FreeBSD host. No non-simulated FreeBSD host proof is claimed here.

## Heart of the mission

DeriveBSD is not primarily a package manager, an installer, a hypervisor wrapper, or a documentation project. The heart of the mission is to make a whole operating system behave like a typed derivation with replayable evidence: `Spec -> Lock -> Plan -> Artifact -> Activate/Launch -> Receipt`, with every authority transfer, mount, build, switch, rollback, and workload launch represented as digest-addressed data that can be audited after the fact.

The distinctive bet is BSD-native minimalism plus evidence discipline. FreeBSD primitives such as ZFS boot environments, jails, Capsicum-style capability reduction, bhyve microVMs, devfs rules, rc/service integration, and base-system packaging are meant to become the substrate for an OS that is reproducible, rollbackable, least-authority by default, and explainable to operators.

The mission succeeds only if the receipt graph corresponds to real host behavior. The cube already understands this: its current front door names the real FreeBSD removable-media local fallback proof as the riskiest unfinished item. That is the correct center of gravity.

## What I validated in this cloudtainer

- `release-critical`: passed `38 / 38` checks in the Linux cloudtainer.
- `schema-cube-audit`: passed `3 / 3` checks in the Linux cloudtainer.
- Strict duplicate-key guard: previously observed passing over `1379` JSON files during this session.
- Removable-media FreeBSD host proof-bundle guard: previously observed passing, including rejection of non-proof simulations by default.
- New proof claim added by this review: none. The validation here is cloudtainer validation, not real host proof.

The validation ledgers for the two hygiene profiles are checked into this session review set beside this note.

## What is missing

1. Real FreeBSD host proof is still missing. The cube has a collector, receipt validator, finalizer, and proof-bundle validator, but it does not yet contain a checked-in, non-simulated FreeBSD receipt from the removable-media local fallback lane.

2. The first vertical slice is not yet morally complete. The project has many correct-looking schemas and receipts, but v0 should be judged by one boring end-to-end path: manifest to lock, lock to plan, plan to artifact, artifact to host generation or workload image, switch or launch, then rollback with receipts.

3. Version semantics are overloaded. The uploaded archive is `rev0540`; the internal cube cut reports `2026-06-13r571`; the host-smoke runner and examples still emit `generated_for_version` / `smoke_id` tokens from `2026-06-05r554` in places, while the proof-bundle wrapper names `2026-06-13r571`. This may be intentional runner-contract versioning, but it is currently easy for a human or future importer to mistake stale runner metadata for proof freshness.

4. The FreeBSD target matrix should be re-centered. The cube still carries 14.3-oriented simulation traces, but the online release context now points at FreeBSD 15.1 as production, with 15.0 / 14.4 / 14.3 as legacy at the time of this review. That matters because 15.x also moves base-system packaging and release engineering closer to DeriveBSD's design.

5. The red-corpus story is underpowered. The only PDF fixture I inspected is `fixtures/removable-media/local-fallback/exfat-card/invoice.pdf`; render inspection produced a blank page even though `strings` exposes intended text, and the PDF has a bad startxref / missing font-resource shape. That can be useful as a malformed red fixture, but it should not be the only representative document fixture.

6. The product cutline needs sharper enforcement. The cube already contains strong warnings against feature expansion, but the file distribution shows heavy investment in removable media, workstation isolation, post-detach flows, proof machinery, and schema registries. That work is valuable only if it keeps collapsing toward one proof-backed v0 path.

## What should change next

1. Freeze net-new receipt families until the real FreeBSD proof is imported. Allow only fixes that make the real proof easier, make a receipt less ambiguous, or make a validator stricter.

2. Add an explicit version-semantics checker. Either require the host-smoke runner's `generated_for_version` to match the current cube cut, or rename it to something like `runner_contract_version` and add a separate `cube_cut_version`. Do not leave proof freshness encoded in an ambiguous field.

3. Add a small fixture-PDF sanity checker. Keep one intentionally malformed PDF in a clearly named red corpus, but add a well-formed minimal PDF that renders visible text and participates in the removable-media harness. The current `invoice.pdf` name implies a normal document, while its rendered behavior says malformed/blank.

4. Make FreeBSD 15.x a first-class proof target, or explicitly document why 14.x remains the initial proof host. The 15.0 pkgbase and no-root release-artifact changes look strategically aligned with DeriveBSD's own typed-artifact mission.

5. Add a schema-growth brake tied to the v0 cutline. For example: no net-new schemas unless the session either imports a real proof receipt, reduces an open schema backlog item, or advances the end-to-end v0 path.

6. Turn `docs/420-context-pack.md` into the human front door for new sessions and keep bulky index material generated. The current cube is rich, but the cost of rereading it is rising.

## Places where something has gone wrong or wasteful

### Evidence theatre risk

The cube is highly disciplined about ledgers, schemas, receipts, and validators. That is a strength. It becomes waste if the evidence graph outruns the physical proof graph. The most severe risk is that DeriveBSD becomes a beautiful model of an OS rather than a proven OS path.

Correction over time: make every future session answer one question first: did this move the real-host proof or v0 vertical slice forward? If not, it should be treated as optional and probably deferred.

### Version drift risk

The r554/r571 split in host-smoke metadata is the most concrete local ambiguity I found. It may simply mean runner contract version versus cube release version, but the field names do not make that distinction hard to misuse.

Correction over time: patch schemas and examples to make version intent explicit, then add a check that fails on ambiguous proof-version fields.

### Fixture weakness

The PDF fixture currently behaves like a malformed/blank rendering test while carrying the ordinary name `invoice.pdf`. That is wasteful because a safe-removable-media harness should test both boring valid files and hostile malformed files.

Correction over time: split it into `invoice-minimal-valid.pdf` and `invoice-malformed-missing-font-red.pdf`, or equivalent, and add a render/extract sanity receipt.

### Spec gravity before ship gravity

The cube has hundreds of schemas and many receipt classes. That is not inherently bad for an evidence OS, but it is past the point where additional schema surface proves anything by itself.

Correction over time: bias toward deleting, consolidating, or proving. New schemas should pay rent by reducing operator ambiguity or enabling one executable path.

## Online research notes folded into this review

- FreeBSD release state has changed since older cube material: 15.1 is production; 15.0, 14.4, and 14.3 are legacy.
- FreeBSD 15.0's packaged base system and no-root release-artifact generation look unusually relevant to DeriveBSD's host-artifact model.
- Capsicum and bhyve remain well-aligned substrate choices for least-authority workers and microVM-first workload isolation.
- Nix, Qubes, in-toto, TUF, Sigstore/Rekor, SCITT, RFC 8785/JCS, and Reproducible Builds all cover adjacent territory. DeriveBSD should compose with these ideas where possible instead of re-inventing every trust primitive.

## Recommended next cloudtainer patch set

1. `check_host_smoke_version_semantics.py`: fail ambiguous `generated_for_version` use in proof-shaped host-smoke receipts, or require explicit `runner_contract_version` plus `cube_cut_version`.
2. `check_pdf_fixture_render_sanity.py`: require at least one valid fixture PDF to render non-blank visible content, and require malformed fixtures to be named/classified as red corpus.
3. `docs/current/freebsd-proof-target-matrix.md`: declare the first real proof target across FreeBSD 15.1, 15.0, 14.4, and 14.3.
4. `tools/check_v0_cutline_schema_growth.py`: ratchet schema count or require an explicit exception ledger when adding net-new schemas before real host proof.
5. `docs/current/real-host-proof-import-packet.md`: single-page import checklist for the human who runs the collector on FreeBSD and brings the proof bundle back.

## Local structure snapshot before this review file was added

```json
{
  "file_count_before_review_files": 3203,
  "top_level_file_count_by_dir": {
    "adrs": 368,
    "docs": 822,
    "fixtures": 2,
    "rfcs": 184,
    "session-reviews": 131,
    "spec": 1277,
    "tools": 400,
    "validation": 17
  },
  "total_bytes_before_review_files": 21514870
}
```
