# Wire canonicalization before live transport

`wirecanon.py` is a transport-neutral envelope fixture.  It is not the production wire protocol.

The purpose is to force the DHT to answer basic questions before live SAM/I2P adds latency, retries, router differences, and partial failure:

- What exactly is signed?
- What payload digest is being committed to?
- What version is this message?
- How long is the frame valid?
- Is the payload too large for this lane?
- Can transcripts be reproduced byte-for-byte?

Frame kinds currently include node lookup, provider lookup, store record, custody challenge/proof, epoch head, repair offer, useful refusal, and witness receipt.

Canonical transcripts are used as design evidence.  They do not claim network reachability.
