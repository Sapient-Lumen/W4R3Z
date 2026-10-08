# Python surface — rev0009 risk-first implementation

## `headlog.py`

Important objects:

- `VersionedHeadValue`
- `make_versioned_head_record`
- `head_record_digest`
- `LocalHeadMemory`
- `HeadVerdict`
- `WitnessReceipt`
- `summarize_receipts`

Primary behavior: remember accepted mutable-head history locally; reject or flag rollback, same-sequence forks, missing previous links, and previous-link mismatches.

## `capability.py`

Important objects:

- `CapabilityGrant`
- `CapabilityRevocation`
- `RevocationSet`
- `validate_capability_chain`

Primary behavior: validate scoped, expiring delegation chains and deny chains whose grant hash appears in a signed revocation set.

## `chaos.py`

Important objects:

- `FakeHeadResponder`
- `run_head_lookup_scenario`
- `HeadLookupTranscript`
- `risky_lookup_needs_more_paths`

Primary behavior: feed fake stale/fork/empty/honest mutable-head answers into local memory and preserve the transcript.

## Tests

`tests/test_headlog_capability_chaos.py` adds seven tests covering:

- clean versioned advances;
- missing/wrong previous-head links;
- rollback receipts;
- same-sequence fork receipts;
- capability chain validation;
- revocation heads;
- chaos lookup transcripts.
