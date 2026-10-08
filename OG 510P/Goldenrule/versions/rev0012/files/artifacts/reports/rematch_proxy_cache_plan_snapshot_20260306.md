# Rematch-Proxy Cache Plan Snapshot (2026-03-06)

Method:
- analyzed all `243` entrant support signatures over `{C, D, both}^5` in the current leave/rematch proxy
- compared the inherited naive canonicalization plan of full entrant-signature keying plus `h=50` against exact quotient regimes and exact horizons
- base proxy pool remains `extortion_chi3_v1, mem1_generous_tft_v1` over `243` deterministic `memory_one_exit` focal codes

Main findings:
- `deterministic no-noise` can be compiled to `17` cache bucket(s) at exact horizon `3`; that reduces naive key-depth slots from `12150` to `51` (`238.2x` smaller).
- `opponent support tremble` can be compiled to `1` cache bucket(s) at exact horizon `2`; that reduces naive key-depth slots from `12150` to `2` (`6075.0x` smaller).
- `focal support tremble` can be compiled to `2` cache bucket(s) at exact horizon `2`; that reduces naive key-depth slots from `12150` to `4` (`3037.5x` smaller).
- `bilateral support tremble` can be compiled to `1` cache bucket(s) at exact horizon `1`; that reduces naive key-depth slots from `12150` to `1` (`12150.0x` smaller).

Recommended provisional planner:
- `deterministic no-noise` — key `['noise_mode', 'support_regime_id']`, horizon `3`, planner kind `lookup-table`. Use the explicit 17-bucket support-regime lookup in the JSON artifact; full entrant support would over-key this proxy.
- `opponent support tremble` — key `['noise_mode']`, horizon `2`, planner kind `single-bucket`. All entrant support signatures share one exact quotient regime in this mode.
- `focal support tremble` — key `['noise_mode', 'entrant_initial_support_includes_D']`, horizon `2`, planner kind `boolean-gate`. The exact quotient regime is fully determined by whether the entrant can initially defect.
- `bilateral support tremble` — key `['noise_mode']`, horizon `1`, planner kind `single-bucket`. All entrant support signatures share one exact quotient regime once both sides tremble.

Zero-noise regime manifest:
- The JSON artifact includes an explicit `signature_to_regime` lookup for all 243 entrant support signatures. The largest bucket is the cooperative-start bucket; the rest split only once initial D support appears.
- `none_r00` — `81` signatures, family count `63`, representatives: `CCCCC`, `CCCCD`, `CCCCB`
- `none_r01` — `18` signatures, family count `99`, representatives: `DCCBB`, `DCDBB`, `DCBBB`
- `none_r02` — `18` signatures, family count `95`, representatives: `DCCBD`, `DCDBD`, `DCBBD`
- `none_r03` — `18` signatures, family count `95`, representatives: `DCCDB`, `DCDDB`, `DCBDB`
- `none_r04` — `18` signatures, family count `87`, representatives: `DCCDD`, `DCDDD`, `DCBDD`
- `none_r05` — `12` signatures, family count `95`, representatives: `DCDCB`, `DCBCB`, `DDDCB`
- `none_r06` — `12` signatures, family count `91`, representatives: `DCDCD`, `DCBCD`, `DDDCD`
- `none_r07` — `12` signatures, family count `95`, representatives: `DDCBC`, `DDDBC`, `DDBBC`
- `none_r08` — `12` signatures, family count `91`, representatives: `DDCDC`, `DDDDC`, `DDBDC`
- `none_r09` — `8` signatures, family count `91`, representatives: `DDDCC`, `DDBCC`, `DBDCC`
- `none_r10` — `6` signatures, family count `93`, representatives: `DCCBC`, `DCDBC`, `DCBBC`
- `none_r11` — `6` signatures, family count `93`, representatives: `DCCCB`, `DDCCB`, `DBCCB`
- `none_r12` — `6` signatures, family count `89`, representatives: `DCCCD`, `DDCCD`, `DBCCD`
- `none_r13` — `6` signatures, family count `89`, representatives: `DCCDC`, `DCDDC`, `DCBDC`
- `none_r14` — `4` signatures, family count `89`, representatives: `DCDCC`, `DCBCC`, `BCDCC`
- `none_r15` — `4` signatures, family count `89`, representatives: `DDCCC`, `DBCCC`, `BDCCC`
- `none_r16` — `2` signatures, family count `87`, representatives: `DCCCC`, `BCCCC`

Interpretation:
- The current proxy now supports a compact machine-readable canonicalization planner rather than a vague recommendation to “be world-aware.”
- Most of the inherited naive plan is dead weight here: exact cache planning is not only safer than full-signature reuse, it is orders of magnitude cheaper.

Implementor implication:
- Treat this report JSON as a provisional compile-time planner for the current proxy only. Vendor the table if useful, but regenerate it whenever the real rematch world changes entrant support, noise topology, outside-option timing, or memory depth.

