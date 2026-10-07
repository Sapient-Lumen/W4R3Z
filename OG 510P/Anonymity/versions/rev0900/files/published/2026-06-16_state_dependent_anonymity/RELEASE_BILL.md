# Release bill — Anonymity: State-Dependent Anonymity

- Public head: `[[2026.06.16 - Anonymity: State-Dependent Anonymity]]`
- Published path: `published/2026-06-16_state_dependent_anonymity/`
- Source: `series/anondht_state_series/paper1_state_dependent_anonymity/paper.tex`
- Source SHA-256: `fdf56b4926892fcd2bfe8e78f66bdaed963d350217982db74a1a1989419e790b`
- Decision note: `release_queue/decisions/2026.06.16-1558-stateunitguard-publicspine-publish.md`
- Evidence pack: `release_queue/evidence_packs/2026.06.16-state-dependent-anonymity/EVIDENCE_PACK_MANIFEST.json`
- Compile witness: `release_queue/freeze_packets/2026.06.16-state-dependent-anonymity/FREEZE_COMPILE_WITNESS.snapshot.json`
- Freeze packet: `release_queue/freeze_packets/2026.06.16-state-dependent-anonymity/FREEZE_PACKET_MANIFEST.json`
- Publication receipt: `published/2026-06-16_state_dependent_anonymity/PUBLICATION_RECEIPT.json`

## Claim carried by this public head

State-Dependent Anonymity publishes the generic control-plane stability/accountant root for the state-family lane. The public card binds `exposure_nf_id = enf-committee-contact-bucket-v2`, `tw_id = tw-24h-200-lookups`, `state_decl_id = state-routing-scores-cache-v1`, score sensitivity `Delta=0.01`, softmax temperature `tau=0.20`, the natural-log cap `epsilon_nat=0.10`, the converted bit-unit cap `epsilon_bits ~= 0.144`, a `16`-epoch no-reset horizon, total budget about `2.31` bits, and per-epoch odds inflation about `1.105`.

## Machine-checkable release card

The release evidence pack contains `STATE_ANONYMITY_CARD.json`, extracted from `tab:minimal-state-anonymity-card`. The card recomputes `epsilon_nat=2*Delta/tau`, converts it to `epsilon_bits=epsilon_nat/ln 2`, checks the 16-epoch total and per-epoch odds row, and verifies the State-card unit conversion guard.

## Boundary

This publication is not MUCC contact-floor evidence, not CPPC monitoring evidence, not evaluator notarization, not runtime conformance, and not release-lineage packaging. Later papers may quote the state card only as a bit-unit control-plane stability/accountant receipt for the exact observation/window/state tuple. The raw natural-log value `0.10` must not be copied into the bit-unit exponent or composed as `16*0.10` bits.

## Why this release is safe enough

The source is hash-bound, queue-bound, supported by a source-specific state-anonymity card, deterministic clean LaTeX compile snapshot, freeze packet, explicit publish decision, publication receipt, and public citation-head update. The riskiest unit substitution failure is now stated in the source and checked by the evidence card before publication.
