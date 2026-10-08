# MP4-M4A-ATOM-BUDGET coherence refactor — rev0032

This pass keeps **MP4-M4A-ATOM-BUDGET-01 / U-125** narrow. The shared theme is local media-parser budgeting, but the concrete invariant is MP4 atom-leaf materialization before fixed-prefix duration/header parsing.

## Canonical packet

```text
MP4-M4A-ATOM-BUDGET-01:
  U-125 = canonical lead.
```

## Kept separate

```text
OGG-CONTINUATION-ACCUM-01 / U-124:
  Media-parser adjacent, but the invariant is Ogg page-lacing continuation
  accumulation before packet yield. U-125 is MP4 atom-size-driven leaf reads.

WMA-ASF-TINYSTEP-01 / U-273:
  Media-parser adjacent, but the invariant is ASF object-size progress and an
  under-header relative seek. U-125 is not an object progress/tiny-step issue.

FLAC STREAMINFO block validation / U-127:
  Media-parser adjacent and still queued behind MP4, but the invariant is a
  fixed-length STREAMINFO block advertised-size check, not MP4 atom traversal.

ID3v2 advertised frame length / U-138:
  Media-parser adjacent but public-ambiguous after TinyTag's public ID3 SYLT
  parser advisory. Keep archived unless re-scored.

SHARE-SCAN-CACHE-01 / U-248:
  Same local share-scanner area, but cache provenance and mtime reuse are not
  parser atom materialization.

FILE-ATTRIBUTE-BUDGET-01 / U-199:
  Same budget theme, but U-199 is network result/list parsing and a per-file
  metadata-count loop. U-125 is local media metadata parsing.

UNCOMPRESSED-MESSAGE-CAPS / U-02 / 3.3.11 RC context:
  Broad network-message byte caps are not a substitute for local MP4 parser
  atom-leaf budgets.
```

## Cluster audit/refactor note

The `share-scanner-media-parser` cluster also contains rows that are not actually media parser rows:

```text
U-229 chat-history popover log-tail budget
U-219 optional Anti Shout plugin remote-line transform budget
U-89  private-chat logging file/open-handle fanout
U-73  terminal control-sequence logging
```

Rev0032 did not rewrite historical cluster labels, but it did mark these rows as **cluster-label hygiene only** in the queue delta/coherence table. They should not be used to justify or merge the MP4/Ogg/WMA/FLAC/ID3 parser sequence. If revisited, they belong in UI/log/plugin resource-budget batches.

## Compatibility guardrails

```text
Avoid:
  - treating all large MP4 atoms as invalid by definition;
  - merging all media-parser rows into one vague parser-hardening packet;
  - promoting based solely on local file indexing overhead;
  - breaking normal M4A/MP4 duration extraction.

Prefer:
  - one MP4-specific metadata atom-leaf budget or fixed-prefix streaming parser;
  - explicit tests for normal small mvhd/mp4a/alac leaves and over-budget leaves;
  - source-line proof in each active source lane;
  - conservative public-overlap language that distinguishes direct overlap from
    public source and parser-class adjacency.
```

## Strict decision

```text
Verified current behavior: yes.
Hard-search status: candidate no direct exact public match found; public source
  and MP4 parser-class adjacency found.
Strict promotion: no.
Reason: local parser memory budget with proportional-to-file work and no
  stronger consequence than the current strict candidates.
```
