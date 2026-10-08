# CELL-190: Prompt-State Memory Bandit

Priority: P1

Status: candidate

Idea: IDEA-0189

Source: SRC-0196

Cheap first run: No runnable probe yet; nonstationary tasks with mutable prompt variables.

Metrics:
- regret
- stale-state penalty
- adaptation speed

Baselines:
- reset prompt
- persistent prompt
- rollback checkpoint
- per-task prompt
- oracle task ID

Stop condition: If persistent prompt state collapses under shifts, require rollback/monitoring.
