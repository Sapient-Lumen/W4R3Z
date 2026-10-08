# rev0801 recovery basis

The requested predecessor archive named rev0800 was byte-preserved but
structurally incomplete. It contains 10 ZIP members, of which only two are
files: a 2,733-byte rev0799 fork-cleanup reproducer and a 148-byte manifest.
There is no implementation tree to continue from.

Rev0801 therefore uses the last complete source archive, rev0799, as its active
code parent. The incomplete rev0800 archive, exact digest, listing, and
reproducer remain in-tree as lineage evidence. This is a recovery fork over a
missing implementation revision, not a claim that rev0800's advertised changes
were present or validated.
