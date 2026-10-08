# Experiment matrix — rev0068

## Active questions

|ID|Question|Primary output|Stop condition|Status|
|---|---|---|---|---|
|E68-1|Does `counter_guard` remain useful against a fixed population rather than one opponent?|population payoff matrix, meta-strategy, worst-case payoff|all named policies evaluated on frozen paired seed blocks|planned|
|E68-2|Can a response oracle improve materially against the current meta-strategy?|oracle gain / exploitability proxy|two consecutive oracle rounds below registered gain threshold|planned|
|E68-3|How much of rev0067's 60-vs-60 life-40 signal survives paired holdout replication?|paired policy delta with interval|registered precision reached or maximum budget exhausted|planned|
|E68-4|Can a reduced exact MUC-5 subgame be represented independently?|history/information-state/utility conformance|zero mismatches on directed corpus|planned|
|E68-5|Can the linked core fall below 300 MiB with all raw evidence still addressable?|package size and evidence-index audit|zero unindexed moved objects|planned|

## Required design fields for every new experiment

```text
question and claim ID
primary estimand
complete factor matrix
seed pairing/allocation
sample or precision target
stopping rule
primary/exploratory designation
holdout family
promotion, demotion, and inconclusive outcomes
raw-evidence retention class
```
