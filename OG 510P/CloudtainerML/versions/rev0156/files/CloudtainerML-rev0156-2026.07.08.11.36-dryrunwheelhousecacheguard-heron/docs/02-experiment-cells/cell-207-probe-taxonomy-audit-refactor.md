# CELL-207 — Probe Taxonomy Audit Refactor

Priority: **P0**  
Status: **implemented_refactor**  
Idea: `IDEA-0207`  
Sources: SRC-0233

## Cheap first run

Run tools/probe_taxonomy_audit.py and classify current revision artifacts into coarse families.

## Metrics

- uncategorized count
- tag counts

## Required baselines

- manual priority list
- taxonomy audit

## Stop condition

If taxonomy does not guide priority changes, demote to docs.
