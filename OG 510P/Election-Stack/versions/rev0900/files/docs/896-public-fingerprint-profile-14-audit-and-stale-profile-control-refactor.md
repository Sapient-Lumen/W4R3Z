# Public-fingerprint profile 1.4 audit and stale profile-control refactor

**Track:** Shared

## Change

rev0862 removes a stale-profile foot-gun from the public-fingerprint safety check and from the strict policy fixture. The executable check now reads the helper's current `REPORT_FORMAT_VERSION` instead of hard-coding the previous profile string.

The strict policy fixture also now aligns all three relevant profile surfaces:

```text
tools/public_fingerprint_report.py REPORT_FORMAT_VERSION = 1.4
verification-policy-lockfile packet_public_fingerprint_profile = 1.4
verification-policy-lockfile controls.packet_public_fingerprint_profile_must_match_verifier_helper = 1.4
```

## Audit artifacts

The generated audit is:

```text
artifacts/reports/public-fingerprint-portable-name-surface-audit-rev0862.json
artifacts/reports/public-fingerprint-portable-name-surface-audit-rev0862.md
```

It builds a synthetic same-selector packet with reserved public filenames and proves that the helper emits warnings and that public-fingerprint comparison returns `UNSAFE_WARNING` rather than `MATCH` or an ordinary mismatch.

## Maintenance rule

When the public-fingerprint helper profile changes, the current strict policy fixture, policy-publication receipt, packet-verification-report schema const, and public-fingerprint safety gate must advance together. A helper profile bump without the policy binding is no longer acceptable for the strict synthetic path.
