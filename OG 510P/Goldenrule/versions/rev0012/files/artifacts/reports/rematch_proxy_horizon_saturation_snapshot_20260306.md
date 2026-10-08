# Rematch-Proxy Horizon Saturation Snapshot (2026-03-06)

Method:
- analyzed all `243` deterministic `memory_one_exit` codes in the current leave/rematch proxy
- compared canonicalization at horizons `1..50` against the current `h=50` reference
- also checked the full entrant-signature regime map over `243` support signatures at each horizon
- reachability is support-based and stops at exit; no payoff simulation is used here

Main findings:
- `deterministic no-noise` saturates exactly by horizon `3` for both the base quotient (`63` families) and the full entrant-signature regime map (`17` regimes).
- `opponent support tremble` saturates exactly by horizon `2` for both the base quotient (`99` families) and the full entrant-signature regime map (`1` regimes).
- `focal support tremble` saturates exactly by horizon `2` for both the base quotient (`147` families) and the full entrant-signature regime map (`2` regimes).
- `bilateral support tremble` saturates exactly by horizon `1` for both the base quotient (`163` families) and the full entrant-signature regime map (`1` regimes).

Exact-horizon savings vs the inherited `h=50` bound:
- `deterministic no-noise` — exact at `3`, a `94.0%` reduction in reachability depth
- `opponent support tremble` — exact at `2`, a `96.0%` reduction in reachability depth
- `focal support tremble` — exact at `2`, a `96.0%` reduction in reachability depth
- `bilateral support tremble` — exact at `1`, a `98.0%` reduction in reachability depth

Progression by horizon:
- `deterministic no-noise` — `h=1`→base `7` / regimes `2`, `h=2`→base `27` / regimes `10`, `h=3`→base `63` / regimes `17`
- `opponent support tremble` — `h=1`→base `19` / regimes `1`, `h=2`→base `99` / regimes `1`, `h=3`→base `99` / regimes `1`
- `focal support tremble` — `h=1`→base `19` / regimes `2`, `h=2`→base `147` / regimes `2`, `h=3`→base `147` / regimes `2`
- `bilateral support tremble` — `h=1`→base `163` / regimes `1`, `h=2`→base `163` / regimes `1`, `h=3`→base `163` / regimes `1`

Interpretation:
- In the current proxy, the expensive-looking `h=50` reachability walk is mostly unnecessary for support-level canonicalization. The quotient closes once the reachable one-step state graph has finished unfolding.
- The slowest case is deterministic no-noise, which still stabilizes by the third consultation round. No current noise mode needs more than two rounds once tremble support is admitted, and bilateral tremble collapses immediately.

Implementor implication:
- Keep the exact-horizon caps local to this proxy and semantics family, but stop paying for `h=50` in support-level rematch canonicalization here. Use `{none: 3, opponent_tremble: 2, focal_tremble: 2, bilateral_tremble: 1}` and revalidate whenever memory depth, noise semantics, or rematch timing changes.

