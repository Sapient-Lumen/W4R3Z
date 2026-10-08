# rev0034 scout notes

## Boundary repair

`SRC-0348` adds a clean graph-level exactness failure: nearby tokens can be unreachable under fixed block-causal masks. This makes boundary phase a promotion guard for sparse attention.

## Sessa

`SRC-0349` is parked as P1: attention inside a recurrent feedback path may create different long-tail influence surfaces than one-shot attention or fixed state.

## Routing absorption trained escalation

`CELL-331` converts the routing-absorption idea from a symbolic C++ wind tunnel into a tiny PyTorch lookup/copy task. The point is not final accuracy; it is soft-vs-hard deployment evidence.
