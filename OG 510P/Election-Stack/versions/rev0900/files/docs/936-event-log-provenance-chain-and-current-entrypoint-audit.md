# 936 — Event-log provenance chain and current-entrypoint audit

**Track:** A — mission-kernel closeout and evidence intake.

v895 through v898 made the synthetic Example County results lane more executable: primary CDF replay, independent replay, reporting-unit comparison, and ballot-accounting reconciliation. The riskiest remaining gap was provenance shape. Those reports could agree while still appearing as loose generated artifacts rather than a chronological evidence-event chain.

v899 adds a minimal synthetic election-event-log witness that binds each critical artifact by SHA-256, previous-event hash, timestamp, role, and release boundary. This is intentionally a small executable bridge, not a broad new doctrine surface.

## Executable change

- `tools/election_event_log_reconciler.py` builds and checks `artifacts/examples/example_county_2026_municipal_pilot/cdf/election-event-log-minimal.json`.
- `scripts/check_election_event_log_reconciler.py` gates the event chain, shipped reconciliation report, public boundary summary, and negative controls.
- `artifacts/reports/election-event-log-reconciliation-rev0899.json` is a current transcript with 12 required artifact roles and zero default errors.
- `artifacts/test-vectors/election-event-log/` now contains fail-closed fixtures for broken previous hash, artifact digest mismatch, timestamp regression, and missing required role.
- The release gate, go/no-go decision, maintainer handoff, current-fixture sweep, mission-kernel closeout, and pilot-data ledger all now cite the event-chain check as current evidence.

## Audit/refactor finding

The current-sweep immediately exposed stale current-entrypoint drift while v899 was being assembled: the source-byte reports, trust-policy lockfile/receipt, PacketVerificationReport example, and Example County scenario outputs were all still carrying the previous revision. That was not a cosmetic issue. A verifier archive whose root says one version while packet, policy, or source-byte entrypoints say another is weaker exactly where public reproduction depends on it.

v899 refreshes those entrypoints and keeps them in the current-revision sweep instead of relying on root navigation alone. The audit result is a stronger release-coherence firewall: current version claims now have to agree across replay, accounting, event-chain, source-byte, policy, packet-report, and Example County scenario surfaces.

## Remaining blockers

This is still synthetic-only. The event-chain fixture is not live Election Event Log evidence, not full NIST EEL/CDF conformance, not the NIST CDF Test Method, not certification, not outcome proof, not current voter instruction, and not legal advice. The real blockers remain jurisdiction-generated exports, authorized local custody and ballot-accounting records, signer/trust-root governance, independent external review, public-release authority, and retention/redaction/legal approval.

## Size/refactor action

Regenerating the v899 source-byte, policy, packet-report, and event-chain surfaces pushed the governed tree over the release size budget. Rather than weakening the budget or deleting history, v899 compacts 37 superseded v898 current-entrypoint/source-byte reports and workpack files into `artifacts/history/rev0899-superseded-v898-sourcebyte-entrypoints.tar.gz` and records the recovery contract in `artifacts/reports/rev0899-retrievable-history-compaction.json`.

The original bytes remain recoverable by path from the deterministic tar+gzip bundle. Current v899 source-byte, policy, packet-report, and event-chain artifacts remain complete and gate-checked.
