# DeriveBSD: selected design and runtime snapshots

Eight supplied snapshots of a FreeBSD-first, proof-carrying system-control-plane project, preserved for the W4R3Z / OG 510P historical showcase.

DeriveBSD's central idea is to turn declarative intent into verified, reproducible and rollbackable host/workload artifacts, with typed evidence explaining privileged transitions. The early sources present a design archive; the latest supplied snapshot carries a local dry-run runtime and its recorded evidence. The [early core design](versions/rev0185/contents/docs/02-derive-core.md) and [latest runtime account](versions/rev0605/contents/docs/current/runtime-golden-thread.md) make that progression readable.

## Start here

- For the project's original ambition: [rev0185 vision](versions/rev0185/contents/docs/00-vision.md)
- For the latest supplied status: [rev0605 editorial guide](versions/rev0605/README.md) and [preserved README](versions/rev0605/contents/README.md)
- For the evidence behind these summaries: [source map](ARCHIVAL-EVIDENCE.md)

The latest source explicitly calls the project **pre-product**. It describes a fixture-bound dry-run path and expressly withholds claims of an authoritative FreeBSD package index, actual `bectl` activation, bhyve launch or imported real-host proof. Its carried run summary reports `cloudtainer-local-dry-run` and `no-freebsd-system-mutation`. Those records are historical source material, not tests rerun during this curation.

## Selected history

These are selected uploads, not a complete release history or a reconstructed Git commit chain. The filename label and carried cut are separate identities.

- [rev0185](versions/rev0185/README.md) · carried `2026-03-04r185` · MicroVM example wrappers. Thin wrapper schemas pin force-stop and denied-stop examples while referring back to the shared microVM stop contracts.
- [rev0251](versions/rev0251/README.md) · carried `2026-03-09r254` · Metadata-only packet-export checks. A typed follow-up receipt describes metadata-only reverification of the same accepted stronger packet-capture export, preserving its remote identity and protection context.
- [rev0307](versions/rev0307/README.md) · carried `2026-03-19r307` · Relay locator grammar. Relay locator values are constrained by their declared kind: URI hints remain URI-shaped, while portal-object, object-path and opaque values remain non-URI-shaped.
- [rev0359](versions/rev0359/README.md) · carried `2026-03-21r359` · Breakglass authority in support bundles. Incident/support bundles name the exact emergency-access authority receipt by digest when breakglass access materially participated in the incident.
- [rev0409](versions/rev0409/README.md) · carried `2026-03-22r409` · Finite-collection manifest design. A reviewed finite-collection handoff is shaped around normalized member paths and kinds, plus payload digests and byte lengths for regular files.
- [rev0452](versions/rev0452/README.md) · carried `2026-03-23r452` · Visible case-object reverification. Supplementary breakglass evidence may carry a typed metadata-only re-check of an exact accepted case-object revision when an adapter can honestly observe it.
- [rev0501-next57](versions/rev0501-next57/README.md) · carried `2026-05-30r533` · Post-detach successor cutover. A typed terminal-closure successor cutover receipt binds earlier cutover, checkpoint and reader-admission evidence, while the successor-index schema is split into a runtime contract and an exact historical fixture.
- [rev0605](versions/rev0605/README.md) · carried `2026-06-18r630` · Fixture repository snapshot admission. The latest supplied snapshot describes a dry-run runtime that admits a byte-bound fixture repository snapshot before package catalog projection and dependency closure.

The distinctions are especially important for `rev0251` → `r254`, `rev0501-next57` → `r533`, and `rev0605` → `r630`. Original stale or compatibility metadata remains intact inside each snapshot.

## How preservation works

Each `versions/<label>/` directory contains a later editorial README, the unchanged original ZIP with its original filename, and a `contents/` tree that retains every original file-member path. The original wrapper directories in rev0251 and rev0307 remain visible inside `contents/`.

The selection contains **18,040 extracted files**. Original ZIP hashes, sizes, file counts and path mappings are listed in [ARCHIVE-MANIFEST.json](ARCHIVE-MANIFEST.json). Byte verification establishes that the preserved copies match the supplied archives; it does not authenticate the authorship, dates, correctness or engineering claims of those archives.

## Reading this as an archive

The documents, schemas, fixture examples, checkers, logs and session reviews show how the project framed its ambitions and narrowed its contracts. In particular, rev0409's finite-collection handoff remains an RFC-shaping design, and rev0452's metadata-only reverification is conditional on what an adapter can observe.

Historical runbooks, permissions, shell commands and host-proof work orders are preserved context. They are not current instructions to execute, deploy or resume experiments. No uploaded code or binary was run during this review.

## Rights and review limits

No repository-wide license grant was identified in the supplied snapshots during the bounded review. This collection does not invent a license or represent that public visibility supplies reuse rights. See [archival notes](ARCHIVAL-NOTES.md) for preservation, privacy and validation limits.
