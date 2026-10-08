# Metrics veil observability pressure

Operator feedback is necessary for garden nodes, but metrics are also a metadata leak.  `metricsveil.py` treats metric emission as a local protocol boundary.

The first guard rejects:

- raw 32-byte / 20-byte hex identifiers in labels;
- `.b32.i2p` destination-looking labels;
- label values that exceed a small byte budget;
- unknown labels;
- scope mismatch;
- high-cardinality label growth.

Accepted metrics are stored as veiled events: label values are digested under a domain separator and raw labels do not leave the local guard.  This does not claim perfect telemetry privacy.  It is a pressure surface that prevents the easiest operator-dashboard mistakes from becoming part of the future protocol culture.
