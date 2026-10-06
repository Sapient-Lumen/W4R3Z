# DeriveBSD rev0185: MicroVM example wrappers

Selected historical snapshot for the W4R3Z / OG 510P showcase. This page is a later editorial guide; the preserved source files retain their original wording and metadata.

## What to notice

Thin wrapper schemas pin force-stop and denied-stop examples while referring back to the shared microVM stop contracts. The snapshot shows the project making example semantics mechanically expressible without adding those exact fixture values to the core contract.

## Identity and preserved material

- Original ZIP: [DeriveBSD-rev0185-2026.03.04.19.26-microvm-variant-example-wrappers-validated-northstar(3).zip](DeriveBSD-rev0185-2026.03.04.19.26-microvm-variant-example-wrappers-validated-northstar%283%29.zip)
- Filename revision label: `rev0185`
- Carried README/changelog cut: `2026-03-04r185`
- Original ZIP size: 1,847,227 bytes
- Extracted files: 1,355
- Original ZIP SHA-256: `da9d2b891958817fe67bd633192181063ea4e4a481d74073f3e99c1527b0b741`

The outer archive label and the carried cut are recorded separately; neither has been rewritten. The original member paths begin directly under `contents/`. The unchanged ZIP sits beside the extracted tree, and all original file-member paths are retained. Archive/member timestamps are historical metadata, not independently authenticated dates.

## Read the source

- [README.md](contents/README.md)
- [CHANGELOG.md](contents/CHANGELOG.md)
- [docs/00-index.md](contents/docs/00-index.md)
- [spec/microvm.stop.plan.force.schema.json](contents/spec/microvm.stop.plan.force.schema.json)
- [spec/microvm.stop.receipt.denied.schema.json](contents/spec/microvm.stop.receipt.denied.schema.json)
- [spec/examples/microvm.stop.plan.force.json](contents/spec/examples/microvm.stop.plan.force.json)
- [spec/examples/microvm.stop.receipt.denied.json](contents/spec/examples/microvm.stop.receipt.denied.json)

## Evidence boundary

The word “validated” in the archive filename is a carried author claim. The wrapper files can be inspected statically; this review did not validate them or launch or stop a microVM.

This curation used static inspection and byte-integrity checks. It did not execute uploaded code, checkers, bytecode, host-proof work orders or experiments. “Passed,” “validated,” and similar language inside the preserved source describes carried project claims, not a fresh result from this review.

No repository-wide license grant was identified in this bounded review. Public availability does not establish a reuse license; see [archival notes](../../ARCHIVAL-NOTES.md).

[Back to selected DeriveBSD history](../../README.md)
