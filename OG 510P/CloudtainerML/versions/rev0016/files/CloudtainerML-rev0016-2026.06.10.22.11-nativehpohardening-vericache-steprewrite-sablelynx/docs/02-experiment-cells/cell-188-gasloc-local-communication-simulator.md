# CELL-188: GASLoC Local Communication Simulator

Priority: P2

Status: candidate

Idea: IDEA-0187

Source: SRC-0223

Cheap first run: No runnable probe yet; tiny distributed optimizer simulator.

Metrics:
- convergence steps
- communication volume
- staleness regret

Baselines:
- all-reduce
- local steps plus periodic average
- sparse gossip
- oracle topology

Stop condition: If topology tuning dominates, keep as systems background.
