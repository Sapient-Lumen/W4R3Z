# rev0347 evidence-exclusion events / observed-sector refactor audit

Current linked revision: `rev0347` (`evidence-exclusion-events-observed-sector-refactor`).

## Scope

This pass targets a concrete leakage risk rather than adding doctrine: source-carrying rows still stored old `revXXXX_*note` fields that said fresh public records were denominator pressure only. Those notes were easy to preserve historically but weak as executable semantics. rev0347 converts the riskiest cluster into typed `source_role_events` and adds lint so the old keys cannot quietly regrow in the normalized ledgers.

## Refactor counts

- `EVIDENCE-UNIT-LEDGER.json`: 64 ad hoc per-revision source-role notes removed; 64 `source_role_events` added.
- `OBSERVED-SECTOR-RECOVERY-LEDGER.json`: 5 ad hoc notes removed; 5 `source_role_events` added.
- `CLASSICAL-LIMIT-LEDGER.json`: 6 ad hoc notes removed; 6 `source_role_events` added.
- `WEAK-FIELD-PPN-LEDGER.json`: 6 ad hoc notes removed; 6 `source_role_events` added.
- `LOCAL-QFT-RECOVERY-LEDGER.json`: 5 ad hoc notes removed; 5 `source_role_events` added.
- Total retired in this pass: 86 old note fields.
- Total typed `source_role_events` now present across normalized ledgers including the rev0346 equivalence-principle pass: 100.

## Semantic change

The change is not a route-state change. It is a custody/exclusion refactor:

- evidence-unit rows now record which refs are excluded from acquired evidence-unit `source_refs`, why they remain capped at `S0`, and which empirical-delta handles they reciprocate;
- metadata-wrapper evidence units now record forbidden denominator handles explicitly;
- observed-sector, classical-limit, weak-field/PPN, and local-QFT rows now record denominator-retained refs as typed events rather than ad hoc revision prose;
- classical-GR and QM/QFT frontier-source assertions now carry per-source snapshot receipts in `FRONTIER-SOURCE-FRESHNESS-ASSERTIONS.json`.

## Executable controls added

`tools/lint_archive.py` now rejects, for the normalized ledgers in this pass:

- any row-level `rev####_*note` key;
- duplicate or malformed source-role event ids;
- source-role events with unknown roles or dispositions;
- event refs missing from the bibliography;
- excluded or metadata-forbidden refs that leak into acquired evidence-unit `source_refs`;
- excluded or metadata-forbidden events not capped at `S0`;
- missing denominator-retained events on the selected observed-sector/classical-limit/weak-field/local-QFT rows.

## No-promotion boundary

The public records are still denominator pressure or operational-status runway only. EHT, DESI, S2, CODATA/NIST, electron-moment, equivalence-principle, fifth-force, clock/redshift, and torsion-balance records do not become candidate-native evidence, dark-sector detections, quantum-gravity signals, black-hole microstate evidence, or route promotions.

## Remaining risk

The next high-risk cluster is not another prose doctrine layer. It is the remaining note-field population in route-state and adjacent source-role ledgers. In particular, `CANDIDATE-ROUTE-STATE-LEDGER.json` and several horizon/cosmology/scattering/QFT ledgers still need the same event migration or a tighter family-local equivalent, followed by compression of generated audits so the archive does not grow by replaying every passing row on human surfaces.
