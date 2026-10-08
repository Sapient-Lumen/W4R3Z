# Risk register — rev0034

- Launch quorum is a toy local gate, not a production session manager.
- Metrics veil is a heuristic leak guard, not a formal telemetry privacy proof.
- Label redaction by digest can still leak through timing, counters, and cardinality.
- SAM probe remains no-network transcript classification, not a real router test.
- Persistjoin is newly folded from a parallel branchlet and should be exercised more under corrupted restart fixtures.
- Foldmerge audits navigation but does not prove architectural simplicity.
