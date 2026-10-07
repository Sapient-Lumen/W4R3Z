# Release bill — Anonymity: W-Congestion-EQ

- Public head: `[[2026.06.16 - Anonymity: W-Congestion-EQ]]`
- Published path: `published/2026-06-16_w_congestion_eq/`
- Source: `series/congestion_series/paper3_w_congestion_eq/paper.tex`
- Source SHA-256: `e738565c80bcfeffe4263a1884125d628fbf51a52509674037a57f724a8b71ff`
- Decision note: `release_queue/decisions/2026.06.16-1151-wcongeq-publicspine-publish.md`
- Evidence pack: `release_queue/evidence_packs/2026.06.16-w-congestion-eq/EVIDENCE_PACK_MANIFEST.json`
- Compile witness: `release_queue/freeze_packets/2026.06.16-w-congestion-eq/FREEZE_COMPILE_WITNESS.snapshot.json`
- Freeze packet: `release_queue/freeze_packets/2026.06.16-w-congestion-eq/FREEZE_PACKET_MANIFEST.json`
- Publication receipt: `published/2026-06-16_w_congestion_eq/PUBLICATION_RECEIPT.json`

## Claim carried by this public head

W-Congestion-EQ publishes the local replay/checker layer for the congestion family. The public claim is deliberately narrow: a signed, canonicalized claim object using witness `congeq.wait.twostage.v1`, mechanism `pscq.calendar.v1`, accountant `congeq.epochsum.v1`, and checker `wcongeq-checker.v1` deterministically replays to the declared five-epoch cap `0.090` when its schema, signatures, arithmetic, and support-bundle checks pass.

## Machine-checkable release card

The release evidence pack contains `W_CONGESTION_EQ_REPLAY_CARD.json`, extracted from `tab:minimal-wcongeq-card`. The card recomputes the per-epoch cap from `(0.010,0.008)`, recomputes the reset cap as `5*(0.010+0.008)=0.090`, verifies the PSC-Q admissibility rows, binds the replay-soundness theorem, and records the deployment-truth boundary.

## Boundary

This publication does not prove that a deployment followed PSC-Q, that support logs are complete, that runtime measurements are honest, or that unmodeled channels are absent. Acceptance is a deterministic receipt for the declared bundle only. Operational conformance remains owned by the downstream operational, evaluation, and release-accounting surfaces.

## Why this release is safe enough

The source is hash-bound, queue-bound, supported by a source-specific replay card, deterministic clean LaTeX compile snapshot, freeze packet, explicit publish decision, publication receipt, and public citation-head update. The source now states the non-substitution theorem and prevents the checker receipt from being quoted as broader deployment anonymity evidence.
