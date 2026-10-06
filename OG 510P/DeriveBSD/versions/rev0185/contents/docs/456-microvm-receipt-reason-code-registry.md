# MicroVM receipt reason-code registry (v0)

**Tier:** A (Core)
**Profiles:** A, B, C, D
**Pillars:** operability, isolation
**Patterns:** Plan→Apply→Receipt

MicroVM lifecycle receipts (`microvm.launch.receipt`, `microvm.stop.receipt`) are a **stable contract** between:

- host-local enforcement (`derive-vmmd`),
- fleet/workstation tooling,
- and incident/forensics bundles.

A free-form message is not a stable API. Reason **codes** are.
This doc is the **single registry** for the v0 microVM reason-code vocabulary.

## Rules

- Receipts MUST include a non-empty `reasons[]` list on non-success outcomes (see `adrs/ADR-0045-microvm-receipt-reason-codes.md`).
- `reasons[].code` MUST be chosen from the registry below.
- When you add a new reason code, you MUST:
  1) add it to this registry,
  2) reference it from the relevant ADR/doc (or add a micro-ADR if the semantics are subtle), and
  3) update/introduce at least one example receipt that demonstrates it.

Guardrail: `tools/check_microvm_reason_code_registry.py` enforces that example receipts only use registered codes.

## Registry

The registry is intentionally small. Prefer a **two-code** pattern when helpful:

- a generic umbrella reason (e.g. `denied-by-policy`, `backend-error`)
- plus a specific subreason (e.g. `force-stop-denied`, `instance-id-collision`)

<!-- registry:start -->

### Policy / authorization

- denied-by-policy
- force-stop-denied
- instance-id-collision
- plan-digest-mismatch

### Artifact verification

- artifact-missing
- signature-invalid
- digest-mismatch

### Backend / runtime

- backend-error
- timeout

### Input / validation

- invalid-request

<!-- registry:end -->

## Notes

- Codes are kebab-case with optional dot-separated namespaces (schema constraint). Keep v0 codes **short and stable**.
- `message` is for humans; do not encode backend-specific paths or transient identifiers into `code`.

See also:
- `docs/455-microvm-launch-plans-and-receipts.md`
- `docs/229-evidence-spine-overview.md`

Last updated: 2026-03-04r184
