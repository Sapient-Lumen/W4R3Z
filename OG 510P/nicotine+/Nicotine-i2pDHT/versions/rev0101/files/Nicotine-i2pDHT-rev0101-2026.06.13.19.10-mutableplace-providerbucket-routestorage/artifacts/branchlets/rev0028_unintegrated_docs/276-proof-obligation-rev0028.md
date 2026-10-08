# Proof obligations — rev0028

Toy-tested obligations:

- linked journal frames replay to the latest valid snapshot;
- malformed tail frame is repairable only after a linked prior frame;
- previous-frame mismatch is quarantined;
- hard-negative loss across restart is quarantined;
- generated fuzz corpus is deterministic by seed;
- generated fuzz covers parseguard, wire frame, and shadow frame surfaces;
- generated fuzz rejects missing-surface corpora;
- refusal-heavy windows back off future scheduling;
- refusal-loop quarantine happens before scheduler laundering;
- protected scheduler starvation remains quarantine pressure;
- fold spine sees current revision modules, tests, docs, public pointers, and ledger entries.
