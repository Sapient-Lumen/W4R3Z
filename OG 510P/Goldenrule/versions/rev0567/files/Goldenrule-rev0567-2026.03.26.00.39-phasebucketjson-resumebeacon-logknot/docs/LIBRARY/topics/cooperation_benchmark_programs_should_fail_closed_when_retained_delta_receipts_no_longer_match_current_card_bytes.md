# Cooperation benchmark programs should fail closed when retained delta receipts no longer match current card bytes

Once compact-card delta receipts start carrying lineage meaning for citation or inheritance, they stop being mere convenience diffs and become part of the retained basis for “what changed” between claim-ready versions.

Keep that basis current.

## What to do

When a retained delta receipt is used as lineage evidence for citation or handoff:

1. verify that the predecessor and successor card bytes still match the receipt’s recorded hashes;
2. fail citation / handoff surfaces closed if either side has drifted in place;
3. repair the lineage with one fresh compact delta receipt bound to the current predecessor and successor card bytes; and
4. surface the drift as an actionable review item rather than letting inheritors silently rely on stale ancestry evidence.

## Why this matters

A delta receipt that no longer matches the cards it names can still look structurally plausible while misdescribing the actual retained basis.
That is exactly the kind of archive ambiguity compact-card lineage machinery is supposed to remove.
The smallest durable fix is to treat retained deltas the same way guarded freeze treats citation heads: current enough or explicitly drifted, never silently assumed.
