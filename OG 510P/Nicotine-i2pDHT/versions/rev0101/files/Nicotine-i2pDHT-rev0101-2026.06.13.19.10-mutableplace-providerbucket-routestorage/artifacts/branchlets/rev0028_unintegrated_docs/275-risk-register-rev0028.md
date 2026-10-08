# Risk register — rev0028

Risk-first surfaces worked in this revision:

- crash-cut journal replay can accidentally accept malformed or forked local memory;
- generated fuzz cases can overfit accepted seeds if the corpus is not deterministic and audited;
- useful refusals can launder non-service into scheduling confidence;
- SAM-shadow scripts can accidentally bless send-before-session or destination drift;
- fold modules can rot into navigation debt.

Open debts:

- no production disk/journal format;
- no coverage-guided fuzzing or shrinking;
- no live SAM/I2P router test;
- no privacy budget for SAM transcript metadata;
- foldspine still wraps old folds instead of replacing them.
