# Repository hygiene and scope audit

The verified parent and rev0872 each contain 337 files in the verifier's active
v2 projection. Exactly ten active files differ; there are no active additions
or removals. The delta is narrow: CMake registration commentary, two lease
files, two SQLite-owner files, two tests, and three structural/release tools.

An early projection detected three generated Python bytecode files under
`tools/__pycache__`. They were deleted, projection recomputed, and a final scan
confirmed no cache directories or bytecode. The release package must contain no
build tree, VCS metadata, object, static/shared library, executable, core dump,
Python cache, or symlink.

The clock remains a single bounded row instead of a growing observation log,
and it is kept outside evidence generations. This avoids a correctness fix
turning into unbounded storage or gratuitous replicated-history churn.
