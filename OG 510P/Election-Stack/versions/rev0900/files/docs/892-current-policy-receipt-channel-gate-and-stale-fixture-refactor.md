# 892 — Current-policy receipt channel gate and stale-fixture refactor

**Track:** Shared / Verifier / Release gate

rev0861 refactors `scripts/check_publication_receipt_channel_digests.py` so the gate resolves the strict verification-policy fixture from `VERSION` rather than hardcoding a historical rev0860 fixture.

Why this matters: publication-receipt channel-digest checks are only useful if they follow the current strict-policy bytes. A hardcoded old policy can pass while the current policy/receipt pair drifts, leaving the release gate green for the wrong trust-chain fixture.

Executable behavior:

- the checker now targets `artifacts/examples/trust_policies/verification-policy-lockfile-ed25519-authorized-threshold2-rev####.*` using the current `VERSION`;
- trust-keyset, governance-bundle, status-snapshot, signer-authorization-roster, and verification-policy receipts must keep per-channel observed digest fields;
- policy receipt alias coherence is still checked;
- removing per-channel digest observations still fails closed through the verifier.

Audit: `artifacts/reports/current-policy-receipt-channel-gate-audit-rev0861.json`.

Boundary: this is a synthetic fixture gate. It does not prove real publication-channel custody, election-office authority, or independent governance.
