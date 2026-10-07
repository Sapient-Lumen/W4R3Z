# Pre-publication checklist: Anonymity: W-Congestion-EQ

- Freeze packet id: `2026.06.16-w-congestion-eq`
- Source: `series/congestion_series/paper3_w_congestion_eq/paper.tex`
- Source SHA-256: `e738565c80bcfeffe4263a1884125d628fbf51a52509674037a57f724a8b71ff`
- Prospective target: `published/2026-06-16_w_congestion_eq`
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
