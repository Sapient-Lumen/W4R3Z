# Attribute-plane receipt page — policy basis, courier fate, and claim ceiling interface spec

## Purpose

After any metadata-carriage decision, the product needs one receipt that survives memory loss and future disagreement.

## Core decision

Every reviewed metadata-carriage action should emit an **Attribute-plane receipt**.

## Required fields

- `subject_id`
- `subject_name`
- `review_id`
- `applied_at`
- `channels_required`
- `channels_optional`
- `policy_basis`
- `seat_classes_after_apply`
- `shape_risk_after_apply`
- `claim_ceiling`
- `operator_waivers`

## Receipt sections

### 1) Policy basis

State whether the result came from:

- explicit reviewed policy
- inherited policy accepted as-is
- imported legacy state normalized
- temporary waiver

### 2) Seat classes after apply

List every affected seat as:

- native preserver
- courier-only relay
- reduced-fidelity holder
- blocked

### 3) Courier fate

If any seat remains courier-only, the receipt must say so plainly and durably.
It must never imply full preservation where only onward relay is proven.

### 4) Shape risk after apply

Record whether the action leaves:

- no known shape risk
- bundle-shape risk on named seats
- local-rendering loss only
- broad reduced-meaning warning

### 5) Claim ceiling

The receipt must end with one strongest safe summary sentence, for example:

- `All required metadata channels are preserved natively on all active seats.`
- `Required metadata channels are preserved natively on seats A/B and couriered only on seat C.`
- `This subject now exists on seat D under reduced meaning fidelity.`

## Forbidden receipt language

Do not allow the receipt to say only:

- `synced`
- `supported`
- `xattrs enabled`
- `advanced option changed`

Those phrases are too weak to preserve the real contract.
