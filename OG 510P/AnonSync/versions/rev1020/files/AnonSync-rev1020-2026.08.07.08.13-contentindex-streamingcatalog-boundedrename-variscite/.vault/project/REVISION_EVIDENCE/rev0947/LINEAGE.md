# Rev0947 lineage

Rev0947 descends from the exact uploaded rev0946 archive:

`AnonSync-rev0946-2026.07.30.01.32-capacitycontract-prefixstarvation-indexroadmap-amberlattice.zip`

Parent SHA-256:

`8dab57663134f72fb7209756fd41d98205ba01d184b74a40ef49641c3d10c39d`

The parent archive passed its own wrapper-aware release verification and was
extracted as the immutable comparison basis. Rev0947 changes ten active files in
the shipping folder observation/reconciliation lane and its tests/tools. The
exact unified patch is retained in
`REVISION_EVIDENCE/rev0947/SOURCE_DIFF_rev0946_to_rev0947.patch`.

Two internal prototypes were inspected during development: a cursor-only form
and a durable authenticated epoch-journal form. The latter is the retained
source because it preserves deletion authority across restart. The cursor-only
prototype and transient build directories are not packaged.

All reported GCC and Clang results are bound to the active hidden project path by
`CMAKE_HOME_DIRECTORY`. Generated build output, Python caches, VCS metadata, and
symlinks are excluded from the release package.
