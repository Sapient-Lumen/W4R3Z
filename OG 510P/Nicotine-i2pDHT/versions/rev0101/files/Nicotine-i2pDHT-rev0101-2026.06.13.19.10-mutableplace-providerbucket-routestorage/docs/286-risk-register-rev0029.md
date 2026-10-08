# Risk register — rev0029

Newly tested risks:

- checkpoint rollback;
- checkpoint same-generation fork;
- checkpoint previous-link mismatch;
- checkpoint hard-negative drop;
- conflicting checkpoint facts;
- raw-key egress budget exhaustion;
- real provider probes without decoy budget;
- family-monoculture outbound work;
- replayed egress event digest;
- handler-scope leak at dispatch;
- handler-object/body digest leak at dispatch;
- forbidden raw-key egress for witness/refusal/repair handlers;
- current-revision audit drift.

Still open:

- production persistence and crash-safety;
- real database compaction;
- live I2P/SAM behavior;
- production privacy analysis;
- actual set reconciliation beyond toy range summaries;
- measured I2P path/family independence;
- adversarial fuzzing beyond deterministic fixtures.
