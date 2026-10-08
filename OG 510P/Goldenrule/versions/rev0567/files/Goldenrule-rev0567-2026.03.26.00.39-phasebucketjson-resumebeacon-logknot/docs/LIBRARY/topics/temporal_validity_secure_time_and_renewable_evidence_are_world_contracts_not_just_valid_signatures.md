# Temporal validity, securely attested time, and renewable evidence are world contracts, not just valid signatures

Recent provenance work adds one more missing layer beneath signatures, logs, and witnesses for any successor-facing archive or trust lane.

- `RS-GR-346` shows that a timestamp is a proof that a datum existed before a particular time only if the Time-Stamp Authority uses a trustworthy source of time, and it explicitly notes that using two different TSAs is one way to mitigate compromise risk.
- `RS-GR-347` shows that long-lived archives need more than a one-shot timestamp because long-term evidence requires timestamp renewal and, when hash functions weaken, hash-tree renewal, so temporal proof is a maintained object rather than a one-time ceremony.
- `RS-GR-336` shows that even public transparency logs publish under an explicit Maximum Merge Delay and that clients audit against an SCT only after the SCT timestamp plus that delay, so append-only publication still has freshness bounds and temporary blind spots.
- `RS-GR-348` shows that a client may need the current or latest securely attested time before it can safely verify metadata at all, and that expiration checks across root, timestamp, snapshot, and targets metadata are part of freeze-attack defense rather than optional hygiene.
- `RS-GR-349` shows that trusted time bootstrap is an operational contract: if a device receives a time too far in the future it can brick itself on apparent expiry, and if it receives a time from the past it can accept stale metadata as current.
- `RS-GR-350` shows that authenticated time can itself be witnessable and contestable: Roughtime lets clients obtain rough time without already knowing the time and gives them cryptographic evidence when different time servers are inconsistent or malicious.
- Together, these sources warn that a benchmark can look more successor-safe because it changed **freshness windows, publication-latency bounds, securely attested time, or timestamp-renewal architecture** — not because the underlying Golden-Rule disposition improved.

A future benchmark should not treat a valid signature, a log inclusion proof, or one timestamp as a complete temporal-trust design.

At minimum, it should distinguish between:

1. a world with signatures or receipts but no explicit expiry or freshness contract;
2. a world with expiry fields but no secure clock bootstrap or attested time source;
3. a world with attested time but no explicit publication-latency bound or stale-proof policy;
4. a world with freshness bounds plus renewable timestamp / evidence maintenance over long horizons;
5. a world with freshness bounds, renewable evidence, and multi-source clock inconsistency detection or escalation.

These are different worlds.
They change whether successors can tell that proof is merely authentic, still timely, still globally visible, or still renewable after long offline periods and cryptographic turnover.

So temporal validity and secure time belong in the world contract.

## Minimum contract to publish

Any Golden Rule benchmark that claims durable provenance, successor-safe authenticity, or long-horizon evidence should publish at least:

1. which time sources are trusted, how time is bootstrapped after factory reset / long dormancy / offline recovery, and whether clocks are local, externally attested, or cross-checked across multiple services;
2. the expiration / freshness window for each metadata, receipt, checkpoint, or timestamp type, and what the verifier does when evidence is present but stale;
3. any publication-latency bound between acceptance and globally auditable visibility, plus the maximum expected blind window before outsiders can verify inclusion or freshness;
4. whether temporal proof is a single timestamp, a renewable evidence record, or some other renewable chain, and what events trigger renewal or hash / algorithm refresh;
5. what happens when time sources disagree or appear compromised: reject, warn, freeze use, fall back, seek other sources, or escalate to an incident / repair path.

Without that compact contract, future inheritors can mistake freshness architecture for Golden-Rule progress.
