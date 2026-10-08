# ADR 0177 — Repair ACKs are evidence, not closure

Accepted for rev0066.

Repair ACKs get a separate ledger.  ACK, NACK, absence, mixed state, replay, and one-family monoculture are different local observations.  None closes duplicate conflict alone.
