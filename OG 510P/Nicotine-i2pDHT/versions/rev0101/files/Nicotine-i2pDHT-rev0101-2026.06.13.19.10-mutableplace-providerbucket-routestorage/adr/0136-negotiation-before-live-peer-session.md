# ADR 0136 — negotiation before live peer session

Status: accepted in rev0033.

A future live peer session must not begin from a loose feature advertisement. It needs signed offers, signed or locally derived selection, namespace-policy digest binding, downgrade pressure, and frame-budget checks.
