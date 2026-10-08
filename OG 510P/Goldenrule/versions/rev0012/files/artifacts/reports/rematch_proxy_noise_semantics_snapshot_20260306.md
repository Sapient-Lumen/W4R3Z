# Rematch-Proxy Noise-Semantics Snapshot (2026-03-06)

Method:
- analyzed all `243` deterministic `memory_one_exit` codes in the current leave/rematch proxy
- compared support-reachable canonical families under four action-support semantics: deterministic no-noise, opponent tremble, focal tremble, and bilateral tremble
- each tremble mode is a support-level model of any nonzero action error: once a non-exit action is intended, both `C` and `D` are treated as reachable
- also reran the prior start-support sweep over `243` entrant signatures inside each noise mode
- match horizon for reachability = `50` rounds

Main findings:
- The zero-noise cooperative-pool quotient is `63` families.
- Opponent tremble alone raises it to `99` families, which already matches the strongest invalidation seen in the prior zero-noise start-support scan.
- Focal tremble alone raises it further to `147` families.
- Bilateral tremble yields `163` families.

Base quotient by noise mode:
- `deterministic no-noise` — base quotient `63`; `C`-only additions `63`–`63`; initial-`D` additions `87`–`99`
- `opponent support tremble` — base quotient `99`; `C`-only additions `99`–`99`; initial-`D` additions `99`–`99`
- `focal support tremble` — base quotient `147`; `C`-only additions `147`–`147`; initial-`D` additions `163`–`163`
- `bilateral support tremble` — base quotient `163`; `C`-only additions `163`–`163`; initial-`D` additions `163`–`163`

Interpretation:
- The earlier start-support cache gate is real, but it is a zero-noise result. As soon as tremble semantics are admitted, the cache key must widen from entrant support alone to entrant support plus noise semantics.
- Opponent tremble is the sharpest counterexample: once the current cooperative pool itself can emit either opening action through error support, every extra entrant signature collapses to the same `99`-family quotient.
- Focal tremble keeps a weaker gate (`147` for `C`-only additions, `163` for initial-`D` additions), so actor-side error semantics matter too.

Implementor implication:
- Treat any nonzero action-tremble semantics as an immediate invalidation of the zero-noise rematch canonicalization cache. Recompute under the active tremble model before ranking discoveries.

