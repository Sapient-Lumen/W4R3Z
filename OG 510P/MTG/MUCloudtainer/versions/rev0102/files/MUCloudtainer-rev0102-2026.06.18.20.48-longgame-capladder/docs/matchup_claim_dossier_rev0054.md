# rev0054 Matchup Claim Dossier

rev0053 identified `cf34_counter_wall` versus `pub_threat_overlord` as the cleanest concrete cell candidate.  rev0054 deepens that single cell instead of adding another learned policy.

The schedule is intentionally narrow:

```text
target:      cf34_counter_wall
opponent:    pub_threat_overlord
life totals: 20 and 40
target seats: p0 and p1
starting players: 0 and 1
reps:        20 per seat/start/life
max decisions: 900
```

That produces 160 terminal-clean games and 80 target-perspective games per life total.  The dossier records target/life cells, target-seat slices, starting-player slices, life-by-seat slices, replay traces, and C++ transition shadow rows.

## Claim labels

`terminal_matchup_claim.py` distinguishes:

- `concrete_matchup_claim_candidate`: total lower confidence bound above 0.5, both life totals positive, and life split stable.
- `life_sensitive_matchup_claim_candidate`: total lower confidence bound above 0.5, both life totals positive, but the life-total split is nontrivial.
- `positive_matchup_watch`: positive mean signal without enough conservative support.
- `terminal_clean_signal_only`: terminal-clean data exists but no claim label is justified.
- `needs_more_games`: sample budget too small.

rev0054 produces a `life_sensitive_matchup_claim_candidate`, not a life-stable concrete claim.
