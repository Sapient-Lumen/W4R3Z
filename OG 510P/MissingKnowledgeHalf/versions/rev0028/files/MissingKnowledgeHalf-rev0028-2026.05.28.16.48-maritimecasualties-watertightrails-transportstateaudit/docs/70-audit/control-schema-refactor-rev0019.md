# Control-schema refactor audit — rev0019

Revision: rev0019

Audit/refactor question: should pattern controls be represented as comments inside `PATTERN-REDTEAM-LEDGER.json`, or as first-class records?

Decision: add a provisional `CTL` record type.

Reason: controls need claims, sources, ethics, unknowns, next actions, graph edges, and source-permanence treatment. A ledger row alone is too thin.

Risks introduced:

- record-type proliferation;
- accidental celebration of positive findings in a cube about negative space;
- future sessions may treat positive controls as pattern maturity.

Mitigations added:

- `schemas/control-record.schema.json` marks controls as calibration surfaces;
- `CALIBRATION-CONTROL-LEDGER.json` states that controls do not mature patterns by themselves;
- `MKH-PAT-0015` remains candidate-only with negative controls and caveat records still required;
- lint checks `CTL` records like other non-source records.
