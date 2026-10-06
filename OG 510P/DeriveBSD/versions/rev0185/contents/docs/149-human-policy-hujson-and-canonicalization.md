# Human-editable policy files (HuJSON) + canonicalization for signing

DeriveBSD wants policy to be:

- **reviewable** (diffable, code-reviewed)
- **human-editable** (comments, trailing commas)
- **signable** (stable canonical representation)
- **explainable** ("which policy text produced this decision?")

This doc proposes a two-layer policy format:

1) a *human policy source* (`*.hujson`) for operators
2) a *canonical machine policy* (`*.policy.json`) that is schema-validated, JCS-canonicalized, hashed, and signed

## Prior art

Tailscale’s tailnet policy is stored in a HuJSON/JWCC-like “human JSON” format (comments + trailing commas), enabling GitOps workflows without losing readability.

## DeriveBSD shape

### Inputs

- `policy.hujson` (operator-authored)
  - allows comments and trailing commas
  - must remain structurally compatible with the JSON schema

### Compilation pipeline

`policy.hujson` → parse/strip comments → **packed JSON** → schema validate → JCS canonicalize → hash → sign

Outputs:

- `policy.packed.json` (comments removed; trailing commas normalized)
- `policy.canonical.json` (JCS output; hashable)
- `policy.sig` (detached signature; policy authority)
- policy digest pinned into Lock/Plan

### Properties

- Comments never affect the signed object.
- Two different textual policy sources that parse to the same JSON produce the same canonical digest.
- The policy authority can sign the canonical form once, enabling safe distribution.

### Explainability

Policy decision records should reference:

- canonical policy digest
- signature key id
- optionally, a store pointer to the original `policy.hujson` as *untrusted context* (useful for operator review)

## Why this matters for DeriveBSD

- Makes “policy-governed” practical at scale.
- Supports auditability: a decision is justified by a specific, signed policy digest.
- Avoids inventing a new DSL while still being operator-friendly.

See also:
- `docs/93-policy-decision-records.md`
- `docs/62-replay-rollback-freeze.md`
- `spec/trust.policy.schema.json`
