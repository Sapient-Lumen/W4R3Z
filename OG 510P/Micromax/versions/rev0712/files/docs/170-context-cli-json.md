# Rev229 — repo context should be machine-readable too

`tools/mxcontext.py` already gave humans and future LLMs a curated text snapshot of
this archive.

That was useful, but it still left one avoidable handoff gap:

- humans could read it quickly
- shell scripts/CI glue could *not* consume it directly
- future LLMs receiving an offline archive still had to scrape prose to discover
  the current revision, current priorities, and the small set of entry docs/code
  files worth opening first

Rev229 keeps the tool tiny but makes it more reusable:

```bash
python tools/mxcontext.py
python tools/mxcontext.py --json
python tools/mxcontext.py --check
```

## What the new modes do

- `--json` emits a stable machine-readable snapshot of:
  - current repo revision
  - latest top-of-README revision note
  - current high-leverage priorities parsed from `TODO.md`
  - curated docs/code entrypoints
  - useful commands
  - top-level repo tree
- `--check` fails if any curated path referenced by the context snapshot no longer
  exists, so the archive's “start here” breadcrumbs stay honest.

## Why this exists

Micromax keeps leaning into an **archive-first, inspectable-by-hand** workflow.
A tiny context helper is part of that story too.

The same archive that should be pleasant for a human to browse should also be
pleasant for:

- future LLMs
- tiny offline automation
- CI smoke checks
- ad hoc shell tooling during bring-up

So the right move is not a bigger indexing system; it is one small helper that
stays:

- obvious
- curated
- stable
- easy to validate

## Small companion polish

The Makefile now also exposes:

```bash
make context-json
make context-check
```

That keeps the human path (`make context`) and the machine path adjacent.
