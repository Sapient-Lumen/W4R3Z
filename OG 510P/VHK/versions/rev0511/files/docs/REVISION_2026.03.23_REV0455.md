# Revision 0455 — flagship datacube becomes explicit

This revision turns the active i3/X11 product shape into an explicit control-plane contract instead of leaving it spread across long-form docs and helper descriptions.

## What changed

- Added `docs/FLAGSHIP_DATACUBE_2026.03.23.md` as the shortest repo-level statement of the current VHK lane.
- `control-plane.json` now carries a machine-readable `flagship_datacube` section.
- The generated stack README now tells operators and a private LLM that `control-plane.json` includes that datacube contract.
- `stack_state_json.sh` now mirrors `flagship_datacube` under `control_plane`, so the fused runtime snapshot keeps the same authority map without reopening the manifest.
- README and architecture docs now point to the new datacube note first instead of making callers rediscover the current boundary from scattered prose.

## Why it matters

The repo already had the right warm-runtime surfaces, but the active authority map was still implicit: runtime truth lived in one place, selected-macro truth in another, and source-vs-proof boundaries in long-form docs.

A private LLM and a human operator now get the same one-read answer to five recurring questions:

- is the resident lane healthy now?
- what is the sharpest next move for the selected macro?
- what file is authoritative to edit?
- should execution dispatch or direct-run?
- is existing proof still current?
