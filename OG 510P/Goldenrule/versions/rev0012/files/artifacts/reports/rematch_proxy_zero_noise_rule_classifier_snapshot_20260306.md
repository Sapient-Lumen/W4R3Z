# Rematch-Proxy Zero-Noise Rule Classifier Snapshot (2026-03-06)

Method:
- loaded the current `deterministic no-noise` support-regime lookup from `artifacts/reports/rematch_proxy_cache_plan_snapshot_20260306.json`
- replaced the 243-entry `signature -> regime` map with an ordered wildcard rule list over the five support positions `{start, CC, CD, DC, DD}`
- validated that the ordered rule list reproduces the exact regime assignment for all 243 support signatures

Main findings:
- the current zero-noise regime dispatch compresses from `243` explicit lookup entries to `17` exact ordered wildcard rules (`14.294118x` smaller).
- the largest rule bucket is `zr00` / `C****` with `81` signatures.
- the smallest rule bucket is `zr16` / `[DB]CCCC` with `2` signatures.

Exact ordered rules:
- `zr00` — `C****` -> `none_r00` (`81` signatures, family count `63`)
- `zr01` — `[DB]**BB` -> `none_r01` (`18` signatures, family count `99`)
- `zr02` — `[DB]**BD` -> `none_r02` (`18` signatures, family count `95`)
- `zr03` — `[DB]**DB` -> `none_r03` (`18` signatures, family count `95`)
- `zr04` — `[DB]**DD` -> `none_r04` (`18` signatures, family count `87`)
- `zr05` — `[DB]*[DB]CB` -> `none_r05` (`12` signatures, family count `95`)
- `zr06` — `[DB]*[DB]CD` -> `none_r06` (`12` signatures, family count `91`)
- `zr07` — `[DB][DB]*BC` -> `none_r07` (`12` signatures, family count `95`)
- `zr08` — `[DB][DB]*DC` -> `none_r08` (`12` signatures, family count `91`)
- `zr09` — `[DB][DB][DB]CC` -> `none_r09` (`8` signatures, family count `91`)
- `zr10` — `[DB]C*BC` -> `none_r10` (`6` signatures, family count `93`)
- `zr11` — `[DB]*CCB` -> `none_r11` (`6` signatures, family count `93`)
- `zr12` — `[DB]*CCD` -> `none_r12` (`6` signatures, family count `89`)
- `zr13` — `[DB]C*DC` -> `none_r13` (`6` signatures, family count `89`)
- `zr14` — `[DB]C[DB]CC` -> `none_r14` (`4` signatures, family count `89`)
- `zr15` — `[DB][DB]CCC` -> `none_r15` (`4` signatures, family count `89`)
- `zr16` — `[DB]CCCC` -> `none_r16` (`2` signatures, family count `87`)

Interpretation:
- The current zero-noise planner no longer needs a bulky opaque `signature -> regime` table to be exact. A small ordered wildcard classifier is enough, which makes the planner easier to embed, diff, and audit.
- Order matters: these rules are an exact decision list for the current proxy, not a claim about future rematch worlds.

Implementor implication:
- If the engine needs a zero-noise scratch classifier before rematch worlds expose planner metadata natively, prefer this ordered rule list over vendoring a 243-entry dispatch table. Regenerate it whenever entrant support, outside-option timing, memory depth, or noise semantics change.
