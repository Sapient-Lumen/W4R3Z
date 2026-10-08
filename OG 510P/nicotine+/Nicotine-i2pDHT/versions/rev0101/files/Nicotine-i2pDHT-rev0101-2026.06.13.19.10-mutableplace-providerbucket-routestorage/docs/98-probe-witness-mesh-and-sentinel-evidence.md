# Probe witness mesh and sentinel evidence

`probewitness.py` models garden/sentinel receipts as signed evidence.

## Witness claims

```text
provider_true
provider_false
provider_refused
mutable_latest
mutable_stale
mutable_fork
path_empty
```

## The guardrail

```text
signed receipt != truth
many receipts from one family != diversity
contradictory witness != reliable helper
```

## Decisions

```text
escalate_diverse_evidence
continue_insufficient_diversity
quarantine_contradictions
ignore_invalid_only
```

Escalation means preserve evidence, ask more paths, perhaps warn locally, perhaps feed local autocuration. It does not mean the DHT has reached global consensus.

## What tests cover

- Four receipts from one family do not count as quorum.
- Three receipts from three families can escalate evidence.
- A witness that claims both provider-true and provider-false for the same target is quarantined.
- Expired/tampered receipts are ignored.
