# Alias-retention witnesses and validation-toolchain manifest audit

This is the compact successor surface for `OQ-0221`.

`rev0327` resolves `OQ-0221` by keeping path aliases audit-only while adding a validation-toolchain manifest so alias retirement, folding, or compaction can be decided from explicit evidence rather than from memory of a prior refactor.  The key move is conservative: `PATH-ALIAS-LEDGER.json` remains retained as provenance for now, but its authority is narrowed by `ALIAS-RETENTION-POLICY.json`; future compaction is allowed only when current paths, validation coverage, release provenance, and manifest hashes show that old-path lookup is no longer needed.

## Governed exact-token family

Family: `alias_retention_state` / `WVF-0126`.

Allowed tokens:

- `alias-retained-audit-only` — the alias ledger stays present only as provenance for old-path disappearance, not as a live redirect registry.
- `alias-compaction-deferred` — compaction is intentionally deferred until repeated future package evidence shows consumers no longer need old-path mappings.
- `old-path-non-routing` — old paths may appear only inside audit metadata and cannot be used as current surface pointers.
- `toolchain-fingerprinted` — the validation toolchain is surfaced as ordered scripts, support modules, entry points, sizes, and hashes rather than only as an aggregate count.
- `manifest-backed-retirement` — future alias retirement must cite release manifests, validation manifests, and old-path absence checks before removing provenance.
- `admission-wrapper-audited` — `make lint` remains an admission wrapper, but its constituent tools and generators are now inspectable as a generated manifest.
- `mixed-alias-retention` — alias retention, validation fingerprinting, release provenance, and future compaction triggers are all load-bearing and must remain bounded evidence.

Excluded synonyms:

- `redirect-authority-board`
- `path-alias-court`
- `lint-sovereign`
- `toolchain-certification-tribunal`
- `hash-governance-court`
- `manifest-notary-authority`
- `old-path-resurrection-registry`
- `validation-score-sovereign`

## Alias-retention rule

The alias ledger can retire, fold, or compact only after a public revision shows all of the following: current references use `new_path` values, old paths remain absent on disk, release integrity and validation-toolchain manifests are fresh, and landing/runbook cues do not route ordinary reentry through alias history.  Until then, the safe state is retained audit-only provenance.

`ALIAS-RETENTION-POLICY.json` records that current state.  It is not a redirect authority.  It describes when alias provenance may be retained, compacted, folded into release provenance, or quarantined.

## Validation-toolchain manifest

`VALIDATION-TOOLCHAIN-MANIFEST.json` and `docs/00-meta/validation-toolchain.md` make the admission wrapper inspectable.  They list the ordered `make lint` tools, support modules, entrypoints, hashes, and counts.  This is an audit/refactor of the validation subsystem: `VALIDATION-INDEX.json` still explains coverage families, while the toolchain manifest exposes exact script identity.

## Guard set

- `tools/gen_validation_toolchain_manifest.py` generates the validation-toolchain manifest and guide from the actual ordered toolchain and support modules.
- `tools/check_validation_toolchain_manifest_contract.py` verifies the generated manifest against current scripts, support modules, hashes, and guide text.
- `tools/check_alias_retention_policy_contract.py` verifies `ALIAS-RETENTION-POLICY.json` remains current, bounded, and non-authoritative.
- `tools/check_alias_retention_witness_contract.py` ties this method, vocabulary family, receipt slot, policy, toolchain manifest, self-sufficiency assay, and successor question together.
- `tools/check_current_witness_receipt_slot.py` keeps the current witness family explicit in the receipt.

## Successor

`OQ-0222` asks when validation-toolchain manifests should be used for admission evidence without turning `make lint`, hashes, or generated manifests into a certification authority.
