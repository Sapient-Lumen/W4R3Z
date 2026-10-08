# Rematch-Proxy Canonicalization Sensitivity Snapshot (2026-03-06)

Method:
- analyzed all `243` deterministic `memory_one_exit` codes
- canonicalized each code by the decision parameters that are support-reachable before exit
- varied only the opponent pool; the focal strategy class and reachability horizon stayed fixed
- match horizon for reachability = `50` rounds

Main finding:
- The current proxy quotient (`63` families) is not stable to a hostile entrant.
- Adding one suspicious starter (`always_d_v1`) raises the count to `87` families.
- That is `24` extra families, or `38.1%` more than the current proxy quotient.
- Adding more cooperative starters (`tit_for_tat_v1`, `win_stay_lose_shift_v1`) leaves the quotient unchanged in this snapshot.

Scenario table:
- `Current proxy pool` — `63` families, `74.1%` raw-space reduction, largest family `E****` (`81` codes)
- `Current pool + Tit-for-Tat` — `63` families, `74.1%` raw-space reduction, largest family `E****` (`81` codes)
- `Current pool + WSLS` — `63` families, `74.1%` raw-space reduction, largest family `E****` (`81` codes)
- `Current pool + suspicious starter` — `87` families, `64.2%` raw-space reduction, largest family `E****` (`81` codes)
- `Mixed pool` — `87` families, `64.2%` raw-space reduction, largest family `E****` (`81` codes)

Families that split once a suspicious starter is added:
- Current family `CE***` (size `27`) splits into `CEC**`, `CED*C`, `CED*D`, `CED*E`, `CEE**`.
- Current family `D**E*` (size `27`) splits into `D**ED`, `D**EE`, `D*CEC`, `D*DEC`, `D*EEC`.
- Current family `CD*DD` (size `3`) splits into `CDCDD`, `CDDDD`, `CDEDD`.
- Current family `CD*DE` (size `3`) splits into `CDCDE`, `CDDDE`, `CDEDE`.
- Current family `CD*ED` (size `3`) splits into `CDCED`, `CDDED`, `CDEED`.
- Current family `CD*EE` (size `3`) splits into `CDCEE`, `CDDEE`, `CDEEE`.

Interpretation:
- The current `63`-family quotient is best treated as an optimistic lower bound tied to a cooperative-starting pool, not as a universal property of rematch worlds.
- Cooperative-starting additions are cheap from a search-geometry perspective here; suspicious starters are the structural event that reopens wildcard states.
- This means canonicalization must be world-aware and pool-aware. A cached quotient from one pool can under-deduplicate a richer pool and distort discovery counts.

Implementor implication:
- When the endogenous rematch world lands, recompute the canonicalization map whenever the entrant pool or start-state support changes. Do not freeze the current proxy quotient into the engine.
