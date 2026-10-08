# CELL-061 — Head-Aware Budget Allocation Toy

Priority: P1

Status: candidate

Source IDs: SRC-0110

## Cheap first run

Multi-head synthetic tasks where heads have local/global/anchor/noise roles.

## Baselines

- uniform budgets
- role-aware static budgets
- learned per-head budgets
- oracle per-head budgets

## Metrics

- task accuracy
- cache bytes
- head starvation count
- role recovery

## Stop condition

If role-aware budgets do not beat uniform in constructed heterogeneous heads, demote.
