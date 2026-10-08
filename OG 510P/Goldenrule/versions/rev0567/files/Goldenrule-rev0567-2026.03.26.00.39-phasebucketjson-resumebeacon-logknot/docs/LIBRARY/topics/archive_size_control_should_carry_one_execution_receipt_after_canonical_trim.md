# Archive size control should carry one execution receipt after canonical trim

Once a cited exact-file report frontier actually leaves the archive, retain one tiny execution receipt rather than relying on memory of what was removed.

Why this matters:
- the archive should not widen again just because a future inheritor cannot tell which compaction frontier already executed,
- the first live manifest after a real trim is a new frontier, not a replay of the old one,
- and package-size discipline is stronger when bytes reclaimed, removed paths, and the new leading hotspot are all cited in one compact place.

What to keep:
- the removed frontier as exact paths with source digests and durable handles,
- the pre-trim report-bucket and tree totals,
- the post-trim package / hotspot / manifest / rehearsal receipt digests,
- and one statement of what the next current frontier became.

What not to keep:
- do not retain the removed report pairs themselves,
- do not retain a second broad report family just to narrate the trim,
- and do not keep scratch-stage mirrors across the revision zip once execution has completed.
