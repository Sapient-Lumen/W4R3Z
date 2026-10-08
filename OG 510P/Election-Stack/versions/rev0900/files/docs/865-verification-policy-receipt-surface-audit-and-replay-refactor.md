# 865 — Verification-policy receipt surface audit and replay refactor

**Track:** Shared / Verification / Policy lockfile
**Status:** v855/v856 release-gate coherence repair

**Release:** `v851`

The trust-chain fixture-surface audit keeps the strongest policy path small enough to inspect. In `v851`, the audited trust-chain surface is:

```text
fixture_count: 9
failure_count: 0
all_sidecars_match: true
all_fixtures_packet_external: true
```

The important refactor is that the policy lockfile and policy publication receipt stay outside the packet under test and remain sidecar-pinned. They should not be copied into the packet as “helpful context,” because that would let the artifact under verification help authenticate itself.

See:

```text
artifacts/reports/trust-chain-fixture-surface-rev0851.json
artifacts/reports/verification-policy-lockfile-scope-rev0851.json
artifacts/reports/verification-policy-receipt-temporal-order-audit-rev0851.json
```

Boundary: fixture-surface coherence is not production trust-root governance, current voter instruction, certification, legal reliance, or live-pilot authorization.
