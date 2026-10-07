# Pre-publication checklist: Anonymity: Congestion-EQ

- Freeze packet id: `2026.06.16-congestion-eq`
- Source: `series/congestion_series/paper1_congestion_eq/paper.tex`
- Source SHA-256: `12ea46985036b1b5f3a4012083afd482af8ac4d4f868fbc1f6dd0390a1031c2d`
- Prospective target: `published/2026-06-16_congestion_eq`
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
