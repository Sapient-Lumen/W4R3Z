# rev0015 worklog

- Focused on F-CONN-FRAME-01 / U-164 as queued from rev0014.
- Built a current-behavior probe for `FileTransferInit` and `FileOffset` partial fragments.
- Ran the probe across `github-tag-3.3.10`, `github-branch-3.3.x`, and `github-branch-master`.
- Strengthened the maintainer-style pytest witness to cover every split position: 1..3 for `FileTransferInit`, 1..7 for `FileOffset`, complete-frame controls, and wrong-token/wrong-offset resynchronization.
- Ran the pytest witness across all three lanes: **22 passed per lane**.
- Added source trace, public-overlap notes, machine-readable queue delta, and coherence refactor.
- Kept strict document at 3 report-candidates; did not promote U-164.
