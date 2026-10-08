# Fuzzwire generated malformed fixtures

`src/i2p_dht_lab/fuzzwire.py` is a tiny deterministic fuzz lane. It does not replace real fuzzing. It pins classes of malformed input that should fail before live transport makes errors noisy:

- non-canonical bencode;
- parser resource-limit violations;
- payload digest mismatch;
- expired wire frames;
- shadow report digest mismatch;
- report kind / frame kind mutation.

The current fixture generator spans `parseguard.py`, `wirecanon.py`, and `transportshadow.py`. The important design rule is that a signed outer frame is still not safe if the payload is malformed, stale, role-mismatched, or digest-mismatched.
