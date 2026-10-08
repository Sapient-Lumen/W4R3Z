# 874 — Trust-chain fixture surface audit and fingerprint refactor

**Track:** Shared / Verification / Trust chain fixtures
**Status:** v855/v856 release-gate coherence repair

rev0854 keeps the strongest synthetic trust-chain path compact instead of adding another hidden CLI maze.

The fixture surface remains ten packet-external byte-pinned artifacts:

1. trust keyset
2. trust-keyset publication receipt
3. trust-governance bundle
4. trust-governance-bundle publication receipt
5. trust-status snapshot
6. trust-status-snapshot publication receipt
7. signer-authorization roster
8. signer-authorization-roster publication receipt
9. verification-policy lockfile
10. verification-policy-lockfile publication receipt

The key refactor is that the verification-policy lockfile now carries the packet public fingerprint and the policy receipt repeats that value. Operators should use the rev0854 policy-lockfile fast path instead of hand-copying the long trust-chain flag set.

Generated audit artifacts:

```text
artifacts/reports/trust-chain-fixture-surface-rev0854.csv
artifacts/reports/trust-chain-fixture-surface-rev0854.json
artifacts/reports/verification-policy-lockfile-scope-rev0854.csv
artifacts/reports/verification-policy-lockfile-scope-rev0854.json
artifacts/reports/policy-packet-fingerprint-binding-audit-rev0854.md
artifacts/reports/policy-packet-fingerprint-binding-audit-rev0854.json
```

Current audit result: all sidecars match, all fixtures are packet-external, and the same-selector mutated-packet negative control fails closed with `signature_verification_policy_lockfile_packet_fingerprint_mismatch`.
