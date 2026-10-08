# FLAC ID3v2 prelude coherence refactor — rev0034

## Purpose

Rev0034 adds U-139 as a verified audited-backlog packet while correcting the media-parser cluster boundary. The key distinction is that **leading ID3v2 prelude traversal** is not the same issue as native FLAC STREAMINFO block-size validation and not the same as the general ID3v2 frame-size row.

## Decisions

```text
FLAC-LEADING-ID3V2-DURATION-PRELUDE-01 / U-139:
  canonical rev0034 packet.
  Stable/3.3.x parse/apply mapped leading ID3v2 text frames despite tags=False;
  master propagates tags=False and avoids mapped text-frame application.

FLAC-STREAMINFO-BLOCK-BUDGET-01 / U-127:
  keep separate.
  Native FLAC metadata-block length validation for the fixed 34-byte STREAMINFO
  duration record.

U-138 / general ID3v2 advertised-frame materialization:
  keep adjacent but separate.
  U-139 demonstrates a leading-FLAC ID3v2 subcase on stable/3.3.x; it does not
  fully prove or replace the standalone MP3/ID3 row.

MP4-M4A-ATOM-BUDGET-01 / U-125:
  keep separate.
  MP4 atom-leaf traversal and materialization is not FLAC prelude parsing.

OGG-CONTINUATION-ACCUM-01 / U-124:
  keep separate.
  Ogg page-lacing/packet assembly differs from ID3v2 envelope traversal.

WMA-ASF-TINYSTEP-01 / U-273:
  keep separate.
  ASF object-size progress is not tags=False propagation.

U-248 / share-scan cache provenance and U-199 / network file-attribute budget:
  keep separate due different trust boundary and fix shape.
```

## Lane-split correction

The rev0034 audit prevents a false all-lane claim:

```text
3.3.10 / 3.3.x:
  full mapped ID3v2 text-frame body read and field application in duration-only
  leading-FLAC path.

master:
  no mapped text-frame field application when tags=False and no full large body
  read for the mapped TIT2 frame in the witness; still parses/probes the leading
  ID3 envelope to reach native FLAC duration metadata.
```

## Queue hygiene

Rows U-229, U-219, U-89, and U-73 remain historical cluster-label drift under the broad `share-scanner-media-parser` cluster and are **not** media-parser merge inputs. They belong in future UI/log/plugin resource-budget or logging-sanitization batches.

## Result

```text
U-139 is now verified audited backlog.
No strict/front-lane promotion.
No production-ready disclosure text.
The coherence-cluster linter was rerun and reported no structural coherence-map errors.
```

Evidence: `evidence/rev0034-coherence-cluster-linter.txt`.
