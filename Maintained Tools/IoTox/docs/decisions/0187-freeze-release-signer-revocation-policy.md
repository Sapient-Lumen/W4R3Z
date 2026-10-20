# ADR 0187: Freeze release signer revocation policy

Status: accepted

## Context

rev0040 separated release intent from sync delivery by requiring a release-signed
`signed-update-bundle-v1` plus owner-local update policy before any inert slot staging. rev0041 then
allowed a remote principal with `install.firmware` authority to request staging of the exact current
accepted HEAD through the durable command journal.

That left release-signer lifecycle underspecified. Removing an old release key from the active signer
set denies future bundles from that key, but the policy carried no explicit epoch or retired-key
record. Operators need an auditable way to state, “this signer was deliberately retired,” without
changing the frozen bundle manifest, silently deleting inactive slots, or pretending that software-only
state can solve hardware rollback.

## Decision

Keep `signed-update-bundle-v1` unchanged. Add owner-local update policy v2:

- `iotox-update-policy-v1` remains the canonical output when no signer-policy epoch or revoked signer
  set is present.
- `iotox-update-policy-v2` adds one positive canonical `signer-policy-epoch=` line after the existing
  fixed fields.
- Active `signer=` keys remain the only keys accepted for future bundle verification.
- Optional `revoked-signer=` keys follow all active signer lines. Active and revoked sets must be
  sorted by raw public-key bytes, unique, nonzero, bounded, and disjoint.
- A revoked signer list without a positive signer-policy epoch is invalid. A v1 record cannot carry
  revoked signers. A v2 record cannot place active signers after the revoked-signer section.

Expose the policy through the existing local review path:

```text
iotox update-policy-template NAMESPACE TARGET ROOT \
  [--signer-policy-epoch N] SIGNER_PUBLIC_KEY_HEX... \
  [--revoked-signer PUBLIC_KEY_HEX...]
iotox update-policy-lint PATH
```

`update-policy-template` rejects duplicate signer-policy epoch flags and emits canonical policy text
only. `update-policy-lint` reports signer-policy epoch, revoked signer count, active signer count, and
canonical status without dumping keys.

## Consequences

A rotated v2 policy can reject future staging of bundles signed by a retired release key and can prove
that the old key is intentionally not active. The active signer set still decides verification; the
revoked set is a local denial/audit guard against accidental reintroduction in the same reviewed
policy.

This is not release-key operations. It does not generate, distribute, back up, rotate, or destroy
release keys. It does not retroactively reinterpret already staged or confirmed update state, lower the
confirmed sequence, delete rollback material, prune inactive slots, create a transparency log, or add a
hardware monotonic counter. Those remain M7 gates.

The construction host directly covers canonical policy v2 encode/decode, active/revoked overlap
rejection, revoked-without-epoch rejection, retired-signer bundle denial under a rotated policy, CLI
template/lint output, and a libFuzzer seed for the v2 grammar. Full target deployment remains blocked
on the boot/service adapter and representative power-cut evidence.
