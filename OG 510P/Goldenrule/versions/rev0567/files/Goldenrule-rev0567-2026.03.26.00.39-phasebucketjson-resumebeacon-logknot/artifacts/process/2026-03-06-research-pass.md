# 2026-03-06 Research Pass

## What changed

- Added Golden-Rule-adjacent source entries for longer memory, fair resistance to extortion, partner choice, opting out, and universalisation.
- Added an inheritor brief focused on next-step tranche selection.
- Compacted the archive to citation-first mode by removing long-term PDF blobs.

## Environment notes

- `make doctor` failed because `cargo` / `junest` are unavailable in the current environment.
- `make test-quick` reached Python checks successfully but failed at the Rust library test step for the same reason.

## Research direction

- Do not widen search until extortion evaluation stops optimizing raw `avg_a` alone.
- Add leave/rematch and longer-memory baselines before broad strategy discovery.
- Keep universalisation as an explicit benchmark family, not just a philosophical motivation.
- Tightened the exit/partner-choice boundary: deterministic `memory_one_exit` can look fair by defecting first and exiting, so unilateral exit should remain diagnostic until a rematch world exists.
- Added a minimal leave/rematch proxy result: nice-start exit policies become competitive once rematching exists, with `mem1_exit_after_break_v1` kept as the compact handoff baseline.


- Added a structural canonicalization result for the rematch proxy: the current proxy pool compresses 243 raw deterministic `memory_one_exit` codes to 63 support-distinct families, so rematch-enabled search should deduplicate aliases before optimization.

- Added a sensitivity result for rematch-world canonicalization: the current 63-family quotient is stable to extra cooperative starters but rises to 87 families once a single suspicious starter enters the pool.

- Added a start-support gate result for the current rematch proxy: all `C`-only entrant support signatures preserve the `63`-family quotient, while any entrant whose initial support includes `D` invalidates the cache and reopens the quotient to `87`–`99` families.
- Added a noise-semantics result for rematch canonicalization: the current 63-family quotient is a zero-noise artifact, expanding to 99 families under opponent tremble, 147 under focal tremble, and 163 under bilateral tremble.

- Added an exact cache-regime result for rematch canonicalization: the current proxy has `17` quotient regimes in deterministic no-noise semantics, but only `1` under opponent tremble, `2` under focal tremble, and `1` under bilateral tremble.

- Added a horizon saturation result for rematch canonicalization: the current support-level proxy reaches its exact `h=50` quotient/regime map by horizon `3` in zero-noise, `2` in opponent/focal tremble, and `1` in bilateral tremble.
- Added a compile-time cache-planner result for rematch canonicalization: the current proxy can replace naive full-signature/`h=50` keying with exact plans costing `51/2/4/1` key-depth slots across `{none, opponent, focal, bilateral}` noise modes.
- Added a provisional canonicalization-plan contract for the current rematch proxy: a schema plus a validator now check the scratch planner report for internal consistency, exact mode keys, and full regime coverage.

- Added an exact zero-noise rule-classifier result for rematch canonicalization: the current `243`-entry `support_signature -> regime` lookup compresses to `17` ordered wildcard rules, making the scratch planner cheaper to embed and audit without losing exactness.
- Added a schema-backed packaging gate for the zero-noise ordered classifier: interim planner embeddings should now carry both `schemas/zero_noise_rule_classifier.schema.json` and `scripts/test/check_rematch_zero_noise_rule_contract.py` rather than relying on the report alone.
- Added a derived delay-pressure report for the rematch proxy: rematch delay behaves like a real tax on leave-based policies and should become an explicit swept world field.
- Added a rematch-contract note from restart-world literature: role assignment on rematch must be treated as part of the world contract, with fixed-role and role-swapped companion benchmarks.

- Added a delay-vs-market-thickness boundary: the current exogenous-pool rematch proxy treats delay as a one-sided tax, so its delay sweeps should remain diagnostic until an endogenous matching world separates delay from market thickness / search difficulty.
