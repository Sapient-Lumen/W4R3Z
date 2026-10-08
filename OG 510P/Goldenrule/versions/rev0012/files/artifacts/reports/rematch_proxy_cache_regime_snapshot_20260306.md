# Rematch-Proxy Cache-Regime Snapshot (2026-03-06)

Method:
- analyzed all `243` entrant support signatures over `{C, D, both}^5`
- for each noise mode, computed the full canonical family set over all `243` deterministic `memory_one_exit` focal codes
- grouped entrant signatures by exact quotient-set equality, not just by family-count equality
- current proxy pool remains `extortion_chi3_v1, mem1_generous_tft_v1` with reachability horizon `50`

Main findings:
- `deterministic no-noise` has `17` exact quotient regime(s): family-count range `63`–`99`. C-only entrants share one safe cache bucket, but once initial D support appears the quotient splinters into 16 additional regimes.
- `opponent support tremble` has `1` exact quotient regime(s): family-count range `99`–`99`. Cache key can ignore entrant support entirely; noise mode alone determines the quotient in this proxy.
- `focal support tremble` has `2` exact quotient regime(s): family-count range `147`–`163`. Cache key collapses to noise mode plus whether the entrant can initially defect.
- `bilateral support tremble` has `1` exact quotient regime(s): family-count range `163`–`163`. Cache key can ignore entrant support entirely once both sides have nonzero action-error support.

Mode-specific cache guidance:
- `deterministic no-noise` — Keep the C-only fast path, but after initial-D support appears do not collapse to a single coarse key; later support still splits the quotient.
- `opponent support tremble` — Key on noise mode only; entrant support does not change the quotient in this proxy.
- `focal support tremble` — Key on noise mode plus whether the entrant has initial-D support.
- `bilateral support tremble` — Key on noise mode only; entrant support does not change the quotient once both sides tremble.

Representative regime structure:
- `deterministic no-noise` — `CCCCC` (81 sigs; init `C`; `63` families); `DCCBB` (18 sigs; init `B,D`; `99` families); `DCCBD` (18 sigs; init `B,D`; `95` families); `DCCDB` (18 sigs; init `B,D`; `95` families)
- `opponent support tremble` — `CCCCC` (243 sigs; init `B,C,D`; `99` families)
- `focal support tremble` — `DCCCC` (162 sigs; init `B,D`; `163` families); `CCCCC` (81 sigs; init `C`; `147` families)
- `bilateral support tremble` — `CCCCC` (243 sigs; init `B,C,D`; `163` families)

Interpretation:
- The current proxy does not just have a noise-sensitive cache; it has a small number of distinct cache regimes, and those regimes depend strongly on which side can tremble.
- This means the next rematch-world engine should separate cache-key design into correctness-critical fields (noise topology, initial-defect reachability where relevant) and avoid paying for unnecessary full-signature cache keys in regimes where entrant support is already washed out.

