# P0002-D010 ruler-for-water / self-reference-burden audit — rev0034

Current head: `P0002-D010`  
Draft: `poems/P0002/draft_010.md`  
Packet: `poems/P0002/material/source_material_packet_010.json`

## Risk addressed

`P0002-D009` was cold-reviewed `revise_not_promote` because it solved infrastructure overexposure but still narrated its own honesty: poem, file, proof, source-definition prose. That failure was substantive, not a registry gap.

## Substantive move

`P0002-D010 — A Ruler for Water` keeps the Station Datum / first tide staff anchor, the pier behind the Marine Inspection Office, the old tide-staff/ruler material, and the failed local current-water reach, but removes body-level poem/file/proof/source self-reference. The draft now tests whether ruler, staff, held zero, harbor, ferry wash, piles, bolt holes, brine, and boards can carry the pressure.

## Refactor

`tools/check_external_material_pressure.py` now supports `self_reference_burden_policy.mode = poem_body_self_reference_burden_cap`.

That guard caps body terms such as `poem`, `file`, `proof`, `source`, `packet`, `disclosure`, and `latest`; forbids D009 explanatory phrases; and requires material pressure strings such as `A tide staff is honest`, `Water found it anyway.`, and `Only a held zero,`.

## Gate snapshot

External-material check during audit: `True` with `976` checks and `0` failures.  
Source-snapshot check during audit: `True` with `324` checks and `0` failures.

## Non-claim

This audit verifies source traceability, current-head packet linkage, and regression guards. It does not claim that D010 is good, admitted, evidence-ready, or externally judged.
