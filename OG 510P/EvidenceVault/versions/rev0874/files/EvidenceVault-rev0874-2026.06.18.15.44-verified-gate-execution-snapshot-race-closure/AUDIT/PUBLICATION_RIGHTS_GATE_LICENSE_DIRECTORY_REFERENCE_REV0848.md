# publication-rights-gate LICENSES-directory references

- Revision: `rev0848`
- Created: `2026-06-13T12:31:00Z`
- Target: `scripts/publication_rights_gate.py`
- Status: `passed_after_targeted_validation`

## Risk reduced

A component README could point at LICENSES/Apache-2.0.txt with a neutral label such as Apache-2.0 and bypass the fresh local-rights reference scan until rev0848.

## Changes observed

- Recognizes local rights references whose path includes LICENSES/licences/notices/copyright components even when the leaf filename is not license-like.
- Keeps resolved LICENSES-directory component-license files non-blocking.
- Continues to block missing local component-license references before publication.

## Validator

- `scripts/validate_publication_rights_gate_license_directory_reference_rev0848.py`

## Validator assertions

- missing LICENSES/Apache-2.0.txt reference blocks publication
- resolved LICENSES/Apache-2.0.txt reference passes a ready fixture
- British licences/MPL-2.0.txt directory spelling is checked

## Publication rights effect

None. Publication remains blocked pending owner-approved rights files and component license conclusions.
