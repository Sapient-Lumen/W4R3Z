# Rev0025 branch reconciliation audit

The workspace contained two nonzero rev0024 branches:

- `PoliceMisconduct-rev0024-2026.05.26.02.52-identityoffice-mergeabstention-unmergereceipts-refactoraudit.zip`
- `PoliceMisconduct-rev0024-2026.05.26.02.58-civiliandignity-familyconsent-privacyaudit-gatehard.zip`

The identity branch was the user-visible linked head. The civilian/family-dignity branch existed in the workspace and contained substantive unique files. Rev0025 reconciles them by using the identity branch as base, copying civilian-unique paths, preserving conflicting branch receipts under rev0025 refactor paths, and recording the collision instead of hiding it.

Counts:

- Identity-unique files: 50.
- Civilian-unique files copied: 53.
- Common files with different hashes: 22.
- Destructive moves: 0.

This is intentionally a non-destructive merge. Root namespace sprawl remains mapped, not rearranged.
