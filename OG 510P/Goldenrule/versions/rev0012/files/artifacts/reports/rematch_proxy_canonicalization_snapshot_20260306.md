# Rematch-Proxy Canonicalization Snapshot (2026-03-06)

Method:
- analyzed all `243` deterministic `memory_one_exit` codes against the current proxy opponent pool
- canonicalized each code by the decision parameters that are support-reachable before exit across `extortion_chi3_v1` and `mem1_generous_tft_v1`
- match horizon for reachability = `50` rounds
- this is a structural support analysis, not a Monte Carlo ranking pass

Main finding:
- Raw search space `243` collapses to `63` support-distinct families in the current rematch proxy.
- That is a `74.1%` shrink in raw deterministic search volume before scoring.
- The largest collapse is immediate exit: `E****` covers `81` raw codes.
- The compact handoff baseline family `CCE**` covers `9` raw codes, so search should canonicalize it rather than rediscovering nine aliases.

Largest canonical families:
- `E****` — size `81` — representative `ECCCC` — Immediate-exit family: once the first move is Exit, every later parameter is unreachable.
- `CE***` — size `27` — representative `CECCC` — Pool-specific collapse: both current proxy opponents start with C, so a policy that exits after CC never consults later states.
- `D**E*` — size `27` — representative `DCCEC` — Defect-first then leave-after-DC family: the current proxy pool starts with C, so the first consulted repair/exit state is p_dc.
- `CCC**` — size `9` — representative `CCCCC` — Always-stay-on-C family within the current pool: only cooperative-prefix decisions are reachable under the proxy opponents.
- `CCE**` — size `9` — representative `CCECC` — Leave-after-break family: after first-round CC, any non-CC signal triggers exit before p_dc or p_dd can matter.
- `D**DD` — size `9` — representative `DCCDD` — Support-distinct family under the current proxy opponent pool.
- `D**DE` — size `9` — representative `DCCDE` — Support-distinct family under the current proxy opponent pool.
- `CD*DD` — size `3` — representative `CDCDD` — Support-distinct family under the current proxy opponent pool.
- `CD*DE` — size `3` — representative `CDCDE` — Support-distinct family under the current proxy opponent pool.
- `CD*ED` — size `3` — representative `CDCED` — Support-distinct family under the current proxy opponent pool.

Top candidate patterns already present in the proxy report:
- `CCDDE` -> `CCDDE`; proxy mean `2.746167`, proxy min `2.423221`
- `CCECC` -> `CCE**`; proxy mean `2.755101`, proxy min `2.414051`
- `CCECD` -> `CCE**`; proxy mean `2.755101`, proxy min `2.414051`
- `CCECE` -> `CCE**`; proxy mean `2.755101`, proxy min `2.414051`
- `CCEDC` -> `CCE**`; proxy mean `2.755101`, proxy min `2.414051`
- `CDDCE` -> `CDDCE`; proxy mean `2.817035`, proxy min `2.490705`
- `DDDCE` -> `DDDCE`; proxy mean `2.795099`, proxy min `2.482256`
- `DCDCE` -> `DCDCE`; proxy mean `2.752798`, proxy min `2.434330`

Interpretation:
- The previous `CCE**` hint was real but incomplete: the current proxy opponent pool compresses the full deterministic space much more aggressively than one family alone suggests.
- This compression is pool-specific because both current proxy opponents start with cooperation. If a future endogenous world adds suspicious or noisy entrants, some wildcard states may become reachable again.
- The implementor consequence is concrete: perform genotype-to-phenotype canonicalization before optimization in rematch-enabled worlds, or the search will waste budget on aliases.

Immediate implementor implication:
- The next engine-supported rematch world should expose a canonicalization hook or post-processor for unreachable exit-tail parameters, with `CCEEE` kept as the human-readable representative of the `CCE**` family.
