# CELL-067 — Modular Cartridge Routing Toy

Priority: **P1**
Status: `candidate`

## Cheapest first run

Generate fact shards, train tiny memory vectors per shard, then test routed composition against monolithic compression.

## Baselines

- explicit fact oracle
- monolithic cartridge
- isolated modules naive mix
- router-selected modules
- random modules

## Metrics

- exact answer rate
- distractor collapse rate
- memory tokens
- routing precision
- compression ratio

## Stop condition

If router-selected modules cannot beat monolithic at matched budget, pause.

## Source ids

SRC-0121, SRC-0108, SRC-0113
