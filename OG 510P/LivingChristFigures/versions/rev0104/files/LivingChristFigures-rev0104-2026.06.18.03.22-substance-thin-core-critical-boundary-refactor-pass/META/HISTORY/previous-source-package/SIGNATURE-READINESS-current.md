# Signature Readiness — current

Current revision: rev0102

Current pass shape: critical-path work-order traceability refactor gate pass.

Signature readiness status: ready after final checksum regeneration and detached signature verification.

Required files:

- `SHA256SUMS.txt`
- `SHA256SUMS.txt.sig`
- `SIGNING-PUBLIC-KEY-rev0102.pem`
- `RELEASE-PUBLIC-KEY.asc`

Release rule: regenerate `SHA256SUMS.txt` after all report generation, sign that final checksum file, then run QA and verify the detached signature. The signing public key is included only for integrity verification; it is not public-release permission and does not authorize publication of closed evidence, source URLs, contact paths, routes, referrals, service-capacity claims, case/client details, images, stories, testimony, legal guidance, or medical guidance.
