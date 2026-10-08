# Structural audit rev0317

## Focus

Rev0317 audited the real-public Beaver Valley emergency-preparedness branch for a source-clock defect and a jurisdiction-parity defect.

## Findings

1. The rev0316 ETE table is source-faithful to the Pennsylvania public fact sheet, but the public source clock is incomplete. The 2025 Ohio REP Plan names a Beaver Valley KLD Engineering ETE document dated August 29, 2022. This creates a source-clock conflict with the Pennsylvania public table note saying the KLD report had not been released.
2. The WV/Hancock seam was still too weak. The cube had a stale WV support-plan locator and now has a current-plan reference plus a KI public page, but not the current WV REP/Hancock RERP packet needed for offsite readiness.
3. Public-source authority is now ranked so event reports, plans, machine feeds, brochures, news, and synthetic fixtures cannot be merged into one evidence class.

## Refactor

Real-site emergency-readiness queries should now route through:

`public source clock -> authority rank -> packet demand -> jurisdiction parity -> firebreak regression -> local evidence import -> corrected scorecard -> public claim gate`

The legacy universal crossproduct remains a compatibility surface only. The real-public BVPS branch remains no-claim.
