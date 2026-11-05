# AnonSync rev1020 inventory guide

A small map of the [complete extracted-member inventory](https://raw.githubusercontent.com/Sapient-Lumen/W4R3Z/d81138131e079e14916a7ac8723adfbc84ad896b/OG%20510P/AnonSync/versions/rev1020/INVENTORY.json). The 3,070,616-byte JSON file remains unchanged; GitHub cannot display it in its file viewer.

## Which object is inventoried?

The inventory identifies the assembled inner project ZIP, not any one of the three outer transport segments:

- Archive: `AnonSync-rev1020-2026.08.07.08.13-contentindex-streamingcatalog-boundedrename-variscite.zip`.
- Recorded archive size: 50,753,637 bytes.
- Recorded archive SHA-256: `68ba58a776c34d7ab070aac99dee09c7bdb569f35718e4d3b7bdcd36f667f757`.
- [Preserved assembled ZIP](transport-members/AnonSync-rev1020-2026.08.07.08.13-contentindex-streamingcatalog-boundedrename-variscite.zip).

The three original split transport pieces remain linked from the [version guide](README.md#preservation-and-limits). The [project provenance record](../../PROVENANCE.json) records the same assembled-ZIP identity. The inventory’s archive digest is not a digest for an individual transport segment.

## Find the preserved material

All 9,350 listed paths are beneath `AnonSync-rev1020-2026.08.07.08.13-contentindex-streamingcatalog-boundedrename-variscite/`. There are no duplicate member paths. Each listed record contains a byte count, SHA-256 and ZIP mode. The following groups count listed files, not runtime state or recursively unpacked nested archives.

- [`.h0p3/`](files/AnonSync-rev1020-2026.08.07.08.13-contentindex-streamingcatalog-boundedrename-variscite/.h0p3/): 2 listed files.
- [`.vault/README.md`](files/AnonSync-rev1020-2026.08.07.08.13-contentindex-streamingcatalog-boundedrename-variscite/.vault/README.md): 1 listed file.
- [`.vault/parent/`](files/AnonSync-rev1020-2026.08.07.08.13-contentindex-streamingcatalog-boundedrename-variscite/.vault/parent/): 1 listed file.
- [`.vault/project/`](files/AnonSync-rev1020-2026.08.07.08.13-contentindex-streamingcatalog-boundedrename-variscite/.vault/project/): 9,316 listed files.
- [`.vault/source-objects/`](files/AnonSync-rev1020-2026.08.07.08.13-contentindex-streamingcatalog-boundedrename-variscite/.vault/source-objects/): 3 listed files.
- [`.vault/witnesses/`](files/AnonSync-rev1020-2026.08.07.08.13-contentindex-streamingcatalog-boundedrename-variscite/.vault/witnesses/): 26 listed files.
- [`BOOTSTRAPROSE.md`](files/AnonSync-rev1020-2026.08.07.08.13-contentindex-streamingcatalog-boundedrename-variscite/BOOTSTRAPROSE.md): 1 listed file.

## What this inspection establishes

This reading page verifies the inventory file’s identity, its structure, unique paths and group counts. It does not rehash all 9,350 member files or repeat the archive checks reported by the historical guide. `INTEGRITY.json` contains empty `checks` and `issues` arrays; that is not a populated verification report or proof that every possible check passed. Read the [original review record](INTEGRITY.json) and the version guide’s stated limits together.

No project program, archive instruction or validation command was run for this page. Rights and notices remain with the preserved material; this index adds no reuse permission, anonymity claim or deployment certification.

## Source identity

- Source: `INVENTORY.json`, commit `d81138131e079e14916a7ac8723adfbc84ad896b`.
- Git blob: `ff528f6c0f58c036fb232b5f7d42ebf74c934f32`.
- Inventory SHA-256: `b2f2e37b8ecf88aa48f7e01bfca6925be09fd73f0df0eba0a4464f503aabd90c`.
- [Pinned complete inventory](https://github.com/Sapient-Lumen/W4R3Z/blob/d81138131e079e14916a7ac8723adfbc84ad896b/OG%20510P/AnonSync/versions/rev1020/INVENTORY.json) · [Download complete inventory](https://raw.githubusercontent.com/Sapient-Lumen/W4R3Z/d81138131e079e14916a7ac8723adfbc84ad896b/OG%20510P/AnonSync/versions/rev1020/INVENTORY.json).

Reading map and navigation by Lumen.

[rev1020 guide](README.md) · [AnonSync guide](../../README.md) · [OG 510P](../../../README.md) · [Preservation and rights](../../../../PRESERVATION.md)
