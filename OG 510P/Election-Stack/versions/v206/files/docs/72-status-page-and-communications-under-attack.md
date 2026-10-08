# Status page & communications under attack (make outages legible)

**Track:** A (Deployable core)


> **Threat:** attackers win by creating confusion — not just by changing numbers.

This doc specifies an operational communications plan with cryptographic anchoring.

## Channels (minimum)
1. **Primary status page** (hosted separately from ENR)
2. **Out-of-band mirror** (different provider / domain)
3. **Signed statements feed** (content-addressed + PBB-anchored)
4. **Optional physical posting** (QR + digest cards; see docs/206) for high-stakes environments

## Status page content (normative)
Must always show:
- current **system state**: `NORMAL`, `DEGRADED`, `VERIFYING`, `UNDER_ATTACK`, `OFFLINE`
- last witness-quorum checkpoint ID and time
- latest FINAL RRP hash
- known incident summaries with IDs
- links to evidence bundles and DriftAlerts

## Signed statements
All public incident statements should be published as:
- `Statement` object (text + metadata)
- signed by the incident communications key
- anchored into PBB

Statements MUST clearly distinguish:
- unofficial ENR
- certified results
- what can be verified now vs later

## Triggered comms rules
- If checkpoint gap exceeds a threshold → automatically display “verification delayed” banner.
- If any CRITICAL DriftAlert exists → display banner linking to alert.
- If PBB equivocation proof exists → freeze public ENR updates until adjudication.

## Social media
If used:
- publish only links to content-addressed objects
- never publish numbers that are not traceable to a specific CRO hash