# Operator attestation lineage receipt page: assertion basis, scope, expiry, and blocked stronger sentences

Every human-supplied assertion that materially affects behavior or claim language must emit one durable receipt.
This receipt is the audit answer to:

> who supplied missing certainty here, what exactly did they assert, what did they review, how far did that assertion reach, when did it expire, and what stronger sentence remained blocked?

## Receipt fields

- `operator_attestation_receipt_id`
- `attestation_id`
- `assertion_class`
- `actor_ref`
- `scope_ref`
- `commit_action`
- `evidence_reviewed[]`
- `missing_machine_proof[]`
- `blast_radius_summary`
- `expiry_basis`
- `reopen_triggers[]`
- `supersession_ref` nullable
- `strongest_safe_sentence`
- `blocked_stronger_sentence`
- `issued_at`

## Human-readable layout

### 1) Assertion summary

State in one sentence what the operator asserted and what commit depended on it.

Example:

- `Operator asserted that this occupied target is the previously bound tree, allowing same-tree reconnect without treating the path as a fresh merge target.`

### 2) Evidence basis

List the evidence classes actually reviewed and keep `not reviewed` visible where applicable.

### 3) Consequence scope

Show whether the attestation changed:

- warning visibility only
- reconnect path choice
- republish eligibility
- destructive repair approval
- overwrite acceptance

### 4) Expiry and invalidators

Show the first-class expiry basis and the highest-signal reopen triggers.

### 5) Blocked stronger sentence

Keep the strongest forbidden sentence permanently adjacent to the receipt.
This is the anti-folklore protection.

## Example compact receipt rows

```text
warning-is-no-longer-actionable     warning hidden locally only     no proof every peer lacks bytes     expires when any absent peer returns     blocked: all sources are gone
```

```text
archive-reviewed-nothing-critical-remains     destructive recreate approved     archive reviewed by human only     expires after successor epoch created or new residue discovered     blocked: no valuable recovery material existed anywhere
```

## Rules

### Rule 1 — receipt language must keep human truth human

Never rewrite a human attestation as machine proof.

### Rule 2 — receipts must survive even if UI banners disappear

Later operators need to know that a risky step depended on judgment, not on universal proof.

### Rule 3 — supersession must not erase the original assumption

A later stronger proof may supersede the attestation, but the original assertion and its blast radius must remain inspectable.
