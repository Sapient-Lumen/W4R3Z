# Path-alias ledger-audit witnesses, stable handle paths, and strict portability budget

This is the compact successor surface for `OQ-0220`.

`rev0326` resolves `OQ-0220` by letting generated ledger-audit summaries trigger a mechanical continuity-memory refactor only when the refactor produces bounded evidence, not authority.  The concrete refactor is path hygiene: long descriptive method and contract paths are rewritten to stable `WVF` aliases, while `PATH-ALIAS-LEDGER.json` preserves the old descriptive paths as audit metadata only.

## Governed exact-token family

Family: `path_alias_state` / `WVF-0125`.

Allowed tokens:

- `batch-alias-bounded` — compact batch alias groups retain retired checker provenance without wrapper-regrowth-by-alias.
- `alias-ledger-bounded` — alias mappings are recorded in `PATH-ALIAS-LEDGER.json` with old path, new path, handle, kind, rationale, and non-authority warning.
- `long-path-refactored` — previously long method and contract paths are moved to short stable `WVF` aliases rather than carried forward under advisory warnings.
- `stable-handle-routed` — the live path uses the existing witness-family handle, so the short name remains tied to `WITNESS-FAMILY-HANDLES.json` rather than inventing a new path vocabulary court.
- `reference-rewrite-verified` — rewritten references are validated by lint, the alias-ledger guard, internal surface checks, and generated compact surfaces.
- `path-budget-hardened` — `tools/check_path_portability_contract.py` now fails paths above the stricter archive-relative and component budgets instead of merely warning near practical extraction limits.
- `old-path-audit-only` — old descriptive paths remain only inside alias provenance metadata and must not be treated as current surface pointers.
- `generated-surface-resynced` — context, innovation, frontier, validation, ledger-audit, release-integrity, and package surfaces are regenerated after the refactor.
- `mixed-path-alias` — path aliasing, ledger audit, reference rewrite, and portability budgets are all load-bearing and must remain bounded evidence.

Excluded synonyms:

- `path-migration-court`
- `alias-authority-board`
- `filename-canonization`
- `ledger-review-court`
- `stale-path-senate`
- `reference-rewrite-tribunal`
- `portability-notary`
- `redirect-registry-authority`
- `wrapper-regrowth-by-alias`

## Audit/refactor rule

A generated audit may trigger a refactor when it exposes a mechanical portability or reentry hazard that can be repaired by ordinary surface edits and guards.  The audit does not decide semantic authority.  Here, the ledger-audit/refactor move is allowed because the output is observable: old paths disappear from live archive locations, new paths exist, current references are rewritten, and `make lint` re-runs the generated compact surfaces.

## Path-alias ledger

`PATH-ALIAS-LEDGER.json` records the refactor.  Its entries are navigational/provenance rows, not method content.  The current live paths are the `new_path` values; `old_path` values are audit facts and should not be followed as archive surfaces.

## Stricter portability budget

`tools/check_path_portability_contract.py` now fails archive-relative paths over 180 characters and path components over 170 characters.  This revision brings the current package inside that stricter envelope, reducing the risk that extraction under ordinary parent directories, sync clients, or editors trips path-length limits.

## Guard set

- `tools/check_path_alias_witness_contract.py` ties this method, vocabulary family, receipt slot, current question posture, self-sufficiency assay, and alias ledger together.
- `tools/check_path_alias_ledger_contract.py` verifies `PATH-ALIAS-LEDGER.json`, old-path absence, new-path existence, alias uniqueness, and current path-budget compliance.
- `tools/check_path_portability_contract.py` enforces the stricter path budget.
- `tools/check_json_schema_surface_contract.py` now includes `schemas/path-alias-ledger.schema.json` for the alias ledger.
- `tools/check_current_witness_receipt_slot.py` keeps the current witness family explicit in the receipt.

## Successor

`OQ-0221` asks when path-alias ledgers should be retired, folded, or compacted without losing provenance or becoming a redirect registry authority.


Batch alias guard: `PATH-ALIAS-LEDGER.json#batch_alias_groups` is provenance-only and must not create wrapper-regrowth-by-alias. The checker verifies batch alias source-count drift and wrapper non-regrowth.
