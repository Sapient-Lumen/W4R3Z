# 573 — Nuclear emergency preparedness: EOF-power follow-up, proofcut compiler, and package overclaim scan

Revision: **rev0366**  
Base: **rev0365**  
Status: P0 current-risk hardening plus one bounded audit/refactor. Public-context-only; no real-site readiness or unreadiness claim.

## Why this revision exists

Rev0365 made the evidence intake path executable, but the cube still had three live failure modes:

1. It could receive a fragmentary public-meeting packet and still lack a plain **proofcut status board** that shows which artifact classes remain missing.
2. It treated a recent Beaver Valley emergency-response-facility power event as ordinary background instead of turning it into a targeted follow-up question for the June 2026 exercise/public meeting window.
3. Its no-overclaim scan covered only a small file list, leaving stale prose and tables outside the current-risk surface.

Rev0366 addresses those without adding a new doctrine layer.

## P0 rule

A packet is not credited merely because it was received, public, official, or associated with the June 2026 exercise clock. For every artifact class in the rev0365 contract, the cube must be able to say one of three concrete things: real candidate evidence received with hash and sidecar metadata, quarantined/deficient artifact received, or still missing. Fixture rows and public notices remain zero-credit for readiness closure.

The March 2026 EOF power-loss event is treated as a targeted follow-up item, not as proof of readiness or unreadiness. The follow-up asks whether EOF/backup-power repair, compensatory measures, and exercise evaluation evidence can be linked to dated artifacts.

## Operational files

- `tools/compile_nuclear_emergency_bvps_proofcut_status_rev0366.py` — compiles the rev0365 evidence contract and ledgers into a proofcut status board.
- `cube/nuclear-emergency-bvps-proofcut-status-rev0366.csv` — current proofcut board: zero real candidate rows, fixture rows counted separately, all real readiness closure blocked.
- `cube/nuclear-emergency-bvps-eof-power-followup-rev0366.csv` — current-event follow-up created from NRC Event Notification 58200.
- `cube/nuclear-emergency-bvps-public-meeting-capture-checklist-rev0366.csv` — capture list for the June 12 preliminary-findings/public-meeting lane.
- `tools/audit_nuclear_emergency_bvps_package_claim_surface_rev0366.py` and `tools/validate_nuclear_emergency_bvps_package_overclaim_scanner_rev0366.py` — package-level claim scan, with explicit allowed negative-control contexts.
- `cube/bvps-active-hotpath-resource-manifest-rev0366.csv` — bounded hotpath manifest so future sessions do not default to scanning giant historical matrices.
- `cube/bvps-exact-duplicate-alias-refactor-rev0366.csv` — exact-duplicate alias map for long-standing duplicate resources.

## Refactor boundary

Rev0366 does not delete heavy historical matrices, SQLite mirrors, or compatibility aliases. It reduces forward operational waste by defining a hotpath manifest and by validating known exact-duplicate alias pairs instead of letting operators mistake them for independent evidence.

## Current state

The cube is now more ready to handle the first real/anonymized packet and less likely to overclaim from public context. It still has no real Beaver Valley exercise evidence packet. The honest state remains: **capture-ready / chain-of-custody-ready / proofcut-board-ready / claim-frozen / no local readiness conclusion**.
