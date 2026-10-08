# Rev644 — guard the recent TODO handoff trail

The top of `TODO.md` is the archive's most human-scanned handoff lane. Recent Micromax
revisions intentionally use a calm rhythm there:

- `RevN note: ...`
- `Latest tiny landing (revN): ...`
- `# TODO (revN)` with the completed checklist

That structure matters because future humans and LLMs often read the top TODO history
first, before they inspect deeper docs or code. A stale or delayed checklist heading is
small, but it teaches the wrong revision story in exactly the place that is supposed to be
most trustworthy.

Rev644 tightens that seam in two ways:

- repairs the recent checklist-era trail so the visible blocks are back to one matching
  `note -> landing -> checklist` rhythm
- teaches `tools/mxcontext.py` to parse those recent interstitial handoff blocks and warn
  when a heading is missing its matching preamble or when orphan rev preambles are stacked
  in front of a later heading

The goal is not more bureaucracy. The goal is that a future handoff can skim the top of
`TODO.md`, run `python tools/mxcontext.py --check`, and trust that both tell the same
boring story about what revision they are really looking at.

## Validation

- `pytest -q tests/test_mxcontext.py tests/test_mkrevzip.py`
- `python tools/mxcontext.py --check`
