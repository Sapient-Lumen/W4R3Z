# Proof obligations rev0028

Toy-tested obligations:

- linked journal replay accepts signed prefixes and counts hard negatives;
- crash-cut tail is accepted only after a safe prefix;
- middle corruption, previous-link mismatch, rollback, and same-sequence fork are rejected;
- generated fuzz corpus rejects all generated mutations;
- refusal-budget join accepts balanced service and quarantines refusal laundering/starvation;
- SAM-shadow script accepts ordered session/send and rejects send-before-session, destination drift, and frame mismatch;
- foldspine keeps rev0028 navigation and predecessor folds visible.
