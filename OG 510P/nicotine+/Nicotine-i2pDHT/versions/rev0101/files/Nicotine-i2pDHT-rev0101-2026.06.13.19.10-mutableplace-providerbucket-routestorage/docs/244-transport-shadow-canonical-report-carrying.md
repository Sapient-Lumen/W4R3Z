# Transport shadow canonical report carrying

`src/i2p_dht_lab/transportshadow.py` creates tiny signed report frames before any live SAM/I2P transport exists.

It binds:

- a shadow payload kind,
- a report digest,
- a subject digest,
- a time window,
- a signed `WireFrame`,
- kind-specific flags.

The validator rejects payload tampering, parse failure, report-digest mismatch, and frame-kind/payload-kind mismatch. This does not define the production wire protocol. It gives the cube a pressure-tested seam for carrying report digests before live transport hides basic canonicalization mistakes.
