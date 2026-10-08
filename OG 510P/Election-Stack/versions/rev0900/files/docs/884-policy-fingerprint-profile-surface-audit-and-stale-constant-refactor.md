# 884 — Policy fingerprint-profile surface audit and stale-constant refactor

**Track:** Shared / Verification / Audit
**Status:** v858 audit/refactor companion

rev0858 also removes a small but recurring maintenance trap from the Ed25519 verifier regression check. The check no longer hard-codes the current archive version, report version, or strict policy fixture name. It reads `VERSION`, resolves the current `rev####` policy fixture, and reads `REPORT_VERSION` plus the public-fingerprint helper profile from the verifier tools.

That matters because this family changes often. A stale hard-coded regression constant can make the test fail for the wrong reason, or worse, make a newly advanced fixture look current while the test is still pointed at an older policy.

Generated audit surfaces:

```text
artifacts/reports/policy-public-fingerprint-profile-audit-rev0858.md
artifacts/reports/policy-public-fingerprint-profile-audit-rev0858.json
artifacts/reports/verification-policy-lockfile-scope-rev0858.csv
artifacts/reports/verification-policy-lockfile-scope-rev0858.json
artifacts/reports/trust-chain-fixture-surface-rev0858.csv
artifacts/reports/trust-chain-fixture-surface-rev0858.json
```

Current fixture-surface boundary:

```text
fixture_count: 10
failure_count: 0
all_sidecars_match: true
all_fixtures_packet_external: true
```

Maintainer rule: keep the strict synthetic trust chain compact and current by advancing the current policy fixture once per release, with sidecar pins and policy-publication receipt pins regenerated from bytes. Do not move policy, keyset, status, governance, authorization, or receipt fixtures into the packet under verification.

Boundary: this audit is release engineering and synthetic verifier hygiene only. It is not production key ceremony, independent validation, certification, current voter instruction, legal reliance, or live-pilot authorization.
