# Rematch-Proxy Start-Support Gate Snapshot (2026-03-06)

Method:
- analyzed all `243` memory-one support signatures over `{C, D, both}^5`
- each signature acts as one extra entrant added to the current leave/rematch proxy pool (`extortion_chi3_v1`, `mem1_generous_tft_v1`)
- canonicalized all `243` deterministic `memory_one_exit` focal codes by support-reachable consultation states before exit
- match horizon for reachability = `50` rounds

Main finding:
- Every signature with `C`-only initial support (`81` of `243`) leaves the quotient unchanged at `63` families.
- Every signature whose initial support includes `D` (`162` of `243`) invalidates that cache and raises the family count into `87`–`99`.
- Pure-`D` and mixed-start (`both`) entrants have the same family-count histogram in this snapshot.

Histogram by initial support:
- `C` initial support — `63`→`81`
- `D` initial support — `87`→`10`, `89`→`10`, `91`→`16`, `93`→`6`, `95`→`30`, `99`→`9`
- `B` initial support — `87`→`10`, `89`→`10`, `91`→`16`, `93`→`6`, `95`→`30`, `99`→`9`

Representative support signatures:
- max safe reuse: `s0=C` family represented by `CCCCC`
- smallest invalidating family-count representative: `DCCCC` -> `87` families
- largest invalidating family-count representative: `DCCBB` -> `99` families

Interpretation:
- In the current deterministic no-noise proxy, the cheapest sound cache gate is an initial-support check: if a new entrant can open with `D`, the old cooperative-start quotient is no longer trustworthy.
- That gate is only a trigger, not a replacement for recomputation. Later support decisions still determine whether the reopened quotient is `87`, `89`, `91`, `93`, `95`, or `99` families.

Implementor implication:
- Reuse the current rematch-proxy canonicalization cache only when every added entrant has `C`-only initial support under the current world semantics. Otherwise invalidate and recompute.

