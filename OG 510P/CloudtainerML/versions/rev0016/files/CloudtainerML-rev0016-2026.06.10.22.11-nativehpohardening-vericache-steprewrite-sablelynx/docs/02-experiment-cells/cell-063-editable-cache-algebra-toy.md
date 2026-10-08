# CELL-063 — Editable Cache Algebra Toy

Priority: P1

Status: candidate

Source IDs: SRC-0114, SRC-0115

## Cheap first run

Span splice/reuse/forget operations over synthetic attention histories.

## Baselines

- full re-prefill oracle
- prefix-only cache
- segment reuse no correction
- segment reuse with sparse correction

## Metrics

- attention output error
- correction token count
- reuse hit rate
- position-drift error

## Stop condition

If corrections approach full re-prefill cost, keep only as systems note.
