# Structural audit rev0346

Base: `Global-Warming-rev0345-2026.06.05.12.04-packoutfs-autoscan-intakehash-refactor.zip`.

Main correction: rev0345 materialized packet folders, but the intake path still lacked payload-like files. Rev0346 seeds 24 synthetic packets with raw, redacted, custody and QA files, hashes every payload, pairs surrogates, classifies packets, and keeps every packet blocked from readiness claims.

Counts:

- 24 seeded synthetic packets
- 96 synthetic payload files
- 36 packets still missing payloads
- 60 active loss caps
- 0 packets ready to claim
- 0 public-context-to-local-closure leaks

The package still contains no real/anonymized June 2026 Beaver Valley exercise evidence. `REAL_BVPS_PUBLIC_ONLY` remains public-context-only.
