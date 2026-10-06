# DeriveBSD rev0565 session review

This pass stayed on the scarce real-FreeBSD proof path and closed a mutable sealed-archive race. Before rev0565, the sealed importer bound the source archive digest before unsealing, but the path remained mutable between digesting and ZIP validation/extraction. That meant a changed removable-media archive path could make durable receipt provenance ambiguous.

The concrete change is sealed-archive snapshotting before any ZIP reads. `tools/freebsd/unseal_removable_media_local_fallback_host_proof_handoff.py` now copies the archive through a bounded nofollow regular-file snapshot before deterministic ZIP validation and extraction. `tools/freebsd/import_sealed_removable_media_local_fallback_host_proof_handoff.py` performs the same snapshot-first step and records the copied archive snapshot in `source_transport.archive_snapshot`.

The import auditor was refactored so durable sealed-import evidence is checked against the recorded archive snapshot, not by rereading a mutable source archive path that may later be replaced or deleted. The sealed importer checker now mutates the source archive after snapshot and proves the import follows the copied snapshot bytes rather than the later source path contents.

The cut also refreshed host-smoke/proof-bundle examples, schema/refactor/checkset artifacts, current docs, and the canonical hygiene ledger for `2026-06-16r594`. The release-critical profile completed 48 of 48 checks, and the schema-cube-audit profile completed 3 of 3 checks.

Caveat: this is still a Linux cloudtainer pass. It materially hardens the path for receiving and importing a real FreeBSD proof handoff, but it does not include a non-simulated FreeBSD `real-host-proof` import.
