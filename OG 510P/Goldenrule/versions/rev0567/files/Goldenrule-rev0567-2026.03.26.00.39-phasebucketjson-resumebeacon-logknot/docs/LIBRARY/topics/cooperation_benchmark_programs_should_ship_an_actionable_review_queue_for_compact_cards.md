# Cooperation benchmark programs should ship an actionable review queue for compact cards

Once the archive already has compact cards, freeze receipts, delta receipts, and lineage heads, one further operational gap remains: future inheritors still need one place to answer **what exactly requires action right now, and what command should I run locally to review or repair it**.

Keep that answer in one tiny generated review queue rather than in memory, logs, or scattered warnings.

## What to retain

For every retained compact cooperation-card family, publish one generated queue that can list:

1. latest operational heads that still need freeze before they can become citation heads;
2. frozen render/card surfaces whose retained hashes no longer match the stored freeze receipt; and
3. lineage topologies whose branching or head ambiguity blocks a simple citation answer.

For each queue item, retain stable reason codes plus the minimal review/apply commands and context paths needed for local repair.

## Why this matters

Inventories and head registers tell inheritors what exists and which tip is current.
They do not by themselves tell operators what to do next.
An actionable review queue is the smallest durable fix because it reuses the standing compact artifacts and simply translates their warning surfaces into explicit local maintenance work.
