# SAM shadow transcripts

`samshadow.py` is a no-network harness for future I2P/SAM integration.

The DHT core still does not talk to I2P.  The shadow layer only canonicalizes and validates command/response shapes that a future Python transport might use.

## Current posture

The rev0015 shadow profile is **streaming-first**:

```text
HELLO VERSION
DEST GENERATE SIGNATURE_TYPE=7
SESSION CREATE STYLE=STREAM ID=... DESTINATION=...
STREAM CONNECT ID=... DESTINATION=...
```

It rejects:

- `STREAM CONNECT` before session creation;
- persistent-DHT profiles that use `DESTINATION=TRANSIENT`;
- unexpected signature type assumptions;
- early dependence on SAM 3.3 primary/datagram subsession support in the bundle-first i2pd path.

## Why this exists before live SAM

Live I2P transport will add latency, router state, tunnel warmup, and implementation differences.  The cube should first make the integration assumptions explicit and testable.  SAM shadow transcripts let the DHT lab say: “these are the session-shape assumptions we think we are making,” before a real router hides bad assumptions behind runtime noise.
