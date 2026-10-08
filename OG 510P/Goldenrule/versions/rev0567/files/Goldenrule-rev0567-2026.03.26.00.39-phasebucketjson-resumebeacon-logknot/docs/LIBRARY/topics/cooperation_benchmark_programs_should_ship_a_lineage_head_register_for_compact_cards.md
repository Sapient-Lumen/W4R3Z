# Cooperation benchmark programs should ship a lineage-head register for compact cards

Once the archive already has a compact card inventory and delta-linked lineages, one further operational gap remains: future inheritors still need one place to answer **which retained card is merely latest in a lineage, which one is actually frozen for citation, and whether the lineage has branched into multiple competing tips**.

Keep that answer in one tiny generated head register rather than in memory or scattered prose.

## What to retain

For every retained cooperation-card lineage, publish one compact head register that records:

1. the lineage id plus the retained card ids and paths inside that lineage;
2. the root ids and tip ids implied by retained delta receipts;
3. the claim-ready tip ids that qualify as **operational heads**;
4. the frozen claim-ready tip ids that qualify as **citation heads**; and
5. any branch, ambiguity, or missing-freeze warnings that block a unique citation-ready head.

## Why this matters

An inventory can say what cards exist.
A freeze receipt can bind one card to one rendered view.
A delta receipt can say what changed between two cards.
But none of those alone answers the inheritor-facing question: **what should I cite right now for this lineage, and is that answer unique?**

A generated head register is the smallest durable fix because it reuses the standing card, inventory, freeze, and delta artifacts instead of widening them.
It also keeps a useful distinction explicit: the latest claim-ready tip can be a valid operational head before it is frozen, while the citation head is the smaller stricter object that has already been frozen and bound to a rendered review surface.
