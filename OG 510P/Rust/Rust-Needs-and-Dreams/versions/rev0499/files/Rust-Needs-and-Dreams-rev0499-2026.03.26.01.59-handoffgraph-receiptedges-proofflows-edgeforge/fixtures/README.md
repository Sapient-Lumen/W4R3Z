## Current note (rev0488)
The top-band fixture corpus is now paired with a first **artifact schema pack** under `schemas/top-band-v0/`.
That means replay fixtures no longer name only the scenario inputs and expected checks; they now sit beside explicit JSON families that witness outputs can validate against.

# Fixture corpora

This directory holds **replay-oriented input corpora** for archive-maintained machine surfaces.

Current lanes:
- `cargo-report-pack-kit/` — earlier report-pack schemas and fixture scenarios.
- `portfolio-envelope-v0/` — portfolio-envelope hygiene fixtures.
- `top-band-v0/` — replayable kernel fixture packs for the current top-band kernels.

Interpretation rule:
- fixtures are **inputs plus expected checks**, not live operational truth;
- witnesses are **example outputs**;
- contracts are **surface commitments**;
- and fixtures should bind the other layers to real proving-ground scenarios instead of floating free as prose.
