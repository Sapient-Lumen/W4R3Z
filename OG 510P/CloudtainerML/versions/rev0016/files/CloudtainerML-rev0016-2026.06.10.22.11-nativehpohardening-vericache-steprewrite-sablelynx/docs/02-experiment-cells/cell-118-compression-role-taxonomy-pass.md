# CELL-118: Compression Role Taxonomy Pass

Priority: **P0**
Idea: `IDEA-0117`
Status: **active-refactor**

## Cheap first run

Annotate cells/sources with roles: answer substrate, router, index, prefetcher, stale filter, writable memory.

## Required baselines

- family-only grouping
- priority-only grouping

## Metrics

- role coverage
- ambiguous role count
- priority changes

## Stop / demote condition

If role tags do not clarify code targets, remove.
