# rev0060 — livesendgate-deliverywitness-fenceaudit

rev0060 moves one step past settlement-store/tomb-repair/canary readiness.  It still performs no network I/O.  The risky seam is the moment where a no-network canary might accidentally be treated as permission to write to the public edge.

The new rule is: a canary-ready public edge is not live.  Live-send permission, delivery evidence, and restart-safe send fencing are separate local observations that must bind to the same action, profile, service, scope, request, payload, idempotency key, session, destination, and endpoint.

Active surfaces:

- `livesendgate.py` gates the final no-network permission before a future public send.
- `deliverywitness.py` models exact-boundary post-send acknowledgement evidence.
- `sendfence.py` models local monotonic memory so delivery state survives restart without laundering pending work.
- `fenceaudit.py` pins the current revision and preserves the rev0059 predecessor path.

Nonclaim: this is not live SAM/I2P transport, not a production DHT, and not a production delivery protocol.
