# Cube hygiene — rev0031

## Hygiene pass

The rev0031 packaging pass pruned generated Python and pytest cache directories from the cube before building the zip.

The large upstream source bundle remains external. The cube records source-lane hashes, line traces, and reproducer evidence, but does not embed `source-trees/`, `git-full/`, or the large `Nicotine-source.zip` contents.

## Refactor/audit focus

The local media-parser cluster was re-audited after adding U-124:

```text
U-124 / Ogg continuation accumulation:
  verified in rev0031; canonical Ogg packet assembly budget packet.

U-273 / WMA-ASF tiny-step:
  verified in rev0030; kept separate as ASF object-size progress.

U-125 / MP4-M4A atom memory:
  held as the next probable media-parser target.

U-127 / FLAC STREAMINFO validation:
  held behind MP4 unless re-scored.

U-138 / ID3v2 frame-size rows:
  kept lower/public-ambiguous after TinyTag's public ID3 SYLT advisory adjacency.

U-248 / share-scan cache provenance:
  not merged with parser packet budgets.

U-199 / network file-attribute budgets:
  not merged with local media metadata parsing.
```

## Packaging checks

The final zip should have one root directory, no generated cache directories, and no embedded large upstream source tree.
