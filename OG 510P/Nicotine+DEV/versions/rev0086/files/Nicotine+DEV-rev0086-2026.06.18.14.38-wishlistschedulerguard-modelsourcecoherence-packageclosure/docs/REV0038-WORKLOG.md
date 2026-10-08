# rev0038 worklog

1. Loaded rev0037 and followed the queued PB-01 strict/front target.
2. Re-read PB-01 rev0010/rev0011 docs and the existing 10-case current-behavior witness.
3. Source-traced the relevant `pynicotine/slskproto.py` anchors across `github-tag-3.3.10`, `github-branch-3.3.x`, and `github-branch-master`.
4. Wrote `test_peer_connection_primary_election_fixed_regression.py`, an 11-case fixed-behavior regression with compatibility baselines.
5. Ran the fixed regression against current source: 6 failed / 5 passed on all three lanes.
6. Prototyped the selected established-primary guard patch.
7. Ran the fixed regression against patched lanes: 11 passed on all three lanes.
8. Ran the old rev0011 current-behavior witness against patched lanes: 6 failed / 4 passed on all three lanes, confirming expected inversion while compatibility cases remain.
9. Added production report draft, selected fix skeleton, patch diff, evidence, public-overlap notes, queue updates, strict-promotion table, and coherence refactor.
10. Packaged the compact cube without upstream source trees or cache directories.
