# 893 — Public-fingerprint profile 1.3 and current-policy fixture surface audit

**Track:** Shared / Verifier / Release gate

rev0861 keeps the strict verifier surface compact while advancing the current policy fixture to archive `v861`, PacketVerificationReport `1.25.0`, and public-fingerprint profile `1.3`.

The release-relevant surface is deliberately small:

- `tools/public_fingerprint_report.py` owns the bounded public-fingerprint profile and warning semantics;
- `tools/observer_verify_packet.py` treats public-fingerprint warnings as strict-policy authentication failures;
- `scripts/check_public_fingerprint_tool_safety.py` exercises route/name ambiguity and unyielded-symlink cases;
- `scripts/check_publication_receipt_channel_digests.py` checks the current policy fixture instead of a stale hardcoded fixture;
- `scripts/report_trust_chain_fixture_surface.py` keeps the packet-external trust-chain fixture set visible.

Audit surfaces:

- `artifacts/reports/public-fingerprint-unyielded-symlink-audit-rev0861.json`
- `artifacts/reports/current-policy-receipt-channel-gate-audit-rev0861.json`
- `artifacts/reports/trust-chain-fixture-surface-rev0861.json`

Boundary: the archive remains synthetic-release only. This change improves verifier route safety and release-gate freshness, not production signer authority or legal/certification status.
