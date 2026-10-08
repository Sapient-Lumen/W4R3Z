# Meta note — rev0410 thematic tags in the archive index

rev0410 adds lightweight thematic tags to `ARCHIVE_INDEX.json` so future continuation bundles are easier to merge, diff, and cluster without relying only on filenames.

This is intentionally small rather than over-engineered:

- tags are inferred from stable keyword rules over each note’s slug, title, and one-line thesis,
- the goal is merge hygiene and retrieval, not a perfect ontology,
- the tags make it easier to see that notes about notice, appeals, evidence, accessibility, incidents, procurement, and interoperability belong to recurring archive threads.

This helps later comparisons ask higher-value questions such as:

- which revisions deepened contestability,
- which notes touch accessibility or equivalent alternatives,
- which notes are about lifecycle evidence rather than deployment policy,
- where a full historical archive should add backlinks during merge.
