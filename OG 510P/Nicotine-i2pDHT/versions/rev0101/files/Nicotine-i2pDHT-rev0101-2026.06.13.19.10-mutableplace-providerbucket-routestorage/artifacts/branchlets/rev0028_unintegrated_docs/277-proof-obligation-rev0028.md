# Proof obligations — rev0028

New local proof obligations:

- journal replay must reject rollback, same-sequence fork, bad signature, previous-link mismatch, and malformed non-tail bytes;
- journal compaction must preserve hard-negative records;
- generated fuzz corpus must turn accepted seed cases into rejected mutations across parser/wire/shadow surfaces;
- refusal budget join must not allow refusal loops or no-service-with-refusals to schedule as success;
- SAM wire shadow must reject send-before-session, destination drift, and invalid canonical frames;
- foldspine must keep rev0028 and selected historical folds visible.
