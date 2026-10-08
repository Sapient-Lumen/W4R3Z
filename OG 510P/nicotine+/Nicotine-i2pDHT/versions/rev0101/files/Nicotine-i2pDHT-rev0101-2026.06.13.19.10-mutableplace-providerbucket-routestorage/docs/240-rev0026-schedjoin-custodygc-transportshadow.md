# rev0026 — schedjoin / custodygc / transportshadow

rev0026 joins boundaries that were intentionally separate in earlier revisions:

- capability-gated dispatch must still survive queue and garden scheduling pressure;
- evidence GC must normalize custody, tombstone, witness, and revocation pressure before soft evidence can bury hard negative evidence;
- partition merge must wait for route and witness pressure before committing a locally merged mutable epoch head;
- report digests need a canonical shadow transport before live SAM/I2P makes framing bugs noisy.

The core rule for this revision:

```text
A joined boundary is where local safety invariants most often leak.
```

This is still a no-network Python design cube. It does not implement live I2P/SAM transport, a production DHT, or production scheduling, custody, evidence, partition, or wire protocols.
