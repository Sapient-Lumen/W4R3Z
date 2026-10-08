# ADR 0060 — Explicit lookup transcripts before wire format

## Decision

Use transport-neutral lookup transcript objects before choosing final DHT wire behavior.

## Reason

Provider proofs, mutable-head observations, witness receipts, timeouts, useful refusals, and fast-window capture need a common local evidence language.  A wire format chosen too early would hide pressure decisions inside transport noise.

## Consequence

`lookuptranscript.py` records path families, timings, event kinds, payload digests, and deterministic transcript digests without claiming to be the network protocol.
