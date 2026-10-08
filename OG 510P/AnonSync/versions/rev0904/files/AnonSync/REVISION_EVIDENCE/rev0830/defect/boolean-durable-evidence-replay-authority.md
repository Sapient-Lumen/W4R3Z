# Defect: Boolean durable evidence minted false replay authority

## Old decision

After reset returned or raised a typed post-commit error, the protocol exposed
`durable_reset_observed()`. The CLI reduced recovery to:

- false -> ordinary failure; or
- true -> rerun the exact request to a fresh receipt path.

A result-binding contradiction after normal return was placed in the second
bucket because the reset call had completed.

## Why that was unsound

Completion of the reset call does not prove that the durable ledger identity
still equals this request’s deterministic receipt. Between the transaction
boundary and protocol interpretation, evidence can be contradictory, inspection
can fail, or another durable identity can win. The old Boolean discarded that
distinction and over-authorized replay.

## Executable reproduction

The internal test seam runs after reset return and before result binding. The
oracle:

1. corrupts the returned reason digest;
2. opens the real ledger and replaces `ledger_instance_id` with a different
   durable identity;
3. lets production binding reject the returned result; and
4. observes the protocol’s recovery classification.

The corrected result is:

- failure `ResetDurableIdentityIndeterminate`;
- evidence `DurableIdentityIndeterminate`;
- recovery `ResolveDurableIdentityBeforeRecovery`;
- reported outcome `Committed` (informational only);
- no publication effect;
- no final receipt or temporary residue; and
- CLI status 4 when surfaced by the command boundary.

The sibling trace that corrupts only returned evidence is promoted to exact
recovery only after the independent reopen verifies the original path object and
expected receipt identity.
