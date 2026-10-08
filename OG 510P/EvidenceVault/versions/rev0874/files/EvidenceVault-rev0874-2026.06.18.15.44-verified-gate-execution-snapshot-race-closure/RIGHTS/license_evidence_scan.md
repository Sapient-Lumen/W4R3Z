# Rights evidence scan

This scan gathers license/rights clues from shipped component payloads. It does **not** grant a license and does **not** replace the component license ledger.

- Status: `evidence_scan_complete_license_conclusions_still_noassertion`
- Components examined: **9**
- Files examined: **4050**
- Files with rights evidence: **3**

## Aggregate finding counts

| Finding kind | Count |
| --- | ---: |
| `copyright_statement` | 4 |
| `license_like_filename` | 1 |
| `license_phrase` | 4 |
| `referenced_license_file_present` | 1 |

## Interpretation

The one detected local `LICENSE` reference is now resolved with exact pinned upstream bytes. No root license-like file exists, and all component conclusions remain `NOASSERTION` pending owner/upstream review.

## Component results

| Component | Files examined | Files with evidence | Finding counts |
| --- | ---: | ---: | --- |
| `core_governance` | 8 | 0 | none |
| `papers` | 16 | 0 | none |
| `ctg` | 92 | 0 | none |
| `docf` | 694 | 1 | `copyright_statement`=1 |
| `pact` | 648 | 2 | `copyright_statement`=3, `license_like_filename`=1, `license_phrase`=4, `referenced_license_file_present`=1 |
| `ocf_llm` | 2222 | 0 | none |
| `streamfold` | 83 | 0 | none |
| `zkrtp` | 193 | 0 | none |
| `validators_and_scripts` | 94 | 0 | none |

## PACT evidence samples

- `sources/pact/PACT_workdir/eval_real_registry_scan/servers_README.md`: license transition phrase; local reference resolves to `sources/pact/PACT_workdir/eval_real_registry_scan/LICENSE`.
- `sources/pact/PACT_workdir/eval_real_registry_scan/LICENSE`: exact upstream transition notice and full Apache-2.0, MIT, and CC-BY-4.0 terms from commit `f4244583a6af9425633e433a3eec000d23f4e011`.
