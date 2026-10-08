# Audit rev0131 — multi-source adjudication disagreement guard

## Risk selected

After rev0130, chrony and ntpq could agree for equivalent evidence, but consumers still lacked an executable rule for what to do when multiple local assessed states are available. The unsafe failure mode is cherry-picking the most favorable adapter result or treating cross-adapter agreement as proof of independent roots.

## Correction

rev0131 adds `tools/multisource_adjudicator.py`:

- it consumes local-assessed-state objects, not raw chrony/ntpq text;
- it intersects intervals only when they overlap;
- it carries forward the weakest P1 conformance/applicability/actionability lane;
- it fails closed when intervals are disjoint or profile/timescale/source-posture compatibility is not established;
- fail-closed output uses the union interval, preserving uncertainty instead of hiding it;
- authentication and source-diversity claims remain non-strengthening.

## Refactor value

The multi-input decision is now outside adapter-specific parser code. Chrony and ntpq remain responsible for turning management text into assessed states; the adjudicator handles consumer-facing composition of assessed states.

## Remaining risks

- Live chronyd/ntpd/NTPsec capture remains unproven in this cloud container.
- NTS, symmetric-key, packet-MAC, and packet-transcript verification remain unsupported.
- Cross-adapter agreement does not prove independent upstream roots.
- Named UTC realization and leap-smear policies remain unverified.
- PTP operational-state comparison remains open before any cross-domain interoperability claim.
