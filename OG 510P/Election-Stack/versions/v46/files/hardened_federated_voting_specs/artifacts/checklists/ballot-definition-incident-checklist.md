# Ballot definition incident checklist (BD pipeline compromise / mismatch)

Trigger this checklist when ballot definition hashes mismatch, canaries trip, or a BD artifact is suspected compromised.

## Containment
- Stop further publication of ballot definitions.
- Preserve logs, build artifacts, and signing environment state.
- Publish an `IncidentCommsPackage` with known affected jurisdictions/precincts.

## Verification
- Compare content-addressed BD artifacts across mirrors.
- Verify signatures and checkpoint inclusion for EPB references.
- Validate CDF mapping manifest consistency.

## Recovery
- Re-issue corrected artifacts with tombstones (see `DOC:docs/144-staleness-and-tombstones-for-parameter-migrations.md`)
- Run observer-kit verification steps to confirm public reproducibility.

## Post-incident
- File an After Action Report.
