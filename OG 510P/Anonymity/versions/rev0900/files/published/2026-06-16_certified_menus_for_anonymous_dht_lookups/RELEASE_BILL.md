# Release bill: Certified Menus for Anonymous DHT Lookups

- Public head: `[[2026.06.16 - Anonymity: Certified Menus for Anonymous DHT Lookups]]`
- Published source: `published/2026-06-16_certified_menus_for_anonymous_dht_lookups/paper.tex`
- Source freeze: `series/certified_series/paperA_certified_menus_anonymous_dht/paper.tex`
- Source SHA-256: `4a5de337eb176df8811d6cf2dd95cd2c43eeb6f077f7f66f44ff36bdaa5e99d6`
- Publication decision: `release_queue/decisions/2026.06.16-0356-certifiedmenus-publicspine-publish.md`
- Publication receipt: `published/2026-06-16_certified_menus_for_anonymous_dht_lookups/PUBLICATION_RECEIPT.json`
- Evidence pack: `release_queue/evidence_packs/2026.05.21-certified-menus-for-anonymous-dht-lookups/EVIDENCE_PACK_MANIFEST.json`
- Compile witness: `release_queue/FREEZE_COMPILE_WITNESS.json`
- Compile witness snapshot: `release_queue/freeze_packets/2026.05.21-certified-menus-for-anonymous-dht-lookups/FREEZE_COMPILE_WITNESS.snapshot.json`
- Freeze packet: `release_queue/freeze_packets/2026.05.21-certified-menus-for-anonymous-dht-lookups/FREEZE_PACKET_MANIFEST.json`

## Claim boundary

This release exposes the raw-M certified-menu theorem and its minimal public card. The claim is valid only with the named witness/interface version, fixed finite policy class, source-bound multiplicity accounting, support/overlap assumptions, censoring treatment, retained logging propensities or weights, and adversary-facing transcript projection.

## Non-claims

This release does not publish Certified B compression, Certified C deployed drift handling, or a general claim that any future policy switch remains safe without preserving the same-card rows. Those remain downstream work and should not be cited as part of this public head.

## Hostile-review target

A hostile reviewer should attack the off-policy support assumptions, menu membership row, raw-M multiplicity accounting, transcript projection, and whether later padding/token/logging/parser changes are correctly routed to successor-card rather than wrapper refreshes.
