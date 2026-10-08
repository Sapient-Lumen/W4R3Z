# BVPS rev0353 rehydration conflict repair runbook

Use this when an offline packet, live packet, release manifest, redacted surrogate, or public statement does not agree.

1. Freeze public claims.
2. Identify packet ID and branch gate.
3. Recompute original and surrogate hashes.
4. Normalize capture, hash, rehydration, and release-review clocks.
5. Check custody transfer and verifier fields.
6. Confirm the artifact is not synthetic, red-team, README-only, public-context-only, or hash-only.
7. Classify the packet as reject, hold, candidate for adjudication, reopen signal, or context/no-upgrade.
8. Never mark local readiness closed from this board.
