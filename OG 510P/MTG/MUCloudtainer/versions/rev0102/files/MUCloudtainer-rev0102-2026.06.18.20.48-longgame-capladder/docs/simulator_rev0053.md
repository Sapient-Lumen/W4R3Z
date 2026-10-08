# Simulator rev0053

No card-rule semantics changed.

The simulator continues to use:

- exact five-card MUC-5 referee,
- public DecisionFrame hidden-information boundary,
- terminal-clean payoff rows for claim work,
- split transition/agent RNG,
- replay traces for sampled games,
- C++ transition shadow checking for every payoff-heavy panel.

rev0053 adds a new terminal-clean evaluation panel on concrete cells chosen from rev0052 retested target/life rows.  The panel is designed to prevent old low-sample life-flip stories from becoming claims without concrete matchup confirmation.
