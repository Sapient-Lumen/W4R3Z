# Archive size control should cite one compaction-candidate receipt

The hotspot receipt already tells the inheritor **where** retained growth is concentrated, but that still leaves an operator question unanswered: **which families are safe to compact first without reopening the whole archive to rediscover their meaning?**

A tiny compaction-candidate receipt answers that question by intersecting the current hotspot table with durable non-report handles that already survive elsewhere in the archive — for example library-topic notes, retained benchmark snapshots, or standing benchmark docs.

That matters because the dominant retained size risk is still internal report fanout, not external reading packs. If a large report family is already represented by one of those durable handles, the next session should usually cite that handle instead of carrying another paired JSON+MD surface nearby.

The receipt should therefore rank only the hotspot families that already have durable backing and record, for each one:

1. the family name and byte cost,
2. whether it is a paired JSON+MD family,
3. the durable backing handles that make it citation-safe,
4. a simple readiness class (`citation_ready_pair`, `artifact_backed_pair`, and so on),
5. and one sentence saying why the next inheritor can trim or avoid expanding that family first.

That keeps archive shaping evidence-based: first identify the hotspot, then identify the citation-backed trim candidates inside it, and only then decide whether any new retained report surface is still justified.
