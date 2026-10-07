# Pre-publication checklist: Anonymity: Certified Menus for Anonymous DHT Lookups

- Freeze packet id: `2026.05.21-certified-menus-for-anonymous-dht-lookups`
- Source: `series/certified_series/paperA_certified_menus_anonymous_dht/paper.tex`
- Source SHA-256: `4a5de337eb176df8811d6cf2dd95cd2c43eeb6f077f7f66f44ff36bdaa5e99d6`
- Prospective target: `published/2026-06-16_certified_menus_for_anonymous_dht_lookups`
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
