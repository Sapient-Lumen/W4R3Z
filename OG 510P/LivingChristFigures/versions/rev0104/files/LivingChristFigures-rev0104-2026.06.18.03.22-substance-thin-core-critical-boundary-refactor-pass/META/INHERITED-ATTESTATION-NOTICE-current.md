# Inherited Attestation Notice — rev0103

Any edit after a release gate invalidates package-level attestation for the resulting bytes. Therefore this revision does **not** reuse the source package’s PASS claim.

The original manifest, descriptors, provenance, QA transcript, checksum/signature surfaces, public manifests, release contract, and selected package-level audit reports are preserved under:

`META/HISTORY/previous-source-package/`

They are historical evidence about the source package only. They do not prove the identity, compression, member set, path coherence, freshness, signatures, or release status of this working revision.

Current proof surfaces are intentionally narrow:

- `QA-REPORT-current.txt` — focused pre-archive correction checks;
- `SHA256SUMS.txt` — extracted-file fixity for this package;
- external `LivingChristFigures-rev0104-2026.06.18.03.22-substance-thin-core-critical-boundary-refactor-pass.zip.audit.json` — audit of the exact delivered ZIP;
- external `LivingChristFigures-rev0104-2026.06.18.03.22-substance-thin-core-critical-boundary-refactor-pass.zip.sha256` — hash of the exact delivered ZIP.

This package is unsigned. A later release should use a persistent user-controlled signing key or an externally anchored transparency record, not a new key generated and delivered inside the same package.
