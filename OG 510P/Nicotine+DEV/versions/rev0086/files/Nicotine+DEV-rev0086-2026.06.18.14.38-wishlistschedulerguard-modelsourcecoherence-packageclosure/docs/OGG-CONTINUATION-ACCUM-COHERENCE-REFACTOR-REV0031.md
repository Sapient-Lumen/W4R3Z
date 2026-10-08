# OGG-CONTINUATION-ACCUM coherence refactor — rev0031

This pass keeps **OGG-CONTINUATION-ACCUM-01 / U-124** narrow. The shared theme is local media-parser budgeting, but the concrete invariant is Ogg continuation-packet assembly before metadata classification.

## Canonical packet

```text
OGG-CONTINUATION-ACCUM-01:
  U-124 = canonical lead.
```

## Kept separate

```text
WMA-ASF-TINYSTEP-01 / U-273:
  Media-parser adjacent, but the invariant is ASF object-size progress and an
  under-header relative seek. U-124 is Ogg lacing continuation accumulation.

MP4/M4A atom leaf memory / U-125:
  Media-parser adjacent and likely next, but the invariant is MP4 atom payload
  materialization, not Ogg page lacing.

FLAC STREAMINFO block validation / U-127:
  Media-parser adjacent, but fixed-length STREAMINFO validation differs from
  continuation-packet assembly.

ID3v2 advertised frame length / U-138:
  Media-parser adjacent but public-ambiguous after TinyTag's public ID3 SYLT
  parser advisory. Keep archived unless re-scored.

SHARE-SCAN-CACHE-01 / U-248:
  Same local share-scanner area, but cache provenance and mtime reuse are not
  parser packet assembly.

FILE-ATTRIBUTE-BUDGET-01 / U-199:
  Same budget theme, but U-199 is network result/list parsing and a per-file
  metadata-count loop. U-124 is local media metadata parsing.

UNCOMPRESSED-MESSAGE-CAPS / U-02 / 3.3.11 RC context:
  Broad network-message byte caps are not a substitute for local media parser
  packet assembly budgets.
```

## Compatibility guardrails

```text
Avoid:
  - treating page-spanning Ogg packets as invalid by definition;
  - merging all media-parser rows into one vague parser-hardening packet;
  - promoting based solely on local file indexing overhead;
  - breaking normal Vorbis/Opus/Speex/FLAC-in-Ogg metadata parsing.

Prefer:
  - one Ogg-specific metadata packet byte/page budget;
  - explicit tests for normal small headers and over-budget continuation chains;
  - source-line proof in each active source lane;
  - conservative public-overlap language that distinguishes direct overlap from
    public source and parser-class adjacency.
```

## Strict decision

```text
Verified current behavior: yes.
Hard-search status: candidate no direct exact public match found; public source,
  Ogg-spec, TinyTag advisory-class, and share-rescan-performance adjacency found.
Strict promotion: no.
Reason: local parser memory/copy budget with proportional-to-file work and no
  stronger consequence than the current strict candidates.
```
