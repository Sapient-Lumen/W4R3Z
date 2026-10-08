# Meta 0412 — Release-lineage index note

This revision adds a generated `RELEASES.json` file and a small builder script so the continuation snapshot can be merged back into a larger corpus with less guesswork about which notes arrived in which compact release.

Why this matters:

- previous bundle metadata was strong at the file and note level but weaker at the release level,
- manual comparison across compact revisions is easy for humans but annoying for tooling,
- future merge or diff workflows benefit from a machine-readable list of revision headings, dates, codenames, and carried note groups.

The new release index is deliberately lightweight. It is not a package manager or full historical truth source. It is a continuity aid for comparison, merge, and audit tasks in small archive snapshots.

