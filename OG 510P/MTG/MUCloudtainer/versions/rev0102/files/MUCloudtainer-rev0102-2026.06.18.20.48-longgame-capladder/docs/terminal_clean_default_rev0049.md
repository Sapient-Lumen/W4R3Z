# rev0049 terminal-clean default

rev0048 proved that a low-ceiling smoke panel could be rescued by rerunning the
same schedule at a higher decision ceiling.  rev0049 turns that into a default
rule for promotion-facing payoff tables:

```text
smoke / diagnostic panel: may truncate, but must say so
promotion / comparison panel: should be terminal-clean by construction
```

The new `src/muc5/terminal_clean.py` helper annotates every payoff row with:

```text
terminal_clean_max_decisions
terminal_clean_game
terminal_clean_status
```

It does not change scores.  It makes the scoring contract visible so standings
cannot silently mix terminal wins with max-decision draw-half artifacts.

For rev0049, the yield-ranker panel uses:

```text
max_decisions = 900
max_truncation_rate = 0.0
```

The stronger rule is: truncation is allowed for diagnosing stall behavior and
runtime pressure, but a strategy should not be promoted from a payoff table with
nonterminal truncation rows.
