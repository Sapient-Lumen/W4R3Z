# Witness poison and receipt diversity

Garden witnesses are powerful because they preserve memory. That also makes them a poison surface.

## Rule

```text
A valid witness receipt is evidence, not quorum.
```

`witnesspoison.py` admits receipts only as local evidence. It checks signature validity, expiry, family diversity, and contradictory statements from the same witness.

## Why one family is not enough

A single garden node or garden family can emit many signed receipts. That should not count as many independent views. rev0010 groups receipts by `family_id` hints and requires multiple alarm families before treating alarm receipts as usable quorum pressure.

## Contradictions

The analyzer flags a witness that emits incompatible statements for the same target in the same evidence window, such as claiming both highest-seen and rollback evidence. This is not final proof of malice; clocks, windows, and partial knowledge are messy. It is enough to quarantine that batch as poison.

## Future pressure

The next step is to tie receipt families to path families, garden service catalogs, local encounter salience, and possibly transparency-style checkpoints. The invariant should remain: witnesses help clients remember; they do not decide truth.
