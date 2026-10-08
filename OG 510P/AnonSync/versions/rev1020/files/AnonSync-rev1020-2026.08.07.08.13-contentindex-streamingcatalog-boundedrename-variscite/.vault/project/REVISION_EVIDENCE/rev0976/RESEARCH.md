# Rev0976 research note

The retention boundary was compared with Git's grace-based prune warnings and cruft-pack retention, plus restic's read/write ordering and exclusive forget/prune lock. Those systems reinforce the same conclusion: a physical candidate set is not collection authority without complete live/transient roots, a durable mark, writer exclusion, grace/policy, quarantine/reobservation, restart repair, and final unlink revalidation.

Primary references:

- https://git-scm.com/docs/git-gc
- https://git-scm.com/docs/gitformat-pack#_cruft_packs
- https://restic.readthedocs.io/en/stable/100_references.html#read-and-write-ordering
- https://restic.readthedocs.io/en/stable/060_forget.html
