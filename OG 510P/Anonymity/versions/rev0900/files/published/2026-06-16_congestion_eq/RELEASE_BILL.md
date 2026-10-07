# Release bill — Anonymity: Congestion-EQ

- Public head: `[[2026.06.16 - Anonymity: Congestion-EQ]]`
- Published path: `published/2026-06-16_congestion_eq/`
- Source: `series/congestion_series/paper1_congestion_eq/paper.tex`
- Source SHA-256: `12ea46985036b1b5f3a4012083afd482af8ac4d4f868fbc1f6dd0390a1031c2d`
- Decision note: `release_queue/decisions/2026.06.16-0800-congestioneq-publicroot-publish.md`
- Evidence pack: `release_queue/evidence_packs/2026.06.16-congestion-eq/EVIDENCE_PACK_MANIFEST.json`
- Compile witness: `release_queue/FREEZE_COMPILE_WITNESS.json`
- Freeze packet: `release_queue/freeze_packets/2026.06.16-congestion-eq/FREEZE_PACKET_MANIFEST.json`
- Publication receipt: `published/2026-06-16_congestion_eq/PUBLICATION_RECEIPT.json`

## Claim carried by this public head

Congestion-EQ publishes the congestion-family theorem/accountant root: an end-to-end waiting-time witness family on the declared two-stage anonymous-DHT lookup path, a history-conditioned TV contract, a load envelope `rho in [0.68,0.72]`, stage caps `eps_1=0.010` and `eps_2=0.008`, the per-epoch cap `0.018`, and the five-epoch reset-block cap `0.090`.

## Machine-checkable release card

The release evidence pack contains `CONGESTION_EQ_ACCOUNTANT_CARD.json`, extracted from `tab:minimal-congeq-card`. The card recomputes `0.010 + 0.008 = 0.018`, recomputes `5 * 0.018 = 0.090`, and verifies the local M/M/1 sanity drill that moves mean wait from about `3.33` to about `3.57` across the adjacent effective-arrival rows.

## Boundary

This publication does not publish PSC-Q mechanism knobs, the PSC-Q microstudy addendum, W-Congestion-EQ replay/checker bundles, evaluator runtime conformance logs, or release-facing lineage receipts beyond this entry's own publication receipt. PSC-Q should be the next congestion-family release candidate only after its mechanism-card evidence is staged; W-Congestion-EQ should remain downstream until the theorem root and mechanism packet are public.

## Why this release is safe enough

The source is hash-bound, queue-bound, static-preflight clean except for the resolved evidence-pack warning, supported by a current deterministic clean LaTeX compile witness, frozen into a packet manifest, and materialized through a guarded publish decision. The package-level future-publication flag remains fail-closed.
