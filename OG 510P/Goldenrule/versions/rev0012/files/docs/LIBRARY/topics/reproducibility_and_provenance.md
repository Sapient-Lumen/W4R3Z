# Reproducibility and Provenance

Why this matters:
- A lab without provenance becomes a vibe machine.
- Concord’s entire promise is: “results are artifacts; artifacts are diffable; claims are scoped.”

What Concord should build (concrete):
- Keep strengthening attest/verify:
  - artifact tree hashing (done),
  - optional engine build provenance (git HEAD, binary hash) (done),
  - export bundles that are tamper-evident (done for public).
- Push determinism discipline into every new feature (noise, termination, strategy execution).
- Maintain clear boundaries between:
  - resumable run dirs (mutable working state),
  - shareable exports (public/internal).

Docs + code touchpoints:
- `docs/PROVENANCE.md`
- `grlab/attest.py`, `grlab/verify.py`, `grlab/exporter.py`
- `docs/DETERMINISM.md`

