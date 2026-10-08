# Rev0814 lineage

The exact source parent is `AnonSync-rev0812-2026.07.17.04.13-schemaattest-casefold-migrationseal-constraintprofile.zip` with SHA-256
`566a24efc959383546daf4bd261dc0d51c221059f0a9c1040dcc626e71f459c9`.

The parent ZIP passes 25/25 release-package checks when pinned to `rev0812`.
Its canonical extracted `AnonSync/` directory passes 21/21 checks. Rev0814 was
built from that exact extracted tree; no build output, stale worktree, or
third-party replacement was used as source.

## Intentionally absent rev0813

A prior handoff response named a rev0813 archive, but the sealing process failed
before an archive was created. No rev0813 ZIP exists in the workspace, it is not
a lineage parent, and no unverified rev0813 source was used. Rev0814 is therefore
a direct child of rev0812 and contains the recovered atomic-reset repair plus the
shared typed savepoint boundary and audits described in this revision.

The machine-readable record is `LINEAGE.json`; exact parent verifier output is
under `lineage/`.
