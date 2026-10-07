# Pre-publication checklist: Anonymity: State-Dependent Anonymity

- Freeze packet id: `2026.06.16-state-dependent-anonymity`
- Source: `series/anondht_state_series/paper1_state_dependent_anonymity/paper.tex`
- Source SHA-256: `fdf56b4926892fcd2bfe8e78f66bdaed963d350217982db74a1a1989419e790b`
- Prospective target: `published/2026-06-16_state_dependent_anonymity`
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
