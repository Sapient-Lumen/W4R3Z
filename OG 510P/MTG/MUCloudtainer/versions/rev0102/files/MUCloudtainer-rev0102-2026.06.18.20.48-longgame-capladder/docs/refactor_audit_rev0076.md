# rev0076 refactor audit

Concrete refactor: `target_score_from_seat` and `annotate_focus_target_from_seat` were added to `src/muc5/terminal_mechanisms.py`, and `annotate_threat_response_rows` now uses the shared helper rather than hand-rolling `p0_score if target_seat == 0 else p1_score`.

Why this matters: population panels intentionally alternate the target policy between player seats. Any future runner that forgets the seat orientation can invert wins and losses. The shared helper creates one contract and the score-orientation audit checks historical live raw rows against that contract.

Validation artifact: `data/rev0076_score_orientation_summary.json` reports zero mismatches over 720 rows.
