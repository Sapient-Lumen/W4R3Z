# 48 — Exploration Metrics + Tuning (v0.19)

Exploration is only worth keeping if it produces measurable wins.

## 1) Metrics to log
Per exploration item shown:
- was it acted upon? (referenced in @CTRL/@PROPOSE)
- did it yield a win type? (CE/E/P/SUM/LEASE clarif)
- did it reduce deadlock time? (cursors to next evidence)
- did it increase WS churn? (bad if yes without progress)

## 2) Win rate
`win_rate = wins / exploration_items_shown`

Targets:
- >= 0.15 early is good enough
- < 0.05: exploration is likely wasting attention (disable RANDOM first)

## 3) Random rate
True random is a hedge against blind spots, but it’s derailment risk.
Default:
- RANDOM=0 in normal mode
- RANDOM=1 only when consensus collapse is detected

## 4) When to explore harder
Increase exploration when:
- all agents agree quickly without evidence
- repeated deadlocks without new E#
- many open tasks, no progress

Decrease exploration when:
- truncation spikes
- evidence density is high
- WS is near cap and compaction is frequent

## 5) Tuning loop (MetaLLM)
Observe → adjust → verify via discriminative outcomes:
- Did we get a new CE/E/P?
- Did the next patch selection improve?
