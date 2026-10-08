# SAM wire shadow transcripts

`samwire.py` is not a SAM client. It is a no-network transcript harness for the future Python/I2P seam.

The prototype checks:

```text
HELLO before SESSION CREATE
session before STREAM SEND
persistent destination does not drift
canonical WireFrame validates before send
payload/frame digests bind to the send step
reconnect preserves the same destination
```

The purpose is to keep SAM/I2P assumptions typed before live router behavior adds latency, partial failure, and implementation differences. Streaming remains the safest first assumption; datagram-primary behavior stays out of the hot path until real routers can be tested.
