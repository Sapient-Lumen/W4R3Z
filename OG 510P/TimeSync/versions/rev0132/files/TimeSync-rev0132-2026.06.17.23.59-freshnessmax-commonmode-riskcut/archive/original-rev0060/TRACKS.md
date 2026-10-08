# TRACKS

TimeSync remains a dual-track inquiry.

## Track A — Integration track
Work with the world as it exists:
- NTP / NTS
- PTP and precision timing domains
- GNSS / PNT dependencies and fragilities
- public and private time services
- holdover, fallback, source diversity, and migration

This track now meets the archive mainly through:
- the compact core
- the profile family
- and profile-specific integration guidance yet to be written

## Track B — Greenfield track
Work from first principles:
- new protocol ideas
- richer time-state exports
- better authority and control surfaces
- better global/local structure
- infrastructure that may not yet exist
- possibly broader time / phase / frequency unification
- and native surfacing of `profile_default` hooks where boundary pressure justifies it

The current greenfield pressure point is now narrower than before:
- keep source claims separate from local assessments
- keep identity / authentication separate from traceability
- let source admission and wire responses carry native middle-tier surfaces when profiles need them
- let local state carry the archive-wide minimal core without widening it

## Shared test
Both tracks must answer:
- What object is TimeSync trying to produce?
- For whom?
- In which scenarios?
- Under what trust and failure regimes?
- With what downstream consequences?
- And through which profile, if any?
