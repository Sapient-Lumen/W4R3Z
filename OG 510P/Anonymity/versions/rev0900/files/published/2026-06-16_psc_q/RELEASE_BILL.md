# Release bill — Anonymity: PSC-Q

- Public head: `[[2026.06.16 - Anonymity: PSC-Q]]`
- Published path: `published/2026-06-16_psc_q/`
- Source: `series/congestion_series/paper2_psc_q/paper.tex`
- Source SHA-256: `14d2562e6910bceb799361a50dbc9bb3de40ccfcefd9eddd383e2f05aa7e5aec`
- Decision note: `release_queue/decisions/2026.06.16-0944-pscq-publicspine-publish.md`
- Evidence pack: `release_queue/evidence_packs/2026.06.16-psc-q/EVIDENCE_PACK_MANIFEST.json`
- Compile witness: `release_queue/freeze_packets/2026.06.16-psc-q/FREEZE_COMPILE_WITNESS.snapshot.json`
- Freeze packet: `release_queue/freeze_packets/2026.06.16-psc-q/FREEZE_PACKET_MANIFEST.json`
- Publication receipt: `published/2026-06-16_psc_q/PUBLICATION_RECEIPT.json`

## Claim carried by this public head

PSC-Q publishes the congestion-family mechanism packet that sits between the public Congestion-EQ accountant root and the downstream W-Congestion-EQ replay checker. The public claim is the mechanism card: `pscq.knobs.v0.1`, a 2 ms renewal-style calendar, substitution-only cover semantics, observer-resolution assumptions, and the utilization interval `rho in [0.7,0.8]` with `rho_max=0.8` as the recertification boundary.

## Machine-checkable release card

The release evidence pack contains `PSCQ_MECHANISM_CARD.json`, extracted from `tab:minimal-pscq-card`. The card recomputes a 500 Hz slot rate from the 2 ms public tick, recomputes the slack floor at `rho_max=0.8`, verifies the substitution-only and observer-resolution guards, and records the owner route `Congestion-EQ -> PSC-Q -> W-Congestion-EQ -> Eval 1 -> Operational B -> Release A`.

## Boundary

This publication does not publish W-Congestion-EQ replay/checker bundles, PSC-Q microstudy artifacts, runtime operator receipts, or a successor mechanism. The release guard in the source says that if cover is not preemptible by real work, if cover reserves downstream capacity needed by real work, or if the utilization interval drifts outside the declared card, the safe fallback is not ``PSC-Q with worse constants'' but a reopened/additive or contention-bearing successor mechanism.

## Why this release is safe enough

The source is hash-bound, queue-bound, supported by a source-specific mechanism card, deterministic clean LaTeX compile snapshot, freeze packet, explicit publish decision, publication receipt, and public citation-head update. The package-level future-publication flag remains fail-closed.
