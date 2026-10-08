# rev0031 — scopefence-obligationdebt-decaymesh

This revision attacks a join-boundary failure: one local success accidentally authorizes a different local step.

New surfaces:

- `scopefence.py` — exact signed scope/object/request/purpose claims before evidence can be joined.
- `obligationdebt.py` — explicit proof debt left behind by accept-with-watch or convenience decisions.
- `decaymesh.py` — typed evidence aging that preserves hard negatives while dropping stale convenience memory.
- `auditmesh.py` — current-path audit/refactor fold preserving rev0030 predecessor checks.

Strong sentence: **valid local evidence is not portable across scope boundaries.**

Nonclaim: no live I2P/SAM, no production DHT, no production authorization or persistence protocol.
