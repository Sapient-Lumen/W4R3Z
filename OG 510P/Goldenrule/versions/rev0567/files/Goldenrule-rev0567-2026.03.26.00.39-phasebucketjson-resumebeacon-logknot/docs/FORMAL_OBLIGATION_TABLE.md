# Formal Obligation Table

This table sets minimum formal obligations by claim class.

| claim class | obligation | minimum tools | gate level |
|---|---|---|---|
| `CC-001` Empirical performance | none beyond deterministic replay | n/a | `gate` |
| `CC-002` Robustness | none beyond sweep reproducibility | n/a | `gate` |
| `CC-003` Formal invariance | solver replayable invariant check | z3/cvc5 family | `gate` + strict-ready |
| `CC-004` Cross-solver agreement | two-solver parity on shared encoding | z3 + cvc5 | `gate-strict` |
| `CC-005` Probabilistic bound | simulation/model-checking consistency | PRISM/STORM + simulation | `gate-strict` |
| `CC-006` Operational reproducibility | manifest + checksum reproducibility | release tooling | `gate` |
| `CC-007` Policy exception | dated assumption and mitigation links | spec ledger validators | `gate` |

## Notes

1. Obligations are intentionally progressive; not all claims require strict formal gates.
2. Claim obligations should be promoted only after baseline stability is demonstrated.
