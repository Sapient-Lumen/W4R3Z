# Garden useful-refusal receipts

Garden nodes are giving supernodes, not infinite resources. A useful DHT must help them say no.

## The positive signal

A bounded refusal is a contribution:

```text
service: path_scout / bulk_reprovider / mutable_steward / ...
target digest
reason: overloaded / rate_limited / budget_exhausted
issued_at / expires_at
retry_after_seconds
capacity_epoch
signature
```

A leaf can use this as local curation evidence:

```text
signed + scoped + bounded retry => graceful refusal
```

That should score slightly positive, because it prevented silent failure.

## What refusal does not mean

A refusal is never availability evidence.

```text
garden refused bulk_reprovider for key X
  != key X has no providers
  != key X is banned
  != DHT truth changed
```

Policy refusals are subjective. Unsupported-service refusals are routing hints. Unbounded retry windows are suspicious.

## Why this is risk-first

Without useful refusal, gardens either collapse or lie. A DHT that wants power users to donate bandwidth, RAM, disk, and uptime must make overload visible and bounded. This protects the garden and helps leaves choose better paths.

## Current implementation

```text
GardenRefusalReceipt
assess_refusal_receipt
RefusalAssessment
```

A refusal assessment can turn into a local `EncounterObservation`, but that observation stays local. No global reputation surface is introduced.
