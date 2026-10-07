# Pre-publication checklist: Anonymity: Calibration Recipes for Anonymous DHT Deployments

- Freeze packet id: `2026.06.16-calibration-recipes-for-anonymous-dht-deployments`
- Source: `series/evaluation_series/paper3_calibration_recipes_anondht/paper.tex`
- Source SHA-256: `bc566ec5d37eb65175af33cb0376c9d59e88a97e09fd7a092fb45138612572cf`
- Prospective target: `published/2026-06-16_calibration_recipes_for_anonymous_dht_deployments`
- Publication authorized: `false`

Resolved gates:

- queue binding
- source hash binding
- direct static preflight
- evidence-pack resolution
- frozen-source copy bound to the same source hash
- source-bound compile-witness snapshot embedded in the packet

Compile gate status:

- `pass`

Still required before a public move:

- a current deterministic clean LaTeX compile witness when the compile gate is not `pass`
- an explicit publication decision note with `Publication action: publish`
- execution through the guarded publication helper
- post-publication metadata, public-surface, provenance, and manifest rebuild
