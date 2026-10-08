# Archive size control should cite one compaction-gap receipt

A hotspot receipt says **where** the archive is largest. A compaction-candidate receipt says **which of those families are already safe to cite instead of retaining again**.

There is still one operator question left after those two surfaces: **which large hotspot families are *not* yet safe to compact only because they still lack a durable non-report handle?**

A tiny compaction-gap receipt answers that by listing only the top hotspot families that still have zero durable backing elsewhere in the archive. Those are the families where the next small retained addition should usually be **one handle-unlocking note or snapshot**, not another full report pair.

That matters because archive growth is now mostly internal report fanout. When a family is already in the hotspot table but still has no durable handle, the best next byte-saving move is often to mint the smallest citation surface that unlocks future compaction there.

The receipt should therefore record, for each blocked hotspot:

1. the family name and byte cost,
2. whether it is a paired JSON+MD family,
3. confirmation that it still has zero durable backing handles,
4. the smallest recommended handle kind that would unlock citation-first trimming,
5. and one sentence describing the next minimal unlock move.

That keeps archive shaping progressive instead of repetitive: first identify the hotspot, then cite the already-safe trim candidates, then expose the remaining handle gaps so the next retained addition unlocks future savings instead of widening the archive again.
