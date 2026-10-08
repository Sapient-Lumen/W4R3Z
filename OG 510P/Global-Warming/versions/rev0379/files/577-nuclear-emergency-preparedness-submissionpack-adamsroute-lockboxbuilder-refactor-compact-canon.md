# 577 — Nuclear emergency preparedness: submission packets, ADAMS route verification, and lockbox builder

## Why this revision exists

Rev0369 made the records-request layer visible. Rev0370 makes it artifact-ready. The highest risk is no longer a missing doctrine statement; it is that the June 12, 2026 preliminary-findings meeting, the ANS/siren transition, and the March 2026 EOF power-loss follow-up could be lost in memory, stale links, or unhashable notes before they become admissible evidence.

This revision therefore adds three hard operational controls:

1. **Submission packet builder.** The request templates are rendered into sendable Markdown packets with scope, target artifacts, redaction limits, blockers, and explicit no-readiness-closure language.
2. **Route verification.** Records routes are separated from substantive evidence, including the NRC ADAMS access transition. A route source can help find a record; it cannot prove BVPS readiness.
3. **Public-meeting lockbox builder.** Before the meeting, the package now contains a reproducible empty lockbox with sidecar, hash-ledger, and chain-of-custody templates. Meeting artifacts must be hashed and described before any scoring.

## What changed

New operational files include:

- `cube/nuclear-emergency-bvps-records-route-verification-rev0370.csv`
- `cube/nuclear-emergency-bvps-request-dispatch-ledger-rev0370.csv`
- `cube/nuclear-emergency-bvps-submission-packet-manifest-rev0370.csv`
- `cube/nuclear-emergency-bvps-response-adjudication-rubric-rev0370.csv`
- `cube/nuclear-emergency-bvps-adams-access-transition-audit-rev0370.csv`
- `cube/nuclear-emergency-bvps-meeting-question-card-rev0370.csv`
- `lockbox-templates/bvps-rev0370/*`
- `records-requests/bvps-rev0370/*`
- `evidence-bags/bvps-public-meeting-lockbox-rev0370.zip`

The refactor is practical: the hotpath capsule and SQLite now include the submission-packet/lockbox layer and are generated from a rev0370 source list rather than manual file selection.

## Claim discipline

No public route page, request draft, public meeting notice, plan, mailer, or NRC event notice is scored as readiness evidence. Those records are clocks, routes, or triggers. The cube remains claim-frozen until real or lawfully anonymized artifacts arrive with source/custodian, received time, scope, hashes, and adjudication limits.

Current claim state: **capture-ready / submission-packet-ready / ADAMS-route-verified / public-meeting-lockbox-ready / EOF-LER-watch-open / ANS-transition-gate-open / claim-frozen / no local readiness conclusion**.
