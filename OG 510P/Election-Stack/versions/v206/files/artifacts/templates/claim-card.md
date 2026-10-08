# Claim card (bounded, bundle-ready)

> **Purpose:** Ship this as `claim.md` alongside an evidence bundle (`docs/211-...`).
> Keep it small. If you cannot keep it small, the claim is not bounded.

## ClaimID
- `CLM-???` (prefer an existing row from `artifacts/claims/claim-evidence-matrix.csv`)

## Claim statement (1 paragraph max)
- *(Write the specific claim being asserted or refuted.)*

## Epistemic status + confidence (required)
- Tag the claim statement and any load-bearing inferences using `DOC:docs/218-epistemic-status-tags-and-confidence-rubric.md`.
- Example: `[MEASURED|HIGH] ...` or `[INFERRED|MEDIUM] ...`

## Scope boundaries (what this card is and is not claiming)
- **In-scope:** (bullets; cite scope docs)
  - `DOC:docs/166-scope-and-claims-contract.md`
  - `DOC:docs/167-non-claims-and-boundaries.md`
- **Not claimed / out-of-scope:** (bullets; be explicit)

## Proof obligations in play
- `PO-???` (see `DOC:docs/164-proof-obligations-registry.md`)

## Hazards addressed (if applicable)
- `HZ-???` (hazard register)

## Evidence present (use 163 tokens)
- `DOC:...`
- `SCHEMA:...`
- `EXAMPLE:...`
- `CHECK:...`
- `TOOL:...`
- `SCRIPT:...`
- `MANIFEST:manifest.json` *(in the bundle)*


## Acquisition notes (optional; keep tight)
- If a dispute may hinge on “what bytes were fetched,” include a capture note and pin its digests:
  - `DOC:docs/223-public-surface-capture-notes-and-reproducibility.md`
  - `TEMPLATE:artifacts/templates/public-surface-capture-note.md`
  - `CHECK:artifacts/checklists/public-surface-capture-note-quickcheck.md`
- List the capture-note path(s) here (and in the bundle).

## Evidence missing (if any) + receipts of absence
- Missing: `...`
- Receipt: `DOC:...` / `EXAMPLE:...` *(coverage / missingness artifact proving absence)*

## Decision rule (optional; 1–3 bullets)
- Claim holds if:
- Claim fails if:

## Public statement mapping (optional; keep tight)
- Relevant PublicNotice(s): `...`
- Relevant parity snapshot(s): `...`
- Relevant digest card(s): `...`

## Redaction / sensitivity notes (optional)
- If sensitive material was handled, cite:
  - `DOC:docs/189-sensitive-material-and-secrets.md`
  - `CHECK:artifacts/checklists/public-artifact-redaction-checklist.md`
- If any evidence-relevant artifact was redacted/transformed, include and cite:
  - `DOC:docs/225-redaction-logs-and-transformation-accountability.md`
  - `TEMPLATE:artifacts/templates/redaction-log.md` *(ship as `redaction-log.md`)*
  - `CHECK:artifacts/checklists/redaction-log-quickcheck.md`
