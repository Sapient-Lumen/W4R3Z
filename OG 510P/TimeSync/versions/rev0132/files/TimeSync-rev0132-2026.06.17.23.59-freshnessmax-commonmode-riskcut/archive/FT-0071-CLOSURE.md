# FT-0071 closure — replay-transparency receipts and aggregate verifier audit summaries

Closed in rev0072.

## Decision

TimeSync now defines a detached replay-transparency/audit summary surface for authorized-verifier challenge-result replay:

```text
schema/replay-transparency-audit.schema.json
spec/35-replay-transparency-and-aggregate-verifier-audit.md
```

The surface has two record kinds:

```text
challenge_replay_transparency_receipt
aggregate_verifier_audit_summary
```

## Boundary

The new records are review metadata only. They cannot satisfy profile obligations, update current actionability, reopen assessments, authenticate transport, reveal verifier rosters, reveal legal-authority details, expose salts/preimages, or turn an external log into TimeSync provenance.

## Validator pressure

rev0072 rejects unanchored receipts, replay-purpose upgrades, salt/preimage export through transparency records, small-group aggregate leakage, verifier identity leakage, replay-transparency obligation misuse, and malformed discovery-returned records.
