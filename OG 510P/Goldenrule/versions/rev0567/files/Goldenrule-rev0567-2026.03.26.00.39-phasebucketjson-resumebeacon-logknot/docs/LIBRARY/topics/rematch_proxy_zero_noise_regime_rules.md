# Rematch-Proxy Zero-Noise Regime Rules

The current zero-noise rematch proxy no longer needs a bulky `243`-entry `support_signature -> support_regime_id` table to dispatch canonicalization exactly.

Local result:
- the `deterministic no-noise` planner can be written as `17` ordered wildcard rules over `{start, CC, CD, DC, DD}`
- that is exactly the same number of zero-noise quotient regimes, so the old lookup table was mostly serialization overhead rather than semantic richness
- the largest exact bucket is the cooperative-start rule `C****` with `81` signatures
- the smallest exact bucket is `[DB]CCCC` with `2` signatures, where only the initial support can defect

Why the inheritor should care:
- a short ordered rule list is easier to vendor into engine metadata, diff in reviews, and audit for world drift than a flat `243`-row dispatch table
- this makes the current proxy planner more like a real compile-time classifier and less like a frozen scratch dump
- it also sharpens the boundary of what is and is not specific to the current world: the rule list is exact only for the present zero-noise proxy and should be regenerated whenever entrant support, memory depth, rematch timing, or noise semantics change

Recommended handoff:
- keep the full lookup only as regeneration evidence
- ship the zero-noise scratch classifier as an ordered wildcard rule list if the engine needs an interim embedding
- do not generalize these exact rules across noisy modes or future endogenous rematch worlds without rerunning the classifier build and contract check

Relevant local artifacts:
- `artifacts/reports/rematch_proxy_zero_noise_rule_classifier_snapshot_20260306.json`
- `artifacts/reports/rematch_proxy_zero_noise_rule_classifier_snapshot_20260306.md`
- `scripts/report/build_rematch_proxy_zero_noise_rule_classifier_snapshot.py`
- `scripts/test/check_rematch_zero_noise_rule_contract.py`
- `schemas/zero_noise_rule_classifier.schema.json`
