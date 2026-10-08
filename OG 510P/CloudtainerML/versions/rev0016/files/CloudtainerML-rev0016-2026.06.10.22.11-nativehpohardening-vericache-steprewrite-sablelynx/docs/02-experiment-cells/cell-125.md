# CELL-125 — Planning-Aligned Compression Toy

Priority: **P1**  
Status: **candidate**  
Idea: `IDEA-0124`  
Sources: SRC-0182

## Cheap first run

Scene/action toy where compression is scored by action preservation.

## Metrics

- action preservation
- token retention
- reconstruction error

## Required baselines

- reconstruction top-k
- salience top-k
- planning oracle
- random

## Stop condition

If action preservation tracks reconstruction exactly, redesign task.
