# Human-editable policy files (HuJSON) + canonicalization for signing

DeriveBSD wants policy to be:

- **reviewable** (diffable, code-reviewed)
- **human-editable** (comments, trailing commas)
- **signable** (stable canonical representation)
- **explainable** ("which policy text produced this decision?")

This doc proposes a two-layer policy format:

1) a *human policy source* (`*.hujson`) for operators
2) a *canonical machine policy* (`*.policy.json`) that is schema-validated, JCS-canonicalized, hashed, and signed

The accepted boundary is now explicit too:

- the canonical JSON policy object is authoritative
- `frontend.compile.receipt` is the evidence object for the normalization/compile step
- the HuJSON source remains authoring context rather than policy authority

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
- optional `frontend.compile.receipt` (source/compiler provenance for review/support)
- policy digest pinned into Lock/Plan

### Properties

- Comments never affect the signed object.
- Two different textual policy sources that parse to the same JSON produce the same canonical digest.
- The policy authority can sign the canonical form once, enabling safe distribution.
- The HuJSON source is useful operator context, but the authoritative object remains the canonical JSON digest.

### Explainability

Policy decision records should reference:

- canonical policy digest
- signature key id
- optionally, a store pointer to the original `policy.hujson` as *untrusted context* (useful for operator review)
- optionally, `frontend.compile.receipt` when support/reproducibility needs the exact source/compiler provenance of the normalization step

## Why this matters for DeriveBSD

- Makes “policy-governed” practical at scale.
- Supports auditability: a decision is justified by a specific, signed policy digest.
- Avoids inventing a new DSL while still being operator-friendly.
- Gives DeriveBSD one blessed human-friendly authoring surface without choosing a large frontend language stack prematurely.

See also:
- `docs/93-policy-decision-records.md`
- `docs/62-replay-rollback-freeze.md`
- `docs/495-frontend-source-compile-receipt-and-canonical-ir-boundary.md`
- `spec/trust.policy.schema.json`
- `spec/frontend.compile.receipt.schema.json`

Last updated: 2026-03-07r224
