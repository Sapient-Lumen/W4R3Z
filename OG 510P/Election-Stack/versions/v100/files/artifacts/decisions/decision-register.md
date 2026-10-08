# Decision register

This file is an index into `adr/`.

## Active ADRs
- `adr/0001-adopt-adr-and-change-control.md` — Adopt ADRs and change control (Accepted)

## How to add a decision
1. Create a new ADR in `adr/NNNN-title.md`.
2. Add it to this register with status (Proposed/Accepted/Superseded).
3. If it changes interoperability or trust assumptions, update:
   - `CHANGELOG.md`
   - `VERSION`
   - `artifacts/claims/claim-evidence-matrix.csv` (if claims/evidence moved)
