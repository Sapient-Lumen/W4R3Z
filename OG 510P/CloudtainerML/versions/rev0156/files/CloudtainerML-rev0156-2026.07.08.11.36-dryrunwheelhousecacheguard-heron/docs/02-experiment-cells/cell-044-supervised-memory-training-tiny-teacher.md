# CELL-044 — Supervised Memory Training Tiny Teacher

Priority: P0  
Status: candidate

## Cheap first run

Teacher encoder emits predictive state labels; tiny RNN learns one-step transitions; compare to BPTT.

## Metrics

accuracy/exact match, loss/error, memory bytes, runtime, failure mode count, seed variance

## Stop condition

If teacher labels are not distillable, simplify task.
