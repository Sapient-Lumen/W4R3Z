# ADR 0032 — Do not clone IPNS; build history-aware mutable heads

Accepted for rev0009. IPNS is treated as a warning and research reference, not a protocol template. High-risk mutable heads should support previous-head digest linkage and local monotonic memory.

Consequences: some valid signed heads are rejected or flagged locally when they do not connect to known history. This is intentional.
