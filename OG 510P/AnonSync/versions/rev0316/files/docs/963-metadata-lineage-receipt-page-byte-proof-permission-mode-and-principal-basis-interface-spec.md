# Metadata lineage receipt page — byte proof, permission mode, and principal basis interface spec

## Purpose

This receipt exists so later operators do not misremember `metadata sync was enabled` as `metadata truth was fully applied`.

It must preserve the exact ceiling that held at apply time.

## Receipt sections

1. **Subject and target identity**
2. **Byte outcome**
3. **Metadata mode selected**
4. **Principal and mapping basis**
5. **Apply ceiling at time of receipt**
6. **Blocked stronger sentence**
7. **Supersession and follow-up hooks**

## 1) Subject and target identity

Show:

- subject
- seat / agent
- target path or storage class
- policy/profile source
- runtime identity that acted

## 2) Byte outcome

Show:

- byte outcome class
- integrity proof freshness
- whether byte truth and metadata truth diverged

## 3) Metadata mode selected

Show:

- permission family in scope
- exact mode chosen
- mutability class at that time
- whether the mode was create-time locked

## 4) Principal and mapping basis

Show:

- runtime principal class
- mapping mode used
- proof freshness class
- any unresolved assumptions that were accepted

## 5) Apply ceiling at time of receipt

Exactly one of:

- `full-apply-proved`
- `apply-with-conditions`
- `preserve-only`
- `rewrite-to-local-inheritance`
- `bytes-only`
- `blocked-after-partial-byte-success`

## 6) Blocked stronger sentence

Examples:

- `This receipt does not prove owner parity on all targets.`
- `This receipt does not prove that target identity mappings remained valid after issuance.`
- `This receipt does not prove native ACL enforcement on non-native storage.`

## 7) Supersession and follow-up hooks

Link to:

- fresher principal proof
- later failure review
- later successor / recreate receipt
- policy change receipt

## Object model

### Metadata lineage receipt

- `metadata_lineage_receipt_id`
- `subject_ref`
- `seat_ref`
- `target_ref`
- `byte_outcome_class`
- `metadata_mode`
- `mutability_class`
- `runtime_principal_class`
- `mapping_mode`
- `apply_ceiling`
- `blocked_stronger_sentence`
- `supersedes_receipt_ref` nullable
- `superseded_by_receipt_ref` nullable
- `followup_refs[]`

## CLI shape

```text
anonsync receipts show --kind metadata-lineage --subject finance-share
```

## Result

AnonSync should leave behind a durable record of what part of permission truth was real, conditional, preserved-only, rewritten, or omitted.
Later audits should not have to reopen job-profile settings and runtime folklore to answer that question.
