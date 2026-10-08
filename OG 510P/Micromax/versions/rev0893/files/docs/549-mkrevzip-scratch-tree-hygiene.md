# Rev608 - `mkrevzip` scratch-tree hygiene

## What changed

`tools/mkrevzip.py` now skips top-level hidden scratch/probe trees whose names
start with `.tmp`, for example:

- `.tmp_spotcheck`
- `.tmp_probe_plugins`
- `.tmp_check_opt`

Those paths are useful while evolving the repo, but they are not part of the
intentional archive handoff.

## Why it matters

Micromax release zips are meant to be boring, inspectable handoff artifacts for
future humans and LLMs. The archive already carried the real repo plus one fresh
`MICROMAX-CONTEXT.json` snapshot, but hidden scratch trees still made the zip
look noisier than the actual product surface.

This change keeps the packaging rule tiny and explicit:

- keep real source/docs/tests
- keep the generated context manifest
- drop throwaway hidden `.tmp*` scratch trees

## Scope

This is deliberately small packaging hygiene only:

- no runtime/editor/VM behavior changes
- no change to archive naming or manifest shape
- no new ignore database
- one extra top-level skip rule in `should_skip(...)`

## Focused validation

Rev608 focused validation covered:

- `tests/test_mkrevzip.py`
- manual `mkrevzip.py --tag ...` spot-check of the resulting zip contents
