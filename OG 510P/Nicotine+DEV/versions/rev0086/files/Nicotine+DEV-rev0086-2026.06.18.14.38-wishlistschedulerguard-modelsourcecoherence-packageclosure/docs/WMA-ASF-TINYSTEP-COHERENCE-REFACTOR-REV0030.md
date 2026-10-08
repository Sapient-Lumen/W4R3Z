# WMA-ASF-TINYSTEP coherence refactor — rev0030

This pass keeps **WMA-ASF-TINYSTEP-01 / U-273** narrow. The shared theme is semantic parser progress, but the fix point and trust boundary are different from the other media-parser and network-budget rows.

## Canonical packet

```text
WMA-ASF-TINYSTEP-01:
  U-273 = canonical lead.
```

## Kept separate

```text
Ogg continuation parser / U-124:
  Media-parser adjacent, but the invariant is continuation-packet accumulation,
  not ASF object-size progress. Keep as a possible next target.

MP4/M4A atom leaf memory / U-125:
  Media-parser adjacent, but the invariant is atom payload materialization and
  memory budget, not an under-header relative seek.

FLAC STREAMINFO block validation / U-127:
  Media-parser adjacent, but the invariant is fixed-length block validation
  after an advertised block length.

ID3v2 advertised frame length / U-138:
  Media-parser adjacent but lower-value/public-ambiguous; do not use it to
  inflate U-273.

SHARE-SCAN-CACHE-01 / U-248:
  Same local share-scanner area, but cache provenance and mtime reuse are not
  parser progress.

FILE-ATTRIBUTE-BUDGET-01 / U-199:
  Same semantic-budget idea, but U-199 is network result/list parsing and a
  per-file metadata-count loop. U-273 is local media metadata parsing and ASF
  object-size validation.

UNCOMPRESSED-MESSAGE-CAPS / U-02 / 3.3.11 RC context:
  Broad network-message byte caps are not a substitute for local media parser
  object-progress checks.
```

## Compatibility guardrails

```text
Avoid:
  - treating U-273 as a broad share-scanner DoS umbrella;
  - merging all media-parser rows into one vague parser-hardening packet;
  - promoting solely because a different package has an ASF zero-size advisory;
  - changing normal WMA metadata parsing without regression tests.

Prefer:
  - one WMA/ASF-specific minimum-object-size invariant;
  - tests for malformed under-header object sizes and valid minimum unknown
    objects;
  - source-line proof in each active source lane;
  - conservative public-overlap language that distinguishes direct overlap from
    class adjacency.
```

## Strict decision

```text
Verified current behavior: yes.
Hard-search status: candidate no direct exact public match found; public source
  shape and ASF parser-class adjacency found.
Strict promotion: no.
Reason: local parser-step amplification with bounded/proportional work and no
  stronger consequence than the current strict candidates.
```
