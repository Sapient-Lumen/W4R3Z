# Proof obligation — rev0062

Local proof obligations added:

- terminal ACK path must not coexist with retry/withdraw repair for the same boundary;
- retry idempotency must differ from original send idempotency;
- repair retry must carry rollback-probe evidence;
- remote commit evidence must quarantine retry;
- repair fence markers must be sequence/previous-linked and diverse;
- ACK prune may only prune terminal ACK evidence, not repair debt;
- folded branchlet ancestry must be visible from tests, docs, and fold audit.

Passing tests are evidence that these toy invariants are executable. They are not a production proof.
