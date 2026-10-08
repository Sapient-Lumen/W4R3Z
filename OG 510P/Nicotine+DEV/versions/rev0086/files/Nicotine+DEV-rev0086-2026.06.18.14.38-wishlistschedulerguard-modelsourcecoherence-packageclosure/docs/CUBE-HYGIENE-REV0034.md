# Cube hygiene — rev0034

Rev0034 keeps the compact cube discipline:

```text
- No large upstream source bundle embedded.
- Maintainer artifact only contains the U-139 reproducer and README.
- Generated Python/pytest caches are pruned before packaging.
- Source-lane evidence is recorded by commit/hash/line trace.
- The historical rev0006 coherence-map linter is rerun and captured.
```

## Media-parser refactor

The media-parser sequence now has clearer boundaries:

```text
U-127:
  native FLAC STREAMINFO fixed-block validation/materialization.

U-139:
  leading ID3v2 prelude before native FLAC marker in duration-only share scan.

U-138:
  general ID3v2 advertised-frame materialization; adjacent but not fully proven
  by U-139 and public-novelty weak.

U-125 / U-124 / U-273:
  MP4 atom leaves, Ogg continuation packet accumulation, and ASF object progress
  respectively; not merged with U-139.
```

Rows U-229, U-219, U-89, and U-73 remain historical cluster-label drift and are marked as non-media inputs in the rev0034 queue delta.
