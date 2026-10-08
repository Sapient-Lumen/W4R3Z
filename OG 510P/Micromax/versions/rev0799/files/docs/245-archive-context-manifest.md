# Rev303 — every archive should carry one tiny context manifest

`tools/mxcontext.py` already gave humans and future LLMs a compact repo snapshot.

That helped while the tree was unpacked, but one practical offline handoff problem was
still annoying:

- standard-named release zips did not carry that context *inside* the archive
- future humans/LLMs had to unpack the tree and rerun helpers before they could ask
  basic questions like "what rev is this?" or "what docs/code should I open first?"
- the packaging path did not check whether TODO/README rev breadcrumbs still agreed

Rev303 keeps the archive workflow small, but closes that gap.

```bash
python tools/mkrevzip.py --tag archive-context-manifest-mapotter
python tools/mkrevzip.py --tag archive-context-manifest-mapotter --stamp 2026.03.18.16.20
python tools/mxcontext.py --json
python tools/mxcontext.py --check
```

## What is new

Every standard-named Micromax archive now also contains one generated top-level file:

- `MICROMAX-CONTEXT.json`

That manifest carries two small pieces:

1. `archive` metadata
   - archive filename
   - tag
   - timestamp / timezone
   - manifest path inside the zip
   - creating tool path
2. `context`
   - the same curated `mxcontext --json` payload
   - current rev and latest note
   - current priorities
   - key docs / code / commands
   - path checks
   - compact portability snapshot
   - revision-source health for TODO / README breadcrumbs

Rev303 also tightens the repo-context helper itself:

- `mxcontext --json` now exposes `revision_sources`
- `mxcontext --check` now fails on revision warnings as well as missing paths
- `mkrevzip.py` now supports deterministic `--stamp ...` for tests and repeatable packaging demos

## Why this is the right size

Micromax still does **not** want a heavy packaging/indexing system.

The archive-first workflow works best when the first answer is tiny and durable:

- the zip stays a plain zip
- the manifest stays JSON
- the same curated context is reused instead of invented twice
- revision breadcrumbs get one honest validation pass before release

So the right move is not a larger release database. It is one tiny file that ships
with the archive and points at the existing truth.

## Focused validation

Rev303 focused validation covered:

- `tests/test_mxcontext.py`
- `tests/test_mkrevzip.py`
