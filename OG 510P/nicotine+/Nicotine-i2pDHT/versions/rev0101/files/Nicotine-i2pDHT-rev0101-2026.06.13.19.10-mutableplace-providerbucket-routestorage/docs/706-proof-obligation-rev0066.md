# Proof obligation — rev0066

A future implementation must prove that:

- repair publish markers cannot drift from outbox/cooldown component digests;
- ACK observations cannot replay across repair-publication boundaries;
- NACK or mixed observations cannot settle closure;
- closure cannot drop contradiction evidence;
- final repair side effects cannot occur without the joined gate.

The cube currently proves these only as deterministic toy Python tests.
