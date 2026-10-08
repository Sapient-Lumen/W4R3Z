# Proof obligations — rev0059

Executable obligations added this revision:

- terminal receipt accepts terminal commit and rejects replay/digest drift;
- terminal receipt rejects nonterminal finality;
- idempotency repair accepts pure terminal repair and retry-lineage repair;
- idempotency repair rejects attempt regression and missing dead-letter carry;
- compaction audit accepts preserved evidence and rejects terminal/hard-negative drops;
- terminalfold and settlementfold audit the folded current path.
