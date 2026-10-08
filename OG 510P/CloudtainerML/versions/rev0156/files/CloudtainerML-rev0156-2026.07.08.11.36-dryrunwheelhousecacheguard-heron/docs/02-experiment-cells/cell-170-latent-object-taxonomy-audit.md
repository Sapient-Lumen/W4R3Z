# CELL-170 — Latent Object Taxonomy Audit

Priority: **P1**  
Status: **candidate-audit**  
Idea: `IDEA-0169` — Latent object taxonomy audit

## Core question

Are we mixing cache, hidden-state, residual, adapter, and token-stream compression into one sloppy bucket?

## Source anchors

- `SRC-0208` — Beyond Tokens: A Unified Framework for Latent Communication in LLM-based Multi-Agent Systems (https://arxiv.org/abs/2606.05711)

## Cheap first run

Add WHAT/WHICH/HOW/phase fields to cells and dashboard grouping.

## Metrics

- cells tagged
- ambiguous cells
- priority changes caused by taxonomy

## Required baselines

- current family labels
- manual grouping

## Falsifier / stop condition

If taxonomy adds no steering value, freeze as docs.

## Rev0013 note

This cell was added during the native-frontier pass. C++ is preferred when the inner loop is deterministic, high-volume, and framework-free; Python remains preferred for training, plotting, and orchestration.
