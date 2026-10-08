# Control endpoint receipt page — runtime watermark, endpoint grade, and safe language interface spec

## Purpose

Emit a durable receipt after endpoint entry, switch, recovery, or re-attestation so later work does not fall back to memory.
This receipt answers:

- which control world was actually reached
- how strong the attribution was
- what mutations just happened
- what safe language remains approved afterward

## Inputs

- endpoint attestation object
- optional endpoint switch review
- optional browser target proof
- recent mutation summary
- current claim ceiling
- timestamp and actor

## Receipt layout

### A. Header

Fields:

- receipt id
- timestamp
- actor
- affected endpoint
- runtime watermark
- overall confidence grade

### B. Proven facts

List only facts that passed attestation, such as:

- runtime watermark
- host and principal
- storage lineage
- listener tuple
- audience/auth/transport grade
- seat-lineage verdict

### C. Mutation summary

Show:

- no mutation / entry only
- endpoint switch applied
- credential recovery applied
- browser trust recovery applied
- service/profile switch applied

### D. Approved language block

Emit together:

- strongest approved sentence
- stronger forbidden sentence
- what proof is still missing

### E. Follow-up obligations

Examples:

- `re-attest after restart`
- `compare sibling runtimes before deleting`
- `clear stale bookmark`
- `export receipt to incident dossier`

## Behavior rules

- Receipts must be exportable and referenceable from later reviews.
- Receipts must preserve the distinction between endpoint reachability and runtime identity.
- If confidence is partial, the receipt must say so in the header and in the approved-language block.

## Output object

```text
control_endpoint_receipt {
  receipt_id,
  timestamp,
  actor,
  endpoint_id,
  runtime_watermark,
  confidence_grade,
  proven_facts[],
  mutation_summary,
  strongest_safe_sentence,
  stronger_forbidden_sentence,
  missing_proof,
  followup_obligations[]
}
```