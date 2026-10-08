# AnonSync rev0874 lineage

Rev0874 descends from the verified archive:

`AnonSync-rev0873-2026.07.21.11.00-retryprovenance-exactobservation-v4migration-legacytruthseal.zip`

Parent archive SHA-256:

`654b389740e14a2d5890caeada3b4fde237accf545af1e16f90fcf024cdfd729`

The current verifier passed the parent archive at 26/26 ZIP checks and its
extracted canonical `AnonSync/` root at 22/22 directory checks. Those reports and
the exact parent hash are retained in `lineage/`.

`SOURCE_DIFF_rev0873_to_rev0874.patch` applies to the parent source. Replay was
checked against the v2 active implementation projection: all 342 active paths
and bytes match the candidate exactly, totaling 18,932,565 bytes with SHA-256
`d4d701e97413d599a37f97e882d1f4469872713fa1da2c9c51921048171038f8`.
The content replay scope is explicit; generated evidence, release metadata, and
POSIX extraction-mode normalization are outside that byte projection.

Relative to rev0873's active projection, rev0874 adds five files, removes three,
and modifies eight, for sixteen active-path changes. The source handoff patch
also includes `README.md`, `OWNED_OUTBOX_CLOCK_AUDIT_rev0874.md`, and
`REVISION_NOTES_rev0874.md`, yielding nineteen patch paths in total.
