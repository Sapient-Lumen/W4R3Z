# rev0015 — witnesscache-routingpressure-samshadow

This revision continues the risk-first DHT lab.  The design remains consumer-agnostic: a mutable, garden-aware DHT above I2P, with future applications treated as consumers rather than design owners.

## New hard guesses made executable

1. **Witness evidence decays.**  A signed receipt can be valid and still be stale, monocultured, duplicated, or contradicted.  `witnesscache.py` now tests local evidence aging, duplicate collapse, family caps, contradiction quarantine, and deterministic cache transcripts.

2. **Lookup pressure needs one transcript language.**  Earlier modules tested provider proofs, mutable-head pressure, witness mesh, and latency windows separately.  `lookuptranscript.py` adds a shared local evidence object for path families, events, fast windows, timeouts, useful refusals, and bad-response pressure.

3. **SAM integration should be shadowed before it is live.**  `samshadow.py` models streaming-first SAM command/response transcripts without opening a router connection.  It catches ordering mistakes, ephemeral destination mistakes, stream-before-session mistakes, and premature SAM 3.3 datagram-subsession assumptions.

4. **Garden generosity must be scheduled.**  `gardenscheduler.py` runs multi-window admission/refusal schedules so head-watch, witness, and seed-gate work do not get starved by bulk provider floods.

5. **Provider-plane duplication is now an audited debt.**  `provider_refactor.py` records `provider_poison.py` as the canonical current provider memory/quarantine surface while keeping `providerpoison.py` as legacy history until callers migrate.

## Tests added

`tests/test_rev0015_witnesscache_routingpressure_samshadow.py` adds deterministic tests for:

- diverse fresh witness evidence;
- duplicate witness receipts refreshing but not multiplying;
- same-family witness monoculture caps;
- evidence decay below local weight threshold;
- self-contradicting witness quarantine;
- diverse lookup transcript acceptance;
- captured fast-window quarantine;
- provider-proof transcripts being evidence-only;
- SAM shadow streaming-first validation;
- SAM shadow stream-before-session and transient-destination rejection;
- SAM 3.3 primary/datagram assumption rejection for bundle-first i2pd path;
- multi-window garden scheduling under bulk flood;
- starvation detection for protected garden work;
- provider-surface audit/refactor mapping.

## Strongest new rule

```text
Freshness, path pressure, and transport assumptions are separate evidence surfaces; do not let one valid signature blur them together.
```

## Nonclaims

No live SAM/I2P transport exists here.  No production DHT exists here.  The witness cache is not a quorum.  The lookup transcript is not a wire protocol.  SAM shadow frames are not a router implementation.  Garden scheduling is local policy scaffolding, not a network-wide service contract.
