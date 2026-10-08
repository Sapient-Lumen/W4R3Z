# CELL-231 — Low-Rank Decay Grokking Clock

Priority: **P2**  
Status: **candidate**  
Idea: `IDEA-0230`  
Sources: SRC-0255

## Cheap first run

Tiny modular arithmetic run with no decay, L2, and low-rank decay; log spectrum and generalization clock.

## Metrics

- train_loss
- validation_accuracy
- generalization_step
- singular_value_entropy

## Required baselines

- no_decay
- l2_decay
- low_rank_decay

## Stop condition

If CPU training is too long or no grokking appears, shelve.
