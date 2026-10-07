# Release bill — Anonymity: Calibration Recipes for Anonymous DHT Deployments

- Public head: `[[2026.06.16 - Anonymity: Calibration Recipes for Anonymous DHT Deployments]]`
- Published path: `published/2026-06-16_calibration_recipes_for_anonymous_dht_deployments/`
- Source: `series/evaluation_series/paper3_calibration_recipes_anondht/paper.tex`
- Source SHA-256: `bc566ec5d37eb65175af33cb0376c9d59e88a97e09fd7a092fb45138612572cf`
- Decision note: `release_queue/decisions/2026.06.16-1356-calibrationrecipes-publicspine-publish.md`
- Evidence pack: `release_queue/evidence_packs/2026.06.16-calibration-recipes-for-anonymous-dht-deployments/EVIDENCE_PACK_MANIFEST.json`
- Compile witness: `release_queue/freeze_packets/2026.06.16-calibration-recipes-for-anonymous-dht-deployments/FREEZE_COMPILE_WITNESS.snapshot.json`
- Freeze packet: `release_queue/freeze_packets/2026.06.16-calibration-recipes-for-anonymous-dht-deployments/FREEZE_PACKET_MANIFEST.json`
- Publication receipt: `published/2026-06-16_calibration_recipes_for_anonymous_dht_deployments/PUBLICATION_RECEIPT.json`

## Claim carried by this public head

Calibration Recipes publishes a numbers-first conversion companion for anonymous-DHT deployments. The public card binds the exact imported claim tuple `enf.committee_contact.v1` / `tw.lookup.30d.v1`, the committee-contact witness family, `Delta=0.02`, `eta=0.05`, cadence `10^3` epochs/day, alert target `(0.10,0.01)`, the recomputed horizon of about `2.16e4` epochs / `21.6` days, and the alert-tax value `log2(90) ~= 6.49` bits.

## Machine-checkable release card

The release evidence pack contains `CALIBRATION_RECIPE_CARD.json`, extracted from `tab:minimal-calibration-card`. The card recomputes the horizon and alert-tax arithmetic, binds the owner route, verifies the Calibration-card non-substitution guard, and audits the maintained worked-example artifacts: the owner map names `calibration_recipe_packet` / `eval-calibration-recipe-v1`, while the verifier report, replay plans, and support-bundle map do not materialize that packet, replay hook, or bundle route.

## Boundary

This publication is not a theorem root, not evaluator notarization, not a runtime-conformance receipt, not ABOM/OINL release lineage, and not a materialized `calibration_recipe_packet` verifier/support bundle. Later papers may quote the calibration card only as a conversion receipt for the exact imported tuple, gap/error row, cadence row, alert target, and escalation pointer.

## Why this release is safe enough

The source is hash-bound, queue-bound, supported by a source-specific calibration card, deterministic clean LaTeX compile snapshot, freeze packet, explicit publish decision, publication receipt, and public citation-head update. The source now states the non-substitution rule and prevents the absent worked-example verifier/support packet from being quoted as carried evidence.
