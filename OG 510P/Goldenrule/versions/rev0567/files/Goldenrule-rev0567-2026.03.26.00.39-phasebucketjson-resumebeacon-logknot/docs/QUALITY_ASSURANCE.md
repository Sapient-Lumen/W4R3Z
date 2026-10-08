# Quality Assurance

Concord quality assurance is enforced by executable checks instead of prose-only policy.

## QA Layers

- Deterministic harness (`make test-quick`, `make test-full`)
- Integration gate (`make gate`)
- Strict release posture (`make gate-strict`)
- Targeted validators for docs, artifacts, schemas, and release manifests

## QA Policy

- Fast checks must run without network dependence.
- Integration checks must produce machine-readable evidence under `artifacts/`.
- Strict security checks are required for release candidates.
- Baseline changes (timing, goldens, allowlists) must be auditable.
