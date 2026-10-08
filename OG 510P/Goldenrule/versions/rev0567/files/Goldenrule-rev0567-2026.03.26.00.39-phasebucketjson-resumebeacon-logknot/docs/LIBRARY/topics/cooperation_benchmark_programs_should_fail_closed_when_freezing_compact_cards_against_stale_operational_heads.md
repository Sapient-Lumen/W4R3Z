# Cooperation benchmark programs should fail closed when freezing compact cards against stale operational heads

Once a cooperation-card lineage has more than one retained claim-ready version, a freeze command can mean two different things: bind some historical card for archival review, or mint the **current citation head** inheritors should use now.

Keep that second action explicit and guarded.

## What to do

When freeze is intended to mint or refresh the current citation-ready head of a lineage:

1. require the input card to still be the unique current claim-ready operational head;
2. fail closed if the lineage has branched, has no unique operational head, or has advanced to a newer tip first; and
3. retain the matched guard context in the freeze receipt so future inheritors can tell the freeze was performed against the expected live head rather than against memory.

## Why this matters

Without a guard, a reviewer can innocently freeze an older retained card after the lineage has already moved.
That does not corrupt the older receipt, but it does let citation work proceed under a stale assumption.
A tiny compare-and-set style head guard is the smallest durable fix because it preserves the existing compact card / freeze / head-register design while making citation-intended freeze actions fail closed on drift.
