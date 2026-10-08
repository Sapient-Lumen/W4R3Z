# ADR 0048 — Wire transcripts before live SAM

Decision: canonical signing and transcript hashing should be fixture-tested before live transport.

Rationale: if payload canonicalization drifts, later SAM/I2P debugging will confuse network failure with signature failure.

Status: toy-tested.
