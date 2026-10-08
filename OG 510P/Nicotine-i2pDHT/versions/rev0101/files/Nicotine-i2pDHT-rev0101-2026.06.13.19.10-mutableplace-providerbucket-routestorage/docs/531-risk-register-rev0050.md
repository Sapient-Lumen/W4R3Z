# Risk register — rev0050

Risks attacked:

- staged outbox entries laundering themselves into committed writes;
- component watch debt disappearing during drain;
- same idempotency key mapping to different effects;
- SAM traces becoming side effects without a canary boundary;
- diagnostic labels leaking raw public payload fragments;
- independent compaction splitting live hard-negative evidence;
- active fold surfaces drifting away from the current revision.

Still open:

- real SAM transport behavior;
- actual publication protocol;
- durable database layout;
- cryptographic production key management;
- private retrieval or metadata safety;
- Sybil/capture resistance.
