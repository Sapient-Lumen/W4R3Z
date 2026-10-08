# Independent CDF replay verifier status

**Synthetic independent transcript only. This is not live election evidence and not a full NIST CDF conformance result.**

Archive version: `v900`  
Decision: `INDEPENDENT_SYNTHETIC_CDF_REPLAY_AGREES_NOT_CONFORMANCE`  
Primary CRO hash: `sha256:b0e8bef124f6349e6e2443d7bfb530dfb1c80f9e7c9d56b662ddfa987e419308`

This verifier re-parses the synthetic Ballot Definition, Cast Vote Records, and Election Results minimal projection without importing or executing the primary replay adapter. It recomputes option totals by reporting unit and compares both the primary adapter rows and the shipped CRO vote rows.

## Counts

- Contests: `2`
- Options: `6`
- CVR records: `6`
- Reporting units: `2`
- Comparison rows: `12`
- Errors: `0`

## Boundary

This is an independent synthetic replay transcript, not live jurisdiction export evidence, not a complete parser for NIST BD, CVR, ERR, VRI, or EEL formats, not the NIST CDF Test Method, not certification, not outcome proof, not current voter instruction, and not legal advice.
