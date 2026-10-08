# Visible-order mismatch page — UI alphabetical order, non-splittable files, and overclaim barrier

## Purpose

Prevent the operator from treating the visible queue as proof of actual scheduler order.
This page exists because the current docs still admit a mismatch between what the UI may show and what the engine is actually prioritizing.

## Questions this page must answer

1. Is the list order being shown alphabetical, grouped, or effective-priority order?
2. Does the current scheduler order differ from the visible list?
3. Are non-splittable or exception-bearing files present?
4. What is the strongest safe sentence the interface can make about `first`, `next`, or `blocked by`?

## Required states

### Visible list class

- alphabetical list
- grouped list
- effective-priority list
- mixed / unstable list

### Scheduler confidence

- effective order proven
- effective order partially inferred
- effective order not proven from this surface

### Exception-bearing items

- none present
- present and ahead
- present and behind
- present with unknown effect

## Overclaim barriers

The page must not let the product say:

- `first in the list downloads first`
- `top row is next`
- `higher priority always preempts active transfer`
- `the queue you see is the queue the engine executes`

unless those claims are separately proven on this page.

## Required remediation lane

When visible order is not scheduler proof, the page must direct the operator to the active-window proof instead of pretending the list itself is authoritative.
