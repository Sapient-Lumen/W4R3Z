# rev0869 adopter authority-capture pack and release-date refactor

**Track:** Shared / adopter readiness / source-use safety / no-go pack hygiene  
Status: synthetic release-maintenance artifact  
Release date: 2026-06-10

## What changed

rev0868 made the state/local quarantine safe, but it still left the next operator move too implicit: a maintainer could see `70` quarantined rows and still have to infer what evidence would be required before any one row could be used in a public answer.

rev0869 turns that quarantine into an adopter work queue.

New files:

- `tools/adopter_authority_capture_pack.py`
- `scripts/check_adopter_authority_capture_pack.py`
- `artifacts/templates/adopter-source-authority-capture-worksheet.md`
- `artifacts/reports/adopter-authority-capture-matrix.json`
- `artifacts/reports/adopter-authority-capture-matrix.csv`
- `artifacts/reports/adopter-authority-capture-summary.json`

The generated matrix has one row for each quarantined mutable state/local source row. Each row remains `MISSING_ADOPTER_SOURCE_CAPTURE`, `promotion_allowed=false`, and `public_answer_gate=blocks_public_guidance` until an adopter supplies local capture evidence.

## Required promotion evidence

A quarantined row cannot become public guidance merely because it is an official route or appears in a state/local website. The capture pack requires, at minimum:

- adopter capture id;
- captured-at timestamp;
- capture role;
- source URL or official-channel id;
- byte or text SHA-256;
- responsible office;
- public help route;
- jurisdiction scope;
- election scope or effective date;
- conflict-check status;
- human approver role;
- approval timestamp.

This is a fail-closed promotion path. A captured row is scoped to the adopter and public-answer surface that approved it. It is not cross-jurisdictional and it does not make neighboring state/local examples current.

## Queue posture

| Measure | rev0869 |
|---|---:|
| Quarantined state/local rows | `70` |
| Missing adopter captures | `70` |
| Pin-first candidates | `8` |
| Public-guidance promotions allowed | `0` |
| Current-authority due within 45 days | `0` |
| Source-review due within 30 days | `0` |

Priority lanes from the capture matrix:

| Lane | Count |
|---|---:|
| `pin_first_high_risk_document` | `5` |
| `pin_first_document` | `3` |
| `high_risk_multi_surface_route` | `43` |
| `ordinary_state_local_route` | `19` |

The next highest-value manual work is to choose an adopter jurisdiction and complete captures for the pin-first document rows first, then the high-risk multi-surface routes.

## Release-date drift refactor

A separate audit found that multiple no-go packs regenerated with the current `VERSION` but still carried the old `2026-06-05` release date. That is easy to miss because the version check passed.

rev0869 adds `tools/release_context.py` and refactors these pack builders to read the release date from the top `CHANGELOG.md` entry unless `ELECTION_STACK_RELEASE_DATE` is explicitly set:

- `tools/release_go_no_go_pack.py`
- `tools/local_pilot_intake_pack.py`
- `tools/redaction_publication_pack.py`
- `tools/accessibility_language_pack.py`
- `tools/evidence_custody_provenance_pack.py`
- `tools/independent_review_conflict_pack.py`
- `tools/adopter_authority_capture_pack.py`

The regenerated no-go reports now carry `archive_version=v869` and `release_date=2026-06-10` together.

## Why this is the right risk cut

The external context supports the same fail-closed boundary already enforced inside the archive. EAC says states and territories administer elections differently and that voters must verify EAC summary information through linked state and local sources. Vote.gov likewise routes registration status and registration actions through state or local election websites. EAC/CISA public-communications guidance describes state and local election officials as trusted authoritative sources for election information. Inside this archive, those facts justify routing and capture discipline; they do not justify copying mutable state/local pages into public answers without adopter review. (xref: `eac_register_and_vote_in_your_state_page`; xref: `vote_gov_register_page`; xref: `eac_enhancing_election_security_public_comms_2024_pdf`)

## Gate behavior

`scripts/check_adopter_authority_capture_pack.py` fails if:

1. any quarantined lockfile row is missing from the capture matrix;
2. any matrix row allows promotion in this synthetic archive;
3. any row loses `MISSING_ADOPTER_SOURCE_CAPTURE` status;
4. any row stops blocking public guidance;
5. any row lacks the required capture-evidence fields;
6. the JSON or CSV reports are stale relative to the tool output.

Boundary: rev0869 remains synthetic-only. The adopter capture pack is a no-go queue and workflow scaffold. It is not current voter instruction, legal advice, source-byte cache completeness, accessibility certification, independent validation, production signer authority, publication governance, certification, or live-pilot authorization.
