# Schemas

This directory holds machine-validatable schema packs for archive-defined artifact families.

Purpose:
- make already-earned machine-facing kernels more interoperable;
- keep example payloads from drifting silently;
- and give archive doctor/hygiene checks something stricter than prose to enforce.

Start with:
- `top-band-v0/README.md`
- `top-band-v0/schema-pack-hygiene-checks.json`

Working rule:
- schema packs come after packets, kernels, slices, contracts, witnesses, and fixtures;
- they validate JSON artifact families only;
- markdown/operator renderings may remain unschematized until the repo has a good reason to formalize them.
