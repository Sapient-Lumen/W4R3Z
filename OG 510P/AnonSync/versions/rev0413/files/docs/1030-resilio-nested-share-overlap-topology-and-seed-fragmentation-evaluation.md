# Resilio nested-share overlap topology and seed-fragmentation evaluation

## Why this pass exists

The archive already had strong language for bind outcomes, destination worlds, namespace blockage, subject lineage, and route basis.
What it still did not own with one explicit current Resilio memo was the narrower but highly practical seam:

> if I separately share a child folder that lives inside an already shared parent, what exactly exists now, who can seed whom, how much extra work did I create, and how far can child edits travel?

Current official Resilio docs are still unusually candid here.
They still say all of the following in one FAQ entry:

- a nested child folder can be shared separately, but both parent and child must have `Read & Write` or `Owner` permissions
- both parent and child must have `Selective Sync` disabled
- parent and child are treated as separate sync folders, so the overlapping host does additional indexing and rescanning work
- peers that only have the parent folder do **not** seed data to peers that only have the child folder
- changes made by a child-only peer can still reach a parent-only peer by passing through the overlapping host, because the child is also a subfolder inside the parent share on that host

That combination is exactly the kind of thing AnonSync should study carefully but not clone directly.
Resilio is telling the truth about the graph, but the truth is still too easy to misread if the operator is standing in a filesystem hierarchy and not in the actual sync-subject graph.
A person can very reasonably think `child inside parent` means one share with a narrower audience or one simple derivative view.
Current official Resilio behavior is more subtle:

- there are **two** sync subjects
- one host may become a **bridge** between them
- direct seeding horizons differ by subject membership, not by apparent path containment
- overlap imposes extra local work on the bridge host
- child edits may leak outward to parent-only peers through the bridge even though parent-only peers cannot seed child-only peers directly

That is a strong non-clone signal.
The distinctions are useful, but AnonSync should refuse any interface where nested overlap remains an FAQ curiosity rather than a first-class topology review.

## Hard product decisions locked by this pass

1. Overlap is a first-class topology object, not an incidental folder relationship.
2. A child path inside a parent path may never silently imply one audience, one seed horizon, or one workload.
3. The bridge host that belongs to both subjects must be shown explicitly whenever it can relay edits between otherwise disjoint peer sets.
4. Overlap is blocked by default unless the operator explicitly accepts duplicate indexing / rescanning cost and the carried-edit consequence.
5. Nested overlap receipts must preserve both the strongest safe sentence and the blocked stronger sentence such as `child edits stay only within the child audience`.
