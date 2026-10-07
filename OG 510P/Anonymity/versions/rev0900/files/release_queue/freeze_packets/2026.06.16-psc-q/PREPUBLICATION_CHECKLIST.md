# Pre-publication checklist: Anonymity: PSC-Q

- Freeze packet id: `2026.06.16-psc-q`
- Source: `series/congestion_series/paper2_psc_q/paper.tex`
- Source SHA-256: `14d2562e6910bceb799361a50dbc9bb3de40ccfcefd9eddd383e2f05aa7e5aec`
- Prospective target: `published/2026-06-16_psc_q`
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
