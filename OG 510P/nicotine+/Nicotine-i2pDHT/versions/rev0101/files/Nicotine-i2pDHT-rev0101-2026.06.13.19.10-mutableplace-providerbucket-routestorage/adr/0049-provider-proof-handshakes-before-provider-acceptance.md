# ADR 0049 — Provider proof handshakes before provider acceptance

Accepted for rev0013.

Signed provider records are not semantic truth. The DHT should require challenge-bound proof transcripts before treating a provider as confirmed.

The first implementation is toy but tests wrong digest, replay, bad signature, useful refusal, metadata exposure, and deadline pressure.
