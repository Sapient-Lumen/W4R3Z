# Cube hygiene — rev0032

## Hygiene pass

The rev0032 packaging pass pruned generated Python and pytest cache directories from the cube before building the zip.

The large upstream source bundle remains external. The cube records source-lane hashes, line traces, and reproducer evidence, but does not embed `source-trees/`, `git-full/`, or the large `Nicotine-source.zip` contents.

## Refactor/audit focus

The local media-parser sequence was re-audited after adding U-125:

```text
U-125 / MP4-M4A atom leaf memory:
  verified in rev0032; canonical MP4 atom leaf materialization budget packet.

U-124 / Ogg continuation accumulation:
  verified in rev0031; kept separate as Ogg page-lacing continuation assembly.

U-273 / WMA-ASF tiny-step:
  verified in rev0030; kept separate as ASF object-size progress.

U-127 / FLAC STREAMINFO validation:
  next probable local media-parser target unless re-scored.

U-138 / ID3v2 frame advertised length:
  kept lower/public-ambiguous after TinyTag's public ID3 SYLT advisory adjacency.

U-139 / FLAC leading ID3v2 duration-only path:
  kept separate from the MP4 atom-leaf packet.

U-248 / share-scan cache provenance:
  not merged with parser packet/atom budgets.

U-199 / network file-attribute budgets:
  not merged with local media metadata parsing.
```

## Cluster-label hygiene

Rows U-229, U-219, U-89, and U-73 are currently under `share-scanner-media-parser` in the historical queue but are better treated as UI/log/plugin resource-budget rows. Rev0032 did not rewrite historical cluster fields, but the coherence table marks them as **not media-parser merge inputs**.

## Packaging checks

The final zip should have one root directory, no generated cache directories, and no embedded large upstream source tree.
