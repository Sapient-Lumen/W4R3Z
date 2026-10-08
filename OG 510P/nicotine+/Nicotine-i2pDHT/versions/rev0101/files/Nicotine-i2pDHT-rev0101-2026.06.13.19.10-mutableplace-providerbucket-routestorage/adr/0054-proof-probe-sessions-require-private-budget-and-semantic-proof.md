# ADR 0054 — Proof-probe sessions require both privacy budget and semantic proof

A provider proof response is not enough by itself. It must be evaluated against the probe plan that caused it, including real probes, decoys, raw-key exposure, family caps, and useful refusals.

Decision: add `proofprobe.py` and reject/continue/quarantine sessions that violate metadata or semantic pressure before accepting provider availability.
