# Release-note overlap coherence refactor — rev0045

Rev0045 adds an overlap pass against the 3.3.11 RC release-note/source context. The aim is to prevent stale or duplicate filing, not to inflate the queue.

## Refactor decisions

### Broad network-message size caps are not parser-invariant replacements

The 3.3.x/master source lanes include broader uncompressed message limits, including `MAX_INCOMING_MESSAGE_SIZE_*` in `slskproto.py` and a `FileSearchResponse` decompression cap. Those caps are important, but they do not express the two narrower parser invariants captured by the cube:

```text
SEARCH-RESP-PARSE-BUDGET-A: reject implausible username prefixes before materializing username_len + 4 bytes.
SEARCH-RESP-PARSE-BUDGET-B: bound accepted public+private result rows before constructing result objects.
```

The rev0045 smoke gates still observe the fixed regressions failing on current branch/master lanes before applying the cube patch.

### Upload-spoofing release-note wording does not retire U-123

The master NEWS wording mentions file uploads and spoofed users. U-123 is the download-side same-user/same-token active-owner collision plus identity-aware cleanup. Treat this as identity-adjacent, not exact overlap, unless a newer source audit maps the same code-level invariant.

### Username-identity release-note wording does not retire PB-01

The master NEWS wording about peers being told our username is identity-adjacent. PB-01 is specifically about established-primary replacement and secondary promotion across P/D/F connection handling. The fixed regression still fails on current archived lanes before the selected guard.

### Distributed-search release-note wording does not retire search-response source gates

The release-note text about distributed search is broad. The cube's search-response rows are token/source admission and parser-budget invariants. They remain split and retained.

## Data

Structured overlap decisions are stored in:

```text
data/rev0045_release_note_overlap_rescore.csv
data/rev0045_release_note_overlap_rescore.json
```
