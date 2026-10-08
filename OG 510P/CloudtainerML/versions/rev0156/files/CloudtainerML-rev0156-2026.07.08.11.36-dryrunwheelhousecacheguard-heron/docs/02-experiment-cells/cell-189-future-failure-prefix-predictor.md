# CELL-189: Future-Failure Prefix Predictor

Priority: P1

Status: candidate

Idea: IDEA-0188

Source: SRC-0197, SRC-0161

Cheap first run: No runnable probe yet; derive features from DFS/TRACE traces before terminal reward.

Metrics:
- early failure AUC
- steering improvement
- false alarm rate

Baselines:
- terminal-only
- prefix features
- oracle future
- random

Stop condition: If early signals appear only after failure is explicit, demote.
