# Garden witness receipts

Garden nodes should give evidence, not truth.  rev0009 makes that executable.

A `WitnessReceipt` is a signed statement from a witness key saying it observed a particular mutable-head event:

```text
target
claim kind
observed sequence
observed digest
known sequence/digest, if any
source node id
issued time
signature
```

Current claim kinds:

- `observed_head`
- `observed_rollback`
- `observed_fork`
- `observed_prev_mismatch`
- `observed_missing_prev`

## What receipts are for

Receipts can help a later client or garden answer:

```text
Have others seen a fork for this target?
Which source returned a stale head?
Did a garden observe a previous-link mismatch?
Can we preserve evidence without making a global banlist?
```

## What receipts are not

They are not consensus.  They are not proof that the witness is honest.  They are not an automatic ban.  They are signed evidence that can be locally weighted, cross-checked, expired, or ignored.

## Design guess

Receipts become most useful when they are small, signed, cheap to mirror, and batchable by region.  A garden that keeps rollback/fork receipts for hot mutable heads gives enormous value without storing bulk content or deciding protocol truth.
