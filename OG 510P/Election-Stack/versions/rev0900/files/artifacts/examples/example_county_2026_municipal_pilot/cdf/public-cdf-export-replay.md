# CDF export replay status

**Synthetic replay only. This is not live election evidence and not a full NIST CDF conformance result.**

Archive version: `v900`  
Decision: `SYNTHETIC_CDF_REPLAY_PASS_NOT_CONFORMANCE`  
CRO hash: `sha256:b0e8bef124f6349e6e2443d7bfb530dfb1c80f9e7c9d56b662ddfa987e419308`

The replay recomputes published option totals from the synthetic CVR fixture by reporting unit and compares those precinct-level totals to the synthetic election-results fixture using identifiers supplied by the synthetic ballot-definition fixture.

v900 also ships `public-cdf-independent-verifier.md` and `cdf-independent-replay-verifier-rev0900.json` as a separate synthetic transcript. That second path does not convert this fixture into full NIST conformance or live jurisdiction evidence.

## Counts

- Contests: `2`
- Options: `6`
- CVR records: `6`
- Reporting units: `2`
- Comparison rows: `12`
- Errors: `0`

## Boundary

This fixture is a minimal ID-replay bridge for the mission kernel. It is not a complete parser for NIST BD, CVR, ERR, VRI, or EEL formats; it is not the NIST CDF Test Method; it does not prove a real election outcome; and it does not authorize live pilot, public release, production signing, current voter instruction, certification, or legal reliance.
