# FT-0181 post-readout context receipt gate

Use this only after `owner-post-readout-recheck` records `new_owner_context_available` and a real returned owner context CSV/source packet exists outside the archive.

## Command path

Run the router with the actual returned context file:

```bash
make owner-field-next CSV=/path/to/returned-owner-context.csv OUT=scratch/field/ft0181/ft0181-field-next-action/post-readout-new-context
```

If no matching receipt exists, the router emits:

```bash
make owner-post-readout-context-receipt RECHECK=scratch/.../post-readout-recheck.json CSV=/path/to/returned-owner-context.csv REVIEWER_ROLE_COUNT=2 NO_EXPANSION_CONFIRMED=1 NO_PUBLIC_CLAIM_UPGRADE=1 NO_SERVICE_RECORD_EDIT=1 NO_LIFECYCLE_CHANGE=1 NO_CLOSURE_FROM_CONTEXT_RECEIPT=1 CONFIRM=human-linked-post-readout-owner-context-receipt
```

After the receipt exists, rerun the router with the same CSV. It must emit intake from the receipt:

```bash
make owner-reply-intake CSV=/path/to/returned-owner-context.csv SOURCE_POST_READOUT_CONTEXT_RECEIPT=scratch/.../post-readout-context-receipt.json
```

## Source rule

The receipt can source only one scratch-local `post-readout-recheck.json` with outcome `new_owner_context_available`. It records hashes and class labels only. It must not copy owner answers, contact details, public-language drafts, service-record changes, raw learner rows, protected facts, or security payloads.

## Boundary

The context receipt is not evidence, not accepted `SRC2+`, not custody, not a service-record edit, not lifecycle movement, not public-summary support, and not `FT-0181` closure. It is a lineage gate that lets the same returned context file enter the ordinary intake/workbench path without borrowing an old contact clock.

## Reroute rule after receipt

A `post-readout-context-receipt.json` is not intake. If the receipt is the latest
local artifact and the actual CSV/source packet is not supplied, the router must
stop and emit a same-CSV `owner-field-next` command. Do not fall back to an old
contact clock, an old packet manifest, or a fresh first-contact packet.

When the CSV/source packet is supplied, the matching receipt must point to the
current selected `new_owner_context_available` recheck by both recheck reference
and recheck hash. A receipt from an earlier recheck is stale even if it has the
same CSV hash.
