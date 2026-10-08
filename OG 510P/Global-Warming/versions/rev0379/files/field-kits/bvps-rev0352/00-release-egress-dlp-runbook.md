# BVPS rev0352 release-egress / sensitive-annex DLP runbook

Use this only after a packet has been captured, quarantined, rehydrated if necessary, and classified as a candidate for adjudication. This runbook does not authorize a readiness claim.

1. Confirm packet ID and branch gate.
2. Confirm original artifact hash and custody event.
3. Run sensitive-annex classifier.
4. Split protected fields from public-safe surrogate.
5. Run DLP denylist scan.
6. Confirm no synthetic payload, no replay hash, no redacted-only packet, and no source-ID independence inflation.
7. Run forbidden-phrase lint.
8. Submit to two-person release board.
9. Record release decision in `cube/nuclear-emergency-bvps-public-release-manifest-rev0352.csv`.
10. If anything fails, keep release embargo active and reopen packet if needed.
