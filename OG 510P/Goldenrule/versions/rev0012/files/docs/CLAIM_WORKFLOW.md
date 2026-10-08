# Claim Workflow

This workflow keeps scientific claims auditable from draft to retirement.

## Lifecycle

1. Draft claim in `specs/claim_register.yaml` with `status: draft`.
2. Attach claim class (`CC-*`) from `specs/claim_classes.yaml`.
3. Add local evidence links and related assumptions (`SA-*`) where needed.
4. Run:
   - `make test-claim-classes`
   - `make test-claim-register`
   - `make update-claim-register-summary`
5. Promote to `active` only after required checks for the class pass.
6. Mark `superseded` or `retired` when replaced or invalidated.

## Rules

1. Every active claim must be traceable to local evidence links.
2. Strict claim classes (`strict_gate_required: true`) require release posture before publication claims.
3. Assumption-backed claims must reference active assumption IDs from spec ledger.
4. Claim summaries must be scoped by world/suite context.

## Minimum Audit Commands

1. `make test-claim-register`
2. `make test-claim-matrix`
3. `make test-spec-evidence`
4. `make gate`
