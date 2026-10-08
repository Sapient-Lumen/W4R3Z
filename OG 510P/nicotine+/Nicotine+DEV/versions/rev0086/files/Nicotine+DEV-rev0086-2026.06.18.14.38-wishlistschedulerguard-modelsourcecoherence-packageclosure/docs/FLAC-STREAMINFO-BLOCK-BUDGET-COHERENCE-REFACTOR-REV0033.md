# FLAC STREAMINFO block-budget coherence refactor — rev0033

## Purpose

Rev0033 adds U-127 as a verified audited-backlog packet while keeping the local media-parser cluster coherent. The key refactor is to treat **STREAMINFO fixed-length validation** as its own FLAC parser invariant rather than folding it into other media-parser memory/progress rows.

## Decisions

```text
FLAC-STREAMINFO-BLOCK-BUDGET-01 / U-127:
  canonical rev0033 packet.
  Fixed 34-byte STREAMINFO duration record; advertised metadata block size is
  read before validation/bounding.

MP4-M4A-ATOM-BUDGET-01 / U-125:
  keep separate.
  MP4 atom-leaf materialization uses atom tree traversal and leaf parser calls.

OGG-CONTINUATION-ACCUM-01 / U-124:
  keep separate.
  Ogg continuation packet accumulation is a page-lacing/packet assembly issue.

WMA-ASF-TINYSTEP-01 / U-273:
  keep separate.
  ASF object-size under-header progress is loop progress and object header
  validation, not fixed STREAMINFO length validation.

U-139 / FLAC leading ID3v2 duration-only prelude:
  keep adjacent but separate.
  That row is about leading ID3v2 parsing before FLAC duration extraction, not
  the native FLAC STREAMINFO block length itself.

U-138 / ID3v2 parsable frames:
  keep lower/public-ambiguous and separate.
  ID3 frame-size materialization is a different parser and public-advisory space.

U-248 / share-scan cache provenance:
  previous local share-scanner packet; not a parser block-size issue.

U-199 / network file-attribute budget:
  previous semantic-count packet; different trust boundary from local media
  metadata scanning.
```

## FLAC-specific split

```text
STREAMINFO:
  fixed 34-byte record; duration, sample rate, channel, bit depth, sample count,
  and MD5 fields live here. Rev0033 targets this record only.

Vorbis comment / picture / cuesheet / seektable / padding / application blocks:
  variable-length FLAC metadata surfaces. They may need budgets elsewhere, but
  they should not be used to justify reading arbitrary STREAMINFO lengths before
  fixed-record validation.

Ogg FLAC mapping:
  related but not merged in rev0033. The rev0033 witness targets native .flac
  routing through TinyTag. Ogg-FLAC packet parsing should get its own proof if
  revisited.
```

## Queue hygiene

Rows U-229, U-219, U-89, and U-73 remain historical cluster-label drift under the broad share-scanner-media-parser cluster and are **not** media-parser merge inputs. They belong in future UI/log/plugin resource-budget or logging-sanitization batches.

## Result

```text
U-127 is now verified audited backlog.
No strict/front-lane promotion.
No production-ready disclosure text.
The existing coherence-cluster linter was rerun and reported no structural coherence-map errors.
Next local media-parser target: U-139 unless re-scored.
```


Evidence: `evidence/rev0033-coherence-cluster-linter.txt`.
